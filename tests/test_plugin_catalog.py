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
        self.assertEqual(len(central_skills), 62)
        self.assertEqual(central_skills["grill-me"]["harnesses"], ["codex", "claude-code", "opencode"])
        budgeting = next(package for package in catalog["packages"] if package["name"] == "budgeting")
        self.assertEqual(budgeting["harnesses"], ["codex"])
        self.assertEqual({skill["name"] for skill in budgeting["skills"]},
                         {"budgeting-account-sync", "budgeting-transactions"})
        for skill in budgeting["skills"]:
            self.assertEqual(skill["harnesses"], ["codex"])
            self.assertTrue(skill["prerequisites"][0]["required"])
        for package in catalog["packages"]:
            for skill in package["skills"]:
                self.assertEqual(central_skills[skill["name"]], skill)
        for harness, root in (
            ("codex", self.repository / central["path"]),
            ("claude-code", self.repository / "generated" / "claude" / "plugins" / "agentic-workflows"),
            ("opencode", self.repository / "generated" / "opencode" / "agentic-workflows"),
        ):
            expected = {skill["name"] for skill in central["skills"] if harness in skill["harnesses"]}
            self.assertEqual({path.name for path in (root / "skills").iterdir() if path.is_dir()}, expected)
            self.assertTrue((root / "skills" / "chrome-extensions" / "scripts" / "audit_extension.py").is_file())
            grill = root / "skills" / "grill-me"
            self.assertIn("name: grill-me", (grill / "SKILL.md").read_text())
            provenance = (grill / "references" / "upstream.md").read_text()
            self.assertIn("49dd158d1076134a641b33efb035946536778336", provenance)
            self.assertIn("Copyright (c) 2026 Matt Pocock", provenance)
            self.assertIn("Permission is hereby granted, free of charge", provenance)
            self.assertIn("THE SOFTWARE IS PROVIDED", provenance)
        literature = next(
            package
            for package in catalog["packages"]
            if package["name"] == "literature-review"
        )
        self.assertEqual(
            [skill["name"] for skill in literature["skills"]],
            ["literature-review-workflow"],
        )

    def test_every_skill_discovers_local_harness_aware_capabilities(self) -> None:
        catalog = yaml.safe_load(
            (self.repository / "catalog/plugins-v2.yaml").read_text()
        )
        central = catalog["packages"][0]
        for package in catalog["packages"]:
            for harness in package["harnesses"]:
                root = (
                    self.repository / package["path"]
                    if harness == "codex"
                    else self.repository / "generated/opencode/agentic-workflows"
                    if harness == "opencode"
                    else self.repository / "generated/claude/plugins" / package["name"]
                )
                mapping = (root / "CAPABILITIES.md").read_text()
                for skill in central["skills"]:
                    name = skill["name"]
                    if harness in skill["harnesses"]:
                        self.assertIn(f"`{name}`", mapping)
                    else:
                        self.assertNotIn(f"`{name}`", mapping)
                for skill in package["skills"]:
                    if harness not in skill["harnesses"]:
                        continue
                    entry = root / "skills" / skill["name"] / "SKILL.md"
                    self.assertIn(
                        "[suite capability map](../../CAPABILITIES.md)",
                        entry.read_text(),
                    )
                    self.assertEqual(
                        (entry.parent / "../../CAPABILITIES.md").resolve(),
                        (root / "CAPABILITIES.md").resolve(),
                    )
                    self.assertIn(f"(skills/{skill['name']}/SKILL.md)", mapping)
        motion = self.repository / central["path"] / "skills/motion-design/SKILL.md"
        music = self.repository / central["path"] / "skills/music-composition/SKILL.md"
        self.assertIn("`music-composition`", motion.read_text())
        self.assertIn("`motion-design`", music.read_text())

    def test_shared_guidance_respects_host_delivery_and_companion_availability(self) -> None:
        catalog = yaml.safe_load((self.repository / "catalog/plugins-v2.yaml").read_text())
        for package in catalog["packages"]:
            for harness in package["harnesses"]:
                root = (self.repository / package["path"] if harness == "codex" else
                        self.repository / "generated/opencode/agentic-workflows" if harness == "opencode" else
                        self.repository / "generated/claude/plugins" / package["name"])
                header = (root / "CAPABILITIES.md").read_text().split("## Capability inventory")[0]
                self.assertIn("In Codex, use Standard\n  Development Workflow when installed", header)
                self.assertIn("other hosts retain their existing delivery", header)
                self.assertIn("skill on a supported host (currently Codex only)", header)
                self.assertIn("or an existing component installation", " ".join(header.split()))
                self.assertNotIn("and review under Standard Development Workflow", header)
        standalone = (self.repository / "plugins/ui-design/CAPABILITIES.md").read_text()
        self.assertIn("`music-composition` (not included here)", standalone)
        self.assertNotIn("(skills/music-composition/SKILL.md)", standalone)
        claude = (self.repository / "generated/claude/plugins/agentic-workflows/skills/agentic-workflows/SKILL.md").read_text()
        self.assertIn("other hosts retain their repository delivery rules", claude)

    def test_missing_capability_pointer_and_map_fail_existing_validation(self) -> None:
        path = (
            self.repository
            / "plugins/agentic-workflows/skills/music-composition/SKILL.md"
        )
        path.write_text(
            path.read_text().replace("[suite capability map]", "[removed map]")
        )
        self.assert_validation_failure("capability handoff differs")
        path = self.repository / "plugins/agentic-workflows/CAPABILITIES.md"
        path.unlink()
        result = subprocess.run(
            [sys.executable, "scripts/generate_plugin_packages.py", "--check"],
            cwd=self.repository, capture_output=True, text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("capability map differs", result.stdout)

    def test_stale_capability_description_and_claude_availability_fail_parity(
        self
    ) -> None:
        path = (
            self.repository
            / "plugins/agentic-workflows/skills/music-composition/SKILL.md"
        )
        source = path.read_text()
        description = next(
            line for line in source.splitlines() if line.startswith("description: ")
        )
        changed = source.replace(description, "description: Changed for parity test", 1)
        self.assertNotEqual(changed, source)
        path.write_text(changed)
        result = subprocess.run(
            [sys.executable, "scripts/generate_plugin_packages.py", "--check"],
            cwd=self.repository,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("capability map differs", result.stdout)
        result = subprocess.run(
            [sys.executable, "scripts/generate_plugin_packages.py", "--write"],
            cwd=self.repository,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        path = (
            self.repository
            / "generated/claude/plugins/agentic-workflows/CAPABILITIES.md"
        )
        path.write_text(path.read_text() + "\n`orchestration`\n")
        result = subprocess.run(
            [sys.executable, "scripts/generate_plugin_packages.py", "--check"],
            cwd=self.repository,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Claude capability map differs", result.stdout)

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
                "Python 3.12 or 3.13, provided by uv run",
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

    def generate(self, mode: str = "--check") -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "scripts/generate_plugin_packages.py", mode],
            cwd=self.repository, capture_output=True, text=True,
        )

    def test_opencode_bundle_inventory_roots_and_exclusions(self) -> None:
        root = self.repository / "generated/opencode/agentic-workflows"
        catalog = yaml.safe_load((self.repository / "catalog/plugins-v2.yaml").read_text())
        central = catalog["packages"][0]
        expected = {s["name"] for s in central["skills"] if "opencode" in s["harnesses"]}
        self.assertEqual(len(expected), 52)
        self.assertEqual({p.parent.name for p in (root / "skills").rglob("SKILL.md")}, expected)
        for name in ("hooks", ".codex-plugin", ".claude-plugin"):
            self.assertFalse((root / name).exists())
        router = (root / "skills/agentic-workflows/SKILL.md").read_text()
        self.assertNotIn("- `sdlc-loop`", router)
        self.assertNotIn("with low reasoning, capped at 10 words", router)
        self.assertIn("@skill-id", router)
        continuity = (root / "skills/agentic-workflows/references/task-continuity.md").read_text()
        self.assertIn("https://github.com/wilsonle/agentic-workflows/blob/main/plugins/agentic-workflows/skills/standard-development-workflow/", continuity)
        self.assertNotIn("](../../standard-development-workflow", continuity)
        for relative in ("LICENSE", "scripts/qr_code_generator.py", "skills/grill-me/references/upstream.md", "skills/literature-review-workflow/examples/narrative-review/papers/SRC-NARRATIVE-001.pdf"):
            canonical = self.repository / central["path"] / relative
            self.assertEqual((root / relative).read_bytes(), canonical.read_bytes())
            self.assertEqual((root / relative).stat().st_mode & 0o777, canonical.stat().st_mode & 0o777)
        project = json.loads((self.repository / "opencode.json").read_text())
        self.assertEqual(project["skills"], ["./" + catalog["harnesses"]["opencode"]["skills_path"]])
        self.assertEqual(self.generate().returncode, 0)

    def test_opencode_support_is_explicit_and_not_inherited_at_runtime(self) -> None:
        path = self.repository / "catalog/plugins-v2.yaml"
        catalog = yaml.safe_load(path.read_text())
        for package in catalog["packages"]:
            for skill in package["skills"]:
                if skill["name"] == "humanizer":
                    skill["harnesses"] = ["codex", "claude-code"]
        path.write_text(yaml.safe_dump(catalog, sort_keys=False))
        result = self.generate("--write")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse((self.repository / "generated/opencode/agentic-workflows/skills/humanizer").exists())
        self.assertTrue((self.repository / "generated/claude/plugins/agentic-workflows/skills/humanizer/SKILL.md").exists())

    def test_opencode_helper_reference_and_router_drift_fail_parity(self) -> None:
        root = self.repository / "generated/opencode/agentic-workflows"
        for relative in ("scripts/qr_code_generator.py", "skills/grill-me/references/upstream.md", "skills/agentic-workflows/SKILL.md", "CAPABILITIES.md"):
            with self.subTest(relative=relative):
                path = root / relative
                original = path.read_bytes()
                path.write_bytes(original + b"\ndrift\n")
                result = self.generate()
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("OpenCode file content differs", result.stdout)
                path.write_bytes(original)

    def test_opencode_missing_unexpected_files_and_modes_fail_validation(self) -> None:
        root = self.repository / "generated/opencode/agentic-workflows"
        helper = root / "scripts/qr_code_generator.py"
        helper.chmod(0o644)
        self.assert_validation_failure("OpenCode file mode differs")
        helper.chmod(0o755)
        helper.unlink()
        self.assert_validation_failure("OpenCode file missing")
        self.assertEqual(self.generate("--write").returncode, 0)
        unexpected = root / "skills/sdlc-loop/SKILL.md"
        unexpected.parent.mkdir()
        unexpected.write_text("---\nname: sdlc-loop\ndescription: unavailable\n---\n")
        self.assert_validation_failure("OpenCode unexpected file")
        self.assertEqual(self.generate("--write").returncode, 0)
        self.assertFalse(unexpected.exists())

    def test_opencode_generated_link_and_packaged_reference_validation(self) -> None:
        result = subprocess.run(
            [sys.executable, "-c", "import sys; sys.path.insert(0, 'scripts'); "
             "from pathlib import Path; from validate_plugin_packages import validate_links, validate_packaged_references; "
             "root = Path('generated/opencode/agentic-workflows').resolve(); "
             "validate_links(root / 'skills'); validate_packaged_references(root)"],
            cwd=self.repository, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_opencode_rejects_unsafe_output_path_before_writing(self) -> None:
        path = self.repository / "catalog/plugins-v2.yaml"
        catalog = yaml.safe_load(path.read_text())
        catalog["harnesses"]["opencode"]["skills_path"] = "plugins/agentic-workflows/skills"
        path.write_text(yaml.safe_dump(catalog, sort_keys=False))
        before = (self.repository / "plugins/agentic-workflows/LICENSE").read_bytes()
        result = self.generate("--write")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("OpenCode skills_path must be", result.stderr)
        self.assertEqual((self.repository / "plugins/agentic-workflows/LICENSE").read_bytes(), before)

    def test_opencode_repository_config_drift_fails_parity(self) -> None:
        config = self.repository / "opencode.json"
        for value in (["./plugins/agentic-workflows/skills"], None, "./generated/opencode/agentic-workflows/skills"):
            with self.subTest(value=value):
                config.write_text(json.dumps({"skills": value}))
                result = self.generate()
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("OpenCode repository skills configuration differs", result.stdout)

    def test_portable_entrypoint_links_use_same_generation_and_parity_contract(self) -> None:
        entry = self.repository / "plugins/agentic-workflows/skills/engineering-exploration/SKILL.md"
        addition = "\n[skills](..)\n[Codex delivery](../standard-development-workflow/SKILL.md#delivery-sequence)\n"
        entry.write_text(entry.read_text() + addition)
        result = self.generate("--write")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for root in ("generated/opencode/agentic-workflows", "generated/claude/plugins/agentic-workflows"):
            generated = (self.repository / root / "skills/engineering-exploration/SKILL.md").read_text()
            self.assertIn("[skills](..)", generated)
            self.assertIn("https://github.com/wilsonle/agentic-workflows/blob/main/plugins/agentic-workflows/skills/standard-development-workflow/SKILL.md#delivery-sequence", generated)
            self.assertNotIn("](../standard-development-workflow", generated)
        self.assertIn(addition, entry.read_text())


    def test_claude_full_tree_and_manifest_parity(self) -> None:
        root = self.repository / "generated/claude/plugins/agentic-workflows"
        for relative, marker in (
            ("skills/agentic-workflows/references/onboarding.md", "Claude file content differs"),
            ("scripts/qr_code_generator.py", "Claude file mode differs"),
            ("scripts/unexpected_helper.py", "Claude unexpected file"),
            (".claude-plugin/plugin.json", "Claude manifest differs"),
        ):
            with self.subTest(relative=relative):
                self.assertEqual(self.generate("--write").returncode, 0)
                path = root / relative
                if marker == "Claude file content differs":
                    path.write_text(path.read_text() + "\ndrift\n")
                elif marker == "Claude file mode differs":
                    path.chmod(0o644)
                elif marker == "Claude unexpected file":
                    path.write_text("print('unexpected')\n")
                else:
                    manifest = json.loads(path.read_text())
                    manifest["version"] = "0.2.0+codex.20261008000200"
                    path.write_text(json.dumps(manifest))
                result = self.generate()
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(marker, result.stdout)

    def test_claude_manifest_version_tracks_generated_content(self) -> None:
        manifest = self.repository / "generated/claude/plugins/agentic-workflows/.claude-plugin/plugin.json"
        before = json.loads(manifest.read_text())["version"]
        self.assertRegex(before, r"^\d+\.\d+\.\d+\+claude\.[0-9a-f]{12}$")
        reference = self.repository / "plugins/agentic-workflows/skills/grill-me/references/upstream.md"
        reference.write_text(reference.read_text() + "\nA maintained note.\n")
        self.assertEqual(self.generate("--write").returncode, 0)
        after = json.loads(manifest.read_text())["version"]
        self.assertNotEqual(before, after)
        self.assertEqual(before.split("+")[0], after.split("+")[0])
        self.assertEqual(self.generate("--write").returncode, 0)
        self.assertEqual(json.loads(manifest.read_text())["version"], after)

    def test_claude_skill_bodies_use_claude_path_variables(self) -> None:
        skill = "skills/music-composition/SKILL.md"
        canonical = (self.repository / "plugins/agentic-workflows" / skill).read_text()
        claude = (self.repository / "generated/claude/plugins/agentic-workflows" / skill).read_text()
        opencode = (self.repository / "generated/opencode/agentic-workflows" / skill).read_text()
        self.assertIn("<skill-root>/scripts/synthesize_score.py", canonical)
        self.assertIn("${CLAUDE_SKILL_DIR}/scripts/synthesize_score.py", claude)
        self.assertNotIn("<skill-root>/", claude)
        self.assertIn("<skill-root>/scripts/synthesize_score.py", opencode)
        qr = self.repository / "generated/claude/plugins/agentic-workflows/skills/qr-code-generation"
        self.assertIn("${CLAUDE_PLUGIN_ROOT}/scripts/qr_code_generator.py", (qr / "SKILL.md").read_text())
        self.assertIn(
            "<plugin-root>/scripts/qr_code_generator.py",
            (qr / "references/dependencies-and-licensing.md").read_text(),
        )
        for root in ("generated/claude/plugins/agentic-workflows", "generated/opencode/agentic-workflows"):
            self.assertEqual(list((self.repository / root).rglob("openai.yaml")), [])

    def test_claude_substitution_tokens_and_skill_metadata_limits_fail_validation(self) -> None:
        skill = self.repository / "plugins/agentic-workflows/skills/humanizer/SKILL.md"
        original = skill.read_text()
        for content, marker in (
            (original + "\nRun awk '{print $1}' on the file.\n", "which Claude Code substitutes"),
            (original + "\nPass $ARGUMENTS to the helper.\n", "which Claude Code substitutes"),
            (original.replace("description: ", "description: " + "x" * 1025, 1), "description must be 1-1024"),
            (original + "\nRun <skill-dir>/scripts/tool.py.\n", "undefined placeholder <skill-dir>"),
        ):
            with self.subTest(marker=marker):
                skill.write_text(content)
                self.assert_validation_failure(marker)
        skill.write_text(original)


    def test_claude_version_ignores_checkout_umask_and_flags_stray_output(self) -> None:
        for path in self.repository.rglob("*"):
            if path.is_file():
                path.chmod(path.stat().st_mode | 0o020)
        result = self.generate()
        self.assertEqual(result.returncode, 0, result.stdout)
        root = self.repository / "generated/claude/plugins"
        (root / "agentic-workflows/CAPABILITIES.md").chmod(0o755)
        (root / "reddit").mkdir()
        (root / "reddit/README.md").write_text("stale\n")
        result = self.generate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Claude file mode differs: generated/claude/plugins/agentic-workflows/CAPABILITIES.md", result.stdout)
        self.assertIn("Claude unexpected file: generated/claude/plugins/reddit", result.stdout)

    def test_claude_entrypoints_explain_placeholders_and_helper_commands(self) -> None:
        claude = self.repository / "generated/claude/plugins/agentic-workflows/skills"
        music = (claude / "music-composition/SKILL.md").read_text()
        self.assertIn("Run each shell command on its own", music)
        self.assertNotIn("This skill's references write", music)
        railway = (claude / "railway-account-operations/SKILL.md").read_text()
        self.assertIn("This skill's references write `<plugin-root>` for `${CLAUDE_PLUGIN_ROOT}`.", railway)
        self.assertIn("`<project-root>` is the top-level directory of the checkout", railway)
        self.assertNotIn("CLAUDE_PROJECT_DIR", railway)
        self.assertIn("Claude in Chrome is available only when its browser tools", railway)
        cloudflare = (claude / "cloudflare-account-operations/SKILL.md").read_text()
        self.assertIn("Run each shell command on its own", cloudflare)
        chrome = (claude / "chrome-extensions/SKILL.md").read_text()
        self.assertNotIn("This skill's references write", chrome)
        humanizer = (claude / "humanizer/SKILL.md").read_text()
        self.assertNotIn("claude-code-notes", humanizer)
        opencode = self.repository / "generated/opencode/agentic-workflows/skills"
        self.assertNotIn("claude-code-notes", (opencode / "railway-account-operations/SKILL.md").read_text())

    def test_skill_frontmatter_limits_use_parsed_yaml(self) -> None:
        skill = self.repository / "plugins/agentic-workflows/skills/humanizer/SKILL.md"
        original = skill.read_text()
        head, separator, rest = original.partition("\ndescription: ")
        description, newline, body = rest.partition("\n")
        skill.write_text(f"{head}\ndescription: >-\n  {description}\n{body}")
        self.assertEqual(self.generate("--write").returncode, 0)
        result = self.validate()
        self.assertEqual(result.returncode, 0, result.stderr)
        long_text = " ".join(["Use this skill whenever prose needs review"] * 30)
        skill.write_text(f"{head}\ndescription: {long_text[:600]}\n  {long_text[600:]}\n{body}")
        self.assert_validation_failure("description must be 1-1024")

    def test_claude_load_time_markers_and_unsubstituted_variables_fail_validation(self) -> None:
        skill = self.repository / "plugins/agentic-workflows/skills/humanizer/SKILL.md"
        original = skill.read_text()
        skill.write_text(original + "\nList drafts with !`ls -1 drafts`.\n")
        self.assert_validation_failure("which Claude Code substitutes or executes")
        skill.write_text(original)
        reference = self.repository / "plugins/qr-code-generator/skills/qr-code-generation/references/verification-and-recovery.md"
        reference.write_text(reference.read_text() + "\nRun `uv run ${CLAUDE_PLUGIN_ROOT}/scripts/qr_code_generator.py`.\n")
        self.assert_validation_failure("which is not substituted there")
        reference.write_text(reference.read_text().replace("${CLAUDE_PLUGIN_ROOT}", "<SKILL_DIR>"))
        self.assert_validation_failure("undefined placeholder <SKILL_DIR>")


if __name__ == "__main__":
    unittest.main()
