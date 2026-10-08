# Resultados R6 — teste primal (um fator)

**Data:** 2026-10-06
**Pré-registro:** `docs/technical/reference/experimentos/pre-registro-r5.md` §3
**CSV:** `results/benchmark/r6-primal.csv`
**Controle:** `braco=comp` de `linha_base.csv`, copiado, não reexecutado
**Experimental:** COMP, `MIPFocus = 1`, demais parâmetros iguais (`WorkLimit = 164`, `TimeLimit = 1800` guarda, 4 threads, sem MIP start, seeds 42/43/44)
**Amostra:** D/A, partição desenvolvimento, `m < 1000` (13 instâncias × 3 sementes = 39 pares)

Limiar congelado: melhoria = `UB_controle − UB_foco ≥ 1` nas **três** sementes. Uma semente só não reproduz.

## Checagem

- 78 linhas (39 control + 39 mipfocus1).
- Status 16 (`WorkLimit`) em todas as linhas experimentais. A guarda de parede não disparou.
- Nenhum intervalo de Γ neste arquivo.

## ΔUB por instância (controle − foco)

Valores de `mip_obj`. Positivo = incumbente melhor (menor) com `MIPFocus = 1`.

| Instância | Família | Δ 42 | Δ 43 | Δ 44 | Limiar (3 sementes) |
|---|---|---:|---:|---:|---|
| mapf-room-32-32-4-m10-f8.txt | mapf | 0 | 0 | 0 | não |
| pace18-t2-141-regiao-f4.txt | pace18 | 0 | 1 | 0 | não |
| puc-cc9-2p-seed-r1.txt | puc | 0 | 0 | 0 | não |
| pucn-cc3-10n-seed-r1.txt | pucn | 0 | 0 | 0 | não |
| puc-cc10-2u-seed-r1.txt | puc | 0 | 1 | −1 | não |
| puc-w23c23-seed-r1.txt | puc | −1 | −4 | 3 | não |
| puc-bip42p-regiao-f2.txt | puc | −2 | 0 | −1 | não |
| puc-bip42p-seed-r1.txt | puc | −1 | −1 | 0 | não |
| vienna-I056-regiao-f4.txt | vienna | −1 | 0 | 0 | não |
| puc-cc11-2u-seed-r1.txt | puc | 2 | −3 | 0 | não |
| vienna-I065-intercalado-f2.txt | vienna | −1 | −1 | 0 | não |
| vienna-I065-regiao-f4.txt | vienna | 0 | 0 | 0 | não |
| puc-cc12-2u-seed-r1.txt | puc | −1 | −1 | −2 | não |

Famílias em que o limiar reproduz: **nenhuma**.

Sinal pontual (uma semente, não conta): pace18 semente 43 (Δ=1); puc-cc10 semente 43 (Δ=1); puc-w23 semente 44 (Δ=3); puc-cc11 semente 42 (Δ=2). Em várias outras o foco piora o incumbente.

## LB (`mip_bound`)

O bound dual não sobe de forma sistemática. Casos visíveis: `puc-bip42p*` 33 → 34 nas três sementes (abaixo de uma estação no limiar de UB, e o fator testado é primal). `puc-cc9` semente 44: 30 → 29 (pior). Os restantes repetem o controle à tolerância numérica.

## Veredito do lado UB

O teste de um fator **não** atinge o limiar em duas famílias. Não há evidência reproduzível de folga primal corrigível só com `MIPFocus = 1` neste orçamento.
