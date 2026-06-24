#!/usr/bin/env python3
"""Validate Wave469 vector helper static metadata corrections."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave469-vector-tail-current"
COMMON_TAGS = {"static-reaudit", "vector-tail-wave469", "retail-binary-evidence"}

EXPECTED_DRY = {
    "updated": 0,
    "skipped": 2,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 1,
    "missing": 0,
    "bad": 0,
}
EXPECTED_APPLY = {
    "updated": 2,
    "skipped": 0,
    "created": 0,
    "would_create": 0,
    "renamed": 1,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}
EXPECTED_VERIFY_DRY = {
    "updated": 0,
    "skipped": 2,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}


def target(
    name: str,
    signature: str,
    comment_tokens: list[str],
    tags: list[str],
    decompile_tokens: list[str],
) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "commentTokens": comment_tokens,
        "tags": sorted(COMMON_TAGS | set(tags)),
        "decompileTokens": decompile_tokens,
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x004c7900": target(
        "Vec3__NormalizeInPlace",
        "void __thiscall Vec3__NormalizeInPlace(void * this)",
        ["Wave469 correction", "owner-neutral Vec3 normalize-in-place", "DAT_005d856c", "old CRocket owner label was too narrow"],
        ["vec3", "owner-corrected", "signature-corrected", "comment-hardened"],
        ["DAT_005d856c", "SQRT", "DAT_005d8568"],
    ),
    "0x004c7d90": target(
        "Vec3__CopyXYZ",
        "void * __thiscall Vec3__CopyXYZ(void * this, void * src_vec3)",
        ["Wave469 correction", "owner-neutral Vec3 three-dword copy helper", "RET 0x4", "EAX returns the destination pointer"],
        ["vec3", "signature-corrected", "comment-hardened"],
        ["return this", "src_vec3", "+ 8"],
    ),
}

EXPECTED_XREF_EDGES = {
    ("0x004c7900", "0x004c749e", "CPDSimpleSprite__ProcessAndRenderSpriteList"),
    ("0x004c7d90", "0x004c76d8", "CPDSimpleSprite__ProcessAndRenderSpriteList"),
    ("0x004c7d90", "0x0053ddb4", "CThing__RenderDebugVolumeOverlay"),
    ("0x004c7d90", "0x00543275", "CDXImposter__BuildQuadGeometry"),
}

EXPECTED_INSTRUCTIONS = {
    ("0x004c7900", "0x004c7900", "FLD", "float ptr [ECX + 0x8]", "d9 41 08"),
    ("0x004c7900", "0x004c791e", "FCOM", "float ptr [0x005d856c]", "d8 15 6c 85 5d 00"),
    ("0x004c7900", "0x004c792d", "FDIVR", "float ptr [0x005d8568]", "d8 3d 68 85 5d 00"),
    ("0x004c7900", "0x004c7947", "RET", "", "c3"),
    ("0x004c7d90", "0x004c7d90", "MOV", "EAX, ECX", "8b c1"),
    ("0x004c7d90", "0x004c7d92", "MOV", "ECX, dword ptr [ESP + 0x4]", "8b 4c 24 04"),
    ("0x004c7d90", "0x004c7da6", "RET", "0x4", "c2 04 00"),
}

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "runtime rendering proven",
    "exact layout proven",
    "source identity proven",
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
        for key in ("address", "target_addr", "from_addr", "from_function_addr", "function_entry", "instruction_addr"):
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
        r"SUMMARY\s+updated=(\d+)\s+skipped=(\d+)\s+created=(\d+)\s+would_create=(\d+)\s+renamed=(\d+)\s+would_rename=(\d+)\s+missing=(\d+)\s+bad=(\d+)",
        text,
    )
    if not match:
        return {}
    keys = ("updated", "skipped", "created", "would_create", "renamed", "would_rename", "missing", "bad")
    return {key: int(value) for key, value in zip(keys, match.groups())}


def check_summary(path: Path, expected: dict[str, int], failures: list[str]) -> None:
    actual = parse_summary(path)
    if not actual:
        failures.append(f"{path.name}: missing SUMMARY line")
        return
    for key, expected_value in expected.items():
        actual_value = actual.get(key)
        if actual_value != expected_value:
            failures.append(f"{path.name}: {key} expected {expected_value}, got {actual_value}")
    text = read_text(path)
    if "REPORT: Save succeeded" not in text:
        failures.append(f"{path.name}: missing Ghidra save success marker")


def check_metadata(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_metadata.tsv")
    if len(rows) < len(TARGETS):
        failures.append(f"post_metadata.tsv: expected at least {len(TARGETS)} rows, got {len(rows)}")
    for address, expected in TARGETS.items():
        row = row_by_address(rows, address)
        if row is None:
            failures.append(f"{address}: missing metadata row")
            continue
        if row.get("status") != "OK":
            failures.append(f"{address}: metadata status {row.get('status')!r}")
        if row.get("name") != expected["name"]:
            failures.append(f"{address}: expected name {expected['name']!r}, got {row.get('name')!r}")
        if row.get("signature") != expected["signature"]:
            failures.append(f"{address}: expected signature {expected['signature']!r}, got {row.get('signature')!r}")
        comment = row.get("comment", "")
        for token in expected["commentTokens"]:  # type: ignore[index]
            if token not in comment:
                failures.append(f"{address}: comment missing token {token!r}")
        lowered = comment.lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"{address}: comment contains overclaim token {token!r}")


def check_tags(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_tags.tsv")
    seen: dict[str, set[str]] = {}
    for row in rows:
        address = normalize_address(row.get("address", ""))
        tags = {tag for tag in row.get("tags", "").split(";") if tag}
        seen[address] = tags
    for address, expected in TARGETS.items():
        actual = seen.get(normalize_address(address), set())
        for tag in expected["tags"]:  # type: ignore[index]
            if tag not in actual:
                failures.append(f"{address}: missing tag {tag!r}; actual={sorted(actual)!r}")


def check_xrefs(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_xrefs.tsv")
    edges = {(row.get("target_addr", ""), row.get("from_addr", ""), row.get("from_function", "")) for row in rows}
    for edge in EXPECTED_XREF_EDGES:
        if edge not in edges:
            failures.append(f"post_xrefs.tsv: missing xref edge {edge!r}")


def check_decompile(base: Path, failures: list[str]) -> None:
    for address, expected in TARGETS.items():
        decompile = decompile_text_for(base, address)
        if not decompile:
            failures.append(f"{address}: missing post decompile export")
            continue
        for token in expected["decompileTokens"]:  # type: ignore[index]
            if not token_present(decompile, token):
                failures.append(f"{address}: decompile missing token {token!r}")
        for token in OVERCLAIM_TOKENS:
            if token in decompile.lower():
                failures.append(f"{address}: decompile contains overclaim token {token!r}")


def check_instructions(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_instructions.tsv")
    seen = {
        (
            normalize_address(row.get("target_addr", "")),
            normalize_address(row.get("instruction_addr", "")),
            row.get("mnemonic", ""),
            row.get("operands", ""),
            row.get("bytes", ""),
        )
        for row in rows
    }
    for expected in EXPECTED_INSTRUCTIONS:
        if expected not in seen:
            failures.append(f"post_instructions.tsv: missing instruction evidence {expected!r}")


def run_checks(base: Path) -> tuple[str, list[str]]:
    failures: list[str] = []
    check_summary(base / "dry.log", EXPECTED_DRY, failures)
    check_summary(base / "apply.log", EXPECTED_APPLY, failures)
    check_summary(base / "verify_dry.log", EXPECTED_VERIFY_DRY, failures)
    check_metadata(base, failures)
    check_tags(base, failures)
    check_xrefs(base, failures)
    check_decompile(base, failures)
    check_instructions(base, failures)
    return ("FAIL" if failures else "PASS", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=BASE, help="Wave469 artifact directory")
    parser.add_argument("--check", action="store_true", help="Return nonzero on validation failure")
    args = parser.parse_args()

    status, failures = run_checks(args.base)
    print(f"STATUS {status}")
    for failure in failures:
        print(f"- {failure}")
    if args.check and failures:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
