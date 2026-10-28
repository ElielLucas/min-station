"""AS29: auditoria documental, sem solver nem uso de resultados reservados.

Executar na raiz: poetry run python experiments/benchmark/reconcile_as29.py

Rev. 1 (revisão independente, 17/10/2026) e Rev. 2 (18/10/2026, exportação posterior): revalida toda instalação arquivada
com o oráculo independente (`experiments/cuts/independent_validator.py`),
exclui do LB os braços C/C_K (AS09 `math_gate=PROOF_REVIEW_REQUIRED`), separa
LP de LB MIP, distingue ótimo numérico com e sem UB física e lê seed/threads/
orçamento dos planos com hash conferido em vez de fixá-los no código, exibe
lado a lado (sem fundir) os limites documentados no manifesto e trata caso sem
UB alguma como dado incompleto.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

EPS = 1e-6
ENVELOPE_VERSION = 'AS29-r2'
SPLITS = {'desenvolvimento', 'legado'}
# Formulações com validade estabelecida no baseline: U (base), U_K (COMP+K) e K_IP (relaxação inteira).
# C/C_K (AS09) não têm prova revisada: seus bounds ficam na proveniência, mas não entram no envelope.
LB_ADMISSIBLE = {'U', 'U_K', 'K_IP'}
UB_NUMERIC_ARMS = {'U', 'U_K'}
PROV_FIELDS = ['case','split','class','raw_graph_id','instance_path','instance_sha256','sha_verified','n','m','r','source','source_record','source_sha256','plan_sha256','method','mode','seed','threads','work_limit','wall_budget_s','solver_version','status','censored','numeric_lb','lb_integer','lb_admissible','lp_value','numeric_incumbent','physical_ub_reported','physical_ub','ub_provenance','validation_evidence','result_commit','source_versioned_in','cuts_sha256','cuts_scope','exclusion','notes']


def sha256(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()

def canonical_hash(data):
    """Mesma convenção de `run_as09_extended.canonical_hash`."""
    return hashlib.sha256(json.dumps(data,sort_keys=True,ensure_ascii=False,allow_nan=False,separators=(',',':')).encode('utf-8')).hexdigest()

def versioned_in(root,rel):
    """Último commit git que tocou a fonte (hash curto e data); vazio fora de um clone git."""
    try:out=subprocess.run(['git','-C',str(root),'log','-1','--format=%h %ad','--date=short','--',rel],capture_output=True,text=True,check=True).stdout.strip()
    except (OSError,subprocess.CalledProcessError):return ''
    return out

def num(v):
    if v in ('',None):return None
    try: x=float(v)
    except (ValueError,TypeError):return None
    return x if math.isfinite(x) else None

def lb(v):
    x=num(v)
    return math.ceil(x-EPS) if x is not None else None

def integral(v):
    x=num(v)
    if x is None:return None
    return int(round(x)) if abs(x-round(x))<=EPS else x

def validated_ub(v,installed,invalid):
    """Pré-condição documental: valor inteiro, vetor de mesmo tamanho e zero incumbentes inválidas."""
    x=num(v)
    if x is None or abs(x-round(x))>EPS or invalid not in (0,'0') or not isinstance(installed,list) or len(installed)!=round(x):return None
    return int(round(x))

def rows(path):
    with Path(path).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))

def physical_oracle(root):
    """Oráculo físico independente do modelo MIP: alcance por estados (vértice, bateria) + matching S→T."""
    for p in (root,root/'experiments/cuts'):
        if str(p) not in sys.path:sys.path.insert(0,str(p))
    from ms_utils import ler_instancia,construir_adjacencia
    from independent_validator import viavel
    cache={}
    def check(common,installed):
        key=common['instance_path']
        if key not in cache:
            d=ler_instancia(str(root/key));cache[key]=(d,construir_adjacencia(d['E']))
        d,adj=cache[key];r=float(common['r'])
        if abs(r-round(r))>EPS:return False
        C=[str(v) for v in installed];V={str(v) for v in d['V']}
        if len(set(C))!=len(C) or not set(C)<=V:return False
        return bool(viavel(d['S'],d['T'],d['V'],adj,int(round(r)),C))
    return check

def basic(meta,case,root):
    m=meta[case];p=root/m['caminho'];ok=p.is_file() and sha256(p)==m['sha256']
    documented={f'manifest_{k}':m.get(k,'') for k in ('lb','ub','fonte_lb_ub','lb_melhor','ub_melhor','fonte_melhor')}
    return dict(case=case,split=m['particao'],**{'class':m['classe']},raw_graph_id=f"{m['fonte']}:{m['instancia_original']}",instance_path=m['caminho'],instance_sha256=m['sha256'],sha_verified=str(ok).lower(),n=m['n'],m=m['m'],r=m['r'],_documented=documented)

def baseline_record(r,common,digest,versioned=''):
    arm={'base':'U','comp':'U_K','nucleo':'K_IP'}[r['braco']];obj=num(r['mip_obj'])
    return {**common,'source':'SPEC_A_R4','source_record':'results/benchmark/linha_base.csv','source_sha256':digest,'plan_sha256':'','method':arm,'mode':'IP' if arm=='K_IP' else 'MIP','seed':r['seed'],'threads':r['threads'],'work_limit':r['work_limit'],'wall_budget_s':r['guard_s'],'solver_version':'','status':r['mip_status'],'censored':str(r['mip_status']!='2').lower(),'numeric_lb':num(r['mip_bound']),'lb_integer':lb(r['mip_bound']),'lb_admissible':'true','lp_value':'','numeric_incumbent':obj,'physical_ub_reported':'','physical_ub':'','ub_provenance':'NOT_PHYSICAL_UB' if arm=='K_IP' else 'SOLVER_ONLY','validation_evidence':r['fonte_certificado'],'result_commit':r['commit'],'source_versioned_in':versioned,'cuts_sha256':r['cuts_sha256'],'cuts_scope':'generator' if r['cuts_sha256'] else '','exclusion':'','notes':'K_IP is LB, never UB' if arm=='K_IP' else 'No installation archived in baseline CSV; solver incumbent only'}

def solver_record(x,common,oracle,*,source,source_record,source_sha256,plan_sha256,method,mode,seed,threads,wall_budget_s,cuts,notes,versioned='',work_limit=''):
    """Linha de proveniência de um registro AS06/AS09; UB física só após o oráculo independente."""
    exclusion='' if x.get('instance_sha256')==common['instance_sha256'] else 'INSTANCE_SHA_MISMATCH'
    lp=num(x.get('lp_numeric_value')) if mode=='LP' else None
    reported=validated_ub(x.get('physical_validated_ub'),x.get('installed'),x.get('invalid_incumbents',0)) if mode=='MIP' else None
    phys,prov=None,('NOT_APPLICABLE_LP' if mode=='LP' else 'NOT_VALIDATED')
    if reported is not None and not exclusion:
        if oracle(common,x['installed']):phys,prov=reported,'ORACLE_REVALIDATED_AS29'
        else:prov='ORACLE_REJECTED'
    bound=num(x.get('mip_numeric_bound')) if mode=='MIP' else None
    return {**common,'source':source,'source_record':source_record,'source_sha256':source_sha256,'plan_sha256':plan_sha256,'method':method,'mode':mode,'seed':seed,'threads':threads,'work_limit':work_limit,'wall_budget_s':wall_budget_s,'solver_version':x.get('solver_version',x.get('gurobi_version','')),'status':x.get('status',''),'censored':str(x.get('status')!='OPTIMAL_NUMERIC').lower(),'numeric_lb':bound,'lb_integer':lb(bound),'lb_admissible':str(method in LB_ADMISSIBLE and not exclusion and mode=='MIP' and bound is not None).lower(),'lp_value':lp if lp is not None else '','numeric_incumbent':num(x.get('mip_numeric_incumbent')) if mode=='MIP' else None,'physical_ub_reported':reported if reported is not None else '','physical_ub':phys if phys is not None else '','ub_provenance':prov,'validation_evidence':'installed re-checked by independent_validator.viavel' if prov.startswith('ORACLE') else '','result_commit':'','source_versioned_in':versioned,'cuts_sha256':cuts or '','cuts_scope':'instance_K' if cuts else '','exclusion':exclusion,'notes':notes}

def extra_records(root,common,oracle=None):
    oracle=oracle or physical_oracle(root)
    ret=[]
    a06=root/'results/benchmark/as06-mip-replication-001'
    if (a06/'checkpoints').is_dir():
        plan=json.loads((a06/'plan.json').read_text(encoding='utf-8'));plan_digest=sha256(a06/'plan.json')
        listed=json.loads((a06/'manifest.json').read_text(encoding='utf-8'))['files']
        report=json.loads((a06/'report.json').read_text(encoding='utf-8'))
        if listed.get('plan.json')!=plan_digest or report.get('plan_sha256')!=plan_digest:raise ValueError('AS06 plan digest mismatch')
        ver=versioned_in(root,a06.relative_to(root).as_posix())
        for path in sorted((a06/'checkpoints').glob('*/arm-*.json')):
            case=path.parent.name+'.txt'
            if case not in common:continue
            sidecar=path.with_suffix('.sha256');digest=sha256(path);rel=path.relative_to(a06).as_posix()
            if not sidecar.is_file() or sidecar.read_text(encoding='utf-8').strip()!=digest or listed.get(rel,digest)!=digest:
                raise ValueError('AS06 sidecar integrity failed: '+str(path))
            x=json.loads(path.read_text(encoding='utf-8'))['result']
            if x.get('arm_id') not in UB_NUMERIC_ARMS:continue
            pol=x.get('solver_policy') or {}
            ret.append(solver_record(x,common[case],oracle,source='AS06_REPLICATION',source_record=path.relative_to(root).as_posix(),source_sha256=digest,plan_sha256=plan_digest,method=x['arm_id'],mode='MIP',seed=x.get('seed',''),threads=pol.get('threads',''),wall_budget_s=plan['budget_seconds_per_arm'],cuts=x.get('applied_k_sha256'),notes=f"Exploratory development replication; solver budget = wall budget - validation_reserve_s={pol.get('validation_reserve_s','')}",versioned=ver))
    a09=root/'results/benchmark/as09-expanded-600s-001'
    for mode in ('MIP','LP'):
        folder=a09/mode
        if not folder.is_dir():continue
        digest_manifest=folder/'manifest.json'
        if not digest_manifest.is_file():raise ValueError(f'AS09 missing digest manifest ({mode})')
        manifest=json.loads(digest_manifest.read_text(encoding='utf-8'))
        plan=json.loads((a09/'plan.json').read_text(encoding='utf-8'));plan_digest=canonical_hash(plan)
        if manifest.get('plan_sha256')!=plan_digest:raise ValueError('AS09 plan digest mismatch: '+mode)
        file_hashes=manifest['files'];ver=versioned_in(root,folder.relative_to(root).as_posix())
        for path in sorted(folder.glob('*.json')):
            if path.name=='manifest.json':continue
            # Filtrar antes de abrir JSON para nao acessar resultados reservados.
            name=path.stem.rsplit('--',1)[0]+'.txt'
            if name not in common:continue
            if file_hashes.get(path.name)!=sha256(path):raise ValueError('AS09 digest integrity failed: '+str(path))
            x=json.loads(path.read_text(encoding='utf-8'));case=x.get('case',{}).get('manifest_name','')
            if case!=name or x.get('arm') not in ('U','U_K','C','C_K') or x.get('mode')!=mode:continue
            if x.get('plan_sha256')!=plan_digest:raise ValueError('AS09 record plan digest mismatch: '+str(path))
            note='Mixed-split exploratory source; only development/legacy rows selected'
            if x['arm'] in ('C','C_K'):note+='; formulation C proof pending (PROOF_REVIEW_REQUIRED): bound/LP not admissible'
            ret.append(solver_record(x,common[case],oracle,source='AS09_EXPANDED_EXPLORATORY',source_record=path.relative_to(root).as_posix(),source_sha256=sha256(path),plan_sha256=plan_digest,method=x['arm'],mode=mode,seed=plan['solver']['seed'],threads=plan['solver']['threads'],wall_budget_s=plan['budget_seconds_per_arm'],cuts=x.get('K_sha256'),notes=note,versioned=ver))
    post=root/'results/benchmark/as29-physical-ub-001'
    if post.is_dir():
        ver=versioned_in(root,post.relative_to(root).as_posix())
        for path in sorted(post.glob('*.json')):
            digest=sha256(path);sidecar=path.with_suffix('.sha256')
            if not sidecar.is_file() or sidecar.read_text(encoding='utf-8').strip()!=digest:
                raise ValueError('AS29 export sidecar integrity failed: '+str(path))
            x=json.loads(path.read_text(encoding='utf-8'))
            case=x.get('case_name','')
            if x.get('schema')!='AS29-PHYSICAL-UB-v1' or case not in common or x.get('arm_id') not in UB_NUMERIC_ARMS:continue
            ret.append(solver_record(x,common[case],oracle,source='AS29_POSTERIOR_EXPORT',source_record=path.relative_to(root).as_posix(),source_sha256=digest,plan_sha256='',method=x['arm_id'],mode='MIP',seed=x['seed'],threads=x['threads'],wall_budget_s=x['guard_s'],cuts=None,work_limit=x['work_limit'],versioned=ver,notes=f"Posterior evidence (after AS29 Rev. 1), Spec A R4 configuration reproduced; commit {x.get('commit','')}; may differ from the historical incumbent"))
    return ret

def _first(rows,key,value):
    return next((a for a in rows if a[key]==value),None)

def summarize(common,x):
    """Envelope de um caso. Não é comparação pareada: mistura campanhas e orçamentos distintos."""
    b=[a for a in x if a['source']=='SPEC_A_R4' and a['lb_integer'] is not None]
    lb_base=max((a['lb_integer'] for a in b),default=None);bs=_first(b,'lb_integer',lb_base) if b else None
    adm=[a for a in x if a['lb_admissible']=='true' and a['lb_integer'] is not None]
    hist=max((a['lb_integer'] for a in adm),default=None);hs=_first(adm,'lb_integer',hist) if adm else None
    numeric=[dict(a,_ub=integral(a['numeric_incumbent'])) for a in x if a['method'] in UB_NUMERIC_ARMS and a['mode']=='MIP' and not a['exclusion'] and a['numeric_incumbent'] is not None]
    ub_num=min((a['_ub'] for a in numeric),default=None);ns=_first(numeric,'_ub',ub_num) if numeric else None
    base_ub=min((a['_ub'] for a in numeric if a['source']=='SPEC_A_R4'),default=None)
    physical=[a for a in x if a['physical_ub']!='']
    ub=min((a['physical_ub'] for a in physical),default=None);us=_first(physical,'physical_ub',ub) if physical else None
    lp={arm:next((a for a in x if a['mode']=='LP' and a['method']==arm and a['lp_value']!='' and not a['exclusion']),None) for arm in ('U','U_K')}
    doc=common.get('_documented',{})
    doc_lb=max((v for v in (lb(doc.get('manifest_lb')),lb(doc.get('manifest_lb_melhor'))) if v is not None),default=None)
    doc_ub=min((v for v in (integral(doc.get('manifest_ub')),integral(doc.get('manifest_ub_melhor'))) if v is not None),default=None)
    issues=[]
    if common['sha_verified']!='true':issues.append('FILE_SHA_MISMATCH_OR_MISSING')
    if hist is None:issues.append('NO_ADMISSIBLE_LB')
    if any(a['ub_provenance']=='ORACLE_REJECTED' for a in x):issues.append('ORACLE_REJECTED_RECORD')
    ub_min=min((v for v in (ub,ub_num) if v is not None),default=None)
    if hist is not None and ub_min is not None and hist>ub_min:issues.append('LB_EXCEEDS_UB')
    if ub is None and ub_num is None:issues.append('NO_UB')
    if ub is None:issues.append('NO_PHYSICAL_UB_EVIDENCE')
    if (doc_lb is not None and hist is not None and doc_lb>hist) or (doc_ub is not None and ub_min is not None and doc_ub<ub_min):issues.append('DOCUMENTED_BOUND_OUTSIDE_ENVELOPE')
    if 'FILE_SHA_MISMATCH_OR_MISSING' in issues:status='INTEGRITY_BLOCKED'
    elif {'LB_EXCEEDS_UB','ORACLE_REJECTED_RECORD','NO_ADMISSIBLE_LB'}&set(issues):status='INCONSISTENT'
    elif 'NO_UB' in issues:status='INCOMPLETE'
    elif ub is not None and ub==hist:status='OPT_NUMERIC_PHYSICAL'
    elif ub is not None:status='OPEN_PHYSICAL_UB'
    elif ub_num is not None and ub_num==hist:status='OPT_NUMERIC_SOLVER_ONLY'
    else:status='OPEN_SOLVER_UB_ONLY'
    cert={'OPT_NUMERIC_PHYSICAL':'LB numérico do solver (ceil(bound-1e-6)) = |C| de instalação revalidada pelo oráculo independente; não é certificado racional',
          'OPEN_PHYSICAL_UB':'UB física revalidada pelo oráculo; LB numérico do solver',
          'OPT_NUMERIC_SOLVER_ONLY':'LB e incumbente numéricos do solver coincidem; nenhuma instalação arquivada para validação física',
          'OPEN_SOLVER_UB_ONLY':'LB e incumbente numéricos do solver; nenhuma instalação arquivada para validação física',
          'INCOMPLETE':'dados incompletos: nenhuma UB disponível; não estimar'}.get(status,'não utilizável até resolver a integridade')
    pending='' if ub is not None else 'UB física ausente: usar só como referência de LB/UB numérica; validar instalação no braço controle do pré-registro que usar o caso como referência de UB/OPT'
    opt=hist if status in ('OPT_NUMERIC_PHYSICAL','OPT_NUMERIC_SOLVER_ONLY') else ''
    common={k:v for k,v in common.items() if k!='_documented'}
    return {**common,'base_lb_integer':lb_base,'base_lb_method':bs['method'] if bs else '','base_lb_seed':bs['seed'] if bs else '','base_lb_source':bs['source_record'] if bs else '','base_ub_numeric_only':base_ub,
            'historic_lb_integer':hist,'historic_lb_method':hs['method'] if hs else '','historic_lb_source':hs['source_record'] if hs else '',
            'ub_numeric_envelope':ub_num,'ub_numeric_source':ns['source_record'] if ns else '',
            'physical_ub_validated':ub if ub is not None else '','physical_ub_source':us['source_record'] if us else '',
            'lp_u':lp['U']['lp_value'] if lp['U'] else '','lp_u_k':lp['U_K']['lp_value'] if lp['U_K'] else '','lp_source':(lp['U_K'] or lp['U'] or {}).get('source_record',''),
            **doc,'lb_documented_max':doc_lb if doc_lb is not None else '','ub_documented_min':doc_ub if doc_ub is not None else '',
            'opt_numeric':opt,'status':status,'certification':cert,'ub_reference_eligible':str(ub is not None and status not in ('INTEGRITY_BLOCKED','INCONSISTENT')).lower(),
            'issues':';'.join(issues),'pending':pending,'comparability':'envelope histórico; não pareado (orçamentos/seeds/campanhas distintos); valores manifest_* documentados, sem artefato por execução com SHA, exibidos e não fundidos','n_source_rows':len(x),'envelope_version':ENVELOPE_VERSION}

def gate(summary):
    """G0 pelo contrato vigente (sem emendas). Nunca aprova: PASS exige aprovação do pesquisador (plano, §6).

    `amendment_candidate` ficou do desenho da emenda A1 (não adotada); só é preenchido se algum caso de
    desenvolvimento voltar a ficar sem UB física.
    """
    dev=[x for x in summary if x['split']=='desenvolvimento']
    blocked=[x['case'] for x in dev if x['status'] in ('INTEGRITY_BLOCKED','INCONSISTENT','INCOMPLETE')]
    eligible=[x['case'] for x in dev if x['ub_reference_eligible']=='true']
    if not dev or blocked:verdict,amend='G0_BLOCKED',''
    elif len(eligible)==len(dev):verdict,amend='G0_CANDIDATE_PASS',''
    else:verdict,amend='G0_BLOCKED_EVIDENCE','G0_PASS_RESTRICTED_IF_AMENDMENT_A1_APPROVED'
    return {'gate':verdict,'amendment_candidate':amend,'blocked_cases':blocked,'ub_reference_eligible':eligible,'rev0_strict_physical_ub_all_dev':f'{len(eligible)}/{len(dev)}'}

def audit(root,oracle=None):
    mr=[x for x in rows(root/'instances/manifest.csv') if x['classe']=='principal' and x['particao'] in SPLITS]
    meta={x['nome']:x for x in mr}
    if len(meta)!=len(mr):raise ValueError('Duplicate principal manifest case ID')
    base=[x for x in rows(root/'results/benchmark/linha_base.csv') if x['particao'] in SPLITS]
    names={x['nome'] for x in base}
    keys=[(x['nome'],x['braco'],x['seed']) for x in base]
    if len(set(keys))!=len(keys):raise ValueError('Duplicate baseline case-arm-seed')
    if any({x['braco'] for x in base if x['nome']==case}!={'base','comp','nucleo'} for case in names):raise ValueError('Incomplete baseline arms')
    if names!=set(meta):raise ValueError(f'Baseline and manifest differ: {sorted(names^set(meta))}')
    for x in base:
        m=meta[x['nome']]
        if any(x[k]!=m[k] for k in ('caminho','sha256','particao')):raise ValueError('Identity mismatch: '+x['nome'])
    common={case:basic(meta,case,root) for case in sorted(names)}
    d=sha256(root/'results/benchmark/linha_base.csv');ver=versioned_in(root,'results/benchmark/linha_base.csv')
    proven=[baseline_record(x,common[x['nome']],d,ver) for x in base]+extra_records(root,common,oracle)
    idx=defaultdict(list)
    for x in proven:idx[x['case']].append(x)
    return proven,[summarize(common[case],idx[case]) for case in sorted(names)]

def write_csv(path,fields,records):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore',lineterminator='\n');w.writeheader();w.writerows(records)

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2]);p.add_argument('--output-dir',type=Path);a=p.parse_args()
    root=a.root.resolve();out=a.output_dir or root/'docs/technical/reference/experimentos'
    proven,summary=audit(root)
    proven=[{k:v for k,v in x.items() if k!='_documented'} for x in proven]
    write_csv(out/'as29-envelope-proveniencia.csv',PROV_FIELDS,proven)
    write_csv(out/'as29-envelope-casos.csv',list(summary[0]),summary)
    dev=[x for x in summary if x['split']=='desenvolvimento'];g=gate(summary)
    print(json.dumps({'envelope_version':ENVELOPE_VERSION,'cases':len(summary),'development':len(dev),'provenance_rows':len(proven),'by_status':dict(sorted(Counter(x['status'] for x in summary).items())),'development_by_status':dict(sorted(Counter(x['status'] for x in dev).items())),'oracle_revalidated_records':sum(x['ub_provenance']=='ORACLE_REVALIDATED_AS29' for x in proven),'oracle_rejected_records':sum(x['ub_provenance']=='ORACLE_REJECTED' for x in proven),'documented_outside_envelope':[x['case'] for x in dev if 'DOCUMENTED_BOUND_OUTSIDE_ENVELOPE' in x['issues']],'lb_inadmissible_records':sum(x['mode']=='MIP' and x['lb_admissible']=='false' and x['numeric_lb'] is not None for x in proven),**g},ensure_ascii=False))
if __name__=='__main__':main()
