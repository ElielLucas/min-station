# AS18 — Síntese final da linha H2/HL e continuidade científica

**Data:** 15/10/2026  
**Situação da síntese:** produzida; experimentação HL **não autorizada**.  
**Conclusão de priorização:** encerrar a linha H2/HL neste protocolo e buscar candidatos com ganho marginal sobre **COMP+K**; preservam-se as limitações de revisão independente.

## 1. Registro das etapas e decisões

| Etapa | O que foi realizado | Resultado / limite |
|---|---|---|
| AS13 | Fundamentação matemática e condições de validade de H2/HL nos documentos existentes | Provas/argumentos documentais de AS13 **não equivalem a resultados LP/MIP de HL** |
| AS14 | Oráculo de viabilidade baseado em matching, testes e evidências locais | Certificação operacional de casos sob hipóteses da etapa; não constitui benefício global de H2/HL |
| AS15 | Separação de H2 e microcasos/testes | Implementação de H2 presente; não é demonstração de complementaridade experimental com K |
| AS16 | Piloto LP pareado em seis grafos de desenvolvimento e 36 braços/controles | Gate automático `INVESTIGATE`; decisão científica `STOP` para priorizar H2 |
| AS17 | Piloto MIP H2 exigia AS16 `GO` | **NOT_AUTHORIZED**, nenhum MIP H2 executado |
| AS18 | Gate de HL e síntese condicional | HL **NOT_AUTHORIZED**; apenas gate, verificação e síntese executados |

## 2. Evidências numéricas próprias da AS16

Os valores são **objetivos LP ótimos**, não ótimos inteiros ou certificados racionais externos. Para um problema de minimização, limite inferior maior representa relaxação mais forte.

| Instância | COMP+K LP | COMP+K+H2 LP | Tempo COMP+K | Tempo COMP+K+H2 |
|---|---:|---:|---:|---:|
| PUC CC9 | 27,02679 | 27,02679 | 1,69 s | 3,07 s |
| PUC BIP42 | 31,70605 | 31,70605 | 13,77 s | 31,71 s |
| PUCN CC3 | 16,93333 | 16,93333 | 5,78 s | 23,95 s |
| MAPF Room | 13,20000 | 13,20000 | 1,30 s | 1,74 s |
| Vienna I056 | 8,50000 | 8,50000 | 88,17 s | 88,13 s |
| PUC W3C571 | censurado | censurado | ≥90 s | ≥90 s |

- **Cinco de seis** comparações COMP+K × COMP+K+H2 chegaram a `OPTIMAL`; entre essas, houve **zero ganhos LP** de H2 sobre K.
- H2 sozinho elevou o LP de COMP em dois casos (PUCN CC3 e MAPF Room), mas essa melhoria foi superada pelo K já presente; não confundir aumento sobre U com ganho adicional sobre U+K.
- Os controles com mesmo pool H2 também não melhoraram o bound de COMP+K nos casos disponíveis; são diagnósticos **post hoc**, não validação fora da amostra.
- Nos quatro casos rápidos a adição de H2 aumentou o tempo total; em Vienna os tempos foram parecidos e próximos do limite. Apenas **uma execução por braço**, sem inferência estatística.
- A AS16 teve cinco censuras `TIME_LIMIT` nos braços principais e dois controles `NOT_RUN`; a censura impede conclusão de ganho no sexto grafo, mas não altera o teto de um possível grafo favorável diante da exigência de dois.

**Proveniência:** `docs/technical/reference/experimentos/as16-resultado-lp-h2.md`, `results/benchmark/as16-lp-h2-001/` e verificação `specs/as-18-hl-condicional-e-sintese/as18-gate-evidence.json`.

## 3. O que é prova, hipótese ou resultado empírico

| Natureza | Afirmação responsável |
|---|---|
| Definição / argumento formal | As desigualdades H2 e a estrutura hipotética HL estão discutidas em AS13 e suas condições de certificação. Conferir provas originais e alcance das hipóteses antes de extrapolar |
| Testemunha analítica | A alegação de quatro relés com hierarquia de LP `2`, `8/3`, `3` consta na spec AS18, **mas não foi reproduzida aqui** |
| Resultado LP medido | AS16 mediu ganho nulo de H2 sobre COMP+K nos cinco casos comparáveis; duas melhorias de H2 sobre COMP sem K |
| Resultado MIP | **Nenhum** experimento AS17 MIP com H2 foi autorizado ou executado nesta linha |
| Resultado HL | **Nenhum** corte HL ou LP HL implementado, certificado ou testado nesta etapa |
| Estado da literatura | O projeto cita trabalhos de Das e o mapa de sobreposições existente. **Não se reivindica novidade de H2/HL** sem revisão bibliográfica específica e independente |
| Conclusão metodológica | `STOP` para continuar H2 e `NOT_AUTHORIZED` para AS17/HL são decisões de priorização, **não** teoremas de dominância de COMP+K |

## 4. Gate, regras e possíveis reaberturas

O analisador original deu `INVESTIGATE`: não mudar este resultado no `analysis.json`. O encerramento da AS16 usa decisão separada de pesquisa `STOP`, apoiada no pré-registro: o máximo favorável, ainda que o caso censurado tivesse ganho, seria **um** grafo, abaixo do mínimo de **dois**. A AS17 exigia GO explícito e por isso é `NOT_AUTHORIZED`.

Em AS18, **não há evidência estrutural independente aprovada na documentação disponível** que justifique explorar HL apesar do STOP de H2. Logo, não criar gerador `hl_local.py`, não realizar experimento MIP e não simular valores LP do microexemplo. Reabrir somente com hipótese estrutural nova, prova/certificação apropriada e pré-registro distinto. Ver `docs/technical/plans/execucao/as18-gate-hl.md`.

## 5. Próxima linha científica sugerida (ainda não implementada)

1. **Identificar obstruções residuais de COMP+K** com instâncias de desenvolvimento que possuam raiz LP fracionária e lacuna comprovada frente a soluções inteiras validadas; não usar somente casos em que K já fecha o gap.
2. **Propor cortes candidatos fundamentados** em estruturas que K não capture; exigir prova matemática de validade ou certificação conservadora sobre soluções físicas e confronto com a literatura antes de implementar separação.
3. **Pré-registrar comparação marginal pareada** COMP+K × COMP+K+nova família no mesmo conjunto e orçamento total. Medir limites, tempo de pré-processamento, certificação, reotimização e taxa de censura; incluir controles de mesmo pool quando pertinentes.
4. **Promover apenas sob evidência replicável de ganho líquido**, com separação entre LP, raiz MIP e impacto na árvore; caso negativo encerrar e registrar.

Não se cria automaticamente uma AS19 nem se atribui novidade/resultado à próxima família. A escolha de um mecanismo específico depende de nova hipótese documentada. F-CC/F-C3 e Formulação C permanecem linhas separadas, sem reativação implícita.

## 6. Limitações e auditabilidade

- Seis grafos de desenvolvimento (uma execução por braço), com censuras; sem comparação estatística multi-seed e sem campanha MIP H2.
- Não há prova de que qualquer desigualdade H2 seja globalmente implicada por K; nem de que HL seria redundante.
- A evidência de gate derivada confere consistência de JSON e contagens, **não é segundo solver nem verificador matemático independente**.
- Parecer científico de pessoa distinta do autor não está comprovado; não marcar revisão humana externa como concluída.
- Não sobrescrever `results/benchmark/as16-lp-h2-001` nem alterar `manifest.json`, `rows.json`, `analysis.json` ou os pools para obter outro gate.
