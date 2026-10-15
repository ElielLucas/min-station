"""AS16: fail-closed analysis of paired LP and post-hoc same-pool controls.

No solver is needed to reanalyze an existing run:
  python experiments/cuts/analyze_h2_lp.py --run-dir results/benchmark/as16-...
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path

SCHEMA = 'AS16-ANALYSIS-v1'
ONLINE = ('U', 'U_K', 'U_H2', 'U_K_H2')
FIXED = ('U_FIXED_H2', 'U_K_FIXED_H2')


def strength(base, candidate):
    """LP is minimization. A censored objective is NOT a valid numeric LB."""
    if base is None or candidate is None:
        return {'absolute_gain': None, 'relative_gain': None, 'reason': 'CENSORED'}
    a = base.get('lp_objective') if base.get('status') == 'OPTIMAL' else None
    b = candidate.get('lp_objective') if candidate.get('status') == 'OPTIMAL' else None
    if a is None or b is None or not all(math.isfinite(x) for x in (a, b)):
        return {'absolute_gain': None, 'relative_gain': None, 'reason': 'CENSORED'}
    difference = b - a
    return {'absolute_gain': difference,
            'relative_gain': difference / max(abs(a), 1e-9), 'reason': None}


def cut_accounting(row):
    sep = row.get('separation') or {}
    records = sep.get('records', [])
    counts = Counter(r.get('status') for r in records)
    return {'proposed': sep.get('supports_proposed', 0),
            'examined': sep.get('supports_examined', 0),
            'certified_complements': sum(counts[s] for s in
                ('EMITTED', 'DUPLICATE', 'DEGENERATE_COVER', 'NOT_VIOLATED')),
            'violated': sum(counts[s] for s in ('EMITTED', 'DUPLICATE', 'DEGENERATE_COVER')),
            'accepted': row.get('h2_accepted', 0), 'redundant':
                 counts['DUPLICATE'] + counts['DEGENERATE_COVER'] + row.get('h2_redundant', 0),
            'not_tested': max(0, sep.get('supports_proposed', 0) - len(records)) +
                 sum(len(r.get('unexamined_candidates', [])) for r in records),
            'unknown_complement': counts['UNKNOWN_COMPLEMENT'],
            'status_counts': dict(sorted(counts.items()))}


def analyze(plan, manifest, rows):
    expected = {c['name'] for c in plan['cases']}
    subset = set(manifest['cases'])
    if not subset or not subset <= expected:
        raise ValueError('INVALID_INPUT: outside AS16 six development cases')
    if len(rows) != len(subset) * (len(ONLINE) + len(FIXED)):
        raise ValueError('INVALID_INPUT: missing or duplicate arm rows')
    indexed = {}
    for row in rows:
        name, arm = row['name'], row['arm_id']
        key = (name, arm)
        if key in indexed or name not in subset or arm not in ONLINE + FIXED:
            raise ValueError('INVALID_INPUT: duplicate/unregistered arm')
        case = next(c for c in plan['cases'] if c['name'] == name)
        if row['instance_sha256'] != case['source_sha256'] or row['raw_graph_id'] != case['raw_graph_id']:
            raise ValueError('INVALID_INPUT: source identity mismatch')
        if row['status'] == 'OPTIMAL' and (row.get('lp_objective') is None or
              not math.isfinite(row['lp_objective'])):
            raise ValueError('INVALID_INPUT: OPTIMAL without objective')
        if row['status'] != 'OPTIMAL' and row.get('lp_objective') is not None:
            raise ValueError('INVALID_INPUT: censored objective must be absent')
        indexed[key] = row
    complete = len(subset) == len(expected)
    threshold = plan['gate']['minimum_relative_gain']
    cost_multiple = plan['gate']['maximum_h2_wall_vs_k_multiple']
    wins = []
    paid_wins = []
    comparisons = []
    for name in sorted(subset):
        arms = {a: indexed[(name, a)] for a in ONLINE + FIXED}
        baseline = arms['U_K']
        online = arms['U_K_H2']
        pure_h2 = arms['U_H2']
        case = next(c for c in plan['cases'] if c['name'] == name)
        k_gain = strength(arms['U'], baseline)
        h2_gain = strength(arms['U'], pure_h2)
        marginal_gain = strength(baseline, online)
        pool_u_gain = strength(arms['U'], arms['U_FIXED_H2'])
        pool_k_gain = strength(baseline, arms['U_K_FIXED_H2'])
        gain = marginal_gain['relative_gain']
        improved = gain is not None and gain >= threshold - 1e-10
        total = online.get('elapsed_wall_s')
        k_wall = baseline.get('elapsed_wall_s')
        affordable = (improved and isinstance(total, (float, int)) and
                      isinstance(k_wall, (float, int)) and k_wall > 0 and
                      total <= cost_multiple * k_wall and
                      total <= plan['budget']['wall_seconds_per_arm'] + 0.5)
        if improved:
            wins.append(case['raw_graph_id'])
        if affordable:
            paid_wins.append(case['raw_graph_id'])
        comparisons.append({'name': name, 'raw_graph_id': case['raw_graph_id'],
            'statuses': {a: arms[a]['status'] for a in ONLINE + FIXED},
            'U_to_U_K': k_gain, 'U_to_U_H2': h2_gain,
            'U_K_to_U_K_H2': marginal_gain,
            'same_pool_U': pool_u_gain, 'same_pool_U_K': pool_k_gain,
            'same_pool_is_post_hoc': True,
            'online_h2_cuts': cut_accounting(online),
            'pure_h2_cuts': cut_accounting(pure_h2),
            'wall_s': {a: arms[a].get('elapsed_wall_s') for a in ONLINE + FIXED},
            'phases_s': {a: arms[a].get('timings', {}) for a in ONLINE + FIXED},
            'h2_improves_1pct': improved, 'cost_not_annulled': affordable})
    censored_online = [(name, arm, indexed[(name, arm)]['status']) for name in sorted(subset)
                       for arm in ONLINE if indexed[(name, arm)]['status'] != 'OPTIMAL']
    censored_fixed = [(name, arm, indexed[(name, arm)]['status']) for name in sorted(subset)
                      for arm in FIXED if indexed[(name, arm)]['status'] != 'OPTIMAL']
    raw_gain = len(set(wins))
    raw_paid = len(set(paid_wins))
    if not complete or censored_online or censored_fixed:
        gate = 'INVESTIGATE'
        reason = 'amostra incompleta, resultado censurado ou controle same-pool indisponível'
    elif raw_gain >= plan['gate']['minimum_independent_raw_graphs'] and raw_paid >= 1:
        gate = 'GO'
        reason = 'ganho marginal LP e custo de parede nos limiares pré-registrados'
    else:
        gate = 'STOP'
        reason = 'ganho marginal em grafos brutos independentes e/ou custo insuficiente'
    return {'schema_version': SCHEMA, 'stage': 'AS16', 'gate': gate, 'gate_reason': reason,
            'gate_rules': plan['gate'], 'partial_smoke': not complete,
            'complete_online_optima': not censored_online,
            'all_same_pool_controls_complete': not censored_fixed,
            'independent_raw_graphs_with_gain': raw_gain,
            'independent_raw_graphs_with_paid_gain': raw_paid,
            'arm_rows': len(rows), 'censored_online': censored_online,
            'censored_fixed': censored_fixed, 'comparisons': comparisons,
            'methodological_caveats': [
                'LP ótimo numérico não é certificado racional independente.',
                'O pool fixo é formado a posteriori no desenvolvimento; não é teste out-of-sample.',
                'Um ganho no LP puro não prova persistência na raiz ou no MIP.',
                'Resultados TIME_LIMIT/UNKNOWN/ERROR não substituem ótimos.',
                'GO é decisão exploratória condicionada à revisão independente.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir', type=Path, required=True)
    args = parser.parse_args()
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from run_h2_lp import load_plan
    plan, expected = load_plan()
    manifest = json.loads((args.run_dir / 'manifest.json').read_text())
    if manifest['plan_sha256'] != expected:
        raise ValueError('INVALID_INPUT: preregistration sha does not match run')
    rows = json.loads((args.run_dir / 'rows.json').read_text())
    report = analyze(plan, manifest, rows)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
