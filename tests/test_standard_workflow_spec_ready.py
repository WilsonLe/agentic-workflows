from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC_READY = (
    ROOT
    / "plugins"
    / "agentic-workflows"
    / "skills"
    / "standard-development-workflow"
    / "references"
    / "spec-ready.md"
)


class StandardWorkflowSpecReadyTests(unittest.TestCase):
    def test_ui_requests_require_a_complete_github_visual_package(self) -> None:
        text = SPEC_READY.read_text(encoding="utf-8")
        normalized = " ".join(text.split())
        for marker in (
            "UI change requests: mandatory visual package",
            "every image supplied by the user",
            "preserve the request order",
            "upload each image to GitHub so it is embedded in the issue body",
            "Request images: none",
            "exported PNG sketches",
            "Tool-neutral issue text",
            "No silent omission",
            "one or more inspectable exported PNG sketches",
        ):
            self.assertIn(marker, normalized)
        self.assertNotIn("excalidraw", text.lower())


if __name__ == "__main__":
    unittest.main()
