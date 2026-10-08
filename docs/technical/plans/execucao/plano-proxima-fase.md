# Plano da próxima fase — MIN-STATION depois dos Blocos 1–4 (programa de pesquisa)

**Data:** 2026-10-03. **Base:** commit `9b93650`.

**Decisões do usuário que orientam este plano:**
- não escrever artigo agora, nem depois de um único teste;
- continuar a pesquisa até obter um **avanço considerável**;
- incluir nos próximos testes as duas formulações alternativas, para ver se superam o que existe hoje.

**O que a aprovação de 2026-10-03 fez:**
- este documento foi salvo como `docs/technical/plans/execucao/plano-proxima-fase.md`;
- os três arquivos novos foram renomeados conforme a §6.4:
  `formulacao-fcc-configuracoes-conectadas.md`,
  `formulacao-fc3-consistencia-trios.md`,
  `pereira-ravelo-2026-aranhas.md`.

O restante do saneamento de R1 (cabeçalhos de estado, `open-questions.md`,
`source-map.md`, planos históricos e ponteiro no backlog) acompanha essa
renomeação. Nenhum experimento, implementação ou commit fazia parte da
aprovação. Cada tarefa da §11 é aprovada depois, uma a uma.

**Legenda.**
- **[Fato]**: verificado nesta sessão.
- **[Conferido]**: argumento matemático refeito nesta análise. Ainda não está escrito no repositório.
- **[Evid.]**: resultado medido; vem acompanhado do grau de protocolo.
- **[Hipótese]**: ainda não testado.
- **[Sugestão]**: proposta de planejamento.

---

## 1. Executive Summary

Os Blocos 1–4 deixaram:
- a base correta e provada;
- a infraestrutura experimental confiável;
- uma bateria estrutural feita sob protocolo;
- um posicionamento honesto frente ao IJCAI-26.

**Falta um avanço de método.** Nas 31 instâncias D/A o gap residual vai de 10% a 44%, e `hc9u`
está aberta desde o E3 (OPT ∈ [32, 38]).

**O mecanismo de falha já está medido.** No E12, o limite inferior (LB) do CBI ficou parado no
valor do núcleo, depois de 124 a 1334 iterações. Em `cc9-2p` foram 860 iterações em 27, enquanto o
COMP provou 30. O núcleo de cobertura tem um **platô de ótimos inviáveis**: ele não enxerga a
**compatibilidade coletiva** — estações encadeadas e conectadas no grafo de alcance, atribuição
balanceada.

**As duas formulações novas atacam exatamente esse ponto, por isso entram como linha principal.**
- **F-CC** (configurações conectadas) é exata; a exatidão foi conferida nesta análise. Ela exige que
  as estações usadas por um grupo de robôs formem uma componente conexa em `G^r`.
- **F-C3** acrescenta consistência entre trios de atribuições.

O ganho é **de relaxação, alegado e não medido**. Pelo argumento da §6.2, a F-CC deve ter o mesmo
gap de cobertura do núcleo em SC. O ganho, se houver, aparece onde há compatibilidade (`Γ > 0`).

Pereira & Ravelo (aranhas) entram como **linha de suporte**. O algoritmo é uma fonte de ótimos
exatos em `n` grande, útil para validar as formulações. A prova está em esboço e tem casos que
precisam de teste (§5).

**Programa:**
1. Fundação: linha de base conforme protocolo.
2. Diagnóstico: onde está o gap, e anatomia do platô.
3. Teste barato e decisivo das formulações em instâncias pequenas — começa já, em paralelo.
4. Método escolhido por portões.
5. Confirmação do avanço.

---

## 2. Definição de "avanço considerável" (pré-registrada; confirmar com o usuário)

**[Sugestão]** O programa termina com sucesso quando pelo menos um critério abaixo vale na partição
de avaliação. Condições comuns a todos: mesmo `WorkLimit` em todos os braços, 3 sementes, sem MIP
start, protocolo pareado.

| # | Critério |
|---|---|
| AV-1 | Provar o ótimo de **≥ 3 instâncias D/A** que nenhum braço de referência prova, em ≥ 2 famílias |
| AV-2 | Reduzir a **mediana do gap certificado** `(UB−LB)/UB` das D/A em **≥ 25% relativos** contra a melhor referência, em ≥ 2 famílias, reproduzindo em 3 sementes |
| AV-3 | Formulação ou família de desigualdades **provada** que reduz `Γ` (§7) em **≥ 50%** nas amostras certificadas com `Γ > 0`, em ≥ 2 níveis de tamanho |
| AV-4 | Fechar `hc9u` ou estreitar `[32, 38]` em ≥ 3 unidades |

As referências são o melhor LB e o melhor UB de qualquer braço da linha de base (base, COMP,
núcleo), obtidos na Fase 0. Os limiares podem ser ajustados até a Fase 0 terminar, nunca depois de
ver os resultados de métodos.

---

## 3. What We Now Know (síntese dos Blocos 1–4)

**Corretude.**
- **[Fato]** A base (variante U) é equivalente ao problema de Das, inclusive com `S∩T` e
  permanência (§5.5 de `validacao-formulacao-base.md`).
- O oráculo foi corrigido.
- O validador independente cobre `n ≤ 5`; a regressão de terminais está limpa.
- **Aberto:** não há validação contra ótimos certificados de forma independente em `n` grande. Isso
  passa a ser crítico com formulações novas (S1, §5).

**Confiabilidade.**
- **[Fato]** Já existem T6 (determinismo), T7 (`WorkLimit`), T9 (`NodeCount` e incumbentes) e T10
  (protocolo pareado).
- A partição continua com 11 vazamentos.
- E9–E14 são pré-protocolo: orientam a pesquisa, mas não servem de linha de base.

**Pesquisa.**

| Linha | Estado |
|---|---|
| Núcleo C1+C2+C4 | Forte onde a cobertura domina: prova `OPT = k` na raiz em SC-GF2 com `k = 8, 9`. Fraco onde há compatibilidade: MAPF em 0,87 do COMP; 4 de 8 instâncias F abaixo do ótimo (maze, pace-001, pucn-cc6-2n, lin03); `cc9-2p` dá 27 contra LB 30 |
| CBI / `𝒵` por ponto | Negativo, com mecanismo conhecido: o platô |
| C6 | Válido, efeito nulo |
| BP | Descartada como estresse; o lado "não" tem `Γ = 1` certificado |
| HB | Descartada |
| SC | Promovida; regime `Γ = 0` |
| TR | Validada: o platô em miniatura (k^R ótimos do núcleo, k viáveis) |
| All-V por origem | Ganho de LP que não paga o custo `m·|A_r|` |
| Lagrangeana, Benders clássico | ≤ `z_LP`, por prova |

**Posicionamento.**
- Já publicado (IJCAI-26): `G^r`, matching, as reduções BP e SC, FPT e árvores.
- Espaço livre: o lado **poliédrico e computacional**, onde F-CC, F-C3 e as desigualdades de
  compatibilidade se encaixam.

---

## 4. What Is No Longer Worth Pursuing

| Linha | Decisão | Motivo |
|---|---|---|
| CBI / BC-y com cortes `𝒵` de **ponto único** | Encerrada | O platô do E12 mostra o motivo; mais tempo ou mais sementes não mudam o mecanismo |
| Lagrangeana, Benders clássico | Encerradas | ≤ `z_LP`, por prova |
| C5 por limiar | Encerrada | É o mesmo mecanismo do CBI |
| Reverse-delete, construtivos gulosos | Encerrados | E10 e E10b |
| All-V completa como método; desagregação parcial (antiga M-C) | Encerradas | A F-CC é uma alternativa mais bem estruturada para a mesma lacuna |
| Simetria em SC, pré-processamento, C3 exato | Encerrados ou pausados | Sem evidência nova |
| FPT/árvores como **método** | Fora do escopo | Teoria já publicada. Algoritmos de classes especiais servem só como **certificadores** (S1) |
| BP e HB como estresse | Encerradas | T20. BP-"não" e TR voltam como **instrumentos**, com hipótese nova e pré-registro próprio |

**Geração de colunas — reaberta só para a F-CC, com evidência nova.** A pausa anterior dizia que o
"pricing de conjuntos de estações é o problema original". **[Conferido]** Na F-CC isso não vale. O
pricing é um problema de **subgrafo conexo de prêmio coletado** em `H = G^r`: escolher `W` conexo e
pares balanceados `I ⊆ S∩B(W)`, `J ⊆ T∩B(W)`. Para `W` fixo, o melhor `(I, J)` sai de ordenar os
duais. É NP-difícil, mas é uma família estudada (Steiner de prêmio coletado ponderado em nós), não
o problema original. A reabertura também depende do portão GF1 (§9).

---

## 5. Revisão de Pereira & Ravelo (ETC/CSBC 2026, aranhas)

**[Fato, leitura do `.md`]**
- O problema definido é o de Das, com `S, T ⊆ V` e sem exigir disjunção.
- O algoritmo é guloso em `O(|V|)`:
  1. cada radial é processada da folha para o centro `c`, com estações no limite `r` (Lema 1);
  2. no centro, os robôs restantes são pareados em ordem decrescente de carga remanescente com os
     alvos em ordem decrescente de distância (Lema 2);
  3. decide-se se basta **uma** estação, em `c` (Teorema 1).
- A PLI aparece como trabalho futuro. Não cita o IJCAI-26.

**Pontos da prova que estão em esboço e precisam de teste.** São leituras desta análise, **não**
contraexemplos afirmados:
1. **Robôs que entram em uma radial.** O Lema 1 só argumenta sobre robôs que saem da radial em
   direção a `c`. Robôs que vêm de fora para alvos dentro da radial chegam a `c` com uma carga que
   depende do passo do centro. As estações que o guloso colocou para os robôs que saem podem não
   servir a eles.
2. **"De `c` todo alvo é alcançável"** (Teorema 1). Isso não está justificado quando o alvo está a
   mais de `r` de `c` numa radial sem robôs saindo. Caso a testar: `s` vizinho de `c`, `t` a
   distância `2r+1` de `c` em outra radial vazia. Se a leitura literal estiver certa, o ótimo exige
   estações dentro da radial de `t`, além de `c`.
3. **O argumento de troca do Lema 2** ignora as estações dentro da radial do alvo e os pares internos
   a uma mesma radial.
4. **`S∩T` e permanência** não aparecem nas provas.
5. **Fronteira `r' = 0`.** O texto supõe `0 < r'`.

**Uso no plano (S1).** Implementar os gulosos de caminhos e ciclos (Das) e de aranhas (Pereira &
Ravelo). Comparar com a PLI e com o validador independente num lote pré-registrado que contenha os
casos 1–5. Duas finalidades:
- validar em escala a PLI base e as formulações F-CC e F-C3 quando o guloso estiver correto;
- verificar o próprio algoritmo.

Divergência confirmada por enumeração é comunicada primeiro aos autores, que são do mesmo grupo.

---

## 6. As duas formulações alternativas

### 6.1 F-CC — formulação por configurações conectadas de estações

**Estrutura.**
- Variáveis: `y_v` binário em todo `V`; `λ_q ≥ 0` para configurações `q = (W, I, J)`; `d_st ≥ 0`
  para os pares diretos.
- Configurações: `W` é conexo em `H = G^r`, `I ⊆ S ∩ B(W)`, `J ⊆ T ∩ B(W)`, `|I| = |J| ≥ 1`.
- Pares diretos: `d(s,t) ≤ r`, incluindo `s = t`.
- R1/R2: cada origem e cada destino recebem 1.
- R3: `Σ_{q ∋ v} λ_q ≤ y_v`.

**[Conferido] Exatidão (esboço).**
- Dado `C`, o par `(s, t)` é realizável se e só se `d(s,t) ≤ r` ou existe uma componente `K` de
  `H[C]` com `s, t ∈ B(K)`. Os interiores da rota formam uma caminhada em `H[C]`.
- Logo a compatibilidade dada por `C` é a união de bicliques, uma por componente, mais as arestas
  diretas.
- Toda solução física vira um `λ` inteiro: uma configuração por componente.
- Para `y` binário, R1/R2 dão um emparelhamento perfeito fracionário no suporte compatível. A
  integralidade do politopo de emparelhamento bipartido devolve um emparelhamento inteiro.
- A permanência em `S∩T` é coberta por `d_ss`.

**[Conferido, esboço] Implica C1 e C2 no LP.** Uma configuração que atende `s` sem viagem direta
contém uma estação em `N⁺(s)` e uma estação em cada banda de distância até o alvo. **[Hipótese]**
Implica C4 só parcialmente: o argumento dá `y(Z) ≥ δ/|S'|`, não `≥ 1`. Isso precisa ser medido.

**[Conferido] Domina o LP da base.** Roteando `λ_q|I_q|` pelas estações de `W`, a ativação da base
vale porque `m·y_v ≤ b_v + (m − b_v)·y_v` para `y_v ≤ 1`.

**[Conferido] Não ganha no regime de cobertura.** Em SC-GF2, configurações de uma estação com
`λ = 2^{−(k−1)}` dão LP ≈ 2 contra `OPT = k`. É o gap do LP de set cover, como prevê o Teorema 3 do
IJCAI. **O núcleo inteiro segue melhor ali.** Se a F-CC servir para algo, é no regime `Γ > 0`.

**Ligação com o platô [Hipótese H-desc].** As soluções ótimas inviáveis do núcleo são inviáveis
porque suas estações **não formam componentes** de `H[C]` que liguem os pares. A F-CC impõe isso por
construção. R7 testa essa hipótese.

**Custo.** `Q` é exponencial. Precisa de geração de colunas:
- o LP só vale como limite **depois de convergir**, ou com limite lagrangeano/Farley a cada
  iteração;
- para a integralidade, branch-and-price ramificando em `y`;
- em instâncias com `H` denso (`|A_r|` de 10⁴ a 10⁶) o pricing é caro. Risco alto em escala.

### 6.2 F-C3 — componentes com consistência de trios

**Estrutura.**
- Separa a escolha da infraestrutura da escolha das atribuições: `λ_W`, `α_sW ≤ λ_W`,
  `β_tW ≤ λ_W`, `Σ_s α_sW = Σ_t β_tW`.
- Acrescenta, para cada trio de origens e de destinos, uma rede de 8 estados (diagrama de decisão)
  que impede misturas fracionárias incompatíveis de grupos sobrepostos.

**[Conferido] A separação `λ_W / α / β` preserva o LP da F-CC.** O politopo
`{(a, b) ∈ [0,1]^S × [0,1]^T : Σa = Σb}` tem vértices inteiros: um vértice tem no máximo uma
coordenada fora dos limites da caixa, e a igualdade a força a ser inteira. Assim `α/λ` e `β/λ` se
decompõem em pares `(I, J)` com `|I| = |J|`. A alegação do documento confere.

**F-OD descartada por decisão do usuário.** O documento original cita uma formulação intermediária
`F-OD` na cadeia de dominância, nunca definida em lugar nenhum do repositório. O usuário pediu para
desconsiderá-la. A cadeia relevante passa a ser:

\[
z_{\mathrm{LP}}^{\mathrm{baseline}} \le z_{\mathrm{LP}}^{\mathrm{F\text{-}CC}} \le z_{\mathrm{LP}}^{\mathrm{F\text{-}C3}} \le \mathrm{OPT}.
\]

A primeira desigualdade é a dominância sobre a base, conferida em §6.1. A segunda é a separação
`λ/α/β`, conferida acima. `F2` escreve essa cadeia sem `F-OD`; `F1` edita o arquivo renomeado da
F-C3 para remover a menção.

**Alegações ainda não verificáveis no repositório (independentes de F-OD).**
- A família de 20 vértices e 7 robôs, com valores 1/3/4 (base/F-CC/F-C3) e ótimo inteiro 4.
- A família geral com F-CC = 1,5g contra F-C3 = 2g.
- O contraexemplo de 15 vértices: F-C3 = 2,5 contra ótimo 3.

O documento completo com as provas aponta para um sandbox externo
(`MIN-STATION-formulacao-componentes-consistencia-trios.md`) que **não está no repositório**. Essas
três alegações ficam como **[Hipótese]** até o documento ser obtido ou os valores reproduzidos em
F3. Isso não bloqueia a Linha F: F3 mede o LP da F-CC desde já, e o da F-C3 assim que a enumeração
dos trios estiver implementada, independentemente de ter ou não o documento de provas — o que falta
sem o documento é só a verificação externa dos valores alegados.

**Custo.**
- O número de trios é `O(m³)`: com `m = 100` são cerca de 1,6·10⁵ redes; com `m = 1142` é
  inviável.
- A F-C3 completa só cabe em `m` pequeno. Em escala precisaria de **separação preguiçosa** dos trios
  violados. Isso é projeto novo e não está no documento.

### 6.3 Onde cada uma pode superar o que existe

| Regime | Núcleo (IP) | F-CC (LP) | F-C3 (LP) | Expectativa |
|---|---|---|---|---|
| Cobertura (`Γ = 0`; SC) | Resolve | Gap de set cover | Provavelmente igual | **Sem ganho** (controle negativo) |
| Compatibilidade por desconexão de cadeias (MAPF, maze/lin, `cc9-2p`, TR) | Fraco | **[Hipótese] ganho** | ≥ F-CC | Onde testar primeiro |
| Compatibilidade por partição numérica (BP-"não") | `2n+q` | **[Hipótese] sem ganho**: dividir itens fracionariamente entre caixas é o LP de bin packing | Desconhecido | Teste discriminante |
| Hall coletivo (HB, F2) | Fraco | Parcial (`δ/|S'|`) | **[Hipótese]** melhor | Teste |

"Desempenho melhor que hoje" tem dois níveis, testados nesta ordem:
1. **Força de limite:** LP da F-CC/F-C3 contra o núcleo IP e contra o COMP na raiz.
2. **Desempenho a trabalho igual:** branch-and-price ou price-and-branch contra o COMP, sob o
   protocolo.

O nível 2 só roda se o nível 1 passar no portão GF1.

### 6.4 Novos nomes de arquivo (aplicados na aprovação)

Seguindo o padrão `formulacao-*` e `desagregacao-por-origem.md`:

| Atual | Novo |
|---|---|
| `formulacao-min-station-alternativa-1.md` | `formulacao-fcc-configuracoes-conectadas.md` |
| `formulacao-min-station-alternativa-2.md` | `formulacao-fc3-consistencia-trios.md` |
| `Placement of charging stations for energy-constrained robots in spider graphs.md` | `pereira-ravelo-2026-aranhas.md` (sem espaços) |

Nenhum documento do repositório referencia os nomes atuais (conferido por `grep`), então nada
quebra. Junto com a renomeação, cada arquivo de formulação recebe **só um cabeçalho de estado**:
- origem: proposta externa;
- o que foi conferido nesta análise;
- o que é hipótese;
- o que falta: o documento de provas da F-C3 (a menção a F-OD é removida, não listada como falta).

O corpo muda só para remover a referência a F-OD e ajustar a cadeia de dominância (§6.2). Fora
isso, o `fc3` está escrito como resposta de chat, em primeira pessoa e com link de
sandbox; ele deve ser reescrito como documento de referência quando as provas completas chegarem
(tarefa F1).

---

## 7. Open Scientific Questions (reavaliadas)

`Γ(I) = OPT(I) − OPT_núcleo(I)`, sempre relativo ao núcleo C1+C2+C4-DM.

| # | Pergunta | O que falta | Potencial | Risco | Prioridade |
|---|---|---|---|---|---|
| Q-1 | Nas D/A o gap é de LB ou de UB? | Teste de folga primal com **um** fator (corrige o E13) | Decide a direção | Baixo | **HIGH** |
| Q-2 | Quanto vale `Γ` e onde se concentra? | Medir nas instâncias certificadas; limites `[max(0, LB* − núcleo), UB* − núcleo]` nas D/A | Decide o alvo | Médio | **HIGH** |
| Q-3 | Por que os ótimos do núcleo são inviáveis (H-desc)? | Anatomia do platô | Liga o platô a F-CC/M-A | Médio | **HIGH** |
| Q-4 | A F-CC/F-C3 fecha `Γ` no LP onde o núcleo falha? | Diagnóstico em instâncias pequenas (F3) | **Alto** (AV-3) | Médio | **HIGH**, barato e imediato |
| Q-5 | A F-CC em geração de colunas supera o COMP a trabalho igual? | Pricing, limite válido, branch-and-price | **Alto** (AV-1/2) | **Alto** | MEDIUM, condicionada a GF1 |
| Q-6 | Desigualdades de compatibilidade (projeções da F-CC/F-C3 ou derivadas do platô) no COMP | Derivação, validação, medição | Alto | Alto | MEDIUM, depois de Q-3/Q-4 |
| Q-7 | Matheurística primal ancorada no núcleo | Só se Q-1 apontar UB | Médio | Médio | Condicional |
| Q-8 | Os algoritmos de caminhos, ciclos e aranhas concordam com a PLI? | S1 | Suporte, possível erratum | Baixo | MEDIUM (suporte) |
| Q-9 | Simetria em SC; formulações compactas genéricas | — | Baixo | — | CLOSE |

---

## 8. Formulation, Cuts and Benchmark Assessment

**Base.** Segue como baseline. Comparação oficial: COMP = U + C1+C2+C4 com `f` contínuo, o que fecha
a Q6 de `open-questions.md`. **[Sugestão, a provar com cuidado]** Pelo Corolário 3 do IJCAI (Set
Cover com objetivo preservado), nenhum LP de tamanho polinomial fica dentro de `(1−ε) ln k` do ótimo
no pior caso, salvo P = NP. Isso **não** se aplica à F-CC/F-C3, que são exponenciais e com pricing
NP-difícil, mas em SC elas também têm o gap de cobertura (§6.1).

**Formulação nova.**
- **Sim, só a F-CC e a F-C3**, com portões.
- As demais direções continuam descartadas: matching explícito, rotas, estados de bateria,
  multicommodity completa.
- A desagregação parcial (antiga M-C) sai: a F-CC cobre a mesma lacuna de forma mais estruturada.

**Cortes.**
- Os de cobertura (C1, C2, C4, C6) estão em retorno marginal.
- Desigualdades de compatibilidade (M-A) seguem como linha, agora com duas fontes:
  1. a anatomia do platô (R7);
  2. as projeções em `y` do que a F-CC/F-C3 ganharem no LP. Se a F-C3 ganhar onde a F-CC não ganha,
     a projeção dos trios é candidata natural a corte separável no COMP, sem pagar `O(m³)`.

**Núcleo.** É a régua: separa o regime de cobertura do regime de compatibilidade e é o rival a bater
pela F-CC no limite inferior.

**Famílias.**
- SC: permanente; controle negativo de toda formulação ou corte de compatibilidade.
- TR e BP-"não": instrumentos com `Γ` certificado.
- HB e gadgets: regressão.
- Os exemplos de 20 e 15 vértices do documento da F-C3 entram como gabaritos quando definidos.
- Aranhas, caminhos e ciclos (S1): ótimo exato em `n` grande.
- Nenhuma família nova de dificuldade.

**Benchmark.** Para medir avanço faltam:
1. partição por grafo de origem;
2. linha de base com 3 sementes;
3. tag `v1.0`.

Licenças e ficha descritiva ficam adiadas (só importam para publicação).

---

## 9. Programa em fases, com portões

**Fase 0 — Fundação.** Saneamento mínimo, renomeação, partição, linha de base. Produz `LB*`/`UB*`
por instância.

**Linha F, paralela à Fase 0 — teste barato das formulações.** Não depende da linha de base: usa
instâncias pequenas e o validador.

**Portão GF1 [Sugestão; regra fixada antes da medição].** O LP da F-CC ou da F-C3 fica
**estritamente acima** de `max(LP com C1+C2+C4, núcleo IP)` em pelo menos 2 tipos de instância com
`Γ > 0` (entre TR, BP-"não", HB/F2, gabaritos do documento da F-C3, instâncias F pequenas com
`Γ > 0`) **e** fecha ≥ 50% de `Γ` em pelo menos um deles. Em SC não pode haver ganho; se houver,
investigar erro antes de comemorar.
- Passa: a F-CC entra na Fase 2 como método.
- Não passa: a F-CC fica registrada como caracterização exata, que é resultado teórico menor e
  resultado negativo de LP, e a geração de colunas volta a ficar pausada.

**Fase 1 — Diagnóstico.** Folga primal com um fator, `Γ` certificado e limitado, anatomia do platô
(testa H-desc).

**Portão G1.**
- `Γ` dominante: Fase 2 com M-F (se GF1 passou) e/ou M-A.
- Folga primal dominante: M-B.
- Sem sinal: documentar e devolver a decisão ao usuário.

**Fase 2 — Método.**
- **M-F:** geração de colunas da F-CC, com limite dual válido; depois branch-and-price ou
  price-and-branch. A F-C3 entra por trios **preguiçosos** só se F3 mostrar ganho de trios.
- **M-A:** desigualdades de compatibilidade (do platô ou projetadas da F-CC/F-C3), separadas no
  COMP.
- **M-B:** matheurística, só se G1 indicar.

Em todos os casos a validação segue a ordem: prova → validador → enumeração → S1 em escala →
efeito em `Γ` (com SC de controle) → D/A de desenvolvimento.

**Portão G2.** Efeito em ≥ 2 níveis de tamanho e em 3 sementes na partição de desenvolvimento.

**Fase 3 — Confirmação.** Partição de avaliação, sementes novas, critérios AV-1 a AV-4.
- Atingido: o usuário decide o próximo passo.
- Não atingido: volta ao G1 ou encerra com o resultado negativo documentado.

---

## 10. Prioritization Matrix

| Linha | Potencial | Evidência atual | Custo | Risco | Novidade pós-Bloco 4 | Prioridade |
|---|---|---|---|---|---|---|
| Fase 0 (linha de base) | Pré-requisito | Alta | Médio | Baixo | — | Obrigatória |
| **F3: LP da F-CC/F-C3 em instâncias pequenas** | Alto (decide M-F) | Média: exatidão conferida, ganhos alegados | **Baixo** | Médio | Alta | **Principal — nº 1 imediato** |
| Diagnóstico Q-1/Q-2/Q-3 | Decide a direção | Média–alta | Baixo | Baixo | Média | Principal |
| M-F: geração de colunas F-CC | **Alto** | Depende de GF1 | **Alto** | **Alto** | **Alta** | Principal se GF1 passar |
| M-A: desigualdades de compatibilidade | Alto | Platô medido | Alto | Alto | Alta | Principal / alternativa a M-F |
| S1: classes especiais | Suporte, possível erratum | Média | Baixo | Baixo | Média | Secundária (suporte) |
| M-B: matheurística | Médio | Fraca | Médio | Médio | Baixa | Condicional |
| Encerradas (§4) | — | Contra | — | — | — | Fora |

---

## 11. Proposed Tasks

### Fase 0

**R1 — Saneamento mínimo e renomeação.**
- Aplicar a §6.4: renomear e acrescentar os cabeçalhos de estado.
- Registrar Pereira & Ravelo em `source-map.md` e conferir a ref. 4 do `overlap` contra o `.md`.
- `open-questions.md`: corpo da Q1; Q3 fechada pela T5; Q6 = COMP; Q7 decidida em H11.
- Corrigir o cabeçalho de `direcoes` sobre `S∩T`.
- Marcar os planos antigos como históricos.
- Apontar o backlog para este plano.
- Aceite: nenhuma pergunta fechada aparece como aberta; nenhum resultado alterado.

**R2 — Partição por grafo de origem e tag `benchmark-v1.0`.**
- Regra determinística, escrita antes, sem olhar resultado de método.
- Registrar as 12 instâncias SC da Fase E.
- Aceite: `verify_t8_consolidacao.py` sem vazamento.

**R3 — Pré-registro da linha de base.**
- Braços: base U, COMP, núcleo.
- Instâncias: as 75 `principal`. Excluir da avaliação de avanço, de forma declarada, as estagnadas
  por escala (`m ≥ 1000`).
- Orçamento: `WorkLimit` calibrado; 4 threads; sem start; 3 sementes nas D/A; métricas da T9.

**R4 — Execução da linha de base.**
- Aceite: CSV com proveniência; tabela de `LB*`/`UB*`; comparação explícita com E9/E12.

### Linha F (pode começar logo após R1, em paralelo a R2–R4)

**F1 — Fixar as definições.**
- Remover a menção a `F-OD` do arquivo renomeado da F-C3 (decisão do usuário: desconsiderada) e
  ajustar a cadeia de dominância para `base ≤ F-CC ≤ F-C3 ≤ OPT`.
- Tentar obter do usuário o documento completo de provas da F-C3 (família de separação,
  contraexemplo de 15 vértices, família geral 1,5g/2g). Se não estiver disponível, a F-C3 segue
  mesmo assim para F2/F3 com as provas que o projeto conseguir re-derivar, e os valores alegados
  (20 vértices 1/3/4; 1,5g/2g; contraexemplo 2,5/3) ficam marcados `[Hipótese]` até serem
  reproduzidos ou obtidos.
- Reescrever `formulacao-fc3-consistencia-trios.md` como documento de referência (não mais resposta
  de chat em primeira pessoa), com o cabeçalho de estado da §6.4.

**F2 — Verificação teórica independente, escrita no repositório.**
- Exatidão da F-CC (esboço da §6.1).
- Dominância sobre o LP da base.
- Implicação de C1/C2.
- Relação com C4 e com `LP_cov` sobre `𝒵`.
- Equivalência `λ_W/α/β` (argumento de vértices).
- Aceite: provas escritas, ou o ponto marcado como aberto.

**F3 — Diagnóstico de LP em instâncias pequenas.**
- Implementar a F-CC (e a F-C3, se F1 permitir) por **enumeração explícita** dos `W` conexos, só
  para `n` pequeno.
- Medir, em cada instância: LP da base, LP+C1+C2+C4, núcleo IP, LP F-CC, LP F-C3 e OPT pelo
  validador.
- Instâncias:
  - gabaritos existentes;
  - TR(k=2, 3);
  - BP-"não" mínimas;
  - HB;
  - F2, Tri;
  - SC-GF2(3, 4) como controle negativo;
  - os exemplos de 20 e 15 vértices da F-C3, quando definidos;
  - aranhas pequenas de S1 com OPT exato.
- Conferir os valores alegados (1/3/3/4/4; 1,5g contra 2g; 2,5 contra 3). Divergência é registrada
  como tal, não ajustada.
- Pré-registrar a regra do portão GF1 antes de medir.
- Aceite: tabela completa e veredito GF1.
- Não fazer: geração de colunas, instâncias do benchmark.

### Fase 1

**R5 — Pré-registro do diagnóstico.**
- Definição de `Γ` e das amostras certificadas.
- Limites de `Γ` nas D/A.
- Teste de folga primal: só `MIPFocus=1` contra controle, mesmo `WorkLimit`, 3 sementes.
- Regra do G1.

**R6 — Medição de `Γ` e da folga primal.**
- Aceite: tabela de `Γ` e veredito LB × UB por família.

**R7 — Anatomia do platô.**
- Em 3–5 instâncias com `Γ > 0` (`cc9-2p`, `cc11-2u`, uma MAPF, uma maze/lin, TR, BP-"não"),
  registrar ótimos inviáveis do núcleo, os `Z` mínimos e os robôs não atendidos.
- Testar H-desc: as estações formam componentes de `H[C]` que ligam os pares?
- Aceite: H-desc confirmada ou refutada, com números, e hipóteses de desigualdade escritas.
- Não fazer: rodar CBI como método.

**Portões G1 e GF1:** documento curto de decisão citando F3, R6 e R7.

### Fase 2 (conforme os portões)

**R8 — M-F, geração de colunas da F-CC.**
- Pricing exato por MIP de subgrafo conexo em `H`, mais heurística.
- Limite lagrangeano/Farley a cada iteração; nenhum LB reportado sem convergência ou sem esse
  limite.
- Primeiro nas instâncias certificadas com `Γ > 0` de tamanho médio; depois nas D/A de
  desenvolvimento.
- Parada: o LB não supera `max(núcleo, COMP)` a trabalho igual em ≥ 2 famílias, ou o pricing não
  converge no orçamento nas instâncias-alvo.

**R9 — Branch-and-price ou price-and-branch da F-CC.** Só se R8 passar. Protocolo pareado contra o
COMP; critérios AV.

**R10 — M-A, desigualdades de compatibilidade.**
- Fonte: R7 e/ou a projeção do ganho de F3.
- Ordem: derivação → validador → enumeração → S1 → efeito em `Γ` (SC como controle) → D/A de
  desenvolvimento dentro do COMP.
- Parada: não reduz `Γ` em 2 níveis.
- Máximo de 3 ciclos antes de voltar ao usuário.

**R11 — S1, classes especiais.**
- Pode começar logo após R1.
- Gulosos de caminhos, ciclos e aranhas.
- Lote pré-registrado com os casos 1–5 da §5 e `S∩T`.
- Comparação com a PLI base, a F-CC e o validador.
- Contraexemplo é comunicado aos autores.

**R12 — M-B, matheurística.** Só se G1 indicar folga primal.

### Fase 3

**R13 — Confirmação na avaliação.** Sementes novas; AV-1 a AV-4 congelados antes.

### Sequência

```text
R1 ─┬─ R2 → R3 → R4 → R5 → R6 ┐
    │                    R7 ──┤
    ├─ F1 → F2 ─┐             ├→ G1 + GF1 → { R8 → R9 | R10 | R12 } → G2 → R13
    │           └→ F3 ────────┘
    └─ R11 (paralela; alimenta F3 e R8 com ótimos exatos)
```

---

## 12. Stop Criteria

| Linha | Parar quando |
|---|---|
| F3 / GF1 | O LP da F-CC/F-C3 não supera `max(LP+C1+C2+C4, núcleo)` em instâncias com `Γ > 0`. Também quando os valores alegados não se reproduzem e o documento de provas não estiver disponível; nesse caso a F-C3 fica pausada |
| M-F | O LB não supera `max(núcleo, COMP)` a trabalho igual em ≥ 2 famílias; o pricing não converge no orçamento; ou o ganho não se repete em 3 sementes |
| M-A | Não reduz `Γ` certificado em 2 níveis; inválida ou sem prova; novidade some na revisão; máximo de 3 ciclos |
| M-B | Não melhora o UB a trabalho igual em ≥ 2 famílias |
| S1 | Lote concluído |
| Programa | Avanço atingido (§2), ou linhas esgotadas. Nos dois casos, o resultado é documentado e a decisão volta ao usuário |
| Todas | Nunca seguir só com mais tempo, instâncias maiores, outra semente ou tuning sem hipótese nova |

---

## 13. Documentation / Governance Cleanup (dentro de R1)

- **Renomear e anotar** as formulações e o artigo das aranhas (§6.4).
- `open-questions.md`: Q1, Q3, Q6, Q7 desatualizadas (detalhe em R1).
- `direcoes-pli-min-station.md`: cabeçalho com `S∩T = ∅`.
- `source-map.md`: incluir Pereira & Ravelo, já que o PDF virou `.md`, e as formulações F-CC/F-C3
  como propostas em avaliação, sem tratá-las como baseline.
- `CLAUDE.md`, tabela de contexto, duas linhas novas:
  - "o que é contribuição → `overlap-ijcai2026-min-station.md`";
  - "formulações alternativas em avaliação → `formulacao-fcc-*` e `formulacao-fc3-*`".
- Planos antigos marcados como históricos; backlog apontando para este plano.
- **Adiado** (não há artigo agora): os itens "Passo posterior" do `overlap` §7.1, licenças e ficha
  descritiva do benchmark.

---

## 14. Final Recommendation

**Prioridade nº 1 imediata: F3.** É o diagnóstico de LP da F-CC (e da F-C3, se o documento for
obtido) em instâncias pequenas com `Γ` certificado.
- É o teste mais barato e mais decisivo disponível.
- Responde diretamente se as formulações podem superar o que existe.
- Ataca o mecanismo de falha medido (compatibilidade).
- Pode começar antes da linha de base.
- Tem controle negativo pronto (SC).

**Se o GF1 passar,** a linha que mais provavelmente gera um avanço considerável é a **M-F
(geração de colunas da F-CC)**, combinada com a projeção do ganho em desigualdades para o COMP
(M-A). **Se não passar,** a M-A segue a partir da anatomia do platô, e as formulações ficam como
resultado teórico e negativo documentado.

**Respostas diretas:**
1. **Continuar:** Fase 0, Linha F (F-CC/F-C3), diagnóstico (Q-1/Q-2/Q-3), M-F e M-A conforme os
   portões, S1 como suporte, M-B condicional.
2. **Encerrar:**
   - CBI e BC-y com cortes de ponto único;
   - Lagrangeana e Benders clássico;
   - reverse-delete e construtivos gulosos;
   - all-V completa e desagregação parcial;
   - BP e HB como estresse;
   - simetria em SC;
   - pré-processamento e C3 exato.

   A geração de colunas volta **só** para a F-CC e **só** se o GF1 passar.
3. **Prioridade nº 1:** F3, seguida de G1+GF1.
4. **Formulação nova:** sim, F-CC e F-C3, com portões. Nenhuma outra.
5. **Cortes novos:** sim, de compatibilidade, vindos do platô ou projetados da F-CC/F-C3.
6. **Famílias novas:** não. Instrumentos existentes, gabaritos da F-C3 e aranhas/caminhos/ciclos
   como certificadores.
7. **Benchmark:** suficiente para pesquisa depois de R2 e R4.
8. **Escrita:** fora deste plano, por decisão do usuário. Reavaliar só quando um critério AV for
   atingido.
9. **Obrigatório antes de testes de método em escala:** R1–R4, F1–F3 e R5–R7.
10. **Sequência:** R1 → (F1 → F2 → F3 ‖ R2 → R3 → R4 → R5 → R6/R7 ‖ R11) → G1 + GF1 → R8/R9 ou R10
    ou R12 → G2 → R13.

**Decisões pendentes do usuário:**
1. Os limiares AV-1 a AV-4 (§2).
2. ~~F-OD~~ — resolvida: desconsiderada. A cadeia de dominância passou a `base ≤ F-CC ≤ F-C3 ≤
   OPT`, e o arquivo renomeado da F-C3 é ajustado em F1 para remover a menção.
3. Se possível, fornecer o documento completo de provas da F-C3 (família de separação,
   contraexemplo de 15 vértices, família geral). Não é bloqueante: sem ele, F2/F3 seguem com
   re-derivação própria e os valores alegados ficam `[Hipótese]` até serem confirmados.

---

**Nota pós-análise N1-T0 (2026-10-07).** Este plano R1–R13 é histórico; a análise consolidada (07/10) e specs N1/N2 têm precedência. F-CC passou GF1 nos tipos HB, BP-não e Sec59; no controle SC F-CC não foi medida por `max_W`. R11 encerrou em divergência confirmada e não é oráculo. R8/R10 fundidos na pergunta N1; R9 e R12 continuam bloqueados. As previsões antigas de BP/HB não sobrescrevem os CSVs efetivamente obtidos.
