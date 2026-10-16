"""AS21: sound bounded *cardinality* HL certification by infeasible lower layers.

For R subset V, F=V\\R and integer k>=1, the inequality sum(y[R])>=k
is valid whenever the physical oracle certifies INFEASIBLE for F union A,
for every A subset R with |A|<k. Physical feasibility is monotone in
allowed stations. These certificates prove a LOWER BOUND; they do not claim
that min_{viable A}|A| equals k, nor separate arbitrary facets of conv(Phi_R).
No unclassified pattern, inferred numerical solver value or timed-out oracle
response can justify any cut. AS19 and AS20 are deliberately not modified.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from typing import Mapping

from h2_oracle import PhysicalInstance, MatchingOracle
from h2_oracle_schema import Status, digest, canonical_json, order_vertices, vertex_key
from h2_separator import _certificate_hash
from hl_local import HLCut


@dataclass(frozen=True)
class LayeredOptions:
    max_support_size: int = 14
    max_supports: int = 4
    max_oracle_calls: int = 700
    max_patterns_per_support: int = 180
    max_rhs: int = 3
    total_budget_s: float = 24.
    per_support_budget_s: float = 10.
    min_violation: float = 1e-7

    def __post_init__(self):
        for name in ('max_support_size', 'max_supports', 'max_oracle_calls',
                     'max_patterns_per_support', 'max_rhs'):
            val = getattr(self, name)
            if type(val) is not int or val < (1 if name in ('max_support_size', 'max_rhs') else 0):
                raise ValueError(f'invalid {name}')
        for name in ('total_budget_s', 'per_support_budget_s', 'min_violation'):
            val = getattr(self, name)
            if type(val) not in (int, float) or not math.isfinite(val) or val < 0:
                raise ValueError(f'invalid {name}')


@dataclass(frozen=True)
class LayeredReport:
    instance_sha256: str
    cuts: tuple[HLCut, ...]
    records: tuple[dict, ...]
    oracle_calls: int
    elapsed_wall_s: float
    status: str

    def to_dict(self):
        return {
            'schema_version': 'AS21-HL-LAYERED-v1', 'stage': 'AS21',
            'certificate_semantics': 'infeasible_all_layers_strictly_below_rhs',
            'instance_sha256': self.instance_sha256, 'status': self.status,
            'oracle_calls': self.oracle_calls, 'elapsed_wall_s': self.elapsed_wall_s,
            'cuts_emitted': len(self.cuts), 'cuts': [cut.to_dict() for cut in self.cuts],
            'records': list(self.records),
        }

    def save_new(self, path: str | Path):
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open('x', encoding='utf-8') as fh:
            fh.write(canonical_json(self.to_dict()) + '\n')


def separate_hl_layered(instance: PhysicalInstance, y_star: Mapping, *, supports,
                        options: LayeredOptions | None = None,
                        oracle: MatchingOracle | None = None) -> LayeredReport:
    """Certify a violated cardinality lower bound with only the necessary layers.

    The sole candidate rhs is floor(sum(y_R)+eps)+1. If an allowed pattern
    with cardinality below that rhs is VIABLE, there is no violated integer
    cardinality bound at this LP point. UNKNOWN and missing proofs abstain.
    """
    if not isinstance(instance, PhysicalInstance):
        raise TypeError('PhysicalInstance required')
    opt = options or LayeredOptions()
    V = order_vertices(instance.V)
    if not isinstance(y_star, Mapping) or set(y_star) != set(V) or len(y_star) != len(V):
        raise ValueError('y_star must exactly match physical V')
    for value in y_star.values():
        if type(value) not in (int, float) or not math.isfinite(value) or not 0 <= value <= 1:
            raise ValueError('invalid LP point')
    engine = oracle if oracle is not None else MatchingOracle()
    clock = engine.clock
    begin = clock()
    calls_before = engine.calls
    seen = set()
    proposals = []
    for raw in supports:
        R = order_vertices(raw)
        if not R or len(R) != len(set(R)) or not set(R) <= set(V):
            raise ValueError('invalid support')
        if R not in seen:
            proposals.append(R)
            seen.add(R)
    records, cuts = [], []
    budget_hit = False
    for R in proposals[:opt.max_supports]:
        if engine.calls - calls_before >= opt.max_oracle_calls or clock() - begin >= opt.total_budget_s:
            budget_hit = True
            break
        started = clock()
        prev_calls = engine.calls
        lhs = math.fsum(y_star[v] for v in R)
        target = math.floor(lhs + opt.min_violation) + 1
        record = {'support': list(R), 'support_size': len(R), 'lp_mass': lhs,
                  'target_rhs': target, 'full_patterns': 1 << len(R),
                  'method': 'LOWER_LAYERS_INFEASIBLE'}

        def finish(status, reason, **extra):
            record.update(status=status, reason=reason,
                          oracle_calls=engine.calls - prev_calls,
                          elapsed_wall_s=max(0., clock() - started), **extra)
            records.append(record)

        if len(R) > opt.max_support_size:
            finish('SKIPPED_SIZE', 'SUPPORT_OVER_CAP')
            continue
        if target > len(R) or target > opt.max_rhs:
            finish('SKIPPED_RHS_CAP', 'REQUIRED_RHS_EXCEEDS_CAP')
            continue
        if target < 1:
            finish('NO_CUT', 'NO_POSITIVE_VIOLATION')
            continue
        # A bound sum(y_R)>=target is certified iff ALL subsets with fewer
        # than target installed stations are physically infeasible, when every
        # station outside R is offered to the oracle.
        required = sum(math.comb(len(R), j) for j in range(target))
        record['patterns_required'] = required
        if required > opt.max_patterns_per_support:
            finish('SKIPPED_PATTERN_CAP', 'LOWER_LAYERS_EXCEED_CAP', patterns_examined=0)
            continue
        F = order_vertices(set(V) - set(R))
        certified_hashes = []
        examined = 0
        stop = None
        for j in range(target):
            for A in combinations(R, j):
                if (engine.calls - calls_before >= opt.max_oracle_calls
                        or clock() - begin >= opt.total_budget_s
                        or clock() - started >= opt.per_support_budget_s):
                    stop = ('ABSTAIN', 'ORACLE_OR_WALL_BUDGET')
                    break
                left = min(opt.total_budget_s - (clock() - begin),
                           opt.per_support_budget_s - (clock() - started))
                if left <= 0:
                    stop = ('ABSTAIN', 'ORACLE_OR_WALL_BUDGET')
                    break
                res = engine.check(instance, order_vertices((*F, *A)), budget_s=left)
                examined += 1
                if res.status is Status.UNKNOWN:
                    stop = ('ABSTAIN', 'UNKNOWN_PHYSICAL_ORACLE')
                    break
                if res.status is Status.VIABLE:
                    stop = ('NO_CUT_WITNESS', 'VIABLE_BELOW_TARGET')
                    break
                certified_hashes.append(_certificate_hash(res))
            if stop:
                break
        if stop:
            finish(*stop, patterns_examined=examined,
                   patterns_proven_infeasible=len(certified_hashes))
            continue
        if len(certified_hashes) != required or examined != required:
            finish('ABSTAIN', 'INCOMPLETE_LOWER_LAYERS', patterns_examined=examined)
            continue
        beta = Fraction(target)
        gap = target - lhs
        # Robustness in the unlikely event of roundoff at target computation.
        if gap <= opt.min_violation:
            finish('NOT_VIOLATED', 'NUMERICALLY_SMALL_GAP', rhs=str(beta), violation=gap,
                   patterns_examined=examined)
            continue
        coefs = tuple((v, Fraction(1)) for v in R)
        support_keys = [list(vertex_key(v)) for v in R]
        certificate_sha = digest({'schema': 'AS21-LOWER-LAYERS-v1',
                                  'instance': instance.fingerprint, 'support': support_keys,
                                  'rhs': target, 'pattern_certificate_hashes': certified_hashes})
        cut_sha = digest({'instance': instance.fingerprint,
                          'coefs': [[list(vertex_key(v)), '1'] for v in R],
                          'rhs': str(beta), 'support': support_keys})
        cuts.append(HLCut(R, coefs, beta, gap, certificate_sha, cut_sha,
                          engine.calls-prev_calls, clock()-started))
        finish('CUT', 'LOWER_LAYERS_CERTIFIED', rhs=str(beta), violation=gap,
               patterns_examined=examined, patterns_proven_infeasible=required,
               certificate_sha256=certificate_sha)
    # If a support was skipped for a cap, it is not a negative result for HL.
    if len(proposals) > opt.max_supports or len(records) < min(opt.max_supports, len(proposals)):
        budget_hit = True
    if any(r['status'] in ('ABSTAIN', 'SKIPPED_SIZE', 'SKIPPED_RHS_CAP',
                          'SKIPPED_PATTERN_CAP') for r in records):
        budget_hit = True
    status = 'PARTIAL_BUDGET' if budget_hit else ('CUTS_FOUND' if cuts else 'NO_CUTS')
    return LayeredReport(instance.fingerprint, tuple(cuts), tuple(records),
                         engine.calls - calls_before, max(0., clock() - begin), status)
