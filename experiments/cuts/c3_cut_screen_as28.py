"""AS28: orçamento explícito e certificado estrutural para C3-cut existente.

Este arquivo NAO altera a familia C3; apenas usa as rotinas historicas de
max-flow/min-cut sobre um subconjunto congelado de origens/destinos. A
selecao limitada nao constitui separacao global exaustiva.
"""
from __future__ import annotations

import hashlib
import time
from collections import deque

from experiments.cuts.cuts import _build_flow_net, _edmonds_karp, _reachable_set


def select_terminals(terminals, case_name, side, limit):
    """Amostra deterministica independente da solucao LP (sem tuning por caso)."""
    if limit < 0:
        raise ValueError('INVALID_INPUT: limit must be nonnegative')
    distinct = sorted(set(terminals))
    return tuple(sorted(distinct, key=lambda v: (
        hashlib.sha256(f'AS28|{case_name}|{side}|{v}'.encode()).hexdigest(), v
    ))[:limit])


def _hits_all_paths(root, sinks, arcs, support):
    """Certificado independente do residual: nenhum caminho sem Z alcanca sink."""
    if root in support or root in sinks:
        return False
    nxt = {}
    for u, v in arcs:
        nxt.setdefault(u, []).append(v)
    visited = {root}
    q = deque([root])
    while q:
        u = q.popleft()
        for v in nxt.get(u, ()):
            if v in support or v in visited:
                continue
            if v in sinks:
                return False
            visited.add(v)
            q.append(v)
    return True


def _one_terminal(root, sinks, arcs, y_star, side, min_violation):
    """Um maxflow no grafo original ou reverso; rejeita cut sem certificado."""
    forward = list(arcs) if side == 'origin' else [(v, u) for u, v in arcs]
    # A rotina historica recebe a propria origem do fluxo e destinos livres.
    graph, cap, vertices = _build_flow_net(root, set(), set(sinks), forward, y_star)
    flow = _edmonds_karp(graph, cap, '_s', '_t')
    if flow >= 1.0 - min_violation:
        return {'status': 'NO_VIOLATION', 'min_flow': float(flow), 'cut': None}
    reachable = _reachable_set(graph, cap, '_s')
    Z = frozenset(v for v in vertices if v != root
                  and f'{v}_in' in reachable and f'{v}_out' not in reachable)
    if not Z:
        # Nenhuma cobertura validavel: possivel inviabilidade estrutural.
        return {'status': 'EMPTY_CUT', 'min_flow': float(flow), 'cut': None}
    if not _hits_all_paths(root, set(sinks), forward, Z):
        return {'status': 'CERTIFICATE_FAILED', 'min_flow': float(flow), 'cut': None}
    y_sum = sum(float(y_star.get(v, 0.)) for v in Z)
    if y_sum >= 1.0 - min_violation:
        return {'status': 'NUMERICAL_AMBIGUITY', 'min_flow': float(flow), 'cut': None}
    return {'status': 'VIOLATED', 'min_flow': float(flow), 'cut': tuple(sorted(Z)),
            'lhs': y_sum, 'violation': 1.0-y_sum}


def screen_c3(S, T, arcs, y_star, *, case_name, sources_per_side=8,
              min_violation=1e-6, max_cuts=16, max_seconds=12., seen=()):
    """Seleciona ate N fontes por lado. Maxflow indivisivel: hard timeout e externo.

    Retorna status PARTIAL quando interrompe por tempo/orcamento. A ausencia
    de violacao nesta amostra NAO prova fechamento global C3.
    """
    if sources_per_side < 0 or max_cuts < 0 or max_seconds < 0:
        raise ValueError('INVALID_INPUT: negative budget')
    if not 0 < min_violation < 0.01:
        raise ValueError('INVALID_INPUT: min_violation')
    start = time.monotonic()
    source = select_terminals(S, case_name, 'origin', sources_per_side)
    destination = select_terminals(T, case_name, 'destination', sources_per_side)
    total = len(source)+len(destination)
    examined, violated, duplicates, rows = 0, 0, 0, []
    existing = {tuple(c) for c in seen}
    stopped = None
    for side, terms, sinks in (('origin', source, T), ('destination', destination, S)):
        for vertex in terms:
            if time.monotonic()-start >= max_seconds:
                stopped = 'TIME_BUDGET'
                break
            if len(rows) >= max_cuts:
                stopped = 'CUT_BUDGET'
                break
            result = _one_terminal(vertex, sinks, arcs, y_star, side, min_violation)
            examined += 1
            if result['status'] in ('EMPTY_CUT', 'CERTIFICATE_FAILED', 'NUMERICAL_AMBIGUITY'):
                stopped = result['status']
                break
            if result['status'] == 'VIOLATED':
                violated += 1
                if result['cut'] in existing:
                    duplicates += 1
                else:
                    existing.add(result['cut'])
                    rows.append({'side': side, 'terminal': vertex,
                                 'support': result['cut'], 'lhs': result['lhs'],
                                 'violation': result['violation'],
                                 'min_flow': result['min_flow']})
        if stopped:
            break
    return {'status': 'COMPLETE_SELECTED' if stopped is None else 'PARTIAL_'+stopped,
            'candidate_terminals': total, 'examined_terminals': examined,
            'violated_terminals': violated, 'duplicates': duplicates,
            'emitted': len(rows), 'rows': rows,
            'elapsed_s': time.monotonic()-start,
            'source_terminals': source, 'destination_terminals': destination,
            'global_c3_closed': False}
