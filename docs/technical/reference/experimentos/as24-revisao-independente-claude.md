# AS24 — Registro do parecer independente do Claude

**Data de registro:** 16/10/2026.  
**Fase:** AS24 — separador FC-R/FC-R-T e microvalidação.  
**Revisor:** Claude, revisão independente solicitada pelo pesquisador.  
**Veredito informado pelo pesquisador:** `APPROVED_WITH_MINOR_FINDINGS`.

## Fonte e limites do registro

O pesquisador comunicou o veredito acima na conversa após solicitar uma auditoria adversarial de AS24. **O relatório integral do Claude não foi anexado**; portanto, este registro comprova apenas o veredito comunicado, e **não** contém a lista individual dos achados, sua localização ou a evidência `file:line` produzida pelo revisor. Não afirmar que todos os achados foram corrigidos ou que executamos as verificações privadas do Claude.

O veredito favorável permite encerrar a revisão independente **com achados menores não bloqueantes**. Se o parecer completo trouxer algum critério obrigatório reprovado, reabrir o gate e tratar a divergência; não inventar um `PASS` irrestrito. As observações menores não individualizadas ficam em acompanhamento, sem bloquear o planejamento de AS25.

## Evidências verificáveis no repositório

| Verificação | Evidência de código / teste | Resultado |
|---|---|---|
| Construção canônica e exclusões de terminais | `experiments/cuts/fcr_rows.py:97`; `experiments/cuts/test_as24_fcr.py:91` | PASS na suíte |
| Escolha exata de Q nas duas orientações e saldos 1/2 | `experiments/cuts/fcr_separator.py:51`; `experiments/cuts/test_as24_fcr.py:66` | PASS na suíte |
| Cobertura completa dos singletons elegíveis | `experiments/cuts/fcr_separator.py:143`; `experiments/cuts/test_as24_fcr.py:106` | PASS na suíte |
| Censura, limite de cortes e indicação de cobertura parcial | `experiments/cuts/fcr_separator.py:145`; `experiments/cuts/test_as24_fcr.py:120` | PASS na suíte |
| Deduplicação e determinismo | `experiments/cuts/fcr_separator.py:124`; `experiments/cuts/test_as24_fcr.py:145` | PASS na suíte |
| Linhas violadas na testemunha LP | `experiments/cuts/test_as24_fcr.py:154`; `experiments/cuts/run_fcr_micro_as24.py:28` | PASS na suíte |
| Validade adversarial em micrografos | `experiments/cuts/test_as24_fcr.py:214` | PASS na suíte |

**Teste geral:** 186 testes aprovados na máquina do pesquisador e novamente no ambiente de verificação deste fechamento (extraindo as dependências e instâncias históricas do ZIP recebido).  
**Microexecução:** `results/benchmark/as24-fcr-micro-001.json`, `MICRO_VALIDATION_COMPLETED`, seis casos sintéticos, 72 varreduras unitárias, quatro cortes sobre COMP+K na subfamília singleton e dez na busca com regiões maiores.

## Achados não bloqueantes

- `MINOR-AS24-OPEN-01`: **detalhamento dos achados menores do Claude não disponível**. Acompanhar quando o relatório integral for fornecido; não criar correções hipotéticas.
- `TRACE-AS24-COMMIT`: o manifesto histórico possui `source_commit`, mas também registra `source_has_tracked_modifications=true`. Esse SHA corresponde ao HEAD observado no momento da geração, **não necessariamente ao commit que contém a AS24**. Regenerar o JSON após registrar todas as mudanças no Git, confirmar `source_has_tracked_modifications=false` e então registrar o novo SHA no fechamento, sem reescrever o JSON histórico de forma manual.

## Decisão

**Gate formal da AS24:** `PASS` (`VALIDATED_WITH_MINOR_FINDINGS`).  
**AS25:** liberada para **implementação e preparação do protocolo pré-registrado**. A execução experimental real depende de congelamento de política, hashes, orçamento e comparadores, conforme `specs/as-25-fcr-lp-pareado/spec.md`.  
**AS26/MIP:** não autorizada.

O campo `gate=PENDING_INDEPENDENT_REVIEW` do JSON da microvalidação é preservado como **estado histórico no momento de sua execução**, anterior à revisão externa; a decisão formal posterior é documentada aqui e em `specs/as-24-fcr-separador-micro/validation.md`.
