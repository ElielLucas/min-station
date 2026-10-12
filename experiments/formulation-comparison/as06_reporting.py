"""AS06: comparação pareada, verificação de evidência e gate exploratório.

Nenhuma ausência de UB/dual bound é convertida em zero; os 6 casos entram no
mesmo denominador, mesmo com timeouts, falta de licença ou falha de validação.
"""
from __future__ import annotations

import csv
import io
import json
import math
from pathlib import Path

from as06_mip import (ANALYSIS, MANIFEST, RESULT, CENSORS, PRIMARY, SECONDARY,
                      expected_slots, load_rows, validate_plan)
from as04_schema import digest
from as05_diag_core import _read_or_run_checkpoint, _checkpoint_name, _write_json
from as05_protocol import sha256_file

SUCCESS = frozenset(('OPTIMAL_NUMERIC', 'TIME_LIMIT', 'NO_INCUMBENT', 'INFEASIBLE'))
MEASURABLE = frozenset(('OPTIMAL_NUMERIC', 'TIME_LIMIT'))
HEADERS = ('case','source','raw_graph_id','seed','arm','status','numeric_lb','numeric_ub',
           'physical_ub','validated_gap','wall_s','solver_s','first_valid_ub_solver_s',
           'best_valid_ub_solver_s','nodes','work','variables','constraints','k_sha256')


def finite(x):
    return type(x) in (float,int) and math.isfinite(x)


def validate_run(run: dict, case: dict, *, arm: str, seed: int, plan: dict):
    if (run.get('case_name') != case['manifest_name'] or run.get('arm_id') != arm or
            run.get('seed') != seed or run.get('status') not in SUCCESS | CENSORS):
        raise ValueError('AS06: braço/caso/seed/status incompatível')
    if (run.get('solver_policy') != {**plan['solver'], 'seed': seed} or
            run.get('solver_policy_sha256') != digest({**plan['solver'], 'seed': seed})):
        raise ValueError('AS06: política solver divergente')
    if not finite(run.get('wall_total_s')) or run['wall_total_s'] < 0:
        raise ValueError('AS06: wall time inválido')
    if arm == 'U' and (run.get('k_prepared_for_this_arm') or run.get('reference_k_sha256') or
                       run.get('applied_k_sha256') or run.get('n_k_cuts')):
        raise ValueError('AS06: COMP não pode pagar/aplicar K')
    if run['status'] in SUCCESS:
        if not run.get('model_complete'):
            raise ValueError('AS06: solve com modelo incompleto')
        if run.get('instance_sha256') != case['source_sha256']:
            raise ValueError('AS06: fingerprint da origem diverge')
        if arm != 'U' and (not run.get('reference_k_sha256') or
                           run.get('reference_k_sha256') != run.get('applied_k_sha256')):
            raise ValueError('AS06: K não validado/identificado')
        if arm == SECONDARY and (not run.get('partition_sha256') or
                                  not run.get('a4_parent_sha256')):
            raise ValueError('AS06: A4 sem partição aninhada')
    else:
        if any(run.get(k) is not None for k in ('mip_numeric_bound','mip_numeric_incumbent',
                   'physical_validated_ub','validated_mip_gap')):
            raise ValueError('AS06: censura não pode publicar bounds')
    bound, numeric_ub = run.get('mip_numeric_bound'), run.get('mip_numeric_incumbent')
    ub, gap, installed = run.get('physical_validated_ub'),run.get('validated_mip_gap'),run.get('installed')
    if bound is not None and not finite(bound):
        raise ValueError('AS06: LB não finito')
    if numeric_ub is not None and not finite(numeric_ub):
        raise ValueError('AS06: incumbente não finito')
    if ub is not None:
        if (type(ub) is not int or ub < 0 or run['status'] not in MEASURABLE or
                type(installed) not in (tuple,list) or len(installed) != len(set(installed)) or
                len(installed) != ub or numeric_ub is None or abs(ub-numeric_ub)>1e-4):
            raise ValueError('AS06: UB física sem atestado coerente')
        if bound is not None and (bound > ub+1e-3 or gap is None or
                abs(gap-max(0., (ub-bound)/max(1., abs(ub))))>1e-7):
            raise ValueError('AS06: gap e limites incoerentes')
    elif gap is not None or installed is not None:
        raise ValueError('AS06: UB ausente não pode produzir gap/instalação')
    if run['status'] in ('NO_INCUMBENT','INFEASIBLE') and numeric_ub is not None:
        raise ValueError('AS06: status sem incumbente contraditório')
    if run.get('numeric_callback_dropped_incumbents',0) < 0:
        raise ValueError('AS06: drop contador negativo')
    for event in run.get('numeric_bound_trace',[]):
        if not finite(event.get('solver_s')) or event['solver_s'] < 0:
            raise ValueError('AS06: callback time inválido')
        for key in ('numeric_lb','numeric_incumbent'):
            if event.get(key) is not None and not finite(event[key]):
                raise ValueError('AS06: curva numérica inválida')
    for event in run.get('physical_trace',[]):
        if event.get('validation') not in ('VALIDATED','REJECTED'):
            raise ValueError('AS06: validação de evento desconhecida')
        if event.get('validation') == 'REJECTED' and event.get('physical_ub') is not None:
            raise ValueError('AS06: evento inválido gerou UB')
    expected = plan['k_policy']['expected_previous_hashes'].get(case['name'])
    if expected and arm != 'U' and run.get('reference_k_sha256') is not None and run['reference_k_sha256'] != expected:
        raise ValueError('AS06: SHA de K diferente do validador v2')


def verify_case(case: dict, expected_case: dict, plan: dict):
    if case.get('name') != expected_case['name'] or len(case.get('seeds',[])) != len(plan['seeds']):
        raise ValueError('AS06: caso ou seeds omitidos')
    for srow, seed in zip(case['seeds'], plan['seeds']):
        if srow.get('seed') != seed or [r.get('arm_id') for r in srow['runs']] != expected_case['arms']:
            raise ValueError('AS06: slots/ordem divergente')
        for run, arm in zip(srow['runs'], expected_case['arms']):
            validate_run(run, expected_case, arm=arm, seed=seed, plan=plan)
        ks = {r['reference_k_sha256'] for r in srow['runs'] if r['arm_id'] != 'U' and r['status'] in SUCCESS}
        if len(ks) > 1:
            raise ValueError('AS06: K divergente entre braços')
        pair = srow['runs'][:2]
        if any(r['arm_id'] != a for r,a in zip(pair, PRIMARY)):
            raise ValueError('AS06: par primário omitido')


def rows_csv(report: dict) -> str:
    out = io.StringIO(newline='')
    w=csv.DictWriter(out, fieldnames=HEADERS, lineterminator='\n')
    w.writeheader()
    info = {c['name']:c for c in report['plan_cases']}
    for case in report['cases']:
        c=info[case['name']]
        for seeded in case['seeds']:
            for r in seeded['runs']:
                w.writerow({'case': case['name'], 'source':c['graph_source'],
                  'raw_graph_id':c['raw_graph_id'], 'seed':seeded['seed'],
                  'arm':r['arm_id'], 'status':r['status'],
                  'numeric_lb':r.get('mip_numeric_bound'),
                  'numeric_ub':r.get('mip_numeric_incumbent'),
                  'physical_ub':r.get('physical_validated_ub'),
                  'validated_gap':r.get('validated_mip_gap'),
                  'wall_s':r['wall_total_s'], 'solver_s':r.get('solver_runtime_s'),
                  'first_valid_ub_solver_s':r.get('time_to_first_validated_ub_solver_s'),
                  'best_valid_ub_solver_s':r.get('time_to_best_validated_ub_solver_s'),
                  'nodes':r.get('nodes'), 'work':r.get('solver_work'),
                  'variables':r.get('n_variables'), 'constraints':r.get('n_constraints'),
                  'k_sha256':r.get('reference_k_sha256')})
    return out.getvalue()


def run_campaign(*, root: Path, plan_path: Path, output_dir: Path, resume=False, runner=None):
    from as06_mip import run_arm
    runner = runner or run_arm
    root=root.resolve()
    plan=validate_plan(json.loads(plan_path.read_text(encoding='utf-8')),root)
    if output_dir.exists():
        if not resume or (output_dir/'report.json').exists():
            raise FileExistsError('AS06: saída existente; resultado é append-only')
        if sha256_file(output_dir/'plan.json') != sha256_file(plan_path):
            raise ValueError('AS06: plano incompatível com checkpoints')
    else:
        if resume:
            raise FileNotFoundError('AS06: --resume exige diretório parcial')
        output_dir.mkdir(parents=True)
        (output_dir/'plan.json').write_bytes(plan_path.read_bytes())
    rows=load_rows(root,plan)
    data=[]
    for c in plan['cases']:
        seeds=[]
        for seed in plan['seeds']:
            runs=[]
            for ix,arm in enumerate(c['arms']):
                # Um slot único por par case/seed/arm, evita colisão ao retomar.
                slot=plan['seeds'].index(seed)*3+ix
                job=('as06-mip-v1',plan['stage'],arm,seed,sha256_file(plan_path))
                def perform(arm=arm,seed=seed,c=c):
                    run=runner(rows[c['name']], root=root, plan=plan, arm=arm, seed=seed)
                    return {**run, 'solver_policy':{**plan['solver'],'seed':seed},
                            'solver_policy_sha256':digest({**plan['solver'],'seed':seed})}
                record=_read_or_run_checkpoint(output_dir,c['name'],slot,job,perform,resume=resume)
                runs.append(record)
            seeds.append({'seed':seed,'runs':runs})
        item={'name':c['name'],'seeds':seeds}
        verify_case(item,c,plan)
        data.append(item)
    report={'schema':RESULT,'stage':plan['stage'],'classification':plan['classification'],
            'scientific_gate':'PENDING','scientific_promotion':'NOT_AUTHORIZED',
            'plan_sha256':sha256_file(plan_path), 'plan_cases':plan['cases'],
            'expected_slots':len(expected_slots(plan)), 'cases':data}
    _write_json(output_dir/'report.json',report)
    (output_dir/'arms.csv').write_text(rows_csv(report),encoding='utf-8')
    paths=[output_dir/p for p in ('plan.json','report.json','arms.csv')]
    paths+=sorted(p for p in (output_dir/'checkpoints').rglob('*') if p.is_file())
    _write_json(output_dir/'manifest.json',{'schema':MANIFEST,
                'files':{p.relative_to(output_dir).as_posix():sha256_file(p) for p in paths}})
    return output_dir/'report.json'


def verify_campaign(folder: Path, *, root: Path | None = None, audit_physical=False):
    plan=json.loads((folder/'plan.json').read_text(encoding='utf-8'))
    if root is not None:
        validate_plan(plan,root)
    report=json.loads((folder/'report.json').read_text(encoding='utf-8'))
    manifest=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
    if (report.get('schema')!=RESULT or report.get('stage')!=plan.get('stage') or
        report.get('plan_sha256')!=sha256_file(folder/'plan.json') or
        report.get('plan_cases')!=plan['cases'] or report.get('expected_slots')!=len(expected_slots(plan)) or
        report.get('classification')!=plan['classification'] or
        report.get('scientific_gate')!='PENDING' or
        report.get('scientific_promotion')!='NOT_AUTHORIZED' or len(report.get('cases',[]))!=len(plan['cases'])):
        raise ValueError('AS06: relatório incompatível com plano')
    if (folder/'arms.csv').read_text(encoding='utf-8') != rows_csv(report):
        raise ValueError('AS06: CSV não corresponde ao relatório')
    expected={'plan.json','report.json','arms.csv'}
    for case, expected_case in zip(report['cases'],plan['cases']):
        verify_case(case,expected_case,plan)
        for seeded in case['seeds']:
            for ix,r in enumerate(seeded['runs']):
                slot=plan['seeds'].index(seeded['seed'])*3+ix
                rel=_checkpoint_name(case['name'],slot)
                p=folder/rel
                side=p.with_suffix('.sha256')
                expected.add(rel)
                expected.add(side.relative_to(folder).as_posix())
                if not p.is_file() or not side.is_file() or sha256_file(p)!=side.read_text(encoding='ascii').strip():
                    raise ValueError('AS06: checkpoint sem integridade')
                obj=json.loads(p.read_text(encoding='utf-8'))
                if obj!={'case':case['name'],'index':slot,
                         'job':['as06-mip-v1',plan['stage'],r['arm_id'],seeded['seed'],sha256_file(folder/'plan.json')],
                         'result':r}:
                    raise ValueError('AS06: divergência de checkpoint')
    if manifest.get('schema')!=MANIFEST or set(manifest.get('files',{}))!=expected:
        raise ValueError('AS06: manifesto incompleto ou com arquivos extras')
    for rel, hash_ in manifest['files'].items():
        p=Path(rel)
        if p.is_absolute() or '..' in p.parts or not (folder/p).is_file() or sha256_file(folder/p)!=hash_:
            raise ValueError('AS06: hash divergente em evidência')
    if audit_physical:
        if root is None:
            raise ValueError('AS06: auditoria física exige --root')
        import fc_instances
        rows=load_rows(root,plan)
        for item in report['cases']:
            loaded=fc_instances.load_instance(rows[item['name']],root=root)
            from as04_runner import validate_physical_ub
            for seeded in item['seeds']:
                for r in seeded['runs']:
                    ub=r.get('physical_validated_ub')
                    if ub is not None and validate_physical_ub(loaded,tuple(r['installed']))!=ub:
                        raise ValueError('AS06: auditoria física independente recusou UB')
    return report


def pair_result(u: dict, uk: dict, rule: dict):
    """Gap calculado SOMENTE com UB física validada + bound numérico."""
    if any(r.get('status') not in MEASURABLE or not finite(r.get('validated_mip_gap'))
           for r in (u,uk)):
        return {'status':'NOT_COMPARABLE','reason':f'{u["status"]} vs {uk["status"]}',
                'gap_U':u.get('validated_mip_gap'),'gap_U_K':uk.get('validated_mip_gap'),
                'absolute_gap_gain':None,'relative_gap_reduction':None,'material':False,'severe_regression':False}
    g0,g1=u['validated_mip_gap'],uk['validated_mip_gap']
    gain=g0-g1
    reduction=(gain/g0 if g0>1e-9 else None)
    material=(gain>=rule['absolute_gap_gain_min']-1e-9 or
              (reduction is not None and reduction>=rule['relative_gap_reduction_min']-1e-9 and gain>1e-9))
    return {'status':'MATCHED','gap_U':g0,'gap_U_K':g1,
            'absolute_gap_gain':gain,'relative_gap_reduction':reduction,'material':material,
            'severe_regression':g1-g0>rule['severe_gap_regression_max']+1e-9}


def stage_gate(plan: dict, pairs: list[dict]):
    # Gate de promoção exploratória para replicar; NÃO é homologação científica.
    if any(p['result']['status']!='MATCHED' for p in pairs):
        return 'INCONCLUSIVE_CENSORED'
    if any(p['result']['severe_regression'] for p in pairs):
        return 'STOP_SEVERE_REGRESSION'
    by_case={}
    for p in pairs:
        by_case.setdefault(p['case'],[]).append(p)
    positive=[]
    for group in by_case.values():
        if len(group)==len(plan['seeds']) and sum(p['result']['material'] for p in group)>= (
                1 if plan['stage']=='screening' else 2):
            positive.append(group[0])
    if (len({p['graph_source'] for p in positive})>=plan['advance_gate']['minimum_graph_sources'] and
        len({p['raw_graph_id'] for p in positive})>=plan['advance_gate']['minimum_raw_graphs']):
        return 'GO_REPLICATION_EXPLORATORY' if plan['stage']=='screening' else 'REPLICATION_SIGNAL_EXPLORATORY'
    return 'STOP_NO_REPRODUCIBLE_MULTIFAMILY_BENEFIT'


def analyze_campaign(folder: Path, outdir: Path, *, root: Path | None = None):
    report=verify_campaign(folder,root=root)
    plan=json.loads((folder/'plan.json').read_text(encoding='utf-8'))
    if outdir.exists():
        raise FileExistsError('AS06: análise já existe, não sobrescrever')
    pairs=[]
    for case,p in zip(report['cases'],plan['cases']):
        for seeded in case['seeds']:
            a,b=seeded['runs'][:2]
            result=pair_result(a,b,plan['advance_gate'])
            pairs.append({'case':case['name'],'graph_source':p['graph_source'],
                          'raw_graph_id':p['raw_graph_id'],'seed':seeded['seed'],
                          'result':result, 'U_status':a['status'],'U_K_status':b['status'],
                          'U_wall_s':a['wall_total_s'],'U_K_wall_s':b['wall_total_s'],
                          'U_physical_ub':a.get('physical_validated_ub'),
                          'U_K_physical_ub':b.get('physical_validated_ub'),
                          'U_LB':a.get('mip_numeric_bound'),
                          'U_K_LB':b.get('mip_numeric_bound'),
                          'U_first_validated_s':a.get('time_to_first_validated_ub_solver_s'),
                          'U_K_first_validated_s':b.get('time_to_first_validated_ub_solver_s')})
    decision=stage_gate(plan,pairs)
    analysis={'schema':ANALYSIS,'stage':plan['stage'],
              'classification':'EXPLORATORY_DEVELOPMENT_ONLY',
              'scientific_gate':'PENDING','scientific_promotion':'NOT_AUTHORIZED',
              'parent_report_sha256':sha256_file(folder/'report.json'),
              'parent_manifest_sha256':sha256_file(folder/'manifest.json'),
              'decision':decision,'pairs':pairs,
              'n_cases':len(report['cases']),'n_slots':report['expected_slots'],
              'n_comparable':sum(p['result']['status']=='MATCHED' for p in pairs),
              'n_material':sum(p['result']['material'] for p in pairs),
              'n_censored':sum(p['result']['status']!='MATCHED' for p in pairs),
              'limitations':['Gap MIP numérico usa melhor LB do Gurobi e UB fisicamente validada',
                             'MIPGap não equivale a gap de integralidade com ótimo desconhecido',
                             'Tempo até incumbente validado é relógio do solver, não wall total',
                             'Ausência de evento validado NÃO é interpolada',
                             'Somente desenvolvimento; decisão não promove AS08/AS11']}
    outdir.mkdir(parents=True)
    _write_json(outdir/'analysis.json',analysis)
    lines=['# AS-06 — piloto MIP pareado', '',
           '**Classificação:** exploratória, sem homologação independente.',
           f'**Etapa:** `{plan["stage"]}` · **Decisão:** `{decision}`', '',
           f'Pares comparáveis: {analysis["n_comparable"]}/{len(pairs)}; '
           f'materiais: {analysis["n_material"]}; não comparáveis: {analysis["n_censored"]}.','',
           '| Caso | Seed | COMP gap | COMP+K gap | Δ gap | Estado |',
           '|---|---:|---:|---:|---:|---|']
    fmt=lambda x: f'{x:.4%}' if x is not None else '—'
    for p in pairs:
        r=p['result'];lines.append(f'| {p["case"]} | {p["seed"]} | '
            f'{fmt(r["gap_U"])} | {fmt(r["gap_U_K"])} | '
            f'{fmt(r["absolute_gap_gain"])} | {r["status"]} |')
    lines+=['','## Limitações','']+['- '+x for x in analysis['limitations']]
    (outdir/'analysis.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    _write_json(outdir/'manifest.json',{'schema':'AS06-ANALYSIS-MANIFEST-v1',
        'files':{name:sha256_file(outdir/name) for name in ('analysis.json','analysis.md')}})
    return outdir/'analysis.md'


def verify_analysis(folder: Path, *, expected_stage: str | None = None):
    from as06_mip import make_plan
    analysis=json.loads((folder/'analysis.json').read_text(encoding='utf-8'))
    manifest=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
    if analysis.get('schema')!=ANALYSIS or (expected_stage and analysis.get('stage')!=expected_stage):
        raise ValueError('AS06: análise inválida')
    if manifest.get('schema')!='AS06-ANALYSIS-MANIFEST-v1' or set(manifest.get('files',{}))!={'analysis.json','analysis.md'}:
        raise ValueError('AS06: manifesto de análise inválido')
    for n,h in manifest['files'].items():
        if sha256_file(folder/n)!=h:
            raise ValueError('AS06: análise adulterada')
    campaign=folder.parent
    report=verify_campaign(campaign)
    plan=json.loads((campaign/'plan.json').read_text(encoding='utf-8'))
    if (analysis['parent_report_sha256']!=sha256_file(campaign/'report.json') or
        analysis['parent_manifest_sha256']!=sha256_file(campaign/'manifest.json') or
        analysis['stage']!=plan['stage']):
        raise ValueError('AS06: relatório de origem da análise divergente')
    expected=[]
    for case,pc in zip(report['cases'],plan['cases']):
        for seeded in case['seeds']:
            a,b=seeded['runs'][:2]
            expected.append({'case':case['name'],'graph_source':pc['graph_source'],
                             'raw_graph_id':pc['raw_graph_id'],'seed':seeded['seed'],
                             'result':pair_result(a,b,plan['advance_gate']),
                             'U_status':a['status'],'U_K_status':b['status'],
                             'U_wall_s':a['wall_total_s'],'U_K_wall_s':b['wall_total_s'],
                             'U_physical_ub':a.get('physical_validated_ub'),
                             'U_K_physical_ub':b.get('physical_validated_ub'),
                             'U_LB':a.get('mip_numeric_bound'),
                             'U_K_LB':b.get('mip_numeric_bound'),
                             'U_first_validated_s':a.get('time_to_first_validated_ub_solver_s'),
                             'U_K_first_validated_s':b.get('time_to_first_validated_ub_solver_s')})
    if (analysis['pairs']!=expected or analysis['decision']!=stage_gate(plan,expected) or
        analysis['n_slots']!=report['expected_slots']):
        raise ValueError('AS06: decisão analítica não reproduz os braços')
    return analysis
