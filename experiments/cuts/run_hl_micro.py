#!/usr/bin/env python3
"""AS19 independent HL micro-pilot: physically certified K4, no Gurobi needed.

No automatic use on large instances. Append-only output with LP and wall times.
"""
import argparse
import json
from pathlib import Path
from time import perf_counter

from h2_oracle import PhysicalInstance
from h2_oracle_schema import canonical_json, digest
from hl_local import HLOptions, separate_hl
from verify_as13_foundations import k4, k_cuts, h2_for_support, reach_arcs, solve_comp_lp


def run():
    raw, W = k4()
    S, T, V, adj, r = raw
    A = reach_arcs(V, adj, r)
    K = k_cuts(S, T, V, adj, r, A)
    begin = perf_counter()
    base, fractional_k, _ = solve_comp_lp(S, T, V, A, K)
    t_k = perf_counter() - begin
    h2 = []
    for missing in W:
        R = [v for v in W if v != missing]
        row = h2_for_support(S, T, V, adj, r, R)
        if row is None:
            raise AssertionError('H2 triple construction missing')
        h2.append(row[:2])
    begin = perf_counter()
    lp_h2, fractional_h2, _ = solve_comp_lp(S, T, V, A, K, more=h2)
    t_h2 = perf_counter() - begin
    opt = HLOptions(max_support_size=4, max_oracle_calls=32, total_budget_s=15., per_support_budget_s=12.)
    report = separate_hl(PhysicalInstance.from_tuple(raw), fractional_h2,
                         supports=[W], options=opt)
    if len(report.cuts) != 1:
        raise AssertionError(f'pilot did not certify HL: {report.to_dict()}')
    cut = report.cuts[0]
    begin = perf_counter()
    lp_hl, _, _ = solve_comp_lp(S, T, V, A, K,
                               more=[*h2, (dict(cut.coefficients), cut.rhs)])
    t_hl = perf_counter() - begin
    if not (abs(base - 2) < 1e-7 and abs(lp_h2 - 8 / 3) < 1e-7
            and abs(lp_hl - 3) < 1e-7):
        raise AssertionError('K4 LP hierarchy does not match independently certified expectation')
    return {
        'schema_version': 'AS19-HL-MICRO-v1', 'instance_type': 'SYNTHETIC_K4',
        'not_a_real_instance_benchmark': True,
        'independent_of_as16_gate': True, 'instance_sha256': report.instance_sha256,
        'support': list(W), 'physical_oracle_calls': report.oracle_calls,
        'certification_elapsed_wall_s': report.elapsed_wall_s,
        'lp_comp_k': base, 'lp_comp_k_h2': lp_h2, 'lp_comp_k_h2_hl': lp_hl,
        'marginal_hl_vs_h2': lp_hl - lp_h2,
        'solver_wall_s': {'comp_k': t_k, 'comp_k_h2': t_h2, 'comp_k_h2_hl': t_hl},
        'solver': 'scipy.optimize.linprog(method=highs)',
        'comparability_note': 'single execution, no warm-up; times are descriptive, not statistical',
        'cut_certificate_sha256': cut.certificate_sha256,
        'cut_sha256': cut.cut_hash,
        'separation': report.to_dict(),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True, help='new JSON file; never overwritten')
    args = parser.parse_args()
    result = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8') as f:
        f.write(canonical_json(result) + '\n')
    print(json.dumps({'status': 'CERTIFIED_SYNTHETIC_ONLY',
                      'lp': [result['lp_comp_k'], result['lp_comp_k_h2'], result['lp_comp_k_h2_hl']],
                      'oracle_calls': result['physical_oracle_calls'],
                      'output': str(args.output)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
