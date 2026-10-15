#!/usr/bin/env python3
"""AS14 evidence: independently reconcile tri-state oracle with AS13 references.

No solver, no cut separator and no edits to historical experiments.  A JSON
report is written only with --output, which refuses to overwrite old results.
"""
from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for d in (ROOT / 'experiments/cuts', ROOT / 'experiments/structural',
          ROOT / 'experiments/alternative-formulations'):
    if str(d) not in sys.path:
        sys.path.insert(0, str(d))

from independent_validator import viavel, _grafo_unitario, destinos_alcancaveis  # noqa: E402
from h2_oracle import MatchingOracle, PhysicalInstance, Status, classify_h2  # noqa: E402
from h2_oracle_schema import canonical_json  # noqa: E402
from verify_as13_foundations import (k4, reach_arcs, reach_matching_oracle, small_controls)  # noqa: E402
from hb import construir as construir_hb  # noqa: E402


def _source_hashes():
    """Identify uncommitted code by its exact bytes, independent of git HEAD."""
    paths = (
        'experiments/cuts/h2_oracle.py',
        'experiments/cuts/h2_oracle_cache.py',
        'experiments/cuts/h2_oracle_schema.py',
        'experiments/cuts/independent_validator.py',
        'experiments/cuts/test_h2_oracle.py',
        'experiments/cuts/verify_as14_oracle.py',
        'experiments/cuts/verify_as14_discrimination.py',
        'experiments/cuts/verify_as14_r1_mutants.py',
    )
    return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in paths}


def _source_commit():
    try:
        sha = subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'],
                                      stderr=subprocess.DEVNULL, text=True).strip()
        paths = tuple(_source_hashes())
        subprocess.check_output(['git', '-C', str(ROOT), 'ls-files', '--error-unmatch',
                                 '--', *paths], stderr=subprocess.DEVNULL)
        subprocess.check_call(['git', '-C', str(ROOT), 'diff', '--quiet', 'HEAD', '--', *paths],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return sha
    except (OSError, subprocess.CalledProcessError):
        return None


def _audit_case(name, raw, masks):
    S, T, V, adj, r = raw
    instance = PhysicalInstance.from_tuple(raw)
    oracle = MatchingOracle()
    A_r = reach_arcs(V, adj, r)
    metrics = Counter()
    by_nu = {}
    samples = []
    seen = set()
    for mask in masks:
        if mask in seen:
            raise AssertionError(f'{name}: repeated mask')
        seen.add(mask)
        C = {v for j,v in enumerate(V) if mask & (1 << j)}
        result = oracle.check(instance, C, budget_s=10.)
        battery = viavel(S,T,V,adj,r,C)
        arc_matching = reach_matching_oracle(S,T,V,A_r,C)
        if result.status is Status.UNKNOWN:
            raise AssertionError(f'{name}: UNKNOWN without deliberate timeout, mask={mask}')
        if (result.status is Status.VIABLE) != battery or battery != arc_matching:
            raise AssertionError(f'{name}: oracle disagreement mask={mask}, C={C}')
        if result.status is Status.INFEASIBLE:
            graph = _grafo_unitario(V,adj)
            # Independent certificate reconstruction, including all neighbors
            # of the Hall origins, not just the stored count.
            neighbors = set().union(*(destinos_alcancaveis(s,T,C,graph,r)
                                      for s in result.hall_origins))
            if (neighbors != set(result.hall_destinations) or
                len(neighbors) >= len(result.hall_origins)):
                raise AssertionError(f'{name}: malformed Hall witness mask={mask}')
        else:
            graph = _grafo_unitario(V,adj)
            if (len({s for s,_ in result.witness}) != len(S) or
                len({t for _,t in result.witness}) != len(T) or
                any(t not in destinos_alcancaveis(s,T,C,graph,r)
                    for s,t in result.witness)):
                raise AssertionError(f'{name}: malformed VIABLE witness mask={mask}')
        metrics['VIABLE' if battery else 'INFEASIBLE'] += 1
        metrics['max_matching_size_sum'] += result.matching_size
        metrics['validated_subsets'] += 1
        bucket = by_nu.setdefault(str(result.matching_size), {'calls': 0, 'elapsed_wall_s': 0.0})
        bucket['calls'] += 1
        bucket['elapsed_wall_s'] += result.elapsed_wall_s
        if len(samples) < 4:
            samples.append({'mask': mask, 'status': result.status.value,
                            'nu': result.matching_size,
                            'certificate_sha256': hashlib.sha256(result.to_json().encode()).hexdigest()})
    return {'instance_sha256': instance.fingerprint, 'vertices': len(V), 'robots': len(S),
            'stations_checked': metrics['validated_subsets'],
            'viable': metrics['VIABLE'], 'infeasible': metrics['INFEASIBLE'],
            'matching_size_sum': metrics['max_matching_size_sum'],
            'cost_by_matching_size': by_nu,
            'profiling': oracle.metrics(), 'certificate_samples': samples}


def verify():
    controls = small_controls()
    cases = {}
    for j, raw in enumerate(controls):
        name = f'control-{j}'
        cases[name] = _audit_case(name, raw, range(1 << len(raw[2])))
        if cases[name]['stations_checked'] != (1 << len(raw[2])):
            raise AssertionError(f'{name}: incomplete control enumeration')

    large = [ ('HB', tuple(construir_hb(4, 2, 1)[j] for j in (0,1,2,3,5))),
              ('K4', k4()[0])]
    for name, raw in large:
        masks = {0, (1 << len(raw[2])) - 1}
        for j in range(len(raw[2])):
            masks.add(1 << j)
        for a,b in combinations(range(len(raw[2])), 2):
            masks.add((1 << a) | (1 << b))
        for k in range(200):
            masks.add((k * 229 + k * k * 37) & ((1 << len(raw[2])) - 1))
        cases[name] = _audit_case(name, raw, sorted(masks))

    controls_count = sum(cases[f'control-{j}']['stations_checked'] for j in range(5))
    hb_k4_count = cases['HB']['stations_checked'] + cases['K4']['stations_checked']
    if controls_count != 68 or hb_k4_count != 674:
        raise AssertionError(f'incomplete audit: controls={controls_count}, HB/K4={hb_k4_count}')

    # A separate H2 regression: F=V\\R and Bhat_R independently reconstructed
    # from the battery-state validator, no dependency on H2 implementation.
    h2_supports = 0
    for raw in controls:
        S,T,V,adj,r = raw
        instance = PhysicalInstance.from_tuple(raw)
        oracle = MatchingOracle()
        physical = [set(C) for k in range(len(V)+1) for C in combinations(V,k)
                    if viavel(S,T,V,adj,r,C)]
        for k in range(len(V)+1):
            for R in combinations(V,k):
                F = set(V) - set(R)
                actual = classify_h2(oracle, instance, R)
                complement_viable = viavel(S,T,V,adj,r,F)
                if complement_viable:
                    if actual.state != 'NO_CUT':
                        raise AssertionError('H2 should not be certified when F is viable')
                else:
                    expected_b = {v for v in R if not viavel(S,T,V,adj,r,F | {v})}
                    if actual.state != 'CERTIFIED' or set(actual.Bhat) != expected_b:
                        raise AssertionError('H2 partial/full classification disagreement')
                    for C in physical:
                        if sum(c for v,c in actual.coefficients if v in C) < 2:
                            raise AssertionError('H2 excluded a feasible installation')
                    h2_supports += 1
    return {
        'schema': 'AS14-ORACLE-INDEPENDENT-EVIDENCE-v1',
        'stage': 'AS14',
        'implementation_status': 'LOCAL_CHECKS_PASS',
        'independent_verifier_gate': 'PENDING_EXTERNAL_REVIEW',
        'source_commit': _source_commit(),
        'source_files_sha256': _source_hashes(),
        'checks': {'physical_masks_checked': controls_count + hb_k4_count,
                   'control_masks': controls_count, 'HB_K4_masks': hb_k4_count,
                   'H2_supports_certified': h2_supports,
                   'unknown_promoted_to_infeasible': 0},
        'cases': cases,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, help='write NEW evidence file, never overwrite')
    args = parser.parse_args()
    results = verify()
    rendered = canonical_json(results) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x', encoding='utf8') as f:
            f.write(rendered)
    print(rendered, end='')


if __name__ == '__main__':
    main()
