# Context7 — Consulta Sob Demanda de Documentação de Libs

## O que é

Skill que consulta o **MCP Context7** (Upstash) para buscar documentação atualizada e
correta por versão de qualquer biblioteca, framework, SDK ou API. O objetivo é reduzir
código gerado com base em conhecimento de treino desatualizado ou alucinado — mas **só
quando você pede explicitamente**, para não gastar chamadas MCP/tokens em toda tarefa
que menciona uma lib.

## Como acionar a skill

Dispara **apenas** quando o pedido inclui um pedido explícito de verificar/checar/buscar
documentação. Exemplos que disparam:

- "usa o context7", "consulta o context7", "invoca o context7", "/context7"
- "verifica a documentação atual do Prisma antes de continuar"
- "confirma a assinatura correta desse método do axios na versão 5"
- "isso mudou entre versões do zod? confere a API oficial"
- "check the latest docs for the Stripe SDK"

**Não dispara** só porque o pedido menciona implementar/integrar uma lib — ex.: "integre
a API de pagamentos do Stripe nesse checkout" ou "migre esse serviço de Prisma 4 para
Prisma 5" seguem como implementação normal, sem consulta automática. Se quiser a
verificação, peça explicitamente.

## Fluxo por trás dos panos

1. O agente identifica o nome da lib (e a versão, se der pra inferir do
   `package.json`/`requirements.txt`/etc.).
2. Chama `resolve-library-id` no MCP Context7 para achar o identificador correto da lib.
3. Chama `get-library-docs` com esse identificador para buscar a documentação da versão
   certa.
4. Usa essa documentação como fonte de verdade antes de escrever o código.

## Pré-requisito

MCP `context7` conectado e ativo. Instale com:

```bash
npx @sd-norven/agent-playbook@latest mcp install context7
```

## Chave de API (opcional)

Funciona sem chave, com rate limit público. Para aumentar o limite:

1. Gere uma chave em https://context7.com/dashboard.
2. Exporte `CONTEXT7_API_KEY` no seu shell (`~/.bashrc`/`~/.zshrc`) antes de abrir o
   agente.

## Quando a skill NÃO age

- Qualquer pedido de implementação/integração sem verificação/checagem explícita de
  documentação — mesmo para lib nova no projeto.
- Lógica de negócio pura, sem lib de terceiros envolvida.
- Built-ins triviais da linguagem.
- Perguntas específicas de **Vuetify** — o MCP dedicado `vuetify` responde melhor
  (versionado por release do Vuetify).
- **Figma** para código — use a skill `figma-implement-design`.
- Leitura de tarefas do **Simpli Projects** — use a skill `simpli-project`.

## Troubleshooting

| Problema | Solução |
|---|---|
| "MCP context7 não conectado" | Rode o comando de instalação acima e reinicie o agente. |
| `resolve-library-id` não encontra a lib | Use o nome exato do pacote (ex.: `@upstash/redis`, não "Redis"). |
| Rate limit atingido | Configure a chave de API opcional (veja acima). |
| A skill não disparou | Peça de forma explícita: "consulta o context7 pra verificar isso." |
