"""AS14 independent review: oracle vs verifier-owned physical oracle, certificate replay, H2."""
import json
import random
import sys
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
import os
sys.path.insert(0, os.environ.get('AS14_CUTS', str(ROOT / 'experiments/cuts')))
sys.path.insert(0, str(Path(__file__).parent))

from h2_oracle import MatchingOracle, PhysicalInstance, Status, classify_h2  # noqa: E402
from indep_oracle import reach_sets, nu_brute, max_deficiency, viable  # noqa: E402


def inst(V, S, T, edges, r):
    adj = {v: [] for v in V}
    for u, w in edges:
        adj[u].append((w, 1))
        adj[w].append((u, 1))
    return PhysicalInstance(tuple(V), tuple(S), tuple(T), adj, r)


def subsets(V):
    for k in range(len(V) + 1):
        yield from combinations(V, k)


stats = {'cases': 0, 'masks': 0, 'viable': 0, 'infeasible': 0, 'unknown': 0,
         'disagree_status': 0, 'disagree_nu': 0, 'bad_witness': 0, 'bad_hall': 0,
         'h2_supports': 0, 'h2_bhat_mismatch': 0, 'h2_invalid': 0, 'h2_wrong_state': 0,
         'sxt_cases': 0, 'disconnected_cases': 0}
failures = []


def audit(V, S, T, edges, r, do_h2):
    i = inst(V, S, T, edges, r)
    oracle = MatchingOracle()
    stats['cases'] += 1
    if set(S) & set(T):
        stats['sxt_cases'] += 1
    from indep_oracle import bfs_dist
    if len(bfs_dist(V, edges)[V[0]]) < len(V):
        stats['disconnected_cases'] += 1
    physical = []
    for C in subsets(V):
        x = oracle.check(i, C)
        reach = reach_sets(V, S, T, edges, r, C)
        nu = nu_brute(S, T, reach)
        exp = nu == len(S)
        stats['masks'] += 1
        if exp:
            physical.append(set(C))
        if x.status is Status.UNKNOWN:
            stats['unknown'] += 1
            failures.append(('UNKNOWN', V, S, T, edges, r, C, x.reason))
            continue
        stats['viable' if x.status is Status.VIABLE else 'infeasible'] += 1
        if (x.status is Status.VIABLE) != exp:
            stats['disagree_status'] += 1
            failures.append(('STATUS', V, S, T, edges, r, C))
        if x.matching_size != nu:
            stats['disagree_nu'] += 1
            failures.append(('NU', V, S, T, edges, r, C, x.matching_size, nu))
        if x.status is Status.VIABLE:
            ok = (sorted(s for s, _ in x.witness) == sorted(S) and
                  sorted(t for _, t in x.witness) == sorted(T) and
                  all(t in reach[s] for s, t in x.witness))
            if not ok:
                stats['bad_witness'] += 1
                failures.append(('WITNESS', V, S, T, edges, r, C, x.witness))
        else:
            U = set(x.hall_origins)
            N = set().union(*(reach[s] for s in U)) if U else set()
            ok = (U <= set(S) and N == set(x.hall_destinations) and len(N) < len(U)
                  and len(S) - nu == max_deficiency(S, reach))
            if not ok:
                stats['bad_hall'] += 1
                failures.append(('HALL', V, S, T, edges, r, C, x.hall_origins, x.hall_destinations))
    if not do_h2:
        return
    for R in subsets(V):
        F = set(V) - set(R)
        c = classify_h2(oracle, i, R)
        if viable(V, S, T, edges, r, F):
            if c.state != 'NO_CUT':
                stats['h2_wrong_state'] += 1
                failures.append(('H2STATE', V, S, T, edges, r, R, c.state))
            continue
        exp_b = {v for v in R if not viable(V, S, T, edges, r, F | {v})}
        stats['h2_supports'] += 1
        if c.state != 'CERTIFIED' or set(c.Bhat) != exp_b or c.rhs != 2:
            stats['h2_bhat_mismatch'] += 1
            failures.append(('H2BHAT', V, S, T, edges, r, R, c.Bhat, exp_b))
        coef = dict(c.coefficients)
        if set(coef) != set(R):
            stats['h2_invalid'] += 1
        for C in physical:
            if sum(coef.get(v, 0) for v in C) < 2:
                stats['h2_invalid'] += 1
                failures.append(('H2INVALID', V, S, T, edges, r, R, C))
                break


def main():
    rng = random.Random(20261014)
    # Random micrographs with forced S∩T overlap and disconnected graphs.
    for n in range(2, 8):
        V = tuple(f'v{k}' for k in range(n))
        reps = 60 if n <= 5 else 25
        for rep in range(reps):
            p = rng.choice([0.25, 0.4, 0.6])
            edges = [(V[a], V[b]) for a, b in combinations(range(n), 2) if rng.random() < p]
            m = rng.randint(1, min(n, 4))
            S = rng.sample(V, m)
            if rng.random() < 0.6:
                # force overlap: reuse some origins as destinations
                k = rng.randint(1, m)
                T = S[:k] + rng.sample([v for v in V if v not in S[:k]], m - k)
            else:
                T = rng.sample(V, m)
            r = rng.randint(0, 3)
            audit(V, tuple(S), tuple(T), edges, r, do_h2=(n <= 5))
    # Sparse long-path batch: trees/paths with m up to 5, r in 1..2 (many INFEASIBLE masks).
    for n in range(6, 9):
        V = tuple(f'p{k}' for k in range(n))
        for rep in range(20):
            order = list(V)
            rng.shuffle(order)
            edges = [(order[k], order[rng.randrange(k)]) for k in range(1, n)]
            m = rng.randint(2, min(5, n))
            S = rng.sample(V, m)
            k = rng.randint(0, m)
            T = S[:k] + rng.sample([v for v in V if v not in S[:k]], m - k)
            audit(V, tuple(S), tuple(T), edges, rng.randint(1, 2), do_h2=False)
    print(json.dumps(stats, indent=1))
    print('failures', len(failures))
    for f in failures[:10]:
        print(f)


if __name__ == '__main__':
    main()
