"""
Lote 1a reproduz as instâncias PUC antigas: mesmos S e T e mesmo dígrafo de
alcance A_r (as antigas com pesos e R do arquivo, as novas sem pesos e r=1).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from ms_utils import ler_instancia, construir_adjacencia, construir_arcos_alcance

PARES = [('hc9u', 'puc-hc9u-seed-r1'), ('hc10p', 'puc-hc10p-seed-r1'),
         ('hc11p', 'puc-hc11p-seed-r1'), ('hc12p', 'puc-hc12p-seed-r1'),
         ('bip42p', 'puc-bip42p-seed-r1'), ('cc12-2u', 'puc-cc12-2u-seed-r1')]


def carregar(path):
    d = ler_instancia(str(path))
    A = set(construir_arcos_alcance(d['V'], construir_adjacencia(d['E']), d['R']))
    return d, A


falhas = 0
for antigo, novo in PARES:
    da, Aa = carregar(ROOT / 'instances' / f'{antigo}.txt')
    dn, An = carregar(ROOT / 'instances' / 'benchmark-v1' / 'puc' / f'{novo}.txt')
    mesmo_ST = set(da['S']) == set(dn['S']) and set(da['T']) == set(dn['T'])
    mesmo_Ar = Aa == An
    esperado_Ar = antigo != 'cc12-2u'  # cc12-2u antigo tem pesos 1-3 e R=2: A_r difere de propósito
    ok = mesmo_ST and (mesmo_Ar == esperado_Ar)
    falhas += not ok
    print(f'{antigo:8s} S,T iguais={mesmo_ST}  A_r igual={mesmo_Ar} (|A_r| {len(Aa)} vs {len(An)})  '
          f'{"OK" if ok else "FALHOU"}')
sys.exit(1 if falhas else 0)
