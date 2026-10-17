#!/usr/bin/env python3
"""AS25: preregistered paired LP FC-R pilot (development only, NO MIP).

Examples:
  poetry run python experiments/cuts/run_fcr_lp_as25.py --output-dir results/benchmark/as25-fcr-lp-001
  poetry run python experiments/cuts/run_fcr_lp_as25.py --output-dir /tmp/as25-dry --dry-run
  poetry run python experiments/cuts/run_fcr_lp_as25.py --output-dir results/benchmark/as25-fcr-ablation-001 --ablation

All arms have independent child processes and a 90-second total wall budget.
The optional ablation is a separate, preregistered campaign; it NEVER enters
AS25's main gate. Outputs are append-only and must use a new directory.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import multiprocessing as mp
from pathlib import Path
import resource
import subprocess
import sys
import time
import traceback

HERE=Path(__file__).resolve().parent
if str(HERE) not in sys.path:sys.path.insert(0,str(HERE))
from run_h2_lp import (ROOT, Instance, compile_u, prepare_K, canonical_k,
                       k_digest, load_instance, load_plan as load_as16_plan,
                       validate_sources, sha256_file, _solver, _optimize,
                       _phase, _ensure_budget, _elapsed, _remaining,
                       get_commit, write_json_new)
from experiments.cuts.fcr_lp_policy import IndexedFCR

SCHEMA='AS25-FCR-LP-v1'
PLAN_FILE=ROOT/'docs/technical/plans/execucao/as25-preregistro-fcr-lp.json'
PRIMARY_ARMS=('U','U_K','U_FCR','U_K_FCR')
ABLATION_ARMS=('U_K_FCR_SINGLETON','U_K_FCR_HEURISTIC')
CHECKED_SOURCES=(
    'experiments/cuts/fcr_rows.py','experiments/cuts/fcr_regions.py',
    'experiments/cuts/fcr_separator.py','experiments/cuts/fcr_lp_policy.py',
    'experiments/cuts/run_fcr_lp_as25.py','experiments/cuts/analyze_fcr_lp_as25.py',
    'specs/as-24-fcr-separador-micro/validation.md',
)


def load_plan(path=PLAN_FILE, *, as16_path=None, root=ROOT):
    planpath=Path(path)
    plan=json.loads(planpath.read_text(encoding='utf-8'))
    base, base_sha=load_as16_plan(as16_path) if as16_path else load_as16_plan()
    if plan.get('schema_version')!='AS25-FCR-PLAN-v1' or plan.get('stage')!='AS25':
        raise ValueError('INVALID_INPUT: AS25 plan schema')
    if plan.get('as16_plan_sha256')!=base_sha or plan.get('cases')!=base['cases']:
        raise ValueError('INVALID_INPUT: development identities/hashes differ from AS16')
    if plan.get('solver_parameters')!=base['solver_parameters'] or plan.get('budget')!={'wall_seconds_per_arm':90}:
        raise ValueError('INVALID_INPUT: Gurobi parameters or total wall budget altered')
    if tuple(plan.get('primary_arms',()))!=PRIMARY_ARMS or tuple(plan.get('ablation_arms',()))!=ABLATION_ARMS:
        raise ValueError('INVALID_INPUT: arm order altered')
    if plan.get('fcr')!={'max_variables':1000000,'max_larger':12,'max_rounds':6,
        'max_cuts_per_round':32,'max_cuts_total':128,'min_violation':1e-6,
        'max_separation_wall_s':12,'min_reopt_remaining_s':2}:
        raise ValueError('INVALID_INPUT: FC-R policy altered')
    if plan.get('gate')!={'minimum_relative_gain':0.01,'minimum_independent_raw_graphs':2,
        'maximum_cost_multiple':2.0,'require_full_six_cases':True,
        'no_mip_authorization':True,'human_review_required':True}:
        raise ValueError('INVALID_INPUT: scientific gate changed')
    if not plan.get('preregistered_before_real_lp') or plan.get('ablation')!='SEPARATE_RUN_NOT_IN_PRIMARY_GATE':
        raise ValueError('INVALID_INPUT: preregistration/ablation changed')
    if plan.get('constraints')!=['only development','no MIP','no evaluation','no change COMP or K','append only']:
        raise ValueError('INVALID_INPUT: research boundaries changed')
    validation=(root/'specs/as-24-fcr-separador-micro/validation.md').read_text(encoding='utf-8')
    if ('VALIDATED_WITH_MINOR_FINDINGS' not in validation or
            '**Result:** **PASS**' not in validation or 'Claude' not in validation):
        raise ValueError('BLOCKED: AS24 independent-review gate not documented as PASS')
    return plan,sha256_file(planpath),base


def _source_dirty(root):
    """Whether tracked AS25/AS24 code differs from HEAD; None if no .git."""
    result=subprocess.run(['git','status','--porcelain','--untracked-files=normal',
                           '--',*CHECKED_SOURCES],cwd=root,text=True,capture_output=True,check=False)
    return bool(result.stdout.strip()) if result.returncode==0 else None


def _usage_mb():
    # Linux ru_maxrss is KiB, observational peak for current subprocess.
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024.0


def _point(model, compiled, initial_y):
    variables=model.getVars()
    f={}
    for key,index in compiled.columns.items():
        if key[0]=='F':
            value=float(variables[index].X)
            if not math.isfinite(value) or value < -1e-6:
                raise ValueError('INVALID_LP_POINT: nonfinite/negative flow')
            if value>1e-10:f[key[1],key[2]]=max(value,0.)
    return initial_y,f


def _add_fcr(model,compiled,columns,gp,row):
    # Reconstruct exactly from canonical AS24 row, no approximate row templates.
    expr=gp.quicksum(coef*columns[compiled.columns[key]] for key,coef in row.terms)
    if row.rhs<=0 or row.demand!=row.rhs:
        raise ValueError('INVALID_INPUT: invalid FC-R certificate')
    return model.addConstr(expr>=row.rhs,name='AS25-FCR['+hashlib.sha256(repr(row.signature).encode()).hexdigest()[:16]+']')


def _work_arm(case,row,root,arm,policy,configuration,deadline):
    if arm not in PRIMARY_ARMS+ABLATION_ARMS:raise ValueError('INVALID_INPUT: arm')
    timings={}
    _ensure_budget(deadline)
    loaded=_phase(timings,'load_and_reachability_s',lambda:load_instance(row,root=root))
    if loaded.instance_sha256!=case['source_sha256'] or int(loaded.r)!=loaded.r or loaded.r<1:
        raise ValueError('INVALID_INPUT: source hash/autonomy')
    if any(w!=1 for nbr in loaded.adj.values() for _,w in nbr):
        raise ValueError('INVALID_INPUT: nonunit physical graph')
    ins=Instance(tuple(loaded.V),tuple(loaded.S),tuple(loaded.T),tuple(loaded.A_r),int(loaded.r))
    K=_phase(timings,'k_preparation_s',lambda:canonical_k(ins,prepare_K(ins,loaded.adj,ins.r)))
    has_k=arm in ('U_K','U_K_FCR') or arm.startswith('U_K_FCR_')
    has_fcr=arm in ('U_FCR','U_K_FCR') or arm.startswith('U_K_FCR_')
    include_larger=arm not in ('U_K_FCR_SINGLETON',)
    _ensure_budget(deadline)
    compiled=_phase(timings,'model_construction_s',lambda:compile_u(ins,K if has_k else (),relax=True))
    record={'status':'NOT_RUN','timings':timings,'n_variables':len(compiled.variables),
            'n_constraints_initial':len(compiled.equations),'applied_k_count':len(K) if has_k else 0,
            'prepared_k_count':len(K),'k_sha256':k_digest(ins,K),
            'lp_objective':None,'base_lp_objective':None,'fcr_added':0,'fcr_violated':0,
            'fcr_duplicates':0,'fcr_candidates':0,'fcr_nnz':0,'fcr_rounds':[],
            'fcr_cut_cap_encountered':False,'fcr_total_cut_cap_reached':False,
            'singleton_complete_all_scans':None,'selected_heuristic_complete_all_scans':None,
            'coverage_note':'No FC-R scan performed', 'peak_rss_mb':_usage_mb()}
    if len(compiled.variables)>configuration['max_variables']:
        record.update(status='NOT_MEASURED_CAP',reason='variable limit',peak_rss_mb=_usage_mb())
        return record
    _ensure_budget(deadline)
    model,ycols,gp=_phase(timings,'gurobi_build_s',lambda:_solver(compiled,policy,deadline))
    record.update(n_nonzeros_initial=int(model.NumNZs),peak_rss_mb=_usage_mb())
    first=_phase(timings,'lp_base_optimize_s',lambda:_optimize(model,gp,deadline,ycols))
    record.update(status=first['status'],lp_objective=first['lp_objective'],
                  base_lp_objective=first['lp_objective'],
                  solver_base={k:v for k,v in first.items() if k!='y_star'},
                  time_to_first_lp_s=sum(timings.values()))
    if first['status']!='OPTIMAL' or not has_fcr:return record
    index=_phase(timings,'fcr_region_index_s',lambda:IndexedFCR(
        ins,max_larger=configuration['max_larger'],include_larger=include_larger))
    columns=model.getVars()
    seen=set()
    row_count=0
    current=first
    scan_statuses=[]
    for iteration in range(configuration['max_rounds']):
        if _remaining(deadline)<configuration['min_reopt_remaining_s']:
            record.update(status='TIME_LIMIT',lp_objective=None,
                          reason='insufficient wall budget to complete FC-R reoptimization')
            break
        _ensure_budget(deadline)
        y,f=_phase(timings,'lp_point_extraction_s',lambda:_point(model,compiled,current['y_star']))
        remaining=configuration['max_cuts_total']-row_count
        if remaining<=0:break
        sep_budget=min(configuration['max_separation_wall_s'],max(0,_remaining(deadline)-configuration['min_reopt_remaining_s']))
        report=_phase(timings,'fcr_separation_s',lambda:index.separate(
            y,f,tolerance=configuration['min_violation'],max_cuts=min(remaining,configuration['max_cuts_per_round']),
            time_limit_s=sep_budget,exclude_signatures=seen))
        stats=report['stats']
        record['fcr_candidates']+=stats['examined']
        record['fcr_violated']+=stats['violated']
        record['fcr_duplicates']+=stats['duplicates']
        if stats['capped']>0:record['fcr_cut_cap_encountered']=True
        scan_statuses.append((stats['singleton_complete'],stats['larger_complete_selected']))
        summary={'round':iteration+1,'status':report['status'],'stats':stats,
                 'emitted_cuts':[cut.algebraic_certificate for cut in report['cuts']],
                 'events':report['events']}
        record['fcr_rounds'].append(summary)
        for cut in report['cuts']:
            _ensure_budget(deadline)
            _add_fcr(model,compiled,columns,gp,cut)
            seen.add(cut.signature)
            record['fcr_nnz']+=len(cut.terms)
            row_count+=1
        record['fcr_added']=row_count
        if not report['cuts']:break
        model.update()
        if _remaining(deadline)<configuration['min_reopt_remaining_s']:
            record.update(status='TIME_LIMIT',lp_objective=None,
                          reason='insufficient wall budget after separation')
            break
        current=_phase(timings,'lp_reoptimization_s',lambda:_optimize(model,gp,deadline,ycols))
        record.update(status=current['status'],lp_objective=current['lp_objective'],
                      solver_final={k:v for k,v in current.items() if k!='y_star'},
                      n_constraints_final=int(model.NumConstrs),n_nonzeros_final=int(model.NumNZs))
        if current['status']!='OPTIMAL':break
        if current['lp_objective']+1e-5<first['lp_objective']:
            record.update(status='ERROR',lp_objective=None,reason='LP objective decreased after valid FC-R')
            break
    record['fcr_total_cut_cap_reached']=row_count>=configuration['max_cuts_total']
    record['singleton_complete_all_scans']=all(p[0] for p in scan_statuses) if scan_statuses else False
    record['selected_heuristic_complete_all_scans']=all(p[1] for p in scan_statuses) if scan_statuses else False
    record['coverage_note']='Complete only over eligible singleton regions and selected larger regions; not globally over all L'
    record['peak_rss_mb']=_usage_mb()
    return record


def _worker(conn,case,row,root,arm,policy,config,deadline):
    try:
        data=_work_arm(case,row,root,arm,policy,config,deadline)
    except MemoryError:
        data={'status':'NOT_MEASURED_MEMORY'}
    except TimeoutError:
        data={'status':'TIME_LIMIT','reason':'deadline during preparation/solver'}
    except (ModuleNotFoundError,ImportError) as exc:
        data={'status':'ERROR','reason':f'dependency unavailable: {exc}'}
    except Exception as exc:
        data={'status':'ERROR','reason':f'{type(exc).__name__}: {exc}',
              'traceback':traceback.format_exc(limit=4)}
    try:conn.send(data)
    finally:conn.close()


def run_arm(case,row,root,arm,plan):
    start=time.monotonic()
    deadline=start+plan['budget']['wall_seconds_per_arm']
    ctx=mp.get_context('spawn')
    receiver,sender=ctx.Pipe(duplex=False)
    child=ctx.Process(target=_worker,args=(sender,case,row,root,arm,
                                          plan['solver_parameters'],plan['fcr'],deadline))
    child.start()
    sender.close()
    try:
        if receiver.poll(_remaining(deadline)):
            try:data=receiver.recv()
            except EOFError:data={'status':'ERROR','reason':'worker exited without data'}
        else:data={'status':'TIME_LIMIT','reason':'hard 90s wall deadline; worker terminated'}
    finally:
        if child.is_alive():child.terminate()
        child.join(timeout=2)
        if child.is_alive():child.kill();child.join(timeout=1)
        receiver.close()
    return {'schema_version':SCHEMA,'stage':'AS25','name':case['name'],
            'source_file':case['path'],'instance_sha256':case['source_sha256'],
            'raw_graph_id':case['raw_graph_id'],'arm_id':arm,
            'elapsed_wall_s':_elapsed(start),'budget_s':plan['budget']['wall_seconds_per_arm'],**data}


def execute(plan,plan_sha,source,root,out,names,*,dry_run=False,ablation=False):
    rows_by_name=validate_sources(source,root)
    selection=[c for c in plan['cases'] if c['name'] in names]
    if not selection or len(selection)!=len(names):
        raise ValueError('INVALID_INPUT: unknown or duplicated case, development only')
    if not dry_run and importlib.util.find_spec('gurobipy') is None:
        raise RuntimeError('Gurobi unavailable; use --dry-run to verify protocol')
    if out.exists():raise FileExistsError('append-only output exists: '+str(out))
    out.parent.mkdir(parents=True,exist_ok=True)
    out.mkdir(exist_ok=False)
    arms=ABLATION_ARMS if ablation else PRIMARY_ARMS
    manifest={'schema_version':SCHEMA,'stage':'AS25','mode':'DRY_RUN' if dry_run else 'LP',
              'campaign':'ABLATION' if ablation else 'PRIMARY',
              'plan_sha256':plan_sha,'as16_plan_sha256':plan['as16_plan_sha256'],
              'source_commit':get_commit(),'source_has_tracked_modifications':_source_dirty(root),
              'code_sha256':{
                  rel:sha256_file(root/rel) for rel in CHECKED_SOURCES},
              'cases':[c['name'] for c in selection],
              'raw_graph_ids':[c['raw_graph_id'] for c in selection],
              'arms':list(arms),'budget':plan['budget'],
              'fcr':plan['fcr'],'solver_parameters':plan['solver_parameters'],
              'gurobi_available':importlib.util.find_spec('gurobipy') is not None,
              'scope':'development only; LP only; ABLATION separate; no MIP'}
    write_json_new(out/'manifest.json',manifest)
    rows=[]
    for c in selection:
        for arm in arms:
            res=({'schema_version':SCHEMA,'stage':'AS25','name':c['name'],
                  'raw_graph_id':c['raw_graph_id'],'instance_sha256':c['source_sha256'],
                  'arm_id':arm,'status':'NOT_RUN','budget_s':90,'elapsed_wall_s':0.,
                  'reason':'DRY_RUN does not solve LP'} if dry_run else
                  run_arm(c,rows_by_name[c['name']],root,arm,plan))
            rows.append(res)
    write_json_new(out/'rows.json',rows)
    from analyze_fcr_lp_as25 import analyze
    result=analyze(plan,manifest,rows)
    write_json_new(out/'analysis.json',result)
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan',type=Path,default=PLAN_FILE)
    parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--cases',nargs='+',default=None,
                        help='development subset for smoke test; cannot support complete GO')
    parser.add_argument('--dry-run',action='store_true')
    parser.add_argument('--ablation',action='store_true',help='separate singleton-vs-heuristic run')
    args=parser.parse_args()
    plan,sha,as16=load_plan(args.plan)
    names=set(args.cases) if args.cases is not None else {c['name'] for c in plan['cases']}
    if args.cases is not None and len(names)!=len(args.cases):raise ValueError('duplicate case name')
    analysis=execute(plan,sha,as16,ROOT,args.output_dir,names,dry_run=args.dry_run,ablation=args.ablation)
    print(json.dumps({'status':analysis['gate'],'cases':len(names),'rows':analysis['arm_rows'],
                      'campaign':'ABLATION' if args.ablation else 'PRIMARY',
                      'output_dir':str(args.output_dir)},ensure_ascii=False))


if __name__=='__main__':main()
