"""Detecta estações obrigatórias por separadores no grafo de alcance.

A regra implementada neste módulo é conservadora. Um candidato não terminal
``v`` só é declarado obrigatório quando sua remoção do grafo de alcance cria
alguma componente com números diferentes de origens e destinos. Como os robôs
são não rotulados, esse desequilíbrio precisa atravessar ``v``. Logo, qualquer
solução viável precisa usar ``v`` como ponto intermediário de recarga.

O algoritmo usa uma busca de Tarjan iterativa. Assim, evita o limite de
recursão do Python nas instâncias grandes e executa em O(|V| + |A_R|).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Hashable, Iterable, Iterator


Vertice = Hashable
Arco = tuple[Vertice, Vertice]


@dataclass(frozen=True)
class ResultadoSeparadores:
    """Resultado da análise de separadores obrigatórios."""

    articulacoes: frozenset[Vertice]
    separadores_desbalanceados: frozenset[Vertice]
    estacoes_obrigatorias: frozenset[Vertice]
    saldos_componentes: dict[Vertice, tuple[int, ...]]
    componentes_originais: int

    @property
    def componentes_desbalanceadas_total(self) -> int:
        return sum(
            1
            for saldos in self.saldos_componentes.values()
            for saldo in saldos
            if saldo != 0
        )

    @property
    def maior_desequilibrio(self) -> int:
        return max(
            (
                abs(saldo)
                for saldos in self.saldos_componentes.values()
                for saldo in saldos
            ),
            default=0,
        )


def construir_adjacencia_alcance_nao_direcionada(
    vertices: Iterable[Vertice],
    arcos: Iterable[Arco],
) -> dict[Vertice, set[Vertice]]:
    """Converte os arcos de alcance em uma adjacência não direcionada."""
    adjacencia = {vertice: set() for vertice in vertices}
    conjunto_vertices = set(adjacencia)

    for origem, destino in arcos:
        if (
            origem == destino
            or origem not in conjunto_vertices
            or destino not in conjunto_vertices
        ):
            continue
        adjacencia[origem].add(destino)
        adjacencia[destino].add(origem)

    return adjacencia


def _saldo_terminal(
    vertice: Vertice,
    origens: set[Vertice],
    destinos: set[Vertice],
) -> int:
    return int(vertice in origens) - int(vertice in destinos)


def _percorrer_componente(
    raiz: Vertice,
    adjacencia: dict[Vertice, set[Vertice]],
    origens: set[Vertice],
    destinos: set[Vertice],
    descoberta: dict[Vertice, int],
    menor: dict[Vertice, int],
    pai: dict[Vertice, Vertice | None],
    filhos: dict[Vertice, list[Vertice]],
    saldo_subarvore: dict[Vertice, int],
    proximo_indice: int,
) -> tuple[list[Vertice], int]:
    """Executa uma DFS iterativa e calcula low-link e saldos de subárvore."""
    pai[raiz] = None
    descoberta[raiz] = proximo_indice
    menor[raiz] = proximo_indice
    saldo_subarvore[raiz] = _saldo_terminal(raiz, origens, destinos)
    filhos[raiz] = []
    proximo_indice += 1

    vertices_componente = [raiz]
    pilha: list[tuple[Vertice, Iterator[Vertice]]] = [
        (raiz, iter(adjacencia[raiz]))
    ]

    while pilha:
        atual, vizinhos = pilha[-1]
        try:
            vizinho = next(vizinhos)
        except StopIteration:
            pilha.pop()
            ancestral = pai[atual]
            if ancestral is not None:
                menor[ancestral] = min(menor[ancestral], menor[atual])
                saldo_subarvore[ancestral] += saldo_subarvore[atual]
            continue

        if vizinho not in descoberta:
            pai[vizinho] = atual
            filhos[atual].append(vizinho)
            filhos[vizinho] = []
            descoberta[vizinho] = proximo_indice
            menor[vizinho] = proximo_indice
            saldo_subarvore[vizinho] = _saldo_terminal(
                vizinho, origens, destinos
            )
            proximo_indice += 1
            vertices_componente.append(vizinho)
            pilha.append((vizinho, iter(adjacencia[vizinho])))
        elif vizinho != pai[atual]:
            menor[atual] = min(menor[atual], descoberta[vizinho])

    return vertices_componente, proximo_indice


def _saldos_apos_remocao(
    vertice: Vertice,
    raiz: Vertice,
    saldo_componente: int,
    descoberta: dict[Vertice, int],
    menor: dict[Vertice, int],
    pai: dict[Vertice, Vertice | None],
    filhos: dict[Vertice, list[Vertice]],
    saldo_subarvore: dict[Vertice, int],
    saldo_do_vertice: int,
) -> tuple[int, ...]:
    """Retorna os saldos das componentes geradas pela remoção do vértice."""
    if vertice == raiz:
        if len(filhos[vertice]) <= 1:
            return ()
        return tuple(saldo_subarvore[filho] for filho in filhos[vertice])

    filhos_separados = [
        filho
        for filho in filhos[vertice]
        if menor[filho] >= descoberta[vertice]
    ]
    if not filhos_separados:
        return ()

    saldos_separados = [
        saldo_subarvore[filho] for filho in filhos_separados
    ]
    saldo_restante = (
        saldo_componente - saldo_do_vertice - sum(saldos_separados)
    )
    return tuple([*saldos_separados, saldo_restante])


def detectar_estacoes_obrigatorias(
    *,
    vertices: Iterable[Vertice],
    arcos_alcance: Iterable[Arco],
    origens: Iterable[Vertice],
    destinos: Iterable[Vertice],
    candidatos: Iterable[Vertice] | None = None,
) -> ResultadoSeparadores:
    """Encontra candidatos obrigatórios por articulação e desequilíbrio.

    Terminais são deliberadamente excluídos da fixação. O comportamento de
    uma origem ou destino como estação intermediária depende de regras
    adicionais do modelo e deve ser estudado separadamente.
    """
    lista_vertices = list(dict.fromkeys(vertices))
    conjunto_vertices = set(lista_vertices)
    conjunto_origens = set(origens) & conjunto_vertices
    conjunto_destinos = set(destinos) & conjunto_vertices
    conjunto_terminais = conjunto_origens | conjunto_destinos
    conjunto_candidatos = (
        set(candidatos) & conjunto_vertices
        if candidatos is not None
        else set(conjunto_vertices)
    )

    adjacencia = construir_adjacencia_alcance_nao_direcionada(
        lista_vertices, arcos_alcance
    )

    descoberta: dict[Vertice, int] = {}
    menor: dict[Vertice, int] = {}
    pai: dict[Vertice, Vertice | None] = {}
    filhos: dict[Vertice, list[Vertice]] = {}
    saldo_subarvore: dict[Vertice, int] = {}
    componentes: list[tuple[Vertice, list[Vertice]]] = []
    proximo_indice = 0

    for raiz in lista_vertices:
        if raiz in descoberta:
            continue
        vertices_componente, proximo_indice = _percorrer_componente(
            raiz,
            adjacencia,
            conjunto_origens,
            conjunto_destinos,
            descoberta,
            menor,
            pai,
            filhos,
            saldo_subarvore,
            proximo_indice,
        )
        componentes.append((raiz, vertices_componente))

    articulacoes: set[Vertice] = set()
    separadores_desbalanceados: set[Vertice] = set()
    obrigatorias: set[Vertice] = set()
    saldos_componentes: dict[Vertice, tuple[int, ...]] = {}

    for raiz, vertices_componente in componentes:
        saldo_componente = sum(
            _saldo_terminal(v, conjunto_origens, conjunto_destinos)
            for v in vertices_componente
        )

        for vertice in vertices_componente:
            saldos = _saldos_apos_remocao(
                vertice,
                raiz,
                saldo_componente,
                descoberta,
                menor,
                pai,
                filhos,
                saldo_subarvore,
                _saldo_terminal(
                    vertice, conjunto_origens, conjunto_destinos
                ),
            )
            if not saldos:
                continue

            articulacoes.add(vertice)
            saldos_componentes[vertice] = saldos
            if any(saldo != 0 for saldo in saldos):
                separadores_desbalanceados.add(vertice)
                if (
                    vertice in conjunto_candidatos
                    and vertice not in conjunto_terminais
                ):
                    obrigatorias.add(vertice)

    return ResultadoSeparadores(
        articulacoes=frozenset(articulacoes),
        separadores_desbalanceados=frozenset(
            separadores_desbalanceados
        ),
        estacoes_obrigatorias=frozenset(obrigatorias),
        saldos_componentes=saldos_componentes,
        componentes_originais=len(componentes),
    )
