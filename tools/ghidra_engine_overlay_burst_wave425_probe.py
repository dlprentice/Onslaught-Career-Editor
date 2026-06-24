#!/usr/bin/env python3
"""Validate the Wave425 engine burst/overlay saved-Ghidra correction."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave425-engine-overlay-burst" / "current"

COMMON_TAGS = {"static-reaudit", "engine-overlay-burst-wave425", "retail-binary-evidence"}

TARGETS: dict[str, dict[str, object]] = {
    "0x00490220": {
        "name": "CEngine__ClearBurstOverlaySlotPayloads",
        "signature": "void __fastcall CEngine__ClearBurstOverlaySlotPayloads(void * burst_overlay_state)",
        "commentTokens": [
            "engine +0x18 burst-overlay state helper",
            "six active overlay slot payload blocks",
            "0x74-byte stride",
            "runtime render behavior and rebuild parity remain unproven",
        ],
        "decompileTokens": ["0x1f8", "0x74", "iVar"],
        "tags": ["engine", "burst-overlay", "overlay", "owner-corrected", "signature-hardened", "comment-hardened"],
        "xref": ("0x004499d0", "CEngine__Init"),
    },
    "0x00490280": {
        "name": "CEngine__ResetBurstOverlayState",
        "signature": "int __fastcall CEngine__ResetBurstOverlayState(void * burst_overlay_state)",
        "commentTokens": [
            "resets the burst-overlay candidate count at +0x1c0",
            "clears 0xae dwords from +0x1c4",
            "returns 1",
            "runtime render behavior and rebuild parity remain unproven",
        ],
        "decompileTokens": ["0x1c0", "0xae", "return 1"],
        "tags": ["engine", "burst-overlay", "overlay", "owner-corrected", "signature-hardened", "comment-hardened"],
        "xref": ("0x004499d0", "CEngine__Init"),
    },
    "0x004902b0": {
        "name": "CEngine__TrackBurstEventIfNearby",
        "signature": (
            "void __thiscall CEngine__TrackBurstEventIfNearby"
            "(void * this, void * position, void * gamut, int burst_type, float intensity_scale)"
        ),
        "commentTokens": [
            "engine +0x18 burst-overlay state",
            "candidate count at +0x1c0",
            "appends one 0x1c-byte candidate record",
            "exact argument semantics",
            "runtime projectile/burst behavior",
        ],
        "decompileTokens": ["DAT_0089c9ac", "0x1c0", "0x1c", "intensity_scale"],
        "tags": ["engine", "burst-overlay", "projectile-burst", "signature-hardened", "comment-hardened"],
        "xref": ("0x0044a610", "CEngine__TrackBurstEventFromPreset"),
    },
    "0x004903a0": {
        "name": "CDXEngine__BuildOverlaySlotFromSortedEntry",
        "signature": "void __thiscall CDXEngine__BuildOverlaySlotFromSortedEntry(void * this, int slot_index, int candidate_index)",
        "commentTokens": [
            "RET 0x8",
            "0x74-byte active overlay slot",
            "0x1c-byte sorted candidate",
            "DAT_009c65c0",
            "runtime render behavior and rebuild parity remain unproven",
        ],
        "decompileTokens": ["CStaticShadows__SampleShadowHeightBilinear", "slot_index", "candidate_index", "DAT_009c65c0"],
        "tags": ["dx-engine", "burst-overlay", "overlay", "signature-hardened", "comment-hardened"],
        "xref": ("0x004905f0", "CDXEngine__UpdateOverlaySlotsFromCandidateList"),
    },
    "0x004905f0": {
        "name": "CDXEngine__UpdateOverlaySlotsFromCandidateList",
        "signature": "void __fastcall CDXEngine__UpdateOverlaySlotsFromCandidateList(void * burst_overlay_state)",
        "commentTokens": [
            "decays six active overlay slots",
            "Sort__QuickSortGeneric",
            "CDXEngine__BuildOverlaySlotFromSortedEntry",
            "clears the candidate count at +0x1c0",
            "runtime render behavior and rebuild parity remain unproven",
        ],
        "decompileTokens": ["Sort__QuickSortGeneric", "CDXEngine__BuildOverlaySlotFromSortedEntry", "burst_overlay_state", "0x1c0"],
        "tags": ["dx-engine", "burst-overlay", "overlay", "signature-hardened", "comment-hardened"],
        "xref": ("0x0053e2e0", "CDXEngine__Render"),
    },
    "0x00490780": {
        "name": "CDXEngine__SetOverlaySlotsEnabledForActiveViews",
        "signature": "void __thiscall CDXEngine__SetOverlaySlotsEnabledForActiveViews(void * this, int enabled)",
        "commentTokens": [
            "RET 0x4",
            "toggles global overlay enable flags",
            "+0x1cc",
            "0x74-byte stride",
            "runtime render behavior and rebuild parity remain unproven",
        ],
        "decompileTokens": ["enabled", "DAT_009c68a0", "DAT_009c6904", "0x1cc"],
        "tags": ["dx-engine", "burst-overlay", "overlay", "signature-hardened", "comment-hardened"],
        "xref": ("0x0044a640", "CDXEngine__SetOverlaySlotVisibilityByPlayerView"),
    },
}

EXPECTED_DRY = {
    "updated": 0,
    "skipped": 6,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 2,
    "missing": 0,
    "bad": 0,
}

EXPECTED_APPLY = {
    "updated": 6,
    "skipped": 0,
    "created": 0,
    "would_create": 0,
    "renamed": 2,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}

INSTRUCTION_RETURNS = {
    "0x00490220": ("RET", ""),
    "0x00490280": ("RET", ""),
    "0x004902b0": ("RET", "0x10"),
    "0x004903a0": ("RET", "0x8"),
    "0x004905f0": ("RET", ""),
    "0x00490780": ("RET", "0x4"),
}

STALE_DECOMPILE_TOKENS = {
    "0x004903a0": ["param_3"],
    "0x004905f0": ["unaff_EDI"],
    "0x00490780": ["param_2"],
}

CALLER_EXPECTATIONS = {
    "0044a610_CEngine__TrackBurstEventFromPreset.c": {
        "required": ["CEngine__TrackBurstEventIfNearby", "+ 0x18", "+ 0x470"],
        "forbidden": ["CEngine__TrackBurstEventIfNearby();"],
    },
    "0044a640_CDXEngine__SetOverlaySlotVisibilityByPlayerView.c": {
        "required": ["CDXEngine__SetOverlaySlotsEnabledForActiveViews", "playerView", "+ 0x18"],
        "forbidden": ["unaff_retaddr"],
    },
}

OVERCLAIM_TOKENS = (
    "runtime proof",
    "runtime render behavior proven",
    "runtime projectile/burst behavior proven",
    "source identity proven",
    "concrete layout proven",
    "rebuild parity proven",
    "fully re'ed",
    "100% re",
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


def unescape(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        for key in ("address", "target_addr", "from_function_addr", "function_entry"):
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


def rows_by_address(rows: list[dict[str, str]], address: str, key: str = "address") -> list[dict[str, str]]:
    wanted = normalize_address(address)
    return [row for row in rows if normalize_address(row.get(key, "")) == wanted]


def parse_summary(path: Path) -> dict[str, int] | None:
    text = read_text(path)
    match = re.search(
        r"SUMMARY\s+updated=(\d+)\s+skipped=(\d+)\s+created=(\d+)\s+would_create=(\d+)\s+"
        r"renamed=(\d+)\s+would_rename=(\d+)\s+missing=(\d+)\s+bad=(\d+)",
        text,
    )
    if not match:
        return None
    keys = ("updated", "skipped", "created", "would_create", "renamed", "would_rename", "missing", "bad")
    return {key: int(value) for key, value in zip(keys, match.groups())}


def compare_summary(failures: list[str], label: str, path: Path, expected: dict[str, int]) -> None:
    actual = parse_summary(path)
    if actual is None:
        failures.append(f"{label}: missing SUMMARY")
    elif actual != expected:
        failures.append(f"{label}: summary mismatch {actual} != {expected}")


def decompile_text_for(base: Path, address: str) -> str:
    directory = base / "decompile_after"
    if not directory.is_dir():
        return ""
    matches = sorted(directory.glob(f"{normalize_address(address)[2:]}_*.c"))
    if not matches:
        return ""
    return "\n".join(read_text(path) for path in matches)


def parse_tags(value: str) -> set[str]:
    return {part.strip() for part in value.split(";") if part.strip()}


def instruction_matches(row: dict[str, str], expected: tuple[str, str]) -> bool:
    mnemonic, operand = expected
    if row.get("mnemonic") != mnemonic:
        return False
    if operand:
        return operand in row.get("operands", "")
    return row.get("mnemonic") == mnemonic


def check_targets(base: Path = BASE) -> list[str]:
    failures: list[str] = []
    compare_summary(failures, "dry", base / "apply_dry.log", EXPECTED_DRY)
    compare_summary(failures, "apply", base / "apply_apply.log", EXPECTED_APPLY)

    metadata = read_tsv(base / "metadata_after.tsv")
    tags_rows = read_tsv(base / "tags_after.tsv")
    xrefs = read_tsv(base / "xrefs_after.tsv")
    instructions = read_tsv(base / "instructions_after.tsv")

    if not metadata:
        failures.append("metadata_after.tsv missing or empty")
    if not tags_rows:
        failures.append("tags_after.tsv missing or empty")
    if not xrefs:
        failures.append("xrefs_after.tsv missing or empty")
    if not instructions:
        failures.append("instructions_after.tsv missing or empty")

    for address, expected in TARGETS.items():
        row = row_by_address(metadata, address)
        if row is None:
            failures.append(f"{address}: missing metadata row")
            continue
        if row.get("name") != expected["name"]:
            failures.append(f"{address}: name mismatch {row.get('name')} != {expected['name']}")
        if row.get("signature") != expected["signature"]:
            failures.append(f"{address}: signature mismatch {row.get('signature')} != {expected['signature']}")

        comment = row.get("comment", "")
        for token in expected["commentTokens"]:  # type: ignore[index]
            if not token_present(comment, str(token)):
                failures.append(f"{address}: missing comment token {token!r}")
        for token in OVERCLAIM_TOKENS:
            if token_present(comment, token):
                failures.append(f"{address}: overclaim token present {token!r}")

        tag_row = row_by_address(tags_rows, address)
        if tag_row is None:
            failures.append(f"{address}: missing tag row")
        else:
            actual_tags = parse_tags(tag_row.get("tags", ""))
            missing_tags = sorted((COMMON_TAGS | set(expected["tags"])) - actual_tags)  # type: ignore[arg-type]
            if missing_tags:
                failures.append(f"{address}: missing tags {', '.join(missing_tags)}")

        decompile = decompile_text_for(base, address)
        if not decompile:
            failures.append(f"{address}: missing decompile after text")
        else:
            for token in expected["decompileTokens"]:  # type: ignore[index]
                if not token_present(decompile, str(token)):
                    failures.append(f"{address}: missing decompile token {token!r}")
            for token in STALE_DECOMPILE_TOKENS.get(address, []):
                if token_present(decompile, token):
                    failures.append(f"{address}: stale decompile token present {token!r}")

        from_addr, from_function = expected["xref"]  # type: ignore[misc]
        matching_xrefs = [
            xref
            for xref in xrefs
            if xref.get("target_addr") == normalize_address(address)
            and xref.get("from_function_addr") == normalize_address(str(from_addr))
            and xref.get("from_function") == from_function
        ]
        if not matching_xrefs:
            failures.append(f"{address}: missing expected xref from {from_function}")

        expected_return = INSTRUCTION_RETURNS[address]
        if not any(instruction_matches(row, expected_return) for row in rows_by_address(instructions, address, key="target_addr")):
            failures.append(f"{address}: missing instruction return evidence {expected_return}")

    caller_dir = base / "decompile_callers_after"
    for filename, expectation in CALLER_EXPECTATIONS.items():
        text = read_text(caller_dir / filename)
        if not text:
            failures.append(f"{filename}: missing caller decompile after text")
            continue
        for token in expectation["required"]:
            if not token_present(text, token):
                failures.append(f"{filename}: missing caller token {token!r}")
        for token in expectation["forbidden"]:
            if token_present(text, token):
                failures.append(f"{filename}: stale caller token present {token!r}")

    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=BASE, help="Wave artifact directory to validate")
    parser.add_argument("--check", action="store_true", help="Return non-zero on validation failure")
    args = parser.parse_args(argv)

    failures = check_targets(args.base)
    if failures:
        print("FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1 if args.check else 0
    print("PASS: Wave425 engine burst/overlay saved-Ghidra correction validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
