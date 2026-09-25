# Criador de POP (Procedimento Operacional Padrão)

Skill para agentes de IA que orienta a redação de **POPs em Markdown** — manuais operacionais que descrevem **o que fazer**, **como fazer** e **como saber que está correto**, de modo que **alguém novo no time** consiga executar o processo **só lendo o documento**.

O formato segue o template em `references/pop-template.md`, alinhado ao arquivo raiz `modelo-pop.md` do repositório.

## O que esta skill faz

- Conduz uma **coleta estruturada** (título, responsável, objetivo, passo a passo, resultados esperados e seções opcionais quando fizer sentido).
- Preenche a **tabela de identificação** com convenções definidas na skill: datas em **DD/MM/AAAA** (dia da sessão), **versão 1.0**, **status 🟢 Ativo**, **nome completo** do responsável.
- Mantém as seções editoriais do modelo (**O que é um POP**, **O que NÃO é**, **Como utilizar**, **Dicas importantes**) antes do POP específico.
- Reforça a **barreira de qualidade** (teste do “novato”) usando `references/pop-quality-bar.md`.
- Opcionalmente, você pode validar o arquivo gerado com `scripts/validate_pop.py` (checagens estruturais — não substitui revisão humana).

## POP vs outros documentos — quando usar esta skill?

| Situação | Use esta skill (POP)? |
|----------|----------------------|
| Processo repetível com passos, papéis e validações | **Sim** (com Modo Discovery quando faltar contexto crítico) |
| Só registrar *por que* uma decisão técnica foi tomada | **Não** — considere ADR (`create-adr`) |
| Proposta antes de decidir (buscar consenso) | **Não** — considere RFC (`create-rfc`) |
| Lista de tarefas sem “como executar” | **Não** — POP precisa de execução guiada |

## Como usar

### Uso básico

Você **não precisa** `@mencionar` a skill se o agente já carrega skills do projeto: basta pedir de forma clara.

**Português — pedido direto:**

```
Cria um POP em Markdown para o processo de abertura de chamado crítico no ServiceNow.
```

```
Preciso de um procedimento operacional padrão para backup manual do banco antes do deploy.
```

```
Documenta em formato POP o fluxo de onboarding de um novo desenvolvedor no time.
```

**Com contexto mínimo (a skill completa com perguntas):**

```
Faz um POP para deploy em produção.
```

**Com contexto rico (menos perguntas, entrega mais rápida):**

```
POP: rollback de release em produção. Responsável: Ana Paula Costa Souza.
Fluxo: detectar falha no smoke test → acionar runbook de rollback → notificar #incidentes →
atualizar status no Jira. Inclui critério de quando NÃO fazer rollback (hotfix possível).
```

**Inglês (se seu agente estiver em inglês):**

```
Create a standard operating procedure in Markdown for our production incident escalation flow.
```

### Modo interativo

Se você fornecer **contexto mínimo**, a skill tende a **perguntar** (em uma ou poucas mensagens, sem bombardear de uma vez):

1. **Título do POP** — texto que aparecerá em `# POP de ...`.
2. **Nome completo do responsável** — quem mantém ou “dona” este POP (evita apelido sem confirmação).
3. **Objetivo** — por que este POP existe e que problema ou necessidade resolve.
4. **Resultados esperados** — o que deve existir ao final; como validar que deu certo.
5. **Passo a passo** — o agente pode pedir detalhes até cada etapa ser **executável** por quem não conhece o processo (onde clicar, qual sistema, em que ordem, o que conferir).
6. **Seções opcionais** — quando fizer sentido: critérios de decisão (se/senão), insumos, checklist, riscos, fluxo/diagrama, observações.

Depois disso, ela monta o `.md` completo de forma iterativa: valida identificação/escopo, cria esqueleto de etapas, detalha etapa por etapa e só então consolida com quality gates.

### Convenções que o agente aplica (sem você ter que lembrar)

| Campo | Comportamento usual |
|-------|----------------------|
| **Criado em** | Data de **hoje** (DD/MM/AAAA) na sessão |
| **Data de entrega** | Na primeira emissão, costuma ser a **mesma data de hoje**, salvo você pedir outro marco |
| **Versão** | **1.0** |
| **Status** | **🟢 Ativo** |

Se você quiser **datas ou versão diferentes**, diga explicitamente no prompt.

## Validação opcional do arquivo gerado

Após salvar o POP no disco:

```bash
python3 scripts/validate_pop.py caminho/para/seu-pop.md
```

O script aponta placeholders óbvios e seções obrigatórias ausentes; **revise sempre** o conteúdo operacional à mão.

## Arquivos nesta pasta

| Arquivo | Função |
|---------|--------|
| `SKILL.md` | Instruções para o agente (fluxo completo). |
| `references/pop-template.md` | Estrutura canônica das seções e da tabela. |
| `references/pop-quality-bar.md` | Checklist “novato no time”. |
| `references/pop-domain-examples.md` | Menu de exemplos por domínio para acelerar discovery em contextos não web/IA. |
| `scripts/validate_pop.py` | Validação estrutural opcional. |

## Dica prática

Quanto mais você trouxer no primeiro prompt (**nome do responsável**, **gatilho do processo**, **passos já conhecidos**, **o que é falha**), menos rodadas de perguntas serão necessárias — mas o **modo interativo** existe justamente para quando você só tem a ideia geral e precisa de ajuda para deixar o POP executável.

## Convenções que o agente aplica

Além dos padrões de identificação, o agente aplica comportamento iterativo oficial para POP não trivial: evitar "gerar tudo de uma vez", priorizar refinamento progressivo e validar quality gates internos antes de declarar pronto.
