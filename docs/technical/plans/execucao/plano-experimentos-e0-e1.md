# Plano: experimentos de validação E0, E1' e E1

**Data:** 2026-09-25  
**Status:** concluído (exceto cc12-2p Config E, ainda em execução)

---

## Objetivo

Validar as famílias de cortes de cobertura C1, C2, C4-DM e C3 como fortalecimento da
formulação compacta BASE/U para o MIN-STATION, e verificar empiricamente a Proposição 3.2
(integralidade gratuita de f com y binário).

---

## E0 — integralidade gratuita (BASE-I vs BASE-C)

**Hipótese:** Com y ∈ {0,1}, tornar f ∈ ℝ⁺ não altera o ótimo inteiro.

**Instâncias:** hc9u, cc10-2p, lin23, Chicago st5 R32, Barcelona st15 R24  
**Tempo limite:** 120 s, 4 threads, seed 42

**Resultado:**
- 2/5 provadas ótimas (Chicago OPT=0, Barcelona OPT=1) — ambas triviais na R do arquivo.
- hc9u, cc10-2p e lin23 bateram o limite de tempo. Os incumbentes diferem por trajetórias
  heurísticas distintas, não por ótimos distintos.
- LP relaxado idêntico nos dois casos por construção (relaxar y já torna f livre nos dois).

---

## E1' — validação em instâncias sintéticas

**Objetivo:** verificar que cada família de corte produz o LP esperado segundo a teoria.

**Instâncias:** F1(m=2, k=2 e k=3), F2(k=1 e k=2), Tri, §5.9(L=7)  
**Configurações:** BASE-C, +C1, +C1+C2, +C1+C2+C4, +C1+C2+C4+C3 iterativo

**Resultado:** 16/16 testes verificáveis: PASS.

Padrões confirmados:
- F1: z_LP BASE = 2k+1 → com C1 = 2m+2k−1 → com C1+C2 = 2mk+1 = OPT.
- F2: z_LP BASE = 1/3 → C1 e C2 não ajudam → C4-DM fecha para k = OPT.
- Tri: z_LP BASE = 1 → com C1 = 1,5 (LP_cov); OPT = 2 requer posto 2.
- §5.9(L=7): z_LP BASE = 7/3 → com C4-DM = 11/3; OPT = 7; C3 não adiciona cortes.
  O gap residual 11/3 → 7 é Hall multi-salto (C5): cada vértice wᵢ é separador
  individual, logo y(wᵢ) ≥ 1, e LP_cov = 7.

---

## E1 — raiz em instâncias reais (configs A–E)

**Hipótese A1:** C1 e C2 melhoram significativamente o limitante da raiz nas três regimes.

**Instâncias:** hc9u, hc10p, Chicago st5, Philadelphia st25, cc10-2p, cc12-2p  
**Configurações:** A (sem cortes) → B (+C1) → C (+C2) → D (+C4) → E (+C3 iterativo no LP)  
**Medidas:** LP puro, raiz sem Gurobi (Cuts=0, Presolve=0), raiz padrão Gurobi

**Resultado:**
- **A1 CONFIRMADA** nos três regimes (critério: ≥ 20% em ≥ 2 regimes).
  - R-b (hc9u): raiz 1 → 29 com C1 (+2800%); LP = 256/9 ≈ 28,44 confirmado.
  - R-b (hc10p): raiz 1 → 52 com C1 (+5100%); LP = 512/10 = 51,2.
  - R-a (Philadelphia): raiz 3 → 35 com C1+C2+Gurobi; LP com C3 = 35,34.
  - R-c (cc10-2p): raiz 1 → 3 = OPT com C1 (OPT provado: raiz 3 + UB 3).
- C3 melhora o LP em Philadelphia (+1,74) mas não chegou à raiz porque os cortes não
  foram adicionados ao modelo MIP antes da medição da raiz.
- cc12-2p: LP+C1 = 4,74 → LB ≥ 5 (novo); LP+C4 = 5,17 → LB ≥ 6 (novo). Raiz inválida
  (|A_r| = 2,8M, limite de tempo sem fechar a raiz). Config E ainda em execução.

---

## Decisões decorrentes

- Linha A2 (BC-y): viável se o LP só em y alcança o LP compacto — testar em E2.
- C3 precisa ser adicionado ao MIP como cortes estáticos, não só ao LP iterativo.
- cc12-2p não entra nas medições de raiz desta rodada.
- lin23 e lin37 excluídas da próxima rodada por pedido do usuário.

---

*Código em `experiments/cuts/`; resultados em `results/cuts/e0_resultados.csv` e
`results/cuts/e1_sinteticos.csv`.*
