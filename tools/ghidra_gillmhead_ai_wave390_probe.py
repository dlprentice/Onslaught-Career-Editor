#!/usr/bin/env python3
"""Validate the Wave390 GillMHeadAI / pause-menu Ghidra correction tranche."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "gillmhead-wave390" / "current"

COMMON_TAGS = {"static-reaudit", "gillmhead-ai-wave390", "retail-binary-evidence"}


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
    "0x0047a760": target(
        "CGillMHead__CreateGillMHeadAIComponent",
        "void __thiscall CGillMHead__CreateGillMHeadAIComponent(void * this, void * init_data)",
        ["0x64-byte type-0x16", "CGillMHeadAI RTTI vtable 0x005dbcec", "this+0x13c", "runtime behavior, and rebuild parity remain unproven"],
        ["OID__AllocObject", "CWarspite__Init", "PTR_LAB_005dbcec"],
        ["cgillmhead", "cgillmheadai", "component-create", "owner-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x0047a7f0": target(
        "CGillMHeadAI__ScalarDeletingDestructor",
        "void * __thiscall CGillMHeadAI__ScalarDeletingDestructor(void * this, byte flags)",
        ["CGillMHeadAI vtable 0x005dbcec slot 1", "calls CGillMHeadAI__Destructor", "runtime destruction behavior and rebuild parity remain unproven"],
        ["CGillMHeadAI__Destructor", "OID__FreeObject"],
        ["cgillmheadai", "destructor", "scalar-deleting-dtor", "owner-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x0047a810": target(
        "CGillMHeadAI__Destructor",
        "void __fastcall CGillMHeadAI__Destructor(void * this)",
        ["restores the CUnitAI base vtable 0x005d8d1c", "+0x28", "+0x24", "+0x0c", "runtime cleanup behavior, and rebuild parity remain unproven"],
        ["CSPtrSet__Remove", "CMonitor__Shutdown"],
        ["cgillmheadai", "destructor", "owner-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x0047a8b0": target(
        "CGillMHeadAI__TryTransitionIdleToOpen",
        "int __fastcall CGillMHeadAI__TryTransitionIdleToOpen(void * this)",
        ["pointer table 0x005e42d8 slot 30", "idle", "open", "runtime animation behavior, and rebuild parity remain unproven"],
        ["SharedUnitAnimation__FindAnimationIndexOrZero", "CUnit__UpdateDeployStateAndChargeEffects", "SharedUnitAnimation__PlayAnimationByNameIfPresent"],
        ["cgillmheadai", "animation-state", "owner-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x0047a900": target(
        "CGillMHeadAI__AdvanceOpenAttackCloseState",
        "int __fastcall CGillMHeadAI__AdvanceOpenAttackCloseState(void * this)",
        ["pointer table 0x005e42d8 slot 3", "open, attack, close, and idle", "runtime animation behavior, and rebuild parity remain unproven"],
        ["SharedUnitAnimation__FindAnimationIndexOrZero", "SharedUnitAnimation__PlayAnimationByNameIfPresent", "CVBufTexture__HasAnyTrackedUnitBeforeTimeout"],
        ["cgillmheadai", "animation-state", "owner-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x0047afc0": target(
        "CGillMHeadAI__UpdateAimTransformAndTargetReader",
        "void __fastcall CGillMHeadAI__UpdateAimTransformAndTargetReader(void * this)",
        ["CGillMHeadAI vtable 0x005dbcec slot 3", "100 units along the owner facing vector", "runtime targeting behavior, and rebuild parity remain unproven"],
        ["CSquadNormal__SelectBestSupportOrEscort", "CWarspite__UpdateAimTransformAndAttachTargetReader", "_DAT_005db020"],
        ["cgillmheadai", "targeting", "warspite-base", "owner-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x0047b090": target(
        "CGillMHeadAI__UpdateTargetBallisticArcFlags",
        "void __fastcall CGillMHeadAI__UpdateTargetBallisticArcFlags(void * this)",
        ["older setup-model wording", "CGillMHeadAI vtable 0x005dbcec slot 4", "ballistic firing-readiness flags", "runtime firing behavior, and rebuild parity remain unproven"],
        ["CUnit__CanFireAtTarget_BallisticArcB", "CUnit__CanFireAtTarget_BallisticArcA"],
        ["cgillmheadai", "targeting", "ballistic-arc", "owner-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x004d0ff0": target(
        "CPauseMenu__InitPauseSession",
        "void __thiscall CPauseMenu__InitPauseSession(void * this, int activate_control)",
        ["CGame__Pause calls this on CGame::mPauseMenu", "pause-menu session state", "objective-dependent menu item", "UI runtime behavior, and rebuild parity remain unproven"],
        ["CGame__GetNumPrimaryObjectives", "CMenuItemRange__SetItemEnabled"],
        ["cpausemenu", "pause-flow", "signature-hardened", "comment-hardened"],
    ),
    "0x004d10b0": target(
        "CPauseMenu__DeactivatePauseSession",
        "void __thiscall CPauseMenu__DeactivatePauseSession(void * this, int deactivate_control)",
        ["older GillMHead label", "CGame__UnPause calls this on CGame::mPauseMenu", "+0x08 and +0x3c", "UI runtime behavior, and rebuild parity remain unproven"],
        ["PLATFORM__GetSysTimeFloat", "+ 0x3c", "+ 0x48"],
        ["cpausemenu", "pause-flow", "owner-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x004f4530": target(
        "SharedUnitAnimation__FindAnimationIndexOrZero",
        "int __thiscall SharedUnitAnimation__FindAnimationIndexOrZero(void * this, void * animation_name)",
        ["older CGillMHead-specific label", "BattleEngine animation/morph paths", "this+0x30", "runtime animation behavior, and rebuild parity remain unproven"],
        ["FindAnimationIndex", "+ 0x30"],
        ["shared-animation", "owner-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x004f4560": target(
        "SharedUnitAnimation__PlayAnimationByNameIfPresent",
        "void __thiscall SharedUnitAnimation__PlayAnimationByNameIfPresent(void * this, void * animation_name, int play_flag, int reset_flag)",
        ["older CGillMHead-specific label", "BattleEngine animation/morph paths", "vfunc +0xf0", "runtime animation behavior, and rebuild parity remain unproven"],
        ["FindAnimationIndex", "+ 0xf0"],
        ["shared-animation", "owner-corrected", "signature-hardened", "comment-hardened"],
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

    if not vtable_type_hit(vtable_type_rows, "0x005dbcec", "CGillMHeadAI"):
        failures.append("missing CGillMHeadAI RTTI hit for 0x005dbcec")
    if not vtable_type_hit(vtable_type_rows, "0x005d8d1c", "CUnitAI"):
        failures.append("missing CUnitAI base RTTI hit for 0x005d8d1c")

    required_slots = [
        ("0x005dbcec", "1", "CGillMHeadAI__ScalarDeletingDestructor"),
        ("0x005dbcec", "3", "CGillMHeadAI__UpdateAimTransformAndTargetReader"),
        ("0x005dbcec", "4", "CGillMHeadAI__UpdateTargetBallisticArcFlags"),
    ]
    for vtable, slot, name in required_slots:
        if not vtable_slot_hit(vtable_rows, vtable, slot, name):
            failures.append(f"missing vtable slot hit {vtable} slot {slot} -> {name}")

    required_pointer_slots = [
        ("3", "CGillMHeadAI__AdvanceOpenAttackCloseState"),
        ("30", "CGillMHeadAI__TryTransitionIdleToOpen"),
        ("63", "CGillMHead__CreateGillMHeadAIComponent"),
    ]
    for slot, name in required_pointer_slots:
        if not pointer_table_hit(pointer_rows, slot, name):
            failures.append(f"missing pointer table slot {slot} -> {name}")

    required_xrefs = [
        ("0x004d0ff0", "CGame__Pause"),
        ("0x004d10b0", "CGame__UnPause"),
        ("0x004f4560", "CBattleEngine__Morph"),
        ("0x004f4560", "CGillMHeadAI__TryTransitionIdleToOpen"),
        ("0x004f4530", "CGillMHeadAI__AdvanceOpenAttackCloseState"),
    ]
    for target_addr, source_name in required_xrefs:
        if not xref_hit(xref_rows, target_addr, source_name):
            failures.append(f"missing xref hit {source_name} -> {target_addr}")

    status = "PASS" if not failures else "FAIL"
    report = {
        "schema": "ghidra-gillmhead-ai-wave390",
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
    parser.add_argument("--pointer-table", type=Path, default=BASE / "init_pointer_table_after.tsv")
    parser.add_argument("--xrefs", type=Path, default=BASE / "xrefs_after.tsv")
    parser.add_argument("--dry-log", type=Path, default=BASE / "gillmhead_ai_wave390_dry.log")
    parser.add_argument("--apply-log", type=Path, default=BASE / "gillmhead_ai_wave390_apply.log")
    parser.add_argument("--out", type=Path, default=BASE / "gillmhead-ai-wave390.json")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    _report, status = validate(args)
    return status if args.check else 0


if __name__ == "__main__":
    raise SystemExit(main())
