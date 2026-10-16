# AS22 — Pré-registro da triagem HL poliédrica

**Situação:** pré-registrado **antes da campanha Gurobi AS22**. Fonte de verdade: `as22-preregistro-hl-lp.json` (não editar após iniciar campanha real).

### Pergunta científica

Uma desigualdade HL com **coeficientes racionais não uniformes**, certificada pelo oráculo físico em suportes pequenos, consegue melhorar o limite LP de COMP+K a um custo aceitável em pelo menos duas instâncias independentes?

### Fixações

- **Casos:** os seis grafos de desenvolvimento AS16, sem avaliação; hashes da fonte, identidade de grafo e plano AS16 congelados.
- **Comparação:** pares `U_K` e `U_K_HL`, 90 segundos totais cada, mesmos parâmetros Gurobi.
- **Suportes:** tamanho até 8, até 4, pelo menos uma hipótese de interação K quando disponível, até 2 vagas reservadas; propostas são **hipóteses**, não certificados.
- **Oráculo:** até 256 padrões por suporte, 480 chamadas por braço, 24 s globais e 8 s por suporte. Resultados UNKNOWN abstêm.
- **Separação:** LP auxiliar maximiza violação com α ≥0, Σα=1; racionalização denominador ≤128, β exato sobre projeção fisicamente certificada; violação >10⁻⁶.
- **Cortes:** no máximo três por braço.
- **Gate:** 1% de ganho e custo ≤2× em ≥2 grafos independentes é somente `GO_CANDIDATE_REVIEW`, sujeito à análise independente; casos censurados/incompletos não justificam conclusão negativa.
- **Persistência:** `results/benchmark/as22-hl-lp-001`, saída inédita; AS16–AS21 imutáveis.

Os resultados sintéticos são mantidos separados dos benchmarks, e não autorizam MIP automaticamente.
