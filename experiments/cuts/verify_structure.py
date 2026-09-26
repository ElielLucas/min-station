"""
E5 Bloco A: verificação estrutural das instâncias hc* e bip42p.

Confirma ou refuta, com medição própria, as afirmações levantadas por sondas
anteriores: hc9u..hc12p são hipercubos Q_k com terminais na classe par,
|A_r| = |E| (alcance de 1 salto), C2 e C4-DM contidos em C1, ausência de
gêmeos, e se a solução ótima do núcleo de cobertura de hc9u é viável no
problema real com fluxo.

Saída: results/cuts/e5_estrutura.csv
"""

import csv
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

from gurobipy import GRB
from baseline import construir_modelo_baseline
from harness import load_instance
from cuts import build_neighborhoods, generate_C1, generate_C2, generate_C4_DM
from yspace import solve_ip_yspace

INST_DIR = ROOT / 'instances'
OUT_CSV  = ROOT / 'results' / 'cuts' / 'e5_estrutura.csv'

INSTANCES = ['hc9u.txt', 'hc10p.txt', 'hc11p.txt', 'hc12p.txt', 'bip42p.txt']

HEADER = [
    'instancia', 'n', 'm', 'n_arestas_E', 'n_arcos_Ar',
    'grau_min', 'grau_max', 'grau_uniforme',
    'todas_arestas_diferem_1_bit',
    'S_inter_T', 'S_uniao_T', 'paridade_uniforme_SuT', 'arestas_internas_SuT',
    'Ar_igual_E',
    'linhas_C1', 'tamanho_linha_C1_min', 'tamanho_linha_C1_max',
    'C2_subset_C1', 'C4_subset_C1', 'n_C2', 'n_C4',
    'classes_assinatura', 'maior_classe_assinatura',
    'lp_fechado_2elevkm1_sobre_k',
]


def _bit_diff_count(a, b):
    return bin(int(a) ^ int(b)).count('1')


def analisar(fname):
    path = INST_DIR / fname
    S, T, V, adj, A_r, r = load_instance(path)
    S_set, T_set = set(S), set(T)
    n = len(V)
    m = len(S)

    n_arestas_E = sum(len(vs) for vs in adj.values())  # dirigida dupla, como no arquivo
    n_arcos_Ar  = len(A_r)

    graus = {v: len(adj.get(v, [])) for v in V}
    grau_min = min(graus.values())
    grau_max = max(graus.values())
    grau_uniforme = (grau_min == grau_max)

    # todas as arestas ligam ids que, como inteiros, diferem em exatamente 1 bit?
    # só faz sentido testar se os ids são numéricos (1..n)
    todas_1bit = None
    try:
        ids_ok = all(str(v).isdigit() for v in V)
        if ids_ok:
            todas_1bit = True
            for u, vs in adj.items():
                for w, _ in vs:
                    # ids do arquivo são 1-indexados; comparar o vértice-1 (0-indexado) em binário
                    if _bit_diff_count(int(u) - 1, int(w) - 1) != 1:
                        todas_1bit = False
                        break
                if not todas_1bit:
                    break
    except Exception:
        todas_1bit = None

    S_inter_T = len(S_set & T_set)
    SuT = S_set | T_set
    S_uniao_T = len(SuT)

    paridade_uniforme = None
    if todas_1bit:
        try:
            paridades = {(int(v) - 1).bit_count() % 2 for v in SuT}
            paridade_uniforme = (len(paridades) == 1)
        except Exception:
            paridade_uniforme = None

    arestas_internas_SuT = 0
    for u, vs in adj.items():
        if u in SuT:
            for w, _ in vs:
                if w in SuT:
                    arestas_internas_SuT += 1
    arestas_internas_SuT //= 2  # cada aresta contada nos dois sentidos (u->w e w->u)

    Ar_igual_E = (n_arcos_Ar == n_arestas_E)

    N_plus, N_minus = build_neighborhoods(A_r)
    c1 = generate_C1(S, T, N_plus, N_minus)
    c2 = generate_C2(S, T, adj, r, V)
    c4 = generate_C4_DM(S, T, N_plus, N_minus)

    set_c1 = set(c1)
    c2_subset_c1 = all(z in set_c1 for z in c2) if c2 else True
    c4_subset_c1 = all(z in set_c1 for z in c4) if c4 else True

    tam_linhas = [len(z) for z in c1]
    tam_min = min(tam_linhas) if tam_linhas else None
    tam_max = max(tam_linhas) if tam_linhas else None

    # assinatura por variável: multiconjunto (aqui, conjunto) de linhas C1 em que aparece
    assinatura = {}
    for idx, Z in enumerate(c1):
        for v in Z:
            assinatura.setdefault(v, set()).add(idx)
    # duas variáveis são "gêmeas" se pertencem exatamente às mesmas linhas
    grupos = {}
    for v, linhas in assinatura.items():
        key = frozenset(linhas)
        grupos.setdefault(key, []).append(v)
    classes_assinatura = len(grupos)
    maior_classe = max((len(g) for g in grupos.values()), default=0)

    # LP fechado: 2^(k-1)/k quando n = 2^k (só aplicável às hc*)
    lp_fechado = None
    k = n.bit_length() - 1
    if (1 << k) == n:
        lp_fechado = (2 ** (k - 1)) / k

    return {
        'instancia': fname,
        'n': n,
        'm': m,
        'n_arestas_E': n_arestas_E,
        'n_arcos_Ar': n_arcos_Ar,
        'grau_min': grau_min,
        'grau_max': grau_max,
        'grau_uniforme': grau_uniforme,
        'todas_arestas_diferem_1_bit': todas_1bit,
        'S_inter_T': S_inter_T,
        'S_uniao_T': S_uniao_T,
        'paridade_uniforme_SuT': paridade_uniforme,
        'arestas_internas_SuT': arestas_internas_SuT,
        'Ar_igual_E': Ar_igual_E,
        'linhas_C1': len(c1),
        'tamanho_linha_C1_min': tam_min,
        'tamanho_linha_C1_max': tam_max,
        'C2_subset_C1': c2_subset_c1,
        'C4_subset_C1': c4_subset_c1,
        'n_C2': len(c2),
        'n_C4': len(c4),
        'classes_assinatura': classes_assinatura,
        'maior_classe_assinatura': maior_classe,
        'lp_fechado_2elevkm1_sobre_k': lp_fechado,
    }


def verificar_viabilidade_nucleo_hc9u():
    """
    Resolve o núcleo de cobertura de hc9u (IP em y-space) e testa se a
    solução ótima é viável no problema real com fluxo (modelo compacto).

    Retorna (obj_nucleo, viavel_no_compacto: bool ou None, max_flow_valor: int ou None).
    """
    path = INST_DIR / 'hc9u.txt'
    S, T, V, adj, A_r, r = load_instance(path)

    res = solve_ip_yspace(S, T, V, adj, A_r, r, time_limit=120, seed=42, threads=4)
    if res['ip_status'] != GRB.OPTIMAL or res['ip_obj'] is None:
        return res.get('ip_obj'), None, None

    # reconstrói o conjunto C a partir do y-space: como solve_ip_yspace não
    # devolve y diretamente, resolve de novo aqui para extrair C.
    from yspace import _build_ymodel
    N_plus, N_minus = build_neighborhoods(A_r)
    c1 = generate_C1(S, T, N_plus, N_minus)
    c2 = generate_C2(S, T, adj, r, V)
    c4 = generate_C4_DM(S, T, N_plus, N_minus)
    static = list(set(map(frozenset, c1 + c2 + c4)))
    mip, y = _build_ymodel(V, static, integer=True, seed=42, threads=4, time_limit=120)
    mip.optimize()
    if mip.Status != GRB.OPTIMAL:
        return None, None, None

    C = {v for v in V if y[v].X > 0.5}
    obj_nucleo = len(C)

    # fixa y no modelo compacto: y_v=1 para v em C, y_v=0 caso contrário
    modelo, y_c, f_c, _, _ = construir_modelo_baseline(S, T, V, A_r)
    modelo.Params.OutputFlag = 0
    for v in V:
        y_c[v].lb = 1.0 if v in C else 0.0
        y_c[v].ub = 1.0 if v in C else 0.0
    modelo.update()
    modelo.optimize()

    viavel = (modelo.Status == GRB.OPTIMAL)

    # se inviável, mede o déficit via max-flow simples (m robôs, capacidade m*y_v)
    max_flow_valor = None
    if not viavel:
        import networkx as nx
        G = nx.DiGraph()
        m = len(S)
        S_set, T_set = set(S), set(T)
        for s in S:
            G.add_edge('_s', f'{s}_out', capacity=1.0)
        for t in T:
            G.add_edge(f'{t}_in', '_t', capacity=1.0)
        for v in V:
            cap = (m - 1) if v in (S_set | T_set) else m
            cap = cap if v in C else 0.0
            G.add_edge(f'{v}_in', f'{v}_out', capacity=float(cap))
        for u, v in A_r:
            G.add_edge(f'{u}_out', f'{v}_in', capacity=1e9)
        try:
            max_flow_valor, _ = nx.maximum_flow_value(G, '_s', '_t'), None
            max_flow_valor = nx.maximum_flow_value(G, '_s', '_t')
        except Exception as e:
            max_flow_valor = f'erro: {e}'

    return obj_nucleo, viavel, max_flow_valor


def main():
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    rows = []

    print('=== E5 Bloco A: verificação estrutural ===\n')
    for fname in INSTANCES:
        path = INST_DIR / fname
        if not path.exists():
            print(f'  {fname}: não encontrado — pulando')
            continue
        t0 = time.monotonic()
        row = analisar(fname)
        dt = time.monotonic() - t0
        rows.append(row)
        print(f'  {fname}  ({dt:.2f}s)')
        for k, v in row.items():
            if k != 'instancia':
                print(f'    {k}: {v}')
        print()

    with OUT_CSV.open('w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=HEADER)
        w.writeheader()
        w.writerows(rows)
    print(f'[e5_estrutura] {len(rows)} linhas salvas em {OUT_CSV}\n')

    print('=== Verificação de viabilidade do núcleo de hc9u ===')
    obj, viavel, maxflow = verificar_viabilidade_nucleo_hc9u()
    print(f'  OPT(núcleo) = {obj}')
    print(f'  viável no modelo compacto (fluxo)? {viavel}')
    if not viavel:
        print(f'  max-flow com C do núcleo (m={128 if obj else "?"}): {maxflow}')
        print('  ==> Esta solução de núcleo é inviável no problema real. OPT(hc9u) ∈ [32, 38] continua aberto.')
        print('      (Outras soluções ótimas do núcleo com 32 estações podem existir e ser viáveis.)')
    else:
        print('  ==> Esta solução de núcleo é viável no compacto. OPT(hc9u) = OPT(núcleo).')


if __name__ == '__main__':
    main()
