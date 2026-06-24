#!/usr/bin/env python3
"""Validate Wave577 CEventFunction Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave577-eventfunction-tail-0052f9a0"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_eventfunction_tail_wave577_2026-05-19.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
EVENTFUNCTION_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "EventFunction.cpp.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"

COMMON_TAGS = {
    "static-reaudit",
    "eventfunction-tail-wave577",
    "retail-binary-evidence",
    "signature-corrected",
    "comment-hardened",
    "mission-script",
    "event-function",
}

TARGETS = {
    "0x0052f9a0": {
        "raw": "0052f9a0",
        "name": "CEventFunction__Destructor",
        "signature": "void __thiscall CEventFunction__Destructor(void * this)",
        "tags": COMMON_TAGS | {"destructor", "parameter-list-cleanup", "monitor-cleanup"},
        "comment_tokens": ("0x005e4ef8", "this+0x0c", "CMonitor__Shutdown"),
        "decompile_file": "0052f9a0_CEventFunction__Destructor.c",
        "decompile_tokens": ("CSPtrSet__Clear", "CMonitor__Shutdown", "DAT_009c3df0"),
    },
    "0x0052fa50": {
        "raw": "0052fa50",
        "name": "CEventFunction__ScalarDeletingDestructor",
        "signature": "void * __thiscall CEventFunction__ScalarDeletingDestructor(void * this, byte flags)",
        "tags": COMMON_TAGS | {"destructor", "scalar-deleting-destructor", "vtable-slot"},
        "comment_tokens": ("0x005e4efc", "RET 0x4", "flags&1"),
        "decompile_file": "0052fa50_CEventFunction__ScalarDeletingDestructor.c",
        "decompile_tokens": ("CEventFunction__Destructor", "flags & 1", "CDXMemoryManager__Free"),
    },
    "0x0052fa70": {
        "raw": "0052fa70",
        "name": "CEventFunction__CEventFunction",
        "signature": "void * __thiscall CEventFunction__CEventFunction(void * this, void * script_object_code, void * bytecode_reader)",
        "tags": COMMON_TAGS | {"constructor", "bytecode-read", "symbol-table", "parameter-list"},
        "comment_tokens": ("RET 0x8", "0x005e4ef8", "EventFunction.cpp line 0x40"),
        "decompile_file": "0052fa70_CEventFunction__CEventFunction.c",
        "decompile_tokens": ("CDXMemBuffer__Read", "CScriptObjectCode__GetInstruction", "s_FATAL_ERROR__Event_Function_was_e_0064cd38"),
    },
    "0x0052fbb0": {
        "raw": "0052fbb0",
        "name": "CEventFunction__Clone",
        "signature": "void * __thiscall CEventFunction__Clone(void * this, void * cloned_script_object_code)",
        "tags": COMMON_TAGS | {"clone", "symbol-table", "string-match", "parameter-list"},
        "comment_tokens": ("RET 0x4", "EventFunction.cpp line 0x4e", "line-0x1b wrapper"),
        "decompile_file": "0052fbb0_CEventFunction__Clone.c",
        "decompile_tokens": ("OID__AllocObject(0x20", "CScriptObjectCode__GetInstruction", "s_FATAL_ERROR_can_t_find_event_str_0064cd6c"),
    },
    "0x0052fda0": {
        "raw": "0052fda0",
        "name": "CEventFunction__Execute",
        "signature": "void __thiscall CEventFunction__Execute(void * this)",
        "tags": COMMON_TAGS | {"execute", "event-dispatch", "parameter-wrapper"},
        "comment_tokens": ("0x005e4d50", "local 10-slot array", "CScriptObjectCode__CallEventDirect"),
        "decompile_file": "0052fda0_CEventFunction__Execute.c",
        "decompile_tokens": ("CEventFunctionParam__vtable", "CScriptObjectCode__CallEventDirect", "OID__AllocObject(8"),
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
        BASE / "wave577_apply_dry.log",
        {"updated": 0, "skipped": 5, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "wave577_apply.log",
        {"updated": 5, "skipped": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "wave577_apply_final_dry.log",
        {"updated": 0, "skipped": 5, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )

    expected_counts = {
        "post_metadata.tsv": 5,
        "post_tags.tsv": 5,
        "post_xrefs.tsv": 6,
        "post_target_instructions.tsv": 1305,
        "post_decompile/index.tsv": 5,
        "post_vtables.tsv": 144,
    }
    for relative_path, expected in expected_counts.items():
        actual = row_count(BASE / relative_path)
        if actual != expected:
            failures.append(f"{relative_path} row count mismatch: {actual} != {expected}")

    metadata = read_tsv(BASE / "post_metadata.tsv")
    tags = read_tsv(BASE / "post_tags.tsv")
    decomp_index = read_tsv(BASE / "post_decompile" / "index.tsv")
    xrefs = read_text(BASE / "post_xrefs.tsv")
    instructions = read_text(BASE / "post_target_instructions.tsv")
    vtables = read_text(BASE / "post_vtables.tsv")

    require_tokens(
        "eventfunction vtables",
        vtables,
        ("005e4efc", "CEventFunction__ScalarDeletingDestructor", "005e4d50", "CDataType__ScalarDeletingDestructor"),
        failures,
    )
    require_tokens(
        "xrefs",
        xrefs,
        ("CScriptObjectCode__CScriptObjectCode", "CScriptObjectCode__Clone", "CScriptEventNB__PostEvent", "CScriptEventNB__HandleEventMessage"),
        failures,
    )
    require_tokens(
        "instructions",
        instructions,
        ("RET\t0x8", "RET\t0x4", "0x00539a60", "0x64cce0"),
        failures,
    )

    overclaim_tokens = (
        "runtime behavior proven",
        "runtime event behavior proven",
        "source identity proven",
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
            present = set(filter(None, tag_row["tags"].split(";")))
            missing = spec["tags"] - present
            if missing:
                failures.append(f"{address} missing tags: {sorted(missing)}")

        decomp_row = decomp_index.get(address)
        if decomp_row is None or decomp_row.get("status") != "OK":
            failures.append(f"{address} decompile index missing or not OK")
        decompile_text = read_text(BASE / "post_decompile" / spec["decompile_file"])
        require_tokens(f"{address} decompile", decompile_text, spec["decompile_tokens"], failures)

    queue = json.loads(read_text(QUEUE_JSON))
    if queue.get("totalFunctions") != 6093:
        failures.append(f"queue totalFunctions mismatch: {queue.get('totalFunctions')}")
    quality = queue.get("qualitySignals", {})
    expected_quality = {
        "commentlessFunctionCount": 3171,
        "undefinedSignatureCount": 1425,
        "paramSignatureCount": 1139,
    }
    for key, expected in expected_quality.items():
        if quality.get(key) != expected:
            failures.append(f"queue {key} mismatch: {quality.get(key)} != {expected}")
    head = queue.get("priorityQueues", {}).get("commentlessHighSignal", [{}])[0]
    if head.get("address") != "0x005333b0":
        failures.append(f"queue head mismatch: {head.get('address')} != 0x005333b0")

    backup = json.loads(read_text(BASE / "wave577_backup_summary.json"))
    if backup.get("status") != "PASS" or backup.get("diffCount") != 0:
        failures.append(f"backup summary not PASS: {backup}")

    require_doc_tokens(
        PUBLIC_NOTE,
        (
            "Wave577 CEventFunction Tail Static Ghidra Readiness",
            "0x0052f9a0",
            "0x005333b0 CMonitor__ctor_like_005333b0",
            "runtime event behavior remains unproven",
        ),
        failures,
    )
    require_doc_tokens(
        EVENTFUNCTION_DOC,
        (
            "Wave577 static read-back",
            "void * __thiscall CEventFunction__CEventFunction",
            "local 10-slot array",
            "runtime event behavior remains unproven",
        ),
        failures,
    )
    require_doc_tokens(FUNCTION_INDEX, ("Wave577", "CEventFunction", "0x005333b0"), failures)
    require_doc_tokens(GHIDRA_REFERENCE, ("Wave577", "CEventFunction", "event dispatch"), failures)
    require_doc_tokens(CAMPAIGN, ("Wave577", "2922", "3171", "1425", "0x005333b0"), failures)
    require_doc_tokens(BACKLOG, ("0x0052f9a0,0x0052fa50,0x0052fa70,0x0052fbb0,0x0052fda0", "Wave577"), failures)
    require_doc_tokens(LEDGER, ("wave577", "eventfunction_tail", "0x0052fda0"), failures)

    return failures


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if not args.check:
        parser.error("expected --check")

    failures = run_check()
    result = {"status": "PASS" if not failures else "FAIL", "failureCount": len(failures), "failures": failures}
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Wave577 eventfunction tail probe: {result['status']}")
        for failure in failures:
            print(f"- {failure}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
