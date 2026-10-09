# N1-T6 — Errata operacional: desserialização de A_r

## Contexto

A execução `freeze → generate → certify` terminou com sucesso. A primeira chamada `measure` falhou em `fcc.pares_diretos`, ao executar `set(A_r)`, com `TypeError: unhashable type: 'list'`.

**Causa:** `n1-t6-pares.json` preserva os arcos de alcance em formato JSON `[[u,v], ...]`. Após a leitura, Python devolve `list[list[str]]`, enquanto os modelos esperam `list[tuple[str,str]]` para operações de conjunto.

## Correção adotada

Executar `run_n1_t6_measure_ar_fix.py`, que faz uma cópia rasa do grafo e converte apenas `A_r` para tuplas **em memória**, imediatamente antes de chamar a função original `measure_one`.

Esta errata **não altera** `run_n1_t6.py`, `n1_t6_pairs.py`, `fcc.py`, `fc3.py`, cortes, protocolo congelado, grafos, certificados ou evidências da N1-T5. O adaptador não adiciona ou remove arestas, não altera ordem, não substitui instâncias e não modifica parâmetros numéricos. A checagem original de SHA-256 continua ativa, assim como os limites e o checkpoint da medição.

## Como retomar

Na raiz do projeto, com a N1-T6 já congelada/gerada/certificada:

```bash
PYTHONHASHSEED=0 python -m unittest discover -s experiments/alternative-formulations -p test_n1_t6_measure_ar_fix.py -v
PYTHONHASHSEED=0 python experiments/alternative-formulations/run_n1_t6_measure_ar_fix.py
PYTHONHASHSEED=0 python experiments/alternative-formulations/run_n1_t6.py report
```

**Não** executar novamente `freeze`, `generate` nem `certify`. Preservar os JSON e hashes. Se o `measure` já tiver criado linhas válidas do CSV, o runner original retoma somente o sufixo pendente.

## Rastreabilidade

Registrar no commit os arquivos do adaptador, teste e esta errata. O método de medição é o original, acrescido apenas da normalização do tipo de dados. Após `report`, verificar os status `COMPUTATIONALLY VERIFIED` e `NOT MEASURED` individualmente. A N1-T7 não deve ser aplicada sem conferir o relatório da T6.
