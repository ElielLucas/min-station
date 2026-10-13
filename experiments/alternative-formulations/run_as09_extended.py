#!/usr/bin/env python3
"""AS09 extended exploration: four paired formulations, LP and MIP, 600 s per arm.

Does not imply mathematical equivalence (pending independent proof). Frozen
manifest, source hashes, independent K, absolute wall-clock limits, physically
validated MIP incumbents, append-only artifact manifests and immutable plans.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import resource
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for folder in (HERE, ROOT, ROOT / 'experiments/formulation-comparison'):
    if str(folder) not in sys.path:
        sys.path.insert(0, str(folder))

from as02_model_a import Instance, compile_u
from as09_model_c import compile_c, dimension_estimate, prepare_physical_graph
from as04_runner import _load_timed, _optimize
from as04_schema import SolverPolicy
from as05_diag_core import _timed_k
from as06_mip import _solve_mip
from fc_budget import run_bounded
import fc_instances

SCHEMA = 'AS09-C-EXTENDED-PLAN-v1'
RESULT = 'AS09-C-EXTENDED-RESULT-v1'
MANIFEST = 'AS09-C-EXTENDED-MANIFEST-v1'
ANALYSIS = 'AS09-C-EXTENDED-ANALYSIS-v1'
ARMS = ('U', 'U_K', 'C', 'C_K')
MODES = ('LP', 'MIP')
PRIOR_SIX = (
    'mapf-room-32-32-4-m10-f8',
    'puc-bip42p-regiao-f2',
    'puc-cc9-2p-seed-r1',
    'puc-w3c571-seed-r1',
    'pucn-cc3-10n-seed-r1',
    'vienna-I056-regiao-f4',
)
EXTRA_NINE = (
    'mapf-den312d-m50-f2-rho',
    'mapf-empty-32-32-m25-f4',
    'mapf-maze-32-32-2-m10-f4',
    'mapf-random-64-64-20-m100-f4',
    'pace18-t2-061-regiao-f4',
    'vienna-I052-regiao-f4',
    'urb-apia-m10-f8',
    'b-b18-regiao-f2',
    'i-i160-301-regiao-f2',
)
FULL_CASES = PRIOR_SIX + EXTRA_NINE
SMOKE_CASES = ('mapf-room-32-32-4-m10-f8', 'puc-cc9-2p-seed-r1')
IMPLEMENTATION_PATHS = (
    'experiments/alternative-formulations/as09_model_c.py',
    'experiments/alternative-formulations/as02_model_a.py',
    'experiments/formulation-comparison/as04_runner.py',
    'experiments/formulation-comparison/as05_diag_core.py',
    'experiments/formulation-comparison/as06_mip.py',
    'experiments/formulation-comparison/fc_budget.py',
    'experiments/alternative-formulations/run_as09_extended.py',
)


def canonical_hash(data):
    raw = json.dumps(data, sort_keys=True, ensure_ascii=False, allow_nan=False,
                     separators=(',', ':')).encode('utf-8')
    return hashlib.sha256(raw).hexdigest()


def file_hash(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_once(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as file:
        json.dump(payload, file, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False)
        file.write('\n')


def markdown_once(path: Path, body: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as file:
        file.write(body)


def selected_cases(root: Path, suite: str):
    if suite not in ('full', 'smoke'):
        raise ValueError('Suite inválida')
    names = FULL_CASES if suite == 'full' else SMOKE_CASES
    rows = fc_instances.load_manifest(root / 'instances/manifest.csv')
    cases = []
    for name in names:
        matches = [r for r in rows if Path(r['nome']).stem == name]
        if len(matches) != 1:
            raise ValueError(f'Instância ausente/duplicada: {name}')
        row = matches[0]
        r = float(row['r'])
        if (row.get('classe') != 'principal' or not math.isfinite(r) or r < 1 or
            r != int(r) or float(row.get('peso_min') or 0) != 1 or
            float(row.get('peso_max') or 0) != 1):
            raise ValueError(f'Instância fora do domínio C: {name}')
        cases.append({'case': name, 'manifest_name': row['nome'],
                      'source_sha256': row['sha256'],
                      'source_family': row.get('fonte', ''),
                      'raw_graph_id': row.get('id_grafo_bruto', row.get('grafo', '')),
                      'split': row.get('particao', 'desconhecido'),
                      'r': int(r), 'n': int(row['n']), 'm': int(row['m']),
                      'physical_edges': int(row['arestas_nao_dirigidas']),
                      'reachability_arcs': int(row['n_arcos_alcance'])})
    return cases


def make_plan(root: Path, *, suite='full', budget=600, max_variables=900_000,
              max_constraints=350_000, threads=4, mip_gap=1e-4,
              validation_reserve=45):
    if (suite not in ('full', 'smoke') or not 30 <= budget <= 86_400 or
        not 10_000 <= max_variables <= 10_000_000 or
        not 10_000 <= max_constraints <= 10_000_000 or
        not 1 <= threads <= 32 or not 0 < mip_gap <= 0.1 or
        not 5 <= validation_reserve < budget / 2):
        raise ValueError('Parâmetros fora do domínio permitido')
    return {
        'schema': SCHEMA, 'classification': 'EXPLORATORY_MIXED_SPLITS',
        'suite': suite, 'math_gate': 'PROOF_REVIEW_REQUIRED',
        'manifest_sha256': file_hash(root / 'instances/manifest.csv'),
        'implementation_sha256': {name: file_hash(root / name) for name in IMPLEMENTATION_PATHS},
        'cases': selected_cases(root, suite), 'arms': list(ARMS), 'modes': list(MODES),
        'budget_seconds_per_arm': int(budget),
        'solver': {'backend': 'gurobi', 'threads': int(threads), 'seed': 42,
                   'mip_gap': float(mip_gap), 'validation_reserve_seconds': int(validation_reserve),
                   'warm_start': False},
        'caps': {'max_variables': int(max_variables), 'max_constraints': int(max_constraints)},
        'protocol': [
            'Cada braço recarrega dados, constrói A_r e seus próprios cortes K, quando aplicável',
            'Mesmo arquivo de origem e hash, orçamento e configuração Gurobi por braço',
            'LP compara somente objetivos OPTIMAL_NUMERIC e não prova equivalência analítica',
            'MIP requer validação independente de todo UB físico reportado',
            'Gap MIP somente com UB físico validado e bound numérico do Gurobi',
            'MIP sob limite de tempo preserva bound numérico e UB validado, se disponíveis',
            'Se supervisor matar worker não inventar gap, incumbente nem bound',
            'Resultados de avaliacao não autorizam ajuste posterior e promoção científica',
            'Tempo total inclui carregamento, alcance, K, montagem, solve e validação',
            'Nada altera resultados anteriores AS05/AS06/AS08/AS09',
        ]
    }


def validate_plan(plan: dict, root: Path):
    expected = make_plan(root, suite=plan['suite'], budget=plan['budget_seconds_per_arm'],
                         max_variables=plan['caps']['max_variables'],
                         max_constraints=plan['caps']['max_constraints'],
                         threads=plan['solver']['threads'],
                         mip_gap=plan['solver']['mip_gap'],
                         validation_reserve=plan['solver']['validation_reserve_seconds'])
    if plan != expected:
        raise ValueError('Plano/manifesto/código não coincide com a versão congelada')
    return plan


def _worker(ctx, row, root: str, mode: str, arm: str, plan: dict):
    if mode not in MODES or arm not in ARMS:
        raise ValueError('Modo/braço inválido')
    ctx.phase('preparation')
    loaded, load_s, reach_s = _load_timed(row, root)
    instance = Instance(tuple(loaded.V), tuple(loaded.S), tuple(loaded.T),
                        tuple(loaded.A_r), int(loaded.r))
    initial = {'status': 'NOT_STARTED', 'instance_sha256': loaded.instance_sha256,
               'input_load_s': load_s, 'reachability_s': reach_s,
               'K_sha256': None, 'K_count': 0, 'K_validated': False,
               'lp_numeric_value': None, 'model_complete': False,
               'mip_numeric_bound': None, 'mip_numeric_incumbent': None,
               'physical_validated_ub': None, 'physical_best_observed_ub': None,
               'validated_mip_gap': None, 'solver_runtime_s': None,
               'n_variables': None, 'n_constraints': None, 'n_nonzeros': None,
               'peak_rss_kb': None}
    cuts = ()
    if arm.endswith('_K'):
        ctx.phase('k_preparation')
        cuts, kprofile = _timed_k(instance, loaded, ctx, validator_method='bitset-v2')
        if not kprofile['k_validated']:
            raise ValueError('K não passou na validação independente')
        initial.update({'K_sha256': kprofile['k_sha256'], 'K_count': len(cuts),
                        'K_validated': True, 'k_phase_wall_s': kprofile['phase_wall_s']})
    graph = None
    if arm.startswith('C'):
        ctx.phase('physical_validation')
        graph = prepare_physical_graph(instance, loaded.adj)
        estimated = dimension_estimate(instance, graph, len(cuts))
    else:
        estimated = {'n_variables': len(instance.V) + len(instance.A_r),
                     'n_constraints': 3 * len(instance.V) + len(cuts)}
    initial['estimated_size'] = estimated
    if (estimated['n_variables'] > plan['caps']['max_variables'] or
        estimated['n_constraints'] > plan['caps']['max_constraints']):
        return {**initial, 'status': 'NOT_BUILT_SIZE', 'size_cap': plan['caps'],
                'reason': 'Tamanho pré-montagem excede cap'}
    ctx.phase('model_build')
    compiled = (compile_c(instance, loaded.adj, cuts, relax=mode == 'LP', physical_graph=graph)
                if graph is not None else compile_u(instance, cuts, relax=mode == 'LP'))
    if (len(compiled.variables) > plan['caps']['max_variables'] or
        len(compiled.equations) > plan['caps']['max_constraints']):
        return {**initial, 'status': 'NOT_BUILT_SIZE', 'size_cap': plan['caps'],
                'reason': 'Tamanho compilado excede cap'}
    if mode == 'LP':
        policy = SolverPolicy(seed=plan['solver']['seed'], threads=plan['solver']['threads'],
                              budget_s=plan['budget_seconds_per_arm'])
        result = _optimize(compiled, 'LP', policy, ctx)
        return {**initial, 'status': result['status'], 'model_complete': True,
                'lp_numeric_value': result.get('lp_opt_value') if result['status'] == 'OPTIMAL_NUMERIC' else None,
                'solver_runtime_s': result.get('solver_runtime_s'),
                'solver_version': result.get('solver_version'),
                'n_variables': result['n_variables'], 'n_constraints': result['n_constraints'],
                'n_nonzeros': result['n_nonzeros'],
                'peak_rss_kb': int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)}
    policy = {'threads': plan['solver']['threads'], 'seed': plan['solver']['seed'],
              'MIPGap': plan['solver']['mip_gap'], 'callback_sample_s': 5.0,
              'callback_max_incumbents': 32,
              'validation_reserve_s': plan['solver']['validation_reserve_seconds']}
    if ctx.remaining() < policy['validation_reserve_s'] + 1:
        return {**initial, 'status': 'NOT_BUILT_BUDGET',
                'reason': 'Orçamento restante insuficiente para solver e validação'}
    solved = _solve_mip(compiled, policy, ctx, loaded)
    # _solve_mip is AS06's independent physical incumbent validation code.
    return {**initial, **solved, 'model_complete': solved['status'] not in ('NOT_BUILT_BUDGET', 'SOLVER_ERROR'),
            'n_variables': len(compiled.variables),
            'n_constraints': len(compiled.equations),
            'n_nonzeros': compiled.n_nonzeros}


def _result_file(out: Path, mode: str, name: str, arm: str):
    return out / mode / f'{name}--{arm}.json'


def _expected_filenames(plan):
    return [f'{c["case"]}--{a}.json' for c in plan['cases'] for a in ARMS]


def execute(plan, root: Path, out: Path, *, mode: str, resume=False):
    validate_plan(plan, root)
    if mode not in MODES:
        raise ValueError('Execute LP e MIP separadamente')
    mode_dir = out / mode
    if mode_dir.exists() and any(mode_dir.iterdir()) and not resume:
        raise FileExistsError('Modo já tem arquivos; use --resume ou outra pasta')
    if (out / 'plan.json').exists():
        if json.loads((out / 'plan.json').read_text()) != plan:
            raise ValueError('Plano não coincide com a execução existente')
    else:
        write_once(out / 'plan.json', plan)
    mode_dir.mkdir(parents=True, exist_ok=True)
    rows = {r['nome']: r for r in fc_instances.load_manifest(root / 'instances/manifest.csv')}
    for case in plan['cases']:
        row = rows[case['manifest_name']]
        if row['sha256'] != case['source_sha256']:
            raise ValueError('SHA da instância mudou: ' + case['case'])
        for arm in ARMS:
            path = _result_file(out, mode, case['case'], arm)
            if path.exists():
                data = json.loads(path.read_text(encoding='utf-8'))
                if not resume or data.get('case') != case or data.get('arm') != arm or \
                   data.get('mode') != mode or data.get('plan_sha256') != canonical_hash(plan):
                    raise ValueError('Resultado já existente incompatível com --resume')
                print('AS09_EXT_RESUMED', mode, case['case'], arm, data['status'], flush=True)
                continue
            bounded = run_bounded(_worker, row, str(root), mode, arm, plan,
                                  budget_s=plan['budget_seconds_per_arm'])
            base = {'schema': RESULT, 'case': case, 'arm': arm, 'mode': mode,
                    'plan_sha256': canonical_hash(plan),
                    'wall_total_s': bounded.wall_total_s,
                    'wall_phases_s': dict(bounded.phase_wall_s)}
            if bounded.status == 'COMPLETED':
                payload = bounded.value
            else:
                payload = {'status': bounded.status, 'reason': bounded.reason,
                           'model_complete': False, 'lp_numeric_value': None,
                           'mip_numeric_bound': None, 'mip_numeric_incumbent': None,
                           'physical_validated_ub': None, 'validated_mip_gap': None}
            result = {**base, **payload}
            if result['status'] != 'OPTIMAL_NUMERIC':
                result['lp_numeric_value'] = None
            write_once(path, result)
            metric = ('LP=' + str(result.get('lp_numeric_value')) if mode == 'LP' else
                      'UB=' + str(result.get('physical_validated_ub')) +
                      ' LB=' + str(result.get('mip_numeric_bound')) +
                      ' GAP=' + str(result.get('validated_mip_gap')))
            print('AS09_EXT_CASE', mode, case['case'], arm, result['status'], metric,
                  'WALL', round(bounded.wall_total_s, 2), flush=True)
    files = {name: file_hash(mode_dir / name) for name in _expected_filenames(plan)}
    manifest = {'schema': MANIFEST, 'mode': mode, 'plan_sha256': canonical_hash(plan),
                'files': files}
    if (mode_dir / 'manifest.json').exists():
        if json.loads((mode_dir / 'manifest.json').read_text()) != manifest:
            raise ValueError('Manifest existente diverge da execução')
    else:
        write_once(mode_dir / 'manifest.json', manifest)
    return verify(plan, root, out, mode=mode)


def verify(plan, root: Path, out: Path, *, mode: str):
    validate_plan(plan, root)
    if mode not in MODES:
        raise ValueError('Modo desconhecido')
    stored = json.loads((out / 'plan.json').read_text(encoding='utf8'))
    if stored != plan:
        raise ValueError('Plano executado difere do plano verificado')
    manifest = json.loads((out / mode / 'manifest.json').read_text(encoding='utf8'))
    expected = {'schema': MANIFEST, 'mode': mode, 'plan_sha256': canonical_hash(plan),
                'files': {name: file_hash(out / mode / name) for name in _expected_filenames(plan)}}
    if manifest != expected:
        raise ValueError('Manifest de integridade inválido')
    results = {}
    for case in plan['cases']:
        for arm in ARMS:
            data = json.loads(_result_file(out, mode, case['case'], arm).read_text())
            if (data.get('schema') != RESULT or data.get('case') != case or
                data.get('arm') != arm or data.get('mode') != mode or
                data.get('plan_sha256') != canonical_hash(plan)):
                raise ValueError('Identidade de resultado inválida')
            if mode == 'LP':
                obj = data.get('lp_numeric_value')
                if data['status'] == 'OPTIMAL_NUMERIC':
                    if (not data.get('model_complete') or
                        data.get('instance_sha256') != case['source_sha256'] or
                        not isinstance(obj, (int, float)) or not math.isfinite(obj)):
                        raise ValueError('LP ótimo numérico sem evidência completa')
                elif obj is not None:
                    raise ValueError('Resultado censurado publicou ótimo LP')
            else:
                ub = data.get('physical_validated_ub')
                lb = data.get('mip_numeric_bound')
                gap = data.get('validated_mip_gap')
                if data['status'] in ('OPTIMAL_NUMERIC', 'TIME_LIMIT', 'NO_INCUMBENT'):
                    if not data.get('model_complete') or data.get('instance_sha256') != case['source_sha256']:
                        raise ValueError('Resultado MIP sem modelo ou fonte íntegros')
                if ub is not None and (not isinstance(ub, (int, float)) or
                                       not math.isfinite(ub) or ub < 0):
                    raise ValueError('Incumbente física inválida')
                if lb is not None and (not isinstance(lb, (int, float)) or not math.isfinite(lb)):
                    raise ValueError('Bound inválido')
                if gap is not None:
                    if ub is None or lb is None or abs(gap - max(0.,(ub-lb)/max(1.,abs(ub)))) > 1e-6:
                        raise ValueError('Gap sem evidência de UB e LB')
                if data['status'] not in ('OPTIMAL_NUMERIC', 'TIME_LIMIT', 'NO_INCUMBENT') and \
                   any(data.get(f) is not None for f in ('physical_validated_ub',
                        'mip_numeric_bound', 'validated_mip_gap')):
                    raise ValueError('Resultado censurado divulgou métrica MIP')
            if arm.endswith('_K') and data['status'] in ('OPTIMAL_NUMERIC', 'TIME_LIMIT', 'NO_INCUMBENT'):
                if not data.get('K_validated') or not data.get('K_sha256'):
                    raise ValueError('Resultado com K não validado')
            results[case['case'], arm] = data
        if (results[case['case'], 'U_K'].get('K_sha256') and
            results[case['case'], 'C_K'].get('K_sha256') and
            results[case['case'], 'U_K']['K_sha256'] != results[case['case'], 'C_K']['K_sha256']):
            raise ValueError('Cortes K não coincidem entre COMP+K e C+K')
    return results


def _fmt(x, digits=4):
    return '—' if x is None else (str(x) if isinstance(x, int) else f'{x:.{digits}f}' if isinstance(x, float) else str(x))


def analyze(plan, root: Path, out: Path, *, mode: str):
    modes = MODES if mode == 'ALL' else (mode,)
    data = {m: verify(plan, root, out, mode=m) for m in modes}
    if len(modes) == 2:
        for case in plan['cases']:
            for arm in ('U_K','C_K'):
                left=data['LP'][case['case'],arm].get('K_sha256')
                right=data['MIP'][case['case'],arm].get('K_sha256')
                if left and right and left!=right:
                    raise ValueError('K diverge entre LP e MIP para '+case['case']+'/'+arm)
    rows = []
    pairs = []
    md = ['# AS-09 — Benchmark ampliado COMP, COMP+K, C, C+K', '',
          '**Classificação:** exploratório, equivalência matemática de projeções ainda depende de revisão independente.',
          '', f'**Protocolo:** {len(plan["cases"])} instâncias, {plan["budget_seconds_per_arm"]} s por braço, seed 42, threads {plan["solver"]["threads"]}.',
          'Wall inclui leitura, alcance, cortes, construção e solução; RSS é pico do processo.',
          'Os casos de avaliação não autorizam ajustes de parâmetros posteriores.', '']
    for m in modes:
        md += [f'## {m}', '']
        if m == 'LP':
            md += ['| Caso | Braço | Status | LP | Variáveis | Restrições | Não zeros | Wall(s) | Solver(s) | RSS(MiB) |',
                   '|---|---|---|---:|---:|---:|---:|---:|---:|---:|']
        else:
            md += ['| Caso | Braço | Status | UB físico | LB solver | Gap validado | Nós | Wall(s) | 1ª UB(s) | RSS(MiB) |',
                   '|---|---|---|---:|---:|---:|---:|---:|---:|---:|']
        for case in plan['cases']:
            name = case['case']
            for arm in ARMS:
                result = data[m][name,arm]
                row = {'mode': m, 'case': name, 'source_family': case['source_family'],
                       'split': case['split'], 'arm': arm, 'status': result['status'],
                       'wall_s': result['wall_total_s'], 'solver_s': result.get('solver_runtime_s'),
                       'variables': result.get('n_variables'),
                       'constraints': result.get('n_constraints'),
                       'nonzeros': result.get('n_nonzeros'),
                       'rss_mib': (result['peak_rss_kb'] / 1024 if result.get('peak_rss_kb') is not None else None),
                       'lp_value': result.get('lp_numeric_value') if m == 'LP' else None,
                       'mip_ub_validated': result.get('physical_validated_ub') if m == 'MIP' else None,
                       'mip_lb_numeric': result.get('mip_numeric_bound') if m == 'MIP' else None,
                       'mip_gap_validated': result.get('validated_mip_gap') if m == 'MIP' else None,
                       'nodes': result.get('nodes') if m == 'MIP' else None,
                       'time_first_ub_solver_s': result.get('time_to_first_validated_ub_solver_s') if m == 'MIP' else None}
                rows.append(row)
                if m == 'LP':
                    md.append('| ' + ' | '.join((_fmt(name), arm, row['status'],
                         _fmt(row['lp_value']), _fmt(row['variables']),
                         _fmt(row['constraints']), _fmt(row['nonzeros']),
                         _fmt(row['wall_s'], 2), _fmt(row['solver_s'], 2),
                         _fmt(row['rss_mib'], 1))) + ' |')
                else:
                    md.append('| ' + ' | '.join((_fmt(name), arm, row['status'],
                         _fmt(row['mip_ub_validated']), _fmt(row['mip_lb_numeric']),
                         _fmt(row['mip_gap_validated'], 5), _fmt(row['nodes'], 0),
                         _fmt(row['wall_s'], 2), _fmt(row['time_first_ub_solver_s'], 2),
                         _fmt(row['rss_mib'], 1))) + ' |')
            # LP numeric y objective equality is a necessary signal, not a proof.
            if m == 'LP':
                for suffix in ('', '_K'):
                    a, b = data[m][name, 'U'+suffix], data[m][name, 'C'+suffix]
                    if a['status'] == b['status'] == 'OPTIMAL_NUMERIC':
                        equal = abs(a['lp_numeric_value'] - b['lp_numeric_value']) <= 1e-5
                        if not equal:
                            md.append(f'**ALERTA: LP DISCORDANTE em {name}, cortes={bool(suffix)}.**')
        md.append('')
        md += ['### Comparação pareada — C versus COMP', '']
        if m == 'LP':
            md += ['| Caso | K | LP igual? | Tempo COMP(s) | Tempo C(s) | Economia de tempo | Economia RSS | Economia vars | Economia nnz |',
                   '|---|---|---|---:|---:|---:|---:|---:|---:|']
        else:
            md += ['| Caso | K | Gap COMP | Gap C | Melhora gap (p.p.) | UB COMP | UB C | LB COMP | LB C | Economia de tempo |',
                   '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|']
        for case in plan['cases']:
            for suffix in ('', '_K'):
                lhs=data[m][case['case'], 'U'+suffix]
                rhs=data[m][case['case'], 'C'+suffix]
                def reduction(field):
                    old,new=lhs.get(field),rhs.get(field)
                    return 100*(old-new)/old if isinstance(old,(int,float)) and isinstance(new,(int,float)) and old>0 else None
                p={'mode':m,'case':case['case'],'source_family':case['source_family'],
                   'K':bool(suffix),'status_U':lhs['status'],'status_C':rhs['status'],
                   'wall_speedup_pct':reduction('wall_total_s'),
                   'rss_reduction_pct':reduction('peak_rss_kb'),
                   'variable_reduction_pct':reduction('n_variables'),
                   'nnz_reduction_pct':reduction('n_nonzeros'),
                   'lp_equal_numeric':None,'lp_difference_C_minus_U':None,
                   'gap_U':lhs.get('validated_mip_gap') if m=='MIP' else None,
                   'gap_C':rhs.get('validated_mip_gap') if m=='MIP' else None,
                   'gap_improvement_pp':None,
                   'ub_U':lhs.get('physical_validated_ub') if m=='MIP' else None,
                   'ub_C':rhs.get('physical_validated_ub') if m=='MIP' else None,
                   'lb_U':lhs.get('mip_numeric_bound') if m=='MIP' else None,
                   'lb_C':rhs.get('mip_numeric_bound') if m=='MIP' else None}
                if m=='LP' and lhs['status']==rhs['status']=='OPTIMAL_NUMERIC':
                    delta=rhs['lp_numeric_value']-lhs['lp_numeric_value']
                    p['lp_equal_numeric']=abs(delta)<=1e-5
                    p['lp_difference_C_minus_U']=delta
                if (m=='MIP' and p['gap_U'] is not None and p['gap_C'] is not None):
                    p['gap_improvement_pp']=100*(p['gap_U']-p['gap_C'])
                pairs.append(p)
                def pct(x): return '—' if x is None else f'{x:+.1f}%'
                if m=='LP':
                    md.append('| '+ ' | '.join((case['case'], 'sim' if suffix else 'não',
                       str(p['lp_equal_numeric']),_fmt(lhs['wall_total_s'],2),
                       _fmt(rhs['wall_total_s'],2),pct(p['wall_speedup_pct']),
                       pct(p['rss_reduction_pct']),pct(p['variable_reduction_pct']),
                       pct(p['nnz_reduction_pct'])))+' |')
                else:
                    md.append('| '+ ' | '.join((case['case'], 'sim' if suffix else 'não',
                       pct(100*p['gap_U']) if p['gap_U'] is not None else '—',
                       pct(100*p['gap_C']) if p['gap_C'] is not None else '—',
                       (_fmt(p['gap_improvement_pp'],2) if p['gap_improvement_pp'] is not None else '—'),
                       _fmt(p['ub_U']),_fmt(p['ub_C']),_fmt(p['lb_U']),
                       _fmt(p['lb_C']),pct(p['wall_speedup_pct'])))+' |')
        md.append('')
    disagreement = []
    if 'LP' in data:
        for case in plan['cases']:
            for suffix in ('', '_K'):
                lhs = data['LP'][case['case'], 'U'+suffix]
                rhs = data['LP'][case['case'], 'C'+suffix]
                if lhs['status'] == rhs['status'] == 'OPTIMAL_NUMERIC' and abs(lhs['lp_numeric_value']-rhs['lp_numeric_value']) > 1e-5:
                    disagreement.append((case['case'],suffix))
    if disagreement:
        gate = 'BLOCK_LP_DISAGREEMENT'
    elif any(r['status'] not in ('OPTIMAL_NUMERIC', 'TIME_LIMIT', 'NO_INCUMBENT') for r in rows):
        gate = 'EXPLORATORY_WITH_CENSORED_ARMS'
    elif 'MIP' in data and any(r['mode']=='MIP' and r['status'] != 'OPTIMAL_NUMERIC' for r in rows):
        gate = 'EXPLORATORY_WITH_MIP_LIMITS'
    else:
        gate = 'EXPLORATORY_PROOF_REVIEW_REQUIRED'
    payload = {'schema': ANALYSIS, 'classification':'EXPLORATORY',
               'decision':gate, 'math_gate':'PROOF_REVIEW_REQUIRED',
               'plan_sha256':canonical_hash(plan), 'modes': list(modes),
               'rows':rows, 'pairs':pairs, 'lp_disagreement':disagreement,
               'note':'MIP gap usa exclusivamente UB validado por oráculo físico; bound Gurobi é numérico.'}
    suffix = '-'+mode.lower()
    write_once(out / f'analysis{suffix}.json', payload)
    for filename, content in ((f'arms{suffix}.csv', rows), (f'pairs{suffix}.csv', pairs)):
        path=out/filename
        with path.open('x',encoding='utf-8',newline='') as fh:
            if content:
                writer=csv.DictWriter(fh,fieldnames=list(content[0].keys()))
                writer.writeheader();writer.writerows(content)
    markdown_once(out / f'analysis{suffix}.md', '\n'.join(md)+f'\n**Decisão exploratória:** `{gate}`.\n')
    return gate


def main(argv=None):
    parser = argparse.ArgumentParser(description='AS09 ampliado: LP e MIP 4 braços, 600s por execução')
    action = parser.add_mutually_exclusive_group(required=True)
    for flag in ('init-plan','check-plan','execute','verify','analyze'):
        action.add_argument('--'+flag, action='store_true')
    parser.add_argument('--plan', required=True, type=Path)
    parser.add_argument('--output-dir', type=Path)
    parser.add_argument('--suite', choices=('full','smoke'), default='full')
    parser.add_argument('--mode', choices=('LP','MIP','ALL'), default='ALL')
    parser.add_argument('--budget', type=int, default=600)
    parser.add_argument('--max-variables', type=int, default=900000)
    parser.add_argument('--max-constraints', type=int, default=350000)
    parser.add_argument('--threads', type=int, default=4)
    parser.add_argument('--mip-gap', type=float, default=1e-4)
    parser.add_argument('--validation-reserve', type=int, default=45)
    parser.add_argument('--resume', action='store_true')
    args=parser.parse_args(argv)
    if args.init_plan:
        plan=make_plan(ROOT, suite=args.suite, budget=args.budget,
                       max_variables=args.max_variables,max_constraints=args.max_constraints,
                       threads=args.threads,mip_gap=args.mip_gap,
                       validation_reserve=args.validation_reserve)
        write_once(args.plan, plan)
        print('AS09_EXT_PLAN_CREATED',len(plan['cases']),'cases',len(plan['cases'])*len(ARMS)*len(MODES),
              'arms',canonical_hash(plan));return 0
    plan=json.loads(args.plan.read_text(encoding='utf8'))
    validate_plan(plan,ROOT)
    if args.check_plan:
        print('AS09_EXT_PLAN_VALID',canonical_hash(plan));return 0
    if args.output_dir is None:
        parser.error('--output-dir é obrigatório')
    if args.execute:
        for mode in (MODES if args.mode == 'ALL' else (args.mode,)):
            res=execute(plan,ROOT,args.output_dir,mode=mode,resume=args.resume)
            print('AS09_EXT_COMPLETED',mode,len(res),'arms')
        return 0
    if args.verify:
        for mode in (MODES if args.mode == 'ALL' else (args.mode,)):
            res=verify(plan,ROOT,args.output_dir,mode=mode)
            print('AS09_EXT_VERIFIED',mode,len(res),'arms')
        return 0
    if args.analyze:
        gate=analyze(plan,ROOT,args.output_dir,mode=args.mode)
        print('AS09_EXT_ANALYZED',gate,args.output_dir / f'analysis-{args.mode.lower()}.md')
        return 0
    return 1

if __name__ == '__main__':
    raise SystemExit(main())
