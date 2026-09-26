# Documentação técnica — MIN-STATION

Esta pasta reúne as referências científicas, decisões matemáticas e documentos especializados do projeto.

O objetivo deste índice é permitir que pessoas e agentes de IA encontrem a fonte correta sem carregar toda a documentação.

## Estrutura

```text
technical/
├── README.md
├── governance/
│   └── open-questions.md
├── plans/
│   └── plano-*.md            # planos de execução por rodada de experimentos
└── reference/
    ├── source-map.md
    ├── benchmark-v1.md        # metodologia e resultados das instâncias
    ├── resultados-*.md        # relatórios por rodada (E0-E1, E2-E4, E7, E8, ...)
    ├── direcoes-pli-min-station.md
    ├── validacao-formulacao-base.md
    ├── min-station-das.pdf
    ├── artigo-sbpo.pdf
    └── formulacao-base-all-vertices.pdf
```

Os nomes dos PDFs são sugeridos. Se os arquivos reais tiverem outros nomes, atualizar `reference/source-map.md`.

## Papel das principais referências

1. **Artigo de Das:** define o MIN-STATION original e seus resultados teóricos iniciais.
2. **Artigo da SBPO:** registra uma etapa anterior desta pesquisa, incluindo a primeira formulação de PLI do projeto e a variante com estações apenas nos vértices intermediários.
3. **Formulação all-vertices:** documenta o baseline atual posterior ao artigo da SBPO.
4. **RESEARCH.md:** define o objetivo científico mais amplo, que inclui investigar diferentes formulações e técnicas de otimização.
5. **Código:** define o que efetivamente está implementado em uma determinada versão.

Nenhuma dessas fontes deve substituir silenciosamente as demais.

## Roteamento por necessidade

| Necessidade | Fonte principal |
|---|---|
| Entender o problema original | `../context-ai/min-station-domain.md` + artigo de Das |
| Entender a formulação base atual | `../context-ai/base-formulation.md` |
| Entender a direção da pesquisa | `../../RESEARCH.md` + `../context-ai/research-direction.md` |
| Ver diferenças entre versões | `reference/source-map.md` |
| Ver pontos não resolvidos | `governance/open-questions.md` |
| Entender implementação | `../context-ai/code-guidelines.md` + código real |
| Escolher instâncias experimentais | `reference/benchmark-v1.md` + `../../instances/manifest.csv` |

## Regra sobre formulações experimentais

O baseline atual não deve ser tratado como imutável.

Novas formulações, cortes, relaxações, decomposições ou estratégias podem ser implementadas para pesquisa, mas devem:

- receber nome/identificador próprio;
- preservar a formulação baseline para comparação, quando possível;
- declarar se resolvem o mesmo problema ou uma variante;
- registrar parâmetros e versão usados nos experimentos.

## Regra sobre a formulação generalizada da SBPO

A formulação generalizada do artigo da SBPO não deve ser carregada como contexto padrão do MIN-STATION base.

Ela só deve ser consultada quando a tarefa solicitar explicitamente comparação histórica, generalização ou análise daquele modelo.
