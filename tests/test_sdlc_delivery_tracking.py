"""Regression coverage for mandatory many-to-many SDLC issue/PR tracking."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator

from tests.test_standard_workflow_records import task_run, workflow

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'plugins/agentic-workflows/skills/standard-development-workflow'


class DeliveryTrackingTests(unittest.TestCase):
    def assert_invalid(self, record, message):
        with self.assertRaisesRegex(workflow.RecordError, message):
            workflow.validate_record(record, require_final=True)

    def test_completed_and_final_delivery_cannot_omit_tracking(self):
        record = task_run()
        del record['delivery_tracking']
        for final in (False, True):
            with self.subTest(final=final), self.assertRaisesRegex(
                workflow.RecordError, 'delivery_tracking is required'
            ):
                workflow.validate_record(record, require_final=final)
        record['status'] = 'planned'
        workflow.validate_record(record)  # Retained planning records can be inspected.
        self.assert_invalid(record, 'delivery_tracking is required')
        record['status'] = 'running'
        with self.assertRaisesRegex(workflow.RecordError, 'delivery_tracking is required'):
            workflow.validate_record(record)

    def test_issue_required_before_execution_pr_required_at_delivery(self):
        record = task_run()
        record['status'] = 'running'
        tracking = record['delivery_tracking']
        tracking['pull_requests'] = []
        tracking['links'] = []
        workflow.validate_record(record)
        self.assert_invalid(record, 'at least one tracking issue and one PR')
        record['status'] = 'completed'
        with self.assertRaisesRegex(workflow.RecordError, 'at least one tracking issue and one PR'):
            workflow.validate_record(record)
        tracking['issues'] = []
        self.assert_invalid(record, 'primary tracking issue')

    def test_orphan_issue_and_orphan_pr_block_delivery(self):
        for side in ('issues', 'pull_requests'):
            record = task_run()
            item = copy.deepcopy(record['delivery_tracking'][side][0])
            item['url'] = item['url'].rsplit('/', 1)[0] + '/3'
            record['delivery_tracking'][side].append(item)
            with self.subTest(side=side):
                self.assert_invalid(record, 'must link at least one PR' if side == 'issues'
                                    else 'must link a tracking issue')

    def test_many_to_many_graph_is_valid(self):
        record = task_run()
        tracking = record['delivery_tracking']
        issue = copy.deepcopy(tracking['issues'][0])
        issue['url'] = issue['url'].rsplit('/', 1)[0] + '/3'
        tracking['issues'].append(issue)
        pr = copy.deepcopy(tracking['pull_requests'][0])
        pr['url'] = pr['url'].rsplit('/', 1)[0] + '/4'
        tracking['pull_requests'].append(pr)
        tracking['links'] = [
            {'issue_url': issue['url'], 'pr_url': pr['url'], 'readback_ref': 'live-link-readback'}
            for issue in tracking['issues'] for pr in tracking['pull_requests']
        ]
        workflow.validate_record(record, require_final=True)
        # A non-complete bipartite graph is also valid when every node is covered.
        tracking['links'].pop()
        workflow.validate_record(record, require_final=True)

    def test_duplicates_unknown_nodes_and_missing_readbacks_fail(self):
        for side in ('issues', 'pull_requests', 'links'):
            record = task_run()
            record['delivery_tracking'][side].append(
                copy.deepcopy(record['delivery_tracking'][side][0])
            )
            with self.subTest(duplicate=side):
                self.assert_invalid(record, 'duplicate delivery_tracking')
            record = task_run()
            record['delivery_tracking'][side][0]['readback_ref'] = ''
            with self.subTest(readback=side):
                self.assert_invalid(record, 'readback_ref')
        record = task_run()
        record['delivery_tracking']['links'][0]['pr_url'] = (
            'https://github.com/example/repository/pull/99'
        )
        self.assert_invalid(record, 'unlisted issue or PR')

    def test_primary_issue_and_repository_must_match(self):
        record = task_run()
        record['task']['issue'] = 'https://github.com/example/repository/issues/99'
        record['task']['planning_mode'] = 'legacy'
        self.assert_invalid(record, 'primary tracking issue')
        for url in ('https://github.com/other/repository/pull/2',
                    'https://elsewhere.invalid/example/repository/pull/2',
                    'https://github.com/example/repository/pull/0',
                    'https://github.com/example/repository/issues/2',
                    'https://github.com/example/repository/pull/2?fake=1'):
            record = task_run()
            record['delivery_tracking']['pull_requests'][0]['url'] = url
            with self.subTest(url=url):
                self.assert_invalid(record, 'same-repository pull item')

    def test_ready_handoff_must_be_in_tracking_with_matching_identity(self):
        from tests.test_workflow_efficiencies import pr_handoff
        record = task_run()
        record['pr_handoff'] = pr_handoff()
        workflow.validate_record(record, require_final=True)
        for field, value in (('head_revision', 'b' * 40), ('base_branch', 'other'),
                             ('state', 'merged')):
            changed = copy.deepcopy(record)
            changed['delivery_tracking']['pull_requests'][0][field] = value
            with self.subTest(field=field):
                self.assert_invalid(changed, 'identity differs')
        record['pr_handoff']['pr_url'] = 'https://github.com/example/repository/pull/99'
        self.assert_invalid(record, 'handoff is missing')
        record = task_run()
        record['pr_handoff'] = pr_handoff()
        record['status'] = 'planned'
        del record['delivery_tracking']
        with self.assertRaisesRegex(workflow.RecordError, 'delivery_tracking is required'):
            workflow.validate_record(record)

    def test_blocked_run_preserves_unpaired_issue_without_claiming_completion(self):
        record = task_run()
        record['delivery_tracking']['pull_requests'] = []
        record['delivery_tracking']['links'] = []
        record['status'] = 'blocked'
        workflow.validate_record(record, require_final=True)
        record['status'] = 'completed'
        self.assert_invalid(record, 'at least one tracking issue and one PR')

    def test_schema_requires_tracking_for_executing_records(self):
        schema = json.loads((SKILL / 'schemas/standard-workflow-v1.schema.json').read_text())
        validator = Draft202012Validator(schema)
        record = task_run()
        validator.validate(record)
        del record['delivery_tracking']
        self.assertTrue(list(validator.iter_errors(record)))
        record['status'] = 'planned'
        validator.validate(record)


if __name__ == '__main__':
    unittest.main()
