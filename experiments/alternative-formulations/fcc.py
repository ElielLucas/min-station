"""F-CC por enumeração explícita de conjuntos conexos em H = G^r.

Forma original: variáveis λ_q para q = (W, I, J).
Forma separada: λ_W, α_sW, β_tW (equivalente no LP se P7).

Não implementa as redes de trios da F-C3 (OPEN na spec B).
Não substitui baseline.py.
"""

from collections import deque
from itertools import combinations

from gurobipy import GRB, Model, quicksum


class CapExceeded(Exception):
    def __init__(self, cap_name, value, cap):
        super().__init__(f'{cap_name}={value} excede cap={cap}')
        self.cap_name = cap_name
        self.value = value
        self.cap = cap


def grafo_H(V, A_r):
    """Grafo não dirigido de alcance: aresta se d_G(u,v) <= r, u != v."""
    neigh = {v: set() for v in V}
    for u, v in A_r:
        if u == v:
            continue
        neigh.setdefault(u, set()).add(v)
        neigh.setdefault(v, set()).add(u)
    for v in V:
        neigh.setdefault(v, set())
    return neigh


def pares_diretos(S, T, A_r):
    """D = {(s,t) in S×T : d(s,t) <= r}, incluindo d(s,s)=0 para s in S∩T."""
    Aset = set(A_r)
    D = []
    S, T = list(S), list(T)
    for s in S:
        for t in T:
            if s == t or (s, t) in Aset:
                D.append((s, t))
    return D


def B_de(W, neigh):
    fechado = set(W)
    for w in W:
        fechado |= neigh.get(w, set())
    return fechado


def enumerar_conexos(neigh, V, cap):
    """Subconjuntos não vazios conexos de H, cada um uma vez, até `cap`.

    BFS no reticulado: cada conjunto conexo é gerado a partir de um gerador
    menor, sem reverse search.
    """
    verts = list(V)
    out = []
    visto = set()
    fila = deque()
    for v in verts:
        s = frozenset([v])
        if s in visto:
            continue
        visto.add(s)
        fila.append(s)
        out.append(s)
        if len(out) >= cap:
            return out, True
    while fila:
        S = fila.popleft()
        fronteira = set()
        for u in S:
            fronteira |= neigh.get(u, set())
        fronteira -= S
        for w in fronteira:
            T = frozenset(S | {w})
            if T in visto:
                continue
            visto.add(T)
            out.append(T)
            fila.append(T)
            if len(out) >= cap:
                return out, True
    return out, False


def _configs_qij(W, S, T, neigh):
    I_pool = [s for s in S if s in B_de(W, neigh)]
    J_pool = [t for t in T if t in B_de(W, neigh)]
    qs = []
    kmax = min(len(I_pool), len(J_pool))
    for k in range(1, kmax + 1):
        for I in combinations(I_pool, k):
            for J in combinations(J_pool, k):
                qs.append((frozenset(W), frozenset(I), frozenset(J)))
    return qs


def construir_modelo_fcc(
    S, T, V, A_r, forma='qij', max_W=200000, y_fixo=None, integer_y=False,
):
    """Devolve (modelo, y, extra, meta). extra depende da forma.

    forma: 'qij' (F-CC original) ou 'separada' (λ_W, α, β).
    y_fixo: dict v -> 0/1 para teste de viabilidade.
    integer_y: quando True e y_fixo é None, cria y binário para OPT exacto.
    O default False preserva a F-CC LP usada por F3.
    """
    if forma not in ('qij', 'separada'):
        raise ValueError(f'forma desconhecida: {forma!r}')
    S, T, V = list(S), list(T), list(V)
    neigh = grafo_H(V, A_r)
    D = pares_diretos(S, T, A_r)
    Ws, _trunc = enumerar_conexos(neigh, V, max_W + 1)
    if len(Ws) > max_W:
        raise CapExceeded('max_W', len(Ws), max_W)
    # Q exige |I|=|J|>=1: W sem origem e destino em B(W) não gera configuração.
    Sset, Tset = set(S), set(T)
    Ws_uteis = []
    BWs = []
    for W in Ws:
        BW = B_de(W, neigh)
        if (Sset & BW) and (Tset & BW):
            Ws_uteis.append(W)
            BWs.append(BW)
    Ws = Ws_uteis

    modelo = Model(f'F-CC-{forma}')
    modelo.Params.OutputFlag = 0
    if y_fixo is None:
        if integer_y:
            y = {v: modelo.addVar(vtype=GRB.BINARY, name=f'y[{v}]') for v in V}
        else:
            y = {v: modelo.addVar(lb=0.0, ub=1.0, name=f'y[{v}]') for v in V}
    else:
        y = {}
        for v in V:
            val = float(y_fixo[v])
            y[v] = modelo.addVar(lb=val, ub=val, name=f'y[{v}]')

    dvar = {
        (s, t): modelo.addVar(lb=0.0, name=f'd[{s},{t}]')
        for (s, t) in D
    }
    modelo.setObjective(quicksum(y[v] for v in V), GRB.MINIMIZE)

    extra = {'d': dvar, 'W': Ws, 'D': D}

    if forma == 'qij':
        Q = []
        for W in Ws:
            Q.extend(_configs_qij(W, S, T, neigh))
        lam = {}
        for W, I, J in Q:
            nome = f'lam[{len(lam)}]'
            lam[W, I, J] = modelo.addVar(lb=0.0, name=nome)
        extra['lam'] = lam
        extra['Q'] = Q
        for s in S:
            termos = [lam[W, I, J] for (W, I, J) in Q if s in I]
            termos += [dvar[s, t] for (ss, t) in D if ss == s]
            modelo.addConstr(quicksum(termos) == 1, name=f'R1[{s}]')
        for t in T:
            termos = [lam[W, I, J] for (W, I, J) in Q if t in J]
            termos += [dvar[s, tt] for (s, tt) in D if tt == t]
            modelo.addConstr(quicksum(termos) == 1, name=f'R2[{t}]')
        for v in V:
            termos = [lam[W, I, J] for (W, I, J) in Q if v in W]
            modelo.addConstr(quicksum(termos) <= y[v], name=f'R3[{v}]')
    else:
        nW = len(Ws)
        lamW = modelo.addVars(nW, lb=0.0, name='lamW')
        a_keys = [(s, i) for i, BW in enumerate(BWs) for s in S if s in BW]
        b_keys = [(t, i) for i, BW in enumerate(BWs) for t in T if t in BW]
        alfa = modelo.addVars(a_keys, lb=0.0, name='a')
        beta = modelo.addVars(b_keys, lb=0.0, name='b')
        modelo.addConstrs((alfa[s, i] <= lamW[i] for (s, i) in a_keys), name='a_le')
        modelo.addConstrs((beta[t, i] <= lamW[i] for (t, i) in b_keys), name='b_le')
        modelo.addConstrs(
            (
                quicksum(alfa[s, i] for s in S if (s, i) in alfa)
                == quicksum(beta[t, i] for t in T if (t, i) in beta)
                for i in range(nW)
            ),
            name='balW',
        )
        extra['lamW'] = lamW
        extra['alfa'] = alfa
        extra['beta'] = beta
        for s in S:
            modelo.addConstr(
                quicksum(alfa[s, i] for i in range(nW) if (s, i) in alfa)
                + quicksum(dvar[ss, t] for (ss, t) in D if ss == s)
                == 1,
                name=f'R1[{s}]',
            )
        for t in T:
            modelo.addConstr(
                quicksum(beta[t, i] for i in range(nW) if (t, i) in beta)
                + quicksum(dvar[s, tt] for (s, tt) in D if tt == t)
                == 1,
                name=f'R2[{t}]',
            )
        por_v = {v: [] for v in V}
        for i, W in enumerate(Ws):
            for v in W:
                por_v[v].append(i)
        for v in V:
            modelo.addConstr(
                quicksum(lamW[i] for i in por_v[v]) <= y[v],
                name=f'R3[{v}]',
            )

    modelo.update()
    meta = {
        'n_W': len(Ws),
        'n_D': len(D),
        'forma': forma,
        'integer_y': bool(integer_y),
        'n_vars': modelo.NumVars,
        'n_cons': modelo.NumConstrs,
    }
    return modelo, y, extra, meta


def lp_fcc(S, T, V, A_r, forma='separada', max_W=200000, seed=42, threads=1):
    modelo, _y, _extra, meta = construir_modelo_fcc(
        S, T, V, A_r, forma=forma, max_W=max_W,
    )
    modelo.Params.Seed = seed
    modelo.Params.Threads = threads
    modelo.Params.Method = 2
    modelo.optimize()
    if modelo.Status != GRB.OPTIMAL:
        st = modelo.Status
        modelo.dispose()
        raise RuntimeError(f'F-CC LP status {st}')
    val = float(modelo.ObjVal)
    modelo.dispose()
    return val, meta


def fcc_y_viavel(S, T, V, A_r, C, forma='qij', max_W=200000):
    """True sse o modelo F-CC admite solução com y = 1_C (y contínuo fixo)."""
    Cset = set(C)
    y_fixo = {v: (1.0 if v in Cset else 0.0) for v in V}
    modelo, _y, _e, _m = construir_modelo_fcc(
        S, T, V, A_r, forma=forma, max_W=max_W, y_fixo=y_fixo,
    )
    modelo.optimize()
    ok = modelo.Status == GRB.OPTIMAL
    modelo.dispose()
    return ok


def opt_fcc(
    S, T, V, A_r, forma='separada', max_W=200000, seed=42, threads=1,
    time_limit=1800,
):
    """Resolve a F-CC com ``y`` binário e exige prova de optimalidade.

    É um helper de referência para R11. Não altera ``lp_fcc`` nem o protocolo
    F3. ``CapExceeded`` continua sendo propagado. Status diferente de
    ``GRB.OPTIMAL`` gera ``RuntimeError`` e nunca devolve incumbente como OPT.
    """
    modelo, _y, _extra, meta = construir_modelo_fcc(
        S, T, V, A_r, forma=forma, max_W=max_W, integer_y=True,
    )
    modelo.Params.Seed = seed
    modelo.Params.Threads = threads
    modelo.Params.OutputFlag = 0
    if time_limit is not None:
        modelo.Params.TimeLimit = float(time_limit)
    modelo.optimize()
    status = int(modelo.Status)
    meta = dict(meta)
    meta['status'] = status
    meta['runtime'] = float(getattr(modelo, 'Runtime', 0.0))
    if status != GRB.OPTIMAL:
        modelo.dispose()
        raise RuntimeError(f'F-CC IP status {status}')
    val = float(modelo.ObjVal)
    modelo.dispose()
    return val, meta
