"""
Heurística primal por oráculo (E8): reverse-delete + busca local por troca,
usando `integer_oracle` (rede restrita S∪T∪C, cuts.py).

Candidatos a estação são todos os vértices de V, inclusive origens e
destinos, como no baseline (y_v definido para todo v ∈ V). Uma versão
anterior restringia os candidatos a V∖(S∪T); isso falhava em instâncias cujo
ótimo exige estação em terminal (gabaritos TermRelay e SharedTerminal:
devolvia None) e enviesava o start nas demais.

Invariante: C é viável do início ao fim. O ponto de partida é C = V, viável
se e somente se a instância é viável. Por isso a construção pode ser
interrompida por prazo a qualquer momento sem perder a viabilidade.
"""

import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

from cuts import integer_oracle


def reverse_delete(S, T, V, N_plus, order, deadline=None):
    """
    Parte de C = V e remove, na ordem dada, cada vértice cuja ausência mantém
    a viabilidade. Se `deadline` (time.monotonic()) for atingido, devolve o C
    corrente, que continua viável.

    Retorna frozenset(C), ou None se a instância for inviável (C = V inviável).
    """
    C = set(V)
    viavel0, _ = integer_oracle(S, T, N_plus, C)
    if not viavel0:
        return None

    for v in order:
        if deadline is not None and time.monotonic() > deadline:
            break
        if v not in C:
            continue
        C.discard(v)
        viavel, _ = integer_oracle(S, T, N_plus, C)
        if not viavel:
            C.add(v)

    return frozenset(C)


def _swap_pass(S, T, V, N_plus, C, rng, deadline):
    """
    Busca local first-improvement: remove dois vértices de C; se ficar
    inviável, tenta um substituto de V∖C. Aceita a primeira melhora e
    recomeça. Para no prazo ou sem melhora.
    """
    C = set(C)
    while time.monotonic() < deadline:
        c_list = list(C)
        if len(c_list) < 2:
            break
        rng.shuffle(c_list)
        melhorou = False

        for i in range(len(c_list)):
            if melhorou or time.monotonic() > deadline:
                break
            a = c_list[i]
            for j in range(i + 1, len(c_list)):
                if melhorou or time.monotonic() > deadline:
                    break
                b = c_list[j]
                C2 = C - {a, b}
                if integer_oracle(S, T, N_plus, C2)[0]:
                    C, melhorou = C2, True
                    break
                for w in V:
                    if w in C2 or w in (a, b):
                        continue
                    if time.monotonic() > deadline:
                        break
                    if integer_oracle(S, T, N_plus, C2 | {w})[0]:
                        C, melhorou = C2 | {w}, True
                        break

        if not melhorou:
            break

    return frozenset(C)


def build_primal_solution(S, T, V, N_plus, seed=42, n_orders=5,
                          local_search_budget=10.0, total_budget=60.0):
    """
    Melhor solução viável encontrada em até `total_budget` segundos: várias
    ordens aleatórias de reverse-delete, cada uma seguida de busca local.

    A primeira ordem sempre roda até o fim do reverse-delete ou até o prazo,
    então há sempre uma solução se a instância for viável.

    Retorna dict (y_bin, C, n_estacoes, tempo_s, n_ordens_testadas,
    n_terminais_em_C) ou None se a instância for inviável.
    """
    rng = random.Random(seed)
    t0 = time.monotonic()
    deadline = t0 + total_budget
    best_C = None
    n_ordens = 0

    for _ in range(n_orders):
        if best_C is not None and time.monotonic() > deadline:
            break
        order = list(V)
        rng.shuffle(order)

        C = reverse_delete(S, T, V, N_plus, order, deadline=deadline)
        if C is None:
            return None
        n_ordens += 1

        ls_deadline = min(deadline, time.monotonic() + local_search_budget)
        if time.monotonic() < ls_deadline:
            C = _swap_pass(S, T, V, N_plus, C, rng, ls_deadline)

        if best_C is None or len(C) < len(best_C):
            best_C = C

    ST = set(S) | set(T)
    return {
        'y_bin': {v: (1.0 if v in best_C else 0.0) for v in V},
        'C': best_C,
        'n_estacoes': len(best_C),
        'tempo_s': time.monotonic() - t0,
        'n_ordens_testadas': n_ordens,
        'n_terminais_em_C': len(best_C & ST),
    }
