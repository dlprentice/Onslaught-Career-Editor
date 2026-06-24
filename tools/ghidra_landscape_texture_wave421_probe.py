#!/usr/bin/env python3
"""Validate the Wave421 CLandscapeTexture saved-Ghidra correction tranche."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave421-landscape-texture" / "current"

COMMON_TAGS = {"static-reaudit", "landscape-texture-wave421", "retail-binary-evidence"}

TARGETS: dict[str, dict[str, object]] = {
    "0x0048e310": {
        "name": "CLandscapeTexture__FreeTexture",
        "signature": "void __thiscall CLandscapeTexture__FreeTexture(void * this)",
        "commentTokens": ["+0x08", "OID__FreeObject", "runtime rendering behavior", "rebuild parity remain unproven"],
        "decompileTokens": ["OID__FreeObject", "this", "+ 8"],
        "tags": {"landscape-texture", "texture-lifetime", "signature-hardened", "comment-hardened"},
    },
    "0x0048e330": {
        "name": "CLandscapeTexture__Constructor",
        "signature": "void * __thiscall CLandscapeTexture__Constructor(void * this)",
        "commentTokens": ["CIBuffer__Constructor", "0x005dc1d8", "+0x2c", "vtable layout still has unconfirmed entries"],
        "decompileTokens": ["CIBuffer__Constructor", "PTR_LAB_005dc1d8", "return this"],
        "tags": {"landscape-texture", "constructor", "vtable-context", "signature-hardened", "comment-hardened"},
    },
    "0x0048e360": {
        "name": "CLandscapeTexture__SetupMipLevel",
        "signature": "void __thiscall CLandscapeTexture__SetupMipLevel(void * this, int mip_level, uint edge_flags)",
        "commentTokens": ["mip_level", "+0x24", "edge_flags", "bits 1/2/4/8", "vtable-slot target identity"],
        "decompileTokens": ["mip_level", "edge_flags", "0x1f", "+ 4"],
        "tags": {"landscape-texture", "mip-level", "vtable-dispatch", "signature-hardened", "comment-hardened"},
    },
    "0x0048e430": {
        "name": "CLandscapeTexture__ConstructorMip",
        "signature": "void * __thiscall CLandscapeTexture__ConstructorMip(void * this)",
        "commentTokens": ["CUMTexture", "0x005dc1f0", "+0x40", "adjacent vtable entries remain provisional"],
        "decompileTokens": ["CUMTexture__ctor_like_004f79d0", "PTR_LAB_005dc1f0", "return this"],
        "tags": {"landscape-texture", "constructor", "mip-texture", "vtable-context", "signature-hardened", "comment-hardened"},
    },
    "0x0048e450": {
        "name": "CLandscapeTexture__Destructor",
        "signature": "void __thiscall CLandscapeTexture__Destructor(void * this)",
        "commentTokens": ["0x005dc1f0", "+0x40", "0x006fabf8", "0x006fabf4", "runtime cleanup behavior"],
        "decompileTokens": ["PTR_LAB_005dc1f0", "DAT_006fabf8", "CUMTexture__ctor_like_004f7a40"],
        "tags": {"landscape-texture", "destructor", "shared-texture-lifetime", "signature-hardened", "comment-hardened"},
    },
    "0x0048e4d0": {
        "name": "CLandscapeTexture__Init",
        "signature": "int __thiscall CLandscapeTexture__Init(void * this, int mip_level, int tile_set_index)",
        "commentTokens": ["mip level", "tile-set index", "+0x48/+0x4a", "+0x40/+0x44", "register-carryover"],
        "decompileTokens": ["mip_level", "tile_set_index", "CUMTexture__ConfigureByMode", "DAT_006fabf8"],
        "tags": {"landscape-texture", "init", "mip-level", "update-buffer", "signature-hardened", "comment-hardened"},
    },
    "0x0048e610": {
        "name": "CLandscapeTexture__Reset",
        "signature": "uint __thiscall CLandscapeTexture__Reset(void * this)",
        "commentTokens": ["CUMTexture", "negative status", "+0x2c", "+0x40", "CLandscapeTexture__UpdateTileRange"],
        "decompileTokens": ["CUMTexture__VFunc_02_004f7b60", "CLandscapeTexture__UpdateTileRange", "0x3f"],
        "tags": {"landscape-texture", "reset", "update-buffer", "signature-hardened", "comment-hardened"},
    },
    "0x0048e7b0": {
        "name": "CLandscapeTexture__ResetUpdateQueue",
        "signature": "void __cdecl CLandscapeTexture__ResetUpdateQueue(void)",
        "commentTokens": ["0x0062d868", "0x006fa7d8", "runtime update ordering"],
        "decompileTokens": ["PTR_DAT_0062d868", "DAT_006fa7d8"],
        "tags": {"landscape-texture", "update-queue", "signature-hardened", "comment-hardened"},
    },
    "0x0048e7c0": {
        "name": "CLandscapeTexture__FlushUpdateQueue",
        "signature": "void __cdecl CLandscapeTexture__FlushUpdateQueue(void)",
        "commentTokens": ["20-byte", "CLandscapeTexture__UpdateTile", "compacts deferred records", "runtime update ordering"],
        "decompileTokens": ["DAT_006fa7d8", "PTR_DAT_0062d868", "CLandscapeTexture__UpdateTile"],
        "tags": {"landscape-texture", "update-queue", "queue-flush", "signature-hardened", "comment-hardened"},
    },
    "0x0048e880": {
        "name": "CLandscapeTexture__QueueTileUpdate",
        "signature": "void __thiscall CLandscapeTexture__QueueTileUpdate(void * this, uint tile_coord, int update_mode)",
        "commentTokens": ["tile_coord", "texture X/Y", "deduplicates", "0x006fabbf", "20-byte update record"],
        "decompileTokens": ["tile_coord", "update_mode", "CLandscapeTexture__FlushUpdateQueue", "PTR_DAT_0062d868"],
        "tags": {"landscape-texture", "update-queue", "tile-coordinate", "signature-hardened", "comment-hardened"},
    },
    "0x0048e950": {
        "name": "CLandscapeTexture__CopyTileToTexture",
        "signature": "void __thiscall CLandscapeTexture__CopyTileToTexture(void * this, int * tile_rect)",
        "commentTokens": ["0x006fabf0", "tile_rect", "0x006fabf4", "0x0067a7d8", "RGB565"],
        "decompileTokens": ["DAT_006fabf0", "tile_rect", "DAT_0067a7d8", "0x4c", "0x50"],
        "tags": {"landscape-texture", "texture-copy", "rgb565", "signature-hardened", "comment-hardened"},
    },
    "0x0048ea80": {
        "name": "CLandscapeTexture__UpdateTile",
        "signature": "void __thiscall CLandscapeTexture__UpdateTile(void * this, uint tile_coord)",
        "commentTokens": ["tile_coord", "CLandscapeTexture__BlitTileRegionWithLightingMask", "CLandscapeTexture__BlendAlpha", "overlay record layout"],
        "decompileTokens": ["tile_coord", "CLandscapeTexture__BlitTileRegionWithLightingMask", "CLandscapeTexture__BlendAlpha", "DAT_008be274"],
        "tags": {"landscape-texture", "tile-update", "rgb565", "alpha-overlay", "signature-hardened", "comment-hardened"},
    },
    "0x0048ee00": {
        "name": "CLandscapeTexture__BlendAlpha",
        "signature": "void __cdecl CLandscapeTexture__BlendAlpha(short * dest, int pitch, byte * alpha, int x, int y, byte level, int size)",
        "commentTokens": ["alpha mask", "RGB565", "0x07e0f81f", "runtime visual parity"],
        "decompileTokens": ["dest", "pitch", "alpha", "level", "0x7e0f81f"],
        "tags": {"landscape-texture", "alpha-blend", "rgb565", "signature-hardened", "comment-hardened"},
    },
    "0x0048ef00": {
        "name": "CLandscapeTexture__UpdateTileRange",
        "signature": "void __thiscall CLandscapeTexture__UpdateTileRange(void * this, int min_x, int min_y, int max_x, int max_y)",
        "commentTokens": ["inclusive tile range", "min_y*64+min_x", "CLandscapeTexture__CopyTileToTexture", "exact tile flag semantics"],
        "decompileTokens": ["min_x", "min_y", "max_x", "max_y", "CLandscapeTexture__CopyTileToTexture"],
        "tags": {"landscape-texture", "tile-range", "tile-update", "alpha-overlay", "signature-hardened", "comment-hardened"},
    },
}

EXPECTED_DRY = {
    "updated": 0,
    "skipped": 14,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}

EXPECTED_APPLY = {
    "updated": 14,
    "skipped": 0,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}

STALE_SIGNATURE_RE = re.compile(r"^(undefined|undefined4)\s+CLandscapeTexture__")

OVERCLAIM_TOKENS = (
    "runtime proof",
    "runtime rendering behavior proven",
    "runtime cleanup behavior proven",
    "runtime update ordering proven",
    "runtime visual parity proven",
    "rebuild parity proven",
    "fully re'ed",
    "100% re",
    "complete vtable",
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
        for key in ("address", "target_addr", "function_entry"):
            if key in row and row[key]:
                row[key] = normalize_address(row[key])
        if "comment" in row:
            row["comment"] = unescape(row["comment"])
    return rows


def row_by_address(rows: list[dict[str, str]], address: str, key: str = "address") -> dict[str, str] | None:
    wanted = normalize_address(address)
    for row in rows:
        if row.get(key) == wanted:
            return row
    return None


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


def check_summary(base: Path, failures: list[str]) -> None:
    for filename, expected in (("apply_dry.log", EXPECTED_DRY), ("apply_apply.log", EXPECTED_APPLY)):
        actual = parse_summary(base / filename)
        if actual is None:
            failures.append(f"{filename}: missing SUMMARY")
        elif actual != expected:
            failures.append(f"{filename}: summary mismatch {actual} != {expected}")


def decompile_file_for(base: Path, address: str, name: str) -> Path:
    clean = address.lower().replace("0x", "")
    return base / "decompile_after" / f"{clean}_{name}.c"


def check_targets(base: Path = BASE) -> list[str]:
    failures: list[str] = []
    check_summary(base, failures)

    metadata = read_tsv(base / "metadata_after.tsv")
    tags = read_tsv(base / "tags_after.tsv")
    xrefs = read_tsv(base / "xrefs_after.tsv")
    vtables = read_tsv(base / "vtables_before.tsv")

    if not metadata:
        failures.append("metadata_after.tsv missing or empty")
    if not tags:
        failures.append("tags_after.tsv missing or empty")
    if not xrefs:
        failures.append("xrefs_after.tsv missing or empty")
    if not vtables:
        failures.append("vtables_before.tsv missing or empty")

    for row in metadata:
        signature = row.get("signature", "")
        if STALE_SIGNATURE_RE.search(signature):
            failures.append(f"{row.get('address', '<unknown>')}: stale undefined CLandscapeTexture signature present")

    no_function_vtable_rows = [row for row in vtables if row.get("status") == "NO_FUNCTION_AT_POINTER"]
    if not no_function_vtable_rows:
        failures.append("vtables_before.tsv should preserve provisional NO_FUNCTION_AT_POINTER evidence")

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
        for token in expected["commentTokens"]:  # type: ignore[union-attr]
            if not token_present(comment, str(token)):
                failures.append(f"{address}: missing comment token {token!r}")
        for token in OVERCLAIM_TOKENS:
            if token_present(comment, token):
                failures.append(f"{address}: overclaim token present {token!r}")

        tag_row = row_by_address(tags, address)
        if tag_row is None:
            failures.append(f"{address}: missing tag row")
        else:
            actual_tags = {tag for tag in tag_row.get("tags", "").split(";") if tag}
            expected_tags = COMMON_TAGS | set(expected["tags"])  # type: ignore[arg-type]
            missing_tags = sorted(expected_tags - actual_tags)
            if missing_tags:
                failures.append(f"{address}: missing tags {', '.join(missing_tags)}")

        decompile_text = read_text(decompile_file_for(base, address, str(expected["name"])))
        if not decompile_text:
            failures.append(f"{address}: missing decompile after file")
        else:
            for token in expected["decompileTokens"]:  # type: ignore[union-attr]
                if not token_present(decompile_text, str(token)):
                    failures.append(f"{address}: missing decompile token {token!r}")

        xref_row = row_by_address(xrefs, address, key="target_addr")
        if xref_row is None:
            failures.append(f"{address}: missing xref row")

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
    print("PASS: Wave421 CLandscapeTexture saved-Ghidra corrections validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
