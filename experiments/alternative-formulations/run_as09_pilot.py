#!/usr/bin/env python3
"""AS09/T3 paired LP pilot for C vs COMP, with/without identical K.

Exploratory only: solver is Gurobi; independent mathematical proof review is
separate. Each arm is isolated by FC's absolute wall-clock supervisor.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import resource
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
for folder in (HERE,ROOT,ROOT/'experiments/formulation-comparison'):
    if str(folder) not in sys.path:
        sys.path.insert(0,str(folder))

from as02_model_a import Instance,compile_u
from as09_model_c import compile_c,dimension_estimate,prepare_physical_graph
from as04_runner import _load_timed,_optimize
from as04_schema import SolverPolicy
from as05_diag_core import _timed_k
from fc_budget import run_bounded
import fc_instances

SCHEMA='AS09-C-LP-PILOT-v1'
RESULT='AS09-C-LP-RESULT-v1'
ARMS=('U','C','U_K','C_K')
CASES=('vienna-I056-regiao-f4','mapf-den312d-m50-f2-rho','puc-cc9-2p-seed-r1')


def digest(data):
    return hashlib.sha256(json.dumps(data,sort_keys=True,ensure_ascii=False,
                                     separators=(',',':'),allow_nan=False).encode()).hexdigest()


def sha(path:Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_once(path:Path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8') as f:
        json.dump(data,f,sort_keys=True,ensure_ascii=False,indent=2,allow_nan=False)
        f.write('\n')


def _cases(root):
    rows=fc_instances.load_manifest(root/'instances/manifest.csv')
    out=[]
    for case in CASES:
        matches=[r for r in rows if Path(r['nome']).stem==case]
        if len(matches)!=1:
            raise ValueError(f'Caso do piloto ausente/duplicado: {case}')
        row=matches[0]
        if row.get('classe')!='principal' or float(row['r'])!=int(float(row['r'])) or \
           float(row['peso_min'])!=1 or float(row['peso_max'])!=1:
            raise ValueError('Instância não elegível para AS09 unitária: '+case)
        out.append({'case':case,'manifest_name':row['nome'],
                    'source_sha256':row['sha256'], 'source':row.get('fonte','')})
    return out


def make_plan(root:Path, *, budget=300, max_variables=500_000,
              max_constraints=250_000, threads=4):
    if not 30<=budget<=86400 or not 10_000<=max_variables<=10_000_000 or \
       not 10_000<=max_constraints<=10_000_000 or not 1<=threads<=32:
        raise ValueError('Parâmetros do piloto fora da faixa permitida')
    return {'schema':SCHEMA,'classification':'EXPLORATORY_NOT_HOMOLOGATED',
            'manifest_sha256':sha(root/'instances/manifest.csv'),
            'implementation_sha256':{str(p.relative_to(root)):sha(p) for p in (
                root/'experiments/alternative-formulations/as09_model_c.py',
                root/'experiments/alternative-formulations/as02_model_a.py',
                root/'experiments/formulation-comparison/as04_runner.py',
                root/'experiments/formulation-comparison/as05_diag_core.py',
            )},
            'cases':_cases(root),'arms':list(ARMS),
            'solver':{'backend':'gurobi','mode':'LP','threads':threads,'seed':42},
            'budget_seconds_per_arm':int(budget),
            'caps':{'max_variables':int(max_variables),'max_constraints':int(max_constraints)},
            'math_gate':'PROOF_REVIEW_REQUIRED',
            'gate_rule':{'lp_abs_tolerance':1e-5,'minimum_c_speedup_pct':20.0,
                         'two_dense_graph_sources_required':True},
            'protocol':['Same G, r, A_r, S, T and source bytes per pair',
                        'Both with-K arms regenerate and independently validate identical K',
                        'Time includes source read, A_r generation, K, model build and solution',
                        'U and C without K have no K construction',
                        'No MIP comparison and no implied LP proof without independent review',
                        'Censored LP objectives remain null and results append-only']}


def validate_plan(plan,root):
    if plan.get('schema')!=SCHEMA:
        raise ValueError('Esquema do plano desconhecido')
    exp=make_plan(root,budget=plan['budget_seconds_per_arm'],
                  max_variables=plan['caps']['max_variables'],
                  max_constraints=plan['caps']['max_constraints'],
                  threads=plan['solver']['threads'])
    if plan!=exp:
        raise ValueError('Plano/fonte foi alterado: faça outro plano')
    return plan


def _worker(ctx,row,root:str,arm:str,plan):
    ctx.phase('preparation')
    loaded,load_s,reach_s=_load_timed(row,root)
    if float(loaded.r)!=int(float(loaded.r)):
        return {'status':'NOT_APPLICABLE_NONINTEGER_R','lp_numeric_value':None}
    inst=Instance(tuple(loaded.V),tuple(loaded.S),tuple(loaded.T),
                  tuple(loaded.A_r),int(loaded.r))
    base={'instance_sha256':loaded.instance_sha256,
          'input_load_s':load_s,'reachability_s':reach_s,
          'lp_numeric_value':None,'K_sha256':None,'K_count':0,'K_validated':False,
          'peak_rss_kb':None,'solver_runtime_s':None}
    cuts=()
    if arm.endswith('_K'):
        ctx.phase('k_preparation')
        cuts,profile=_timed_k(inst,loaded,ctx,validator_method='bitset-v2')
        base.update({'K_sha256':profile['k_sha256'],'K_count':len(cuts),
                     'K_validated':profile['k_validated'],
                     'k_phase_wall_s':profile['phase_wall_s']})
    graph=None
    if arm.startswith('C'):
        ctx.phase('physical_validation')
        graph=prepare_physical_graph(inst,loaded.adj)
        estimated=dimension_estimate(inst,graph,len(cuts))
    else:
        estimated={'n_variables':len(inst.V)+len(inst.A_r),
                   'n_constraints':3*len(inst.V)+len(cuts)}
    base['estimated_size']=estimated
    if estimated['n_variables']>plan['caps']['max_variables'] or \
       estimated['n_constraints']>plan['caps']['max_constraints']:
        return {**base,'status':'NOT_BUILT_SIZE','reason':'cap de tamanho antes da montagem',
                'size_cap':plan['caps']}
    ctx.phase('model_build')
    compiled=(compile_c(inst,loaded.adj,cuts,relax=True,physical_graph=graph)
              if graph is not None else compile_u(inst,cuts,relax=True))
    # _optimize faz a montagem efetiva no Gurobi e marca a fase solve.
    pol=SolverPolicy(seed=plan['solver']['seed'],threads=plan['solver']['threads'],
                     budget_s=plan['budget_seconds_per_arm'])
    result=_optimize(compiled,'LP',pol,ctx)
    return {**base,'status':result['status'],
            'lp_numeric_value':result.get('lp_opt_value') if result['status']=='OPTIMAL_NUMERIC' else None,
            'solver_runtime_s':result['solver_runtime_s'],
            'solver_version':result.get('solver_version'),
            'n_variables':result['n_variables'],'n_constraints':result['n_constraints'],
            'n_nonzeros':result['n_nonzeros'],
            'peak_rss_kb':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'model_complete':True}


def execute(plan,root,out,*,resume=False):
    validate_plan(plan,root)
    if out.exists() and any(out.iterdir()) and not resume:
        raise FileExistsError('Diretório de resultados já contém arquivos; escolha um novo')
    out.mkdir(parents=True,exist_ok=True)
    if not (out/'plan.json').exists():
        write_once(out/'plan.json',plan)
    elif json.loads((out/'plan.json').read_text(encoding='utf8'))!=plan:
        raise ValueError('Plano não coincide com a execução existente')
    lookup={r['nome']:r for r in fc_instances.load_manifest(root/'instances/manifest.csv')}
    for case in plan['cases']:
        row=lookup[case['manifest_name']]
        if row['sha256']!=case['source_sha256']:
            raise ValueError('Identidade da instância mudou: '+case['case'])
        for arm in plan['arms']:
            fp=out/f'{case["case"]}--{arm}.json'
            if fp.exists():
                old=json.loads(fp.read_text())
                if not resume or old['plan_sha256']!=digest(plan) or \
                   old['case']!=case or old['arm']!=arm:
                    raise ValueError('Resultado já existente e incompatível')
                print('AS09_RESUMED',case['case'],arm,old['status'],flush=True)
                continue
            outcome=run_bounded(_worker,row,str(root),arm,plan,
                                budget_s=plan['budget_seconds_per_arm'])
            payload=(outcome.value if outcome.status=='COMPLETED' else
                     {'status':outcome.status,'reason':outcome.reason,'lp_numeric_value':None,
                      'model_complete':False})
            data={'schema':RESULT,'plan_sha256':digest(plan),'case':case,'arm':arm,
                  'wall_total_s':outcome.wall_total_s,
                  'wall_phases_s':dict(outcome.phase_wall_s),**payload}
            if data['status']!='OPTIMAL_NUMERIC':
                data['lp_numeric_value']=None
            write_once(fp,data)
            print('AS09_CASE',case['case'],arm,data['status'],
                  'LP',data['lp_numeric_value'],'WALL',round(outcome.wall_total_s,3),flush=True)
    files={f'{c["case"]}--{arm}.json':sha(out/f'{c["case"]}--{arm}.json')
           for c in plan['cases'] for arm in plan['arms']}
    manifest={'schema':'AS09-C-LP-MANIFEST-v1','plan_sha256':digest(plan),'files':files}
    if not (out/'manifest.json').exists():
        write_once(out/'manifest.json',manifest)
    elif json.loads((out/'manifest.json').read_text())!=manifest:
        raise ValueError('Manifest de integridade existente diverge')
    return verify(out,root)


def verify(out,root):
    plan=json.loads((out/'plan.json').read_text())
    validate_plan(plan,root)
    frozen=json.loads((out/'manifest.json').read_text())
    exp={f'{c["case"]}--{a}.json':sha(out/f'{c["case"]}--{a}.json')
         for c in plan['cases'] for a in plan['arms']}
    if frozen!={'schema':'AS09-C-LP-MANIFEST-v1','plan_sha256':digest(plan),'files':exp}:
        raise ValueError('Arquivos/manifest alterados')
    data={}
    for c in plan['cases']:
        for a in plan['arms']:
            res=json.loads((out/f'{c["case"]}--{a}.json').read_text())
            if res['schema']!=RESULT or res['case']!=c or res['arm']!=a or \
               res['plan_sha256']!=digest(plan):
                raise ValueError('Proveniência inconsistente')
            if res['status']!='OPTIMAL_NUMERIC' and res.get('lp_numeric_value') is not None:
                raise ValueError('Resultado censurado publica LP espúrio')
            if res['status']=='OPTIMAL_NUMERIC':
                if res.get('instance_sha256')!=c['source_sha256'] or not res.get('model_complete'):
                    raise ValueError('LP ótimo sem identidade ou modelo completo')
                if a.endswith('_K') and (not res.get('K_validated') or not res.get('K_sha256')):
                    raise ValueError('LP com K sem validação')
                if not isinstance(res['lp_numeric_value'],(int,float)) or \
                   not math.isfinite(res['lp_numeric_value']):
                    raise ValueError('LP não finito')
            data[c['case'],a]=res
        pairU,pairC=data[c['case'],'U_K'],data[c['case'],'C_K']
        if pairU.get('K_sha256') and pairC.get('K_sha256') and \
           pairU['K_sha256']!=pairC['K_sha256']:
            raise ValueError('K diferente entre modelos pareados')
    return data


def analyze(out,root):
    data=verify(out,root)
    cases=CASES
    rows=[]
    for case in cases:
        for suffix in ('','_K'):
            u,c=data[case,'U'+suffix],data[case,'C'+suffix]
            equal=None
            if u['status']=='OPTIMAL_NUMERIC' and c['status']=='OPTIMAL_NUMERIC':
                equal=abs(u['lp_numeric_value']-c['lp_numeric_value'])<=1e-5
            rows.append({'case':case,'K':bool(suffix),'status_U':u['status'],'status_C':c['status'],
                         'LP_U':u.get('lp_numeric_value'),'LP_C':c.get('lp_numeric_value'),
                         'LP_equal_numeric':equal,
                         'nvars_U':u.get('n_variables'),'nvars_C':c.get('n_variables'),
                         'ncons_U':u.get('n_constraints'),'ncons_C':c.get('n_constraints'),
                         'nnz_U':u.get('n_nonzeros'),'nnz_C':c.get('n_nonzeros'),
                         'rss_peak_U_kb':u.get('peak_rss_kb'),'rss_peak_C_kb':c.get('peak_rss_kb'),
                         'wall_U_s':u['wall_total_s'],'wall_C_s':c['wall_total_s']})
    if any(r['LP_equal_numeric'] is False for r in rows):
        gate='BLOCK_LP_DISAGREEMENT_INVESTIGATE'
    elif any(r['LP_equal_numeric'] is None for r in rows):
        gate='INVESTIGATE_CENSORED'
    else:
        # Mathematical proof review is external, regardless of performance.
        dense=[r for r in rows if r['K'] and r['case'] in CASES[:2]]
        if all(r['wall_C_s']<.8*r['wall_U_s'] and r['rss_peak_C_kb']<=r['rss_peak_U_kb']
               for r in dense):
            gate='PROMISING_EXPLORATORY_PROOF_REVIEW_PENDING'
        else:
            gate='NO_MATERIAL_FULL_PIPELINE_ADVANTAGE'
    output={'schema':'AS09-C-LP-ANALYSIS-v1','plan_sha256':digest(json.loads((out/'plan.json').read_text())),
            'classification':'EXPLORATORY','decision':gate,'math_gate':'PROOF_REVIEW_REQUIRED',
            'rows':rows}
    write_once(out/'analysis.json',output)
    md=['# AS09 — Comparação LP COMP × C', '',f'**Decisão exploratória:** `{gate}`.',
        '', '**Equivalência matemática:** revisão independente pendente. LPs são numéricos (Gurobi).',
        '', '| Caso | K | COMP LP | C LP | Equiv. numérica | U vars | C vars | U wall(s) | C wall(s) |',
        '|---|---|---:|---:|---|---:|---:|---:|---:|']
    for r in rows:
        def f(x):return '—' if x is None else f'{x:.5f}' if isinstance(x,float) else str(x)
        md.append(f"| {r['case']} | {'sim' if r['K'] else 'não'} | {f(r['LP_U'])} | {f(r['LP_C'])} | "
                  f"{r['LP_equal_numeric']} | {f(r['nvars_U'])} | {f(r['nvars_C'])} | "
                  f"{f(r['wall_U_s'])} | {f(r['wall_C_s'])} |")
    md+=['','O tempo wall inclui leitura, preparação de A_r, K nos braços com cortes, construção e solução.',
         'Não inferir equivalência LP em caso de censura ou apenas por concordância numérica.', '']
    with (out/'analysis.md').open('x',encoding='utf8') as f:f.write('\n'.join(md))
    return gate


def main(argv=None):
    p=argparse.ArgumentParser(description='AS09 C versus COMP: piloto LP pareado, sem promoção')
    action=p.add_mutually_exclusive_group(required=True)
    for name in ('init-plan','check-plan','execute','verify','analyze'):
        action.add_argument('--'+name,action='store_true')
    p.add_argument('--plan',type=Path,required=True)
    p.add_argument('--output-dir',type=Path)
    p.add_argument('--budget',type=int,default=300)
    p.add_argument('--max-variables',type=int,default=500000)
    p.add_argument('--max-constraints',type=int,default=250000)
    p.add_argument('--threads',type=int,default=4)
    p.add_argument('--resume',action='store_true')
    a=p.parse_args(argv)
    if a.init_plan:
        write_once(a.plan,make_plan(ROOT,budget=a.budget,max_variables=a.max_variables,
                                    max_constraints=a.max_constraints,threads=a.threads))
        print('AS09_PLAN_CREATED',digest(json.loads(a.plan.read_text())))
        return 0
    plan=json.loads(a.plan.read_text(encoding='utf8'))
    validate_plan(plan,ROOT)
    if a.check_plan:
        print('AS09_PLAN_VALID',digest(plan));return 0
    if a.output_dir is None:
        p.error('--output-dir é obrigatório')
    if a.execute:
        data=execute(plan,ROOT,a.output_dir,resume=a.resume)
        print('AS09_PILOT_COMPLETED',len(data),'arms');return 0
    if a.verify:
        data=verify(a.output_dir,ROOT)
        print('AS09_PILOT_VERIFIED',len(data),'arms');return 0
    if a.analyze:
        decision=analyze(a.output_dir,ROOT)
        print('AS09_ANALYSIS_WRITTEN',decision,a.output_dir/'analysis.md');return 0
    return 1

if __name__=='__main__':
    raise SystemExit(main())
