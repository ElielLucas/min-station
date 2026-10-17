# AS28 — Triagem LP restrita de C3-cut por origem/destino

**Estado (pós-campanha, 17/10/2026):** EXECUTADA; `NO_SIGNAL_BOUNDED_POLICY` (4 pares ótimos, 2 censurados); parecer independente/decisão final do pesquisador pendentes. Histórico do desenho pré-campanha preservado nas seções seguintes.
**Natureza:** diagnóstico de viabilidade científica, não promoção de C3-cut nem desbloqueio de AS26.
**Baseline:** COMP+K original no problema de Das; mesmas seis instâncias de desenvolvimento de AS25/AS25.1.
**Pré-registro:** `docs/technical/plans/execucao/as28-preregistro-c3-lp.json`.

## Contexto

Após AS25.1, FC-R deixou de ser linha principal e AS26 está bloqueada. O parecer subsequente do Claude Opus recomendou não seguir com disjunções globais e fazer avaliação de potencial de C3-cut. O projeto **já implementava** `check_C3_violations` e sua versão simétrica em `experiments/cuts/cuts.py` (§5.3 de `direcoes-pli-min-station.md`). O que falta é mensurar sua contribuição LP incremental sobre COMP+K nas instâncias principais de Das, com custo completo.

C3-cut é uma desigualdade de conectividade individual. Para cada origem `s∉T`, qualquer `Z ⊆ V\{s}` que intercepte todos os caminhos de `s` a algum destino em `H` define `y(Z) ≥ 1`; o destino tem versão reversa. O separador legado usa max-flow de capacidade `y*` em vértices intermediários; não confundir esta família com a formulação F-C3 de trios nem com cortes C5 de conectividade global.

## Objetivo

Decidir se uma **política pequena e explícita de separação C3**, sem reconstrução de infraestrutura complexa, dá sinal robusto de ganho LP sobre COMP+K. **Ausência de sinal não demonstra redundância de toda a família C3.**

## Escopo e requisitos

- AS28-01: **Não modificar** COMP, K, `cuts.py`, AS24, AS25 ou AS25.1.
- AS28-02: reutilizar `_build_flow_net`, `_edmonds_karp`, `_reachable_set` existentes para **no máximo oito origens e oito destinos** por instância, selecionados por hash estável do nome da instância e ID do terminal, sem usar o ponto LP para escolher terminais.
- AS28-03: usar **duas rodadas** no máximo, **16 cortes/rodada**, **32 no total**, separação de até **12 s/rodada** e orçamento **90 s/arm**, incluindo preparação e solução LP; proteger contra laço interno demorado usando hard timeout por processo.
- AS28-04: verificar **independentemente do fluxo residual** que o conjunto `Z` de cada corte separa a origem de todos os destinos (ou o destino das origens no grafo reverso); para `S∩T`, permitir permanência de zero passos.
- AS28-05: registrar estados `EMPTY_CUT`, `CERTIFICATE_FAILED`, `NUMERICAL_AMBIGUITY` como **inseguros**, abstendo-se de adicionar novos cortes.
- AS28-06: parear duas formulações LP: `U_K` e `U_K_C3`. Somente `OPTIMAL` dos dois braços forma comparação de limite LP; censuras são excluídas da comparação numérica, mas reportadas como cobertura insuficiente.
- AS28-07: pré-registro em JSON, verificação de hash dos arquivos de origem, importação dos casos de desenvolvimento de AS25.1, append-only na saída e classificação sem autorização MIP.
- AS28-08: testar contra o validador físico independente por enumeração em microinstâncias com `S∩T` e `r∈{1,2}`; não usar Gurobi como oráculo de validade das linhas.
- AS28-09: execução real **somente depois do commit do código e do pré-registro**; não há autorização de campanha ampliada.

## Gate limitado

Critério prospectivo de sinal favorável: `gainLP ≥ 1%` **e** razão de tempo `≤ 2× COMP+K` em pelo menos **dois grafos brutos independentes**, com ambos os LPs certificados ótimos e **todas as fontes selecionadas completamente avaliadas nas rodadas efetivas**, sem teto de corte atingido. Resultado favorável autoriza **apenas revisão independente e eventual planejamento de separador**; nunca MIP automático.

Classificações:

- `PROMISING_FOR_INDEPENDENT_REVIEW`: sinal favorável segundo os critérios acima.
- `NO_SIGNAL_BOUNDED_POLICY`: ao menos 4 pares ótimos, nenhum com ganho ≥ 1%; motivo para parar **a política amostrada**, não prova de fraqueza global de C3.
- `INCONCLUSIVE_OR_COSTLY`: censuras ou custo/ganho inconclusivos.
- `NOT_EXECUTED_DRY_RUN`: somente validação estrutural; nenhuma inferência experimental.

## Exclusões

Não haverá nova família, MIP, root-node, callbacks, uso da partição reservada, mudança de parâmetros após ver resultados, afirmação de fecho global C3, nem comparação com F-C3.

## Aceite desta entrega

- [x] Auditoria básica de validade e microtestes executados.
- [x] Runner LP com isolamento por processo e `--dry-run`.
- [x] Analisador e pré-registro congelado.
- [x] Dry-run: 6 casos × 2 braços = 12 registros `NOT_RUN`.
- [x] Campanha LP real com Gurobi executada: 12 braços, 4 pares ótimos, 2 pares censurados; dados em `results/benchmark/as28-c3-lp-001/`.
- [ ] Parecer independente dos resultados e decisão humana do próximo gate (recomendação STOP documentada em `docs/technical/reference/experimentos/as28-resultado-lp-c3.md`).

## Evidência pós-execução (não altera gate)

Ver [`as28-resultado-lp-c3.md`](../../docs/technical/reference/experimentos/as28-resultado-lp-c3.md) para resultados, censuras, comparação com LB* e recomendação de encerrar **a política limitada** de C3. Não executar campanha ampliada ou AS26 automaticamente.
