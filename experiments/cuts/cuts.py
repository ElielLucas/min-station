"""
Famílias de cortes C1, C2, C4-DM e C3 para o MIN-STATION (Das).

Todas as funções geradoras são puras: recebem estruturas de dados e retornam
listas de frozensets. O chamador decide como adicioná-las ao modelo Gurobi.

Convenção: cada frozenset Z representa um corte  sum_{v in Z} y[v] >= 1.
"""

from collections import deque
from heapq import heappush, heappop


class CorteInvalido(RuntimeError):
    """Um corte y(Z) >= 1 falhou a verificação de validade (V∖Z viável)."""


class InstanciaInviavel(RuntimeError):
    """Corte mínimo com Z=∅: a instância é inviável mesmo com y ≡ 1."""


# ── Utilitários ───────────────────────────────────────────────────────────────

def build_neighborhoods(A_r):
    """Retorna (N_plus, N_minus) indexados por vértice."""
    N_plus  = {}
    N_minus = {}
    for u, v in A_r:
        N_plus.setdefault(u, set()).add(v)
        N_minus.setdefault(v, set()).add(u)
    return N_plus, N_minus


def dijkstra_from(src, adj):
    """Dijkstra completo a partir de src (sem limite de alcance)."""
    dist = {src: 0.0}
    pq   = [(0.0, src)]
    while pq:
        d, u = heappop(pq)
        if d > dist.get(u, float('inf')):
            continue
        for w, cw in adj.get(u, []):
            nd = d + cw
            if nd < dist.get(w, float('inf')):
                dist[w] = nd
                heappush(pq, (nd, w))
    return dist


def _adj_reversa(adj):
    """Grafo com todos os arcos invertidos: (u,v,w) em adj vira (v,u,w)."""
    rev = {}
    for u, vizinhos in adj.items():
        for v, w in vizinhos:
            rev.setdefault(v, []).append((u, w))
    return rev


def dijkstra_to(dst, adj):
    """
    Distância de CADA vértice ATÉ dst (não de dst para eles).

    Em grafo não-dirigido isso coincide com dijkstra_from(dst, adj), mas
    algumas instâncias (redes TNTP como Philadelphia) têm arcos de mão
    única — construir_adjacencia não simetriza. Rodar Dijkstra no grafo
    reverso é o cálculo correto de "chegar em dst", que é o que a prova de
    C2 do lado dos destinos exige.
    """
    return dijkstra_from(dst, _adj_reversa(adj))


# ── C1: primeiro e último salto ───────────────────────────────────────────────

def generate_C1(S, T, N_plus, N_minus):
    r"""
    s ∈ S\T com N+(s) ∩ T = ∅  →  sum_{v ∈ N+(s)} y[v] >= 1
    t ∈ T\S com N-(t) ∩ S = ∅  →  sum_{v ∈ N-(t)} y[v] >= 1
    """
    S_set, T_set = set(S), set(T)
    cuts = set()
    for s in S_set - T_set:
        nbrs = N_plus.get(s, frozenset())
        if nbrs and not (nbrs & T_set):
            cuts.add(frozenset(nbrs))
    for t in T_set - S_set:
        nbrs = N_minus.get(t, frozenset())
        if nbrs and not (nbrs & S_set):
            cuts.add(frozenset(nbrs))
    return list(cuts)


# ── C2: bandas de distância ───────────────────────────────────────────────────

def generate_C2(S, T, adj, r, V):
    r"""
    Para s ∈ S\T: faixas (a, a+r] com a+r < D_s = min_{t∈T} d(s,t), medidas
    por d(s,·) (Dijkstra saindo de s — a direção que o robô percorre).

    Para t ∈ T\S: faixas análogas, mas medidas por d(·,t) — a distância de
    CADA vértice ATÉ t, não de t até eles. Em grafo não-dirigido as duas
    coincidem, mas algumas instâncias (redes TNTP como Philadelphia) têm
    arcos de mão única; usar d(t,·) ali geraria bandas com a métrica
    errada e cortes potencialmente inválidos.
    """
    S_set, T_set = set(S), set(T)
    V_set = set(V)
    cuts  = set()

    for s in S_set - T_set:
        d_s = dijkstra_from(s, adj)
        D_s = min((d_s.get(t, float('inf')) for t in T_set), default=float('inf'))
        if not (D_s < float('inf') and D_s > r + 1e-9):
            continue
        a = 0.0
        while a + r < D_s - 1e-9:
            band = frozenset(
                v for v in V_set
                if a + 1e-9 < d_s.get(v, float('inf')) <= a + r + 1e-9
            )
            if band:
                cuts.add(band)
            a += r

    for t in T_set - S_set:
        d_t = dijkstra_to(t, adj)
        D_t = min((d_t.get(s, float('inf')) for s in S_set), default=float('inf'))
        if not (D_t < float('inf') and D_t > r + 1e-9):
            continue
        a = 0.0
        while a + r < D_t - 1e-9:
            band = frozenset(
                v for v in V_set
                if a + 1e-9 < d_t.get(v, float('inf')) <= a + r + 1e-9
            )
            if band:
                cuts.add(band)
            a += r

    return list(cuts)


# ── C4-DM: Hall de primeiro salto via Dulmage-Mendelsohn ─────────────────────

def _augment(s, adj, mfwd, mbwd, visited):
    for t in adj.get(s, ()):
        if t in visited:
            continue
        visited.add(t)
        if t not in mbwd or _augment(mbwd[t], adj, mfwd, mbwd, visited):
            mfwd[s] = t
            mbwd[t] = s
            return True
    return False


def _max_matching(left, adj):
    import sys
    limit = max(sys.getrecursionlimit(), len(left) * 4 + 200)
    sys.setrecursionlimit(limit)
    mfwd, mbwd = {}, {}
    for s in left:
        _augment(s, adj, mfwd, mbwd, set())
    return mfwd, mbwd


def _alternating_reach(start, adj, mbwd):
    """BFS sobre caminhos M-alternantes a partir de start (lista de origens)."""
    reachable = set(start)
    queue     = deque(start)
    while queue:
        s = queue.popleft()
        for t in adj.get(s, ()):
            if t in mbwd:
                ns = mbwd[t]
                if ns not in reachable:
                    reachable.add(ns)
                    queue.append(ns)
    return reachable


def generate_C4_DM(S, T, N_plus, N_minus):
    """
    Dulmage-Mendelsohn em B_∅ (arcos diretos S→T em A_r).
    Por cada origem (destino) não emparelhada gera um corte via N+(S') (N-(T')).

    Segue §5.4 de direcoes-pli-min-station.md: as origens candidatas são
    S' ⊆ S∖T (um robô que parte de v ∈ S∩T pode ficar parado ali pelo Lema 5
    de Das, e não sustenta o argumento de primeiro salto), mas a vizinhança
    que define a deficiência é N⁺(S') ∩ T com T **inteiro** — um robô de S∖T
    pode perfeitamente terminar em v ∈ S∩T, desde que o robô de v saia, que é
    o que o balanço unificado permite (base-formulation.md §6.1). Do lado dos
    destinos, o simétrico: T' ⊆ T∖S contra S inteiro.

    Até 2026-09-26 o emparelhamento usava T∖S (e S∖T) também do lado da
    vizinhança, suprimindo emparelhamentos legítimos com S∩T. Isso criava
    deficiência de Hall inexistente e os cortes daí derivados cortavam
    soluções viáveis. Ver correcao-c4-dm.md.

    As iterações são ordenadas porque emparelhamento máximo não é único: sem
    isso a família gerada muda entre processos, junto com o LB que ela produz.
    """
    S_set, T_set = set(S), set(T)
    S_only = S_set - T_set
    T_only = T_set - S_set
    cuts = set()

    # Lado S: origens que não alcançam nenhum destino diretamente
    adj_S = {s: sorted(set(N_plus.get(s, ())) & T_set) for s in S_only}
    mfwd_s, mbwd_s = _max_matching(sorted(S_only), adj_S)
    for s0 in sorted(s for s in S_only if s not in mfwd_s):
        S_prime = _alternating_reach([s0], adj_S, mbwd_s)
        N_prime = set()
        for s in S_prime:
            N_prime |= N_plus.get(s, set())
        if N_prime:
            cuts.add(frozenset(N_prime))

    # Lado T: destinos que não recebem nenhuma origem diretamente
    adj_T = {t: sorted(set(N_minus.get(t, ())) & S_set) for t in T_only}
    mfwd_t, mbwd_t = _max_matching(sorted(T_only), adj_T)
    for t0 in sorted(t for t in T_only if t not in mfwd_t):
        T_prime = _alternating_reach([t0], adj_T, mbwd_t)
        N_prime = set()
        for t in T_prime:
            N_prime |= N_minus.get(t, set())
        if N_prime:
            cuts.add(frozenset(N_prime))

    return sorted(cuts, key=sorted)


# ── C3: separação iterativa de LP via max-flow ────────────────────────────────

def _build_flow_net(s, S_set, T_set, A_r, y_star):
    """
    Rede de nós divididos para checar se origem s alcança T com y* dado.

    - sigma → s_out (1)
    - s_in  → s_out (INF)            # s é origem: trânsito livre
    - t_in  → t_out (INF), t_out → tau (1)  # t é destino: termina livremente
    - v_in  → v_out (y*[v])          # relay: capacidade y*
    - u_out → v_in  (INF) para (u,v) ∈ A_r
    """
    INF   = 1e9
    graph = {}
    cap   = {}

    def arc(u, v, c):
        graph.setdefault(u, {})[v] = None
        graph.setdefault(v, {})[u] = None
        cap[(u, v)] = cap.get((u, v), 0.0) + c
        cap.setdefault((v, u), 0.0)

    V_all = set()
    for u, v in A_r:
        V_all.add(u)
        V_all.add(v)
    V_all.add(s)

    arc('_s', f'{s}_out', 1.0)
    arc(f'{s}_in', f'{s}_out', INF)
    if s in T_set:
        # s ∈ S ∩ T: o robô pode ficar parado ocupando o próprio alvo
        # (Lema 5 de Das), sem depender de estação nem de caminho algum.
        arc(f'{s}_out', '_t', 1.0)

    for v in V_all:
        if v == s:
            continue
        if v in T_set:
            arc(f'{v}_in', f'{v}_out', INF)
            arc(f'{v}_out', '_t', 1.0)
        else:
            arc(f'{v}_in', f'{v}_out', max(0.0, y_star.get(v, 0.0)))

    for u, v in A_r:
        arc(f'{u}_out', f'{v}_in', INF)

    return graph, cap, V_all


def _edmonds_karp(graph, cap, source, sink):
    """Max-flow Edmonds-Karp. Modifica cap in-place. Retorna valor de fluxo."""
    flow = 0.0
    while True:
        # BFS
        parent = {source: None}
        queue  = deque([source])
        while queue and sink not in parent:
            u = queue.popleft()
            for v in graph.get(u, {}):
                if v not in parent and cap.get((u, v), 0.0) > 1e-9:
                    parent[v] = u
                    queue.append(v)
        if sink not in parent:
            break
        # gargalo
        pf = float('inf')
        v  = sink
        while parent[v] is not None:
            u = parent[v]
            pf = min(pf, cap[(u, v)])
            v = u
        # aumentar
        v = sink
        while parent[v] is not None:
            u = parent[v]
            cap[(u, v)] -= pf
            cap[(v, u)] = cap.get((v, u), 0.0) + pf
            v = u
        flow += pf
    return flow


def _reachable_set(graph, cap, source):
    visited = {source}
    queue   = deque([source])
    while queue:
        u = queue.popleft()
        for v in graph.get(u, {}):
            if v not in visited and cap.get((u, v), 0.0) > 1e-9:
                visited.add(v)
                queue.append(v)
    return visited


def check_C3_violations_dest(S, T, A_r, y_star):
    """
    Versão simétrica de check_C3_violations: por cada destino t,
    testa se alguma origem consegue alcançar t com fluxo ≥ 1.
    Usa a rede reversa: t é a fonte, S são os sorvedouros.
    """
    S_set = set(S)
    T_set = set(T)
    A_r_rev = [(v, u) for u, v in A_r]
    cuts = []

    for t in T:
        graph, cap, V_all = _build_flow_net(t, T_set, S_set, A_r_rev, y_star)
        flow = _edmonds_karp(graph, cap, '_s', '_t')
        if flow < 1.0 - 1e-6:
            reachable = _reachable_set(graph, cap, '_s')
            Z = set()
            for v in V_all:
                if v == t:
                    continue
                if f'{v}_in' in reachable and f'{v}_out' not in reachable:
                    Z.add(v)
            if Z:
                cuts.append(frozenset(Z))

    return cuts


def _build_flow_net_aggregate(S, T, A_r, y_star):
    """
    Rede N(y*) para separação de cortes fracionários clássicos.

    Capacidades agregadas (m robôs simultâneos):
      σ  → s_out         cap 1            (uma unidade por origem, s ∈ S)
      t_in → τ           cap 1            (uma unidade por destino, t ∈ T)
      v_in → v_out       cap (m-1)*y*[v]  se v é terminal (v ∈ S ∪ T)
      v_in → v_out       cap m*y*[v]      caso contrário (relé comum)
      u_out → v_in       cap INF          para (u,v) ∈ A_r

    Um vértice em S ∩ T recebe os dois arcos de unidade própria (σ→v_out e
    v_in→τ) — o Lema 5 de Das permite que o mesmo vértice seja origem de um
    robô e alvo de outro. O arco terminal sai de t_in (não de t_out): é
    t_in que reparte sua entrada entre a unidade que termina ali (grátis,
    cap 1) e o trânsito de outros robôs (cap (m-1)*y_t) — ver base-formulation
    §7.2. Sair de t_out forçaria a própria unidade terminal a atravessar o
    gargalo de trânsito, contradizendo a formulação.

    Max-flow σ→τ < m ⟹ existe corte fracionário violado.
    """
    m   = len(S)
    INF = 1e9
    S_set = set(S)
    T_set = set(T)

    graph = {}
    cap   = {}

    def arc(u, v, c):
        graph.setdefault(u, {})[v] = None
        graph.setdefault(v, {})[u] = None
        cap[(u, v)] = cap.get((u, v), 0.0) + c
        cap.setdefault((v, u), 0.0)

    V_all = set()
    for u, v in A_r:
        V_all.add(u)
        V_all.add(v)
    for s in S_set:
        V_all.add(s)
    for t in T_set:
        V_all.add(t)

    for v in V_all:
        yv = max(0.0, y_star.get(v, 0.0))
        is_S = v in S_set
        is_T = v in T_set
        if is_S:
            arc('_s', f'{v}_out', 1.0)
        if is_T:
            arc(f'{v}_in', '_t', 1.0)
        if is_S or is_T:
            arc(f'{v}_in', f'{v}_out', (m - 1) * yv)
        else:
            arc(f'{v}_in', f'{v}_out', m * yv)

    for u, v in A_r:
        arc(f'{u}_out', f'{v}_in', INF)

    return graph, cap, V_all, m


def _extract_Z(reachable, V_all, S_set, T_set, m):
    """
    Z(X) = {v : v_in ∈ reachable, v_out ∉ reachable}  (Teorema 4).

    Sem exclusão de terminais: um terminal só entra em Z quando seu arco de
    unidade própria (σ→v_out ou v_in→τ) está saturado, isto é, quando
    precisa servir de ponto de recarga para fluxo adicional — a semântica
    de base-formulation §7.2. Única exceção: com m=1, κ_v=0 nos terminais
    (Σ_{v∈Z} κ_v y_v nunca pode ser satisfeita por um terminal), então eles
    são descartados por não poderem ajudar a desigualdade.
    """
    terminal_util = (m >= 2)
    Z = set()
    for v in V_all:
        if f'{v}_in' in reachable and f'{v}_out' not in reachable:
            if not terminal_util and (v in S_set or v in T_set):
                continue
            Z.add(v)
    return Z


def separate_classical_fracs(S, T, A_r, y_star):
    """
    Separa cortes fracionários clássicos via max-flow na rede N(y*).

    Se max-flow < m, o corte mínimo define um conjunto Z de vértices
    com κ_v y*(v) < δ(X). Retorna a versão arredondada y(Z) ≥ 1,
    que garante LP_cov ≥ z_LP (Teorema do §5.9).

    Se Z sai vazio, a capacidade do corte independe de y: a instância é
    inviável mesmo com y ≡ 1 (levanta InstanciaInviavel).

    Retorna lista de frozensets.
    """
    graph, cap, V_all, m = _build_flow_net_aggregate(S, T, A_r, y_star)
    flow = _edmonds_karp(graph, cap, '_s', '_t')

    if flow >= m - 1e-6:
        return []

    S_set, T_set = set(S), set(T)
    reachable = _reachable_set(graph, cap, '_s')
    Z = _extract_Z(reachable, V_all, S_set, T_set, m)

    if not Z:
        raise InstanciaInviavel(
            f'corte mínimo de capacidade {flow:.6f} < m={m} com Z=∅: '
            'instância inviável mesmo com y ≡ 1'
        )

    # versão arredondada: y(Z) >= 1
    if sum(y_star.get(v, 0.0) for v in Z) < 1.0 - 1e-8:
        return [frozenset(Z)]
    return []


def generate_C5_threshold(S, T, A_r, y_star, thresholds=(0.5, 0.3, 0.1, 0.01)):
    """
    C5 heurístico (Hall multi-salto) por limiar.

    Para cada θ: define o candidato C_θ = {v : y*(v) ≥ θ}. Roda a separação
    INTEIRA (y=1 em C_θ, y=0 fora) na rede N(y). Se o max-flow for < m,
    C_θ é inviável, e o corte mínimo dá um Z ∈ 𝒵 (Teorema 6) — por
    construção, Z é disjunto de C_θ. Aceita o corte y(Z) ≥ 1 se
    y*(Z) < 1 (violado pelo LP corrente).

    Retorna lista de frozensets.
    """
    S_set, T_set = set(S), set(T)
    cuts = set()

    for theta in thresholds:
        C_theta = {v for v in y_star if y_star[v] >= theta}
        if not C_theta:
            continue
        y_bin = {v: 1.0 for v in C_theta}

        graph, cap, V_all, m = _build_flow_net_aggregate(S, T, A_r, y_bin)
        flow = _edmonds_karp(graph, cap, '_s', '_t')
        if flow >= m - 1e-6:
            continue  # C_θ já é viável

        reachable = _reachable_set(graph, cap, '_s')
        Z = _extract_Z(reachable, V_all, S_set, T_set, m)
        if not Z:
            raise InstanciaInviavel(
                f'C5(θ={theta}): corte mínimo de capacidade {flow:.6f} < m={m} '
                'com Z=∅: instância inviável mesmo com y ≡ 1'
            )
        if sum(y_star.get(v, 0.0) for v in Z) < 1.0 - 1e-8:
            cuts.add(frozenset(Z))

    return list(cuts)


def check_C3_violations(S, T, A_r, y_star):
    """
    Para cada origem s: testa se max-flow(s → T) < 1.
    Retorna lista de frozensets de vértices que formam cortes violados.
    """
    S_set = set(S)
    T_set = set(T)
    cuts  = []

    for s in S:
        graph, cap, V_all = _build_flow_net(s, S_set, T_set, A_r, y_star)
        flow = _edmonds_karp(graph, cap, '_s', '_t')
        if flow < 1.0 - 1e-6:
            reachable = _reachable_set(graph, cap, '_s')
            Z = set()
            for v in V_all:
                if v == s:
                    continue
                if f'{v}_in' in reachable and f'{v}_out' not in reachable:
                    Z.add(v)
            if Z:
                cuts.append(frozenset(Z))

    return cuts


# ── Validador de cortes ────────────────────────────────────────────────────────

def _passavel(v, Z, S_set, T_set, m):
    """v pode servir de intermediário em V∖Z? (κ_v=0 em terminais com m=1)."""
    if v in Z:
        return False
    if m < 2 and (v in S_set or v in T_set):
        return False
    return True


def is_valid_cut(S, T, A_r, Z, N_plus=None, N_minus=None):
    """
    True se V∖Z é inviável, isto é, se y(Z) >= 1 é uma desigualdade válida.

    Critério (Proposição 3.1 + Teorema 6): Z é válido sse o bipartido de
    alcance {(s,t) : s alcança t em A_r usando só intermediários de V∖Z}
    não tem emparelhamento perfeito. Origens e destinos são sempre extremos
    válidos de sua própria viagem, independente de pertencerem a Z; um
    vértice s ∈ S ∩ T alcança a si mesmo trivialmente (Lema 5 de Das).

    Duas fases: uma BFS reversa O(|A_r|) que retorna cedo no caso comum
    (alguma origem não alcança T algum), e só quando todas as origens
    alcançam algum destino paga o emparelhamento máximo completo.
    """
    S_set, T_set = set(S), set(T)
    m = len(S)
    Z = set(Z)

    if N_plus is None or N_minus is None:
        N_plus, N_minus = build_neighborhoods(A_r)

    # Fase barata: BFS reversa a partir de T inteiro. Um vértice w só serve
    # de RELÉ para estender a busca (continuar retrocedendo por ele) se for
    # passável (tiver estação); ser origem ou destino não basta — só o
    # próprio arrivo/partida daquele vértice é grátis, não o trânsito
    # de terceiros por ele.
    visited = set(T_set)
    queue = deque(T_set)
    while queue:
        w = queue.popleft()
        pode_relayar = (w in T_set) or _passavel(w, Z, S_set, T_set, m)
        if not pode_relayar:
            continue
        for u in N_minus.get(w, ()):
            if u not in visited:
                visited.add(u)
                queue.append(u)
    for s in S_set:
        if s not in visited:
            return True  # alguma origem não alcança T algum: corte válido

    # Fase completa: testar emparelhamento perfeito S -> T via intermediários
    # de V∖Z (Teorema 1: C viável sse B_C tem emparelhamento perfeito).
    # Mesma regra: chegar num vértice de T é sempre grátis (reach.add), mas
    # continuar a partir dele (usá-lo como relé) exige que seja passável.
    adj = {}
    for s in S_set:
        reach = set()
        if s in T_set:
            reach.add(s)  # ficar parado (Lema 5), sempre disponível
        seen = {s}
        q = deque([s])
        while q:
            u = q.popleft()
            for w in N_plus.get(u, ()):
                if w in seen:
                    continue
                if w in T_set:
                    reach.add(w)
                if _passavel(w, Z, S_set, T_set, m):
                    seen.add(w)
                    q.append(w)
        adj[s] = reach

    mfwd, _ = _max_matching(list(S_set), adj)
    return len(mfwd) < m


def assert_valid_cuts(S, T, A_r, cuts, origem='', N_plus=None, N_minus=None):
    """Levanta CorteInvalido se algum Z em cuts não for válido."""
    for Z in cuts:
        if not is_valid_cut(S, T, A_r, Z, N_plus, N_minus):
            raise CorteInvalido(
                f'[{origem}] corte inválido |Z|={len(Z)}: {sorted(Z)[:20]}'
            )


# ── Oráculo inteiro restrito (E8, Bloco 1) ────────────────────────────────────

def _co_reachable_set(graph, cap, sink):
    """Vértices que alcançam sink no residual (BFS reversa sobre capacidades)."""
    visited = {sink}
    queue = deque([sink])
    while queue:
        v = queue.popleft()
        for u in graph.get(v, {}):
            if u not in visited and cap.get((u, v), 0.0) > 1e-9:
                visited.add(u)
                queue.append(u)
    return visited


def integer_oracle(S, T, N_plus, C):
    r"""
    Testa viabilidade do modelo compacto (rede de fluxo agregada) para
    y binário com C = {v : y_v = 1}, sem materializar A_r inteiro.

    Equivalente a `_build_flow_net_aggregate(S, T, A_r, y_bin)` +
    `_edmonds_karp` + `_extract_Z`, com y_bin[v] = 1 se v ∈ C senão 0, mas
    O(|S∪T∪C| + arcos entre eles) em vez de O(|A_r|) — decisivo quando
    |A_r| é grande (ex.: cc12-2p, |A_r| ≈ 2,8 milhões) e C é pequeno.

    N_plus deve ser pré-computado uma vez por instância (`build_neighborhoods`)
    e reaproveitado entre chamadas — não é reconstruído aqui.

    Vértices fora de S∪T∪C têm capacidade de trânsito m*y_v = 0 no modelo
    original, então são "becos sem saída" para o fluxo e podem ser omitidos
    da rede sem alterar o valor do max-flow. Mas podem aparecer no corte 𝒵
    como CANDIDATOS (vértices ainda não instalados que, se instalados,
    quebrariam o corte) — capturados explicitamente no passo 2 abaixo, já
    que não têm nó próprio na rede restrita.

    Retorna (viavel: bool, Z: frozenset ou None). Se inviável, Z é o corte
    combinatório mínimo do lado da fonte (Teorema 6).
    """
    m = len(S)
    S_set, T_set = set(S), set(T)
    C_set = set(C)
    nodes = S_set | T_set | C_set

    INF = 1e9
    graph = {}
    cap = {}

    def arc(u, v, c):
        graph.setdefault(u, {})[v] = None
        graph.setdefault(v, {})[u] = None
        cap[(u, v)] = cap.get((u, v), 0.0) + c
        cap.setdefault((v, u), 0.0)

    for v in nodes:
        is_S = v in S_set
        is_T = v in T_set
        if is_S:
            arc('_s', f'{v}_out', 1.0)
        if is_T:
            arc(f'{v}_in', '_t', 1.0)
        if v in C_set:
            cap_relay = float(m - 1 if (is_S or is_T) else m)
        else:
            cap_relay = 0.0
        arc(f'{v}_in', f'{v}_out', cap_relay)

    for u in nodes:
        for w in N_plus.get(u, ()):
            if w in nodes:
                arc(f'{u}_out', f'{w}_in', INF)

    flow = _edmonds_karp(graph, cap, '_s', '_t')
    if flow >= m - 1e-6:
        return True, None

    # passo 1: corte restrito aos nós já modelados (S∪T∪C)
    X = _reachable_set(graph, cap, '_s')
    Z = _extract_Z(X, nodes, S_set, T_set, m)

    # passo 2: candidatos não instalados adjacentes à fronteira alcançável.
    # w ∉ nodes não tem nó próprio na rede restrita, mas se algum u com
    # u_out ∈ X tem arco (u,w) em A_r (via N_plus completo, não filtrado),
    # então w_in seria alcançável na rede completa (arco INF) enquanto
    # w_out não (capacidade 0 com y_w=0) — mesma regra de _extract_Z.
    for u in nodes:
        if f'{u}_out' not in X:
            continue
        for w in N_plus.get(u, ()):
            if w not in nodes:
                Z.add(w)

    return False, frozenset(Z)
