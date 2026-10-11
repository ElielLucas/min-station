"""FC-06: contratos puros de pré-registro, elegibilidade e plano pareado.

NÃO contém solver; NÃO infere prova racional de resultados Gurobi.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

SCHEMA = 'FC06-prereg-v1'
ARMS = ('comp_mip', 'fcc_k')
LP_ARMS = ('lp_base', 'lp_comp', 'lp_fcc_k')
SEEDS = (42, 43, 44)
BUDGET_MIP_S = 3600.0
BUDGET_LP_S = 600.0
MAIN_NAMES = frozenset((
    'hb-q4-ndir2-p1-k1-L2.txt', 'bp-nao-q2-B2-s0.txt',
    'hb-q5-ndir2-p1-k1-L2.txt', 'hb-q6-ndir1-p6-k1-L2.txt',
    'bp-sim-q2-B2-s0.txt', 'bp-nao-q2-B3-s0.txt',
))
MIP_METRICS = (
    'wall_total_s', 'solver_runtime_s', 'work', 'status', 'stop_reason',
    'solver_numeric_mip_lb', 'solver_numeric_mip_incumbent',
    'physical_feasible_ub', 'n_vars', 'n_cons', 'nodes',
    'model_complete', 'k_sha256', 'pair_status',
)
LP_METRICS = ('wall_total_s', 'solver_runtime_s', 'work',
              'solver_numeric_lp_objective', 'status', 'model_complete')


def canonical_bytes(obj):
    return (json.dumps(obj, sort_keys=True, ensure_ascii=False,
                       separators=(',', ':'), allow_nan=False) + '\n').encode('utf-8')


def digest(obj):
    return hashlib.sha256(canonical_bytes(obj)).hexdigest()


def valid_digest(value):
    return isinstance(value, str) and len(value) == 64 and all(c in '0123456789abcdef' for c in value)


def csv_rows(path: Path):
    with Path(path).open(encoding='utf-8', newline='') as stream:
        return list(csv.DictReader(stream))


def _number(value):
    try:
        n = float(value)
    except (ValueError, TypeError, OverflowError):
        return None
    return n if math.isfinite(n) else None


def origin_from_manifest(row):
    """Agregação por origem *declarada*, não assume independência de seeds."""
    original = (row.get('instancia_original') or '').strip()
    source = (row.get('fonte') or '').strip()
    if original:
        return f'{source}:{original}'
    path = (row.get('caminho') or '').split('/')
    # Instâncias estruturais compartilham família/gerador; fallback conservador.
    if 'estrutural' in path:
        index = path.index('estrutural')
        return f'estrutural:{path[index+1]}' if len(path) > index + 1 else 'estrutural'
    return f'{source or "origem_nao_identificada"}:{row.get("nome", "sem_nome")}'


def pair_screening(rows, name, instance_digest, *,
                   justification='', minimum_wall_s=30.0):
    """Elegível apenas com par auditado/completo, não trivial OU justificado.

    Uma ausência de dados é censura, nunca equivalência ou objetivo zero.
    """
    found = [r for r in rows if r.get('instance_name') == name and
             r.get('modality') == 'B' and r.get('formulation') in ARMS]
    if len(found) != 2 or {r['formulation'] for r in found} != set(ARMS):
        return False, 'SCREENING_PAIR_MISSING_OR_DUPLICATED', None
    by_arm = {r['formulation']: r for r in found}
    k = {r.get('k_sha256') for r in found}
    if (len(k) != 1 or not valid_digest(next(iter(k))) or
            any(r.get('instance_sha256') != instance_digest for r in found) or
            any(r.get('pair_status') != 'PAIR_VALID' or
                r.get('model_complete', '').lower() != 'true' or
                r.get('k_validated', '').lower() != 'true' or
                _number(r.get('n_K')) is None or
                _number(r.get('n_K')) != _number(r.get('n_K_added'))
                for r in found)):
        return False, 'SCREENING_INTEGRITY_OR_INCOMPLETE_K', None
    statuses = [r.get('status') for r in found]
    if not all(s in ('OPTIMAL', 'TIME_LIMIT') for s in statuses):
        return False, 'SCREENING_CENSORED_OR_INCOMPLETE', None
    if 'TIME_LIMIT' in statuses:
        mode = 'UNRESOLVED_COMPLETE_MODEL'
    elif justification and len(justification.strip()) >= 80:
        if max(_number(r.get('wall_total_s')) or 0.0 for r in found) < minimum_wall_s:
            return False, 'SCREENING_TOO_TRIVIAL_EVEN_WITH_JUSTIFICATION', None
        mode = 'EXPLICIT_METHODOLOGICAL_JUSTIFICATION'
    else:
        return False, 'ALL_ARMS_SOLVED_SHORT_SCREENING_NO_LONG_RUN_JUSTIFICATION', None
    return True, mode, {'k_sha256': next(iter(k)),
                        'screening_statuses': {a: by_arm[a]['status'] for a in ARMS},
                        'screening_wall_s': {a: _number(by_arm[a].get('wall_total_s')) for a in ARMS}}


def choose_instances(screening_rows, instances, rows_by_name, *,
                     requested=(), justification=''):
    """Não escolhe sucessos a posteriori: retorna TODAS exclusões explícitas."""
    requested = tuple(requested or (i.nome for i in instances))
    if len(requested) != len(set(requested)) or not set(requested) <= MAIN_NAMES:
        raise ValueError('Somente instâncias únicas do pool MAIN pré-definido são permitidas')
    by_name = {x.nome: x for x in instances}
    selected, excluded = [], []
    for name in requested:
        if name not in by_name or name not in rows_by_name:
            excluded.append({'instance': name, 'reason': 'NOT_IN_MATERIALIZED_MAIN_POOL'})
            continue
        inst = by_name[name]
        ok, reason, evidence = pair_screening(
            screening_rows, name, inst.instance_sha256,
            justification=justification,
        )
        if not ok:
            excluded.append({'instance': name, 'reason': reason})
            continue
        selected.append({
            'instance': name, 'instance_sha256': inst.instance_sha256,
            'instance_content_sha256': inst.instance_content_sha256,
            'input_path': inst.caminho, 'origin_graph': origin_from_manifest(rows_by_name[name]),
            'familia': inst.familia, 'eligibility': reason,
            'methodological_justification': justification if reason.startswith('EXPLICIT') else '',
            **evidence,
        })
    return selected, excluded


def make_plan(selected, *, seeds=SEEDS, include_lp=True):
    if not selected:
        return []
    if len(seeds) != len(set(seeds)) or not seeds or any(
            not isinstance(s, int) or s < 0 for s in seeds):
        raise ValueError('seeds devem ser inteiras, distintas, não negativas')
    plan = []
    for index, entry in enumerate(selected):
        name = entry['instance']
        if include_lp:
            for arm in LP_ARMS:
                plan.append({'instance': name, 'seed': seeds[0], 'modality': 'A',
                             'formulation': arm, 'wall_budget_s': BUDGET_LP_S,
                             'origin_graph': entry['origin_graph'], 'order': len(plan)})
        for seed_index, seed in enumerate(seeds):
            order = ARMS if (index + seed_index) % 2 == 0 else ARMS[::-1]
            for arm in order:
                plan.append({'instance': name, 'seed': seed, 'modality': 'B',
                             'formulation': arm, 'wall_budget_s': BUDGET_MIP_S,
                             'origin_graph': entry['origin_graph'], 'order': len(plan)})
    return plan


def validate_prereg(prereg):
    if prereg.get('schema') != SCHEMA:
        raise ValueError('FC06: schema de pré-registro desconhecido')
    if prereg.get('pilot_gate') != 'READY_FOR_EXTENDED':
        raise ValueError('FC06: gate FC-05 não autorizado')
    if not prereg.get('selected'):
        raise ValueError('FC06: não há instâncias informativas elegíveis; STOP')
    seeds = prereg.get('seeds')
    if seeds != list(SEEDS):
        raise ValueError('FC06: seeds pré-registradas 42,43,44 obrigatórias')
    if prereg.get('mip_wall_cap_s') != BUDGET_MIP_S:
        raise ValueError('FC06: o teto deve ser exatamente 3600s por braço MIP')
    if prereg.get('lp_wall_cap_s') != BUDGET_LP_S:
        raise ValueError('FC06: o teto LP deve ser 600s')
    if not all(valid_digest(e.get('instance_sha256')) and
               valid_digest(e.get('k_sha256')) for e in prereg['selected']):
        raise ValueError('FC06: hash ausente de instância/K')
    plan = prereg.get('plan')
    if plan != make_plan(prereg['selected'], seeds=SEEDS,
                         include_lp=prereg.get('include_lp') is True):
        raise ValueError('FC06: plano/ordem não corresponde à seleção congelada')
    keys = [(p['instance'], p['seed'], p['modality'], p['formulation']) for p in plan]
    if len(keys) != len(set(keys)):
        raise ValueError('FC06: repetição de braço no pré-registro')
    return True


def grouped_counts(rows, plan):
    """Denominador = plano, inclusive RUN_NOT_RECORDED, timeout ou cap."""
    lookup = defaultdict(list)
    for row in rows:
        lookup[(row['instance'], str(row['seed']), row['modality'], row['formulation'])].append(row)
    by_origin = defaultdict(lambda: {'planned_arms': 0, 'completed_numeric_optimal': 0,
                                     'censored_arms': 0, 'pair_valid_repetitions': 0,
                                     'pair_not_valid_repetitions': 0})
    pair_groups = defaultdict(dict)
    for item in plan:
        group = by_origin[item['origin_graph']]
        group['planned_arms'] += 1
        key = (item['instance'], str(item['seed']), item['modality'], item['formulation'])
        matches = lookup.get(key, [])
        row = matches[0] if len(matches) == 1 else {}
        if row.get('status') == 'OPTIMAL' and row.get('solver_evidence') == 'SOLVER_NUMERIC_OPTIMAL':
            group['completed_numeric_optimal'] += 1
        else:
            group['censored_arms'] += 1
        if item['modality'] == 'B':
            pair_groups[(item['origin_graph'], item['instance'], str(item['seed']))][item['formulation']] = row
    for (origin, _, _), pair in pair_groups.items():
        valid = (len(pair) == 2 and all(pair.get(arm, {}).get('pair_status') == 'PAIR_VALID'
                                         for arm in ARMS))
        by_origin[origin]['pair_valid_repetitions' if valid else 'pair_not_valid_repetitions'] += 1
    return dict(sorted(by_origin.items()))
