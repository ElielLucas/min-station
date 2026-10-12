"""AS05-DIAG v2: verificador *exato* de cortes binários por propagação de bits.

Não altera os geradores, o modelo ou o verificador histórico. Para cada corte Z,
reconstrói integralmente a relação de alcançabilidade S x T com o conjunto
V\\Z de possíveis relés, e testa emparelhamento perfeito. Vértices terminais
podem ser origem/destino sem estação, mas só funcionam como relés quando
passáveis. O alcance permanece dirigido e preserva S ∩ T.

Verificador histórico de referência: experiments.cuts.cuts.is_valid_cut.
"""
from __future__ import annotations

from collections import deque

from experiments.cuts.cuts import CorteInvalido, build_neighborhoods, is_valid_cut


class ExactCutValidator:
    """Pré-processamento invariante em todos os cortes da mesma instância."""

    def __init__(self, S, T, A_r, *, N_plus=None, N_minus=None):
        self.origins = tuple(sorted(S))
        self.targets = tuple(sorted(T))
        if (len(self.origins) != len(self.targets) or
                len(self.origins) != len(set(self.origins)) or
                len(self.targets) != len(set(self.targets))):
            raise ValueError('AS05-DIAG: |S|=|T| e terminais únicos são obrigatórios')
        self.m = len(self.origins)
        self.terminals = frozenset(self.origins) | frozenset(self.targets)
        self.target_bits = {t: 1 << i for i, t in enumerate(self.targets)}
        if N_plus is None or N_minus is None:
            N_plus, N_minus = build_neighborhoods(A_r)
        # Cópia de vizinhanças para um snapshot estável, nunca reconstruído
        # de A_r a cada corte.
        self.plus = {v: set(succs) for v, succs in N_plus.items()}
        self.minus = {v: tuple(sorted(preds)) for v, preds in N_minus.items()}
        self.vertices = frozenset(self.terminals) | frozenset(N_plus) | frozenset(N_minus)

    def valid(self, Z) -> bool:
        """True sse o grafo S->T de alcance sem relés em Z NÃO casa todos.

        Invariante: mask[v] representa os destinos alcançáveis quando v é a
        origem da viagem (inclusive destino v=t). A partir de v só se pode
        atravessar para w como relé caso w seja passável; caso contrário,
        apenas o próprio w=t pode ser alcançado como destino final.
        """
        blocked = set(Z)
        m = self.m
        if not m:
            return False
        # Certificadores baratos (mas EXATOS quando detectam deficiência):
        # algum s sem caminho até T, OU algum t inalcançável por qualquer S.
        # O segundo caso é crucial em C1 do lado dos destinos; o validador
        # histórico só explorava a primeira direção e caía no matching caro.
        seen = set(self.targets)
        queue = deque(self.targets)
        while queue:
            w = queue.popleft()
            if w not in self.target_bits and (w in blocked or (m < 2 and w in self.terminals)):
                continue
            for u in self.minus.get(w, ()):
                if u not in seen:
                    seen.add(u)
                    queue.append(u)
        if any(s not in seen for s in self.origins):
            return True
        seen = set(self.origins)
        queue = deque(self.origins)
        origins_set = set(self.origins)
        while queue:
            u = queue.popleft()
            if u not in origins_set and (u in blocked or (m < 2 and u in self.terminals)):
                continue
            for w in self.plus.get(u, ()):
                if w not in seen:
                    seen.add(w)
                    queue.append(w)
        if any(t not in seen for t in self.targets):
            return True
        # Teste completo de matching para deficiência de Hall sem origem
        # isolada/destino inalcançável: não é omitido nem aproximado.
        # Cada nó de destino começa com sua opção de ser ponto final.
        mask = dict(self.target_bits)
        propagated = {}
        queue = deque(self.targets)
        queued = set(self.targets)
        while queue:
            w = queue.popleft()
            queued.remove(w)
            if w in blocked or (m < 2 and w in self.terminals):
                outward = self.target_bits.get(w, 0)
            else:
                outward = mask.get(w, 0)
            delta = outward & ~propagated.get(w, 0)
            if not delta:
                continue
            propagated[w] = propagated.get(w, 0) | delta
            for u in self.minus.get(w, ()):
                previous = mask.get(u, 0)
                updated = previous | delta
                if updated != previous:
                    mask[u] = updated
                    if u not in queued:
                        queue.append(u)
                        queued.add(u)
        # Falha imediata para origem que não alcança destino algum.
        if any(mask.get(s, 0) == 0 for s in self.origins):
            return True
        # Emparelhamento bipartido exato (augmenting paths). A ordem dos
        # destinos é canônica; cada bit indica aresta S->T alcançável.
        matched = [-1] * m
        for start in range(m):
            queue = deque([start])
            # Para cada origem descoberta, guarda o destino usado para chegar
            # a ela através de uma aresta de emparelhamento; -1 na raiz.
            source_previous_target = {start: -1}
            target_parent = {}
            free_target = None
            while queue and free_target is None:
                origin_idx = queue.popleft()
                choices = mask.get(self.origins[origin_idx], 0)
                while choices:
                    bit = choices & -choices
                    choices -= bit
                    t_idx = bit.bit_length() - 1
                    if t_idx in target_parent:
                        continue
                    target_parent[t_idx] = origin_idx
                    previous = matched[t_idx]
                    if previous < 0:
                        free_target = t_idx
                        break
                    if previous not in source_previous_target:
                        source_previous_target[previous] = t_idx
                        queue.append(previous)
            if free_target is None:
                return True
            t_idx = free_target
            while t_idx >= 0:
                origin_idx = target_parent[t_idx]
                matched[t_idx] = origin_idx
                t_idx = source_previous_target[origin_idx]
        return False

    def check_all(self, cuts, *, origem='', audit_legacy_up_to: int = 0):
        """Nunca aceita corte sem verificar. Auditoria opcional independente."""
        for i, cut in enumerate(cuts):
            is_valid = self.valid(cut)
            if i < audit_legacy_up_to:
                legacy = is_valid_cut(self.origins, self.targets, (), cut,
                                      N_plus=self.plus, N_minus={v: set(x) for v, x in self.minus.items()})
                if legacy != is_valid:
                    raise RuntimeError('AS05-DIAG: desacordo entre verificadores')
            if not is_valid:
                raise CorteInvalido(f'[{origem}] corte inválido |Z|={len(cut)}: {sorted(cut)[:20]}')
