# AS21 — Certificação HL por camadas e seleção estrutural — Specification

**Status:** IMPLEMENTAÇÃO CONCLUÍDA; CAMPANHA GUROBI REAL PENDENTE  
**Branch de referência:** `novos_testes`  
**Origem:** AS20 teve seis execuções e 12 braços, mas nenhum corte HL. A execução AS20 permaneceu `INVESTIGATE`: quatro pares ótimos sem ganho, um par com baseline censurado e um par inteiramente censurado; houve `PARTIAL_BUDGET`, ausência de suporte elegível e custo elevado.  
**Dependências:** COMP+K, oráculo físico AS14, infraestrutura AS20, pré-registro AS16. **Independente do gate H2.**

## Objetivo

Testar se uma **certificação de cardinalidade por camadas inferiores**, com suportes estruturais candidatos, consegue encontrar cortes HL válidos e marginais sobre COMP+K com menor custo que a enumeração integral AS20. Separar três questões: (i) correção da desigualdade, (ii) sucesso da busca sob os limites, (iii) ganho LP em instâncias de desenvolvimento.

## Fundamento matemático — segurança do corte

Para suporte finito `R ⊆ V`, considere seu complemento `F = V \ R` e `viável(C)` representando uma solução física para o conjunto de estações disponíveis `C`. No modelo de recarga, **acrescentar estações permitidas não pode eliminar caminhos ou emparelhamentos alcançáveis**: `C ⊆ D` e `viável(C)` implica `viável(D)`.

Para qualquer inteiro `1 ≤ k ≤ |R|`, se o oráculo físico provar

`∀ A ⊆ R com |A| < k: NÃO viável(F ∪ A)`, então é válida:

`Σ_{v ∈ R} y_v ≥ k`.

**Prova:** se uma solução inteira fisicamente viável selecionasse menos de `k` vértices em `R`, seu conjunto global `C` estaria contido em `F ∪ (C ∩ R)`. Pela monotonicidade, `F ∪ (C ∩ R)` seria viável, contradizendo a prova física para esse padrão. Logo, toda solução inteira viável seleciona pelo menos `k` vértices em `R`.

Esse argumento **não exige** classificar os padrões de cardinalidade `≥ k` e **não prova** que `k` seja o mínimo exato ou que o corte seja uma faceta de `conv(Φ_R)`. Mantemos somente `α_v = 1`. A validade depende do contrato do oráculo físico para o grafo não direcionado, arestas unitárias e matching `S→T`.

## Estratégia pré-registrada

- **Entradas:** exatamente as seis instâncias de desenvolvimento AS16 usadas na AS20 (hashes e identidade de grafo congelados), sem avaliação nem MIP.
- **Braços:** `U_K` e `U_K_HL`; 90 segundos totais por braço, usando os parâmetros Gurobi de AS16 e `compile_u(..., K, relax=True)` inalterado.
- **Suportes:** até 14 vértices, até 4 candidatos; K inteiros, uniões de K, **projeções heurísticas** de K grandes sobrepostos. Projeções não herdam validade da família K; **todo corte precisa de prova física independente**.
- **Orçamento:** até 48 sementes K, 32 propostas por pares, 700 chamadas ao oráculo, 180 padrões por suporte, RHS máximo 3, até 24 s global e 10 s por suporte, até 3 cortes.
- **Certificação:** para ponto LP `y*`, testar unicamente `k = ⌊Σ y*_R + 10⁻⁷⌋ + 1`, quando `1 ≤ k ≤ min(3, |R|)`. Todos os padrões com menos de `k` estações devem ser `INFEASIBLE`, em ordem crescente de cardinalidade. `VIABLE` nesses padrões implica que o RHS proposto não é válido; `UNKNOWN`, deadline ou incompletude ⇒ abstenção.
- **Gate:** ganho ≥1% em pelo menos dois grafos brutos independentes com tempo total até 2× COMP+K gera apenas `GO_CANDIDATE_REVIEW`, condicionado à revisão. Sem candidatos/censuras/oráculo parcial ⇒ `INVESTIGATE`. Nenhuma execução autoriza MIP automaticamente.
- **Rastreabilidade:** `manifest.json`, `rows.json`, `analysis.json` por saída inédita; comparação descritiva com AS20 pode ser gerada em JSON separado. Não sobrescrever AS20 ou AS19.

## Requisitos verificáveis

1. **AS21-01:** O runner valida plano AS16, fontes, hashes, solver e limites antes da campanha real.
2. **AS21-02:** Seleciona suportes deterministicamente, incluindo hipóteses de interações entre K maiores que o teto AS20. Projeções são identificadas como heurísticas, sem validação presumida.
3. **AS21-03:** Emite `Σ y_R ≥ k` apenas após `INFEASIBLE` certificado para *todos* os padrões de cardinalidade menor que `k`.
4. **AS21-04:** `UNKNOWN`, budget/timeout, cap de RHS, tamanho ou padrões não emitem corte; produzem diagnóstico inconclusivo.
5. **AS21-05:** Com suporte K4 e ponto LP COMP+K, reproduz limite LP `2 → 3` e usa 11 consultas, não 16.
6. **AS21-06:** Executa braços sob deadlines idênticos; usa tempo de parede total incluindo custos de preparação, certificação e reotimização.
7. **AS21-07:** Não altera o código matemático de K, COMP, H2 ou a implementação arquivada AS19/AS20.
8. **AS21-08:** Registra resultados com política append-only, censuras e comparação descritiva AS20×AS21; não infere ganhos sem pares ótimos.
9. **AS21-09:** Finaliza a triagem real somente após Gurobi no ambiente do pesquisador e revisão independente; evidência sintética é insuficiente para promoção científica.

## Fora de escopo

Desigualdades HL de coeficientes gerais, descrição de `conv(Φ_R)` completa, facetas, novos cortes K, otimização MIP, avaliação, alteração dos resultados experimentais AS16–AS20, conclusões universais de redundância de HL.

## Situação

**Implementação e testes:** concluídos. **Campanha AS21 com Gurobi:** pendente. **Decisão de pesquisa:** HL continua em investigação, sem promoção automática.
