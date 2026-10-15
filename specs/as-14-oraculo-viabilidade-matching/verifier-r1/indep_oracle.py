"""Verifier-owned physical oracle for AS14 review (independent of independent_validator).

Reachability: a robot from s reaches t iff t == s and s in T (stay), or there is a
sequence s=x0, x1..xk=t with x1..x(k-1) in C and unit-graph distance d(xi,xi+1) <= r.
Matching: brute force over permutations of T (no Kuhn). Hall: brute force over subsets.
"""
from collections import deque
from itertools import combinations, permutations


def bfs_dist(V, edges):
    nb = {v: set() for v in V}
    for u, w in edges:
        nb[u].add(w)
        nb[w].add(u)
    dist = {}
    for s in V:
        d = {s: 0}
        q = deque([s])
        while q:
            u = q.popleft()
            for w in nb[u]:
                if w not in d:
                    d[w] = d[u] + 1
                    q.append(w)
        dist[s] = d
    return dist


def reach_sets(V, S, T, edges, r, C):
    dist = bfs_dist(V, edges)
    C = set(C)
    Tset = set(T)
    out = {}
    for s in S:
        got = {s} & Tset
        # closure over stations reachable via legs of length <= r (never through s itself as a relay
        # unless s in C; starting at s is always with full battery)
        frontier = [s]
        seen = {s}
        while frontier:
            u = frontier.pop()
            for w, d in dist[u].items():
                if w == u or d > r:
                    continue
                if w in Tset:
                    got.add(w)
                if w in C and w not in seen:
                    seen.add(w)
                    frontier.append(w)
        out[s] = got
    return out


def nu_brute(S, T, reach):
    S = list(S)
    best = 0
    for perm in permutations(list(T)):
        best = max(best, sum(1 for s, t in zip(S, perm) if t in reach[s]))
        if best == len(S):
            break
    return best


def max_deficiency(S, reach):
    best = 0
    for k in range(len(S) + 1):
        for U in combinations(S, k):
            N = set().union(*(reach[s] for s in U)) if U else set()
            best = max(best, len(U) - len(N))
    return best


def viable(V, S, T, edges, r, C):
    reach = reach_sets(V, S, T, edges, r, C)
    return nu_brute(S, T, reach) == len(S)
