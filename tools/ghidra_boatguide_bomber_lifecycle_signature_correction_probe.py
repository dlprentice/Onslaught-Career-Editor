#!/usr/bin/env python3
"""Validate the saved BoatGuide/Bomber lifecycle Ghidra signature correction tranche."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "boatguide-bomber-lifecycle-wave312" / "current"

TARGETS = {
    "0x00415d70": {
        "name": "CBoatGuide__ctor",
        "signature": ["void *", "__thiscall", "CBoatGuide__ctor", "void * this", "void * init"],
        "comment": ["constructor", "CGuide__ctor_like_0047e290", "0x005d8d5c", "CBoat__Init", "unproven"],
        "decompile": ["CGuide__ctor_like_0047e290", "PTR_CFrontEndPage__ActiveNotification_NoOp_005d8d5c", "return this"],
        "instruction": ["0x00415d70", "MOV", "EAX"],
    },
    "0x004161a0": {
        "name": "CBomberAI__scalar_deleting_dtor",
        "signature": ["void *", "__thiscall", "CBomberAI__scalar_deleting_dtor", "void * this", "int flags"],
        "comment": ["scalar-delete flag bit 0", "0x004161c0", "OID__FreeObject", "Bomber.cpp source is missing", "unproven"],
        "decompile": ["CBomberAI__dtor_body_004161c0", "OID__FreeObject", "flags"],
        "instruction": ["0x004161a0", "PUSH", "ESI"],
    },
    "0x004161c0": {
        "name": "CBomberAI__dtor_body_004161c0",
        "signature": ["void", "__fastcall", "CBomberAI__dtor_body_004161c0", "void * this"],
        "comment": ["destructor body", "+0x28/+0x24/+0xc", "CSPtrSet__Remove", "CMonitor__Shutdown", "unproven"],
        "decompile": ["CSPtrSet__Remove", "CMonitor__Shutdown", "+ 0x28"],
        "instruction": ["0x004161c0", "PUSH", "-0x1"],
    },
    "0x00416260": {
        "name": "CBomberGuide__scalar_deleting_dtor",
        "signature": ["void *", "__thiscall", "CBomberGuide__scalar_deleting_dtor", "void * this", "int flags"],
        "comment": ["scalar-delete flag bit 0", "0x00416280", "OID__FreeObject", "Bomber.cpp source is missing", "unproven"],
        "decompile": ["CBomberGuide__dtor_body_00416280", "OID__FreeObject", "flags"],
        "instruction": ["0x00416260", "PUSH", "ESI"],
    },
    "0x00416280": {
        "name": "CBomberGuide__dtor_body_00416280",
        "signature": ["void", "__fastcall", "CBomberGuide__dtor_body_00416280", "void * this"],
        "comment": ["destructor body", "+0x2c", "CSPtrSet__Remove", "CMonitor__Shutdown", "unproven"],
        "decompile": ["CSPtrSet__Remove", "CMonitor__Shutdown", "+ 0x2c"],
        "instruction": ["0x00416280", "PUSH", "-0x1"],
    },
}

DEFAULT_DRY = BASE / "signature_correction_dry.log"
DEFAULT_APPLY = BASE / "signature_correction_apply.log"
DEFAULT_METADATA = BASE / "metadata_final.tsv"
DEFAULT_INDEX = BASE / "decompile_final" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_final"
DEFAULT_XREFS = BASE / "xrefs_final.tsv"
DEFAULT_INSTRUCTIONS = BASE / "instructions_final.tsv"
DEFAULT_OUT = BASE / "boatguide-bomber-lifecycle-signature-correction.json"

OVERCLAIM_TOKENS = ["runtime behavior proven", "source identity proven", "fully re'ed", "100% re"]
STALE_NAME_TOKENS = [
    "CBoatGuide__ctor_like_00415d70",
    "CBomberAI__VFunc_01_004161a0",
    "CUnitAI__ctor_like_004161c0",
    "CBomberGuide__VFunc_01_00416260",
    "CBomberGuide__DetachFromSetAndShutdownMonitor",
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
        return list(csv.DictReader(handle, delimiter="\t"))


def parse_apply_summary(log_text: str) -> dict[str, int]:
    match = re.search(r"updated=(\d+)\s+skipped=(\d+)\s+renamed=(\d+)\s+missing=(\d+)\s+bad=(\d+)", log_text)
    if not match:
        return {"updated": -1, "skipped": -1, "renamed": -1, "missing": -1, "bad": -1}
    return {
        "updated": int(match.group(1)),
        "skipped": int(match.group(2)),
        "renamed": int(match.group(3)),
        "missing": int(match.group(4)),
        "bad": int(match.group(5)),
    }


def find_row(rows: list[dict[str, str]], key: str, address: str) -> dict[str, str] | None:
    wanted = normalize_address(address)
    for row in rows:
        if normalize_address(row.get(key, "")) == wanted:
            return row
    return None


def decompile_file_for(decompile_dir: Path, address: str) -> Path | None:
    if not decompile_dir.is_dir():
        return None
    matches = sorted(decompile_dir.glob(f"{normalize_address(address)[2:]}_*.c"))
    return matches[0] if matches else None


def rows_for(rows: list[dict[str, str]], address: str) -> list[dict[str, str]]:
    wanted = normalize_address(address)
    return [
        row
        for row in rows
        if normalize_address(row.get("target_addr", "")) == wanted
        or normalize_address(row.get("function_entry", "")) == wanted
    ]


def build_report(
    *,
    dry_log_path: Path = DEFAULT_DRY,
    apply_log_path: Path = DEFAULT_APPLY,
    metadata_path: Path = DEFAULT_METADATA,
    decompile_index_path: Path = DEFAULT_INDEX,
    decompile_dir: Path = DEFAULT_DECOMPILE_DIR,
    xrefs_path: Path = DEFAULT_XREFS,
    instructions_path: Path = DEFAULT_INSTRUCTIONS,
) -> dict[str, object]:
    dry_log_path = resolve(dry_log_path)
    apply_log_path = resolve(apply_log_path)
    metadata_path = resolve(metadata_path)
    decompile_index_path = resolve(decompile_index_path)
    decompile_dir = resolve(decompile_dir)
    xrefs_path = resolve(xrefs_path)
    instructions_path = resolve(instructions_path)

    failures: list[str] = []
    metadata_rows = read_tsv(metadata_path)
    index_rows = read_tsv(decompile_index_path)
    xref_rows = read_tsv(xrefs_path)
    instruction_rows = read_tsv(instructions_path)

    expected_count = len(TARGETS)
    dry_summary = parse_apply_summary(read_text(dry_log_path))
    apply_summary = parse_apply_summary(read_text(apply_log_path))
    if dry_summary != {"updated": 0, "skipped": expected_count, "renamed": 0, "missing": 0, "bad": 0}:
        failures.append(f"unexpected dry summary: {dry_summary}")
    if apply_summary != {"updated": expected_count, "skipped": 0, "renamed": expected_count, "missing": 0, "bad": 0}:
        failures.append(f"unexpected apply summary: {apply_summary}")

    stale_param_hits = 0
    stale_name_hits = 0
    comment_overclaims = 0

    for address, target in TARGETS.items():
        row = find_row(metadata_rows, "address", address)
        index_row = find_row(index_rows, "address", address)
        if row is None:
            failures.append(f"{address} missing metadata row")
            continue
        if index_row is None:
            failures.append(f"{address} missing decompile index row")
        if row.get("name") != target["name"]:
            failures.append(f"{address} name mismatch: {row.get('name')} != {target['name']}")

        signature = row.get("signature", "")
        for token in target["signature"]:
            if not token_present(signature, str(token)):
                failures.append(f"{address} signature token missing: {token}")
        if "param_" in signature:
            stale_param_hits += 1
            failures.append(f"{address} signature still contains param_N placeholder: {signature}")

        comment = row.get("comment", "")
        for token in target["comment"]:
            if not token_present(comment, str(token)):
                failures.append(f"{address} comment token missing: {token}")
        lowered_comment = comment.lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered_comment:
                comment_overclaims += 1
                failures.append(f"{address} comment overclaim token: {token}")

        decompile_path = decompile_file_for(decompile_dir, address)
        if decompile_path is None:
            failures.append(f"{address} missing decompile file")
        else:
            decompile_text = read_text(decompile_path)
            for token in target["decompile"]:
                if not token_present(decompile_text, str(token)):
                    failures.append(f"{address} decompile token missing: {token}")
            for token in STALE_NAME_TOKENS:
                if token in decompile_text and target["name"] != token:
                    stale_name_hits += 1
                    failures.append(f"{address} decompile still contains stale name: {token}")

        target_instruction_rows = rows_for(instruction_rows, address)
        if not target_instruction_rows:
            failures.append(f"{address} missing instruction rows")
        else:
            joined = "\n".join("\t".join(row.values()) for row in target_instruction_rows)
            for token in target["instruction"]:
                if not token_present(joined, str(token)):
                    failures.append(f"{address} instruction token missing: {token}")

    return {
        "schema": "boatguide-bomber-lifecycle-signature-correction.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not failures else "FAIL",
        "targets": len(TARGETS),
        "renamed": apply_summary.get("renamed", -1),
        "failures": failures,
        "staleParamSignatureHits": stale_param_hits,
        "staleNameHits": stale_name_hits,
        "commentOverclaims": comment_overclaims,
        "xrefRows": len(xref_rows),
        "instructionRows": len(instruction_rows),
        "inputs": {
            "dryLog": relative(dry_log_path),
            "applyLog": relative(apply_log_path),
            "metadata": relative(metadata_path),
            "decompileIndex": relative(decompile_index_path),
            "decompileDir": relative(decompile_dir),
            "xrefs": relative(xrefs_path),
            "instructions": relative(instructions_path),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="return non-zero if validation fails")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    report = build_report()
    out_path = resolve(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(
        "boatguide bomber lifecycle signature correction: "
        f"{report['status']} targets={report['targets']} renamed={report['renamed']} failures={len(report['failures'])}"
    )
    if report["failures"]:
        for failure in report["failures"]:
            print(f"- {failure}", file=sys.stderr)
    if args.check and report["status"] != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
