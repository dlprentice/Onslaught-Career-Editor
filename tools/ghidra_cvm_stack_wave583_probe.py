#!/usr/bin/env python3
"""Validate Wave583 CVM stack-cleanup Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave583-cvm-stack-00535330"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cvm_stack_wave583_2026-05-19.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
SCRIPT_OBJECT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "ScriptObjectCode.cpp.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
BACKUP_SUMMARY = BASE / "wave583_backup_summary.json"

COMMON_TAGS = {
    "static-reaudit",
    "cvm-stack-wave583",
    "retail-binary-evidence",
    "mission-script",
    "cvm",
    "script-vm",
    "signature-corrected",
    "comment-hardened",
}

TARGETS = {
    "0x00535330": {
        "name": "CVM__ScalarDeletingDestructor",
        "signature": "void * __thiscall CVM__ScalarDeletingDestructor(void * this, byte flags)",
        "tags": COMMON_TAGS | {"scalar-deleting-destructor", "vtable-slot-1", "delete-flag", "ret-04"},
        "comment_tokens": ("Vtable slot read-back at 0x005e4f20", "flags&1", "RET 0x4"),
        "decompile_file": "00535330_CVM__ScalarDeletingDestructor.c",
        "decompile_tokens": ("CVM__Destructor(this)", "flags & 1", "CDXMemoryManager__Free"),
    },
    "0x00535350": {
        "name": "CVM__Destructor",
        "signature": "void __thiscall CVM__Destructor(void * this)",
        "tags": COMMON_TAGS | {"destructor-body", "clear-stack", "monitor-shutdown", "thiscall"},
        "comment_tokens": ("CScriptObjectCode__ClearStack(this+0x0c)", "CMonitor__Shutdown(this)", "0x005398c5"),
        "decompile_file": "00535350_CVM__Destructor.c",
        "decompile_tokens": ("CScriptObjectCode__ClearStack", "CMonitor__Shutdown(this)", "ExceptionList"),
    },
}


def normalize_address(address: str) -> str:
    value = address.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def read_tsv(path: Path, key: str = "address") -> dict[str, dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    return {normalize_address(row[key]): row for row in rows}


def row_count(path: Path) -> int:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8", newline="") as handle:
        return sum(1 for _ in csv.DictReader(handle, delimiter="\t"))


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")


def require_tokens(label: str, text: str, tokens: tuple[str, ...] | set[str], failures: list[str]) -> None:
    for token in tokens:
        if token not in text:
            failures.append(f"{label} missing token: {token}")


def require_log_summary(path: Path, expected: dict[str, int], failures: list[str]) -> None:
    text = read_text(path)
    match = re.search(r"SUMMARY\s+([^\r\n]+)", text)
    if not match:
        failures.append(f"{path.name} missing SUMMARY")
        return
    values: dict[str, int] = {}
    for key, value in re.findall(r"([a-z_]+)=([0-9]+)", match.group(1)):
        values[key] = int(value)
    for key, expected_value in expected.items():
        actual = values.get(key)
        if actual != expected_value:
            failures.append(f"{path.name} {key} mismatch: {actual} != {expected_value}")
    if "REPORT: Save succeeded" not in text:
        failures.append(f"{path.name} missing save-success report")
    for bad_token in ("FAIL:", "LockException", "Read-back mismatch", "Function not found", "Input file not found"):
        if bad_token in text:
            failures.append(f"{path.name} contains {bad_token}")


def require_doc_tokens(path: Path, tokens: tuple[str, ...], failures: list[str]) -> None:
    try:
        text = read_text(path)
    except FileNotFoundError:
        failures.append(f"missing doc: {path}")
        return
    require_tokens(str(path.relative_to(ROOT)), text, tokens, failures)


def run_check() -> list[str]:
    failures: list[str] = []

    require_log_summary(
        BASE / "wave583_apply_dry.log",
        {"updated": 0, "skipped": 2, "renamed": 0, "would_rename": 2, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "wave583_apply.log",
        {"updated": 2, "skipped": 0, "renamed": 2, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "wave583_apply_final_dry.log",
        {"updated": 0, "skipped": 2, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )

    expected_counts = {
        "post_metadata.tsv": 2,
        "post_tags.tsv": 2,
        "post_xrefs.tsv": 3,
        "post_instructions.tsv": 242,
        "post_decompile/index.tsv": 2,
        "post_vtables.tsv": 32,
    }
    for relative_path, expected in expected_counts.items():
        actual = row_count(BASE / relative_path)
        if actual != expected:
            failures.append(f"{relative_path} row count mismatch: {actual} != {expected}")

    metadata = read_tsv(BASE / "post_metadata.tsv")
    tags = read_tsv(BASE / "post_tags.tsv")
    decomp_index = read_tsv(BASE / "post_decompile" / "index.tsv")
    xrefs = read_text(BASE / "post_xrefs.tsv")
    instructions = read_text(BASE / "post_instructions.tsv")
    vtables = read_text(BASE / "post_vtables.tsv")

    require_tokens(
        "xrefs",
        xrefs,
        ("005e4f20", "CVM__ScalarDeletingDestructor", "00535333", "005398c5", "CVM__Destructor"),
        failures,
    )
    require_tokens(
        "instructions",
        instructions,
        (
            "CALL\t0x00535350",
            "TEST\tbyte ptr [ESP + 0x8], 0x1",
            "CALL\t0x00549220",
            "RET\t0x4",
            "LEA\tECX, [ESI + 0xc]",
            "CALL\t0x005393e0",
            "CALL\t0x004bac40",
            "RET\t\tc3",
        ),
        failures,
    )
    require_tokens(
        "vtables",
        vtables,
        ("005e4f20", "CVM__ScalarDeletingDestructor", "005e4f54", "CScriptObjectCode__scalar_deleting_dtor"),
        failures,
    )

    overclaim_tokens = (
        "runtime behavior proven",
        "runtime mission-script behavior proven",
        "source identity proven",
        "source class identity proven",
        "rebuild parity proven",
        "fully RE'ed",
        "fully REed",
    )
    for address, spec in TARGETS.items():
        row = metadata.get(address)
        if row is None:
            failures.append(f"{address} missing from post_metadata.tsv")
            continue
        if row["status"] != "OK":
            failures.append(f"{address} metadata status is {row['status']}")
        if row["name"] != spec["name"]:
            failures.append(f"{address} name mismatch: {row['name']} != {spec['name']}")
        if row["signature"] != spec["signature"]:
            failures.append(f"{address} signature mismatch: {row['signature']} != {spec['signature']}")
        require_tokens(f"{address} comment", row["comment"], spec["comment_tokens"], failures)
        for bad_token in overclaim_tokens:
            if bad_token in row["comment"]:
                failures.append(f"{address} comment overclaims: {bad_token}")

        tag_row = tags.get(address)
        if tag_row is None:
            failures.append(f"{address} missing from post_tags.tsv")
        else:
            actual_tags = set(filter(None, tag_row["tags"].split(";")))
            missing = sorted(spec["tags"] - actual_tags)
            if missing:
                failures.append(f"{address} missing tags: {missing}")

        decomp_row = decomp_index.get(address)
        if decomp_row is None or decomp_row["status"] != "OK":
            failures.append(f"{address} missing/failed decompile row")
        else:
            require_tokens(
                f"{address} decompile",
                read_text(BASE / "post_decompile" / spec["decompile_file"]),
                spec["decompile_tokens"],
                failures,
            )

    queue = json.loads(read_text(QUEUE_JSON))
    if queue.get("status") != "PASS":
        failures.append("queue status is not PASS")
    if queue.get("totalFunctions") != 6093:
        failures.append(f"queue totalFunctions mismatch: {queue.get('totalFunctions')} != 6093")
    signals = queue.get("qualitySignals", {})
    for key, expected in {
        "commentlessFunctionCount": 3141,
        "undefinedSignatureCount": 1413,
        "paramSignatureCount": 1119,
    }.items():
        actual = signals.get(key)
        if actual != expected:
            failures.append(f"queue {key} mismatch: {actual} != {expected}")
    head = queue.get("priorityQueues", {}).get("commentlessHighSignal", [{}])[0]
    if head.get("address") != "0x00535670" or head.get("name") != "IScript__GetThingName":
        failures.append(f"unexpected next queue head: {head}")

    backup = json.loads(read_text(BACKUP_SUMMARY))
    if backup.get("status") != "PASS" or backup.get("diffCount") != 0:
        failures.append(f"backup summary failed: {backup}")
    if backup.get("sourceFileCount") != 19 or backup.get("destinationFileCount") != 19:
        failures.append(f"backup file count mismatch: {backup}")
    if int(backup.get("sourceTotalBytes", 0)) != 160598919:
        failures.append(f"backup source bytes mismatch: {backup.get('sourceTotalBytes')} != 160598919")
    if int(backup.get("destinationTotalBytes", 0)) != 160598919:
        failures.append(f"backup destination bytes mismatch: {backup.get('destinationTotalBytes')} != 160598919")
    if backup.get("sourceManifestSha256") != backup.get("destinationManifestSha256"):
        failures.append("backup manifest hashes differ")
    require_tokens(
        "backup destination",
        backup.get("destinationRoot", ""),
        ("post_wave583_cvm_stack_verified",),
        failures,
    )

    require_doc_tokens(
        PUBLIC_NOTE,
        (
            "Wave583",
            "CVM stack cleanup static read-back",
            "CVM__ScalarDeletingDestructor",
            "runtime mission-script behavior remains unproven",
            "exact CVM source class identity/layout remains unproven",
        ),
        failures,
    )
    require_doc_tokens(
        FUNCTION_INDEX,
        (
            "Wave583 CVM stack-cleanup destructor hardening",
            "Post-Wave583 queue telemetry is `6093` functions, `2952` commented, `3141` commentless, `1413` exact-undefined signatures, and `1119` `param_N` signatures.",
            "0x00535670 IScript__GetThingName",
        ),
        failures,
    )
    require_doc_tokens(
        SCRIPT_OBJECT_DOC,
        (
            "## Wave583 Static Read-Back",
            "CVM__ScalarDeletingDestructor",
            "CScriptObjectCode__ClearStack(this+0x0c)",
            "0x005398c5",
        ),
        failures,
    )
    require_doc_tokens(
        GHIDRA_REFERENCE,
        (
            "Wave583 CVM stack cleanup destructors",
            "CVM__ScalarDeletingDestructor",
            "CVM__Destructor",
            "2952/6093 = 48.45%",
        ),
        failures,
    )
    require_doc_tokens(
        CAMPAIGN,
        (
            "Wave 583: CVM Stack Cleanup Destructors",
            "post_wave583_cvm_stack_verified",
            "strict clean-signature proxy `2903/6093 = 47.64%`",
        ),
        failures,
    )
    require_doc_tokens(BACKLOG, ("0x00535330,0x00535350", "Wave583"), failures)
    require_doc_tokens(LEDGER, ("Ghidra CVM stack Wave583", "post_wave583_cvm_stack_verified"), failures)
    require_doc_tokens(ATTEMPT_LOG, ("Ghidra CVM stack Wave583", '"attempt_id":20238'), failures)

    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Return non-zero on failure")
    parser.add_argument("--json", action="store_true", help="Emit JSON summary")
    args = parser.parse_args()

    failures = run_check()
    result = {
        "status": "PASS" if not failures else "FAIL",
        "failureCount": len(failures),
        "failures": failures,
    }
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("Wave583 CVM stack cleanup probe:", result["status"])
        for failure in failures:
            print(f"- {failure}")
    return 1 if args.check and failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
