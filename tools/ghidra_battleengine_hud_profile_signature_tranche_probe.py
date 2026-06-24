#!/usr/bin/env python3
"""Validate the BattleEngine HUD/profile Ghidra signature tranche."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "battleengine-hud-profile-signature-tranche" / "current"

TARGETS = {
    "0x0040c480": {
        "name": "CBattleEngine__IsWeaponOverheated",
        "previous": "CExplosionInitThing__GetCurrentEntrySlotFlag_55C",
        "signatureTokens": ["int", "__thiscall", "CBattleEngine__IsWeaponOverheated", "void * this"],
        "commentTokens": ["Owner/signature re-audit", "CBattleEngine::IsWeaponOverheated", "+0x55c", "runtime HUD behavior remains unproven"],
        "decompileTokens": ["CBattleEngine__IsWeaponOverheated", "CGeneralVolume__GetCurrentEntrySlotFlag_55C", "CGeneralVolume__EntryIterator_GetSlotFlag_55C"],
        "xrefTokens": ["CExplosionInitThing__RenderObjectiveSlotFillPanel"],
    },
    "0x0040c4a0": {
        "name": "CBattleEngine__GetWeaponCharge",
        "previous": "CExplosionInitThing__GetCurrentEntryDistanceProgressRatioOrRacerDelta",
        "signatureTokens": ["float", "__thiscall", "CBattleEngine__GetWeaponCharge", "void * this"],
        "commentTokens": ["Owner/signature re-audit", "CBattleEngine::GetWeaponCharge", "Racer", "terrain/water-style height", "clamps a delta ratio", "runtime weapon charge behavior remains unproven"],
        "decompileTokens": ["CBattleEngine__GetWeaponCharge", "Racer", "CStaticShadows__SampleShadowHeightBilinear", "CGeneralVolume__GetCurrentEntryDistanceProgressRatio"],
        "xrefTokens": ["CExplosionInitThing__RenderObjectiveProgressGaugeAndHeadingNeedle"],
    },
    "0x0040c550": {
        "name": "CBattleEngine__GetWeaponName",
        "previous": "CExplosionInitThing__GetCurrentEntryDisplayString",
        "signatureTokens": ["short *", "__thiscall", "CBattleEngine__GetWeaponName", "void * this"],
        "commentTokens": ["Owner/signature re-audit", "CBattleEngine::GetWeaponName", "HUD status panel", "wide string layout", "runtime HUD behavior"],
        "decompileTokens": ["CBattleEngine__GetWeaponName", "CGeneralVolume__GetCurrentEntryDisplayString", "CGeneralVolume__GetMode3CurrentEntryDisplayString"],
        "xrefTokens": ["CExplosionInitThing__RenderObjectiveStatusPanel"],
    },
    "0x0040c570": {
        "name": "CBattleEngine__GetWeaponPhysicsName",
        "previous": "CGeneralVolume__DispatchModeSpecific_145D0_or_12480",
        "signatureTokens": ["char *", "__thiscall", "CBattleEngine__GetWeaponPhysicsName", "void * this"],
        "commentTokens": ["Owner/signature re-audit", "CBattleEngine::GetWeaponPhysicsName", "IScript__GetThingName", "runtime script behavior remains unproven"],
        "decompileTokens": ["CBattleEngine__GetWeaponPhysicsName", "CGeneralVolume__GetCurrentEntryPayload", "CGeneralVolume__EntryIterator_GetModeId"],
        "xrefTokens": ["IScript__GetThingName"],
    },
    "0x0040c590": {
        "name": "CBattleEngine__GetWeaponIconName",
        "previous": "CExplosionInitThing__GetCurrentEntryFieldA4_38",
        "signatureTokens": ["char *", "__thiscall", "CBattleEngine__GetWeaponIconName", "void * this"],
        "commentTokens": ["Owner/signature re-audit", "CBattleEngine::GetWeaponIconName", "HUD status panel", "icon-name context", "runtime HUD behavior remains unproven"],
        "decompileTokens": ["CBattleEngine__GetWeaponIconName", "CGeneralVolume__GetCurrentEntryFieldA4_38", "CGeneralVolume__EntryIterator_GetIndexedEntryFieldA4_38"],
        "xrefTokens": ["CExplosionInitThing__RenderObjectiveStatusPanel"],
    },
    "0x0040c650": {
        "name": "CBattleEngine__UpdateConfiguration",
        "previous": "CBattleEngine__ApplyWeaponProfileByIndex",
        "signatureTokens": ["void", "__thiscall", "CBattleEngine__UpdateConfiguration", "void * this"],
        "commentTokens": ["Owner/signature re-audit", "CBattleEngine::UpdateConfiguration", "resets jet/walker part configuration", "store overheat/heat/value arrays", "runtime configuration behavior"],
        "decompileTokens": ["CBattleEngine__UpdateConfiguration", "CBattleEngine__GetWeaponProfileByIndex", "CBattleEngineJetPart__ResetConfiguration", "CBattleEngineWalkerPart__ResetConfiguration"],
        "xrefTokens": ["CBattleEngine__Init"],
    },
}

DEFAULT_SIGNATURE_DRY = BASE / "signature_dry.log"
DEFAULT_SIGNATURE_APPLY = BASE / "signature_apply.log"
DEFAULT_METADATA = BASE / "metadata_readback.tsv"
DEFAULT_INDEX = BASE / "decompile_readback" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_readback"
DEFAULT_XREFS = BASE / "xrefs_readback.tsv"
DEFAULT_INSTRUCTIONS = BASE / "instructions_readback.tsv"
DEFAULT_OUT = BASE / "battleengine-hud-profile-signature-tranche.json"

OVERCLAIM_TOKENS = [
    "runtime behavior proven",
    "runtime hud behavior proven",
    "runtime weapon charge proven",
    "runtime script behavior proven",
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
    param_signature_hits = 0
    stale_token_hits = 0
    comment_overclaims = 0
    instruction_name_hits = 0

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
            failures.append(f"signature missing tokens for {address}: {missing_signature_tokens}")
        if "param_" in signature:
            param_signature_hits += 1
            failures.append(f"param_N signature remains for {address}")

        missing_comment_tokens = [token for token in expected["commentTokens"] if not token_present(comment, token)]
        if missing_comment_tokens:
            failures.append(f"comment missing tokens for {address}: {missing_comment_tokens}")
        overclaims = [token for token in OVERCLAIM_TOKENS if token_present(comment, token)]
        if overclaims:
            comment_overclaims += len(overclaims)
            failures.append(f"runtime/source overclaim for {address}: {overclaims}")

        decompile_path = decompile_file_for(decompile_dir, address)
        decompile_text = read_text(decompile_path) if decompile_path else ""
        if index_row is None:
            failures.append(f"decompile index missing {address}")
        if not decompile_path:
            failures.append(f"decompile file missing {address}")
        missing_decompile_tokens = [token for token in expected["decompileTokens"] if not token_present(decompile_text, token)]
        if missing_decompile_tokens:
            failures.append(f"decompile missing tokens for {address}: {missing_decompile_tokens}")

        stale_tokens = []
        if previous != expected["name"]:
            for text_name, text in (("metadata", f"{name} {signature} {comment}"), ("decompile", decompile_text)):
                if token_present(text, previous):
                    stale_tokens.append(f"{text_name}:{previous}")
        if stale_tokens:
            stale_token_hits += len(stale_tokens)
            failures.append(f"stale tokens remain for {address}: {stale_tokens}")

        missing_xref_tokens = [token for token in expected["xrefTokens"] if not token_present(xref_text, token)]
        if missing_xref_tokens:
            failures.append(f"xref missing tokens for {address}: {missing_xref_tokens}")

        if token_present(instruction_text, expected["name"]):
            instruction_name_hits += 1

        target_reports.append(
            {
                "address": address,
                "name": name,
                "signature": signature,
                "comment": comment,
                "decompilePath": relative(decompile_path) if decompile_path else None,
                "missingSignatureTokens": missing_signature_tokens,
                "missingCommentTokens": missing_comment_tokens,
                "missingDecompileTokens": missing_decompile_tokens,
                "missingXrefTokens": missing_xref_tokens,
            }
        )

    summary = {
        "targets": len(TARGETS),
        "renamedTargets": renamed_targets,
        "signatureHardenedTargets": len(TARGETS) - param_signature_hits,
        "paramSignatureHits": param_signature_hits,
        "staleTokenHits": stale_token_hits,
        "commentOverclaims": comment_overclaims,
        "instructionNameHits": instruction_name_hits,
        "xrefRows": max(0, len([line for line in xref_text.splitlines() if line.strip()]) - 1),
        "instructionRows": max(0, len([line for line in instruction_text.splitlines() if line.strip()]) - 1),
    }
    if instruction_name_hits < len(TARGETS):
        failures.append("instruction read-back does not include every corrected function name")

    return {
        "schema": "ghidra-battleengine-hud-profile-signature-tranche.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not failures else "FAIL",
        "summary": summary,
        "inputs": {
            "signatureDryLog": relative(signature_dry_log_path),
            "signatureApplyLog": relative(signature_apply_log_path),
            "metadata": relative(metadata_path),
            "decompileIndex": relative(decompile_index_path),
            "decompileDir": relative(decompile_dir),
            "xrefs": relative(xrefs_path),
            "instructions": relative(instructions_path),
        },
        "drySummary": dry_summary,
        "applySummary": apply_summary,
        "targets": target_reports,
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Return non-zero if the report fails.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output JSON report path.")
    args = parser.parse_args()

    report = build_report()
    out_path = resolve(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"BattleEngine HUD/profile signature tranche: {report['status']}")
    print(f"Report: {relative(out_path)}")
    summary = report["summary"]
    print(f"Targets: {summary['targets']}")
    print(f"Renamed targets: {summary['renamedTargets']}")
    print(f"Signature-hardened targets: {summary['signatureHardenedTargets']}")
    print(f"Param signature hits: {summary['paramSignatureHits']}")
    print(f"Comment overclaims: {summary['commentOverclaims']}")
    print(f"Stale token hits: {summary['staleTokenHits']}")
    print(f"Xref rows: {summary['xrefRows']}")
    print(f"Instruction rows: {summary['instructionRows']}")

    if args.check and report["status"] != "PASS":
        for failure in report["failures"]:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
