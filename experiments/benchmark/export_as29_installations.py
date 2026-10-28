"""AS29 (evidência posterior): exporta e valida a instalação final de U e U_K.

Nota: não liga o callback de incumbente da linha de base (só mede tempos); a reprodução 46/46 mostra que o resultado não mudou.

Reproduz a configuração da linha de base Spec A (WorkLimit=164, 4 threads, guarda de
parede de 1800 s, sem MIP start, seed 42) para casos de desenvolvimento que não têm
instalação arquivada, valida a instalação final no oráculo independente e grava um
JSON por (caso, braço) em results/benchmark/as29-physical-ub-001/.

Não altera linha_base.csv nem outra fonte. Os arquivos gravados são evidência obtida
depois da AS29 original; a UB física daqui pode diferir da incumbente histórica.
Retoma pelos arquivos já gravados.

Uso: poetry run python experiments/benchmark/export_as29_installations.py [--shard i/N] [--cases a,b] [--dry-run]
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT, ROOT / 'experiments' / 'cuts', ROOT / 'experiments' / 'structural'):
    sys.path.insert(0, str(p))

OUT = ROOT / 'results' / 'benchmark' / 'as29-physical-ub-001'
SEED, THREADS, WORK_LIMIT, GUARD_S = 42, 4, 164.0, 1800
ARMS = ('U', 'U_K')
SCHEMA = 'AS29-PHYSICAL-UB-v1'


TARGET_CASES = (
    'b-b06-intercalado-f2.txt',
    'b-b06-regiao-f2.txt',
    'b-b12-intercalado-f2.txt',
    'b-b12-regiao-f2.txt',
    'b-b18-intercalado-f2.txt',
    'lin-lin06-intercalado-f2.txt',
    'lin-lin06-regiao-f4.txt',
    'pace18-t2-141-regiao-f4.txt',
    'pace18-t2-199-regiao-f4.txt',
    'puc-bip42p-seed-r1.txt',
    'puc-cc10-2u-regiao-f2.txt',
    'puc-cc10-2u-seed-r1.txt',
    'puc-cc11-2u-seed-r1.txt',
    'puc-cc12-2u-seed-r1.txt',
    'puc-cc6-3p-seed-r1.txt',
    'puc-w23c23-intercalado-f2-rho.txt',
    'puc-w23c23-seed-r1.txt',
    'pucn-cc3-5n-seed-r1.txt',
    'pucn-cc5-3n-seed-r1.txt',
    'pucn-cc6-2n-seed-r1.txt',
    'urb-mindelo-m25-f4.txt',
    'vienna-I065-intercalado-f2.txt',
    'vienna-I065-regiao-f4.txt',
)
# Lista fixada: os 23 casos de desenvolvimento sem instalação arquivada em AS06/AS09 quando a exportação foi lançada
# (18/10/2026). Não deriva do CSV de casos, que o auditor sobrescreve.


def targets():
    with (ROOT / 'instances/manifest.csv').open(encoding='utf-8') as f:
        rows = [r for r in csv.DictReader(f) if r['classe'] == 'principal' and r['particao'] == 'desenvolvimento' and r['nome'] in TARGET_CASES]
    assert len(rows) == len(TARGET_CASES), 'manifesto não contém todos os casos-alvo em desenvolvimento'
    rows.sort(key=lambda r: (float(r['n'] or 0), r['nome']))
    return rows


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def solve(row, arm):
    from gurobipy import GRB
    import gurobipy
    from harness import load_instance, prepare_cuts, _make_mip
    from independent_validator import viavel
    S, T, V, adj, A_r, r = load_instance(ROOT / row['caminho'], R=float(row['r_usado']))
    t0 = time.monotonic()
    if arm == 'U':
        cuts, f_type, n_cuts = [], 'int', 0
    else:
        cortes, counts = prepare_cuts(S, T, V, adj, A_r, r, {'C1', 'C2', 'C4'})
        cuts, f_type, n_cuts = list(cortes), 'cont', counts['unicos']
    model, y, _f, _ = _make_mip(S, T, V, A_r, f_type, cuts)
    model.Params.OutputFlag = 0
    model.Params.Seed = SEED
    model.Params.Threads = THREADS
    model.Params.TimeLimit = GUARD_S
    model.setParam('WorkLimit', WORK_LIMIT)
    t_model = time.monotonic() - t0
    t1 = time.monotonic()
    model.optimize()
    t_solve = time.monotonic() - t1
    status = model.Status
    out = {'status': {GRB.OPTIMAL: 'OPTIMAL_NUMERIC'}.get(status, 'WORK_LIMIT' if status == GRB.WORK_LIMIT else f'GUROBI_STATUS_{status}'),
           'gurobi_status': int(status), 'mip_numeric_bound': float(model.ObjBound), 'work': float(model.Work),
           'nodes': float(model.NodeCount), 'solver_runtime_s': t_solve, 'model_build_s': t_model, 'n_k_cuts': n_cuts,
           'gurobi_version': '.'.join(map(str, gurobipy.gurobi.version())), 'installed': None,
           'mip_numeric_incumbent': None, 'physical_validated_ub': None, 'invalid_incumbents': 0}
    if model.SolCount > 0:
        out['mip_numeric_incumbent'] = float(model.ObjVal)
        installed = sorted(str(v) for v in V if y[v].X > 0.5)
        out['installed'] = installed
        # Oráculo independente (grafo original); não usa o modelo nem A_r.
        if viavel(S, T, V, adj, int(r), installed):
            out['physical_validated_ub'] = len(installed)
        else:
            out['invalid_incumbents'] = 1
    model.dispose()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--shard', default='0/1', help='i/N: processa os casos de índice ≡ i (mod N)')
    ap.add_argument('--cases', default='', help='lista de nomes (com .txt) separados por vírgula')
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    i, n = map(int, a.shard.split('/'))
    rows = targets()
    if a.cases:
        keep = set(a.cases.split(','))
        rows = [r for r in rows if r['nome'] in keep]
    rows = [r for k, r in enumerate(rows) if k % n == i]
    OUT.mkdir(parents=True, exist_ok=True)
    from io_instancia import commit_atual
    commit = commit_atual()
    for row in rows:
        for arm in ARMS:
            path = OUT / f"{row['nome'][:-4]}--{arm}.json"
            if path.exists():
                continue
            print(f"{row['nome']} {arm} n={row['n']}" + (' [dry-run]' if a.dry_run else ''), flush=True)
            if a.dry_run:
                continue
            t0 = time.monotonic()
            res = solve(row, arm)
            rec = {'schema': SCHEMA, 'case_name': row['nome'], 'arm_id': arm, 'instance_sha256': sha256_file(ROOT / row['caminho']),
                   'seed': SEED, 'threads': THREADS, 'work_limit': WORK_LIMIT, 'guard_s': GUARD_S, 'commit': commit,
                   'protocol': 'Spec A R4 config (linha_base.csv); posterior evidence, not part of the original run',
                   'finished_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), **res}
            data = json.dumps(rec, sort_keys=True, indent=1).encode('utf-8')
            tmp = path.with_suffix('.tmp');tmp.write_bytes(data);tmp.replace(path)
            path.with_suffix('.sha256').write_text(hashlib.sha256(data).hexdigest() + '\n', encoding='utf-8')
            print(f"  -> {rec['status']} lb={rec['mip_numeric_bound']:.3f} ub={rec['mip_numeric_incumbent']} "
                  f"phys={rec['physical_validated_ub']} work={rec['work']:.1f} {time.monotonic()-t0:.0f}s", flush=True)


if __name__ == '__main__':
    main()
