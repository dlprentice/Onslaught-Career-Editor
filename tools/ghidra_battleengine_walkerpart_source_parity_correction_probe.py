#!/usr/bin/env python3
"""Validate the saved BattleEngineWalkerPart source-parity correction tranche."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "walkerpart-source-parity-correction" / "current"

TARGETS = {
    "0x00409e80": {
        "name": "CBattleEngine__AutoZoomOut",
        "previous": ["CGeneralVolume__SetParam2CC_ToOne"],
        "signature": ["void", "__thiscall", "CBattleEngine__AutoZoomOut", "void * this"],
        "comment": ["Source-parity correction", "AutoZoomOut", "+0x2cc", "runtime zoom behavior", "unproven"],
        "decompile": ["+0x2cc", "0x3f800000"],
        "xrefs": ["CBattleEngineWalkerPart__ChangeWeapon", "CBattleEngineJetPart__ChangeWeapon"],
    },
    "0x00409e90": {
        "name": "CBattleEngine__ZoomOut",
        "previous": ["CGeneralVolume__SetParam2CC_ToOne_IfCurrentState1"],
        "signature": ["void", "__thiscall", "CBattleEngine__ZoomOut", "void * this"],
        "comment": ["Source-parity correction", "ZoomOut", "+0x34", "+0x2cc", "runtime zoom behavior", "unproven"],
        "decompile": ["+0x1d4", "+0x34", "+0x2cc", "0x3f800000"],
        "xrefs": ["<no_function>"],
    },
    "0x00409ec0": {
        "name": "CBattleEngine__ZoomIn",
        "previous": ["CGeneralVolume__SetParam2CC_ToPoint4_IfCurrentState1"],
        "signature": ["void", "__thiscall", "CBattleEngine__ZoomIn", "void * this"],
        "comment": ["Source-parity correction", "ZoomIn", "+0x34", "+0x2cc", "runtime zoom behavior", "unproven"],
        "decompile": ["+0x1d4", "+0x34", "+0x2cc", "0x3ecccccd"],
        "xrefs": ["<no_function>"],
    },
    "0x0040c3a0": {
        "name": "CBattleEngine__IsWeaponOverheated",
        "previous": ["CBattleEngine__IsEnergyWeapon"],
        "signature": ["int", "__thiscall", "CBattleEngine__IsWeaponOverheated", "void * this"],
        "comment": ["Source-parity correction", "IsWeaponOverheated", "+0x544", "runtime HUD behavior", "unproven"],
        "decompile": ["CBattleEngineWalkerPart__IsWeaponOverheated", "CBattleEngineJetPart__IsWeaponOverheated"],
        "xrefs": ["CExplosionInitThing__RenderObjectiveSlotFillPanel"],
    },
    "0x0040c480": {
        "name": "CBattleEngine__IsEnergyWeapon",
        "previous": ["CBattleEngine__IsWeaponOverheated"],
        "signature": ["int", "__thiscall", "CBattleEngine__IsEnergyWeapon", "void * this"],
        "comment": ["Source-parity correction", "IsEnergyWeapon", "+0x55c", "runtime HUD behavior", "unproven"],
        "decompile": ["CBattleEngineWalkerPart__IsEnergyWeapon", "CBattleEngineJetPart__IsEnergyWeapon"],
        "xrefs": ["CExplosionInitThing__RenderObjectiveSlotFillPanel"],
    },
    "0x004122b0": {
        "name": "CBattleEngineJetPart__IsEnergyWeapon",
        "previous": ["CBattleEngineJetPart__IsWeaponOverheated"],
        "signature": ["int", "__thiscall", "CBattleEngineJetPart__IsEnergyWeapon", "void * this"],
        "comment": ["Source-parity correction", "IsEnergyWeapon", "+0x55c", "unproven"],
        "decompile": ["+0x55c"],
        "xrefs": ["CBattleEngine__IsEnergyWeapon"],
    },
    "0x00412310": {
        "name": "CBattleEngineJetPart__IsWeaponOverheated",
        "previous": ["CBattleEngineJetPart__IsEnergyWeapon"],
        "signature": ["int", "__thiscall", "CBattleEngineJetPart__IsWeaponOverheated", "void * this"],
        "comment": ["Source-parity correction", "IsWeaponOverheated", "+0x544", "unproven"],
        "decompile": ["+0x544"],
        "xrefs": ["CBattleEngine__IsWeaponOverheated"],
    },
    "0x004135e0": {
        "name": "CBattleEngineWalkerPart__ActivateLandingJets",
        "previous": ["CBattleEngineWalkerPart__ApplyWalkVelocityLimitAndSetMovementLatch"],
        "signature": ["void", "__thiscall", "CBattleEngineWalkerPart__ActivateLandingJets", "void * this"],
        "comment": ["Source-parity correction", "ActivateLandingJets", "+0x638", "runtime landing-jets behavior", "unproven"],
        "decompile": ["+0x20", "+0x638"],
        "xrefs": ["<no_function>"],
    },
    "0x00413760": {
        "name": "CBattleEngineWalkerPart__Move",
        "previous": ["CMonitor__ProcessTrackingAndSurfaceAlignment"],
        "signature": ["void", "__thiscall", "CBattleEngineWalkerPart__Move", "void * this"],
        "comment": ["Source-parity correction", "Move", "surface-alignment", "runtime movement behavior", "unproven"],
        "decompile": ["CBattleEngineWalkerPart__GoingIntoWater", "CBattleEngineWalkerPart__Slide"],
        "xrefs": ["CMonitor__Process"],
    },
    "0x00413a70": {
        "name": "CBattleEngineWalkerPart__GoingIntoWater",
        "previous": ["CMonitor__ShouldUseSurfaceAlignmentPath"],
        "signature": ["int", "__thiscall", "CBattleEngineWalkerPart__GoingIntoWater", "void * this"],
        "comment": ["Source-parity correction", "GoingIntoWater", "static-shadow/height", "runtime water behavior", "unproven"],
        "decompile": ["HeightDelta__Below015_D4", "CStaticShadows__SampleShadowHeightBilinear"],
        "xrefs": ["CBattleEngineWalkerPart__Move"],
    },
    "0x00413b90": {
        "name": "CBattleEngineWalkerPart__Slide",
        "previous": ["CMonitor__ResolveSurfaceAlignmentIterative"],
        "signature": ["void", "__thiscall", "CBattleEngineWalkerPart__Slide", "void * this"],
        "comment": ["Source-parity correction", "Slide", "surface-alignment", "runtime slide behavior", "unproven"],
        "decompile": ["CMonitor__SampleHeightfieldNormalAtXY", "+0x20"],
        "xrefs": ["CBattleEngineWalkerPart__Move"],
    },
    "0x00413cc0": {
        "name": "CBattleEngineWalkerPart__FireWeapon",
        "previous": ["CGeneralVolume__ResetState588AndRefreshCurrentEntry"],
        "signature": ["void", "__thiscall", "CBattleEngineWalkerPart__FireWeapon", "void * this"],
        "comment": ["Source-parity correction", "FireWeapon", "+0x588", "weapon_fire_breaks_stealth", "unproven"],
        "decompile": ["+0x588", "ProjectileBurst__SpawnFromPercentBucketFallback"],
        "xrefs": ["CGeneralVolume__Reset588AndDispatchModeSpecific_13CC0_or_11B90"],
    },
    "0x00413cf0": {
        "name": "CBattleEngineWalkerPart__ChargeWeapon",
        "previous": ["CGeneralVolume__UpdateCurrentEntryProgressAndRefresh"],
        "signature": ["void", "__thiscall", "CBattleEngineWalkerPart__ChargeWeapon", "void * this"],
        "comment": ["Source-parity correction", "ChargeWeapon", "charge/overheat gates", "weapon_fire_breaks_stealth", "unproven"],
        "decompile": ["+0x52c", "+0x544", "+0x55c"],
        "xrefs": ["CGeneralVolume__DispatchModeSpecificReset_13CF0_or_11BF0"],
    },
    "0x00413eb0": {
        "name": "CBattleEngineWalkerPart__ChangeWeapon",
        "previous": ["CGeneralVolume__SelectNextEnabledEntry"],
        "signature": ["void", "__thiscall", "CBattleEngineWalkerPart__ChangeWeapon", "void * this"],
        "comment": ["Source-parity correction", "ChangeWeapon", "current weapon", "AutoZoomOut", "unproven"],
        "decompile": ["CBattleEngineWalkerPart__GetCurrentWeapon", "CBattleEngine__AutoZoomOut"],
        "xrefs": ["CBattleEngine__ChangeWeapon"],
    },
    "0x00414030": {
        "name": "CBattleEngineWalkerPart__GetCurrentWeapon",
        "previous": ["CGeneralVolume__ResolveCurrentOrFallbackEntry"],
        "signature": ["void *", "__thiscall", "CBattleEngineWalkerPart__GetCurrentWeapon", "void * this"],
        "comment": ["Source-parity correction", "GetCurrentWeapon", "primary/augmented/fallback", "unproven"],
        "decompile": ["+0x18", "+0x1c", "+0x10"],
        "xrefs": ["CBattleEngine__IsCurrentResolvedEntry", "CBattleEngineWalkerPart__WeaponFired"],
    },
    "0x004140d0": {
        "name": "CBattleEngineWalkerPart__WeaponFired",
        "previous": ["CEngine__ProcessBurstQuotaInSecondaryEntrySet"],
        "signature": ["int", "__thiscall", "CBattleEngineWalkerPart__WeaponFired", "void * this", "void * weapon"],
        "comment": ["Source-parity correction", "WeaponFired", "ret 0x4", "weapon_fire_breaks_stealth", "unproven"],
        "decompile": ["weapon", "+0x52c", "+0x544", "+0x55c"],
        "xrefs": ["CBattleEngine__CanSpawnBurstForResolvedEntry"],
        "ret": "0x4",
    },
    "0x00414410": {
        "name": "CBattleEngineWalkerPart__GetWeaponAmmoPercentage",
        "previous": ["CGeneralVolume__GetCurrentEntrySlotFillRatio"],
        "signature": ["float", "__thiscall", "CBattleEngineWalkerPart__GetWeaponAmmoPercentage", "void * this"],
        "comment": ["Source-parity correction", "GetWeaponAmmoPercentage", "+0x52c", "+0x4b0", "unproven"],
        "decompile": ["+0x52c", "+0x4b0", "+0x88"],
        "xrefs": ["CBattleEngine__GetWeaponAmmoPercentage"],
    },
    "0x00414470": {
        "name": "CBattleEngineWalkerPart__GetWeaponAmmoCount",
        "previous": ["CGeneralVolume__GetCurrentEntryRoundedSlotValue"],
        "signature": ["int", "__thiscall", "CBattleEngineWalkerPart__GetWeaponAmmoCount", "void * this"],
        "comment": ["Source-parity correction", "GetWeaponAmmoCount", "rounded", "+0x52c", "unproven"],
        "decompile": ["ROUND", "+0x52c"],
        "xrefs": ["CBattleEngine__GetWeaponAmmoCount"],
    },
    "0x004144c0": {
        "name": "CBattleEngineWalkerPart__IsEnergyWeapon",
        "previous": ["CGeneralVolume__GetCurrentEntrySlotFlag_55C"],
        "signature": ["int", "__thiscall", "CBattleEngineWalkerPart__IsEnergyWeapon", "void * this"],
        "comment": ["Source-parity correction", "IsEnergyWeapon", "+0x55c", "unproven"],
        "decompile": ["+0x55c"],
        "xrefs": ["CBattleEngine__IsEnergyWeapon"],
    },
    "0x004144f0": {
        "name": "CBattleEngineWalkerPart__IsWeaponOverheated",
        "previous": ["CCockpit__GetCurrentEntryFlag_544"],
        "signature": ["int", "__thiscall", "CBattleEngineWalkerPart__IsWeaponOverheated", "void * this"],
        "comment": ["Source-parity correction", "IsWeaponOverheated", "+0x544", "unproven"],
        "decompile": ["+0x544"],
        "xrefs": ["CBattleEngine__IsWeaponOverheated"],
    },
    "0x00414520": {
        "name": "CBattleEngineWalkerPart__GetWeaponCharge",
        "previous": ["CGeneralVolume__GetCurrentEntryDistanceProgressRatio"],
        "signature": ["float", "__thiscall", "CBattleEngineWalkerPart__GetWeaponCharge", "void * this"],
        "comment": ["Source-parity correction", "GetWeaponCharge", "+0x60", "unproven"],
        "decompile": ["+0x60", "+0xa4"],
        "xrefs": ["CBattleEngine__GetWeaponCharge"],
    },
    "0x004145a0": {
        "name": "CBattleEngineWalkerPart__GetWeaponName",
        "previous": ["CGeneralVolume__GetCurrentEntryDisplayString"],
        "signature": ["short *", "__thiscall", "CBattleEngineWalkerPart__GetWeaponName", "void * this"],
        "comment": ["Source-parity correction", "GetWeaponName", "CText__GetStringById", "unproven"],
        "decompile": ["CText__GetStringById", "+0x3c"],
        "xrefs": ["CBattleEngine__GetWeaponName"],
    },
    "0x004145d0": {
        "name": "CBattleEngineWalkerPart__GetWeaponPhysicsName",
        "previous": ["CGeneralVolume__GetCurrentEntryPayload"],
        "signature": ["char *", "__thiscall", "CBattleEngineWalkerPart__GetWeaponPhysicsName", "void * this"],
        "comment": ["Source-parity correction", "GetWeaponPhysicsName", "weapon data name", "unproven"],
        "decompile": ["+0xa4"],
        "xrefs": ["CBattleEngine__GetWeaponPhysicsName"],
    },
    "0x004145f0": {
        "name": "CBattleEngineWalkerPart__GetCurrentWeaponZoomMode",
        "previous": ["CGeneralVolume__GetSelectedWeaponDef_CachedPath"],
        "signature": ["int", "__thiscall", "CBattleEngineWalkerPart__GetCurrentWeaponZoomMode", "void * this"],
        "comment": ["Source-parity correction", "GetCurrentWeaponZoomMode", "ChangeWeapon", "unproven"],
        "decompile": ["+0xa4", "+4"],
        "xrefs": ["CBattleEngine__ChangeWeapon"],
    },
    "0x00414610": {
        "name": "CBattleEngineWalkerPart__GetWeaponIconName",
        "previous": ["CGeneralVolume__GetCurrentEntryFieldA4_38"],
        "signature": ["char *", "__thiscall", "CBattleEngineWalkerPart__GetWeaponIconName", "void * this"],
        "comment": ["Source-parity correction", "GetWeaponIconName", "+0x38", "unproven"],
        "decompile": ["+0x38"],
        "xrefs": ["CBattleEngine__GetWeaponIconName"],
    },
    "0x00414630": {
        "name": "CBattleEngineWalkerPart__CanWeaponFire",
        "previous": ["CBattleEngine__IsResolvedEntryUsable"],
        "signature": ["int", "__thiscall", "CBattleEngineWalkerPart__CanWeaponFire", "void * this"],
        "comment": ["Source-parity correction", "CanWeaponFire", "+0x9c", "+0x52c", "unproven"],
        "decompile": ["+0x9c", "+0x52c", "+0x544", "+0x55c"],
        "xrefs": ["CBattleEngine__UpdateAutoTargetSetAndFireProjectiles"],
    },
}

DEFAULT_DRY = BASE / "correction_dry.log"
DEFAULT_APPLY = BASE / "correction_apply.log"
DEFAULT_METADATA = BASE / "metadata_final.tsv"
DEFAULT_INDEX = BASE / "decompile_final" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_final"
DEFAULT_XREFS = BASE / "xrefs_final.tsv"
DEFAULT_INSTRUCTIONS = BASE / "instructions_final.tsv"
DEFAULT_OUT = BASE / "walkerpart-source-parity-correction.json"
EXPECTED_RENAMED_BY_APPLY = 3

OVERCLAIMS = [
    "runtime behavior proven",
    "weapon_fire_breaks_stealth closed",
    "retail cbattleengine::weaponfired identified",
    "concrete layout proven",
    "fully re'ed",
]


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def unescape_tsv(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        for key, value in list(row.items()):
            row[key] = unescape_tsv(value or "")
    return rows


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""


def decompile_text_for(decompile_dir: Path, address: str, name: str) -> str:
    pattern = f"{address[2:]}_{name}.c"
    exact = decompile_dir / pattern
    if exact.is_file():
        return load_text(exact)
    matches = list(decompile_dir.glob(f"{address[2:]}_*.c"))
    return load_text(matches[0]) if matches else ""


def has_tokens(text: str, tokens: list[str]) -> bool:
    compact_text = re.sub(r"\s+", "", text)
    return all(token in text or re.sub(r"\s+", "", token) in compact_text for token in tokens)


def parse_summary(text: str) -> dict[str, int]:
    pairs = dict((key, int(value)) for key, value in re.findall(r"\b(updated|skipped|renamed|missing|bad)=(\d+)", text))
    return pairs


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
    for label, path in {
        "dry log": dry_log_path,
        "apply log": apply_log_path,
        "metadata": metadata_path,
        "decompile index": decompile_index_path,
        "xrefs": xrefs_path,
        "instructions": instructions_path,
    }.items():
        if not path.is_file():
            failures.append(f"missing {label}: {relative(path)}")

    dry_summary = parse_summary(load_text(dry_log_path))
    apply_summary = parse_summary(load_text(apply_log_path))
    target_count = len(TARGETS)
    rename_count = EXPECTED_RENAMED_BY_APPLY
    if dry_summary and dry_summary != {"updated": 0, "skipped": target_count, "renamed": 0, "missing": 0, "bad": 0}:
        failures.append(f"unexpected dry summary: {dry_summary}")
    if apply_summary and apply_summary != {"updated": target_count, "skipped": 0, "renamed": rename_count, "missing": 0, "bad": 0}:
        failures.append(f"unexpected apply summary: {apply_summary}")

    metadata = {normalize_address(row.get("address", "")): row for row in read_tsv(metadata_path)}
    decompile_index = {normalize_address(row.get("address", "")): row for row in read_tsv(decompile_index_path)}
    xref_rows = read_tsv(xrefs_path)
    instruction_rows = read_tsv(instructions_path)

    stale_name_hits = 0
    param_signature_hits = 0
    comment_overclaims = 0
    decompile_hits = 0
    xref_hits = 0
    ret_hits = 0
    checked: list[dict[str, object]] = []

    for address, target in TARGETS.items():
        row = metadata.get(address)
        if row is None:
            failures.append(f"{address} missing metadata row")
            continue
        name = row.get("name", "")
        signature = row.get("signature", "")
        comment = row.get("comment", "")
        if name != target["name"]:
            failures.append(f"{address} unexpected name {name!r}")
        for previous in target["previous"]:
            if previous in name:
                stale_name_hits += 1
                failures.append(f"{address} stale name still present: {previous}")
        if not has_tokens(signature, target["signature"]):
            failures.append(f"{address} signature missing expected tokens: {signature}")
        if "param_" in signature:
            param_signature_hits += 1
            failures.append(f"{address} still has param_N signature: {signature}")
        if not has_tokens(comment, target["comment"]):
            failures.append(f"{address} comment missing expected tokens")
        lowered_comment = comment.lower()
        for token in OVERCLAIMS:
            if token in lowered_comment:
                comment_overclaims += 1
                failures.append(f"{address} comment overclaim: {token}")

        index_row = decompile_index.get(address)
        if index_row is None or index_row.get("name") != target["name"]:
            failures.append(f"{address} missing corrected decompile index row")
        decompile_text = decompile_text_for(decompile_dir, address, target["name"])
        if has_tokens(decompile_text, target["decompile"]):
            decompile_hits += 1
        else:
            failures.append(f"{address} decompile missing expected evidence tokens")

        target_xrefs = [row for row in xref_rows if normalize_address(row.get("target_addr", "")) == address]
        if any(any(token in row.get("from_function", "") for token in target["xrefs"]) for row in target_xrefs):
            xref_hits += 1
        else:
            failures.append(f"{address} missing expected xref evidence")

        expected_ret = target.get("ret")
        if expected_ret:
            if any(
                normalize_address(row.get("target_addr", "")) == address
                and row.get("function_name") == target["name"]
                and row.get("mnemonic") == "RET"
                and row.get("operands") == expected_ret
                for row in instruction_rows
            ):
                ret_hits += 1
            else:
                failures.append(f"{address} missing RET {expected_ret} evidence")

        checked.append({"address": address, "name": target["name"], "signature": signature})

    status = "PASS" if not failures else "FAIL"
    return {
        "schema": "ghidra-battleengine-walkerpart-source-parity-correction.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "summary": {
            "targets": target_count,
            "renamed": rename_count,
            "staleNameHits": stale_name_hits,
            "paramSignatureHits": param_signature_hits,
            "commentOverclaims": comment_overclaims,
            "decompileEvidenceHits": decompile_hits,
            "xrefEvidenceHits": xref_hits,
            "retEvidenceHits": ret_hits,
        },
        "inputs": {
            "dryLog": relative(dry_log_path),
            "applyLog": relative(apply_log_path),
            "metadata": relative(metadata_path),
            "decompileIndex": relative(decompile_index_path),
            "xrefs": relative(xrefs_path),
            "instructions": relative(instructions_path),
        },
        "checkedTargets": checked,
        "failures": failures,
        "whatIsProven": [
            "The saved Ghidra names/signatures/comments match the current BattleEngineWalkerPart source-parity correction target set.",
            "Read-back metadata, decompile, xref, and instruction exports support the corrected static labels and call signatures.",
        ],
        "notProven": [
            "This does not prove runtime weapon, dash, surface, cloak, or fire-while-cloaked behavior.",
            "This does not prove exact retail CBattleEngine::WeaponFired identity or close weapon_fire_breaks_stealth.",
            "This does not prove concrete layouts, tags, local variables, structure types, BEA launch behavior, game patching, or rebuild parity.",
        ],
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--dry-log", type=Path, default=DEFAULT_DRY)
    parser.add_argument("--apply-log", type=Path, default=DEFAULT_APPLY)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--decompile-index", type=Path, default=DEFAULT_INDEX)
    parser.add_argument("--decompile-dir", type=Path, default=DEFAULT_DECOMPILE_DIR)
    parser.add_argument("--xrefs", type=Path, default=DEFAULT_XREFS)
    parser.add_argument("--instructions", type=Path, default=DEFAULT_INSTRUCTIONS)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if not args.check:
        parser.error("expected --check")

    out = resolve(args.out)
    try:
        out.resolve().relative_to((ROOT / "subagents").resolve())
    except ValueError:
        print(f"Refusing to write report outside subagents/: {out}", file=sys.stderr)
        return 1

    report = build_report(
        dry_log_path=args.dry_log,
        apply_log_path=args.apply_log,
        metadata_path=args.metadata,
        decompile_index_path=args.decompile_index,
        decompile_dir=args.decompile_dir,
        xrefs_path=args.xrefs,
        instructions_path=args.instructions,
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        summary = report["summary"]
        print(
            "walkerpart source-parity correction: "
            f"{report['status']} targets={summary['targets']} renamed={summary['renamed']} "
            f"failures={len(report['failures'])} out={relative(out)}"
        )
        for failure in report["failures"]:
            print(f"- {failure}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
