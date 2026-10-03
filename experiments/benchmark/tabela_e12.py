"""
Tabelas e veredito do E12 a partir de results/benchmark/e12_fatia*.csv.

Critério de plano-pos-e13.md §4.7. Nenhum número é digitado à mão.

hc11p e w23c23 não podem satisfazer "vence o NUCLEO" (§4.4.2): o plano
registra empate com o núcleo nessas duas, não derrota.
"""
import csv
import math
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / 'results' / 'benchmark'

AVALIACAO = (
    'puc-cc9-2p-seed-r1.txt',
    'puc-cc11-2u-seed-r1.txt',
    'puc-cc12-2u-seed-r1.txt',
    'puc-hc9u-regiao-f4.txt',
    'puc-hc9u-seed-r1.txt',
    'puc-hc11p-seed-r1.txt',
    'puc-w23c23-seed-r1.txt',
    'pucn-cc7-3n-regiao-f2.txt',
    'pucn-cc7-3n-seed-r1.txt',
)
GRAFOS = {
    'hc9u': ('puc-hc9u-regiao-f4.txt', 'puc-hc9u-seed-r1.txt'),
    'cc7-3n': ('pucn-cc7-3n-regiao-f2.txt', 'pucn-cc7-3n-seed-r1.txt'),
}
NAO_ITERAVEL = {'puc-hc11p-seed-r1.txt', 'puc-w23c23-seed-r1.txt'}
PUCN = 'cc7-3n'


def _f(valor):
    try:
        return float(valor)
    except (TypeError, ValueError):
        return None


def ler(out_dir=OUT_DIR):
    linhas = []
    for arq in sorted(out_dir.glob('e12_fatia*.csv')):
        if arq.stat().st_size == 0:
            continue
        linhas += list(csv.DictReader(arq.open(encoding='utf-8')))
    return linhas


def lb_estrela(lb):
    if lb is None:
        return None
    return math.ceil(lb - 1e-6)


def comparar(lb_a, t_a, opt_a, lb_b, t_b, opt_b):
    """Resultado de A contra B: vence, perde ou empate. §4.7."""
    la, lb = lb_estrela(lb_a), lb_estrela(lb_b)
    if la is not None and lb is not None:
        if la >= lb + 1:
            return 'vence'
        if la <= lb - 1:
            return 'perde'
    if opt_a and opt_b and t_a is not None and t_b is not None:
        if t_b >= 10 and t_a <= t_b / 1.5:
            return 'vence'
        if t_a >= 10 and t_a >= 1.5 * t_b:
            return 'perde'
    return 'empate'


def _chave(linhas):
    return {(r['nome'], r['braco'], r['seed'], r['fase']): r for r in linhas}


def _fase_da_seed(seed):
    return 'A' if str(seed) == '42' else 'R'


def resultado_instancia(chave, nome, braco_b, seed):
    """CBI contra braco_b numa seed. Seed 42 está na fase A; 43 e 44, na R."""
    fase = _fase_da_seed(seed)
    a = chave.get((nome, 'CBI', str(seed), fase))
    b = chave.get((nome, braco_b, str(seed), fase))
    if a is None or b is None:
        return None
    opt_a = a['status_nome'] == 'OPTIMAL'
    opt_b = b['status_nome'] == 'OPTIMAL'
    res = comparar(_f(a['lb']), _f(a['t_otimo_s']), opt_a,
                   _f(b['lb']), _f(b['t_otimo_s']), opt_b)
    if braco_b == 'NUCLEO' and nome in NAO_ITERAVEL and res == 'vence':
        res = 'empate'
    return res


def agregar_seeds(chave, nome, braco_b):
    seeds = sorted({s for (n, b, s, fase) in chave
                    if n == nome and b == 'CBI' and fase in ('A', 'R')})
    votos = []
    for seed in seeds:
        res = resultado_instancia(chave, nome, braco_b, seed)
        if res is not None:
            votos.append(res)
    if not votos:
        return None
    if len(votos) == 1:
        return votos[0]
    if votos.count('vence') >= 2:
        return 'vence'
    if votos.count('perde') >= 2:
        return 'perde'
    return 'empate'


def grafo_de(nome):
    for grafo, membros in GRAFOS.items():
        if nome in membros:
            return grafo
    return nome[:-4]


def agregar_grafo(resultados):
    """Vitória só se alguma variante vence e nenhuma perde."""
    if not resultados or any(r is None for r in resultados):
        return None
    if any(r == 'perde' for r in resultados):
        return 'empate' if any(r == 'vence' for r in resultados) else 'perde'
    if any(r == 'vence' for r in resultados):
        return 'vence'
    return 'empate'


def na_margem(chave, nome):
    a = chave.get((nome, 'CBI', '42', 'A'))
    b = chave.get((nome, 'COMP', '42', 'A'))
    if a is None or b is None:
        return False
    la, lb = lb_estrela(_f(a['lb'])), lb_estrela(_f(b['lb']))
    if la is not None and lb is not None and abs(la - lb) <= 1:
        return True
    if a['status_nome'] == 'OPTIMAL' and b['status_nome'] == 'OPTIMAL':
        ta, tb = _f(a['t_otimo_s']), _f(b['t_otimo_s'])
        if ta and tb and (1 / 1.5) <= ta / tb <= 1.5:
            return True
    return False


def instancias_margem(out_dir=OUT_DIR):
    chave = _chave(ler(out_dir))
    return [nome for nome in AVALIACAO if na_margem(chave, nome)]


def _cel_lb(row):
    if row is None:
        return '—'
    v = lb_estrela(_f(row['lb']))
    return '—' if v is None else str(v)


def _cel_ub(row):
    if row is None:
        return '—'
    v = _f(row['ub'])
    if v is None:
        return '—'
    return str(lb_estrela(v))


def _cel_t(row):
    if row is None:
        return '—'
    v = _f(row['t_metodo_s'])
    if v is None:
        return '—'
    return f'{v:.1f}'.replace('.', ',')


def _cel_st(row):
    if row is None:
        return '—'
    if row['status_nome'] == 'OPTIMAL':
        return 'ótimo'
    if row['status_nome'] == 'TIME_LIMIT':
        return 'TL'
    return row['status_nome']


def _linha(chave, nome, seed, fase, com_voto):
    celulas = [f'`{nome[:-4]}`', str(seed)]
    for braco in ('COMP', 'NUCLEO', 'CBI'):
        row = chave.get((nome, braco, str(seed), fase))
        celulas += [_cel_lb(row), _cel_ub(row), _cel_st(row), _cel_t(row)]
    cbi = chave.get((nome, 'CBI', str(seed), fase))
    if cbi is None:
        celulas += ['—', '—']
    else:
        celulas += [cbi['iteracoes'] or '—', cbi['n_z'] or '—']
    if com_voto:
        celulas.append(resultado_instancia(chave, nome, 'COMP', seed) or '—')
        celulas.append(resultado_instancia(chave, nome, 'NUCLEO', seed) or '—')
    return '| ' + ' | '.join(celulas) + ' |'


def _cabecalho(com_voto):
    base = ('| Instância | seed | COMP LB* | UB | st | t | '
            'NUCLEO LB* | UB | st | t | CBI LB* | UB | st | t | iter | n_z |')
    sep = '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|'
    if com_voto:
        base += ' vs COMP | vs NUCLEO |'
        sep += '---|---|'
    print(base)
    print(sep)


def _blococ(chave, nomes, seeds, fase, com_voto):
    _cabecalho(com_voto)
    for nome in nomes:
        for seed in seeds:
            if chave.get((nome, 'COMP', str(seed), fase)) is None:
                continue
            print(_linha(chave, nome, seed, fase, com_voto))


def tabelas(linhas):
    """Tabelas de LB* = ceil(LB − 1e-6). Não altera o critério de veredito()."""
    chave = _chave(linhas)
    aval = [n for n in AVALIACAO if (n, 'COMP', '42', 'A') in chave]
    controles = []
    dev = []
    for row in linhas:
        if row['fase'] == 'D' and row['nome'] not in dev:
            dev.append(row['nome'])
        if row['fase'] == 'A' and row['nome'] not in AVALIACAO and row['nome'] not in controles:
            controles.append(row['nome'])

    print('### Avaliação, seed 42')
    print()
    _blococ(chave, aval, ('42',), 'A', True)
    print()
    print('### Re-seeds 43 e 44')
    print()
    _blococ(chave, aval, ('43', '44'), 'R', True)
    print()
    print('### Agregado por instância (vitória ou derrota exige 2 de 3 seeds)')
    print()
    print('| Instância | contra COMP | contra NUCLEO |')
    print('|---|---|---|')
    for nome in aval:
        print(f'| `{nome[:-4]}` | {agregar_seeds(chave, nome, "COMP")} | '
              f'{agregar_seeds(chave, nome, "NUCLEO")} |')
    print()
    print('### Controles MAPF, seed 42')
    print()
    _blococ(chave, controles, ('42',), 'A', False)
    print()
    print('### Desenvolvimento, seed 42')
    print()
    _blococ(chave, dev, ('42',), 'D', False)
    print()
    commits = defaultdict(set)
    for row in linhas:
        commits[row['fase']].add(row['commit'])
    print('### Commits por fase')
    print()
    for fase in sorted(commits):
        print(f'- fase {fase}: {", ".join(sorted(commits[fase]))}')
    manifesto = ROOT / 'instances' / 'manifest.csv'
    por_nome = {r['nome']: r for r in csv.DictReader(manifesto.open(encoding='utf-8'))}
    nomes = sorted({r['nome'] for r in linhas})
    ruins = [n for n in nomes if por_nome[n]['rho_S_inter_T'] not in ('0', '0.0', '0.00')]
    print()
    print('### Checagem')
    print()
    print(f'- instâncias no CSV: {len(nomes)}')
    print(f'- S∩T não vazio no manifesto: {len(ruins)} {ruins}')
    print(f'- linhas: {len(linhas)}')


def veredito(linhas):
    chave = _chave(linhas)
    por_grafo = defaultdict(list)
    for nome in AVALIACAO:
        por_grafo[grafo_de(nome)].append(nome)

    print('| Grafo | contra COMP | contra NUCLEO |')
    print('|---|---|---|')
    vence_comp = []
    vence_nucleo = []
    for grafo, membros in sorted(por_grafo.items()):
        rc = agregar_grafo([agregar_seeds(chave, n, 'COMP') for n in membros])
        rn = agregar_grafo([agregar_seeds(chave, n, 'NUCLEO') for n in membros])
        print(f'| `{grafo}` | {rc} | {rn} |')
        if rc == 'vence':
            vence_comp.append(grafo)
            if rn == 'vence':
                vence_nucleo.append(grafo)
    n = len(vence_comp)
    tem_pucn = PUCN in vence_comp
    tem_iter = bool(vence_nucleo)
    if n >= 3 and tem_pucn and tem_iter:
        leitura = 'A2 segue para Das: a iteração com Z acrescenta algo ao núcleo'
    elif n >= 3 and tem_pucn:
        leitura = ('o ganho é do núcleo, não da iteração. '
                   'A2 como CBI é encerrada para Das')
    else:
        leitura = 'A2 encerrada para Das'
    print(f'\nVitórias contra COMP: {n} {vence_comp}')
    print(f'Também vencem o NUCLEO: {vence_nucleo}')
    print(f'Veredito: {leitura}')
    print(f'Margem (re-seed): {instancias_margem()}')


def main():
    linhas = ler()
    if not linhas:
        print('sem CSV do E12')
        return 1
    tabelas(linhas)
    print()
    veredito(linhas)
    return 0


if __name__ == '__main__':
    sys.exit(main())
