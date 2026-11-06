"""Regression coverage for mandatory many-to-many SDLC issue/PR tracking."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from jsonschema import Draft202012Validator

from tests.test_standard_workflow_records import pr_handoff, task_run, workflow

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
        del record['pr_handoff']  # Retained records have not claimed a ready handoff.
        workflow.validate_record(record)  # Retained planning records can be inspected.
        self.assert_invalid(record, 'delivery_tracking is required')
        record['status'] = 'running'
        with self.assertRaisesRegex(workflow.RecordError, 'delivery_tracking is required'):
            workflow.validate_record(record)

    def test_issue_required_before_execution_pr_required_at_delivery(self):
        record = task_run()
        record['status'] = 'running'
        del record['pr_handoff']
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
        record['pr_handoff'].update(state='blocked', blocker='GitHub permission denied',
                                    preserved_work_ref='feature at commit-a')
        workflow.validate_record(record, require_final=True)
        record['status'] = 'completed'
        self.assert_invalid(record, 'blocked PR handoff requires blocked task status')

    def test_schema_requires_tracking_for_executing_records(self):
        schema = json.loads((SKILL / 'schemas/standard-workflow-v1.schema.json').read_text())
        validator = Draft202012Validator(schema)
        record = task_run()
        validator.validate(record)
        del record['delivery_tracking']
        self.assertTrue(list(validator.iter_errors(record)))
        record['status'] = 'planned'
        validator.validate(record)

    def test_local_success_cannot_complete_a_pending_handoff(self):
        # Code, docs, configuration and generated artifacts all need delivery.
        for path in ('src/app.py', 'README.md', '.github/workflows/ci.yml', 'dist/app.zip'):
            for state in ('pending', 'not_applicable'):
                handoff = pr_handoff()
                handoff.update(changed_paths=[path], state=state, pr_url='',
                               pr_head_revision='', readback_ref='', review_state='approved')
                with self.subTest(path=path, state=state), self.assertRaisesRegex(
                    workflow.RecordError, 'lacks a reviewable PR handoff'
                ):
                    # Completion must enforce the gate even without --require-final.
                    workflow.validate_pr_handoff(
                        handoff, task_status='completed', require_final=False,
                    )

    def test_pending_review_cannot_count_as_completed_delivery(self):
        for final in (False, True):
            handoff = pr_handoff()
            handoff['review_state'] = 'pending'
            with self.subTest(final=final), self.assertRaisesRegex(
                workflow.RecordError, 'independent review is incomplete'
            ):
                workflow.validate_pr_handoff(
                    handoff, task_status='completed', require_final=final,
                )
        workflow.validate_pr_handoff(handoff, task_status='running', require_final=False)

    def test_completed_record_cannot_omit_the_handoff_check(self):
        record = task_run()
        del record['pr_handoff']
        for final in (False, True):
            with self.subTest(final=final), self.assertRaisesRegex(
                workflow.RecordError, 'requires pr_handoff completion evidence'
            ):
                workflow.validate_record(record, require_final=final)
        schema = json.loads((SKILL / 'schemas/standard-workflow-v1.schema.json').read_text())
        validator = Draft202012Validator(schema)
        self.assertTrue(list(validator.iter_errors(record)))
        # Retained records remain inspectable before completing delivery.
        record['status'] = 'planned'
        workflow.validate_record(record)
        validator.validate(record)

    def test_explicit_local_only_record_does_not_require_a_pr(self):
        record = task_run()
        record['pr_handoff'].update(
            explicit_local_only=True, state='not_applicable', override_ref='user-local-only',
        )
        record['delivery_tracking'].update(pull_requests=[], links=[])
        workflow.validate_record(record, require_final=True)
        record['pr_handoff']['explicit_local_only'] = False
        self.assert_invalid(record, 'lacks a reviewable PR handoff')

    def test_no_diff_record_does_not_require_an_empty_pr(self):
        record = task_run()
        record['pr_handoff'] = pr_handoff(False)
        record['delivery_tracking'].update(pull_requests=[], links=[])
        workflow.validate_record(record, require_final=True)


class HandoffCompletionCliTests(unittest.TestCase):
    def run_gate(self, handoff, *args):
        with tempfile.TemporaryDirectory() as scratch:
            path = Path(scratch) / 'handoff.json'
            path.write_text(json.dumps(handoff), encoding='utf-8')
            return subprocess.run(
                [sys.executable, str(SKILL / 'scripts/standard_workflow_record.py'),
                 'handoff-check', str(path), *args],
                capture_output=True, text=True, check=False,
            )

    def test_reviewed_pr_completes_without_a_full_task_record(self):
        handoff = pr_handoff()
        handoff['review_state'] = 'approved'
        handoff['existing_pr_url'] = handoff['pr_url']
        result = self.run_gate(handoff)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('PR handoff ready', result.stdout)

    def test_local_edits_commit_or_push_alone_do_not_complete_delivery(self):
        for milestone in ('local edits and passing tests', 'commit-a', 'origin/feature'):
            handoff = pr_handoff()
            handoff.update(state='pending', pr_url='', pr_head_revision='',
                           readback_ref='', preserved_work_ref=milestone)
            with self.subTest(milestone=milestone):
                result = self.run_gate(handoff)
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn('lacks a reviewable PR handoff', result.stderr)

    def test_stale_or_missing_live_readback_blocks_completion(self):
        for field, value, error in (
            ('pr_head_revision', 'b' * 40, 'PR head does not match'),
            ('pr_base_branch', 'other', 'PR base does not match'),
            ('readback_ref', '', 'readback_ref'),
            ('existing_pr_url', 'https://github.com/example/repository/pull/99',
             'not duplicated'),
            ('pr_url', 'https://github.com/example/repository/pull/2?fake=1',
             'pull item'),
            ('review_state', 'pending', 'independent review is incomplete'),
        ):
            handoff = pr_handoff()
            handoff['review_state'] = 'approved'
            handoff[field] = value
            with self.subTest(field=field):
                result = self.run_gate(handoff)
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn(error, result.stderr)

    def test_explicit_local_only_and_no_diff_remain_valid_exceptions(self):
        result = self.run_gate(pr_handoff(False))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('not applicable', result.stdout)
        handoff = pr_handoff()
        handoff.update(explicit_local_only=True, state='not_applicable',
                       override_ref='user explicitly requested local changes only')
        result = self.run_gate(handoff)
        self.assertEqual(result.returncode, 0, result.stderr)
        handoff['override_ref'] = ''
        result = self.run_gate(handoff)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn('override_ref', result.stderr)

    def test_blocked_report_preserves_work_and_never_returns_success(self):
        handoff = pr_handoff()
        handoff.update(state='blocked', blocker='GitHub permission denied',
                       preserved_work_ref='feature at commit-a')
        result = self.run_gate(handoff, '--task-status', 'blocked')
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn('PR delivery incomplete', result.stderr)
        self.assertNotIn('PR handoff ready', result.stdout)
        result = self.run_gate(handoff)  # A blocker cannot be labelled completed.
        self.assertEqual(result.returncode, 1, result.stderr)
        handoff['preserved_work_ref'] = ''
        result = self.run_gate(handoff, '--task-status', 'blocked')
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn('preserved_work_ref', result.stderr)

    def test_blocked_status_requires_an_explicit_handoff_blocker(self):
        result = self.run_gate(pr_handoff(), '--task-status', 'blocked')
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn('blocked handoff must record', result.stderr)


if __name__ == '__main__':
    unittest.main()
