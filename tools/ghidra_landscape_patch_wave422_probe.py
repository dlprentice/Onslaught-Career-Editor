#!/usr/bin/env python3
"""Validate the Wave422 landscape patch/VB saved-Ghidra correction tranche."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave422-landscape-vb-patch" / "current"

COMMON_TAGS = {"static-reaudit", "landscape-patch-wave422", "retail-binary-evidence"}

TARGETS: dict[str, dict[str, object]] = {
    "0x0048f180": {
        "name": "CLandscapeTexture__InvalidateTileMaskOrRefreshAll",
        "signature": "void __thiscall CLandscapeTexture__InvalidateTileMaskOrRefreshAll(void * this)",
        "commentTokens": ["+0x2c", "+0x40", "0xff", "CLandscapeTexture__UpdateTileRange", "runtime rendering behavior"],
        "decompileTokens": ["this", "+ 0x2c", "+ 0x40", "CLandscapeTexture__UpdateTileRange"],
        "tags": {"landscape-texture", "tile-invalidation", "owner-corrected", "signature-hardened", "comment-hardened"},
    },
    "0x0048f1e0": {
        "name": "CDXPatch__CreateGridVertexBuffer",
        "signature": "void __thiscall CDXPatch__CreateGridVertexBuffer(void * this, int grid_step)",
        "commentTokens": ["RET 0x4", "grid_step", "(grid_step+1)^2", "CVBuffer__Create", "0x14", "0x102"],
        "decompileTokens": ["grid_step", "CVBuffer__Create", "0x14", "0x102"],
        "tags": {"dx-patch", "vertex-buffer", "owner-corrected", "signature-hardened", "comment-hardened"},
    },
    "0x0048f210": {
        "name": "CDXPatch__RebuildHeightGridVertexBuffer",
        "signature": "void __thiscall CDXPatch__RebuildHeightGridVertexBuffer(void * this)",
        "commentTokens": ["CVBuffer__Lock", "CWorld__GetHeightSamplePacked16", "+0x2c/+0x30", "+0x34", "0x14-byte"],
        "decompileTokens": ["CVBuffer__Lock", "CWorld__GetHeightSamplePacked16", "DAT_006fbdf4", "CVBuffer__Unlock"],
        "tags": {"dx-patch", "heightfield", "vertex-buffer", "owner-corrected", "signature-hardened", "comment-hardened"},
    },
    "0x0048f320": {
        "name": "CDXPatch__RestoreAndRebuildIfDirty",
        "signature": "int __thiscall CDXPatch__RestoreAndRebuildIfDirty(void * this)",
        "commentTokens": ["0x005e5114", "CVBuffer__Restore", "+0x40", "CDXPatch__RebuildHeightGridVertexBuffer"],
        "decompileTokens": ["CVBuffer__Restore", "CDXPatch__RebuildHeightGridVertexBuffer", "+ 0x40"],
        "tags": {"dx-patch", "vtable-context", "vertex-buffer", "owner-corrected", "signature-hardened", "comment-hardened"},
    },
}

EXPECTED_DRY = {
    "updated": 0,
    "skipped": 4,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 4,
    "missing": 0,
    "bad": 0,
}

EXPECTED_APPLY = {
    "updated": 4,
    "skipped": 0,
    "created": 0,
    "would_create": 0,
    "renamed": 4,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}

STALE_SIGNATURE_RE = re.compile(r"^(undefined|undefined4)\s+(CLandscapeTexture|CDXPatch)__")

OVERCLAIM_TOKENS = (
    "runtime proof",
    "runtime rendering behavior proven",
    "runtime gpu behavior proven",
    "runtime vertex-buffer behavior proven",
    "complete class layout",
    "complete vtable",
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
    vtables = read_tsv(base / "vtables_after.tsv")
    if not vtables:
        vtables = read_tsv(base / "vtables_before.tsv")

    if not metadata:
        failures.append("metadata_after.tsv missing or empty")
    if not tags:
        failures.append("tags_after.tsv missing or empty")
    if not xrefs:
        failures.append("xrefs_after.tsv missing or empty")
    if not vtables:
        failures.append("vtables_after.tsv/vtables_before.tsv missing or empty")

    for row in metadata:
        signature = row.get("signature", "")
        if STALE_SIGNATURE_RE.search(signature):
            failures.append(f"{row.get('address', '<unknown>')}: stale undefined landscape patch signature present")

    vfunc_row = row_by_address(vtables, "0x0048f320", key="function_entry")
    if vfunc_row is None or vfunc_row.get("vtable") != "005e5114":
        failures.append("0x0048f320: missing 0x005e5114 vtable evidence")
    if not any(row.get("status") == "NO_FUNCTION_AT_POINTER" for row in vtables):
        failures.append("vtables evidence should preserve provisional NO_FUNCTION_AT_POINTER rows")

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
    print("PASS: Wave422 landscape patch/VB saved-Ghidra corrections validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
