#!/usr/bin/env python3
"""Validate Wave545 CUnit render distance-fade Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave545-cunit-render-distance-fade-004f6fd0"
ADDRESS = "0x004f6fd0"
RAW_ADDRESS = "004f6fd0"
NAME = "CUnit__RenderWithDistanceFade"
CALLER_NAME = "OID__RenderWithState1BOverride"
SIGNATURE = f"bool __thiscall {NAME}(void * this, uint render_flags)"
COMMON_TAGS = {
    "static-reaudit",
    "unit-render-distance-fade-wave545",
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
        "OID__RenderWithState1BOverride",
        "this+0x48",
        "low-byte return as handled/not-handled",
        "RET 0x4",
        "one stack render_flags argument",
        "0x005d856c",
        "DAT_00672fd0",
        "0x0063012c",
        "CThing__Render",
        "0xff",
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
        (RAW_ADDRESS, NAME, "004bfac0", "004bfab0", CALLER_NAME, "UNCONDITIONAL_CALL"),
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
        "bool __thiscall CUnit__RenderWithDistanceFade(void *this,uint render_flags)",
        "*(float *)(*(int *)((int)this + 0x48) + 0xbc)",
        "DAT_00672fd0",
        "DAT_0063012c = local_8",
        "CThing__Render(this,render_flags)",
        "DAT_0063012c = 0xff",
        "return true",
        "return false",
    ):
        require(token_present(text, token), f"decompile missing {token!r}")
    for token in ("param_1", "param_2", "unaff_EDI"):
        require(not token_present(text, token), f"decompile still contains stale token {token!r}")
    lowered = text.lower()
    for token in OVERCLAIM_TOKENS:
        require(token not in lowered, f"decompile contains overclaim token {token}")


def check_caller_decompile() -> None:
    index = read_tsv(BASE / "post_caller_decomp" / "index.tsv")
    require(len(index) == 1, f"caller decompile index row count {len(index)}")
    require(index[0]["status"] == "OK", f"caller decompile status {index[0]['status']}")
    text = "\n".join(path.read_text(encoding="utf-8") for path in (BASE / "post_caller_decomp").glob("*.c"))
    for token in (
        CALLER_NAME,
        "CUnit__RenderWithDistanceFade(this,render_flags)",
        "RenderState_Set(0x1b,0)",
        "CThing__Render(this,render_flags)",
        "RenderState_Set(0x1b,1)",
    ):
        require(token_present(text, token), f"caller decompile missing {token!r}")
    for token in ("param_2", "unaff_EDI"):
        require(not token_present(text, token), f"caller decompile still contains stale token {token!r}")


def check_instruction_exports() -> None:
    rows = read_tsv(BASE / "post_instructions.tsv")
    require(len(rows) == 321, f"instruction row count {len(rows)}")
    body = {(raw_address(row["instruction_addr"]), row["mnemonic"], row["operands"]) for row in rows}
    for item in (
        ("004f6fd0", "MOV", "EDX, dword ptr [ECX + 0x48]"),
        ("004f6fe7", "JNZ", "0x004f7045"),
        ("004f6ff5", "FSUB", "float ptr [0x00672fd0]"),
        ("004f7016", "MOV", "EDX, dword ptr [ESP + 0xc]"),
        ("004f7029", "MOV", "[0x0063012c], EAX"),
        ("004f702e", "CALL", "0x004f36d0"),
        ("004f7033", "MOV", "dword ptr [0x0063012c], 0xff"),
        ("004f703d", "MOV", "AL, 0x1"),
        ("004f7042", "RET", "0x4"),
        ("004f7045", "XOR", "AL, AL"),
        ("004f704a", "RET", "0x4"),
    ):
        require(item in body, f"instruction export missing {item}")


def check_logs() -> None:
    require(
        parse_summary(BASE / "apply_cunit_render_distance_fade_wave545_apply.log")
        == {"updated": 1, "skipped": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        "apply summary mismatch",
    )
    require(
        parse_summary(BASE / "apply_cunit_render_distance_fade_wave545_verify_dry.log")
        == {"updated": 0, "skipped": 1, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        "verify dry summary mismatch",
    )
    require("REPORT: Save succeeded" in read_text(BASE / "apply_cunit_render_distance_fade_wave545_apply.log"), "apply log missing save report")


def check_docs_when_present() -> None:
    docs = [
        ROOT / "release" / "readiness" / "ghidra_cunit_render_distance_fade_wave545_2026-05-18.md",
        ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md",
        ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md",
        ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Unit.cpp" / "_index.md",
        ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "oids.cpp" / "_index.md",
    ]
    for path in docs:
        if not path.is_file():
            continue
        text = read_text(path)
        if "Wave545" not in text:
            continue
        require(NAME in text, f"{path} missing {NAME}")
        require(ADDRESS in text or RAW_ADDRESS in text, f"{path} missing {ADDRESS}")
        lowered = text.lower()
        for token in OVERCLAIM_TOKENS:
            require(token not in lowered, f"{path} contains overclaim token {token}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run Wave545 checks")
    args = parser.parse_args()
    if not args.check:
        parser.error("--check is required")

    check_metadata()
    check_tags()
    check_xrefs()
    check_decompile()
    check_caller_decompile()
    check_instruction_exports()
    check_logs()
    check_docs_when_present()
    print("Wave545 CUnit render distance-fade probe PASS: signature/comment/read-back evidence verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
