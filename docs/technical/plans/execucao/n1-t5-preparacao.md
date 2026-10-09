# N1-T5 — Preparação e protocolo de execução

**Data:** 2026-10-08. **Status:** `IMPLEMENTED — NOT MEASURED`.
**Autoridade:** `specs/proxima-fase-n1-informacao-compatibilidade/spec.md` (Story 5).

## O que esta entrega implementa

- Runner `run_n1_t5.py` de três fases, com bloqueio estrito de alteração de parâmetros/dados após congelamento.
- Pré-registro gerado localmente **antes** de qualquer LP novo, com as 16 linhas F3 + os dois controles analíticos SOURCE, hashes SHA-256 de cada instância, K e fontes de OPT, tamanhos e limites fixos; manifesto humano fixado abaixo.
- Reprodução obrigatória de F3 com CSV separado e comparação de todas as linhas/colunas (`1e-6` numéricos), sem sobrescrever `f3-fcc.csv`.
- Medições nos oito braços, anotando `NOT MEASURED` e motivo se algum cap impedir.
- Testemunhas computacionais de complementaridade: corte K violado em ótimo F-CC, ou um vetor y* ótimo do COMP não extensível à F-CC+K, ou um vetor y* ótimo da F-CC+K não extensível à F-C3+K, conforme ocorram no conjunto congelado.
- Relatório gerado após **18/18** linhas, com matriz de ablação, deltas negativos preservados e gatilho informativo da N1-T6. **Não executa decisão N1-T7.**

## Pré-registro — elementos fixados ANTES de medir

**Instâncias em ordem fixa:** Direct0, TermRelay, TermRelayForced, StayPut, StayPutIsolado, SharedTerminal, CaminhoABC, Tri, F1(m=2,k=2), F2(k=1,L=3), Sec59(L=7), HB-q4-ndir2-p1, HB-q5-ndir2-p1, BP-nao-[3,1]-q2, TR-k2-L5-r2, SC-GF2-k3, SOURCE-g2, SOURCE-C5.

**Braços:** LP base; LP COMP; core IP; LP F-CC; LP F-CC+K; LP F-C3; LP F-C3+K; OPT certificado.

**K:** saída completa e deduplicada de `prepare_cuts(S,T,V,adj,A_r,r, {'C1','C2','C4'})`, ordenada por `cortes_ordenados`; cada hash SHA-256 é obtido por `fcc_k.prepare_k`, não por gerador alternativo; mesmo K injetado sem recomputação em F-CC+K e F-C3+K. Não inclui C5/C6.

**Caps:** n≤21; |W| brutos≤200000; enumeração de OPT se n≤16; para F-C3 `2*comb(m,3)*(35*|W_util|+8)≤5000000`. Tolerância LP 1e-6, Gurobi Seed=42, Threads=1, `PYTHONHASHSEED=0`.

**Fontes OPT:** `opt_por_enumeracao` (n≤16); `otimo_base` Gurobi MIP com status `OPTIMAL` (n>16). O F3 reproduz esses certificados nos 16 controles históricos. SOURCE é certificado independentemente durante T5 e confrontado com suas previsões, sem usar F-C3 para provar OPT.

**Métricas congeladas:** B0 = max(LP COMP, core IP); Γ=OPT-core IP; Δ_FCC=LP FCC−B0; Δ_FCC+K=LP FCC+K−B0; Δ_trio=LP FC3+K−LP FCC+K; Δ_trio_raw=LP FC3−LP FCC; ρ=(LP braço−B0)/(OPT−B0) apenas quando OPT>B0+1e-6; ρ histórica GF1=(LP FCC−B0)/Γ somente para Γ>1e-6. Sem truncar valores negativos.

**Gates:** aplicar os critérios e o desempate da seção `Gate / Promotion Criteria` da spec vigente; N1-T5 não decide a promoção. N1-T6 só pode abrir com menos de duas estruturas distintas com Γ>0 e LP F-CC+K<OPT−1e-6.

**Finalização do congelamento:** o comando `freeze` acrescenta dados verificáveis dependentes de cada instância (hash K, tamanho, fonte OPT), gera `experiments/alternative-formulations/n1-t5-freeze.json` e recusa sobrescrevê-lo. Este arquivo deve ser versionado **antes** de iniciar `measure`.

## Executar no ambiente de pesquisa com Gurobi

Na raiz do projeto, após aplicar o patch, na branch correta:

```bash
PYTHONHASHSEED=0 python -m unittest discover \
  -s experiments/alternative-formulations -p test_n1_t5_offline.py -v

# 1. PRE-REGISTRO. Pode consumir tempo para enumerar W em instâncias grandes.
PYTHONHASHSEED=0 python experiments/alternative-formulations/run_n1_t5.py freeze

# Verificar o JSON; registrar um commit separado se desejar selar a ordem temporal:
git status --short
# 2. REPRODUÇÃO HISTÓRICA (interrompe se qualquer dado divergir):
PYTHONHASHSEED=0 python experiments/alternative-formulations/run_n1_t5.py reproduce-f3

# 3. NOVAS MEDIDAS; NÃO executá-las se a etapa 2 falhar:
PYTHONHASHSEED=0 python experiments/alternative-formulations/run_n1_t5.py measure
```

### Saídas

| Caminho | Função |
|---|---|
| `experiments/alternative-formulations/n1-t5-freeze.json` | pré-registro congelado com hashes/OPT/caps; pode ser commitado antes do restante |
| `results/alternative-formulations/n1-t5-f3-reproduzido.csv` | resultados atuais de F3, preserva histórico |
| `results/alternative-formulations/n1-t5-reproducao.json` | atestado de comparação numérica (todas as linhas) |
| `results/alternative-formulations/n1-t5-diagnostico.csv` | diagnóstico incremental; **parcial** até registrar 18/18 linhas |
| `results/alternative-formulations/n1-t5-testemunhas.json` | pontos y*, cortes violados e inviabilidade sob y fixo |
| `docs/technical/plans/execucao/n1-t5-diagnostico.md` | relatório final, somente depois de 18/18 |

**Importante:** `freeze` e `reproduce-f3` são *create-only*, e `measure` cria checkpoints por linha. Se `measure` falhar, NÃO interpretar o CSV parcial como conclusão/gate. Não alterar caps, nem substituir instâncias ou seeds com base nos resultados já obtidos. O protocolo conservador desta primeira versão não reutiliza automaticamente um CSV parcial; preserve-o para diagnóstico e avaliação antes de qualquer retomada controlada.

## Limites da validação desta entrega

O código foi analisado e pode ser testado sem Gurobi em ambiente local. Ainda **não existem valores experimentais T5** produzidos nesta entrega. A execução completa requer Gurobi instalado e licenciado na máquina do pesquisador. A etapa SOURCE-g2 e outros casos com muitos W podem ser computacionalmente caros; não atribuir automaticamente timeout, valor zero ou ganho nulo.

O campo `tipo` do F3 é a unidade de estrutura para avaliar o gatilho (variantes de uma família contam uma vez). O relatório aponta o gatilho, mas a construção de pares é tarefa N1-T6 e a seleção de representação para N2 é N1-T7.
