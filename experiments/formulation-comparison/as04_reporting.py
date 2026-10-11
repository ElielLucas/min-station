"""AS-04: relatórios append-only com censura e classes de evidência separadas.

Não sobreescreve um diretório existente. Os CSVs guardam um registro por braço,
mesmo quando o modelo não foi construído, o solver falhou ou não há objetivo.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from as04_schema import SCHEMA
from fc_integrity import dump_json_bytes


RESULT_COLUMNS = (
    'case_name', 'arm_id', 'mode', 'status', 'reason', 'instance_sha256',
    'structural_sha256', 'reference_k_sha256', 'applied_k_sha256', 'k_policy',
    'k_validated', 'solver_policy_sha256', 'model_complete', 'partition_sha256',
    'wall_total_s', 'solver_version', 'input_load_s', 'reachability_s', 'wall_input_reachability_s', 'wall_k_preparation_s',
    'wall_model_build_s', 'wall_solve_s', 'wall_validation_s',
    'wall_supervisor_shutdown_s', 'solver_runtime_s', 'presolve_wall_s',
    'solver_work', 'nodes', 'peak_rss_kb', 'n_variables', 'n_constraints',
    'n_nonzeros', 'lp_opt_value', 'lp_dual_bound', 'mip_numeric_bound',
    'mip_numeric_incumbent', 'physical_validated_ub', 'physical_ub_status',
    'rational_verified_lb_exact', 'rational_verifier_id',
    'rational_certification', 'evidence_class', 'comparison_role',
)


def flatten_arm(arm: dict):
    if arm.get('schema') != SCHEMA:
        raise ValueError('Schema incompatível')
    phases = arm['wall_phases_s']
    row = {k: arm.get(k) for k in RESULT_COLUMNS}
    for field, phase in (
        ('wall_input_reachability_s', 'preparation'),
        ('wall_k_preparation_s', 'k_preparation'),
        ('wall_model_build_s', 'model_build'),
        ('wall_solve_s', 'solve'), ('wall_validation_s', 'validation'),
        ('wall_supervisor_shutdown_s', 'supervisor_shutdown'),
    ):
        row[field] = phases.get(phase)  # None quando não observado; nunca zero imputado
    return row


def publish_run(data: dict, directory: Path, *, expected_arms: tuple[str, ...]) -> Path:
    """Escreve JSON/CSV/manifests; falha se o caminho já existir.

    O chamador precisa fornecer o universo planejado. Nenhuma linha desaparece.
    """
    if data.get('schema') != SCHEMA:
        raise ValueError('Schema de resultados inválido')
    arms = data.get('arms', ())
    names = tuple(a['arm_id'] for a in arms)
    if len(names) != len(set(names)) or set(names) != set(expected_arms):
        raise ValueError('DENOMINATOR_ERROR: faltam ou sobram braços planejados')
    for arm in arms:
        if arm.get('mode') != data.get('mode') or arm.get('case_name') != data.get('case_name'):
            raise ValueError('INTEGRITY_ERROR: resultados misturam instâncias/modalidades')
        if arm.get('solver_policy_sha256') != data.get('policy_sha256'):
            raise ValueError('INTEGRITY_ERROR: política divergente')
    directory.mkdir(parents=True, exist_ok=False)
    payload = dump_json_bytes(data)
    (directory / 'comparison.json').write_bytes(payload)
    with (directory / 'arms.csv').open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=RESULT_COLUMNS)
        writer.writeheader()
        writer.writerows(flatten_arm(arm) for arm in arms)
    pairs = data['comparison']['pairs']
    with (directory / 'pairs.csv').open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=('effect', 'left', 'right', 'status', 'reason',
                                                    'lp_delta', 'wall_delta_s'))
        writer.writeheader()
        writer.writerows(pairs)
    generated = {name: hashlib.sha256((directory / name).read_bytes()).hexdigest()
                 for name in ('comparison.json', 'arms.csv', 'pairs.csv')}
    (directory / 'manifest.json').write_text(
        json.dumps({'schema': SCHEMA, 'generated_sha256': generated,
                    'expected_arms': list(expected_arms)},
                   ensure_ascii=False, sort_keys=True, indent=2) + '\n', encoding='utf-8')
    return directory


def verify_run(directory: Path):
    manifest = json.loads((directory / 'manifest.json').read_text(encoding='utf-8'))
    for name, expected in manifest['generated_sha256'].items():
        if hashlib.sha256((directory / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f'INTEGRITY_ERROR: artefato alterado: {name}')
    data = json.loads((directory / 'comparison.json').read_text(encoding='utf-8'))
    expected = set(manifest['expected_arms'])
    if {x['arm_id'] for x in data['arms']} != expected or len(data['arms']) != len(expected):
        raise ValueError('DENOMINATOR_ERROR: resultado incompleto')
    return True
