#!/usr/bin/env python3
"""AS25.1 analysis: AS25 reference gate + preregistered A/B/C/D classification.

Pairs must be OPTIMAL on both arms; every other status stays censored.
No class authorizes MIP (AS26) automatically.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import sys

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
from analyze_fcr_lp_as25 import _optimal, _pair

SCHEMA = 'AS251-FCR-ANALYSIS-v1'
FCR_ARMS = ('U_K_FCR_AS25', 'U_K_FCR_INFRA', 'U_K_FCR_AS251')


def infra_equivalence(as25, infra, tolerance):
    """Same rows round by round (digests) and same final LP objective."""
    if not (_optimal(as25) and _optimal(infra)):
        return False
    left, right = as25.get('fcr_rounds', []), infra.get('fcr_rounds', [])
    if len(left) != len(right):
        return False
    for a, b in zip(left, right):
        if (a.get('signature_digest') != b.get('signature_digest') or
                a.get('terms_digest') != b.get('terms_digest')):
            return False
    x, y = float(as25['lp_objective']), float(infra['lp_objective'])
    return abs(x-y) <= tolerance*max(1., abs(x))


def _overhead(arm, control):
    return arm['elapsed_wall_s']-control['elapsed_wall_s']


def _coverage_complete(row):
    return bool(row.get('singleton_complete_all_scans') is True and
                row.get('larger_complete_or_deferred_all_scans') is True and
                not row.get('fcr_cut_cap_encountered', False) and
                not row.get('fcr_total_cut_cap_reached', False))


def analyze(plan, manifest, rows):
    arms = tuple(manifest.get('arms', ()))
    if arms != tuple(plan['arms']):
        raise ValueError('arm list differs from frozen plan')
    rule = plan['classification']
    cases = plan['cases']
    identities = {c['name']: c for c in cases}
    selected = set(manifest.get('cases', ()))
    if not selected or not selected <= set(identities):
        raise ValueError('unknown cases in manifest')
    bycase = {name: {} for name in selected}
    for row in rows:
        name, arm = row.get('name'), row.get('arm_id')
        if name not in bycase or arm not in arms or arm in bycase[name]:
            raise ValueError('duplicate/unknown case arm')
        if (row.get('raw_graph_id') != identities[name]['raw_graph_id'] or
                row.get('instance_sha256') != identities[name]['source_sha256']):
            raise ValueError('source identity mismatch')
        bycase[name][arm] = row
    if len(rows) != len(selected)*len(arms) or any(len(group) != len(arms) for group in bycase.values()):
        raise ValueError('incomplete or excessive arm rows')

    detailed, qualified, gain_only = [], set(), set()
    reductions, equivalence, rescued = [], [], []
    for case in cases:
        name = case['name']
        if name not in selected:
            continue
        data = bycase[name]
        control, candidate = data[rule['control_arm']], data[rule['candidate_arm']]
        marginal = _pair(control, candidate)
        as25_marginal = _pair(control, data['U_K_FCR_AS25'])
        complete = _coverage_complete(candidate)
        gain_ok = (marginal['paired_optimal'] and marginal['relative_gain'] is not None and
                   not marginal['objective_nonmonotone'] and
                   marginal['relative_gain'] >= rule['minimum_relative_gain'])
        if gain_ok:
            gain_only.add(case['raw_graph_id'])
        if (gain_ok and complete and marginal['cost_multiple'] is not None and
                marginal['cost_multiple'] <= rule['maximum_cost_multiple']):
            qualified.add(case['raw_graph_id'])
        equivalent = None
        reduction = None
        if all(_optimal(data[a]) for a in ('U_K', 'U_K_FCR_AS25', 'U_K_FCR_INFRA')):
            equivalent = infra_equivalence(data['U_K_FCR_AS25'], data['U_K_FCR_INFRA'],
                                           rule['infra_objective_tolerance'])
            equivalence.append(equivalent)
            base = _overhead(data['U_K_FCR_AS25'], control)
            if base > 0:
                reduction = 1-_overhead(data['U_K_FCR_INFRA'], control)/base
                reductions.append(reduction)
        elif _optimal(control) and _optimal(data['U_K_FCR_INFRA']) and not _optimal(data['U_K_FCR_AS25']):
            rescued.append(name)
        detailed.append({
            'name': name, 'raw_graph_id': case['raw_graph_id'],
            'as251_vs_U_K': marginal, 'as25_policy_vs_U_K': as25_marginal,
            'infra_vs_U_K': _pair(control, data['U_K_FCR_INFRA']),
            'as251_vs_as25_policy': _pair(data['U_K_FCR_AS25'], candidate),
            'as251_coverage_complete': complete, 'counts_for_A': case['raw_graph_id'] in qualified,
            'infra_equivalent': equivalent, 'infra_overhead_reduction': reduction,
            'objective_by_round': {a: [r.get('objective_after') for r in data[a].get('fcr_rounds', [])]
                                   for a in FCR_ARMS},
            'arms': {a: {'status': data[a].get('status'), 'lp_objective': data[a].get('lp_objective'),
                         'elapsed_wall_s': data[a].get('elapsed_wall_s'), 'reason': data[a].get('reason'),
                         'fcr_added': data[a].get('fcr_added', 0), 'fcr_nnz': data[a].get('fcr_nnz', 0),
                         'timings': data[a].get('timings', {})} for a in arms}})

    efficiency = bool(equivalence and all(equivalence) and reductions and
                      statistics.median(reductions) >= rule['efficiency_minimum_median_overhead_reduction'])
    minimum = rule['minimum_independent_raw_graphs']
    if manifest.get('mode') != 'LP':
        classification = 'NOT_CLASSIFIED_DRY_RUN'
    elif len(qualified) >= minimum:
        classification = 'A'
    elif len(gain_only) >= minimum:
        classification = 'C'
    elif efficiency:
        classification = 'B'
    else:
        classification = 'D'

    censored = [{'name': name, 'arm_id': arm, 'status': row.get('status'), 'reason': row.get('reason')}
                for name, group in bycase.items() for arm, row in group.items() if not _optimal(row)]
    full_six = len(selected) == len(cases) and len({identities[n]['raw_graph_id'] for n in selected}) == 6
    if (manifest.get('mode') != 'LP' or censored or not full_six or
            any(not _coverage_complete(bycase[n][rule['candidate_arm']]) for n in selected)):
        reference_gate = 'INVESTIGATE'
    elif len(qualified) >= plan['as25_reference_gate']['minimum_independent_raw_graphs']:
        reference_gate = 'GO_CANDIDATE_REVIEW'
    else:
        reference_gate = 'STOP'
    return {'schema_version': SCHEMA, 'stage': 'AS25.1', 'mode': manifest.get('mode'),
            'classification': classification, 'as25_reference_gate': reference_gate,
            'arm_rows': len(rows), 'case_count': len(selected),
            'qualified_raw_graph_ids': sorted(qualified), 'gain_at_least_1pct_raw_graph_ids': sorted(gain_only),
            'efficiency': {'holds': efficiency, 'infra_equivalent_cases': equivalence.count(True),
                           'infra_compared_cases': len(equivalence), 'overhead_reductions': reductions,
                           'median_overhead_reduction': statistics.median(reductions) if reductions else None,
                           'rescued_cases': rescued},
            'fully_preregistered_six_case_scope': full_six, 'censored': censored,
            'censored_arm_count': len(censored), 'cases': detailed, 'plan_sha256': manifest.get('plan_sha256'),
            'note': ('Gain counts only the LP objective; added rows with unchanged objective are flow-only. '
                     'AS25 reference gate applied to U_K_FCR_AS251 with deferred larger regions counted as covered.'),
            'mip_automatically_authorized': False, 'scientific_review_required': True,
            'region_coverage_scope': 'complete eligible singletons + bounded selected heuristics; never all L'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--results-dir', type=Path, required=True)
    parser.add_argument('--plan', type=Path, default=Path(__file__).resolve().parents[2] /
                        'docs/technical/plans/execucao/as251-preregistro-fcr-lp.json')
    parser.add_argument('--output', type=Path, default=None)
    args = parser.parse_args()
    plan = json.loads(args.plan.read_text())
    manifest = json.loads((args.results_dir/'manifest.json').read_text())
    rows = json.loads((args.results_dir/'rows.json').read_text())
    report = analyze(plan, manifest, rows)
    if args.output:
        with args.output.open('x', encoding='utf-8') as out:
            json.dump(report, out, indent=2, ensure_ascii=False)
    else:
        print(json.dumps({'classification': report['classification'],
                          'as25_reference_gate': report['as25_reference_gate'],
                          'censored': report['censored_arm_count'],
                          'efficiency': report['efficiency']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
