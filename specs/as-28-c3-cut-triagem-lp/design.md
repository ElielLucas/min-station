# AS28 — Design e garantias

## Reutilização do separador

- `c3_cut_screen_as28.py` usa as rotinas exatas **já existentes** em `cuts.py`; os métodos históricos permanecem sem modificações.
- Cada terminal origina max-flow unitário em rede de nós divididos. Vértices de trânsito não terminais têm capacidade `y*`; destino final é gratuito. O caso `s∈T` tem término sem deslocamento.
- Para cut de suporte `Z`, **um segundo algoritmo BFS** examina o digrafo de alcance, exclui `Z` e comprova que não existe caminho de origem a destinos, ou a versão reversa. Somente então adiciona `sum(y[v] for v in Z) >= 1`.
- O BFS garante validade estrutural para `y` binário em MIN-STATION, mas não torna exaustiva a separação em `y*`.
- Erros de certificado, suporte vazio e divergência numérica encerram o braço com classificação não elegível. Verificações racionais de toda linha não estão incluídas neste piloto e são pendência para qualquer promoção.

## Amostra e orçamento

A seleção de fontes é uma ordenação SHA-256 de `AS28|nome_instancia|lado|terminal`. Até oito origens e oito destinos. A regra não depende dos valores de `y*`; não há aprendizado sobre a amostra. São duas rodadas; orçamento por separação de 12 s, até 16 cortes por rodada, até 32 cortes por braço, 90 s por processo.

A rotina legado de max-flow pode superar o limite de 12 s **dentro de um único max-flow**. O timer local é checado entre mincuts; o processo externo aplica o limite rígido de 90 s. Portanto, o orçamento local de 12 s é um orçamento *soft* e não uma garantia hard para cada chamada. Isso deve ser documentado em qualquer interpretação de tempo.

## Comparação LP

Importa `compile_u` e `prepare_K` das mesmas implementações AS25, com `relax=True` para ambas as armas. O controle `U_K` nunca recebe cortes C3. O candidato `U_K_C3` adiciona exclusivamente linhas unitárias comprovadas pela BFS, com reotimização após cada rodada. O último objetivo LP só é reportado em status `OPTIMAL`. Uma rodada incompleta é explicitamente marcada e impede o gate favorável; a política nunca afirma fechamento global.

A instância é autenticada por hash do arquivo bruto, identidade do grafo, manifesto e partição de desenvolvimento. O pré-registro inclui hash de cada módulo sensível e do plano AS25.1. O runner recusa alterações silenciosas.

## Decisões de risco

1. **C3 e C5 diferentes:** o cut-set individual por origem não incorpora matching global nem substitui C5.
2. **Amostragem de terminais:** ausência de cortes no subconjunto não prova que origens não selecionadas não violem C3.
3. **Censura:** braço interrompido não fornece novo ótimo LP certificado.
4. **Custo:** mede preparação, compilação, solver, mincuts e inserção no prazo total; não subtrai tempos de execuções distintas para declarar economias irreais.
5. **Precedência:** todos os documentos e JSONs de H2/HL/FC-R permanecem intactos.
6. **Limites do ambiente:** sem Gurobi neste ambiente, não há evidência do ganho LP de C3 na campanha real.
