#!/usr/bin/env python3
"""Validate Wave763 unwind-continuation read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave763-unwind-continuation"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_unwind_continuation_wave763_2026-05-23.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
PLANE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Plane.cpp" / "_index.md"
PAUSE_MENU_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "PauseMenu.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260523-150812_post_wave763_unwind_continuation_verified"

TARGET_XREFS = {
    "0x005d4477": "0x0061cde4",
    "0x005d4493": "0x0061cdec",
    "0x005d44af": "0x0061cdf4",
    "0x005d44cb": "0x0061cdfc",
    "0x005d44e7": "0x0061ce04",
    "0x005d4503": "0x0061ce0c",
    "0x005d451f": "0x0061ce14",
    "0x005d453b": "0x0061ce1c",
    "0x005d4557": "0x0061ce24",
    "0x005d4573": "0x0061ce2c",
    "0x005d45a0": "0x0061ce54",
    "0x005d45a8": "0x0061ce5c",
    "0x005d45c0": "0x0061ce84",
    "0x005d45dc": "0x0061ce8c",
    "0x005d45e4": "0x0061ce94",
    "0x005d45ef": "0x0061ce9c",
    "0x005d45fa": "0x0061cea4",
    "0x005d4616": "0x0061ceac",
    "0x005d4640": "0x0061ced4",
    "0x005d4648": "0x0061cedc",
    "0x005d4653": "0x0061cee4",
    "0x005d4670": "0x0061cf0c",
    "0x005d4686": "0x0061cf14",
    "0x005d469c": "0x0061cf1c",
    "0x005d46c0": "0x0061cf44",
}

COMMON_TAGS = {
    "static-reaudit",
    "unwind-continuation-wave763",
    "wave763-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "compiler-unwind",
    "scope-table",
}

COMMENT_TOKENS = {
    "0x005d4477": ("Wave763 static read-back", "PauseMenu.cpp", "0x006314dc", "0x59c"),
    "0x005d44af": ("Wave763 static read-back", "PauseMenu.cpp", "0x5aa"),
    "0x005d45a0": ("Wave763 static read-back", "CMonitor__Shutdown_Thunk", "EBP-0x10"),
    "0x005d45a8": ("Wave763 static read-back", "CSPtrSet__Clear", "0x14"),
    "0x005d45e4": ("Wave763 static read-back", "CMenuItemRangeVariant__Destructor", "0x0c"),
    "0x005d45ef": ("Wave763 static read-back", "CSPtrSet__Clear", "0x3c"),
    "0x005d4670": ("Wave763 static read-back", "Plane.cpp", "0x00631630", "0x17"),
    "0x005d469c": ("Wave763 static read-back", "Plane.cpp", "0x2a", "0x10"),
    "0x005d46c0": ("Wave763 static read-back", "CMonitor__Shutdown", "EBP-0x10"),
}

STRING_EXPECTATIONS = {
    "string-006314dc.tsv": r"[maintainer-local-source-export-root]\PauseMenu.cpp",
    "string-00631630.tsv": r"[maintainer-local-source-export-root]\Plane.cpp",
}

CORE_ANCHORS = (
    "Wave763 unwind continuation",
    "unwind-continuation-wave763",
    "0x005d4477 Unwind@005d4477",
    "0x005d44af Unwind@005d44af",
    "0x005d45a0 Unwind@005d45a0",
    "0x005d45a8 Unwind@005d45a8",
    "0x005d45e4 Unwind@005d45e4",
    "0x005d45ef Unwind@005d45ef",
    "0x005d4670 Unwind@005d4670",
    "0x005d469c Unwind@005d469c",
    "0x005d46c0 Unwind@005d46c0",
    "0x005d46c8 Unwind@005d46c8",
    "0x0042f220 CSPtrSet__Clear",
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime exception behavior proven",
    "runtime cleanup behavior proven",
    "fully reverse-engineered",
    "rebuild parity proven",
)


def normalize_address(address: str) -> str:
    value = address.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def expected_name(address: str) -> str:
    return f"Unwind@{address[2:]}"


def expected_signature(address: str) -> str:
    return f"void __cdecl {expected_name(address)}(void)"


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
        "pre-metadata.tsv": 25,
        "pre-tags.tsv": 25,
        "pre-xrefs.tsv": 25,
        "pre-instructions.tsv": 2625,
        "pre-decompile/index.tsv": 25,
        "post-metadata.tsv": 25,
        "post-tags.tsv": 25,
        "post-xrefs.tsv": 25,
        "post-instructions.tsv": 2625,
        "post-decompile/index.tsv": 25,
        "pre-helper-metadata.tsv": 6,
        "post-helper-metadata.tsv": 6,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    helper_names = {row["name"] for row in read_tsv(BASE / "post-helper-metadata.tsv")}
    for name in (
        "OID__FreeObject_Callback",
        "CMonitor__Shutdown_Thunk",
        "CSPtrSet__Clear",
        "CMenuItemRangeVariant__Destructor",
        "CMonitor__Shutdown",
        "CRT__SehDispatchWithScopeTable_Thunk_0055d731",
    ):
        require(name in helper_names, f"missing helper metadata row: {name}", failures)

    for relative, expected in STRING_EXPECTATIONS.items():
        rows = read_tsv(BASE / relative)
        require(rows and rows[0].get("cstring") == expected, f"{relative} string mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs = {normalize_address(row["target_addr"]): row for row in read_tsv(BASE / "post-xrefs.tsv")}

    for address, expected_scope in TARGET_XREFS.items():
        name = expected_name(address)
        signature = expected_signature(address)
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            comment = row.get("comment", "")
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in COMMENT_TOKENS.get(address, ("Wave763 static read-back", expected_scope, "Static retail Ghidra metadata/decompile/xref evidence only")):
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"tags missing at {address}: {COMMON_TAGS - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        xref_row = xrefs.get(address)
        require(xref_row is not None, f"missing xref for {address}", failures)
        if xref_row is not None:
            require(normalize_address(xref_row.get("from_addr", "")) == expected_scope, f"xref scope mismatch at {address}", failures)
            require(xref_row.get("ref_type") == "DATA", f"xref type mismatch at {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=25 found=25 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=25 missing=0",
        "post-xrefs.log": "Wrote 25 rows",
        "post-instructions.log": "Wrote 2625 instruction rows",
        "post-decompile.log": "targets=25 dumped=25 missing=0 failed=0",
        "post-helper-metadata.log": "targets=6 found=6 missing=0",
        "quality-refresh.log": "total_functions=6098 commented_functions=4937",
        "queue-probe.log": "Commentless functions: 1161",
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave763.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave763_queue_probe.log",
    }
    for relative, token in expected.items():
        path = aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 1161, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 638, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 27, "param_N count mismatch", failures)
    high_signal = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(high_signal["address"] == "0x005d46c8", "high-signal head mismatch", failures)
    require(high_signal["name"] == "Unwind@005d46c8", "high-signal name mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 4937, "quality TSV commented count mismatch", failures)
    require(strict_clean == 4879, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x0042f220", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CSPtrSet__Clear", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 169118599 or backup.get("totalBytes") == 169118599.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = [
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in CORE_ANCHORS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    owner_docs = {
        PAUSE_MENU_DOC: ("Wave763", "unwind-continuation-wave763", "0x005d4477 Unwind@005d4477", "0x005d4653 Unwind@005d4653", BACKUP_PATH),
        PLANE_DOC: ("Wave763", "unwind-continuation-wave763", "0x005d4670 Unwind@005d4670", "0x005d46c0 Unwind@005d46c0", BACKUP_PATH),
    }
    for path, tokens in owner_docs.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(scripts.get("test:ghidra-unwind-continuation-wave763") == r"py -3 tools\ghidra_unwind_continuation_wave763_probe.py --check", "missing package script", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave763 unwind continuation" for row in ledger_rows), "missing Wave763 ledger row", failures)
    require(any(row.get("task") == "Wave763 unwind continuation" and row.get("attempt_id") == 20418 for row in attempts), "missing Wave763 attempt row", failures)


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
        print("Wave763 unwind-continuation probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave763 unwind-continuation probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
