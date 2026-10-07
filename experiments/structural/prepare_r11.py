#!/usr/bin/env python3
"""Materializa o catálogo R11 e congela seus SHA-256 sem executar experimentos.

Este script NÃO chama certificadores, validador, enumeração, baseline, Gurobi
ou F-CC. Ele deve ser executado e o manifesto versionado antes de ``run_r11``.
"""

from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))

from io_instancia import gravar
from r11_catalog import catalogo_oficial

MANIFEST = ROOT / 'instances' / 'estrutural' / 'r11-manifest.csv'


def _pasta(inst):
    return ROOT / 'instances' / 'estrutural' / inst['familia']


def _exigir_commit_limpo():
    try:
        status = subprocess.check_output(
            ['git', 'status', '--porcelain'], cwd=ROOT, text=True,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        raise RuntimeError('não foi possível conferir o estado Git antes da materialização') from exc
    if status:
        raise RuntimeError(
            'prepare_r11.py exige working tree limpa. Commit/versione primeiro a '
            'implementação e a documentação preparatórias; depois materialize os hashes.'
        )


def main():
    _exigir_commit_limpo()
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for inst in catalogo_oficial():
        meta = {
            'nome': inst['id'],
            'familia': inst['familia'],
            'fonte': 'R11 Spec D',
            'referencia': 'pre-registro-r11-certificadores.md',
            'regra_ST': inst['politica'],
            'regra_r': inst['r'],
            'seed': 'hand' if inst['seed'] is None else inst['seed'],
            'papel': inst['papel'],
            'estrato': inst['estrato'],
        }
        if inst.get('radiais'):
            meta['radiais'] = ','.join(map(str, inst['radiais']))
        caminho, digest = gravar(
            _pasta(inst), f'{inst["id"]}.txt',
            inst['S'], inst['T'], inst['V'], inst['arestas'], inst['r'], meta,
        )
        rows.append({
            'id': inst['id'],
            'familia': inst['familia'],
            'estrato': inst['estrato'],
            'n': inst['n'],
            'm': inst['m'],
            'r': inst['r'],
            'seed': '' if inst['seed'] is None else inst['seed'],
            'politica': inst['politica'],
            'radiais': '' if not inst.get('radiais') else ','.join(map(str, inst['radiais'])),
            'arquivo': caminho.relative_to(ROOT).as_posix(),
            'sha256': digest,
        })
        print(inst['id'], digest)

    campos = [
        'id', 'familia', 'estrato', 'n', 'm', 'r', 'seed', 'politica',
        'radiais', 'arquivo', 'sha256',
    ]
    with MANIFEST.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        w.writerows(rows)
    print('manifest', MANIFEST)


if __name__ == '__main__':
    main()
