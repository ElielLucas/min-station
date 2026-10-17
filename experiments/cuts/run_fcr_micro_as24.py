"""AS24 synthetic-only evidence: canonical FC-R separator on AS23 rational LPs.

No real-world LP/MIP run and no LP reoptimization.  AS25 is a distinct,
preregistered experiment after the AS24 scientific gate.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.cuts.fcr_separator import scan
from experiments.cuts.verify_fcr_witness import build_system, recheck_saved

ROOT = Path(__file__).resolve().parents[2]


def _sha(file: Path) -> str:
    return hashlib.sha256(file.read_bytes()).hexdigest()


def run(evidence: Path | None = None, max_larger=12):
    path = evidence or ROOT/'results'/'benchmark'/'as23-fcr-witness-001.json'
    saved = json.loads(path.read_text(encoding='utf-8'))
    if saved.get('status')!='EXACT_CERTIFIED' or saved.get('kind')!='SYNTHETIC_ONLY':
        raise ValueError('AS23 evidence must be exact certified synthetic evidence')
    system = build_system()
    model = system['compiled']
    for model_name, add in (
        ('COMP_K',()), ('COMP_K_FCR',('FCR',)),
        ('COMP_K_C8',('C8',)), ('COMP_K_C8_FCR',('C8','FCR')),
        ('COMP_K_C6_C8',('C6','C8')),
        ('COMP_K_C6_C8_FCR',('C6','C8','FCR')),
    ):
        rows = system['base'] + [row for name in add for row in system[name]]
        recheck_saved(model,rows,saved['cases'][model_name])
    expected_graph = {'V': list(system['instance'].V), 'S': list(system['instance'].S),
                      'T': list(system['instance'].T),
                      'A_r': [list(arc) for arc in system['instance'].A_r],
                      'edges': [list(edge) for edge in sorted(system['edges'])],
                      'r': system['instance'].r}
    if saved.get('graph') != expected_graph or saved['graph_sha256'] != hashlib.sha256(
            json.dumps(expected_graph,sort_keys=True,separators=(',',':')).encode()).hexdigest():
        raise ValueError('AS23 graph/hash differs from current compiled witness')
    sha_map = {}
    for name in ('fcr_rows.py','fcr_regions.py','fcr_separator.py','run_fcr_micro_as24.py','test_as24_fcr.py'):
        rel = 'experiments/cuts/'+name
        sha_map[rel] = _sha(ROOT/rel)
    try:
        rev = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True,
                                       stderr=subprocess.DEVNULL).strip()
        dirty = bool(subprocess.check_output(
            ['git','status','--porcelain','--untracked-files=normal','--',
             *sha_map.keys()],cwd=ROOT,text=True,stderr=subprocess.DEVNULL).strip())
    except (OSError,subprocess.CalledProcessError):
        rev,dirty = None,None
    cases={}
    ins=system['instance']
    for case_name in ('COMP_K','COMP_K_FCR','COMP_K_C8','COMP_K_C8_FCR','COMP_K_C6_C8','COMP_K_C6_C8_FCR'):
        vector=tuple(F(v) for v in saved['cases'][case_name]['primal'])
        y={v:vector[model.columns['y',v]] for v in ins.V}
        f={(u,v):vector[model.columns['F',u,v]] for u,v in ins.A_r}
        results={}
        for label,larger in (('singleton',False),('singleton_plus_heuristic',True)):
            scan_result=scan(ins,y,f,include_larger=larger,max_larger=max_larger,
                             tolerance=1e-12, max_cuts=100)
            if not scan_result.stats['singleton_complete']:
                raise AssertionError('micro run unexpectedly incomplete singletons')
            results[label]={
                'status':scan_result.status,
                'stats':scan_result.stats,
                'cuts':[r.algebraic_certificate for r in scan_result.cuts],
                'events':scan_result.events,
            }
            # Timing is observational and platform-dependent, not part of the
            # exact mathematical evidence.
        cases[case_name]={'lp_objective_as23':saved['cases'][case_name]['objective'],
                          'separator_scans':results}
    return {
        'schema_version':'as24-fcr-micro-v1',
        'kind':'SYNTHETIC_ONLY',
        'status':'MICRO_VALIDATION_COMPLETED',
        'gate':'PENDING_INDEPENDENT_REVIEW',
        'source_commit':rev,
        'source_has_tracked_modifications':dirty,
        'source_sha256':sha_map,
        'as23_evidence_sha256':_sha(path),
        'graph_sha256_as23':saved['graph_sha256'],
        'scope':('Complete separation over all strict-excess singletons; '
                 'exact Q per fixed region; deterministic bounded selected pairs; '
                 'no claim of global region completeness or benchmark gain'),
        'case_count':len(cases),
        'cases':cases,
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',default='results/benchmark/as24-fcr-micro-001.json')
    parser.add_argument('--as23-evidence',default=None)
    parser.add_argument('--max-larger',type=int,default=12)
    args=parser.parse_args()
    report=run(Path(args.as23_evidence) if args.as23_evidence else None,max_larger=args.max_larger)
    destination=Path(args.output)
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text(json.dumps(report,indent=2,sort_keys=True,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'status':report['status'],'gate':report['gate'],
                      'cases':report['case_count'],
                      'singletons_verified':sum(v['separator_scans']['singleton']['stats']['singletons_checked']
                                                 for v in report['cases'].values()),
                      'cuts_on_COMP_K':len(report['cases']['COMP_K']['separator_scans']['singleton']['cuts']),
                      'output':str(destination)},ensure_ascii=False))


if __name__=='__main__':main()
