"""N2-T2B: controles matemáticos dirigidos (parecer independente, seção D.3).

Instâncias minúsculas definidas aqui, fora do corpus congelado em n2-t1-freeze.json.
Não é medição N2, não implementa geração de colunas e não escreve arquivos.
A aritmética de certificação usa `fractions.Fraction`: cada float finito é um
racional exato. Os testes que precisam de LP/MIP exigem `gurobipy` e são
ignorados sem ele; o restante roda em Python puro.

Documento: docs/technical/reference/formulacoes/n2-t2b-master-dual-pricing-revisao.md
"""
import itertools
import math
import random
import sys
import unittest
from decimal import ROUND_FLOOR, Decimal
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

try:
    import gurobipy as gp
    from gurobipy import GRB
    from fcc import enumerar_conexos
    from fcc import grafo_H as grafo_H_fcc
    HAVE_GUROBI = True
except ImportError:
    HAVE_GUROBI = False

EPS = Fraction(1, 10**6)


# ── referência em Python puro ────────────────────────────────────────────────

def alcance(V, edges, r):
    """H = G^r e D para G unitário. Retorna (neigh, D)."""
    adj = {v: set() for v in V}
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    neigh = {v: set() for v in V}
    D = set()
    for s in V:
        dist = {s: 0}
        frontier = [s]
        while frontier:
            nxt = []
            for u in frontier:
                for w in adj[u]:
                    if w not in dist:
                        dist[w] = dist[u] + 1
                        nxt.append(w)
            frontier = nxt
        for v, d in dist.items():
            if d <= r:
                D.add((s, v))
                if v != s:
                    neigh[s].add(v)
    return neigh, D


def fecho(W, neigh):
    out = set(W)
    for w in W:
        out |= neigh[w]
    return out


def conexo(W, neigh):
    W = set(W)
    if not W:
        return False
    seen = {next(iter(W))}
    stack = list(seen)
    while stack:
        u = stack.pop()
        for w in neigh[u] & W:
            if w not in seen:
                seen.add(w)
                stack.append(w)
    return seen == W


def conexos_forca_bruta(V, neigh):
    out = set()
    for k in range(1, len(V) + 1):
        for W in itertools.combinations(V, k):
            if conexo(W, neigh):
                out.add(frozenset(W))
    return out


def colunas(S, T, V, neigh):
    Q = []
    for W in sorted(conexos_forca_bruta(V, neigh), key=sorted):
        BW = fecho(W, neigh)
        Ip = [s for s in S if s in BW]
        Jp = [t for t in T if t in BW]
        for k in range(1, min(len(Ip), len(Jp)) + 1):
            for I in itertools.combinations(Ip, k):
                for J in itertools.combinations(Jp, k):
                    Q.append((frozenset(W), frozenset(I), frozenset(J)))
    return Q


def custo_reduzido(q, pi, tau, mu):
    W, I, J = q
    return sum(mu[v] for v in W) - sum(pi[s] for s in I) - sum(tau[t] for t in J)


def c_estrela(Q, pi, tau, mu):
    return min(custo_reduzido(q, pi, tau, mu) for q in Q)


def valor_L(S, T, V, K, pi, tau, mu, kappa):
    """L = Σπ + Στ + Σκ − Σ max{0, μ_v + κ(v) − 1}; κ indexado como K."""
    kv = {v: Fraction(0) for v in V}
    for Z, kz in zip(K, kappa):
        for v in Z:
            kv[v] += kz
    eta = sum((max(Fraction(0), mu[v] + kv[v] - 1) for v in V), Fraction(0))
    return sum(pi.values()) + sum(tau.values()) + sum(kappa) - eta


def valor_delta(D, pi, tau):
    """δ = min({0} ∪ {−π_s − τ_t}); δ = 0 se D é vazio (L0)."""
    return min([Fraction(0)] + [-(pi[s] + tau[t]) for (s, t) in D])


def lb_cg(L, ell, delta, m):
    """L1: max{0, L + m·min(a, δ), (L + m·δ)/(1 − a)}, a = min(0, ℓ)."""
    a = min(Fraction(0), ell)
    return max(Fraction(0), L + m * min(a, delta), (L + m * delta) / (1 - a))


def projetar(valor, nao_negativo=False):
    """float finito vira racional exato; NaN/infinito são rejeitados."""
    if isinstance(valor, float) and not math.isfinite(valor):
        raise ValueError('multiplicador não finito')
    x = Fraction(valor)
    return max(Fraction(0), x) if nao_negativo else x


def certificar_enum(S, T, V, D, K, neigh, pi, tau, mu, kappa, cap_atingido):
    """Referência do ramo ENUM: recusa certificado se a enumeração foi truncada."""
    if cap_atingido:
        raise RuntimeError('ENUM truncado: sem certificado')
    Q = colunas(S, T, V, neigh)
    ell = c_estrela(Q, pi, tau, mu)
    L = valor_L(S, T, V, K, pi, tau, mu, kappa)
    return lb_cg(L, ell, valor_delta(D, pi, tau), len(S)), ell


def exportar_para_baixo(x, casas=12):
    """Decimal ≤ x (arredondamento dirigido para baixo) a partir de Fraction."""
    q = Decimal(10) ** -casas
    d = Decimal(x.numerator) / Decimal(x.denominator)
    return d.quantize(q, rounding=ROUND_FLOOR)


def arredondar_inteiro(lb):
    """⌈LB − 10⁻⁶⌉ (convenção congelada), em racionais."""
    return math.ceil(lb - EPS)


def top_k(valores, k):
    return sum(sorted(valores, reverse=True)[:k], Fraction(0))


def ell_analitico(S, T, V, pi, tau, mu):
    """N1 do parecer: min_v μ_v − max_{1≤k≤m}(Top_k(π;S) + Top_k(τ;T))."""
    m = len(S)
    melhor = max(top_k([pi[s] for s in S], k) + top_k([tau[t] for t in T], k)
                 for k in range(1, m + 1))
    return min(mu[v] for v in V) - melhor


# ── pricing P0–P5 como dados (linhas '=' e '>=') ─────────────────────────────

def linhas_pricing(S, T, V, neigh):
    """Retorna (ub, linhas, ordem_das_variaveis). Variáveis em [0, ub].

    linhas: lista de (coeficientes, sentido, rhs) com sentido '=' ou '>='.
    Binárias: x, rho, a, b. Contínuas: g (ub n), f (ub n−1).
    """
    n = len(V)
    arcos = [(u, w) for u in V for w in sorted(neigh[u])]
    ub = {}
    for v in V:
        ub[('x', v)] = 1
        ub[('rho', v)] = 1
        ub[('g', v)] = n
    for s in S:
        ub[('a', s)] = 1
    for t in T:
        ub[('b', t)] = 1
    for (u, w) in arcos:
        ub[('f', u, w)] = n - 1
    linhas = []
    for s in S:
        c = {('x', w): 1 for w in fecho([s], neigh)}
        c[('a', s)] = -1
        linhas.append((c, '>=', 0))
    for t in T:
        c = {('x', w): 1 for w in fecho([t], neigh)}
        c[('b', t)] = -1
        linhas.append((c, '>=', 0))
    c = {('a', s): 1 for s in S}
    for t in T:
        c[('b', t)] = -1
    linhas.append((c, '=', 0))
    linhas.append(({('a', s): 1 for s in S}, '>=', 1))
    linhas.append(({('rho', v): 1 for v in V}, '=', 1))
    for v in V:
        linhas.append(({('x', v): 1, ('rho', v): -1}, '>=', 0))
        linhas.append(({('rho', v): n, ('g', v): -1}, '>=', 0))
        c = {('g', v): 1, ('x', v): -1}
        for u in neigh[v]:
            c[('f', u, v)] = c.get(('f', u, v), 0) + 1
        for w in neigh[v]:
            c[('f', v, w)] = c.get(('f', v, w), 0) - 1
        linhas.append((c, '=', 0))
    for (u, w) in arcos:
        linhas.append(({('x', u): n - 1, ('f', u, w): -1}, '>=', 0))
        linhas.append(({('x', w): n - 1, ('f', u, w): -1}, '>=', 0))
    return ub, linhas


def objetivo_pricing(S, T, V, pi, tau, mu):
    c = {}
    for v in V:
        c[('x', v)] = mu[v]
    for s in S:
        c[('a', s)] = -pi[s]
    for t in T:
        c[('b', t)] = -tau[t]
    return c


def ell_caixa(ub, linhas, c, duais):
    """N2 do parecer: θᵀb + νᵀh + Σ u_j·min{0, c_j − (Aᵀθ)_j − (Bᵀν)_j}."""
    res = {j: Fraction(c.get(j, 0)) for j in ub}
    const = Fraction(0)
    for (coefs, sentido, rhs), y in zip(linhas, duais):
        if sentido == '>=':
            assert y >= 0
        const += y * rhs
        for j, a in coefs.items():
            res[j] -= y * a
    return const + sum((ub[j] * min(Fraction(0), res[j]) for j in ub), Fraction(0))


# ── instâncias e utilitários ─────────────────────────────────────────────────

def caminho_abc():
    V = ['a', 'b', 'c']
    neigh, D = alcance(V, [('a', 'b'), ('b', 'c')], 1)
    return V, neigh, D


def instancia_aleatoria(rng, n_min=2, n_max=5):
    n = rng.randint(n_min, n_max)
    V = [f'v{i}' for i in range(n)]
    edges = {(V[rng.randrange(i)], V[i]) for i in range(1, n)}
    for _ in range(rng.randint(0, n)):
        a, b = rng.sample(V, 2) if n > 1 else (V[0], V[0])
        if a != b:
            edges.add((a, b))
    r = rng.choice([1, 1, 2])
    neigh, D = alcance(V, sorted(edges), r)
    m = rng.randint(1, min(3, n))
    return V, rng.sample(V, m), rng.sample(V, m), neigh, D


def lp_master(S, T, V, D, cols, K):
    """LP do master qij + K com as colunas `cols` (requer gurobipy)."""
    md = gp.Model()
    md.Params.OutputFlag = 0
    y = {v: md.addVar(lb=0, ub=1) for v in V}
    d = {e: md.addVar() for e in sorted(D) if e[0] in S and e[1] in T}
    lam = {q: md.addVar() for q in cols}
    md.setObjective(gp.quicksum(y.values()), GRB.MINIMIZE)
    for s in S:
        md.addConstr(gp.quicksum(lam[q] for q in cols if s in q[1])
                     + gp.quicksum(d[e] for e in d if e[0] == s) == 1)
    for t in T:
        md.addConstr(gp.quicksum(lam[q] for q in cols if t in q[2])
                     + gp.quicksum(d[e] for e in d if e[1] == t) == 1)
    for v in V:
        md.addConstr(gp.quicksum(lam[q] for q in cols if v in q[0]) <= y[v])
    for Z in K:
        md.addConstr(gp.quicksum(y[v] for v in Z) >= 1)
    md.optimize()
    assert md.Status == GRB.OPTIMAL
    val = md.ObjVal
    md.dispose()
    return val


def F(*xs):
    return [Fraction(x) for x in xs]


class ControlesCaminhoABC(unittest.TestCase):
    """Caminho a–b–c, r=1, S={a}, T={c}: D=∅, K={{b}}, z_Q=OPT=1."""

    def setUp(self):
        self.V, self.neigh, self.D = caminho_abc()
        self.S, self.T = ['a'], ['c']
        self.K = [frozenset({'b'})]
        self.Q = colunas(self.S, self.T, self.V, self.neigh)

    def test_D_vazio_delta_zero_e_custos_reduzidos(self):
        self.assertEqual({e for e in self.D if e[0] in self.S and e[1] in self.T}, set())
        pi = {'a': Fraction(3)}
        tau = {'c': Fraction(0)}
        mu = {v: Fraction(1) for v in self.V}
        self.assertEqual(valor_delta(set(), pi, tau), 0)
        custos = {tuple(sorted(q[0])): custo_reduzido(q, pi, tau, mu) for q in self.Q}
        self.assertEqual(custos, {('b',): -2, ('a', 'b'): -1, ('b', 'c'): -1, ('a', 'b', 'c'): 0})

    def test_pricing_completo_certifica_um_e_busca_parcial_falsifica(self):
        pi = {'a': Fraction(3)}
        tau = {'c': Fraction(0)}
        mu = {v: Fraction(1) for v in self.V}
        kappa = [Fraction(0)]
        lb, ell = certificar_enum(self.S, self.T, self.V, set(), self.K, self.neigh,
                                  pi, tau, mu, kappa, cap_atingido=False)
        self.assertEqual((ell, lb), (-2, 1))
        L = valor_L(self.S, self.T, self.V, self.K, pi, tau, mu, kappa)
        self.assertEqual(L, 3)
        # Busca limitada a W = V: 0 é cota superior de c*, não inferior.
        falso = lb_cg(L, Fraction(0), Fraction(0), 1)
        self.assertEqual(falso, 3)
        self.assertGreater(falso, 1)  # acima de OPT = 1: certificado falso

    def test_eta_positivo_e_necessario(self):
        pi = {'a': Fraction(2)}
        tau = {'c': Fraction(0)}
        mu = {'a': Fraction(0), 'b': Fraction(2), 'c': Fraction(0)}
        kappa = []
        lb, ell = certificar_enum(self.S, self.T, self.V, set(), [], self.neigh,
                                  pi, tau, mu, kappa, cap_atingido=False)
        L = valor_L(self.S, self.T, self.V, [], pi, tau, mu, kappa)
        self.assertEqual((ell, L, lb), (0, 1, 1))
        sem_eta = sum(pi.values()) + sum(tau.values())
        self.assertEqual(sem_eta, 2)
        self.assertGreater(sem_eta, 1)  # sem η o dual passaria de OPT = 1

    def test_parada_com_vetor_zero_nao_e_convergencia(self):
        zero = {v: Fraction(0) for v in self.V}
        pi, tau = {'a': Fraction(0)}, {'c': Fraction(0)}
        lb, ell = certificar_enum(self.S, self.T, self.V, set(), self.K, self.neigh,
                                  pi, tau, zero, [Fraction(0)], cap_atingido=False)
        self.assertEqual((ell, lb), (0, 0))
        self.assertGreaterEqual(ell, -EPS)  # critério ℓ ≥ −10⁻⁶ satisfeito
        if HAVE_GUROBI:
            U = lp_master(self.S, self.T, self.V, set(), [(frozenset(self.V), frozenset(self.S),
                                                           frozenset(self.T))], self.K)
            self.assertEqual(round(U, 9), 3)
            self.assertGreater(U - lb, EPS)  # G2 recusa: gap 3 > ε

    @unittest.skipUnless(HAVE_GUROBI, 'requer gurobipy')
    def test_rmp_acima_do_lp_completo_e_convergencia_g2(self):
        full = (frozenset(self.V), frozenset(self.S), frozenset(self.T))
        z_R0 = lp_master(self.S, self.T, self.V, set(), [full], self.K)
        z_Q = lp_master(self.S, self.T, self.V, set(), self.Q, self.K)
        self.assertAlmostEqual(z_R0, 3, places=7)
        self.assertAlmostEqual(z_Q, 1, places=7)
        # Dual ótimo do RMP inicial: certificado ainda não converge (G2).
        pi, tau = {'a': Fraction(3)}, {'c': Fraction(0)}
        mu = {v: Fraction(1) for v in self.V}
        lb, ell = certificar_enum(self.S, self.T, self.V, set(), self.K, self.neigh,
                                  pi, tau, mu, [Fraction(0)], cap_atingido=False)
        self.assertEqual(lb, 1)
        self.assertGreater(z_R0 - lb, EPS)
        # Após a coluna ({b},{a},{c}): dual π_a=1, μ_b=1 converge com gap 0.
        col = (frozenset({'b'}), frozenset(self.S), frozenset(self.T))
        z_R1 = lp_master(self.S, self.T, self.V, set(), [full, col], self.K)
        pi, tau = {'a': Fraction(1)}, {'c': Fraction(0)}
        mu = {'a': Fraction(0), 'b': Fraction(1), 'c': Fraction(0)}
        lb, ell = certificar_enum(self.S, self.T, self.V, set(), self.K, self.neigh,
                                  pi, tau, mu, [Fraction(0)], cap_atingido=False)
        self.assertEqual((ell, lb), (0, 1))
        self.assertAlmostEqual(z_R1, 1, places=7)
        self.assertLessEqual(z_R1 - lb, EPS)
        self.assertLessEqual(lb, z_Q + EPS)


class ControlePermanencia(unittest.TestCase):
    """Dois vértices ligados, r=1, S=T={a}, K=∅: D={(a,a)}, z_Q=OPT=0."""

    def test_delta_negativo_invalida_l_menos_m_eps(self):
        V = ['a', 'b']
        neigh, D = alcance(V, [('a', 'b')], 1)
        S, T = ['a'], ['a']
        self.assertIn(('a', 'a'), D)
        pi, tau = {'a': Fraction(1)}, {'a': Fraction(0)}
        mu = {'a': 1 - EPS / 2, 'b': Fraction(1)}
        Q = colunas(S, T, V, neigh)
        self.assertEqual(c_estrela(Q, pi, tau, mu), -EPS / 2)
        L = valor_L(S, T, V, [], pi, tau, mu, [])
        ell, delta = c_estrela(Q, pi, tau, mu), valor_delta({('a', 'a')}, pi, tau)
        self.assertEqual((L, delta), (1, -1))
        self.assertEqual(lb_cg(L, ell, delta, 1), 0)
        self.assertGreater(L - 1 * EPS, 0)  # a observação (iv) antiga seria falsa
        # Versão corrigida: δ ≥ −γ  ⇒  LB ≥ max{0, L − m·max(ε, γ)}.
        gamma = -delta
        self.assertGreaterEqual(lb_cg(L, ell, delta, 1), max(Fraction(0), L - max(EPS, gamma)))


class ControlesAritmetica(unittest.TestCase):
    def test_float_vira_racional_exato_e_projecao(self):
        self.assertNotEqual(Fraction(0.1), Fraction(1, 10))
        self.assertEqual(projetar(0.5), Fraction(1, 2))
        self.assertEqual(projetar(-1e-17, nao_negativo=True), 0)
        for ruim in (float('nan'), float('inf'), float('-inf')):
            with self.assertRaises(ValueError):
                projetar(ruim)

    def test_exportacao_para_baixo_e_arredondamento_inteiro(self):
        self.assertLessEqual(Fraction(exportar_para_baixo(Fraction(1, 3))), Fraction(1, 3))
        self.assertEqual(str(exportar_para_baixo(Fraction(2, 3))), '0.666666666666')
        self.assertEqual(exportar_para_baixo(Fraction(-1, 3)) <= Decimal(-1) / Decimal(3), True)
        self.assertEqual(arredondar_inteiro(Fraction(1)), 1)
        self.assertEqual(arredondar_inteiro(Fraction(2) - Fraction(1, 10**9)), 2)
        self.assertEqual(arredondar_inteiro(Fraction(1) + Fraction(1, 10**7)), 1)

    def test_enum_truncado_nao_certifica(self):
        V, neigh, D = caminho_abc()
        with self.assertRaises(RuntimeError):
            certificar_enum(['a'], ['c'], V, D, [], neigh, {'a': Fraction(3)}, {'c': Fraction(0)},
                            {v: Fraction(1) for v in V}, [], cap_atingido=True)


@unittest.skipUnless(HAVE_GUROBI, 'requer gurobipy')
class ControlesEnumeracao(unittest.TestCase):
    def test_enumerar_conexos_cobre_todos_os_conexos(self):
        rng = random.Random(20261009)
        for _ in range(25):
            V, S, T, neigh, D = instancia_aleatoria(rng)
            esperado = conexos_forca_bruta(V, neigh)
            lista, trunc = enumerar_conexos(grafo_H_fcc(V, [(u, w) for u in V for w in neigh[u]]),
                                            V, len(esperado) + 1)
            self.assertFalse(trunc)
            self.assertEqual(set(lista), esperado)
            self.assertEqual(len(lista), len(set(lista)))

    def test_cap_igual_ao_total_e_marcado_como_truncado(self):
        V, neigh, _ = caminho_abc()
        H = grafo_H_fcc(V, [(u, w) for u in V for w in neigh[u]])
        total = len(conexos_forca_bruta(V, neigh))
        self.assertEqual(total, 6)
        _, trunc_igual = enumerar_conexos(H, V, total)
        _, trunc_menor = enumerar_conexos(H, V, total - 1)
        _, trunc_maior = enumerar_conexos(H, V, total + 1)
        self.assertTrue(trunc_igual)   # conservador: cap atingido ⇒ sem certificado
        self.assertTrue(trunc_menor)
        self.assertFalse(trunc_maior)  # só cap > total prova cobertura completa


class ControlesLimitesGlobais(unittest.TestCase):
    """N1 (analítico) e N2 (caixa): validade ℓ ≤ c* em racionais exatos."""

    def sorteio(self, rng, S, T, V):
        pi = {s: Fraction(rng.randint(-8, 8), 4) for s in S}
        tau = {t: Fraction(rng.randint(-8, 8), 4) for t in T}
        mu = {v: Fraction(rng.randint(0, 8), 4) for v in V}
        return pi, tau, mu

    def test_n1_analitico_e_cota_inferior_de_c_estrela(self):
        rng = random.Random(7)
        for _ in range(200):
            V, S, T, neigh, D = instancia_aleatoria(rng)
            pi, tau, mu = self.sorteio(rng, S, T, V)
            Q = colunas(S, T, V, neigh)
            self.assertLessEqual(ell_analitico(S, T, V, pi, tau, mu), c_estrela(Q, pi, tau, mu))

    def test_caixa_com_multiplicadores_arbitrarios_e_cota_inferior(self):
        rng = random.Random(11)
        for _ in range(150):
            V, S, T, neigh, D = instancia_aleatoria(rng)
            pi, tau, mu = self.sorteio(rng, S, T, V)
            ub, linhas = linhas_pricing(S, T, V, neigh)
            c = objetivo_pricing(S, T, V, pi, tau, mu)
            cstar = c_estrela(colunas(S, T, V, neigh), pi, tau, mu)
            for _ in range(3):
                duais = [Fraction(rng.randint(-8, 8), 4) if sent == '=' else
                         Fraction(rng.randint(0, 8), 4) for (_c, sent, _r) in linhas]
                self.assertLessEqual(ell_caixa(ub, linhas, c, duais), cstar)

    @unittest.skipUnless(HAVE_GUROBI, 'requer gurobipy')
    def test_caixa_com_duais_do_lp_e_cota_valida_e_nao_vazia(self):
        rng = random.Random(13)
        for _ in range(40):
            V, S, T, neigh, D = instancia_aleatoria(rng)
            pi, tau, mu = self.sorteio(rng, S, T, V)
            ub, linhas = linhas_pricing(S, T, V, neigh)
            c = objetivo_pricing(S, T, V, pi, tau, mu)
            md = gp.Model()
            md.Params.OutputFlag = 0
            md.Params.Method = 1
            var = {j: md.addVar(lb=0, ub=ub[j]) for j in ub}
            md.setObjective(gp.quicksum(float(c[j]) * var[j] for j in c), GRB.MINIMIZE)
            rows = []
            for coefs, sent, rhs in linhas:
                ex = gp.quicksum(a * var[j] for j, a in coefs.items())
                rows.append(md.addConstr(ex >= rhs) if sent == '>=' else md.addConstr(ex == rhs))
            md.optimize()
            self.assertEqual(md.Status, GRB.OPTIMAL)
            duais = [projetar(r.Pi, nao_negativo=(s == '>=')) for r, (_c, s, _h) in zip(rows, linhas)]
            lp = md.ObjVal
            md.dispose()
            cstar = c_estrela(colunas(S, T, V, neigh), pi, tau, mu)
            ell = ell_caixa(ub, linhas, c, duais)
            self.assertLessEqual(ell, cstar)
            self.assertGreaterEqual(float(ell), lp - 1e-6)  # exatidão numérica do dual, não prova


@unittest.skipUnless(HAVE_GUROBI, 'requer gurobipy')
class ControlesProjecaoPricing(unittest.TestCase):
    """proj_{x,a,b}(soluções inteiras de P1–P5) = {(1_W,1_I,1_J) : (W,I,J) ∈ Q}."""

    def viavel(self, S, T, V, neigh, W, I, J):
        ub, linhas = linhas_pricing(S, T, V, neigh)
        md = gp.Model()
        md.Params.OutputFlag = 0
        var = {}
        for j, u in ub.items():
            if j[0] in ('x', 'a', 'b'):
                val = {'x': j[1] in W, 'a': j[1] in I, 'b': j[1] in J}[j[0]]
                var[j] = md.addVar(lb=int(val), ub=int(val))
            elif j[0] == 'rho':
                var[j] = md.addVar(vtype=GRB.BINARY)
            else:
                var[j] = md.addVar(lb=0, ub=u)
        for coefs, sent, rhs in linhas:
            ex = gp.quicksum(a * var[j] for j, a in coefs.items())
            md.addConstr(ex >= rhs) if sent == '>=' else md.addConstr(ex == rhs)
        md.optimize()
        ok = md.Status == GRB.OPTIMAL
        md.dispose()
        return ok

    def confere_exaustivo(self, S, T, V, neigh):
        Q = {(W, I, J) for (W, I, J) in colunas(S, T, V, neigh)}
        for kw in range(len(V) + 1):
            for W in itertools.combinations(V, kw):
                for ki in range(len(S) + 1):
                    for I in itertools.combinations(S, ki):
                        for kj in range(len(T) + 1):
                            for J in itertools.combinations(T, kj):
                                esperado = (frozenset(W), frozenset(I), frozenset(J)) in Q
                                self.assertEqual(self.viavel(S, T, V, neigh, set(W), set(I), set(J)),
                                                 esperado, (W, I, J))

    def test_caminho_abc_todos_os_padroes(self):
        V, neigh, _ = caminho_abc()
        self.confere_exaustivo(['a'], ['c'], V, neigh)

    def test_vertice_unico_com_s_igual_t(self):
        neigh, _ = alcance(['a'], [], 1)
        self.confere_exaustivo(['a'], ['a'], ['a'], neigh)

    def test_terminal_compartilhado_e_terminal_instalado_como_rele(self):
        # a–t1–t2 e s2–t1, r=1; t1 ∈ S∩T como vértice compartilhado
        V = ['s1', 't1', 't2']
        neigh, _ = alcance(V, [('s1', 't1'), ('t1', 't2')], 1)
        self.confere_exaustivo(['s1', 't1'], ['t1', 't2'], V, neigh)

    def test_instancias_aleatorias_minusculas(self):
        rng = random.Random(17)
        for _ in range(6):
            V, S, T, neigh, _ = instancia_aleatoria(rng, 2, 4)
            self.confere_exaustivo(S, T, V, neigh)


if __name__ == '__main__':
    unittest.main()
