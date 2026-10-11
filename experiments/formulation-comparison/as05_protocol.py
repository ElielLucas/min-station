"""AS-05: adendo prospectivo ao AS-00; NÃO altera o pré-registro congelado.

O protocolo deve ser materializado e inspecionado antes de qualquer solve LP.
Alterá-lo após uma campanha exige novo run e explicitação de desvio.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

from as04_schema import digest

SCHEMA = 'AS05-PILOT-PLAN-v1'
MAIN = ('U', 'U_K', 'A2_K')


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_plan(as00: dict, *, as00_sha256: str, manifest_sha256: str) -> dict:
    cases = {x['name']: x for x in as00['cases']}
    pilot = list(as00['pilot_cases'])
    if len(pilot) != 6 or len(pilot) != len(set(pilot)):
        raise ValueError('AS05: piloto deve conter seis instâncias distintas')
    if any(n not in cases or cases[n]['split'] != 'desenvolvimento' or not cases[n]['pilot'] for n in pilot):
        raise ValueError('AS05: somente seis casos de desenvolvimento AS00')
    budget = as00['budget']
    if budget['lp_wall_seconds_per_arm'] != 90 or budget['threads'] != 4:
        raise ValueError('AS05: mudança de orçamento/threads exige adendo novo')
    # Limiar específico AS05 prospectivo, explicitamente NÃO presente em AS00.
    return {
        'schema': SCHEMA,
        'basis_protocol_sha256': as00_sha256,
        'basis_manifest_sha256': manifest_sha256,
        'basis_version': as00['protocol_version'],
        'main_arms': list(MAIN),
        'pilot_cases': [
            {'name': n, 'manifest_name': cases[n]['manifest_name'], 'source_file': cases[n]['source_file'],
             'source_sha256': cases[n]['source_sha256'],
             'raw_graph_id': cases[n]['raw_graph_id'],
             'family_id': cases[n]['family_id'],
             'graph_source': cases[n]['raw_graph_id'].split(':')[0],
             'split': cases[n]['split']}
            for n in pilot],
        'policy': {'backend': 'gurobi', 'mode': 'LP', 'seed': as00['seeds']['baseline'][0],
                   'threads': budget['threads'], 'wall_budget_s_per_arm': budget['lp_wall_seconds_per_arm'],
                   'memory_limit_bytes': budget['memory_gib_per_arm']*1024**3,
                   'reproducibility_seeds': as00['seeds']['reproducibility'],
                   'warm_start': 'none', 'grouping_seed': as00['seeds']['baseline'][0]},
        'materiality_addendum': {
            'relative_gain_min': 0.01,
            'absolute_tolerance': 1e-6,
            'relative_tolerance': 1e-6,
            'max_wall_ratio_a2_over_uk': 3.0,
            'minimum_distinct_raw_graphs': as00['promotion']['minimum_independent_raw_graphs_with_reproducible_gain'],
            'minimum_distinct_graph_sources': 2,
            'zero_denominator_scale': 1.0,
            'scope': 'development_only',
            'not_in_as00': True,
            'interpretation': 'proposta prospectiva AS05; não inferir limiares do parecer Astra',
        },
        'a4': {'policy': 'OFF', 'preselected_case_hypotheses': {},
               'note': 'A4 omitida por padrão; qualquer ativação exige plano novo anterior aos solves'},
        'auxiliary_controls': {'core_ip': 'NOT_IMPLEMENTED_IN_AS04',
                               'fcc_complete_small': 'SEPARATE_SMALL_CONTROL_ONLY'},
        'freeze': {'as00_immutable': True, 'no_evaluation_cases': True,
                   'no_posthoc_partition_selection': True},
    }


def validate_plan(plan: dict, as00: dict, root: Path) -> None:
    expected = make_plan(as00, as00_sha256=sha256_file(root / 'results/benchmark/protocol.json'),
                         manifest_sha256=sha256_file(root / 'instances/manifest.csv'))
    # Parâmetros de materialidade podem ser fixados diferentemente em um adendo NOVO,
    # mas devem ser números finitos positivos com semântica preservada.
    keys_to_ignore = ('materiality_addendum', 'a4')
    for key in expected:
        if key not in keys_to_ignore and plan.get(key) != expected[key]:
            raise ValueError(f'AS05: alteração não permitida no plano: {key}')
    rule = plan.get('materiality_addendum')
    if not isinstance(rule, dict) or set(rule) != set(expected['materiality_addendum']):
        raise ValueError('AS05: contrato dos limiares incompleto')
    for key in ('relative_gain_min', 'absolute_tolerance', 'relative_tolerance',
                'max_wall_ratio_a2_over_uk', 'zero_denominator_scale'):
        val = rule.get(key)
        if type(val) not in (float, int) or not math.isfinite(val) or val <= 0:
            raise ValueError(f'AS05: limiar inválido: {key}')
    if rule['relative_gain_min'] > 1 or rule['max_wall_ratio_a2_over_uk'] < 1:
        raise ValueError('AS05: limiares incoerentes')
    if type(rule.get('minimum_distinct_raw_graphs')) is not int or rule['minimum_distinct_raw_graphs'] < 2:
        raise ValueError('AS05: exigência de independência insuficiente')
    if type(rule.get('minimum_distinct_graph_sources')) is not int or rule['minimum_distinct_graph_sources'] < 2:
        raise ValueError('AS05: fontes de grafos independentes insuficientes')
    for name in ('scope','not_in_as00','interpretation'):
        if rule.get(name) != expected['materiality_addendum'][name]:
            raise ValueError(f'AS05: contexto do adendo alterado: {name}')
    a4 = plan.get('a4')
    if not isinstance(a4, dict) or set(a4) != set(expected['a4']):
        raise ValueError('AS05: configuração A4 incompleta')
    if a4['policy'] not in ('OFF','ON_MATERIAL_A2_GAIN','PRESELECTED_HYPOTHESIS'):
        raise ValueError('AS05: política A4 inválida')
    hypotheses = a4['preselected_case_hypotheses']
    if not isinstance(hypotheses, dict) or not set(hypotheses) <= set(plan['pilot_cases'][i]['name'] for i in range(6)):
        raise ValueError('AS05: hipótese A4 fora do desenvolvimento')
    if any(not isinstance(s, str) or len(s.strip()) < 15 for s in hypotheses.values()):
        raise ValueError('AS05: hipótese A4 sem justificativa concreta')
    if a4['policy'] == 'OFF' and hypotheses:
        raise ValueError('AS05: hipóteses A4 contradizem política OFF')
    if a4['policy'] == 'PRESELECTED_HYPOTHESIS' and not hypotheses:
        raise ValueError('AS05: A4 pré-selecionada exige hipótese por caso')
    if a4['note'] != expected['a4']['note']:
        raise ValueError('AS05: descrição A4 alterada')


def plan_digest(plan: dict) -> str:
    return digest(plan)


def read_plan(path: Path, root: Path) -> tuple[dict, dict]:
    plan = json.loads(path.read_text(encoding='utf-8'))
    as00 = json.loads((root/'results/benchmark/protocol.json').read_text(encoding='utf-8'))
    validate_plan(plan, as00, root)
    return plan, as00
