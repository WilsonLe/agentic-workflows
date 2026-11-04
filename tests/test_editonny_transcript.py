from __future__ import annotations

from contextlib import nullcontext
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "plugins/agentic-workflows/skills/video-editing/scripts/editonny_transcript.py"
SPEC = importlib.util.spec_from_file_location("editonny_transcript", SCRIPT)
assert SPEC and SPEC.loader
adapter = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(adapter)


def content_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


class EditonnyTranscriptTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.source = self.root / "Café talk.mp4"
        self.source.write_bytes(b"approved synthetic source")
        self.project = self.root / "job/project/v001/project"
        self.project.mkdir(parents=True)
        self.edit = self.project.parent / "edit"
        (self.edit / "transcripts").mkdir(parents=True)
        (self.edit / "verify").mkdir()
        self.native_source = self.edit / "transcripts/Café talk.json"
        self.cut_transcript = self.edit / "transcripts/cut.json"
        self.contract_hash = "1" * 64
        self.config = {"workflow": {"language": {"transcription": "en"}, "video": {"timing": "cfr"}}}
        self.record = {"id": "source-001", "path": str(self.source), "sha256": content_hash(self.source),
                       "facts": {"duration": 3.0, "audio_tracks": 1}}
        self.write(self.project / "project.json", self.config)
        self.write(self.edit / "state.json", {"settingsConfirmation": True})
        self.write(self.edit / "source_manifest.json", {"sources": [self.record]})
        self.normalized = self.root / "normalized.json"
        self.portable = {
            "schema_version": 1, "asset_id": f"sha256:{self.record['sha256']}",
            "source": {"path": str(self.source), "stream_index": 1, "duration_seconds": 3.0},
            "language": "en", "requested_language": "en", "runtime": "openrouter", "runtime_version": None,
            "model": "openai/whisper-large-v3-turbo", "timestamp_granularity": "word",
            "analysis_to_source": {"offset_seconds": 0.0, "analysis_duration_seconds": 3.0,
                                   "audio_sha256": "2" * 64, "rounding_tolerance_seconds": 0.05},
            "provider_response_sha256": "3" * 64, "segment_grouping": "word_span",
            "segments": [{"text": "Keep speech", "start_seconds": 0.6, "end_seconds": 1.1, "words": [
                {"text": "Keep", "start_seconds": 0.6, "end_seconds": 0.8, "confidence": None},
                {"text": "speech", "start_seconds": 0.8, "end_seconds": 1.1, "confidence": None},
            ]}],
        }
        self.write(self.normalized, self.portable)
        self.mapping = mock.Mock(return_value=(
            [{"text": "Keep", "start": 0.1, "end": 0.3, "seg": 0}], "sources", [],
        ))
        self.lock = mock.Mock(side_effect=lambda _project: nullcontext())
        self.confirmed = mock.Mock(return_value=self.config)
        imports = {
            "common": SimpleNamespace(
                content_hash=content_hash, file_signature=lambda path: f"test:{path.stat().st_size}",
            ),
            "project_contract": SimpleNamespace(managed_config=self.confirmed, digest=digest,
                                                settings_hash=lambda _config: self.contract_hash),
            "workspace": SimpleNamespace(managed_revision=lambda project: project.parent,
                                         selected_sources=lambda manifest, _config: manifest,
                                         verify_sources=self.verify_sources, revision_lock=self.lock),
            "render_cut": SimpleNamespace(edl_signature=digest, resolve_source=lambda name, _edit: Path(name)),
            "captions": SimpleNamespace(words_from_sources=self.mapping),
        }
        # Use the actual shared transcript validator and substitute only the optional
        # external Editonny runtime. The suite tests need no Editonny installation.
        self.enterContext(mock.patch.dict(sys.modules, imports))
        self.enterContext(mock.patch.object(sys, "path", [str(adapter.SUITE_SCRIPTS), *sys.path]))
        self.enterContext(mock.patch("openrouter_transcribe.probe_source", return_value=(1, 3.0)))

    @staticmethod
    def write(path, value):
        path.write_text(json.dumps(value), encoding="utf-8")

    def verify_sources(self, manifest):
        if any(content_hash(Path(row["path"])) != row["sha256"] for row in manifest["sources"]):
            raise ValueError("Source content changed")

    def native_cut(self):
        cut = self.edit / "cut.mp4"
        cut.write_bytes(b"measured cut")
        edl = self.edit / "edl.json"
        decisions = {"contractHash": self.contract_hash, "sources": {"alias": str(self.source)}, "ranges": [{}]}
        self.write(edl, decisions)
        timeline = self.edit / "cut_timeline.json"
        self.write(timeline, {
            "video": "cut.mp4", "preview": False, "contractHash": self.contract_hash, "duration": 2.5,
            "edl_sig": digest(decisions), "segments": [{"source": "alias", "source_path": str(self.source)}],
        })
        report = self.edit / "verify/cut_report.json"
        verification = digest({"video": content_hash(cut), "edl": content_hash(edl),
                               str(timeline): content_hash(timeline),
                               str(self.project / "project.json"): content_hash(self.project / "project.json")})
        self.write(report, {"video": str(cut), "edl": str(edl), "timeline": str(timeline),
                            "verificationIdentity": verification, "status": "failed", "flags": [{"code": "DEAD-AIR"}]})
        return cut, timeline, report

    def test_inspect_is_metadata_only_and_preserves_blocked_proposal(self):
        requested = self.root / "request.json"
        self.write(requested, {"captions": True})
        inspect = mock.Mock(return_value={"sources": [self.record]})
        propose = mock.Mock(side_effect=ValueError("Native proposal blocker"))
        intake = SimpleNamespace(inspect_sources=inspect, propose_settings=propose)
        with mock.patch.dict(sys.modules, {"intake": intake}):
            report = adapter.inspect_source(self.source, requested)
        inspect.assert_called_once_with([self.source], detect_language=False)
        self.assertEqual(propose.call_args.args[1], {"captions": True})
        self.assertEqual(report["proposalBlocked"], "Native proposal blocker")
        self.assertNotIn("proposal", report)

    def test_import_preserves_hosted_words_and_existing_transcript(self):
        result = adapter.import_transcript(self.project, self.normalized)
        native = adapter.read_object(self.native_source)
        self.assertEqual(native["words"], [
            {"text": "Keep", "start": 0.6, "end": 0.8}, {"text": "speech", "start": 0.8, "end": 1.1},
        ])
        self.assertEqual(native["source_sha256"], content_hash(self.source))
        self.assertEqual(native["provenance"]["normalized_transcript_sha256"], content_hash(self.normalized))
        self.assertEqual(result["sha256"], content_hash(self.native_source))
        if os.name != "nt":
            self.assertEqual(stat.S_IMODE(self.native_source.stat().st_mode), 0o600)
        inode = self.native_source.stat().st_ino
        self.assertEqual(adapter.import_transcript(self.project, self.normalized), result)
        self.assertEqual(self.native_source.stat().st_ino, inode)
        self.native_source.write_text("keep native transcript", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Preserved conflicting transcript"):
            adapter.import_transcript(self.project, self.normalized)
        self.assertEqual(self.native_source.read_text(), "keep native transcript")
        self.assertEqual(list(self.native_source.parent.glob(".transcript-*")), [])

    def test_import_blocks_unconfirmed_or_wrong_source_and_invalid_timing(self):
        self.confirmed.return_value = None
        with self.assertRaisesRegex(ValueError, "confirmed managed"):
            adapter.import_transcript(self.project, self.normalized)
        self.confirmed.return_value = self.config
        self.portable["asset_id"] = "sha256:" + "b" * 64
        self.write(self.normalized, self.portable)
        with self.assertRaisesRegex(ValueError, "selected source bytes"):
            adapter.import_transcript(self.project, self.normalized)
        self.portable["asset_id"] = f"sha256:{self.record['sha256']}"
        self.portable["segments"][0]["words"][0]["end_seconds"] = 2.0
        self.write(self.normalized, self.portable)
        with self.assertRaisesRegex(ValueError, "word timing"):
            adapter.import_transcript(self.project, self.normalized)
        self.assertFalse(self.native_source.exists())

    def test_maps_using_native_timeline_and_rejects_stale_cut(self):
        adapter.import_transcript(self.project, self.normalized)
        cut, timeline, report = self.native_cut()
        status = adapter.map_cut(self.project)
        self.mapping.assert_called_once()
        edit, native_timeline, fallback, mode = self.mapping.call_args.args
        self.assertEqual((edit, native_timeline["segments"][0]["source"], fallback, mode),
                         (self.edit, self.source.stem, None, "sources"))
        mapped = adapter.read_object(self.cut_transcript)
        self.assertEqual(mapped["words"][0]["start"], 0.1)
        self.assertEqual(mapped["source_sha256"], content_hash(cut))
        self.assertEqual(mapped["provenance"]["timeline_sha256"], content_hash(timeline))
        self.assertEqual(mapped["provenance"]["verification_identity"], adapter.read_object(report)["verificationIdentity"])
        self.assertEqual(status["sha256"], content_hash(self.cut_transcript))
        cut.write_bytes(b"new unverified cut")
        with self.assertRaisesRegex(ValueError, "verification is stale"):
            adapter.map_cut(self.project)
        self.assertEqual(status["sha256"], content_hash(self.cut_transcript))
        self.mapping.assert_called_once()

    def test_mapping_preserves_native_cut_findings_and_refuses_boundary_warnings(self):
        adapter.import_transcript(self.project, self.normalized)
        _, _, report = self.native_cut()
        self.mapping.return_value = ([], "sources", ["private recognized word"])
        with self.assertRaisesRegex(ValueError, "uncertain cut boundaries") as exc:
            adapter.map_cut(self.project)
        self.assertNotIn("private recognized word", str(exc.exception))
        blocked = adapter.read_object(report)
        blocked["flags"] = [{"code": "DURATION"}]
        self.write(report, blocked)
        with self.assertRaisesRegex(ValueError, "media or timeline findings"):
            adapter.map_cut(self.project)
        self.assertFalse(self.cut_transcript.exists())

    def test_report_before_source_import_requires_native_recheck(self):
        _, _, report = self.native_cut()
        adapter.import_transcript(self.project, self.normalized)
        os.utime(report, (1, 1))
        with self.assertRaisesRegex(ValueError, "after importing the source transcript"):
            adapter.map_cut(self.project)
        self.mapping.assert_not_called()

    def test_rejects_unrecognized_engine_version_before_loading_helpers(self):
        root = self.root / "engine"
        root.mkdir()
        (self.root / "VERSION").write_text("1.1.1\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "requires a trusted Editonny 1.1.0"):
            adapter.configure_engine(root)


if __name__ == "__main__":
    unittest.main()
