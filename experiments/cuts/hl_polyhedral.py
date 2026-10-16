"""AS22: certified bounded separation of general nonnegative HL inequalities.

For R subset V, F=V minus R, classify EVERY pattern A subset R for the
physical station set F union A. The resulting monotone finite set Phi_R
contains the restriction of every globally feasible integer solution.

A candidate alpha is obtained by a *numerical* LP, then rationalized;
beta=min_{A in Phi_R} alpha(A) is recomputed EXACTLY with Fractions. Thus
numerical separation proposes coefficients but cannot certify validity.
UNKNOWN, any incomplete classification, caps or budget => abstain.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from typing import Mapping

from h2_oracle import MatchingOracle, PhysicalInstance
from h2_oracle_schema import Status, canonical_json, digest, order_vertices, vertex_key
from h2_separator import _certificate_hash
from hl_local import HLCut


@dataclass(frozen=True)
class PolyOptions:
    max_support_size: int = 8
    max_supports: int = 4
    max_patterns_per_support: int = 256
    max_oracle_calls: int = 480
    max_denominator: int = 128
    total_budget_s: float = 24.
    per_support_budget_s: float = 8.
    min_violation: float = 1e-6

    def __post_init__(self):
        for name in ('max_support_size', 'max_supports', 'max_patterns_per_support',
                     'max_oracle_calls', 'max_denominator'):
            value = getattr(self, name)
            if type(value) is not int or value < (1 if name in ('max_support_size', 'max_denominator') else 0):
                raise ValueError(f'invalid {name}')
        for name in ('total_budget_s', 'per_support_budget_s', 'min_violation'):
            value = getattr(self, name)
            if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
                raise ValueError(f'invalid {name}')


@dataclass(frozen=True)
class PolyReport:
    instance_sha256: str
    cuts: tuple[HLCut, ...]
    records: tuple[dict, ...]
    oracle_calls: int
    elapsed_wall_s: float
    status: str

    def to_dict(self):
        return {
            'schema_version': 'AS22-HL-POLY-v1', 'stage': 'AS22',
            'method': 'complete_monotone_projection_rational_certificate',
            'instance_sha256': self.instance_sha256,
            'status': self.status, 'oracle_calls': self.oracle_calls,
            'elapsed_wall_s': self.elapsed_wall_s, 'cuts_emitted': len(self.cuts),
            'cuts': [cut.to_dict() for cut in self.cuts], 'records': list(self.records),
        }

    def save_new(self, path: str | Path):
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open('x', encoding='utf-8') as out:
            out.write(canonical_json(self.to_dict()) + '\n')


def _find_rational_cut(R, y_star, feasible_masks, *, max_denominator, min_violation):
    """Only the final exact rational beta certifies a numerically proposed row."""
    from scipy.optimize import linprog

    n = len(R)
    viable = sorted(set(feasible_masks))
    if not viable:
        return None, 'EMPTY_FEASIBLE_PROJECTION'
    # With monotone physical feasibility, nonnegative normals suffice for
    # separating a point in the unit cube from the upward-closed hull.
    # max t : alpha.(z - y*) >= t for all z in Phi_R, sum(alpha)=1.
    lp = linprog(c=[0.] * n + [-1.],
                 A_ub=[[float(y_star[v]) - float((mask >> i) & 1) for i, v in enumerate(R)] + [1.]
                       for mask in viable],
                 b_ub=[0.] * len(viable),
                 A_eq=[[1.] * n + [0.]], b_eq=[1.],
                 bounds=[(0., 1.)] * n + [(0., None)],
                 method='highs')
    if lp.status == 2:
        return None, 'NO_NUMERICAL_SEPARATION'
    if lp.status != 0 or lp.x is None or not all(math.isfinite(float(x)) for x in lp.x):
        return None, f'NUMERICAL_SEPARATION_STATUS_{lp.status}'
    if lp.x[-1] <= min_violation:
        return None, 'NO_NUMERICAL_SEPARATION'
    alpha = tuple(Fraction(str(max(0., float(value)))).limit_denominator(max_denominator)
                  for value in lp.x[:n])
    if not any(alpha):
        return None, 'RATIONALIZED_ZERO_NORMAL'
    beta = min(sum((alpha[i] for i in range(n) if mask & (1 << i)), Fraction(0))
               for mask in viable)
    lhs = math.fsum(float(alpha[i]) * y_star[v] for i, v in enumerate(R))
    gap = float(beta) - lhs
    if beta <= 0 or not math.isfinite(gap) or gap <= min_violation:
        return None, 'RATIONALIZATION_LOST_VIOLATION'
    # Never take beta from the floating LP; it comes exclusively from all
    # physically certified viable patterns with exact rational arithmetic.
    return (alpha, beta, gap), 'EXACT_FINITE_PROJECTION'


def separate_hl_poly(instance: PhysicalInstance, y_star: Mapping, *, supports,
                     options: PolyOptions | None = None,
                     oracle: MatchingOracle | None = None) -> PolyReport:
    if not isinstance(instance, PhysicalInstance):
        raise TypeError('PhysicalInstance required')
    opt = options or PolyOptions()
    V = order_vertices(instance.V)
    if not isinstance(y_star, Mapping) or set(y_star) != set(V) or len(y_star) != len(V):
        raise ValueError('y_star must match all physical vertices')
    if any(type(y_star[v]) not in (int, float) or not math.isfinite(y_star[v])
           or not 0 <= y_star[v] <= 1 for v in V):
        raise ValueError('invalid LP point')
    proposals = []
    seen = set()
    for raw in supports:
        R = order_vertices(raw)
        if not R or len(R) != len(set(raw)) or not set(R) <= set(V):
            raise ValueError('invalid support')
        if R not in seen:
            seen.add(R)
            proposals.append(R)

    engine = oracle if oracle is not None else MatchingOracle()
    clock = engine.clock
    begin = clock()
    initial_calls = engine.calls
    records, cuts = [], []
    partial = False
    for R in proposals[:opt.max_supports]:
        if clock() - begin >= opt.total_budget_s or engine.calls - initial_calls >= opt.max_oracle_calls:
            partial = True
            break
        started = clock()
        before = engine.calls
        n = len(R)
        record = {'support': list(R), 'size': n, 'patterns_total': 1 << n,
                  'separation_family': 'GENERAL_NONNEGATIVE_ALPHA',
                  'classification_complete': False}

        def finish(status, reason, **fields):
            record.update(status=status, reason=reason,
                          oracle_calls=engine.calls-before,
                          elapsed_wall_s=max(0., clock()-started), **fields)
            records.append(record)

        if n > opt.max_support_size:
            partial = True
            finish('SKIPPED_SIZE', 'SUPPORT_EXCEEDS_CAP')
            continue
        if 1 << n > opt.max_patterns_per_support:
            partial = True
            finish('SKIPPED_PATTERN_CAP', 'COMPLETE_PROJECTION_EXCEEDS_CAP')
            continue
        F = order_vertices(set(V)-set(R))
        examined = 0
        inferred = 0
        feasible_masks = []
        viable_witnesses = {}
        certificates = []
        stop = None
        for j in range(n+1):
            for bits in combinations(range(n), j):
                mask = sum(1 << b for b in bits)
                # A VIABLE smaller station set certifies every larger pattern
                # by physical station-set monotonicity (no second oracle call).
                inferred_from = next((w for w in sorted(viable_witnesses)
                                      if (mask & w) == w), None)
                if inferred_from is not None:
                    feasible_masks.append(mask)
                    inferred += 1
                    certificates.append([mask, 'VIABLE_INFERRED', inferred_from,
                                         viable_witnesses[inferred_from]])
                    continue
                remaining = min(opt.total_budget_s-(clock()-begin),
                                opt.per_support_budget_s-(clock()-started))
                if engine.calls-initial_calls >= opt.max_oracle_calls or remaining <= 0:
                    stop = 'ORACLE_OR_WALL_BUDGET'
                    break
                A = tuple(R[i] for i in bits)
                result = engine.check(instance, order_vertices((*F, *A)), budget_s=remaining)
                examined += 1
                if result.status is Status.UNKNOWN:
                    stop = 'UNKNOWN_PHYSICAL_ORACLE'
                    break
                certificate_hash = _certificate_hash(result)
                certificates.append([mask, result.status.value, certificate_hash])
                if result.status is Status.VIABLE:
                    feasible_masks.append(mask)
                    viable_witnesses[mask] = certificate_hash
            if stop:
                break
        if stop:
            partial = True
            finish('ABSTAIN', stop, patterns_examined=examined, patterns_inferred=inferred)
            continue
        if examined + inferred != 1 << n:
            partial = True
            finish('ABSTAIN', 'INCOMPLETE_PROJECTION', patterns_examined=examined,
                   patterns_inferred=inferred)
            continue
        certificate_sha = digest({'schema':'AS22-COMPLETE-PROJECTION-v1',
                                  'instance':instance.fingerprint,
                                  'support':[list(vertex_key(v)) for v in R],
                                  'classification':certificates})
        base = {'classification_complete': True, 'patterns_examined': examined,
                'patterns_inferred': inferred, 'patterns_viable': len(feasible_masks),
                'patterns_infeasible': (1 << n)-len(feasible_masks),
                'certificate_sha256':certificate_sha,
                'classification_evidence': certificates}
        if not feasible_masks:
            partial = True
            finish('ABSTAIN', 'EMPTY_FEASIBLE_PROJECTION', **base)
            continue
        candidate, reason = _find_rational_cut(R, y_star, feasible_masks,
                        max_denominator=opt.max_denominator, min_violation=opt.min_violation)
        if candidate is None:
            finish('NO_CUT', reason, **base)
            continue
        alpha, beta, gap = candidate
        coefs = tuple(zip(R, alpha))
        cut_sha = digest({'instance': instance.fingerprint,
                    'coefs': [[list(vertex_key(v)), str(a)] for v,a in coefs],
                    'rhs': str(beta),
                    'support': [list(vertex_key(v)) for v in R]})
        cuts.append(HLCut(R, coefs, beta, gap, certificate_sha, cut_sha,
                          engine.calls-before, clock()-started))
        finish('CUT', reason, rhs=str(beta),
               coefficients=[str(a) for a in alpha], violation=gap, **base)
    if len(proposals) > opt.max_supports or len(records) < min(opt.max_supports,len(proposals)):
        partial = True
    status = 'PARTIAL_BUDGET' if partial else ('CUTS_FOUND' if cuts else 'NO_CUTS')
    return PolyReport(instance.fingerprint, tuple(cuts), tuple(records),
                      engine.calls-initial_calls, max(0.,clock()-begin), status)
