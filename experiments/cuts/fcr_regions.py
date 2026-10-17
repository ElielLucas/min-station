"""AS24: complete eligible singletons, bounded deterministic larger regions.

Heuristics generate candidates only; a complete search over all regions is
neither claimed nor attempted.  No cap is applied to the singleton generator.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from .fcr_rows import _graph, region_excess


@dataclass(frozen=True)
class RegionPlan:
    singletons: tuple[tuple[str, ...], ...]
    larger: tuple[tuple[str, ...], ...]
    larger_generated: int
    larger_discarded: int
    larger_limit: int

    @property
    def larger_coverage(self) -> str:
        return 'SELECTED_HEURISTIC_ONLY'


def choose_regions(instance, *, max_larger: int=12, include_larger: bool=True) -> RegionPlan:
    if not isinstance(max_larger, int) or max_larger < 0:
        raise ValueError('invalid regional cap')
    vertices, arcs = _graph(instance)
    singles = tuple((v,) for v in sorted(vertices)
                    if region_excess(instance, (v,), 'origin') > 0 or
                       region_excess(instance, (v,), 'destination') > 0)
    if not include_larger:
        return RegionPlan(singles, (), 0, 0, max_larger)
    S, T = set(instance.S), set(instance.T)
    terminal_origins = sorted(S - T)
    terminal_destinations = sorted(T - S)
    adj = {v: set() for v in vertices}
    for u, v in arcs:
        adj[u].add(v)
        adj[v].add(u)
    potential = set()
    # Small connected regions in H (the reachability digraph, NOT physical G).
    for u, v in arcs:
        if u != v:
            potential.add(tuple(sorted((u,v))))
    # Pairs of same-sign terminals sharing a neighbor can create demand >=2
    # even without adjacency; these detect coupling missed by singletons.
    for items in (terminal_origins, terminal_destinations):
        for u, v in combinations(items, 2):
            if adj[u].intersection(adj[v]):
                potential.add((u,v))
    valid = sorted((R for R in potential if
                    region_excess(instance, R, 'origin') > 0 or
                    region_excess(instance, R, 'destination') > 0),
                   key=lambda r: (-abs(len(S.intersection(r))-len(T.intersection(r))),r))
    chosen = tuple(valid[:max_larger])
    return RegionPlan(singles, chosen, len(valid), len(valid)-len(chosen), max_larger)
