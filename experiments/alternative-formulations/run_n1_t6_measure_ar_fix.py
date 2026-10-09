#!/usr/bin/env python3
"""Adaptador de serializacao para a medicao N1-T6 apos o freeze.

O protocolo pre-registrado conserva o JSON com arcos [[u,v], ...].
As formulacoes F-CC/F-C3 esperam arcos hashable: [(u,v), ...].
Esta correcao e SOMENTE EM MEMORIA; nao reescreve arquivos ou fontes congeladas.

Uso:
    PYTHONHASHSEED=0 python experiments/alternative-formulations/run_n1_t6_measure_ar_fix.py
"""
from __future__ import annotations

import os
import run_n1_t6 as t6


def normalize_arcs_for_solver(graph: dict) -> dict:
    """Cria copia rasa e converte somente A_r; nao altera o JSON/graph_hash."""
    arcs = graph['A_r']
    if not isinstance(arcs, list):
        raise TypeError('A_r deve ser uma lista JSON de pares')
    if any(not isinstance(edge, (list, tuple)) or len(edge) != 2 or
           not all(isinstance(v, str) for v in edge) for edge in arcs):
        raise ValueError('A_r contem arco invalido; recusando conversao silenciosa')
    local = dict(graph)
    local['A_r'] = [tuple(edge) for edge in arcs]
    return local


def measure():
    if os.environ.get('PYTHONHASHSEED') != '0':
        raise RuntimeError('Execute com PYTHONHASHSEED=0')

    # Verifica o freeze, os hashes da T5, os grafos e os certificados originais.
    # Nao modifica nenhum dos elementos verificados.
    t6.checked_certificates()

    original = t6.measure_one

    def corrected(graph, proof, pair_status):
        return original(normalize_arcs_for_solver(graph), proof, pair_status)

    t6.measure_one = corrected
    try:
        t6.measure()  # checkpoint/retomada e todas as validacoes do runner original
    finally:
        t6.measure_one = original


if __name__ == '__main__':
    measure()
