"""AS-03: preditor estrutural, orçamento e classificação sem solver.

A estimativa de memória é um PROXY heurístico, não limite seguro para RSS.
Não elimina casos do denominador de aplicabilidade do benchmark AS-00.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class SizeEstimate:
    n: int
    m: int
    a: int
    k: int
    h: int
    variables: int
    constraints: int
    nonzeros_upper: int
    memory_proxy_bytes: int
    memory_estimator: str = 'heuristic_proxy_v1_not_rss_bound'


@dataclass(frozen=True)
class BuildBudget:
    max_variables: int | None = None
    max_constraints: int | None = None
    max_nonzeros: int | None = None
    max_memory_bytes: int | None = None
    remaining_seconds: float | None = None
    minimum_build_reserve_seconds: float = 0.0

    def __post_init__(self):
        for field in ('max_variables', 'max_constraints', 'max_nonzeros', 'max_memory_bytes'):
            value = getattr(self, field)
            if value is not None and (type(value) is not int or value < 0):
                raise ValueError(f'{field} deve ser inteiro não negativo ou None')
        for field in ('remaining_seconds', 'minimum_build_reserve_seconds'):
            value = getattr(self, field)
            if (value is not None and
                (not isinstance(value, (float, int)) or isinstance(value, bool) or
                 value != value or value == float('inf') or value < 0)):
                raise ValueError(f'{field} deve ser número finito não negativo')


def estimate_size(instance, blocks, *, k_cuts: tuple[tuple[str, ...], ...] = ()) -> SizeEstimate:
    """Conta variáveis exatamente; demais valores são limites/conservadores.

    Fórmula AS03-03: n + k(a+n+m) + h.
    h = |S∩T|, porque cada origem pertence a exatamente um bloco.
    k_cuts guarda os cortes já conhecidos para contabilizar A6.
    """
    from as03_grouping import _snapshot, _canonical_blocks

    V, S, T, arcs, _ = _snapshot(instance)
    norm = _canonical_blocks(blocks, S, k=len(blocks))
    n, m, a, k = len(V), len(S), len(arcs), len(norm)
    h = len(set(S) & set(T))
    valid_v = set(V)
    cuts = tuple(tuple(z) for z in k_cuts)
    if any(not z or not set(z) <= valid_v or len(set(z)) != len(z) for z in cuts):
        raise ValueError('Cortes inválidos')
    nvars = n + k * (a + n + m) + h
    # A1, A2, A4: 3*k*n; A3: m; A5: n; A6: |K|.
    nrows = 3 * k * n + m + n + len(cuts)
    # Limite superior simples considerando todas as incidências e coeficientes
    # não cancelados. Podem existir menos coeficientes reais.
    nnz_upper = 2*k*a + 2*k*m + 5*k*n + n + 2*h + sum(len(z) for z in cuts)
    # Proxy com overhead explícito, NÃO promessa de alocação real.
    proxy = 4 * (192*nvars + 128*nrows + 32*nnz_upper)
    return SizeEstimate(n, m, a, k, h, nvars, nrows, nnz_upper, proxy)


@dataclass(frozen=True)
class BuildDecision:
    status: str
    reason: str
    case_name: str
    arm_id: str
    applicable: bool
    measured_lp: float | None
    measured_mip: float | None
    estimate: SizeEstimate | None
    partition_hash: str | None
    policy: str
    seed: int

    def to_record(self) -> dict:
        obj = asdict(self)
        obj['estimate'] = asdict(self.estimate) if self.estimate else None
        return obj


def decide_build(case_name: str, arm_id: str, grouping, estimate: SizeEstimate | None,
                 budget: BuildBudget, *, reason_if_na: str | None = None) -> BuildDecision:
    """Admissibilidade pré-construção; NA/size/memory/budget preservam a linha.

    A classe READY_FOR_BUILD autoriza apenas tentativa de construção,
    não significa que a alocação real caberá em memória/tempo.
    """
    if not case_name or not arm_id:
        raise ValueError('Identidade de caso e braço obrigatória')
    if grouping is None or estimate is None:
        status, reason = 'NOT_APPLICABLE', reason_if_na or 'partição não disponível'
    elif ((budget.max_variables is not None and estimate.variables > budget.max_variables)
          or (budget.max_constraints is not None and estimate.constraints > budget.max_constraints)
          or (budget.max_nonzeros is not None and estimate.nonzeros_upper > budget.max_nonzeros)):
        status, reason = 'NOT_BUILT_SIZE', 'limite de representação excedido'
    elif budget.max_memory_bytes is not None and estimate.memory_proxy_bytes > budget.max_memory_bytes:
        status, reason = 'NOT_BUILT_MEMORY', 'proxy heurístico de memória excede limite'
    elif (budget.remaining_seconds is not None
          and budget.remaining_seconds < budget.minimum_build_reserve_seconds):
        status, reason = 'NOT_BUILT_BUDGET', 'tempo remanescente inferior à reserva mínima pré-registrada'
    else:
        status, reason = 'READY_FOR_BUILD', 'filtro pré-construção aprovado; uso real não garantido'
    return BuildDecision(status, reason, case_name, arm_id, True, None, None,
                         estimate, grouping.partition_hash if grouping else None,
                         grouping.policy if grouping else 'not_applicable',
                         grouping.seed if grouping else 0)
