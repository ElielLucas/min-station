"""AS09 T3 pre-screen, no solver: theoretical sizes from frozen manifest metadata.

Does NOT purport to measure full K construction, runtime or actual RSS. Those
are explicit prerequisites for a cost-benefit decision in the subsequent pilot.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CASES = (
    'mapf-room-32-32-4-m10-f8',
    'mapf-den312d-m50-f2-rho',
    'vienna-I056-regiao-f4',
    'puc-cc9-2p-seed-r1',
    'puc-w3c571-seed-r1',
)


def screen(rows, case_ids):
    selected = []
    for case in case_ids:
        matches = [row for row in rows if Path(row['nome']).stem == case]
        if len(matches) != 1:
            raise ValueError(f'Caso ausente ou duplicado no manifesto: {case}')
        r = matches[0]
        if float(r['r']) != int(float(r['r'])) or int(float(r['r'])) < 1:
            selected.append({'case':case, 'status':'NOT_APPLICABLE_NONINTEGER_R'})
            continue
        if float(r.get('peso_min') or 0) != 1 or float(r.get('peso_max') or 0) != 1:
            selected.append({'case':case, 'status':'NOT_APPLICABLE_NONUNIT_WEIGHTS'})
            continue
        n = int(r['n']); m = int(r['m']); rad = int(float(r['r']))
        e = int(r['arestas_nao_dirigidas']); a = int(r['n_arcos_alcance'])
        u = n+a
        c = n+2*rad*e+n*rad+m*(rad+1)
        selected.append({
            'case':case, 'status':'ESTIMATED_PRE_PRESOLVE',
            'source_sha256':r.get('sha256',''),
            'n':n,'m':m,'r':rad,'physical_edges':e,'reachability_arcs_manifest':a,
            'u_variables':u, 'c_variables':c,
            'u_rows_without_K':3*n,
            'c_rows_without_K':n*(rad+1)+m+n,
            'c_over_u_variables':round(c/u,6),
            'estimated_variable_reduction_pct':round(100*(1-c/u),3),
            'K_generation':'NOT_MEASURED',
            'reachability_generation':'NOT_MEASURED',
            'model_build_time':'NOT_MEASURED',
            'model_solve_time':'NOT_MEASURED',
            'memory_rss':'NOT_MEASURED',
            'LP_y_projection':'UNPROVEN_ANALYTIC',
        })
    return selected


def report(rows):
    parts = [
        '# AS09 — Triagem estrutural (não é benchmark completo)', '',
        '| Instância | U variáveis | C variáveis | C/U | Redução estimada | Linhas U sem K | Linhas C sem K |',
        '|---|---:|---:|---:|---:|---:|---:|',
    ]
    for row in rows:
        if row['status']!='ESTIMATED_PRE_PRESOLVE':
            parts.append(f"| {row['case']} | — | — | — | {row['status']} | — | — |")
        else:
            parts.append(f"| {row['case']} | {row['u_variables']:,} | {row['c_variables']:,} | "
                         f"{row['c_over_u_variables']:.3f} | {row['estimated_variable_reduction_pct']:.1f}% | "
                         f"{row['u_rows_without_K']:,} | {row['c_rows_without_K']:,} |")
    parts += [
        '', '## Interpretação e limites', '',
        '- Valores derivados exclusivamente do manifesto e das fórmulas exatas de dimensionamento; ainda não incluem presolve.',
        '- A geração de A_r, preparação de K, construção de modelos, tempo total e memória **não foram medidos**.',
        '- As duas formulações recebem os mesmos cortes K; todas as linhas de K devem ser contadas no experimento completo.',
        '- Não foi provada nem certificada a equivalência de projeções LP por este pré-screen.',
        '- Uma razão C/U baixa autoriza apenas um piloto, nunca uma alegação de desempenho superior.',
        '',
    ]
    return '\n'.join(parts)


def main(argv=None):
    p=argparse.ArgumentParser(description='AS09 screen de dimensão C vs U antes de investimento de solução')
    p.add_argument('--manifest',type=Path,default=ROOT/'instances/manifest.csv')
    p.add_argument('--cases',nargs='+',default=list(DEFAULT_CASES))
    p.add_argument('--output-dir',type=Path,default=ROOT/'results/benchmark/as09-screen-001')
    a=p.parse_args(argv)
    raw=a.manifest.read_bytes()
    rows=list(csv.DictReader(raw.decode('utf8').splitlines()))
    screened=screen(rows,a.cases)
    payload={'protocol':'AS09-SCREEN-v1','manifest_sha256':hashlib.sha256(raw).hexdigest(),
             'cases':screened,'gate':'SCREEN_ONLY_NO_SCIENTIFIC_PROMOTION'}
    dest=a.output_dir
    if dest.exists() and any(dest.iterdir()):
        raise FileExistsError('A saída já contém artefatos; use uma pasta nova')
    dest.mkdir(parents=True,exist_ok=True)
    (dest/'screen.json').write_text(json.dumps(payload,indent=2,ensure_ascii=False,sort_keys=True)+'\n',encoding='utf8')
    (dest/'screen.md').write_text(report(screened),encoding='utf8')
    for row in screened:
        if row['status']=='ESTIMATED_PRE_PRESOLVE':
            print('AS09_SCREEN',row['case'],'U',row['u_variables'],'C',row['c_variables'],
                  'REDUCTION_PCT',row['estimated_variable_reduction_pct'])
    print('AS09_SCREEN_ONLY',dest)
    return 0

if __name__=='__main__':
    raise SystemExit(main())
