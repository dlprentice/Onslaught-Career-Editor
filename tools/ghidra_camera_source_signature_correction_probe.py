#!/usr/bin/env python3
"""Validate the saved Ghidra Camera source/signature correction wave."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "camera-wave317" / "current"

TARGETS = {
    "0x00418ef0": {
        "name": "CThing3rdPersonCamera__ctor",
        "signature": ["void *", "__thiscall", "void * this", "void * forThing"],
        "comment": ["Source-parity", "Camera.cpp", "CBSpline", "GetRadius", "unproven"],
        "decompile": ["CBSpline", "GetRadius"],
    },
    "0x00419120": {
        "name": "CThing3rdPersonCamera__scalar_deleting_dtor",
        "signature": ["void *", "__thiscall", "byte flags"],
        "comment": ["scalar deleting destructor", "CThing3rdPersonCamera", "unproven"],
        "decompile": ["CThing3rdPersonCamera__dtor"],
    },
    "0x00419140": {
        "name": "CThing3rdPersonCamera__dtor",
        "signature": ["void", "__fastcall", "void * this"],
        "comment": ["Source-parity", "destructor", "mCurve", "active-reader", "unproven"],
        "decompile": ["CSPtrSet__Remove"],
    },
    "0x004198d0": {
        "name": "CPanCamera__ctor",
        "signature": ["void *", "__thiscall", "void * this", "void * forThing", "void * curve", "float length"],
        "comment": ["Source-parity", "CPanCamera", "start-time", "length", "unproven"],
        "decompile": ["DAT_00672fd0", "CPanCamera__Update"],
    },
    "0x00419a40": {
        "name": "CPanCamera__scalar_deleting_dtor",
        "signature": ["void *", "__thiscall", "byte flags"],
        "comment": ["scalar deleting destructor", "CPanCamera", "unproven"],
        "decompile": ["CPanCamera__dtor"],
    },
    "0x00419a60": {
        "name": "CPanCamera__dtor",
        "signature": ["void", "__fastcall", "void * this"],
        "comment": ["Source-parity", "CPanCamera", "curve", "active-reader", "unproven"],
        "decompile": ["CSPtrSet__Remove"],
    },
    "0x00419b00": {
        "name": "CPanCamera__Update",
        "signature": ["void", "__fastcall", "void * this"],
        "comment": ["Source-parity", "CBSpline", "UPDATE_CAMERA", "unproven"],
        "decompile": ["CBSpline", "CEventManager"],
    },
    "0x00419e00": {
        "name": "CViewPointCamera__ctor",
        "previous": ["CViewPointCamera__ctor_like_00419e00"],
        "signature": ["void *", "__thiscall", "void * this", "void * point", "float * rotateSpeed", "float * startDistance", "float * endDistance", "float * timeBetweenDistance"],
        "comment": ["Name/signature correction", "CViewPointCamera", "look-at point", "runtime death-camera behavior remains unproven"],
        "decompile": ["CViewPointCamera__ctor", "DAT_00660588"],
    },
    "0x0041a740": {
        "name": "CControllableCamera__ctor",
        "signature": ["void *", "__thiscall", "float posX", "float posW", "float orientation00", "float orientation23"],
        "comment": ["Signature hardening", "CControllableCamera", "FVector pos", "FMatrix orientation", "frame-count", "runtime free-camera behavior remains unproven"],
        "decompile": ["CControllableCamera__ctor", "DAT_006605c8"],
    },
}

STALE_TOKENS = [
    "CViewPointCamera__ctor_like_00419e00",
    "undefined CControllableCamera__ctor(void)",
]

DEFAULT_DRY = BASE / "signature_correction_dry.log"
DEFAULT_APPLY = BASE / "signature_correction_apply.log"
DEFAULT_METADATA = BASE / "metadata_final.tsv"
DEFAULT_INDEX = BASE / "decompile_final" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_final"
DEFAULT_XREFS = BASE / "xrefs_final.tsv"
DEFAULT_INSTRUCTIONS = BASE / "instructions_final.tsv"
DEFAULT_CALLSITES = BASE / "callsites_instructions_before.tsv"
DEFAULT_OUT = BASE / "camera-source-signature-correction.json"

OVERCLAIM_TOKENS = [
    "runtime camera behavior proven",
    "runtime free-camera behavior proven",
    "runtime death-camera behavior proven",
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
    callsites_path: Path = DEFAULT_CALLSITES,
) -> dict[str, object]:
    dry_log_path = resolve(dry_log_path)
    apply_log_path = resolve(apply_log_path)
    metadata_path = resolve(metadata_path)
    decompile_index_path = resolve(decompile_index_path)
    decompile_dir = resolve(decompile_dir)
    xrefs_path = resolve(xrefs_path)
    instructions_path = resolve(instructions_path)
    callsites_path = resolve(callsites_path)

    failures: list[str] = []
    for label, path in (
        ("dry log", dry_log_path),
        ("apply log", apply_log_path),
        ("metadata read-back", metadata_path),
        ("decompile index", decompile_index_path),
        ("xref read-back", xrefs_path),
        ("instruction read-back", instructions_path),
        ("callsite instruction context", callsites_path),
    ):
        if not path.is_file():
            failures.append(f"missing {label}: {relative(path)}")
    if not decompile_dir.is_dir():
        failures.append(f"missing decompile dir: {relative(decompile_dir)}")

    dry_summary = parse_summary(read_text(dry_log_path))
    apply_summary = parse_summary(read_text(apply_log_path))
    if dry_summary != {"updated": 0, "skipped": 9, "renamed": 0, "missing": 0, "bad": 0}:
        failures.append(f"unexpected dry summary: {dry_summary}")
    if apply_summary.get("updated") != 9 or apply_summary.get("skipped") != 0 or apply_summary.get("renamed") not in (0, 1) or apply_summary.get("missing") != 0 or apply_summary.get("bad") != 0:
        failures.append(f"unexpected apply summary: {apply_summary}")

    metadata_rows = read_tsv(metadata_path)
    index_rows = read_tsv(decompile_index_path)
    xref_rows = read_tsv(xrefs_path)
    instruction_rows = read_tsv(instructions_path)
    callsite_rows = read_tsv(callsites_path)

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

        for stale_name in expected.get("previous", []):
            if stale_name == name:
                failures.append(f"stale name still saved at {address}: {stale_name}")

        if not target_xrefs:
            failures.append(f"xrefs missing {address}")
        if not target_instructions:
            failures.append(f"instructions missing {address}")

        target_reports.append(
            {
                "address": address,
                "name": name,
                "signature": signature,
                "xrefRows": len(target_xrefs),
                "instructionRows": len(target_instructions),
            }
        )

    if not any(token_present(row.get("operands", ""), "0x00419e00") for row in callsite_rows):
        failures.append("missing CViewPointCamera constructor callsite context")
    if not any(token_present(row.get("operands", ""), "0x0041a740") for row in callsite_rows):
        failures.append("missing CControllableCamera constructor callsite context")
    if not any(token_present(row.get("mnemonic", ""), "SUB") and token_present(row.get("operands", ""), "ESP, 0x10") for row in callsite_rows):
        failures.append("missing by-value FVector stack-copy callsite clue for CControllableCamera")

    all_text = "\n".join(
        [
            read_text(metadata_path),
            read_text(decompile_index_path),
            "\n".join(decompile_text_for(decompile_dir, address) for address in TARGETS),
        ]
    )
    for stale_token in STALE_TOKENS:
        if stale_token in all_text:
            failures.append(f"stale token remains in final read-back: {stale_token}")
    for token in OVERCLAIM_TOKENS:
        if token_present(all_text, token):
            failures.append(f"overclaim token present: {token}")

    return {
        "schema": "ghidra-camera-source-signature-correction.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": "FAIL" if failures else "PASS",
        "classification": "camera-source-signature-and-constructor-correction",
        "targets": len(TARGETS),
        "renamedTargets": 1,
        "drySummary": dry_summary,
        "applySummary": apply_summary,
        "metadataRows": len(metadata_rows),
        "decompileRows": len(index_rows),
        "xrefRows": len(xref_rows),
        "instructionRows": len(instruction_rows),
        "callsiteRows": len(callsite_rows),
        "targetReports": target_reports,
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="exit non-zero when the report fails")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--dry-log", type=Path, default=DEFAULT_DRY)
    parser.add_argument("--apply-log", type=Path, default=DEFAULT_APPLY)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--decompile-index", type=Path, default=DEFAULT_INDEX)
    parser.add_argument("--decompile-dir", type=Path, default=DEFAULT_DECOMPILE_DIR)
    parser.add_argument("--xrefs", type=Path, default=DEFAULT_XREFS)
    parser.add_argument("--instructions", type=Path, default=DEFAULT_INSTRUCTIONS)
    parser.add_argument("--callsites", type=Path, default=DEFAULT_CALLSITES)
    args = parser.parse_args()

    report = build_report(
        dry_log_path=args.dry_log,
        apply_log_path=args.apply_log,
        metadata_path=args.metadata,
        decompile_index_path=args.decompile_index,
        decompile_dir=args.decompile_dir,
        xrefs_path=args.xrefs,
        instructions_path=args.instructions,
        callsites_path=args.callsites,
    )

    out_path = resolve(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"Status: {report['status']}")
    print(f"Classification: {report['classification']}")
    print(f"Targets: {report['targets']}")
    print(f"Renamed targets: {report['renamedTargets']}")
    print(f"Failures: {len(report['failures'])}")
    print(f"Report: {relative(out_path)}")
    if report["failures"]:
        for failure in report["failures"]:
            print(f"- {failure}")

    return 1 if args.check and report["status"] != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
