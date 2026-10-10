# MIN-STATION — Fechamento da fase N2

**Estado:** `ENCERRADA`  
**Decisão pré-registrada:** **`N2 FAIL`**  
**Data:** 2026-10-10 (`America/Sao_Paulo`)  
**Caminho analisado:** B — F-CC+K, root-only, sem branching.

## 1. Registro de conclusão

| Etapa | Encerramento | Evidência principal |
|---|---|---|
| N2-T1 | Concluída | Freeze `b036e9d0fe8f446dfcaca2716df85054c73dbb8702484aacce3c807e6574de71` |
| N2-T2B | Concluída | Master/dual/pricing e gates M/O anteriores |
| N2-T3 | Concluída | E1–E5, certificação racional N1/ENUM/N2, revalidação K/E5 e aceite |
| N2-T4 | Aceita com exceção explícita | 22 controles CG + `Direct0` com prova exata independente; um controle sem LP excluído |
| N2-T5 | Execução e registro concluídos | 4/4 limites físicos certificados, 4 famílias-níveis cobertas, custo abaixo do teto |
| N2-T6 | **Fechada — N2 FAIL** | 13/13 testes e Ruff PASS; `VERIFY_ARTIFACT_BYTES...` concluído no checkout local, segundo log do responsável |

> **Nota:** o literal efetivamente emitido pelo auditor é `VERIFIED_ARTIFACT_BYTES_AND_TABULAR_INVARIANTS`. Não se declara reauditoria independente da prova E5 por este registro.

## 2. Decisão científica

| Caso | B0 (referência, não E5-certificado) | LB físico certificado | Ganho exato | Work |
|---|---:|---:|---:|---:|
| HB nível 1 | `1` | `1/2` | `−1/2` | 0,417963 |
| BP nível 1 | `6` | `1` | `−5` | 0,083058 |
| HB nível 2 | `11500000000000001/10000000000000000` | `2/3` | `−14500000000000003/30000000000000000` | 1,364441 |
| BP nível 2 | `8` | `18/13` | `−86/13` | 0,670544 |

**Ganho certificado positivo:** `0/4`. **Recuperação mínima de 50%:** `0/2` casos de nível 1 com LP completo histórico (`−1/2` e `−5`). **G2:** não demonstrado (`NOT_CONVERGED_CERTIFIED` em todas as linhas). **Work máximo:** `1,364442`, abaixo do teto `164`.

A regra congelada exige ganho acima de B0 nas duas famílias e nos dois tamanhos e recuperação ≥50% do incremento LP conhecido. Logo, a decisão obrigatória é **`N2 FAIL`**. Esse resultado negativo é válido para este protocolo e implementação; não constitui prova de impossibilidade de melhorar F-CC+K em novos estudos.

## 3. Evidência de auditoria e alcance do aceite

O pesquisador compartilhou em 2026-10-10 os seguintes resultados executados no próprio checkout:

- Testes `test_n2_t6_gate.py`: **13/13 PASS**;
- Ruff (`verify_n2_t6_gate.py`, `test_n2_t6_gate.py`): **All checks passed!**;
- Auditor `verify_n2_t6_gate.py`: `audit_status=VERIFIED_ARTIFACT_BYTES_AND_TABULAR_INVARIANTS`; `decision=N2 FAIL`; SHA-256 dos quatro artefatos prospectivos coincidentes com o manifesto.

Os hashes completos constam em `n2-t6-gate-decisao-cientifica.md`. A presente documentação registra a **auditoria local reportada**, não acesso independente aos arquivos originais e não uma nova prova matemática.

**Pendências administrativas de rastreabilidade** (não impedem o fechamento da decisão): SHA-256 do `n2-t5-manifest.json`, `git rev-parse HEAD` do checkout e, se necessário, revisão independente adicional. Não fabricar esses identificadores.

## 4. Consequências e preservação

- **N3 bloqueada** sob o protocolo congelado; não iniciar branch-and-price para compensar a reprovação.
- Preservar freezes, scripts, N1, código E1–E5, logs, CSV, curvas, manifesto e gates anteriores **sem edição retrospectiva**.
- Manter F-CC+K como contribuição **teórica e diagnóstica**.
- Qualquer análise de multiplicadores não nulos do N2-box ou pricing global deve ser **pós-gate, com nova pergunta, protocolo e resultados separados**.
- O objetivo RMP (`2, 7, 3, 9`) e o `ObjBoundC` não substituem prova de LB global. A referência B0 é numérica/histórica, sem certificado físico E5 independente.

## 5. Referências internas

- `docs/technical/plans/execucao/n2-t5-registro-resultados-prospectivos.md`
- `docs/technical/plans/execucao/n2-t6-gate-decisao-cientifica.md`
- `experiments/alternative-formulations/verify_n2_t6_gate.py`
- `results/alternative-formulations/n2-t5-prospectivo/` (artefatos originais locais, **não anexados** ao presente pacote)
- `specs/proxima-fase-n2-limite-compatibilidade-certificado/spec.md` — Story 6

**Decisão encerrada:** `N2 FAIL` — validação técnica completada, objetivo científico pré-registrado não atingido.
