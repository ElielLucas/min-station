# AS21 — Design

## Fluxo de um braço

`run_hl_lp_as21.py` usa o mesmo carregamento, K, compilador COMP+K, parâmetros Gurobi e deadline AS20; só o braço `U_K_HL` recebe `select_structural_supports()` e `separate_hl_layered()`.

1. Resolver LP COMP+K (`y*`) para o braço HL.
2. Selecionar suportes determinísticos: K integrais pequenos, uniões admissíveis e projeções de K grandes sobrepostos. **Uma projeção é uma hipótese**, não uma restrição certificada.
3. Calcular `lhs = Σ y*_R` e `k = floor(lhs + eps)+1`.
4. Excluir explicitamente suportes acima dos limites (`SKIPPED_RHS_CAP`, `SKIPPED_PATTERN_CAP`, `SKIPPED_SIZE`).
5. Com o complemento `F` instalado, submeter ao oráculo todos os subconjuntos `A ⊆ R` com `|A|<k`; usar os certificados de inviabilidade identificados por hash estável.
6. Ao encontrar `VIABLE` abaixo de k, parar sem corte (`NO_CUT_WITNESS`); ao encontrar `UNKNOWN` ou orçamento, abster-se (`ABSTAIN`).
7. Apenas com todos os padrões necessários `INFEASIBLE`, emitir coeficientes inteiros unitários e RHS k com hash de certificado.
8. Reotimizar LP no mesmo modelo com os cortes certificados. Limite de 90 s cobre toda a execução do processo, inclusive preparação e oráculo.
9. Escrever manifesto e análises no diretório novo, preservando o histórico.

## Complexidade

Para provar cardinalidade k em suporte R com n vértices, no máximo `Σ_{j=0}^{k-1} C(n,j)` padrões, versus `2^n` na AS20. Para n=14 e k=3: `1+14+91=106` padrões, contra 16.384; para K4 e k=3: 11 contra 16. A comparação é no número de testes de padrões, **não** uma garantia de menor tempo (padrões individuais podem ser caros).

## Segurança e evidência

- O cache físico pode economizar recomputações, mas o hash de cada certificado continua associado à instância e ao padrão exato.
- A prova não assume monotonicidade de inviabilidade na direção errada; usa apenas que adicionar estações não prejudica a viabilidade.
- Um suporte projetado e a ausência de corte não implicam restrição matemática adicional nem ausência de desigualdades HL fora dessa triagem.
- O gate de análise herda os cuidados AS20 para pares ótimos, censuras, tempo de parede e independência dos grafos. Seu `stage` é AS21.
- Módulos novos mantêm o comportamento AS19 e AS20 reproduzível.
