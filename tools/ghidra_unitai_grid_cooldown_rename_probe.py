#!/usr/bin/env python3
"""Validate the saved Ghidra rename for the CUnitAI grid-cooldown helper."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "unitai-grid-cooldown-rename" / "current"

ADDRESS = "0x0040dda0"
OLD_NAME = "CUnitAI_Unk_0044c720__Wrapper_0040dda0"
NEW_NAME = "CUnitAI__RefreshGridCooldownFromOccupiedCells"
CALLER_ADDRESS = "0x00485d50"
CALLER_NAME = "CExplosionInitThing__RenderObjectiveStatusPanel"

DEFAULT_METADATA = BASE / "metadata_readback.tsv"
DEFAULT_INDEX = BASE / "decompile_readback" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_readback"
DEFAULT_XREFS = BASE / "xrefs_readback.tsv"
DEFAULT_INSTRUCTIONS = BASE / "instructions_readback.tsv"
DEFAULT_CALLER_INDEX = BASE / "caller_decompile_readback" / "index.tsv"
DEFAULT_CALLER_DECOMPILE_DIR = BASE / "caller_decompile_readback"
DEFAULT_QUEUE_REPORT = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
DEFAULT_OUT = BASE / "unitai-grid-cooldown-rename.json"

DECOMPILE_TOKENS = [
    NEW_NAME,
    "CSquadNormal__GetCellValueAtWorldXY",
    "DAT_008a9d7c",
    "DAT_008a9d80",
    "0x2e8",
    "DAT_00672fd0",
]
COMMENT_TOKENS = [
    "CUnitAI",
    "Proof-boundary",
    "+0x2e8",
    "runtime behavior",
]
CALLER_TOKENS = [
    f"{NEW_NAME}(*(void **)(param_1 + 0x50))",
    "DAT_00672fd0 - *(float *)(*(int *)(param_1 + 0x50) + 0x2e8)",
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
    if value in {"", "<none>", "<no_function>", "<no_instruction>"}:
        return value
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def compact(value: str) -> str:
    return "".join(value.lower().split())


def has_token(text: str, token: str) -> bool:
    return compact(token) in compact(text)


def unescape_tsv(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_metadata(path: Path) -> dict[str, dict[str, str]]:
    rows = read_tsv(path)
    for row in rows:
        row["address"] = normalize_address(row.get("address", ""))
        row["comment"] = unescape_tsv(row.get("comment", ""))
    return {row["address"]: row for row in rows if row.get("address")}


def read_index(path: Path) -> dict[str, dict[str, str]]:
    rows = read_tsv(path)
    for row in rows:
        row["address"] = normalize_address(row.get("address", ""))
    return {row["address"]: row for row in rows if row.get("address")}


def read_xrefs(path: Path) -> list[dict[str, str]]:
    rows = read_tsv(path)
    for row in rows:
        row["target_addr_norm"] = normalize_address(row.get("target_addr", ""))
        row["from_addr_norm"] = normalize_address(row.get("from_addr", ""))
        row["from_function_addr_norm"] = normalize_address(row.get("from_function_addr", ""))
    return rows


def read_instructions(path: Path) -> list[dict[str, str]]:
    rows = read_tsv(path)
    for row in rows:
        row["target_addr_norm"] = normalize_address(row.get("target_addr", ""))
        row["instruction_addr_norm"] = normalize_address(row.get("instruction_addr", ""))
    return rows


def read_json(path: Path) -> dict[str, object]:
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
    caller_index_path: Path = DEFAULT_CALLER_INDEX,
    caller_decompile_dir: Path = DEFAULT_CALLER_DECOMPILE_DIR,
    queue_report_path: Path = DEFAULT_QUEUE_REPORT,
) -> dict[str, object]:
    metadata_path = resolve(metadata_path)
    decompile_index_path = resolve(decompile_index_path)
    decompile_dir = resolve(decompile_dir)
    xrefs_path = resolve(xrefs_path)
    instructions_path = resolve(instructions_path)
    caller_index_path = resolve(caller_index_path)
    caller_decompile_dir = resolve(caller_decompile_dir)
    queue_report_path = resolve(queue_report_path)

    failures: list[str] = []
    for label, path in (
        ("metadata read-back", metadata_path),
        ("decompile index", decompile_index_path),
        ("xref read-back", xrefs_path),
        ("instruction read-back", instructions_path),
        ("caller decompile index", caller_index_path),
        ("queue report", queue_report_path),
    ):
        if not path.is_file():
            failures.append(f"missing {label}: {relative(path)}")
    for label, path in (("decompile dir", decompile_dir), ("caller decompile dir", caller_decompile_dir)):
        if not path.is_dir():
            failures.append(f"missing {label}: {relative(path)}")

    metadata = read_metadata(metadata_path)
    decompile_index = read_index(decompile_index_path)
    caller_index = read_index(caller_index_path)
    xrefs = read_xrefs(xrefs_path)
    instructions = read_instructions(instructions_path)
    queue_report = read_json(queue_report_path)
    queue_signals = queue_report.get("qualitySignals", {}) if isinstance(queue_report, dict) else {}

    row = metadata.get(ADDRESS)
    if not row:
        failures.append(f"{ADDRESS}: missing metadata read-back row")
        name = None
        signature = None
        comment = ""
    else:
        name = row.get("name")
        signature = row.get("signature")
        comment = row.get("comment", "")
        if row.get("status") != "OK":
            failures.append(f"{ADDRESS}: metadata status is not OK")
        if name != NEW_NAME:
            failures.append(f"{ADDRESS}: expected {NEW_NAME}, got {name or '<blank>'}")
        if name == OLD_NAME:
            failures.append(f"{ADDRESS}: stale name survived ({OLD_NAME})")
        for token in COMMENT_TOKENS:
            if not has_token(comment, token):
                failures.append(f"{ADDRESS}: comment missing token {token!r}")

    index_row = decompile_index.get(ADDRESS)
    if not index_row or index_row.get("status") != "OK":
        failures.append(f"{ADDRESS}: missing OK decompile index row")
    elif index_row.get("name") != NEW_NAME:
        failures.append(f"{ADDRESS}: decompile index has stale or unexpected name {index_row.get('name')}")

    decompile_file = find_decompile_file(decompile_dir, ADDRESS)
    decompile_text = read_text(decompile_file)
    for token in DECOMPILE_TOKENS:
        if not has_token(decompile_text, token):
            failures.append(f"{ADDRESS}: decompile missing token {token!r}")
    if has_token(decompile_text, OLD_NAME):
        failures.append(f"{ADDRESS}: decompile still contains stale name {OLD_NAME}")

    expected_xrefs = [
        row
        for row in xrefs
        if row.get("target_addr_norm") == ADDRESS
        and row.get("from_addr_norm") == "0x004862af"
        and row.get("from_function_addr_norm") == CALLER_ADDRESS
        and row.get("from_function") == CALLER_NAME
        and row.get("ref_type") == "UNCONDITIONAL_CALL"
    ]
    if not expected_xrefs:
        failures.append(f"{ADDRESS}: missing expected xref from {CALLER_NAME} at 0x004862af")

    target_instructions = [row for row in instructions if row.get("target_addr_norm") == ADDRESS]
    if not target_instructions:
        failures.append(f"{ADDRESS}: missing target instruction rows")

    caller_row = caller_index.get(CALLER_ADDRESS)
    if not caller_row or caller_row.get("status") != "OK":
        failures.append(f"{ADDRESS}: missing OK caller decompile index row for {CALLER_ADDRESS}")
    caller_decompile_file = find_decompile_file(caller_decompile_dir, CALLER_ADDRESS)
    caller_text = read_text(caller_decompile_file)
    for token in CALLER_TOKENS:
        if not has_token(caller_text, token):
            failures.append(f"{ADDRESS}: caller decompile missing token {token!r}")
    if has_token(caller_text, OLD_NAME):
        failures.append(f"{ADDRESS}: caller decompile still contains stale name {OLD_NAME}")

    expected_queue = {
        "helperAddressNameCount": 0,
        "wrapperAddressNameCount": 2,
        "uncertainOwnerNameCount": 1,
    }
    for key, expected in expected_queue.items():
        if queue_signals.get(key) != expected:
            failures.append(f"queue {key}: expected {expected}, got {queue_signals.get(key)}")

    return {
        "schema": "ghidra-unitai-grid-cooldown-rename.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not failures else "FAIL",
        "address": ADDRESS,
        "oldName": OLD_NAME,
        "newName": NEW_NAME,
        "signature": signature,
        "inputs": {
            "metadata": relative(metadata_path),
            "decompileIndex": relative(decompile_index_path),
            "decompileDir": relative(decompile_dir),
            "xrefs": relative(xrefs_path),
            "instructions": relative(instructions_path),
            "callerDecompileIndex": relative(caller_index_path),
            "callerDecompileDir": relative(caller_decompile_dir),
            "queueReport": relative(queue_report_path),
        },
        "decompile": relative(decompile_file),
        "callerDecompile": relative(caller_decompile_file),
        "xrefRows": len(xrefs),
        "expectedXrefRows": len(expected_xrefs),
        "instructionRows": len(target_instructions),
        "queueSignals": queue_signals,
        "failures": failures,
        "whatIsProven": [
            "Ghidra read-back shows 0x0040dda0 saved as CUnitAI__RefreshGridCooldownFromOccupiedCells.",
            "The corrected body still checks two CSquadNormal grids and refreshes the +0x2e8 timestamp.",
            "The checked caller still passes the object at param_1+0x50 and reads the same +0x2e8 timestamp.",
        ],
        "notProven": [
            "This does not harden the signature, parameter names, locals, tags, structures, or type information.",
            "This does not prove exact source-to-retail identity or runtime behavior.",
            "This does not resolve the remaining 0x00402dd0 raw caller-boundary or 0x00418090 table-owner deferrals.",
        ],
        "privacy": "Report stores repo-relative artifact paths, public addresses, names, counts, and proof boundaries only; raw exports remain ignored under subagents/.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--decompile-index", type=Path, default=DEFAULT_INDEX)
    parser.add_argument("--decompile-dir", type=Path, default=DEFAULT_DECOMPILE_DIR)
    parser.add_argument("--xrefs", type=Path, default=DEFAULT_XREFS)
    parser.add_argument("--instructions", type=Path, default=DEFAULT_INSTRUCTIONS)
    parser.add_argument("--caller-index", type=Path, default=DEFAULT_CALLER_INDEX)
    parser.add_argument("--caller-decompile-dir", type=Path, default=DEFAULT_CALLER_DECOMPILE_DIR)
    parser.add_argument("--queue-report", type=Path, default=DEFAULT_QUEUE_REPORT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--check", action="store_true")
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
        caller_decompile_dir=args.caller_decompile_dir,
        queue_report_path=args.queue_report,
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("Ghidra CUnitAI grid-cooldown rename probe")
        print(f"Status: {report['status']}")
        print(f"Output: {relative(out)}")
        print(f"Name: {report['newName']}")
        for failure in report["failures"]:
            print(f"- {failure}")

    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
