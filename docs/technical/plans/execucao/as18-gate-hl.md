# AS18 — Gate de autorização de HL (15/10/2026)

**Decisão:** `NOT_AUTHORIZED` para implementar ou executar HL neste protocolo.  
**Natureza:** decisão de pré-condição e priorização, **não** demonstração de que HL seja matematicamente redundante ou inválida.  
**Fonte auditável:** `results/benchmark/as16-lp-h2-001/{manifest,rows,analysis}.json`; auditoria derivada em `specs/as-18-hl-condicional-e-sintese/as18-gate-evidence.json`.

## Cadeia de decisão

1. AS16 foi executada em seis grafos brutos distintos, com 36 registros (quatro braços LP e dois controles same-pool por caso). O gate **automático** é `INVESTIGATE` por censuras; não o reescrever.
2. O pré-registro exigia ganho relativo LP de pelo menos 1% de U+K para U+K+H2 em no mínimo dois grafos independentes e custo adicional justificável.
3. Cinco comparações principais foram ótimas e mostraram **zero ganho**. A sexta está censurada: mesmo supondo ganho, no máximo um grafo satisfaria o critério de dois.
4. A decisão científica já registrada em AS16 é `STOP` **para promover/priorizar H2 nesta linha**, sem prova de dominância sobre H2.
5. AS17 exige `AS16 GO explícito`; logo seu piloto MIP H2 está **`NOT_AUTHORIZED`**, não executado.
6. A AS18 exige indício **estrutural independente** de padrão local não capturado pelos H2 disponíveis para abrir HL. A campanha AS16 não forneceu essa testemunha para os casos considerados e a documentação fornecida não registra uma nova hipótese independente aprovada. Portanto, `NOT_AUTHORIZED` para HL.

**Verificador local reproduzível (padrão fail-closed):**

```bash
python experiments/cuts/verify_as18_gate.py \
  --as16-dir results/benchmark/as16-lp-h2-001
python -m unittest discover -s experiments/cuts -p 'test_as18_gate.py' -q
```

O verificador confere pareamento e identidades dos grafos, ótimos versus censuras, valores LP e contagens do analisador. Ele **não verifica independentemente a matemática dos cortes nem autoriza HL**; uma hipotética reabertura precisa de revisão humana e plano novo. O JSON de evidências é derivado, não substitui arquivos de campanha.

## Condições para eventual reabertura (nova pesquisa, não continuação automática)

- Documentar testemunha de incompatibilidade local não capturada por K e H2, com conjunto de suporte `R` explícito e verificação independente de viabilidade física.
- Antes de qualquer enumeração, testar `ν(V\R)`; se `ν(V\R)=m`, rejeitar esse suporte como fonte de desigualdade HL não trivial.
- Se continuar, priorizar `|R| ≤ 10`, certificar todos os padrões admissíveis (ou oráculo exato equivalente), tratar `UNKNOWN` conservadoramente, recomputar `β_R(α)` de forma exata com coeficientes racionais, e testar contra COMP+K com orçamento total e controles pareados.
- Microexemplo de quatro relés e alegada hierarquia de LP (`2`, `8/3`, `3`) continuam **hipóteses não testadas nesta etapa**; não usar como evidência computacional nova.
- Nova spec e novo pré-registro/decisão são necessários antes de implementar `hl_local.py` ou rodar MIP.

## Rastreabilidade

| Requisito | Situação |
|---|---|
| AS18-01 | Gate aplicado com ausência de testemunha estrutural independente documentada: HL `NOT_AUTHORIZED` |
| AS18-02 | Condicional; suporte `R` **não selecionado** porque não houve autorização. Procedimento fica para reabertura |
| AS18-03–06 | **NOT_EXECUTED** por bloqueio do gate; sem cortes/certificados HL |
| AS18-07–08 | **NOT_MEASURED**; não houve microteste HL nem ganhos ou custos medidos |
| AS18-09 | Síntese elaborada em `docs/technical/reference/experimentos/as18-sintese-h2-hl.md` |

**Limitação de validação:** análise de dados e testes automatizados não constituem parecer de revisor científico externo distinto do autor. Sem tal parecer, não alegar homologação independente de AS18.

---

## Adendo posterior — investigação independente AS19 (15/10/2026)

Após esta decisão histórica, o pesquisador autorizou **manter HL como hipótese independente de H2**, em nova etapa AS19. Isso **não muda** o gate original AS18 (`NOT_AUTHORIZED` no protocolo condicional) nem reabre AS17/H2. Ver `specs/as-19-hl-independente/` e `docs/technical/reference/experimentos/as19-hl-independente-microtriagem.md`. O microteste K4 de AS19 é evidência **posterior e sintética**, não um novo resultado da campanha AS18 nem autorização automática para benchmark MIP.
