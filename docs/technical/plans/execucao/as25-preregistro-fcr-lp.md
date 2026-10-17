# AS25 — Pré-registro FC-R: piloto LP pareado

**Estado:** PROTOCOLO CONGELADO PARA PRIMEIRA EXECUÇÃO (sem resultados de benchmark nesta entrega).  
**Plano legível por máquina:** [`as25-preregistro-fcr-lp.json`](as25-preregistro-fcr-lp.json). O JSON governa os parâmetros; a implementação rejeita alterações em braços, políticas, amostra e gate.  
**Fonte:** AS23 (certificados racionais); AS24 (`VALIDATED_WITH_MINOR_FINDINGS`, conforme `specs/as-24-fcr-separador-micro/validation.md`); recomendações científicas do parecer Astra.  
**Não autoriza MIP nem avaliação reservada.**

## Pergunta e comparadores

Os quatro braços LP primários são `U` (COMP), `U_K` (COMP+K), `U_FCR` (COMP+FC-R) e `U_K_FCR` (COMP+K+FC-R). A comparação decisória é **`U_K` vs `U_K_FCR`**, incluindo todo o custo de preparação, solução, separação e reotimização. Os outros braços são controles complementares, não substitutos do teste marginal.

## Amostra congelada

| Nome | raw_graph_id | SHA-256 dos bytes da instância |
|---|---|---|
| puc-cc9-2p-seed-r1 | `puc:cc9-2p` | `0312f43552cddc102081d9937465429e29797ddb86cf85a6871752d50aeec88c` |
| puc-bip42p-regiao-f2 | `puc:bip42p` | `d7c53596522401d4071563d5007d9c8647ee0d37c893426b5ab3b1d65d97743a` |
| pucn-cc3-10n-seed-r1 | `pucn:cc3-10n` | `9123c0e46228c22ba586bb7f730757a7fa2c4b0f815b54afba59f54a3bc8b431` |
| mapf-room-32-32-4-m10-f8 | `mapf:map:raw-data/mapf/maps/room-32-32-4.map` | `78be3e1261f31f4e583d0808bdfc9c93d9c9eb335d86d13b059ce428af5f303f` |
| vienna-I056-regiao-f4 | `vienna:I056` | `645da5115a0eeaa6fba9eeae9f4942aebecfa66c4bcbc7aaec2bd0c994eb0ccc` |
| puc-w3c571-seed-r1 | `puc:w3c571` | `e85ced7daef779e6e88f302ee9d80a467129f448a7ac5c6ce465d64b963300fd` |

A fonte operacional é exatamente o plano AS16 identificado pelo SHA-256 no JSON. O runner revalida também manifests, partição desenvolvimento e arquivos físicos pelo protocolo AS16. Não há busca de instâncias alternativas ou tuning pós-hoc.

## Orçamento e política

- **90 s de parede por braço**, incluindo o processo, carga, K para todos os braços, construção LP, Gurobi, construção do índice regional, separação FC-R e reotimização. Worker morto ao alcançar o prazo; resultados sem status OPTIMAL são censurados.
- Gurobi igual ao AS16: `Threads=4`, `Seed=42`, `Method=1`, `MemLimitGiB=16`, `NumericFocus=1`, `FeasibilityTol=1e-6`, `OptimalityTol=1e-6`, `Presolve=-1`.
- Máximo de `1_000_000` variáveis, `12` regiões maiores escolhidas pela mesma política determinística da AS24, `6` rodadas de separação/reotimização, `32` cortes por rodada, `128` no total, tolerância de violação `1e-6`, separação limitada a `12 s` por rodada e reserva de `2 s` para a reotimização.
- **Cobertura declarada:** todas as regiões unitárias de excesso estrito em cada rodada *somente se não censuradas*, mais uma lista fixa e limitada de regiões maiores selecionadas heuristicamente. Não se alega separação global sobre todos os L.
- A escolha de seis rodadas foi feita **antes de qualquer benchmark AS25**, após um microteste sintético que revelou múltiplos pontos ótimos alternativos: duas rodadas não melhoravam o bound, enquanto seis rodadas o elevaram. O orçamento de 90 s continua absoluto e censura braços que não terminarem.
- A AS25 usa indexação das fronteiras de H para tornar a avaliação de candidatas eficiente; o corte emitido é sempre reconstruído pelo construtor canônico da AS24, com as exclusões obrigatórias de terminais. Testes de equivalência microcaso compararam assinaturas e coeficientes.
- Métricas: status, orçamento, parede total, preparo de K, construção, primeira LP, extração da solução, seleção, separação, reotimização, cortes examinados/violados/adicionados/duplicados, NNZ, variáveis, linhas, memória RSS do subprocesso, completude de varredura e objetivos LP.

## Ablação separada

`--ablation` executa **em outro diretório novo** apenas `U_K_FCR_SINGLETON` (somente regiões unitárias) e `U_K_FCR_HEURISTIC` (unitárias + até 12 regiões maiores). São 12 braços (2 x 6), também com 90 s cada. O gate é sempre `ABLATION_DESCRIPTIVE_ONLY`; seus resultados **não** entram na contagem do gate principal. Não comparar custo da ablação a um braço executado em outra campanha como evidência controlada de ganho temporal.

## Gate e censura

Para `GO_CANDIDATE_REVIEW` exige-se **toda a amostra de seis grafos brutos independentes**, todos os 24 braços com LP ótimo, sem incompletude da varredura unitária nem da lista de regiões maiores selecionadas, e melhora relativa **≥1%** de `U_K_FCR` sobre `U_K`, com parede total **≤2×** a de `U_K`, em **pelo menos dois grafos brutos independentes**.

- Braços não ótimos, amostra parcial, erro, limite de tempo, limite de cortes atingido, falta de licença ou varredura parcial resultam em `INVESTIGATE`, sem concluir ausência de ganho.
- Sem caso positivo suficiente após campanha completa e comparável, usar `STOP` **para esta política experimental**, não prova de redundância global de FC-R.
- Mudanças de fluxo sem aumento do objetivo LP têm ganho de bound zero. Se objetivo basal é zero, ganho percentual é indefinido e não conta como sinal positivo.
- `GO_CANDIDATE_REVIEW` exige nova decisão humana/revisão científica para AS26; **nunca** autoriza MIP automaticamente.

## Proveniência e execução

Exigir diretório de saída novo (`open('x')` para JSON) e incluir hashes do pré-registro, do código relevante, dos dados e do `source_commit` observado. Uma pasta de dry-run **não é** resultado LP. Cabe ao pesquisador conferir que os arquivos implementados foram commitados antes de executar a campanha e preservar o JSON congelado. Diferenças nos artefatos exigem nova rodada identificada, sem sobrescrever a original.

```bash
poetry run python experiments/cuts/run_fcr_lp_as25.py --output-dir /tmp/as25-dry --dry-run
poetry run python experiments/cuts/run_fcr_lp_as25.py --output-dir results/benchmark/as25-fcr-lp-001
poetry run python experiments/cuts/run_fcr_lp_as25.py --output-dir results/benchmark/as25-fcr-ablation-001 --ablation
```
