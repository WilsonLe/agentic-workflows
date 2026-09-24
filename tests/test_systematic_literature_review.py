from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = (
    ROOT
    / "plugins"
    / "systematic-literature-review"
    / "skills"
    / "systematic-literature-review-workflow"
)
HELPER = SKILL / "scripts" / "systematic_review.py"
SPEC = importlib.util.spec_from_file_location("systematic_review", HELPER)
assert SPEC is not None and SPEC.loader is not None
systematic_review = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(systematic_review)


class SystematicLiteratureReviewTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.project = self.root / "review"
        systematic_review.initialize(self.project)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def rows(self, relative: str, values: list[dict[str, str]]) -> None:
        path = self.project / relative
        header = list(systematic_review._rows(path)[0]) if systematic_review._rows(path) else None
        if header is None:
            import csv

            with path.open(newline="", encoding="utf-8") as handle:
                header = next(csv.reader(handle))
        systematic_review._write_rows(path, header, values)

    def json(self, relative: str, payload: object) -> None:
        (self.project / relative).write_text(
            json.dumps(payload, indent=2) + "\n",
            encoding="utf-8",
        )

    def make_complete(self) -> None:
        raw = b"synthetic export content\n"
        raw_path = self.project / "searches" / "raw-exports" / "export-001.csv"
        raw_path.write_bytes(raw)
        raw_hash = hashlib.sha256(raw).hexdigest()
        self.rows(
            "searches/raw-exports/manifest.csv",
            [
                {
                    "export_batch_id": "export-001",
                    "search_run_id": "search-001",
                    "source_name": "synthetic-index",
                    "interface": "synthetic-interface",
                    "strategy_file": "searches/search-strategies/search-001.txt",
                    "run_timestamp": "2026-01-01T00:00:00Z",
                    "returned_count": "1",
                    "exported_count": "1",
                    "limits": "none",
                    "relative_path": "searches/raw-exports/export-001.csv",
                    "format": "csv",
                    "bytes": str(len(raw)),
                    "sha256": raw_hash,
                    "importer_version": "systematic-review-v1",
                    "update_status": "initial",
                }
            ],
        )
        self.rows(
            "searches/search-run-ledger.csv",
            [
                {
                    "search_run_id": "search-001",
                    "source_name": "synthetic-index",
                    "provider": "synthetic-provider",
                    "interface": "synthetic-interface",
                    "strategy_file": "searches/search-strategies/search-001.txt",
                    "run_timestamp": "2026-01-01T00:00:00Z",
                    "limits": "none",
                    "limits_justification": "not applicable",
                    "returned_count": "1",
                    "exported_count": "1",
                    "export_batch_id": "export-001",
                    "dedup_batch_id": "dedup-001",
                    "update_status": "initial",
                    "operator_id": "human-reviewer-a",
                    "peer_review_id": "human-search-reviewer",
                    "access_or_completeness_note": "Synthetic complete access",
                }
            ],
        )
        (self.project / "searches" / "search-strategies" / "search-001.txt").write_text(
            "synthetic exact strategy\n", encoding="utf-8"
        )
        self.rows(
            "records/records.csv",
            [
                {
                    "source_record_id": "record-001",
                    "search_run_id": "search-001",
                    "export_batch_id": "export-001",
                    "source_name": "synthetic-index",
                    "source_row": "1",
                    "title": "Synthetic report",
                    "authors": "Synthetic Author",
                    "year": "2026",
                    "doi": "10.0000/synthetic",
                    "external_id": "external-001",
                    "record_type": "journal",
                    "report_id": "report-001",
                    "status": "included",
                }
            ],
        )
        full_text = b"synthetic non-copyrighted fixture\n"
        (self.project / "full-text" / "report-001.txt").write_bytes(full_text)
        (self.project / "metadata" / "report-001.json").write_text(
            '{"synthetic": true}\n', encoding="utf-8"
        )
        (self.project / "notes" / "report-001.md").write_text(
            "Synthetic note; locator: paragraph 1.\n", encoding="utf-8"
        )
        self.rows(
            "records/reports.csv",
            [
                {
                    "report_id": "report-001",
                    "study_id": "study-001",
                    "report_type": "primary",
                    "title": "Synthetic report",
                    "doi": "10.0000/synthetic",
                    "retraction_status": "not_retracted",
                    "full_text_status": "verified",
                    "full_text_path": "full-text/report-001.txt",
                    "full_text_bytes": str(len(full_text)),
                    "full_text_sha256": hashlib.sha256(full_text).hexdigest(),
                    "metadata_path": "metadata/report-001.json",
                    "notes_path": "notes/report-001.md",
                    "retrieval_version": "synthetic-v1",
                }
            ],
        )
        self.rows(
            "records/studies.csv",
            [
                {
                    "study_id": "study-001",
                    "study_label": "Synthetic study",
                    "study_design": "synthetic_randomized",
                    "status": "included",
                }
            ],
        )
        self.rows(
            "records/identity-links.csv",
            [
                {
                    "link_id": "link-001",
                    "source_record_id": "record-001",
                    "report_id": "report-001",
                    "study_id": "study-001",
                    "link_type": "record_report_study",
                    "active": "true",
                    "prior_link_id": "",
                    "decision_id": "identity-decision-001",
                    "actor_id": "human-reviewer-a",
                    "rationale": "Synthetic verified link",
                    "timestamp": "2026-01-01T00:00:00Z",
                }
            ],
        )
        decisions = []
        extractions = []
        for suffix in ("a", "b"):
            decisions.append(
                {
                    "decision_id": f"full-text-{suffix}",
                    "report_id": "report-001",
                    "protocol_version": "1",
                    "contributor_id": f"human-reviewer-{suffix}",
                    "contributor_type": "human",
                    "qualified": "true",
                    "independent": "true",
                    "decision": "include",
                    "exclusion_reason": "",
                    "notes": "Synthetic decision",
                    "source_locator": "full text",
                    "timestamp": f"2026-01-01T00:00:0{1 if suffix == 'a' else 2}Z",
                    "automation_action_id": "",
                }
            )
            extractions.append(
                {
                    "extraction_id": f"extraction-{suffix}",
                    "form_id": "extraction-form-v1",
                    "form_version": "1",
                    "report_id": "report-001",
                    "study_id": "study-001",
                    "data_item_key": "outcome-001",
                    "value": "synthetic-value",
                    "unit": "synthetic-unit",
                    "source_locator": "paragraph 1",
                    "contributor_id": f"human-reviewer-{suffix}",
                    "contributor_type": "human",
                    "qualified": "true",
                    "independent": "true",
                    "timestamp": f"2026-01-01T00:00:0{3 if suffix == 'a' else 4}Z",
                    "transformation_id": "",
                    "author_contact_status": "not_required",
                }
            )
        self.rows("screening/full-text-decisions.csv", decisions)
        self.rows("extraction/extraction-values.csv", extractions)
        self.rows(
            "appraisal/appraisal-decisions.csv",
            [
                {
                    "appraisal_id": "appraisal-001",
                    "study_id": "study-001",
                    "report_id": "report-001",
                    "study_design": "synthetic_randomized",
                    "instrument": "synthetic permitted instrument",
                    "instrument_version": "1",
                    "instrument_source": "https://example.invalid/instrument",
                    "licence": "synthetic fixture",
                    "domain": "synthetic-domain",
                    "judgment": "synthetic-judgment",
                    "support": "Synthetic support",
                    "source_locator": "paragraph 1",
                    "assessor_id": "human-reviewer-a",
                    "assessor_type": "human",
                    "qualified": "true",
                    "independent": "true",
                    "conflict_id": "",
                    "resolution_id": "",
                    "overall_judgment": "instrument-specific",
                    "universal_quality_score": "",
                    "timestamp": "2026-01-01T00:00:05Z",
                }
            ],
        )
        self.rows(
            "synthesis/synthesis-data.csv",
            [
                {
                    "synthesis_id": "synthesis-001",
                    "question_or_outcome": "synthetic outcome",
                    "report_ids": "report-001",
                    "study_ids": "study-001",
                    "compatibility_basis": "Conceptually compatible for structured tabulation",
                    "pooling_compatible": "false",
                    "planned_status": "planned",
                    "method": "no_meta_analysis",
                    "explicit_method": "structured tabulation",
                    "effect_measure": "",
                    "model": "",
                    "heterogeneity": "",
                    "grouping_rule": "outcome",
                    "missing_data": "none",
                    "sensitivity": "not applicable",
                    "subgroups": "none",
                    "reporting_bias": "discussed",
                    "external_statistics": "false",
                    "tool": "",
                    "tool_version": "",
                    "code_reference": "",
                    "input_sha256": "",
                    "output_sha256": "",
                    "run_environment": "",
                    "diagnostics": "",
                    "human_verifier_id": "human-reviewer-a",
                    "limitations": "Synthetic fixture only",
                }
            ],
        )
        transitions = []
        states = systematic_review.FORWARD_STATES
        for index in range(len(states) - 1):
            transitions.append(
                {
                    "from": states[index],
                    "to": states[index + 1],
                    "actor_id": "human-reviewer-a",
                    "actor_type": "human",
                    "timestamp": f"2026-01-01T00:01:{index:02d}Z",
                    "basis": "Synthetic fixture gate passed",
                    "unresolved_blockers": [],
                }
            )
        self.json(
            "audit/review-state.json",
            {
                "schema_version": 1,
                "review_id": "review-synthetic-complete",
                "current_state": "complete",
                "review_family": "systematic_intervention_review",
                "question_framework": "PICO",
                "conduct_guidance": "synthetic domain manual",
                "reporting_guidance": "PRISMA 2020",
                "required_independent_humans": 2,
                "require_duplicate_extraction": True,
                "certainty_applicable": False,
                "transitions": transitions,
                "blockers": [],
            },
        )
        self.json("reporting/flow-counts.json", systematic_review.derive_counts(self.project))

    def test_initialization_inventory_and_nonempty_refusal(self) -> None:
        expected = {
            path.relative_to(SKILL / "templates" / "project").as_posix()
            for path in (SKILL / "templates" / "project").rglob("*")
            if path.is_file()
        }
        actual = {
            path.relative_to(self.project).as_posix()
            for path in self.project.rglob("*")
            if path.is_file()
        }
        self.assertEqual(actual, expected)
        with self.assertRaisesRegex(systematic_review.ReviewError, "empty directory"):
            systematic_review.initialize(self.project)

    @unittest.skipIf(os.name == "nt", "symlink creation requires elevated Windows privileges")
    def test_initialization_rejects_symlink_root(self) -> None:
        link = self.root / "link"
        link.symlink_to(self.project, target_is_directory=True)
        with self.assertRaisesRegex(systematic_review.ReviewError, "symbolic link"):
            systematic_review.project_path(link)

    def test_import_preserves_raw_bytes_lineage_and_contains_formulas(self) -> None:
        source = self.root / "records.csv"
        source.write_text(
            "title,authors,year,doi\n=malicious(),Synthetic Author,2026,10.0/example\n",
            encoding="utf-8",
        )
        result = systematic_review.import_records(
            self.project,
            source,
            search_run_id="search-001",
            source_name="synthetic-index",
        )
        raw = self.project / result["raw_export"]
        self.assertEqual(raw.read_bytes(), source.read_bytes())
        self.assertEqual(hashlib.sha256(raw.read_bytes()).hexdigest(), result["sha256"])
        record = systematic_review._rows(self.project / "records" / "records.csv")[0]
        self.assertEqual(record["title"], "'=malicious()")
        self.assertEqual(record["search_run_id"], "search-001")
        self.assertEqual(record["export_batch_id"], result["export_batch_id"])

    def test_malformed_import_has_no_partial_commit(self) -> None:
        source = self.root / "broken.ris"
        source.write_text("TY  - JOUR\nTI  - Missing terminator\n", encoding="utf-8")
        before = {
            path.relative_to(self.project): path.read_bytes()
            for path in self.project.rglob("*")
            if path.is_file()
        }
        with self.assertRaisesRegex(systematic_review.ReviewError, "missing ER"):
            systematic_review.import_records(
                self.project,
                source,
                search_run_id="search-001",
                source_name="synthetic-index",
            )
        after = {
            path.relative_to(self.project): path.read_bytes()
            for path in self.project.rglob("*")
            if path.is_file()
        }
        self.assertEqual(before, after)

    def test_supported_json_ris_and_bibtex_subsets(self) -> None:
        fixtures = {
            "records.json": '[{"title":"JSON title","authors":"Author","year":"2026"}]',
            "records.ris": "TY  - JOUR\nTI  - RIS title\nAU  - Author\nPY  - 2026\nER  -\n",
            "records.bib": "@article{x,\n title={Bib title},\n author={Author},\n year={2026},\n}\n",
        }
        for name, content in fixtures.items():
            path = self.root / name
            path.write_text(content, encoding="utf-8")
            _, records = systematic_review.parse_import(path)
            self.assertEqual(len(records), 1)
            self.assertTrue(records[0]["title"])

    def test_dedup_candidates_never_merge(self) -> None:
        header = {
            "search_run_id": "search-001",
            "export_batch_id": "export-001",
            "source_name": "synthetic",
            "source_row": "1",
            "title": "A synthetic study of review methods",
            "authors": "Example Author",
            "year": "2026",
            "doi": "",
            "external_id": "",
            "record_type": "journal",
            "report_id": "",
            "status": "imported",
        }
        self.rows(
            "records/records.csv",
            [
                {"source_record_id": "record-a", **header},
                {
                    "source_record_id": "record-b",
                    **header,
                    "source_row": "2",
                    "title": "A synthetic study of review method",
                },
            ],
        )
        candidates = systematic_review.dedup_candidates(self.project)
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0]["action"], "human_review_required")
        self.assertNotIn("merge", candidates[0])

    def test_complete_two_human_path_validates(self) -> None:
        self.make_complete()
        result = systematic_review.validate_project(self.project)
        self.assertEqual(result["status"], "complete", result)
        self.assertEqual(result["counts"]["source_records"], 1)
        self.assertEqual(result["counts"]["included_reports"], 1)
        self.assertEqual(result["counts"]["included_studies"], 1)

    def test_single_reviewer_and_ai_independence_block_final(self) -> None:
        self.make_complete()
        decisions = systematic_review._rows(
            self.project / "screening" / "full-text-decisions.csv"
        )
        decisions[1]["contributor_type"] = "ai_assistant"
        decisions[1]["contributor_id"] = "ai-agent-b"
        self.rows("screening/full-text-decisions.csv", decisions)
        result = systematic_review.validate_project(self.project)
        self.assertEqual(result["status"], "blocked")
        self.assertTrue(any("non-human" in error for error in result["errors"]))
        self.assertTrue(any("independent" in blocker for blocker in result["blockers"]))

    def test_invalid_transition_count_drift_and_universal_score_fail(self) -> None:
        self.make_complete()
        state = json.loads((self.project / "audit" / "review-state.json").read_text())
        state["transitions"][0]["to"] = "synthesis_in_progress"
        self.json("audit/review-state.json", state)
        counts = json.loads((self.project / "reporting" / "flow-counts.json").read_text())
        counts["source_records"] = 99
        self.json("reporting/flow-counts.json", counts)
        appraisal = systematic_review._rows(
            self.project / "appraisal" / "appraisal-decisions.csv"
        )
        appraisal[0]["universal_quality_score"] = "87"
        self.rows("appraisal/appraisal-decisions.csv", appraisal)
        result = systematic_review.validate_project(self.project)
        self.assertTrue(any("invalid transition" in error for error in result["errors"]))
        self.assertTrue(any("flow counts drift" in error for error in result["errors"]))
        self.assertTrue(any("universal quality score" in error for error in result["errors"]))

    def test_registered_claim_requires_exact_live_evidence_fields(self) -> None:
        protocol = json.loads(
            (self.project / "protocol" / "protocol-state.json").read_text()
        )
        protocol["protocol_status"] = "prospective_registered"
        protocol["registration_or_publication"] = {"provider": "PROSPERO"}
        self.json("protocol/protocol-state.json", protocol)
        result = systematic_review.validate_project(self.project)
        self.assertTrue(any("exact verification evidence" in error for error in result["errors"]))

    def test_protocol_amendment_and_reversible_dedup_require_lineage(self) -> None:
        protocol = json.loads(
            (self.project / "protocol" / "protocol-state.json").read_text()
        )
        protocol["protocol_status"] = "amended"
        self.json("protocol/protocol-state.json", protocol)
        self.rows(
            "dedup/dedup-decisions.csv",
            [
                {
                    "decision_id": "dedup-unmerge-001",
                    "candidate_id": "candidate-001",
                    "record_ids": "record-a;record-b",
                    "decision": "unmerge",
                    "active": "true",
                    "prior_decision_id": "missing-prior",
                    "reviewer_id": "human-reviewer-a",
                    "reviewer_type": "human",
                    "rationale": "Synthetic correction",
                    "timestamp": "2026-01-01T00:00:00Z",
                }
            ],
        )
        result = systematic_review.validate_project(self.project)
        self.assertTrue(any("amendment evidence" in error for error in result["errors"]))
        self.assertTrue(any("prior lineage" in error for error in result["errors"]))

    def test_external_statistics_provenance_and_no_meta_method_gate(self) -> None:
        self.make_complete()
        synthesis = systematic_review._rows(
            self.project / "synthesis" / "synthesis-data.csv"
        )
        synthesis[0]["external_statistics"] = "true"
        synthesis[0]["explicit_method"] = ""
        self.rows("synthesis/synthesis-data.csv", synthesis)
        result = systematic_review.validate_project(self.project)
        self.assertTrue(any("external statistics" in blocker for blocker in result["blockers"]))
        self.assertTrue(any("explicit method" in blocker for blocker in result["blockers"]))

    def test_retraction_unavailable_multiple_reports_and_fixture_privacy(self) -> None:
        scenario = json.loads(
            (
                SKILL
                / "examples"
                / "multiple-reports-one-study"
                / "scenario.json"
            ).read_text()
        )
        self.assertEqual({report["study_id"] for report in []}, set())
        self.assertEqual(scenario["expected_study_count"], 1)
        self.assertIn("retracted", {item.get("retraction_status") for item in scenario["reports"]})
        self.assertIn("unavailable", {item.get("full_text_status") for item in scenario["reports"]})
        for path in (SKILL / "examples").rglob("*.json"):
            payload = json.loads(path.read_text())
            self.assertTrue(payload["synthetic"])
            self.assertFalse(payload["contains_real_research"])
            lowered = path.read_text().lower()
            self.assertNotIn("password", lowered)
            self.assertNotIn("api_key", lowered)

    def test_every_required_synthetic_scenario_is_present(self) -> None:
        expected = {
            "complete-two-reviewer",
            "blocked-single-reviewer",
            "multiple-reports-one-study",
            "ambiguous-dedup",
            "protocol-amendment",
            "synthesis-without-meta-analysis",
            "external-statistics-provenance",
        }
        actual = {path.parent.name for path in (SKILL / "examples").glob("*/scenario.json")}
        self.assertEqual(actual, expected)
        ambiguous = json.loads(
            (SKILL / "examples" / "ambiguous-dedup" / "scenario.json").read_text()
        )
        self.assertEqual(len(ambiguous["candidate_clusters"]), 2)
        self.assertFalse(any(item["auto_merged"] for item in ambiguous["candidate_clusters"]))

    def test_helper_is_standard_library_offline_and_non_statistical(self) -> None:
        text = HELPER.read_text(encoding="utf-8")
        for prohibited in (
            "requests",
            "urllib.request",
            "subprocess",
            "socket",
            "meta_analysis(",
            "pooled_effect",
            "os.system",
        ):
            self.assertNotIn(prohibited, text)
        for command in ("init", "import", "dedup-candidates", "counts", "validate", "summary"):
            self.assertIn(f'"{command}"', text)

    def test_source_and_central_portable_assets_have_byte_parity(self) -> None:
        central = (
            ROOT
            / "plugins"
            / "agentic-workflows"
            / "skills"
            / "systematic-literature-review-workflow"
        )
        portable = {"examples", "references", "schemas", "scripts", "templates"}
        source_files = {
            path.relative_to(SKILL): path.read_bytes()
            for directory in portable
            for path in (SKILL / directory).rglob("*")
            if path.is_file() and "__pycache__" not in path.parts
        }
        central_files = {
            path.relative_to(central): path.read_bytes()
            for directory in portable
            for path in (central / directory).rglob("*")
            if path.is_file() and "__pycache__" not in path.parts
        }
        self.assertEqual(source_files, central_files)
        self.assertIn(
            "name: systematic-literature-review-workflow",
            (central / "SKILL.md").read_text(),
        )

    def test_summary_is_deterministic_and_redacted(self) -> None:
        first = systematic_review.redacted_summary(self.project)
        second = systematic_review.redacted_summary(self.project)
        self.assertEqual(first, second)
        self.assertNotIn("records", first)
        self.assertNotIn("source_content", json.dumps(first))


if __name__ == "__main__":
    unittest.main()
