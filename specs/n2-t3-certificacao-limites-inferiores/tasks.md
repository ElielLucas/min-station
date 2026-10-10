# MIN-STATION — N2-T3: plano de tarefas e gates

**Estado:** `E1–E5 CONCLUÍDAS — GATE N2-T3 ACEITO PARA PROSSEGUIR À N2-T4` (2026-10-10). **Evidência:** 115/115 N2-T3 e 80/80 N2-T2B (execuções com Gurobi relatadas pelo pesquisador), Ruff PASS; 7/7 N2-T1 e verificadores N1-T7/N2-T1 PASS (reexecutados sobre pacote reconstruído). **Ressalvas:** commit N2-T3 ainda não informado; revisão independente formal do código não foi apresentada, embora os testes matemáticos e o parecer independente da formulação estejam disponíveis. Ver registro formal em `docs/technical/plans/execucao/n2-t3-gate-aceite-certificacao.md`.
**Documentos:** [spec.md](spec.md) · [design.md](design.md)  
**Pré-requisito:** Gate O N2-T2B aprovado. Não abrir N2-T4/N2-T5.

## Execution Protocol

Implementar com `/tlc-spec-driven` e `/karpathy-guidelines` ativos no ambiente local. Seguir o fluxo de testes derivados dos critérios de aceite, revisão independente e validação final de requisitos. **Aprovação desta documentação não autoriza commit automático:** o `CLAUDE.md` do MIN-STATION exige solicitação explícita do usuário para cada commit. Sem push ou PR. Preservar hashes e arquivos congelados.

As tarefas T1–T11 possuem implementação e evidências de validação local. O Gate N2-T3 está registrado como aceito para a etapa N2-T4, com as ressalvas e o escopo precisos do documento formal. A matemática normativa é a revisão v2.1.

## Registro de implementação — E1 (T1–T3)

- **Arquivos novos:** `experiments/alternative-formulations/n2_t3_cert_core.py` e `test_n2_t3_cert_core.py`.
- **T1:** `RationalDual`, `rationalize_snapshot` e `vector_digest` prontos. A identidade incorpora `D` obtido do `DualSnapshot.direct_rc` real, além de K/hash, instância e revisão/solve_id. Vetor pós-projeção em `Fraction`.
- **T2:** cálculo puro exato de L0/L1, e emissor de certificado do **LP completo F-CC+K** que revalida N1; exportação decimal/float conservadora. O arredondamento inteiro é testado matematicamente, mas a **publicação física** fica bloqueada até a prova H-K da E5 (a E1 não certifica MIN-STATION).
- **T3:** N1 analítico com TopK exato e evidência reavaliável. ENUM (E2) e N2 (E3) têm emissores próprios, sem modificar o núcleo E1.
- **Testes locais disponíveis:** 27 testes E1: **27 OK, 0 skipped**; dentre eles, 70 combinações de instâncias pequenas com verificação independente por enumeração de `W,I,J`. Controles matemáticos legados: 18 executados, 10 OK e **8 skipped**, pois `gurobipy` não está instalado aqui.
- **Evidência adicional de E1 informada pelo pesquisador:** 27/27 testes e `python -m ruff check` dos dois arquivos = `All checks passed!`. A regressão total com Gurobi (87 testes), a integração com snapshot real e o freeze permanecem exigíveis para o gate final da N2-T3.
- **Limites preservados na E1:** nenhuma alteração em `n2_t2b_*`, Gate M/O, documentos matemáticos ou freeze N2-T1; sem N2-T4/T5.

## Registro de implementação — E2 (T4)

- **Arquivos novos:** `experiments/alternative-formulations/n2_t3_cert_enum.py` e `test_n2_t3_cert_enum.py`.
- **T4:** `enumerate_global_bound(dual,H,cap,...)` implementa enumeração exaustiva determinística dos `W` conexos e TopK racional; retorna `GlobalPricingBound(source='ENUM')` apenas quando **nenhuma limitação ocorreu**, e `EnumAbstention` sem `ell` sob cap exato/parcial/interrupção.
- **Validação:** `evaluate_enum_theorem_l(...)` recompõe o mesmo mínimo e as evidências com o vetor identificado, verifica `D` contra o snapshot e aplica L0/L1 exatamente. Não usa `ObjBound` ou Gurobi.
- **Cobertura rastreável:** registra total de conjuntos conexos e elegíveis, `truncated=False`, hash dos conjuntos visitados, identidade do grafo `H`, cap, vetor/instância/iteração e testemunho `W,I,J,k`.
- **Risco de identidade:** a E2 confere `D` contra `H` e registra digest do grafo, mas **não demonstra sozinha que o H fornecido é o mesmo `G^r` do master**. A integração E4 deverá fornecer `RestrictedMaster.reach_graph` da mesma instância, vinculando o certificado aos dados reais. O certificado E2 é para o LP parametrizado por esse H; a certificação física também exige H-K da E5.
- **Equivalência com `fcc.enumerar_conexos`:** a rotina usa BFS determinística em Python puro com a **mesma regra conservadora de cap** (`visited >= cap` significa truncamento), evitando importar `fcc.py`/Gurobi apenas para enumerar. A completude é comprovada estruturalmente pelo crescimento por vizinhos, e os testes confrontam independentemente todos os `2^n-1` subconjuntos em instâncias pequenas. Não houve alteração em `fcc.py`.
- **Testes E2 neste ambiente:** 20 testes próprios aprovados, incluindo 120 grafos aleatórios com `n≤6` e força bruta independente de todos `W,I,J`. Total E1+E2: **47/47 OK, zero skips**, também sob outro `PYTHONHASHSEED`; compilação Python PASS. O pesquisador informou 47/47 testes E1+E2 e Ruff PASS em seu ambiente. A regressão com Gurobi completa permanece para o Gate N2-T3.
- **E2 não generaliza o exportador `floor_export` da E1:** ele aceita apenas certificados N1; o certificado ENUM preserva `lb_exact` racional e sua exportação unificada será parte da integração E4/E5, sem mudar o contrato aceito da E1 nesta entrega.

## Registro de implementação — E3 (T5–T6)

- **Arquivos novos:** `experiments/alternative-formulations/n2_t3_cert_box.py` e `test_n2_t3_cert_box.py`; E1, E2 e N2-T2B não foram modificadas.
- **T5:** `build_rational_pricing_lp(dual,H)` constrói em `Fraction` as variáveis e todas as linhas P0–P5 da formulação do pricing, normalizadas como `Aw=b` e `Bw≥h`, incluindo ambas as direções de `H`, `g≤n`, `f≤n-1`, `n=1` e bounds de binárias `[0,1]`. Registra digests de H, vetor, instância e matriz completa. O certificado não confia apenas nesses digests: a matriz recebida é **reconstruída e comparada** antes de qualquer prova.
- **T6:** `certify_box_bound(dual,H,lp,theta,nu)` avalia a fórmula N2 em aritmética racional exata, aceita `θ` livre e projeta `ν` em não negativo; `evaluate_box_theorem_l` reconstrói a matriz e a evidência, reavalia o bound e aplica L0/L1. Um `ell` forjado, `ObjBoundC` ou matriz alterada não é aceito como certificado. O escopo continua **apenas LP completo F-CC+K**, condicionado ao `H` fornecido (vínculo com master será E4, H-K/B0/G2 serão E5).
- **Candidato opcional:** `propose_lp_multipliers(lp)` usa SciPy/HiGHS somente para **sugerir** `θ,ν`; a prova independe do solver e funciona até com vetores zero. Multiplicadores numéricos são racionalizados antes da verificação, nunca tratados como prova isolada. A dependência SciPy é opcional e importada sob demanda.
- **Interface segura:** E3 recebe obrigatoriamente `dual`, `H` e `lp`, em vez de aceitar apenas `lp` e seu digest: isso impede que uma matriz inventada, porém autoconsistente, gere indevidamente `CERTIFIED`. O vínculo entre `H` e o master concreto permanece explicitamente pendente de E4.
- **Testes realizados neste ambiente:** 24 testes próprios E3, incluindo 100 grafos pequenos com força bruta independente de `c*` e três variantes de multiplicadores (300 comparações exatas); total E1+E2+E3 = **71/71 OK, zero falhas e zero skips**; Python `py_compile` PASS. O teste `test_gurobi_pricing_p0_p5_matrix_parity_when_available` confronta objetivos, variáveis e **todas** as linhas da matriz racional com o modelo real de `n2_t2b_pricing.build_pricing_model` quando Gurobi está disponível. A ausência de Gurobi neste ambiente deixa apenas essa paridade para execução local. **O pesquisador reexecutou a E3 em seu venv com Gurobi: 71/71 testes PASS (incluindo paridade P0–P5), zero erros/skips, e Ruff `All checks passed!` nos seis arquivos.**
- **Escopo:** sem alteração de N2-T2B, contratos de E1/E2, Gate M/O, pre-registro N2-T1 ou materiais congelados; E3 não habilita certificação física do MIN-STATION, exportação unificada nem convergência G2.

## Registro de implementação — E4 (T7–T8)

- **Arquivos alterados/novos:** extensão mínima opt-in de `experiments/alternative-formulations/n2_t2b_column_generation.py`; novos `n2_t3_cert_integration.py` e `test_n2_t3_cert_integration.py`. As E1/E2/E3 e os demais módulos legados permanecem inalterados.
- **T7:** `run_column_generation(..., certification_hook=None)` preserva o retorno e as decisões antigas no modo padrão; somente quando informado o hook (interno a `run_certified_column_generation`) captura snapshot **atual** antes de pricing/inserção/descarte. `RestrictedMaster.reach_graph` fornece o H efetivo já validado pela entrada do master. O protocolo `prepare`/`accept` não comita provas construídas após ultrapassagem do orçamento global de tempo/Work.
- **T8:** `run_certified_column_generation(...,options=CertificationOptions(...)) -> CertifiedCGResult` conserva o `base_result` numérico UNCERTIFIED, histórico por `iteration/revision/solve_id`, provas reavaliadas de N1/ENUM/N2 e máximo **racional** de L1 entre iterações. Erros e abstenções não alteram certificados anteriores; ausência de evidência nunca reutiliza `ObjBoundC`/`z_R`. Toda afirmação `CERTIFIED` é **apenas para o LP F-CC+K completo** (`FULL_FCC_K_LP_ONLY`); H-K físico/U/G2/B0 continuam E5.
- **Política de recursos:** E4 não executa LP/MIP auxiliar na certificação: N1/ENUM/N2 são operações em Python puro e o N2 usa `theta=nu=0` (bound global válido, possivelmente fraco). `enum_cap`, `max_enum_vertices`, `max_n2_vertices` e o tempo restante limitam custo; o wall time do controlador inclui cada prova e o Work contabilizado permanece somente dos solves master/pricing. **Não interpretar o N2 com vetores zero como bound LP de melhor qualidade:** candidatos duais auxiliares numéricos serão objeto de trabalho posterior, com contabilização adequada, se necessários.
- **Testes desta preparação:** 20 testes E4 descobertos, sendo 18 aprovados sem Gurobi e dois testes reais de integração Gurobi deliberadamente `skipped` neste ambiente; ao executar o conjunto E1–E4, **91 testes** foram descobertos, **89 PASS + 2 skips por Gurobi indisponível**. São usados fakes apenas para o solver, mas o módulo real de controlador é carregado dos arquivos da E4 e seus caminhos de parada/hook são exercitados. Compilação Python PASS. **Ruff e os 27 testes legados do controlador, mais os dois testes reais da E4, devem ser executados no venv do pesquisador** antes de homologar a E4.
- **Proibições mantidas:** nenhum novo branching, cortes, mudanças em K/freeze, validação física H-K, U/G2/B0, campanhas N2-T4/T5 ou novos `CERTIFIED` em `ColumnGenerationResult` legado.

## Registro de implementação — E5 (T9–T11)

- **Arquivos:** `experiments/alternative-formulations/n2_t3_cert_validation.py` e `test_n2_t3_cert_validation.py` criados; `n2_t3_cert_integration.py` alterado minimamente para guardar uma cópia racional do vetor no `IterationCertification` (campo opcional e retrocompatível). Nenhum código congelado foi modificado.
- **T9:** `validate_k_evidence(S,T,V,adj,A_r,r,K,k_hash=...)` reconstrói G simples, unitário, não dirigido e conexo, confere A_r=G^r por BFS, deriva H e D, recalcula o hash canônico e invoca `assert_valid_cuts` do código histórico. A evidência imutável carrega identidade do grafo original/terminais/cortes e é revalidada antes do uso. K NÃO é regenerado.
- **T10:** `verify_primal_rational(ctx,witness)` verifica em `Fraction` cada variável, coluna (W,I,J), R1/R2/R3, K e limites, produzindo `U=sum(y)`; `initial_primal_witness` gera a semente viável `(V,S,T)`. `check_g2` exige U revalidado e reexecução da evidência E4 do mesmo vetor e instância, e aceita somente gap não negativo `<=1/1_000_000`. Soluções do Gurobi em float não são automaticamente provas.
- **T11:** `finalize_verified_result` reaudita os oráculos N1/ENUM/N2 da trilha E4, evitando que flag/digest/objbound isolado produza certificado físico. `run_verified_column_generation` faz E5 como opt-in e mantém `run_column_generation` legado inalterado. A saída isola LB do LP, LB inteiro MIN-STATION, B0, G2, `rmp_objective` diagnóstico, exportação decimal para baixo, identidade e histórico.
- **B0:** `verify_baseline` aceita candidatos somente com prova física independente por enumeração de subconjuntos de cardinalidade inferior ao valor alegado (até cap explícito), ou prova de não negatividade para zero. A prova NÃO demonstra que o candidato coincide com o valor **oficial congelado** `max(z_COMP^LP,z_core^IP)` ou com cada resultado de solver. Acima do cap ou com core incompleto, B0 permanece `UNCERTIFIED`. Antes de N2-T5, a proveniência do B0 oficial em instâncias grandes exige verificadores próprios, não é inferida do registro histórico nem de incumbentes.
- **Orçamento:** nenhum solve adicional Gurobi na E5; preparação e auditoria E5 consomem tempo de parede, registrado (`validation_wall`). Com `time_limit`, o wrapper reduz o orçamento encaminhado ao CG e recusa selos físicos produzidos fora do prazo. Work do solver permanece medido apenas no controlador, sem custos fictícios.
- **Testes disponíveis neste ambiente:** E1–E5: **115 descobertos, 112 PASS, 3 skips** exclusivamente por ausência de Gurobi (2 E4 + 1 E5); todos os testes específicos da E5 que não dependem do Gurobi passaram. Compilação Python PASS. **Ruff não instalado neste ambiente**. `test_n2_t3_cert_validation.py` cobre K vazio/válido/inválido, identidade adulterada, testemunhos U, G2, B0, permanência e injeção de provas inválidas.
- **Pendente para aceite N2-T3:** executar 115/115 testes no ambiente com Gurobi e Ruff; reexecutar as 87 regressões Gate O e os verificadores de freeze N1/N2-T1; revisar a segurança de H-K, U/G2, B0 e a proveniência do B0 oficial quando relevante; registrar decisão humana explícita em documento separado. **Não abrir N2-T4 automaticamente.**

## Test Coverage Matrix

> Proveniência: `CLAUDE.md`; `test_n2_t2b_master.py`, `test_n2_t2b_pricing.py`, `test_n2_t2b_column_generation.py`, `test_n2_t2b_controles_matematicos.py`, `test_n2_t1_offline.py`; comandos reais do Gate O. Não confundir esses testes com uma certificação de limites da N2-T3.

| Code Layer | Required Test Type | Coverage Expectation | Location Pattern | Run Command |
|---|---|---|---|---|
| Núcleo racional e Teorema L | unit, exatos | Todos os ramos, finitude, vetor único, projeção, D vazio, eta positivo, exportação dirigida, negativos | `experiments/alternative-formulations/test_n2_t3_cert_core.py` | `python -m unittest discover -s experiments/alternative-formulations -p 'test_n2_t3_cert_core.py' -v` |
| Certificadores N1/ENUM/N2 | unit + comparação independente | `ell≤c*`, cobertura/cap, TopK, LP racional P0–P5, adversariais, n=1, overlap | `experiments/alternative-formulations/test_n2_t3_cert_{core,enum,box}.py` | Uma suíte `test_n2_t3_cert_*.py` por arquivo |
| Integração CG e interrupções | integration | Múltiplas iterações, degenerate, Work/time, snapshots, prova anterior, opt-out N2-T2B | `experiments/alternative-formulations/test_n2_t3_cert_integration.py` | `python -m unittest discover -s experiments/alternative-formulations -p 'test_n2_t3_cert_integration.py' -v` |
| K, U/G2, baseline B0 e serialização | unit + integration | H-K, R1–R4 exatas, witness válido/inválido, G2, B0 distinto, justificativa | `experiments/alternative-formulations/test_n2_t3_cert_validation.py` | `python -m unittest discover -s experiments/alternative-formulations -p 'test_n2_t3_cert_validation.py' -v` |
| Legado e freeze | regression | Todas as 87 verificações do Gate O; nenhum skip inadvertido; hashes intocados | `experiments/alternative-formulations/test_n2_t2b_*.py`; `test_n2_t1_offline.py` | Comandos do Gate O e verificadores descritos abaixo |

## Gate Check Commands

Executar a partir da raiz com o ambiente Python do projeto e Gurobi disponível. Os módulos N2-T3 são criados pelas tarefas; não executar os novos comandos até os arquivos correspondentes existirem.

| Gate Level | When to Use | Command |
|---|---|---|
| Quick | Após cada módulo | `PYTHONHASHSEED=0 python -m unittest discover -s experiments/alternative-formulations -p 'test_n2_t3_cert_<modulo>.py' -v` (substituir pelo nome real da suíte) |
| Full | Ao completar entregas E1–E5 | `PYTHONHASHSEED=0 python -m unittest discover -s experiments/alternative-formulations -p 'test_n2_t3_cert_*.py' -v` |
| Regression | Após alterar controlador/master/pricing | `PYTHONHASHSEED=0 python -m unittest discover -s experiments/alternative-formulations -p 'test_n2_t2b_*.py' -v` **mais** `test_n2_t1_offline.py` |
| Integrity | Antes de encerrar E5 | `PYTHONHASHSEED=0 python experiments/alternative-formulations/run_n2_t1.py check` e `PYTHONHASHSEED=0 python experiments/alternative-formulations/verify_n1_t7_gate.py` |
| Build | Ao encerrar cada fase | `python -m ruff check experiments/alternative-formulations/n2_t3_cert_*.py experiments/alternative-formulations/test_n2_t3_cert_*.py` e Ruff dos módulos legados alterados; todos os gates acima |

**Observação sobre glob:** `unittest discover -p 'test_n2_t3_cert_*.py'` seleciona todos os arquivos existentes no padrão. O gate Regression (`test_n2_t2b_*.py`) cobre master, pricing, CG e controles matemáticos (80 testes no Gate O), e `test_n2_t1_offline.py` completa os **87**. Exigir **zero skips inesperados** e conferir contagens, não somente exit code. Correr `ruff` apenas em arquivos efetivamente existentes em cada fase.

## Execution Plan

```text
E1 / fase 1: T1 → T2 → T3        (racionais, L1, N1)
E2 / fase 2: T4                  (ENUM)
E3 / fase 3: T5 → T6             (modelo racional P0–P5 e N2)
E4 / fase 4: T7 → T8             (integração opt-in + histórico)
E5 / fase 5: T9 → T10 → T11      (K, U/G2, B0 e gate)
```

**Dependências entre fases:** E2 depende de T1–T3; E3 depende de T1–T3 e usa E2 para comparação exata; E4 depende dos três oráculos; E5 depende da integração. A execução é sequencial; paralelismo entre branches não está autorizado.

## Task Breakdown

### Phase 1 — E1: núcleo racional, Teorema L e N1

### T1: Representar vetor dual racional identificado

**Status:** VALIDADA — aceita no Gate N2-T3; detalhes dos testes no registro formal.  
**What:** Definir `RationalDual` e conversão exata dos floats de um `DualSnapshot`, projeção `μ,κ≥0` e digest canônico ligado a instância/K/solve.  
**Where:** `experiments/alternative-formulations/n2_t3_cert_core.py`  
**Depends on:** None  
**Reuses:** `DualSnapshot`, `DualValues` e valores imutáveis de `n2_t2b_master.py`.  
**Requirement:** `CERT-01`, parte de `CERT-07`.  
**Done when:** Coeficientes não finitos/índices inconsistentes falham; projeção prévia comprovada; todos os coeficientes e a identidade ficam estáveis ao serializar/reabrir.  
**Tests:** Em `test_n2_t3_cert_core.py`: razão binária exata, NaN, ±inf, negativos projetados, digest reproduzível e instância diferente.  
**Gate:** Quick + Ruff do arquivo criado.

### T2: Calcular L0/L1 e exportação racional segura

**Status:** VALIDADA — aceita no Gate N2-T3; detalhes dos testes no registro formal.  
**What:** Implementar `η,L,δ` e os três ramos de L1 com `Fraction`, exportação para baixo e arredondamento inteiro somente após prova.  
**Where:** `experiments/alternative-formulations/n2_t3_cert_core.py`  
**Depends on:** T1  
**Reuses:** revisão v2.1 §§6.1–6.4 e contraexemplos do parecer.  
**Requirement:** `CERT-02`, `CERT-03`, `CERT-07`.  
**Done when:** Fórmula matemática independente não rotula como `CERTIFIED` um `ell` não validado; `D=∅`, `η>0`, `δ<0` e valor não representável em float passam. A E1 não emite limite inteiro físico sem H-K; o cálculo de `ceil` é validado isoladamente.  
**Tests:** Ampliar `test_n2_t3_cert_core.py` com comparação racional independente e tentativa de injetar `ell` não provado.  
**Gate:** Quick + Ruff.

### T3: Implementar limite analítico global N1

**Status:** VALIDADA — aceita no Gate N2-T3; detalhes dos testes no registro formal.  
**What:** Emitir `GlobalPricingBound(source='N1')` para um único vetor projetado, com prova algorítmica por TopK exato.  
**Where:** `experiments/alternative-formulations/n2_t3_cert_core.py`  
**Depends on:** T2  
**Reuses:** função racional TopK e `H`/domínio de T1.  
**Requirement:** `CERT-04`, `CERT-07`.  
**Done when:** `ell_N1` é finito e cobre `c*` em força-bruta de grafos minúsculos; prêmios negativos não são descartados.  
**Tests:** Adicionar à `test_n2_t3_cert_core.py` casos `n=1`, `S∩T`, prêmios negativos, vetor arbitrário e `ell_N1≤c*`.  
**Gate:** Quick + Ruff + validação independente dos cálculos.

### Phase 2 — E2: ENUM rigoroso

### T4: Implementar ENUM com prova de cobertura

**Status:** VALIDADA; 20 testes E2 PASS neste ambiente, 47 testes E1+E2 e Ruff PASS informados pelo pesquisador.  
**What:** Enumerar `W` conexos e calcular `c*` por TopK exato; abster-se sob cap/truncamento/interrupção.  
**Where:** `experiments/alternative-formulations/n2_t3_cert_enum.py`  
**Depends on:** T3  
**Reuses:** `fcc.enumerar_conexos`, `B_de` e `RationalDual`.  
**Requirement:** `CERT-05`, `CERT-07`.  
**Done when:** `truncated=False` obrigatório; `cap=total` recusado; `cap>total` aceito; contagem e min exato validados por enumeração **independente** `2^n`.  
**Tests:** `test_n2_t3_cert_enum.py`, com conexidade, W unitário, H denso/esparso, S∩T, cap 0/1/total/total+1 e interrupção.  
**Gate:** Full parcial + Ruff.

### Phase 3 — E3: certificado N2 com relaxação de caixa

### T5: Construir P0–P5 racional completo — VALIDADA

**What:** Representar `c,A,b,B,h,u` de P0–P5 exatamente e com índices canônicos, sem copiar matriz numérica do Gurobi como prova.  
**Where:** `experiments/alternative-formulations/n2_t3_cert_box.py`  
**Depends on:** T4  
**Reuses:** `n2_t2b_pricing.build_pricing_model` para comparação semântica; §§5.2 e 6.3 da revisão v2.1.  
**Requirement:** `CERT-06` (modelo).  
**Done when:** Cada variável e linha original tem correspondência definida; `n=1` gera `u_f=0`; sinais e normalização `Bw≥h` são auditáveis.  
**Tests:** `test_n2_t3_cert_box.py`: matriz e avaliação de restrições de padrões fixos no MIP, grafos de n=1/2, raiz/fluxo e todos os limites.  
**Gate:** Quick + Ruff.

### T6: Calcular/verificar `ell_N2` por caixa — VALIDADA

**What:** Avaliar exatamente fórmula N2 para `θ` livres e `ν≥0`; nunca usar o `ObjBoundC` como prova.  
**Where:** `experiments/alternative-formulations/n2_t3_cert_box.py`  
**Depends on:** T5  
**Reuses:** `RationalDual`, matriz racional de T5, resultados ENUM T4 como comparação.  
**Requirement:** `CERT-06`, `CERT-07`.  
**Done when:** Multiplicadores artificiais válidos/inválidos, `ν` projetado e falhas da matriz são tratados; todo caso minúsculo satisfaz `ell_N2≤c*` exato.  
**Tests:** Ampliar `test_n2_t3_cert_box.py` com `θ,ν=0`, positivos/negativos, projeção de `ν`, N2 vs ENUM e bound não ótimo.  
**Gate:** Full parcial + Ruff.

### Phase 4 — E4: integração e histórico

### T7: Adicionar integração de certificação opt-in ao controlador CG — VALIDADA

**What:** Acoplar o certificador antes de `add_column()`/`dispose()`, preservando exatamente a API legada no modo opt-out.  
**Where:** `experiments/alternative-formulations/n2_t2b_column_generation.py`  
**Depends on:** T6  
**Reuses:** `MasterResult.dual`, `RestrictedMaster.reach_graph`, oráculos T3/T4/T6.  
**Requirement:** `CERT-09`, parte de `CERT-10`.  
**Done when:** Snapshot imutável/cópia correta, sem `gp.Model` exportado; nenhuma mudança nos 27 testes do CG sem certificação; Work/tempo de solves adicionais cobertos.  
**Tests:** Novo `test_n2_t3_cert_integration.py` e execução dos testes legados.  
**Gate:** Full + Regression + Ruff dos arquivos alterados.

### T8: Registrar melhor LB e política de interrupções — VALIDADA

**What:** Construir `CertifiedCGResult` com histórico de certificados e justificativas; escolher máximo racional verificado sem usar iteração interrompida não comprovada.  
**Where:** `experiments/alternative-formulations/n2_t3_cert_integration.py`  
**Depends on:** T7  
**Reuses:** resultado de CG, `CertifiedIteration` e status/Work legados.  
**Requirement:** `CERT-08`, `CERT-10`, parte de `CERT-14`.  
**Done when:** Testes com nenhum/um/múltiplos certificados, perda do master, preço interrompido, estagnação e work inválido passam.  
**Tests:** Ampliar `test_n2_t3_cert_integration.py`, verificando justificativa não vazia e separação `rmp_objective`/LB.  
**Gate:** Full + Regression + Ruff.

### Phase 5 — E5: K, U/G2, B0 e aceite

### T9: Garantir evidência por instância da validade de K — VALIDADA

**What:** Vincular prova de validade de cortes à instância e ao hash canônico antes de publicar LB do MIN-STATION.  
**Where:** `experiments/alternative-formulations/n2_t3_cert_validation.py`  
**Depends on:** T8  
**Reuses:** `fcc_k.prepare_k`, `harness.add_cuts_to_model` e verificador `assert_valid_cuts`; não alterar os cortes congelados.  
**Requirement:** `CERT-11`.  
**Done when:** Hash divergente/corte inválido/validação omitida impedem certificado físico.  
**Tests:** `test_n2_t3_cert_validation.py`: K vazio/válido/inválido, hash de conteúdo errado e outra instância.  
**Gate:** Quick + Ruff.

### T10: Verificar testemunho primal racional e G2 — VALIDADA

**What:** Construir/verificar `U` primal com R1–R4 exatas e checar `U−LB_CG≤10⁻⁶`.  
**Where:** `experiments/alternative-formulations/n2_t3_cert_validation.py`  
**Depends on:** T9  
**Reuses:** estrutura de RMP em `n2_t2b_master`, K/`D`/colunas; L1 de T2.  
**Requirement:** `CERT-12`.  
**Done when:** Witness `(V,S,T)` fornece `U=n` e é verificado; perturbação exata falha; G2 positivo/negativo não depende de estacionariedade numérica.  
**Tests:** Ampliar `test_n2_t3_cert_validation.py` com igualdade, violação R3/K, gap menor/maior que 1e-6 e `U` ausente.  
**Gate:** Quick + Ruff.

### T11: Isolar B0, consolidar evidências e passar Gate N2-T3 — ACEITA COM RESSALVAS

**What:** Anexar B0 com origem/prova própria, serializar resultados e fechar a matriz de aceitação sem executar N2-T4/T5.  
**Where:** `experiments/alternative-formulations/n2_t3_cert_validation.py`  
**Depends on:** T10  
**Reuses:** objetos dos módulos N2-T3, `ColumnGenerationResult`, especificação congelada.  
**Requirement:** `CERT-13`, `CERT-14`.  
**Done when:** B0=2 com LP=3/2 não viola checagem espúria; core interrompido não gera B0 certificado; status/justificativa invariantes; teste total, Ruff, freeze e revisão independente aprovados.  
**Tests:** Ampliar `test_n2_t3_cert_validation.py`; executar testes novos, regressão 87 do Gate O, verificadores N1/N2-T1, revisão de rastreabilidade por revisor distinto.  
**Gate:** Full + Regression + Integrity + Build.

## Phase Execution Map

```text
Fase 1: T1 ─→ T2 ─→ T3
                       ↓
Fase 2:               T4
                       ↓
Fase 3:               T5 ─→ T6
                              ↓
Fase 4:                     T7 ─→ T8
                                    ↓
Fase 5:                           T9 ─→ T10 ─→ T11
```

## Traceability and Verification Plan

| Requisito | Tarefa(s) | Evidência objetiva |
|---|---|---|
| `CERT-01` | T1 | Hash e vetor racional pós-projeção íntegros |
| `CERT-02`/`CERT-03` | T2 | Cálculos L0/L1/inteiro/floor em Fraction |
| `CERT-04` | T3 | N1 ≤ c* por enumerador independente |
| `CERT-05` | T4 | ENUM exato e cap recusado |
| `CERT-06` | T5/T6 | P0–P5 racional + N2≤c* |
| `CERT-07` | T1–T6 | Ninguém promove ObjBound ou ell não provado |
| `CERT-08`/`CERT-09` | T7/T8 | Opt-out e histórico sob interrupções |
| `CERT-10` | T7/T8 | Work/tempo rastreáveis e limites encaminhados |
| `CERT-11` | T9 | K válido/mesmo hash e instância |
| `CERT-12` | T10 | Testemunho U exato + G2 correto |
| `CERT-13`/`CERT-14` | T11 | B0 separado, rótulos e gates completos |

## Review & Approval Conditions

T1–T11 possuem testes associados e passaram nas evidências apresentadas. O aceite operacional solicitado está no registro formal, que diferencia testes, auditoria dos hashes, evidência matemática independente e a **ausência de parecer independente novo específico sobre o código E1–E5**. Para publicação científica, solicitar revisão independente desse código e preservar o manifesto SHA-256. Não editar v2.1, parecer ou pré-registro para ajustar resultados. N2-T4/T5/T6 continuam separadas.
