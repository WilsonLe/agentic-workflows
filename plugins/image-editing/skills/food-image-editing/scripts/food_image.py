#!/usr/bin/env python3
"""Measure, non-generatively edit, and verify food images with ImageMagick."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = 2
SUPPORTED_RECIPE_VERSIONS = {1, 2}
MAX_ANALYSIS_SIDE = 640
MAX_MASK_RADIUS_PX = 64


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


def validate_point(value: Iterable[float], name: str) -> tuple[float, float]:
    try:
        numbers = tuple(float(item) for item in value)
    except (TypeError, ValueError) as exc:
        raise UserError(f"{name} must contain normalized x and y values.") from exc
    if len(numbers) != 2:
        raise UserError(f"{name} must contain normalized x and y values.")
    x, y = numbers
    if not 0 <= x <= 1 or not 0 <= y <= 1:
        raise UserError(f"{name} must stay inside normalized image bounds.")
    return x, y


def integer(
    value: Any,
    name: str,
    minimum: int,
    maximum: int,
    *,
    default: int,
) -> int:
    if value is None:
        return default
    if isinstance(value, bool):
        raise UserError(f"{name} must be an integer.")
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise UserError(f"{name} must be an integer.") from exc
    if parsed != value or not minimum <= parsed <= maximum:
        raise UserError(f"{name} must be an integer between {minimum} and {maximum}.")
    return parsed


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


def validate_geometric_mask(mask: dict[str, Any], name: str) -> None:
    validate_bbox(mask.get("bbox", []), f"{name}.bbox")
    if mask.get("shape", "ellipse") not in ("ellipse", "rectangle"):
        raise UserError(f"{name}.shape must be ellipse or rectangle.")
    number(
        mask.get("feather_fraction"),
        f"{name}.feather_fraction",
        0,
        0.25,
        default=0.08,
    )
    if not isinstance(mask.get("invert", False), bool):
        raise UserError(f"{name}.invert must be true or false.")


def validate_layer_mask(mask: dict[str, Any], name: str, recipe_version: int) -> None:
    mask_type = mask.get("type", "geometric")
    if mask_type == "geometric":
        validate_geometric_mask(mask, name)
        return
    if mask_type != "color_similarity":
        raise UserError(f"{name}.type must be geometric or color_similarity.")
    if recipe_version < 2:
        raise UserError(f"{name}.type color_similarity requires recipe schema_version 2.")
    if mask.get("basis", "global_base") != "global_base":
        raise UserError(f"{name}.basis must be global_base.")
    seed = validate_point(mask.get("seed", []), f"{name}.seed")
    roi = validate_bbox(mask.get("roi", []), f"{name}.roi")
    if not (
        roi[0] <= seed[0] <= roi[0] + roi[2]
        and roi[1] <= seed[1] <= roi[1] + roi[3]
    ):
        raise UserError(f"{name}.seed must be inside {name}.roi.")
    if mask.get("colorspace", "Lab") not in ("Lab", "Luv"):
        raise UserError(f"{name}.colorspace must be Lab or Luv.")
    number(mask.get("fuzz_percent"), f"{name}.fuzz_percent", 0.1, 20, default=5)
    cleanup = mask.get("cleanup", {})
    if not isinstance(cleanup, dict):
        raise UserError(f"{name}.cleanup must be an object.")
    integer(cleanup.get("open_px"), f"{name}.cleanup.open_px", 0, 12, default=0)
    integer(cleanup.get("close_px"), f"{name}.cleanup.close_px", 0, 12, default=0)
    integer(cleanup.get("grow_px"), f"{name}.cleanup.grow_px", -24, 24, default=0)
    integer(
        cleanup.get("feather_px"),
        f"{name}.cleanup.feather_px",
        0,
        MAX_MASK_RADIUS_PX,
        default=0,
    )
    if not isinstance(mask.get("invert", False), bool):
        raise UserError(f"{name}.invert must be true or false.")
    combinations = mask.get("combine", [])
    if not isinstance(combinations, list) or len(combinations) > 8:
        raise UserError(f"{name}.combine must be an array with at most 8 entries.")
    for index, combination in enumerate(combinations):
        combination_name = f"{name}.combine[{index}]"
        if not isinstance(combination, dict):
            raise UserError(f"{combination_name} must be an object.")
        if combination.get("operation") not in ("intersect", "union", "subtract"):
            raise UserError(
                f"{combination_name}.operation must be intersect, union, or subtract."
            )
        operand = combination.get("mask")
        if not isinstance(operand, dict):
            raise UserError(f"{combination_name}.mask must be an object.")
        if operand.get("type", "geometric") != "geometric":
            raise UserError(f"{combination_name}.mask must be non-recursive geometric mask.")
        validate_geometric_mask(operand, f"{combination_name}.mask")
        if float(operand.get("feather_fraction", 0)) != 0:
            raise UserError(
                f"{combination_name}.mask.feather_fraction must be 0 for binary mask algebra."
            )


def validate_recipe(recipe: dict[str, Any]) -> dict[str, Any]:
    recipe_version = recipe.get("schema_version")
    if recipe_version not in SUPPORTED_RECIPE_VERSIONS:
        versions = ", ".join(str(item) for item in sorted(SUPPORTED_RECIPE_VERSIONS))
        raise UserError(f"recipe schema_version must be one of: {versions}.")
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
        validate_layer_mask(mask, f"{name}.mask", recipe_version)
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


def bbox_pixels(
    bbox: Iterable[float], width: int, height: int, name: str
) -> tuple[int, int, int, int]:
    normalized = validate_bbox(bbox, name)
    left, top, right, bottom = selected_indices(width, height, normalized)
    return left, top, right, bottom


def geometric_mask_command(
    binary: str,
    mask_settings: dict[str, Any],
    width: int,
    height: int,
    output: Path,
    name: str,
    *,
    apply_invert: bool = False,
    threshold_output: bool = True,
) -> list[str]:
    left, top, right, bottom = bbox_pixels(
        mask_settings["bbox"], width, height, f"{name}.bbox"
    )
    command = [binary, "-size", f"{width}x{height}", "xc:black", "-fill", "white"]
    if mask_settings.get("shape", "ellipse") == "ellipse":
        center_x, center_y = (left + right) / 2, (top + bottom) / 2
        radius_x, radius_y = max(1, (right - left) / 2), max(1, (bottom - top) / 2)
        command.extend(
            [
                "-draw",
                (
                    f"ellipse {center_x:.3f},{center_y:.3f} "
                    f"{radius_x:.3f},{radius_y:.3f} 0,360"
                ),
            ]
        )
    else:
        command.extend(["-draw", f"rectangle {left},{top} {right},{bottom}"])
    if apply_invert and mask_settings.get("invert", False):
        command.append("-negate")
    if threshold_output:
        command.extend(["-threshold", "50%"])
    command.append(str(output))
    return command


def mask_artifact_paths(temp: Path, file_stem: str) -> dict[str, Path]:
    return {
        "binary": temp / f"{file_stem}-binary-mask.png",
        "outline": temp / f"{file_stem}-outline.png",
        "alpha": temp / f"{file_stem}-alpha-mask.png",
    }


def mask_commands(
    *,
    binary: str,
    basis: Path,
    mask_settings: dict[str, Any],
    width: int,
    height: int,
    temp: Path,
    file_stem: str,
    opacity: float,
) -> tuple[list[list[str]], dict[str, Path]]:
    """Build a stable binary selection, QA outline, and final alpha mask."""
    artifacts = mask_artifact_paths(temp, file_stem)
    commands: list[list[str]] = []
    mask_type = mask_settings.get("type", "geometric")
    working = temp / f"{file_stem}-working-0.png"

    if mask_type == "geometric":
        commands.append(
            geometric_mask_command(
                binary,
                mask_settings,
                width,
                height,
                working,
                f"{file_stem}.mask",
                threshold_output=False,
            )
        )
    else:
        left, top, right, bottom = bbox_pixels(
            mask_settings["roi"], width, height, f"{file_stem}.mask.roi"
        )
        roi_width, roi_height = right - left, bottom - top
        seed_x, seed_y = validate_point(mask_settings["seed"], f"{file_stem}.mask.seed")
        seed_pixel_x = min(roi_width - 1, max(0, round(seed_x * width) - left))
        seed_pixel_y = min(roi_height - 1, max(0, round(seed_y * height) - top))
        roi_mask = temp / f"{file_stem}-roi-selection.png"
        commands.append(
            [
                binary,
                str(basis),
                "-crop",
                f"{roi_width}x{roi_height}+{left}+{top}",
                "+repage",
                "-colorspace",
                mask_settings.get("colorspace", "Lab"),
                "-alpha",
                "set",
                "-channel",
                "RGBA",
                "-fuzz",
                f"{float(mask_settings.get('fuzz_percent', 5)):.6f}%",
                "-fill",
                "none",
                "-draw",
                f"alpha {seed_pixel_x},{seed_pixel_y} floodfill",
                "+channel",
                "-alpha",
                "extract",
                "-negate",
                "-threshold",
                "50%",
                str(roi_mask),
            ]
        )
        commands.append(
            [
                binary,
                "-size",
                f"{width}x{height}",
                "xc:black",
                str(roi_mask),
                "-geometry",
                f"+{left}+{top}",
                "-compose",
                "Lighten",
                "-composite",
                str(working),
            ]
        )
        cleanup = mask_settings.get("cleanup", {})
        cleanup_args: list[str] = []
        open_px = int(cleanup.get("open_px", 0))
        close_px = int(cleanup.get("close_px", 0))
        grow_px = int(cleanup.get("grow_px", 0))
        if open_px:
            cleanup_args.extend(["-morphology", "Open", f"Diamond:{open_px}"])
        if close_px:
            cleanup_args.extend(["-morphology", "Close", f"Diamond:{close_px}"])
        if grow_px > 0:
            cleanup_args.extend(["-morphology", "Dilate", f"Diamond:{grow_px}"])
        elif grow_px < 0:
            cleanup_args.extend(["-morphology", "Erode", f"Diamond:{abs(grow_px)}"])
        if cleanup_args:
            cleaned = temp / f"{file_stem}-working-cleaned.png"
            commands.append([binary, str(working), *cleanup_args, str(cleaned)])
            working = cleaned

        compose_operators = {
            "intersect": "Darken",
            "union": "Lighten",
            "subtract": "MinusSrc",
        }
        for index, combination in enumerate(mask_settings.get("combine", [])):
            operand = temp / f"{file_stem}-combine-{index + 1}-operand.png"
            commands.append(
                geometric_mask_command(
                    binary,
                    combination["mask"],
                    width,
                    height,
                    operand,
                    f"{file_stem}.mask.combine[{index}].mask",
                    apply_invert=True,
                )
            )
            combined = temp / f"{file_stem}-working-combined-{index + 1}.png"
            commands.append(
                [
                    binary,
                    str(working),
                    str(operand),
                    "-compose",
                    compose_operators[combination["operation"]],
                    "-composite",
                    "-threshold",
                    "50%",
                    str(combined),
                ]
            )
            working = combined

    commands.append(
        [
            binary,
            str(working),
            "-threshold",
            "50%",
            "-strip",
            str(artifacts["binary"]),
        ]
    )
    commands.append(
        [
            binary,
            str(artifacts["binary"]),
            "-morphology",
            "Edge",
            "Diamond:1",
            "-strip",
            str(artifacts["outline"]),
        ]
    )

    alpha_source = working if mask_type == "geometric" else artifacts["binary"]
    alpha_command = [binary, str(alpha_source)]
    if mask_type == "color_similarity":
        feather = float(mask_settings.get("cleanup", {}).get("feather_px", 0))
    else:
        feather = float(mask_settings.get("feather_fraction", 0.08)) * min(width, height)
    if feather > 0:
        alpha_command.extend(["-blur", f"0x{feather:.4f}"])
    if mask_settings.get("invert", False):
        alpha_command.append("-negate")
    if opacity < 1:
        alpha_command.extend(["-evaluate", "multiply", f"{opacity:.6f}"])
    alpha_command.append("-strip")
    alpha_command.append(str(artifacts["alpha"]))
    commands.append(alpha_command)
    return commands, artifacts


def adjustment_layer_commands(
    *,
    binary: str,
    active: Path,
    settings: dict[str, Any],
    mask: Path,
    temp: Path,
    file_stem: str,
) -> tuple[list[list[str]], Path]:
    """Duplicate the current composite, adjust it, and blend it through a prepared mask."""
    duplicate = temp / f"{file_stem}-duplicate.miff"
    duplicate_command = [binary, str(active), *correction_args(settings, local=True)]
    sharpen = float(settings.get("sharpen_amount", 0))
    if sharpen > 0:
        duplicate_command.extend(["-unsharp", f"0x0.8+{sharpen:.6f}+0.02"])
    duplicate_command.append(str(duplicate))
    result = temp / f"{file_stem}-composite.miff"
    composite_command = [binary, str(active), str(duplicate), str(mask), "-composite", str(result)]
    return [duplicate_command, composite_command], result


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


def base_image_command(
    input_path: Path, recipe: dict[str, Any], base: Path
) -> tuple[list[str], int, int]:
    binary = magick_binary()
    oriented_width, oriented_height = image_dimensions(input_path)
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
    base_width, base_height = image_dimensions_after_plan(input_path, recipe)
    return command, base_width, base_height


def edit_plan(
    input_path: Path, output_path: Path, recipe: dict[str, Any], temp: Path
) -> tuple[list[list[str]], list[dict[str, Any]], int]:
    binary = magick_binary()
    base = temp / "global-base.miff"
    base_command, base_width, base_height = base_image_command(input_path, recipe, base)
    commands = [base_command]
    mask_plans: list[dict[str, Any]] = []

    local = recipe.get("local_food_zone")
    if local and adjustment_has_effect(local):
        legacy_mask = {
            "type": "geometric",
            "shape": local.get("shape", "ellipse"),
            "bbox": local["bbox"],
            "feather_fraction": local.get("feather_fraction", 0.08),
            "invert": False,
        }
        local_mask_commands, artifacts = mask_commands(
            binary=binary,
            mask_settings=legacy_mask,
            basis=base,
            width=base_width,
            height=base_height,
            temp=temp,
            file_stem="legacy-local-food-zone",
            opacity=1,
        )
        commands.extend(local_mask_commands)
        mask_plans.append(
            {
                "layer_name": "legacy local food zone",
                "layer_order": 0,
                "mask_settings": legacy_mask,
                "artifacts": artifacts,
            }
        )

    for index, layer in enumerate(recipe.get("adjustment_layers", [])):
        layer_mask_commands, artifacts = mask_commands(
            binary=binary,
            mask_settings=layer["mask"],
            basis=base,
            width=base_width,
            height=base_height,
            temp=temp,
            file_stem=f"layer-{index + 1}",
            opacity=float(layer.get("opacity", 1)),
        )
        commands.extend(layer_mask_commands)
        mask_plans.append(
            {
                "layer_name": layer["name"],
                "layer_order": index + 1,
                "mask_settings": layer["mask"],
                "artifacts": artifacts,
            }
        )

    pre_edit_command_count = len(commands)
    active = base
    if local and adjustment_has_effect(local):
        layer_commands, active = adjustment_layer_commands(
            binary=binary,
            active=active,
            settings=local,
            mask=mask_plans[0]["artifacts"]["alpha"],
            temp=temp,
            file_stem="legacy-local-food-zone",
        )
        commands.extend(layer_commands)

    plan_offset = 1 if local and adjustment_has_effect(local) else 0
    for index, layer in enumerate(recipe.get("adjustment_layers", [])):
        layer_commands, active = adjustment_layer_commands(
            binary=binary,
            active=active,
            settings=layer,
            mask=mask_plans[index + plan_offset]["artifacts"]["alpha"],
            temp=temp,
            file_stem=f"layer-{index + 1}",
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
    return commands, mask_plans, pre_edit_command_count


def edit_commands(input_path: Path, output_path: Path, recipe: dict[str, Any], temp: Path) -> list[list[str]]:
    commands, _, _ = edit_plan(input_path, output_path, recipe, temp)
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


def image_statistic(path: Path, expression: str) -> str:
    result = run(
        [magick_binary(), str(path), "-format", expression, "info:"],
        capture=True,
    )
    return result.stdout.decode("utf-8").strip()


def foreground_component_count(path: Path) -> int:
    result = run(
        [
            magick_binary(),
            str(path),
            "-define",
            "connected-components:verbose=true",
            "-connected-components",
            "8",
            "null:",
        ],
        capture=True,
    )
    count = 0
    payload = result.stdout + result.stderr
    for line in payload.decode("utf-8", errors="replace").splitlines():
        match = re.search(r"gray\(([-\d.]+)(%)?\)\s*$", line)
        if not match:
            continue
        value = float(match.group(1))
        if match.group(2):
            value *= 2.55
        if value > 127.5:
            count += 1
    return count


def mask_statistics(
    plan: dict[str, Any], width: int, height: int
) -> dict[str, Any]:
    artifacts = plan["artifacts"]
    binary_mask = artifacts["binary"]
    alpha_mask = artifacts["alpha"]
    coverage = float(image_statistic(binary_mask, "%[fx:mean]"))
    if coverage <= 0:
        raise UserError(f"Mask for layer {plan['layer_name']!r} selected no pixels.")
    geometry_result = run(
        [magick_binary(), str(binary_mask), "-format", "%@", "info:"],
        capture=True,
    )
    geometry = geometry_result.stdout.decode("utf-8").strip()
    match = re.fullmatch(r"(\d+)x(\d+)\+(-?\d+)\+(-?\d+)", geometry)
    bounds = None
    if match:
        bounds = [int(match.group(index)) for index in range(3, 5)] + [
            int(match.group(1)),
            int(match.group(2)),
        ]
    settings = plan["mask_settings"]
    warnings: list[str] = []
    if coverage >= 0.995:
        warnings.append("near_full_canvas_selection")
    elif coverage >= 0.80:
        warnings.append("large_canvas_selection")
    component_count = foreground_component_count(binary_mask)
    if component_count > 1:
        warnings.append("fragmented_selection")
    if settings.get("type", "geometric") == "color_similarity":
        left, top, right, bottom = bbox_pixels(
            settings["roi"], width, height, "mask.roi"
        )
        if bounds:
            bound_x, bound_y, bound_width, bound_height = bounds
            if (
                bound_x <= left
                or bound_y <= top
                or bound_x + bound_width >= right
                or bound_y + bound_height >= bottom
            ):
                warnings.append("selection_touches_roi_boundary")
        if float(settings.get("fuzz_percent", 5)) > 12:
            warnings.append("high_fuzz_requires_extra_review")
    alpha_mean = float(image_statistic(alpha_mask, "%[fx:mean]"))
    return {
        "layer_name": plan["layer_name"],
        "layer_order": plan["layer_order"],
        "mask_type": settings.get("type", "geometric"),
        "basis": settings.get("basis", "global_base"),
        "binary_coverage_fraction": round(coverage, 6),
        "alpha_mean": round(alpha_mean, 6),
        "foreground_components": component_count,
        "bounding_box_pixels": bounds,
        "warnings": warnings,
        "binary_sha256": sha256(binary_mask),
        "outline_sha256": sha256(artifacts["outline"]),
        "alpha_sha256": sha256(alpha_mask),
    }


def resolve_layer(recipe: dict[str, Any], selector: str) -> tuple[int, dict[str, Any]]:
    layers = recipe.get("adjustment_layers", [])
    try:
        index = int(selector) - 1
    except ValueError:
        matches = [
            (index, layer)
            for index, layer in enumerate(layers)
            if layer["name"] == selector
        ]
        if len(matches) != 1:
            raise UserError("Layer selector must be a unique layer name or 1-based index.")
        return matches[0]
    if not 0 <= index < len(layers):
        raise UserError("Layer index is outside adjustment_layers.")
    return index, layers[index]


def mask_preview(
    input_path: Path,
    recipe_path: Path,
    layer_selector: str,
    output_dir: Path,
    report_path: Path | None,
) -> dict[str, Any]:
    if not input_path.is_file():
        raise UserError(f"Input file does not exist: {input_path}")
    recipe = validate_recipe(json.loads(recipe_path.read_text(encoding="utf-8")))
    layer_index, layer = resolve_layer(recipe, layer_selector)
    output_dir.mkdir(parents=True, exist_ok=True)
    resolved_report = report_path or output_dir / "mask-preview.json"
    input_hash = sha256(input_path)

    with tempfile.TemporaryDirectory(prefix="food-mask-preview-") as temp_name:
        temp = Path(temp_name)
        base = temp / "global-base.miff"
        base_command, width, height = base_image_command(input_path, recipe, base)
        commands = [base_command]
        derived_commands, artifacts = mask_commands(
            binary=magick_binary(),
            basis=base,
            mask_settings=layer["mask"],
            width=width,
            height=height,
            temp=temp,
            file_stem=f"layer-{layer_index + 1}",
            opacity=float(layer.get("opacity", 1)),
        )
        commands.extend(derived_commands)
        for command in commands:
            run(command)
        plan = {
            "layer_name": layer["name"],
            "layer_order": layer_index + 1,
            "mask_settings": layer["mask"],
            "artifacts": artifacts,
        }
        statistics_payload = mask_statistics(plan, width, height)

        red_overlay = temp / "red-overlay.png"
        overlay = temp / "overlay.png"
        red_command = [
            magick_binary(),
            "-size",
            f"{width}x{height}",
            "xc:#ff2d2d",
            str(red_overlay),
        ]
        overlay_command = [
            magick_binary(),
            str(base),
            str(red_overlay),
            str(artifacts["alpha"]),
            "-composite",
            "-strip",
            str(overlay),
        ]
        run(red_command)
        run(overlay_command)
        commands.extend([red_command, overlay_command])

        destinations = {
            "binary_mask": output_dir / "binary-mask.png",
            "outline": output_dir / "outline.png",
            "alpha_mask": output_dir / "alpha-mask.png",
            "overlay": output_dir / "overlay.png",
        }
        shutil.copy2(artifacts["binary"], destinations["binary_mask"])
        shutil.copy2(artifacts["outline"], destinations["outline"])
        shutil.copy2(artifacts["alpha"], destinations["alpha_mask"])
        shutil.copy2(overlay, destinations["overlay"])
        report = {
            "schema_version": SCHEMA_VERSION,
            "mode": "mask-preview",
            "input": str(input_path.resolve()),
            "input_sha256": input_hash,
            "basis": "global_base",
            "basis_sha256": sha256(base),
            "basis_dimensions": [width, height],
            "layer": {
                "order": layer_index + 1,
                "name": layer["name"],
                "purpose": layer["purpose"],
                "opacity": layer.get("opacity", 1),
                "mask": layer["mask"],
            },
            "statistics": statistics_payload,
            "artifacts": {
                key: {
                    "path": str(path.resolve()),
                    "sha256": sha256(path),
                    "dimensions": list(image_dimensions(path)),
                }
                for key, path in destinations.items()
            },
            "commands": [shell_display(command) for command in commands],
            "input_unchanged": input_hash == sha256(input_path),
            "non_generative_operations_only": True,
            "complete": False,
            "completion_rule": (
                "Inspect the overlay at normal size and 100% before using this mask."
            ),
        }
        write_json(report, resolved_report)
        return report


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
        temp = Path(temp_name)
        commands, mask_plans, pre_edit_command_count = edit_plan(
            input_path, output_path, recipe, temp
        )
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
            for command in commands[:pre_edit_command_count]:
                run(command)
            base_width, base_height = image_dimensions_after_plan(input_path, recipe)
            report["mask_provenance"] = [
                mask_statistics(plan, base_width, base_height) for plan in mask_plans
            ]
            for command in commands[pre_edit_command_count:]:
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
    with tempfile.TemporaryDirectory(prefix="food-mask-verify-") as temp_name:
        temp = Path(temp_name)
        planned_output = temp / "unused-output.png"
        commands, mask_plans, pre_edit_command_count = edit_plan(
            input_path, planned_output, recipe, temp
        )
        for command in commands[:pre_edit_command_count]:
            run(command)
        mask_width, mask_height = image_dimensions_after_plan(input_path, recipe)
        mask_provenance = [
            mask_statistics(plan, mask_width, mask_height) for plan in mask_plans
        ]
    for mask in mask_provenance:
        add(
            f"mask_{mask['layer_order']}_nonempty",
            mask["binary_coverage_fraction"] > 0,
            (
                f"coverage={mask['binary_coverage_fraction']}, "
                f"components={mask['foreground_components']}, "
                f"warnings={mask['warnings']}"
            ),
        )
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
        "mask_provenance": mask_provenance,
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

    preview_parser = subparsers.add_parser(
        "mask-preview", help="derive and inspect one reviewed layer mask"
    )
    preview_parser.add_argument("input", type=Path)
    preview_parser.add_argument("--recipe", type=Path, required=True)
    preview_parser.add_argument("--layer", required=True, help="layer name or 1-based index")
    preview_parser.add_argument("--output-dir", type=Path, required=True)
    preview_parser.add_argument("--report", type=Path)

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
        elif args.command == "mask-preview":
            write_json(
                mask_preview(
                    args.input,
                    args.recipe,
                    args.layer,
                    args.output_dir,
                    args.report,
                ),
                None,
            )
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
