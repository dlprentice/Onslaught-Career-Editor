#!/usr/bin/env python3
"""Validate the saved weapon/burst signature-hardening tranche."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "signature-debt-tranche4" / "current"

TARGETS = {
    "0x00506930": {
        "name": "CWeapon__HandleFireBurstEvent",
        "mode": "hardened",
        "signatureTokens": ["void", "__thiscall", "CWeapon__HandleFireBurstEvent", "void * this", "void * eventRecord"],
        "commentTokens": ["Signature hardening", "event id 0x1389", "not exact source CWeapon::Fire", "not runtime stealth proof"],
        "instructionTokens": ["MOV", "[ESP + 0x4]", "0x1389", "CALL", "0x005069f0", "RET", "0x4"],
        "decompileTokens": ["CWeapon__HandleFireBurstEvent", "CEngine__SpawnProjectileBurstFromCurrentPreset", "CEventManager__AddEvent_AtTime"],
    },
    "0x00505f70": {
        "name": "CWeapon__scalar_deleting_dtor",
        "mode": "hardened",
        "signatureTokens": ["void *", "__thiscall", "CWeapon__scalar_deleting_dtor", "void * this", "byte flags"],
        "commentTokens": ["Signature hardening", "scalar deleting destructor", "flags bit 0", "not weapon-fire or stealth behavior proof"],
        "instructionTokens": ["CALL", "0x00505f90", "TEST", "0x1", "CALL", "0x00549220", "RET", "0x4"],
        "decompileTokens": ["CWeapon__scalar_deleting_dtor", "CWeapon__DetachFromSetAndShutdownMonitor", "OID__FreeObject"],
    },
    "0x005069f0": {
        "name": "CEngine__SpawnProjectileBurstFromCurrentPreset",
        "mode": "provisional",
        "signatureTokens": ["int", "__fastcall", "CEngine__SpawnProjectileBurstFromCurrentPreset", "void * param_1"],
        "commentTokens": ["Deferral note", "current-preset projectile-burst body", "provisional owner/name", "runtime stealth behavior remain unproven"],
        "instructionTokens": ["CALL", "0x004e1940"],
        "decompileTokens": ["CEngine__SpawnProjectileBurstFromCurrentPreset", "CWorldPhysicsManager__CreateProjectile"],
    },
    "0x00506010": {
        "name": "CGeneralVolume__SpawnBurstFromPresetWithFallback",
        "mode": "provisional",
        "signatureTokens": ["int", "__fastcall", "CGeneralVolume__SpawnBurstFromPresetWithFallback", "void * param_1"],
        "commentTokens": ["Deferral note", "shared preset fallback dispatcher", "provisional owner/name", "Not source weapon-fire identity"],
        "instructionTokens": ["0x51eb851f", "CALL", "0x00406d20"],
        "decompileTokens": ["CGeneralVolume__SpawnBurstFromPresetWithFallback", "CEngine__SpawnProjectileBurstFromCurrentPreset"],
    },
}

DEFAULT_SIGNATURE_DRY = BASE / "signature_dry.log"
DEFAULT_SIGNATURE_APPLY = BASE / "signature_apply.log"
DEFAULT_COMMENTS_DRY = BASE / "comments_dry.log"
DEFAULT_COMMENTS_APPLY = BASE / "comments_apply.log"
DEFAULT_METADATA = BASE / "metadata_readback.tsv"
DEFAULT_INDEX = BASE / "decompile_readback" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_readback"
DEFAULT_XREFS = BASE / "xrefs.tsv"
DEFAULT_INSTRUCTIONS = BASE / "instructions.tsv"
DEFAULT_OUT = BASE / "weapon-burst-signature-tranche.json"

OVERCLAIM_TOKENS = [
    "runtime behavior proven",
    "runtime stealth proven",
    "stealth behavior proven",
    "source identity proven",
    "exact source identity proven",
    "weapon fire proven",
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


def parse_comment_summary(log_text: str) -> dict[str, int]:
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


def instruction_rows_for(rows: list[dict[str, str]], address: str) -> list[dict[str, str]]:
    wanted = normalize_address(address)
    return [row for row in rows if normalize_address(row.get("target_addr", "")) == wanted]


def build_report(
    *,
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

    signature_dry = read_text(signature_dry_log_path)
    signature_apply = read_text(signature_apply_log_path)
    comments_dry = read_text(comments_dry_log_path)
    comments_apply = read_text(comments_apply_log_path)
    metadata_rows = read_tsv(metadata_path)
    index_rows = read_tsv(decompile_index_path)
    xref_rows = read_tsv(xrefs_path)
    instruction_rows = read_tsv(instructions_path)

    dry_summary = parse_update_summary(signature_dry)
    apply_summary = parse_update_summary(signature_apply)
    comments_dry_summary = parse_comment_summary(comments_dry)
    comments_apply_summary = parse_comment_summary(comments_apply)
    if dry_summary != {"updated": 0, "skipped": 2, "missing": 0, "bad": 0}:
        failures.append("signature dry summary is not clean")
    if apply_summary != {"updated": 2, "skipped": 0, "missing": 0, "bad": 0}:
        failures.append("signature apply summary is not clean")
    if comments_dry_summary != {"applied": 0, "skipped": 4, "missing": 0, "bad": 0}:
        failures.append("comment dry summary is not clean")
    if comments_apply_summary != {"applied": 4, "skipped": 0, "missing": 0, "bad": 0}:
        failures.append("comment apply summary is not clean")

    target_reports: list[dict[str, object]] = []
    stale_hardened = 0
    provisional_targets = 0
    comment_overclaims = 0
    for address, expected in TARGETS.items():
        row = find_row(metadata_rows, "address", address)
        index_row = find_row(index_rows, "address", address)
        if row is None:
            failures.append(f"metadata missing {address}")
            continue
        signature = row.get("signature", "")
        comment = row.get("comment", "")
        mode = expected["mode"]
        if row.get("name") != expected["name"] or row.get("status") != "OK":
            failures.append(f"metadata name/status mismatch for {address}")
        if mode == "hardened" and signature.lower().startswith("undefined"):
            stale_hardened += 1
            failures.append(f"stale undefined signature remains at hardened target {address}")
        if mode == "provisional":
            provisional_targets += 1
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
        instruction_text = "\n".join(
            "\t".join(row.get(key, "") for key in ("mnemonic", "operands", "flow_type"))
            for row in instruction_rows_for(instruction_rows, address)
        )
        missing_instruction_tokens = [token for token in expected["instructionTokens"] if not token_present(instruction_text, token)]
        if missing_instruction_tokens:
            failures.append(f"instruction tokens missing at {address}: {missing_instruction_tokens}")
        target_reports.append(
            {
                "address": address,
                "name": row.get("name"),
                "mode": mode,
                "signature": signature,
                "commentPresent": bool(comment),
                "xrefRows": sum(
                    1
                    for xref in xref_rows
                    if normalize_address(xref.get("target_addr", "")) == normalize_address(address)
                ),
                "instructionRows": len(instruction_rows_for(instruction_rows, address)),
            }
        )

    report = {
        "status": "PASS" if not failures else "FAIL",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "classification": "weapon-burst-signature-tranche-saved" if not failures else "weapon-burst-signature-tranche-invalid",
        "summary": {
            "targets": len(TARGETS),
            "signatureHardenedTargets": sum(1 for item in TARGETS.values() if item["mode"] == "hardened") - stale_hardened,
            "provisionalTargets": provisional_targets,
            "staleHardenedSignatures": stale_hardened,
            "commentOverclaims": comment_overclaims,
            "xrefRows": len(xref_rows),
            "instructionRows": len(instruction_rows),
        },
        "summaries": {
            "signatureDry": dry_summary,
            "signatureApply": apply_summary,
            "commentsDry": comments_dry_summary,
            "commentsApply": comments_apply_summary,
        },
        "targets": target_reports,
        "files": {
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
        "notProven": [
            "exact source CWeapon::Fire identity",
            "exact CBattleEngine::WeaponFired identity",
            "weapon_fire_breaks_stealth closure",
            "runtime stealth behavior",
            "final owner/name for the inner projectile-burst body",
            "final owner/name for the shared preset fallback dispatcher",
            "full signature-debt closure",
        ],
        "failures": failures,
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Exit non-zero when validation fails.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Write report JSON to this path.")
    args = parser.parse_args()

    report = build_report()
    out_path = resolve(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print("Ghidra weapon/burst signature tranche probe")
    print(f"Status: {report['status']}")
    print(f"Output: {relative(out_path)}")
    print(
        "Targets: {targets}; hardened: {signatureHardenedTargets}; provisional: {provisionalTargets}; xref rows: {xrefRows}; instruction rows: {instructionRows}".format(
            **report["summary"]
        )
    )
    if report["failures"]:
        print("Failures:")
        for failure in report["failures"]:
            print(f"- {failure}")

    return 1 if args.check and report["status"] != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
