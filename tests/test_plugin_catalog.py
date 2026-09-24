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

    def test_agent_orchestration_catalog_and_central_route_are_declared(self) -> None:
        catalog = yaml.safe_load(
            (self.repository / "catalog" / "plugins-v1.yaml").read_text()
        )
        package = next(
            package
            for package in catalog["packages"]
            if package["name"] == "agent-orchestration"
        )
        self.assertEqual(
            [skill["name"] for skill in package["skills"]],
            ["orchestration", "sdlc-loop"],
        )
        self.assertTrue(
            any(
                "stable realpath-normalized same-worktree claims" in dependency
                for dependency in package["runtime_dependencies"]
            )
        )
        self.assertTrue(
            any(
                "Same unchanged full base/head review and verification pair"
                in dependency
                for dependency in package["runtime_dependencies"]
            )
        )
        central = next(
            package
            for package in catalog["packages"]
            if package["name"] == "amsoft-agentic-workflows"
        )
        self.assertIn(
            "amsoft-orchestration",
            {skill["name"] for skill in central["skills"]},
        )
        self.assertIn(
            "amsoft-sdlc-loop",
            {skill["name"] for skill in central["skills"]},
        )
        self.assertIn(
            "sdlc-loop-skill",
            {mirror["name"] for mirror in catalog["mirrors"]},
        )
        router = (
            self.repository
            / "plugins"
            / "amsoft-agentic-workflows"
            / "skills"
            / "amsoft-agentic-workflows"
            / "SKILL.md"
        ).read_text()
        self.assertIn("archived and its shared-worktree claim released", router)
        self.assertIn("v4 ownership ambiguity fails", router)
        self.assertEqual(
            {
                "agent-orchestration-skill",
                "agent-orchestration-helper",
                "agent-orchestration-schemas",
                "agent-orchestration-examples",
            },
            {
                mirror["name"]
                for mirror in catalog["mirrors"]
                if mirror["name"].startswith("agent-orchestration-")
            },
        )

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

    def test_qr_code_catalog_and_central_route_are_declared(self) -> None:
        catalog = yaml.safe_load(
            (self.repository / "catalog" / "plugins-v1.yaml").read_text()
        )
        package = next(
            package
            for package in catalog["packages"]
            if package["name"] == "qr-code-generator"
        )
        self.assertEqual(
            [skill["name"] for skill in package["skills"]],
            ["qr-code-generation"],
        )
        self.assertEqual(
            package["runtime_dependencies"],
            [
                "Python 3.12 or newer",
                "segno==1.6.6",
                "Pillow==11.3.0",
                "zxing-cpp==2.3.0",
                "Host image capability only when an approved theme background is requested",
            ],
        )
        central = next(
            package
            for package in catalog["packages"]
            if package["name"] == "amsoft-agentic-workflows"
        )
        self.assertIn(
            "amsoft-qr-code-generation",
            {skill["name"] for skill in central["skills"]},
        )
        self.assertIn(
            "scripts/qr_code_generator.py",
            central["executables"],
        )
        self.assertEqual(
            {
                "qr-code-generation-skills",
                "qr-code-generator-helper",
            },
            {
                mirror["name"]
                for mirror in catalog["mirrors"]
                if mirror["name"].startswith("qr-code-generator")
                or mirror["name"].startswith("qr-code-generation")
            },
        )
        router = (
            self.repository
            / "plugins"
            / "amsoft-agentic-workflows"
            / "skills"
            / "amsoft-agentic-workflows"
            / "SKILL.md"
        ).read_text()
        self.assertIn("`amsoft-qr-code-generation`", router)
        self.assertIn("decoder verification", router)

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

    def test_top_level_plugin_license_drift_fails(self) -> None:
        manifest = (
            self.repository
            / "plugins"
            / "agent-orchestration"
            / ".codex-plugin"
            / "plugin.json"
        )
        payload = json.loads(manifest.read_text())
        payload["license"] = "LicenseRef-AMSoft-Proprietary"
        manifest.write_text(json.dumps(payload))
        self.assert_validation_failure(
            "manifest license must be MIT"
        )
        payload["license"] = "MIT"
        manifest.write_text(json.dumps(payload))
        (
            self.repository / "plugins" / "agent-orchestration" / "LICENSE"
        ).write_text("different license\n")
        self.assert_validation_failure(
            "differs from the canonical MIT License"
        )

    def test_nested_third_party_license_and_attribution_are_preserved(self) -> None:
        nested_license = (
            self.repository
            / "plugins"
            / "amsoft-agentic-workflows"
            / "skills"
            / "humanizer"
            / "LICENSE"
        ).read_text()
        nested_skill = (
            self.repository
            / "plugins"
            / "amsoft-agentic-workflows"
            / "skills"
            / "humanizer"
            / "SKILL.md"
        ).read_text()
        self.assertTrue(nested_license.startswith("MIT License"))
        self.assertIn("The original and this adaptation", nested_skill)

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

    def test_broken_markdown_anchor_fails(self) -> None:
        skill = (
            self.repository
            / "plugins"
            / "erpnext-operations"
            / "skills"
            / "erpnext-sales-crm"
            / "SKILL.md"
        )
        skill.write_text(f"{skill.read_text()}\n[broken](#missing-heading)\n")
        self.assert_validation_failure("links to missing anchor #missing-heading")

    def test_ambiguous_packaged_executable_path_fails(self) -> None:
        skill = (
            self.repository
            / "plugins"
            / "calorie-tracker"
            / "skills"
            / "calorie-tracker"
            / "SKILL.md"
        )
        skill.write_text(f"{skill.read_text()}\n`python scripts/example.py`\n")
        self.assert_validation_failure("uses ambiguous executable path scripts/example.py")

    def test_missing_rooted_packaged_reference_fails(self) -> None:
        skill = (
            self.repository
            / "plugins"
            / "calorie-tracker"
            / "skills"
            / "calorie-tracker"
            / "SKILL.md"
        )
        skill.write_text(f"{skill.read_text()}\n`<plugin-root>/scripts/missing.py`\n")
        self.assert_validation_failure(
            "references missing <plugin-root>/scripts/missing.py"
        )

    def test_unrooted_inline_asset_path_fails(self) -> None:
        skill = (
            self.repository
            / "plugins"
            / "calorie-tracker"
            / "skills"
            / "calorie-tracker"
            / "SKILL.md"
        )
        skill.write_text(f"{skill.read_text()}\nUse `templates/example.json`.\n")
        self.assert_validation_failure(
            "uses unrooted inline asset path templates/example.json"
        )

    def test_agent_metadata_prompt_without_skill_invocation_fails(self) -> None:
        metadata = (
            self.repository
            / "plugins"
            / "calorie-tracker"
            / "skills"
            / "calorie-tracker"
            / "agents"
            / "openai.yaml"
        )
        payload = yaml.safe_load(metadata.read_text())
        payload["interface"]["default_prompt"] = "Track a meal."
        metadata.write_text(yaml.safe_dump(payload, sort_keys=False))
        self.assert_validation_failure("default prompt must invoke $calorie-tracker")

    def test_registry_source_drift_fails(self) -> None:
        registry = (
            self.repository
            / "plugins"
            / "amsoft-agentic-workflows"
            / "skills"
            / "amsoft-agentic-workflows"
            / "references"
            / "plugin-registry.md"
        )
        registry.write_text(
            registry.read_text().replace(
                "`plugins/calorie-tracker` | `amsoft`",
                "`plugins/wrong-source` | `amsoft`",
                1,
            )
        )
        self.assert_validation_failure(
            "registry source for calorie-tracker must be catalog path"
        )

    def test_registry_marketplace_drift_fails(self) -> None:
        registry = (
            self.repository
            / "plugins"
            / "amsoft-agentic-workflows"
            / "skills"
            / "amsoft-agentic-workflows"
            / "references"
            / "plugin-registry.md"
        )
        lines = registry.read_text().splitlines()
        lines = [
            line.replace("| `amsoft` |", "| `wrong` |")
            if line.startswith("| `calorie-tracker` |")
            else line
            for line in lines
        ]
        registry.write_text("\n".join(lines) + "\n")
        self.assert_validation_failure("registry marketplace for calorie-tracker must be amsoft")

    def test_registry_source_manifest_version_mismatch_fails(self) -> None:
        source = self.repository / "external-source"
        manifest = source / ".codex-plugin" / "plugin.json"
        manifest.parent.mkdir(parents=True)
        manifest.write_text(
            json.dumps(
                {
                    "name": "standard-development-workflow",
                    "version": "0.0.0-wrong",
                }
            )
        )
        registry = (
            self.repository
            / "plugins"
            / "amsoft-agentic-workflows"
            / "skills"
            / "amsoft-agentic-workflows"
            / "references"
            / "plugin-registry.md"
        )
        lines = registry.read_text().splitlines()
        lines = [
            line.replace(
                "`external-unavailable:standard-development-workflow@personal`",
                f"`{source}`",
            ).replace("| not-live-verified |", "| 2026-08-11 |")
            if line.startswith("| `standard-development-workflow` |")
            else line
            for line in lines
        ]
        registry.write_text("\n".join(lines) + "\n")
        self.assert_validation_failure(
            "registry source manifest version differs for standard-development-workflow"
        )

    def test_unavailable_external_registry_source_cannot_claim_live_verification(self) -> None:
        registry = (
            self.repository
            / "plugins"
            / "amsoft-agentic-workflows"
            / "skills"
            / "amsoft-agentic-workflows"
            / "references"
            / "plugin-registry.md"
        )
        lines = registry.read_text().splitlines()
        lines = [
            line.replace("| not-live-verified |", "| 2026-08-11 |")
            if line.startswith("| `standard-development-workflow` |")
            else line
            for line in lines
        ]
        registry.write_text("\n".join(lines) + "\n")
        self.assert_validation_failure(
            "unavailable registry source for standard-development-workflow must use not-live-verified"
        )

    def test_central_reference_to_standalone_skill_fails(self) -> None:
        router = (
            self.repository
            / "plugins"
            / "amsoft-agentic-workflows"
            / "skills"
            / "amsoft-agentic-workflows"
            / "SKILL.md"
        )
        router.write_text(f"{router.read_text()}\nUse `calorie-tracker`.\n")
        self.assert_validation_failure(
            "references standalone skill calorie-tracker from the central package"
        )

    def test_duplicate_catalog_yaml_key_fails(self) -> None:
        catalog = self.repository / "catalog" / "plugins-v1.yaml"
        catalog.write_text(catalog.read_text().replace("schema_version: 1", "schema_version: 1\nschema_version: 1", 1))
        self.assert_validation_failure("found duplicate key 'schema_version'")

    def test_duplicate_manifest_json_key_fails(self) -> None:
        manifest = (
            self.repository
            / "plugins"
            / "calorie-tracker"
            / ".codex-plugin"
            / "plugin.json"
        )
        manifest.write_text(manifest.read_text().replace('"name":', '"name": "duplicate",\n  "name":', 1))
        self.assert_validation_failure("duplicate JSON key: name")

    def test_wordpress_devops_assets_and_systematic_route_are_mirrored(self) -> None:
        catalog = yaml.safe_load(
            (self.repository / "catalog" / "plugins-v1.yaml").read_text()
        )
        mirrors = {mirror["name"]: mirror for mirror in catalog["mirrors"]}
        self.assertEqual(
            mirrors["wordpress-devops-schemas"]["destination"],
            "plugins/amsoft-agentic-workflows/schemas",
        )
        self.assertEqual(
            mirrors["wordpress-devops-examples"]["destination"],
            "plugins/amsoft-agentic-workflows/examples",
        )
        systematic = mirrors["systematic-literature-review-skill"]
        self.assertIn(
            {
                "from": "`literature-review-workflow`",
                "to": "`amsoft-literature-review-workflow`",
            },
            systematic["replacements"],
        )

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
