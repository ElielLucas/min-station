"""Smoke AS-05: decisões sintéticas sem solver; NÃO é campanha nem prova matemática."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for directory in (ROOT, HERE, HERE.parent / 'alternative-formulations'):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

from as05_protocol import make_plan, sha256_file  # noqa: E402
from as05_gate import assess_gate  # noqa: E402


def main():
    path = ROOT/'results/benchmark/protocol.json'
    protocol = json.loads(path.read_text(encoding='utf-8'))
    plan = make_plan(protocol, as00_sha256=sha256_file(path),
                     manifest_sha256=sha256_file(ROOT/'instances/manifest.csv'))
    cases=[]
    for c in plan['pilot_cases']:
        cases.append({'name':c['name'],'raw_graph_id':c['raw_graph_id'],
                      'graph_source':c['graph_source'],
                      'contrasts':{'K_EFFECT':{'status':'MATCHED_COMPLETE'},
                                   'A_EFFECT':{'status':'MATCHED_COMPLETE'}},
                      'numerical_nondominance_violation':False,
                      'material_a_gain':True,'wall_acceptable':True,
                      'reproduction':{'status':'PENDING'},
                      'arm_statuses':{'U':'OPTIMAL_NUMERIC','U_K':'OPTIMAL_NUMERIC',
                                      'A2_K':'OPTIMAL_NUMERIC'}})
    pending=assess_gate(cases,plan)
    assert pending['verdict']=='INVESTIGATE'
    for c in cases:
        c['reproduction']={'status':'PASS','verified_seeds':[43,44]}
    completed=assess_gate(cases,plan)
    assert completed['verdict']=='GO'
    cases[0]['contrasts']['A_EFFECT']['status']='MATCHED_CENSORED'
    interrupted=assess_gate(cases,plan)
    assert interrupted['verdict']=='INVESTIGATE'
    print(f'AS05_SMOKE_PASS (100% sintético; gate pendente={pending["verdict"]}, '
          f'gate com evidências simuladas={completed["verdict"]}, censura={interrupted["verdict"]})')


if __name__=='__main__':
    main()
