# mermaid-studio

Skill especialista em criar, validar e renderizar diagramas Mermaid com dois motores de saída (SVG/PNG/ASCII), cobrindo mais de 20 tipos de diagrama — incluindo arquitetura C4, `architecture-beta` com ícones de nuvem (AWS/GCP/Azure), flowcharts, sequência, ERD, state, class, mindmap, timeline, git graph, sankey e outros.

## O que faz

- Aplica um conjunto de **regras de ouro** para diagrama elegante por padrão: sempre usar uma diretiva `%%{init}%%` com paleta curada (nunca o tema padrão do Mermaid, que produz linhas pretas duras), linhas suaves (`lineColor: '#94a3b8'`), no máximo ~15 nós por diagrama, labels em linguagem natural e no máximo 3-4 cores por diagrama mapeadas a significado.
- Opera em três modos conforme a intenção do pedido: **Create** (gera só o código `.mmd`), **Render** (renderiza um `.mmd` já existente) e **Full** (cria → valida → renderiza), sendo Full o padrão quando a intenção não é clara.
- Traz uma **matriz de decisão** para escolher o tipo de diagrama certo a partir da descrição do usuário (processo → flowchart, chamadas de API → sequence, schema de banco → ERD, etc.), e carrega arquivos de referência sob demanda apenas quando o tipo de diagrama exige (C4, AWS/cloud, code-to-diagram, temas, troubleshooting).
- Antes de renderizar, sempre valida a sintaxe (`scripts/validate.mjs`), com no máximo 3 tentativas de correção antes de perguntar ao usuário.
- Renderiza para SVG, PNG ou ASCII via `scripts/render.mjs` / `scripts/render-ascii.mjs`, com suporte a mais de 15 temas prontos (`beautiful-mermaid`) além dos 5 temas nativos do `mermaid-cli`, e a pacotes de ícones (Iconify) para diagramas `architecture-beta`.
- Suporta renderização em lote de múltiplos diagramas via `scripts/batch.mjs`.
- Faz **code-to-diagram**: analisa uma codebase existente (dependências de módulo, rotas de API, schema de dados, arquitetura de serviços, máquinas de estado) e gera o diagrama correspondente.

## Quando usar

- Criar ou visualizar arquitetura de sistema, fluxo de dados ou modelo de banco de dados.
- Renderizar um arquivo `.mmd` existente para SVG, PNG ou ASCII.
- Desenhar infraestrutura AWS/cloud com ícones de serviço.
- Documentar fluxos de sistema, diagramas de sequência ou diagramas C4.
- Analisar uma codebase e gerar um diagrama a partir da estrutura do código.
- Qualquer pedido mencionando "mermaid", "diagrama", "flowchart", "diagrama de arquitetura", "diagrama de sequência", "ERD", "C4" ou "diagrama ASCII".

Não use para: geração de imagem que não seja Mermaid, plotagem de dados com bibliotecas de gráfico (chart libraries) ou escrita de documentação geral sem diagrama envolvido.

## Estrutura de arquivos

| Arquivo | Função |
|---------|--------|
| `SKILL.md` | Regras de ouro de estilo, modos de operação, matriz de decisão de tipo de diagrama, fluxo completo de criação/validação/renderização e troubleshooting rápido. |
| `references/diagram-types.md` | Sintaxe completa e detalhada de todos os 20+ tipos de diagrama suportados. |
| `references/c4-architecture.md` | Sintaxe C4 completa, padrão de estilização obrigatório (linhas suaves, `UpdateRelStyle`) e limites de layout (máx. 6 `Rel()` por diagrama). |
| `references/aws-architecture.md` | Sintaxe `architecture-beta`, catálogo de ícones AWS/cloud e instruções de renderização com pacotes de ícone. |
| `references/code-to-diagram.md` | Metodologia de análise de código para gerar diagramas a partir de uma codebase existente. |
| `references/themes.md` | Catálogo completo de temas (nativos do `mermaid-cli` e do motor `beautiful-mermaid`) e exemplos de estilização de sequence/ERD. |
| `references/troubleshooting.md` | Soluções para erros comuns de sintaxe e renderização. |
| `scripts/validate.mjs` | Valida a sintaxe de um arquivo `.mmd` antes de renderizar. |
| `scripts/render.mjs` | Renderiza um `.mmd` para SVG ou PNG, com suporte a temas e pacotes de ícone. |
| `scripts/render-ascii.mjs` | Renderiza um `.mmd` para ASCII (terminais, READMEs). |
| `scripts/batch.mjs` | Renderiza múltiplos diagramas de uma vez, com workers paralelos. |
| `scripts/setup.sh` | Instala os motores de renderização e dependências de pacote de ícone (rodar uma vez por ambiente). |
| `assets/puppeteer-config.json` | Configuração do Puppeteer usada na renderização via Chromium headless. |

## Pré-requisito

Rodar `bash <skill-dir>/scripts/setup.sh` uma vez por ambiente para instalar os motores de renderização (`mermaid-cli` e `beautiful-mermaid`) e as dependências de pacote de ícone.
