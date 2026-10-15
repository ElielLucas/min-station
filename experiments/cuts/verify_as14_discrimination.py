#!/usr/bin/env python3
"""AS14: adversarial source mutations executed in isolated temporary copies.

Every mutant changes runtime semantics and must fail its specific AS14 test.
A mere import error or syntax error does not count as a killed mutant.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
FILES = ('h2_oracle.py', 'h2_oracle_schema.py', 'h2_oracle_cache.py',
         'independent_validator.py', 'test_h2_oracle.py')

# (name, file, unique original, replacement, test name)
MUTANTS = (
    ('M1_VIABLE_FOR_ALL', 'h2_oracle.py',
     'status = Status.VIABLE if size == len(instance.S) else Status.INFEASIBLE',
     'status = Status.VIABLE',
     'test_as14_02_infeasible_has_replayable_hall_witness'),
    ('M2_PHYSICAL_STATIONS_IGNORED', 'h2_oracle.py',
     'reach[s] = destinos_alcancaveis(s, instance.T, stations, graph, instance.r)',
     'reach[s] = destinos_alcancaveis(s, instance.T, (), graph, instance.r)',
     'test_as14_01_terminal_as_relay'),
    ('M3_BUDGET_DISABLED', 'h2_oracle.py',
     'if budget is not None and elapsed() >= budget:',
     'if False:',
     'test_as14_03_zero_budget_always_unknown'),
    ('M4_CROSS_INSTANCE_CACHE', 'h2_oracle_cache.py',
     'return (instance_sha256, frozenset(allowed))',
     "return ('CONSTANT', frozenset(allowed))",
     'test_as14_05_graphs_same_size_do_not_collide'),
    ('M5_UNKNOWN_PROMOTED_IN_BHAT', 'h2_oracle.py',
     'if outcome.status is Status.INFEASIBLE:',
     'if outcome.status is not Status.VIABLE:',
     'test_as14_06_candidate_exception_does_not_enter_bhat'),
    ('M6_COMPLEMENT_WRONG', 'h2_oracle.py',
     'F = frozenset(instance.V) - R',
     'F = R',
     'test_as14_04_complement_on_actual_physical_V'),
    ('M7_MONOTONICITY_DISABLED', 'h2_oracle_cache.py',
     "        for (other_hash, other_allowed), entry in self._items.items():",
     "        for (other_hash, other_allowed), entry in ():",
     'test_as14_07_cached_monotonic_conflicts_fail_closed'),
)


def run():
    outcomes = []
    for name, filename, original, mutant, test in MUTANTS:
        with tempfile.TemporaryDirectory(prefix='as14-mutant-') as temp:
            dest = Path(temp)
            for path in FILES:
                shutil.copy2(HERE / path, dest / path)
            file_path = dest / filename
            text = file_path.read_text(encoding='utf8')
            if text.count(original) != 1:
                raise AssertionError(f'{name}: mutation location must occur exactly once')
            file_path.write_text(text.replace(original, mutant), encoding='utf8')
            command = [sys.executable, '-m', 'unittest', '-v',
                       f'test_h2_oracle.AS14OracleTests.{test}']
            proc = subprocess.run(command, cwd=dest, capture_output=True,
                                  text=True, timeout=30)
            log = proc.stdout + proc.stderr
            killed = proc.returncode != 0 and (' ... FAIL' in log or ' ... ERROR' in log) \
                     and ('Ran 1 test' in log) and ('ModuleNotFoundError' not in log)
            outcomes.append({'mutant':name, 'killed':killed,
                             'test':test, 'signature':next((s.strip() for s in log.splitlines()
                                if s.startswith(test) and ('FAIL' in s or 'ERROR' in s)),
                                 'NO_EXPECTED_TEST_FAILURE')})
    result = {'schema':'AS14-SOURCE-MUTATION-v1', 'injected':len(MUTANTS),
              'killed':sum(o['killed'] for o in outcomes),
              'survived':sum(not o['killed'] for o in outcomes),
              'workspace_modified':False, 'mutants':outcomes,
              'independent_verifier_gate':'PENDING_EXTERNAL_REVIEW'}
    print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
    if result['survived']:
        sys.exit(1)


if __name__ == '__main__':
    run()
