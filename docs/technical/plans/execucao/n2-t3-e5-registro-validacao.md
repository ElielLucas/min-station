# MIN-STATION — N2-T3 / E5: implementação e evidências técnicas

**Estado:** `IMPLEMENTADA E HOMOLOGADA — GATE N2-T3 ACEITO PARA N2-T4` (ver registro formal de 2026-10-10)  
**Escopo:** T9–T11; H-K, testemunho racional U, G2, B0 independente e consolidação N2-T3.  
**Branch exigida:** `novos_testes`.  
**Referência normativa:** `docs/technical/reference/formulacoes/n2-t2b-master-dual-pricing-revisao.md` (v2.1, SHA-256 `db1fb71b6e4afba421ccc9f8d4f244aee6700edb886dc1c0219ed7e812aa9237`).  
**Pré-requisito:** Gate O N2-T2B aprovado. O parecer independente e os congelamentos N1/N2-T1 não foram editados.

## 1. Arquivos

- `experiments/alternative-formulations/n2_t3_cert_validation.py` — módulo E5 novo.
- `experiments/alternative-formulations/test_n2_t3_cert_validation.py` — testes E5 novos.
- `experiments/alternative-formulations/n2_t3_cert_integration.py` — extensão retrocompatível de `IterationCertification` com o campo `dual` racional, para reauditoria sem modelo Gurobi.
- `specs/n2-t3-certificacao-limites-inferiores/tasks.md` — implementação registrada, sem aprovação de Gate por inferência.

## 2. Contratos implementados

| Requisito | Implementação | Garantia/limitação |
|---|---|---|
| CERT-11 / T9 | `validate_k_evidence` | Reconstrói e confere G unitário, A_r=G^r, H, D, K, hash e `assert_valid_cuts` na instância real. Não regenera K. |
| CERT-12 / T10 | `verify_primal_rational` | Valida **exatamente** R1/R2/R3/K/domínios de um testemunho e calcula `U=sum(y)` como racional. |
| CERT-12 / T10 | `check_g2` | Exige limite do LP revalidado (E1/E2/E3), testemunho exato do mesmo contexto e `0 <= U-LB_CG <= 1/1000000`. |
| CERT-13 / T11 | `verify_baseline` | Valida B0 candidato apenas por prova física independente em instâncias pequenas (ou LB=0). Sem prova ou acima do cap, `UNCERTIFIED`. |
| CERT-14 / T11 | `run_verified_column_generation`, `finalize_verified_result` | Emite campos separados para LB do LP, LB inteiro físico, B0, convergência e diagnóstico numérico. Reexecuta verificadores originais sobre vetor racional da iteração correta. |

**Importante sobre B0:** certificar por exaustão que um valor candidato é LB do problema físico **não** certifica que ele coincide com o baseline oficial congelado `max(z_COMP^LP,z_core^IP)`. A origem declarada COMP/core é registrada, mas não substitui prova dos componentes nem do ótimo core. Em instâncias grandes, na ausência de prova oficial verificável, B0 fica `UNCERTIFIED` e não pode alimentar comparações de ganho da N2-T5.

**Orçamento:** a E5 não chama outro solve Gurobi. Tempo de parede de validação é medido separadamente; Work do solver permanece na E4. Quando um limite global de tempo é fornecido, sua parte consumida antes da CG é descontada; certificados físicos/B0 não são publicados se a auditoria exceder o prazo. As estimativas numéricas `z_R`, `ObjBoundC` e `GRB.OPTIMAL` nunca são provas globais.

## 3. Evidência disponível nesta preparação

- `test_n2_t3_cert_*.py`: **115 testes descobertos; 112 PASS, 3 SKIP** apenas por ausência de Gurobi (2 da E4 e 1 da E5); sem falhas/erros neste ambiente.
- 24 testes E5 próprios, incluindo identidade adulterada, K inválido, certificação física, B0, U e G2.
- `python -m py_compile`: PASS para módulos novos/atualizados.
- Ruff: **pendente** (não instalado neste ambiente).
- Regressão histórica N2-T2B e freeze N2-T1: o pesquisador informou 80/80 e 7/7 na avaliação E4; devem ser reexecutados no Gate N2-T3 na versão integrada.

## 4. Validação obrigatória no ambiente do pesquisador

```bash
PYTHONHASHSEED=0 python -m unittest discover \
  -s experiments/alternative-formulations \
  -p 'test_n2_t3_cert_*.py' -v

PYTHONHASHSEED=0 python -m unittest discover \
  -s experiments/alternative-formulations \
  -p 'test_n2_t2b_*.py' -v

PYTHONHASHSEED=0 python -m unittest discover \
  -s experiments/alternative-formulations \
  -p 'test_n2_t1_offline.py' -v

PYTHONHASHSEED=0 python experiments/alternative-formulations/run_n2_t1.py check
PYTHONHASHSEED=0 python experiments/alternative-formulations/verify_n1_t7_gate.py

python -m ruff check \
  experiments/alternative-formulations/n2_t3_cert_*.py \
  experiments/alternative-formulations/test_n2_t3_cert_*.py \
  experiments/alternative-formulations/n2_t2b_column_generation.py
```

Conferir os 14 requisitos `CERT-01..CERT-14` contra `spec.md` e validar que **nenhuma alteração** ocorreu em arquivos matemáticos e experimentais congelados.

## 5. Gate N2-T3

**Recomendação técnica preliminar:** pronto para validação local, **não homologado**.  
**Decisão humana formal:** `PENDENTE`.  
**Restrições:** não executar N2-T4, N2-T5 nem N2-T6 nesta entrega; não alterar freeze, orçamento ou formulação para contornar resultados.


## 6. Atualização de homologação — 2026-10-10

A seção 3 acima registra fielmente a preparação anterior à homologação. Os resultados posteriores foram:

- **N2-T3 E1–E5:** 115/115 testes `OK`, 0 falhas, 0 erros, 0 skips; execução real com Gurobi informada pelo pesquisador.
- **N2-T2B:** 80/80 testes `OK`, incluindo master, pricing, controle matemático e geração de colunas, informado pelo pesquisador.
- **Ruff:** `All checks passed!` no comando que abrange módulos/testes N2-T3 e controlador N2-T2B.
- **N2-T1 offline:** 7/7 testes `OK`, reexecutados nesta conferência sobre checkout reconstruído.
- **Integridade:** `run_n2_t1.py check` e `verify_n1_t7_gate.py` `PASS` no pacote reconstruído; decisão N1 `PROMOTE FCC + EXISTING CUTS`; N2 caminho B e 164 Work imutáveis.
- **Referências:** SHA-256 da revisão v2.1 e do parecer conferidos, sem edição.

A recomendação técnica de implementação passa a **`APTO PARA ACEITE OPERACIONAL`**. O registro de decisão e seu escopo encontram-se em [`n2-t3-gate-aceite-certificacao.md`](n2-t3-gate-aceite-certificacao.md). O aceite **não** certifica automaticamente qualquer execução numérica, B0 oficial ou ganho experimental, nem substitui a regressão N2-T4. O commit final N2-T3 não foi informado e deverá ser relacionado ao manifesto do gate após o commit local.
