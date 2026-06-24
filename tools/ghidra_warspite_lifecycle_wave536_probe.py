#!/usr/bin/env python3
"""Validate Wave536 Warspite lifecycle Ghidra metadata hardening."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave536-warspite-lifecycle-00504460"
COMMON_TAGS = {
    "static-reaudit",
    "warspite-lifecycle-wave536",
    "retail-binary-evidence",
    "signature-corrected",
    "comment-hardened",
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
    "0x00504460": target(
        "CWarspite__Create",
        "void __thiscall CWarspite__Create(void * this, void * init_context)",
        ["RET 0x4", "0x005dfbdc", "this+0x13c", "rebuild parity remain unproven"],
        ["warspite-ai", "factory", "allocator", "vtable-readback"],
        ["init_context", "CWarspite__Init", "0x005dfbdc"],
    ),
    "0x005044f0": target(
        "CWarspite__ScalarDeletingDestructor",
        "void * __thiscall CWarspite__ScalarDeletingDestructor(void * this, byte delete_flags)",
        ["vtable 0x005dfbdc slot 1", "delete_flags", "MSVC scalar deleting destructor", "rebuild parity remain unproven"],
        ["warspite-ai", "destructor", "scalar-deleting-destructor", "renamed", "vtable-readback"],
        ["delete_flags", "CWarspite__Destructor", "CDXMemoryManager__Free"],
    ),
    "0x00504510": target(
        "CWarspite__Destructor",
        "void __fastcall CWarspite__Destructor(void * this)",
        ["0x005d8d1c", "CSPtrSet", "CMonitor__Shutdown", "rebuild parity remain unproven"],
        ["warspite-ai", "destructor", "csptrset-unregister", "monitor-shutdown"],
        ["0x005d8d1c", "CSPtrSet__Remove", "CMonitor__Shutdown"],
    ),
    "0x005047e0": target(
        "CWarspiteDome__Init",
        "void __thiscall CWarspiteDome__Init(void * this, void * init_context)",
        ["RET 0x4", "0x005dfc14", "CMCWarspiteDome", "rebuild parity remain unproven"],
        ["warspitedome", "init", "allocator", "motion-controller", "occupancy-shadow"],
        ["init_context", "CGroundUnit__Init", "CWarspite__Init", "CMCWarspiteDome__Constructor"],
    ),
    "0x00504990": target(
        "CWarspiteDome__ScalarDeletingDestructor",
        "void * __thiscall CWarspiteDome__ScalarDeletingDestructor(void * this, byte delete_flags)",
        ["vtable 0x005dfc14 slot 1", "delete_flags", "MSVC scalar deleting destructor", "rebuild parity remain unproven"],
        ["warspitedome", "destructor", "scalar-deleting-destructor", "vtable-readback"],
        ["delete_flags", "CWarspiteDome__Destructor", "CDXMemoryManager__Free"],
    ),
    "0x005049b0": target(
        "CWarspiteDome__Destructor",
        "void __fastcall CWarspiteDome__Destructor(void * this)",
        ["0x005d8d1c", "CSPtrSet", "CMonitor__Shutdown", "rebuild parity remain unproven"],
        ["warspitedome", "destructor", "csptrset-unregister", "monitor-shutdown"],
        ["0x005d8d1c", "CSPtrSet__Remove", "CMonitor__Shutdown"],
    ),
}

EXPECTED_XREFS = {
    ("0x00504460", "005e085c", "<no_function>"),
    ("0x005044f0", "005dfbe0", "<no_function>"),
    ("0x00504510", "005044f3", "CWarspite__ScalarDeletingDestructor"),
    ("0x005047e0", "005e0200", "<no_function>"),
    ("0x00504990", "005dfc18", "<no_function>"),
    ("0x005049b0", "00504993", "CWarspiteDome__ScalarDeletingDestructor"),
}

EXPECTED_APPLY = {"updated": 6, "skipped": 0, "renamed": 1, "would_rename": 0, "missing": 0, "bad": 0}
EXPECTED_VERIFY_DRY = {"updated": 0, "skipped": 6, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}
OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "source identity proven",
    "rebuild parity proven",
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
        for key in ("address", "target_addr"):
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


def decompile_text_for(address: str) -> str:
    directory = BASE / "post_decomp"
    if not directory.is_dir():
        return ""
    prefix = normalize_address(address)[2:]
    matches = sorted(directory.glob(f"{prefix}_*.c"))
    return read_text(matches[0]) if matches else ""


def parse_summary(text: str) -> dict[str, int] | None:
    match = re.search(
        r"SUMMARY\s+updated=(\d+)\s+skipped=(\d+)\s+renamed=(\d+)\s+would_rename=(\d+)\s+missing=(\d+)\s+bad=(\d+)",
        text,
    )
    if not match:
        return None
    keys = ["updated", "skipped", "renamed", "would_rename", "missing", "bad"]
    return {key: int(value) for key, value in zip(keys, match.groups(), strict=True)}


def check_metadata(failures: list[str]) -> None:
    metadata = read_tsv(BASE / "post_metadata.tsv")
    tags = read_tsv(BASE / "post_tags.tsv")
    for address, spec in TARGETS.items():
        row = row_by_address(metadata, address)
        if row is None:
            failures.append(f"{address}: missing post_metadata row")
            continue
        if row.get("name") != spec["name"]:
            failures.append(f"{address}: name mismatch {row.get('name')!r}")
        if row.get("signature") != spec["signature"]:
            failures.append(f"{address}: signature mismatch {row.get('signature')!r}")
        comment = row.get("comment", "")
        for token in spec["commentTokens"]:  # type: ignore[index]
            if not token_present(comment, str(token)):
                failures.append(f"{address}: comment missing token {token!r}")
        lowered = comment.lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"{address}: overclaim token present {token!r}")

        tag_row = row_by_address(tags, address)
        if tag_row is None:
            failures.append(f"{address}: missing post_tags row")
        else:
            actual = {item.strip() for item in re.split(r"[;,]", tag_row.get("tags", "")) if item.strip()}
            missing = sorted(set(spec["tags"]) - actual)  # type: ignore[arg-type]
            if missing:
                failures.append(f"{address}: missing tags {missing}")


def check_decompile(failures: list[str]) -> None:
    for address, spec in TARGETS.items():
        text = decompile_text_for(address)
        if not text:
            failures.append(f"{address}: missing post decompile")
            continue
        for token in spec["decompileTokens"]:  # type: ignore[index]
            if not token_present(text, str(token)):
                failures.append(f"{address}: decompile missing token {token!r}")
        lowered = text.lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"{address}: decompile overclaim token present {token!r}")


def check_xrefs(failures: list[str]) -> None:
    rows = read_tsv(BASE / "post_xrefs.tsv")
    actual = {
        (row.get("target_addr", ""), row.get("from_addr", "").lower(), row.get("from_function", ""))
        for row in rows
    }
    for target_addr, from_addr, from_function in EXPECTED_XREFS:
        key = (normalize_address(target_addr), from_addr.lower(), from_function)
        if key not in actual:
            failures.append(f"{target_addr}: missing xref from {from_addr} / {from_function}")


def check_logs(failures: list[str]) -> None:
    apply_log = read_text(BASE / "apply_warspite_lifecycle_wave536_apply.log")
    verify_log = read_text(BASE / "apply_warspite_lifecycle_wave536_verify_dry.log")
    if parse_summary(apply_log) != EXPECTED_APPLY:
        failures.append("apply log summary mismatch")
    if parse_summary(verify_log) != EXPECTED_VERIFY_DRY:
        failures.append("verify-dry log summary mismatch")
    for label, text in (("apply", apply_log), ("verify-dry", verify_log)):
        if "REPORT: Save succeeded" not in text:
            failures.append(f"{label} log missing save-success marker")
        for token in ("FAIL:", "Exception", "LockException", "BADNAME:", "MISSING:"):
            if token in text:
                failures.append(f"{label} log unexpected token {token!r}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    _ = parser.parse_args()

    failures: list[str] = []
    check_metadata(failures)
    check_decompile(failures)
    check_xrefs(failures)
    check_logs(failures)

    if failures:
        print("Wave536 Warspite lifecycle probe FAILED:")
        for failure in failures:
            print(f" - {failure}")
        return 1
    print("Wave536 Warspite lifecycle probe PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
