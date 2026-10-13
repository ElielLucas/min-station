# AS09 — Triagem estrutural (não é benchmark completo)

| Instância | U variáveis | C variáveis | C/U | Redução estimada | Linhas U sem K | Linhas C sem K |
|---|---:|---:|---:|---:|---:|---:|
| mapf-room-32-32-4-m10-f8 | 12,304 | 11,172 | 0.908 | 9.2% | 2,046 | 4,102 |
| mapf-den312d-m50-f2-rho | 552,141 | 182,927 | 0.331 | 66.9% | 7,335 | 44,060 |
| vienna-I056-regiao-f4 | 383,591 | 102,432 | 0.267 | 73.3% | 5,973 | 27,899 |
| puc-cc9-2p-seed-r1 | 5,120 | 5,696 | 1.113 | -11.2% | 1,536 | 1,568 |
| puc-w3c571-seed-r1 | 24,553 | 30,834 | 1.256 | -25.6% | 11,991 | 13,133 |

## Interpretação e limites

- Valores derivados exclusivamente do manifesto e das fórmulas exatas de dimensionamento; ainda não incluem presolve.
- A geração de A_r, preparação de K, construção de modelos, tempo total e memória **não foram medidos**.
- As duas formulações recebem os mesmos cortes K; todas as linhas de K devem ser contadas no experimento completo.
- Não foi provada nem certificada a equivalência de projeções LP por este pré-screen.
- Uma razão C/U baixa autoriza apenas um piloto, nunca uma alegação de desempenho superior.

> Esta prévia foi gerada a partir do manifesto incluído no ZIP usado nesta análise. Execute novamente `run_as09_screen.py` no repositório atualizado antes de usar as contagens em qualquer relatório.
