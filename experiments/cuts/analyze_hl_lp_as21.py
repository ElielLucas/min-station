"""AS21 paired LP gate, with strictly descriptive AS20 cross-campaign comparison.

Gurobi wall times from different experimental runs are exploratory, never a
proof of speedup. Structural caps and UNKNOWN prevent negative conclusions.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from analyze_hl_lp import analyze as analyze_as20


def analyze(plan, manifest, rows):
    base = analyze_as20(plan, manifest, rows)
    base['schema_version'] = 'AS21-HL-ANALYSIS-v1'
    base['stage'] = 'AS21'
    base['method'] = 'lower_cardinality_layers_independently_certified'
    base['note'] = ('Certified lower bound on regional cardinality only, NOT an exact '
                    'description of conv(Phi_R) or a proof of superiority over K. '
                    'Censored/partial supports remain inconclusive. Preliminary GO '
                    'requires independent review, not MIP authorization.')
    return base


def compare_as20(as20, as21):
    """Compare grounded archived metrics by case and raw graph, never infer GO."""
    old = {row['name']: row for row in as20['cases']}
    pairs = []
    for row in as21['cases']:
        prev = old.get(row['name'])
        if prev is None or prev['raw_graph_id'] != row['raw_graph_id']:
            continue
        pairs.append({
            'name': row['name'], 'raw_graph_id': row['raw_graph_id'],
            'as20_cuts': prev['cuts_certified'], 'as21_cuts': row['cuts_certified'],
            'as20_oracle_calls': prev['oracle_calls'], 'as21_oracle_calls': row['oracle_calls'],
            'as20_gain': prev['marginal_gain'], 'as21_gain': row['marginal_gain'],
            'as20_time_s': prev['k_hl_elapsed_wall_s'],
            'as21_time_s': row['k_hl_elapsed_wall_s'],
            'as20_incomplete': prev['screen_incomplete'],
            'as21_incomplete': row['screen_incomplete'],
        })
    return {'schema_version': 'AS21-AS20-COMPARISON-v1',
            'scope': 'descriptive cross-run comparison; timings not paired across runs',
            'cases': pairs}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--as20', type=Path, required=True, help='archived AS20 analysis.json')
    parser.add_argument('--as21', type=Path, required=True, help='new AS21 analysis.json')
    parser.add_argument('--output', type=Path, required=True, help='new path (append-only)')
    args = parser.parse_args()
    a20 = json.loads(args.as20.read_text(encoding='utf-8'))
    a21 = json.loads(args.as21.read_text(encoding='utf-8'))
    if a20.get('stage') != 'AS20' or a21.get('stage') != 'AS21':
        raise ValueError('INVALID_INPUT: stages must be AS20 and AS21')
    result = compare_as20(a20, a21)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8') as fh:
        json.dump(result, fh, ensure_ascii=False, indent=2, allow_nan=False)
        fh.write('\n')
    print(json.dumps({'cases_compared':len(result['cases']), 'output':str(args.output)}))


if __name__ == '__main__':
    main()
