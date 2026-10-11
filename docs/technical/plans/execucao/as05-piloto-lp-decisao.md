# AS-05 — Piloto LP e gate de continuidade

**Estado:** implementação preparada; **campanha Gurobi NÃO EXECUTADA**.  
**Dependências:** AS-00..AS-04, com AS-01/AS-02/AS-04 sujeitos a revisão independente.  
**Plano prospectivo:** gerado por `run_as05_pilot.py --init-plan`, sem sobrescrever `results/benchmark/protocol.json`.

## Hipótese e desenho experimental

Testar se a **partição automática da AS-03**, aplicada à formulação A2+K, fortalece de maneira material a relaxação LP de U+K, separando o ganho dos cortes (`U` × `U_K`) e da formulação (`U_K` × `A2_K`). Seis instâncias de **desenvolvimento**, sem consulta a resultados de avaliação, definidas no pré-registro AS-00:

1. `mapf-room-32-32-4-m10-f8`
2. `puc-bip42p-regiao-f2`
3. `puc-cc9-2p-seed-r1`
4. `puc-w3c571-seed-r1`
5. `pucn-cc3-10n-seed-r1`
6. `vienna-I056-regiao-f4`

A ordem de execução é a do pré-registro `pilot_cases`. Cada braço tem **90 s de parede**, incluindo carregamento, cálculo de alcance, K, construção e solução, **4 threads**, limite de memória declarado de **16 GiB** e **sem warm start**. O backend de campanha é Gurobi; o smoke sintético não usa solver. Seeds: **42** (base); **43 e 44** para confirmar pares com ganho candidato. **A política de agrupamento permanece com seed 42** em todas as reproduções; mudar a seed do solver não deve mudar simultaneamente os grupos. Qualquer divergência de partição/identidade impede inferência.

## Adendo prospectivo de materialidade

O AS-00 congelado exige ganho reprodutível em **pelo menos dois grafos brutos independentes**, benefício em tempo e ausência de regressões graves, mas **não definiu números** para a palavra “material”. Para tornar o gate verificável, esta implementação propõe no plano AS-05, **antes de resolver as seis instâncias**:

| Condição | Valor proposto no adendo AS-05 |
|---|---:|
| Ganho relativo mínimo A2+K contra U+K | **1%** |
| Tolerância LP absoluta e relativa | **1e-6** cada |
| Razão máxima de tempo ponta a ponta A2+K/U+K | **3,0** |
| Grafos brutos distintos com ganho repetido | **≥ 2** |
| Fontes independentes de grafos (`mapf`, `puc`, `pucn`, `vienna`) | **≥ 2** |
| Seeds obrigatórias para reproduzir ganhos candidatos | **42, 43, 44** |

Esses valores **não são números atribuídos ao Astra ou ao AS-00**. São uma **proposta de decisão prospectiva da AS-05**: revisar a adequação científica, fixar no arquivo do plano e registrar o hash **antes** da primeira rodada. Caso se alterem após observar LP, gerar novo adendo e registrar desvio; não substituir retrospectivamente o plano original. O ganho relativo é `(z_LP(A2+K) − z_LP(U+K)) / max(|z_LP(U+K)|, 1)`.

### Decisão

- **GO:** seis casos completos e comparáveis; nenhum caso com regressão de dominância LP além da tolerância; nenhum caso pareado com razão de tempo acima de 3; ao menos dois grafos **e duas fontes** distintos com ganho material **reproduzido** nas seeds 43/44. Passar o gate não substitui a revisão matemática.
- **STOP:** dados completos, mas ganhos insuficientes, sem reprodução, ou custo além do limite.
- **INVESTIGATE:** ao menos um caso censurado, ausência de reprodução exigida, inconsistência de dominância numérica ou impossibilidade de concluir; **não promover**.

Casos não construídos, interrompidos, sem memória, sem Gurobi ou sem gate anterior permanecem no denominador com `null` para objetivo LP ausente. Não imputar zeros nem transformar valor primal interrompido em limite inferior global.

## A4 e controles condicionais

**A4 permanece desligada** no plano padrão e gera `NOT_SELECTED_REASON`. Um **novo plano prospectivo** pode habilitar `ON_MATERIAL_A2_GAIN` ou `PRESELECTED_HYPOTHESIS` com justificativas antes dos solves; o refinamento aninhado A2→A4 é realizado exclusivamente pelo adaptador AS-03. O resultado A4 é diagnóstico opcional, não altera o denominador 6×3 do gate.

**CORE_IP:** adaptador não homologado na AS-04, relatório `NOT_IMPLEMENTED_IN_AS04`; **não substitui limite LP da formulação A**. **F-CC+K:** somente controle pequeno **com enumeração completa comprovada**, em protocolo separado; nenhum master restrito pode ser declarado LP completo. A AS-05 **não inventa** essas medidas quando o adaptador/certificação está indisponível. Para homologar esse ramo condicional será necessária evidência de enumeração completa, caso e orçamento.

## Saídas e auditabilidade

Diretório novo, **append-only**:

- `plan.json` e `manifest.json`: plano congelado e digests dos arquivos;
- `cases/<case>/comparison.json`, `arms.csv`, `pairs.csv`, `manifest.json`: dados AS-04 de cada caso;
- `reproducibility/<case>/seed-43|seed-44/`: pareamento adicional `U_K`, `A2_K` quando houver ganho candidato;
- `lp_summary.csv`: resumo de todos os seis casos sem valores inventados;
- `lp_gate.json`: regras, contrastes, status A4, decisões e limitações;
- `a4_optional.json`: só se A4 foi prospectivamente selecionada.

O comando `--execute` exige arquivo de evidências com revisão independente AS-01/AS-02 e homologação AS-04 (`as04_verdict=PASS`). Uma simples declaração JSON **não comprova revisão humana**: autores, revisores e pareceres precisam ser auditados externamente. O executável recusa por padrão sem esse arquivo ou com gate pendente. Nenhum resultado histórico N1, N2 ou FC é alterado.

## Threats to validity

LP mais forte pode não melhorar tempo ou bound MIP; seis casos são triagem de desenvolvimento; sucesso artificial de Sec59 não é critério de promoção; as seeds medem estabilidade condicional e **não** dão independência de grafos; MAPF da mesma fonte/mapa deve contar uma única vez; a partição automática não deve ser trocada pela partição testemunha após examinar os resultados. Mesmo `GO` é uma recomendação de continuar para AS-06, **não evidência de superioridade estatística geral**.
