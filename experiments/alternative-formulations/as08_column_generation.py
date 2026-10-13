"""AS08/T3 — RMP de B+K com geração simultânea de linhas e colunas.

Apenas relaxação LP (não branch-and-price). Não confundir o objetivo do RMP
com limite inferior global. Certificado global racional deriva de um dual
viável do mestre completo com custos reduzidos verificados por pricing exato.
"""
from __future__ import annotations

import math
import time
from dataclasses import dataclass, asdict
from fractions import Fraction
from typing import Iterable, Callable

from as02_model_a import Instance, _Compiler, _cuts, _validated_instance
from as08_pricing import PricingGraph, iter_price, prepare_pricing


SELECTIONS = ('global', 'per_source', 'matching')


@dataclass(frozen=True)
class CGConfig:
    backend: str = 'scipy-highs'
    seconds: float = 90.0
    iterations: int = 150
    max_columns: int = 10_000
    max_rows: int = 60_000
    per_round: int = 200
    threads: int = 1
    seed: int = 42
    tolerance: float = 1e-7
    rational_certificate: bool = True
    # Ordem de aceitação das colunas negativas (ver `selection_order`). Só
    # decide QUAIS colunas entram; nunca substitui o pricing exato completo.
    selection: str = 'global'
    progress_interval_s: float = 10.0
    # AS-08/LB: certificados intermediários opcionais; comportamento v2 permanece
    # idêntico quando every=0. São limites GLOBAIS após pricing racional completo.
    intermediate_cert_every: int = 0
    intermediate_cert_budget_s: float = 15.0
    intermediate_cert_min_remaining_s: float = 20.0
    intermediate_cert_max_attempts: int = 3

    def validate(self):
        if self.backend not in ('scipy-highs', 'gurobi'):
            raise ValueError('backend desconhecido')
        if not math.isfinite(self.seconds) or self.seconds <= 0 or self.iterations < 1:
            raise ValueError('limites de tempo/iterações inválidos')
        if any(x < 1 for x in (self.max_columns, self.max_rows, self.per_round, self.threads)):
            raise ValueError('caps devem ser positivos')
        if not 0 < self.tolerance < 1e-3:
            raise ValueError('tolerância fora dos limites seguros')
        if self.selection not in SELECTIONS:
            raise ValueError('estratégia de seleção desconhecida')
        if not self.progress_interval_s > 0:
            raise ValueError('intervalo de progresso inválido')
        if (self.intermediate_cert_every < 0 or self.intermediate_cert_max_attempts < 0
            or not math.isfinite(self.intermediate_cert_budget_s)
            or self.intermediate_cert_budget_s <= 0
            or not math.isfinite(self.intermediate_cert_min_remaining_s)
            or self.intermediate_cert_min_remaining_s <= 0):
            raise ValueError('política de certificados intermediários inválida')
        if self.intermediate_cert_every and not self.rational_certificate:
            raise ValueError('certificação intermediária requer rational_certificate=True')


@dataclass
class RMPResult:
    status: str
    objective: float | None
    pi: dict
    tau: dict
    gamma: dict
    mu: dict
    theta: dict
    y: dict
    paths_x: dict
    artificial_sum: float | None
    vars: int
    rows: int
    nnz: int
    solver_wall_s: float
    solver_version: str


def rmp_row_counts(instance: Instance, K, b3_pairs) -> dict:
    """Linhas que `compile_rmp` cria, por família, sem montar o modelo.

    B1=|S|, B2=|T|, B3=pares (origem, vértice interno) DISTINTOS tocados pelas
    colunas, B4=|T\\S|, BK=|K| (K já canônico). Cada par B3 é uma linha só,
    não importa quantos caminhos o compartilhem.
    """
    counts = {'B1': len(instance.S), 'B2': len(instance.T), 'B3': len(b3_pairs),
              'B4': len(set(instance.T) - set(instance.S)), 'BK': len(K)}
    counts['total'] = sum(counts.values())
    return counts


def b3_pairs_of(path: tuple[str, ...]) -> set:
    return {(path[0], v) for v in path[1:-1]}


def compile_rmp(instance: Instance, K: Iterable[Iterable[str]], columns: Iterable[tuple[str, ...]],
                *, penalty: float | None = None, graph: PricingGraph | None = None):
    """Master restrito sempre viável por a_s,b_t. B3 somente para pares tocados.

    A variável artificial pertence APENAS ao RMP e é retirada de toda
    interpretação de viabilidade, bound e resultado final de B.
    `graph` (já validado por `prepare_pricing`) evita revalidar a instância
    a cada iteração; o modelo produzido é o mesmo.
    """
    if graph is None:
        _validated_instance(instance)
        arcs = set(instance.A_r)
    elif graph.instance is not instance:
        raise ValueError('grafo de pricing pertence a outra instância')
    K = _cuts(instance.V, K)
    m = len(instance.S)
    P = float(penalty if penalty is not None else 10*(len(instance.V)+1))
    if not math.isfinite(P) or P <= len(instance.V):
        raise ValueError('penalidade artificial precisa superar o custo máximo de instalações')
    cols = tuple(sorted(set(tuple(p) for p in columns)))
    aset, tset = set(instance.S), set(instance.T)
    vertset = graph.V if graph is not None else set(instance.V)
    has_arc = ((lambda u, v: (u, v) in arcs) if graph is None
               else (lambda u, v: v in graph.adjacency[u]))
    for p in cols:
        if not p or p[0] not in aset or p[-1] not in tset or len(set(p)) != len(p) or any(v not in vertset for v in p):
            raise ValueError('coluna com origem, destino ou caminho simples inválido')
        if any(not has_arc(u, v) for u, v in zip(p, p[1:])):
            raise ValueError('coluna usa arco inexistente')
    c = _Compiler()
    y = {v: c.var(('y', v), 'y[' + v + ']', ub=1) for v in instance.V}
    # Não incluir o caminho inteiro no nome exportado ao solver: o Gurobi
    # limita nomes a 255 caracteres. A chave ('x', caminho) continua íntegra
    # em compiled.columns, preservando a rastreabilidade matemática.
    x = {p: c.var(('x', p), f'x[{i}]') for i, p in enumerate(cols)}
    ass = {s: c.var(('a_s', s), 'a_s[' + s + ']') for s in instance.S}
    ats = {t: c.var(('a_t', t), 'a_t[' + t + ']') for t in instance.T}
    c.objective = {**{j: 1. for j in y.values()},
                   **{j: P for j in (*ass.values(), *ats.values())}}
    # Índices em uma passada sobre as colunas (antes: uma varredura por linha).
    by_source, by_target, internal, touching = {}, {}, {}, {}
    for p in cols:
        term = (x[p], 1)
        by_source.setdefault(p[0], []).append(term)
        by_target.setdefault(p[-1], []).append(term)
        for v in p[1:-1]:
            touching.setdefault((p[0], v), []).append(term)
            internal.setdefault(v, []).append(term)
    for s in instance.S:
        c.row('B1', 'B1[' + s + ']', by_source.get(s, []) + [(ass[s], 1)], '==', 1)
    for t in instance.T:
        c.row('B2', 'B2[' + t + ']', by_target.get(t, []) + [(ats[t], 1)], '==', 1)
    for (s, v) in sorted(touching):
        c.row('B3', f'B3[{s},{v}]', touching[s, v] + [(y[v], -1)], '<=', 0)
    # B4 só em T\\S; sua redundância fora disso foi provada em T1.
    for v in instance.T:
        if v not in aset:
            c.row('B4', f'B4[{v}]', internal.get(v, []) + [(y[v], -(m - 1))], '<=', 0)
    for j, cut in enumerate(K):
        c.row('BK', f'BK[{j}]', [(y[v], 1) for v in sorted(cut)], '>=', 1)
    return c.output(), K


def _solve(compiled, instance, K, config: CGConfig, *, seconds: float) -> RMPResult:
    """Duais para LINHAS ORIGINAIS: Pi<=0 em <=, Pi>=0 em >= (min)."""
    started = time.monotonic()
    if config.backend == 'scipy-highs':
        import numpy as np
        from scipy.optimize import linprog
        from scipy.sparse import coo_matrix
        n = len(compiled.variables)
        indices = {'eq': ([], [], [], []), 'ub': ([], [], [], [])}
        rhs = {'eq': [], 'ub': []}
        rowkeys = {'eq': [], 'ub': []}
        for row in compiled.equations:
            kind = 'eq' if row.sense == '==' else 'ub'
            sign = -1.0 if row.sense == '>=' else 1.0
            idx = len(rhs[kind])
            rhs[kind].append(sign*row.rhs)
            rowkeys[kind].append((row.name, sign))
            for j, coeff in row.terms:
                indices[kind][0].append(idx)
                indices[kind][1].append(j)
                indices[kind][2].append(sign*coeff)
        matrices = {k: coo_matrix((v[2], (v[0], v[1])), shape=(len(rhs[k]),n)).tocsr()
                    for k, v in indices.items()}
        costs = np.zeros(n)
        for j, coeff in compiled.objective.items():
            costs[j] = coeff
        res = linprog(costs, A_ub=matrices['ub'], b_ub=rhs['ub'],
                      A_eq=matrices['eq'], b_eq=rhs['eq'],
                      bounds=[(v.lb, None if math.isinf(v.ub) else v.ub) for v in compiled.variables],
                      method='highs', options={'time_limit': max(0.001, seconds),
                                                'primal_feasibility_tolerance': config.tolerance,
                                                'dual_feasibility_tolerance': config.tolerance})
        if res.status != 0:
            return RMPResult('TIME_LIMIT' if res.status == 1 else 'INFEASIBLE' if res.status == 2 else 'SOLVER_ERROR',
                             None, {}, {}, {}, {}, {}, {}, {}, None,
                             n, len(compiled.equations), compiled.n_nonzeros,
                             time.monotonic()-started, 'scipy-highs')
        values = res.x
        marg = {k: {name: float(val)*sgn for (name, sgn), val in zip(rowkeys[k],
                      res.eqlin.marginals if k == 'eq' else res.ineqlin.marginals)} for k in ('eq','ub')}
        solver_version = 'scipy-highs'
    else:
        import gurobipy as gp
        model = gp.Model('AS08-B-RMP')
        model.Params.OutputFlag = 0
        model.Params.Threads = config.threads
        model.Params.Seed = config.seed
        model.Params.TimeLimit = max(0.001, seconds)
        var = [model.addVar(lb=v.lb, ub=v.ub if math.isfinite(v.ub) else gp.GRB.INFINITY,
                            name=v.name) for v in compiled.variables]
        model.setObjective(gp.quicksum(val*var[j] for j, val in compiled.objective.items()), gp.GRB.MINIMIZE)
        rows = {'eq': {}, 'ub': {}}
        for row in compiled.equations:
            expr = gp.quicksum(coef*var[j] for j, coef in row.terms)
            if row.sense == '==':
                con = model.addConstr(expr == row.rhs, name=row.name)
                rows['eq'][row.name] = con
            elif row.sense == '<=':
                con = model.addConstr(expr <= row.rhs, name=row.name)
                rows['ub'][row.name] = con
            else:
                con = model.addConstr(expr >= row.rhs, name=row.name)
                rows['ub'][row.name] = con
        model.optimize()
        if model.Status != gp.GRB.OPTIMAL:
            return RMPResult('TIME_LIMIT' if model.Status == gp.GRB.TIME_LIMIT else 'INFEASIBLE'
                             if model.Status == gp.GRB.INFEASIBLE else 'SOLVER_ERROR',
                             None, {}, {}, {}, {}, {}, {}, {}, None,
                             len(var), len(compiled.equations), compiled.n_nonzeros,
                             time.monotonic()-started, '.'.join(map(str, gp.gurobi.version())))
        values = [v.X for v in var]
        marg = {k: {name: con.Pi for name, con in rows[k].items()} for k in rows}
        solver_version = '.'.join(map(str, gp.gurobi.version()))
    pi = {s: marg['eq'][f'B1[{s}]'] for s in instance.S}
    tau = {t: marg['eq'][f'B2[{t}]'] for t in instance.T}
    gamma, mu, theta = {}, {}, {}
    for (name, value) in marg['ub'].items():
        if name.startswith('B3['):
            # Parse via instâncias fonte: nomes podem conter vírgula? grafos usam IDs simples.
            s, v = name[3:-1].split(',', 1)
            gamma[s, v] = max(0.0, -value)
        elif name.startswith('B4['):
            mu[name[3:-1]] = max(0.0, -value)
        elif name.startswith('BK['):
            theta[int(name[3:-1])] = max(0.0, value)
    xs = {key[1]: float(values[j]) for key, j in compiled.columns.items() if key[0] == 'x'}
    artificials = sum(max(0.0,float(values[j])) for key,j in compiled.columns.items() if key[0] in ('a_s','a_t'))
    return RMPResult('OPTIMAL', float(sum(compiled.objective[j]*values[j] for j in compiled.objective)),
                     pi,tau,gamma,mu,theta,
                     {v:float(values[j]) for (typ,v),j in compiled.columns.items() if typ=='y'},
                     xs, artificials, len(compiled.variables), len(compiled.equations),
                     compiled.n_nonzeros, time.monotonic()-started,solver_version)


def _minimum_reduced_costs(graph: PricingGraph, pi, tau, gamma, mu, deadline=None):
    """Mínimo EXATO do custo reduzido por origem, sem reter caminhos.

    None para origem sem caminho. Retorna None inteiro se o prazo esgotar:
    um mínimo parcial nunca é usado como certificado.
    """
    out = {}
    for s, priced in iter_price(graph, pi, tau, gamma, mu, exact=True):
        out[s] = priced[0].reduced_cost if priced else None
        if deadline is not None and time.monotonic() > deadline:
            return None
    return out


def _dual_objective(instance: Instance, K, pi, tau, gamma, mu, theta, minimal):
    """l(π,τ,γ,μ,θ) com η reparado + Σ_s min(0, custo reduzido mínimo de s)."""
    frac = Fraction
    kappa = {v: len(instance.S)-int(v in instance.S or v in instance.T) for v in instance.V}
    # Agregações em uma passada (antes: |V|·|S| e |V|·|K| consultas).
    gamma_at = {}
    for (s, v), value in gamma.items():
        if s != v:
            gamma_at[v] = gamma_at.get(v, frac(0)) + value
    theta_at = {}
    for j, Z in enumerate(K):
        value = theta.get(j, 0)
        if value:
            for v in Z:
                theta_at[v] = theta_at.get(v, frac(0)) + value
    eta = {v: max(frac(0), kappa[v]*mu.get(v, 0) + gamma_at.get(v, frac(0))
                  + theta_at.get(v, frac(0)) - 1) for v in instance.V}
    l = (sum(pi.values(), frac(0)) + sum(tau.values(), frac(0))
         + sum(theta.values(), frac(0)) - sum(eta.values(), frac(0)))
    correction = sum((min(frac(0), v) for v in minimal.values()), frac(0))
    return max(frac(0), l+correction), correction


def certified_bound(instance: Instance, K, dual: RMPResult, *, graph: PricingGraph | None = None,
                    deadline: float | None = None):
    """Reconstrói dual FEASÍVEL exato sobre TODAS as colunas não enumeradas.

    Float do Gurobi/HiGHS vira Fraction(decimal), preços/rhs são racionais.
    O resultado NÃO é apenas aproximação do objetivo do RMP. A validade da
    família K para o problema físico permanece condição externa.
    """
    if dual.status != 'OPTIMAL':
        raise ValueError('certificado exige RMP resolvido')
    conv = lambda value: Fraction(str(float(value)))
    pi = {s:conv(dual.pi[s]) for s in instance.S}
    tau = {t:conv(dual.tau[t]) for t in instance.T}
    gamma = {k:max(Fraction(0),conv(v)) for k,v in dual.gamma.items()}
    mu = {k:max(Fraction(0),conv(v)) for k,v in dual.mu.items()}
    theta = {j:max(Fraction(0),conv(v)) for j,v in dual.theta.items()}
    minimal = _minimum_reduced_costs(graph or prepare_pricing(instance), pi, tau, gamma, mu, deadline)
    if minimal is None:
        return {'status':'CERTIFICATE_TIMEOUT','lower_bound':None,'rational':None,
                'reason':'prazo esgotado durante o pricing exato; nenhum limite emitido'}
    if any(v is None for v in minimal.values()):
        return {'status':'INFEASIBLE_SUPPORT','lower_bound':None,'rational':None,
                'reason':'origem sem caminho; limite dual não construído'}
    K = _cuts(instance.V,K)
    bound, correction = _dual_objective(instance, K, pi, tau, gamma, mu, theta, minimal)
    return {'status':'CERTIFIED_RATIONAL_DUAL', 'lower_bound':float(bound),
            'duals':{'pi':{s:str(v) for s,v in pi.items()},
                     'tau':{s:str(v) for s,v in tau.items()},
                     'gamma':[[s,v,str(value)] for (s,v),value in sorted(gamma.items())],
                     'mu':{s:str(v) for s,v in mu.items()},
                     'theta':{str(j):str(v) for j,v in theta.items()}},
            'rational':f'{bound.numerator}/{bound.denominator}',
            'minimum_reduced_costs':{s:float(v) for s,v in minimal.items()},
            'negative_count':sum(v<0 for v in minimal.values()),
            'dual_correction':float(correction),
            'scope':'LP(B+K) completo; K presumido válido e idêntico ao comparador'}


def selection_order(kept: dict, strategy: str):
    """Ordem determinística em que as colunas negativas são oferecidas ao RMP.

    `kept[s]` já vem em ordem (custo reduzido, destino). Desempate global por
    (custo, origem, destino), total porque há um preço por par (s,t).
    - global: menor custo reduzido primeiro (comportamento anterior);
    - per_source: rodízio por posto — a melhor de cada origem, depois a
      segunda de cada origem, ...;
    - matching: passadas sucessivas; em cada passada, no máximo uma coluna
      por origem E por destino (emparelhamento guloso pelo custo).
    É gerador: o consumidor para assim que a cota da rodada enche.
    """
    key = lambda p: (p.reduced_cost, p.source, p.target)
    if strategy == 'global':
        yield from sorted((p for group in kept.values() for p in group), key=key)
    elif strategy == 'per_source':
        depth = max((len(g) for g in kept.values()), default=0)
        for k in range(depth):
            yield from sorted((g[k] for g in kept.values() if len(g) > k), key=key)
    elif strategy == 'matching':
        remaining = sorted((p for group in kept.values() for p in group), key=key)
        while remaining:
            used_s, used_t, rest = set(), set(), []
            for p in remaining:
                if p.source in used_s or p.target in used_t:
                    rest.append(p)
                else:
                    used_s.add(p.source)
                    used_t.add(p.target)
                    yield p
            remaining = rest
    else:
        raise ValueError('estratégia de seleção desconhecida')


def select_columns(order, *, limit: int, row_room: int, b3_pairs: set):
    """Aceita colunas na ordem dada respeitando EXATAMENTE os caps.

    `limit` = vagas de colunas na rodada; `row_room` = linhas B3 novas que
    ainda cabem em max_rows. Uma coluna que criaria linhas além do cap é
    pulada (contada em `row_blocked`), não interrompe a rodada.
    """
    selected, new_pairs, row_blocked = [], set(), 0
    if limit <= 0:
        return selected, new_pairs, row_blocked
    for p in order:
        extra = b3_pairs_of(p.path) - b3_pairs - new_pairs
        if len(new_pairs) + len(extra) > row_room:
            row_blocked += 1
            continue
        selected.append(p)
        new_pairs |= extra
        if len(selected) >= limit:
            break
    return selected, new_pairs, row_blocked


def run_column_generation(instance: Instance, K=(), *, config: CGConfig | None=None,
                          progress: Callable[[dict], None] | None = None):
    config = config or CGConfig()
    config.validate()
    started = time.monotonic()
    deadline = started + config.seconds
    graph = prepare_pricing(instance)
    K = _cuts(instance.V,K)
    columns: set[tuple[str,...]] = set()
    b3_pairs: set = set()
    iterations = []
    best_cert = None
    intermediate_cert_attempts = 0
    intermediate_cert_successes = 0
    first_feasible_cert_attempted = False
    feasible_upper = None
    stop = 'NOT_STARTED'
    stop_detail = {}
    last = None
    stage = 'SETUP'

    def report(event: str, **details):
        # Só informações agregadas: não confundir objetivo do RMP com LB global.
        if progress is not None:
            progress({'schema':'AS08-CG-PROGRESS-v1','event':event,
                      'elapsed_seconds':time.monotonic()-started,
                      'columns':len(columns),'completed_iterations':len(iterations),
                      'certified_global_lb':best_cert['lower_bound'] if best_cert else None,
                      **details})

    def finish(reason: str, **detail):
        nonlocal stop, stop_detail
        stop = reason
        stop_detail = {'reason':reason,'stage':stage,**detail}

    report('CG_STARTED', planned_iterations=config.iterations,
           budget_seconds=config.seconds, selection=config.selection,
           max_columns=config.max_columns, max_rows=config.max_rows,
           per_round=config.per_round, setup_seconds=time.monotonic()-started)
    for step in range(1, config.iterations+1):
        stage = 'BUILD_RMP'
        if time.monotonic() >= deadline:
            finish('TIME_LIMIT')
            break
        row_counts = rmp_row_counts(instance, K, b3_pairs)
        if row_counts['total'] > config.max_rows:
            # Só ocorre se as linhas-base (sem colunas) já excedem o cap.
            finish('CAP_EXCEEDED', limit='max_rows', observed=row_counts['total'],
                   configured=config.max_rows)
            break
        report('BUILD_RMP', iteration=step, rmp_rows_predicted=row_counts['total'])
        t0 = time.monotonic()
        compiled,_ = compile_rmp(instance, K, columns, graph=graph)
        build_s = time.monotonic()-t0
        if len(compiled.equations) != row_counts['total']:
            raise RuntimeError('contagem de linhas do RMP divergiu do modelo compilado')
        stage = 'SOLVING_RMP'
        report('SOLVING_RMP', iteration=step, rmp_rows=len(compiled.equations),
               rmp_row_families=row_counts, rmp_variables=len(compiled.variables),
               rmp_nnz=compiled.n_nonzeros, build_seconds=build_s)
        t0 = time.monotonic()
        try:
            last = _solve(compiled,instance,K,config,seconds=max(.001,deadline-time.monotonic()))
        except (ImportError, ModuleNotFoundError) as ex:
            stop = 'SOLVER_UNAVAILABLE'
            return {'status':stop,'reason':str(ex),'global_lower_bound':None,
                    'rmp_objective':None,'iterations':iterations,'columns':len(columns)}
        rmp_s = time.monotonic()-t0
        if last.status != 'OPTIMAL':
            report('RMP_NOT_OPTIMAL', iteration=step, rmp_status=last.status,
                   solve_seconds=last.solver_wall_s)
            finish('RMP_'+last.status)
            break
        if last.artificial_sum is not None and last.artificial_sum <= config.tolerance:
            # RMP com artificiais nulas fornece solução viável do mestre completo
            # (em aritmética numérica): upper bound para LP, NÃO para IP.
            feasible_upper = sum(last.y.values())
        current = {'iter':step,'rmp_objective_with_artificials':last.objective,
                   'artificial_sum':last.artificial_sum,'columns':len(columns),
                   'rows':last.rows,'nnz':last.nnz,'solve_s':last.solver_wall_s,
                   'build_s':build_s,'rmp_total_s':rmp_s,
                   'physical_lp_ub':feasible_upper,'global_lower_bound':None}
        report('RMP_SOLVED', iteration=step, rmp_status=last.status,
               rmp_objective_with_artificials=last.objective,
               artificial_sum=last.artificial_sum,
               feasible_lp_upper_bound=feasible_upper,
               rmp_rows=last.rows, rmp_nnz=last.nnz, solve_seconds=last.solver_wall_s,
               rmp_total_seconds=rmp_s)
        if time.monotonic() >= deadline:
            iterations.append(current)
            finish('TIME_LIMIT')
            break
        # Pricing FLOAT EXATO sobre todas as origens (sem pricing parcial):
        # escolhe colunas; o certificado é recalculado em modo racional.
        stage = 'PRICING'
        report('PRICING', iteration=step, origins_total=len(instance.S))
        t0 = tick = last_emit = time.monotonic()
        kept, negatives, duplicates, processed = {}, 0, 0, 0
        slowest, no_path, timed_out = (0.0, None), None, False
        for s, priced in iter_price(graph,last.pi,last.tau,last.gamma,last.mu,exact=False):
            if not priced:
                no_path = s
                break
            group = []
            for p in priced:
                if p.reduced_cost >= -config.tolerance:
                    break
                negatives += 1
                # A cota por origem nunca supera per_round: nenhuma estratégia
                # aceitaria mais que isso de uma única origem na rodada.
                if len(group) < config.per_round:
                    if p.path in columns:
                        duplicates += 1
                    else:
                        group.append(p)
            if group:
                kept[s] = group
            processed += 1
            now = time.monotonic()
            if now-tick > slowest[0]:
                slowest = (now-tick, s)
            tick = now
            if now >= deadline:
                timed_out = True
                break
            if now-last_emit >= config.progress_interval_s:
                last_emit = now
                report('PRICING_PROGRESS', iteration=step, origins_processed=processed,
                       origins_total=len(instance.S), negative_candidates_so_far=negatives,
                       pricing_seconds=now-t0)
        pricing_s = time.monotonic()-t0
        current.update({'pricing_s':pricing_s,'origins_processed':processed,
                        'pricing_slowest_origin_s':slowest[0],
                        'pricing_slowest_origin':slowest[1],
                        'pricing_mean_origin_s':pricing_s/processed if processed else None,
                        'negative_candidate_count':negatives,
                        'negative_duplicate_columns':duplicates,
                        'origins_with_candidates':len(kept)})
        if no_path is not None:
            iterations.append(current)
            finish('NO_PATH_FOR_ORIGIN', origin=no_path)
            break
        if timed_out:
            iterations.append(current)
            finish('TIME_LIMIT', origins_processed=processed, origins_total=len(instance.S))
            report('PRICING_INTERRUPTED', iteration=step, origins_processed=processed,
                   origins_total=len(instance.S), pricing_seconds=pricing_s)
            break
        report('PRICING_FINISHED', iteration=step, negative_candidates=negatives,
               origins_processed=processed, origins_with_candidates=len(kept),
               negative_duplicate_columns=duplicates, pricing_seconds=pricing_s,
               pricing_slowest_origin_seconds=slowest[0])
        # AS-08/LB: demonstrar potencial matemático ANTES da convergência.
        # O pricing de seleção acima é float; o certificado executa novamente
        # TODAS as origens em Fraction. Resultado parcial não vira bound.
        is_feasible_now = (last.artificial_sum is not None
                           and last.artificial_sum <= config.tolerance)
        first_feasible_due = is_feasible_now and not first_feasible_cert_attempted
        periodic_due = (config.intermediate_cert_every > 0
                        and step % config.intermediate_cert_every == 0)
        should_try = (bool(kept) and config.rational_certificate
                      and config.intermediate_cert_every > 0
                      and intermediate_cert_attempts < config.intermediate_cert_max_attempts
                      and (periodic_due or first_feasible_due))
        if should_try:
            available = deadline - time.monotonic()
            if available >= config.intermediate_cert_min_remaining_s:
                stage = 'CERTIFYING_INTERMEDIATE'
                cert_deadline = min(deadline - 1.0,
                                    time.monotonic() + config.intermediate_cert_budget_s)
                intermediate_cert_attempts += 1
                if first_feasible_due:
                    first_feasible_cert_attempted = True
                report('INTERMEDIATE_CERT_STARTED', iteration=step,
                       attempted=intermediate_cert_attempts,
                       cert_budget_seconds=config.intermediate_cert_budget_s)
                tcert = time.monotonic()
                cert = certified_bound(instance, K, last, graph=graph,
                                       deadline=cert_deadline)
                cert_elapsed = time.monotonic() - tcert
                current['intermediate_cert_s'] = cert_elapsed
                current['intermediate_cert_status'] = cert['status']
                improved = False
                if cert['status'] == 'CERTIFIED_RATIONAL_DUAL':
                    intermediate_cert_successes += 1
                    # Comparar os certificados como racionais, não como floats.
                    if (best_cert is None or
                            Fraction(cert['rational']) > Fraction(best_cert['rational'])):
                        best_cert = cert
                        current['global_lower_bound'] = cert['lower_bound']
                        improved = True
                        # Evento completo é necessário para recuperar o
                        # certificado se o supervisor encerrar o worker.
                        # O driver registra o payload separadamente do log.
                        report('INTERMEDIATE_CERT_IMPROVED', iteration=step,
                               certified_global_lb=cert['lower_bound'],
                               certified_global_lb_rational=cert['rational'],
                               dual_correction=cert['dual_correction'],
                               certificate=cert)
                report('INTERMEDIATE_CERT_FINISHED', iteration=step,
                       status=cert['status'], improved=improved,
                       cert_seconds=cert_elapsed,
                       certified_global_lb=best_cert['lower_bound'] if best_cert else None)
            else:
                report('INTERMEDIATE_CERT_SKIPPED', iteration=step,
                       remaining_seconds=max(0., available), reason='insufficient_budget')
        # Certificar na última iteração se sem candidato; não aceitar pricing
        # aproximado como certificado global nem objetivo do mestre restrito.
        if not kept:
            stage = 'CERTIFYING'
            if config.rational_certificate:
                if time.monotonic() < deadline:
                    report('CERTIFYING', iteration=step)
                    t0 = time.monotonic()
                    exact = certified_bound(instance,K,last,graph=graph,deadline=deadline)
                    current['certify_s'] = time.monotonic()-t0
                    if time.monotonic() <= deadline and exact['status']=='CERTIFIED_RATIONAL_DUAL':
                        if (best_cert is None or
                                Fraction(exact['rational']) > Fraction(best_cert['rational'])):
                            best_cert = exact
                        current['global_lower_bound']=best_cert['lower_bound']
                        report('FINAL_CERTIFIED', iteration=step,
                               certified_global_lb=best_cert['lower_bound'],
                               certificate=best_cert)
                    else:
                        finish('CERTIFICATE_TIMEOUT_OR_INFEASIBLE', certificate_status=exact['status'])
                else:
                    finish('TIME_LIMIT')
            else:
                finish('NO_GLOBAL_LB_CERTIFICATE_DISABLED')
            if not stop.startswith(('CERTIFICATE_','TIME_LIMIT','NO_GLOBAL_')):
                tolerance_gap=max(1e-6,config.tolerance*max(1.0,abs(feasible_upper or 0.0)))
                finish('CONVERGED' if (best_cert is not None and last.artificial_sum <= config.tolerance
                       and feasible_upper is not None
                       and abs(best_cert['lower_bound']-feasible_upper)<=tolerance_gap)
                       else 'UNCERTIFIED_LP_OPTIMALITY' if best_cert is not None and feasible_upper is not None
                       else 'NO_FEASIBLE_MASTER')
            iterations.append(current)
            break
        stage = 'SELECTING'
        t0 = time.monotonic()
        col_room = config.max_columns-len(columns)
        row_room = config.max_rows-row_counts['total']
        selected, new_pairs, row_blocked = select_columns(
            selection_order(kept, config.selection), limit=min(col_room, config.per_round),
            row_room=row_room, b3_pairs=b3_pairs)
        current.update({'selection_s':time.monotonic()-t0,'added_columns':len(selected),
                        'added_rows':len(new_pairs),'row_blocked_candidates':row_blocked,
                        'selected_origins':len({p.source for p in selected}),
                        'selected_targets':len({p.target for p in selected})})
        if not selected:
            iterations.append(current)
            if col_room <= 0:
                finish('CAP_EXCEEDED', limit='max_columns', observed=len(columns),
                       configured=config.max_columns, negative_candidates=negatives)
            else:
                finish('CAP_EXCEEDED', limit='max_rows', observed=row_counts['total'],
                       configured=config.max_rows, negative_candidates=negatives,
                       row_blocked_candidates=row_blocked)
            break
        columns.update(p.path for p in selected)
        b3_pairs |= new_pairs
        iterations.append(current)
        report('ITERATION_COMPLETE', iteration=step, added_columns=len(selected),
               added_rows=len(new_pairs), row_blocked_candidates=row_blocked,
               selected_origins=current['selected_origins'],
               selected_targets=current['selected_targets'],
               negative_candidates=negatives,
               rmp_objective_with_artificials=last.objective,
               artificial_sum=last.artificial_sum,
               feasible_lp_upper_bound=feasible_upper,
               iteration_seconds=build_s+rmp_s+pricing_s+current['selection_s'])
    else:
        stage = 'ITERATION_LIMIT'
        finish('ITERATION_LIMIT', configured=config.iterations)
    # Não reutilizar um bound antigo para um RMP novo sem rastrear. Um dual
    # certificado é sempre válido globalmente; um RMP sem solução viável não.
    result = {'schema':'AS08-CG-v2','status':stop,'stop_detail':stop_detail,
              'intermediate_cert_attempts':intermediate_cert_attempts,
              'intermediate_cert_successes':intermediate_cert_successes,
              'rmp_status':last.status if last else None,
              'solver_backend':config.backend,'selection':config.selection,
              'iterations':iterations,
              'n_iterations':len(iterations),'columns':len(columns),
              'rmp_rows_final':rmp_row_counts(instance, K, b3_pairs),
              'rmp_objective':last.objective if last else None,
              'rmp_artificial_sum':last.artificial_sum if last else None,
              'global_lower_bound':best_cert['lower_bound'] if best_cert else None,
              'global_lb_certificate':best_cert,
              'feasible_lp_upper_bound':feasible_upper,
              'bound_semantics':('rmp_objective e feasible_lp_upper_bound são objetivos do '
                                 'mestre RESTRITO: limite SUPERIOR de LP(B+K) quando as '
                                 'artificiais são nulas, NUNCA limite inferior global. '
                                 'Só global_lower_bound (dual racional) é limite inferior.'),
              'elapsed_seconds':time.monotonic()-started,
              'classification':'EXPLORATORY_NOT_SCIENTIFICALLY_HOMOLOGATED'}
    report('CG_FINISHED', status=stop, stop_detail=stop_detail, n_iterations=len(iterations),
           rmp_objective_with_artificials=last.objective if last else None,
           feasible_lp_upper_bound=feasible_upper,
           certified_global_lb=best_cert['lower_bound'] if best_cert else None)
    if stop=='CONVERGED' and best_cert is not None and feasible_upper is not None:
        result['numeric_primal_dual_gap']=max(0.,feasible_upper-best_cert['lower_bound'])
    return result


def verify_rational_certificate(instance: Instance, K, certificate: dict) -> bool:
    """Audita a identidade do dual racional e os preços de TODOS os destinos.

    Não usa o resultado do solver/RMP; reconstrução com aritmética exata e
    Dijkstra próprio (grafo preparado de novo). A verificação da validade
    física dos cortes K é externa, via AS05.
    """
    if certificate.get('status')!='CERTIFIED_RATIONAL_DUAL':
        raise ValueError('certificado ausente')
    raw=certificate['duals']
    frac=Fraction
    pi={s:frac(v) for s,v in raw['pi'].items()}
    tau={t:frac(v) for t,v in raw['tau'].items()}
    gamma={(s,v):frac(w) for s,v,w in raw['gamma']}
    mu={v:frac(w) for v,w in raw['mu'].items()}
    theta={int(i):frac(w) for i,w in raw['theta'].items()}
    K=_cuts(instance.V,K)
    if (set(pi)!=set(instance.S) or set(tau)!=set(instance.T)
            or any(value<0 for value in (*gamma.values(),*mu.values(),*theta.values()))
            or any(j not in range(len(K)) for j in theta)):
        raise ValueError('duais inválidos')
    minimal=_minimum_reduced_costs(prepare_pricing(instance),pi,tau,gamma,mu)
    if any(v is None for v in minimal.values()):
        raise ValueError('origem sem caminhos, certificado não aplicável')
    bound,_=_dual_objective(instance,K,pi,tau,gamma,mu,theta,minimal)
    if bound!=frac(certificate['rational']):
        raise ValueError('certificado adulterado ou aritmética inconsistente')
    return True
