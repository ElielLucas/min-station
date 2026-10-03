"""Escrita determinística de instâncias estruturais e proveniência."""

import hashlib
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GERADOR_VERSAO = '1'


def commit_atual():
    try:
        h = subprocess.check_output(
            ['git', 'rev-parse', '--short', 'HEAD'], cwd=ROOT, text=True,
        ).strip()
        sujo = subprocess.call(['git', 'diff', '--quiet'], cwd=ROOT) != 0
        return h + ('-dirty' if sujo else '')
    except (subprocess.CalledProcessError, FileNotFoundError):
        return 'desconhecido'


def sha256_bytes(dados):
    return hashlib.sha256(dados).hexdigest()


def texto_instancia(S, T, V, arestas, r, meta):
    """arestas: pares não dirigidos. O arquivo grava os dois sentidos, ordenados."""
    arcos = []
    for u, v in arestas:
        a, b = (u, v) if str(u) <= str(v) else (v, u)
        arcos.append((a, b, 1))
        arcos.append((b, a, 1))
    arcos = sorted(set(arcos), key=lambda t: (str(t[0]), str(t[1])))
    linhas = []
    for chave in sorted(meta):
        linhas.append(f'# meta: {chave}={meta[chave]}')
    linhas.append(f'N {len(V)}')
    linhas.append(f'M {len(arcos)}')
    linhas.append(f'R {int(r) if float(r) == int(r) else r}')
    linhas.append('# u v length')
    for u, v, w in arcos:
        linhas.append(f'{u} {v} {w}')
    linhas.append(f'S {len(S)}')
    linhas.append(' '.join(str(s) for s in S))
    linhas.append(f'T {len(T)}')
    linhas.append(' '.join(str(t) for t in T))
    linhas.append('')
    return '\n'.join(linhas).encode('utf-8')


def gravar(pasta, nome, S, T, V, arestas, r, meta):
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    meta = dict(meta)
    meta.setdefault('classe', 'estrutural')
    meta.setdefault('das_compat', 'exata')
    meta.setdefault('versao_gerador', GERADOR_VERSAO)
    meta.setdefault('script', 'experiments/structural')
    meta.setdefault('commit_gerador', commit_atual())
    bruto = texto_instancia(S, T, V, arestas, r, meta)
    caminho = pasta / nome
    caminho.write_bytes(bruto)
    return caminho, sha256_bytes(bruto)


def adjacencia(arestas):
    adj = {}
    for u, v in arestas:
        adj.setdefault(u, []).append((v, 1))
        adj.setdefault(v, []).append((u, 1))
    return adj


def conferir_fidelidade(S, T, V, arestas, r):
    if len(S) != len(T):
        raise ValueError(f'|S|={len(S)} |T|={len(T)}')
    if set(S) & set(T):
        raise ValueError('S∩T não é vazio')
    if float(r) != int(r) or int(r) < 1:
        raise ValueError(f'r={r} não é inteiro positivo')
    vistos = set(V)
    if set(S) - vistos or set(T) - vistos:
        raise ValueError('terminal fora de V')
    if len(vistos) != len(V):
        raise ValueError('V tem repetição')
    for u, v in arestas:
        if u == v or u not in vistos or v not in vistos:
            raise ValueError(f'aresta inválida {u}-{v}')
    und = {tuple(sorted((str(u), str(v)))) for u, v in arestas}
    if len(und) != len(arestas):
        raise ValueError('aresta repetida')
