# caveman

Fale como caveman inteligente. Mesmo cérebro, menos tokens.

## O que faz

Comprime toda resposta do modelo para prosa estilo caveman. Remove artigos, enchimento, formalidades e hedging. Mantém todo detalhe técnico, bloco de código, string de erro e símbolo exato. Reduz ~65-75% dos tokens de saída com precisão total preservada. O modo persiste durante toda a sessão até ser mudado ou interrompido.

Seis níveis de intensidade:

| Nível | O que muda |
|-------|-------------|
| `lite` | Remove enchimento/hedging. Frases ficam completas. Profissional mas conciso. |
| `full` | Padrão. Remove artigos, fragmentos OK, sinônimos curtos. |
| `ultra` | Fragmentos crus. Sem abreviação inventada (cfg/impl/req/fn), sem setas de causalidade — tokenizer não economiza nada nisso. Uma palavra quando basta uma palavra. |
| `wenyan-lite` | Registro de chinês clássico, compressão leve. |
| `wenyan-full` | 文言文 máximo. 80-90% de redução de caracteres. |
| `wenyan-ultra` | Compressão clássica extrema. |

Regra de auto-clareza: o caveman volta para prosa normal em avisos de segurança, confirmações de ação irreversível, sequências multi-etapa onde a ambiguidade de fragmentos arrisca interpretação errada, e quando o usuário repete uma pergunta. Retoma depois da parte clara.

## Como invocar

```
/caveman              # modo full (padrão)
/caveman lite         # compressão mais leve
/caveman ultra        # compressão extrema
/caveman wenyan       # chinês clássico
stop caveman          # voltar à prosa normal
```

## Exemplo de saída

Pergunta: "Por que meu componente React está sendo renderizado novamente?"

Prosa normal:
> Seu componente está sendo renderizado novamente porque você cria uma nova referência de objeto a cada renderização. Envolvê-lo em `useMemo` resolverá o problema..

Caveman (full):
> Nova referência de objeto a cada renderização. Propriedade de objeto inline = nova referência = nova renderização. Envolva em `useMemo`.

Caveman (ultra):
> Propriedade obj embutida, nova referência, renderiza de novo. `useMemo`.

## Veja também

- [`SKILL.md`](./SKILL.md) — instruções completas voltadas ao LLM
- [Caveman README](../../README.md) — visão geral do repositório, instalação, benchmarks
