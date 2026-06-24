#!/usr/bin/env python3
"""Validate Wave544 TerrainGuide constructor Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave544-cterrainguide-ctor-004f1ec0"
ADDRESS = "0x004f1ec0"
RAW_ADDRESS = "004f1ec0"
OLD_NAME = "CTerrainGuide__ctor_like_004f1ec0"
NAME = "CTerrainGuide__ctor"
SIGNATURE = f"void * __thiscall {NAME}(void * this, void * guideOwner)"
COMMON_TAGS = {
    "static-reaudit",
    "terrain-guide-wave544",
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


def parse_comment_summary(path: Path) -> dict[str, int]:
    text = read_text(path)
    match = re.search(r"SUMMARY updated=(\d+) skipped=(\d+) missing=(\d+) bad=(\d+)", text)
    require(match is not None, f"missing comment summary in {path}")
    keys = ("updated", "skipped", "missing", "bad")
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
        "0x20-byte guide object",
        "RET 0x4 proves one owner/guideOwner stack argument",
        "CGuide__ctor_base",
        "vtable 0x005df4ec",
        "GillM, WarspiteDome, Cannon, and Sentinel",
        "owner+0x208",
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
        (RAW_ADDRESS, NAME, "00479cf1", "00479cb0", "CGillM__InitTerrainGuideComponent", "UNCONDITIONAL_CALL"),
        (RAW_ADDRESS, NAME, "00504857", "005047e0", "CWarspiteDome__Init", "UNCONDITIONAL_CALL"),
        (RAW_ADDRESS, NAME, "0041b24b", "0041b1a0", "CCannon__Init", "UNCONDITIONAL_CALL"),
        (RAW_ADDRESS, NAME, "004deb44", "004dea50", "CSentinel__Init", "UNCONDITIONAL_CALL"),
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
        "void * __thiscall CTerrainGuide__ctor(void *this,void *guideOwner)",
        "CGuide__ctor_base(this,guideOwner)",
        "PTR_SharedVFunc__NoOpOneArg_004014c0_005df4ec",
        "return this",
    ):
        require(token_present(text, token), f"decompile missing {token!r}")
    require(OLD_NAME not in text, "decompile still contains old function name")
    lowered = text.lower()
    for token in OVERCLAIM_TOKENS:
        require(token not in lowered, f"decompile contains overclaim token {token}")


def check_instruction_exports() -> None:
    rows = read_tsv(BASE / "post_instructions.tsv")
    require(len(rows) == 225, f"instruction row count {len(rows)}")
    body = {(raw_address(row["instruction_addr"]), row["mnemonic"], row["operands"]) for row in rows}
    for item in (
        ("004f1ec0", "MOV", "EAX, dword ptr [ESP + 0x4]"),
        ("004f1ec7", "PUSH", "EAX"),
        ("004f1ec8", "CALL", "0x0047e290"),
        ("004f1ecd", "MOV", "dword ptr [ESI], 0x5df4ec"),
        ("004f1ed3", "MOV", "EAX, ESI"),
        ("004f1ed6", "RET", "0x4"),
    ):
        require(item in body, f"instruction export missing {item}")


def check_caller_decompile() -> None:
    index = read_tsv(BASE / "post_caller_decomp" / "index.tsv")
    require(len(index) == 4, f"caller decompile index row count {len(index)}")
    require(all(row["status"] == "OK" for row in index), "caller decompile status not all OK")
    combined = "\n".join(path.read_text(encoding="utf-8") for path in (BASE / "post_caller_decomp").glob("*.c"))
    for token in (
        "CGillM__InitTerrainGuideComponent",
        "CWarspiteDome__Init",
        "CCannon__Init",
        "CSentinel__Init",
        "CTerrainGuide__ctor",
        "0x208",
    ):
        require(token_present(combined, token), f"caller decompile missing {token!r}")
    require(OLD_NAME not in combined, "caller decompile still contains old function name")


def check_vtable() -> None:
    rows = read_tsv(BASE / "post_vtable.tsv")
    require(len(rows) == 8, f"vtable row count {len(rows)}")
    by_slot = {row["slot_index"]: row for row in rows}
    require(by_slot["0"]["function_name"] == "SharedVFunc__NoOpOneArg_004014c0", "slot 0 mismatch")
    require(by_slot["2"]["function_name"] == "CMonitor__Shutdown_Core", "slot 2 mismatch")
    require(by_slot["3"]["pointer_addr"] == "004f1ee0", "slot 3 pointer mismatch")


def check_logs() -> None:
    require(
        parse_summary(BASE / "apply_terrain_guide_ctor_wave544_apply.log")
        == {"updated": 1, "skipped": 0, "renamed": 1, "would_rename": 0, "missing": 0, "bad": 0},
        "apply summary mismatch",
    )
    require(
        parse_summary(BASE / "apply_terrain_guide_ctor_wave544_verify_dry.log")
        == {"updated": 0, "skipped": 1, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        "verify dry summary mismatch",
    )
    require("REPORT: Save succeeded" in read_text(BASE / "apply_terrain_guide_ctor_wave544_apply.log"), "apply log missing save report")
    require(
        parse_comment_summary(BASE / "apply_terrain_guide_caller_comment_wave544_apply.log")
        == {"updated": 1, "skipped": 0, "missing": 0, "bad": 0},
        "caller comment apply summary mismatch",
    )
    require(
        parse_comment_summary(BASE / "apply_terrain_guide_caller_comment_wave544_verify_dry.log")
        == {"updated": 0, "skipped": 1, "missing": 0, "bad": 0},
        "caller comment verify dry summary mismatch",
    )
    require(
        "REPORT: Save succeeded" in read_text(BASE / "apply_terrain_guide_caller_comment_wave544_apply.log"),
        "caller comment apply log missing save report",
    )


def check_docs_when_present() -> None:
    docs = [
        ROOT / "release" / "readiness" / "ghidra_terrain_guide_ctor_wave544_2026-05-18.md",
        ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md",
        ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md",
        ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Guide.cpp" / "_index.md",
    ]
    for path in docs:
        if not path.is_file():
            continue
        text = read_text(path)
        if "Wave544" not in text:
            continue
        require(NAME in text, f"{path} missing {NAME}")
        require(ADDRESS in text or RAW_ADDRESS in text, f"{path} missing {ADDRESS}")
        lowered = text.lower()
        for token in OVERCLAIM_TOKENS:
            require(token not in lowered, f"{path} contains overclaim token {token}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run Wave544 checks")
    args = parser.parse_args()
    if not args.check:
        parser.error("--check is required")

    check_metadata()
    check_tags()
    check_xrefs()
    check_decompile()
    check_instruction_exports()
    check_caller_decompile()
    check_vtable()
    check_logs()
    check_docs_when_present()
    print("Wave544 TerrainGuide constructor probe PASS: name/signature/comment/read-back evidence verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
