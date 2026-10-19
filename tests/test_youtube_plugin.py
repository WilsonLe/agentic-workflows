from __future__ import annotations

import importlib.util
import json
import os
import shutil
import stat
import subprocess
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


def codex_payload(**updates: object) -> bytes:
    cookie = {
        "domain": ".example.com", "path": "/", "name": "SID", "value": SENTINEL,
        "secure": True, "httpOnly": True, "expires": -1,
    }
    cookie.update(updates)
    return json.dumps({"cookies": [cookie]}).encode()


class CodexCookieTests(unittest.TestCase):
    def test_session_and_httponly_preserve_cookie_semantics(self) -> None:
        data = cookie_store.codex_cookie_bytes(codex_payload(), ["https://www.example.com/video"])
        self.assertIn(b"#HttpOnly_.example.com\tTRUE\t/\tTRUE\t0\tSID\t", data)

    def test_invalid_scope_and_cookie_shape_fail_without_secret_output(self) -> None:
        for updates in (
            {"domain": ".other.com"}, {"domain": ".com"},
            {"domain": "example.com"}, {"partitionKey": {"topLevelSite": "https://other.com"}},
            {"name": "bad\nname"}, {"value": SENTINEL + "\tbad"},
            {"secure": "TRUE"}, {"httpOnly": None}, {"path": "relative"},
            {"expires": float("nan")}, {"expires": True}, {"expires": -2}, {"expires": -0.5},
        ):
            with self.subTest(updates=updates), self.assertRaises(cookie_store.CookieStoreError) as error:
                cookie_store.codex_cookie_bytes(codex_payload(**updates), ["https://www.example.com/video"])
            self.assertNotIn(SENTINEL, str(error.exception))

    def test_opaque_and_nonce_partition_markers_are_rejected(self) -> None:
        for flag in (True, False, None, "false", 0, {}):
            with self.subTest(flag=flag), self.assertRaisesRegex(cookie_store.CookieStoreError, "partitioned"):
                cookie_store.codex_cookie_bytes(
                    codex_payload(partitionKeyOpaque=flag), ["https://example.com/"],
                )
        with self.assertRaisesRegex(cookie_store.CookieStoreError, "partitioned"):
            cookie_store.codex_cookie_bytes(
                codex_payload(partitionKey=None), ["https://example.com/"],
            )

    def test_empty_expired_malformed_and_oversized_responses_fail(self) -> None:
        for payload in (
            b"{}", b"{", b"[]", b'{"cookies":[]}', b'{"cookies":[null]}',
            codex_payload(expires=1), b"x" * (cookie_store.MAX_COOKIE_FILE_BYTES + 1),
        ):
            with self.subTest(size=len(payload)), self.assertRaises(cookie_store.CookieStoreError):
                cookie_store.codex_cookie_bytes(payload, ["https://example.com/"])

    def test_scope_requires_one_https_origin(self) -> None:
        for urls in (
            ["http://example.com/"],
            ["https://example.com/", "https://www.example.com/"],
        ):
            with self.assertRaisesRegex(cookie_store.CookieStoreError, "one HTTPS origin"):
                cookie_store.codex_cookie_bytes(codex_payload(), urls)

    def test_temporary_cookie_file_is_protected_and_removed_on_exception(self) -> None:
        destination = None
        with self.assertRaisesRegex(RuntimeError, "consumer failed"):
            with cookie_store.codex_cookie_file(codex_payload(), ["https://example.com/"]) as destination:
                self.assertEqual(stat.S_IMODE(destination.parent.stat().st_mode), 0o700)
                self.assertEqual(stat.S_IMODE(destination.stat().st_mode), 0o600)
                self.assertIn(SENTINEL, destination.read_text())
                raise RuntimeError("consumer failed")
        self.assertFalse(destination.exists())
        self.assertFalse(destination.parent.exists())


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

    def test_unknown_fields_and_unsafe_urls_fail_closed(self) -> None:
        with self.assertRaisesRegex(youtube.YouTubeOperationError, "unknown fields"):
            youtube.validate_request(inspect_request(raw_args=["--exec", "bad"]))
        for url in (
            "file:///tmp/video", "https://user:secret@example.com/video",
            "https:///missing", "https://example.com:bad/video",
            "https://example.com:0/video", "https://example.com/video\n",
            "ytsearch:video", "https://example.com/a b",
        ):
            with self.subTest(url=url), self.assertRaises(youtube.YouTubeOperationError):
                youtube.validate_request(inspect_request(urls=[url]))

    def test_platform_selection_is_delegated_to_yt_dlp(self) -> None:
        for url in (
            "https://vimeo.com/123", "https://www.tiktok.com/@user/video/123",
            "https://www.instagram.com/reel/123/", "https://www.dailymotion.com/video/123",
            "https://example.com/video", "http://example.com/video",
        ):
            with self.subTest(url=url):
                payload = inspect_request(urls=[url])
                jsonschema.validate(payload, json.loads(OPERATION_SCHEMA.read_text()))
                request = youtube.validate_request(payload)
                self.assertEqual(youtube.build_command(request)[-1], url)

    def test_fragment_routed_media_keeps_identifier_at_execution_boundary(self) -> None:
        for url in (
            "https://ladigitale.dev/digiview/#/v/67a8e50aee2ec",
            "https://www.udemy.com/course/example/#/lecture/172757",
        ):
            with self.subTest(url=url):
                request = youtube.validate_request(inspect_request(urls=[url]))
                command = youtube.build_command(request)
                self.assertEqual(request["urls"][0], url)
                self.assertEqual(command[-1], url)
                self.assertNotIn("#", youtube.redacted_command(command)[-1])

    def test_youtube_cookie_file_cannot_authenticate_other_sites(self) -> None:
        with self.assertRaisesRegex(youtube.YouTubeOperationError, "only YouTube"):
            youtube.validate_request(inspect_request(
                urls=["https://vimeo.com/123"], auth_mode="browser_cookie_file",
            ))

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

    def test_non_youtube_outputs_include_extractor_namespace_and_youtube_paths_remain(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            youtube_command = youtube.build_command(youtube.validate_request(download_request(directory)))
            other_command = youtube.build_command(youtube.validate_request(download_request(
                directory, urls=["https://vimeo.com/123"],
            )))
            self.assertTrue(youtube_command[youtube_command.index("--output") + 1].startswith("%(uploader_id"))
            self.assertTrue(other_command[other_command.index("--output") + 1].startswith("%(extractor_key"))

    def test_codex_plan_is_cookie_free_and_runtime_requires_concealed_input(self) -> None:
        request = youtube.validate_request(inspect_request(
            urls=["https://example.com/video"], auth_mode="codex_browser",
        ))
        command = youtube.build_command(request)
        self.assertIn("<codex-browser-cookie-file>", command)
        with self.assertRaisesRegex(youtube.YouTubeOperationError, "concealed browser bridge"):
            youtube.execute(request)
        with self.assertRaisesRegex(youtube.YouTubeOperationError, "requires auth_mode"):
            youtube.execute(youtube.validate_request(inspect_request()), codex_cookie_payload=codex_payload())
        for urls in (["http://example.com/"], ["https://example.com/", "https://vimeo.com/"]):
            with self.assertRaisesRegex(youtube.YouTubeOperationError, "one HTTPS origin"):
                youtube.validate_request(inspect_request(urls=urls, max_items=2, auth_mode="codex_browser"))

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
                self.assertEqual(preview[index + 1], "<protected-browser-cookie-file>")
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

    def test_other_platform_download_reaches_consumer_and_sanitizes_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fake = self._fake_yt_dlp(root)
            body = fake.read_text().replace(
                "https://www.youtube.com/watch?v=BaW_jenozKc",
                "https://vimeo.com/123?token=private",
            )
            fake.write_text(body)
            request = youtube.validate_request(download_request(
                str(root / "output"), urls=["https://vimeo.com/123"],
            ))
            result = youtube.execute(request, yt_dlp=str(fake))
            self.assertEqual(result["records"][0]["webpage_url"], "https://vimeo.com/123")
            self.assertEqual(result["command"][-1], "https://vimeo.com/123")
            self.assertEqual(result["files"][0]["size"], 5)
            self.assertNotIn("token=private", json.dumps(result))

    def test_unsupported_platform_failure_is_sanitized(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fake = self._fake_yt_dlp(Path(directory), failure=f"Unsupported URL {SENTINEL}")
            request = youtube.validate_request(inspect_request(urls=["https://example.com/video"]))
            with self.assertRaisesRegex(youtube.YouTubeOperationError, "^unsupported_url$"):
                youtube.execute(request, yt_dlp=str(fake))

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

    @unittest.skipUnless(shutil.which("node"), "Node required for the Codex host transport")
    def test_codex_bridge_denies_missing_capability_without_raw_error_or_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            request = Path(directory) / "request.json"
            request.write_text(json.dumps(inspect_request(
                urls=["https://example.com/"], auth_mode="codex_browser",
            )))
            bridge = (SCRIPTS / "codex_browser_cookies.mjs").as_uri()
            script = f"""
import {{runWithCodexCookies}} from {json.dumps(bridge)};
const tab = {{capabilities: {{get: async () => {{ throw Error({json.dumps(SENTINEL)}); }}}}}};
try {{
  await runWithCodexCookies({{tab, requestPath: {json.dumps(str(request))}}});
  process.exitCode = 1;
}} catch (error) {{ console.log(error.message); }}
"""
            completed = subprocess.run(
                ["node", "--input-type=module", "-e", script], capture_output=True, text=True, timeout=30,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn("origin-scoped cookie transfer is unavailable", completed.stdout)
            self.assertNotIn(SENTINEL, completed.stdout + completed.stderr)

    def test_codex_cookie_reaches_consumer_and_is_removed_after_success_failure_and_timeout(self) -> None:
        for outcome in ("success", "failure", "timeout"):
            paths = []

            def consumer(command, **kwargs):
                path = Path(command[command.index("--cookies") + 1])
                paths.append(path)
                self.assertIn(SENTINEL, path.read_text())
                self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
                self.assertNotIn(SENTINEL, json.dumps(command))
                if outcome == "timeout":
                    raise subprocess.TimeoutExpired(command, 30, output=SENTINEL)
                return subprocess.CompletedProcess(
                    command, 0 if outcome == "success" else 1,
                    stdout='{"id":"test"}', stderr="cookie invalid " + SENTINEL,
                )

            request = youtube.validate_request(inspect_request(
                urls=["https://example.com/video"], auth_mode="codex_browser",
            ))
            with self.subTest(outcome=outcome), mock.patch.object(youtube.subprocess, "run", side_effect=consumer):
                if outcome == "success":
                    result = youtube.execute(request, codex_cookie_payload=codex_payload())
                    jsonschema.validate(result, json.loads(RESULT_SCHEMA.read_text()))
                    self.assertNotIn(SENTINEL, json.dumps(result))
                    self.assertNotIn(str(paths[0]), json.dumps(result))
                else:
                    with self.assertRaises(youtube.YouTubeOperationError) as error:
                        youtube.execute(request, codex_cookie_payload=codex_payload())
                    self.assertNotIn(SENTINEL, str(error.exception))
            self.assertEqual(len(paths), 1)
            self.assertFalse(paths[0].parent.exists())

    def test_cookie_is_removed_before_manifest_even_when_tempdir_is_inside_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "output"
            output.mkdir()
            request = youtube.validate_request(download_request(
                str(output), urls=["https://example.com/video"], auth_mode="codex_browser",
            ))
            with mock.patch.object(cookie_store.tempfile, "tempdir", str(output)), mock.patch.object(
                youtube.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, '{"id":"test"}', ''),
            ):
                result = youtube.execute(request, codex_cookie_payload=codex_payload())
            self.assertEqual(result["files"], [])
            self.assertEqual(list(output.iterdir()), [])
            self.assertNotIn(SENTINEL, json.dumps(result))

    @unittest.skipUnless(shutil.which("node"), "Node required for the Codex host transport")
    def test_codex_javascript_bridge_pipes_cookies_to_real_python_cli(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fake = self._fake_yt_dlp(root)
            # Prove the subprocess receives the credential without echoing it.
            body = fake.read_text().replace('args = sys.argv[1:]',
                'args = sys.argv[1:]\nassert "--cookies" in args\n'
                + f'assert {SENTINEL!r} in pathlib.Path(args[args.index("--cookies") + 1]).read_text()')
            fake.write_text(body)
            request = root / "request.json"
            request.write_text(json.dumps(download_request(
                "./output", urls=["https://example.com/video"], auth_mode="codex_browser",
            )))
            bridge = (SCRIPTS / "codex_browser_cookies.mjs").as_uri()
            config = {
                "requestPath": str(request), "python": sys.executable, "ytDlp": str(fake),
                "resultFile": str(root / "result.json"),
            }
            script = f"""
import {{runWithCodexCookies}} from {json.dumps(bridge)};
const config = {json.dumps(config)};
const response = {codex_payload().decode()};
const tab = {{capabilities: {{get: async name => {{
  if (name !== 'cdp') throw Error('wrong capability');
  return {{send: async (method, params) => {{
    if (method !== 'Network.getCookies' || params.urls[0] !== 'https://example.com/video') throw Error('wrong scope');
    return response;
  }}}};
}}}}}};
const result = await runWithCodexCookies({{...config, tab}});
console.log(JSON.stringify(result));
"""
            completed = subprocess.run(
                ["node", "--input-type=module", "-e", script], capture_output=True, text=True, timeout=30,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertNotIn(SENTINEL, completed.stdout + completed.stderr)
            result = json.loads(completed.stdout)
            self.assertTrue(result["ok"])
            self.assertEqual(result["auth_mode"], "codex_browser")
            self.assertTrue((root / "result.json").exists())
            self.assertTrue((root / "output/channel/single/test.mp4").exists())

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
        for name in ("youtube_cookie_store.py", "youtube_yt_dlp.py", "codex_browser_cookies.mjs"):
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
