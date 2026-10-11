"""AS-04: adapters finos sobre compiladores AS-02 e partições AS-03.

Não altera modelos de FC/N1/N2 e nunca trata um master F-CC restrito
como formulação completa.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ALTERNATIVES = HERE.parent / 'alternative-formulations'
if str(ALTERNATIVES) not in sys.path:
    sys.path.insert(0, str(ALTERNATIVES))

from as02_model_a import Instance, compile_a, compile_u  # noqa: E402
from as03_grouping import instance_fingerprint, partition_two, refine_four  # noqa: E402
from as04_schema import ARM_IDS, digest  # noqa: E402


def canonical_k(instance: Instance, cuts) -> tuple[tuple[str, ...], ...]:
    vertices = set(instance.V)
    prepared = tuple(tuple(sorted(group)) for group in cuts)
    if any(not group or len(set(group)) != len(group) or not set(group) <= vertices
           for group in prepared):
        raise ValueError('INTEGRITY_ERROR: corte K vazio, duplicado ou fora de V')
    return tuple(sorted(set(prepared)))


def k_digest(instance: Instance, cuts) -> str:
    return digest(canonical_k(instance, cuts))


def compile_arm(arm_id: str, instance: Instance, cuts, *, mode: str,
                grouping_policy: str = 'reachability_degree', seed: int = 0,
                allow_a4: bool = False):
    """Retorna (compiled, partition_hash). Apenas braços implementados.

    A4 exige autorização AS-05 externa além desta flag; este adaptador não
    deve ser chamado em campanhas sem a verificação correspondente.
    """
    if arm_id not in ARM_IDS or mode not in ('LP', 'MIP'):
        raise ValueError('Braço/modo inválido')
    k = canonical_k(instance, cuts)
    if arm_id == 'U':
        return compile_u(instance, K=(), relax=(mode == 'LP')), None
    if arm_id == 'U_K':
        return compile_u(instance, K=k, relax=(mode == 'LP')), None
    if arm_id == 'A2_K':
        groups = partition_two(instance, grouping_policy, seed)
        return compile_a(instance, groups.blocks, K=k, relax=(mode == 'LP')), groups.partition_hash
    if arm_id == 'A4_K':
        groups2 = partition_two(instance, grouping_policy, seed)
        groups4 = refine_four(instance, groups2, authorized=allow_a4)
        return compile_a(instance, groups4.blocks, K=k, relax=(mode == 'LP')), groups4.partition_hash
    raise NotImplementedError(f'{arm_id} não possui modelo completo homologado em AS-04')


def context_hash(instance: Instance, arm_id: str, mode: str,
                 cuts, partition_sha256: str | None) -> str:
    return digest({'as04_arm': arm_id, 'mode': mode,
                   'instance': instance_fingerprint(instance),
                   'K': k_digest(instance, cuts) if arm_id != 'U' else None,
                   'partition': partition_sha256})
