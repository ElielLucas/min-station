"""
Gera instances/manifest.csv (benchmark-v1 §7): uma linha por arquivo de instância.

- Instâncias antigas (instances/*.txt): proveniência registrada na tabela
  LEGADO abaixo, reconstruída a partir dos conversores e dos relatórios E0–E8.
- Instâncias novas (instances/benchmark-v1/**/*.txt): proveniência lida das
  linhas `# meta: chave=valor` do cabeçalho, escritas por build_benchmark.py.

Dificuldade, LB e UB vêm de results/benchmark/dificuldade_v1*.csv
(experiments/benchmark/run_dificuldade.py) quando existirem.

Atributos (instance_features.py) calculados na autonomia efetivamente usada:
para as antigas, o R dos experimentos (r_usado), que em algumas TNTP difere do
R gravado no arquivo.

Uso: python src/converters/build_manifest.py [--sem-atributos]
"""
import argparse
import csv
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from ms_utils import ler_instancia
from instance_features import calcular_atributos

OUT = ROOT / 'instances' / 'manifest.csv'

STEINLIB_URL = 'https://steinlib.zib.de/steinlib.php'
STEINLIB_REF = 'Koch, Martin, Voss. SteinLib: an updated library on Steiner tree problems in graphs (KMV00)'
PUC_REF = STEINLIB_REF + '; família PUC: Rosseti et al. (2001), a confirmar'
TNTP_URL = 'https://github.com/bstabler/TransportationNetworks'
TNTP_REF = 'Transportation Networks for Research Core Team, TransportationNetworks (TNTP)'
CONV_ST = 'src/converters/steinlib_to_minstation.py'
CONV_TN = 'src/converters/gen_min_station_tntp_to_minstation.py'
TRANS_ST = ('arestas SteinLib nos dois sentidos com pesos originais; terminais '
            'embaralhados (seed 42) e divididos ao meio em S e T')
TRANS_TN = ('subgrafo conexo por BFS; comprimentos em km inteiros (ceil); arcos '
            'dirigidos mantidos; S e T = maiores origens e destinos da matriz O/D, disjuntos')
R_ST = 'R gravado no arquivo; origem da escolha não registrada (não segue a regra por percentil do conversor)'
R_TN = 'percentil 50 das distâncias S-T no arquivo; experimentos usam R das referências históricas'

# nome -> (classe, das, original, problema, transformação, regra_r, r_usado, obs)
LEGADO = {
    'hc9u.txt': ('principal', 'exata', 'hc9u', 'Steiner em grafos (PUC)', TRANS_ST, R_ST, None, ''),
    'hc10p.txt': ('principal', 'via A_r=E (r=1)', 'hc10p', 'Steiner em grafos (PUC)', TRANS_ST, R_ST, None, 'pesos 100-110 e R=150: uma aresta por carga'),
    'hc11p.txt': ('principal', 'via A_r=E (r=1)', 'hc11p', 'Steiner em grafos (PUC)', TRANS_ST, R_ST, None, 'idem'),
    'hc12p.txt': ('principal', 'via A_r=E (r=1)', 'hc12p', 'Steiner em grafos (PUC)', TRANS_ST, R_ST, None, 'idem'),
    'bip42p.txt': ('principal', 'via A_r=E (r=1)', 'bip42p', 'Steiner em grafos (PUC)', TRANS_ST, R_ST, None, 'pesos 101-110 e R=200'),
    'cc10-2p.txt': ('extensao_ponderada', 'nao', 'cc10-2p', 'Steiner em grafos (PUC)', TRANS_ST, R_ST, None, 'OPT=3 (E1)'),
    'cc12-2p.txt': ('extensao_ponderada', 'nao', 'cc12-2p', 'Steiner em grafos (PUC)', TRANS_ST, R_ST, None, 'OPT=6 certificado (E8)'),
    'cc12-2u.txt': ('extensao_ponderada', 'nao', 'cc12-2u', 'Steiner em grafos (PUC)', TRANS_ST, R_ST, None, 'pesos 1-3 apesar do sufixo u'),
    'lin23.txt': ('historico', 'nao', 'lin23', 'Steiner em grafos (LIN, VLSI)', TRANS_ST, R_ST, None, 'fora de escopo por decisão do usuário'),
    'lin37.txt': ('historico', 'nao', 'lin37', 'Steiner em grafos (LIN, VLSI)', TRANS_ST, R_ST, None, 'fora de escopo por decisão do usuário'),
    'fnl4461fst.txt': ('historico', 'nao', 'fnl4461fst', 'Steiner retilíneo (TSPFST)', TRANS_ST, R_ST, None, 'fora de escopo'),
    'Chicago_n400_m1130_st5.txt': ('extensao_dirigida', 'nao', 'Chicago-Sketch', 'fluxo de tráfego', TRANS_TN, R_TN, None, ''),
    'Chicago_n400_m1130_st10.txt': ('extensao_dirigida', 'nao', 'Chicago-Sketch', 'fluxo de tráfego', TRANS_TN, R_TN, None, ''),
    'Chicago_n400_m1130_st15.txt': ('extensao_dirigida', 'nao', 'Chicago-Sketch', 'fluxo de tráfego', TRANS_TN, R_TN, 7, 'arquivo R=26; E4-E8 usam R=7 (OPT=17)'),
    'Barcelona_n930_m2522_st_15.txt': ('extensao_dirigida', 'nao', 'Barcelona', 'fluxo de tráfego', TRANS_TN, R_TN, 5, 'arquivo R=24; E4-E8 usam R=5 (OPT=15)'),
    'Barcelona_n930_m2522_st_25.txt': ('extensao_dirigida', 'nao', 'Barcelona', 'fluxo de tráfego', TRANS_TN, R_TN, None, ''),
    'Barcelona_n930_m2522_st_50.txt': ('extensao_dirigida', 'nao', 'Barcelona', 'fluxo de tráfego', TRANS_TN, R_TN, None, ''),
    'inst_Barcelona_n1020_m2522_st_54.txt': ('extensao_dirigida', 'nao', 'Barcelona', 'fluxo de tráfego', TRANS_TN, R_TN, None, 'cabeçalho N=1020, 930 vértices'),
    'Philadelphia_n800_m2404_st_5.txt': ('extensao_dirigida', 'nao', 'Philadelphia', 'fluxo de tráfego', TRANS_TN, R_TN, 2, 'arquivo R=22; E4-E8 usam R=2 (ref. 41)'),
    'Philadelphia_n800_m2404_st_25.txt': ('extensao_dirigida', 'nao', 'Philadelphia', 'fluxo de tráfego', TRANS_TN, R_TN, None, 'ref. [42,46]'),
    'Philadelphia_n800_m2404_st_39.txt': ('extensao_dirigida', 'nao', 'Philadelphia', 'fluxo de tráfego', TRANS_TN, R_TN, None, ''),
    'inst_Anaheim_n416_m914_st_19.txt': ('extensao_dirigida', 'nao', 'Anaheim', 'fluxo de tráfego', TRANS_TN, R_TN, None, ''),
}
PESADAS = {'lin37.txt', 'fnl4461fst.txt'}

CAMPOS_PROV = ['nome', 'caminho', 'classe', 'das_compat', 'instancia_original', 'fonte',
               'problema_original', 'url', 'referencia', 'transformacao', 'regra_ST', 'regra_r',
               'r_arquivo', 'r_usado', 'seed', 'script', 'commit_gerador', 'sha256',
               'sha256_conteudo', 'observacao']
CAMPOS_AT = ['n', 'arestas_nao_dirigidas', 'arcos_arquivo', 'arcos_sem_reverso', 'pesos_distintos',
             'peso_min', 'peso_max', 'conexo', 'grau_medio', 'grau_max', 'frac_folhas', 'm', 'r',
             'frac_terminais', 'frac_terminais_folha', 'rho_S_inter_T', 'planar', 'classes_wl',
             'frac_classes_wl', 'diametro_saltos', 'diametro_exato', 'treewidth_ub',
             'lambda_estrela', 'demanda_saltos', 'opt_zero', 'n_arcos_alcance',
             'densidade_alcance', 'classe_tamanho', 'regime']
CAMPOS_RES = ['dificuldade', 'lb', 'ub', 'fonte_lb_ub', 'particao']
CAMPOS_MELHOR = ['lb_melhor', 'ub_melhor', 'fonte_melhor']
CAMPOS_GRUPO = ['duplicata_de', 'particoes_do_grupo']
GRUPOS = ROOT / 'instances' / 'grupos_origem.csv'

# Melhores limites provados até agora, fora do protocolo de dificuldade (que só
# roda o baseline com TL 600 s e pode não ter fechado o ótimo). Ver os
# relatórios citados na fonte de cada linha; não confundir com `lb`/`ub` de
# CAMPOS_RES, que são só o resultado daquele protocolo.
_E13 = 'E13, COMP C1+C2+C4, MIPFocus=1, TL 1800 s — resultados-e13-pli.md'

MELHORES = {
    'hc9u.txt': (32, 38, 'LB: núcleo C1+C4-DM (E3); UB: verificado no compacto (E4). '
                         'OPT(hc9u) in [32, 38] segue aberto — resultados-e2-e4-pli.md'),
    'cc10-2p.txt': (3, 3, 'OPT certificado — resultados-e0-e1-pli.md (E1)'),
    'cc12-2p.txt': (6, 6, 'OPT certificado — verify_e8_cc12_opt.py, resultados-e8-pli.md §3'),
    'Chicago_n400_m1130_st15.txt': (17, 17, 'OPT provado no compacto, R=7 — resultados-e8-pli.md'),
    'Barcelona_n930_m2522_st_15.txt': (15, 15, 'OPT provado no compacto, R=5 — resultados-e8-pli.md'),
    'Philadelphia_n800_m2404_st_5.txt': (41, 41, 'referência histórica não reprovada nesta linha, '
                                                  'R=2 — run_e8.py'),
    # E13 contra o protocolo regenerado. Ficaram de fora mapf-empty-32-32-m25-f4
    # (o protocolo tem LB 14 e o E13 tem 13) e mapf-room-32-32-4-m10-f8 (16/18 nos dois).
    'mapf-den312d-m25-f4.txt': (17, 17, _E13),
    'mapf-den312d-m50-f2-rho.txt': (5, 9, _E13),
    'mapf-random-32-32-10-m25-f4.txt': (15, 20, _E13),
    'mapf-random-32-32-10-m50-f8.txt': (54, 68, _E13),
    'mapf-random-64-64-20-m100-f4.txt': (41, 63, _E13),
    'mapf-room-32-32-4-m25-f4-rho.txt': (17, 19, _E13),
    'mapf-warehouse-10-20-10-2-1-m25-f4.txt': (29, 42, _E13),
    'mapf-warehouse-10-20-10-2-1-m50-f8.txt': (81, 117, _E13),
    'vienna-I056-regiao-f4.txt': (9, 11, _E13),
    'vienna-I065-intercalado-f2.txt': (17, 19, _E13),
    'vienna-I065-regiao-f4.txt': (14, 17, _E13),
}


def lado_origem(instancia_original):
    """Lado D/A pelo SHA-256 de instancia_original. Ver regra-particao-origem.md."""
    digest = hashlib.sha256(instancia_original.encode('utf-8')).digest()
    return 'desenvolvimento' if int.from_bytes(digest, 'big') % 3 == 0 else 'avaliacao'


def aplicar_particao_origem(saida):
    """Reatribui só D/A em benchmark-v1. Legado e estrutural não mudam de classe."""
    for linha in saida:
        caminho = linha.get('caminho', '')
        if caminho.startswith('instances/estrutural/'):
            linha['particao'] = 'estrutural'
        elif caminho.startswith('instances/benchmark-v1/'):
            linha['particao'] = lado_origem(linha['instancia_original'])


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_conteudo(path):
    """
    Hash só das linhas que não começam com `# meta:`. O cabeçalho grava
    `commit_gerador=<HEAD>`, então o SHA-256 do arquivo inteiro muda a cada
    commit que regera o benchmark, mesmo sem nenhuma mudança de conteúdo.
    """
    linhas = [ln for ln in path.read_text(encoding='utf-8').splitlines()
              if not ln.startswith('# meta:')]
    return hashlib.sha256('\n'.join(linhas).encode('utf-8')).hexdigest()


def meta_do_cabecalho(path):
    meta = {}
    with path.open(encoding='utf-8') as fh:
        for ln in fh:
            if not ln.startswith('#'):
                if ln.strip():
                    break
                continue
            if ln.startswith('# meta:'):
                chave, _, valor = ln[len('# meta:'):].strip().partition('=')
                meta[chave.strip()] = valor.strip()
    return meta


def linha_legado(path):
    classe, das, orig, prob, trans, regra_r, r_usado, obs = LEGADO[path.name]
    steinlib = trans == TRANS_ST
    dados = ler_instancia(str(path))
    return {
        'nome': path.name, 'caminho': str(path.relative_to(ROOT)), 'classe': classe,
        'das_compat': das, 'instancia_original': orig,
        'fonte': 'SteinLib' if steinlib else 'TNTP', 'problema_original': prob,
        'url': STEINLIB_URL if steinlib else TNTP_URL,
        'referencia': (PUC_REF if 'PUC' in prob else STEINLIB_REF) if steinlib else TNTP_REF,
        'transformacao': trans,
        'regra_ST': 'terminais SteinLib, sorteio seed 42' if steinlib else 'maiores demandas O/D',
        'regra_r': regra_r, 'r_arquivo': dados['R'],
        'r_usado': r_usado if r_usado is not None else dados['R'],
        'seed': 42 if steinlib else '', 'script': CONV_ST if steinlib else CONV_TN,
        'commit_gerador': 'anterior ao controle de versão', 'sha256': sha256(path),
        'sha256_conteudo': sha256_conteudo(path),
        'observacao': obs,
    }, dados


def linha_nova(path):
    meta = meta_do_cabecalho(path)
    dados = ler_instancia(str(path))
    linha = {k: meta.get(k, '') for k in CAMPOS_PROV}
    linha.update(nome=path.name, caminho=str(path.relative_to(ROOT)), sha256=sha256(path),
                 sha256_conteudo=sha256_conteudo(path), r_arquivo=dados['R'], r_usado=dados['R'])
    return linha, dados


def assinatura_estrutural(caminho):
    """N, número de arcos, R, S, T e o conjunto de arcos, sem peso e sem sha256."""
    dados = ler_instancia(str(caminho))
    arcos = tuple(sorted((u, v) for u, v, _w in dados['E']))
    return (
        len(dados['V']),
        len(arcos),
        float(dados['R']),
        tuple(sorted(dados['S'])),
        tuple(sorted(dados['T'])),
        arcos,
    )


def anotar_grupos(saida):
    """Agrupa por instancia_original e marca duplicata estrutural.

    Não altera dificuldade, limites nem partição. A partição já decidida
    continua; o vazamento entre desenvolvimento e avaliação fica registrado
    em particoes_do_grupo e em instances/grupos_origem.csv.
    """
    por_origem = {}
    for linha in saida:
        por_origem.setdefault(linha['instancia_original'], []).append(linha)

    por_assinatura = {}
    for linha in saida:
        caminho = ROOT / linha['caminho']
        por_assinatura.setdefault(assinatura_estrutural(caminho), []).append(linha['nome'])

    canonico = {}
    for nomes in por_assinatura.values():
        if len(nomes) < 2:
            continue
        primeiro = min(nomes)
        for nome in nomes:
            if nome != primeiro:
                canonico[nome] = primeiro

    with GRUPOS.open('w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=[
            'instancia_original', 'n_variantes', 'variantes', 'particoes', 'vazamento',
        ])
        w.writeheader()
        for origem in sorted(por_origem):
            grupo = sorted(por_origem[origem], key=lambda l: l['nome'])
            particoes = [l.get('particao', '') for l in grupo]
            conjunto = set(particoes)
            w.writerow({
                'instancia_original': origem,
                'n_variantes': len(grupo),
                'variantes': ' | '.join(l['nome'] for l in grupo),
                'particoes': ' | '.join(particoes),
                'vazamento': 'sim' if 'desenvolvimento' in conjunto and 'avaliacao' in conjunto else 'nao',
            })

    for linha in saida:
        origem = linha['instancia_original']
        partes = sorted({l.get('particao', '') for l in por_origem[origem]})
        linha['particoes_do_grupo'] = '|'.join(partes)
        linha['duplicata_de'] = canonico.get(linha['nome'], '')


LIMITE_ATRIBUTOS_ESTRUTURAL = 200


def _linhas_estruturais():
    pasta = ROOT / 'instances' / 'estrutural'
    if not pasta.exists():
        return []
    novas = []
    for path in sorted(pasta.rglob('*.txt')):
        linha, dados = linha_nova(path)
        linha['classe'] = 'estrutural'
        linha['particao'] = 'estrutural'
        for k in CAMPOS_RES:
            linha.setdefault(k, '')
        linha['particao'] = 'estrutural'
        for k in CAMPOS_MELHOR:
            linha[k] = ''
        if len(dados['V']) <= LIMITE_ATRIBUTOS_ESTRUTURAL:
            at = calcular_atributos(dados, r=linha['r_usado'])
            linha.update({k: at.get(k) for k in CAMPOS_AT})
        else:
            linha.update({k: '' for k in CAMPOS_AT})
            linha['n'] = len(dados['V'])
            linha['m'] = len(dados['S'])
        novas.append(linha)
    return novas


def aplicar_estrutural():
    """Troca as linhas estruturais e preserva dificuldade, limites e partição do restante."""
    with OUT.open(encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        campos = list(reader.fieldnames)
        saida = [row for row in reader if row.get('classe') != 'estrutural']
    for extra in CAMPOS_GRUPO:
        if extra not in campos:
            campos.append(extra)
    saida.extend(_linhas_estruturais())
    anotar_grupos(saida)
    with OUT.open('w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=campos, extrasaction='ignore')
        w.writeheader()
        w.writerows(saida)
    n_est = sum(1 for row in saida if row.get('classe') == 'estrutural')
    print(f'{len(saida)} linhas, {n_est} estruturais; grupos em {GRUPOS.relative_to(ROOT)}')


def aplicar_repartir_origem():
    """Reatribui particao por grafo de origem. Preserva o restante das colunas."""
    with OUT.open(encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        campos = list(reader.fieldnames)
        saida = list(reader)
    aplicar_particao_origem(saida)
    for extra in CAMPOS_GRUPO:
        if extra not in campos:
            campos.append(extra)
    anotar_grupos(saida)
    with OUT.open('w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=campos, extrasaction='ignore')
        w.writeheader()
        w.writerows(saida)
    n_d = sum(1 for row in saida if row.get('particao') == 'desenvolvimento')
    n_a = sum(1 for row in saida if row.get('particao') == 'avaliacao')
    print(f'{len(saida)} linhas; D={n_d} A={n_a}; grupos em {GRUPOS.relative_to(ROOT)}')


def aplicar_so_grupos():
    """Reescreve só as colunas de grupo. As correções da H17 permanecem."""
    with OUT.open(encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        campos = list(reader.fieldnames)
        saida = list(reader)
    for extra in CAMPOS_GRUPO:
        if extra not in campos:
            campos.append(extra)
    anotar_grupos(saida)
    with OUT.open('w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=campos, extrasaction='ignore')
        w.writeheader()
        w.writerows(saida)
    print(f'{len(saida)} linhas; grupos em {GRUPOS.relative_to(ROOT)}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sem-atributos', action='store_true')
    ap.add_argument('--so-grupos', action='store_true',
                    help='só recalcula duplicata_de, particoes_do_grupo e grupos_origem.csv')
    ap.add_argument('--estrutural', action='store_true',
                    help='reescreve só as linhas classe=estrutural; não recalcula o restante')
    ap.add_argument('--repartir-origem', action='store_true',
                    help='reatribui particao por SHA-256 de instancia_original (regra-particao-origem.md)')
    args = ap.parse_args()
    if args.so_grupos:
        aplicar_so_grupos()
        return
    if args.estrutural:
        aplicar_estrutural()
        return
    if args.repartir_origem:
        aplicar_repartir_origem()
        return

    antigos = OUT.exists() and {row['nome']: row for row in csv.DictReader(OUT.open(encoding='utf-8'))} or {}
    linhas = []
    for path in sorted((ROOT / 'instances').glob('*.txt')):
        if path.name not in LEGADO:
            print(f'[aviso] sem proveniência registrada: {path.name}')
            continue
        linhas.append((path, *linha_legado(path)))
    for path in sorted((ROOT / 'instances' / 'benchmark-v1').rglob('*.txt')):
        linhas.append((path, *linha_nova(path)))
    pasta_est = ROOT / 'instances' / 'estrutural'
    if pasta_est.exists():
        for path in sorted(pasta_est.rglob('*.txt')):
            linhas.append((path, *linha_nova(path)))

    dificuldade = {}
    for arq in sorted((ROOT / 'results' / 'benchmark').glob('dificuldade_v1*.csv')):
        for row in csv.DictReader(arq.open(encoding='utf-8')):
            dificuldade[row['nome']] = row

    saida = []
    for path, linha, dados in linhas:
        estrutural = linha.get('classe') == 'estrutural' or str(path).find('/estrutural/') >= 0
        pular_atributos = (
            args.sem_atributos
            or path.name in PESADAS
            or (estrutural and len(dados['V']) > LIMITE_ATRIBUTOS_ESTRUTURAL)
        )
        if not pular_atributos:
            at = calcular_atributos(dados, r=linha['r_usado'])
            linha.update({k: at.get(k) for k in CAMPOS_AT})
        elif estrutural:
            linha['n'] = len(dados['V'])
            linha['m'] = len(dados['S'])
        velho = antigos.get(linha['nome'], {})
        for k in CAMPOS_RES:
            linha[k] = velho.get(k, '')
        d = dificuldade.get(linha['nome'])
        if d:
            linha.update(dificuldade=d['dificuldade'], lb=d['lb'], ub=d['ub'],
                         fonte_lb_ub=f"{d['metodo']}, TL {d['tl_s']} s, seed {d['seed']}")
        melhor = MELHORES.get(linha['nome'])
        for k in CAMPOS_MELHOR:
            linha[k] = ''
        if melhor:
            lb_m, ub_m, fonte_m = melhor
            linha.update(lb_melhor=lb_m, ub_melhor=ub_m, fonte_melhor=fonte_m)
        saida.append(linha)
        print(f'{linha["nome"]:42s} {linha["classe"]:20s} {linha.get("classe_tamanho", "")} '
              f'{linha.get("regime", "")}', flush=True)

    # partição por grafo de origem (regra-particao-origem.md): SHA-256 de
    # instancia_original; legado e estrutural ficam fora do D/A
    for linha in saida:
        if linha['caminho'].startswith('instances/estrutural/'):
            linha['classe'] = 'estrutural'
        elif not linha['caminho'].startswith('instances/benchmark-v1/'):
            linha['particao'] = 'legado'
    aplicar_particao_origem(saida)

    with OUT.open('w', newline='', encoding='utf-8') as fh:
        anotar_grupos(saida)
        w = csv.DictWriter(fh, fieldnames=CAMPOS_PROV + CAMPOS_AT + CAMPOS_RES + CAMPOS_MELHOR + CAMPOS_GRUPO)
        w.writeheader()
        w.writerows(saida)
    print(f'\n{len(saida)} linhas em {OUT.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
