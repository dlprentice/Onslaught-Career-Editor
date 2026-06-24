#!/usr/bin/env python3
"""Validate Wave543 CUnit default tuning-block Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave543-cunit-default-tuning-004eb9a0"
ADDRESS = "0x004eb9a0"
RAW_ADDRESS = "004eb9a0"
NAME = "CUnit__InitDefaultTuningBlock"
SIGNATURE = f"void __fastcall {NAME}(void * tuning_block)"
COMMON_TAGS = {
    "static-reaudit",
    "unit-default-tuning-wave543",
    "retail-binary-evidence",
    "signature-corrected",
    "comment-hardened",
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


def raw_address(value: str) -> str:
    value = value.strip().lower()
    if not value or value.startswith("<"):
        return value
    if value.startswith("0x"):
        value = value[2:]
    return value.zfill(8)


def normalize_address(value: str) -> str:
    raw = raw_address(value)
    if raw.startswith("<"):
        return raw
    return "0x" + raw


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
        "tuning block passed in ECX",
        "+0x00..+0x84",
        "1.0 at +0x00/+0x04/+0x08/+0x0c/+0x1c/+0x50/+0x60",
        "0.1 at +0x40",
        "0.8 at +0x54/+0x58/+0x5c",
        "0x004eb1d0",
        "0x0083d248",
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
        (RAW_ADDRESS, NAME, "004eb1d5", "<none>", "<no_function>", "UNCONDITIONAL_CALL"),
    }
    require(expected.issubset(actual), f"missing expected xref rows: {sorted(expected - actual)}")


def check_decompile() -> None:
    index = read_tsv(BASE / "post_decomp" / "index.tsv")
    require(len(index) == 1, f"decompile index row count {len(index)}")
    require(index[0]["status"] == "OK", f"decompile status {index[0]['status']}")
    text = read_text(BASE / "post_decomp" / f"{RAW_ADDRESS}_{NAME}.c")
    for token in (
        f"/* name: {NAME} */",
        f"/* signature: {SIGNATURE} */",
        "void __fastcall CUnit__InitDefaultTuningBlock(void *tuning_block)",
        "*(undefined4 *)tuning_block = 0x3f800000",
        "*(undefined4 *)((int)tuning_block + 0x40) = 0x3dcccccd",
        "*(undefined4 *)((int)tuning_block + 0x54) = 0x3f4ccccd",
        "*(undefined4 *)((int)tuning_block + 0x84) = 0",
    ):
        require(token_present(text, token), f"decompile missing {token!r}")
    lowered = text.lower()
    for token in OVERCLAIM_TOKENS:
        require(token not in lowered, f"decompile contains overclaim token {token}")


def check_instruction_exports() -> None:
    rows = read_tsv(BASE / "post_instructions.tsv")
    require(len(rows) == 145, f"instruction row count {len(rows)}")
    body = {(raw_address(row["instruction_addr"]), row["mnemonic"], row["operands"]) for row in rows}
    for item in (
        ("004eb9a0", "MOV", "EAX, ECX"),
        ("004eb9a2", "MOV", "EDX, 0x3f800000"),
        ("004eb9d8", "MOV", "dword ptr [EAX + 0x40], 0x3dcccccd"),
        ("004eb9eb", "MOV", "dword ptr [EAX + 0x54], 0x3f4ccccd"),
        ("004eba18", "MOV", "dword ptr [EAX + 0x80], ECX"),
        ("004eba1e", "MOV", "dword ptr [EAX + 0x84], ECX"),
        ("004eba24", "RET", ""),
    ):
        require(item in body, f"instruction export missing {item}")


def check_caller_instruction_exports() -> None:
    rows = read_tsv(BASE / "post_caller_instructions.tsv")
    require(len(rows) == 97, f"caller instruction row count {len(rows)}")
    body = {(raw_address(row["instruction_addr"]), row["function_entry"], row["function_name"], row["mnemonic"], row["operands"]) for row in rows}
    for item in (
        ("004eb1d0", "<none>", "<no_function>", "MOV", "ECX, 0x83d248"),
        ("004eb1d5", "<none>", "<no_function>", "JMP", "0x004eb9a0"),
    ):
        require(item in body, f"caller instruction export missing {item}")


def check_logs() -> None:
    require(
        parse_summary(BASE / "apply_unit_default_tuning_wave543_apply.log")
        == {"updated": 1, "skipped": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        "apply summary mismatch",
    )
    require(
        parse_summary(BASE / "apply_unit_default_tuning_wave543_verify_dry.log")
        == {"updated": 0, "skipped": 1, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        "verify dry summary mismatch",
    )
    require("REPORT: Save succeeded" in read_text(BASE / "apply_unit_default_tuning_wave543_apply.log"), "apply log missing save report")


def check_docs_when_present() -> None:
    docs = [
        ROOT / "release" / "readiness" / "ghidra_unit_default_tuning_wave543_2026-05-18.md",
        ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md",
        ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md",
        ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Unit.cpp" / "_index.md",
    ]
    for path in docs:
        if not path.is_file():
            continue
        text = read_text(path)
        if "Wave543" not in text:
            continue
        require(NAME in text, f"{path} missing {NAME}")
        require(ADDRESS in text or RAW_ADDRESS in text, f"{path} missing {ADDRESS}")
        lowered = text.lower()
        for token in OVERCLAIM_TOKENS:
            require(token not in lowered, f"{path} contains overclaim token {token}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run Wave543 checks")
    args = parser.parse_args()
    if not args.check:
        parser.error("--check is required")

    check_metadata()
    check_tags()
    check_xrefs()
    check_decompile()
    check_instruction_exports()
    check_caller_instruction_exports()
    check_logs()
    check_docs_when_present()
    print("Wave543 CUnit default tuning probe PASS: signature/comment/read-back evidence verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
