"""FC-06: publicação separada do estudo LP e MIP; nunca imputa censura."""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

from fc06_campaign import ARMS, grouped_counts

CAMPAIGN_EXTRA_FIELDS = ('instance', 'seed', 'origin_graph', 'plan_order', 'wall_budget_s')


def write_results(path, rows, base_fields):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(CAMPAIGN_EXTRA_FIELDS) + list(base_fields)
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)


def summary(rows, prereg):
    """Denominadores pré-registrados, inclusive ausentes/erro/cap/timeout."""
    plan = prereg['plan']
    grouped = grouped_counts(rows, plan)
    total = len(plan)
    successful = sum(v['completed_numeric_optimal'] for v in grouped.values())
    pairs = defaultdict(dict)
    lp = defaultdict(dict)
    for row in rows:
        key = (row.get('instance'), str(row.get('seed')))
        if row.get('modality') == 'B':
            pairs[key][row.get('formulation')] = row
        elif row.get('modality') == 'A':
            lp[row.get('instance')][row.get('formulation')] = row
    comparisons = []
    for entry in prereg['selected']:
        name = entry['instance']
        for seed in prereg['seeds']:
            arms = pairs.get((name, str(seed)), {})
            comparable = (len(arms) == len(ARMS) and
                          all(arms.get(a, {}).get('pair_status') == 'PAIR_VALID' for a in ARMS))
            both_optimal = comparable and all(arms[a].get('status') == 'OPTIMAL' for a in ARMS)
            comparisons.append({
                'instance': name, 'seed': seed, 'origin_graph': entry['origin_graph'],
                'pair_status': 'PAIR_VALID' if comparable else 'PAIR_CENSORED_OR_INVALID',
                'both_solver_optimal': bool(both_optimal),
                'comp_wall_s': _safe_num(arms.get('comp_mip', {}).get('wall_total_s')),
                'fcc_wall_s': _safe_num(arms.get('fcc_k', {}).get('wall_total_s')),
                'comparison_of_runtime_allowed': bool(both_optimal),
                'rational_verification': 'NOT_CERTIFIED',
            })
    lp_comparisons = []
    for entry in prereg['selected']:
        name = entry['instance']
        r = lp.get(name, {})
        controls = (r.get('lp_comp', {}), r.get('lp_fcc_k', {}))
        measured = (all(row.get('status') == 'OPTIMAL' and
                        row.get('solver_evidence') == 'SOLVER_NUMERIC_OPTIMAL' for row in controls))
        lp_comparisons.append({
            'instance': name, 'origin_graph': entry['origin_graph'],
            'solver_numeric_comp_lp': _safe_num(controls[0].get('solver_numeric_lp_objective'))
            if measured else None,
            'solver_numeric_fcc_lp': _safe_num(controls[1].get('solver_numeric_lp_objective'))
            if measured else None,
            'comparison_available': measured,
            'rational_verification': 'NOT_CERTIFIED',
        })
    return {
        'schema': 'FC06-report-v1',
        'planned_arms_total': total, 'recorded_arms_total': len(rows),
        'numeric_optimal_arms_total': successful,
        'censored_or_missing_arms_total': total - successful,
        'planned_mip_pairs_total': len(comparisons),
        'comparable_mip_pairs_total': sum(c['pair_status'] == 'PAIR_VALID' for c in comparisons),
        'both_numeric_optimal_pairs_total': sum(c['both_solver_optimal'] for c in comparisons),
        'origin_graph_groups': grouped,
        'mip_pair_outcomes': comparisons, 'lp_strength_observations': lp_comparisons,
        'any_rational_certification_claimed': False,
        'universal_superiority_claimed': False,
        'interpretation': ('Exploratory conditional sample; censored/missing cases retained in '
                           'denominators; solver results are NUMERIC ONLY; '
                           'seeds/repetitions from the same graph are correlated.'),
    }


def _safe_num(value):
    try:
        import math
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return number if math.isfinite(number) else None


def write_report(out_dir, data):
    out_dir = Path(out_dir)
    (out_dir / 'campaign_report.json').write_text(
        json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    lines = [
        '# FC-06 — Relatório descritivo da campanha condicionada', '',
        f'- Braços planejados: **{data["planned_arms_total"]}**',
        f'- Braços registrados: **{data["recorded_arms_total"]}**',
        f'- Braços censurados/não ótimos/não registrados: **{data["censored_or_missing_arms_total"]}**',
        f'- Pares MIP planejados: **{data["planned_mip_pairs_total"]}**',
        f'- Pares MIP comparáveis: **{data["comparable_mip_pairs_total"]}**',
        f'- Pares MIP numericamente ótimos em ambos os braços: **{data["both_numeric_optimal_pairs_total"]}**',
        '', '## Grupos de grafo de origem', '',
        '| Origem | Braços previstos | Censurados/não ótimos | Pares válidos |',
        '|---|---:|---:|---:|',
    ]
    for origin, group in data['origin_graph_groups'].items():
        lines.append(f'| {origin.replace("|", "/")} | {group["planned_arms"]} | '
                     f'{group["censored_arms"]} | {group["pair_valid_repetitions"]} |')
    lines.extend([
        '', '## Interpretação e limites', '',
        '- LP e MIP são relatados separadamente; não comparar LP como tempo inteiro.',
        '- Teto global de 3600 segundos por braço MIP; LP usa teto distinto de 600 segundos.',
        '- CAP_EXCEEDED, TIME_LIMIT, TIMEOUT e falhas permanecem no denominador.',
        '- Comparações de tempo apenas quando ambos os MIPs terminaram com ótimo numérico.',
        '- Os valores do Gurobi não são provas racionais independentes.',
        '- Instâncias da mesma origem e seeds repetidas não são observações independentes.',
        '- Nenhuma superioridade universal pode ser inferida desta amostra condicional.',
        '- O status `N2 FAIL` permanece inalterado.', '',
    ])
    (out_dir / 'campaign_report.md').write_text('\n'.join(lines), encoding='utf-8')
