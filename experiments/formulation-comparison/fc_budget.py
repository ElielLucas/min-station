"""FC-01: limite de parede efetivo por braço, incluindo código Python.

Cada trabalho executa em processo Python *spawn* independente: o processo
supervisor pode encerrar enumeração/construção que não cooperem com deadlines.
Nunca converta Work em segundos; cada medida é reportada separadamente.
"""
from __future__ import annotations

import math
import multiprocessing as mp
import time
import traceback
from dataclasses import dataclass
from typing import Callable

PREPARATION_PHASES = frozenset({'startup', 'k_preparation', 'model_build', 'preparation'})


class BudgetExpired(TimeoutError):
    """O orçamento acabou antes de iniciar uma próxima operação."""


@dataclass(frozen=True)
class BoundedOutcome:
    status: str
    value: object | None
    wall_total_s: float
    phase_wall_s: tuple[tuple[str, float], ...]
    reason: str = ''


class WallBudget:
    """Deadline absoluto com relógio injetável para testes sem Gurobi."""

    def __init__(self, budget_s: float, *, clock: Callable[[], float] = time.monotonic,
                 started_at: float | None = None):
        if not isinstance(budget_s, (int, float)) or not math.isfinite(budget_s) or budget_s <= 0:
            raise ValueError('budget_s deve ser positivo e finito')
        self._clock = clock
        self.started_at = clock() if started_at is None else started_at
        self.deadline = self.started_at + float(budget_s)

    def remaining(self) -> float:
        return max(0.0, self.deadline - self._clock())

    def elapsed(self) -> float:
        return max(0.0, self._clock() - self.started_at)

    def require_remaining(self) -> float:
        remaining = self.remaining()
        if remaining <= 0:
            raise BudgetExpired('Prazo global esgotado antes de iniciar a próxima operação')
        return remaining


class WorkerContext:
    """API de fase/duração disponível para o trabalho supervisionado."""

    def __init__(self, connection, budget: WallBudget):
        self._connection = connection
        self._budget = budget

    def phase(self, name: str) -> None:
        self._connection.send(('phase', name, time.monotonic()))
        self._budget.require_remaining()

    def remaining(self) -> float:
        return self._budget.remaining()

    def require_remaining(self) -> float:
        return self._budget.require_remaining()

    def elapsed(self) -> float:
        return self._budget.elapsed()


def _worker_entry(connection, func, args, kwargs, budget_s: float, started_at: float) -> None:
    """Alvo importável para multiprocessing spawn; dados retornam pelo pipe."""
    budget = WallBudget(budget_s, started_at=started_at)
    ctx = WorkerContext(connection, budget)
    try:
        ctx.phase('startup')
        value = func(ctx, *args, **kwargs)
        budget.require_remaining()
        connection.send(('result', value))
    except BaseException as exc:  # noqa: BLE001 - fronteira isolada do worker
        kind = type(exc).__name__
        if isinstance(exc, BudgetExpired):
            status = 'TIMEOUT'
        elif kind == 'CapExceeded':
            status = 'CAP_EXCEEDED'
        elif kind in ('GurobiError', 'ImportError', 'ModuleNotFoundError'):
            status = 'SOLVER_UNAVAILABLE' if 'license' in str(exc).lower() else 'WORKER_ERROR'
        else:
            status = 'WORKER_ERROR'
        connection.send(('error', status, f'{kind}: {exc}\n{traceback.format_exc()}'))
    finally:
        connection.close()


def _timeout_status(phase: str) -> str:
    if phase in PREPARATION_PHASES or phase == 'cleanup':
        return 'TIMEOUT_PREPARATION'
    if phase == 'validation':
        return 'TIMEOUT_VALIDATION'
    return 'TIMEOUT_SOLVER'


def run_bounded(func, *args, budget_s: float, start_method: str = 'spawn', **kwargs) -> BoundedOutcome:
    """Executa um braço com prazo global, inclusive spawn, setup e teardown.

    Um resultado só pode ser publicado após o worker reportar conclusão.
    Se o deadline vencer, o supervisor termina o worker e devolve abstenção.
    O overhead do controle também conta; pequenas ultrapassagens por
    escalonamento do SO são possíveis e são registradas (não escondidas).
    """
    budget = WallBudget(budget_s)
    ctx = mp.get_context(start_method)
    recv, send = ctx.Pipe(duplex=False)
    process = ctx.Process(target=_worker_entry,
                          args=(send, func, args, kwargs, float(budget_s), budget.started_at))
    last_phase = 'startup'
    phase_started = budget.started_at
    phase_durations: dict[str, float] = {}
    final_status = None
    final_value = None
    final_reason = ''

    def close_phase(now: float):
        nonlocal phase_started
        dt = max(0.0, now - phase_started)
        phase_durations[last_phase] = phase_durations.get(last_phase, 0.0) + dt
        phase_started = now

    try:
        process.start()
        send.close()
        while True:
            remaining = budget.remaining()
            if remaining <= 0:
                final_status = _timeout_status(last_phase)
                final_reason = f'Prazo global {budget_s:g}s esgotado na fase {last_phase}'
                break
            if recv.poll(min(remaining, 0.1)):
                try:
                    msg = recv.recv()
                except EOFError:
                    final_status = 'WORKER_ERROR'
                    final_reason = f'Worker encerrou o pipe sem resultado; exitcode={process.exitcode}'
                    break
                if msg[0] == 'phase':
                    # monotonic é compartilhado pelo SO entre os processos.
                    close_phase(max(budget.started_at, min(msg[2], time.monotonic())))
                    last_phase = msg[1]
                elif msg[0] == 'result':
                    final_status = 'COMPLETED'
                    final_value = msg[1]
                    break
                elif msg[0] == 'error':
                    final_status = _timeout_status(last_phase) if msg[1] == 'TIMEOUT' else msg[1]
                    final_reason = msg[2]
                    break
            elif not process.is_alive():
                # pipe pode ter sido fechado sem nenhuma mensagem.
                final_status = 'WORKER_ERROR'
                final_reason = f'Worker encerrou sem resultado; exitcode={process.exitcode}'
                break
    except (OSError, RuntimeError, ValueError) as exc:
        final_status = 'WORKER_ERROR'
        final_reason = f'Falha ao iniciar/supervisionar o processo: {type(exc).__name__}: {exc}'
    finally:
        close_phase(time.monotonic())
        shutdown_started = phase_started
        if process.pid is not None and process.is_alive():
            process.terminate()
            process.join(timeout=0.2)
            if process.is_alive():
                process.kill()
                process.join(timeout=0.2)
        elif process.pid is not None:
            process.join(timeout=0.1)
        recv.close()
        send.close()
        phase_durations['supervisor_shutdown'] = max(
            0.0, time.monotonic() - shutdown_started,
        )
    total = budget.elapsed()
    return BoundedOutcome(
        status=final_status or 'WORKER_ERROR', value=final_value if final_status == 'COMPLETED'
        else None, wall_total_s=total,
        phase_wall_s=tuple(sorted(phase_durations.items())), reason=final_reason,
    )
