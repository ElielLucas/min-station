# N1 — Registro de implementação e próximos gates

**Data:** 2026-10-07. **Branch-alvo:** `novos_testes`. **Sem commit criado.**
**Authority:** `specs/proxima-fase-n1-informacao-compatibilidade/spec.md` e análise consolidada de 07/10.

| Tarefa | Estado da entrega | Evidência e ressalvas |
|---|---|---|
| N1-T0 | `DONE` para migração documental e notas de §15 | 208 ocorrências de caminhos com basename único, 7 links relativos; 16 notas datadas; registro de SOURCE; `check_paths_n1.py` passa. Coletor histórico `run_r7_plato.py` preservado mesmo com uma referência textual obsoleta; exemplos geradores sem arquivo criado não são links de entrada |
| N1-T1 | `DONE` quanto à prova escrita/rotulagem | P2/P7 reescritas como `PROVEN`; P3/P4 reclassificadas `HYPOTHESIS` (sem inventar testes). Revisão independente de provas é recomendável |
| N1-T2 | `PARTIAL` | Documento canônico v1, auditoria §§2–12, pontos O1–O5 e `d_ss` definidos; registro MR-F3 feito como `OPEN`. O gate de aceitação não foi satisfeito |
| N1-T3 | `PARTIAL` | Novo módulo `fcc_k.py` com K idêntico à COMP/hash + script `verify_fcc_k_n1.py`, **não executados** sem Gurobi. F-C3 não implementada: proibida pelo gate MR-F3 aberto |
| N1-T4 | `DONE` para os pools registrados | 610 linhas, 3 novos CSV, testemunhas Hall, 0 divergências com o `oracle_viavel` registrado, cc9 frequência 21 versus cobertura 27; 4 testes unitários offline passaram |
| N1-T5 | `BLOCKED` | Não existe pre-registro adicional com hashes K/OPT nem medição nova. Antes de qualquer braço novo: MR-F3, equivalência por instalação, reprodução F3 (`1e-6`), então congelar hashes K e fontes OPT |
| N1-T6 | `BLOCKED` | Gatilho só pode ser avaliado com valores medidos N1-T5; nenhum par novo criado |
| N1-T7 | `BLOCKED` | Não há decisão de promoção sem CSV certificado. N2 continua `CONDITIONAL` |

## Restrições respeitadas

- `baseline.py`, `experiments/alternative-formulations/fcc.py`, `run_f3.py`, `run_r7_plato.py`, `results/benchmark/r7-plato.csv` e `r7-plato-resumo.csv` não modificados.
- Documento SOURCE preservado com SHA-256 `fd5e9a0054ef6d10ba9f791f2cc77df55389c8cf72bcac3ccf56376558ef49f4`.
- Pré-registros existentes preservados. Não foi criado commit, não foram geradas instâncias nem executados novos LPs.
- Os rótulos `PROVEN`, `HYPOTHESIS`, `OPEN`, `COMPUTATIONALLY VERIFIED` e `NOT MEASURED` são usados com os sentidos da spec.
- A ausência de Gurobi neste ambiente impede certificar F3, F-CC + K e F-C3. **Não** interpretar ausência de medição como ausência de efeito.

## Comandos disponíveis

A partir da raiz do projeto, em ambiente com Python e `gurobipy`/licença Gurobi quando necessário:

```bash
# Releitura R7 já executada, independente do solver
python experiments/benchmark/audit_r7_n1.py
python -m unittest discover -s experiments/benchmark -p test_audit_r7_n1.py -v
python experiments/benchmark/check_paths_n1.py
sha256sum docs/technical/reference/formulacoes/formulacao-fc3-componentes-trios.md

# Pendente, em ambiente com Gurobi
PYTHONHASHSEED=0 python experiments/alternative-formulations/verify_fcc.py
PYTHONHASHSEED=0 python experiments/alternative-formulations/run_f3.py
PYTHONHASHSEED=0 python experiments/alternative-formulations/verify_fcc_k_n1.py
```

**Antes de rodar `run_f3.py`:** preservar cópia do CSV histórico para comparação de cada valor com tolerância `1e-6`, pois esse runner escreve no arquivo de saída histórico. Não sobrescrever evidências anteriores sem registrar e comparar os hashes.

**Próxima etapa lógica:** revisão matemática independente e aceitação explícita do MR-F3; só depois implementar F-C3 segundo as redes C31–C34 e validar toda instalação para cada modelo novo. Em paralelo, executar os testes F-CC + K e reprodução F3 em Gurobi. Não iniciar T5 sem os gates anteriores.

---

## Atualização posterior — N1-T3, N1-T5 e gatilho N1-T6 (2026-10-08)

> **Nota histórica:** a tabela inicial acima reflete o estado de 07/10/2026 e **não é mais o status atual**. Esta atualização registra fatos posteriores sem reescrever o histórico ou os pré-registros congelados.

| Tarefa | Estado atualizado | Evidência / ressalva |
|---|---|---|
| N1-T2 | `ACCEPTED` (MR-F3) | `docs/technical/reference/formulacoes/revisao-mr-f3-n1.md` aceita revisão matemática; não substitui o teste computacional |
| N1-T3 | `COMPUTATIONALLY VERIFIED` no conjunto testado | `results/alternative-formulations/n1-t3-validacao.csv`, `n1-t3-lp-invariantes.csv` e `n1-t3-source-regressoes.csv`: 9 instâncias, 878 instalações sem discordância; SOURCE-C5 LP = 2,5; SOURCE-g2 `NOT MEASURED` por cap |
| N1-T4 | `DONE` na auditoria dos pools registrados | `results/benchmark/n1-r7-auditoria-resumo.csv`; mantém o limite de inferência aos pools registrados |
| N1-T5 | `COMPUTATIONALLY VERIFIED` no diagnóstico congelado | `experiments/alternative-formulations/n1-t5-freeze.json`, `results/alternative-formulations/n1-t5-diagnostico.csv`, `n1-t5-testemunhas.json` e `docs/technical/plans/execucao/n1-t5-diagnostico.md`; 18 linhas de instância, com braços `NOT MEASURED` explicitamente identificados |
| N1-T6 | `TRIGGERED / IMPLEMENTED — NOT MEASURED` | N1-T5 detectou apenas a família `sec59` com `Γ > 0` e `LP F-CC+K < OPT`; a tarefa exige congelar antes de gerar os três pares definidos em `n1_t6_pairs.py`. Ver `docs/technical/plans/execucao/n1-t6-preparacao.md` |
| N1-T7 | `PENDING` | Decisão científica final somente após concluir N1-T6 e aplicar o gate original da spec |

**Interpretação do resultado T5:** `Tri` apresentou LP F-CC+K = 1,5, LP F-C3+K = 2,0 e OPT = 2,0, com testemunha de incompatibilidade registrada. `Sec59(L=7)` apresentou `Δ_trio = 0`; nos controles SOURCE, os braços excluídos por cap permanecem `NOT MEASURED`. Esses fatos **não são** a decisão promocional N1-T7.

**Nota operacional:** nenhum commit ou experimento novo é criado por esta atualização documental. Os comandos `freeze`, `generate`, `certify`, `measure` e `report` da N1-T6 são descritos no documento de preparação. Resultados dos pares T6 só passam a existir após execução explícita no ambiente do pesquisador.

---

## Atualização posterior — encerramento de N1-T6 e gate N1-T7 (2026-10-08)

> Esta seção substitui **somente o estado operacional**, não altera as notas históricas acima nem os congelamentos T5/T6.

| Tarefa | Estado atual | Evidência e limite |
|---|---|---|
| N1-T5 | `COMPUTATIONALLY VERIFIED` (conjunto congelado) | 18 instâncias, com exclusões `NOT MEASURED` preservadas; relatório `n1-t5-diagnostico.md` |
| N1-T6 | `COMPUTATIONALLY VERIFIED` para braços medidos; 6 variantes `CERTIFIED` | `n1-t6-diagnostico.csv`, `n1-t6-certificados.json`, `n1-t6-diagnostico.md`; correção da serialização `A_r` documentada em `n1-t6-errata-serializacao-ar.md`, sem alterar o runner congelado |
| N1-T7 | `DECIDED — PROMOTE FCC + EXISTING CUTS` | `n1-t7-decisao-cientifica.md`; seleção única do caminho B de N2, sem trio. Gatilhos rederiváveis por `verify_n1_t7_gate.py` |
| N2 | `ACTIVATED FOR T1 ONLY` | `specs/proxima-fase-n2-limite-compatibilidade-certificado/spec.md`; iniciar pré-registro e derivação teórica antes de código, medição e certificação. N3/R9 permanecem bloqueados |

O ganho estrito de F-C3+K foi medido somente na família `tri` e nesses casos o core IP já alcançava OPT. A escolha de F-CC+K se apoia em ganho sobre B0 nas famílias `sec59`, `hb` e `bp-nao`, com testemunha de complementaridade dos cortes K em `Sec59(L=7)`. Não tratar os valores LP como evidência de melhoria de tempo computacional.
