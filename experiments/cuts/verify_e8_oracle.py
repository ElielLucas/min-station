"""
Verificação do oráculo do E8: integer_oracle (rede restrita S∪T∪C) contra
_build_flow_net_aggregate + _edmonds_karp (rede completa), com C amostrado
sobre V INTEIRO — estações em intermediários, origens e destinos.

Duas baterias:
  1. Exaustiva: todos os 2^|V| subconjuntos C nos gabaritos pequenos, que
     incluem S∩T≠∅ (StayPut, SharedTerminal), relé obrigatório em terminal
     (TermRelay, TermRelayForced) e m=1 (PathM1).
  2. Amostral: C aleatório sobre V nas instâncias reais, mais C = V e C = ∅.

Critério: mesmo veredito de viabilidade; quando inviável, o Z devolvido pelo
oráculo tem de ser um corte válido (is_valid_cut). Z não precisa coincidir
com o da rede completa, porque pode haver mais de um corte mínimo.
"""
import itertools
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

import synthetic as syn
from harness import load_instance
from ms_utils import construir_arcos_alcance
from cuts import (
    build_neighborhoods,
    _build_flow_net_aggregate,
    _edmonds_karp,
    integer_oracle,
    is_valid_cut,
)


def make_PathM1(r=1):
    """Caminho s-a-b-t, um robô (m=1), r=1: OPT=2 (a e b). Exercita κ_terminal=0."""
    S, T, V = ['s'], ['t'], ['s', 'a', 'b', 't']
    edges = [('s', 'a', 1), ('a', 'b', 1), ('b', 't', 1)]
    adj = syn._adj_undirected(edges)
    return S, T, V, adj, construir_arcos_alcance(V, adj, r), r, {'OPT': 2.0}


def oraculo_completo(S, T, A_r, C):
    g, c, _, m = _build_flow_net_aggregate(S, T, A_r, {v: 1.0 for v in C})
    return _edmonds_karp(g, c, '_s', '_t') >= m - 1e-6


def checar(label, S, T, A_r, N_plus, N_minus, amostras):
    ST = set(S) | set(T)
    n = div = inval = com_terminal = 0
    t_ref = t_new = 0.0
    for C in amostras:
        n += 1
        if C & ST:
            com_terminal += 1
        t0 = time.monotonic()
        ref = oraculo_completo(S, T, A_r, C)
        t_ref += time.monotonic() - t0
        t0 = time.monotonic()
        ok, Z = integer_oracle(S, T, N_plus, C)
        t_new += time.monotonic() - t0
        if ok != ref:
            div += 1
            print(f'  DIVERGÊNCIA {label}: |C|={len(C)} ref={ref} novo={ok}')
        elif not ok and not is_valid_cut(S, T, A_r, Z, N_plus, N_minus):
            inval += 1
            print(f'  CORTE INVÁLIDO {label}: C={sorted(C)[:10]} Z={sorted(Z)[:10]}')
    speed = t_ref / t_new if t_new > 1e-9 else float('inf')
    tag = 'OK' if div == inval == 0 else 'FALHOU'
    print(f'{label:<38} {n:>5} casos ({com_terminal} com terminal em C), '
          f'{div} divergências, {inval} cortes inválidos, speedup={speed:.1f}x [{tag}]')
    return div + inval


def main():
    total = 0

    print('=== 1. Exaustiva (todo C ⊆ V) ===')
    for label, fn in [
        ('Direct0', syn.make_Direct0), ('TermRelay', syn.make_TermRelay),
        ('TermRelayForced', syn.make_TermRelayForced), ('Tri', syn.make_Tri),
        ('StayPut', syn.make_StayPut), ('SharedTerminal', syn.make_SharedTerminal),
        ('F1(2,2)', lambda: syn.make_F1(m=2, k=2, r=1)),
        ('F2(k=1)', lambda: syn.make_F2(k=1, L=3, r=1)),
        ('PathM1', make_PathM1),
    ]:
        S, T, V, adj, A_r, r, meta = fn()
        if len(V) > 14:
            print(f'{label:<38} |V|={len(V)} grande demais para exaustivo — pulando')
            continue
        N_plus, N_minus = build_neighborhoods(A_r)
        amostras = [frozenset(c) for k in range(len(V) + 1)
                    for c in itertools.combinations(V, k)]
        total += checar(label, S, T, A_r, N_plus, N_minus, amostras)

    print('\n=== 2. Amostral nas instâncias reais (C sobre V inteiro) ===')
    for fname, R, n_am in [
        ('Chicago_n400_m1130_st15.txt', 7, 200),
        ('Philadelphia_n800_m2404_st_25.txt', 3, 200),
        ('hc9u.txt', None, 30),
        ('cc10-2p.txt', None, 30),
    ]:
        path = ROOT / 'instances' / fname
        if not path.exists():
            print(f'  {fname}: não encontrado — pulando')
            continue
        S, T, V, adj, A_r, r = load_instance(path, R=R)
        N_plus, N_minus = build_neighborhoods(A_r)
        rng = random.Random(42)
        amostras = [frozenset(), frozenset(V)]
        for _ in range(n_am):
            amostras.append(frozenset(rng.sample(V, rng.randint(0, len(V)))))
        total += checar(fname, S, T, A_r, N_plus, N_minus, amostras)

    print()
    if total == 0:
        print('RESULTADO FINAL: 0 divergências, 0 cortes inválidos.')
    else:
        print(f'RESULTADO FINAL: {total} problemas — investigar.')
        sys.exit(1)


if __name__ == '__main__':
    main()
