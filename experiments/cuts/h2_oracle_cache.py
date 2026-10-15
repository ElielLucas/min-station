"""AS14: instance-scoped canonical cache for *certified* matching results."""
from __future__ import annotations

from dataclasses import dataclass

from h2_oracle_schema import Status, ViabilityResult, vertex_key


@dataclass(frozen=True)
class CachedCertificate:
    result: ViabilityResult


class CertifiedCache:
    """In-memory cache. UNKNOWN and inconclusive errors are not persisted.

    Cache isolation is by full physical instance SHA and canonical allowed set;
    monotonicity conflicts are fail-closed, never silently substituted.
    """
    def __init__(self):
        self._items: dict[tuple[str, frozenset], CachedCertificate] = {}
        self.hits = 0
        self.misses = 0

    @staticmethod
    def key(instance_sha256: str, allowed) -> tuple[str, frozenset]:
        for v in allowed:
            vertex_key(v)
        return (instance_sha256, frozenset(allowed))

    def get(self, instance_sha256: str, allowed) -> ViabilityResult | None:
        key = self.key(instance_sha256, allowed)
        item = self._items.get(key)
        if item is None:
            self.misses += 1
            return None
        self.hits += 1
        return item.result

    def put(self, result: ViabilityResult):
        if result.status is Status.UNKNOWN:
            return
        key = self.key(result.instance_sha256, result.allowed_stations)
        if key in self._items and self._items[key].result.status != result.status:
            raise AssertionError('conflicting matching certificates for identical cache key')
        for (other_hash, other_allowed), entry in self._items.items():
            if other_hash != result.instance_sha256:
                continue
            other = entry.result
            allowed = key[1]
            if ((result.status is Status.VIABLE and other.status is Status.INFEASIBLE
                 and allowed <= other_allowed) or
                (result.status is Status.INFEASIBLE and other.status is Status.VIABLE
                 and other_allowed <= allowed)):
                raise AssertionError('viability contradicts station monotonicity')
        self._items[key] = CachedCertificate(result)

    def __len__(self):
        return len(self._items)
