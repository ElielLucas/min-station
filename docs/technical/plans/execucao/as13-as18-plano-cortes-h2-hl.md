# AS13–AS18 — Plano de pesquisa: cortes H2 e HL para COMP+K

**Status:** Planejamento / não executado. **Branch-alvo:** `novos_testes`.  
**Origem:** parecer Astra analisado em 13/10/2026. **Decisão:** suspender uso da Formulação C neste estudo; referência MIP é COMP+K.

## Hipótese central

Existem suportes R com massa fracionária baixa nos quais instalações que satisfazem K continuam fisicamente insuficientes. Certificar essa insuficiência para uma escolha isolada pode produzir H2 além do núcleo inteiro de K, com custo de separação viável em instâncias difíceis.

### Fundamento dos cortes (a validar independentemente em AS13)

Seja F=V\R. O matching máximo ν(C) do bipartido de origem-destino com estações disponíveis em C define viabilidade ν(C)=m.

Se ν(F)<m, seja B_R={v∈R:ν(F∪{v})<m} e G_R=R\B_R. Então, para instalações binárias fisicamente viáveis:

  Σ_{v∈B_R} y_v + 2Σ_{v∈G_R} y_v ≥ 2. (H2)

Com classificação parcial certificada B̂_R⊆B_R, é segura a linha com coeficiente 1 em B̂_R e 2 em R\B̂_R. Se ν(F)=m, não há H2 não trivial naquele suporte.

A extensão HL examina Φ_R={z∈{0,1}^R:ν(F∪supp(z))=m}, Q_R=conv(Φ_R). Para α≥0 racional e β=min_{z∈Φ_R}αᵀz, vale αᵀy_R≥β. Não emitir se β não for certificado sobre todos os padrões possíveis.

## Sequência e gates

| Etapa | Finalidade | Só avança se... |
|---|---|---|
| AS13 | Revisar provas, exemplos HB e quatro relés, novelty/precedentes | Provas e witness independentes validados |
| AS14 | Oráculo de matching físico triestado com cache, limites e evidências | Nenhum falso INFEASIBLE e UNKNOWN conservador |
| AS15 | Seleção de R e separador H2 certificado | Corte não redundante e testes exaustivos seguros |
| AS16 | LP 4 braços, seis instâncias de desenvolvimento, tempo total | Melhora >=1% em >=2 grafos independentes e sinal de custo líquido |
| AS17 | MIP 300s raiz COMP+K versus +H2; seeds/600s se justificado | Benefício replicável sem UB não validada |
| AS18 | HL local condicional e síntese | Só executar HL se houver residual estrutural além de H2 |

**Importante:** Quando o gate AS16 der STOP, não há execução automática de AS17. AS18 pode concluir formalmente NOT_AUTHORIZED sem implementar HL. Qualquer exceção exige nova justificativa antes de executar.

## Matriz de braços

| LP AS16 | Modelo |
|---|---|
| U | COMP |
| U+K | COMP+K, controle |
| U+H2 | COMP+H2 |
| U+K+H2 | COMP+K+H2 |

No MIP AS17: somente U+K versus U+K+H2, com cortes H2 certificados adicionados na raiz. A contribuição incremental deve ser medida também frente aos cortes nativos de raiz do solver.

## Limitações e pré-registro

- AS00: seis instâncias de desenvolvimento; preservar separação de avaliação, hashes, famílias brutas e freezes. Não selecionar apenas instâncias favoráveis.
- AS16: orçamento exploratório de **90 s por braço LP**, incluindo geração e separação; meta GO pré-registrada de ganho relativo de bound >=1% em pelo menos 2 grafos brutos independentes e custo líquido plausível. Isso é um **default de planejamento**, não um resultado obtido.
- AS17: **300 s totais por braço** inicialmente. 600s e seeds 42/43/44 somente se evidência justificar; 3600s condicionado a novo gate.
- Separador possui precisão certificada, mas pode ser incompleto. Não encontrar corte não prova inexistência.
- Sempre distinguir objetivo LP, LB numérico MIP, UB fisicamente validada e gap. Status de solver e timeout são métricas, não dados ausentes descartáveis.
- Testemunhas analíticas HB e quatro relés não são ganhos observados em instâncias reais.
- Não reiniciar CBI, C6, C3 individual, CG/zero-half sobre K ou L_bot como se fossem famílias inéditas. Comparações com limites globais existentes devem ser registradas.
- Não usar deficiência de Hall como número de estações; não supor submodularidade do ganho de matching.
- Não alterar `CLAUDE.md`, modelos históricos, cortes K ou artefatos congelados; nenhum código de AS13–AS18 está incluído neste pacote.

## Arquivos

Todos os arquivos executáveis como instruções estão em `specs/as-13-*` até `specs/as-18-*`, com `spec.md`, `design.md` e `tasks.md` em cada diretório.

## Fontes

- Parecer Astra H2/HL anexado em conversa (13/10/2026); formalização ainda sujeita a AS13.
- `docs/project-overview.md`, `RESEARCH.md`, `CLAUDE.md`.
- `docs/technical/plans/execucao/as00-benchmark-protocolo.md`.
- `docs/technical/reference/baseline-e-metodo/protocolo-comparacao-pareada.md`.
- `experiments/alternative-formulations/as02_model_a.py` e `experiments/cuts/cuts.py`.
