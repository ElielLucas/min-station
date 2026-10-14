#!/usr/bin/env python3
"""AS13 R2: adversarial source mutations in isolated temporary checkouts.

Unlike mocks, this changes one exact statement in a COPY of the verifier and
runs a real unittest process. Never edits the active checkout or previous
validation.md. Nonzero from each mutant is necessary but not sufficient:
assert that the failure is an AssertionError from the intended test gate.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FILES = (
    'experiments/cuts/verify_as13_foundations.py',
    'experiments/cuts/test_as13_foundations.py',
    'experiments/cuts/cuts.py',
    'experiments/cuts/independent_validator.py',
    'experiments/cuts/verify_as13_delivery.py',
    'experiments/structural/hb.py',
    'experiments/structural/io_instancia.py',
    'experiments/alternative-formulations/as02_model_a.py',
)
MUTANTS = (
    ('N2', 'for i, (S, T, V, adj, r) in enumerate(controls):',
     'for i, (S, T, V, adj, r) in []:',
     'test_as13_r2_exhaustive_cuts_rejects_one_false_classification'),
    ('N3', 'for name, case in cases:', 'for name, case in []:',
     'test_as13_r2_oracle_hb_k4_rejects_one_false_classification'),
    ('N4', 'for i, case in enumerate(controls):', 'for i, case in []:',
     'test_as13_r2_control_oracle_rejects_one_false_classification'),
    ('N5', 'for rm in range(total):', 'for rm in []:',
     'test_as13_r2_k4_all_h2_supports_reject_one_false_classification'),
    ('N7', 'beta = hl_beta_from_patterns(patterns, alpha)', 'beta = 0',
     'test_as13_r2_hl_beta_is_positive_and_checked_independently'),
)


def validate():
    outcomes = []
    with tempfile.TemporaryDirectory(prefix='as13-r2-source-mutants-') as tmp:
        folder = Path(tmp) / 'min-station'
        for rel in FILES:
            dest = folder / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / rel, dest)
        target = folder / FILES[0]
        original = target.read_text(encoding='utf-8')
        env = {**os.environ, 'PYTHONPATH': str(folder / 'experiments/cuts')}
        for name, old, new, test_name in MUTANTS:
            if original.count(old) != 1:
                raise AssertionError(f'{name}: mutation anchor is not unique')
            target.write_text(original.replace(old, new, 1), encoding='utf-8')
            # A fresh Python process prevents cross-mutant import caching.
            proc = subprocess.run(
                [sys.executable, '-m', 'unittest',
                 f'test_as13_foundations.AS13Foundations.{test_name}'],
                cwd=folder, env=env, text=True, capture_output=True,
                timeout=90, check=False)
            target.write_text(original, encoding='utf-8')
            output = proc.stdout + '\n' + proc.stderr
            killed = proc.returncode != 0 and 'AssertionError' in output
            outcomes.append({'mutant': name, 'test': test_name,
                             'killed': killed,
                             'failure_signature': next(
                                 (x.strip() for x in output.splitlines()
                                  if x.strip().startswith('AssertionError:')), 'MISSING')})
            if not killed:
                raise AssertionError(f'{name}: survived source mutation; {output[-2000:]}')
    return {'schema': 'AS13-SOURCE-MUTATION-v3',
            'mutants': outcomes,
            'injected': len(outcomes),
            'killed': sum(x['killed'] for x in outcomes),
            'survived': sum(not x['killed'] for x in outcomes),
            'workspace_modified': False,
            'gate': 'PENDING_INDEPENDENT_REVIEW_AS14_BLOCKED'}


if __name__ == '__main__':
    print(json.dumps(validate(), ensure_ascii=False, indent=2, sort_keys=True))
