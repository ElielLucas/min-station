#!/usr/bin/env python3
"""Re-run the five non-equivalent AS14 R1 mutants against the AS14 unit suite.

The reviewer-defined mutations are read, unchanged, from verifier-r1/review_mutants.py.
Each mutant runs in an isolated temp directory; no repository files are modified.
"""
from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REVIEW = (ROOT / 'specs/as-14-oraculo-viabilidade-matching/verifier-r1'
          / 'review_mutants.py')
REQUIRED = ('R09', 'R10', 'R23', 'R29', 'R30')
FILES = ('h2_oracle.py', 'h2_oracle_schema.py', 'h2_oracle_cache.py',
         'independent_validator.py', 'test_h2_oracle.py')


def verify():
    spec = importlib.util.spec_from_file_location('as14_review_mutants_r1', REVIEW)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'Cannot load reviewer mutations: {REVIEW}')
    review = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(review)
    selected = [m for m in review.M if m[0].split('_', 1)[0] in REQUIRED]
    if tuple(sorted(m[0].split('_', 1)[0] for m in selected)) != tuple(sorted(REQUIRED)):
        raise RuntimeError('Required R1 mutant specifications are missing or duplicated')
    records = []
    for name, filename, original, replacement in selected:
        with tempfile.TemporaryDirectory(prefix='as14-r1-mutant-') as temp:
            work = Path(temp)
            for source in FILES:
                shutil.copy2(ROOT / 'experiments/cuts' / source, work / source)
            review.apply(work, filename, original, replacement, name)
            proc = subprocess.run(
                [sys.executable, '-m', 'unittest', 'test_h2_oracle', '-q'],
                cwd=work, capture_output=True, text=True, timeout=60, check=False)
            log = proc.stdout + proc.stderr
            records.append({'mutant': name.split('_', 1)[0], 'name': name,
                            'killed': proc.returncode != 0,
                            'failure_excerpt': log[-950:] if proc.returncode else ''})
    return {'schema': 'AS14-R1-TARGETED-SOURCE-MUTATIONS-v1',
            'required_mutants': list(REQUIRED),
            'injected': len(records),
            'killed': sum(item['killed'] for item in records),
            'survived': sum(not item['killed'] for item in records),
            'workspace_modified': False, 'results': records,
            'independent_gate': 'STOP_UNTIL_NEW_EXTERNAL_REVIEW'}


def main():
    evidence = verify()
    print(json.dumps(evidence, ensure_ascii=False, indent=2))
    if evidence['injected'] != len(REQUIRED) or evidence['survived']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
