# security-best-practices

Skill para revisões de segurança específicas por linguagem e framework, com sugestões de melhoria. Existe para dar ao agente um processo guiado de identificar a stack do projeto, carregar a referência de segurança correspondente e então escrever código seguro por padrão, detectar vulnerabilidades passivamente ou produzir um relatório completo quando solicitado.

## O que faz

- Identifica todas as linguagens e frameworks em uso (frontend e backend, quando aplicável) e carrega os arquivos de referência correspondentes em `references/`, no padrão de nome `<linguagem>-<framework>-<stack>-security.md` (ou a variante `-general-` quando o framework não é especificado).
- Opera em três modos: (1) escrever código novo já seguro por padrão; (2) detectar passivamente vulnerabilidades críticas enquanto trabalha no projeto e avisar o usuário; (3) gerar um relatório de segurança completo e priorizado por severidade quando solicitado.
- Define formato de relatório: resumo executivo no topo, achados numerados com ID, seções por severidade, impacto em uma frase para achados críticos, e referência a números de linha do código citado.
- Define fluxo de correção: uma vulnerabilidade por vez, comentários explicando a prática de segurança aplicada, atenção a regressões, e respeito ao fluxo de commit/teste já configurado no projeto.
- Permite que o usuário sobreponha uma prática de segurança por motivo específico do projeto, sugerindo documentar a decisão em vez de insistir.
- Traz dois avisos gerais válidos para qualquer stack: evitar IDs incrementais para recursos públicos (preferir UUID/hex aleatório) e cuidado ao reportar falta de TLS/HSTS/cookies seguros em ambientes de desenvolvimento sem TLS.

## Quando usar

- Pedido explícito por boas práticas de segurança, revisão/relatório de segurança ou ajuda para escrever código seguro por padrão.
- Projetos em Python, JavaScript/TypeScript ou Go (linguagens com referência documentada nesta skill).

Não use quando: o pedido for revisão de código geral sem foco em segurança, debugging, threat modeling (use `security-threat-model`) ou qualquer tarefa não relacionada a segurança.

## Estrutura de arquivos

| Arquivo | Função |
|---------|--------|
| `SKILL.md` | Fluxo de trabalho, árvore de decisão, formato de relatório e regras de override. |
| `references/golang-general-backend-security.md` | Boas práticas de segurança para backend Go genérico. |
| `references/javascript-express-web-server-security.md` | Boas práticas para servidores Express (Node.js). |
| `references/javascript-general-web-frontend-security.md` | Boas práticas para frontend JavaScript genérico. |
| `references/javascript-jquery-web-frontend-security.md` | Boas práticas para frontend com jQuery. |
| `references/javascript-typescript-nextjs-web-server-security.md` | Boas práticas para servidores Next.js. |
| `references/javascript-typescript-react-web-frontend-security.md` | Boas práticas para frontend React/TypeScript. |
| `references/javascript-typescript-vue-web-frontend-security.md` | Boas práticas para frontend Vue/TypeScript. |
| `references/python-django-web-server-security.md` | Boas práticas para servidores Django. |
| `references/python-fastapi-web-server-security.md` | Boas práticas para servidores FastAPI. |
| `references/python-flask-web-server-security.md` | Boas práticas para servidores Flask. |
