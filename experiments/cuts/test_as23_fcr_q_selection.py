"""AS23 acceptance: fixed-region Q minimizer versus exact exhaustive subsets."""
import itertools
import unittest
from fractions import Fraction as F

from verify_fcr_witness import (build_system, fcr_region_row, row_value,
                                select_q_fixed_region)


class RegionMinimizerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.system=build_system()

    def compare_all(self, direction, region, y, flows):
        system=self.system
        ins=system['instance']
        if direction=='origin':
            eligible=sorted({v for u,v in ins.A_r if u in region and v not in region}-set(ins.T))
        else:
            eligible=sorted({u for u,v in ins.A_r if v in region and u not in region}-set(ins.S))
        qstar=select_q_fixed_region(ins,region,y,flows,direction)
        values=[]
        point=[F(0)]*len(system['compiled'].variables)
        for v, weight in y.items():point[system['compiled'].columns['y',v]]=F(weight)
        for (u,v), weight in flows.items():point[system['compiled'].columns['F',u,v]]=F(weight)
        for size in range(len(eligible)+1):
            for sub in itertools.combinations(eligible,size):
                row=fcr_region_row(ins,system['compiled'].columns,region,sub,direction)
                values.append((row_value(row,point),tuple(sub)))
        qrow=fcr_region_row(ins,system['compiled'].columns,region,qstar,direction)
        self.assertEqual(row_value(qrow,point),min(v for v,_ in values))
        self.assertIn(qstar,[sub for v,sub in values if v==min(x for x,_ in values)])
        return qstar

    def test_origin_exhaustive_including_ties(self):
        y={'x11':F(1,2),'x12':F(1,4),'x13':F(1,3)}
        flow={('a1','x11'):F(3,4),('a1','x12'):F(1,4),
              ('a1','x13'):F(1,3),('a1','c1'):F(1,5)}
        self.assertEqual(self.compare_all('origin',('a1',),y,flow),('x11',))

    def test_destination_exhaustive_including_ties(self):
        y={'x11':F(1,4),'x21':F(1,3),'x31':F(1,2),'x41':F(1,4)}
        flow={('x11','d1'):F(1,2),('x21','d1'):F(1,3),
              ('x31','d1'):F(1,10),('x41','d1'):F(1,4)}
        self.assertEqual(self.compare_all('destination',('d1',),y,flow),('x11',))

    def test_balanced_region_rejected(self):
        ins=self.system['instance']
        with self.assertRaises(ValueError):
            select_q_fixed_region(ins,('a1','c1'),{}, {},'origin')
        with self.assertRaises(ValueError):
            select_q_fixed_region(ins,('a1','c1'),{}, {},'destination')

    def test_multi_vertex_region_and_demand_two(self):
        y={v:F(1,10) for v in self.system['instance'].V}
        flow={('a1','x11'):F(1,2),('a2','x21'):F(1,2),
              ('a1','c1'):F(1,10)}
        self.assertEqual(self.compare_all('origin',('a1','a2'),y,flow),('x11','x21'))
        y={'x11':F(1,10),'x21':F(1,10)}
        flow={('x11','d1'):F(1,2),('x21','d2'):F(1,2)}
        self.assertEqual(self.compare_all('destination',('d1','d2'),y,flow),('x11','x21'))


if __name__ == '__main__':unittest.main()
