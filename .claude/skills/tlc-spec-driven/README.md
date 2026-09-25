<p align="center">
  <img src="https://img.shields.io/badge/Skill-TLC%20Spec--Driven-blue?style=for-the-badge" alt="skill badge" />
  <img src="https://img.shields.io/badge/Stack-Agnostic-green?style=for-the-badge" alt="stack agnostic" />
  <img src="https://img.shields.io/badge/Version-2.0.0-purple?style=for-the-badge" alt="version" />
</p>

<h1 align="center">🎯 TLC Spec-Driven</h1>

<p align="center">
  <strong>Planeje e implemente funcionalidades com precisão. Tarefas granulares. Dependências claras. Ferramentas certas. Zero cerimônia.</strong>
</p>

<p align="center">
  <em>Da comunidade <a href="https://github.com/tech-leads-club">Tech Lead's Club</a></em>
</p>

<p align="center">
  <strong>Autor:</strong> <a href="https://github.com/felipfr">Felipe Rodrigues</a> · 
  <a href="https://linkedin.com/in/felipfr">LinkedIn</a>
</p>

## ✨ O Que É Esta Skill?

**TLC Spec-Driven** transforma a forma como agentes de IA planejam e implementam funcionalidades. Em vez de um pipeline rígido e burocrático, ela usa **4 fases adaptativas** que se auto-ajustam com base na complexidade — aplicando rigor total para funcionalidades complexas e pulando cerimônia para as simples:

```
┌──────────┐   ┌──────────┐   ┌─────────┐   ┌─────────┐
│ SPECIFY  │ → │  DESIGN  │ → │  TASKS  │ → │ EXECUTE │
└──────────┘   └──────────┘   └─────────┘   └─────────┘
   obrigatório   opcional*      opcional*     obrigatório

* O agente pula automaticamente quando o escopo não precisa
```

O que diferencia esta versão:

- **Requisitos em notação EARS** — critérios de aceitação testáveis e sem ambiguidade (Ubiquitous, Event-driven, State-driven, Optional-feature, Unwanted-behavior, Complex).
- **Gates determinísticos por script**, não por memória do modelo — `validate_spec.py`, `validate_tasks.py`, `check_commit.py` e `validate_state.py` fecham cada fase por código, não por autoavaliação.
- **Verifier independente** (author ≠ verifier) — um sub-agente novo audita a implementação depois do último commit com checagem spec-anchored evidence-or-zero e um **sensor de discriminação** (mutation testing leve em scratch isolado).
- **Log de decisões** (`STATE.md`) — decisões de projeto (`AD-NNN`) e snapshot de pausa/retomada (Handoff), com escrita sempre restrita à sua própria seção.
- **Camada de lições auto-aprimorável** — falhas reais de verificação viram lições reutilizáveis (`scripts/lessons.py`), promovidas depois de recorrer em features distintas.

Agnóstica de stack e de ferramenta.

**A complexidade está no sistema, não no seu fluxo de trabalho.** Você fala naturalmente — a skill decide o quão profundo ir:

| Escopo                               | O que acontece                                                      |
| ----------------------------------- | ----------------------------------------------------------------- |
| **Pequeno** (≤3 arquivos)                | Spec de uma linha, inline — implementar → verificar direto no Execute |
| **Médio** (funcionalidade clara, <10 tarefas) | Specify → Execute (design e tarefas inline)                       |
| **Grande** (multi-componente)         | Pipeline completo com design formal e divisão de tarefas              |
| **Complexo** (ambiguidade, novo domínio) | Pipeline completo + discussão de zonas cinzentas + pesquisa + UAT interativo |

## 🚀 Início Rápido

### Instalação

```bash
npx @tech-leads-club/agent-skills install -s tlc-spec-driven
```

### Primeiros Comandos

| O Que Você Quer                | Diga Isso                                     |
| ------------------------------ | ---------------------------------------------- |
| Planejar uma funcionalidade    | `"Specify feature [name]"`                     |
| Discutir zonas cinzentas       | `"Discuss feature"` ou `"How should this work"` |
| Desenhar a arquitetura         | `"Design feature"` ou `"Architecture"`         |
| Dividir em tarefas              | `"Break into tasks"` ou `"Create tasks"`       |
| Implementar                     | `"Implement task"`, `"Build"`, `"Execute"`     |
| Validar o que foi feito        | `"Validate"`, `"Verify work"`, `"UAT"`         |
| Registrar uma decisão de projeto | `"Record decision"`                            |
| Retomar trabalho anterior      | `"Resume work"` ou `"Continue"`                |

> 💬 **Conversa Natural, Não Comandos**
>
> Estas são frases-gatilho, não comandos estritos. A skill funciona através de **conversa natural** — fale com seu agente como falaria com um colega. Diga coisas como _"I want to build an authentication system"_ ou _"Fix the login button, it returns 401"_. O agente entende contexto e intenção, não apenas palavras-chave.

## 📁 Estrutura do Projeto

A skill cria um diretório `.specs/` para organizar toda a documentação de funcionalidades e a memória do projeto:

```
.specs/
├── STATE.md            # Memória do projeto: log de decisões (AD-NNN) + snapshot de handoff
├── LESSONS.md          # Playbook de lições auto-aprimorável (renderizado por scripts/lessons.py — não editar à mão)
├── lessons.json        # Estado canônico das lições (propriedade do script)
│
└── features/            # Especificações de funcionalidades
    └── [feature-name]/
        ├── spec.md       # Requisitos em notação EARS com IDs rastreáveis (FEAT-01, AUTH-02...)
        ├── context.md    # Decisões do usuário para zonas cinzentas (somente quando discuss é disparado)
        ├── design.md     # Arquitetura, componentes e riscos/concerns (somente para grande/complexo)
        ├── tasks.md      # Tarefas atômicas + matriz de cobertura de testes (somente para grande/complexo)
        └── validation.md # Relatório do Verifier: PASS/FAIL, evidência por AC, resultado do sensor, diff range
```

`context.md`, `design.md`, `tasks.md` e `validation.md` só são criados quando a fase correspondente realmente produz conteúdo — nunca ficam vazios como placeholder de fase pulada.

## 🔄 As Quatro Fases Adaptativas

### Specify (sempre)

**Objetivo:** Capturar O QUE construir com requisitos testáveis e rastreáveis.

O agente carrega antes as **lições confirmadas** do projeto (`scripts/lessons.py list --status confirmed`) para não repetir falhas de verificação já conhecidas, faz uma varredura leve do código existente e atua como um parceiro de raciocínio — não um entrevistador. Ele desafia vaguezas e fecha a spec com critérios em **notação EARS**:

```markdown
### P1: User Login ⭐ MVP

**User Story:** As a user, I want to log in so that I can access my account.

| Requirement ID | Acceptance Criteria                                                            |
| -------------- | ------------------------------------------------------------------------------ |
| AUTH-01        | WHEN user enters valid credentials THEN system SHALL authenticate and redirect |
| AUTH-02        | WHEN user enters invalid credentials THEN system SHALL display error message   |
| AUTH-03        | WHILE session is active WHEN user requests /login THEN system SHALL redirect to dashboard |
```

Antes de confirmar a spec, `python3 <skill-dir>/scripts/validate_spec.py` roda como gate de fechamento (critérios em formato EARS, assumptions preenchidas, IDs bem formados).

**Discutir zonas cinzentas (auto-disparado):** Quando a spec tem decisões ambíguas e voltadas ao usuário (ou qualquer dimensão de requisito implícito presente — persistência, chamadas externas, auth, pagamentos, concorrência, transições de estado), o agente automaticamente pergunta ao usuário sobre elas — criando um `context.md` que trava essas decisões antes do design. Isso NÃO é uma fase separada — só acontece dentro de Specify.

### Design (quando necessário)

**Objetivo:** Definir COMO construir. Arquitetura, componentes, o que reutilizar.

**Pulado quando:** A mudança é direta — sem decisões arquiteturais, sem novos padrões. Para funcionalidades simples, o design acontece inline durante o Execute.

Antes de qualquer decisão arquitetural, o agente lê `.specs/STATE.md` (seção `## Decisions`) — toda entrada `AD-NNN` ativa é uma restrição de projeto que o design deve respeitar ou conscientemente substituir (nova entrada que supera a antiga). Também flagra riscos e dívida técnica encontrados no código (`## Risks & Concerns` no `design.md`), cada um com uma mitigação obrigatória.

**Inclui pesquisa:** Antes de projetar com tecnologia desconhecida, o agente segue a **Cadeia de Verificação de Conhecimento** (codebase → documentação do projeto → Context7 MCP → busca na web → marcar como incerto). Ele **nunca assume ou fabrica** — se não conseguir encontrar documentação, ele diz isso.

**Saída:** `design.md` com diagramas de arquitetura, definições de componentes, pontos de integração e riscos/concerns com mitigação.

### Tasks (quando necessário)

**Objetivo:** Dividir em tarefas GRANULARES e ATÔMICAS com dependências claras.

**Pulado quando:** Há ≤3 passos óbvios. Nesse caso, as tarefas são listadas inline no início do Execute.

**Válvula de segurança:** Se listar passos inline revelar >5 passos ou dependências complexas, o agente PARA e cria um `tasks.md` formal — reconhecendo que a fase Tasks foi erroneamente pulada.

| ❌ Tarefa Vaga | ✅ Tarefas Atômicas                   |
| ------------- | --------------------------------- |
| "Create form" | T1: Create email input component  |
|               | T2: Add email validation function |
|               | T3: Create submit button          |
|               | T4: Add form state management     |

Toda `tasks.md` sempre inclui uma **matriz de cobertura de testes** (mapeando cada AC a um teste) e uma tabela de **Gate Check Commands** (nível `quick`/`full`/`build`, cada tarefa aponta a qual pertence). Antes de apresentar as tarefas para aprovação, `python3 <skill-dir>/scripts/validate_tasks.py` roda como gate (cheiro de granularidade, paridade diagrama × `Depends on`, sem dependência de fase futura).

Cada tarefa inclui: O quê (entregável), Onde (caminho do arquivo), Depende de (pré-requisitos), Reutiliza (código existente), Requisito (ID rastreável), Testes + Gate, Concluído quando (critérios verificáveis), Commit (formato da mensagem).

### Execute (sempre)

**Objetivo:** Implementar uma tarefa por vez. Verificar. Commitar. Repetir.

Toda tarefa segue o mesmo ciclo:

```
Plan → Implement → Verify → Commit → Next
```

**Princípios-chave:**

- **Mudanças cirúrgicas** — Toque apenas nos arquivos necessários
- **Sem scope creep** — Se não estiver na tarefa, não toque
- **Testes derivam da spec** — nunca espelham a implementação; nunca são enfraquecidos, pulados ou apagados para passar
- **Um commit atômico por tarefa** — cada `git commit` passa por `python3 <skill-dir>/scripts/check_commit.py --message "<msg>"`, que valida [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)

```
feat(auth): add email validation to login form

refactor(api): extract token refresh logic into service

fix(cart): prevent negative quantity on item decrement
```

**Delegação a sub-agentes (opt-in):** Se a feature tiver mais de ~8 tarefas, o agente oferece empacotá-las em workers de ~7 tarefas por fases inteiras (nunca divide uma fase entre workers) — o usuário precisa aceitar explicitamente antes de qualquer sub-agente ser disparado.

**Verifier sempre roda, nunca é opcional:** depois do último commit, um sub-agente **novo** (author ≠ verifier) audita a feature — checagem spec-anchored evidence-or-zero por AC e um **sensor de discriminação** (injeta falhas comportamentais em scratch isolado — worktree temporário ou cópias de arquivo, nunca `git stash` — e confirma que os testes matam o mutante). Escreve `.specs/features/[feature]/validation.md` (PASS/FAIL, evidência `file:line`, resultado do sensor) e, ao final, **destila lições** de qualquer falha real encontrada. `python3 <skill-dir>/scripts/validate_state.py <feature>` é o gate de conclusão: sem um `validation.md` com veredito PASS e evidência citada, a feature não é declarada pronta.

## 📋 Referência Completa de Comandos

Esses padrões de gatilho ajudam o agente a reconhecer sua intenção, mas você não precisa usá-los literalmente. Fale naturalmente — o agente entende variações e contexto.

### Nível de Funcionalidade (auto-dimensionado)

| Padrão de Gatilho                           | Descrição                             |
| ----------------------------------------- | ---------------------------------------- |
| `Specify feature`, `Define requirements`  | Cria o spec.md com IDs de requisitos em EARS |
| `Discuss feature`, `How should this work` | Captura decisões do usuário para zonas cinzentas   |
| `Design feature`, `Architecture`          | Cria o design.md com arquitetura e riscos/concerns |
| `Break into tasks`, `Create tasks`        | Cria o tasks.md com divisão atômica + matriz de testes |
| `Implement task`, `Build`, `Execute`      | Executa a tarefa específica com verificação |
| `Validate`, `Verify work`, `UAT`          | Dispara o Verifier: checagem spec-anchored + sensor de discriminação |

### Memória e Lições

| Padrão de Gatilho                                        | Descrição                                              |
| ---------------------------------------------------------- | ------------------------------------------------------- |
| `Record decision`, `This is a project-level decision`      | Registra uma entrada `AD-NNN` em `.specs/STATE.md`      |
| `Pause work`, `End session`, `I need to stop`              | Sobrescreve só a seção `## Handoff` de `STATE.md`        |
| `Resume work`, `Continue`, `Pick up where we left off`     | Lê o Handoff e reconcilia com git antes de propor o próximo passo |
| `Load lessons`, `What have we learned`                     | Carrega lições confirmadas via `scripts/lessons.py`     |
| `Record lesson`, `Distill lessons`                         | Roda automaticamente após cada validação — não é um passo manual |

## 🔁 Exemplos de Fluxo de Trabalho

### Implementando uma Funcionalidade (auto-dimensionado)

```
You: Specify feature user-authentication

Agent: [Carrega lições confirmadas, faz perguntas esclarecedoras,
       cria spec.md com IDs de requisitos em EARS]
       I notice some gray areas in the UX — how should failed login attempts behave?
       [Discute zonas cinzentas, cria context.md]

You: Design the feature

Agent: [Lê STATE.md Decisions, pesquisa JWT via Context7, flagra riscos,
       cria design.md]

You: Break into tasks

Agent: [Cria tasks.md com 8 tarefas atômicas + matriz de cobertura de testes]

You: Implement T1

Agent: Implementing T1: Create auth service interface
       Files: src/services/auth.interface.ts
       Approach: Define interface based on design
       Verify: Interface compiles, exports correctly

       [Implements...]

       ✅ Committed: feat(auth): create auth service interface
       Next available: T2, T3 [P] (parallel)

--- Depois da última tarefa ---

Agent: [Dispara Verifier automaticamente — spec-anchored check + sensor
       de discriminação]

       ## Validation: user-authentication — PASS ✅
       Spec-anchored check: 8/8 ACs matched spec outcome
       Gate: 12 passed, 0 failed
       Sensor: 3 mutations injected, 3 killed, 0 survived
       Report: .specs/features/user-authentication/validation.md
```

### Correção Pequena (escopo Pequeno, inline)

```
You: Quick fix: login button returns 401 because token refresh skips expired check

Agent: [Escopo Pequeno — spec de uma linha inline, sem Design/Tasks formais]
       Approach: Add expiry validation before refresh attempt
       Verify: Login with expired token returns new session, not 401

       [Implements...]

       ✅ Committed: fix(auth): add expiry check to token refresh
       [Verifier roda automaticamente após o commit]
```

### Continuidade de Sessão

```
You: Pause work

Agent: [Sobrescreve só a seção ## Handoff de .specs/STATE.md]
       ✅ Handoff saved
       - Feature: user-authentication
       - Completed: T1, T2 (committed)
       - In progress: T3 (70%)
       - Next step: Continue T3, then T4

--- Later, new session ---

You: Resume work

Agent: [Lê STATE.md — Decisions + Handoff — depois reconcilia com git
       (branch, status --porcelain, commits recentes) antes de agir]
       Resuming user-authentication at T3
       - Completed: T1 (auth interface), T2 (token storage)
       - In progress: T3 - auth service at src/services/auth.service.ts:45
       - Next: Complete T3, then T4 (parallel with T5)

       Continue with T3?
```

## 🧠 Gerenciamento de Contexto

A skill é projetada para funcionar dentro dos limites de contexto:

| Estratégia de Carregamento          | Documentos                                   | Tokens |
| ---------------------- | -------------------------------------------- | ------ |
| **Carregamento sob demanda** | `STATE.md` (Decisions/Handoff), lições confirmadas, spec/context/design/tasks atuais | +5-10k cada |
| **Nunca simultâneo** | Múltiplas specs de funcionalidades ou documentos de arquitetura | —      |

**Meta:** <40k tokens carregados (20% do contexto)
**Reserva:** 160k+ tokens para trabalho, raciocínio, saídas

Limites por arquivo: `spec.md` até 5.000 tokens, `design.md` até 8.000, `tasks.md` até 10.000. Quando o contexto total excede 40k, a skill exibe um indicador de status; acima de 60k, um aviso ativo sugerindo otimização.

## 📚 Arquivos de Referência

A skill inclui documentação de referência detalhada carregada sob demanda:

| Arquivo                   | Propósito                                                                |
| -------------------------- | ---------------------------------------------------------------------- |
| `specify.md`               | Coleta de requisitos testáveis em notação EARS, dimensões de requisito implícito |
| `discuss.md`               | Discussão de zonas cinzentas e captura de contexto                     |
| `design.md`                | Arquitetura, pesquisa, reuso de código e sinalização de riscos/concerns |
| `tasks.md`                 | Divisão granular, matriz de cobertura de testes, gate check commands   |
| `implement.md`             | Execute: implementação + verificação + commits atômicos                |
| `validate.md`              | Verifier: checagem spec-anchored evidence-or-zero + sensor de discriminação |
| `memory.md`                | `STATE.md`: log de decisões (AD-NNN) + pausa/retomada (Handoff)         |
| `lessons.md`               | Camada de lições auto-aprimorável (`scripts/lessons.py`)                |
| `sub-agents.md`            | Delegação a sub-agentes: batch workers por fase + Verifier             |
| `coding-principles.md`     | Diretrizes comportamentais para implementação e voz de escrita          |
| `context-limits.md`        | Orçamento e monitoramento de tokens                                     |
| `code-analysis.md`         | Ferramentas disponíveis e alternativas                                 |

### Scripts (gates determinísticos)

| Script                    | Propósito                                                                |
| -------------------------- | ---------------------------------------------------------------------- |
| `scripts/validate_spec.py` | Gate de fechamento da spec: critérios em formato EARS, assumptions, IDs |
| `scripts/validate_tasks.py`| Cheiro de granularidade, paridade diagrama × dependências, sem dependência para frente |
| `scripts/check_commit.py`  | Valida a mensagem de commit contra Conventional Commits                |
| `scripts/validate_state.py`| Gate de conclusão: exige `validation.md` com veredito PASS e evidência  |
| `scripts/lessons.py`       | Única forma de mutar `.specs/lessons.json` / `.specs/LESSONS.md`        |

Um exit code diferente de zero em qualquer script significa parar e corrigir antes de prosseguir. Scripts só são pulados quando nenhuma ferramenta de execução de código está disponível — nesse caso, o agente faz as mesmas checagens lendo o artefato manualmente.

## ⚡ Dicas para Melhores Resultados

### Faça ✅

- **Seja específico sobre o escopo** — Limites claros previnem scope creep
- **Confie no auto-dimensionamento** — O agente aplica a profundidade certa
- **Use linguagem natural** — Não há necessidade de memorizar comandos
- **Diga "record decision"** para decisões de projeto difíceis de reverter — mantém `STATE.md` como fonte da verdade
- **Diga "pause work" antes de terminar** — Permite retomada sem atritos
- **Desafie o agente** — Se algo parecer errado, diga

### Não Faça ❌

- **Não force todas as fases** — Deixe o agente pular o que for desnecessário
- **Não trabalhe em múltiplas funcionalidades ao mesmo tempo** — Uma funcionalidade por ciclo
- **Não ignore o Verifier** — Ele roda automaticamente; não peça para pular
- **Não aceite respostas vagas** — Se o agente disser algo nebuloso, peça especificidade

## 💡 Recomendação de Modelo

> **Melhores resultados com modelos modernos e capazes de raciocínio:**
>
> - **Claude Opus 4.6 / Sonnet 4.5** — Excelente para todas as fases
> - **Gemini 3 Pro / GPT 5.2** — Raciocínio forte e janela de contexto grande
> - **Gemini 3 Flash / Claude Haiku 4.5** — Ótimo desempenho de uso geral
>
> Se o harness permitir escolher modelo por sub-agente, a skill sugere um tier por papel: Design e fases de alta ambiguidade em tier de raciocínio alto, o Verifier em tier médio-alto (raciocínio adversarial), e workers em fases mecânicas (entidades, config, wiring) em tier mais rápido/barato. Isso é apenas uma recomendação — nenhum gate depende disso.

## 🤖 Compatibilidade

Esta skill funciona com **qualquer agente de codificação de IA** que suporte skills ou instruções personalizadas.

**Testado e verificado em:**

| Agente                | Status    |
| -------------------- | --------- |
| Antigravity (Gemini) | ✅ Testado |
| Claude Code          | ✅ Testado |
| GitHub Copilot       | ✅ Testado |
| Cursor               | ✅ Testado |
| Opencode             | ✅ Testado |

> **Nota:** Se seu agente suporta o carregamento de instruções ou skills personalizadas, esta skill deve funcionar. Os agentes acima são simplesmente onde ela foi ativamente testada.

## ❓ FAQ

**P: Posso pular fases?**
R: Sim! A skill se auto-dimensiona. Design e Tasks são pulados para funcionalidades simples. Você só recebe cerimônia quando o escopo exige.

**P: E se meu projeto já tiver código existente?**
R: A própria fase Specify faz uma varredura leve do código antes de perguntar qualquer coisa (Passo 1 da Cadeia de Verificação de Conhecimento), e Design lê `STATE.md` para respeitar decisões de projeto já tomadas. Não há mais uma fase separada de mapeamento de codebase — o contexto existente é coletado sob demanda, dentro do orçamento de tokens.

**P: Como funciona a rastreabilidade de requisitos?**
R: Cada requisito recebe um ID único (ex.: `AUTH-01`) no spec.md, escrito em notação EARS (WHEN/THEN, WHILE, WHERE, IF/THEN). As tarefas referenciam esses IDs na matriz de cobertura de testes, e o Verifier confirma que o valor testado bate com o resultado definido na spec — não só que existe uma asserção.

**P: O que são commits git atômicos?**
R: Cada tarefa produz exatamente um commit seguindo os [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/), validado por `scripts/check_commit.py` antes de fechar a tarefa.

**P: O que é o Verifier e por que ele roda sempre?**
R: É um sub-agente novo, dispatado automaticamente após o último commit de uma feature — nunca o mesmo agente que escreveu o código (author ≠ verifier). Ele reconfirma a cobertura evidence-or-zero por AC e roda um **sensor de discriminação**: injeta uma falha comportamental pequena em um scratch isolado e confirma que os testes a matam. Isso nunca é opcional nem perguntado ao usuário.

**P: O que é a camada de lições?**
R: Cada falha real detectada pelo Verifier (mutante sobrevivente, gap de precisão de spec, AC sem evidência) vira uma lição de uma frase, gravada via `scripts/lessons.py`. Uma lição só é "confirmada" — e carregada em Specify/Design — depois de se repetir em pelo menos duas features distintas. Um PASS limpo não gera lição nenhuma.

**P: Os scripts Python são obrigatórios?**
R: São o caminho padrão dos gates. Só são pulados quando não há ferramenta de execução de código disponível no harness — nesse caso o agente faz a mesma checagem lendo o artefato manualmente e avisa que está em modo degradado.

**P: Isso funciona com qualquer stack tecnológica?**
R: Sim! A skill é completamente agnóstica de stack e de ferramenta. Funciona com qualquer linguagem, framework ou arquitetura.

**P: E se o agente inventar uma API ou padrão que não existe?**
R: A skill aplica uma rigorosa **Cadeia de Verificação de Conhecimento**: codebase → documentação do projeto → Context7 MCP → busca na web → marcar como incerto. Ela NUNCA fabrica informação. Se o agente não conseguir encontrar documentação, ele dirá "I don't know" em vez de adivinhar.

## 📄 Licença

CC-BY-4.0 © [Tech Lead's Club](https://github.com/tech-leads-club)

<p align="center">
  <sub>Construído com ❤️ pela comunidade Tech Lead's Club</sub>
</p>
