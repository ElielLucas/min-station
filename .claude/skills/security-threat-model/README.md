# security-threat-model

Skill para gerar um modelo de ameaças (threat model) de nível AppSec específico para um repositório ou caminho de projeto, em vez de um checklist genérico. Existe para entregar um documento Markdown acionável, onde cada afirmação arquitetural é ancorada em evidência real do código e as suposições ficam explícitas.

## O que faz

- Conduz um fluxo de 8 etapas: extrair o modelo do sistema (componentes, entrypoints, separação runtime vs CI/dev), derivar boundaries/ativos/pontos de entrada, calibrar capacidades do atacante, enumerar ameaças como abuse paths, priorizar por likelihood × impact, validar suposições com o usuário, recomendar mitigações concretas e rodar um quality check final.
- Exige confirmação do usuário antes do relatório final: resume as suposições que mais afetam a priorização e faz 1–3 perguntas direcionadas (dono do serviço, ambiente, escala, modelo de deploy, authn/authz, exposição à internet, sensibilidade de dados, multi-tenancy).
- Classifica risco em alto (RCE pré-auth, bypass de autenticação, acesso cross-tenant, exfiltração de dados sensíveis, roubo de chave/token, comprometimento de integridade de modelo/config, sandbox escape), médio (DoS direcionado, exposição parcial de dados, bypass de rate-limit, poisoning de logs/métricas) e baixo (leaks de baixa sensibilidade, DoS ruidoso de fácil mitigação).
- Distingue mitigações já existentes (com evidência) de mitigações recomendadas, amarrando cada uma a um componente/boundary/entry point concreto.
- Salva o resultado final em Markdown como `<nome-do-repo-ou-dir>-threat-model.md`.

## Quando usar

- Pedido para threat model de um codebase ou caminho específico.
- Pedido para enumerar ameaças ou abuse paths de um sistema.
- Necessidade de uma análise AppSec formal antes de decisões de arquitetura ou segurança.

Não use quando: o pedido for um resumo geral de arquitetura, revisão de código, boas práticas de segurança (use `security-best-practices`) ou trabalho de design não relacionado a segurança.

## Estrutura de arquivos

| Arquivo | Função |
|---------|--------|
| `SKILL.md` | Fluxo completo de 8 etapas, critérios de priorização e contrato de saída. |
| `references/prompt-template.md` | Template de prompt e contrato de formato de saída a ser seguido literalmente. |
| `references/security-controls-and-assets.md` | Lista de referência opcional de controles e ativos de segurança. |
