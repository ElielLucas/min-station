#!/usr/bin/env python3
"""T18: OPT da desagregação coincide com a base e com a enumeração."""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAIZ = HERE.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / 'experiments' / 'cuts'))

from baseline import construir_modelo_baseline
from desagregacao import medir_par
from independent_validator import opt_por_enumeracao
from synthetic import make_CaminhoABC, make_StayPutIsolado, make_Tri


def main():
    falhas = []
    for nome, fabrica in (
        ('Tri', make_Tri),
        ('CaminhoABC', make_CaminhoABC),
        ('StayPutIsolado', make_StayPutIsolado),
    ):
        S, T, V, adj, A_r, r, meta = fabrica()
        linha = medir_par(S, T, V, A_r, construir_modelo_baseline)
        enumerado = opt_por_enumeracao(S, T, V, adj, r)
        print(
            f'{nome}: zLP base={linha["z_lp_base"]:.4f} des={linha["z_lp_des"]:.4f} '
            f'OPT base={linha["opt_base"]:.0f} des={linha["opt_des"]:.0f} enum={enumerado} '
            f'vars {linha["vars_base"]}→{linha["vars_des"]} '
            f'montar {linha["t_montar_base"]:.4f}s→{linha["t_montar_des"]:.4f}s '
            f'lp {linha["t_lp_base"]:.4f}s→{linha["t_lp_des"]:.4f}s'
        )
        if abs(linha['opt_base'] - linha['opt_des']) > 1e-6 or enumerado != int(round(linha['opt_base'])):
            falhas.append(f'{nome}: OPT divergente')
        if nome == 'Tri' and (abs(linha['opt_des'] - 2) > 1e-6 or abs(linha['z_lp_base'] - 1) > 1e-6):
            falhas.append(f'Tri fora do esperado: {linha}')
    if falhas:
        for f in falhas:
            print('FALHA:', f)
        raise SystemExit(1)
    print('ok')


if __name__ == '__main__':
    main()
