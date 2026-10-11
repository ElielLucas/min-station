# AS-03 — Políticas de agrupamento das origens

**Estado:** protótipo implementado e testado localmente; fechamento bloqueado pelos gates independentes da AS-01/AS-02/AS-03.  
**Versão de contrato:** `AS03-GROUPING-V1`  
**Conexão:** AS-00 (universo / braços), AS-02 (`Instance`, `compile_a`), AS-04 (comparador), AS-05 (promoção condicional A4).

## Objetivo científico

Produzir as partições de origens que alimentam a formulação A **sem consultar resultados LP/MIP, bounds, tempo de solver ou a partição de avaliação**. A política não é descrita como ótima: é uma hipótese estrutural testável. Cada decisão deve distinguir admissibilidade de construção e qualidade do modelo.

## Políticas v1

| ID no código | Papel | Procedimento | Parâmetros sugeridos |
|---|---|---|---|
| `reachability_degree` | Candidata estrutural padrão para A2 | Calcula, para cada origem, graus de entrada/saída em `A_r` e vizinhança de outras origens; ordena por descritores estruturais, com desempate SHA-256 versionado; distribui alternadamente entre dois blocos. Quando todos os descritores são iguais, aplica a ordem canônica balanceada. | `seed=0` |
| `balanced` | Controle independente da estrutura | Ordena os rótulos das origens e os distribui por alternância entre dois blocos. | `seed=0` (sem efeito no controle) |

> **Limitação consciente:** a política `reachability_degree` usa graus e não descobre automaticamente regiões espaciais ou componentes. Um agrupamento por bolsões é uma hipótese futura e exigiria nova versão do protocolo. Não se infere que uma das duas políticas seja superior.

### A2

- Se `m >= 2`, produz **dois blocos não vazios e disjuntos** que cobrem `S` exatamente.
- A saída é canonicalizada antes do hash, para independência da ordem de `V`, `S`, `T` e `A_r`.
- Hash registra instância estrutural, política, `seed`, versão e blocos.
- Com `m = 1`, retorna `NOT_APPLICABLE` para o braço A2 e **mantém a linha do caso**.

### A4 — somente refinamento de A2

- A4 é proposta **somente** mediante autorização registrada pelo gate AS-05.
- Refina *cada* um dos dois blocos de A2 em dois blocos internos, sem mover origens de um grupo pai para outro.
- Só é possível quando ambos os blocos pais contêm pelo menos duas origens (`m >= 4` é necessário, mas não suficiente para partições desequilibradas).
- O hash A4 inclui `parent_hash`; o algoritmo verifica o hash e a instância associados ao pai.
- Não comparar `A4` contra `A2` como hierarquia LP, salvo quando existe refinamento comprovado; partições não aninhadas **não têm dominância geral garantida**.
- Em modo de teste, `authorized_by_as05=True` apenas exercita a API e **não constitui autorização real para uma campanha**. O executor deve rastrear a aprovação a uma decisão AS-05 versionada.

## Orçamento e abstenção

O estimador calcula, antes de construir o modelo:

\[
N_{var}=n+k(a+n+m)+h,\quad h=|S\cap T|,\quad a=|A_r|.
\]

É a contagem exata de variáveis do `compile_a` da AS-02, incluindo variáveis de permanência para a interseção de terminais. Também estima as restrições `3kn+m+n+|K|`, um limite superior de coeficientes não nulos e **um proxy heurístico de memória**. O proxy considera uma margem multiplicativa explícita; **não é um limite superior de RSS ou prova de capacidade de memória**.

| Status | Interpretação | LP/MIP |
|---|---|---|
| `READY_FOR_BUILD` | Filtros prévios satisfeitos; tentativa de construção permitida | Não medido |
| `NOT_BUILT_SIZE` | Variáveis/restrições/não zeros acima do cap pré-registrado | Ausente (`null`) |
| `NOT_BUILT_MEMORY` | Proxy de memória ultrapassou cap; não afirmar OOM real | Ausente (`null`) |
| `NOT_BUILT_BUDGET` | Tempo remanescente abaixo da reserva mínima definida | Ausente (`null`) |
| `NOT_APPLICABLE` | Partição k solicitada matematicamente impossível ou A2 não disponível | Ausente (`null`) |
| `NOT_AUTHORIZED` | A4 ainda não promovida por AS-05 | Ausente (`null`) |

Os estados não excluem o caso do universo de AS-00. O comparador da AS-04 deverá registrar também falhas **após** a construção, como `ERROR`, OOM e timeout, sem reclassificar essas falhas como incapacidade de representação prevista.

`k_cuts` é um argumento opcional para contabilizar os cortes K conhecidos. Uma previsão sem os cortes **não é uma medição completa do braço +K**. A AS-04 deverá fornecer K gerado conforme a política congelada; caso não o faça, rotular explicitamente a previsão como *sem K*.

## Reprodutibilidade e não vazamento

- As funções `partition_two`, `refine_four` e `plan_a2` não recebem nem consultam objetivos, bounds, tempos de solver, resultados da avaliação ou nomes de formulações vencedoras.
- O campo `case_name` é **apenas identificação do registro**, não entra na construção dos blocos.
- Seeds, política e parâmetros devem ser registrados **antes** de rodar qualquer braço no conjunto de avaliação. O default inicial para desenvolvimento é `reachability_degree`, `seed=0`, com `balanced` como controle.
- Nunca reajustar o agrupamento para acomodar resultados observados da partição de avaliação. Toda mudança requer nova versão de protocolo, justificativa e reporte de desvio.
- Preservar as 31 instâncias D/A de AS-00 (14 desenvolvimento / 17 avaliação), inclusive casos não construídos.

## Estrutura e APIs

```text
experiments/alternative-formulations/
├── as03_grouping.py          # partition_two, refine_four, is_nested, hashes
├── as03_size.py              # estimate_size, BuildBudget, BuildDecision
├── as03_planner.py           # plan_a2, plan_a4, PlannedArm
├── run_as03_smoke.py         # verificação de integração AS-02 sem solver
├── test_as03_grouping.py
└── test_as03_size.py
```

`plan_a2` retorna `PlannedArm(grouping, decision)` e `plan_a4` retorna o mesmo contrato; `.to_record()` fornece campos serializáveis em JSON, inclusive `policy_version`, `instance_hash`, `partition_hash`, `parent_hash`, estimativa e valores `measured_* = null`.

## Limites do resultado da AS-03

A AS-03 **não** executa pilotos, não escolhe a melhor política, não prova melhora de LP nem homologação da formulação A. Os testes de integração com `compile_a` validam contagem e compatibilidade estrutural. A AS-04 será responsável por executar braços comparáveis com o mesmo K, orçamento e conjunto de instâncias.

## Gate de encerramento

- Testes AS03-01..05 e sensor de discriminação aprovados no checkout real.
- Validadores de spec e tarefas, Ruff e `git diff --check` aprovados.
- `AS02=PASS` e revisão matemática independente de AS-01/AS-02 registrados.
- Revisor independente (autor diferente do verificador) deve emitir `validation.md` com PASS/FAIL, caminhos/linhas e decisões.
- Commits locais atômicos por tarefa conforme `/tlc-spec-driven`; sem push.
