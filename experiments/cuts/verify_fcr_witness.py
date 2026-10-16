"""AS23: independent, exact-rational audit of the FC-R relay witness.

Not a production separator. HiGHS proposes primal/dual points; only exact
Fraction checks against *recompiled* COMP+K rows certify the conclusions.
Run: python experiments/cuts/verify_fcr_witness.py --output results/benchmark/as23-fcr-witness-001.json
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import sys
import subprocess
from dataclasses import dataclass
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
AS02_DIR = ROOT / 'experiments' / 'alternative-formulations'
if str(AS02_DIR) not in sys.path:
    sys.path.insert(0, str(AS02_DIR))
from as02_model_a import Instance, compile_u, prepare_K
from experiments.cuts.cuts import build_neighborhoods, generate_C6


@dataclass(frozen=True)
class Row:
    name: str
    terms: tuple[tuple[int, F], ...]
    sense: str
    rhs: F


def make_row(name, terms, sense, rhs):
    combined = {}
    for j, coefficient in terms:
        combined[j] = combined.get(j, F(0)) + F(coefficient)
    return Row(name, tuple(sorted((j, c) for j, c in combined.items() if c)), sense, F(rhs))


def witness_instance():
    """Build physical edges independently of Astra's claimed K and bounds."""
    a = tuple(f'a{i}' for i in range(1, 5))
    e = ('e1', 'e2')
    c = ('c1', 'c2')
    d = ('d1', 'd2')
    g = ('g1', 'g2')
    blocks = tuple(tuple(f'x{i}{j}' for j in range(1, 4)) for i in range(1, 5))
    V = a + e + c + d + g + tuple(itertools.chain.from_iterable(blocks))
    edges = set()

    def edge(u, v):
        edges.add(tuple(sorted((u, v))))

    for i, s in enumerate(a):
        for t in c:
            edge(s, t)
        for x in blocks[i]:
            edge(s, x)
            for t in d:
                edge(x, t)
    for i, s in enumerate(e):
        edge(s, d[i])
        edge(s, g[i])
    arcs = tuple(sorted((u, v) for x, y in edges for u, v in ((x, y), (y, x))))
    adj = {v: [] for v in V}
    for u, v in arcs:
        adj[u].append((v, 1))
    adj = {v: tuple(sorted(neighbors)) for v, neighbors in adj.items()}
    instance = Instance(V=V, S=a + e, T=c + d + g, A_r=arcs, r=1)
    return instance, adj, blocks, edges


def build_system():
    instance, adj, blocks, edges = witness_instance()
    K = prepare_K(instance, adj, instance.r)
    compiled = compile_u(instance, K, relax=True)
    rows = [make_row(row.name, row.terms, row.sense, row.rhs)
            for row in compiled.equations]
    columns = compiled.columns
    plus, minus = build_neighborhoods(instance.A_r)
    sources = set(instance.S)
    targets = set(instance.T)

    c6, incomplete = generate_C6(instance.S, instance.T, plus, minus)
    c6_rows = [make_row(f'C6[{i}]', ((columns['y', v], k) for v, k in terms),
                        '>=', rhs) for i, (terms, rhs) in enumerate(c6)]
    # C8 is the documented P4 family: an origin can recycle only f_in(s),
    # and a destination can recycle only f_out(t). Direct terminal arcs
    # are excluded since they do not require an intermediate station.
    c8_rows = []
    for s in sorted(sources - targets):
        for v in sorted(plus.get(s, set()) - targets):
            terms = [(columns['F', s, v], 1), (columns['y', v], -1)]
            terms += [(columns['F', u, s], -1) for u in sorted(minus.get(s, set()))]
            c8_rows.append(make_row(f'C8O[{s},{v}]', terms, '<=', 0))
    for t in sorted(targets - sources):
        for u in sorted(minus.get(t, set()) - sources):
            terms = [(columns['F', u, t], 1), (columns['y', u], -1)]
            terms += [(columns['F', t, v], -1) for v in sorted(plus.get(t, set()))]
            c8_rows.append(make_row(f'C8T[{u},{t}]', terms, '<=', 0))

    fcr = [fcr_region_row(instance, columns, (s,), blocks[i], 'origin')
           for i, s in enumerate(instance.S[:4])]
    return {'instance': instance, 'adj': adj, 'blocks': blocks, 'edges': edges,
            'K': K, 'compiled': compiled, 'base': rows,
            'C6': c6_rows, 'C8': c8_rows, 'FCR': fcr,
            'c6_incomplete': incomplete}


def fcr_region_row(instance, columns, L, Q, direction='origin'):
    """Audit-only constructor: refuses invalid terminal sets or reachability."""
    V, S, T = set(instance.V), set(instance.S), set(instance.T)
    region, chosen = set(L), set(Q)
    if not region or not region <= V or not chosen <= V:
        raise ValueError('invalid L or Q')
    excess = len(S & region) - len(T & region)
    if direction == 'origin':
        demand = excess
        permitted = {v for u, v in instance.A_r if u in region and v not in region} - T
        arcs = [(u, v) for u, v in instance.A_r if u in region and v not in region | chosen]
    elif direction == 'destination':
        demand = -excess
        permitted = {u for u, v in instance.A_r if v in region and u not in region} - S
        arcs = [(u, v) for u, v in instance.A_r if v in region and u not in region | chosen]
    else:
        raise ValueError('direction must be origin/destination')
    if demand <= 0 or not chosen <= permitted or (chosen & region):
        raise ValueError('nonpositive regional excess or Q contains noneligible vertices')
    terms = [(columns['F', u, v], 1) for u, v in arcs]
    terms += [(columns['y', v], demand) for v in sorted(chosen)]
    return make_row(f'FC-R-{direction}[{",".join(sorted(region))};{",".join(sorted(chosen))}]',
                    terms, '>=', demand)


def select_q_fixed_region(instance, L, y, f, direction='origin'):
    """Exact Q for fixed L; ties remain outside Q for deterministic output."""
    region = set(L)
    excess = len(set(instance.S) & region) - len(set(instance.T) & region)
    if direction == 'origin':
        d = excess
        arcs = ((u, v) for u, v in instance.A_r if u in region and v not in region)
        excluded = set(instance.T)
        target = lambda u, v: v
    elif direction == 'destination':
        d = -excess
        arcs = ((u, v) for u, v in instance.A_r if v in region and u not in region)
        excluded = set(instance.S)
        target = lambda u, v: u
    else:
        raise ValueError('direction')
    if d <= 0:
        raise ValueError('region must have strict directional excess')
    weights = {}
    for u, v in arcs:
        w = target(u, v)
        if w not in excluded:
            weights[w] = weights.get(w, F(0)) + F(f.get((u, v), 0))
    return tuple(sorted(v for v, weight in weights.items()
                        if weight > d * F(y.get(v, 0))))


def rationalize(x, limit=100000):
    if not math.isfinite(float(x)):
        raise ValueError('nonfinite LP candidate')
    return F(float(x)).limit_denominator(limit)


def row_value(row, vector):
    return sum((coef * vector[j] for j, coef in row.terms), F(0))


def primal_checked(rows, variables, vector):
    for v, x in zip(variables, vector):
        if x < F(v.lb) or (math.isfinite(v.ub) and x > F(v.ub)):
            raise AssertionError(f'variable bound: {v.name}={x}')
    for row in rows:
        lhs = row_value(row, vector)
        ok = ((row.sense == '==' and lhs == row.rhs) or
              (row.sense == '<=' and lhs <= row.rhs) or
              (row.sense == '>=' and lhs >= row.rhs))
        if not ok:
            raise AssertionError(f'row {row.name}: {lhs} {row.sense} {row.rhs}')


def solve_exact_certificate(compiled, rows):
    """Floating optimizer *proposes* values; exact primal/dual prove optimality."""
    import numpy as np
    from scipy.optimize import linprog

    n = len(compiled.variables)
    aub, bub, aeq, beq = [], [], [], []
    ub_rows, eq_rows = [], []
    for row in rows:
        coeff = np.zeros(n)
        for j, k in row.terms:
            coeff[j] = float(k)
        if row.sense == '==':
            aeq.append(coeff); beq.append(float(row.rhs)); eq_rows.append(row)
        else:
            sign = -1 if row.sense == '>=' else 1
            aub.append(sign * coeff); bub.append(sign * float(row.rhs))
            ub_rows.append((row, sign))
    bounds = [(v.lb, v.ub if math.isfinite(v.ub) else None)
              for v in compiled.variables]
    objective = [F(compiled.objective.get(j, 0)) for j in range(n)]
    result = linprog([float(c) for c in objective],
                     A_ub=aub, b_ub=bub, A_eq=aeq, b_eq=beq,
                     bounds=bounds, method='highs')
    if not result.success:
        raise RuntimeError('HiGHS failed: ' + result.message)
    primal = tuple(map(rationalize, result.x))
    primal_checked(rows, compiled.variables, primal)
    primal_value = sum((objective[j] * primal[j] for j in range(n)), F(0))

    du = tuple(map(rationalize, result.ineqlin.marginals))
    de = tuple(map(rationalize, result.eqlin.marginals))
    dl = tuple(map(rationalize, result.lower.marginals))
    dh = tuple(map(rationalize, result.upper.marginals))
    assert all(x <= 0 for x in du) and all(x >= 0 for x in dl) and all(x <= 0 for x in dh)
    dual_expression = [F(0)] * n
    dual_value = F(0)
    for (row, sign), weight in zip(ub_rows, du):
        for j, k in row.terms:
            dual_expression[j] += weight * sign * k
        dual_value += weight * sign * row.rhs
    for row, weight in zip(eq_rows, de):
        for j, k in row.terms:
            dual_expression[j] += weight * k
        dual_value += weight * row.rhs
    for j, variable in enumerate(compiled.variables):
        dual_expression[j] += dl[j] + dh[j]
        dual_value += dl[j] * F(variable.lb)
        if math.isfinite(variable.ub):
            dual_value += dh[j] * F(variable.ub)
        elif dh[j]:
            raise AssertionError('dual nonzero at missing upper bound')
    if tuple(dual_expression) != tuple(objective):
        raise AssertionError('exact dual stationarity mismatch')
    if dual_value != primal_value:
        raise AssertionError(f'exact primal-dual gap: {primal_value} vs {dual_value}')
    y = {key[1]: primal[j] for key, j in compiled.columns.items() if key[0] == 'y'}
    active = [{'row': row.name, 'multiplier': str(weight)}
              for (row, _), weight in zip(ub_rows, du) if weight]
    active += [{'row': row.name, 'multiplier': str(weight)}
               for row, weight in zip(eq_rows, de) if weight]
    active += [{'row': compiled.variables[j].name, 'bound': 'lower', 'multiplier': str(weight)}
               for j, weight in enumerate(dl) if weight]
    active += [{'row': compiled.variables[j].name, 'bound': 'upper', 'multiplier': str(weight)}
               for j, weight in enumerate(dh) if weight]
    return {'objective': str(primal_value), 'primal': [str(v) for v in primal],
            'dual_ub': [str(v) for v in du], 'dual_eq': [str(v) for v in de],
            'dual_lower': [str(v) for v in dl], 'dual_upper': [str(v) for v in dh],
            'dual_objective': str(dual_value), 'nonzero_dual': active,
            'y_nonzero': {v: str(z) for v, z in sorted(y.items()) if z}}


def recheck_saved(compiled, rows, certificate):
    """Validate stored witness with no scipy, Gurobi or optimizer involved."""
    primal = tuple(map(F, certificate['primal']))
    primal_checked(rows, compiled.variables, primal)
    n = len(compiled.variables)
    du, de, dl, dh = (tuple(map(F, certificate[k])) for k in
                      ('dual_ub', 'dual_eq', 'dual_lower', 'dual_upper'))
    ub_rows = [(r, -1 if r.sense == '>=' else 1) for r in rows if r.sense != '==']
    eq_rows = [r for r in rows if r.sense == '==']
    if (len(du),len(de),len(dl),len(dh)) != (len(ub_rows),len(eq_rows),n,n):
        raise AssertionError('certificate dimension mismatch')
    if any(x > 0 for x in du) or any(x < 0 for x in dl) or any(x > 0 for x in dh):
        raise AssertionError('dual sign mismatch')
    c = [F(compiled.objective.get(j, 0)) for j in range(n)]
    stat = [F(0)] * n
    dualval = F(0)
    for (r, sign), mu in zip(ub_rows, du):
        dualval += sign * r.rhs * mu
        for j, val in r.terms: stat[j] += sign * val * mu
    for r, mu in zip(eq_rows, de):
        dualval += r.rhs * mu
        for j, val in r.terms: stat[j] += val * mu
    for j, v in enumerate(compiled.variables):
        stat[j] += dl[j] + dh[j]
        dualval += dl[j] * F(v.lb)
        if math.isfinite(v.ub): dualval += dh[j] * F(v.ub)
        elif dh[j]: raise AssertionError('unbounded variable has upper dual')
    val = sum((c[j]*primal[j] for j in range(n)), F(0))
    if stat != c or dualval != val or certificate['objective'] != str(val):
        raise AssertionError('invalid exact primal/dual certificate')
    return val


def physical_report(system):
    cuts_dir = str(ROOT / 'experiments' / 'cuts')
    if cuts_dir not in sys.path:sys.path.insert(0, cuts_dir)
    from independent_validator import viavel
    ins = system['instance']
    empty = viavel(ins.S, ins.T, ins.V, system['adj'], ins.r, [])
    singleton = [s for s in ins.V if viavel(ins.S, ins.T, ins.V, system['adj'], ins.r, [s])]
    two_stations = (system['blocks'][0][0], system['blocks'][1][0])
    pair = viavel(ins.S, ins.T, ins.V, system['adj'], ins.r, two_stations)
    if empty or singleton or not pair:
        raise AssertionError(f'physical mismatch: empty {empty}, singleton {singleton}, pair {pair}')
    return {'empty_viable': empty, 'viable_singletons': singleton,
            'checked_singletons': len(ins.V), 'feasible_pair': list(two_stations),
            'pair_viable': pair, 'proved_integer_optimum': 2}


def declared_c8_counterexample(system):
    """Independently reconstruct Astra's explicit 17/15 C8-compatible point."""
    model = system['compiled']
    vec = [F(0)] * len(model.variables)
    cols = model.columns
    def y(vertex, value):
        vec[cols['y', vertex]] = F(value)
    def flow(u, v, value):
        vec[cols['F', u, v]] += F(value)
    for block in system['blocks'][:2]:
        for v in block:
            y(v, F(1, 6))
    for v in ('a1', 'a2', 'c1', 'c2'):
        y(v, F(1, 30))
    for i in range(2):
        s = f'a{i+1}'
        for relay in system['blocks'][i]:
            flow(s, relay, F(1,3))
            for target in ('d1', 'd2'):
                flow(relay, target, F(1,6))
        target = f'c{i+1}'
        flow(s, target, F(1,6))
        flow(target, s, F(1,6))
    flow('a3', 'c1', 1)
    flow('a4', 'c2', 1)
    flow('e1', 'g1', 1)
    flow('e2', 'g2', 1)
    primal_checked(system['base'] + system['C8'], model.variables, vec)
    cost = sum((vec[cols['y', v]] for v in system['instance'].V), F(0))
    if cost != F(17,15):
        raise AssertionError(f'declared 17/15 counterexample has cost {cost}')
    fcr_deficits = [r.rhs-row_value(r, vec) for r in system['FCR']]
    if fcr_deficits != [F(1,3),F(1,3),F(0),F(0)]:
        raise AssertionError(f'declared FC-R deficits differ: {fcr_deficits}')
    c6_deficits = [r.rhs-row_value(r, vec) for r in system['C6']]
    if not all(x > 0 for x in c6_deficits):
        raise AssertionError('17/15 example should violate C6')
    return {'objective': str(cost), 'fcr_deficits': [str(x) for x in fcr_deficits],
            'c6_deficits': [str(x) for x in c6_deficits],
            'description': 'Explicit 17/15 point satisfies COMP+K+C8; violates C6 and FC-R'}


def source_revision():
    """Report the actual HEAD; do not misrepresent dirty changes as committed."""
    try:
        result = subprocess.run(['git', '-C', str(ROOT), 'rev-parse', '--verify', 'HEAD'],
                                check=True, capture_output=True, text=True)
        revision = result.stdout.strip()
        if len(revision) != 40 or any(c not in '0123456789abcdef' for c in revision):
            raise ValueError('invalid git SHA')
        changed = subprocess.run(['git', '-C', str(ROOT), 'status', '--porcelain',
                                  '--untracked-files=normal', '--',
                                  'experiments/cuts/verify_fcr_witness.py',
                                  'experiments/alternative-formulations/as02_model_a.py',
                                  'experiments/cuts/cuts.py',
                                  'experiments/cuts/independent_validator.py'],
                                 check=True, capture_output=True, text=True)
        if changed.stdout.strip():
            return revision, ('HEAD is not the exact source snapshot: relevant files have '
                              'uncommitted changes; inspect source_sha256 and rerun after commit')
        return revision, 'Git HEAD for source files; verify source_sha256 for exact content'
    except (OSError, subprocess.CalledProcessError, ValueError):
        return None, ('No verified Git HEAD available; source_sha256 identifies exact '
                      'source files; rerun from the committed checkout to register source_commit')


def run():
    system = build_system()
    ins = system['instance']
    counts = (len(ins.V), len(system['edges']), len(ins.A_r), len(ins.S), len(ins.T),
              len(system['K']), len(system['base']), len(system['C8']), len(system['C6']))
    if counts != (24, 48, 96, 6, 6, 4, 76, 36, 1):
        raise AssertionError('witness structure differs from Astra description')
    if system['c6_incomplete']:
        raise AssertionError('C6 generation truncated')
    cases = {'COMP_K': [], 'COMP_K_FCR': ['FCR'],
             'COMP_K_C8': ['C8'], 'COMP_K_C8_FCR': ['C8','FCR'],
             'COMP_K_C6_C8': ['C6', 'C8'],
             'COMP_K_C6_C8_FCR': ['C6', 'C8', 'FCR']}
    certs = {}
    for label, families in cases.items():
        rows = system['base'] + [r for family in families for r in system[family]]
        certs[label] = solve_exact_certificate(system['compiled'], rows)
        recheck_saved(system['compiled'], rows, certs[label])
    def value(label): return F(certs[label]['objective'])
    expected = {'COMP_K': F(1), 'COMP_K_FCR': F(7,5),
                'COMP_K_C8': F(11,10), 'COMP_K_C8_FCR': F(7,5),
                'COMP_K_C6_C8': F(47,30), 'COMP_K_C6_C8_FCR': F(17,10)}
    for label, expected_value in expected.items():
        if value(label) != expected_value:
            raise AssertionError(f'{label}: {value(label)} != {expected_value}')
    if not (value('COMP_K_C8') < value('COMP_K_FCR') and
            value('COMP_K_C6_C8') < value('COMP_K_C6_C8_FCR')):
        raise AssertionError('strict marginal LP strengthening not reproduced')
    base_point = tuple(map(F, certs['COMP_K']['primal']))
    violation = [str(r.rhs-row_value(r, base_point)) for r in system['FCR']]
    if not any(F(v)>0 for v in violation):
        raise AssertionError('COMP+K primal point does not violate FC-R')
    physical = physical_report(system)
    astra_c8_point = declared_c8_counterexample(system)
    graph = {'V': list(ins.V), 'S': list(ins.S), 'T': list(ins.T), 'r': ins.r,
             'edges': [list(p) for p in sorted(system['edges'])],
             'A_r': [list(a) for a in ins.A_r]}
    graph_hash = hashlib.sha256(json.dumps(graph, sort_keys=True,separators=(',',':')).encode()).hexdigest()
    source_sha256 = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in [Path(__file__), AS02_DIR/'as02_model_a.py',
                               ROOT/'experiments/cuts/cuts.py',
                               ROOT/'experiments/cuts/independent_validator.py']}
    source_commit, source_commit_note = source_revision()
    return {'schema_version': 2, 'status': 'EXACT_CERTIFIED', 'kind': 'SYNTHETIC_ONLY',
            'source_commit': source_commit, 'source_commit_note': source_commit_note,
            'source_sha256': source_sha256,
            'graph_sha256': graph_hash, 'graph': graph, 'K': [sorted(x) for x in system['K']],
            'C6': [{'terms': [[key[1], int(k)] for j,k in r.terms for key,idx in system['compiled'].columns.items()
                    if key[0]=='y' and idx==j], 'rhs': str(r.rhs)} for r in system['C6']],
            'counts': {'vertices': len(ins.V), 'physical_edges': len(system['edges']),
                       'reach_arcs': len(ins.A_r), 'COMP_K_rows': len(system['base']),
                       'K': len(system['K']), 'C6': len(system['C6']), 'C8': len(system['C8']),
                       'FCR': len(system['FCR'])},
            'physical': physical, 'declared_c8_point': astra_c8_point,
            'base_primal_fcr_deficits': violation,
            'cases': certs,
            'comparison': {'K_to_K_FCR': str(value('COMP_K_FCR')-value('COMP_K')),
                           'K_C8_to_K_C8_FCR': str(value('COMP_K_C8_FCR')-value('COMP_K_C8')),
                           'K_C6_C8_to_FCR': str(value('COMP_K_C6_C8_FCR')-value('COMP_K_C6_C8'))}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=None)
    args = parser.parse_args()
    result = run()
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)+'\n', encoding='utf-8')
    print(json.dumps({'status': result['status'], 'graph_sha256':result['graph_sha256'],
                      'objectives': {k:v['objective'] for k,v in result['cases'].items()},
                      'physical':result['physical']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
