"""AS15: static, bounded H2 separation with AS14 matching certificates.

The y* vector is consulted only for support priority and inequality violation.
Validity comes exclusively from physical certificates for V\\R and V\\R+v.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from h2_cut import H2Cut
from h2_oracle import MatchingOracle, PhysicalInstance
from h2_oracle_schema import (VALIDATOR_IDENTITY, Status, canonical_json,
                              digest, order_vertices, vertex_key)
from h2_supports import SupportProposal, select_supports


@dataclass(frozen=True)
class SeparatorOptions:
    min_violation: float = 1e-7
    total_budget_s: float | None = 10.0
    per_support_budget_s: float | None = 2.0
    max_supports: int = 32
    max_support_size: int | None = None
    max_pairs: int = 32
    max_oracle_calls: int = 500
    max_candidates_per_support: int | None = None
    max_cuts: int = 16

    def __post_init__(self):
        for name in ('total_budget_s', 'per_support_budget_s', 'min_violation'):
            value = getattr(self, name)
            if value is None and name != 'min_violation':
                continue
            if (isinstance(value, bool) or not isinstance(value, (int, float))
                    or not math.isfinite(value) or value < 0):
                raise ValueError(f'invalid {name}')
        for name in ('max_supports', 'max_pairs', 'max_oracle_calls', 'max_cuts',
                     'max_support_size', 'max_candidates_per_support'):
            value = getattr(self, name)
            if value is not None and (type(value) is not int or value < 0):
                raise ValueError(f'invalid {name}')


@dataclass(frozen=True)
class SeparationReport:
    instance_sha256: str
    cuts: tuple[H2Cut, ...]
    records: tuple[dict, ...]
    status: str
    oracle_calls: int
    elapsed_wall_s: float
    budget_s: float | None
    support_count: int
    source_commit: str | None = None
    evidence_path: str | None = None

    def to_dict(self) -> dict:
        out = {'schema_version': 'AS15-H2-SEPARATOR-v1', 'stage': 'AS15',
               'cut_family': 'H2', 'instance_sha256': self.instance_sha256,
               'status': self.status, 'oracle_calls': self.oracle_calls,
               'elapsed_wall_s': self.elapsed_wall_s, 'budget_s': self.budget_s,
               'supports_proposed': self.support_count,
               'supports_examined': len(self.records), 'cuts_emitted': len(self.cuts),
               'nondegenerate_cuts': sum(not c.degenerate_cover for c in self.cuts),
               'degenerate_supports': sum(r['status'] == 'DEGENERATE_COVER' for r in self.records),
               'unknown_supports': sum(r['status'] == 'UNKNOWN_COMPLEMENT' for r in self.records),
               'validator_identity': VALIDATOR_IDENTITY,
               'cuts': [c.to_dict() for c in self.cuts],
               'records': list(self.records)}
        if self.source_commit:
            out['source_commit'] = self.source_commit
        if self.evidence_path:
            out['evidence_path'] = self.evidence_path
        return out

    def save_new(self, path: str | Path) -> None:
        """Append-only experimental contract: never overwrite a previous run."""
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open('x', encoding='utf-8') as f:
            f.write(canonical_json(self.to_dict()) + '\n')


def _certificate_hash(result) -> str:
    """Stable physical certificate: timestamps, call numbers and cache hits excluded."""
    if result.status is Status.UNKNOWN:
        raise ValueError('UNKNOWN is not a certificate')
    def typed(items):
        return [list(vertex_key(v)) for v in items]
    return digest({'status': result.status.value, 'instance_sha256': result.instance_sha256,
                   'allowed_stations': typed(result.allowed_stations),
                   'robot_count': result.robot_count, 'matching_size': result.matching_size,
                   'witness': [[list(vertex_key(u)), list(vertex_key(v))] for u, v in result.witness],
                   'hall_origins': typed(result.hall_origins),
                   'hall_destinations': typed(result.hall_destinations)})


def separate_h2(instance: PhysicalInstance, y_star: Mapping, *,
                oracle: MatchingOracle | None = None, k_supports=(), hall_supports=(),
                proposed_supports=None, options: SeparatorOptions | None = None,
                source_commit: str | None = None, evidence_path: str | None = None
                ) -> SeparationReport:
    """Propose R, certify complement, then conservatively classify candidates.

    For a certified-infeasible complement F, every v that cannot be certified
    INFEASIBLE in F+v receives coefficient 2. This includes UNKNOWN, timeout,
    unexamined, and VIABLE; no other physical implication is inferred.
    """
    if not isinstance(instance, PhysicalInstance):
        raise TypeError('instance must be PhysicalInstance')
    opt = options or SeparatorOptions()
    V = order_vertices(instance.V)
    if set(y_star) != set(V):
        raise ValueError('y_star must contain exactly the physical vertices')
    for v in V:
        if (isinstance(y_star[v], bool) or not isinstance(y_star[v], (int, float))
                or not math.isfinite(y_star[v]) or not 0 <= y_star[v] <= 1):
            raise ValueError('y_star must have finite values in [0, 1]')
    if source_commit is not None and not source_commit.strip():
        raise ValueError('empty source_commit')
    engine = oracle if oracle is not None else MatchingOracle()
    clock = engine.clock
    begin = clock()
    calls_at_start = engine.calls
    if proposed_supports is None:
        supports = select_supports(V, y_star, k_supports=k_supports,
                                   hall_supports=hall_supports, max_supports=opt.max_supports,
                                   max_support_size=opt.max_support_size,
                                   max_pairs=opt.max_pairs)
    else:
        # Explicit microinstance control, still bounded and deterministic.
        unique = {}
        for raw in proposed_supports:
            proposal = raw if isinstance(raw, SupportProposal) else SupportProposal(tuple(raw), 'EXPLICIT', 0.)
            for v in proposal.support:
                vertex_key(v)
            R = order_vertices(set(proposal.support))
            if not set(R) <= set(V):
                raise ValueError('support outside V')
            if not R or (opt.max_support_size is not None and len(R) > opt.max_support_size):
                continue
            candidate = SupportProposal(R, proposal.source, sum(y_star[v] for v in R))
            if R not in unique or candidate.source < unique[R].source:
                unique[R] = candidate
        supports = tuple(unique[k] for k in sorted(unique, key=lambda R: tuple(vertex_key(v) for v in R)))[:opt.max_supports]
    cuts = []
    records = []
    existing = set()
    budget_exhausted = False

    def total_remaining():
        if opt.total_budget_s is None:
            return None
        return max(0., opt.total_budget_s - max(0., clock() - begin))

    for proposed in supports:
        if len(cuts) >= opt.max_cuts:
            break
        if engine.calls - calls_at_start >= opt.max_oracle_calls or total_remaining() == 0:
            budget_exhausted = True
            break
        R = proposed.support
        start = clock()
        calls_before = engine.calls
        record = {'support': list(R), 'source': proposed.source, 'mass': proposed.mass}

        def finish(status, reason=None, **fields):
            record.update({'status': status, 'reason': reason,
                           'oracle_calls': engine.calls - calls_before,
                           'elapsed_wall_s': max(0., clock() - start)})
            record.update(fields)
            records.append(record)

        # Necessary pre-filter: coefficients >=1, so y(R)>=2 cannot violate H2.
        if proposed.mass >= 2:
            finish('FILTERED_MASS', 'Y_R_GE_2')
            continue
        F = order_vertices(set(V) - set(R))

        def support_remaining():
            local = None if opt.per_support_budget_s is None else max(0., opt.per_support_budget_s - max(0., clock() - start))
            global_ = total_remaining()
            if local is None:
                return global_
            if global_ is None:
                return local
            return min(local, global_)

        if support_remaining() == 0:
            finish('UNKNOWN_COMPLEMENT', 'BUDGET_EXHAUSTED_BEFORE_COMPLEMENT')
            continue
        base = engine.check(instance, F, budget_s=support_remaining())
        if base.status is Status.UNKNOWN:
            finish('UNKNOWN_COMPLEMENT', base.reason)
            continue
        if base.status is Status.VIABLE:
            finish('NO_CUT', 'COMPLEMENT_VIABLE')
            continue
        hashes = [_certificate_hash(base)]
        bhat = []
        unknown = []
        unexamined = []
        # High LP mass first: proving 1 instead of 2 has greatest gain here.
        candidates = sorted(R, key=lambda v: (-y_star[v], vertex_key(v)))
        for j, v in enumerate(candidates):
            if ((opt.max_candidates_per_support is not None and j >= opt.max_candidates_per_support)
                    or engine.calls - calls_at_start >= opt.max_oracle_calls
                    or support_remaining() == 0):
                unexamined.extend(candidates[j:])
                break
            result = engine.check(instance, order_vertices((*F, v)), budget_s=support_remaining())
            if result.status is Status.INFEASIBLE:
                bhat.append(v)
                hashes.append(_certificate_hash(result))
            elif result.status is Status.UNKNOWN:
                unknown.append(v)
        bhat = order_vertices(bhat)
        coeffs = tuple((v, 1 if v in bhat else 2) for v in R)
        lhs = float(sum(coef * y_star[v] for v, coef in coeffs))
        violation = 2. - lhs
        aggregate = digest({'instance_sha256': instance.fingerprint,
                            'support': [list(vertex_key(v)) for v in R],
                            'bhat': [list(vertex_key(v)) for v in bhat],
                            'certificate_hashes': hashes})
        cut = H2Cut(instance_sha256=instance.fingerprint, support=R, bhat=bhat,
                    coefficients=coeffs, certificate_sha256=aggregate,
                    certificate_hashes=tuple(hashes), violation=violation,
                    lhs_at_lp=lhs, oracle_calls=engine.calls - calls_before,
                    elapsed_wall_s=max(0., clock() - start), unknown_candidates=order_vertices(unknown),
                    unexamined_candidates=order_vertices(unexamined), source=proposed.source)
        if violation <= opt.min_violation:
            finish('NOT_VIOLATED', 'BELOW_TOLERANCE', violation=violation)
        elif cut.degenerate_cover:
            finish('DEGENERATE_COVER', 'EQUIVALENT_TO_Y_R_GE_1',
                   violation=violation, minimal_cover_certified=cut.minimal_cover_certified,
                   unknown_candidates=list(cut.unknown_candidates),
                   unexamined_candidates=list(cut.unexamined_candidates))
        elif cut.cut_hash in existing:
            finish('DUPLICATE', 'CUT_HASH_EXISTS', cut_hash=cut.cut_hash)
        else:
            existing.add(cut.cut_hash)
            cuts.append(cut)
            finish('EMITTED', None, violation=violation, cut_hash=cut.cut_hash,
                   certificate_sha256=cut.certificate_sha256,
                   unknown_candidates=list(cut.unknown_candidates),
                   unexamined_candidates=list(cut.unexamined_candidates))
    status = 'CUTS_FOUND' if cuts else ('BUDGET_EXHAUSTED' if budget_exhausted else 'NO_CUT')
    if not cuts and any(r['status'] == 'UNKNOWN_COMPLEMENT' for r in records):
        status = 'UNKNOWN'
    return SeparationReport(instance_sha256=instance.fingerprint, cuts=tuple(cuts),
                            records=tuple(records), status=status,
                            oracle_calls=engine.calls - calls_at_start,
                            elapsed_wall_s=max(0., clock() - begin),
                            budget_s=opt.total_budget_s, support_count=len(supports),
                            source_commit=source_commit, evidence_path=evidence_path)
