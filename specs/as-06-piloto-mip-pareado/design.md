# AS06 — Piloto MIP pareado — Design implementado

**Status:** infraestrutura criada; revisão independente e testes reais Gurobi pendentes.  
**Spec:** `specs/as-06-piloto-mip-pareado/spec.md`.

## Decisões

1. **Não alterar o comparador AS04/AS05.** `as06_mip.py` compila com `compile_u(..., relax=False)` e `compile_a(..., relax=False)` já existentes. Compilador garante y binária e variáveis contínuas de fluxo.
2. **Separar base vs +K.** U não invoca geradores de K. U_K e A4_K usam geradores históricos e validador bitset-v2, no worker e no budget individual.
3. **Mesmos dados, seeds e parâmetros.** Plano derivado de `as05-factorial-plan-v1.json`, validando relatório, manifesto e hashes AS05; recusa split de avaliação. A4 usa refinamento aninhado fixo.
4. **Deadline real FC01.** `run_bounded` inicia um worker por braço e contabiliza também import/parse, preparação, solve e validação. `Params.TimeLimit` recebe o saldo de wall. Em caso de interrupção do supervisor, descartar bounds parciais não verificáveis.
5. **Dual numérico ≠ ótimo certificado.** `ObjBound` e `ObjVal` apenas numéricos Gurobi. Oracle independente valida y no grafo físico e matching. Um UB apenas numérico não serve ao gate. Callback registra seus próprios eventos; o tempo para confirmar a viabilidade é pago depois do solve.
6. **Resultado append-only.** `as06_reporting.py` grava checkpoints/sidecars e relaciona relatório, CSV, análise e manifestos. Retomada não sobrescreve run final.
7. **Replicação controlada.** `make_plan(stage='replication')` só produz plano se `verify_analysis` comprovar GO. Replicação usa 6 × 3 × 2 = 36 solves, sementes 42,43,44, 600 s totais por braço.

## Arquitetura

```text
results/benchmark/as05-factorial-* (somente leitura)
              |
       make_plan / validate_plan
              |
        run_as06_mip.py
              |
           fc_budget.spawn
              |
   _load_timed → (_timed_k quando +K) → compile_u/a (MIP)
              |
      _solve_mip Gurobi + callbacks
              |
   independent_validator.viavel → UB física/gap
              |
  checkpoint.sha256 → report/arms.csv/manifest
              |
      --verify [--audit-physical] → --analyze → gate
              |
        GO? → plano novo 600 s / seeds 42,43,44
```

## Validade e riscos

- Não inferir ganho inteiro de ganhos LP anteriores.
- Gurobi pode encontrar incumbente cuja instalação é fisicamente inválida: bloquear, nunca reportar como UB física.
- A4 secundário selecionado após LP: não é evidência confirmatória.
- Comparar tempo fim-a-fim primeiro. Tempos apenas de `optimize()` não refletem custos de K e build.
- Medida de `ru_maxrss` em Linux corresponde aproximadamente a KiB; proxy antes do build não substitui RSS medido.
- Nenhuma chamada Gurobi executada na construção desta entrega; somente teste MIP HiGHS opcional e mocks.

## Exit Gate

Código e testes locais podem estar concluídos sem que a **pesquisa** esteja homologada. Exigir relatório Gurobi real e validador/revisor independente antes de atualizar gate científico ou decidir AS11.
