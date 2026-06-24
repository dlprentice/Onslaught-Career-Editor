#!/usr/bin/env python3
"""Validate Wave972 console-menu boundary recovery artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave972-console-menu-constructor-review"
QUEUE = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_console_menu_boundary_recovery_wave972_2026-05-28.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
CONSOLE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "console.cpp" / "_index.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260528-185042_post_wave972_console_menu_boundary_recovery_verified"

TARGETS = {
    "0x00401480": {
        "name": "SharedVFunc__ReturnTrue_00401480",
        "signature": "int __thiscall SharedVFunc__ReturnTrue_00401480(void * this)",
        "tokens": ("0x005d96fc", "0x005d971c", "0x005d973c", "MOV AL, 0x1"),
        "slots": ("005d96fc", "005d971c", "005d973c"),
    },
    "0x00429e30": {
        "name": "CConsoleRootMenu__GetName",
        "signature": "void __thiscall CConsoleRootMenu__GetName(void * this, char * outName)",
        "tokens": ("0x005d972c", "0x00624d3c", "Onslaught"),
        "slots": ("005d972c",),
    },
    "0x00429e60": {
        "name": "CConsoleRootMenu__GetEntry",
        "signature": "void __thiscall CConsoleRootMenu__GetEntry(void * this, int index, char * outText)",
        "tokens": ("0x005d9734", "0x00624d48", "???"),
        "slots": ("005d9734",),
    },
    "0x00429e90": {
        "name": "CConsoleCommandMenu__GetName",
        "signature": "void __thiscall CConsoleCommandMenu__GetName(void * this, char * outName)",
        "tokens": ("0x005d970c", "0x00624d4c", "Console commands"),
        "slots": ("005d970c",),
    },
    "0x0042c460": {
        "name": "CConsoleMenu__UnlinkChild",
        "signature": "void __thiscall CConsoleMenu__UnlinkChild(void * this, void * child)",
        "tokens": ("0x005d9704", "0x005d9724", "0x005d9744", "0x005d9764", "unlinks a child"),
        "slots": ("005d9704", "005d9724", "005d9744", "005d9764"),
    },
    "0x0042c4b0": {
        "name": "CConsoleCommandMenu__GetNumEntries",
        "signature": "int __thiscall CConsoleCommandMenu__GetNumEntries(void * this)",
        "tokens": ("0x005d9710", "0x0066582c", "+0xa8"),
        "slots": ("005d9710",),
    },
    "0x0042c4d0": {
        "name": "CConsoleCommandMenu__GetEntry",
        "signature": "void __thiscall CConsoleCommandMenu__GetEntry(void * this, int index, char * outText)",
        "tokens": ("0x005d9714", "0x0066582c", "0x00624d48"),
        "slots": ("005d9714",),
    },
    "0x0042c530": {
        "name": "CConsoleCommandMenu__OnClick",
        "signature": "void __thiscall CConsoleCommandMenu__OnClick(void * this, int index)",
        "tokens": ("0x005d9718", "0x0066529c", "0x00665824", "PLATFORM__SetKeySink"),
        "slots": ("005d9718",),
    },
    "0x0042c5e0": {
        "name": "CConsoleVarMenu__GetNumEntries",
        "signature": "int __thiscall CConsoleVarMenu__GetNumEntries(void * this)",
        "tokens": ("0x005d96f0", "0x00665830", "+0xac"),
        "slots": ("005d96f0",),
    },
    "0x0042c600": {
        "name": "CConsoleVarMenu__GetEntry",
        "signature": "void __thiscall CConsoleVarMenu__GetEntry(void * this, int index, char * outText)",
        "tokens": ("0x005d96f4", "CConsoleVar__FormatValueToString", "CConsoleVar__GetTypeName", "0x00625480"),
        "slots": ("005d96f4",),
    },
    "0x0042c6a0": {
        "name": "CConsoleVarMenu__OnClick",
        "signature": "void __thiscall CConsoleVarMenu__OnClick(void * this, int index)",
        "tokens": ("0x005d96f8", "set-command text", "0x0066529c", "PLATFORM__SetKeySink"),
        "slots": ("005d96f8",),
    },
}

COMMON_TAGS = {
    "static-reaudit",
    "console-menu-boundary-recovery-wave972",
    "wave972-readback-verified",
    "retail-binary-evidence",
    "function-boundary-recovered",
    "console-system",
    "console-menu",
    "vtable-target",
    "comment-hardened",
    "signature-hardened",
}

STRING_EXPECTATIONS = {
    "string-00624d3c.tsv": "Onslaught",
    "string-00624d48.tsv": "???",
    "string-00624d4c.tsv": "Console commands",
    "string-0062547c.tsv": "%s ",
    "string-00625480.tsv": r"%s (%s) %s\x0a %s",
    "string-00625490.tsv": "set %s ",
}

CORE_TOKENS = (
    "Wave972",
    "console-menu-boundary-recovery-wave972",
    "0x00401480 SharedVFunc__ReturnTrue_00401480",
    "0x00429e30 CConsoleRootMenu__GetName",
    "0x0042c460 CConsoleMenu__UnlinkChild",
    "0x0042c530 CConsoleCommandMenu__OnClick",
    "0x0042c6a0 CConsoleVarMenu__OnClick",
    "345/1408 = 24.50%",
    "402/1465 = 27.44%",
    "6209/6209 = 100.00%",
    BACKUP_PATH,
    "function-boundary recovery",
)

OVERCLAIMS = (
    "runtime console menu behavior proven",
    "runtime key-sink side effects proven",
    "rebuild parity proven",
    "fully reverse-engineered",
)


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def normalize_slot(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return value.zfill(8)


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
    return token in text or token.replace("\\", "\\\\") in text


def signature_counts(rows: list[dict[str, str]]) -> tuple[int, int]:
    commented = sum(1 for row in rows if row.get("comment", "").strip())
    strict_clean = sum(
        1
        for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not re.search(r"\bparam_\d+\b", row.get("signature", ""))
    )
    return commented, strict_clean


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "metadata.tsv": 5,
        "tags.tsv": 5,
        "xrefs.tsv": 15,
        "instructions.tsv": 112,
        "decompile/index.tsv": 5,
        "post-metadata.tsv": 11,
        "post-tags.tsv": 11,
        "post-xrefs.tsv": 83,
        "post-body-instructions.tsv": 283,
        "post-decompile/index.tsv": 11,
        "post-vtable-slots.tsv": 36,
    }
    for relative, expected in expected_counts.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == expected, f"{relative} count mismatch: {actual} != {expected}", failures)

    for relative, expected in STRING_EXPECTATIONS.items():
        rows = read_tsv(BASE / relative)
        require(rows and rows[0].get("cstring") == expected, f"{relative} string mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    slots = {(normalize_slot(row["slot_addr"]), normalize_address(row["pointer_addr"])): row for row in read_tsv(BASE / "post-vtable-slots.tsv")}

    for address, expected in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == expected["name"], f"name mismatch at {address}", failures)
            require(row.get("signature") == expected["signature"], f"signature mismatch at {address}: {row.get('signature')}", failures)
            comment = row.get("comment", "")
            for token in ("Wave972 console-menu boundary recovery", "Static retail Ghidra evidence only", *expected["tokens"]):
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"tags missing at {address}: {COMMON_TAGS - actual_tags}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == expected["signature"], f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        for slot in expected["slots"]:
            slot_row = slots.get((normalize_slot(slot), address))
            require(slot_row is not None, f"missing vtable slot {slot} for {address}", failures)
            if slot_row is not None:
                require(slot_row.get("function_name") == expected["name"], f"vtable function mismatch at {slot}", failures)
                require(slot_row.get("status") == "OK", f"vtable status mismatch at {slot}", failures)


def check_logs_queue_backup(failures: list[str]) -> None:
    expected_logs = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 created=0 would_create=11 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=11 skipped=0 created=11 would_create=0 renamed=0 would_rename=0 signature_updated=11 comment_only_updated=22 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=11 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=11 found=11 missing=0",
        "post-tags.log": "rows=11 missing=0",
        "post-xrefs.log": "Wrote 83 rows",
        "post-body-instructions.log": "Wrote 283 function-body instruction rows",
        "post-decompile.log": "targets=11 dumped=11 missing=0 failed=0",
        "post-vtable-slots.log": "ExportVtableSlots complete: targets=3 rows=36",
        "export-functions-quality-wave972.log": "total_functions=6209 commented_functions=6209",
        "wave972_queue_probe.log": "Total functions: 6209",
    }
    aliases = {
        "export-functions-quality-wave972.log": QUEUE / "export-functions-quality-wave972.log",
        "wave972_queue_probe.log": QUEUE / "wave972_queue_probe.log",
    }
    for relative, token in expected_logs.items():
        path = aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    queue = read_json(QUEUE / "static-reaudit-queue.json")
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6209, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(quality["uncertainOwnerNameCount"] == 0, "uncertain owner count mismatch", failures)
    require(quality["helperAddressNameCount"] == 0, "address helper count mismatch", failures)
    require(quality["wrapperAddressNameCount"] == 0, "address wrapper count mismatch", failures)

    rows = read_tsv(QUEUE / "functions_quality.tsv")
    commented, strict_clean = signature_counts(rows)
    require(len(rows) == 6209, "quality TSV row count mismatch", failures)
    require(commented == 6209, "quality TSV commented count mismatch", failures)
    require(strict_clean == 6209, "strict clean-signature count mismatch", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 173771655, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [PUBLIC_NOTE, GHIDRA_REFERENCE, CAMPAIGN, FUNCTION_INDEX, CONSOLE_DOC, BACKLOG, DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE]
    for path in docs:
        text = read_text(path)
        for token in CORE_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIMS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-console-menu-boundary-recovery-wave972")
        == r"py -3 tools\ghidra_console_menu_boundary_recovery_wave972_probe.py --check",
        "missing package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave972 console menu boundary recovery" for row in ledger_rows), "missing Wave972 ledger row", failures)
    require(
        any(row.get("task") == "Wave972 console menu boundary recovery" and row.get("attempt_id") == 20568 for row in attempts),
        "missing Wave972 attempt row",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_queue_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave972 console-menu boundary recovery probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Wave972 console-menu boundary recovery probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
