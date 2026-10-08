#!/usr/bin/env python3
"""N1-T0: confere referências literais com caminhos de raiz em Markdown/Python.

Não interpreta exemplos genéricos de skills como artefatos reais nem confunde
permalinks fixados em commits com caminhos do filesystem local.
"""
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RE = re.compile(r'(?<![\w/])(?:docs|experiments|specs|src|instances|results)/[\w.\-/]+\.(?:md|py|txt|csv)')
MARKDOWN_LINK = re.compile(r'\]\(([^\s#)]+\.(?:md|py|txt|csv))(?:#[^)]+)?\)')
SKIP_SOURCE = ROOT / 'docs/technical/reference/formulacoes/formulacao-fc3-componentes-trios.md'
# N1-T4 requires the historical collector to remain byte-for-byte unchanged.
SKIP_PROTECTED = {ROOT / 'experiments/benchmark/run_r7_plato.py'}


def links_missing():
    filenames = defaultdict(list)
    for path in ROOT.rglob('*'):
        if path.is_file():
            filenames[path.name].append(path)
    moved, other = [], []
    for path in ROOT.rglob('*'):
        if path.suffix not in ('.md', '.py') or '.git' in path.parts:
            continue
        if ('pre-registro' in path.name or '.claude' in path.parts or path == SKIP_SOURCE
                or path in SKIP_PROTECTED or path.name == 'n1-t0-changelog-caminhos.md'):
            continue
        for number, line in enumerate(path.read_text(encoding='utf8', errors='replace').splitlines(), 1):
            if ('https://' in line and ('/blob/' in line or '/commit/' in line)) or '--saida ' in line:
                continue
            for link in MARKDOWN_LINK.finditer(line):
                target = link.group(1)
                if ('://' in target or target.startswith(('sandbox:', 'data:'))
                        or (path.parent / target).exists() or (ROOT / target).exists()):
                    continue
                entry = (str(path.relative_to(ROOT)), number, target)
                if len(filenames[Path(target).name]) == 1:
                    moved.append(entry)
                else:
                    other.append(entry)
            for m in RE.finditer(line):
                token = m.group()
                if (ROOT / token).exists():
                    continue
                entry = (str(path.relative_to(ROOT)), number, token)
                if len(filenames[Path(token).name]) == 1:
                    moved.append(entry)
                else:
                    other.append(entry)
    return moved, other


def main():
    moved, other = links_missing()
    for category, entries in (('MOVIDO', moved), ('NAO_RESOLVIDO', other)):
        for name, line, target in entries:
            print(f'{category} {name}:{line} -> {target}')
    for selected in ('CLAUDE.md', 'RESEARCH.md'):
        if any(x[0] == selected for x in moved + other):
            raise AssertionError(f'{selected}: caminhos quebrados')
    if any(x[0].startswith('docs/context-ai/') for x in moved + other):
        raise AssertionError('docs/context-ai: caminhos quebrados')
    if moved:
        raise AssertionError(f'{len(moved)} referencias a arquivos existentes em outros caminhos')
    print(f'PASS: 0 referências movidas; {len(other)} exemplos/ausências sem correspondente único')


if __name__ == '__main__':
    main()
