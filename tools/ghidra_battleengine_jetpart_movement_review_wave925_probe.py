#!/usr/bin/env python3
"""Validate Wave925 BattleEngine/JetPart movement read-only review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave925-battleengine-jetpart-movement-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_battleengine_jetpart_movement_review_wave925_2026-05-27.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BATTLEENGINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "BattleEngine.cpp" / "_index.md"
JETPART_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "BattleEngineJetPart.cpp" / "_index.md"
PACKAGE_JSON = ROOT / "package.json"
STATE_FILES = [
    ROOT / "developer_agent_state.json",
    ROOT / "documentation_agent_state.json",
    ROOT / "re_orchestrator_state.json",
]

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260527-223000_post_wave925_battleengine_jetpart_movement_review_verified"
SCRIPT_NAME = "test:ghidra-battleengine-jetpart-movement-review-wave925"
SCRIPT_VALUE = r"py -3 tools\ghidra_battleengine_jetpart_movement_review_wave925_probe.py --check"

TARGETS = {
    "0x00409e80": ("CBattleEngine__AutoZoomOut", "void __thiscall CBattleEngine__AutoZoomOut(void * this)"),
    "0x00410310": ("CBattleEngineJetPart__Thrust", "void __thiscall CBattleEngineJetPart__Thrust(void * this, float moveY)"),
    "0x00410490": ("CBattleEngineJetPart__Turn", "void __thiscall CBattleEngineJetPart__Turn(void * this, float moveX)"),
    "0x00410670": ("CBattleEngineJetPart__Pitch", "void __thiscall CBattleEngineJetPart__Pitch(void * this, float moveY)"),
    "0x00410740": ("CBattleEngineJetPart__YawLeft", "void __thiscall CBattleEngineJetPart__YawLeft(void * this, float moveX)"),
    "0x004109d0": ("CBattleEngineJetPart__YawRight", "void __thiscall CBattleEngineJetPart__YawRight(void * this, float moveX)"),
    "0x00411b70": ("CBattleEngineJetPart__IsStateMachineActive", "int __thiscall CBattleEngineJetPart__IsStateMachineActive(void * this)"),
}

EXPECTED_XREFS = {
    "0x00409e80": {("0x00411fe5", "CBattleEngineJetPart__ChangeWeapon", "UNCONDITIONAL_CALL"), ("0x00413ff9", "CBattleEngineWalkerPart__ChangeWeapon", "UNCONDITIONAL_CALL")},
    "0x00410310": {("0x004d3415", "<no_function>", "UNCONDITIONAL_CALL"), ("0x004d342a", "<no_function>", "UNCONDITIONAL_CALL")},
    "0x00410490": {("0x004d33c1", "<no_function>", "UNCONDITIONAL_CALL")},
    "0x00410670": {("0x004d33d6", "<no_function>", "UNCONDITIONAL_CALL")},
    "0x00410740": {("0x004d33eb", "<no_function>", "UNCONDITIONAL_CALL")},
    "0x004109d0": {("0x004d3400", "<no_function>", "UNCONDITIONAL_CALL")},
    "0x00411b70": {("0x0040a5bf", "CBattleEngine__Morph", "UNCONDITIONAL_CALL")},
}

CORE_TOKENS = (
    "Wave925",
    "battleengine-jetpart-movement-review-wave925",
    "96/1408 = 6.82%",
    "6113/6113 = 100.00%",
    BACKUP,
    "0x00409e80",
    "0x00410310",
    "0x00411b70",
)

OVERCLAIMS = (
    "runtime jet input behavior proven",
    "runtime zoom behavior proven",
    "runtime morph behavior proven",
    "fully reverse-engineered",
    "rebuild parity proven",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8-sig", errors="replace")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def normalized(addr: str) -> str:
    value = (addr or "").lower().strip()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def row_by_addr(rows: list[dict[str, str]], addr: str) -> dict[str, str]:
    want = normalized(addr)
    for row in rows:
        got = row.get("address") or row.get("target_addr") or row.get("function_entry") or ""
        if normalized(got) == want:
            return row
    return {}


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def build_report() -> dict[str, object]:
    failures: list[str] = []
    metadata = read_tsv(BASE / "metadata.tsv")
    tags = read_tsv(BASE / "tags.tsv")
    xrefs = read_tsv(BASE / "xrefs.tsv")
    instructions = read_tsv(BASE / "instructions.tsv")
    decomp = read_tsv(BASE / "decompile" / "index.tsv")
    summary = json.loads(read_text(BASE / "wave925-battleengine-jetpart-movement-review.json") or "{}")
    backup = json.loads(read_text(BASE / "backup-summary.json") or "{}")

    require(len(metadata) == 7, "metadata row count mismatch", failures)
    require(len(tags) == 7, "tag row count mismatch", failures)
    require(len(xrefs) == 9, "xref row count mismatch", failures)
    require(len(instructions) == 697, "instruction row count mismatch", failures)
    require(len(decomp) == 7, "decompile row count mismatch", failures)

    for addr, (name, signature) in TARGETS.items():
        mrow = row_by_addr(metadata, addr)
        require(mrow.get("name") == name, f"metadata name mismatch for {addr}", failures)
        require(mrow.get("signature") == signature, f"metadata signature mismatch for {addr}", failures)
        require(mrow.get("status") == "OK", f"metadata status mismatch for {addr}", failures)
        drow = row_by_addr(decomp, addr)
        require(drow.get("name") == name, f"decompile name mismatch for {addr}", failures)
        require(drow.get("signature") == signature, f"decompile signature mismatch for {addr}", failures)
        require(drow.get("status") == "OK", f"decompile status mismatch for {addr}", failures)
        require(row_by_addr(tags, addr).get("status") == "OK", f"tag status mismatch for {addr}", failures)

    actual_xrefs: dict[str, set[tuple[str, str, str]]] = {}
    for row in xrefs:
        target = normalized(row.get("target_addr", ""))
        actual_xrefs.setdefault(target, set()).add((normalized(row.get("from_addr", "")), row.get("from_function", ""), row.get("ref_type", "")))
    for addr, expected in EXPECTED_XREFS.items():
        actual = actual_xrefs.get(normalized(addr), set())
        normalized_expected = {(normalized(from_addr), from_func, ref_type) for from_addr, from_func, ref_type in expected}
        require(normalized_expected.issubset(actual), f"xref mismatch for {addr}: {normalized_expected - actual}", failures)

    for log_name, token in {
        "metadata.log": "targets=7 found=7 missing=0",
        "tags.log": "rows=7 missing=0",
        "xrefs.log": "Wrote 9 rows",
        "instructions.log": "Wrote 697 function-body instruction rows",
        "decompile.log": "targets=7 dumped=7 missing=0 failed=0",
    }.items():
        text = read_text(BASE / log_name)
        require(token in text, f"missing log token in {log_name}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "FAIL:", "missing=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {log_name}: {bad}", failures)

    require(summary.get("selectedTargets") == 7, "summary selected target mismatch", failures)
    require(summary.get("mutatedTargets") == 0, "summary mutation mismatch", failures)
    require(summary.get("focusedReauditProgressAfter") == "96/1408 = 6.82%", "summary progress mismatch", failures)
    require(summary.get("staticExportContractClosure") == "6113/6113 = 100.00%", "summary closure mismatch", failures)
    require(summary.get("instructionRows") == 697, "summary instruction count mismatch", failures)

    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 173247367, "backup byte count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)

    docs = [NOTE, CAMPAIGN, BATTLEENGINE_DOC, JETPART_DOC, *STATE_FILES]
    for path in docs:
        text = read_text(path)
        for token in CORE_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = json.loads(read_text(PACKAGE_JSON) or "{}")
    require(package.get("scripts", {}).get(SCRIPT_NAME) == SCRIPT_VALUE, "package script mismatch", failures)

    return {
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "counts": {
            "metadata": len(metadata),
            "tags": len(tags),
            "xrefs": len(xrefs),
            "instructions": len(instructions),
            "decompile": len(decomp),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()
    report = build_report()
    report_path = BASE / "wave925-probe-report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("Ghidra Wave925 BattleEngine/JetPart movement review probe")
    print(f"Status: {report['status']}")
    print(f"Output: {report_path.relative_to(ROOT)}")
    if report["failures"]:
        for failure in report["failures"]:
            print(f"- {failure}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
