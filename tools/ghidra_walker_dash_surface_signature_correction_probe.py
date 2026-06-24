#!/usr/bin/env python3
"""Validate the saved WalkerPart/Monitor/GeneralVolume dash-surface correction tranche."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "walker-dash-surface-correction-tranche" / "current"

TARGETS = {
    "0x004127a0": {
        "name": "CGeneralVolume__EnableLinkedEntriesByName",
        "previous": ["CBattleEngineJetPart__EnableWeapon"],
        "renamedByCorrection": True,
        "signature": ["void", "__thiscall", "CGeneralVolume__EnableLinkedEntriesByName", "void * this", "char * entryName"],
        "forbiddenSignature": ["param_"],
        "comment": ["Correction", "linked-entry group helper", "+0x9c", "stale JetPart weapon label", "unproven"],
        "decompile": ["entryName", "+0x9c"],
        "xrefs": ["CBattleEngine__EnableVolumeEntryGroupsByName"],
        "ret": "0x4",
    },
    "0x00412900": {
        "name": "CMonitor__CanUseTrackingUpdate",
        "previous": ["CBattleEngineJetPart__AutoLevel"],
        "renamedByCorrection": True,
        "signature": ["int", "__thiscall", "CMonitor__CanUseTrackingUpdate", "void * this"],
        "forbiddenSignature": ["param_"],
        "comment": ["Correction", "monitor predicate", "stale JetPart AutoLevel label", "runtime flight/camera behavior", "unproven"],
        "decompile": ["+0x18", "+0xfc", "+0x48"],
        "xrefs": ["CMonitor__UpdateCameraVectorsAndInput"],
        "ret": "",
    },
    "0x004129a0": {
        "name": "LinkedObjectList__CountFlag9C",
        "previous": ["CBattleEngineJetPart__CountActiveWeapons"],
        "renamedByCorrection": True,
        "signature": ["int", "__thiscall", "LinkedObjectList__CountFlag9C", "void * this"],
        "forbiddenSignature": ["param_"],
        "comment": ["Correction", "linked-object-list helper", "+0x9c", "stale JetPart active-weapon label", "unproven"],
        "decompile": ["+0x9c"],
        "xrefs": ["CBattleEngine__CountFlag9CBySelectionMode", "CBattleEngine__ChangeWeapon"],
        "ret": "",
    },
    "0x00412bc0": {
        "name": "CBattleEngineWalkerPart__ctor",
        "previous": ["CBattleEngine__InitDashMoveParams"],
        "renamedByCorrection": False,
        "signature": ["void *", "__thiscall", "CBattleEngineWalkerPart__ctor", "void * this", "void * mainPart"],
        "forbiddenSignature": ["param_"],
        "comment": ["Owner/signature correction", "CBattleEngineWalkerPart constructor", "g_dash_", "ResetConfiguration", "unproven"],
        "decompile": ["mainPart", "g_dash_start", "g_dash_velocity", "CBattleEngineWalkerPart__ResetConfiguration"],
        "xrefs": ["CBattleEngine__Init"],
        "ret": "0x4",
    },
    "0x00412cf0": {
        "name": "CBattleEngineWalkerPart__dtor_base",
        "previous": ["CCockpit__DestroyWeaponSetAndOwnedNodes"],
        "renamedByCorrection": False,
        "signature": ["void", "__thiscall", "CBattleEngineWalkerPart__dtor_base", "void * this"],
        "forbiddenSignature": ["param_"],
        "comment": ["Owner/signature correction", "CBattleEngineWalkerPart destructor-base", "primary", "augmented", "unproven"],
        "decompile": ["CSPtrSet__Remove", "CSPtrSet__Clear", "+0x18", "+0x1c"],
        "xrefs": ["CBattleEngine__dtor_base"],
        "ret": "",
    },
    "0x00412d80": {
        "name": "CBattleEngineWalkerPart__Forward",
        "previous": ["CGeneralVolume__HandleDashForwardInput"],
        "renamedByCorrection": False,
        "signature": ["void", "__thiscall", "CBattleEngineWalkerPart__Forward", "void * this", "float moveY"],
        "forbiddenSignature": ["param_"],
        "comment": ["Owner/signature correction", "forward input helper", "moveY", "Runtime dash behavior", "unproven"],
        "decompile": ["moveY", "+0x40", "+0x34"],
        "xrefs": ["<no_function>"],
        "ret": "0x4",
    },
    "0x00412f70": {
        "name": "CBattleEngineWalkerPart__Backward",
        "previous": ["CGeneralVolume__HandleDashBackwardInput"],
        "renamedByCorrection": False,
        "signature": ["void", "__thiscall", "CBattleEngineWalkerPart__Backward", "void * this", "float moveY"],
        "forbiddenSignature": ["param_"],
        "comment": ["Owner/signature correction", "backward input helper", "moveY", "Runtime dash behavior", "unproven"],
        "decompile": ["moveY", "+0x40", "+0x38"],
        "xrefs": ["<no_function>"],
        "ret": "0x4",
    },
    "0x00413160": {
        "name": "CBattleEngineWalkerPart__StrafeLeft",
        "previous": ["CGeneralVolume__HandleDashLeftInput"],
        "renamedByCorrection": False,
        "signature": ["void", "__thiscall", "CBattleEngineWalkerPart__StrafeLeft", "void * this", "float moveX"],
        "forbiddenSignature": ["param_"],
        "comment": ["Owner/signature correction", "strafe-left helper", "moveX", "Runtime dash behavior", "unproven"],
        "decompile": ["moveX", "+0x3c", "+0x30"],
        "xrefs": ["<no_function>"],
        "ret": "0x4",
    },
    "0x00413360": {
        "name": "CBattleEngineWalkerPart__StrafeRight",
        "previous": ["CGeneralVolume__HandleDashRightInput"],
        "renamedByCorrection": False,
        "signature": ["void", "__thiscall", "CBattleEngineWalkerPart__StrafeRight", "void * this", "float moveX"],
        "forbiddenSignature": ["param_"],
        "comment": ["Owner/signature correction", "strafe-right helper", "moveX", "Runtime dash behavior", "unproven"],
        "decompile": ["moveX", "+0x3c", "+0x2c"],
        "xrefs": ["<no_function>"],
        "ret": "0x4",
    },
    "0x004135d0": {
        "name": "CBattleEngineWalkerPart__GetIsDoingSpecialWalkerMove",
        "previous": ["CGeneralVolume__IsDashLockoutActive"],
        "renamedByCorrection": False,
        "signature": ["int", "__thiscall", "CBattleEngineWalkerPart__GetIsDoingSpecialWalkerMove", "void * this"],
        "forbiddenSignature": ["param_"],
        "comment": ["Owner/signature correction", "GetIsDoingSpecialWalkerMove", "+0x44", "Runtime dash behavior", "unproven"],
        "decompile": ["+0x44"],
        "xrefs": ["CBattleEngine__Morph"],
        "ret": "",
    },
    "0x004135e0": {
        "name": "CBattleEngineWalkerPart__ApplyWalkVelocityLimitAndSetMovementLatch",
        "previous": ["CBattleEngineWalkerPart__ActivateLandingJets", "CGeneralVolume__ApplyScaledVelocityAndSetMovementLatch"],
        "renamedByCorrection": True,
        "signature": ["void", "__thiscall", "CBattleEngineWalkerPart__ApplyWalkVelocityLimitAndSetMovementLatch", "void * this"],
        "forbiddenSignature": ["param_"],
        "comment": ["Correction", "samples main-part velocity", "+0x638", "stale ActivateLandingJets label", "unproven"],
        "decompile": ["+0x20", "+0x638"],
        "xrefs": ["<no_function>"],
        "ret": "",
    },
    "0x00413760": {
        "name": "CMonitor__ProcessTrackingAndSurfaceAlignment",
        "previous": ["CBattleEngineWalkerPart__Move"],
        "renamedByCorrection": True,
        "signature": ["void", "__thiscall", "CMonitor__ProcessTrackingAndSurfaceAlignment", "void * this"],
        "forbiddenSignature": ["param_"],
        "comment": ["Correction", "CMonitor processing helper", "tracked render pairs", "stale WalkerPart Move label", "unproven"],
        "decompile": ["CMonitor__ShouldUseSurfaceAlignmentPath", "CMonitor__UpdateTrackedRenderPair", "CMonitor__ResolveSurfaceAlignmentIterative"],
        "xrefs": ["CMonitor__Process"],
        "ret": "",
    },
    "0x00413a70": {
        "name": "CMonitor__ShouldUseSurfaceAlignmentPath",
        "previous": ["CBattleEngineWalkerPart__GoingIntoWater"],
        "renamedByCorrection": True,
        "signature": ["int", "__thiscall", "CMonitor__ShouldUseSurfaceAlignmentPath", "void * this"],
        "forbiddenSignature": ["param_"],
        "comment": ["Correction", "monitor predicate", "static-shadow height", "stale WalkerPart GoingIntoWater label", "unproven"],
        "decompile": ["HeightDelta__Below015_D4", "CStaticShadows__SampleShadowHeightBilinear"],
        "xrefs": ["CMonitor__ProcessTrackingAndSurfaceAlignment"],
        "ret": "",
    },
    "0x00413b90": {
        "name": "CMonitor__ResolveSurfaceAlignmentIterative",
        "previous": ["CBattleEngineWalkerPart__Slide", "CCylinder__ResolveSurfaceAlignmentIterative"],
        "renamedByCorrection": True,
        "signature": ["void", "__thiscall", "CMonitor__ResolveSurfaceAlignmentIterative", "void * this"],
        "forbiddenSignature": ["param_"],
        "comment": ["Correction", "monitor surface-alignment helper", "iteration cap", "stale CCylinder", "WalkerPart Slide", "unproven"],
        "decompile": ["CMonitor__SampleHeightfieldNormalAtXY", "+0x20"],
        "xrefs": ["CMonitor__ProcessTrackingAndSurfaceAlignment"],
        "ret": "",
    },
    "0x00413cc0": {
        "name": "CGeneralVolume__ResetState588AndRefreshCurrentEntry",
        "previous": ["CBattleEngineWalkerPart__FireWeapon"],
        "renamedByCorrection": True,
        "signature": ["void", "__thiscall", "CGeneralVolume__ResetState588AndRefreshCurrentEntry", "void * this"],
        "forbiddenSignature": ["param_"],
        "comment": ["Correction", "GeneralVolume helper", "+0x588", "ProjectileBurst__SpawnFromPercentBucketFallback", "weapon_fire_breaks_stealth", "unproven"],
        "decompile": ["+0x588", "ProjectileBurst__SpawnFromPercentBucketFallback", "CGeneralVolume__ResolveCurrentOrFallbackEntry"],
        "xrefs": ["CGeneralVolume__Reset588AndDispatchModeSpecific_13CC0_or_11B90"],
        "ret": "",
    },
    "0x00413cf0": {
        "name": "CGeneralVolume__UpdateCurrentEntryProgressAndRefresh",
        "previous": ["CBattleEngineWalkerPart__ChargeWeapon"],
        "renamedByCorrection": True,
        "signature": ["void", "__thiscall", "CGeneralVolume__UpdateCurrentEntryProgressAndRefresh", "void * this"],
        "forbiddenSignature": ["param_"],
        "comment": ["Correction", "GeneralVolume helper", "range/progress/charge/overheat-style gates", "weapon_fire_breaks_stealth", "unproven"],
        "decompile": ["+0x52c", "+0x544", "+0x55c", "ProjectileBurst__SpawnFromPercentBucketFallback"],
        "xrefs": ["CGeneralVolume__DispatchModeSpecificReset_13CF0_or_11BF0"],
        "ret": "",
    },
}

DEFAULT_CORRECTION_DRY = BASE / "correction_dry.log"
DEFAULT_CORRECTION_APPLY = BASE / "correction_apply.log"
DEFAULT_METADATA = BASE / "metadata_final.tsv"
DEFAULT_INDEX = BASE / "decompile_final" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_final"
DEFAULT_XREFS = BASE / "xrefs_final.tsv"
DEFAULT_INSTRUCTIONS = BASE / "instructions_final.tsv"
DEFAULT_OUT = BASE / "walker-dash-surface-correction.json"

OVERCLAIMS = [
    "runtime behavior proven",
    "exact source identity proven",
    "concrete layout proven",
    "weapon_fire_breaks_stealth closed",
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


def parse_summary(log_text: str) -> dict[str, int]:
    match = re.search(r"updated=(\d+)\s+skipped=(\d+)\s+renamed=(\d+)\s+missing=(\d+)\s+bad=(\d+)", log_text)
    if not match:
        return {"changed": -1, "skipped": -1, "renamed": -1, "missing": -1, "bad": -1}
    return {
        "changed": int(match.group(1)),
        "skipped": int(match.group(2)),
        "renamed": int(match.group(3)),
        "missing": int(match.group(4)),
        "bad": int(match.group(5)),
    }


def build_report(
    *,
    correction_dry_log_path: Path = DEFAULT_CORRECTION_DRY,
    correction_apply_log_path: Path = DEFAULT_CORRECTION_APPLY,
    metadata_path: Path = DEFAULT_METADATA,
    decompile_index_path: Path = DEFAULT_INDEX,
    decompile_dir: Path = DEFAULT_DECOMPILE_DIR,
    xrefs_path: Path = DEFAULT_XREFS,
    instructions_path: Path = DEFAULT_INSTRUCTIONS,
) -> dict[str, object]:
    correction_dry_log_path = resolve(correction_dry_log_path)
    correction_apply_log_path = resolve(correction_apply_log_path)
    metadata_path = resolve(metadata_path)
    decompile_index_path = resolve(decompile_index_path)
    decompile_dir = resolve(decompile_dir)
    xrefs_path = resolve(xrefs_path)
    instructions_path = resolve(instructions_path)

    failures: list[str] = []
    target_count = len(TARGETS)
    renamed_expected = sum(1 for target in TARGETS.values() if target.get("renamedByCorrection"))

    correction_dry = parse_summary(read_text(correction_dry_log_path))
    correction_apply = parse_summary(read_text(correction_apply_log_path))

    if correction_dry != {"changed": 0, "skipped": target_count, "renamed": 0, "missing": 0, "bad": 0}:
        failures.append(f"correction dry summary mismatch: {correction_dry}")
    if correction_apply != {"changed": target_count, "skipped": 0, "renamed": renamed_expected, "missing": 0, "bad": 0}:
        failures.append(f"correction apply summary mismatch: {correction_apply}")

    metadata_rows = {normalize_address(row.get("address", "")): row for row in read_tsv(metadata_path)}
    index_rows = {normalize_address(row.get("address", "")): row for row in read_tsv(decompile_index_path)}
    xref_rows = read_tsv(xrefs_path)
    instruction_text = read_text(instructions_path)

    stale_name_hits = 0
    param_signature_hits = 0
    comment_overclaims = 0
    xref_evidence_hits = 0
    decompile_evidence_hits = 0
    return_evidence_hits = 0

    for address, target in TARGETS.items():
        row = metadata_rows.get(address)
        if not row:
            failures.append(f"{address}: missing metadata row")
            continue
        if row.get("status") != "OK":
            failures.append(f"{address}: metadata status {row.get('status')}")

        name = row.get("name", "")
        signature = unescape_tsv(row.get("signature", ""))
        comment = unescape_tsv(row.get("comment", ""))
        if name != target["name"]:
            failures.append(f"{address}: name {name!r} != {target['name']!r}")
        for previous in target["previous"]:
            if previous == name or token_present(signature, previous):
                stale_name_hits += 1
                failures.append(f"{address}: stale previous name token still present: {previous}")
        for token in target["signature"]:
            if not token_present(signature, str(token)):
                failures.append(f"{address}: signature missing {token!r}: {signature}")
        for token in target.get("forbiddenSignature", []):
            if token_present(signature, str(token)):
                param_signature_hits += 1
                failures.append(f"{address}: forbidden signature token {token!r}: {signature}")
        for token in target["comment"]:
            if not token_present(comment, str(token)):
                failures.append(f"{address}: comment missing {token!r}: {comment}")
        for token in OVERCLAIMS:
            if token_present(comment, token):
                comment_overclaims += 1
                failures.append(f"{address}: comment overclaim token {token!r}")

        index_row = index_rows.get(address)
        if not index_row or index_row.get("status") != "OK":
            failures.append(f"{address}: missing/failed decompile index row")
        decompile_path = None
        if decompile_dir.is_dir():
            matches = list(decompile_dir.glob(address[2:] + "_*.c"))
            decompile_path = matches[0] if matches else None
        decompile_text = read_text(decompile_path)
        if all(token_present(decompile_text, str(token)) for token in target["decompile"]):
            decompile_evidence_hits += 1
        else:
            failures.append(f"{address}: decompile evidence tokens missing")

        xref_text = "\n".join("\t".join(row.values()) for row in xref_rows if normalize_address(row.get("target_addr", "")) == address)
        if all(token_present(xref_text, str(token)) for token in target["xrefs"]):
            xref_evidence_hits += 1
        else:
            failures.append(f"{address}: xref evidence tokens missing")

        ret_token = str(target.get("ret", ""))
        if ret_token:
            if token_present(instruction_text, address) and token_present(instruction_text, f"RET\t{ret_token}"):
                return_evidence_hits += 1
            else:
                failures.append(f"{address}: return evidence {ret_token} missing")

    summary = {
        "targets": target_count,
        "renamedTargets": renamed_expected,
        "staleNameHits": stale_name_hits,
        "paramSignatureHits": param_signature_hits,
        "commentOverclaims": comment_overclaims,
        "xrefEvidenceHits": xref_evidence_hits,
        "decompileEvidenceHits": decompile_evidence_hits,
        "returnEvidenceHits": return_evidence_hits,
    }
    return {
        "schema": "ghidra-walker-dash-surface-correction.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": "FAIL" if failures else "PASS",
        "summary": summary,
        "inputs": {
            "correctionDryLog": relative(correction_dry_log_path),
            "correctionApplyLog": relative(correction_apply_log_path),
            "metadata": relative(metadata_path),
            "decompileIndex": relative(decompile_index_path),
            "decompileDir": relative(decompile_dir),
            "xrefs": relative(xrefs_path),
            "instructions": relative(instructions_path),
        },
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    report = build_report()
    out_path = resolve(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(
        "walker dash surface correction: "
        f"{report['status']} targets={report['summary']['targets']} "
        f"renamed={report['summary']['renamedTargets']} "
        f"failures={len(report['failures'])} out={relative(out_path)}"
    )
    if args.check and report["status"] != "PASS":
        for failure in report["failures"]:
            print(f"- {failure}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
