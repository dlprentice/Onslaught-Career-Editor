#!/usr/bin/env python3
"""Validate the saved Ghidra Cannon activation/signature correction wave."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "cannon-wave315" / "current"

TARGETS = {
    "0x0041b1a0": {
        "name": "CCannon__Init",
        "signature": ["void", "__thiscall", "void * this", "void * init"],
        "comment": ["CGroundUnit__Init", "Active", "Inactive", "0x20", "0x60", "0x14", "+0x260", "unproven"],
        "decompile": ["CGroundUnit__Init", "CWorld__AddUnitToOccupancyGridAndRebuildShadows_Thunk"],
    },
    "0x0041b370": {
        "name": "CCannon__UpdateState",
        "signature": ["void", "__fastcall", "void * this"],
        "comment": ["activation update", "Activate", "Deactivate", "+0x214", "+0x13c", "+0x260", "+0x264", "unproven"],
        "decompile": ["CGroundUnit__UpdateLinkedEffectsByHeightClearance", "s_Activate", "s_Deactivate"],
    },
    "0x0041b450": {
        "name": "CCannon__VFuncSlot_02_RemoveFromWorldAndForward",
        "previous": ["CCannon__Destructor"],
        "signature": ["void", "__fastcall", "void * this"],
        "comment": ["slot-2", "CCannon", "CSentinel", "CWarspiteDome", "occupancy-grid", "VFuncSlot_02_004f95d0", "not a destructor", "unproven"],
        "decompile": ["CWorld__RemoveUnitFromOccupancyGrid_Thunk", "VFuncSlot_02_004f95d0"],
    },
    "0x0041b470": {
        "name": "CCannon__AdvanceActivationAnimationState",
        "previous": ["CCannon__SetState"],
        "signature": ["int", "__fastcall", "void * this"],
        "comment": ["current animation", "Activate", "Deactivate", "Active", "Inactive", "+0x260", "unproven"],
        "decompile": ["FindAnimationIndex", "s_Activate", "s_Deactivate", "s_Active", "s_Inactive"],
    },
    "0x0041b540": {
        "name": "CCannon__GetMidpoint",
        "signature": ["void", "__thiscall", "void * this", "float * outMidpoint"],
        "comment": ["target position", "scales the result", "+0x1c", "+0x20", "+0x24", "0.5", "unproven"],
        "decompile": ["CCannon__SelectTarget", "outMidpoint"],
    },
    "0x0041b590": {
        "name": "CCannon__VFuncSlot_50_MarkDestroyedResetDeployGraph",
        "previous": ["CCannon__CanFire"],
        "signature": ["int", "__fastcall", "void * this"],
        "comment": ["slot-50", "CCannon", "CWarspiteDome", "CGroundVehicle", "MarkDestroyed", "does not support the old CanFire label", "unproven"],
        "decompile": ["CGroundUnit__MarkDestroyedAndResetState", "CUnit__ResetDeploymentGraphAndScheduleEvent"],
    },
    "0x0047c970": {
        "name": "CGroundUnit__UpdateLinkedEffectsByHeightClearance",
        "signature": ["void", "__fastcall", "void * this"],
        "comment": ["CGroundUnit vtable", "height clearance", "+0x1d4", "+0x1e4", "+0x25c", "Cross-subclass", "unproven"],
        "decompile": ["CWorld__GetHeightSamplePacked16", "CUnit__UpdateMotionAttachmentsAndEffects"],
    },
    "0x0047ce80": {
        "name": "CGroundUnit__MarkDestroyedAndResetState",
        "signature": ["int", "__fastcall", "void * this"],
        "comment": ["CGroundUnit vtable", "CUnit__MarkDestroyedAndCleanupLinks", "+0x25c", "returns 1", "unproven"],
        "decompile": ["CUnit__MarkDestroyedAndCleanupLinks", "+ 0x25c"],
    },
    "0x004fd4d0": {
        "name": "CCannon__SelectTarget",
        "signature": ["void", "__thiscall", "void * this", "float * outTargetPosition"],
        "comment": ["outTargetPosition", "+0x178", "CDiveBomber__SelectTarget", "CUnitAI__GetWorldPositionForTargeting", "unproven"],
        "decompile": ["CDiveBomber__SelectTarget", "CUnitAI__GetWorldPositionForTargeting"],
    },
}

STALE_NAMES = [
    "CCannon__Destructor",
    "CCannon__SetState",
    "CCannon__CanFire",
]

EXPECTED_VTABLE_TYPES = {"CCannon", "CSentinel", "CWarspiteDome", "CGroundVehicle"}

DEFAULT_DRY = BASE / "signature_correction_dry.log"
DEFAULT_APPLY = BASE / "signature_correction_apply.log"
DEFAULT_METADATA = BASE / "metadata_final.tsv"
DEFAULT_INDEX = BASE / "decompile_final" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_final"
DEFAULT_XREFS = BASE / "xrefs_final.tsv"
DEFAULT_INSTRUCTIONS = BASE / "instructions_final.tsv"
DEFAULT_VTABLES = BASE / "vtable_selected_final.tsv"
DEFAULT_OUT = BASE / "cannon-activation-signature-correction.json"

OVERCLAIM_TOKENS = [
    "exact source identity proven",
    "runtime behavior proven",
    "rebuild parity proven",
    "fully re'ed",
]


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def unescape(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


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
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        for key in ("address", "target_addr", "function_entry"):
            if key in row and row[key] and not row[key].startswith("<"):
                row[key] = normalize_address(row[key])
        if "comment" in row:
            row["comment"] = unescape(row["comment"])
    return rows


def parse_summary(text: str) -> dict[str, int]:
    match = re.search(r"updated=(\d+)\s+skipped=(\d+)\s+renamed=(\d+)\s+missing=(\d+)\s+bad=(\d+)", text)
    if not match:
        return {"updated": -1, "skipped": -1, "renamed": -1, "missing": -1, "bad": -1}
    return {
        "updated": int(match.group(1)),
        "skipped": int(match.group(2)),
        "renamed": int(match.group(3)),
        "missing": int(match.group(4)),
        "bad": int(match.group(5)),
    }


def row_by_address(rows: list[dict[str, str]], address: str, key: str = "address") -> dict[str, str] | None:
    wanted = normalize_address(address)
    for row in rows:
        if normalize_address(row.get(key, "")) == wanted:
            return row
    return None


def rows_for_address(rows: list[dict[str, str]], address: str, key: str) -> list[dict[str, str]]:
    wanted = normalize_address(address)
    return [row for row in rows if normalize_address(row.get(key, "")) == wanted]


def decompile_text_for(directory: Path, address: str) -> str:
    if not directory.is_dir():
        return ""
    matches = sorted(directory.glob(f"{normalize_address(address)[2:]}_*.c"))
    if not matches:
        return ""
    return read_text(matches[0])


def build_report(
    *,
    dry_log_path: Path = DEFAULT_DRY,
    apply_log_path: Path = DEFAULT_APPLY,
    metadata_path: Path = DEFAULT_METADATA,
    decompile_index_path: Path = DEFAULT_INDEX,
    decompile_dir: Path = DEFAULT_DECOMPILE_DIR,
    xrefs_path: Path = DEFAULT_XREFS,
    instructions_path: Path = DEFAULT_INSTRUCTIONS,
    vtable_path: Path = DEFAULT_VTABLES,
) -> dict[str, object]:
    dry_log_path = resolve(dry_log_path)
    apply_log_path = resolve(apply_log_path)
    metadata_path = resolve(metadata_path)
    decompile_index_path = resolve(decompile_index_path)
    decompile_dir = resolve(decompile_dir)
    xrefs_path = resolve(xrefs_path)
    instructions_path = resolve(instructions_path)
    vtable_path = resolve(vtable_path)

    failures: list[str] = []
    for label, path in (
        ("dry log", dry_log_path),
        ("apply log", apply_log_path),
        ("metadata read-back", metadata_path),
        ("decompile index", decompile_index_path),
        ("xref read-back", xrefs_path),
        ("instruction read-back", instructions_path),
        ("vtable read-back", vtable_path),
    ):
        if not path.is_file():
            failures.append(f"missing {label}: {relative(path)}")
    if not decompile_dir.is_dir():
        failures.append(f"missing decompile dir: {relative(decompile_dir)}")

    dry_summary = parse_summary(read_text(dry_log_path))
    apply_summary = parse_summary(read_text(apply_log_path))
    if dry_summary != {"updated": 0, "skipped": 9, "renamed": 0, "missing": 0, "bad": 0}:
        failures.append(f"unexpected dry summary: {dry_summary}")
    if apply_summary != {"updated": 9, "skipped": 0, "renamed": 3, "missing": 0, "bad": 0}:
        failures.append(f"unexpected apply summary: {apply_summary}")

    metadata_rows = read_tsv(metadata_path)
    index_rows = read_tsv(decompile_index_path)
    xref_rows = read_tsv(xrefs_path)
    instruction_rows = read_tsv(instructions_path)
    vtable_rows = read_tsv(vtable_path)

    target_reports: list[dict[str, object]] = []
    for address, expected in TARGETS.items():
        row = row_by_address(metadata_rows, address)
        index_row = row_by_address(index_rows, address)
        if row is None:
            failures.append(f"metadata missing {address}")
            continue
        if index_row is None:
            failures.append(f"decompile index missing {address}")
            continue

        name = row.get("name", "")
        signature = row.get("signature", "")
        comment = row.get("comment", "")
        decompile_text = decompile_text_for(decompile_dir, address)
        target_xrefs = rows_for_address(xref_rows, address, "target_addr")
        target_instructions = rows_for_address(instruction_rows, address, "target_addr")

        if name != expected["name"]:
            failures.append(f"name mismatch {address}: {name} != {expected['name']}")
        for token in expected["signature"]:
            if not token_present(signature, token):
                failures.append(f"signature token missing {address}: {token} in {signature}")
        for token in expected["comment"]:
            if not token_present(comment, token):
                failures.append(f"comment token missing {address}: {token}")
        for token in expected["decompile"]:
            if not token_present(decompile_text, token):
                failures.append(f"decompile token missing {address}: {token}")
        if not target_xrefs:
            failures.append(f"xref rows missing {address}")
        if not target_instructions:
            failures.append(f"instruction rows missing {address}")

        combined_text = "\n".join([name, signature, comment, decompile_text])
        for stale in expected.get("previous", []):
            if token_present(name, stale) or token_present(signature, stale):
                failures.append(f"stale name still saved {address}: {stale}")
        for token in OVERCLAIM_TOKENS:
            if token_present(combined_text, token):
                failures.append(f"overclaim token present {address}: {token}")

        target_reports.append(
            {
                "address": address,
                "name": name,
                "signature": signature,
                "xrefRows": len(target_xrefs),
                "instructionRows": len(target_instructions),
            }
        )

    all_metadata_text = "\n".join(row.get("name", "") + "\t" + row.get("signature", "") for row in metadata_rows)
    for stale in STALE_NAMES:
        if token_present(all_metadata_text, stale):
            failures.append(f"stale saved label remains in metadata: {stale}")

    vtable_types = {row.get("demangled_type_name", "") for row in vtable_rows}
    missing_vtables = sorted(EXPECTED_VTABLE_TYPES - vtable_types)
    if missing_vtables:
        failures.append(f"missing vtable type read-back: {', '.join(missing_vtables)}")

    report: dict[str, object] = {
        "schema": "ghidra-cannon-activation-signature-correction.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": "FAIL" if failures else "PASS",
        "targets": target_reports,
        "drySummary": dry_summary,
        "applySummary": apply_summary,
        "vtableTypes": sorted(vtable_types),
        "evidence": {
            "dryLog": relative(dry_log_path),
            "applyLog": relative(apply_log_path),
            "metadata": relative(metadata_path),
            "decompileIndex": relative(decompile_index_path),
            "decompileDir": relative(decompile_dir),
            "xrefs": relative(xrefs_path),
            "instructions": relative(instructions_path),
            "vtables": relative(vtable_path),
        },
        "failures": failures,
    }
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if the report is not PASS")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report()
    out_path = resolve(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"ghidra_cannon_activation_signature_correction_probe: {report['status']}")
    print(f"report: {relative(out_path)}")
    if report["failures"]:
        for failure in report["failures"]:
            print(f"FAIL: {failure}")
    return 1 if args.check and report["status"] != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
