#!/usr/bin/env python3
"""N2-T5 — medição prospectiva F-CC+K raiz, conforme freeze N2-T1.

    PYTHONHASHSEED=0 python experiments/alternative-formulations/run_n2_t5.py check
    PYTHONHASHSEED=0 python experiments/alternative-formulations/run_n2_t5.py run

Quatro instâncias congeladas, duas famílias, dois níveis. WorkLimit 164 POR
INSTÂNCIA, compartilhado por COMP/core/master/pricing. Wall guard 1800s.
Não modifica nenhum arquivo da N1/N2-T1--T4, nem antecipa N2 PASS/FAIL.
Não usa objetivo RMP/ObjBoundC como LB. Ausência de dado != valor zero.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import os
import resource
import subprocess
import sys
import time
from xml.sax.saxutils import escape as xml_escape
from dataclasses import dataclass, field
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
RESULTS = ROOT / 'results' / 'alternative-formulations'
FREEZE = HERE / 'n2-t1-freeze.json'
T4_REPORT = RESULTS / 'n2-t4-replay-corrigido' / 'n2-t4-regressao.csv'
T4_MANIFEST = RESULTS / 'n2-t4-replay-corrigido' / 'n2-t4-regressao-manifest.json'
T4_GATE = ROOT / 'docs' / 'technical' / 'plans' / 'execucao' / 'n2-t4-gate-aceite-regressao.md'
DEFAULT_OUTPUT = RESULTS / 'n2-t5-prospectivo'
CERTIFIED = 'CERTIFIED'
UNCERTIFIED = 'UNCERTIFIED'
EPS = Fraction(1, 1_000_000)
EXPECTED_NAMES = ('HB-q4-ndir2-p1', 'BP-nao-[3,1]-q2',
                  'HB-q6-ndir2-p1', 'BP-nao-[2,2,2]-q2')
FIELDS = (
    'name', 'family', 'level', 'n', 'm', 'r', 'instance_sha256', 'k_sha256', 'n_K',
    'freeze_sha256', 'path', 'seed', 'threads', 'work_cap', 'wall_cap_s',
    'b0_reference', 'b0_reference_status', 'b0_comp_lp', 'b0_core_ip',
    'b0_certificate_status', 'b0_certified_exact', 'full_lp_historical',
    'lp_status', 'lp_lb_exact', 'lb_continuous_exact', 'lp_source',
    'physical_status', 'physical_lb_exact', 'physical_integer_lb',
    'upper_exact', 'g2_status', 'gain_over_b0_reference',
    'recovery_fraction_level1', 'rmp_obj_numeric_diagnostic', 'stop_reason',
    'pricing_calls', 'columns_added', 'n_columns_final', 'iterations',
    'n_cuts', 'pricing_gap_last_numeric', 'pricing_gap_max_numeric',
    'work_comp_lp', 'work_core_ip', 'work_master', 'work_pricing',
    'work_total', 'work_unmeasured_calls', 'wall_assembly_s', 'wall_reach_s',
    'wall_k_s', 'wall_comp_lp_s', 'wall_core_ip_s', 'wall_cg_s',
    'wall_master_solver_s', 'wall_pricing_solver_s', 'wall_cg_overhead_s',
    'wall_validation_s', 'wall_postcheck_s', 'wall_other_s', 'wall_total_s',
    'peak_rss_mb', 'n_curve_points', 'audit_warnings', 'status', 'justification',
)
CURVE_FIELDS = ('name', 'family', 'level', 'iteration', 'cumulative_work',
                'cumulative_wall_s', 'lb_status', 'lb_exact', 'lb_source',
                'reference_b0', 'reference_full_lp', 'numeric_rmp_objective',
                'n_columns', 'pricing_calls', 'note')


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read(path: Path):
    return json.loads(path.read_text(encoding='utf8'))


def _ratio(value):
    if value is None:
        return ''
    if not isinstance(value, Fraction):
        raise TypeError('não converter valor numérico em prova sem Fraction')
    return f'{value.numerator}/{value.denominator}'


def _reference(value):
    if value is None:
        return None
    x = Decimal(str(value))
    if not x.is_finite() or x < 0:
        raise ValueError('referência histórica não finita ou negativa')
    return Fraction(x)


def _safe_json(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       indent=2, allow_nan=False) + '\n').encode('utf8')


def _csv_bytes(rows, columns):
    f = io.StringIO(newline='')
    w = csv.DictWriter(f, fieldnames=columns, extrasaction='ignore', lineterminator='\n')
    w.writeheader()
    for row in rows:
        w.writerow({key: row.get(key, '') for key in columns})
    return f.getvalue().encode('utf8')


def _finite_work(work):
    return (type(work) in (int, float) and math.isfinite(work) and work >= 0)


def _max_rss_mb():
    # Linux ru_maxrss = KiB. Pico de processo, inclui importações prévias.
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def check_t4_gate():
    """Reaudita os arquivos de replay reais, sem executar solver nem editar gate."""
    text = T4_GATE.read_text(encoding='utf8')
    if ('APROVADO_COM_EXCECAO_DE_DOMINIO_DIRECT0' not in text or
            'ACEITA_COM_EXCECAO_FORMAL' not in text or 'LIBERAR N2-T5' not in text):
        raise ValueError('decisão humana N2-T4 não confirmada')
    manifest = _read(T4_MANIFEST)
    if manifest.get('status') != 'SCOPE_EXCEPTION_REVIEW_BLOCK_N2_T5':
        raise ValueError('manifesto N2-T4 adulterado: manter status original')
    required = {'expected_eligible': 23, 'eligible_checked': 23, 'passed': 23,
                'cg_evaluated': 22, 'failures': [],
                'exact_domain_exceptions': ['T5:Direct0'],
                'excluded': ['T5:SC-GF2-k3'], 'task': 'N2-T4'}
    for key, expected in required.items():
        if manifest.get(key) != expected:
            raise ValueError(f'N2-T4: {key} não coincide com gate aprovado')
    if _sha(T4_REPORT) != manifest.get('csv_sha256'):
        raise ValueError('N2-T4: hash do CSV não coincide com manifesto')
    if manifest.get('n2_t1_sha256') != _sha(FREEZE):
        raise ValueError('N2-T4 foi feito com outro pré-registro N2-T1')
    for rel, digest in manifest.get('n1_sources_sha256', {}).items():
        if _sha(ROOT / rel) != digest:
            raise ValueError(f'N2-T4: origem N1 alterada: {rel}')
    with T4_REPORT.open(encoding='utf8', newline='') as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 24 or len({x['id'] for x in rows}) != 24:
        raise ValueError('N2-T4: número de controles divergente')
    counts = {'cg': 0, 'direct': 0, 'excluded': 0}
    for row in rows:
        status = row['comparison']
        if row['id'] == 'T5:Direct0':
            if status != 'PASS_DIRECT_ZERO_EXACT_OUTSIDE_CONNECTED_DOMAIN' or row['lp_lb_exact'] != '0/1':
                raise ValueError('N2-T4: exceção Direct0 não corresponde à prova aceita')
            counts['direct'] += 1
        elif row['id'] == 'T5:SC-GF2-k3':
            if status != 'EXCLUDED_NO_FULL_LP_REFERENCE':
                raise ValueError('N2-T4: exclusão histórica divergente')
            counts['excluded'] += 1
        else:
            if not status.startswith('PASS_') or row['lp_certification_status'] != CERTIFIED:
                raise ValueError(f'N2-T4: controle {row["id"]} não aprovado/certificado')
            counts['cg'] += 1
    if counts != {'cg': 22, 'direct': 1, 'excluded': 1}:
        raise ValueError('N2-T4: composição de controles divergente')
    return {'csv_sha256': _sha(T4_REPORT), 'manifest_sha256': _sha(T4_MANIFEST),
            'gate_sha256': _sha(T4_GATE), 'counts': counts}


def check_freeze(*, full=True):
    if os.environ.get('PYTHONHASHSEED') != '0':
        raise RuntimeError('PYTHONHASHSEED=0 obrigatório')
    freeze = _read(FREEZE)
    if freeze.get('task') != 'N2-T1' or freeze.get('state') != 'FROZEN' or freeze.get('path') != 'B':
        raise ValueError('N2-T1 não congelada para caminho B')
    if freeze.get('representation') != 'F-CC + K' or freeze.get('root_only') is not True:
        raise ValueError('mudança de representação proibida')
    rows = freeze['instances']
    if tuple(x['name'] for x in rows) != EXPECTED_NAMES:
        raise ValueError('identidade/ordem das quatro instâncias mudou')
    if [(x['family'], x['level']) for x in rows] != [
            ('hb', 1), ('bp-nao', 1), ('hb', 2), ('bp-nao', 2)]:
        raise ValueError('famílias/níveis alterados')
    proto = freeze['protocol']
    if (proto['WorkLimit_total'] != 164.0 or proto['wall_guard_seconds'] != 1800
            or proto['threads'] != 4 or proto['seed'] != 42
            or proto['min_recovery_fraction'] != 0.5
            or proto['tolerance'] != 1e-6 or proto['branching'] is not False):
        raise ValueError('protocolo científico congelado foi alterado')
    for case in rows:
        if case['level'] == 1:
            if case['B0_reference'] is None or case['full_lp_reference'] is None:
                raise ValueError('nível 1 requer valores históricos congelados')
        elif case['B0_reference'] is not None or case['full_lp_reference'] is not None:
            raise ValueError('nível 2 não pode receber referências históricas fabricadas')
    if full:
        for rel, digest in freeze['source_hashes'].items():
            if _sha(ROOT / rel) != digest:
                raise ValueError(f'fonte do freeze N2-T1 divergente: {rel}')
        command = [sys.executable, str(HERE / 'run_n2_t1.py'), 'check']
        proc = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
        if proc.returncode or 'PASS' not in proc.stdout.upper():
            raise RuntimeError('Gate N2-T1 não passou: ' + proc.stdout + proc.stderr)
        gate = subprocess.run([sys.executable, str(HERE / 'verify_n1_t7_gate.py')],
                              cwd=ROOT, capture_output=True, text=True, check=False)
        if gate.returncode or 'PROMOTE FCC + EXISTING CUTS' not in gate.stdout:
            raise RuntimeError('Gate N1-T7 divergiu: ' + gate.stdout + gate.stderr)
    return freeze


def check(*, full=True):
    f = check_freeze(full=full)
    proof = check_t4_gate()
    return {'freeze_sha256': _sha(FREEZE), 't4': proof,
            'names': [item['name'] for item in f['instances']],
            'work_cap': 164.0, 'wall_cap_s': 1800, 'threads': 4, 'seed': 42}


@dataclass
class Budget:
    cap: float
    wall_cap: float
    clock: object = time.monotonic
    started: float = field(init=False)
    work_items: dict = field(default_factory=dict)
    unmeasured: int = 0

    def __post_init__(self):
        self.started = self.clock()
        if not _finite_work(self.cap) or not _finite_work(self.wall_cap):
            raise ValueError('orçamentos não finitos')

    def elapsed(self):
        return max(0.0, self.clock() - self.started)

    def remaining(self):
        return max(0.0, self.cap - sum(self.work_items.values()))

    def remaining_wall(self):
        return max(0.0, self.wall_cap - self.elapsed())

    def ensure(self):
        if self.unmeasured:
            raise RuntimeError('Work de algum solve não foi mensurado')
        if self.remaining() <= 0 or self.remaining_wall() <= 0:
            raise TimeoutError('orçamento de Work/wall esgotado')

    def add(self, phase, value):
        if not _finite_work(value):
            self.unmeasured += 1
            raise RuntimeError(f'Work {phase}: ausente ou inválido; nenhuma imputação')
        self.work_items[phase] = self.work_items.get(phase, 0.0) + float(value)
        if sum(self.work_items.values()) > self.cap + 1e-10:
            raise TimeoutError('solve excedeu orçamento global Work: descartar resultado tardio')
        if self.remaining_wall() <= 0:
            raise TimeoutError('solve excedeu orçamento global wall: descartar resultado tardio')


def _solver_once(kind, data, K, budget: Budget, *, seed, threads):
    """Mede LP COMP ou core IP. Nunca devolve ótimo para solve interrompido.

    O próprio model.Work do Gurobi é debitado no orçamento conjunto; construções
    e validações entram no wall. Core IP é solver-numérico, não prova B0 E5.
    """
    budget.ensure()
    S, T, V, adj, A_r, r = data
    from gurobipy import GRB
    model = original = None
    try:
        if kind == 'comp_lp':
            from baseline import construir_modelo_baseline
            from harness import add_cuts_to_model
            original, y, *_ = construir_modelo_baseline(S, T, V, A_r)
            if len(K) != add_cuts_to_model(original, y, K, validate=(S, T, A_r)):
                raise ValueError('COMP LP: cortes K ausentes')
            original.update()
            model = original.relax()
        elif kind == 'core_ip':
            from yspace import _build_ymodel
            model, _ = _build_ymodel(V, K, integer=True, seed=seed, threads=threads,
                                      time_limit=budget.remaining_wall())
        else:
            raise ValueError('solve desconhecido')
        model.Params.OutputFlag = 0
        model.Params.Seed = seed
        model.Params.Threads = threads
        model.Params.WorkLimit = budget.remaining()
        model.Params.TimeLimit = budget.remaining_wall()
        if kind == 'comp_lp':
            model.Params.Method = 2
        model.optimize()
        work = getattr(model, 'Work', None)
        status = model.Status
        budget.add(kind, work)
        # WorkLimit da API é aproximado; não publicar solve que ultrapassou teto.
        optimal = status == GRB.OPTIMAL
        val = float(model.ObjVal) if optimal else None
        if val is not None and (not math.isfinite(val) or val < -1e-6):
            raise ValueError('referência baseline numérica inválida')
        return {'status': 'OPTIMAL_NUMERIC' if optimal else f'INCOMPLETE_GUROBI_{status}',
                'objective': val, 'solver_work': float(work)}
    finally:
        if model is not None:
            model.dispose()
        if original is not None:
            original.dispose()


def _load_instance(row):
    """Não lê instâncias de um resultado; usa fábricas históricas/geradores congelados."""
    if row['level'] == 1:
        from run_n1_t5 import corpus, instance_hash
        matches = [inst for inst in corpus() if inst['nome'] == row['name']]
        if len(matches) != 1:
            raise ValueError(f'{row["name"]}: corpus da N1 divergiu')
        inst = matches[0]
        if instance_hash(inst) != row['instance_sha256']:
            raise ValueError('instância histórica N1-T5 mudou')
        data = tuple(inst[k] for k in ('S', 'T', 'V', 'adj', 'A_r', 'r'))
    else:
        from run_n2_t1 import level_two_instance
        inst = level_two_instance(row['source'], row['parameters'])
        if inst['data_sha256_n2'] != row['instance_sha256']:
            raise ValueError('instância gerada nível 2 divergiu do freeze')
        data = tuple(inst[k] for k in ('S', 'T', 'V', 'adj', 'A_r', 'r'))
    S, T, V, adj, A_r, r = data
    if (len(V), len(S), r) != (row['n'], row['m'], row['r']):
        raise ValueError('dimensões N2-T1 alteradas')
    return data


def _verify_reach(data):
    """Recalcula alcance com código-base original e rejeita arcos incompatíveis."""
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from ms_utils import construir_arcos_alcance
    _, _, V, adj, arcs, r = data
    expected = construir_arcos_alcance(V, adj, r)
    if len(arcs) != len(set(arcs)) or set(arcs) != set(expected):
        raise ValueError('alcance A_r divergiu da reconstrução independente')
    return len(expected)


def _prepare_k(data, row):
    from fcc_k import prepare_k
    S, T, V, adj, A_r, r = data
    K, digest, counts = prepare_k(S, T, V, adj, A_r, r)
    if row.get('k_sha256') is not None and row['k_sha256'] != digest:
        raise ValueError('hash K nível 1 divergiu da N1 congelada')
    return K, digest, counts


def _make_curve(case, final, prior_work, phase_wall):
    """Reverifica prova de CADA snapshot via E5 (sem reler Gurobi).

    Prova de LP só é promovida no gráfico se K foi validado pela E5 e se
    a execução global não foi excedida. Sem prova, coluna LB permanece vazia.
    """
    from n2_t3_cert_integration import CertifiedCGResult
    from n2_t3_cert_core import LP_SCOPE
    from n2_t3_cert_validation import _verify_e4_events
    base = final.numerical_result
    history = getattr(base, 'history', ())
    by_iteration = {e.iteration: e for e in final.audit_history}
    result = []
    best = None
    for rec in history:
        event = by_iteration.get(rec.iteration)
        reason = ''
        if event is not None and final.physical_status == CERTIFIED:
            stub = CertifiedCGResult(base, (event,), None, CERTIFIED, LP_SCOPE,
                                     'replay racional E5 para curva', 0.0)
            checked, warnings = _verify_e4_events(stub, final.k_evidence,
                                                   max_enum_vertices=10)
            if warnings:
                reason = '; '.join(warnings)
            if checked is not None and (best is None or checked.lb_exact > best[0]):
                best = (checked.lb_exact, checked.source)
        work = rec.cumulative_work
        cumulative = (None if work is None else prior_work + work)
        result.append({
            'name': case['name'], 'family': case['family'], 'level': case['level'],
            'iteration': rec.iteration,
            'cumulative_work': '' if cumulative is None else cumulative,
            'cumulative_wall_s': phase_wall + rec.wall_elapsed,
            'lb_status': CERTIFIED if best else UNCERTIFIED,
            'lb_exact': _ratio(best[0]) if best else '',
            'lb_source': best[1] if best else '',
            'reference_b0': ('' if case['B0_reference'] is None else case['B0_reference']),
            'reference_full_lp': ('' if case['full_lp_reference'] is None else case['full_lp_reference']),
            'numeric_rmp_objective': (rec.rmp_objective if rec.rmp_objective is not None else ''),
            'n_columns': rec.columns_after, 'pricing_calls': sum(
                bool(x.pricing_cost) for x in history if x.iteration <= rec.iteration),
            'note': reason or rec.decision,
        })
    if best and best[0] > final.physical_lb_exact:
        raise AssertionError('curva contém LB maior que prova final E5')
    return result


def _record_summary(case, data, digest, K, final, budget, phases, b0_comp, b0_core,
                    curve, *, freeze_hash):
    base = final.numerical_result
    b0 = _reference(case['B0_reference'])
    if case['level'] == 2 and b0_comp['objective'] is not None and b0_core['objective'] is not None:
        b0 = _reference(max(b0_comp['objective'], b0_core['objective']))
    num = getattr(base, 'rmp_objective', None)
    lb = final.physical_lb_exact if final.physical_status == CERTIFIED else None
    gain = None if lb is None or b0 is None else lb - b0
    incr = (_reference(case['expected_positive_increment']) if case['level'] == 1 else None)
    recovery = (None if gain is None or incr is None or incr <= 0 else gain / incr)
    hmaster = sum((rec.master_cost.runtime or 0.0) for rec in base.history)
    hprice = sum((rec.pricing_cost.runtime or 0.0) for rec in base.history
                 if rec.pricing_cost is not None)
    wmaster = sum(rec.master_cost.work for rec in base.history
                  if rec.master_cost.work is not None)
    wprice = sum(rec.pricing_cost.work for rec in base.history
                 if rec.pricing_cost is not None and rec.pricing_cost.work is not None)
    missing = base.unmeasured_work_calls
    if any(rec.master_cost.work is None or
           (rec.pricing_cost is not None and rec.pricing_cost.work is None)
           for rec in base.history):
        missing = max(1, missing)
    if missing:
        work = None
    else:
        work = budget.work_items.get('comp_lp', 0.0) + budget.work_items.get('core_ip', 0.0) + wmaster + wprice
    gaps = [abs(rec.candidate_reduced_cost - rec.pricing_solver_bound)
            for rec in base.history if rec.pricing_solver_bound is not None and
            rec.candidate_reduced_cost is not None and
            math.isfinite(rec.pricing_solver_bound) and math.isfinite(rec.candidate_reduced_cost)]
    status = ('CERTIFIED_PHYSICAL_LB' if lb is not None and work is not None and
              work <= budget.cap + 1e-10 and budget.remaining_wall() > 0
              else 'UNCERTIFIED_OR_BUDGET_EXHAUSTED')
    row = dict(
        name=case['name'], family=case['family'], level=case['level'], n=case['n'],
        m=case['m'], r=case['r'], instance_sha256=case['instance_sha256'],
        k_sha256=digest, n_K=len(K), freeze_sha256=freeze_hash,
        path='B/F-CC+K ROOT_ONLY', seed=42, threads=4, work_cap=budget.cap,
        wall_cap_s=budget.wall_cap,
        b0_reference='' if b0 is None else _ratio(b0),
        b0_reference_status=('N1_FROZEN_REFERENCE' if case['level'] == 1 else
                             'OPTIMAL_NUMERIC_NOT_E5_CERTIFIED' if b0 is not None else
                             'NOT_MEASURED_OR_INTERRUPTED'),
        b0_comp_lp=b0_comp.get('objective', '') if b0_comp.get('objective') is not None else '',
        b0_core_ip=b0_core.get('objective', '') if b0_core.get('objective') is not None else '',
        b0_certificate_status=UNCERTIFIED, b0_certified_exact='',
        full_lp_historical='' if case['full_lp_reference'] is None else case['full_lp_reference'],
        lp_status=final.lp_status, lp_lb_exact=_ratio(final.lp_lb_exact),
        lb_continuous_exact=_ratio(lb), lp_source=final.lp_source or '',
        physical_status=final.physical_status, physical_lb_exact=_ratio(lb),
        physical_integer_lb=final.physical_integer_lb if lb is not None else '',
        upper_exact=_ratio(final.primal_upper.u_exact) if final.primal_upper else '',
        g2_status=final.convergence_status,
        gain_over_b0_reference=_ratio(gain),
        recovery_fraction_level1=_ratio(recovery),
        rmp_obj_numeric_diagnostic=num if num is not None else '',
        stop_reason=base.stop_reason, pricing_calls=base.pricing_calls,
        columns_added=base.columns_added, n_columns_final=len(base.columns),
        iterations=base.iterations, n_cuts=len(K),
        pricing_gap_last_numeric=gaps[-1] if gaps else '',
        pricing_gap_max_numeric=max(gaps) if gaps else '',
        work_comp_lp=budget.work_items.get('comp_lp', 0.0),
        work_core_ip=budget.work_items.get('core_ip', 0.0),
        work_master=wmaster, work_pricing=wprice,
        work_total=work if work is not None else '', work_unmeasured_calls=missing,
        wall_assembly_s=phases.get('assembly', 0), wall_reach_s=phases.get('reach', 0),
        wall_k_s=phases.get('K', 0), wall_comp_lp_s=phases.get('comp_lp', 0),
        wall_core_ip_s=phases.get('core_ip', 0), wall_cg_s=phases.get('cg', 0),
        wall_master_solver_s=hmaster, wall_pricing_solver_s=hprice,
        wall_cg_overhead_s=max(0.0, base.wall_time - hmaster - hprice),
        wall_validation_s=final.validation_wall,
        wall_postcheck_s=phases.get('postcheck', 0),
        wall_other_s=0.0, wall_total_s=budget.elapsed(),
        peak_rss_mb=_max_rss_mb(), n_curve_points=len(curve),
        audit_warnings='; '.join(final.audit_warnings), status=status,
        justification=final.justification + '; B0: referência numérica/histórica, '
                       'SEM prova independente de B0 por E5; controle nível2 != benchmark',
    )
    # Fases de nível superior disjuntas: CG inclui solve e certificação E4;
    # wall_validation integra a chamada E5; subtempos não são somados duas vezes.
    exclusive = sum(float(phases.get(p, 0)) for p in ('assembly', 'reach', 'K',
                        'comp_lp', 'core_ip', 'cg', 'postcheck'))
    row['wall_other_s'] = max(0.0, row['wall_total_s'] - exclusive)
    return row


class MeasuredAbstention(RuntimeError):
    def __init__(self, cause, budget, phases):
        super().__init__(f'{type(cause).__name__}: {cause}')
        self.work_items = dict(budget.work_items)
        self.unmeasured = budget.unmeasured
        self.wall_phases = dict(phases)
        self.wall_elapsed = budget.elapsed()


def run_one(case, *, freeze_hash, clock=time.monotonic):
    """Mede apenas a instância informada; sem buscar novas instâncias adaptativamente."""
    budget = Budget(164.0, 1800.0, clock=clock)
    phases = {}
    try:
        start = clock()
        data = _load_instance(case)
        phases['assembly'] = max(0.0, clock() - start)
        # Reconstruir alcance independentemente; fábrica mede assembly; esta
        # segunda checagem mede reach e impede usar H construído errado.
        start = clock()
        try:
            _verify_reach(data)
        finally:
            phases['reach'] = max(0.0, clock() - start)
        budget.ensure()
        start = clock()
        K, digest, _ = _prepare_k(data, case)
        phases['K'] = max(0.0, clock() - start)
        budget.ensure()
        b0_comp, b0_core = {'objective': None}, {'objective': None}
        if case['level'] == 1:
            from run_n2_t1 import prior_rows
            historic, _ = prior_rows()
            historical_row = historic[case['name']]
            if _reference(historical_row['B0']) != _reference(case['B0_reference']):
                raise ValueError('B0 N1-T5 divergiu do freeze N2-T1')
            if _reference(historical_row['lp_fcc_k']) != _reference(case['full_lp_reference']):
                raise ValueError('LP N1-T5 divergiu do freeze N2-T1')
            b0_comp = {'objective': float(historical_row['lp_comp']),
                       'status': 'HISTORICAL_N1_T5_NOT_REMEASURED'}
            b0_core = {'objective': float(historical_row['core_ip']),
                       'status': 'HISTORICAL_N1_T5_NOT_REMEASURED'}
            if abs(max(b0_comp['objective'], b0_core['objective']) -
                   float(case['B0_reference'])) > 1e-6:
                raise ValueError('B0 não coincide com max(COMP LP,core IP) histórico')
        if case['level'] == 2:
            for label in ('comp_lp', 'core_ip'):
                budget.ensure()
                start = clock()
                try:
                    measured = _solver_once(label, data, K, budget, seed=42, threads=4)
                finally:
                    phases[label] = max(0.0, clock() - start)
                if label == 'comp_lp':
                    b0_comp = measured
                else:
                    b0_core = measured
        # No nível 1 não gastar Work reproduzindo baseline já congelada.
        budget.ensure()
        from n2_t3_cert_integration import CertificationOptions
        from n2_t3_cert_validation import run_verified_column_generation
        options = CertificationOptions(use_n1=True, use_n2=True, enum_cap=None,
                                       max_enum_vertices=10, max_n2_vertices=24)
        start = clock()
        final = run_verified_column_generation(
            *data, K=K, k_hash=digest, options=options,
            max_iterations=300, work_limit=budget.remaining(),
            time_limit=budget.remaining_wall(),
            master_params={'Seed': 42, 'Threads': 4},
            pricing_params={'Seed': 42, 'Threads': 4},
        )
        phases['cg'] = max(0.0, clock() - start)
        if final.numerical_result is None:
            raise RuntimeError('E5 sem resultado do controlador; não imputar Work')
        base = final.numerical_result
        if base.unmeasured_work_calls:
            raise RuntimeError('CG utilizou solve com Work não mensurado')
        if base.total_work is None:
            raise RuntimeError('CG sem total de Work certificado contabilmente')
        decomposed = sum(rec.master_cost.work for rec in base.history)
        decomposed += sum(rec.pricing_cost.work for rec in base.history
                          if rec.pricing_cost is not None)
        if not math.isclose(decomposed, base.total_work, rel_tol=1e-10, abs_tol=1e-9):
            raise RuntimeError('Work da CG não coincide com soma master+pricing')
        budget.add('cg', base.total_work)
        start = clock()
        curve = _make_curve(case, final, budget.work_items.get('comp_lp', 0) +
                            budget.work_items.get('core_ip', 0),
                            phases['assembly'] + phases['reach'] + phases['K'] +
                            phases.get('comp_lp', 0) + phases.get('core_ip', 0))
        phases['postcheck'] = max(0.0, clock() - start)
        if budget.remaining_wall() <= 0:
            raise TimeoutError('auditoria/pós-verificação excedeu guarda de parede')
        if budget.remaining() > 0:
            budget.ensure()
        row = _record_summary(case, data, digest, K, final, budget, phases,
                              b0_comp, b0_core, curve, freeze_hash=freeze_hash)
        # Check exato de coerência do prefixo e da evidência final.
        if curve and final.physical_status == CERTIFIED:
            certified = [Fraction(item['lb_exact']) for item in curve if item['lb_status'] == CERTIFIED]
            if certified and max(certified) != final.physical_lb_exact:
                raise ValueError('evolução LB vs Work contradiz prova E5 final')
        return row, curve

    except (RuntimeError, ValueError, TypeError, TimeoutError, AssertionError) as exc:
        raise MeasuredAbstention(exc, budget, phases) from exc


def _failed_row(case, freeze_hash, exc, wall_seconds):
    # Uma exceção nunca é convertida em LB=0 nem em B0=0.
    partial = dict(getattr(exc, 'work_items', {}))
    return {'name': case['name'], 'family': case['family'], 'level': case['level'],
            'n': case['n'], 'm': case['m'], 'r': case['r'],
            'instance_sha256': case['instance_sha256'], 'freeze_sha256': freeze_hash,
            'path': 'B/F-CC+K ROOT_ONLY', 'seed': 42, 'threads': 4,
            'work_cap': 164.0, 'wall_cap_s': 1800.0,
            'status': 'ABSTAINED_INCOMPLETE', 'lp_status': UNCERTIFIED,
            'physical_status': UNCERTIFIED, 'b0_certificate_status': UNCERTIFIED,
            'wall_total_s': wall_seconds,
            'work_comp_lp': partial.get('comp_lp', ''),
            'work_core_ip': partial.get('core_ip', ''),
            'work_total': '',
            'work_unmeasured_calls': getattr(exc, 'unmeasured', ''),
            'audit_warnings': ('partial_cg_work=' + str(partial.get('cg', 'UNKNOWN'))),
            'justification': f'{type(exc).__name__}: {exc}; partial Work: {partial}'}


def _curve_svg(curves, rows):
    """Gráfico reproduzível por instância, sem solver ou dependências extras.

    Apenas pontos E5 revalidados. Gráfico em degraus: o último limite
    certificado continua válido nas iterações seguintes (Work cumulativo).
    """
    width, height = 920, 240 * len(EXPECTED_NAMES) + 50
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
             f'viewBox="0 0 {width} {height}">',
             '<rect width="100%" height="100%" fill="white"/>',
             '<text x="32" y="28" font-family="sans-serif" font-size="18">'
             'N2-T5 — LB físico certificado × Work cumulativo</text>']
    palette = ('#135d9c', '#ba5a1f', '#39723b', '#75369b')
    for index, name in enumerate(EXPECTED_NAMES):
        records = [p for p in curves if p['name'] == name and p['lb_status'] == CERTIFIED
                   and p['cumulative_work'] != '']
        row = next((r for r in rows if r['name'] == name), None)
        top = 65 + 240 * index
        parts.append(f'<text x="42" y="{top}" font-size="15" '
                     f'font-family="sans-serif">{xml_escape(name)}</text>')
        x0, y0, x1, y1 = 70, top + 30, 840, top + 174
        parts.extend([f'<path d="M{x0},{y0} V{y1} H{x1}" stroke="#222" '
                      'stroke-width="1.1" fill="none"/>',
                      f'<text x="375" y="{y1+28}" font-size="12" '
                      'font-family="sans-serif">Work Gurobi acumulado</text>',
                      f'<text x="20" y="{y0+10}" font-size="12" '
                      'font-family="sans-serif">LB</text>'])
        if not records:
            parts.append(f'<text x="95" y="{y0+65}" fill="#777" '
                         'font-family="sans-serif" font-size="13">'
                         'Nenhum ponto físico certificado registrado</text>')
            continue
        points = [(float(p['cumulative_work']), float(Fraction(p['lb_exact'])))
                  for p in records]
        max_x = max([x for x, _ in points] + [1e-8])
        max_y = max([y for _, y in points] + [1])
        coords = [(x0 + 20 + (x / max_x) * (x1 - x0 - 40),
                   y1 - 8 - (y / max_y) * (y1 - y0 - 20)) for x, y in points]
        steps = f'M{coords[0][0]:.2f},{coords[0][1]:.2f}'
        for cx, cy in coords[1:]:
            steps += f' H{cx:.2f} V{cy:.2f}'
        color = palette[index]
        parts.append(f'<path d="{steps}" fill="none" '
                     f'stroke="{color}" stroke-width="2"/>')
        for px, py in coords:
            parts.append(f'<circle cx="{px:.2f}" cy="{py:.2f}" '
                         f'r="3" fill="{color}"/>')
        parts.extend([f'<text x="{x0}" y="{y1+15}" font-size="11" '
                      f'font-family="sans-serif">0</text>',
                      f'<text x="{x1-50}" y="{y1+15}" font-size="11" '
                      f'font-family="sans-serif">{max_x:.5g}</text>',
                      f'<text x="{x0-36}" y="{y0+10}" font-size="11" '
                      f'font-family="sans-serif">{max_y:.5g}</text>'])
        if row and row.get('b0_reference'):
            parts.append(f'<text x="640" y="{y0+12}" fill="#666" '
                         f'font-size="12" font-family="sans-serif">'
                         f'B0 referência: {xml_escape(str(row["b0_reference"]))}</text>')
    parts.append('</svg>')
    return ('\n'.join(parts) + '\n').encode('utf8')


def _write_new(directory: Path, rows, curves, manifest, report):
    """Arquivos de evidência somente create-only; não deixa resultados antigos desaparecerem."""
    if directory.exists() and any(directory.iterdir()):
        raise FileExistsError('diretório de N2-T5 não está vazio; usar --output-dir novo')
    directory.mkdir(parents=True, exist_ok=True)
    artifacts = {
        'n2-t5-medicoes.csv': _csv_bytes(rows, FIELDS),
        'n2-t5-lb-versus-work.csv': _csv_bytes(curves, CURVE_FIELDS),
        'n2-t5-custos.md': report.encode('utf8'),
        'n2-t5-lb-versus-work.svg': _curve_svg(curves, rows),
    }
    manifest = dict(manifest)
    manifest['artifacts_sha256'] = {name: hashlib.sha256(raw).hexdigest()
                                    for name, raw in artifacts.items()}
    artifacts['n2-t5-manifest.json'] = _safe_json(manifest)
    for name, raw in artifacts.items():
        with (directory / name).open('xb') as f:
            f.write(raw)
    return tuple(directory / name for name in artifacts)


def validate_accounting(row):
    """Soma independente dos campos declarados (sem runtime contado duas vezes)."""
    if row.get('work_total', '') != '':
        actual = sum(float(row.get(k, 0)) for k in (
            'work_comp_lp', 'work_core_ip', 'work_master', 'work_pricing'))
        if not math.isclose(actual, float(row['work_total']), rel_tol=1e-10, abs_tol=1e-9):
            raise ValueError('Work total não coincide com as quatro parcelas do solver')
        if actual > 164 + 1e-9:
            raise ValueError('Work total acima do congelado')
    if row.get('wall_total_s', '') != '' and row.get('status') != 'ABSTAINED_INCOMPLETE':
        keys = ('wall_assembly_s', 'wall_reach_s', 'wall_k_s', 'wall_comp_lp_s',
                'wall_core_ip_s', 'wall_cg_s', 'wall_postcheck_s', 'wall_other_s')
        parts = sum(float(row.get(k, 0)) for k in keys)
        if not math.isclose(parts, float(row['wall_total_s']), abs_tol=1e-6):
            raise ValueError('Wall total não coincide com fases disjuntas')
    if row.get('lp_status') == CERTIFIED and not row.get('lp_lb_exact'):
        raise ValueError('status CERTIFIED sem certificado racional')
    if row.get('physical_status') == CERTIFIED and not row.get('physical_lb_exact'):
        raise ValueError('limite físico declarado sem evidência')
    if row.get('b0_reference', '') == '' and row.get('gain_over_b0_reference', '') != '':
        raise ValueError('não pode calcular ganho sem B0')


def _cost_report(rows, curves, *, context):
    lines = [
        '# N2-T5 — custos e curvas prospectivos', '',
        'Medições produzidas pelo executor congelado em N2-T1. **N2 PASS/FAIL não é decidido aqui.**',
        '', '## Proveniência e protocolo', '',
        f"- Freeze N2-T1 SHA-256: `{context['freeze_sha256']}`",
        f"- Replay corrigido N2-T4 CSV SHA-256: `{context['t4']['csv_sha256']}`",
        '- F-CC+K root-only, Gurobi Threads=4, Seed=42, PYTHONHASHSEED=0.',
        '- Work cap=164 por instância para *todos* os solves; wall cap=1800 s.',
        '- Ref. nível 1: B0 e full LP históricos. Nível 2: COMP LP + core IP recomputados.',
        '- Baselines de solver/histórico são referências, NÃO prova E5 de B0 físico.',
        '- Certified físico somente com reauditoria E5. RMP/ObjBoundC são diagnósticos.',
        '- Curva de LB certificado reaudita evidências da E4 contra o K real antes de publicar.',
        '- Visualização: `n2-t5-lb-versus-work.svg` (somente pontos certificados).',
        '- Memória é máximo RSS do processo até a medição; não é pico isolado por solve.',
        '', '## Medições', '',
        '| Caso | B0 referência | LB físico (exato) | Estado | Work total | Wall s | Pontos curva |',
        '|---|---:|---:|---|---:|---:|---:|',
    ]
    for r in rows:
        lines.append(f"| `{r['name']}` | {r.get('b0_reference') or 'NOT MEASURED'} | "
                     f"{r.get('physical_lb_exact') or 'UNCERTIFIED'} | {r.get('status')} | "
                     f"{r.get('work_total') if r.get('work_total', '') != '' else 'UNKNOWN'} | "
                     f"{r.get('wall_total_s', '')} | {r.get('n_curve_points', 0)} |")
    lines.extend([
        '', '## Contabilidade', '',
        'Work = COMP LP + core IP + master + pricing (unidades Work Gurobi).',
        'Wall fases mutuamente exclusivas = montagem + alcance + K + COMP + core + CG '
        '+ pós-validação + outros. O runtime do master/pricing e a validação E5 são '
        'subpartes da fase CG; não somar duas vezes.',
        'Ausência/erro de Work ou perda de prazo invalida a publicação de um LB novo.',
        '', '## Limites científicos', '',
        '- Nível 2 não possui LP completo histórico: não imputar.',
        '- A medição B0 nível 2 é numérica. Sem auditoria independente, não chamá-la de LB físico certificado.',
        '- N2 N2-box usa multiplicadores racionais zero na E4; limites podem ser fracos.',
        '- Pontos LB × Work pertencem ao momento anterior à auditoria final e só entram '
        'quando suas provas passam na reauditoria racional E5.',
        '- Experimentos não alteram split benchmark-v1, freezes, nem introduzem branch-and-price.',
        '- Gate N2-T6 aplicará as condições de ganho ≥50%, repetição por família/nível, custo e validade.',
        '', '## Histórico de curva', '',
        f'{len(curves)} pontos em `n2-t5-lb-versus-work.csv`.', ''
    ])
    return '\n'.join(lines)


def run_all(output_dir: Path, *, evaluator=run_one, preflight=check, clock=time.monotonic):
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError('saída já existe; execução é create-only')
    context = preflight()
    freeze = check_freeze(full=False)
    rows, curves = [], []
    freeze_hash = context['freeze_sha256']
    for item in freeze['instances']:
        started = clock()
        try:
            row, points = evaluator(item, freeze_hash=freeze_hash)
            validate_accounting(row)
            if row['name'] != item['name'] or row['family'] != item['family']:
                raise ValueError('executor devolveu outra instância')
        except (ValueError, TypeError, RuntimeError, TimeoutError, AssertionError) as exc:
            row, points = _failed_row(item, freeze_hash, exc, clock() - started), []
        rows.append(row)
        curves.extend(points)
        print(f"{item['name']}: {row['status']}", flush=True)
    total_certified = sum(row.get('physical_status') == CERTIFIED and
                          row.get('status') == 'CERTIFIED_PHYSICAL_LB' for row in rows)
    manifest = {
        'task': 'N2-T5', 'status': 'MEASURED_PENDING_N2_T6', 'scope': 'prospective, root only',
        'freeze_sha256': freeze_hash, 't4_sha256': context['t4'],
        'instances_in_freeze_order': list(EXPECTED_NAMES),
        'n_rows': len(rows), 'n_physical_certified': total_certified,
        'protocol': freeze['protocol'],
        'limitations': [
            'NOT N2 PASS/FAIL', 'RMP objective is not LB', 'ObjBoundC is diagnostic only',
            'N2-T3 E4 N2 multipliers initially zero',
            'B0 numeric/archive reference is not certified independent proof E5',
            'B0 and full LP for level 2 may be NOT MEASURED',
        ],
    }
    report = _cost_report(rows, curves, context=context)
    files = _write_new(output_dir, rows, curves, manifest, report)
    for p in files:
        print('EVIDÊNCIA', p)
    return 0 if len(rows) == 4 and all(row['status'] == 'CERTIFIED_PHYSICAL_LB'
                                      for row in rows) else 2


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('check', 'run'))
    parser.add_argument('--output-dir', type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    try:
        if args.action == 'check':
            state = check()
            print('N2-T5 CHECK PASS: 4 instâncias, 2 famílias, 2 níveis; '
                  'Gate N2-T4 + freeze validados, sem solves ou saída gerada')
            print('freeze:', state['freeze_sha256'])
            return 0
        return run_all(args.output_dir)
    except (RuntimeError, ValueError, OSError, FileExistsError) as exc:
        print('N2-T5 ERROR:', type(exc).__name__, str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
