# AS22 — Design técnico

## Fluxo

1. `run_hl_lp_as22.py`: verifica pré-registro, hashes e fontes de desenvolvimento; compila o COMP+K original e otimiza seu LP.
2. `hl_poly_supports.py`: candidatos deterministicamente estratificados entre K inteiros/projeções e interações K/uniões/projeções de pares. Reserva até duas vagas para interações distintas (sem presumir validade).
3. `hl_polyhedral.py`: constrói `F = V \ R`, classifica todos os `2^|R|` padrões por certificados do oráculo AS14 ou por monotonicidade a partir de padrões viáveis.
4. `scipy.optimize.linprog(method='highs')`: sugere um vetor normal não negativo sobre o casco convexo da projeção completa. **Não produz certificado físico.**
5. O módulo racionaliza α, recalcula β exato sobre os padrões viáveis e valida violação estrita; só então fornece `HLCut` com hash e evidências.
6. Runner adiciona até três cortes comprovados ao mesmo LP e mede limite, custo, censura e quantidade de oráculos.
7. `analyze_hl_lp_as22.py`: reutiliza verificação pareada conservadora da AS20 e especifica o escopo HL geral.

## Segurança e invariantes

- `UNKNOWN` jamais equivale a `INFEASIBLE` ou `VIABLE`.
- Inferência monotônica apenas a partir de **VIABLE certificado** para superconjuntos; cada inferência referencia a testemunha base.
- Sem classificação integral, sem coeficientes racionais, sem corte.
- `β` nunca é herdado de saída de ponto flutuante; é mínimo exato da projeção física certificada.
- Conjunto viável vazio implica abstenção (possível inviabilidade física global, fora do escopo).
- O compilador, as equações K, o oráculo AS14 e os experimentos históricos não são modificados.
- Seleção heurística, caps e dry-run não autorizam conclusões negativas universais.

## Arquivos novos

- `experiments/cuts/hl_polyhedral.py`
- `experiments/cuts/hl_poly_supports.py`
- `experiments/cuts/run_hl_lp_as22.py`
- `experiments/cuts/analyze_hl_lp_as22.py`
- `experiments/cuts/run_hl_poly_micro.py`
- `experiments/cuts/test_as22_hl_poly.py`

## Validação

A testemunha física `s-a-t` ou `s-b-c-t`, com autonomia 1 e suporte `{a,b,c}`, satisfaz viabilidade `a ∨ (b ∧ c)`. O ponto `(0.1, 0.5, 0.5)` possui soma 1.1 e, portanto, não viola a cardinalidade mínima 1, mas viola a desigualdade válida `1/2 y_a + 1/2 y_c ≥ 1/2`. Isso é uma testemunha de **HL geral contra cardinalidade**, não uma demonstração de ganho adicional sobre COMP+K em benchmarks.

K4 é a testemunha separada de integração real do compilador COMP+K: 2 → 3 com HL certificado.
