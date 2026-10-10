# MIN-STATION — Gate N2-T4: aceite da regressão prospectiva nos controles N1

**Decisão:** `APROVADO_COM_EXCECAO_DE_DOMINIO_DIRECT0` — **liberada a preparação e execução da N2-T5** sob o pré-registro congelado.  
**Data da decisão:** 2026-10-10 (`America/Sao_Paulo`).  
**Autoridade da decisão:** manifestação explícita do responsável pela pesquisa nesta conversa: **“aprovo”**, em resposta à proposta de aceitar formalmente a exceção `T5:Direct0`. Não é uma assinatura digital.  
**Ramo de referência:** `novos_testes` (não foi verificado o HEAD do checkout local).  
**Escopo:** aceite da **N2-T4**, não `N2 PASS`, não demonstração de ganho experimental nem aceite da N2-T5.

## 1. Objeto da decisão

A N2-T4 confronta a implementação real da geração de colunas F-CC+K e os certificados da N2-T3 com controles N1 historicamente congelados. O corpus possui **24 casos registrados**, sendo **23 elegíveis** para comparação com o LP completo e **1 excluído** por ausência de referência, `T5:SC-GF2-k3`. Dos 23 elegíveis:

- **22 casos** pertencem ao domínio conexo da N2-T3 e foram executados com geração de colunas, retornando `PASS_NUMERIC_STATIONARY_WITH_CERTIFIED_LB`;
- **1 caso**, `T5:Direct0`, é desconexo e foi verificado por prova exata independente, retornando `PASS_DIRECT_ZERO_EXACT_OUTSIDE_CONNECTED_DOMAIN`;
- **nenhum caso elegível** retornou `FAIL` no replay apresentado pelo pesquisador.

A distribuição acima é retirada do **log de terminal apresentado pelo pesquisador**, não de uma inspeção independente dos bytes do CSV/JSON locais. O arquivo de resultados deve ser preservado e vinculado a este gate, conforme §5.

## 2. Exceção histórica explicitamente aprovada

**Controle:** `T5:Direct0`.  
**Razão:** `G` tem duas componentes, fora da hipótese **G conexo** das implementações N2-T2B/N2-T3. O erro anterior `ValueError: G desconexo` era uma rejeição legítima da entrada pelo domínio matemático, não defeito do solver.  
**Método aceito:** `EXACT_DIRECT_MATCHING_ZERO_NO_CG`, validado pelo executor com identidade histórica de instância/K, alcance por BFS e matching direto perfeito.

Para o `Direct0`, os pares diretos entre S e T realizam um matching perfeito. Com `K=∅`, o ponto `y=0`, `λ=0`, `d=1` nos pares do matching satisfaz R1–R4 do LP completo F-CC+K. A não negatividade de y implica `z_LP >= 0`; a construção implica `z_LP <= 0`; logo **`z_LP=0` exatamente**, coincidente com o valor histórico. A mesma solução sem estações fornece a viabilidade física de custo zero.

**Aprovação do responsável:** aceita-se esta prova como **substituição justificada do replay apenas para esse controle congelado**. A decisão **não** amplia o domínio da formulação N2-T3, **não** autoriza inserir arestas artificiais, **não** equivale a execução de CG para `Direct0`, **não** é G2 e **não** modifica a base N1.

## 3. Matriz de aceite

| Critério | Evidência disponível | Decisão |
|---|---|---|
| Regressão de testes | `24 tests ... OK` em Gurobi local | PASS |
| Ruff de `run_n2_t4.py` e `test_n2_t4_regression.py` | `All checks passed!` | PASS |
| `run_n2_t4.py check` | `N2-T4 CHECK PASS` e 24 controles, 23 elegíveis, 1 excluído | PASS |
| Regressão com geração de colunas | 22 linhas `PASS_NUMERIC_STATIONARY_WITH_CERTIFIED_LB` | PASS (numérico + LB certificado) |
| Exceção histórica `Direct0` | `PASS_DIRECT_ZERO_EXACT_OUTSIDE_CONNECTED_DOMAIN` | **APROVADA EXPRESSAMENTE** |
| `SC-GF2-k3` | `EXCLUDED_NO_FULL_LP_REFERENCE` | EXCLUSÃO MANTIDA |
| Arquivos de replay | CSV/manifesto produzidos em pasta nova; caminhos informados | GERADOS, **BYTES AINDA NÃO AUDITADOS NESTA CONVERSA** |
| Congelamentos | `check` passou no checkout local | PRESERVADOS SEGUNDO LOG |

Não foi apresentado `CONVERGED_CERTIFIED` (G2) para os 22 casos; a comparação estacionária com o LP histórico e um limite inferior certificado **não implica G2**. A N2-T4 é uma *regressão de consistência*, não uma medição de recuperação do ganho. Portanto, não declarar que 22 casos tiveram o ótimo do LP formalmente provado por G2.

## 4. Como interpretar o status automático de bloqueio

O executor `run_n2_t4.py` foi escrito para **não decidir por conta própria** sobre exceções de domínio. Por isso, mesmo com as 23 verificações aprovadas, ele gera `status=SCOPE_EXCEPTION_REVIEW_BLOCK_N2_T5` e pode terminar com **código de saída 2**. Esse comportamento é correto e **não deve ser alterado retroativamente**.

**Este gate registra a decisão humana requerida pelo próprio status**. A conjunção de:

1. resultado apresentado com 22 controles CG aprovados;
2. prova exata especial aprovada somente para `T5:Direct0`;
3. exclusão previamente justificada de `T5:SC-GF2-k3`; e
4. decisão explícita do responsável pela pesquisa;

permite classificar a **N2-T4 como `ACEITA_COM_EXCECAO_FORMAL`** e **liberar a N2-T5**. O gate documentado **não transforma** o status histórico do manifesto em `PASS`, nem exige reexecutar as otimizações apenas para mudar um código de saída. Qualquer pipeline que deseje interpretar o aceite precisa considerar este documento além do manifesto original.

## 5. Rastreabilidade e evidências a vincular

**Diretório informado pelo pesquisador:**

```text
results/alternative-formulations/n2-t4-replay-corrigido/
  n2-t4-regressao.csv
  n2-t4-regressao-manifest.json
```

**Estado de inspeção:** os dois arquivos reais **não foram anexados à conversa**. Os resultados citados nos §§1–3 foram lidos do log compartilhado; não foram recalculados do CSV nem foi confrontado `csv_sha256` com os bytes do CSV. A vinculação desses hashes é uma **pendência documental de rastreabilidade**, não uma nova autorização necessária sobre `Direct0`.

No checkout local, executar e guardar a saída:

```bash
sha256sum \
  results/alternative-formulations/n2-t4-replay-corrigido/n2-t4-regressao.csv \
  results/alternative-formulations/n2-t4-replay-corrigido/n2-t4-regressao-manifest.json

git branch --show-current
git rev-parse HEAD
git status --short
```

Conferir que o manifesto contém `expected_eligible=23`, `eligible_checked=23`, `passed=23`, `cg_evaluated=22`, `exact_domain_exceptions=["T5:Direct0"]`, `excluded=["T5:SC-GF2-k3"]`, `failures=[]`, `status=SCOPE_EXCEPTION_REVIEW_BLOCK_N2_T5` e `csv_sha256` idêntico ao `sha256sum` do CSV. Esses campos são **valores esperados pelo código e pelo log**, não confirmação de inspeção já realizada. Preservar a primeira tentativa com erro e o replay corrigido; não reescrever evidências.

Hashes da implementação entregue nesta conversa (conferir no checkout que efetivamente executou os testes):

| Artefato | SHA-256 do pacote corrigido |
|---|---|
| `experiments/alternative-formulations/run_n2_t4.py` | `a083c04548a08b0d142bde82febffb6fb66cddca190baff7d95e0371eb861b77` |
| `experiments/alternative-formulations/test_n2_t4_regression.py` | `648de4340c44929859d6ecb1e94e51eb1b968e2792807f1cce25155588dd5ad5` |

**Commit HEAD e SHA-256 dos resultados:** pendentes de registro, por não terem sido disponibilizados. Não inventar esses identificadores; eventual rechecagem divergente deve interromper a reutilização do aceite até esclarecimento.

## 6. Invariantes preservados para N2-T5

- **Pré-registro N2-T1:** duas famílias × dois níveis; orçamento total de **164 Work**; limiar de recuperação **≥50%** do incremento positivo do LP sobre B0 para instâncias elegíveis. O Gate N2-T4 não consome nem altera a medição principal da N2-T5.
- **Caminho B:** F-CC+K root-only; sem branch-and-price, formulações alternativas ou escolha posterior de novas instâncias orientada por resultados.
- **Certificação:** não confundir `z_R`, `ObjBoundC`, limite certificado LP, limite físico validado e B0. A ausência de B0 certificado não equivale a ganho zero; a ausência de G2 não equivale a fracasso da regressão.
- **Rigor da medição:** tempos e Work contabilizados segundo o protocolo experimental; toda exclusão, abstenção e resultado incompleto deve ser explicitamente divulgado.
- **Não antecipar decisão científica:** `N2 PASS` ou `N2 FAIL` somente no **Gate N2-T6**, após as medições N2-T5.

## 7. Decisão final

| Campo | Registro |
|---|---|
| Gate | **N2-T4** |
| Estado final de governança | **`ACEITA_COM_EXCECAO_FORMAL`** |
| Decisão sobre `Direct0` | **APROVADA** por manifestação explícita do responsável pela pesquisa |
| Efeito operacional | **LIBERAR N2-T5** respeitando o pré-registro |
| Resultado original do executor | `SCOPE_EXCEPTION_REVIEW_BLOCK_N2_T5` (mantido e interpretado pelo presente gate) |
| Ressalva documental | Vincular SHA-256/manifesto local e HEAD efetivo; conteúdo dos arquivos ainda não inspecionado aqui |
| Alteração dos freezes / matemática N2-T3 | **Nenhuma** |
| Próximo gate científico | **N2-T6** (`N2 PASS/FAIL`), ainda não realizado |

**Conclusão:** a N2-T4 está **aceita por decisão expressa sobre a única exceção histórica**, com 22 replays CG bem-sucedidos segundo o log local e um controle desconexo comprovado independentemente. O início da N2-T5 está autorizado, mantendo registrada a pendência de associação documental dos arquivos de resultado e do commit.
