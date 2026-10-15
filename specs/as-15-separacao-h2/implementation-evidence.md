# AS15 — Evidência de implementação local

**Estado:** implementação local verificada; `PASS / GO` independente **não atribuído**.
**Base:** ZIP `min-station(20261015-030610).zip`, acrescido do pré-gate AS15 e do hotfix do sensor fornecidos na conversa. **Commit de origem:** não disponível nesta cópia; não fabricar `source_commit`.

## Entregáveis

- `experiments/cuts/h2_cut.py` — desigualdade imutável, RHS 2, coeficientes 1/2, hash tipado.
- `experiments/cuts/h2_supports.py` — propostas limitadas, determinísticas, usando V, K, Hall e massa fracionária.
- `experiments/cuts/h2_separator.py` — certificação somente por AS14, descarte precoce, orçamento, UNKNOWN conservador, violação, filtro de degeneração, diagnóstico e exportação append-only.
- `experiments/cuts/test_h2_separator.py` — 19 testes diretamente derivados de AS15-01..08 e controles negativos.
- `experiments/cuts/verify_as15_separation.py` — controle físico independente do código do oráculo (mesma autoria que a implementação; **não substitui** revisor externo).
- `experiments/cuts/verify_as15_mutations.py` — sete mutantes de fonte injetados em cópias isoladas.

## Resultado reproduzido

| Verificação | Observado |
|---|---|
| `python -m unittest discover -s experiments/cuts -p 'test_*.py' -q` | **91/91 PASS** (AS13+AS14+pré-gate+AS15) |
| `python experiments/cuts/verify_as15_mutations.py` | **7/7 mutantes mortos**, 0 sobreviventes, workspace não alterado |
| `python experiments/cuts/verify_as15_separation.py` | **91 cortes** emitidos e fisicamente examinados, precisão **100% nos controles** |
| Busca heurística versus suportes exaustivos em microinstâncias | **8/83** suportes encontrados, recall **9,64%** (sem exigência de completude) |
| Testemunha HB (`q=4, ndir=2, p=1`) | COMP+K LP **1,0** → COMP+K+H2 LP **2,0**; H2 `y(V)≥2`, violação **1,0** |
| `validate_spec.py`, `validate_tasks.py` | **0 erros / 0 avisos** em cada |
| Ruff AS15 | **não executado neste ambiente** (binário indisponível) |
| Parecer independente autor ≠ verificador | **pendente** |

Artefatos de auditoria: `as15-local-audit.json`, `as15-local-mutations.json`. O SHA256 dos fontes está no primeiro artefato; hashes de certificado/corte HB também.

## Contrato de segurança

O complemento `V\R` **deve** ser `INFEASIBLE` antes de qualquer linha; `VIABLE` gera `NO_CUT`, `UNKNOWN` gera abstenção. Para `Bhat`, somente `INFEASIBLE` de `V\R + v` permite coeficiente 1. Um resultado `VIABLE`, `UNKNOWN` ou candidato não visitado mantém coeficiente 2. Cortes degenerados `y(R)≥1` são contados, não emitidos como novidade. A busca de suportes **não** certifica cortes.

## Comandos sugeridos no checkout final

```bash
poetry run python -m unittest discover -s experiments/cuts -p 'test_*.py' -q
poetry run python experiments/cuts/verify_as15_separation.py
poetry run python experiments/cuts/verify_as15_mutations.py
poetry run ruff check experiments/cuts/h2_cut.py experiments/cuts/h2_supports.py experiments/cuts/h2_separator.py experiments/cuts/test_h2_separator.py experiments/cuts/verify_as15_separation.py experiments/cuts/verify_as15_mutations.py
```

Não utilizar o resultado local como substituto da R1 independente do Claude Opus. Não modificar COMP+K ou os freezes.
