"""AS-03: partições determinísticas de origens para a formulação A.

Não lê resultados LP/MIP, custos, bounds, partições de avaliação ou solver.
O seed é parte do protocolo, não uma escolha após observar resultados.
A4 só pode ser produzido como refinamento aninhado de uma A2 explícita.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Iterable


POLICIES = ('balanced', 'reachability_degree')
POLICY_VERSION = 'AS03-GROUPING-V1'


class NotApplicable(ValueError):
    """O número de origens ou tamanho dos blocos impede o k solicitado."""


@dataclass(frozen=True)
class Grouping:
    blocks: tuple[tuple[str, ...], ...]
    policy: str
    seed: int
    instance_hash: str
    partition_hash: str
    parent_hash: str | None = None

    @property
    def k(self) -> int:
        return len(self.blocks)


def _sha(value: object) -> str:
    data = json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(',', ':'), allow_nan=False)
    return sha256(data.encode('utf-8')).hexdigest()


def _stable_pair(v: Iterable[str]) -> tuple[str, ...]:
    raw = tuple(v)
    if not raw or not all(isinstance(x, str) and x for x in raw):
        raise ValueError('Rótulos devem ser strings não vazias')
    if len(set(raw)) != len(raw):
        raise ValueError('Duplicação de rótulos')
    return tuple(sorted(raw))


def _snapshot(instance) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...], tuple[tuple[str, str], ...], int]:
    """Contrato estrutural mínimo compatível com AS02 Instance."""
    V = _stable_pair(instance.V)
    S = _stable_pair(instance.S)
    T = _stable_pair(instance.T)
    if len(S) != len(T) or not set(S + T).issubset(V):
        raise ValueError('S/T inválidos ou fora de V')
    if not isinstance(instance.r, int) or isinstance(instance.r, bool) or instance.r < 1:
        raise ValueError('r deve ser inteiro positivo')
    arcs = tuple(instance.A_r)
    vertices = set(V)  # O(1) amortizado por arco; importante em MAPF grande.
    if len(arcs) != len(set(arcs)) or any(
        not isinstance(a, tuple) or len(a) != 2 or a[0] == a[1]
        or a[0] not in vertices or a[1] not in vertices for a in arcs
    ):
        raise ValueError('A_r inválido')
    return V, S, T, tuple(sorted(arcs)), instance.r


def instance_fingerprint(instance) -> str:
    V, S, T, arcs, r = _snapshot(instance)
    return _sha({'V': V, 'S': S, 'T': T, 'A_r': arcs, 'r': r})


def _validated_policy(policy: str, seed: int) -> None:
    if policy not in POLICIES:
        raise ValueError(f'Política desconhecida: {policy!r}')
    if not isinstance(seed, int) or isinstance(seed, bool) or seed < 0:
        raise ValueError('seed deve ser inteiro >= 0')


def _canonical_blocks(blocks: Iterable[Iterable[str]], S: tuple[str, ...], *, k: int) -> tuple[tuple[str, ...], ...]:
    raw = tuple(tuple(part) for part in blocks)
    if len(raw) != k:
        raise ValueError(f'Partição deve conter exatamente {k} blocos')
    if any(not part or len(part) != len(set(part)) for part in raw):
        raise ValueError('Grupo vazio ou origem repetida dentro de grupo')
    flat = [o for part in raw for o in part]
    if len(flat) != len(set(flat)) or set(flat) != set(S):
        raise ValueError('Partição deve cobrir S exatamente uma vez')
    return tuple(sorted((tuple(sorted(p)) for p in raw)))


def _ordering(origins: tuple[str, ...], arcs: tuple[tuple[str, str], ...], policy: str, seed: int) -> tuple[str, ...]:
    if policy == 'balanced':
        # Controle sem características estruturais: ordem canônica de rótulos.
        return origins
    eligible = set(origins)
    degree = {v: [0, 0, 0] for v in origins}
    for u, v in arcs:
        if u in eligible:
            degree[u][0] += 1
            degree[u][2] += int(v in eligible)
        if v in eligible:
            degree[v][1] += 1
    if len({tuple(x) for x in degree.values()}) <= 1:
        # Sem informação discriminatória, controle balanceado (seed não muda).
        return origins
    return tuple(sorted(origins, key=lambda v: (
        -degree[v][2], -(degree[v][0] + degree[v][1]),
        -abs(degree[v][0] - degree[v][1]),
        _sha({'seed': seed, 'v': v}), v,
    )))


def _split(origins: tuple[str, ...], arcs: tuple[tuple[str, str], ...],
           policy: str, seed: int) -> tuple[tuple[str, ...], tuple[str, ...]]:
    if len(origins) < 2:
        raise NotApplicable('Não é possível criar dois blocos não vazios com menos de duas origens')
    ordered = _ordering(origins, arcs, policy, seed)
    return tuple(sorted(ordered[::2])), tuple(sorted(ordered[1::2]))


def _grouping(instance, blocks, policy: str, seed: int, parent_hash=None) -> Grouping:
    _, S, _, _, _ = _snapshot(instance)
    raw_blocks = tuple(tuple(part) for part in blocks)
    norm = _canonical_blocks(raw_blocks, S, k=len(raw_blocks))
    fingerprint = instance_fingerprint(instance)
    digest = _sha({'version': POLICY_VERSION, 'instance_hash': fingerprint,
                   'blocks': norm, 'policy': policy, 'seed': seed,
                   'parent_hash': parent_hash})
    return Grouping(norm, policy, seed, fingerprint, digest, parent_hash)


def partition_two(instance, policy: str = 'reachability_degree', seed: int = 0) -> Grouping:
    """Gera dois blocos não vazios, estáveis sob permutações das entradas."""
    _validated_policy(policy, seed)
    _, S, _, arcs, _ = _snapshot(instance)
    return _grouping(instance, _split(S, arcs, policy, seed), policy, seed)


def refine_four(instance, groups2: Grouping, *, policy: str | None = None,
                seed: int | None = None, authorized: bool = False) -> Grouping:
    """Refina cada bloco de A2 em dois; exige liberação explícita AS-05.

    Em testes de implementação a autorização pode ser passada diretamente;
    o runner comparativo deve vinculá-la à decisão versionada de AS-05.
    """
    if not authorized:
        raise PermissionError('A4 requer autorização registrada no gate AS-05')
    if not isinstance(groups2, Grouping) or groups2.k != 2:
        raise ValueError('É necessária uma partição A2 válida')
    policy = policy if policy is not None else groups2.policy
    seed = seed if seed is not None else groups2.seed
    _validated_policy(policy, seed)
    _, S, _, arcs, _ = _snapshot(instance)
    _canonical_blocks(groups2.blocks, S, k=2)
    if groups2.instance_hash != instance_fingerprint(instance):
        raise ValueError('Partição A2 pertence a uma instância diferente')
    if groups2.parent_hash is not None:
        raise ValueError('Partição A2 não pode ter parent_hash')
    _validated_policy(groups2.policy, groups2.seed)
    expected_parent = _grouping(instance, groups2.blocks, groups2.policy, groups2.seed)
    if groups2.partition_hash != expected_parent.partition_hash:
        raise ValueError('Hash da partição A2 não confere')
    if min(map(len, groups2.blocks)) < 2:
        raise NotApplicable('A4 requer pelo menos duas origens em cada grupo A2')
    children = []
    for block in groups2.blocks:
        children.extend(_split(block, arcs, policy, seed))
    a4 = _grouping(instance, children, policy, seed, parent_hash=groups2.partition_hash)
    parents = list(map(set, groups2.blocks))
    if any(sum(set(child) <= p for p in parents) != 1 for child in a4.blocks):
        raise AssertionError('Violação de refinamento aninhado')
    return a4


def is_nested(groups2: Iterable[Iterable[str]], groups4: Iterable[Iterable[str]]) -> bool:
    """Predicado matemático independente do hash e da política."""
    parents = tuple(set(g) for g in groups2)
    children = tuple(set(g) for g in groups4)
    if len(parents) != 2 or len(children) != 4:
        return False
    if any(not g for g in parents + children):
        return False
    parent_flat = [x for g in parents for x in g]
    child_flat = [x for g in children for x in g]
    return (len(parent_flat) == len(set(parent_flat))
            and len(child_flat) == len(set(child_flat))
            and set(parent_flat) == set(child_flat)
            and all(sum(c <= p for p in parents) == 1 for c in children))
