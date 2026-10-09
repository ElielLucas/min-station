# N2-T2B — Gate M: decisão de autorização matemática para implementação

**Estado:** `APROVADO PARA IMPLEMENTAÇÃO` — Gate M autorizado expressamente pelo pesquisador responsável em 2026-10-09. **Não equivale ao Gate O nem a aprovação de resultados experimentais.**  
**Preparado em:** 2026-10-09 (America/Sao_Paulo).  
**Escopo da decisão:** exclusivamente N2-T2B, caminho B (`F-CC+K`), geração de colunas na raiz.  
**Gate posterior:** Gate O, aceite operacional da implementação, distinto da autorização matemática aqui tratada.

## 1. Objeto exato submetido à decisão

| Fonte | Identificação e finalidade |
|---|---|
| Revisão matemática | `docs/technical/reference/formulacoes/n2-t2b-master-dual-pricing-revisao.md`, **v2.1**, SHA-256 `db1fb71b6e4afba421ccc9f8d4f244aee6700edb886dc1c0219ed7e812aa9237` |
| Parecer independente | `docs/technical/reference/formulacoes/parecer-independente-N2-T2B.md`, SHA-256 `32a62d416e994de1d58f31e1d3b3aa61bf8d365e223025273728d52b9559a888`, veredito `ACCEPTED WITH CONDITIONS` |
| Spec vinculante | `specs/proxima-fase-n2-limite-compatibilidade-certificado/spec.md` |
| Seleção N1 | `docs/technical/plans/execucao/n1-t7-decisao-cientifica.md`: `PROMOTE FCC + EXISTING CUTS` |
| Pré-registro congelado | `docs/technical/plans/execucao/n2-t1-pre-registro.md` e `experiments/alternative-formulations/n2-t1-freeze.json` |
| Definição dos gates | Revisão matemática v2.1, §§11.1, 11.2, 12.1 e 12.2 |

**Regra de integridade:** antes da assinatura, conferir novamente o SHA-256 da revisão matemática. Se não coincidir, esta minuta **não** autoriza a versão alterada; reavaliar o objeto e registrar sua nova identificação, sem aproveitar automaticamente a aprovação anterior.

## 2. Verificação dos pré-requisitos do Gate M

| ID | Critério | Evidência registrada | Estado para decisão |
|---|---|---|---|
| M-1 | N1-T7 selecionou F-CC+K; freeze N2-T1 íntegro | Decisão N1-T7; nesta preparação, `run_n2_t1.py check` retornou `PASS: N2-T1 freeze íntegro; caminho B; 2 famílias x 2 níveis; orçamento total 164 Work` | **Verificado na preparação; reconferir ao aprovar** |
| M-2 | Primal, dual, custos reduzidos, pricing e Teorema L formalizados e submetidos a revisão independente | Revisão v2.1 §§2–6; parecer de 2026-10-09 aceita o núcleo matemático com condições | **Documentado** |
| M-3 | Achados R-01 a R-10 incorporados ou encaminhados explicitamente à etapa de implementação pertinente | Matriz da revisão v2.1, §8.2; não exige concluir testes sobre código inexistente | **Documentado** |
| M-4 | Contrato de certificação fixado previamente à implementação | Revisão v2.1 §§5.3, 6.3–6.5: política ENUM, limites globais verificáveis, MIP numérico `UNCERTIFIED` e interrupções | **Documentado** |
| M-5 | Controles matemáticos prévios sem falhas, com limitações registradas | Pesquisador executou em 2026-10-09 `python -m unittest discover -s experiments/alternative-formulations -p test_n2_t2b_controles_matematicos.py -v`: **18 testes, `OK`, zero skipped, 2,612 s**, incluindo casos com Gurobi; evidência informada pelo pesquisador, não reexecutada nesta preparação | **Evidência informada; conferir se necessário** |
| M-6 | Responsável humano registra decisão expressa, data, escopo e condições | Seção 5 deste documento | **APROVADO — manifestação humana expressa registrada na seção 5** |

**Distinção importante:** os 18 testes são controles matemáticos prévios. Não representam aprovação do código futuro, execução das regressões N2-T4 nem medição N2-T5. A confirmação de M-1 a M-5 e a decisão de M-6 pertencem ao responsável pelo Gate M.

## 3. Escopo que uma eventual aprovação autoriza

Com a decisão humana **`APROVADO PARA IMPLEMENTAÇÃO`** registrada na seção 5, fica autorizado:

1. Implementar **master restrito F-CC+K**, com colunas `q=(W,I,J)`, pares diretos, variáveis `y`, cortes K congelados e limites superiores, fiel à revisão v2.1.
2. Extrair e conferir dual e custos reduzidos, incluindo `η` reconstruído de `μ,κ` quando necessário; registrar convenção de sinais e tratamento de `S∩T`.
3. Implementar pricing por configurações admissíveis com conectividade de `H=G^r`, elegibilidade, balanço e validação combinatória de toda coluna adicionada; classificar cada chamada como `exact` ou `heuristic` e guardar status e evidências.
4. Implementar **geração de colunas somente na raiz**, começando por RMP viável, adicionando colunas negativas verificadas e reotimizando; registrar custos e parâmetros dos subsolves, sem tratar `z_R` como LB certificado.
5. Criar e executar testes de integração de master, dual, pricing, coluna e política de saída para subsidiar o **Gate O** posterior.

**Restrições vinculantes:**

- `ObjBound` e `ObjBoundC` de MIP numérico, mesmo finitos ou sob `OPTIMAL`, **não** produzem `CERTIFIED` isoladamente.
- Pricing heurístico pode propor colunas; não prova ausência de novas colunas.
- Um limite global `ℓ` só sustenta certificação quando sua validade para **todo** `Q` estiver demonstrada e calculada com aritmética segura; ENUM certificador exige enumeração completa, vetor racional consistente, cálculos rigorosos e exportação conservadora.
- Até implementação/verificação da N2-T3, nenhuma rotina nova deve publicar `LB_CG` como `CERTIFIED` sem satisfazer integralmente esse contrato. `UNCERTIFIED` é o padrão seguro.
- Não modificar N1, freeze N2-T1, orçamento, partições, cortes K, baseline, `fcc.py`, `fcc_k.py` ou convenções científicas congeladas.
- Não implementar caminho A, trios, branch-and-price, branching, cortes novos ou experimentos N2-T5. Não fazer commit sem autorização expressa do usuário.

## 4. O que **não** é condição de entrada do Gate M

Estas entregas são posteriores e **não devem bloquear a decisão matemática por dependerem de código ainda não escrito**:

| Etapa | Entrega posterior |
|---|---|
| N2-T2B / Gate O | Código do RMP, pricing e ciclo de colunas, testes sobre funções reais, rastreabilidade operacional e aceite do algoritmo |
| N2-T3 | Certificação efetiva ENUM/N1/N2, `U` validado para convergência G2, `H-K`, tratamento de `B0` e interrupções |
| N2-T4 | Regressão prospectiva contra os **23 controles N1**, com tolerância e premissas da spec |
| N2-T5 | Campanha experimental pré-registrada e contabilização de **todo** Work |
| N2-T6 | Decisão científica `N2 PASS` ou `N2 FAIL` |

Uma autorização matemática não substitui o Gate O, não comprova escalabilidade, não certifica limites inferiores produzidos pela futura implementação e não altera os stop criteria.

## 5. Decisão formal — manifestação expressa do responsável

**Decisão:** `APROVADO PARA IMPLEMENTAÇÃO` (Gate M).  
**Data:** 2026-10-09 (America/Sao_Paulo; hora exata não registrada nesta evidência).  
**Responsável:** pesquisador responsável pelo projeto MIN-STATION, que manifestou a autorização diretamente nesta conversa. Não foi atribuída assinatura digital ou identidade nominal não comprovada.  
**Evidência da decisão:** manifestação expressa do responsável: **“cara. já não está claro que eu aprovei? vamos. vamos seguir”**, após a apresentação do Gate M e dos respectivos limites. Esta documentação transcreve a decisão humana; não a substitui por inferência de uma IA.

| Campo | Registro |
|---|---|
| Objeto autorizado | `n2-t2b-master-dual-pricing-revisao.md` **v2.1**, SHA-256 **`db1fb71b6e4afba421ccc9f8d4f244aee6700edb886dc1c0219ed7e812aa9237`** |
| Parecer aceito como condição | `parecer-independente-N2-T2B.md`, SHA-256 **`32a62d416e994de1d58f31e1d3b3aa61bf8d365e223025273728d52b9559a888`**, `ACCEPTED WITH CONDITIONS` |
| M-1 | **CONFIRMADO**: freeze N2-T1 validado novamente na preparação desta atualização, `PASS`, caminho B, 2 famílias × 2 níveis, 164 Work |
| M-2 | **CONFIRMADO**: derivação do master, dual, pricing e Teorema L submetidos ao parecer independente |
| M-3 | **CONFIRMADO documentalmente**: rastreabilidade R-01 a R-10 da revisão v2.1, sem exigir implementação futura |
| M-4 | **CONFIRMADO documentalmente**: política de certificação e interrupções definida; cumprimento pelo software permanece pendente |
| M-5 | **CONFIRMADO como evidência informada pelo pesquisador**: 18 testes `OK`, 0 `skipped`, Gurobi disponível em seu ambiente (resultado colado na conversa; testes não reexecutados integralmente nesta preparação) |
| M-6 | **CUMPRIDO**: aprovação humana expressa, escopo restrito e data registrados neste arquivo |
| Resultado | **`APROVADO PARA IMPLEMENTAÇÃO` — Gate M** |
| Ressalvas bloqueantes da etapa matemática | Nenhuma identificada para iniciar código **dentro do escopo**; condições numéricas/operacionais continuam obrigatórias |
| Gate O | **PENDENTE**, após implementação e verificação dos controles correspondentes |

### Alcance e condições da autorização

Aprova-se **somente o início do desenvolvimento** do caminho B (F-CC+K, raiz), começando pela entrega isolada
`n2-t2b-implementacao-master-dual.md`. A aprovação **não** transforma `ACCEPTED WITH CONDITIONS` em aceite irrestrito,
não autoriza o rótulo `CERTIFIED` para pricing MIP numérico, não autoriza experimentar, alterar baseline ou congelamentos,
nem declara o algoritmo ou os limites operacionais validados. As condições da seção 3 são parte integrante desta decisão.

O documento matemático v2.1 mantém, como fotografia histórica anterior a esta decisão, a palavra `PENDENTE` na
seção de Gate M. **O estado atualizado e documentalmente vigente do gate é este registro
separado.** O documento matemático não deve ser editado para corrigir apenas seu cabeçalho, porque isso alteraria
o SHA-256 exato do objeto aprovado.

**Próxima execução autorizada:** implementar o master restrito e a extração/validação do dual em módulo próprio,
com testes, conforme `n2-t2b-implementacao-master-dual.md`. Pricing e ciclo completo de geração de colunas
permanecem etapas subsequentes da **mesma autorização geral**, sujeitas a validação incremental.

## 6. Comandos para conferir/reproduzir a integridade da autorização

Na raiz do repositório:

```bash
sha256sum docs/technical/reference/formulacoes/n2-t2b-master-dual-pricing-revisao.md
sha256sum docs/technical/reference/formulacoes/parecer-independente-N2-T2B.md
PYTHONHASHSEED=0 python experiments/alternative-formulations/run_n2_t1.py check
PYTHONHASHSEED=0 python -m unittest discover -s experiments/alternative-formulations -p test_n2_t2b_controles_matematicos.py -v
```

Esperado para os dois SHA-256: os valores exatos indicados na seção 1. Se qualquer comando falhar em uma verificação posterior, registrar a divergência, suspender uso da revisão afetada e investigar antes de prosseguir. Não executar `freeze` novamente, não sobrescrever os arquivos congelados e não ajustar os thresholds para obter aprovação.
