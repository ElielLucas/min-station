#!/usr/bin/env python3
"""Gráfico de evolução LB/UB x tempo a partir de um `evolution.csv` real.

Não inventa pontos: plota exatamente os registros gravados por
`fc_core.EvolutionTracker` (marcos cruzados + ponto final), um ponto por
chamada de callback que cruzou um marco. Uso:

    python fc_plot_evolution.py <evolution.csv> <instance_name> <out.png>
"""
from __future__ import annotations

import csv
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402


def load_points(csv_path, instance_name):
    por_formulacao = {}
    with open(csv_path, newline='', encoding='utf-8') as fh:
        for row in csv.DictReader(fh):
            if row['instance_name'] != instance_name:
                continue
            por_formulacao.setdefault(row['formulation'], []).append(row)
    for pts in por_formulacao.values():
        pts.sort(key=lambda r: float(r['observed_time_s']))
    return por_formulacao


def plot(csv_path, instance_name, out_path):
    dados = load_points(csv_path, instance_name)
    if not dados:
        raise SystemExit(f'nenhum ponto para {instance_name!r} em {csv_path}')
    fig, ax = plt.subplots(figsize=(7, 4.5))
    cores = {'baseline': 'tab:blue', 'fcc_k': 'tab:orange'}
    for formulacao, pontos in sorted(dados.items()):
        t = [float(p['observed_time_s']) for p in pontos]
        lb = [float(p['lb']) if p['lb'] != '' else None for p in pontos]
        ub = [float(p['ub']) if p['ub'] != '' else None for p in pontos]
        cor = cores.get(formulacao, 'tab:gray')
        ax.plot(t, lb, marker='o', linestyle='-', color=cor, label=f'{formulacao} LB (ObjBound)')
        ax.plot(t, ub, marker='s', linestyle='--', color=cor, alpha=0.7,
               label=f'{formulacao} UB (incumbente)')
    ax.set_xlabel('tempo observado (s) — pontos reais, não interpolados')
    ax.set_ylabel('valor do objetivo (estações)')
    ax.set_title(f'Evolução LB/UB — {instance_name}')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f'gráfico salvo em {out_path}')


if __name__ == '__main__':
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    plot(sys.argv[1], sys.argv[2], sys.argv[3])
