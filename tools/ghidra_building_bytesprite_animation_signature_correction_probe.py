#!/usr/bin/env python3
"""Validate Wave 314 Building / ByteSprite saved-Ghidra corrections."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "bytesprite-animation-wave314" / "current"

TARGETS = {
    "0x00417870": {
        "name": "CBuilding__VFuncSlot_02_RemoveFromWorldUpdateShadowAndForward",
        "previous": ["VFuncSlot_02_00417870"],
        "signature": ["void", "__fastcall", "void * this"],
        "comment": ["RTTI read-back", "CBuilding", "CSimpleBuilding", "occupancy grid", "static-shadow", "0x004f95d0", "remain unproven"],
    },
    "0x004178a0": {
        "name": "CBuilding__ProcessClosingAndUnshuttingAnimations",
        "previous": ["CUnit__ProcessClosingAndUnshuttingAnimations"],
        "signature": ["void", "__fastcall", "void * this"],
        "comment": ["Owner/signature correction", "CBuilding vtable", "closing/unshutting", "+0x254", "+0x268", "remain unproven"],
    },
    "0x00418120": {
        "name": "CBuilding__AdvanceOpenCloseAnimationState",
        "previous": ["CCockpit__AdvanceOpenCloseAnimationState"],
        "signature": ["int", "__fastcall", "void * this"],
        "comment": ["Owner/signature correction", "CBuilding vtable", "open/close/shut", "+0x58", "+0xf0", "+0x264", "remain unproven"],
    },
    "0x004183d0": {
        "name": "CBuildingNamedMesh__dtor_base",
        "previous": ["CByteSprite__dtor_base"],
        "signature": ["void", "__fastcall", "void * this"],
        "comment": ["CBuildingNamedMesh", "superseding", "CByteSprite deferral", "CActor__dtor_base", "remain unproven"],
    },
    "0x00418430": {
        "name": "CBuildingNamedMesh__scalar_deleting_dtor",
        "previous": ["CByteSprite__scalar_deleting_dtor"],
        "signature": ["void *", "__thiscall", "void * this", "int flags"],
        "comment": ["scalar-deleting destructor", "CBuildingNamedMesh__dtor_base", "OID__FreeObject", "returns this", "remain unproven"],
    },
    "0x00418450": {
        "name": "CBuildingNamedMesh__VFuncSlot_02_RemoveFromWorldAndForwardNamedMesh",
        "previous": ["CByteSprite__vfunc_stub"],
        "signature": ["void", "__fastcall", "void * this"],
        "comment": ["CBuildingNamedMesh vtable", "occupancy grid", "CNamedMesh slot 2", "remain unproven"],
    },
    "0x00418470": {
        "name": "CByteSprite__Init",
        "previous": [],
        "signature": ["void *", "__fastcall", "void * this"],
        "comment": ["CByteSprite init", "zeroes", "loaded-frame count", "0x20-byte", "remain unproven"],
    },
    "0x004184c0": {
        "name": "CByteSprite__Load",
        "previous": [],
        "signature": ["int", "__thiscall", "void * this", "char * rawName", "int width", "int height", "int frameCount", "byte transparentThreshold"],
        "comment": ["data_%s.raw", "DXMemBuffer", "CByteSprite__EncodeFrame", "16x16", "20 frames", "threshold 4", "remain unproven"],
    },
    "0x00418720": {
        "name": "CByteSprite__SetTarget",
        "previous": [],
        "signature": ["void", "__thiscall", "void * this", "void * targetBuffer", "int pitch", "int width", "int height", "byte wrapFlag"],
        "comment": ["destination buffer", "+0xc", "+0x1c", "512x512", "wrap enabled", "remain unproven"],
    },
    "0x00418750": {
        "name": "CByteSprite__DrawRLE_NoClip",
        "previous": [],
        "signature": ["void", "__thiscall", "void * this", "char * rleData", "int x", "int y", "int height"],
        "comment": ["RLE", "without horizontal clipping", "target buffer", "remain unproven"],
    },
    "0x004187e0": {
        "name": "CByteSprite__DrawRLE_ClipLeft",
        "previous": [],
        "signature": ["void", "__thiscall", "void * this", "char * rleData", "int x", "int y", "int height"],
        "comment": ["RLE", "left-edge clipping", "destination x is negative", "remain unproven"],
    },
    "0x00418880": {
        "name": "CByteSprite__DrawRLE_ClipRight",
        "previous": [],
        "signature": ["void", "__thiscall", "void * this", "char * rleData", "int x", "int y", "int height"],
        "comment": ["RLE", "right-edge clipping", "target width", "remain unproven"],
    },
    "0x00418920": {
        "name": "CByteSprite__DrawFrame",
        "previous": [],
        "signature": ["void", "__thiscall", "void * this", "int frameIndex", "int x", "int y"],
        "comment": ["frameIndex", "frame offset", "RLE", "wraps horizontally", "remain unproven"],
    },
    "0x004189f0": {
        "name": "CByteSprite__EncodeFrame",
        "previous": [],
        "signature": ["int", "__fastcall", "void * workState"],
        "comment": ["raw-frame work state", "threshold byte", "RLE packet stream", "returns 1", "empty frame", "remain unproven"],
    },
}

DEFAULT_DRY = BASE / "signature_correction_dry.log"
DEFAULT_APPLY = BASE / "signature_correction_apply.log"
DEFAULT_METADATA = BASE / "metadata_final.tsv"
DEFAULT_INDEX = BASE / "decompile_final" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_final"
DEFAULT_XREFS = BASE / "xrefs_final.tsv"
DEFAULT_INSTRUCTIONS = BASE / "instructions_final.tsv"
DEFAULT_VTABLES = BASE / "vtable_type_names.tsv"
DEFAULT_CALLER_INDEX = BASE / "caller_decompile_final" / "index.tsv"
DEFAULT_CALLER_DIR = BASE / "caller_decompile_final"
DEFAULT_OUT = BASE / "building-bytesprite-animation-signature-correction.json"

OVERCLAIMS = [
    "runtime behavior proven",
    "exact source identity proven",
    "class layout proven",
    "rebuild parity proven",
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
        for key in ("address", "target_addr"):
            if key in row:
                row[key] = normalize_address(row[key])
        if "comment" in row:
            row["comment"] = unescape(row["comment"])
    return rows


def parse_summary(text: str) -> dict[str, int]:
    match = re.search(r"updated=(\d+)\s+skipped=(\d+)\s+renamed=(\d+)\s+missing=(\d+)\s+bad=(\d+)", text)
    if not match:
        return {"updated": -1, "skipped": -1, "renamed": -1, "missing": -1, "bad": -1}
    keys = ("updated", "skipped", "renamed", "missing", "bad")
    return {key: int(match.group(index + 1)) for index, key in enumerate(keys)}


def row_by_address(rows: list[dict[str, str]], address: str, key: str = "address") -> dict[str, str] | None:
    wanted = normalize_address(address)
    for row in rows:
        if normalize_address(row.get(key, "")) == wanted:
            return row
    return None


def decompile_text_for(directory: Path, address: str, name: str) -> str:
    if not directory.is_dir():
        return ""
    addr = normalize_address(address)[2:]
    matches = sorted(directory.glob(f"{addr}_*.c"))
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
    vtable_path: Path = DEFAULT_VTABLES,
    caller_index_path: Path = DEFAULT_CALLER_INDEX,
    caller_dir: Path = DEFAULT_CALLER_DIR,
) -> dict[str, object]:
    paths = [resolve(path) for path in (dry_log_path, apply_log_path, metadata_path, decompile_index_path, xrefs_path, instructions_path, vtable_path, caller_index_path)]
    dry_log_path, apply_log_path, metadata_path, decompile_index_path, xrefs_path, instructions_path, vtable_path, caller_index_path = paths
    decompile_dir = resolve(decompile_dir)
    caller_dir = resolve(caller_dir)

    failures: list[str] = []
    for label, path in (
        ("dry log", dry_log_path),
        ("apply log", apply_log_path),
        ("metadata read-back", metadata_path),
        ("decompile index", decompile_index_path),
        ("xref read-back", xrefs_path),
        ("instruction read-back", instructions_path),
        ("vtable type read-back", vtable_path),
        ("caller decompile index", caller_index_path),
    ):
        if not path.is_file():
            failures.append(f"missing {label}: {relative(path)}")
    for label, path in (("decompile dir", decompile_dir), ("caller decompile dir", caller_dir)):
        if not path.is_dir():
            failures.append(f"missing {label}: {relative(path)}")

    dry_summary = parse_summary(read_text(dry_log_path))
    apply_summary = parse_summary(read_text(apply_log_path))
    if dry_summary != {"updated": 0, "skipped": 14, "renamed": 0, "missing": 0, "bad": 0}:
        failures.append(f"unexpected dry summary: {dry_summary}")
    if apply_summary != {"updated": 14, "skipped": 0, "renamed": 6, "missing": 0, "bad": 0}:
        failures.append(f"unexpected apply summary: {apply_summary}")

    metadata_rows = read_tsv(metadata_path)
    index_rows = read_tsv(decompile_index_path)
    xref_rows = read_tsv(xrefs_path)
    instruction_rows = read_tsv(instructions_path)
    vtable_rows = read_tsv(vtable_path)
    caller_rows = read_tsv(caller_index_path)

    stale_names: list[str] = []
    target_reports: list[dict[str, object]] = []
    for address, expected in TARGETS.items():
        row = row_by_address(metadata_rows, address)
        index_row = row_by_address(index_rows, address)
        if row is None:
            failures.append(f"metadata missing {address}")
            continue
        if row.get("status") != "OK":
            failures.append(f"metadata status not OK at {address}")
        if row.get("name") != expected["name"]:
            failures.append(f"name mismatch at {address}: {row.get('name')} != {expected['name']}")
        signature = row.get("signature", "")
        comment = row.get("comment", "")
        missing_signature = [token for token in expected["signature"] if not token_present(signature, token)]
        missing_comment = [token for token in expected["comment"] if not token_present(comment, token)]
        if missing_signature:
            failures.append(f"signature tokens missing at {address}: {missing_signature}")
        if missing_comment:
            failures.append(f"comment tokens missing at {address}: {missing_comment}")
        for previous in expected["previous"]:
            if previous == row.get("name"):
                stale_names.append(f"{address}:{previous}")
            if previous in signature or previous in comment:
                stale_names.append(f"{address}:{previous}:text")
        for token in OVERCLAIMS:
            if token_present(comment, token):
                failures.append(f"overclaim token in comment at {address}: {token}")
        if index_row is None or index_row.get("status") != "OK":
            failures.append(f"decompile index missing/failed at {address}")
        decompile_text = decompile_text_for(decompile_dir, address, expected["name"])
        if expected["name"] not in decompile_text:
            failures.append(f"decompile text missing expected name at {address}")
        target_reports.append({
            "address": address,
            "name": row.get("name"),
            "signature": signature,
            "commented": bool(comment.strip()),
        })

    if stale_names:
        failures.append(f"stale names remain: {stale_names}")
    if len(metadata_rows) != len(TARGETS):
        failures.append(f"metadata target count mismatch: {len(metadata_rows)}")
    if len(index_rows) != len(TARGETS):
        failures.append(f"decompile target count mismatch: {len(index_rows)}")
    if len(xref_rows) < 19:
        failures.append(f"xref row count too low: {len(xref_rows)}")
    if len(instruction_rows) < 1300:
        failures.append(f"instruction row count too low: {len(instruction_rows)}")

    vtable_types = {row.get("demangled_type_name", "") for row in vtable_rows}
    for expected_type in ("CBuilding", "CSimpleBuilding", "CBuildingNamedMesh"):
        if expected_type not in vtable_types:
            failures.append(f"missing vtable type {expected_type}")

    caller_ok = any(row.get("address") == "0x0053be40" and row.get("status") == "OK" for row in caller_rows)
    if not caller_ok:
        failures.append("caller decompile for CDXCompass__Init missing/failed")
    caller_text = "".join(read_text(path) for path in sorted(caller_dir.glob("*.c"))) if caller_dir.is_dir() else ""
    for token in ("CByteSprite__Init", "CByteSprite__Load", "CByteSprite__SetTarget", "compass", "0x10", "0x14", "0x200"):
        if not token_present(caller_text, token):
            failures.append(f"caller decompile missing token: {token}")

    status = "PASS" if not failures else "FAIL"
    return {
        "schema": "ghidra-building-bytesprite-animation-signature-correction.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "inputs": {
            "metadata": relative(metadata_path),
            "decompileIndex": relative(decompile_index_path),
            "xrefs": relative(xrefs_path),
            "instructions": relative(instructions_path),
            "vtableTypes": relative(vtable_path),
            "callerDecompileIndex": relative(caller_index_path),
        },
        "drySummary": dry_summary,
        "applySummary": apply_summary,
        "targetCount": len(TARGETS),
        "renamedTargets": apply_summary.get("renamed", 0),
        "xrefRows": len(xref_rows),
        "instructionRows": len(instruction_rows),
        "vtableTypes": sorted(vtable_types),
        "targets": target_reports,
        "failures": failures,
        "whatIsProven": [
            "Saved Ghidra names/signatures/comments match the Wave 314 Building, BuildingNamedMesh, and CByteSprite read-back evidence.",
            "The stale CUnit/CCockpit/CByteSprite owner labels checked by this wave no longer remain on the corrected targets.",
            "The CByteSprite load/draw helpers now carry stack-argument signatures matching final decompile and caller read-back.",
        ],
        "notProven": [
            "This does not prove exact Stuart-source method identities.",
            "This does not prove concrete class layouts, local variables, tags, or structure types.",
            "This does not prove runtime building animation, named-mesh, compass, sprite rendering, palette, or transparency behavior.",
            "This does not patch, launch, or mutate BEA.exe or the installed game.",
        ],
    }


def write_report(report: dict[str, object], out_path: Path) -> None:
    out_path = resolve(out_path)
    try:
        out_path.resolve().relative_to((ROOT / "subagents").resolve())
    except ValueError as exc:
        raise ValueError(f"refusing to write outside subagents: {out_path}") from exc
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if not args.check:
        parser.error("expected --check")

    report = build_report()
    write_report(report, args.out)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("Ghidra Building/ByteSprite animation signature correction")
        print(f"Status: {report['status']}")
        print(f"Targets: {report['targetCount']}")
        print(f"Renamed targets: {report['renamedTargets']}")
        print(f"Xref rows: {report['xrefRows']}")
        print(f"Instruction rows: {report['instructionRows']}")
        for failure in report["failures"]:
            print(f"- {failure}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
