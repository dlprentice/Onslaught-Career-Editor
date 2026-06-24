#!/usr/bin/env python3
"""Validate Wave475 GeneralVolume parameter-tail hardening."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave475-generalvolume-param-tail"

EXPECTED_SIGNATURES = {
    "0x00411b90": "void __fastcall CGeneralVolume__DispatchSelectedBurstPreset(void * general_volume)",
    "0x00411bf0": "void __fastcall CGeneralVolume__DispatchMode3BurstProgressAndSpawn(void * general_volume)",
    "0x00412240": "int __fastcall CGeneralVolume__GetMode3CurrentEntryRoundedSlotValue(void * general_volume)",
    "0x00412420": "short * __fastcall CGeneralVolume__GetMode3CurrentEntryDisplayString(void * general_volume)",
    "0x00412830": "void __thiscall CGeneralVolume__DisableLinkedEntriesByNameAndReselect(void * this, char * entry_name)",
    "0x00413660": "void __thiscall CGeneralVolume__ApplyYawInputByWeaponClass(void * this, int axis_input)",
    "0x004136e0": "void __thiscall CGeneralVolume__ApplyPitchInputByWeaponClass(void * this, int axis_input)",
}
EXPECTED_NAMES = {
    "0x00411b90": "CGeneralVolume__DispatchSelectedBurstPreset",
    "0x00411bf0": "CGeneralVolume__DispatchMode3BurstProgressAndSpawn",
    "0x00412240": "CGeneralVolume__GetMode3CurrentEntryRoundedSlotValue",
    "0x00412420": "CGeneralVolume__GetMode3CurrentEntryDisplayString",
    "0x00412830": "CGeneralVolume__DisableLinkedEntriesByNameAndReselect",
    "0x00413660": "CGeneralVolume__ApplyYawInputByWeaponClass",
    "0x004136e0": "CGeneralVolume__ApplyPitchInputByWeaponClass",
}
EXPECTED_TAGS = {
    "0x00411b90": {
        "static-reaudit",
        "generalvolume-param-tail-wave475",
        "retail-binary-evidence",
        "general-volume",
        "mode3-burst",
        "selected-entry",
        "signature-corrected",
        "comment-hardened",
    },
    "0x00411bf0": {
        "static-reaudit",
        "generalvolume-param-tail-wave475",
        "retail-binary-evidence",
        "general-volume",
        "mode3-burst",
        "progress",
        "signature-corrected",
        "comment-hardened",
    },
    "0x00412240": {
        "static-reaudit",
        "generalvolume-param-tail-wave475",
        "retail-binary-evidence",
        "general-volume",
        "mode3-burst",
        "hud-value",
        "signature-corrected",
        "comment-hardened",
    },
    "0x00412420": {
        "static-reaudit",
        "generalvolume-param-tail-wave475",
        "retail-binary-evidence",
        "general-volume",
        "mode3-burst",
        "hud-string",
        "signature-corrected",
        "comment-hardened",
    },
    "0x00412830": {
        "static-reaudit",
        "generalvolume-param-tail-wave475",
        "retail-binary-evidence",
        "general-volume",
        "entry-selection",
        "string-compare",
        "signature-corrected",
        "comment-hardened",
    },
    "0x00413660": {
        "static-reaudit",
        "generalvolume-param-tail-wave475",
        "retail-binary-evidence",
        "general-volume",
        "axis-input",
        "yaw",
        "signature-corrected",
        "comment-hardened",
    },
    "0x004136e0": {
        "static-reaudit",
        "generalvolume-param-tail-wave475",
        "retail-binary-evidence",
        "general-volume",
        "axis-input",
        "pitch",
        "signature-corrected",
        "comment-hardened",
    },
}
COMMENT_TOKENS = {
    "0x00411b90": ["Wave475", "CGeneralVolume-like list context", "+0x588", "+0x10", "+0x9c", "runtime weapon behavior"],
    "0x00411bf0": ["Wave475", "mode-3 burst progress", "+0x52c", "+0x544", "+0x55c", "+0x588", "runtime weapon behavior"],
    "0x00412240": ["Wave475", "+0x24", "+0x55c", "+0x52c", "FISTP", "runtime HUD behavior"],
    "0x00412420": ["Wave475", "CText__GetStringById", "entry +0xa4 +0x3c", "runtime HUD behavior"],
    "0x00412830": ["Wave475", "RET 0x4", "entry_name", "+0xa4", "+0x9c", "0x00411e70", "exact helper identity"],
    "0x00413660": ["Wave475", "RET 0x4", "0x004d337b", "axis_input", "+0x278", "DAT_005d8cd8", "runtime control behavior"],
    "0x004136e0": ["Wave475", "RET 0x4", "0x004d3390", "axis_input", "+0x280", "DAT_005d8c90", "runtime control behavior"],
}
DECOMPILE_TOKENS = {
    "0x00411b90": ["general_volume", "ProjectileBurst__SpawnFromPercentBucketFallback", "+ 0x588", "+ 0x9c"],
    "0x00411bf0": [
        "general_volume",
        "CSPtrSet__First",
        "CEngine__ClampBurstStartTimeFloorNow",
        "ProjectileBurst__SpawnFromPercentBucketFallback",
        "+ 0x588",
    ],
    "0x00412240": ["general_volume", "ROUND", "+ 0x52c", "+ 0x55c"],
    "0x00412420": ["general_volume", "CText__GetStringById", "g_Text", "+ 0x3c"],
    "0x00412830": ["entry_name", "(byte *)entry_name", "+ 0x9c", "CBattleEngineJetPart__ChangeWeapon"],
    "0x00413660": ["axis_input", "+ 0x278", "_DAT_005d8cd8", "CGeneralVolume__ToDoubleIdentity"],
    "0x004136e0": ["axis_input", "+ 0x280", "_DAT_005d8c90", "CGeneralVolume__ToDoubleIdentity"],
}
EXPECTED_XREFS = {
    ("0x00411b90", "0x00409f6a", "CGeneralVolume__Reset588AndDispatchModeSpecific_13CC0_or_11B90"),
    ("0x00411bf0", "0x00409f11", "CGeneralVolume__DispatchModeSpecificReset_13CF0_or_11BF0"),
    ("0x00412240", "0x0040c47a", "CBattleEngine__GetWeaponAmmoCount"),
    ("0x00412420", "0x0040c56a", "CBattleEngine__GetWeaponName"),
    ("0x00412830", "0x0040dc7b", "CBattleEngine__DisableVolumeEntryGroupsByNameAndReselect"),
    ("0x00413660", "0x004d337b", "<no_function>"),
    ("0x004136e0", "0x004d3390", "<no_function>"),
}
EXPECTED_DRY = {
    "updated": 0,
    "skipped": 7,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}
EXPECTED_APPLY = {
    "updated": 7,
    "skipped": 0,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}
OVERCLAIMS = (
    "runtime weapon behavior proven",
    "runtime hud behavior proven",
    "runtime control behavior proven",
    "exact source identity proven",
    "exact helper identity proven",
    "fully re'ed",
)


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if not value or value.startswith("<"):
        return value
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


def unescape(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        for key in ("address", "target_addr", "from_addr", "from_function_addr", "instruction_addr", "function_entry"):
            if key in row and row[key]:
                row[key] = normalize_address(row[key])
        if "comment" in row:
            row["comment"] = unescape(row["comment"])
    return rows


def row_by_address(rows: list[dict[str, str]], address: str, key: str = "address") -> dict[str, str] | None:
    wanted = normalize_address(address)
    for row in rows:
        if normalize_address(row.get(key, "")) == wanted:
            return row
    return None


def decompile_text_for(base: Path, address: str) -> str:
    directory = base / "post-decomp"
    if not directory.is_dir():
        return ""
    wanted = normalize_address(address)[2:]
    for path in directory.glob(f"{wanted}_*.c"):
        return read_text(path)
    return ""


def parse_summary(path: Path) -> dict[str, int]:
    text = read_text(path)
    match = re.search(
        r"updated=(?P<updated>\d+) skipped=(?P<skipped>\d+) created=(?P<created>\d+) "
        r"would_create=(?P<would_create>\d+) renamed=(?P<renamed>\d+) would_rename=(?P<would_rename>\d+) "
        r"missing=(?P<missing>\d+) bad=(?P<bad>\d+)",
        text,
    )
    if not match:
        return {}
    return {key: int(value) for key, value in match.groupdict().items()}


def check_summary(path: Path, expected: dict[str, int], label: str, failures: list[str]) -> None:
    actual = parse_summary(path)
    if actual != expected:
        failures.append(f"{label}: expected summary {expected}, got {actual or '<missing>'}")
    if "REPORT: Save succeeded" not in read_text(path):
        failures.append(f"{label}: missing REPORT: Save succeeded")


def check_metadata(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_metadata.tsv")
    if len(rows) != 7:
        failures.append(f"post_metadata.tsv: expected 7 rows, got {len(rows)}")
    for address, expected_signature in EXPECTED_SIGNATURES.items():
        row = row_by_address(rows, address)
        if row is None:
            failures.append(f"{address}: missing metadata row")
            continue
        if row.get("name") != EXPECTED_NAMES[address]:
            failures.append(f"{address}: expected name {EXPECTED_NAMES[address]}, got {row.get('name')}")
        if row.get("signature") != expected_signature:
            failures.append(f"{address}: expected signature {expected_signature}, got {row.get('signature')}")
        if "param_" in row.get("signature", ""):
            failures.append(f"{address}: signature still contains param_N")
        comment = row.get("comment", "")
        for token in COMMENT_TOKENS[address]:
            if not token_present(comment, token):
                failures.append(f"{address}: comment missing token {token!r}")
        for token in OVERCLAIMS:
            if token_present(comment, token):
                failures.append(f"{address}: comment contains overclaim token {token!r}")


def check_tags(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_tags.tsv")
    for address, expected in EXPECTED_TAGS.items():
        row = row_by_address(rows, address)
        if row is None:
            failures.append(f"{address}: missing tag row")
            continue
        tags = {tag for tag in row.get("tags", "").split(";") if tag}
        missing = sorted(expected - tags)
        if missing:
            failures.append(f"{address}: missing tags {missing}")


def check_xrefs(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_xrefs.tsv")
    edges = {
        (
            normalize_address(row.get("target_addr", "")),
            normalize_address(row.get("from_addr", "")),
            row.get("from_function", ""),
        )
        for row in rows
    }
    for edge in EXPECTED_XREFS:
        wanted = (normalize_address(edge[0]), normalize_address(edge[1]), edge[2])
        if wanted not in edges:
            failures.append(f"missing xref edge {wanted}")


def check_disassembly(base: Path, failures: list[str]) -> None:
    disable_rows = read_tsv(base / "post_00412830_range.tsv")
    by_addr = {normalize_address(row.get("address", "")): row for row in disable_rows}
    if by_addr.get("0x0041285a", {}).get("operands") != "EAX, dword ptr [ESP + 0x18]":
        failures.append("0x0041285a: missing entry_name stack load")
    if by_addr.get("0x004128f7", {}).get("operands") != "0x4":
        failures.append("0x004128f7: missing RET 0x4")

    axis_rows = read_tsv(base / "post_004d337b_axis_calls.tsv")
    by_addr = {normalize_address(row.get("address", "")): row for row in axis_rows}
    if by_addr.get("0x004d3374", {}).get("mnemonic") != "PUSH":
        failures.append("0x004d3374: missing yaw axis_input push")
    if by_addr.get("0x004d337b", {}).get("operands") != "0x00413660":
        failures.append("0x004d337b: missing yaw helper call")
    if by_addr.get("0x004d338f", {}).get("mnemonic") != "PUSH":
        failures.append("0x004d338f: missing pitch axis_input push")
    if by_addr.get("0x004d3390", {}).get("operands") != "0x004136e0":
        failures.append("0x004d3390: missing pitch helper call")

    rows = read_tsv(base / "post_instructions.tsv")
    by_addr = {normalize_address(row.get("instruction_addr", "")): row for row in rows}
    if by_addr.get("0x004136d7", {}).get("operands") != "0x4":
        failures.append("0x004136d7: missing yaw RET 0x4")
    if by_addr.get("0x0041374e", {}).get("operands") != "0x4":
        failures.append("0x0041374e: missing pitch RET 0x4")


def check_decompile(base: Path, failures: list[str]) -> None:
    for address, tokens in DECOMPILE_TOKENS.items():
        text = decompile_text_for(base, address)
        if not text:
            failures.append(f"{address}: missing decompile text")
            continue
        for token in tokens:
            if not token_present(text, token):
                failures.append(f"{address}: decompile missing token {token!r}")


def run(base: Path) -> list[str]:
    failures: list[str] = []
    check_summary(base / "dry.log", EXPECTED_DRY, "dry.log", failures)
    check_summary(base / "apply.log", EXPECTED_APPLY, "apply.log", failures)
    check_summary(base / "verify_dry.log", EXPECTED_DRY, "verify_dry.log", failures)
    check_metadata(base, failures)
    check_tags(base, failures)
    check_xrefs(base, failures)
    check_disassembly(base, failures)
    check_decompile(base, failures)
    return failures


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--check", action="store_true", help="Compatibility flag for npm verification scripts.")
    args = parser.parse_args(argv)

    failures = run(args.base)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print(f"PASS: Wave475 GeneralVolume parameter-tail evidence validated at {args.base}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
