# FC-03 — Semântica de limites, certificados e convergência — Design

**Spec:** `specs/fc-03-semantica-evidencia-numerica/spec.md`  
**Status:** RASCUNHO  
**Dependência:** FC-02; pode evoluir em paralelo com FC-04 após a interface estabilizada

## Architecture Overview

Estabelecer estrutura de resultado com três campos ortogonais: `solver_evidence` (numérica); `rational_evidence` (ausente ou verificável); `physical_ub_validation` (válida/inválida/ausente). Um MIP completo com `ObjBound` pode reportar `solver_numeric_lb`; um master restrito não. `GRB.OPTIMAL` não cria racional_evidence. Relatórios conservam as colunas legadas com `legacy_*` ou versão de schema, mas convertem rótulos enganosos. GAP numérico e certificado em colunas diferentes e nunca misturar os dois.

```mermaid
flowchart TD
    A[Entrada com identidade e parâmetros] --> B[Reuso de componentes existentes]
    B --> C[Implementação local desta spec]
    C --> D[Testes por AC]
    D --> E[Verifier independente]
    E --> F[Artefatos auditáveis ou abstenção]
```

## Code Reuse Analysis

| Component / location | How to leverage |
|---|---|
| `fc_core.py` | Status atuais e extração de Gurobi |
| `fc_reporting.py` | Campos objetivo, lower bound e gaps |
| `n2_t3_cert_validation.py` | Separação entre validação racional e solver numeric |

**Não duplicar** implementações matemáticas de `baseline`, `harness`, `fcc`, `fcc_k` e dos certificadores N2. Quando uma interface não fornecer o dado requerido, criar adaptação estreita e testada.

## Components and Interfaces

| Component | Purpose | Interface / responsibility |
|---|---|---|
| `fc_evidence.py` (novo) | Enums/tipos e checagem de domínios de evidência | `classify_bound(...) -> EvidenceState` |
| `fc_core.py` | Anexação de proveniência real | `LPResult`, `MIPResult` |
| `fc_reporting.py` | Campos numeric vs rational e gap | `RESULTS_FIELDS` |

## Data Models / Contracts

- `instance_sha256`: digest calculado sobre bytes reais da entrada.
- `k_sha256`: conjunto K canônico associado à instância, quando usado.
- `solver_numeric_*`: valor/status fornecidos pelo solver, sempre numericamente rotulados.
- `rational_verified_*`: valor exato `Fraction` e identificador de prova independente, ou ausente.
- `physical_ub_*`: incumbente com instalação e matching validados, ou ausente.
- `wall_total_s`: tempo monotônico de ponta a ponta por execução; `solver_runtime_s` é apenas sua subparte.
- `work_total`: soma de unidades Work do Gurobi, sem convertê-las em segundos.
- `stop_reason`: enum explícito; não traduzir cap/timeout/erro como zero ou sucesso.

Somente os campos relevantes devem ser adicionados aos módulos desta feature; não impor migração global antecipada.

## Error Handling Strategy

| Error | Handling | Published evidence |
|---|---|---|
| Falta de Gurobi ou licença | Falhar de forma explícita; não trocar solver | `SOLVER_UNAVAILABLE` com diagnóstico |
| Timeout/cap durante preparação | Abortar braço dentro do deadline global | Sem valor ótimal/global fabricado |
| Hash/K divergente | Bloquear combinação pareada | `INTEGRITY_ERROR` |
| Solução física inválida | Não publicar UB físico | `INVALID_PHYSICAL_WITNESS` |
| Prova racional ausente | Preservar apenas número do solver como diagnóstico | `NOT_CERTIFIED` |

## Risks & Concerns

| Concern (location) | Impact | Mitigation |
|---|---|---|
| `fc_core.py`: rótulo CERTIFIED do status Gurobi | Confusão com certificado E5 | Contrato tipado com prova independente opcional. |
| `fc_core.py`: ObjBound de MIP interrompido | Bound numérico interpretado como prova racional | Etiquetar evidência e completude. |

## Tech Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Compatibilidade | Preservar N1/N2 e caminhos existentes; novos módulos opt-in quando tocar legado | Não modificar evidência congelada. |
| Precisão | Racional para prova independente; float apenas para valores numéricos do solver e custo de execução | Evitar falsa certificação. |
| Experimentos | Novas pastas de saída, auditáveis por checksum | Reprodução e não sobreposição de evidências. |

## Alternatives considered

- **Reescrever tudo:** rejeitado por duplicar código matemático validado e aumentar risco de divergência.
- **Alterar in-place resultados históricos:** rejeitado por perder proveniência.
- **Adaptar o runner existente com interfaces estreitas:** **escolhido**, por reaproveitar validação e permitir regressão.

## Verification Strategy

Para cada requisito `PROOF-NN` em `spec.md`, escrever teste que checa resultado declarado, não apenas o fluxo interno da implementação. Asserções negativas são obrigatórias para timeout, cap e certificado inexistente quando pertinentes. O Verifier independente compara o estado final com `spec.md` e registra arquivo:linha, resultados executados e sensor de discriminação.
