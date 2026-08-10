from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "plugins" / "wordpress-git-sync"
CLI = PACKAGE / "scripts" / "wp_content_sync.py"

SPEC = importlib.util.spec_from_file_location("wp_content_sync", CLI)
assert SPEC and SPEC.loader
SYNC = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SYNC)


class WordPressGitSyncContractTests(unittest.TestCase):
    def example(self, name: str) -> dict:
        return json.loads((PACKAGE / "examples" / name).read_text())

    def test_examples_validate_against_schemas_and_runtime_contract(self) -> None:
        pairs = {
            "managed-page-v1.json": "managed-object-v1.schema.json",
            "managed-template-v1.json": "managed-object-v1.schema.json",
            "managed-pattern-v1.json": "managed-object-v1.schema.json",
            "managed-media-v1.json": "managed-object-v1.schema.json",
            "managed-acf-field-group-v1.json": "managed-object-v1.schema.json",
            "sync-project-v1.json": "sync-project-v1.schema.json",
            "content-lock-v2.json": "content-lock-v2.schema.json",
            "media-manifest-v1.json": "media-manifest-v1.schema.json",
            "automation-event-v1.json": "automation-event-v1.schema.json",
        }
        for example_name, schema_name in pairs.items():
            with self.subTest(example=example_name):
                schema = json.loads((PACKAGE / "schemas" / schema_name).read_text())
                jsonschema.Draft202012Validator(schema).validate(self.example(example_name))
        for name in (
            "managed-page-v1.json",
            "managed-template-v1.json",
            "managed-pattern-v1.json",
            "managed-media-v1.json",
            "managed-acf-field-group-v1.json",
        ):
            SYNC.validate_managed_object(self.example(name), git_safe=True)

    @unittest.skipUnless(shutil.which("php"), "PHP runtime is covered by the disposable compatibility matrix")
    def test_canonical_digest_matches_php_runtime(self) -> None:
        obj = self.example("managed-page-v1.json")
        expected = SYNC.managed_digest(obj)
        php = """
        <?php
        function wp_json_encode($value, $flags = 0) { return json_encode($value, $flags); }
        require $argv[1];
        $object = json_decode(file_get_contents($argv[2]), true, 512, JSON_THROW_ON_ERROR);
        $canonicalizer = new AMSoft\\WordPressGitSync\\Canonicalizer();
        echo $canonicalizer->managed_digest($object);
        """
        with tempfile.TemporaryDirectory() as temporary:
            runner = Path(temporary) / "digest.php"
            runner.write_text(php)
            result = subprocess.run(
                [
                    "php",
                    str(runner),
                    str(PACKAGE / "runtime" / "amsoft-wordpress-git-sync" / "includes" / "class-amsoft-sync-canonicalizer.php"),
                    str(PACKAGE / "examples" / "managed-page-v1.json"),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
        self.assertEqual(result.stdout.strip(), expected)

    def test_secret_fields_private_content_and_raw_serialized_acf_fail_closed(self) -> None:
        obj = self.example("managed-page-v1.json")
        obj["provenance"]["token"] = "must-not-enter-git"
        with self.assertRaisesRegex(SYNC.SyncError, "secret-shaped"):
            SYNC.validate_managed_object(obj)

        private = self.example("managed-page-v1.json")
        private["classification"] = "restricted"
        private["data"]["status"] = "private"
        with self.assertRaisesRegex(SYNC.SyncError, "non-public"):
            SYNC.validate_managed_object(private, git_safe=True)

        with self.assertRaisesRegex(SYNC.SyncError, "PHP-serialized"):
            SYNC.validate_acf_values({
                "target_ref": "page:page:about",
                "field_group_refs": ["acf_field_group:group:page-details"],
                "values": {"field_bad": 'a:1:{s:3:"bad";s:3:"yes";}'},
            })

    def test_fixture_transport_is_atomic_idempotent_and_conflict_aware(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            state_path = root / "fixture.json"
            shutil.copyfile(PACKAGE / "examples" / "fixture-remote-v1.json", state_path)
            project = self.example("sync-project-v1.json")
            project["repository_root"] = str(root)
            transport = SYNC.FixtureTransport(state_path, project)
            before = transport.get("page:page:about")
            desired = json.loads(json.dumps(before["object"]))
            desired["data"]["title"]["raw"] = "About us"

            dry_run = transport.apply(
                desired,
                expected_sha256=before["sha256"],
                expected_revision=before["revision"],
                idempotency_key="fixture-dry-run-01",
                dry_run=True,
            )
            self.assertTrue(dry_run["dry_run"])
            self.assertEqual(transport.get("page:page:about")["sha256"], before["sha256"])

            applied = transport.apply(
                desired,
                expected_sha256=before["sha256"],
                expected_revision=before["revision"],
                idempotency_key="fixture-apply-01",
                dry_run=False,
            )
            replay = transport.apply(
                desired,
                expected_sha256=before["sha256"],
                expected_revision=before["revision"],
                idempotency_key="fixture-apply-01",
                dry_run=False,
            )
            self.assertFalse(applied["idempotent_replay"])
            self.assertTrue(replay["idempotent_replay"])
            self.assertEqual(replay["after_sha256"], SYNC.managed_digest(desired))
            with self.assertRaisesRegex(SYNC.SyncError, "changed since"):
                transport.apply(
                    before["object"],
                    expected_sha256=before["sha256"],
                    expected_revision=before["revision"],
                    idempotency_key="fixture-stale-01",
                    dry_run=False,
                )

    def test_cli_pull_plan_dry_run_execute_and_readback(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            state = root / "fixture.json"
            shutil.copyfile(PACKAGE / "examples" / "fixture-remote-v1.json", state)
            project = self.example("sync-project-v1.json")
            project["repository_root"] = str(root)
            project["transport"]["state_path"] = state.name
            project_path = root / "project.json"
            project_path.write_text(json.dumps(project))
            source = root / "page.json"
            lock = root / "lock.json"

            pull = self.run_cli(
                "pull", "--project", project_path, "--object", "page:page:about",
                "--output", source, "--lock-output", lock, "--verify-remote",
            )
            self.assertEqual(pull["operation"], "pull")
            local = json.loads(source.read_text())
            local["data"]["excerpt"]["raw"] = "Updated through guarded sync."
            source.write_text(json.dumps(local))
            locked = json.loads(lock.read_text())

            plan = self.run_cli(
                "plan", "--project", project_path, "--source", source, "--lock", lock,
            )
            self.assertEqual(plan["action"], "apply")
            common = (
                "apply", "--project", project_path, "--source", source, "--lock", lock,
                "--expected-remote-sha256", locked["remote"]["sha256"],
                "--expected-remote-revision", locked["remote"]["revision"],
                "--require-atomic-check", "--idempotency-key", "cli-apply-0001",
                "--approval-id", "issue-71",
            )
            dry_run = self.run_cli(*common)
            self.assertTrue(dry_run["dry_run"])
            applied = self.run_cli(*common, "--execute")
            self.assertTrue(applied["lock_updated"])
            status = self.run_cli(
                "status", "--project", project_path, "--source", source, "--lock", lock,
            )
            self.assertEqual(status["state"], "clean")

    def test_automation_code_export_and_wave_guards(self) -> None:
        event = self.example("automation-event-v1.json")
        plan = SYNC.automation_plan(event)
        self.assertEqual(plan["action"], "create-or-update-pull-request")
        self.assertFalse(plan["protected_branch_write"])
        event["classification"] = "internal"
        self.assertEqual(SYNC.automation_plan(event)["action"], "excluded")
        invalid_event = self.example("automation-event-v1.json")
        invalid_event["site_key"] = "../../unsafe-branch"
        with self.assertRaisesRegex(SYNC.SyncError, "site_key"):
            SYNC.automation_plan(invalid_event)

        inventory = {
            "surfaces": [
                {"identity": "attachment:media:hero", "compatibility": "supported", "dependencies": []},
                {"identity": "page:page:home", "compatibility": "supported", "dependencies": ["attachment:media:hero"]},
            ]
        }
        self.assertEqual(
            SYNC.topological_waves(inventory, 10),
            [["attachment:media:hero"], ["page:page:home"]],
        )
        inventory["surfaces"][0]["dependencies"] = ["page:page:home"]
        with self.assertRaisesRegex(SYNC.SyncError, "cycle"):
            SYNC.topological_waves(inventory, 10)

        with tempfile.TemporaryDirectory() as temporary:
            theme = Path(temporary)
            (theme / "templates").mkdir()
            (theme / "templates" / "home.html").write_text("<!-- wp:post-content /-->")
            export = SYNC.validate_code_export(theme)
            self.assertTrue(export["requires_human_review"])
            self.assertFalse(export["direct_protected_branch_write"])
            outside = theme.parent / "outside.css"
            outside.write_text("private")
            (theme / "assets").mkdir()
            (theme / "assets" / "linked.css").symlink_to(outside)
            with self.assertRaisesRegex(SYNC.SyncError, "symlink"):
                SYNC.validate_code_export(theme)

    def test_catalog_routing_templates_and_runtime_are_shipped(self) -> None:
        catalog = yaml.safe_load((ROOT / "catalog" / "plugins-v1.yaml").read_text())
        self.assertIn("wordpress-git-sync", catalog["marketplace"]["plugin_order"])
        package = next(item for item in catalog["packages"] if item["name"] == "wordpress-git-sync")
        self.assertEqual(package["executables"], ["scripts/wp_content_sync.py"])
        central = next(item for item in catalog["packages"] if item["name"] == "amsoft-agentic-workflows")
        self.assertIn("amsoft-wordpress-git-sync-management", {item["name"] for item in central["skills"]})
        self.assertEqual(catalog["documentation"]["central_component_count"], 28)
        self.assertTrue((PACKAGE / "templates" / "github" / "wordpress-managed-content-sync.yml").is_file())
        self.assertGreaterEqual(len(list((PACKAGE / "skills" / "wordpress-git-sync-management" / "templates" / "migration").iterdir())), 5)
        php = shutil.which("php")
        if php:
            for php_file in (PACKAGE / "runtime" / "amsoft-wordpress-git-sync").rglob("*.php"):
                result = subprocess.run([php, "-l", str(php_file)], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def run_cli(self, *arguments: object) -> dict:
        result = subprocess.run(
            [sys.executable, str(CLI), *map(str, arguments)],
            check=False,
            capture_output=True,
            text=True,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(result.returncode, 0, payload)
        return payload


if __name__ == "__main__":
    unittest.main()
