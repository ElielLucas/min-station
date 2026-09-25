# Barreira de qualidade para POP

Use esta barreira antes da entrega final do `.md`. Se qualquer gate falhar, refine o POP na seção indicada e repita a validação.

## Gate 1 — Identificação e controle

**Critério**
- Nome do POP preenchido e específico.
- Responsável com nome completo.
- Datas em DD/MM/AAAA.
- Versão presente (padrão inicial 1.0).
- Status explícito (padrão: 🟢 Ativo).
- Vigência e revisão quando o processo exigir governança formal.

**Como verificar**
- Conferir tabela de identificação.
- Procurar placeholders (`xx/xx/xxxx`, `[NOME COMPLETO]`, `[TÍTULO DO POP]`).
- Confirmar consistência de datas e status.

**Se falhar**
- Refinar seção de identificação.
- Revalidar antes de seguir para outros gates.

## Gate 2 — Núcleo executável das etapas

**Critério**
- Toda etapa relevante tem: Ação, Entrada, Execução, Saída esperada, Validação objetiva, Se falhar.
- Subpassos usam verbo no imperativo.
- Fluxo cobre gatilho inicial até encerramento.
- Há critérios de decisão explícitos quando existem ramificações.

**Como verificar**
- Revisar seção de passo a passo linha a linha.
- Procurar etapas sem saída ou sem validação.
- Verificar se há pelo menos um caminho de falha para blocos críticos.

**Se falhar**
- Refinar seção de passo a passo e, se necessário, critérios de decisão.
- Quebrar etapas longas em etapas atômicas.

## Gate 3 — Rastreabilidade e governança

**Critério**
- Papéis claramente atribuídos.
- Se houver múltiplos papéis, RACI explícito.
- Aprovadores documentados quando existir fluxo formal.
- Gatilhos de revisão/versionamento quando aplicável.

**Como verificar**
- Conferir seção de escopo, responsabilidades e aprovações.
- Validar se cada decisão relevante aponta quem decide/quem aprova.

**Se falhar**
- Incluir tabela RACI ou explicitar owner único.
- Completar campos de aprovação e revisão.

## Gate 4 — Teste do novato no time (expandido)

**Critério**
1. Papéis: está claro quem executa.
2. Início/fim: gatilho de início e definição de pronto.
3. Atomicidade: ações observáveis, sem salto lógico oculto.
4. Ferramentas/lugares: sistemas e contextos nomeados.
5. Validação: forma objetiva de conferir cada bloco crítico.
6. Decisão: caminhos se/senão com critério explícito.
7. Falha: retry, fallback, rollback ou escalação documentados.
8. Ambiguidade: texto sem interpretações conflitantes.

**Como verificar**
- Simular leitura por alguém novo no time.
- Perguntar: "Consigo executar sem perguntar nada ao autor?"

**Se falhar**
- Reescrever trechos ambíguos.
- Adicionar contexto operacional faltante.

## Gate 5 — Política anti-resumo

**Critério**
- Nomes de ferramentas/sistemas/papéis preservados.
- Decisões fornecidas pelo usuário aparecem explicitamente.
- Conteúdo rico não foi comprimido em prosa genérica.
- Detalhes operacionais críticos continuam no fluxo executável.

**Como verificar**
- Comparar entradas do usuário com conteúdo final.
- Procurar generalizações vagas substituindo termos específicos.

**Se falhar**
- Reintroduzir detalhes removidos.
- Reestruturar em etapas atômicas sem perda semântica.

## Gate 6 — Sem placeholders e sem ambiguidade

**Critério**
- Zero placeholders técnicos/editoriais no documento emitido.
- Zero trechos "TBD", "a definir", "[...]" sem justificativa de não aplicável.
- Sem blocos `>` vazios em seções usadas.

**Como verificar**
- Busca textual por placeholders comuns.
- Revisão final de seções opcionais.

**Se falhar**
- Substituir placeholders por valores reais.
- Remover seção opcional vazia ou marcar "Não aplicável: [justificativa]".

## Sinais de POP fraco (corrija)

- Passos que só fazem sentido para quem já conhece o processo.
- Verbos vagos ("analisar", "validar", "alinhar") sem critério nem artefato.
- Ausência de exemplos quando o domínio exige interpretação.
- Resumo excessivo de conteúdo operacional rico.
- Falta de modo discovery quando contexto estava insuficiente.
- Etapas sem saída esperada.
- Etapas sem validação objetiva.

## Política de refinamento

Quando um gate falhar:
1. Não declarar pronto.
2. Refinar somente as seções afetadas.
3. Reexecutar a barreira completa.
4. Registrar bypass apenas em caso excepcional justificado pelo usuário.
