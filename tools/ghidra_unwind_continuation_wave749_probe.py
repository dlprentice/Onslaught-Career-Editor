#!/usr/bin/env python3
"""Validate Wave749 unwind-continuation read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave749-unwind-continuation"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_unwind_continuation_wave749_2026-05-22.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
DIVEBOMBER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DiveBomber.cpp" / "_index.md"
DROPSHIP_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Dropship.cpp" / "_index.md"
ENGINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "engine.cpp" / "_index.md"
EVENTMANAGER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "eventmanager.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260522-190133_post_wave749_unwind_continuation_verified"

TARGET_XREFS = {
    "0x005d2250": "0x0061b10c",
    "0x005d2266": "0x0061b114",
    "0x005d2290": "0x0061b13c",
    "0x005d2298": "0x0061b144",
    "0x005d22a3": "0x0061b14c",
    "0x005d22c0": "0x0061b174",
    "0x005d22e0": "0x0061b19c",
    "0x005d22f6": "0x0061b1a4",
    "0x005d230c": "0x0061b1ac",
    "0x005d2322": "0x0061b1b4",
    "0x005d2350": "0x0061b1dc",
    "0x005d2358": "0x0061b1e4",
    "0x005d2363": "0x0061b1ec",
    "0x005d2380": "0x0061b214",
    "0x005d2388": "0x0061b21c",
    "0x005d23a0": "0x0061b244",
    "0x005d23b9": "0x0061b24c",
    "0x005d23d2": "0x0061b254",
    "0x005d23eb": "0x0061b25c",
    "0x005d2404": "0x0061b264",
    "0x005d241d": "0x0061b26c",
    "0x005d2440": "0x0061b294",
    "0x005d2470": "0x0061b2bc",
    "0x005d2490": "0x0061b2e4",
    "0x005d24b0": "0x0061b30c",
}

COMMON_TAGS = {
    "static-reaudit",
    "unwind-continuation-wave749",
    "wave749-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "compiler-unwind",
    "scope-table",
}

CORE_ANCHORS = (
    "Wave749 unwind continuation",
    "unwind-continuation-wave749",
    "0x005d2250 Unwind@005d2250",
    "0x005d22e0 Unwind@005d22e0",
    "0x005d23a0 Unwind@005d23a0",
    "0x005d24b0 Unwind@005d24b0",
    "0x005d24e0 Unwind@005d24e0",
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
        "pre-helper-metadata.tsv": 10,
        "string-006289c0.tsv": 1,
        "string-00628a54.tsv": 1,
        "string-00628b40.tsv": 1,
        "string-00628d3c.tsv": 1,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    helper_names = {row["name"] for row in read_tsv(BASE / "pre-helper-metadata.tsv")}
    for name in (
        "OID__FreeObject_Callback",
        "CMonitor__Shutdown",
        "CGenericActiveReader__dtor",
        "CMonitor__Shutdown_Thunk",
        "CRT__SehDispatchWithScopeTable_Thunk_0055d731",
        "CParticleManager__RemoveFromGlobalList_Thunk",
        "CLine__SetBaseVtable_00426360",
        "CDXLandscape__DestroyResourceDescriptorArray_Thunk",
        "CRT__EhVectorDestructorIterator_WithUnwind",
        "CSPtrSet__Clear",
    ):
        require(name in helper_names, f"missing helper metadata row: {name}", failures)

    expected_strings = {
        "string-006289c0.tsv": r"C:\dev\ONSLAUGHT2\DiveBomber.cpp",
        "string-00628a54.tsv": r"C:\dev\ONSLAUGHT2\Dropship.cpp",
        "string-00628b40.tsv": r"C:\dev\ONSLAUGHT2\engine.cpp",
        "string-00628d3c.tsv": r"C:\dev\ONSLAUGHT2\eventmanager.cpp",
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
            for token in ("Wave749 static read-back", "compiler-generated SEH unwind", expected_scope, "Static retail Ghidra metadata/decompile/xref evidence only"):
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
        "quality-refresh.log": "total_functions=6098 commented_functions=4587",
        "queue-probe.log": "Commentless functions: 1511",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave749.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave749_queue_probe.log",
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
    require(quality["commentlessFunctionCount"] == 1511, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 988, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 27, "param_N count mismatch", failures)
    high_signal = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(high_signal["address"] == "0x005d24e0", "high-signal head mismatch", failures)
    require(high_signal["name"] == "Unwind@005d24e0", "high-signal name mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 4587, "quality TSV commented count mismatch", failures)
    require(strict_clean == 4529, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x0042f220", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CSPtrSet__Clear", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 167807879 or backup.get("totalBytes") == 167807879.0, "backup byte count mismatch", failures)
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
        DIVEBOMBER_DOC: ("Wave749", "unwind-continuation-wave749", "0x005d2250 Unwind@005d2250", "0x005d2266 Unwind@005d2266", BACKUP_PATH),
        DROPSHIP_DOC: ("Wave749", "unwind-continuation-wave749", "0x005d22e0 Unwind@005d22e0", "0x005d2350 Unwind@005d2350", "0x005d2388 Unwind@005d2388", BACKUP_PATH),
        ENGINE_DOC: ("Wave749", "unwind-continuation-wave749", "0x005d23a0 Unwind@005d23a0", "0x005d2440 Unwind@005d2440", "0x005d2470 Unwind@005d2470", BACKUP_PATH),
        EVENTMANAGER_DOC: ("Wave749", "unwind-continuation-wave749", "0x005d24b0 Unwind@005d24b0", "0x005d24e0 Unwind@005d24e0", BACKUP_PATH),
    }
    for path, tokens in function_docs.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(scripts.get("test:ghidra-unwind-continuation-wave749") == r"py -3 tools\ghidra_unwind_continuation_wave749_probe.py --check", "missing package script", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave749 unwind continuation" for row in ledger_rows), "missing Wave749 ledger row", failures)
    require(any(row.get("task") == "Wave749 unwind continuation" and row.get("attempt_id") == 20404 for row in attempts), "missing Wave749 attempt row", failures)


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
        print("Wave749 unwind-continuation probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave749 unwind-continuation probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
