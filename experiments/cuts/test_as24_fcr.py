"""AS24 microvalidation: brute-force Q, binary-flow adversaries, strict coverage.

Independent oracle for Q enumerates all candidate subsets and evaluates the
closed-form inequality directly, without calling the production constructor.
"""
import itertools
import json
import random
import unittest
from fractions import Fraction as F
from pathlib import Path
from unittest.mock import patch

from experiments.cuts.fcr_rows import construct_row, eligible_frontier, region_excess, evaluate
from experiments.cuts.fcr_separator import separate_fixed, scan
from experiments.cuts.fcr_regions import choose_regions
from verify_fcr_witness import witness_instance, build_system, row_value
from as02_model_a import Instance, compile_u


def brute_q(instance, L, direction, y, f):
    R = set(L)
    signed = len(R.intersection(instance.S))-len(R.intersection(instance.T))
    demand = signed if direction == 'origin' else -signed
    assert demand > 0
    if direction == 'origin':
        edge = [(u,v) for u,v in instance.A_r if u in R and v not in R]
        possible = sorted({v for u,v in edge}-set(instance.T))
    else:
        edge = [(u,v) for u,v in instance.A_r if v in R and u not in R]
        possible = sorted({u for u,v in edge}-set(instance.S))
    outcomes=[]
    for n in range(len(possible)+1):
        for sub in itertools.combinations(possible,n):
            Q=set(sub)
            # Independent expression from the flow balance and Q split.
            flow=sum((f.get((u,v),0) for u,v in edge if (v if direction=='origin' else u) not in Q),F(0))
            station=sum((y.get(v,0) for v in Q),F(0))
            outcomes.append((flow+demand*station,sub))
    optimum=min(lhs for lhs,_ in outcomes)
    winners=[Q for lhs,Q in outcomes if lhs==optimum]
    return optimum,winners


def tiny_instance(V, S, T, undirected_edges, r=1):
    arcs=tuple(sorted({(u,v) for a,b in undirected_edges for u,v in ((a,b),(b,a))}))
    return Instance(tuple(V),tuple(S),tuple(T),arcs,r)


class AS24FCRTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ins, *_ = witness_instance()

    def test_general_rows_match_as23_independent_constructor(self):
        from verify_fcr_witness import fcr_region_row
        compiled=compile_u(self.ins,relax=True)
        for L,Q,direction in [(('a1',),('x11','x12','x13'),'origin'),
                               (('d1',),('x11','x21'),'destination'),
                               (('a1','a2'),('x11','x21'),'origin'),
                               (('d1','d2'),('x11','x21'),'destination')]:
            new=construct_row(self.ins,L,Q,direction).as_compiled(compiled.columns)
            old=fcr_region_row(self.ins,compiled.columns,L,Q,direction)
            self.assertEqual((new.terms,new.sense,new.rhs),(old.terms,old.sense,old.rhs))

    def test_q_optimality_exhaustive_both_directions_demand_one_and_two(self):
        rng=random.Random(24002)
        cases=[('origin',('a1',)),('destination',('d1',)),
               ('origin',('a1','a2')),('destination',('d1','d2'))]
        for direction,L in cases:
            for _ in range(20):
                y={v:F(rng.randrange(0,11),10) for v in self.ins.V}
                f={a:F(rng.randrange(0,15),12) for a in self.ins.A_r}
                expected,winners=brute_q(self.ins,L,direction,y,f)
                actual=separate_fixed(self.ins,L,y,f,direction)
                self.assertEqual(actual.lhs,expected)
                self.assertIn(actual.q_opt,winners)
                self.assertEqual(actual.row.rhs,2 if len(L)==2 else 1)

    def test_ties_excluded_and_negative_candidate_rejected(self):
        x=separate_fixed(self.ins,('a1',),{'x11':F(1,3)},
                         {('a1','x11'):F(1,3)},'origin')
        self.assertNotIn('x11',x.q_opt)
        with self.assertRaises(ValueError):
            separate_fixed(self.ins,('a1',),{'x11':-F(1,2)}, {}, 'origin')
        with self.assertRaises(ValueError):
            separate_fixed(self.ins,('a1',),{}, {('a1','x11'):float('nan')}, 'origin')
        with self.assertRaises(ValueError):
            separate_fixed(self.ins,('a1',),{'unlisted':F(1)}, {}, 'origin')

    def test_invalid_Q_terminal_and_invalid_region_abstain(self):
        for L,Q,direction in [(('a1',),('c1',),'origin'),
                               (('d1',),('e1',),'destination'),
                               (('a1',),('a1',),'origin'),
                               (('a1',),('x21',),'origin'),
                               (('a1',),('x11','x11'),'origin'),
                               (('a1','c1'),(),'origin'),
                               (('a1',),('x11',),'destination')]:
            with self.subTest(L=L,Q=Q,direction=direction),self.assertRaises(ValueError):
                construct_row(self.ins,L,Q,direction)
        self.assertEqual(eligible_frontier(self.ins,('d1',),'destination'),
                         tuple(sorted({v for v in ('x11','x21','x31','x41',
                                                  'x12','x22','x32','x42',
                                                  'x13','x23','x33','x43')})))

    def test_full_singleton_coverage_and_regional_ablation(self):
        plan=choose_regions(self.ins,max_larger=4)
        self.assertEqual(len(plan.singletons),len(set(self.ins.S)^set(self.ins.T)))
        self.assertLessEqual(len(plan.larger),4)
        self.assertEqual(plan.larger_generated,len(plan.larger)+plan.larger_discarded)
        result=scan(self.ins,{}, {}, max_larger=4)
        self.assertTrue(result.stats['singleton_complete'])
        self.assertEqual(result.stats['singletons_eligible'],result.stats['singletons_checked'])
        self.assertEqual(result.stats['larger_checked'],len(plan.larger))
        self.assertFalse(result.stats['global_region_separation'])
        result2=scan(self.ins,{}, {},include_larger=False)
        self.assertEqual(result2.stats['larger_checked'],0)
        self.assertEqual(result2.stats['singletons_checked'],result.stats['singletons_checked'])

    def test_time_budget_reports_partial_and_cap_does_not_hide_singletons(self):
        partial=scan(self.ins,{}, {},time_limit_s=0)
        self.assertEqual(partial.status,'PARTIAL_SINGLETONS')
        self.assertEqual(partial.stats['coverage'],'PARTIAL_SINGLETONS')
        # This point is deliberately not a feasible COMP LP point; the
        # separator is required only to find candidate row violations.
        capped=scan(self.ins,{}, {},max_cuts=0,include_larger=False)
        self.assertTrue(capped.stats['singleton_complete'])
        self.assertEqual(len(capped.cuts),0)
        self.assertGreater(capped.stats['capped'],0)
        self.assertEqual(capped.status,'CUT_CAP_REACHED')

    def test_budget_cutoff_after_complete_singletons_is_declared(self):
        n=len(choose_regions(self.ins,max_larger=3).singletons)
        calls=[0]
        def clock():
            calls[0]+=1
            return 0 if calls[0]<=n+1 else 10
        with patch('experiments.cuts.fcr_separator.time.monotonic',side_effect=clock):
            result=scan(self.ins,{}, {}, max_larger=3,time_limit_s=5)
        self.assertEqual(result.status,'PARTIAL_HEURISTIC')
        self.assertTrue(result.stats['singleton_complete'])
        self.assertFalse(result.stats['larger_complete_selected'])
        self.assertEqual(result.stats['reason'],'TIME_LIMIT')

    def test_determinism_and_deduplication(self):
        x=scan(self.ins,{}, {},max_larger=5)
        y=scan(self.ins,{}, {},max_larger=5)
        self.assertEqual([r.signature for r in x.cuts],[r.signature for r in y.cuts])
        self.assertEqual(x.events,y.events)
        self.assertEqual(len(x.cuts),len({r.signature for r in x.cuts}))
        self.assertEqual(x.stats['violated'],x.stats['emitted']+x.stats['capped']+x.stats['duplicates'])
        self.assertTrue(all(c.demand>0 and c.rhs==c.demand for c in x.cuts))

    def test_stored_witness_lp_produces_actual_violations(self):
        system=build_system()
        file=Path(__file__).resolve().parents[2]/'results/benchmark/as23-fcr-witness-001.json'
        data=json.loads(file.read_text())
        primal=[F(v) for v in data['cases']['COMP_K']['primal']]
        model=system['compiled']
        y={v:primal[model.columns['y',v]] for v in self.ins.V}
        f={(u,v):primal[model.columns['F',u,v]] for u,v in self.ins.A_r}
        result=scan(self.ins,y,f,max_larger=12)
        self.assertTrue(result.stats['singleton_complete'])
        self.assertGreater(len(result.cuts),0)
        for row in result.cuts:
            converted=row.as_compiled(model.columns)
            self.assertEqual(F(row.rhs)-row_value(converted,primal),row.rhs-evaluate(row,y,f))
            self.assertGreater(F(row.rhs)-row_value(converted,primal),0)
        self.assertTrue(any(r.region==('a1',) for r in result.cuts))

    def test_balanced_s_equal_t_and_overlap(self):
        ins=tiny_instance(('s','t','x'),('s',),('s',),[('s','t'),('t','x')])
        self.assertEqual(choose_regions(ins).singletons,())
        self.assertEqual(scan(ins,{},{}).stats['examined'],0)
        partial=tiny_instance(('a','e','t','x'),('a','e'),('e','t'),
                              [('a','t'),('a','x'),('t','x')])
        self.assertEqual(choose_regions(partial).singletons,(('a',),('t',)))
        self.assertNotIn('e',choose_regions(partial).singletons[0])

    def test_r_greater_than_one_uses_reachability_not_physical_edges(self):
        # H contains s->x and s->t due to r=2, although physical G
        # has only two edges s--x--t.  A terminal t cannot enter Q.
        physical=[('s','x'),('x','t')]
        V=('s','x','t')
        distances={u:{u:0} for u in V}
        for u in V:
            stack=[u]
            for v in stack:
                for a,b in physical:
                    w=b if a==v else (a if b==v else None)
                    if w is not None and w not in distances[u]:
                        distances[u][w]=distances[u][v]+1
                        stack.append(w)
        reach=tuple(sorted((u,v) for u in V for v,dist in distances[u].items() if u!=v and dist<=2))
        ins=Instance(V,('s',),('t',),reach,2)
        self.assertEqual(eligible_frontier(ins,('s',),'origin'),('x',))
        self.assertIn(('F','s','t'),[key for key,c in construct_row(ins,('s',),('x',)).terms])

    def test_direct_pair_no_station_and_shared_station_two_robots(self):
        direct=Instance(('s','t'),('s',),('t',),(('s','t'),),1)
        self.assertEqual(scan(direct,{}, {('s','t'):F(1)}).cuts,())
        self.assertTrue(scan(direct,{}, {('s','t'):F(1)}).stats['singleton_complete'])
        shared=tiny_instance(('a','b','x','t','w'),('a','b'),('t','w'),
                             [('a','x'),('b','x'),('x','t'),('x','w')])
        f={('a','x'):F(1),('b','x'):F(1),('x','t'):F(1),('x','w'):F(1)}
        y={'x':F(1)}
        src=separate_fixed(shared,('a','b'),y,f,'origin')
        dst=separate_fixed(shared,('t','w'),y,f,'destination')
        self.assertEqual(src.rhs,2)
        self.assertEqual(dst.rhs,2)
        self.assertLessEqual(src.deficit,0)
        self.assertLessEqual(dst.deficit,0)

    def test_adversarial_integral_network_flows_against_every_small_row(self):
        # Small integer station choices; adversarial flows minimize each
        # row subject to *all COMP equations*, including possible cycles.
        import numpy as np
        from scipy.optimize import linprog
        instances=[
            tiny_instance(('s','x','t'),('s',),('t',),
                          [('s','x'),('x','t'),('s','t')]),
            tiny_instance(('s','x','z','t'),('s',),('t',),
                          [('s','x'),('x','z'),('z','t'),('s','t')]),
            tiny_instance(('a','e','x','t'),('a','e'),('e','t'),
                          [('a','t'),('a','x'),('x','t')]),
            tiny_instance(('a','b','x','t','w'),('a','b'),('t','w'),
                          [('a','x'),('b','x'),('x','t'),('x','w'),('a','t'),('b','w')]),
        ]
        count=0
        for ins in instances:
            model=compile_u(ins,relax=True)
            aub, bub, aeq, beq=[],[],[],[]
            for eq in model.equations:
                vector=np.zeros(len(model.variables))
                for j,c in eq.terms: vector[j]=c
                if eq.sense=='==': aeq.append(vector);beq.append(eq.rhs)
                elif eq.sense=='>=': aub.append(-vector);bub.append(-eq.rhs)
                else: aub.append(vector);bub.append(eq.rhs)
            regions=[]
            V=list(ins.V)
            for k in range(1,min(3,len(V))+1):
                regions+=list(itertools.combinations(V,k))
            rows=[]
            for L in regions:
                for direction in ('origin','destination'):
                    if region_excess(ins,L,direction)<=0:continue
                    E=eligible_frontier(ins,L,direction)
                    for n in range(len(E)+1):
                        for q in itertools.combinations(E,n):
                            rows.append(construct_row(ins,L,q,direction))
            for bits in itertools.product((0,1),repeat=len(V)):
                bounds=[(float(bit),float(bit)) for bit in bits]
                bounds +=[(0,None)]*(len(model.variables)-len(V))
                # The compiler always indexes y first; assert to avoid hidden drift.
                self.assertEqual([model.columns['y',v] for v in V],list(range(len(V))))
                for row in rows:
                    c=np.zeros(len(model.variables))
                    for j,val in row.as_compiled(model.columns).terms:c[j]=val
                    result=linprog(c,A_ub=np.array(aub) if aub else None,
                                   b_ub=np.array(bub) if bub else None,
                                   A_eq=np.array(aeq) if aeq else None,
                                   b_eq=np.array(beq) if beq else None,
                                   bounds=bounds,method='highs')
                    if result.status==2:continue # infeasible y pattern
                    self.assertEqual(result.status,0,(ins.V,row.signature,result.message))
                    self.assertGreaterEqual(result.fun + 1e-7,row.rhs,
                                            (ins.V,row.signature,bits,result.fun,row.rhs))
                    count+=1
        self.assertGreater(count,30)


if __name__=='__main__':
    unittest.main()
