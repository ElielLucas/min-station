"""AS15: immutable, reproducible H2 inequality backed by AS14 certificates."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Mapping

from h2_oracle_schema import digest, order_vertices, vertex_key


@dataclass(frozen=True)
class H2Cut:
    instance_sha256: str
    support: tuple
    bhat: tuple
    coefficients: tuple[tuple, ...]
    certificate_sha256: str
    certificate_hashes: tuple[str, ...]
    violation: float
    lhs_at_lp: float
    oracle_calls: int
    elapsed_wall_s: float
    unknown_candidates: tuple = ()
    unexamined_candidates: tuple = ()
    source: str = 'unspecified'
    rhs: int = 2

    def __post_init__(self):
        for v in self.support + self.bhat + self.unknown_candidates + self.unexamined_candidates:
            vertex_key(v)
        if len(set(self.support)) != len(self.support) or self.support != order_vertices(self.support):
            raise ValueError('support must be a canonical vertex set')
        if self.bhat != order_vertices(self.bhat) or not set(self.bhat) <= set(self.support):
            raise ValueError('Bhat must be a canonical subset of R')
        if self.coefficients != tuple((v, 1 if v in self.bhat else 2) for v in self.support):
            raise ValueError('H2 coefficients must be 1 on Bhat and 2 elsewhere')
        if self.rhs != 2:
            raise ValueError('H2 rhs must be 2')
        if not self.certificate_hashes or any(len(s) != 64 for s in self.certificate_hashes):
            raise ValueError('missing certificate hashes')
        if len(self.certificate_sha256) != 64:
            raise ValueError('missing aggregate certificate hash')
        if (not math.isfinite(self.violation) or not math.isfinite(self.lhs_at_lp)
                or abs(self.rhs - self.lhs_at_lp - self.violation) > 1e-8):
            raise ValueError('inconsistent violation')
        if self.oracle_calls < 1 or self.elapsed_wall_s < 0 or not math.isfinite(self.elapsed_wall_s):
            raise ValueError('invalid resource counts')
        if (not set(self.unknown_candidates) <= set(self.support)
                or not set(self.unexamined_candidates) <= set(self.support)
                or set(self.unknown_candidates) & set(self.unexamined_candidates)):
            raise ValueError('unknown/unexamined candidates must be disjoint subsets of R')
        if set(self.unknown_candidates) & set(self.bhat) or set(self.unexamined_candidates) & set(self.bhat):
            raise ValueError('uncertified vertex in Bhat')

    @property
    def cut_hash(self) -> str:
        return digest({'family': 'H2', 'instance_sha256': self.instance_sha256,
                       'coefficients': [[list(vertex_key(v)), c] for v, c in self.coefficients],
                       'rhs': self.rhs})

    @property
    def degenerate_cover(self) -> bool:
        """Exactly y(R)>=1; full testing proves R inclusion-minimal for coverage."""
        return not self.bhat

    @property
    def minimal_cover_certified(self) -> bool:
        return self.degenerate_cover and not self.unknown_candidates and not self.unexamined_candidates

    def lhs(self, y: Mapping) -> float:
        return sum(coef * y[v] for v, coef in self.coefficients)

    def to_dict(self) -> dict:
        return {'schema_version': 'AS15-H2-CUT-v1', 'stage': 'AS15',
                'cut_family': 'H2', 'instance_sha256': self.instance_sha256,
                'support': list(self.support), 'Bhat': list(self.bhat),
                'coefficients': [[v, c] for v, c in self.coefficients], 'rhs': self.rhs,
                'cut_hash': self.cut_hash, 'certificate_sha256': self.certificate_sha256,
                'certificate_hashes': list(self.certificate_hashes),
                'violation': self.violation, 'lhs_at_lp': self.lhs_at_lp,
                'oracle_calls': self.oracle_calls, 'elapsed_wall_s': self.elapsed_wall_s,
                'unknown_candidates': list(self.unknown_candidates),
                'unexamined_candidates': list(self.unexamined_candidates),
                'degenerate_cover': self.degenerate_cover,
                'minimal_cover_certified': self.minimal_cover_certified, 'source': self.source}
