#!/usr/bin/env python3
"""AS08 T2a — verificação reprodutível B enumerada × A unitária × COMP(+K).

Exemplo: PYTHONPATH=. poetry run python experiments/alternative-formulations/run_as08_t2a.py \
  --backend gurobi --output-dir results/benchmark/as08-t2a-exact-001

O conjunto de testes é sintético de desenvolvimento, NÃO benchmark/promoção.
Amostras finitas não substituem a prova das projeções LP de T1.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import random
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from as02_model_a import Instance, compile_a, compile_u, prepare_K
from as02_solve import solve
from as08_b_exact import PathEnumerationLimit, compile_b
from experiments.cuts.independent_validator import viavel

VERSION = 'as08-t2a-v1'


@dataclass(frozen=True)
class Fixture:
    name: str
    edges: tuple[tuple[str, str], ...]
    S: tuple[str, ...]
    T: tuple[str, ...]
    r: int = 1
    isolated: tuple[str, ...] = ()


FIXTURES = (
    Fixture('e1-b4-star', (('a','c'),('b','c'),('c','d')), ('a','b'), ('c','d')),
    Fixture('e2-disaggregated-hub', (('s1','h'),('s2','h'),('h','t1'),('h','t2'),('s1','t2')), ('s1','s2'), ('t1','t2')),
    Fixture('e3-lp-gap', (('a','c'),('b','c'),('a','x'),('b','x'),('x','d')), ('a','b'), ('c','d')),
    Fixture('e4-stay-only', (('s','u'),), ('s',), ('s',)),
    Fixture('e5-origin-destination-swap', (('a','v'),('v','b')), ('a','v'), ('v','b')),
    Fixture('one-arc-direct', (('s','t'),), ('s',), ('t',)),
    Fixture('relay-line', (('a','b'),('b','c'),('c','d')), ('a','b'), ('c','d')),
    Fixture('autonomy-two', (('a','b'),('b','c'),('c','d')), ('a','d'), ('b','c'), 2),
    Fixture('infeasible-components', (('a','b'),('c','d')), ('a','b'), ('c','d')),
    Fixture('overlap-triangle', (('a','b'),('b','c'),('a','c')), ('a','b'), ('b','c')),
)


def build_fixture(fixture: Fixture) -> tuple[Instance, dict]:
    vertices = tuple(sorted({v for edge in fixture.edges for v in edge}
                            | set(fixture.S) | set(fixture.T) | set(fixture.isolated)))
    adj: dict[str, list[tuple[str, int]]] = {v: [] for v in vertices}
    for u, v in fixture.edges:
        if u == v:
            raise ValueError('aresta com laço')
        adj[u].append((v, 1))
        adj[v].append((u, 1))
    for v in adj:
        adj[v].sort()
    reach = []
    for s in vertices:
        seen = {s}
        frontier = {s}
        for _ in range(fixture.r):
            frontier = {w for u in frontier for w, _ in adj[u]} - seen
            seen |= frontier
        reach.extend((s, t) for t in sorted(seen - {s}))
    return Instance(vertices, fixture.S, fixture.T, tuple(reach), fixture.r), adj


def digest(payload) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(',', ':'),
                                    ensure_ascii=False).encode('utf-8')).hexdigest()


def y_vectors(vertices: tuple[str, ...], *, max_fractional: int, seed: int):
    """Inclui extremos relevantes e uma amostra determinística do interior.

    Não proclama equivalência universal com base nessa amostragem finita.
    """
    rng = random.Random(seed)
    binary = tuple(itertools.product((0., 1.), repeat=len(vertices)))
    choices = {(0.5,) * len(vertices), (0.,) * len(vertices), (1.,) * len(vertices)}
    for v in range(len(vertices)):
        choices.add(tuple(.5 if i == v else 0. for i in range(len(vertices))))
        choices.add(tuple(.5 if i == v else 1. for i in range(len(vertices))))
    while len(choices) < min(3 ** len(vertices), max_fractional + 2 ** len(vertices)):
        choices.add(tuple(rng.choice((0., .5, 1.)) for _ in vertices))
    fractional = [vec for vec in sorted(choices) if any(value == .5 for value in vec)]
    return binary, tuple(fractional[:max_fractional])


def run_case(fixture: Fixture, *, backend: str, seconds: float,
             max_vertices: int, max_paths: int, fractionals: int, seed: int) -> dict:
    instance, adj = build_fixture(fixture)
    case = {'name': fixture.name, 'instance': asdict(instance),
            'case_sha256': digest({'fixture': asdict(fixture), 'instance': asdict(instance)}),
            'status': 'INCOMPLETE', 'checks': {}, 'counterexamples': []}
    if len(instance.V) > max_vertices:
        case['reason'] = 'PATH_ENUM_LIMIT_VERTICES'
        return case
    try:
        paths_no_k = None
        modes = {}
        for suffix, with_k in (('no_k', False), ('with_k', True)):
            K = prepare_K(instance, adj, instance.r) if with_k else ()
            b, paths = compile_b(instance, K, relax=True,
                                 max_vertices=max_vertices, max_paths=max_paths)
            a = compile_a(instance, ((s,) for s in instance.S), K, relax=True)
            u = compile_u(instance, K, relax=True)
            modes[suffix] = {'K': K, 'B': b, 'A': a, 'U': u, 'paths': paths}
            if paths_no_k is None:
                paths_no_k = paths
        assert paths_no_k is not None
        case['path_count'] = paths_no_k.count
        case['per_source_paths'] = {s: len(ps) for s, ps in paths_no_k.by_source.items()}
        case['model_sizes'] = {mode: {name: {'variables': len(entry[name].variables),
                                            'rows': len(entry[name].equations),
                                            'nnz': entry[name].n_nonzeros}
                                     for name in ('B', 'A', 'U')}
                               for mode, entry in modes.items()}
        case['K_count'] = len(modes['with_k']['K'])
        case['K_sha256'] = digest([sorted(k) for k in modes['with_k']['K']])
        all_good = True
        for mode, entry in modes.items():
            objectives = {name: solve(entry[name], backend=backend, time_limit=seconds)
                          for name in ('B', 'A', 'U')}
            case['checks'][mode] = {'LP': {name: asdict(out) for name, out in objectives.items()},
                                    'fixed_y_binary': 0, 'fixed_y_fractional': 0,
                                    'physical_oracle': 0, 'mip_optimum': None}
            out_b, out_a, out_u = (objectives[k] for k in ('B', 'A', 'U'))
            if any(o.status not in ('OPTIMAL', 'INFEASIBLE') for o in objectives.values()):
                case['reason'] = 'SOLVER_UNRESOLVED_LP'
                return case
            if out_b.status != out_a.status or (
                out_b.status == 'OPTIMAL' and (
                    abs(out_b.objective-out_a.objective) > 1e-6 or
                    out_u.status != 'OPTIMAL' or out_b.objective + 1e-6 < out_u.objective)):
                all_good = False
                case['counterexamples'].append({'kind': 'LP_COMPARISON', 'mode': mode,
                                                'objectives': case['checks'][mode]['LP']})
            binary, fractional = y_vectors(instance.V, max_fractional=fractionals,
                                           seed=seed + int(mode == 'with_k'))
            expected_opt = None
            for values in binary:
                y = dict(zip(instance.V, values))
                physical = viavel(instance.S, instance.T, instance.V, adj, instance.r,
                                  {v for v, val in y.items() if val == 1})
                if physical:
                    expected_opt = min(expected_opt, int(sum(values))) if expected_opt is not None else int(sum(values))
                result_b = solve(entry['B'], y, backend=backend, time_limit=seconds)
                result_a = solve(entry['A'], y, backend=backend, time_limit=seconds)
                if result_b.status not in ('OPTIMAL', 'INFEASIBLE') or result_a.status not in ('OPTIMAL', 'INFEASIBLE'):
                    case['reason'] = 'SOLVER_UNRESOLVED_BINARY'
                    return case
                valid_b, valid_a = result_b.status == 'OPTIMAL', result_a.status == 'OPTIMAL'
                if valid_b != physical or valid_a != physical:
                    all_good = False
                    case['counterexamples'].append({'kind': 'PHYSICAL_DISAGREEMENT', 'mode': mode,
                                                    'y': y, 'physical': physical,
                                                    'B': result_b.status, 'A': result_a.status})
                case['checks'][mode]['fixed_y_binary'] += 1
                case['checks'][mode]['physical_oracle'] += 1
            case['checks'][mode]['physical_optimum'] = expected_opt
            mip_b, _ = compile_b(instance, entry['K'], relax=False,
                                 max_vertices=max_vertices, max_paths=max_paths)
            mip_result = solve(mip_b, backend=backend, time_limit=seconds)
            case['checks'][mode]['mip_optimum'] = asdict(mip_result)
            if ((mip_result.status == 'OPTIMAL') != (expected_opt is not None) or
                (expected_opt is not None and mip_result.objective is not None and
                 abs(mip_result.objective - expected_opt) > 1e-6)):
                all_good = False
                case['counterexamples'].append({'kind': 'MIP_PHYSICAL_DISAGREEMENT', 'mode': mode,
                                                'expected': expected_opt, 'got': asdict(mip_result)})
            if mip_result.status not in ('OPTIMAL', 'INFEASIBLE'):
                case['reason'] = 'SOLVER_UNRESOLVED_MIP'
                return case
            for values in fractional:
                y = dict(zip(instance.V, values))
                b_result = solve(entry['B'], y, backend=backend, time_limit=seconds)
                a_result = solve(entry['A'], y, backend=backend, time_limit=seconds)
                if any(o.status not in ('OPTIMAL', 'INFEASIBLE') for o in (b_result,a_result)):
                    case['reason'] = 'SOLVER_UNRESOLVED_FRACTIONAL'
                    return case
                if b_result.status != a_result.status:
                    all_good = False
                    case['counterexamples'].append({'kind': 'FIBER_DISAGREEMENT', 'mode': mode,
                                                    'y': y, 'B': b_result.status, 'A': a_result.status})
                case['checks'][mode]['fixed_y_fractional'] += 1
        case['status'] = 'PASS' if all_good else 'FAIL'
        return case
    except PathEnumerationLimit as exc:
        case['reason'] = 'PATH_ENUM_LIMIT'
        case['detail'] = str(exc)
        return case
    except (ImportError, ModuleNotFoundError) as exc:
        case['reason'] = 'SOLVER_UNAVAILABLE'
        case['detail'] = str(exc)
        return case
    except Exception as exc:
        case['reason'] = 'EXCEPTION'
        case['detail'] = f'{type(exc).__name__}: {exc}'
        return case


def write_results(output_dir: Path, payload: dict) -> None:
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError(f'output não vazio: {output_dir} (não sobrescrever evidências)')
    output_dir.mkdir(parents=True, exist_ok=True)
    content = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + '\n'
    (output_dir / 'results.json').write_text(content, encoding='utf-8')
    sha = hashlib.sha256(content.encode('utf-8')).hexdigest()
    (output_dir / 'results.sha256').write_text(sha + '\n', encoding='utf-8')
    lines = ['# AS-08/T2a — validação exata de B enumerada', '',
             '**Natureza:** controle exploratório de desenvolvimento, não certifica a prova de T1.',
             f'**Backend:** `{payload["backend"]}`. **Versão:** `{VERSION}`.',
             f'**Decisão:** `{payload["decision"]}`.', '',
             '| Caso | Caminhos | Sem K | Com K |', '|---|---:|---|---|']
    for row in payload['cases']:
        state = row['status']
        lines.append(f'| {row["name"]} | {row.get("path_count", "—")} | '
                     f'{row.get("checks", {}).get("no_k", {}).get("LP", {}).get("B", {}).get("objective", "—")} | '
                     f'{row.get("checks", {}).get("with_k", {}).get("LP", {}).get("B", {}).get("objective", "—")} |')
        if state != 'PASS':
            lines.append(f'\n**{row["name"]}:** `{state}` — {row.get("reason", row.get("counterexamples", []))}')
    lines.extend(['', 'Todos os resultados de LP são numéricos; amostras finitas de fibras y não provam equivalência universal.',
                  'B completo por enumeração, não RMP nem bound de column generation.',
                  'K foi preparado pelas famílias C1+C2+C4-DM do projeto.',
                  'Não substitui revisão matemática independente de T1.'])
    (output_dir / 'analysis.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')


def verify(output_dir: Path) -> dict:
    content = (output_dir / 'results.json').read_bytes()
    claimed = (output_dir / 'results.sha256').read_text(encoding='utf-8').strip()
    if hashlib.sha256(content).hexdigest() != claimed:
        raise ValueError('INTEGRITY_ERROR: SHA256 não confere')
    payload = json.loads(content)
    if payload.get('schema') != VERSION or payload.get('decision') not in ('PASS_EXPLORATORY', 'INCOMPLETE', 'FAIL'):
        raise ValueError('INTEGRITY_ERROR: schema/decisão inválidos')
    if [c.get('name') for c in payload.get('cases', [])] != [f.name for f in FIXTURES]:
        raise ValueError('INTEGRITY_ERROR: faltam/duplicam casos ou ordem incorreta')
    expected = ('PASS_EXPLORATORY' if all(c['status']=='PASS' for c in payload['cases'])
                else 'FAIL' if any(c['status']=='FAIL' for c in payload['cases']) else 'INCOMPLETE')
    if expected != payload['decision']:
        raise ValueError('INTEGRITY_ERROR: decisão incompatível')
    return payload


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--backend', choices=('gurobi', 'scipy-highs'), default='gurobi')
    parser.add_argument('--output-dir', type=Path, default=Path('results/benchmark/as08-t2a-exact-001'))
    parser.add_argument('--verify', action='store_true')
    parser.add_argument('--max-vertices', type=int, default=9)
    parser.add_argument('--max-paths', type=int, default=20000)
    parser.add_argument('--fractional-samples', type=int, default=12)
    parser.add_argument('--time-limit', type=float, default=30)
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args(argv)
    if args.verify:
        result = verify(args.output_dir)
        print(f'AS08_T2A_VERIFIED cases={len(result["cases"])} decision={result["decision"]}')
        return 0
    if args.fractional_samples < 1 or args.time_limit <= 0:
        parser.error('amostras e limite de tempo devem ser positivos')
    cases = [run_case(fixture, backend=args.backend, seconds=args.time_limit,
                      max_vertices=args.max_vertices, max_paths=args.max_paths,
                      fractionals=args.fractional_samples, seed=args.seed)
             for fixture in FIXTURES]
    decision = ('PASS_EXPLORATORY' if all(c['status'] == 'PASS' for c in cases)
                else 'FAIL' if any(c['status'] == 'FAIL' for c in cases) else 'INCOMPLETE')
    payload = {'schema': VERSION, 'backend': args.backend,
               'parameters': {'max_vertices': args.max_vertices, 'max_paths': args.max_paths,
                              'fractional_samples': args.fractional_samples, 'seed': args.seed,
                              'time_limit': args.time_limit},
               'cases': cases, 'decision': decision,
               'scientific_gate': 'PENDING_INDEPENDENT_REVIEW'}
    write_results(args.output_dir, payload)
    print(f'AS08_T2A_COMPLETED cases={len(cases)} decision={decision}')
    for case in cases:
        print(f'  {case["name"]}: {case["status"]} paths={case.get("path_count", "—")} '
              f'{case.get("reason", "")}')
    return 0 if decision == 'PASS_EXPLORATORY' else 2


if __name__ == '__main__':
    raise SystemExit(main())
