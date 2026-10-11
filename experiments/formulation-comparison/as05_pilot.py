"""AS-05: executor autorizado, preservando 6x3 braços e relatórios AS-04."""
from __future__ import annotations

import csv
import json
from pathlib import Path

from as04_reporting import publish_run, verify_run
from as04_runner import run_case, run_arm
from as04_schema import SolverPolicy, ArmResult, SCHEMA
from as05_gate import a4_selection, assess_gate, metrics_for_case, assess_reproduction
from as05_protocol import MAIN, plan_digest, read_plan, sha256_file
from fc_instances import load_manifest
from as04_compare import compare_case
from dataclasses import asdict


def verify_preconditions(evidence: dict) -> None:
    """Dados de auditoria externa são necessários; não implica revisão independente por si."""
    from as02_validation_gate import GateEvidence, assess
    if not isinstance(evidence, dict) or evidence.get('as04_verdict') != 'PASS':
        raise RuntimeError('AS05_BLOCKED: AS04 não homologada')
    data = evidence.get('as02_evidence')
    if not isinstance(data, dict) or assess(GateEvidence(**data)) != 'PASS':
        raise RuntimeError('AS05_BLOCKED: AS01/AS02 sem revisão independente')
    reviewers = evidence.get('reviewers')
    if not isinstance(reviewers, dict):
        raise RuntimeError('AS05_BLOCKED: trilha de revisores ausente')
    for feature in ('as01','as02','as04'):
        entry = reviewers.get(feature)
        if not isinstance(entry, dict) or not all(isinstance(entry.get(x), str) and entry[x].strip()
                                                  for x in ('author','reviewer','evidence_path')):
            raise RuntimeError(f'AS05_BLOCKED: evidência de autoria/revisão {feature} ausente')
        if entry['author'] == entry['reviewer']:
            raise RuntimeError(f'AS05_BLOCKED: revisor não independente {feature}')
    # O revisor deverá conferir as provas e os caminhos indicados fora da máquina.


def _manifest_index(root: Path, plan: dict) -> dict:
    rows = load_manifest(root/'instances/manifest.csv')
    index = {r['nome']:r for r in rows}
    if len(index) != len(rows):
        raise ValueError('AS05: manifesto contém nomes duplicados')
    for case in plan['pilot_cases']:
        if case['manifest_name'] not in index:
            raise ValueError('AS05: caso não encontrado no manifesto')
        row = index[case['manifest_name']]
        if row['caminho'] != case['source_file'] or row.get('particao') != 'desenvolvimento':
            raise ValueError('AS05: manifesto divergiu do pré-registro')
        if sha256_file(root / row['caminho']) != case['source_sha256']:
            raise ValueError('AS05: bytes da instância divergem do AS00')
    return index


def _policy(plan: dict, seed: int | None = None) -> SolverPolicy:
    p = plan['policy']
    return SolverPolicy(seed=p['seed'] if seed is None else seed, threads=p['threads'],
                        budget_s=p['wall_budget_s_per_arm'],
                        memory_limit_bytes=p['memory_limit_bytes'])


def _safe_case_runner(callable_, row: dict, arm_ids: tuple[str, ...], **kw) -> dict:
    """Retém todos os braços sob erro operacional inesperado do runner.

    AS04 já transforma timeouts em observações censuradas. Esta última barreira
    impede uma exceção isolada de desaparecer do denominador.
    """
    try:
        return callable_(row, arm_ids=arm_ids, **kw)
    except Exception as exc:
        pol = kw['policy']
        records = [ArmResult(case_name=row['nome'], arm_id=arm, mode='LP',
                             status='WORKER_ERROR', reason=f'{type(exc).__name__}: {exc}',
                             instance_sha256=None, structural_sha256=None,
                             reference_k_sha256=None, applied_k_sha256=None,
                             k_validated=False, solver_policy_sha256=pol.sha256,
                             solver_policy=asdict(pol)) for arm in arm_ids]
        return {'schema':SCHEMA, 'case_name':row['nome'], 'mode':'LP',
                'policy_sha256':pol.sha256,'arms':[r.to_dict() for r in records],
                'comparison':compare_case(records)}


def run_pilot(*, root: Path, plan_path: Path, evidence_path: Path, output_dir: Path,
              max_variables: int=1_000_000, run_case_fn=run_case, run_arm_fn=run_arm) -> Path:
    plan, _ = read_plan(plan_path, root)
    evidence = json.loads(evidence_path.read_text(encoding='utf-8'))
    verify_preconditions(evidence)
    if output_dir.exists():
        raise FileExistsError('AS05: destino append-only já existe')
    manifest = _manifest_index(root, plan)
    policy = _policy(plan)
    from as02_validation_gate import GateEvidence
    gate = GateEvidence(**evidence['as02_evidence'])
    case_results = []
    metrics = []
    selected_a4 = []
    repeated_results = []
    for case in plan['pilot_cases']:
        row = manifest[case['manifest_name']]
        result = _safe_case_runner(run_case_fn, row, arm_ids=MAIN, root=root, mode='LP', policy=policy,
                             as02_gate=gate, max_variables=max_variables,
                             grouping_seed=plan['policy']['grouping_seed'])
        metric = metrics_for_case(case, result, plan['materiality_addendum'])
        take_a4, reason = a4_selection(case, metric, plan)
        if metric['material_a_gain'] and metric['wall_acceptable']:
            repeated = []
            for seed in plan['policy']['reproducibility_seeds'][1:]:
                repeat = _safe_case_runner(run_case_fn, row, arm_ids=('U_K','A2_K'), root=root, mode='LP',
                                     policy=_policy(plan, seed), as02_gate=gate,
                                     max_variables=max_variables,
                                     grouping_seed=plan['policy']['grouping_seed'])
                repeated.append(repeat)
                repeated_results.append((case['name'],seed,repeat))
            metric['reproduction'] = assess_reproduction(
                case, result, repeated, plan['materiality_addendum'],
                plan['policy']['reproducibility_seeds'])
        metric['a4_triggered'] = take_a4
        metric['a4_not_selected_reason'] = None if take_a4 else reason
        case_results.append(result)
        metrics.append(metric)
        if take_a4:
            extra = run_arm_fn(row, root=root, arm_id='A4_K', mode='LP', policy=policy,
                               as02_gate=gate, allow_a4=True, max_variables=max_variables,
                               grouping_seed=plan['policy']['grouping_seed'])
            selected_a4.append({'name':case['name'], 'trigger':reason, 'arm':extra.to_dict()})
    gate_decision = assess_gate(metrics, plan)
    report = {'schema':'AS05-PILOT-v1', 'plan_sha256':plan_digest(plan),
              'plan_file_sha256':sha256_file(plan_path),
              'as00_sha256':plan['basis_protocol_sha256'],
              'manifest_sha256':plan['basis_manifest_sha256'],
              'precondition_evidence_sha256':sha256_file(evidence_path),
              'cases':metrics,'decision':gate_decision,
              'a4_optional':selected_a4,
              'auxiliary_controls':{'CORE_IP':'NOT_IMPLEMENTED_IN_AS04',
                                    'FCC_K_SMALL':'NOT_RUN_SEPARATE_COMPLETE_ONLY'},
              'comparison_scope':'DEVELOPMENT_ONLY',
              'limitations':['LP numerico não é certificado racional',
                             'A4 é condicional e não integra contraste obrigatório',
                             'CORE_IP e F-CC completa exigem adaptador/evidência próprios']}
    # Persistência pós-coleta, sem sobrescrita e com hashes; output criado somente após execução.
    output_dir.mkdir(parents=True, exist_ok=False)
    paths = []
    for result, case in zip(case_results, plan['pilot_cases']):
        case_dir = output_dir / 'cases' / case['name']
        publish_run(result, case_dir, expected_arms=MAIN)
        verify_run(case_dir)
        paths.extend(case_dir/name for name in ('comparison.json','arms.csv','pairs.csv','manifest.json'))
    for name, seed, result in repeated_results:
        replay_path = output_dir / 'reproducibility' / name / f'seed-{seed}'
        publish_run(result, replay_path, expected_arms=('U_K','A2_K'))
        verify_run(replay_path)
        paths.extend(replay_path/filename for filename in ('comparison.json','arms.csv','pairs.csv','manifest.json'))
    summary_path = output_dir / 'lp_summary.csv'
    summary_fields = ('case_name','graph_source','raw_graph_id','U_status','U_K_status',
                      'A2_K_status','k_delta','a_delta','a_relative_gain',
                      'a_wall_ratio','material_a_gain','reproduction_status',
                      'a4_triggered','a4_not_selected_reason')
    with summary_path.open('w',encoding='utf-8',newline='') as out:
        writer = csv.DictWriter(out,fieldnames=summary_fields)
        writer.writeheader()
        for metric in metrics:
            kv = metric['contrasts']['K_EFFECT']
            av = metric['contrasts']['A_EFFECT']
            writer.writerow({'case_name':metric['name'],'graph_source':metric['graph_source'],
                             'raw_graph_id':metric['raw_graph_id'],
                             **{f'{arm}_status':metric['arm_statuses'][arm] for arm in MAIN},
                             'k_delta':kv['absolute'],'a_delta':av['absolute'],
                             'a_relative_gain':av['relative'],'a_wall_ratio':av['wall_ratio'],
                             'material_a_gain':metric['material_a_gain'],
                             'reproduction_status':metric['reproduction']['status'],
                             'a4_triggered':metric['a4_triggered'],
                             'a4_not_selected_reason':metric['a4_not_selected_reason']})
    paths.append(summary_path)
    report_path = output_dir/'lp_gate.json'
    (output_dir/'plan.json').write_bytes(plan_path.read_bytes())
    paths.append(output_dir/'plan.json')
    report_path.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True,
                                      allow_nan=False, indent=2)+'\n',encoding='utf-8')
    paths.append(report_path)
    if selected_a4:
        extras = output_dir/'a4_optional.json'
        extras.write_text(json.dumps(selected_a4, ensure_ascii=False, sort_keys=True,
                                    allow_nan=False, indent=2)+'\n',encoding='utf-8')
        paths.append(extras)
    inventory = {p.relative_to(output_dir).as_posix():sha256_file(p) for p in paths}
    (output_dir/'manifest.json').write_text(json.dumps({'schema':'AS05-INTEGRITY-v1',
                                                        'files':inventory},
                                                       sort_keys=True,indent=2)+'\n',encoding='utf-8')
    return report_path


def verify_pilot(path: Path) -> dict:
    manifest = json.loads((path/'manifest.json').read_text(encoding='utf-8'))
    if manifest.get('schema') != 'AS05-INTEGRITY-v1':
        raise ValueError('AS05: manifesto inválido')
    for name, expected in manifest['files'].items():
        file_path = path/name
        if not file_path.is_file() or sha256_file(file_path) != expected:
            raise ValueError(f'AS05: integridade falhou: {name}')
    report = json.loads((path/'lp_gate.json').read_text(encoding='utf-8'))
    if sha256_file(path/'plan.json') != report['plan_file_sha256']:
        raise ValueError('AS05: plano congelado diverge do relatório')
    if len(report['cases']) != 6 or report['decision']['denominator_cases'] != 6:
        raise ValueError('AS05: denominador incorreto')
    for case in report['cases']:
        verify_run(path/'cases'/case['name'])
    return report
