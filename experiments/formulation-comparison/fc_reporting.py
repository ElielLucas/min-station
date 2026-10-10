"""Comparação base × F-CC+K: escrita de CSV/JSON/relatório.

Toda linha escrita vem de um `LPResult`/`MIPResult` real produzido por
`fc_core`. Nenhum valor é inferido, interpolado ou preenchido por padrão
além dos rótulos de status/certificação explícitos já definidos em
`fc_core` (`NOT_MEASURED_*`, `UNCERTIFIED_*`). Nada aqui sobrescreve
arquivos de execuções anteriores: cada rodada grava em um subdiretório
próprio, nomeado por timestamp (ver `run_comparison.py`).
"""
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path

from fc_core import LPResult, MIPResult

RESULTS_FIELDS = [
    'instance_name', 'classe', 'familia', 'n', 'm_arestas', 'm_robos', 'r', 'instance_sha256',
    'formulation', 'modality', 'status', 'certification', 'objective_primal', 'lb_best', 'ub_best',
    'gap_abs', 'gap_rel', 'optimality_proven', 'time_s', 'work', 'ru_maxrss_kb_before',
    'ru_maxrss_kb_after', 'n_vars', 'n_cons', 'time_to_first_feasible_s', 'time_to_best_s',
    'time_to_proof_s', 'nodes', 'physically_validated', 'observations',
    'wall_total_s', 'solver_runtime_s', 'stop_reason', 'wall_startup_s',
    'wall_k_preparation_s', 'wall_model_build_s', 'wall_solve_s',
    'wall_validation_s', 'wall_supervisor_shutdown_s', 'wall_phases_json',
    'comparison_role', 'pair_status', 'pair_reason', 'k_sha256', 'n_K',
    'n_K_added', 'k_validated', 'physical_ub_status', 'pair_instance_sha256',
    'pair_k_sha256',
]

EVOLUTION_FIELDS = [
    'instance_name', 'formulation', 'modality', 'mark_s', 'observed_time_s', 'lb', 'ub', 'nodes',
    'work',
]


def _wall_fields(result):
    phases = dict(result.phase_wall_s)
    return {
        'wall_total_s': result.time_s,
        'solver_runtime_s': result.solver_runtime_s if result.solver_runtime_s is not None else '',
        'stop_reason': (result.stop_reason or
                        (result.status if isinstance(result, LPResult) else result.status_name)),
        'wall_startup_s': phases.get('startup', 0.0),
        'wall_k_preparation_s': phases.get('k_preparation', 0.0),
        'wall_model_build_s': phases.get('model_build', 0.0),
        'wall_solve_s': phases.get('solve', 0.0),
        'wall_validation_s': phases.get('validation', 0.0),
        'wall_supervisor_shutdown_s': phases.get('supervisor_shutdown', 0.0),
        'wall_phases_json': json.dumps(phases, sort_keys=True),
    }


def _lp_row(instance, result: LPResult):
    return {
        'instance_name': instance.nome, 'classe': instance.classe, 'familia': instance.familia,
        'n': instance.n, 'm_arestas': instance.m_arestas, 'm_robos': instance.m, 'r': instance.r,
        'instance_sha256': instance.instance_sha256,
        'formulation': 'baseline' if result.formulation in ('lp_base', 'lp_comp') else 'fcc_k',
        'modality': 'A', 'status': result.status, 'certification': result.certification,
        'objective_primal': '', 'lb_best': result.value if result.value is not None else '',
        'ub_best': '', 'gap_abs': '', 'gap_rel': '', 'optimality_proven': '',
        'time_s': result.time_s, 'work': result.work if result.work is not None else '',
        'ru_maxrss_kb_before': '', 'ru_maxrss_kb_after': '',
        'n_vars': result.n_vars if result.n_vars is not None else '',
        'n_cons': result.n_cons if result.n_cons is not None else '',
        'time_to_first_feasible_s': '', 'time_to_best_s': '', 'time_to_proof_s': '', 'nodes': '',
        'physically_validated': '',
        'observations': (f'{result.formulation}; K={result.n_K}; {result.reason}').strip('; '),
        'comparison_role': 'lp_control', 'pair_status': '', 'pair_reason': '',
        'k_sha256': result.k_sha256 or '', 'n_K': result.n_K if result.n_K is not None else '',
        'n_K_added': '', 'k_validated': '', 'physical_ub_status': '',
        'pair_instance_sha256': '', 'pair_k_sha256': '',
        **_wall_fields(result),
    }


def _mip_row(instance, result: MIPResult, pair=None):
    return {
        'instance_name': instance.nome, 'classe': instance.classe, 'familia': instance.familia,
        'n': instance.n, 'm_arestas': instance.m_arestas, 'm_robos': instance.m, 'r': instance.r,
        'instance_sha256': instance.instance_sha256, 'formulation': result.formulation,
        'modality': 'B', 'status': result.status_name, 'certification': result.certification,
        'objective_primal': result.objective_ub if result.objective_ub is not None else '',
        'lb_best': result.objective_lb if result.objective_lb is not None else '',
        'ub_best': result.objective_ub if result.objective_ub is not None else '',
        'gap_abs': result.gap_abs if result.gap_abs is not None else '',
        'gap_rel': result.gap_rel if result.gap_rel is not None else '',
        'optimality_proven': result.status_name == 'OPTIMAL',
        'time_s': result.time_s, 'work': result.work,
        'ru_maxrss_kb_before': (result.ru_maxrss_kb_before
                                 if result.ru_maxrss_kb_before is not None else ''),
        'ru_maxrss_kb_after': (result.ru_maxrss_kb_after
                                if result.ru_maxrss_kb_after is not None else ''),
        'n_vars': result.n_vars, 'n_cons': result.n_cons,
        'time_to_first_feasible_s': result.time_to_first_feasible_s
        if result.time_to_first_feasible_s is not None else '',
        'time_to_best_s': result.time_to_best_s if result.time_to_best_s is not None else '',
        'time_to_proof_s': result.time_to_proof_s if result.time_to_proof_s is not None else '',
        'nodes': result.nodes, 'physically_validated': result.physically_validated
        if result.physically_validated is not None else '',
        'observations': result.reason,
        'comparison_role': ('primary' if result.formulation in ('comp_mip', 'fcc_k')
                            else 'ablation_no_k'),
        'pair_status': (pair.status if pair is not None and
                        result.formulation in ('comp_mip', 'fcc_k') else
                        'ABLATION_ONLY' if result.formulation == 'baseline' else 'NOT_ASSESSED'),
        'pair_reason': (pair.reason if pair is not None and
                        result.formulation in ('comp_mip', 'fcc_k') else ''),
        'k_sha256': result.k_sha256 or '',
        'n_K': result.n_K if result.n_K is not None else '',
        'n_K_added': result.n_K_added if result.n_K_added is not None else '',
        'k_validated': result.k_validated,
        'physical_ub_status': result.physical_ub_status,
        'pair_instance_sha256': (pair.instance_sha256 or '') if pair is not None and
        result.formulation in ('comp_mip', 'fcc_k') else '',
        'pair_k_sha256': (pair.k_sha256 or '') if pair is not None and
        result.formulation in ('comp_mip', 'fcc_k') else '',
        **_wall_fields(result),
    }


def rows_for_modality_a(instance, a_results):
    """Linhas de resultado só da Modalidade A (quando B não foi executada)."""
    return [_lp_row(instance, a_results[k]) for k in ('lp_base', 'lp_comp', 'lp_fcc_k')
            if k in a_results]


def rows_for_instance(instance, a_results, b_baseline=None, b_fcc_k=None,
                      *, b_comp_mip=None, pair=None):
    """FC-02: par primário COMP+K × FCC+K e ablação sem K opcional.

    A assinatura antiga (instance, a, baseline, fcc) permanece aceita nos
    testes de regressão FC-01; esses dados legados não são par FC-02 válido.
    """
    rows = rows_for_modality_a(instance, a_results)
    evolution = []
    for result in (b_comp_mip, b_fcc_k, b_baseline):
        if result is None:
            continue
        rows.append(_mip_row(instance, result, pair))
        for point in result.evolution:
            evolution.append({
                'instance_name': instance.nome, 'formulation': result.formulation,
                'modality': 'B/C', 'mark_s': point.mark_s if point.mark_s != float('inf') else 'final',
                'observed_time_s': point.observed_time_s,
                'lb': point.lb if point.lb is not None else '',
                'ub': point.ub if point.ub is not None else '', 'nodes': point.nodes,
                'work': point.work if point.work is not None else '',
            })
    return rows, evolution


def write_csv(path: Path, fields, rows, append=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    novo = not path.exists()
    with path.open('a' if append else 'w', newline='', encoding='utf-8') as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        if novo or not append:
            writer.writeheader()
        writer.writerows(rows)


def _git_info(root: Path):
    def run(args):
        try:
            return subprocess.check_output(['git', *args], cwd=root, text=True).strip()
        except Exception as exc:  # pragma: no cover - ambiente sem git
            return f'ERRO: {exc}'
    return {
        'branch': run(['rev-parse', '--abbrev-ref', 'HEAD']),
        'commit': run(['rev-parse', 'HEAD']),
        'dirty': run(['status', '--porcelain']) != '',
    }


def _sha256_file(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reproducibility_manifest(root: Path, cfg, instances, environment, commands, limitations,
                             generated_files):
    """Hashes dos arquivos de formulação REUTILIZADOS (não dos novos), para
    provar que nada congelado foi tocado por esta comparação."""
    referenced = [
        'baseline.py', 'experiments/cuts/harness.py', 'experiments/cuts/cuts.py',
        'experiments/cuts/independent_validator.py',
        'experiments/alternative-formulations/fcc.py',
        'experiments/alternative-formulations/fcc_k.py',
        'instances/manifest.csv',
    ]
    hashes = {rel: _sha256_file(root / rel) for rel in referenced if (root / rel).is_file()}
    return {
        'git': _git_info(root),
        'config': cfg.as_dict(),
        'environment': environment,
        'reused_files_sha256': hashes,
        'instances': [
            {'nome': i.nome, 'classe': i.classe, 'familia': i.familia, 'n': i.n, 'm': i.m,
             'r': i.r, 'instance_sha256': i.instance_sha256}
            for i in instances
        ],
        'commands': commands,
        'limitations': limitations,
        'generated_files': generated_files,
    }


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str), encoding='utf-8')
