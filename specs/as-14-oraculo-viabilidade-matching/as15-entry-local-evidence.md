# Pré-gate da AS15 — Cobertura residual da AS13 e N08 da AS14

**Situação:** correções locais verificadas; aguardando rechecagem externa antes de alterar o gate da AS15 para GO.

**Base:** parecer independente AS13 R3 (`specs/as-13-fundamentacao-h2-hl/validation.md`, §R3.3) e AS14 R2 (`validation.md`, §R2.7/§R2.9), preservados sem alterações.

## Escopo exato

- Guardas da AS13: `H2 excludes physical`, `H2 partial excludes`, `HL projection identity fails`. Novos testes em `experiments/cuts/test_as13_as15_guards.py` **injetam** uma H2 inválida, H2 parcial inválida e a omissão de um padrão viável sem alterar `β`. Exigem o erro específico, não apenas a presença de uma contagem.
- Quarto sobrevivente, ordem 2: combinação de coeficientes inválidos em `G_R` com a guarda de validade H2 desativada. O teste também falha; as outras guardas não mascaram o erro.
- N08: novo teste `test_as15_entry_t_only_change_cannot_reuse_viable_cache` em `test_h2_oracle.py`. Instâncias `(V=(0,1), E=∅, r=0, S=(0,), T=(0,))` e a mesma com `T=(1,)` partilham todos os dados **exceto T**. A primeira é VIABLE por permanência zero; a segunda INFEASIBLE. Um único `MatchingOracle` não pode devolver `VIABLE` do cache para a segunda. O teste existente que só mudava `S` passou a mudar `T` também.

## Mutação de fonte reprodutível

`experiments/cuts/verify_as15_entry_mutations.py` executa cinco mutações reais **em cópias temporárias**: três remoções de guardas, o mutante combinado e a remoção de `T` do fingerprint. Verifica que a base passa antes de cada mutação e que a falha é uma asserção pertinente; não altera o checkout nem `validation.md`.

**Resultado local:** 5 mutações injetadas, 5 detectadas, 0 sobreviventes. Em N08, a asserção falha por `Status.VIABLE != Status.INFEASIBLE`, demonstrando contaminação real do cache. Na HL, a comparação de β permanece correta quando a guarda de identidade de projeção é removida; por isso a mutação só é detectada pela identidade.

## Regressão local executada

| Suite | Resultado |
|---|---|
| `test_as13_foundations.py` | 27/27 PASS |
| `test_as13_as15_guards.py` | 3/3 PASS |
| `test_h2_oracle.py` | 42/42 PASS |
| `verify_as15_entry_mutations.py` | 5/5 mutações detectadas |
| `verify_as14_discrimination.py` | 7/7 mutações detectadas |
| `verify_as14_r1_mutants.py` | 5/5 mutações detectadas |
| Python `-O`, testes AS13 guards/AS14 | 3/3 e 42/42 PASS |

A verificação Ruff ainda precisa ser executada no ambiente do repositório; não estava disponível no ambiente que produziu o patch. Não foi feito commit.

**Gate:** AS14 permanece `PASS/GO` conforme Opus R2. **AS15 permanece `STOP` até rechecagem independente dos dois pré-requisitos, lint dos novos arquivos e fixação da proveniência do código**. Não iniciar experimentos AS15 com estes resultados locais apenas.
