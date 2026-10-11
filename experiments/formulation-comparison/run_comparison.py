#!/usr/bin/env python3
"""Comparação base × F-CC+K — executor independente da fase N2.

Não reabre N1/N2: reutiliza as formulações já validadas (`baseline.py`,
`experiments/cuts/harness.py`, `experiments/alternative-formulations/fcc.py`
e `fcc_k.py`) em um experimento novo, isolado, com seus próprios arquivos de
resultado. A N2 encerrou com `N2 FAIL` (ver
`docs/technical/plans/execucao/n2-t6-gate-decisao-cientifica.md`); nada
aqui reinterpreta ou mede o master restrito/pricing da N2 — a Modalidade B
usa o F-CC+K *completo*, por enumeração total de `(W,I,J)`, não a geração
de colunas na raiz.

Exemplos:
    PYTHONHASHSEED=0 python run_comparison.py --tier pilot
    PYTHONHASHSEED=0 python run_comparison.py --tier main --time-limit 3600 \\
        --threads 4 --seed 42
    PYTHONHASHSEED=0 python run_comparison.py --tier scalability \\
        --modalities A --time-limit 600

Cada execução grava em `results/formulation-comparison/<tier>-<timestamp>/`,
sem sobrescrever rodadas anteriores. Não faz commit.
"""
from __future__ import annotations

import argparse
import csv
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import fc_config as fcfg  # noqa: E402
import fc_instances as fi  # noqa: E402
import fc_reporting as rep  # noqa: E402

RESULTS_DIR = ROOT / 'results' / 'formulation-comparison'

DEFAULT_FORMULATIONS = ('comp_mip', 'fcc_k')
ALLOWED_FORMULATIONS = frozenset((*DEFAULT_FORMULATIONS, 'baseline'))


def _check_gurobi():
    """Retorna (ok, mensagem). Nunca troca de solver silenciosamente."""
    try:
        import gurobipy as gp
    except ImportError as exc:
        return False, f'gurobipy não instalado neste ambiente: {exc}'
    try:
        m = gp.Model()
        m.dispose()
    except gp.GurobiError as exc:
        return False, f'Gurobi sem licença/recursos utilizáveis neste ambiente: {exc}'
    return True, ''


def _order_tasks(instances, formulations=DEFAULT_FORMULATIONS):
    """Alterna ordem do PAR e roda ablação, se solicitada, separadamente."""
    primary = tuple(f for f in DEFAULT_FORMULATIONS if f in formulations)
    optional = tuple(f for f in formulations if f not in primary)
    tasks = []
    for idx, inst in enumerate(instances):
        order = primary if idx % 2 == 0 else tuple(reversed(primary))
        tasks.append((inst, order + optional))
    return tasks


def run(tier, cfg, out_dir, modalities, formulations=DEFAULT_FORMULATIONS, *, plots=False):
    import fc_core as fcore
    from fc_pairing import assess_primary_pair
    from fc_evidence import physical_upper_bound, safe_solver_bound
    from fc_integrity import scalability_from_csv, source_inventory

    # Congela o inventário antes da leitura/otimização. Um arquivo de código
    # alterado durante a rodada não pode ser publicado como se fosse executado.
    code_at_start = source_inventory(ROOT)
    shared_start = time.monotonic()
    instances = fi.pool(tier)
    shared_instance_load_s = time.monotonic() - shared_start
    # FC-04: fail-closed se a pasta já contiver qualquer artefato anterior.
    if out_dir.exists() and any(out_dir.iterdir()):
        raise FileExistsError(f'FC04: pasta de resultados não vazia: {out_dir}')
    out_dir.mkdir(parents=True, exist_ok=True)
    results_csv = out_dir / 'results.csv'
    evolution_csv = out_dir / 'evolution.csv'
    log_path = out_dir / 'run.log'
    environment = fcfg.environment_manifest()
    print(f'[{tier}] {len(instances)} instâncias; modalidades={modalities}; '
          f'formulations={formulations}; saída={out_dir}')

    all_results_written = False
    errors = []
    with log_path.open('w', encoding='utf-8') as log:
        def report(msg):
            print(msg)
            log.write(msg + '\n')
            log.flush()

        for inst, order in _order_tasks(instances, formulations):
            report(f'== {inst.nome} (n={inst.n}, m={inst.m}, r={inst.r}, '
                   f'família={inst.familia}, classe={inst.classe})')
            a_results = {}
            if 'A' in modalities:
                try:
                    a_results = fcore.run_modality_a(inst, cfg)
                    for k in ('lp_base', 'lp_comp', 'lp_fcc_k'):
                        r = a_results.get(k)
                        if r:
                            report(f'   A/{k}: {r.status} valor={r.value} '
                                   f'solver_evidence={r.solver_evidence} rational={r.certification} '
                                   f'wall={r.time_s:.3f}s '
                                   f'solver={r.solver_runtime_s} work={r.work} '
                                   f'stop={r.stop_reason} reason={r.reason.splitlines()[0] if r.reason else ""}')
                            if r.status in ('WORKER_ERROR', 'SOLVER_UNAVAILABLE'):
                                errors.append((inst.nome, f'A/{k}', r.reason))
                except Exception:  # noqa: BLE001 - falha de uma instância não derruba o lote
                    tb = traceback.format_exc()
                    report(f'   A: FALHA\n{tb}')
                    errors.append((inst.nome, 'A', tb))

            b_results = {}
            pair = None
            if 'B' in modalities:
                runners = {'comp_mip': fcore.run_modality_b_comp,
                           'fcc_k': fcore.run_modality_b_fcc_k,
                           'baseline': fcore.run_modality_b_baseline}
                for formulation in order:
                    try:
                        b_results[formulation] = runners[formulation](inst, cfg)
                        r = b_results[formulation]
                        report(f'   B/{formulation}: {r.status_name} ub={r.objective_ub} '
                               f'lb_numeric={safe_solver_bound(r)} solver_evidence={r.solver_evidence} '
                               f'rational={r.certification} physical_ub={physical_upper_bound(r)} '
                               f'wall={r.time_s:.3f}s solver={r.solver_runtime_s} '
                               f'work={r.work:.4f} stop={r.stop_reason} '
                               f'validado={r.physically_validated} k={r.k_sha256} '
                               f'reason={r.reason.splitlines()[0] if r.reason else ""}')
                        if r.status_name in ('WORKER_ERROR', 'SOLVER_UNAVAILABLE'):
                            errors.append((inst.nome, f'B/{formulation}', r.reason))
                    except Exception:  # noqa: BLE001
                        tb = traceback.format_exc()
                        report(f'   B/{formulation}: FALHA\n{tb}')
                        errors.append((inst.nome, f'B/{formulation}', tb))
                pair = assess_primary_pair(inst, b_results.get('comp_mip'),
                                           b_results.get('fcc_k'))
                report(f'   B/PRIMARY_PAIR: {pair.status} '
                       f'k={pair.k_sha256} reason={pair.reason}')
                if pair.status in ('INTEGRITY_ERROR', 'INVALID_PHYSICAL_WITNESS'):
                    errors.append((inst.nome, 'B/PRIMARY_PAIR', pair.reason))

            if a_results or b_results:
                rows, evo = rep.rows_for_instance(
                    inst, a_results, b_results.get('baseline'), b_results.get('fcc_k'),
                    b_comp_mip=b_results.get('comp_mip'), pair=pair,
                )
                rep.write_csv(results_csv, rep.RESULTS_FIELDS, rows,
                              append=all_results_written)
                if evo:
                    rep.write_csv(evolution_csv, rep.EVOLUTION_FIELDS, evo,
                                  append=all_results_written)
                all_results_written = True

    # Artefatos completos são finalizados ANTES do manifesto e seu sidecar.
    if not results_csv.exists():
        rep.write_csv(results_csv, rep.RESULTS_FIELDS, [])
    if not evolution_csv.exists():
        rep.write_csv(evolution_csv, rep.EVOLUTION_FIELDS, [])
    if plots:
        from fc_plot_evolution import plot
        from fc_plot_evolution import load_points
        names = [i.nome for i in instances]
        for name in names:
            if load_points(evolution_csv, name):
                plot(evolution_csv, name, out_dir / f'evolution-{Path(name).stem}.png')
    scalability = None
    if tier == 'scalability':
        scalability = scalability_from_csv(
            results_csv, expected_instances=[i.nome for i in instances],
        )
        rep.write_json(out_dir / 'scalability_summary.json', scalability)
    # FC-05: a avaliação candidata é publicada ANTES da finalização FC-04,
    # para que pilot_gate.json e pilot_report.md recebam SHA-256 no manifesto.
    # Gate autoritativo é recomputado somente DEPOIS de conferir todos os hashes.
    if tier == 'pilot':
        from verify_comparison_pilot import publish_candidate
        with results_csv.open(encoding='utf-8', newline='') as stream:
            pilot_rows = list(csv.DictReader(stream))
        candidate_manifest = {
            'tier': tier,
            'modalities': list(modalities),
            'formulations': list(formulations),
            'config': cfg.as_dict(),
            'instances': [
                {'nome': inst.nome, 'instance_sha256': inst.instance_sha256}
                for inst in instances
            ],
            'errors': [{'instance': name, 'stage': stage, 'traceback': detail}
                       for name, stage, detail in errors],
        }
        publish_candidate(out_dir, pilot_rows, candidate_manifest)

    commands = [
        f'PYTHONHASHSEED=0 python run_comparison.py --tier {tier} '
        f'--modalities {",".join(modalities)} --time-limit {cfg.time_limit_s} '
        f'--threads {cfg.threads} --seed {cfg.seed} --max-w {cfg.max_w} '
        f'--lp-time-limit {cfg.lp_time_limit_s} '
        f'--formulations {",".join(formulations)}' + (' --plots' if plots else ''),
    ]
    limitations = [
        'F-CC+K (Modalidades A e B) usa enumeração completa de (W,I,J); instâncias acima do '
        'cap de enumeração (max_w) são marcadas NOT_MEASURED_CAP_EXCEEDED, nunca aproximadas.',
        'O lote scalability inclui instâncias deliberadamente acima do cap, para documentar a '
        'fronteira de escalabilidade, não para comparar diretamente as duas formulações nelas.',
        'Memória é resource.ru_maxrss do worker isolado (pico cumulativo do worker); '
        'ver fc_config.ExperimentConfig.memory_metric.',
        'FC-02: par inteiro primário COMP+K (y binário, fluxo contínuo) × F-CC+K; '
        'baseline sem K é ablação opcional, nunca controle principal.',
        'PAIR_VALID confirma somente comparabilidade dos parâmetros e validade física das '
        'incumbentes observadas; não constitui prova racional independente de otimalidade.',
        'FC-03: solver_numeric_* são dados de ponto flutuante do Gurobi. ObjBound de '
        'modelo completo é apenas bound numérico; jamais certificado racional sem verifier.',
        'FC-03: nenhum comprovante racional independente é produzido automaticamente; '
        'rational_verification=NOT_CERTIFIED e certified_gap_status=INCONCLUSIVE por padrão.',
        'FC-03: colunas legadas ambíguas lb_best, ub_best, gap_abs, gap_rel, '
        'optimality_proven e time_to_proof_s permanecem vazias no schema FC03-v1.',
        'FC-04: relatório de escalabilidade mede somente as instâncias selecionadas no lote; '
        'nenhuma conclusão é estendida às 75 instâncias principais não sondadas.',
        'FC-05: o relatório pilot_gate.json é pré-auditoria; somente o verificador independente '
        'pós-manifesto fornece READY_FOR_EXTENDED. Nenhuma campanha longa é disparada.',
        'Este experimento é independente da N2 (N2-T2B/N2-T3..T6); não usa a geração de colunas '
        'na raiz nem reabre a decisão N2 FAIL.',
    ]
    generated = [p.relative_to(ROOT).as_posix() for p in sorted(out_dir.rglob('*'))
                 if p.is_file() and p.name not in ('manifest.json', 'manifest.sha256')]
    if source_inventory(ROOT) != code_at_start:
        raise ValueError('INTEGRITY_ERROR: código alterado durante a execução; '
                         'não publicar manifesto como se representasse o código executado')
    manifest = rep.reproducibility_manifest(ROOT, cfg, instances, environment, commands,
                                            limitations, generated, strict_generated=True)
    manifest['shared_instance_loading_wall_s'] = shared_instance_load_s
    manifest['tier'] = tier
    manifest['modalities'] = list(modalities)
    manifest['formulations'] = list(formulations)
    manifest['primary_comparison'] = ['comp_mip', 'fcc_k']
    manifest['optional_ablation'] = 'baseline'
    manifest['evidence_schema'] = 'FC03-v1'
    manifest['rational_verifier_executed'] = False
    manifest['rational_proofs_automatically_generated'] = False
    manifest['solver_numeric_bounds_are_rational_proofs'] = False
    manifest['scalability_summary'] = scalability
    manifest['errors'] = [{'instance': n, 'stage': s, 'traceback': tb} for n, s, tb in errors]
    rep.finalize_manifest(out_dir / 'manifest.json', manifest)
    gate_failed = False
    if tier == 'pilot':
        from verify_comparison_pilot import READY, evaluate
        audit_gate = evaluate(out_dir, root=ROOT)
        print(f'FC-05/GATE: {audit_gate["status"]} '
              f'artifact_audit={audit_gate["artifact_audit"]} '
              f'problems={audit_gate["problems"]}')
        # Não transforma incompletude em sucesso. Não inicia --tier main.
        gate_failed = audit_gate['status'] != READY
    print(f'Concluído. {len(errors)} falha(s) de execução; '
          f'gate_failed={gate_failed}. Artefatos em {out_dir}')
    return len(errors) + int(gate_failed)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--tier', choices=('pilot', 'main', 'scalability'), required=True)
    parser.add_argument('--modalities', default='A,B',
                        help='subconjunto separado por vírgula de {A,B} (C é coletada junto com B)')
    parser.add_argument('--formulations', default=','.join(DEFAULT_FORMULATIONS),
                        help='braços MIP: comp_mip,fcc_k[,baseline]; baseline sem K é ablação')
    parser.add_argument('--time-limit', type=float, default=None,
                        help='segundos globais por braço de MIP, incluindo montagem e validação; default 3600, '
                             'ou 120 com --tier pilot')
    parser.add_argument('--lp-time-limit', type=float, default=None,
                        help='segundos globais por braço LP, incluindo K, montagem e solver; default 60 no pilot')
    parser.add_argument('--threads', type=int, default=4)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--max-w', type=int, default=200000)
    parser.add_argument('--out-dir', type=Path, default=None)
    parser.add_argument('--plots', action='store_true',
                        help='gera PNGs da evolução antes de finalizar o manifesto')
    args = parser.parse_args(argv)

    modalities = tuple(sorted(set(args.modalities.split(','))))
    if not modalities or set(modalities) - {'A', 'B'}:
        parser.error('--modalities deve conter apenas A,B')
    formulations = tuple(f.strip() for f in args.formulations.split(',') if f.strip())
    if (not formulations or len(formulations) != len(set(formulations)) or
            set(formulations) - ALLOWED_FORMULATIONS):
        parser.error('--formulations aceita comp_mip,fcc_k,baseline, sem repetições')

    ok, msg = _check_gurobi()
    if not ok:
        print(f'ERRO: {msg}')
        print('Nenhum solver alternativo foi usado. Execute este comando em um ambiente com '
             'licença Gurobi válida.')
        return 2

    time_limit = args.time_limit
    if time_limit is None:
        time_limit = 120.0 if args.tier == 'pilot' else 3600.0
    lp_time_limit = args.lp_time_limit
    if lp_time_limit is None:
        lp_time_limit = 60.0 if args.tier == 'pilot' else 600.0
    cfg = fcfg.ExperimentConfig(threads=args.threads, seed=args.seed, time_limit_s=time_limit,
                                lp_time_limit_s=lp_time_limit, max_w=args.max_w,
                                modalities=('A', 'B', 'C'))

    out_dir = args.out_dir
    if out_dir is None:
        ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        out_dir = RESULTS_DIR / f'{args.tier}-{ts}'

    n_errors = run(args.tier, cfg, out_dir, modalities, formulations=formulations,
                   plots=args.plots)
    return 1 if n_errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
