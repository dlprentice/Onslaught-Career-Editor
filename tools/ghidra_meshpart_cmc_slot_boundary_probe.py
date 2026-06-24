#!/usr/bin/env python3
"""Validate the saved MeshPart/CMC slot-boundary recovery tranche."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


DEFAULT_ROOT = Path("subagents/ghidra-static-reaudit/meshpart-cmc-slot-wave357/current")
OUTPUT_NAME = "meshpart-cmc-slot-boundary.json"

COMMON_TAGS = {
    "static-reaudit",
    "meshpart-cmc-slot-wave357",
    "retail-binary-evidence",
}


def target(
    name: str,
    signature: str,
    comment_tokens: list[str],
    decompile_tokens: list[str],
    tags: list[str],
) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "commentTokens": comment_tokens,
        "decompileTokens": decompile_tokens,
        "tags": tags,
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x00495770": target(
        "CMCComponent__VFunc_08_CheckOwnerRangeWindow",
        "bool __thiscall CMCComponent__VFunc_08_CheckOwnerRangeWindow(void * this)",
        ["CMCComponent vtable slot 8", "+0xe0/+0xe4", "+0xe8/+0xf0", "remain unproven"],
        ["CMCComponent__VFunc_08_CheckOwnerRangeWindow", "this"],
        ["cmccomponent", "function-boundary", "vtable-slot", "range-window"],
    ),
    "0x004959a0": target(
        "CMCComponent__VFunc_04_UpdateTurretBarrelTransform",
        "void __thiscall CMCComponent__VFunc_04_UpdateTurretBarrelTransform(void * this, void * meshPart, void * heightAdjustOut, void * transformOut, int reservedArg)",
        ["CMCComponent vtable slot 4", "turret", "barrel", "RET 0x10", "remain unproven"],
        ["meshPart", "heightAdjustOut", "transformOut"],
        ["cmccomponent", "function-boundary", "vtable-slot", "turret-barrel"],
    ),
    "0x00496100": target(
        "CMCDropship__VFunc_05_UpdateDoorAnimationValue",
        "void __thiscall CMCDropship__VFunc_05_UpdateDoorAnimationValue(void * this, void * meshPart, void * doorAnimationValueOut)",
        ["CMCDropship vtable slot 5", "door", "dooropening", "doorclosing", "remain unproven"],
        ["meshPart", "doorAnimationValueOut"],
        ["cmcdropship", "function-boundary", "vtable-slot", "door-animation"],
    ),
    "0x00496200": target(
        "CMCDropship__VFunc_08_CheckOwnerStateAndTimeWindow",
        "bool __thiscall CMCDropship__VFunc_08_CheckOwnerStateAndTimeWindow(void * this)",
        ["CMCDropship vtable slot 8", "+0x27c", "+0x2a4/+0x2a8", "remain unproven"],
        ["CMCDropship__VFunc_08_CheckOwnerStateAndTimeWindow", "this"],
        ["cmcdropship", "function-boundary", "vtable-slot", "state-time-window"],
    ),
}


XREF_EVIDENCE = [
    ("0x004959a0", "0x005dc2e8", "DATA"),
    ("0x00495770", "0x005dc2f8", "DATA"),
    ("0x00496100", "0x005dc318", "DATA"),
    ("0x00496200", "0x005dc324", "DATA"),
]

VTABLE_EVIDENCE = [
    ("0x005dc2d8", "4", "0x005dc2e8", "0x004959a0"),
    ("0x005dc2d8", "8", "0x005dc2f8", "0x00495770"),
    ("0x005dc304", "5", "0x005dc318", "0x00496100"),
    ("0x005dc304", "8", "0x005dc324", "0x00496200"),
]

INSTRUCTION_EVIDENCE = [
    ("0x00495770", "0x00495770", "MOV", "[ECX + 0x8]"),
    ("0x00495770", "0x004957c6", "RET", ""),
    ("0x004959a0", "0x004959bf", "MOV", "0x62dd20"),
    ("0x004959a0", "0x00495cbd", "PUSH", "0x62dd18"),
    ("0x004959a0", "0x00495def", "RET", "0x10"),
    ("0x00496100", "0x00496111", "PUSH", "0x62dd6c"),
    ("0x00496100", "0x0049615e", "PUSH", "0x628a98"),
    ("0x00496100", "0x0049618a", "PUSH", "0x628a8c"),
    ("0x00496100", "0x004961f5", "RET", "0x8"),
    ("0x00496200", "0x00496212", "MOV", "[EDX + 0x27c]"),
    ("0x00496200", "0x00496242", "RET", ""),
]

STRING_EVIDENCE = [
    ("string_0062dd18.tsv", "barrel"),
    ("string_0062dd20.tsv", "turret"),
    ("string_0062dd6c.tsv", "door"),
    ("string_00628a98.tsv", "dooropening"),
    ("string_00628a8c.tsv", "doorclosing"),
]

STALE_SIGNATURE_TOKENS = ["<none>", "<no_function>", "MISSING", "undefined ", "param_1", "param_2", "param_3", "param_4"]
STALE_DECOMPILE_TOKENS = ["<no_function>", "MISSING"]
OVERCLAIM_TOKENS = [
    "runtime behavior proven",
    "source identity proven",
    "exact source virtual name proven",
    "layout proven",
]


def norm_addr(value: object) -> str:
    text = str(value or "").strip().lower()
    if text.startswith("0x"):
        text = text[2:]
    if not text or text.startswith("<"):
        return text
    return "0x" + text.zfill(8)


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def parse_summary(log_text: str) -> dict[str, object]:
    result: dict[str, object] = {}
    match = re.search(r"targets=(\d+)\s+changed_or_would_change=(\d+)\s+failed=(\d+)\s+dry=(true|false)", log_text)
    if match:
        result["targets"] = int(match.group(1))
        result["changedOrWouldChange"] = int(match.group(2))
        result["failed"] = int(match.group(3))
        result["dry"] = match.group(4) == "true"
    return result


def row_by_addr(rows: list[dict[str, str]], key: str = "address") -> dict[str, dict[str, str]]:
    return {norm_addr(row.get(key, "")): row for row in rows}


def any_row(rows: list[dict[str, str]], predicate) -> bool:
    return any(predicate(row) for row in rows)


def decompile_for(decompile_dir: Path, address: str, name: str) -> str:
    exact = decompile_dir / f"{address[2:]}_{name}.c"
    if exact.exists():
        return read_text(exact)
    matches = sorted(decompile_dir.glob(f"{address[2:]}_*.c"))
    return "\n".join(read_text(path) for path in matches)


def string_value(path: Path) -> str:
    rows = read_tsv(path)
    if not rows:
        return ""
    return rows[0].get("cstring", "")


def build_report(
    *,
    root: Path = DEFAULT_ROOT,
    dry_log_path: Path | None = None,
    apply_log_path: Path | None = None,
    metadata_path: Path | None = None,
    tags_path: Path | None = None,
    xrefs_path: Path | None = None,
    instructions_path: Path | None = None,
    vtable_path: Path | None = None,
    decompile_dir: Path | None = None,
) -> dict[str, object]:
    dry_log_path = dry_log_path or root / "meshpart_cmc_slot_boundary_dry.log"
    apply_log_path = apply_log_path or root / "meshpart_cmc_slot_boundary_apply.log"
    metadata_path = metadata_path or root / "metadata_after.tsv"
    tags_path = tags_path or root / "tags_after.tsv"
    xrefs_path = xrefs_path or root / "xrefs_after.tsv"
    instructions_path = instructions_path or root / "instructions_after.tsv"
    vtable_path = vtable_path or root / "vtable_slots_after.tsv"
    decompile_dir = decompile_dir or root / "decompile_after"

    failures: list[str] = []
    dry_summary = parse_summary(read_text(dry_log_path))
    apply_summary = parse_summary(read_text(apply_log_path))
    if dry_summary.get("targets") != len(TARGETS) or dry_summary.get("failed") != 0 or dry_summary.get("dry") is not True:
        failures.append(f"dry summary mismatch: {dry_summary}")
    if apply_summary.get("targets") != len(TARGETS) or apply_summary.get("failed") != 0 or apply_summary.get("dry") is not False:
        failures.append(f"apply summary mismatch: {apply_summary}")

    metadata = row_by_addr(read_tsv(metadata_path))
    tags = row_by_addr(read_tsv(tags_path))
    xrefs = read_tsv(xrefs_path)
    instructions = read_tsv(instructions_path)
    vtables = read_tsv(vtable_path)

    for address, spec in TARGETS.items():
        row = metadata.get(address)
        if not row:
            failures.append(f"{address} metadata missing")
            continue
        if row.get("status") != "OK":
            failures.append(f"{address} metadata status is {row.get('status')}")
        if row.get("name") != spec["name"]:
            failures.append(f"{address} name mismatch: {row.get('name')} != {spec['name']}")
        if row.get("signature") != spec["signature"]:
            failures.append(f"{address} signature mismatch: {row.get('signature')} != {spec['signature']}")
        comment = row.get("comment", "")
        for token in spec["commentTokens"]:  # type: ignore[index]
            if str(token) not in comment:
                failures.append(f"{address} comment missing token: {token}")
        for token in OVERCLAIM_TOKENS:
            if token in comment:
                failures.append(f"{address} comment overclaim token present: {token}")

        tag_row = tags.get(address)
        tag_text = tag_row.get("tags", "") if tag_row else ""
        for tag in sorted(COMMON_TAGS | set(spec["tags"])):  # type: ignore[arg-type]
            if tag not in tag_text:
                failures.append(f"{address} tag missing: {tag}")

        decompile = decompile_for(decompile_dir, address, str(spec["name"]))
        if not decompile:
            failures.append(f"{address} decompile missing")
        for token in spec["decompileTokens"]:  # type: ignore[index]
            if str(token) not in decompile:
                failures.append(f"{address} decompile missing token: {token}")
        for token in STALE_SIGNATURE_TOKENS:
            if token in row.get("signature", ""):
                failures.append(f"{address} stale signature token present: {token}")
        for token in STALE_DECOMPILE_TOKENS:
            if token in decompile:
                failures.append(f"{address} stale decompile token present: {token}")

    xref_hits = 0
    for target_addr, from_addr, ref_type in XREF_EVIDENCE:
        if any_row(
            xrefs,
            lambda row, target_addr=target_addr, from_addr=from_addr, ref_type=ref_type: (
                norm_addr(row.get("target_addr")) == norm_addr(target_addr)
                and norm_addr(row.get("from_addr")) == norm_addr(from_addr)
                and row.get("ref_type") == ref_type
            ),
        ):
            xref_hits += 1
        else:
            failures.append(f"xref evidence missing: {target_addr} from {from_addr} {ref_type}")

    instruction_hits = 0
    for target_addr, instr_addr, mnemonic, operand_token in INSTRUCTION_EVIDENCE:
        if any_row(
            instructions,
            lambda row, target_addr=target_addr, instr_addr=instr_addr, mnemonic=mnemonic, operand_token=operand_token: (
                norm_addr(row.get("target_addr")) == norm_addr(target_addr)
                and norm_addr(row.get("instruction_addr")) == norm_addr(instr_addr)
                and row.get("mnemonic") == mnemonic
                and (not operand_token or operand_token in row.get("operands", ""))
            ),
        ):
            instruction_hits += 1
        else:
            failures.append(f"instruction evidence missing: {target_addr} {instr_addr} {mnemonic} {operand_token}")

    vtable_hits = 0
    for vtable, slot, slot_addr, pointer_addr in VTABLE_EVIDENCE:
        if any_row(
            vtables,
            lambda row, vtable=vtable, slot=slot, slot_addr=slot_addr, pointer_addr=pointer_addr: (
                norm_addr(row.get("vtable")) == norm_addr(vtable)
                and row.get("slot_index") == slot
                and norm_addr(row.get("slot_addr")) == norm_addr(slot_addr)
                and norm_addr(row.get("pointer_addr")) == norm_addr(pointer_addr)
                and norm_addr(row.get("function_entry")) == norm_addr(pointer_addr)
                and row.get("status") == "OK"
            ),
        ):
            vtable_hits += 1
        else:
            failures.append(f"vtable evidence missing: {vtable} slot {slot} -> {pointer_addr}")

    string_hits = 0
    for filename, expected in STRING_EVIDENCE:
        actual = string_value(root / filename)
        if actual == expected:
            string_hits += 1
        else:
            failures.append(f"string evidence mismatch: {filename} {actual!r} != {expected!r}")

    return {
        "schema": "meshpart-cmc-slot-boundary.v1",
        "status": "PASS" if not failures else "FAIL",
        "summary": {
            "targets": len(TARGETS),
            "xrefEvidenceHits": xref_hits,
            "instructionEvidenceHits": instruction_hits,
            "vtableEvidenceHits": vtable_hits,
            "stringEvidenceHits": string_hits,
        },
        "artifacts": {
            "root": str(root),
            "dryLog": str(dry_log_path),
            "applyLog": str(apply_log_path),
            "metadata": str(metadata_path),
            "tags": str(tags_path),
            "xrefs": str(xrefs_path),
            "instructions": str(instructions_path),
            "vtableSlots": str(vtable_path),
            "decompileDir": str(decompile_dir),
        },
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    report = build_report(root=args.root)
    out_path = args.out or args.root / OUTPUT_NAME
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"{report['status']}: wrote {out_path}")
    if args.check and report["status"] != "PASS":
        for failure in report["failures"]:
            print(f"FAIL: {failure}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
