from __future__ import annotations

import importlib.util
import json
import os
import shutil
import stat
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "youtube"
SCRIPTS = PLUGIN / "scripts"
INSPECTION = PLUGIN / "skills" / "youtube-content-inspection"
OPERATION_SCHEMA = INSPECTION / "schemas" / "youtube-operation-v1.schema.json"
RESULT_SCHEMA = INSPECTION / "schemas" / "youtube-result-v1.schema.json"

sys.path.insert(0, str(SCRIPTS))


def load_module(name: str, path: Path):
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


cookie_store = load_module("youtube_cookie_store", SCRIPTS / "youtube_cookie_store.py")
youtube = load_module("youtube_yt_dlp", SCRIPTS / "youtube_yt_dlp.py")

SENTINEL = "COOKIE_SECRET_SENTINEL_7de193"


def netscape_cookie(
    *,
    domain: str = ".youtube.com",
    expiry: int = 4102444800,
    value: str = SENTINEL,
) -> bytes:
    return (
        "# Netscape HTTP Cookie File\n"
        f"{domain}\tTRUE\t/\tTRUE\t{expiry}\tSID\t{value}\n"
    ).encode()


def inspect_request(**updates: object) -> dict[str, object]:
    request: dict[str, object] = {
        "schema_version": 1,
        "operation": "inspect",
        "urls": ["https://www.youtube.com/watch?v=BaW_jenozKc"],
        "auth_mode": "public",
        "playlist_policy": "single",
        "max_items": 1,
    }
    request.update(updates)
    return request


def download_request(output_root: str, **updates: object) -> dict[str, object]:
    request: dict[str, object] = {
        "schema_version": 1,
        "operation": "download",
        "urls": ["https://www.youtube.com/watch?v=BaW_jenozKc"],
        "auth_mode": "public",
        "rights_basis": {
            "category": "service_authorized",
            "statement": "Bounded public yt-dlp integration test media.",
        },
        "output_root": output_root,
        "playlist_policy": "single",
        "max_items": 1,
        "media_mode": "video",
        "max_resolution": 360,
    }
    request.update(updates)
    return request


class CookieStoreTests(unittest.TestCase):
    def test_valid_cookie_summary_contains_no_names_or_values(self) -> None:
        summary = cookie_store.validate_cookie_bytes(netscape_cookie(), now=1)
        public = summary.public()
        self.assertEqual(public["record_count"], 1)
        self.assertEqual(public["domains"], ["youtube.com"])
        self.assertNotIn(SENTINEL, json.dumps(public))
        self.assertNotIn("SID", json.dumps(public))

    def test_http_only_youtube_cookie_is_allowed(self) -> None:
        payload = netscape_cookie(domain="#HttpOnly_.youtube.com")
        self.assertEqual(cookie_store.validate_cookie_bytes(payload).record_count, 1)

    def test_non_youtube_domain_is_rejected(self) -> None:
        with self.assertRaisesRegex(cookie_store.CookieStoreError, "non-YouTube"):
            cookie_store.validate_cookie_bytes(netscape_cookie(domain=".google.com"))

    def test_malformed_and_expired_only_files_are_rejected(self) -> None:
        with self.assertRaisesRegex(cookie_store.CookieStoreError, "Netscape"):
            cookie_store.validate_cookie_bytes(b"not a cookie file")
        with self.assertRaisesRegex(cookie_store.CookieStoreError, "expired"):
            cookie_store.validate_cookie_bytes(netscape_cookie(expiry=10), now=20)

    def test_install_uses_owner_only_modes_and_status_is_redacted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "export.txt"
            source.write_bytes(netscape_cookie())
            source.chmod(0o600)
            config = root / "config"
            with mock.patch.dict(os.environ, {"AGENTIC_WORKFLOWS_YOUTUBE_CONFIG_DIR": str(config)}):
                cookie_store.install(source)
                destination = config / "cookies.txt"
                self.assertEqual(stat.S_IMODE(config.stat().st_mode), 0o700)
                self.assertEqual(stat.S_IMODE(destination.stat().st_mode), 0o400)
                rendered = json.dumps(cookie_store.status())
                self.assertNotIn(SENTINEL, rendered)
                self.assertNotIn("SID", rendered)

    def test_symlink_and_group_writable_source_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.txt"
            source.write_bytes(netscape_cookie())
            source.chmod(0o620)
            with self.assertRaisesRegex(cookie_store.CookieStoreError, "writable"):
                cookie_store.validate_cookie_file(source)
            source.chmod(0o600)
            link = root / "link.txt"
            link.symlink_to(source)
            with self.assertRaisesRegex(cookie_store.CookieStoreError, "symbolic"):
                cookie_store.validate_cookie_file(link)

    def test_failed_rotation_restores_previous_record(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = root / "config"
            previous = root / "previous.txt"
            replacement = root / "replacement.txt"
            previous.write_bytes(netscape_cookie(value="previous"))
            replacement.write_bytes(netscape_cookie(value="replacement"))
            previous.chmod(0o600)
            replacement.chmod(0o600)
            with mock.patch.dict(os.environ, {"AGENTIC_WORKFLOWS_YOUTUBE_CONFIG_DIR": str(config)}):
                cookie_store.install(previous)
                with mock.patch.object(
                    cookie_store, "verify", side_effect=cookie_store.CookieStoreError("failed")
                ):
                    with self.assertRaisesRegex(cookie_store.CookieStoreError, "failed"):
                        cookie_store.rotate(
                            replacement,
                            verify_url="https://www.youtube.com/watch?v=test",
                            yt_dlp="yt-dlp",
                        )
                self.assertEqual((config / "cookies.txt").read_bytes(), previous.read_bytes())

    def test_revoke_requires_exact_confirmation(self) -> None:
        with self.assertRaisesRegex(cookie_store.CookieStoreError, "exact confirmation"):
            cookie_store.revoke("yes")

    def test_verification_rejects_non_youtube_url_before_process(self) -> None:
        with self.assertRaisesRegex(cookie_store.CookieStoreError, "YouTube URL"):
            cookie_store.verify("https://example.com/watch?v=x")


class RequestAndCommandTests(unittest.TestCase):
    def test_public_inspect_is_media_free_and_has_no_cookie_option(self) -> None:
        request = youtube.validate_request(inspect_request())
        command = youtube.build_command(request)
        self.assertIn("--simulate", command)
        self.assertIn("--dump-single-json", command)
        self.assertNotIn("--cookies", command)
        self.assertNotIn("--cookies-from-browser", command)
        self.assertIn("--no-plugin-dirs", command)
        self.assertIn("--no-remote-components", command)
        self.assertIn("--no-exec", command)
        if shutil.which("deno") or shutil.which("node"):
            self.assertIn("--js-runtimes", command)

    def test_media_operation_requires_rights_basis(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            request = download_request(directory)
            del request["rights_basis"]
            with self.assertRaisesRegex(youtube.YouTubeOperationError, "rights_basis"):
                youtube.validate_request(request)

    def test_unknown_fields_and_non_youtube_urls_fail_closed(self) -> None:
        with self.assertRaisesRegex(youtube.YouTubeOperationError, "unknown fields"):
            youtube.validate_request(inspect_request(raw_args=["--exec", "bad"]))
        with self.assertRaisesRegex(youtube.YouTubeOperationError, "YouTube URLs"):
            youtube.validate_request(inspect_request(urls=["https://example.com/video"]))
        with self.assertRaisesRegex(youtube.YouTubeOperationError, "YouTube URLs"):
            youtube.validate_request(inspect_request(urls=["file:///tmp/video"]))

    def test_playlist_and_resource_bounds(self) -> None:
        with self.assertRaisesRegex(youtube.YouTubeOperationError, "max_items"):
            youtube.validate_request(
                inspect_request(playlist_policy="playlist", max_items=101)
            )
        with self.assertRaisesRegex(youtube.YouTubeOperationError, "concurrent_fragments"):
            youtube.validate_request(inspect_request(concurrent_fragments=5))
        with self.assertRaisesRegex(youtube.YouTubeOperationError, "rate_limit"):
            youtube.validate_request(inspect_request(rate_limit="unlimited"))
        with self.assertRaisesRegex(youtube.YouTubeOperationError, "exactly one URL"):
            youtube.validate_request(
                inspect_request(
                    urls=[
                        "https://www.youtube.com/playlist?list=PL123",
                        "https://www.youtube.com/playlist?list=PL456",
                    ],
                    playlist_policy="playlist",
                    max_items=2,
                )
            )
        with self.assertRaisesRegex(youtube.YouTubeOperationError, "every explicit URL"):
            youtube.validate_request(
                inspect_request(
                    urls=[
                        "https://www.youtube.com/watch?v=BaW_jenozKc",
                        "https://youtu.be/jNQXAC9IVRw",
                    ],
                    max_items=1,
                )
            )

    def test_live_mode_is_explicitly_experimental(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(youtube.YouTubeOperationError, "explicit"):
                youtube.validate_request(
                    download_request(directory, media_mode="live")
                )

    def test_authenticated_mode_uses_only_managed_cookie_path_and_redacts_it(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = root / "config"
            source = root / "export.txt"
            source.write_bytes(netscape_cookie())
            source.chmod(0o600)
            with mock.patch.dict(os.environ, {"AGENTIC_WORKFLOWS_YOUTUBE_CONFIG_DIR": str(config)}):
                cookie_store.install(source)
                request = youtube.validate_request(
                    inspect_request(auth_mode="browser_cookie_file")
                )
                command = youtube.build_command(request)
                self.assertEqual(command.count("--cookies"), 1)
                self.assertNotIn("--cookies-from-browser", command)
                index = command.index("--cookies")
                self.assertEqual(command[index + 1], str(config / "cookies.txt"))
                preview = youtube.redacted_command(command)
                self.assertEqual(preview[index + 1], "<protected-youtube-cookie-file>")
                self.assertNotIn(str(config), json.dumps(preview))

    def test_audio_section_subtitle_and_sponsorblock_options_are_allowlisted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            request = youtube.validate_request(
                download_request(
                    directory,
                    media_mode="audio",
                    audio_format="m4a",
                    subtitle_languages=["en"],
                    automatic_subtitles=True,
                    sections=["*0:00-0:05"],
                    sponsorblock_mark=["sponsor"],
                )
            )
            command = youtube.build_command(request)
            self.assertIn("--extract-audio", command)
            self.assertIn("--write-subs", command)
            self.assertIn("--write-auto-subs", command)
            self.assertIn("--download-sections", command)
            self.assertIn("--sponsorblock-mark", command)
            self.assertIn("--no-overwrites", command)

    def test_sync_has_bounded_archive_under_output_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            request = youtube.validate_request(
                {
                    **download_request(directory),
                    "operation": "sync",
                    "playlist_policy": "playlist",
                    "playlist_items": "1:5",
                    "max_items": 5,
                }
            )
            command = youtube.build_command(request)
            archive = Path(command[command.index("--download-archive") + 1])
            self.assertEqual(archive.parent, Path(directory).resolve())
            self.assertEqual(archive.name, ".youtube-download-archive.txt")
            self.assertEqual(command[command.index("--playlist-end") + 1], "5")


class ExecutionTests(unittest.TestCase):
    def _fake_yt_dlp(self, directory: Path, *, failure: str | None = None) -> Path:
        script = directory / "fake-yt-dlp"
        if failure is None:
            body = """#!/usr/bin/env python3
import json
import pathlib
import sys
args = sys.argv[1:]
if "--paths" in args:
    root = pathlib.Path(args[args.index("--paths") + 1].removeprefix("home:"))
    target = root / "channel" / "single" / "test.mp4"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(b"media")
print(json.dumps({
    "id": "BaW_jenozKc",
    "title": "Test video",
    "webpage_url": "https://www.youtube.com/watch?v=BaW_jenozKc",
    "formats": [{"format_id": "18", "height": 360, "url": "https://secret.invalid/token"}],
    "http_headers": {"Cookie": "COOKIE_SECRET_SENTINEL_7de193"},
    "subtitles": {"en": [{"url": "https://secret.invalid/sub"}]}
}))
"""
        else:
            body = f"""#!/usr/bin/env python3
import sys
sys.stderr.write({failure!r})
raise SystemExit(1)
"""
        script.write_text(body, encoding="utf-8")
        script.chmod(0o755)
        return script

    def test_inspect_output_is_sanitized(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fake = self._fake_yt_dlp(Path(directory))
            request = youtube.validate_request(inspect_request())
            result = youtube.execute(request, yt_dlp=str(fake))
            rendered = json.dumps(result)
            self.assertNotIn(SENTINEL, rendered)
            self.assertNotIn("secret.invalid", rendered)
            self.assertNotIn("http_headers", rendered)
            self.assertEqual(result["records"][0]["subtitle_languages"], ["en"])

    def test_download_manifest_hashes_created_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fake = self._fake_yt_dlp(root)
            output = root / "output"
            result_file = root / "result.json"
            request = youtube.validate_request(download_request(str(output)))
            result = youtube.execute(request, yt_dlp=str(fake), result_file=result_file)
            self.assertEqual(len(result["files"]), 1)
            self.assertEqual(result["files"][0]["path"], "channel/single/test.mp4")
            self.assertEqual(result["files"][0]["size"], 5)
            jsonschema.validate(json.loads(result_file.read_text()), json.loads(RESULT_SCHEMA.read_text()))

    def test_failure_is_classified_without_raw_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fake = self._fake_yt_dlp(
                Path(directory),
                failure=f"HTTP Error 429 cookie={SENTINEL}",
            )
            request = youtube.validate_request(inspect_request())
            with self.assertRaisesRegex(youtube.YouTubeOperationError, "^rate_limited$") as caught:
                youtube.execute(request, yt_dlp=str(fake))
            self.assertNotIn(SENTINEL, str(caught.exception))


class PackageContractTests(unittest.TestCase):
    def test_examples_validate_against_schema_and_runtime(self) -> None:
        schema = json.loads(OPERATION_SCHEMA.read_text())
        examples = sorted(PLUGIN.glob("skills/*/examples/*.json"))
        self.assertGreaterEqual(len(examples), 4)
        for path in examples:
            with self.subTest(path=path.relative_to(PLUGIN)):
                payload = json.loads(path.read_text())
                jsonschema.validate(payload, schema)
                self.assertEqual(youtube.validate_request(payload)["schema_version"], 1)

    def test_source_and_central_skills_and_helpers_match_generated_contract(self) -> None:
        central = ROOT / "plugins" / "agentic-workflows"
        for source_skill in sorted((PLUGIN / "skills").iterdir()):
            central_skill = central / "skills" / f"{source_skill.name}"
            self.assertTrue(central_skill.is_dir())
            for source in source_skill.rglob("*"):
                if not source.is_file():
                    continue
                destination = central_skill / source.relative_to(source_skill)
                self.assertTrue(destination.is_file())
        for name in ("youtube_cookie_store.py", "youtube_yt_dlp.py"):
            self.assertEqual(
                (SCRIPTS / name).read_bytes(),
                (central / "scripts" / name).read_bytes(),
            )

    def test_skill_contract_forbids_secret_and_unsafe_surfaces(self) -> None:
        text = "\n".join(path.read_text() for path in (PLUGIN / "skills").rglob("*.md"))
        for marker in (
            "Never paste or display",
            "rights basis",
            "No DRM",
            "No raw config",
            "PO-token",
            "no-overwrite",
        ):
            self.assertIn(marker.lower(), text.lower())
        self.assertNotIn(SENTINEL, text)


if __name__ == "__main__":
    unittest.main()
