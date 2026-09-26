"""
Pré-processamento experimental (E8, Bloco 3): dominância de vizinhança,
vértices mortos e obrigatórios. Não faz parte da formulação base — é uma
redução opcional aplicada antes de resolver, testada por igualdade de OPT.

Justificativa (dominância). Seja u um vértice não terminal e w ≠ u com
N⁺(u) ⊆ N⁺(w) e N⁻(u) ⊆ N⁻(w) (todo vértice alcançável a partir de u em
A_r também é alcançável a partir de w, e todo vértice que alcança u também
alcança w). Qualquer robô que usa u como estação de recarga pode usar w no
lugar: todo destino que u alcançaria a partir dali, w também alcança: e
todo trecho que chegava a u chegando por N⁻(u) também chega a w por
N⁻(w) ⊇ N⁻(u). Logo existe sempre uma solução ótima com y_u = 0 sempre que
w (com y_w=1 ou substituível) domina u — fixar y_u = 0 não perde nenhuma
solução ótima. Só não terminais são candidatos a u, porque terminais
carregam arcos próprios (σ→v_out, v_in→τ) que não se transferem para outro
vértice. Um terminal pode ser o dominador w apenas com m ≥ 2: com m = 1 sua
capacidade de trânsito é κ = m−1 = 0 e ele não substitui u como relé.

Obrigatórios: v é obrigatório se V∖{v} (todos os outros vértices, inclusive
terminais, com estação) é inviável. Uma versão anterior testava só os não
terminais; isso marcava vértices como obrigatórios sem que fossem (o ótimo
podia usar um terminal) e piorava o OPT — contraexemplo no gabarito
TermRelayForced: OPT 1 virava 2.
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

from cuts import build_neighborhoods, integer_oracle


def find_dominated(S, T, V, N_plus, N_minus):
    """
    Retorna o conjunto de vértices não terminais u para os quais existe
    w ≠ u (não terminal ou terminal) com N⁺(u) ⊆ N⁺(w) e N⁻(u) ⊆ N⁻(w).
    Em empate exato (mesma vizinhança nos dois sentidos, "gêmeos"), mantém
    um representante por classe (não marca todos como dominados).

    Varre todo w ∈ V para cada candidato u — uma primeira versão restringia
    a busca aos vizinhos de u (assumindo que um dominador teria de ser
    vizinho), mas isso é falso: medido em Chicago st15, a busca restrita
    achava 0 dominados contra 15 da busca completa (w fora da vizinhança de
    u também pode satisfazer N⁺(u)⊆N⁺(w) e N⁻(u)⊆N⁻(w)). A busca completa é
    O(|candidatos|·|V|), mas rápida na prática (Chicago: 0,05s) porque a
    comparação de conjuntos tem saída antecipada.
    """
    S_set, T_set = set(S), set(T)
    candidatos = [v for v in V if v not in S_set | T_set]
    terminal_pode_dominar = len(S) >= 2

    P = {v: frozenset(N_plus.get(v, ())) for v in V}
    M = {v: frozenset(N_minus.get(v, ())) for v in V}

    ordem = {v: i for i, v in enumerate(V)}
    dominados = set()

    for u in candidatos:
        Pu, Mu = P[u], M[u]
        for w in V:
            if w == u:
                continue
            if not terminal_pode_dominar and (w in S_set or w in T_set):
                continue
            Pw, Mw = P[w], M[w]
            if Pu <= Pw and Mu <= Mw:
                if Pu == Pw and Mu == Mw and w not in T_set and w not in S_set:
                    # gêmeos exatos: mantém só um representante (menor ordem)
                    if ordem[w] < ordem[u]:
                        dominados.add(u)
                        break
                else:
                    dominados.add(u)
                    break

    return dominados


def find_dead(S, T, V, A_r):
    """
    Vértices não alcançáveis a partir de alguma origem, ou que não alcançam
    nenhum destino, em A_r. Nunca podem fazer parte de uma rota, então
    y_v = 0 é válido independentemente de dominância.
    """
    from collections import deque
    N_plus, N_minus = build_neighborhoods(A_r)
    S_set, T_set = set(S), set(T)

    from_S = set(S_set)
    q = deque(S_set)
    while q:
        u = q.popleft()
        for w in N_plus.get(u, ()):
            if w not in from_S:
                from_S.add(w)
                q.append(w)

    to_T = set(T_set)
    q = deque(T_set)
    while q:
        u = q.popleft()
        for w in N_minus.get(u, ()):
            if w not in to_T:
                to_T.add(w)
                q.append(w)

    candidatos = [v for v in V if v not in S_set | T_set]
    return {v for v in candidatos if v not in from_S or v not in to_T}


def find_mandatory(S, T, V, N_plus, candidatos=None):
    """
    R2: v é obrigatório se V∖{v} já é inviável no oráculo (todos os outros
    vértices de V, inclusive terminais, com estação). Então y_v = 1 em toda
    solução viável e pode ser fixado.

    candidatos: vértices a testar (padrão: todo V). Terminais também podem ser
    obrigatórios (ex.: t1 em TermRelayForced).
    """
    if candidatos is None:
        candidatos = list(V)
    C_completo = frozenset(V)
    obrigatorios = set()
    for v in candidatos:
        viavel, _ = integer_oracle(S, T, N_plus, C_completo - {v})
        if not viavel:
            obrigatorios.add(v)
    return obrigatorios


def preprocess(S, T, V, adj, A_r):
    """
    Aplica dominância + mortos + obrigatórios. Retorna dict com:
    fixados_0 (dominados ∪ mortos), fixados_1 (obrigatórios), V_reduzido
    (V menos fixados_0, que é o único conjunto que sai do modelo — os
    fixados_1 continuam no modelo com y=1 fixo, não removidos).
    """
    N_plus, N_minus = build_neighborhoods(A_r)

    mortos = find_dead(S, T, V, A_r)
    dominados = find_dominated(S, T, V, N_plus, N_minus)
    fixados_0 = mortos | dominados

    candidatos_restantes = [v for v in V if v not in fixados_0]
    obrigatorios = find_mandatory(S, T, V, N_plus, candidatos=candidatos_restantes)

    V_reduzido = [v for v in V if v not in fixados_0]

    return {
        'mortos': mortos,
        'dominados': dominados,
        'fixados_0': fixados_0,
        'fixados_1': obrigatorios,
        'V_reduzido': V_reduzido,
        'n_removidos': len(fixados_0),
        'n_obrigatorios': len(obrigatorios),
    }
