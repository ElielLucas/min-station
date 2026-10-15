# AS14 — Parecer do verificador independente (R1)

**Data:** 2026-10-14
**Papel:** verificador independente (autor ≠ verificador). Os resultados do autor não foram aceitos como prova; tudo o que aparece abaixo foi reexecutado ou testado com código próprio.
**Checkout:** branch `novos_testes`, HEAD `3baf7b188292982294e475aa48ef98272bb40f0f` (2026-10-14 14:50:13 -0300). Python 3.12.3 via `poetry run`.
**Ressalva de proveniência:** o código da AS14 **não está no HEAD**. Os arquivos estão não rastreados (`git ls-files --error-unmatch experiments/cuts/h2_oracle.py` falha). Por isso o campo `source_commit` dos relatórios não identifica o código auditado. Os SHA-256 dos arquivos auditados estão na §6.

## Veredito

**GATE AS14: STOP.** A AS14 **não** está concluída.

- Correção do oráculo: **nenhum contraexemplo encontrado.** 17.360 máscaras próprias e 742 máscaras do autor (reproduzidas) concordam com oráculos físicos independentes. Os certificados VIABLE e INFEASIBLE foram reproduzidos. Nenhum UNKNOWN foi promovido a INFEASIBLE, inclusive sob relógio adversarial.
- Motivo do STOP: a **cobertura adversarial é insuficiente**, e há **um defeito de contrato em AS14-03**.
  - Cinco mutantes próprios, não equivalentes, sobrevivem à suíte unitária do autor. Três deles (R23, R29, R30) também sobrevivem ao `verify_as14_oracle.py`.
  - Um desses sobreviventes (R29) produz certificado VIABLE **falso** através do cache.
  - Dois deles (R09, R10) violam exatamente a semântica de terminais que a seção *Independent Test* da spec manda testar.
- **AS15 continua bloqueada** por dois motivos: este STOP, e os quatro mutantes residuais da AS13 (R3.3), que seguem abertos. As mensagens `H2 excludes physical`, `H2 partial excludes` e `HL projection identity fails` existem apenas em `verify_as13_foundations.py:399,408,427`; nenhum teste as exige.

## 1. Comandos executados e resultados

| # | Comando | Resultado observado |
|---|---|---|
| 1 | `poetry run python -m unittest discover -s experiments/cuts -p 'test_h2_oracle.py' -v` | 35/35 OK |
| 2 | `poetry run python -m unittest discover -s experiments/cuts -p 'test_as13_foundations.py'` | 27/27 OK |
| 3 | `poetry run python experiments/cuts/verify_as14_oracle.py --output results/as14/as14-oracle-audit-verifier-r1.json` | exit 0; `physical_masks_checked=742` (68+674), `H2_supports_certified=36`, `unknown_promoted_to_infeasible=0`; `source_commit=3baf7b1…` (ver ressalva). O mesmo conteúdo, descontados tempos e hashes de certificado que contêm tempo, também saiu em uma execução separada para o scratchpad e é idêntico a `results/as14/as14-oracle-audit-001.json` |
| 4 | `verify_as14_oracle.py --output results/as14/as14-oracle-audit-001.json` (tentativa de sobrescrita) | `FileExistsError`; o arquivo existente foi preservado (append-only confirmado) |
| 5 | `poetry run python experiments/cuts/verify_as14_discrimination.py` | 7 injetados, 7 mortos (reproduz o sensor do autor) |
| 6 | `poetry run ruff check <6 arquivos AS14>` | **7 erros**: F401 em `test_h2_oracle.py:17` e em `verify_as14_oracle.py:11`; E402 em `verify_as14_oracle.py:24-28`. O gate *Full* de `tasks.md` exige Ruff; logo, a marcação "gates técnicos locais PASS" de T4 não confere |
| 7 | `python3 .claude/skills/tlc-spec-driven/scripts/validate_spec.py …/spec.md` / `validate_tasks.py …/tasks.md` | 0 erros e 0 avisos em ambos |
| 8 | `python3 .claude/skills/tlc-spec-driven/scripts/validate_state.py specs/as-14-oraculo-viabilidade-matching` | "no .specs/features directory - nothing to check": **passa vacuamente**, porque o validador não suporta o layout `specs/`. Não conta como evidência |
| 9 | `poetry run python -O -m unittest test_h2_oracle` (em `experiments/cuts`) e `review_audit.py` sob `-O` | 35/35 OK; 0 falhas. Os `assert` internos (`h2_oracle.py:201-205`) somem, mas o `raise` explícito (`:126-127`) e as guardas do schema (`h2_oracle_schema.py:69-78`) continuam ativos |
| 10 | `poetry run python specs/as-14-oraculo-viabilidade-matching/verifier-r1/review_audit.py` | 350 instâncias, 17.360 máscaras (14.128 VIABLE, 3.232 INFEASIBLE), 321 com S∩T≠∅ e 150 desconexas; 816 suportes H2. **0 divergências** de status, ν, testemunha, Hall, B̂ e validade do H2. 0 UNKNOWN |
| 11 | `…/verifier-r1/review_micro.py` | 11/11 OK (valores esperados derivados à mão) |
| 12 | `…/verifier-r1/review_budget.py` | 6/7 OK; **1 FAIL esperado**, que documenta o defeito D1 (§4) |
| 13 | `…/verifier-r1/review_mutants.py` | 33 mutantes próprios; resultado em `verifier-r1/mutants-r1.json` (§3) |

Nenhum arquivo rastreado foi alterado (`git diff --quiet HEAD -- experiments/ results/ docs/ specs/as-13-fundamentacao-h2-hl/` retorna 0). Validadores da AS13, COMP+K, K, N1/N2/FC e os congelamentos estão intactos. Os mutantes rodaram apenas em cópias temporárias.

## 2. Oráculo físico independente e semântica

O oráculo do verificador (`verifier-r1/indep_oracle.py`) não importa `independent_validator`:

- **Alcance:** t é alcançável a partir de s sse (a) s=t com s∈T, ou (b) existe uma sequência s=x0,…,xk=t com x1..x(k−1)∈C e distância BFS d(xi,xi+1)≤r no grafo unitário.
- **Matching:** ν é calculado por força bruta sobre permutações de T, sem Kuhn.
- **Deficiência:** max_U(|U|−|N(U)|) é calculada por força bruta sobre subconjuntos de S. Para cada INFEASIBLE, a auditoria exige m−ν = deficiência máxima (König–Hall), além de N(U) completo igual ao declarado e |N(U)|<|U|.

Isso importa porque os testes unitários do autor comparam apenas com `independent_validator.viavel`, que **compartilha** `destinos_alcancaveis` com o oráculo. Um erro de alcance comum aos dois não aparece nessa comparação (ver R10).

Semântica conferida com microinstâncias próprias (`review_micro.py`, valores derivados à mão):

| Item | Caso | Resultado |
|---|---|---|
| Grafo unitário | `PhysicalInstance` recusa peso ≠1, peso `True`, laço, aresta duplicada e adjacência assimétrica (`h2_oracle.py:45-58`) | conforme |
| S∩T, o robô precisa sair do próprio alvo | s–x–t, S={s,x}, T={x,t}, r=1 | VIABLE com testemunha {(s,x),(x,t)} |
| Permanência s=t sem dupla contagem | x isolado em S∩T, y precisa de relé | INFEASIBLE com ν=1 sem estação; VIABLE com {a} |
| Origem sem estação não recarrega | a–m–b–n–c, b–q, S={a,b}, T={c,q}, r=2 | INFEASIBLE, Hall U={a}, N(U)=∅; VIABLE com C={b} (terminal usado como estação) |
| Destino sem estação não recarrega | a–m–t1–n–t2, u–t1, r=2 | INFEASIBLE; VIABLE com C={t1} |
| Duas recargas | caminho de 7 vértices, r=2 | {c,e} VIABLE; {c}, {e} e {b,e} INFEASIBLE |
| Compartilhamento ilimitado | 3 robôs, estrela por w | INFEASIBLE sem estação; VIABLE com {w}, ν=3 |
| Robôs anônimos / Kuhn com aumento | s1→{t1,t2}, s2→{t1} | VIABLE {(s1,t2),(s2,t1)} (o guloso falharia) |
| Hall com expansão alternante | s1→{t1}, s2→{t1,t2}, s3→{t2} | ν=2, U={s1,s2,s3}, N={t1,t2} |
| Estação na origem | s–a–b, r=1 | {s} INFEASIBLE (a bateria inicial já é cheia); {a} VIABLE |
| H2 em cadeia | R={c,d,e}, F={a,b,f,g} | B̂={c,e}, coeficientes c:1, d:2, e:1, RHS 2 |

## 3. Mutação adversarial própria (33 mutantes)

Matriz completa em `verifier-r1/mutants-r1.json`. Colunas: **S** = suíte unitária do autor; **V** = `verify_as14_oracle.py` do autor; **Rv** = scripts do verificador. K indica mutante morto; – indica sobrevivente.

| Mutante | Alvo | S | V | Rv |
|---|---|---|---|---|
| R01 Kuhn sem aumento | matching | K | K | K |
| R02 `seen` compartilhado | matching | K | K | K |
| R03 ν−1 em INFEASIBLE | ν | K | – | K |
| R04 VIABLE com ν≥m−1 | limiar de ν | K | K | K |
| R05 Hall sem expansão alternante | Hall | K | K | K |
| R06 Hall reporta só origens livres | Hall | K | K | K |
| R07 N(U)=∅ sem checagens internas | Hall | K | K | K |
| R08 alcance omite a última origem | laço de viabilidade | K | K | K |
| **R09 origens tratadas como estações no oráculo** | semântica de terminais | **–** | K | K |
| **R10 terminais recarregam (`independent_validator`, compartilhado)** | semântica de terminais | **–** | K | K |
| R11 remoção do `alcance.add(origem)` inicial | permanência | – | – | – (**equivalente**: o laço BFS adiciona a origem, e r≥0 é imposto) |
| R12 bateria com erro de um passo | alcance | K | K | K |
| R13 estação consumida por robô | compartilhamento | K | K | K |
| R14 F=(S∪T)\R | F=V\R | K | K | K |
| R15 F=V | F=V\R | K | K | K |
| R16 B̂ sem adicionar v | B̂ | K | K | K |
| R17 coeficiente 1 para todo examinado | B̂ | K | K | K |
| R18 coeficiente 1 para não candidatos | B̂ parcial | K | – | – |
| R19 complemento UNKNOWN prossegue | UNKNOWN em H2 | K | – | – |
| R20 `remaining()` ignora o budget | budget em H2 | K | – | – |
| R21 timeout promovido a INFEASIBLE | retorno UNKNOWN | K | – | K |
| R22 erro promovido a INFEASIBLE | retorno UNKNOWN | K | – | – |
| **R23 sem `probe()` final antes do cache** | budget | **–** | **–** | K |
| R24 cache armazena UNKNOWN | cache | – | – | – (**inalcançável via `check()`**: UNKNOWN nunca chega a `put`) |
| R25 chave sem estações | chave do cache | K | K | K |
| R26 fingerprint sem r | chave do cache | K | – | – |
| R27 fingerprint sem arestas | chave do cache | K | – | – |
| R28 fingerprint sem S | chave do cache | K | – | – |
| **R29 fingerprint sem etiqueta de tipo (`str(x)`)** | chave do cache | **–** | **–** | **–** |
| **R30 ramo "VIABLE ⊆ INFEASIBLE em cache" desativado** | monotonicidade | **–** | **–** | **–** |
| R31 ramo INFEASIBLE invertido | monotonicidade | K | K | – |
| R32 conflito com a mesma chave ignorado | cache | – | – | – (**inalcançável via `check()`**: chave igual vira acerto de cache antes de `put`) |
| R33 guarda INFEASIBLE do schema + `seen` compartilhado + sem raise de Hall (ordem 3) | defesa em profundidade | K | K | K |

Sobreviventes não equivalentes da suíte do autor:

- **R09 e R10.** O teste `test_as14_01_terminal_as_relay` (`test_h2_oracle.py:69-72`) tem nome enganoso: b e c **não** são terminais em a–b–c–d com S={a}, T={d}. A suíte não tem caso com terminal atravessado sem estação nem com terminal usado como estação, embora a seção *Independent Test* da spec liste "terminais usados como recarga". O `verify_as14_oracle.py` mata os dois mutantes porque compara com o oráculo A_r da AS13.
- **R23.** Nenhum teste usa relógio injetado. O `probe()` em `h2_oracle.py:209` é o único que rebaixa um resultado quando o prazo cruza entre a certificação e o retorno, e nenhum teste o exige. A varredura de relógio do verificador mata o mutante.
- **R29.** Reproduzido: com V=(1,2,'1','2'), a instância A tem a aresta 1–2 e a instância B tem a aresta '1'–'2', ambas com S=(1,), T=(2,). No código atual os fingerprints diferem (A VIABLE, B INFEASIBLE). Sob o mutante, os fingerprints colidem e B devolve **VIABLE falso** com `cache_hit=True`. A etiqueta de tipo em `h2_oracle.py:75-76` sustenta o AS14-05 e não é testada (`test_as14_05_bool_vertex_does_not_alias_integer` testa só `bool`).
- **R30.** `test_as14_07_cached_monotonic_conflicts_fail_closed` (`test_h2_oracle.py:264-275`) exercita só o ramo INFEASIBLE-depois-de-VIABLE (`h2_oracle_cache.py:53-54`). O ramo VIABLE-depois-de-INFEASIBLE (`:51-52`) pode ser removido sem que nada falhe.

## 4. Budget cooperativo e operações indivisíveis

| Teste (`review_budget.py`) | Observação | Resultado |
|---|---|---|
| `destinos_alcancaveis` com 0,2 s e budget de 0,05 s | a chamada **não é preemptada** (wall ≥0,2 s) | UNKNOWN, sem ν e sem certificado: conforme |
| `_grafo_unitario` com 0,15 s e budget de 0,05 s | idem | UNKNOWN: conforme |
| Relógio que salta o prazo em cada leitura possível, caminho sem cache | em todo ponto de cruzamento: UNKNOWN, ou certificado com `elapsed < budget` | conforme |
| `classify_h2` com salto em cada uma de 199 leituras | nunca CERTIFIED com candidato UNKNOWN em B̂; estado ∈ {CERTIFIED, UNKNOWN} | conforme |
| **D1: caminho com acerto de cache** | salto entre o `probe()` de `h2_oracle.py:183` e `result()` de `:184` devolve **VIABLE com `elapsed_wall_s=100 ≥ budget_s=10`** | **viola a letra de AS14-03**. O certificado é verdadeiro (foi certificado antes), então não é certificado falso |
| **D2: fingerprint fora do budget** | `sha = instance.fingerprint` (`:157`) é calculado antes de `begin` (`:161`). Com fingerprint de 0,2 s e budget de 0,05 s: VIABLE, wall 0,201 s, `elapsed_wall_s` declarado 0,0001 s | canonicalização não contabilizada; não é certificado falso |
| Kuhn recursivo, m=1500, cadeia de aumento forçada | `RecursionError` | UNKNOWN (`ORACLE_ERROR:RecursionError`), nunca INFEASIBLE: seguro, mas há abstenção sistemática possível. O `manifest.csv` principal tem m de até 1142 |

**Limitação declarada:** o budget é cooperativo. Uma operação indivisível (alcance de uma origem, construção do grafo, fingerprint) pode ultrapassar o prazo por um tempo ilimitado. A garantia verificada é só esta: uma ultrapassagem detectada no caminho sem cache resulta em UNKNOWN e nunca em certificado falso. Não há garantia de tempo de parede.

## 5. Parecer por critério

"Implementação" avalia o comportamento do código. "Cobertura" avalia se os testes do autor detectam regressões do critério.

| Critério | Implementação | Cobertura | Evidência (arquivo:linha) | Observações |
|---|---|---|---|---|
| AS14-01 VIABLE só com ν=m certificado | **PASS** | **insuficiente** | `h2_oracle.py:197,200-202`; `h2_oracle_schema.py:72-74` | 14.128 VIABLE próprios com testemunha bijetiva conferida no oráculo independente. Semântica de terminais não coberta pela suíte (R09, R10) |
| AS14-02 INFEASIBLE com evidência de matching insuficiente | **PASS** | adequada | `h2_oracle.py:112-128,204-205`; `h2_oracle_schema.py:75-78` | 3.232 INFEASIBLE próprios: N(U) completo, \|N(U)\|<\|U\| e m−ν igual à deficiência máxima por força bruta. R01-R07 e R33 mortos |
| AS14-03 orçamento/falha resulta em UNKNOWN, nunca prova de inviabilidade | **FAIL (parcial)** | **insuficiente** | `h2_oracle.py:157,161,181-187,209,213-223` | Cláusula "nunca prova de inviabilidade": PASS (R21, R22 mortos; nenhuma promoção em nenhuma varredura). Cláusula "SHALL retornar UNKNOWN se exceder": violada no acerto de cache (D1). Budget exclui o fingerprint (D2). R23 sobrevive à suíte |
| AS14-04 F=V\R sobre a instância física | **PASS** | adequada | `h2_oracle.py:262-273` | 816 suportes próprios. R14, R15 mortos |
| AS14-05 chave com identidade da instância + estações canônicas | **PASS** | **insuficiente** | `h2_oracle.py:59-80`; `h2_oracle_cache.py:26-29` | R25-R28 mortos. R29 (sem tipo) sobrevive a tudo e gera VIABLE falso via cache |
| AS14-06 só INFEASIBLE certificado entra em B̂ | **PASS** | adequada | `h2_oracle.py:281-304` | R16-R20 mortos; varredura de relógio em `classify_h2` sem promoção |
| AS14-07 VIABLE(C) impede INFEASIBLE(C′⊇C) | **PASS** | **insuficiente** | `h2_oracle_cache.py:46-55` | O oráculo do verificador é monótono por construção; 0 divergências em 17.360 máscaras implicam oráculo monótono nesses casos. O ramo `:51-52` do mecanismo fail-closed não é testado (R30) |

## 6. Proveniência do código auditado (SHA-256)

```
2de7d6d541095c1e09295ae423cada8c3f3348d89c0002e30b18c40012d1170e  experiments/cuts/h2_oracle.py
e2375cd89db47415ef79b3aa5a74c80c1a32b53cbb0115d6cd11dec2e3792592  experiments/cuts/h2_oracle_schema.py
d6b70360af91bb84bdde4807d91ce5d8d011cb67eb0c32be531a41f00794f8ce  experiments/cuts/h2_oracle_cache.py
e6e96df497d43235d069b2dbd4bbfeec708fd0488fa5700b481905d76bb65fd8  experiments/cuts/test_h2_oracle.py
28ae43a120bb96449eeed2b772ddd1faedb31922cd6de35505c8ed644ec2cc12  experiments/cuts/verify_as14_oracle.py
06268b6ca70c394b98755189e9cf77d3a305b6cd924d96403a6a907163f2157b  experiments/cuts/verify_as14_discrimination.py
fb18fd4a02533120129efc68c0acb6078c29f3af8dbade5f8d4852c7973cd352  experiments/cuts/independent_validator.py  (rastreado, inalterado)
```

`specs/…/as14-oracle-evidence.json` tem `source_commit=null` (gerado a partir do ZIP). `results/as14/as14-oracle-audit-001.json` e `…-verifier-r1.json` têm `3baf7b1`, commit que não contém o código da AS14.

## 7. Correções mínimas para reabrir o gate (bloqueantes)

1. **D1, AS14-03:** no caminho de acerto de cache, chamar `probe()` depois de construir a resposta, ou rejeitar quando `answer.elapsed_wall_s >= budget`. Adicionar um teste com relógio injetado que varra os pontos de cruzamento nos caminhos com e sem cache. Isso mata R23.
2. **Semântica de terminais, AS14-01:** adicionar testes unitários com origem e com destino atravessados sem estação (inviável) e com terminal usado como estação (viável), por exemplo os dois casos de `review_micro.py`. Renomear `test_as14_01_terminal_as_relay`. Isso mata R09 e R10.
3. **AS14-05:** teste de colisão int/str (o par A/B da §3), exigindo fingerprints distintos e ausência de acerto de cache. Isso mata R29.
4. **AS14-07:** teste que grava INFEASIBLE(C′) e depois tenta VIABLE(C⊆C′), exigindo `AssertionError`. Isso mata R30.
5. **Ruff:** zerar os 7 erros (ou justificar E402 com `# noqa: E402`, padrão de `sys.path`) antes de marcar o gate *Full*.
6. **Proveniência:** antes do relatório final, versionar o código (commit autorizado pelo usuário) ou registrar no JSON de evidência os SHA-256 das fontes. Hoje `source_commit` não identifica o código.

Depois disso, uma nova rodada do verificador limitada aos itens 1-6 e à reexecução de `review_mutants.py` basta. Não foi encontrada falha matemática que exija nova revisão do oráculo.

## 8. Melhorias futuras (não bloqueantes para a AS14)

- Trocar o Kuhn recursivo por Hopcroft–Karp iterativo antes de qualquer campanha AS15 em instâncias grandes. Com m de até 1142 no benchmark principal, cadeias de aumento longas resultam em UNKNOWN, ou seja, em abstenção de corte.
- Iniciar o relógio antes da canonicalização e do fingerprint, ou declarar formalmente que ficam fora do budget (D2). Guardar o fingerprint em cache na `PhysicalInstance`, porque hoje ele é recalculado em toda chamada (O(E log E)).
- Trocar os `assert` de certificação interna (`h2_oracle.py:201-205`) por `raise` explícito, para que sobrevivam a `python -O`.
- Incluir na suíte unitária um oráculo de alcance que não compartilhe `destinos_alcancaveis` (A_r ou distâncias BFS), já que hoje só o script de verificação tem essa independência.
- R03, R18-R22 e R26-R28 são mortos apenas pela suíte unitária. Se o `verify_as14_oracle.py` passar a ser o gate principal, ele precisa de asserções de ν e de estados H2 sob UNKNOWN.
- Mutantes inalcançáveis via `check()` (R24, R32): proteger as guardas de `CertifiedCache.put` com testes diretos de API, ou documentá-las como defesa em profundidade.
- Adaptar `validate_state.py` ao layout `specs/` ou registrar formalmente a exceção.
- Divergência documental: o critério de sucesso original de `spec.md` ("testes derivados da spec, não espelhados do código") foi substituído por contagens (35 testes, 742 máscaras, 7 mutantes). Esta revisão mostra que as contagens não bastavam. Recomenda-se restaurar o critério qualitativo.

## 9. Artefatos do verificador

Criados por esta revisão; nenhum arquivo existente foi alterado, exceto este `validation.md`, que é novo:

- `specs/as-14-oraculo-viabilidade-matching/verifier-r1/indep_oracle.py`, `review_audit.py`, `review_micro.py`, `review_budget.py`, `review_mutants.py`, `mutants-r1.json`
- `results/as14/as14-oracle-audit-verifier-r1.json`

Nenhum commit nem push foi feito. Este parecer não declara a AS14 concluída e não altera `spec.md`, `tasks.md` ou `design.md`.

---

# AS14 — Parecer do verificador independente (R2)

**Data:** 2026-10-15
**Papel:** verificador independente (autor ≠ verificador). Escopo: verificar as correções exigidas na §7 da R1 e procurar defeitos novos. As contagens do autor (`as14-r1-correction-evidence.json`) foram tratadas como alegações a reproduzir.
**Checkout:** branch `novos_testes`, HEAD `3baf7b188292982294e475aa48ef98272bb40f0f`. Python 3.12.3 e Ruff 0.15.19 via `poetry run`.

## R2.1 Resumo executivo e veredito

**GATE AS14: PASS / GO.**

- As seis correções bloqueantes da R1 (R09, R10, R23, R29, R30 e D1/AS14-03) estão no código atual. Cada mutante correspondente foi reinjetado e é morto pela suíte unitária do autor, pela asserção esperada.
- Nenhum contraexemplo físico foi encontrado. Isso inclui um cache único compartilhado entre 255 instâncias e varreduras de relógio controlado nos caminhos inédito e de acerto de cache, com resultados VIABLE e INFEASIBLE.
- O Ruff está limpo nos sete arquivos da AS14. Os 112 erros globais de `experiments/cuts` são todos de arquivos anteriores à AS14.
- Proveniência: o código **continua sem commit**. A correção 6 da R1 previa duas opções, e foi atendida pela alternativa de registrar os SHA-256 das fontes. Os hashes registrados conferem byte a byte com os arquivos revisados (§R2.6).
- **AS15: STOP**, por um motivo que vem de fora da AS14: os quatro mutantes residuais da AS13 continuam abertos. Antes da AS15 também é preciso fechar a lacuna de teste N08 (§R2.7).

## R2.2 Matriz das correções da R1

| Item | Implementação atual | Teste que mata | Reinjeção (R2) | Situação |
|---|---|---|---|---|
| R09 terminais como estações no oráculo | `h2_oracle.py:197` passa só `stations` | `test_as14_01_origin_terminal_without_station_does_not_recharge` (`test_h2_oracle.py:57`) | FAIL: `VIABLE != INFEASIBLE` | **Corrigido** |
| R10 terminais recarregam no alcance | `independent_validator.py` sem alteração em relação ao HEAD | `test_as14_01_destination_terminal_without_station_does_not_recharge` (`:72`) | FAIL: `VIABLE != INFEASIBLE` | **Corrigido** |
| R23 `probe()` final removido | `h2_oracle.py:213` | `test_as14_03_budget_crossings_include_final_probe_and_cache_hit` (`:186`) e `test_as14_03_final_probe_rejects_certificate_when_clock_crosses` (`:224`) | FAIL: `100.0 not less than 10.0 : ('fresh', 9)` e `VIABLE != UNKNOWN` | **Corrigido** |
| R29 fingerprint sem tipo | `h2_oracle.py:75-80` usa `vertex_key` | `test_as14_05_int_and_str_vertices_never_share_fingerprint_or_cache` (`:292`) | FAIL: fingerprints iguais | **Corrigido** |
| R30 ramo reverso de monotonicidade | `h2_oracle_cache.py:51-52` | `test_as14_07_cached_infeasible_superset_rejects_viable_subset` (`:395`) | FAIL: `AssertionError not raised` | **Corrigido** |
| D1 / AS14-03 cache fora do budget | `h2_oracle.py:183-189`: `probe()` antes e depois de construir a resposta | Os dois testes de R23 (subteste `cache_hit=True`) | N01 e N03 (§R2.4) mortos | **Corrigido** |

Por que D1 está fechado: `result()` lê o relógio em t₁ (`elapsed_wall_s`), e o `probe()` seguinte lê t₂ ≥ t₁, porque o relógio é monotônico. Se t₁ − begin ≥ budget, então t₂ − begin ≥ budget, e o `probe()` lança `_BudgetExceeded`. Logo, nenhum certificado sai com `elapsed_wall_s ≥ budget`. O mesmo argumento vale para o caminho inédito (`:210-213`).

Reinjeção: `poetry run python experiments/cuts/verify_as14_r1_mutants.py` resultou em `injected 5, killed 5, survived 0`. As mutações vêm sem alteração de `verifier-r1/review_mutants.py`, cuja lógica é idêntica à da R1: o único diff é `ROOT` relativo, feito pelo próprio verificador na R1. As falhas foram conferidas uma a uma: cada mutante falha no teste do seu critério, nunca por importação ou sintaxe. No código restaurado, os 41 testes passam.

## R2.3 Testes reproduzidos

| Comando | Resultado |
|---|---|
| `poetry run python -m unittest discover -s experiments/cuts -p 'test_h2_oracle.py' -v` | 41/41 OK (também com `python -O`) |
| `poetry run python -m unittest discover -s experiments/cuts -p 'test_as13_foundations.py'` | 27/27 OK |
| `poetry run python experiments/cuts/verify_as14_r1_mutants.py` | 5/5 mortos |
| `poetry run python experiments/cuts/verify_as14_discrimination.py` | 7/7 mortos |
| `poetry run python experiments/cuts/verify_as14_oracle.py --output results/as14/as14-oracle-audit-verifier-r2.json` | 742 máscaras, 36 suportes H2, `unknown_promoted_to_infeasible 0`. `checks`, status, ν e `instance_sha256` são idênticos aos de `…-001.json` e `…-verifier-r1.json`. Os `certificate_sha256` diferem porque `to_json()` inclui `elapsed_wall_s` |
| `verifier-r1/review_micro.py` | 11/11 OK |
| `verifier-r1/review_budget.py` | 7/7 OK. O teste D1 (`test_cache_hit_crossing_point`), que falhava na R1, agora passa: varredura `[(1,VIABLE,0.0),(2..5,UNKNOWN),(6,VIABLE,0.0),(7,VIABLE,0.0)]`. Os VIABLE com 0.0 são leituras em que todo o intervalo fica do mesmo lado do salto |
| `verifier-r1/review_audit.py` (dentro de `review_mutants.py`) | 0 falhas no código original |
| `verifier-r2/review_r2_adversarial.py` (novo) | 0 falhas: 4.188 checagens de budget (2.577 certificados dentro do prazo, 1.611 UNKNOWN), 6.312 máscaras com cache compartilhado (3.172 acertos), 2.796 classificações H2 sob relógios variados (707 CERTIFIED) |

`review_r2_adversarial.py` verifica quatro invariantes contra o oráculo físico próprio da R1 (`indep_oracle.py`, sem `independent_validator`):
- **I1:** certificado ⇒ `elapsed_wall_s < budget` e status igual ao físico. Testado com budget 0, 1e-9, 0.5, 1 e 10; salto exatamente no prazo, em prazo ± 1e-12 e grande; relógio com base 1000 (não zero) e relógio em degraus; caminhos inédito e de cache; instâncias VIABLE e INFEASIBLE, inclusive com rótulos int e str misturados; chamadas repetidas com budgets `None, 0, 0.05, 0.3, None, 0, 100`.
- **I2:** UNKNOWN nunca traz certificado e nunca entra no cache.
- **I3:** um único `MatchingOracle` atende 255 instâncias embaralhadas em duas rodadas: mesma topologia com `r`, S ou T diferentes, e cópias int/str.
- **I4:** sob qualquer relógio, `classify_h2` só põe em B̂ vértices fisicamente inviáveis, só emite corte quando F=V∖R é fisicamente inviável, e o corte vale em toda instalação fisicamente viável.

Casos de budget pedidos no item 4 e cobertos: chamada inédita e acerto de cache; budget zero (sempre UNKNOWN, também com cache); prazo atingido exatamente (`>=` gera UNKNOWN); cruzamento antes, durante e depois da construção da resposta; certificados VIABLE e INFEASIBLE; budgets diferentes em chamadas repetidas; relógio sempre controlado (exceto nos dois testes de operação indivisível da R1, que usam `sleep` e só exigem UNKNOWN).

## R2.4 Mutação

**Suíte da R1 reexecutada (33 mutantes,** `verifier-r1/review_mutants.py`, resultado em `verifier-r2/mutants-r1-rerun-r2.json`**):** 30 mortos e 3 sobreviventes: R11, R24 e R32. Os três já tinham sido classificados na R1, sem mudança: R11 é equivalente; R24 e R32 são inalcançáveis via `check()`. Na R1 a suíte do autor matava 23 mutantes; agora mata 30. Os ganhos são exatamente R09, R10, R23, R29 e R30. Nenhum mutante morto na R1 passou a sobreviver.

**Mutantes novos da R2 contra as próprias correções** (`verifier-r2/review_r2_mutants.py`, resultado em `verifier-r2/mutants-r2.json`):

| Mutante | Suíte do autor | `review_r2_adversarial` | Classificação |
|---|---|---|---|
| N01 remove o `probe()` após a resposta no acerto de cache | morto | morto | — |
| N02 prazo `>=` trocado por `>` | sobrevive | morto | Não bloqueante: AS14-03 diz "exceder", então `>` também cumpre a letra da spec. Com relógio real, a igualdade exata tem medida nula |
| N03 remove os dois `probe()` do acerto de cache | morto | morto | — |
| N04 `cache.get` ignora a instância | morto | morto | — |
| N05 monotonicidade comparada entre instâncias diferentes | morto | morto | — |
| N06 testemunha truncada no acerto de cache | morto | morto | — |
| N07 `elapsed` medido a partir de 0, não de `begin` | sobrevive | sobrevive | Não bloqueante para a correção: com `time.monotonic` real, todo budget finito vira UNKNOWN. É falha de vivacidade e de métrica, nunca certificado falso. Os testes usam relógios com base 0, onde o mutante é equivalente |
| N08 fingerprint sem T | sobrevive | morto | **Lacuna de teste com certificado falso demonstrável** (§R2.7) |
| N09 `probe()` final movido para depois do `cache.put` | sobrevive | sobrevive | Quase equivalente: o cache passa a guardar um certificado fisicamente válido obtido fora do prazo, a resposta devolvida continua UNKNOWN e o próximo acerto recalcula `elapsed`. Não afeta a correção |

## R2.5 Ruff

- `poetry run ruff check` nos sete arquivos da AS14 (`h2_oracle.py`, `h2_oracle_cache.py`, `h2_oracle_schema.py`, `test_h2_oracle.py`, `verify_as14_discrimination.py`, `verify_as14_oracle.py`, `verify_as14_r1_mutants.py`): **All checks passed!**
- `poetry run ruff check experiments/cuts --statistics` dá 112 erros: 96 E402, 5 E702, 4 F401, 4 F841, 2 F541 e 1 E741. Nenhum está nos arquivos da AS14, já que o recorte acima é zero; `independent_validator.py` também passa. São preexistentes e não entram neste gate.

## R2.6 Proveniência

- `git rev-parse HEAD` = `3baf7b188292982294e475aa48ef98272bb40f0f`. Os sete arquivos da AS14 aparecem como `??` em `git status --short`: a implementação **não está commitada**. Nenhum commit-base é atribuído a ela.
- Os SHA-256 de `as14-r1-correction-evidence.json` (`source_files_sha256`) conferem byte a byte com os arquivos revisados nesta R2: `h2_oracle.py` `5e6dd2b8225e8a2216f72fedcceae4b9f0c243be6a6f6383e9c14767aaa16d4d`, `h2_oracle_cache.py` `d6b70360…f8ce`, `h2_oracle_schema.py` `e2375cd8…2592`, `independent_validator.py` `fb18fd4a…d352`, `test_h2_oracle.py` `93ee7d76…b654`, `verify_as14_discrimination.py` `06268b6c…157b`, `verify_as14_oracle.py` `f5ea2084…9502`, `verify_as14_r1_mutants.py` `3abb025a…a511`. Os testes e evidências desta R2 correspondem, portanto, ao código revisado.
- `git diff --quiet HEAD -- experiments/ results/ docs/ specs/as-13-fundamentacao-h2-hl/ instances/` retorna 0: nenhum arquivo rastreado foi alterado, inclusive AS13, COMP+K, K, N1/N2/FC e resultados congelados.
- Histórico preservado: a R1 deste arquivo, `verifier-r1/` (lógica idêntica à da R1), `as14-oracle-audit-001.json` e `…-verifier-r1.json` estão intactos. A auditoria R2 foi gravada em arquivo novo.
- Recomendação, não bloqueante para a AS14: commitar o código da AS14, com autorização do usuário, antes de qualquer resultado da AS15 que dependa dele, para que `source_commit` passe a identificar o código.

## R2.7 Defeitos novos

Nenhum defeito no código atual. Uma lacuna de teste é relevante:

**N08, terminais T fora do fingerprint, não detectado pela suíte do autor.** O código atual inclui T (`h2_oracle.py:79`), e o I3 confirma que o cache não confunde instâncias que diferem só em T. Mesmo assim, uma regressão que retire T do fingerprint passa pelos 41 testes e gera VIABLE falso via cache.
- Contraexemplo sob o mutante: V=(0,1), sem arestas, r=0, S=(0,). A instância com T=(0,) é VIABLE (permanência s=t). Gravada no cache, ela atende a instância com T=(1,), que é fisicamente INFEASIBLE, e devolve `VIABLE, cache_hit=True`.
- O teste `test_as14_05_same_graph_different_r_and_terminals` (`test_h2_oracle.py:320`) promete cobrir terminais, mas só varia S (`'a'`→`'b'`), nunca T.
- Correção mínima: incluir nesse teste uma instância que difira apenas em T e exigir fingerprint distinto e ausência de acerto de cache.

Não bloqueia a AS14, porque o critério AS14-05 está cumprido pelo código e verificado por evidência independente. **É condição de entrada da AS15**, que vai emitir cortes H2 a partir de certificados em cache.

## R2.8 Critérios de aceite

| Critério | R1 | R2 | Evidência R2 |
|---|---|---|---|
| AS14-01 VIABLE só com ν=m certificado | UNPROVEN (R09/R10) | **PASS** | §R2.2; micro 11/11; I1 e I3 |
| AS14-02 INFEASIBLE com Hall reproduzível | PASS | **PASS** | auditoria R1 reexecutada (0 falhas); R05-R07 mortos |
| AS14-03 budget/erro resulta em UNKNOWN, nunca prova | FAIL (D1) | **PASS** | §R2.2 (argumento de monotonicidade); I1/I2; N01/N03 mortos; R21/R22 mortos |
| AS14-04 F=V∖R físico | PASS | **PASS** | R14/R15 mortos; I4 |
| AS14-05 chave com identidade e estações canônicas | UNPROVEN (R29) | **PASS** (lacuna N08 registrada) | R25-R29, N04 mortos; I3 |
| AS14-06 só INFEASIBLE certificado entra em B̂ | PASS | **PASS** | R16-R20 mortos; I4 sob relógios variados |
| AS14-07 monotonicidade | UNPROVEN (R30) | **PASS** | R30/R31/N05 mortos |

## R2.9 Pendências bloqueantes

- **Para a AS14:** nenhuma.
- **Para a AS15:**
  1. Fechar os quatro mutantes residuais da AS13 (R3.3). Continuam abertos: nenhum arquivo além de `verify_as13_foundations.py` referencia `H2 excludes physical`, `H2 partial excludes` ou `HL projection identity fails`, e `verify_as13_foundations.py`/`test_as13_foundations.py` não mudaram desde `3baf7b1`.
  2. Adicionar o teste de T no fingerprint (N08).

Não bloqueante (melhorias):
- Testes com relógio de base não nula, que matariam N07.
- Teste com `elapsed == budget` exato, que fixaria a política `>=` (N02).
- Kuhn iterativo ou Hopcroft–Karp para m grande, porque `RecursionError` resulta em UNKNOWN, ou seja, abstenção.
- Fingerprint dentro do budget e calculado uma vez por instância (D2).
- `raise` no lugar dos `assert` de certificação interna.

## R2.10 Decisão

- **AS14: PASS / GO.** As correções da R1 estão verificadas, os contratos matemáticos e temporais valem, o lint próprio está limpo e a proveniência por SHA-256 confere. A pesquisa pode seguir sobre o oráculo AS14 como infraestrutura certificada.
- **AS15: STOP** até os itens 1 e 2 da §R2.9.

Artefatos novos da R2:
- `specs/as-14-oraculo-viabilidade-matching/verifier-r2/review_r2_adversarial.py` (SHA-256 `a2455da5…56d4`)
- `review_r2_mutants.py` (`9ea8bd5d…1b0f`)
- `mutants-r2.json`
- `mutants-r1-rerun-r2.json`
- `results/as14/as14-oracle-audit-verifier-r2.json`

Nenhum commit nem push foi feito. Este parecer não altera `spec.md`, `tasks.md`, `design.md`, nem o código da AS14.
