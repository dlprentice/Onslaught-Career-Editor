#!/usr/bin/env python3
"""Validate Wave551 CVertexShader VSDS deserialize Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave551-resource-accumulator-shaders-005042f0"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_resource_accumulator_shaders_wave551_2026-05-18.md"
GHIDRA_REF = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
STATIC_CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
VERTEX_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "VertexShader.cpp" / "_index.md"
RESOURCE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "ResourceAccumulator.cpp" / "_index.md"

TARGET = "0x005042f0"
RAW = "005042f0"
NAME = "CVertexShader__DeserializeAll"
SIGNATURE = "void __cdecl CVertexShader__DeserializeAll(void * chunk_reader)"
COMMON_TAGS = {
    "comment-hardened",
    "cvertexshader",
    "deserialize",
    "name-corrected",
    "owner-corrected",
    "resource-accumulator-shaders-wave551",
    "resource-load",
    "retail-binary-evidence",
    "signature-corrected",
    "static-reaudit",
    "vsds",
}
COMMENT_TOKENS = (
    "CResourceAccumulator__ReadResourceFile dispatches the VSDS chunk",
    "CVertexShader::DeserializeAll(&c)",
    "DAT_00854e74",
    "0x00634070",
    "0x00634074..0x00634554",
    "CVertexShader__Clone(chunk_reader, shader_index)",
    "Static retail evidence only",
    "platform-guard differences from source",
)
DECOMPILE_TOKENS = (
    "void __cdecl CVertexShader__DeserializeAll(void *chunk_reader)",
    "CChunkReader__Read(chunk_reader,&local_4,4,1)",
    "DAT_00634070",
    "PTR_s_f_create_eyespace_vertex_00634074",
    "DAT_00854e74",
    "CVertexShader__Clone(this,shader_index)",
)
INSTRUCTION_TOKENS = (
    ("0x005042f3", "MOV", "[ESP + 0x10]"),
    ("0x00504302", "CALL", "0x00423960"),
    ("0x00504319", "PUSH", "0x4e0"),
    ("0x0050431e", "PUSH", "0x634070"),
    ("0x0050432a", "MOV", "0x634074"),
    ("0x00504338", "CMP", "0x634554"),
    ("0x00504349", "MOV", "0x00854e74"),
    ("0x00504355", "CALL", "0x00503f90"),
    ("0x00504369", "RET", ""),
)
CALLER_TOKENS = (
    "0x004d7775",
    "PUSH\tESI",
    "0x004d7776",
    "CALL\t0x005042f0",
    "0x004d777b",
    "ADD\tESP, 0x4",
)
DOC_TOKENS = {
    PUBLIC_NOTE: ("Wave551", NAME, "VSDS", "updated=1", "renamed=1", "runtime shader behavior"),
    GHIDRA_REF: ("Wave551", NAME, "2608/6089 = 42.83%"),
    STATIC_CAMPAIGN: ("Wave 551: CVertexShader VSDS Deserialize", "updated=1", "strict comment-plus-clean-signature proxy"),
    VERTEX_DOC: ("Wave551", NAME, "0x00634070"),
    RESOURCE_DOC: ("Wave551", NAME, "VSDS"),
}
OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "source identity proven",
    "rebuild parity proven",
    "fully recovered",
    "complete shader system",
    "concrete layout proven",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_text(path: Path) -> str:
    require(path.exists(), f"missing file: {path}")
    return path.read_text(encoding="utf-8", errors="replace")


def read_tsv(path: Path) -> list[dict[str, str]]:
    require(path.exists(), f"missing file: {path}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def compact(value: str) -> str:
    return "".join(" ".join((value or "").replace("`", "").split()).lower().split())


def token_present(text: str, token: str) -> bool:
    return compact(token) in compact(text)


def parse_summary(path: Path) -> dict[str, int]:
    text = read_text(path)
    match = re.search(
        r"SUMMARY: mode=(dry|apply) updated=(\d+) skipped=(\d+) renamed=(\d+) would_rename=(\d+) missing=(\d+) bad=(\d+)",
        text,
    )
    require(match is not None, f"missing summary in {path}")
    keys = ("updated", "skipped", "renamed", "would_rename", "missing", "bad")
    return {key: int(value) for key, value in zip(keys, match.groups()[1:])}


def check_logs() -> None:
    dry = parse_summary(BASE / "wave551_dry.log")
    apply = parse_summary(BASE / "wave551_apply.log")
    verify = parse_summary(BASE / "wave551_verify_dry.log")
    require(dry == {"updated": 0, "skipped": 1, "renamed": 0, "would_rename": 1, "missing": 0, "bad": 0}, f"dry summary mismatch {dry}")
    require(apply == {"updated": 1, "skipped": 0, "renamed": 1, "would_rename": 0, "missing": 0, "bad": 0}, f"apply summary mismatch {apply}")
    require(verify == {"updated": 0, "skipped": 1, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}, f"verify summary mismatch {verify}")
    for path in (BASE / "wave551_dry.log", BASE / "wave551_apply.log", BASE / "wave551_verify_dry.log"):
        text = read_text(path)
        require("REPORT: Save succeeded" in text, f"{path.name} missing save success")
        for bad in ("LockException", "MISSING:", "BADADDR:", "FAIL:"):
            require(bad not in text, f"{path.name} contains {bad}")


def check_metadata() -> None:
    rows = read_tsv(BASE / "post_metadata.tsv")
    require(len(rows) == 1, f"expected 1 metadata row, got {len(rows)}")
    row = rows[0]
    require(row["address"].lower() == TARGET, f"metadata address mismatch {row['address']}")
    require(row["name"] == NAME, f"metadata name mismatch {row['name']}")
    require(row["signature"] == SIGNATURE, f"signature mismatch {row['signature']}")
    require(row["status"] == "OK", f"metadata status mismatch {row['status']}")
    for token in COMMENT_TOKENS:
        require(token_present(row["comment"], token), f"comment missing {token!r}")
    lowered = row["comment"].lower()
    for token in OVERCLAIM_TOKENS:
        require(token not in lowered, f"comment contains overclaim token {token}")


def check_tags() -> None:
    rows = read_tsv(BASE / "post_tags.tsv")
    require(len(rows) == 1, f"expected 1 tag row, got {len(rows)}")
    row = rows[0]
    require(row["address"].lower() == RAW, f"tag address mismatch {row['address']}")
    tags = set(filter(None, row["tags"].split(";")))
    require(COMMON_TAGS.issubset(tags), f"missing tags {sorted(COMMON_TAGS - tags)}")


def check_xrefs() -> None:
    rows = read_tsv(BASE / "post_xrefs.tsv")
    require(len(rows) == 1, f"expected 1 xref row, got {len(rows)}")
    row = rows[0]
    require(row["target_addr"].lower() == RAW, f"xref target mismatch {row['target_addr']}")
    require(row["target_name"] == NAME, f"xref target name mismatch {row['target_name']}")
    require(row["from_addr"].lower() == "004d7776", f"xref from mismatch {row['from_addr']}")
    require(row["from_function"] == "CResourceAccumulator__ReadResourceFile", f"xref function mismatch {row['from_function']}")
    require(row["ref_type"] == "UNCONDITIONAL_CALL", f"xref type mismatch {row['ref_type']}")


def check_decompile() -> None:
    matches = list((BASE / "post_decomp").glob(f"{RAW}_*.c"))
    require(len(matches) == 1, f"expected one decompile export, got {len(matches)}")
    require(NAME in matches[0].name, f"decompile filename does not include {NAME}")
    text = read_text(matches[0])
    for token in DECOMPILE_TOKENS:
        require(token_present(text, token), f"decompile missing {token!r}")
    caller = read_text(BASE / "post_caller_decomp" / "004d7200_CResourceAccumulator__ReadResourceFile.c")
    require(token_present(caller, "CVertexShader__DeserializeAll(pcVar6);"), "caller decompile missing renamed call")


def check_instructions() -> None:
    rows = read_tsv(BASE / "post_instructions.tsv")
    require(len(rows) == 181, f"expected 181 target instruction rows, got {len(rows)}")
    haystack = "\n".join("\t".join(row.values()) for row in rows)
    for addr, mnemonic, operand in INSTRUCTION_TOKENS:
        require(addr.lower() in haystack.lower() and mnemonic in haystack and operand.lower() in haystack.lower(),
                f"instruction token missing {(addr, mnemonic, operand)}")

    caller_rows = read_tsv(BASE / "post_caller_instructions.tsv")
    require(len(caller_rows) == 621, f"expected 621 caller instruction rows, got {len(caller_rows)}")
    caller_text = "\n".join("\t".join(row.values()) for row in caller_rows)
    for token in CALLER_TOKENS:
        require(token_present(caller_text, token), f"caller instruction export missing {token}")


def check_docs() -> None:
    for path, tokens in DOC_TOKENS.items():
        text = read_text(path)
        for token in tokens:
            require(token_present(text, token), f"{path}: missing token {token}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.check:
        parser.error("expected --check")

    check_logs()
    check_metadata()
    check_tags()
    check_xrefs()
    check_decompile()
    check_instructions()
    check_docs()
    print("Wave551 resource-accumulator shader deserialize probe PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
