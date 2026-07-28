#!/usr/bin/env python3

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

import food_image


def recipe(rotate_deg: float) -> dict:
    return {
        "schema_version": 2,
        "purpose": "Rotation regression test",
        "angle": "overhead",
        "angle_confidence": 1,
        "hero_bbox": [0.1, 0.1, 0.8, 0.8],
        "notes": ["Synthetic geometry only; no food-image claim."],
        "rotate_deg": rotate_deg,
        "white_balance_rgb": [1, 1, 1],
        "exposure_ev": 0,
        "contrast": 0,
        "saturation": 1,
        "levels": {
            "black_percent": 0,
            "white_percent": 0,
            "gamma": 1,
        },
        "quality": 92,
    }


def composition_brief() -> dict:
    return {
        "intent": "hero-led",
        "target_aspect_ratio": "4:5",
        "balance_strategy": "centered",
        "primary_anchor": [0.1, 0.1, 0.8, 0.8],
        "secondary_anchors": [],
        "visual_flow": "The plate is the single visual anchor.",
        "negative_space_side": "none",
        "plate_edge_policy": "preserve",
        "text_safe_side": "none",
        "truth_risks": ["Do not flatten intentional food height."],
    }


class RotationTests(unittest.TestCase):
    def test_any_finite_rotation_is_accepted_and_normalized(self) -> None:
        self.assertEqual(food_image.rotation_degrees(recipe(90)), 90)
        self.assertEqual(food_image.rotation_degrees(recipe(450)), 90)
        self.assertEqual(food_image.rotation_degrees(recipe(270)), -90)
        self.assertEqual(food_image.rotation_degrees(recipe(-810)), -90)

        for invalid in (float("inf"), float("-inf"), float("nan")):
            with self.assertRaises(food_image.UserError):
                food_image.validate_recipe(recipe(invalid))

    def test_quarter_turn_swaps_dimensions_without_padding(self) -> None:
        self.assertEqual(food_image.safe_rotated_dimensions(120, 200, 90), (200, 120))
        self.assertEqual(food_image.safe_rotated_dimensions(120, 200, 270), (200, 120))

    def test_edit_plan_executes_quarter_turn(self) -> None:
        with tempfile.TemporaryDirectory(prefix="food-image-rotation-test-") as name:
            directory = Path(name)
            source = directory / "portrait.png"
            base = directory / "base.miff"
            subprocess.run(
                [
                    food_image.magick_binary(),
                    "-size",
                    "120x200",
                    "gradient:#111111-#eeeeee",
                    str(source),
                ],
                check=True,
            )
            settings = food_image.validate_recipe(recipe(90))
            command, width, height = food_image.base_image_command(source, settings, base)
            subprocess.run(command, check=True)

            self.assertEqual((width, height), (200, 120))
            self.assertEqual(food_image.image_dimensions(base), (200, 120))
            self.assertIn("-rotate", command)
            self.assertEqual(command[command.index("-rotate") + 1], "90.000000")


class PerspectiveCropTests(unittest.TestCase):
    def perspective_recipe(self, quad: list[list[float]]) -> dict:
        settings = recipe(0)
        settings["schema_version"] = 3
        settings["composition_brief"] = composition_brief()
        settings["perspective_crop"] = {"source_quad": quad}
        settings["crop"] = [0, 0, 1, 1]
        return settings

    def test_identity_quad_preserves_dimensions(self) -> None:
        geometry = food_image.perspective_geometry(
            {"source_quad": [[0, 0], [1, 0], [1, 1], [0, 1]]}, 120, 200
        )
        self.assertEqual(geometry["output_dimensions"], [120, 200])

    def test_trapezoid_is_rectified_before_rectangular_crop(self) -> None:
        with tempfile.TemporaryDirectory(prefix="food-image-perspective-test-") as name:
            directory = Path(name)
            source = directory / "source.png"
            base = directory / "base.miff"
            subprocess.run(
                [
                    food_image.magick_binary(),
                    "-size",
                    "160x100",
                    "gradient:#111111-#eeeeee",
                    str(source),
                ],
                check=True,
            )
            settings = food_image.validate_recipe(
                self.perspective_recipe(
                    [[0.1, 0.1], [0.9, 0.16], [0.84, 0.9], [0.16, 0.86]]
                )
            )
            command, width, height = food_image.base_image_command(
                source, settings, base
            )
            subprocess.run(command, check=True)

            self.assertEqual(food_image.image_dimensions(base), (width, height))
            self.assertIn("-distort", command)
            self.assertEqual(command[command.index("-distort") + 1], "Perspective")
            provenance = food_image.geometry_provenance(source, settings)
            self.assertEqual(
                provenance["perspective_crop"]["output_dimensions"], [width, height]
            )

    def test_invalid_quads_fail_with_actionable_errors(self) -> None:
        invalid_quads = [
            [[0, 0], [1, 0], [0, 1]],
            [[0, 0], [0, 1], [1, 1], [1, 0]],
            [[0, 0], [1, 0], [0, 1], [1, 1]],
            [[0, 0], [1, 0], [0.5, 0.4], [0, 1]],
            [[0, 0], [1, 0], [1, 0], [0, 1]],
            [[-0.01, 0], [1, 0], [1, 1], [0, 1]],
            [[0, 0], [float("nan"), 0], [1, 1], [0, 1]],
            [[0, 0], [float("inf"), 0], [1, 1], [0, 1]],
        ]
        for quad in invalid_quads:
            with self.subTest(quad=quad), self.assertRaises(food_image.UserError):
                food_image.validate_recipe(self.perspective_recipe(quad))


if __name__ == "__main__":
    unittest.main()
