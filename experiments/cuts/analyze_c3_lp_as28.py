#!/usr/bin/env python3
"""AS28: analise conservadora da triagem LP limitada C3-cut, sem promover MIP."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def analyze(plan, manifest, rows):
    expected = {(c['name'], arm) for c in plan['cases'] if c['name'] in manifest['cases']
                for arm in plan['arms']}
    actual = [(r.get('name'), r.get('arm_id')) for r in rows]
    if len(actual) != len(set(actual)) or set(actual) != expected:
        raise ValueError('INVALID_INPUT: missing/duplicate arms')
    if manifest['mode'] == 'DRY_RUN':
        if any(r['status'] != 'NOT_RUN' for r in rows):
            raise ValueError('INVALID_INPUT: dryrun performed computation')
        return {'classification': 'NOT_EXECUTED_DRY_RUN', 'arm_rows': len(rows),
                'paired_optimal': 0, 'qualified_raw_graphs': [],
                'scope': 'LP bounded sample, no MIP'}
    by_key = {(r['name'], r['arm_id']): r for r in rows}
    pairs, qualified, censored = [], set(), []
    for case in plan['cases']:
        if case['name'] not in manifest['cases']:
            continue
        ctrl, cand = (by_key[case['name'], arm] for arm in plan['arms'])
        if ctrl['status'] != 'OPTIMAL' or cand['status'] != 'OPTIMAL':
            censored.append({'name': case['name'], 'control_status': ctrl['status'],
                             'candidate_status': cand['status']})
            continue
        z0, z1 = ctrl.get('lp_objective'), cand.get('lp_objective')
        if z0 is None or z1 is None or z0 < 0 or z1 < z0-1e-5:
            raise ValueError('INVALID_INPUT: inconsistent LP bounds')
        gain = (z1-z0)/max(abs(z0), 1e-12)
        ratio = cand['elapsed_wall_s']/max(ctrl['elapsed_wall_s'], 1e-12)
        complete = bool(cand.get('complete_selected_all_scans')) and not cand.get('cut_cap_reached')
        passed = (gain >= plan['gate']['minimum_relative_gain'] and
                  ratio <= plan['gate']['maximum_cost_multiple'] and complete)
        pairs.append({'name': case['name'], 'raw_graph_id': case['raw_graph_id'],
                      'base_lp': z0, 'candidate_lp': z1, 'relative_gain': gain,
                      'cost_multiple': ratio, 'c3_rows': cand['n_c3_cuts'],
                      'complete_selected_scans': complete,
                      'qualifies_bounded_screen': passed})
        if passed:
            qualified.add(case['raw_graph_id'])
    if len(qualified) >= plan['gate']['minimum_independent_raw_graphs']:
        cls = 'PROMISING_FOR_INDEPENDENT_REVIEW'
    elif len(pairs) >= plan['gate']['min_paired_optimal'] and not any(
        p['relative_gain'] >= plan['gate']['minimum_relative_gain'] for p in pairs
    ):
        cls = 'NO_SIGNAL_BOUNDED_POLICY'
    else:
        cls = 'INCONCLUSIVE_OR_COSTLY'
    return {'classification': cls, 'arm_rows': len(rows), 'paired_optimal': len(pairs),
            'censored_pairs': censored, 'qualified_raw_graphs': sorted(qualified),
            'pairs': pairs, 'gate': plan['gate'],
            'caution': 'No C3 global closure: at most 8 origins + 8 destinations and 2 rounds; '
                       'even PROMISING does not authorize MIP or large experiments',
            'mip_automatically_authorized': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results-dir', required=True, type=Path)
    args = parser.parse_args()
    from run_c3_lp_as28 import load_plan
    plan, sha = load_plan()
    root = args.results_dir
    manifest = json.loads((root/'manifest.json').read_text())
    if manifest['plan_sha256'] != sha:
        raise ValueError('INVALID_INPUT: plan SHA mismatch')
    rows = json.loads((root/'rows.json').read_text())
    outcome = analyze(plan, manifest, rows)
    print(json.dumps(outcome, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
