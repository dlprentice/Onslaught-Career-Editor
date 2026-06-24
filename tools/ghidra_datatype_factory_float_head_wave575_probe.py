#!/usr/bin/env python3
"""Validate Wave575 datatype factory/float Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave575-datatype-factory-float-head-0052ec60"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_datatype_factory_float_head_wave575_2026-05-19.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
DATATYPE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DataType.cpp.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"

COMMON_TAGS = {
    "static-reaudit",
    "datatype-factory-float-head-wave575",
    "retail-binary-evidence",
    "signature-corrected",
    "comment-hardened",
    "mission-script",
    "datatype",
}

TARGETS = {
    "0x0052ec60": {
        "raw": "0052ec60",
        "name": "CDataType__CreateFromType",
        "signature": "void * __cdecl CDataType__CreateFromType(int type_id, void * bytecode_reader)",
        "tags": COMMON_TAGS | {"datatype-factory", "factory-type-cleanup", "type-id-switch"},
        "comment_tokens": ("type_id 1..6", "type 2 -> CFloatDataType", "type 4 -> observed CBoolDataType", "unknown-data-type"),
    },
    "0x0052ef50": {
        "raw": "0052ef50",
        "name": "CFloatDataType__Add",
        "signature": "void * __thiscall CFloatDataType__Add(void * this, void * rhs)",
        "tags": COMMON_TAGS | {"add", "arithmetic", "float-datatype", "vtable-slot"},
        "comment_tokens": ("0x005e4ea8", "vtable slot +0x34", "stores the sum"),
    },
    "0x0052efc0": {
        "raw": "0052efc0",
        "name": "CFloatDataType__Subtract",
        "signature": "void * __thiscall CFloatDataType__Subtract(void * this, void * rhs)",
        "tags": COMMON_TAGS | {"arithmetic", "float-datatype", "subtract", "vtable-slot"},
        "comment_tokens": ("0x005e4eac", "subtracts rhs", "stores the difference"),
    },
    "0x0052f030": {
        "raw": "0052f030",
        "name": "CFloatDataType__Multiply",
        "signature": "void * __thiscall CFloatDataType__Multiply(void * this, void * rhs)",
        "tags": COMMON_TAGS | {"arithmetic", "float-datatype", "multiply", "vtable-slot"},
        "comment_tokens": ("0x005e4eb0", "multiplies", "stores the product"),
    },
    "0x0052f0a0": {
        "raw": "0052f0a0",
        "name": "CFloatDataType__Divide",
        "signature": "void * __thiscall CFloatDataType__Divide(void * this, void * rhs)",
        "tags": COMMON_TAGS | {"arithmetic", "divide", "float-datatype", "vtable-slot"},
        "comment_tokens": ("0x005e4eb4", "divides", "divide-by-zero behavior"),
    },
    "0x0052f110": {
        "raw": "0052f110",
        "name": "CFloatDataType__Equals",
        "signature": "bool __thiscall CFloatDataType__Equals(void * this, void * rhs)",
        "tags": COMMON_TAGS | {"comparison", "equals", "float-datatype", "vtable-slot"},
        "comment_tokens": ("0x005e4ebc", "returns whether it equals", "bool/float ABI"),
    },
    "0x0052f140": {
        "raw": "0052f140",
        "name": "CFloatDataType__NotEquals",
        "signature": "bool __thiscall CFloatDataType__NotEquals(void * this, void * rhs)",
        "tags": COMMON_TAGS | {"comparison", "float-datatype", "not-equals", "vtable-slot"},
        "comment_tokens": ("0x005e4ec0", "returns whether it differs", "bool/float ABI"),
    },
    "0x0052f170": {
        "raw": "0052f170",
        "name": "CFloatDataType__Assign",
        "signature": "void __thiscall CFloatDataType__Assign(void * this, void * rhs)",
        "tags": COMMON_TAGS | {"assignment", "float-datatype", "vtable-slot"},
        "comment_tokens": ("0x005e4eb8", "stores the returned float", "this+0x04"),
    },
    "0x0052f190": {
        "raw": "0052f190",
        "name": "CFloatDataType__LessThan",
        "signature": "bool __thiscall CFloatDataType__LessThan(void * this, void * rhs)",
        "tags": COMMON_TAGS | {"comparison", "float-datatype", "less-than", "vtable-slot"},
        "comment_tokens": ("0x005e4ec4", "less than rhs", "vtable slot +0x34"),
    },
    "0x0052f1c0": {
        "raw": "0052f1c0",
        "name": "CFloatDataType__GreaterThan",
        "signature": "bool __thiscall CFloatDataType__GreaterThan(void * this, void * rhs)",
        "tags": COMMON_TAGS | {"comparison", "float-datatype", "greater-than", "vtable-slot"},
        "comment_tokens": ("0x005e4ec8", "greater than rhs", "vtable slot +0x34"),
    },
    "0x0052f1f0": {
        "raw": "0052f1f0",
        "name": "CFloatDataType__LessOrEqual",
        "signature": "bool __thiscall CFloatDataType__LessOrEqual(void * this, void * rhs)",
        "tags": COMMON_TAGS | {"comparison", "float-datatype", "less-or-equal", "vtable-slot"},
        "comment_tokens": ("0x005e4ecc", "less than or equal", "vtable slot +0x34"),
    },
    "0x0052f220": {
        "raw": "0052f220",
        "name": "CFloatDataType__GreaterOrEqual",
        "signature": "bool __thiscall CFloatDataType__GreaterOrEqual(void * this, void * rhs)",
        "tags": COMMON_TAGS | {"comparison", "float-datatype", "greater-or-equal", "vtable-slot"},
        "comment_tokens": ("0x005e4ed0", "greater than or equal", "vtable slot +0x34"),
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
        BASE / "wave575_apply_dry.log",
        {"updated": 0, "skipped": 12, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "wave575_apply.log",
        {"updated": 12, "skipped": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "wave575_apply_final_dry.log",
        {"updated": 0, "skipped": 12, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )

    expected_counts = {
        "post_metadata.tsv": 12,
        "post_tags.tsv": 12,
        "post_xrefs.tsv": 12,
        "post_target_instructions.tsv": 2748,
        "post_decompile/index.tsv": 12,
        "post_datatype_vtables.tsv": 384,
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
    vtables = read_text(BASE / "post_datatype_vtables.tsv")

    require_tokens(
        "datatype vtables",
        vtables,
        ("005e4ea4", "CFloatDataType__Add", "005e4d64", "CBoolDataType__Assign"),
        failures,
    )

    overclaim_tokens = (
        "runtime behavior proven",
        "runtime MissionScript behavior proven",
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

    backup = json.loads(read_text(BASE / "wave575_backup_summary.json"))
    if backup.get("status") != "PASS":
        failures.append(f"backup status mismatch: {backup.get('status')}")
    if not str(backup.get("destination", "")).endswith("BEA_20260519-020812_post_wave575_datatype_factory_float_head_verified"):
        failures.append(f"backup destination mismatch: {backup.get('destination')}")
    if backup.get("fileCount") != 19:
        failures.append(f"backup fileCount mismatch: {backup.get('fileCount')}")
    if backup.get("byteCount") != 160369543:
        failures.append(f"backup byteCount mismatch: {backup.get('byteCount')}")
    if backup.get("sourceManifestHash") != "DF7C8BD3CCAE9DD1C8FBE58FD8D25CE789E793765732D46BC850ABF9D9629079":
        failures.append("backup sourceManifestHash mismatch")
    if backup.get("destinationManifestHash") != backup.get("sourceManifestHash"):
        failures.append("backup source/destination manifest hash mismatch")

    queue = json.loads(read_text(QUEUE_JSON))
    expected_queue = {
        "totalFunctions": 6093,
        "commentlessFunctionCount": 3189,
        "undefinedSignatureCount": 1443,
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
    if head.get("address") != "0x0052f2c0" or head.get("name") != "CStringDataType__Clone":
        failures.append(f"queue head mismatch: {head}")

    require_doc_tokens(
        PUBLIC_NOTE,
        (
            "Ghidra DataType Factory/Float Head Wave575 Readiness Note",
            "CDataType__CreateFromType",
            "CFloatDataType__GreaterOrEqual",
            "2904 / 6093 = 47.66%",
            "2853 / 6093 = 46.82%",
            "BEA_20260519-020812_post_wave575_datatype_factory_float_head_verified",
        ),
        failures,
    )
    require_doc_tokens(
        GHIDRA_REFERENCE,
        (
            "Current Signature Caveat: MissionScript DataType Factory/Float Head (2026-05-19)",
            "Wave575 datatype factory/float head hardened twelve adjacent rows",
            "void * __cdecl CDataType__CreateFromType(int type_id, void * bytecode_reader)",
            "runtime MissionScript behavior",
        ),
        failures,
    )
    require_doc_tokens(
        CAMPAIGN,
        (
            "Fresh headless export on 2026-05-19 after Wave575",
            "Current datatype factory/float head follow-up",
            "Wave 575: DataType Factory/Float Head",
            "2904/6093 = 47.66%",
        ),
        failures,
    )
    require_doc_tokens(
        FUNCTION_INDEX,
        (
            "Latest saved-correction note: Wave575",
            "CDataType__CreateFromType",
            "CFloatDataType__GreaterOrEqual",
            "Post-Wave575 queue telemetry",
        ),
        failures,
    )
    require_doc_tokens(
        DATATYPE_DOC,
        (
            "Wave575 Factory/Float Static Read-Back",
            "void * __cdecl CDataType__CreateFromType(int type_id, void * bytecode_reader)",
            "bool __thiscall CFloatDataType__GreaterOrEqual(void * this, void * rhs)",
            "type 2 installs `CFloatDataType` vtable `0x005e4ea4`",
        ),
        failures,
    )
    require_doc_tokens(
        BACKLOG,
        (
            "Ghidra datatype factory/float head Wave575 signature/comment hardening",
            "ApplyDataTypeFactoryFloatHeadWave575.java",
            "160369543",
        ),
        failures,
    )
    require_doc_tokens(
        LEDGER,
        (
            "Ghidra datatype factory/float head Wave575 signature/comment hardening",
            "CFloatDataType__GreaterOrEqual",
            "BEA_20260519-020812_post_wave575_datatype_factory_float_head_verified",
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
        print("FAIL: Wave575 datatype factory/float-head probe found drift:")
        for failure in failures:
            print(f"- {failure}")
    else:
        print("PASS: Wave575 datatype factory/float-head artifacts validated.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
