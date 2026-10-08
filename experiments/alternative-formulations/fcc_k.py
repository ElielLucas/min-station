#!/usr/bin/env python3
"""N1-T3 (braço de controle): F-CC + K sem alterar F-CC histórica.

K é EXATAMENTE o output de prepare_cuts(..., {'C1','C2','C4'}).
O hash é do conjunto ordenado por cortes_ordenados; nas comparações N1,
K deve ser compartilhado com QUALQUER outra formulação que aceite cortes.
Não contém redes F-C3 e não autoriza medir F-C3 sem gate MR-F3.
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'experiments' / 'cuts'))
sys.path.insert(0, str(HERE))

from gurobipy import GRB
from fcc import construir_modelo_fcc
from harness import add_cuts_to_model, prepare_cuts
from cuts import cortes_ordenados


def prepare_k(S, T, V, adj, A_r, r):
    """Retorna (cortes_K, sha256) em ordem/serialização estáveis.

    Hash cobre o conteúdo completo, não somente cardinalidade ou seed.
    """
    K, counts = prepare_cuts(S, T, V, adj, A_r, r, {'C1','C2','C4'})
    K = cortes_ordenados(K)
    canonical = [sorted(str(v) for v in Z) for Z in K]
    payload = json.dumps(canonical, ensure_ascii=False, separators=(',', ':')).encode('utf8')
    digest = hashlib.sha256(payload).hexdigest()
    return K, digest, counts


def build_fcc_plus_k(S, T, V, adj, A_r, r, *, K=None, k_hash=None,
                     max_W=200000, y_fixo=None, integer_y=False):
    """Modelo F-CC LP/separado mais todas as desigualdades unitárias de K.

    Fornecer K do pré-registro impede re-geração de cortes diferentes entre
    braços; o hash de K fornecido é sempre recalculado e conferido.
    """
    if K is None:
        K, digest, _ = prepare_k(S, T, V, adj, A_r, r)
    else:
        K = cortes_ordenados(K)
        canonical = [sorted(str(v) for v in Z) for Z in K]
        digest = hashlib.sha256(json.dumps(canonical, ensure_ascii=False,
                            separators=(',', ':')).encode('utf8')).hexdigest()
    if k_hash is not None and digest != k_hash:
        raise ValueError('K congelado não coincide com o hash fornecido')
    model, y, extra, meta = construir_modelo_fcc(
        S, T, V, A_r, forma='separada', max_W=max_W,
        y_fixo=y_fixo, integer_y=integer_y,
    )
    try:
        n_added = add_cuts_to_model(model, y, K, validate=(S, T, A_r))
        if n_added != len(K):
            raise AssertionError(f'K: {len(K)} cortes, somente {n_added} adicionados')
        model.update()
        meta.update(k_hash=digest, n_K=len(K), n_K_added=n_added,
                    n_vars=model.NumVars, n_cons=model.NumConstrs)
        return model, y, extra, meta
    except Exception:
        model.dispose()
        raise


def lp_fcc_plus_k(S, T, V, adj, A_r, r, *, K=None, k_hash=None,
                  max_W=200000, seed=42, threads=1):
    model, _y, _extra, meta = build_fcc_plus_k(
        S, T, V, adj, A_r, r, K=K, k_hash=k_hash, max_W=max_W,
    )
    try:
        model.Params.OutputFlag = 0
        model.Params.Seed = seed
        model.Params.Threads = threads
        model.Params.Method = 2
        model.optimize()
        if model.Status != GRB.OPTIMAL:
            raise RuntimeError(f'F-CC+K LP sem certificado ótimo: status={model.Status}')
        return float(model.ObjVal), meta
    finally:
        model.dispose()


def fcc_plus_k_y_feasible(S, T, V, adj, A_r, r, C, *, max_W=200000):
    chosen = set(C)
    y_fixo = {v: 1.0 if v in chosen else 0.0 for v in V}
    model, _y, _extra, _meta = build_fcc_plus_k(
        S, T, V, adj, A_r, r, max_W=max_W, y_fixo=y_fixo,
    )
    try:
        model.Params.OutputFlag = 0
        model.Params.DualReductions = 0
        model.optimize()
        if model.Status not in (GRB.OPTIMAL, GRB.INFEASIBLE):
            raise RuntimeError(f'F-CC+K decisão não certificada: status={model.Status}')
        return model.Status == GRB.OPTIMAL
    finally:
        model.dispose()
