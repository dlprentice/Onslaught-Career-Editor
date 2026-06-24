#!/usr/bin/env python3
"""Validate Wave901 post-100 static system-review baseline artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave901-post100-static-system-review"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BASELINE_JSON = BASE / "post100-static-system-review-baseline.json"
OWNER_SUMMARY = BASE / "owner-prefix-summary.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_static_system_review_wave901_2026-05-26.md"
REVIEW_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "static-system-review-2026-05-26.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
PACKAGE_JSON = ROOT / "package.json"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260526-092313_post_wave901_static_system_review_verified"
CORE_ANCHORS = (
    "Wave901",
    "post100-static-system-review-wave901",
    "static system review",
    "6113/6113 = 100.00%",
    "0 commentless",
    "0 exact-undefined signatures",
    "0 param_N",
    "CDXTexture",
    "CFastVB",
    "MissionScript/IScript",
    "Unit/BattleEngine",
    BACKUP_PATH,
)
OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "patch behavior proven",
    "rebuild parity proven",
    "all systems complete",
    "every system is complete",
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


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def check_queue(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6113, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    for name, rows in queue["priorityQueues"].items():
        require(rows == [], f"priority queue not empty: {name}", failures)

    rows = read_tsv(QUEUE_TSV)
    require(len(rows) == 6113, "quality TSV row count mismatch", failures)
    require(all(row.get("comment", "").strip() for row in rows), "quality TSV has commentless row", failures)
    require(not any(row.get("signature", "").startswith("undefined ") for row in rows), "quality TSV has undefined signature", failures)
    require(
        not any(re.search(r"\bparam_\d+\b", row.get("signature", "")) for row in rows),
        "quality TSV has param_N signature",
        failures,
    )


def check_baseline(failures: list[str]) -> None:
    baseline = read_json(BASELINE_JSON)
    require(baseline.get("wave") == "Wave901 post-100 static system review baseline", "baseline wave mismatch", failures)
    require(baseline.get("queueTotal") == 6113, "baseline total mismatch", failures)
    require(baseline.get("commentless") == 0, "baseline commentless mismatch", failures)
    require(baseline.get("undefinedSignatures") == 0, "baseline undefined mismatch", failures)
    require(baseline.get("paramSignatures") == 0, "baseline param mismatch", failures)
    require(baseline.get("strictProxy") == "6113/6113 = 100.00%", "baseline strict proxy mismatch", failures)

    owners = {row["Owner"]: row for row in read_tsv(OWNER_SUMMARY)}
    expected = {
        "CDXTexture": "366",
        "CFastVB": "347",
        "CRT": "341",
        "CTexture": "233",
        "CUnit": "90",
        "IScript": "49",
        "CBattleEngine": "47",
    }
    for owner, count in expected.items():
        require(owner in owners, f"missing owner summary row: {owner}", failures)
        if owner in owners:
            require(owners[owner].get("Functions") == count, f"owner count mismatch for {owner}", failures)
            require(owners[owner].get("Commented") == count, f"owner commented mismatch for {owner}", failures)
            require(owners[owner].get("CleanSignatures") == count, f"owner clean-signature mismatch for {owner}", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes", 0)) == 173247367, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = (
        PUBLIC_NOTE,
        REVIEW_DOC,
        MAPPED_SYSTEMS,
        FUNCTION_COVERAGE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        RE_INDEX,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    )
    for path in docs:
        text = read_text(path)
        for token in CORE_ANCHORS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:ghidra-static-system-review-wave901")
        == r"py -3 tools\ghidra_static_system_review_wave901_probe.py --check",
        "missing package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_queue(failures)
    check_baseline(failures)
    check_docs(failures)

    if failures:
        print("Wave901 static system-review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave901 static system-review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
