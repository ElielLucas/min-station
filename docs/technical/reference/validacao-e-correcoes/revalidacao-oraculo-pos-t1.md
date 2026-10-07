# Revalidação dos experimentos que usaram o oráculo (T4)

**Data:** 2026-10-03
**Oráculo corrigido:** arco de permanência `v_out → v_in` em `experiments/cuts/cuts.py` (`integer_oracle` e `_build_flow_net_aggregate`).

Critério, o mesmo da spec: um experimento é candidato se chama, direta ou indiretamente, `integer_oracle`, `separate_classical_fracs`, `solve_cbi`, `solve_bc_yspace`, `solve_lp_cutting_plane` ou `solve_ip_yspace`, e se rodou em ao menos uma instância com `S∩T ≠ ∅` (`rho_S_inter_T > 0` no manifesto).

O defeito só muda a viabilidade quando a permanência é necessária e não há troca por aresta. Uma instância com sobreposição e com arestas pode continuar bem classificada pela rede antiga, como `make_StayPut`.

## Quem chama o oráculo

| Script | Função | Instâncias com `S∩T ≠ ∅` | Decisão |
|---|---|---|---|
| `experiments/cuts/run_e2.py` | `solve_lp_cutting_plane`, `solve_ip_yspace` | não; lote antigo, `rho = 0` | não afetado |
| `experiments/cuts/run_e6.py` | `solve_bc_yspace` | não | não afetado |
| `experiments/cuts/run_e7.py` | `solve_bc_yspace` | não | não afetado |
| `experiments/cuts/run_e8.py` | `solve_bc_yspace`, `solve_cbi` | não; Chicago, Barcelona, Philadelphia, hc9u, hc10p, bip42p, cc12-2p | não afetado |
| `experiments/benchmark/run_e9.py` | `solve_ip_yspace` | sim: `mapf-den312d-m50-f2-rho`, `mapf-room-32-32-4-m25-f4-rho`, `puc-w23c23-intercalado-f2-rho` em `results/benchmark/e9_raiz_fatia3.csv` | candidato; ver abaixo |
| `experiments/benchmark/run_e10.py` | `primal.py` → `integer_oracle` | sim: as duas MAPF `-rho` em `e10_primal_fatia2.csv` | candidato; ver abaixo |
| `experiments/benchmark/run_e10b.py` | `solve_ip_yspace` e `integer_oracle` | sim: as mesmas duas MAPF `-rho` | candidato; ver abaixo |
| `experiments/benchmark/run_e12.py` | `solve_cbi` | não; o CSV não contém nome `-rho`, e o relatório registra `S∩T` vazio | não afetado |
| `run_e0.py`, `run_e1.py`, `run_e1prime.py`, `run_e4.py` | não chamam as funções acima | — | não afetado |
| `run_e13.py`, `run_e14.py` | `measure_mip` no compacto, sem oráculo | têm linhas `-rho`, mas não entram no critério | não afetado |

As cinco principais com `rho_S_inter_T > 0` são `mapf-den312d-m50-f2-rho`, `mapf-room-32-32-4-m25-f4-rho`, `puc-w23c23-intercalado-f2-rho`, `b-b09-intercalado-f2-rho` e `i-i160-301-intercalado-f2-rho`. As duas últimas são classe F e não aparecem nos CSVs de E9, E10 ou E10b.

## Candidatos: por que não houve reexecução

O veredito publicado não depende do resultado do oráculo nessas linhas.

- **E9.** `resultados-e9-e10-pli.md` §6 diz que nenhuma conclusão do relatório depende de `den312d-m50` nem de `room-m25-rho`. As leituras por família são medianas. `w23c23-intercalado-f2-rho` é classe F, fora das D/A que sustentam o texto.
- **E10.** Os construtores perdem para o incumbente do Gurobi em 29 de 30 D/A e em 13 de 13 MAPF/Vienna. Um falso negativo do oráculo só piora o primal. Corrigi-lo pode melhorar no máximo as duas linhas `-rho`. Isso não transforma o resultado em evidência de um primal robusto, que é o que o relatório recusou.
- **E10b.** A única vitória contra o UB do COMP é `w23c23-seed`, sem sobreposição (`resultados-e9-e10-pli.md` §4). As linhas `-rho` não são essa vitória. O veredito continua inconclusivo sem elas.
- **E12.** Fora do conjunto. Controles MAPF sem `-rho`. A2 encerrada para Das não usa instância com sobreposição.

Nenhuma linha foi substituída. Nenhum número antigo foi declarado obsoleto por causa deste defeito. Os números afetados pelo C4-DM inválido continuam registrados em `correcao-c4-dm.md`; isso é outro defeito, já corrigido, e não é o oráculo de permanência.

## Listas

**Não afetado.** E0, E1, E1', E2, E4, E6, E7, E8, E12, E13, E14.

**Candidato, sem reexecução, justificativa acima.** E9, E10, E10b.

**Reexecutado.** nenhum.

**Substituído.** nenhum.
