from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = (
    ROOT
    / "plugins"
    / "image-editing"
    / "skills"
    / "food-image-editing"
    / "scripts"
    / "food_image.py"
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class FoodImageEditingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not shutil.which("magick"):
            raise unittest.SkipTest("ImageMagick 7 is not installed")

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="food-image-test-")
        self.root = Path(self.temp.name)
        self.source = self.root / "source.png"
        subprocess.run(
            [
                "magick",
                "-size",
                "160x100",
                "xc:#303030",
                "-fill",
                "#d44b32",
                "-draw",
                "rectangle 20,20 90,80",
                "-draw",
                "rectangle 125,25 150,75",
                "-fill",
                "#303030",
                "-draw",
                "circle 70,50 70,48",
                str(self.source),
            ],
            check=True,
        )
        self.source_hash = digest(self.source)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_tool(
        self, *arguments: str, expected: int = 0
    ) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            ["python3", str(TOOL), *arguments],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(
            result.returncode,
            expected,
            msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )
        return result

    def write_recipe(
        self,
        *,
        schema_version: int = 2,
        mask: dict[str, object] | None = None,
        layers: list[dict[str, object]] | None = None,
    ) -> Path:
        if layers is None:
            layers = [
                {
                    "name": "warm connected food",
                    "purpose": "lift only the connected red food region",
                    "source": "duplicate_current",
                    "opacity": 0.8,
                    "mask": mask
                    or {
                        "type": "color_similarity",
                        "basis": "global_base",
                        "seed": [0.3, 0.5],
                        "roi": [0.0, 0.0, 1.0, 1.0],
                        "colorspace": "Lab",
                        "fuzz_percent": 8,
                        "cleanup": {
                            "open_px": 1,
                            "close_px": 3,
                            "grow_px": 0,
                            "feather_px": 3,
                        },
                        "combine": [
                            {
                                "operation": "intersect",
                                "mask": {
                                    "type": "geometric",
                                    "shape": "rectangle",
                                    "bbox": [0.1, 0.1, 0.45, 0.8],
                                    "feather_fraction": 0,
                                    "invert": False,
                                },
                            },
                            {
                                "operation": "union",
                                "mask": {
                                    "type": "geometric",
                                    "shape": "ellipse",
                                    "bbox": [0.5, 0.4, 0.2, 0.2],
                                    "feather_fraction": 0,
                                    "invert": False,
                                },
                            },
                            {
                                "operation": "subtract",
                                "mask": {
                                    "type": "geometric",
                                    "shape": "ellipse",
                                    "bbox": [0.22, 0.38, 0.12, 0.24],
                                    "feather_fraction": 0,
                                    "invert": False,
                                },
                            }
                        ],
                        "invert": False,
                    },
                    "exposure_ev": 0.1,
                    "contrast": 0,
                    "saturation": 1,
                    "sharpen_amount": 0,
                }
            ]
        recipe = {
            "schema_version": schema_version,
            "purpose": "synthetic food mask verification",
            "angle": "overhead",
            "angle_confidence": 1,
            "hero_bbox": [0.1, 0.1, 0.5, 0.8],
            "crop": [0, 0, 1, 1],
            "rotate_deg": 0,
            "white_balance_rgb": [1, 1, 1],
            "exposure_ev": 0,
            "levels": {
                "black_percent": 0,
                "white_percent": 0,
                "gamma": 1,
            },
            "contrast": 0,
            "saturation": 1,
            "local_food_zone": None,
            "adjustment_layers": layers,
            "global_sharpen": {
                "radius": 0,
                "sigma": 0.8,
                "amount": 0,
                "threshold": 0.02,
            },
            "resize": None,
            "quality": 92,
            "notes": ["Synthetic fixture; no scene semantics are inferred."],
        }
        path = self.root / f"recipe-{len(list(self.root.glob('recipe-*.json')))}.json"
        path.write_text(json.dumps(recipe), encoding="utf-8")
        return path

    def pixel_gray(self, path: Path, x: int, y: int) -> float:
        result = subprocess.run(
            [
                "magick",
                str(path),
                "-format",
                f"%[fx:p{{{x},{y}}}.r]",
                "info:",
            ],
            check=True,
            stdout=subprocess.PIPE,
            text=True,
        )
        return float(result.stdout)

    def test_color_mask_preview_is_connected_cleaned_combined_and_feathered(self) -> None:
        recipe = self.write_recipe()
        preview = self.root / "preview"
        self.run_tool(
            "mask-preview",
            str(self.source),
            "--recipe",
            str(recipe),
            "--layer",
            "warm connected food",
            "--output-dir",
            str(preview),
        )
        report = json.loads((preview / "mask-preview.json").read_text())
        binary = preview / "binary-mask.png"
        alpha = preview / "alpha-mask.png"

        self.assertGreater(self.pixel_gray(binary, 60, 40), 0.99)
        self.assertLess(self.pixel_gray(binary, 137, 50), 0.01)
        self.assertLess(self.pixel_gray(binary, 44, 50), 0.01)
        self.assertGreater(self.pixel_gray(binary, 70, 50), 0.99)
        self.assertGreater(self.pixel_gray(binary, 105, 50), 0.99)

        alpha_bytes = subprocess.run(
            ["magick", str(alpha), "-depth", "8", "gray:-"],
            check=True,
            stdout=subprocess.PIPE,
        ).stdout
        self.assertTrue(any(0 < value < 255 for value in alpha_bytes))
        self.assertEqual(report["statistics"]["foreground_components"], 1)
        self.assertTrue(report["input_unchanged"])
        self.assertEqual(digest(self.source), self.source_hash)
        self.assertEqual(
            {
                "alpha-mask.png",
                "binary-mask.png",
                "mask-preview.json",
                "outline.png",
                "overlay.png",
            },
            {path.name for path in preview.iterdir()},
        )

    def test_edit_records_mask_provenance_and_uses_stable_basis(self) -> None:
        first_layer = {
            "name": "global color shift",
            "purpose": "prove later masks do not derive from earlier layer pixels",
            "source": "duplicate_current",
            "opacity": 1,
            "mask": {
                "type": "geometric",
                "shape": "rectangle",
                "bbox": [0, 0, 1, 1],
                "feather_fraction": 0,
                "invert": False,
            },
            "exposure_ev": 0,
            "contrast": 0,
            "saturation": 0.75,
            "sharpen_amount": 0,
        }
        color_layer = json.loads(self.write_recipe().read_text())["adjustment_layers"][0]
        recipe = self.write_recipe(layers=[first_layer, color_layer])
        preview = self.root / "stable-preview"
        self.run_tool(
            "mask-preview",
            str(self.source),
            "--recipe",
            str(recipe),
            "--layer",
            "2",
            "--output-dir",
            str(preview),
        )
        preview_report = json.loads((preview / "mask-preview.json").read_text())
        output = self.root / "edited.png"
        edit_report = self.root / "edit.json"
        self.run_tool(
            "edit",
            str(self.source),
            str(output),
            "--recipe",
            str(recipe),
            "--report",
            str(edit_report),
        )
        edit_payload = json.loads(edit_report.read_text())
        second_mask = edit_payload["mask_provenance"][1]
        self.assertEqual(
            preview_report["statistics"]["binary_sha256"],
            second_mask["binary_sha256"],
        )
        self.assertEqual(edit_payload["input_unchanged"], True)
        self.assertEqual(digest(self.source), self.source_hash)
        self.assertTrue(output.is_file())
        verify_report = self.root / "verify.json"
        self.run_tool(
            "verify",
            str(self.source),
            str(output),
            "--recipe",
            str(recipe),
            "--output",
            str(verify_report),
        )
        verify_payload = json.loads(verify_report.read_text())
        self.assertEqual(len(verify_payload["mask_provenance"]), 2)
        self.assertTrue(
            any(check["name"] == "mask_2_nonempty" for check in verify_payload["checks"])
        )

    def test_schema_v1_geometric_recipe_remains_supported(self) -> None:
        mask = {
            "shape": "ellipse",
            "bbox": [0.1, 0.1, 0.5, 0.8],
            "feather_fraction": 0.05,
            "invert": False,
        }
        recipe = self.write_recipe(schema_version=1, mask=mask)
        output = self.root / "legacy.png"
        dry_run = self.run_tool(
            "edit",
            str(self.source),
            str(output),
            "--recipe",
            str(recipe),
            "--dry-run",
        )
        payload = json.loads(dry_run.stdout)
        self.assertEqual(payload["recipe"]["schema_version"], 1)
        self.assertIn("ellipse", payload["commands"][1])
        self.run_tool(
            "edit",
            str(self.source),
            str(output),
            "--recipe",
            str(recipe),
        )
        self.assertTrue(output.is_file())
        self.assertGreaterEqual(self.pixel_gray(output, 50, 50), 0)
        self.assertEqual(digest(self.source), self.source_hash)

    def test_invalid_and_empty_masks_fail_safely(self) -> None:
        invalid_mask = {
            "type": "color_similarity",
            "seed": [0.9, 0.9],
            "roi": [0, 0, 0.5, 0.5],
            "colorspace": "RGB",
            "fuzz_percent": 5,
            "cleanup": {},
        }
        invalid_recipe = self.write_recipe(mask=invalid_mask)
        invalid = self.run_tool(
            "mask-preview",
            str(self.source),
            "--recipe",
            str(invalid_recipe),
            "--layer",
            "1",
            "--output-dir",
            str(self.root / "invalid"),
            expected=2,
        )
        self.assertIn("seed must be inside", invalid.stderr)

        empty_mask = {
            "type": "color_similarity",
            "basis": "global_base",
            "seed": [0.3, 0.5],
            "roi": [0, 0, 1, 1],
            "colorspace": "Luv",
            "fuzz_percent": 5,
            "cleanup": {"open_px": 0, "close_px": 0, "grow_px": 0, "feather_px": 0},
            "combine": [
                {
                    "operation": "subtract",
                    "mask": {
                        "type": "geometric",
                        "shape": "rectangle",
                        "bbox": [0, 0, 1, 1],
                        "feather_fraction": 0,
                        "invert": False,
                    },
                }
            ],
            "invert": False,
        }
        empty_recipe = self.write_recipe(mask=empty_mask)
        empty = self.run_tool(
            "mask-preview",
            str(self.source),
            "--recipe",
            str(empty_recipe),
            "--layer",
            "1",
            "--output-dir",
            str(self.root / "empty"),
            expected=2,
        )
        self.assertIn("selected no pixels", empty.stderr)
        self.assertEqual(digest(self.source), self.source_hash)


if __name__ == "__main__":
    unittest.main()
