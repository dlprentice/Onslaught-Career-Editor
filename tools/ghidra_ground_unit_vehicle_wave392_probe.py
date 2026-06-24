#!/usr/bin/env python3
"""Validate the Wave392 GroundUnit / GroundVehicle Ghidra correction tranche."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "ground-unit-vehicle-wave392" / "current"

COMMON_TAGS = {"static-reaudit", "ground-unit-vehicle-wave392", "retail-binary-evidence"}


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
    "0x0047c730": target(
        "CGroundUnit__Init",
        "void __thiscall CGroundUnit__Init(void * this, void * init_data)",
        ["CGroundUnit vtable 0x005e32d4 slot 9", "delegates to CUnit__Init", "Thruster", "+0x1d4", "+0x1e4"],
        ["CUnit__Init", "s_Thruster_00623080", "GroundUnit_cpp", "CSPtrSet__AddToTail", "Random__NextLCGAbs"],
        ["cgroundunit", "init", "signature-hardened", "comment-hardened"],
    ),
    "0x0047c8e0": target(
        "CGroundUnit__CreateCollisionSphere",
        "void __thiscall CGroundUnit__CreateCollisionSphere(void * this, void * collision_owner)",
        ["CGroundUnit vtable 0x005e32d4 slot 35", "collision sphere", "CThing__AddCollision"],
        ["OID__AllocObject(0x1c", "GroundUnit_cpp", "PTR_CLine__ScalarDeletingDestructor", "CThing__AddCollision"],
        ["cgroundunit", "collision", "signature-hardened", "comment-hardened"],
    ),
    "0x0047c970": target(
        "CGroundUnit__UpdateLinkedEffectsByHeightClearance",
        "void __fastcall CGroundUnit__UpdateLinkedEffectsByHeightClearance(void * this)",
        ["CGroundUnit vtable 0x005e32d4 slot 66", "superseding the over-specific CCannon owner label", "samples height clearance", "CUnit__UpdateMotionAttachmentsAndEffects"],
        ["HeightDelta__Below025_D0", "CWorld__GetHeightSamplePacked16", "CUnit__FinalizeLinkedUnitStateAndClear", "CUnit__UpdateMotionAttachmentsAndEffects", "+ 0x25c"],
        ["cgroundunit", "height-clearance", "linked-effects", "owner-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x0047ce80": target(
        "CGroundUnit__MarkDestroyedAndResetState",
        "int __fastcall CGroundUnit__MarkDestroyedAndResetState(void * this)",
        ["CGroundUnit vtable 0x005e32d4 slot 50", "superseding the over-specific CCannon owner label", "CUnit__MarkDestroyedAndCleanupLinks", "+0x25c"],
        ["CUnit__MarkDestroyedAndCleanupLinks", "+ 0x25c", "return 1"],
        ["cgroundunit", "destruction-reset", "owner-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x0047cea0": target(
        "CGroundUnit__ClearLinkedThingFlagsAndResetCounter",
        "void __fastcall CGroundUnit__ClearLinkedThingFlagsAndResetCounter(void * this)",
        ["GroundUnit linked set at +0x1d4", "clears +0x1e4", "supersedes the older CUnitAI owner label", "CUnit__FinalizeLinkedUnitStateAndClear"],
        ["CUnit__FinalizeLinkedUnitStateAndClear", "+ 0x1d4", "+ 0x1e4"],
        ["cgroundunit", "linked-effects", "owner-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x0047cfd0": target(
        "CGroundVehicle__Init",
        "void __thiscall CGroundVehicle__Init(void * this, void * init_data)",
        ["CGroundVehicle vtable 0x005e297c slot 9", "delegates to CGroundUnit__Init", "WheelMotion", "constructs CGroundVehicleGuide"],
        ["CGroundUnit__Init", "s_WheelMotion_0062cb54", "CMCGroundVehicle__Constructor", "CMCBuggy__CMCBuggy", "CGroundVehicleGuide__Constructor", "CWarspite__Init"],
        ["cgroundvehicle", "init", "component-create", "signature-hardened", "comment-hardened"],
    ),
    "0x0047d590": target(
        "CGroundVehicleGuide__Constructor",
        "void * __thiscall CGroundVehicleGuide__Constructor(void * this, void * owner_unit)",
        ["constructor", "CGuide__ctor_base", "CGroundVehicleGuide vtable 0x005dbd90", "CUnit__GetGridMapByType"],
        ["CGuide__ctor_base", "PTR_SharedVFunc__NoOpOneArg_004014c0_005dbd90", "CUnit__GetGridMapByType"],
        ["cgroundvehicleguide", "constructor", "signature-hardened", "comment-hardened"],
    ),
    "0x0047d650": target(
        "CGroundVehicleGuide__ScalarDeletingDestructor",
        "void * __thiscall CGroundVehicleGuide__ScalarDeletingDestructor(void * this, byte flags)",
        ["CGroundVehicleGuide vtable 0x005dbd90 slot 1", "CGroundVehicleGuide__Destructor", "flags bit 0"],
        ["CGroundVehicleGuide__Destructor", "OID__FreeObject"],
        ["cgroundvehicleguide", "destructor", "scalar-deleting-dtor", "signature-hardened", "comment-hardened"],
    ),
    "0x0047d6d0": target(
        "CGroundVehicleGuide__Destructor",
        "void __fastcall CGroundVehicleGuide__Destructor(void * this)",
        ["destructor body", "frees owned fields +0x3c and +0x34", "CMonitor__Shutdown"],
        ["OID__FreeObject", "+ 0x3c", "+ 0x34", "CMonitor__Shutdown"],
        ["cgroundvehicleguide", "destructor", "signature-hardened", "comment-hardened"],
    ),
    "0x00496a50": target(
        "CMCGroundVehicle__Constructor",
        "void * __thiscall CMCGroundVehicle__Constructor(void * this, void * motion_target)",
        ["constructs this motion controller", "CMotionController__ctor_like_004bae30", "CMCGroundVehicle vtable 0x005dc35c"],
        ["CMotionController__ctor_like_004bae30", "PTR_SharedVFunc__NoOpOneArg_004014c0_005dc35c", "0xc479c000"],
        ["cmcgroundvehicle", "constructor", "signature-hardened", "comment-hardened"],
    ),
    "0x00496a80": target(
        "CMCGroundVehicle__ScalarDeletingDestructor",
        "void * __thiscall CMCGroundVehicle__ScalarDeletingDestructor(void * this, byte flags)",
        ["CMCGroundVehicle vtable 0x005dc35c slot 1", "CMCGroundVehicle__Destructor", "flags bit 0"],
        ["CMCGroundVehicle__Destructor", "OID__FreeObject"],
        ["cmcgroundvehicle", "destructor", "scalar-deleting-dtor", "signature-hardened", "comment-hardened"],
    ),
    "0x00496aa0": target(
        "CMCGroundVehicle__Destructor",
        "void __fastcall CMCGroundVehicle__Destructor(void * this)",
        ["destructor body", "CMCGroundVehicle vtable 0x005dc35c", "CMotionController__ctor_like_004bae50"],
        ["PTR_SharedVFunc__NoOpOneArg_004014c0_005dc35c", "CMotionController__ctor_like_004bae50"],
        ["cmcgroundvehicle", "destructor", "signature-hardened", "comment-hardened"],
    ),
    "0x0050ed10": target(
        "CGroundUnit__Constructor",
        "void * __fastcall CGroundUnit__Constructor(void * this)",
        ["constructor", "CActor__ctor_like_004f7e90", "CGroundUnit primary vtable 0x005e32d4"],
        ["CActor__ctor_like_004f7e90", "PTR_VFuncSlot_00_004f9820_005e32d4", "PTR_CActor__GetRenderPos_005e325c"],
        ["cgroundunit", "constructor", "signature-hardened", "comment-hardened"],
    ),
}

EXPECTED_DRY = {"updated": 0, "skipped": 13, "renamed": 0, "would_rename": 10, "missing": 0, "bad": 0}
EXPECTED_APPLY = {"updated": 13, "skipped": 0, "renamed": 10, "would_rename": 0, "missing": 0, "bad": 0}

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
    xref_rows = read_tsv(resolve(args.xrefs))
    dry_summary = parse_summary(read_text(resolve(args.dry_log)))
    apply_summary = parse_summary(read_text(resolve(args.apply_log)))

    failures: list[str] = []
    checked: dict[str, object] = {
        "metadataRows": len(metadata_rows),
        "tagRows": len(tag_rows),
        "vtableTypeRows": len(vtable_type_rows),
        "vtableRows": len(vtable_rows),
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

    required_types = [
        ("0x005e32d4", "CGroundUnit"),
        ("0x005e297c", "CGroundVehicle"),
        ("0x005dbd90", "CGroundVehicleGuide"),
        ("0x005dc35c", "CMCGroundVehicle"),
    ]
    for vtable, type_name in required_types:
        if not vtable_type_hit(vtable_type_rows, vtable, type_name):
            failures.append(f"missing RTTI hit {vtable} -> {type_name}")

    required_slots = [
        ("0x005e32d4", "9", "CGroundUnit__Init"),
        ("0x005e32d4", "35", "CGroundUnit__CreateCollisionSphere"),
        ("0x005e32d4", "50", "CGroundUnit__MarkDestroyedAndResetState"),
        ("0x005e32d4", "66", "CGroundUnit__UpdateLinkedEffectsByHeightClearance"),
        ("0x005e297c", "9", "CGroundVehicle__Init"),
        ("0x005e297c", "35", "CGroundUnit__CreateCollisionSphere"),
        ("0x005dbd90", "1", "CGroundVehicleGuide__ScalarDeletingDestructor"),
        ("0x005dc35c", "1", "CMCGroundVehicle__ScalarDeletingDestructor"),
    ]
    for vtable, slot, name in required_slots:
        if not vtable_slot_hit(vtable_rows, vtable, slot, name):
            failures.append(f"missing vtable slot hit {vtable} slot {slot} -> {name}")

    required_xrefs = [
        ("0x0047c730", "CGroundVehicle__Init"),
        ("0x0047d590", "CGroundVehicle__Init"),
        ("0x0047d650", "<no_function>"),
        ("0x0047d6d0", "CGroundVehicleGuide__ScalarDeletingDestructor"),
        ("0x00496a50", "CGroundVehicle__Init"),
        ("0x00496aa0", "CMCGroundVehicle__ScalarDeletingDestructor"),
        ("0x0050ed10", "CWorldPhysicsManager__CreateThingByType"),
    ]
    for target_addr, source_name in required_xrefs:
        if not xref_hit(xref_rows, target_addr, source_name):
            failures.append(f"missing xref hit {source_name} -> {target_addr}")

    status = "PASS" if not failures else "FAIL"
    report = {
        "schema": "ghidra-ground-unit-vehicle-wave392",
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
    parser.add_argument("--xrefs", type=Path, default=BASE / "xrefs_after.tsv")
    parser.add_argument("--dry-log", type=Path, default=BASE / "ground_unit_vehicle_wave392_dry.log")
    parser.add_argument("--apply-log", type=Path, default=BASE / "ground_unit_vehicle_wave392_apply.log")
    parser.add_argument("--out", type=Path, default=BASE / "ground-unit-vehicle-wave392.json")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    _report, status = validate(args)
    return status if args.check else 0


if __name__ == "__main__":
    raise SystemExit(main())
