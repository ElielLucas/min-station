#!/usr/bin/env python3
"""Mutate four AS13 guards and AS14 N08 in a disposable source checkout.

Acceptance requires an assertion from the intended, deliberately fault-injecting
unit test (not an incidental import, syntax, or environment failure).
This does NOT alter the user's checkout or prior independent validation logs.
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
CUTS = ROOT / 'experiments' / 'cuts'
FILES = (
    'experiments/cuts/verify_as13_foundations.py',
    'experiments/cuts/test_as13_as15_guards.py',
    'experiments/cuts/test_h2_oracle.py',
    'experiments/cuts/h2_oracle.py',
    'experiments/cuts/h2_oracle_cache.py',
    'experiments/cuts/h2_oracle_schema.py',
    'experiments/cuts/independent_validator.py',
    'experiments/cuts/cuts.py',
    'experiments/structural/hb.py',
    'experiments/structural/io_instancia.py',
    'experiments/alternative-formulations/as02_model_a.py',
)
H2 = 'if sum(coefs.get(v, 0) for v in C) < rhs:'
PARTIAL = 'if sum(pcoefs.get(w, 0) for w in C) < prhs:'
PROJECTION = 'if projections != {frozenset(P) for P in patterns}:'
CORRUPT_G = 'coefs = {v: 1 if v in B else 2 for v in R}'

# (name, filename, source substitutions, exact test, required failure text)
MUTANTS = (
    ('AS13_H2_GUARD_REMOVED', 'verify_as13_foundations.py',
     ((H2, 'if False and sum(coefs.get(v, 0) for v in C) < rhs:'),),
     'test_as13_as15_guards.AS13AS15EntryGuards.test_as15_entry_invalid_full_h2_must_be_rejected',
     'AssertionError: AssertionError not raised'),
    ('AS13_H2_PARTIAL_GUARD_REMOVED', 'verify_as13_foundations.py',
     ((PARTIAL, 'if False and sum(pcoefs.get(w, 0) for w in C) < prhs:'),),
     'test_as13_as15_guards.AS13AS15EntryGuards.test_as15_entry_invalid_partial_h2_must_be_rejected',
     'AssertionError: AssertionError not raised'),
    ('AS13_HL_IDENTITY_GUARD_REMOVED', 'verify_as13_foundations.py',
     ((PROJECTION, 'if False and projections != {frozenset(P) for P in patterns}:'),),
     'test_as13_as15_guards.AS13AS15EntryGuards.test_as15_entry_hl_projection_identity_not_redundant_with_beta',
     'AssertionError: AssertionError not raised'),
    ('AS13_H2_BAD_G_PLUS_GUARD_REMOVED', 'verify_as13_foundations.py',
     ((H2, 'if False and sum(coefs.get(v, 0) for v in C) < rhs:'),
      (CORRUPT_G,
       'coefs = {v: (1 if partial_insufficient is None else '
       '(1 if v in B else 2)) for v in R}')),
     'test_as13_as15_guards.AS13AS15EntryGuards.test_as15_entry_invalid_full_h2_must_be_rejected',
     'AssertionError: AssertionError not raised'),
    ('N08_AS14_FINGERPRINT_OMITS_T', 'h2_oracle.py',
     (("'T': [row(x) for x in order_vertices(self.T)],", "'T': [],"),),
     'test_h2_oracle.AS14OracleTests.test_as15_entry_t_only_change_cannot_reuse_viable_cache',
     "AssertionError: <Status.VIABLE: 'VIABLE'> != <Status.INFEASIBLE: 'INFEASIBLE'>"),
)


def run_test(root: Path, test: str):
    env = {**os.environ, 'PYTHONPATH': str(root / 'experiments/cuts')}
    return subprocess.run(
        [sys.executable, '-m', 'unittest', test, '-v'],
        cwd=root, env=env, capture_output=True, text=True,
        timeout=40, check=False)


def verify():
    results = []
    with tempfile.TemporaryDirectory(prefix='as15-entry-mutants-') as temp:
        root = Path(temp) / 'min-station'
        for rel in FILES:
            dest = root / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / rel, dest)
        for name, filename, substitutions, test, signature in MUTANTS:
            target = root / 'experiments/cuts' / filename
            original = target.read_text(encoding='utf-8')
            baseline = run_test(root, test)
            if baseline.returncode != 0:
                raise AssertionError(f'{name}: baseline failed: {baseline.stderr[-1200:]}')
            mutated = original
            for before, after in substitutions:
                if mutated.count(before) != 1:
                    raise AssertionError(f'{name}: missing/non-unique source anchor: {before}')
                mutated = mutated.replace(before, after, 1)
            target.write_text(mutated, encoding='utf-8')
            try:
                proc = run_test(root, test)
            finally:
                target.write_text(original, encoding='utf-8')
            output = proc.stdout + proc.stderr
            # Inspect the assertion emitted by unittest, not an expected-error
            # string that might merely be echoed in traceback source lines.
            assertion_lines = [line.strip() for line in output.splitlines()
                               if line.startswith('AssertionError:')]
            method = test.rsplit('.', 1)[-1]
            expected_failure = f'FAIL: {method} ('
            killed = (proc.returncode != 0
                      and expected_failure in output
                      and 'Ran 1 test' in output
                      and 'FAILED (failures=1)' in output
                      and len(assertion_lines) == 1
                      and assertion_lines[0] == signature
                      and 'ModuleNotFoundError' not in output
                      and 'SyntaxError' not in output)
            results.append({
                'name': name, 'killed': killed,
                'targeted_test': test,
                'failure_signature': assertion_lines[0] if assertion_lines else 'MISSING',
            })
            if not killed:
                raise AssertionError(f'{name} survived or failed for wrong reason: {output[-1800:]}')
    return {'schema': 'AS15-ENTRY-MUTATION-v1', 'injected': len(results),
            'killed': sum(item['killed'] for item in results),
            'survived': sum(not item['killed'] for item in results),
            'mutants': results, 'workspace_modified': False,
            'scientific_gate': 'PENDING_EXTERNAL_REVIEW'}


if __name__ == '__main__':
    print(json.dumps(verify(), ensure_ascii=False, indent=2))
