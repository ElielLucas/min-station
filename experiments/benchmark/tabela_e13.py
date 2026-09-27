"""
Gera as tabelas e o veredito de docs/technical/reference/resultados-e13-pli.md
a partir dos CSVs de results/benchmark/ (e13_base*, e13_longo*).

O veredito sai daqui, não da leitura à mão: o critério foi pré-registrado no
cabeçalho de run_e13.py antes da execução.

Uso: python experiments/benchmark/tabela_e13.py
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / 'results' / 'benchmark'

LIMIAR_PRIMAL = 0.05    # Δ_UB >= 5% conta como queda apreciável
LIMIAR_DUAL = 0.01      # Δ_UB < 1% conta como UB parado
MIN_PRIMAL = 7          # de 13
MIN_DUAL = 9            # de 13


def ler(padrao):
    linhas = []
    for arq in sorted(RES.glob(padrao)):
        linhas += list(csv.DictReader(arq.open(encoding='utf-8')))
    return linhas


def f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def num(x, casas=0):
    return '—' if x is None else f'{x:.{casas}f}'.replace('.', ',')


def pct(x):
    return '—' if x is None else f'{x * 100:+.1f}%'.replace('.', ',')


def status(s):
    return {'2': 'ótimo', '9': 'TL'}.get(str(s), str(s))


def tabela_base(base, longo):
    print('| Instância | Família | m | LB ctrl | UB ctrl | LB focus | UB focus | Δ_UB | '
          'UB 1800 s | Δ_UB 1800 | manifesto |')
    print('|---|---|---|---|---|---|---|---|---|---|---|')
    for r in sorted(base, key=lambda r: (r['familia'], int(r['n_arcos_alcance']))):
        lg = longo.get(r['nome'], {})
        bate = 'bate' if r['controle_bate_manifesto'] == 'True' else '**difere**'
        print(f"| `{r['nome'][:-4]}` | {r['familia']} | {r['m']} | "
              f"{num(f(r['lb_controle']))} | {num(f(r['ub_controle']))} | "
              f"{num(f(r['lb_focus600']))} | {num(f(r['ub_focus600']))} | "
              f"{pct(f(r['delta_ub_600']))} | {num(f(lg.get('ub_focus1800')))} | "
              f"{pct(f(lg.get('delta_ub_1800')))} | {bate} |")


def veredito(base, longo):
    """Δ_UB de cada instância: o melhor entre focus600 e focus1800."""
    deltas = {}
    for r in base:
        d = f(r['delta_ub_600'])
        dl = f(longo.get(r['nome'], {}).get('delta_ub_1800'))
        cands = [x for x in (d, dl) if x is not None]
        deltas[r['nome']] = max(cands) if cands else None

    medidas = {k: v for k, v in deltas.items() if v is not None}
    n = len(base)
    caiu = sum(v >= LIMIAR_PRIMAL for v in medidas.values())
    parado = sum(v < LIMIAR_DUAL for v in medidas.values())

    # o ramo dual foi pré-registrado com "mesmo com TL triplicado": sem a fase longo
    # o veredito é preliminar, e dizê-lo firme seria afirmar o que não foi medido
    com_longo = sum(1 for r in base if f(longo.get(r['nome'], {}).get('delta_ub_1800')) is not None)
    fechadas = sum(1 for r in base if str(r['status_focus600']) == '2')
    falta_longo = n - com_longo - fechadas

    print(f'\nInstâncias: {n}; com Δ_UB medido: {len(medidas)}; '
          f'com fase longo (1800 s): {com_longo}; fecharam em 600 s: {fechadas}.')
    print(f'- Δ_UB ≥ {LIMIAR_PRIMAL:.0%} (queda apreciável): **{caiu}** '
          f'(critério de gap primal: ≥ {MIN_PRIMAL})')
    print(f'- Δ_UB < {LIMIAR_DUAL:.0%} (UB parado): **{parado}** '
          f'(critério de gap dual: ≥ {MIN_DUAL})')

    tl = ('sob ênfase primal e com TL triplicado' if falta_longo == 0
          else 'sob ênfase primal no mesmo TL')
    if caiu >= MIN_PRIMAL:
        v = ('**GAP PRIMAL.** O incumbente do B&B padrão estava longe do que o próprio solver '
             'alcança com ênfase primal. O E11, que ataca o lado dual, não sobe na fila.')
    elif parado >= MIN_DUAL:
        v = (f'**GAP DUAL.** O UB não se move {tl}: o incumbente já está perto do melhor que o '
             'solver acha, e o gap remanescente está no LB. O E11 sobe na fila.')
    else:
        v = ('**INCONCLUSIVO.** Nenhum dos dois ramos pré-registrados foi acionado. Registrar como '
             'tal, sem forçar leitura; o E11 continua condicionado a outra evidência.')
    print(f'\nVeredito: {v}')
    if falta_longo:
        print(f'\n**Preliminar:** {falta_longo} instância(s) ainda sem a fase longo. O ramo dual foi '
              'pré-registrado com "mesmo com TL triplicado"; até essa fase terminar, o veredito vale '
              'para o TL de 600 s apenas.')
    print('\nOs dois ramos comparam contra o incumbente, nunca contra o OPT, que é desconhecido '
          'nestas instâncias — é evidência para priorizar o próximo experimento, não prova.')


def divergencias(base):
    difs = [r for r in base if r['controle_bate_manifesto'] != 'True']
    if not difs:
        print('\nO braço `controle` reproduziu LB e UB do manifesto nas 13 — reprodutibilidade OK.')
        return
    print(f'\n{len(difs)} instância(s) em que o `controle` divergiu do manifesto '
          '(esperado só onde a correção do C4-DM mudou a família de cortes):\n')
    print('| Instância | LB manifesto | LB controle | UB manifesto | UB controle |')
    print('|---|---|---|---|---|')
    for r in difs:
        print(f"| `{r['nome'][:-4]}` | {num(f(r['lb_manifesto']))} | {num(f(r['lb_controle']))} | "
              f"{num(f(r['ub_manifesto']))} | {num(f(r['ub_controle']))} |")


def main():
    base = ler('e13_base*.csv')
    if not base:
        print('sem resultados de e13_base*.csv')
        return
    longo = {r['nome']: r for r in ler('e13_longo*.csv')}
    print('## E13 — primal × dual em MAPF/Vienna\n')
    tabela_base(base, longo)
    veredito(base, longo)
    divergencias(base)


if __name__ == '__main__':
    main()
