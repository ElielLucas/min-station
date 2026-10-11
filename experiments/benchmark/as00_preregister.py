"""AS-00: materializa protocolo pré-registrado imutável, antes dos solves."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

# Seleção pré-registrada apenas com informações históricas de família e estrato.
FINAL_EVALUATION = (
    'mapf-den312d-m50-f2-rho', 'mapf-empty-32-32-m25-f4',
    'mapf-random-32-32-10-m50-f8', 'mapf-random-64-64-20-m100-f4',
    'mapf-warehouse-10-20-10-2-1-m25-f4',
    'puc-hc9u-regiao-f4', 'puc-hc10p-seed-r1',
    'puc-hc11p-seed-r1', 'puc-hc12p-seed-r1',
    'pucn-cc7-3n-regiao-f2',
)

ARM_IDS = ('U_NO_K', 'U_PLUS_K', 'A2_PLUS_K', 'A4_PLUS_K',
           'FCC_PLUS_K_SMALL_CONTROL', 'INTEGER_KERNEL_CONTROL',
           'MATCHING_CUTS_CONDITIONAL', 'PATHS_B_CONDITIONAL',
           'CUMULATIVE_C_CONDITIONAL')


def make_protocol(universe: dict) -> dict:
    cases = {c['name']: c for c in universe['cases']}
    if any(name not in cases or cases[name]['split'] != 'avaliacao' for name in FINAL_EVALUATION):
        raise ValueError('FINAL_SELECTION_INVALID: caso fora da avaliação')
    if len({cases[n]['raw_graph_id'] for n in FINAL_EVALUATION}) != len(FINAL_EVALUATION):
        raise ValueError('FINAL_SELECTION_INVALID: grafos brutos repetidos')
    if any(cases[n]['independence'] != 'INDEPENDENT_RAW_SOURCE' for n in FINAL_EVALUATION):
        raise ValueError('FINAL_SELECTION_INVALID: vazamento D/A')
    return {
        **universe,
        'protocol_version': 'AS00-2026-10-11-v1',
        'legacy_freezes': 'READ_ONLY',
        'arm_ids': list(ARM_IDS),
        'mandatory_initial_arms': ['U_NO_K', 'U_PLUS_K', 'A2_PLUS_K'],
        'conditional_arms_require_new_authorization': True,
        'pilot_cases': [c['name'] for c in universe['cases'] if c['pilot']],
        'final_evaluation_cases': list(FINAL_EVALUATION),
        'evaluation_support_cases': sorted(name for name, c in cases.items()
                                          if c['split'] == 'avaliacao' and name not in FINAL_EVALUATION),
        'seeds': {'baseline': [42], 'reproducibility': [42, 43, 44]},
        'budget': {
            'lp_wall_seconds_per_arm': 90, 'mip_pilot_seconds_per_arm': [300, 600],
            'final_wall_seconds_per_arm': 3600, 'threads': 4,
            'memory_gib_per_arm': 16,
            'include_shared_preparation': True,
        },
        'hypotheses': [
            'A2+K melhora o limite LP sobre U+K em famílias independentes.',
            'A2+K melhora LB/gap MIP no mesmo orçamento total sem custo excessivo.',
            'Maior força LP não garante menor tempo MIP.',
        ],
        'promotion': {
            'minimum_independent_raw_graphs_with_reproducible_gain': 2,
            'require_positive_wall_cost_benefit': True,
            'require_no_hidden_severe_losses': True,
            'selection_from_evaluation': '10 frozen raw-independent cases; all 17 retained for coverage',
            'no_automatic_promotion_when_missing': True,
        },
        'missing_outcomes': [
            'NOT_MEASURED_INPUT', 'NOT_MEASURED_CAP', 'NOT_MEASURED_MEMORY',
            'NOT_MEASURED_BUDGET', 'ERROR',
        ],
        'initial_outcome': 'NOT_RUN',
        'claims': {
            'related_evaluation_cases_are_not_independent': True,
            'numeric_lp_not_rational_certificate': True,
            'no_FCC_feasibility_screening': True,
        },
        'execution_authorized': False,  # AS00 não autoriza LP/MIP; gates posteriores decidem
    }


def pre_registration_text(protocol: dict, hexdigest: str) -> str:
    counts = protocol['counts']
    related = [c for c in protocol['cases']
               if c['split'] == 'avaliacao' and c['independence'] != 'INDEPENDENT_RAW_SOURCE']
    return f'''# AS-00 — Pré-registro v1 (sem solves)

**Estado:** CONGELADO para AS-00; execuções futuras dependem dos gates AS-01..AS-06.  
**Protocolo SHA-256:** `{hexdigest}`  
**Manifesto SHA-256:** `{protocol['manifest_sha256']}`

## Universo

- D/A: **{len(protocol['cases'])}**, desenvolvimento **{counts['desenvolvimento']}**, avaliação **{counts['avaliacao']}**.
- Piloto: {', '.join(f'`{x}`' for x in protocol['pilot_cases'])}.
- Se a construção da F-CC exceder o cap ou a memória, o caso permanece no denominador.
- São preservados G, S, T, r, A_r, hash do arquivo e vínculos com a fonte.
- Variantes do mesmo mapa e cenário MAPF são relacionadas, ainda que mudem m/r.

## Hipóteses pré-registradas

''' + '\n'.join(f'- {h}' for h in protocol['hypotheses']) + f'''

## Critérios de promoção

- Ganho reproduzido em pelo menos **2 grafos brutos independentes**.
- Comparações pareadas entre as mesmas instâncias, com orçamento total incluindo preparação.
- Controles: U sem K, U+K, núcleo IP quando aplicável; F-CC apenas controle pequeno.
- A4, cortes, B e C são condicionais e não entram automaticamente no estudo.
- Avaliação final: **10 casos** estratificados e congelados nesta versão, antes dos solves.
- Casos de avaliação relacionados ao desenvolvimento: **{len(related)}**, nunca rotular como validação independente.
- Seleção principal de avaliação: {', '.join(f'`{n}`' for n in protocol['final_evaluation_cases'])}.
- Restante da avaliação: **{len(protocol['evaluation_support_cases'])}** casos preservados no universo e cobertura.
- Falhas/cap/memória/budget/errors ficam registrados, não substituídos por 0.
- LP do solver não é certificado racional; incumbentes devem passar no validador físico.

## Orçamento pré-registrado (por braço)

- LP diagnóstico: {protocol['budget']['lp_wall_seconds_per_arm']} s.
- MIP piloto: {protocol['budget']['mip_pilot_seconds_per_arm']} s.
- Campanha final: {protocol['budget']['final_wall_seconds_per_arm']} s.
- Threads: {protocol['budget']['threads']}; seeds piloto {protocol['seeds']['baseline']}; repetições {protocol['seeds']['reproducibility']}.
- Limite de memória: {protocol['budget']['memory_gib_per_arm']} GiB.
- A execução de qualquer braço exige autorização por gates futuros.
- Alterações: gerar nova versão/diretório e registrar desvio; nunca sobrescrever este snapshot.

## Limites de interpretação

Os estratos D/A e sua dificuldade são históricos, não medidas novas. O protocolo
não declara sucesso de A, não reabre `N2 FAIL` e não altera N1, N2 ou FC.
'''


def write_preregistration(universe: dict, output_dir: Path) -> Path:
    protocol = make_protocol(universe)
    raw = (json.dumps(protocol, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode('utf-8')
    hexdigest = hashlib.sha256(raw).hexdigest()
    # mkdir exclusive: do not overwrite an existing preregistration, even if identical.
    output_dir.mkdir(parents=True, exist_ok=False)
    (output_dir / 'protocol.json').write_bytes(raw)
    (output_dir / 'protocol.sha256').write_text(hexdigest + '  protocol.json\n', encoding='ascii')
    (output_dir / 'pre_register.md').write_text(pre_registration_text(protocol, hexdigest), encoding='utf-8')
    return output_dir
