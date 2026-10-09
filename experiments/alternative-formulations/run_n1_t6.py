#!/usr/bin/env python3
"""N1-T6: freeze -> generate -> certify -> measure -> report.

A ordem protege a pre-registracao: nenhum grafo novo e gerado antes de freeze.
Nao altera T5, os modelos, os dados historicos, nem executa o gate T7.
Uso: PYTHONHASHSEED=0 python experiments/alternative-formulations/run_n1_t6.py <phase>
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import sys
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
for x in (HERE, ROOT, ROOT / 'experiments' / 'cuts', ROOT / 'experiments' / 'structural'):
    if str(x) not in sys.path:
        sys.path.insert(0, str(x))

from n1_t6_pairs import RECIPES, build_pair, shortcut_diagnostics

EPS = 1e-6
RESULTS = ROOT / 'results' / 'alternative-formulations'
DOCS = ROOT / 'docs' / 'technical' / 'plans' / 'execucao'
FREEZE = HERE / 'n1-t6-freeze.json'
GENERATED = RESULTS / 'n1-t6-pares.json'
CERT = RESULTS / 'n1-t6-certificados.json'
MEASURED = RESULTS / 'n1-t6-diagnostico.csv'
REPORT = DOCS / 'n1-t6-diagnostico.md'
# O timeout de 600 s aplica-se a cada resolucao, NAO ao pre-processamento.
TIME_LIMIT = 600
N_MAX, MAX_W, ARC_CAP = 21, 200_000, 5_000_000
FIELDS = ['pair_id', 'family', 'role', 'name', 'n', 'm', 'r', 'graph_hash',
          'k_hash', 'n_K', 'n_W_raw', 'n_W_util', 'arc_bound',
          'opt', 'opt_source', 'core_ip', 'lp_base', 'lp_comp',
          'lp_fcc', 'lp_fcc_k', 'lp_fc3', 'lp_fc3_k', 'gamma', 'B0',
          'delta_fcc_k', 'delta_trio', 'delta_trio_raw',
          'status_core_ip', 'status_lp_base', 'status_lp_comp',
          'status_lp_fcc', 'status_lp_fcc_k', 'status_lp_fc3', 'status_lp_fc3_k',
          'reason_core_ip', 'reason_lp_base', 'reason_lp_comp',
          'reason_lp_fcc', 'reason_lp_fcc_k', 'reason_lp_fc3', 'reason_lp_fc3_k',
          'pair_status', 'shortcut_review']


def jbytes(obj):
    return (json.dumps(obj, sort_keys=True, indent=2, ensure_ascii=False) + '\n').encode('utf8')


def digest_bytes(b):
    return hashlib.sha256(b).hexdigest()


def digest_file(p):
    return digest_bytes(p.read_bytes())


def load(p):
    return json.loads(p.read_text(encoding='utf8'))


def save_new(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('xb') as f:
        f.write(jbytes(obj))
    print('CRIADO', p, flush=True)


def read_csv(p):
    with p.open(newline='', encoding='utf8') as f:
        return list(csv.DictReader(f))


def write_csv_new(p, rows):
    buffer = io.StringIO(newline='')
    writer = csv.DictWriter(buffer, fieldnames=FIELDS, extrasaction='ignore')
    writer.writeheader()
    writer.writerows(rows)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('xb') as f:
        f.write(buffer.getvalue().encode('utf8'))


def validate_previous():
    """Testa gatilho SEM contar valores NOT MEASURED como zero."""
    import run_n1_t5 as t5
    t5.require_attest()  # confirma hashes do freeze, modelos e reproducao F3
    old = read_csv(t5.OUT)
    if len(old) != 18 or tuple(r['instancia'] for r in old) != t5.NAMES:
        raise RuntimeError('T5 nao tem 18 linhas na ordem congelada')
    witness = load(t5.WITNESSES)
    if witness.get('state') != 'COMPUTATIONALLY VERIFIED':
        raise RuntimeError('testemunhas T5 incompletas')
    eligible = []
    for row in old:
        if (row['gamma'] not in ('', 'NOT MEASURED') and
            row['lp_fcc_k'] not in ('', 'NOT MEASURED') and
            row['opt'] not in ('', 'NOT MEASURED') and
            row['status_lp_fcc_k'] == 'COMPUTATIONALLY VERIFIED' and
            float(row['gamma']) > EPS and
            float(row['lp_fcc_k']) < float(row['opt']) - EPS):
            eligible.append({'instancia':row['instancia'], 'family':row['tipo'],
                             'gamma':float(row['gamma']),
                             'residual':float(row['opt'])-float(row['lp_fcc_k'])})
    families = sorted({r['family'] for r in eligible})
    if len(families) >= 2:
        raise RuntimeError(f'Gatilho T6 NAO ativado: familias {families}')
    return {'eligible_rows': eligible, 'families': families,
            'n_distinct': len(families), 'triggered': True,
            'source_hashes': {str(p.relative_to(ROOT)): digest_file(p) for p in (
                t5.FREEZE, t5.F3_ATTEST, t5.OUT, t5.WITNESSES, t5.REPORT)}}


def freeze():
    if any(p.exists() for p in (FREEZE, GENERATED, CERT, MEASURED, REPORT)):
        raise RuntimeError('Artefatos T6 existentes; nao congelar sobre dados anteriores')
    gate = validate_previous()
    if not 1 <= len(RECIPES) <= 12 or len({r['id'] for r in RECIPES}) != len(RECIPES):
        raise AssertionError('protocolo exige de 1 a 12 pares unicos')
    inputs = ['experiments/alternative-formulations/n1_t6_pairs.py',
              'experiments/alternative-formulations/run_n1_t6.py',
              'experiments/cuts/synthetic.py', 'ms_utils.py',
              'experiments/cuts/independent_validator.py',
              'experiments/alternative-formulations/fcc.py',
              'experiments/alternative-formulations/fcc_k.py',
              'experiments/alternative-formulations/fc3.py',
              'specs/proxima-fase-n1-informacao-compatibilidade/spec.md']
    data = {'task':'N1-T6', 'status':'FROZEN',
            'frozen_utc':datetime.now(timezone.utc).isoformat(),
            'gate_t5':gate, 'pairs': list(RECIPES),
            'obstruction_method': 'assinatura de arestas obrigatorias por familia',
            'paired_control_method': 'uma remocao e uma adicao de aresta unitaria',
            'certificate': 'independent_validator.opt_por_enumeracao, n<=10; witness C',
            'terminal_shortcuts': 'arcos diretos S->T e estacoes em terminais; OPT=0 exclui somente a variante de obstrucao; controle com OPT=0 e valido',
            'non_replacement': 'par excluido permanece excluido; nenhum par adicional',
            'caps': {'n':10, 'pairs':12, 'max_W':MAX_W,
                     'network_arcs':ARC_CAP, 'time_limit_per_lp_seconds':TIME_LIMIT},
            'solver':{'seed':42, 'threads':1, 'hashseed':'0','tolerance':EPS},
            'source_hashes': {name:digest_file(ROOT / name) for name in inputs},
            'measurement_arms':['lp_base','lp_comp','core_ip','lp_fcc','lp_fcc_k',
                                'lp_fc3','lp_fc3_k','OPT']}
    save_new(FREEZE, data)
    print('N1-T6 CONGELADA: nenhum par gerado nem LP medido')


def checked_freeze():
    if os.environ.get('PYTHONHASHSEED') != '0':
        raise RuntimeError('Execute com PYTHONHASHSEED=0')
    frozen = load(FREEZE)
    if frozen['status'] != 'FROZEN' or frozen['pairs'] != list(RECIPES):
        raise RuntimeError('pre-registro alterado')
    for name, expected in frozen['source_hashes'].items():
        if digest_file(ROOT / name) != expected:
            raise RuntimeError('fonte alterada apos congelamento: ' + name)
    for name, expected in frozen['gate_t5']['source_hashes'].items():
        if digest_file(ROOT / name) != expected:
            raise RuntimeError('evidencia T5 alterada apos congelamento: ' + name)
    return frozen


def pair_structure(pair):
    from n1_t6_pairs import _obstruction_holds
    a, b = pair['graphs']
    recipe = pair['recipe']
    ae, be = set(map(tuple,a['edges'])), set(map(tuple,b['edges']))
    if not _obstruction_holds(recipe,ae) or _obstruction_holds(recipe,be):
        raise RuntimeError('obstrucao nao reproduzida: ' + recipe['id'])
    if (a['V'],a['S'],a['T'],a['r']) != (b['V'],b['S'],b['T'],b['r']):
        raise RuntimeError('par nao comparavel')
    if len(a['V'])>10 or len(a['S'])!=3 or len(ae)!=len(be):
        raise RuntimeError('dimensoes fora da spec')
    return True


def generate():
    pre = checked_freeze()
    if any(p.exists() for p in (GENERATED,CERT,MEASURED,REPORT)):
        raise RuntimeError('dados T6 ja existem')
    pairs=[]
    for recipe in pre['pairs']:
        a,b=build_pair(recipe)
        pair={'recipe':recipe,'graphs':[a,b]}
        pair_structure(pair)
        for g in pair['graphs']:
            g['shortcut_diagnostics']=shortcut_diagnostics(g)
            g['graph_hash']=digest_bytes(jbytes({k:g[k] for k in ('S','T','V','r','edges','A_r')}))
        pairs.append(pair)
        print('GERADO', recipe['id'], 'n=',len(a['V']),'m=',len(a['S']),flush=True)
    save_new(GENERATED, {'freeze_hash':digest_file(FREEZE),
                         'pair_count':len(pairs),'pairs':pairs})


def read_pairs():
    pre=checked_freeze()
    data=load(GENERATED)
    if data['freeze_hash']!=digest_file(FREEZE) or len(data['pairs'])!=len(pre['pairs']):
        raise RuntimeError('grafo nao corresponde ao freeze')
    for item,recipe in zip(data['pairs'],pre['pairs']):
        a,b=build_pair(recipe)
        for actual,exp in zip(item['graphs'],(a,b)):
            if actual['edges']!=exp['edges'] or actual['A_r']!=exp['A_r']:
                raise RuntimeError('grafo alterado: '+recipe['id'])
        pair_structure(item)
    return data


def certify():
    data=read_pairs()
    if CERT.exists() or MEASURED.exists() or REPORT.exists():
        raise RuntimeError('certificados/medicoes ja existem')
    from independent_validator import opt_por_enumeracao, viavel
    records=[]
    for pair in data['pairs']:
        results=[]
        for graph in pair['graphs']:
            S,T,V,adj,r=[graph[k] for k in ('S','T','V','adj','r')]
            opt=opt_por_enumeracao(S,T,V,adj,r)
            if opt is None:
                results.append({'name':graph['name'],'status':'EXCLUDED',
                                'reason':'nenhuma instalacao viavel','opt':None})
                continue
            witness=next((list(C) for C in combinations(V,opt) if viavel(S,T,V,adj,r,C)),None)
            if witness is None:
                raise AssertionError('OPT sem instalacao testemunha')
            nonterminal=[v for v in V if v not in set(S)|set(T)]
            opt_without_terminals=next((k for k in range(len(nonterminal)+1)
                                        if any(viavel(S,T,V,adj,r,C)
                                               for C in combinations(nonterminal,k))),None)
            # OPT=0 no controle e permitido: e justamente o contrafactual sem barreira.
            valid = opt > 0 or graph['role']=='control'
            results.append({'name':graph['name'],'status':'CERTIFIED' if valid else 'EXCLUDED',
                            'reason':('' if opt>0 else ('controle com atalho intencional, OPT=0'
                                    if graph['role']=='control' else 'obstrucao perdida, OPT=0')),
                            'opt':opt,'C_star':witness, 'method':'opt_por_enumeracao',
                            'n_subsets_at_most':2**len(V),
                            'opt_without_terminal_stations':opt_without_terminals,
                            'terminal_station_shortcut':(opt_without_terminals is None or
                                                        opt_without_terminals>opt),
                            'direct_terminal_arcs': graph['shortcut_diagnostics']['direct_origin_destination_arcs']})
        if any(r['status']!='CERTIFIED' for r in results):
            status='EXCLUDED'
        else:
            status='CERTIFIED'
        records.append({'pair_id':pair['recipe']['id'],'family':pair['recipe']['family'],
                        'pair_status':status,'variants':results})
        print('CERTIFICADO',pair['recipe']['id'], status,
              [(r['name'],r['opt']) for r in results], flush=True)
    save_new(CERT,{'freeze_hash':digest_file(FREEZE),
                   'generated_hash':digest_file(GENERATED),'pairs':records})


def checked_certificates():
    data=read_pairs()
    cert=load(CERT)
    if cert['freeze_hash']!=digest_file(FREEZE) or cert['generated_hash']!=digest_file(GENERATED):
        raise RuntimeError('certificados nao correspondem aos grafos')
    if len(cert['pairs'])!=len(data['pairs']):
        raise RuntimeError('certificados incompletos')
    for pair,rec in zip(data['pairs'],cert['pairs']):
        if pair['recipe']['id']!=rec['pair_id'] or len(rec['variants'])!=2:
            raise RuntimeError('inconsistencia na certificacao')
    return data,cert


def write_checkpoint(rows):
    """Checkpoint atomico: somente saida T6, sem alterar T5 ou o protocolo."""
    buffer = io.StringIO(newline='')
    writer = csv.DictWriter(buffer, fieldnames=FIELDS, extrasaction='ignore')
    writer.writeheader()
    writer.writerows(rows)
    MEASURED.parent.mkdir(parents=True, exist_ok=True)
    temp = MEASURED.with_suffix('.csv.tmp')
    with temp.open('wb') as f:
        f.write(buffer.getvalue().encode('utf8'))
    os.replace(temp, MEASURED)


def measure():
    """Pode retomar apenas o SUFIXO nao medido da MESMA lista congelada."""
    pairs, cert = checked_certificates()
    if REPORT.exists():
        raise RuntimeError('relatorio T6 ja existe; nao repetir medicao')
    jobs = [(g, proof, c['pair_status'])
            for pair, c in zip(pairs['pairs'], cert['pairs'])
            for g, proof in zip(pair['graphs'], c['variants'])]
    rows = read_csv(MEASURED) if MEASURED.exists() else []
    if len(rows) > len(jobs):
        raise RuntimeError('CSV T6 maior que a lista congelada')
    for i, row in enumerate(rows):
        g, proof, status = jobs[i]
        if (row['name'] != g['name'] or row['graph_hash'] != g['graph_hash'] or
            row['pair_status'] != status or
            (row['opt'] != '' and abs(float(row['opt']) - proof['opt']) > EPS)):
            raise RuntimeError('checkpoint T6 nao corresponde ao protocolo: linha '+str(i+1))
    if len(rows) == len(jobs):
        print('T6 ja possui todas as linhas; execute report')
        return
    if rows:
        print('RETOMANDO T6: preservando', len(rows), 'linhas concluidas', flush=True)
    for g, proof, status in jobs[len(rows):]:
        print('MEDINDO T6',g['name'],flush=True)
        row = measure_one(g,proof,status)
        rows.append(row)
        write_checkpoint(rows)
        print(' ',row['pair_status'],'OPT',row['opt'],
              'FCC+K',row['lp_fcc_k'],'FC3+K',row['lp_fc3_k'], flush=True)
    print('T6 medidas:',len(rows),'linhas; executar report para validar completude')


def measure_one(g,proof,pair_status):
    from gurobipy import GRB
    from fcc import grafo_H,enumerar_conexos,B_de,construir_modelo_fcc,CapExceeded
    from fc3 import (construir_modelo_fc3,build_fc3_plus_k,
                     bound_network_arcs,FC3SizeExceeded)
    from fcc_k import prepare_k,build_fcc_plus_k
    from harness import measure_lp
    from medir import nucleo
    S,T,V,adj,A_r,r=[g[k] for k in ('S','T','V','adj','A_r','r')]
    row={k:'' for k in FIELDS}
    row.update(pair_id=g['pair_id'],family=g['family'],role=g['role'],name=g['name'],
               n=len(V),m=len(S),r=r,graph_hash=g['graph_hash'],
               opt=proof['opt'] if proof['opt'] is not None else '',
               opt_source='opt_por_enumeracao' if proof['opt'] is not None else '',
               pair_status=pair_status,
               shortcut_review='terminal_station_shortcut='+str(proof.get('terminal_station_shortcut')))
    for arm in ('core_ip','lp_base','lp_comp','lp_fcc','lp_fcc_k','lp_fc3','lp_fc3_k'):
        row['status_'+arm]='NOT MEASURED'
    if pair_status=='EXCLUDED':
        for arm in ('core_ip','lp_base','lp_comp','lp_fcc','lp_fcc_k','lp_fc3','lp_fc3_k'):
            row['reason_'+arm]='par excluido antes de medir: '+proof.get('reason','variante par')
        return row
    K,k_hash,counts=prepare_k(S,T,V,adj,A_r,r)
    row['k_hash'],row['n_K']=k_hash,len(K)
    for field,cuts in [('lp_base',[]),('lp_comp',K)]:
        res=measure_lp(S,T,V,A_r,'cont',cuts,seed=42,threads=1,time_limit=TIME_LIMIT)
        if res['lp_bound'] is not None and res['lp_status']==GRB.OPTIMAL:
            row[field]=float(res['lp_bound']); row['status_'+field]='COMPUTATIONALLY VERIFIED'
        else:
            row['reason_'+field]='LP status='+str(res['lp_status'])
    try:
        row['core_ip']=float(nucleo(S,T,V,adj,r))
        row['status_core_ip']='COMPUTATIONALLY VERIFIED'
    except RuntimeError as exc:
        row['reason_core_ip']='sem otimo certificado: '+str(exc)
    nW=''
    try:
        nbr=grafo_H(V,A_r)
        Ws,_=enumerar_conexos(nbr,V,MAX_W+1)
        nW=len(Ws)
        row['n_W_raw']=nW
        if nW>MAX_W:
            reason=f'n_W_raw={nW}>max_W={MAX_W}'
            for arm in ('lp_fcc','lp_fcc_k','lp_fc3','lp_fc3_k'):
                row['reason_'+arm]=reason
        else:
            row['n_W_util']=sum(bool(set(S)&B_de(W,nbr)) and bool(set(T)&B_de(W,nbr)) for W in Ws)
            row['arc_bound']=bound_network_arcs(len(S),row['n_W_util'])
            for arm,fn in (
                ('lp_fcc', lambda: construir_modelo_fcc(S,T,V,A_r,forma='separada',max_W=MAX_W)),
                ('lp_fcc_k',lambda:build_fcc_plus_k(S,T,V,adj,A_r,r,K=K,k_hash=k_hash,max_W=MAX_W))):
                _solve(row,arm,fn,GRB)
            if row['arc_bound']>ARC_CAP:
                reason=f'network_arc_bound={row["arc_bound"]}>cap={ARC_CAP}'
                for arm in ('lp_fc3','lp_fc3_k'):
                    row['reason_'+arm]=reason
            else:
                for arm,fn in (
                    ('lp_fc3',lambda:construir_modelo_fc3(S,T,V,A_r,max_W=MAX_W,max_network_arcs=ARC_CAP)),
                    ('lp_fc3_k',lambda:build_fc3_plus_k(S,T,V,adj,A_r,r,K=K,k_hash=k_hash,
                                                      max_W=MAX_W,max_network_arcs=ARC_CAP))):
                    _solve(row,arm,fn,GRB)
    except (CapExceeded,FC3SizeExceeded) as exc:
        for arm in ('lp_fcc','lp_fcc_k','lp_fc3','lp_fc3_k'):
            if row['status_'+arm]=='NOT MEASURED' and not row['reason_'+arm]:
                row['reason_'+arm]=str(exc)
    opt=row['opt']
    for arm in ('core_ip','lp_base','lp_comp','lp_fcc','lp_fcc_k','lp_fc3','lp_fc3_k'):
        if row[arm]!='' and row[arm]>opt+EPS:
            raise RuntimeError(g['name']+': '+arm+' excedeu OPT certificado')
    for strong,weak in (('lp_fcc_k','lp_fcc'),('lp_fc3','lp_fcc'),
                        ('lp_fc3_k','lp_fcc_k'),('lp_fc3_k','lp_fc3')):
        if row[strong]!='' and row[weak]!='' and row[strong]+EPS<row[weak]:
            raise RuntimeError(g['name']+': dominancia LP violada '+strong+' / '+weak)
    if row['core_ip']!='' and row['lp_comp']!='':
        row['B0']=max(row['core_ip'],row['lp_comp'])
        row['gamma']=opt-row['core_ip']
        if row['lp_fcc_k']!='':
            row['delta_fcc_k']=row['lp_fcc_k']-row['B0']
    if row['lp_fc3_k']!='' and row['lp_fcc_k']!='':
        row['delta_trio']=row['lp_fc3_k']-row['lp_fcc_k']
    if row['lp_fc3']!='' and row['lp_fcc']!='':
        row['delta_trio_raw']=row['lp_fc3']-row['lp_fcc']
    return row


def _solve(row,arm,factory,GRB):
    model=None
    try:
        model,_y,_extra,_meta=factory()
        model.Params.OutputFlag=0
        model.Params.Seed=42
        model.Params.Threads=1
        model.Params.Method=2
        model.Params.TimeLimit=TIME_LIMIT
        model.optimize()
        if model.Status==GRB.OPTIMAL:
            row[arm]=float(model.ObjVal)
            row['status_'+arm]='COMPUTATIONALLY VERIFIED'
        else:
            row['reason_'+arm]='sem certificado LP otimo: status='+str(model.Status)
    finally:
        if model is not None:
            model.dispose()


def report():
    pairs,cert=checked_certificates()
    if not MEASURED.exists() or REPORT.exists():
        raise RuntimeError('medicoes ausentes ou relatorio ja existe')
    rows=read_csv(MEASURED)
    expected=[g['name'] for pair in pairs['pairs'] for g in pair['graphs']]
    if [r['name'] for r in rows]!=expected:
        raise RuntimeError('CSV T6 parcial ou ordem diferente: gate T7 proibido')
    text=['# N1-T6 — Microinstancias condicionais', '',
          '**Estado:** `COMPUTATIONALLY VERIFIED` somente para valores medidos; '
          '`NOT MEASURED` para caps e timeouts. Este documento NAO aplica o gate N1-T7.', '',
          f'**Freeze SHA-256:** `{digest_file(FREEZE)}`',
          f'**Grafos SHA-256:** `{digest_file(GENERATED)}`',
          f'**Certificados SHA-256:** `{digest_file(CERT)}`',
          f'**Pares pre-registrados:** {len(pairs["pairs"])}; sem substituicoes pos-medicao.', '',
          '## Protocolo e verificacao', '',
          '- Cada par conserva V, S, T, n, m, r e o numero de arestas.',
          '- O controle troca exatamente uma aresta unitaria definida no freeze.',
          '- OPT certificado por `opt_por_enumeracao` (independente dos LPs).',
          '- Atalhos e uso de terminais como estacoes auditados no JSON de certificados.',
          '- O controle pode conter um atalho INTENCIONAL; nao e uma prova de ganho.', '',
          '## Resultados', '',
          '| Par | Familia | Variante | OPT | core IP | FCC+K | FC3+K | Δ trio | Status |',
          '|---|---|---|---:|---:|---:|---:|---:|---|']
    def display(v):
        return v if v not in ('',None) else 'NOT MEASURED'
    for r in rows:
        text.append('| '+' | '.join(map(str,[r['pair_id'],r['family'],r['role'],
                  display(r['opt']),display(r['core_ip']),display(r['lp_fcc_k']),
                  display(r['lp_fc3_k']),display(r['delta_trio']),r['pair_status']]))+' |')
    text += ['', '## Limites de interpretacao', '',
             '- Resultados somente para os pares pre-registrados; nao ha busca sistematica.',
             '- Uma diferenca positiva no LP nao e ganho computacional de tempo.',
             '- Nenhuma linha com `NOT MEASURED` pode ser tratada como ganho zero.',
             '- N1-T7 deve aplicar o gate PRE-EXISTENTE da spec, combinando T5 e T6.',
             '- Se nenhuma promocao satisfizer os criterios, parar sem inventar outra familia.', '']
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    with REPORT.open('x',encoding='utf8') as f:
        f.write('\n'.join(text))
    print('RELATORIO',REPORT)
    print('N1-T6 concluida; gate N1-T7 ainda pendente')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase',choices=('freeze','generate','certify','measure','report'))
    args=parser.parse_args()
    if os.environ.get('PYTHONHASHSEED')!='0':
        raise RuntimeError('Use PYTHONHASHSEED=0')
    dict(freeze=freeze,generate=generate,certify=certify,measure=measure,report=report)[args.phase]()


if __name__=='__main__':
    main()
