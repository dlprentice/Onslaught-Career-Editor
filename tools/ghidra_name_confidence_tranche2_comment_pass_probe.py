#!/usr/bin/env python3
"""Verify the second Ghidra name-confidence saved comment pass."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "name-confidence-tranche2-comment-pass" / "current"
DEFAULT_DRY_LOG = BASE / "comments_dry.log"
DEFAULT_APPLY_LOG = BASE / "comments_apply.log"
DEFAULT_METADATA = BASE / "metadata_after.tsv"
DEFAULT_DECOMPILE_INDEX = BASE / "decompile_after" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_after"
DEFAULT_XREFS = BASE / "xrefs_after.tsv"
DEFAULT_OUT = BASE / "name-confidence-tranche2-comment-pass.json"

TARGETS = [
    {
        "address": "0x00411bf0",
        "name": "CEngine_Unk_0050a080__Wrapper_00411bf0",
        "commentTokens": [
            "mode-specific burst dispatch helper",
            "CEngine__CanProceedByTargetRangeGate",
            "CGeneralVolume__SpawnBurstFromPresetWithFallback",
            "runtime behavior remain",
        ],
        "decompileTokens": [
            "CEngine__CanProceedByTargetRangeGate",
            "CEngine__ClampBurstStartTimeFloorNow",
            "CGeneralVolume__SpawnBurstFromPresetWithFallback",
        ],
        "expectedXrefFunctions": ["CGeneralVolume__DispatchModeSpecificReset_13CF0_or_11BF0"],
    },
    {
        "address": "0x00412240",
        "name": "ROUND__Wrapper_00412240",
        "commentTokens": ["selected-entry rounded slot value", "not proven as a generic ROUND wrapper", "+0x55c", "runtime behavior remain"],
        "decompileTokens": ["ROUND(", "+ 0x55c", "+ 0x52c"],
        "expectedXrefFunctions": ["CExplosionInitThing__GetCurrentEntryRoundedSlotValue"],
    },
    {
        "address": "0x00412420",
        "name": "CText_GetStringById__Wrapper_00412420",
        "commentTokens": ["selected-entry display string helper", "CText__GetStringById", "g_Text", "runtime behavior remain"],
        "decompileTokens": ["CText__GetStringById", "g_Text", "+ 0x3c"],
        "expectedXrefFunctions": ["CExplosionInitThing__GetCurrentEntryDisplayString"],
    },
    {
        "address": "0x00412650",
        "name": "CSPtrSet_Remove__Wrapper_00412650",
        "commentTokens": ["profile weapon-list rebuild helper", "CSPtrSet__Remove", "CWorldPhysicsManager__CreateWeaponByIndex", "runtime behavior remain"],
        "decompileTokens": ["CSPtrSet__Remove", "CWorldPhysicsManager__CreateWeaponByIndex", "+ 0x50"],
        "expectedXrefFunctions": ["CBattleEngine__ApplyWeaponProfileByIndex", "CBattleEngine__InitTargetSetBucketState"],
    },
    {
        "address": "0x00412830",
        "name": "CCockpit_Unk_00411e70__Wrapper_00412830",
        "commentTokens": ["cockpit disable matching weapon and reselect helper", "CCockpit__CycleToNextUsableWeapon", "+0x9c", "runtime behavior remain"],
        "decompileTokens": ["CCockpit__CycleToNextUsableWeapon", "+ 0x9c", "param_1"],
        "expectedXrefRows": 1,
    },
    {
        "address": "0x00412ad0",
        "name": "ABS__Wrapper_00412ad0",
        "commentTokens": ["monitor surface-alignment angle update helper", "not proven as a generic ABS wrapper", "_DAT_005d85e0", "runtime behavior remain"],
        "decompileTokens": ["ABS(", "+ 0x24", "_DAT_005d85e0"],
        "expectedXrefFunctions": ["CMonitor__ProcessTrackingAndSurfaceAlignment"],
    },
    {
        "address": "0x00413660",
        "name": "CGeneralVolume_Unk_00409e60__Wrapper_00413660",
        "commentTokens": ["general-volume scaled energy drain helper", "CGeneralVolume__ToDoubleIdentity", "+0x278", "runtime behavior remain"],
        "decompileTokens": ["CGeneralVolume__ToDoubleIdentity", "+ 0x278", "+ 0x2c8"],
        "expectedXrefRows": 1,
    },
    {
        "address": "0x004146b0",
        "name": "CSPtrSet_Remove__Wrapper_004146b0",
        "commentTokens": ["profile weapon and special-slot rebuild helper", "CSPtrSet__Remove", "CWorldPhysicsManager__CreateWeaponByIndex", "runtime behavior remain"],
        "decompileTokens": ["CSPtrSet__Remove", "CWorldPhysicsManager__CreateWeaponByIndex", "+ 0x40", "+ 0x60"],
        "expectedXrefFunctions": ["CBattleEngine__ApplyWeaponProfileByIndex", "CBattleEngine__InitDashMoveParams"],
    },
    {
        "address": "0x004d3080",
        "name": "CGenericActiveReader_SetReader__Wrapper_004d3080",
        "commentTokens": ["game reader rebind and post-load toggle helper", "CGenericActiveReader__SetReader", "CGame__PostLoadProcess", "runtime behavior remain"],
        "decompileTokens": ["CGenericActiveReader__SetReader", "+ 0x574", "+ 0x154"],
        "expectedXrefFunctions": ["CGame__PostLoadProcess", "CGame__RespawnPlayer"],
    },
]


def relative(path: Path) -> str:
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


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def unescape_tsv(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_metadata(path: Path) -> list[dict[str, str]]:
    rows = read_tsv(path)
    for row in rows:
        row["comment"] = unescape_tsv(row.get("comment", ""))
    return rows


def read_xrefs(path: Path) -> list[dict[str, str]]:
    rows = read_tsv(path)
    for row in rows:
        row["target_addr"] = normalize_address(row.get("target_addr", ""))
    return rows


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


def has_log_line(log_text: str, prefix: str, address: str, name: str) -> bool:
    return f"{prefix}: {address} {name}" in log_text


def find_row(rows: list[dict[str, str]], address_key: str, address: str) -> dict[str, str] | None:
    wanted = normalize_address(address)
    for row in rows:
        if normalize_address(row.get(address_key, "")) == wanted:
            return row
    return None


def find_decompile_file(decompile_dir: Path, address: str) -> Path | None:
    if not decompile_dir.is_dir():
        return None
    needle = normalize_address(address)[2:]
    matches = sorted(decompile_dir.glob(f"{needle}_*.c"))
    return matches[0] if matches else None


def build_report(
    *,
    dry_log_path: Path = DEFAULT_DRY_LOG,
    apply_log_path: Path = DEFAULT_APPLY_LOG,
    metadata_path: Path = DEFAULT_METADATA,
    decompile_index_path: Path = DEFAULT_DECOMPILE_INDEX,
    decompile_dir: Path = DEFAULT_DECOMPILE_DIR,
    xrefs_path: Path = DEFAULT_XREFS,
) -> dict[str, object]:
    dry_log_path = resolve(dry_log_path)
    apply_log_path = resolve(apply_log_path)
    metadata_path = resolve(metadata_path)
    decompile_index_path = resolve(decompile_index_path)
    decompile_dir = resolve(decompile_dir)
    xrefs_path = resolve(xrefs_path)

    failures: list[str] = []
    for label, path in (
        ("dry comment log", dry_log_path),
        ("apply comment log", apply_log_path),
        ("metadata read-back", metadata_path),
        ("decompile index", decompile_index_path),
        ("xref read-back", xrefs_path),
    ):
        if not path.is_file():
            failures.append(f"missing {label}: {relative(path)}")
    if not decompile_dir.is_dir():
        failures.append(f"missing decompile dir: {relative(decompile_dir)}")

    dry_text = read_text(dry_log_path)
    apply_text = read_text(apply_log_path)
    metadata_rows = read_metadata(metadata_path)
    index_rows = read_tsv(decompile_index_path)
    xrefs = read_xrefs(xrefs_path)
    xrefs_by_target: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in xrefs:
        xrefs_by_target[row["target_addr"]].append(row)

    expected_count = len(TARGETS)
    dry_summary = parse_summary(dry_text)
    apply_summary = parse_summary(apply_text)
    if dry_summary != {"applied": 0, "skipped": expected_count, "missing": 0, "bad": 0}:
        failures.append("dry comment log summary is not the expected clean dry-run shape")
    if apply_summary != {"applied": expected_count, "skipped": 0, "missing": 0, "bad": 0}:
        failures.append("apply comment log summary is not the expected clean apply shape")

    readback: dict[str, object] = {}
    all_present = True
    for target in TARGETS:
        address = target["address"]
        name = target["name"]
        if not has_log_line(dry_text, "DRY", address, name):
            failures.append(f"dry log missing expected target {address} {name}")
        if not has_log_line(apply_text, "OK", address, name):
            failures.append(f"apply log missing expected target {address} {name}")

        metadata_row = find_row(metadata_rows, "address", address)
        index_row = find_row(index_rows, "address", address)
        decompile_file = find_decompile_file(decompile_dir, address)
        decompile_text = read_text(decompile_file) if decompile_file else ""
        target_xrefs = xrefs_by_target[normalize_address(address)]

        comment_tokens_present = False
        metadata_ok = False
        if metadata_row is None:
            failures.append(f"metadata read-back missing {address}")
        else:
            comment = metadata_row.get("comment", "")
            comment_tokens_present = all(token in comment for token in target["commentTokens"])
            metadata_ok = metadata_row.get("name") == name and metadata_row.get("status") == "OK" and comment_tokens_present
            if not metadata_ok:
                failures.append(f"metadata read-back for {address} lacks expected name/status/comment tokens")

        index_ok = False
        if index_row is None:
            failures.append(f"decompile index missing {address}")
        else:
            index_ok = index_row.get("name") == name and index_row.get("status") == "OK"
            if not index_ok:
                failures.append(f"decompile index for {address} lacks expected name/status")

        decompile_tokens_present = bool(decompile_text) and all(token in decompile_text for token in target["decompileTokens"])
        if not decompile_tokens_present:
            failures.append(f"decompile read-back for {address} lacks expected behavior tokens")

        xref_ok = True
        expected_rows = int(target.get("expectedXrefRows", 0))
        expected_functions = set(target.get("expectedXrefFunctions", []))
        if expected_rows and len(target_xrefs) < expected_rows:
            failures.append(f"{address} expected xref rows >= {expected_rows}, found {len(target_xrefs)}")
            xref_ok = False
        if expected_functions:
            observed = {row.get("from_function", "") for row in target_xrefs}
            missing = sorted(expected_functions - observed)
            if missing:
                failures.append(f"{address} missing expected xref context: {', '.join(missing)}")
                xref_ok = False

        target_ok = metadata_ok and index_ok and decompile_tokens_present and xref_ok
        all_present = all_present and target_ok
        readback[address] = {
            "name": metadata_row.get("name") if metadata_row else None,
            "status": metadata_row.get("status") if metadata_row else None,
            "commentTokensPresent": comment_tokens_present,
            "decompileTokensPresent": decompile_tokens_present,
            "xrefRows": len(target_xrefs),
            "decompile": relative(decompile_file) if decompile_file else None,
        }

    status = "PASS" if not failures else "FAIL"
    return {
        "schema": "ghidra-name-confidence-tranche2-comment-pass.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "candidateClassification": "tranche2-comment-candidates-commented"
        if status == "PASS"
        else "tranche2-comment-pass-blocked",
        "drySummary": dry_summary,
        "applySummary": apply_summary,
        "targetCount": expected_count,
        "targets": [{"address": target["address"], "name": target["name"]} for target in TARGETS],
        "readback": {"allCommentsAndContextPresent": all_present, "functions": readback, "xrefRows": len(xrefs)},
        "inputs": {
            "dryLog": relative(dry_log_path),
            "applyLog": relative(apply_log_path),
            "metadata": relative(metadata_path),
            "decompileIndex": relative(decompile_index_path),
            "decompileDir": relative(decompile_dir),
            "xrefs": relative(xrefs_path),
        },
        "failures": failures,
        "whatIsProven": [
            "The saved Ghidra project has proof-boundary comments for nine second-tranche name-confidence comment candidates.",
            "Read-back metadata confirms the expected current names and comment tokens after apply.",
            "Decompile and xref read-backs preserve the behavior/caller context that justified commenting instead of renaming.",
        ],
        "notProven": [
            "This does not rename any of the nine functions.",
            "This does not harden signatures, parameter names, local names, tags, structures, or data types.",
            "This does not prove exact source-to-retail identity or runtime behavior.",
            "This does not complete the broader Ghidra static re-audit queue.",
        ],
        "privacy": "Report stores repo-relative artifact paths, public addresses, function names, command summaries, counts, and proof boundaries only; raw Ghidra logs, metadata, decompile exports, and xrefs remain ignored under subagents/.",
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--dry-log", type=Path, default=DEFAULT_DRY_LOG)
    parser.add_argument("--apply-log", type=Path, default=DEFAULT_APPLY_LOG)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--decompile-index", type=Path, default=DEFAULT_DECOMPILE_INDEX)
    parser.add_argument("--decompile-dir", type=Path, default=DEFAULT_DECOMPILE_DIR)
    parser.add_argument("--xrefs", type=Path, default=DEFAULT_XREFS)
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
        metadata_path=args.metadata,
        decompile_index_path=args.decompile_index,
        decompile_dir=args.decompile_dir,
        xrefs_path=args.xrefs,
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("Ghidra name-confidence tranche 2 comment-pass probe")
        print(f"Status: {report['status']}")
        print(f"Output: {relative(out)}")
        print(f"Classification: {report['candidateClassification']}")
        print(f"Targets: {report['targetCount']}")
        print(f"Dry summary: {report['drySummary']}")
        print(f"Apply summary: {report['applySummary']}")
        print(f"All comments/context present: {report['readback']['allCommentsAndContextPresent']}")
        if report["failures"]:
            print("Failures:")
            for failure in report["failures"]:
                print(f"- {failure}")

    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
