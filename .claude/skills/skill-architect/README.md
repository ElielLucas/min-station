# skill-architect

Guia especializado para projetar e construir **skills de alta qualidade do zero**, através de uma conversa estruturada em fases — não um gerador que despeja um template, mas um processo que primeiro entende profundamente o problema do usuário antes de escrever qualquer SKILL.md. Cobre tanto skills standalone quanto workflows aprimorados por MCP.

## O que faz

- Conduz o usuário por 5 fases sequenciais: **Discovery → Architecture → Craft → Validate → Deliver**, sem nunca pular a Discovery.
- Na fase de Discovery, levanta 2-3 casos de uso concretos (trigger, passos, ferramentas, resultado esperado) e identifica a categoria da skill (Document & Asset Creation, Workflow Automation, MCP Enhancement).
- Na fase de Architecture, escolhe o padrão estrutural primário (Sequential Workflow, Multi-MCP Coordination, Iterative Refinement, Context-Aware Selection, Domain-Specific Intelligence — detalhados em `references/patterns.md`), planeja a estrutura de pastas (`SKILL.md`, `scripts/`, `references/`, `assets/`) e desenha o campo `description` seguindo a fórmula "O que faz + Quando usar (com gatilhos) + Quando NÃO usar".
- Na fase de Craft, escreve o frontmatter (regras rígidas: kebab-case, nunca usar "claude"/"anthropic" no nome, description em uma única linha, sem `<` `>`, license `CC-BY-4.0`) e o corpo do SKILL.md com instruções imperativas, exemplos realistas e referências claras a arquivos auxiliares.
- Na fase de Validate, roda o checklist de `references/quality-checklist.md` e o script `scripts/validate_skill.py` para checagem estrutural automatizada, além de testar mentalmente frases-gatilho que devem e não devem disparar a skill.
- Na fase de Deliver, empacota a skill final e apresenta um resumo (o que faz, como instalar, frase de teste sugerida).
- Reforça princípios transversais: progressive disclosure em 3 níveis (frontmatter → corpo do SKILL.md → arquivos linkados), composabilidade com outras skills já carregadas, e a regra de nunca incluir README.md dentro da pasta da skill (skills são escritas para agentes, não humanos).

## Quando usar

- "criar uma nova skill" / "construir uma skill" / "desenhar uma skill"
- "transforma isso em uma skill" / "quero automatizar esse workflow" / "como eu ensino meu agente a fazer X"
- Pedidos envolvendo a criação de arquivos SKILL.md, sejam skills standalone ou que envolvam ferramentas MCP

Não use quando: o pedido for para criar um **subagent** (use `subagent-creator` ou `cursor-subagent-creator`) ou um **technical design document** (use `create-technical-design-doc`); também não use para melhorar, avaliar ou fazer benchmark de uma skill já existente — a própria skill direciona esses casos para uma skill `skill-creator` separada.

## Estrutura de arquivos

| Arquivo | Função |
|---------|--------|
| `SKILL.md` | Workflow completo das 5 fases (Discovery, Architecture, Craft, Validate, Deliver) com regras de frontmatter e anti-padrões. |
| `references/patterns.md` | Os 5 padrões de arquitetura de skill, com templates de estrutura e critérios de quando escolher cada um. |
| `references/examples.md` | Exemplos de descriptions boas e más, e princípios de escrita de instruções. |
| `references/quality-checklist.md` | Checklist de validação estrutural (pass/fail) e de qualidade da description (score 1-5). |
| `scripts/validate_skill.py` | Script Python que valida uma pasta de skill (frontmatter, casing, kebab-case, ausência de README.md, etc.), com saída em texto ou JSON. |

## Exemplo de uso

Comando de validação sugerido na fase Validate:

```bash
python scripts/validate_skill.py <caminho-para-pasta-da-skill>
python scripts/validate_skill.py <caminho-para-pasta-da-skill> --format json
```

Estrutura de description recomendada (fase Architecture):

```
[O que faz] + [Quando usar, com frases-gatilho específicas] + [O que NÃO usar para]
```
