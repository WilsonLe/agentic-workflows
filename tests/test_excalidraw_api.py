from __future__ import annotations

import argparse
import io
import json
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "plugins" / "excalidraw" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import excalidraw_api as api  # noqa: E402

SYNTHETIC_KEY = "synthetic-excalidraw-personal-key-for-tests-only"


class FakeResponse:
    def __init__(self, payload: object, headers: dict[str, str] | None = None):
        self.raw = json.dumps(payload).encode("utf-8")
        self.headers = headers or {}

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self, _size: int) -> bytes:
        return self.raw


class ExcalidrawAPITests(unittest.TestCase):
    def args(self, **overrides: object) -> argparse.Namespace:
        values: dict[str, object] = {
            "collection_id": None,
            "scene_id": None,
            "user_id": None,
            "invite_id": None,
            "confirm_write": None,
            "confirm_replace": None,
            "confirm_destructive": None,
        }
        values.update(overrides)
        return argparse.Namespace(**values)

    def test_collection_list_path_needs_no_unrelated_ids(self) -> None:
        self.assertEqual(
            api.resolve_path(api.OPERATIONS["collections"], self.args()),
            "/collections",
        )
        self.assertEqual(
            api.resolve_path(
                api.OPERATIONS["collection"],
                self.args(collection_id="private/id"),
            ),
            "/collections/private%2Fid",
        )

    def test_pagination_bounds(self) -> None:
        self.assertEqual(
            api.bounded_pagination(100, 0), {"limit": "100", "offset": "0"}
        )
        for limit in (0, 101):
            with self.assertRaises(api.ExcalidrawAPIError):
                api.bounded_pagination(limit, 0)
        with self.assertRaises(api.ExcalidrawAPIError):
            api.bounded_pagination(10, -1)

    def test_write_classes_require_exact_confirmations(self) -> None:
        with self.assertRaises(api.ExcalidrawAPIError):
            api.require_approvals(api.OPERATIONS["scene-content-patch"], self.args())
        api.require_approvals(
            api.OPERATIONS["scene-content-patch"],
            self.args(confirm_write=api.WRITE_CONFIRMATION),
        )
        with self.assertRaises(api.ExcalidrawAPIError):
            api.require_approvals(
                api.OPERATIONS["scene-content-replace"],
                self.args(confirm_write=api.WRITE_CONFIRMATION),
            )
        with self.assertRaises(api.ExcalidrawAPIError):
            api.require_approvals(
                api.OPERATIONS["scene-delete"],
                self.args(confirm_write=api.WRITE_CONFIRMATION),
            )

    def test_metadata_payloads_are_typed(self) -> None:
        api.validate_metadata_payload("collection-create", {"name": "Project"})
        api.validate_metadata_payload(
            "scene-create",
            {"name": "Architecture", "pinned": False, "collectionId": "c1"},
        )
        api.validate_metadata_payload(
            "collection-scene-create",
            {"name": "Architecture", "pinned": False},
        )
        api.validate_metadata_payload("scene-update", {"pinned": True})
        api.validate_metadata_payload(
            "workspace-update",
            {"name": "Design", "picture": "https://example.com/logo.png"},
        )
        api.validate_metadata_payload(
            "user-update",
            {
                "role": "admin",
                "preferences": {
                    "sceneOrder": "updated",
                    "ossAutoRedirect": True,
                },
            },
        )
        api.validate_metadata_payload(
            "invite-create",
            {"email": "person@example.com", "role": "member"},
        )
        api.validate_metadata_payload(
            "invite-create",
            {
                "role": "admin",
                "maxUses": "unlimited",
                "restrictedDomains": ["example.com"],
            },
        )
        with self.assertRaises(api.ExcalidrawAPIError):
            api.validate_metadata_payload("scene-update", {"unknown": True})
        with self.assertRaises(api.ExcalidrawAPIError):
            api.validate_metadata_payload(
                "invite-create",
                {"email": "not-an-email", "role": "member"},
            )
        with self.assertRaises(api.ExcalidrawAPIError):
            api.validate_metadata_payload(
                "user-update",
                {"preferences": {"sceneOrder": "random"}},
            )

    def test_broad_account_routes_are_typed(self) -> None:
        self.assertEqual(
            api.resolve_path(
                api.OPERATIONS["collection-scene-create"],
                self.args(collection_id="c1"),
            ),
            "/collections/c1/scenes",
        )
        self.assertEqual(
            api.resolve_path(
                api.OPERATIONS["user-update"],
                self.args(user_id="u1"),
            ),
            "/workspaces/users/u1",
        )
        self.assertEqual(
            api.resolve_path(
                api.OPERATIONS["invite-delete"],
                self.args(invite_id="i1"),
            ),
            "/workspaces/invites/i1",
        )

    def test_request_uses_fixed_origin_and_parses_rate_headers(self) -> None:
        response = FakeResponse(
            {"data": []},
            {"X-RateLimit-Remaining": "599"},
        )
        with (
            mock.patch.object(api, "tls_context"),
            mock.patch.object(
                api.urllib.request, "urlopen", return_value=response
            ) as open_url,
        ):
            payload, headers = api.request_json(
                SYNTHETIC_KEY,
                "GET",
                "/collections",
                query={"limit": "1"},
            )
        self.assertEqual(payload, {"data": []})
        self.assertEqual(headers["x-ratelimit-remaining"], "599")
        request = open_url.call_args.args[0]
        self.assertEqual(
            request.full_url,
            "https://api.excalidraw.com/api/v1/collections?limit=1",
        )
        self.assertEqual(request.get_header("Authorization"), f"Bearer {SYNTHETIC_KEY}")

    def test_safe_read_retries_but_unknown_write_does_not(self) -> None:
        response = FakeResponse({"data": []})
        with (
            mock.patch.object(api, "tls_context"),
            mock.patch.object(
                api.urllib.request,
                "urlopen",
                side_effect=(urllib.error.URLError("temporary"), response),
            ) as open_url,
            mock.patch.object(api.time, "sleep"),
        ):
            payload, _ = api.request_json(SYNTHETIC_KEY, "GET", "/collections")
        self.assertEqual(payload, {"data": []})
        self.assertEqual(open_url.call_count, 2)

        with (
            mock.patch.object(api, "tls_context"),
            mock.patch.object(
                api.urllib.request,
                "urlopen",
                side_effect=urllib.error.URLError("unknown"),
            ) as open_url,
        ):
            with self.assertRaises(api.UnknownWriteOutcome):
                api.request_json(
                    SYNTHETIC_KEY, "PATCH", "/scenes/s1", body={"name": "X"}
                )
        self.assertEqual(open_url.call_count, 1)

    def test_http_errors_are_sanitized_and_redacted(self) -> None:
        error = urllib.error.HTTPError(
            "https://api.excalidraw.com/api/v1/collections",
            401,
            "Unauthorized",
            {},
            io.BytesIO(json.dumps({"message": f"invalid {SYNTHETIC_KEY}"}).encode()),
        )
        with (
            mock.patch.object(api, "tls_context"),
            mock.patch.object(api.urllib.request, "urlopen", side_effect=error),
        ):
            with self.assertRaises(api.ExcalidrawAPIError) as caught:
                api.request_json(
                    SYNTHETIC_KEY, "GET", "/collections", max_read_retries=0
                )
        self.assertNotIn(SYNTHETIC_KEY, str(caught.exception))

    def test_load_payload_rejects_credential_fields(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "payload.json"
            path.write_text(json.dumps({"authorization": "bad"}), encoding="utf-8")
            with self.assertRaises(api.ExcalidrawAPIError):
                api.load_payload(path)


if __name__ == "__main__":
    unittest.main()
