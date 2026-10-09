#!/usr/bin/env python3
"""N1-T5: preregistro imutavel -> reproducao F3 -> oito bracos no mesmo corpus.

Uso da raiz, PYTHONHASHSEED=0:
  python experiments/alternative-formulations/run_n1_t5.py freeze
  python experiments/alternative-formulations/run_n1_t5.py reproduce-f3
  python experiments/alternative-formulations/run_n1_t5.py measure

Nao sobrescreve f3-fcc.csv, nao modifica modelos de fases anteriores.
Nao permite re-congelar apos observar valores de novos bracos.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for p in (ROOT, ROOT / 'experiments' / 'cuts', ROOT / 'experiments' / 'structural', HERE):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

FREEZE = HERE / 'n1-t5-freeze.json'
RESULTS = ROOT / 'results' / 'alternative-formulations'
F3 = RESULTS / 'f3-fcc.csv'
F3_REPRO = RESULTS / 'n1-t5-f3-reproduzido.csv'
F3_ATTEST = RESULTS / 'n1-t5-reproducao.json'
OUT = RESULTS / 'n1-t5-diagnostico.csv'
REPORT = ROOT / 'docs' / 'technical' / 'plans' / 'execucao' / 'n1-t5-diagnostico.md'
WITNESSES = RESULTS / 'n1-t5-testemunhas.json'
EPS = 1e-6
N_MAX, MAX_W, N_OPT_ENUM, ARC_CAP = 21, 200000, 16, 5000000
SEED, THREADS = 42, 1
# A ordem foi fixada pela Spec N1 (§ Experimental Pre-registration).
NAMES = (
    'Direct0', 'TermRelay', 'TermRelayForced', 'StayPut', 'StayPutIsolado',
    'SharedTerminal', 'CaminhoABC', 'Tri', 'F1(m=2,k=2)', 'F2(k=1,L=3)',
    'Sec59(L=7)', 'HB-q4-ndir2-p1', 'HB-q5-ndir2-p1',
    'BP-nao-[3,1]-q2', 'TR-k2-L5-r2', 'SC-GF2-k3',
    'SOURCE-g2', 'SOURCE-C5',
)
ARMS = ('lp_base', 'lp_comp', 'core_ip', 'lp_fcc', 'lp_fcc_k', 'lp_fc3', 'lp_fc3_k', 'opt')
NUMERIC_FIELDS = ('n', 'm', 'r', 'lp_base', 'lp_c1c2c4', 'nucleo', 'lp_fcc', 'opt', 'gamma', 'n_W', 'lp_setcover')
FIELDS = [
    'instancia', 'tipo', 'n', 'm', 'r', 'k_hash', 'n_K', 'n_W_raw',
    'n_W_util', 'network_arc_bound', 'opt_source', 'opt',
    'lp_base', 'lp_comp', 'core_ip', 'lp_fcc', 'lp_fcc_k', 'lp_fc3', 'lp_fc3_k',
    'gamma', 'B0', 'delta_fcc', 'delta_fcc_k', 'delta_trio', 'delta_trio_raw',
    'rho_fcc', 'rho_fcc_k', 'rho_fc3', 'rho_fc3_k', 'rho_fcc_historico',
    'status_lp_base', 'status_lp_comp', 'status_core_ip', 'status_lp_fcc',
    'status_lp_fcc_k', 'status_lp_fc3', 'status_lp_fc3_k', 'status_opt',
    'reason_lp_fcc', 'reason_lp_fcc_k', 'reason_lp_fc3', 'reason_lp_fc3_k',
    'n_vars_fcc_k', 'n_cons_fcc_k', 'n_vars_fc3', 'n_cons_fc3',
    'n_vars_fc3_k', 'n_cons_fc3_k', 'source_f3',
]


def now():
    return datetime.now(timezone.utc).isoformat()


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha_file(path):
    return sha_bytes(path.read_bytes())


def json_bytes(data):
    return (json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + '\n').encode('utf8')


def save_new(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as f:
        f.write(data)
    print('CRIADO', path, flush=True)


def load_json(path):
    return json.loads(path.read_text(encoding='utf8'))


def read_csv(path):
    with path.open(newline='', encoding='utf8') as f:
        return list(csv.DictReader(f))


def write_csv(path, rows):
    import io
    buf = io.StringIO(newline='')
    w = csv.DictWriter(buf, FIELDS, extrasaction='ignore')
    w.writeheader()
    for row in rows:
        w.writerow({k: row.get(k, '') for k in FIELDS})
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(buf.getvalue(), encoding='utf8')


def corpus():
    from run_f3 import _instancias
    from source_controls_fc3_n1 import make_source_c5, make_source_g2
    seq = _instancias()
    for factory in (make_source_g2, make_source_c5):
        S, T, V, adj, A_r, r, meta = factory()
        seq.append(dict(nome=meta['name'], tipo='source', S=S, T=T, V=V,
                        adj=adj, A_r=A_r, r=r, sc=None))
    names = tuple(x['nome'] for x in seq)
    if names != NAMES:
        raise AssertionError(f'Instancias diferentes do pre-registro! {names!r}')
    return seq


def instance_hash(inst):
    """Assinatura de dados do grafo, nao so nome e dimensoes."""
    vs = list(inst['V'])
    edges = sorted((str(u), str(v), str(w)) for u, adj in inst['adj'].items()
                   for v, w in adj)
    reach = sorted((str(u), str(v)) for u, v in inst['A_r'])
    return sha_bytes(json_bytes({'V': [str(v) for v in vs], 'S': [str(s) for s in inst['S']],
                      'T': [str(t) for t in inst['T']], 'r': inst['r'],
                      'adj': edges, 'A_r': reach}))


def spec():
    return ROOT / 'specs' / 'proxima-fase-n1-informacao-compatibilidade' / 'spec.md'


def require_t3():
    records = read_csv(RESULTS / 'n1-t3-validacao.csv')
    errors = ('viavel_sim_fc3_nao', 'viavel_nao_fc3_sim',
              'viavel_sim_fcck_nao', 'viavel_nao_fcck_sim',
              'viavel_sim_fc3k_nao', 'viavel_nao_fc3k_sim')
    if not records or len(records) != 9 or any(
            int(row['n_instalacoes']) != 2 ** int(row['n']) or
            any(int(row[field]) != 0 for field in errors)
            for row in records):
        raise RuntimeError('Validação N1-T3 não comprova 9 instâncias e zero divergências')
    records_lp = read_csv(RESULTS / 'n1-t3-lp-invariantes.csv')
    if not records_lp or any(r.get('status') != 'COMPUTATIONALLY VERIFIED' for r in records_lp):
        raise RuntimeError('Invariantes LP N1-T3 não estão todos COMPUTATIONALLY VERIFIED')
    regressions = RESULTS / 'n1-t3-source-regressoes.csv'
    source = {r['instancia']: r for r in read_csv(regressions)}
    if (source.get('SOURCE-g2', {}).get('status') not in ('NOT MEASURED', 'COMPUTATIONALLY VERIFIED') or
        source.get('SOURCE-C5', {}).get('status') != 'COMPUTATIONALLY VERIFIED' or
        abs(float(source['SOURCE-C5']['measured']) - 2.5) > EPS):
        raise RuntimeError('Regressoes SOURCE T3 sem estado esperado')
    r7 = ROOT / 'results' / 'benchmark' / 'n1-r7-auditoria-resumo.csv'
    if not r7.exists():
        raise RuntimeError('Evidencia N1-T4 nao encontrada')
    mr = ROOT / 'docs' / 'technical' / 'reference' / 'formulacoes' / 'revisao-mr-f3-n1.md'
    if '**Decisão:** `ACCEPTED`' not in mr.read_text(encoding='utf8'):
        raise RuntimeError('MR-F3 ainda nao aceito')
    return {'validation_sha256': sha_file(RESULTS / 'n1-t3-validacao.csv'),
            'lp_sha256': sha_file(RESULTS / 'n1-t3-lp-invariantes.csv'),
            'source_sha256': sha_file(regressions), 'r7_sha256': sha_file(r7),
            'mr_f3_sha256': sha_file(mr)}


def freeze():
    if FREEZE.exists() or F3_ATTEST.exists() or OUT.exists():
        raise RuntimeError('Ja existem freeze/medicoes T5. Nao re-congelar nem sobrescrever.')
    if os.environ.get('PYTHONHASHSEED') != '0':
        raise RuntimeError('Use PYTHONHASHSEED=0')
    evidence = require_t3()
    from fcc_k import prepare_k
    from fcc import grafo_H, enumerar_conexos, B_de
    from fc3 import bound_network_arcs
    f3_rows = {r['nome']: r for r in read_csv(F3)}
    rows = []
    for inst in corpus():
        name = inst['nome']
        print('FREEZE', name, flush=True)
        S, T, V, adj, A_r, r = (inst[k] for k in ('S', 'T', 'V', 'adj', 'A_r', 'r'))
        K, digest, counts = prepare_k(S, T, V, adj, A_r, r)
        if len(K) != counts['unicos']:
            raise AssertionError('K com contagem inconsistente')
        n = len(V)
        raw_w, useful_w, cap_reason = None, None, ''
        if n > N_MAX:
            cap_reason = f'n={n} > n_max={N_MAX}'
        else:
            neigh = grafo_H(V, A_r)
            ws, _ = enumerar_conexos(neigh, V, MAX_W + 1)
            raw_w = len(ws)
            if raw_w > MAX_W:
                cap_reason = f'n_W_raw={raw_w} > max_W={MAX_W}'
            else:
                useful_w = sum(bool(set(S) & B_de(W, neigh)) and
                               bool(set(T) & B_de(W, neigh)) for W in ws)
        cap_arcs = (bound_network_arcs(len(S), useful_w)
                    if useful_w is not None else None)
        f3 = f3_rows.get(name)
        if f3 is None and inst['tipo'] != 'source':
            raise AssertionError(f'{name}: nao tem linha F3 historica')
        # T5 exige OPT independente, nao computado de F-CC ou F-C3.
        opt_source = 'enum' if n <= N_OPT_ENUM else 'mip_base'
        if f3 and f3['fonte_opt'] != opt_source:
            raise AssertionError(f'{name}: fonte OPT historica difere')
        rows.append({
            'nome': name, 'tipo': inst['tipo'], 'n': n, 'm': len(S), 'r': r,
            'data_sha256': instance_hash(inst), 'k_hash': digest, 'n_K': len(K),
            'n_W_raw': raw_w, 'n_W_util': useful_w, 'network_arc_bound': cap_arcs,
            'fcc_cap_reason': cap_reason, 'fc3_cap_reason': cap_reason or (
                f'network_arc_bound={cap_arcs} > {ARC_CAP}'
                if cap_arcs is not None and cap_arcs > ARC_CAP else ''),
            'opt_source': opt_source,
        })
    data = {
        'task': 'N1-T5', 'state': 'FROZEN', 'frozen_utc': now(),
        'spec_sha256': sha_file(spec()), 'historical_f3_sha256': sha_file(F3),
        'pipeline_sha256': sha_file(Path(__file__)),
        'models_sha256': {name: sha_file(HERE / name) for name in
                          ('run_f3.py','fcc.py','fcc_k.py','fc3.py','source_controls_fc3_n1.py')},
        'historical_t3': evidence,
        'caps': {'n_max': N_MAX, 'max_W': MAX_W, 'n_opt_enum': N_OPT_ENUM,
                 'fc3_network_arcs': ARC_CAP},
        'solver': {'seed': SEED, 'threads': THREADS, 'lp_tolerance': EPS,
                   'hashseed': '0'},
        'K': "prepare_cuts(S,T,V,adj,A_r,r,{'C1','C2','C4'}); cortes_ordenados; sha256 fcc_k.prepare_k",
        'arms': list(ARMS),
        'metrics': {'B0': 'max(lp_comp, core_ip)',
                    'gamma': 'OPT-core_ip',
                    'delta_fcc': 'lp_fcc-B0', 'delta_fcc_k': 'lp_fcc_k-B0',
                    'delta_trio': 'lp_fc3_k-lp_fcc_k',
                    'delta_trio_raw': 'lp_fc3-lp_fcc',
                    'rho': '(lp_arm-B0)/(OPT-B0) somente se OPT>B0+1e-6',
                    'rho_fcc_historico': '(lp_fcc-B0)/(OPT-core_ip) se Gamma>1e-6'},
        'gate': 'spec.md / Gate / Promotion Criteria (inalterado)',
        'instances': rows,
    }
    save_new(FREEZE, json_bytes(data))
    print('FROZEN: hashes e caps registrados antes dos novos LPs')


def check_freeze():
    if os.environ.get('PYTHONHASHSEED') != '0':
        raise RuntimeError('Use PYTHONHASHSEED=0')
    data = load_json(FREEZE)
    if data['spec_sha256'] != sha_file(spec()) or data['historical_f3_sha256'] != sha_file(F3):
        raise RuntimeError('Spec ou CSV F3 historico alterado depois do freeze')
    if data['pipeline_sha256'] != sha_file(Path(__file__)):
        raise RuntimeError('Pipeline alterado depois do freeze')
    if any(sha_file(HERE / name) != digest for name, digest in data['models_sha256'].items()):
        raise RuntimeError('Modelos ou runner F3 alterados depois do freeze')
    if tuple(r['nome'] for r in data['instances']) != NAMES:
        raise RuntimeError('Corpus congelado nao coincide')
    for path, key in [('n1-t3-validacao.csv', 'validation_sha256'),
                      ('n1-t3-lp-invariantes.csv', 'lp_sha256'),
                      ('n1-t3-source-regressoes.csv', 'source_sha256')]:
        if data['historical_t3'][key] != sha_file(RESULTS / path):
            raise RuntimeError(f'Evidencia T3 alterada: {path}')
    if data['historical_t3']['r7_sha256'] != sha_file(ROOT / 'results' / 'benchmark' / 'n1-r7-auditoria-resumo.csv'):
        raise RuntimeError('Evidencia T4 mudou')
    if data['historical_t3']['mr_f3_sha256'] != sha_file(ROOT / 'docs' / 'technical' / 'reference' / 'formulacoes' / 'revisao-mr-f3-n1.md'):
        raise RuntimeError('MR-F3 mudou')
    return data


def equivalent_f3(a, b):
    for k in a:
        if k not in b:
            return f'coluna ausente: {k}'
        x, y = a[k], b[k]
        if k in NUMERIC_FIELDS and x not in ('', 'OPEN') and y not in ('', 'OPEN'):
            try:
                if abs(float(x) - float(y)) > EPS:
                    return f'{k}: {x} != {y}'
                continue
            except ValueError:
                pass
        if x != y:
            return f'{k}: {x!r} != {y!r}'
    return None


def reproduce():
    data = check_freeze()
    if F3_ATTEST.exists() or F3_REPRO.exists() or OUT.exists():
        raise RuntimeError('Reproducao ja iniciada: nao sobrescrever arquivos.')
    # Runner historico parametrizado por redirecionamento de CSV_PATH, sem alterar F3.
    code = ("import run_f3; from pathlib import Path; "
            "run_f3.CSV_PATH=Path(" + repr(str(F3_REPRO)) + "); run_f3.main()")
    env = dict(os.environ)
    env['PYTHONHASHSEED'] = '0'
    print('REPRODUZINDO F3 (arquivo historico sera preservado)', flush=True)
    cmd = [sys.executable, '-c', code]
    try:
        subprocess.run(cmd, cwd=HERE, env=env, check=True)
        old, new = read_csv(F3), read_csv(F3_REPRO)
        if len(old) != len(new):
            raise RuntimeError(f'F3 numero de linhas {len(new)} != {len(old)}')
        for a, b in zip(old, new):
            if a['nome'] != b['nome']:
                raise RuntimeError(f'F3 ordem/instancia distinta: {a["nome"]} / {b["nome"]}')
            diff = equivalent_f3(a, b)
            if diff:
                raise RuntimeError(f'F3 NAO REPRODUZIU {a["nome"]}: {diff}')
        # Verificacao do hash historico apos rerun.
        if sha_file(F3) != data['historical_f3_sha256']:
            raise RuntimeError('F3 historico foi alterado indevidamente')
        save_new(F3_ATTEST, json_bytes({
            'state': 'COMPUTATIONALLY VERIFIED', 'checked_utc': now(),
            'freeze_sha256': sha_file(FREEZE),
            'f3_historical_sha256': sha_file(F3), 'f3_reproduced_sha256': sha_file(F3_REPRO),
            'rows': len(old), 'eps': EPS, 'comparison': 'all fields/rows; numeric tolerance 1e-6',
        }))
        print('PASS F3 reproduzido; diferencas dentro de 1e-6')
    except Exception:
        print('STOP F3 NAO REPRODUZIU. Nao execute measure. Investigue sem re-congelar.', file=sys.stderr)
        raise


def require_attest():
    freeze_data = check_freeze()
    attest = load_json(F3_ATTEST)
    if attest['state'] != 'COMPUTATIONALLY VERIFIED' or attest['freeze_sha256'] != sha_file(FREEZE):
        raise RuntimeError('Reproducao F3 nao valida para este freeze')
    if attest['f3_reproduced_sha256'] != sha_file(F3_REPRO):
        raise RuntimeError('CSV da reproducao F3 alterado')
    return freeze_data


def checked(value, label):
    if value is None or not isinstance(value, (float, int)):
        raise RuntimeError(f'Valor nao numerico/inconclusivo: {label}={value!r}')
    return float(value)


def solve_and_witness(inst, K):
    """Testemunha completa: y* de F-CC e ao menos um corte de K violado."""
    from gurobipy import GRB
    from fcc import construir_modelo_fcc
    from cuts import vertices_do_corte
    S, T, V, A_r = (inst[k] for k in ('S', 'T', 'V', 'A_r'))
    model, y, _extra, _meta = construir_modelo_fcc(S, T, V, A_r, forma='separada', max_W=MAX_W)
    try:
        model.Params.OutputFlag = 0
        model.Params.Seed = SEED
        model.Params.Threads = THREADS
        model.Params.Method = 2
        model.optimize()
        if model.Status != GRB.OPTIMAL:
            raise RuntimeError(f'F-CC testemunha: status {model.Status}')
        ys = {str(v): float(y[v].X) for v in V}
        cuts = []
        for Z in K:
            vs = vertices_do_corte(Z, y)
            lhs = sum(float(y[v].X) for v in vs)
            if lhs < 1 - EPS:
                cuts.append({'Z': sorted(str(v) for v in Z), 'lhs': lhs,
                             'rhs': 1.0, 'violation': 1.0 - lhs})
        return {'instancia': inst['nome'], 'lp_fcc': float(model.ObjVal),
                'y_star': ys, 'violated_K': cuts, 'label': 'COMPUTATIONALLY VERIFIED'}
    finally:
        model.dispose()


def compatibility_witness(inst, prereg, K, k_hash, row):
    """Certificado de mecanismo: y* de COMP (já com K) não admite F-CC+K.

    Diferente de conectividade global: testa o próprio modelo F-CC+K com y
    fracionário congelado. Requer objetivo COMP abaixo do ótimo F-CC+K.
    """
    from gurobipy import GRB
    from harness import _make_mip
    from fcc_k import build_fcc_plus_k
    S, T, V, A_r, adj, r = (inst[k] for k in ('S', 'T', 'V', 'A_r', 'adj', 'r'))
    base, _y, _f, _ = _make_mip(S, T, V, A_r, 'cont', K)
    lp = base.relax()
    base.dispose()
    try:
        lp.Params.OutputFlag = 0
        lp.Params.Seed, lp.Params.Threads, lp.Params.Method = SEED, THREADS, 2
        lp.optimize()
        if lp.Status != GRB.OPTIMAL:
            raise RuntimeError('COMP testemunha sem LP otimo')
        y_star = {v: float(lp.getVarByName(f'y[{v}]').X) for v in V}
        z = float(lp.ObjVal)
        if abs(z - row['lp_comp']) > EPS:
            raise RuntimeError('COMP testemunha nao reproduziu LP COMP')
    finally:
        lp.dispose()
    model, _y2, _extra, _meta = build_fcc_plus_k(
        S, T, V, adj, A_r, r, K=K, k_hash=k_hash,
        max_W=MAX_W, y_fixo=y_star)
    try:
        model.Params.OutputFlag = 0
        model.Params.Threads = THREADS
        model.Params.Seed = SEED
        model.Params.DualReductions = 0
        model.optimize()
        if model.Status != GRB.INFEASIBLE:
            raise RuntimeError(f'F-CC+K fixo nao provou incompatibilidade: status {model.Status}')
        return {'instancia': inst['nome'], 'mechanism': 'COMP versus configuracoes conexas + K',
                'label': 'COMPUTATIONALLY VERIFIED', 'opt_lp_comp': z,
                'opt_lp_fcc_k': float(row['lp_fcc_k']), 'k_hash': k_hash,
                'y_star_comp': {str(v): value for v, value in y_star.items()},
                'status_fcc_k_y_fixed': 'INFEASIBLE (Gurobi GRB.INFEASIBLE)',
                'explanation': 'O y* do LP COMP, que satisfaz todo K, nao admite extensao F-CC+K.'}
    finally:
        model.dispose()


def trio_witness(inst, K, k_hash, row):
    """LP ótimo F-CC+K cuja projeção y não é extensível à F-C3+K."""
    from gurobipy import GRB
    from fcc_k import build_fcc_plus_k
    from fc3 import build_fc3_plus_k
    S, T, V, adj, A_r, r = (inst[k] for k in ('S','T','V','adj','A_r','r'))
    model, y, _, _ = build_fcc_plus_k(S,T,V,adj,A_r,r,K=K,k_hash=k_hash,max_W=MAX_W)
    try:
        model.Params.OutputFlag = 0
        model.Params.Seed, model.Params.Threads, model.Params.Method = SEED, THREADS, 2
        model.optimize()
        if model.Status != GRB.OPTIMAL or abs(float(model.ObjVal)-row['lp_fcc_k']) > EPS:
            raise RuntimeError('Testemunha F-CC+K: nao reproduziu LP otimo')
        values = {v: float(y[v].X) for v in V}
    finally:
        model.dispose()
    model, _, _, _ = build_fc3_plus_k(S,T,V,adj,A_r,r,K=K,k_hash=k_hash,
                                     max_W=MAX_W,max_network_arcs=ARC_CAP,y_fixo=values)
    try:
        model.Params.OutputFlag = 0
        model.Params.Threads = THREADS
        model.Params.Seed = SEED
        model.Params.DualReductions = 0
        model.optimize()
        if model.Status != GRB.INFEASIBLE:
            raise RuntimeError('Testemunha trio: F-C3+K fixo nao provou inviabilidade')
        return {'instancia': inst['nome'], 'mechanism': 'consistencia de trios',
                'label': 'COMPUTATIONALLY VERIFIED', 'opt_lp_fcc_k': row['lp_fcc_k'],
                'opt_lp_fc3_k': row['lp_fc3_k'], 'k_hash': k_hash,
                'y_star_fcc_k': {str(v): x for v,x in values.items()},
                'status_fc3_k_y_fixed': 'INFEASIBLE (Gurobi GRB.INFEASIBLE)'}
    finally:
        model.dispose()


def compute_metrics(row):
    """Métricas congeladas; não truncar incrementos negativos."""
    if row['opt'] == '' or row['lp_comp'] == '' or row['core_ip'] == '':
        raise ValueError('OPT, LP COMP e core IP obrigatórios para B0')
    b0 = max(row['lp_comp'], row['core_ip'])
    row['B0'] = b0
    row['gamma'] = row['opt'] - row['core_ip']
    for field, first, second in [
        ('delta_fcc', 'lp_fcc', None), ('delta_fcc_k', 'lp_fcc_k', None),
        ('delta_trio', 'lp_fc3_k', 'lp_fcc_k'),
        ('delta_trio_raw', 'lp_fc3', 'lp_fcc')]:
        if row[first] != '' and (second is None or row[second] != ''):
            row[field] = row[first] - (b0 if second is None else row[second])
    if row['opt'] > b0 + EPS:
        for arm in ('lp_fcc', 'lp_fcc_k', 'lp_fc3', 'lp_fc3_k'):
            if row[arm] != '':
                row['rho_' + arm.removeprefix('lp_')] = (row[arm] - b0) / (row['opt'] - b0)
    if row['gamma'] > EPS and row['lp_fcc'] != '':
        row['rho_fcc_historico'] = (row['lp_fcc'] - b0) / row['gamma']
    return row


def measure_one(inst, prereg, f3):
    from fcc_k import lp_fcc_plus_k, prepare_k
    from fc3 import lp_fc3, lp_fc3_plus_k
    from fcc import lp_fcc
    from harness import measure_lp
    from independent_validator import opt_por_enumeracao
    from medir import nucleo, otimo_base
    S, T, V, adj, A_r, r = (inst[k] for k in ('S', 'T', 'V', 'adj', 'A_r', 'r'))
    if prereg['data_sha256'] != instance_hash(inst):
        raise RuntimeError('Instancia mudou desde freeze: ' + inst['nome'])
    K, digest, _counts = prepare_k(S, T, V, adj, A_r, r)
    if digest != prereg['k_hash'] or len(K) != prereg['n_K']:
        raise RuntimeError('K mudou desde freeze: ' + inst['nome'])
    row = {key: '' for key in FIELDS}
    row.update(instancia=inst['nome'], tipo=prereg['tipo'], n=prereg['n'],
               m=prereg['m'], r=prereg['r'], k_hash=digest, n_K=len(K),
               n_W_raw=prereg['n_W_raw'], n_W_util=prereg['n_W_util'],
               network_arc_bound=prereg['network_arc_bound'],
               opt_source=prereg['opt_source'], source_f3='historical_and_reproduced' if f3 else 'measured_new')
    for arm in ARMS:
        row['status_' + arm] = 'NOT MEASURED'
    witness = None
    if f3 is not None:
        for field, f3_field in [('lp_base', 'lp_base'), ('lp_comp', 'lp_c1c2c4'),
                                ('core_ip', 'nucleo'), ('opt', 'opt')]:
            if f3[f3_field] != '':
                row[field] = float(f3[f3_field])
                row['status_' + field] = 'COMPUTATIONALLY VERIFIED'
        if f3['lp_fcc'] != '':
            row['lp_fcc'] = float(f3['lp_fcc'])
            row['status_lp_fcc'] = 'COMPUTATIONALLY VERIFIED'
    else:
        # SOURCE nao estava no F3; mesmos solvers/parametros do runner F3.
        for arm, cuts in [('lp_base', []), ('lp_comp', K)]:
            res = measure_lp(S, T, V, A_r, 'cont', cuts, seed=SEED, threads=THREADS)
            row[arm] = checked(res['lp_bound'], arm)
            row['status_' + arm] = 'COMPUTATIONALLY VERIFIED'
        row['core_ip'] = checked(nucleo(S, T, V, adj, r), 'core IP')
        row['status_core_ip'] = 'COMPUTATIONALLY VERIFIED'
        if prereg['opt_source'] == 'enum':
            row['opt'] = checked(opt_por_enumeracao(S, T, V, adj, r), 'OPT enum')
        elif prereg['opt_source'] == 'mip_base':
            row['opt'] = checked(otimo_base(S, T, V, adj, r), 'OPT base MIP')
        else:
            raise RuntimeError('Fonte OPT proibida')
        row['status_opt'] = 'COMPUTATIONALLY VERIFIED'
        from source_controls_fc3_n1 import make_source_g2, make_source_c5
        source_meta = (make_source_g2() if inst['nome'] == 'SOURCE-g2' else make_source_c5())[-1]
        if abs(row['opt'] - float(source_meta['opt_expected'])) > EPS:
            raise RuntimeError(f'{inst["nome"]}: OPT certificado diverge da previsão SOURCE')
    if row['opt'] == '':
        raise RuntimeError(f'{inst["nome"]}: sem OPT certificado')
    if f3 and (f3['fonte_opt'] != prereg['opt_source']):
        raise RuntimeError('Fonte OPT F3 nao coincide')
    if prereg['fcc_cap_reason']:
        for arm in ('lp_fcc', 'lp_fcc_k'):
            row['reason_' + arm] = prereg['fcc_cap_reason']
            row['status_' + arm] = 'NOT MEASURED'
        for arm in ('lp_fc3', 'lp_fc3_k'):
            row['reason_' + arm] = prereg['fc3_cap_reason']
            row['status_' + arm] = 'NOT MEASURED'
        row['lp_fcc'] = ''
    else:
        if row['lp_fcc'] == '':
            z, _meta = lp_fcc(S, T, V, A_r, forma='separada', max_W=MAX_W,
                               seed=SEED, threads=THREADS)
            row['lp_fcc'] = checked(z, 'F-CC')
            row['status_lp_fcc'] = 'COMPUTATIONALLY VERIFIED'
        z, meta = lp_fcc_plus_k(S, T, V, adj, A_r, r, K=K, k_hash=digest,
                                max_W=MAX_W, seed=SEED, threads=THREADS)
        row['lp_fcc_k'] = checked(z, 'F-CC+K')
        row['status_lp_fcc_k'] = 'COMPUTATIONALLY VERIFIED'
        row['n_vars_fcc_k'], row['n_cons_fcc_k'] = meta['n_vars'], meta['n_cons']
        if row['lp_fcc_k'] > row['lp_fcc'] + EPS:
            witness = solve_and_witness(inst, K)
            if abs(witness['lp_fcc'] - row['lp_fcc']) > EPS or not witness['violated_K']:
                raise RuntimeError(f'{inst["nome"]}: ganho K sem testemunha C1/C2/C4-DM')
    if prereg['fc3_cap_reason']:
        for arm in ('lp_fc3', 'lp_fc3_k'):
            row['reason_' + arm] = prereg['fc3_cap_reason']
            row['status_' + arm] = 'NOT MEASURED'
    else:
        z, meta = lp_fc3(S, T, V, A_r, max_W=MAX_W,
                         max_network_arcs=ARC_CAP, seed=SEED, threads=THREADS)
        row['lp_fc3'] = checked(z, 'F-C3')
        row['status_lp_fc3'] = 'COMPUTATIONALLY VERIFIED'
        row['n_vars_fc3'], row['n_cons_fc3'] = meta['n_vars'], meta['n_cons']
        z, meta = lp_fc3_plus_k(S, T, V, adj, A_r, r, K=K, k_hash=digest,
                                max_W=MAX_W, max_network_arcs=ARC_CAP,
                                seed=SEED, threads=THREADS)
        row['lp_fc3_k'] = checked(z, 'F-C3+K')
        row['status_lp_fc3_k'] = 'COMPUTATIONALLY VERIFIED'
        row['n_vars_fc3_k'], row['n_cons_fc3_k'] = meta['n_vars'], meta['n_cons']
    for arm in ('lp_base', 'lp_comp', 'lp_fcc', 'lp_fcc_k', 'lp_fc3', 'lp_fc3_k'):
        if row[arm] != '' and row[arm] > row['opt'] + EPS:
            raise RuntimeError(f'{inst["nome"]}: INVARIANTE {arm} > OPT')
    for stronger, weaker in [('lp_fc3', 'lp_fcc'), ('lp_fc3_k', 'lp_fcc_k'),
                             ('lp_fcc_k', 'lp_fcc'), ('lp_fc3_k', 'lp_fc3')]:
        if row[stronger] != '' and row[weaker] != '' and row[stronger] + EPS < row[weaker]:
            raise RuntimeError(f'{inst["nome"]}: INVARIANTE {stronger} < {weaker}')
    if row['core_ip'] != '' and row['core_ip'] > row['opt'] + EPS:
        raise RuntimeError(f'{inst["nome"]}: INVARIANTE core IP > OPT')
    compute_metrics(row)
    if inst['nome'] in ('SOURCE-g2', 'SOURCE-C5') and row['lp_fc3'] != '':
        expected = 4.0 if inst['nome'] == 'SOURCE-g2' else 2.5
        if abs(row['lp_fc3'] - expected) > EPS:
            raise RuntimeError(f'{inst["nome"]}: LP F-C3 diverge da SOURCE')
    return row, witness


def measure():
    frozen = require_attest()
    if OUT.exists() or WITNESSES.exists():
        raise RuntimeError('Diagnostico ja existe; nao sobrescrever ou rerodar seletivamente.')
    old = {r['nome']: r for r in read_csv(F3_REPRO)}
    rows, witnesses = [], []
    compatibility_done = False
    trio_done = False
    try:
        for inst, pre in zip(corpus(), frozen['instances']):
            print('MEDINDO T5', inst['nome'], flush=True)
            row, witness = measure_one(inst, pre, old.get(inst['nome']))
            rows.append(row)
            if witness:
                witnesses.append(witness)
            # Primeiro caso elegível na ordem FROZEN, nunca escolhido pós-resultado.
            if (not compatibility_done and row['lp_fcc_k'] != '' and
                row['lp_fcc_k'] > row['B0'] + EPS and
                row['lp_comp'] + EPS < row['lp_fcc_k'] and
                row['gamma'] > EPS):
                from fcc_k import prepare_k
                k, kh, _ = prepare_k(*(inst[z] for z in ('S','T','V','adj','A_r','r')))
                witnesses.append(compatibility_witness(inst, pre, k, kh, row))
                compatibility_done = True
            if (not trio_done and row['delta_trio'] != '' and
                row['delta_trio'] > EPS and row['lp_fcc_k'] < row['opt'] - EPS):
                from fcc_k import prepare_k
                k, kh, _ = prepare_k(*(inst[z] for z in ('S','T','V','adj','A_r','r')))
                witnesses.append(trio_witness(inst, k, kh, row))
                trio_done = True
            print(' ', 'OPT', row['opt'], 'FCC+K', row['lp_fcc_k'],
                  'FC3+K', row['lp_fc3_k'], flush=True)
            write_csv(OUT, rows)  # checkpoint parcial identificavel por 18/18
            WITNESSES.write_bytes(json_bytes({'state':'IN PROGRESS','rows':witnesses}))
    except Exception:
        print('STOP: T5 parcial; CSV tem somente linhas concluídas, NAO usar para gate.', file=sys.stderr)
        raise
    WITNESSES.write_bytes(json_bytes({'state': 'COMPUTATIONALLY VERIFIED',
                                     'freeze_sha256': sha_file(FREEZE), 'rows': witnesses}))
    make_report(rows, witnesses)
    print('T5 concluida: CSV, testemunhas e relatorio. Gate N1-T7 ainda nao executado.')


def make_report(rows, witnesses):
    if len(rows) != len(NAMES):
        raise RuntimeError('Nao gerar relatorio conclusivo com CSV incompleto')
    useful = [r for r in rows if r['lp_fcc_k'] != '' and r['opt'] != '' and
              r['gamma'] != '' and r['gamma'] > EPS and r['lp_fcc_k'] < r['opt'] - EPS]
    types = sorted(set(r['tipo'] for r in useful))
    t5 = ['# N1-T5 — Diagnóstico congelado', '',
          '**Status:** `COMPUTATIONALLY VERIFIED` para braços medidos; demais `NOT MEASURED`. ',
          '**Base:** spec N1, seção Experimental Pre-registration. Não é decisão N1-T7.',
          '', f'**Freeze SHA-256:** `{sha_file(FREEZE)}`',
          f'**Reprodução F3:** `{sha_file(F3_REPRO)}`',
          f'**Casos registrados:** {len(rows)} (16 F3 + 2 SOURCE).',
          '', '## Matriz de inclusão e ablação', '',
          '| Braço | Informação acrescida |', '|---|---|',
          '| LP base | Fluxo U sem K |', '| LP COMP | Fluxo U + K |',
          '| core IP | Cobertura inteira em y + K; limitante inferior, NÃO solução |',
          '| LP F-CC | Configurações conexas sem K |',
          '| LP F-CC+K | Configurações conexas + mesmo K congelado |',
          '| LP F-C3 | Consistência de trios sem K |',
          '| LP F-C3+K | Consistência de trios + mesmo K congelado |',
          '| OPT | Oracle independente (enum/MIP base) |',
          '', '## Comparação por instância', '',
          '| Instância | Tipo | B0 | OPT | LP FCC | LP FCC+K | LP FC3 | LP FC3+K | ΔFCC | ΔFCC+K | Δtrio |',
          '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    def fmt(v):
        return f'{v:.6g}' if isinstance(v, (int, float)) else 'NOT MEASURED'
    for r in rows:
        t5.append('| ' + ' | '.join([
            r['instancia'], r['tipo'], *[fmt(r[k]) for k in
            ('B0','opt','lp_fcc','lp_fcc_k','lp_fc3','lp_fc3_k',
             'delta_fcc','delta_fcc_k','delta_trio')]]) + ' |')
    t5.extend(['', '## Controle de mecanismo e caps', '',
               f'- Casos com Γ>0 e residual F-CC+K: {len(useful)}; famílias: {types}.',
               '- Regra N1-T6: **ativar somente se menos de duas famílias distintas** acima.',
               f'- Gatilho calculado: {"ATIVADO" if len(types) < 2 else "NÃO ATIVADO"}.',
               f'- Registros de testemunha: {len(witnesses)};',
               '  os vetores y* e status do modelo fixado estão em `results/alternative-formulations/n1-t5-testemunhas.json`.',
               '- Diferenças negativas (ex. SharedTerminal) preservadas sem truncamento.',
               '- Status NOT MEASURED e seus limites devem ser lidos no CSV, nunca como ganho zero.',
               '- Não inferir melhora de tempo de CPU a partir de valores LP.',
               '', '## Testemunhas de complementaridade', ''])
    if not witnesses:
        t5.append('Nenhuma diferença LP F-CC+K > F-CC produziu testemunha K; mecanismo positivo não demonstrado.')
    for w in witnesses:
        if w.get('violated_K'):
            first = w['violated_K'][0]
            t5.append(f'- **{w["instancia"]}**: ponto ótimo y* da F-CC com objetivo '
                      f'{w["lp_fcc"]:.7g}, corte K violado Z={first["Z"]} '
                      f'(Σy*={first["lhs"]:.7g} < 1); vetor completo em JSON.')
        elif w.get('mechanism') == 'consistencia de trios':
            t5.append(f'- **{w["instancia"]}**: F-CC+K={w["opt_lp_fcc_k"]:.7g} '
                      f'(< F-C3+K={w["opt_lp_fc3_k"]:.7g}); vetor ótimo y* do F-CC+K '
                      'não admite extensão F-C3+K (status INFEASIBLE). Prova computacional local em JSON.')
        elif 'mechanism' in w:
            t5.append(f'- **{w["instancia"]}**: LP COMP={w["opt_lp_comp"]:.7g} '
                      f'(< LP F-CC+K={w["opt_lp_fcc_k"]:.7g}), e o vetor ótimo y* '
                      'do COMP torna F-CC+K inviável quando fixado. Vetor completo, hash K '
                      'e status em JSON. Testemunha computacional apenas no caso nomeado.')
    t5.extend(['', '## Limitações', '',
               '- Ganho é suportado apenas no conjunto pré-registrado; não é prova global.',
               '- SOURCE-g2/C5 são controles antigos, não pares sintéticos de N1-T6.',
               '- Este relatório não aplica o gate promocional N1-T7.', ''])
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text('\n'.join(t5), encoding='utf8')
    print('RELATORIO', REPORT)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=('freeze', 'reproduce-f3', 'measure', 'report'))
    args = parser.parse_args()
    if args.phase == 'freeze':
        freeze()
    elif args.phase == 'reproduce-f3':
        reproduce()
    elif args.phase == 'measure':
        measure()
    else:
        data = require_attest()
        rows = read_csv(OUT)
        if len(rows) != len(NAMES) or tuple(r['instancia'] for r in rows) != NAMES:
            raise RuntimeError('CSV incompleto; relatorio/gate proibido')
        converted = []
        for row in rows:
            for field in FIELDS:
                if field in ('n','m','r','n_K','n_W_raw','n_W_util','network_arc_bound','opt',
                             'lp_base','lp_comp','core_ip','lp_fcc','lp_fcc_k', 'lp_fc3',
                             'lp_fc3_k','gamma','B0','delta_fcc','delta_fcc_k',
                             'delta_trio','delta_trio_raw','rho_fcc','rho_fcc_k',
                             'rho_fc3','rho_fc3_k','rho_fcc_historico'):
                    if row[field] not in ('', None):
                        row[field] = float(row[field])
            converted.append(row)
        witnesses = load_json(WITNESSES)
        if witnesses['state'] != 'COMPUTATIONALLY VERIFIED':
            raise RuntimeError('Testemunhas incompletas')
        make_report(converted, witnesses['rows'])


if __name__ == '__main__':
    main()
