#!/usr/bin/env python3
"""Validate Wave756 unwind-continuation read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave756-unwind-continuation"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_unwind_continuation_wave756_2026-05-23.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
MCTENTACLE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "MCTentacle.cpp.md"
MECH_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Mech.cpp" / "_index.md"
MONITOR_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "monitor.h" / "_index.md"
MEMORY_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "MemoryManager.cpp" / "_index.md"
MENUITEM_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "MenuItem.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260523-112625_post_wave756_unwind_continuation_verified"

TARGET_XREFS = {
    "0x005d3392": "0x0061c0ac",
    "0x005d33c0": "0x0061c0d4",
    "0x005d33e0": "0x0061c0fc",
    "0x005d3400": "0x0061c124",
    "0x005d3420": "0x0061c14c",
    "0x005d3440": "0x0061c174",
    "0x005d3460": "0x0061c19c",
    "0x005d3480": "0x0061c1c4",
    "0x005d3488": "0x0061c1cc",
    "0x005d3493": "0x0061c1d4",
    "0x005d34b0": "0x0061c1fc",
    "0x005d34b8": "0x0061c204",
    "0x005d34c3": "0x0061c20c",
    "0x005d34ce": "0x0061c214",
    "0x005d34f0": "0x0061c23c",
    "0x005d34f8": "0x0061c244",
    "0x005d3503": "0x0061c24c",
    "0x005d3520": "0x0061c274",
    "0x005d3540": "0x0061c29c",
    "0x005d3560": "0x0061c2c4",
    "0x005d3580": "0x0061c2ec",
    "0x005d35a0": "0x0061c314",
    "0x005d35bc": "0x0061c31c",
    "0x005d35f0": "0x0061c344",
    "0x005d360c": "0x0061c34c",
}

COMMON_TAGS = {
    "static-reaudit",
    "unwind-continuation-wave756",
    "wave756-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "compiler-unwind",
    "scope-table",
}

HELPER_NAMES = (
    "OID__FreeObject_Callback",
    "CParticleManager__RemoveFromGlobalList_Thunk",
    "CUnitAI__dtor_body_00415080",
    "CMonitor__Shutdown",
    "CGenericActiveReader__dtor",
    "CMonitor__Shutdown_Thunk",
    "CDXLandscape__FreeObjectCallback",
    "CUnitAI__FreeOwnedObjects_10_18",
    "CMCBuggy__ProfileEnd",
    "CMemoryHeap__ReleaseMutexUnwindCleanup",
    "CDXMemBuffer__dtor_base",
    "CMenuItem__RestoreCompactVTable",
    "CRT__SehDispatchWithScopeTable_Thunk_0055d731",
)

STRING_EXPECTATIONS = {
    "string-00622b80.tsv": r"[maintainer-local-source-export-root]\Monitor.h",
    "string-0062e06c.tsv": r"[maintainer-local-source-export-root]\MCTentacle.cpp",
    "string-0062e0e0.tsv": r"[maintainer-local-source-export-root]\Mech.cpp",
    "string-0062f590.tsv": r"[maintainer-local-source-export-root]\MemoryManager.cpp",
    "string-0062f7d8.tsv": r"[maintainer-local-source-export-root]\MenuItem.cpp",
}

COMMENT_TOKENS = {
    "0x005d3392": ("Wave756 static read-back", "MCTentacle.cpp", "0x0062e06c", "0x6d"),
    "0x005d33c0": ("Wave756 static read-back", "Mech.cpp", "0x0062e0e0", "0x3d"),
    "0x005d3420": ("Wave756 static read-back", "Mech.cpp", "0x0062e0e0", "0x57"),
    "0x005d3440": ("Wave756 static read-back", "CParticleManager__RemoveFromGlobalList_Thunk", "EBP-0x8c"),
    "0x005d3480": ("Wave756 static read-back", "CMonitor__Shutdown", "0x0061c1c4"),
    "0x005d3488": ("Wave756 static read-back", "CGenericActiveReader__dtor", "0x0c"),
    "0x005d34b0": ("Wave756 static read-back", "CMonitor__Shutdown_Thunk", "0x0061c1fc"),
    "0x005d34b8": ("Wave756 static read-back", "CDXLandscape__FreeObjectCallback", "0x0061c204"),
    "0x005d34c3": ("Wave756 static read-back", "CUnitAI__FreeOwnedObjects_10_18", "0x0061c20c"),
    "0x005d34f0": ("Wave756 static read-back", "CMonitor__Shutdown_Thunk", "0x0061c23c"),
    "0x005d3520": ("Wave756 static read-back", "CMCBuggy__ProfileEnd", "EBP-0x34"),
    "0x005d3540": ("Wave756 static read-back", "CMemoryHeap__ReleaseMutexUnwindCleanup", "EBP-0x10"),
    "0x005d3580": ("Wave756 static read-back", "CDXMemBuffer__dtor_base", "EBP-0x6844"),
    "0x005d35a0": ("Wave756 static read-back", "MemoryManager.cpp", "0x0062f590", "0x708"),
    "0x005d35bc": ("Wave756 static read-back", "MemoryManager.cpp", "0x0062f590", "0x77a"),
    "0x005d35f0": ("Wave756 static read-back", "MenuItem.cpp", "0x0062f7d8", "0xad"),
    "0x005d360c": ("Wave756 static read-back", "CMenuItem__RestoreCompactVTable", "0x0061c34c"),
}

CORE_ANCHORS = (
    "Wave756 unwind continuation",
    "unwind-continuation-wave756",
    "0x005d3392 Unwind@005d3392",
    "0x005d33c0 Unwind@005d33c0",
    "0x005d3420 Unwind@005d3420",
    "0x005d3480 Unwind@005d3480",
    "0x005d34b0 Unwind@005d34b0",
    "0x005d3540 Unwind@005d3540",
    "0x005d35a0 Unwind@005d35a0",
    "0x005d35f0 Unwind@005d35f0",
    "0x005d360c Unwind@005d360c",
    "0x005d3614 Unwind@005d3614",
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
        "pre-instructions.tsv": 925,
        "pre-decompile/index.tsv": 25,
        "post-metadata.tsv": 25,
        "post-tags.tsv": 25,
        "post-xrefs.tsv": 25,
        "post-instructions.tsv": 925,
        "post-decompile/index.tsv": 25,
        "pre-helper-metadata.tsv": 13,
        "post-helper-metadata.tsv": 13,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    helper_names = {row["name"] for row in read_tsv(BASE / "post-helper-metadata.tsv")}
    for name in HELPER_NAMES:
        require(name in helper_names, f"missing helper metadata row: {name}", failures)

    for relative, expected in STRING_EXPECTATIONS.items():
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
            tokens = COMMENT_TOKENS.get(
                address,
                ("Wave756 static read-back", expected_scope, "Static retail Ghidra metadata/decompile/xref evidence only"),
            )
            for token in tokens:
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
        "post-instructions.log": "Wrote 925 instruction rows",
        "post-decompile.log": "targets=25 dumped=25 missing=0 failed=0",
        "post-helper-metadata.log": "targets=13 found=13 missing=0",
        "quality-refresh.log": "total_functions=6098 commented_functions=4762",
        "queue-probe.log": "Commentless functions: 1336",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave756.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave756_queue_probe.log",
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
    require(quality["commentlessFunctionCount"] == 1336, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 813, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 27, "param_N count mismatch", failures)
    high_signal = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(high_signal["address"] == "0x005d3614", "high-signal head mismatch", failures)
    require(high_signal["name"] == "Unwind@005d3614", "high-signal name mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 4762, "quality TSV commented count mismatch", failures)
    require(strict_clean == 4704, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x0042f220", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CSPtrSet__Clear", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 168496007 or backup.get("totalBytes") == 168496007.0, "backup byte count mismatch", failures)
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
        MCTENTACLE_DOC: ("Wave756", "unwind-continuation-wave756", "0x005d3392 Unwind@005d3392", "0x0062e06c", BACKUP_PATH),
        MECH_DOC: ("Wave756", "unwind-continuation-wave756", "0x005d33c0 Unwind@005d33c0", "0x005d3420 Unwind@005d3420", "0x005d3440 Unwind@005d3440", BACKUP_PATH),
        MONITOR_DOC: ("Wave756", "unwind-continuation-wave756", "0x005d3480 Unwind@005d3480", "0x005d34b0 Unwind@005d34b0", "0x005d34f0 Unwind@005d34f0", BACKUP_PATH),
        MEMORY_DOC: ("Wave756", "unwind-continuation-wave756", "0x005d3540 Unwind@005d3540", "0x005d3580 Unwind@005d3580", "0x005d35a0 Unwind@005d35a0", "0x005d35bc Unwind@005d35bc", BACKUP_PATH),
        MENUITEM_DOC: ("Wave756", "unwind-continuation-wave756", "0x005d35f0 Unwind@005d35f0", "0x005d360c Unwind@005d360c", "0x0062f7d8", BACKUP_PATH),
    }
    for path, tokens in function_docs.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-unwind-continuation-wave756")
        == r"py -3 tools\ghidra_unwind_continuation_wave756_probe.py --check",
        "missing package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave756 unwind continuation" for row in ledger_rows), "missing Wave756 ledger row", failures)
    require(
        any(row.get("task") == "Wave756 unwind continuation" and row.get("attempt_id") == 20411 for row in attempts),
        "missing Wave756 attempt row",
        failures,
    )


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
        print("Wave756 unwind-continuation probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave756 unwind-continuation probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
