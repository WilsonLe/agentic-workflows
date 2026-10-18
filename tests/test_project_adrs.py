from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'plugins/agentic-workflows/skills/standard-development-workflow'
SCRIPT = SKILL / 'scripts/project_adrs.py'
spec = importlib.util.spec_from_file_location('project_adrs', SCRIPT)
adr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adr)


def record(identifier='0001', title='Use project-owned decisions', status='accepted',
           supersedes='none', replaced_by='none'):
    return f'''# ADR-{identifier}: {title}

- Status: {status}
- Date: 2026-10-18
- Owner: Project maintainer
- Evidence: User authorized this design in https://example.org/issues/1
- Supersedes: {supersedes}
- Superseded by: {replaced_by}

## Context

Each repository needs durable rationale.

## Decision

Keep decisions in this project and maintain them during development.

## Alternatives

A global registry loses the repository's authority boundary.

## Consequences

Changes to architecture include the affected decision history in review.

## Revisit

Reconsider when independently governed projects share one repository.
'''


class ProjectAdrTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.store = self.root / 'docs/adr'
        self.cli('init')

    def cli(self, command, *arguments, success=True):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), command, '--project-root', str(self.root), *arguments],
            capture_output=True, text=True,
        )
        if success:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout)
        return result

    def write(self, identifier='0001', **kwargs):
        path = self.store / f'{identifier}-decision.md'
        path.write_text(record(identifier=identifier, **kwargs))
        return path

    def test_project_lifecycle_through_cli_and_read_only_check(self):
        self.cli('new', '--title', 'Use project-owned decisions', '--date', '2026-10-18')
        proposal = self.store / '0001-use-project-owned-decisions.md'
        self.assertIn('- Status: proposed', proposal.read_text())
        self.assertIn('without placeholders', self.cli('check', success=False).stderr)
        proposal.write_text(record(status='proposed'))
        self.assertIn('stale ADR index', self.cli('check', success=False).stderr)
        self.cli('refresh')
        before = {path.name: (path.read_bytes(), path.stat().st_mtime_ns) for path in self.store.iterdir()}
        self.cli('check')
        self.assertEqual(before, {path.name: (path.read_bytes(), path.stat().st_mtime_ns) for path in self.store.iterdir()})
        self.assertIn('| [ADR-0001](0001-use-project-owned-decisions.md) | Use project-owned decisions | proposed | 2026-10-18 |', (self.store / 'README.md').read_text())
        self.cli('init')
        self.cli('refresh')
        self.assertEqual(before['README.md'][0], (self.store / 'README.md').read_bytes())
        self.cli('new', '--title', 'Choose a new boundary', '--date', '2026-10-18')
        self.assertTrue((self.store / '0002-choose-a-new-boundary.md').is_file())

    def test_supersession_chain_and_retired_records_stay_indexed(self):
        self.write(status='superseded', replaced_by='0002')
        self.write('0002', status='superseded', supersedes='0001', replaced_by='0003')
        self.write('0003', status='deprecated', supersedes='0002')
        self.write('0004', status='rejected')
        self.cli('refresh')
        self.cli('check')
        text = (self.store / 'README.md').read_text()
        self.assertIn('| superseded |', text)
        self.assertIn('| deprecated |', text)
        self.assertIn('| rejected |', text)
        self.assertEqual(text.count('| [ADR-'), 4)

    def test_broken_graphs_fail_without_replacing_index(self):
        cases = [
            [('0001', dict(supersedes='0009'))],
            [('0001', dict(supersedes='0001'))],
            [('0001', dict(status='superseded'))],
            [('0001', dict(replaced_by='0002')), ('0002', {})],
            [('0001', dict(status='superseded', replaced_by='0002')), ('0002', {})],
            [('0001', dict(status='superseded', replaced_by='0002')), ('0002', dict(status='proposed', supersedes='0001'))],
            [('0001', dict(status='superseded', supersedes='0002', replaced_by='0002')),
             ('0002', dict(status='superseded', supersedes='0001', replaced_by='0001'))],
            [('0001', dict(status='superseded', replaced_by='0002, 0003')), ('0002', {}), ('0003', {})],
        ]
        original = (self.store / 'README.md').read_bytes()
        for case in cases:
            with self.subTest(case=case):
                for path in self.store.glob('*-decision.md'):
                    path.unlink()
                for identifier, kwargs in case:
                    self.write(identifier, **kwargs)
                self.cli('refresh', success=False)
                self.assertEqual((self.store / 'README.md').read_bytes(), original)

    def test_invalid_records_reject_placeholders_dates_fields_and_ids(self):
        valid = record()
        for text in (
            valid.replace('- Status: accepted', '- Status: implemented'),
            valid.replace('- Date: 2026-10-18', '- Date: 2026-02-30'),
            valid.replace('- Owner: Project maintainer\n', ''),
            valid.replace('- Owner: Project maintainer', '- Owner: A\n- Owner: B'),
            valid.replace('## Revisit', '## Missing'),
            valid.replace('Each repository needs durable rationale.', 'TODO'),
            valid.replace('Each repository needs durable rationale.', ''),
            valid.replace('- Supersedes: none', '- Supersedes: 0002, 0002'),
            valid.replace('ADR-0001:', 'ADR-0009:'),
        ):
            with self.subTest(text=text):
                (self.store / '0001-decision.md').write_text(text)
                self.cli('check', success=False)
        self.write()
        (self.store / '0001-other.md').write_text(valid)
        self.assertIn('duplicate ADR ID', self.cli('check', success=False).stderr)
        (self.store / '0001-other.md').unlink()
        (self.store / '00001-other.md').write_text(record(identifier='00001'))
        self.cli('check', success=False)

    def test_existing_convention_is_preserved(self):
        other = self.root / 'existing'
        other.mkdir()
        index = other / 'README.md'
        index.write_text('Our established ADR index\n')
        for command in ('init', 'refresh', 'check'):
            self.cli(command, '--directory', 'existing', success=False)
        self.assertEqual(index.read_text(), 'Our established ADR index\n')

    def test_paths_symlinks_and_interrupted_writer_fail_safely(self):
        for directory in ('../escape', str(self.root / 'absolute'), '.'):
            self.cli('init', '--directory', directory, success=False)
        outside = self.root / 'outside'
        outside.mkdir()
        (self.root / 'linked').symlink_to(outside, target_is_directory=True)
        self.cli('init', '--directory', 'linked/adr', success=False)
        self.assertEqual(list(outside.iterdir()), [])
        target = outside / 'sentinel.md'
        target.write_text('preserve me')
        (self.store / '0001-linked.md').symlink_to(target)
        self.cli('refresh', success=False)
        (self.store / '0001-linked.md').unlink()
        index = self.store / 'README.md'
        index.unlink()
        index.symlink_to(target)
        self.cli('refresh', success=False)
        self.assertEqual(target.read_text(), 'preserve me')
        index.unlink()
        self.cli('init')
        with adr.writer(self.store):
            self.cli('new', '--title', 'Another decision', '--date', '2026-10-18', success=False)
        self.assertEqual(list(self.store.glob('000*.md')), [])
        temporary = self.store / '.project-adrs-index.tmp'
        temporary.write_text('interrupted output')
        self.cli('refresh', success=False)
        self.assertEqual(temporary.read_text(), 'interrupted output')
        self.assertFalse((self.store / '.project-adrs-lock').exists())

    def test_custom_project_boundary_and_title_validation(self):
        self.cli('init', '--directory', 'applications/api/adr')
        self.cli('new', '--directory', 'applications/api/adr', '--title', 'API boundary', '--date', '2026-10-18')
        self.assertTrue((self.root / 'applications/api/adr/0001-api-boundary.md').is_file())
        self.assertEqual(list(self.store.glob('000*.md')), [])
        for title in (' ', 'Bad\nheading', 'Table | injection', 'TBD'):
            self.cli('new', '--title', title, '--date', '2026-10-18', success=False)
        self.cli('new', '--title', 'Valid title', success=False)
        self.cli('new', '--title', 'Valid title', '--date', '20261018', success=False)
        self.assertEqual(list(self.store.glob('000*.md')), [])

    def test_repository_adoption_and_workflow_consumers(self):
        result = subprocess.run([sys.executable, str(SCRIPT), 'check', '--project-root', str(ROOT)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        consumers = [
            SKILL / 'SKILL.md', SKILL / 'references/stage-contracts.md',
            SKILL / 'references/documentation-impact.md',
            SKILL.parent / 'engineering-intake/SKILL.md',
            SKILL.parent / 'engineering-exploration/SKILL.md',
            SKILL.parent / 'engineering-review/references/review-checklist.md',
        ]
        for path in consumers:
            self.assertIn('project-adrs.md', path.read_text(), str(path))
        self.assertIn('docs/adr/README.md', (ROOT / 'AGENTS.md').read_text())


if __name__ == '__main__':
    unittest.main()
