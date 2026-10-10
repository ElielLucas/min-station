"""FC-04: inventário determinístico de artefatos e contagens medidas.

Manifestos usam caminhos relativos à raiz do repositório e SHA-256 de bytes.
Nenhum resultado de solver é reclassificado ou certificado aqui.
"""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

SCHEMA = 'FC04-v1'
PRIMARY_CAP_STATUSES = frozenset({'CAP_EXCEEDED', 'NOT_MEASURED_CAP_EXCEEDED'})
FCC_OBSERVATIONS = frozenset({'fcc_k', 'lp_fcc_k'})
INDETERMINATE_STATUSES = frozenset({
    'WORKER_ERROR', 'SOLVER_UNAVAILABLE', 'TIMEOUT_PREPARATION',
    'TIMEOUT_SOLVER', 'TIMEOUT_VALIDATION', 'TIME_LIMIT',
})
SOURCE_FILES = (
    'baseline.py', 'ms_utils.py', 'experiments/cuts/harness.py',
    'experiments/cuts/cuts.py', 'experiments/cuts/independent_validator.py',
    'experiments/alternative-formulations/fcc.py',
    'experiments/alternative-formulations/fcc_k.py',
    'instances/manifest.csv',
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def relative_inside(root: Path, path: Path) -> str:
    """Não permite referências fora do repo nem symlinks para fora dele."""
    root = root.resolve(strict=True)
    path = path.resolve(strict=True)
    try:
        return path.relative_to(root).as_posix()
    except ValueError as exc:
        raise ValueError(f'INTEGRITY_ERROR: arquivo fora do repositório: {path}') from exc


def source_inventory(root: Path) -> dict[str, str]:
    """Inventário de TODOS os scripts locais fc (inclusive plot/verificador/testes)."""
    local = root / 'experiments' / 'formulation-comparison'
    names = set(SOURCE_FILES)
    names.update(p.relative_to(root).as_posix() for p in local.glob('*.py'))
    missing = sorted(name for name in names if not (root / name).is_file())
    if missing:
        raise ValueError(f'INTEGRITY_ERROR: scripts/modelos ausentes: {missing}')
    return {name: sha256_file(root / name) for name in sorted(names)}


def input_inventory(root: Path, instances) -> dict[str, str]:
    """Reconfere bytes no fim da rodada; rejeita mutação depois do load."""
    digests = {}
    for instance in instances:
        path = root / instance.caminho
        name = relative_inside(root, path)
        actual = sha256_file(path)
        if actual != instance.instance_sha256:
            raise ValueError(f'INTEGRITY_ERROR: instância mudou durante a execução: {name}')
        digests[name] = actual
    return dict(sorted(digests.items()))


def generated_inventory(root: Path, files) -> dict[str, str]:
    hashes = {}
    for filename in files:
        path = root / filename if not Path(filename).is_absolute() else Path(filename)
        relative = relative_inside(root, path)
        if path.name in ('manifest.json', 'manifest.sha256'):
            raise ValueError('INTEGRITY_ERROR: manifestos autorreferentes não são permitidos')
        hashes[relative] = sha256_file(path)
    return dict(sorted(hashes.items()))


def measured_scalability(rows, *, expected_instances=()):
    """Contagem POR INSTÂNCIA, não por braço LP/MIP; sem inferir não medidos.

    F-CC+K aparece como `lp_fcc_k` na modalidade A do schema FC03 e
    `fcc_k` na modalidade B (ou A/B nos CSVs históricos). CAP_EXCEEDED
    exige todas as observações disponíveis com essa classificação.
    Evidências conflitantes
    produzem estado MIXED, em vez de contar duas vezes ou extrapolar.
    """
    groups = defaultdict(list)
    for row in rows:
        if row.get('formulation') in FCC_OBSERVATIONS:
            name = (row.get('instance_name') or '').strip()
            if not name:
                raise ValueError('CSV de escalabilidade possui instância sem nome')
            groups[name].append((row.get('status') or '').strip())
    expected = set(expected_instances)
    if not expected:
        expected = set(groups)
    if not set(groups) <= expected:
        raise ValueError('CSV contém instâncias não declaradas no lote')
    states = {}
    for name in sorted(expected):
        statuses = groups.get(name, [])
        if not statuses:
            states[name] = 'NOT_TESTED'
        elif all(s in PRIMARY_CAP_STATUSES for s in statuses):
            states[name] = 'CAP_EXCEEDED'
        elif all(s == 'OPTIMAL' for s in statuses):
            states[name] = 'OPTIMAL_NUMERIC'
        elif all(s in INDETERMINATE_STATUSES for s in statuses):
            states[name] = 'INCONCLUSIVE'
        else:
            states[name] = 'MIXED_OR_INCONCLUSIVE'
    counts = Counter(states.values())
    return {
        'schema': SCHEMA,
        'scope': 'selected_scalability_instances_only',
        'counting_unit': 'unique_instance_name_with_fcc_lp_or_mip_rows',
        'selected_total': len(expected),
        'tested_total': sum(s != 'NOT_TESTED' for s in states.values()),
        'not_tested_total': counts['NOT_TESTED'],
        'cap_exceeded_total': counts['CAP_EXCEEDED'],
        'optimal_numeric_total': counts['OPTIMAL_NUMERIC'],
        'inconclusive_total': counts['INCONCLUSIVE'] + counts['MIXED_OR_INCONCLUSIVE'],
        'instance_states': states,
        'not_evidence_about_unselected_instances': True,
    }


def scalability_from_csv(path: Path, *, expected_instances=()):
    with path.open(newline='', encoding='utf-8') as stream:
        return measured_scalability(csv.DictReader(stream), expected_instances=expected_instances)


def dump_json_bytes(data) -> bytes:
    return (json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False,
                       default=str) + '\n').encode('utf-8')
