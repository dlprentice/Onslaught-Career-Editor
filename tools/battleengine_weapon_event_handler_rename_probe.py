#!/usr/bin/env python3
"""Verify the weapon event-handler semantic rename read-back.

This probe checks a small saved Ghidra rename tranche for the recovered weapon
slot-0 handler and slot-1 scalar deleting destructor. It intentionally keeps
the claim behavior-based: event handling and destructor shape, not exact
source `CWeapon::Fire` or retail stealth behavior.
"""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "weapon-cluster-provisional-name" / "current"
DEFAULT_DRY_LOG = BASE / "rename_dry.log"
DEFAULT_APPLY_LOG = BASE / "rename_apply.log"
DEFAULT_DECOMPILE_INDEX = BASE / "decompile_after_rename" / "index.tsv"
DEFAULT_POINTER_TABLE = BASE / "table_005dfc94_after_rename.tsv"
DEFAULT_EVENT_DECOMPILE = BASE / "decompile_after_rename" / "00506930_CWeapon__HandleFireBurstEvent.c"
DEFAULT_DTOR_DECOMPILE = BASE / "decompile_after_rename" / "00505f70_CWeapon__scalar_deleting_dtor.c"
DEFAULT_OUT = BASE / "weapon-event-handler-rename.json"

EVENT_ADDR = "0x00506930"
DTOR_ADDR = "0x00505f70"
EVENT_OLD = "CWeapon__VFunc_00_00506930"
EVENT_NEW = "CWeapon__HandleFireBurstEvent"
DTOR_OLD = "CWeapon__VFunc_01_00505f70"
DTOR_NEW = "CWeapon__scalar_deleting_dtor"


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if value in {"", "<none>", "<no_function>"}:
        return value
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def find_row(rows: list[dict[str, str]], key: str, address: str) -> dict[str, str] | None:
    wanted = normalize_address(address)
    for row in rows:
        if normalize_address(row.get(key, "")) == wanted:
            return row
    return None


def parse_summary(log_text: str) -> dict[str, int]:
    match = re.search(r"applied=(\d+)\s+skipped=(\d+)\s+missing=(\d+)\s+bad=(\d+)", log_text)
    if not match:
        return {"applied": -1, "skipped": -1, "missing": -1, "bad": -1}
    return {
        "applied": int(match.group(1)),
        "skipped": int(match.group(2)),
        "missing": int(match.group(3)),
        "bad": int(match.group(4)),
    }


def has_rename_line(log_text: str, prefix: str, address: str, old: str, new: str) -> bool:
    wanted = f"{prefix}: {address} {old} -> {new}"
    return wanted in log_text


def build_report(
    *,
    dry_log_path: Path = DEFAULT_DRY_LOG,
    apply_log_path: Path = DEFAULT_APPLY_LOG,
    decompile_index_path: Path = DEFAULT_DECOMPILE_INDEX,
    pointer_table_path: Path = DEFAULT_POINTER_TABLE,
    event_decompile_path: Path = DEFAULT_EVENT_DECOMPILE,
    dtor_decompile_path: Path = DEFAULT_DTOR_DECOMPILE,
) -> dict[str, object]:
    dry_log_path = resolve(dry_log_path)
    apply_log_path = resolve(apply_log_path)
    decompile_index_path = resolve(decompile_index_path)
    pointer_table_path = resolve(pointer_table_path)
    event_decompile_path = resolve(event_decompile_path)
    dtor_decompile_path = resolve(dtor_decompile_path)

    failures: list[str] = []
    for label, path in (
        ("dry rename log", dry_log_path),
        ("apply rename log", apply_log_path),
        ("decompile read-back index", decompile_index_path),
        ("pointer table read-back", pointer_table_path),
        ("event handler decompile", event_decompile_path),
        ("scalar deleting destructor decompile", dtor_decompile_path),
    ):
        if not path.is_file():
            failures.append(f"missing {label}: {relative(path)}")

    dry_text = read_text(dry_log_path)
    apply_text = read_text(apply_log_path)
    index_rows = read_tsv(decompile_index_path)
    table_rows = read_tsv(pointer_table_path)
    event_text = read_text(event_decompile_path)
    dtor_text = read_text(dtor_decompile_path)

    dry_summary = parse_summary(dry_text)
    apply_summary = parse_summary(apply_text)

    dry_expected = (
        has_rename_line(dry_text, "DRY", EVENT_ADDR, EVENT_OLD, EVENT_NEW)
        and has_rename_line(dry_text, "DRY", DTOR_ADDR, DTOR_OLD, DTOR_NEW)
        and dry_summary == {"applied": 0, "skipped": 2, "missing": 0, "bad": 0}
    )
    if not dry_expected:
        failures.append("dry rename log does not show the expected two clean DRY rows")

    apply_expected = (
        has_rename_line(apply_text, "OK", EVENT_ADDR, EVENT_OLD, EVENT_NEW)
        and has_rename_line(apply_text, "OK", DTOR_ADDR, DTOR_OLD, DTOR_NEW)
        and apply_summary == {"applied": 2, "skipped": 0, "missing": 0, "bad": 0}
    )
    if not apply_expected:
        failures.append("apply rename log does not show the expected two clean OK rows")

    event_row = find_row(index_rows, "address", EVENT_ADDR)
    dtor_row = find_row(index_rows, "address", DTOR_ADDR)
    event_handler_renamed = event_row is not None and event_row.get("name") == EVENT_NEW and event_row.get("status") == "OK"
    scalar_dtor_renamed = dtor_row is not None and dtor_row.get("name") == DTOR_NEW and dtor_row.get("status") == "OK"
    if not event_handler_renamed:
        failures.append(f"missing decompile read-back for {EVENT_ADDR} as {EVENT_NEW}")
    if not scalar_dtor_renamed:
        failures.append(f"missing decompile read-back for {DTOR_ADDR} as {DTOR_NEW}")

    table_slot0 = next((row for row in table_rows if row.get("slot") == "0"), None)
    table_slot1 = next((row for row in table_rows if row.get("slot") == "1"), None)
    table_slot4 = next((row for row in table_rows if row.get("slot") == "4"), None)
    table_names_updated = (
        table_slot0 is not None
        and normalize_address(table_slot0.get("ptr", "")) == EVENT_ADDR
        and table_slot0.get("ptr_name") == EVENT_NEW
        and table_slot1 is not None
        and normalize_address(table_slot1.get("ptr", "")) == DTOR_ADDR
        and table_slot1.get("ptr_name") == DTOR_NEW
    )
    if not table_names_updated:
        failures.append("pointer table read-back does not show updated slot 0/1 names")

    adjacent_non_code_after_vtable = table_slot4 is not None and table_slot4.get("ptr_name") == "<none>"

    event_schedules_burst = all(
        token in event_text
        for token in ("0x1389", "CEventManager__AddEvent_AtTime", "CEngine__SpawnProjectileBurstFromCurrentPreset")
    )
    if not event_schedules_burst:
        failures.append("event handler decompile is missing the event id, burst helper, or reschedule token")

    dtor_is_scalar_deleting = all(
        token in dtor_text
        for token in ("CWeapon__DetachFromSetAndShutdownMonitor", "OID__FreeObject")
    )
    if not dtor_is_scalar_deleting:
        failures.append("destructor decompile is missing detach/shutdown or conditional free evidence")

    status = "PASS" if not failures else "FAIL"
    return {
        "schema": "battleengine-weapon-event-handler-rename.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "candidateClassification": "weapon-event-handler-and-dtor-renamed"
        if status == "PASS"
        else "weapon-event-handler-rename-blocked",
        "renames": [
            {"address": EVENT_ADDR, "oldName": EVENT_OLD, "newName": EVENT_NEW},
            {"address": DTOR_ADDR, "oldName": DTOR_OLD, "newName": DTOR_NEW},
        ],
        "drySummary": dry_summary,
        "applySummary": apply_summary,
        "readback": {
            "eventHandlerRenamed": event_handler_renamed,
            "scalarDtorRenamed": scalar_dtor_renamed,
            "pointerTableNamesUpdated": table_names_updated,
        },
        "evidence": {
            "eventSchedulesBurst": event_schedules_burst,
            "dtorIsScalarDeleting": dtor_is_scalar_deleting,
            "adjacentNonCodeAfterFirstVtable": adjacent_non_code_after_vtable,
        },
        "inputs": {
            "dryLog": relative(dry_log_path),
            "applyLog": relative(apply_log_path),
            "decompileIndex": relative(decompile_index_path),
            "pointerTable": relative(pointer_table_path),
            "eventDecompile": relative(event_decompile_path),
            "dtorDecompile": relative(dtor_decompile_path),
        },
        "failures": failures,
        "whatIsProven": [
            "The saved Ghidra names for 0x00506930 and 0x00505f70 were changed after a clean dry-run and clean apply.",
            "Read-back shows 0x00506930 as CWeapon__HandleFireBurstEvent and 0x00505f70 as CWeapon__scalar_deleting_dtor.",
            "The event-handler decompile contains the weapon burst event id, projectile-burst helper call, and event reschedule path.",
            "The destructor decompile detaches/shuts down the weapon and conditionally frees the object.",
        ],
        "notProven": [
            "This does not prove exact source CWeapon::Fire or CBattleEngine::WeaponFired identity.",
            "This does not prove retail weapon fire clears or preserves stealth.",
            "This does not settle the owner/name/signature for 0x00506010 or 0x005069f0.",
            "This does not prove runtime cloak activation, target-lock behavior, projectile behavior, or fire-while-cloaked behavior.",
        ],
        "privacy": "Report stores repo-relative artifact paths, public addresses, function names, command summaries, counts, and proof boundaries only; raw decompile and Ghidra logs remain ignored under subagents/.",
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--dry-log", type=Path, default=DEFAULT_DRY_LOG)
    parser.add_argument("--apply-log", type=Path, default=DEFAULT_APPLY_LOG)
    parser.add_argument("--decompile-index", type=Path, default=DEFAULT_DECOMPILE_INDEX)
    parser.add_argument("--pointer-table", type=Path, default=DEFAULT_POINTER_TABLE)
    parser.add_argument("--event-decompile", type=Path, default=DEFAULT_EVENT_DECOMPILE)
    parser.add_argument("--dtor-decompile", type=Path, default=DEFAULT_DTOR_DECOMPILE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if not args.check:
        parser.error("expected --check")

    out = resolve(args.out)
    try:
        out.resolve().relative_to((ROOT / "subagents").resolve())
    except ValueError:
        print(f"Refusing to write report outside subagents/: {out}", file=sys.stderr)
        return 1

    report = build_report(
        dry_log_path=args.dry_log,
        apply_log_path=args.apply_log,
        decompile_index_path=args.decompile_index,
        pointer_table_path=args.pointer_table,
        event_decompile_path=args.event_decompile,
        dtor_decompile_path=args.dtor_decompile,
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("BattleEngine weapon event-handler rename probe")
        print(f"Status: {report['status']}")
        print(f"Output: {relative(out)}")
        print(f"Classification: {report['candidateClassification']}")
        for rename in report["renames"]:
            print(f"Rename: {rename['address']} {rename['oldName']} -> {rename['newName']}")
        print(f"Dry summary: {report['drySummary']}")
        print(f"Apply summary: {report['applySummary']}")
        print(f"Event handler renamed: {report['readback']['eventHandlerRenamed']}")
        print(f"Scalar dtor renamed: {report['readback']['scalarDtorRenamed']}")
        print(f"Event schedules burst: {report['evidence']['eventSchedulesBurst']}")
        print(f"Scalar deleting dtor evidence: {report['evidence']['dtorIsScalarDeleting']}")
        if report["failures"]:
            print("Failures:")
            for failure in report["failures"]:
                print(f"- {failure}")

    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
