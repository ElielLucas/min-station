# codenavi

Skill que atua como guia metódico para navegar em códigos desconhecidos, confusos ou mal documentados. Investiga antes de agir, executa com precisão cirúrgica e nunca assume o que não sabe. Existe para reduzir retrabalho e erros em tarefas de desenvolvimento em bases de código não familiares, transformando cada descoberta em conhecimento persistente guardado em `.notebook/`.

## O que faz

- Aplica um ciclo de missão fixo para toda tarefa: **Briefing → Recon → Plan → Execute → Verify → Debrief**, com disciplina de tokens (ler só o necessário, usar grep/busca em vez de leitura sequencial).
- Mantém uma base de conhecimento (`.notebook/`) que cresce entre sessões: `INDEX.md` como índice compacto e notas individuais por flow, pattern, gotcha ou domain, sempre referenciando código por `arquivo:função()` (nunca colando blocos de código, que ficam obsoletos).
- Define uma "Knowledge Verification Chain" para validar conhecimento antes de aplicar: `.notebook/` → docs do projeto → MCP Context7 → busca web → declarar incerteza explicitamente como último recurso.
- Convoca aliados (skills carregadas, MCPs como Context7, busca web, ferramentas nativas) em ordem de prioridade antes de tentar resolver algo do zero.
- Escala a cerimônia do ciclo conforme o tamanho da missão: trivial (typo/rename) vira plano de uma linha; padrão (bug fix, feature pequena) usa ciclo completo; complexa (mudança arquitetural) estende o Recon; exploração (entender um flow) tem o Recon como entregável principal.
- Segue regras de execução cirúrgica: simplicidade primeiro, tocar só o que a missão exige, casar com o estilo já existente, nunca silenciar convenções conflitantes sem avisar o desenvolvedor.

## Quando usar

- Corrigir bugs, implementar features, refatorar ou investigar fluxos em uma base de código pouco familiar.
- Perguntas do tipo "como isso funciona", "investiga esse fluxo", "me ajuda com esse código", "corrige isso", "implementa isso".
- Onboarding em um módulo desconhecido, onde entender o fluxo já é o entregável principal.

Não use quando: a tarefa é scaffolding de projeto do zero (greenfield), configuração de CI/CD ou provisionamento de infraestrutura.

## Estrutura de arquivos

| Arquivo | Função |
|---------|--------|
| `SKILL.md` | Ciclo de missão completo (Briefing, Recon, Plan, Execute, Verify, Debrief), regras de ouro, sistema de convocação de aliados e exemplos completos de uso. |
| `references/coding-principles.md` | Princípios de codificação a seguir na fase de Execute: pensar antes de codificar, simplicidade, mudanças cirúrgicas, execução orientada a metas, respeito às convenções do projeto, boas práticas de linguagem, dependências, tratamento de erro, testes e comentários. |
| `references/notebook-spec.md` | Especificação do formato do `.notebook/`: estrutura de pastas, formato do `INDEX.md`, formato das notas individuais, gatilhos para criar/atualizar notas e orçamento de tokens. |

## Exemplo de uso

A própria skill traz três exemplos completos no `SKILL.md`: correção de bug de cupom em checkout (rastreando da entrada até a causa raiz, documentando no `.notebook/`), mapeamento do fluxo de autenticação de um projeto desconhecido, e adição de validação com Zod consultando documentação atual via MCP Context7 antes de implementar.
