#!/usr/bin/env python3
"""Measure, non-generatively edit, and verify food images with ImageMagick."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import shutil
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = 1
MAX_ANALYSIS_SIDE = 640


class UserError(RuntimeError):
    pass


def magick_binary() -> str:
    binary = shutil.which("magick")
    if not binary:
        raise UserError("ImageMagick 7 is required: the `magick` executable was not found.")
    return binary


def run(command: list[str], *, capture: bool = False) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        command,
        check=True,
        stdout=subprocess.PIPE if capture else subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )


def image_dimensions(path: Path) -> tuple[int, int]:
    result = run(
        [magick_binary(), "identify", "-ping", "-format", "%w %h", str(path)],
        capture=True,
    )
    try:
        width, height = map(int, result.stdout.decode("utf-8").split())
    except ValueError as exc:
        raise UserError(f"Could not read image dimensions for {path}") from exc
    if width < 1 or height < 1:
        raise UserError("Image dimensions must be positive.")
    return width, height


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def analysis_rgb(path: Path) -> tuple[int, int, bytes]:
    width, height = image_dimensions(path)
    scale = min(1.0, MAX_ANALYSIS_SIDE / max(width, height))
    sample_width = max(1, round(width * scale))
    sample_height = max(1, round(height * scale))
    result = run(
        [
            magick_binary(),
            str(path),
            "-auto-orient",
            "-alpha",
            "off",
            "-colorspace",
            "sRGB",
            "-resize",
            f"{sample_width}x{sample_height}!",
            "-depth",
            "8",
            "rgb:-",
        ],
        capture=True,
    )
    expected = sample_width * sample_height * 3
    if len(result.stdout) != expected:
        raise UserError(
            f"Unexpected pixel payload: received {len(result.stdout)} bytes, expected {expected}."
        )
    return sample_width, sample_height, result.stdout


def parse_bbox(value: str | None) -> tuple[float, float, float, float] | None:
    if value is None:
        return None
    try:
        bbox = tuple(float(item.strip()) for item in value.split(","))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("bbox must be x,y,width,height") from exc
    if len(bbox) != 4:
        raise argparse.ArgumentTypeError("bbox must contain four numbers")
    validate_bbox(bbox, "bbox")
    return bbox  # type: ignore[return-value]


def validate_bbox(value: Iterable[float], name: str) -> tuple[float, float, float, float]:
    numbers = tuple(float(item) for item in value)
    if len(numbers) != 4:
        raise UserError(f"{name} must have four values: x, y, width, height.")
    x, y, width, height = numbers
    if min(x, y, width, height) < 0 or width <= 0 or height <= 0:
        raise UserError(f"{name} values must be non-negative and size must be positive.")
    if x + width > 1.000001 or y + height > 1.000001:
        raise UserError(f"{name} must stay inside normalized image bounds.")
    return x, y, width, height


def percentile_from_histogram(histogram: list[int], fraction: float, count: int) -> int:
    target = max(0, min(count - 1, math.ceil(fraction * count) - 1))
    running = 0
    for value, frequency in enumerate(histogram):
        running += frequency
        if running > target:
            return value
    return 255


def selected_indices(
    width: int, height: int, bbox: tuple[float, float, float, float] | None
) -> tuple[int, int, int, int]:
    if bbox is None:
        return 0, 0, width, height
    x, y, box_width, box_height = bbox
    left = min(width - 1, max(0, math.floor(x * width)))
    top = min(height - 1, max(0, math.floor(y * height)))
    right = min(width, max(left + 1, math.ceil((x + box_width) * width)))
    bottom = min(height, max(top + 1, math.ceil((y + box_height) * height)))
    return left, top, right, bottom


def region_metrics(
    pixels: bytes,
    width: int,
    height: int,
    bbox: tuple[float, float, float, float] | None = None,
) -> dict[str, Any]:
    left, top, right, bottom = selected_indices(width, height, bbox)
    luma_hist = [0] * 256
    sum_luma = 0.0
    sum_luma_sq = 0.0
    sum_r = sum_g = sum_b = 0
    sum_saturation = 0.0
    saturation_values: list[float] = []
    luma_values: list[int] = []
    any_channel_low = any_channel_high = 0
    all_channel_low = all_channel_high = 0

    for row in range(top, bottom):
        for column in range(left, right):
            offset = (row * width + column) * 3
            red, green, blue = pixels[offset], pixels[offset + 1], pixels[offset + 2]
            luma = round(0.2126 * red + 0.7152 * green + 0.0722 * blue)
            maximum = max(red, green, blue)
            minimum = min(red, green, blue)
            saturation = 0.0 if maximum == 0 else (maximum - minimum) / maximum
            luma_hist[luma] += 1
            luma_values.append(luma)
            saturation_values.append(saturation)
            sum_luma += luma
            sum_luma_sq += luma * luma
            sum_r += red
            sum_g += green
            sum_b += blue
            sum_saturation += saturation
            any_channel_low += int(minimum == 0)
            any_channel_high += int(maximum == 255)
            all_channel_low += int(maximum == 0)
            all_channel_high += int(minimum == 255)

    count = len(luma_values)
    mean_luma = sum_luma / count
    variance = max(0.0, sum_luma_sq / count - mean_luma * mean_luma)
    luma_stddev = math.sqrt(variance)
    saturation_values.sort()

    edge_sum = 0.0
    edge_count = 0
    region_width = right - left
    for local_row in range(bottom - top):
        row_start = local_row * region_width
        for local_column in range(region_width):
            index = row_start + local_column
            if local_column:
                edge_sum += abs(luma_values[index] - luma_values[index - 1])
                edge_count += 1
            if local_row:
                edge_sum += abs(luma_values[index] - luma_values[index - region_width])
                edge_count += 1

    p95_sat_index = min(count - 1, max(0, math.ceil(0.95 * count) - 1))
    return {
        "sample_count": count,
        "mean_rgb_8bit": [round(sum_r / count, 3), round(sum_g / count, 3), round(sum_b / count, 3)],
        "luma": {
            "mean_8bit": round(mean_luma, 3),
            "stddev_8bit": round(luma_stddev, 3),
            "rms_contrast": round(luma_stddev / mean_luma, 4) if mean_luma else None,
            "p01": percentile_from_histogram(luma_hist, 0.01, count),
            "p05": percentile_from_histogram(luma_hist, 0.05, count),
            "p50": percentile_from_histogram(luma_hist, 0.50, count),
            "p95": percentile_from_histogram(luma_hist, 0.95, count),
            "p99": percentile_from_histogram(luma_hist, 0.99, count),
            "shadow_clip_percent": round(100 * luma_hist[0] / count, 4),
            "highlight_clip_percent": round(100 * luma_hist[255] / count, 4),
        },
        "rgb_clip_percent": {
            "any_channel_low": round(100 * any_channel_low / count, 4),
            "any_channel_high": round(100 * any_channel_high / count, 4),
            "all_channels_low": round(100 * all_channel_low / count, 4),
            "all_channels_high": round(100 * all_channel_high / count, 4),
        },
        "saturation": {
            "mean": round(sum_saturation / count, 4),
            "p95": round(saturation_values[p95_sat_index], 4),
        },
        "edge_energy_mean_8bit": round(edge_sum / edge_count, 4) if edge_count else 0.0,
    }


def neutral_suggestion(metrics: dict[str, Any]) -> dict[str, Any]:
    means = metrics["mean_rgb_8bit"]
    neutral = sum(means) / 3
    raw = [neutral / value if value else 1.0 for value in means]
    clipped = [min(1.25, max(0.80, value)) for value in raw]
    return {
        "raw_rgb_gains": [round(value, 4) for value in raw],
        "bounded_rgb_gains": [round(value, 4) for value in clipped],
        "gain_was_bounded": any(abs(a - b) > 1e-8 for a, b in zip(raw, clipped)),
        "warning": "Use only if this rectangle is genuinely neutral under the scene lighting.",
    }


def analyze(path: Path, subject_bbox: Any = None, neutral_bbox: Any = None) -> dict[str, Any]:
    if not path.is_file():
        raise UserError(f"Input file does not exist: {path}")
    original_width, original_height = image_dimensions(path)
    width, height, pixels = analysis_rgb(path)
    full = region_metrics(pixels, width, height)
    zones = []
    for row in range(3):
        for column in range(3):
            bbox = (column / 3, row / 3, 1 / 3, 1 / 3)
            zone = region_metrics(pixels, width, height, bbox)
            attention = (
                zone["luma"]["stddev_8bit"] / 64
                + zone["saturation"]["mean"]
                + zone["edge_energy_mean_8bit"] / 32
            )
            zones.append(
                {
                    "zone": f"{row + 1},{column + 1}",
                    "bbox": [round(value, 4) for value in bbox],
                    "mean_luma_8bit": zone["luma"]["mean_8bit"],
                    "luma_stddev_8bit": zone["luma"]["stddev_8bit"],
                    "mean_saturation": zone["saturation"]["mean"],
                    "edge_energy_mean_8bit": zone["edge_energy_mean_8bit"],
                    "attention_proxy": round(attention, 4),
                }
            )
    zones.sort(key=lambda item: item["attention_proxy"], reverse=True)
    result: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "input": str(path.resolve()),
        "sha256": sha256(path),
        "original_dimensions": [original_width, original_height],
        "analysis_dimensions": [width, height],
        "aspect_ratio": round(original_width / original_height, 6),
        "angle": {
            "value": "not_inferred",
            "reason": "Camera angle requires visual scene interpretation.",
        },
        "full_frame": full,
        "zones_ranked_by_attention_proxy": zones,
        "measurement_notes": [
            "Metrics use a downsampled, auto-oriented sRGB rendering.",
            "Attention proxy is not object detection or aesthetic judgment.",
            "Edge energy is not a definitive focus or sharpness measurement.",
        ],
    }
    if subject_bbox is not None:
        bbox = validate_bbox(subject_bbox, "subject_bbox")
        result["subject_bbox"] = list(bbox)
        result["subject"] = region_metrics(pixels, width, height, bbox)
    if neutral_bbox is not None:
        bbox = validate_bbox(neutral_bbox, "neutral_bbox")
        metrics = region_metrics(pixels, width, height, bbox)
        result["neutral_bbox"] = list(bbox)
        result["neutral_patch"] = metrics
        result["neutral_white_balance_suggestion"] = neutral_suggestion(metrics)
    return result


def number(
    value: Any,
    name: str,
    minimum: float,
    maximum: float,
    *,
    default: float,
) -> float:
    if value is None:
        return default
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise UserError(f"{name} must be numeric.") from exc
    if not minimum <= parsed <= maximum:
        raise UserError(f"{name} must be between {minimum} and {maximum}.")
    return parsed


def validate_recipe(recipe: dict[str, Any]) -> dict[str, Any]:
    if recipe.get("schema_version") != SCHEMA_VERSION:
        raise UserError(f"recipe schema_version must be {SCHEMA_VERSION}.")
    for key in ("purpose", "angle", "angle_confidence", "hero_bbox", "notes"):
        if key not in recipe:
            raise UserError(f"recipe is missing required field: {key}")
    if recipe["angle"] not in ("overhead", "three-quarter", "side", "macro/detail"):
        raise UserError("angle must be overhead, three-quarter, side, or macro/detail.")
    number(recipe["angle_confidence"], "angle_confidence", 0, 1, default=0)
    validate_bbox(recipe["hero_bbox"], "hero_bbox")
    if "crop" in recipe and recipe["crop"] is not None:
        validate_bbox(recipe["crop"], "crop")
    gains = recipe.get("white_balance_rgb", [1, 1, 1])
    if len(gains) != 3:
        raise UserError("white_balance_rgb must contain R, G, and B gains.")
    for index, gain in enumerate(gains):
        number(gain, f"white_balance_rgb[{index}]", 0.5, 1.5, default=1)
    number(recipe.get("rotate_deg"), "rotate_deg", -15, 15, default=0)
    number(recipe.get("exposure_ev"), "exposure_ev", -2, 2, default=0)
    number(recipe.get("contrast"), "contrast", -5, 5, default=0)
    number(recipe.get("saturation"), "saturation", 0.5, 1.5, default=1)
    levels = recipe.get("levels", {})
    number(levels.get("black_percent"), "levels.black_percent", 0, 5, default=0)
    number(levels.get("white_percent"), "levels.white_percent", 0, 5, default=0)
    number(levels.get("gamma"), "levels.gamma", 0.5, 2, default=1)
    resize = recipe.get("resize")
    if resize is not None:
        if len(resize) != 2 or any(int(item) < 1 or int(item) > 8192 for item in resize):
            raise UserError("resize must contain width and height between 1 and 8192.")
    number(recipe.get("quality"), "quality", 1, 100, default=92)
    local = recipe.get("local_food_zone")
    if local:
        validate_bbox(local["bbox"], "local_food_zone.bbox")
        if local.get("shape", "ellipse") not in ("ellipse", "rectangle"):
            raise UserError("local_food_zone.shape must be ellipse or rectangle.")
        number(local.get("feather_fraction"), "local_food_zone.feather_fraction", 0, 0.25, default=0.08)
        number(local.get("exposure_ev"), "local_food_zone.exposure_ev", -1, 1, default=0)
        number(local.get("saturation"), "local_food_zone.saturation", 0.75, 1.35, default=1)
        number(local.get("sharpen_amount"), "local_food_zone.sharpen_amount", 0, 2, default=0)
    layers = recipe.get("adjustment_layers", [])
    if not isinstance(layers, list):
        raise UserError("adjustment_layers must be an array.")
    if len(layers) > 8:
        raise UserError("adjustment_layers may contain at most 8 layers.")
    layer_names: set[str] = set()
    for index, layer in enumerate(layers):
        name = f"adjustment_layers[{index}]"
        if not isinstance(layer, dict):
            raise UserError(f"{name} must be an object.")
        if not isinstance(layer.get("name"), str) or not layer["name"].strip():
            raise UserError(f"{name}.name must be a non-empty string.")
        if layer["name"] in layer_names:
            raise UserError(f"{name}.name must be unique.")
        layer_names.add(layer["name"])
        if not isinstance(layer.get("purpose"), str) or not layer["purpose"].strip():
            raise UserError(f"{name}.purpose must be a non-empty string.")
        if layer.get("source", "duplicate_current") != "duplicate_current":
            raise UserError(f"{name}.source must be duplicate_current.")
        number(layer.get("opacity"), f"{name}.opacity", 0.05, 1, default=1)
        mask = layer.get("mask")
        if not isinstance(mask, dict):
            raise UserError(f"{name}.mask must be an object.")
        validate_bbox(mask.get("bbox", []), f"{name}.mask.bbox")
        if mask.get("shape", "ellipse") not in ("ellipse", "rectangle"):
            raise UserError(f"{name}.mask.shape must be ellipse or rectangle.")
        number(
            mask.get("feather_fraction"),
            f"{name}.mask.feather_fraction",
            0,
            0.25,
            default=0.08,
        )
        if not isinstance(mask.get("invert", False), bool):
            raise UserError(f"{name}.mask.invert must be true or false.")
        number(layer.get("exposure_ev"), f"{name}.exposure_ev", -1, 1, default=0)
        number(layer.get("contrast"), f"{name}.contrast", -2, 2, default=0)
        number(layer.get("saturation"), f"{name}.saturation", 0.75, 1.35, default=1)
        number(layer.get("sharpen_amount"), f"{name}.sharpen_amount", 0, 1, default=0)
        if not adjustment_has_effect(layer):
            raise UserError(f"{name} must contain at least one non-neutral correction.")
    sharpen = recipe.get("global_sharpen", {})
    number(sharpen.get("radius"), "global_sharpen.radius", 0, 5, default=0)
    number(sharpen.get("sigma"), "global_sharpen.sigma", 0.1, 5, default=0.8)
    number(sharpen.get("amount"), "global_sharpen.amount", 0, 2, default=0)
    number(sharpen.get("threshold"), "global_sharpen.threshold", 0, 1, default=0.02)
    if not isinstance(recipe["notes"], list):
        raise UserError("notes must be an array.")
    return recipe


def correction_args(settings: dict[str, Any], *, local: bool = False) -> list[str]:
    args: list[str] = []
    if not local:
        gains = settings.get("white_balance_rgb", [1, 1, 1])
        for channel, gain in zip(("R", "G", "B"), gains):
            if abs(float(gain) - 1) > 1e-8:
                args.extend(["-channel", channel, "-evaluate", "multiply", f"{float(gain):.8f}", "+channel"])
    exposure = float(settings.get("exposure_ev", 0))
    if abs(exposure) > 1e-8:
        args.extend(["-colorspace", "RGB", "-evaluate", "multiply", f"{2 ** exposure:.8f}", "-colorspace", "sRGB"])
    if not local:
        levels = settings.get("levels", {})
        black = float(levels.get("black_percent", 0))
        white = float(levels.get("white_percent", 0))
        gamma = float(levels.get("gamma", 1))
        if black or white or abs(gamma - 1) > 1e-8:
            args.extend(["-level", f"{black:.4f}%,{100 - white:.4f}%,{gamma:.6f}"])
    contrast = float(settings.get("contrast", 0))
    if contrast > 0:
        args.extend(["-sigmoidal-contrast", f"{contrast:.6f}x50%"])
    elif contrast < 0:
        args.extend(["+sigmoidal-contrast", f"{abs(contrast):.6f}x50%"])
    saturation = float(settings.get("saturation", 1))
    if abs(saturation - 1) > 1e-8:
        args.extend(["-modulate", f"100,{saturation * 100:.6f},100"])
    return args


def adjustment_has_effect(settings: dict[str, Any]) -> bool:
    return (
        abs(float(settings.get("exposure_ev", 0))) > 1e-8
        or abs(float(settings.get("contrast", 0))) > 1e-8
        or abs(float(settings.get("saturation", 1)) - 1) > 1e-8
        or float(settings.get("sharpen_amount", 0)) > 0
    )


def adjustment_layer_commands(
    *,
    binary: str,
    active: Path,
    settings: dict[str, Any],
    mask_settings: dict[str, Any],
    width: int,
    height: int,
    temp: Path,
    file_stem: str,
    opacity: float = 1,
) -> tuple[list[list[str]], Path]:
    """Duplicate the current composite, adjust it, and blend it through a mask."""
    duplicate = temp / f"{file_stem}-duplicate.miff"
    duplicate_command = [binary, str(active), *correction_args(settings, local=True)]
    sharpen = float(settings.get("sharpen_amount", 0))
    if sharpen > 0:
        duplicate_command.extend(["-unsharp", f"0x0.8+{sharpen:.6f}+0.02"])
    duplicate_command.append(str(duplicate))

    x, y, box_width, box_height = validate_bbox(mask_settings["bbox"], f"{file_stem}.mask.bbox")
    left, top = round(x * width), round(y * height)
    right, bottom = round((x + box_width) * width), round((y + box_height) * height)
    mask = temp / f"{file_stem}-mask.png"
    mask_command = [binary, "-size", f"{width}x{height}", "xc:black", "-fill", "white"]
    if mask_settings.get("shape", "ellipse") == "ellipse":
        center_x, center_y = (left + right) / 2, (top + bottom) / 2
        radius_x, radius_y = max(1, (right - left) / 2), max(1, (bottom - top) / 2)
        mask_command.extend(
            ["-draw", f"ellipse {center_x:.3f},{center_y:.3f} {radius_x:.3f},{radius_y:.3f} 0,360"]
        )
    else:
        mask_command.extend(["-draw", f"rectangle {left},{top} {right},{bottom}"])
    feather = float(mask_settings.get("feather_fraction", 0.08)) * min(width, height)
    if feather > 0:
        mask_command.extend(["-blur", f"0x{feather:.4f}"])
    if mask_settings.get("invert", False):
        mask_command.append("-negate")
    if opacity < 1:
        mask_command.extend(["-evaluate", "multiply", f"{opacity:.6f}"])
    mask_command.append(str(mask))

    result = temp / f"{file_stem}-composite.miff"
    composite_command = [binary, str(active), str(duplicate), str(mask), "-composite", str(result)]
    return [duplicate_command, mask_command, composite_command], result


def crop_geometry(crop: Iterable[float], width: int, height: int) -> str:
    x, y, crop_width, crop_height = validate_bbox(crop, "crop")
    pixel_x = max(0, min(width - 1, round(x * width)))
    pixel_y = max(0, min(height - 1, round(y * height)))
    pixel_width = max(1, min(width - pixel_x, round(crop_width * width)))
    pixel_height = max(1, min(height - pixel_y, round(crop_height * height)))
    return f"{pixel_width}x{pixel_height}+{pixel_x}+{pixel_y}"


def safe_rotated_dimensions(width: int, height: int, degrees: float) -> tuple[int, int]:
    """Largest centered axis-aligned rectangle wholly inside a rotated rectangle."""
    angle = math.radians(abs(degrees) % 180)
    if angle < 1e-10:
        return width, height
    sine, cosine = abs(math.sin(angle)), abs(math.cos(angle))
    long_side, short_side = max(width, height), min(width, height)
    if short_side <= 2 * sine * cosine * long_side or abs(sine - cosine) < 1e-10:
        half_short = 0.5 * short_side
        safe_width = half_short / sine
        safe_height = half_short / cosine
        if width < height:
            safe_width, safe_height = safe_height, safe_width
    else:
        cos_two = cosine * cosine - sine * sine
        safe_width = (width * cosine - height * sine) / cos_two
        safe_height = (height * cosine - width * sine) / cos_two
    return max(1, math.floor(safe_width)), max(1, math.floor(safe_height))


def edit_commands(input_path: Path, output_path: Path, recipe: dict[str, Any], temp: Path) -> list[list[str]]:
    binary = magick_binary()
    oriented_width, oriented_height = image_dimensions(input_path)
    base = temp / "base.miff"
    command = [binary, str(input_path), "-auto-orient", "-alpha", "off", "-colorspace", "sRGB"]
    rotate = float(recipe.get("rotate_deg", 0))
    planned_width, planned_height = oriented_width, oriented_height
    if abs(rotate) > 1e-8:
        safe_width, safe_height = safe_rotated_dimensions(oriented_width, oriented_height, rotate)
        command.extend(
            [
                "-background",
                "none",
                "-rotate",
                f"{rotate:.6f}",
                "-gravity",
                "center",
                "-crop",
                f"{safe_width}x{safe_height}+0+0",
                "+repage",
                "-alpha",
                "off",
            ]
        )
        planned_width, planned_height = safe_width, safe_height
    crop = recipe.get("crop")
    if crop is not None:
        command.extend(["-crop", crop_geometry(crop, planned_width, planned_height), "+repage"])
    command.extend(correction_args(recipe))
    command.append(str(base))
    commands = [command]

    active = base
    base_width, base_height = image_dimensions_after_plan(input_path, recipe)
    local = recipe.get("local_food_zone")
    if local and adjustment_has_effect(local):
        legacy_mask = {
            "shape": local.get("shape", "ellipse"),
            "bbox": local["bbox"],
            "feather_fraction": local.get("feather_fraction", 0.08),
            "invert": False,
        }
        layer_commands, active = adjustment_layer_commands(
            binary=binary,
            active=active,
            settings=local,
            mask_settings=legacy_mask,
            width=base_width,
            height=base_height,
            temp=temp,
            file_stem="legacy-local-food-zone",
        )
        commands.extend(layer_commands)

    for index, layer in enumerate(recipe.get("adjustment_layers", [])):
        layer_commands, active = adjustment_layer_commands(
            binary=binary,
            active=active,
            settings=layer,
            mask_settings=layer["mask"],
            width=base_width,
            height=base_height,
            temp=temp,
            file_stem=f"layer-{index + 1}",
            opacity=float(layer.get("opacity", 1)),
        )
        commands.extend(layer_commands)

    final_command = [binary, str(active)]
    sharpen = recipe.get("global_sharpen", {})
    amount = float(sharpen.get("amount", 0))
    if amount > 0:
        radius = float(sharpen.get("radius", 0))
        sigma = float(sharpen.get("sigma", 0.8))
        threshold = float(sharpen.get("threshold", 0.02))
        final_command.extend(["-unsharp", f"{radius}x{sigma}+{amount}+{threshold}"])
    resize = recipe.get("resize")
    if resize is not None:
        final_command.extend(["-resize", f"{int(resize[0])}x{int(resize[1])}!"])
    final_command.extend(["-colorspace", "sRGB", "-strip"])
    if output_path.suffix.lower() in (".jpg", ".jpeg"):
        final_command.extend(["-quality", str(round(float(recipe.get("quality", 92))))])
    final_command.append(str(output_path))
    commands.append(final_command)
    return commands


def image_dimensions_after_plan(input_path: Path, recipe: dict[str, Any]) -> tuple[int, int]:
    width, height = image_dimensions(input_path)
    rotate = float(recipe.get("rotate_deg", 0))
    if abs(rotate) > 1e-8:
        width, height = safe_rotated_dimensions(width, height, rotate)
    crop = recipe.get("crop")
    if crop is not None:
        _, _, crop_width, crop_height = validate_bbox(crop, "crop")
        width = max(1, round(width * crop_width))
        height = max(1, round(height * crop_height))
    return width, height


def shell_display(command: list[str]) -> str:
    import shlex

    return shlex.join(command)


def edit(
    input_path: Path,
    output_path: Path,
    recipe_path: Path,
    report_path: Path | None,
    dry_run: bool,
) -> dict[str, Any]:
    if not input_path.is_file():
        raise UserError(f"Input file does not exist: {input_path}")
    if input_path.resolve() == output_path.resolve():
        raise UserError("Refusing to overwrite the original. Choose a new output path.")
    recipe = validate_recipe(json.loads(recipe_path.read_text(encoding="utf-8")))
    resize = recipe.get("resize")
    if resize is not None:
        planned_width, planned_height = image_dimensions_after_plan(input_path, recipe)
        planned_ratio = planned_width / planned_height
        target_ratio = int(resize[0]) / int(resize[1])
        relative_error = abs(planned_ratio - target_ratio) / target_ratio
        if relative_error > 0.005:
            raise UserError(
                "Crop and resize aspect ratios differ by more than 0.5%; "
                "adjust crop coordinates instead of stretching the food."
            )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="food-image-edit-") as temp_name:
        commands = edit_commands(input_path, output_path, recipe, Path(temp_name))
        report: dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "mode": "dry-run" if dry_run else "edit",
            "input": str(input_path.resolve()),
            "output": str(output_path.resolve()),
            "input_sha256": sha256(input_path),
            "recipe": recipe,
            "commands": [shell_display(command) for command in commands],
            "layer_stack": [
                {
                    "order": index + 1,
                    "name": layer["name"],
                    "purpose": layer["purpose"],
                    "source": layer.get("source", "duplicate_current"),
                    "opacity": layer.get("opacity", 1),
                    "mask": layer["mask"],
                }
                for index, layer in enumerate(recipe.get("adjustment_layers", []))
            ],
            "non_generative_operations_only": True,
        }
        if not dry_run:
            for command in commands:
                run(command)
            report["output_sha256"] = sha256(output_path)
            report["output_dimensions"] = list(image_dimensions(output_path))
            report["input_unchanged"] = report["input_sha256"] == sha256(input_path)
            if not report["input_unchanged"]:
                raise UserError("The original changed unexpectedly; stop and investigate.")
        if report_path:
            report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        return report


def verify(input_path: Path, output_path: Path, recipe_path: Path) -> dict[str, Any]:
    recipe = validate_recipe(json.loads(recipe_path.read_text(encoding="utf-8")))
    before = analyze(input_path, recipe.get("hero_bbox"))
    after = analyze(output_path)
    before_luma = before["full_frame"]["luma"]
    after_luma = after["full_frame"]["luma"]
    checks = []

    def add(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": passed, "detail": detail})

    add("original_and_output_are_distinct_files", input_path.resolve() != output_path.resolve(), "")
    add("original_hash_available", bool(before["sha256"]), before["sha256"])
    resize = recipe.get("resize")
    if resize is not None:
        actual = after["original_dimensions"]
        add("target_dimensions", actual == [int(resize[0]), int(resize[1])], f"actual={actual}, target={resize}")
    highlight_increase = after_luma["highlight_clip_percent"] - before_luma["highlight_clip_percent"]
    shadow_increase = after_luma["shadow_clip_percent"] - before_luma["shadow_clip_percent"]
    add(
        "highlight_clipping_guardrail",
        after_luma["highlight_clip_percent"] <= 0.5 and highlight_increase <= 0.25,
        f"after={after_luma['highlight_clip_percent']}%, increase={round(highlight_increase, 4)}pp",
    )
    add(
        "shadow_clipping_guardrail",
        after_luma["shadow_clip_percent"] <= 0.5 and shadow_increase <= 0.25,
        f"after={after_luma['shadow_clip_percent']}%, increase={round(shadow_increase, 4)}pp",
    )
    add(
        "visual_review_required",
        False,
        "Open original and output side by side; this check cannot be automated.",
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "input_sha256": before["sha256"],
        "output_sha256": after["sha256"],
        "before": before,
        "after": after,
        "checks": checks,
        "automated_checks_passed": all(
            item["passed"] for item in checks if item["name"] != "visual_review_required"
        ),
        "complete": False,
        "completion_rule": "Set complete only after a human/agent visually inspects the original and output.",
    }


def write_json(data: dict[str, Any], output: Path | None) -> None:
    payload = json.dumps(data, indent=2) + "\n"
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Measure and non-generatively edit food images using ImageMagick."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze_parser = subparsers.add_parser("analyze", help="measure an image")
    analyze_parser.add_argument("input", type=Path)
    analyze_parser.add_argument("--subject-bbox", type=parse_bbox)
    analyze_parser.add_argument("--neutral-bbox", type=parse_bbox)
    analyze_parser.add_argument("--output", type=Path)

    edit_parser = subparsers.add_parser("edit", help="apply a reviewed JSON recipe")
    edit_parser.add_argument("input", type=Path)
    edit_parser.add_argument("output", type=Path)
    edit_parser.add_argument("--recipe", type=Path, required=True)
    edit_parser.add_argument("--report", type=Path)
    edit_parser.add_argument("--dry-run", action="store_true")

    verify_parser = subparsers.add_parser("verify", help="compare source and edited output")
    verify_parser.add_argument("input", type=Path)
    verify_parser.add_argument("output_image", type=Path)
    verify_parser.add_argument("--recipe", type=Path, required=True)
    verify_parser.add_argument("--output", type=Path)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "analyze":
            write_json(analyze(args.input, args.subject_bbox, args.neutral_bbox), args.output)
        elif args.command == "edit":
            write_json(
                edit(args.input, args.output, args.recipe, args.report, args.dry_run),
                None if not args.dry_run else None,
            )
        elif args.command == "verify":
            write_json(verify(args.input, args.output_image, args.recipe), args.output)
        else:
            raise AssertionError(args.command)
        return 0
    except (UserError, OSError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        if isinstance(exc, subprocess.CalledProcessError) and exc.stderr:
            detail = exc.stderr.decode("utf-8", errors="replace").strip()
            print(f"error: {detail}", file=sys.stderr)
        else:
            print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
