#!/usr/bin/env python3
"""Validate Wave745 unwind-continuation read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave745-unwind-continuation"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_unwind_continuation_wave745_2026-05-22.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
CARRIER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Carrier.cpp" / "_index.md"
CARVER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Carver.cpp.md"
CHUNKER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "chunker.cpp" / "_index.md"
COMPONENT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Component.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260522-170426_post_wave745_unwind_continuation_verified"

TARGETS = {
    "0x005d1840": {"scope": "0x0061a6ac", "tokens": ("Carrier.cpp", "line 0x1a", "memtype 0x17"), "tags": {"carrier", "carrier-cpp", "free-object"}},
    "0x005d1856": {"scope": "0x0061a6b4", "tokens": ("Carrier.cpp", "line 0x1b", "memtype 0x16"), "tags": {"carrier", "carrier-cpp", "free-object"}},
    "0x005d1880": {"scope": "0x0061a6dc", "tokens": ("CMonitor__Shutdown", "EBP-0x10"), "tags": {"carrier", "monitor", "shutdown"}},
    "0x005d1888": {"scope": "0x0061a6e4", "tokens": ("CGenericActiveReader__dtor", "0xc"), "tags": {"carrier", "active-reader", "embedded-reader"}},
    "0x005d1893": {"scope": "0x0061a6ec", "tokens": ("CGenericActiveReader__dtor", "0x24"), "tags": {"carrier", "active-reader", "embedded-reader"}},
    "0x005d18b0": {"scope": "0x0061a714", "tokens": ("Carver.cpp", "line 0x16", "memtype 0x17"), "tags": {"carver", "carver-cpp", "free-object"}},
    "0x005d18c6": {"scope": "0x0061a71c", "tokens": ("Carver.cpp", "line 0x17", "memtype 0x16"), "tags": {"carver", "carver-cpp", "free-object"}},
    "0x005d18f0": {"scope": "0x0061a744", "tokens": ("CMonitor__Shutdown", "EBP-0x10"), "tags": {"carver", "monitor", "shutdown"}},
    "0x005d18f8": {"scope": "0x0061a74c", "tokens": ("CGenericActiveReader__dtor", "0xc"), "tags": {"carver", "active-reader", "embedded-reader"}},
    "0x005d1903": {"scope": "0x0061a754", "tokens": ("CGenericActiveReader__dtor", "0x24"), "tags": {"carver", "active-reader", "embedded-reader"}},
    "0x005d1920": {"scope": "0x0061a77c", "tokens": ("CMonitor__Shutdown_Thunk", "EBP-0x10"), "tags": {"carver", "monitor", "shutdown", "thunk"}},
    "0x005d1940": {"scope": "0x0061a7a4", "tokens": ("chunker.cpp", "line 0x62", "memtype 0x11"), "tags": {"chunker", "chunker-cpp", "free-object"}},
    "0x005d1960": {"scope": "0x0061a7cc", "tokens": ("CMonitor__Shutdown", "EBP-0x468"), "tags": {"chunker", "monitor", "shutdown", "stack-local"}},
    "0x005d196b": {"scope": "0x0061a7d4", "tokens": ("CDXLandscape__DestroyResourceDescriptorArray_Thunk", "EBP-0x434"), "tags": {"chunker", "cdxlandscape", "resource-descriptor", "stack-local"}},
    "0x005d1980": {"scope": "0x0061a7fc", "tokens": ("CMonitor__Shutdown", "EBP-0x10"), "tags": {"chunker", "monitor", "shutdown"}},
    "0x005d19a0": {"scope": "0x0061a824", "tokens": ("CMonitor__Shutdown", "EBP-0x10"), "tags": {"chunker", "monitor", "shutdown"}},
    "0x005d19c0": {"scope": "0x0061a84c", "tokens": ("CLine__SetBaseVtable_00426360", "EBP-0x40"), "tags": {"chunker", "line-helper", "stack-local"}},
    "0x005d19e0": {"scope": "0x0061a874", "tokens": ("Component.cpp", "line 0x4d", "memtype 0x1b"), "tags": {"component", "component-cpp", "free-object"}},
    "0x005d1a00": {"scope": "0x0061a89c", "tokens": ("Component.cpp", "line 0x53", "memtype 0x17"), "tags": {"component", "component-cpp", "free-object"}},
    "0x005d1a20": {"scope": "0x0061a8c4", "tokens": ("Component.cpp", "line 0x5c", "memtype 0x16"), "tags": {"component", "component-cpp", "free-object"}},
    "0x005d1a36": {"scope": "0x0061a8cc", "tokens": ("Component.cpp", "line 0x5e", "memtype 0x16"), "tags": {"component", "component-cpp", "free-object"}},
    "0x005d1a4c": {"scope": "0x0061a8d4", "tokens": ("Component.cpp", "line 0x60", "memtype 0x16"), "tags": {"component", "component-cpp", "free-object"}},
    "0x005d1a62": {"scope": "0x0061a8dc", "tokens": ("Component.cpp", "line 0x63", "memtype 0x16"), "tags": {"component", "component-cpp", "free-object"}},
    "0x005d1a90": {"scope": "0x0061a904", "tokens": ("CMonitor__Shutdown", "EBP-0x10"), "tags": {"component", "monitor", "shutdown"}},
    "0x005d1a98": {"scope": "0x0061a90c", "tokens": ("CGenericActiveReader__dtor", "0xc"), "tags": {"component", "active-reader", "embedded-reader"}},
}

COMMON_TAGS = {
    "static-reaudit",
    "unwind-continuation-wave745",
    "wave745-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "compiler-unwind",
    "scope-table",
}

COMMON_DOC_TOKENS = (
    "Wave745 unwind continuation",
    "unwind-continuation-wave745",
    "0x005d1840 Unwind@005d1840",
    "0x005d18b0 Unwind@005d18b0",
    "0x005d1940 Unwind@005d1940",
    "0x005d196b Unwind@005d196b",
    "0x005d19e0 Unwind@005d19e0",
    "0x005d1a98 Unwind@005d1a98",
    "0x005d1aa3 Unwind@005d1aa3",
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
        "pre-instructions.tsv": 575,
        "pre-decompile/index.tsv": 25,
        "post-metadata.tsv": 25,
        "post-tags.tsv": 25,
        "post-xrefs.tsv": 25,
        "post-instructions.tsv": 575,
        "post-decompile/index.tsv": 25,
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
        for token in ("Wave745 static read-back", "compiler-generated SEH unwind cleanup callback", expected["scope"], "Static retail Ghidra metadata/decompile/xref evidence only"):
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
        "apply-dry.log": "SUMMARY: updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=25 found=25 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=25 missing=0",
        "post-xrefs.log": "Wrote 25 rows",
        "post-instructions.log": "Wrote 575 instruction rows",
        "post-decompile.log": "targets=25 dumped=25 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6098 commented_functions=4487",
        "queue-probe.log": "Commentless functions: 1611",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave745.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave745_queue_probe.log",
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
    require(quality["commentlessFunctionCount"] == 1611, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 1088, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 27, "param_N count mismatch", failures)
    high_signal = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(high_signal["address"] == "0x005d1aa3", "high-signal head mismatch", failures)
    require(high_signal["name"] == "Unwind@005d1aa3", "high-signal name mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 4487, "quality TSV commented count mismatch", failures)
    require(strict_clean == 4429, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x0042f220", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CSPtrSet__Clear", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 167447431 or backup.get("totalBytes") == 167447431.0, "backup byte count mismatch", failures)
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
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    function_docs = {
        CARRIER_DOC: ("Wave745 unwind continuation", "unwind-continuation-wave745", "0x005d1840 Unwind@005d1840", "0x005d1893 Unwind@005d1893", "0x005d1aa3 Unwind@005d1aa3", BACKUP_PATH),
        CARVER_DOC: ("Wave745", "unwind-continuation-wave745", "0x005d18b0 Unwind@005d18b0", "0x005d1920 Unwind@005d1920", "0x005d1aa3 Unwind@005d1aa3", BACKUP_PATH),
        CHUNKER_DOC: ("Wave745", "unwind-continuation-wave745", "0x005d1940", "0x005d196b", "0x005d19c0", "0x005d1aa3 Unwind@005d1aa3", BACKUP_PATH),
        COMPONENT_DOC: ("Wave745 unwind continuation", "unwind-continuation-wave745", "0x005d19e0 Unwind@005d19e0", "0x005d1a98 Unwind@005d1a98", "0x005d1aa3 Unwind@005d1aa3", BACKUP_PATH),
    }
    for path, tokens in function_docs.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(scripts.get("test:ghidra-unwind-continuation-wave745") == r"py -3 tools\ghidra_unwind_continuation_wave745_probe.py --check", "missing package script", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave745 unwind continuation" for row in ledger_rows), "missing Wave745 ledger row", failures)
    require(any(row.get("task") == "Wave745 unwind continuation" and row.get("attempt_id") == 20400 for row in attempts), "missing Wave745 attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    args = parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs(failures)
    check_queue_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave745 unwind-continuation probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave745 unwind-continuation probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
