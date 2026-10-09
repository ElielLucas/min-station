#!/usr/bin/env python3
"""N1-T7: auditoria READ-ONLY do gate congelado N1 (§Gate / Promotion Criteria).

Não importa Gurobi, não gera novas instâncias, não modifica qualquer evidência.
Executar com PYTHONHASHSEED=0 por consistência com as medições anteriores.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
R = ROOT / 'results' / 'alternative-formulations'
E = ROOT / 'experiments' / 'alternative-formulations'
D = ROOT / 'docs' / 'technical' / 'plans' / 'execucao'
TOL = 1e-6
VERIFIED = 'COMPUTATIONALLY VERIFIED'
DECISION = 'PROMOTE FCC + EXISTING CUTS'
RECORD = D / 'n1-t7-decisao-cientifica.md'


def require(ok: bool, message: str) -> None:
    if not ok:
        raise AssertionError(message)


def num(row: dict, key: str) -> float | None:
    raw = row.get(key, '')
    return float(raw) if raw not in ('', None, 'NOT MEASURED') else None


def measured(row: dict, arm: str) -> float | None:
    value = num(row, arm)
    status = row.get('status_' + arm)
    if status == VERIFIED:
        require(value is not None and math.isfinite(value), f'{row.get("instancia", row.get("name"))}: {arm} marcado como medido sem valor')
        return value
    require(status == 'NOT MEASURED' and value is None, f'{row.get("instancia", row.get("name"))}: estado inconsistente em {arm}: {status} / {value}')
    return None


def load_csv(path: Path, expected: int) -> list[dict]:
    with path.open(encoding='utf-8', newline='') as f:
        rows = list(csv.DictReader(f))
    require(len(rows) == expected, f'{path.name}: esperado {expected}, encontrado {len(rows)}')
    return rows


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_chain() -> None:
    """Confere o vínculo T6→T5 congelado e os hashes relatados na T6."""
    freeze = json.loads((E / 'n1-t6-freeze.json').read_text(encoding='utf-8'))
    require(freeze['gate_t5']['triggered'] is True, 'T6 não acionada no freeze')
    require(freeze['gate_t5']['n_distinct'] < 2, 'T6 teria sido gerada sem gatilho')
    for path, wanted in freeze['gate_t5']['source_hashes'].items():
        source = ROOT / path
        require(source.is_file() and sha(source) == wanted, f'Hash T5 divergente: {path}')
    report = (D / 'n1-t6-diagnostico.md').read_text(encoding='utf-8')
    for path in (
        E / 'n1-t6-freeze.json',
        R / 'n1-t6-pares.json',
        R / 'n1-t6-certificados.json',
    ):
        require(sha(path) in report, f'Hash T6 não registrado no relatório: {path.name}')
    pairdata = json.loads((R / 'n1-t6-pares.json').read_text(encoding='utf-8'))
    certdata = json.loads((R / 'n1-t6-certificados.json').read_text(encoding='utf-8'))
    require(pairdata is not None and certdata is not None, 'Ausência das evidências T6')


def check_row(row: dict, *, phase: str) -> None:
    name = row['instancia'] if phase == 'T5' else row['name']
    opt = num(row, 'opt')
    core = measured(row, 'core_ip')
    comp = measured(row, 'lp_comp')
    fcc = measured(row, 'lp_fcc')
    fcc_k = measured(row, 'lp_fcc_k')
    fc3 = measured(row, 'lp_fc3')
    fc3_k = measured(row, 'lp_fc3_k')
    measured(row, 'lp_base')
    require(opt is not None, f'{name}: OPT ausente')
    if phase == 'T5':
        require(row['status_opt'] == VERIFIED, f'{name}: OPT sem status verificado')
    else:
        require(row['pair_status'] == 'CERTIFIED', f'{name}: OPT não certificado')
        require(row['opt_source'] == 'opt_por_enumeracao', f'{name}: origem OPT inesperada')
    if core is not None and comp is not None:
        require(abs(num(row, 'B0') - max(core, comp)) <= TOL, f'{name}: B0 inconsistente')
    if fcc_k is not None and num(row, 'B0') is not None:
        require(abs(num(row, 'delta_fcc_k') - (fcc_k - num(row, 'B0'))) <= TOL,
                f'{name}: delta_fcc_k inconsistente')
    if fcc_k is not None and fc3_k is not None:
        require(abs(num(row, 'delta_trio') - (fc3_k - fcc_k)) <= TOL,
                f'{name}: delta_trio inconsistente')
        require(fc3_k >= fcc_k - TOL, f'{name}: dominância F-C3+K violada')
    if fcc is not None and fc3 is not None:
        require(fc3 >= fcc - TOL, f'{name}: dominância F-C3 violada')
    for value in (core, comp, fcc, fcc_k, fc3, fc3_k):
        if value is not None:
            require(value <= opt + TOL, f'{name}: limite excedeu OPT')


def evaluate(t5: list[dict], t6: list[dict], witnesses: list[dict]) -> dict:
    """Somente valores numéricos medidos qualificam; famílias = unidades distintas."""
    fcc_eligible = [r for r in t5
                    if num(r, 'gamma') is not None and num(r, 'gamma') > TOL
                    and measured(r, 'lp_fcc_k') is not None
                    and num(r, 'delta_fcc_k') > TOL]
    fcc_families = sorted({r['tipo'] for r in fcc_eligible})
    trio_rows = []
    for phase, source in (('T5', t5), ('T6', t6)):
        for r in source:
            fcc_k = measured(r, 'lp_fcc_k')
            fc3_k = measured(r, 'lp_fc3_k')
            if fcc_k is not None and fc3_k is not None and fc3_k - fcc_k > TOL:
                trio_rows.append((phase, r))
    trio_families = sorted({r['tipo'] if phase == 'T5' else r['family'] for phase, r in trio_rows})
    trio_nontrivial = [r['instancia'] if phase == 'T5' else r['name']
                       for phase, r in trio_rows
                       if num(r, 'core_ip') < num(r, 'opt') - TOL
                       and num(r, 'lp_fcc_k') < num(r, 'opt') - TOL]
    # Testemunha mecanística específica: um ótimo F-CC infringe um corte K.
    mechanism = []
    for w in witnesses:
        if w.get('label') != VERIFIED or 'lp_fcc' not in w:
            continue
        for cut in w.get('violated_K', []):
            if cut['lhs'] < cut['rhs'] - TOL:
                mechanism.append({'instancia': w['instancia'], 'Z': cut['Z'],
                                  'lhs': cut['lhs'], 'rhs': cut['rhs']})
    require(mechanism, 'Sem testemunha de complementaridade K versus F-CC')
    # Nenhuma família de desigualdade projetada com prova/teste foi registrada em N1-T5/T6.
    # A ausência de evidência não permite promover essa categoria.
    projected_qualifies = False
    fcc_qualifies = len(fcc_families) >= 2 and bool(mechanism)
    trio_qualifies = len(trio_families) >= 2 and bool(trio_nontrivial)
    candidates = [x for x, yes in (
        ('PROMOTE PROJECTED COMPATIBILITY INEQUALITY', projected_qualifies),
        (DECISION, fcc_qualifies),
        ('PROMOTE FCC + C3', trio_qualifies),
    ) if yes]
    # Neste conjunto não há empate: não inventar operacionalização de um tie-break não acionado.
    require(len(candidates) <= 1, 'Mais de uma categoria qualificada: aplicar o desempate formal da spec')
    final = candidates[0] if candidates else 'NO INCREMENTAL TARGET FOUND'
    return {'decision': final, 'fcc_cases': [(r['instancia'], r['tipo'], round(num(r, 'delta_fcc_k'), 9)) for r in fcc_eligible],
            'fcc_families': fcc_families,
            'trio_cases': [(phase, r['instancia'] if phase == 'T5' else r['name']) for phase, r in trio_rows],
            'trio_families': trio_families, 'trio_nontrivial_cases': trio_nontrivial,
            'mechanism': mechanism, 'candidates': candidates}


def main() -> None:
    check_chain()
    t5 = load_csv(R / 'n1-t5-diagnostico.csv', 18)
    t6 = load_csv(R / 'n1-t6-diagnostico.csv', 6)
    require(len({r['instancia'] for r in t5}) == 18, 'Instância T5 duplicada')
    require(len({r['name'] for r in t6}) == 6, 'Variante T6 duplicada')
    require(len({r['pair_id'] for r in t6}) == 3, 'T6 sem três pares')
    for r in t5:
        check_row(r, phase='T5')
    for r in t6:
        check_row(r, phase='T6')
    t3 = load_csv(R / 'n1-t3-validacao.csv', 9)
    require(sum(int(row['n_instalacoes']) for row in t3) == 878, 'N1-T3: total de instalações diverge de 878')
    for row in t3:
        for key in ('viavel_sim_fc3_nao', 'viavel_nao_fc3_sim', 'viavel_sim_fcck_nao',
                    'viavel_nao_fcck_sim', 'viavel_sim_fc3k_nao', 'viavel_nao_fc3k_sim'):
            require(int(row[key]) == 0, f'N1-T3: discordância em {row["instancia"]} / {key}')
    reproduction = json.loads((R / 'n1-t5-reproducao.json').read_text(encoding='utf-8'))
    require(reproduction['state'] == VERIFIED and reproduction['rows'] == 16, 'Reprodução F3 não validada')
    require(reproduction['f3_historical_sha256'] == reproduction['f3_reproduced_sha256'],
            'F3 histórico não reproduzido')
    mr = (ROOT / 'docs/technical/reference/formulacoes/revisao-mr-f3-n1.md').read_text(encoding='utf-8')
    require('ACCEPTED' in mr, 'MR-F3 não aceito')
    witnesses = json.loads((R / 'n1-t5-testemunhas.json').read_text(encoding='utf-8'))['rows']
    result = evaluate(t5, t6, witnesses)
    require(RECORD.is_file(), 'Registro N1-T7 ausente')
    require(f'**Decisão:** `{result["decision"]}`' in RECORD.read_text(encoding='utf-8'),
            'Registro de decisão difere do gate recalculado')
    print('PASS: N1-T5 = 18; N1-T6 = 6; cadeia de hashes íntegra; MR-F3 aceito')
    print('F-CC+K: famílias com Γ>0 e Δ_FCC+K>0:', ', '.join(result['fcc_families']))
    for name, fam, delta in result['fcc_cases']:
        print(f'  {name} ({fam}): Δ_FCC+K={delta:g}')
    print('F-C3+K: ganhos estritos:', ', '.join(f'{phase}:{name}' for phase, name in result['trio_cases']))
    print('F-C3+K: famílias distintas:', ', '.join(result['trio_families']))
    print('F-C3+K: casos elegíveis com core IP < OPT:', result['trio_nontrivial_cases'])
    print('Testemunhas K versus F-CC:', ', '.join(w['instancia'] for w in result['mechanism']))
    print('Desempate:', 'não acionado' if len(result['candidates']) < 2 else 'necessário')
    print('DECISÃO N1-T7:', result['decision'])
    print('N2: caminho B — F-CC + K (apenas raiz; implementação ainda não iniciada)')


if __name__ == '__main__':
    main()
