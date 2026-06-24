#!/usr/bin/env python3
"""Validate Wave581 IScript vector/range Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave581-iscript-vector-range-005345d0"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_iscript_vector_range_wave581_2026-05-19.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
ISCRIPT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "IScript.cpp.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"

COMMON_TAGS = {
    "static-reaudit",
    "iscript-vector-range-wave581",
    "retail-binary-evidence",
    "mission-script",
    "iscript",
    "command-handler",
    "signature-corrected",
    "comment-hardened",
    "fixed-script-abi",
    "script-command-registry",
}

TARGETS = {
    "0x005345d0": {
        "name": "IScript__GetVectorLength",
        "signature": "void __stdcall IScript__GetVectorLength(void * script_args, void * unused_state, void * out_result)",
        "tags": COMMON_TAGS | {"vector-input", "float-result", "vector-length", "result-datatype"},
        "comment_tokens": ("GetVectorLength(vector)", "0x005e4ea4", "sqrt(x*x+y*y+z*z)"),
        "decompile_file": "005345d0_IScript__GetVectorLength.c",
        "decompile_tokens": ("script_args", "out_result", "SQRT", "PTR_CDataType__ScalarDeletingDestructor_005e4ea4"),
    },
    "0x005347b0": {
        "name": "IScript__CheckValueInRange",
        "signature": "void __stdcall IScript__CheckValueInRange(void * script_args, void * unused_state, void * out_result)",
        "tags": COMMON_TAGS | {"range-check", "float-input", "bool-result", "result-datatype"},
        "comment_tokens": ("CheckValueInRange(value,min,max)", "vtable slot +0x34", "ascending and descending bounds"),
        "decompile_file": "005347b0_IScript__CheckValueInRange.c",
        "decompile_tokens": ("script_args", "out_result", "CEventFunctionParam__vtable", "*(undefined1 *)(puVar2 + 1) = 1", "*(undefined1 *)(puVar2 + 1) = 0"),
    },
    "0x00534b80": {
        "name": "IScript__GetVectorX",
        "signature": "void __stdcall IScript__GetVectorX(void * script_args, void * unused_state, void * out_result)",
        "tags": COMMON_TAGS | {"vector-input", "float-result", "vector-component", "component-x", "result-datatype"},
        "comment_tokens": ("GetVectorX(vector)", "component offset +0", "0x005e4ea4"),
        "decompile_file": "00534b80_IScript__GetVectorX.c",
        "decompile_tokens": ("script_args", "out_result", "PTR_CDataType__ScalarDeletingDestructor_005e4ea4", "puVar2[1] = uVar1"),
    },
    "0x00534c10": {
        "name": "IScript__GetVectorY",
        "signature": "void __stdcall IScript__GetVectorY(void * script_args, void * unused_state, void * out_result)",
        "tags": COMMON_TAGS | {"vector-input", "float-result", "vector-component", "component-y", "result-datatype"},
        "comment_tokens": ("GetVectorY(vector)", "component offset +4", "0x005e4ea4"),
        "decompile_file": "00534c10_IScript__GetVectorY.c",
        "decompile_tokens": ("script_args", "out_result", "PTR_CDataType__ScalarDeletingDestructor_005e4ea4", "*(undefined4 *)(iVar3 + 4)"),
    },
    "0x00534ca0": {
        "name": "IScript__GetVectorZ",
        "signature": "void __stdcall IScript__GetVectorZ(void * script_args, void * unused_state, void * out_result)",
        "tags": COMMON_TAGS | {"vector-input", "float-result", "vector-component", "component-z", "result-datatype"},
        "comment_tokens": ("GetVectorZ(vector)", "component offset +8", "0x005e4ea4"),
        "decompile_file": "00534ca0_IScript__GetVectorZ.c",
        "decompile_tokens": ("script_args", "out_result", "PTR_CDataType__ScalarDeletingDestructor_005e4ea4", "*(undefined4 *)(iVar3 + 8)"),
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
        BASE / "wave581_apply_dry.log",
        {"updated": 0, "skipped": 5, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "wave581_apply.log",
        {"updated": 5, "skipped": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "wave581_apply_final_dry.log",
        {"updated": 0, "skipped": 5, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )

    expected_counts = {
        "post_metadata.tsv": 5,
        "post_tags.tsv": 5,
        "post_xrefs.tsv": 5,
        "post_target_instructions.tsv": 3545,
        "post_decompile/index.tsv": 5,
        "post_vtables.tsv": 24,
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

    require_tokens("xrefs", xrefs, ("ScriptCommandRegistry__InitBuiltins", "IScript__GetVectorLength", "IScript__GetVectorZ"), failures)
    require_tokens("instructions", instructions, ("RET\t0xc", "0x5e4ea4", "FSQRT", "0x2f3", "0x2fa", "0x2ff"), failures)
    require_tokens("vtables", vtables, ("005e4ea4", "CFloatDataType__Add", "005e4d50", "CBoolDataType__Assign"), failures)

    overclaim_tokens = (
        "runtime behavior proven",
        "runtime mission-script behavior proven",
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
            actual_tags = set(filter(None, tag_row["tags"].split(";")))
            missing = sorted(spec["tags"] - actual_tags)
            if missing:
                failures.append(f"{address} missing tags: {missing}")

        decomp_row = decomp_index.get(address)
        if decomp_row is None:
            failures.append(f"{address} missing from post_decompile/index.tsv")
        elif decomp_row["status"] != "OK":
            failures.append(f"{address} decompile status is {decomp_row['status']}")
        decomp_text = read_text(BASE / "post_decompile" / spec["decompile_file"])
        require_tokens(f"{address} decompile", decomp_text, spec["decompile_tokens"], failures)

    queue = json.loads(read_text(QUEUE_JSON))
    if queue.get("status") != "PASS":
        failures.append("queue status is not PASS")
    signals = queue.get("qualitySignals", {})
    expected_signals = {
        "commentlessFunctionCount": 3149,
        "undefinedSignatureCount": 1413,
        "paramSignatureCount": 1127,
    }
    for key, expected in expected_signals.items():
        actual = signals.get(key)
        if actual != expected:
            failures.append(f"queue {key} mismatch: {actual} != {expected}")
    head = queue.get("priorityQueues", {}).get("commentlessHighSignal", [{}])[0]
    if head.get("address") != "0x00534fb0" or head.get("name") != "IScript__SetThingValueViaVFunc198_FromArg":
        failures.append(f"unexpected next queue head: {head}")

    backup = json.loads(read_text(BASE / "wave581_backup_summary.json"))
    if backup.get("status") != "PASS":
        failures.append("backup status is not PASS")
    if backup.get("fileCount") != 19:
        failures.append(f"backup fileCount mismatch: {backup.get('fileCount')} != 19")
    if int(backup.get("totalBytes", 0)) != 160500615:
        failures.append(f"backup totalBytes mismatch: {backup.get('totalBytes')} != 160500615")
    if backup.get("diffCount") != 0:
        failures.append(f"backup diffCount mismatch: {backup.get('diffCount')} != 0")
    if backup.get("manifestSha256") != "66EAC6D25839E7626D5F27E6A496E682085E0169D2D38E22BAD8E61E00E4F687":
        failures.append("backup manifest hash mismatch")

    require_doc_tokens(
        PUBLIC_NOTE,
        (
            "Wave581 IScript Vector/Range Static Read-Back",
            "IScript__GetVectorLength",
            "IScript__CheckValueInRange",
            "2944/6093 = 48.32%",
            "runtime mission-script behavior remains unproven",
            "script corpus coverage remains unproven",
        ),
        failures,
    )
    require_doc_tokens(
        ISCRIPT_DOC,
        (
            "Wave581 Static Read-Back",
            "IScript__GetVectorZ",
            "0x00534fb0",
        ),
        failures,
    )
    require_doc_tokens(
        FUNCTION_INDEX,
        (
            "Wave581",
            "IScript__GetVectorLength",
            "0x00534fb0 IScript__SetThingValueViaVFunc198_FromArg",
        ),
        failures,
    )
    require_doc_tokens(
        GHIDRA_REFERENCE,
        (
            "MissionScript IScript Vector/Range Handlers",
            "Wave581",
            "CheckValueInRange(value,min,max)",
            "2944/6093 = 48.32%",
        ),
        failures,
    )
    require_doc_tokens(
        CAMPAIGN,
        (
            "Wave 581: IScript Vector/Range Command Handlers",
            "3545",
            "strict clean-signature proxy `2895/6093 = 47.51%`",
        ),
        failures,
    )
    require_doc_tokens(BACKLOG, ("Ghidra IScript vector/range Wave581", "160500615", "66EAC6D2"), failures)
    require_tokens("ledger", read_text(LEDGER), ("iscript_vector_range Wave581", "0x005345d0,0x005347b0", "strict clean-signature proxy 2895/6093 = 47.51%"), failures)
    require_tokens("attempt_log", read_text(ATTEMPT_LOG), ('"attempt_id":20236', "iscript_vector_range Wave581", "Post-Wave581 queue telemetry"), failures)

    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Run validation checks")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
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
        print(f"Wave581 IScript vector/range probe: {result['status']}")
        for failure in failures:
            print(f"- {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
