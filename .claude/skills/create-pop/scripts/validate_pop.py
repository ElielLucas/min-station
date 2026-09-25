#!/usr/bin/env python3
"""
Validação estrutural de um arquivo POP (.md) gerado pelo fluxo create-pop (v2.0).
Alinhado ao template canônico v3 da skill create-pop.

Uso:
    python scripts/validate_pop.py /caminho/para/pop.md
    python scripts/validate_pop.py /caminho/para/pop.md --json

Códigos de saída:
    0 = sem erros (avisos permitidos)
    1 = pelo menos um erro

Não substitui revisão humana; captura placeholders óbvios e seções obrigatórias ausentes.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


REQUIRED_MARKERS = [
    ("heading_intro", r"(?im)^##\s+Introdução\s*$"),
    ("heading_what_pop", r"(?im)^##\s+O que é um POP\??\s*$"),
    ("heading_not_pop", r"(?im)^##\s+O que NÃO é um POP\s*$"),
    ("section_identification", r"(?im)^#\s+1\.\s+Identificação"),
    ("section_purpose", r"(?im)^#\s+2\.\s+Propósito"),
    ("section_steps_or_procedure", r"(?im)^#\s+(5|7)\.\s+(Passo a passo|Procedimento operacional executável).*$"),
    ("section_results_or_summary", r"(?im)^#\s+(7|8)\.\s+(Resultados esperados|Resumo).*$"),
]

# Linhas que são só ">" após um título são comuns no modelo — flag apenas se houver MUITAS no corpo principal.
WARN_IF_MANY_EMPTY_GT = 8
VAGUE_VERBS = ("analisar", "validar", "alinhar")
CRITERIA_HINTS = ("critério", "evidência", "métrica", "aprov", "log", "checklist", "resultado")


def validate_pop(md_path: Path) -> dict:
    text = md_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    results: dict = {"path": str(md_path), "errors": [], "warnings": []}

    strict_required = {"heading_intro", "heading_what_pop", "heading_not_pop", "section_identification", "section_purpose"}
    for key, pattern in REQUIRED_MARKERS:
        if not re.search(pattern, text, re.MULTILINE):
            msg = f"Marcador obrigatório ausente ou formato divergente: {key} ({pattern})"
            if key in strict_required:
                results["errors"].append(msg)
            else:
                results["warnings"].append(msg)

    if "xx/xx/xxxx" in text:
        results["errors"].append("Ainda contém placeholder de data xx/xx/xxxx")

    # Versão e status esperados para emissão padrão
    if not re.search(r"(?i)\*\*Versão\*\*\s*\|\s*1\.0", text) and not re.search(r"(?i)\*\*Versão\*\*.*1\.0", text):
        results["warnings"].append("Não encontrou claramente Versão 1.0 na tabela de identificação")

    if not re.search(r"(?i)Ativo", text):
        results["warnings"].append("Não encontrou menção a status Ativo")

    placeholder_patterns = [
        r"\[NOME COMPLETO\]",
        r"\[TÍTULO DO POP\]",
        r"\[DD/MM/AAAA\]",
        r"\[Papel[^\]]*\]",
        r"\[Atividade[^\]]*\]",
        r"\bTBD\b",
        r"\ba definir\b",
        r"\bFulano\b",
    ]
    for p in placeholder_patterns:
        if re.search(p, text, re.IGNORECASE):
            results["warnings"].append(f"Placeholder detectado: padrão `{p}`")

    empty_gt = sum(1 for line in lines if line.strip() == ">")
    if empty_gt >= WARN_IF_MANY_EMPTY_GT:
        results["warnings"].append(
            f"Muitas linhas só com '>' ({empty_gt}); verifique se Passo a passo e Resultados foram preenchidos"
        )

    # Placeholder de título óbvio
    if re.search(r"(?i)POP de \[SUBSTITUIR", text) or "POP de [TÍTULO DO POP]" in text:
        results["errors"].append("Título do POP ainda está como placeholder")

    # Estrutura mínima de etapa
    if not re.search(r"(?im)^###\s+Etapa\s+\d+\s+—", text):
        results["warnings"].append("Não encontrou nenhuma seção no formato `### Etapa N — ...`")

    # Verifica por etapa se existem saída e validação próximas
    stage_matches = list(re.finditer(r"(?im)^###\s+Etapa\s+\d+\s+—.*$", text))
    for idx, stage in enumerate(stage_matches):
        start = stage.start()
        end = stage_matches[idx + 1].start() if idx + 1 < len(stage_matches) else len(text)
        chunk = text[start:end]
        stage_name = stage.group(0).strip()
        if "**Validação objetiva:**" not in chunk:
            results["warnings"].append(f"{stage_name}: sem `**Validação objetiva:**`")
        if "**Saída esperada:**" not in chunk:
            results["warnings"].append(f"{stage_name}: sem `**Saída esperada:**`")

    # Verbos vagos no início de bullet sem critério nas próximas linhas
    for i, line in enumerate(lines):
        striped = line.strip().lower()
        if not striped.startswith("- "):
            continue
        content = striped[2:].strip()
        if any(content.startswith(v) for v in VAGUE_VERBS):
            neighborhood = " ".join(lines[i : i + 3]).lower()
            if not any(h in neighborhood for h in CRITERIA_HINTS):
                results["warnings"].append(
                    f"Linha {i + 1}: verbo potencialmente vago sem critério próximo (`{line.strip()}`)"
                )

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Valida estrutura mínima de um arquivo POP (.md)")
    parser.add_argument("path", type=Path, help="Caminho para o arquivo .md")
    parser.add_argument("--json", action="store_true", help="Saída em JSON")
    args = parser.parse_args()

    if not args.path.is_file():
        print(json.dumps({"errors": [f"Arquivo não encontrado: {args.path}"]})) if args.json else print(
            f"Erro: arquivo não encontrado: {args.path}", file=sys.stderr
        )
        return 1

    r = validate_pop(args.path)
    ok = len(r["errors"]) == 0

    if args.json:
        r["ok"] = ok
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        print(f"Arquivo: {r['path']}")
        for e in r["errors"]:
            print(f"  ERRO: {e}")
        for w in r["warnings"]:
            print(f"  AVISO: {w}")
        if ok and not r["warnings"]:
            print("Validação estrutural: OK")
        elif ok:
            print("Validação estrutural: OK com avisos")
        else:
            print("Validação estrutural: FALHOU")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
