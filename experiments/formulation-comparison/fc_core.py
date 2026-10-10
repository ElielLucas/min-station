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
import sys
import time
from dataclasses import dataclass, replace
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
for p in (ROOT, ROOT / 'experiments' / 'cuts', ROOT / 'experiments' / 'alternative-formulations'):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import gurobipy as gp  # noqa: E402
from gurobipy import GRB  # noqa: E402

from baseline import construir_modelo_baseline  # noqa: E402
from harness import measure_lp  # noqa: E402
from fcc import CapExceeded  # noqa: E402
from fcc_k import build_fcc_plus_k, lp_fcc_plus_k, prepare_k  # noqa: E402

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


def _make_callback(tracker):
    def callback(model, where):
        try:
            if where == GRB.Callback.MIP:
                t = model.cbGet(GRB.Callback.RUNTIME)
                lb = model.cbGet(GRB.Callback.MIP_OBJBND)
                ub = model.cbGet(GRB.Callback.MIP_OBJBST)
                nodes = int(model.cbGet(GRB.Callback.MIP_NODCNT))
                work = model.cbGet(GRB.Callback.WORK)
                tracker.on_periodic(t, lb, ub if model.cbGet(GRB.Callback.MIP_SOLCNT) > 0 else None,
                                    nodes, work)
            elif where == GRB.Callback.MIPSOL:
                t = model.cbGet(GRB.Callback.RUNTIME)
                ub = model.cbGet(GRB.Callback.MIPSOL_OBJ)
                tracker.on_incumbent(t, ub)
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
    ru_maxrss_kb_before: int
    ru_maxrss_kb_after: int
    installed: tuple
    physically_validated: bool | None
    evolution: tuple
    reason: str = ''


def _k_for(instance):
    K, k_hash, _counts = prepare_k(instance.S, instance.T, instance.V, instance.adj,
                                   instance.A_r, instance.r)
    return K, k_hash


def run_modality_a(instance, cfg):
    """LP base (sem cortes), LP COMP (base+K) e LP F-CC+K completo.

    Os três são LPs *exatos* resolvidos até `GRB.OPTIMAL` (ou marcados
    `NOT_MEASURED_*`; nunca um `ObjVal` parcial é relatado como valor final).
    """
    results = {}
    t0 = time.monotonic()
    K, k_hash = _k_for(instance)
    # n_vars/n_cons do baseline (U): f sobre A_r + y por vértice; balanço e as
    # duas ativações por vértice (mesma contagem de baseline.executar_para_R);
    # cada corte unitário de K soma uma linha adicional em lp_comp.
    n_vars_base = len(instance.A_r) + len(instance.V)
    n_cons_base = 3 * len(instance.V)
    for name, cuts in (('lp_base', []), ('lp_comp', K)):
        t1 = time.monotonic()
        res = measure_lp(instance.S, instance.T, instance.V, instance.A_r, 'cont', cuts,
                         seed=cfg.seed, threads=cfg.threads, time_limit=cfg.lp_time_limit_s)
        dt = time.monotonic() - t1
        status_ok = res['lp_status'] == GRB.OPTIMAL
        results[name] = LPResult(
            formulation=name, value=res['lp_bound'] if status_ok else None,
            status='OPTIMAL' if status_ok else f'STATUS_{res["lp_status"]}',
            certification=CERTIFIED_LP if status_ok else NOT_MEASURED_SOLVER_ERROR,
            time_s=dt, n_K=len(cuts), n_vars=n_vars_base, n_cons=n_cons_base + len(cuts),
        )
    t1 = time.monotonic()
    try:
        z, meta = lp_fcc_plus_k(instance.S, instance.T, instance.V, instance.adj,
                                           instance.A_r, instance.r, K=K, k_hash=k_hash,
                                           max_W=cfg.max_w, seed=cfg.seed, threads=cfg.threads)
        results['lp_fcc_k'] = LPResult(
            formulation='lp_fcc_k', value=z, status='OPTIMAL', certification=CERTIFIED_LP,
            time_s=time.monotonic() - t1, n_K=len(K),
            n_vars=meta.get('n_vars'), n_cons=meta.get('n_cons'),
        )
    except CapExceeded as exc:
        results['lp_fcc_k'] = LPResult(
            formulation='lp_fcc_k', value=None, status='CAP_EXCEEDED',
            certification=NOT_MEASURED_CAP_EXCEEDED, time_s=time.monotonic() - t1,
            n_K=len(K), reason=str(exc),
        )
    results['_wall_time_s'] = time.monotonic() - t0
    results['_k_hash'] = k_hash
    return results


def _validate(instance, installed):
    if viavel is None:
        return None
    return bool(viavel(instance.S, instance.T, instance.V, instance.adj, instance.r,
                       sorted(installed)))


def _solve_mip_with_evolution(model, cfg, formulation, y_vars, n_vars, n_cons):
    tracker = EvolutionTracker(cfg.checkpoints_s)
    model.Params.OutputFlag = 0
    model.Params.Seed = cfg.seed
    model.Params.Threads = cfg.threads
    model.Params.TimeLimit = cfg.time_limit_s
    mem_before = _ru_maxrss_kb()
    t0 = time.monotonic()
    try:
        model.optimize(_make_callback(tracker))
    except gp.GurobiError as exc:
        return MIPResult(
            formulation=formulation, status_name='SOLVER_ERROR', objective_ub=None,
            objective_lb=None, certification=NOT_MEASURED_SOLVER_ERROR, gap=None,
            time_s=time.monotonic() - t0, work=0.0, time_to_first_feasible_s=None,
            time_to_best_s=None, time_to_proof_s=None, nodes=0, n_vars=n_vars, n_cons=n_cons,
            ru_maxrss_kb_before=mem_before, ru_maxrss_kb_after=_ru_maxrss_kb(),
            installed=(), physically_validated=None, evolution=(), reason=str(exc),
        )
    runtime = float(model.Runtime)
    mem_after = _ru_maxrss_kb()
    status = int(model.Status)
    sol_count = int(model.SolCount)
    status_name = {GRB.OPTIMAL: 'OPTIMAL', GRB.TIME_LIMIT: 'TIME_LIMIT',
                  GRB.INFEASIBLE: 'INFEASIBLE'}.get(status, f'STATUS_{status}')
    lb = float(model.ObjBound) if hasattr(model, 'ObjBound') else None
    ub = float(model.ObjVal) if sol_count > 0 else None
    gap_abs = (ub - lb) if (ub is not None and lb is not None) else None
    # Relativo só quando o denominador faz sentido (ub>0); caso contrário fica
    # None (nunca uma divisão por zero/quase-zero travestida de percentual).
    gap_rel = (gap_abs / ub) if (gap_abs is not None and ub and ub > 1e-9) else None
    if status == GRB.OPTIMAL:
        certification = CERTIFIED_MIP_OPTIMAL
    elif sol_count > 0:
        certification = CERTIFIED_MIP_BOUND  # LB nativo de B&B sobre o modelo completo
    else:
        certification = UNCERTIFIED_NO_INCUMBENT
    installed = tuple(sorted(v for v, var in y_vars.items() if var.X > 0.5)) if sol_count > 0 else ()
    tracker.final(runtime, lb, ub, int(getattr(model, 'NodeCount', 0)), float(model.Work))
    return MIPResult(
        formulation=formulation, status_name=status_name, objective_ub=ub, objective_lb=lb,
        certification=certification, gap_abs=gap_abs, gap_rel=gap_rel,
        time_s=runtime, work=float(model.Work),
        time_to_first_feasible_s=tracker.first_feasible_time, time_to_best_s=tracker.best_time,
        time_to_proof_s=runtime if status == GRB.OPTIMAL else None,
        nodes=int(getattr(model, 'NodeCount', 0)), n_vars=n_vars, n_cons=n_cons,
        ru_maxrss_kb_before=mem_before, ru_maxrss_kb_after=mem_after,
        installed=installed, physically_validated=None,
        evolution=tuple(tracker.points), reason='',
    )


def run_modality_b_baseline(instance, cfg):
    """Formulação base (Das, variante U) como MIP completo, até `GRB.OPTIMAL`
    ou `cfg.time_limit_s`."""
    model, y, f, n_arcos, n_vert = construir_modelo_baseline(instance.S, instance.T, instance.V,
                                                             instance.A_r)
    n_vars = len(f) + n_vert
    n_cons = 3 * n_vert
    try:
        result = _solve_mip_with_evolution(model, cfg, 'baseline', y, n_vars, n_cons)
    finally:
        model.dispose()
    if result.objective_ub is not None:
        validado = _validate(instance, set(result.installed))
        result = replace(result, physically_validated=validado)
    return result


def run_modality_b_fcc_k(instance, cfg):
    """F-CC+K como MIP completo (enumeração total de `(W,I,J)`), sem geração
    de colunas. `CapExceeded` (fora do alcance da enumeração) é reportado
    explicitamente, nunca aproximado."""
    K, k_hash = _k_for(instance)
    try:
        model, y, _extra, meta = build_fcc_plus_k(
            instance.S, instance.T, instance.V, instance.adj, instance.A_r, instance.r,
            K=K, k_hash=k_hash, max_W=cfg.max_w, integer_y=True,
        )
    except CapExceeded as exc:
        return MIPResult(
            formulation='fcc_k', status_name='CAP_EXCEEDED', objective_ub=None,
            objective_lb=None, certification=NOT_MEASURED_CAP_EXCEEDED, gap_abs=None, gap_rel=None,
            time_s=0.0, work=0.0, time_to_first_feasible_s=None, time_to_best_s=None,
            time_to_proof_s=None, nodes=0, n_vars=0, n_cons=0,
            ru_maxrss_kb_before=_ru_maxrss_kb(), ru_maxrss_kb_after=_ru_maxrss_kb(),
            installed=(), physically_validated=None, evolution=(), reason=str(exc),
        )
    try:
        result = _solve_mip_with_evolution(model, cfg, 'fcc_k', y, meta['n_vars'], meta['n_cons'])
    finally:
        model.dispose()
    if result.objective_ub is not None:
        validado = _validate(instance, set(result.installed))
        result = replace(result, physically_validated=validado)
    return result
