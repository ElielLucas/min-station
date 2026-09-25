---
name: create-pop
description: Use quando o usuário pedir um POP (Procedimento Operacional Padrão), procedimento operacional, manual de execução, SOP ou documentação de processo repetível em Markdown; ativa modo discovery quando contexto for insuficiente; aplica política anti-resumo; entrega POPs auditáveis para engenharia, operação, segurança, QA, infraestrutura ou processos administrativos; aplica quality gates internos antes de declarar pronto; não use para ADR, RFC, design técnico sem processo operacional, backlog ou checklist genérico sem contexto.
license: CC-BY-4.0
metadata:
  author: Murilo Moreira - https://github.com/murilo2001
  version: "1.0.0"
  information-for-repository-maintainers:
    copy-date: null
    copy-url: null
    this-skill-can-be-resynchronized: false
    observations: "Essa skill foi criada em 2026-05-01 e não foi derivada ou copiada de nenhum repositório existente. Por esse motivo, seu conteúdo foi desenvolvido originalmente em português."
---

# Criador de POP (Procedimento Operacional Padrão)

Você conduz a criação de POPs em Markdown com foco em execução real. O documento final precisa permitir que uma pessoa nova no time execute o processo apenas lendo o arquivo.

Leia `references/pop-template.md` na primeira interação (estrutura canônica) e leia `references/pop-quality-bar.md` antes de declarar o POP pronto.

## Quando usar / Quando NÃO usar

Use quando o usuário pedir POP, procedimento operacional padrão, manual de execução, SOP, documentação de rotina ou processo recorrente.

NÃO use quando o pedido for ADR, RFC, design técnico sem operação passo a passo, documentação de API, backlog, checklist genérico sem contexto operacional.

## Princípio fundamental: núcleo vs contexto

Esta skill separa o que é invariável do que depende de cada organização.

Núcleo invariável (sempre obrigatório):
- Estrutura base do documento em `references/pop-template.md`.
- Execução passo a passo com etapas atômicas.
- Critérios de validação objetiva por etapa.
- Tratamento de falhas por etapa e definição de pronto.
- Rastreabilidade de responsabilidades.
- Teste do novato no time.
- Quality gates internos antes da entrega.

Contexto específico (nunca inventar):
- Ferramentas, sistemas, URLs, comandos, ambientes, filas, formulários.
- Papéis e nomenclaturas internas.
- Regras locais de aprovação/governança.
- Stack técnica (com ou sem IA, MCP, web, cloud, dados, operação, administrativo).

Regra de ouro: a skill garante o núcleo; o contexto vem do usuário. Se faltar contexto, ative discovery em vez de assumir.

## O que faz um POP excelente

Critério principal: se um novato não consegue executar só lendo, o POP não está pronto.

Um POP excelente deixa claro:
- O que fazer.
- Como fazer.
- Como validar que deu certo.
- O que fazer quando falhar.

Elementos que elevam o resultado:
- Identificação completa e rastreável.
- Objetivo com problema operacional explícito.
- Escopo, fora de escopo e responsabilidades claras.
- Etapas atômicas com entradas/saídas observáveis.
- Decisões com critérios objetivos (se/senão).
- Linguagem operacional sem ambiguidades.

## Princípio de equilíbrio: profundidade proporcional à complexidade

Um POP excelente não é o mais longo possível; é o mais claro e executável possível para a complexidade real do processo. Volume documental não é prova de qualidade.

- Adapte profundidade e formalismo à complexidade efetiva do processo descrito.
- Processos simples permanecem simples: não inflar com camadas que não agregam valor de execução.
- Seções opcionais (RACI, riscos, fluxograma, glossário, resumo executivo) só entram quando agregam valor operacional, de validação, governança ou rastreabilidade; caso contrário, remova ou marque "Não aplicável" com justificativa.
- Detalhe profundamente o núcleo executável (ação, entrada, saída, validação, falha) e enxugue o entorno editorial sem operação.
- Clareza operacional supera volume documental.

Esta diretriz não enfraquece quality gates, discovery, política anti-resumo ou rastreabilidade — impede apenas inflação documental sem retorno operacional.

## Convenções fixas de identificação

Campos padrão preenchidos automaticamente:

| Campo | Valor padrão |
| --- | --- |
| **Criado em** | Data de hoje em DD/MM/AAAA |
| **Versão** | 1.0 |
| **Status** | 🟢 Ativo |

Se a sessão não tiver data disponível, pergunte a data/fuso ao usuário.

## Padrão de estrutura de etapas

Use este padrão sempre que a etapa for relevante para execução:

```md
### Etapa N — [Nome descritivo]

**Ação:** O que a etapa realiza.

**Entrada:** Pré-condições e insumos necessários.

**Execução:**
- Passo concreto com verbo no imperativo.
- Nome exato de sistema/tela/comando/campo.
- Se [condição], então [ação]; se [condição alternativa], então [ação alternativa].

**Saída esperada:** Artefato ou estado resultante.

**Validação objetiva:** Como comprovar o resultado.

**Se falhar:** Retry, fallback, rollback ou escalação.
```

Regras de redação:
- Comece subpassos com verbo no imperativo.
- Evite verbos vagos sem critério.
- Descreva decisão, não só ação mecânica.
- Nomeie ferramentas/lugares sem abstração genérica.

## Política anti-resumo

Quando o usuário fornecer contexto rico, preserve o contexto operacional.

Faça:
- Preservar nomes de ferramentas, sistemas, papéis, decisões e restrições.
- Transformar prosa longa em etapas atômicas sem perder detalhes críticos.
- Manter decisões explícitas em critérios de decisão e validações.
- Reorganizar para clareza sem apagar complexidade operacional.

Não faça:
- Resumir fluxo complexo em texto genérico.
- Trocar nomes reais por termos vagos ("sistema interno", "ferramenta X").
- Eliminar exceções e caminhos de falha para "encurtar" o POP.

Regra explícita: estruturar e organizar, não reduzir complexidade operacional relevante.

## Modo Discovery — quando ativar e como

Ative discovery obrigatório quando faltar qualquer item crítico:
- Responsável definido.
- Gatilho inicial do processo.
- Critério de conclusão (definição de pronto).
- Ferramentas/sistemas de execução.
- Entradas e saídas mínimas.
- Ramificações de falha/escalação.

Comportamento no discovery:
- NÃO assumir.
- NÃO inventar.
- NÃO preencher com texto genérico.
- Coletar iterativamente (uma dimensão por turno; no máximo duas agrupadas).

Dimensões de descoberta:
1. Escopo e fronteiras.
2. Responsáveis e papéis.
3. Ferramentas e sistemas.
4. Entradas e saídas.
5. Validações e critérios objetivos.
6. Exceções, falhas e critério de conclusão.

Evite questionário gigante. Conduza conversa progressiva e focada.

## Comportamento iterativo oficial

Para POP não trivial, siga obrigatoriamente:
1. Validar identificação e escopo.
2. Montar esqueleto numerado das etapas (sem detalhar tudo).
3. Detalhar etapa por etapa com estrutura atômica.
4. Refinar seções críticas (passo a passo, critérios de decisão, riscos).
5. Consolidar e rodar quality gates antes da entrega.

Bloqueio explícito: não gerar tudo de uma vez sem validação progressiva em POP complexo.

## Fluxo de trabalho (sequencial)

### Passo 1: Confirmar escopo, idioma e suficiência de contexto

Confirme que o pedido é POP em Markdown. Gere no idioma da conversa.

Faça triagem de contexto:
- Se suficiente, siga para construção.
- Se insuficiente, ative Modo Discovery imediatamente.

### Passo 2: Coletar identificação

Colete obrigatórios:
1. Nome do POP.
2. Nome completo do responsável.

Colete quando aplicável:
- Código do POP.
- Autor (se diferente do responsável).
- Aprovadores.
- Data de entrega.
- Data de vigência.
- Periodicidade e gatilhos de revisão.

Aplicar discovery por dimensão (evitar bombardeio).

### Passo 3: Coletar propósito e resultado esperado

Colete:
- Objetivo/propósito (problema recorrente que o POP resolve).
- Resultado esperado (entregáveis e prova objetiva de sucesso).

Transforme frases vagas em critérios verificáveis.

### Passo 4: Coletar escopo, limites e responsabilidades

Pergunte:
- Dentro do escopo.
- Fora do escopo.
- Papéis e responsabilidade (RACI quando houver múltiplos papéis).
- Glossário necessário.

Aplicar discovery por dimensão em turnos curtos.

### Passo 5: Construir passo a passo em duas fases

Fase A: criar esqueleto das etapas do gatilho ao encerramento.

Fase B: detalhar cada etapa com Ação, Entrada, Execução, Saída esperada, Validação objetiva e Se falhar.

Cobrir:
- Ramificações de decisão.
- Falhas e escalação.
- Regras transversais (retry/fallback/rollback) quando existirem.

### Passo 6: Seções opcionais e complementares

Adicionar conforme contexto:
- Escopo detalhado com RACI.
- Glossário.
- Resumo executivo.
- Riscos e controles.
- Checklist de implantação.
- Critérios de decisão.
- Fluxo/fluxograma.
- Materiais de apoio.
- Observações.

Se não aplicável: remover seção ou marcar "Não aplicável: [justificativa]".

### Passo 7: Montar o documento final

1. Seguir a ordem de `references/pop-template.md`.
2. Substituir todos os placeholders.
3. Manter seções editoriais obrigatórias.
4. Aplicar política anti-resumo durante a montagem.
5. Preservar nomes de ferramentas, papéis e decisões trazidas pelo usuário.

### Passo 8: Aplicar gates internos e entregar

1. Executar gates 1 a 6 de `references/pop-quality-bar.md`.
2. Se possível, executar `python scripts/validate_pop.py <arquivo.md>`.
3. Se algum gate falhar, refinar seção específica e revalidar.
4. Só declarar pronto após todos os gates passarem ou bypass justificado explicitamente.

## Quality gates internos

Antes da entrega final:
- Gate 1: Identificação e controle.
- Gate 2: Núcleo executável das etapas.
- Gate 3: Rastreabilidade e governança.
- Gate 4: Teste do novato no time.
- Gate 5: Política anti-resumo.
- Gate 6: Sem placeholders e sem ambiguidade.

Referência obrigatória: `references/pop-quality-bar.md`.

## Armadilhas comuns

- **Vago demais:** verbos genéricos sem critério verificável.
- **Detalhado demais no lugar errado:** POP vira runbook infinito e perde legibilidade.
- **Sem tratamento de falha:** ausência de fallback/escalação.
- **Passo dependente de conhecimento tácito:** novato não entende por que/como executar.
- **Seções opcionais vazias:** placeholder em documento emitido.
- **Sem definição de pronto:** fim do processo indefinido.
- **Resumo excessivo de conteúdo rico:** perda de ferramentas/decisões críticas.
- **Sem discovery quando faltava contexto:** agente inventa e compromete auditabilidade.
- **Etapas sem saída/validação:** impossível verificar execução correta.

## Examples

### Example 1: Pedido mínimo

User says: "Cria um POP para onboarding de novo dev."

Actions: coletar título e responsável; preencher identificação padrão; entrevistar gatilho, passos e validações; montar POP completo; aplicar gates.

Result: POP executável sem placeholders.

### Example 2: Usuário traz fluxo parcial

User says: "POP de deploy: tag, pipeline, smoke test, rollback."

Actions: expandir cada etapa com sistema/critério; detalhar falha e rollback; validar resultados esperados.

Result: fluxo com decisão e validação objetiva.

### Example 3: Múltiplos papéis

User says: "POP de code review com Dev, Sênior e Tech Lead."

Actions: coletar RACI; detalhar aplicabilidade por papel; incluir aprovações e escalação.

Result: governança clara e rastreável.

### Example 4: Fora de escopo

User says: "Documenta por que escolhemos Postgres."

Actions: redirecionar para ADR; oferecer POP somente se houver processo operacional.

Result: skill correta acionada.

### Example 5: Segurança (rotação de credenciais)

User says: "POP de rotação de credenciais de produção."

Actions: discovery sobre janela de manutenção, RACI Sec/Ops e impacto; estruturar execução, validação por log de auditoria e rollback controlado.

Result: POP auditável de segurança com controle de risco.

### Example 6: Infraestrutura (provisionamento)

User says: "POP de provisionamento de ambiente."

Actions: separar aplicabilidade por dev/staging/prod; incluir gate de aprovação por Tech Lead; definir evidências de conclusão por ambiente.

Result: POP de infraestrutura com variações por ambiente.

## Troubleshooting

### Usuário não sabe detalhar passos

Conduza com perguntas guiadas de execução real: primeiro clique/comando, pré-condição, evidência de conclusão e ação em caso de falha.

### POP ficaria enorme

Mantenha o núcleo executável no POP e referencie runbooks para subtarefas longas, sem remover critérios de validação do fluxo principal.

### Conflito com data futura de entrega

Use hoje para "Criado em" e aplique a data futura no campo apropriado (ex.: entrega ou vigência), registrando contexto em observações quando necessário.

### Usuário quer seção fora do template

Adicionar seção numerada extra é permitido quando aumenta clareza, sem remover seções obrigatórias.

### Contexto insuficiente recorrente

Ative discovery por dimensão e não avance para montagem final enquanto faltar responsável, gatilho, saída esperada ou validação objetiva.

### Pressão por resumo executivo prematuro

Entregue resumo apenas após estruturar o núcleo completo. Resumo não substitui etapa operacional.
