"""
Certificado de OPT(cc12-2p) = 6 (R = 500, extensão ponderada, variante U).

UB: a solução de 6 estações encontrada na revisão pós-E7 (primeira solução do
pool de ótimos do núcleo) é viável no oráculo restrito e no modelo compacto
com y fixado.

LB: o núcleo (IP em y com cortes estáticos) é relaxação do problema real se
todo corte y(Z) >= 1 usado for válido. Só C1 dá 5; C1 + C4-DM dá 6. Cada um
desses cortes é validado.

`is_valid_cut` leva ~130 s por corte em cc12-2p (|A_r| ≈ 2,8 milhões), e a
fase de emparelhamento faz uma BFS por origem. Como cc12-2p é não dirigida
(A_r simétrico), uso um validador equivalente por componentes conexas:
quem uma origem alcança passando só por vértices passáveis é o fecho de
vizinhança das componentes (no subgrafo passável) adjacentes a ela. Antes de
usá-lo, o script o compara com `is_valid_cut` em instâncias não dirigidas
menores (gabaritos, hc9u, cc10-2p) e em cortes aleatórios.

Saída: results/cuts/e8_certificado_cc12.txt (e stdout).
"""
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

from gurobipy import GRB
import synthetic as syn
from baseline import construir_modelo_baseline
from harness import load_instance
from cuts import (build_neighborhoods, generate_C1, generate_C4_DM,
                  integer_oracle, is_valid_cut, _max_matching)
from yspace import _build_ymodel

C_UB = frozenset({'109', '1157', '2387', '2873', '3834', '968'})
OUT = ROOT / 'results' / 'cuts' / 'e8_certificado_cc12.txt'


def is_valid_cut_undirected(S, T, V, N_plus, Z):
    """
    Mesmo critério de is_valid_cut (V∖Z inviável ⟺ o bipartido de alcance não
    tem emparelhamento perfeito), válido só para A_r simétrico.

    Passável = fora de Z (e, com m < 2, não terminal), como em _passavel.
    Uma origem s alcança t se t ∈ N⁺(s), ou se t está numa componente K do
    subgrafo passável adjacente a s, ou em N⁺(K). Com A_r simétrico, o
    conjunto de vértices passáveis alcançáveis a partir de um vizinho passável
    w de s é exatamente a componente de w.
    """
    S_set, T_set = set(S), set(T)
    m = len(S)
    Z = set(Z)

    def passavel(v):
        return v not in Z and not (m < 2 and (v in S_set or v in T_set))

    P = [v for v in V if passavel(v)]
    pai = {v: v for v in P}

    def raiz(v):
        while pai[v] != v:
            pai[v] = pai[pai[v]]
            v = pai[v]
        return v

    for u in P:
        for w in N_plus.get(u, ()):
            if w in pai:
                ru, rw = raiz(u), raiz(w)
                if ru != rw:
                    pai[ru] = rw

    alvo_comp = {}
    for v in P:
        k = raiz(v)
        conj = alvo_comp.setdefault(k, set())
        if v in T_set:
            conj.add(v)
        conj.update(w for w in N_plus.get(v, ()) if w in T_set)

    adj = {}
    for s in S_set:
        reach = {t for t in N_plus.get(s, ()) if t in T_set}
        if s in T_set:
            reach.add(s)
        for w in N_plus.get(s, ()):
            if w in pai:
                reach |= alvo_comp[raiz(w)]
        adj[s] = reach

    mfwd, _ = _max_matching(list(S_set), adj)
    return len(mfwd) < m


def conferir_validador(log):
    """Compara com is_valid_cut em instâncias não dirigidas menores."""
    casos = []
    for fn in [syn.make_Tri, syn.make_TermRelay, syn.make_SharedTerminal,
               syn.make_TermRelayForced, lambda: syn.make_F1(m=2, k=2, r=1),
               lambda: syn.make_Sec59(L=7, r=1)]:
        S, T, V, adj, A_r, r, _ = fn()
        casos.append(('gabarito', S, T, V, A_r, 200))
    for fname, n in [('hc9u.txt', 60), ('cc10-2p.txt', 15)]:
        S, T, V, adj, A_r, r = load_instance(ROOT / 'instances' / fname)
        casos.append((fname, S, T, V, A_r, n))

    rng = random.Random(7)
    total = diverg = 0
    for nome, S, T, V, A_r, n in casos:
        N_plus, N_minus = build_neighborhoods(A_r)
        assert all(u in N_plus.get(v, ()) for u, v in A_r), f'{nome} não é simétrica'
        estruturados = [frozenset(Z) for Z in generate_C1(S, T, N_plus, N_minus)
                        + generate_C4_DM(S, T, N_plus, N_minus)]
        cortes = estruturados[:n // 2]
        while len(cortes) < n:
            k = rng.randint(0, max(1, len(V) // 3))
            cortes.append(frozenset(rng.sample(V, k)))
        for Z in cortes:
            total += 1
            if is_valid_cut(S, T, A_r, Z, N_plus, N_minus) != \
                    is_valid_cut_undirected(S, T, V, N_plus, Z):
                diverg += 1
    log(f'conferência do validador por componentes: {total} cortes, {diverg} divergências')
    return diverg == 0


def main():
    linhas = []

    def log(msg):
        print(msg, flush=True)
        linhas.append(msg)

    validador_ok = conferir_validador(log)

    t0 = time.monotonic()
    S, T, V, adj, A_r, r = load_instance(ROOT / 'instances' / 'cc12-2p.txt')
    log(f'cc12-2p: n={len(V)} m={len(S)} |A_r|={len(A_r)} R={r} '
        f'(carga {time.monotonic()-t0:.0f}s)')
    N_plus, N_minus = build_neighborhoods(A_r)
    simetrica = all(u in N_plus.get(v, ()) for u, v in A_r)
    log(f'A_r simétrico: {simetrica}')

    ok_or, _ = integer_oracle(S, T, N_plus, C_UB)
    modelo, y, _, _, _ = construir_modelo_baseline(S, T, V, A_r)
    modelo.Params.OutputFlag = 0
    for v in V:
        val = 1.0 if v in C_UB else 0.0
        y[v].lb = val
        y[v].ub = val
    modelo.update()
    modelo.optimize()
    ok_comp = modelo.Status == GRB.OPTIMAL
    del modelo
    log(f'UB: |C|={len(C_UB)} C={sorted(C_UB)} oráculo={ok_or} compacto={ok_comp}')

    cortes = list({frozenset(Z) for Z in generate_C1(S, T, N_plus, N_minus)
                   + generate_C4_DM(S, T, N_plus, N_minus)})
    t1 = time.monotonic()
    invalidos = [Z for Z in cortes if not is_valid_cut_undirected(S, T, V, N_plus, Z)]
    log(f'cortes C1+C4-DM: {len(cortes)} únicos, {len(cortes)-len(invalidos)} válidos '
        f'(t={time.monotonic()-t1:.0f}s)')

    mip, _ = _build_ymodel(V, cortes, integer=True, time_limit=600)
    mip.optimize()
    lb_ok = mip.Status == GRB.OPTIMAL
    lb = mip.ObjVal if lb_ok else None
    log(f'núcleo C1+C4-DM: status={mip.Status} ótimo={lb}')

    certificado = (validador_ok and simetrica and ok_or and ok_comp and not invalidos
                   and lb_ok and abs(lb - len(C_UB)) < 0.5)
    log(f'CERTIFICADO OPT(cc12-2p)=6: {"SIM" if certificado else "NÃO"}')

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text('\n'.join(linhas) + '\n', encoding='utf-8')
    if not certificado:
        sys.exit(1)


if __name__ == '__main__':
    main()
