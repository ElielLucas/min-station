#!/usr/bin/env python3
"""AS15 source mutation sensor in isolated copies; no actual workspace edits."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Every injected behavioral error must break a specific spec-derived assertion.
MUTANTS = (
    ('H2_COMPLEMENT_VIABLE_GATE_REMOVED', 'h2_separator.py',
     "if base.status is Status.VIABLE:", "if base.status is Status.INFEASIBLE:",
     'test_as15_01_viable_complement_never_emits_h2', 'FAIL'),
    ('H2_BHAT_INVERSION', 'h2_separator.py',
     "if result.status is Status.INFEASIBLE:", "if result.status is Status.VIABLE:",
     'test_as15_02_03_exact_bhat_coefficients_rhs_and_physical_validity', 'FAIL'),
    ('H2_COEFFICIENTS_SWAP', 'h2_separator.py',
     "coeffs = tuple((v, 1 if v in bhat else 2) for v in R)",
     "coeffs = tuple((v, 2 if v in bhat else 1) for v in R)",
     'test_as15_02_03_exact_bhat_coefficients_rhs_and_physical_validity', 'ERROR'),
    ('H2_MASS_GATE_GT', 'h2_separator.py',
     "if proposed.mass >= 2:", "if proposed.mass > 2:",
     'test_as15_05_mass_boundary_two', 'FAIL'),
    ('H2_DEGENERATION_GATE_REMOVED', 'h2_separator.py',
     "elif cut.degenerate_cover:", "elif False and cut.degenerate_cover:",
     'test_as15_08_minimal_cover_degenerates_without_novelty', 'FAIL'),
    ('H2_PARTIAL_UNKNOWN_COEFF1', 'h2_separator.py',
     "coeffs = tuple((v, 1 if v in bhat else 2) for v in R)",
     "coeffs = tuple((v, 1 if v in bhat or v in unknown else 2) for v in R)",
     'test_as15_06_unknown_candidate_never_enters_bhat', 'ERROR'),
    ('H2_VIOLATION_TOLERANCE_INCLUSIVE', 'h2_separator.py',
     "if violation <= opt.min_violation:", "if violation < opt.min_violation:",
     'test_as15_04_exact_violation_tolerance_boundary', 'FAIL'),
)


def verify():
    required = ('h2_cut.py', 'h2_supports.py', 'h2_separator.py', 'h2_oracle.py',
                'h2_oracle_cache.py', 'h2_oracle_schema.py', 'independent_validator.py',
                'test_h2_separator.py')
    report = []
    with tempfile.TemporaryDirectory(prefix='as15-mutants-') as temp:
        tempdir = Path(temp)
        for idx, (name, file, old, new, test, expected) in enumerate(MUTANTS):
            scratch = tempdir / str(idx)
            scratch.mkdir()
            for fname in required:
                shutil.copyfile(HERE / fname, scratch / fname)
            target = scratch / file
            content = target.read_text()
            if content.count(old) != 1:
                raise AssertionError(f'{name}: mutation anchor not unique')
            target.write_text(content.replace(old, new, 1))
            env = dict(os.environ)
            env['PYTHONPATH'] = str(scratch)
            proc = subprocess.run(
                [sys.executable, '-m', 'unittest', '-v',
                 f'test_h2_separator.AS15SeparatorTests.{test}'],
                cwd=scratch, env=env, text=True, stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, timeout=25, check=False)
            output = proc.stdout
            killed = (proc.returncode != 0 and f'test_{test.removeprefix("test_")}' in output
                      and ((expected == 'FAIL' and 'FAILED (failures=' in output) or
                           (expected == 'ERROR' and 'FAILED (errors=' in output)))
            report.append({'mutant': name, 'killed': killed,
                           'targeted_test': test,
                           'failure_signature': (output[-600:] if not killed else expected)})
            if not killed:
                raise AssertionError(f'{name} survived or failed unexpectedly:\n{output[-1100:]}')
    return {'schema_version': 'AS15-SOURCE-MUTATIONS-v1',
            'injected': len(report), 'killed': sum(x['killed'] for x in report),
            'survived': sum(not x['killed'] for x in report),
            'mutants': report, 'workspace_modified': False,
            'scientific_gate': 'PENDING_INDEPENDENT_REVIEW'}


if __name__ == '__main__':
    print(json.dumps(verify(), ensure_ascii=False, indent=2))
