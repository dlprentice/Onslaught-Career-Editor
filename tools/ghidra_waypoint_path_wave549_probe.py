#!/usr/bin/env python3
"""Validate Wave549 Waypoint / WaypointPath Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave549-waypoint-random-path-004ffe00"
SPECS = {
    "0x004ffe00": {
        "raw": "004ffe00",
        "name": "CWaypoint__RandomizeOffsetVectors",
        "signature": "void __fastcall CWaypoint__RandomizeOffsetVectors(void * this)",
        "comment_tokens": (
            "global random context 0x008a9d9c",
            "offsets +0x48 and +0x54",
            "mirrored pairs at +0x50/+0x5c",
            "Static retail evidence only",
        ),
        "tags": {"cwaypoint", "random-offsets", "waypoint-path-wave549"},
        "xref_count": 4,
        "decompile_tokens": (
            "void __fastcall CWaypoint__RandomizeOffsetVectors(void *this)",
            "Random__NextLCGAbs",
            "0x48",
            "0x54",
            "0x50",
            "0x5c",
        ),
        "instruction_tokens": (
            ("004ffe00", "PUSH", "ECX"),
            ("004ffe02", "MOV", "ESI, ECX"),
            ("004ffe0a", "CALL", "0x004de8d0"),
            ("004ffe25", "FMUL", "float ptr [0x005dfb7c]"),
            ("004ffe31", "FSTP", "float ptr [ESI + 0x48]"),
            ("004ffefa", "RET", ""),
        ),
    },
    "0x00505bb0": {
        "raw": "00505bb0",
        "name": "CWaypointPath__scalar_deleting_dtor",
        "signature": "void * __thiscall CWaypointPath__scalar_deleting_dtor(void * this, byte flags)",
        "comment_tokens": (
            "scalar-deleting destructor wrapper",
            "CWaypointPath__dtor_base",
            "flags bit 0",
            "RET 0x4",
            "Static retail evidence only",
        ),
        "tags": {"cwaypointpath", "scalar-deleting-dtor", "name-corrected"},
        "xref_count": 1,
        "decompile_tokens": (
            "void * __thiscall CWaypointPath__scalar_deleting_dtor(void *this,byte flags)",
            "CWaypointPath__dtor_base(this)",
            "CDXMemoryManager__Free",
            "return this",
        ),
        "instruction_tokens": (
            ("00505bb0", "PUSH", "ESI"),
            ("00505bb1", "MOV", "ESI, ECX"),
            ("00505bb3", "CALL", "0x00505bd0"),
            ("00505bb8", "TEST", "byte ptr [ESP + 0x8], 0x1"),
            ("00505bcd", "RET", "0x4"),
        ),
    },
    "0x00505bd0": {
        "raw": "00505bd0",
        "name": "CWaypointPath__dtor_base",
        "signature": "void __fastcall CWaypointPath__dtor_base(void * this)",
        "comment_tokens": (
            "register-only CWaypointPath destructor body",
            "table pointer 0x005dfc8c",
            "pointer at +0x04",
            "CSPtrSet at +0x08",
            "Static retail evidence only",
        ),
        "tags": {"cwaypointpath", "dtor-base", "name-corrected"},
        "xref_count": 1,
        "decompile_tokens": (
            "void __fastcall CWaypointPath__dtor_base(void *this)",
            "PTR_CWaypointPath__scalar_deleting_dtor_005dfc8c",
            "CDXMemoryManager__Free",
            "CSPtrSet__Clear",
        ),
        "instruction_tokens": (
            ("00505bd0", "PUSH", "-0x1"),
            ("00505bd7", "MOV", "EAX, FS:[0x0]"),
            ("00505bed", "MOV", "dword ptr [ESI], 0x5dfc8c"),
            ("00505c08", "CALL", "0x00549220"),
            ("00505c18", "CALL", "0x004e5c60"),
            ("00505c2c", "RET", ""),
        ),
    },
}
COMMON_TAGS = {
    "static-reaudit",
    "waypoint-path-wave549",
    "retail-binary-evidence",
    "signature-corrected",
    "comment-hardened",
}
FORBIDDEN_TOKENS = (
    "CWaypointPath__VFunc_00_00505bb0",
    "CWaypointPath__scalar_deleting_dtor_00505bd0",
    "param_1",
    "param_2",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def raw_address(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return value.zfill(8)


def normalize_address(value: str) -> str:
    return "0x" + raw_address(value)


def token_present(text: str, token: str) -> bool:
    return token.lower() in text.lower()


def parse_summary(path: Path) -> dict[str, int]:
    text = read_text(path)
    match = re.search(
        r"SUMMARY: mode=(?P<mode>\w+) updated=(?P<updated>\d+) skipped=(?P<skipped>\d+) "
        r"renamed=(?P<renamed>\d+) would_rename=(?P<would_rename>\d+) "
        r"missing=(?P<missing>\d+) bad=(?P<bad>\d+)",
        text,
    )
    require(match is not None, f"Missing summary in {path}")
    return {
        "updated": int(match.group("updated")),
        "skipped": int(match.group("skipped")),
        "renamed": int(match.group("renamed")),
        "would_rename": int(match.group("would_rename")),
        "missing": int(match.group("missing")),
        "bad": int(match.group("bad")),
    }


def check() -> None:
    metadata_rows = read_tsv(BASE / "post_metadata.tsv")
    tags_rows = read_tsv(BASE / "post_tags.tsv")
    xref_rows = read_tsv(BASE / "post_xrefs.tsv")
    instruction_rows = read_tsv(BASE / "post_instructions.tsv")

    require(len(metadata_rows) == 3, f"Expected 3 metadata rows, got {len(metadata_rows)}")
    require(len(tags_rows) == 3, f"Expected 3 tag rows, got {len(tags_rows)}")
    require(len(xref_rows) == 6, f"Expected 6 xref rows, got {len(xref_rows)}")
    require(len(instruction_rows) == 1287, f"Expected 1287 instruction rows, got {len(instruction_rows)}")

    metadata = {normalize_address(row["address"]): row for row in metadata_rows}
    tags = {normalize_address(row["address"]): set(filter(None, row["tags"].split(";"))) for row in tags_rows}
    xrefs_by_target: dict[str, list[dict[str, str]]] = {}
    for row in xref_rows:
        xrefs_by_target.setdefault(normalize_address(row["target_addr"]), []).append(row)
    instructions = {
        (raw_address(row["instruction_addr"]), row["mnemonic"], row["operands"]): row
        for row in instruction_rows
    }

    dry = parse_summary(BASE / "apply_waypoint_path_wave549_dry.log")
    apply = parse_summary(BASE / "apply_waypoint_path_wave549_apply.log")
    verify = parse_summary(BASE / "apply_waypoint_path_wave549_verify_dry.log")
    require(dry == {"updated": 0, "skipped": 3, "renamed": 0, "would_rename": 2, "missing": 0, "bad": 0}, f"Unexpected dry summary: {dry}")
    require(apply == {"updated": 3, "skipped": 0, "renamed": 2, "would_rename": 0, "missing": 0, "bad": 0}, f"Unexpected apply summary: {apply}")
    require(verify == {"updated": 0, "skipped": 3, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}, f"Unexpected verify summary: {verify}")

    for address, spec in SPECS.items():
        require(address in metadata, f"Missing metadata row for {address}")
        row = metadata[address]
        require(row["name"] == spec["name"], f"{address} name mismatch: {row['name']}")
        require(row["signature"] == spec["signature"], f"{address} signature mismatch: {row['signature']}")
        for token in spec["comment_tokens"]:
            require(token_present(row["comment"], token), f"{address} comment missing token: {token}")
        tag_set = tags.get(address, set())
        require(COMMON_TAGS <= tag_set, f"{address} missing common tags: {COMMON_TAGS - tag_set}")
        require(set(spec["tags"]) <= tag_set, f"{address} missing specific tags: {set(spec['tags']) - tag_set}")
        target_xrefs = xrefs_by_target.get(address, [])
        require(len(target_xrefs) == spec["xref_count"], f"{address} xref count mismatch: {len(target_xrefs)}")

        decompile_text = read_text(BASE / "post_decomp" / f"{spec['raw']}_{spec['name']}.c")
        for token in spec["decompile_tokens"]:
            require(token_present(decompile_text, token), f"{address} decompile missing token: {token}")
        for token in FORBIDDEN_TOKENS:
            if address != "0x00505bd0" or token != "CWaypointPath__scalar_deleting_dtor_00505bd0":
                require(not token_present(decompile_text, token), f"{address} decompile still contains stale token: {token}")

        for token in spec["instruction_tokens"]:
            require(token in instructions, f"{address} missing instruction tuple: {token}")

    print("Wave549 Waypoint / WaypointPath probe PASS: name/signature/comment/read-back evidence verified.")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="validate Wave549 artifacts")
    args = parser.parse_args()
    if not args.check:
        parser.error("Use --check")
    check()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
