"""AS14 R2 review: adversarial budget/cache/H2 checks against the reviewer-owned physical oracle.

Invariants checked:
  I1 certified (VIABLE/INFEASIBLE) result => elapsed_wall_s < budget_s and status == physical truth;
  I2 UNKNOWN never carries matching_size / certificate and never enters the cache;
  I3 one oracle (one cache) shared across many instances never returns another instance's answer;
  I4 classify_h2 under any clock: Bhat only contains vertices physically certified infeasible,
     and the emitted cut is valid on every physically feasible installation.
"""
import os
import random
import sys
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, os.environ.get('AS14_CUTS', str(ROOT / 'experiments/cuts')))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'verifier-r1'))

from h2_oracle import MatchingOracle, PhysicalInstance, Status, classify_h2  # noqa: E402
from indep_oracle import reach_sets, nu_brute, viable  # noqa: E402

fail = []
count = {'budget_checks': 0, 'certified_in_budget': 0, 'unknown': 0, 'shared_cache_masks': 0,
         'shared_cache_hits': 0, 'h2_runs': 0, 'h2_certified': 0}


def inst(V, S, T, E, r):
    adj = {v: [] for v in V}
    for u, w in E:
        adj[u].append((w, 1))
        adj[w].append((u, 1))
    return PhysicalInstance(tuple(V), tuple(S), tuple(T), adj, r)


def truth(V, S, T, E, r, C):
    return nu_brute(S, T, reach_sets(V, S, T, E, r, C)) == len(S)


class OffsetJump:
    """Monotonic: base until read k, then base+delta forever."""
    def __init__(self, base, k, delta):
        self.n, self.base, self.k, self.delta = 0, base, k, delta

    def __call__(self):
        self.n += 1
        return self.base + (self.delta if self.k is not None and self.n >= self.k else 0.0)


class Step:
    def __init__(self, dt):
        self.n, self.dt = 0, dt

    def __call__(self):
        self.n += 1
        return 1000.0 + self.n * self.dt


def check_answer(x, budget, exp, tag):
    count['budget_checks'] += 1
    if x.status is Status.UNKNOWN:
        count['unknown'] += 1
        if x.matching_size is not None or x.witness or x.hall_origins:
            fail.append(('UNKNOWN_WITH_CERT', tag))
        return
    if budget is not None and not x.elapsed_wall_s < budget:
        fail.append(('CERT_OVER_BUDGET', tag, x.elapsed_wall_s, budget))
    if (x.status is Status.VIABLE) != exp:
        fail.append(('CERT_WRONG', tag, x.status))
    count['certified_in_budget'] += 1


CASES = [  # (V, S, T, E, r, C)  one VIABLE and one INFEASIBLE per topology
    (tuple('abc'), ('a',), ('c',), [('a', 'b'), ('b', 'c')], 1, ('b',)),
    (tuple('abc'), ('a',), ('c',), [('a', 'b'), ('b', 'c')], 1, ()),
    ((1, 2, '1', '2'), (1,), ('2',), [(1, 2), ('1', '2'), (2, '1')], 1, (2,)),
    (('s1', 's2', 't1', 't2'), ('s1', 's2'), ('t1', 't2'), [('s1', 't1'), ('s2', 't1')], 1, ()),
]


def budget_sweeps():
    for V, S, T, E, r, C in CASES:
        i = inst(V, S, T, E, r)
        exp = truth(V, S, T, E, r, C)
        for budget in (0.0, 1e-9, 0.5, 1.0, 10.0):
            for delta in (budget, budget - 1e-12 if budget else 0.0, budget + 1e-12, 100.0):
                for k in list(range(1, 25)) + [None]:
                    # fresh path
                    x = MatchingOracle(clock=OffsetJump(1000.0, k, delta)).check(i, C, budget_s=budget)
                    check_answer(x, budget, exp, ('fresh', V, C, budget, delta, k))
                    # cache-hit path (cache warmed without budget)
                    o = MatchingOracle()
                    o.check(i, C)
                    o.clock = OffsetJump(1000.0, k, delta)
                    x = o.check(i, C, budget_s=budget)
                    check_answer(x, budget, exp, ('cache', V, C, budget, delta, k))
                    if x.status is not Status.UNKNOWN and not x.cache_hit:
                        fail.append(('CACHE_MISS_UNEXPECTED', V, C))
            for dt in (0.001, 0.1, 0.25, 1.0):
                for path in ('fresh', 'cache'):
                    o = MatchingOracle()
                    if path == 'cache':
                        o.check(i, C)
                    o.clock = Step(dt)
                    x = o.check(i, C, budget_s=budget)
                    check_answer(x, budget, exp, ('step', path, V, C, budget, dt))
        # repeated calls with different budgets on one oracle
        o = MatchingOracle(clock=Step(0.1))
        seq = [None, 0.0, 0.05, 0.3, None, 0.0, 100.0]
        for b in seq:
            before = len(o.cache)
            x = o.check(i, C, budget_s=b)
            check_answer(x, b, exp, ('repeat', V, C, b))
            if x.status is Status.UNKNOWN and len(o.cache) != before:
                fail.append(('UNKNOWN_CACHED', V, C, b))


def shared_cache():
    rng = random.Random(14_2)
    o = MatchingOracle()   # one cache across all instances
    pool = []
    for n in range(2, 7):
        for rep in range(25):
            labels = [rng.choice([k, str(k)]) for k in range(n)]
            if len(set(map(str, labels))) < n:
                continue
            V = tuple(labels)
            E = [(V[a], V[b]) for a, b in combinations(range(n), 2) if rng.random() < 0.4]
            m = rng.randint(1, min(3, n))
            S = tuple(rng.sample(V, m))
            T = tuple(S[:rng.randint(0, m)])
            T = T + tuple(rng.sample([v for v in V if v not in T], m - len(T)))
            pool.append((V, S, T, E, rng.randint(0, 2)))
    # also same graph, different r / terminals / str-vs-int copies, to stress identity
    pool += [(('1', '2', 1, 2), (1,), (2,), [(1, 2)], 1), (('1', '2', 1, 2), (1,), (2,), [('1', '2')], 1),
             (tuple('abc'), ('a',), ('c',), [('a', 'b'), ('b', 'c')], 1),
             (tuple('abc'), ('a',), ('c',), [('a', 'b'), ('b', 'c')], 2),
             (tuple('abc'), ('b',), ('c',), [('a', 'b'), ('b', 'c')], 1)]
    for rnd in range(2):  # second round: mostly cache hits, interleaved order
        order = list(pool)
        rng.shuffle(order)
        for V, S, T, E, r in order:
            i = inst(V, S, T, E, r)
            for k in range(len(V) + 1):
                for C in combinations(V, k):
                    x = o.check(i, C)
                    count['shared_cache_masks'] += 1
                    count['shared_cache_hits'] += int(x.cache_hit)
                    if x.status is Status.UNKNOWN or (x.status is Status.VIABLE) != truth(V, S, T, E, r, C):
                        fail.append(('SHARED_CACHE', V, S, T, E, r, C, x.status, x.cache_hit))


def h2_under_clocks():
    rng = random.Random(2026_10_15)
    for rep in range(60):
        n = rng.randint(3, 5)
        V = tuple(f'v{k}' for k in range(n))
        E = [(V[a], V[b]) for a, b in combinations(range(n), 2) if rng.random() < 0.45]
        m = rng.randint(1, 2)
        S = tuple(rng.sample(V, m))
        T = tuple(rng.sample(V, m))
        r = rng.randint(1, 2)
        i = inst(V, S, T, E, r)
        physical = [set(C) for k in range(n + 1) for C in combinations(V, k) if viable(V, S, T, E, r, set(C))]
        for k in range(1, n + 1):
            for R in combinations(V, k):
                for clock_kind in ('none', 'step', 'jump'):
                    o = MatchingOracle()
                    budget = None
                    if clock_kind == 'step':
                        o.clock, budget = Step(0.01), rng.choice([0.05, 0.2, 1.0])
                    elif clock_kind == 'jump':
                        o.clock, budget = OffsetJump(5.0, rng.randint(1, 40), 50.0), 10.0
                    c = classify_h2(o, i, R, budget_s=budget)
                    count['h2_runs'] += 1
                    F = set(V) - set(R)
                    if c.state != 'CERTIFIED':
                        if c.state == 'NO_CUT' and not viable(V, S, T, E, r, F):
                            fail.append(('H2_NO_CUT_WRONG', V, R))
                        continue
                    count['h2_certified'] += 1
                    if viable(V, S, T, E, r, F):
                        fail.append(('H2_CERT_ON_VIABLE_COMPLEMENT', V, R))
                    for v in c.Bhat:
                        if viable(V, S, T, E, r, F | {v}):
                            fail.append(('H2_BHAT_FALSE', V, R, v))
                    coef = dict(c.coefficients)
                    for C in physical:
                        if sum(coef.get(v, 0) for v in C) < 2:
                            fail.append(('H2_CUT_INVALID', V, R, C))
                            break


if __name__ == '__main__':
    budget_sweeps()
    shared_cache()
    h2_under_clocks()
    print(count)
    print('failures', len(fail))
    for f in fail[:10]:
        print(f)
    sys.exit(1 if fail else 0)
