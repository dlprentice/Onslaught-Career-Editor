#!/usr/bin/env python3
"""Validate Wave744 unwind-continuation read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave744-unwind-continuation"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_unwind_continuation_wave744_2026-05-22.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
MONITOR_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "monitor.h" / "_index.md"
CAMERA_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Camera.cpp" / "_index.md"
CANNON_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Cannon.cpp" / "_index.md"
SPTRSET_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "SPtrSet.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260522-163423_post_wave744_unwind_continuation_verified"

TARGETS = {
    "0x005d1610": {"scope": "0x0061a47c", "tokens": ("CGenericCamera__dtor", "EBP-0x10"), "tags": {"camera", "generic-camera"}},
    "0x005d1618": {"scope": "0x0061a484", "tokens": ("CGenericActiveReader__dtor", "0x4"), "tags": {"active-reader", "embedded-reader"}},
    "0x005d1630": {"scope": "0x0061a4ac", "tokens": ("CGenericCamera__dtor", "EBP-0x24"), "tags": {"camera", "generic-camera"}},
    "0x005d1638": {"scope": "0x0061a4b4", "tokens": ("CMonitor__Shutdown", "0x4"), "tags": {"monitor", "shutdown", "embedded-monitor"}},
    "0x005d1643": {"scope": "0x0061a4bc", "tokens": ("CGenericActiveReader__dtor", "EBP-0x20"), "tags": {"active-reader"}},
    "0x005d164b": {"scope": "0x0061a4c4", "tokens": ("Monitor.h", "line 0x18", "memtype 0x5e"), "tags": {"monitor", "monitor-h", "free-object"}},
    "0x005d1661": {"scope": "0x0061a4cc", "tokens": ("CGenericActiveReader__dtor", "0xc"), "tags": {"active-reader", "embedded-reader"}},
    "0x005d1680": {"scope": "0x0061a4f4", "tokens": ("CGenericCamera__dtor", "EBP-0x10"), "tags": {"camera", "generic-camera"}},
    "0x005d1688": {"scope": "0x0061a4fc", "tokens": ("CMonitor__Shutdown", "EBP-0x14"), "tags": {"monitor", "shutdown", "conditional-cleanup"}},
    "0x005d16af": {"scope": "0x0061a504", "tokens": ("CGenericActiveReader__dtor", "0xc"), "tags": {"active-reader", "embedded-reader"}},
    "0x005d16d0": {"scope": "0x0061a52c", "tokens": ("CGenericCamera__dtor", "EBP-0x24"), "tags": {"camera", "generic-camera"}},
    "0x005d16d8": {"scope": "0x0061a534", "tokens": ("CGenericActiveReader__dtor", "EBP-0x20"), "tags": {"active-reader"}},
    "0x005d16e0": {"scope": "0x0061a53c", "tokens": ("Monitor.h", "line 0x18", "memtype 0x5e"), "tags": {"monitor", "monitor-h", "free-object"}},
    "0x005d1700": {"scope": "0x0061a564", "tokens": ("CGenericCamera__dtor", "EBP-0x10"), "tags": {"camera", "generic-camera"}},
    "0x005d1720": {"scope": "0x0061a58c", "tokens": ("CGenericCamera__dtor", "EBP-0x10"), "tags": {"camera", "generic-camera"}},
    "0x005d1740": {"scope": "0x0061a5b4", "tokens": ("CGenericCamera__dtor", "EBP-0x1a0"), "tags": {"camera", "generic-camera", "stack-local"}},
    "0x005d1760": {"scope": "0x0061a5dc", "tokens": ("Cannon.cpp", "line 0x22", "memtype 0x17"), "tags": {"cannon", "cannon-cpp", "free-object"}},
    "0x005d1776": {"scope": "0x0061a5e4", "tokens": ("Cannon.cpp", "line 0x23", "memtype 0x16"), "tags": {"cannon", "cannon-cpp", "free-object"}},
    "0x005d178c": {"scope": "0x0061a5ec", "tokens": ("Cannon.cpp", "line 0x26", "memtype 0x1b"), "tags": {"cannon", "cannon-cpp", "free-object"}},
    "0x005d17b0": {"scope": "0x0061a61c", "tokens": ("CSPtrSet__Clear", "EBP-0x1c"), "tags": {"sptrset", "stack-local"}},
    "0x005d17b8": {"scope": "0x0061a614", "tokens": ("CSPtrSet__Clear", "EBP-0x20"), "tags": {"sptrset", "conditional-cleanup"}},
    "0x005d17e0": {"scope": "0x0061a64c", "tokens": ("CSPtrSet__Clear", "EBP-0x1c"), "tags": {"sptrset", "stack-local"}},
    "0x005d17e8": {"scope": "0x0061a654", "tokens": ("CSPtrSet__Clear", "EBP-0x2c"), "tags": {"sptrset", "stack-local"}},
    "0x005d17f0": {"scope": "0x0061a644", "tokens": ("CSPtrSet__Clear", "EBP-0x30"), "tags": {"sptrset", "conditional-cleanup"}},
    "0x005d1820": {"scope": "0x0061a67c", "tokens": ("CSPtrSet__Clear", "EBP-0x2c"), "tags": {"sptrset", "stack-local"}},
    "0x005d1828": {"scope": "0x0061a684", "tokens": ("CSPtrSet__Clear", "EBP-0x1c"), "tags": {"sptrset", "stack-local"}},
}

COMMON_TAGS = {
    "static-reaudit",
    "unwind-continuation-wave744",
    "wave744-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "compiler-unwind",
    "scope-table",
}

COMMON_DOC_TOKENS = (
    "Wave744 unwind continuation",
    "unwind-continuation-wave744",
    "0x005d1610 Unwind@005d1610",
    "0x005d164b Unwind@005d164b",
    "0x005d1760 Unwind@005d1760",
    "0x005d17b0 Unwind@005d17b0",
    "0x005d1828 Unwind@005d1828",
    "0x005d1840 Unwind@005d1840",
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
        "pre-metadata.tsv": 26,
        "pre-tags.tsv": 26,
        "pre-xrefs.tsv": 26,
        "pre-instructions.tsv": 598,
        "pre-decompile/index.tsv": 26,
        "post-metadata.tsv": 26,
        "post-tags.tsv": 26,
        "post-xrefs.tsv": 26,
        "post-instructions.tsv": 598,
        "post-decompile/index.tsv": 26,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    for address, expected in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is None:
            continue
        name = f"Unwind@{address[2:]}"
        signature = f"void __cdecl {name}(void)"
        comment = row.get("comment", "")
        require(row.get("name") == name, f"name mismatch at {address}", failures)
        require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
        require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
        for token in ("Wave744 static read-back", "compiler-generated SEH unwind cleanup callback", expected["scope"], "Static retail Ghidra metadata/decompile/xref evidence only"):
            require(token in comment, f"missing comment token at {address}: {token}", failures)
        for token in expected["tokens"]:
            require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            required_tags = COMMON_TAGS | expected["tags"]
            require(required_tags.issubset(actual_tags), f"tags missing at {address}: {required_tags - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    xrefs = {normalize_address(row["target_addr"]): row for row in read_tsv(BASE / "post-xrefs.tsv")}
    for address, expected in TARGETS.items():
        row = xrefs.get(address)
        require(row is not None, f"missing xref for {address}", failures)
        if row is not None:
            require(normalize_address(row.get("from_addr", "")) == expected["scope"], f"xref scope mismatch at {address}", failures)
            require(row.get("ref_type") == "DATA", f"xref type mismatch at {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=26 renamed=0 would_rename=0 signature_updated=26 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=26 skipped=0 renamed=0 would_rename=0 signature_updated=26 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=26 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=26 found=26 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=26 missing=0",
        "post-xrefs.log": "Wrote 26 rows",
        "post-instructions.log": "Wrote 598 instruction rows",
        "post-decompile.log": "targets=26 dumped=26 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6098 commented_functions=4462",
        "queue-probe.log": "Commentless functions: 1636",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave744.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave744_queue_probe.log",
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
    require(quality["commentlessFunctionCount"] == 1636, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 1113, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 27, "param_N count mismatch", failures)
    high_signal = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(high_signal["address"] == "0x005d1840", "high-signal head mismatch", failures)
    require(high_signal["name"] == "Unwind@005d1840", "high-signal name mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 4462, "quality TSV commented count mismatch", failures)
    require(strict_clean == 4404, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x0042f220", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CSPtrSet__Clear", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 167381895 or backup.get("totalBytes") == 167381895.0, "backup byte count mismatch", failures)
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
        for token in COMMON_DOC_TOKENS:
            require(contains_token(text, token), f"missing doc token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    specialized = {
        MONITOR_DOC: ("Wave744 unwind continuation", "0x005d164b Unwind@005d164b", "0x005d16e0 Unwind@005d16e0"),
        CAMERA_DOC: ("Wave744 unwind continuation", "0x005d1610", "0x005d1740"),
        CANNON_DOC: ("Wave744 unwind continuation", "0x005d1760", "0x005d178c"),
        SPTRSET_DOC: ("Wave744 unwind continuation", "0x005d17b0", "0x005d1828"),
    }
    for path, tokens in specialized.items():
        text = read_text(path)
        for token in tokens:
            require(token in text, f"missing specialized doc token in {path.relative_to(ROOT)}: {token}", failures)

    package_text = read_text(PACKAGE_JSON)
    require("test:ghidra-unwind-continuation-wave744" in package_text, "missing npm script", failures)

    for path in (LEDGER, ATTEMPT_LOG):
        entries = read_jsonl(path)
        require(entries, f"empty jsonl: {path}", failures)
        last = entries[-1]
        require(last.get("task") == "Wave744 unwind continuation", f"last JSONL task mismatch in {path.name}", failures)
        notes = last.get("notes", "")
        for token in COMMON_DOC_TOKENS:
            require(contains_token(notes, token), f"missing JSONL token in {path.name}: {token}", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Run validation and exit nonzero on failure")
    parser.parse_args()

    failures: list[str] = []
    for check in (check_artifacts, check_logs, check_queue_and_backup, check_docs):
        try:
            check(failures)
        except Exception as exc:
            failures.append(f"{check.__name__}: {exc}")

    if failures:
        print("Wave744 unwind-continuation probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Wave744 unwind-continuation probe: PASS")
    print(f"Targets: {len(TARGETS)}")
    print("Post exports: metadata=26 tags=26 xrefs=26 instructions=598 decompile=26")
    print("Queue: total=6098 commented=4462 commentless=1636 undefined=1113 param_N=27 strict=4404")
    print(f"Backup: {BACKUP_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
