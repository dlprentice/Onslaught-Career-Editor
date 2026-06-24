#!/usr/bin/env python3
"""Validate saved Ghidra recovery of the two raw weapon-burst caller boundaries."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "weapon-burst-raw-boundary-recovery" / "current"

TARGET_ADDRESS = "0x00506010"
TARGET_NAME = "ProjectileBurst__SpawnFromPercentBucketFallback"
CURRENT_PRESET_ADDRESS = "0x005069f0"
CURRENT_PRESET_NAME = "ProjectileBurst__SpawnFromCurrentPreset"

BOUNDARIES = [
    {
        "address": "0x0044e020",
        "name": "ProjectileBurstCallerBoundary_0044e020",
        "callsite": "0x0044e093",
        "context": "list/range",
    },
    {
        "address": "0x004f4920",
        "name": "ProjectileBurstCallerBoundary_004f4920",
        "callsite": "0x004f4bd6",
        "context": "floating-point threshold/setup",
    },
]

DEFAULT_CREATE_DRY = BASE / "create_function_dry.tsv"
DEFAULT_CREATE_APPLY = BASE / "create_function_apply.tsv"
DEFAULT_METADATA = BASE / "metadata_readback.tsv"
DEFAULT_DECOMPILE_INDEX = BASE / "decompile_readback" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_readback"
DEFAULT_XREFS = BASE / "xrefs_to_00506010.tsv"
DEFAULT_INSTRUCTIONS = BASE / "callsite_instruction_readback.tsv"
DEFAULT_OUT = BASE / "weapon-burst-raw-boundary-recovery.json"

BOUNDARY_COMMENT_TOKENS = [
    "Recovered owner-neutral projectile-burst raw caller boundary",
    TARGET_NAME,
    "Proof-boundary",
    "weapon_fire_breaks_stealth",
    "runtime behavior",
]
TARGET_COMMENT_TOKENS = [
    "raw caller-boundary recovery",
    "0x0044e093",
    "0x004f4bd6",
    "weapon_fire_breaks_stealth",
    "runtime stealth behavior",
]
CURRENT_PRESET_COMMENT_TOKENS = [
    "raw percent-bucket fallback callsites",
    "ProjectileBurstCallerBoundary_0044e020",
    "ProjectileBurstCallerBoundary_004f4920",
    "weapon_fire_breaks_stealth",
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
    if value in {"", "<none>", "<no_function>", "<no_instruction>"}:
        return value
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def compact(value: str) -> str:
    return "".join(value.lower().split())


def has_token(text: str, token: str) -> bool:
    return compact(token) in compact(text)


def unescape_tsv(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_metadata(path: Path) -> dict[str, dict[str, str]]:
    rows = read_tsv(path)
    for row in rows:
        row["address"] = normalize_address(row.get("address", ""))
        row["comment"] = unescape_tsv(row.get("comment", ""))
    return {row["address"]: row for row in rows if row.get("address")}


def read_index(path: Path) -> dict[str, dict[str, str]]:
    rows = read_tsv(path)
    for row in rows:
        row["address"] = normalize_address(row.get("address", ""))
    return {row["address"]: row for row in rows if row.get("address")}


def read_create_report(path: Path) -> dict[str, dict[str, str]]:
    rows = read_tsv(path)
    for row in rows:
        row["address"] = normalize_address(row.get("address", ""))
    return {row["address"]: row for row in rows if row.get("address")}


def read_xrefs(path: Path) -> list[dict[str, str]]:
    rows = read_tsv(path)
    for row in rows:
        row["target_addr_norm"] = normalize_address(row.get("target_addr", ""))
        row["from_addr_norm"] = normalize_address(row.get("from_addr", ""))
        row["from_function_addr_norm"] = normalize_address(row.get("from_function_addr", ""))
    return rows


def read_instructions(path: Path) -> list[dict[str, str]]:
    rows = read_tsv(path)
    for row in rows:
        row["target_addr_norm"] = normalize_address(row.get("target_addr", ""))
        row["instruction_addr_norm"] = normalize_address(row.get("instruction_addr", ""))
        row["function_entry_norm"] = normalize_address(row.get("function_entry", ""))
    return rows


def find_decompile_file(decompile_dir: Path, address: str) -> Path | None:
    if not decompile_dir.is_dir():
        return None
    matches = sorted(decompile_dir.glob(f"{normalize_address(address)[2:]}_*.c"))
    return matches[0] if matches else None


def read_text(path: Path | None) -> str:
    if path is None or not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def build_report(
    *,
    create_dry_path: Path = DEFAULT_CREATE_DRY,
    create_apply_path: Path = DEFAULT_CREATE_APPLY,
    metadata_path: Path = DEFAULT_METADATA,
    decompile_index_path: Path = DEFAULT_DECOMPILE_INDEX,
    decompile_dir: Path = DEFAULT_DECOMPILE_DIR,
    xrefs_path: Path = DEFAULT_XREFS,
    instructions_path: Path = DEFAULT_INSTRUCTIONS,
) -> dict[str, object]:
    create_dry_path = resolve(create_dry_path)
    create_apply_path = resolve(create_apply_path)
    metadata_path = resolve(metadata_path)
    decompile_index_path = resolve(decompile_index_path)
    decompile_dir = resolve(decompile_dir)
    xrefs_path = resolve(xrefs_path)
    instructions_path = resolve(instructions_path)

    failures: list[str] = []
    for label, path in (
        ("create dry report", create_dry_path),
        ("create apply report", create_apply_path),
        ("metadata read-back", metadata_path),
        ("decompile index", decompile_index_path),
        ("xrefs", xrefs_path),
        ("callsite instructions", instructions_path),
    ):
        if not path.is_file():
            failures.append(f"missing {label}: {relative(path)}")
    if not decompile_dir.is_dir():
        failures.append(f"missing decompile dir: {relative(decompile_dir)}")

    create_dry = read_create_report(create_dry_path)
    create_apply = read_create_report(create_apply_path)
    metadata = read_metadata(metadata_path)
    decompile_index = read_index(decompile_index_path)
    xrefs = read_xrefs(xrefs_path)
    instructions = read_instructions(instructions_path)

    target_row = metadata.get(TARGET_ADDRESS)
    if not target_row:
        failures.append(f"{TARGET_ADDRESS}: missing target metadata row")
    else:
        if target_row.get("name") != TARGET_NAME or target_row.get("status") != "OK":
            failures.append(f"{TARGET_ADDRESS}: target metadata did not read back as {TARGET_NAME}/OK")
        target_comment = target_row.get("comment", "")
        for token in TARGET_COMMENT_TOKENS:
            if not has_token(target_comment, token):
                failures.append(f"{TARGET_ADDRESS}: target comment missing token {token!r}")

    current_preset_row = metadata.get(CURRENT_PRESET_ADDRESS)
    if not current_preset_row:
        failures.append(f"{CURRENT_PRESET_ADDRESS}: missing current-preset metadata row")
    else:
        if current_preset_row.get("name") != CURRENT_PRESET_NAME or current_preset_row.get("status") != "OK":
            failures.append(f"{CURRENT_PRESET_ADDRESS}: current-preset metadata did not read back as {CURRENT_PRESET_NAME}/OK")
        current_comment = current_preset_row.get("comment", "")
        for token in CURRENT_PRESET_COMMENT_TOKENS:
            if not has_token(current_comment, token):
                failures.append(f"{CURRENT_PRESET_ADDRESS}: current-preset comment missing token {token!r}")

    recovered: list[dict[str, object]] = []
    for boundary in BOUNDARIES:
        address = boundary["address"]
        name = boundary["name"]
        callsite = boundary["callsite"]

        dry_row = create_dry.get(address)
        if not dry_row or dry_row.get("status") != "would_create" or not has_token(dry_row.get("note", ""), name):
            failures.append(f"{address}: dry report did not prove would_create for {name}")

        apply_row = create_apply.get(address)
        if not apply_row or apply_row.get("status") != "created" or apply_row.get("name") != name:
            failures.append(f"{address}: apply report did not prove created/renamed {name}")

        meta_row = metadata.get(address)
        if not meta_row:
            failures.append(f"{address}: missing metadata read-back row")
        else:
            if meta_row.get("name") != name or meta_row.get("status") != "OK":
                failures.append(f"{address}: metadata did not read back as {name}/OK")
            comment = meta_row.get("comment", "")
            for token in [*BOUNDARY_COMMENT_TOKENS, callsite, boundary["context"]]:
                if not has_token(comment, token):
                    failures.append(f"{address}: comment missing token {token!r}")

        index_row = decompile_index.get(address)
        if not index_row or index_row.get("status") != "OK" or index_row.get("name") != name:
            failures.append(f"{address}: missing OK decompile index row for {name}")
        decompile_text = read_text(find_decompile_file(decompile_dir, address))
        if not has_token(decompile_text, name) or not has_token(decompile_text, TARGET_NAME):
            failures.append(f"{address}: decompile read-back missing boundary name or target helper call")

        xref_match = next(
            (
                row
                for row in xrefs
                if row["target_addr_norm"] == TARGET_ADDRESS
                and row["from_addr_norm"] == callsite
                and row["from_function_addr_norm"] == address
                and row.get("from_function") == name
                and row.get("ref_type") == "UNCONDITIONAL_CALL"
            ),
            None,
        )
        if not xref_match:
            failures.append(f"{callsite}: xref to {TARGET_NAME} did not resolve from {name}")

        instruction_match = next(
            (
                row
                for row in instructions
                if row["target_addr_norm"] == callsite
                and row["instruction_addr_norm"] == callsite
                and row["function_entry_norm"] == address
                and row.get("function_name") == name
                and row.get("mnemonic") == "CALL"
                and normalize_address(row.get("operands", "")) == TARGET_ADDRESS
            ),
            None,
        )
        if not instruction_match:
            failures.append(f"{callsite}: instruction read-back did not resolve inside {name}")

        recovered.append(
            {
                "address": address,
                "name": name,
                "callsite": callsite,
                "context": boundary["context"],
                "created": bool(apply_row),
                "xrefResolved": bool(xref_match),
                "instructionResolved": bool(instruction_match),
            }
        )

    report: dict[str, object] = {
        "schema": "ghidra.weapon_burst_raw_boundary_recovery.v1",
        "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not failures else "FAIL",
        "targetAddress": TARGET_ADDRESS,
        "targetName": TARGET_NAME,
        "currentPresetAddress": CURRENT_PRESET_ADDRESS,
        "currentPresetName": CURRENT_PRESET_NAME,
        "recoveredBoundaries": recovered,
        "weaponFireBreaksStealthStatus": "unresolved",
        "proofBoundary": [
            "exact CWeapon::Fire identity remains unproven",
            "exact CBattleEngine::WeaponFired retail identity remains unproven",
            "weapon_fire_breaks_stealth remains unresolved",
            "runtime cloak activation and fire-while-cloaked behavior remain unproven",
            "locals/types/signatures/tags are not claimed complete",
        ],
        "inputs": {
            "createDry": relative(create_dry_path),
            "createApply": relative(create_apply_path),
            "metadata": relative(metadata_path),
            "decompileIndex": relative(decompile_index_path),
            "xrefs": relative(xrefs_path),
            "instructions": relative(instructions_path),
        },
        "failures": failures,
    }
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Return non-zero if the probe fails")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output JSON path")
    args = parser.parse_args(argv)

    report = build_report()
    out_path = resolve(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print("Ghidra weapon-burst raw boundary recovery probe")
    print(f"Status: {report['status']}")
    print(f"Output: {relative(out_path)}")
    print(f"Recovered boundaries: {len(report['recoveredBoundaries'])}")
    print(f"weapon_fire_breaks_stealth: {report['weaponFireBreaksStealthStatus']}")
    if report["failures"]:
        print("Failures:")
        for failure in report["failures"]:
            print(f"- {failure}")
    return 1 if args.check and report["status"] != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
