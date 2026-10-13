#!/usr/bin/env python3
"""AS-08/LB — investigação exploratória de limites racionais intermediários.

Experimento isolado: três casos de desenvolvimento, COMP+K LP versus limite
inferior exato de LP(B+K). Não resolve MIP, não altera planos v1/v2.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for folder in (HERE, ROOT, ROOT/'experiments/formulation-comparison'):
    if str(folder) not in sys.path:
        sys.path.insert(0, str(folder))

import fc_instances
from fc_budget import run_bounded
from as02_model_a import Instance
from as04_arms import k_digest
from as05_diag_core import _timed_k
from as08_column_generation import verify_rational_certificate
from run_as08_b_pilot import (
    SCHEMA as PARENT_SCHEMA, _worker, atomic_progress_write, digest, json_write,
    make_plan as make_parent_plan, progress_record, sha, verify_progress,
)

SCHEMA = 'AS08-LB-PROBE-PLAN-v1'
RESULT = 'AS08-LB-PROBE-RESULT-v1'
MANIFEST = 'AS08-LB-PROBE-MANIFEST-v1'
SELECTED = (
    'mapf-room-32-32-4-m10-f8',
    'puc-cc9-2p-seed-r1',
    'vienna-I056-regiao-f4',
)
ARMS = ('U_K', 'B_K')


def make_plan(root: Path, *, budget=300, backend='gurobi', max_iterations=100,
              max_columns=5000, max_rows=60000, selection='matching',
              cert_every=5, cert_budget=15.0, cert_min_remaining=20.0,
              cert_max_attempts=3):
    base = make_parent_plan(root, budget=budget, backend=backend,
                            max_iterations=max_iterations, max_columns=max_columns,
                            max_rows=max_rows, selection=selection)
    if base['schema'] != PARENT_SCHEMA:
        raise ValueError('referência AS-08 v2 inesperada')
    selected = [c for c in base['cases'] if c['name'] in SELECTED]
    if [c['name'] for c in selected] != list(SELECTED):
        raise ValueError('instâncias do experimento LB divergem da lista pré-definida')
    if cert_every < 1 or cert_max_attempts < 1 or not (0 < cert_budget <= budget):
        raise ValueError('parâmetros da certificação inválidos')
    if not (0 < cert_min_remaining <= budget):
        raise ValueError('reserva da certificação inválida')
    base.update(schema=SCHEMA, cases=selected,
                classification='EXPLORATORY_BOUND_STRENGTH_ONLY',
                scientific_gate='NO_AUTOMATIC_PROMOTION')
    base['cg'].update(intermediate_cert_every=cert_every,
                      intermediate_cert_budget_s=float(cert_budget),
                      intermediate_cert_min_remaining_s=float(cert_min_remaining),
                      intermediate_cert_max_attempts=cert_max_attempts)
    base['protocol'] = [
        'Three AS05 development cases, frozen order, six independently bounded arms',
        'COMP+K LP numeric baseline; B+K dual rational certified global LB',
        'Never compare restricted master objective to complete LP',
        'No certificate without exact pricing of all sources and independent audit',
        'Timeout can preserve last complete certificate in immutable sidecar',
        'A global LB strictly exceeding COMP+K establishes LP strengthening',
        'No convergence implies no B LP objective and no MIP conclusion',
        'Development evidence is exploratory: no scientific promotion',
    ]
    return base


def validate_plan(plan, root):
    if plan.get('schema') != SCHEMA:
        raise ValueError('esquema AS08-LB incompatível')
    cg = plan['cg']
    expected = make_plan(root, budget=plan['budget_seconds_per_arm'],
                         backend=plan['solver']['backend'],
                         max_iterations=cg['iterations'], max_columns=cg['max_columns'],
                         max_rows=cg['max_rows'], selection=cg['selection'],
                         cert_every=cg['intermediate_cert_every'],
                         cert_budget=cg['intermediate_cert_budget_s'],
                         cert_min_remaining=cg['intermediate_cert_min_remaining_s'],
                         cert_max_attempts=cg['intermediate_cert_max_attempts'])
    if plan != expected:
        raise ValueError('plano alterado, crie outro novo')
    return plan


def _result_filenames(plan):
    return [f'{c["name"]}--{arm}.json' for c in plan['cases'] for arm in plan['arms']]


def _progress_name(case):
    return f'{case["name"]}--B_K.cg-progress.json'


def execute(plan, root: Path, output: Path, *, resume=False):
    validate_plan(plan, root)
    if output.exists() and any(output.iterdir()) and not resume:
        raise FileExistsError('diretório contém arquivos; use --resume só para o mesmo plano')
    output.mkdir(parents=True, exist_ok=True)
    if not (output/'plan.json').exists():
        json_write(output/'plan.json', plan)
    if json.loads((output/'plan.json').read_text()) != plan:
        raise ValueError('plano do diretório diverge')
    manifest_rows = {r['nome']: r for r in fc_instances.load_manifest(root/'instances/manifest.csv')}
    for case in plan['cases']:
        row = manifest_rows[case['manifest_name']]
        if row['sha256'] != case['source_sha256']:
            raise ValueError('hash de instância mudou: '+case['name'])
        for arm in ARMS:
            path = output/f'{case["name"]}--{arm}.json'
            if path.exists():
                if not resume:
                    raise FileExistsError(str(path))
                existing = json.loads(path.read_text())
                if (existing.get('plan_sha256') != digest(plan)
                    or existing.get('case') != case or existing.get('arm') != arm):
                    raise ValueError('checkpoint pertence a outro experimento')
                print('AS08_LB_RESUMED', case['name'], arm, existing['status'], flush=True)
                continue
            progress_path = output/_progress_name(case)
            progress = progress_record(plan,case,arm) if arm == 'B_K' else None
            if progress is not None and progress_path.exists():
                raise FileExistsError('checkpoint incompleto preexistente: '+str(progress_path))

            def on_progress(event):
                if progress is None:
                    return
                msg = dict(event)
                certificate = msg.pop('certificate', None)
                if certificate is not None:
                    if certificate.get('status') != 'CERTIFIED_RATIONAL_DUAL':
                        raise ValueError('certificado intermediário inválido')
                    old = progress.get('latest_certificate')
                    if (old is None or Fraction(certificate['rational']) >
                        Fraction(old['rational'])):
                        progress['latest_certificate'] = certificate
                        progress['latest_certificate_iteration'] = msg.get('iteration')
                    msg['complete_certificate_archived'] = True
                progress['events'].append(msg)
                atomic_progress_write(progress_path, progress)

            outcome = run_bounded(_worker, row, str(root), arm, plan,
                                  budget_s=plan['budget_seconds_per_arm'],
                                  on_progress=on_progress if arm == 'B_K' else None)
            payload = (outcome.value if outcome.status == 'COMPLETED' else {
                'status': outcome.status, 'reason': outcome.reason,
                'lp_numeric_value': None, 'global_lower_bound': None})
            if progress is not None:
                # Um timeout elimina o resultado do worker, NÃO um certificado
                # exato completo já recebido e persistido pelo supervisor.
                saved = progress.get('latest_certificate')
                if saved is not None:
                    current = payload.get('global_lb_certificate')
                    if current is None or Fraction(saved['rational']) > Fraction(current['rational']):
                        payload['global_lb_certificate'] = saved
                        payload['global_lower_bound'] = float(Fraction(saved['rational']))
                        payload['certified_lb_recovered_from_progress'] = True
                    ready = next((e for e in progress['events'] if e['event']=='INPUT_READY'),None)
                    if ready:
                        payload.setdefault('K_sha256',ready['K_sha256'])
                        payload.setdefault('instance_sha256',ready['instance_sha256'])
                        payload.setdefault('K_count',ready['K_count'])
                        payload.setdefault('k_validated',True)
                progress['outcome']={'supervisor_status':outcome.status,
                                     'arm_status':payload['status'],
                                     'wall_total_s':outcome.wall_total_s}
                atomic_progress_write(progress_path,progress)
            record = {
                'schema':RESULT,'plan_sha256':digest(plan),'case':case,'arm':arm,
                'wall_total_s':outcome.wall_total_s,
                'wall_phases_s':dict(outcome.phase_wall_s),**payload,
            }
            if progress is not None:
                record['cg_progress_checkpoint']={
                    'file':progress_path.name,'sha256':sha(progress_path),
                    'events':len(progress['events']),
                    'last_event':progress['events'][-1] if progress['events'] else None}
            json_write(path,record)
            print('AS08_LB_CASE',case['name'],arm,record['status'],
                  'LP',record.get('lp_numeric_value'),
                  'CERT_LB',record.get('global_lower_bound'),flush=True)
    frozen = {
        'schema':MANIFEST,'plan_sha256':digest(plan),
        'files':{fn:sha(output/fn) for fn in _result_filenames(plan)},
        'progress_files':{
            _progress_name(c):sha(output/_progress_name(c))
            for c in plan['cases'] if (output/_progress_name(c)).exists()
        },
    }
    if not (output/'manifest.json').exists():
        json_write(output/'manifest.json',frozen)
    elif json.loads((output/'manifest.json').read_text()) != frozen:
        raise ValueError('manifest anterior diverge')
    return verify(output,root)


def verify(output: Path,root: Path):
    plan=json.loads((output/'plan.json').read_text())
    validate_plan(plan,root)
    frozen=json.loads((output/'manifest.json').read_text())
    expected={
        'schema':MANIFEST,'plan_sha256':digest(plan),
        'files':{fn:sha(output/fn) for fn in _result_filenames(plan)},
        'progress_files':{
            _progress_name(c):sha(output/_progress_name(c))
            for c in plan['cases'] if (output/_progress_name(c)).exists()
        },
    }
    if frozen != expected:
        raise ValueError('manifest/arquivos alterados')
    results=[]
    for c in plan['cases']:
        for arm in ARMS:
            row=json.loads((output/f'{c["name"]}--{arm}.json').read_text())
            if (row.get('schema')!=RESULT or row.get('case')!=c
                or row.get('arm')!=arm or row.get('plan_sha256')!=digest(plan)):
                raise ValueError('resultado de outro plano ou instância')
            if arm == 'B_K':
                if row['status'] != 'CONVERGED' and row.get('lp_numeric_value') is not None:
                    raise ValueError('B censurado não pode declarar LP ótimo')
                cp=row.get('cg_progress_checkpoint') or {}
                if cp.get('file') != _progress_name(c) or cp.get('sha256') != sha(output/_progress_name(c)):
                    raise ValueError('checkpoint de B ausente/modificado')
                record=json.loads((output/_progress_name(c)).read_text())
                verify_progress(record,plan,c,arm)
                if (cp.get('events')!=len(record['events'])
                    or cp.get('last_event')!=(record['events'][-1] if record['events'] else None)
                    or record.get('outcome',{}).get('arm_status') != row['status']):
                    raise ValueError('checkpoint divergente')
                cert=row.get('global_lb_certificate')
                if cert is not None:
                    if cert.get('status')!='CERTIFIED_RATIONAL_DUAL':
                        raise ValueError('status do certificado inválido')
                    if row.get('global_lower_bound') is None:
                        raise ValueError('LB sem valor')
                    if abs(float(Fraction(cert['rational']))-row['global_lower_bound'])>1e-7:
                        raise ValueError('LB não corresponde ao racional')
                    if (not row.get('k_validated')
                        or row.get('instance_sha256')!=c['source_sha256']
                        or not row.get('K_sha256')):
                        raise ValueError('certificado sem proveniência da instância/K')
                    archived=record.get('latest_certificate')
                    if archived is not None and Fraction(cert['rational']) < Fraction(archived['rational']):
                        raise ValueError('certificado final inferior ao checkpoint')
                elif row.get('global_lower_bound') is not None:
                    raise ValueError('LB numérico sem certificado')
                elif record.get('latest_certificate') is not None:
                    raise ValueError('certificado persistido não foi transferido ao resultado')
            else:
                if row['status'] != 'OPTIMAL_NUMERIC' and row.get('lp_numeric_value') is not None:
                    raise ValueError('U censurado não pode declarar ótimo')
                if row.get('lp_numeric_value') is not None and (
                    not row.get('k_validated') or row.get('instance_sha256')!=c['source_sha256']):
                    raise ValueError('comparador sem proveniência')
            results.append(row)
    if len(results)!=len(plan['cases'])*2:
        raise ValueError('execução incompleta')
    return results


def audit_duals(runs,root):
    """Recalcula instância, K e todos os preços racionais independentemente."""
    manifest={r['nome']:r for r in fc_instances.load_manifest(root/'instances/manifest.csv')}
    checked=[]
    for record in runs:
        if record['arm']!='B_K' or record.get('global_lb_certificate') is None:
            continue
        c=record['case']
        loaded=fc_instances.load_instance(manifest[c['manifest_name']],root=root)
        if loaded.instance_sha256 != c['source_sha256']:
            raise ValueError('hash físico divergente durante auditoria')
        if int(loaded.r)!=loaded.r:
            raise ValueError('autonomia inconsistente')
        ins=Instance(tuple(loaded.V),tuple(loaded.S),tuple(loaded.T),
                     tuple(loaded.A_r),int(loaded.r))
        cuts,profile=_timed_k(ins,loaded,validator_method='bitset-v2')
        if k_digest(ins,cuts)!=record.get('K_sha256'):
            raise ValueError('cortes K diferem dos usados no certificado')
        verify_rational_certificate(ins,cuts,record['global_lb_certificate'])
        checked.append(c['name'])
    return checked


def analyze(runs, output, audited):
    pairs=[]
    for i in range(0,len(runs),2):
        u,b=runs[i:i+2]
        assert u['arm']=='U_K' and b['arm']=='B_K' and u['case']==b['case']
        uv=u.get('lp_numeric_value')
        cert=b.get('global_lb_certificate')
        lb=Fraction(cert['rational']) if cert is not None else None
        if lb is not None and b['case']['name'] not in audited:
            raise ValueError('certificado não auditado')
        if uv is not None and lb is not None and u.get('K_sha256')!=b.get('K_sha256'):
            raise ValueError('cortes K diferentes entre os braços')
        # Proteção explícita contra ruído de solução numérica de U.
        eps=max(1e-6,1e-7*abs(uv)) if uv is not None else None
        absolute = float(lb)-uv if uv is not None and lb is not None else None
        ratio = absolute/uv if absolute is not None and uv>0 else None
        material = (u['status']=='OPTIMAL_NUMERIC' and lb is not None
                    and ratio is not None and absolute>eps and ratio>=0.01+eps/uv)
        pairs.append({
            'case':u['case']['name'],'graph_source':u['case']['graph_source'],
            'u_lp_numeric':uv,'b_status':b['status'],
            'b_lp_optimal':b.get('lp_numeric_value'),
            'b_global_lb_rational':str(lb) if lb is not None else None,
            'b_global_lb_numeric_for_display':float(lb) if lb is not None else None,
            'b_primal_upper_bound':(b.get('cg_diagnostics') or {}).get('feasible_lp_upper_bound'),
            'certified_gain_absolute':absolute, 'certified_gain_fraction':ratio,
            'material_gain_gt_1pct':material,
            'audited':lb is not None,
            'u_wall_s':u['wall_total_s'],'b_wall_s':b['wall_total_s'],
        })
    passed=[p for p in pairs if p['material_gain_gt_1pct']]
    families=set(p['graph_source'] for p in passed)
    decision=('EVIDENCE_FOR_CONTINUATION_EXPLORATORY'
              if len(passed)>=2 and len(families)>=2 else
              'SINGLE_CASE_OR_SMALL_GAIN_EXPLORATORY' if passed else
              'INCONCLUSIVE_NO_MATERIAL_CERTIFIED_GAIN')
    result={'schema':'AS08-LB-PROBE-ANALYSIS-v1',
            'classification':'EXPLORATORY_NOT_SCIENTIFICALLY_HOMOLOGATED',
            'scientific_gate':'PENDING','decision':decision,
            'audited_certificates':sorted(audited),'cases':pairs,
            'gain_threshold_fraction':0.01}
    fmt=lambda n:'—' if n is None else f'{n:.6f}'
    lines=['# AS-08/LB — Limites inferiores racionais intermediários', '',
           '**Decisão:** `'+decision+'` (exploratória, sem promoção científica).','',
           'Objetivo do RMP não é limite inferior global. Censura não invalida '
           'certificado completo recuperado do checkpoint.','',
           '| Caso | COMP+K LP | B+K LB racional | Ganho mínimo certificado | Status B |',
           '|---|---:|---:|---:|---|']
    for p in pairs:
        lines.append(f"| {p['case']} | {fmt(p['u_lp_numeric'])} | "
                     f"{fmt(p['b_global_lb_numeric_for_display'])} | "
                     f"{fmt(100*p['certified_gain_fraction'])+'%' if p['certified_gain_fraction'] is not None else '—'} | "
                     f"{p['b_status']} |")
    lines.extend(['','**Aviso:** ganho calculado de LB global de B em relação ao LP numérico '
                  'do comparador, não de objetivo do mestre restrito.',
                  'O ganho percentual negativo não implica que B seja mais fraco.',
                  'Se não houver certificado relevante, o resultado permanece inconclusivo.'])
    json_write(output/'analysis.json',result)
    if (output/'analysis.md').exists():
        raise FileExistsError('não sobrescrever relatório')
    (output/'analysis.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    return result


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    mode=parser.add_mutually_exclusive_group(required=True)
    for name in ('init-plan','check-plan','execute','verify','analyze'):
        mode.add_argument('--'+name,action='store_true')
    parser.add_argument('--plan',default='results/benchmark/as08-lb-probe-plan-v1.json')
    parser.add_argument('--output-dir',default='results/benchmark/as08-lb-probe-001')
    parser.add_argument('--backend',choices=('gurobi','scipy-highs'),default='gurobi')
    parser.add_argument('--budget',type=int,default=300)
    parser.add_argument('--max-iterations',type=int,default=100)
    parser.add_argument('--max-columns',type=int,default=5000)
    parser.add_argument('--max-rows',type=int,default=60000)
    parser.add_argument('--selection',choices=('global','per_source','matching'),default='matching')
    parser.add_argument('--cert-every',type=int,default=5)
    parser.add_argument('--cert-budget',type=float,default=15.0)
    parser.add_argument('--cert-min-remaining',type=float,default=20.0)
    parser.add_argument('--cert-max-attempts',type=int,default=3)
    parser.add_argument('--resume',action='store_true')
    parser.add_argument('--audit-dual',action='store_true')
    args=parser.parse_args(argv)
    root=ROOT
    pp=root/args.plan
    out=root/args.output_dir
    if args.init_plan:
        p=make_plan(root,budget=args.budget,backend=args.backend,
                    max_iterations=args.max_iterations,max_columns=args.max_columns,
                    max_rows=args.max_rows,selection=args.selection,
                    cert_every=args.cert_every,cert_budget=args.cert_budget,
                    cert_min_remaining=args.cert_min_remaining,
                    cert_max_attempts=args.cert_max_attempts)
        json_write(pp,p)
        print('AS08_LB_PLAN_CREATED',len(p['cases']),'cases/6 arms',digest(p))
        return 0
    p=json.loads(pp.read_text(encoding='utf-8'))
    validate_plan(p,root)
    if args.check_plan:
        print('AS08_LB_PLAN_VALID',digest(p));return 0
    if args.execute:
        runs=execute(p,root,out,resume=args.resume)
        print('AS08_LB_COMPLETED',len(runs),'arms');return 0
    runs=verify(out,root)
    if args.verify:
        if args.audit_dual:
            print('AS08_LB_DUAL_AUDITED',len(audit_duals(runs,root)),'cases')
        print('AS08_LB_VERIFIED',len(runs),'arms');return 0
    checked=audit_duals(runs,root)
    result=analyze(runs,out,checked)
    print('AS08_LB_ANALYZED',result['decision'],out/'analysis.md')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
