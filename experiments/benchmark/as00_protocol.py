"""AS-00: inventário e identidade de instâncias, sem dependência de F-CC."""
from __future__ import annotations

import argparse
from collections import defaultdict, deque
import csv
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'experiments' / 'formulation-comparison'))
from fc_instances import load_instance  # noqa: E402 (reutiliza loader e verificações existentes)
from as00_families import annotate_related, load_specs, normalized_name, raw_family_keys  # noqa: E402

EXPECTED_COUNTS = {'desenvolvimento': 14, 'avaliacao': 17}

PILOT = (
    'puc-cc9-2p-seed-r1', 'puc-bip42p-regiao-f2',
    'pucn-cc3-10n-seed-r1', 'mapf-room-32-32-4-m10-f8',
    'vienna-I056-regiao-f4', 'puc-w3c571-seed-r1',
)


def digest(value) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True,
                         separators=(',', ':')).encode('utf-8')
    return hashlib.sha256(payload).hexdigest()


def raw_graph_edges(instance) -> list[tuple[str, str, float]]:
    arcs = {}
    for u, successors in instance.adj.items():
        for v, weight in successors:
            key = (u, v)
            if key in arcs and arcs[key] != weight:
                raise ValueError(f'INTEGRITY_ERROR: aresta conflitante: {u}->{v}')
            arcs[key] = weight
    for (u, v), weight in arcs.items():
        if arcs.get((v, u)) != weight or u == v:
            raise ValueError(f'INTEGRITY_ERROR: grafo não-direcionado inválido: {u}->{v}')
    return sorted((min(u, v), max(u, v), weight)
                  for (u, v), weight in arcs.items() if u < v)


def fingerprint_case(row: dict, root: Path, spec_by_name: dict[str, dict]) -> dict:
    inst = load_instance(row, root=root)
    if len(set(inst.S)) != inst.m or len(set(inst.T)) != inst.m:
        raise ValueError(f'INTEGRITY_ERROR: terminais repetidos: {row["nome"]}')
    if inst.r <= 0:
        raise ValueError(f'INTEGRITY_ERROR: autonomia inválida: {row["nome"]}')
    raw_graph_id, family_id = raw_family_keys(row, spec_by_name)
    edges = raw_graph_edges(inst)
    adj_u = defaultdict(set)
    for u, v, w in edges:
        adj_u[u].add(v)
        adj_u[v].add(u)
        if 'benchmark-v1/' in row['caminho'] and w != 1.0:
            raise ValueError(f'INTEGRITY_ERROR: aresta não-unitária: {row["nome"]}')
    if inst.V:
        reached = {inst.V[0]}
        q = deque([inst.V[0]])
        while q:
            for v in adj_u[q.popleft()]:
                if v not in reached:
                    reached.add(v)
                    q.append(v)
        if reached != set(inst.V):
            raise ValueError(f'INTEGRITY_ERROR: grafo desconexo: {row["nome"]}')
    if row.get('n_arcos_alcance'):
        declared = int(row['n_arcos_alcance'])
        if declared != len(set(inst.A_r)):
            raise ValueError(f'INTEGRITY_ERROR: n_arcos_alcance divergente: {row["nome"]}')
    gh = digest({'V': sorted(inst.V), 'E': edges})
    sh = digest(sorted(inst.S))
    th = digest(sorted(inst.T))
    ah = digest(sorted(set(inst.A_r)))
    # A equivalência de alcance usa S/T/A_r, mas NÃO finge que G ou r são idênticos.
    reach_id = digest({'S': sh, 'T': th, 'A_r': ah})
    return {
        'name': normalized_name(row['nome']), 'manifest_name': row['nome'],
        'source_file': row['caminho'], 'source_sha256': inst.instance_sha256,
        'source_content_sha256': inst.instance_content_sha256,
        'family': inst.familia, 'raw_graph_id': raw_graph_id,
        'family_id': family_id,
        'split': row['particao'], 'historical_difficulty': row['dificuldade'],
        'n': inst.n, 'm': inst.m, 'r': inst.r, 'a_r_count': len(set(inst.A_r)),
        'graph_hash': gh, 'S_hash': sh, 'T_hash': th, 'A_r_hash': ah,
        'reach_equivalence_id': reach_id,
        'pilot': normalized_name(row['nome']) in PILOT,
        'comparison_eligible': True,  # Não condicionado a enumeração de W/F-CC
    }


def manifest_rows(root: Path) -> list[dict]:
    with (root / 'instances/manifest.csv').open(encoding='utf-8', newline='') as fh:
        return list(csv.DictReader(fh))


def build_universe(root: Path = ROOT) -> dict:
    rows = manifest_rows(root)
    selected = [r for r in rows if r['classe'] == 'principal'
                and r['caminho'].startswith('instances/benchmark-v1/')
                and r['dificuldade'] in ('D', 'A')]
    if len({normalized_name(r['nome']) for r in selected}) != len(selected):
        raise ValueError('INTEGRITY_ERROR: nomes normalizados colidem')
    specs = load_specs(root / 'instances/benchmark-v1/spec.csv')
    cases = [fingerprint_case(r, root, specs) for r in selected]
    cases.sort(key=lambda x: x['name'])
    annotate_related(cases)
    counts = {p: sum(c['split'] == p for c in cases)
              for p in ('desenvolvimento', 'avaliacao')}
    if counts != EXPECTED_COUNTS:
        raise ValueError(f'INTEGRITY_ERROR: universo D/A diverge do snapshot: {counts}')
    pilot_names = {c['name'] for c in cases if c['pilot']}
    if pilot_names != set(PILOT):
        raise ValueError(f'PILOT_INVALID: faltam {sorted(set(PILOT) - pilot_names)}')
    if any(c['split'] != 'desenvolvimento' for c in cases if c['pilot']):
        raise ValueError('PILOT_INVALID: piloto contém instância de avaliação')
    return {'schema': 'as00-universe-v1', 'manifest_file': 'instances/manifest.csv',
            'manifest_sha256': hashlib.sha256((root / 'instances/manifest.csv').read_bytes()).hexdigest(),
            'counts': counts, 'cases': cases}


def retain_outcome(cases: list[dict], case_name: str, status: str) -> list[dict]:
    """O resultado de um braço modifica só status no relatório derivado, nunca o denominador."""
    valid = {'NOT_RUN', 'OPTIMAL', 'TIME_LIMIT', 'NOT_MEASURED_INPUT',
             'NOT_MEASURED_CAP', 'NOT_MEASURED_MEMORY', 'NOT_MEASURED_BUDGET', 'ERROR'}
    if status not in valid:
        raise ValueError(f'status não reconhecido: {status}')
    if case_name not in {c['name'] for c in cases}:
        raise KeyError(case_name)
    return [{**c, 'outcome': status if c['name'] == case_name else c.get('outcome', 'NOT_RUN')}
            for c in cases]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    from as00_preregister import write_preregistration
    uni = build_universe(args.root)
    target = write_preregistration(uni, args.output_dir)
    print(f'AS00 pré-registro criado: {target}')
    print(f'Casos: {len(uni["cases"])}; divisões: {uni["counts"]}')


if __name__ == '__main__':
    main()
