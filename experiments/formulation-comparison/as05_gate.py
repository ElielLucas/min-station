"""AS-05: métricas LP/decisão determinística sem usar casos de avaliação."""
from __future__ import annotations

import math
from collections import Counter

MAIN = ('U', 'U_K', 'A2_K')


def _valid_optimum(row: dict) -> float | None:
    if row.get('status') != 'OPTIMAL_NUMERIC' or row.get('model_complete') is not True:
        return None
    value = row.get('lp_opt_value')
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        return None
    return float(value)


def _positive_wall(row: dict) -> float | None:
    wall = row.get('wall_total_s')
    return float(wall) if isinstance(wall, (int, float)) and not isinstance(wall, bool) and math.isfinite(wall) and wall > 0 else None


def metrics_for_case(case: dict, result: dict, rule: dict) -> dict:
    if result.get('case_name') != case.get('manifest_name', case['name']) or result.get('mode') != 'LP':
        raise ValueError('AS05: caso ou modalidade divergente')
    rows = result.get('arms')
    if not isinstance(rows, list) or len(rows) != len({x.get('arm_id') for x in rows}) or {x.get('arm_id') for x in rows} != set(MAIN):
        raise ValueError('AS05: denominador obrigatório 3 braços')
    arms = {a['arm_id']: a for a in rows}
    if any(a.get('case_name') != case.get('manifest_name', case['name']) or a.get('mode') != 'LP' for a in rows):
        raise ValueError('AS05: dados de outro caso misturados')
    pair_rows = result.get('comparison', {}).get('pairs', [])
    pairs = {p['effect']: p for p in pair_rows}
    if not all(effect in pairs for effect in ('K_EFFECT', 'A_EFFECT')):
        raise ValueError('AS05: contrastes AS04 ausentes')
    deltas = {}
    for effect, left, right in [('K_EFFECT','U','U_K'), ('A_EFFECT','U_K','A2_K')]:
        p = pairs[effect]
        a, b = arms[left], arms[right]
        if p['left'] != left or p['right'] != right:
            raise ValueError('AS05: pares AS04 trocados')
        za, zb = _valid_optimum(a), _valid_optimum(b)
        complete = p['status'] == 'MATCHED_COMPLETE' and za is not None and zb is not None
        if complete:
            # Nunca confiar apenas no delta informado pelo relatório.
            if p.get('lp_delta') is None or abs(float(p['lp_delta'])-(zb-za)) > rule['absolute_tolerance']:
                raise ValueError('AS05: delta adulterado')
            diff = zb-za
            rel = diff/max(abs(za), rule['zero_denominator_scale'])
            denom_a, denom_b = _positive_wall(a), _positive_wall(b)
            ratio = (denom_b/denom_a if denom_a is not None and denom_b is not None else None)
            deltas[effect] = {'status':'MATCHED_COMPLETE','absolute':diff,'relative':rel,
                              'wall_ratio':ratio}
        else:
            if p['status'] == 'MATCHED_COMPLETE':
                raise ValueError('AS05: par completo sem ótimo LP')
            deltas[effect] = {'status':p['status'],'absolute':None,'relative':None,'wall_ratio':None}
    a = deltas['A_EFFECT']
    tol = rule['absolute_tolerance'] + rule['relative_tolerance']*max(
        abs(_valid_optimum(arms['U_K']) or 0), abs(_valid_optimum(arms['A2_K']) or 0))
    numerical_violation = (a['absolute'] is not None and a['absolute'] < -tol)
    material = a['relative'] is not None and a['absolute'] > tol and a['relative'] >= rule['relative_gain_min']
    wall_good = a['wall_ratio'] is not None and a['wall_ratio'] <= rule['max_wall_ratio_a2_over_uk']
    return {'name':case['name'],'raw_graph_id':case['raw_graph_id'],
            'graph_source':case['graph_source'], 'family_id':case['family_id'],
            'contrasts':deltas,'numerical_nondominance_violation':numerical_violation,
            'material_a_gain':bool(material), 'wall_acceptable':bool(wall_good),
            'a4_triggered':False,'a4_not_selected_reason':None,
            'arm_statuses':{k:arms[k]['status'] for k in MAIN},
            'reproduction':{'status':'PENDING' if material and wall_good else 'NOT_SELECTED',
                            'reason':'Aguardando seeds independentes 43/44' if material and wall_good else 'Sem ganho material/custo aceitável'}}


def assess_reproduction(case: dict, main_result: dict, repeated: list[dict],
                        rule: dict, seeds: list[int]) -> dict:
    """Confere ganhos em todas as seeds pré-registradas, sem duplicar grafos.

    Seed não muda identidade estrutural, K, particionamento ou fonte; muda
    unicamente a política solver e a seed da política de agrupamento AS03.
    Isso pode mudar a partição: essa variação deve ser explicitamente reportada.
    """
    expected = set(seeds[1:])
    if len(seeds) != len(set(seeds)) or len(repeated) != len(expected):
        return {'status':'PENDING','reason':'Rodadas de reprodução ausentes ou duplicadas',
                'verified_seeds':[]}
    base = {x['arm_id']:x for x in main_result['arms']}
    checked = []
    for report in repeated:
        if report.get('case_name') != case.get('manifest_name',case['name']) or report.get('mode') != 'LP':
            raise ValueError('AS05: reprodução de outro caso ou modalidade')
        arms = report.get('arms',[])
        if len(arms) != 2 or {x.get('arm_id') for x in arms} != {'U_K','A2_K'}:
            raise ValueError('AS05: reprodução deve conter U_K e A2_K')
        k,a = sorted(arms,key=lambda x:0 if x['arm_id']=='U_K' else 1)
        seed = k.get('solver_policy',{}).get('seed')
        if type(seed) is not int or seed not in expected or seed in checked or seed != a.get('solver_policy',{}).get('seed'):
            raise ValueError('AS05: seed repetida/fora do pré-registro')
        checked.append(seed)
        for row in (k,a):
            previous = base[row['arm_id']]
            for identity in ('instance_sha256','structural_sha256','reference_k_sha256','applied_k_sha256'):
                if not row.get(identity) or row.get(identity) != previous.get(identity):
                    raise ValueError(f'AS05: identidade alterada na reprodução: {identity}')
            if row['arm_id'] == 'A2_K' and row.get('partition_sha256') != previous.get('partition_sha256'):
                raise ValueError('AS05: partição A2 alterada ao variar seed do solver')
            prior_policy = previous['solver_policy']
            cur_policy = row['solver_policy']
            if {x:y for x,y in cur_policy.items() if x!='seed'} != {x:y for x,y in prior_policy.items() if x!='seed'}:
                raise ValueError('AS05: parâmetros do solver divergentes na reprodução')
        # Somente +K emparelhados; AS04 informa K_EFFECT ausente normalmente.
        pair = next((x for x in report.get('comparison',{}).get('pairs',[]) if x.get('effect')=='A_EFFECT'),None)
        if pair is None or pair.get('left')!='U_K' or pair.get('right')!='A2_K':
            raise ValueError('AS05: par de reprodução inexistente')
        zk,za = _valid_optimum(k),_valid_optimum(a)
        if pair['status'] != 'MATCHED_COMPLETE' or zk is None or za is None:
            return {'status':'PENDING','reason':f'Seed {seed} sem LPs comparáveis',
                    'verified_seeds':sorted(checked)}
        delta = za-zk
        if pair.get('lp_delta') is None or abs(float(pair['lp_delta'])-delta)>rule['absolute_tolerance']:
            raise ValueError('AS05: delta adulterado na reprodução')
        tol = rule['absolute_tolerance']+rule['relative_tolerance']*max(abs(zk),abs(za))
        wallk,walla = _positive_wall(k),_positive_wall(a)
        if (delta <= tol or delta/max(abs(zk),rule['zero_denominator_scale']) < rule['relative_gain_min']
                or wallk is None or walla is None or walla/wallk>rule['max_wall_ratio_a2_over_uk']):
            return {'status':'FAIL','reason':f'Seed {seed} não reproduziu ganho/custo',
                    'verified_seeds':sorted(checked)}
    if set(checked)!=expected:
        return {'status':'PENDING','reason':'Seeds de reprodução incompletas',
                'verified_seeds':sorted(checked)}
    return {'status':'PASS','reason':'Ganho material e custo reproduzidos em todas as seeds',
            'verified_seeds':sorted(checked)}


def a4_selection(case: dict, metric: dict, plan: dict) -> tuple[bool,str]:
    rule = plan['a4']
    if rule['policy'] == 'OFF':
        return False, 'NOT_SELECTED_REASON:A4_DISABLED_IN_FROZEN_PLAN'
    if rule['policy'] == 'PRESELECTED_HYPOTHESIS':
        return (True,'PRESELECTED_HYPOTHESIS') if case['name'] in rule['preselected_case_hypotheses'] else (False,'NOT_SELECTED_REASON:NO_PRESELECTED_HYPOTHESIS')
    if rule['policy'] == 'ON_MATERIAL_A2_GAIN':
        return (True,'MATERIAL_A2_GAIN') if metric['material_a_gain'] else (False,'NOT_SELECTED_REASON:A2_GAIN_NOT_MATERIAL_OR_CENSORED')
    raise ValueError('AS05: política A4 inesperada')


def assess_gate(metrics: list[dict], plan: dict) -> dict:
    expected = {x['name'] for x in plan['pilot_cases']}
    if len(metrics) != len(expected) or {m['name'] for m in metrics} != expected:
        raise ValueError('AS05: decisões devem preservar seis casos')
    if any(m['raw_graph_id'] != next(x['raw_graph_id'] for x in plan['pilot_cases'] if x['name']==m['name']) or
           m['graph_source'] != next(x['graph_source'] for x in plan['pilot_cases'] if x['name']==m['name']) for m in metrics):
        raise ValueError('AS05: identidade da família adulterada')
    rule = plan['materiality_addendum']
    censored = [m['name'] for m in metrics if any(m['contrasts'][x]['status'] != 'MATCHED_COMPLETE' for x in ('K_EFFECT','A_EFFECT'))]
    violations = [m['name'] for m in metrics if m['numerical_nondominance_violation']]
    winners = [m for m in metrics if m['material_a_gain'] and m['wall_acceptable']
               and m.get('reproduction',{}).get('status') == 'PASS']
    pending_reproduction = [m['name'] for m in metrics if m['material_a_gain'] and m['wall_acceptable']
                            and m.get('reproduction',{}).get('status') == 'PENDING']
    raw = {m['raw_graph_id'] for m in winners}
    sources = {m['graph_source'] for m in winners}
    slow = [m['name'] for m in metrics if m['contrasts']['A_EFFECT']['status']=='MATCHED_COMPLETE' and not m['wall_acceptable']]
    if violations:
        verdict, why = 'INVESTIGATE', 'A2 apresentou violação numérica de dominância LP; investigar integridade/tolerância'
    elif censored:
        verdict, why = 'INVESTIGATE', 'Braços censurados impedem decisão conclusiva; permanecer no denominador'
    elif slow:
        verdict, why = 'STOP', 'Custo total do A2 ultrapassou limiar materialidade em casos pareados'
    elif pending_reproduction:
        verdict, why = 'INVESTIGATE', 'Ganho aparente requer seeds adicionais para comprovar reprodutibilidade'
    elif len(raw) >= rule['minimum_distinct_raw_graphs'] and len(sources) >= rule['minimum_distinct_graph_sources']:
        verdict, why = 'GO', 'Ganho material A2+K em grafos brutos e fontes distintas, custo aceitável'
    else:
        verdict, why = 'STOP', 'Ganho A2 insuficiente em pelo menos duas fontes de grafos independentes'
    return {'verdict':verdict,'reason':why,'raw_graphs_with_material_gain':sorted(raw),
            'sources_with_material_gain':sorted(sources),'n_winning_raw_graphs':len(raw),
            'n_winning_sources':len(sources),'censored_cases':sorted(censored),
            'numeric_dominance_violations':sorted(violations),'slowdown_cases':sorted(slow),
            'pending_reproduction':sorted(pending_reproduction),
            'denominator_cases':len(expected),'arm_status_counts':dict(sorted(Counter(
                status for m in metrics for status in m['arm_statuses'].values()).items()))}
