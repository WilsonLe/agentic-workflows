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


if __name__ == "__main__":
    unittest.main()
