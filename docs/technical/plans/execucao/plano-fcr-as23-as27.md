# Programa FC-R — Decisão de pesquisa após AS22 (AS23–AS27)

**Estado (16/10/2026):** AS23 validada; AS24 `VALIDATED_WITH_MINOR_FINDINGS` após parecer independente do Claude relatado pelo pesquisador. AS25 liberada para implementação/pré-registro, **não executada**. Nenhuma campanha Gurobi real ou autorização MIP. Proveniência final da AS24 depende do commit local.  
**Fonte externa original:** [`parecer-astra-fcr-pos-as22.md`](../../reference/tecnico/parecer-astra-fcr-pos-as22.md) (Astra; consulta declarada `novos_testes@285261b`).  
**Baseline científico:** COMP+K original, modelo de Das com estações em todo `V`, fluxos agregados no dígrafo de alcance `H`, autonomia comum, terminais e interseção `S∩T` preservados.  
**Status de HL:** interromper a estratégia local testada; não declarar redundância global.

## Questão central e escopo

A família candidata FC-R preserva o fluxo nas desigualdades, tentando impedir a reutilização fracionária da mesma parcela de reentrada que limita cortes C8 individuais. A validade das formas de origem e destino decorre de balanço e ativação, **para variáveis de instalação binárias**. A separação ótima do conjunto de vértices `Q` é linear na fronteira **para uma região `L` fixa**, mas a seleção global de regiões **não possui prova de complexidade polinomial no parecer**.

### Formulação avaliada na AS23

Seja `H=(V,A_r)` o dígrafo de alcance, `d_L=|S∩L|-|T∩L|>0` e `Q ⊆ N_H⁺(L)\setminus(L∪T)`:

$$
 f(L,V\setminus(L\cup Q)) + d_L \sum_{v\in Q} y_v \ge d_L. \tag{FC-R}
$$

Para `h_L=|T∩L|-|S∩L|>0` e `Q ⊆ N_H⁻(L)\setminus(L∪S)`:

$$
 f(V\setminus(L\cup Q),L) + h_L \sum_{v\in Q} y_v \ge h_L. \tag{FC-R-T}
$$

No ponto `(f*,y*)`, para `L` fixo de excesso positivo, o parecer propõe selecionar:

$$
 Q^* = \{v\in N_H^+(L)\setminus(L\cup T): f^*(L,\{v\})>d_Ly_v^*\}.
$$

Empates podem ser decididos deterministicamente, sem alterar a violação matemática. A versão simétrica de destino foi especificada e testada na AS23; a separação por região fixa foi implementada na AS24.

## Evidência original do Astra e reprodução posterior na AS23

Construção do Astra: 24 vértices, 96 arcos, `r=1`, relés `X_i` com três vértices cada, 6 origens/6 destinos. Valores **originalmente afirmados pelo parecer**, posteriormente reproduzidos na AS23 por certificados exatos:

| Modelo | Valor atribuído pelo parecer | Natureza da evidência declarada |
|---|---:|---|
| `COMP+K` | `1` | ponto racional e limites inferiores |
| `COMP+K+FC-R` (quatro linhas) | `7/5` | ponto racional e combinação algébrica |
| `COMP+K+C6+C8` | `≤47/30` | ponto racional |
| `COMP+K+C6+C8+FC-R` | `17/10` | testemunha + combinação algébrica |
| MIP físico | `2` | argumento e enumeração declarada de conjuntos até cardinalidade 1 |

A AS23 reconstruiu a instância, conferiu a viabilidade física e os objetivos racionais. Veja `docs/technical/reference/experimentos/as23-validacao-fcr.md` e `specs/as-23-fcr-revisao-matematica/validation.md`. O parecer do Astra, por si só, não relatava campanha LP/MIP; a AS24 também não executou benchmarks reais. A AS24 registrou quatro violações unitárias no ponto COMP+K desse microcaso (`as24-validacao-separador-fcr.md`).

## Dependências e decisões condicionais

| Fase | Propósito | Entrada exigida | Saída/gate |
|---|---|---|---|
| **AS23** | Revisão independente da matemática e reprodução racional | Parecer externo + COMP/K/C6/C8 atuais | `VALIDATED` ou `BLOCKED`; nenhuma execução nova autorizada sem prova |
| **AS24** | Separador FC-R implementado e microtestado | AS23 `VALIDATED` técnico | `VALIDATED_WITH_MINOR_FINDINGS`; autoriza preparar AS25 após congelar protocolo, sem iniciar MIP |
| **AS25** | Piloto LP pareado nas seis instâncias de desenvolvimento | AS24 satisfaz critérios; protocolo pré-registrado | `GO_CANDIDATE_REVIEW`, `INVESTIGATE` ou `STOP`; nenhuma autorização MIP automática |
| **AS26** | Raiz MIP / piloto inteiro | AS25 com sinal suficiente + aprovação científica explícita | Comparar efeito após cortes automáticos, nós/tempo/gap; não ativado nesta entrega |
| **AS27** | Avaliação independente em grafos reservados | Política congelada e decisão pós-AS26 | Validar generalização sem vazamento; não ativado nesta entrega |

## Gate prospectivo de AS25 — sujeito a pré-registro antes de rodar

Quatro braços: `COMP`, `COMP+K`, `COMP+FC-R`, `COMP+K+FC-R`. A campanha principal totaliza 24 registros. A ablação entre separação por regiões unitárias e separação por regiões unitárias+maiores deve ser executada em rodada distinta e pré-registrada, com orçamento comparável e resultados identificados separadamente. Separar subfamília **regiões unitárias** (cobertura exaustiva nessa subfamília) de **regiões maiores selecionadas heuristicamente**. Os mesmos seis grafos brutos de desenvolvimento de AS16–AS22, mesmos hashes e identidade física, orçamento inicial de **90 s totais por braço** (preparação, separação, verificações e reotimização), com todos os casos censurados preservados.

Critério inicial sugerido pelo Astra: melhora LP ≥ **1%** em pelo menos **dois grafos brutos independentes**, custo total ≤ **2×** do braço controle nesses casos, com cobertura e censuras honestas. Este critério é **proposto**, deve ser congelado antes da campanha e não equivale a autorização de MIP.

Métricas mínimas: objetivo LP, incremento absoluto/relativo, linhas candidatas/violadas/adicionadas/duplicadas, tempo de preparação/separação/verificação/reotimização, variáveis/linhas/não zeros/memória, número de regiões elegíveis/testadas, razão de abstenção, mudança de fluxo sem ganho de objetivo, IDs de grafos, hash de instanciação e censuras.

## Fora de escopo e precauções

- Não alterar COMP+K, K, C6/C8, oráculos, experimentos passados nem a formulação física do problema durante AS23.
- Não afirmar novidade na literatura para fixed-charge flow, programação disjuntiva ou FC-R antes de mapeamento com artigos citáveis.
- Não declarar ganho real de FC-R com base na testemunha sintética; não extrapolar resultados para instâncias reservadas.
- Separação ótima **em `Q` para `L` fixo** não implica separação global ótima em `L`.
- Estações **sem capacidade** compartilhadas por quaisquer robôs; coeficiente regional `d_L` não cria capacidade física na estação.
- Distinguir valores reais de LP dos limites demonstrados por desigualdades e testemunhas.
- Nenhuma fase futura reabre MIP sem gate científico explícito; sem commits ou pushes automáticos.

## Artefatos previstos

- [`AS23`](../../../../specs/as-23-fcr-revisao-matematica/spec.md) — prova e testemunha independente.
- [`AS24`](../../../../specs/as-24-fcr-separador-micro/spec.md) — separação e microtestes.
- [`AS25`](../../../../specs/as-25-fcr-lp-pareado/spec.md) — LP pareado pré-registrado.
- [`AS26`](../../../../specs/as-26-fcr-mip-condicional/spec.md) — raiz MIP condicionada.
- [`AS27`](../../../../specs/as-27-fcr-avaliacao-independente/spec.md) — generalização em reserva (condicionada).

> **Roteamento TLC:** manter o padrão versionado do repositório `specs/as-XX-.../` em vez de duplicá-lo em `.specs/features/`. Cada fase tem `spec.md`, `design.md` e `tasks.md`; os validadores do `/tlc-spec-driven` aceitam caminhos explícitos. Specs planejadas não têm `validation.md` — esse arquivo só deve ser criado com evidências efetivas da execução/verificação.
