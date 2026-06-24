#!/usr/bin/env python3
"""Validate the saved BattleEngine helper signature tranche."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "battleengine-helper-signature-tranche" / "current"

TARGETS = {
    "0x00405a40": {
        "name": "CBattleEngine__dtor_base",
        "signatureTokens": ["void", "__fastcall", "CBattleEngine__dtor_base", "void * this"],
        "commentTokens": ["BattleEngine destructor-base cleanup", "tracked projectile set +0x294", "runtime behavior proof"],
        "decompileTokens": ["CBattleEngine__dtor_base", "CSPtrSet__Clear", "CUnit__scalar_deleting_dtor_004f84e0", "0x294"],
    },
    "0x00405f60": {
        "name": "CBattleEngine__scalar_deleting_dtor",
        "signatureTokens": ["void *", "__thiscall", "CBattleEngine__scalar_deleting_dtor", "void * this", "byte flags"],
        "commentTokens": ["scalar-deleting destructor wrapper", "delete flag bit 0", "runtime behavior proof"],
        "decompileTokens": ["CBattleEngine__scalar_deleting_dtor", "CBattleEngine__dtor_base", "OID__FreeObject", "return this"],
    },
    "0x00405f80": {
        "name": "CBattleEngine__VFunc_02_00405f80",
        "signatureTokens": ["void", "__fastcall", "CBattleEngine__VFunc_02_00405f80", "void * this"],
        "commentTokens": ["BattleEngine finalization-vfunc", "vibration", "runtime behavior proof"],
        "decompileTokens": [
            "CBattleEngine__VFunc_02_00405f80",
            "CGame__DispatchVibrationWithCareerGate",
            "CUnit__FinalizeLinkedUnitStateAndClear",
            "VFuncSlot_02_004f95d0",
        ],
    },
    "0x004063a0": {
        "name": "CBattleEngine__GetFloatAt0x118_AsDouble",
        "signatureTokens": ["double", "__fastcall", "CBattleEngine__GetFloatAt0x118_AsDouble", "void * this"],
        "commentTokens": ["field +0x118 float accessor", "runtime behavior proof"],
        "decompileTokens": ["CBattleEngine__GetFloatAt0x118_AsDouble", "0x118"],
    },
    "0x004063b0": {
        "name": "CBattleEngine__UpdateWeaponEffect",
        "signatureTokens": ["void", "__fastcall", "CBattleEngine__UpdateWeaponEffect", "void * this"],
        "commentTokens": ["weapon/effect object helper", "BattleEngine.cpp line 0x1f5", "runtime behavior proof"],
        "decompileTokens": [
            "CBattleEngine__UpdateWeaponEffect",
            "OID__AllocObject",
            "0x1f5",
            "PTR_VFuncSlot_00_00426340_005d88cc",
        ],
    },
    "0x00406460": {
        "name": "CBattleEngine__SwapPrimarySecondaryPartReadersForState",
        "signatureTokens": [
            "void",
            "__fastcall",
            "CBattleEngine__SwapPrimarySecondaryPartReadersForState",
            "void * this",
        ],
        "commentTokens": ["primary/secondary reader swap", "+0x5ec", "runtime behavior proof"],
        "decompileTokens": [
            "CBattleEngine__SwapPrimarySecondaryPartReadersForState",
            "CMCMech__Reset",
            "CInfluenceMap__SetTrackedThingAndClearCachedObject",
            "0x5ec",
        ],
    },
    "0x00406560": {
        "name": "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles",
        "signatureTokens": [
            "void",
            "__fastcall",
            "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles",
            "void * this",
        ],
        "commentTokens": [
            "tracked-target projectile helper",
            "tracked-target set +0x294",
            "CBattleEngine__AddProjectile",
            "does not prove exact CBattleEngine::WeaponFired identity",
            "weapon-fired stealth reset behavior",
        ],
        "decompileTokens": [
            "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles",
            "CBattleEngine__AddProjectile",
            "CBattleEngine__IsWeaponModeCompatibleWithMountState",
            "CSPtrSet__First",
        ],
    },
    "0x00406fc0": {
        "name": "CBattleEngine__AddProjectile",
        "signatureTokens": [
            "void",
            "__thiscall",
            "CBattleEngine__AddProjectile",
            "void * this",
            "void * target",
            "float lifetime",
            "int modeFlag",
        ],
        "commentTokens": ["tracked projectile insertion", "duplicate target", "BattleEngine.cpp line 0x332", "runtime behavior proof"],
        "decompileTokens": [
            "CBattleEngine__AddProjectile",
            "CGenericActiveReader__SetReader",
            "OID__AllocObject",
            "0x332",
            "CSPtrSet__AddToTail",
        ],
    },
}

DEFAULT_RENAME_DRY = BASE / "rename_dry.log"
DEFAULT_RENAME_APPLY = BASE / "rename_apply.log"
DEFAULT_SIGNATURE_DRY = BASE / "signature_dry.log"
DEFAULT_SIGNATURE_APPLY = BASE / "signature_apply.log"
DEFAULT_COMMENTS_DRY = BASE / "comments_dry.log"
DEFAULT_COMMENTS_APPLY = BASE / "comments_apply.log"
DEFAULT_METADATA = BASE / "metadata_readback.tsv"
DEFAULT_INDEX = BASE / "decompile_readback" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_readback"
DEFAULT_XREFS = BASE / "xrefs_readback.tsv"
DEFAULT_INSTRUCTIONS = BASE / "instructions_readback.tsv"
DEFAULT_OUT = BASE / "battleengine-helper-signature-tranche.json"

OVERCLAIM_TOKENS = [
    "runtime behavior proven",
    "source identity proven",
    "exact source identity proven",
    "this proves exact",
    "proves exact cbattleengine::weaponfired",
    "weapon-fired stealth reset proven",
    "weapon_fire_breaks_stealth closed",
]

STALE_NAMES = [
    "CBattleEngine__scalar_deleting_dtor_00405a40",
    "CBattleEngine__VFunc_01_00405f60",
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


def parse_apply_summary(log_text: str) -> dict[str, int]:
    match = re.search(r"applied=(\d+)\s+skipped=(\d+)\s+missing=(\d+)\s+bad=(\d+)", log_text)
    if not match:
        return {"applied": -1, "skipped": -1, "missing": -1, "bad": -1}
    return {
        "applied": int(match.group(1)),
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


def rows_for(rows: list[dict[str, str]], address: str) -> list[dict[str, str]]:
    wanted = normalize_address(address)
    return [row for row in rows if normalize_address(row.get("target_addr", "")) == wanted]


def build_report(
    *,
    rename_dry_log_path: Path = DEFAULT_RENAME_DRY,
    rename_apply_log_path: Path = DEFAULT_RENAME_APPLY,
    signature_dry_log_path: Path = DEFAULT_SIGNATURE_DRY,
    signature_apply_log_path: Path = DEFAULT_SIGNATURE_APPLY,
    comments_dry_log_path: Path = DEFAULT_COMMENTS_DRY,
    comments_apply_log_path: Path = DEFAULT_COMMENTS_APPLY,
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
    comments_dry_log_path = resolve(comments_dry_log_path)
    comments_apply_log_path = resolve(comments_apply_log_path)
    metadata_path = resolve(metadata_path)
    decompile_index_path = resolve(decompile_index_path)
    decompile_dir = resolve(decompile_dir)
    xrefs_path = resolve(xrefs_path)
    instructions_path = resolve(instructions_path)

    failures: list[str] = []
    for label, path in (
        ("rename dry log", rename_dry_log_path),
        ("rename apply log", rename_apply_log_path),
        ("signature dry log", signature_dry_log_path),
        ("signature apply log", signature_apply_log_path),
        ("comment dry log", comments_dry_log_path),
        ("comment apply log", comments_apply_log_path),
        ("metadata read-back", metadata_path),
        ("decompile index", decompile_index_path),
        ("xref read-back", xrefs_path),
        ("instruction read-back", instructions_path),
    ):
        if not path.is_file():
            failures.append(f"missing {label}: {relative(path)}")
    if not decompile_dir.is_dir():
        failures.append(f"missing decompile dir: {relative(decompile_dir)}")

    rename_dry = read_text(rename_dry_log_path)
    rename_apply = read_text(rename_apply_log_path)
    signature_dry = read_text(signature_dry_log_path)
    signature_apply = read_text(signature_apply_log_path)
    comments_dry = read_text(comments_dry_log_path)
    comments_apply = read_text(comments_apply_log_path)
    metadata_rows = read_tsv(metadata_path)
    index_rows = read_tsv(decompile_index_path)
    xref_rows = read_tsv(xrefs_path)
    instruction_rows = read_tsv(instructions_path)

    rename_dry_summary = parse_apply_summary(rename_dry)
    rename_apply_summary = parse_apply_summary(rename_apply)
    dry_summary = parse_update_summary(signature_dry)
    apply_summary = parse_update_summary(signature_apply)
    comments_dry_summary = parse_apply_summary(comments_dry)
    comments_apply_summary = parse_apply_summary(comments_apply)

    if rename_dry_summary != {"applied": 0, "skipped": 2, "missing": 0, "bad": 0}:
        failures.append("rename dry summary is not clean")
    if rename_apply_summary != {"applied": 2, "skipped": 0, "missing": 0, "bad": 0}:
        failures.append("rename apply summary is not clean")
    if dry_summary != {"updated": 0, "skipped": 8, "missing": 0, "bad": 0}:
        failures.append("signature dry summary is not clean")
    if apply_summary != {"updated": 8, "skipped": 0, "missing": 0, "bad": 0}:
        failures.append("signature apply summary is not clean")
    if comments_dry_summary != {"applied": 0, "skipped": 8, "missing": 0, "bad": 0}:
        failures.append("comment dry summary is not clean")
    if comments_apply_summary != {"applied": 8, "skipped": 0, "missing": 0, "bad": 0}:
        failures.append("comment apply summary is not clean")

    target_reports: list[dict[str, object]] = []
    stale_signature_count = 0
    comment_overclaims = 0
    stale_name_count = 0
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
        if name in STALE_NAMES:
            stale_name_count += 1
            failures.append(f"stale name remains at {address}: {name}")
        if "param_" in signature or signature.startswith("undefined "):
            stale_signature_count += 1
        missing_signature_tokens = [token for token in expected["signatureTokens"] if not token_present(signature, token)]
        if missing_signature_tokens:
            failures.append(f"signature tokens missing at {address}: {missing_signature_tokens}")
        missing_comment_tokens = [token for token in expected["commentTokens"] if token not in comment]
        if missing_comment_tokens:
            failures.append(f"comment tokens missing at {address}: {missing_comment_tokens}")
        overclaim_hits = [token for token in OVERCLAIM_TOKENS if token in comment.lower()]
        if overclaim_hits:
            comment_overclaims += 1
            failures.append(f"weapon/runtime overclaim in comment at {address}: {overclaim_hits}")

        if index_row is None or index_row.get("name") != expected["name"] or index_row.get("status") != "OK":
            failures.append(f"decompile index mismatch for {address}")
        decompile_file = decompile_file_for(decompile_dir, address)
        decompile_text = read_text(decompile_file) if decompile_file else ""
        if not decompile_file:
            failures.append(f"missing decompile file for {address}")
        else:
            for token in expected["decompileTokens"]:
                if not token_present(decompile_text, token):
                    failures.append(f"decompile token missing at {address}: {token}")

        target_reports.append(
            {
                "address": address,
                "name": name,
                "signature": signature,
                "commentPresent": bool(comment),
                "xrefRows": len(rows_for(xref_rows, address)),
                "instructionRows": len(rows_for(instruction_rows, address)),
            }
        )

    if len(xref_rows) < len(TARGETS):
        failures.append(f"xref row count too low: {len(xref_rows)}")
    if len(instruction_rows) < len(TARGETS):
        failures.append(f"instruction row count too low: {len(instruction_rows)}")

    report = {
        "status": "PASS" if not failures else "FAIL",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "classification": "battleengine-helper-signature-tranche-saved" if not failures else "battleengine-helper-signature-tranche-invalid",
        "summary": {
            "targets": len(TARGETS),
            "renamedTargets": rename_apply_summary["applied"] if rename_apply_summary["applied"] >= 0 else 0,
            "signatureHardenedTargets": len(TARGETS) - stale_signature_count,
            "staleParamOrUndefinedSignatures": stale_signature_count,
            "staleNames": stale_name_count,
            "commentOverclaims": comment_overclaims,
            "xrefRows": len(xref_rows),
            "instructionRows": len(instruction_rows),
            "weaponFiredStealthStatus": "unresolved",
        },
        "summaries": {
            "renameDry": rename_dry_summary,
            "renameApply": rename_apply_summary,
            "signatureDry": dry_summary,
            "signatureApply": apply_summary,
            "commentsDry": comments_dry_summary,
            "commentsApply": comments_apply_summary,
        },
        "targets": target_reports,
        "files": {
            "renameDryLog": relative(rename_dry_log_path),
            "renameApplyLog": relative(rename_apply_log_path),
            "signatureDryLog": relative(signature_dry_log_path),
            "signatureApplyLog": relative(signature_apply_log_path),
            "commentsDryLog": relative(comments_dry_log_path),
            "commentsApplyLog": relative(comments_apply_log_path),
            "metadata": relative(metadata_path),
            "decompileIndex": relative(decompile_index_path),
            "decompileDir": relative(decompile_dir),
            "xrefs": relative(xrefs_path),
            "instructions": relative(instructions_path),
        },
        "failures": failures,
        "notProven": [
            "Exact retail identity for CBattleEngine::WeaponFired",
            "Retail weapon-fired stealth reset behavior",
            "Runtime cloak activation or fire-while-cloaked behavior",
            "Concrete CBattleEngine field layout or structure typing",
            "Local-variable recovery, tags, or full static-binary RE completion",
            "Rebuild parity",
        ],
    }
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="return non-zero if validation fails")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="JSON output path")
    args = parser.parse_args(argv)

    report = build_report()
    out_path = resolve(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"BattleEngine helper signature tranche: {report['status']}")
    print(f"Targets: {report['summary']['targets']}")
    print(f"Renamed targets: {report['summary']['renamedTargets']}")
    print(f"Signature-hardened targets: {report['summary']['signatureHardenedTargets']}")
    print(f"Stale names: {report['summary']['staleNames']}")
    print(f"Stale param/undefined signatures: {report['summary']['staleParamOrUndefinedSignatures']}")
    print(f"Comment overclaims: {report['summary']['commentOverclaims']}")
    print(f"Weapon-fired stealth status: {report['summary']['weaponFiredStealthStatus']}")
    print(f"Xref rows: {report['summary']['xrefRows']}")
    print(f"Instruction rows: {report['summary']['instructionRows']}")
    print(f"Wrote {relative(out_path)}")
    if report["failures"]:
        print("Failures:")
        for failure in report["failures"]:
            print(f"- {failure}")
    return 1 if args.check and report["status"] != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
