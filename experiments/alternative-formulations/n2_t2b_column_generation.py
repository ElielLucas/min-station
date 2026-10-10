"""N2-T2B / Entrega 3: geração de colunas na raiz, master F-CC+K + pricing P0--P5.

Matemática: revisão v2.1, §§2--6. Componentes: RestrictedMaster (Entrega 1) e
price() (Entrega 2). Não implementa branching, certificação N2-T3, ENUM/N1/N2,
regressão N2-T4 nem escrita de resultados.

Uso:
    result = run_column_generation(S, T, V, adj, A_r, r, K=K, k_hash=digest,
                                   max_iterations=200, work_limit=164.0)
    result.stop_reason            # ver STOP_REASONS
    result.rmp_objective          # z_R numérico; NÃO é LB de MIN-STATION

Ciclo (uma iteração = uma resolução do master + no máximo um pricing):
  1. resolver o RMP; sem snapshot dual válido: MASTER_FAILURE (ou limite global);
  2. price(master, snapshot) com o snapshot DESTA resolução (nunca price_vector);
  3. coluna negativa: conferir rc pelo master com o mesmo snapshot, rejeitar
     duplicata, add_column (revalida e invalida o snapshot), voltar a 1;
  4. sem coluna negativa sob término numérico ótimo: NUMERICAL_STATIONARY;
     em qualquer outro término: PRICING_INCOMPLETE (ou limite global).

Garantias e limites:
- Toda coluna inserida pertence a Q (validada pelo pricing e por add_column)
  e tem rc < -entry_tolerance recalculado pelo master com o snapshot corrente.
- Q é finito e duplicatas encerram o laço; logo o ciclo termina mesmo sem
  melhoria estrita (degeneração é registrada, não tratada como erro).
- certification_status é sempre UNCERTIFIED e convergence_status nunca é
  certificado: o pricing MIP é numérico (revisão v2.1 §6.3); G2 não é
  verificado. NUMERICAL_STATIONARY é diagnóstico (NUMERIC_UNCERTIFIED).
- Work: soma do atributo Work de cada solve de master e pricing; chamadas
  sem Work mensurável são contadas à parte e tornam total_work=None. Tempo:
  relógio de parede do controlador (inclui montagem). Limites globais são
  repassados como TimeLimit/WorkLimit restantes a cada subsolve.
"""
# E402: bootstrap do diretório experimental; E741: notação normativa W,I,J.
# ruff: noqa: E402, E741
import math
import sys
import time
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import gurobipy as gp
from n2_t2b_master import RestrictedMaster
from n2_t2b_pricing import (
    NEGATIVE_COLUMN, NO_INCUMBENT, NONNEGATIVE_INCUMBENT, NUMERICALLY_OPTIMAL,
    SOLVER_FAILURE, UNCERTIFIED, price,
)

# Motivos de parada. COMPLETED_NUMERICAL não é usado: seria sinônimo de
# NUMERICAL_STATIONARY, o único término "bem-sucedido" possível sem N2-T3.
NUMERICAL_STATIONARY = 'NUMERICAL_STATIONARY'
PRICING_INCOMPLETE = 'PRICING_INCOMPLETE'
MASTER_FAILURE = 'MASTER_FAILURE'
PRICING_FAILURE = 'PRICING_FAILURE'
DUPLICATE_COLUMN = 'DUPLICATE_COLUMN'
ITERATION_LIMIT = 'ITERATION_LIMIT'
WORK_LIMIT = 'WORK_LIMIT'
TIME_LIMIT = 'TIME_LIMIT'
WORK_UNMEASURED = 'WORK_UNMEASURED'
STOP_REASONS = frozenset({
    NUMERICAL_STATIONARY, PRICING_INCOMPLETE, MASTER_FAILURE, PRICING_FAILURE,
    DUPLICATE_COLUMN, ITERATION_LIMIT, WORK_LIMIT, TIME_LIMIT, WORK_UNMEASURED,
})
CONTINUE = 'CONTINUE'

# Estacionariedade numérica sem prova global; nunca "CERTIFIED".
NUMERIC_UNCERTIFIED = 'NUMERIC_UNCERTIFIED'
NOT_CONVERGED = 'NOT_CONVERGED'


def _measured(value):
    """Work válido: finito e >= 0. Negativo/NaN/ausente é inválido, nunca descontado."""
    return value is not None and math.isfinite(value) and value >= 0


@dataclass(frozen=True)
class SubsolveCost:
    """Custo de um solve; work=None quando o valor do solver é ausente ou inválido.

    forwarded_limits: TimeLimit/WorkLimit efetivamente passados ao solve;
    global_binding: nomes dos limites em que o restante global era o menor;
    raw_work: valor bruto devolvido pela API, preservado para auditoria.
    """
    kind: str
    work: float | None
    runtime: float | None
    forwarded_limits: Mapping
    global_binding: frozenset
    raw_work: float | None = None


@dataclass(frozen=True)
class IterationRecord:
    """Uma resolução do master e, se houve, a chamada de pricing seguinte.

    rmp_objective é z_R numérico (não LB). pricing_solver_bound é o ObjBoundC
    do pricing, registrado só como diagnóstico; não é usado em decisão.
    """
    iteration: int
    columns_before: int
    columns_after: int
    master_status: str
    master_revision: int
    master_solve_id: int
    rmp_objective: float | None
    objective_decrease: float | None
    degenerate_step: bool
    master_cost: SubsolveCost
    pricing_outcome: str | None
    pricing_termination: str | None
    pricing_status: str | None
    candidate_column: tuple | None
    candidate_reduced_cost: float | None
    pricing_solver_bound: float | None
    pricing_cost: SubsolveCost | None
    column_added: tuple | None
    cumulative_work: float | None
    cumulative_solver_runtime: float
    wall_elapsed: float
    decision: str
    note: str | None


@dataclass(frozen=True)
class ColumnGenerationResult:
    """Resultado imutável do controlador; nunca é certificado de LB.

    rmp_objective é o ObjVal da última resolução OPTIMAL do master;
    objective_reflects_all_columns indica se essa resolução já contém todas
    as colunas de columns (False se a parada ocorreu entre add e solve).
    """
    stop_reason: str
    message: str
    rmp_objective: float | None
    objective_reflects_all_columns: bool
    iterations: int
    pricing_calls: int
    columns_added: int
    degenerate_steps: int
    columns: tuple
    history: tuple
    k_hash: str
    n_K: int
    settings: Mapping
    total_work: float | None
    measured_work: float
    unmeasured_work_calls: int
    total_solver_runtime: float
    wall_time: float
    gurobi_version: tuple
    convergence_status: str = NOT_CONVERGED
    certification_status: str = UNCERTIFIED
    scope: str = 'ROOT_CG_NUMERICAL_ONLY'


def _limit_params(base, *, remaining_work, remaining_time):
    """Mescla limites por chamada do usuário com o orçamento global restante.

    Retorna (params, limites repassados, limites em que o global é o menor).
    """
    params = dict(base)
    forwarded, binding = {}, set()
    for name, remaining in (('WorkLimit', remaining_work), ('TimeLimit', remaining_time)):
        if remaining is None:
            continue
        per_call = params.get(name, math.inf)
        params[name] = forwarded[name] = min(remaining, per_call)
        if remaining <= per_call:
            binding.add(name)
    return params, MappingProxyType(forwarded), frozenset(binding)


def _validate_settings(max_iterations, work_limit, time_limit, entry_tolerance,
                       monotonicity_tolerance, rc_agreement_tolerance):
    if not isinstance(max_iterations, int) or isinstance(max_iterations, bool) \
            or max_iterations < 0:
        raise ValueError('max_iterations deve ser inteiro >= 0')
    for name, value in (('work_limit', work_limit), ('time_limit', time_limit)):
        if value is not None and (not math.isfinite(value) or value < 0):
            raise ValueError(f'{name} deve ser None ou finito >= 0')
    for name, value in (('entry_tolerance', entry_tolerance),
                        ('monotonicity_tolerance', monotonicity_tolerance),
                        ('rc_agreement_tolerance', rc_agreement_tolerance)):
        if not math.isfinite(value) or value < 0:
            raise ValueError(f'{name} deve ser finita e >= 0')


def run_column_generation(S, T, V, adj, A_r, r, *, K=None, k_hash=None,
                          max_iterations=1000, work_limit=None, time_limit=None,
                          master_params=None, pricing_params=None,
                          entry_tolerance=1e-7, monotonicity_tolerance=1e-7,
                          rc_agreement_tolerance=1e-9,
                          pricer=price, clock=time.monotonic):
    """Geração de colunas na raiz; ver docstring do módulo.

    max_iterations limita as chamadas de pricing; ao atingi-lo, o master já
    reotimizado com a última coluna é registrado e a parada é ITERATION_LIMIT.
    work_limit/time_limit são orçamentos globais (Work Gurobi / segundos de
    parede). master_params/pricing_params seguem as listas permitidas das
    APIs; seus TimeLimit/WorkLimit valem por chamada e nunca excedem o
    restante global. pricer e clock são pontos de substituição para testes.
    """
    _validate_settings(max_iterations, work_limit, time_limit, entry_tolerance,
                       monotonicity_tolerance, rc_agreement_tolerance)
    master_params = dict(master_params or {})
    pricing_params = dict(pricing_params or {})
    settings = MappingProxyType({
        'max_iterations': max_iterations, 'work_limit': work_limit, 'time_limit': time_limit,
        'master_params': MappingProxyType(master_params),
        'pricing_params': MappingProxyType(pricing_params),
        'entry_tolerance': entry_tolerance, 'monotonicity_tolerance': monotonicity_tolerance,
        'rc_agreement_tolerance': rc_agreement_tolerance,
        'pricer': getattr(pricer, '__name__', repr(pricer)),
    })
    start = clock()
    history = []
    state = {'work': 0.0, 'unmeasured': 0, 'runtime': 0.0}

    def elapsed():
        return clock() - start

    def remaining():
        rw = None if work_limit is None else work_limit - state['work']
        rt = None if time_limit is None else time_limit - elapsed()
        return rw, rt

    def account(kind, work, runtime, forwarded, binding):
        if _measured(work):
            state['work'] += work
        else:
            state['unmeasured'] += 1
        if runtime is not None and math.isfinite(runtime):
            state['runtime'] += runtime
        return SubsolveCost(kind, work if _measured(work) else None, runtime,
                            forwarded, binding, work)

    def budget_stop():
        """Motivo de parada antes de um novo subsolve, ou None."""
        if work_limit is not None and state['unmeasured']:
            return WORK_UNMEASURED, ('Work ausente ou inválido (não finito ou negativo) '
                                     'com orçamento global de Work ativo')
        rw, rt = remaining()
        if rw is not None and rw <= 0:
            return WORK_LIMIT, f'Work global esgotado ({state["work"]!r} >= {work_limit!r})'
        if rt is not None and rt <= 0:
            return TIME_LIMIT, f'tempo global esgotado ({elapsed()!r} s)'
        return None

    def overrun():
        """Orçamento global (Work ou tempo) ultrapassado pelo consumo já contabilizado.

        Reavaliado após cada subsolve, inclusive o último antes de decidir
        NUMERICAL_STATIONARY/PRICING_INCOMPLETE: o WorkLimit/TimeLimit por
        chamada é aproximado (overhead fora do solver, arredondamento do
        Gurobi), então o subsolve pode retornar OPTIMAL já além do orçamento
        global. Nesse caso o resultado do subsolve é descartado.
        """
        if work_limit is not None and state['work'] > work_limit:
            return WORK_LIMIT, (f'Work global ultrapassado: consumo {state["work"]!r} > '
                                f'limite {work_limit!r}; resultado do último subsolve descartado')
        if time_limit is not None and elapsed() > time_limit:
            return TIME_LIMIT, (f'tempo global ultrapassado: decorrido {elapsed()!r} s > '
                                f'limite {time_limit!r} s; resultado do último subsolve descartado')
        return None

    def interrupted_by_global(status_name, binding):
        """Limite do solve atingido em que o orçamento global era o limite efetivo."""
        if status_name == 'WORK_LIMIT' and 'WorkLimit' in binding:
            return WORK_LIMIT
        if status_name == 'TIME_LIMIT' and 'TimeLimit' in binding:
            return TIME_LIMIT
        return None

    master = None
    stop = message = None
    last_objective = None
    objective_current = False
    pricing_calls = columns_added = degenerate = 0
    try:
        master = RestrictedMaster(S, T, V, adj, A_r, r, K=K, k_hash=k_hash)
        iteration = 0
        while stop is None:
            pending = budget_stop()
            if pending:
                stop, message = pending
                break
            rw, rt = remaining()
            mparams, mforward, mbinding = _limit_params(master_params, remaining_work=rw,
                                                        remaining_time=rt)
            columns_before = len(master.columns)
            mres = master.solve(params=mparams)
            mcost = account('master', mres.work, mres.runtime, mforward, mbinding)
            record = dict(
                iteration=iteration, columns_before=columns_before,
                columns_after=columns_before, master_status=mres.status_name,
                master_revision=mres.revision, master_solve_id=mres.solve_id,
                rmp_objective=mres.objective_rmp, objective_decrease=None,
                degenerate_step=False, master_cost=mcost, pricing_outcome=None,
                pricing_termination=None, pricing_status=None, candidate_column=None,
                candidate_reduced_cost=None, pricing_solver_bound=None, pricing_cost=None,
                column_added=None, note=None,
            )

            def close(decision, note=None, rec=record):
                rec['decision'] = decision
                rec['note'] = note if note is not None else rec['note']
                rec['cumulative_work'] = None if state['unmeasured'] else state['work']
                rec['cumulative_solver_runtime'] = state['runtime']
                rec['wall_elapsed'] = elapsed()
                history.append(IterationRecord(**rec))

            snapshot = mres.dual
            exceeded = overrun()
            if exceeded:
                # O solve passou do orçamento (WorkLimit do Gurobi é aproximado):
                # seu resultado não é usado para decidir nada.
                stop, message = exceeded
                close(stop, message)
                break
            if snapshot is None:
                stop = interrupted_by_global(mres.status_name, mbinding) or MASTER_FAILURE
                message = f'master sem snapshot dual válido: {mres.status_name}; {mres.error}'
                close(stop, message)
                break
            if last_objective is not None:
                decrease = last_objective - mres.objective_rmp
                record['objective_decrease'] = decrease
                if decrease < -monotonicity_tolerance:
                    stop = MASTER_FAILURE
                    message = (f'objetivo do RMP aumentou após inserir coluna: '
                               f'{last_objective!r} -> {mres.objective_rmp!r}')
                    close(stop, message)
                    break
                if decrease <= monotonicity_tolerance:
                    record['degenerate_step'] = True
                    degenerate += 1
            last_objective, objective_current = mres.objective_rmp, True

            if iteration >= max_iterations:
                stop, message = ITERATION_LIMIT, f'{max_iterations} chamadas de pricing'
                close(stop, message)
                break
            pending = budget_stop()
            if pending:
                stop, message = pending
                close(stop, message)
                break

            rw, rt = remaining()
            pparams, pforward, pbinding = _limit_params(pricing_params, remaining_work=rw,
                                                        remaining_time=rt)
            pres = pricer(master, snapshot, params=pparams, entry_tolerance=entry_tolerance)
            pricing_calls += 1
            record.update(
                pricing_outcome=pres.outcome, pricing_termination=pres.termination,
                pricing_status=pres.status_name, candidate_column=pres.column,
                candidate_reduced_cost=pres.reduced_cost,
                pricing_solver_bound=pres.solver_bound,
                pricing_cost=account('pricing', pres.work, pres.runtime, pforward, pbinding),
            )
            iteration += 1
            exceeded = overrun()
            if exceeded:
                # Mesmo com pricing OPTIMAL: não declarar estacionariedade nem
                # inserir coluna obtida além do orçamento (Work ou tempo).
                stop, message = exceeded
                close(stop, message)
                break
            if work_limit is not None and record['pricing_cost'].work is None:
                # Work do último pricing ausente/inválido: não declarar
                # estacionariedade nem inserir a coluna sem custo mensurável.
                stop = WORK_UNMEASURED
                message = ('Work do último pricing ausente ou inválido (não finito ou '
                           'negativo) com orçamento global de Work ativo')
                close(stop, message)
                break
            if pres.certification_status != UNCERTIFIED or pres.proves_no_negative_column:
                stop, message = PRICING_FAILURE, 'pricing violou a política UNCERTIFIED'
                close(stop, message)
                break

            if pres.outcome == NEGATIVE_COLUMN:
                column = pres.column
                try:
                    # Mesmo snapshot: StaleDualError se o pricing usou outro dual.
                    rc = master.reduced_cost(column, snapshot=snapshot)
                except (ValueError, RuntimeError) as exc:
                    stop, message = PRICING_FAILURE, f'coluna do pricing rejeitada: {exc}'
                    close(stop, message)
                    break
                if (pres.reduced_cost is None or not math.isfinite(pres.reduced_cost)
                        or not math.isfinite(rc)
                        or abs(rc - pres.reduced_cost) > rc_agreement_tolerance):
                    stop = PRICING_FAILURE
                    message = f'rc inconsistente: master {rc!r}, pricing {pres.reduced_cost!r}'
                    close(stop, message)
                    break
                if column in master.columns:
                    # Colunas do RMP têm rc >= -check_tolerance no dual verificado;
                    # duplicata "negativa" indica inconsistência numérica. Reinserir
                    # é proibido (DuplicateColumnError) e repetir não progride.
                    stop = DUPLICATE_COLUMN
                    message = f'coluna rotulada negativa já presente no RMP (rc {rc!r})'
                    close(stop, message)
                    break
                if rc >= -entry_tolerance:
                    stop, message = PRICING_FAILURE, f'coluna rotulada negativa com rc {rc!r}'
                    close(stop, message)
                    break
                try:
                    master.add_column(column)
                except ValueError as exc:
                    stop, message = PRICING_FAILURE, f'add_column rejeitou a coluna: {exc}'
                    close(stop, message)
                    break
                columns_added += 1
                objective_current = False
                record['column_added'] = column
                record['columns_after'] = len(master.columns)
                close(CONTINUE, None if pres.termination == NUMERICALLY_OPTIMAL
                      else f'coluna de pricing interrompido ({pres.status_name})')
                continue

            if pres.outcome == NONNEGATIVE_INCUMBENT and pres.termination == NUMERICALLY_OPTIMAL:
                stop = NUMERICAL_STATIONARY
                message = (f'pricing OPTIMAL numérico sem coluna < -{entry_tolerance!r}; '
                           'sem prova global (UNCERTIFIED)')
            elif pres.outcome in (NONNEGATIVE_INCUMBENT, NO_INCUMBENT) \
                    and pres.termination != NUMERICALLY_OPTIMAL \
                    and pres.termination != SOLVER_FAILURE:
                stop = interrupted_by_global(pres.status_name, pbinding) or PRICING_INCOMPLETE
                message = f'pricing interrompido ({pres.status_name}) sem coluna negativa'
            else:
                stop = PRICING_FAILURE
                message = f'pricing: {pres.outcome}/{pres.termination}: {pres.error}'
            close(stop, message)
    finally:
        if master is not None:
            columns, k_digest, n_K = master.columns, master.k_hash, len(master.K)
            master.dispose()
    return ColumnGenerationResult(
        stop_reason=stop, message=message, rmp_objective=last_objective,
        objective_reflects_all_columns=objective_current, iterations=len(history),
        pricing_calls=pricing_calls, columns_added=columns_added,
        degenerate_steps=degenerate, columns=columns, history=tuple(history),
        k_hash=k_digest, n_K=n_K, settings=settings,
        total_work=None if state['unmeasured'] else state['work'],
        measured_work=state['work'], unmeasured_work_calls=state['unmeasured'],
        total_solver_runtime=state['runtime'], wall_time=elapsed(),
        gurobi_version=tuple(gp.gurobi.version()),
        convergence_status=NUMERIC_UNCERTIFIED if stop == NUMERICAL_STATIONARY else NOT_CONVERGED,
    )
