#!/usr/bin/env python3
"""Validate Wave490 ResourceAccumulator static RE evidence."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave490-resource-accumulator-004d6f70"

EXPECTED = {
    "0x004d6f70": {
        "name": "CResourceAccumulator__GetResourceFilename",
        "signature": "void __cdecl CResourceAccumulator__GetResourceFilename(char * out_path, int resource_id, int platform_id)",
        "tags": {
            "static-reaudit",
            "resource-accumulator-wave490",
            "retail-binary-evidence",
            "resource-accumulator",
            "aya-resource",
            "signature-corrected",
            "comment-hardened",
            "resource-path",
        },
        "comment": ["out_path", "resource_id", "platform_id", "PC/PS2/XBOX", "data\\Resources", "rebuild parity remain unproven"],
        "decompile": ["platform_id", "resource_id", "out_path", "data\\Resources", "s_data_Resources_goodie"],
    },
    "0x004d7200": {
        "name": "CResourceAccumulator__ReadResourceFile",
        "signature": "void __cdecl CResourceAccumulator__ReadResourceFile(int resource_id, void * existing_buffer, int skip_optional_chunks)",
        "tags": {
            "static-reaudit",
            "resource-accumulator-wave490",
            "retail-binary-evidence",
            "resource-accumulator",
            "aya-resource",
            "signature-corrected",
            "comment-hardened",
            "chunk-reader",
            "resource-load",
        },
        "comment": ["resource_id", "existing_buffer", "skip_optional_chunks", "CChunkReader", "MESH", "GDIE", "rebuild parity remain unproven"],
        "decompile": ["resource_id", "existing_buffer", "skip_optional_chunks", "CResourceAccumulator__GetResourceFilename", "CChunkReader__OpenFile", "CFEPGoodies__Deserialise"],
    },
}

EXPECTED_SUMMARIES = {
    "apply_resource_accumulator_wave490_dry.log": {"updated": 0, "skipped": 2, "created": 0, "would_create": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
    "apply_resource_accumulator_wave490_apply.log": {"updated": 2, "skipped": 0, "created": 0, "would_create": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
    "apply_resource_accumulator_wave490_verify_dry.log": {"updated": 0, "skipped": 2, "created": 0, "would_create": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
}

XREFS = [
    ("0x004d6f70", "0x004d72f9", "CResourceAccumulator__ReadResourceFile"),
    ("0x004d6f70", "0x0045ca4e", "CFEPGoodies__StartLoadingGoody"),
    ("0x004d7200", "0x004eff20", "CLTShell__InitializeRuntimeAndLoadCoreResources"),
    ("0x004d7200", "0x004687f8", "CFrontEnd__LoadSharedResources"),
    ("0x004d7200", "0x0046cd87", "CGame__LoadResources"),
    ("0x004d7200", "0x0045cc86", "CFEPGoodies__LoadingGoodyPoll"),
]

CALLSITE_TOKENS = [
    "0x004d72f1\t0x004d7200\tCResourceAccumulator__ReadResourceFile\tPUSH\t0x1",
    "0x004d72f3\t0x004d7200\tCResourceAccumulator__ReadResourceFile\tPUSH\tEBX",
    "0x004d72f4\t0x004d7200\tCResourceAccumulator__ReadResourceFile\tPUSH\tEDI",
    "0x004d72fe\t0x004d7200\tCResourceAccumulator__ReadResourceFile\tADD\tESP, 0xc",
    "0x004eff1e\t0x004efb10\tCLTShell__InitializeRuntimeAndLoadCoreResources\tPUSH\t-0x1",
    "0x004eff25\t0x004efb10\tCLTShell__InitializeRuntimeAndLoadCoreResources\tADD\tESP, 0xc",
    "0x004687f6\t0x004687e0\tCFrontEnd__LoadSharedResources\tPUSH\t-0x2",
    "0x004687fd\t0x004687e0\tCFrontEnd__LoadSharedResources\tADD\tESP, 0xc",
    "0x0046cd86\t0x0046cd30\tCGame__LoadResources\tPUSH\tEDI",
    "0x0046cd8c\t0x0046cd30\tCGame__LoadResources\tADD\tESP, 0xc",
]

OVERCLAIMS = ("fully re'ed", "runtime behavior proven", "source identity proven", "exact layout proven", "rebuild parity proven")


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if not value or value.startswith("<"):
        return value
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def compact(value: str) -> str:
    return "".join(value.lower().split())


def has_token(text: str, token: str) -> bool:
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
        for key in ("address", "target_addr", "from_addr"):
            if key in row and row[key]:
                row[key] = normalize_address(row[key])
        if "comment" in row:
            row["comment"] = unescape(row["comment"])
    return rows


def parse_summary(text: str) -> dict[str, int] | None:
    match = re.search(
        r"updated=(\d+)\s+skipped=(\d+)\s+created=(\d+)\s+would_create=(\d+)\s+renamed=(\d+)\s+would_rename=(\d+)\s+missing=(\d+)\s+bad=(\d+)",
        text,
    )
    if not match:
        return None
    keys = ("updated", "skipped", "created", "would_create", "renamed", "would_rename", "missing", "bad")
    return {key: int(value) for key, value in zip(keys, match.groups(), strict=True)}


def decompile_text(base: Path, address: str, name: str) -> str:
    return read_text(base / "post-decomp" / f"{normalize_address(address)[2:]}_{name}.c")


def check_logs(base: Path, failures: list[str]) -> None:
    for filename, expected in EXPECTED_SUMMARIES.items():
        text = read_text(base / filename)
        if not text:
            failures.append(f"{filename}: missing")
            continue
        if parse_summary(text) != expected:
            failures.append(f"{filename}: summary mismatch {parse_summary(text)} != {expected}")
        for bad in ("FAIL:", "LockException", "Exception:"):
            if bad in text:
                failures.append(f"{filename}: unexpected token {bad!r}")
        if "REPORT: Save succeeded" not in text:
            failures.append(f"{filename}: missing save-success marker")


def check_metadata(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_metadata.tsv")
    tags = read_tsv(base / "post_tags.tsv")
    if len(rows) != len(EXPECTED):
        failures.append(f"post_metadata.tsv: expected {len(EXPECTED)} rows, got {len(rows)}")
    for address, expected in EXPECTED.items():
        row = next((r for r in rows if r.get("address") == address), None)
        if row is None:
            failures.append(f"{address}: missing metadata")
            continue
        if row.get("name") != expected["name"]:
            failures.append(f"{address}: name {row.get('name')} != {expected['name']}")
        if compact(row.get("signature", "")) != compact(str(expected["signature"])):
            failures.append(f"{address}: signature {row.get('signature')} != {expected['signature']}")
        comment = row.get("comment", "")
        for token in expected["comment"]:  # type: ignore[index]
            if not has_token(comment, str(token)):
                failures.append(f"{address}: comment missing token {token!r}")
        for token in OVERCLAIMS:
            if has_token(comment, token):
                failures.append(f"{address}: overclaim token {token!r}")
        tag_row = next((r for r in tags if r.get("address") == address), None)
        if tag_row is None:
            failures.append(f"{address}: missing tags")
            continue
        actual_tags = {part.strip() for part in re.split(r"[;,]", tag_row.get("tags", "")) if part.strip()}
        missing = set(expected["tags"]) - actual_tags  # type: ignore[arg-type]
        if missing:
            failures.append(f"{address}: missing tags {sorted(missing)}")


def check_decompile(base: Path, failures: list[str]) -> None:
    for address, expected in EXPECTED.items():
        text = decompile_text(base, address, str(expected["name"]))
        if not text:
            failures.append(f"{address}: missing decompile")
            continue
        for token in expected["decompile"]:  # type: ignore[index]
            if not has_token(text, str(token)):
                failures.append(f"{address}: decompile missing token {token!r}")


def check_xrefs(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_xrefs.tsv")
    for target, from_addr, from_function in XREFS:
        row = next((r for r in rows if r.get("target_addr") == target and r.get("from_addr") == from_addr), None)
        if row is None:
            failures.append(f"{target}: missing xref from {from_addr}")
            continue
        if row.get("from_function") != from_function:
            failures.append(f"{target}: xref {from_addr} function {row.get('from_function')} != {from_function}")


def check_instructions(base: Path, failures: list[str]) -> None:
    text = read_text(base / "post_callsite_instructions.tsv")
    for token in CALLSITE_TOKENS:
        if token not in text:
            failures.append(f"post_callsite_instructions.tsv missing token {token!r}")
    target_text = read_text(base / "post_instructions.tsv")
    for token in ("0x004d6f70", "MOV\tEAX, dword ptr [ESP + 0xc]", "0x004d7200", "CALL\t0x004d6f70", "CALL\t0x004d7200"):
        if token not in target_text and token not in text:
            failures.append(f"instruction exports missing token {token!r}")


def run(base: Path = DEFAULT_BASE) -> list[str]:
    failures: list[str] = []
    check_logs(base, failures)
    check_metadata(base, failures)
    check_decompile(base, failures)
    check_xrefs(base, failures)
    check_instructions(base, failures)
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    failures = run(args.base)
    if failures:
        print("FAIL Wave490 ResourceAccumulator probe")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("PASS Wave490 ResourceAccumulator probe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
