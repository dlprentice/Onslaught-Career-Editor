#!/usr/bin/env python3
"""Validate Wave952 GameInterface menu-control boundary read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave952-game-interface-menu-execution-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_game_interface_menu_control_boundary_wave952_2026-05-28.md"
PACKAGE_JSON = ROOT / "package.json"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
FRONTEND_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FrontEnd.cpp" / "_index.md"
GAME_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "game.cpp" / "_index.md"
CONTROLLER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Controller.cpp" / "_index.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260528-091135_post_wave952_game_interface_menu_control_boundary_verified"
TARGET = "0x00472d50"
TARGET_NAME = "CGameInterface__VFunc_03_HandleMenuControlInput"
TARGET_SIGNATURE = (
    "void __thiscall CGameInterface__VFunc_03_HandleMenuControlInput("
    "void * this, void * control_context, int button_id, int button_context)"
)

COMMON_TAGS = {
    "static-reaudit",
    "game-interface-menu-control-boundary-wave952",
    "wave952-readback-verified",
    "retail-binary-evidence",
    "function-boundary-recovered",
    "signature-hardened",
    "comment-hardened",
    "game-interface",
    "pause-menu",
    "vtable-slot-3",
    "menu-control-input",
    "button-dispatch",
    "ret0c",
}

COMMENT_TOKENS = (
    "Wave952 GameInterface menu-control boundary recovery",
    "CGameInterface vtable 0x005dbc2c slot 3",
    "pre-metadata had no function",
    "button/control IDs 0x2a..0x39",
    "CGameInterface__AdvanceMenuSelectionWithWrap",
    "CGameInterface__HandleMenuSelection(control_context)",
    "CController__RelinquishControl(control_context)",
    "CGame__UnPause(&DAT_008a9a98)",
    "RET 0x0c",
    "runtime pause/menu/input behavior",
)

DECOMPILE_TOKENS = (
    "switch(button_id)",
    "case 0x2a",
    "case 0x2b",
    "case 0x33",
    "case 0x39",
    "CFrontEnd__PlaySound(0)",
    "CGameInterface__AdvanceMenuSelectionWithWrap(this)",
    "CGameInterface__HandleMenuSelection(this,control_context)",
    "DAT_00679fbc",
    "CGame__UnPause(&DAT_008a9a98)",
)

CORE_TOKENS = (
    "Wave952",
    "game-interface-menu-control-boundary-wave952",
    "0x00472d50 CGameInterface__VFunc_03_HandleMenuControlInput",
    "0x005dbc2c slot 3",
    "button/control IDs 0x2a..0x39",
    "CController__RelinquishControl",
    "CGame__UnPause",
    "276/1408 = 19.60%",
    "6151/6151 = 100.00%",
    BACKUP_PATH,
)

OVERCLAIMS = (
    "runtime pause/menu/input behavior proven",
    "runtime input behavior proven",
    "runtime menu behavior proven",
    "fully reverse-engineered",
    "rebuild parity proven",
)


def normalize_address(value: str) -> str:
    text = (value or "").strip().lower()
    if text.startswith("0x"):
        text = text[2:]
    return "0x" + text.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in read_text(path).splitlines() if line.strip()]


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    token_variants = {
        token,
        token.replace("\\", "\\\\"),
        token.replace("\\", "\\\\\\\\"),
    }
    text_variants = {text, text.replace("`", "")}
    return any(candidate in haystack for haystack in text_variants for candidate in token_variants)


def check_artifacts(failures: list[str]) -> None:
    counts = {
        "pre-metadata.tsv": 5,
        "pre-tags.tsv": 5,
        "pre-xrefs.tsv": 7,
        "pre-instructions.tsv": 1643,
        "pre-decompile/index.tsv": 5,
        "context-metadata.tsv": 9,
        "context-tags.tsv": 9,
        "context-xrefs.tsv": 12,
        "context-instructions.tsv": 896,
        "context-decompile/index.tsv": 9,
        "vtables.tsv": 16,
        "boundary-around-00472d50.tsv": 131,
        "boundary-pre-metadata.tsv": 1,
        "boundary-pre-xrefs.tsv": 1,
        "boundary-helper-metadata.tsv": 3,
        "boundary-helper-decompile/index.tsv": 3,
        "receive-context-metadata.tsv": 4,
        "receive-known-metadata.tsv": 3,
        "cgame-vtable.tsv": 8,
        "post-metadata.tsv": 6,
        "post-tags.tsv": 6,
        "post-xrefs.tsv": 8,
        "post-instructions.tsv": 1714,
        "post-decompile/index.tsv": 6,
        "post-vtables.tsv": 16,
    }
    for relative, expected in counts.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == expected, f"{relative} row count mismatch: {actual} != {expected}", failures)

    pre_boundary = read_tsv(BASE / "boundary-pre-metadata.tsv")
    require(pre_boundary[0].get("address") == TARGET, "boundary pre-metadata address mismatch", failures)
    require(pre_boundary[0].get("status") == "MISSING", "boundary pre-metadata should prove missing function", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    xrefs = read_tsv(BASE / "post-xrefs.tsv")
    vtables = read_tsv(BASE / "post-vtables.tsv")
    decompile_index = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    row = metadata.get(TARGET)
    require(row is not None, f"missing post metadata for {TARGET}", failures)
    if row:
        require(row.get("name") == TARGET_NAME, "target name mismatch", failures)
        require(row.get("signature") == TARGET_SIGNATURE, f"target signature mismatch: {row.get('signature')}", failures)
        require(row.get("status") == "OK", "target metadata status mismatch", failures)
        for token in COMMENT_TOKENS:
            require(token in row.get("comment", ""), f"missing comment token: {token}", failures)

    tag_row = tags.get(TARGET)
    require(tag_row is not None, f"missing post tags for {TARGET}", failures)
    if tag_row:
        actual_tags = set(tag_row.get("tags", "").split(";"))
        require(COMMON_TAGS.issubset(actual_tags), f"tags missing: {COMMON_TAGS - actual_tags}", failures)

    dec = decompile_index.get(TARGET)
    require(dec is not None, f"missing decompile index for {TARGET}", failures)
    if dec:
        require(dec.get("name") == TARGET_NAME, "decompile name mismatch", failures)
        require(dec.get("signature") == TARGET_SIGNATURE, "decompile signature mismatch", failures)
        require(dec.get("status") == "OK", "decompile status mismatch", failures)
    decompile = read_text(BASE / "post-decompile" / "00472d50_CGameInterface__VFunc_03_HandleMenuControlInput.c")
    for token in DECOMPILE_TOKENS:
        require(token in decompile, f"missing decompile token: {token}", failures)

    require(
        any(
            row.get("vtable", "").lower() == "005dbc2c"
            and row.get("slot_index") == "3"
            and normalize_address(row.get("pointer_addr", "")) == TARGET
            and row.get("function_name") == TARGET_NAME
            and row.get("status") == "OK"
            for row in vtables
        ),
        "missing post-vtable slot 3 target",
        failures,
    )
    require(
        any(
            normalize_address(row.get("target_addr", "")) == TARGET
            and normalize_address(row.get("from_addr", "")) == "0x005dbc38"
            and row.get("ref_type") == "DATA"
            for row in xrefs
        ),
        "missing vtable DATA xref to recovered target",
        failures,
    )
    require(
        any(
            normalize_address(row.get("target_addr", "")) == "0x00472b40"
            and normalize_address(row.get("from_addr", "")) == "0x00472df6"
            and normalize_address(row.get("from_function_addr", "")) == TARGET
            for row in xrefs
        ),
        "missing recovered-function call to CGameInterface__HandleMenuSelection",
        failures,
    )


def check_logs(failures: list[str]) -> None:
    expected = {
        "pre-metadata.log": "targets=5 found=5 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=5 missing=0",
        "pre-xrefs.log": "Wrote 7 rows",
        "pre-instructions.log": "Wrote 1643 function-body instruction rows",
        "pre-decompile.log": "targets=5 dumped=5 missing=0 failed=0",
        "context-metadata.log": "targets=9 found=9 missing=0",
        "context-tags.log": "ExportFunctionTagsByAddress complete: rows=9 missing=0",
        "context-xrefs.log": "Wrote 12 rows",
        "context-instructions.log": "Wrote 896 function-body instruction rows",
        "context-decompile.log": "targets=9 dumped=9 missing=0 failed=0",
        "vtables.log": "ExportVtableSlots complete: targets=1 rows=16",
        "boundary-pre-metadata.log": "targets=1 found=0 missing=1",
        "boundary-around-00472d50.log": "Wrote 131 instruction rows",
        "boundary-pre-xrefs.log": "Wrote 1 rows",
        "boundary-helper-metadata.log": "targets=3 found=3 missing=0",
        "boundary-helper-decompile.log": "targets=3 dumped=3 missing=0 failed=0",
        "receive-context-metadata.log": "targets=4 found=3 missing=1",
        "receive-known-metadata.log": "targets=3 found=3 missing=0",
        "cgame-vtable.log": "ExportVtableSlots complete: targets=1 rows=8",
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 created=0 would_create=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=1 skipped=0 created=1 would_create=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=1 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=6 found=6 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=6 missing=0",
        "post-xrefs.log": "Wrote 8 rows",
        "post-instructions.log": "Wrote 1714 function-body instruction rows",
        "post-decompile.log": "targets=6 dumped=6 missing=0 failed=0",
        "post-vtables.log": "ExportVtableSlots complete: targets=1 rows=16",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR", "FAIL:", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    quality_log = read_text(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave952.log")
    require("total_functions=6151 commented_functions=6151" in quality_log, "quality refresh mismatch", failures)
    queue_log = read_text(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave952_queue_probe.log")
    require("Total functions: 6151" in queue_log, "queue probe total mismatch", failures)
    require("Commentless functions: 0" in queue_log, "queue probe commentless mismatch", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6151, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(quality["uncertainOwnerNameCount"] == 0, "uncertain owner count mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    require(len(rows) == 6151, "quality TSV row count mismatch", failures)
    require(all(row.get("comment", "").strip() for row in rows), "quality TSV has commentless rows", failures)
    require(not any(row.get("signature", "").startswith("undefined ") for row in rows), "quality TSV has undefined signature rows", failures)
    require(not any(re.search(r"\bparam_\d+\b", row.get("signature", "")) for row in rows), "quality TSV has param_N rows", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes", 0)) == 173542279, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        NOTE,
        CAMPAIGN,
        GHIDRA_REFERENCE,
        FUNCTION_INDEX,
        BACKLOG,
        FRONTEND_DOC,
        GAME_DOC,
        CONTROLLER_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in docs:
        text = read_text(path)
        for token in CORE_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:ghidra-game-interface-menu-control-boundary-wave952")
        == r"py -3 tools\ghidra_game_interface_menu_control_boundary_wave952_probe.py --check",
        "missing package script",
        failures,
    )
    ledger = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave952 GameInterface menu control boundary review" for row in ledger), "missing Wave952 ledger row", failures)
    require(any(row.get("task") == "Wave952 GameInterface menu control boundary review" and row.get("attempt_id") == 20561 for row in attempts), "missing Wave952 attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs(failures)
    check_queue_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave952 GameInterface menu-control boundary probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave952 GameInterface menu-control boundary probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
