#!/usr/bin/env python3
"""Validate the Wave420 Particle/Token/Landscape saved-Ghidra correction tranche."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave420-particle-token-landscape-head" / "current"

COMMON_TAGS = {"static-reaudit", "particle-token-landscape-wave420", "retail-binary-evidence"}

TARGETS: dict[str, dict[str, object]] = {
    "0x0048ddd0": {
        "name": "CDXMemBuffer__OpenReadMode11",
        "signature": "int __thiscall CDXMemBuffer__OpenReadMode11(void * this, char * filename)",
        "commentTokens": [
            "ECX is the CDXMemBuffer receiver",
            "single stack argument is the filename",
            "0x11, 1, 0",
            "only observed caller",
            "runtime particle archive loading remains unproven",
        ],
        "decompileTokens": ["CDXMemBuffer__InitFromFile", "filename", "0x11"],
        "tags": {"dx-mem-buffer", "particle-file-context", "owner-corrected", "signature-corrected", "comment-hardened"},
    },
    "0x0048de00": {
        "name": "CTokenArchive__ReadLine",
        "signature": "void __stdcall CTokenArchive__ReadLine(char * line_buffer, int max_len)",
        "commentTokens": [
            "DXMemBuffer__ReadLine",
            "trailing LF",
            "0x0083e288",
            "max length 999",
            "archive parser runtime coverage remains unproven",
        ],
        "decompileTokens": ["DXMemBuffer__ReadLine", "line_buffer", "max_len", "'\\n'"],
        "tags": {"token-archive", "line-reader", "signature-corrected", "comment-hardened"},
    },
    "0x0048de30": {
        "name": "CDXEngine__FormatCubeTextureFilename",
        "signature": "void __cdecl CDXEngine__FormatCubeTextureFilename(char * out_path, int cube_index, int suffix_index)",
        "commentTokens": [
            "cube_%02d_%s.tga",
            "cube_index",
            "suffix_index",
            "five-iteration loop",
            "texture load/runtime render behavior remains unproven",
        ],
        "decompileTokens": ["sprintf", "out_path", "cube_index", "suffix_index", "s_cubes_cube__2d__s_tga_0062d7d0"],
        "tags": {"dx-engine", "kempy-cube", "signature-corrected", "comment-hardened"},
    },
    "0x0048de90": {
        "name": "CDXLandscape__ClearPendingHudMarkerHandle",
        "signature": "void * __thiscall CDXLandscape__ClearPendingHudMarkerHandle(void * this)",
        "commentTokens": [
            "CDXLandscape +0x8",
            "0x0067a7d0",
            "returns the same subobject pointer",
            "HUD marker lifetime behavior remains unproven",
        ],
        "decompileTokens": ["DAT_0067a7d0", "this"],
        "tags": {"dx-landscape", "hud-marker", "signature-corrected", "comment-hardened"},
    },
    "0x0048df20": {
        "name": "CLandscapeIB__CreateIndexBuffer",
        "signature": "void __thiscall CLandscapeIB__CreateIndexBuffer(void * this)",
        "commentTokens": [
            "DAT_009c64e4/e8/ec",
            "+0x24/+0x28",
            "+0x2c",
            "CDXMeshVB__BuildStripBatchesAndEmitIndexBuffer",
            "landscape render behavior remains unproven",
        ],
        "decompileTokens": [
            "DAT_009c64e0",
            "CDXMeshVB__BuildStripBatchesAndEmitIndexBuffer",
            "+ 0x2c",
            "+ 0x30",
        ],
        "tags": {"landscape-ib", "index-buffer", "signature-corrected", "comment-hardened"},
    },
}

EXPECTED_DRY = {
    "updated": 0,
    "skipped": 5,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}

EXPECTED_APPLY = {
    "updated": 5,
    "skipped": 0,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}

STALE_SIGNATURE_TOKENS = {
    "void __stdcall CParticleSet__OpenRead(int param_1)",
    "void __cdecl CDXEngine__FormatCubeTextureFilename(void * param_1)",
    "undefined CLandscapeIB__CreateIndexBuffer(void)",
}

STALE_NAMES = {"CParticleSet__OpenRead"}

OVERCLAIM_TOKENS = (
    "runtime proof",
    "runtime particle archive loading proven",
    "archive parser runtime coverage proven",
    "texture load/runtime render behavior proven",
    "HUD marker lifetime behavior proven",
    "landscape render behavior proven",
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

    if not metadata:
        failures.append("metadata_after.tsv missing or empty")
    if not tags:
        failures.append("tags_after.tsv missing or empty")
    if not xrefs:
        failures.append("xrefs_after.tsv missing or empty")

    all_names = {row.get("name", "") for row in metadata}
    stale_present = sorted(name for name in STALE_NAMES if name in all_names)
    if stale_present:
        failures.append("stale names still present: " + ", ".join(stale_present))

    for row in metadata:
        signature = row.get("signature", "")
        for token in STALE_SIGNATURE_TOKENS:
            if token_present(signature, token):
                failures.append(f"{row.get('address', '<unknown>')}: stale signature present {token!r}")

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
    print("PASS: Wave420 Particle/Token/Landscape saved-Ghidra corrections validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
