"""AS-05: 24 contraprovas numéricas pequenas; não é revisão independente.

Depende de SciPy/HiGHS para LP/MIP. Não usa Gurobi, não altera resultados.
"""
from __future__ import annotations

import itertools
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / 'experiments/alternative-formulations')]

from as02_model_a import Instance, compile_a, compile_u  # noqa: E402
from as02_solve import solve_scipy  # noqa: E402
from experiments.cuts.independent_validator import opt_por_enumeracao  # noqa: E402


def probe() -> dict:
    rng = random.Random(20261011)
    results = []
    for q in range(24):
        n = 5 + q % 3
        vertices = tuple(f'v{i}' for i in range(n))
        edges = {(vertices[i], vertices[i + 1]) for i in range(n - 1)}
        for u, v in itertools.combinations(vertices, 2):
            if rng.random() < 0.32:
                edges.add((u, v))
        adj = {v: [] for v in vertices}
        for u, v in edges:
            adj[u].append((v, 1))
            adj[v].append((u, 1))
        r = 1 + q % 2
        arcs = []
        for u in vertices:
            visited, frontier = {u}, {u}
            for _ in range(r):
                frontier = {v for x in frontier for v, _ in adj[x]}
                visited.update(frontier)
            arcs.extend((u, v) for v in visited if v != u)
        m = 3
        origins = tuple(sorted(rng.sample(vertices, m)))
        destinations = tuple(sorted(rng.sample(vertices, m)))
        instance = Instance(vertices, origins, destinations, tuple(sorted(arcs)), r)
        partitions = [(origins,), (origins[:2], origins[2:]),
                      tuple((x,) for x in origins)]
        u_lp = solve_scipy(compile_u(instance, relax=True))
        a_lps = [solve_scipy(compile_a(instance, p, relax=True)) for p in partitions]
        a_mip = solve_scipy(compile_a(instance, partitions[1], relax=False))
        physical_opt = opt_por_enumeracao(origins, destinations, vertices, adj, r)
        values = [u_lp.objective] + [s.objective for s in a_lps]
        ok = (all(s.status == 'OPTIMAL' for s in (u_lp, *a_lps, a_mip))
              and abs(values[0] - values[1]) < 1e-6
              and values[1] <= values[2] + 1e-6
              and values[2] <= values[3] + 1e-6
              and a_mip.objective == physical_opt)
        results.append({'index': q, 'lp': values,
                        'mip': a_mip.objective, 'physical_opt': physical_opt,
                        'ok': ok})
    return {'n_cases': len(results),
            'passed': sum(x['ok'] for x in results),
            'failures': [x for x in results if not x['ok']]}


if __name__ == '__main__':
    result = probe()
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result['passed'] == result['n_cases'] else 1)
