# AS-08/LB — Prova exploratória de fortalecimento LP via duais intermediários

**Classificação:** desenvolvimento exploratório, sem promoção científica.  
**Modelos:** LP(COMP+K) comparador e LP(B+K) com geração de colunas.  
**Decisão a investigar:** existe LB global racional validado de B+K estritamente superior ao LP numérico de COMP+K?

## Justificativa

Os pilotos anteriores da AS-08 terminaram censurados sem ótimo LP B+K. Cinco instâncias atingiram o limite real de 5.000 colunas no piloto 003, e PUC w3c571 ficou sem convergência. Objetivos de mestres restritos podem exceder o LP completo e **não provam força da formulação**. O novo experimento extrai duais intermediários e faz pricing de todas as origens com `Fraction`, corrigindo a função dual antes de publicar qualquer bound.

## Garantias

1. Os cortes K continuam sendo os mesmos validados por `bitset-v2`, com identidade e hash da instância preservados.
2. A certificação requer solver RMP ótimo, pricing racional completo, duais reparados e reconstrução independente na auditoria.
3. Cada tentativa possui orçamento próprio e deadline. Se o prazo expirar antes de todos os mínimos racionais, nenhum bound é publicado para aquela tentativa.
4. Mantém-se o maior **racional** obtido (não simplesmente o maior float); certificados completos são transmitidos ao supervisor e persistidos em checkpoint.
5. O supervisor pode recuperar o último certificado completo quando o worker termina por tempo; um checkpoint parcial nunca vira certificado.
6. `CONVERGED` é exigido para reportar `lp_numeric_value` de B. Um LB global intermediário não equivale ao ótimo do LP.
7. O controle de integridade verifica SHA-256 de resultados e checkpoints; `--analyze` ainda recalcula K e verifica cada certificado por preços racionais sobre todas as origens.
8. Planos e resultados anteriores permanecem imutáveis. Não existe branch-and-price nem execução MIP nesta etapa.

## Casos e parâmetros pré-definidos

- MAPF room (`mapf-room-32-32-4-m10-f8`)
- PUC cc9 (`puc-cc9-2p-seed-r1`)
- Vienna I056 (`vienna-I056-regiao-f4`)

Orçamento: 300 s por braço, 100 iterações, 5.000 colunas, 60.000 linhas, seleção `matching`, até três tentativas intermediárias, uma a cada 5 iterações ou na primeira solução RMP fisicamente viável; 15 s por tentativa e reserva mínima de 20 s. O período e o orçamento ficam congelados no plano.

## Regras de interpretação

Como se trata de minimização, um certificado racional global de B+K pode demonstrar força **sem convergência**, caso exceda com margem adequada o LP numérico ótimo COMP+K da mesma instância e dos mesmos cortes K. A margem operacional de ganho relevante é 1% e é aplicada com guarda para tolerância numérica. O estudo considera continuação promissora quando pelo menos duas famílias independentes exibirem ganhos materiais.

Se os limites forem ruins ou não houver tempo para certificá-los, a decisão é **inconclusiva**, não uma prova de ausência de ganho da formulação B+K. Não inferir MIP, escalabilidade geral ou nova superioridade científica sem replicação e estudos adicionais.

## Uso

Consulte o arquivo `AS08-LB-PROBE-GUIA-EXECUCAO.md` do patch para comandos de instalação, testes, execução, verificação e análise.
