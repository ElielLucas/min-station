#!/usr/bin/env python3
"""AS08/T4 — piloto exploratório pareado COMP+K × B+K (LP apenas).

T2a não é modificada. Cada braço usa supervisor FC01 e paga leitura, alcance,
validação de K e solver no próprio orçamento. RMP não é tratado como LP(B).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for folder in (HERE, ROOT, ROOT/'experiments/formulation-comparison'):
    if str(folder) not in sys.path:
        sys.path.insert(0, str(folder))

from as02_model_a import Instance, compile_u
from as08_column_generation import CGConfig, SELECTIONS, run_column_generation
from as04_runner import _load_timed, _optimize
from as04_schema import SolverPolicy
from as05_diag_core import _timed_k
from fc_budget import run_bounded
import fc_instances

SCHEMA = 'AS08-B-PILOT-PLAN-v2'
# v1 (pilotos 001/002: estimativa de linhas por soma de comprimentos, seleção
# global) continua verificável, mas não executável com o código atual.
LEGACY_SCHEMAS = ('AS08-B-PILOT-PLAN-v1',)
DEFAULT_SELECTION = 'matching'
RESULT = 'AS08-B-PILOT-RESULT-v1'
REF = 'results/benchmark/as05-prospective-plan-v1.json'
ARMS = ('U_K','B_K')


def digest(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':'),
                                      ensure_ascii=False,allow_nan=False).encode()).hexdigest()


def sha(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_write(path: Path, obj):
    if path.exists():
        raise FileExistsError(f'não sobrescrever: {path}')
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2,sort_keys=True,
                               allow_nan=False)+'\n',encoding='utf-8')


def make_plan(root: Path, *, budget=300, backend='gurobi', max_iterations=100,
              max_columns=5000, max_rows=60000, rational_certificate=True,
              selection=DEFAULT_SELECTION, schema=SCHEMA):
    src=root/REF
    parent=json.loads(src.read_text(encoding='utf-8'))
    cases=parent['pilot_cases']
    if len(cases)!=6 or any(c['split']!='desenvolvimento' for c in cases):
        raise ValueError('AS08 requer exatamente as 6 instâncias de desenvolvimento AS05')
    if backend not in ('gurobi','scipy-highs') or not 1<=budget<=86400:
        raise ValueError('backend/orçamento inválido')
    if schema not in (SCHEMA,*LEGACY_SCHEMAS):
        raise ValueError('schema de plano desconhecido')
    plan = {'schema':schema,'classification':'EXPLORATORY_DEVELOPMENT_ONLY',
            'scientific_gate':'PENDING','parent_file':REF,'parent_sha256':sha(src),
            'instance_manifest_sha256':sha(root/'instances/manifest.csv'),
            'cases':[{k:c[k] for k in ('name','manifest_name','source_sha256','graph_source','raw_graph_id','split')}
                     for c in cases],
            'arms':list(ARMS),'budget_seconds_per_arm':budget,
            'solver':{'backend':backend,'threads':4,'seed':42,'mode':'LP'},
            'cg':{'iterations':max_iterations,'max_columns':max_columns,'max_rows':max_rows,
                  'per_round':200,'tolerance':1e-7,'rational_certificate':rational_certificate},
            'protocol':['LP only: no branch-and-price/MIP claims',
                        'RMP objective never reported as full-master global lower bound',
                        'Censored arm has null numerical comparison',
                        'Each arm separately prepares and validates K',
                        'Review independently before any scientific promotion']}
    if schema == SCHEMA:
        if selection not in SELECTIONS:
            raise ValueError('estratégia de seleção desconhecida')
        plan['cg']['selection'] = selection
        plan['cg_implementation'] = ('AS08-CG-v2: linhas RMP contadas exatamente (pares B3 '
                                     'distintos), pricing exato em todas as origens a cada iteração')
    return plan


def validate_plan(plan: dict, root: Path, *, allow_legacy=False):
    schema = plan.get('schema')
    if schema in LEGACY_SCHEMAS and not allow_legacy:
        raise ValueError('plano v1 só pode ser verificado; execute com um plano '+SCHEMA)
    if schema not in (SCHEMA,*LEGACY_SCHEMAS) or plan.get('parent_sha256')!=sha(root/REF) or \
       plan.get('instance_manifest_sha256')!=sha(root/'instances/manifest.csv'):
        raise ValueError('AS08 plano/fonte de referência divergiu')
    x=make_plan(root,budget=plan['budget_seconds_per_arm'],backend=plan['solver']['backend'],
                max_iterations=plan['cg']['iterations'],max_columns=plan['cg']['max_columns'],
                max_rows=plan['cg']['max_rows'],rational_certificate=plan['cg']['rational_certificate'],
                selection=plan['cg'].get('selection',DEFAULT_SELECTION),schema=schema)
    if plan!=x:
        raise ValueError('AS08 plano alterado, crie outro com novos parâmetros')
    return plan


def _worker(ctx, row:dict, root:str, arm:str, plan:dict):
    if arm not in ARMS:
        raise ValueError('braço desconhecido')
    ctx.phase('preparation')
    loaded,load_s,reach_s=_load_timed(row,root)
    if int(loaded.r)!=loaded.r:
        return {'status':'NOT_APPLICABLE','reason':'autonomia não inteira',
                'lp_numeric_value':None,'global_lower_bound':None}
    ins=Instance(tuple(loaded.V),tuple(loaded.S),tuple(loaded.T),tuple(loaded.A_r),int(loaded.r))
    ctx.phase('k_preparation')
    cuts,profile=_timed_k(ins,loaded,ctx,validator_method='bitset-v2')
    from as04_arms import k_digest
    digest_k=k_digest(ins,cuts)
    if digest_k!=profile['k_sha256']:
        raise ValueError('hash de K divergiu no perfil')
    base={'case_name':row['nome'],'instance_sha256':loaded.instance_sha256,
          'K_sha256':digest_k,'K_count':len(cuts),'k_validated':True,
          'input_load_s':load_s,'reachability_s':reach_s,
          'lp_numeric_value':None,'global_lower_bound':None}
    if arm=='U_K':
        if len(ins.V)+len(ins.A_r)>2_000_000:
            return {**base,'status':'NOT_BUILT_SIZE','reason':'COMP+K excede cap de variáveis'}
        ctx.phase('model_build')
        model=compile_u(ins,cuts,relax=True)
        ctx.phase('solve')
        if plan['solver']['backend']=='gurobi':
            policy=SolverPolicy(seed=plan['solver']['seed'], threads=plan['solver']['threads'],
                                budget_s=plan['budget_seconds_per_arm'])
            answer=_optimize(model,'LP',policy,ctx)
            return {**base,'status':answer['status'],
                    'lp_numeric_value':answer.get('lp_opt_value'),
                    'n_variables':answer['n_variables'],'n_constraints':answer['n_constraints'],
                    'solver_seconds':answer.get('solver_runtime_s')}
        from as02_solve import solve
        answer=solve(model,backend='scipy-highs',time_limit=max(.001,ctx.remaining()-1))
        return {**base,'status':'OPTIMAL_NUMERIC' if answer.status=='OPTIMAL' else answer.status,
                'lp_numeric_value':answer.objective if answer.status=='OPTIMAL' else None,
                'n_variables':len(model.variables),'n_constraints':len(model.equations)}
    ctx.progress({'schema':'AS08-CG-PROGRESS-v1','event':'INPUT_READY',
                  'K_sha256':digest_k,'instance_sha256':loaded.instance_sha256,
                  'K_count':len(cuts),'elapsed_seconds':ctx.elapsed()})
    ctx.phase('model_build')
    cfg=CGConfig(backend=plan['solver']['backend'],seconds=max(.001,ctx.remaining()-1.0),
                 iterations=plan['cg']['iterations'],max_columns=plan['cg']['max_columns'],
                 max_rows=plan['cg']['max_rows'],per_round=plan['cg']['per_round'],
                 tolerance=plan['cg']['tolerance'],selection=plan['cg']['selection'],
                 threads=plan['solver']['threads'],seed=plan['solver']['seed'],
                 rational_certificate=plan['cg']['rational_certificate'],
                 intermediate_cert_every=plan['cg'].get('intermediate_cert_every', 0),
                 intermediate_cert_budget_s=plan['cg'].get('intermediate_cert_budget_s', 15.0),
                 intermediate_cert_min_remaining_s=plan['cg'].get('intermediate_cert_min_remaining_s', 20.0),
                 intermediate_cert_max_attempts=plan['cg'].get('intermediate_cert_max_attempts', 3))
    ctx.phase('solve')
    answer=run_column_generation(ins,cuts,config=cfg,progress=ctx.progress)
    status=answer['status']
    # Somente convergência certificada pode aparecer como LP(B+K) resolvido.
    lpval=answer.get('feasible_lp_upper_bound') if status=='CONVERGED' else None
    cert=answer.get('global_lb_certificate')
    return {**base,'status':status,'lp_numeric_value':lpval,
            'global_lower_bound':answer.get('global_lower_bound'),
            'global_lb_certificate':cert,
            'cg_diagnostics':{k:answer.get(k) for k in ('schema','selection','n_iterations','columns',
                                                       'elapsed_seconds','intermediate_cert_attempts','intermediate_cert_successes','stop_detail','rmp_rows_final',
                                                       'rmp_artificial_sum','rmp_objective',
                                                       'feasible_lp_upper_bound','numeric_primal_dual_gap',
                                                       'bound_semantics')},
            'iteration_history':answer['iterations']}


def atomic_progress_write(path: Path, obj: dict) -> None:
    """Checkpoint substituível ANTES de congelar manifesto/resultado.

    Nunca atualiza arquivos de resultado final nem diretórios de outras execuções.
    A escrita por rename no mesmo filesystem evita JSON truncado por timeout.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.tmp')
    try:
        with temp.open('x', encoding='utf-8') as stream:
            json.dump(obj, stream, ensure_ascii=False, indent=2, sort_keys=True,
                      allow_nan=False)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
    finally:
        if temp.exists():
            temp.unlink()


def progress_record(plan: dict, case: dict, arm: str):
    return {'schema':'AS08-B-PILOT-PROGRESS-v1','classification':'DIAGNOSTIC_ONLY',
            'plan_sha256':digest(plan),'case':case,'arm':arm,
            'events':[],'outcome':None}


def verify_progress(record:dict, plan:dict, case:dict, arm:str) -> bool:
    if (record.get('schema')!='AS08-B-PILOT-PROGRESS-v1'
        or record.get('classification')!='DIAGNOSTIC_ONLY'
        or record.get('plan_sha256')!=digest(plan)
        or record.get('case')!=case or record.get('arm')!=arm
        or not isinstance(record.get('events'),list)):
        raise ValueError('checkpoint de progresso pertence a outro experimento')
    for item in record['events']:
        if (not isinstance(item,dict)
            or item.get('schema')!='AS08-CG-PROGRESS-v1'
            or not isinstance(item.get('event'),str)
            or not isinstance(item.get('elapsed_seconds'),(int,float))
            or not math.isfinite(item['elapsed_seconds'])
            or item['elapsed_seconds']<0):
            raise ValueError('evento de progresso inválido')
        for key in ('rmp_objective_with_artificials','certified_global_lb'):
            if key in item and item[key] is not None and not math.isfinite(item[key]):
                raise ValueError('número inválido em progresso')
    if record.get('outcome') is not None and not isinstance(record['outcome'],dict):
        raise ValueError('resultado de supervisor inválido no progresso')
    return True


def execute(plan, root:Path, output:Path, *, resume=False):
    validate_plan(plan,root)
    if output.exists() and any(output.iterdir()) and not resume:
        raise FileExistsError('saída já tem arquivos; use --resume somente com plano idêntico')
    output.mkdir(parents=True,exist_ok=True)
    plan_path=output/'plan.json'
    if not plan_path.exists():
        json_write(plan_path,plan)
    if json.loads(plan_path.read_text())!=plan:
        raise ValueError('plano da execução existente diverge')
    manifests={row['nome']:row for row in fc_instances.load_manifest(root/'instances/manifest.csv')}
    for case in plan['cases']:
        row=manifests[case['manifest_name']]
        if row['sha256']!=case['source_sha256']:
            raise ValueError('hash de entrada divergiu: '+row['nome'])
        for arm in plan['arms']:
            path=output/f"{case['name']}--{arm}.json"
            if path.exists():
                check=json.loads(path.read_text())
                if not resume or check['plan_sha256']!=digest(plan) or \
                   check['case']!=case or check['arm']!=arm:
                    raise ValueError('checkpoint inválido: '+str(path))
                print('AS08_RESUMED',case['name'],arm,check['status'])
                continue
            progress_path=output/f"{case['name']}--{arm}.cg-progress.json"
            record=progress_record(plan,case,arm) if arm=='B_K' else None
            if record is not None and progress_path.exists():
                raise FileExistsError('checkpoint de outra execução: '+str(progress_path))

            def progress_handler(event):
                if record is None:
                    return
                if not isinstance(event,dict):
                    raise ValueError('diagnóstico inválido do worker')
                record['events'].append(event)
                atomic_progress_write(progress_path,record)

            out=run_bounded(_worker,row,str(root),arm,plan,
                            budget_s=plan['budget_seconds_per_arm'],
                            on_progress=progress_handler if arm=='B_K' else None)
            if out.status=='COMPLETED':
                payload=out.value
            else:
                payload={'status':out.status,'reason':out.reason,'lp_numeric_value':None,
                         'global_lower_bound':None}
            if record is not None:
                record['outcome']={'supervisor_status':out.status,
                                   'arm_status':payload.get('status'),
                                   'wall_total_s':out.wall_total_s}
                atomic_progress_write(progress_path,record)
            data={'schema':RESULT,'plan_sha256':digest(plan),'case':case,'arm':arm,
                  'wall_total_s':out.wall_total_s,'wall_phases_s':dict(out.phase_wall_s),
                  **payload}
            if record is not None:
                data['cg_progress_checkpoint']={'file':progress_path.name,
                    'sha256':sha(progress_path),'events':len(record['events']),
                    'last_event':record['events'][-1] if record['events'] else None}
            json_write(path,data)
            print('AS08_CASE',case['name'],arm,data['status'],
                  'LP',data.get('lp_numeric_value'),'LB',data.get('global_lower_bound'),flush=True)
    # Congela fingerprints dos 12 arquivos; qualquer edição posterior falha em --verify.
    manifest={'schema':'AS08-B-PILOT-MANIFEST-v1','plan_sha256':digest(plan),
              'files':{f'{c["name"]}--{arm}.json':sha(output/f'{c["name"]}--{arm}.json')
                       for c in plan['cases'] for arm in plan['arms']}}
    checkpoints={f'{c["name"]}--B_K.cg-progress.json':sha(output/f'{c["name"]}--B_K.cg-progress.json')
                 for c in plan['cases'] if (output/f'{c["name"]}--B_K.cg-progress.json').exists()}
    if checkpoints:
        manifest['progress_files']=checkpoints
    if not (output/'manifest.json').exists():
        json_write(output/'manifest.json',manifest)
    elif json.loads((output/'manifest.json').read_text())!=manifest:
        raise ValueError('manifest anterior diverge: não sobrescrever')
    return verify(output, root)


def verify(output:Path,root:Path):
    plan=json.loads((output/'plan.json').read_text())
    validate_plan(plan,root,allow_legacy=True)
    frozen=json.loads((output/'manifest.json').read_text())
    expected_files={f'{c["name"]}--{arm}.json':sha(output/f'{c["name"]}--{arm}.json')
                    for c in plan['cases'] for arm in plan['arms']}
    expected_manifest={'schema':'AS08-B-PILOT-MANIFEST-v1',
                       'plan_sha256':digest(plan),'files':expected_files}
    if 'progress_files' in frozen:
        expected_manifest['progress_files']={
            f'{c["name"]}--B_K.cg-progress.json':
                sha(output/f'{c["name"]}--B_K.cg-progress.json')
            for c in plan['cases']
            if (output/f'{c["name"]}--B_K.cg-progress.json').exists()}
    if frozen!=expected_manifest:
        raise ValueError('manifest de integridade diverge')
    runs=[]
    for case in plan['cases']:
        for arm in plan['arms']:
            data=json.loads((output/f"{case['name']}--{arm}.json").read_text())
            if (data['schema']!=RESULT or data['plan_sha256']!=digest(plan)
                or data['case']!=case or data['arm']!=arm):
                raise ValueError('resultado corrompido/diferente: '+case['name']+arm)
            if data['status']!='CONVERGED' and arm=='B_K' and data.get('lp_numeric_value') is not None:
                raise ValueError('B censurado não pode exibir ótimo LP')
            if data['status']!='OPTIMAL_NUMERIC' and arm=='U_K' and data.get('lp_numeric_value') is not None:
                raise ValueError('U censurado não pode exibir ótimo LP')
            if ((arm=='B_K' and data['status']=='CONVERGED') or
                (arm=='U_K' and data['status']=='OPTIMAL_NUMERIC')):
                if (not data.get('k_validated') or not data.get('K_sha256') or
                    data.get('instance_sha256')!=case['source_sha256']):
                    raise ValueError('sucesso sem integridade de K/instância')
            if arm=='B_K' and 'cg_progress_checkpoint' in data:
                cp=data['cg_progress_checkpoint']
                name=f"{case['name']}--B_K.cg-progress.json"
                if cp.get('file')!=name or cp.get('sha256')!=sha(output/name):
                    raise ValueError('checkpoint CG alterado ou ausente')
                record=json.loads((output/name).read_text(encoding='utf-8'))
                verify_progress(record,plan,case,arm)
                if (cp.get('events')!=len(record['events']) or
                    cp.get('last_event')!=(record['events'][-1] if record['events'] else None) or
                    record['outcome'] is None or
                    record['outcome'].get('arm_status')!=data['status']):
                    raise ValueError('checkpoint CG diverge do resultado final')
            elif arm=='B_K' and 'progress_files' in frozen:
                raise ValueError('resultado B sem checkpoint de progresso')
            if arm=='B_K' and data.get('global_lower_bound') is not None:
                cert=data.get('global_lb_certificate') or {}
                from fractions import Fraction
                if cert.get('status')!='CERTIFIED_RATIONAL_DUAL' or \
                   abs(float(Fraction(cert['rational']))-data['global_lower_bound'])>1e-7:
                    raise ValueError('bound sem certificado racional')
                if (data.get('lp_numeric_value') is not None and
                    data['global_lower_bound']>data['lp_numeric_value']+1e-5):
                    raise ValueError('limite dual excede solução LP numericamente viável')
            runs.append(data)
    if len(runs)!=12:
        raise ValueError('comparações incompletas')
    return runs



def audit_certificates(runs:list[dict],root:Path):
    """Reexecuta K (incluindo validador bitset) e verifica dual por Fraction.

    É uma auditoria opcional potencialmente cara nas seis instâncias reais.
    Não acessa os duais calculados internamente pelo solver original.
    """
    from as08_column_generation import verify_rational_certificate
    from as04_arms import k_digest
    rows={row['nome']:row for row in fc_instances.load_manifest(root/'instances/manifest.csv')}
    checked=[]
    for record in runs:
        if record['arm']!='B_K' or record.get('global_lb_certificate') is None:
            continue
        row=rows[record['case']['manifest_name']]
        loaded=fc_instances.load_instance(row,root=root)
        if loaded.instance_sha256!=record['case']['source_sha256']:
            raise ValueError('hash físico diverge na auditoria')
        if int(loaded.r)!=loaded.r:
            raise ValueError('autonomia incompatível')
        instance=Instance(tuple(loaded.V),tuple(loaded.S),tuple(loaded.T),
                          tuple(loaded.A_r),int(loaded.r))
        cuts,profile=_timed_k(instance,loaded,validator_method='bitset-v2')
        if k_digest(instance,cuts)!=record['K_sha256']:
            raise ValueError('K mudou desde o experimento: '+record['case']['name'])
        verify_rational_certificate(instance,cuts,record['global_lb_certificate'])
        checked.append(record['case']['name'])
    return checked

def analyze(runs, output:Path):
    pairs=[]
    for i in range(0,len(runs),2):
        u,b=runs[i:i+2]
        assert u['arm']=='U_K' and b['arm']=='B_K' and u['case']==b['case']
        uv=u.get('lp_numeric_value')
        bv=b.get('lp_numeric_value')
        if (u['status']=='OPTIMAL_NUMERIC' and b['status']=='CONVERGED' and
            (u.get('K_sha256')!=b.get('K_sha256') or
             u.get('instance_sha256')!=b.get('instance_sha256'))):
            raise ValueError('pareamento invalido: K/instancia divergentes')
        comparable=(u['status']=='OPTIMAL_NUMERIC' and b['status']=='CONVERGED'
                    and uv is not None and bv is not None)
        delta=bv-uv if comparable else None
        if comparable and delta<-1e-5:
            decision='FAIL_DOMINANCE'
        elif comparable:
            decision='COMPARABLE'
        else:
            decision='CENSORED'
        checkpoint=b.get('cg_progress_checkpoint') or {}
        last_event=checkpoint.get('last_event') or {}
        stop_detail=(b.get('cg_diagnostics') or {}).get('stop_detail') or {}
        pairs.append({'case':u['case']['name'],'u_status':u['status'],'b_status':b['status'],
                      'u_lp':uv,'b_lp':bv,'b_cert_lb':b.get('global_lower_bound'),
                      'lp_gain':delta,'decision':decision,
                      'u_wall_s':u['wall_total_s'],'b_wall_s':b['wall_total_s'],
                      'b_progress_last_event':last_event.get('event'),
                      'b_progress_iteration':last_event.get('iteration'),
                      'b_progress_columns':last_event.get('columns'),
                      'b_progress_events':checkpoint.get('events'),
                      'b_stop_detail':stop_detail or None})
    qualifying=[p for p in pairs if p['decision']=='COMPARABLE' and p['u_lp']>1e-8
                and p['lp_gain']/p['u_lp']>=.01 and p['b_wall_s']<=3*p['u_wall_s']]
    qualifying_sources={next(c['case']['graph_source'] for c in runs[::2] if c['case']['name']==p['case'])
                        for p in qualifying}
    decision=('FAIL_DOMINANCE' if any(x['decision']=='FAIL_DOMINANCE' for x in pairs) else
              'INVESTIGATE_CENSORED' if any(x['decision']=='CENSORED' for x in pairs) else
              'GO_FURTHER_MIP_RESEARCH_EXPLORATORY' if len(qualifying)>=2 and len(qualifying_sources)>=2 else
              'STOP_LOW_LP_GAIN_OR_HIGH_COST_EXPLORATORY')
    result={'schema':'AS08-B-PILOT-ANALYSIS-v1','classification':'EXPLORATORY_ONLY',
            'scientific_gate':'PENDING','decision':decision,'pairs':pairs,
            'thresholds':{'lp_material_relative_min':.01,'max_wall_ratio':3.0}}
    lines=['# AS-08 — Piloto exploratório LP: COMP+K × B+K','',f'**Decisão:** `{decision}`.',
           '**Não comparar o objetivo RMP com o limite LP completo.**','',
           '| Caso | COMP+K LP | B+K LP | Ganho B | B LB racional | Status |',
           '|---|---:|---:|---:|---:|---|']
    fmt=lambda x:'—' if x is None else f'{x:.6f}'
    for p in pairs:
        lines.append(f"| {p['case']} | {fmt(p['u_lp'])} | {fmt(p['b_lp'])} | "
                     f"{fmt(p['lp_gain'])} | {fmt(p['b_cert_lb'])} | {p['decision']} |")
    lines.extend(['','## Diagnóstico de progresso B+K',
                  'O evento representa o último checkpoint persistido pelo supervisor. ',
                  'Objetivos intermediários do RMP NÃO são limites inferiores globais.',
                  '', '| Caso | Status B | Etapa/limite | Último evento | Iteração | Colunas | Eventos |',
                  '|---|---|---|---|---:|---:|---:|'])
    for p in pairs:
        sd=p['b_stop_detail'] or {}
        where=sd.get('stage','—')+(f" {sd['limit']} {sd.get('observed')}/{sd.get('configured')}"
                                   if sd.get('limit') else '')
        lines.append(f"| {p['case']} | {p['b_status']} | {where} | {p['b_progress_last_event'] or '—'} | "
                     f"{p['b_progress_iteration'] if p['b_progress_iteration'] is not None else '—'} | "
                     f"{p['b_progress_columns'] if p['b_progress_columns'] is not None else '—'} | "
                     f"{p['b_progress_events'] if p['b_progress_events'] is not None else '—'} |")
    lines.extend(['','O pilot é desenvolvimento exploratório, sem autorização de promoção científica.',
                  'Branch-and-price não foi implementado; nenhum resultado MIP para B é alegado.'])
    json_write(output/'analysis.json',result)
    if (output/'analysis.md').exists():
        raise FileExistsError('relatório já existe')
    (output/'analysis.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    return result


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    cmds=parser.add_mutually_exclusive_group(required=True)
    for flag in ('init-plan','check-plan','execute','verify','analyze'):
        cmds.add_argument('--'+flag,action='store_true')
    parser.add_argument('--plan',default='results/benchmark/as08-b-pilot-plan-v2.json')
    parser.add_argument('--output-dir',default='results/benchmark/as08-b-pilot-003')
    parser.add_argument('--budget',type=int,default=300)
    parser.add_argument('--backend',choices=('gurobi','scipy-highs'),default='gurobi')
    parser.add_argument('--max-iterations',type=int,default=100)
    parser.add_argument('--max-columns',type=int,default=5000)
    parser.add_argument('--max-rows',type=int,default=60000)
    parser.add_argument('--selection',choices=SELECTIONS,default=DEFAULT_SELECTION)
    parser.add_argument('--resume',action='store_true')
    parser.add_argument('--audit-dual',action='store_true',help='Reconstruir K e verificar duals racionais (pode ser demorado)')
    a=parser.parse_args(argv)
    root=ROOT
    p=root/a.plan
    out=root/a.output_dir
    if a.init_plan:
        item=make_plan(root,budget=a.budget,backend=a.backend,
                       max_iterations=a.max_iterations,max_columns=a.max_columns,
                       max_rows=a.max_rows,selection=a.selection)
        json_write(p,item)
        print('AS08_PLAN_CREATED',len(item['cases']),'cases / 12 arms',digest(item))
        return 0
    plan=json.loads(p.read_text(encoding='utf-8'))
    validate_plan(plan,root,allow_legacy=not a.execute)
    if a.check_plan:
        print('AS08_PLAN_VALID',digest(plan));return 0
    if a.execute:
        runs=execute(plan,root,out,resume=a.resume)
        print('AS08_PILOT_COMPLETED',len(runs),'arms');return 0
    runs=verify(out,root)
    if a.verify:
        if a.audit_dual:
            checked=audit_certificates(runs,root)
            print('AS08_RATIONAL_DUAL_AUDITED',len(checked),'cases')
        print('AS08_PILOT_VERIFIED',len(runs),'arms');return 0
    report=analyze(runs,out)
    print('AS08_ANALYSIS_WRITTEN',report['decision'],out/'analysis.md')
    return 0


if __name__=='__main__':
    raise SystemExit(main())
