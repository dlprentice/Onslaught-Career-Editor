#!/usr/bin/env python3
"""Validate saved Ghidra corrections for the fifth name-confidence tranche."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "name-confidence-tranche5-correction" / "current"
QUEUE = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
DEFAULT_METADATA = BASE / "metadata_readback.tsv"
DEFAULT_INDEX = BASE / "decompile_readback" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_readback"
DEFAULT_XREFS = BASE / "xrefs_readback.tsv"
DEFAULT_QUEUE = QUEUE
DEFAULT_OUT = BASE / "name-confidence-tranche5-correction.json"

EXPECTED_QUEUE_SIGNALS = {
    "commentlessFunctionCount": 5495,
    "undefinedSignatureCount": 2087,
    "paramSignatureCount": 2563,
    "uncertainOwnerNameCount": 5,
    "helperAddressNameCount": 0,
    "wrapperAddressNameCount": 8,
}

REMAINING_NAME_CONFIDENCE_ADDRESSES = {
    "0x00402dd0",
    "0x0040dda0",
    "0x00411bf0",
    "0x00412240",
    "0x00412420",
    "0x00412830",
    "0x00413660",
    "0x00418090",
}

RULES = {
    "0x00412650": {
        "oldName": "CSPtrSet_Remove__Wrapper_00412650",
        "newName": "CBattleEngineJetPart__ResetConfiguration",
        "tokens": ["CSPtrSet__Remove", "CWorldPhysicsManager__CreateWeaponByIndex", "0x50", "CSPtrSet__AddToTail"],
        "commentTokens": ["Proof-boundary", "source/decompile/xref backed", "runtime behavior"],
        "expectedXrefFunctions": ["CBattleEngine__ApplyWeaponProfileByIndex", "CBattleEngine__InitTargetSetBucketState"],
        "scope": "Source-aligned CBattleEngineJetPart::ResetConfiguration candidate.",
    },
    "0x00412ad0": {
        "oldName": "ABS__Wrapper_00412ad0",
        "newName": "CMonitor__UpdateSurfaceAlignmentAngle",
        "tokens": ["ABS", "0x24", "_DAT_005d85e0", "0x6c"],
        "commentTokens": ["Proof-boundary", "exact source method identity", "runtime behavior"],
        "expectedXrefFunctions": ["CMonitor__ProcessTrackingAndSurfaceAlignment"],
        "scope": "Monitor surface-alignment angle update helper.",
    },
    "0x004146b0": {
        "oldName": "CSPtrSet_Remove__Wrapper_004146b0",
        "newName": "CBattleEngineWalkerPart__ResetConfiguration",
        "tokens": ["CSPtrSet__Remove", "CWorldPhysicsManager__CreateWeaponByIndex", "0x40", "0x60"],
        "commentTokens": ["Proof-boundary", "source/decompile/xref backed", "runtime behavior"],
        "expectedXrefFunctions": ["CBattleEngine__ApplyWeaponProfileByIndex", "CBattleEngine__InitDashMoveParams"],
        "scope": "Source-aligned CBattleEngineWalkerPart::ResetConfiguration candidate.",
    },
    "0x004d3080": {
        "oldName": "CGenericActiveReader_SetReader__Wrapper_004d3080",
        "newName": "CPlayer__AssignBattleEngine",
        "tokens": ["CGenericActiveReader__SetReader", "0x574", "0x154", "0xe0"],
        "commentTokens": ["Proof-boundary", "source parity", "runtime behavior"],
        "expectedXrefFunctions": ["CGame__PostLoadProcess", "CGame__RespawnPlayer"],
        "scope": "Source-aligned CPlayer::AssignBattleEngine candidate.",
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


def find_decompile_file(decompile_dir: Path, address: str) -> Path | None:
    if not decompile_dir.is_dir():
        return None
    matches = sorted(decompile_dir.glob(f"{normalize_address(address)[2:]}_*.c"))
    return matches[0] if matches else None


def read_text(path: Path | None) -> str:
    if path is None or not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def read_queue(path: Path) -> dict[str, object]:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_report(
    *,
    metadata_path: Path = DEFAULT_METADATA,
    decompile_index_path: Path = DEFAULT_INDEX,
    decompile_dir: Path = DEFAULT_DECOMPILE_DIR,
    xrefs_path: Path = DEFAULT_XREFS,
    queue_path: Path = DEFAULT_QUEUE,
) -> dict[str, object]:
    metadata_path = resolve(metadata_path)
    decompile_index_path = resolve(decompile_index_path)
    decompile_dir = resolve(decompile_dir)
    xrefs_path = resolve(xrefs_path)
    queue_path = resolve(queue_path)

    failures: list[str] = []
    for label, path in (
        ("metadata read-back", metadata_path),
        ("decompile index", decompile_index_path),
        ("decompile dir", decompile_dir),
        ("xref read-back", xrefs_path),
        ("queue report", queue_path),
    ):
        if label == "decompile dir":
            if not path.is_dir():
                failures.append(f"missing {label}: {relative(path)}")
        elif not path.is_file():
            failures.append(f"missing {label}: {relative(path)}")

    metadata = read_metadata(metadata_path)
    index = read_index(decompile_index_path)
    xrefs = read_xrefs(xrefs_path)
    queue = read_queue(queue_path)
    xrefs_by_target: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in xrefs:
        xrefs_by_target[row["target_addr"]].append(row)

    targets: list[dict[str, object]] = []
    seen = set()
    for row in metadata:
        address = row["address"]
        seen.add(address)
        rule = RULES.get(address)
        if rule is None:
            failures.append(f"{address} has no correction rule")
            continue

        name = row.get("name", "")
        comment = row.get("comment", "")
        if row.get("status") != "OK":
            failures.append(f"{address} metadata status is not OK")
        if name != rule["newName"]:
            failures.append(f"{address} expected saved name {rule['newName']}, found {name}")

        index_row = index.get(address)
        if index_row is None or index_row.get("status") != "OK":
            failures.append(f"{address} missing OK decompile index row")
        elif index_row.get("name", "") != name:
            failures.append(f"{address} metadata/index name mismatch: {name} != {index_row.get('name', '')}")

        decompile_file = find_decompile_file(decompile_dir, address)
        decompile_text = read_text(decompile_file)
        missing_tokens = [token for token in rule["tokens"] if token not in decompile_text]
        if missing_tokens:
            failures.append(f"{address} missing expected decompile tokens: {', '.join(missing_tokens)}")

        missing_comment_tokens = [token for token in rule["commentTokens"] if token not in comment]
        if missing_comment_tokens:
            failures.append(f"{address} missing proof-boundary comment tokens: {', '.join(missing_comment_tokens)}")

        observed_xref_functions = {xref.get("from_function", "") for xref in xrefs_by_target[address]}
        missing_xref_functions = sorted(set(rule["expectedXrefFunctions"]) - observed_xref_functions)
        if missing_xref_functions:
            failures.append(f"{address} missing expected xref context: {', '.join(missing_xref_functions)}")

        targets.append(
            {
                "address": address,
                "oldName": rule["oldName"],
                "savedName": name,
                "signature": row.get("signature", ""),
                "scope": rule["scope"],
                "xrefRows": len(xrefs_by_target[address]),
                "decompile": relative(decompile_file),
                "missingTokens": missing_tokens,
                "missingCommentTokens": missing_comment_tokens,
            }
        )

    for address in RULES:
        if address not in seen:
            failures.append(f"{address} missing from metadata read-back")

    quality = queue.get("qualitySignals", {}) if isinstance(queue, dict) else {}
    if queue.get("status") != "PASS":
        failures.append("queue report did not pass")
    for key, expected in EXPECTED_QUEUE_SIGNALS.items():
        observed = quality.get(key)
        if observed != expected:
            failures.append(f"expected queue {key} {expected}, found {observed}")

    name_confidence = queue.get("priorityQueues", {}).get("nameConfidence", []) if isinstance(queue, dict) else []
    queued_addresses = {normalize_address(str(row.get("address", ""))) for row in name_confidence if isinstance(row, dict)}
    corrected_still_queued = sorted(set(RULES) & queued_addresses)
    if corrected_still_queued:
        failures.append(f"corrected addresses still appear in name-confidence queue: {', '.join(corrected_still_queued)}")
    missing_remaining = sorted(REMAINING_NAME_CONFIDENCE_ADDRESSES - queued_addresses)
    if missing_remaining:
        failures.append(f"remaining name-confidence queue missing expected deferred addresses: {', '.join(missing_remaining)}")

    status = "PASS" if not failures else "FAIL"
    return {
        "schema": "ghidra-name-confidence-tranche5-correction.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "inputs": {
            "metadata": relative(metadata_path),
            "decompileIndex": relative(decompile_index_path),
            "decompileDir": relative(decompile_dir),
            "xrefs": relative(xrefs_path),
            "queue": relative(queue_path),
        },
        "targetCount": len(metadata),
        "xrefRows": len(xrefs),
        "targets": targets,
        "remainingNameConfidenceQueue": sorted(queued_addresses),
        "queue": queue,
        "failures": failures,
        "whatIsProven": [
            "The four tranche-5 correction targets have saved source/decompile/xref-backed names and proof-boundary comments in the Ghidra project.",
            "Read-back metadata, decompile, and xref exports still contain the context used for the saved corrections.",
            "The refreshed static re-audit queue now reports eight remaining address-suffixed wrapper names.",
        ],
        "notProven": [
            "This does not harden signatures, parameter names, local names, structures, or tags.",
            "This does not prove every remaining wrapper or uncertain-owner name is wrong or right.",
            "This does not prove runtime behavior, exhaustive source identity, or rebuild parity.",
        ],
        "privacy": "Report stores repo-relative artifact paths, public addresses, names, counts, and proof boundaries only; raw decompiles, instructions, and xrefs remain ignored under subagents/.",
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--decompile-index", type=Path, default=DEFAULT_INDEX)
    parser.add_argument("--decompile-dir", type=Path, default=DEFAULT_DECOMPILE_DIR)
    parser.add_argument("--xrefs", type=Path, default=DEFAULT_XREFS)
    parser.add_argument("--queue", type=Path, default=DEFAULT_QUEUE)
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
        queue_path=args.queue,
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        queue = report.get("queue", {})
        quality = queue.get("qualitySignals", {}) if isinstance(queue, dict) else {}
        print("Ghidra name-confidence tranche 5 correction probe")
        print(f"Status: {report['status']}")
        print(f"Output: {relative(out)}")
        print(f"Targets: {report['targetCount']}")
        print(f"Xref rows: {report['xrefRows']}")
        print(f"Uncertain owners: {quality.get('uncertainOwnerNameCount')}")
        print(f"Address-suffixed wrappers: {quality.get('wrapperAddressNameCount')}")
        for failure in report["failures"]:
            print(f"- {failure}")

    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
