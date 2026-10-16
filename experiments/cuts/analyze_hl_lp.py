"""AS20: conservative paired LP assessment of independent local HL screening.

No result from an incomplete, censored, or capped screen can establish general
HL redundancy. Never change the independent pre-registered selection post hoc.
"""
from __future__ import annotations

import math

SCHEMA = 'AS20-HL-ANALYSIS-v1'


def analyze(plan, manifest, rows):
    all_cases = {c['name']: c for c in plan['cases']}
    names = manifest['cases']
    if len(set(names)) != len(names) or any(name not in all_cases for name in names):
        raise ValueError('INVALID_INPUT: invalid manifest case selection')
    keys = set()
    per_case = []
    gains = set()
    for row in rows:
        key = (row.get('name'), row.get('arm_id'))
        if (key in keys or key[0] not in names or key[1] not in ('U_K', 'U_K_HL')
                or row.get('instance_sha256') != all_cases[key[0]]['source_sha256']
                or row.get('raw_graph_id') != all_cases[key[0]]['raw_graph_id']):
            raise ValueError('INVALID_INPUT: duplicated or untrusted result row')
        keys.add(key)
    if keys != {(name, arm) for name in names for arm in ('U_K', 'U_K_HL')}:
        raise ValueError('INVALID_INPUT: incomplete paired rows')
    lookup = {(r['name'], r['arm_id']): r for r in rows}
    for name in names:
        base, hl = (lookup[(name, key)] for key in ('U_K', 'U_K_HL'))
        optimal_pair = base['status'] == hl['status'] == 'OPTIMAL'
        baseline, strengthened = base.get('lp_objective'), hl.get('lp_objective')
        is_number = lambda x: type(x) in (int, float) and math.isfinite(x)
        if optimal_pair and not (is_number(baseline) and is_number(strengthened)):
            raise ValueError('INVALID_INPUT: optimal result missing finite LP')
        delta = strengthened - baseline if optimal_pair else None
        if optimal_pair and delta < -1e-5:
            optimal_pair = False  # report numeric anomaly, never count a gain
        fraction = delta / max(1., abs(baseline)) if optimal_pair else None
        bcost, hcost = base.get('elapsed_wall_s'), hl.get('elapsed_wall_s')
        ratio = hcost / bcost if (is_number(bcost) and is_number(hcost) and bcost > 0) else None
        accepted = hl.get('hl_accepted', 0)
        report = hl.get('separation') or {}
        selection = hl.get('selection') or {}
        partial = (not selection or selection.get('no_eligible_support', False)
                   or report.get('status') == 'PARTIAL_BUDGET'
                   or any(r.get('status') in ('ABSTAIN', 'SKIPPED_SIZE')
                          for r in report.get('records', []))
                   or len(report.get('records', [])) < selection.get('selected_count', 0))
        improved = bool(optimal_pair and fraction >= 0.01 - 1e-9)
        affordable = bool(ratio is not None and ratio <= 2)
        if improved and affordable:
            gains.add(all_cases[name]['raw_graph_id'])
        per_case.append({
            'name': name, 'raw_graph_id': all_cases[name]['raw_graph_id'],
            'baseline_status': base['status'], 'hl_status': hl['status'],
            'paired_optimal': optimal_pair,
            'k_lp': baseline if optimal_pair else None,
            'k_hl_lp': strengthened if optimal_pair else None,
            'marginal_gain': delta if optimal_pair else None,
            'relative_gain': fraction,
            'k_elapsed_wall_s': bcost, 'k_hl_elapsed_wall_s': hcost,
            'cost_ratio': ratio, 'cuts_certified': accepted,
            'proposals_selected': selection.get('selected_count'),
            'screen_incomplete': partial,
            'gain_at_least_1pct': improved, 'gain_and_cost_acceptable': improved and affordable,
            'separation_status': hl.get('separation_status'),
            'oracle_calls': report.get('oracle_calls'),
            'separation_wall_s': report.get('elapsed_wall_s'),
        })
    complete_six = set(names) == set(all_cases)
    ready = (manifest['mode'] == 'LP' and complete_six
             and all(item['paired_optimal'] and not item['screen_incomplete'] for item in per_case))
    if manifest['mode'] != 'LP':
        gate = 'NOT_EXECUTED'
    elif len(gains) >= 2 and complete_six:
        gate = 'GO_CANDIDATE_REVIEW'
    elif not ready:
        gate = 'INVESTIGATE'
    else:
        gate = 'NO_GAIN_IN_BOUNDED_SCREEN'
    return {'schema_version': SCHEMA, 'stage': 'AS20', 'gate': gate,
            'note': ('Only local cardinality HL on preselected bounded supports. '
                     'A negative result does not prove HL dominated by K, nor certify STOP. '
                     'GO_CANDIDATE_REVIEW is not MIP authorization.'),
            'arm_rows': len(rows), 'selected_cases': names,
            'complete_six_development_cases': complete_six,
            'complete_conclusive_screen': ready,
            'independent_raw_graphs_gain_at_least_1pct_cost_at_most_2x': len(gains),
            'cases': per_case}
