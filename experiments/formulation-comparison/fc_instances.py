"""Comparação base × F-CC+K: carregamento de instâncias e seleção dos lotes.

Não reimplementa leitura de instância nem adjacência: reutiliza `ms_utils`
(mesmo loader usado em todo o projeto) e `instances/manifest.csv` (mesmo
manifesto usado pela N1/N2, 75 instâncias `classe=principal` + 57
`classe=estrutural`). Nenhuma instância é gerada ou alterada aqui.

A seleção dos lotes (piloto/principal/escalabilidade) é derivada de uma
sondagem empírica de tratabilidade da enumeração de W (ver
`tractability_probe`), documentada em
`docs/technical/plans/execucao/formulation-comparison-protocolo.md`.
`lin23`/`lin37` são excluídas por instrução explícita e por serem
`classe=historico` (fora de `principal`/`estrutural`).
"""
from __future__ import annotations

import csv
import hashlib
import math
import signal
import sys
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
for p in (ROOT, ROOT / 'experiments' / 'cuts', ROOT / 'experiments' / 'alternative-formulations'):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from ms_utils import construir_adjacencia, construir_arcos_alcance, ler_instancia  # noqa: E402

MANIFEST = ROOT / 'instances' / 'manifest.csv'
EXCLUDED_NAMES = frozenset({'lin23.txt', 'lin37.txt'})  # classe=historico; instrução explícita


@dataclass(frozen=True)
class Instance:
    """Instância materializada: S, T, V, adj, A_r, r e metadados do manifesto.

    `instance_sha256` é sempre o SHA dos bytes reais (`sha256` do manifesto).
    `sha256_conteudo` é verificado separadamente excluindo linhas `# meta:`.
    """
    nome: str
    caminho: str
    classe: str
    familia: str
    n: int
    m_arestas: int
    r: float
    m: int
    S: tuple
    T: tuple
    V: tuple
    adj: dict
    A_r: tuple
    instance_sha256: str
    instance_content_sha256: str = ""
    metadata_checks: dict | None = None


def _familia(caminho):
    partes = caminho.split('/')
    if 'benchmark-v1' in partes:
        return partes[partes.index('benchmark-v1') + 1]
    if 'estrutural' in partes:
        return partes[partes.index('estrutural') + 1]
    return 'legado'


def load_manifest(path=MANIFEST):
    with open(path, encoding='utf-8') as fh:
        return list(csv.DictReader(fh))


def _declared(row, field, converter, actual, checks, *, tolerance=None):
    """Valida um campo numérico do manifesto contra o dado efetivamente lido."""
    raw = (row.get(field) or '').strip()
    if not raw:
        checks[field] = {'status': 'NOT_DECLARED'}
        return
    try:
        expected = converter(raw)
    except (ValueError, TypeError) as exc:
        raise ValueError(f'INTEGRITY_ERROR: {field} inválido no manifesto: {raw!r}') from exc
    if isinstance(expected, float) and not math.isfinite(expected):
        raise ValueError(f'INTEGRITY_ERROR: {field} não finito no manifesto')
    match = (math.isclose(actual, expected, rel_tol=0, abs_tol=tolerance)
             if tolerance is not None else actual == expected)
    if not match:
        raise ValueError(f'INTEGRITY_ERROR: metadado {field} divergente: '
                         f'manifesto={expected!r} arquivo={actual!r}')
    checks[field] = {'status': 'MATCH', 'expected': expected, 'observed': actual}


def _source_header(conteudo: bytes):
    """Valida N/M/R declarados dentro do arquivo, sem confiar em warnings de ms_utils."""
    header = {}
    for line in conteudo.decode('utf-8').splitlines():
        words = line.strip().split()
        if len(words) == 2 and words[0] in ('N', 'M', 'R'):
            key = words[0]
            if key in header:
                raise ValueError(f'INTEGRITY_ERROR: cabeçalho {key} duplicado')
            try:
                header[key] = float(words[1]) if key == 'R' else int(words[1])
            except ValueError as exc:
                raise ValueError(f'INTEGRITY_ERROR: cabeçalho {key} inválido') from exc
            if key == 'R':
                break
    return header


def load_instance(row, root=ROOT):
    """Valida bytes, dois contratos de hash e metadados ANTES da otimização."""
    caminho = root / row['caminho']
    conteudo = caminho.read_bytes()
    sha_bytes = hashlib.sha256(conteudo).hexdigest()
    sha_normalizado = hashlib.sha256('\n'.join(
        ln for ln in conteudo.decode('utf-8').splitlines()
        if not ln.startswith('# meta:')
    ).encode('utf-8')).hexdigest()
    digest_bruto = (row.get('sha256') or '').strip()
    digest_conteudo = (row.get('sha256_conteudo') or '').strip()
    if digest_bruto and digest_bruto != sha_bytes:
        raise ValueError(f'INTEGRITY_ERROR: sha256 (bytes) divergente em {caminho}')
    if digest_conteudo and digest_conteudo != sha_normalizado:
        raise ValueError(f'INTEGRITY_ERROR: sha256_conteudo (sem metadados) divergente em {caminho}')
    dados = ler_instancia(str(caminho))
    header = _source_header(conteudo)
    checks = {}
    n = len(dados['V'])
    arcs = len(dados['E'])
    undirected = len({tuple(sorted((u, v))) for u, v, _ in dados['E']})
    if len(dados['S']) != len(dados['T']):
        raise ValueError('INTEGRITY_ERROR: |S| difere de |T| na instância')
    _declared(row, 'n', int, n, checks)
    _declared(row, 'm', int, len(dados['S']), checks)
    _declared(row, 'arestas_nao_dirigidas', int, undirected, checks)
    _declared(row, 'arcos_arquivo', int, arcs, checks)
    _declared(row, 'r_arquivo', float, float(dados['R']), checks, tolerance=1e-9)
    # r_usado pode diferir de R do arquivo para instâncias históricas;
    # ambas as identidades são registradas, jamais confundidas.
    r = float(row['r']) if row.get('r') else float(dados['R'])
    _declared(row, 'r', float, r, checks, tolerance=1e-9)
    _declared(row, 'r_usado', float, r, checks, tolerance=1e-9)
    if 'N' in header and header['N'] != n:
        raise ValueError(f'INTEGRITY_ERROR: N do arquivo={header["N"]} diverge dos nós={n}')
    if 'M' in header and header['M'] != arcs:
        raise ValueError(f'INTEGRITY_ERROR: M do arquivo={header["M"]} diverge dos arcos={arcs}')
    checks['file_N'] = {'status': 'MATCH' if 'N' in header else 'NOT_DECLARED'}
    checks['file_M'] = {'status': 'MATCH' if 'M' in header else 'NOT_DECLARED'}
    # Demais metadados topológicos do manifesto dependem de métricas externas
    # (WL, treewidth, planaridade) não reimplementadas neste loader.
    for field in ('planar', 'classes_wl', 'treewidth_ub', 'frac_folhas',
                  'diametro_exato', 'dificuldade', 'densidade_alcance'):
        if (row.get(field) or '').strip():
            checks[field] = {'status': 'UNSUPPORTED',
                             'reason': 'metrica derivada não recalculada por este loader'}
    checks['sha256'] = {'status': 'MATCH' if digest_bruto else 'NOT_DECLARED'}
    checks['sha256_conteudo'] = {'status': 'MATCH' if digest_conteudo else 'NOT_DECLARED'}
    adj = construir_adjacencia(dados['E'])
    A_r = tuple(construir_arcos_alcance(dados['V'], adj, r))
    return Instance(
        nome=row['nome'], caminho=row['caminho'], classe=row['classe'],
        familia=_familia(row['caminho']), n=n, m_arestas=undirected, r=r,
        m=len(dados['S']), S=tuple(dados['S']), T=tuple(dados['T']), V=tuple(dados['V']),
        adj=dict(adj), A_r=A_r, instance_sha256=sha_bytes,
        instance_content_sha256=sha_normalizado, metadata_checks=checks,
    )


class _Timeout(Exception):
    pass


def _alarm(_signum, _frame):
    raise _Timeout()


def tractability_probe(instance, max_w=200000, wall_guard_s=15):
    """Sonda se a enumeração de conjuntos conexos de W é tratável.

    Não resolve nenhum LP/IP; só conta |W| em H. Retorna
    (tratavel: bool, n_W: int|None, motivo: str). `wall_guard_s` é um teto de
    parede independente de `max_w`, para não travar a sondagem em instâncias
    densas onde a enumeração nunca atinge o cap mas também não termina depressa.
    Requer SIGALRM (não funciona em threads secundárias nem Windows); chame
    sempre na thread principal.
    """
    from fcc import grafo_H, enumerar_conexos
    H = grafo_H(instance.V, instance.A_r)
    anterior = signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(int(wall_guard_s))
    try:
        Ws, truncado = enumerar_conexos(H, list(instance.V), max_w + 1)
    except _Timeout:
        return False, None, f'TIMEOUT_WALL_GUARD({wall_guard_s}s)'
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, anterior)
    if len(Ws) > max_w:
        return False, max_w, f'CAP_EXCEEDED(>{max_w})'
    return True, len(Ws), 'OK'


# Lotes fixados a partir da sondagem empírica registrada no protocolo (não
# recalculados a cada execução: a enumeração de W para instâncias no limite
# do cap já consome alguns segundos cada). Nomes exatamente como aparecem na
# coluna `nome` do manifesto.
PILOT_NAMES = (
    'hb-q4-ndir2-p1-k1-L2.txt',   # n=16, m=6 — HB, tratável, referência histórica N1
    'bp-nao-q2-B2-s0.txt',        # n=16, m=4 — BP, tratável
)

MAIN_NAMES = PILOT_NAMES + (
    'hb-q5-ndir2-p1-k1-L2.txt',    # n=21, m=8 — HB, tratável (referência histórica N1)
    'hb-q6-ndir1-p6-k1-L2.txt',    # n=23, m=11 — HB, tratável, maior ponto tratável encontrado
    'bp-sim-q2-B2-s0.txt',         # n=19, m=4 — BP, tratável
    'bp-nao-q2-B3-s0.txt',         # n=23, m=6 — BP, tratável, maior ponto tratável encontrado
)

# Instâncias que a sondagem (ver protocolo) encontrou ACIMA do cap de
# enumeração de F-CC+K: servem só para documentar a fronteira de
# escalabilidade (Modalidade B/C aplicada apenas à formulação base nelas;
# F-CC+K entra como NOT_MEASURED_CAP_EXCEEDED, nunca 0/omitido em silêncio).
SCALABILITY_NAMES = (
    'hb-q6-ndir1-p2-k1-L2.txt',     # n=25 — HB, logo acima do cap
    'hb-q6-ndir1-p1-k1-L2.txt',     # n=28 — HB, acima do cap
    'hb-q8-ndir1-p1-k1-L2.txt',     # n=38 — HB, acima do cap
    'bp-sim-q2-B3-s0.txt',          # n=26 — BP, logo acima do cap
    'sc-gf2-k3.txt',                # n=21 — SC, acima do cap já no menor tamanho da família
    'sc-rigida-k3-s0.txt',          # n=21 — SC, idem (controle de mesma família)
    'tr-k2-L5-r2-sig2-m2.txt',      # n=18 — TR, tratável (ponto de referência)
    'tr-k3-L5-r2-sig2-m2.txt',      # n=25 — TR, acima do cap
    'b-b06-regiao-f2.txt',          # n=50 — classe=principal, menor instância do benchmark-v1
    'pucn-cc6-2n-seed-r1.txt',      # n=64 — classe=principal (família pucn)
)


def _select(names, rows_by_name):
    missing = [n for n in names if n not in rows_by_name]
    if missing:
        raise KeyError(f'instâncias não encontradas no manifesto: {missing}')
    return [rows_by_name[n] for n in names]


def pool(tier, manifest_path=MANIFEST, root=ROOT):
    """tier em {'pilot','main','scalability'}. Retorna lista de `Instance`."""
    names_map = {'pilot': PILOT_NAMES, 'main': MAIN_NAMES, 'scalability': SCALABILITY_NAMES}
    if tier not in names_map:
        raise ValueError(f"tier deve ser um de {sorted(names_map)}, recebido {tier!r}")
    rows = load_manifest(manifest_path)
    rows_by_name = {r['nome']: r for r in rows}
    for n in EXCLUDED_NAMES:
        rows_by_name.pop(n, None)
    selected = _select(names_map[tier], rows_by_name)
    return [load_instance(r, root=root) for r in selected]
