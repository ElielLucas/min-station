## Introdução

## O que é um POP?

**POP (Procedimento Operacional Padrão)** é um **documento descritivo**, em formato de manual ou guia, que detalha o problema ou necessidade a ser endereçada e o **passo a passo** para executar tarefas específicas de forma repetível na organização. É uma espécie de manual interno que detalha tudo que deve ser feito para que a operação seja padronizada e seguindo critérios de qualidade.

Objetivos típicos: **consistência**, **qualidade**, **redução de erros** e **transferência de conhecimento** entre pessoas e turnos.

---

## O que NÃO é um POP

- Não é **documentação técnica extensa de código** (classes, APIs linha a linha) — pode _referenciar_ onde isso existe
- Não é **backlog de tarefas** nem lista de issues sem o "como" e o "quando"
- Não é apenas um **checklist solto** sem contexto, papéis, insumos e critérios de pronto
- Não é um **documento genérico** que qualquer time poderia usar sem adaptação ao seu contexto

---

## Como utilizar esse documento?

- Tópicos marcados como **_(Opcional)_** devem ser **preenchidos ou removidos conforme o contexto**; se não se aplicam, remova a seção ou indique "Não aplicável" com uma linha de justificativa
- Os demais tópicos devem estar **obrigatoriamente preenchidos** com conteúdo acionável
- Novos tópicos podem ser adicionados quando **agregarem clareza** sem repetir o que já está em Passo a passo

---

## Dicas importantes

Um bom POP deve responder com clareza:

- **O que fazer**
- **Como fazer**
- **Como saber que está correto** (evidência, validação, critério de pronto)

**Critério de qualidade:** se alguém **novo no time** não conseguir executar o processo e entender **por que** cada passo existe **apenas lendo este documento**, o POP **ainda não está bom o suficiente**.

- Evite **ambiguidade**; use verbos no imperativo e uma ação por passo quando possível
- Prefira **exemplos práticos** (entradas/saídas, links internos, nomes de ferramentas)
- **Documente decisões** ("se A então X; se B então Y") e não só cliques
- Se algo depender de contexto (ambiente, permissão, janela de manutenção), **deixe explícito**

---

# 1. Identificação e controle de documento

| Identificação                | Detalhes                                                     |
| :--------------------------- | :----------------------------------------------------------- |
| **Código do POP**            | [POP-XXX-001 — remover se a org não usa numeração]           |
| **Nome do POP**              | [TÍTULO DO POP]                                              |
| **Responsável**              | [NOME COMPLETO]                                              |
| **Autor**                    | [NOME COMPLETO — remover se igual ao Responsável]            |
| **Aprovadores**              | [NOMES ou PAPÉIS — remover se não houver fluxo formal]       |
| **Criado em**                | [DD/MM/AAAA]                                                 |
| **Data de entrega**          | [DD/MM/AAAA — remover se não aplicável]                      |
| **Data de vigência**         | [DD/MM/AAAA — remover se não houver data de vigência formal] |
| **Periodicidade de revisão** | [Ex.: Trimestral — remover se não houver ciclo definido]     |
| **Versão**                   | 1.0                                                          |
| **Status**                   | 🟢 Ativo                                                     |

## 1.1 Controle de vigência e revisão _(Opcional)_

- Este POP entra em vigor em **[DD/MM/AAAA]**.
- A revisão ordinária ocorre a cada **[período — ex.: 90 dias, semestral, anual]**.
- Revisões extraordinárias devem ocorrer quando houver:
  - [Gatilho 1 — ex.: mudança de política relevante para o processo]
  - [Gatilho 2 — ex.: entrada ou remoção de ferramenta/sistema obrigatório]
  - [Gatilho 3 — ex.: ajuste estrutural no fluxo operacional]

## 1.2 Critérios de versionamento _(Opcional)_

- **x.y** para ajustes incrementais sem ruptura de fluxo.
- **x+1.0** para mudança estrutural significativa no procedimento.
- Toda nova versão deve registrar: data de publicação, responsável, resumo das alterações e impacto operacional esperado.

---

# 2. Propósito (Objetivo)

**Descrição:** Explique o **motivo da existência deste POP**, **qual problema ou necessidade recorrente** ele resolve e o que acontece sem ele. O objetivo deve contextualizar o problema — não apenas descrever "o que faz", mas por que este documento é necessário e qual impacto a ausência do processo gera.

>

---

# 3. Escopo, limites e responsabilidades _(Opcional)_

**Descrição:** Delimita claramente o que este POP cobre, o que está fora do escopo e quem é responsável por cada atividade. Use quando o processo envolver múltiplas áreas, perfis ou quando os limites precisarem ser explícitos para evitar uso indevido.

## 3.1 Escopo do POP

**Descrição:** O que este POP cobre — sistemas, áreas, perfis, contextos ou trilhas aplicáveis.

>

## 3.2 Limites e fora de escopo

**Descrição:** O que este POP **não** cobre. Ser explícito evita interpretações indevidas do documento.

Este POP **não** cobre:

- [Atividade ou contexto fora do escopo]
- [Outra atividade ou contexto fora do escopo]

## 3.3 RACI simplificado por perfil _(Opcional)_

**Descrição:** Use quando houver **mais de um papel** envolvido. Remova se o processo for executado por uma única pessoa.

| Atividade     | [Papel 1] | [Papel 2] | [Papel 3] |
| :------------ | :-------: | :-------: | :-------: |
| [Atividade 1] |     R     |     C     |     I     |
| [Atividade 2] |     A     |     R     |     C     |

**Legenda RACI**

| Sigla | Significado | Uso prático                                                 |
| :---: | :---------- | :---------------------------------------------------------- |
| **R** | Responsável | Executa diretamente a atividade                             |
| **A** | Aprovador   | Dá aprovação final e assume a decisão                       |
| **C** | Consultado  | **(Opcional)**: Deve ser envolvido antes da decisão final   |
| **I** | Informado   | **(Opcional)**: Recebe status e evidências, sem ação direta |

---

# 4. Termos e definições _(Opcional)_

**Descrição:** Glossário dos principais termos, siglas e ferramentas relevantes para o entendimento e execução do processo. Use quando o domínio tiver vocabulário específico que precise ser compartilhado com novos integrantes. Para cada termo, inclua um exemplo prático em blockquote. Agrupe por categoria quando houver muitos termos.

- **[Termo ou sigla]:** definição clara e objetiva do que é e para que serve.
  > **Exemplo:** [exemplo concreto de uso ou ocorrência no contexto deste processo].
- **[Outro termo]:** definição.
  > **Exemplo:** [exemplo concreto].

---

# 5. Passo a passo

**Descrição:** Sequência ordenada e executável de etapas do processo, do gatilho inicial ao encerramento. Cada etapa deve ser executável por quem não participou da criação deste documento. Use o padrão atômico abaixo — simplifique quando a etapa for simples o suficiente.

### Etapa 1 — [Nome descritivo]

**Ação:** O que esta etapa realiza em uma frase.

**Entrada:** O que precisa estar disponível ou concluído antes de iniciar.

**Execução:**

- [Passo com verbo no imperativo — nomeie o sistema, ferramenta ou campo exato]
- Se [condição], então [ação]; se [condição alternativa], então [ação alternativa]

**Saída esperada:** O que deve existir ao final desta etapa (artefato, estado, evidência).

**Validação objetiva:** Como confirmar que está correto — teste, aprovação, log, métrica, checklist.

**Se falhar:** Ação a tomar; limite de tentativas quando aplicável; quando escalar.

---

### Etapa 2 — [Nome descritivo]

>

---

### Etapa 3 — [Nome descritivo]

>

---

**Regras transversais de falha _(Opcional)_**

Use quando o processo tiver múltiplas etapas críticas e regras globais de tratamento de erro se aplicarem a todo o fluxo:

- **Retry controlado:** máximo de [N] tentativas na mesma etapa antes de mudar estratégia.
- **Fallback:** após [N] tentativas sem resultado, [ação alternativa] e registre o motivo.
- **Rollback:** obrigatório diante de [condição — ex.: regressão funcional, falha de validação].
- **Escalamento imediato:** [condição — ex.: incidente de segurança, bloqueio acima do SLA].

---

# 6. Resumo _(Opcional)_

**Descrição:** Síntese do processo em linguagem executiva — o problema que o POP resolve, o fluxo de etapas em alto nível e os recursos ou ferramentas envolvidos. Use quando o POP for extenso ou precisar de uma visão gerencial rápida para onboarding.

>

---

# 7. Resultados esperados

**Descrição:** O que deve ser **entregue ao final do processo** e como validar que o resultado está correto.

>

---

# 8. Riscos e controles _(Opcional)_

**Descrição:** Riscos identificáveis no processo e controles ou mitigações correspondentes.

- **Risco:** [descrição do risco].
- **Solução:** [ação de mitigação ou controle].
  <br>
- **Risco:** [descrição do risco].
- **Solução:** [ação de mitigação ou controle].

---

# 9. Checklist de implantação _(Opcional)_

**Descrição:** Lista de verificação para garantir que todos os pré-requisitos estejam atendidos antes do go-live ou da primeira execução formal do processo. Agrupe por categoria. Responsável: [papel].

**[Categoria 1]**

- [ ] [Item verificável com critério claro de conclusão]
- [ ] [Item verificável]

**[Categoria 2]**

- [ ] [Item verificável]
- [ ] [Item verificável]

---

# 10. Critérios de decisão _(Opcional)_

**Descrição:** Defina **como decisões devem ser tomadas durante o processo** — situações onde há mais de um caminho possível e o executor precisa de critério objetivo para escolher.

**Exemplo:**

- Quando usar abordagem A vs B
- Quando escalar um problema

>

---

# 11. Fluxo / Fluxograma _(Opcional)_

**Descrição:** Representação **visual do processo** (link, diagrama Mermaid ou descrição da sequência).

>

---

# 12. Materiais de apoio _(Opcional)_

**Descrição:** Documentos, arquivos, planilhas, links ou referências externas que apoiam a execução ou o entendimento do processo.

- [Nome do material]: `[caminho ou link]`
- [Nome do material]: `[caminho ou link]`

---

# 13. Observações _(Opcional)_

**Descrição:** Informações adicionais **relevantes para o entendimento ou execução** que não se encaixam nas seções anteriores (ex.: janelas de manutenção, SLAs, exceções conhecidas).

>

---
