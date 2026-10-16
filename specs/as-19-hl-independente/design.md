# AS19 — Design de microtriagem HL independente

## Pipeline

```text
Decisão do pesquisador (HL independente de H2)
    |
COMP+K LP y*  ──> suporte R explícito e pequeno
    |
β com oráculo AS14: check(F) / se VIABLE descarta
    |
Enumera TODOS z ∈ {0,1}^R com orçamento global e local
    |
UNKNOWN / limite / incompleto? ──> ABSTAIN (zero cortes)
    |
β=min_{viáveis} α'z em Fraction; lhs(y*) < β?
    |
Emite corte e hashes estáveis; LP COMP+K+H2+HL
    |
Evidência sintética K4; NÃO promover a benchmark real
```

`experiments/cuts/hl_local.py` implementa somente corte HL por vetor de coeficientes racionais **fornecido** (padrão alfa unitário), com enumeração exaustiva de `2^k` padrões certificados pela infraestrutura AS14. `MatchingOracle.check()` garante VIABLE com matching completo, INFEASIBLE com testemunha de Hall ou UNKNOWN. Para cada padrão, a classificação e certificado são incorporados ao hash estável. `UNKNOWN` nunca suporta `β` positivo.

O runner `run_hl_micro.py` usa exatamente `compile_u`/`K` via `verify_as13_foundations.solve_comp_lp()`, os cortes H2 dos quatro trios e, por fim, o HL calculado. Nem ele nem a certificação abrem novo braço MIP. Os dados não incluem solves Gurobi de instâncias reais.

### Contratos

- Entrada: `PhysicalInstance`, `y_star` em `[0,1]^V`, suportes explícitos `R⊆V`, opcionais `α_v≥0` e `HLOptions`.
- Saída: `HLReport` com status, registros por suporte, número de chamadas, tempos, cortes e hashes; cortes contêm `Fraction` para `α` e `β`.
- Falha conservadora: `UNKNOWN` de um único padrão => nenhum corte daquele suporte. Limite de chamadas, orçamento e tamanho se aplicam inclusive antes do oráculo.
- Identidades: `instance_sha256` deriva de vértices/arestas/máquinas/r; hash da linha depende de todos os coeficientes racionais e RHS; certificado contém hash de cada diagnóstico físico e sua ordem estável.
- Integração futura: deve ler cortes do relatório e adicionar constraints somente se `CUT` certificado. Esta etapa não altera geração/heurística de H2.
