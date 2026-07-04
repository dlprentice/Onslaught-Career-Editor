#!/usr/bin/env python3
"""Validate Wave751 unwind-continuation read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave751-unwind-continuation"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_unwind_continuation_wave751_2026-05-22.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
FRONTEND_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FrontEnd.cpp" / "_index.md"
GAME_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "game.cpp" / "_index.md"
MONITOR_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "monitor.h" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260522-204801_post_wave751_unwind_continuation_verified"

TARGET_XREFS = {
    "0x005d2730": "0x0061b5a4",
    "0x005d2760": "0x0061b5cc",
    "0x005d2780": "0x0061b5f4",
    "0x005d2799": "0x0061b5fc",
    "0x005d27a1": "0x0061b604",
    "0x005d27a9": "0x0061b60c",
    "0x005d27d0": "0x0061b634",
    "0x005d27f0": "0x0061b65c",
    "0x005d27f8": "0x0061b664",
    "0x005d2810": "0x0061b68c",
    "0x005d2829": "0x0061b694",
    "0x005d2842": "0x0061b69c",
    "0x005d285b": "0x0061b6a4",
    "0x005d2874": "0x0061b6ac",
    "0x005d288d": "0x0061b6b4",
    "0x005d28a6": "0x0061b6bc",
    "0x005d28bf": "0x0061b6c4",
    "0x005d28f0": "0x0061b6ec",
    "0x005d2909": "0x0061b6f4",
    "0x005d2930": "0x0061b71c",
    "0x005d2950": "0x0061b744",
    "0x005d2970": "0x0061b76c",
    "0x005d29a0": "0x0061b794",
    "0x005d29d0": "0x0061b7bc",
    "0x005d29d8": "0x0061b7c4",
}

COMMON_TAGS = {
    "static-reaudit",
    "unwind-continuation-wave751",
    "wave751-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "compiler-unwind",
    "scope-table",
}

CORE_ANCHORS = (
    "Wave751 unwind continuation",
    "unwind-continuation-wave751",
    "0x005d2730 Unwind@005d2730",
    "0x005d2780 Unwind@005d2780",
    "0x005d27a9 Unwind@005d27a9",
    "0x005d2930 Unwind@005d2930",
    "0x005d29d8 Unwind@005d29d8",
    "0x005d29f1 Unwind@005d29f1",
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
        "pre-instructions.tsv": 725,
        "pre-decompile/index.tsv": 25,
        "post-metadata.tsv": 25,
        "post-tags.tsv": 25,
        "post-xrefs.tsv": 25,
        "post-instructions.tsv": 725,
        "post-decompile/index.tsv": 25,
        "pre-helper-metadata.tsv": 7,
        "string-00629df0.tsv": 1,
        "string-0062bba4.tsv": 1,
        "string-0062551c.tsv": 1,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    helper_names = {row["name"] for row in read_tsv(BASE / "pre-helper-metadata.tsv")}
    for name in (
        "OID__FreeObject_Callback",
        "CDXLandscape__DestroyResourceDescriptorArray_Thunk",
        "CGenericCamera__dtor",
        "CGenericActiveReader__dtor",
        "CMonitor__Shutdown_Thunk",
        "CDXLandscape__ReleaseSurfaces",
        "CRT__SehDispatchWithScopeTable_Thunk_0055d731",
    ):
        require(name in helper_names, f"missing helper metadata row: {name}", failures)

    expected_strings = {
        "string-00629df0.tsv": r"[maintainer-local-source-export-root]\FrontEnd.cpp",
        "string-0062bba4.tsv": r"[maintainer-local-source-export-root]\game.cpp",
        "string-0062551c.tsv": r"[maintainer-local-source-export-root]\monitor.h",
    }
    for relative, expected in expected_strings.items():
        rows = read_tsv(BASE / relative)
        require(rows and rows[0].get("cstring") == expected, f"{relative} string mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs = {normalize_address(row["target_addr"]): row for row in read_tsv(BASE / "post-xrefs.tsv")}

    for address, expected_scope in TARGET_XREFS.items():
        name = f"Unwind@{address[2:]}"
        signature = f"void __cdecl {name}(void)"
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            comment = row.get("comment", "")
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in ("Wave751 static read-back", "compiler-generated SEH unwind", expected_scope, "Static retail Ghidra metadata/decompile/xref evidence only"):
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
        "post-instructions.log": "Wrote 725 instruction rows",
        "post-decompile.log": "targets=25 dumped=25 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6098 commented_functions=4637",
        "queue-probe.log": "Commentless functions: 1461",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave751.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave751_queue_probe.log",
    }
    for relative, token in expected.items():
        path = log_aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 1461, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 938, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 27, "param_N count mismatch", failures)
    high_signal = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(high_signal["address"] == "0x005d29f1", "high-signal head mismatch", failures)
    require(high_signal["name"] == "Unwind@005d29f1", "high-signal name mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 4637, "quality TSV commented count mismatch", failures)
    require(strict_clean == 4579, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x0042f220", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CSPtrSet__Clear", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 168004487 or backup.get("totalBytes") == 168004487.0, "backup byte count mismatch", failures)
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

    function_docs = {
        FRONTEND_DOC: ("Wave751", "unwind-continuation-wave751", "0x005d2730 Unwind@005d2730", "0x005d2760 Unwind@005d2760", BACKUP_PATH),
        GAME_DOC: ("Wave751", "unwind-continuation-wave751", "0x005d2780 Unwind@005d2780", "0x005d2930 Unwind@005d2930", "0x005d2950 Unwind@005d2950", "0x005d29d8 Unwind@005d29d8", BACKUP_PATH),
        MONITOR_DOC: ("Wave751", "unwind-continuation-wave751", "0x005d27a9 Unwind@005d27a9", BACKUP_PATH),
    }
    for path, tokens in function_docs.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(scripts.get("test:ghidra-unwind-continuation-wave751") == r"py -3 tools\ghidra_unwind_continuation_wave751_probe.py --check", "missing package script", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave751 unwind continuation" for row in ledger_rows), "missing Wave751 ledger row", failures)
    require(any(row.get("task") == "Wave751 unwind continuation" and row.get("attempt_id") == 20406 for row in attempts), "missing Wave751 attempt row", failures)


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
        print("Wave751 unwind-continuation probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave751 unwind-continuation probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
