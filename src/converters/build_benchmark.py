"""
Gerador do benchmark-v1 (plano-benchmark-v1.md §4 e §7).

Lê `instances/benchmark-v1/spec.csv` e gera uma instância MIN-STATION compatível
com Das (grafo simples, não dirigido, conexo, passos unitários) por linha, em
`instances/benchmark-v1/<familia>/<nome>.txt`, no formato de `ms_utils.ler_instancia`
com a proveniência em linhas `# meta: chave=valor` (ignoradas pelo leitor).

Regras nomeadas (coluna da spec -> valores):
  regra_G       G-UNIT | G-SUBDIV:<delta> | G-GRID
  regra_ST      ST-SEED:<seed> | ST-REGIAO | ST-INTERCALADO | NATIVO
  m             inteiro | metade  (metade = floor(|terminais|/2))
  regra_r       R-1 | R-FRAC:<k> | R-FIXO:<r>
  rho           fração de pares S-T transformados em S∩T (padrão 0)

Formatos de fonte: stp (SteinLib/DIMACS/PACE), mapf (arquivo .map; terminais do
.scen indicado em `terminais`, formato "<arquivo.scen>:<k primeiros agentes>"),
graphml (redes viárias OSMnx; terminais candidatos = interseções originais).

Instância trivial (r ≥ λ*, logo OPT = 0) não é gravada.

Uso: python src/converters/build_benchmark.py [--so NOME ...]
"""
import argparse
import csv
import math
import random
import subprocess
import sys
from collections import deque
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

from steinlib_to_minstation import parse_stp
from instance_features import lambda_estrela

SPEC = ROOT / 'instances' / 'benchmark-v1' / 'spec.csv'
OUT_DIR = ROOT / 'instances' / 'benchmark-v1'
SCRIPT = 'src/converters/build_benchmark.py'
MAPF_LIVRE = set('.GS')


def _commit():
    try:
        return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'],
                                       cwd=ROOT, text=True).strip()
    except Exception:
        return 'desconhecido'


# ── leitura das fontes: (arestas [(u, v, comprimento)], terminais [ids], papéis) ──

def ler_stp(path):
    _, edges, terminais = parse_stp(str(path))
    return edges, terminais, None


def ler_mapf(path_map, terminais_spec):
    linhas = path_map.read_text().splitlines()
    i = linhas.index('map') + 1
    grade = linhas[i:]
    livre = {(y, x) for y, lin in enumerate(grade) for x, c in enumerate(lin) if c in MAPF_LIVRE}
    edges = []
    for (y, x) in livre:
        for dy, dx in ((0, 1), (1, 0)):
            if (y + dy, x + dx) in livre:
                edges.append((f'{y}_{x}', f'{y + dy}_{x + dx}', 1.0))
    arq_scen, k = terminais_spec.rsplit(':', 1)
    S, T = [], []
    for ln in (path_map.parent / arq_scen).read_text().splitlines()[1:int(k) + 1]:
        p = ln.split('\t')
        sx, sy, gx, gy = int(p[4]), int(p[5]), int(p[6]), int(p[7])
        S.append(f'{sy}_{sx}')
        T.append(f'{gy}_{gx}')
    return edges, S + T, (S, T)


def ler_graphml(path):
    """
    Rede viária OSMnx (GraphML): grafo não dirigido subjacente, comprimento em
    metros (menor valor entre arestas paralelas). Terminais candidatos = todas
    as interseções originais (sem papel; a regra ST define S e T).
    """
    import networkx as nx
    G = nx.read_graphml(path)
    comp = {}
    for u, v, d in G.edges(data=True):
        if u == v:
            continue
        chave = (min(u, v), max(u, v))
        comp[chave] = min(comp.get(chave, float('inf')), float(d.get('length', 1.0)))
    edges = [(u, v, w) for (u, v), w in comp.items()]
    return edges, list(G.nodes()), None


# ── regra G ──────────────────────────────────────────────────────────────────

def aplicar_G(edges, regra):
    """Devolve adjacência não dirigida de passos unitários {v: set(vizinhos)}."""
    adj = {}

    def liga(a, b):
        if a != b:
            adj.setdefault(a, set()).add(b)
            adj.setdefault(b, set()).add(a)

    vistos = set()
    for u, v, w in edges:
        chave = (min(u, v), max(u, v))
        if u == v or chave in vistos:
            continue
        vistos.add(chave)
        if regra.startswith('G-SUBDIV'):
            delta = float(regra.split(':')[1])
            partes = max(1, round(w / delta))
            anterior = chave[0]
            for j in range(1, partes):
                meio = f'{chave[0]}~{chave[1]}~{j}'
                liga(anterior, meio)
                anterior = meio
            liga(anterior, chave[1])
        else:  # G-UNIT e G-GRID
            liga(u, v)
    return adj


def maior_componente(adj):
    melhor, visto = set(), set()
    for v0 in sorted(adj):
        if v0 in visto:
            continue
        comp, fila = {v0}, deque([v0])
        while fila:
            u = fila.popleft()
            for w in adj[u]:
                if w not in comp:
                    comp.add(w)
                    fila.append(w)
        visto |= comp
        if len(comp) > len(melhor):
            melhor = comp
    return {v: adj[v] & melhor for v in melhor}


def bfs(adj, fonte):
    dist, fila = {fonte: 0}, deque([fonte])
    while fila:
        u = fila.popleft()
        for w in adj[u]:
            if w not in dist:
                dist[w] = dist[u] + 1
                fila.append(w)
    return dist


def _ordem(v):
    return (0, int(v)) if str(v).isdigit() else (1, str(v))


# ── regras de S/T ─────────────────────────────────────────────────────────────

def dividir_ST(adj, terminais, regra, m):
    terms = [t for t in dict.fromkeys(terminais) if t in adj]
    if m == 'metade':
        m = len(terms) // 2
    m = int(m)
    if 2 * m > len(terms):
        raise ValueError(f'm={m} exige {2 * m} terminais, há {len(terms)}')

    if regra.startswith('ST-SEED'):
        # mesma sequência de steinlib_to_minstation.py: shuffle na ordem lida
        rng = random.Random(int(regra.split(':')[1]))
        terms = list(terms)
        rng.shuffle(terms)
        if len(terms) % 2:
            terms.pop()
        metade = len(terms) // 2
        return terms[:metade][:m], terms[metade:][:m]

    ordenados = sorted(terms, key=_ordem)
    if regra == 'ST-REGIAO':
        d0 = bfs(adj, ordenados[0])
        a = max(ordenados, key=lambda t: (d0[t], _ordem(t)))
        da = bfs(adj, a)
        b = max(ordenados, key=lambda t: (da[t], _ordem(t)))
        db = bfs(adj, b)
        chave = sorted(ordenados, key=lambda t: (da[t] - db[t], _ordem(t)))
        return chave[:m], chave[-m:]

    if regra == 'ST-INTERCALADO':
        livres = list(ordenados)
        S, T = [], []
        while livres and len(S) < m:
            u = livres.pop(0)
            du = bfs(adj, u)
            v = min(livres, key=lambda t: (du[t], _ordem(t)))
            livres.remove(v)
            S.append(u)
            T.append(v)
        return S, T

    raise ValueError(f'regra_ST desconhecida: {regra}')


def aplicar_rho(adj, S, T, rho):
    """Os ⌈rho·m⌉ pares (s, t) mais próximos, t ∉ S, passam a ter t := s (S∩T)."""
    k = math.ceil(float(rho) * len(S))
    if k == 0:
        return S, T
    T = list(T)
    candidatos = []
    for s in S:
        ds = bfs(adj, s)
        for j, t in enumerate(T):
            candidatos.append((ds[t], _ordem(s), j, s))
    usados_s, usados_t = set(T) & set(S), set()
    for _, _, j, s in sorted(candidatos):
        if k == 0:
            break
        if s in usados_s or j in usados_t:
            continue
        T[j] = s
        usados_s.add(s)
        usados_t.add(j)
        k -= 1
    return S, T


def escolher_r(adj, S, T, regra):
    adj_w = {v: [(w, 1.0) for w in vs] for v, vs in adj.items()}
    lam = lambda_estrela(S, T, adj_w)
    if regra == 'R-1':
        return 1, lam
    if regra.startswith('R-FRAC'):
        return max(1, math.ceil(lam / int(regra.split(':')[1]))), lam
    if regra.startswith('R-FIXO'):
        return int(regra.split(':')[1]), lam
    raise ValueError(f'regra_r desconhecida: {regra}')


# ── escrita ───────────────────────────────────────────────────────────────────

def gravar(spec, adj, S, T, r, lam, commit):
    destino = OUT_DIR / spec['familia'] / f'{spec["nome"]}.txt'
    destino.parent.mkdir(parents=True, exist_ok=True)
    meta = {
        'nome': spec['nome'], 'familia': spec['familia'], 'classe': 'principal',
        'das_compat': 'exata', 'instancia_original': spec['instancia_original'],
        'fonte': spec['fonte'], 'problema_original': spec['problema_original'],
        'url': spec['url'], 'referencia': spec['referencia'],
        'transformacao': f'{spec["regra_G"]}; maior componente conexa; não dirigido; passos unitários',
        'regra_ST': spec['regra_ST'] + (f'; rho={spec["rho"]}' if float(spec.get('rho') or 0) else ''),
        'regra_r': f'{spec["regra_r"]} (lambda*={lam:g})', 'seed': spec.get('seed', ''),
        'script': SCRIPT, 'commit_gerador': commit,
        'observacao': spec.get('observacao', ''),
    }
    arestas = sorted({(min(u, v, key=_ordem), max(u, v, key=_ordem))
                      for u, vs in adj.items() for v in vs}, key=lambda e: (_ordem(e[0]), _ordem(e[1])))
    with destino.open('w', encoding='utf-8') as fh:
        for k, v in meta.items():
            fh.write(f'# meta: {k}={v}\n')
        fh.write(f'N {len(adj)}\nM {2 * len(arestas)}\nR {r}\n# u v length\n')
        for u, v in arestas:
            fh.write(f'{u} {v} 1\n{v} {u} 1\n')
        fh.write(f'S {len(S)}\n{" ".join(S)}\nT {len(T)}\n{" ".join(T)}\n')
    return destino


def gerar(spec, commit):
    fonte = ROOT / spec['arquivo_fonte']
    if spec['formato'] == 'stp':
        edges, terminais, papeis = ler_stp(fonte)
    elif spec['formato'] == 'graphml':
        edges, terminais, papeis = ler_graphml(fonte)
    elif spec['formato'] == 'mapf':
        edges, terminais, papeis = ler_mapf(fonte, spec['terminais'])
    else:
        raise ValueError(f'formato desconhecido: {spec["formato"]}')

    adj = maior_componente(aplicar_G(edges, spec['regra_G']))
    if spec['regra_ST'] == 'NATIVO':
        S, T = papeis
        m = int(spec['m'])
        S, T = S[:m], T[:m]
        if not set(S) | set(T) <= set(adj):
            raise ValueError('terminal nativo fora da maior componente')
        if len(set(S)) != m or len(set(T)) != m:
            raise ValueError('terminais nativos repetidos no prefixo do cenário')
    else:
        S, T = dividir_ST(adj, terminais, spec['regra_ST'], spec['m'])
    S, T = aplicar_rho(adj, S, T, spec.get('rho') or 0)
    r, lam = escolher_r(adj, S, T, spec['regra_r'])
    if r >= lam:
        return None, r, lam
    return gravar(spec, adj, S, T, r, lam, commit), r, lam


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--so', nargs='*', help='gera só estas instâncias')
    args = ap.parse_args()
    commit = _commit()
    specs = list(csv.DictReader(SPEC.open(encoding='utf-8')))
    for spec in specs:
        if args.so and spec['nome'] not in args.so:
            continue
        destino, r, lam = gerar(spec, commit)
        estado = 'TRIVIAL (r >= lambda*), não gravada' if destino is None else destino.relative_to(ROOT)
        print(f'{spec["nome"]:34s} r={r} lambda*={lam:g}  {estado}', flush=True)


if __name__ == '__main__':
    main()
