#!/usr/bin/env python3
"""AS25 conservative four-arm LP analysis (no automatic MIP authorization).

Pairs must be OPTIMAL on both arms; all other statuses remain censored.
The standalone ablation never contributes to the primary scientific gate.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path

SCHEMA='AS25-FCR-ANALYSIS-v1'


def _optimal(row):
    value=row.get('lp_objective')
    return (row.get('status')=='OPTIMAL' and isinstance(value,(int,float))
            and math.isfinite(value) and value>=-1e-8)


def _pair(left,right):
    if not _optimal(left) or not _optimal(right):
        return {'paired_optimal':False,'reason':f"{left.get('status','MISSING')} / {right.get('status','MISSING')}",
                'absolute_gain':None,'relative_gain':None,'cost_multiple':None,
                'flow_only_zero_bound_gain':False}
    original=float(left['lp_objective']);new=float(right['lp_objective'])
    gain=new-original
    # Denominator of 0 means relative gain is not defined; never score as 1%.
    relative=gain/abs(original) if abs(original)>1e-10 else None
    base_cost=left.get('elapsed_wall_s');extra_cost=right.get('elapsed_wall_s')
    cost=(extra_cost/base_cost if isinstance(base_cost,(float,int)) and base_cost>0 and
          isinstance(extra_cost,(float,int)) and math.isfinite(extra_cost) else None)
    return {'paired_optimal':True,'absolute_gain':gain,'relative_gain':relative,
            'cost_multiple':cost,'flow_only_zero_bound_gain':
              bool(right.get('fcr_added',0)>0 and abs(gain)<=1e-7),
            'objective_nonmonotone':gain < -1e-5}


def analyze(plan,manifest,rows):
    arms=tuple(manifest.get('arms',()))
    ablation=manifest.get('campaign')=='ABLATION'
    expected=tuple(plan['ablation_arms'] if ablation else plan['primary_arms'])
    if arms!=expected:raise ValueError('arm list differs from frozen plan')
    cases=plan['cases']
    selected=set(manifest.get('cases',()))
    if not selected or not selected<=set(c['name'] for c in cases):
        raise ValueError('unknown cases in manifest')
    identities={c['name']:c for c in cases}
    bycase={name:{} for name in selected}
    for row in rows:
        name=row.get('name');arm=row.get('arm_id')
        if name not in bycase or arm not in arms or arm in bycase[name]:
            raise ValueError('duplicate/unknown case arm')
        if (row.get('raw_graph_id')!=identities[name]['raw_graph_id'] or
            row.get('instance_sha256')!=identities[name]['source_sha256']):
            raise ValueError('source identity mismatch')
        bycase[name][arm]=row
    if len(rows)!=len(selected)*len(arms) or any(len(rs)!=len(arms) for rs in bycase.values()):
        raise ValueError('incomplete or excessive arm rows')
    detailed=[]
    successes=set()
    for case in cases:
        name=case['name']
        if name not in selected:continue
        data=bycase[name]
        if ablation:
            comparison=_pair(data['U_K_FCR_SINGLETON'],data['U_K_FCR_HEURISTIC'])
            entry={'name':name,'raw_graph_id':case['raw_graph_id'],
                   'comparison_singletons_vs_extended':comparison,
                   'arms':{a:{'status':data[a].get('status'),'objective':data[a].get('lp_objective'),
                              'elapsed_wall_s':data[a].get('elapsed_wall_s'),
                              'fcr_added':data[a].get('fcr_added',0)} for a in arms}}
        else:
            comparisons={
                'FC_R_vs_COMP':_pair(data['U'],data['U_FCR']),
                'K_vs_COMP':_pair(data['U'],data['U_K']),
                'FC_R_marginal_over_K':_pair(data['U_K'],data['U_K_FCR']),
            }
            marginal=comparisons['FC_R_marginal_over_K']
            enhanced=data['U_K_FCR']
            complete=bool(enhanced.get('singleton_complete_all_scans') is True and
                          enhanced.get('selected_heuristic_complete_all_scans') is True and
                          not enhanced.get('fcr_cut_cap_encountered',False) and
                          not enhanced.get('fcr_total_cut_cap_reached',False))
            qualified=(marginal['paired_optimal'] and not marginal['objective_nonmonotone']
                       and marginal['relative_gain'] is not None
                       and marginal['relative_gain']>=plan['gate']['minimum_relative_gain']
                       and marginal['cost_multiple'] is not None
                       and marginal['cost_multiple']<=plan['gate']['maximum_cost_multiple']
                       and complete)
            if qualified:successes.add(case['raw_graph_id'])
            entry={'name':name,'raw_graph_id':case['raw_graph_id'],
                   'comparisons':comparisons,'counts_for_gate':qualified,
                   'fcr_coverage_complete_selected':complete,
                   'fcr_added':enhanced.get('fcr_added',0),
                   'fcr_violated':enhanced.get('fcr_violated',0),
                   'fcr_duplicates':enhanced.get('fcr_duplicates',0),
                   'arms':{a:{'status':data[a].get('status'),
                              'lp_objective':data[a].get('lp_objective'),
                              'elapsed_wall_s':data[a].get('elapsed_wall_s'),
                              'reason':data[a].get('reason'),
                              'coverage':data[a].get('singleton_complete_all_scans')}
                           for a in arms}}
        detailed.append(entry)
    censured=[{'name':name,'arm_id':arm,'status':row.get('status'),
               'reason':row.get('reason')} for name,group in bycase.items()
             for arm,row in group.items() if not _optimal(row)]
    full_six=len(selected)==len(cases) and len({identities[name]['raw_graph_id'] for name in selected})==6
    if ablation:
        gate='ABLATION_DESCRIPTIVE_ONLY'
    elif (manifest.get('mode')!='LP' or censured or not full_six
          or any(not (bycase[name][arm].get('singleton_complete_all_scans') is True
                      and bycase[name][arm].get('selected_heuristic_complete_all_scans') is True)
                 for name in selected for arm in ('U_FCR','U_K_FCR'))
          or any(bycase[name][arm].get('fcr_cut_cap_encountered',False) or
                 bycase[name][arm].get('fcr_total_cut_cap_reached',False)
                 for name in selected for arm in ('U_FCR','U_K_FCR'))):
        gate='INVESTIGATE'
    elif len(successes)>=plan['gate']['minimum_independent_raw_graphs']:
        gate='GO_CANDIDATE_REVIEW'
    else:
        gate='STOP'
    return {'schema_version':SCHEMA,'stage':'AS25','campaign':manifest['campaign'],
            'mode':manifest.get('mode'),'gate':gate,'arm_rows':len(rows),
            'case_count':len(selected),'independent_raw_graphs':len(set(
                identities[name]['raw_graph_id'] for name in selected)),
            'qualified_raw_graph_ids':sorted(successes),
            'qualified_raw_graph_count':len(successes),'fully_preregistered_six_case_scope':full_six,
            'censored':censured,'censored_arm_count':len(censured),
            'cases':detailed,'plan_sha256':manifest['plan_sha256'],
            'note':('Ablation is descriptive and excluded from the primary gate.' if ablation else
                    'Marginal objective, not flow representation change, determines gain. '
                    'Only all-six fully comparable and uncensored runs can advance to candidate review.'),
            'mip_automatically_authorized':False,
            'scientific_review_required':True,
            'region_coverage_scope':'complete eligible singletons + bounded selected heuristics; never all L'}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--results-dir',type=Path,required=True)
    parser.add_argument('--plan',type=Path,default=Path(__file__).resolve().parents[2]/
                        'docs/technical/plans/execucao/as25-preregistro-fcr-lp.json')
    parser.add_argument('--output',type=Path,default=None)
    args=parser.parse_args()
    plan=json.loads(args.plan.read_text())
    manifest=json.loads((args.results_dir/'manifest.json').read_text())
    rows=json.loads((args.results_dir/'rows.json').read_text())
    report=analyze(plan,manifest,rows)
    if args.output:
        with args.output.open('x',encoding='utf-8') as out:json.dump(report,out,indent=2,ensure_ascii=False)
    else:print(json.dumps({'gate':report['gate'],'cases':report['case_count'],
                           'censored':report['censored_arm_count']},ensure_ascii=False))


if __name__=='__main__':main()
