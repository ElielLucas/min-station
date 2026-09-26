"""
Verificação de primal.build_primal_from_core (construtor do E10b) nos
gabaritos de synthetic.py, cujo OPT é conhecido analiticamente.

Critério, por gabarito:
  1. a solução devolvida é viável, checada por integer_oracle;
  2. |C| >= OPT (nenhum construtor pode bater o ótimo);
  3. quando o núcleo já é viável, o construtor não o piora.

Também exercita o caso em que a solução do núcleo é INVIÁVEL (Sec59): o
núcleo é um relaxamento em espaço-y, sem acoplamento de fluxo, então C_núcleo
pode não admitir emparelhamento — é exatamente o que o reparo existe para
corrigir.

Uso: python experiments/cuts/verify_e10b_primal.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

import synthetic as syn
from cuts import build_neighborhoods, integer_oracle
from primal import build_primal_from_core
from yspace import solve_ip_yspace

GABARITOS = [
    ('F1(2,2)', syn.make_F1, dict(m=2, k=2, r=1)),
    ('F1(2,3)', syn.make_F1, dict(m=2, k=3, r=1)),
    ('F2(k=1)', syn.make_F2, dict(k=1, L=3, r=1)),
    ('Tri', syn.make_Tri, dict(r=1)),
    ('Sec59(L=7)', syn.make_Sec59, dict(L=7, r=1)),
    ('Direct0', syn.make_Direct0, dict(r=1)),
    ('TermRelay', syn.make_TermRelay, dict(r=1)),
    ('StayPut', syn.make_StayPut, dict(r=1)),
    ('SharedTerminal', syn.make_SharedTerminal, dict(r=1)),
    ('TermRelayForced', syn.make_TermRelayForced, dict(r=1)),
]


def main():
    falhas = []
    print(f'{"gabarito":20s} {"OPT":>5s} {"nucleo":>7s} {"viav?":>6s} '
          f'{"reparo":>7s} {"poda":>5s} {"final":>6s}  veredito')
    for label, fn, kw in GABARITOS:
        S, T, V, adj, A_r, r, meta = fn(**kw)
        N_plus, _ = build_neighborhoods(A_r)
        opt = meta['OPT']

        nuc = solve_ip_yspace(S, T, V, adj, A_r, r, time_limit=30, seed=42, threads=1)
        C0 = nuc['C']
        if C0 is None:
            falhas.append(f'{label}: nucleo sem solucao')
            continue
        nucleo_viavel = integer_oracle(S, T, N_plus, C0)[0]

        res = build_primal_from_core(S, T, V, N_plus, C0, seed=42, total_budget=30.0)
        if res is None:
            falhas.append(f'{label}: construtor nao devolveu solucao viavel')
            print(f'{label:20s} {opt:5.0f} {len(C0):7d} {str(nucleo_viavel):>6s} '
                  f'{"—":>7s} {"—":>5s} {"—":>6s}  FALHA')
            continue

        problemas = []
        if not integer_oracle(S, T, N_plus, res['C'])[0]:
            problemas.append('solucao final INVIAVEL')
        if res['n_estacoes'] < opt - 1e-6:
            problemas.append(f'|C|={res["n_estacoes"]} < OPT={opt:.0f}')
        if nucleo_viavel and res['n_estacoes'] > len(C0):
            problemas.append(f'piorou nucleo viavel: {len(C0)} -> {res["n_estacoes"]}')

        veredito = 'ok' if not problemas else 'FALHA: ' + '; '.join(problemas)
        if problemas:
            falhas.append(f'{label}: ' + '; '.join(problemas))
        marca = '' if res['n_estacoes'] > opt + 1e-6 else ' (=OPT)'
        print(f'{label:20s} {opt:5.0f} {len(C0):7d} {str(nucleo_viavel):>6s} '
              f'{res["n_reparo"]:7d} {res["n_poda"]:5d} {res["n_estacoes"]:6d}  '
              f'{veredito}{marca}')

    print()
    if falhas:
        print(f'{len(falhas)} falha(s):')
        for f in falhas:
            print('  -', f)
        return 1
    print(f'{len(GABARITOS)} gabaritos: solucao viavel e >= OPT em todos.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
