# Pareceres do Astra — MIN-STATION

Esta pasta preserva os dois pareceres de análise científica externa consultados na definição da fase AS.

## Documentos

1. [Parecer 01 — COMP+K, cortes por origem e matching compartilhado](2026-10-11-01-parecer-comp-cortes-matching.md)
   - Diagnóstico da escalabilidade da F-CC+K explícita e das limitações do protocolo FC-06.
   - Proposta inicial de fortalecimento implícito do COMP+K.
   - Revisão crítica da alegação de dominância LP da desagregação histórica T18.
   - Recomendação de benchmark difícil e experimentação controlada.

2. [Parecer 02 — Desagregação corrigida por grupos de origens](2026-10-11-02-parecer-fluxos-por-grupos.md)
   - Atualiza a recomendação anterior: priorizar a **formulação A**, com fluxos por grupos e acoplamento global.
   - Apresenta argumentos de equivalência inteira e hierarquia LP por refinamento de partições.
   - Propõe as alternativas condicionais B (caminhos) e C (cumulativa corrigida).
   - Recomenda comparação progressiva com COMP/COMP+K e gates experimentais.

## Ordem e relação entre os pareceres

O **Parecer 02 substitui a prioridade de implementação do Parecer 01**, mas não o invalida.
O fortalecimento do COMP+K por cortes permanece como hipótese concorrente, não como frente
de implementação imediata. Os dois pareceres devem ser mantidos para rastreabilidade.

## Relação com as specs

- `specs/as-00-benchmark-e-pre-registro/`: benchmark difícil e pré-registro.
- `specs/as-01-formalizacao-matematica-a/`: auditoria e formalização da formulação A.
- `specs/as-04-comparador-multiformulacao/`: comparação entre controles e candidatas.
- `specs/as-07-cortes-origem-matching/`: alternativa condicional do primeiro parecer.
- `specs/as-08-formulacao-b-caminhos/` e `specs/as-09-formulacao-c-cumulativa/`: contingências do segundo parecer.

## Política documental

- Os dois arquivos de parecer reproduzem **integralmente o texto recebido**, sem correções editoriais.
- As conclusões são recomendações e argumentos do Astra, **não validação matemática independente**.
- Decisões futuras, erratas, provas revisadas e resultados experimentais devem ser documentados
  separadamente, sem sobrescrever os pareceres.
- As referências a commit, instâncias, resultados e datas registram o contexto da análise,
  não implicam que o estado atual da branch continue idêntico.

Data de organização documental: 2026-10-11.
