from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "plugins/trend-to-product/scripts/trend_to_product.py"
SPEC = importlib.util.spec_from_file_location("trend_to_product_tests", HELPER)
assert SPEC is not None and SPEC.loader is not None
trend = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(trend)


def record(kind: str, **values: object) -> dict[str, object]:
    return {"schema_version": 1, "record_type": kind, "limitations": [], **values}


class TrendToProductTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.project = Path(self.temporary.name) / "shop"
        self.project.mkdir()
        trend.project_init(
            Namespace(
                project=str(self.project),
                artifact_root="artifacts/trend-to-product",
                git_policy="mixed",
            )
        )
        self.artifact = self.project / "artifacts/trend-to-product"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write(self, name: str, payload: object) -> Path:
        path = Path(self.temporary.name) / name
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def test_custom_artifact_root_and_escape_rejection(self) -> None:
        other = Path(self.temporary.name) / "other"
        other.mkdir()
        result = trend.project_init(
            Namespace(project=str(other), artifact_root="research/trends", git_policy="tracked")
        )
        self.assertEqual(Path(result["artifact_root"]), (other / "research/trends").resolve())
        escape_project = Path(self.temporary.name) / "escape-project"
        escape_project.mkdir()
        with self.assertRaisesRegex(trend.TrendError, "project-relative"):
            trend.project_init(
                Namespace(project=str(escape_project), artifact_root="../escape", git_policy="mixed")
            )

    def test_audience_revision_is_immutable(self) -> None:
        audience = record(
            "audience",
            audience_id="vn-hcm-18-28",
            market="VN",
            city="Ho Chi Minh City",
            age_range=[18, 28],
            languages=["vi"],
        )
        path = self.write("audience.json", audience)
        first = trend.audience_create(Namespace(project=str(self.project), input=str(path)))
        second = trend.audience_create(
            Namespace(project=str(self.project), input=str(path)), revision=True
        )
        self.assertEqual((first["revision"], second["revision"]), (1, 2))
        self.assertTrue((self.artifact / "audiences/vn-hcm-18-28/revisions/0001.json").is_file())

    def configure_source(self) -> None:
        source = record(
            "source",
            source_id="fixture-rss",
            source_class="editorial_rss",
            adapter_type="fixture",
            auth_mode="none",
            credential_ref=None,
            permitted_operations=["read"],
            markets=["VN"],
            languages=["vi"],
            coverage_notes="National editorial attention only",
        )
        path = self.write("source.json", source)
        trend.source_write(Namespace(project=str(self.project), input=str(path)))

    def test_source_requires_enable_and_deduplicates_import(self) -> None:
        self.configure_source()
        imported = [
            {"source_item_id": "same", "summary": "One", "metric": 0.8},
            {"source_item_id": "same", "summary": "Syndicated", "metric": 0.8},
        ]
        path = self.write("import.json", imported)
        args = Namespace(
            project=str(self.project), source_id="fixture-rss",
            input=str(path), observed_at="2026-07-30T00:00:00Z",
        )
        with self.assertRaisesRegex(trend.TrendError, "enabled"):
            trend.source_import(args)
        trend.source_state(
            Namespace(project=str(self.project), source_id="fixture-rss"), "ready"
        )
        result = trend.source_import(args)
        self.assertEqual(result["accepted"], 1)
        self.assertEqual(result["records"][0]["region_status"], "unknown")

    def configure_audience_tracking(self) -> None:
        audience = record("audience", audience_id="vn-hcm-18-28")
        path = self.write("audience-min.json", audience)
        trend.audience_create(Namespace(project=str(self.project), input=str(path)))
        trend.tracking_create(
            Namespace(
                project=str(self.project),
                tracking_id="hcm-daily",
                audience_id="vn-hcm-18-28",
                cadence="P1D",
            )
        )

    def run_input(self) -> dict[str, object]:
        evidence = record(
            "evidence",
            evidence_id="ev-one",
            source_id="fixture-rss",
            observed_at="2026-07-30T00:00:00Z",
            signal_type="editorial_attention",
            metrics=[{
                "name": "mentions", "value": 3, "unit": "articles",
                "window": "P1D", "measurement_type": "observed",
            }],
        )
        score_inputs = {
            "momentum": 1, "cross_platform_spread": 0.5, "target_relevance": 0.5,
            "remixability": 1, "product_visual_suitability": 1,
            "shopping_intent": 0.5, "competition_gap": 0.5,
            "useful_lifespan": 1, "evidence_quality": 1,
        }
        fit_inputs = {
            "audience_resonance": 1, "recognizability": 1, "product_context": 1,
            "commercial_gap": 0.5, "margin": 1, "manufacturability": 1,
            "speed": 1, "extensibility": 1, "testability": 1,
        }
        return {
            "limitations": ["National evidence does not establish city prevalence"],
            "evidence": [evidence],
            "trends": [{"trend_id": "trend-one", "score_inputs": score_inputs}],
            "opportunities": [{
                "opportunity_id": "opp-one", "score_inputs": fit_inputs,
                "hard_gates": {
                    "rights": True, "likeness": True, "sensitive_topic": True,
                    "known_margin": True, "manufacturable": True, "fulfilment": True,
                },
            }],
            "concepts": [{"concept_id": "concept-one"}],
        }

    def test_run_scoring_manifest_and_tamper_detection(self) -> None:
        self.configure_audience_tracking()
        path = self.write("run.json", self.run_input())
        result = trend.run_create(
            Namespace(
                project=str(self.project), tracking_id="hcm-daily",
                input=str(path), run_id="fixture-run", trigger_type="manual",
            )
        )
        run = Path(result["path"])
        self.assertEqual(json.loads((run / "trends.json").read_text())[0]["score"], 78)
        self.assertEqual(trend.verify_directory(run)["status"], "verified")
        (run / "concepts.json").write_text("[]\n", encoding="utf-8")
        with self.assertRaisesRegex(trend.TrendError, "digest mismatch"):
            trend.verify_directory(run)

    def test_tracking_is_configured_until_bound(self) -> None:
        self.configure_audience_tracking()
        path = self.artifact / "tracking/hcm-daily.json"
        self.assertEqual(json.loads(path.read_text())["status"], "configured")
        bound = trend.tracking_bind(
            Namespace(
                project=str(self.project),
                tracking_id="hcm-daily",
                scheduler_id="automation-external-123",
            )
        )
        self.assertEqual(bound["status"], "active")

    def test_design_requires_approved_brief_and_preserves_lineage(self) -> None:
        self.configure_audience_tracking()
        run_path = self.write("run-design.json", self.run_input())
        trend.run_create(
            Namespace(
                project=str(self.project), tracking_id="hcm-daily",
                input=str(run_path), run_id="design-run", trigger_type="manual",
            )
        )
        brief = record(
            "design_brief",
            concept_id="concept-one",
            opportunity_id="opp-one",
            approval_status="draft",
            design_revision=1,
        )
        brief_path = self.write("brief.json", brief)
        args = Namespace(project=str(self.project), run_id="design-run", input=str(brief_path))
        with self.assertRaisesRegex(trend.TrendError, "approved"):
            trend.design_brief(args)
        brief["approval_status"] = "approved"
        brief_path.write_text(json.dumps(brief), encoding="utf-8")
        result = trend.design_brief(args)
        readiness = json.loads(
            (Path(result["path"]) / "production-readiness.json").read_text()
        )
        self.assertEqual(readiness["status"], "concept_only")

    def test_secret_and_session_fields_are_rejected(self) -> None:
        with self.assertRaisesRegex(trend.TrendError, "prohibited field"):
            trend.validate_record(record("source", source_id="bad", access_token="secret"))


if __name__ == "__main__":
    unittest.main()
