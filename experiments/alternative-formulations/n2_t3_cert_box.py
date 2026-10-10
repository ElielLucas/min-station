"""N2-T3 / E3 (T5--T6): limite global N2 por relaxação racional de P0--P5.

O problema LP é reconstruído de dados combinatórios, sem extrair coeficientes
numéricos de Gurobi. Toda igualdade tem forma Aw=b; toda desigualdade Bw>=h;
e todas as variáveis têm limites racionais 0<=w<=u. Para theta livre e nu>=0:

  ell = theta*b + nu*h + sum_j u_j * min(0, c_j - (A^T theta)_j
                                                     - (B^T nu)_j).

Esse ell é um limite inferior global de pricing, inclusive com theta/nu não
ótimos, porque a caixa contém a relaxação inteira do MIP. A rotina de
verificação recompõe a matriz racional original e a evidência; hashes e
ObjBound/ObjBoundC isolados NÃO são provas. O certificado L1 é apenas do LP
completo F-CC+K relativo ao H fornecido. H=G^r/master e H-K são E4/E5.

`propose_lp_multipliers` é APENAS um gerador opcional de candidatos via SciPy;
a verificação racional independente não depende de SciPy/Gurobi.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from fractions import Fraction

from n2_t3_cert_core import (
    CERTIFIED,
    LP_SCOPE,
    UNCERTIFIED,
    CertifiedIteration,
    GlobalPricingBound,
    RationalDual,
    _abstain,
    _freeze,
    _frac_pair,
    _rational,
    _theorem_l_formula,
    _validated_dual,
    vector_digest,
)
from n2_t3_cert_enum import _canonical_graph, graph_digest

ZERO = Fraction(0)
ONE = Fraction(1)
BOX_SOURCE = 'N2'
BOX_FORMULA = 'N2-BOX-v2.1'


@dataclass(frozen=True)
class LinearRow:
    """Linha exata, nomeada e esparsa. Semântica depende do grupo A ou B."""
    name: tuple
    coefficients: Mapping
    rhs: Fraction


@dataclass(frozen=True)
class RationalLP:
    """Relaxação racional original P0--P5, não um modelo de solver.

    Os limites superiores de g e f são redundantes no inteiro, mas necessários
    para a prova por caixa; g<=n, f<=n-1. As binárias são relaxadas em [0,1].
    """
    variables: tuple
    objective: Mapping
    upper: Mapping
    equalities: tuple[LinearRow, ...]
    inequalities: tuple[LinearRow, ...]
    instance_key: str
    vector_digest: str
    graph_digest: str
    lp_digest: str


@dataclass(frozen=True)
class BoxAbstention:
    status: str
    source: str
    vector_digest: str
    reason: str
    ell: None = None


def _row(name, terms, rhs=0):
    coeff = {}
    for var, value in terms:
        val = _rational(value, 'coeficiente da matriz P0--P5')
        coeff[var] = coeff.get(var, ZERO) + val
    return LinearRow(tuple(name), _freeze({v: c for v, c in coeff.items() if c}),
                     _rational(rhs, 'rhs da matriz P0--P5'))


def _tags(key):
    return [[type(value).__name__, value] for value in key]


def _lp_payload(lp):
    def row_data(row):
        return {'name': _tags(row.name), 'rhs': _frac_pair(row.rhs),
                'coeff': [[_tags(v), _frac_pair(row.coefficients[v])]
                          for v in lp.variables if v in row.coefficients]}
    return {
        'format': 'MIN-STATION-N2-T3-P0-P5-LP-V1',
        'instance_key': lp.instance_key,
        'vector_digest': lp.vector_digest,
        'graph_digest': lp.graph_digest,
        'variables': [_tags(v) for v in lp.variables],
        'objective': [_frac_pair(lp.objective[v]) for v in lp.variables],
        'upper': [_frac_pair(lp.upper[v]) for v in lp.variables],
        'equalities': [row_data(row) for row in lp.equalities],
        'inequalities': [row_data(row) for row in lp.inequalities],
    }


def build_rational_pricing_lp(dual: RationalDual, H: Mapping) -> RationalLP:
    """Constrói do zero P0--P5; valida H/D e vetor racional a cada chamada."""
    _validated_dual(dual)
    graph = _canonical_graph(dual, H)
    V, S, T = dual.V, dual.S, dual.T
    n = len(V)
    arcs = tuple((u, v) for u in V for v in sorted(graph[u]))
    xs = [('x', v) for v in V]
    origins = [('a', s) for s in S]
    destinations = [('b', t) for t in T]
    roots = [('rho', v) for v in V]
    sources = [('g', v) for v in V]
    flows = [('f', u, v) for u, v in arcs]
    variables = tuple(xs + origins + destinations + roots + sources + flows)
    objective = {}
    upper = {}
    for var in variables:
        kind = var[0]
        objective[var] = (dual.mu[var[1]] if kind == 'x' else
                          -dual.pi[var[1]] if kind == 'a' else
                          -dual.tau[var[1]] if kind == 'b' else ZERO)
        upper[var] = (Fraction(n) if kind == 'g' else
                      Fraction(n - 1) if kind == 'f' else ONE)

    eq = []
    ge = []
    # P1a, P1b: a_s/b_t <= sum_{v in N_H[terminal]} x_v.
    for s in S:
        ge.append(_row(('P1a', s),
                       [(('x', v), ONE) for v in sorted({s} | graph[s])]
                       + [(('a', s), -ONE)]))
    for t in T:
        ge.append(_row(('P1b', t),
                       [(('x', v), ONE) for v in sorted({t} | graph[t])]
                       + [(('b', t), -ONE)]))
    # P2: equilibrio e ao menos um terminal de origem.
    eq.append(_row(('P2bal',),
                   [(('a', s), ONE) for s in S]
                   + [(('b', t), -ONE) for t in T]))
    ge.append(_row(('P2min',), [(('a', s), ONE) for s in S], ONE))
    # P3: raiz única; rho<=x, g<=n*rho.
    eq.append(_row(('P3root',), [(('rho', v), ONE) for v in V], ONE))
    for v in V:
        ge.append(_row(('P3rx', v), [(('x', v), ONE), (('rho', v), -ONE)]))
        ge.append(_row(('P3g', v), [(('rho', v), n), (('g', v), -ONE)]))
        # P4: g_v + in-flow - out-flow = x_v.
        eq.append(_row(('P4', v),
                       [(('g', v), ONE), (('x', v), -ONE)]
                       + [(('f', u, v), ONE) for u in sorted(graph[v])]
                       + [(('f', v, w), -ONE) for w in sorted(graph[v])]))
    # P5: f_uv <= (n-1)*x_u and <= (n-1)*x_v.
    for u, v in arcs:
        ge.append(_row(('P5u', u, v),
                       [(('x', u), n - 1), (('f', u, v), -ONE)]))
        ge.append(_row(('P5w', u, v),
                       [(('x', v), n - 1), (('f', u, v), -ONE)]))

    draft = RationalLP(variables, _freeze(objective), _freeze(upper),
                       tuple(eq), tuple(ge), dual.instance_key,
                       dual.vector_digest, graph_digest(graph, V), '')
    return RationalLP(draft.variables, draft.objective, draft.upper,
                      draft.equalities, draft.inequalities,
                      draft.instance_key, draft.vector_digest,
                      draft.graph_digest, vector_digest(_lp_payload(draft)))


def _same_lp(original, dual, H):
    """Verificação por reconstrução independente do objeto recebido.

    Em especial, lp_digest pré-computado não é tratado como assinatura confiável.
    """
    expected = build_rational_pricing_lp(dual, H)
    return (isinstance(original, RationalLP)
            and original == expected
            and original.lp_digest == vector_digest(_lp_payload(original)))


def _multipliers(rows, raw, name, *, nonnegative=False):
    keys = tuple(row.name for row in rows)
    if raw is None:
        return _freeze({key: ZERO for key in keys})
    if not isinstance(raw, Mapping) or set(raw) != set(keys):
        raise ValueError(f'{name}: exatamente uma entrada por linha da matriz')
    output = {}
    for key in keys:
        value = _rational(raw[key], name)
        # Projetar ν negativo explicitamente para 0: continua uma prova válida.
        output[key] = max(ZERO, value) if nonnegative else value
    return _freeze(output)


def _box_formula(lp: RationalLP, theta: Mapping, nu: Mapping):
    """Resultado racional e resíduos por variável da fórmula universal N2."""
    constant = (sum((theta[row.name] * row.rhs for row in lp.equalities), ZERO)
                + sum((nu[row.name] * row.rhs for row in lp.inequalities), ZERO))
    adjusted = dict(lp.objective)
    for row in lp.equalities:
        factor = theta[row.name]
        for var, coeff in row.coefficients.items():
            adjusted[var] -= factor * coeff
    for row in lp.inequalities:
        factor = nu[row.name]
        for var, coeff in row.coefficients.items():
            adjusted[var] -= factor * coeff
    contribution = sum((lp.upper[v] * min(ZERO, adjusted[v]) for v in lp.variables), ZERO)
    return constant + contribution, constant, contribution


def certify_box_bound(dual: RationalDual, H: Mapping, lp: RationalLP,
                      theta: Mapping | None = None,
                      nu: Mapping | None = None) -> GlobalPricingBound | BoxAbstention:
    """Recompõe a matriz original e calcula ell_N2 exatamente.

    `theta/nu` são sugestões arbitrárias. Em particular, zero é seguro mesmo
    sem solver. Um candidato LP numérico só serve após racionalização exata.
    """
    _validated_dual(dual)
    if not _same_lp(lp, dual, H):
        return BoxAbstention(UNCERTIFIED, BOX_SOURCE, dual.vector_digest,
                            'LP racional não corresponde à matriz original P0--P5')
    theta_r = _multipliers(lp.equalities, theta, 'theta')
    nu_r = _multipliers(lp.inequalities, nu, 'nu', nonnegative=True)
    ell, constant, box_part = _box_formula(lp, theta_r, nu_r)
    evidence = _freeze({
        'formula': BOX_FORMULA,
        'instance_key': dual.instance_key,
        'revision': dual.revision,
        'solve_id': dual.solve_id,
        'k_hash': dual.k_hash,
        'vector_digest': dual.vector_digest,
        'graph_digest': lp.graph_digest,
        'lp_digest': lp.lp_digest,
        'theta': tuple((row.name, theta_r[row.name]) for row in lp.equalities),
        'nu': tuple((row.name, nu_r[row.name]) for row in lp.inequalities),
        'constant': constant,
        'box_contribution': box_part,
        'n_variables': len(lp.variables),
        'n_equalities': len(lp.equalities),
        'n_inequalities': len(lp.inequalities),
        'method': 'BOX-EXACT-FRACTION',
    })
    return GlobalPricingBound(ell, BOX_SOURCE, dual.vector_digest, evidence)


def evaluate_box_theorem_l(dual: RationalDual, H: Mapping, lp: RationalLP,
                           bound, D) -> CertifiedIteration:
    """Reverifica a prova N2, inclusive multiplicadores e identidade da matriz.

    Forjar um GlobalPricingBound ou atribuir um valor a ObjBoundC não certifica.
    """
    _validated_dual(dual)
    if not isinstance(bound, GlobalPricingBound) or bound.source != BOX_SOURCE:
        return _abstain(dual, 'N2: fonte/evidência de bound global ausente')
    if bound.vector_digest != dual.vector_digest:
        return _abstain(dual, 'N2: limite pertence a outro vetor/iteração')
    try:
        if tuple(D) != dual.D:
            return _abstain(dual, 'N2: pares diretos D não coincidem com snapshot')
        if not isinstance(bound.evidence, Mapping):
            return _abstain(dual, 'N2: evidência ausente')
        theta = dict(bound.evidence['theta'])
        nu = dict(bound.evidence['nu'])
        rebuilt = certify_box_bound(dual, H, lp, theta, nu)
    except (ValueError, TypeError, KeyError, OverflowError) as exc:
        return _abstain(dual, f'N2: evidência/LP inválidos: {exc}')
    if (not isinstance(rebuilt, GlobalPricingBound)
            or type(bound.ell) is not Fraction or bound.ell != rebuilt.ell
            or dict(bound.evidence) != dict(rebuilt.evidence)):
        return _abstain(dual, 'N2: prova não coincide com recálculo racional')
    result = _theorem_l_formula(dual, rebuilt.ell, dual.D)
    return CertifiedIteration(
        CERTIFIED, LP_SCOPE, result.lb_exact, BOX_SOURCE,
        'N2: matriz racional P0--P5 reconstruída; theta/nu projetados e '
        'Teorema L avaliados exatamente para a mesma iteração; '
        f'LP={lp.lp_digest}; H={lp.graph_digest}; '
        'vínculo H=G^r/master e H-K/MIN-STATION pendentes E4/E5',
        dual.revision, dual.solve_id, dual.vector_digest, dual.k_hash,
        result.l_exact, result.delta_exact, result.ell_exact,
        result.winning_branch,
    )


def propose_lp_multipliers(lp: RationalLP):
    """Candidatos numéricos opcionais do LP relaxado via scipy.optimize.linprog.

    NÃO é verificador nem prova. O usuário deve passar o retorno por
    certify_box_bound, que reconstrói a matriz original e avalia tudo em
    Fraction. Se SciPy estiver ausente, ocorre ImportError explícito.
    """
    from scipy.optimize import linprog  # import opcional: a prova não depende disto

    def matrix(rows, sign):
        return [[sign * float(row.coefficients.get(var, ZERO)) for var in lp.variables]
                for row in rows]

    result = linprog(
        c=[float(lp.objective[v]) for v in lp.variables],
        A_eq=matrix(lp.equalities, 1),
        b_eq=[float(row.rhs) for row in lp.equalities],
        A_ub=matrix(lp.inequalities, -1),
        b_ub=[-float(row.rhs) for row in lp.inequalities],
        bounds=[(0, float(lp.upper[v])) for v in lp.variables],
        method='highs',
    )
    if not result.success:
        raise RuntimeError(f'LP auxiliar não devolveu multiplicadores: {result.message}')
    theta = _freeze({row.name: _rational(float(value), 'theta do LP numérico')
                     for row, value in zip(lp.equalities, result.eqlin.marginals, strict=True)})
    nu = _freeze({row.name: max(ZERO, _rational(float(-value), 'nu do LP numérico'))
                  for row, value in zip(lp.inequalities, result.ineqlin.marginals, strict=True)})
    return theta, nu
