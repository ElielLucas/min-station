# MIN-STATION — N2-T4: protocolo da regressão prospectiva nos controles N1

**Estado:** **regressão prospectiva executada no checkout do pesquisador e exceção `Direct0` formalmente aprovada em 2026-10-10**. Gate de aceite: [`n2-t4-gate-aceite-regressao.md`](n2-t4-gate-aceite-regressao.md). Os hashes de arquivos de resultado/HEAD ainda devem ser vinculados ao gate.  
**Caminho:** B — F-CC+K, geração de colunas somente na raiz.  
**Dependência:** N2-T3 aprovada, com certificado racional revalidável e validação de K.

## 1. Objetivo e delimitação

Executar o código real da geração de colunas e os certificadores N2-T3 sobre as instâncias **já congeladas na N1**, usando o valor histórico do **LP completo F-CC+K** exclusivamente como referência de regressão. Isso verifica se a implementação é compatível com os valores históricos, inclusive quando termina sem convergência certificada. A regressão **não mede** a força dos limites nem a recuperação do ganho pré-registrado; essas comparações pertencem à **N2-T5**. Não altera o orçamento congelado de **164 Work** nem executa instâncias nível 2.

Fonte normativa: `specs/proxima-fase-n2-limite-compatibilidade-certificado/spec.md`, *Story 4*; revisão matemática v2.1, §11.2 (P-8 reservado à N2-T4). A N2-T3 deve ser tratada como implementação já aprovada, sem reabrir seus gates.

## 2. Corpus e contagem exata

| Proveniência | Casos registrados | Com LP completo medido | Tratamento |
|---|---:|---:|---|
| N1-T5 — `n1-t5-freeze.json`, `n1-t5-diagnostico.csv` | 18 | 17 | `SC-GF2-k3` sem LP F-CC+K por cap: registrar `EXCLUDED_NO_FULL_LP_REFERENCE` sem imputar zero |
| N1-T6 — 3 pares obstrução/controle, `n1-t6-freeze.json`, `n1-t6-pares.json`, `n1-t6-diagnostico.csv` | 6 | 6 | Manter cada variante como um controle independente, conferir `graph_hash` e `k_hash` |
| **Total** | **24** | **23** | Aceite exige **23 comparações elegíveis**, com 1 exclusão histórica justificada |

O manifesto compara hashes históricos, ordem, identidade do grafo de alcance e cortes K. As instâncias são reconstruídas pelos **geradores originais** (`run_n1_t5.corpus`, `run_n1_t6.read_pairs`), e não inferidas dos valores numéricos do CSV.

## 2.1. Exceção de domínio: `T5:Direct0` (identificada no replay local)

**Achado real:** `Direct0` é um grafo com **duas componentes** (`s1–t1` e
`s2–t2`). A N2-T2B e a N2-T3/E5 pressupõem **G conexo**, portanto o master
restrito inicial `(V,S,T)` e seu certificador físico **não podem** ser usados
nesse caso. O erro observado (`ValueError: G desconexo`) é uma rejeição
correta do domínio; **não** afrouxar essa pré-condição nem conectar vértices
artificialmente.

Para não perder o controle histórico, a N2-T4 aplica exclusivamente a
`T5:Direct0` uma **prova independente de ótimo LP exatamente zero**:

1. Reconstruir a instância a partir da N1-T5, conferir o SHA-256 canônico,
   e comparar o hash de K ao hash histórico. Exigir `K=∅`.
2. Revalidar grafo simples, não dirigido e unitário, as **duas componentes**
   e todo `A_r` por BFS com a autonomia original.
3. Construir e verificar um matching direto perfeito em `S×T`. Aqui:
   `s1→t1` e `s2→t2` são pares diretos.
4. No LP completo F-CC+K, definir `y=0`, `λ=0`, `d=1` nos pares do matching.
   R1/R2 são satisfeitas; R3 e R4 são satisfeitas porque K é vazio. Como
   `y≥0`, obtemos rigorosamente `0≤z_Q≤0`; portanto `z_Q=0`, compatível
   com o LP histórico 0. Os próprios caminhos diretos mostram `OPT=0`.

Essa prova **não executa geração de colunas nem E5**, não demonstra G2 e
não representa extensão do algoritmo a grafos desconexos. O CSV registra
`proof_method=EXACT_DIRECT_MATCHING_ZERO_NO_CG`,
`comparison=PASS_DIRECT_ZERO_EXACT_OUTSIDE_CONNECTED_DOMAIN`,
`iterations=0`, `direct_matching` serializado e justificativa explícita. Não usar `PASS_G2` ou
`PASS_NUMERIC_STATIONARY_WITH_CERTIFIED_LB` para essa linha.

**Consequência para o Gate da N2-T4:** se os demais 22 controles passarem,
o manifesto terá `passed=23`, `cg_evaluated=22` e
`exact_domain_exceptions=["T5:Direct0"]`, mas o status será
`SCOPE_EXCEPTION_REVIEW_BLOCK_N2_T5`. A saída do comando permanece não
zero porque a substituição de um replay CG por prova exata requer **decisão
expressa do pesquisador** antes da liberação da N2-T5. Não converter esse
estado automaticamente em `N2-T4 PASS`.

As opções para resolver o gate são aceitar **formalmente a exceção
histórica** (sem alegar 23 execuções CG) ou desenvolver/provar uma
extensão algorítmica para grafos desconexos, com nova revisão independente.
Nenhuma das duas decisões deve alterar os freezes ou a matemática v2.1.

## 3. Política matemática de comparação

Seja `z_ref` o valor numérico histórico do **LP completo F-CC+K** e `eps=1e-6`.

1. Toda execução elegível de **CG em G conexo** **deve** produzir `lp_status=CERTIFIED`, proveniente de provas N1/ENUM/N2 revalidadas pela E5, e `physical_status=CERTIFIED` após validar K; nunca aproveitar `ObjBoundC`, `z_R` ou `OPT` como LB.
2. Em **parada incompleta**, sem G2 e sem estacionariedade numérica, aceitar apenas `LB_CG <= z_ref + eps`, com justificativa não vazia. Isso **não** demonstra convergência nem força útil; a N2-T5 analisará qualidade.
3. Em **`NUMERICAL_STATIONARY`**, além da prova do LB, exigir que o RMP resolvido corresponda a todas as colunas geradas e que `|z_R - z_ref| <= eps`. Esse é um **teste numérico auxiliar**, e não substitui G2.
4. Em **`CONVERGED_CERTIFIED` (G2)**, exigir que `U` primal exato validado e `LB_CG` satisfaçam `|LB_CG-z_ref| <= eps` e `|U-z_ref| <= eps`. Nenhum status do solver sozinho é prova de G2.
5. Qualquer falso certificado, referência alterada, `K` divergente, execução sem LB certificável ou desigualdade violada produz `FAIL`, bloqueia a N2-T5 e encerra a regressão naquele controle. O caso desconexo `Direct0` é tratado separadamente na §2.1 e também bloqueia o aceite automático.

A referência histórica é um LP obtido numericamente; a tolerância absoluta é **comparação de regressão**, não uma demonstração independente da exatidão racional do LP histórico.

## 4. Execução local

A partir da raiz do repositório, na branch `novos_testes`, com o ambiente Python/Gurobi ativo:

```bash
PYTHONHASHSEED=0 python -m unittest discover \
  -s experiments/alternative-formulations \
  -p 'test_n2_t4_regression.py' -v

python -m ruff check \
  experiments/alternative-formulations/run_n2_t4.py \
  experiments/alternative-formulations/test_n2_t4_regression.py

PYTHONHASHSEED=0 python experiments/alternative-formulations/run_n2_t4.py check

PYTHONHASHSEED=0 python experiments/alternative-formulations/run_n2_t4.py run \
  --output-dir results/alternative-formulations/n2-t4-replay-corrigido
```

O modo `check` exige integridade dos freezes N1-T5, N1-T6, N2-T1 e decisão N1-T7 e **não otimiza nem escreve resultados**. `run` executa a regressão prospectiva, com, por padrão, `TimeLimit` global de 600 segundos por controle, `max_iterations=300`, `Threads=1`, `Seed=42`, uso de N1/N2 e ENUM para `n<=10` com cap 2048. Esses limites são do teste de regressão, **não** alteram o pré-registro experimental da N2-T1. Podem ser informados explicitamente `--time-limit`, `--work-limit`, `--max-iterations`, `--enum-cap`, com registro no manifesto. Evitar mudanças posteriores escolhidas em função de resultados sem registrar essa decisão e sua razão.

Saídas criadas **somente por `run`**, com modo create-only:

- `results/alternative-formulations/n2-t4-regressao.csv` — uma linha por controle processado (incluindo a exclusão histórica), resultado, justificativa, LB exato e diagnósticos.
- `results/alternative-formulations/n2-t4-regressao-manifest.json` — versão dos parâmetros, hashes, digest do CSV, quantidade verificada e `PASS`, `FAIL_BLOCK_N2_T5` ou `SCOPE_EXCEPTION_REVIEW_BLOCK_N2_T5` (exceção Direct0 ainda não aprovada).

**IMPORTANTE:** a primeira tentativa já gerou `n2-t4-regressao.csv` e `n2-t4-regressao-manifest.json` com falha em Direct0. **Não apague nem sobrescreva esses arquivos.** O comando corrigido usa uma pasta nova para preservar as duas tentativas.

O script **nunca sobrescreve** resultados anteriores. Se precisar repetir uma execução, use outro destino com `--output-dir`, registrando por que a anterior não foi aceita. A presença de falha produz exit code diferente de zero, e o histórico parcial permanece auditável. Não usar saídas de testes simulados como evidência da regressão real.

## 5. Evidências e aceite

A N2-T4 somente pode ser encerrada depois de verificar **no ambiente do pesquisador com Gurobi**:

- Os testes próprios e regressões anteriores aprovados, com Ruff limpo.
- `run_n2_t4.py check` aprovado sem alterar arquivos N1/N2-T1.
- `run_n2_t4.py run` com todos os 23 controles elegíveis avaliados, `passed=23` e exclusão de `SC-GF2-k3`. **Com Direct0 fora do domínio**, o status esperado é `SCOPE_EXCEPTION_REVIEW_BLOCK_N2_T5` e a saída é não zero até haver decisão expressa; não confundir com falha matemática dos 22 controles conexos.
- Registro da diferença entre casos G2, estacionários numericamente, interrompidos com LB certificado e a prova exata de Direct0 sem CG.
- Auditoria dos arquivos finais, versão/commit de código e decisão assinada sobre a exceção Direct0. Só após isso a N2-T5 pode começar; o gate científico `N2 PASS/N2 FAIL` continua reservado à N2-T6.

**Aviso:** nesta entrega do código não foram realizadas as 23 otimizações prospectivas, pois Gurobi não está disponível no ambiente de geração. Não há CSV/manifesto prospectivo incluído no pacote.

## 6. Adendo de aceite posterior ao replay (2026-10-10)

A execução efetiva foi apresentada pelo pesquisador depois da correção `Direct0`:

- 24/24 testes do executor aprovados e Ruff `All checks passed!`;
- `check` aprovado, preservando 24 controles históricos (23 elegíveis + 1 exclusão);
- 22 controles conexos produziram `PASS_NUMERIC_STATIONARY_WITH_CERTIFIED_LB`;
- `T5:Direct0` recebeu `PASS_DIRECT_ZERO_EXACT_OUTSIDE_CONNECTED_DOMAIN`;
- `T5:SC-GF2-k3` permaneceu `EXCLUDED_NO_FULL_LP_REFERENCE`;
- replay novo registrado em `results/alternative-formulations/n2-t4-replay-corrigido/`.

**Decisão expressa:** o responsável pela pesquisa **aprovou** a exceção de domínio `Direct0` e sua prova exata independente, sem classificá-la como CG/G2. O status `SCOPE_EXCEPTION_REVIEW_BLOCK_N2_T5` do manifesto é preservado; o Gate N2-T4 documenta a resolução humana e **autoriza seguir à N2-T5**. Ver [`n2-t4-gate-aceite-regressao.md`](n2-t4-gate-aceite-regressao.md) para decisão, limites, rastreabilidade pendente e condições do pré-registro.

**Importante:** as menções anteriores a bloqueio por exceção refletem corretamente a política *antes da decisão humana* e continuam úteis para auditar o comportamento original do executor; não representam o estado final do gate após este adendo. O CSV e o manifesto locais ainda não foram inspecionados aqui byte a byte.
