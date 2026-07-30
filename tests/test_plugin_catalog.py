from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


class PluginCatalogValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.repository = Path(self.temporary.name) / "repository"
        shutil.copytree(
            ROOT,
            self.repository,
            ignore=shutil.ignore_patterns(
                ".git",
                ".ruff_cache",
                ".venv",
                "__pycache__",
                "*.pyc",
            ),
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def validate(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "scripts/validate_plugin_packages.py"],
            cwd=self.repository,
            check=False,
            capture_output=True,
            text=True,
        )

    def assert_validation_failure(self, marker: str) -> None:
        result = self.validate()
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(marker, result.stderr)

    def test_catalog_covers_every_marketplace_package(self) -> None:
        catalog = yaml.safe_load(
            (self.repository / "catalog" / "plugins-v1.yaml").read_text()
        )
        marketplace = json.loads(
            (
                self.repository / ".agents" / "plugins" / "marketplace.json"
            ).read_text()
        )
        self.assertEqual(
            catalog["marketplace"]["plugin_order"],
            [entry["name"] for entry in marketplace["plugins"]],
        )
        self.assertEqual(
            {package["name"] for package in catalog["packages"]},
            {entry["name"] for entry in marketplace["plugins"]},
        )
        self.assertEqual(
            catalog["marketplace"]["plugin_order"].count("literature-review"),
            1,
        )
        literature = next(
            package
            for package in catalog["packages"]
            if package["name"] == "literature-review"
        )
        self.assertEqual(
            [skill["name"] for skill in literature["skills"]],
            ["literature-review-workflow"],
        )

    def test_literature_review_central_route_and_mirror_are_declared(self) -> None:
        catalog = yaml.safe_load(
            (self.repository / "catalog" / "plugins-v1.yaml").read_text()
        )
        central = next(
            package
            for package in catalog["packages"]
            if package["name"] == "amsoft-agentic-workflows"
        )
        self.assertEqual(
            [
                skill["name"]
                for skill in central["skills"]
                if "literature-review" in skill["name"]
            ],
            [
                "amsoft-literature-review-workflow",
                "amsoft-systematic-literature-review-workflow",
            ],
        )
        router = (
            self.repository
            / "plugins"
            / "amsoft-agentic-workflows"
            / "skills"
            / "amsoft-agentic-workflows"
            / "SKILL.md"
        ).read_text()
        self.assertIn("`amsoft-literature-review-workflow`", router)
        self.assertIn("`amsoft-systematic-literature-review-workflow`", router)
        self.assertIn("AMSoft Systematic Literature Review", router)

    def test_trend_to_product_catalog_and_central_routes_are_declared(self) -> None:
        catalog = yaml.safe_load(
            (self.repository / "catalog" / "plugins-v1.yaml").read_text()
        )
        package = next(
            package
            for package in catalog["packages"]
            if package["name"] == "trend-to-product"
        )
        self.assertEqual(
            [skill["name"] for skill in package["skills"]],
            [
                "trend-product-design",
                "trend-product-discovery",
                "trend-product-onboarding",
                "trend-product-operations",
                "trend-product-opportunity",
            ],
        )
        central = next(
            package
            for package in catalog["packages"]
            if package["name"] == "amsoft-agentic-workflows"
        )
        central_names = {skill["name"] for skill in central["skills"]}
        for name in (
            "amsoft-trend-product-design",
            "amsoft-trend-product-discovery",
            "amsoft-trend-product-onboarding",
            "amsoft-trend-product-operations",
            "amsoft-trend-product-opportunity",
        ):
            self.assertIn(name, central_names)
        self.assertIn(
            "trend-to-product-skills",
            {mirror["name"] for mirror in catalog["mirrors"]},
        )

    def test_erpnext_manifest_drift_fails(self) -> None:
        manifest = (
            self.repository
            / "plugins"
            / "erpnext-operations"
            / ".codex-plugin"
            / "plugin.json"
        )
        payload = json.loads(manifest.read_text())
        payload["name"] = "wrong-name"
        manifest.write_text(json.dumps(payload))
        self.assert_validation_failure("name must match its directory")

    def test_erpnext_registry_version_drift_fails(self) -> None:
        manifest = (
            self.repository
            / "plugins"
            / "erpnext-operations"
            / ".codex-plugin"
            / "plugin.json"
        )
        version = json.loads(manifest.read_text())["version"]
        registry = (
            self.repository
            / "plugins"
            / "amsoft-agentic-workflows"
            / "skills"
            / "amsoft-agentic-workflows"
            / "references"
            / "plugin-registry.md"
        )
        rows = registry.read_text().splitlines()
        rows = [
            (
                row.replace(f"`{version}`", "`0.0.0-invalid`")
                if row.startswith("| `erpnext-operations` |")
                else row
            )
            for row in rows
        ]
        registry.write_text("\n".join(rows) + "\n")
        self.assert_validation_failure(
            "registry does not contain the current erpnext-operations version"
        )

    def test_required_agent_metadata_fails_when_missing(self) -> None:
        metadata = (
            self.repository
            / "plugins"
            / "image-editing"
            / "skills"
            / "food-image-editing"
            / "agents"
            / "openai.yaml"
        )
        metadata.unlink()
        self.assert_validation_failure("is required by the catalog")

    def test_broken_link_in_any_package_fails(self) -> None:
        skill = (
            self.repository
            / "plugins"
            / "erpnext-operations"
            / "skills"
            / "erpnext-sales-crm"
            / "SKILL.md"
        )
        skill.write_text(f"{skill.read_text()}\n[broken](references/missing.md)\n")
        self.assert_validation_failure("links to missing path")

    def test_declared_mirror_drift_fails(self) -> None:
        skill = (
            self.repository
            / "plugins"
            / "amsoft-agentic-workflows"
            / "skills"
            / "food-image-editing"
            / "SKILL.md"
        )
        skill.write_text(f"{skill.read_text()}\nmirror drift\n")
        self.assert_validation_failure("generated mirror content differs")

    def test_generated_marketplace_drift_fails(self) -> None:
        marketplace = self.repository / ".agents" / "plugins" / "marketplace.json"
        payload = json.loads(marketplace.read_text())
        payload["plugins"].reverse()
        marketplace.write_text(json.dumps(payload))
        self.assert_validation_failure("marketplace plugin order or inventory differs")

    def test_runtime_cache_files_do_not_enter_mirrors(self) -> None:
        cache = (
            self.repository
            / "plugins"
            / "restaurant-marketing"
            / "skills"
            / "restaurant-marketing-management"
            / "scripts"
            / "__pycache__"
        )
        cache.mkdir()
        (cache / "restaurant_marketing.cpython-312.pyc").write_bytes(
            b"\xcb\x00runtime-cache"
        )
        result = self.validate()
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
