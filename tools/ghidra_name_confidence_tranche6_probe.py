#!/usr/bin/env python3
"""Classify the sixth read-only Ghidra name-confidence re-audit tranche."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "name-confidence-tranche6" / "current"
DEFAULT_METADATA = BASE / "metadata.tsv"
DEFAULT_INDEX = BASE / "decompile" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile"
DEFAULT_XREFS = BASE / "xrefs.tsv"
DEFAULT_INSTRUCTIONS = BASE / "instructions.tsv"
DEFAULT_CALLER_INDEX = BASE / "caller_decompile" / "index.tsv"
DEFAULT_XREF_CONTEXT_INSTRUCTIONS = BASE / "xref_context_instructions.tsv"
DEFAULT_OUT = BASE / "name-confidence-tranche6.json"

RULES = {
    "0x00402dd0": {
        "currentName": "CHeightField_Unk_0047eb80__Wrapper_00402dd0",
        "classification": "shadow-heightfield-corner-test-raw-caller-boundary-deferred",
        "action": "deferRawCallerBoundary",
        "candidateName": "ShadowHeightfield__AnyBoundsCornerAboveSampledHeight",
        "tokens": [
            "CStaticShadows__SampleShadowHeightBilinear",
            "DAT_006fbdfc",
            "return 1",
            "return 0",
        ],
        "expectedXrefFunction": "<no_function>",
        "expectedRefType": "UNCONDITIONAL_CALL",
        "note": "The body is a shadow/heightfield corner test, but its only exported caller sits outside a named function boundary, so owner/name mutation is deferred.",
    },
    "0x0040dda0": {
        "currentName": "CUnitAI_Unk_0044c720__Wrapper_0040dda0",
        "classification": "unitai-grid-cooldown-owner-identity-deferred",
        "action": "deferOwnerIdentity",
        "candidateName": "CUnitAI__RefreshGridCooldownFromOccupiedCells",
        "tokens": [
            "CSquadNormal__GetCellValueAtWorldXY",
            "DAT_008a9d7c",
            "DAT_008a9d80",
            "0x2e8",
        ],
        "expectedXrefFunction": "CExplosionInitThing__RenderObjectiveStatusPanel",
        "expectedRefType": "UNCONDITIONAL_CALL",
        "note": "The grid/cooldown behavior is specific, but the surprising objective-status-panel caller means owner identity still needs a separate boundary/xref pass.",
    },
    "0x00411bf0": {
        "currentName": "CEngine_Unk_0050a080__Wrapper_00411bf0",
        "classification": "mode3-general-volume-burst-dispatch-owner-correction",
        "action": "ownerCorrectionCandidate",
        "candidateName": "CGeneralVolume__DispatchMode3BurstProgressAndSpawn",
        "tokens": [
            "CEngine__CanProceedByTargetRangeGate",
            "CEngine__ClampBurstStartTimeFloorNow",
            "CGeneralVolume__SpawnBurstFromPresetWithFallback",
            "0x588",
        ],
        "expectedXrefFunction": "CGeneralVolume__DispatchModeSpecificReset_13CF0_or_11BF0",
        "expectedRefType": "UNCONDITIONAL_CALL",
        "note": "The caller and callee evidence points at the mode-3 GeneralVolume burst path, not a final CEngine owner.",
    },
    "0x00412240": {
        "currentName": "ROUND__Wrapper_00412240",
        "classification": "mode3-current-entry-rounded-slot-value-rename-candidate",
        "action": "renameCandidate",
        "candidateName": "CGeneralVolume__GetMode3CurrentEntryRoundedSlotValue",
        "tokens": [
            "ROUND",
            "0x55c",
            "0x52c",
            "0xa4",
        ],
        "expectedXrefFunction": "CExplosionInitThing__GetCurrentEntryRoundedSlotValue",
        "expectedRefType": "UNCONDITIONAL_CALL",
        "note": "The mode-3 caller context and slot-value read are stronger than the generic ROUND wrapper name.",
    },
    "0x00412420": {
        "currentName": "CText_GetStringById__Wrapper_00412420",
        "classification": "mode3-current-entry-display-string-rename-candidate",
        "action": "renameCandidate",
        "candidateName": "CGeneralVolume__GetMode3CurrentEntryDisplayString",
        "tokens": [
            "CText__GetStringById",
            "g_Text",
            "0x3c",
            "0xa4",
        ],
        "expectedXrefFunction": "CExplosionInitThing__GetCurrentEntryDisplayString",
        "expectedRefType": "UNCONDITIONAL_CALL",
        "note": "The mode-3 caller context and selected-entry string-id read are stronger than the generic CText wrapper name.",
    },
    "0x00412830": {
        "currentName": "CCockpit_Unk_00411e70__Wrapper_00412830",
        "classification": "cockpit-disable-matching-weapon-raw-caller-boundary-deferred",
        "action": "deferRawCallerBoundary",
        "candidateName": "CCockpit__DisableMatchingWeaponAndReselect",
        "tokens": [
            "CCockpit__CycleToNextUsableWeapon",
            "0x9c",
            "param_1",
            "0xa4",
        ],
        "expectedXrefFunction": "<no_function>",
        "expectedRefType": "UNCONDITIONAL_CALL",
        "note": "The helper behavior is clear, but the xref is a tiny raw/no-function stub that needs boundary work before a saved rename.",
    },
    "0x00413660": {
        "currentName": "CGeneralVolume_Unk_00409e60__Wrapper_00413660",
        "classification": "general-volume-scaled-energy-drain-raw-caller-boundary-deferred",
        "action": "deferRawCallerBoundary",
        "candidateName": "CGeneralVolume__DrainLinkedEnergyScaledByClass",
        "tokens": [
            "CGeneralVolume__ToDoubleIdentity",
            "0x278",
            "0x2c8",
            "0x4b0",
        ],
        "expectedXrefFunction": "<no_function>",
        "expectedRefType": "UNCONDITIONAL_CALL",
        "note": "The scaled drain body is specific, but the xref sits in raw jump-table/case code and needs boundary review before mutation.",
    },
    "0x00418090": {
        "currentName": "FindAnimationIndex__Wrapper_00418090",
        "classification": "opening-animation-callback-table-owner-deferred",
        "action": "deferTableOwner",
        "candidateName": "OpeningAnimationStateCallback__StartOpeningIfPending",
        "tokens": [
            "FindAnimationIndex",
            "s_opening_00623ba4",
            "0x254",
            "0x25c",
        ],
        "expectedXrefFunction": "<no_function>",
        "expectedRefType": "DATA",
        "note": "The state callback behavior is clear, but the only xref is a mixed table/data slot, so table ownership and exact class identity stay deferred.",
    },
}


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
        row["address"] = normalize_address(row.get("address", ""))
        row["comment"] = unescape_tsv(row.get("comment", ""))
    return rows


def read_index(path: Path) -> dict[str, dict[str, str]]:
    rows = read_tsv(path)
    for row in rows:
        row["address"] = normalize_address(row.get("address", ""))
    return {row.get("address", ""): row for row in rows}


def read_xrefs(path: Path) -> list[dict[str, str]]:
    rows = read_tsv(path)
    for row in rows:
        row["target_addr"] = normalize_address(row.get("target_addr", ""))
    return rows


def read_instructions(path: Path) -> list[dict[str, str]]:
    rows = read_tsv(path)
    for row in rows:
        row["target_addr"] = normalize_address(row.get("target_addr", ""))
        row["instruction_addr"] = normalize_address(row.get("instruction_addr", "")) if row.get("instruction_addr", "") not in ("", "<none>") else row.get("instruction_addr", "")
    return rows


def find_decompile_file(decompile_dir: Path, address: str) -> Path | None:
    if not decompile_dir.is_dir():
        return None
    matches = sorted(decompile_dir.glob(f"{normalize_address(address)[2:]}_*.c"))
    return matches[0] if matches else None


def read_text(path: Path | None) -> str:
    if path is None or not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def build_report(
    *,
    metadata_path: Path = DEFAULT_METADATA,
    decompile_index_path: Path = DEFAULT_INDEX,
    decompile_dir: Path = DEFAULT_DECOMPILE_DIR,
    xrefs_path: Path = DEFAULT_XREFS,
    instructions_path: Path = DEFAULT_INSTRUCTIONS,
    caller_index_path: Path = DEFAULT_CALLER_INDEX,
    xref_context_instructions_path: Path = DEFAULT_XREF_CONTEXT_INSTRUCTIONS,
) -> dict[str, object]:
    metadata_path = resolve(metadata_path)
    decompile_index_path = resolve(decompile_index_path)
    decompile_dir = resolve(decompile_dir)
    xrefs_path = resolve(xrefs_path)
    instructions_path = resolve(instructions_path)
    caller_index_path = resolve(caller_index_path)
    xref_context_instructions_path = resolve(xref_context_instructions_path)

    failures: list[str] = []
    for label, path in (
        ("metadata export", metadata_path),
        ("decompile index", decompile_index_path),
        ("decompile dir", decompile_dir),
        ("xref export", xrefs_path),
        ("instruction export", instructions_path),
        ("caller decompile index", caller_index_path),
        ("xref-context instruction export", xref_context_instructions_path),
    ):
        if label == "decompile dir":
            if not path.is_dir():
                failures.append(f"missing {label}: {relative(path)}")
        elif not path.is_file():
            failures.append(f"missing {label}: {relative(path)}")

    metadata = read_metadata(metadata_path)
    index = read_index(decompile_index_path)
    caller_index = read_index(caller_index_path)
    xrefs = read_xrefs(xrefs_path)
    instructions = read_instructions(instructions_path)
    xref_context_instructions = read_instructions(xref_context_instructions_path)

    xrefs_by_target: dict[str, list[dict[str, str]]] = defaultdict(list)
    instructions_by_target: dict[str, list[dict[str, str]]] = defaultdict(list)
    xref_context_by_target: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in xrefs:
        xrefs_by_target[row["target_addr"]].append(row)
    for row in instructions:
        instructions_by_target[row["target_addr"]].append(row)
    for row in xref_context_instructions:
        xref_context_by_target[row["target_addr"]].append(row)

    targets: list[dict[str, object]] = []
    action_counts: Counter[str] = Counter()
    classification_counts: Counter[str] = Counter()
    seen = set()

    for row in metadata:
        address = row["address"]
        seen.add(address)
        rule = RULES.get(address)
        if rule is None:
            failures.append(f"{address} has no tranche classification rule")
            continue

        name = row.get("name", "")
        signature = row.get("signature", "")
        comment = row.get("comment", "")
        if row.get("status") != "OK":
            failures.append(f"{address} metadata status is not OK")
        if name != rule["currentName"]:
            failures.append(f"{address} expected current name {rule['currentName']}, found {name}")
        if not comment:
            failures.append(f"{address} missing metadata comment")

        index_row = index.get(address)
        if index_row is None or index_row.get("status") != "OK":
            failures.append(f"{address} missing OK decompile index row")
        elif index_row.get("name", "") != name:
            failures.append(f"{address} metadata/index name mismatch: {name} != {index_row.get('name', '')}")

        decompile_file = find_decompile_file(decompile_dir, address)
        decompile_text = read_text(decompile_file)
        if not decompile_text:
            failures.append(f"{address} missing decompile file")
        missing_tokens = [token for token in rule["tokens"] if token not in decompile_text]
        if missing_tokens:
            failures.append(f"{address} missing expected decompile tokens: {', '.join(missing_tokens)}")

        target_xrefs = xrefs_by_target[address]
        if not target_xrefs:
            failures.append(f"{address} missing xref rows")
        expected_function = str(rule.get("expectedXrefFunction", ""))
        expected_ref_type = str(rule.get("expectedRefType", ""))
        if expected_function:
            observed_functions = {xref.get("from_function", "") for xref in target_xrefs}
            if expected_function not in observed_functions:
                failures.append(f"{address} missing expected xref function: {expected_function}")
        if expected_ref_type:
            observed_ref_types = {xref.get("ref_type", "") for xref in target_xrefs}
            if expected_ref_type not in observed_ref_types:
                failures.append(f"{address} missing expected xref ref_type: {expected_ref_type}")

        instruction_rows = instructions_by_target[address]
        if not instruction_rows:
            failures.append(f"{address} missing target instruction rows")

        if rule["action"] == "deferRawCallerBoundary":
            raw_context = [row for row in target_xrefs if row.get("from_function", "") == "<no_function>"]
            if not raw_context:
                failures.append(f"{address} expected at least one raw/no-function xref")
        if rule["action"] == "deferTableOwner":
            data_context = [row for row in target_xrefs if row.get("ref_type", "") == "DATA"]
            if not data_context:
                failures.append(f"{address} expected at least one DATA xref")

        action = str(rule["action"])
        classification = str(rule["classification"])
        action_counts[action] += 1
        classification_counts[classification] += 1
        targets.append(
            {
                "address": address,
                "currentName": name,
                "signature": signature,
                "classification": classification,
                "suggestedAction": action,
                "candidateName": rule["candidateName"],
                "xrefRows": len(target_xrefs),
                "instructionRows": len(instruction_rows),
                "xrefContextRows": sum(len(xref_context_by_target[normalize_address(xref.get("from_addr", ""))]) for xref in target_xrefs),
                "expectedXrefFunction": expected_function,
                "expectedRefType": expected_ref_type,
                "note": rule["note"],
                "missingTokens": missing_tokens,
                "decompile": relative(decompile_file),
            }
        )

    for address in RULES:
        if address not in seen:
            failures.append(f"{address} missing from metadata export")

    extra_addresses = sorted(seen - set(RULES))
    if extra_addresses:
        failures.append(f"metadata export has unexpected addresses: {', '.join(extra_addresses)}")
    if not metadata:
        failures.append("metadata export contained no rows")
    if caller_index and len(caller_index) < 4:
        failures.append(f"caller decompile index expected at least 4 rows, found {len(caller_index)}")

    status = "PASS" if not failures else "FAIL"
    return {
        "schema": "ghidra-name-confidence-tranche6.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "inputs": {
            "metadata": relative(metadata_path),
            "decompileIndex": relative(decompile_index_path),
            "decompileDir": relative(decompile_dir),
            "xrefs": relative(xrefs_path),
            "instructions": relative(instructions_path),
            "callerDecompileIndex": relative(caller_index_path),
            "xrefContextInstructions": relative(xref_context_instructions_path),
        },
        "targetCount": len(metadata),
        "xrefRows": len(xrefs),
        "instructionRows": len(instructions),
        "xrefContextInstructionRows": len(xref_context_instructions),
        "actionCounts": dict(action_counts),
        "classificationCounts": dict(classification_counts),
        "targets": targets,
        "failures": failures,
        "whatIsProven": [
            "The sixth name-confidence queue tranche has read-only metadata, decompile, xref, instruction, caller, and raw callsite/table context for the eight remaining queued targets.",
            "Two targets have stronger rename-candidate evidence, one has owner-correction-candidate evidence, and five remain deferred behind caller-boundary, owner-identity, or table-owner uncertainty.",
            "The tranche narrows the next mutation plan without exposing raw decompile text publicly.",
        ],
        "notProven": [
            "This does not mutate Ghidra names, signatures, comments, tags, or function boundaries.",
            "This does not prove the candidate names, owners, tags, signatures, or function boundaries are final.",
            "This does not prove exact source-to-retail identity or runtime behavior.",
        ],
        "privacy": "Report stores repo-relative artifact paths, public addresses, function names, counts, classifications, caller names, candidate labels, and proof boundaries only; raw decompiles, instructions, and xrefs remain ignored under subagents/.",
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--decompile-index", type=Path, default=DEFAULT_INDEX)
    parser.add_argument("--decompile-dir", type=Path, default=DEFAULT_DECOMPILE_DIR)
    parser.add_argument("--xrefs", type=Path, default=DEFAULT_XREFS)
    parser.add_argument("--instructions", type=Path, default=DEFAULT_INSTRUCTIONS)
    parser.add_argument("--caller-index", type=Path, default=DEFAULT_CALLER_INDEX)
    parser.add_argument("--xref-context-instructions", type=Path, default=DEFAULT_XREF_CONTEXT_INSTRUCTIONS)
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
        metadata_path=args.metadata,
        decompile_index_path=args.decompile_index,
        decompile_dir=args.decompile_dir,
        xrefs_path=args.xrefs,
        instructions_path=args.instructions,
        caller_index_path=args.caller_index,
        xref_context_instructions_path=args.xref_context_instructions,
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("Ghidra name-confidence tranche 6 probe")
        print(f"Status: {report['status']}")
        print(f"Output: {relative(out)}")
        print(f"Targets: {report['targetCount']}")
        print(f"Xref rows: {report['xrefRows']}")
        print(f"Instruction rows: {report['instructionRows']}")
        print(f"Action counts: {report['actionCounts']}")
        print(f"Classification counts: {report['classificationCounts']}")
        for failure in report["failures"]:
            print(f"- {failure}")

    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
