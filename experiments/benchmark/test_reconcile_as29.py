"""Testes da AS29 derivados de YR29-01 a YR29-06, sem solver."""
import csv
import hashlib
import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('reconcile_as29',HERE/'reconcile_as29.py')
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
ROOT=HERE.parents[1]
CC9='puc-cc9-2p-seed-r1.txt'
_AUDIT=None

def audit():
    global _AUDIT
    if _AUDIT is None:_AUDIT=m.audit(ROOT)
    return _AUDIT

def case(name):
    return next(x for x in audit()[1] if x['case']==name)

def common(name='x.txt',sha='h'):
    return {'case':name,'split':'desenvolvimento','class':'principal','raw_graph_id':'micro','instance_path':'x','instance_sha256':sha,'sha_verified':'true','n':'3','m':'1','r':'1'}

def row(method,*,source='SRC',mode='MIP',lb=None,inc=None,phys='',prov='SOLVER_ONLY',admissible=None,exclusion=''):
    if admissible is None:admissible=method in m.LB_ADMISSIBLE and mode!='LP' and lb is not None
    return {**common(),'source':source,'source_record':f'{source}/{method}','method':method,'mode':mode,'seed':'42','numeric_lb':lb,'lb_integer':m.lb(lb),'lb_admissible':str(admissible).lower(),'lp_value':'','numeric_incumbent':inc,'physical_ub':phys,'ub_provenance':prov,'exclusion':exclusion}

def as09_record(**over):
    x={'instance_sha256':'h','arm':'U','status':'OPTIMAL_NUMERIC','mip_numeric_bound':2.0,'mip_numeric_incumbent':2.0,'physical_validated_ub':2,'installed':['a','b'],'invalid_incumbents':0,'solver_version':'12.0.3'}
    x.update(over);return x

def make_record(x,oracle=lambda c,i:True,method=None):
    return m.solver_record(x,common(),oracle,source='AS09_EXPANDED_EXPLORATORY',source_record='r',source_sha256='s',plan_sha256='p',method=method or x['arm'],mode='MIP',seed=42,threads=4,wall_budget_s=600,cuts=None,notes='')

class TestBounds(unittest.TestCase):
    def test_integer_bound_with_historical_tolerance(self):
        self.assertEqual(m.lb(32.000346),33)
        self.assertEqual(m.lb(31.706052),32)
        self.assertEqual(m.lb(30.0000003),30)
        self.assertIsNone(m.lb('TIME_LIMIT'))
        self.assertIsNone(m.lb('nan'))

    def test_baseline_nucleus_not_upper_bound(self):
        r={'braco':'nucleo','mip_bound':'18','mip_obj':'18','mip_status':'2','seed':'42','threads':'4','work_limit':'164','guard_s':'1800','fonte_certificado':'solver','commit':'old','cuts_sha256':''}
        out=m.baseline_record(r,{'case':'micro'},'h')
        self.assertEqual(out['lb_integer'],18)
        self.assertEqual(out['physical_ub'],'')
        self.assertEqual(out['ub_provenance'],'NOT_PHYSICAL_UB')

    def test_k_ip_incumbent_never_enters_ub_envelope(self):
        s=m.summarize(common(),[row('K_IP',lb=5,inc=5,prov='NOT_PHYSICAL_UB'),row('U',lb=4,inc=7)])
        self.assertEqual(s['historic_lb_integer'],5)
        self.assertEqual(s['ub_numeric_envelope'],7)
        self.assertEqual(s['status'],'OPEN_SOLVER_UB_ONLY')

    def test_unproven_formulation_bound_is_not_admissible(self):
        r=make_record(as09_record(arm='C',mip_numeric_bound=99.0,mip_numeric_incumbent=99.0,physical_validated_ub=None,installed=None))
        self.assertEqual(r['lb_admissible'],'false')
        s=m.summarize(common(),[r,row('U',lb=3,inc=4)])
        self.assertEqual(s['historic_lb_integer'],3)
        self.assertEqual(s['status'],'OPEN_SOLVER_UB_ONLY')

    def test_lp_value_kept_apart_from_mip_lb(self):
        lp=row('U_K',mode='LP',admissible=False,prov='NOT_APPLICABLE_LP');lp['lp_value']=9.5
        s=m.summarize(common(),[lp,row('U',lb=3,inc=4)])
        self.assertEqual(s['lp_u_k'],9.5)
        self.assertEqual(s['historic_lb_integer'],3)

    def test_lp_column_ignores_unproven_formulation(self):
        lp=row('C_K',mode='LP',admissible=False,prov='NOT_APPLICABLE_LP');lp['lp_value']=40.0
        s=m.summarize(common(),[lp,row('U',lb=3,inc=4)])
        self.assertEqual((s['lp_u'],s['lp_u_k']),('',''))

    def test_censoring_follows_solver_status(self):
        r={'braco':'base','mip_bound':'4','mip_obj':'6','mip_status':'16','seed':'42','threads':'4','work_limit':'164','guard_s':'1800','fonte_certificado':'solver','commit':'c','cuts_sha256':''}
        self.assertEqual(m.baseline_record(r,{'case':'x'},'h')['censored'],'true')
        self.assertEqual(m.baseline_record({**r,'mip_status':'2'},{'case':'x'},'h')['censored'],'false')
        self.assertEqual(make_record(as09_record(status='TIME_LIMIT'))['censored'],'true')
        self.assertEqual(make_record(as09_record())['censored'],'false')

    def test_case_without_any_ub_is_incomplete_and_blocks(self):
        s=m.summarize(common(),[row('K_IP',lb=3,inc=3,prov='NOT_PHYSICAL_UB')])
        self.assertEqual(s['status'],'INCOMPLETE')
        self.assertEqual(s['opt_numeric'],'')
        self.assertEqual(m.gate([s])['gate'],'G0_BLOCKED')

    def test_documented_bounds_shown_side_by_side_not_merged(self):
        c={**common(),'_documented':{'manifest_lb':'3','manifest_ub':'9','manifest_fonte_lb_ub':'P','manifest_lb_melhor':'5','manifest_ub_melhor':'6','manifest_fonte_melhor':'E13'}}
        s=m.summarize(c,[row('U',lb=4,inc=7)])
        self.assertEqual((s['historic_lb_integer'],s['ub_numeric_envelope']),(4,7))
        self.assertEqual((s['lb_documented_max'],s['ub_documented_min'],s['manifest_fonte_melhor']),(5,6,'E13'))
        self.assertIn('DOCUMENTED_BOUND_OUTSIDE_ENVELOPE',s['issues'])
        self.assertEqual(s['status'],'OPEN_SOLVER_UB_ONLY')
        self.assertNotIn('_documented',s)
        # Lado UB: manifest_ub abaixo da UB numérica, sem lb/ub_melhor e sem UB física.
        c={**common(),'_documented':{'manifest_lb':'2','manifest_ub':'6','manifest_fonte_lb_ub':'P','manifest_lb_melhor':'','manifest_ub_melhor':'','manifest_fonte_melhor':''}}
        s=m.summarize(c,[row('U',lb=4,inc=7)])
        self.assertEqual((s['lb_documented_max'],s['ub_documented_min']),(2,6))
        self.assertIn('DOCUMENTED_BOUND_OUTSIDE_ENVELOPE',s['issues'])

    def test_lb_above_ub_is_inconsistent_not_optimal(self):
        s=m.summarize(common(),[row('U',lb=5,inc=4)])
        self.assertEqual(s['status'],'INCONSISTENT')
        self.assertIn('LB_EXCEEDS_UB',s['issues'])
        s=m.summarize(common(),[row('U_K',lb=5,inc=6),row('U',inc=6,phys=4,prov='ORACLE_REVALIDATED_AS29')])
        self.assertEqual(s['status'],'INCONSISTENT')

    def test_opt_classes_distinguish_physical_and_solver_only(self):
        s=m.summarize(common(),[row('U',lb=3,inc=3)])
        self.assertEqual((s['status'],s['opt_numeric'],s['ub_reference_eligible']),('OPT_NUMERIC_SOLVER_ONLY',3,'false'))
        s=m.summarize(common(),[row('U',source='SPEC_A_R4',lb=3,inc=4),row('U',lb=2,inc=3,phys=3,prov='ORACLE_REVALIDATED_AS29')])
        self.assertEqual((s['status'],s['opt_numeric'],s['ub_reference_eligible']),('OPT_NUMERIC_PHYSICAL',3,'true'))
        s=m.summarize(common(),[row('U',lb=2,inc=3,phys=3,prov='ORACLE_REVALIDATED_AS29')])
        self.assertEqual((s['status'],s['opt_numeric']),('OPEN_PHYSICAL_UB',''))

class TestPhysicalEvidence(unittest.TestCase):
    def test_physical_validation_must_have_consistent_support(self):
        self.assertEqual(m.validated_ub(3,['a','b','c'],0),3)
        self.assertIsNone(m.validated_ub(3,['a','b'],0))
        self.assertIsNone(m.validated_ub(3,['a','b','c'],1))
        self.assertIsNone(m.validated_ub(3.2,['a','b','c'],0))
        self.assertIsNone(m.validated_ub('',[],0))

    def test_reported_ub_requires_independent_oracle(self):
        ok=make_record(as09_record())
        self.assertEqual((ok['physical_ub'],ok['ub_provenance']),(2,'ORACLE_REVALIDATED_AS29'))
        bad=make_record(as09_record(),oracle=lambda c,i:False)
        self.assertEqual((bad['physical_ub'],bad['ub_provenance']),('','ORACLE_REJECTED'))
        s=m.summarize(common(),[bad,row('U',lb=2,inc=2)])
        self.assertEqual(s['status'],'INCONSISTENT')

    def test_evidence_from_other_instance_is_rejected(self):
        r=make_record(as09_record(instance_sha256='other'),oracle=lambda c,i:self.fail('oracle must not run'))
        self.assertEqual(r['exclusion'],'INSTANCE_SHA_MISMATCH')
        self.assertEqual((r['physical_ub'],r['lb_admissible']),('','false'))
        s=m.summarize(common(),[r,row('U',lb=1,inc=3)])
        self.assertEqual((s['historic_lb_integer'],s['ub_numeric_envelope'],s['physical_ub_validated']),(1,3,''))

    def test_oracle_accepts_archived_installation_and_rejects_reduced_one(self):
        oracle=m.physical_oracle(ROOT)
        x=json.loads((ROOT/'results/benchmark/as06-mip-replication-001/checkpoints/puc-cc9-2p-seed-r1/arm-00.json').read_text())['result']
        c=case(CC9);C=x['installed']
        self.assertEqual(len(C),31)
        self.assertTrue(oracle(c,C))
        # LB numérico 31: qualquer instalação com 30 estações deve ser rejeitada.
        self.assertFalse(oracle(c,C[1:]))
        self.assertFalse(oracle(c,[]))
        self.assertFalse(oracle(c,C+[C[0]]))
        self.assertFalse(oracle(c,C[:-1]+['nao-e-vertice']))

class TestIntegrity(unittest.TestCase):
    def test_missing_source_hash_cannot_silently_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp);p=base/'instance.txt';p.write_bytes(b'bad')
            meta={'x.txt':{'nome':'x.txt','caminho':'instance.txt','sha256':hashlib.sha256(b'good').hexdigest(),'particao':'desenvolvimento','classe':'principal','fonte':'micro','instancia_original':'x','n':'2','m':'1','r':'1'}}
            d=m.basic(meta,'x.txt',base)
            self.assertEqual(d['sha_verified'],'false')
            self.assertEqual(m.summarize(d,[row('U',lb=1,inc=1)])['status'],'INTEGRITY_BLOCKED')

    def _as09_copy(self,root):
        live=ROOT/'results/benchmark/as09-expanded-600s-001';base=root/'results/benchmark/as09-expanded-600s-001'
        (base/'MIP').mkdir(parents=True);shutil.copy2(live/'plan.json',base/'plan.json');shutil.copy2(live/'MIP/manifest.json',base/'MIP/manifest.json')
        return live,base

    def test_as09_manifest_integrity_rejects_tamper(self):
        with tempfile.TemporaryDirectory() as tmp:
            live,base=self._as09_copy(Path(tmp))
            name='puc-cc9-2p-seed-r1--U.json'
            (base/'MIP'/name).write_bytes((live/'MIP'/name).read_bytes()+b' ')
            with self.assertRaisesRegex(ValueError,'AS09 digest integrity'):
                m.extra_records(Path(tmp),{CC9:common(CC9,'x')},oracle=lambda c,i:True)

    def test_as09_plan_tamper_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            live,base=self._as09_copy(Path(tmp))
            plan=json.loads((base/'plan.json').read_text());plan['budget_seconds_per_arm']=601
            (base/'plan.json').write_text(json.dumps(plan))
            with self.assertRaisesRegex(ValueError,'AS09 plan digest'):
                m.extra_records(Path(tmp),{CC9:common(CC9,'x')},oracle=lambda c,i:True)

    def test_reserved_results_are_never_opened(self):
        with tempfile.TemporaryDirectory() as tmp:
            live,base=self._as09_copy(Path(tmp))
            (base/'MIP/i-i160-301-regiao-f2--U.json').write_bytes(b'{not json')
            self.assertEqual(m.extra_records(Path(tmp),{CC9:common(CC9,'x')},oracle=lambda c,i:True),[])

    def test_as06_plan_tamper_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);a06=root/'results/benchmark/as06-mip-replication-001';(a06/'checkpoints').mkdir(parents=True)
            live=ROOT/'results/benchmark/as06-mip-replication-001'
            for f in ('manifest.json','report.json'):shutil.copy2(live/f,a06/f)
            plan=json.loads((live/'plan.json').read_text());plan['budget_seconds_per_arm']=99999
            (a06/'plan.json').write_text(json.dumps(plan))
            with self.assertRaisesRegex(ValueError,'AS06 plan digest'):
                m.extra_records(root,{CC9:common(CC9,'x')},oracle=lambda c,i:True)

    def test_as06_sidecar_integrity_rejects_tamper(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);a06=root/'results/benchmark/as06-mip-replication-001';base=a06/'checkpoints/puc-cc9-2p-seed-r1';base.mkdir(parents=True)
            live=ROOT/'results/benchmark/as06-mip-replication-001'
            for f in ('plan.json','manifest.json','report.json'):shutil.copy2(live/f,a06/f)
            shutil.copy2(live/'checkpoints/puc-cc9-2p-seed-r1/arm-00.sha256',base/'arm-00.sha256')
            (base/'arm-00.json').write_bytes((live/'checkpoints/puc-cc9-2p-seed-r1/arm-00.json').read_bytes()+b' ')
            with self.assertRaisesRegex(ValueError,'AS06 sidecar integrity'):
                m.extra_records(root,{CC9:common(CC9,'x')},oracle=lambda c,i:True)

class TestRealEnvelope(unittest.TestCase):
    def test_full_scope_excludes_evaluation(self):
        p,s=audit()
        reserved={x['nome'] for x in m.rows(ROOT/'instances/manifest.csv') if x['particao']=='avaliacao'}
        self.assertEqual(sum(x['split']=='desenvolvimento' for x in s),31)
        self.assertEqual(sum(x['split']=='legado' for x in s),5)
        self.assertFalse(any(x['split']=='avaliacao' or x['case'] in reserved for x in p+s))
        self.assertTrue(all(x['sha_verified']=='true' for x in s))
        # 192 Spec A + 36 AS06 (U/U_K × 3 seeds × 6 casos) + 32 AS09 MIP + 32 AS09 LP (4 braços × 8 casos)
        # + 46 da exportação posterior (23 casos × U/U_K).
        self.assertEqual(Counter((x['source'],x['mode']) for x in p),{('SPEC_A_R4','MIP'):128,('SPEC_A_R4','IP'):64,('AS06_REPLICATION','MIP'):36,('AS09_EXPANDED_EXPLORATORY','MIP'):32,('AS09_EXPANDED_EXPLORATORY','LP'):32,('AS29_POSTERIOR_EXPORT','MIP'):46})

    def test_cuts_hash_scope_is_labelled(self):
        p,_=audit()
        self.assertEqual({x['cuts_scope'] for x in p if x['source']=='SPEC_A_R4'},{'generator'})
        self.assertEqual({x['cuts_scope'] for x in p if x['source']!='SPEC_A_R4' and x['cuts_sha256']},{'instance_K'})
        self.assertEqual({x['cuts_scope'] for x in p if x['source']!='SPEC_A_R4' and not x['cuts_sha256']},{''})

    def test_every_physical_ub_was_revalidated_by_oracle(self):
        p,_=audit()
        phys=[x for x in p if x['physical_ub']!='']
        self.assertTrue(phys)
        self.assertTrue(all(x['ub_provenance']=='ORACLE_REVALIDATED_AS29' and x['physical_ub']==x['physical_ub_reported'] for x in phys))
        self.assertFalse(any(x['ub_provenance']=='ORACLE_REJECTED' for x in p))

    def test_cc9_baseline_bound_not_merged_with_later_numeric_opt(self):
        p,_=audit();x=case(CC9)
        self.assertEqual(x['base_lb_integer'],30)
        self.assertTrue(all(r['lb_integer']==30 for r in p if r['case']==CC9 and r['source']=='SPEC_A_R4' and r['method']!='K_IP'))
        self.assertEqual((x['historic_lb_integer'],x['physical_ub_validated'],x['opt_numeric'],x['status']),(31,31,31,'OPT_NUMERIC_PHYSICAL'))
        self.assertIn('as06-mip-replication-001',x['historic_lb_source'])

    def test_w3c571_later_bound_kept_apart(self):
        x=case('puc-w3c571-seed-r1.txt')
        self.assertEqual((x['base_lb_integer'],x['historic_lb_integer'],x['historic_lb_method']),(669,678,'U_K'))
        self.assertEqual((x['base_ub_numeric_only'],x['physical_ub_validated'],x['status']),(1064,1079,'OPEN_PHYSICAL_UB'))

    def test_no_fabricated_physical_ub_for_unvalidated_baseline(self):
        # A UB física vem da instalação revalidada (seed 42, 58), não do menor objetivo numérico (57, seed 44, sem instalação).
        x=case('puc-cc10-2u-seed-r1.txt')
        self.assertEqual((x['ub_numeric_envelope'],x['physical_ub_validated'],x['status'],x['ub_reference_eligible']),(57,58,'OPEN_PHYSICAL_UB','true'))
        self.assertIn('AS29_POSTERIOR_EXPORT'.lower().replace('as29_posterior_export','as29-physical-ub-001'),x['physical_ub_source'])
        self.assertEqual(x['pending'],'')

    def test_no_confusion_between_mip_lb_and_lp(self):
        x=case('puc-bip42p-regiao-f2.txt')
        self.assertEqual((x['base_lb_integer'],x['base_lb_method']),(35,'K_IP'))
        self.assertEqual((x['physical_ub_validated'],x['opt_numeric']),(43,''))
        self.assertLess(x['lp_u_k'],x['historic_lb_integer'])

    def test_manifest_bounds_outside_envelope_are_reported(self):
        x=case('vienna-I065-intercalado-f2.txt')
        self.assertEqual((x['historic_lb_integer'],x['ub_numeric_envelope']),(16,20))
        self.assertEqual((x['lb_documented_max'],x['ub_documented_min']),(17,19))
        self.assertIn('DOCUMENTED_BOUND_OUTSIDE_ENVELOPE',x['issues'])
        self.assertNotIn('DOCUMENTED_BOUND_OUTSIDE_ENVELOPE',case(CC9)['issues'])
        # Só o lado UB diverge aqui: manifesto ub=19 e ub_melhor=17 contra UB numérica 20.
        y=case('vienna-I065-regiao-f4.txt')
        self.assertEqual((y['historic_lb_integer'],y['lb_documented_max'],y['ub_numeric_envelope'],y['ub_documented_min']),(14,14,20,17))
        self.assertIn('DOCUMENTED_BOUND_OUTSIDE_ENVELOPE',y['issues'])

    def test_deterministic(self):
        p,s=audit();p2,s2=m.audit(ROOT)
        self.assertEqual(p,p2);self.assertEqual(s,s2)

class TestGate(unittest.TestCase):
    def _s(self,status,eligible,split='desenvolvimento'):
        return {'case':status+split+eligible,'split':split,'status':status,'ub_reference_eligible':eligible}

    def test_gate_rules(self):
        self.assertEqual(m.gate([self._s('OPT_NUMERIC_PHYSICAL','true'),self._s('OPEN_PHYSICAL_UB','true')])['gate'],'G0_CANDIDATE_PASS')
        g=m.gate([self._s('OPT_NUMERIC_PHYSICAL','true'),self._s('OPT_NUMERIC_SOLVER_ONLY','false')])
        self.assertEqual((g['gate'],g['amendment_candidate']),('G0_BLOCKED_EVIDENCE','G0_PASS_RESTRICTED_IF_AMENDMENT_A1_APPROVED'))
        for bad in ('INCONSISTENT','INTEGRITY_BLOCKED','INCOMPLETE'):
            g=m.gate([self._s('OPT_NUMERIC_PHYSICAL','true'),self._s(bad,'false')])
            self.assertEqual((g['gate'],g['amendment_candidate']),('G0_BLOCKED',''))
        self.assertEqual(m.gate([self._s('OPT_NUMERIC_PHYSICAL','true','legado')])['gate'],'G0_BLOCKED')
        self.assertEqual(m.gate([self._s('OPT_NUMERIC_PHYSICAL','true'),self._s('INCONSISTENT','false','legado')])['gate'],'G0_CANDIDATE_PASS')

    def test_real_gate_follows_original_contract_and_never_approves(self):
        g=m.gate(audit()[1])
        self.assertEqual((g['gate'],g['amendment_candidate']),('G0_CANDIDATE_PASS',''))
        self.assertEqual((g['blocked_cases'],g['rev0_strict_physical_ub_all_dev']),([],'31/31'))
        self.assertTrue(all(case(c)['physical_ub_validated']!='' for c in g['ub_reference_eligible']))
        self.assertNotIn('APPROVED',g['gate'])

    def test_posterior_export_reproduces_historical_seed42_rows(self):
        hist={(r['nome'],{'base':'U','comp':'U_K'}[r['braco']]):r for r in m.rows(ROOT/'results/benchmark/linha_base.csv') if r['braco'] in('base','comp') and r['seed']=='42'}
        p,_=audit();new=[x for x in p if x['source']=='AS29_POSTERIOR_EXPORT']
        self.assertEqual(len(new),46)
        for x in new:
            h=hist[(x['case'],x['method'])]
            self.assertEqual(float(h['mip_obj']),x['numeric_incumbent'],x['case'])
            self.assertAlmostEqual(float(h['mip_bound']),x['numeric_lb'],delta=1e-2,msg=x['case'])
            self.assertEqual((x['ub_provenance'],x['work_limit'],x['threads']),('ORACLE_REVALIDATED_AS29',164.0,4))

    def test_posterior_export_infeasible_installation_is_rejected_by_oracle(self):
        name='pucn-cc6-2n-seed-r1';c=case(name+'.txt')
        live=json.loads((ROOT/f'results/benchmark/as29-physical-ub-001/{name}--U.json').read_text())
        oracle=m.physical_oracle(ROOT);real=live['installed'];n=len(real)
        from ms_utils import ler_instancia
        verts=sorted(str(v) for v in ler_instancia(str(ROOT/c['instance_path']))['V'])
        fake=[v for v in verts if v not in set(real)][:n]
        self.assertEqual(len(fake),n)
        self.assertFalse(oracle(c,fake))
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);d=root/'results/benchmark/as29-physical-ub-001';d.mkdir(parents=True)
            data=json.dumps({**live,'installed':fake,'physical_validated_ub':n}).encode()
            (d/f'{name}--U.json').write_bytes(data);(d/f'{name}--U.sha256').write_text(hashlib.sha256(data).hexdigest()+'\n')
            recs=m.extra_records(root,{name+'.txt':{**c,'instance_sha256':live['instance_sha256']}},oracle=oracle)
        self.assertEqual((recs[0]['ub_provenance'],recs[0]['physical_ub']),('ORACLE_REJECTED',''))
        s=m.summarize(c,[recs[0],row('U',lb=6,inc=6)])
        self.assertEqual(s['status'],'INCONSISTENT')

    def test_posterior_export_sidecar_tamper_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);d=root/'results/benchmark/as29-physical-ub-001';d.mkdir(parents=True)
            live=ROOT/'results/benchmark/as29-physical-ub-001';name='b-b06-intercalado-f2--U'
            shutil.copy2(live/(name+'.sha256'),d/(name+'.sha256'))
            (d/(name+'.json')).write_bytes((live/(name+'.json')).read_bytes()+b' ')
            with self.assertRaisesRegex(ValueError,'AS29 export sidecar'):
                m.extra_records(root,{'b-b06-intercalado-f2.txt':common('b-b06-intercalado-f2.txt','x')},oracle=lambda c,i:True)

if __name__=='__main__':unittest.main()
