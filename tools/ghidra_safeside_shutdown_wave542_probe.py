#!/usr/bin/env python3
"""Validate Wave542 CSafeSide shutdown/unlink Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave542-safeside-vfunc-004de1d0"
ADDRESS = "0x004de1d0"
RAW_ADDRESS = "004de1d0"
NAME = "CSafeSide__ShutdownAndUnlinkFactionAnchor"
SIGNATURE = f"void __fastcall {NAME}(void * this)"
COMMON_TAGS = {
    "static-reaudit",
    "safeside-wave542",
    "retail-binary-evidence",
    "signature-corrected",
    "comment-hardened",
    "owner-retained",
    "renamed",
}
OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "source identity proven",
    "rebuild parity proven",
    "fully recovered",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if not value or value.startswith("<"):
        return value
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def raw_address(value: str) -> str:
    value = value.strip().lower()
    if not value or value.startswith("<"):
        return value
    if value.startswith("0x"):
        value = value[2:]
    return value.zfill(8)


def token_present(text: str, token: str) -> bool:
    return token.lower() in text.lower()


def parse_summary(path: Path) -> dict[str, int]:
    text = read_text(path)
    match = re.search(
        r"SUMMARY updated=(\d+) skipped=(\d+) renamed=(\d+) would_rename=(\d+) missing=(\d+) bad=(\d+)",
        text,
    )
    require(match is not None, f"missing summary in {path}")
    keys = ("updated", "skipped", "renamed", "would_rename", "missing", "bad")
    return {key: int(value) for key, value in zip(keys, match.groups())}


def check_metadata() -> None:
    rows = read_tsv(BASE / "post_metadata.tsv")
    require(len(rows) == 1, f"metadata row count {len(rows)}")
    row = rows[0]
    require(normalize_address(row["address"]) == ADDRESS, "metadata address mismatch")
    require(row["name"] == NAME, f"metadata name mismatch {row['name']}")
    require(row["signature"] == SIGNATURE, f"signature mismatch {row['signature']}")
    require(row["status"] == "OK", f"metadata status {row['status']}")
    for token in (
        "vtable slot data at 0x005dcce4",
        "DAT_00855160",
        "CSPtrSet__Remove",
        "CComplexThing__Shutdown",
        "CUnit__FindNearestFactionAnchor",
        "Static retail evidence only",
    ):
        require(token_present(row["comment"], token), f"comment missing {token!r}")
    lowered = row["comment"].lower()
    for token in OVERCLAIM_TOKENS:
        require(token not in lowered, f"comment contains overclaim token {token}")


def check_tags() -> None:
    rows = read_tsv(BASE / "post_tags.tsv")
    require(len(rows) == 1, f"tag row count {len(rows)}")
    row = rows[0]
    require(raw_address(row["address"]) == RAW_ADDRESS, "tag address mismatch")
    tags = set(filter(None, row["tags"].split(";")))
    require(COMMON_TAGS.issubset(tags), f"missing tags {sorted(COMMON_TAGS - tags)}")


def check_xrefs() -> None:
    rows = read_tsv(BASE / "post_xrefs.tsv")
    actual = {
        (
            raw_address(row["target_addr"]),
            row["target_name"],
            raw_address(row["from_addr"]),
            raw_address(row["from_function_addr"]),
            row["from_function"],
            row["ref_type"],
        )
        for row in rows
    }
    expected = {
        (RAW_ADDRESS, NAME, "005dcce4", "<none>", "<no_function>", "DATA"),
    }
    require(expected.issubset(actual), f"missing expected xref rows: {sorted(expected - actual)}")


def check_vtables() -> None:
    rows = read_tsv(BASE / "post_vtables.tsv")
    actual = {
        (raw_address(row["vtable"]), row["slot_index"], raw_address(row["slot_addr"]), raw_address(row["function_entry"]), row["function_name"], row["status"])
        for row in rows
    }
    expected = {
        ("005dccc0", "9", "005dcce4", RAW_ADDRESS, NAME, "OK"),
        ("005dccc4", "8", "005dcce4", RAW_ADDRESS, NAME, "OK"),
        ("005dccd0", "5", "005dcce4", RAW_ADDRESS, NAME, "OK"),
    }
    require(expected.issubset(actual), f"missing expected vtable rows: {sorted(expected - actual)}")


def check_decompile() -> None:
    index = read_tsv(BASE / "post_decomp" / "index.tsv")
    require(len(index) == 1, f"decompile index row count {len(index)}")
    require(index[0]["status"] == "OK", f"decompile status {index[0]['status']}")
    text = read_text(BASE / "post_decomp" / f"{RAW_ADDRESS}_{NAME}.c")
    for token in (
        f"/* name: {NAME} */",
        f"/* signature: {SIGNATURE} */",
        "CSPtrSet__Remove(&DAT_00855160,this)",
        "CComplexThing__Shutdown(this)",
    ):
        require(token_present(text, token), f"decompile missing {token!r}")
    lowered = text.lower()
    for token in OVERCLAIM_TOKENS:
        require(token not in lowered, f"decompile contains overclaim token {token}")


def check_instruction_exports() -> None:
    rows = read_tsv(BASE / "post_instructions.tsv")
    require(len(rows) == 241, f"instruction row count {len(rows)}")
    body = {(raw_address(row["instruction_addr"]), row["mnemonic"], row["operands"]) for row in rows}
    for item in (
        ("004de1d0", "PUSH", "ESI"),
        ("004de1d4", "MOV", "ECX, 0x855160"),
        ("004de1d9", "CALL", "0x004e5bd0"),
        ("004de1e0", "CALL", "0x004f41b0"),
        ("004de1e6", "RET", ""),
    ):
        require(item in body, f"instruction export missing {item}")


def check_logs() -> None:
    require(
        parse_summary(BASE / "apply_safeside_shutdown_wave542_apply.log")
        == {"updated": 1, "skipped": 0, "renamed": 1, "would_rename": 0, "missing": 0, "bad": 0},
        "apply summary mismatch",
    )
    require(
        parse_summary(BASE / "apply_safeside_shutdown_wave542_verify_dry.log")
        == {"updated": 0, "skipped": 1, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        "verify dry summary mismatch",
    )
    require("REPORT: Save succeeded" in read_text(BASE / "apply_safeside_shutdown_wave542_apply.log"), "apply log missing save report")


def check_docs_when_present() -> None:
    docs = [
        ROOT / "release" / "readiness" / "ghidra_safeside_shutdown_wave542_2026-05-18.md",
        ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md",
        ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md",
        ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Sentinel.cpp" / "_index.md",
    ]
    for path in docs:
        if not path.is_file():
            continue
        text = read_text(path)
        if "Wave542" not in text:
            continue
        require(NAME in text, f"{path} missing {NAME}")
        require(ADDRESS in text or RAW_ADDRESS in text, f"{path} missing {ADDRESS}")
        lowered = text.lower()
        for token in OVERCLAIM_TOKENS:
            require(token not in lowered, f"{path} contains overclaim token {token}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run Wave542 checks")
    args = parser.parse_args()
    if not args.check:
        parser.error("--check is required")

    check_metadata()
    check_tags()
    check_xrefs()
    check_vtables()
    check_decompile()
    check_instruction_exports()
    check_logs()
    check_docs_when_present()
    print("Wave542 SafeSide shutdown probe PASS: 1 function, vtable/read-back evidence verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
