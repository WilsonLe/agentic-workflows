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
        self.output = Path(self.temporary.name) / "distribution"
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

    def validate(self, *arguments: str | Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "scripts/validate_plugin_packages.py", *arguments],
            cwd=self.repository,
            check=False,
            capture_output=True,
            text=True,
        )

    def assert_validation_failure(self, marker: str, *arguments: str | Path) -> None:
        result = self.validate(*arguments)
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
        self.assertEqual(claude["plugins"][0]["source"], {
            "source": "git-subdir",
            "url": "https://github.com/WilsonLe/agentic-workflows.git",
            "ref": "dist",
            "path": "generated/claude/plugins/agentic-workflows",
        })
        central = next(package for package in catalog["packages"] if package["name"] == "agentic-workflows")
        central_skills = {skill["name"]: skill for skill in central["skills"]}
        self.assertEqual(len(central_skills), 69)
        self.assertEqual(central_skills["product-growth"]["harnesses"], ["codex", "claude-code", "opencode"])
        self.assertEqual(central_skills["grill-me"]["harnesses"], ["codex", "claude-code", "opencode"])
        self.assertEqual(central_skills["interactive-plan"]["harnesses"], ["codex", "claude-code", "opencode"])
        self.assertEqual(central_skills["ponytail"]["harnesses"], ["codex", "claude-code", "opencode"])
        self.assertEqual(central_skills["delegation"]["harnesses"], ["codex", "claude-code", "opencode"])
        self.assertEqual([path.name for path in (self.repository / "plugins").iterdir()], ["agentic-workflows"])
        for name in ("budgeting-account-sync", "budgeting-transactions"):
            skill = central_skills[name]
            self.assertEqual(skill["harnesses"], ["codex"])
            self.assertTrue(skill["prerequisites"][0]["required"])
        for harness, root in (
            ("codex", self.repository / central["path"]),
            ("claude-code", self.distribution / "generated" / "claude" / "plugins" / "agentic-workflows"),
            ("opencode", self.distribution / "generated" / "opencode" / "agentic-workflows"),
        ):
            expected = {skill["name"] for skill in central["skills"] if harness in skill["harnesses"]}
            self.assertEqual({path.name for path in (root / "skills").iterdir() if path.is_dir()}, expected)
            self.assertTrue((root / "skills" / "chrome-extensions" / "scripts" / "audit_extension.py").is_file())
            # A discovered growth skill must ship its usable records and research
            # contracts in each supported harness, not just its entrypoint.
            growth = root / "skills" / "product-growth"
            for asset in (
                "references/search-research.md",
                "references/content-production.md",
                "references/ugc-production.md",
                "references/measurement.md",
                "references/source-basis.md",
                "templates/growth-cycle.md",
            ):
                self.assertEqual(
                    (growth / asset).read_bytes(),
                    (self.repository / central["path"] / "skills" / "product-growth" / asset).read_bytes(),
                )
            grill = root / "skills" / "grill-me"
            self.assertIn("name: grill-me", (grill / "SKILL.md").read_text())
            provenance = (grill / "references" / "upstream.md").read_text()
            self.assertIn("49dd158d1076134a641b33efb035946536778336", provenance)
            self.assertIn("Copyright (c) 2026 Matt Pocock", provenance)
            self.assertIn("Permission is hereby granted, free of charge", provenance)
            self.assertIn("THE SOFTWARE IS PROVIDED", provenance)
            ponytail = root / "skills" / "ponytail"
            self.assertIn("name: ponytail", (ponytail / "SKILL.md").read_text())
            ponytail_provenance = (ponytail / "references" / "upstream.md").read_text()
            self.assertIn("09c434ab73ca43761c5d8b0c5d341926c2fba710", ponytail_provenance)
            self.assertIn("Copyright (c) 2026 DietrichGebert", ponytail_provenance)
            self.assertIn("Permission is hereby granted, free of charge", ponytail_provenance)
            self.assertIn("THE SOFTWARE IS PROVIDED", ponytail_provenance)
            self.assertIn("ponytail", (root / "CAPABILITIES.md").read_text())
            router = (root / "skills" / "agentic-workflows" / "SKILL.md").read_text()
            self.assertIn("`ponytail`", router)
            for caller in (
                "engineering-intake/SKILL.md",
                "engineering-diagnosis/SKILL.md",
                "engineering-exploration/SKILL.md",
                "engineering-review/references/review-checklist.md",
            ):
                self.assertIn("ponytail/SKILL.md", (root / "skills" / caller).read_text())
            if harness == "codex":
                self.assertIn("Use $ponytail", (ponytail / "agents" / "openai.yaml").read_text())

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
                    else self.distribution / "generated/opencode/agentic-workflows"
                    if harness == "opencode"
                    else self.distribution / "generated/claude/plugins" / package["name"]
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
                        self.distribution / "generated/opencode/agentic-workflows" if harness == "opencode" else
                        self.distribution / "generated/claude/plugins" / package["name"])
                header = (root / "CAPABILITIES.md").read_text().split("## Capability inventory")[0]
                self.assertIn("Use Standard Development\n  Workflow when installed on Codex, Claude Code, or OpenCode", header)
                self.assertIn("skill on a supported host (currently Codex only)", header)
                self.assertNotIn("and review under Standard Development Workflow", header)
        claude = (self.distribution / "generated/claude/plugins/agentic-workflows/skills/agentic-workflows/SKILL.md").read_text()
        self.assertIn("The portable packages include ordinary\nStandard Development Workflow", claude)

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
            self.distribution / "generated/claude/plugins/agentic-workflows/CAPABILITIES.md"
        )
        path.write_text(path.read_text() + "\n`orchestration`\n")
        result = self.generate("--check-build", self.distribution)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("distribution content differs", result.stdout)

    def test_literature_review_catalog_and_routes_are_declared(self) -> None:
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

    def test_codex_only_orchestration_assets_stay_in_the_suite(self) -> None:
        catalog = yaml.safe_load((self.repository / "catalog/plugins-v2.yaml").read_text())
        package, = catalog["packages"]
        skills = {item["name"]: item for item in package["skills"]}
        for name in ("orchestration", "sdlc-loop"):
            self.assertEqual(skills[name]["harnesses"], ["codex"])
        source = self.repository / package["path"]
        router = (source / "skills/agentic-workflows/SKILL.md").read_text()
        for name in ("orchestration", "sdlc-loop"):
            self.assertIn(f"`{name}`", router)
        codex_files = (
            *[f"schemas/orchestration-state-v{v}.schema.json" for v in range(1, 8)],
            "schemas/worktree-claim-v1.schema.json",
            "scripts/orchestration_state.py",
            "scripts/calorie_tracker.py",
            "examples/register.json",
            "examples/worktree-claim.json",
        )
        for path in codex_files:
            self.assertTrue((source / path).is_file())
            for portable in ("generated/claude/plugins/agentic-workflows", "generated/opencode/agentic-workflows"):
                self.assertFalse((self.distribution / portable / path).exists())

    def test_trend_product_skills_are_cataloged(self) -> None:
        catalog = yaml.safe_load((self.repository / "catalog/plugins-v2.yaml").read_text())
        package, = catalog["packages"]
        names = {item["name"] for item in package["skills"]}
        self.assertEqual({name for name in names if name.startswith("trend-product-")}, {
            "trend-product-design", "trend-product-discovery", "trend-product-onboarding",
            "trend-product-operations", "trend-product-opportunity",
        })

    def test_qr_code_catalog_and_route_are_declared(self) -> None:
        catalog = yaml.safe_load((self.repository / "catalog/plugins-v2.yaml").read_text())
        package, = catalog["packages"]
        skill = next(item for item in package["skills"] if item["name"] == "qr-code-generation")
        self.assertEqual(skill["harnesses"], ["codex", "claude-code", "opencode"])
        self.assertIn("scripts/qr_code_generator.py", package["executables"])
        router = (self.repository / package["path"] / "skills/agentic-workflows/SKILL.md").read_text()
        self.assertIn("`qr-code-generation`", router)

    def test_suite_manifest_drift_fails(self) -> None:
        manifest = (
            self.repository
            / "plugins"
            / "agentic-workflows"
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
            / "agentic-workflows"
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
            self.repository / "plugins" / "agentic-workflows" / "LICENSE"
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

        seo = self.repository / "plugins/agentic-workflows/skills/seo-audit"
        notice = (seo / "licenses/claude-seo-MIT.txt").read_bytes()
        self.assertIn(b"Copyright (c) 2026 agricidaniel", notice)
        for harness in ("claude/plugins", "opencode"):
            packaged = self.distribution / "generated" / harness / "agentic-workflows/skills/seo-audit"
            for directory in ("references", "templates", "licenses"):
                for source in (seo / directory).rglob("*"):
                    if source.is_file():
                        self.assertEqual(
                            (packaged / source.relative_to(seo)).read_bytes(),
                            source.read_bytes(),
                        )

    def test_suite_registry_version_drift_fails(self) -> None:
        manifest = (
            self.repository
            / "plugins"
            / "agentic-workflows"
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
                if row.startswith("| `agentic-workflows` |")
                else row
            )
            for row in rows
        ]
        registry.write_text("\n".join(rows) + "\n")
        self.assert_validation_failure(
            "registry does not contain the current agentic-workflows version"
        )

    def test_required_agent_metadata_fails_when_missing(self) -> None:
        metadata = (
            self.repository
            / "plugins"
            / "agentic-workflows"
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
            / "agentic-workflows"
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
            / "agentic-workflows"
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
            / "agentic-workflows"
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
            / "agentic-workflows"
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
            / "agentic-workflows"
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
            / "agentic-workflows"
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
                "`plugins/agentic-workflows` | `agentic-workflows`",
                "`plugins/wrong-source` | `agentic-workflows`",
                1,
            )
        )
        self.assert_validation_failure(
            "registry source for agentic-workflows must be catalog path"
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
            line.replace("`plugins/agentic-workflows` | `agentic-workflows`", "`plugins/agentic-workflows` | `wrong`")
            if line.startswith("| `agentic-workflows` |")
            else line
            for line in lines
        ]
        registry.write_text("\n".join(lines) + "\n")
        self.assert_validation_failure("registry marketplace for agentic-workflows must be agentic-workflows")

    def test_duplicate_catalog_yaml_key_fails(self) -> None:
        catalog = self.repository / "catalog" / "plugins-v2.yaml"
        catalog.write_text(catalog.read_text().replace("schema_version: 2", "schema_version: 2\nschema_version: 2", 1))
        self.assert_validation_failure("found duplicate key 'schema_version'")

    def test_duplicate_manifest_json_key_fails(self) -> None:
        manifest = (
            self.repository
            / "plugins"
            / "agentic-workflows"
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

    def test_generated_marketplace_drift_fails(self) -> None:
        marketplace = self.repository / ".agents" / "plugins" / "marketplace.json"
        payload = json.loads(marketplace.read_text())
        payload["plugins"].append(dict(payload["plugins"][0], name="literature-review"))
        marketplace.write_text(json.dumps(payload))
        self.assert_validation_failure("marketplace plugin order or inventory differs")

    def test_catalog_cannot_publish_a_second_plugin(self) -> None:
        path = self.repository / "catalog" / "plugins-v2.yaml"
        catalog = yaml.safe_load(path.read_text())
        catalog["packages"].append(dict(catalog["packages"][0], name="second-plugin"))
        path.write_text(yaml.safe_dump(catalog, sort_keys=False))
        self.assert_validation_failure("plugin catalog schema violation")

    def test_unknown_publication_name_fails(self) -> None:
        path = self.repository / "catalog" / "plugins-v2.yaml"
        catalog = yaml.safe_load(path.read_text())
        catalog["marketplace"]["plugin_order"] = ["unknown-plugin"]
        path.write_text(yaml.safe_dump(catalog, sort_keys=False))
        self.assert_validation_failure("marketplace plugin order contains an unknown catalog package")

    def test_missing_canonical_skill_fails_check_and_cannot_be_regenerated(self) -> None:
        root = self.repository / "plugins/agentic-workflows/skills/ui-design"
        shutil.rmtree(root)
        self.assert_validation_failure("skill inventory differs from catalog")
        result = self.generate("--write")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(root.exists())

    def test_runtime_cache_files_do_not_enter_distributions(self) -> None:
        cache = (
            self.repository
            / "plugins"
            / "agentic-workflows"
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
        self.assertFalse(any(self.distribution.rglob("*.pyc")))

    @property
    def distribution(self) -> Path:
        if not self.output.exists():
            result = self.generate("--build", self.output)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return self.output

    def generate(self, *arguments: str | Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "scripts/generate_plugin_packages.py", *arguments],
            cwd=self.repository, capture_output=True, text=True,
        )

    def test_opencode_bundle_inventory_roots_and_exclusions(self) -> None:
        root = self.distribution / "generated/opencode/agentic-workflows"
        catalog = yaml.safe_load((self.repository / "catalog/plugins-v2.yaml").read_text())
        central = catalog["packages"][0]
        expected = {s["name"] for s in central["skills"] if "opencode" in s["harnesses"]}
        self.assertEqual(len(expected), 60)
        self.assertEqual({p.parent.name for p in (root / "skills").rglob("SKILL.md")}, expected)
        for name in ("hooks", ".codex-plugin", ".claude-plugin"):
            self.assertFalse((root / name).exists())
        router = (root / "skills/agentic-workflows/SKILL.md").read_text()
        self.assertNotIn("- `sdlc-loop`", router)
        self.assertNotIn("with low reasoning, capped at 10 words", router)
        self.assertIn("@skill-id", router)
        continuity = (root / "skills/agentic-workflows/references/task-continuity.md").read_text()
        self.assertIn("](../../standard-development-workflow/references/stage-contracts.md", continuity)
        self.assertIn("standard-development-workflow", expected)
        for relative in ("LICENSE", "scripts/qr_code_generator.py", "skills/grill-me/references/upstream.md", "skills/literature-review-workflow/examples/narrative-review/papers/SRC-NARRATIVE-001.pdf"):
            canonical = self.repository / central["path"] / relative
            self.assertEqual((root / relative).read_bytes(), canonical.read_bytes())
            self.assertEqual((root / relative).stat().st_mode & 0o777, canonical.stat().st_mode & 0o777)
        project = json.loads((self.distribution / "opencode.json").read_text())
        self.assertEqual(project["skills"], ["./" + catalog["harnesses"]["opencode"]["skills_path"]])
        self.assertEqual(self.generate("--check-build", self.distribution).returncode, 0)

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
        self.assertFalse((self.distribution / "generated/opencode/agentic-workflows/skills/humanizer").exists())
        self.assertTrue((self.distribution / "generated/claude/plugins/agentic-workflows/skills/humanizer/SKILL.md").exists())

    def test_opencode_helper_reference_and_router_drift_fail_parity(self) -> None:
        root = self.distribution / "generated/opencode/agentic-workflows"
        for relative in ("scripts/qr_code_generator.py", "skills/grill-me/references/upstream.md", "skills/agentic-workflows/SKILL.md", "CAPABILITIES.md"):
            with self.subTest(relative=relative):
                path = root / relative
                original = path.read_bytes()
                path.write_bytes(original + b"\ndrift\n")
                result = self.generate("--check-build", self.distribution)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("distribution content differs", result.stdout)
                path.write_bytes(original)

    def test_opencode_missing_unexpected_files_and_modes_fail_validation(self) -> None:
        root = self.distribution / "generated/opencode/agentic-workflows"
        helper = root / "scripts/qr_code_generator.py"
        helper.chmod(0o644)
        self.assert_validation_failure("distribution executable mode differs", "--build-root", self.distribution)
        helper.chmod(0o755)
        contents = helper.read_bytes()
        helper.unlink()
        self.assert_validation_failure("distribution file missing", "--build-root", self.distribution)
        helper.write_bytes(contents)
        helper.chmod(0o755)
        unexpected = root / "skills/sdlc-loop/SKILL.md"
        unexpected.parent.mkdir()
        unexpected.write_text("---\nname: sdlc-loop\ndescription: unavailable\n---\n")
        self.assert_validation_failure("distribution unexpected entry", "--build-root", self.distribution)

    def test_opencode_generated_link_and_packaged_reference_validation(self) -> None:
        result = self.validate("--build-root", self.distribution)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_opencode_rejects_unsafe_output_path_before_writing(self) -> None:
        path = self.repository / "catalog/plugins-v2.yaml"
        catalog = yaml.safe_load(path.read_text())
        catalog["harnesses"]["opencode"]["skills_path"] = "plugins/agentic-workflows/skills"
        path.write_text(yaml.safe_dump(catalog, sort_keys=False))
        before = (self.repository / "plugins/agentic-workflows/LICENSE").read_bytes()
        result = self.generate("--build", self.output)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("OpenCode skills_path must be", result.stderr)
        self.assertEqual((self.repository / "plugins/agentic-workflows/LICENSE").read_bytes(), before)

    def test_opencode_repository_config_drift_fails_parity(self) -> None:
        config = self.distribution / "opencode.json"
        for value in (["./plugins/agentic-workflows/skills"], None, "./generated/opencode/agentic-workflows/skills"):
            with self.subTest(value=value):
                config.write_text(json.dumps({"skills": value}))
                result = self.generate("--check-build", self.distribution)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("distribution content differs: opencode.json", result.stdout)

    def test_portable_entrypoint_links_use_same_generation_and_parity_contract(self) -> None:
        entry = self.repository / "plugins/agentic-workflows/skills/engineering-exploration/SKILL.md"
        addition = (
            "\n[skills](..)\n[Ordinary delivery](../standard-development-workflow/SKILL.md#delivery-sequence)\n"
            "[Codex autopilot](../sdlc-loop/SKILL.md#delivery-procedure)\n"
        )
        entry.write_text(entry.read_text() + addition)
        result = self.generate("--write")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for root in ("generated/opencode/agentic-workflows", "generated/claude/plugins/agentic-workflows"):
            generated = (self.distribution / root / "skills/engineering-exploration/SKILL.md").read_text()
            self.assertIn("[skills](..)", generated)
            self.assertIn("](../standard-development-workflow/SKILL.md#delivery-sequence)", generated)
            self.assertIn("https://github.com/wilsonle/agentic-workflows/blob/main/plugins/agentic-workflows/skills/sdlc-loop/SKILL.md#delivery-procedure", generated)
            self.assertNotIn("](../sdlc-loop", generated)
            package = self.distribution / root
            for relative in (
                "SKILL.md", "references/stage-contracts.md",
                "references/verification-deployment-cleanup.md",
                "scripts/standard_workflow_record.py", "scripts/project_adrs.py",
                "schemas/standard-workflow-v1.schema.json",
            ):
                self.assertTrue((package / "skills/standard-development-workflow" / relative).is_file())
        self.assertIn(addition, entry.read_text())

    def test_cleanup_discovery_reaches_same_contract_in_each_harness(self) -> None:
        source = self.repository / "plugins/agentic-workflows"
        for root in (source,
                     self.distribution / "generated/opencode/agentic-workflows",
                     self.distribution / "generated/claude/plugins/agentic-workflows"):
            with self.subTest(root=root):
                skill = root / "skills/standard-development-workflow"
                entry = (skill / "SKILL.md").read_text()
                description = yaml.safe_load(entry.split("---", 2)[1])["description"]
                self.assertIn("stop all simulators", description)
                self.assertIn("cleanup coordination", (root / "skills/agentic-workflows/SKILL.md").read_text())
                self.assertIn("references/verification-deployment-cleanup.md#direct-cleanup-and-active-consumers", entry)
                self.assertIn("no implementation plan, tracking issue, empty PR", entry)
                for relative in (
                    "references/verification-deployment-cleanup.md",
                    "references/workflow-record-model.md",
                    "scripts/standard_workflow_record.py",
                    "schemas/standard-workflow-v1.schema.json",
                ):
                    self.assertEqual((skill / relative).read_bytes(),
                                     (source / "skills/standard-development-workflow" / relative).read_bytes())


    def test_claude_full_tree_and_manifest_parity(self) -> None:
        root = self.distribution / "generated/claude/plugins/agentic-workflows"
        manifest = root / ".claude-plugin/plugin.json"
        payload = json.loads(manifest.read_text())
        payload["version"] = "0.2.0+codex.20261008000200"
        manifest.write_text(json.dumps(payload))
        result = self.generate("--check-build", self.distribution)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(f"distribution content differs: {manifest.relative_to(self.distribution)}", result.stdout)

    def test_claude_manifest_version_tracks_generated_content(self) -> None:
        relative = "generated/claude/plugins/agentic-workflows/.claude-plugin/plugin.json"
        before = json.loads((self.distribution / relative).read_text())["version"]
        self.assertRegex(before, r"^\d+\.\d+\.\d+\+claude\.[0-9a-f]{12}$")
        reference = self.repository / "plugins/agentic-workflows/skills/grill-me/references/upstream.md"
        reference.write_text(reference.read_text() + "\nA maintained note.\n")
        rebuilt = self.output.with_name("rebuilt")
        result = self.generate("--build", rebuilt)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        after = json.loads((rebuilt / relative).read_text())["version"]
        self.assertNotEqual(before, after)
        self.assertEqual(before.split("+")[0], after.split("+")[0])
        self.assertEqual(self.generate("--check-build", rebuilt).returncode, 0)

    def test_claude_skill_bodies_use_claude_path_variables(self) -> None:
        skill = "skills/music-composition/SKILL.md"
        canonical = (self.repository / "plugins/agentic-workflows" / skill).read_text()
        claude = (self.distribution / "generated/claude/plugins/agentic-workflows" / skill).read_text()
        opencode = (self.distribution / "generated/opencode/agentic-workflows" / skill).read_text()
        self.assertIn("<skill-root>/scripts/synthesize_score.py", canonical)
        self.assertIn("${CLAUDE_SKILL_DIR}/scripts/synthesize_score.py", claude)
        self.assertNotIn("<skill-root>/", claude)
        self.assertIn("<skill-root>/scripts/synthesize_score.py", opencode)
        qr = self.distribution / "generated/claude/plugins/agentic-workflows/skills/qr-code-generation"
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
        output = self.distribution
        for path in self.repository.rglob("*"):
            if path.is_file():
                path.chmod(path.stat().st_mode | 0o020)
        result = self.generate("--check-build", output)
        self.assertEqual(result.returncode, 0, result.stdout)
        root = output / "generated/claude/plugins"
        (root / "agentic-workflows/CAPABILITIES.md").chmod(0o755)
        (root / "reddit").mkdir()
        (root / "reddit/README.md").write_text("stale\n")
        result = self.generate("--check-build", output)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("distribution executable mode differs: generated/claude/plugins/agentic-workflows/CAPABILITIES.md", result.stdout)
        self.assertIn("distribution unexpected entry: generated/claude/plugins/reddit", result.stdout)

    def test_claude_entrypoints_explain_placeholders_and_helper_commands(self) -> None:
        claude = self.distribution / "generated/claude/plugins/agentic-workflows/skills"
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
        opencode = self.distribution / "generated/opencode/agentic-workflows/skills"
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
        reference = self.repository / "plugins/agentic-workflows/skills/qr-code-generation/references/verification-and-recovery.md"
        reference.write_text(reference.read_text() + "\nRun `uv run ${CLAUDE_PLUGIN_ROOT}/scripts/qr_code_generator.py`.\n")
        self.assert_validation_failure("which is not substituted there")
        reference.write_text(reference.read_text().replace("${CLAUDE_PLUGIN_ROOT}", "<SKILL_DIR>"))
        self.assert_validation_failure("undefined placeholder <SKILL_DIR>")


if __name__ == "__main__":
    unittest.main()
