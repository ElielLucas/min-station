"""AS14: typed, deterministic evidence contracts for physical matching.

The evidence describes a computational certificate, not a formal proof that
arbitrary input software has been verified.  UNKNOWN is never a negative proof.
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from enum import Enum
from typing import Any

SCHEMA_VERSION = 'AS14-MATCHING-ORACLE-v1'
VALIDATOR_IDENTITY = 'independent_validator.destinos_alcancaveis + deterministic_bipartite_matching/v1'


class Status(str, Enum):
    VIABLE = 'VIABLE'
    INFEASIBLE = 'INFEASIBLE'
    UNKNOWN = 'UNKNOWN'


def vertex_key(value: str | int) -> tuple[str, str | int]:
    """Canonical, type-preserving representation; `True` is not vertex 1."""
    if type(value) is str:
        return ('str', value)
    if type(value) is int:
        return ('int', value)
    raise ValueError('vertices must have type str or int (not bool)')


def order_vertices(vertices):
    return tuple(sorted(vertices, key=vertex_key))


def canonical_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(',', ':'),
                      allow_nan=False)


def digest(data: Any) -> str:
    return hashlib.sha256(canonical_json(data).encode('utf-8')).hexdigest()


@dataclass(frozen=True)
class ViabilityResult:
    status: Status
    instance_sha256: str
    allowed_stations: tuple
    robot_count: int
    matching_size: int | None
    elapsed_wall_s: float
    budget_s: float | None
    calls: int
    fingerprint: str
    witness: tuple[tuple, ...] = ()
    hall_origins: tuple = ()
    hall_destinations: tuple = ()
    reason: str | None = None
    cache_hit: bool = False

    def __post_init__(self):
        if self.elapsed_wall_s < 0 or not math.isfinite(self.elapsed_wall_s):
            raise ValueError('invalid elapsed time')
        if self.budget_s is not None and (self.budget_s < 0 or not math.isfinite(self.budget_s)):
            raise ValueError('invalid budget')
        if self.status is Status.UNKNOWN and (self.matching_size is not None or self.witness or
                                              self.hall_origins or self.hall_destinations):
            raise ValueError('UNKNOWN must not provide an unverified certificate')
        if self.status is Status.VIABLE and (self.matching_size != self.robot_count or
                                             len(self.witness) != self.robot_count):
            raise ValueError('VIABLE requires a complete matching witness')
        if self.status is Status.INFEASIBLE and not (self.matching_size is not None and
                                                     self.matching_size < self.robot_count and
                                                     len(self.hall_origins) > len(self.hall_destinations)):
            raise ValueError('INFEASIBLE requires a matching deficiency and Hall witness')

    def to_dict(self) -> dict:
        out = {
            'schema_version': SCHEMA_VERSION,
            'stage': 'AS14',
            'status': self.status.value,
            'instance_sha256': self.instance_sha256,
            'allowed_stations': list(self.allowed_stations),
            'robot_count': self.robot_count,
            'elapsed_wall_s': self.elapsed_wall_s,
            'budget_s': self.budget_s,
            'calls': self.calls,
            'fingerprint': self.fingerprint,
            'validator_identity': VALIDATOR_IDENTITY,
            'cache_hit': self.cache_hit,
        }
        if self.matching_size is not None:
            out['matching_size'] = self.matching_size
        if self.status is Status.VIABLE:
            out['witness'] = [list(p) for p in self.witness]
        if self.status is Status.INFEASIBLE:
            out['hall_certificate'] = {
                'origins': list(self.hall_origins),
                'neighbors': list(self.hall_destinations),
                'deficiency': len(self.hall_origins) - len(self.hall_destinations),
            }
        if self.reason is not None:
            out['reason'] = self.reason
        return out

    def to_json(self) -> str:
        return canonical_json(self.to_dict())
