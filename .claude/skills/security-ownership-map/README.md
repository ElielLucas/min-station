# security-ownership-map

Skill para analisar repositórios git e construir uma topologia de propriedade (ownership) com foco em segurança — relacionando pessoas a arquivos, calculando bus factor e identificando código sensível órfão. Existe para responder perguntas de risco organizacional grounded em histórico real de commits, exportando os resultados em CSV/JSON para uso em grafos (Neo4j/Gephi) ou consultas pontuais.

## O que faz

- Constrói um grafo bipartido pessoas↔arquivos a partir do histórico git e calcula risco de propriedade (bus factor, código sensível sem dono ativo).
- Constrói também um grafo de co-mudança de arquivos (similaridade de Jaccard sobre commits compartilhados), ignorando por padrão commits "ruidosos" (lockfiles, `.github/*`, configs de editor) e commits de bots como Dependabot.
- Detecta comunidades de arquivos por padrão (pode ser desativado com `--no-communities`) e identifica os principais mantenedores de cada comunidade.
- Aceita regras de sensibilidade customizadas via CSV (padrão glob, tag, peso) para marcar caminhos como `auth`, `crypto`, `secrets` etc.
- Exporta artefatos (`people.csv`, `files.csv`, `edges.csv`, `cochange_edges.csv`, `summary.json`, `communities.json`, grafos `.graphml` opcionais) e oferece um helper de consulta (`query_ownership.py`) que retorna fatias JSON pequenas sem carregar o grafo completo no contexto.
- Inclui detecção de fuso horário por pessoa com base no offset dos commits.

## Quando usar

- Pedido explícito por análise de ownership ou bus factor orientada a segurança, baseada em histórico git.
- Perguntas como: código sensível órfão, mantenedores de segurança, conferência de CODEOWNERS contra risco real, hotspots sensíveis ou clusters de propriedade.

Não use quando: o pedido for por uma lista geral de mantenedores sem viés de segurança, perguntas de ownership não relacionadas a segurança, ou threat modeling (use `security-threat-model`).

## Estrutura de arquivos

| Arquivo | Função |
|---------|--------|
| `SKILL.md` | Fluxo de uso, parâmetros, formato de saída e exemplos de consultas. |
| `scripts/run_ownership_map.py` | Gera o mapa de ownership a partir do histórico git (artefatos CSV/JSON/graphml). |
| `scripts/query_ownership.py` | Consulta os artefatos gerados, retornando fatias JSON bounded (pessoas, arquivos, comunidades, co-mudança, resumo). |
| `scripts/community_maintainers.py` | Calcula mantenedores por comunidade em janelas de tempo (mensal/trimestral). |
| `scripts/build_ownership_map.py` | Lógica de construção do grafo de ownership/co-mudança usada pelo runner. |
| `references/neo4j-import.md` | Constraints e Cypher para importar os CSVs no Neo4j, com dicas de visualização. |
