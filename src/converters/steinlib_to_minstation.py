import argparse
import random
import networkx as nx
import math
from pathlib import Path
from statistics import median

def parse_stp(filepath):
    """Lê o formato STP da SteinLib e retorna grafo e terminais."""
    with open(filepath, 'r') as f:
        lines = [l.strip() for l in f if l.strip()]

    mode = None
    edges = []
    terminals = []
    num_nodes = 0

    for line in lines:
        if line.startswith("SECTION Graph"):
            mode = "GRAPH"
            continue
        elif line.startswith("SECTION Terminals"):
            mode = "TERMINALS"
            continue
        elif line.startswith("END"):
            mode = None
            continue
        
        if mode == "GRAPH":
            parts = line.split()
            if parts[0] == "Nodes":
                num_nodes = int(parts[1])
            elif parts[0] == "E":
                u, v, w = parts[1], parts[2], float(parts[3])
                edges.append((u, v, w))
        
        elif mode == "TERMINALS":
            parts = line.split()
            if parts[0] == "T":
                terminals.append(parts[1])

    return num_nodes, edges, terminals

def calcular_r_automatico(G, S, T, percentil=0.5):
    """Calcula caminhos mínimos entre todos os pares S->T e define R."""
    distancias = []
    print(f"   -> Calculando caminhos para calibrar R ({len(S)}x{len(T)} pares)...")
    
    # Para grafos muito grandes, podemos amostrar, mas para Set B/C dá para fazer tudo
    for s in S:
        try:
            # Dijkstra de 's' para todos os outros
            dists_from_s = nx.single_source_dijkstra_path_length(G, s, weight='weight')
            for t in T:
                if t in dists_from_s:
                    distancias.append(dists_from_s[t])
        except Exception:
            pass # Grafo desconexo ou sem caminho

    if not distancias:
        print("   [AVISO] Não foram encontrados caminhos entre S e T. R padrão = 100.0")
        return 100.0 # Fallback

    distancias.sort()
    idx = int(len(distancias) * percentil)
    # Garante índice válido
    if idx >= len(distancias):
        idx = len(distancias) - 1
        
    r_val = distancias[idx]
    return max(1.0, math.ceil(r_val))

def main():
    parser = argparse.ArgumentParser(description="Converte SteinLib STP -> MIN-STATION TXT (Balanceado)")
    parser.add_argument("input", type=str, help="Arquivo .stp de entrada")
    parser.add_argument("output", type=str, help="Arquivo .txt de saída")
    parser.add_argument("--seed", type=int, default=42, help="Semente para divisão aleatória S/T")
    parser.add_argument("--percentil", type=float, default=0.5, help="Percentil para R (0.1 a 1.0)")
    args = parser.parse_args()

    # 1. Parsing
    print(f"[1/4] Lendo {args.input}...")
    try:
        n_nodes, edges_raw, terminals = parse_stp(args.input)
    except Exception as e:
        print(f"ERRO ao ler arquivo STP: {e}")
        return

    # 2. Setup Grafo e Terminais
    print(f"[2/4] Processando topologia e terminais...")
    random.seed(args.seed)
    random.shuffle(terminals)
    
    # --- CORREÇÃO DE BALANCEAMENTO ---
    num_terminals = len(terminals)
    if num_terminals % 2 != 0:
        print(f"   -> [Ajuste] Número ímpar de terminais ({num_terminals}). Descartando 1 para garantir |S|=|T|.")
        terminals.pop() # Remove o último da lista embaralhada
        num_terminals -= 1
    
    if num_terminals == 0:
        raise ValueError("Erro: A instância não possui terminais suficientes (menos de 2).")

    mid = num_terminals // 2
    S = terminals[:mid]
    T = terminals[mid:]
    
    print(f"   -> Definidos: |S|={len(S)} e |T|={len(T)} (Total usados: {num_terminals})")
    # ----------------------------------------------------------------

    # Montar Grafo NetworkX para cálculo de distâncias
    G = nx.Graph()
    output_edges = []
    
    # SteinLib é não-dirigido. Para Min-Station (fluxo), geramos ida e volta.
    for u, v, w in edges_raw:
        G.add_edge(u, v, weight=w)
        # Formato de saída Min-Station espera arestas dirigidas
        output_edges.append((u, v, w))
        output_edges.append((v, u, w))

    # 3. Calcular R
    print(f"[3/4] Calibrando Autonomia (R)...")
    R = calcular_r_automatico(G, S, T, args.percentil)
    print(f"   -> R definido (Percentil {args.percentil}): {R}")

    # 4. Escrita
    print(f"[4/4] Salvando em {args.output}...")
    with open(args.output, "w") as f:
        # Cabeçalho esperado por ms_utils.ler_instancia
        f.write(f"N {n_nodes}\n")
        f.write(f"M {len(output_edges)}\n")
        f.write(f"R {R}\n")
        f.write("# u v length\n")
        
        for u, v, w in output_edges:
            f.write(f"{u} {v} {w}\n")
            
        f.write(f"S {len(S)}\n")
        f.write(" ".join(S) + "\n")
        f.write(f"T {len(T)}\n")
        f.write(" ".join(T) + "\n")

    print(f"Concluído com sucesso: {args.output}")

if __name__ == "__main__":
    main()