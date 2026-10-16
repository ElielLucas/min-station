"""AS19: bounded, certified local HL cardinality separation (independent of H2).

Enumerate the complete binary projection Phi_R for k<=max_support_size.
Only physical VIABLE/INFEASIBLE oracle certificates are conclusive. Any
UNKNOWN, exhausted budget or incomplete enumeration causes abstention.
No LP solver or historical COMP/K code is modified here.
"""
from __future__ import annotations

import math
import time
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from typing import Mapping

from h2_oracle import MatchingOracle, PhysicalInstance
from h2_oracle_schema import Status, canonical_json, digest, order_vertices, vertex_key
from h2_separator import _certificate_hash


@dataclass(frozen=True)
class HLOptions:
    max_support_size: int = 8
    max_oracle_calls: int = 300
    max_supports: int = 12
    total_budget_s: float = 15.0
    per_support_budget_s: float = 5.0
    min_violation: float = 1e-7
    max_denominator: int = 1000

    def __post_init__(self):
        for name in ('max_support_size', 'max_oracle_calls', 'max_supports', 'max_denominator'):
            value = getattr(self, name)
            if type(value) is not int or value < (1 if name in ('max_support_size', 'max_denominator') else 0):
                raise ValueError(f'invalid {name}')
        for name in ('total_budget_s', 'per_support_budget_s', 'min_violation'):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value) or value < 0:
                raise ValueError(f'invalid {name}')


@dataclass(frozen=True)
class HLCut:
    support: tuple
    coefficients: tuple[tuple[object, Fraction], ...]
    rhs: Fraction
    violation: float
    certificate_sha256: str
    cut_hash: str
    oracle_calls: int
    elapsed_wall_s: float

    def to_dict(self):
        return {
            'support': list(self.support),
            'coefficients': [{'vertex': v, 'value': str(a)} for v, a in self.coefficients],
            'rhs': str(self.rhs), 'violation': self.violation,
            'certificate_sha256': self.certificate_sha256,
            'cut_hash': self.cut_hash, 'oracle_calls': self.oracle_calls,
            'elapsed_wall_s': self.elapsed_wall_s,
        }


@dataclass(frozen=True)
class HLReport:
    instance_sha256: str
    cuts: tuple[HLCut, ...]
    records: tuple[dict, ...]
    oracle_calls: int
    elapsed_wall_s: float
    status: str

    def to_dict(self):
        return {
            'schema_version': 'AS19-HL-LOCAL-v1', 'stage': 'AS19',
            'instance_sha256': self.instance_sha256,
            'status': self.status, 'oracle_calls': self.oracle_calls,
            'elapsed_wall_s': self.elapsed_wall_s,
            'cuts_emitted': len(self.cuts),
            'cuts': [c.to_dict() for c in self.cuts], 'records': list(self.records),
        }

    def save_new(self, path: str | Path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('x', encoding='utf-8') as f:
            f.write(canonical_json(self.to_dict()) + '\n')


def _rational_coefficient(value, max_denominator):
    if isinstance(value, bool) or not isinstance(value, (str, int, float, Fraction)):
        raise ValueError('coefficients must be nonnegative finite rationals/decimals')
    try:
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError('nonfinite coefficient')
        fraction = Fraction(str(value)) if not isinstance(value, Fraction) else value
    except (ValueError, ZeroDivisionError, OverflowError) as exc:
        raise ValueError('invalid coefficient') from exc
    if fraction < 0:
        raise ValueError('negative coefficient')
    # Coefficients may change slightly when rationalized; the certificate beta
    # is computed AGAIN for these exact fractions, never for the input floats.
    return fraction.limit_denominator(max_denominator)


def separate_hl(instance: PhysicalInstance, y_star: Mapping, *,
                supports, alpha=None, options: HLOptions | None = None,
                oracle: MatchingOracle | None = None) -> HLReport:
    """Find HL cuts on explicit, bounded supports; alpha defaults to cardinality.

    A complete oracle classification of all 2^|R| patterns certifies beta.
    No positive HL is emitted on UNKNOWN; supports not proven are recorded.
    The caller selects R using COMP+K fractional values, not H2 success.
    """
    if not isinstance(instance, PhysicalInstance):
        raise TypeError('instance must be PhysicalInstance')
    opt = options or HLOptions()
    V = order_vertices(instance.V)
    if set(y_star) != set(V) or len(y_star) != len(V):
        raise ValueError('y_star must cover exactly physical V')
    for value in y_star.values():
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not 0 <= value <= 1:
            raise ValueError('invalid LP value')
    if alpha is not None and not isinstance(alpha, Mapping):
        raise ValueError('alpha must be a vertex coefficient mapping')
    engine = oracle if oracle is not None else MatchingOracle()
    clock = engine.clock
    begin = clock()
    calls_before = engine.calls
    unique = set()
    proposals = []
    for raw in supports:
        R = order_vertices(set(raw))
        if not R or not set(R) <= set(V):
            raise ValueError('invalid support')
        if R not in unique:
            unique.add(R)
            proposals.append(R)
    cuts, records = [], []
    budget_hit = False

    for R in proposals[:opt.max_supports]:
        if engine.calls - calls_before >= opt.max_oracle_calls or clock() - begin >= opt.total_budget_s:
            budget_hit = True
            break
        start = clock()
        initial_calls = engine.calls
        record = {'support': list(R), 'patterns_total': 1 << len(R)}

        def finish(status, reason=None, **fields):
            record.update(status=status, reason=reason, oracle_calls=engine.calls - initial_calls,
                          elapsed_wall_s=max(0., clock() - start), **fields)
            records.append(record)

        if len(R) > opt.max_support_size:
            finish('SKIPPED_SIZE', 'SUPPORT_EXCEEDS_ENUMERATION_CAP')
            continue
        if alpha is None:
            coeff = {v: Fraction(1) for v in R}
        else:
            if set(alpha) != set(R):
                raise ValueError('alpha must match every vertex in selected support')
            coeff = {v: _rational_coefficient(alpha[v], opt.max_denominator) for v in R}
        if not any(coeff.values()):
            finish('NO_CUT', 'ZERO_COEFFICIENTS')
            continue
        F = order_vertices(set(V) - set(R))

        def remaining():
            return max(0., min(opt.total_budget_s - (clock() - begin),
                               opt.per_support_budget_s - (clock() - start)))

        def query(stations):
            if engine.calls - calls_before >= opt.max_oracle_calls or remaining() <= 0:
                return None
            return engine.check(instance, stations, budget_s=remaining())

        # Mandatory pre-filter: viable complement => every pattern is viable.
        base = query(F)
        if base is None or base.status is Status.UNKNOWN:
            finish('ABSTAIN', 'UNKNOWN_COMPLEMENT')
            continue
        if base.status is Status.VIABLE:
            finish('NO_CUT', 'COMPLEMENT_VIABLE', patterns_examined=0)
            continue

        certified = [_certificate_hash(base)]
        feasible_costs = []
        examined = 0
        unknown = False
        # Inspect patterns in cardinality order to improve early monitoring.
        # Still inspect ALL of them before accepting beta.
        for k in range(len(R) + 1):
            for subset in combinations(R, k):
                # Empty pattern already has the certified complement result.
                result = base if k == 0 else query(order_vertices((*F, *subset)))
                if result is None or result.status is Status.UNKNOWN:
                    unknown = True
                    break
                if k:
                    certified.append(_certificate_hash(result))
                examined += 1
                if result.status is Status.VIABLE:
                    feasible_costs.append(sum((coeff[v] for v in subset), Fraction(0)))
            if unknown:
                break
        if unknown:
            finish('ABSTAIN', 'UNKNOWN_OR_INCOMPLETE_PATTERN', patterns_examined=examined)
            continue
        if examined != (1 << len(R)) or not feasible_costs:
            finish('ABSTAIN', 'INCOMPLETE_OR_EMPTY_FEASIBLE_SET', patterns_examined=examined)
            continue
        beta = min(feasible_costs)  # exactly rational over ALL certified patterns
        lhs = sum(float(coeff[v]) * y_star[v] for v in R)
        gap = float(beta) - lhs
        if beta <= 0 or gap <= opt.min_violation:
            finish('NOT_VIOLATED', 'NO_POSITIVE_MARGINAL_GAP', rhs=str(beta),
                   violation=gap, patterns_examined=examined)
            continue
        canonical_coeff = [[list(vertex_key(v)), str(coeff[v])] for v in R]
        certificate_sha = digest({'instance': instance.fingerprint,
                                  'support': [list(vertex_key(v)) for v in R],
                                  'pattern_certificate_hashes': certified})
        cut_sha = digest({'instance': instance.fingerprint, 'coefs': canonical_coeff,
                          'rhs': str(beta), 'support': [list(vertex_key(v)) for v in R]})
        cuts.append(HLCut(R, tuple((v, coeff[v]) for v in R), beta, gap,
                          certificate_sha, cut_sha, engine.calls - initial_calls,
                          clock() - start))
        finish('CUT', 'FULL_ENUMERATION_CERTIFIED', rhs=str(beta), violation=gap,
               certificate_sha256=certificate_sha, patterns_examined=examined)
    status = 'PARTIAL_BUDGET' if budget_hit else ('CUTS_FOUND' if cuts else 'NO_CUTS')
    return HLReport(instance.fingerprint, tuple(cuts), tuple(records),
                    engine.calls - calls_before, max(0., clock() - begin), status)
