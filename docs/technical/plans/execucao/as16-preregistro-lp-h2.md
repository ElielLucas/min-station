# AS16 — Pré-registro imutável do piloto LP com H2

**Estado:** congelado antes da execução de novos LPs. **Nenhuma medição Gurobi foi realizada nesta entrega.**  
**Fonte:** AS-00 (`experiments/benchmark/as00_protocol.py`, protocolo `AS00-2026-10-11-v1`).  
**Manifesto legível por máquina:** [`as16-preregistro-lp-h2.json`](as16-preregistro-lp-h2.json).  
**SHA-256 do JSON de pré-registro:** `4056fd08244a15085367a60a0c71fbfc3f44fc2d2f0a7686fdd31063b1de2dfe`.

## Instâncias de desenvolvimento congeladas

| Nome sem `.txt` | SHA-256 dos bytes de origem | Identidade do grafo bruto |
|---|---|---|
| `puc-cc9-2p-seed-r1` | `0312f43552cddc102081d9937465429e29797ddb86cf85a6871752d50aeec88c` | `puc:cc9-2p` |
| `puc-bip42p-regiao-f2` | `d7c53596522401d4071563d5007d9c8647ee0d37c893426b5ab3b1d65d97743a` | `puc:bip42p` |
| `pucn-cc3-10n-seed-r1` | `9123c0e46228c22ba586bb7f730757a7fa2c4b0f815b54afba59f54a3bc8b431` | `pucn:cc3-10n` |
| `mapf-room-32-32-4-m10-f8` | `78be3e1261f31f4e583d0808bdfc9c93d9c9eb335d86d13b059ce428af5f303f` | `mapf:map:raw-data/mapf/maps/room-32-32-4.map` |
| `vienna-I056-regiao-f4` | `645da5115a0eeaa6fba9eeae9f4942aebecfa66c4bcbc7aaec2bd0c994eb0ccc` | `vienna:I056` |
| `puc-w3c571-seed-r1` | `e85ced7daef779e6e88f302ee9d80a467129f448a7ac5c6ce465d64b963300fd` | `puc:w3c571` |

A identidade do **grafo bruto**, não a igualdade de `A_r`, determina independência. Os seis casos foram selecionados pelo AS-00 e permanecem exclusivamente na partição `desenvolvimento`. Não tocar nas 17 instâncias de avaliação nem nos resultados congelados.

## Tratamentos: braços pareados

| Braço | COMP/U | K aplicado ao LP | H2 aplicado ao LP | Preparação de K contabilizada |
|---|---|---|---|---|
| `U` | Sim | Não | Não | Sim, para política comparável |
| `U_K` | Sim | Sim | Não | Sim |
| `U_H2` | Sim | Não | Sim, por separação certificada | **Sim**, inclusive para orientar suportes |
| `U_K_H2` | Sim | Sim | Sim, por separação certificada | Sim |

Controles algébricos **adicionais**, explicitamente *post hoc*: `U_FIXED_H2` e `U_K_FIXED_H2`. O pool por instância reúne cortes H2 com certificados emitidos nos dois braços on-line; ambas as reotimizações usam o **mesmo pool**, sem escolher cortes específicos com base no resultado do controle. Esse pool não é validação fora da amostra. Os tempos de construção do pool já constam dos braços on-line; não são atribuídos gratuitamente aos resultados desses braços.

## Orçamento e decisões pré-registrados

- Pareamento: mesmos arquivos, fonte, parâmetros, seed `42`, `Threads=4`, `Method=1` (dual simplex), `NumericFocus=1`, tolerâncias `1e-6` e presolve Gurobi padrão.
- Relógio absoluto: **90 s por braço**, incluindo partida do processo, leitura, alcance, cálculo dos K, montagem, LP inicial, seleção de R, chamadas de certificação AS14 e reotimização. O worker é interrompido ao esgotar o orçamento.
- Limite de memória no solver: `MemLimit=16 GiB`; não declarar como uma medida da memória efetivamente usada. Cap de segurança pré-registrado: 1.000.000 de variáveis na compilação. Acima do cap, registrar `NOT_MEASURED_CAP`.
- Separação H2: até 12 suportes, 24 uniões de pares, 120 chamadas ao oráculo, 120 candidatos examinados por suporte, 8 cortes; orçamento de 18 s de certificação por braço e 4 s por suporte, sempre limitados pelo relógio global. Violação mínima `1e-7`.
- Corte H2 só entra após certificado conservador AS14/AS15. Sem cortes válidos/violados significa `NO_CUT`, nunca que todos os cortes possíveis foram esgotados.
- Separar objetivo LP ótimo do controle, objetivo da reotimização e `time_to_first_lp_s`; registrar fases `load_and_reachability_s`, `k_preparation_s`, `model_construction_s`, `gurobi_build_s`, `lp_base_optimize_s`, `support_selection_s`, `h2_certification_s`, `lp_reoptimization_s` e `elapsed_wall_s`.
- `GO` exploratório exige ganho relativo LP marginal contra `U_K` de ao menos **1% em ≥2 grafos brutos distintos**, com ao menos um deles alcançando custo de parede de `U_K_H2` **≤ 2× o custo de `U_K`** e **≤90 s**. Esses limiares são premissas experimentais pré-registradas, não conclusões científicas.
- `STOP` quando todos os quatro braços e controles de pool fixo terminarem ótimos em todos os seis casos, mas o gate falhar. `INVESTIGATE` em caso de dados ausentes, censurados ou controles não executados; o gate é conservador.
- Somente `OPTIMAL` do LP produz um objetivo comparável; `TIME_LIMIT`, `UNKNOWN`, `ERROR`, `NOT_MEASURED_MEMORY` e `NOT_RUN` preservam objetivo ausente. Status `OPTIMAL` é numérico, não certificado racional.

## Reproduzir

Na raiz do repositório, com Poetry/Gurobi/licença habilitados:

```bash
# Validação estrutural sem solver, sem sobrescrever saídas existentes
python experiments/cuts/run_h2_lp.py \
  --output-dir results/benchmark/as16-prereg-smoke-01 \
  --cases puc-cc9-2p-seed-r1 puc-w3c571-seed-r1 --dry-run

# Piloto LP completo (24 braços on-line e até 12 controles pool fixo)
python experiments/cuts/run_h2_lp.py \
  --output-dir results/benchmark/as16-lp-h2-001

# Reanálise de uma execução existente
python experiments/cuts/analyze_h2_lp.py \
  --run-dir results/benchmark/as16-lp-h2-001

# Suite de testes sem necessidade de Gurobi
python -m unittest discover -s experiments/cuts -p 'test_as16_lp.py' -v
```

Cada execução escreve `manifest.json`, `rows.json`, `analysis.json` e (se houver cortes certificados) um `*-pool.json` por instância. O diretório de saída precisa **não existir**. A marcação de caso `--cases` permite apenas subconjuntos das seis instâncias do piloto; resultados de smoke nunca autorizam o gate `GO`. Qualquer alteração de orçamento, grafo, parâmetro, cut/heurística ou threshold exige novo pré-registro versionado, não edição retrospectiva.

## Integridade e limites

O runner valida o SHA de `instances/manifest.csv`, `instances/benchmark-v1/spec.csv`, as seis fontes físicas e os arquivos AS13–AS15 e `as02_model_a.py` congelados no JSON. `source_commit` só é preenchido se existir um repositório Git; em ZIP sem `.git`, fica `null`, e **não** é inventado.

Não substituir a análise numérica por estimativas, resolver MIP, aplicar Formulação C, alterar K, modificar N1/N2/FC ou promover AS17 automaticamente. Revisão independente humana permanece separada dos testes automatizados.
