#!/usr/bin/env python3
"""Validate saved Ghidra corrections for the fourth name-confidence tranche."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "name-confidence-tranche4-correction" / "current"
QUEUE = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
DEFAULT_METADATA = BASE / "metadata_readback.tsv"
DEFAULT_INDEX = BASE / "decompile_readback" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_readback"
DEFAULT_XREFS = BASE / "xrefs_readback.tsv"
DEFAULT_QUEUE = QUEUE
DEFAULT_OUT = BASE / "name-confidence-tranche4-correction.json"

RULES = {
    "0x00403ff0": {
        "oldName": "CFastVB_Unk_0055db0a__Wrapper_00403ff0",
        "newName": "CDXLandscape__DestroyResourceDescriptorArray_Thunk",
        "tokens": ["CDXLandscape__DestroyArrayWithCallback", "CResourceDescriptor__dtor", "0x41c"],
        "commentTokens": ["Proof-boundary", "destructor/unwind", "runtime behavior"],
        "expectedXrefFunctions": ["Unwind@005d0fb0"],
        "scope": "Resource-descriptor array destroy thunk.",
    },
    "0x0040dcc0": {
        "oldName": "CGeneralVolume_Unk_0040a580__Wrapper_0040dcc0",
        "newName": "CMonitor__ResetTransitionFlagAndUpdateIfState3_Thunk",
        "tokens": ["0x58c", "0x260", "CMonitor__UpdateFlightWalkerTransitionState"],
        "commentTokens": ["Proof-boundary", "owner/source identity", "runtime behavior"],
        "scope": "Monitor transition-state flag reset and conditional update thunk.",
    },
    "0x00410670": {
        "oldName": "CGeneralVolume_Unk_00409e60__Wrapper_00410670",
        "newName": "CGeneralVolume__DrainLinkedObjectFromVelocity",
        "tokens": ["CGeneralVolume__ToDoubleIdentity", "0x280", "0x588", "0x520"],
        "commentTokens": ["Proof-boundary", "energy/drain semantics", "runtime behavior"],
        "scope": "General-volume linked-object velocity-scaled drain/update body.",
    },
    "0x00411b90": {
        "oldName": "CEngine_Unk_00506010__Wrapper_00411b90",
        "newName": "CGeneralVolume__DispatchSelectedBurstPreset",
        "tokens": ["CGeneralVolume__SpawnBurstFromPresetWithFallback", "0x588", "0x9c"],
        "commentTokens": ["Proof-boundary", "does not prove", "weapon-fired stealth reset"],
        "expectedXrefFunctions": ["CGeneralVolume__Reset588AndDispatchModeSpecific_13CC0_or_11B90"],
        "scope": "General-volume selected burst-preset dispatch body.",
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

        expected_functions = set(rule.get("expectedXrefFunctions", []))
        if expected_functions:
            observed = {xref.get("from_function", "") for xref in xrefs_by_target[address]}
            missing = sorted(expected_functions - observed)
            if missing:
                failures.append(f"{address} missing expected xref context: {', '.join(missing)}")

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
    if quality.get("uncertainOwnerNameCount") != 5:
        failures.append(f"expected uncertain owner count 5, found {quality.get('uncertainOwnerNameCount')}")
    if quality.get("wrapperAddressNameCount") != 12:
        failures.append(f"expected wrapper address count 12, found {quality.get('wrapperAddressNameCount')}")

    status = "PASS" if not failures else "FAIL"
    return {
        "schema": "ghidra-name-confidence-tranche4-correction.v1",
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
        "queue": queue,
        "failures": failures,
        "whatIsProven": [
            "The four tranche-4 correction targets have saved behavior-backed names and proof-boundary comments in the Ghidra project.",
            "Read-back metadata, decompile, and xref exports still contain the context used for the saved corrections.",
            "The refreshed static re-audit queue now reports fewer uncertain-owner and address-suffixed wrapper names.",
        ],
        "notProven": [
            "This does not harden signatures, parameter names, local names, structures, or tags.",
            "This does not prove exact source-to-retail identity or runtime behavior.",
            "This does not close weapon-fired stealth reset identity or runtime cloak/fire behavior.",
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
        print("Ghidra name-confidence tranche 4 correction probe")
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
