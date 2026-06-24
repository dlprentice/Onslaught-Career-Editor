#!/usr/bin/env python3
"""Validate the recovered Ghidra caller boundary for the shadow-heightfield helper."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "heightfield-shadow-caller-boundary" / "current"

CALLER_ADDRESS = "0x00447120"
CALLER_NAME = "VFuncSlot_1c_00447120"
TARGET_ADDRESS = "0x00402dd0"
TARGET_OLD_NAME = "CHeightField_Unk_0047eb80__Wrapper_00402dd0"
TARGET_NAME = "ShadowHeightfield__AnyBoundsCornerAboveSampledHeight"
CALLSITE_ADDRESS = "0x004478a3"
VTABLE_SLOT_ADDRESS = "0x005e1ee0"
VTABLE_SLOT = "28"

DEFAULT_METADATA = BASE / "metadata_readback.tsv"
DEFAULT_TARGET_INDEX = BASE / "target_decompile_readback" / "index.tsv"
DEFAULT_TARGET_DECOMPILE_DIR = BASE / "target_decompile_readback"
DEFAULT_CALLER_INDEX = BASE / "caller_decompile_readback" / "index.tsv"
DEFAULT_CALLER_DECOMPILE_DIR = BASE / "caller_decompile_readback"
DEFAULT_TARGET_XREFS = BASE / "target_xrefs_readback.tsv"
DEFAULT_CALLER_XREFS = BASE / "caller_xrefs_readback.tsv"
DEFAULT_CALLER_INSTRUCTIONS = BASE / "caller_instructions_readback.tsv"
DEFAULT_POINTER_TABLE = BASE / "pointer_table_005e1e70.tsv"
DEFAULT_CREATE_APPLY = BASE / "create_function_apply.tsv"
DEFAULT_OUT = BASE / "heightfield-shadow-caller-boundary.json"

TARGET_DECOMPILE_TOKENS = [
    TARGET_NAME,
    "CStaticShadows__SampleShadowHeightBilinear",
    "DAT_006fbdfc",
    "return 1",
    "return 0",
]
TARGET_COMMENT_TOKENS = [
    "Shadow/heightfield",
    "CStaticShadows__SampleShadowHeightBilinear",
    "Proof-boundary",
    "runtime",
]
CALLER_COMMENT_TOKENS = [
    "Recovered virtual-table caller boundary",
    VTABLE_SLOT_ADDRESS,
    TARGET_NAME,
    "Proof-boundary",
]
CALLER_DECOMPILE_TOKENS = [
    CALLER_NAME,
    TARGET_NAME,
]


def relative(path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if value in {"", "<none>", "<no_function>", "<no_instruction>"}:
        return value
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def compact(value: str) -> str:
    return "".join(value.lower().split())


def has_token(text: str, token: str) -> bool:
    return compact(token) in compact(text)


def unescape_tsv(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_metadata(path: Path) -> dict[str, dict[str, str]]:
    rows = read_tsv(path)
    for row in rows:
        row["address"] = normalize_address(row.get("address", ""))
        row["comment"] = unescape_tsv(row.get("comment", ""))
    return {row["address"]: row for row in rows if row.get("address")}


def read_index(path: Path) -> dict[str, dict[str, str]]:
    rows = read_tsv(path)
    for row in rows:
        row["address"] = normalize_address(row.get("address", ""))
    return {row["address"]: row for row in rows if row.get("address")}


def read_xrefs(path: Path) -> list[dict[str, str]]:
    rows = read_tsv(path)
    for row in rows:
        row["target_addr_norm"] = normalize_address(row.get("target_addr", ""))
        row["from_addr_norm"] = normalize_address(row.get("from_addr", ""))
        row["from_function_addr_norm"] = normalize_address(row.get("from_function_addr", ""))
    return rows


def read_instructions(path: Path) -> list[dict[str, str]]:
    rows = read_tsv(path)
    for row in rows:
        row["target_addr_norm"] = normalize_address(row.get("target_addr", ""))
        row["instruction_addr_norm"] = normalize_address(row.get("instruction_addr", ""))
        row["function_entry_norm"] = normalize_address(row.get("function_entry", ""))
    return rows


def read_pointer_table(path: Path) -> list[dict[str, str]]:
    rows = read_tsv(path)
    for row in rows:
        row["entry_addr_norm"] = normalize_address(row.get("entry_addr", ""))
        row["ptr_norm"] = normalize_address(row.get("ptr", ""))
    return rows


def read_create_report(path: Path) -> list[dict[str, str]]:
    rows = read_tsv(path)
    for row in rows:
        row["address_norm"] = normalize_address(row.get("address", ""))
    return rows


def find_decompile_file(decompile_dir: Path, address: str) -> Path | None:
    if not decompile_dir.is_dir():
        return None
    matches = sorted(decompile_dir.glob(f"{normalize_address(address)[2:]}_*.c"))
    return matches[0] if matches else None


def read_text(path: Path | None) -> str:
    if path is None or not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def build_report(
    *,
    metadata_path: Path = DEFAULT_METADATA,
    target_decompile_index_path: Path = DEFAULT_TARGET_INDEX,
    target_decompile_dir: Path = DEFAULT_TARGET_DECOMPILE_DIR,
    caller_decompile_index_path: Path = DEFAULT_CALLER_INDEX,
    caller_decompile_dir: Path = DEFAULT_CALLER_DECOMPILE_DIR,
    target_xrefs_path: Path = DEFAULT_TARGET_XREFS,
    caller_xrefs_path: Path = DEFAULT_CALLER_XREFS,
    caller_instructions_path: Path = DEFAULT_CALLER_INSTRUCTIONS,
    pointer_table_path: Path = DEFAULT_POINTER_TABLE,
    create_apply_path: Path = DEFAULT_CREATE_APPLY,
) -> dict[str, object]:
    metadata_path = resolve(metadata_path)
    target_decompile_index_path = resolve(target_decompile_index_path)
    target_decompile_dir = resolve(target_decompile_dir)
    caller_decompile_index_path = resolve(caller_decompile_index_path)
    caller_decompile_dir = resolve(caller_decompile_dir)
    target_xrefs_path = resolve(target_xrefs_path)
    caller_xrefs_path = resolve(caller_xrefs_path)
    caller_instructions_path = resolve(caller_instructions_path)
    pointer_table_path = resolve(pointer_table_path)
    create_apply_path = resolve(create_apply_path)

    failures: list[str] = []
    for label, path in (
        ("metadata read-back", metadata_path),
        ("target decompile index", target_decompile_index_path),
        ("caller decompile index", caller_decompile_index_path),
        ("target xrefs", target_xrefs_path),
        ("caller xrefs", caller_xrefs_path),
        ("caller instructions", caller_instructions_path),
        ("pointer table", pointer_table_path),
        ("create apply report", create_apply_path),
    ):
        if not path.is_file():
            failures.append(f"missing {label}: {relative(path)}")
    for label, path in (("target decompile dir", target_decompile_dir), ("caller decompile dir", caller_decompile_dir)):
        if not path.is_dir():
            failures.append(f"missing {label}: {relative(path)}")

    metadata = read_metadata(metadata_path)
    target_index = read_index(target_decompile_index_path)
    caller_index = read_index(caller_decompile_index_path)
    target_xrefs = read_xrefs(target_xrefs_path)
    caller_xrefs = read_xrefs(caller_xrefs_path)
    caller_instructions = read_instructions(caller_instructions_path)
    pointer_table = read_pointer_table(pointer_table_path)
    create_rows = read_create_report(create_apply_path)

    target_row = metadata.get(TARGET_ADDRESS)
    if not target_row:
        failures.append(f"{TARGET_ADDRESS}: missing metadata read-back row")
        target_name = None
    else:
        target_name = target_row.get("name")
        target_comment = target_row.get("comment", "")
        if target_row.get("status") != "OK":
            failures.append(f"{TARGET_ADDRESS}: metadata status is not OK")
        if target_name != TARGET_NAME:
            failures.append(f"{TARGET_ADDRESS}: expected {TARGET_NAME}, got {target_name or '<blank>'}")
        if target_name == TARGET_OLD_NAME:
            failures.append(f"{TARGET_ADDRESS}: stale target name survived ({TARGET_OLD_NAME})")
        for token in TARGET_COMMENT_TOKENS:
            if not has_token(target_comment, token):
                failures.append(f"{TARGET_ADDRESS}: comment missing token {token!r}")

    caller_row = metadata.get(CALLER_ADDRESS)
    if not caller_row:
        failures.append(f"{CALLER_ADDRESS}: missing metadata read-back row")
        caller_name = None
    else:
        caller_name = caller_row.get("name")
        caller_comment = caller_row.get("comment", "")
        if caller_row.get("status") != "OK":
            failures.append(f"{CALLER_ADDRESS}: metadata status is not OK")
        if caller_name != CALLER_NAME:
            failures.append(f"{CALLER_ADDRESS}: expected {CALLER_NAME}, got {caller_name or '<blank>'}")
        for token in CALLER_COMMENT_TOKENS:
            if not has_token(caller_comment, token):
                failures.append(f"{CALLER_ADDRESS}: comment missing token {token!r}")

    target_index_row = target_index.get(TARGET_ADDRESS)
    if not target_index_row or target_index_row.get("status") != "OK":
        failures.append(f"{TARGET_ADDRESS}: missing OK target decompile index row")
    elif target_index_row.get("name") != TARGET_NAME:
        failures.append(f"{TARGET_ADDRESS}: target decompile index has unexpected name {target_index_row.get('name')}")

    caller_index_row = caller_index.get(CALLER_ADDRESS)
    if not caller_index_row or caller_index_row.get("status") != "OK":
        failures.append(f"{CALLER_ADDRESS}: missing OK caller decompile index row")
    elif caller_index_row.get("name") != CALLER_NAME:
        failures.append(f"{CALLER_ADDRESS}: caller decompile index has unexpected name {caller_index_row.get('name')}")

    target_decompile_file = find_decompile_file(target_decompile_dir, TARGET_ADDRESS)
    target_text = read_text(target_decompile_file)
    for token in TARGET_DECOMPILE_TOKENS:
        if not has_token(target_text, token):
            failures.append(f"{TARGET_ADDRESS}: target decompile missing token {token!r}")
    if has_token(target_text, TARGET_OLD_NAME):
        failures.append(f"{TARGET_ADDRESS}: target decompile still contains stale name {TARGET_OLD_NAME}")

    caller_decompile_file = find_decompile_file(caller_decompile_dir, CALLER_ADDRESS)
    caller_text = read_text(caller_decompile_file)
    for token in CALLER_DECOMPILE_TOKENS:
        if not has_token(caller_text, token):
            failures.append(f"{CALLER_ADDRESS}: caller decompile missing token {token!r}")

    target_call_rows = [
        row
        for row in target_xrefs
        if row.get("target_addr_norm") == TARGET_ADDRESS
        and row.get("from_addr_norm") == CALLSITE_ADDRESS
        and row.get("from_function_addr_norm") == CALLER_ADDRESS
        and row.get("from_function") == CALLER_NAME
        and row.get("ref_type") == "UNCONDITIONAL_CALL"
    ]
    if not target_call_rows:
        failures.append(f"{TARGET_ADDRESS}: missing xref from recovered caller {CALLER_NAME} at {CALLSITE_ADDRESS}")

    caller_data_rows = [
        row
        for row in caller_xrefs
        if row.get("target_addr_norm") == CALLER_ADDRESS
        and row.get("from_addr_norm") == VTABLE_SLOT_ADDRESS
        and row.get("ref_type") == "DATA"
    ]
    if not caller_data_rows:
        failures.append(f"{CALLER_ADDRESS}: missing DATA xref from table slot {VTABLE_SLOT_ADDRESS}")

    prologue_rows = [
        row
        for row in caller_instructions
        if row.get("instruction_addr_norm") == CALLER_ADDRESS
        and row.get("function_entry_norm") == CALLER_ADDRESS
        and row.get("function_name") == CALLER_NAME
        and row.get("mnemonic") == "SUB"
        and "0x424" in row.get("operands", "")
    ]
    if not prologue_rows:
        failures.append(f"{CALLER_ADDRESS}: missing recovered prologue instruction row")

    callsite_rows = [
        row
        for row in caller_instructions
        if row.get("instruction_addr_norm") == CALLSITE_ADDRESS
        and row.get("function_entry_norm") == CALLER_ADDRESS
        and row.get("function_name") == CALLER_NAME
        and row.get("mnemonic") == "CALL"
        and TARGET_ADDRESS in row.get("operands", "")
    ]
    if not callsite_rows:
        failures.append(f"{CALLER_ADDRESS}: missing callsite instruction row for {TARGET_ADDRESS}")

    ret_rows = [
        row
        for row in caller_instructions
        if row.get("instruction_addr_norm") == "0x00447a38"
        and row.get("function_entry_norm") == CALLER_ADDRESS
        and row.get("function_name") == CALLER_NAME
        and row.get("mnemonic") == "RET"
    ]
    if not ret_rows:
        failures.append(f"{CALLER_ADDRESS}: missing recovered RET boundary at 0x00447a38")

    slot_rows = [
        row
        for row in pointer_table
        if row.get("slot") == VTABLE_SLOT
        and row.get("entry_addr_norm") == VTABLE_SLOT_ADDRESS
        and row.get("ptr_norm") == CALLER_ADDRESS
        and row.get("ptr_name") == CALLER_NAME
    ]
    if not slot_rows:
        failures.append(f"{CALLER_ADDRESS}: pointer table slot {VTABLE_SLOT} at {VTABLE_SLOT_ADDRESS} does not resolve to {CALLER_NAME}")

    create_ok_rows = [
        row
        for row in create_rows
        if row.get("address_norm") == CALLER_ADDRESS
        and row.get("name") == CALLER_NAME
        and row.get("status") in {"created", "renamed_existing", "already_exists"}
    ]
    if not create_ok_rows:
        failures.append(f"{CALLER_ADDRESS}: create/apply report does not show a saved {CALLER_NAME} function")

    return {
        "schema": "ghidra-heightfield-shadow-caller-boundary.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not failures else "FAIL",
        "targetAddress": TARGET_ADDRESS,
        "targetName": target_name,
        "callerAddress": CALLER_ADDRESS,
        "callerName": caller_name,
        "targetCallerFunction": target_call_rows[0].get("from_function") if target_call_rows else None,
        "tableSlotAddress": VTABLE_SLOT_ADDRESS,
        "tableSlot": VTABLE_SLOT,
        "paths": {
            "metadata": relative(metadata_path),
            "targetDecompileIndex": relative(target_decompile_index_path),
            "targetDecompileDir": relative(target_decompile_dir),
            "callerDecompileIndex": relative(caller_decompile_index_path),
            "callerDecompileDir": relative(caller_decompile_dir),
            "targetXrefs": relative(target_xrefs_path),
            "callerXrefs": relative(caller_xrefs_path),
            "callerInstructions": relative(caller_instructions_path),
            "pointerTable": relative(pointer_table_path),
            "createApply": relative(create_apply_path),
        },
        "findings": [
            f"{CALLER_ADDRESS} is a recovered function boundary with saved name {CALLER_NAME}.",
            f"{TARGET_ADDRESS} is renamed to {TARGET_NAME} and called from {CALLSITE_ADDRESS} inside {CALLER_NAME}.",
            f"{VTABLE_SLOT_ADDRESS} table slot {VTABLE_SLOT} points to {CALLER_ADDRESS}.",
        ],
        "notProven": [
            "This does not prove the exact vtable owner or source method identity.",
            "This does not prove parameter/local types, class layout, or function signature correctness.",
            "This does not prove runtime shadow behavior.",
        ],
        "failures": failures,
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="exit non-zero when the report fails")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="write JSON report")
    args = parser.parse_args(argv)

    report = build_report()
    out_path = resolve(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"{report['status']}: wrote {relative(out_path)}")
    if report["failures"]:
        for failure in report["failures"]:
            print(f" - {failure}")
    return 1 if args.check and report["status"] != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
