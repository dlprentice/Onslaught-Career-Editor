#!/usr/bin/env python3
"""Validate the Wave431 destructable-segments cylinder-cache Ghidra correction."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave431-cmcbuggy-hiveboss-current"

COMMON_TAGS = {"static-reaudit", "cmcbuggy-hiveboss-wave431", "retail-binary-evidence"}


def target(
    name: str,
    signature: str,
    comment_tokens: list[str],
    decompile_tokens: list[str],
    tags: list[str],
    xref_tokens: list[str] | None = None,
) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "commentTokens": comment_tokens,
        "decompileTokens": decompile_tokens,
        "tags": sorted(COMMON_TAGS | set(tags)),
        "xrefTokens": xref_tokens or [],
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x00497130": target(
        "CDestructableSegmentsMotionController__DestructorThunk_00497130",
        "void __fastcall CDestructableSegmentsMotionController__DestructorThunk_00497130(void * this)",
        [
            "one-instruction JMP thunk",
            "0x00494cc0",
            "only observed caller",
            "CMCHiveBoss__VFunc_01_00497110",
            "runtime destruction coverage remain unproven",
        ],
        ["CDestructableSegmentsMotionController__Destructor", "CMotionController__ctor_like_004bae50"],
        ["destructable-segments", "destructor", "thunk", "renamed", "signature-corrected", "comment-hardened"],
        ["CMCHiveBoss__VFunc_01_00497110"],
    ),
    "0x00497140": target(
        "CDestructableSegmentsMotionController__CacheNamedCollisionCylinders",
        "void __thiscall CDestructableSegmentsMotionController__CacheNamedCollisionCylinders(void * this, void * mesh_model)",
        [
            "RET 0x4",
            "one mesh/model stack argument",
            "count at +0x15c",
            "pointer table at +0x160",
            "names at +0xdc",
            "caches matching parts into +0x18..+0x74",
            "sets +0x14",
            "runtime collision behavior remain unproven",
        ],
        ["s_Nmidoutcyl", "s_Stopincyl", "+0x15c", "+0x160", "+0xdc", "+ 0x74"],
        ["destructable-segments", "collision-cylinder-cache", "token-readback", "owner-corrected", "renamed", "signature-corrected", "comment-hardened"],
        ["0x004976f1", "<no_function>"],
    ),
}

EXPECTED_DRY = {"updated": 0, "skipped": 2, "renamed": 0, "would_rename": 2, "missing": 0, "bad": 0}
EXPECTED_APPLY = {"updated": 2, "skipped": 0, "renamed": 2, "would_rename": 0, "missing": 0, "bad": 0}
EXPECTED_VERIFY_DRY = {"updated": 0, "skipped": 2, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}

OVERCLAIM_TOKENS = (
    "runtime proof",
    "runtime behavior proven",
    "runtime collision behavior proven",
    "runtime destruction behavior proven",
    "concrete layout proven",
    "source identity proven",
    "rebuild parity proven",
    "fully re'ed",
    "100% re",
)

EXPECTED_INSTRUCTIONS = {
    "0x00497130": [("TARGET", "JMP", "0x00494cc0")],
    "0x00497140": [("AFTER", "RET", "0x4"), ("AFTER", "MOV", "dword ptr [ECX + 0x74]")],
}


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
        for key in ("address", "target_addr", "from_addr", "from_function_addr", "function_entry"):
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


def rows_by_address(rows: list[dict[str, str]], address: str, key: str = "target_addr") -> list[dict[str, str]]:
    wanted = normalize_address(address)
    return [row for row in rows if normalize_address(row.get(key, "")) == wanted]


def decompile_text_for(base: Path, address: str) -> str:
    directory = base / "decompile_after"
    if not directory.is_dir():
        return ""
    prefix = normalize_address(address)[2:]
    matches = sorted(directory.glob(f"{prefix}_*.c"))
    if not matches:
        return ""
    return read_text(matches[0])


def parse_summary(text: str) -> dict[str, int] | None:
    match = re.search(
        r"SUMMARY:\s+updated=(\d+)\s+skipped=(\d+)\s+renamed=(\d+)\s+would_rename=(\d+)\s+missing=(\d+)\s+bad=(\d+)",
        text,
    )
    if not match:
        return None
    keys = ["updated", "skipped", "renamed", "would_rename", "missing", "bad"]
    return {key: int(value) for key, value in zip(keys, match.groups(), strict=True)}


def check_apply_log(base: Path, name: str, expected: dict[str, int], failures: list[str]) -> None:
    text = read_text(base / name)
    if not text:
        failures.append(f"{name}: missing or empty")
        return
    summary = parse_summary(text)
    if summary != expected:
        failures.append(f"{name}: summary mismatch expected {expected}, got {summary}")
    for token in ("FAIL:", "Exception", "LockException"):
        if token in text:
            failures.append(f"{name}: unexpected failure token {token!r}")
    if "REPORT: Save succeeded" not in text and name.endswith(".log") and name != "apply_dry.log":
        failures.append(f"{name}: missing Ghidra save-success marker")


def check_metadata(base: Path, failures: list[str]) -> None:
    metadata = read_tsv(base / "metadata_after.tsv")
    tags = read_tsv(base / "tags_after.tsv")
    xrefs = read_tsv(base / "xrefs_after.tsv")
    instructions = read_tsv(base / "instructions_after.tsv")
    full_cylinder_instructions = read_tsv(base / "instructions_cylinders_full_after.tsv")

    for address, spec in TARGETS.items():
        row = row_by_address(metadata, address)
        if row is None:
            failures.append(f"{address}: missing metadata_after row")
            continue
        if row.get("name") != spec["name"]:
            failures.append(f"{address}: name mismatch {row.get('name')!r}")
        if row.get("signature") != spec["signature"]:
            failures.append(f"{address}: signature mismatch {row.get('signature')!r}")
        comment = row.get("comment", "")
        for token in spec["commentTokens"]:  # type: ignore[index]
            if not token_present(comment, str(token)):
                failures.append(f"{address}: comment missing token {token!r}")
        lowered_comment = comment.lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered_comment:
                failures.append(f"{address}: overclaim token present {token!r}")

        tag_row = row_by_address(tags, address)
        if tag_row is None:
            failures.append(f"{address}: missing tags_after row")
        else:
            actual_tags = {item.strip() for item in re.split(r"[;,]", tag_row.get("tags", "")) if item.strip()}
            missing = sorted(set(spec["tags"]) - actual_tags)  # type: ignore[arg-type]
            if missing:
                failures.append(f"{address}: missing tags {missing}")

        decompile = decompile_text_for(base, address)
        if not decompile:
            failures.append(f"{address}: missing decompile_after")
        for token in spec["decompileTokens"]:  # type: ignore[index]
            if not token_present(decompile, str(token)):
                failures.append(f"{address}: decompile missing token {token!r}")

        if spec["xrefTokens"]:  # type: ignore[index]
            text = "\n".join("\t".join(row.values()) for row in rows_by_address(xrefs, address))
            for token in spec["xrefTokens"]:  # type: ignore[index]
                if not token_present(text, str(token)):
                    failures.append(f"{address}: xrefs_after missing token {token!r}")

        rows = rows_by_address(instructions, address)
        if address == "0x00497140":
            rows += rows_by_address(full_cylinder_instructions, address)
        for role, mnemonic, operand in EXPECTED_INSTRUCTIONS[address]:
            if not any(
                row.get("role") == role
                and row.get("mnemonic") == mnemonic
                and token_present(row.get("operands", ""), operand)
                for row in rows
            ):
                failures.append(f"{address}: instruction evidence missing {role} {mnemonic} {operand}")


def run(base: Path) -> dict[str, object]:
    failures: list[str] = []
    check_apply_log(base, "apply_dry.log", EXPECTED_DRY, failures)
    check_apply_log(base, "apply.log", EXPECTED_APPLY, failures)
    check_apply_log(base, "apply_verify_dry.log", EXPECTED_VERIFY_DRY, failures)
    check_metadata(base, failures)

    return {
        "status": "PASS" if not failures else "FAIL",
        "checkedAt": datetime.now(timezone.utc).isoformat(),
        "base": str(base),
        "targets": sorted(TARGETS),
        "failures": failures,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=BASE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    result = run(args.base)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
