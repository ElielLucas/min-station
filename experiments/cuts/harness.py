"""
Harness compartilhado para experimentos E0, E1', E1.

Fornece:
  - add_cuts_to_model(): adiciona C1/C2/C4/C3 ao modelo Gurobi
  - measure_lp():   LP puro com C3 iterativo opcional
  - measure_root(): limitante da raiz com parâmetros configuráveis
  - run_config():   executa as três medidas para uma configuração
"""

import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))   # baseline.py, ms_utils.py
sys.path.insert(0, str(HERE))   # cuts.py (mesmo diretório)

from gurobipy import GRB, quicksum
from baseline import construir_modelo_baseline
from ms_utils import construir_adjacencia, construir_arcos_alcance
from cuts import (
    build_neighborhoods,
    generate_C1,
    generate_C2,
    generate_C4_DM,
    check_C3_violations,
    assert_valid_cuts,
)


# ── Adição de cortes ao modelo ────────────────────────────────────────────────

def add_cuts_to_model(modelo, y, cuts_specs, validate=None):
    """
    cuts_specs: lista de frozensets de vértices.
    Adiciona  sum_{v in Z} y[v] >= 1  para cada frozenset Z.
    Retorna número de restrições adicionadas.

    validate: opcional, tupla (S, T, A_r). Se dado, cada corte é checado por
    assert_valid_cuts antes de entrar no modelo; um corte inválido aborta
    (CorteInvalido) em vez de ser adicionado em silêncio.
    """
    if validate is not None:
        S, T, A_r = validate
        assert_valid_cuts(S, T, A_r, cuts_specs, origem='add_cuts_to_model')

    n = 0
    for Z in cuts_specs:
        vs = [v for v in Z if v in y]
        if vs:
            modelo.addConstr(quicksum(y[v] for v in vs) >= 1)
            n += 1
    return n


def prepare_cuts(S, T, V, adj, A_r, r, active_cuts):
    """
    Calcula todas as famílias de cortes pedidas (exceto C3, que é iterativo).

    active_cuts: subconjunto de {'C1', 'C2', 'C4'}
    Retorna (lista_de_frozensets_únicos, contagens_por_família)

    counts['unicos'] registra o tamanho após deduplicação entre famílias,
    que pode ser bem menor que a soma bruta (ex.: C1==C2==C4 em hipercubos).
    """
    N_plus, N_minus = build_neighborhoods(A_r)
    all_cuts = []
    counts   = {'C1': 0, 'C2': 0, 'C4': 0}

    if 'C1' in active_cuts:
        c = generate_C1(S, T, N_plus, N_minus)
        all_cuts += c
        counts['C1'] = len(c)

    if 'C2' in active_cuts:
        c = generate_C2(S, T, adj, r, V)
        all_cuts += c
        counts['C2'] = len(c)

    if 'C4' in active_cuts:
        c = generate_C4_DM(S, T, N_plus, N_minus)
        all_cuts += c
        counts['C4'] = len(c)

    all_cuts = list({frozenset(Z) for Z in all_cuts})
    counts['unicos'] = len(all_cuts)

    return all_cuts, counts


# ── Medições ──────────────────────────────────────────────────────────────────

def _make_mip(S, T, V, A_r, f_type, upfront_cuts, y_dict_ref=None):
    """
    Constrói um modelo MIP limpo e adiciona os cortes a priori.
    Retorna (modelo, y, f, n_cuts_added).
    """
    modelo, y, f, _, _ = construir_modelo_baseline(S, T, V, A_r)
    modelo.Params.OutputFlag = 0

    if f_type == 'cont':
        for var in modelo.getVars():
            if var.VarName.startswith('f['):
                var.vtype = GRB.CONTINUOUS
        modelo.update()

    n = add_cuts_to_model(modelo, y, upfront_cuts)
    modelo.update()
    return modelo, y, f, n


def measure_lp(S, T, V, A_r, f_type, upfront_cuts, use_c3=False,
               c3_max_rounds=30, seed=42, threads=1):
    """
    Resolve a relaxação LP do modelo com os cortes a priori.
    Se use_c3=True, itera separação de C3 até convergência.

    Retorna dict com: lp_bound, n_c3_cuts, n_c3_rounds, time_s.
    """
    modelo, y, f, _ = _make_mip(S, T, V, A_r, f_type, upfront_cuts)
    lp = modelo.relax()
    lp.Params.OutputFlag = 0
    lp.Params.Seed       = seed
    lp.Params.Threads    = threads

    t0       = time.monotonic()
    n_c3     = 0
    n_rounds = 0

    if use_c3:
        for _ in range(c3_max_rounds):
            lp.optimize()
            if lp.Status != GRB.OPTIMAL:
                break
            y_star = {}
            for var in lp.getVars():
                nm = var.VarName
                if nm.startswith('y[') and nm.endswith(']'):
                    v = nm[2:-1]
                    y_star[v] = var.X
            viols = check_C3_violations(S, T, A_r, y_star)
            n_rounds += 1
            if not viols:
                break
            for Z in viols:
                vs = [v for v in Z if lp.getVarByName(f'y[{v}]') is not None]
                if vs:
                    lp.addConstr(quicksum(lp.getVarByName(f'y[{v}]') for v in vs) >= 1)
                    n_c3 += 1

    lp.optimize()
    t1 = time.monotonic()

    lp_bound = lp.ObjVal if lp.Status == GRB.OPTIMAL else None
    return {
        'lp_bound':    lp_bound,
        'lp_status':   lp.Status,
        'n_c3_cuts':   n_c3,
        'n_c3_rounds': n_rounds,
        'time_lp_s':   t1 - t0,
    }


def measure_root(S, T, V, A_r, f_type, upfront_cuts, gurobi_cuts=-1,
                 presolve=-1, seed=42, threads=1, time_limit=300):
    """
    Resolve o MIP até a raiz da árvore B&B (NodeLimit=0).

    gurobi_cuts=-1 → padrão; gurobi_cuts=0 → desabilitado.
    Retorna dict com: root_bound, root_ub, root_status, time_s.
    """
    modelo, y, f, _ = _make_mip(S, T, V, A_r, f_type, upfront_cuts)
    modelo.Params.OutputFlag = 0
    modelo.Params.Seed       = seed
    modelo.Params.Threads    = threads
    modelo.Params.TimeLimit  = time_limit
    modelo.Params.NodeLimit  = 0
    modelo.Params.Cuts       = gurobi_cuts
    modelo.Params.Presolve   = presolve

    t0 = time.monotonic()
    modelo.optimize()
    t1 = time.monotonic()

    status = modelo.Status
    try:
        root_bound = float(modelo.ObjBound)
    except Exception:
        root_bound = None
    try:
        root_ub = float(modelo.ObjVal) if modelo.SolCount > 0 else None
    except Exception:
        root_ub = None

    return {
        'root_bound':  root_bound,
        'root_ub':     root_ub,
        'root_status': status,
        'time_root_s': t1 - t0,
    }


def measure_mip(S, T, V, A_r, f_type, upfront_cuts, seed=42, threads=1, time_limit=1200,
                y_start=None):
    """
    Resolve o MIP completo até otimalidade (ou time_limit).
    Usado em E0 para validar BASE-I == BASE-C.

    y_start: dict opcional v -> 0/1 passado como MIP start só nas variáveis y
    (o Gurobi completa f). Permite dar ao compacto o mesmo start dos métodos
    em espaço-y.
    """
    modelo, y, f, _ = _make_mip(S, T, V, A_r, f_type, upfront_cuts)
    modelo.Params.OutputFlag = 0
    modelo.Params.Seed       = seed
    modelo.Params.Threads    = threads
    modelo.Params.TimeLimit  = time_limit
    if y_start is not None:
        for v in V:
            y[v].Start = y_start.get(v, 0.0)
        modelo.update()

    t0 = time.monotonic()
    modelo.optimize()
    t1 = time.monotonic()

    status = modelo.Status
    try:
        obj = float(modelo.ObjVal) if modelo.SolCount > 0 else None
    except Exception:
        obj = None
    try:
        bound = float(modelo.ObjBound)
    except Exception:
        bound = None
    try:
        gap = float(modelo.MIPGap) if modelo.SolCount > 0 else None
    except Exception:
        gap = None

    return {
        'mip_obj':    obj,
        'mip_bound':  bound,
        'mip_gap':    gap,
        'mip_status': status,
        'sol_count':  modelo.SolCount,
        'time_mip_s': t1 - t0,
    }


# ── Configuração de instância ─────────────────────────────────────────────────

def load_instance(path, R=None):
    """
    Carrega instância .txt. Retorna (S, T, V, adj, A_r, r).

    R: opcional, sobrescreve o campo R do arquivo (para reproduzir a
    autonomia das referências históricas, que difere do R gravado em
    algumas instâncias). Sem override, preserva o valor do arquivo sem
    truncar: R=2.5 no arquivo continua 2.5, não vira 2.
    """
    from ms_utils import ler_instancia
    dados = ler_instancia(str(path))
    S    = dados['S']
    T    = dados['T']
    V    = dados['V']
    r_val = float(dados['R'] if R is None else R)
    r    = int(r_val) if r_val.is_integer() else r_val
    adj  = construir_adjacencia(dados['E'])
    A_r  = construir_arcos_alcance(V, adj, r)
    return S, T, V, adj, A_r, r
