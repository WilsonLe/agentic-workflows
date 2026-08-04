from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path
from unittest import mock

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "plugins" / "qr-code-generator" / "scripts" / "qr_code_generator.py"
SPEC = importlib.util.spec_from_file_location("qr_code_generator_tests", HELPER)
assert SPEC is not None and SPEC.loader is not None
qr = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(qr)


class QRCodeGeneratorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.outputs = self.root / "outputs"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def example(self, name: str) -> dict[str, object]:
        path = (
            ROOT
            / "plugins"
            / "qr-code-generator"
            / "skills"
            / "qr-code-generation"
            / "examples"
            / f"{name}.json"
        )
        return json.loads(path.read_text(encoding="utf-8"))

    def render(self, request: dict[str, object], output_dir: Path | None = None) -> dict[str, object]:
        validated = qr.validate_request(request)
        destination = output_dir or self.outputs
        destination.mkdir(parents=True, exist_ok=True)
        return qr.render_request(validated, destination)

    def assert_qr_error(self, category: str, request: dict[str, object]) -> None:
        with self.assertRaises(qr.QRCodeError) as context:
            qr.validate_request(request)
        self.assertEqual(context.exception.category, category)

    def test_examples_render_and_verify_with_payload_redaction(self) -> None:
        for name in ("plain-url", "styled-restaurant-menu", "image-generation-assisted"):
            with self.subTest(name=name):
                manifest = self.render(self.example(name), self.root / name)
                self.assertEqual(manifest["state"], "verified")
                self.assertFalse(manifest["raw_payload_included"])
                self.assertNotIn("payload", manifest)
                self.assertEqual(manifest["output"]["border"], self.example(name)["output"]["border"])
                self.assertEqual(manifest["output"]["scale"], self.example(name)["output"]["scale"])
                self.assertTrue(manifest["created_at"].endswith("Z"))
                self.assertTrue(manifest["verified_at"].endswith("Z"))
                self.assertIn("prompt_sha256", manifest["image_generation"])
                output = Path(manifest["output"]["path"])
                self.assertTrue(output.is_file())
                self.assertEqual(
                    qr.verify_path(output, manifest["payload_sha256"]),
                    manifest["payload_sha256"],
                )

    def test_svg_output_has_a_verified_raster_companion(self) -> None:
        request = self.example("plain-url")
        request["qr_id"] = "svg-menu"
        request["output"] = {"format": "svg", "scale": 8, "border": 4}
        manifest = self.render(request)
        self.assertEqual(manifest["state"], "verified")
        self.assertEqual(manifest["output"]["format"], "svg")
        self.assertTrue(Path(manifest["output"]["path"]).is_file())
        verification = Path(manifest["output"]["verification_image_path"])
        self.assertTrue(verification.is_file())
        self.assertEqual(qr.verify_path(verification, manifest["payload_sha256"]), manifest["payload_sha256"])

    def test_unicode_whitespace_payload_is_encoded_exactly(self) -> None:
        payload = "  Wi-Fi: café ☕\n"
        request = self.example("plain-url")
        request.update({"qr_id": "exact-unicode", "payload_type": "custom", "payload": payload})
        manifest = self.render(request)
        self.assertEqual(manifest["state"], "verified")
        self.assertEqual(manifest["payload_sha256"], qr.digest(payload.encode("utf-8")))

    def test_same_request_has_deterministic_png_bytes(self) -> None:
        request = self.example("styled-restaurant-menu")
        first = self.render(request, self.root / "first")
        second = self.render(request, self.root / "second")
        self.assertEqual(
            Path(first["output"]["path"]).read_bytes(),
            Path(second["output"]["path"]).read_bytes(),
        )
        self.assertEqual(first["output"]["sha256"], second["output"]["sha256"])

    def test_quiet_zone_and_frame_stay_outside_the_functional_qr_field(self) -> None:
        request = self.example("styled-restaurant-menu")
        validated = qr.validate_request(request)
        qr_object = qr.make_qr(validated)
        qr_image = qr.qr_png_image(qr_object, validated)
        canvas = qr.fit_canvas(qr_image, validated)
        left = (canvas.width - qr_image.width) // 2
        top = (canvas.height - qr_image.height) // 2
        quiet_zone_pixel = canvas.getpixel(
            (left + (validated["output"]["border"] * validated["output"]["scale"]) // 2, top + 2)
        )
        frame_gap = max(6, validated["output"]["scale"] // 2)
        frame_pixel = canvas.getpixel((left + qr_image.width // 2, top - frame_gap + 1))
        self.assertEqual(quiet_zone_pixel[:3], qr.rgb(validated["style_resolved"]["light"]))
        self.assertEqual(frame_pixel[:3], qr.rgb(validated["style_resolved"]["frame"]))
        manifest = self.render(request, self.root / "quiet-zone")
        self.assertEqual(manifest["qr"]["quiet_zone_modules"], 4)

    def test_raw_payload_is_opt_in_for_a_local_manifest(self) -> None:
        request = self.example("plain-url")
        request["privacy"] = {"allow_raw_payload_in_manifest": True}
        manifest = self.render(request, self.root / "raw-opt-in")
        self.assertTrue(manifest["raw_payload_included"])
        self.assertEqual(manifest["payload"], request["payload"])

    def test_image_generation_prompt_contains_no_payload(self) -> None:
        request = self.example("image-generation-assisted")
        request["payload"] = "https://example.com/menu?token=private-secret-123"
        validated = qr.validate_request(request)
        prompt = qr.build_image_generation_prompt(validated)
        self.assertIn("[QR SAFE AREA]", prompt)
        self.assertNotIn(request["payload"], prompt)
        self.assertNotIn("private-secret-123", prompt)

    def test_low_contrast_and_unauthorized_inputs_are_rejected(self) -> None:
        low_contrast = self.example("plain-url")
        low_contrast["style"] = {
            "theme": "custom",
            "dark": "#777777",
            "light": "#888888",
            "frame": "#777777",
            "background": "#FFFFFF",
        }
        self.assert_qr_error("invalid_style", low_contrast)

        background = self.root / "background.png"
        Image.new("RGB", (400, 400), "#E8DDC8").save(background)
        unauthorized = self.example("plain-url")
        unauthorized["background"] = {"path": str(background), "authorized": False}
        self.assert_qr_error("approval_required", unauthorized)

        one_dimension = self.example("plain-url")
        one_dimension["output"] = {"format": "png", "scale": 8, "border": 4, "width": 500}
        self.assert_qr_error("invalid_input", one_dimension)

        relative_logo = self.example("plain-url")
        relative_logo["logo"] = {"path": "logo.png", "authorized": True}
        self.assert_qr_error("unsafe_path", relative_logo)

    def test_long_payload_is_bounded_and_preserved(self) -> None:
        request = self.example("plain-url")
        request.update(
            {
                "qr_id": "long-payload",
                "payload_type": "custom",
                "payload": "x" * 2950,
                "error_correction": "L",
                "output": {"format": "png", "scale": 2, "border": 4},
            }
        )
        manifest = self.render(request, self.root / "long")
        self.assertEqual(manifest["state"], "verified")
        self.assertEqual(
            manifest["payload_sha256"],
            qr.digest(("x" * 2950).encode("utf-8")),
        )

        too_long = copy.deepcopy(request)
        too_long["payload"] = "x" * 4097
        self.assert_qr_error("invalid_input", too_long)

    def test_decoder_unavailable_is_not_reported_as_verified(self) -> None:
        request = self.example("plain-url")
        with mock.patch.object(
            qr.zxingcpp,
            "read_barcode",
            side_effect=RuntimeError("decoder unavailable"),
        ):
            manifest = self.render(request, self.root / "unavailable")
        self.assertEqual(manifest["state"], "verification_unavailable")
        self.assertEqual(manifest["failure_category"], "decoder_error")
        self.assertIsNone(manifest["verified_at"])

    def test_output_collision_leaves_verified_baseline_untouched(self) -> None:
        request = self.example("plain-url")
        destination = self.root / "collision"
        first = self.render(request, destination)
        with self.assertRaises(qr.QRCodeError) as context:
            self.render(request, destination)
        self.assertEqual(context.exception.category, "output_collision")
        self.assertEqual(first["state"], "verified")
        self.assertEqual(
            qr.verify_path(Path(first["output"]["path"]), first["payload_sha256"]),
            first["payload_sha256"],
        )

    def test_logo_requires_higher_error_correction_and_is_verified(self) -> None:
        logo = self.root / "logo.png"
        Image.new("RGBA", (80, 80), "#D8E3D1").save(logo)
        invalid = self.example("plain-url")
        invalid["logo"] = {"path": str(logo), "authorized": True}
        self.assert_qr_error("invalid_input", invalid)

        request = self.example("styled-restaurant-menu")
        request["qr_id"] = "logo-menu"
        request["logo"] = {"path": str(logo), "authorized": True}
        manifest = self.render(request)
        self.assertEqual(manifest["state"], "verified")

    def test_authorized_background_is_composed_outside_the_qr_safe_area(self) -> None:
        request = self.example("image-generation-assisted")
        request["qr_id"] = "composed-menu"
        baseline = self.render(request, self.root / "baseline")
        background = self.root / "generated-background.png"
        image = Image.new("RGBA", (1600, 1200), "#20372B")
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, 1599, 1200), outline="#E8DDC8", width=28)
        draw.ellipse((80, 80, 420, 420), fill="#A4C3A2")
        image.save(background)
        request["background"] = {"path": str(background), "authorized": True}
        request_path = self.root / "request.json"
        request_path.write_text(json.dumps(request), encoding="utf-8")

        composed = qr.command_compose(
            Namespace(
                input=str(request_path),
                output_dir=str(self.root / "composed"),
                qr=baseline["output"]["path"],
                background=str(background),
            )
        )
        self.assertEqual(composed["state"], "verified")
        self.assertEqual(composed["image_generation"]["status"], "background_supplied")
        self.assertTrue(Path(composed["output"]["path"]).is_file())

    def test_mismatched_payload_digest_rejects_variant(self) -> None:
        first_request = self.example("plain-url")
        second_request = copy.deepcopy(first_request)
        second_request["qr_id"] = "other-menu"
        second_request["payload"] = "https://example.com/other"
        first = self.render(first_request, self.root / "first")
        second = self.render(second_request, self.root / "second")
        with self.assertRaises(qr.QRCodeError) as context:
            qr.verify_path(Path(second["output"]["path"]), first["payload_sha256"])
        self.assertEqual(context.exception.category, "decode_mismatch")


if __name__ == "__main__":
    unittest.main()
