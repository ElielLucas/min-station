# AS-05 — Auditoria preliminar AS-01/AS-02/AS-04 e situação do piloto

**Data:** 2026-10-11  
**Fonte:** snapshot `min-station(20261011-221601).zip`, fornecido pelo usuário.  
**Natureza:** auditoria técnica assistida, **não é revisão matemática independente de autor diferente**.  
**Veredito:** **PENDING / BLOQUEADO** — não converter esta análise em `as04_verdict=PASS` e não executar o piloto científico sem pareceres efetivos.

## 1. O bloqueio reproduzido

O arquivo `docs/technical/plans/execucao/as05-gate-evidence-REVISADO.json` tem `as04_verdict="PENDING"`, `as01_verdict="PENDING"`, indicadores `false` e nomes/caminhos de pareceres vazios. `as05_pilot.verify_preconditions` (`experiments/formulation-comparison/as05_pilot.py:18–38`) bloqueia primeiro a AS-04; depois AS-01/AS-02 e o registro de revisores. Copiar o template não cria uma homologação. O erro `AS05_BLOCKED: AS04 não homologada` é **esperado e correto**.

## 2. Evidências técnicas reproduzidas

Executadas no recorte extraído do snapshot, Python 3.13/SciPy-HiGHS, com os seis arquivos de desenvolvimento extraídos do próprio ZIP. Sem Gurobi neste ambiente.

| Subsistema | Regressão | Resultado | Alcance |
|---|---:|---|---|
| AS-01 | `test_as01*.py` | **9/9 PASS** | Testemunhas com frações racionais; não constitui prova universal |
| AS-02 | `test_as02*.py` | **10/10 PASS** | Modelo, exaustão de estações em grafos pequenos, Sec59 |
| AS-04 | `test_as04*.py` | **30/30 PASS** | Identidades, cortes, pareamento, censura, orçamento |
| AS-05 | `test_as05*.py` do snapshot original | **31/31 PASS** | Plano, bloqueios, regras de decisão sintéticas |
| Auditoria adicional | `as05_review_probe.py` | **24/24 PASS** | 24 grafos pequenos aleatórios determinísticos; U-LP = A(1)-LP ≤ A(2)-LP ≤ A(unitária)-LP; A(2)-MIP = ótimo por enumeração física |

**Limite das evidências adicionais:** os 24 casos foram gerados com seed fixa 20261011, até 7 vértices, três origens e três destinos, autonomia 1 ou 2, com grafos conectados; `as05_review_probe.py` usa `as02_solve.solve_scipy` e `independent_validator.opt_por_enumeracao`. Trata-se de teste numérico e não demonstra dominância universal. Não houve execução da campanha AS-05 nem invocação de Gurobi. `ruff` indisponível neste ambiente; o usuário executou Ruff anteriormente na AS-05, mas isso não substitui lint desta nova entrega.

## 3. Revisão preliminar dos argumentos AS-01

**3.1. Formulação e tradução (evidência favorável, ainda não homologada).** `formulacao-a-grupos-origens.md` especifica A1–A7; `as02_model_a.py:141–180` materializa as duas conservações por grupo, atendimento, ativações local/global e K. A variante U em `as02_model_a.py:182–208` coincide, nos limites nodais e no balanço, com `baseline.py:103–125`; ressalva: o fluxo no baseline MIP é inteiro, enquanto a variante U nova usa fluxo contínuo, diferença que precisa ser justificada via integralidade/exatidão com y fixo.

**3.2. Exatidão inteira A (pendência de prova independente).** `provas-formulacao-a.md:9–42` constrói fluxos de caminhos físicos e projeta uma solução A com y binário na U. A direção U→instalação usa como lema a exatidão inteira da U, cuja prova completa com terminais sobrepostos precisa ser checada pelo revisor. Os testes físicos oferecem suporte empírico restrito.

**3.3. Um grupo U-LP e refinamento A (argumentos examinados, não homologados).** `provas-formulacao-a.md:44–83` fornece levantamento por tipo de vértice (inclui S∩T) e agregação de subgrupos; a identidade dos coeficientes de A4 e os testes de cadeias LP são consistentes nos casos auditados. O revisor deve examinar simbolicamente todos os casos e a preservação de `p` e `h`.

**3.4. A unitária → caminhos e F-CC → B (NÃO HOMOLOGADOS).** As equivalências e inclusões de `provas-formulacao-a.md:84–90` e `relacoes-lp-formulacao-a.md` exigem verificar formalmente decomposição de fluxos, retornos à origem, sobreposição S/T, incidência de configurações e hipótese R3. Essas relações não são necessárias para executar o contraste principal U/U+K/A2+K, mas não devem ser publicadas como teoremas sem prova externa.

**3.5. Controle Sec59 e T18 (evidência parcial).** Os testes verificaram numericamente `zLP(U+K)=11/3` e `zLP(A2+K)=9/2` para a partição testemunha de Sec59 e usam testemunhas racionais. As afirmações F-CC+K=5 e OPT=7 permanecem referências não reproduzidas nesta auditoria. A errata T18 aborda a ausência de acoplamento global A5, sem generalização indevida com K.

## 4. Revisão preliminar AS-02

- O compilador é determinístico e explicita A1, A2, A3, A4, A5 e K (`as02_model_a.py:141–180`).
- Testes de exaustão enumeram instalações em sete topologias pequenas e comparam com oráculo físico construído sobre o grafo original (`test_as02_model_a.py`; `experiments/cuts/independent_validator.py`).
- Em caso fracionário adverso, remover A5 reduz o LP de 1 para 0,5, e o teste detecta a mutação.
- **PENDÊNCIAS:** revisão de terceiro da correção modelo↔implementação; teste de reprodução do worker Gurobi no ambiente real; auditoria dos limites de memória; eventual validação adversarial extra em grafos dirigidos/ponderados **se forem declarados no escopo** — a formulação auditada exige G não direcionado, distâncias unitárias no oráculo.

## 5. Revisão preliminar AS-04 — ressalvas prioritárias

1. **BLOCKER CIENTÍFICO — revisão independente:** `specs/as-04-comparador-multiformulacao/validation-local.md` já registra `PENDING` e informa ausência de execução Gurobi do worker. A homologação não existe no snapshot.
2. **BLOCKER METODOLÓGICO — validade de K:** `prepare_K` (`as02_model_a.py:238–258`) gera C1/C2/C4-DM e chama `assert_valid_cuts` **no mesmo módulo de cortes**. Isso é uma checagem de validade útil, mas não constitui, sozinho, um parecer matemático independente da validade universal de K no domínio inteiro. O revisor deve verificar geradores, validador e provas, incluindo casos S∩T e extremos.
3. **ATENÇÃO — alegação de independência:** `as04_compare.py` usa a flag `k_validated`, que é produzida pelo runner após `prepare_K`; a flag comprova checagem interna, não revisão externa. Não descrevê-la como certificado racional independente.
4. **ATENÇÃO — gate declarativo:** `as05_pilot.py:18–38` testa strings e diferenças de nomes, mas **não verifica a existência/conteúdo dos arquivos de pareceres**. Um JSON preenchido manualmente com nomes diferentes pode satisfazer o gate de código sem que uma revisão real tenha acontecido. O novo `as05_review_preflight.py` verifica existência dos caminhos como defesa adicional, mas nem ele autentica autoria ou analisa a prova; a validação por pessoa distinta continua mandatória.
5. **ATENÇÃO — cenário de execução:** as AS-04/AS-05 preservam resultados censurados e não publicam LP interrompido como bound certificado. Reexecutar com Gurobi real é pendência obrigatória, observando as seis instâncias, os 90s e o protocolo de pareamento.
6. **ATENÇÃO — cap de variáveis:** `run_as05_pilot.py` permite `--max-variables` como parâmetro de execução. Documentar seu valor (`1_000_000` padrão) na evidência de campanha; alteração prospectiva precisa ficar rastreável, pois pode modificar a censura das instâncias.

## 6. Pré-registro e integridade

O hash **canônico do conteúdo do plano** gerado por `as05_protocol.plan_digest` é:

`193a0fb1812c10e502d2e086d9dc2e1f857b724046955bbb0684ad99c038ef3b`

O SHA-256 dos **bytes** do arquivo `results/benchmark/as05-prospective-plan-v1.json` do snapshot é diferente (`339c4559333747fb10fb9132aa90368398ae32bcb7b50955a2bd23cd8e5506cc`) porque mede outro objeto; essa diferença **não é erro**. `results/benchmark/protocol.json` e `instances/manifest.csv` possuem SHA-256 compatíveis com os campos-base do plano: `ee328a...` e `218c49...`, respectivamente. Se o arquivo for reformatado, o hash dos bytes muda e precisa ser registrado.

## 7. Veredito por etapa

| Etapa | Código/testes | Parecer independente | Status autorizado |
|---|---|---|---|
| AS-01 | Evidência técnica favorável | Ausente | `PENDING` |
| AS-02 | Evidência técnica favorável | Ausente | `PENDING` |
| AS-04 | Infraestrutura local testada | Ausente; Gurobi pendente | `PENDING` |
| AS-05 | Implementada; plano validado | Depende das anteriores | **`BLOCKED` / `INVESTIGATE` sem dados LP** |

Não há justificativa para escrever `PASS` em `as05-gate-evidence-REVISADO.json` neste momento. Falta assinatura e parecer de revisor efetivamente distinto, além de execução do comparador no ambiente Gurobi.

## 8. Ações de fechamento real

1. Designar revisores efetivamente independentes e fornecer `as05-roteiro-revisor-independente.md` com documentação, provas e código do snapshot.
2. Revisar AS-01 e AS-02, registrar decisões AC por AC, corrigir objeções substantivas e reexecutar testes se houver mudanças.
3. Revisar AS-04, conferir K e identidade, executar pelo menos um controle pareado real com Gurobi, registrar parâmetros, versão e logs.
4. Criar pareceres **originais** assinados, com responsáveis, hash das fontes revistas, referência `arquivo:linha`, método, contraexemplos, limitações e veredito. Não utilizar templates vazios como `evidence_path`.
5. Somente após decisões `PASS` genuínas, atualizar o arquivo `as05-gate-evidence-REVISADO.json` de acordo com `as02_validation_gate.GateEvidence` e rodar o preflight.
6. Antes da campanha, conferir/cristalizar o adendo de materialidade e executar `--check-plan`; em seguida executar `--execute` com Gurobi, preservar os 18 braços/6 casos e `verify_pilot`.
7. Não promover AS-06 sem interpretar honestamente o resultado `GO`, `STOP` ou `INVESTIGATE`.
