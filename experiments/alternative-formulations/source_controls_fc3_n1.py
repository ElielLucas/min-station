#!/usr/bin/env python3
"""Controles analíticos reproduzíveis da SOURCE F-C3 §§8–9 (N1-T3).

NÃO são sintéticos novos da story 6. Todas as arestas têm peso unitário.
Não pressupor que suas relaxações caibam nos caps da N1.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from ms_utils import construir_arcos_alcance


def _instance_aux(name, vertices, edges, lp_expected, opt_expected):
    S, T = [], []
    V = [f'c_{v}' for v in vertices]
    adj = {v: [] for v in V}
    for i, (u, v) in enumerate(edges):
        s, t = f's_{i}', f't_{i}'
        S.append(s)
        T.append(t)
        V.extend((s, t))
        for terminal in (s, t):
            for candidate in (f'c_{u}', f'c_{v}'):
                adj.setdefault(terminal, []).append((candidate, 1))
                adj.setdefault(candidate, []).append((terminal, 1))
    return S, T, V, adj, construir_arcos_alcance(V, adj, 1), 1, {
        'name': name, 'lp_fc3_expected': float(lp_expected),
        'opt_expected': float(opt_expected),
        'source': 'formulacao-fc3-componentes-trios.md',
    }


def make_source_g2():
    """SOURCE §8: 2 triângulos e ponte a1--a2; n=20, m=7, LP=4."""
    vertices = [f'{p}{i}' for i in (1, 2) for p in 'abc']
    edges = []
    for i in (1, 2):
        edges += [(f'a{i}', f'b{i}'), (f'b{i}', f'c{i}'), (f'c{i}', f'a{i}')]
    edges.append(('a1', 'a2'))
    return _instance_aux('SOURCE-g2', vertices, edges, 4.0, 4.0)


def make_source_c5():
    """SOURCE §9: ciclo de 5 candidatos; n=15, m=5, LP=2.5."""
    vertices = [f'v{i}' for i in range(5)]
    edges = [(f'v{i}', f'v{(i + 1) % 5}') for i in range(5)]
    return _instance_aux('SOURCE-C5', vertices, edges, 2.5, 3.0)


def make_two_components():
    """Controle N1: C={x,y} tem duas componentes, e terceiro par é direto.

    n=8, m=3, G conexo. Ausência de conectividade global entre estações é
    *intencional*: modelos não podem exigir H[C] conexo.
    """
    V = ['s1', 's2', 's3', 't1', 't2', 't3', 'x', 'y']
    S, T = V[:3], V[3:6]
    edges = [('s1', 'x'), ('x', 't1'), ('s2', 'y'), ('y', 't2'),
             ('s3', 't3'), ('t1', 's3'), ('s3', 's2')]
    adj = {v: [] for v in V}
    for u, v in edges:
        adj[u].append((v, 1))
        adj[v].append((u, 1))
    return S, T, V, adj, construir_arcos_alcance(V, adj, 1), 1, {
        'name': 'MultiComp-N1', 'witness_C': ['x', 'y'],
    }
