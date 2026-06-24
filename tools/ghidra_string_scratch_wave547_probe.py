#!/usr/bin/env python3
"""Validate Wave547 string scratch Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave547-string-temp-buffers-004f7c70"
SPECS = {
    "0x004f7c70": {
        "raw": "004f7c70",
        "name": "StringScratch__CopyToRotating4KBufferA",
        "signature": "char * __cdecl StringScratch__CopyToRotating4KBufferA(char * source_string)",
        "counter": "0x00854d44",
        "buffer": "0x00848d40",
        "xref_tokens": ("PCPlatform__LoadFonts", "CD3DApplication__Create", "CWaveSoundRead__Open", "CDXTexture__LoadTextureFromFile_Core"),
    },
    "0x004f7cd0": {
        "raw": "004f7cd0",
        "name": "StringScratch__CopyToRotating4KBufferB",
        "signature": "char * __cdecl StringScratch__CopyToRotating4KBufferB(char * source_string)",
        "counter": "0x00854d48",
        "buffer": "0x00844d40",
        "xref_tokens": ("CDXBitmapFont__InitNamedFontSlot", "CFEPDevelopment__EnumerateWorldFiles"),
    },
}
COMMON_TAGS = {
    "static-reaudit",
    "string-scratch-wave547",
    "retail-binary-evidence",
    "name-corrected",
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
    if value.startswith("0x"):
        value = value[2:]
    return value.zfill(8)


def normalize_address(value: str) -> str:
    return "0x" + raw_address(value)


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
    rows = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post_metadata.tsv")}
    require(set(rows) == set(SPECS), f"metadata addresses mismatch {sorted(rows)}")
    for address, spec in SPECS.items():
        row = rows[address]
        require(row["name"] == spec["name"], f"{address} metadata name mismatch {row['name']}")
        require(row["signature"] == spec["signature"], f"{address} signature mismatch {row['signature']}")
        require(row["status"] == "OK", f"{address} metadata status {row['status']}")
        for token in ("source_string", spec["counter"], spec["buffer"], "slot*0x1000", "Static retail evidence only"):
            require(token_present(row["comment"], token), f"{address} comment missing {token!r}")
        lowered = row["comment"].lower()
        for token in OVERCLAIM_TOKENS:
            require(token not in lowered, f"{address} comment contains overclaim token {token}")


def check_tags() -> None:
    rows = {raw_address(row["address"]): row for row in read_tsv(BASE / "post_tags.tsv")}
    for spec in SPECS.values():
        row = rows.get(spec["raw"])
        require(row is not None, f"missing tag row for {spec['raw']}")
        tags = set(filter(None, row["tags"].split(";")))
        require(COMMON_TAGS.issubset(tags), f"{spec['raw']} missing tags {sorted(COMMON_TAGS - tags)}")


def check_xrefs() -> None:
    rows = read_tsv(BASE / "post_xrefs.tsv")
    require(len(rows) == 25, f"xref row count {len(rows)}")
    by_target: dict[str, list[dict[str, str]]] = {spec["raw"]: [] for spec in SPECS.values()}
    for row in rows:
        target = raw_address(row["target_addr"])
        if target in by_target:
            by_target[target].append(row)
    require(len(by_target["004f7c70"]) == 23, "BufferA xref count mismatch")
    require(len(by_target["004f7cd0"]) == 2, "BufferB xref count mismatch")
    for spec in SPECS.values():
        xref_text = "\n".join(row["from_function"] for row in by_target[spec["raw"]])
        for token in spec["xref_tokens"]:
            require(token_present(xref_text, token), f"{spec['raw']} xrefs missing {token!r}")


def check_decompile() -> None:
    index = read_tsv(BASE / "post_decomp" / "index.tsv")
    require(len(index) == 2, f"decompile index row count {len(index)}")
    require(all(row["status"] == "OK" for row in index), "decompile index has non-OK row")
    for spec in SPECS.values():
        text = read_text(BASE / "post_decomp" / f"{spec['raw']}_{spec['name']}.c")
        for token in (
            f"/* name: {spec['name']} */",
            f"/* signature: {spec['signature']} */",
            f"char * __cdecl {spec['name']}(char *source_string)",
            f"DAT_{spec['counter'][2:]}",
            f"DAT_{spec['buffer'][2:]}",
            "return &DAT_",
        ):
            require(token_present(text, token), f"{spec['raw']} decompile missing {token!r}")
        require(not token_present(text, "param_1"), f"{spec['raw']} decompile still contains stale param_1")
        lowered = text.lower()
        for token in OVERCLAIM_TOKENS:
            require(token not in lowered, f"{spec['raw']} decompile contains overclaim token {token}")


def check_instruction_exports() -> None:
    rows = read_tsv(BASE / "post_instructions.tsv")
    require(len(rows) == 562, f"instruction row count {len(rows)}")
    body = {(raw_address(row["instruction_addr"]), row["mnemonic"], row["operands"]) for row in rows}
    for item in (
        ("004f7c70", "PUSH", "EBP"),
        ("004f7c7e", "MOV", "EDX, dword ptr [0x00854d44]"),
        ("004f7c84", "SCASB.REPNE", "ES:EDI"),
        ("004f7caa", "LEA", "EDI, [ECX + 0x848d40]"),
        ("004f7cd0", "PUSH", "EBP"),
        ("004f7cde", "MOV", "EDX, dword ptr [0x00854d48]"),
        ("004f7ce4", "SCASB.REPNE", "ES:EDI"),
        ("004f7d0a", "LEA", "EDI, [ECX + 0x844d40]"),
    ):
        require(item in body, f"instruction export missing {item}")


def check_logs() -> None:
    require(
        parse_summary(BASE / "apply_string_scratch_wave547_apply.log")
        == {"updated": 2, "skipped": 0, "renamed": 2, "would_rename": 0, "missing": 0, "bad": 0},
        "apply summary mismatch",
    )
    require(
        parse_summary(BASE / "apply_string_scratch_wave547_verify_dry.log")
        == {"updated": 0, "skipped": 2, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        "verify dry summary mismatch",
    )
    require("REPORT: Save succeeded" in read_text(BASE / "apply_string_scratch_wave547_apply.log"), "apply log missing save report")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run Wave547 checks")
    args = parser.parse_args()
    if not args.check:
        parser.error("--check is required")

    check_metadata()
    check_tags()
    check_xrefs()
    check_decompile()
    check_instruction_exports()
    check_logs()
    print("Wave547 string scratch probe PASS: name/signature/comment/read-back evidence verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
