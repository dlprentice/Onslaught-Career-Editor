#!/usr/bin/env python3
"""Validate Wave984 BattleEngine WalkerPart dash-gate read-only review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave984-battleengine-walker-dash-gate-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_battleengine_walker_dash_gate_review_wave984_2026-05-31.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
BATTLEENGINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "BattleEngine.cpp" / "_index.md"
WALKER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "BattleEngineWalkerPart.cpp" / "_index.md"
SOURCE_GAP_PROBE = ROOT / "tools" / "battleengine_source_binary_gap_probe.py"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260531-005829_post_wave984_battleengine_walker_dash_gate_review_verified"

TARGETS = {
    "0x0040a580": ("CBattleEngine__Morph", "void __fastcall CBattleEngine__Morph(void * battleEngine)"),
    "0x00412d80": ("CBattleEngineWalkerPart__Forward", "void __thiscall CBattleEngineWalkerPart__Forward(void * this, float moveY)"),
    "0x00412f70": ("CBattleEngineWalkerPart__Backward", "void __thiscall CBattleEngineWalkerPart__Backward(void * this, float moveY)"),
    "0x00413160": ("CBattleEngineWalkerPart__StrafeLeft", "void __thiscall CBattleEngineWalkerPart__StrafeLeft(void * this, float moveX)"),
    "0x00413360": ("CBattleEngineWalkerPart__StrafeRight", "void __thiscall CBattleEngineWalkerPart__StrafeRight(void * this, float moveX)"),
    "0x004135d0": ("CBattleEngineWalkerPart__GetIsDoingSpecialWalkerMove", "int __thiscall CBattleEngineWalkerPart__GetIsDoingSpecialWalkerMove(void * this)"),
    "0x004135e0": ("CBattleEngineWalkerPart__ActivateLandingJets", "void __thiscall CBattleEngineWalkerPart__ActivateLandingJets(void * this)"),
    "0x00413760": ("CBattleEngineWalkerPart__Move", "void __thiscall CBattleEngineWalkerPart__Move(void * this)"),
}

LOG_TOKENS = {
    "ExportFunctionMetadataByAddress.log": ("targets=8 found=8 missing=0",),
    "ExportFunctionTagsByAddress.log": ("ExportFunctionTagsByAddress complete: rows=8 missing=0",),
    "ExportXrefsForAddresses.log": ("Wrote 14 rows",),
    "ExportFunctionBodyInstructionsByAddress.log": ("Wrote 1084 function-body instruction rows", "targets=8 missing=0"),
    "ExportFunctionsByAddressDecompile.log": ("targets=8 dumped=8 missing=0 failed=0",),
}

DECOMPILE_TOKENS = {
    "0040a580_CBattleEngine__Morph.c": (
        "CBattleEngineJetPart__IsStateMachineActive",
        "CBattleEngineWalkerPart__GetIsDoingSpecialWalkerMove",
        "s_flytowalk_006234bc",
        "s_walktofly_006234b0",
        "CEventManager__AddEvent_AtTime",
    ),
    "004135d0_CBattleEngineWalkerPart__GetIsDoingSpecialWalkerMove.c": (
        "return (uint)(0 < *(int *)((int)this + 0x44));",
    ),
    "004135e0_CBattleEngineWalkerPart__ActivateLandingJets.c": (
        "CBattleEngineWalkerPart__ActivateLandingJets",
    ),
    "00413760_CBattleEngineWalkerPart__Move.c": (
        "CBattleEngineWalkerPart__Move",
    ),
}

DOC_TOKENS = (
    "Wave984",
    "battleengine-walker-dash-gate-review-wave984",
    "0x0040a580 CBattleEngine__Morph",
    "0x004135d0 CBattleEngineWalkerPart__GetIsDoingSpecialWalkerMove",
    "transform_reject_special_moves",
    "392/1408 = 27.84%",
    "451/1478 = 30.51%",
    "6222/6222 = 100.00%",
    BACKUP_PATH,
)

OVERCLAIMS = (
    "runtime dash behavior proven",
    "runtime transform rejection proven",
    "rebuild parity proven",
    "exact cbattleenginewalkerpart structure layout proven",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig", errors="replace").replace("\x00", "")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def row_by_address(rows: list[dict[str, str]], address: str, field: str = "address") -> dict[str, str] | None:
    target = normalize_address(address)
    for row in rows:
        if normalize_address(row.get(field, "")) == target:
            return row
    return None


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_path_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def check_exports(failures: list[str]) -> None:
    expected_counts = {
        "metadata.tsv": 8,
        "tags.tsv": 8,
        "xrefs.tsv": 14,
        "instructions.tsv": 1084,
        "decompile/index.tsv": 8,
    }
    for relative, expected in expected_counts.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == expected, f"{relative} row count {actual} != {expected}", failures)

    metadata = read_tsv(BASE / "metadata.tsv")
    tags = read_tsv(BASE / "tags.tsv")
    decompile_index = read_tsv(BASE / "decompile" / "index.tsv")
    for address, (name, signature) in TARGETS.items():
        row = row_by_address(metadata, address)
        require(row is not None, f"metadata missing {address}", failures)
        if row:
            require(row.get("name") == name, f"metadata name mismatch {address}: {row.get('name')}", failures)
            require(row.get("signature") == signature, f"metadata signature mismatch {address}", failures)
            require("Runtime" in row.get("comment", "") or "runtime" in row.get("comment", ""), f"metadata boundary missing runtime caveat {address}", failures)
            require("CGeneralVolume__IsDashLockoutActive" not in row.get("comment", ""), f"stale GeneralVolume predicate in metadata {address}", failures)

        tag_row = row_by_address(tags, address)
        require(tag_row is not None and tag_row.get("status") == "OK", f"tag row missing/status mismatch {address}", failures)

        dec = row_by_address(decompile_index, address)
        require(dec is not None, f"decompile index missing {address}", failures)
        if dec:
            require(dec.get("name") == name, f"decompile name mismatch {address}", failures)
            require(dec.get("signature") == signature, f"decompile signature mismatch {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch {address}", failures)

    xrefs = read_tsv(BASE / "xrefs.tsv")
    require(
        any(
            normalize_address(row.get("target_addr", "")) == "0x004135d0"
            and normalize_address(row.get("from_function_addr", "")) == "0x0040a580"
            and row.get("from_function") == "CBattleEngine__Morph"
            for row in xrefs
        ),
        "missing Morph xref to WalkerPart special-move predicate",
        failures,
    )


def check_logs(failures: list[str]) -> None:
    bad_tokens = ("LockException", "ERROR REPORT SCRIPT ERROR", "MISSING:", "BADNAME:", "BADSIG:", "missing=1", "bad=1", "failed=1")
    for relative, tokens in LOG_TOKENS.items():
        text = read_text(BASE / relative)
        for token in tokens:
            require(token in text, f"{relative} missing token: {token}", failures)
        for bad in bad_tokens:
            require(bad not in text, f"{relative} contains bad token: {bad}", failures)


def check_decompile_backup_docs(failures: list[str]) -> None:
    for filename, tokens in DECOMPILE_TOKENS.items():
        text = read_text(BASE / "decompile" / filename)
        for token in tokens:
            require(token in text, f"{filename} missing token: {token}", failures)
        require("CGeneralVolume__IsDashLockoutActive" not in text, f"{filename} still contains stale GeneralVolume predicate", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes", 0)) == 173837191, "backup byte count mismatch", failures)
    for key in ("missingCount", "extraCount", "diffCount", "hashDiffCount"):
        require(backup.get(key) == 0, f"backup {key} mismatch", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:ghidra-battleengine-walker-dash-gate-review-wave984")
        == r"py -3 tools\ghidra_battleengine_walker_dash_gate_review_wave984_probe.py --check",
        "package script mismatch",
        failures,
    )

    docs = [
        NOTE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        BATTLEENGINE_DOC,
        WALKER_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_path_token(text, token), f"{path.relative_to(ROOT)} missing token: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lower, f"{path.relative_to(ROOT)} contains overclaim token: {bad}", failures)

    source_gap_text = read_text(SOURCE_GAP_PROBE)
    for token in (
        "release/readiness/ghidra_battleengine_walker_dash_gate_review_wave984_2026-05-31.md",
        "`CBattleEngine__Morph`",
        "`CBattleEngineWalkerPart__GetIsDoingSpecialWalkerMove`",
        "`transform_reject_special_moves`",
    ):
        require(token in source_gap_text, f"source gap probe missing token: {token}", failures)

    ghidra_text = read_text(GHIDRA_REFERENCE)
    require("CGeneralVolume__IsDashLockoutActive | Returns whether dash lockout" not in ghidra_text, "GHIDRA reference still has stale active predicate table row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    failures: list[str] = []
    check_exports(failures)
    check_logs(failures)
    check_decompile_backup_docs(failures)

    if failures:
        print("Wave984 BattleEngine Walker dash-gate review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1 if args.check else 0

    print("Wave984 BattleEngine Walker dash-gate review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
