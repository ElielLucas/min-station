"""AS18: auditoria conservadora do gate de transição a partir da campanha AS16.

Não implementa, separa ou autoriza cortes HL. Não altera artefatos AS16.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

ARMS = ("U", "U_K", "U_H2", "U_K_H2", "U_FIXED_H2", "U_K_FIXED_H2")


class InvalidEvidence(ValueError):
    """Evidência inconsistente ou incompleta: nenhuma autorização pode ser derivada."""


def _load(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise InvalidEvidence(f"Não foi possível ler {path.name}: {exc}") from exc


def evaluate(as16_dir: Path) -> dict:
    """Deriva decisão conservadora com base em linhas LP, sem imputar censuras."""
    manifest = _load(as16_dir / "manifest.json")
    rows = _load(as16_dir / "rows.json")
    analysis = _load(as16_dir / "analysis.json")
    if not isinstance(manifest, dict) or not isinstance(analysis, dict) or not isinstance(rows, list):
        raise InvalidEvidence("Estrutura JSON inválida")
    if (manifest.get("stage"), analysis.get("stage")) != ("AS16", "AS16"):
        raise InvalidEvidence("Etapa incompatível")
    cases = manifest.get("cases")
    if not isinstance(cases, list) or not cases or len(cases) != len(set(cases)):
        raise InvalidEvidence("Casos ausentes ou repetidos no manifesto")
    if manifest.get("arms") != list(ARMS[:4]) or manifest.get("post_hoc_same_pool_arms") != list(ARMS[4:]):
        raise InvalidEvidence("Braços divergentes do pré-registro AS16")
    if len(rows) != len(cases) * len(ARMS) or len(rows) != analysis.get("arm_rows"):
        raise InvalidEvidence("Número de registros incompatível com manifesto/análise")
    if analysis.get("gate") not in ("GO", "STOP", "INVESTIGATE"):
        raise InvalidEvidence("Gate automático não reconhecido")
    rules = analysis.get("gate_rules")
    if not isinstance(rules, dict):
        raise InvalidEvidence("Regras de gate ausentes")
    min_graphs = rules.get("minimum_independent_raw_graphs")
    threshold = rules.get("minimum_relative_gain")
    if type(min_graphs) is not int or min_graphs < 1 or not isinstance(threshold, (float, int)) or not math.isfinite(threshold) or threshold <= 0:
        raise InvalidEvidence("Limiar de gate inválido")

    by_case: dict[str, dict] = {name: {} for name in cases}
    origins = {}
    for r in rows:
        if not isinstance(r, dict):
            raise InvalidEvidence("Registro de braço inválido")
        case, arm = r.get("name"), r.get("arm_id")
        if case not in by_case or arm not in ARMS or arm in by_case[case]:
            raise InvalidEvidence("Caso/braço desconhecido ou repetido")
        if not r.get("raw_graph_id") or not r.get("instance_sha256"):
            raise InvalidEvidence("Identidade do grafo/instância ausente")
        identity = (r["raw_graph_id"], r["instance_sha256"])
        if case in origins and origins[case] != identity:
            raise InvalidEvidence("Identidade de grafo incompatível entre braços")
        origins[case] = identity
        by_case[case][arm] = r
    if len({i[0] for i in origins.values()}) != len(cases):
        raise InvalidEvidence("Os casos não representam grafos brutos independentes")

    # Auditoria cruzada: não permitir que status de um braço seja alterado sem
    # atualizar o registro de censuras, nem que UNKNOWN seja tomado como ótimo.
    def censored(arms):
        return sorted([case, arm, by_case[case][arm].get("status")]
                      for case in cases for arm in arms
                      if by_case[case][arm].get("status") != "OPTIMAL")
    if censored(ARMS[:4]) != sorted(analysis.get("censored_online", [])):
        raise InvalidEvidence("Censuras online divergentes da análise")
    if censored(ARMS[4:]) != sorted(analysis.get("censored_fixed", [])):
        raise InvalidEvidence("Censuras same-pool divergentes da análise")
    if bool(analysis.get("complete_online_optima")) != (not censored(ARMS[:4])):
        raise InvalidEvidence("Flag de completude online inconsistente")
    if bool(analysis.get("all_same_pool_controls_complete")) != (not censored(ARMS[4:])):
        raise InvalidEvidence("Flag de completude same-pool inconsistente")

    reported = analysis.get("comparisons")
    if not isinstance(reported, list) or len(reported) != len(cases) or {c.get("name") for c in reported if isinstance(c, dict)} != set(cases):
        raise InvalidEvidence("Comparações ausentes, repetidas ou inconsistentes")
    reported_by_case = {c["name"]: c for c in reported}
    comparable = 0
    gains = 0
    censored = []
    case_results = []
    for case in cases:
        arm_k, arm_h2 = by_case[case]["U_K"], by_case[case]["U_K_H2"]
        if arm_k.get("status") == "OPTIMAL" and arm_h2.get("status") == "OPTIMAL":
            k, h2 = arm_k.get("lp_objective"), arm_h2.get("lp_objective")
            if not isinstance(k, (int, float)) or not isinstance(h2, (int, float)) or not math.isfinite(k) or not math.isfinite(h2) or k <= 0:
                raise InvalidEvidence("Objetivo LP ótimo ausente, não finito ou inválido")
            gain = (h2 - k) / k
            claimed = reported_by_case[case].get("U_K_to_U_K_H2", {}).get("relative_gain")
            if not isinstance(claimed, (int, float)) or not math.isfinite(claimed) or not math.isclose(gain, claimed, rel_tol=1e-6, abs_tol=1e-7):
                raise InvalidEvidence("Ganho declarado difere dos objetivos LP registrados")
            comparable += 1
            if gain >= threshold - 1e-10:
                gains += 1
            case_results.append({"name": case, "status": "COMPARABLE", "relative_gain": gain})
        else:
            censored.append(case)
            case_results.append({"name": case, "status": "NOT_COMPARABLE", "relative_gain": None,
                                 "arm_statuses": {"U_K": arm_k.get("status"), "U_K_H2": arm_h2.get("status")}})
    if gains != analysis.get("independent_raw_graphs_with_gain"):
        raise InvalidEvidence("Contagem declarada de ganhos diverge dos LPs")
    max_possible = gains + len(censored)
    research_decision = "STOP" if max_possible < min_graphs else "UNRESOLVED"
    # A hipótese independente de HL exigida por AS18 não está documentada na campanha AS16.
    # Não deduzimos que H2 seja dominado nem autorizamos HL por padrão.
    hl_gate = "NOT_AUTHORIZED" if research_decision == "STOP" else "REVIEW_REQUIRED"
    return {
        "schema_version": "AS18-GATE-v1", "stage": "AS18",
        "source_dir": as16_dir.as_posix(), "as16_source_commit": manifest.get("source_commit"),
        "as16_plan_sha256": manifest.get("plan_sha256"), "as16_automatic_gate": analysis["gate"],
        "as16_research_decision": research_decision, "as17_mip_gate": "NOT_AUTHORIZED" if analysis["gate"] != "GO" else "REVIEW_REQUIRED",
        "as18_hl_gate": hl_gate, "independent_structural_witness": "NOT_PROVIDED",
        "requirement": {"min_independent_graphs_with_gain": min_graphs, "min_relative_gain": threshold},
        "comparison": {"total_graphs": len(cases), "comparable_graphs": comparable,
                       "observed_graphs_with_gain": gains, "censored_graphs": len(censored),
                       "maximum_possible_graphs_with_gain": max_possible},
        "cases": case_results,
        "interpretation": "Gate automático preservado; STOP é priorização científica, não prova de dominância ou MIP.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--as16-dir", type=Path, default=Path("results/benchmark/as16-lp-h2-001"))
    parser.add_argument("--output", type=Path, help="Escreve JSON de evidência novo (não sobrescreve)")
    args = parser.parse_args()
    result = evaluate(args.as16_dir)
    encoded = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as f:
            f.write(encoded)
    else:
        print(encoded, end="")


if __name__ == "__main__":
    main()
