# git-commit

Skill que gera e **executa** commits git (`git add` + `git commit`, nunca `git push`) a partir das mudanças staged/unstaged do usuário, com foco em commits pequenos, focados e seguros.

## O que faz

- Analisa `git status`, `git diff --stat` e `git log` recente antes de agir, reaproveitando essa leitura para todos os grupos de commit da sequência.
- Roda um **gate de secrets** antes de qualquer `git add`: bloqueia nome de arquivo suspeito (`.env*`, `*.pem`, `*.key`, `*credentials*` — exceto templates como `.env.example`) e conteúdo suspeito (chaves AWS, blocos `PRIVATE KEY`, `password=`, `secret=`, `token=` etc.). A checagem de conteúdo usa `grep -Eiq` (quiet) e decide só pelo exit code — nunca imprime a linha do segredo no contexto do agente (evita exfiltração). Se achar algo, para, diz qual arquivo bateu no gate e deixa o usuário inspecionar — nunca exclui em silêncio.
- Agrupa mudanças em **vários commits focados** por intenção > área (backend/frontend/infra/docs) > tipo de mudança, em vez de um commit gigante; só faz commit único quando a mudança é realmente uma unidade lógica só ou o usuário pediu explicitamente.
- Usa um vocabulário fixo de tipo de commit (`feat`, `fix`, `refactor`, `docs`, `test`, `build`, `review`) no formato `<type>: <descrição>`, com subject ≤50 chars no primeiro `-m` e o corpo detalhado num **segundo** `-m` (recomendação do Git: subject curto no grafo, descrição só ao abrir o commit).
- Nunca roda `git push`, `git rebase`, `git reset --hard`, `git checkout --` ou `git commit --amend` — são ações só do usuário, sem exceção. Também nunca mexe no stash (`git stash` e derivados), que poderia trazer código não relacionado pro commit.
- Nunca pula hooks (`--no-verify`) ou assinatura (`--no-gpg-sign`); se um hook rejeitar o commit, reporta a saída e para, em vez de tentar contornar.
- Nunca usa `git add -A`/`git add .`/`git add -f` — sempre arquivos/paths explícitos, e sempre com `git add -- "<path>"` (com `--` e aspas) pra um nome de arquivo com metacaracteres de shell nunca ser interpretado como código.
- Nunca adiciona trailers de atribuição de IA (`Co-Authored-By`, `Generated with`, etc.) na mensagem de commit.
- Tem um modo "escape hatch": se o usuário pedir "só mostra os comandos"/"print only", imprime os comandos num único bloco de código sem executar.

## Quando usar

- Pedidos como `/commit`, "faça um commit", "crie um commit", "separa em commits", "sugira uma mensagem de commit".
- Revisão do staging/status antes de commitar.

### Modos de uso

- **`/commit`** — modo padrão: agrupa as mudanças em commits lógicos e **executa** `git add` + `git commit` de fato.
- **`/commit print only`** (ou "só mostra os comandos", "não commita ainda") — modo escape hatch: gera os mesmos comandos `git add`/`git commit`, mas só imprime, num único bloco de código, sem executar nada.

Não use para: `git push`, abertura de pull requests, ou reescrita de histórico já publicado/compartilhado (rebase, amend em commits que já foram para o remoto).

## Configuração recomendada (evitar trailer de IA)

Algumas ferramentas injetam o trailer de atribuição de IA (`Co-Authored-By`, `Generated with`, etc.) por fora do texto gerado pelo modelo — nesse caso, nenhuma instrução na mensagem resolve, é preciso desligar na configuração da ferramenta:

- **Claude Code**: em `settings.json`, defina `includeCoAuthoredBy: false` e `attribution: {commit: "", pr: ""}`.
- **Cursor**: em Settings → Rules/Attribution, desative o trailer; ou rode `cursor /update-cli-config`.

## Relação com o MCP do GitHub

O MCP oficial do GitHub (`github/github-mcp-server`) tem ferramentas como `create_or_update_file` e `push_files` que também criam commits, mas via API REST do GitHub, sem passar pelo working copy local: não leem staged/unstaged, não rodam hooks locais, não assinam com o GPG do usuário, não agrupam mudanças por intenção/tipo e não têm gate de secrets. São complementares, não substitutos — o MCP serve para operações remotas via API; esta skill cobre o fluxo local de commit.