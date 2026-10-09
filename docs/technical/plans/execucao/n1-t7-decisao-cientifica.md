# N1-T7 — Decisão científica final do gate N1

**Data:** 2026-10-08 (America/Sao_Paulo).  
**Spec vinculante:** `specs/proxima-fase-n1-informacao-compatibilidade/spec.md`, seções **Gate / Promotion Criteria**, **Stop Criteria** e **Story 7**.  
**Decisão:** `PROMOTE FCC + EXISTING CUTS`  
**Única representação autorizada para investigação na N2:** **F-CC + K**, **caminho B** (geração de colunas na raiz, condicionada às pré-condições matemáticas e à certificação da spec N2).  
**Status epistemológico:** `SUPPORTED BY EXPERIMENT` para os ganhos observados no conjunto congelado; `COMPUTATIONALLY VERIFIED` para comparações e testemunhas indicadas; não há alegação de dominância global ou ganho de tempo.

## 1. Bases imutáveis da decisão

- Revisão MR-F3 `ACCEPTED`: `docs/technical/reference/formulacoes/revisao-mr-f3-n1.md`.
- Validação por instalação N1-T3: `results/alternative-formulations/n1-t3-validacao.csv`, além de `n1-t3-lp-invariantes.csv`. Nove instâncias, 878 instalações, zero discordâncias na bateria registrada.
- N1-T5, **18** casos pré-registrados: `experiments/alternative-formulations/n1-t5-freeze.json`, `results/alternative-formulations/n1-t5-diagnostico.csv`, `results/alternative-formulations/n1-t5-testemunhas.json`, `docs/technical/plans/execucao/n1-t5-diagnostico.md`.
- N1-T6, **3 pares/6 variantes**: `experiments/alternative-formulations/n1-t6-freeze.json`, `results/alternative-formulations/n1-t6-pares.json`, `results/alternative-formulations/n1-t6-certificados.json`, `results/alternative-formulations/n1-t6-diagnostico.csv`, `docs/technical/plans/execucao/n1-t6-diagnostico.md`. Todas as variantes estão marcadas `CERTIFIED`.
- Os hashes T5 usados para acionar T6 são conferidos contra `n1-t6-freeze.json`; os três hashes T6 estão identificados no relatório T6. Nada foi recertificado ou reotimizado na N1-T7.

**Interpretação de K e B0.** `K` é exatamente `prepare_cuts(..., active_cuts={'C1','C2','C4'})` (C4-DM), comum aos braços que o recebem, com hash por instância. `B0 = max(LP COMP, core IP)`. **core IP é um limitante inferior**, não uma solução primal. Os valores faltantes continuam `NOT MEASURED`, nunca zero.

## 2. Categoria aprovada — `PROMOTE FCC + EXISTING CUTS`

A condição pré-registrada exige `Γ > 0`, `Δ_FCC+K = z_FCC+K − B0 > 1e-6` em **ao menos duas estruturas distintas**, além de uma testemunha de complementaridade entre K e a formulação por configurações.

| Linha do CSV N1-T5 | Família (`tipo`) | Γ | B0 | LP F-CC+K | OPT | Δ_FCC+K |
|---|---|---:|---:|---:|---:|---:|
| `Sec59(L=7)` | `sec59` | 5 | 3,666667 | 5 | 7 | +1,333333 |
| `HB-q4-ndir2-p1` | `hb` | 1 | 1 | 2 | 2 | +1 |
| `HB-q5-ndir2-p1` | `hb` | 2 | 1,083333 | 3 | 3 | +1,916667 |
| `BP-nao-[3,1]-q2` | `bp-nao` | 1 | 6 | 7 | 7 | +1 |

São **quatro casos, em três famílias de construção distintas** (`sec59`, `hb`, `bp-nao`); as duas instâncias HB contam como **uma** estrutura. A categoria satisfaz o limiar de duas estruturas, mesmo sem considerar N1-T6.

**Testemunha específica de mecanismo — `Sec59(L=7)`:** o vetor `y*` ótimo do LP F-CC (valor **4,5**) viola o corte congelado de K associado a `Z={t1,w1}`: `Σ_{v∈Z}y*_v = 0,5 < 1`. Com K, o LP F-CC+K vale **5**. O vetor, o corte e a violação constam de `results/alternative-formulations/n1-t5-testemunhas.json` (`COMPUTATIONALLY VERIFIED`). Há ainda uma testemunha K para `SharedTerminal`, mas seu `Γ=0`; ela **não** é contada para o critério de estruturas com `Γ>0`.

**Limite da evidência:** as linhas HB/BP demonstram ganho de F-CC+K sobre B0, mas não demonstram que K *isoladamente* cause esse ganho: nelas, LP F-CC e LP F-CC+K são iguais. A complementaridade estrita com K foi efetivamente documentada em `Sec59`. Não atribuir o ganho completo de HB/BP aos cortes K isoladamente.

## 3. Categorias não aprovadas

### `PROMOTE FCC + C3` — não atende aos critérios

Para esta categoria, a regra exige `Δ_trio = LP F-C3+K − LP F-CC+K > 1e-6` em **duas famílias distintas** e ao menos um caso com `core IP < OPT` e `LP F-CC+K < OPT`.

| Origem | Linha | Família | core IP | OPT | LP F-CC+K | LP F-C3+K | Δ_trio |
|---|---|---|---:|---:|---:|---:|---:|
| N1-T5 | `Tri` | `tri` | 2 | 2 | 1,5 | 2 | +0,5 |
| N1-T6 | `T6-TRI-01-obstruction` | `tri` | 2 | 2 | 1,5 | 2 | +0,5 |

Existem **duas linhas com ganho**, porém **uma única família (`tri`)**. Além disso, nas duas linhas `core IP = OPT`; nenhuma delas cumpre o requisito adicional `core IP < OPT`. Não são evidência suficiente para promover a formulação com redes de trios.

Resultados negativos relevantes: `Sec59(L=7)` tem `Δ_trio = 0`; `T6-SEC59-01-obstruction` também tem `Δ_trio = 0`, embora tenha `OPT=4` e `LP F-CC+K=3,5`. A variante F2 da T6 não registra ganho de trios. Os casos excluídos por cap na T5 permanecem `NOT MEASURED`, sem inferência negativa.

**Conclusão sobre F-C3:** mantê-la como resultado matemático e computacional delimitado; o reforço é real na família `tri`, mas não satisfaz a promoção congelada. Não iniciar uma campanha adicional de F-C3 na N1.

### `PROMOTE PROJECTED COMPATIBILITY INEQUALITY` — não atende aos critérios

Não foi apresentada nesta rodada uma família de desigualdades projetadas com **prova geral de validade**, teste exaustivo por instalação, ganho em duas estruturas e testemunha de um ponto que satisfaça C1/C2/C4-DM/C5/C6 e a viole. Não inferir existência de tal família a partir dos cortes K ou da diferença entre LPs. Categoria **não qualificada por ausência dos requisitos de evidência**.

## 4. Aplicação literal do gate e do desempate

1. Definições matemáticas: revisão MR-F3 aceita e N1-T3 testada; as alegações continuam limitadas às provas documentadas e ao conjunto verificado.
2. Mecanismo específico: testemunha `Sec59` de K violado por um ótimo F-CC, com ganho LP medido.
3. Ganho em estruturas distintas: `sec59`, `hb`, `bp-nao` satisfazem `Γ>0` e `Δ_FCC+K>0`.
4. F-C3: somente `tri`, e `core IP = OPT` nos ganhos observados; falha em suas duas condições específicas.
5. Desigualdade projetada: sem prova, teste e testemunha exigidos; não qualificada.
6. **Desempate de 50%:** **não acionado**, pois somente uma categoria se qualificou. Não há comparação hipotética entre categorias nem escolha ad hoc.

**Saída única do gate:** `PROMOTE FCC + EXISTING CUTS`.

## 5. Efeito sobre a N2 e regras de parada

- **N1-T7:** encerrada como decisão documental fundamentada por evidências pré-existentes; nenhuma medição nova foi criada.
- **N2:** a condição de ativação da spec `specs/proxima-fase-n2-limite-compatibilidade-certificado/spec.md` está satisfeita **para o caminho B, F-CC + K**, sem a variante de trios. A implementação N2 **ainda não está autorizada a saltar** as próprias etapas de pré-registro e derivação/revisão do master, dual, custo reduzido e pricing.
- **N2-T1:** próximo trabalho permitido: ativação formal e pré-registro dos dois tipos estruturais e níveis de tamanho, orçamento (`WorkLimit`), controles e critério de recuperação de pelo menos 50%, **antes** de qualquer resultado N2.
- **N2-T2B:** formulação e revisão escrita do primal/dual, pricing e certificação antes de código. **Uma solução de master restrito não é, por si, um limitante inferior certificado.**
- **N3, R9, benchmark-v1, branch-and-price e N4:** continuam bloqueados/não abertos de acordo com as specs vigentes.
- Não criar mais pares, seeds, desigualdades ou campanhas para tentar alterar a seleção desta rodada.

## 6. Reprodutibilidade da decisão

Na raiz do repositório, executar:

```bash
PYTHONHASHSEED=0 python experiments/alternative-formulations/verify_n1_t7_gate.py
```

O verificador somente **lê** os CSVs/JSONs, confere hashes e estados, recompõe os indicadores e exige que o presente registro contenha exatamente a decisão obtida. Não requer Gurobi e não sobrescreve arquivos congelados. A interpretação de ausência de prova de desigualdade projetada está explicitamente declarada nesta decisão e não é substituída por um detector automático.

**Limitação geral:** a decisão seleciona a informação para pesquisar na N2; não demonstra escalabilidade, economia de tempo, superioridade universal de F-CC+K, nem estabelece um novo bound certificado por geração de colunas.
