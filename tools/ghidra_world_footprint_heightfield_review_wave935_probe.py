#!/usr/bin/env python3
"""Validate Wave935 world-footprint/heightfield read-only review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave935-world-footprint-heightfield-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_world_footprint_heightfield_review_wave935_2026-05-28.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
WORLD_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "World.cpp" / "_index.md"
HEIGHT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "HeightField.cpp" / "_index.md"
PACKAGE_JSON = ROOT / "package.json"
STATE_FILES = [
    ROOT / "developer_agent_state.json",
    ROOT / "documentation_agent_state.json",
    ROOT / "re_orchestrator_state.json",
]

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260528-011246_post_wave935_world_footprint_heightfield_review_verified"
SCRIPT_NAME = "test:ghidra-world-footprint-heightfield-review-wave935"
SCRIPT_VALUE = r"py -3 tools\ghidra_world_footprint_heightfield_review_wave935_probe.py --check"

TARGETS = {
    "0x0047ea20": (
        "CHeightField__GetHeightSamplePacked16",
        "uint __fastcall CHeightField__GetHeightSamplePacked16(void * this, uint x_packed, uint z_packed)",
        ("+0x1028", "0x200", "0xa1ffe"),
        {"heightfield-wave394", "map-resource-wave426", "owner-corrected", "packed-height-sample"},
    ),
    "0x004bd5c0": (
        "CWorld__RasterizeFootprintIntoOccupancyBitplanes",
        "void __cdecl CWorld__RasterizeFootprintIntoOccupancyBitplanes(int min_world_x, int min_world_y, int max_world_x, int max_world_y, int skip_shadow_rebuild)",
        ("0..511", "CHeightField__GetHeightSamplePacked16", "CMonitor__SampleHeightfieldNormalAtXY", "CWorld__SetOrClearOccupancyBit", "CWorld__ClearCrossNeighborsInBitplane"),
        {"world-occupancy-wave457", "occupancy", "static-shadow", "world"},
    ),
}

CONTEXT = {
    "0x0047ec60": (
        "CMonitor__SampleHeightfieldNormalAtXY",
        "float * __fastcall CMonitor__SampleHeightfieldNormalAtXY(void * heightfield_or_monitor, void * out_normal, void * world_pos)",
        {"heightfield-wave394", "terrain-normal"},
    ),
    "0x004bdf70": (
        "CWorld__SetOrClearOccupancyBit",
        "void __thiscall CWorld__SetOrClearOccupancyBit(void * this, int world_x, int world_y, int set_flag)",
        {"world-occupancy-wave457", "bitplane", "occupancy"},
    ),
    "0x004bd440": (
        "CWorld__ClearCrossNeighborsInBitplane",
        "void __thiscall CWorld__ClearCrossNeighborsInBitplane(void * this, int world_x, int world_y)",
        {"world-occupancy-wave457", "bitplane", "occupancy"},
    ),
    "0x00490e30": (
        "CHeightField__BuildCellMinMaxHeightTable",
        "void __fastcall CHeightField__BuildCellMinMaxHeightTable(void * this)",
        {"map-resource-wave426", "minmax-table", "terrain-heightfield"},
    ),
    "0x004bcd60": (
        "CWorld__RebuildOccupancyGridFromDynamicSet",
        "void __cdecl CWorld__RebuildOccupancyGridFromDynamicSet(void)",
        {"world-occupancy-bitplanes-wave819", "dynamic-set", "occupancy"},
    ),
}

EXPECTED_XREFS = {
    ("0x0047ea20", "0x00490e79", "CHeightField__BuildCellMinMaxHeightTable", "UNCONDITIONAL_CALL"),
    ("0x0047ea20", "0x004bd007", "CWorld__RebuildOccupancyGridFromDynamicSet", "UNCONDITIONAL_CALL"),
    ("0x0047ea20", "0x004bd782", "CWorld__RasterizeFootprintIntoOccupancyBitplanes", "UNCONDITIONAL_CALL"),
    ("0x0047ea20", "0x0054500f", "CDXLandscape__BuildVertexBuffer", "UNCONDITIONAL_CALL"),
    ("0x004bd5c0", "0x004bc46b", "CWorld__RemoveUnitFromOccupancyGrid", "UNCONDITIONAL_CALL"),
    ("0x004bd5c0", "0x004bc4f3", "CWorld__AddUnitToOccupancyGridAndRebuildShadows", "UNCONDITIONAL_CALL"),
}

EXPECTED_CONTEXT_XREFS = {
    ("0x0047ec60", "0x004bd88d", "CWorld__RasterizeFootprintIntoOccupancyBitplanes", "UNCONDITIONAL_CALL"),
    ("0x004bdf70", "0x004bd7b7", "CWorld__RasterizeFootprintIntoOccupancyBitplanes", "UNCONDITIONAL_CALL"),
    ("0x004bd440", "0x004bd93a", "CWorld__RasterizeFootprintIntoOccupancyBitplanes", "UNCONDITIONAL_CALL"),
    ("0x00490e30", "0x0046d244", "CGame__PostLoadProcess", "UNCONDITIONAL_CALL"),
    ("0x004bcd60", "0x0050d47a", "CWorld__LoadWorld", "UNCONDITIONAL_CALL"),
}

EXPECTED_INSTRUCTIONS = {
    ("0x0047ea45", "MOV", "0x1028", "CHeightField__GetHeightSamplePacked16"),
    ("0x0047ea63", "RET", "0x4", "CHeightField__GetHeightSamplePacked16"),
    ("0x004bd782", "CALL", "0x0047ea20", "CWorld__RasterizeFootprintIntoOccupancyBitplanes"),
    ("0x004bd88d", "CALL", "0x0047ec60", "CWorld__RasterizeFootprintIntoOccupancyBitplanes"),
    ("0x004bd7b7", "CALL", "0x004bdf70", "CWorld__RasterizeFootprintIntoOccupancyBitplanes"),
    ("0x004bd93a", "CALL", "0x004bd440", "CWorld__RasterizeFootprintIntoOccupancyBitplanes"),
    ("0x004bd9d7", "RET", "", "CWorld__RasterizeFootprintIntoOccupancyBitplanes"),
}

DECOMPILE_TOKENS = {
    "decompile/0047ea20_CHeightField__GetHeightSamplePacked16.c": ("CHeightField__GetHeightSamplePacked16", "x_packed", "z_packed", "0x1028"),
    "decompile/004bd5c0_CWorld__RasterizeFootprintIntoOccupancyBitplanes.c": ("CWorld__RasterizeFootprintIntoOccupancyBitplanes", "CHeightField__GetHeightSamplePacked16", "CMonitor__SampleHeightfieldNormalAtXY", "CWorld__SetOrClearOccupancyBit", "CWorld__ClearCrossNeighborsInBitplane"),
    "context-decompile/0047ec60_CMonitor__SampleHeightfieldNormalAtXY.c": ("out_normal", "world_pos", "0x1028"),
    "context-decompile/004bdf70_CWorld__SetOrClearOccupancyBit.c": ("set_flag", "world_x", "world_y"),
    "context-decompile/004bd440_CWorld__ClearCrossNeighborsInBitplane.c": ("world_x", "world_y"),
    "context-decompile/00490e30_CHeightField__BuildCellMinMaxHeightTable.c": ("CHeightField__GetHeightSamplePacked16",),
    "context-decompile/004bcd60_CWorld__RebuildOccupancyGridFromDynamicSet.c": ("CWorld__SetOrClearOccupancyBit", "CWorld__ClearCrossNeighborsInBitplane"),
}

CORE_TOKENS = (
    "Wave935",
    "world-footprint-heightfield-review-wave935",
    "148/1408 = 10.51%",
    "6113/6113 = 100.00%",
    BACKUP,
    "0x0047ea20 CHeightField__GetHeightSamplePacked16",
    "0x004bd5c0 CWorld__RasterizeFootprintIntoOccupancyBitplanes",
    "0x0047ec60 CMonitor__SampleHeightfieldNormalAtXY",
    "0x004bdf70 CWorld__SetOrClearOccupancyBit",
    "0x004bd440 CWorld__ClearCrossNeighborsInBitplane",
    "0x00490e30 CHeightField__BuildCellMinMaxHeightTable",
    "0x004bcd60 CWorld__RebuildOccupancyGridFromDynamicSet",
    "no mutation",
)

OVERCLAIMS = (
    "runtime occupancy behavior proven",
    "runtime terrain behavior proven",
    "runtime pathing behavior proven",
    "fully reverse-engineered",
    "rebuild parity proven",
)


def normalize_address(value: str) -> str:
    text = value.strip().lower()
    if text.startswith("0x"):
        text = text[2:]
    return "0x" + text.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8-sig", errors="replace")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def check_counts_and_logs(failures: list[str]) -> None:
    expected_counts = {
        "metadata.tsv": 2,
        "tags.tsv": 2,
        "xrefs.tsv": 12,
        "instructions.tsv": 422,
        "decompile/index.tsv": 2,
        "context-metadata.tsv": 5,
        "context-tags.tsv": 5,
        "context-xrefs.tsv": 110,
        "context-instructions.tsv": 905,
        "context-decompile/index.tsv": 5,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    expected_logs = {
        "metadata.log": "targets=2 found=2 missing=0",
        "tags.log": "rows=2 missing=0",
        "xrefs.log": "Wrote 12 rows",
        "instructions.log": "Wrote 422 function-body instruction rows",
        "decompile.log": "targets=2 dumped=2 missing=0 failed=0",
        "context-metadata.log": "targets=5 found=5 missing=0",
        "context-tags.log": "rows=5 missing=0",
        "context-xrefs.log": "Wrote 110 rows",
        "context-instructions.log": "Wrote 905 function-body instruction rows",
        "context-decompile.log": "targets=5 dumped=5 missing=0 failed=0",
    }
    for relative, token in expected_logs.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_metadata_and_tags(failures: list[str]) -> None:
    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "tags.tsv")}
    context_metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "context-metadata.tsv")}
    context_tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "context-tags.tsv")}

    for address, (name, signature, comment_tokens, expected_tags) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in comment_tokens:
                require(token in row.get("comment", ""), f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual = set(tag_row.get("tags", "").split(";"))
            require(expected_tags.issubset(actual), f"tags missing at {address}: {expected_tags - actual}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

    for address, (name, signature, expected_tags) in CONTEXT.items():
        row = context_metadata.get(address)
        require(row is not None, f"missing context metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"context name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"context signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"context metadata status mismatch at {address}", failures)

        tag_row = context_tags.get(address)
        require(tag_row is not None, f"missing context tags for {address}", failures)
        if tag_row is not None:
            actual = set(tag_row.get("tags", "").split(";"))
            require(expected_tags.issubset(actual), f"context tags missing at {address}: {expected_tags - actual}", failures)
            require(tag_row.get("status") == "OK", f"context tag status mismatch at {address}", failures)


def check_xrefs_and_decompiles(failures: list[str]) -> None:
    xrefs = {
        (
            normalize_address(row["target_addr"]),
            normalize_address(row["from_addr"]),
            row.get("from_function", ""),
            row.get("ref_type", ""),
        )
        for row in read_tsv(BASE / "xrefs.tsv")
    }
    context_xrefs = {
        (
            normalize_address(row["target_addr"]),
            normalize_address(row["from_addr"]),
            row.get("from_function", ""),
            row.get("ref_type", ""),
        )
        for row in read_tsv(BASE / "context-xrefs.tsv")
    }
    instructions = {
        (
            normalize_address(row["instruction_addr"]),
            row.get("mnemonic", ""),
            row.get("operands", ""),
            row.get("function_name", ""),
        )
        for row in read_tsv(BASE / "instructions.tsv")
    }

    for expected in EXPECTED_XREFS:
        require(expected in xrefs, f"missing xref: {expected}", failures)
    for expected in EXPECTED_CONTEXT_XREFS:
        require(expected in context_xrefs, f"missing context xref: {expected}", failures)
    for addr, mnemonic, operand_token, function_name in EXPECTED_INSTRUCTIONS:
        found = any(
            row_addr == addr
            and row_mnemonic == mnemonic
            and function == function_name
            and (not operand_token or operand_token in operands)
            for row_addr, row_mnemonic, operands, function in instructions
        )
        require(found, f"missing instruction: {addr} {mnemonic} {operand_token} {function_name}", failures)

    for relative, tokens in DECOMPILE_TOKENS.items():
        text = read_text(BASE / relative)
        for token in tokens:
            require(token in text, f"missing decompile token in {relative}: {token}", failures)


def check_docs_and_state(failures: list[str]) -> None:
    for path in [NOTE, CAMPAIGN, WORLD_DOC, HEIGHT_DOC, *STATE_FILES]:
        text = read_text(path)
        for token in CORE_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = json.loads(read_text(PACKAGE_JSON))
    scripts = package.get("scripts", {})
    require(scripts.get(SCRIPT_NAME) == SCRIPT_VALUE, "missing package script", failures)


def check_backup(failures: list[str]) -> None:
    backup = json.loads(read_text(BASE / "backup-summary.json"))
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes", -1)) == 173247367, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_counts_and_logs(failures)
    check_metadata_and_tags(failures)
    check_xrefs_and_decompiles(failures)
    check_backup(failures)
    check_docs_and_state(failures)

    if failures:
        print("Wave935 world-footprint/heightfield probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave935 world-footprint/heightfield probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
