"""AS-01: aritmetica exata de testemunhas; nao resolve LP/MIP.

Somente biblioteca padrao. Artefatos historicos e solvers nao sao modificados.
"""
from __future__ import annotations

import unittest
from collections import defaultdict
from fractions import Fraction as Q

ZERO = Q(0)
ONE = Q(1)


def arcs_from_edges(edges):
    return {(u, v) for a, b in edges for u, v in ((a, b), (b, a))}


def sum_flow(arcs, flows, v, incoming):
    return sum((amount for (u, w), amount in flows.items()
                if (w == v if incoming else u == v)), ZERO)


def agg_from_paths(path_weights):
    flows = defaultdict(lambda: ZERO)
    for _source, path, weight in path_weights:
        for u, v in zip(path, path[1:]):
            flows[u, v] += weight
    return dict(flows)


def group_from_paths(groups, S, T, paths):
    """Construir somente testemunhas de caminhos, nao otimizador de A."""
    origin_group = {s: B for B in groups for s in B}
    assert set(origin_group) == set(S)
    f = defaultdict(lambda: ZERO)
    g = defaultdict(lambda: ZERO)
    p = defaultdict(lambda: ZERO)
    h = defaultdict(lambda: ZERO)
    for s, path, weight in paths:
        assert path[0] == s and path[-1] in T
        assert len(set(path)) == len(path)
        B = origin_group[s]
        p[B, path[-1]] += weight
        if len(path) == 1:
            h[B, s] += weight
        for v in path[1:-1]:
            g[B, v] += weight
        for u, v in zip(path, path[1:]):
            f[B, u, v] += weight
    return f, g, p, h


def check_U(V, S, T, arcs, y, f):
    m = len(S)
    assert set(y) == set(V)
    assert all(ZERO <= val <= ONE for val in y.values())
    assert all(pair in arcs and amount >= 0 for pair, amount in f.items())
    for v in V:
        inside = sum_flow(arcs, f, v, incoming=True)
        outside = sum_flow(arcs, f, v, incoming=False)
        a = int(v in S)
        b = int(v in T)
        assert outside - inside == a - b, ('balance', v)
        assert inside <= b + (m-b) * y[v], ('U incoming activation', v)
        assert outside <= a + (m-a) * y[v], ('U outgoing activation', v)


def check_A(V, S, T, arcs, groups, y, f, g, p, h, *, require_global=True):
    assert set.union(*(set(B) for B in groups)) == set(S)
    assert sum(map(len, groups)) == len(S)
    m = len(S)
    assert all(ZERO <= val <= ONE for val in y.values())
    for B in groups:
        for v in V:
            inn = sum((amount for (grp, u, w), amount in f.items()
                       if grp == B and w == v), ZERO)
            out = sum((amount for (grp, u, w), amount in f.items()
                       if grp == B and u == v), ZERO)
            hval = h.get((B, v), ZERO)
            pval = p.get((B, v), ZERO)
            gval = g.get((B, v), ZERO)
            assert not hval or (v in B and v in T)
            assert not pval or v in T
            assert ZERO <= hval <= ONE and ZERO <= pval <= ONE and gval >= ZERO
            assert inn + hval == pval + gval, ('A1', B, v)
            assert out + hval == int(v in B) + gval, ('A2', B, v)
            c_Bv = len(B) - int(v in B)
            assert gval <= c_Bv * y[v], ('A4', B, v)
    for t in T:
        assert sum((p.get((B, t), ZERO) for B in groups), ZERO) == ONE, ('A3', t)
    if require_global:
        for v in V:
            kappa = m - 1 if v in S or v in T else m
            assert sum((g.get((B, v), ZERO) for B in groups), ZERO) <= kappa * y[v], ('A5', v)


def check_T18(V, S, T, arcs, y, p, f):
    """Restricoes historicas desagregacao.py com variaveis relaxadas."""
    assert all(ZERO <= val <= ONE for val in y.values())
    assert all(ZERO <= val <= ONE for val in f.values())
    assert all(ZERO <= val <= ONE for val in p.values())
    for s in S:
        assert sum((p.get((s, t), ZERO) for t in T), ZERO) == ONE
    for t in T:
        assert sum((p.get((s, t), ZERO) for s in S), ZERO) == ONE
    for s in S:
        sf = {(u, v): amount for (source, u, v), amount in f.items() if source == s}
        for v in V:
            inn = sum_flow(arcs, sf, v, True)
            out = sum_flow(arcs, sf, v, False)
            demand = p.get((s, v), ZERO) if v in T else ZERO
            assert out - inn == int(v == s) - demand, ('T18 balance', s, v)
            assert inn <= (demand + y[v] if v in T else y[v]), ('T18 in', s, v)
            assert out <= (ONE if v == s else y[v]), ('T18 out', s, v)


class AS01RationalWitness(unittest.TestCase):
    def test_star_T18_feasible_but_U_aggregate_activation_violated(self):
        V = {'a', 'b', 'c', 'd'}
        S, T = {'a', 'b'}, {'c', 'd'}
        arcs = arcs_from_edges({('a', 'c'), ('b', 'c'), ('c', 'd')})
        y = {v: (Q(1, 2) if v == 'c' else ZERO) for v in V}
        p = {(s, t): Q(1, 2) for s in S for t in T}
        f = {('a', 'a', 'c'): ONE, ('a', 'c', 'd'): Q(1, 2),
             ('b', 'b', 'c'): ONE, ('b', 'c', 'd'): Q(1, 2)}
        check_T18(V, S, T, arcs, y, p, f)
        aggregate = defaultdict(lambda: ZERO)
        for (_, u, v), value in f.items():
            aggregate[u, v] += value
        with self.assertRaisesRegex(AssertionError, 'U incoming activation'):
            check_U(V, S, T, arcs, y, aggregate)
        self.assertEqual(sum(y.values()), Q(1, 2))
        self.assertEqual(sum_flow(arcs, aggregate, 'c', True), Q(2))
        self.assertEqual(Q(1) + y['c'], Q(3, 2))

    def test_star_U_has_feasible_one_station_witness(self):
        V = {'a', 'b', 'c', 'd'}
        S, T = {'a', 'b'}, {'c', 'd'}
        arcs = arcs_from_edges({('a', 'c'), ('b', 'c'), ('c', 'd')})
        y = {v: (ONE if v == 'c' else ZERO) for v in V}
        check_U(V, S, T, arcs, y,
                agg_from_paths([('a', ('a', 'c'), ONE), ('b', ('b', 'c', 'd'), ONE)]))
        self.assertEqual(sum(y.values()), ONE)

    def test_star_A5_blocks_same_fractional_T18_point(self):
        V = {'a', 'b', 'c', 'd'}
        S, T = {'a', 'b'}, {'c', 'd'}
        arcs = arcs_from_edges({('a', 'c'), ('b', 'c'), ('c', 'd')})
        groups = (frozenset({'a'}), frozenset({'b'}))
        paths = [(s, (s, 'c'), Q(1, 2)) for s in S] + [
            (s, (s, 'c', 'd'), Q(1, 2)) for s in S]
        y = {v: (Q(1, 2) if v == 'c' else ZERO) for v in V}
        f, g, p, h = group_from_paths(groups, S, T, paths)
        check_A(V, S, T, arcs, groups, y, f, g, p, h, require_global=False)
        with self.assertRaisesRegex(AssertionError, 'A5'):
            check_A(V, S, T, arcs, groups, y, f, g, p, h)

    def test_sec59_U_and_A2_exact_primal_witness(self):
        V = {'s1', 's2', 's3', 't1', 't2', 't3'} | {f'w{i}' for i in range(1, 8)}
        S, T = {'s1', 's2', 's3'}, {'t1', 't2', 't3'}
        edges = {('s1','t1'), ('s2','t1'), ('s1','w1'), ('s2','w1'),
                 ('w7','t2'), ('t2','s3'), ('s3','t3')}
        edges |= {(f'w{i}', f'w{i+1}') for i in range(1, 7)}
        arcs = arcs_from_edges(edges)
        paths = [('s1', ('s1','t1'), Q(1,2)),
                 ('s2', ('s2','t1'), Q(1,2)),
                 ('s1', ('s1', *(f'w{i}' for i in range(1,8)), 't2'), Q(1,2)),
                 ('s2', ('s2', *(f'w{i}' for i in range(1,8)), 't2'), Q(1,2)),
                 ('s3', ('s3','t3'), ONE)]
        u_y = {v: (ONE if v in ('w1','w7') else Q(1,3) if v.startswith('w') else ZERO)
               for v in V}
        check_U(V, S, T, arcs, u_y, agg_from_paths(paths))
        self.assertEqual(sum(u_y.values()), Q(11,3))
        a_y = {v: (ONE if v in ('w1','w7') else Q(1,2) if v.startswith('w') else ZERO)
               for v in V}
        groups = (frozenset({'s1','s2'}), frozenset({'s3'}))
        f, g, p, h = group_from_paths(groups, S, T, paths)
        check_A(V, S, T, arcs, groups, a_y, f, g, p, h)
        self.assertEqual(sum(a_y.values()), Q(9,2))
        self.assertGreater(sum(a_y.values()), sum(u_y.values()))
        for y in (u_y, a_y):
            self.assertGreaterEqual(y['t1'] + y['w1'], ONE)
            self.assertGreaterEqual(y['s3'] + y['w7'], ONE)
        self.assertEqual({g[groups[0],f'w{i}'] for i in range(1,8)}, {ONE})

    def test_one_group_overlap_lift_when_zero_incoming(self):
        V, S, T = {'a', 'v', 'b'}, {'a', 'v'}, {'v', 'b'}
        arcs = arcs_from_edges({('a','v'), ('v','b')})
        paths = [('a', ('a','v'), ONE), ('v',('v','b'),ONE)]
        y = {v:ZERO for v in V}
        check_U(V,S,T,arcs,y,agg_from_paths(paths))
        groups=(frozenset(S),)
        f,g,p,h=group_from_paths(groups,S,T,paths)
        check_A(V,S,T,arcs,groups,y,f,g,p,h)

    def test_one_group_overlap_lift_when_incoming_exceeds_one(self):
        # Solucao viavel da U com ciclo fracionario/integral e overlap.
        # Testa a parte g=max(0,in-1) do levantamento, nao so h.
        V, S, T = {'a', 'v', 'b'}, {'a', 'v'}, {'v', 'b'}
        arcs = arcs_from_edges({('a', 'v'), ('v', 'b')})
        F = {('a','v'):Q(2), ('v','a'):ONE, ('v','b'):ONE}
        y = {'a':ONE, 'v':ONE, 'b':ZERO}
        check_U(V,S,T,arcs,y,F)
        B=frozenset(S)
        f={(B,u,w):val for (u,w),val in F.items()}
        g={(B,'a'):ONE, (B,'v'):ONE, (B,'b'):ZERO}
        h={}
        p={(B,'v'):ONE,(B,'b'):ONE}
        check_A(V,S,T,arcs,(B,),y,f,g,p,h)

    def test_zero_length_stay_put(self):
        V, S, T = {'a'}, {'a'}, {'a'}
        groups=(frozenset(S),)
        paths=[('a',('a',),ONE)]
        f,g,p,h=group_from_paths(groups,S,T,paths)
        check_A(V,S,T,set(),groups,{'a':ZERO},f,g,p,h)
        self.assertEqual(h[groups[0], 'a'], ONE)

    def test_partial_partition_is_rejected(self):
        with self.assertRaises(AssertionError):
            check_A({'a','b'}, {'a','b'}, {'a','b'}, set(), (frozenset({'a'}),),
                    {'a':ZERO, 'b':ZERO}, {},{},{},{})

    def test_integer_station_failure_blocks_unpaid_transit(self):
        V={'a','b','c','d'}
        S,T={'a','b'},{'c','d'}
        arcs=arcs_from_edges({('a','c'),('b','c'),('c','d')})
        groups=(frozenset(S),)
        paths=[('a',('a','c'),ONE),('b',('b','c','d'),ONE)]
        f,g,p,h=group_from_paths(groups,S,T,paths)
        with self.assertRaisesRegex(AssertionError,'A4'):
            check_A(V,S,T,arcs,groups,{v:ZERO for v in V},f,g,p,h)


if __name__=='__main__':
    unittest.main()
