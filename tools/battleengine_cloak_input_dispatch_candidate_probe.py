#!/usr/bin/env python3
"""Validate bounded cloak input-dispatch candidate evidence.

This probe checks a narrow retail-control path:

- the controls UI remap evidence maps action 0x4C to persisted entry 0x3B
  with binding type 8;
- the retail dispatch jump table maps action 0x3B to the call site that invokes
  the current candidate cloak latch helper at 0x0040d4d0;
- the Ghidra xref/instruction exports agree with that call path.

It intentionally does not claim exact source CBattleEngine::HandleCloak identity
or runtime cloak activation.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import struct
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_ROOT = ROOT / "subagents" / "battleengine-cloak-input-dispatch-candidate" / "current"
DEFAULT_BEA_EXE = Path(
    os.environ.get("BEA_EXE", r"C:\Program Files (x86)\Steam\steamapps\common\Battle Engine Aquila\BEA.exe")
)
DEFAULT_OUT = DEFAULT_ARTIFACT_ROOT / "cloak-input-dispatch-candidate.json"

IMAGE_BASE = 0x400000
PRIMARY_JUMP_TABLE_VA = 0x004D3434
PRIMARY_INDEX_TABLE_VA = 0x004D345C
PRIMARY_JUMP_TABLE_COUNT = 10
PRIMARY_INDEX_TABLE_COUNT = 0x30

EXPECTED_DECOMPILES = {
    "0x0040d4d0": "CGeneralVolume__Update4ACLatchFromHeightAndA0",
    "0x00453f50": "Controls__DispatchRemap",
    "0x00455010": "ControlsUI__RenderBindingsList",
    "0x004565d0": "OptionsEntries__SetBindingSlot",
}


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def normalize_addr(value: str) -> str:
    text = str(value or "").strip().lower()
    if text in {"", "<none>", "<no_function>"}:
        return text
    if text.startswith("0x"):
        text = text[2:]
    return "0x" + text.zfill(8)


def normalized(text: str) -> str:
    return "".join(str(text).split()).lower()


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def read_dwords(handle, va: int, count: int) -> list[int]:
    handle.seek(va - IMAGE_BASE)
    return [struct.unpack("<I", handle.read(4))[0] for _ in range(count)]


def read_bytes(handle, va: int, count: int) -> list[int]:
    handle.seek(va - IMAGE_BASE)
    return list(handle.read(count))


def read_retail_jump_tables(bea_exe: Path) -> dict[str, object]:
    with bea_exe.open("rb") as handle:
        primary_jump_table = read_dwords(handle, PRIMARY_JUMP_TABLE_VA, PRIMARY_JUMP_TABLE_COUNT)
        primary_index_table = read_bytes(handle, PRIMARY_INDEX_TABLE_VA, PRIMARY_INDEX_TABLE_COUNT)

    mapping = []
    for index, target_index in enumerate(primary_index_table[:0x2F]):
        action = 0x10 + index
        target = primary_jump_table[target_index] if target_index < len(primary_jump_table) else None
        mapping.append(
            {
                "action": f"0x{action:02x}",
                "targetIndex": target_index,
                "target": f"0x{target:08x}" if target is not None else "<bad>",
            }
        )

    return {
        "primaryJumpTable": [f"0x{value:08x}" for value in primary_jump_table],
        "primaryIndexTableLength": len(primary_index_table),
        "actionMapping": mapping,
    }


def find_decompile_file(decompile_dir: Path, address: str, name: str) -> Path:
    prefix = normalize_addr(address)[2:]
    candidates = sorted(decompile_dir.glob(f"{prefix}_{name}.c"))
    return candidates[0] if candidates else decompile_dir / f"{prefix}_{name}.c"


def build_report(artifact_root: Path, bea_exe: Path) -> dict[str, object]:
    decompile_dir = artifact_root / "decomp"
    xrefs_path = artifact_root / "xrefs.tsv"
    callsite_path = artifact_root / "callsite-instructions.tsv"
    failures: list[str] = []

    if not bea_exe.is_file():
        failures.append(f"missing BEA.exe for read-only table check: {bea_exe}")
        jump_tables: dict[str, object] = {"primaryJumpTable": [], "actionMapping": []}
    else:
        jump_tables = read_retail_jump_tables(bea_exe)

    index_rows = read_tsv(decompile_dir / "index.tsv")
    if not index_rows:
        failures.append(f"missing or empty decompile index: {relative(decompile_dir / 'index.tsv')}")
    for address, name in EXPECTED_DECOMPILES.items():
        matches = [
            row
            for row in index_rows
            if normalize_addr(row.get("address", "")) == address and row.get("name") == name and row.get("status") == "OK"
        ]
        if not matches:
            failures.append(f"decompile index lacks OK row for {address} {name}")

    controls_text = read_text(find_decompile_file(decompile_dir, "0x00453f50", "Controls__DispatchRemap"))
    if "case 0x4c:" not in controls_text:
        failures.append("Controls__DispatchRemap decompile lacks case 0x4c")
    if "(*callback)(key_or_value,0x3b,8);" not in normalized(controls_text):
        failures.append("Controls__DispatchRemap decompile lacks action 0x4c -> entry 0x3b/type 8 callback")

    xref_rows = read_tsv(xrefs_path)
    if not xref_rows:
        failures.append(f"missing or empty xref export: {relative(xrefs_path)}")
    else:
        expected_xref = [
            row
            for row in xref_rows
            if normalize_addr(row.get("target_addr", "")) == "0x0040d4d0"
            and normalize_addr(row.get("from_addr", "")) == "0x004d32e2"
            and row.get("target_name") == "CGeneralVolume__Update4ACLatchFromHeightAndA0"
            and row.get("ref_type") == "UNCONDITIONAL_CALL"
        ]
        if not expected_xref:
            failures.append("xref export lacks 0x004d32e2 -> 0x0040d4d0 unconditional call")

    instruction_rows = read_tsv(callsite_path)
    if not instruction_rows:
        failures.append(f"missing or empty callsite instruction export: {relative(callsite_path)}")
    else:
        instruction_by_addr = {normalize_addr(row.get("instruction_addr", "")): row for row in instruction_rows}
        required_instructions = {
            "0x004d329d": ("MOV", "byte ptr [EAX + 0x4d345c]"),
            "0x004d32a3": ("JMP", "dword ptr [EDX*0x4 + 0x4d3434]"),
            "0x004d32e2": ("CALL", "0x0040d4d0"),
        }
        for address, (mnemonic, operand_token) in required_instructions.items():
            row = instruction_by_addr.get(address)
            if not row:
                failures.append(f"callsite export lacks instruction {address}")
                continue
            if row.get("mnemonic") != mnemonic or operand_token not in row.get("operands", ""):
                failures.append(
                    f"callsite {address} mismatch: expected {mnemonic} {operand_token}, got "
                    f"{row.get('mnemonic')} {row.get('operands')}"
                )

    action_3b = next(
        (entry for entry in jump_tables.get("actionMapping", []) if entry.get("action") == "0x3b"),
        None,
    )
    if action_3b is None:
        failures.append("retail primary action mapping lacks action 0x3b")
    elif action_3b.get("targetIndex") != 6 or action_3b.get("target") != "0x004d32e2":
        failures.append(f"action 0x3b mapping mismatch: {action_3b}")

    return {
        "schema": "battleengine-cloak-input-dispatch-candidate.v1",
        "status": "pass" if not failures else "blocked",
        "artifactRoot": relative(artifact_root),
        "beaExeInput": "read-only local BEA.exe path supplied by operator/environment",
        "decompileIndex": relative(decompile_dir / "index.tsv"),
        "xrefExport": relative(xrefs_path),
        "callsiteInstructions": relative(callsite_path),
        "retailJumpTables": jump_tables,
        "failures": failures,
        "whatIsProven": [
            "Current Controls__DispatchRemap decompile maps UI action 0x4C to persisted entry 0x3B with binding type 8.",
            "Read-only retail jump-table bytes map action 0x3B to dispatch call site 0x004d32e2.",
            "The Ghidra xref export confirms 0x004d32e2 calls CGeneralVolume__Update4ACLatchFromHeightAndA0 at 0x0040d4d0.",
            "The instruction export shows the action-index table at 0x004d345c and jump table at 0x004d3434 feed that call site.",
        ],
        "notProven": [
            "Exact source-to-retail identity for CBattleEngine::HandleCloak, Cloak, Decloak, Render, or WeaponFired.",
            "Runtime cloak activation in the tested level/profile state.",
            "Retail RF_CLOAKED render-flag identity.",
            "Weapon-fired stealth reset identity.",
            "Runtime fire-while-cloaked behavior.",
            "Ghidra rename-map mutation or project semantic promotion.",
            "Rebuildable open-source gameplay implementation.",
        ],
        "privacy": "Report stores repo-relative artifact paths, public addresses, sanitized jump-table targets, and proof boundaries only; raw decompile/instruction exports remain ignored under subagents/.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check BattleEngine cloak input-dispatch candidate evidence.")
    parser.add_argument("--check", action="store_true", help="run the candidate probe")
    parser.add_argument("--artifact-root", type=Path, default=DEFAULT_ARTIFACT_ROOT, help="ignored Ghidra export root")
    parser.add_argument("--bea-exe", type=Path, default=DEFAULT_BEA_EXE, help="read-only BEA.exe path")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="ignored JSON report path")
    parser.add_argument("--json", action="store_true", help="print full JSON report")
    args = parser.parse_args()
    if not args.check:
        parser.error("expected --check")

    artifact_root = args.artifact_root if args.artifact_root.is_absolute() else ROOT / args.artifact_root
    out = args.out if args.out.is_absolute() else ROOT / args.out
    try:
        out.resolve().relative_to((ROOT / "subagents").resolve())
    except ValueError:
        print(f"Refusing to write report outside subagents/: {out}")
        return 1

    report = build_report(artifact_root, args.bea_exe)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8", newline="\n")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("BattleEngine cloak input-dispatch candidate probe")
        print(f"Status: {report['status']}")
        action_3b = next(
            (
                entry
                for entry in report["retailJumpTables"].get("actionMapping", [])
                if entry.get("action") == "0x3b"
            ),
            {},
        )
        print(f"Action 0x3B target: {action_3b.get('target', '<missing>')}")
        print(f"Failures: {len(report['failures'])}")
        for failure in report["failures"]:
            print(f"- FAIL: {failure}")

    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
