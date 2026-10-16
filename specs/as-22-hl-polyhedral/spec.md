# AS22 — Separação poliédrica HL de coeficientes gerais — Specification

**Status:** implementação, validações sintéticas e campanha Gurobi real concluídas; gate `INVESTIGATE`; **estratégia HL local não promovida**. Resultado em `docs/technical/reference/experimentos/as22-resultado-lp-hl.md`.  
**Branch de referência:** `novos_testes`.  
**Dependências:** COMP+K, oráculo físico AS14, AS19–AS21, pré-registro AS16. **Não depende de GO de H2 nem autoriza MIP.**

## Objetivo

Verificar se desigualdades HL não restritas à cardinalidade podem eliminar pontos LP fracionários de COMP+K. A AS21 identificou 16 suportes avaliados em quatro casos ótimos, sem cortes e com dois casos censurados. A AS22 foi executada posteriormente e encontrou 16 projeções triviais, registradas no relatório AS22 atualizado. Isso não testa a família HL geral.

## Modelo matemático e prova

Sejam `R ⊆ V` pequeno, `F = V \ R` o conjunto de estações **permitidas fora de R** e `Φ_R = {1_A ∈ {0,1}^R : VIABLE(F ∪ A)}`. A viabilidade física é monotônica na inclusão de estações permitidas (o oráculo AS14 é baseado em caminhos de alcance e matching). Toda solução inteira globalmente viável, quando projetada em R, pertence a `Φ_R`: permitir todas as estações fora de R só pode preservar a viabilidade.

Para qualquer `α ∈ Q_+^R`, é válida a desigualdade:

`Σ_{v∈R} α_v y_v ≥ β(α)`, onde `β(α) = min_{A : 1_A∈Φ_R} Σ_{v∈A} α_v`.

Para descobrir um corte, resolver o LP auxiliar de separação numérico:

`max t` sujeito a `Σ α_v(z_v - y*_v) ≥ t` para todo `z∈Φ_R`, `Σ α_v = 1`, `α_v ≥ 0`, `t ≥ 0`.

O LP auxiliar **apenas propõe** α. Os coeficientes são racionalizados com denominador limitado e **β é recalculado exatamente** com `fractions.Fraction` sobre todos os padrões certificados viáveis. Somente se `β > 0` e `β − α·y* > ε` uma desigualdade será emitida. Nunca usar β numérico do LP como prova. Como `Φ_R` é monotônico para cima, normais não negativas são uma escolha suficiente para detectar separação inferior dentro do cubo unitário, mas este piloto não afirma enumerar facetas nem otimizar todas as famílias de cortes.

### Certificação física e abstenção

- Classificar **todo** padrão de R em ordem de cardinalidade, consultando `VIABLE`/`INFEASIBLE` com prova física AS14.
- É permitido inferir `VIABLE` para um padrão se um subpadrão já recebeu certificado `VIABLE`; a inferência registra qual certificado originou a monotonicidade.
- `UNKNOWN`, prazo, limite de padrões/chamadas, suporte grande ou ausência de padrões viáveis ⇒ **não emitir corte naquele suporte** e registrar causa.
- A classificação integral (direta ou inferida) entra no hash do certificado e na evidência serializada; hashes e coeficientes não dependem de duração ou ordem de entrada do suporte.
- Uma projeção heurística de K grande **não** recebe validade de K; somente o oráculo físico pode certificar a desigualdade sobre o suporte projetado.

## Protocolo LP pré-registrado

| Item | Política |
|---|---|
| Fonte | Seis grafos de desenvolvimento idênticos aos da AS16, hashes/identidades congelados |
| Braços | `U_K` vs `U_K_HL`, compilação de COMP+K original |
| Solver | Parâmetros Gurobi AS16, LP relaxado, sem MIP |
| Orçamento | 90 s totais por braço, incluindo preparação, certificação e reotimização |
| Suportes | até 8 vértices; até 4 por caso; até 2 vagas reservadas para interações K distintas |
| Busca de candidatos | no máximo 48 sementes K e 64 hipóteses de pares; projeções são heurísticas |
| Certificação | até 256 padrões/suporte; 480 chamadas; 24 s globais; 8 s/suporte |
| Numerics | denominadores até 128; violação estrita maior que `1e-6` |
| Cortes incorporados | até 3 por braço |
| Gate exploratório | ganho ≥1% e custo ≤2× em pelo menos 2 grafos brutos independentes com campanha completa ⇒ `GO_CANDIDATE_REVIEW`, **não autorização MIP** |
| Persistência | saídas inéditas `manifest.json`, `rows.json`, `analysis.json`; experimentos históricos imutáveis |

### Interpretação de resultados

- `CUTS_FOUND` = desigualdade válida certificada; requer prova de melhora no LP para **ganho**.
- `NO_CUTS` = nenhum corte violado **nesses suportes**; não implica dominância global de K.
- `PARTIAL_BUDGET`, sem suporte elegível, Gurobi censurado, `UNKNOWN` ⇒ inconclusivo.
- `INVESTIGATE` não é sucesso ou fracasso científico universal; objetivo é reconhecer capacidade/custo de separação.

## Critérios verificáveis

1. AS22-01: plano congela os seis grafos, SHA AS16/AS21, parâmetros do solver e limites AS22.
2. AS22-02: suporte selecionado deterministicamente; pelo menos uma hipótese de interação se existir, observadas vagas disponíveis.
3. AS22-03: classificação completa da projeção física antes de qualquer corte; apenas `VIABLE` por monotonicidade pode ser inferido.
4. AS22-04: cortes racionais não negativos; β calculado exatamente, validade garantida no conjunto `Φ_R`.
5. AS22-05: `UNKNOWN`, caps e timeouts abstêm sem qualquer corte indevidamente emitido.
6. AS22-06: testemunha física não uniforme `a OR (b ∧ c)` corta ponto com massa ≥ mínimo de cardinalidade; K4 volta a elevar COMP+K de 2 a 3.
7. AS22-07: runner pareado com 90 s/arm e saídas append-only, sem alterar COMP/K/H2/AS19–AS21.
8. AS22-08: 12 registros no dry-run para as seis instâncias; nenhum resultado real artificial atribuído ao Gurobi.
9. AS22-09: revisão independente exigida antes de promoção científica ou autorização MIP.

## Fora de escopo

Cortes com coeficientes negativos, suporte grande arbitrário, separação global exata, cortes fracionários gerais além da projeção monotônica local, avaliação reservada, MIP, alteração de resultados anteriores. **O limite de tamanho é computacional, não uma limitação teórica da definição HL.**

## Fechamento experimental posterior

Os arquivos `results/benchmark/as22-hl-lp-001/{manifest,rows,analysis}.json` contêm 12 braços de seis casos, com quatro pares ótimos e dois censurados, sem corte HL certificado/adicionado e sem ganho LP observado. Em 16 suportes, `VIABLE(V\R)` comprovou projeções cúbicas completas pela monotonicidade. O gate automático `INVESTIGATE` permanece, mas a interpretação científica é **interromper a linha de HL local AS20–AS22** e estudar FC-R somente após prova independente AS23. Ver [parecer Astra](../../docs/technical/reference/tecnico/parecer-astra-fcr-pos-as22.md).
