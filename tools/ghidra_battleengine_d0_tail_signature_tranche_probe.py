#!/usr/bin/env python3
"""Validate the BattleEngine D0-tail saved-Ghidra signature/name tranche."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "battleengine-d0-tail-signature-tranche" / "current"

TARGETS = {
    "0x0040d0f0": {
        "name": "CWeaponStatement__UsesBallisticArcNoLocks",
        "previousName": "CEngine__CanUseBallisticArcNoLocks",
        "signatureTokens": ["int", "__thiscall", "CWeaponStatement__UsesBallisticArcNoLocks", "void * weaponStatement"],
        "commentTokens": ["Owner/name correction", "weapon-definition", "gravity", "+0x50/+0x6c", "not runtime weapon-fire"],
        "decompileTokens": ["CWeaponStatement__UsesBallisticArcNoLocks", "+ 0x3c", "+ 0x50", "+ 0x6c"],
        "xrefFunctions": [
            "CUnit__ComputeMinBallisticTravelDistance",
            "CUnit__ComputeMaxBallisticTravelDistance",
            "OID__CanFireAtTarget_BallisticArcA",
            "OID__UpdateAimTransformAndAttachTargetReader",
        ],
        "instructionTokens": ["FLD", "[ECX + 0x3c]", "JNZ", "RET"],
    },
    "0x0040d470": {
        "name": "CLine__ctor_fromEndpoints",
        "previousName": "CGeneralVolume__ctor_like_0040d470",
        "signatureTokens": ["void", "__thiscall", "CLine__ctor_fromEndpoints", "void * this", "void * startPoint", "void * endPoint"],
        "commentTokens": ["Owner/name correction", "CLine vtable", "CGeneralVolume base vtable", "two 16-byte endpoint/vector blocks", "runtime collision behavior remain unproven"],
        "decompileTokens": ["CLine__ctor_fromEndpoints", "PTR_VFuncSlot_00_00426340_005d8bfc"],
        "xrefFunctions": [],
        "instructionTokens": ["MOV", "0x5d892c", "MOV", "0x5d8bfc", "RET", "0x8"],
    },
    "0x0040da30": {
        "name": "CBattleEngine__BuildInterpolatedWorldTransform",
        "previousName": "CExplosionInitThing__BuildInterpolatedWorldTransform",
        "signatureTokens": ["void *", "__thiscall", "CBattleEngine__BuildInterpolatedWorldTransform", "void * this", "void * outWorldTransform", "void * unusedContext"],
        "commentTokens": ["Owner/name correction", "target-marker caller", "BattleEngine world transform", "runtime render behavior remain unproven"],
        "decompileTokens": ["CBattleEngine__BuildInterpolatedWorldTransform", "Vec3__SubtractToOut", "CSquadNormal__BuildOrientationMatrixFromEuler", "CMCBuggy__MultiplyMat34Basis"],
        "xrefFunctions": ["CExplosionInitThing__RenderTargetMarkers3D"],
        "instructionTokens": ["SUB", "0x138", "[ESI + 0x1c]", "[ESI + 0x8c]"],
    },
    "0x0040dc90": {
        "name": "CBattleEngine__CountFlag9CBySelectionMode",
        "previousName": "CExplosionInitThing__CountFlag9CBySelectionMode",
        "signatureTokens": ["int", "__thiscall", "CBattleEngine__CountFlag9CBySelectionMode", "void * this"],
        "commentTokens": ["Owner/name correction", "tail-calls LinkedObjectList__CountFlag9C", "+0x260 == 3", "+0x57c", "+0x578", "not objective completion runtime proof"],
        "decompileTokens": ["CBattleEngine__CountFlag9CBySelectionMode", "LinkedObjectList__CountFlag9C", "LinkedObjectList__CountFlag9C_IncludingExtra", "+ 0x260", "+ 0x57c", "+ 0x578"],
        "xrefFunctions": ["CExplosionInitThing__RenderObjectiveStatusPanel"],
        "instructionTokens": ["CMP", "[ECX + 0x260]", "JMP", "0x004129a0", "JMP", "0x00414b70"],
    },
    "0x0040dcb0": {
        "name": "CBattleEngine__SetFlag58CEnabled",
        "previousName": "CCockpit__SetFlag58C_Enabled",
        "signatureTokens": ["void", "__thiscall", "CBattleEngine__SetFlag58CEnabled", "void * this"],
        "commentTokens": ["Owner correction", "writes 1 to +0x58c", "+0x260/+0x58c transition-selection context", "runtime behavior remain unproven"],
        "decompileTokens": ["CBattleEngine__SetFlag58CEnabled", "+ 0x58c", "= 1"],
        "xrefFunctions": [],
        "instructionTokens": ["MOV", "[ECX + 0x58c]", "0x1", "RET"],
    },
    "0x0040dce0": {
        "name": "CBattleEngine__HostileEnvironment",
        "previousName": "CBattleEngine__HostileEnvironment",
        "signatureTokens": ["void", "__thiscall", "CBattleEngine__HostileEnvironment", "void * this"],
        "commentTokens": ["Source bridge", "CBattleEngine::HostileEnvironment", "hud_hostile_environment", "mLastTimeInHostileEnviroment", "not runtime HUD audio proof"],
        "decompileTokens": ["CBattleEngine__HostileEnvironment", "CBattleEngine__FindSoundEventByNameIfEnabled", "CMonitor__PlayRandomSampleFromChain", "CConsole__Printf", "+ 0x510", "DAT_00672fd0"],
        "xrefFunctions": ["CMonitor__ApplyHostileEnvironmentPenalty"],
        "instructionTokens": ["FLD", "0x00672fd0", "CALL", "0x004e1910", "CALL", "0x004e1940"],
    },
}

DEFAULT_SIGNATURE_DRY = BASE / "signature_dry.log"
DEFAULT_SIGNATURE_APPLY = BASE / "signature_apply.log"
DEFAULT_METADATA = BASE / "metadata_readback.tsv"
DEFAULT_INDEX = BASE / "decompile_readback" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_readback"
DEFAULT_XREFS = BASE / "xrefs_readback.tsv"
DEFAULT_INSTRUCTIONS = BASE / "instructions_readback.tsv"
DEFAULT_VTABLES = BASE / "vtable_types_pre.tsv"
DEFAULT_OUT = BASE / "battleengine-d0-tail-signature-tranche.json"

OVERCLAIM_TOKENS = [
    "runtime behavior proven",
    "runtime weapon-fire proven",
    "runtime hud audio proof confirmed",
    "exact source identity proven",
    "weapon_fire_breaks_stealth closed",
    "objective completion proven",
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


def parse_update_summary(log_text: str) -> dict[str, int]:
    match = re.search(r"updated=(\d+)\s+skipped=(\d+)\s+missing=(\d+)\s+bad=(\d+)", log_text)
    if not match:
        return {"updated": -1, "skipped": -1, "missing": -1, "bad": -1}
    return {
        "updated": int(match.group(1)),
        "skipped": int(match.group(2)),
        "missing": int(match.group(3)),
        "bad": int(match.group(4)),
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


def joined_instruction_text(rows: list[dict[str, str]], address: str) -> str:
    wanted = normalize_address(address)
    parts: list[str] = []
    for row in rows:
        if normalize_address(row.get("target_addr", "")) == wanted:
            parts.extend(row.values())
    return " ".join(parts)


def xref_callers(rows: list[dict[str, str]], address: str) -> set[str]:
    wanted = normalize_address(address)
    return {
        row.get("from_function", "")
        for row in rows
        if normalize_address(row.get("target_addr", "")) == wanted
    }


def build_report(
    *,
    signature_dry_log_path: Path = DEFAULT_SIGNATURE_DRY,
    signature_apply_log_path: Path = DEFAULT_SIGNATURE_APPLY,
    metadata_path: Path = DEFAULT_METADATA,
    decompile_index_path: Path = DEFAULT_INDEX,
    decompile_dir: Path = DEFAULT_DECOMPILE_DIR,
    xrefs_path: Path = DEFAULT_XREFS,
    instructions_path: Path = DEFAULT_INSTRUCTIONS,
    vtables_path: Path = DEFAULT_VTABLES,
) -> dict[str, object]:
    signature_dry_log_path = resolve(signature_dry_log_path)
    signature_apply_log_path = resolve(signature_apply_log_path)
    metadata_path = resolve(metadata_path)
    decompile_index_path = resolve(decompile_index_path)
    decompile_dir = resolve(decompile_dir)
    xrefs_path = resolve(xrefs_path)
    instructions_path = resolve(instructions_path)
    vtables_path = resolve(vtables_path)

    failures: list[str] = []
    for label, path in (
        ("signature dry log", signature_dry_log_path),
        ("signature apply log", signature_apply_log_path),
        ("metadata read-back", metadata_path),
        ("decompile index", decompile_index_path),
        ("xref read-back", xrefs_path),
        ("instruction read-back", instructions_path),
        ("vtable type read-back", vtables_path),
    ):
        if not path.is_file():
            failures.append(f"missing {label}: {relative(path)}")
    if not decompile_dir.is_dir():
        failures.append(f"missing decompile dir: {relative(decompile_dir)}")

    dry_summary = parse_update_summary(read_text(signature_dry_log_path))
    apply_summary = parse_update_summary(read_text(signature_apply_log_path))
    if dry_summary != {"updated": 0, "skipped": 6, "missing": 0, "bad": 0}:
        failures.append("signature dry summary is not clean")
    if apply_summary != {"updated": 6, "skipped": 0, "missing": 0, "bad": 0}:
        failures.append("signature apply summary is not clean")

    metadata_rows = read_tsv(metadata_path)
    index_rows = read_tsv(decompile_index_path)
    xref_rows = read_tsv(xrefs_path)
    instruction_rows = read_tsv(instructions_path)
    vtable_text = read_text(vtables_path)

    if not all(token_present(vtable_text, token) for token in ("CGeneralVolume", "CLine", "005d892c", "005d8bfc")):
        failures.append("vtable type read-back does not contain expected CGeneralVolume and CLine rows")

    target_reports: list[dict[str, object]] = []
    comment_overclaims = 0
    corrected_names = 0
    hardened_signatures = 0
    for address, expected in TARGETS.items():
        row = find_row(metadata_rows, "address", address)
        index_row = find_row(index_rows, "address", address)
        if row is None:
            failures.append(f"metadata missing {address}")
            continue

        name = row.get("name", "")
        signature = row.get("signature", "")
        comment = row.get("comment", "")
        if name != expected["name"] or row.get("status") != "OK":
            failures.append(f"metadata name/status mismatch for {address}")
        if expected["previousName"] != expected["name"] and name == expected["name"]:
            corrected_names += 1
        if "param_" not in signature and "undefined" not in signature.lower():
            hardened_signatures += 1

        missing_signature_tokens = [token for token in expected["signatureTokens"] if not token_present(signature, token)]
        if missing_signature_tokens:
            failures.append(f"signature tokens missing at {address}: {missing_signature_tokens}")

        missing_comment_tokens = [token for token in expected["commentTokens"] if not token_present(comment, token)]
        if missing_comment_tokens:
            failures.append(f"comment tokens missing at {address}: {missing_comment_tokens}")
        if any(token in comment.lower() for token in OVERCLAIM_TOKENS):
            comment_overclaims += 1
            failures.append(f"runtime/source overclaim in comment at {address}")

        if index_row is None or index_row.get("name") != expected["name"] or index_row.get("status") != "OK":
            failures.append(f"decompile index mismatch for {address}")
        decompile_file = decompile_file_for(decompile_dir, address)
        decompile_text = read_text(decompile_file) if decompile_file else ""
        if not decompile_file:
            failures.append(f"missing decompile file for {address}")
        else:
            missing_decompile_tokens = [token for token in expected["decompileTokens"] if not token_present(decompile_text, token)]
            if missing_decompile_tokens:
                failures.append(f"decompile tokens missing at {address}: {missing_decompile_tokens}")

        callers = xref_callers(xref_rows, address)
        missing_callers = [caller for caller in expected["xrefFunctions"] if caller not in callers]
        if missing_callers:
            failures.append(f"xref callers missing at {address}: {missing_callers}")

        instruction_text = joined_instruction_text(instruction_rows, address)
        missing_instruction_tokens = [token for token in expected["instructionTokens"] if not token_present(instruction_text, token)]
        if missing_instruction_tokens:
            failures.append(f"instruction tokens missing at {address}: {missing_instruction_tokens}")

        target_reports.append(
            {
                "address": address,
                "name": name,
                "previousName": expected["previousName"],
                "signature": signature,
                "commentPresent": bool(comment),
                "decompileFile": relative(decompile_file) if decompile_file else None,
                "xrefCallers": sorted(callers),
            }
        )

    status = "PASS" if not failures else "FAIL"
    return {
        "status": status,
        "checkedAt": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "targets": len(TARGETS),
            "correctedNames": corrected_names,
            "hardenedSignatures": hardened_signatures,
            "commentOverclaims": comment_overclaims,
            "drySummary": dry_summary,
            "applySummary": apply_summary,
        },
        "paths": {
            "signatureDryLog": relative(signature_dry_log_path),
            "signatureApplyLog": relative(signature_apply_log_path),
            "metadata": relative(metadata_path),
            "decompileIndex": relative(decompile_index_path),
            "decompileDir": relative(decompile_dir),
            "xrefs": relative(xrefs_path),
            "instructions": relative(instructions_path),
            "vtables": relative(vtables_path),
        },
        "targets": target_reports,
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Return non-zero when validation fails.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    report = build_report()
    out_path = resolve(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"Status: {report['status']}")
    print(f"Targets: {report['summary']['targets']}")
    print(f"Corrected names: {report['summary']['correctedNames']}")
    print(f"Hardened signatures: {report['summary']['hardenedSignatures']}")
    print(f"Report: {relative(out_path)}")
    if report["failures"]:
        for failure in report["failures"]:
            print(f"FAIL: {failure}")
    return 1 if args.check and report["status"] != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
