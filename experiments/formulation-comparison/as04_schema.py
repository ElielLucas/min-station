"""AS-04: esquema de resultados sem confundir evidências LP, MIP e racionais.

Pure functions; nenhuma informação faltante é substituída por zero.
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field, asdict

SCHEMA = 'AS04-COMPARISON-v1'
ARM_IDS = ('U', 'U_K', 'A2_K', 'A4_K', 'CUTS_K', 'B_K', 'C_K', 'FCC_K', 'CORE_IP')
EFFECTS = {'K_EFFECT': ('U', 'U_K'), 'A_EFFECT': ('U_K', 'A2_K'),
           'REFINEMENT_EFFECT': ('A2_K', 'A4_K')}
SUCCESS = {'OPTIMAL_NUMERIC', 'TIME_LIMIT', 'NO_INCUMBENT', 'INFEASIBLE'}
CENSORED = {'NOT_AUTHORIZED', 'NOT_APPLICABLE', 'NOT_BUILT_SIZE',
            'NOT_BUILT_CAP', 'MEMORY_LIMIT', 'SOLVER_ERROR', 'VALIDATION_FAIL',
            'NOT_MEASURED', 'TIMEOUT_PREPARATION', 'TIMEOUT_SOLVER',
            'TIMEOUT_VALIDATION', 'WORKER_ERROR', 'INTEGRITY_ERROR'}


def digest(value) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def number(value) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    x = float(value)
    return x if math.isfinite(x) else None


@dataclass(frozen=True)
class SolverPolicy:
    backend: str = 'gurobi'
    seed: int = 42
    threads: int = 1
    budget_s: float = 120.0
    warm_start: str = 'none'
    solver_settings: tuple[tuple[str, str], ...] = ()
    memory_limit_bytes: int | None = None

    def __post_init__(self):
        if self.backend != 'gurobi' or type(self.seed) is not int or self.seed < 0:
            raise ValueError('Backend produtivo gurobi e seed não negativo são obrigatórios')
        if type(self.threads) is not int or self.threads < 1 or number(self.budget_s) is None or self.budget_s <= 0:
            raise ValueError('Threads e budget inválidos')
        if self.warm_start != 'none':
            raise ValueError('Warm starts não implementados; não há comparação com regras heterogêneas')
        if self.memory_limit_bytes is not None and (type(self.memory_limit_bytes) is not int or self.memory_limit_bytes < 1):
            raise ValueError('Limite de RAM inválido')
        if self.solver_settings:
            raise ValueError('Parâmetros extras ainda não homologados; fail-closed')

    @property
    def sha256(self):
        return digest(asdict(self))


@dataclass
class ArmResult:
    case_name: str
    arm_id: str
    mode: str
    status: str
    instance_sha256: str | None
    structural_sha256: str | None
    reference_k_sha256: str | None
    applied_k_sha256: str | None
    k_validated: bool
    solver_policy_sha256: str
    solver_policy: dict
    model_complete: bool = False
    reason: str = ''
    wall_total_s: float | None = None
    wall_phases_s: dict[str, float] = field(default_factory=dict)
    solver_version: str | None = None
    input_load_s: float | None = None
    reachability_s: float | None = None
    solver_runtime_s: float | None = None
    presolve_wall_s: float | None = None
    solver_work: float | None = None
    nodes: float | None = None
    peak_rss_kb: int | None = None
    n_variables: int | None = None
    n_constraints: int | None = None
    n_nonzeros: int | None = None
    partition_sha256: str | None = None
    lp_opt_value: float | None = None
    lp_dual_bound: float | None = None
    mip_numeric_bound: float | None = None
    mip_numeric_incumbent: float | None = None
    physical_validated_ub: int | None = None
    installed: tuple[str, ...] | None = None
    rational_verified_lb_exact: str | None = None
    rational_verifier_id: str | None = None
    evidence_class: str = 'NOT_MEASURED'
    comparison_role: str = 'physical_model'

    def __post_init__(self):
        if self.arm_id not in ARM_IDS or self.mode not in ('LP', 'MIP'):
            raise ValueError('Braço ou modalidade desconhecida')
        if self.status not in SUCCESS | CENSORED:
            raise ValueError(f'Status desconhecido: {self.status}')
        if self.arm_id == 'CORE_IP':
            self.comparison_role = 'lower_bound_control_only'
            if self.physical_validated_ub is not None:
                raise ValueError('CORE_IP não atesta instalação física')
        if self.arm_id == 'FCC_K' and not self.model_complete:
            self.lp_opt_value = self.lp_dual_bound = self.mip_numeric_bound = None
        if self.mode == 'LP':
            self.mip_numeric_bound = None
            self.mip_numeric_incumbent = None
            self.physical_validated_ub = None
            self.installed = None
            if self.status != 'OPTIMAL_NUMERIC' or not self.model_complete:
                self.lp_opt_value = None
            # AS04 não aceita automaticamente bound parcial de LP interrompido.
            self.lp_dual_bound = None
        else:
            self.lp_opt_value = self.lp_dual_bound = None
            if not self.model_complete or self.status not in ('OPTIMAL_NUMERIC', 'TIME_LIMIT'):
                self.mip_numeric_bound = self.mip_numeric_incumbent = None
            if self.status not in ('OPTIMAL_NUMERIC', 'TIME_LIMIT'):
                self.physical_validated_ub = None
                self.installed = None
        if self.physical_validated_ub is not None:
            if (self.mip_numeric_incumbent is None or
                    abs(self.mip_numeric_incumbent - self.physical_validated_ub) > 1e-5):
                raise ValueError('UB física e objetivo MIP devem coincidir')
            if (self.mode != 'MIP' or self.arm_id == 'CORE_IP' or
                    self.installed is None or len(set(self.installed)) != len(self.installed) or
                    self.physical_validated_ub != len(self.installed)):
                raise ValueError('UB física exige instalação não repetida e validada')
        if self.rational_verified_lb_exact is not None or self.rational_verifier_id is not None:
            raise ValueError('AS04 não fabrica certificados racionais; usar verificador externo FC-03')
        if self.status in CENSORED or self.status == 'NO_INCUMBENT':
            self.lp_opt_value = self.lp_dual_bound = None
            self.mip_numeric_bound = self.mip_numeric_incumbent = None
            self.physical_validated_ub = None
            self.installed = None
        for fieldname in ('lp_opt_value', 'lp_dual_bound', 'mip_numeric_bound',
                          'mip_numeric_incumbent', 'solver_runtime_s', 'solver_work',
                          'nodes', 'input_load_s', 'reachability_s'):
            x = getattr(self, fieldname)
            if x is not None and number(x) is None:
                raise ValueError(f'Medida não finita: {fieldname}')
        if self.arm_id == 'U' and self.applied_k_sha256 is not None:
            raise ValueError('U é WITHOUT_K')
        if self.arm_id not in ('U', 'CORE_IP') and self.model_complete and not self.k_validated:
            raise ValueError('+K não pode ser completo com K não validado')
        if self.model_complete and self.arm_id not in ('U', 'CORE_IP') and not self.applied_k_sha256:
            raise ValueError('Hash de K obrigatório')
        if self.wall_total_s is not None and (number(self.wall_total_s) is None or self.wall_total_s < 0):
            raise ValueError('Tempo total inválido')
        if any(number(x) is None or x < 0 for x in self.wall_phases_s.values()):
            raise ValueError('Tempo de fase inválido')
        if self.mode == 'LP' and self.lp_opt_value is not None:
            self.evidence_class = 'SOLVER_NUMERIC_LP_OPTIMAL'
        elif self.mode == 'MIP' and self.mip_numeric_bound is not None:
            self.evidence_class = 'SOLVER_NUMERIC_MIP_BOUND'

    def to_dict(self):
        result = asdict(self)
        result['schema'] = SCHEMA
        result['k_policy'] = 'WITHOUT_K' if self.arm_id == 'U' else 'WITH_K'
        result['rational_certification'] = 'NOT_CERTIFIED'
        result['physical_ub_status'] = ('UB_PHYSICAL_VALIDATED' if self.physical_validated_ub is not None
                                        else 'NOT_VALIDATED')
        return result
