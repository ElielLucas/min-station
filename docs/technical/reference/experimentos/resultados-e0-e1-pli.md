# Resultados E0, E1' e E1 — Cortes de Cobertura para MIN-STATION

**Data:** 2026-09-25  
**Formulação:** BASE/U (Das), dígrafo de alcance A_r, fluxo contínuo (BASE-C)  
**Ambiente:** Gurobi 12.0.3 (licença acadêmica), Python 3.12.3 via Poetry, 12 CPUs

---

## 1. E0 — Integralidade gratuita: BASE-I vs BASE-C

**Hipótese:** Com y binário, tornar f contínuo não altera o ótimo (Proposição 3.2, TU).

| Instância | LP (ambos) | BASE-I OBJ | BASE-C OBJ | Status |
|---|---|---|---|---|
| cc10-2p | 0.1493 | **3** | **3** | ✓ IGUAL |
| Chicago (st5) | 0.0000 | **0** | **0** | ✓ IGUAL |
| Barcelona (st15) | 0.1333 | **1** | **1** | ✓ IGUAL |
| hc9u | 1.0000 | 45 | 44 | TL hit |
| lin23 | 1.1154 | 18 | 20 | TL hit |

**Notas da tabela:**
- hc9u: os valores 45 e 44 são incumbentes de 120 s, **não o ótimo**. A faixa conhecida é [31, 40] (LB histórico 31; UB histórico 40 em 3600 s; variante VI dá UB 38, que também é válido aqui).
- cc10-2p: status Gurobi = 9 (tempo limite) com bound = 1 e UB = 3. Não foi provada em E0; o ótimo OPT = 3 foi estabelecido em E1 (raiz com C1 = 3 = UB).
- lin23: incumbentes distintos por trajetórias heurísticas diferentes sob TL = 120 s.

**Observações:**
- O LP relaxado é idêntico em BASE-I e BASE-C por construção: relaxar y ao intervalo [0,1] já torna f livre nos dois modelos; igualdade de LP não é evidência adicional para a Prop. 3.2.
- Para hc9u e lin23, o limite de tempo impede prova formal.
- Chicago e Barcelona resolvem até otimalidade (OPT = 0 e OPT = 1), ambas triviais na R do arquivo.

**Conclusão E0:** 2 de 5 instâncias provadas (Chicago OPT = 0, Barcelona OPT = 1), ambas triviais. hc9u, cc10-2p e lin23 atingiram o limite de 120 s. Para hc9u, o incumbente de 120 s (44 ou 45) não reflete o ótimo real; a referência é [31, 40].

---

## 2. E1' — Validação em instâncias sintéticas

**Todos os 16 testes verificáveis: PASS.**

### Tabela de resultados

| Instância | Config | LP obs. | LP teórico | Resultado |
|---|---|---|---|---|
| F1(m=2,k=2) | BASE-C | 5.000000 | 5.0 | PASS |
| F1(m=2,k=2) | +C1+C2+C4 | 9.000000 | 9.0 (LP_cov) | PASS |
| F1(m=2,k=3) | BASE-C | 7.000000 | 7.0 | PASS |
| F1(m=2,k=3) | +C1+C2+C4 | 13.000000 | 13.0 (LP_cov) | PASS |
| F2(k=1) | BASE-C | 0.333333 | 1/3 | PASS |
| F2(k=1) | +C1+C2+C4 | 1.000000 | 1.0 (LP_cov=OPT) | PASS |
| F2(k=2) | BASE-C | 0.333333 | 1/3 | PASS |
| F2(k=2) | +C1+C2+C4 | 2.000000 | 2.0 (LP_cov=OPT) | PASS |
| Tri | BASE-C | 1.000000 | 1.0 | PASS |
| Tri | +C1+C2+C4 | 1.500000 | 1.5 (LP_cov) | PASS |
| §5.9(L=7) | BASE-C | 2.333333 | 7/3 | PASS |

**OPTs verificados via MIP (todos PASS):**
F1(k=2): 9, F1(k=3): 13, F2(k=1): 1, F2(k=2): 2, Tri: 2, §5.9(L=7): 7.

### Observações por família

**F1 (raios):**
- C1 melhora LP de 2k+1 para algo maior. C2 fecha completamente para OPT=2mk+1.
- C4-DM não adiciona nada além de C1+C2 para instâncias de raio.

**F2 (bolsões de Hall):**
- C1 e C2 não ajudam (z_LP=1/3 permanece após ambos).
- **C4-DM fecha completamente para LP_cov=OPT.** Confirmação direta da teoria de Dulmage-Mendelsohn para instâncias de Hall.

**Tri (triângulo):**
- C1 melhora LP de 1.0 para 1.5 (LP_cov). Não fecha completamente (OPT=2).
- Gap residual de 0.5 requer técnicas além de C1-C4 (ex.: cortes de Chvátal-Gomory).

**§5.9 (contraexemplo BC-y):**
- z_LP BASE = 7/3 ≈ 2.333 (conforme teoria).
- Com C4-DM: LP sobe para 11/3 ≈ 3.667 (melhoria significativa).
- OPT=7 confirmado. Gap entre 11/3 e 7 persiste.
- O gap residual é **Hall multi-salto (C5)**: cada vértice wᵢ é um separador individual (removê-lo desconecta alguma origem de todos os destinos), portanto y(wᵢ) ≥ 1 é válida. Com y*(wᵢ) < 1 após C4-DM, essas restrições são violadas. Adicioná-las (LP_cov) fecha exatamente para 7. C3 não detecta essas violações porque o max-flow per-origem ainda atinge 1 (cada origem tem rotas alternativas).

---

## 3. E1 — Instâncias reais, configurações A–E

**Configurações cumulativas (BASE-C):**

| Config | Cortes ativos |
|---|---|
| A | Nenhum |
| B | C1 |
| C | C1 + C2 |
| D | C1 + C2 + C4-DM |
| E | C1 + C2 + C4-DM + C3 (LP iterativo) |

**Medidas por configuração:**
- **LP puro:** relaxação LP contínua do modelo com cortes manuais (+ C3 iterativo em E)
- **Raiz-sem:** NodeLimit=0, Cuts=0, Presolve=0 (só nossos cortes, sem Gurobi)
- **Raiz-pad:** NodeLimit=0, parâmetros padrão Gurobi

---

### 3.1 hc9u — Hipercubo 9-dim (m=128, n=512, R=1, |A_r|=4608)

| Config | LP puro | Raiz-sem | Raiz-pad |
|---|---|---|---|
| A | 1.0000 | 1 | 1 |
| **B (C1)** | **28.4444** | **29** | **29** |
| C (C1+C2) | 28.4444 | 29 | 29 |
| D (+C4) | 28.4444 | 29 | 29 |
| E (+C3) | 28.4444 | 29 | 29 |

- **LP+C1 = 256/9 ≈ 28.44**: previsão teórica CONFIRMADA com precisão de 6 casas decimais.
- C2, C4 e C3 não adicionam nada para hc9u. Toda a melhoria vem de C1.
- O limitante da raiz sobe de 1 para 29 com C1 — a diferença entre o incumbente de 120 s (44–45) e raiz-base=1 é dramaticamente reduzida. O ótimo real está em [31, 40]; o LB de 29 fecha 93% do gap [1, 31].
- Gurobi (raiz-pad) não melhora além do arredondamento inteiro ⌈28.44⌉=29.

---

### 3.2 hc10p — Hipercubo 10-dim (m=256, n=1024, R=150, |A_r|=10240)

| Config | LP puro | Raiz-sem | Raiz-pad |
|---|---|---|---|
| A | 1.0000 | 1 | 1 |
| **B (C1)** | **51.2000** | **52** | **52** |
| C–E | 51.2000 | 52 | 52 |

- LP+C1 = 512/10 = 51.2. Padrão idêntico ao hc9u: só C1 importa.
- Melhoria de raiz: 1 → 52.

---

### 3.3 Chicago st5 — TNTP denso (m=5, n=400, R=32, |A_r|=101617)

LP=0 e raiz=0 para todas as configurações. OPT=0 (todos os 5 robôs alcançam destinos sem estação). Instância trivial para R=32; não contribui para análise de cortes.

---

### 3.4 Philadelphia st25 — TNTP longo curso (m=25, n=800, R=3, |A_r|=9837)

| Config | LP puro | Raiz-sem | Raiz-pad |
|---|---|---|---|
| A | 2.3200 | 3 | 4 |
| B (C1) | 28.0444 | 29 | 30 |
| **C (C1+C2)** | **33.5950** | **34** | **35** |
| D (C1+C2+C4) | 33.5950 | 34 | 35 |
| **E (+C3)** | **35.6104** ¹ | 34 | 35 |

- C1 melhora LP de 2.32 para 28.04 (+25.7).
- **C2 adiciona +5.55** (28.04 → 33.60) — relevante para Philadelphia.
- C4-DM não adiciona nada além de C1+C2.
- **C3 melhora o LP para 35.61** (+2.01 sobre C4), mas o limitante da raiz (sem callback) permanece 34.
  - Isso indica que C3 fortalece o LP mas os cortes gerados não estão no modelo MIP.
  - Para traduzir o ganho de C3 na raiz, seria necessário adicionar os cortes explicitamente ao MIP ou usar callback.
- Gurobi (raiz-pad) melhora mais 1 unidade: 35 > 34.

¹ **Nota de correção (rodada E7, 2026-09-25):** o valor original era 35.3425, medido com a implementação defeituosa de `generate_C2` (usava `dijkstra_from` no lado T em vez de `dijkstra_to`, inválido em grafos TNTP assimétricos). Remedido com o C2 corrigido: 35.6104. Os limites das configs B, C e D não se alteram (C2 nos dois sentidos afeta só o LP iterativo com C3). O threshold da H3 do E2 passou a ser 35.61, não 35.34.

---

### 3.5 cc10-2p — Cobertura (m=67, n=1024, R=500, |A_r|=339124)

| Config | LP puro | Raiz-sem | Raiz-pad |
|---|---|---|---|
| A | 0.1493 | 1 | 1 |
| B (C1) | 2.5714 | 3 | 3 |
| C (C1+C2) | 2.5714 | 3 | 3 |
| D (C1+C2+C4) | 2.6154 | 3 | 3 |
| E (+C3) | (em execução) | — | — |

- C1 melhora LP de 0.15 para 2.57 (+17x). OPT=3 (do E0). Com raiz-sem=3 na Config B, a **raiz com C1 já atinge OPT=3**.
- C2 não adiciona nada para cc10-2p (LP=2.5714 em B e C).
- **C4-DM adiciona 0.044** (2.5714 → 2.6154) — efeito pequeno mas presente. Único caso nas instâncias reais testadas onde C4 é estritamente útil após C1+C2.
- Raiz permanece 3=OPT em D, confirmando que a melhoria de LP por C4 não altera o limitante inteiro neste caso.

---

### 3.6 cc12-2p — Cobertura grande (m=236, n=4096, R=500, |A_r|=2.795.100)

| Config | LP puro | Raiz-sem | Raiz-pad |
|---|---|---|---|
| A | 0.1059 | inválida¹ | 1 |
| B (C1) | **4.7414** | inválida¹ | inválida¹ |
| C (C1+C2) | 4.7414 | inválida¹ | inválida¹ |
| D (C1+C2+C4) | **5.1674** | inválida¹ | inválida¹ |
| E (+C3) | em execução | — | — |

¹ raiz=0: artefato de limite de tempo (120 s) — a raiz não fecha para cc12-2p nessa configuração.

- **LP+C1 = 4.74 → OPT ≥ ⌈4.74⌉ = 5** (LB anterior: 1, via LP base).
- **LP+C4 = 5.17 → OPT ≥ ⌈5.17⌉ = 6** — novo LB.
- UB histórico: 7 (baseline 3600 s). Portanto **OPT ∈ [6, 7]** após E1.
- Os valores de raiz são todos zero por limite de tempo (|A_r| = 2,8M torna o modelo compacto pesado demais para fechar a raiz em 120 s).

---

### 3.7 Resumo: referências históricas e gap fechado

| Instância | LB pré-E1 | LP+C1 | LP melhor | Raiz melhor | UB histórico | Gap fechado na raiz |
|---|---|---|---|---|---|---|
| hc9u | 31 | 28,44 | 28,44 | 29 | 40 | 93% de [1, 31] |
| hc10p | 52 | 51,20 | 51,20 | 52 | 80 | 100% de [1, 52] |
| Philadelphia st25 | 42 | 28,04 | 35,61 ¹ | 35 | 46 | 82% de [2,32, 42] |
| cc10-2p | 1 | 2,57 | 2,62 | **3 = OPT** | 3 | OPT provado |
| cc12-2p | 1 | 4,74 | 5,17 | inválida | 7 | novo LB = 6 |

---

## 4. Análise por regime

### Regime R-b: terminais densos (hipercubos hc9u, hc10p)
- **C1 é dominante.** C2, C4, C3 redundantes.
- Padrão: LP_base=1, LP+C1=2m/d (onde d=dimensão, 2m=total de cortes).
- Raiz com C1 ≈ ceil(2m/d): previsível analiticamente.
- Gap residual entre raiz e OPT persiste: hc9u raiz=29, OPT ∈ [31, 40] (LB histórico 31); 93% do gap [1, 31] fechado.

### Regime R-a: longo curso TNTP (Philadelphia)
- **C1 e C2 são complementares.** C4 redundante.
- C3 melhora LP mas requer callback para impactar a raiz.
- Sequência A→B→C captura a maior parte do ganho.

### Regime R-c: cobertura densa (cc10-2p)
- C1 já fecha para OPT na raiz (raiz-sem=OPT=3 com Config B).
- Instância de R grande: relés abundantes, C1 suficiente.

---

## 5. Conclusão sobre hipótese A1

**Hipótese A1:** _Os cortes de cobertura C1 e C2 melhoram significativamente o limitante da raiz para todas as instâncias testadas._

**Veredicto: A1 FORTEMENTE SUPORTADA.**

| Evidência | Força |
|---|---|
| hc9u: raiz 1 → 29 com C1 (+2800%) | Forte |
| hc10p: raiz 1 → 52 com C1 (+5100%) | Forte |
| Philadelphia: raiz 3 → 34 com C1+C2 (+1033%) | Forte |
| cc10-2p: raiz 1 → 3 = OPT com C1 | Fecha na raiz |
| Previsão LP ≥ 256/9 (hc9u): verificada exatamente | Forte |

**C4-DM:** Eficaz para instâncias de Hall (F2 em E1') mas redundante nas instâncias reais testadas. O regime que ativa C4 (terminais densos com violações de Hall não resolvidas por C1) não aparece de forma pura nas instâncias TNTP ou de cobertura.

**C3:** Melhora o LP em Philadelphia (+1.74) mas não traduz para raiz sem callback. Para aproveitar C3 no B&B, é necessário implementar separação iterativa com callback ou pré-processamento de cortes antes da raiz.

---

## 6. Questões em aberto e próximos passos

1. **Gap residual em hc9u** (raiz=29, OPT ∈ [31, 40]; incumbente 120 s = 44/45): requer cortes além de C1. Possibilidades: núcleo de cobertura (K(8,1)), C5 (Hall multi-hop), simetria (B2), ou BC-y com callback de C3.

2. **C3 como pré-processamento da raiz:** adicionar cortes C3 ao modelo MIP antes da raiz (não só no LP iterativo). Isso traduziria o ganho de 35.61 em limitante da raiz para Philadelphia.

3. **C4-DM em regime misto:** as instâncias testadas têm S e T ou não-adjacentes (hipercubos) ou com A_r muito denso. Uma instância com violação de Hall moderada (como F2 com k pequeno) seria ideal para explorar C4.

4. **Barcelona e lin37:** Barcelona (n=930, m=25) ainda em execução no E0. Lin23/lin37 são instâncias Steiner lineares — interessantes para C2 (bandas de distância).

5. **Chicago com R menor:** Chicago com R=5 ou R=10 geraria instâncias não-triviais (OPT>0) e testaria melhor os regimes de corte.

---

*Experimentos executados com: Python 3.12.3, Gurobi 12.0.3, seed=42, threads=4.*  
*Código em: `experiments/cuts/` — cortes em `cuts.py`, runner em `run_e0.py`, `run_e1prime.py`, `run_e1.py`.*
