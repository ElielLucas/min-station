# Exemplos de POP por domínio

Use este arquivo como menu de partida quando o pedido do usuário estiver fora do contexto original da skill. O objetivo é acelerar discovery sem perder especificidade operacional.

## Índice

1. Engenharia / desenvolvimento
2. Operação
3. Segurança
4. QA
5. Infraestrutura
6. Processos administrativos

## 1) Engenharia / desenvolvimento

**Título sugerido**
- POP de Deploy Controlado com Rollback Assistido

**Gatilho típico**
- Liberação de versão em branch principal.
- Correção urgente com janela de publicação.

**Papéis comuns**
- Dev responsável pela release.
- Revisor técnico.
- Tech Lead aprovador.
- On-call de suporte.

**Etapas-chave (linha única)**
- Validar prerequisitos de merge e checklist de release.
- Gerar tag/versionamento conforme convenção.
- Executar pipeline de deploy no ambiente alvo.
- Rodar smoke test mínimo pós-publicação.
- Decidir manter release ou executar rollback.
- Registrar evidências e comunicar encerramento.

**Validação típica**
- Pipeline verde com hash/version correta.
- Smoke test aprovado com evidência (log/ticket).
- Comunicação de conclusão no canal oficial.

**Gates específicos do domínio**
- Critério objetivo para rollback.
- Referência explícita de branch/tag.
- Rastreabilidade entre commit, build e ambiente.

## 2) Operação

**Título sugerido**
- POP de Resposta a Incidente com Escalação

**Gatilho típico**
- Alerta crítico em monitoramento.
- Chamado P1/P0 aberto por cliente interno ou externo.

**Papéis comuns**
- Analista on-call.
- Incident Commander.
- Especialista de domínio consultado.
- Gestor informado.

**Etapas-chave (linha única)**
- Confirmar severidade e abrir registro de incidente.
- Estabilizar serviço com ação de contenção inicial.
- Acionar escalação conforme matriz de severidade.
- Comunicar status em intervalos definidos.
- Encerrar incidente e consolidar causa raiz.
- Abrir postmortem e plano de ação.

**Validação típica**
- Serviço restaurado dentro de SLA.
- Linha do tempo documentada.
- Postmortem registrado com responsáveis e prazos.

**Gates específicos do domínio**
- Critérios de severidade explícitos.
- Regra clara de escalação por tempo/impacto.
- Critério de encerramento operacional mensurável.

## 3) Segurança

**Título sugerido**
- POP de Rotação de Credenciais Críticas

**Gatilho típico**
- Janela periódica de rotação.
- Suspeita de comprometimento.
- Mudança de equipe com acesso privilegiado.

**Papéis comuns**
- Segurança (owner do controle).
- Operações/Plataforma (execução técnica).
- Dono do sistema impactado.
- Auditoria/Compliance informado.

**Etapas-chave (linha única)**
- Confirmar janela, impacto e plano de rollback.
- Inventariar credenciais e sistemas afetados.
- Rotacionar credenciais por ordem de criticidade.
- Atualizar segredos e reiniciar serviços dependentes.
- Validar autenticação e trilhas de auditoria.
- Revogar credenciais antigas e registrar evidências.

**Validação típica**
- Logs de auditoria com rotação concluída.
- Serviços autenticando com credenciais novas.
- Ausência de falha de autenticação após troca.

**Gates específicos do domínio**
- Janela de manutenção documentada.
- RACI Sec/Ops explícito.
- Evidência de revogação e rastreabilidade de logs.

## 4) QA

**Título sugerido**
- POP de Regressão e Liberação de Release Candidate

**Gatilho típico**
- Build candidato para release.
- Correção de bug crítico antes de publicação.

**Papéis comuns**
- QA executor.
- QA Lead aprovador.
- Dev de suporte para correções.
- Product/Negócio informado.

**Etapas-chave (linha única)**
- Preparar ambiente e massa de teste controlada.
- Executar suíte de regressão prioritária.
- Rodar smoke test funcional de alto risco.
- Abrir e classificar defeitos por severidade.
- Validar correções e retestar cenários críticos.
- Aprovar ou bloquear release candidate.

**Validação típica**
- Matriz de casos com status aprovado/reprovado.
- Defeitos críticos sem pendência para go-live.
- Parecer final de QA registrado.

**Gates específicos do domínio**
- Critério de bloqueio por severidade definido.
- Evidência de cobertura mínima da regressão.
- Definição explícita de "aprovado para release".

## 5) Infraestrutura

**Título sugerido**
- POP de Provisionamento de Ambiente (dev/staging/prod)

**Gatilho típico**
- Novo projeto/squad.
- Necessidade de ambiente adicional.
- Recriação após incidente.

**Papéis comuns**
- Plataforma/Infra executor.
- Tech Lead aprovador.
- Segurança consultada.
- Time solicitante informado.

**Etapas-chave (linha única)**
- Coletar requisitos e aprovações do ambiente.
- Provisionar recursos base (rede, compute, storage).
- Configurar acesso, segredos e políticas.
- Implantar stack base e monitoramento.
- Validar conectividade, observabilidade e backup.
- Entregar evidências e aceite do solicitante.

**Validação típica**
- Ambiente acessível com permissões corretas.
- Alertas e logs ativos.
- Backup/restore testado no escopo definido.

**Gates específicos do domínio**
- Aplicabilidade clara por ambiente (dev/staging/prod).
- Gate de aprovação por Tech Lead antes de produção.
- Evidência de segurança e observabilidade mínima.

## 6) Processos administrativos

**Título sugerido**
- POP de Onboarding/Offboarding e Acessos Corporativos

**Gatilho típico**
- Entrada de novo colaborador.
- Desligamento ou mudança de função.
- Solicitação de acesso extraordinário.

**Papéis comuns**
- RH.
- Gestor solicitante.
- TI/Service Desk executor.
- Segurança/Compliance consultado.

**Etapas-chave (linha única)**
- Receber solicitação formal com dados mínimos.
- Validar aprovação e documentação obrigatória.
- Criar/alterar/remover acessos conforme perfil.
- Confirmar entrega de ativos e termos.
- Registrar evidência e comunicar conclusão.
- Revisar acessos após período de estabilização.

**Validação típica**
- Chamado finalizado com evidências anexas.
- Acessos concedidos/revogados conforme aprovação.
- Termos e registros administrativos concluídos.

**Gates específicos do domínio**
- Aprovação formal por papel autorizado.
- Rastreabilidade de acessos concedidos/revogados.
- Critério de conformidade documental explícito.
