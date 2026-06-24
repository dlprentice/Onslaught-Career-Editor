#!/usr/bin/env python3
"""Validate the saved Ghidra correction for a name-confidence deferral slice."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "name-confidence-deferrals" / "current"
QUEUE = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

DEFAULT_METADATA = BASE / "metadata_readback.tsv"
DEFAULT_INDEX = BASE / "decompile_readback" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_readback"
DEFAULT_XREFS = BASE / "xrefs_readback.tsv"
DEFAULT_INSTRUCTIONS = BASE / "instructions_readback.tsv"
DEFAULT_CREATE_DRY = BASE / "create_function_dry.tsv"
DEFAULT_CREATE_APPLY = BASE / "create_function_apply.tsv"
DEFAULT_QUEUE = QUEUE
DEFAULT_OUT = BASE / "name-confidence-deferral-correction.json"

CREATED_FUNCTIONS = {"0x0040dc30", "0x0040dc60"}
RENAMED_FUNCTIONS = {"0x00412830"}
REMAINING_NAME_CONFIDENCE_ADDRESSES = {
    "0x00402dd0",
    "0x0040dda0",
    "0x00413660",
    "0x00418090",
}

EXPECTED_QUEUE_SIGNALS = {
    "commentlessFunctionCount": 5495,
    "undefinedSignatureCount": 2089,
    "paramSignatureCount": 2563,
    "uncertainOwnerNameCount": 3,
    "helperAddressNameCount": 0,
    "wrapperAddressNameCount": 4,
}

RULES = {
    "0x0040dc30": {
        "oldName": "<no_function>",
        "newName": "CExplosionInitThing__EnableVolumeEntryGroupsByName",
        "classification": "raw-boundary-created-enable-volume-groups",
        "tokens": [
            "CExplosionInitThing__EnableVolumeEntryGroupsByName",
            "CGeneralVolume__EnableEntriesByName",
            "CGeneralVolume__EnableLinkedEntriesByName",
            "0x578",
            "0x57c",
        ],
        "commentTokens": ["Proof-boundary", "signature/types", "runtime behavior"],
        "expectedXrefs": [
            {
                "from_addr": "005d8b5c",
                "from_function_addr": "<none>",
                "from_function": "<no_function>",
                "ref_type": "DATA",
            }
        ],
        "scope": "Recovered raw dispatch stub for enabling both GeneralVolume entry groups by name.",
    },
    "0x0040dc60": {
        "oldName": "<no_function>",
        "newName": "CExplosionInitThing__DisableVolumeEntryGroupsByNameAndReselect",
        "classification": "raw-boundary-created-disable-volume-groups",
        "tokens": [
            "CExplosionInitThing__DisableVolumeEntryGroupsByNameAndReselect",
            "CGeneralVolume__DisableEntriesByNameAndReselect",
            "CGeneralVolume__DisableLinkedEntriesByNameAndReselect",
            "0x578",
            "0x57c",
        ],
        "commentTokens": ["Proof-boundary", "signature/types", "runtime behavior"],
        "expectedXrefs": [
            {
                "from_addr": "005d8b60",
                "from_function_addr": "<none>",
                "from_function": "<no_function>",
                "ref_type": "DATA",
            }
        ],
        "scope": "Recovered raw dispatch stub for disabling both GeneralVolume entry groups by name.",
    },
    "0x00412830": {
        "oldName": "CCockpit_Unk_00411e70__Wrapper_00412830",
        "newName": "CGeneralVolume__DisableLinkedEntriesByNameAndReselect",
        "classification": "stale-owner-corrected-general-volume-linked-disable",
        "tokens": [
            "CGeneralVolume__DisableLinkedEntriesByNameAndReselect",
            "0x9c",
            "0xa4",
        ],
        "commentTokens": ["Corrected from the stale CCockpit", "Proof-boundary", "runtime behavior"],
        "expectedXrefs": [
            {
                "from_addr": "0040dc7b",
                "from_function_addr": "0040dc60",
                "from_function": "CExplosionInitThing__DisableVolumeEntryGroupsByNameAndReselect",
                "ref_type": "UNCONDITIONAL_CALL",
            }
        ],
        "scope": "Corrected stale CCockpit wrapper label to the linked GeneralVolume disable/reselect helper.",
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
    if not value or value in {"<none>", "<no_function>"}:
        return value
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
    return {row["address"]: row for row in rows if row.get("address")}


def read_xrefs(path: Path) -> list[dict[str, str]]:
    rows = read_tsv(path)
    for row in rows:
        row["target_addr"] = normalize_address(row.get("target_addr", ""))
        row["from_addr_norm"] = normalize_address(row.get("from_addr", ""))
        row["from_function_addr_norm"] = normalize_address(row.get("from_function_addr", ""))
    return rows


def read_instructions(path: Path) -> list[dict[str, str]]:
    rows = read_tsv(path)
    for row in rows:
        row["target_addr"] = normalize_address(row.get("target_addr", ""))
        row["function_entry_norm"] = normalize_address(row.get("function_entry", ""))
    return rows


def read_create_rows(path: Path) -> dict[str, dict[str, str]]:
    rows = read_tsv(path)
    for row in rows:
        row["address"] = normalize_address(row.get("address", ""))
    return {row["address"]: row for row in rows if row.get("address")}


def read_queue(path: Path) -> dict[str, object]:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


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
    create_dry_path: Path = DEFAULT_CREATE_DRY,
    create_apply_path: Path = DEFAULT_CREATE_APPLY,
    queue_path: Path = DEFAULT_QUEUE,
) -> dict[str, object]:
    metadata_path = resolve(metadata_path)
    decompile_index_path = resolve(decompile_index_path)
    decompile_dir = resolve(decompile_dir)
    xrefs_path = resolve(xrefs_path)
    instructions_path = resolve(instructions_path)
    create_dry_path = resolve(create_dry_path)
    create_apply_path = resolve(create_apply_path)
    queue_path = resolve(queue_path)

    failures: list[str] = []
    for label, path in (
        ("metadata read-back", metadata_path),
        ("decompile index", decompile_index_path),
        ("decompile dir", decompile_dir),
        ("xref read-back", xrefs_path),
        ("instruction read-back", instructions_path),
        ("create dry result", create_dry_path),
        ("create apply result", create_apply_path),
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
    instructions = read_instructions(instructions_path)
    create_dry = read_create_rows(create_dry_path)
    create_apply = read_create_rows(create_apply_path)
    queue = read_queue(queue_path)

    xrefs_by_target: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in xrefs:
        xrefs_by_target[row["target_addr"]].append(row)

    instructions_by_target: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in instructions:
        instructions_by_target[row["target_addr"]].append(row)

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

        for expected in rule["expectedXrefs"]:
            if not any(
                xref.get("from_addr_norm") == normalize_address(expected["from_addr"])
                and xref.get("from_function_addr_norm") == normalize_address(expected["from_function_addr"])
                and xref.get("from_function", "") == expected["from_function"]
                and xref.get("ref_type", "") == expected["ref_type"]
                for xref in xrefs_by_target[address]
            ):
                failures.append(f"{address} missing expected xref from {expected['from_addr']} ({expected['from_function']})")

        if not any(
            row.get("role") == "TARGET"
            and row.get("function_name") == name
            and row.get("function_entry_norm") == address
            for row in instructions_by_target[address]
        ):
            failures.append(f"{address} missing instruction ownership read-back for {name}")

        targets.append(
            {
                "address": address,
                "oldName": rule["oldName"],
                "savedName": name,
                "signature": row.get("signature", ""),
                "classification": rule["classification"],
                "scope": rule["scope"],
                "xrefRows": len(xrefs_by_target[address]),
                "instructionRows": len(instructions_by_target[address]),
                "decompile": relative(decompile_file),
                "missingTokens": missing_tokens,
                "missingCommentTokens": missing_comment_tokens,
            }
        )

    for address in RULES:
        if address not in seen:
            failures.append(f"{address} missing from metadata read-back")

    for address in CREATED_FUNCTIONS:
        dry = create_dry.get(address)
        applied = create_apply.get(address)
        if dry is None or dry.get("status") != "would_create":
            failures.append(f"{address} create dry result was not would_create")
        if applied is None or applied.get("status") != "created":
            failures.append(f"{address} create apply result was not created")
        elif applied.get("name") != RULES[address]["newName"]:
            failures.append(f"{address} create apply saved unexpected name {applied.get('name')}")

    quality = queue.get("qualitySignals", {}) if isinstance(queue, dict) else {}
    if queue.get("status") != "PASS":
        failures.append("queue report did not pass")
    if queue.get("totalFunctions") != 5865:
        failures.append(f"expected queue totalFunctions 5865, found {queue.get('totalFunctions')}")
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
        failures.append(f"remaining deferred addresses missing from name-confidence queue: {', '.join(missing_remaining)}")

    status = "PASS" if not failures else "FAIL"
    return {
        "schema": "ghidra-name-confidence-deferral-correction.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "inputs": {
            "metadata": relative(metadata_path),
            "decompileIndex": relative(decompile_index_path),
            "decompileDir": relative(decompile_dir),
            "xrefs": relative(xrefs_path),
            "instructions": relative(instructions_path),
            "createDry": relative(create_dry_path),
            "createApply": relative(create_apply_path),
            "queue": relative(queue_path),
        },
        "targetCount": len(targets),
        "createdFunctionCount": len(CREATED_FUNCTIONS),
        "correctedRenameCount": len(RENAMED_FUNCTIONS),
        "targets": targets,
        "queue": {
            "totalFunctions": queue.get("totalFunctions"),
            "qualitySignals": quality,
            "remainingNameConfidence": sorted(REMAINING_NAME_CONFIDENCE_ADDRESSES),
        },
        "failures": failures,
        "whatIsProven": [
            "The saved Ghidra project now has recovered function boundaries at 0x0040dc30 and 0x0040dc60.",
            "The saved Ghidra name for 0x00412830 was corrected from the stale CCockpit wrapper label to a GeneralVolume linked-entry disable/reselect helper.",
            "Metadata, decompile, xref, instruction ownership, and queue read-back match the corrected state.",
        ],
        "notProven": [
            "This does not harden signatures, parameter names, local names, structures, or tags.",
            "This does not prove exact source method identity for these bodies.",
            "This does not prove runtime behavior or broader database correctness.",
            "This does not resolve the remaining 0x00402dd0, 0x0040dda0, 0x00413660, or 0x00418090 deferrals.",
        ],
        "privacy": "Report stores repo-relative artifact paths, public addresses, function names, counts, command summaries, and proof boundaries only; raw decompile/instruction exports remain ignored under subagents/.",
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--decompile-index", type=Path, default=DEFAULT_INDEX)
    parser.add_argument("--decompile-dir", type=Path, default=DEFAULT_DECOMPILE_DIR)
    parser.add_argument("--xrefs", type=Path, default=DEFAULT_XREFS)
    parser.add_argument("--instructions", type=Path, default=DEFAULT_INSTRUCTIONS)
    parser.add_argument("--create-dry", type=Path, default=DEFAULT_CREATE_DRY)
    parser.add_argument("--create-apply", type=Path, default=DEFAULT_CREATE_APPLY)
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
        instructions_path=args.instructions,
        create_dry_path=args.create_dry,
        create_apply_path=args.create_apply,
        queue_path=args.queue,
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        quality = report["queue"]["qualitySignals"]
        print("Ghidra name-confidence deferral correction probe")
        print(f"Status: {report['status']}")
        print(f"Output: {relative(out)}")
        print(f"Targets: {report['targetCount']}")
        print(f"Created functions: {report['createdFunctionCount']}")
        print(f"Corrected renames: {report['correctedRenameCount']}")
        print(f"Total functions: {report['queue']['totalFunctions']}")
        print(f"Uncertain owners: {quality.get('uncertainOwnerNameCount')}")
        print(f"Address-suffixed wrappers: {quality.get('wrapperAddressNameCount')}")
        for failure in report["failures"]:
            print(f"FAIL: {failure}")

    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
