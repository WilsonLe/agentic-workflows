from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "plugins" / "excalidraw" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import excalidraw_render as render  # noqa: E402


class ExcalidrawRenderTests(unittest.TestCase):
    def document(self) -> dict[str, object]:
        return json.loads(
            (
                ROOT
                / "plugins"
                / "excalidraw"
                / "skills"
                / "excalidraw-scene-operations"
                / "examples"
                / "minimal-scene.json"
            ).read_text(encoding="utf-8")
        )

    def test_accepts_raw_scene_document(self) -> None:
        document = self.document()
        self.assertEqual(render.complete_scene_document(document), document)

    def test_extracts_complete_scene_from_api_helper_envelope(self) -> None:
        document = self.document()
        envelope = {
            "operation": "scene-content",
            "method": "GET",
            "result": document,
            "rate_limit": {},
        }
        self.assertEqual(render.complete_scene_document(envelope), document)

    def test_rejects_partial_patch_envelope(self) -> None:
        with self.assertRaisesRegex(render.ExcalidrawRenderError, "complete scene document"):
            render.complete_scene_document(
                {
                    "operation": "scene-content-patch",
                    "result": {"appState": {"viewBackgroundColor": "#fff"}},
                }
            )

    def test_invokes_pinned_npx_renderer_with_private_temporary_input(self) -> None:
        document = self.document()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path = root / "api-response.json"
            output_path = root / "preview.png"
            input_path.write_text(
                json.dumps(
                    {
                        "operation": "scene-content",
                        "result": document,
                    }
                ),
                encoding="utf-8",
            )
            temporary_input: Path | None = None

            def fake_run(
                command: list[str], **_: object
            ) -> subprocess.CompletedProcess[str]:
                nonlocal temporary_input
                self.assertEqual(command[0], "/usr/bin/npx")
                self.assertEqual(command[1:3], ["--yes", "excalidraw-export-cli@1.0.0"])
                temporary_input = Path(command[3])
                self.assertTrue(Path(command[4]).name == "render.png")
                self.assertNotEqual(Path(command[4]), output_path.resolve())
                self.assertEqual(temporary_input.stat().st_mode & 0o777, 0o600)
                self.assertEqual(
                    json.loads(temporary_input.read_text(encoding="utf-8")),
                    document,
                )
                Path(command[4]).write_bytes(b"\x89PNG\r\n\x1a\nsynthetic")
                return subprocess.CompletedProcess(command, 0, "", "")

            with (
                mock.patch.object(render.shutil, "which", return_value="/usr/bin/npx"),
                mock.patch.object(render.subprocess, "run", side_effect=fake_run),
            ):
                result = render.render_scene(input_path, output_path)

            self.assertEqual(result.output_path, output_path.resolve())
            self.assertEqual(output_path.read_bytes(), b"\x89PNG\r\n\x1a\nsynthetic")
            self.assertEqual(result.element_count, 0)
            self.assertEqual(result.file_count, 0)
            self.assertIsNotNone(temporary_input)
            self.assertFalse(temporary_input.exists())

    def test_rejects_renderer_failure_without_writing_scene(self) -> None:
        document = self.document()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path = root / "scene.json"
            output_path = root / "preview.png"
            input_path.write_text(json.dumps(document), encoding="utf-8")
            output_path.write_bytes(b"previous-preview")
            failed = subprocess.CompletedProcess(
                ["renderer"], 17, "", "renderer failed safely"
            )
            with (
                mock.patch.object(render.shutil, "which", return_value="/usr/bin/npx"),
                mock.patch.object(render.subprocess, "run", return_value=failed),
            ):
                with self.assertRaisesRegex(render.ExcalidrawRenderError, "exit code 17"):
                    render.render_scene(input_path, output_path)
            self.assertEqual(output_path.read_bytes(), b"previous-preview")

    def test_does_not_overwrite_input(self) -> None:
        document = self.document()
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "scene.json"
            input_path.write_text(json.dumps(document), encoding="utf-8")
            with self.assertRaisesRegex(render.ExcalidrawRenderError, "overwrite"):
                render.render_scene(input_path, input_path)


if __name__ == "__main__":
    unittest.main()
