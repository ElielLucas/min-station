# AS23 — Relatório da reprodução matemática de FC-R

**Resultado científico do verificador local: `EXACT_CERTIFIED` na testemunha sintética.** A prova de validade de FC-R/FC-R-T está documentada em [`../tecnico/as23-prova-fcr.md`](../tecnico/as23-prova-fcr.md). **Revisão matemática externa:** parecer do Claude Code informado pelo pesquisador como `CHANGES_REQUIRED (leve)`, sem bloqueios matemáticos; as correções obrigatórias de teste foram aplicadas e verificadas nesta entrega. **Gate técnico AS23: `VALIDATED` (PASS)**; a atualização do `source_commit` para o commit final exige executar novamente o verificador após o commit no repositório local.

## Escopo executado

- Fonte: parecer Astra `parecer-astra-fcr-pos-as22.md` (declara leitura da branch `novos_testes` no commit `285261b`). Entrada para esta correção: snapshot `min-station(20261016-225034).zip`. O `.git/HEAD` do arquivo aponta para `56b8957485c673fb08460ef836257773fb67933f`, **não necessariamente para os arquivos da AS23**, pois parte deles ainda não foi commitada no snapshot. O campo `source_commit` do verificador captura o HEAD efetivamente disponível e `source_commit_note` explicita a presença de alterações; `source_sha256` identifica o código exato. Após o commit local, executar novamente o verificador e registrar o novo SHA. Nenhum SHA de commit futuro foi inventado.
- Script: `experiments/cuts/verify_fcr_witness.py`, que reconstrói o grafo, chama **os geradores reais** `prepare_K` e `generate_C6`, compila `compile_u` e representa as linhas C8 documentadas. Apenas **quatro linhas FC-R explicitamente definidas** são estudadas. Não há separador geral nem alterações ao baseline.
- Método: SciPy/HiGHS para **propor** pontos primais e duais, `Fraction.limit_denominator` para reconstruí-los e verificações racionais **exatas** em todas as linhas, cotas e equações de dualidade. `recheck_saved` valida cada certificado a partir do JSON sem chamar solver. Se racionalização falhar, o script aborta e **não** atribui sucesso.
- Validação física: `independent_validator.viavel` na instalação vazia, em **cada uma das 24 instalações únicas** e no par `{x11,x21}`. Isso comprova `OPT=2` na instância **sob o validador físico já adotado no projeto**, não em benchmarks.

## Caracterização reconstituída

| Elemento | Evidência |
|---|---:|
| Vértices | 24 |
| Arestas físicas não direcionadas | 48 |
| Arcos de alcance, `r=1` | 96 |
| Origens / destinos | 6 / 6 |
| Cortes K de `prepare_K` | 4 |
| Linhas do COMP+K compilado | 76 |
| Cortes C6 do gerador do repositório | 1, `δ=2`, sem truncamento |
| C8 individuais aplicáveis | 36 |
| FC-R unitárias escolhidas | 4 |

As quatro coberturas K são as mesmas descritas no parecer; seus conjuntos completos são serializados no JSON. Nenhum RHS ou objetivo do Astra é injetado na compilação.

## Certificados exatos dos LPs

| Formulação | Objetivo primal exato | Objetivo dual exato | Status |
|---|---:|---:|---|
| COMP+K | `1` | `1` | Certificado |
| COMP+K+4 FC-R | `7/5` | `7/5` | Certificado |
| COMP+K+C8 (36) | `11/10` | `11/10` | Certificado |
| COMP+K+C8+4 FC-R | `7/5` | `7/5` | Certificado |
| COMP+K+C6+C8 | `47/30` | `47/30` | Certificado |
| COMP+K+C6+C8+4 FC-R | `17/10` | `17/10` | Certificado |

A comparação entre modelos se mantém em termos exatos:

\[
\frac75 - 1=\frac25>0,\qquad
\frac75-\frac{11}{10}=\frac3{10}>0,\qquad
\frac{17}{10}-\frac{47}{30}=\frac{2}{15}>0.
\]

**Observação nova:** o parecer fornecia um ponto de `17/15` compatível com COMP+K+C8; a otimização independente achou o **ótimo `11/10`** para essa formulação, menor que `17/15`. A testemunha explícita de `17/15` também foi reconstruída sem otimizador: seus dois primeiros FC-R têm déficit `1/3`, e o C6 existente a elimina. Isso reproduz a afirmação de existência do ponto, mas não confunde esse ponto com o ótimo de COMP+K+C8.

## Validade, segurança e casos adversariais

- `fcr_region_row` rejeita `Q` com destinos na versão origem, origens na versão destino, membros de `L`, vértices inexistentes ou sem arco de fronteira. O teste contém **`L=('d1',), Q=('e1',)` na versão destino**, detectando a mutação `noSexcl`, e um contraexemplo físico mínimo `e1→d1` com `y_e1=0`. O par simétrico de origem continua coberto.
- A prova inclui explicitamente a versão FC-R-T e não assume fluxos sem circulação. O teste combina terminais com interseção e fluxo cíclico admissível em COMP.
- A regra de seleção ótima de `Q` para `L` fixa foi comparada com todos os subconjuntos da fronteira nos testes de origem e destino, incluindo empates e excesso regional 2. Regiões equilibradas são rejeitadas.
- Certificados com objetivo adulterado, multiplicador de sinal incorreto ou variável fora da cota são rejeitados pelo rechecker exato. O teste também **lê o JSON salvo em disco**, confere os hashes do código e reexecuta `recheck_saved` sobre **seis modelos**, sem solver.
- Nenhuma conclusão de separação **global de L**, novidade acadêmica, ganho computacional real ou melhoria MIP é emitida nesta fase.

## Verificação bibliográfica

A revisão bibliográfica documentada em `as23-prova-fcr.md` conferiu obras de Padberg–Van Roy–Wolsey (1985), Van Roy–Wolsey (1985), Rardin–Wolsey (1993) e Atamtürk (2001), por fontes editoriais e seus metadados. Elas estabelecem precedentes para cortes de fixed-charge flow. Uma **equivalência formal entre FC-R e uma família específica da literatura não foi demonstrada**, e não se reivindica originalidade.

## Arquivos verificáveis e comandos

- `results/benchmark/as23-fcr-witness-001.json`: todos os pontos primais, multiplicadores duais, contagens, conjuntos K e hashes (JSON determinístico); resultado `EXACT_CERTIFIED` significa prova sintética com Fraction, **não** campanha de benchmark.
- `experiments/cuts/test_as23_fcr_witness.py` e `test_as23_fcr_q_selection.py`: regressão ligada aos critérios de aceite.

```bash
python experiments/cuts/verify_fcr_witness.py --output results/benchmark/as23-fcr-witness-001.json
poetry run python -m unittest discover -s experiments/cuts -p 'test_*.py' -q
python3 .claude/skills/tlc-spec-driven/scripts/validate_spec.py specs/as-23-fcr-revisao-matematica/spec.md
python3 .claude/skills/tlc-spec-driven/scripts/validate_tasks.py specs/as-23-fcr-revisao-matematica/tasks.md
```

## Parecer externo recebido e correções de fechamento

O pesquisador informou uma revisão independente realizada pelo **Claude Code**: `CHANGES_REQUIRED (leve)`, sem bloqueadores matemáticos. Segundo a síntese fornecida, houve reprodução independente em Gurobi, certificado dual próprio, cerca de 473 mil casos adversariais e confirmação do ótimo inteiro 2. **A íntegra e os logs dessa execução externa não foram disponibilizados neste pacote**; esses quantitativos são atribuídos ao parecer relatado, não a testes executados por este verificador.

Correções realizadas e reproduzidas localmente:

1. **MAJOR:** o teste FC-R-T passou a rejeitar `Q=('e1',)` para `L=('d1',)` e construiu um contraexemplo inteiro físico sem estação em `e1`. Detecta a exclusão obrigatória de `S`.
2. **MINOR:** a subfamília com excesso regional `d_L=2`, tanto origem quanto destino, é confrontada com todas as escolhas de `Q` no teste de minimização existente.
3. **MINOR:** o JSON persistido é rechecado por testes em seis modelos, inclusive hashes e certificado primal/dual exato.
4. **MINOR:** acrescentado o modelo `COMP_K_C8_FCR` com ótimo `7/5` e comparação marginal exata frente a `COMP_K_C8` (`11/10`).
5. **MINOR:** terminologia de ganho alterada de “strict complementarity” para **fortalecimento LP marginal estrito**; documentos e proveniência alinhados com os resultados efetivos.

Os **dez itens MINOR não foram fornecidos individualmente**, portanto esta revisão não certifica que cada observação opcional do Claude foi resolvida; o registro integral continua sendo necessário para rastreabilidade fina. A revisão matemático-científica não precisa ser repetida segundo o resumo fornecido, mas isso não substitui a conferência do conjunto completo de achados menores.

## Critérios e gate

| Critério | Resultado |
|---|---|
| Provas FC-R e FC-R-T | PASS, demonstração completa e condições de Q |
| Seleção exata em Q com L fixo | PASS, dedução e enumeração independente em microcasos |
| Grafo, K, C6, C8 físicos | PASS, geradores e validador do projeto |
| Pontos e limites exatos | PASS, certificados primal/dual em Fraction |
| Comparação além de C6+C8 | PASS, ganho racional estrito |
| Precedentes bibliográficos | PASS para posicionamento; equivalência exata não demonstrada |
| Revisão matemática por verificador diferente (Claude Code) | **PASS segundo parecer resumido fornecido pelo pesquisador**; relatório integral não anexado |

**Decisão:** **AS23 PASS / `VALIDATED` no escopo matemático e de testes obrigatórios** após corrigir o achado MAJOR e reproduzir as verificações locais. **AS24 fica liberável após commit das correções e regeneração do JSON com `source_commit` do repositório local.** Os achados MINOR cuja descrição não foi compartilhada não são declarados encerrados. Não há autorização de execução MIP ou conclusão sobre benchmarks reais.
