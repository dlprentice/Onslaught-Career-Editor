#!/usr/bin/env python3
"""Validate Wave911 reconstruction preflight surfaces."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
FOCUSED_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "wave911-risk-rank" / "wave911-focused-correction-candidates.json"
FOCUSED_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "wave911-risk-rank" / "wave911-focused-correction-candidates.tsv"
RISK_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "wave911-risk-rank" / "wave911-risk-ranked-functions.json"
RISK_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "wave911-risk-rank" / "wave911-risk-ranked-functions.tsv"

NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave911-reconstruction-preflight.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave911-reconstruction-preflight.md"
READINESS = ROOT / "release" / "readiness" / "wave911_reconstruction_preflight_wave1107_2026-06-04.md"
WAVE911_READINESS = ROOT / "release" / "readiness" / "ghidra_wave911_static_reaudit_risk_rank_2026-05-27.md"
ACCOUNTING = ROOT / "reverse-engineering" / "binary-analysis" / "wave911-residual-accounting.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

LATEST_BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified"

CORE_TOKENS = (
    "wave911-reconstruction-preflight-wave1107",
    "not reconstructable",
    "totalFunctions=6113",
    "6411/6411 = 100.00%",
    "address`, `name`, `signature`, `comment`, and `status",
    "four output files",
    "focused candidates: 1408",
    "afa2c0f0 RE: verify Wave910 queue and seed Wave911 risk rank.",
    "e56f8c89 Merge main: Wave910 queue verification and Wave911 risk rank.",
    "candidateFunctions=1408",
    "top sample count `200`",
    "`300` data rows",
    "candidateFunctions=5803",
    "top sample count `250`",
    "`500` data rows",
    "596",
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
    "exact original wave911 list recovered",
    "full `1408` focused queue materialized",
    "runtime gameplay behavior proven",
    "exact layouts proven",
    "clean-room rebuild parity proven",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def check_artifacts(failures: list[str]) -> None:
    queue_rows = read_tsv(QUEUE_TSV)
    require(len(queue_rows) == 6411, "current queue row count mismatch", failures)
    require(list(queue_rows[0].keys()) == ["address", "name", "signature", "comment", "status"], "current queue header mismatch", failures)

    focused = read_json(FOCUSED_JSON)
    risk = read_json(RISK_JSON)
    require(focused.get("schema") == "wave911-focused-correction-candidates.v1", "focused schema mismatch", failures)
    require(focused.get("totalFunctions") == 6113, "focused totalFunctions mismatch", failures)
    require(focused.get("candidateFunctions") == 1408, "focused candidateFunctions mismatch", failures)
    require(len(focused.get("top", [])) == 200, "focused JSON top count mismatch", failures)
    require(len(read_tsv(FOCUSED_TSV)) == 300, "focused TSV row count mismatch", failures)

    require(risk.get("schema") == "wave911-risk-ranked-functions.v1", "risk schema mismatch", failures)
    require(risk.get("totalFunctions") == 6113, "risk totalFunctions mismatch", failures)
    require(risk.get("candidateFunctions") == 5803, "risk candidateFunctions mismatch", failures)
    require(len(risk.get("top", [])) == 250, "risk JSON top count mismatch", failures)
    require(len(read_tsv(RISK_TSV)) == 500, "risk TSV row count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    canonical_docs = {
        "wave911-reconstruction-preflight.md": read_text(NOTE),
        "wave911_reconstruction_preflight_wave1107_2026-06-04.md": read_text(READINESS),
        "wave911-residual-accounting.md": read_text(ACCOUNTING),
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

    wave911_text = read_text(WAVE911_READINESS)
    require("focused candidates: 1408" in wave911_text, "Wave911 readiness missing focused count", failures)
    require("Heuristic Signals" in wave911_text, "Wave911 readiness missing heuristic section", failures)
    require(read_text(NOTE) == read_text(NOTE_MIRROR), "preflight mirror mismatch", failures)


def check_package(failures: list[str]) -> None:
    package = read_json(PACKAGE_JSON)
    expected = r"py -3 tools\wave911_reconstruction_preflight_probe.py --check"
    require(package.get("scripts", {}).get("test:wave911-reconstruction-preflight") == expected, "missing package script", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_docs(failures)
    check_package(failures)

    if failures:
        print("Wave911 reconstruction preflight probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave911 reconstruction preflight probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
