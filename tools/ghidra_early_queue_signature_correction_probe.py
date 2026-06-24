#!/usr/bin/env python3
"""Validate the saved early-queue Ghidra signature/comment correction tranche."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "early-signature-queue-wave309" / "current"

TARGETS = {
    "0x00402dd0": {
        "name": "ShadowHeightfield__AnyBoundsCornerAboveSampledHeight",
        "signature": [
            "int",
            "__thiscall",
            "ShadowHeightfield__AnyBoundsCornerAboveSampledHeight",
            "void * this",
        ],
        "comment": ["ECX-backed object pointer", "eight attached-bounds", "runtime shadow behavior", "unproven"],
        "decompile": ["CStaticShadows__SampleShadowHeightBilinear", "+0x60", "+0xc0"],
        "instruction": ["0x00402dd0", "MOV", "ESI, ECX"],
    },
    "0x00403ff0": {
        "name": "CDXLandscape__DestroyResourceDescriptorArray_Thunk",
        "signature": [
            "void",
            "__thiscall",
            "CDXLandscape__DestroyResourceDescriptorArray_Thunk",
            "void * this",
        ],
        "comment": ["this+8", "0x41c", "CResourceDescriptor__dtor", "runtime behavior", "unproven"],
        "decompile": ["CDXLandscape__DestroyArrayWithCallback", "0x41c", "CResourceDescriptor__dtor"],
        "instruction": ["0x00403ff7", "ADD", "ECX, 0x8"],
    },
    "0x00404dd0": {
        "name": "CBattleEngine__Init",
        "signature": ["void", "__thiscall", "CBattleEngine__Init", "void * this", "void * init"],
        "comment": ["ret 0x4", "CBattleEngineInitThing", "walker/jet parts", "weapon_fire_breaks_stealth", "unproven"],
        "decompile": ["CBattleEngineWalkerPart__ctor", "CBattleEngineJetPart__ctor", "+0x5d4", "+0x5d8", "+0x5dc"],
        "instruction": ["0x004058f7", "RET", "0x4"],
    },
    "0x00405930": {
        "name": "CControllerDefinition__VFunc_03_00405930",
        "signature": ["int", "__thiscall", "CControllerDefinition__VFunc_03_00405930", "void * this"],
        "comment": ["vtable slot", "returns 0", "runtime control-remap behavior", "unproven"],
        "decompile": ["return 0"],
        "instruction": ["0x00405932", "RET"],
    },
    "0x004059a0": {
        "name": "CCylinder__VFunc_01_004059a0",
        "signature": [
            "int",
            "__thiscall",
            "CCylinder__VFunc_01_004059a0",
            "void * this",
            "void * forwardedA",
            "void * forwardedB",
            "void * dispatchObject",
            "void * forwardedC",
        ],
        "comment": ["ret 0x10", "dispatchObject vfunc +0x8", "exact CCylinder virtual contract", "unproven"],
        "decompile": ["dispatchObject", "+ 0x8"],
        "instruction": ["0x004059bd", "RET", "0x10"],
    },
    "0x00405d80": {
        "name": "CParticleManager__RemoveFromGlobalList_Thunk",
        "previous": ["CParticleManager__RemoveFromGlobalList"],
        "signature": ["void", "__fastcall", "CParticleManager__RemoveFromGlobalList_Thunk", "void * node"],
        "comment": ["jump thunk", "0x004cb050", "target signature", "runtime particle behavior", "unproven"],
        "decompile": ["CParticleManager__RemoveFromGlobalList"],
        "instruction": ["0x00405d80", "JMP", "0x004cb050"],
    },
    "0x00405db0": {
        "name": "VFuncSlot_12_00405db0",
        "signature": ["void", "__thiscall", "VFuncSlot_12_00405db0", "void * this", "void * arg1", "void * arg2"],
        "comment": ["no-op vtable slot", "ret 0x8", "owner table", "runtime behavior", "unproven"],
        "decompile": ["VFuncSlot_12_00405db0"],
        "instruction": ["0x00405db0", "RET", "0x8"],
    },
    "0x00406da0": {
        "name": "CBattleEngine__SelectNearestForwardTargetFromGlobalSet",
        "signature": [
            "void *",
            "__thiscall",
            "CBattleEngine__SelectNearestForwardTargetFromGlobalSet",
            "void * this",
            "void * profile",
            "float originX",
            "float originY",
            "float originZ",
            "float originW",
            "float rangeScale",
        ],
        "comment": ["ret 0x18", "global target set", "+0x294", "weapon_fire_breaks_stealth", "unproven"],
        "decompile": [
            "CBattleEngine__IsWeaponModeCompatibleWithMountState",
            "CBattleEngine__DoesTargetMaskMatchProfileByDistance",
            "CSPtrSet__First",
        ],
        "instruction": ["0x00406fae", "RET", "0x18"],
    },
    "0x004cb050": {
        "name": "CParticleManager__RemoveFromGlobalList",
        "signature": ["void", "__fastcall", "CParticleManager__RemoveFromGlobalList", "void * node"],
        "comment": ["global particle-manager linked list", "0x0082b3e8", "node", "runtime particle behavior", "unproven"],
        "decompile": ["0x0082b3e8"],
        "instruction": ["0x004cb060", "RET"],
    },
}

DEFAULT_DRY = BASE / "signature_correction_dry.log"
DEFAULT_APPLY = BASE / "signature_correction_apply.log"
DEFAULT_METADATA = BASE / "metadata_final.tsv"
DEFAULT_INDEX = BASE / "decompile_final" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_final"
DEFAULT_XREFS = BASE / "xrefs_final.tsv"
DEFAULT_INSTRUCTIONS = BASE / "instructions_final.tsv"
DEFAULT_OUT = BASE / "early-queue-signature-correction.json"

OVERCLAIM_TOKENS = [
    "runtime behavior proven",
    "source identity proven",
    "exact source identity proven",
    "weapon_fire_breaks_stealth closed",
    "weapon-fired stealth reset proven",
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
    expected_renamed = 1

    if dry_summary != {"updated": 0, "skipped": expected_count, "renamed": 0, "missing": 0, "bad": 0}:
        failures.append(f"unexpected dry summary: {dry_summary}")
    if apply_summary != {"updated": expected_count, "skipped": 0, "renamed": expected_renamed, "missing": 0, "bad": 0}:
        failures.append(f"unexpected apply summary: {apply_summary}")

    stale_param_hits = 0
    comment_overclaims = 0
    xref_count = len(xref_rows)
    instruction_count = len(instruction_rows)

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

    thunk_row = find_row(metadata_rows, "address", "0x00405d80")
    target_row = find_row(metadata_rows, "address", "0x004cb050")
    if thunk_row and target_row and thunk_row.get("name") == target_row.get("name"):
        failures.append("particle thunk and target still share the same function name")

    report = {
        "status": "PASS" if not failures else "FAIL",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "classification": "early-queue-signature-comment-correction",
        "summary": {
            "targets": expected_count,
            "renamedTargets": apply_summary.get("renamed", -1),
            "signatureHardenedTargets": apply_summary.get("updated", -1),
            "staleParamSignatureHits": stale_param_hits,
            "commentOverclaims": comment_overclaims,
            "xrefRows": xref_count,
            "instructionRows": instruction_count,
            "weaponFiredStealthStatus": "unresolved",
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
        "early queue signature correction: "
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
