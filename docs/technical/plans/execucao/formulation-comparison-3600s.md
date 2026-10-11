# MIN-STATION — FC-06: campanha prospectiva pareada, condicionada (até 3.600 s)

**Status:** implementação operacional preparada; **campanha longa NÃO executada**.  
**Dependências:** FC-01 a FC-05; Gate FC-05 auditado `READY_FOR_EXTENDED`; sondagem MAIN **nova** auditada FC-04.  
**Proteção:** `N2 FAIL` permanece fechado; nenhum arquivo ou resultado N1/N2 é reescrito.

## 1. Questão experimental

> Em instâncias tratáveis pela enumeração completa de F-CC+K e suficientemente informativas, como se comparam COMP+K e F-CC+K em custo computacional e qualidade da relaxação linear?

O ganho observado do LP da F-CC+K nas instâncias HB-q4 e BP-q2 **não demonstrou redução de tempo MIP**; ambas foram resolvidas em poucos segundos. Logo, essas duas instâncias, isoladamente, **não justificam 3.600 s por braço**.

A campanha não parte de uma suposição de superioridade, nem substitui COMP+K por baseline sem cortes. A baseline sem K é uma **ablação externa** à comparação inteira primária.

## 2. Pré-condições e seleção congelada

1. Um diretório piloto da FC-05 deve satisfazer o verificador independente completo, com `READY_FOR_EXTENDED` e `artifact_audit=PASS` **na data da preparação e novamente antes da execução**.
2. Fazer uma **sondagem nova** sobre o pool fixo MAIN (seis instâncias), `--tier main --modalities B --formulations comp_mip,fcc_k --time-limit 120`, mantendo o cap de enumeração. Auditar o diretório com `verify_comparison_artifacts.py`.
3. Excluir casos sem hash de instância/K coincidente, modelo completo, cortes K inteiramente aplicados e par `PAIR_VALID`. CAP e timeout no *worker* não comprovam enumeração completa.
4. Seleção padrão: pelo menos um braço MIP completo encerrou `TIME_LIMIT` na sondagem. Instâncias com **ambos os braços OPTIMAL** são excluídas por padrão. Exceção explícita: justificativa metodológica escrita (mínimo 80 caracteres) **e** ao menos um tempo `wall_total_s` >= 30 s; isso permite registrar uma hipótese, **não assegura que a campanha longa seja útil**.
5. Se a lista de elegíveis ficar vazia: `NOT_ELIGIBLE`, sem pré-registro executável e **sem campanha de uma hora**. Investigar formulações reduzidas, pricing ou certificação em experimento distinto.

Não selecionar instâncias a posteriori com base nos resultados de 3.600 s. O manifesto da preparação grava também **todas as exclusões**, para evitar viés oculto.

## 3. Protocolo congelado

| Dimensão | Definição |
|---|---|
| Braços inteiros | COMP+K × F-CC+K completo; sem RMP restrito ou N2 pricing |
| Tempo máximo MIP | **3.600 s de wall por braço**, incluindo inicialização, K, enumeração, montagem, Gurobi, validação e término |
| LP independente | `lp_base`, `lp_comp`, `lp_fcc_k`; **600 s de wall por LP**; uma vez por instância (seed 42), não confundidos com pares MIP |
| Seeds MIP | 42, 43, 44; mesmos valores em ambos os braços |
| Ordem de execução | Alternada por (índice da instância + índice da seed), conforme `plan.csv` selado |
| Threads | 4 por padrão; gravadas no manifesto |
| Cap de enumeração | `max_w=200000` por padrão; registrado e aplicado ao F-CC+K |
| Grupo de origem | `fonte:instancia_original` quando presente; fallback conservador à família estrutural, nunca declarar seeds independentes |
| Métricas primárias | wall total, status, censura, Work, tempo de solver, conclusão do par |
| Métricas secundárias | LB/UB **numéricos** MIP, LB LP numérica, primeiro incumbente, memória, nós, UB físico validado |
| Prova racional | Somente com verificador racional independente; FC-06 **não** o produz (`NOT_CERTIFIED`) |
| Denominadores | TODOS os braços/seeds do plano, incluindo ausentes, CAP, timeout, falha e não resolvidos |

O arquivo `preregistration.json` é publicado **antes do primeiro solve**, acompanhado de `preregistration.sha256`; o `plan.csv` e as verificações de máquina/código/instâncias/gates são checados antes de executar. Nenhuma execução longa é disparada automaticamente ao preparar.

## 4. Comandos do projeto

Na raiz do repositório, após incorporar a implementação:

```bash
PYTHONHASHSEED=0 python -m unittest discover \
  -s experiments/formulation-comparison -p 'test_*.py' -v
python -m ruff check experiments/formulation-comparison
```

Reverifique o piloto FC-05 existente:

```bash
python experiments/formulation-comparison/verify_comparison_pilot.py \
  results/formulation-comparison/pilot-20261011T002026Z
```

Gere nova sondagem curta **sem iniciar campanha longa**:

```bash
PYTHONHASHSEED=0 python experiments/formulation-comparison/run_comparison.py \
  --tier main --modalities B --formulations comp_mip,fcc_k \
  --time-limit 120 --lp-time-limit 60 --max-w 200000
```

Audite o diretório `main-...` efetivamente gerado:

```bash
python experiments/formulation-comparison/verify_comparison_artifacts.py \
  results/formulation-comparison/main-<DATA_REAL>
```

**Somente pré-registre**, com diretório NOVO para cada tentativa:

```bash
PYTHONHASHSEED=0 python experiments/formulation-comparison/run_extended_comparison.py \
  --prepare \
  --pilot-run results/formulation-comparison/pilot-20261011T002026Z \
  --screening-run results/formulation-comparison/main-<DATA_REAL> \
  --run-dir results/formulation-comparison/extended-<IDENTIFICADOR_UNICO>
```

Se `NOT_ELIGIBLE`, **pare aqui**; não force instâncias triviais. Examine `eligibility_report.json`. Se houver elegíveis, examine `preregistration.json`, `plan.csv`, exclusões, orçamento máximo e grupo de origem, **antes de optar** por iniciar.

Um caso resolvido na sondagem só poderá ser pré-registrado como exceção usando `--methodological-justification 'JUSTIFICATIVA_CIENTÍFICA_ESPECÍFICA_DE_PELO_MENOS_80_CARACTERES'`, desde que não seja trivial (tempo medido >= 30 s). Não usar esse parâmetro apenas para conseguir rodar um experimento caro.

A execução de longa duração é um **segundo comando explícito** (não executar sem decidir a pertinência científica):

```bash
PYTHONHASHSEED=0 python experiments/formulation-comparison/run_extended_comparison.py \
  --execute \
  --run-dir results/formulation-comparison/extended-<IDENTIFICADOR_UNICO> \
  --confirm-long-run
```

Após a execução, auditar:

```bash
python experiments/formulation-comparison/verify_extended_campaign.py \
  results/formulation-comparison/extended-<IDENTIFICADOR_UNICO>
```

A auditoria externa dos artefatos exige que o código e as instâncias continuem acessíveis no mesmo estado verificado. Alterar código depois da preparação invalida o pré-registro — preparar novamente em **outro diretório**.

## 5. Saídas e política de interpretação

| Saída | Conteúdo |
|---|---|
| `eligibility_report.json` | Todas as instâncias candidatas, selecionadas e excluídas e motivos |
| `preregistration.json` e `.sha256` | Snapshot de hashes das fontes, código, máquina, seleção, ordem e métricas |
| `plan.csv` | Denominador completo antes do primeiro solver |
| `events.jsonl` | Evento inicial e eventos por braço, incremental |
| `results.csv` | Cada braço planejado e a sua evidência, incluindo censura |
| `campaign_report.json` e `.md` | Resumo LP separado de MIP, pares, grupos de origem e limitações |
| `manifest.json` e `.sha256` | Inventário dos artefatos e da execução, incluindo pré-registro e código |

`PAIR_VALID` atesta integridade da comparação e da incumbente, **não** certificação matemática de otimalidade. `GRB.OPTIMAL` é evidência numérica do solver. Sem prova racional verificada, todo *gap certificado* é `INCONCLUSIVE`. Não concluir superioridade global a partir de seis instâncias do MAIN ou de repetições correlacionadas do mesmo grafo.

## 6. Condição de parada científica

Mesmo com o gate `READY_FOR_EXTENDED` da FC-05, a FC-06 deve **abster-se** se a sondagem não revelar casos informativos e completamente enumeráveis. O registro `NOT_ELIGIBLE` é um **resultado metodológico válido**, não uma falha a ocultar. Nesse caso, formular estudo separado de pricing/relaxação e de G2 racional, sem reabrir a decisão congelada `N2 FAIL`.
