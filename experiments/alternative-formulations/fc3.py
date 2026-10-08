#!/usr/bin/env python3
"""N1-T3: F-C3 canônica (CA0-CA6 e C31-C34), sem alterar F-CC.

Base matemática: docs/technical/reference/formulacoes/formulacao-fc3-canonica-v1.md
A aceitação matemática MR-F3 não substitui verify_fc3_n1.py. Não interpretar
valores de LP até toda a bateria de equivalência por instalação terminar com zero
falhas para ambos os braços. Os cortes K são o controle histórico F-CC + K.
"""
from __future__ import annotations

from itertools import combinations
from math import comb
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
for path in (str(HERE), str(ROOT), str(ROOT / 'experiments' / 'cuts')):
    if path not in sys.path:
        sys.path.insert(0, path)

MAX_N = 21
MAX_W = 200000
MAX_NETWORK_ARCS = 5_000_000


class FC3SizeExceeded(ValueError):
    """Cap pré-registrado ultrapassado: braço deve ser NOT MEASURED."""

    def __init__(self, label, value, limit):
        super().__init__(f'{label}={value} excede cap={limit}; NOT MEASURED')
        self.label, self.value, self.limit = label, value, limit


def bound_network_arcs(m: int, n_w: int) -> int:
    """Limite superior fixado em N1: duas famílias de trios, 35 arcos/etapa."""
    if m < 0 or n_w < 0:
        raise ValueError('m e n_w devem ser não negativos')
    return 2 * comb(m, 3) * (35 * n_w + 8) if m >= 3 else 0


def stage_arcs(eligible_mask: int):
    """Enumera (B, R, destino, uso) de uma etapa: não uso e TODO R⊆ elegível menos B.

    Uso com R=0 é diferente de não uso; as 8 máscaras representam subconjuntos
    de três membros do trio. Sem dependências de solver, para testes de unidade.
    """
    if not 0 <= eligible_mask <= 7:
        raise ValueError('máscara deve estar em 0..7')
    for b in range(8):
        yield b, 0, b, False  # não utilização
        allowed = eligible_mask & (7 ^ b)
        r = allowed
        while True:
            yield b, r, b | r, True  # utilização, incluindo R=∅
            if r == 0:
                break
            r = (r - 1) & allowed


def _validate_inputs(S, T, V):
    if len(S) != len(T):
        raise ValueError('|S| diferente de |T|')
    if len(set(V)) != len(V) or len(set(S)) != len(S) or len(set(T)) != len(T):
        raise ValueError('vértices/terminais duplicados')
    if not set(S).issubset(V) or not set(T).issubset(V):
        raise ValueError('terminais fora de V')


def prepare_fc3(S, T, V, A_r, *, max_W=MAX_W, n_max=MAX_N,
                max_network_arcs=MAX_NETWORK_ARCS):
    """Enumera exatamente W elegíveis; bloqueia pelos caps ANTES de criar modelo.

    A enumeração histórica fcc.enumerar_conexos é reutilizada, mas a ordem das
    configurações úteis é fixada pelos índices de V (não por iteração de sets).
    """
    S, T, V = list(S), list(T), list(V)
    _validate_inputs(S, T, V)
    if len(V) > n_max:
        raise FC3SizeExceeded('n', len(V), n_max)
    from fcc import grafo_H, B_de, enumerar_conexos, pares_diretos
    neighbours = grafo_H(V, A_r)
    all_W, _ = enumerar_conexos(neighbours, V, max_W + 1)
    if len(all_W) > max_W:
        raise FC3SizeExceeded('max_W', len(all_W), max_W)
    index = {v: j for j, v in enumerate(V)}
    items = []
    for W in all_W:
        B = B_de(W, neighbours)
        sw = frozenset(set(S) & B)
        tw = frozenset(set(T) & B)
        if sw and tw:
            items.append((tuple(sorted(W, key=index.__getitem__)), sw, tw))
    items.sort(key=lambda x: tuple(index[v] for v in x[0]))
    Ws = [x[0] for x in items]
    arc_limit = bound_network_arcs(len(S), len(Ws))
    if arc_limit > max_network_arcs:
        raise FC3SizeExceeded('network_arc_bound', arc_limit, max_network_arcs)
    return {
        'W': Ws, 'S_W': [x[1] for x in items], 'T_W': [x[2] for x in items],
        'D': pares_diretos(S, T, A_r), 'n_W': len(Ws),
        'network_arc_bound': arc_limit,
    }


def _add_trio_network(model, side, trio_id, trio, Ws_elig, lam, marg, direct):
    """C31–C34 para UM trio: fluxo unitário em DAG com acoplamento global.

    Máscaras 0..7 são relativas à ordem em trio, não aos índices de V.
    previous[b] é a massa ENTRANTE no estado (j-1,b). No início apenas
    (0,∅) tem oferta 1. Variáveis do arco são contínuas inclusive com y binário.
    """
    from gurobipy import quicksum
    # previous representa uma expressão linear de fluxo para cada máscara.
    previous = [1.0] + [0.0] * 7
    n_arcs = 0
    for j, eligible in enumerate(Ws_elig):
        eligible_mask = sum(1 << p for p, u in enumerate(trio) if u in eligible)
        incoming = [[] for _ in range(8)]
        outgoing = [[] for _ in range(8)]
        use = []
        use_by_terminal = [[] for _ in range(3)]
        for b, r, dest, is_use in stage_arcs(eligible_mask):
            arc = model.addVar(lb=0.0, ub=1.0,
                               name=f'phi[{side},{trio_id},{j},{b},{r},{int(is_use)}]')
            n_arcs += 1
            outgoing[b].append(arc)
            incoming[dest].append(arc)
            if is_use:
                use.append(arc)
                for p in range(3):
                    if r & (1 << p):
                        use_by_terminal[p].append(arc)
        for b in range(8):
            model.addConstr(quicksum(outgoing[b]) == previous[b],
                            name=f'C31[{side},{trio_id},{j},{b}]')
        model.addConstr(quicksum(use) == lam[j],
                        name=f'C32[{side},{trio_id},{j}]')
        for p, u in enumerate(trio):
            rhs = marg.get((u, j), 0.0)
            model.addConstr(quicksum(use_by_terminal[p]) == rhs,
                            name=f'C33[{side},{trio_id},{j},{p}]')
        previous = [quicksum(incoming[b]) for b in range(8)]
    finals = [model.addVar(lb=0.0, ub=1.0,
                           name=f'phi[{side},{trio_id},final,{b}]') for b in range(8)]
    n_arcs += 8
    for b in range(8):
        model.addConstr(finals[b] == previous[b],
                        name=f'C31-final[{side},{trio_id},{b}]')
    model.addConstr(quicksum(finals) == 1.0,
                    name=f'C31-sink[{side},{trio_id}]')
    for p, u in enumerate(trio):
        model.addConstr(quicksum(finals[b] for b in range(8) if not b & (1 << p))
                        == direct[u], name=f'C34[{side},{trio_id},{p}]')
    return n_arcs


def construir_modelo_fc3(S, T, V, A_r, *, max_W=MAX_W, n_max=MAX_N,
                         max_network_arcs=MAX_NETWORK_ARCS, y_fixo=None,
                         integer_y=False, structure=None):
    """Constrói F-C3 (y LP por padrão), devolve (modelo,y,extra,meta).

    Em caso de cap: FC3SizeExceeded, nenhum modelo é criado. Não utiliza a
    forma separada histórica porque ela omite CA5; implementa CA1–CA6.
    """
    from gurobipy import GRB, Model, quicksum
    S, T, V = list(S), list(T), list(V)
    _validate_inputs(S, T, V)
    data = structure if structure is not None else prepare_fc3(
        S, T, V, A_r, max_W=max_W, n_max=n_max,
        max_network_arcs=max_network_arcs,
    )
    # O cap é reavaliado também quando a estrutura é injetada.
    if len(data['W']) > max_W:
        raise FC3SizeExceeded('max_W', len(data['W']), max_W)
    if len(V) > n_max:
        raise FC3SizeExceeded('n', len(V), n_max)
    if bound_network_arcs(len(S), len(data['W'])) > max_network_arcs:
        raise FC3SizeExceeded('network_arc_bound',
                              bound_network_arcs(len(S), len(data['W'])),
                              max_network_arcs)
    if y_fixo is not None and set(y_fixo) != set(V):
        raise ValueError('y_fixo deve conter exatamente V')
    model = Model('F-C3')
    model.Params.OutputFlag = 0
    try:
        y = {}
        for v in V:
            lb = float(y_fixo[v]) if y_fixo is not None else 0.0
            ub = float(y_fixo[v]) if y_fixo is not None else 1.0
            y[v] = model.addVar(lb=lb, ub=ub, vtype=GRB.BINARY if integer_y and
                                y_fixo is None else GRB.CONTINUOUS, name=f'y[{v}]')
        nW = len(data['W'])
        lam = model.addVars(range(nW), lb=0.0, name='lamW')
        a_keys = [(s, j) for j, group in enumerate(data['S_W']) for s in S if s in group]
        b_keys = [(t, j) for j, group in enumerate(data['T_W']) for t in T if t in group]
        alfa = model.addVars(a_keys, lb=0.0, name='a')
        beta = model.addVars(b_keys, lb=0.0, name='b')
        dvar = {(s, t): model.addVar(lb=0.0, name=f'd[{s},{t}]') for s, t in data['D']}
        model.setObjective(quicksum(y.values()), GRB.MINIMIZE)
        for s in S:
            model.addConstr(quicksum(alfa[s, j] for j in range(nW) if (s, j) in alfa)
                            + quicksum(dvar[ss, t] for ss, t in data['D'] if ss == s)
                            == 1.0, name=f'CA1[{s}]')
        for t in T:
            model.addConstr(quicksum(beta[t, j] for j in range(nW) if (t, j) in beta)
                            + quicksum(dvar[s, tt] for s, tt in data['D'] if tt == t)
                            == 1.0, name=f'CA2[{t}]')
        for s, j in a_keys:
            model.addConstr(alfa[s, j] <= lam[j], name=f'CA3S[{s},{j}]')
        for t, j in b_keys:
            model.addConstr(beta[t, j] <= lam[j], name=f'CA3T[{t},{j}]')
        for j in range(nW):
            lhs = quicksum(alfa[s, j] for s in S if (s, j) in alfa)
            rhs = quicksum(beta[t, j] for t in T if (t, j) in beta)
            model.addConstr(lhs == rhs, name=f'CA4[{j}]')
            model.addConstr(lam[j] <= lhs, name=f'CA5[{j}]')
        for v in V:
            model.addConstr(quicksum(lam[j] for j, W in enumerate(data['W']) if v in W)
                            <= y[v], name=f'CA6[{v}]')
        n_phi = 0
        n_networks = 0
        for side, terminals, eligible, marg in (
            ('S', S, data['S_W'], alfa), ('T', T, data['T_W'], beta),
        ):
            direct = {
                u: quicksum(dvar[s, t] for s, t in data['D']
                            if (s if side == 'S' else t) == u)
                for u in terminals
            }
            for trio_id, trio in enumerate(combinations(terminals, 3)):
                n_phi += _add_trio_network(model, side, trio_id, trio,
                                          eligible, lam, marg, direct)
                n_networks += 1
        model.update()
        meta = {
            'n_W': nW, 'n_D': len(data['D']), 'n_trio_networks': n_networks,
            'n_network_arcs': n_phi,
            'network_arc_bound': data['network_arc_bound'],
            'n_vars': model.NumVars, 'n_cons': model.NumConstrs,
            'formulation': 'F-C3-v1.0.1',
            'integer_y': bool(integer_y),
        }
        extra = {'W': data['W'], 'S_W': data['S_W'], 'T_W': data['T_W'],
                 'D': data['D'], 'lamW': lam, 'alfa': alfa, 'beta': beta,
                 'd': dvar}
        return model, y, extra, meta
    except Exception:
        model.dispose()
        raise


def build_fc3_plus_k(S, T, V, adj, A_r, r, *, K=None, k_hash=None,
                     max_W=MAX_W, n_max=MAX_N,
                     max_network_arcs=MAX_NETWORK_ARCS, y_fixo=None):
    """Mesmo conjunto K de fcc_k, obtido sem recalcular quando fornecido."""
    from fcc_k import prepare_k
    from harness import add_cuts_to_model
    from cuts import cortes_ordenados
    import hashlib
    import json
    if K is None:
        K, digest, _ = prepare_k(S, T, V, adj, A_r, r)
    else:
        K = cortes_ordenados(K)
        canonical = [sorted(str(v) for v in Z) for Z in K]
        digest = hashlib.sha256(json.dumps(canonical, ensure_ascii=False,
                             separators=(',', ':')).encode('utf8')).hexdigest()
    if k_hash is not None and digest != k_hash:
        raise ValueError('K congelado não coincide com o hash informado')
    model, y, extra, meta = construir_modelo_fc3(
        S, T, V, A_r, max_W=max_W, n_max=n_max,
        max_network_arcs=max_network_arcs, y_fixo=y_fixo,
    )
    try:
        added = add_cuts_to_model(model, y, K, validate=(S, T, A_r))
        if added != len(K):
            raise AssertionError(f'K: {len(K)} cortes, adicionados {added}')
        model.update()
        meta.update({'k_hash': digest, 'n_K': len(K), 'n_K_added': added,
                     'n_vars': model.NumVars, 'n_cons': model.NumConstrs})
        return model, y, extra, meta
    except Exception:
        model.dispose()
        raise


def _solve_lp(model, meta, seed=42, threads=1):
    from gurobipy import GRB
    try:
        model.Params.OutputFlag = 0
        model.Params.Seed = seed
        model.Params.Threads = threads
        model.Params.Method = 2
        model.optimize()
        if model.Status != GRB.OPTIMAL:
            raise RuntimeError(f'F-C3 LP não certificado: status={model.Status}')
        return float(model.ObjVal), dict(meta)
    finally:
        model.dispose()


def lp_fc3(S, T, V, A_r, *, max_W=MAX_W, max_network_arcs=MAX_NETWORK_ARCS,
           seed=42, threads=1):
    model, _, _, meta = construir_modelo_fc3(
        S, T, V, A_r, max_W=max_W, max_network_arcs=max_network_arcs)
    return _solve_lp(model, meta, seed, threads)


def lp_fc3_plus_k(S, T, V, adj, A_r, r, *, K=None, k_hash=None,
                  max_W=MAX_W, max_network_arcs=MAX_NETWORK_ARCS,
                  seed=42, threads=1):
    model, _, _, meta = build_fc3_plus_k(
        S, T, V, adj, A_r, r, K=K, k_hash=k_hash,
        max_W=max_W, max_network_arcs=max_network_arcs)
    return _solve_lp(model, meta, seed, threads)
