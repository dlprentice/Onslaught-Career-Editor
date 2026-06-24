#!/usr/bin/env python3
"""Validate the BattleEngine volume/augment/pickup saved-Ghidra signature tranche."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "battleengine-volume-augment-pickup-signature-tranche" / "current"

TARGETS = {
    "0x0040dc30": {
        "name": "CBattleEngine__EnableVolumeEntryGroupsByName",
        "previousName": "CExplosionInitThing__EnableVolumeEntryGroupsByName",
        "signatureTokens": ["void", "__thiscall", "CBattleEngine__EnableVolumeEntryGroupsByName", "void * this", "void * entryName"],
        "commentTokens": ["Owner/name correction", "BattleEngine volume-entry group", "CGeneralVolume__EnableEntriesByName", "+0x578", "+0x57c", "runtime behavior remain unproven"],
        "decompileTokens": ["CBattleEngine__EnableVolumeEntryGroupsByName", "CGeneralVolume__EnableEntriesByName", "CGeneralVolume__EnableLinkedEntriesByName", "+ 0x578", "+ 0x57c"],
        "xrefTokens": ["005d8b5c", "DATA"],
        "instructionTokens": ["[ESI + 0x578]", "CALL", "0x00414970", "[ESI + 0x57c]", "0x004127a0", "RET", "0x4"],
    },
    "0x0040dc60": {
        "name": "CBattleEngine__DisableVolumeEntryGroupsByNameAndReselect",
        "previousName": "CExplosionInitThing__DisableVolumeEntryGroupsByNameAndReselect",
        "signatureTokens": ["void", "__thiscall", "CBattleEngine__DisableVolumeEntryGroupsByNameAndReselect", "void * this", "void * entryName"],
        "commentTokens": ["Owner/name correction", "BattleEngine volume-entry group", "CGeneralVolume__DisableEntriesByNameAndReselect", "+0x578", "+0x57c", "runtime behavior remain unproven"],
        "decompileTokens": ["CBattleEngine__DisableVolumeEntryGroupsByNameAndReselect", "CGeneralVolume__DisableEntriesByNameAndReselect", "CGeneralVolume__DisableLinkedEntriesByNameAndReselect", "+ 0x578", "+ 0x57c"],
        "xrefTokens": ["005d8b60", "DATA"],
        "instructionTokens": ["[ESI + 0x578]", "CALL", "0x00414a40", "[ESI + 0x57c]", "0x00412830", "RET", "0x4"],
    },
    "0x0040dcc0": {
        "name": "CBattleEngine__ClearFlag58CAndMorphIfState3",
        "previousName": "CMonitor__ResetTransitionFlagAndUpdateIfState3_Thunk",
        "signatureTokens": ["void", "__thiscall", "CBattleEngine__ClearFlag58CAndMorphIfState3", "void * this"],
        "commentTokens": ["Owner/name correction", "clears +0x58c", "state +0x260", "CBattleEngine__Morph", "runtime transform behavior remain unproven"],
        "decompileTokens": ["CBattleEngine__ClearFlag58CAndMorphIfState3", "+ 0x58c", "+ 0x260", "CBattleEngine__Morph"],
        "xrefTokens": ["00535099", "UNCONDITIONAL_CALL"],
        "instructionTokens": ["[ECX + 0x260]", "[ECX + 0x58c]", "CMP", "0x3", "JMP", "0x0040a580"],
    },
    "0x0040dda0": {
        "name": "CUnitAI__RefreshGridCooldownFromOccupiedCells",
        "previousName": "CUnitAI__RefreshGridCooldownFromOccupiedCells",
        "signatureTokens": ["void", "__thiscall", "CUnitAI__RefreshGridCooldownFromOccupiedCells", "void * this"],
        "commentTokens": ["Signature hardening", "DAT_00672fd0", "+0x10c", "CSquadNormal", "+0x2e8", "owner, exact source identity"],
        "decompileTokens": ["CUnitAI__RefreshGridCooldownFromOccupiedCells", "CSquadNormal__GetCellValueAtWorldXY", "DAT_008a9d7c", "DAT_008a9d80", "+ 0x2e8"],
        "xrefTokens": ["CExplosionInitThing__RenderObjectiveStatusPanel"],
        "instructionTokens": ["0x00672fd0", "[EDI + 0x2e8]", "[EAX + 0x10c]", "0x008a9d7c", "0x008a9d80"],
    },
    "0x0040de40": {
        "name": "CBattleEngine__AugmentWeapon",
        "previousName": "CMonitor__HandleTargetStateChangeAndHudPrompt",
        "signatureTokens": ["void", "__thiscall", "CBattleEngine__AugmentWeapon", "void * this"],
        "commentTokens": ["Owner/name correction", "CBattleEngine::AugmentWeapon", "MAX_AUG_VALUE", "10.0", "hud_weapon_augmented", "runtime augmented-weapon behavior"],
        "decompileTokens": ["CBattleEngine__AugmentWeapon", "+ 0x55c", "+ 0x52c", "+ 0x588", "+ 0x300", "+ 0x2f8", "+ 0x2fc", "+ 0x30c", "CBattleEngine__FindSoundEventByNameIfEnabled", "CMonitor__PlayRandomSampleFromChain"],
        "xrefTokens": ["CMonitor__Process", "UNCONDITIONAL_CALL"],
        "instructionTokens": ["[ESI + 0x578]", "[ESI + EAX*0x4 + 0x55c]", "[ESI + EAX*0x4 + 0x52c]", "[ESI + 0x588]", "0x41200000", "0x623540", "0x623314"],
    },
    "0x0040dfb0": {
        "name": "CGeneralVolume__SpawnPickupAndDispatch",
        "previousName": "CGeneralVolume__SpawnPickupAndDispatch",
        "signatureTokens": ["void", "__thiscall", "CGeneralVolume__SpawnPickupAndDispatch", "void * this"],
        "commentTokens": ["Signature hardening", "pickup name", "this+0x4b0/+0x68", "CWorldPhysicsManager__CreatePickup", "exact owner/source identity", "runtime pickup behavior remain provisional"],
        "decompileTokens": ["CGeneralVolume__SpawnPickupAndDispatch", "+ 0x4b0", "+ 0x68", "DAT_008553f8", "CWorldPhysicsManager__CreatePickup", "CInfluenceMap__Init", "HeightDelta__Below025_D0"],
        "xrefTokens": ["CUnit__ProcessStateSwapAndDeathChecks", "CBattleEngine__StartDieProcess"],
        "instructionTokens": ["[ECX + 0x4b0]", "[EAX + 0x68]", "0x008553f8", "SUB", "0x3e0"],
    },
}

DEFAULT_SIGNATURE_DRY = BASE / "signature_dry.log"
DEFAULT_SIGNATURE_APPLY = BASE / "signature_apply.log"
DEFAULT_METADATA = BASE / "metadata_readback.tsv"
DEFAULT_INDEX = BASE / "decompile_readback" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_readback"
DEFAULT_XREFS = BASE / "xrefs_readback.tsv"
DEFAULT_INSTRUCTIONS = BASE / "instructions_readback.tsv"
DEFAULT_OUT = BASE / "battleengine-volume-augment-pickup-signature-tranche.json"

OVERCLAIM_TOKENS = [
    "runtime behavior proven",
    "runtime augmented-weapon proven",
    "runtime pickup proven",
    "exact source identity proven",
    "concrete layout proven",
    "rebuild parity proven",
    "weapon_fire_breaks_stealth closed",
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


def joined_xref_text(rows: list[dict[str, str]], address: str) -> str:
    wanted = normalize_address(address)
    parts: list[str] = []
    for row in rows:
        if normalize_address(row.get("target_addr", "")) == wanted:
            parts.extend(row.values())
    return " ".join(parts)


def build_report(
    *,
    signature_dry_log_path: Path = DEFAULT_SIGNATURE_DRY,
    signature_apply_log_path: Path = DEFAULT_SIGNATURE_APPLY,
    metadata_path: Path = DEFAULT_METADATA,
    decompile_index_path: Path = DEFAULT_INDEX,
    decompile_dir: Path = DEFAULT_DECOMPILE_DIR,
    xrefs_path: Path = DEFAULT_XREFS,
    instructions_path: Path = DEFAULT_INSTRUCTIONS,
) -> dict[str, object]:
    signature_dry_log_path = resolve(signature_dry_log_path)
    signature_apply_log_path = resolve(signature_apply_log_path)
    metadata_path = resolve(metadata_path)
    decompile_index_path = resolve(decompile_index_path)
    decompile_dir = resolve(decompile_dir)
    xrefs_path = resolve(xrefs_path)
    instructions_path = resolve(instructions_path)

    failures: list[str] = []
    for label, path in (
        ("signature dry log", signature_dry_log_path),
        ("signature apply log", signature_apply_log_path),
        ("metadata read-back", metadata_path),
        ("decompile index", decompile_index_path),
        ("xref read-back", xrefs_path),
        ("instruction read-back", instructions_path),
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

        xref_text = joined_xref_text(xref_rows, address)
        missing_xref_tokens = [token for token in expected["xrefTokens"] if not token_present(xref_text, token)]
        if missing_xref_tokens:
            failures.append(f"xref tokens missing at {address}: {missing_xref_tokens}")

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
