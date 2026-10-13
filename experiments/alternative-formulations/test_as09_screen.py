import tempfile
import unittest
from pathlib import Path
from run_as09_screen import screen, report, main

class TestAS09Screen(unittest.TestCase):
    def test_denser_reachability_can_reduce_variable_count(self):
        rows=[{'nome':'dense.txt','n':'10','m':'2','r':'3','peso_min':'1','peso_max':'1',
               'arestas_nao_dirigidas':'9','n_arcos_alcance':'90','sha256':'x'}]
        result=screen(rows,['dense'])[0]
        self.assertEqual(result['u_variables'],100)
        self.assertEqual(result['c_variables'],10+2*3*9+10*3+2*4)
        self.assertEqual(result['LP_y_projection'],'UNPROVEN_ANALYTIC')
        self.assertEqual(result['K_generation'],'NOT_MEASURED')
        self.assertIn('não é benchmark completo',report([result]))

    def test_nonunit_instance_is_refused(self):
        rows=[{'nome':'weighted.txt','n':'4','m':'1','r':'2','peso_min':'1','peso_max':'2',
               'arestas_nao_dirigidas':'3','n_arcos_alcance':'7'}]
        self.assertEqual(screen(rows,['weighted'])[0]['status'],'NOT_APPLICABLE_NONUNIT_WEIGHTS')

    def test_output_append_only_and_manifest_traceable(self):
        with tempfile.TemporaryDirectory() as d:
            mf=Path(d)/'manifest.csv'
            mf.write_text('nome,n,m,r,peso_min,peso_max,arestas_nao_dirigidas,n_arcos_alcance,sha256\n'
                          'dense.txt,10,2,3,1,1,9,90,demo\n')
            out=Path(d)/'output'
            argv=['--manifest',str(mf),'--cases','dense','--output-dir',str(out)]
            self.assertEqual(main(argv),0)
            self.assertTrue((out/'screen.json').is_file())
            self.assertTrue((out/'screen.md').is_file())
            with self.assertRaises(FileExistsError):
                main(argv)

if __name__=='__main__':
    unittest.main()
