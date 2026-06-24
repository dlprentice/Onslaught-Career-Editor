#!/usr/bin/env python3
"""Validate the Wave389 GillM-family Ghidra correction tranche."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "gillm-family-wave389" / "current"

COMMON_TAGS = {"static-reaudit", "gillm-family-wave389", "retail-binary-evidence"}


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
    "0x004799c0": target(
        "CGillM__VFunc09_InitGroundedSpawnState",
        "void __thiscall CGillM__VFunc09_InitGroundedSpawnState(void * this, void * spawn_state)",
        ["CGillM RTTI vtable 0x005e0b30 slot 9", "+0x26c", "+0x274 grounded", "runtime behavior, and rebuild parity remain unproven"],
        ["+ 0x26c", "+ 0x274", "CStaticShadows__SampleShadowHeightBilinear"],
        ["cgillm", "vtable-slot", "owner-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x00479a50": target(
        "CGillM__InitLegMotion",
        "void __thiscall CGillM__InitLegMotion(void * this, void * init_data)",
        ["CGillM vtable 0x005e0b30 slot 117", "LegMotion", "0xf0-byte CMCGillM", "runtime animation behavior, and rebuild parity remain unproven"],
        ["s_LegMotion_00623074", "OID__AllocObject(0xf0", "CMCMech__SetParams"],
        ["cgillm", "cmcgillm", "legmotion", "signature-hardened", "comment-hardened"],
    ),
    "0x00479b40": target(
        "SharedCMCMech__ScalarDeletingDestructor",
        "void * __thiscall SharedCMCMech__ScalarDeletingDestructor(void * this, byte flags)",
        ["CMCBattleEngine, CMCGillM, and CMCThunderHead", "calls CMCMech__Destructor", "runtime destruction behavior, and rebuild parity remain unproven"],
        ["CMCMech__Destructor", "OID__FreeObject"],
        ["shared-cmc", "destructor", "scalar-deleting-dtor", "owner-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x00479b60": target(
        "CGillM__InitGillMAIComponent",
        "void __thiscall CGillM__InitGillMAIComponent(void * this, void * init_data)",
        ["CGillM vtable 0x005e0b30 slot 118", "CGillMAI RTTI vtable 0x005dbcb4", "this+0x13c", "runtime behavior, and rebuild parity remain unproven"],
        ["OID__AllocObject(0x60", "CWarspite__Init", "+ 0x13c"],
        ["cgillm", "cgillmai", "warspite-base", "owner-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x00479bf0": target(
        "CGillMAI__ScalarDeletingDestructor",
        "void * __thiscall CGillMAI__ScalarDeletingDestructor(void * this, byte flags)",
        ["CGillMAI RTTI vtable 0x005dbcb4 slot 1", "calls CGillMAI__Destructor", "runtime destruction behavior, and rebuild parity remain unproven"],
        ["CGillMAI__Destructor", "OID__FreeObject"],
        ["cgillmai", "destructor", "scalar-deleting-dtor", "owner-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x00479c10": target(
        "CGillMAI__Destructor",
        "void __fastcall CGillMAI__Destructor(void * this)",
        ["called only by the CGillMAI scalar-deleting destructor", "this+0x28", "CMonitor__Shutdown", "runtime destruction behavior, and rebuild parity remain unproven"],
        ["CSPtrSet__Remove", "CMonitor__Shutdown"],
        ["cgillmai", "destructor", "owner-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x00479cb0": target(
        "CGillM__InitTerrainGuideComponent",
        "void __fastcall CGillM__InitTerrainGuideComponent(void * this)",
        ["CGillM vtable 0x005e0b30 slot 119", "CTerrainGuide__ctor_like_004f1ec0", "this+0x208", "runtime behavior, and rebuild parity remain unproven"],
        ["OID__AllocObject(0x20", "CTerrainGuide__ctor_like_004f1ec0", "+ 0x208"],
        ["cgillm", "terrain-guide", "owner-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x00479d10": target(
        "CGillM__UpdateGroundedVerticalDrift",
        "void __fastcall CGillM__UpdateGroundedVerticalDrift(void * this)",
        ["owner correction from the older CExplosionInitThing label", "CGillM RTTI vtable 0x005e0b30 slot 66", "+0x244 mode/state", "runtime behavior, and rebuild parity remain unproven"],
        ["+ 0x274", "+ 0x244", "CStaticShadows__SampleShadowHeightBilinear"],
        ["cgillm", "grounded-state", "owner-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x00479db0": target(
        "CGillM__TriggerRandomArmHitAnimationIfReady",
        "void __fastcall CGillM__TriggerRandomArmHitAnimationIfReady(void * this)",
        ["owner/name correction from the older CExplosionInitThing label", "Gill_M_Left_Arm", "Gill_M_Right_Arm", "runtime animation behavior, and rebuild parity remain unproven"],
        ["Gill_M_Left_Arm", "Gill_M_Right_Arm", "CUnitAI__PlayHitAnimationAndSetFlag"],
        ["cgillm", "arm-hit-animation", "owner-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x00479f30": target(
        "CGillM__ComputeTerrainClearanceNoiseScale",
        "double __fastcall CGillM__ComputeTerrainClearanceNoiseScale(void * this)",
        ["owner correction from the older CUnitAI label", "CMCGillM slot-wrapper region", "samples two static-shadow heights", "runtime movement behavior, and rebuild parity remain unproven"],
        ["CStaticShadows__SampleShadowHeightBilinear", "Vec3__Magnitude", "OID__AcosWrapper"],
        ["cgillm", "terrain", "owner-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x0047a0b0": target(
        "CGillM__ComputeLateralSlopeAlignment",
        "double __fastcall CGillM__ComputeLateralSlopeAlignment(void * this)",
        ["owner correction from the older CUnitAI label", "heading field +0x114", "samples a heightfield normal", "runtime movement behavior, and rebuild parity remain unproven"],
        ["+ 0x114", "CMonitor__SampleHeightfieldNormalAtXY", "SQRT"],
        ["cgillm", "terrain", "owner-corrected", "signature-hardened", "comment-hardened"],
    ),
}

EXPECTED_DRY = {"updated": 0, "skipped": 11, "renamed": 0, "would_rename": 10, "missing": 0, "bad": 0}
EXPECTED_APPLY = {"updated": 11, "skipped": 0, "renamed": 10, "would_rename": 0, "missing": 0, "bad": 0}

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
        for key in ("address", "target_addr", "vtable", "slot_addr", "pointer_addr", "function_entry"):
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


def vtable_slot_hit(rows: list[dict[str, str]], vtable: str, slot: str, function_name: str) -> bool:
    for row in rows:
        if normalize_address(row.get("vtable", "")) != normalize_address(vtable):
            continue
        if row.get("slot_index") != slot:
            continue
        if row.get("function_name") == function_name:
            return True
    return False


def type_hit(rows: list[dict[str, str]], vtable: str, type_name: str) -> bool:
    for row in rows:
        if normalize_address(row.get("vtable", "")) == normalize_address(vtable) and row.get("demangled_type_name") == type_name:
            return True
    return False


def validate(args: argparse.Namespace) -> tuple[dict[str, object], int]:
    metadata_rows = read_tsv(resolve(args.metadata))
    tag_rows = read_tsv(resolve(args.tags))
    vtable_type_rows = read_tsv(resolve(args.vtable_types))
    vtable_rows = read_tsv(resolve(args.vtable_slots))
    cgillm_vtable_rows = read_tsv(resolve(args.cgillm_vtable_slots))
    dry_summary = parse_summary(read_text(resolve(args.dry_log)))
    apply_summary = parse_summary(read_text(resolve(args.apply_log)))

    failures: list[str] = []
    checked: dict[str, object] = {
        "metadataRows": len(metadata_rows),
        "tagRows": len(tag_rows),
        "vtableTypeRows": len(vtable_type_rows),
        "vtableRows": len(vtable_rows),
        "cgillmVtableRows": len(cgillm_vtable_rows),
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

    for vtable, expected in {
        "0x005e0b30": "CGillM",
        "0x005dbc74": "CMCGillM",
        "0x005dbcb4": "CGillMAI",
        "0x005d88ec": "CMCBattleEngine",
        "0x005df890": "CMCThunderHead",
    }.items():
        if not type_hit(vtable_type_rows, vtable, expected):
            failures.append(f"missing RTTI hit {vtable} {expected}")

    required_slots = [
        (cgillm_vtable_rows, "0x005e0b30", "9", "CGillM__VFunc09_InitGroundedSpawnState"),
        (cgillm_vtable_rows, "0x005e0b30", "66", "CGillM__UpdateGroundedVerticalDrift"),
        (cgillm_vtable_rows, "0x005e0b30", "117", "CGillM__InitLegMotion"),
        (cgillm_vtable_rows, "0x005e0b30", "118", "CGillM__InitGillMAIComponent"),
        (cgillm_vtable_rows, "0x005e0b30", "119", "CGillM__InitTerrainGuideComponent"),
        (vtable_rows, "0x005dbcb4", "1", "CGillMAI__ScalarDeletingDestructor"),
        (vtable_rows, "0x005dbc74", "1", "SharedCMCMech__ScalarDeletingDestructor"),
        (vtable_rows, "0x005d88ec", "1", "SharedCMCMech__ScalarDeletingDestructor"),
        (vtable_rows, "0x005df890", "1", "SharedCMCMech__ScalarDeletingDestructor"),
    ]
    for rows, vtable, slot, name in required_slots:
        if not vtable_slot_hit(rows, vtable, slot, name):
            failures.append(f"missing vtable slot hit {vtable} slot {slot} -> {name}")

    status = "PASS" if not failures else "FAIL"
    report = {
        "schema": "ghidra-gillm-family-wave389",
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
            "cgillmVtableSlots": relative(resolve(args.cgillm_vtable_slots)),
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
    parser.add_argument("--vtable-types", type=Path, default=BASE / "vtable_types.tsv")
    parser.add_argument("--vtable-slots", type=Path, default=BASE / "vtable_slots_after.tsv")
    parser.add_argument("--cgillm-vtable-slots", type=Path, default=BASE / "cgillm_vtable_slots_after.tsv")
    parser.add_argument("--dry-log", type=Path, default=BASE / "gillm_family_wave389_dry.log")
    parser.add_argument("--apply-log", type=Path, default=BASE / "gillm_family_wave389_apply.log")
    parser.add_argument("--out", type=Path, default=BASE / "gillm-family-wave389.json")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    _report, status = validate(args)
    return status if args.check else 0


if __name__ == "__main__":
    raise SystemExit(main())
