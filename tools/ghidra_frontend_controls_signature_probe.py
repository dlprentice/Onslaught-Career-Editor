#!/usr/bin/env python3
"""Validate the Wave370 frontend/control-binding Ghidra signature tranche."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

DEFAULT_ROOT = Path("subagents/ghidra-static-reaudit/frontend-controls-wave370/current")
OUTPUT_NAME = "frontend-controls-signature.json"

COMMON_TAGS = {
    "static-reaudit",
    "frontend-controls-wave370",
    "retail-binary-evidence",
}


def target(name: str, signature: str, comment_tokens: list[str], tags: list[str]) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "commentTokens": comment_tokens,
        "tags": tags,
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x00453460": target(
        "OptionsEntries__InitDefaultDualBindingsTable",
        "void __cdecl OptionsEntries__InitDefaultDualBindingsTable(void)",
        ["dual-binding", "DAT_00677af0", "16 normal entries", "sentinel", "remain unproven"],
        ["controls", "options-entry", "signature-hardened"],
    ),
    "0x00453970": target(
        "CControllerDefinition__InitDefaults",
        "void __thiscall CControllerDefinition__InitDefaults(void * this)",
        ["vtable 0x005db404", "+0x04", "+0x2c", "remain unproven"],
        ["controls", "controller-definition", "signature-hardened"],
    ),
    "0x004539b0": target(
        "CControllerDefinition__scalar_deleting_dtor",
        "void * __thiscall CControllerDefinition__scalar_deleting_dtor(void * this, int flags)",
        ["scalar deleting", "CControllerDefinition__dtor", "remain unproven"],
        ["controls", "controller-definition", "signature-hardened"],
    ),
    "0x004539d0": target(
        "CControllerDefinition__dtor",
        "void __thiscall CControllerDefinition__dtor(void * this)",
        ["key-sink", "g_ControlRemapActive", "+0x2c", "remain unproven"],
        ["controls", "controller-definition", "signature-hardened"],
    ),
    "0x00453ac0": target(
        "SharedVFunc__NoOp_Ret0C",
        "void __stdcall SharedVFunc__NoOp_Ret0C(int unused0, int unused1, int unused2)",
        ["RET 0x0c", "shared vtable target", "CControllerDefinition-specific label was too narrow", "remain unproven"],
        ["shared-noop", "owner-corrected", "signature-hardened"],
    ),
    "0x00453ad0": target(
        "CControllerDefinition__RenderBindingsAndPollRemapInput",
        "void __thiscall CControllerDefinition__RenderBindingsAndPollRemapInput(void * this, float x, float y, int interactive)",
        ["ControlsUI__RenderBindingsList", "arrow texture", "polls keyboard/controller state", "remain unproven"],
        ["controls", "controller-definition", "remap", "name-corrected", "signature-hardened"],
    ),
    "0x00455010": target(
        "ControlsUI__RenderBindingsList",
        "void __thiscall ControlsUI__RenderBindingsList(void * this, int columnIndex, float unusedRowOffset, float listY, int interactive)",
        ["RET 0x10", "rowIndex + 0x37", "Controls__BeginRemapCapture", "remain unproven"],
        ["controls", "control-bindings", "remap", "signature-hardened"],
    ),
    "0x00456080": target(
        "Controls__BeginRemapCapture",
        "void __fastcall Controls__BeginRemapCapture(void * controllerDefinition)",
        ["g_ControlRemapActive", "g_ControlRemapArmed", "key-sink callback", "remain unproven"],
        ["controls", "remap", "signature-hardened"],
    ),
    "0x004565d0": target(
        "OptionsEntries__SetBindingSlot",
        "void __cdecl OptionsEntries__SetBindingSlot(int slotIndex, int entryId, int field0, int deviceCode, short scan, short vk)",
        ["finds an options entry", "slotIndex", "scan", "vk", "remain unproven"],
        ["controls", "options-entry", "remap", "signature-hardened"],
    ),
    "0x00456610": target(
        "CControllerDefinition__GetWidth",
        "int __thiscall CControllerDefinition__GetWidth(void * this)",
        ["returns the fixed width 0x190", "vtable slot 5", "remain unproven"],
        ["controls", "controller-definition", "signature-hardened"],
    ),
    "0x00456620": target(
        "CControllerDefinition__GetRowHeight",
        "int __thiscall CControllerDefinition__GetRowHeight(void * this)",
        ["returns fixed value 0xe6", "vtable slot 6", "remain unproven"],
        ["controls", "controller-definition", "signature-hardened"],
    ),
    "0x00456630": target(
        "CControllerDefinition__GetFlag1C",
        "byte __thiscall CControllerDefinition__GetFlag1C(void * this)",
        ["reads the byte flag at this+0x1c", "vtable slot 8", "remain unproven"],
        ["controls", "controller-definition", "signature-hardened"],
    ),
    "0x00456640": target(
        "CControllerDefinition__ClearFlag1C",
        "void __thiscall CControllerDefinition__ClearFlag1C(void * this)",
        ["clears the byte flag at this+0x1c", "vtable slot 12", "remain unproven"],
        ["controls", "controller-definition", "signature-hardened"],
    ),
}

VTABLE_EVIDENCE = [
    ("0x00622264", "0", "0x00622264", "0x00453460", "OptionsEntries__InitDefaultDualBindingsTable"),
    ("0x005db404", "0", "0x005db404", "0x004539b0", "CControllerDefinition__scalar_deleting_dtor"),
    ("0x005db404", "1", "0x005db408", "0x00453ac0", "SharedVFunc__NoOp_Ret0C"),
    ("0x005db404", "4", "0x005db414", "0x00453ad0", "CControllerDefinition__RenderBindingsAndPollRemapInput"),
    ("0x005db404", "5", "0x005db418", "0x00456610", "CControllerDefinition__GetWidth"),
    ("0x005db404", "6", "0x005db41c", "0x00456620", "CControllerDefinition__GetRowHeight"),
    ("0x005db404", "8", "0x005db424", "0x00456630", "CControllerDefinition__GetFlag1C"),
    ("0x005db404", "12", "0x005db434", "0x00456640", "CControllerDefinition__ClearFlag1C"),
    ("0x005e4c6c", "1", "0x005e4c70", "0x00453ac0", "SharedVFunc__NoOp_Ret0C"),
    ("0x005e4d3c", "1", "0x005e4d40", "0x00453ac0", "SharedVFunc__NoOp_Ret0C"),
]

XREF_EVIDENCE = [
    ("0x00453460", "0x00622264", "DATA"),
    ("0x00453970", "0x004ce3d8", "UNCONDITIONAL_CALL"),
    ("0x004539b0", "0x005db404", "DATA"),
    ("0x004539d0", "0x004539b3", "UNCONDITIONAL_CALL"),
    ("0x00453ac0", "0x0052ff3e", "DATA"),
    ("0x00453ac0", "0x005db408", "DATA"),
    ("0x00453ac0", "0x005e4c70", "DATA"),
    ("0x00453ac0", "0x005e4d40", "DATA"),
    ("0x00453ad0", "0x005db414", "DATA"),
    ("0x00455010", "0x00453b12", "UNCONDITIONAL_CALL"),
    ("0x00456080", "0x00455b8d", "UNCONDITIONAL_CALL"),
    ("0x004565d0", "0x004562f3", "UNCONDITIONAL_CALL"),
    ("0x004565d0", "0x00456311", "UNCONDITIONAL_CALL"),
    ("0x004565d0", "0x00456330", "UNCONDITIONAL_CALL"),
    ("0x004565d0", "0x00456389", "UNCONDITIONAL_CALL"),
    ("0x004565d0", "0x004563dd", "UNCONDITIONAL_CALL"),
    ("0x004565d0", "0x004563f9", "UNCONDITIONAL_CALL"),
    ("0x004565d0", "0x00456457", "UNCONDITIONAL_CALL"),
    ("0x004565d0", "0x00456488", "UNCONDITIONAL_CALL"),
    ("0x004565d0", "0x004564e5", "UNCONDITIONAL_CALL"),
    ("0x004565d0", "0x00456546", "UNCONDITIONAL_CALL"),
    ("0x004565d0", "0x00456562", "UNCONDITIONAL_CALL"),
    ("0x00456610", "0x005db418", "DATA"),
    ("0x00456620", "0x005db41c", "DATA"),
    ("0x00456630", "0x005db424", "DATA"),
    ("0x00456640", "0x005db434", "DATA"),
]

INSTRUCTION_EVIDENCE = [
    ("0x00453ac0", "0x00453ac0", "RET", "0xc"),
    ("0x00453ad0", "0x00453b12", "CALL", "0x00455010"),
    ("0x00455010", "0x00455191", "CALL", "0x00453f50"),
    ("0x00455010", "0x0045519c", "CALL", "0x0042db10"),
    ("0x00455010", "0x00455b8d", "CALL", "0x00456080"),
    ("0x00455010", "0x00455d98", "RET", "0x10"),
    ("0x00456080", "0x004560d4", "MOV", "[0x006290b4]"),
    ("0x00456080", "0x004560dd", "MOV", "[0x00677d74]"),
    ("0x004565d0", "0x004565d0", "MOV", "[ESP + 0x8]"),
    ("0x004565d0", "0x0045660d", "RET", ""),
    ("0x00456610", "0x00456610", "MOV", "0x190"),
    ("0x00456620", "0x00456620", "MOV", "0xe6"),
    ("0x00456630", "0x00456630", "MOV", "[ECX + 0x1c]"),
    ("0x00456640", "0x00456640", "MOV", "[ECX + 0x1c]"),
]

STALE_TOKENS = [
    "undefined ",
    "param_",
    "unaff_",
    "CControllerDefinition__VFunc_01_00453ac0",
    "CControllerDefinition__VFunc_04_00453ad0",
    "CControllerDefinition__VFunc_05_00456610",
    "CControllerDefinition__VFunc_06_00456620",
    "CControllerDefinition__VFunc_08_00456630",
    "CControllerDefinition__VFunc_12_00456640",
]
OVERCLAIM_TOKENS = [
    "fully re'ed",
    "100% re",
    "runtime behavior proven",
    "source identity proven",
    "rebuild parity proven",
]


def norm_addr(value: object) -> str:
    text = str(value or "").strip().lower()
    if text.startswith("0x"):
        text = text[2:]
    if not text or text.startswith("<"):
        return text
    return "0x" + text.zfill(8)


def compact(value: str) -> str:
    return "".join(value.lower().split())


def token_present(text: str, token: str) -> bool:
    return compact(token) in compact(text)


def unescape_tsv(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def read_tsv(path: Path, *, unescape_comment: bool = False) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if unescape_comment:
        for row in rows:
            row["comment"] = unescape_tsv(row.get("comment", ""))
    return rows


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def parse_summary(log_text: str) -> dict[str, object]:
    match = re.search(r"targets=(\d+)\s+changed_or_would_change=(\d+)\s+failed=(\d+)\s+dry=(true|false)", log_text)
    if not match:
        return {}
    return {
        "targets": int(match.group(1)),
        "changed_or_would_change": int(match.group(2)),
        "failed": int(match.group(3)),
        "dry": match.group(4) == "true",
    }


def row_by_addr(rows: list[dict[str, str]], key: str = "address") -> dict[str, dict[str, str]]:
    return {norm_addr(row.get(key, "")): row for row in rows}


def any_row(rows: list[dict[str, str]], predicate) -> bool:
    return any(predicate(row) for row in rows)


def build_report(
    *,
    root: Path = DEFAULT_ROOT,
    dry_log_path: Path | None = None,
    apply_log_path: Path | None = None,
    metadata_path: Path | None = None,
    tags_path: Path | None = None,
    vtable_path: Path | None = None,
    instructions_path: Path | None = None,
    controlsui_instructions_path: Path | None = None,
    xrefs_path: Path | None = None,
) -> dict[str, object]:
    root = Path(root)
    dry_log_path = dry_log_path or root / "frontend_controls_signature_dry.log"
    apply_log_path = apply_log_path or root / "frontend_controls_signature_apply.log"
    metadata_path = metadata_path or root / "metadata_after.tsv"
    tags_path = tags_path or root / "tags_after.tsv"
    vtable_path = vtable_path or root / "vtable_slots_after.tsv"
    instructions_path = instructions_path or root / "instructions_after.tsv"
    controlsui_instructions_path = controlsui_instructions_path or root / "controlsui_instructions_after.tsv"
    xrefs_path = xrefs_path or root / "xrefs_after.tsv"

    failures: list[str] = []
    expected_count = len(TARGETS)
    dry_summary = parse_summary(read_text(dry_log_path))
    apply_summary = parse_summary(read_text(apply_log_path))
    if dry_summary != {"targets": expected_count, "changed_or_would_change": expected_count, "failed": 0, "dry": True}:
        failures.append(f"unexpected dry summary: {dry_summary}")
    if apply_summary != {"targets": expected_count, "changed_or_would_change": expected_count, "failed": 0, "dry": False}:
        failures.append(f"unexpected apply summary: {apply_summary}")

    metadata = row_by_addr(read_tsv(metadata_path, unescape_comment=True))
    tags = row_by_addr(read_tsv(tags_path))
    vtable_rows = read_tsv(vtable_path)
    instruction_rows = read_tsv(instructions_path) + read_tsv(controlsui_instructions_path)
    xref_rows = read_tsv(xrefs_path)

    stale_hits = 0
    overclaim_hits = 0
    for address, spec in TARGETS.items():
        row = metadata.get(norm_addr(address))
        if row is None:
            failures.append(f"missing metadata for {address}")
            continue
        if row.get("status") != "OK":
            failures.append(f"metadata status mismatch for {address}: {row.get('status')}")
        if row.get("name") != spec["name"]:
            failures.append(f"name mismatch for {address}: {row.get('name')} != {spec['name']}")
        if row.get("signature") != spec["signature"]:
            failures.append(f"signature mismatch for {address}: {row.get('signature')} != {spec['signature']}")
        comment = row.get("comment", "")
        for token in spec["commentTokens"]:
            if not token_present(comment, str(token)):
                failures.append(f"comment token missing for {address}: {token}")
        text = "\n".join([row.get("name", ""), row.get("signature", ""), comment])
        for token in STALE_TOKENS:
            if token_present(text, token):
                stale_hits += 1
                failures.append(f"stale token for {address}: {token}")
        for token in OVERCLAIM_TOKENS:
            if token_present(text, token):
                overclaim_hits += 1
                failures.append(f"overclaim token for {address}: {token}")

        tag_row = tags.get(norm_addr(address))
        if tag_row is None or tag_row.get("status") != "OK":
            failures.append(f"missing tag row for {address}")
        else:
            found_tags = {tag.strip() for tag in tag_row.get("tags", "").split(";") if tag.strip()}
            expected_tags = COMMON_TAGS | set(spec["tags"])
            missing = sorted(expected_tags - found_tags)
            if missing:
                failures.append(f"missing tags for {address}: {missing}")

    vtable_hits = 0
    for vtable_addr, slot, slot_addr, pointer, name in VTABLE_EVIDENCE:
        if any_row(
            vtable_rows,
            lambda row, vtable_addr=vtable_addr, slot=slot, slot_addr=slot_addr, pointer=pointer, name=name: (
                norm_addr(row.get("vtable")) == norm_addr(vtable_addr)
                and row.get("slot_index") == slot
                and norm_addr(row.get("slot_addr")) == norm_addr(slot_addr)
                and norm_addr(row.get("pointer_addr")) == norm_addr(pointer)
                and norm_addr(row.get("function_entry")) == norm_addr(pointer)
                and row.get("function_name") == name
                and row.get("status") == "OK"
            ),
        ):
            vtable_hits += 1
        else:
            failures.append(f"missing vtable evidence {vtable_addr} slot {slot} -> {pointer} {name}")

    xref_hits = 0
    for target_addr, from_addr, ref_type in XREF_EVIDENCE:
        if any_row(
            xref_rows,
            lambda row, target_addr=target_addr, from_addr=from_addr, ref_type=ref_type: (
                norm_addr(row.get("target_addr")) == norm_addr(target_addr)
                and norm_addr(row.get("from_addr")) == norm_addr(from_addr)
                and row.get("ref_type") == ref_type
            ),
        ):
            xref_hits += 1
        else:
            failures.append(f"missing xref evidence {from_addr} -> {target_addr} {ref_type}")

    instruction_hits = 0
    for target_addr, instruction_addr, mnemonic, operand_token in INSTRUCTION_EVIDENCE:
        if any_row(
            instruction_rows,
            lambda row, target_addr=target_addr, instruction_addr=instruction_addr, mnemonic=mnemonic, operand_token=operand_token: (
                norm_addr(row.get("function_entry")) == norm_addr(target_addr)
                and norm_addr(row.get("instruction_addr")) == norm_addr(instruction_addr)
                and row.get("mnemonic") == mnemonic
                and token_present(row.get("operands", ""), operand_token)
            ),
        ):
            instruction_hits += 1
        else:
            failures.append(f"missing instruction evidence {target_addr} {instruction_addr} {mnemonic} {operand_token}")

    return {
        "status": "PASS" if not failures else "FAIL",
        "summary": {
            "targets": expected_count,
            "vtableEvidenceHits": vtable_hits,
            "xrefEvidenceHits": xref_hits,
            "instructionEvidenceHits": instruction_hits,
            "staleTokenHits": stale_hits,
            "overclaimHits": overclaim_hits,
        },
        "paths": {
            "root": str(root),
            "metadata": str(metadata_path),
            "tags": str(tags_path),
            "vtable": str(vtable_path),
            "instructions": str(instructions_path),
            "controlsuiInstructions": str(controlsui_instructions_path),
            "xrefs": str(xrefs_path),
        },
        "failures": failures,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    report = build_report(root=args.root)
    args.root.mkdir(parents=True, exist_ok=True)
    output_path = args.root / OUTPUT_NAME
    output_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"{report['status']}: wrote {output_path}")
    print(json.dumps(report["summary"], sort_keys=True))
    if args.check and report["status"] != "PASS":
        for failure in report["failures"]:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
