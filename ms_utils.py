import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Tuple
from collections import defaultdict
from heapq import heappush, heappop

No   = str
Arco = Tuple[No, No]

def ler_instancia(caminho):
    """
    Espera (ordem flexível):
      N <int>
      M <int>
      R <float>
      # u v length
      u v w
      ...
      S <m>
      <m ids>
      T <m>
      <m ids>
    Retorna: {"S":[], "T":[], "VI":[], "V":[], "E":[(u,v,w)], "R":float}
    """
    with open(caminho, "r", encoding="utf-8") as f:
        bruto = [ln.strip() for ln in f if ln.strip()]

    linhas = [ln for ln in bruto if not ln.startswith("#")]

    N = None
    M_declarado = None
    R = None
    E = []
    S_lista = []
    T_lista = []

    i = 0
    while i < len(linhas):
        ln = linhas[i]
        if ln.startswith("N "):
            N = int(ln.split()[1]); i += 1; continue
        if ln.startswith("M "):
            M_declarado = int(ln.split()[1]); i += 1; continue
        if ln.startswith("R "):
            R = float(ln.split()[1]); i += 1; break
        i += 1
    if R is None:
        raise ValueError("Campo R ausente no arquivo.")

    while i < len(linhas) and not linhas[i].startswith("S "):
        partes = linhas[i].split()
        if len(partes) == 3:
            u, v, w = partes
            E.append((u, v, float(w)))
        i += 1

    if i >= len(linhas) or not linhas[i].startswith("S "):
        raise ValueError("Bloco 'S <m>' não encontrado.")
    
    mS = int(linhas[i].split()[1]); i += 1
    if i >= len(linhas):
        raise ValueError("Linha com IDs de S ausente.")
    
    S_lista = linhas[i].split(); i += 1
    if len(S_lista) != mS:
        raise ValueError(f"S: esperado {mS}, veio {len(S_lista)}")

    if i >= len(linhas) or not linhas[i].startswith("T "):
        raise ValueError("Bloco 'T <m>' não encontrado.")
    
    mT = int(linhas[i].split()[1]); i += 1
    if i >= len(linhas):
        raise ValueError("Linha com IDs de T ausente.")
    
    T_lista = linhas[i].split(); i += 1
    if len(T_lista) != mT:
        raise ValueError(f"T: esperado {mT}, veio {len(T_lista)}")

    V_conjunto = set(S_lista) | set(T_lista)
    for u, v, _ in E:
        V_conjunto.add(u); V_conjunto.add(v)
    V = sorted(V_conjunto)
    VI = [n for n in V if n not in set(S_lista) and n not in set(T_lista)]

    if (M_declarado is not None) and (len(E) != M_declarado):
        print(f"[aviso:{Path(caminho).name}] M declarado={M_declarado}, lido={len(E)} — usando lido.")

    if (N is not None) and (len(V) > N):
        print(f"[aviso:{Path(caminho).name}] N declarado={N}, únicos lidos={len(V)} — usando {len(V)}.")

    return {"S": S_lista, "T": T_lista, "VI": VI, "V": V, "E": E, "R": R}

def construir_adjacencia(arestas):
    adj = defaultdict(list)

    for u, v, w in arestas:
        adj[u].append((v, w))

    return adj

def construir_arcos_alcance(nos, adj, R):
    A = []
    Vset = set(nos)

    for s in nos:
        dist = {s: 0.0}
        pq = [(0.0, s)]

        while pq:
            d, u = heappop(pq)
            if d > R:
                continue

            for w, cw in adj.get(u, []):
                nd = d + cw
                if nd <= R and (w not in dist or nd < dist[w] - 1e-12):
                    dist[w] = nd
                    heappush(pq, (nd, w))

        for v, dv in dist.items():
            if v != s and dv <= R and v in Vset:
                A.append((s, v))
    return A

class RegistSerieTemporal:
    """
    Guarda pontos (tempo, LB, UB, nós de busca) e gera CSV/PNG.
    """
    def __init__(
            self, 
            instancia, 
            R, 
            pasta_saida,
            intervalo_amostra = 5.0,
            suffix = "",
            titulo_tag = ""
        ):
        
        self.instancia = instancia
        self.R = R
        self.pasta_saida = pasta_saida
        self.intervalo_amostra = float(intervalo_amostra)
        self.suffix = suffix
        self.titulo_tag = titulo_tag
        self.pontos = []
        self._t_ultimo = -1.0
        self._lb_ultimo = None
        self._ub_ultimo = None

        if pasta_saida:
            pasta_saida.mkdir(parents=True, exist_ok=True)

    def talvez_adicionar(self, t, lb, ub, nos_busca, forcar = False):

        mudou = (self._lb_ultimo is None
                 or (lb is not None and self._lb_ultimo is not None and abs(lb - self._lb_ultimo) > 1e-12)
                 or (ub is not None and self._ub_ultimo is not None and abs(ub - self._ub_ultimo) > 1e-12))
        
        if forcar or mudou or (t - self._t_ultimo >= self.intervalo_amostra):
            self.pontos.append((float(t),
                                float(lb) if lb is not None else float("nan"),
                                float(ub) if ub is not None else float("nan"),
                                int(nos_busca)))
            
            self._t_ultimo = float(t)
            self._lb_ultimo = lb
            self._ub_ultimo = ub

    def salvar_csv(self):
        if not self.pasta_saida:
            return None
        caminho_csv = self.pasta_saida / f"{self.instancia}__R{int(self.R)}__timeseries{self.suffix}.csv"
        import csv as _csv
        with caminho_csv.open("w", newline="", encoding="utf-8") as f:
            w = _csv.writer(f)
            w.writerow(["time_s", "LB", "UB", "nodes"])
            for t, lb, ub, nd in self.pontos:
                w.writerow([t, lb, ub, nd])
        return caminho_csv

    def salvar_grafico(
            self, 
            escala_y = "linear", 
            corte_inicial_s = 0.5,
            teto_percentil = 99.0, 
            mostrar_gap = True,
            max_pontos = 400
        ):
        
        if not self.pasta_saida:
            return None
        if not self.pontos:
            print("[plot] sem pontos para plotar")
            return None

        ts  = np.array([p[0] for p in self.pontos], dtype=float)
        lbs = np.array([p[1] for p in self.pontos], dtype=float)
        ubs = np.array([p[2] for p in self.pontos], dtype=float)

        # O Gurobi pode usar valores muito altos para representar infinito.
        # Esses valores não devem ser considerados no gráfico.
        limite_infinito = 1e90

        lbs[~np.isfinite(lbs) | (np.abs(lbs) >= limite_infinito)] = np.nan
        ubs[~np.isfinite(ubs) | (np.abs(ubs) >= limite_infinito)] = np.nan

        if len(ts) > max_pontos:
            idx = np.linspace(0, len(ts)-1, max_pontos).round().astype(int)
            ts, lbs, ubs = ts[idx], lbs[idx], ubs[idx]

        mascara = ts >= float(corte_inicial_s)
        ref = np.r_[lbs[mascara], ubs[mascara]]
        ref = ref[np.isfinite(ref)]

        if ref.size == 0:
            ref_total = np.r_[lbs, ubs]
            ref = ref_total[np.isfinite(ref_total)]

        if ref.size == 0:
            print("[plot] sem valores numéricos")
            return None

        ymin = max(0.0, float(np.nanmin(ref)))
        ymax = float(np.nanpercentile(ref, float(teto_percentil)))
        if not np.isfinite(ymax) or ymax <= ymin:
            ymax = ymin + 1.0

        plt.figure(figsize=(7.2, 4.2))
        ax = plt.gca()
        ax.plot(ts, lbs, marker="o", linestyle="-", label="LB")
        ax.plot(ts, ubs, marker="s", linestyle="--", label="UB")
        ax.set_xlabel("Tempo (s)")
        ax.set_ylabel("Valor dos limitantes")

        if escala_y.lower() == "symlog":
            ax.set_yscale("symlog", linthresh=1e-2)

        ax.set_ylim(ymin*0.95, ymax*1.05)
        ax.grid(True, which="both", linewidth=0.6, alpha=0.5)
        ax.legend(loc="best")
        tag = f" [{self.titulo_tag}]" if self.titulo_tag else ""
        ax.set_title(f"Evolução dos limitantes — {self.instancia} (r={int(self.R)}){tag}")

        if mostrar_gap:
            with np.errstate(divide='ignore', invalid='ignore'):
                gap_pct = (ubs - lbs) / np.where(np.abs(ubs) > 1e-12, np.abs(ubs), np.nan) * 100.0

            ax2 = ax.twinx()
            ax2.plot(ts, gap_pct, linestyle=":", label="gap (%)")

            if np.isfinite(gap_pct).any():
                topo = float(np.nanpercentile(gap_pct[np.isfinite(gap_pct)], 99.0))
                ax2.set_ylim(0, max(5.0, topo*1.15))

            ax2.set_ylabel("Gap (%)")
            ax2.grid(False)
            h1, l1 = ax.get_legend_handles_labels()
            h2, l2 = ax2.get_legend_handles_labels()
            ax2.legend(h1+h2, l1+l2, loc="upper right")

        caminho_png = self.pasta_saida / f"{self.instancia}__R{int(self.R)}__lb_ub{self.suffix}.png"
        plt.tight_layout()
        plt.savefig(caminho_png, dpi=160)
        plt.close()
        return caminho_png
