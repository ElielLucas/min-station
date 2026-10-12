"""AS06: testes derivados dos sete critérios de aceite; sem licença Gurobi."""
from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
for d in (ROOT,HERE,HERE.parent/'alternative-formulations'):
    if str(d) not in sys.path: sys.path.insert(0,str(d))

from as02_model_a import Instance
from as06_mip import (PRIMARY,SECONDARY,make_plan,validate_plan,preflight,
                      compile_mip,physical_trace,expected_slots,_worker,run_arm)
from as06_reporting import (run_campaign,verify_campaign,analyze_campaign,
                            verify_analysis,stage_gate,pair_result,validate_run)
from as04_schema import digest
from experiments.cuts.synthetic import make_F1


class Context:
    def __init__(self): self.phases=[]
    def phase(self,name): self.phases.append(name)
    def remaining(self): return 200
    def require_remaining(self): return 200


def mock_run(row,*,root,plan,arm,seed):
    v=plan['cases'][next(i for i,c in enumerate(plan['cases']) if c['manifest_name']==row['nome'])]
    ub=20
    lb=10 if arm=='U' else 18
    from as04_schema import digest
    k=plan['k_policy']['expected_previous_hashes'].get(v['name'],'K-demo') if arm!='U' else None
    return {'case_name':row['nome'],'seed':seed,'arm_id':arm,'status':'TIME_LIMIT',
       'instance_sha256':row['sha256'], 'structural_sha256':'test-fingerprint',
       'model_complete':True,'wall_total_s':3.,'wall_phases_s':{'solve':1.2},
       'mip_numeric_bound':lb,'mip_numeric_incumbent':float(ub),
       'physical_validated_ub':ub,'installed':[str(x) for x in range(ub)],
       'validated_mip_gap':(ub-lb)/ub,'k_prepared_for_this_arm':arm!='U',
       'reference_k_sha256':k, 'applied_k_sha256':k,
       'n_k_cuts':0 if arm=='U' else 4,
       'partition_sha256':'g4' if arm==SECONDARY else None,
       'a4_parent_sha256':'g2' if arm==SECONDARY else None,
       'numeric_bound_trace':[{'solver_s':1.2,'numeric_lb':lb,'numeric_incumbent':20.,'nodes':0}],
       'physical_trace':[{'solver_s':1.2,'physical_ub':20,'validation':'VALIDATED'}],
       'solver_runtime_s':1.2,'nodes':2.,'solver_work':.2,
       'time_to_first_validated_ub_solver_s':1.2,
       'time_to_best_validated_ub_solver_s':1.2,
       'numeric_callback_dropped_incumbents':0}


class PlanTests(unittest.TestCase):
    def test_fixed_slots_and_sources(self):
        p=make_plan(ROOT)
        self.assertEqual(len(p['cases']),6)
        self.assertEqual(len(expected_slots(p)),15)
        self.assertEqual(p['seeds'],[42])
        self.assertEqual([c['name'] for c in p['cases'] if SECONDARY in c['arms']],list(p['comparison']['secondary_cases']))
        self.assertEqual({c['split'] for c in p['cases']},{'desenvolvimento'})
        self.assertEqual(validate_plan(p,ROOT),p)
    def test_mutation_rejected(self):
        for field,new in [('budget_seconds_per_arm',301),('seeds',[43]),('stage','replication')]:
            p=make_plan(ROOT)
            p[field]=new
            with self.assertRaises((ValueError,FileNotFoundError,KeyError,TypeError)):
                validate_plan(p,ROOT)
    def test_replication_without_gate_refused(self):
        with self.assertRaises(ValueError):make_plan(ROOT,stage='replication')
    def test_size_preflight_does_not_solve(self):
        p=make_plan(ROOT)
        sizes=preflight(ROOT,p)
        self.assertEqual(len(sizes),15)
        self.assertTrue(all(x['status_without_K']=='READY_FOR_BUILD' for x in sizes))


class MathematicalTests(unittest.TestCase):
    def test_compilers_y_binary_and_k(self):
        a=make_F1(m=4,k=1)
        ins=Instance.from_synthetic(a)
        from as03_grouping import partition_two,refine_four
        g2=partition_two(ins,policy='reachability_degree',seed=42)
        g4=refine_four(ins,g2,authorized=True)
        for arm in ('U','U_K','A4_K'):
            model=compile_mip(ins,arm,K=(('h',),) if arm!='U' else (),grouping=g4)
            self.assertEqual(model.families.get('A6',0),int(arm!='U'))
            self.assertTrue(all(v.binary==(key[0]=='y') for key,j in model.columns.items()
                                for v in [model.variables[j]]))
        with self.assertRaises(ValueError):compile_mip(ins,'U',K=(('h',),))
        with self.assertRaises(ValueError):compile_mip(ins,'A4_K',K=(('h',),))
    def test_comp_mip_small_highs(self):
        try:
            import numpy as np
            from scipy.optimize import milp,Bounds,LinearConstraint
            from scipy.sparse import coo_matrix
        except ImportError:
            self.skipTest('SciPy opcional')
        ins=Instance(('s','h','t'),('s',),('t',),
                     (('s','h'),('h','t'),('h','s'),('t','h')),1)
        for arm,cuts in (('U',()),('U_K',(('h',),))):
            m=compile_mip(ins,arm,K=cuts)
            rr,cc,dd=[],[],[]
            lhs,rhs=[],[]
            for i,row in enumerate(m.equations):
                for j,v in row.terms:rr.append(i);cc.append(j);dd.append(v)
                lhs.append(row.rhs if row.sense in ('==','>=') else -np.inf)
                rhs.append(row.rhs if row.sense in ('==','<=') else np.inf)
            A=coo_matrix((dd,(rr,cc)),shape=(len(m.equations),len(m.variables))).tocsr()
            res=milp(np.array([m.objective.get(i,0.) for i in range(len(m.variables))]),
              integrality=np.array([int(v.binary) for v in m.variables]),
              bounds=Bounds([v.lb for v in m.variables],[v.ub for v in m.variables]),
              constraints=LinearConstraint(A,lhs,rhs),options={'time_limit':20})
            self.assertEqual(res.status,0,arm)
            self.assertGreaterEqual(res.fun,1.-1e-6)
            self.assertEqual(int(round(res.fun)),1)
            installed=[k[1] for k,j in m.columns.items() if k[0]=='y' and res.x[j]>.5]
            self.assertIn('h',installed)
    def test_invalid_incumbent_rejected(self):
        loaded=SimpleNamespace(V=('s','h','t'),S=('s',),T=('t',),r=1,
                               adj={'s':[('h',1)],'h':[('s',1),('t',1)],'t':[('h',1)]})
        r=physical_trace(loaded,[{'installed':[],'solver_s':.1,'numeric_ub':0.},
                   {'installed':['h'],'solver_s':.5,'numeric_ub':1.}],['h'],1.)
        self.assertEqual(r['invalid_incumbents'],1)
        self.assertEqual(r['physical_validated_ub'],1)
        self.assertEqual(r['time_to_first_validated_ub_solver_s'],.5)
        self.assertIsNone(r['physical_trace'][0]['physical_ub'])
        r2=physical_trace(loaded,[],[],0.)
        self.assertIsNone(r2['physical_validated_ub'])


class ReporterTests(unittest.TestCase):
    def test_gap_gate_requires_two_families(self):
        rule=make_plan(ROOT)['advance_gate']
        a={'status':'TIME_LIMIT','validated_mip_gap':.5}
        b={'status':'TIME_LIMIT','validated_mip_gap':.1}
        self.assertTrue(pair_result(a,b,rule)['material'])
        pairs=[{'case':'a','graph_source':'puc','raw_graph_id':'puc:a','result':pair_result(a,b,rule)},
               {'case':'b','graph_source':'puc','raw_graph_id':'puc:b','result':pair_result(a,b,rule)}]
        self.assertEqual(stage_gate(make_plan(ROOT),pairs),'STOP_NO_REPRODUCIBLE_MULTIFAMILY_BENEFIT')
        pairs[1]['graph_source']='mapf'
        self.assertEqual(stage_gate(make_plan(ROOT),pairs),'GO_REPLICATION_EXPLORATORY')
        pairs[1]['result']=pair_result(b,a,rule)
        self.assertEqual(stage_gate(make_plan(ROOT),pairs),'STOP_SEVERE_REGRESSION')
        pairs[1]['result']=pair_result({'status':'NO_INCUMBENT'},b,rule)
        self.assertEqual(stage_gate(make_plan(ROOT),pairs),'INCONCLUSIVE_CENSORED')
    def test_gap_no_ub_not_zero(self):
        rule=make_plan(ROOT)['advance_gate']
        r=pair_result({'status':'NO_INCUMBENT','validated_mip_gap':None},
                      {'status':'TIME_LIMIT','validated_mip_gap':0.1},rule)
        self.assertEqual(r['status'],'NOT_COMPARABLE')
        self.assertIsNone(r['absolute_gap_gain'])
    def test_budget_timeout_never_fabricates_bounds(self):
        from fc_budget import BoundedOutcome
        timed=BoundedOutcome('TIMEOUT_PREPARATION',None,3.,(('preparation',3.),),'budget')
        with patch('as06_mip.run_bounded',return_value=timed):
            r=run_arm({'nome':'toy.txt'},root=ROOT,plan=make_plan(ROOT),arm='U_K',seed=42)
        self.assertEqual(r['status'],'TIMEOUT_PREPARATION')
        self.assertIsNone(r['mip_numeric_bound'])
        self.assertIsNone(r['physical_validated_ub'])
    def test_missing_solver_not_marked_optimal(self):
        p=make_plan(ROOT)
        f=mock_run({'nome':p['cases'][0]['manifest_name'], 'sha256':p['cases'][0]['source_sha256']},
                   root=ROOT,plan=p,arm='U_K',seed=42)
        f['status']='SOLVER_ERROR'
        f['mip_numeric_bound']=None
        f['mip_numeric_incumbent']=None
        f['physical_validated_ub']=None
        f['validated_mip_gap']=None
        f['model_complete']=False
        f['installed']=None
        f['solver_policy']={**p['solver'],'seed':42}
        f['solver_policy_sha256']=digest(f['solver_policy'])
        validate_run(f,p['cases'][0],arm='U_K',seed=42,plan=p)
    def test_worker_without_k_does_not_prepare_k(self):
        sample=make_F1(m=4,k=1)
        ins=Instance.from_synthetic(sample)
        S,T,V,adj,arcs,r,_=sample
        loaded=SimpleNamespace(V=V,S=S,T=T,adj=adj,A_r=arcs,r=r,
                               instance_sha256='toy-sha')
        row={'nome':'toy.txt'}
        fake={'status':'TIME_LIMIT','mip_numeric_bound':0.0,'mip_numeric_incumbent':None,
              'physical_validated_ub':None,'validated_mip_gap':None}
        with patch('as06_mip._load_timed',return_value=(loaded,.01,.01)),\
             patch('as06_mip._timed_k',side_effect=AssertionError('sem K!')),\
             patch('as06_mip.resource.setrlimit'),\
             patch('as06_mip._solve_mip',return_value=fake):
            r=_worker(Context(),row,str(ROOT),'U',42,make_plan(ROOT))
        self.assertEqual(r['status'],'TIME_LIMIT')
        self.assertFalse(r['k_prepared_for_this_arm'])
        self.assertIsNone(r['reference_k_sha256'])
    def test_full_campaign_integrity_and_analysis(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'results/benchmark',prefix='as06-test-') as tmp:
            d=Path(tmp);p=ROOT/'results/benchmark/as06-mip-plan-v1.json'
            run_campaign(root=ROOT,plan_path=p,output_dir=d/'campaign',runner=mock_run)
            rep=verify_campaign(d/'campaign',root=ROOT)
            self.assertEqual(rep['expected_slots'],15)
            self.assertEqual(len(rep['cases']),6)
            report=analyze_campaign(d/'campaign',d/'campaign'/'analysis',root=ROOT)
            self.assertTrue(report.is_file())
            an=verify_analysis(d/'campaign'/'analysis')
            self.assertEqual(an['decision'],'GO_REPLICATION_EXPLORATORY')
            # somente após gate reproduzível pode iniciar replicação em plano novo
            follow=make_plan(ROOT,stage='replication',parent_analysis=d/'campaign'/'analysis')
            self.assertEqual(len(expected_slots(follow)),36)
            self.assertEqual(follow['seeds'],[42,43,44])
            self.assertEqual(follow['budget_seconds_per_arm'],600)
            with self.assertRaises(FileExistsError):
                run_campaign(root=ROOT,plan_path=p,output_dir=d/'campaign',runner=mock_run)
    def test_checkpoint_mutation_cannot_be_resumed_or_verified(self):
        with tempfile.TemporaryDirectory(prefix='as06-tamper-') as temp:
            folder=Path(temp)/'run'
            p=ROOT/'results/benchmark/as06-mip-plan-v1.json'
            run_campaign(root=ROOT,plan_path=p,output_dir=folder,runner=mock_run)
            ck=next(folder.glob('checkpoints/**/*.json'))
            ck.write_text(ck.read_text()+'\n',encoding='utf-8')
            with self.assertRaises(ValueError):verify_campaign(folder)
    def test_analysis_tamper_changes_gate_rejected(self):
        with tempfile.TemporaryDirectory(prefix='as06-analysis-') as temp:
            folder=Path(temp)/'run'
            p=ROOT/'results/benchmark/as06-mip-plan-v1.json'
            run_campaign(root=ROOT,plan_path=p,output_dir=folder,runner=mock_run)
            analyze_campaign(folder,folder/'analysis')
            ap=folder/'analysis'/'analysis.json'
            obj=json.loads(ap.read_text())
            obj['decision']='STOP_NO_REPRODUCIBLE_MULTIFAMILY_BENEFIT'
            ap.write_text(json.dumps(obj),encoding='utf-8')
            with self.assertRaises(ValueError):verify_analysis(folder/'analysis')

if __name__=='__main__':unittest.main()
