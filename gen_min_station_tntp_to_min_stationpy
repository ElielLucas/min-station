import argparse
import math
import re
from collections import defaultdict, deque
from pathlib import Path
from statistics import median
from heapq import heappush, heappop
from typing import List


PERCENTIL_R: float = 0.50
R_MIN_KM: int     = 1

MILHA_PARA_KM = 1.609344
PE_PARA_KM    = 0.0003048

def detectar_unidade_comprimento(comprimentos):
    if not comprimentos:
        return "milhas"
    return "pes" if median(comprimentos) >= 1000.0 else "milhas"

def ler_rede_tntp_dirigida(caminho_rede):
    if not caminho_rede.exists():
        raise FileNotFoundError(f"Arquivo de rede não encontrado: {caminho_rede}")
    
    arestas = []
    comprimentos = []
    with caminho_rede.open("r", encoding="utf-8", errors="ignore") as f:
        for linha in f:
            s = linha.strip()
            if not s or s.startswith("~") or s.startswith("<"):
                continue
            partes = re.split(r"[,\s;]+", s)
            if len(partes) < 4:
                continue
            try:
                u = int(float(partes[0])); v = int(float(partes[1]))
                length = float(partes[3])
                if u != v:
                    arestas.append((u, v, length))
                    comprimentos.append(length)
            except Exception:
                pass
    return arestas, comprimentos

def ler_trips_tntp_fluxos(caminho_trips: Path):
    if not caminho_trips.exists():
        raise FileNotFoundError(f"Arquivo de trips não encontrado: {caminho_trips}")
    
    outfluxo = defaultdict(float)
    influxo = defaultdict(float)
    origem_atual = None
    re_origem = re.compile(r"^\s*Origin\s+(\d+)", re.IGNORECASE)
    re_par = re.compile(r"(\d+)\s*:\s*([+\-]?\d+(?:\.\d*)?(?:[Ee][+\-]?\d+)?)\s*;")
    with caminho_trips.open("r", encoding="utf-8", errors="ignore") as f:
        for linha in f:
            s = linha.strip()
            if not s or s.startswith("~"):
                continue
            m = re_origem.match(s)
            if m:
                origem_atual = int(m.group(1))
                continue
            if origem_atual is None:
                continue
            for (dst, val) in re_par.findall(s):
                d = int(dst)
                try:
                    dem = float(val)
                except Exception:
                    continue
                if dem > 0:
                    outfluxo[origem_atual] += dem
                    influxo[d]            += dem
    outfluxo = {i: v for i, v in outfluxo.items() if v > 0}
    influxo  = {j: v for j, v in influxo.items()  if v > 0}
    return outfluxo, influxo

def escolher_ST_disjuntos(outfluxo,
                          influxo,
                          m = None):
    O = set(outfluxo.keys())
    D = set(influxo.keys())
    S = sorted(O - D)
    T = sorted(D - O)
    C = sorted(O & D)
    m_max = min(len(O), len(D), (len(S) + len(T) + len(C)) // 2)
    if m is None:
        m = m_max
    if m > m_max:
        m = m_max
    C_ordenado = sorted(C, key=lambda i: (outfluxo.get(i, 0.0) - influxo.get(i, 0.0)), reverse=True)
    for i in C_ordenado:
        if len(S) >= m and len(T) >= m:
            break
        if len(S) < len(T) and len(S) < m:
            S.append(i)
        elif len(T) < len(S) and len(T) < m:
            T.append(i)
        else:
            if (outfluxo.get(i, 0.0) - influxo.get(i, 0.0)) >= 0:
                if len(S) < m: S.append(i)
                elif len(T) < m: T.append(i)
            else:
                if len(T) < m: T.append(i)
                elif len(S) < m: S.append(i)
    for i in C_ordenado:
        if i in S or i in T: continue
        if len(S) < m:   S.append(i)
        elif len(T) < m: T.append(i)
        if len(S) == m and len(T) == m: break
    if len(S) != m or len(T) != m or (set(S) & set(T)):
        raise RuntimeError("Falha ao construir S,T disjuntos.")
    return S, T


def dijkstra_para_todos_alvos(adj, s):
    dist = {s: 0}
    pq = [(0, s)]
    while pq:
        d, u = heappop(pq)
        if d != dist[u]:
            continue
        for w, cw in adj.get(u, []):
            nd = d + cw
            if w not in dist or nd < dist[w]:
                dist[w] = nd
                heappush(pq, (nd, w))
    return dist

def distancias_st_km_inteiro(S, T, arestas_int):
    adj = defaultdict(list)
    for u, v, w in arestas_int:
        adj[u].append((v, w))
    dists: List[int] = []
    for s in S:
        dist = dijkstra_para_todos_alvos(adj, s)
        for t in T:
            if t != s and t in dist:
                dists.append(dist[t])
    return dists

def quantil(xs, q) -> float:
    if not xs:
        return float("inf")
    ys = sorted(xs)
    if q <= 0: return float(ys[0])
    if q >= 1: return float(ys[-1])
    idx = q * (len(ys) - 1)
    lo = int(idx); hi = min(lo + 1, len(ys) - 1)
    frac = idx - lo
    return ys[lo] * (1 - frac) + ys[hi] * frac

def escolher_R_por_percentil(S, T, arestas_int, p, r_min_km) -> int:
    dists = distancias_st_km_inteiro(S, T, arestas_int)
    if not dists:
        fallback = max(w for _, _, w in arestas_int) * 2
        return max(r_min_km, fallback)
    q = quantil(dists, p)
    return max(r_min_km, int(math.ceil(q)))


def _adjacencia_nao_dirigida(arestas_int):
    adj_und = defaultdict(set)
    for u, v, _ in arestas_int:
        adj_und[u].add(v)
        adj_und[v].add(u)
    return adj_und

def _nos_presentes(arestas_int):
    vs = set()
    for u, v, _ in arestas_int:
        vs.add(u); vs.add(v)
    return vs

def extrair_subgrafo_conexo(arestas_int, n_nos, sementes_preferenciais = None):
    n_nos = max(1, n_nos)
    adj_und = _adjacencia_nao_dirigida(arestas_int)
    todos_nos = _nos_presentes(arestas_int)

    seeds: List[int] = []
    if sementes_preferenciais:
        seeds.extend([s for s in sementes_preferenciais if s in todos_nos])
    deg_sorted = sorted(todos_nos, key=lambda x: len(adj_und.get(x, ())), reverse=True)
    for v in deg_sorted:
        if v not in seeds:
            seeds.append(v)

    visitados = set()
    for s in seeds:
        if s in visitados:
            continue
        fila = deque([s])
        visitados.add(s)
        while fila and len(visitados) < n_nos:
            u = fila.popleft()
            for w in adj_und.get(u, ()):
                if w not in visitados:
                    visitados.add(w)
                    fila.append(w)
                    if len(visitados) >= n_nos:
                        break
        if len(visitados) >= n_nos:
            break

    if len(visitados) < n_nos:
        for v in todos_nos:
            if v not in visitados:
                visitados.add(v)
                if len(visitados) >= n_nos:
                    break

    sub_arestas = [(u, v, w) for (u, v, w) in arestas_int if u in visitados and v in visitados]
    return visitados, sub_arestas

def reindexar_subgrafo(nos, arestas, S, T):
    ordem = sorted(nos)
    mapa = {v: (i+1) for i, v in enumerate(ordem)}
    arestas2 = [(mapa[u], mapa[v], w) for (u, v, w) in arestas]
    S2 = [mapa[s] for s in S]
    T2 = [mapa[t] for t in T]
    return arestas2, S2, T2, mapa


def write_instancia(arquivo_saida, arestas_int, r_km_int, S, T, nos_presentes):

    with arquivo_saida.open("w", encoding="utf-8") as f:
        f.write(f"N {len(nos_presentes)}\n")
        f.write(f"M {len(arestas_int)}\n")
        f.write(f"R {r_km_int}\n")
        f.write("# u v length\n")

        for u, v, w in arestas_int:
            f.write(f"{u} {v} {w}\n")
        
        f.write(f"S {len(S)}\n")
        f.write(" ".join(map(str, S)) + "\n")
        f.write(f"T {len(T)}\n")
        f.write(" ".join(map(str, T)) + "\n")


def encontrar_arquivos_tntp(pasta_caso):

    cand_net   = sorted(pasta_caso.glob("*_net.tntp"))
    cand_trips = sorted(pasta_caso.glob("*_trips.tntp"))

    if not cand_net:
        raise FileNotFoundError(f"Nenhum *_net.tntp encontrado em: {pasta_caso}")
    
    if not cand_trips:
        raise FileNotFoundError(f"Nenhum *_trips.tntp encontrado em: {pasta_caso}")
    
    def stem_sem_sufixo(p: Path, sufixo: str) -> str:
        name = p.name
        return name[: -len(sufixo)] if name.endswith(sufixo) else name
    
    stems_net   = {stem_sem_sufixo(p, "_net.tntp"): p for p in cand_net}
    stems_trips = {stem_sem_sufixo(p, "_trips.tntp"): p for p in cand_trips}
    comuns = set(stems_net.keys()) & set(stems_trips.keys())

    if comuns:
        chave = sorted(comuns)[0]
        return stems_net[chave], stems_trips[chave]
    
    return cand_net[0], cand_trips[0]

def main():
    parser = argparse.ArgumentParser(description="TNTP -> MIN-STATION (subgrafo conexo)")
    parser.add_argument("--repositorio", type=str, required=True, help="Pasta raiz do TransportationNetworks")
    parser.add_argument("--caso", type=str, required=True, help="Subpasta do caso Ex. Barcelona")
    parser.add_argument("--saida", type=str, required=True, help="Arquivo de saída da instância")
    parser.add_argument("--n-nos", type=int, required=True, help="Quantidade de nós no subgrafo")
    parser.add_argument("--m-st", type=int, default=None, help="|S|=|T| desejado (opcional)")
    parser.add_argument("--semente", type=int, default=None, help="Nó semente para o BFS (opcional)")
    parser.add_argument("--reindexar", action="store_true", help="Reindexar nós do subgrafo para 1..N")
    parser.add_argument("--percentil-r", type=float, default=PERCENTIL_R, help="Percentil para R (0..1)")
    args = parser.parse_args()

    pasta_caso = Path(args.repositorio) / args.caso
    caminho_rede, caminho_trips = encontrar_arquivos_tntp(pasta_caso)

    # 1) Rede + conversão de unidades -> km inteiros
    arestas_raw, compr_brutos = ler_rede_tntp_dirigida(caminho_rede)
    unidade = detectar_unidade_comprimento(compr_brutos)
    fator = PE_PARA_KM if unidade == "pes" else MILHA_PARA_KM
    arestas_int = [(u, v, max(1, int(math.ceil(w * fator)))) for (u, v, w) in arestas_raw]

    # 2) Fluxos OD (para escolher S,T e semente preferencial)
    outfluxo_full, influxo_full = ler_trips_tntp_fluxos(caminho_trips)

    # 3) Subgrafo conexo por BFS
    sementes_pref = []
    if args.semente is not None:
        sementes_pref.append(args.semente)
    # prioriza nós com maior (out+in) como sementes adicionais
    by_flow = sorted(set(list(outfluxo_full.keys()) + list(influxo_full.keys())),
                     key=lambda v: (outfluxo_full.get(v,0.0) + influxo_full.get(v,0.0)),
                     reverse=True)
    sementes_pref.extend(by_flow)
    nos_sub, arestas_sub = extrair_subgrafo_conexo(arestas_int, args.n_nos, sementes_preferenciais=sementes_pref)

    # 4) Restringe fluxos a V_sub e escolhe S,T
    outfluxo = {i:v for i,v in outfluxo_full.items() if i in nos_sub}
    influxo  = {j:v for j,v in influxo_full.items() if j in nos_sub}
    S, T = escolher_ST_disjuntos(outfluxo, influxo, m=args.m_st)

    # 5) R pelo percentil (sem margem)
    R_int = escolher_R_por_percentil(S, T, arestas_sub, p=args.percentil_r, r_min_km=R_MIN_KM)

    # 6) Reindexação opcional
    if args.reindexar:
        arestas_out, S_out, T_out, mapa = reindexar_subgrafo(nos_sub, arestas_sub, S, T)
        nos_out = set(mapa.values())
    else:
        arestas_out, S_out, T_out = arestas_sub, S, T
        nos_out = set(nos_sub)

    write_instancia(Path(args.saida), arestas_out, R_int, S_out, T_out, nos_presentes=nos_out)

    print(f"[arquivos] net={caminho_rede.name} | trips={caminho_trips.name}")
    print(f"[subgrafo] |V|={len(nos_out)} |E|={len(arestas_out)}  |S|=|T|={len(S_out)}")
    print(f"[auto-R] p={args.percentil_r:.2f} -> R={R_int} km (inteiro)")
    print(f"[unidades] {unidade} -> km (ceil)")
    print(f"OK: {args.saida}")

if __name__ == "__main__":
    main()
