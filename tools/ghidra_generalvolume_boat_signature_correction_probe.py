#!/usr/bin/env python3
"""Validate the saved GeneralVolume/Boat Ghidra signature and name correction tranche."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "generalvolume-boat-queue-wave310" / "current"

TARGETS = {
    "0x00414970": {
        "name": "CGeneralVolume__EnableEntriesByName",
        "signature": ["void", "__thiscall", "CGeneralVolume__EnableEntriesByName", "void * this", "char * entryName"],
        "comment": ["entry-name matcher", "linked entries", "+0x18", "+0x9c", "unproven"],
        "decompile": ["+ 0xa4", "+ 0x9c"],
        "instruction": ["0x00414970", "PUSH", "EBX"],
    },
    "0x00414a40": {
        "name": "CGeneralVolume__DisableEntriesByNameAndReselect",
        "signature": [
            "void",
            "__thiscall",
            "CGeneralVolume__DisableEntriesByNameAndReselect",
            "void * this",
            "char * entryName",
        ],
        "comment": ["entry-name matcher", "clears enable flag", "+0x18", "+0x9c", "reselects", "unproven"],
        "decompile": ["CBattleEngineWalkerPart__GetCurrentWeapon", "CBattleEngineWalkerPart__ChangeWeapon", "+ 0x9c"],
        "instruction": ["0x00414a40", "PUSH", "ECX"],
    },
    "0x00414b70": {
        "name": "CGeneralVolume__CountEnabledEntriesIncludingPrimary",
        "signature": ["int", "__fastcall", "CGeneralVolume__CountEnabledEntriesIncludingPrimary", "void * this"],
        "comment": ["counts linked entries", "+0x9c", "primary entry", "+0x18", "unproven"],
        "decompile": ["+ 0x9c", "+ 0x18"],
        "instruction": ["0x00414b70", "PUSH", "ESI"],
    },
    "0x00414cb0": {
        "name": "CDXBattleLine__PopulateBattleLineAndInfluenceOverlayVertices",
        "signature": ["void", "__thiscall", "CDXBattleLine__PopulateBattleLineAndInfluenceOverlayVertices", "void * this"],
        "comment": ["resets vertex count", "+0x60", "DAT_00855140", "DAT_008550a0", "CDXBattleLine__AppendOverlayVertex", "unproven"],
        "decompile": ["CDXBattleLine__AppendOverlayVertex", "DAT_00855140", "DAT_008550a0"],
        "instruction": ["0x00414cb0", "PUSH", "ESI"],
    },
    "0x00414e50": {
        "name": "CBoat__Init",
        "signature": ["void", "__thiscall", "CBoat__Init", "void * this", "void * init"],
        "comment": ["CBoat init", "CGroundUnit__Init", "CBoatGuide", "Warspite", "+0x260", "+0x264", "+0x268", "unproven"],
        "decompile": ["CGroundUnit__Init", "CBoatGuide__ctor_like_00415d70", "CWarspite__Init", "+ 0x260"],
        "instruction": ["0x00414e50", "PUSH", "-0x1"],
    },
    "0x00414fa0": {
        "name": "CBoatAI__scalar_deleting_dtor",
        "signature": ["void *", "__thiscall", "CBoatAI__scalar_deleting_dtor", "void * this", "int flags"],
        "comment": ["destructor wrapper", "0x00414fc0", "scalar-delete flag", "OID__FreeObject", "unproven"],
        "decompile": ["CBoatAI__dtor_body_00414fc0", "OID__FreeObject"],
        "instruction": ["0x00414fa0", "CALL", "0x00414fc0"],
    },
    "0x00414fc0": {
        "name": "CBoatAI__dtor_body_00414fc0",
        "signature": ["void", "__fastcall", "CBoatAI__dtor_body_00414fc0", "void * this"],
        "comment": ["destructor body", "0x005d8d1c", "+0x28/+0x24/+0xc", "CSPtrSet__Remove", "CMonitor__Shutdown", "unproven"],
        "decompile": ["CSPtrSet__Remove", "CMonitor__Shutdown", "+ 0x28", "+ 0x24", "+ 0xc"],
        "instruction": ["0x00414fc0", "PUSH", "-0x1"],
    },
    "0x00415060": {
        "name": "CUnitAI__scalar_deleting_dtor",
        "signature": ["void *", "__thiscall", "CUnitAI__scalar_deleting_dtor", "void * this", "int flags"],
        "comment": ["destructor wrapper", "0x00415080", "scalar-delete flag", "OID__FreeObject", "unproven"],
        "decompile": ["CUnitAI__dtor_body_00415080", "OID__FreeObject"],
        "instruction": ["0x00415060", "CALL", "0x00415080"],
    },
    "0x00415080": {
        "name": "CUnitAI__dtor_body_00415080",
        "signature": ["void", "__fastcall", "CUnitAI__dtor_body_00415080", "void * this"],
        "comment": ["destructor body", "0x005d8d1c", "+0x28/+0x24/+0xc", "CSPtrSet__Remove", "CMonitor__Shutdown", "unproven"],
        "decompile": ["CSPtrSet__Remove", "CMonitor__Shutdown", "+ 0x28", "+ 0x24", "+ 0xc"],
        "instruction": ["0x00415080", "PUSH", "-0x1"],
    },
}

DEFAULT_DRY = BASE / "signature_correction_dry.log"
DEFAULT_APPLY = BASE / "signature_correction_apply.log"
DEFAULT_METADATA = BASE / "metadata_final.tsv"
DEFAULT_INDEX = BASE / "decompile_final" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_final"
DEFAULT_XREFS = BASE / "xrefs_final.tsv"
DEFAULT_INSTRUCTIONS = BASE / "instructions_final.tsv"
DEFAULT_OUT = BASE / "generalvolume-boat-signature-correction.json"

OVERCLAIM_TOKENS = [
    "runtime behavior proven",
    "source identity proven",
    "exact source identity proven",
    "fully re'ed",
    "100% re",
]

STALE_NAME_TOKENS = [
    "LinkedObjectList__CountFlag9C_IncludingExtra",
    "CExplosionInitThing__PopulateBattleLinePoints",
    "CBoatAI__VFunc_01_00414fa0",
    "CUnitAI__VFunc_01_00415060",
    "ctor_like_00414fc0",
    "ctor_like_00415080",
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
    dry_text = read_text(dry_log_path)
    apply_text = read_text(apply_log_path)
    metadata_rows = read_tsv(metadata_path)
    index_rows = read_tsv(decompile_index_path)
    xref_rows = read_tsv(xrefs_path)
    instruction_rows = read_tsv(instructions_path)

    dry_summary = parse_apply_summary(dry_text)
    apply_summary = parse_apply_summary(apply_text)
    expected_count = len(TARGETS)
    expected_renamed = 6

    if dry_summary != {"updated": 0, "skipped": expected_count, "renamed": 0, "missing": 0, "bad": 0}:
        failures.append(f"unexpected dry summary: {dry_summary}")
    if apply_summary != {"updated": expected_count, "skipped": 0, "renamed": expected_renamed, "missing": 0, "bad": 0}:
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
                failures.append(f"{address} comment overclaim token present: {token}")

        decompile_file = decompile_file_for(decompile_dir, address)
        decompile_text = read_text(decompile_file) if decompile_file else ""
        if not decompile_text:
            failures.append(f"{address} missing decompile file")
        for token in target["decompile"]:
            if not token_present(decompile_text, str(token)):
                failures.append(f"{address} decompile token missing: {token}")

        instruction_blob = "\n".join(
            " ".join(row.get(field, "") for field in ("instruction_addr", "mnemonic", "operands"))
            for row in rows_for(instruction_rows, address)
        )
        for token in target["instruction"]:
            if not token_present(instruction_blob, str(token)):
                failures.append(f"{address} instruction token missing: {token}")

    metadata_blob = "\n".join(row.get("name", "") + "\t" + row.get("signature", "") for row in metadata_rows)
    for token in STALE_NAME_TOKENS:
        if token in metadata_blob:
            stale_name_hits += 1
            failures.append(f"stale function label remains in metadata: {token}")

    report = {
        "status": "PASS" if not failures else "FAIL",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "classification": "generalvolume-boat-signature-name-correction",
        "summary": {
            "targets": expected_count,
            "renamedTargets": apply_summary.get("renamed", -1),
            "signatureHardenedTargets": apply_summary.get("updated", -1),
            "staleParamSignatureHits": stale_param_hits,
            "staleNameHits": stale_name_hits,
            "commentOverclaims": comment_overclaims,
            "xrefRows": len(xref_rows),
            "instructionRows": len(instruction_rows),
            "fullyReedClaim": "not-claimed",
        },
        "inputs": {
            "dryLog": relative(dry_log_path),
            "applyLog": relative(apply_log_path),
            "metadata": relative(metadata_path),
            "decompileIndex": relative(decompile_index_path),
            "decompileDir": relative(decompile_dir),
            "xrefs": relative(xrefs_path),
            "instructions": relative(instructions_path),
        },
        "failures": failures,
    }
    return report


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-log", type=Path, default=DEFAULT_DRY)
    parser.add_argument("--apply-log", type=Path, default=DEFAULT_APPLY)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--decompile-index", type=Path, default=DEFAULT_INDEX)
    parser.add_argument("--decompile-dir", type=Path, default=DEFAULT_DECOMPILE_DIR)
    parser.add_argument("--xrefs", type=Path, default=DEFAULT_XREFS)
    parser.add_argument("--instructions", type=Path, default=DEFAULT_INSTRUCTIONS)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    report = build_report(
        dry_log_path=args.dry_log,
        apply_log_path=args.apply_log,
        metadata_path=args.metadata,
        decompile_index_path=args.decompile_index,
        decompile_dir=args.decompile_dir,
        xrefs_path=args.xrefs,
        instructions_path=args.instructions,
    )
    out_path = resolve(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(
        "generalvolume boat signature correction: "
        f"{report['status']} targets={report['summary']['targets']} "
        f"renamed={report['summary']['renamedTargets']} "
        f"failures={len(report['failures'])}"
    )
    if args.check and report["status"] != "PASS":
        for failure in report["failures"]:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
