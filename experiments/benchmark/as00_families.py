"""Identificação de famílias sem confundir variante MAPF com caso independente."""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


def normalized_name(name: str) -> str:
    return Path(name).stem


def raw_family_keys(row: dict, spec_by_name: dict[str, dict]) -> tuple[str, str]:
    """Retorna (grafo bruto, grafo+cenário) usando proveniência, não m/r.

    Uma proveniência desconhecida é erro, nunca evidência de independência.
    """
    name = normalized_name(row['nome'])
    parts = row['caminho'].split('/')
    family = parts[2] if len(parts) > 2 and parts[1] == 'benchmark-v1' else 'legado'
    original = (row.get('instancia_original') or '').strip()
    if family == 'mapf':
        spec = spec_by_name.get(name)
        if spec is None or not spec.get('arquivo_fonte') or '.scen' not in original:
            raise ValueError(f'Proveniência MAPF insuficiente: {name}')
        scenario = original.split('(')[0].strip()
        mapfile = spec['arquivo_fonte'].strip()
        graph = f'mapf:map:{mapfile}'
        return graph, f'{graph}|scenario:{scenario}'
    if not original:
        raise ValueError(f'Proveniência original ausente: {name}')
    key = f'{family}:{original}'
    return key, key


def load_specs(path: Path) -> dict[str, dict]:
    with path.open(encoding='utf-8', newline='') as fh:
        rows = list(csv.DictReader(fh))
    return {row['nome']: row for row in rows}


def annotate_related(cases: list[dict]) -> None:
    """Marca parentesco D/A, preservando todos os casos no universo."""
    dev = defaultdict(list)
    dev_graph = defaultdict(list)
    for case in cases:
        if case['split'] == 'desenvolvimento':
            dev[case['family_id']].append(case['name'])
            dev_graph[case['raw_graph_id']].append(case['name'])
    for case in cases:
        if case['split'] != 'avaliacao':
            case['independence'] = 'DEVELOPMENT'
            case['related_development'] = []
            continue
        related = sorted(dev[case['family_id']])
        same_graph = sorted(dev_graph[case['raw_graph_id']])
        case['related_development'] = related
        case['same_raw_graph_development'] = same_graph
        case['independence'] = ('RELATED_SCENARIO' if related else
                                'RELATED_RAW_GRAPH' if same_graph else 'INDEPENDENT_RAW_SOURCE')
