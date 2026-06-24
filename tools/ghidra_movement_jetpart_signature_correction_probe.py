#!/usr/bin/env python3
"""Validate the saved movement/JetPart Ghidra correction tranche."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "movement-terrain-queue-tranche" / "current"

TARGETS = {
    "0x00411630": {
        "name": "CMonitor__IntegrateMovementAgainstTerrain",
        "previous": [],
        "signature": ["void", "__thiscall", "CMonitor__IntegrateMovementAgainstTerrain", "void * this"],
        "comment": ["Signature hardening", "terrain/static-shadow", "Vec3", "runtime behavior", "remain unproven"],
        "decompile": ["monitor", "CStaticShadows__SampleShadowHeightBilinear", "Vec3__Cross", "+0x280", "+0x27c"],
        "xrefs": ["CMonitor__UpdateMovementTransitionAndEffects"],
        "ret": "",
    },
    "0x00411a60": {
        "name": "Vec3__Cross",
        "previous": [],
        "signature": ["void", "__thiscall", "Vec3__Cross", "void * this", "void * outCross", "void * rhs"],
        "forbiddenSignature": ["param_", "void * param_3"],
        "comment": ["Signature hardening", "ret 0x8", "this x rhs", "outCross"],
        "decompile": ["outCross", "rhs", "*outCross"],
        "xrefs": ["CMonitor__IntegrateMovementAgainstTerrain", "CMCBuggy__UpdateWheel", "CMeshCollisionVolume__ResolveContactNormalAndPlane"],
        "ret": "0x8",
    },
    "0x00411aa0": {
        "name": "CMonitor__ComputeTerrainVelocityScalar",
        "previous": [],
        "signature": ["float", "__thiscall", "CMonitor__ComputeTerrainVelocityScalar", "void * this"],
        "forbiddenSignature": ["double", "param_"],
        "comment": ["Signature hardening", "terrain/static-shadow", "velocity", "runtime behavior", "remain unproven"],
        "decompile": ["monitor", "CStaticShadows__SampleShadowHeightBilinear", "SQRT"],
        "xrefs": ["CMonitor__UpdateMovementTransitionAndEffects"],
        "ret": "",
    },
    "0x00411b70": {
        "name": "CBattleEngineJetPart__IsStateMachineActive",
        "previous": ["CGeneralVolume__IsStateMachineActive"],
        "signature": ["int", "__thiscall", "CBattleEngineJetPart__IsStateMachineActive", "void * this"],
        "comment": ["Owner/signature correction", "+0x57c", "+0x2c", "+0x48", "remain unproven"],
        "decompile": ["+0x2c", "+0x48"],
        "xrefs": ["CBattleEngine__Morph"],
        "ret": "",
    },
    "0x00411e70": {
        "name": "CBattleEngineJetPart__ChangeWeapon",
        "previous": ["CCockpit__CycleToNextUsableWeapon"],
        "signature": ["void", "__thiscall", "CBattleEngineJetPart__ChangeWeapon", "void * this"],
        "comment": ["Owner/signature correction", "CBattleEngineJetPart::ChangeWeapon", "+0x57c", "runtime weapon switching", "unproven"],
        "decompile": ["CSPtrSet__First", "+0x55c", "+0x52c", "+0x588", "CGeneralVolume__SetParam2CC_ToOne"],
        "xrefs": ["CBattleEngine__ChangeWeapon"],
        "ret": "",
    },
    "0x00412000": {
        "name": "CBattleEngineJetPart__LoseWeaponCharge",
        "previous": ["CMonitor__ClearTrackedEntryFlag60ByIndex"],
        "signature": ["void", "__thiscall", "CBattleEngineJetPart__LoseWeaponCharge", "void * this"],
        "comment": ["Owner/signature correction", "CBattleEngine::Morph", "+0x57c", "+0x60", "remain unproven"],
        "decompile": ["+0x60"],
        "xrefs": ["CBattleEngine__Morph", "CBattleEngine__AugmentWeapon"],
        "ret": "",
    },
    "0x00412050": {
        "name": "CBattleEngineJetPart__WeaponFired",
        "previous": ["CEngine__ProcessBurstQuotaInPrimaryEntrySet"],
        "signature": ["int", "__thiscall", "CBattleEngineJetPart__WeaponFired", "void * this", "void * weapon"],
        "forbiddenSignature": ["param_", "int param_2"],
        "comment": ["Owner/signature correction", "WeaponFired", "+0x57c", "stealth reset", "does not prove"],
        "decompile": ["weapon", "+0x55c", "+0x52c", "+0x544", "CEngine__ClampBurstStartTimeFloorNow"],
        "xrefs": ["CBattleEngine__CanSpawnBurstForResolvedEntry"],
        "ret": "0x4",
    },
    "0x004121b0": {
        "name": "CBattleEngineJetPart__GetWeaponAmmoPercentage",
        "previous": ["CGeneralVolume__EntryIterator_GetSlotFillRatio"],
        "signature": ["float", "__thiscall", "CBattleEngineJetPart__GetWeaponAmmoPercentage", "void * this"],
        "forbiddenSignature": ["double", "param_"],
        "comment": ["Owner/signature correction", "GetWeaponAmmoPercentage", "+0x57c", "+0x52c", "+0x88"],
        "decompile": ["+0x52c", "+0x88"],
        "xrefs": ["CBattleEngine__GetWeaponAmmoPercentage"],
        "ret": "",
    },
    "0x004122b0": {
        "name": "CBattleEngineJetPart__IsWeaponOverheated",
        "previous": ["CGeneralVolume__EntryIterator_GetSlotFlag_55C"],
        "signature": ["int", "__thiscall", "CBattleEngineJetPart__IsWeaponOverheated", "void * this"],
        "comment": ["Owner/signature correction", "IsWeaponOverheated", "+0x57c", "+0x55c"],
        "decompile": ["+0x55c"],
        "xrefs": ["CBattleEngine__IsWeaponOverheated"],
        "ret": "",
    },
    "0x00412310": {
        "name": "CBattleEngineJetPart__IsEnergyWeapon",
        "previous": ["CGeneralVolume__EntryIterator_GetSlotFlag_544"],
        "signature": ["int", "__thiscall", "CBattleEngineJetPart__IsEnergyWeapon", "void * this"],
        "comment": ["Owner/signature correction", "IsEnergyWeapon", "+0x57c", "+0x544"],
        "decompile": ["+0x544"],
        "xrefs": ["CBattleEngine__IsEnergyWeapon"],
        "ret": "",
    },
    "0x00412370": {
        "name": "CBattleEngineJetPart__GetWeaponCharge",
        "previous": ["CGeneralVolume__EntryIterator_GetDistanceProgressRatio"],
        "signature": ["float", "__thiscall", "CBattleEngineJetPart__GetWeaponCharge", "void * this"],
        "forbiddenSignature": ["double", "param_"],
        "comment": ["Owner/signature correction", "GetWeaponCharge", "+0x57c", "+0x60", "remain unproven"],
        "decompile": ["+0x60", "500"],
        "xrefs": ["CBattleEngine__GetWeaponCharge"],
        "ret": "",
    },
    "0x00412480": {
        "name": "CBattleEngineJetPart__GetWeaponPhysicsName",
        "previous": ["CGeneralVolume__EntryIterator_GetModeId"],
        "signature": ["char *", "__thiscall", "CBattleEngineJetPart__GetWeaponPhysicsName", "void * this"],
        "comment": ["Owner/signature correction", "GetWeaponPhysicsName", "+0x57c", "+0x00"],
        "decompile": ["+0xa4"],
        "xrefs": ["CBattleEngine__GetWeaponPhysicsName"],
        "ret": "",
    },
    "0x004124d0": {
        "name": "CBattleEngineJetPart__GetCurrentWeaponNameField04",
        "previous": ["CGeneralVolume__GetSelectedWeaponDef"],
        "signature": ["char *", "__thiscall", "CBattleEngineJetPart__GetCurrentWeaponNameField04", "void * this"],
        "comment": ["Owner/signature correction", "CBattleEngine__ChangeWeapon", "+0x57c", "+0x04", "remain unproven"],
        "decompile": ["+0xa4", "+4"],
        "xrefs": ["CBattleEngine__ChangeWeapon"],
        "ret": "",
    },
    "0x00412520": {
        "name": "CBattleEngineJetPart__GetWeaponIconName",
        "previous": ["CGeneralVolume__EntryIterator_GetIndexedEntryFieldA4_38"],
        "signature": ["char *", "__thiscall", "CBattleEngineJetPart__GetWeaponIconName", "void * this"],
        "comment": ["Owner/signature correction", "GetWeaponIconName", "+0x57c", "+0x38"],
        "decompile": ["+0xa4", "+0x38"],
        "xrefs": ["CBattleEngine__GetWeaponIconName"],
        "ret": "",
    },
    "0x00412570": {
        "name": "CBattleEngineJetPart__CanWeaponFire",
        "previous": ["CBattleEngine__IsIndexedEntryUsable"],
        "signature": ["int", "__thiscall", "CBattleEngineJetPart__CanWeaponFire", "void * this"],
        "comment": ["Owner/signature correction", "CanWeaponFire", "does not prove", "fire-while-cloaked"],
        "decompile": ["+0x55c", "+0x52c", "+0x544"],
        "xrefs": ["CBattleEngine__UpdateAutoTargetSetAndFireProjectiles"],
        "ret": "",
    },
    "0x00412610": {
        "name": "CBattleEngineJetPart__GetCurrentWeapon",
        "previous": ["CBattleEngine__GetIndexedEntry"],
        "signature": ["void *", "__thiscall", "CBattleEngineJetPart__GetCurrentWeapon", "void * this"],
        "comment": ["Owner/signature correction", "GetCurrentWeapon", "+0x57c", "remain unproven"],
        "decompile": ["return", "+0x10"],
        "xrefs": ["CBattleEngine__UpdateAutoTargetSetAndFireProjectiles", "CBattleEngine__IsCurrentResolvedEntry"],
        "ret": "",
    },
}

DEFAULT_RENAME_DRY = BASE / "rename_dry.log"
DEFAULT_RENAME_APPLY = BASE / "rename_apply.log"
DEFAULT_SIGNATURE_DRY = BASE / "signature_dry.log"
DEFAULT_SIGNATURE_APPLY = BASE / "signature_apply.log"
DEFAULT_METADATA = BASE / "metadata_final.tsv"
DEFAULT_INDEX = BASE / "decompile_final" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_final"
DEFAULT_XREFS = BASE / "xrefs_final.tsv"
DEFAULT_INSTRUCTIONS = BASE / "instructions_final.tsv"
DEFAULT_OUT = BASE / "movement-jetpart-signature-correction.json"

OVERCLAIMS = [
    "runtime behavior proven",
    "exact source identity proven",
    "concrete layout proven",
    "weapon_fire_breaks_stealth closed",
    "fire-while-cloaked proven",
    "fully re'ed",
]


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def relative(path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def normalize_address(value: str) -> str:
    value = (value or "").strip().lower()
    if value in {"", "<none>", "<no_function>"}:
        return value
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def compact(value: str) -> str:
    return "".join((value or "").lower().split())


def token_present(text: str, token: str) -> bool:
    return compact(token) in compact(text)


def read_text(path: Path | None) -> str:
    if path is None or not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def unescape_tsv(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


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


def parse_rename_summary(log_text: str) -> dict[str, int]:
    match = re.search(r"updated=(\d+)\s+skipped=(\d+)\s+missing=(\d+)\s+bad=(\d+)", log_text)
    if match:
        return {
            "updated": int(match.group(1)),
            "skipped": int(match.group(2)),
            "missing": int(match.group(3)),
            "bad": int(match.group(4)),
        }
    match = re.search(r"applied=(\d+)\s+skipped=(\d+)\s+missing=(\d+)\s+bad=(\d+)", log_text)
    if match:
        return {
            "updated": int(match.group(1)),
            "skipped": int(match.group(2)),
            "missing": int(match.group(3)),
            "bad": int(match.group(4)),
        }
    return parse_update_summary(log_text)


def metadata_map(path: Path) -> dict[str, dict[str, str]]:
    rows = read_tsv(path)
    out = {}
    for row in rows:
        row["address"] = normalize_address(row.get("address", ""))
        row["comment"] = unescape_tsv(row.get("comment", ""))
        out[row["address"]] = row
    return out


def index_map(path: Path) -> dict[str, dict[str, str]]:
    return {normalize_address(row.get("address", "")): row for row in read_tsv(path)}


def decompile_file(decompile_dir: Path, address: str) -> Path | None:
    if not decompile_dir.is_dir():
        return None
    matches = sorted(decompile_dir.glob(f"{normalize_address(address)[2:]}_*.c"))
    return matches[0] if matches else None


def build_report(
    *,
    rename_dry_log_path: Path = DEFAULT_RENAME_DRY,
    rename_apply_log_path: Path = DEFAULT_RENAME_APPLY,
    signature_dry_log_path: Path = DEFAULT_SIGNATURE_DRY,
    signature_apply_log_path: Path = DEFAULT_SIGNATURE_APPLY,
    metadata_path: Path = DEFAULT_METADATA,
    decompile_index_path: Path = DEFAULT_INDEX,
    decompile_dir: Path = DEFAULT_DECOMPILE_DIR,
    xrefs_path: Path = DEFAULT_XREFS,
    instructions_path: Path = DEFAULT_INSTRUCTIONS,
) -> dict[str, object]:
    rename_dry_log_path = resolve(rename_dry_log_path)
    rename_apply_log_path = resolve(rename_apply_log_path)
    signature_dry_log_path = resolve(signature_dry_log_path)
    signature_apply_log_path = resolve(signature_apply_log_path)
    metadata_path = resolve(metadata_path)
    decompile_index_path = resolve(decompile_index_path)
    decompile_dir = resolve(decompile_dir)
    xrefs_path = resolve(xrefs_path)
    instructions_path = resolve(instructions_path)

    failures: list[str] = []
    rename_dry = parse_rename_summary(read_text(rename_dry_log_path))
    rename_apply = parse_rename_summary(read_text(rename_apply_log_path))
    signature_dry = parse_update_summary(read_text(signature_dry_log_path))
    signature_apply = parse_update_summary(read_text(signature_apply_log_path))
    target_count = len(TARGETS)
    rename_count = sum(1 for target in TARGETS.values() if target.get("previous"))

    if rename_dry != {"updated": 0, "skipped": rename_count, "missing": 0, "bad": 0}:
        failures.append(f"rename dry summary unexpected: {rename_dry}")
    if rename_apply != {"updated": rename_count, "skipped": 0, "missing": 0, "bad": 0}:
        failures.append(f"rename apply summary unexpected: {rename_apply}")
    if signature_dry != {"updated": 0, "skipped": target_count, "missing": 0, "bad": 0}:
        failures.append(f"signature dry summary unexpected: {signature_dry}")
    if signature_apply != {"updated": target_count, "skipped": 0, "missing": 0, "bad": 0}:
        failures.append(f"signature apply summary unexpected: {signature_apply}")

    metadata = metadata_map(metadata_path)
    index = index_map(decompile_index_path)
    xrefs = read_tsv(xrefs_path)
    instructions = read_tsv(instructions_path)

    stale_name_hits = 0
    param_signature_hits = 0
    comment_overclaims = 0
    ret_evidence_hits = 0
    xref_evidence_hits = 0
    decompile_evidence_hits = 0

    for address, expected in TARGETS.items():
        row = metadata.get(address)
        if not row:
            failures.append(f"{address}: missing metadata row")
            continue
        if row.get("name") != expected["name"]:
            failures.append(f"{address}: name mismatch {row.get('name')} != {expected['name']}")
        signature = row.get("signature", "")
        for token in expected["signature"]:
            if not token_present(signature, token):
                failures.append(f"{address}: signature missing token {token!r}: {signature}")
        forbidden = ["param_"] + expected.get("forbiddenSignature", [])
        for token in forbidden:
            if token and token_present(signature, token):
                param_signature_hits += 1
                failures.append(f"{address}: forbidden signature token remains {token!r}: {signature}")
        for previous in expected.get("previous", []):
            if previous and token_present(row.get("name", ""), previous):
                stale_name_hits += 1
                failures.append(f"{address}: stale previous name remains in metadata: {previous}")

        comment = row.get("comment", "")
        for token in expected["comment"]:
            if not token_present(comment, token):
                failures.append(f"{address}: comment missing token {token!r}")
        for token in OVERCLAIMS:
            if token_present(comment, token):
                comment_overclaims += 1
                failures.append(f"{address}: runtime/source overclaim token present: {token!r}")

        index_row = index.get(address)
        if not index_row:
            failures.append(f"{address}: missing decompile index row")
        elif index_row.get("name") != expected["name"]:
            stale_name_hits += 1
            failures.append(f"{address}: decompile index name mismatch {index_row.get('name')} != {expected['name']}")

        dec_path = decompile_file(decompile_dir, address)
        dec_text = read_text(dec_path)
        if not dec_text:
            failures.append(f"{address}: missing decompile text")
        elif all(token_present(dec_text, token) for token in expected["decompile"]):
            decompile_evidence_hits += 1
        else:
            missing = [token for token in expected["decompile"] if not token_present(dec_text, token)]
            failures.append(f"{address}: decompile missing tokens: {missing}")

        target_xrefs = [row for row in xrefs if normalize_address(row.get("target_addr", "")) == address]
        found_xref = False
        for token in expected["xrefs"]:
            if any(token_present(row.get("from_function", ""), token) for row in target_xrefs):
                found_xref = True
            else:
                failures.append(f"{address}: xref missing caller token {token!r}")
        if found_xref:
            xref_evidence_hits += 1

        ret_operand = expected.get("ret", "")
        if ret_operand:
            if any(
                normalize_address(row.get("target_addr", "")) == address
                and normalize_address(row.get("function_entry", "")) == address
                and row.get("mnemonic") == "RET"
                and token_present(row.get("operands", ""), ret_operand)
                for row in instructions
            ):
                ret_evidence_hits += 1
            else:
                failures.append(f"{address}: missing RET evidence {ret_operand}")

    summary = {
        "targets": target_count,
        "renamedTargets": rename_count,
        "staleNameHits": stale_name_hits,
        "paramSignatureHits": param_signature_hits,
        "commentOverclaims": comment_overclaims,
        "retEvidenceHits": ret_evidence_hits,
        "xrefEvidenceHits": xref_evidence_hits,
        "decompileEvidenceHits": decompile_evidence_hits,
        "renameDry": rename_dry,
        "renameApply": rename_apply,
        "signatureDry": signature_dry,
        "signatureApply": signature_apply,
    }
    return {
        "schema": "ghidra-movement-jetpart-signature-correction-probe.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not failures else "FAIL",
        "summary": summary,
        "targets": {address: {"name": target["name"], "previous": target.get("previous", [])} for address, target in TARGETS.items()},
        "artifacts": {
            "renameDryLog": relative(rename_dry_log_path),
            "renameApplyLog": relative(rename_apply_log_path),
            "signatureDryLog": relative(signature_dry_log_path),
            "signatureApplyLog": relative(signature_apply_log_path),
            "metadata": relative(metadata_path),
            "decompileIndex": relative(decompile_index_path),
            "decompileDir": relative(decompile_dir),
            "xrefs": relative(xrefs_path),
            "instructions": relative(instructions_path),
        },
        "whatIsProven": [
            "The saved Ghidra project has the checked names, signatures, comments, xrefs, and decompile evidence for the movement/JetPart tranche.",
            "The stale GeneralVolume/Cockpit/CEngine/CMonitor/CBattleEngine owner labels checked by this probe were replaced for the selected +0x57c JetPart weapon helpers.",
            "The probe records source/caller/decompile alignment only; it does not prove runtime gameplay behavior.",
        ],
        "notProven": [
            "This does not complete all Ghidra functions.",
            "This does not prove exact C++ layouts, local variables, tags, runtime cloak activation, fire-while-cloaked behavior, or rebuild parity.",
            "This does not close weapon_fire_breaks_stealth.",
        ],
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Exit non-zero if validation fails.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Write JSON report here.")
    args = parser.parse_args()

    report = build_report()
    out_path = resolve(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        f"movement jetpart signature correction: {report['status']} "
        f"targets={report['summary']['targets']} renamed={report['summary']['renamedTargets']} "
        f"failures={len(report['failures'])} out={relative(out_path)}"
    )
    if args.check and report["status"] != "PASS":
        for failure in report["failures"][:20]:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
