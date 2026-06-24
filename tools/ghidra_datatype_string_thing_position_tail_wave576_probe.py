#!/usr/bin/env python3
"""Validate Wave576 datatype string/thing-pointer/position Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave576-datatype-string-thingptr-position-tail-0052f2c0"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_datatype_string_thing_position_tail_wave576_2026-05-19.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
DATATYPE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DataType.cpp.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"

COMMON_TAGS = {
    "static-reaudit",
    "datatype-string-thing-position-tail-wave576",
    "retail-binary-evidence",
    "signature-corrected",
    "comment-hardened",
    "mission-script",
    "datatype",
}

TARGETS = {
    "0x0052f2c0": {
        "raw": "0052f2c0",
        "name": "CStringDataType__Clone",
        "signature": "void * __thiscall CStringDataType__Clone(void * this)",
        "tags": COMMON_TAGS | {"clone", "string-datatype", "vtable-slot"},
        "comment_tokens": ("0x005e4e94", "heap buffer", "null-terminates the clone buffer"),
        "decompile_file": "0052f2c0_CStringDataType__Clone.c",
        "decompile_tokens": ("OID__AllocObject(8", "PTR_CStringDataType__ScalarDeletingDestructor_005e4e4c", "_strncpy"),
    },
    "0x0052f360": {
        "raw": "0052f360",
        "name": "CStringDataType__Equals",
        "signature": "bool __thiscall CStringDataType__Equals(void * this, void * rhs)",
        "tags": COMMON_TAGS | {"comparison", "equals", "string-datatype", "vtable-slot"},
        "comment_tokens": ("0x005e4e64", "vtable slot +0x38", "string pointer stored at this+0x04"),
        "decompile_file": "0052f360_CStringDataType__Equals.c",
        "decompile_tokens": ("CStringDataType__Equals", "+ 0x38", "return 1"),
    },
    "0x0052f430": {
        "raw": "0052f430",
        "name": "CStringDataType__Print",
        "signature": "void __thiscall CStringDataType__Print(void * this, void * rhs)",
        "tags": COMMON_TAGS | {"reader-bridge", "string-datatype", "vtable-slot"},
        "comment_tokens": ("0x005e4e0c", "vtable slot +0x40", "CGenericActiveReader__SetReader"),
        "decompile_file": "0052f430_CStringDataType__Print.c",
        "decompile_tokens": ("+ 0x40", "CGenericActiveReader__SetReader"),
    },
    "0x0052f470": {
        "raw": "0052f470",
        "name": "CThingPtrDataType__Clone",
        "signature": "void * __thiscall CThingPtrDataType__Clone(void * this)",
        "tags": COMMON_TAGS | {"clone", "pointer-tracking", "thingptr-datatype", "vtable-slot"},
        "comment_tokens": ("0x005e4e40", "CSPtrSet__AddToHead", "0x005e4df8"),
        "decompile_file": "0052f470_CThingPtrDataType__Clone.c",
        "decompile_tokens": ("CSPtrSet__Init", "CSPtrSet__AddToHead", "PTR_CThingPtrDataType__ScalarDeletingDestructor_005e4df8"),
    },
    "0x0052f550": {
        "raw": "0052f550",
        "name": "CThingPtrDataType__ScalarDeletingDestructor",
        "signature": "void * __thiscall CThingPtrDataType__ScalarDeletingDestructor(void * this, byte flags)",
        "tags": COMMON_TAGS | {"destructor", "scalar-deleting-destructor", "thingptr-datatype", "vtable-slot"},
        "comment_tokens": ("0x005e4df8", "flags&1", "CThingPtrDataType__Destructor"),
        "decompile_file": "0052f550_CThingPtrDataType__ScalarDeletingDestructor.c",
        "decompile_tokens": ("CThingPtrDataType__Destructor", "flags & 1", "CDXMemoryManager__Free"),
    },
    "0x0052f570": {
        "raw": "0052f570",
        "name": "CThingPtrDataType__Destructor",
        "signature": "void __thiscall CThingPtrDataType__Destructor(void * this)",
        "tags": COMMON_TAGS | {"destructor", "pointer-tracking", "thingptr-datatype"},
        "comment_tokens": ("CSPtrSet", "0x005e4b4c", "pointer-set lifetime"),
        "decompile_file": "0052f570_CThingPtrDataType__Destructor.c",
        "decompile_tokens": ("CSPtrSet__Remove", "PTR_LAB_005e4b4c"),
    },
    "0x0052f670": {
        "raw": "0052f670",
        "name": "CDataType__ScalarDeletingDestructor",
        "signature": "void * __thiscall CDataType__ScalarDeletingDestructor(void * this, byte flags)",
        "tags": COMMON_TAGS | {"base-datatype", "destructor", "scalar-deleting-destructor", "shared-vtable-head"},
        "comment_tokens": ("CIntDataType", "CPositionDataType", "flags&1"),
        "decompile_file": "0052f670_CDataType__ScalarDeletingDestructor.c",
        "decompile_tokens": ("CDataType__Destructor", "flags & 1", "CDXMemoryManager__Free"),
    },
    "0x0052f690": {
        "raw": "0052f690",
        "name": "CStringDataType__InitFromString",
        "signature": "void * __thiscall CStringDataType__InitFromString(void * this, char * source_text)",
        "tags": COMMON_TAGS | {"constructor-init", "string-copy", "string-datatype"},
        "comment_tokens": ("source_text", "0x005e4e4c", "returns this"),
        "decompile_file": "0052f690_CStringDataType__InitFromString.c",
        "decompile_tokens": ("PTR_CStringDataType__ScalarDeletingDestructor_005e4e4c", "_strncpy", "return this"),
    },
    "0x0052f720": {
        "raw": "0052f720",
        "name": "CStringDataType__ScalarDeletingDestructor",
        "signature": "void * __thiscall CStringDataType__ScalarDeletingDestructor(void * this, byte flags)",
        "tags": COMMON_TAGS | {"destructor", "scalar-deleting-destructor", "string-datatype", "vtable-slot"},
        "comment_tokens": ("0x005e4e4c", "flags&1", "CStringDataType__Destructor"),
        "decompile_file": "0052f720_CStringDataType__ScalarDeletingDestructor.c",
        "decompile_tokens": ("CStringDataType__Destructor", "flags & 1", "CDXMemoryManager__Free"),
    },
    "0x0052f740": {
        "raw": "0052f740",
        "name": "CStringDataType__Destructor",
        "signature": "void __thiscall CStringDataType__Destructor(void * this)",
        "tags": COMMON_TAGS | {"destructor", "string-buffer-free", "string-datatype"},
        "comment_tokens": ("string buffer", "this+0x04", "0x005e4b4c"),
        "decompile_file": "0052f740_CStringDataType__Destructor.c",
        "decompile_tokens": ("CDXMemoryManager__Free", "PTR_LAB_005e4b4c"),
    },
    "0x0052f790": {
        "raw": "0052f790",
        "name": "CStringDataType__ReadFromBuffer",
        "signature": "void * __thiscall CStringDataType__ReadFromBuffer(void * this, void * bytecode_reader)",
        "tags": COMMON_TAGS | {"buffer-read", "bytecode-read", "string-datatype"},
        "comment_tokens": ("CWorld__LoadScriptEvents", "4-byte string length", "length+1"),
        "decompile_file": "0052f790_CStringDataType__ReadFromBuffer.c",
        "decompile_tokens": ("CDXMemBuffer__Read", "OID__AllocObject((int)bytecode_reader + 1", "return this"),
    },
    "0x0052f8a0": {
        "raw": "0052f8a0",
        "name": "CPositionDataType__SubtractPosition",
        "signature": "void * __thiscall CPositionDataType__SubtractPosition(void * this, void * rhs)",
        "tags": COMMON_TAGS | {"arithmetic", "position-datatype", "subtract", "vtable-slot"},
        "comment_tokens": ("0x005e4dac", "vtable slot +0x44", "x/y/z differences"),
        "decompile_file": "0052f8a0_CPositionDataType__SubtractPosition.c",
        "decompile_tokens": ("+ 0x44", "OID__AllocObject(0x14", "fVar1 - fVar2"),
    },
    "0x0052f920": {
        "raw": "0052f920",
        "name": "CPositionDataType__ScaleByFloat",
        "signature": "void * __thiscall CPositionDataType__ScaleByFloat(void * this, void * rhs)",
        "tags": COMMON_TAGS | {"arithmetic", "float-rhs", "position-datatype", "scale", "vtable-slot"},
        "comment_tokens": ("0x005e4db0", "vtable slot +0x34", "x/y/z scaled"),
        "decompile_file": "0052f920_CPositionDataType__ScaleByFloat.c",
        "decompile_tokens": ("+ 0x34", "OID__AllocObject(0x14", "fVar5 *"),
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
        BASE / "wave576_apply_dry.log",
        {"updated": 0, "skipped": 13, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "wave576_apply.log",
        {"updated": 13, "skipped": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "wave576_apply_final_dry.log",
        {"updated": 0, "skipped": 13, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )

    expected_counts = {
        "post_metadata.tsv": 13,
        "post_tags.tsv": 13,
        "post_xrefs.tsv": 26,
        "post_target_instructions.tsv": 2977,
        "post_decompile/index.tsv": 13,
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
        ("005e4e4c", "CStringDataType__ScalarDeletingDestructor", "005e4df8", "CThingPtrDataType__ScalarDeletingDestructor", "005e4da4"),
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
        else:
            decomp_text = read_text(BASE / "post_decompile" / spec["decompile_file"])
            require_tokens(f"{address} decompile", decomp_text, spec["decompile_tokens"], failures)

        if spec["raw"] not in instructions:
            failures.append(f"{address} missing from post_target_instructions.tsv")
        if spec["name"] not in xrefs and address not in xrefs:
            failures.append(f"{address} missing from post_xrefs.tsv")

    backup = json.loads(read_text(BASE / "wave576_backup_summary.json"))
    if backup.get("status") != "PASS":
        failures.append(f"backup status mismatch: {backup.get('status')}")
    if not str(backup.get("destination", "")).endswith("BEA_20260519-023729_post_wave576_datatype_string_thing_position_tail_verified"):
        failures.append(f"backup destination mismatch: {backup.get('destination')}")
    if backup.get("fileCount") != 19:
        failures.append(f"backup fileCount mismatch: {backup.get('fileCount')}")
    if int(backup.get("byteCount", -1)) != 160402311:
        failures.append(f"backup byteCount mismatch: {backup.get('byteCount')}")
    if backup.get("sourceManifestHash") != "9A6A9EEF1378754A0E241C8EDF1871EB9F4AC3D6A9A33928CB5922E10C3BE0BC":
        failures.append("backup sourceManifestHash mismatch")
    if backup.get("destinationManifestHash") != backup.get("sourceManifestHash"):
        failures.append("backup source/destination manifest hash mismatch")

    queue = json.loads(read_text(QUEUE_JSON))
    expected_queue = {
        "totalFunctions": 6093,
        "commentlessFunctionCount": 3176,
        "undefinedSignatureCount": 1430,
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
    if head.get("address") != "0x0052f9a0" or head.get("name") != "CEventFunction__Destructor":
        failures.append(f"queue head mismatch: {head}")

    require_doc_tokens(
        PUBLIC_NOTE,
        (
            "Ghidra DataType String/Thing/Position Tail Wave576 Readiness Note",
            "CStringDataType__Clone",
            "CThingPtrDataType__ScalarDeletingDestructor",
            "CPositionDataType__ScaleByFloat",
            "2917 / 6093 = 47.87%",
            "2866 / 6093 = 47.04%",
            "BEA_20260519-023729_post_wave576_datatype_string_thing_position_tail_verified",
        ),
        failures,
    )
    require_doc_tokens(
        GHIDRA_REFERENCE,
        (
            "Current Signature Caveat: MissionScript DataType String/Thing/Position Tail (2026-05-19)",
            "Wave576 datatype string/thing-pointer/position tail hardened thirteen adjacent rows",
            "void * __thiscall CStringDataType__Clone(void * this)",
            "runtime MissionScript behavior",
        ),
        failures,
    )
    require_doc_tokens(
        CAMPAIGN,
        (
            "Fresh headless export on 2026-05-19 after Wave576",
            "Current datatype string/thing/position tail follow-up",
            "Wave 576: DataType String/Thing/Position Tail",
            "2917/6093 = 47.87%",
        ),
        failures,
    )
    require_doc_tokens(
        FUNCTION_INDEX,
        (
            "Latest saved-correction note: Wave576",
            "CStringDataType__Clone",
            "CEventFunction__Destructor",
            "Post-Wave576 queue telemetry",
        ),
        failures,
    )
    require_doc_tokens(
        DATATYPE_DOC,
        (
            "Wave576 String/Thing/Position Static Read-Back",
            "void * __thiscall CStringDataType__Clone(void * this)",
            "void * __thiscall CPositionDataType__ScaleByFloat(void * this, void * rhs)",
            "shared CDataType scalar-deleting destructor wrapper",
        ),
        failures,
    )
    require_doc_tokens(
        BACKLOG,
        (
            "Ghidra datatype string/thing/position tail Wave576 signature/comment hardening",
            "ApplyDataTypeStringThingPositionTailWave576.java",
            "160402311",
        ),
        failures,
    )
    require_doc_tokens(
        LEDGER,
        (
            "Ghidra datatype string/thing/position tail Wave576 signature/comment hardening",
            "CPositionDataType__ScaleByFloat",
            "BEA_20260519-023729_post_wave576_datatype_string_thing_position_tail_verified",
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
        print("FAIL: Wave576 datatype string/thing-position probe found drift:")
        for failure in failures:
            print(f"- {failure}")
    else:
        print("PASS: Wave576 datatype string/thing-position artifacts validated.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
