#!/usr/bin/env python3
"""Validate the weapon/burst provisional owner-name review tranche."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "weapon-burst-provisional-review" / "current"

TARGETS = {
    "0x005069f0": {
        "name": "ProjectileBurst__SpawnFromCurrentPreset",
        "previousName": "CEngine__SpawnProjectileBurstFromCurrentPreset",
        "signatureTokens": ["int", "__fastcall", "ProjectileBurst__SpawnFromCurrentPreset", "void * burstContext"],
        "commentTokens": [
            "Owner-neutral correction",
            "current-preset projectile-burst body",
            "burstContext +0xa0",
            "weapon event handler",
            "runtime stealth behavior",
            "remain unproven",
        ],
        "decompileTokens": [
            "ProjectileBurst__SpawnFromCurrentPreset",
            "CWorldPhysicsManager__CreateProjectile",
            "CEngine__SetProjectileTargetReader",
            "CBattleEngine__RandomizeBurstOffsetsAndAccumulateRange",
        ],
        "xrefFunctions": [
            "ProjectileBurst__SpawnFromPercentBucketFallback",
            "CWeapon__HandleFireBurstEvent",
        ],
        "instructionTokens": ["CALL", "0x004e1940", "CALL", "0x004062d0", "RET"],
    },
    "0x00506010": {
        "name": "ProjectileBurst__SpawnFromPercentBucketFallback",
        "previousName": "CGeneralVolume__SpawnBurstFromPresetWithFallback",
        "signatureTokens": ["int", "__fastcall", "ProjectileBurst__SpawnFromPercentBucketFallback", "void * burstContext"],
        "commentTokens": [
            "Owner-neutral correction",
            "percent-bucket fallback dispatcher",
            "burstContext +0xa4",
            "ProjectileBurst__SpawnFromCurrentPreset",
            "event 0x1389",
            "remain unproven",
        ],
        "decompileTokens": [
            "ProjectileBurst__SpawnFromPercentBucketFallback",
            "ProjectileBurst__SpawnFromCurrentPreset",
            "CEventManager__AddEvent_AtTime",
            "+ 0xa4",
            "+ 0x60",
            "+ 0x68",
            "+ 0xa0",
        ],
        "xrefFunctions": [
            "CUnitAI__TrySpawnOrFinalizeAttachedUnit",
            "CSentinel__UpdateFlamethrowers",
            "CGeneralVolume__DispatchMode3BurstProgressAndSpawn",
            "CGeneralVolume__UpdateCurrentEntryProgressAndRefresh",
            "CGeneralVolume__DispatchSelectedBurstPreset",
        ],
        "instructionTokens": ["CALL", "0x005069f0", "RET"],
    },
}

DEFAULT_SIGNATURE_DRY = BASE / "signature_dry.log"
DEFAULT_SIGNATURE_APPLY = BASE / "signature_apply.log"
DEFAULT_METADATA = BASE / "metadata_readback.tsv"
DEFAULT_INDEX = BASE / "decompile_readback" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_readback"
DEFAULT_XREFS = BASE / "xrefs_readback.tsv"
DEFAULT_INSTRUCTIONS = BASE / "instructions_readback.tsv"
DEFAULT_CALLER_METADATA = BASE / "caller_metadata.tsv"
DEFAULT_RAW_XREF_INSTRUCTIONS = BASE / "raw_xref_instructions.tsv"
DEFAULT_OUT = BASE / "weapon-burst-provisional-review.json"

OVERCLAIM_TOKENS = [
    "runtime behavior proven",
    "runtime stealth behavior proven",
    "stealth behavior proven",
    "source identity proven",
    "exact source identity proven",
    "cweapon::fire proven",
    "cbattleengine::weaponfired proven",
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


def xref_callers(rows: list[dict[str, str]], address: str) -> set[str]:
    wanted = normalize_address(address)
    return {
        row.get("from_function", "")
        for row in rows
        if normalize_address(row.get("target_addr", "")) == wanted
    }


def raw_callsite_count(rows: list[dict[str, str]]) -> int:
    return sum(
        1
        for row in rows
        if row.get("role") == "TARGET"
        and row.get("mnemonic") == "CALL"
        and row.get("function_name") == "<no_function>"
    )


def build_report(
    *,
    signature_dry_log_path: Path = DEFAULT_SIGNATURE_DRY,
    signature_apply_log_path: Path = DEFAULT_SIGNATURE_APPLY,
    metadata_path: Path = DEFAULT_METADATA,
    decompile_index_path: Path = DEFAULT_INDEX,
    decompile_dir: Path = DEFAULT_DECOMPILE_DIR,
    xrefs_path: Path = DEFAULT_XREFS,
    instructions_path: Path = DEFAULT_INSTRUCTIONS,
    caller_metadata_path: Path = DEFAULT_CALLER_METADATA,
    raw_xref_instructions_path: Path = DEFAULT_RAW_XREF_INSTRUCTIONS,
) -> dict[str, object]:
    signature_dry_log_path = resolve(signature_dry_log_path)
    signature_apply_log_path = resolve(signature_apply_log_path)
    metadata_path = resolve(metadata_path)
    decompile_index_path = resolve(decompile_index_path)
    decompile_dir = resolve(decompile_dir)
    xrefs_path = resolve(xrefs_path)
    instructions_path = resolve(instructions_path)
    caller_metadata_path = resolve(caller_metadata_path)
    raw_xref_instructions_path = resolve(raw_xref_instructions_path)

    failures: list[str] = []
    for label, path in (
        ("signature dry log", signature_dry_log_path),
        ("signature apply log", signature_apply_log_path),
        ("metadata read-back", metadata_path),
        ("decompile index", decompile_index_path),
        ("xref read-back", xrefs_path),
        ("instruction read-back", instructions_path),
        ("caller metadata read-back", caller_metadata_path),
        ("raw xref instruction read-back", raw_xref_instructions_path),
    ):
        if not path.is_file():
            failures.append(f"missing {label}: {relative(path)}")
    if not decompile_dir.is_dir():
        failures.append(f"missing decompile dir: {relative(decompile_dir)}")

    dry_summary = parse_update_summary(read_text(signature_dry_log_path))
    apply_summary = parse_update_summary(read_text(signature_apply_log_path))
    if dry_summary != {"updated": 0, "skipped": 2, "missing": 0, "bad": 0}:
        failures.append("signature dry summary is not clean")
    if apply_summary != {"updated": 2, "skipped": 0, "missing": 0, "bad": 0}:
        failures.append("signature apply summary is not clean")

    metadata_rows = read_tsv(metadata_path)
    index_rows = read_tsv(decompile_index_path)
    xref_rows = read_tsv(xrefs_path)
    instruction_rows = read_tsv(instructions_path)
    caller_rows = read_tsv(caller_metadata_path)
    raw_rows = read_tsv(raw_xref_instructions_path)

    target_reports: list[dict[str, object]] = []
    renamed_targets = 0
    hardened_signatures = 0
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
        if name != expected["name"] or row.get("status") != "OK":
            failures.append(f"metadata name/status mismatch for {address}")
        if name == expected["name"] and expected["previousName"] != expected["name"]:
            renamed_targets += 1
        if "param_" not in signature and "undefined" not in signature.lower():
            hardened_signatures += 1

        missing_signature_tokens = [token for token in expected["signatureTokens"] if not token_present(signature, token)]
        if missing_signature_tokens:
            failures.append(f"{address} signature tokens missing: {missing_signature_tokens}")
        missing_comment_tokens = [token for token in expected["commentTokens"] if not token_present(comment, token)]
        if missing_comment_tokens:
            failures.append(f"{address} comment tokens missing: {missing_comment_tokens}")
        if any(token_present(comment, token) for token in OVERCLAIM_TOKENS):
            failures.append(f"{address} runtime/source overclaim in comment")
            comment_overclaims += 1

        if index_row is None or index_row.get("status") != "OK":
            failures.append(f"decompile index missing/failed for {address}")

        decompile_file = decompile_file_for(decompile_dir, address)
        decompile_text = read_text(decompile_file) if decompile_file is not None else ""
        missing_decompile_tokens = [token for token in expected["decompileTokens"] if not token_present(decompile_text, token)]
        if missing_decompile_tokens:
            failures.append(f"{address} decompile tokens missing: {missing_decompile_tokens}")

        callers = xref_callers(xref_rows, address)
        missing_callers = [caller for caller in expected["xrefFunctions"] if caller not in callers]
        if missing_callers:
            failures.append(f"{address} xref callers missing: {missing_callers}")

        instruction_text = joined_instruction_text(instruction_rows, address)
        missing_instruction_tokens = [
            token for token in expected["instructionTokens"] if not token_present(instruction_text, token)
        ]
        if missing_instruction_tokens:
            failures.append(f"{address} instruction tokens missing: {missing_instruction_tokens}")

        target_reports.append(
            {
                "address": address,
                "name": name,
                "signature": signature,
                "comment": comment,
                "decompilePath": relative(decompile_file),
                "xrefCallers": sorted(callers),
            }
        )

    caller_missing_rows = [
        row for row in caller_rows
        if row.get("status") == "MISSING" and normalize_address(row.get("address", "")) in {"0x0044e093", "0x004f4bd6"}
    ]
    raw_missing = raw_callsite_count(raw_rows)
    if len(caller_missing_rows) != 2 or raw_missing != 2:
        failures.append("expected two raw caller boundaries to remain missing/unowned")

    report = {
        "schema": "ghidra-weapon-burst-provisional-review.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not failures else "FAIL",
        "summary": {
            "targets": len(TARGETS),
            "renamedTargets": renamed_targets,
            "hardenedSignatures": hardened_signatures,
            "commentOverclaims": comment_overclaims,
            "rawCallsitesWithoutFunctions": raw_missing,
            "weaponFireBreaksStealthStatus": "unresolved",
        },
        "files": {
            "signatureDryLog": relative(signature_dry_log_path),
            "signatureApplyLog": relative(signature_apply_log_path),
            "metadata": relative(metadata_path),
            "decompileIndex": relative(decompile_index_path),
            "decompileDir": relative(decompile_dir),
            "xrefs": relative(xrefs_path),
            "instructions": relative(instructions_path),
            "callerMetadata": relative(caller_metadata_path),
            "rawXrefInstructions": relative(raw_xref_instructions_path),
        },
        "targets": target_reports,
        "failures": failures,
    }
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Exit non-zero when the saved tranche is invalid.")
    parser.add_argument("--signature-dry-log", type=Path, default=DEFAULT_SIGNATURE_DRY)
    parser.add_argument("--signature-apply-log", type=Path, default=DEFAULT_SIGNATURE_APPLY)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--decompile-index", type=Path, default=DEFAULT_INDEX)
    parser.add_argument("--decompile-dir", type=Path, default=DEFAULT_DECOMPILE_DIR)
    parser.add_argument("--xrefs", type=Path, default=DEFAULT_XREFS)
    parser.add_argument("--instructions", type=Path, default=DEFAULT_INSTRUCTIONS)
    parser.add_argument("--caller-metadata", type=Path, default=DEFAULT_CALLER_METADATA)
    parser.add_argument("--raw-xref-instructions", type=Path, default=DEFAULT_RAW_XREF_INSTRUCTIONS)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(
        signature_dry_log_path=args.signature_dry_log,
        signature_apply_log_path=args.signature_apply_log,
        metadata_path=args.metadata,
        decompile_index_path=args.decompile_index,
        decompile_dir=args.decompile_dir,
        xrefs_path=args.xrefs,
        instructions_path=args.instructions,
        caller_metadata_path=args.caller_metadata,
        raw_xref_instructions_path=args.raw_xref_instructions,
    )
    out_path = resolve(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    summary = report["summary"]
    print(f"Status: {report['status']}")
    print(
        "Targets: {targets}; renamed: {renamedTargets}; hardened signatures: {hardenedSignatures}; "
        "raw caller boundaries open: {rawCallsitesWithoutFunctions}; stealth status: {weaponFireBreaksStealthStatus}".format(
            **summary
        )
    )
    print(f"Report: {relative(out_path)}")
    if report["failures"]:
        for failure in report["failures"]:
            print(f"- {failure}", file=sys.stderr)
    return 1 if args.check and report["status"] != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
