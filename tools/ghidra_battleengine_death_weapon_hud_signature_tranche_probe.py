#!/usr/bin/env python3
"""Validate the BattleEngine death/weapon HUD Ghidra signature tranche."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "battleengine-profile-death-signature-tranche" / "current"

TARGETS = {
    "0x0040bfd0": {
        "name": "CBattleEngine__StartDieProcess",
        "previous": "CBattleEngine__StartDieProcess",
        "signatureTokens": ["int", "__thiscall", "CBattleEngine__StartDieProcess", "void * this"],
        "commentTokens": ["Signature/comment re-audit", "StartDieProcess", "CGame__DeclarePlayerDead", "oily smoke", "runtime death behavior is not re-proven"],
        "decompileTokens": ["CBattleEngine__StartDieProcess", "CGame__DeclarePlayerDead", "CParticleManager__CreateEffect"],
        "xrefTokens": ["005d8a8c"],
    },
    "0x0040c2e0": {
        "name": "CBattleEngine__CanSpawnBurstForResolvedEntry",
        "previous": "CEngine__CanSpawnBurstForResolvedEntry",
        "signatureTokens": ["int", "__thiscall", "CBattleEngine__CanSpawnBurstForResolvedEntry", "void * this", "void * burstContext"],
        "commentTokens": ["Owner/signature re-audit", "BattleEngine-owned burst quota helper", "+0x57c", "+0x578", "stealth-reset runtime behavior"],
        "decompileTokens": ["CBattleEngine__CanSpawnBurstForResolvedEntry", "CEngine__ProcessBurstQuotaInPrimaryEntrySet", "CEngine__ProcessBurstQuotaInSecondaryEntrySet"],
        "xrefTokens": ["CEngine__SpawnProjectileBurstFromCurrentPreset"],
    },
    "0x0040c340": {
        "name": "CBattleEngine__RandomizeBurstOffsetsAndAccumulateRange",
        "previous": "CEngine__RandomizeBurstOffsetsAndAccumulateRange",
        "signatureTokens": ["void", "__thiscall", "CBattleEngine__RandomizeBurstOffsetsAndAccumulateRange", "void * this", "void * burstContext"],
        "commentTokens": ["Owner/signature re-audit", "BattleEngine-owned burst spread helper", "+0x4b8", "+0x4c0", "+0x604"],
        "decompileTokens": ["CBattleEngine__RandomizeBurstOffsetsAndAccumulateRange", "CGeneralVolume__RandomizeOffsets4B8_4C0"],
        "xrefTokens": ["CEngine__SpawnProjectileBurstFromCurrentPreset"],
    },
    "0x0040c3a0": {
        "name": "CBattleEngine__IsEnergyWeapon",
        "previous": "CExplosionInitThing__GetCurrentEntrySlotFlag_544",
        "signatureTokens": ["int", "__thiscall", "CBattleEngine__IsEnergyWeapon", "void * this"],
        "commentTokens": ["Owner/signature re-audit", "CBattleEngine::IsEnergyWeapon", "HUD rendering", "walker or jet", "runtime HUD behavior remains unproven"],
        "decompileTokens": ["CBattleEngine__IsEnergyWeapon", "CCockpit__GetCurrentEntryFlag_544", "CGeneralVolume__EntryIterator_GetSlotFlag_544"],
        "xrefTokens": ["CExplosionInitThing__RenderObjectiveSlotFillPanel"],
    },
    "0x0040c3c0": {
        "name": "CBattleEngine__GetWeaponAmmoPercentage",
        "previous": "CExplosionInitThing__GetCurrentEntrySlotFillRatioOrRacerSpeed",
        "signatureTokens": ["float", "__thiscall", "CBattleEngine__GetWeaponAmmoPercentage", "void * this"],
        "commentTokens": ["Owner/signature re-audit", "CBattleEngine::GetWeaponAmmoPercentage", "Racer", "walker/jet ammo percentage", "runtime HUD behavior remains unproven"],
        "decompileTokens": ["CBattleEngine__GetWeaponAmmoPercentage", "Racer", "CGeneralVolume__GetCurrentEntrySlotFillRatio", "CGeneralVolume__EntryIterator_GetSlotFillRatio"],
        "xrefTokens": ["CExplosionInitThing__RenderObjectiveSlotFillPanel"],
    },
    "0x0040c460": {
        "name": "CBattleEngine__GetWeaponAmmoCount",
        "previous": "CExplosionInitThing__GetCurrentEntryRoundedSlotValue",
        "signatureTokens": ["int", "__thiscall", "CBattleEngine__GetWeaponAmmoCount", "void * this"],
        "commentTokens": ["Owner/signature re-audit", "CBattleEngine::GetWeaponAmmoCount", "non-meter weapon readout", "walker or jet", "runtime HUD behavior remains unproven"],
        "decompileTokens": ["CBattleEngine__GetWeaponAmmoCount", "CGeneralVolume__GetCurrentEntryRoundedSlotValue", "CGeneralVolume__GetMode3CurrentEntryRoundedSlotValue"],
        "xrefTokens": ["CExplosionInitThing__RenderObjectiveSlotFillPanel"],
    },
}

DEFAULT_SIGNATURE_DRY = BASE / "signature_dry.log"
DEFAULT_SIGNATURE_APPLY = BASE / "signature_apply.log"
DEFAULT_METADATA = BASE / "metadata_readback.tsv"
DEFAULT_INDEX = BASE / "decompile_readback" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_readback"
DEFAULT_XREFS = BASE / "xrefs_readback.tsv"
DEFAULT_INSTRUCTIONS = BASE / "instructions_readback.tsv"
DEFAULT_OUT = BASE / "battleengine-death-weapon-hud-signature-tranche.json"

OVERCLAIM_TOKENS = [
    "runtime behavior proven",
    "runtime hud behavior proven",
    "runtime stealth proof",
    "stealth reset proven",
    "weapon_fire_breaks_stealth closed",
    "exact cweapon::fire proven",
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

    signature_dry = read_text(signature_dry_log_path)
    signature_apply = read_text(signature_apply_log_path)
    metadata_rows = read_tsv(metadata_path)
    index_rows = read_tsv(decompile_index_path)
    xref_text = read_text(xrefs_path)
    instruction_text = read_text(instructions_path)

    dry_summary = parse_update_summary(signature_dry)
    apply_summary = parse_update_summary(signature_apply)
    if dry_summary != {"updated": 0, "skipped": 6, "missing": 0, "bad": 0}:
        failures.append("signature dry summary is not clean")
    if apply_summary != {"updated": 6, "skipped": 0, "missing": 0, "bad": 0}:
        failures.append("signature apply summary is not clean")

    target_reports: list[dict[str, object]] = []
    renamed_targets = 0
    comment_overclaims = 0
    for address, expected in TARGETS.items():
        row = find_row(metadata_rows, "address", address)
        index_row = find_row(index_rows, "address", address)
        if row is None:
            failures.append(f"metadata missing {address}")
            continue
        name = row.get("name", "")
        signature = row.get("signature", "")
        comment = row.get("comment", "")
        previous = expected["previous"]
        if name != expected["name"] or row.get("status") != "OK":
            failures.append(f"metadata name/status mismatch for {address}")
        if previous != expected["name"] and name == expected["name"]:
            renamed_targets += 1
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
            missing_decompile_tokens = [
                token for token in expected["decompileTokens"] if not token_present(decompile_text, token)
            ]
            if missing_decompile_tokens:
                failures.append(f"decompile tokens missing at {address}: {missing_decompile_tokens}")
        missing_xref_tokens = [token for token in expected["xrefTokens"] if not token_present(xref_text, token)]
        if missing_xref_tokens:
            failures.append(f"xref tokens missing at {address}: {missing_xref_tokens}")
        if not token_present(instruction_text, normalize_address(address)[2:]):
            failures.append(f"instruction rows missing {address}")
        target_reports.append(
            {
                "address": address,
                "name": name,
                "previousName": previous,
                "signature": signature,
                "comment": comment,
                "decompileFile": relative(decompile_file) if decompile_file else None,
            }
        )

    status = "PASS" if not failures else "FAIL"
    return {
        "schema": "ghidra.battleengine_death_weapon_hud_signature_tranche.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "summary": {
            "targets": len(TARGETS),
            "renamedTargets": renamed_targets,
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
    parser = argparse.ArgumentParser(description="Validate BattleEngine death/weapon HUD Ghidra signature tranche evidence.")
    parser.add_argument("--check", action="store_true", help="fail if the report is not PASS")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="JSON report path")
    args = parser.parse_args()

    report = build_report()
    out_path = resolve(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"BattleEngine death/weapon HUD signature tranche: {report['status']}")
    print(f"Report: {relative(out_path)}")
    if report["failures"]:
        for failure in report["failures"]:
            print(f"- {failure}")
    return 1 if args.check and report["status"] != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
