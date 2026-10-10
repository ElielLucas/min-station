# MIN-STATION — N2-T5: registro final dos resultados prospectivos

**Estado experimental:** `MEDIDA — 4/4 INSTÂNCIAS`  
**Resultado científico a encaminhar à N2-T6:** **não atingiu os requisitos de ganho**  
**Data da análise:** 2026-10-10  
**Branch exigida:** `novos_testes` (HEAD efetivo da execução não informado)  
**Papel deste documento:** registrar as medições **sem modificar** a execução, os artefatos, o pré-registro ou os critérios de aceitação.

## 1. Origem e limites da evidência

Os valores abaixo foram transcritos dos conteúdos de `n2-t5-medicoes.csv`, `n2-t5-manifest.json`, `n2-t5-lb-versus-work.csv` e `n2-t5-custos.md` **colados pelo pesquisador nesta conversa**. O log local também informa:

- `30/30` testes N2-T5 aprovados com Gurobi disponível;
- `python -m ruff check` aprovado após remover atribuição não utilizada;
- `run_n2_t5.py check`: PASS, com quatro instâncias congeladas;
- `run_n2_t5.py run`: quatro retornos `CERTIFIED_PHYSICAL_LB`.

**Limitação de auditoria:** os bytes dos quatro arquivos e do SVG **não foram enviados como arquivos anexados**. Por isso, os hashes informados no manifesto estão documentados, mas **ainda não foram confrontados nesta conversa contra os arquivos originais**. O verificador N2-T6 incluído no pacote realiza essa conferência no checkout local sem solves.

O arquivo congelado `experiments/alternative-formulations/n2-t1-freeze.json` foi inspecionado em uma cópia do repositório previamente fornecida; seu SHA-256 foi confirmado como:

`b036e9d0fe8f446dfcaca2716df85054c73dbb8702484aacce3c807e6574de71`.

## 2. Protocolo e referências preservados

- Caminho B: `F-CC+K`, **somente na raiz**; sem branch-and-price.
- Instâncias: duas famílias (HB e BP-não), dois níveis, previamente selecionadas.
- `Seed=42`, `Threads=4`, `PYTHONHASHSEED=0`.
- Teto por instância: **164 unidades de Work** em conjunto; guarda temporal de **1800 segundos**.
- `B0 = max(LP COMP, core IP)` na mesma instância. Nível 1 usa referência congelada N1; nível 2 usa solves numéricos realizados dentro do orçamento.
- Critério de sucesso: limites inferiores **certificados** acima de B0 nas duas famílias e nos dois níveis, recuperação de pelo menos **50% do incremento positivo conhecido** do LP completo sobre B0 no nível 1 e custo viável.
- `ObjBoundC` e objetivo RMP são diagnósticos, **não** substituem o LB certificado.

## 3. Resultados medidos

| Ordem | Instância | Família | Nível | B0 de referência | LB físico certificado | Ganho `LB − B0` | Work total | Wall total (s) |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1 | `HB-q4-ndir2-p1` | HB | 1 | `1` | `1/2` | `−1/2` | 0,417963 | 4,401834 |
| 2 | `BP-nao-[3,1]-q2` | BP | 1 | `6` | `1` | `−5` | 0,083058 | 1,248764 |
| 3 | `HB-q6-ndir2-p1` | HB | 2 | `11500000000000001/10000000000000000` (≈1,15) | `2/3` | `−14500000000000003/30000000000000000` (≈−0,483333) | 1,364441 | 5,787275 |
| 4 | `BP-nao-[2,2,2]-q2` | BP | 2 | `8` | `18/13` | `−86/13` (≈−6,615385) | 0,670544 | 7,001145 |

**Origem dos limites:** `lp_source=N1` nas quatro linhas; certificação física após verificação K/E5. Cada uma tem `physical_status=CERTIFIED`, `status=CERTIFIED_PHYSICAL_LB` e `g2_status=NOT_CONVERGED_CERTIFIED`.

O atributo `b0_certificate_status=UNCERTIFIED` aparece nas quatro instâncias: B0 **não possui prova física independente E5**, embora seja referência numérica/histórica do protocolo. Isso exige não promover B0 a LB rigoroso, mas **não autoriza descartar a comparação pré-registrada nem substituir a referência por zero**.

### 3.1. Recuperação do incremento LP no nível 1

Para instâncias com LP completo histórico, a recuperação assinada é:

`recuperação = (LB_físico_certificado − B0) / (LP_completo_histórico − B0)`.

| Instância | B0 | LP completo histórico | Incremento conhecido | Recuperação obtida | Limiar congelado |
|---|---:|---:|---:|---:|---:|
| HB nível 1 | 1 | 2 | 1 | `−1/2` (−50%) | `≥1/2` (+50%) |
| BP nível 1 | 6 | 7 | 1 | `−5` (−500%) | `≥1/2` (+50%) |

Ambas **não atingiram** o limiar. Os níveis 2 não têm LP completo histórico; a recuperação ali permanece **não mensurada**, sem imputação.

### 3.2. Evolução LB × Work (82 pontos)

| Instância | Pontos | LB inicial | LB final | Primeira estabilização observável do melhor LB | Última parada |
|---|---:|---:|---:|---|---|
| HB nível 1 | 18 | `1/2` | `1/2` | desde a primeira observação | `NUMERICAL_STATIONARY` |
| BP nível 1 | 11 | `1` | `1` | desde a primeira observação | `NUMERICAL_STATIONARY` |
| HB nível 2 | 28 | `1/2` | `2/3` | a partir da iteração 6 | `NUMERICAL_STATIONARY` |
| BP nível 2 | 25 | `1` | `18/13` | a partir da iteração 17 | `NUMERICAL_STATIONARY` |

As **82 observações** publicadas estão marcadas como `CERTIFIED`, com `lb_source=N1`. Não foi atribuído progresso certificado à ENUM ou ao N2-box neste experimento. Isso **não prova** que esses dois métodos seriam incapazes de produzir bound melhor; significa apenas que **não produziram o melhor LB publicado nesta execução**.

### 3.3. Master numérico versus certificação

| Instância | Objetivo RMP final (diagnóstico) | LB físico certificado |
|---|---:|---:|
| HB nível 1 | 2 | 1/2 |
| BP nível 1 | 7 | 1 |
| HB nível 2 | 3 | 2/3 |
| BP nível 2 | 9 | 18/13 |

Os valores RMP terminaram com `NUMERICAL_STATIONARY` e **não constituem prova G2**. A desigualdade entre RMP e LB certificado descreve a fraqueza da **cota global comprovada** nesta execução, não um erro da formulação matemática.

## 4. Custos e integridade de contabilidade

- Work máximo observado: **1,364442** (HB nível 2), inferior a 164 por instância.
- Wall máximo observado: **7,001145 s** (BP nível 2), inferior a 1800 s.
- `work_unmeasured_calls=0` nas quatro linhas, segundo o CSV apresentado.
- Work da linha = COMP LP + core IP + master + pricing; montagem, alcance, K, auditoria e outros custos de tempo são contabilizados separadamente em Wall. Subtempos dentro da fase CG não devem ser somados de novo à soma de fases de Wall.
- O baixo Work consumido indica que a execução **não foi interrompida por esgotamento do orçamento**, mas **não demonstra** que incrementar Work melhoraria o certificado: a parada registrada foi `NUMERICAL_STATIONARY` em todas as instâncias.

## 5. Proveniência dos arquivos experimentais

Diretório original informado pelo pesquisador:

`results/alternative-formulations/n2-t5-prospectivo/`

| Arquivo original | SHA-256 publicado no manifesto N2-T5 |
|---|---|
| `n2-t5-medicoes.csv` | `2e1215e135561d4af962318f15eeaa96be0d04aed09a8e801765ae577958bac5` |
| `n2-t5-lb-versus-work.csv` | `c0be65a1fe79f7da59be50bc3b184e0143f6c97a7f0153e66464c26a43563d5` |
| `n2-t5-custos.md` | `0b6700ed47b257e1fb5aa368d5bd1b5ec17bbf832d691b89625c912601258d0a` |
| `n2-t5-lb-versus-work.svg` | `520f82c4e0e64dec45c3d4d11ce5c61abfe150aaaedc76c5bd9cecd0f55f9920` |

O próprio `n2-t5-manifest.json` precisa ser preservado com seus bytes originais. Seu SHA-256 **não foi informado**; obtê-lo localmente para rastreabilidade do commit final. Não reconstruir o CSV a partir da transcrição para simular o digest original.

O manifesto identifica o replay N2-T4 autorizado pela exceção `Direct0`:

- CSV N2-T4: `62032d439ce86b62673b50e1cb3936e56fcea8cfef59c5a2376baf4b077c4153`;
- manifesto N2-T4: `ee91420e67a74934e01c1225025e93fb6b0490c6c054e0457e3088e88520e000`;
- gate N2-T4: `24bd101da8c2c94bdf371a6119677f0200301b38227fe12855c888f0090626cc`.

## 6. Conclusão e transferência à N2-T6

1. **N2-T5, execução técnica:** quatro instâncias medidas, orçamento respeitado e quatro LBs físicos publicados como certificados.
2. **N2-T5, objetivo experimental:** **não demonstrou ganho** sobre B0 em nenhuma família/nível; **não demonstrou 50%** de recuperação nos controles de nível 1.
3. **Sem G2:** a conclusão numérica não se converteu em um certificado de convergência LP.
4. **Gate científico previsto pela N2-T1:** encaminhar **`N2 FAIL`** à N2-T6 com razões explícitas; não alterar o pré-registro nem executar nova campanha adaptativa para modificar esse resultado.
5. **Auditoria local realizada e reportada:** 13/13 testes e Ruff PASS; o verificador confirmou os quatro hashes e emitiu `N2 FAIL`. **Rastreabilidade remanescente:** registrar SHA-256 do manifesto e commit HEAD. A auditoria tabular não substitui a reauditoria das provas matemáticas E5.

O resultado negativo é **sobre esta implementação, protocolo, certificadores e instâncias**. Não prova inviabilidade universal de F-CC+K, nem invalida os resultados matemáticos anteriores.


## 7. Atualização de fechamento N2-T6 (2026-10-10)

O responsável executou `verify_n2_t6_gate.py` no ambiente original e apresentou:

- `audit_status=VERIFIED_ARTIFACT_BYTES_AND_TABULAR_INVARIANTS`;
- `decision=N2 FAIL`;
- seis razões de bloqueio (ganho não positivo nas quatro instâncias; recuperação inferior a `1/2` nos dois casos de nível 1);
- 13/13 testes do auditor e Ruff PASS.

O **Gate N2-T6 foi encerrado com `N2 FAIL`**; F-CC+K permanece contribuição teórica/diagnóstica. Nenhuma instância ou medição é alterada por este adendo.
