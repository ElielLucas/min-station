# AS29 — Design técnico

**Spec:** `specs/as-29-yrbc-reconciliacao-lb-opt/spec.md`
**Status:** implementado e revisado (Rev. 2, 18/10/2026). G0 pelo contrato vigente, sem emendas: `G0_CANDIDATE_PASS` (31/31 com UB física). A aprovação do gate é do pesquisador.

## Architecture Overview

**Contexto de decisão:** A linha de base reúne LP, limites MIP, ótimo de núcleo e incumbentes físicos sob orçamentos diferentes. Há divergências históricas, especialmente CC9 (OPT=31 reportado em AS06/AS09, enquanto a tabela de LB* da Spec A marca 30) e artefatos anteriores à correção de K. Sem proveniência rigorosa, comparar Y-RBC com o envelope pode induzir uma conclusão falsa.

```mermaid
flowchart TD
  A[AS29 — entradas versionadas] --> B[Implementação/estudo conforme Spec]
  B --> C[Verificações independentes]
  C --> D{Gate aprovado?}
  D -->|Sim, com revisão humana| E[Próxima etapa autorizável]
  D -->|Não ou inconclusivo| F[STOP / BLOCKED / INCONCLUSIVE]
```

## Abordagem e fronteiras

Agrupar por identidade física de instância e hash bruto, nunca pelo prefixo PUC isolado. Manter três colunas distintas: LP ótimo, melhor MIP bound e UB de instalação comprovada. Para OPT=31 de CC9, verificar fonte AS06/AS09 e status numérico antes de atualizar a régua. Reportar envelope por seed e orçamento e outro envelope histórico meramente informativo. Incluir revisão específica de E9 anterior à correção de C4-DM e nomenclatura COMP E7–E14 versus AS.

## Code Reuse Analysis

| Fonte existente | Papel / verificação necessária |
|---|---|
| `results/benchmark/linha_base.csv` | Reutilizar apenas depois de conferir versão, semântica, hashes e permissões. |
| `docs/technical/reference/experimentos/resultados-linha-de-base.md` | Reutilizar apenas depois de conferir versão, semântica, hashes e permissões. |
| `docs/technical/reference/experimentos/resultados-e8-pli.md` | Reutilizar apenas depois de conferir versão, semântica, hashes e permissões. |
| `docs/technical/reference/experimentos/as28-resultado-lp-c3.md` | Reutilizar apenas depois de conferir versão, semântica, hashes e permissões. |
| `instances/manifest.csv` | Reutilizar apenas depois de conferir versão, semântica, hashes e permissões. |

## Components and Interfaces

| Artefato previsto | Responsabilidade |
|---|---|
| `docs/technical/reference/experimentos/as29-envelope-lb-opt.md` | Documento/manifesto auditável |
| `docs/technical/reference/experimentos/as29-envelope-proveniencia.csv` | Documento/manifesto auditável |
| `docs/technical/reference/experimentos/as29-erratas-e-incompatibilidades.md` | Documento/manifesto auditável |

## Contratos de integridade e evidência

- Toda instância recebe ID físico, SHA-256 bruto, classe, partição, autonomia `r` e cardinalidades `|S|`, `|T|`.
- Todo teste numérico tem versão de Gurobi, configuração, seed, limite de trabalho, tempo, status e natureza da certificação.
- Uma incumbente `y` só conta como UB físico depois de validação independente de viabilidade; ótimo do núcleo é apenas LB, salvo validação adicional.
- Resultados censurados e falhas de certificado são explícitos e contam na cobertura.
- Mudança de política após resultado é exploratória e exige novo pré-registro; sem reclassificação retroativa.
- Nenhuma etapa possui permissão implícita para fazer push, mexer nos dados de avaliação ou desbloquear AS26.

## Risks & Concerns

| Risco concreto | Consequência | Mitigação |
|---|---|---|
| LB* é bound numérico e pode ser confundido com certificado racional | Falso ganho, incorretude ou baixa reprodutibilidade | Exigir o certificado/teste e registrar STOP/INCONCLUSIVE quando faltar prova. |
| Núcleo inteiro fornece LB mas sua incumbente pode ser fisicamente inviável | Falso ganho, incorretude ou baixa reprodutibilidade | Exigir o certificado/teste e registrar STOP/INCONCLUSIVE quando faltar prova. |
| Misturar resultados de versões e orçamentos diferentes distorce ganhos | Falso ganho, incorretude ou baixa reprodutibilidade | Exigir o certificado/teste e registrar STOP/INCONCLUSIVE quando faltar prova. |

## Tech Decisions

| Decisão | Escolha | Racional |
|---|---|---|
| Escopo temporal | AS29 somente; sem executar a etapa seguinte | Gates devem ser aprovados separadamente. |
| Organização | `specs/as-XX-*` | Padrão concreto já utilizado pelo MIN-STATION, apesar do default `.specs/features/` da skill. |
| Validação | Scripts `validate_spec.py` e `validate_tasks.py` da skill | Passam nos diretórios explicitamente apontados. |
| Gate | G0 — Fontes reconciliadas | G0 PASS: 100% dos casos de desenvolvimento usados nos futuros gates com hash, LB fonte, UB fisicamente validado e classe de status; divergências explicitamente abertas ou resolvidas; CC9 contextualizada. G0 BLOCKED se não houver rastro de proveniência suficiente. |

## Critérios de abstenção

- Se prova, comparação ou certificado estiverem incompletos: registrar hipótese/INCONCLUSIVE e não inferir GO.
- Se o teste contradisser uma hipótese matemática: registrar contraexemplo com instância mínima e bloquear dependentes.
- Se não houver Gurobi disponível: executar apenas testes independentes e dry-run, sem preencher resultados MIP fictícios.

## As-built da AS29

- `experiments/benchmark/reconcile_as29.py`: reconstrói a auditoria de fontes e os envelopes sem solver e sem ler resultados reservados do AS09.
- `experiments/benchmark/test_reconcile_as29.py`: testa classificação de fontes, arredondamento, integralidade, integridade de manifests e isolamento da avaliação.
- `as29-envelope-proveniencia.csv`: linha por braço e fonte, com SHA do arquivo, seed/limites quando constam da fonte, status e natureza do UB.
- `as29-envelope-casos.csv`: síntese por caso, sem fundir o LB* original com limites posteriores.
- `as29-envelope-lb-opt.md` e `as29-erratas-e-incompatibilidades.md`: interpretação, protocolo de comparabilidade e casos inconsistentes.
- Não foi construída uma solução física nova, executado MIP/LP ou corrigido o CSV original. (Rev. 0: G0 bloqueado.)

### Rev. 1 (revisão independente)

- **UB física = oráculo reexecutado.** `physical_oracle()` usa `ms_utils.ler_instancia` e `experiments/cuts/independent_validator.viavel` (estados vértice-bateria + emparelhamento), com `r` do manifesto. Não usa o modelo MIP, `A_r` nem K. Metadado `physical_validated_ub` é só pré-condição (`validated_ub`).
- **Admissibilidade de LB:** `U`, `U_K`, `K_IP`. `C`/`C_K` (AS09, `PROOF_REVIEW_REQUIRED`) ficam registrados com `lb_admissible=false`.
- **Três colunas distintas, como previsto acima:** LP (`lp_u`, `lp_u_k`, AS09), LB MIP (`historic_lb_integer`), UB física (`physical_ub_validated`), mais UB numérica (`ub_numeric_envelope`) rotulada `SOLVER_ONLY`.
- **Estados:** `OPT_NUMERIC_PHYSICAL`, `OPEN_PHYSICAL_UB`, `OPT_NUMERIC_SOLVER_ONLY`, `OPEN_SOLVER_UB_ONLY`, `INCONSISTENT`, `INTEGRITY_BLOCKED` (`summarize()`).
- **Identidade:** registro com `instance_sha256` diferente do manifesto recebe `exclusion=INSTANCE_SHA_MISMATCH` e fica fora do envelope. Planos AS09 conferidos por hash canônico contra o manifesto e cada registro; AS06 por sidecar e manifesto.
- **Gate:** `gate()` aplica o critério vigente (`G0_CANDIDATE_PASS`, `G0_BLOCKED_EVIDENCE` ou `G0_BLOCKED` para `INCONSISTENT`/`INCOMPLETE`/`INTEGRITY_BLOCKED`) e informa separadamente `amendment_candidate` (emenda A1, não adotada). A aprovação é sempre humana.
- **Rev. 2:** nova fonte `AS29_POSTERIOR_EXPORT` (`results/benchmark/as29-physical-ub-001/`, schema `AS29-PHYSICAL-UB-v1`, sidecar SHA-256), gerada por `export_as29_installations.py` com a configuração da Spec A. Entra como `U`/`U_K` MIP com instalação revalidada pelo oráculo; por ser evidência posterior, a nota de cada linha o diz.
- **Fontes divergentes:** limites `lb`/`ub`/`lb_melhor`/`ub_melhor` do manifesto aparecem lado a lado (`manifest_*`, `lb_documented_max`, `ub_documented_min`) e não entram no envelope (sem SHA por execução).
- **Proveniência temporal:** `source_versioned_in` = commit e data git da fonte; `cuts_scope` distingue o hash do gerador do hash de K por instância.
- **Envelope histórico vs. corrida pareada:** o CSV de casos marca `comparability` como envelope não pareado; comparações de desempenho exigem nova corrida pareada pré-registrada.
