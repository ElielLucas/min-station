# AS-05 — Roteiro de revisão independente e homologação formal

**Estado:** roteiro; **não é parecer emitido**. Deve ser preenchido por pessoa que não seja o autor dos artefatos avaliados.

## Identificação do parecer

- Etapa: `[AS-01 / AS-02 / AS-04]`
- Nome do autor dos artefatos: `[a preencher]`
- Nome/afiliação do revisor: `[a preencher]`
- Data e ambiente: `[a preencher]`
- Commit/branch e hash do snapshot: `[a preencher]`
- Arquivos e versões efetivamente consultados: `[a preencher]`
- Veredito: `[PENDING | PASS | FAIL | PASS_WITH_RESERVATIONS]`

**Importante:** `PASS_WITH_RESERVATIONS` só pode virar `PASS` no gate automatizado se todas as ressalvas bloqueantes tiverem sido sanadas ou formalmente afastadas, com evidência. Revisão por IA que também participou da autoria **não satisfaz** a exigência `author != reviewer`.

## AS-01 — Matemática

- [ ] U (`baseline.py`) corresponde ao problema físico enunciado, com S∩T, permanência e terminais como estações potenciais.
- [ ] A1–A7 são verificadas termo a termo para os quatro tipos de vértice.
- [ ] Prova de exatidão inteira A é completa; dependência da exatidão de U está provada ou tem referência válida.
- [ ] Prova U-LP = A(um grupo)-LP: levantamento explícito para S∩T e y fracionário.
- [ ] Prova de refinamento LP: projeção por soma preserva A1–A5, p e h.
- [ ] A unitária↔B: decomposição de fluxos e voltas à origem, ou veredito `UNPROVEN`.
- [ ] F-CC→B: revisão das hipóteses P2/R3 ou veredito `UNPROVEN`.
- [ ] Contraexemplo T18 verificado em aritmética racional, incluindo os dois sentidos de bound.
- [ ] Sec59: limites 11/3 e 9/2, partição testemunha e separação do K completo.
- [ ] Se alguma prova for corrigida, alteração documentada e testes repetidos.

## AS-02 — Correção de implementação

- [ ] Conferência independente de cada equação compilada com seu enunciado matemático.
- [ ] Domínios y,f,g,p,h, identificação S∩T e regras de partição.
- [ ] Oráculo físico é suficientemente independente e suas hipóteses são compatíveis com os benchmarks.
- [ ] Exaustão de instalações em casos pequenos; mutação que remove A5 é detectada.
- [ ] Sec59 e outras instâncias adversariais reproduzidas; demonstrar não extrapolação.
- [ ] Comparação baseline U vs implementação de controle `compile_u`, explicando fluxo inteiro/contínuo.
- [ ] Logs de execução com Gurobi e flags/famílias de restrições relevantes.
- [ ] Gate AS-02: `physical_exhaustion_passed` e `sec59_lp_passed` sustentados por registros reais.

## AS-04 — Metodologia de comparação

- [ ] U **sem K**, U+K, A2+K correspondem às definições corretas e compartilham o mesmo conjunto K quando aplicável.
- [ ] C1/C2/C4-DM: validade universal, implementação e tratamento de S∩T; verificar independentemente do gerador.
- [ ] O hash estrutural inclui dados que determinam A_r; isolamento de instâncias confirmado.
- [ ] A2 selecionada pela política AS-03, jamais substituída post hoc pela testemunha Sec59.
- [ ] Política solver homogênea: threads, seed, parâmetros, warm start e orçamento.
- [ ] Gurobi real: executar pelo menos um controle pareado; guardar versão, logs, métricas, hardware e tempos.
- [ ] LP interrompido é censurado; status `OPTIMAL_NUMERIC` não é prova racional.
- [ ] Modelos restritos/CORE não entram como se fossem F-CC completa nem instalações físicas.
- [ ] Reproduções de seeds 43/44 preservam partição, K e identidade estrutural.
- [ ] Limite de variáveis/memória é registrado de modo prospectivo; linhas censuradas não somem.

## Evidências a entregar

Parecer Markdown específico e original por etapa, contendo **matriz de itens julgados**, prova ou achado concreto para cada bloco, referência `arquivo:linha`, logs gerados no ambiente do revisor, veredito e assinatura/identificação. Para aprovar, o revisor deve declarar explicitamente que leu e verificou as demonstrações essenciais, não apenas a execução dos testes.

Na integração, adicionar os caminhos dos pareceres emitidos ao JSON revisado, mantendo nomes reais do autor e de um revisor distinto. O comando `as05_review_preflight.py` fornece diagnóstico de preenchimento, **não autentica revisão humana**.
