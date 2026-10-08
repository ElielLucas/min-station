# Resultados R6 — Γ e classificação

**Data:** 2026-10-06
**Pré-registro:** `docs/technical/reference/experimentos/pre-registro-r5.md` (congelado 2026-10-06T10:40:00-03:00, antes desta medição)
**CSV:** `results/benchmark/r6-gamma.csv`
**Núcleo:** IP em `y` com C1+C2+C4-DM, o mesmo da linha de base.
**Definição:** `Γ = OPT − OPT_core`. Intervalo nunca é apresentado como valor único.

Este relatório cobre só a tabela de `Γ`. O teste primal (MIPFocus=1) está em `resultados-r6-primal.md`.

## Checagens obrigatórias

| Instrumento | Esperado | Medido |
|---|---|---|
| SC-GF2 k=3 | núcleo = 3 | 3 |
| SC-GF2 k=4 | núcleo = 4 | 4 |
| BP-"não" q=2 B=10 | núcleo = 2n+q = 14 (6 itens), OPT = 15 | 14 e 15 |
| BP-[3,1] | núcleo = 6, OPT = 7 | 6 e 7 |
| TR k=2 L=5 r=2 | núcleo = 3 = OPT, Γ = 0 | 3 e Γ = 0 |

`plantar_nao(2, 8, ·)` e `plantar_nao(2, 12, ·)` falham no gerador. O pré-registro registrou `B=10` **antes** de qualquer valor de Γ dessas linhas. As seeds 0 e 1 produziram o mesmo vetor de itens `[3, 3, 3, 5, 3, 3]`; as duas linhas existem porque o contrato pedia duas seeds de gerador, não duas instâncias distintas.

## Classe `exact` (OPT e núcleo provados)

Fonte de OPT nas F/legado: `LB* = UB*` da linha de base. Fonte estrutural: teorema, DP, enumeração ou fórmula TR, conforme a coluna.

| Instância | Família | OPT | OPT_core | Γ | Fonte OPT |
|---|---|---:|---:|---:|---|
| mapf-maze-32-32-2-m10-f4.txt | mapf | 7 | 5 | 2 | linha_base LB*=UB* |
| mapf-maze-32-32-2-m25-f2.txt | mapf | 5 | 3 | 2 | linha_base LB*=UB* |
| pace18-t2-001-regiao-f2.txt | pace18 | 3 | 2 | 1 | linha_base LB*=UB* |
| pace18-t2-061-regiao-f4.txt | pace18 | 7 | 6 | 1 | linha_base LB*=UB* |
| pace18-t2-081-regiao-f2.txt | pace18 | 3 | 2 | 1 | linha_base LB*=UB* |
| pace18-t2-181-regiao-f2.txt | pace18 | 2 | 2 | 0 | linha_base LB*=UB* |
| puc-cc10-2u-regiao-f2.txt | puc | 2 | 2 | 0 | linha_base LB*=UB* |
| puc-cc6-3p-seed-r1.txt | puc | 32 | 31 | 1 | linha_base LB*=UB* |
| puc-hc10p-regiao-f4.txt | puc | 6 | 6 | 0 | linha_base LB*=UB* |
| puc-hc9u-regiao-f2.txt | puc | 5 | 4 | 1 | linha_base LB*=UB* |
| puc-w23c23-intercalado-f2-rho.txt | puc | 128 | 128 | 0 | linha_base LB*=UB* |
| pucn-cc3-5n-seed-r1.txt | pucn | 8 | 5 | 3 | linha_base LB*=UB* |
| pucn-cc5-3n-seed-r1.txt | pucn | 15 | 14 | 1 | linha_base LB*=UB* |
| pucn-cc6-2n-seed-r1.txt | pucn | 6 | 4 | 2 | linha_base LB*=UB* |
| b-b06-intercalado-f2.txt | b | 1 | 1 | 0 | linha_base LB*=UB* |
| b-b06-regiao-f2.txt | b | 3 | 3 | 0 | linha_base LB*=UB* |
| b-b09-intercalado-f2-rho.txt | b | 2 | 2 | 0 | linha_base LB*=UB* |
| b-b12-intercalado-f2.txt | b | 7 | 7 | 0 | linha_base LB*=UB* |
| b-b12-regiao-f2.txt | b | 3 | 3 | 0 | linha_base LB*=UB* |
| b-b15-regiao-f4.txt | b | 9 | 8 | 1 | linha_base LB*=UB* |
| b-b18-intercalado-f2.txt | b | 1 | 1 | 0 | linha_base LB*=UB* |
| b-b18-regiao-f2.txt | b | 2 | 2 | 0 | linha_base LB*=UB* |
| i-i080-001-regiao-f2.txt | i | 1 | 1 | 0 | linha_base LB*=UB* |
| i-i080-041-regiao-f2.txt | i | 1 | 1 | 0 | linha_base LB*=UB* |
| i-i080-301-regiao-f2.txt | i | 5 | 5 | 0 | linha_base LB*=UB* |
| i-i080-341-intercalado-f2.txt | i | 2 | 2 | 0 | linha_base LB*=UB* |
| i-i160-301-intercalado-f2-rho.txt | i | 5 | 5 | 0 | linha_base LB*=UB* |
| i-i160-301-regiao-f2.txt | i | 4 | 4 | 0 | linha_base LB*=UB* |
| lin-lin01-regiao-f2.txt | lin | 2 | 2 | 0 | linha_base LB*=UB* |
| lin-lin03-regiao-f4.txt | lin | 7 | 5 | 2 | linha_base LB*=UB* |
| lin-lin06-intercalado-f2.txt | lin | 3 | 3 | 0 | linha_base LB*=UB* |
| lin-lin06-regiao-f4.txt | lin | 7 | 6 | 1 | linha_base LB*=UB* |
| urb-apia-m10-f8.txt | urb | 8 | 8 | 0 | linha_base LB*=UB* |
| urb-belize_city-m25-f4.txt | urb | 4 | 4 | 0 | linha_base LB*=UB* |
| urb-st_helier-m10-f4.txt | urb | 4 | 4 | 0 | linha_base LB*=UB* |
| SC-GF2-k3 | sc | 3 | 3 | 0 | teorema OPT=k |
| SC-GF2-k4 | sc | 4 | 4 | 0 | teorema OPT=k |
| BP-nao-q2-B10-s0 | bp-nao | 15 | 14 | 1 | DP sem partição → 2n+q+1 |
| BP-nao-q2-B10-s1 | bp-nao | 15 | 14 | 1 | DP sem partição → 2n+q+1 |
| BP-nao-[3,1]-q2 | bp-nao | 7 | 6 | 1 | enum independent_validator |
| HB-q4-ndir2-p1 | hb | 2 | 1 | 1 | enum independent_validator |
| HB-q5-ndir2-p1 | hb | 3 | 1 | 2 | mip_base T5 |
| TR-k2-L5-r2 | tr | 3 | 3 | 0 | fórmula TR |

## Classe `interval` (núcleo provado; OPT não)

Reporta-se `[max(0, LB* − OPT_core), UB* − OPT_core]`. Nenhum destes números é Γ.

| Instância | Família | OPT_core | Γ lo | Γ hi | LB* | UB* |
|---|---|---:|---:|---:|---:|---:|
| mapf-room-32-32-4-m10-f8.txt | mapf | 13 | 3 | 5 | 16 | 18 |
| pace18-t2-141-regiao-f4.txt | pace18 | 8 | 2 | 4 | 10 | 12 |
| puc-cc10-2u-seed-r1.txt | puc | 52 | 1 | 5 | 53 | 57 |
| puc-cc11-2u-seed-r1.txt | puc | 92 | 0 | 9 | 92 | 101 |
| puc-cc12-2u-seed-r1.txt | puc | 164 | 1 | 29 | 165 | 193 |
| puc-cc9-2p-seed-r1.txt | puc | 27 | 3 | 4 | 30 | 31 |
| puc-w23c23-seed-r1.txt | puc | 139 | 1 | 17 | 140 | 156 |
| pucn-cc3-10n-seed-r1.txt | pucn | 18 | 0 | 8 | 18 | 26 |
| vienna-I056-regiao-f4.txt | vienna | 9 | 0 | 2 | 9 | 11 |
| vienna-I065-intercalado-f2.txt | vienna | 16 | 0 | 4 | 16 | 20 |
| vienna-I065-regiao-f4.txt | vienna | 13 | 1 | 7 | 14 | 20 |
| hc9u.txt | hc9u | 32 | 0 | 9 | 32 | 41 |

`hc9u.txt` é legado com núcleo ótimo e `LB* ≠ UB*`. A tabela de classes da spec (não o rótulo F) manda intervalo.

## Classe `unknown` (núcleo sem prova)

Sem estimativa.

| Instância | status_core | LB* | UB* |
|---|---:|---:|---:|
| bip42p.txt | 16 | 35 | 43 |
| hc10p.txt | 16 | 56 | 77 |
| hc11p.txt | 16 | 97 | 161 |
| hc12p.txt | 16 | 171 | 376 |
| puc-bip42p-regiao-f2.txt | 16 | 35 | 43 |
| puc-bip42p-seed-r1.txt | 16 | 35 | 43 |

As duas `puc-bip42p*` estão na amostra D/A de desenvolvimento, mas o núcleo não fechou; o caso de borda da spec prevalece sobre o rótulo da amostra.

## Famílias exact com Γ > 0

Oito famílias: `mapf`, `pace18`, `puc`, `pucn`, `b`, `lin`, `bp-nao`, `hb`.

A regra G1 pede Γ > 0 em pelo menos duas famílias exact. Essa metade da regra já está satisfeita. A outra metade é o teste primal.

## Ressalva F fácil por seleção

As instâncias F (e os gadgets) entram em `exact` precisamente porque o solver prova OPT no orçamento da linha de base. Isso **pode subestimar** o Γ das D/A. Os intervalos D/A acima mostram limites inferiores de Γ positivos em várias famílias (`mapf` ≥ 3, `pace18` ≥ 2, `puc-cc9` ≥ 3), mas não são valores de Γ e **não** entram na regra G1.

## Veredito por família (só o lado LB; primal à parte)

| Família | Exact Γ > 0 | Papel no G1 (LB) |
|---|---|---|
| mapf | sim (2, 2) | conta |
| pace18 | sim (1, 1, 1) | conta |
| puc | sim (1, 1) | conta |
| pucn | sim (3, 1, 2) | conta |
| b | sim (1) | conta |
| lin | sim (2, 1) | conta |
| bp-nao | sim (1) | conta |
| hb | sim (1, 2) | conta |
| sc, tr, urb, i | não (todos 0) | não conta para o limiar ≥ 2 |

---

**Nota pós-análise N1-T0 (2026-10-07).** Resultados P/E e baseline rotulados por `-dirty` requerem snapshot, diff arquivado ou hash completo dos códigos quando forem reutilizados como reprodução exata. Hash do gerador de cortes isolado não substitui proveniência de todo o experimento. N1 precisa preservar `PYTHONHASHSEED=0`, versões e hashes por braço.
