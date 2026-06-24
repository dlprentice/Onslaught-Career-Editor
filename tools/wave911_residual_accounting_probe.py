#!/usr/bin/env python3
"""Validate Wave911 residual static accounting surfaces."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
ACCOUNTING = ROOT / "reverse-engineering" / "binary-analysis" / "wave911-residual-accounting.md"
ACCOUNTING_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave911-residual-accounting.md"
READINESS = ROOT / "release" / "readiness" / "wave911_residual_accounting_wave1106_2026-06-04.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

FOCUSED_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "wave911-risk-rank" / "wave911-focused-correction-candidates.json"
FOCUSED_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "wave911-risk-rank" / "wave911-focused-correction-candidates.tsv"
RISK_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "wave911-risk-rank" / "wave911-risk-ranked-functions.json"
RISK_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "wave911-risk-rank" / "wave911-risk-ranked-functions.tsv"

LATEST_BACKUP = r"G:\GhidraBackups\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified"

EXPECTED = {
    "function_total": 6411,
    "expanded_done": 1560,
    "expanded_total": 1560,
    "wave911_done": 812,
    "wave911_total": 1408,
    "wave911_remaining": 596,
    "top500_done": 500,
    "top500_total": 500,
    "focused_source_total": 6113,
    "focused_json_top": 200,
    "focused_tsv_rows": 300,
    "risk_candidate_functions": 5803,
    "risk_json_top": 250,
    "risk_tsv_rows": 500,
}

CORE_TOKENS = (
    "wave911-residual-accounting-wave1106",
    "6411/6411 = 100.00%",
    "0 / 0 / 0",
    "1560/1560 = 100.00%",
    "812/1408 = 57.67%",
    "500/500 = 100.00%",
    "596",
    "candidateFunctions=1408",
    "top sample count `200`",
    "`300` data rows",
    "candidateFunctions=5803",
    "top sample count `250`",
    "`500` data rows",
    LATEST_BACKUP,
)

STATE_TOKENS = (
    "wave911-residual-accounting-wave1106",
    "wave911-reconstruction-preflight-wave1107",
    "6411/6411 = 100.00%",
    "812/1408 = 57.67%",
    "historical-retired/non-reconstructable",
    "596",
    "300",
    "1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence",
)

OVERCLAIM_TOKENS = (
    "runtime gameplay behavior proven",
    "exact layouts proven",
    "bea patching behavior proven",
    "clean-room rebuild parity proven",
    "full `1408` focused queue materialized",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def count_tsv_rows(path: Path) -> int:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return sum(1 for _ in csv.DictReader(handle, delimiter="\t"))


def ratio(done: int, total: int) -> str:
    return f"{done}/{total} = {(done / total) * 100:.2f}%"


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def check_progress(failures: list[str]) -> None:
    progress = read_json(PROGRESS)
    quality = progress.get("functionQuality", {})
    require(quality.get("totalFunctions") == EXPECTED["function_total"], "function total mismatch", failures)
    require(quality.get("commentedFunctions") == EXPECTED["function_total"], "commented function total mismatch", failures)
    require(quality.get("commentlessFunctions") == 0, "commentless count mismatch", failures)
    require(quality.get("undefinedSignatures") == 0, "undefined signature count mismatch", failures)
    require(quality.get("paramSignatures") == 0, "param_N count mismatch", failures)
    require(quality.get("strictCleanSignatureProxy") == ratio(EXPECTED["function_total"], EXPECTED["function_total"]), "strict clean ratio mismatch", failures)

    reaudit = progress.get("post100Reaudit", {})
    expanded = reaudit.get("expandedStaticSurface", {})
    focused = reaudit.get("wave911Focused", {})
    top500 = reaudit.get("wave911Top500RiskRanked", {})
    require(expanded.get("completed") == EXPECTED["expanded_done"], "expanded done mismatch", failures)
    require(expanded.get("total") == EXPECTED["expanded_total"], "expanded total mismatch", failures)
    require(focused.get("completed") == EXPECTED["wave911_done"], "Wave911 done mismatch", failures)
    require(focused.get("total") == EXPECTED["wave911_total"], "Wave911 total mismatch", failures)
    require(focused.get("percent") == "57.67%", "Wave911 percent mismatch", failures)
    require(focused.get("status") == "historical-retired/non-reconstructable", "Wave911 status mismatch", failures)
    require(focused.get("active") is False, "Wave911 active flag mismatch", failures)
    require(focused.get("residualIdentityUnproven") == EXPECTED["wave911_remaining"], "Wave911 residual mismatch", failures)
    require(focused.get("materializedFocusedRows") == EXPECTED["focused_tsv_rows"], "Wave911 materialized row count mismatch", failures)
    require(top500.get("completed") == EXPECTED["top500_done"], "top500 done mismatch", failures)
    require(top500.get("total") == EXPECTED["top500_total"], "top500 total mismatch", failures)


def check_wave911_artifacts(failures: list[str]) -> None:
    focused = read_json(FOCUSED_JSON)
    risk = read_json(RISK_JSON)
    require(focused.get("schema") == "wave911-focused-correction-candidates.v1", "focused schema mismatch", failures)
    require(focused.get("totalFunctions") == EXPECTED["focused_source_total"], "focused source total mismatch", failures)
    require(focused.get("candidateFunctions") == EXPECTED["wave911_total"], "focused candidate count mismatch", failures)
    require(len(focused.get("top", [])) == EXPECTED["focused_json_top"], "focused JSON top count mismatch", failures)
    require(count_tsv_rows(FOCUSED_TSV) == EXPECTED["focused_tsv_rows"], "focused TSV row count mismatch", failures)

    require(risk.get("schema") == "wave911-risk-ranked-functions.v1", "risk schema mismatch", failures)
    require(risk.get("totalFunctions") == EXPECTED["focused_source_total"], "risk source total mismatch", failures)
    require(risk.get("candidateFunctions") == EXPECTED["risk_candidate_functions"], "risk candidate count mismatch", failures)
    require(len(risk.get("top", [])) == EXPECTED["risk_json_top"], "risk JSON top count mismatch", failures)
    require(count_tsv_rows(RISK_TSV) == EXPECTED["risk_tsv_rows"], "risk TSV row count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    canonical_docs = {
        "wave911-residual-accounting.md": read_text(ACCOUNTING),
        "wave911_residual_accounting_wave1106_2026-06-04.md": read_text(READINESS),
        "mapped-systems.md": read_text(MAPPED_SYSTEMS),
        "static-reaudit-campaign.md": read_text(CAMPAIGN),
        "binary-analysis/_index.md": read_text(BINARY_INDEX),
        "RE-INDEX.md": read_text(RE_INDEX),
    }
    state_docs = {
        "developer_agent_state.json": read_text(DEVELOPER_STATE),
        "documentation_agent_state.json": read_text(DOCUMENTATION_STATE),
        "re_orchestrator_state.json": read_text(RE_STATE),
    }
    for name, text in canonical_docs.items():
        for token in CORE_TOKENS:
            require(contains_token(text, token), f"missing token in {name}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {name}: {bad}", failures)
    for name, text in state_docs.items():
        for token in STATE_TOKENS:
            require(contains_token(text, token), f"missing state token in {name}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {name}: {bad}", failures)

    require(read_text(ACCOUNTING) == read_text(ACCOUNTING_MIRROR), "wave911 accounting mirror mismatch", failures)
    require("no Ghidra export" in canonical_docs["wave911_residual_accounting_wave1106_2026-06-04.md"], "readiness missing no-export boundary", failures)
    require("no Ghidra mutation" in canonical_docs["wave911_residual_accounting_wave1106_2026-06-04.md"], "readiness missing no-mutation boundary", failures)


def check_package(failures: list[str]) -> None:
    package = read_json(PACKAGE_JSON)
    expected = r"py -3 tools\wave911_residual_accounting_probe.py --check"
    require(package.get("scripts", {}).get("test:wave911-residual-accounting") == expected, "missing package script", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_progress(failures)
    check_wave911_artifacts(failures)
    check_docs(failures)
    check_package(failures)

    if failures:
        print("Wave911 residual accounting probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave911 residual accounting probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
