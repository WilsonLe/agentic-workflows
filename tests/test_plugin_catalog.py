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

    def test_marketplaces_publish_only_the_complete_bundle(self) -> None:
        catalog = yaml.safe_load(
            (self.repository / "catalog" / "plugins-v2.yaml").read_text()
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
        self.assertEqual([entry["name"] for entry in marketplace["plugins"]], ["agentic-workflows"])
        claude = json.loads((self.repository / ".claude-plugin" / "marketplace.json").read_text())
        self.assertEqual([entry["name"] for entry in claude["plugins"]], ["agentic-workflows"])
        central = next(package for package in catalog["packages"] if package["name"] == "agentic-workflows")
        central_skills = {skill["name"]: skill for skill in central["skills"]}
        self.assertEqual(len(central_skills), 50)
        for package in catalog["packages"]:
            for skill in package["skills"]:
                self.assertEqual(central_skills[skill["name"]], skill)
        for harness, root in (
            ("codex", self.repository / central["path"]),
            ("claude-code", self.repository / "generated" / "claude" / "plugins" / "agentic-workflows"),
        ):
            expected = {skill["name"] for skill in central["skills"] if harness in skill["harnesses"]}
            self.assertEqual({path.name for path in (root / "skills").iterdir() if path.is_dir()}, expected)
            self.assertTrue((root / "skills" / "chrome-extensions" / "scripts" / "audit_extension.py").is_file())
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
            (self.repository / "catalog" / "plugins-v2.yaml").read_text()
        )
        central = next(
            package
            for package in catalog["packages"]
            if package["name"] == "agentic-workflows"
        )
        self.assertEqual(
            [
                skill["name"]
                for skill in central["skills"]
                if "literature-review" in skill["name"]
            ],
            [
                "literature-review-workflow",
                "systematic-literature-review-workflow",
            ],
        )
        router = (
            self.repository
            / "plugins"
            / "agentic-workflows"
            / "skills"
            / "agentic-workflows"
            / "SKILL.md"
        ).read_text()
        self.assertIn("`literature-review-workflow`", router)
        self.assertIn("`systematic-literature-review-workflow`", router)
        self.assertIn("`systematic-literature-review-workflow`", router)

    def test_agent_orchestration_catalog_and_central_route_are_declared(self) -> None:
        catalog = yaml.safe_load(
            (self.repository / "catalog" / "plugins-v2.yaml").read_text()
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
            if package["name"] == "agentic-workflows"
        )
        self.assertIn(
            "orchestration",
            {skill["name"] for skill in central["skills"]},
        )
        self.assertIn(
            "sdlc-loop",
            {skill["name"] for skill in central["skills"]},
        )
        self.assertIn(
            "sdlc-loop-skill",
            {mirror["name"] for mirror in catalog["mirrors"]},
        )
        router = (
            self.repository
            / "plugins"
            / "agentic-workflows"
            / "skills"
            / "agentic-workflows"
            / "SKILL.md"
        ).read_text()
        self.assertIn("`orchestration`", router)
        self.assertIn("`sdlc-loop`", router)
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
            (self.repository / "catalog" / "plugins-v2.yaml").read_text()
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
            if package["name"] == "agentic-workflows"
        )
        central_names = {skill["name"] for skill in central["skills"]}
        for name in (
            "trend-product-design",
            "trend-product-discovery",
            "trend-product-onboarding",
            "trend-product-operations",
            "trend-product-opportunity",
        ):
            self.assertIn(name, central_names)
        self.assertIn(
            "trend-to-product-skills",
            {mirror["name"] for mirror in catalog["mirrors"]},
        )

    def test_qr_code_catalog_and_central_route_are_declared(self) -> None:
        catalog = yaml.safe_load(
            (self.repository / "catalog" / "plugins-v2.yaml").read_text()
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
            if package["name"] == "agentic-workflows"
        )
        self.assertIn(
            "qr-code-generation",
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
            / "agentic-workflows"
            / "skills"
            / "agentic-workflows"
            / "SKILL.md"
        ).read_text()
        self.assertIn("`qr-code-generation`", router)
        self.assertIn("`qr-code-generation`", router)

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
        payload["license"] = "LicenseRef-Agentic Workflows-Proprietary"
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
            / "agentic-workflows"
            / "skills"
            / "humanizer"
            / "LICENSE"
        ).read_text()
        nested_skill = (
            self.repository
            / "plugins"
            / "agentic-workflows"
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
            / "agentic-workflows"
            / "skills"
            / "agentic-workflows"
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
            / "agentic-workflows"
            / "skills"
            / "agentic-workflows"
            / "references"
            / "plugin-registry.md"
        )
        registry.write_text(
            registry.read_text().replace(
                "`plugins/calorie-tracker` | `agentic-workflows`",
                "`plugins/wrong-source` | `agentic-workflows`",
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
            / "agentic-workflows"
            / "skills"
            / "agentic-workflows"
            / "references"
            / "plugin-registry.md"
        )
        lines = registry.read_text().splitlines()
        lines = [
            line.replace("| `agentic-workflows` |", "| `wrong` |")
            if line.startswith("| `calorie-tracker` |")
            else line
            for line in lines
        ]
        registry.write_text("\n".join(lines) + "\n")
        self.assert_validation_failure("registry marketplace for calorie-tracker must be agentic-workflows")

    def test_duplicate_catalog_yaml_key_fails(self) -> None:
        catalog = self.repository / "catalog" / "plugins-v2.yaml"
        catalog.write_text(catalog.read_text().replace("schema_version: 2", "schema_version: 2\nschema_version: 2", 1))
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

    def test_retired_packages_and_skills_are_absent(self) -> None:
        catalog = yaml.safe_load((self.repository / "catalog" / "plugins-v2.yaml").read_text())
        self.assertTrue(all("wordpress" not in package["name"] for package in catalog["packages"]))
        self.assertTrue(all("wordpress" not in skill["name"] for package in catalog["packages"] for skill in package["skills"]))
        self.assertFalse((self.repository / "plugins" / "wordpress-content").exists())

    def test_declared_mirror_drift_fails(self) -> None:
        skill = (
            self.repository
            / "plugins"
            / "agentic-workflows"
            / "skills"
            / "food-image-editing"
            / "SKILL.md"
        )
        skill.write_text(f"{skill.read_text()}\nmirror drift\n")
        self.assert_validation_failure("generated mirror content differs")

    def test_generated_marketplace_drift_fails(self) -> None:
        marketplace = self.repository / ".agents" / "plugins" / "marketplace.json"
        payload = json.loads(marketplace.read_text())
        payload["plugins"].append(dict(payload["plugins"][0], name="literature-review"))
        marketplace.write_text(json.dumps(payload))
        self.assert_validation_failure("marketplace plugin order or inventory differs")

    def test_catalog_cannot_publish_a_second_plugin(self) -> None:
        path = self.repository / "catalog" / "plugins-v2.yaml"
        catalog = yaml.safe_load(path.read_text())
        catalog["marketplace"]["plugin_order"].append("ui-design")
        path.write_text(yaml.safe_dump(catalog, sort_keys=False))
        self.assert_validation_failure("marketplace must publish only agentic-workflows")

    def test_unknown_publication_name_fails(self) -> None:
        path = self.repository / "catalog" / "plugins-v2.yaml"
        catalog = yaml.safe_load(path.read_text())
        catalog["marketplace"]["plugin_order"] = ["unknown-plugin"]
        path.write_text(yaml.safe_dump(catalog, sort_keys=False))
        self.assert_validation_failure("marketplace plugin order contains an unknown catalog package")

    def test_bundle_cannot_drop_a_component_skill(self) -> None:
        path = self.repository / "catalog" / "plugins-v2.yaml"
        catalog = yaml.safe_load(path.read_text())
        central = next(package for package in catalog["packages"] if package["name"] == "agentic-workflows")
        central["skills"] = [skill for skill in central["skills"] if skill["name"] != "ui-design"]
        path.write_text(yaml.safe_dump(catalog, sort_keys=False))
        shutil.rmtree(self.repository / central["path"] / "skills" / "ui-design")
        self.assert_validation_failure("central bundle must preserve ui-design/ui-design")

    def test_bundle_cannot_change_component_harness_support(self) -> None:
        path = self.repository / "catalog" / "plugins-v2.yaml"
        catalog = yaml.safe_load(path.read_text())
        central = next(package for package in catalog["packages"] if package["name"] == "agentic-workflows")
        skill = next(skill for skill in central["skills"] if skill["name"] == "chrome-extensions")
        skill["harnesses"] = ["codex"]
        path.write_text(yaml.safe_dump(catalog, sort_keys=False))
        self.assert_validation_failure("central bundle must preserve chrome-extensions/chrome-extensions")

    def test_generator_bootstraps_missing_bundled_skill(self) -> None:
        root = self.repository / "plugins" / "agentic-workflows" / "skills" / "ui-design"
        shutil.rmtree(root)
        result = subprocess.run(
            [sys.executable, "scripts/generate_plugin_packages.py", "--write"],
            cwd=self.repository, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((root / "SKILL.md").is_file())
        self.assertEqual(self.validate().returncode, 0)

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
