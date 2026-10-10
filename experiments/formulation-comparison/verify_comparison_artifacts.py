#!/usr/bin/env python3
"""FC-04: auditoria somente leitura de artefatos de um run completo.

Uso: python experiments/formulation-comparison/verify_comparison_artifacts.py \
          results/formulation-comparison/pilot-.../

Nenhum acesso ao Gurobi; não reexecuta modelos nem modifica resultados.
O checksum sidecar detecta alterações acidentais no manifesto, mas NÃO substitui
assinatura digital ou cópia imutável fora do repositório.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def _sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for part in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(part)
    return digest.hexdigest()


def _resolved(root, name, problems):
    if not isinstance(name, str) or not name or Path(name).is_absolute():
        problems.append(f'INVALID_PATH: {name!r}')
        return None
    components = Path(name).parts
    if '..' in components or '.' in components:
        problems.append(f'INVALID_PATH: {name!r}')
        return None
    path = root / name
    if path.is_symlink():
        problems.append(f'SYMLINK_FORBIDDEN: {name}')
        return None
    try:
        actual = path.resolve(strict=True)
        actual.relative_to(root.resolve(strict=True))
        if not actual.is_file():
            raise ValueError('não é arquivo')
    except (FileNotFoundError, OSError, ValueError) as exc:
        problems.append(f'MISSING_OR_OUTSIDE: {name}: {exc}')
        return None
    return actual


def _group_check(root, title, data, issues):
    if not isinstance(data, dict) or not data:
        issues.append(f'MISSING_INVENTORY: {title}')
        return
    for name, expected in data.items():
        path = _resolved(root, name, issues)
        if path is None:
            continue
        if not isinstance(expected, str) or len(expected) != 64:
            issues.append(f'INVALID_DIGEST: {title}/{name}')
            continue
        actual = _sha(path)
        if actual != expected:
            issues.append(f'HASH_MISMATCH: {title}/{name} ({expected} != {actual})')


def _scalability_counts(rows, expected):
    # Implementação independente do agregador de publicação.
    statuses = {}
    for name in expected:
        observed = [row['status'] for row in rows
                    if row.get('instance_name') == name and
                    row.get('formulation') in ('fcc_k', 'lp_fcc_k')]
        if not observed:
            statuses[name] = 'NOT_TESTED'
        elif all(x in ('CAP_EXCEEDED', 'NOT_MEASURED_CAP_EXCEEDED') for x in observed):
            statuses[name] = 'CAP_EXCEEDED'
        elif all(x == 'OPTIMAL' for x in observed):
            statuses[name] = 'OPTIMAL_NUMERIC'
        elif all(x in ('TIME_LIMIT', 'WORKER_ERROR', 'SOLVER_UNAVAILABLE',
                       'TIMEOUT_SOLVER', 'TIMEOUT_PREPARATION', 'TIMEOUT_VALIDATION')
                 for x in observed):
            statuses[name] = 'INCONCLUSIVE'
        else:
            statuses[name] = 'MIXED_OR_INCONCLUSIVE'
    return statuses


def verify(run_dir: Path, *, root: Path = ROOT):
    """Retorna (ok, problemas) sem modificar nenhum byte do repositório."""
    run_dir = Path(run_dir).resolve()
    root = Path(root).resolve()
    problems = []
    manifest_path = run_dir / 'manifest.json'
    sidecar_path = run_dir / 'manifest.sha256'
    if not manifest_path.is_file() or not sidecar_path.is_file():
        return False, ['MISSING_MANIFEST_OR_CHECKSUM: formato FC04-v1 necessário']
    try:
        stored = sidecar_path.read_text(encoding='ascii').split()
        if len(stored) != 2 or stored[1] != 'manifest.json' or stored[0] != _sha(manifest_path):
            problems.append('MANIFEST_CHECKSUM_MISMATCH')
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    except (UnicodeError, OSError, json.JSONDecodeError) as exc:
        return False, [f'INVALID_MANIFEST: {exc}']
    if manifest.get('artifact_schema') != 'FC04-v1':
        problems.append('UNSUPPORTED_SCHEMA: requer FC04-v1')
        return False, problems
    for section in ('code_files_sha256', 'input_files_sha256', 'generated_files_sha256'):
        _group_check(root, section, manifest.get(section), problems)
    produced = manifest.get('generated_files_sha256', {})
    try:
        path_prefix = run_dir.resolve(strict=True).relative_to(root.resolve(strict=True)).as_posix()
    except ValueError:
        return False, ['RUN_OUTSIDE_REPOSITORY']
    if isinstance(produced, dict):
        for rel in produced:
            if not rel.startswith(path_prefix + '/'):
                problems.append(f'ARTIFACT_OUTSIDE_RUN: {rel}')
        actual_files = {
            p.relative_to(root).as_posix() for p in run_dir.rglob('*') if p.is_file()
        }
        excluded = {f'{path_prefix}/manifest.json', f'{path_prefix}/manifest.sha256'}
        unexpected = actual_files - set(produced) - excluded
        if unexpected:
            problems.append(f'UNTRACKED_OUTPUTS: {sorted(unexpected)}')
        expected_paths = set(manifest.get('generated_files', []))
        if expected_paths != set(produced):
            problems.append('GENERATED_FILE_INDEX_MISMATCH')
    inputs = manifest.get('input_files_sha256', {})
    for inst in manifest.get('instances', []):
        if not isinstance(inst, dict) or inputs.get(inst.get('caminho')) != inst.get('instance_sha256'):
            problems.append(f'INSTANCE_DIGEST_MISMATCH: {inst!r}')
    if manifest.get('tier') == 'scalability':
        summary_rel = f'{path_prefix}/scalability_summary.json'
        results_rel = f'{path_prefix}/results.csv'
        if summary_rel not in produced or results_rel not in produced:
            problems.append('MISSING_SCALABILITY_FILES')
        else:
            try:
                summary = json.loads((root / summary_rel).read_text(encoding='utf-8'))
                with (root / results_rel).open(encoding='utf-8', newline='') as stream:
                    rows = list(csv.DictReader(stream))
                names = [i['nome'] for i in manifest['instances']]
                actual_states = _scalability_counts(rows, names)
                if summary.get('instance_states') != actual_states:
                    problems.append('SCALABILITY_SUMMARY_MISMATCH')
                for field, target in {
                    'selected_total': len(names),
                    'tested_total': sum(v != 'NOT_TESTED' for v in actual_states.values()),
                    'not_tested_total': list(actual_states.values()).count('NOT_TESTED'),
                    'cap_exceeded_total': list(actual_states.values()).count('CAP_EXCEEDED'),
                }.items():
                    if summary.get(field) != target:
                        problems.append(f'SCALABILITY_COUNT_MISMATCH: {field}')
                extra = {r['instance_name'] for r in rows
                         if r.get('formulation') in ('fcc_k', 'lp_fcc_k')} - set(names)
                if extra:
                    problems.append(f'UNEXPECTED_SCALABILITY_INSTANCE: {sorted(extra)}')
            except (KeyError, ValueError, OSError, json.JSONDecodeError) as exc:
                problems.append(f'INVALID_SCALABILITY_REPORT: {exc}')
    return not problems, problems


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run_dir', type=Path)
    args = parser.parse_args(argv)
    ok, issues = verify(args.run_dir)
    print(json.dumps({'status': 'PASS' if ok else 'INTEGRITY_FAIL',
                      'problems': issues}, indent=2, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
