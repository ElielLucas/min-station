# Fase E — SC, registro anterior à avaliação

**Data:** 2026-10-03
**Decisão que autoriza:** `decisao-fase-p.md`. Só SC foi promovida.

Congelado antes do primeiro `optimize` de avaliação.

- Escalas acima do piloto: `k ∈ {8, 9}`.
- GF2, uma instância por escala. Gêmeo rígido nas sementes de geração 100, 101, 102, 103 e 104. Nenhuma dessas sementes está em {0, 1}.
- O par GF2/gêmeo de cada escala fica inteiro na avaliação. Não há fatia de desenvolvimento nesta rodada.
- Sementes de solver 42, 43 e 44.
- Métodos: base, COMP (C1+C2+C4), núcleo inteiro, COMP+C6. Os mesmos do piloto.
- `WorkLimit = 297`, `TimeLimit = 1800` só como guarda, 4 threads, sem MIP start.
- Métricas as do piloto.
- O ótimo do gêmeo continua saindo do IP de set cover. Sem prova em 90 s a célula não entra, e o MIN-STATION não substitui o certificado.
- `k = 8` monta: 765 vértices, 195330 arcos de alcance, 7 s nesta máquina. `k = 9` entra se a montagem terminar; se não terminar, o fato fica registrado e a escala não é substituída por outra.

## Medição posterior ao registro

`experiments/structural/fase_e.py` terminou em 2026-10-03. CSV: `results/structural/fase_e_sc.csv`, 24 linhas.

Os dez gêmeos, `k ∈ {8, 9}` e sementes 100–104, saíram antes de qualquer solve: o IP de set cover não provou o ótimo em 90 s. A comparação de simetria não foi avaliada nessas escalas.

No GF2, nas duas escalas e nas três sementes de solver, o quadro é o mesmo. A base para com incumbente `k` e limite 1, num nó. O COMP para com incumbente `k` e limite 2 ou 3, num nó. COMP+C6 fica no mesmo intervalo, com limite 2, 3 ou 4. O núcleo prova `OPT = k` num nó (trabalho entre 0,92 e 8,96). Status 16 é o `WorkLimit`.

| Escala | Sementes | Base | COMP | Núcleo | COMP+C6 |
|---|---|---|---|---|---|
| k=8 | 42, 43, 44 | UB 8, LB 1, status 16 | UB 8, LB 3, status 16 | OPT 8, 1 nó | UB 8, LB 3 ou 4, status 16 |
| k=9 | 42, 43, 44 | UB 9, LB 1, status 16 | UB 9, LB 2 ou 3, status 16 | OPT 9, 1 nó | UB 9, LB 2 ou 3, status 16 |

O fenômeno do piloto se repete nas duas escalas acima e nas três sementes: o incumbente `k` aparece, a base e o COMP não provam, o núcleo prova na raiz do modelo de `y`. Em `k = 7` o COMP ainda provava; em `k = 8` e `k = 9` também para no orçamento, sem sair do nó raiz.
