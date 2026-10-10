"""Comparação base × F-CC+K: execução das Modalidades A, B e C.

Reutiliza integralmente as formulações já validadas do repositório:

- Formulação base (Das, variante U): `baseline.construir_modelo_baseline`
  (y binário, fluxo `f` sobre o dígrafo de alcance `A_r`), e
  `experiments.cuts.harness.measure_lp`/`_make_mip` para a relaxação LP
  com cortes a priori (`lp_base` sem cortes, `lp_comp` com K = C1+C2+C4-DM).
- F-CC+K: `experiments.alternative_formulations.fcc_k.build_fcc_plus_k` e
  `lp_fcc_plus_k` (configurações conectadas `(W,I,J)` por enumeração
  completa — não é o master restrito/geração de colunas da N2, que a N2-T6
  encerrou com `N2 FAIL` por falta de certificação; aqui usamos o LP/IP
  *completo*, já validado em N1 por P1/P7 e por 878 instalações sem
  divergência contra `independent_validator.viavel`).

Nenhuma formulação é reimplementada ou alterada. Nenhum resultado desta
comparação altera N1/N2.
"""
from __future__ import annotations

import resource
import math
import sys
import time
from dataclasses import dataclass, replace
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
# As dependências legadas precisam estar acessíveis, mas não podem sombrear
# módulos fc_* desta comparação. Em particular, versões antigas de
# fc_reporting/fc_instances podem existir em alternative-formulations.
for p in (ROOT, ROOT / 'experiments' / 'cuts', ROOT / 'experiments' / 'alternative-formulations'):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
# Reposiciona HERE mesmo quando já consta em sys.path: somente checar
# "if not in sys.path" não garante precedência depois dos inserts acima.
if str(HERE) in sys.path:
    sys.path.remove(str(HERE))
sys.path.insert(0, str(HERE))

import gurobipy as gp  # noqa: E402
from gurobipy import GRB  # noqa: E402

from baseline import construir_modelo_baseline  # noqa: E402
from harness import _make_mip  # noqa: E402
from fcc_k import build_fcc_plus_k, prepare_k  # noqa: E402
from fc_budget import BoundedOutcome, run_bounded  # noqa: E402

try:
    from independent_validator import viavel
except ImportError:  # pragma: no cover - deps do ambiente, não do código
    viavel = None

NOT_MEASURED_CAP_EXCEEDED = 'NOT_MEASURED_CAP_EXCEEDED'
NOT_MEASURED_SOLVER_ERROR = 'NOT_MEASURED_SOLVER_ERROR'
CERTIFIED_LP = 'CERTIFIED_LP'  # LP exato (não restrito), relaxação dual-factível válida
CERTIFIED_MIP_OPTIMAL = 'CERTIFIED_MIP_OPTIMAL'
CERTIFIED_MIP_BOUND = 'CERTIFIED_MIP_BOUND'  # ObjBound de B&B nativo sobre o modelo COMPLETO
# ^ Distinção deliberada do caso N2: aqui o MIP já contém TODAS as colunas
# (enumeração completa), então o ObjBound de um branch-and-bound nativo do
# Gurobi é o bound dual-padrão de uma árvore de B&B sobre uma formulação
# fechada — não o ObjBound de um MIP auxiliar de pricing sobre um master
# restrito exponencial (essa é a situação específica que a revisão v2.1 da
# N2-T2B trata como não certificável). As duas situações não são a mesma.
UNCERTIFIED_NO_INCUMBENT = 'UNCERTIFIED_NO_INCUMBENT'


def _ru_maxrss_kb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss  # KB no Linux


@dataclass(frozen=True)
class EvolutionPoint:
    mark_s: float
    observed_time_s: float
    lb: float | None
    ub: float | None
    nodes: int
    work: float | None


class EvolutionTracker:
    """Decide quais marcos de checkpoint já foram cruzados, sem interpolar.

    `on_periodic` é alimentado por amostragem periódica do solver (LB/UB
    correntes); `on_incumbent` é alimentado só quando uma nova solução
    incumbente aparece, para registrar `first_feasible_time`/`best_time`
    com o instante exato do evento, não o próximo ponto de amostragem.
    Testável sem Gurobi: os métodos recebem valores já extraídos.
    """

    def __init__(self, marks_s):
        self._marks = tuple(sorted(marks_s))
        self._next = 0
        self.points: list[EvolutionPoint] = []
        self.first_feasible_time: float | None = None
        self.best_time: float | None = None
        self._best_ub = None

    def on_periodic(self, t, lb, ub, nodes, work):
        while self._next < len(self._marks) and t >= self._marks[self._next]:
            self.points.append(EvolutionPoint(self._marks[self._next], t, lb, ub, nodes, work))
            self._next += 1

    def on_incumbent(self, t, ub):
        if self.first_feasible_time is None:
            self.first_feasible_time = t
        if self._best_ub is None or ub < self._best_ub - 1e-9:
            self._best_ub = ub
            self.best_time = t

    def final(self, t, lb, ub, nodes, work):
        """Registra o estado final, mesmo que nenhum marco tenha sido cruzado."""
        self.points.append(EvolutionPoint(float('inf'), t, lb, ub, nodes, work))


def _make_callback(tracker, offset_s=0.0):
    def callback(model, where):
        try:
            if where == GRB.Callback.MIP:
                t = model.cbGet(GRB.Callback.RUNTIME)
                lb = model.cbGet(GRB.Callback.MIP_OBJBND)
                ub = model.cbGet(GRB.Callback.MIP_OBJBST)
                nodes = int(model.cbGet(GRB.Callback.MIP_NODCNT))
                work = model.cbGet(GRB.Callback.WORK)
                tracker.on_periodic(t + offset_s, lb, ub if model.cbGet(GRB.Callback.MIP_SOLCNT) > 0 else None,
                                    nodes, work)
            elif where == GRB.Callback.MIPSOL:
                t = model.cbGet(GRB.Callback.RUNTIME)
                ub = model.cbGet(GRB.Callback.MIPSOL_OBJ)
                tracker.on_incumbent(t + offset_s, ub)
        except gp.GurobiError:  # pragma: no cover - callback não deve derrubar o solve
            pass
    return callback


@dataclass(frozen=True)
class LPResult:
    formulation: str
    value: float | None
    status: str
    certification: str
    time_s: float
    n_K: int | None = None
    n_vars: int | None = None
    n_cons: int | None = None
    reason: str = ''
    solver_runtime_s: float | None = None
    work: float | None = None
    phase_wall_s: tuple = ()
    stop_reason: str = ''


@dataclass(frozen=True)
class MIPResult:
    formulation: str
    status_name: str
    objective_ub: float | None
    objective_lb: float | None
    certification: str
    gap_abs: float | None
    gap_rel: float | None
    time_s: float
    work: float
    time_to_first_feasible_s: float | None
    time_to_best_s: float | None
    time_to_proof_s: float | None
    nodes: int
    n_vars: int
    n_cons: int
    ru_maxrss_kb_before: int | None
    ru_maxrss_kb_after: int | None
    installed: tuple
    physically_validated: bool | None
    evolution: tuple
    reason: str = ''
    solver_runtime_s: float | None = None
    phase_wall_s: tuple = ()
    stop_reason: str = ''


def _k_for(instance):
    K, k_hash, _counts = prepare_k(instance.S, instance.T, instance.V, instance.adj,
                                   instance.A_r, instance.r)
    return K, k_hash


def _solver_time_limit(ctx):
    """Reserva parte da janela para serialização, validação e descarte.

    O limite continua global: a reserva é SUBTRAÍDA do tempo restante,
    nunca adicionada ao prazo absoluto. Se não há resto, não inicia solve.
    """
    remaining = ctx.require_remaining()
    reserve = min(2.0, remaining * 0.02)
    return max(1e-6, remaining - reserve)


def _lp_job(ctx, instance, cfg, formulation):
    """Resolve LP *completo* dentro de um único deadline por formulação.

    Usa os mesmos construtores `harness._make_mip` e `fcc_k.build_fcc_plus_k`
    anteriormente empregados por `measure_lp` e `lp_fcc_plus_k`.
    Separar montagem/otimização é necessário para passar `remaining()`
    **depois** da montagem e coletar Runtime/Work do solver.
    """
    model = None
    lp = None
    k_hash = None
    try:
        ctx.phase('k_preparation')
        if formulation == 'lp_base':
            cuts = []
        else:
            cuts, k_hash = _k_for(instance)
        ctx.phase('model_build')
        if formulation == 'lp_fcc_k':
            model, _y, _extra, meta = build_fcc_plus_k(
                instance.S, instance.T, instance.V, instance.adj, instance.A_r, instance.r,
                K=cuts, k_hash=k_hash, max_W=cfg.max_w,
            )
            lp = model
            n_vars = meta['n_vars']
            n_cons = meta['n_cons']
        else:
            model, _y, _f, _n_added = _make_mip(
                instance.S, instance.T, instance.V, instance.A_r, 'cont', cuts,
            )
            lp = model.relax()
            n_vars = lp.NumVars
            n_cons = lp.NumConstrs

        lp.Params.OutputFlag = 0
        lp.Params.Seed = cfg.seed
        lp.Params.Threads = cfg.threads
        if formulation == 'lp_fcc_k':
            lp.Params.Method = 2
        ctx.phase('solve')
        lp.Params.TimeLimit = _solver_time_limit(ctx)
        lp.optimize()
        runtime = float(lp.Runtime)
        work = float(lp.Work)
        optimal = lp.Status == GRB.OPTIMAL
        result = LPResult(
            formulation=formulation, value=float(lp.ObjVal) if optimal else None,
            status='OPTIMAL' if optimal else ('TIME_LIMIT' if lp.Status == GRB.TIME_LIMIT
                                             else f'STATUS_{lp.Status}'),
            certification=CERTIFIED_LP if optimal else NOT_MEASURED_SOLVER_ERROR,
            time_s=ctx.elapsed(), n_K=len(cuts), n_vars=n_vars, n_cons=n_cons,
            solver_runtime_s=runtime, work=work,
            stop_reason='OPTIMAL' if optimal else ('TIME_LIMIT_SOLVER' if lp.Status == GRB.TIME_LIMIT
                                                   else f'Gurobi status {lp.Status}'),
        )
        return result, k_hash
    finally:
        if lp is not None and lp is not model:
            lp.dispose()
        if model is not None:
            model.dispose()


def _lp_failed(formulation, outcome: BoundedOutcome):
    status = 'CAP_EXCEEDED' if outcome.status == 'CAP_EXCEEDED' else outcome.status
    return LPResult(
        formulation=formulation, value=None, status=status,
        certification=(NOT_MEASURED_CAP_EXCEEDED if status == 'CAP_EXCEEDED'
                       else NOT_MEASURED_SOLVER_ERROR),
        time_s=outcome.wall_total_s, reason=outcome.reason,
        phase_wall_s=outcome.phase_wall_s, stop_reason=status,
    )


def run_modality_a(instance, cfg):
    """Executa LP base, COMP, F-CC+K: **cada braço** tem prazo global próprio."""
    results = {}
    t0 = time.monotonic()
    hashes = set()
    for formulation in ('lp_base', 'lp_comp', 'lp_fcc_k'):
        outcome = run_bounded(_lp_job, instance, cfg, formulation,
                              budget_s=cfg.lp_time_limit_s)
        if outcome.status == 'COMPLETED':
            value, k_hash = outcome.value
            results[formulation] = replace(
                value, time_s=outcome.wall_total_s,
                phase_wall_s=outcome.phase_wall_s,
            )
            if k_hash is not None:
                hashes.add(k_hash)
        else:
            results[formulation] = _lp_failed(formulation, outcome)
    results['_wall_time_s'] = time.monotonic() - t0
    # FC-04 deverá validar integralmente os hashes de K/instâncias.
    results['_k_hash'] = next(iter(hashes)) if len(hashes) == 1 else None
    if len(hashes) > 1:
        raise ValueError('Hashes K divergentes entre os braços LP')
    return results


def _validate(instance, installed):
    if viavel is None:
        return None
    return bool(viavel(instance.S, instance.T, instance.V, instance.adj, instance.r,
                       sorted(installed)))


def _solve_mip_with_evolution(model, cfg, formulation, y_vars, n_vars, n_cons, ctx):
    """MIP completo, com TimeLimit = *tempo restante*, não o orçamento original."""
    tracker = EvolutionTracker(cfg.checkpoints_s)
    model.Params.OutputFlag = 0
    model.Params.Seed = cfg.seed
    model.Params.Threads = cfg.threads
    mem_before = _ru_maxrss_kb()
    ctx.phase('solve')
    model.Params.TimeLimit = _solver_time_limit(ctx)
    offset = ctx.elapsed()
    model.optimize(_make_callback(tracker, offset))
    runtime = float(model.Runtime)
    mem_after = _ru_maxrss_kb()
    status = int(model.Status)
    sol_count = int(model.SolCount)
    status_name = {GRB.OPTIMAL: 'OPTIMAL', GRB.TIME_LIMIT: 'TIME_LIMIT',
                   GRB.INFEASIBLE: 'INFEASIBLE'}.get(status, f'STATUS_{status}')
    try:
        lb = float(model.ObjBound)
    except (AttributeError, gp.GurobiError):
        lb = None
    if lb is not None and not math.isfinite(lb):
        lb = None
    ub = float(model.ObjVal) if sol_count > 0 else None
    gap_abs = (ub - lb) if ub is not None and lb is not None else None
    gap_rel = (gap_abs / ub) if gap_abs is not None and ub and ub > 1e-9 else None
    if status == GRB.OPTIMAL:
        certification = CERTIFIED_MIP_OPTIMAL
    elif sol_count > 0:
        certification = CERTIFIED_MIP_BOUND
    else:
        certification = UNCERTIFIED_NO_INCUMBENT
    installed = tuple(sorted(v for v, var in y_vars.items() if var.X > 0.5)) if sol_count else ()
    work = float(model.Work)
    tracker.final(ctx.elapsed(), lb, ub, int(getattr(model, 'NodeCount', 0)), work)
    return MIPResult(
        formulation=formulation, status_name=status_name, objective_ub=ub, objective_lb=lb,
        certification=certification, gap_abs=gap_abs, gap_rel=gap_rel,
        time_s=ctx.elapsed(), work=work,
        time_to_first_feasible_s=tracker.first_feasible_time,
        time_to_best_s=tracker.best_time,
        time_to_proof_s=ctx.elapsed() if status == GRB.OPTIMAL else None,
        nodes=int(getattr(model, 'NodeCount', 0)), n_vars=n_vars, n_cons=n_cons,
        ru_maxrss_kb_before=mem_before, ru_maxrss_kb_after=mem_after,
        installed=installed, physically_validated=None,
        evolution=tuple(tracker.points), reason='', solver_runtime_s=runtime,
        stop_reason='OPTIMAL' if status == GRB.OPTIMAL else status_name,
    )


def _mip_job(ctx, instance, cfg, formulation):
    model = None
    try:
        ctx.phase('k_preparation')
        if formulation == 'fcc_k':
            K, k_hash = _k_for(instance)
        else:
            K = k_hash = None
        ctx.phase('model_build')
        if formulation == 'fcc_k':
            model, y, _extra, meta = build_fcc_plus_k(
                instance.S, instance.T, instance.V, instance.adj, instance.A_r, instance.r,
                K=K, k_hash=k_hash, max_W=cfg.max_w, integer_y=True,
            )
            n_vars, n_cons = meta['n_vars'], meta['n_cons']
        else:
            model, y, f, _n_arcos, n_vert = construir_modelo_baseline(
                instance.S, instance.T, instance.V, instance.A_r,
            )
            n_vars, n_cons = len(f) + n_vert, 3 * n_vert
        result = _solve_mip_with_evolution(model, cfg, formulation, y, n_vars, n_cons, ctx)
        if result.objective_ub is not None:
            ctx.phase('validation')
            validado = _validate(instance, set(result.installed))
            result = replace(result, physically_validated=validado)
        return replace(result, ru_maxrss_kb_after=_ru_maxrss_kb())
    finally:
        if model is not None:
            model.dispose()


def _failed_mip(formulation, outcome: BoundedOutcome):
    status = 'CAP_EXCEEDED' if outcome.status == 'CAP_EXCEEDED' else outcome.status
    return MIPResult(
        formulation=formulation, status_name=status,
        objective_ub=None, objective_lb=None,
        certification=(NOT_MEASURED_CAP_EXCEEDED if status == 'CAP_EXCEEDED'
                       else NOT_MEASURED_SOLVER_ERROR),
        gap_abs=None, gap_rel=None, time_s=outcome.wall_total_s, work=0.0,
        time_to_first_feasible_s=None, time_to_best_s=None, time_to_proof_s=None,
        nodes=0, n_vars=0, n_cons=0,
        ru_maxrss_kb_before=None, ru_maxrss_kb_after=None,
        installed=(), physically_validated=None, evolution=(),
        reason=outcome.reason, phase_wall_s=outcome.phase_wall_s,
        stop_reason=status,
    )


def _run_mip_bounded(instance, cfg, formulation):
    outcome = run_bounded(_mip_job, instance, cfg, formulation,
                          budget_s=cfg.time_limit_s)
    if outcome.status != 'COMPLETED':
        return _failed_mip(formulation, outcome)
    return replace(outcome.value, time_s=outcome.wall_total_s,
                   phase_wall_s=outcome.phase_wall_s)


def run_modality_b_baseline(instance, cfg):
    """MIP base: montagem, optimize e validação incluídos no teto total."""
    return _run_mip_bounded(instance, cfg, 'baseline')


def run_modality_b_fcc_k(instance, cfg):
    """MIP F-CC+K completo: K e enumeração **dentro** do mesmo teto."""
    return _run_mip_bounded(instance, cfg, 'fcc_k')
