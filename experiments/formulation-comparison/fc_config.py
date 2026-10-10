"""Comparação base × F-CC+K: configuração experimental e captura de ambiente.

Nada aqui resolve um modelo; é só o contrato de parâmetros e o registro do
ambiente (Python, Gurobi, SO) para o manifesto de reprodutibilidade.
"""
from __future__ import annotations

import math
import platform
import sys
from dataclasses import dataclass

CHECKPOINT_MARKS_S = (1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0, 600.0, 1800.0, 3600.0)

MODALITIES = ('A', 'B', 'C')  # C é coletada como subproduto de B, não uma execução própria


@dataclass(frozen=True)
class ExperimentConfig:
    """Parâmetros de uma rodada. Imutável: cada rodada grava sua própria cópia.

    `time_limit_s` é o limite por execução de MIP (Modalidade B/C), global
    por braço (preparação, solver e validação) — não reiniciado entre formulações nem dentro de
    uma mesma chamada. `lp_time_limit_s` é um teto de segurança separado
    para a Modalidade A (LPs devem ser rápidos; um teto evita travar o lote
    inteiro por degenerescência, ver nota em `harness.measure_lp`).
    `max_w` é o cap de enumeração de conjuntos conexos de F-CC+K (mesma
    convenção de `fcc.py`/N1: `CapExceeded` acima dele vira
    `NOT_MEASURED_CAP_EXCEEDED`, nunca um valor inventado).
    """
    threads: int = 4
    seed: int = 42
    time_limit_s: float = 3600.0
    lp_time_limit_s: float = 600.0
    max_w: int = 200000
    checkpoints_s: tuple = CHECKPOINT_MARKS_S
    modalities: tuple = MODALITIES
    memory_metric: str = 'ru_maxrss_kb_worker_process_cumulative'

    def __post_init__(self):
        if self.threads < 1:
            raise ValueError('threads deve ser >= 1')
        if (not math.isfinite(self.time_limit_s) or self.time_limit_s <= 0 or
                not math.isfinite(self.lp_time_limit_s) or self.lp_time_limit_s <= 0):
            raise ValueError('limites de tempo devem ser positivos')
        if self.max_w < 1:
            raise ValueError('max_w deve ser >= 1')
        if not all(math.isfinite(c) and c > 0 for c in self.checkpoints_s):
            raise ValueError('checkpoints_s devem ser positivos e finitos')
        if list(self.checkpoints_s) != sorted(self.checkpoints_s):
            raise ValueError('checkpoints_s deve estar em ordem crescente')
        bad = set(self.modalities) - set(MODALITIES)
        if bad:
            raise ValueError(f'modalidades desconhecidas: {bad}')

    def as_dict(self):
        return {
            'threads': self.threads, 'seed': self.seed, 'time_limit_s': self.time_limit_s,
            'lp_time_limit_s': self.lp_time_limit_s, 'max_w': self.max_w,
            'checkpoints_s': list(self.checkpoints_s), 'modalities': list(self.modalities),
            'memory_metric': self.memory_metric,
        }


PILOT_CONFIG = ExperimentConfig(time_limit_s=120.0, lp_time_limit_s=60.0)


def environment_manifest():
    """Versões reais do ambiente de execução — nunca hardcoded."""
    info = {
        'python_version': sys.version.replace('\n', ' '),
        'platform': platform.platform(),
        'processor': platform.processor() or platform.machine(),
    }
    try:
        import gurobipy as gp
        info['gurobi_version'] = '.'.join(str(x) for x in gp.gurobi.version())
        info['gurobi_available'] = True
    except ImportError as exc:
        info['gurobi_version'] = None
        info['gurobi_available'] = False
        info['gurobi_import_error'] = str(exc)
    return info
