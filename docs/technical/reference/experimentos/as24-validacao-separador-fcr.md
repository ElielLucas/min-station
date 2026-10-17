# AS24 — Microvalidação do separador FC-R/FC-R-T

**Data da execução local:** 16/10/2026.  
**Escopo:** `SYNTHETIC_ONLY`, sem campanha nas instâncias reais, sem MIP e sem mudança no COMP+K.  
**Gate técnico:** PASS nos testes locais. **Gate TLC final (posterior à execução do JSON):** `VALIDATED_WITH_MINOR_FINDINGS`, após veredito independente `APPROVED_WITH_MINOR_FINDINGS`. O JSON original mantém o gate anterior como fato histórico; ver `as24-revisao-independente-claude.md`.

## Implementação e princípio matemático

- `experiments/cuts/fcr_rows.py` constrói a linha canônica para uma região não vazia `L` com excesso estrito e um `Q` contido na fronteira admissível de `H`. A restrição sobre `Q` exclui `T` para FC-R e `S` para FC-R-T. Os termos têm coeficientes inteiros, assinatura determinística e certificado algébrico descritivo. Não se trata de certificado numérico de viabilidade do solver.
- `experiments/cuts/fcr_separator.py`: em cada `L` fixa calcula `w_v` no fluxo da fronteira e escolhe `Q*={v:w_v>d_L y*_v}`; em empates exclui `v`. Emite apenas déficits `> tolerance` e valida domínios, deduplicação, limites e estados de abstenção.
- `experiments/cuts/fcr_regions.py`: enumera **todos** os singletons de excesso estrito e propõe, com teto explícito, pares que são vizinhos em `H` ou terminais de mesmo sinal com vizinho comum. Essa lista de regiões maiores **não é separação completa** de todos os subconjuntos `L`.
- `experiments/cuts/run_fcr_micro_as24.py`: reaproveita os pontos LP racionais certificados da AS23 e executa a separação unitária e a ablação com regiões maiores. **Não reotimiza o LP** após acrescentar os cortes; objetivo LP diferente do da AS23 não é alegado.

## Validação independente da fórmula de Q (dentro da suíte)

`experiments/cuts/test_as24_fcr.py` usa expressão de fluxo de fronteira independente do construtor produtivo e enumera exaustivamente subconjuntos elegíveis de Q para `L` fixas, nas orientações origem/destino, excessos 1 e 2, valores racionais fracionários e empates. Todas as verificações locais passaram.

Para testar validade, fixa todas as instalações binárias em micrografos com até cinco vértices, resolve um LP adversarial que minimiza a expressão de cada FC-R admissível sujeito a **todas as restrições COMP**, inclusive fluxos fracionários/circulações admitidas pelo sistema, e rejeita qualquer mínimo abaixo do lado direito. Inclui interseção `S∩T`, origens/destinos diretos, compartilhamento, rotas com recarga intermediária, `S=T`, uso correto de `H` para `r>1`, saída de `T` e entrada de `S`, pontos fracionários e censura por orçamento. **Esse procedimento é abrangente apenas nos micrografos escolhidos; não constitui prova geral independente** (a prova geral foi tratada na AS23).

## Resultado da execução sintética

**Evidência machine-readable:** `results/benchmark/as24-fcr-micro-001.json`, versão `as24-fcr-micro-v1`.

| Ponto LP certificado na AS23 | Objetivo do ponto | Cortes com regiões unitárias | Cortes com unitárias + 12 regiões heurísticas |
|---|---:|---:|---:|
| COMP+K | `1` | 4 | 10 |
| COMP+K+FC-R (quatro linhas anteriores) | `7/5` | 2 | 5 |
| COMP+K+C8 | `11/10` | 2 | 4 |
| COMP+K+C8+FC-R | `7/5` | 0 | 0 |
| COMP+K+C6+C8 | `47/30` | 2 | 2 |
| COMP+K+C6+C8+FC-R | `17/10` | 0 | 0 |

- **Cobertura:** 12 singletons admissíveis por ponto LP, isto é, 72 verificações unitárias nas seis formulações (contadas uma vez em cada braço de ablação). Todas concluídas.
- **Regiões maiores:** 46 candidatos distintos gerados por critérios estruturais, 12 selecionados, 34 não examinados por teto, para **cada** ponto LP. Isso exclui qualquer alegação de completude sobre regiões maiores.
- **Teste principal:** quatro violações encontradas no ponto ótimo de COMP+K da AS23, recuperando o sinal científico da testemunha.
- **Ablação:** a seleção estrutural encontrou mais violações em alguns pontos LP, mas ainda não mediu incremento no objetivo após reotimização. Um ponto LP que satisfaz as linhas testadas tampouco prova ausência global de FC-R.
- **Controle de custo:** os testes checam `TIME_LIMIT`, `CUT_CAP_REACHED`, abstenção explícita em L/Q inválidos e contagem de cobertura, sem fingir que o orçamento global é sempre suficiente.

## Reprodutibilidade

```bash
poetry run python experiments/cuts/run_fcr_micro_as24.py \
  --output results/benchmark/as24-fcr-micro-001.json
poetry run python -m unittest discover \
  -s experiments/cuts -p 'test_*.py' -q
python3 .claude/skills/tlc-spec-driven/scripts/validate_spec.py \
  specs/as-24-fcr-separador-micro/spec.md
python3 .claude/skills/tlc-spec-driven/scripts/validate_tasks.py \
  specs/as-24-fcr-separador-micro/tasks.md
```

**Proveniência:** o manifesto armazena SHA-256 dos cinco arquivos novos, o hash da evidência AS23, o hash do grafo e o HEAD detectável. O checkout utilizado para preparar esta entrega pode conter arquivos não commitados; esse HEAD **não deve ser apresentado como commit contendo a AS24**. Regenerar o JSON após o commit no checkout definitivo.

## Pendências / decisão

1. Implementação e microtestes: **PASS técnico local**.
2. Validação formal: **aprovada com achados menores**, conforme veredito do Claude relatado pelo pesquisador. O relatório integral não foi fornecido; observações menores seguem não detalhadas e não bloqueantes em `as24-revisao-independente-claude.md`.
3. AS25: **liberada para preparação e implementação**. Antes da primeira execução real, congelar protocolo, quatro braços, hashes, seleção de regiões e orçamento total; não iniciar MIP.
4. Proveniência final: **aguarda commit no checkout do pesquisador** e regeneração do JSON, sem modificar retroativamente a evidência histórica.
