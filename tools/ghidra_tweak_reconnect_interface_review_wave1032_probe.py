#!/usr/bin/env python3
"""Validate Wave1032 CTweak / reconnect-interface read-only artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1032-tweak-reconnect-interface-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_tweak_reconnect_interface_review_wave1032_2026-06-01.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1032_recheck_2026-06-01.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FRONTEND_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FrontEnd.cpp" / "_index.md"
FEPMULTI_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FEPMultiplayerStart.cpp" / "_index.md"
CLIPARAMS_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "CLIParams.cpp" / "_index.md"
ENGINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "engine.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260601-043550_post_wave1032_tweak_reconnect_interface_review_verified"

TARGETS = {
    "0x00527c90": (
        "CReconnectInterface__ctor",
        "void * __thiscall CReconnectInterface__ctor(void * this, void * tweak_name, int default_index_one_based)",
        ("CTweak__ctor_base", "0x005e4a80", "default_index_one_based - 1"),
    ),
    "0x00527d00": (
        "CReconnectInterface__VFunc_07_00527d00",
        "void __thiscall CReconnectInterface__VFunc_07_00527d00(void * this, float tweak_value)",
        ("rounds the single float", "this+0x0c", "-landscape0/-landscape1/-landscape2"),
    ),
    "0x00528690": (
        "CTweak__ctor_base",
        "void * __thiscall CTweak__ctor_base(void * this, void * callback_context)",
        ("callback_context", "DAT_0089c018", "global tweak list"),
    ),
    "0x005286b0": (
        "CTweak__dtor_base",
        "void __fastcall CTweak__dtor_base(void * this)",
        ("destructor-base", "DAT_0089c018", "unlinks"),
    ),
    "0x00528b20": (
        "CTweakInt_SetNumViewpoints__ctor",
        "void * __thiscall CTweakInt_SetNumViewpoints__ctor(void * this, void * callback_context, int initial_value)",
        ("PTR_CEngine__SetNumViewpoints_005e4aa4", "initial_value", "+0x0c"),
    ),
}

CONTEXT_TARGETS = {
    "0x004530a0": (
        "CTweak__dtor_base_thunk_004530a0",
        "void __fastcall CTweak__dtor_base_thunk_004530a0(void * this)",
        "OK",
    ),
    "0x00527c50": (
        "CFrontEnd__AdvanceStateAndRelinquishControl",
        "bool __thiscall CFrontEnd__AdvanceStateAndRelinquishControl(void * this, void * controller, int caller_state_token)",
        "OK",
    ),
    "0x0054d4ac": ("<none>", "<none>", "MISSING"),
}

DOC_TOKENS = (
    "Wave1032",
    "tweak-reconnect-interface-review-wave1032",
    "0x00527c90 CReconnectInterface__ctor",
    "0x00527d00 CReconnectInterface__VFunc_07_00527d00",
    "0x00528690 CTweak__ctor_base",
    "0x005286b0 CTweak__dtor_base",
    "0x00528b20 CTweakInt_SetNumViewpoints__ctor",
    "0x00527c50 CFrontEnd__AdvanceStateAndRelinquishControl",
    "0x004530a0 CTweak__dtor_base_thunk_004530a0",
    "0x0054d4ac",
    "631/1408 = 44.82%",
    "860/1493 = 57.60%",
    "500/500 = 100.00%",
    "6238/6238 = 100.00%",
    BACKUP_PATH,
    "no mutation",
)

OVERCLAIMS = (
    "runtime frontend reconnect behavior proven",
    "runtime landscape-detail behavior proven",
    "runtime viewpoint tweak behavior proven",
    "runtime tweak registration proven",
    "exact source symbol identity proven",
    "exact layout proven",
    "rebuild parity proven",
    "fully reverse-engineered",
)


def normalize_address(value: str) -> str:
    text = value.strip().lower()
    if text.startswith("0x"):
        text = text[2:]
    return "0x" + text.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig", errors="replace").replace("\x00", "")


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
    return token in text or token.replace("\\", "\\\\") in text


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "metadata.tsv": 5,
        "tags.tsv": 5,
        "xrefs.tsv": 15,
        "instructions.tsv": 58,
        "decompile/index.tsv": 5,
        "context-metadata.tsv": 3,
        "context-tags.tsv": 3,
        "context-xrefs.tsv": 53,
        "context-instructions.tsv": 19,
        "context-decompile/index.tsv": 3,
        "xref-site-windows.tsv": 273,
        "vtable-slots.tsv": 24,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "decompile" / "index.tsv")}

    for address, (name, signature, comment_tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata at {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in comment_tokens:
                require(token in row.get("comment", ""), f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags at {address}", failures)
        if tag_row is not None:
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)
            tag_text = tag_row.get("tags", "")
            require("static-reaudit" in tag_text, f"missing static-reaudit tag at {address}", failures)
            if address in {"0x00527c90", "0x00527d00"}:
                require("frontend-reconnect-wave569" in tag_text, f"missing Wave569 tag at {address}", failures)
            if address in {"0x00528690", "0x005286b0", "0x00528b20"}:
                require("frontend-briefing-tweak-wave380" in tag_text, f"missing Wave380 tag at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index at {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    context = {normalize_address(row["address"]): row for row in read_tsv(BASE / "context-metadata.tsv")}
    for address, (name, signature, status) in CONTEXT_TARGETS.items():
        row = context.get(address)
        require(row is not None, f"missing context row at {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"context name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"context signature mismatch at {address}", failures)
            require(row.get("status") == status, f"context status mismatch at {address}", failures)

    instructions = read_text(BASE / "instructions.tsv")
    for token in ("CALL\t0x00528690", "RET\t0x8", "FISTP", "RET\t0x4", "0x0089c018"):
        require(token in instructions, f"missing instruction token: {token}", failures)

    xref_windows = read_text(BASE / "xref-site-windows.tsv")
    for token in (
        "0x00423f45",
        "0x00423f66",
        "0x00423f87",
        "CALL\t0x00527d00",
        "0x0054d4ac",
        "CDXMeshVB__ReleaseResources",
        "0x0054d4dc",
        "CALL\t0x00527c90",
    ):
        require(token in xref_windows, f"missing xref-window token: {token}", failures)

    vtables = read_text(BASE / "vtable-slots.tsv")
    for token in (
        "005e4a80\t0\t005e4a80\t0x00527d00",
        "0x40000000",
        "0x3fd33333",
        "CRT__Purecall_0055df1f",
        "CVar__SetValueRounded",
        "CEngine__SetNumViewpoints",
    ):
        require(token in vtables, f"missing vtable token: {token}", failures)

    for relative in (
        "string-00618938.tsv",
        "string-00618988.tsv",
        "string-006189d8.tsv",
        "string-00618a08.tsv",
        "string-00618a38.tsv",
    ):
        rows = read_tsv(BASE / relative)
        require(len(rows) == 1, f"{relative} row count mismatch", failures)
        if rows:
            require(rows[0].get("cstring", "") == "", f"{relative} expected empty cstring", failures)

    decompile_text = "\n".join(read_text(path) for path in (BASE / "decompile").glob("*.c"))
    for token in (
        "CReconnectInterface__ctor",
        "PTR_CReconnectInterface__VFunc_07_00527d00_005e4a80",
        "ROUND(tweak_value)",
        "DAT_0089c018",
        "CTweakInt_SetNumViewpoints__ctor",
    ):
        require(token in decompile_text, f"missing decompile token: {token}", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected = {
        "metadata.log": "targets=5 found=5 missing=0",
        "tags.log": "ExportFunctionTagsByAddress complete: rows=5 missing=0",
        "xrefs.log": "Wrote 15 rows",
        "instructions.log": "Wrote 58 function-body instruction rows",
        "decompile.log": "targets=5 dumped=5 missing=0 failed=0",
        "context-metadata.log": "targets=3 found=2 missing=1",
        "context-tags.log": "ExportFunctionTagsByAddress complete: rows=2 missing=1",
        "context-xrefs.log": "Wrote 53 rows",
        "context-instructions.log": "Wrote 19 function-body instruction rows",
        "context-decompile.log": "targets=3 dumped=2 missing=1 failed=0",
        "xref-site-windows.log": "targets=13 missing=0",
        "vtable-slots.log": "targets=3 rows=24",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR", "BADNAME:", "FAIL:", "failed=1", "bad=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    for relative in (
        "string-00618938.log",
        "string-00618988.log",
        "string-006189d8.log",
        "string-00618a08.log",
        "string-00618a38.log",
    ):
        text = read_text(BASE / relative)
        require("DumpCStringAtAddress complete" in text, f"missing string dump completion in {relative}", failures)
        require("REPORT: Save succeeded" in text, f"missing string dump save success in {relative}", failures)
        require("LockException" not in text, f"LockException in {relative}", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes", 0)) == 173968263, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_docs_and_state(failures: list[str]) -> None:
    docs = [
        NOTE,
        AGGREGATE_NOTE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        FRONTEND_DOC,
        FEPMULTI_DOC,
        CLIPARAMS_DOC,
        ENGINE_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-tweak-reconnect-interface-review-wave1032")
        == r"py -3 tools\ghidra_tweak_reconnect_interface_review_wave1032_probe.py --check",
        "missing focused package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1032-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1032 --check",
        "missing aggregate package script",
        failures,
    )

    ledger = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1032 tweak reconnect interface review" for row in ledger), "missing ledger row", failures)
    require(
        any(row.get("task") == "Wave1032 tweak reconnect interface review" and row.get("attempt_id") == 20614 for row in attempts),
        "missing attempt row",
        failures,
    )

    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    require(queue.get("totalFunctions") == 6238, "queue total mismatch", failures)
    require(quality.get("commentlessFunctionCount") == 0, "commentless count mismatch", failures)
    require(quality.get("undefinedSignatureCount") == 0, "undefined count mismatch", failures)
    require(quality.get("paramSignatureCount") == 0, "param_N count mismatch", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_docs_and_state(failures)

    if failures:
        print("Wave1032 tweak reconnect-interface review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1032 tweak reconnect-interface review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
