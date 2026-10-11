#!/usr/bin/env python3
"""FC-06: pré-registro manual e execução OPCIONAL de até 3600s/ braço MIP.

Dois passos distintos: --prepare apenas lê/valida hashes e cria pré-registro;
--execute requer --confirm-long-run e pré-registro selado. Não há autoexecução.
Nunca modifica a N2 ou saídas anteriores.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import sys
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import fc_config as fcfg  # noqa: E402
import fc_instances as fi  # noqa: E402
from fc06_campaign import (  # noqa: E402
    ARMS, BUDGET_LP_S, BUDGET_MIP_S, SCHEMA, SEEDS,
    choose_instances, csv_rows, digest, make_plan, validate_prereg,
)
from fc_integrity import (source_inventory, sha256_file)  # noqa: E402
from verify_comparison_artifacts import verify as audit_artifacts  # noqa: E402
from verify_comparison_pilot import READY, evaluate as evaluate_pilot  # noqa: E402

EXTENDED_ROOT = ROOT / 'results' / 'formulation-comparison'


def _in_repo_dir(path: Path, *, must_exist=True):
    path = Path(path).resolve(strict=must_exist)
    path.relative_to(ROOT.resolve())  # ValueError em caminho fora do repositório
    return path


def _machine():
    return {'node': platform.node(), 'platform': platform.platform(),
            'python': sys.version.replace('\n', ' '), 'cpu_count': os.cpu_count(),
            'environment': fcfg.environment_manifest()}


def _screening_preflight(path: Path):
    path = _in_repo_dir(path)
    ok, problems = audit_artifacts(path, root=ROOT)
    if not ok:
        raise ValueError(f'SCREENING_ARTIFACT_AUDIT_FAILED:{problems}')
    manifest = json.loads((path / 'manifest.json').read_text(encoding='utf-8'))
    if manifest.get('tier') != 'main' or not {'comp_mip', 'fcc_k'} <= set(
            manifest.get('formulations', [])):
        raise ValueError('SCREENING_REQUIRES_MAIN_AND_BOTH_PRIMARY_ARMS')
    cfg = manifest.get('config', {})
    if cfg.get('time_limit_s', float('inf')) > 120 or cfg.get('time_limit_s', 0) <= 0:
        raise ValueError('SCREENING_MIP_CAP_MUST_BE_AT_MOST_120_SECONDS')
    return manifest, csv_rows(path / 'results.csv')


def _pilot_preflight(path: Path):
    path = _in_repo_dir(path)
    gate = evaluate_pilot(path, root=ROOT)
    if gate['status'] != READY:
        raise ValueError('FC05_GATE_NOT_READY:' + str(gate.get('problems')))
    return gate


def _safe_out_dir(path: Path):
    path = _in_repo_dir(path, must_exist=False)
    # Nenhum output anterior ou pasta fora de results/formulation-comparison.
    path.relative_to(EXTENDED_ROOT.resolve())
    if path == EXTENDED_ROOT.resolve() or not path.name.startswith('extended-'):
        raise ValueError('FC06: o destino deve ser uma nova pasta extended-*')
    return path


def prepare(*, pilot_run, screening_run, run_dir, requested=(),
            justification='', include_lp=True, threads=4, max_w=200000):
    """Não invoca gurobipy, _mip_job, optimize, nem quaisquer modelos."""
    out_dir = _safe_out_dir(run_dir)
    if out_dir.exists():
        raise FileExistsError(f'FC06: pasta já existe; proibido sobrescrever {out_dir}')
    pilot_run = _in_repo_dir(pilot_run)
    screening_run = _in_repo_dir(screening_run)
    _pilot_preflight(pilot_run)
    screening_manifest, screening_rows = _screening_preflight(screening_run)
    cfg = fcfg.ExperimentConfig(threads=threads, seed=42, time_limit_s=BUDGET_MIP_S,
                                lp_time_limit_s=BUDGET_LP_S, max_w=max_w)
    main = fi.pool('main')
    manifest_rows = {r['nome']: r for r in fi.load_manifest()}
    if requested:
        if len(requested) != len(set(requested)):
            raise ValueError('FC06: seleção com nomes duplicados')
        unknown = set(requested) - {inst.nome for inst in main}
        if unknown:
            raise ValueError(f'FC06: fora do pool MAIN: {sorted(unknown)}')
    selected, excluded = choose_instances(
        screening_rows, main, manifest_rows,
        requested=requested, justification=justification,
    )
    out_dir.mkdir(parents=True)
    (out_dir / 'eligibility_report.json').write_text(
        json.dumps({'status': 'ELIGIBLE' if selected else 'NOT_ELIGIBLE',
                    'selected': selected, 'excluded': excluded,
                    'note': 'Sem candidatos não se inicia a campanha de 3600s.'},
                   indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    if not selected:
        return {'status': 'NOT_ELIGIBLE', 'selected': [], 'excluded': excluded,
                'run_dir': str(out_dir)}
    plan = make_plan(selected, seeds=SEEDS, include_lp=include_lp)
    prereg = {
        'schema': SCHEMA, 'prepared_utc': datetime.now(timezone.utc).isoformat(),
        'pilot_gate': READY,
        'pilot_run': pilot_run.relative_to(ROOT).as_posix(),
        'pilot_manifest_sha256': sha256_file(pilot_run / 'manifest.json'),
        'screening_run': screening_run.relative_to(ROOT).as_posix(),
        'screening_manifest_sha256': sha256_file(screening_run / 'manifest.json'),
        'screening_results_sha256': sha256_file(screening_run / 'results.csv'),
        'selected': selected, 'excluded': excluded,
        'seeds': list(SEEDS), 'include_lp': bool(include_lp),
        'mip_wall_cap_s': BUDGET_MIP_S, 'lp_wall_cap_s': BUDGET_LP_S,
        'config': cfg.as_dict(), 'machine': _machine(),
        'code_files_sha256': source_inventory(ROOT),
        'metrics_mip': list(__import__('fc06_campaign').MIP_METRICS),
        'metrics_lp': list(__import__('fc06_campaign').LP_METRICS),
        'plan': plan,
        'no_universal_superiority_claim': True,
        'n2_gate_unchanged': 'N2 FAIL',
    }
    validate_prereg(prereg)
    payload = __import__('fc06_campaign').canonical_bytes(prereg)
    (out_dir / 'preregistration.json').write_bytes(payload)
    (out_dir / 'preregistration.sha256').write_text(
        hashlib.sha256(payload).hexdigest() + '  preregistration.json\n', encoding='ascii')
    with (out_dir / 'plan.csv').open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(plan[0]))
        writer.writeheader()
        writer.writerows(plan)
    return {'status': 'PRE_REGISTERED', 'selected': selected,
            'excluded': excluded, 'planned_arms': len(plan), 'run_dir': str(out_dir)}


def preflight_execute(run_dir):
    """A execução só é liberada após conferir TUDO, antes do 1o worker."""
    run_dir = _safe_out_dir(run_dir)
    if (run_dir / 'manifest.json').exists() or (run_dir / 'results.csv').exists():
        raise FileExistsError('FC06: campanha já iniciada ou publicada; nenhum overwrite/retry implícito')
    body = (run_dir / 'preregistration.json').read_bytes()
    sidecar = (run_dir / 'preregistration.sha256').read_text(encoding='ascii').strip()
    if sidecar != hashlib.sha256(body).hexdigest() + '  preregistration.json':
        raise ValueError('FC06: pré-registro adulterado')
    prereg = json.loads(body)
    validate_prereg(prereg)
    # Além do JSON selado, os arquivos auxiliares do pré-registro devem
    # coincidir EXATAMENTE antes do primeiro solver.
    expected_files = {'preregistration.json', 'preregistration.sha256',
                      'plan.csv', 'eligibility_report.json'}
    actual_files = {p.name for p in run_dir.iterdir() if p.is_file()}
    if actual_files != expected_files:
        raise ValueError('FC06: conteúdo inesperado/incompleto na pasta pré-registrada')
    plan_on_disk = csv_rows(run_dir / 'plan.csv')
    if len(plan_on_disk) != len(prereg['plan']) or any(
            any(str(actual.get(k)) != str(v) for k, v in frozen.items())
            for actual, frozen in zip(plan_on_disk, prereg['plan'])):
        raise ValueError('FC06: plan.csv diverge da seleção selada')
    eligibility = json.loads((run_dir / 'eligibility_report.json').read_text(encoding='utf-8'))
    if (eligibility.get('status') != 'ELIGIBLE' or
            eligibility.get('selected') != prereg['selected'] or
            eligibility.get('excluded') != prereg['excluded']):
        raise ValueError('FC06: relatório de elegibilidade foi alterado')
    from fc06_campaign import canonical_bytes
    if canonical_bytes(prereg) != body:
        raise ValueError('FC06: pré-registro não canônico')
    if prereg['machine'] != _machine():
        raise ValueError('FC06: máquina/software mudou desde o pré-registro')
    if prereg['code_files_sha256'] != source_inventory(ROOT):
        raise ValueError('FC06: código mudou desde o pré-registro')
    pilot_dir = _in_repo_dir(ROOT / prereg['pilot_run'])
    screen_dir = _in_repo_dir(ROOT / prereg['screening_run'])
    if (sha256_file(pilot_dir / 'manifest.json') != prereg['pilot_manifest_sha256'] or
            sha256_file(screen_dir / 'manifest.json') != prereg['screening_manifest_sha256'] or
            sha256_file(screen_dir / 'results.csv') != prereg['screening_results_sha256']):
        raise ValueError('FC06: fontes piloto/sondagem alteradas')
    _pilot_preflight(pilot_dir)
    _, screen_rows = _screening_preflight(screen_dir)
    main = {x.nome: x for x in fi.pool('main')}
    for e in prereg['selected']:
        if (e['instance'] not in main or
                main[e['instance']].instance_sha256 != e['instance_sha256'] or
                main[e['instance']].instance_content_sha256 != e['instance_content_sha256']):
            raise ValueError('FC06: bytes de instância divergentes')
        ok, _, evidence = __import__('fc06_campaign').pair_screening(
            screen_rows, e['instance'], e['instance_sha256'],
            justification=e.get('methodological_justification', ''),
        )
        if not ok or evidence['k_sha256'] != e['k_sha256']:
            raise ValueError('FC06: evidência de elegibilidade mudou')
    return prereg, main


def _row_from_result(inst, seed, plan_item, result, *, pair=None):
    import fc_reporting as rep
    if plan_item['modality'] == 'A':
        row = rep._lp_row(inst, result)
    else:
        row = rep._mip_row(inst, result, pair)
    # FC01 may return work=0 for an aborted worker before the solver reported
    # its Work. Preserve wall cost, but never claim measured zero solver Work.
    if result.solver_runtime_s is None:
        row['work'] = ''
    return {**row, 'formulation': plan_item['formulation'],
            'instance': inst.nome, 'seed': seed,
            'origin_graph': plan_item['origin_graph'],
            'plan_order': plan_item['order'],
            'wall_budget_s': plan_item['wall_budget_s']}


def _failure_row(plan_item, reason):
    """Nenhum bound, work ou UB de solver fictício em falhas inesperadas."""
    return {**plan_item, 'plan_order': plan_item['order'], 'status': 'WORKER_ERROR',
            'stop_reason': 'WORKER_ERROR', 'observations': reason,
            'solver_evidence': 'NOT_MEASURED', 'rational_verification': 'NOT_CERTIFIED',
            'certified_gap_status': 'INCONCLUSIVE', 'model_complete': False,
            'instance_name': plan_item['instance'], 'pair_status': 'PAIR_NOT_AVAILABLE',
            'wall_total_s': '', 'solver_runtime_s': '', 'work': '',
            'physical_feasible_ub': '', 'solver_numeric_mip_lb': '',
            'solver_numeric_mip_incumbent': ''}


def execute(run_dir, *, confirm_long_run=False, mip_runners=None, lp_runner=None,
            check_license=True):
    """Executa APENAS após preparo selado e confirmação explícita do usuário."""
    if not confirm_long_run:
        raise ValueError('FC06: exige --confirm-long-run explícito')
    prereg, main = preflight_execute(run_dir)
    run_dir = _safe_out_dir(run_dir)
    if check_license:
        from run_comparison import _check_gurobi
        ok, reason = _check_gurobi()
        if not ok:
            raise RuntimeError('FC06: Gurobi indisponível, nenhuma execução iniciada: ' + reason)
    import fc_core as core
    import fc_reporting as rep
    import fc06_reporting as campaign_report
    from fc_pairing import assess_primary_pair
    from fc_integrity import source_inventory as code_inventory

    mip_runners = mip_runners or {'comp_mip': core.run_modality_b_comp,
                                  'fcc_k': core.run_modality_b_fcc_k}
    lp_runner = lp_runner or core.run_modality_a
    plan = prereg['plan']
    cfg_base = fcfg.ExperimentConfig(**{k: v for k, v in prereg['config'].items()
                                        if k in ('threads', 'seed', 'time_limit_s',
                                                 'lp_time_limit_s', 'max_w')})
    print(f'FC-06: início explícito; {len(plan)} braços, {len(prereg["selected"])} '
          f'instâncias; teto MIP={BUDGET_MIP_S}s por braço.')
    # Log de eventos incrementais permite recuperar casos interrompidos; todos
    # os braços planejados continuam no denominador do relatório/verificador.
    result_rows = []
    events = run_dir / 'events.jsonl'
    with events.open('x', encoding='utf-8') as out:
        out.write(json.dumps({'event': 'START', 'preregistration_sha256':
                              sha256_file(run_dir / 'preregistration.json'),
                              'planned': len(plan)}) + '\n')
        out.flush()
        lp_by_instance = {}
        mip_by_group = {}
        for item in plan:
            name = item['instance']
            seed = item['seed']
            inst = main[name]
            cfg = replace(cfg_base, seed=seed)
            key = (name, seed)
            try:
                if item['modality'] == 'A':
                    if name not in lp_by_instance:
                        lp_by_instance[name] = lp_runner(inst, cfg)
                    result = lp_by_instance[name][item['formulation']]
                    row = _row_from_result(inst, seed, item, result)
                else:
                    # Accumulate 2 primary runs to assess pair once, AFTER both.
                    record = mip_by_group.setdefault(key, {})
                    record[item['formulation']] = mip_runners[item['formulation']](inst, cfg)
                    if len(record) < 2:
                        row = None  # recorded after the second arm
                    else:
                        assessment = assess_primary_pair(
                            inst, record['comp_mip'], record['fcc_k'])
                        eligible = next(e for e in prereg['selected'] if e['instance'] == name)
                        if assessment.status == 'PAIR_VALID' and assessment.k_sha256 != eligible['k_sha256']:
                            assessment = replace(assessment, status='INTEGRITY_ERROR',
                                                 reason='K diverge do pré-registro')
                        matching = [p for p in plan if p['instance'] == name and
                                    p['seed'] == seed and p['modality'] == 'B']
                        for p in matching:
                            result_rows.append(_row_from_result(
                                inst, seed, p, record[p['formulation']], pair=assessment))
                        row = None
            except Exception as exc:  # noqa: BLE001 - registrar censura, nunca inventar ótimo
                row = _failure_row(item, f'{type(exc).__name__}: {exc}')
            if row is not None:
                result_rows.append(row)
            out.write(json.dumps({'event': 'ARM_FINISHED', 'order': item['order'],
                                  'instance': name, 'seed': seed, 'formulation': item['formulation'],
                                  'status': (row or {}).get('status', 'PAIR_PENDING_OR_FINALIZED')},
                                 ensure_ascii=False) + '\n')
            out.flush()
    # Pair interrompido por erro antes de preencher os dois resultados gera
    # uma linha explícita para cada membro que não entrou nos resultados.
    seen = {(r['instance'], str(r['seed']), r['modality'], r['formulation'])
            for r in result_rows}
    for item in plan:
        key = (item['instance'], str(item['seed']), item['modality'], item['formulation'])
        if key not in seen:
            result_rows.append(_failure_row(item, 'INCOMPLETE_PRIMARY_PAIR_NOT_RECORDED'))
    result_rows.sort(key=lambda row: int(row['plan_order']))
    campaign_report.write_results(run_dir / 'results.csv', result_rows, rep.RESULTS_FIELDS)
    report = campaign_report.summary(result_rows, prereg)
    campaign_report.write_report(run_dir, report)
    # hash output only after all files published, including prereg, plan,
    # eligibility report, ledger and markdown/json report.
    if code_inventory(ROOT) != prereg['code_files_sha256']:
        raise ValueError('FC06: código alterado durante a execução; manifesto recusado')
    chosen = [main[e['instance']] for e in prereg['selected']]
    generated = sorted(p.relative_to(ROOT).as_posix() for p in run_dir.iterdir()
                       if p.is_file() and p.name not in ('manifest.json', 'manifest.sha256'))
    manifest = rep.reproducibility_manifest(
        ROOT, cfg_base, chosen, fcfg.environment_manifest(),
        ['python experiments/formulation-comparison/run_extended_comparison.py --execute '
         f'--run-dir {run_dir.relative_to(ROOT)} --confirm-long-run'],
        ['Campanha condicional; timeouts e caps preservados no denominador.',
         'LP e MIP analisados separadamente.',
         'Resultados são evidência numérica; nenhuma certificação racional foi executada.',
         'Seeds repetidas/origens compartilhadas não são observações independentes.',
         'N2 FAIL inalterado.'], generated, strict_generated=True)
    manifest.update({
        'tier': 'extended', 'fc06_schema': 'FC06-run-v1',
        'preregistration_sha256': sha256_file(run_dir / 'preregistration.json'),
        'preregistration_plan_sha256': digest(plan),
        'pilot_run': prereg['pilot_run'], 'screening_run': prereg['screening_run'],
        'seed_list': list(SEEDS), 'selected_count': len(chosen),
        'planned_arm_count': len(plan), 'reported_arm_count': len(result_rows),
        'rational_verifier_executed': False, 'superiority_claimed': False,
    })
    rep.finalize_manifest(run_dir / 'manifest.json', manifest)
    from verify_extended_campaign import verify
    verified = verify(run_dir, root=ROOT)
    print('FC-06/VERIFY:', verified['status'], verified['problems'])
    return verified


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--prepare', action='store_true')
    mode.add_argument('--execute', action='store_true')
    parser.add_argument('--run-dir', type=Path, required=True)
    parser.add_argument('--pilot-run', type=Path)
    parser.add_argument('--screening-run', type=Path)
    parser.add_argument('--instances', default='', help='nomes exatos separados por vírgula; padrão MAIN')
    parser.add_argument('--methodological-justification', default='',
                        help='exceção explícita para par já resolvido >= 30s, mínimo 80 caracteres')
    parser.add_argument('--no-lp', action='store_true')
    parser.add_argument('--threads', type=int, default=4)
    parser.add_argument('--max-w', type=int, default=200000)
    parser.add_argument('--confirm-long-run', action='store_true')
    args = parser.parse_args(argv)
    try:
        if args.prepare:
            if not args.pilot_run or not args.screening_run or args.confirm_long_run:
                parser.error('--prepare exige --pilot-run e --screening-run; não --confirm-long-run')
            outcome = prepare(
                pilot_run=args.pilot_run, screening_run=args.screening_run,
                run_dir=args.run_dir, requested=tuple(x.strip() for x in args.instances.split(',')
                                                     if x.strip()),
                justification=args.methodological_justification,
                include_lp=not args.no_lp, threads=args.threads, max_w=args.max_w,
            )
            print(json.dumps(outcome, indent=2, ensure_ascii=False))
            return 0 if outcome['status'] == 'PRE_REGISTERED' else 3
        if not args.confirm_long_run:
            parser.error('--execute exige --confirm-long-run (risco de horas de execução)')
        outcome = execute(args.run_dir, confirm_long_run=True)
        return 0 if outcome['status'] == 'PASS' else 1
    except (ValueError, FileNotFoundError, FileExistsError, RuntimeError, OSError) as exc:
        print(f'FC-06/REFUSED: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
