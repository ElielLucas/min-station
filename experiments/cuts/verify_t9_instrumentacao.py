#!/usr/bin/env python3
"""T9: tempos de incumbente em measure_mip, sem mudar os campos já publicados."""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

import synthetic as syn
from harness import measure_mip

CAMPOS_ANTIGOS = (
    'mip_obj', 'mip_bound', 'mip_gap', 'mip_status',
    'sol_count', 'node_count', 'time_mip_s',
)


def checar(rotulo, S, T, V, A_r, coletar):
    res = measure_mip(
        S, T, V, A_r, 'int', [],
        seed=42, threads=1, time_limit=30,
        coletar_incumbente=coletar,
    )
    faltando = [c for c in CAMPOS_ANTIGOS if c not in res]
    if faltando:
        raise SystemExit(f'{rotulo}: campos antigos ausentes: {faltando}')
    if coletar:
        primeiro = res['time_to_first_incumbent_s']
        melhor = res['time_to_best_incumbent_s']
        if primeiro is None or melhor is None:
            raise SystemExit(f'{rotulo}: incumbente não registrado')
        if not (primeiro <= melhor <= res['time_mip_s'] + 1e-6):
            raise SystemExit(f'{rotulo}: ordem dos tempos inválida {primeiro}, {melhor}, {res["time_mip_s"]}')
        if res['sol_count'] == 1 and abs(primeiro - melhor) > 1e-6:
            raise SystemExit(f'{rotulo}: um incumbente e tempos diferentes')
        if res['time_to_proof_s'] is None:
            raise SystemExit(f'{rotulo}: prova não registrada em status ótimo')
    else:
        if res['time_to_first_incumbent_s'] is not None:
            raise SystemExit(f'{rotulo}: callback ligado com a coleta desligada')
    print(f'{rotulo}: obj={res["mip_obj"]} nos={res["node_count"]} '
          f'primeiro={res["time_to_first_incumbent_s"]} '
          f'melhor={res["time_to_best_incumbent_s"]} '
          f'prova={res["time_to_proof_s"]}')


def main():
    S, T, V, _adj, A_r, _r, meta = syn.make_CaminhoABC()
    checar(meta['name'] + '/com', S, T, V, A_r, True)
    checar(meta['name'] + '/sem', S, T, V, A_r, False)
    S, T, V, _adj, A_r, _r, meta = syn.make_TermRelay()
    checar(meta['name'] + '/com', S, T, V, A_r, True)
    print('ok')


if __name__ == '__main__':
    main()
