from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "plugins" / "excalidraw" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import excalidraw_api as api  # noqa: E402


def base(identifier: str, kind: str) -> dict[str, object]:
    return {
        "id": identifier,
        "type": kind,
        "x": 0,
        "y": 0,
        "width": 100,
        "height": 50,
        "angle": 0,
        "frameId": None,
        "boundElements": None,
    }


class ExcalidrawSceneSchemaTests(unittest.TestCase):
    def document(self) -> dict[str, object]:
        shape = base("shape", "rectangle")
        shape["boundElements"] = [
            {"id": "label", "type": "text"},
            {"id": "arrow", "type": "arrow"},
        ]
        label = base("label", "text")
        label["containerId"] = "shape"
        arrow = base("arrow", "arrow")
        arrow["points"] = [[0, 0], [100, 50]]
        arrow["startBinding"] = {
            "elementId": "shape",
            "fixedPoint": [1, 0.5],
            "mode": "inside",
        }
        arrow["endBinding"] = None
        return {
            "type": "excalidraw",
            "version": 2,
            "source": "test",
            "appState": {
                "viewBackgroundColor": "#ffffff",
                "lockedMultiSelections": {},
            },
            "elements": [shape, label, arrow],
            "files": {},
        }

    def test_complete_document_with_reciprocal_links_is_valid(self) -> None:
        payload = self.document()
        self.assertIs(api.validate_scene_content(payload, partial=False), payload)

    def test_patch_requires_content_section(self) -> None:
        with self.assertRaises(api.ExcalidrawAPIError):
            api.validate_scene_content({}, partial=True)
        api.validate_scene_content(
            {"appState": {"viewBackgroundColor": "#000000"}}, partial=True
        )

    def test_invalid_frame_binding_and_nonfinite_geometry_fail(self) -> None:
        invalid_frame = self.document()
        invalid_frame["elements"][1]["frameId"] = "shape"  # type: ignore[index]
        with self.assertRaises(api.ExcalidrawAPIError):
            api.validate_scene_content(invalid_frame, partial=False)

        invalid_binding = self.document()
        invalid_binding["elements"][0]["boundElements"] = []  # type: ignore[index]
        with self.assertRaises(api.ExcalidrawAPIError):
            api.validate_scene_content(invalid_binding, partial=False)

        invalid_geometry = self.document()
        invalid_geometry["elements"][0]["x"] = float("nan")  # type: ignore[index]
        with self.assertRaises(api.ExcalidrawAPIError):
            api.validate_scene_content(invalid_geometry, partial=False)

    def test_image_requires_matching_file_record(self) -> None:
        payload = self.document()
        image = base("image", "image")
        image["fileId"] = "file-1"
        payload["elements"].append(image)  # type: ignore[union-attr]
        with self.assertRaises(api.ExcalidrawAPIError):
            api.validate_scene_content(payload, partial=False)
        valid = copy.deepcopy(payload)
        valid["files"] = {
            "file-1": {
                "id": "file-1",
                "mimeType": "image/png",
                "dataURL": "data:image/png;base64,AA==",
            }
        }
        api.validate_scene_content(valid, partial=False)


if __name__ == "__main__":
    unittest.main()
