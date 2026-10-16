"""AS23 acceptance: physical graph, exact nonredundancy, C6/C8 and tampering."""
import copy
import hashlib
import json
import unittest
from pathlib import Path
from fractions import Fraction as F

from verify_fcr_witness import (build_system, declared_c8_counterexample, fcr_region_row, physical_report,
                                primal_checked, recheck_saved, row_value, run, witness_instance)
from as02_model_a import Instance, compile_u


class FCRWitnessReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.system = build_system()
        cls.evidence = run()

    def test_reconstructed_graph_and_real_k(self):
        s = self.system
        ins = s['instance']
        self.assertEqual((len(ins.V), len(s['edges']), len(ins.A_r), ins.r),
                         (24, 48, 96, 1))
        self.assertEqual((len(ins.S), len(ins.T)), (6, 6))
        X = [set(x) for x in s['blocks']]
        c = {'c1', 'c2'}
        expected = {frozenset(c | X[0] | X[1] | X[2]),
                    frozenset(c | X[0] | X[1] | X[3]),
                    frozenset(set.union(*X) | {'e1'}),
                    frozenset(set.union(*X) | {'e2'})}
        self.assertEqual(set(s['K']), expected)
        self.assertEqual(s['compiled'].families,
                         {'A6':4, 'U_bal':24, 'U_in':24, 'U_out':24})
        self.assertEqual((len(s['C6']), len(s['C8']), len(s['FCR'])), (1, 36, 4))
        c6 = s['C6'][0]
        self.assertEqual(c6.rhs, F(2))

    def test_physical_independent_matching(self):
        self.assertEqual(physical_report(self.system), {
            'empty_viable':False, 'viable_singletons':[], 'checked_singletons':24,
            'feasible_pair':['x11','x21'], 'pair_viable':True,
            'proved_integer_optimum':2})

    def test_exact_optima_from_primal_and_dual(self):
        values = {'COMP_K':F(1), 'COMP_K_FCR':F(7,5),
                  'COMP_K_C8':F(11,10), 'COMP_K_C8_FCR':F(7,5),
                  'COMP_K_C6_C8':F(47,30),
                  'COMP_K_C6_C8_FCR':F(17,10)}
        for model, objective in values.items():
            families = {'COMP_K':[], 'COMP_K_FCR':['FCR'], 'COMP_K_C8':['C8'],
                        'COMP_K_C8_FCR':['C8','FCR'],
                        'COMP_K_C6_C8':['C6','C8'],
                        'COMP_K_C6_C8_FCR':['C6','C8','FCR']}[model]
            rows = self.system['base'] + [r for fam in families for r in self.system[fam]]
            certificate = self.evidence['cases'][model]
            self.assertEqual(recheck_saved(self.system['compiled'], rows, certificate), objective)
            self.assertEqual(F(certificate['dual_objective']), objective)
        self.assertGreater(F(self.evidence['comparison']['K_to_K_FCR']),0)
        self.assertGreater(F(self.evidence['comparison']['K_C8_to_K_C8_FCR']),0)
        self.assertGreater(F(self.evidence['comparison']['K_C6_C8_to_FCR']),0)

    def test_witness_violates_at_least_one_fcr_and_c8_point_exists(self):
        s = self.system
        cand = tuple(map(F,self.evidence['cases']['COMP_K']['primal']))
        deficits = [r.rhs-row_value(r,cand) for r in s['FCR']]
        self.assertTrue(any(x>0 for x in deficits))
        c8_point = tuple(map(F,self.evidence['cases']['COMP_K_C8']['primal']))
        self.assertTrue(any(row_value(row,c8_point) < row.rhs for row in s['FCR']))
        self.assertLess(F(self.evidence['cases']['COMP_K_C8']['objective']),F(7,5))

    def test_declared_seventeen_fifteenths_point(self):
        point = declared_c8_counterexample(self.system)
        self.assertEqual(point['objective'], '17/15')
        self.assertEqual(list(map(F, point['fcr_deficits'])),
                         [F(1,3),F(1,3),F(0),F(0)])
        self.assertEqual(len(point['c6_deficits']),1)
        self.assertGreater(F(point['c6_deficits'][0]),0)

    def test_tampered_certificates_are_rejected(self):
        rows = self.system['base'] + self.system['C6'] + self.system['C8'] + self.system['FCR']
        base = self.evidence['cases']['COMP_K_C6_C8_FCR']
        corrupt = copy.deepcopy(base)
        corrupt['objective'] = '0'
        with self.assertRaises(AssertionError):
            recheck_saved(self.system['compiled'],rows,corrupt)
        corrupt = copy.deepcopy(base)
        corrupt['dual_lower'][0] = '-1'
        with self.assertRaises(AssertionError):
            recheck_saved(self.system['compiled'],rows,corrupt)
        corrupt = copy.deepcopy(base)
        corrupt['primal'][0] = '2'
        with self.assertRaises(AssertionError):
            recheck_saved(self.system['compiled'],rows,corrupt)

    def test_reject_invalid_q_and_terminal_counterexamples(self):
        ins, adj, blocks, edges = witness_instance()
        cols = self.system['compiled'].columns
        for Q in [('c1',), ('a1',), ('x21',), ('not-a-vertex',)]:
            with self.subTest(Q=Q):
                with self.assertRaises(ValueError):
                    fcr_region_row(ins, cols, ('a1',), Q)
        # e1->d1 is a direct terminal arc. Excluding S from Q is essential:
        # a source may emit its initial unit without installing a station.
        # This exact case detects the noSexcl mutation.
        for Q in [('a1',), ('d1',), ('e1',)]:
            with self.subTest(Q=Q):
                with self.assertRaises(ValueError):
                    fcr_region_row(ins, cols, ('d1',), Q, direction='destination')
        # Direct terminal trip a1->c1, no stations: the illegally removed
        # flow would make 0 >= 1, demonstrating why terminal Q is forbidden.
        flow = {('a1','c1'):F(1)}
        self.assertEqual(sum(v for (u,w),v in flow.items() if u=='a1' and w not in ('a1','c1')),F(0))
        self.assertEqual(sum(v for (u,w),v in flow.items() if w=='c1' and u not in ('a1','c1')),F(0))
        # A separate physically valid one-robot instance proves the mirror
        # condition without relying only on rejection in the constructor.
        tiny=Instance(('e1','d1'),('e1',),('d1',),(('e1','d1'),),1)
        compiled=compile_u(tiny,relax=False)
        witness=[F(0)]*len(compiled.variables)
        witness[compiled.columns['F','e1','d1']]=F(1)
        from verify_fcr_witness import make_row
        primal_checked([make_row(r.name,r.terms,r.sense,r.rhs)
                        for r in compiled.equations],compiled.variables,witness)
        # Were Q={e1} accepted for FC-R-T with L={d1}, the invalid
        # inequality would be y_e1 >= 1, contradicted by this witness.
        self.assertEqual(witness[compiled.columns['y','e1']],F(0))
        self.assertEqual(witness[compiled.columns['F','e1','d1']],F(1))

    def test_committed_json_rechecked_independently_of_solver(self):
        path=Path(__file__).resolve().parents[2]/'results/benchmark/as23-fcr-witness-001.json'
        self.assertTrue(path.is_file(), f'missing reproducibility evidence: {path}')
        disk=json.loads(path.read_text(encoding='utf-8'))
        self.assertEqual(disk['status'],'EXACT_CERTIFIED')
        self.assertEqual(disk['kind'],'SYNTHETIC_ONLY')
        self.assertEqual(disk['graph_sha256'],self.evidence['graph_sha256'])
        self.assertEqual(disk['K'],self.evidence['K'])
        for relative, saved_hash in disk['source_sha256'].items():
            source=Path(__file__).resolve().parents[2]/relative
            self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),saved_hash)
        models={
            'COMP_K':[], 'COMP_K_FCR':['FCR'],
            'COMP_K_C8':['C8'], 'COMP_K_C8_FCR':['C8','FCR'],
            'COMP_K_C6_C8':['C6','C8'],
            'COMP_K_C6_C8_FCR':['C6','C8','FCR']
        }
        for name, families in models.items():
            with self.subTest(model=name):
                rows=self.system['base']+[r for fam in families for r in self.system[fam]]
                value=recheck_saved(self.system['compiled'],rows,disk['cases'][name])
                self.assertEqual(value,F(self.evidence['cases'][name]['objective']))
                self.assertEqual(str(value),disk['cases'][name]['dual_objective'])
        self.assertEqual(disk['physical'],physical_report(self.system))

    def test_circulation_and_overlapping_terminals_are_legal(self):
        V=('a','e','t','x')
        S=('a','e'); T=('e','t')
        edges=[('a','t'),('a','x'),('t','x')]
        arcs=tuple((u,v) for a,b in edges for u,v in ((a,b),(b,a)))
        ins=Instance(V,S,T,arcs,1)
        model=compile_u(ins,relax=True)
        point=[F(0)]*len(model.variables)
        for v in ('a','t','x'):point[model.columns['y',v]]=F(1)
        for u,v,value in [('a','t',F(1)),('a','x',F(1,2)),
                          ('x','t',F(1,2)),('t','a',F(1,2))]:
            point[model.columns['F',u,v]]=value
        from verify_fcr_witness import make_row
        compiled_rows=[make_row(row.name,row.terms,row.sense,row.rhs)
                       for row in model.equations]
        primal_checked(compiled_rows,model.variables,point)
        src=fcr_region_row(ins,model.columns,('a',),('x',),'origin')
        dst=fcr_region_row(ins,model.columns,('t',),('x',),'destination')
        self.assertGreaterEqual(row_value(src,point),src.rhs)
        self.assertGreaterEqual(row_value(dst,point),dst.rhs)
        self.assertEqual(point[model.columns['F','t','a']],F(1,2))


if __name__ == '__main__':
    unittest.main()
