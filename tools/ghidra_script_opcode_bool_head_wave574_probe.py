#!/usr/bin/env python3
"""Validate Wave574 MissionScript opcode/bool Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave574-script-opcode-bool-head-0052e0f0"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_script_opcode_bool_head_wave574_2026-05-19.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
ASM_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "AsmInstruction.cpp.md"
DATATYPE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DataType.cpp.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"

COMMON_TAGS = {
    "static-reaudit",
    "script-opcode-bool-head-wave574",
    "retail-binary-evidence",
    "signature-corrected",
    "comment-hardened",
    "mission-script",
}

INSTRUCTION_SIGNATURE = "void __thiscall {name}(void * this, void * script_state, void * data_stack, void * object_code)"

TARGETS = {
    "0x0052e0f0": {
        "raw": "0052e0f0",
        "name": "CAsmInstruction__ExecutePop",
        "signature": INSTRUCTION_SIGNATURE.format(name="CAsmInstruction__ExecutePop"),
        "tags": COMMON_TAGS | {"asm-instruction", "bytecode-vm", "datatype-dispatch", "opcode-executor", "pop", "stack"},
        "comment_tokens": ("POP", "script_state+0x224", "script_state+0x214", "one-valued CIntDataType"),
    },
    "0x0052e2c0": {
        "raw": "0052e2c0",
        "name": "CInstructionOP_PUSH__VFunc_00_0052e2c0",
        "signature": INSTRUCTION_SIGNATURE.format(name="CInstructionOP_PUSH__VFunc_00_0052e2c0"),
        "tags": COMMON_TAGS | {"asm-instruction", "bytecode-vm", "instruction-vfunc", "opcode-executor", "push", "stack"},
        "comment_tokens": ("OP_PUSH", "this+0x04", "CAsmInstruction__GetAttributeValue", "data_stack"),
    },
    "0x0052e380": {
        "raw": "0052e380",
        "name": "CAsmInstruction__ExecuteCompareEqual",
        "signature": INSTRUCTION_SIGNATURE.format(name="CAsmInstruction__ExecuteCompareEqual"),
        "tags": COMMON_TAGS | {"asm-instruction", "boolean-result", "bytecode-vm", "comparison", "datatype-dispatch", "opcode-executor"},
        "comment_tokens": ("equality comparison", "vtable slot +0x18", "boolean result object", "releases both operands"),
    },
    "0x0052e420": {
        "raw": "0052e420",
        "name": "CBoolDataType__Equals",
        "signature": "bool __thiscall CBoolDataType__Equals(void * this, void * rhs)",
        "tags": COMMON_TAGS | {"bool-datatype", "comparison", "datatype", "semantic-rename", "vtable-slot"},
        "comment_tokens": ("semantic rename", "0x005e4d68", "slot +0x3c", "this+0x04"),
    },
    "0x0052e440": {
        "raw": "0052e440",
        "name": "CBoolDataType__NotEquals",
        "signature": "bool __thiscall CBoolDataType__NotEquals(void * this, void * rhs)",
        "tags": COMMON_TAGS | {"bool-datatype", "comparison", "datatype", "semantic-rename", "vtable-slot"},
        "comment_tokens": ("semantic rename", "0x005e4d6c", "slot +0x3c", "this+0x04"),
    },
    "0x0052e460": {
        "raw": "0052e460",
        "name": "CBoolDataType__Assign",
        "signature": "void __thiscall CBoolDataType__Assign(void * this, void * rhs)",
        "tags": COMMON_TAGS | {"bool-datatype", "datatype", "semantic-rename", "vtable-slot"},
        "comment_tokens": ("semantic rename", "0x005e4d64", "slot +0x3c", "storing the returned byte"),
    },
    "0x0052e4d0": {
        "raw": "0052e4d0",
        "name": "CAsmInstruction__ExecuteOr",
        "signature": INSTRUCTION_SIGNATURE.format(name="CAsmInstruction__ExecuteOr"),
        "tags": COMMON_TAGS | {"asm-instruction", "boolean-op", "bytecode-vm", "datatype-dispatch", "opcode-executor", "or"},
        "comment_tokens": ("OR opcode", "logical OR", "boolean result object", "releases both operands"),
    },
    "0x0052e580": {
        "raw": "0052e580",
        "name": "CAsmInstruction__ExecuteAnd",
        "signature": INSTRUCTION_SIGNATURE.format(name="CAsmInstruction__ExecuteAnd"),
        "tags": COMMON_TAGS | {"and", "asm-instruction", "boolean-op", "bytecode-vm", "datatype-dispatch", "opcode-executor"},
        "comment_tokens": ("AND opcode", "logical AND", "boolean result object", "releases both operands"),
    },
    "0x0052e630": {
        "raw": "0052e630",
        "name": "CAsmInstruction__ExecuteGreaterThan",
        "signature": INSTRUCTION_SIGNATURE.format(name="CAsmInstruction__ExecuteGreaterThan"),
        "tags": COMMON_TAGS | {"asm-instruction", "bytecode-vm", "comparison", "datatype-dispatch", "greater-than", "opcode-executor"},
        "comment_tokens": ("greater-than comparison", "vtable slot +0x24", "boolean result object", "releases both operands"),
    },
    "0x0052e6d0": {
        "raw": "0052e6d0",
        "name": "CAsmInstruction__ExecuteLessThan",
        "signature": INSTRUCTION_SIGNATURE.format(name="CAsmInstruction__ExecuteLessThan"),
        "tags": COMMON_TAGS | {"asm-instruction", "bytecode-vm", "comparison", "datatype-dispatch", "less-than", "opcode-executor"},
        "comment_tokens": ("less-than comparison", "vtable slot +0x20", "boolean result object", "releases both operands"),
    },
    "0x0052e770": {
        "raw": "0052e770",
        "name": "CAsmInstruction__ExecuteGreaterOrEqual",
        "signature": INSTRUCTION_SIGNATURE.format(name="CAsmInstruction__ExecuteGreaterOrEqual"),
        "tags": COMMON_TAGS | {"asm-instruction", "bytecode-vm", "comparison", "datatype-dispatch", "greater-or-equal", "opcode-executor"},
        "comment_tokens": ("greater-or-equal comparison", "vtable slot +0x2c", "boolean result object", "releases both operands"),
    },
    "0x0052e810": {
        "raw": "0052e810",
        "name": "CAsmInstruction__ExecuteLessOrEqual",
        "signature": INSTRUCTION_SIGNATURE.format(name="CAsmInstruction__ExecuteLessOrEqual"),
        "tags": COMMON_TAGS | {"asm-instruction", "bytecode-vm", "comparison", "datatype-dispatch", "less-or-equal", "opcode-executor"},
        "comment_tokens": ("less-or-equal comparison", "vtable slot +0x28", "boolean result object", "releases both operands"),
    },
    "0x0052e8b0": {
        "raw": "0052e8b0",
        "name": "CAsmInstruction__ExecuteCompareNotEqual",
        "signature": INSTRUCTION_SIGNATURE.format(name="CAsmInstruction__ExecuteCompareNotEqual"),
        "tags": COMMON_TAGS | {"asm-instruction", "boolean-result", "bytecode-vm", "comparison", "datatype-dispatch", "opcode-executor"},
        "comment_tokens": ("inequality comparison", "vtable slot +0x1c", "boolean result object", "releases both operands"),
    },
    "0x0052e950": {
        "raw": "0052e950",
        "name": "CInstructionOP_JMPFALSE__VFunc_00_0052e950",
        "signature": INSTRUCTION_SIGNATURE.format(name="CInstructionOP_JMPFALSE__VFunc_00_0052e950"),
        "tags": COMMON_TAGS | {"asm-instruction", "bytecode-vm", "control-flow", "datatype-dispatch", "instruction-vfunc", "jump-false", "opcode-executor"},
        "comment_tokens": ("JMPFALSE", "script_state+0x214", "value is false", "branch-target encoding"),
    },
    "0x0052ea40": {
        "raw": "0052ea40",
        "name": "CAsmInstruction__ExecuteCall",
        "signature": INSTRUCTION_SIGNATURE.format(name="CAsmInstruction__ExecuteCall"),
        "tags": COMMON_TAGS | {"asm-instruction", "bytecode-vm", "call", "datatype-dispatch", "function-call-dispatch", "global-scratch", "opcode-executor"},
        "comment_tokens": ("CALL opcode", "global call scratch array", "0x0064ce50", "return-type encoding"),
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
        BASE / "wave574_apply_dry.log",
        {"updated": 0, "skipped": 15, "renamed": 0, "would_rename": 3, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "wave574_apply.log",
        {"updated": 15, "skipped": 0, "renamed": 3, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "wave574_apply_final_dry.log",
        {"updated": 0, "skipped": 15, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )

    expected_counts = {
        "post_metadata.tsv": 15,
        "post_tags.tsv": 15,
        "post_xrefs.tsv": 15,
        "post_target_instructions.tsv": 2715,
        "post_decompile/index.tsv": 15,
        "post_dispatch_table_slots.tsv": 112,
        "factory_peek_datatype_vtables.tsv": 48,
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
    factory_peek = read_text(BASE / "factory_peek_datatype_vtables.tsv")

    require_tokens(
        "factory peek",
        factory_peek,
        ("005e4d64", "CBoolDataType__Assign", "005e4ea4", "CFloatDataType__Add"),
        failures,
    )

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
        elif decomp_row["signature"] != spec["signature"]:
            failures.append(f"{address} decompile index signature mismatch")

        if spec["raw"] not in instructions:
            failures.append(f"{address} missing from post_target_instructions.tsv")
        if spec["name"] not in xrefs and address not in xrefs:
            failures.append(f"{address} missing from post_xrefs.tsv")

    queue = json.loads(read_text(QUEUE_JSON))
    expected_queue = {
        "totalFunctions": 6093,
        "commentlessFunctionCount": 3201,
        "undefinedSignatureCount": 1455,
        "paramSignatureCount": 1139,
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
    if head.get("address") != "0x0052ec60" or head.get("name") != "CDataType__CreateFromType":
        failures.append(f"queue head mismatch: {head}")

    require_doc_tokens(
        PUBLIC_NOTE,
        (
            "Ghidra Script Opcode/Bool Head Wave574 Readiness Note",
            "CAsmInstruction__ExecuteCall",
            "CBoolDataType__Assign",
            "2892 / 6093 = 47.46%",
            "2841 / 6093 = 46.63%",
            "BEA_20260519-013338_post_wave574_script_opcode_bool_head_verified",
        ),
        failures,
    )
    require_doc_tokens(
        GHIDRA_REFERENCE,
        (
            "Current Signature Caveat: MissionScript Opcode/Bool Head (2026-05-19)",
            "Wave574 script opcode/bool head hardened fifteen adjacent rows",
            "void __thiscall CAsmInstruction__ExecuteCall(void * this, void * script_state, void * data_stack, void * object_code)",
            "runtime MissionScript behavior",
        ),
        failures,
    )
    require_doc_tokens(
        CAMPAIGN,
        (
            "Fresh headless export on 2026-05-19 after Wave574",
            "Current script opcode/bool head follow-up",
            "Wave 574: Script Opcode/Bool Head",
            "2892/6093 = 47.46%",
        ),
        failures,
    )
    require_doc_tokens(
        FUNCTION_INDEX,
        (
            "Latest saved-correction note: Wave574",
            "CAsmInstruction__ExecutePop",
            "CBoolDataType__Assign",
            "Post-Wave574 queue telemetry",
        ),
        failures,
    )
    require_doc_tokens(
        ASM_DOC,
        (
            "Wave574 Static Read-Back",
            "CAsmInstruction__ExecuteCall",
            "CInstructionOP_JMPFALSE__VFunc_00_0052e950",
            "CDataType__CreateFromType",
        ),
        failures,
    )
    require_doc_tokens(
        DATATYPE_DOC,
        (
            "Wave574 Bool Static Read-Back",
            "bool __thiscall CBoolDataType__Equals(void * this, void * rhs)",
            "type 2 installs vtable `0x005e4ea4`",
            "type 4 installs the vtable region with the Wave574 CBoolDataType slots",
        ),
        failures,
    )
    require_doc_tokens(
        BACKLOG,
        (
            "Ghidra script opcode/bool head Wave574 signature/comment hardening",
            "ApplyScriptOpcodeBoolHeadWave574.java",
            "160271239",
        ),
        failures,
    )
    require_doc_tokens(
        LEDGER,
        (
            "Ghidra script opcode/bool head Wave574 signature/comment hardening",
            "CAsmInstruction__ExecuteCall",
            "BEA_20260519-013338_post_wave574_script_opcode_bool_head_verified",
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
        print("FAIL: Wave574 script opcode/bool-head probe found drift:")
        for failure in failures:
            print(f"- {failure}")
    else:
        print("PASS: Wave574 script opcode/bool-head artifacts validated.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
