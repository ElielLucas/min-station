# AS-04 — Protocolo do comparador multiformulação

**Status:** infraestrutura implementada para testes, sem campanha AS-05/AS-06.
**Spec:** `specs/as-04-comparador-multiformulacao/spec.md`.

## Definições e comparações

| ID | Formulação / papel | Construção nesta etapa |
|---|---|---|
| `U` | Base U, fluxo contínuo, `y` binário no MIP, **WITHOUT_K** | Adapter AS-02; pronta |
| `U_K` | Base U+K (COMP em relatórios históricos) | Adapter AS-02; pronta |
| `A2_K` | Formulação A com dois grupos gerados AS-03 | Pronta; execução depende de gate AS-01/AS-02 |
| `A4_K` | Refinamento de A2 em quatro grupos aninhados | Pronta; execução depende também de AS-05 |
| `CUTS_K`, `B_K`, `C_K` | Alternativas condicionais posteriores | `NOT_AUTHORIZED`, sem medida ou zero imputado |
| `FCC_K` | F-CC+K **completa** (nunca RMP restrito) | `NOT_AUTHORIZED` até integração completa |
| `CORE_IP` | Controle de limite inferior, **não** solução física | `NOT_AUTHORIZED` até integração específica |

Comparações pareadas predefinidas: `K_EFFECT=U→U_K`, `A_EFFECT=U_K→A2_K`,
`REFINEMENT_EFFECT=A2_K→A4_K`. A relação entre braços exige mesma instância,
mesma fonte `A_r`, mesma política/seed/threads/orçamento, e, onde aplicável,
mesmo hash de K. Instância relacionada de avaliação não é fonte de validação independente.

## Execução e recursos

- FC-01 `run_bounded` supervisiona **cada braço** em processo isolado, com deadline
  absoluto desde startup. Carregamento, verificação SHA, geração de A_r, K,
  construção, presolve/solver e validação ficam dentro do orçamento por braço.
- A implementação **repete** o carregamento e K para cada braço (não oculta ou
  rateia custo compartilhado). Esta convenção deve ser idêntica em todos os braços.
  **Inclusive U prepara K apenas para obter o hash de referência, mas não adiciona
  os cortes ao modelo.** Assim, U vs U_K isola o efeito dos cortes sobre o modelo;
  a diferença de `wall_total_s` não mede a economia operacional de deixar de
  calcular K. Esta distinção deve aparecer nas análises subsequentes.
- O loader e auditoria de bytes vêm de `fc_instances.load_instance` (FC). A fase
  `preparation` é cronometrada pelo supervisor; um wrapper isolado mede as partes
  `input_load_s` e `reachability_s` durante a chamada. A soma pode ser inferior ao
  valor da fase pelo overhead de mensagens e inicialização do worker.
- `solver_runtime_s` inclui presolve; `presolve_wall_s=null` até instrumentação
  suportada, **não zero**. `solver_work`, `nodes` e `ru_maxrss` (pico acumulado do
  subprocesso Linux) são reportados se observados; RSS não é proxy seguro de RAM.
- Cap de número de variáveis limita tentativa de build. Excedê-lo dá
  `NOT_BUILT_SIZE` e preserva o caso no denominador; **não prova inviabilidade**.
- `memory_limit_bytes` opcional em `SolverPolicy` usa limite de espaço virtual
  do SO (`RLIMIT_AS` Linux), não medição de RSS nem prova de cap real.
- Uma instância do manifesto deve ser especificada em cada execução; as rodadas
  finais, conjunto de casos e critérios de promoção pertencem a AS-05/AS-06.

## Evidência matemática e científica

`lp_opt_value` é publicado somente se Gurobi devolve `OPTIMAL` para o **LP
completo**. Interrupções não exportam primal LP como limite inferior global;
`lp_dual_bound` permanece nulo nesta versão.

`mip_numeric_bound` deriva do `ObjBound` de um **MIP completo** e é uma evidência
numérica de solver, não um certificado racional. `mip_numeric_incumbent` contém
apenas o objetivo incumbente informado pelo solver. `physical_validated_ub`
só é preenchido após a instalação passar por
`experiments/cuts/independent_validator.viavel` no grafo original. `rational_verified_lb_exact`
permanece nulo: a AS-04 não executa um verificador de provas FC-03.

Quando um braço falta, atinge cap, tem OOM, timeout, falha de licença ou ainda
não tem adapter, sua linha permanece no relatório e a comparação fica censurada
ou não comparável; **não** se atribui `0`, ótimo, viabilidade ou bound.

## Sec59 — regressão do efeito da partição

Na `Sec59(L=7), r=1`, com K congelado C1+C2+C4-DM:

| Modelo | LP HiGHS observado (smoke local) |
|---|---:|
| U | `7/3` |
| U+K | `11/3` |
| A2+K, política estrutural AS-03 (seed=0) | `11/3` |
| A2+K, partição de testemunha `(s1,s2) | (s3)` | `9/2` |

A última partição é um **controle matemático selecionado a priori no teste**.
Ela não deve ser substituída pela partição automática em um relatório de
campanha nem escolhida post hoc para representar o resultado médio de A2.

## Regras de publicação

`as04_reporting.publish_run` exige exatamente os braços planejados, cria
um **diretório novo** (`exist_ok=False`), grava JSON, CSV e manifestos SHA-256.
Verificação por `verify_run` após a escrita. Resultados históricos FC/N1/N2
permanecem intocados. O manifesto gerado não certifica as provas matemáticas.

## Gates abertos

- Validação independente das provas da AS-01 e autorização AS-02, conforme
  `as02_validation_gate.GateEvidence`. Um JSON com booleans não substitui
  evidências assinadas e revisadas por outro responsável.
- Testar o executor com Gurobi no checkout real; aqui o smoke foi executado
  com SciPy/HiGHS, que **não** é o backend de comparação principal.
- Ruff, revisão independente dos testes/artefatos da AS-04, commits atômicos.
- AS-05 para experimentar várias instâncias e, separadamente, liberar A4.
