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
    generate_C6,
    check_C3_violations,
    assert_valid_cuts,
    cortes_ordenados,
    vertices_do_corte,
)


# ── Adição de cortes ao modelo ────────────────────────────────────────────────

def corte_ponderado(corte):
    """Corte C6: ((v, coeficiente), ...), rhs com rhs >= 1."""
    return (
        isinstance(corte, tuple)
        and len(corte) == 2
        and isinstance(corte[0], tuple)
        and isinstance(corte[1], int)
    )


def add_cuts_to_model(modelo, y, cuts_specs, validate=None):
    """
    Cortes unitários (frozenset) viram y(Z) >= 1, na ordem de cortes_ordenados.
    Cortes ponderados (C6) viram soma coeficiente*y >= rhs, ordenados por
    (rhs, coeficientes). Os dois grupos não se misturam na ordenação.

    validate: opcional, tupla (S, T, A_r). Vale só para os cortes unitários.
    """
    unitarios = [c for c in cuts_specs if not corte_ponderado(c)]
    ponderados = [c for c in cuts_specs if corte_ponderado(c)]
    if validate is not None and unitarios:
        S, T, A_r = validate
        assert_valid_cuts(S, T, A_r, unitarios, origem='add_cuts_to_model')

    n = 0
    for Z in cortes_ordenados(unitarios):
        vs = vertices_do_corte(Z, y)
        if vs:
            modelo.addConstr(quicksum(y[v] for v in vs) >= 1)
            n += 1
    for coefs, rhs in sorted(ponderados, key=lambda c: (c[1], c[0])):
        termos = [(coef, y[v]) for v, coef in coefs if v in y and coef]
        if termos:
            modelo.addConstr(quicksum(coef * var for coef, var in termos) >= rhs)
            n += 1
    return n


def prepare_cuts(S, T, V, adj, A_r, r, active_cuts):
    """
    Calcula todas as famílias de cortes pedidas (exceto C3, que é iterativo).

    active_cuts: subconjunto de {'C1', 'C2', 'C4', 'C6'}
    Retorna (lista_de_frozensets_únicos, contagens_por_família)

    C6 não entra na lista unitária: counts['C6_cortes'] traz as desigualdades
    ponderadas, para não passar por cortes_ordenados.

    counts['unicos'] registra o tamanho após deduplicação entre famílias,
    que pode ser bem menor que a soma bruta (ex.: C1==C2==C4 em hipercubos).
    """
    N_plus, N_minus = build_neighborhoods(A_r)
    all_cuts = []
    counts   = {'C1': 0, 'C2': 0, 'C4': 0, 'C6': 0, 'C6_cortes': []}

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

    if 'C6' in active_cuts:
        c6, incompletas = generate_C6(S, T, N_plus, N_minus)
        counts['C6'] = len(c6)
        counts['C6_cortes'] = c6
        counts['C6_incompletas'] = incompletas

    all_cuts = cortes_ordenados(all_cuts)
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
               c3_max_rounds=30, seed=42, threads=1, time_limit=None):
    """
    Resolve a relaxação LP do modelo com os cortes a priori.
    Se use_c3=True, itera separação de C3 até convergência.

    time_limit: opcional, segundos. Sem ele (padrão), sem limite — como
    antes. Com ele, se o LP for interrompido antes da otimalidade (modelo
    degenerado em f com |A_r| grande, ver A2 em direcoes-pli-min-station.md),
    lp_bound continua sendo o ObjVal corrente, mas lp_status registra que não
    é ótimo — não deve ser lido como z_LP provado nesse caso.

    Retorna dict com: lp_bound, lp_status, n_c3_cuts, n_c3_rounds, time_s.
    """
    modelo, y, f, _ = _make_mip(S, T, V, A_r, f_type, upfront_cuts)
    lp = modelo.relax()
    lp.Params.OutputFlag = 0
    lp.Params.Seed       = seed
    lp.Params.Threads    = threads
    if time_limit is not None:
        lp.Params.TimeLimit = time_limit

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
                y_start=None, params=None, coletar_incumbente=False):
    """
    Resolve o MIP completo até otimalidade (ou time_limit).
    Usado em E0 para validar BASE-I == BASE-C.

    y_start: dict opcional v -> 0/1 passado como MIP start só nas variáveis y
    (o Gurobi completa f). Permite dar ao compacto o mesmo start dos métodos
    em espaço-y.

    params: dict opcional de parâmetros extras do Gurobi (ex.: {'MIPFocus': 1}),
    aplicado depois dos acima — quem passa pode sobrescrever Seed/Threads/
    TimeLimit de propósito. Registre no CSV do experimento o que foi passado.

    coletar_incumbente: se True, um callback só de leitura registra o tempo do
    primeiro e do melhor incumbente. Não adiciona corte. O padrão é False
    para não alterar o caminho de busca dos experimentos já publicados.
    Callback em measure_lp/measure_root não é ligado: essas funções medem
    LP/raiz em volume alto e não têm incumbente inteiro.
    """
    t_modelo = time.monotonic()
    modelo, y, f, _ = _make_mip(S, T, V, A_r, f_type, upfront_cuts)
    time_modelo_s = time.monotonic() - t_modelo
    modelo.Params.OutputFlag = 0
    modelo.Params.Seed       = seed
    modelo.Params.Threads    = threads
    modelo.Params.TimeLimit  = time_limit
    for chave, valor in (params or {}).items():
        modelo.setParam(chave, valor)
    if y_start is not None:
        for v in V:
            y[v].Start = y_start.get(v, 0.0)
        modelo.update()

    incumbente = {'primeiro': None, 'melhor': None, 'obj': None}

    def _cb_incumbente(m, where):
        if where != GRB.Callback.MIPSOL:
            return
        t = float(m.cbGet(GRB.Callback.RUNTIME))
        ub = float(m.cbGet(GRB.Callback.MIPSOL_OBJ))
        if incumbente['primeiro'] is None:
            incumbente['primeiro'] = t
        if incumbente['obj'] is None or ub < incumbente['obj'] - 1e-8:
            incumbente['obj'] = ub
            incumbente['melhor'] = t

    t0 = time.monotonic()
    if coletar_incumbente:
        modelo.optimize(_cb_incumbente)
    else:
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
        'node_count': int(modelo.NodeCount),
        'time_mip_s': t1 - t0,
        'time_modelo_s': time_modelo_s,
        'time_to_first_incumbent_s': incumbente['primeiro'],
        'time_to_best_incumbent_s': incumbente['melhor'],
        'time_to_proof_s': (t1 - t0) if status == GRB.OPTIMAL else None,
        'work': float(modelo.Work),
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
