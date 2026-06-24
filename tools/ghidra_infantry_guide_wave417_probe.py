#!/usr/bin/env python3
"""Validate the Wave417 CInfantryGuide Ghidra boundary/signature correction tranche."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave417-infantry-guide" / "current"

COMMON_TAGS = {"static-reaudit", "infantry-guide-wave417", "retail-binary-evidence"}

TARGETS: dict[str, dict[str, object]] = {
    "0x0048a3c0": {
        "name": "CInfantryGuide__ctor",
        "signature": "void * __thiscall CInfantryGuide__ctor(void * this, void * owner_unit)",
        "commentTokens": [
            "CInfantryGuide constructor",
            "CGuide__ctor_base",
            "owner_unit",
            "vtable 0x005dbfa8",
            "two 0x54 guide buffers",
            "event 2000",
            "runtime guide behavior",
            "rebuild parity remain unproven",
        ],
        "tags": {"infantry-guide", "constructor", "signature-corrected", "comment-hardened"},
        "instructionEvidence": [("CALL", "0x0047e290"), ("RET", "0x4")],
    },
    "0x0048a4b0": {
        "name": "SharedGuide__GetField24Block_0048a4b0",
        "signature": "void * __fastcall SharedGuide__GetField24Block_0048a4b0(void * this)",
        "commentTokens": [
            "Recovered shared guide vtable helper",
            "returns this+0x24",
            "CInfantryGuide",
            "CGroundVehicleGuide",
            "exact field semantics",
            "runtime guide behavior",
            "remain unproven",
        ],
        "tags": {"guide", "shared-helper", "function-boundary", "signature-hardened", "comment-hardened"},
        "instructionEvidence": [("LEA", "[ECX + 0x24]"), ("RET", "")],
    },
    "0x0048a4c0": {
        "name": "CInfantryGuide__scalar_deleting_dtor",
        "signature": "void * __thiscall CInfantryGuide__scalar_deleting_dtor(void * this, byte flags)",
        "commentTokens": [
            "scalar-deleting destructor wrapper",
            "CInfantryGuide__dtor",
            "flags bit 0",
            "OID__FreeObject",
            "returns this",
            "runtime cleanup behavior unproven",
        ],
        "tags": {"infantry-guide", "destructor", "owner-corrected", "signature-corrected", "comment-hardened"},
        "instructionEvidence": [("TEST", "[ESP + 0x8]"), ("RET", "0x4")],
    },
    "0x0048a4e0": {
        "name": "CInfantryGuide__dtor",
        "signature": "void __fastcall CInfantryGuide__dtor(void * this)",
        "commentTokens": [
            "destructor body reached by CInfantryGuide scalar deleting destructor",
            "reader link at this+0x44",
            "frees guide buffers",
            "+0x3c/+0x34",
            "CMonitor__Shutdown",
            "runtime cleanup behavior unproven",
        ],
        "tags": {"infantry-guide", "destructor", "signature-hardened", "comment-hardened"},
        "instructionEvidence": [("CALL", "0x004e5bd0"), ("CALL", "0x004bac40")],
    },
    "0x0048a570": {
        "name": "CInfantryGuide__UpdateGuidanceState_0048a570",
        "signature": "void __fastcall CInfantryGuide__UpdateGuidanceState_0048a570(void * this)",
        "commentTokens": [
            "Recovered CInfantryGuide vtable slot 3 body",
            "owner/reader positions",
            "guide state",
            "target line",
            "source body is absent",
            "runtime guide behavior",
            "rebuild parity remain unproven",
        ],
        "tags": {"infantry-guide", "vtable-slot", "function-boundary", "signature-hardened", "comment-hardened"},
        "instructionEvidence": [("SUB", "0x48"), ("RET", "")],
    },
    "0x0048ac70": {
        "name": "CInfantryGuide__HandleTargetRecheckEvent",
        "signature": "void __thiscall CInfantryGuide__HandleTargetRecheckEvent(void * this, void * event)",
        "commentTokens": [
            "Function-boundary correction",
            "starts at 0x0048ac70",
            "not stale mid-body 0x0048ac80",
            "event id 0x7d0",
            "CInfantryGuide__SelectNearestTargetReader",
            "reschedules event 2000",
            "runtime guide behavior unproven",
        ],
        "tags": {"infantry-guide", "event-handler", "function-boundary", "signature-corrected", "comment-hardened"},
        "instructionEvidence": [("CMP", "[EDI + 0x4]"), ("RET", "0x4")],
    },
    "0x0048ace0": {
        "name": "CInfantryGuide__SelectNearestTargetReader",
        "signature": "void __fastcall CInfantryGuide__SelectNearestTargetReader(void * this)",
        "commentTokens": [
            "clears active reader at +0x44",
            "MapWho radius 1.0",
            "filters candidate flags/team",
            "nearest hostile/preferred reader",
            "threshold constants 0x005d8568/0x005dbfd0",
            "runtime target behavior unproven",
        ],
        "tags": {"infantry-guide", "target-selection", "signature-hardened", "comment-hardened"},
        "instructionEvidence": [("CALL", "0x00491ea0"), ("CALL", "0x00492c90")],
    },
}

EXPECTED_DRY = {
    "updated": 0,
    "skipped": 5,
    "created": 0,
    "would_create": 2,
    "boundary_moved": 0,
    "would_boundary_move": 1,
    "renamed": 0,
    "would_rename": 3,
    "missing": 0,
    "bad": 0,
}

EXPECTED_APPLY = {
    "updated": 7,
    "skipped": 0,
    "created": 2,
    "would_create": 0,
    "boundary_moved": 1,
    "would_boundary_move": 0,
    "renamed": 2,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}

VTABLE_EXPECTED = {
    ("0x005dbfa8", "0"): ("0x0048ac70", "CInfantryGuide__HandleTargetRecheckEvent"),
    ("0x005dbfa8", "1"): ("0x0048a4c0", "CInfantryGuide__scalar_deleting_dtor"),
    ("0x005dbfa8", "3"): ("0x0048a570", "CInfantryGuide__UpdateGuidanceState_0048a570"),
    ("0x005dbfa8", "9"): ("0x0048a4b0", "SharedGuide__GetField24Block_0048a4b0"),
    ("0x005dbd90", "9"): ("0x0048a4b0", "SharedGuide__GetField24Block_0048a4b0"),
}

OVERCLAIM_TOKENS = (
    "runtime proof",
    "runtime guide behavior proven",
    "runtime target behavior proven",
    "runtime cleanup behavior proven",
    "source identity proven",
    "source body identity proven",
    "rebuild parity proven",
    "fully re'ed",
    "100% re",
)

STALE_NAMES = {
    "CInfantryGuide__ctor_like_0048a3c0",
    "CInfantryGuide__VFunc_01_0048a4c0",
    "CInfantryGuide__SelectTargetAndScheduleRecheck",
}


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if not value or value.startswith("<"):
        return value
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def compact(value: str) -> str:
    return "".join(value.lower().split())


def token_present(text: str, token: str) -> bool:
    return compact(token) in compact(text)


def unescape(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        for key in (
            "address",
            "target_addr",
            "function_entry",
            "containing_entry",
            "vtable",
            "pointer_addr",
        ):
            if key in row and row[key]:
                row[key] = normalize_address(row[key])
        if "comment" in row:
            row["comment"] = unescape(row["comment"])
    return rows


def row_by_address(rows: list[dict[str, str]], address: str, key: str = "address") -> dict[str, str] | None:
    wanted = normalize_address(address)
    for row in rows:
        if normalize_address(row.get(key, "")) == wanted:
            return row
    return None


def parse_tags(value: str) -> set[str]:
    return {part.strip() for part in value.split(";") if part.strip()}


def parse_summary(log_text: str) -> dict[str, int]:
    match = re.search(
        r"updated=(\d+)\s+skipped=(\d+)\s+created=(\d+)\s+would_create=(\d+)\s+boundary_moved=(\d+)\s+would_boundary_move=(\d+)\s+renamed=(\d+)\s+would_rename=(\d+)\s+missing=(\d+)\s+bad=(\d+)",
        log_text,
    )
    keys = (
        "updated",
        "skipped",
        "created",
        "would_create",
        "boundary_moved",
        "would_boundary_move",
        "renamed",
        "would_rename",
        "missing",
        "bad",
    )
    if not match:
        return {key: -1 for key in keys}
    return {key: int(value) for key, value in zip(keys, match.groups())}


def compare_summary(failures: list[str], label: str, actual: dict[str, int], expected: dict[str, int]) -> None:
    for key, expected_value in expected.items():
        actual_value = actual.get(key)
        if actual_value != expected_value:
            failures.append(f"{label} summary {key}: expected {expected_value}, got {actual_value}")


def check_instruction_evidence(
    failures: list[str],
    rows: list[dict[str, str]],
    address: str,
    evidence: list[tuple[str, str]],
) -> None:
    target_rows = [row for row in rows if normalize_address(row.get("target_addr", "")) == normalize_address(address)]
    for mnemonic, operand_token in evidence:
        if not any(row.get("mnemonic", "") == mnemonic and token_present(row.get("operands", ""), operand_token) for row in target_rows):
            failures.append(f"{address} missing instruction evidence {mnemonic} {operand_token}".rstrip())


def check_vtable_slots(failures: list[str], rows: list[dict[str, str]]) -> None:
    for (vtable, slot), (pointer, name) in VTABLE_EXPECTED.items():
        matched = [
            row
            for row in rows
            if normalize_address(row.get("vtable", "")) == normalize_address(vtable)
            and row.get("slot_index") == slot
        ]
        if not matched:
            failures.append(f"missing vtable slot {vtable}[{slot}]")
            continue
        row = matched[0]
        if normalize_address(row.get("pointer_addr", "")) != normalize_address(pointer):
            failures.append(f"vtable slot {vtable}[{slot}] pointer mismatch: {row.get('pointer_addr')} != {pointer}")
        if row.get("function_name") != name:
            failures.append(f"vtable slot {vtable}[{slot}] name mismatch: {row.get('function_name')} != {name}")
        if row.get("status") != "OK":
            failures.append(f"vtable slot {vtable}[{slot}] status expected OK, got {row.get('status')}")


def check_targets(base: Path = BASE) -> list[str]:
    failures: list[str] = []
    metadata = read_tsv(base / "metadata_after.tsv")
    tags_rows = read_tsv(base / "tags_after.tsv")
    instructions = read_tsv(base / "instructions_after.tsv")
    vtable_rows = read_tsv(base / "vtable_slots_after.tsv")
    decompile_index = read_text(base / "decompile_after" / "index.tsv")

    compare_summary(failures, "dry", parse_summary(read_text(base / "apply_dry.log")), EXPECTED_DRY)
    compare_summary(failures, "apply", parse_summary(read_text(base / "apply_apply.log")), EXPECTED_APPLY)

    for address, expected in TARGETS.items():
        row = row_by_address(metadata, address)
        if row is None:
            failures.append(f"{address} missing metadata row")
            continue
        if row.get("status") != "OK":
            failures.append(f"{address} metadata status expected OK, got {row.get('status')}")
        if row.get("name") != expected["name"]:
            failures.append(f"{address} name expected {expected['name']}, got {row.get('name')}")
        if row.get("signature") != expected["signature"]:
            failures.append(f"{address} signature expected {expected['signature']}, got {row.get('signature')}")
        comment = row.get("comment", "")
        for token in expected["commentTokens"]:  # type: ignore[index]
            if not token_present(comment, str(token)):
                failures.append(f"{address} comment missing token: {token}")
        for token in OVERCLAIM_TOKENS:
            if token_present(comment, token):
                failures.append(f"{address} comment contains overclaim token: {token}")

        tag_row = row_by_address(tags_rows, address)
        if tag_row is None:
            failures.append(f"{address} missing tags row")
        else:
            actual_tags = parse_tags(tag_row.get("tags", ""))
            expected_tags = COMMON_TAGS | set(expected["tags"])  # type: ignore[arg-type]
            missing = sorted(expected_tags - actual_tags)
            if missing:
                failures.append(f"{address} tags missing {missing}")

        instruction_evidence = expected.get("instructionEvidence")
        if instruction_evidence:
            check_instruction_evidence(failures, instructions, address, instruction_evidence)  # type: ignore[arg-type]

        if normalize_address(address) not in {normalize_address(line.split("\t", 1)[0]) for line in decompile_index.splitlines()[1:] if line.strip()}:
            failures.append(f"{address} missing from decompile index")

    stale_row = row_by_address(metadata, "0x0048ac80")
    if stale_row is None:
        failures.append("0x0048ac80 stale mid-body metadata row missing")
    elif stale_row.get("status") != "MISSING":
        failures.append(f"0x0048ac80 expected MISSING after boundary move, got {stale_row.get('status')}")

    stale_metadata_names = [row.get("name", "") for row in metadata if row.get("name", "") in STALE_NAMES]
    if stale_metadata_names:
        failures.append(f"stale InfantryGuide names remain in metadata_after.tsv: {stale_metadata_names}")

    check_vtable_slots(failures, vtable_rows)
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=BASE, help="Wave417 artifact directory")
    parser.add_argument("--check", action="store_true", help="Return non-zero when validation fails")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    args = parser.parse_args(argv)

    failures = check_targets(args.base)
    result = {
        "status": "PASS" if not failures else "FAIL",
        "base": str(args.base),
        "target_count": len(TARGETS),
        "failures": failures,
    }
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Status: {result['status']}")
        print(f"Targets: {result['target_count']}")
        if failures:
            print("Failures:")
            for failure in failures:
                print(f"- {failure}")
    if failures and args.check:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
