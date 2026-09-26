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


def reverse_delete(S, T, V, N_plus, order, deadline=None, C0=None):
    """
    Parte de C = C0 (padrão V) e remove, na ordem dada, cada vértice cuja
    ausência mantém a viabilidade. Se `deadline` (time.monotonic()) for
    atingido, devolve o C corrente, que continua viável.

    Retorna frozenset(C), ou None se C0 for inviável (com C0 = V: instância
    inviável).
    """
    C = set(V if C0 is None else C0)
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


def greedy_augment(S, T, V, N_plus, deadline=None, C0=None):
    """
    H3 (direcoes-pli-min-station.md §11): aumento guloso a partir de C = C0
    (padrão ∅). Com C0 = solução do núcleo de cobertura, é o reparo do E10b.

    A cada passo, se C é inviável, `integer_oracle` devolve um corte
    testemunha Z (candidatos que resolveriam esse corte específico). H3
    literal avaliaria o ganho marginal de TODO v ∈ V a cada passo — o mesmo
    custo que travou o start guloso original (O(n) avaliações × O(n) passos
    sobre a rede completa, antes de `integer_oracle` existir). Aqui a busca
    a cada passo fica restrita a v ∈ Z: são os únicos candidatos que
    resolvem aquele corte específico (Z ∩ C = ∅ para C inteiro, §5.5).
    Escolhe o de maior grau de saída em A_r (heurística, sem garantia).

    A versão usada no E10 desempatava primeiro pelo número de cortes já
    vistos em que v aparecia; medido depois, isso gerava C 2–2,5× maior e
    4–10× mais lento (mapf-room-m10: 574 vs. 233 estações) — ver
    resultados-e9-e10-pli.md.

    Retorna frozenset(C), viável ao final (para no prazo mesmo que ainda
    inviável — quem chama deve checar com integer_oracle se precisar).
    """
    C = set(C0 or ())
    while deadline is None or time.monotonic() < deadline:
        viavel, Z = integer_oracle(S, T, N_plus, C)
        if viavel:
            break
        C.add(max(Z, key=lambda v: len(N_plus.get(v, ()))))
    return frozenset(C)


def build_primal_h3(S, T, V, N_plus, seed=42, construct_budget=20.0,
                    local_search_budget=40.0, total_budget=60.0):
    """
    H3 (aumento guloso a partir de C=∅) seguido de H6 (busca local
    drop/add/swap, `_swap_pass`). Alternativa a `build_primal_solution`
    (reverse-delete a partir de C=V), pensada para instâncias grandes onde
    o reverse-delete gasta o orçamento inteiro sem terminar (E8 §7, item 3).

    Retorna dict no mesmo formato de `build_primal_solution`, ou None se a
    construção não atingiu viabilidade dentro do prazo.
    """
    rng = random.Random(seed)
    t0 = time.monotonic()
    deadline_constr = t0 + construct_budget
    deadline_total = t0 + total_budget

    C = greedy_augment(S, T, V, N_plus, deadline=deadline_constr)
    viavel, _ = integer_oracle(S, T, N_plus, C)
    if not viavel:
        return None

    ls_deadline = min(deadline_total, time.monotonic() + local_search_budget)
    if time.monotonic() < ls_deadline:
        C = _swap_pass(S, T, V, N_plus, C, rng, ls_deadline)

    ST = set(S) | set(T)
    return {
        'y_bin': {v: (1.0 if v in C else 0.0) for v in V},
        'C': C,
        'n_estacoes': len(C),
        'tempo_s': time.monotonic() - t0,
        'n_ordens_testadas': 1,
        'n_terminais_em_C': len(C & ST),
    }


def build_primal_from_core(S, T, V, N_plus, C0, seed=42, total_budget=120.0):
    """
    E10b: repara uma solução do núcleo de cobertura (C0, em geral inviável
    no problema real e do tamanho do LB) até a viabilidade, poda os vértices
    redundantes e aplica busca local. É o item 3 adiado do E8: partir de um
    C pequeno em vez de C = V (reverse-delete) ou C = ∅ (H3).

    Retorna dict com o C final e o tamanho após cada fase, ou None se o
    reparo não atingiu a viabilidade no prazo.
    """
    rng = random.Random(seed)
    t0 = time.monotonic()
    deadline = t0 + total_budget

    C = greedy_augment(S, T, V, N_plus, deadline=deadline, C0=C0)
    if not integer_oracle(S, T, N_plus, C)[0]:
        return None
    n_reparo, t_reparo = len(C), time.monotonic() - t0

    ordem = list(C)
    rng.shuffle(ordem)
    C = reverse_delete(S, T, V, N_plus, ordem, deadline=deadline, C0=C)
    n_poda = len(C)

    if time.monotonic() < deadline:
        C = _swap_pass(S, T, V, N_plus, C, rng, deadline)

    return {
        'C': C,
        'n_nucleo': len(C0),
        'n_reparo': n_reparo,
        'n_poda': n_poda,
        'n_estacoes': len(C),
        't_reparo_s': t_reparo,
        'tempo_s': time.monotonic() - t0,
    }


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
