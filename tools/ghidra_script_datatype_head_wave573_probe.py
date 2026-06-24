#!/usr/bin/env python3
"""Validate Wave573 MissionScript/DataType Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave573-script-datatype-head-0052d040"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_script_datatype_head_wave573_2026-05-19.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
ASM_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "AsmInstruction.cpp.md"
DATATYPE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DataType.cpp.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"

COMMON_TAGS = {
    "static-reaudit",
    "script-datatype-head-wave573",
    "retail-binary-evidence",
    "signature-corrected",
    "comment-hardened",
    "mission-script",
}

TARGETS = {
    "0x0052d040": {
        "raw": "0052d040",
        "name": "CAsmInstruction__GetAttributeValue",
        "signature": "void * __stdcall CAsmInstruction__GetAttributeValue(void * instruction)",
        "tags": COMMON_TAGS | {"asm-instruction", "bytecode-vm"},
        "comment_tokens": ("OP_PUSH", "RET 0x4 confirms", "CIntDataType fallback"),
        "decompile_file": "0052d040_CAsmInstruction__GetAttributeValue.c",
        "decompile_tokens": ("instruction + 8", "+ 0x48", "FATAL_ERROR__no_data_set_for_att", "PTR_CDataType__ScalarDeletingDestructor_005e4af8"),
    },
    "0x0052d0a0": {
        "raw": "0052d0a0",
        "name": "CIntDataType__Add",
        "signature": "void * __thiscall CIntDataType__Add(void * this, void * rhs)",
        "tags": COMMON_TAGS | {"datatype", "int-datatype", "vtable-slot"},
        "comment_tokens": ("arithmetic add", "vtable slot +0x30", "summed integer"),
        "decompile_file": "0052d0a0_CIntDataType__Add.c",
        "decompile_tokens": ("CIntDataType__Add", "+ 0x30", "puVar2[1] = iVar3 + iVar1"),
    },
    "0x0052d110": {
        "raw": "0052d110",
        "name": "CIntDataType__Subtract",
        "signature": "void * __thiscall CIntDataType__Subtract(void * this, void * rhs)",
        "tags": COMMON_TAGS | {"datatype", "int-datatype", "vtable-slot"},
        "comment_tokens": ("arithmetic subtract", "RET 0x4 confirms", "stores the result"),
        "decompile_file": "0052d110_CIntDataType__Subtract.c",
        "decompile_tokens": ("CIntDataType__Subtract", "+ 0x30", "- iVar3"),
    },
    "0x0052d180": {
        "raw": "0052d180",
        "name": "CIntDataType__Multiply",
        "signature": "void * __thiscall CIntDataType__Multiply(void * this, void * rhs)",
        "tags": COMMON_TAGS | {"datatype", "int-datatype", "vtable-slot"},
        "comment_tokens": ("arithmetic multiply", "RET 0x4 confirms", "stores the product"),
        "decompile_file": "0052d180_CIntDataType__Multiply.c",
        "decompile_tokens": ("CIntDataType__Multiply", "+ 0x30", "* *(int *)((int)this + 4)"),
    },
    "0x0052d1f0": {
        "raw": "0052d1f0",
        "name": "CIntDataType__Divide",
        "signature": "void * __thiscall CIntDataType__Divide(void * this, void * rhs)",
        "tags": COMMON_TAGS | {"datatype", "int-datatype", "vtable-slot"},
        "comment_tokens": ("arithmetic divide", "divide-by-zero behavior", "quotient"),
        "decompile_file": "0052d1f0_CIntDataType__Divide.c",
        "decompile_tokens": ("CIntDataType__Divide", "+ 0x30", "puVar2[1] = iVar1 / iVar3"),
    },
    "0x0052d260": {
        "raw": "0052d260",
        "name": "CIntDataType__Equals",
        "signature": "bool __thiscall CIntDataType__Equals(void * this, void * rhs)",
        "tags": COMMON_TAGS | {"datatype", "int-datatype", "vtable-slot", "comparison"},
        "comment_tokens": ("equality compare", "bool ABI", "equals"),
        "decompile_file": "0052d260_CIntDataType__Equals.c",
        "decompile_tokens": ("CIntDataType__Equals", "+ 0x30", "=="),
    },
    "0x0052d280": {
        "raw": "0052d280",
        "name": "CIntDataType__NotEquals",
        "signature": "bool __thiscall CIntDataType__NotEquals(void * this, void * rhs)",
        "tags": COMMON_TAGS | {"datatype", "int-datatype", "vtable-slot", "comparison"},
        "comment_tokens": ("inequality compare", "bool ABI", "differs"),
        "decompile_file": "0052d280_CIntDataType__NotEquals.c",
        "decompile_tokens": ("CIntDataType__NotEquals", "+ 0x30", "!="),
    },
    "0x0052d2a0": {
        "raw": "0052d2a0",
        "name": "CIntDataType__Assign",
        "signature": "void __thiscall CIntDataType__Assign(void * this, void * rhs)",
        "tags": COMMON_TAGS | {"datatype", "int-datatype", "vtable-slot"},
        "comment_tokens": ("assignment", "stores the returned integer", "this+0x04"),
        "decompile_file": "0052d2a0_CIntDataType__Assign.c",
        "decompile_tokens": ("CIntDataType__Assign", "+ 0x30", "*(undefined4 *)((int)this + 4) ="),
    },
    "0x0052d2c0": {
        "raw": "0052d2c0",
        "name": "CIntDataType__LessThan",
        "signature": "bool __thiscall CIntDataType__LessThan(void * this, void * rhs)",
        "tags": COMMON_TAGS | {"datatype", "int-datatype", "vtable-slot", "comparison"},
        "comment_tokens": ("less-than compare", "RET 0x4 confirms", "less than"),
        "decompile_file": "0052d2c0_CIntDataType__LessThan.c",
        "decompile_tokens": ("CIntDataType__LessThan", "+ 0x30", "<"),
    },
    "0x0052d2e0": {
        "raw": "0052d2e0",
        "name": "CIntDataType__GreaterThan",
        "signature": "bool __thiscall CIntDataType__GreaterThan(void * this, void * rhs)",
        "tags": COMMON_TAGS | {"datatype", "int-datatype", "vtable-slot", "comparison"},
        "comment_tokens": ("greater-than compare", "RET 0x4 confirms", "greater than"),
        "decompile_file": "0052d2e0_CIntDataType__GreaterThan.c",
        "decompile_tokens": ("CIntDataType__GreaterThan", "+ 0x30", "< *(int *)((int)this + 4)"),
    },
    "0x0052d300": {
        "raw": "0052d300",
        "name": "CIntDataType__LessOrEqual",
        "signature": "bool __thiscall CIntDataType__LessOrEqual(void * this, void * rhs)",
        "tags": COMMON_TAGS | {"datatype", "int-datatype", "vtable-slot", "comparison"},
        "comment_tokens": ("less-or-equal compare", "RET 0x4 confirms", "less than or equal"),
        "decompile_file": "0052d300_CIntDataType__LessOrEqual.c",
        "decompile_tokens": ("CIntDataType__LessOrEqual", "+ 0x30", "<="),
    },
    "0x0052d320": {
        "raw": "0052d320",
        "name": "CIntDataType__GreaterOrEqual",
        "signature": "bool __thiscall CIntDataType__GreaterOrEqual(void * this, void * rhs)",
        "tags": COMMON_TAGS | {"datatype", "int-datatype", "vtable-slot", "comparison"},
        "comment_tokens": ("greater-or-equal compare", "RET 0x4 confirms", "greater than or equal"),
        "decompile_file": "0052d320_CIntDataType__GreaterOrEqual.c",
        "decompile_tokens": ("CIntDataType__GreaterOrEqual", "+ 0x30", "<="),
    },
    "0x0052d390": {
        "raw": "0052d390",
        "name": "CDataType__Destructor",
        "signature": "void __thiscall CDataType__Destructor(void * this)",
        "tags": COMMON_TAGS | {"datatype", "destructor"},
        "comment_tokens": ("base destructor", "scalar-deleting destructor", "base CDataType vtable"),
        "decompile_file": "0052d390_CDataType__Destructor.c",
        "decompile_tokens": ("CDataType__Destructor", "PTR_LAB_005e4b4c"),
    },
    "0x0052d3d0": {
        "raw": "0052d3d0",
        "name": "CAsmInstruction__SpawnFromOpcode",
        "signature": "void * __cdecl CAsmInstruction__SpawnFromOpcode(int opcode, void * bytecode_reader)",
        "tags": COMMON_TAGS | {"asm-instruction", "opcode-factory", "bytecode-vm"},
        "comment_tokens": ("bytecode instruction factory", "unknown-instruction", "opcode enum"),
        "decompile_file": "0052d3d0_CAsmInstruction__SpawnFromOpcode.c",
        "decompile_tokens": ("switch(opcode)", "CDXMemBuffer__Read(bytecode_reader", "PTR_CInstructionOP_PUSH__VFunc_00_0052e2c0", "FATAL_ERROR__uknown_instruction_i"),
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
        BASE / "apply_dry.log",
        {"updated": 0, "skipped": 14, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "apply.log",
        {"updated": 14, "skipped": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "apply_verify_dry.log",
        {"updated": 0, "skipped": 14, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )

    expected_counts = {
        "post_metadata.tsv": 14,
        "post_tags.tsv": 14,
        "post_xrefs.tsv": 34,
        "post_target_instructions.tsv": 2254,
        "post_decompile/index.tsv": 14,
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

    overclaim_tokens = (
        "runtime behavior proven",
        "runtime script behavior proven",
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
            missing_tags = set(spec["tags"]) - present
            if missing_tags:
                failures.append(f"{address} missing tags: {sorted(missing_tags)}")
            for forbidden in ("source-parity", "runtime-proven", "rebuild-parity"):
                if forbidden in present:
                    failures.append(f"{address} has forbidden tag {forbidden}")

        decomp_row = decomp_index.get(address)
        if decomp_row is None:
            failures.append(f"{address} missing from post_decompile/index.tsv")
        else:
            if decomp_row["signature"] != spec["signature"]:
                failures.append(f"{address} decompile index signature mismatch")
            decomp_text = read_text(BASE / "post_decompile" / spec["decompile_file"])
            require_tokens(f"{address} decompile", decomp_text, spec["decompile_tokens"], failures)

        if spec["raw"] not in instructions:
            failures.append(f"{address} missing from post_target_instructions.tsv")
        if spec["name"] not in xrefs and address not in xrefs:
            failures.append(f"{address} missing from post_xrefs.tsv")

    queue = json.loads(read_text(QUEUE_JSON))
    expected_queue = {
        "totalFunctions": 6093,
        "commentlessFunctionCount": 3216,
        "undefinedSignatureCount": 1465,
        "paramSignatureCount": 1144,
    }
    if queue.get("status") != "PASS":
        failures.append(f"queue status mismatch: {queue.get('status')}")
    if queue.get("totalFunctions") != expected_queue["totalFunctions"]:
        failures.append(f"queue totalFunctions mismatch: {queue.get('totalFunctions')}")
    signals = queue.get("qualitySignals", {})
    for key, expected in expected_queue.items():
        if key == "totalFunctions":
            continue
        actual = signals.get(key)
        if actual != expected:
            failures.append(f"queue {key} mismatch: {actual} != {expected}")
    head = queue.get("priorityQueues", {}).get("commentlessHighSignal", [{}])[0]
    if head.get("address") != "0x0052e0f0" or head.get("name") != "CAsmInstruction__ExecutePop":
        failures.append(f"queue head mismatch: {head}")

    require_doc_tokens(
        PUBLIC_NOTE,
        (
            "Ghidra Script/DataType Head Wave573 Readiness Note",
            "CAsmInstruction__SpawnFromOpcode",
            "CIntDataType__Divide",
            "2877 / 6093 = 47.22%",
            "2826 / 6093 = 46.39%",
            "BEA_20260519-010737_post_wave573_script_datatype_head_verified",
        ),
        failures,
    )
    require_doc_tokens(
        GHIDRA_REFERENCE,
        (
            "Current Signature Caveat: MissionScript DataType Head (2026-05-19)",
            "Wave573 script/datatype head hardened fourteen adjacent rows",
            "void * __cdecl CAsmInstruction__SpawnFromOpcode(int opcode, void * bytecode_reader)",
            "runtime script behavior",
        ),
        failures,
    )
    require_doc_tokens(
        CAMPAIGN,
        (
            "Fresh headless export on 2026-05-19 after Wave573",
            "Current script/datatype head follow-up",
            "Wave 573: Script/DataType Head",
            "2877/6093 = 47.22%",
        ),
        failures,
    )
    require_doc_tokens(
        FUNCTION_INDEX,
        (
            "Latest saved-correction note: Wave573",
            "CAsmInstruction__GetAttributeValue",
            "CIntDataType__GreaterOrEqual",
            "Post-Wave573 queue telemetry",
        ),
        failures,
    )
    require_doc_tokens(
        ASM_DOC,
        (
            "Status: ACTIVE STATIC READ-BACK",
            "CAsmInstruction__GetAttributeValue",
            "CAsmInstruction__SpawnFromOpcode",
            "opcode factory",
        ),
        failures,
    )
    require_doc_tokens(
        DATATYPE_DOC,
        (
            "Last updated: 2026-05-19",
            "Wave573 Static Read-Back",
            "void * __thiscall CIntDataType__Add(void * this, void * rhs)",
            "bool __thiscall CIntDataType__GreaterOrEqual(void * this, void * rhs)",
        ),
        failures,
    )
    require_doc_tokens(
        BACKLOG,
        (
            "Ghidra script/datatype head Wave573 signature/comment hardening",
            "ApplyScriptDataTypeHeadWave573.java",
            "160205703",
        ),
        failures,
    )
    require_doc_tokens(
        LEDGER,
        (
            "Ghidra script/datatype head Wave573 signature/comment hardening",
            "CAsmInstruction__SpawnFromOpcode",
            "BEA_20260519-010737_post_wave573_script_datatype_head_verified",
        ),
        failures,
    )

    return failures


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate artifacts and exit nonzero on drift.")
    parser.add_argument("--json", action="store_true", help="Emit JSON result.")
    args = parser.parse_args(argv)

    failures = run_check()
    result = {
        "status": "PASS" if not failures else "FAIL",
        "failureCount": len(failures),
        "failures": failures,
    }
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif failures:
        print("FAIL: Wave573 script/datatype-head probe found drift:")
        for failure in failures:
            print(f"- {failure}")
    else:
        print("PASS: Wave573 script/datatype-head artifacts validated.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
