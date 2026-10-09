#!/usr/bin/env python3
"""N2-T2B: verificação algébrica da revisão master/dual/pricing (NÃO é medição N2).

Usa somente instâncias aleatórias minúsculas geradas aqui (n <= 8, semente fixa),
fora do corpus congelado em n2-t1-freeze.json. Não escreve arquivos, não executa
geração de colunas e não produz bound para nenhuma instância N2.

Checa, contra enumeração completa de Q:
  V1  P7: LP qij+K (colunas (W,I,J)) == LP separada+K de fcc_k.py;
  V2  sinais Gurobi -> (pi, tau, mu=-Pi(R3), kappa=Pi(K)), eta=max(0, mu+kappa(v)-1),
      e objetivo dual == objetivo primal;
  V3  custo reduzido da fórmula == RC do Gurobi para toda coluna;
  V4  forma fechada TopK do pricing == força bruta sobre (I,J), duais livres;
  V5  limites LB_A (massa m) e LB_B (razão via R3) <= z_LP para multiplicadores
      arbitrários e para duais de masters restritos;
  V6  pricing MIP com conectividade por fluxo == mínimo por enumeração;
  V7  redução: pricing com S=T=V, pi=tau=M, mu=1, r=1 resolve conjunto dominante
      conexo mínimo.
Limites (parecer independente, D.2): comparações e otimizações em ponto flutuante;
regressão auxiliar, não prova formal; não testa bound de MIP interrompido, ℓ < c*
deliberado, enumeração truncada nem exportação racional. Esses riscos têm controles
dirigidos em test_n2_t2b_controles_matematicos.py.
Documento: docs/technical/reference/formulacoes/n2-t2b-master-dual-pricing-revisao.md
"""
import itertools
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for p in (ROOT, ROOT / 'experiments' / 'cuts', HERE):
    sys.path.insert(0, str(p))

from gurobipy import GRB, Model, quicksum
from ms_utils import construir_arcos_alcance
from fcc import grafo_H, B_de, enumerar_conexos, pares_diretos
from fcc_k import prepare_k, build_fcc_plus_k
from harness import add_cuts_to_model

rng = random.Random(20261009)


def inst_aleatoria():
    n = rng.randint(4, 8)
    V = [f'v{i}' for i in range(n)]
    edges = set()
    for i in range(1, n):
        edges.add((V[rng.randrange(i)], V[i]))
    for _ in range(rng.randint(0, n)):
        a, b = rng.sample(V, 2)
        if (b, a) not in edges:
            edges.add((a, b))
    adj = {}
    for u, v in edges:
        adj.setdefault(u, []).append((v, 1))
        adj.setdefault(v, []).append((u, 1))
    r = rng.choice([1, 1, 2])
    m = rng.randint(1, min(3, n))
    S = rng.sample(V, m)
    T = rng.sample(V, m)  # S∩T permitido
    A_r = construir_arcos_alcance(V, adj, r)
    return S, T, V, adj, A_r, r


def todas_configs(S, T, V, neigh):
    Ws, trunc = enumerar_conexos(neigh, V, 10**6)
    assert not trunc
    Q = []
    for W in Ws:
        BW = B_de(W, neigh)
        Ip = [s for s in S if s in BW]
        Jp = [t for t in T if t in BW]
        for k in range(1, min(len(Ip), len(Jp)) + 1):
            for I in itertools.combinations(Ip, k):
                for J in itertools.combinations(Jp, k):
                    Q.append((frozenset(W), frozenset(I), frozenset(J)))
    return Ws, Q


def rc(q, pi, tau, mu):
    W, I, J = q
    return sum(mu[v] for v in W) - sum(pi[s] for s in I) - sum(tau[t] for t in J)


def topk_price(W, S, T, neigh, pi, tau, mu):
    BW = B_de(W, neigh)
    a = sorted((pi[s] for s in S if s in BW), reverse=True)
    b = sorted((tau[t] for t in T if t in BW), reverse=True)
    kmax = min(len(a), len(b))
    if kmax == 0:
        return None
    g = a[0] + b[0]
    for k in range(1, kmax):
        g += max(0.0, a[k] + b[k])
    return sum(mu[v] for v in W) - g


def lagr_bound(S, T, V, D, K, pi, tau, mu, kap, ell):
    m = len(S)
    kv = {v: 0.0 for v in V}
    for Z, kz in zip(K, kap):
        for v in Z:
            kv[v] += kz
    L = sum(pi.values()) + sum(tau.values()) + sum(kap) - sum(max(0.0, mu[v] + kv[v] - 1) for v in V)
    dD = min([0.0] + [-(pi[s] + tau[t]) for (s, t) in D])
    lm = min(0.0, ell)
    LA = L + m * min(lm, dD)
    LB = (L + m * dD) / (1 - lm)
    return L, LA, LB


def build_qij_k(S, T, V, adj, A_r, r, K, Qsub=None, ub=True):
    """Master qij+K com subconjunto de colunas Qsub (None = todas)."""
    neigh = grafo_H(V, A_r)
    D = pares_diretos(S, T, A_r)
    if Qsub is None:
        _, Qsub = todas_configs(S, T, V, neigh)
    md = Model('m')
    md.Params.OutputFlag = 0
    y = {v: md.addVar(lb=0, ub=(1 if ub else GRB.INFINITY)) for v in V}
    d = {e: md.addVar() for e in D}
    lam = {q: md.addVar() for q in Qsub}
    md.setObjective(quicksum(y.values()), GRB.MINIMIZE)
    R1 = {s: md.addConstr(quicksum(lam[q] for q in Qsub if s in q[1]) + quicksum(d[e] for e in D if e[0] == s) == 1) for s in S}
    R2 = {t: md.addConstr(quicksum(lam[q] for q in Qsub if t in q[2]) + quicksum(d[e] for e in D if e[1] == t) == 1) for t in T}
    R3 = {v: md.addConstr(quicksum(lam[q] for q in Qsub if v in q[0]) <= y[v]) for v in V}
    md.update()
    nK0 = md.NumConstrs
    n_added = add_cuts_to_model(md, y, K, validate=(S, T, A_r))
    md.update()
    Krows = md.getConstrs()[nK0:]
    assert len(Krows) == n_added == len(K), (len(Krows), n_added, len(K), nK0, md.NumConstrs)
    md.Params.Method = 1
    md.optimize()
    assert md.Status == GRB.OPTIMAL
    return md, y, d, lam, R1, R2, R3, Krows, D, neigh


def main():
    stats = dict(inst=0, P7=0, dual_eq=0, rc_eq=0, topk=0, lagr_rand=0, lagr_rmp=0,
                 mip=0, ub_diff=0, rmp_above=0, farley_better=0,
                 K_nonempty=0, ST_overlap=0, D_nonempty=0, z_pos=0, kappa_pos=0, eta_pos=0)
    worst = 0.0
    for it in range(60):
        S, T, V, adj, A_r, r = inst_aleatoria()
        K, _h, _ = prepare_k(S, T, V, adj, A_r, r)
        md, y, d, lam, R1, R2, R3, Krows, D, neigh = build_qij_k(S, T, V, adj, A_r, r, K)
        z = md.ObjVal
        stats['inst'] += 1
        stats['K_nonempty'] += int(len(K) > 0)
        stats['ST_overlap'] += int(bool(set(S) & set(T)))
        stats['D_nonempty'] += int(len(D) > 0)
        stats['z_pos'] += int(z > 1e-7)
        # P7: separada + K (implementação congelada)
        ms, *_ = build_fcc_plus_k(S, T, V, adj, A_r, r, K=K)
        ms.optimize()
        assert ms.Status == GRB.OPTIMAL
        assert abs(ms.ObjVal - z) < 1e-6, ('P7', ms.ObjVal, z)
        stats['P7'] += 1
        # duais com convenção Gurobi
        pi = {s: R1[s].Pi for s in S}
        tau = {t: R2[t].Pi for t in T}
        mu = {v: -R3[v].Pi for v in V}           # R3 escrita como sum lam - y <= 0, Pi <= 0
        kap = [c.Pi for c in Krows]              # y(Z) >= 1, Pi >= 0
        assert min(mu.values()) >= -1e-9 and min(kap + [0]) >= -1e-9
        eta_g = {v: max(0.0, -y[v].RC) for v in V}
        L, LA, LBf = lagr_bound(S, T, V, D, K, pi, tau, mu, kap, 0.0)
        assert abs(L - z) < 1e-6, ('dual', L, z)
        kv = {v: 0.0 for v in V}
        for Z, kz in zip(K, kap):
            for v in Z:
                kv[v] += kz
        for v in V:
            assert abs(max(0.0, mu[v] + kv[v] - 1) - eta_g[v]) < 1e-7
        stats['dual_eq'] += 1
        stats['kappa_pos'] += int(any(k > 1e-9 for k in kap))
        stats['eta_pos'] += int(any(e > 1e-9 for e in eta_g.values()))
        for q, var in lam.items():
            assert abs(var.RC - rc(q, pi, tau, mu)) < 1e-7
        stats['rc_eq'] += 1
        Ws, Q = todas_configs(S, T, V, neigh)
        assert min(rc(q, pi, tau, mu) for q in Q) >= -1e-7
        # TopK == força bruta, duais aleatórios livres
        for _ in range(5):
            pr = {s: rng.uniform(-2, 2) for s in S}
            tr = {t: rng.uniform(-2, 2) for t in T}
            mr = {v: rng.uniform(0, 2) for v in V}
            for W in Ws:
                bf = [rc(q, pr, tr, mr) for q in Q if q[0] == frozenset(W)]
                tk = topk_price(W, S, T, neigh, pr, tr, mr)
                if not bf:
                    assert tk is None
                else:
                    assert abs(min(bf) - tk) < 1e-9
            stats['topk'] += 1
            # bound lagrangiano com multiplicadores arbitrários (kappa >= 0)
            kr = [rng.uniform(0, 1) for _ in K]
            ell = min(rc(q, pr, tr, mr) for q in Q)
            _, la, lb = lagr_bound(S, T, V, D, K, pr, tr, mr, kr, ell)
            assert la <= z + 1e-9 and lb <= z + 1e-9, (la, lb, z)
            worst = max(worst, max(la, lb) - z)
            stats['lagr_rand'] += 1
            # pricing MIP exato == enumeração
            mm = pricing_mip(S, T, V, neigh, pr, tr, mr)
            assert abs(mm - ell) < 1e-6, (mm, ell)
            stats['mip'] += 1
        # masters restritos aleatórios contendo (V,S,T)
        full = (frozenset(V), frozenset(S), frozenset(T))
        assert full in set(Q)
        for _ in range(4):
            sub = [full] + rng.sample(Q, rng.randint(0, min(6, len(Q))))
            sub = list(dict.fromkeys(sub))
            mr_, y2, d2, lam2, R1b, R2b, R3b, Kb, *_ = build_qij_k(S, T, V, adj, A_r, r, K, Qsub=sub)
            zr = mr_.ObjVal
            assert zr >= z - 1e-7
            stats['rmp_above'] += int(zr > z + 1e-7)
            p2 = {s: R1b[s].Pi for s in S}
            t2 = {t: R2b[t].Pi for t in T}
            m2 = {v: max(0.0, -R3b[v].Pi) for v in V}
            k2 = [max(0.0, c.Pi) for c in Kb]
            ell = min(rc(q, p2, t2, m2) for q in Q)
            _, la, lb = lagr_bound(S, T, V, D, K, p2, t2, m2, k2, ell)
            assert la <= z + 1e-7 and lb <= z + 1e-7, (la, lb, z)
            stats['farley_better'] += int(lb > la + 1e-9)
            stats['lagr_rmp'] += 1
            mr_.dispose()
        # efeito do UB y<=1 (diagnóstico)
        mu_, *_ = build_qij_k(S, T, V, adj, A_r, r, K, Qsub=Q, ub=False)
        stats['ub_diff'] += int(abs(mu_.ObjVal - z) > 1e-7)
        for mod in (md, ms, mu_):
            mod.dispose()
    mcds_check()
    print(stats, 'max(LB - z)=', worst)
    print('PASS')


def pricing_mip(S, T, V, neigh, pi, tau, mu):
    n = len(V)
    md = Model('p')
    md.Params.OutputFlag = 0
    md.Params.MIPGap = 0
    md.Params.MIPGapAbs = 0
    x = {v: md.addVar(vtype=GRB.BINARY) for v in V}
    a = {s: md.addVar(vtype=GRB.BINARY) for s in S}
    b = {t: md.addVar(vtype=GRB.BINARY) for t in T}
    rho = {v: md.addVar(vtype=GRB.BINARY) for v in V}
    g = {v: md.addVar() for v in V}
    arcs = [(u, w) for u in V for w in neigh[u]]
    f = {e: md.addVar() for e in arcs}
    for s in S:
        md.addConstr(a[s] <= x[s] + quicksum(x[w] for w in neigh[s]))
    for t in T:
        md.addConstr(b[t] <= x[t] + quicksum(x[w] for w in neigh[t]))
    md.addConstr(quicksum(a.values()) == quicksum(b.values()))
    md.addConstr(quicksum(a.values()) >= 1)
    md.addConstr(quicksum(rho.values()) == 1)
    for v in V:
        md.addConstr(rho[v] <= x[v])
        md.addConstr(g[v] <= n * rho[v])
        md.addConstr(g[v] + quicksum(f[u, v] for u in neigh[v]) - quicksum(f[v, w] for w in neigh[v]) == x[v])
    for (u, w) in arcs:
        md.addConstr(f[u, w] <= (n - 1) * x[u])
        md.addConstr(f[u, w] <= (n - 1) * x[w])
    md.setObjective(quicksum(mu[v] * x[v] for v in V) - quicksum(pi[s] * a[s] for s in S)
                    - quicksum(tau[t] * b[t] for t in T), GRB.MINIMIZE)
    md.optimize()
    assert md.Status == GRB.OPTIMAL
    val = md.ObjVal
    md.dispose()
    return val


def mcds_check():
    """Pricing com S=T=V, pi=tau=M, mu=1, r=1 resolve conjunto dominante conexo mínimo."""
    for _ in range(15):
        S, T, V, adj, A_r, r = inst_aleatoria()
        A_r = construir_arcos_alcance(V, adj, 1)
        neigh = grafo_H(V, A_r)
        n = len(V)
        M = n  # 2M > n-1
        Ws, _ = enumerar_conexos(neigh, V, 10**6)
        best = min(topk_price(W, V, V, neigh, {v: M for v in V}, {v: M for v in V}, {v: 1 for v in V}) for W in Ws)
        cds = min(len(W) for W in Ws if B_de(W, neigh) == set(V))
        assert abs(best - (cds - 2 * M * n)) < 1e-9


if __name__ == '__main__':
    main()
