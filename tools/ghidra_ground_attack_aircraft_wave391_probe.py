#!/usr/bin/env python3
"""Validate the Wave391 GroundAttackAircraft / AI / Guide Ghidra correction tranche."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "ground-attack-aircraft-wave391" / "current"

COMMON_TAGS = {"static-reaudit", "ground-attack-aircraft-wave391", "retail-binary-evidence"}


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
        "tags": sorted(COMMON_TAGS | set(tags)),
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x0047bab0": target(
        "CGroundAttackAI__InitState",
        "void __fastcall CGroundAttackAI__InitState(void * this)",
        ["CGroundAttackAI allocation/vtable install", "clears field +0x60", "+0x64 timer/float", "GroundAttackAircraft.cpp source body is missing"],
        ["Random__NextLCGAbs", "CGroundAttackAircraft__CloseBay"],
        ["cgroundattackai", "init-state", "bay-state", "owner-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x0047bbf0": target(
        "CGroundAttackAircraft__Init",
        "void __thiscall CGroundAttackAircraft__Init(void * this, void * init_data)",
        ["function table 0x005e2bf0 slot 0", "CAirUnit__Init", "CMCGroundAttack, CGroundAttackAI, and CGroundAttackGuide", "Corrects the older constructor label"],
        ["CAirUnit__Init", "OID__AllocObject(0x14,0x1b", "CMCGroundAttack__ctor_like_004964d0", "PTR_LAB_005dbd4c", "CGroundAttackAI__InitState", "PTR_CAirGuide__HandleEvent_005dbd20"],
        ["cgroundattackaircraft", "init", "component-create", "owner-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x0047bd70": target(
        "CGroundAttackAI__ScalarDeletingDestructor",
        "void * __thiscall CGroundAttackAI__ScalarDeletingDestructor(void * this, byte flags)",
        ["CGroundAttackAI vtable 0x005dbd4c slot 1", "CGroundAttackAI__Destructor", "older GroundAttackAircraft owner label"],
        ["CGroundAttackAI__Destructor", "OID__FreeObject"],
        ["cgroundattackai", "destructor", "scalar-deleting-dtor", "owner-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x0047bd90": target(
        "CGroundAttackAI__Destructor",
        "void __fastcall CGroundAttackAI__Destructor(void * this)",
        ["CUnitAI base vtable 0x005d8d1c", "+0x28", "+0x24", "+0x0c", "runtime cleanup behavior, and rebuild parity remain unproven"],
        ["PTR_LAB_005d8d1c", "CSPtrSet__Remove", "CMonitor__Shutdown"],
        ["cgroundattackai", "destructor", "owner-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x0047be30": target(
        "CGroundAttackGuide__ScalarDeletingDestructor",
        "void * __thiscall CGroundAttackGuide__ScalarDeletingDestructor(void * this, byte flags)",
        ["CGroundAttackGuide vtable 0x005dbd20 slot 1", "CGroundAttackGuide__Destructor", "stale GillMHead label"],
        ["CGroundAttackGuide__Destructor", "OID__FreeObject"],
        ["cgroundattackguide", "destructor", "scalar-deleting-dtor", "owner-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x0047be50": target(
        "CGroundAttackGuide__Destructor",
        "void __fastcall CGroundAttackGuide__Destructor(void * this)",
        ["linked reader/set field at +0x2c", "CMonitor__Shutdown", "stale GillMHead label"],
        ["+ 0x2c", "CSPtrSet__Remove", "CMonitor__Shutdown"],
        ["cgroundattackguide", "destructor", "owner-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x0047bfa0": target(
        "CGroundAttackAircraft__OpenBay",
        "void __fastcall CGroundAttackAircraft__OpenBay(void * this)",
        ["bay state +0x27c", "sets state 2", "open animation token", "runtime animation behavior, and rebuild parity remain unproven"],
        ["DAT_00623bb4", "FindAnimationIndex", "+ 0xf0"],
        ["cgroundattackaircraft", "bay-state", "animation-state", "signature-hardened", "comment-hardened"],
    ),
    "0x0047bff0": target(
        "CGroundAttackAircraft__CloseBay",
        "void __fastcall CGroundAttackAircraft__CloseBay(void * this)",
        ["bay state +0x27c", "sets state 3", "close animation token", "runtime animation behavior, and rebuild parity remain unproven"],
        ["s_close_006289e4", "FindAnimationIndex", "+ 0xf0"],
        ["cgroundattackaircraft", "bay-state", "animation-state", "signature-hardened", "comment-hardened"],
    ),
    "0x0047c040": target(
        "CGroundAttackAircraft__AdvanceCloseShootAnimationState",
        "int __fastcall CGroundAttackAircraft__AdvanceCloseShootAnimationState(void * this)",
        ["function table 0x005e2bf0 slot 50", "open, shoot, and close tokens", "writes bay state +0x27c", "older broad CUnitAI label"],
        ["DAT_00623bb4", "s_shoot_006289ec", "s_close_006289e4", "PTR_DAT_0062359c", "+ 0x27c"],
        ["cgroundattackaircraft", "bay-state", "animation-state", "owner-corrected", "signature-hardened", "comment-hardened"],
    ),
}

EXPECTED_DRY = {"updated": 0, "skipped": 9, "renamed": 0, "would_rename": 7, "missing": 0, "bad": 0}
EXPECTED_APPLY = {"updated": 9, "skipped": 0, "renamed": 7, "would_rename": 0, "missing": 0, "bad": 0}

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "runtime proof",
    "source identity proven",
    "fully re'ed",
    "100% re",
    "rebuild parity proven",
)


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


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
        for key in ("address", "target_addr", "vtable", "slot_addr", "pointer_addr", "function_entry", "entry_addr"):
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


def decompile_text_for(directory: Path, address: str) -> str:
    if not directory.is_dir():
        return ""
    matches = sorted(directory.glob(f"{normalize_address(address)[2:]}_*.c"))
    if not matches:
        return ""
    return read_text(matches[0])


def parse_tags(value: str) -> set[str]:
    return {part.strip() for part in value.split(";") if part.strip()}


def parse_summary(log_text: str) -> dict[str, int]:
    match = re.search(
        r"updated=(\d+)\s+skipped=(\d+)\s+renamed=(\d+)\s+would_rename=(\d+)\s+missing=(\d+)\s+bad=(\d+)",
        log_text,
    )
    if not match:
        return {"updated": -1, "skipped": -1, "renamed": -1, "would_rename": -1, "missing": -1, "bad": -1}
    return {
        "updated": int(match.group(1)),
        "skipped": int(match.group(2)),
        "renamed": int(match.group(3)),
        "would_rename": int(match.group(4)),
        "missing": int(match.group(5)),
        "bad": int(match.group(6)),
    }


def vtable_type_hit(rows: list[dict[str, str]], vtable: str, type_name: str) -> bool:
    for row in rows:
        if normalize_address(row.get("vtable", "")) == normalize_address(vtable) and row.get("demangled_type_name") == type_name:
            return True
    return False


def vtable_slot_hit(rows: list[dict[str, str]], vtable: str, slot: str, function_name: str) -> bool:
    for row in rows:
        if normalize_address(row.get("vtable", "")) != normalize_address(vtable):
            continue
        if row.get("slot_index") != slot:
            continue
        if row.get("function_name") == function_name:
            return True
    return False


def pointer_table_hit(rows: list[dict[str, str]], slot: str, function_name: str) -> bool:
    for row in rows:
        if row.get("slot") == slot and row.get("ptr_name") == function_name:
            return True
    return False


def xref_hit(rows: list[dict[str, str]], target: str, source_name: str) -> bool:
    wanted = normalize_address(target)
    for row in rows:
        if normalize_address(row.get("target_addr", "")) == wanted and row.get("from_function") == source_name:
            return True
    return False


def validate(args: argparse.Namespace) -> tuple[dict[str, object], int]:
    metadata_rows = read_tsv(resolve(args.metadata))
    tag_rows = read_tsv(resolve(args.tags))
    vtable_type_rows = read_tsv(resolve(args.vtable_types))
    vtable_rows = read_tsv(resolve(args.vtable_slots))
    pointer_rows = read_tsv(resolve(args.pointer_table))
    xref_rows = read_tsv(resolve(args.xrefs))
    dry_summary = parse_summary(read_text(resolve(args.dry_log)))
    apply_summary = parse_summary(read_text(resolve(args.apply_log)))

    failures: list[str] = []
    checked: dict[str, object] = {
        "metadataRows": len(metadata_rows),
        "tagRows": len(tag_rows),
        "vtableTypeRows": len(vtable_type_rows),
        "vtableRows": len(vtable_rows),
        "pointerRows": len(pointer_rows),
        "xrefRows": len(xref_rows),
        "drySummary": dry_summary,
        "applySummary": apply_summary,
    }

    if dry_summary != EXPECTED_DRY:
        failures.append(f"dry summary mismatch: {dry_summary} != {EXPECTED_DRY}")
    if apply_summary != EXPECTED_APPLY:
        failures.append(f"apply summary mismatch: {apply_summary} != {EXPECTED_APPLY}")

    for addr, spec in TARGETS.items():
        row = row_by_address(metadata_rows, addr)
        if row is None:
            failures.append(f"missing metadata for {addr}")
            continue
        if row.get("name") != spec["name"]:
            failures.append(f"{addr} name mismatch: {row.get('name')} != {spec['name']}")
        if row.get("signature") != spec["signature"]:
            failures.append(f"{addr} signature mismatch: {row.get('signature')} != {spec['signature']}")
        comment = row.get("comment", "")
        for token in spec["commentTokens"]:  # type: ignore[index]
            if not token_present(comment, str(token)):
                failures.append(f"{addr} missing comment token: {token}")
        for token in OVERCLAIM_TOKENS:
            if token_present(comment, token):
                failures.append(f"{addr} comment overclaim token present: {token}")

        decompile = decompile_text_for(resolve(args.decompile_dir), addr)
        if not decompile:
            failures.append(f"{addr} missing decompile export")
        for token in spec["decompileTokens"]:  # type: ignore[index]
            if not token_present(decompile, str(token)):
                failures.append(f"{addr} missing decompile token: {token}")

        tag_row = row_by_address(tag_rows, addr)
        actual_tags = parse_tags(tag_row.get("tags", "")) if tag_row else set()
        for tag in spec["tags"]:  # type: ignore[index]
            if str(tag) not in actual_tags:
                failures.append(f"{addr} missing tag: {tag}")

    if not vtable_type_hit(vtable_type_rows, "0x005dbd4c", "CGroundAttackAI"):
        failures.append("missing CGroundAttackAI RTTI hit for 0x005dbd4c")
    if not vtable_type_hit(vtable_type_rows, "0x005dbd20", "CGroundAttackGuide"):
        failures.append("missing CGroundAttackGuide RTTI hit for 0x005dbd20")

    required_slots = [
        ("0x005dbd4c", "1", "CGroundAttackAI__ScalarDeletingDestructor"),
        ("0x005dbd20", "1", "CGroundAttackGuide__ScalarDeletingDestructor"),
    ]
    for vtable, slot, name in required_slots:
        if not vtable_slot_hit(vtable_rows, vtable, slot, name):
            failures.append(f"missing vtable slot hit {vtable} slot {slot} -> {name}")

    required_pointer_slots = [
        ("0", "CGroundAttackAircraft__Init"),
        ("50", "CGroundAttackAircraft__AdvanceCloseShootAnimationState"),
    ]
    for slot, name in required_pointer_slots:
        if not pointer_table_hit(pointer_rows, slot, name):
            failures.append(f"missing pointer table slot {slot} -> {name}")

    required_xrefs = [
        ("0x0047bab0", "CGroundAttackAircraft__Init"),
        ("0x0047bd90", "CGroundAttackAI__ScalarDeletingDestructor"),
        ("0x0047be50", "CGroundAttackGuide__ScalarDeletingDestructor"),
        ("0x0047bff0", "CGroundAttackAI__InitState"),
    ]
    for target_addr, source_name in required_xrefs:
        if not xref_hit(xref_rows, target_addr, source_name):
            failures.append(f"missing xref hit {source_name} -> {target_addr}")

    status = "PASS" if not failures else "FAIL"
    report = {
        "schema": "ghidra-ground-attack-aircraft-wave391",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "targets": len(TARGETS),
        "checked": checked,
        "failures": failures,
        "inputs": {
            "metadata": relative(resolve(args.metadata)),
            "tags": relative(resolve(args.tags)),
            "decompileDir": relative(resolve(args.decompile_dir)),
            "vtableTypes": relative(resolve(args.vtable_types)),
            "vtableSlots": relative(resolve(args.vtable_slots)),
            "pointerTable": relative(resolve(args.pointer_table)),
            "xrefs": relative(resolve(args.xrefs)),
            "dryLog": relative(resolve(args.dry_log)),
            "applyLog": relative(resolve(args.apply_log)),
        },
    }

    out = resolve(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        f"status={status} targets={len(TARGETS)} "
        f"metadata_rows={len(metadata_rows)} tags={len(tag_rows)} failures={len(failures)}"
    )
    return report, 0 if status == "PASS" else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="return non-zero when validation fails")
    parser.add_argument("--metadata", type=Path, default=BASE / "metadata_after.tsv")
    parser.add_argument("--tags", type=Path, default=BASE / "tags_after.tsv")
    parser.add_argument("--decompile-dir", type=Path, default=BASE / "decompile_after")
    parser.add_argument("--vtable-types", type=Path, default=BASE / "vtable_types_after.tsv")
    parser.add_argument("--vtable-slots", type=Path, default=BASE / "vtable_slots_after.tsv")
    parser.add_argument("--pointer-table", type=Path, default=BASE / "pointer_table_005e2bf0_after.tsv")
    parser.add_argument("--xrefs", type=Path, default=BASE / "xrefs_after.tsv")
    parser.add_argument("--dry-log", type=Path, default=BASE / "ground_attack_aircraft_wave391_dry.log")
    parser.add_argument("--apply-log", type=Path, default=BASE / "ground_attack_aircraft_wave391_apply.log")
    parser.add_argument("--out", type=Path, default=BASE / "ground-attack-aircraft-wave391.json")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    _report, status = validate(args)
    return status if args.check else 0


if __name__ == "__main__":
    raise SystemExit(main())
