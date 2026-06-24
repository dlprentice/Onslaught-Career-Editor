#!/usr/bin/env python3
"""Classify the fourth read-only Ghidra name-confidence re-audit tranche."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "name-confidence-tranche4" / "current"
DEFAULT_METADATA = BASE / "metadata.tsv"
DEFAULT_INDEX = BASE / "decompile" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile"
DEFAULT_XREFS = BASE / "xrefs.tsv"
DEFAULT_INSTRUCTIONS = BASE / "instructions.tsv"
DEFAULT_OUT = BASE / "name-confidence-tranche4.json"

RULES = {
    "0x00402dd0": {
        "classification": "shadow-heightfield-corner-test-owner-deferred",
        "action": "deferOwnerIdentity",
        "candidateName": "ShadowHeightfield__AnyBoundsCornerAboveSampledHeight",
        "tokens": [
            "CStaticShadows__SampleShadowHeightBilinear",
            "DAT_006fbdfc",
            "return 1",
            "return 0",
        ],
        "commentTokens": ["Proof-boundary", "owner", "not runtime shadow behavior proof"],
        "expectedXrefRows": 1,
        "note": "The body tests object bounds corners against sampled/static shadow height, but the caller is outside a named function, so owner identity stays deferred.",
    },
    "0x00403ff0": {
        "classification": "resource-descriptor-array-destroy-wrapper",
        "action": "renameCandidate",
        "candidateName": "CDXLandscape__DestroyResourceDescriptorArray_Thunk",
        "tokens": [
            "CDXLandscape__DestroyArrayWithCallback",
            "CResourceDescriptor__dtor",
            "0x41c",
        ],
        "commentTokens": ["Proof-boundary", "destructor/unwind"],
        "expectedXrefRows": 2,
        "expectedXrefFunctions": ["Unwind@005d0fb0"],
        "note": "The current CFastVB/_Unk owner is weaker than the destroy-array helper and resource-descriptor destructor evidence.",
    },
    "0x0040dcc0": {
        "classification": "monitor-transition-state-wrapper",
        "action": "renameCandidate",
        "candidateName": "CMonitor__ResetTransitionFlagAndUpdateIfState3_Thunk",
        "tokens": [
            "0x58c",
            "0x260",
            "CMonitor__UpdateFlightWalkerTransitionState",
        ],
        "commentTokens": ["Proof-boundary", "exact source method identity"],
        "expectedXrefRows": 1,
        "note": "The body clears the transition flag and dispatches to the named CMonitor transition helper when state equals 3; source identity remains separate.",
    },
    "0x0040dda0": {
        "classification": "unitai-grid-cooldown-stamp-owner-deferred",
        "action": "deferCallerOwnerReview",
        "candidateName": "CUnitAI__RefreshGridCooldownFromOccupiedCells",
        "tokens": [
            "CSquadNormal__GetCellValueAtWorldXY",
            "0x2e8",
            "DAT_008a9d7c",
            "DAT_008a9d80",
        ],
        "commentTokens": ["Proof-boundary", "exact owner identity"],
        "expectedXrefFunctions": ["CExplosionInitThing__RenderObjectiveStatusPanel"],
        "note": "The CUnitAI-like body is clear, but the surprising current caller context means owner/function-boundary review should precede a rename.",
    },
    "0x00410670": {
        "classification": "general-volume-linked-object-drain-wrapper",
        "action": "renameCandidate",
        "candidateName": "CGeneralVolume__DrainLinkedObjectFromVelocity",
        "tokens": [
            "CGeneralVolume__ToDoubleIdentity",
            "0x280",
            "0x588",
            "0x520",
        ],
        "commentTokens": ["Proof-boundary", "source/runtime proof"],
        "expectedXrefRows": 1,
        "note": "The linked-object vector/scale/drain behavior is specific enough for a conservative future rename, while exact energy semantics stay unproven.",
    },
    "0x00411b90": {
        "classification": "general-volume-burst-list-dispatch-owner-correction",
        "action": "ownerCorrectionCandidate",
        "candidateName": "CGeneralVolume__DispatchSelectedBurstPreset_Thunk",
        "tokens": [
            "CGeneralVolume__SpawnBurstFromPresetWithFallback",
            "0x588",
            "0x9c",
        ],
        "commentTokens": ["Proof-boundary", "does not prove", "stealth reset"],
        "expectedXrefFunctions": ["CGeneralVolume__Reset588AndDispatchModeSpecific_13CC0_or_11B90"],
        "note": "The caller/callee context points at CGeneralVolume burst dispatch, not CEngine or weapon-fire stealth reset identity.",
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
    return rows


def find_decompile_file(decompile_dir: Path, address: str) -> Path | None:
    if not decompile_dir.is_dir():
        return None
    needle = normalize_address(address)[2:]
    matches = sorted(decompile_dir.glob(f"{needle}_*.c"))
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
) -> dict[str, object]:
    metadata_path = resolve(metadata_path)
    decompile_index_path = resolve(decompile_index_path)
    decompile_dir = resolve(decompile_dir)
    xrefs_path = resolve(xrefs_path)
    instructions_path = resolve(instructions_path)

    failures: list[str] = []
    for label, path in (
        ("metadata export", metadata_path),
        ("decompile index", decompile_index_path),
        ("decompile dir", decompile_dir),
        ("xref export", xrefs_path),
        ("instruction export", instructions_path),
    ):
        if label == "decompile dir":
            if not path.is_dir():
                failures.append(f"missing {label}: {relative(path)}")
        elif not path.is_file():
            failures.append(f"missing {label}: {relative(path)}")

    metadata_rows = read_metadata(metadata_path)
    index = read_index(decompile_index_path)
    xrefs = read_xrefs(xrefs_path)
    instructions = read_instructions(instructions_path)

    xrefs_by_target: dict[str, list[dict[str, str]]] = defaultdict(list)
    instructions_by_target: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in xrefs:
        xrefs_by_target[row["target_addr"]].append(row)
    for row in instructions:
        instructions_by_target[row["target_addr"]].append(row)

    targets: list[dict[str, object]] = []
    action_counts: Counter[str] = Counter()
    classification_counts: Counter[str] = Counter()

    for row in metadata_rows:
        address = row["address"]
        rule = RULES.get(address)
        if rule is None:
            failures.append(f"{address} has no tranche classification rule")
            continue

        name = row.get("name", "")
        signature = row.get("signature", "")
        comment = row.get("comment", "")
        if row.get("status") != "OK":
            failures.append(f"{address} metadata status is not OK")
        if "Unk" not in name and "Wrapper_" not in name:
            failures.append(f"{address} no longer looks like name-confidence debt: {name}")

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

        missing_comment_tokens = [token for token in rule["commentTokens"] if token not in comment]
        if missing_comment_tokens:
            failures.append(f"{address} missing proof-boundary comment tokens: {', '.join(missing_comment_tokens)}")

        target_xrefs = xrefs_by_target[address]
        expected_rows = int(rule.get("expectedXrefRows", 0))
        if expected_rows and len(target_xrefs) < expected_rows:
            failures.append(f"{address} expected xref rows >= {expected_rows}, found {len(target_xrefs)}")
        expected_functions = set(rule.get("expectedXrefFunctions", []))
        if expected_functions:
            observed = {xref.get("from_function", "") for xref in target_xrefs}
            missing = sorted(expected_functions - observed)
            if missing:
                failures.append(f"{address} missing expected xref context: {', '.join(missing)}")

        action = str(rule["action"])
        classification = str(rule["classification"])
        action_counts[action] += 1
        classification_counts[classification] += 1
        targets.append(
            {
                "address": address,
                "name": name,
                "signature": signature,
                "classification": classification,
                "suggestedAction": action,
                "candidateName": rule["candidateName"],
                "xrefRows": len(target_xrefs),
                "instructionRows": len(instructions_by_target[address]),
                "expectedXrefFunctions": sorted(expected_functions),
                "note": rule["note"],
                "missingTokens": missing_tokens,
                "missingCommentTokens": missing_comment_tokens,
                "decompile": relative(decompile_file),
            }
        )

    if not metadata_rows:
        failures.append("metadata export contained no rows")

    status = "PASS" if not failures else "FAIL"
    return {
        "schema": "ghidra-name-confidence-tranche4.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "inputs": {
            "metadata": relative(metadata_path),
            "decompileIndex": relative(decompile_index_path),
            "decompileDir": relative(decompile_dir),
            "xrefs": relative(xrefs_path),
            "instructions": relative(instructions_path),
        },
        "targetCount": len(metadata_rows),
        "xrefRows": len(xrefs),
        "instructionRows": len(instructions),
        "actionCounts": dict(action_counts),
        "classificationCounts": dict(classification_counts),
        "targets": targets,
        "failures": failures,
        "whatIsProven": [
            "The fourth name-confidence queue tranche has read-only metadata, decompile, xref, and instruction context for each selected target.",
            "Each selected target still carries proof-boundary comments and has a public-safe classification with a next suggested action.",
            "The tranche narrows several old _Unk/Wrapper names into candidate rename or owner-review buckets without exposing raw decompile text publicly.",
        ],
        "notProven": [
            "This does not mutate Ghidra names, signatures, comments, tags, or function boundaries.",
            "This does not prove the candidate names, owners, or signatures are final.",
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
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("Ghidra name-confidence tranche 4 probe")
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
