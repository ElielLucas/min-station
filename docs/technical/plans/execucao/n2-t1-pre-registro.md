# N2-T1 — Pré-registro imutável do caminho B

**Congelado UTC:** `2026-10-09T03:17:03.483351+00:00`. **Caminho único:** `B / F-CC + K` (raiz apenas).
**Estado:** `FROZEN`; nenhum resultado N2 foi medido por este comando.

## Corpus prospectivo

| Instância | Família | Nível | n | m | B0 | LP completo F-CC+K |
|---|---|---:|---:|---:|---:|---:|
| `HB-q4-ndir2-p1` | `hb` | 1 | 16 | 6 | 1 | 2 |
| `BP-nao-[3,1]-q2` | `bp-nao` | 1 | 16 | 4 | 6 | 7 |
| `HB-q6-ndir2-p1` | `hb` | 2 | 26 | 10 | NOT MEASURED | NOT MEASURED |
| `BP-nao-[2,2,2]-q2` | `bp-nao` | 2 | 23 | 6 | NOT MEASURED | NOT MEASURED |

Nível 1: instâncias N1-T5 e seus hashes/LPs históricos; nível 2: geradores estruturais já existentes, acima do cap N1 `n_max=21`. 
Instâncias de nível 2 são **desenvolvimento estrutural**, não avaliação da partição benchmark-v1. 
Os códigos, parâmetros e hashes de dados por instância estão congelados em `experiments/alternative-formulations/n2-t1-freeze.json`.

## Orçamento e certificação

- **Orçamento total por instância:** `WorkLimit=164.0` unidades de trabalho do solver, com `Threads=4`, `Seed=42` e guarda de parede de `1800` segundos.
- Todos os subsolves consomem o mesmo orçamento total: não reiniciar um WorkLimit cheio para cada pricing.
- Registrar Wall time, pico de memória, custos de preparação, master, pricing, separação e verificação, número de colunas/cortes/chamadas e gap de pricing.
- `B0=max(LP COMP, core IP)` em instâncias comparáveis; nos casos grandes, calcular B0 sob o protocolo, jamais preenchê-lo com zero.
- Objetivo de master restrito de minimização é apenas valor de master restrito, **não** LB certificado.
- Certificação de um novo LB somente com pricing global exato demonstrando dual completo viável, ou bound incompleto demonstrado e revisado especificamente para F-CC+K.
- Com pricing interrompido: usar somente último limite válido previamente certificado (B0, quando validado) ou `UNCERTIFIED`.
- Arredondamento: `ceil(LB - 1e-6)` exclusivamente após certificação.

## Regressão N1

Há `23` controles de LP completo historicamente medidos (N1-T5/N1-T6). 
Antes do nível 2, pricing exato deve coincidir com enumeração do custo reduzido e o master convergido deve reproduzir cada LP conhecido até `1e-6`. 
Qualquer falha interrompe o nível 2.

## Gate e parada

- N2 PASS exige, conjuntamente: certificados válidos nos controles; ganho sobre B0 em HB e BP; reprodução em níveis 1 e 2; recuperação ≥50% do incremento positivo do LP completo nos casos conhecidos, dentro do orçamento total; custo compatível com a utilidade.
- Caso contrário N2 FAIL, incluindo ausência de certificado, custo excessivo ou falta de escala.
- No máximo uma mudança de representação, **somente** após diagnóstico escrito, sem novo pré-registro retrospectivo.
- Sem branch-and-price, N3, novos sintéticos ou alterações de baseline.

## Pré-condição pendente antes do código N2-T2B

Primal, dual, custo reduzido, pricing exato e eventual fórmula de limite com pricing incompleto devem ser revistos formalmente **antes da implementação**. A minuta está em `docs/technical/reference/formulacoes/n2-t2b-master-dual-pricing-revisao.md`.

## Proveniência

- SHA-256 do runner: `578c653d0182e93058673f78264936cd2e08f1320085236b34f8a74a9fbf38a3`.
- Hashes e parâmetros completos: `n2-t1-freeze.json`.
- Não sobrescrever este documento após os primeiros resultados N2.
