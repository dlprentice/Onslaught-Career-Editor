#!/usr/bin/env python3
"""Validate the air-unit vfunc owner/name correction tranche."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "airunit-vfunc-owner-correction" / "current"

TARGETS = {
    "0x00402030": {
        "name": "CActor__VFunc_18_SyncOldVectorAfterBaseCall",
        "signatureTokens": ["void", "__thiscall", "void * this"],
        "commentTokens": ["CActor", "vtable slot 18", "this+0x1c", "this+0x8c", "provisional"],
        "decompileTokens": ["CActor__VFunc_18_SyncOldVectorAfterBaseCall", "this", "0x1c", "0x8c"],
    },
    "0x00402fa0": {
        "name": "CUnit__UpdateMotionAndTrailEffects",
        "signatureTokens": ["void", "__thiscall", "void * this"],
        "commentTokens": ["Unit motion/effects pass", "vtable slot 66", "velocity", "trail", "low-altitude"],
        "decompileTokens": ["CUnit__UpdateMotionAndTrailEffects", "CUnit__UpdateMotionAttachmentsAndEffects", "0x170"],
    },
    "0x00403730": {
        "name": "CAirUnit__VFunc_68_TimestampAndCrashIfNoAirSupport",
        "signatureTokens": ["void", "__thiscall", "void * this"],
        "commentTokens": ["Air-unit vtable slot 68", "unit-data +0x11c", "Not a CExplosionInitThing"],
        "decompileTokens": ["CAirUnit__VFunc_68_TimestampAndCrashIfNoAirSupport", "CUnitAI__SetStateTimestampCCToNow", "0x11c"],
    },
    "0x00403760": {
        "name": "CAirUnit__VFunc_69_ResetD0AndCrashIfNoSupportModes",
        "signatureTokens": ["void", "__thiscall", "void * this"],
        "commentTokens": ["Air-unit vtable slot 69", "unit-data +0x11c/+0x124", "duplicate CUnitAI"],
        "decompileTokens": ["CAirUnit__VFunc_69_ResetD0AndCrashIfNoSupportModes", "CUnit__ResetFieldD0ToGlobalThreshold", "0x124"],
    },
    "0x00403a50": {
        "name": "CAirUnit__VFunc_117_HasPositionDeltaWhileFlag4Clear",
        "signatureTokens": ["int", "__thiscall", "void * this"],
        "commentTokens": ["Air-unit vtable slot 117", "position components differ", "Not a CFrontEndPage"],
        "decompileTokens": ["CAirUnit__VFunc_117_HasPositionDeltaWhileFlag4Clear", "0x8c", "0x1c", "0x2c"],
    },
    "0x004d20a0": {
        "name": "CPlane__VFunc_68_CrashIfNoAirSupport",
        "signatureTokens": ["void", "__thiscall", "void * this"],
        "commentTokens": ["Plane-family vtable slot 68", "CAirUnit slot-68", "unit-data +0x11c"],
        "decompileTokens": ["CPlane__VFunc_68_CrashIfNoAirSupport", "CAirUnit__VFunc_68_TimestampAndCrashIfNoAirSupport", "0x11c"],
    },
    "0x0047bf60": {
        "name": "CPlane__VFunc_69_CrashIfNoSupportModes",
        "signatureTokens": ["void", "__thiscall", "void * this"],
        "commentTokens": ["Plane-family vtable slot 69", "CAirUnit slot-69", "unit-data +0x11c/+0x124"],
        "decompileTokens": ["CPlane__VFunc_69_CrashIfNoSupportModes", "CAirUnit__VFunc_69_ResetD0AndCrashIfNoSupportModes", "0x124"],
    },
}

EXPECTED_VTABLE_ROWS = {
    ("00402030", "CActor", "18"),
    ("00403730", "CAirUnit", "68"),
    ("00403760", "CAirUnit", "69"),
    ("00403a50", "CAirUnit", "117"),
    ("004d20a0", "CPlane", "68"),
    ("0047bf60", "CPlane", "69"),
}

DEFAULT_APPLY_DRY = BASE / "apply_dry.log"
DEFAULT_APPLY = BASE / "apply.log"
DEFAULT_METADATA = BASE / "metadata_final.tsv"
DEFAULT_INDEX = BASE / "decompile_final" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_final"
DEFAULT_XREFS = BASE / "xrefs_final.tsv"
DEFAULT_INSTRUCTIONS = BASE / "instructions_final.tsv"
DEFAULT_VTABLES = BASE / "vtable_owner_map_final.tsv"
DEFAULT_OUT = BASE / "airunit-vfunc-owner-correction.json"

STALE_NAME_TOKENS = [
    "CExplosionInitThing__UpdateAndTriggerDeferredStart",
    "CExplosionInitThing__UpdateAndTriggerDeferredStart_NoUnitAIPrepass",
    "CUnitAI__ProcessAndCrashIfNoAirOrHoverSupport",
    "CFrontEndPage__HasPendingPositionLerp",
    "VFuncSlot_18_00402030",
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
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def compact(value: str) -> str:
    return "".join(value.lower().split())


def token_present(text: str, token: str) -> bool:
    return compact(token) in compact(text)


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def parse_update_summary(log_text: str) -> dict[str, int]:
    match = re.search(r"updated=(\d+)\s+skipped=(\d+)\s+missing=(\d+)\s+bad=(\d+)", log_text)
    if not match:
        return {"updated": -1, "skipped": -1, "missing": -1, "bad": -1}
    return {
        "updated": int(match.group(1)),
        "skipped": int(match.group(2)),
        "missing": int(match.group(3)),
        "bad": int(match.group(4)),
    }


def find_row(rows: list[dict[str, str]], key: str, address: str) -> dict[str, str] | None:
    wanted = normalize_address(address)
    for row in rows:
        if normalize_address(row.get(key, "")) == wanted:
            return row
    return None


def decompile_file_for(decompile_dir: Path, address: str) -> Path | None:
    if not decompile_dir.is_dir():
        return None
    matches = sorted(decompile_dir.glob(f"{normalize_address(address)[2:]}_*.c"))
    return matches[0] if matches else None


def build_report(
    *,
    apply_dry_log_path: Path = DEFAULT_APPLY_DRY,
    apply_log_path: Path = DEFAULT_APPLY,
    metadata_path: Path = DEFAULT_METADATA,
    decompile_index_path: Path = DEFAULT_INDEX,
    decompile_dir: Path = DEFAULT_DECOMPILE_DIR,
    xrefs_path: Path = DEFAULT_XREFS,
    instructions_path: Path = DEFAULT_INSTRUCTIONS,
    vtable_map_path: Path = DEFAULT_VTABLES,
) -> dict[str, object]:
    metadata_rows = read_tsv(metadata_path)
    index_rows = read_tsv(decompile_index_path)
    xref_rows = read_tsv(xrefs_path)
    instruction_rows = read_tsv(instructions_path)
    vtable_rows = read_tsv(vtable_map_path)

    failures: list[str] = []
    stale_hits: list[dict[str, str]] = []
    target_reports: dict[str, dict[str, object]] = {}

    apply_dry = parse_update_summary(read_text(apply_dry_log_path))
    apply = parse_update_summary(read_text(apply_log_path))
    if apply_dry != {"updated": 0, "skipped": len(TARGETS), "missing": 0, "bad": 0}:
        failures.append(f"unexpected dry summary {apply_dry}")
    if apply != {"updated": len(TARGETS), "skipped": 0, "missing": 0, "bad": 0}:
        failures.append(f"unexpected apply summary {apply}")

    for address, expected in TARGETS.items():
        metadata = find_row(metadata_rows, "address", address)
        index = find_row(index_rows, "address", address)
        decompile_file = decompile_file_for(decompile_dir, address)
        decompile_text = read_text(decompile_file) if decompile_file else ""
        name_sig = " ".join([
            metadata.get("name", "") if metadata else "",
            metadata.get("signature", "") if metadata else "",
            index.get("name", "") if index else "",
            index.get("signature", "") if index else "",
        ])

        report = {
            "name": metadata.get("name") if metadata else None,
            "signature": metadata.get("signature") if metadata else None,
            "comment": metadata.get("comment") if metadata else None,
            "decompileFile": relative(decompile_file) if decompile_file else None,
        }
        target_reports[address] = report

        if metadata is None:
            failures.append(f"{address} missing metadata row")
            continue
        if metadata.get("name") != expected["name"]:
            failures.append(f"{address} name mismatch: {metadata.get('name')} != {expected['name']}")
        if index is None or index.get("name") != expected["name"]:
            failures.append(f"{address} missing/mismatched decompile index row")

        missing_sig = [token for token in expected["signatureTokens"] if not token_present(metadata.get("signature", ""), token)]
        if missing_sig:
            failures.append(f"{address} signature tokens missing: {missing_sig}")
        missing_comment = [token for token in expected["commentTokens"] if not token_present(metadata.get("comment", ""), token)]
        if missing_comment:
            failures.append(f"{address} comment tokens missing: {missing_comment}")
        missing_decompile = [token for token in expected["decompileTokens"] if not token_present(decompile_text, token)]
        if missing_decompile:
            failures.append(f"{address} decompile tokens missing: {missing_decompile}")

        for token in STALE_NAME_TOKENS:
            if token_present(name_sig, token):
                stale_hits.append({"address": address, "token": token})
                failures.append(f"{address} stale name/signature token retained: {token}")

    vtable_seen = {
        (row.get("target_addr", "").lower(), row.get("type", ""), row.get("slot", ""))
        for row in vtable_rows
    }
    for expected_row in EXPECTED_VTABLE_ROWS:
        if expected_row not in vtable_seen:
            failures.append(f"missing vtable owner-map row {expected_row}")

    xref_target_count = len({normalize_address(row.get("target_addr", "")) for row in xref_rows if row.get("target_addr")})
    instruction_target_count = len({normalize_address(row.get("target_addr", "")) for row in instruction_rows if row.get("target_addr")})
    if xref_target_count < len(TARGETS):
        failures.append(f"xrefs cover only {xref_target_count}/{len(TARGETS)} targets")
    if instruction_target_count < len(TARGETS):
        failures.append(f"instructions cover only {instruction_target_count}/{len(TARGETS)} targets")

    report = {
        "schema": "airunit-vfunc-owner-correction.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not failures else "FAIL",
        "summary": {
            "targets": len(TARGETS),
            "renamedOrHardenedTargets": len(TARGETS) - len([a for a in TARGETS if f"{a} missing metadata row" in failures]),
            "metadataRows": len(metadata_rows),
            "xrefRows": len(xref_rows),
            "instructionRows": len(instruction_rows),
            "vtableOwnerRows": len(vtable_rows),
            "staleNameTokenHits": len(stale_hits),
        },
        "apply": {"dry": apply_dry, "apply": apply},
        "targets": target_reports,
        "artifacts": {
            "applyDryLog": relative(apply_dry_log_path),
            "applyLog": relative(apply_log_path),
            "metadata": relative(metadata_path),
            "decompileIndex": relative(decompile_index_path),
            "decompileDir": relative(decompile_dir),
            "xrefs": relative(xrefs_path),
            "instructions": relative(instructions_path),
            "vtableOwnerMap": relative(vtable_map_path),
        },
        "staleHits": stale_hits,
        "failures": failures,
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Exit non-zero unless the probe passes.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--apply-dry-log", type=Path, default=DEFAULT_APPLY_DRY)
    parser.add_argument("--apply-log", type=Path, default=DEFAULT_APPLY)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--decompile-index", type=Path, default=DEFAULT_INDEX)
    parser.add_argument("--decompile-dir", type=Path, default=DEFAULT_DECOMPILE_DIR)
    parser.add_argument("--xrefs", type=Path, default=DEFAULT_XREFS)
    parser.add_argument("--instructions", type=Path, default=DEFAULT_INSTRUCTIONS)
    parser.add_argument("--vtable-map", type=Path, default=DEFAULT_VTABLES)
    args = parser.parse_args()

    report = build_report(
        apply_dry_log_path=resolve(args.apply_dry_log),
        apply_log_path=resolve(args.apply_log),
        metadata_path=resolve(args.metadata),
        decompile_index_path=resolve(args.decompile_index),
        decompile_dir=resolve(args.decompile_dir),
        xrefs_path=resolve(args.xrefs),
        instructions_path=resolve(args.instructions),
        vtable_map_path=resolve(args.vtable_map),
    )

    out_path = resolve(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"Status: {report['status']}")
    print(f"Targets: {report['summary']['targets']}")
    print(f"Vtable owner rows: {report['summary']['vtableOwnerRows']}")
    print(f"Stale name token hits: {report['summary']['staleNameTokenHits']}")
    print(f"Report: {relative(out_path)}")

    if args.check and report["status"] != "PASS":
        for failure in report["failures"]:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
