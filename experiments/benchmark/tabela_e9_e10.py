"""
Gera as tabelas de docs/technical/reference/experimentos/resultados-e9-e10-pli.md a partir
dos CSVs de results/benchmark/ (E9, E10 e, se existir, E10b).

Uso: python experiments/benchmark/tabela_e9_e10.py
"""
import csv
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / 'results' / 'benchmark'


def ler(padrao):
    rows = []
    for arq in sorted(RES.glob(padrao)):
        rows += list(csv.DictReader(arq.open(encoding='utf-8')))
    return rows


def f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def fmt(x, casas=1):
    return '—' if x is None else f'{x:.{casas}f}'.replace('.', ',')


def tabela_e9(man):
    rows = ler('e9_raiz_fatia*.csv')
    print('| Instância | Classe | m | z_LP | +C1 | +C1+C2 | controle | núcleo LB (60 s) | L_bot | LB COMP | UB COMP |')
    print('|---|---|---|---|---|---|---|---|---|---|---|')
    for r in sorted(rows, key=lambda r: (r['classe_dif'] != 'F', r['familia'], r['nome'])):
        mm = man[r['nome']]
        nuc = fmt(f(r['ip_nucleo_bound']), 0)
        if r['ip_nucleo_status'] != '2':
            nuc += ' (TL)'
        print(f"| `{r['nome'][:-4]}` | {r['classe_dif']} | {r['m']} | {fmt(f(r['z_lp']))} | "
              f"{fmt(f(r['root_c1']))} | {fmt(f(r['root_c1c2']))} | {fmt(f(r['root_c1c2c4']))} | "
              f"{nuc} | {r['l_bot']} | {fmt(f(mm['lb']), 0)} | {fmt(f(r['ub_ref']), 0)} |")

    print('\nPor família (só D/A): mediana de controle/LB_COMP e de núcleo/LB_COMP; '
          'núcleo > LB_COMP conta as instâncias em que o núcleo supera o B&B de 600 s.\n')
    print('| Família | D/A | controle / LB COMP | núcleo / LB COMP | núcleo > LB COMP |')
    print('|---|---|---|---|---|')
    fam = {}
    for r in rows:
        if r['classe_dif'] in ('D', 'A'):
            fam.setdefault(r['familia'], []).append(r)
    for nome, g in sorted(fam.items()):
        rc, rn, acima = [], [], 0
        for r in g:
            lb = f(man[r['nome']]['lb'])
            ctrl, nuc = f(r['root_c1c2c4']), f(r['ip_nucleo_bound'])
            if lb:
                if ctrl is not None:
                    rc.append(ctrl / lb)
                if nuc is not None:
                    rn.append(nuc / lb)
                    acima += nuc > lb + 1e-6
        print(f"| `{nome}` | {len(g)} | {fmt(statistics.median(rc), 2) if rc else '—'} | "
              f"{fmt(statistics.median(rn), 2) if rn else '—'} | {acima} |")


def tabela_e10():
    rows = ler('e10_primal_fatia*.csv')
    print('| Instância | n | m | reverse-delete | H3 | UB COMP |')
    print('|---|---|---|---|---|---|')
    for r in sorted(rows, key=lambda r: int(r['n_arcos_alcance'])):
        print(f"| `{r['nome'][:-4]}` | {r['n']} | {r['m']} | {r['n_estacoes_reverse']} | "
              f"{r['n_estacoes_h3'] or '— (não terminou)'} | {fmt(f(r['ub_comp_600s']), 0)} |")
    terminou = [r for r in rows if r['n_estacoes_h3']]
    vence = sum(int(r['n_estacoes_h3']) < int(r['n_estacoes_reverse']) for r in terminou)
    quase_v = sum(int(r['n_estacoes_reverse']) >= 0.9 * int(r['n']) for r in rows)
    print(f'\nH3 terminou em {len(terminou)}/{len(rows)}; entre essas, venceu o reverse-delete em '
          f'{vence}. Reverse-delete devolveu ≥ 90% de V em {quase_v}/{len(rows)}.')


def tabela_e10b():
    rows = ler('e10b_construcao*.csv')
    if not rows:
        return
    comp = {r['nome']: r for r in ler('e10b_comp*.csv')}
    print('| Instância | Regime | núcleo \\|C\\| | reparo | poda | final | LB COMP | UB COMP | '
          'LB c/ start | UB c/ start |')
    print('|---|---|---|---|---|---|---|---|---|---|')
    for r in sorted(rows, key=lambda r: int(r['n_arcos_alcance'])):
        c = comp.get(r['nome'], {})
        print(f"| `{r['nome'][:-4]}` | {r['regime']} | {fmt(f(r['nucleo_obj']), 0)} | "
              f"{r['n_reparo'] or '—'} | {r['n_poda'] or '—'} | {r['n_final'] or '—'} | "
              f"{fmt(f(r['lb_comp_600s']), 0)} | {fmt(f(r['ub_comp_600s']), 0)} | "
              f"{fmt(f(c.get('lb_com_start')), 0)} | {fmt(f(c.get('ub_com_start')), 0)} |")
    for fams in (('mapf', 'vienna'), None):
        g = [r for r in rows if fams is None or r['familia'] in fams]
        v = sum(r['vence_comp600'] == 'True' for r in g)
        rotulo = '+'.join(fams) if fams else 'todas'
        print(f'\nReparo < UB COMP ({rotulo}): {v}/{len(g)}')


def main():
    man = {r['nome']: r for r in csv.DictReader((ROOT / 'instances' / 'manifest.csv').open(encoding='utf-8'))}
    print('## E9\n')
    tabela_e9(man)
    print('\n## E10\n')
    tabela_e10()
    print('\n## E10b\n')
    tabela_e10b()


if __name__ == '__main__':
    main()
