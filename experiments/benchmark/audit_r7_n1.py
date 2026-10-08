#!/usr/bin/env python3
"""N1-T4: releitura *offline* dos pools R7 já gravados, sem novo oráculo Gurobi.

Entradas imutáveis: r7-plato.csv e cinco arquivos de instância; os nomes
históricos TR/BP são mapeados a seus arquivos estruturais correspondentes.
Não extrapola pools truncados ao platô completo.
"""
import csv
from collections import Counter, defaultdict, deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'results/benchmark/r7-plato.csv'
OUT = ROOT / 'results/benchmark'
INSTANCE_PATHS = {
    'TR-k2-L5-r2': 'instances/estrutural/tr/tr-k2-L5-r2-siginf-m2.txt',
    'BP-nao-[3,1]-q2': 'instances/estrutural/bp/bp-nao-q2-B2-s0.txt',
    'mapf-maze-32-32-2-m10-f4': 'instances/benchmark-v1/mapf/mapf-maze-32-32-2-m10-f4.txt',
    'lin-lin03-regiao-f4': None,  # resolvido pela localização única do arquivo
    'puc-cc9-2p-seed-r1': 'instances/benchmark-v1/puc/puc-cc9-2p-seed-r1.txt',
}


def read_instance(name):
    relative = INSTANCE_PATHS[name]
    if relative is None:
        paths = list((ROOT / 'instances').rglob('lin-lin03-regiao-f4.txt'))
        if len(paths) != 1:
            raise RuntimeError(f'{name}: esperado um arquivo, obtidos {len(paths)}')
        path = paths[0]
    else:
        path = ROOT / relative
    if not path.is_file():
        raise FileNotFoundError(path)
    lines = [line.strip() for line in path.read_text(encoding='utf8').splitlines()
             if line.strip() and not line.lstrip().startswith('#')]
    r = None
    edges = []
    s = t = None
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith('R '):
            r = float(line.split()[1])
        elif line.startswith('S '):
            s = lines[i + 1].split()
            if len(s) != int(line.split()[1]):
                raise ValueError(f'{path}: tamanho S incorreto')
            i += 1
        elif line.startswith('T '):
            t = lines[i + 1].split()
            if len(t) != int(line.split()[1]):
                raise ValueError(f'{path}: tamanho T incorreto')
            i += 1
        elif len(line.split()) == 3 and not line.startswith(('N ', 'M ')):
            u, v, w = line.split()
            edges.append((u, v, float(w)))
        i += 1
    if r is None or s is None or t is None:
        raise ValueError(f'{path}: arquivo malformado')
    adj = defaultdict(dict)
    for u, v, weight in edges:
        adj[u][v] = min(weight, adj[u].get(v, float('inf')))
        adj[v][u] = min(weight, adj[v].get(u, float('inf')))
    return s, t, r, adj, path


class Reach:
    """Vizinhança de alcance limitada a r, usando pesos não negativos."""
    def __init__(self, adj, r):
        self.adj, self.r, self.cache = adj, r, {}

    def of(self, origin):
        if origin not in self.cache:
            import heapq
            found, queue = {origin: 0.0}, [(0.0, origin)]
            while queue:
                d, u = heapq.heappop(queue)
                if d > found[u] + 1e-12:
                    continue
                for v, w in self.adj.get(u, {}).items():
                    nd = d + w
                    if nd <= self.r + 1e-12 and nd < found.get(v, float('inf')):
                        found[v] = nd
                        heapq.heappush(queue, (nd, v))
            self.cache[origin] = frozenset(found)
        return self.cache[origin]


def component_matching(sources, targets, installation, reach):
    """Caracterização por H[C]: diretos + bicliques de componentes."""
    C = set(installation)
    unseen = set(C)
    components = []
    while unseen:
        start = min(unseen)
        unseen.remove(start)
        group = {start}
        queue = deque([start])
        while queue:
            u = queue.popleft()
            neighbors = set(reach.of(u)) & unseen
            unseen -= neighbors
            group.update(neighbors)
            queue.extend(sorted(neighbors))
        components.append(group)

    target_set = set(targets)
    reachable = {s: set(reach.of(s)) & target_set for s in sources}
    for group in components:
        eligible_s = [s for s in sources if any(c in reach.of(s) for c in group)]
        eligible_t = {t for t in targets if any(c in reach.of(t) for c in group)}
        for s in eligible_s:
            reachable[s].update(eligible_t)
    return reachable, components


def matching_hall(sources, reachable):
    """Devolve tamanho de matching máximo e testemunha por caminhos alternantes."""
    mate_t = {}
    def augment(s, seen):
        for t in sorted(reachable[s]):
            if t in seen:
                continue
            seen.add(t)
            if t not in mate_t or augment(mate_t[t], seen):
                mate_t[t] = s
                return True
        return False
    for s in sources:
        augment(s, set())
    matched_s = set(mate_t.values())
    q = deque(sorted(set(sources) - matched_s))
    witness_s, witness_t = set(q), set()
    while q:
        s = q.popleft()
        for t in sorted(reachable[s]):
            if t in witness_t:
                continue
            witness_t.add(t)
            if t in mate_t and mate_t[t] not in witness_s:
                other = mate_t[t]
                witness_s.add(other)
                q.append(other)
    deficit = len(witness_s) - len(witness_t)
    if len(mate_t) != len(sources) and deficit <= 0:
        raise AssertionError('testemunha de Hall inválida')
    if len(mate_t) == len(sources):
        return len(mate_t), [], [], 0
    return len(mate_t), sorted(witness_s), sorted(witness_t), deficit


def write_csv(path, rows, fields):
    with path.open('w', encoding='utf8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def audit():
    with SOURCE.open(newline='', encoding='utf8') as fh:
        rows = list(csv.DictReader(fh))
    grouped = defaultdict(list)
    for row in rows:
        grouped[row['instancia']].append(row)
    frequency_rows, witness_rows, audit_rows = [], [], []
    for name, pool in grouped.items():
        sources, targets, r, adj, path = read_instance(name)
        reach = Reach(adj, r)
        sets = [set(row['estacoes'].split()) for row in pool]
        zfreq = Counter(frozenset(row['Z'].split()) for row in pool if row['Z'].strip())
        for Z in sorted(zfreq, key=lambda val: (len(val), tuple(sorted(val)))):
            count = sum(not (C & Z) for C in sets)
            frequency_rows.append({
                'instancia': name, 'Z': ' '.join(sorted(Z)), 'n_Z': len(Z),
                'z_freq_retorno': zfreq[Z], 'z_n_instalacoes_cortadas': count,
                'n_instalacoes_gravadas': len(pool),
                'pool_truncado': int(any(x['truncado_pool'] == '1' for x in pool)),
            })
        classifications = Counter()
        mismatches = 0
        for row, C in zip(pool, sets):
            graph, components = component_matching(sources, targets, C, reach)
            nmatch, bad_sources, bad_targets, deficit = matching_hall(sources, graph)
            degree_zero = sorted(s for s in sources if not graph[s])
            feasible = nmatch == len(sources)
            if feasible != (row['oracle_viavel'] == '1'):
                mismatches += 1
            if feasible:
                category = 'viavel'
            elif degree_zero:
                category = 'sem_alcance_individual'
            elif deficit > 0:
                category = 'deficiencia_Hall_sem_grau_zero'
            else:
                category = 'inexplicado'
            classifications[category] += 1
            witness_rows.append({
                'instancia': name, 'idx': row['idx'], 'oracle_viavel_csv': row['oracle_viavel'],
                'matching_viavel': int(feasible), 'n_origens_grau_zero': len(degree_zero),
                'origens_grau_zero': ' '.join(degree_zero),
                'n_origens_nao_emparelhadas': len(sources) - nmatch,
                'hall_deficit': deficit,
                'hall_testemunha_origens': ' '.join(bad_sources),
                'hall_testemunha_vizinhos': ' '.join(bad_targets),
                'n_componentes_recalculado': len(components), 'categoria': category,
            })
        max_freq = max(zfreq.values(), default=0)
        max_cover = max((x['z_n_instalacoes_cortadas'] for x in frequency_rows
                         if x['instancia'] == name), default=0)
        audit_rows.append({'instancia': name, 'arquivo': str(path.relative_to(ROOT)),
                           'n_pool': len(pool), 'truncado': int(any(x['truncado_pool'] == '1' for x in pool)),
                           'n_Z': len(zfreq), 'max_z_freq_retorno': max_freq,
                           'max_z_n_instalacoes_cortadas': max_cover,
                           'divergencias_oracle_matching': mismatches,
                           **{f'categoria_{key}': classifications[key]
                              for key in ('viavel','sem_alcance_individual',
                                          'deficiencia_Hall_sem_grau_zero','inexplicado')}})
        print(name, 'pool=', len(pool), 'freq=', max_freq, 'coverage=', max_cover,
              'matching_divergencias=', mismatches)
    write_csv(OUT/'n1-r7-cortes-corrigidos.csv', frequency_rows,
              ['instancia','Z','n_Z','z_freq_retorno','z_n_instalacoes_cortadas',
               'n_instalacoes_gravadas','pool_truncado'])
    write_csv(OUT/'n1-r7-testemunhas-hall.csv', witness_rows,
              ['instancia','idx','oracle_viavel_csv','matching_viavel',
               'n_origens_grau_zero','origens_grau_zero','n_origens_nao_emparelhadas',
               'hall_deficit','hall_testemunha_origens','hall_testemunha_vizinhos',
               'n_componentes_recalculado','categoria'])
    fields = list(audit_rows[0]) if audit_rows else []
    write_csv(OUT/'n1-r7-auditoria-resumo.csv', audit_rows, fields)
    # Checagens registradas na spec; não inferir cobertura a partir da frequência.
    assert {x['instancia']: x['max_z_freq_retorno'] for x in audit_rows} == {
        'TR-k2-L5-r2': 2, 'BP-nao-[3,1]-q2': 1,
        'mapf-maze-32-32-2-m10-f4': 49, 'lin-lin03-regiao-f4': 17,
        'puc-cc9-2p-seed-r1': 21,
    }
    assert next(x for x in audit_rows if x['instancia'] == 'puc-cc9-2p-seed-r1')[
        'max_z_n_instalacoes_cortadas'] == 27
    assert all(x['divergencias_oracle_matching'] == 0 for x in audit_rows)
    return audit_rows


if __name__ == '__main__':
    audit()
