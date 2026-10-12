"""AS05-DIAG: sintetizar três estágios concluídos, sem reexecutar solves."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for directory in (ROOT, HERE, HERE.parent / 'alternative-formulations'):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

from as05_diag_analysis import build_analysis  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--plan', type=Path,
                        default=Path('results/benchmark/as05-diagnostic-plan-v1.json'))
    parser.add_argument('--results-dir', type=Path,
                        default=Path('results/benchmark/as05-diagnostic-001'))
    parser.add_argument('--output-dir', type=Path)
    args = parser.parse_args()
    stage_paths = {stage: args.results_dir/stage for stage in ('cuts', 'censored', 'grouping')}
    out = args.output_dir or (args.results_dir/'analysis')
    result = build_analysis(root=args.root, plan_path=args.plan,
                            stage_folders=stage_paths, output_dir=out)
    print(f'AS05_DIAGNOSTIC_ANALYSIS_WRITTEN {result}')
    print('AS05_SCIENTIFIC_GATE PENDING | DIAGNOSTIC_ONLY')


if __name__ == '__main__':
    main()
