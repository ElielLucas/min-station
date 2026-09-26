"""
Regenera o benchmark-v1 num diretório temporário e compara o hash de conteúdo
(sha256_conteudo do manifesto) com o gravado em instances/manifest.csv.

Só o conteúdo é comparado, não o SHA-256 do arquivo inteiro: cada instância
grava `# meta: commit_gerador=<HEAD>` no cabeçalho, então regerar depois de um
novo commit muda o SHA-256 do arquivo mesmo sem nenhuma mudança de conteúdo.
Ver build_manifest.sha256_conteudo.

Uso: python experiments/benchmark/verify_regeneracao.py
"""
import csv
import importlib
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'src' / 'converters'))

import build_benchmark as bb  # noqa: E402
from build_manifest import sha256_conteudo  # noqa: E402

MANIFESTO = ROOT / 'instances' / 'manifest.csv'


def main():
    manifesto = {row['nome']: row['sha256_conteudo'] for row in
                 csv.DictReader(MANIFESTO.open(encoding='utf-8'))
                 if row['caminho'].startswith('instances/benchmark-v1/')}
    if not manifesto:
        print('[erro] nenhuma linha de benchmark-v1 no manifesto; rode build_manifest.py antes')
        sys.exit(1)

    with tempfile.TemporaryDirectory() as tmp:
        bb.OUT_DIR = Path(tmp)
        commit = bb._commit()
        specs = list(csv.DictReader(bb.SPEC.open(encoding='utf-8')))

        gerados, faltando, divergentes = {}, [], []
        for spec in specs:
            destino, _, _ = bb.gerar(spec, commit)
            if destino is None:
                continue
            gerados[spec['nome'] + '.txt'] = sha256_conteudo(destino)

        for nome, hash_manifesto in manifesto.items():
            hash_novo = gerados.get(nome)
            if hash_novo is None:
                faltando.append(nome)
            elif hash_novo != hash_manifesto:
                divergentes.append(nome)

    print(f'{len(manifesto)} instâncias no manifesto; {len(gerados)} regeneradas nesta rodada')
    if faltando:
        print(f'[FALHOU] {len(faltando)} não regeneradas (ficaram triviais ou saíram do spec):')
        for n in faltando:
            print(f'  {n}')
    if divergentes:
        print(f'[FALHOU] {len(divergentes)} com conteúdo divergente do manifesto:')
        for n in divergentes:
            print(f'  {n}')
    ok = not faltando and not divergentes
    print('OK: regeneração reproduz o conteúdo do manifesto' if ok else 'FALHOU')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
