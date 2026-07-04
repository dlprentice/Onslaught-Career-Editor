#!/usr/bin/env python3
"""Validate Wave819 world occupancy-bitplane read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave819-world-occupancy-bitplanes"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_world_occupancy_bitplanes_wave819_2026-05-24.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
WORLD_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "World.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260524-164330_post_wave819_world_occupancy_bitplanes_verified"
NEXT_HEAD = "0x004bc2e0 CExplosionInitThing__ClearCostGridBoundsAndBuildPath"

TARGET_SIGNATURES = {
    "0x004bc2d0": "void __cdecl CWorld__ClearDynamicOccupancySet(void)",
    "0x004bc8d0": "void __cdecl CWorld__ClearOccupancyBitsUsingHeightBands(void)",
    "0x004bcbf0": "void __cdecl CWorld__ApplyStaticMaskToOccupancyBitplanes(void)",
    "0x004bcd60": "void __cdecl CWorld__RebuildOccupancyGridFromDynamicSet(void)",
    "0x004bdff0": "void __thiscall CWorld__SkipLegacyOccupancyChunk(void * this, void * mem_buffer)",
    "0x004be170": "void __cdecl CWorld__ReadOccupancyChunkHeader(void * mem_buffer)",
}

TARGET_NAMES = {
    "0x004bc2d0": "CWorld__ClearDynamicOccupancySet",
    "0x004bc8d0": "CWorld__ClearOccupancyBitsUsingHeightBands",
    "0x004bcbf0": "CWorld__ApplyStaticMaskToOccupancyBitplanes",
    "0x004bcd60": "CWorld__RebuildOccupancyGridFromDynamicSet",
    "0x004bdff0": "CWorld__SkipLegacyOccupancyChunk",
    "0x004be170": "CWorld__ReadOccupancyChunkHeader",
}

TARGET_XREFS = {
    "0x004bc2d0": "0x0050d683",
    "0x004bc8d0": "0x0050d456",
    "0x004bcbf0": "0x0050d473",
    "0x004bcd60": "0x0050d47a",
    "0x004bdff0": "0x0050d331",
    "0x004be170": "0x0050d386",
}

COMMENT_TOKENS = {
    "0x004bc2d0": ("Wave819 static read-back", "DAT_00809588", "CSPtrSet__Clear", "0x0050d683"),
    "0x004bc8d0": ("Wave819 static read-back", "0x0050d456", "CHeightField__GetHeightSamplePacked16", "DAT_00855290"),
    "0x004bcbf0": ("Wave819 static read-back", "0x0050d473", "DAT_00807580", "DAT_00809598"),
    "0x004bcd60": ("Wave819 static read-back", "0x0050d47a", "CSPtrSet__First", "CWorld__ClearCrossNeighborsInBitplane"),
    "0x004bdff0": ("Wave819 static read-back", "0x0050d331", "RET 0x4", "0x8000", "0x2000"),
    "0x004be170": ("Wave819 static read-back", "0x0050d386", "ADD ESP, 0x4", "five 4-byte fields"),
}

COMMON_TAGS = {
    "static-reaudit",
    "world-occupancy-bitplanes-wave819",
    "wave819-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
}

HELPER_NAMES = {
    "CSPtrSet__Clear",
    "CHeightField__GetHeightSamplePacked16",
    "CMonitor__SampleHeightfieldNormalAtXY",
    "CWorld__SetOrClearOccupancyBit",
    "CWorld__ClearCrossNeighborsInBitplane",
    "CSPtrSet__First",
    "CSPtrSet__Next",
    "CDXMemBuffer__Read",
}

CORE_ANCHORS = (
    "Wave819 world occupancy bitplanes",
    "world-occupancy-bitplanes-wave819",
    "0x004bc2d0 CWorld__ClearDynamicOccupancySet",
    "0x004bc8d0 CWorld__ClearOccupancyBitsUsingHeightBands",
    "0x004bcbf0 CWorld__ApplyStaticMaskToOccupancyBitplanes",
    "0x004bcd60 CWorld__RebuildOccupancyGridFromDynamicSet",
    "0x004bdff0 CWorld__SkipLegacyOccupancyChunk",
    "0x004be170 CWorld__ReadOccupancyChunkHeader",
    "DAT_00855290",
    "DAT_00855294",
    "DAT_00855298",
    "5612/6098 = 92.03%",
    NEXT_HEAD,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime pathing behavior proven",
    "runtime world-load behavior proven",
    "fully reverse-engineered",
    "rebuild parity proven",
)


def normalize_address(address: str) -> str:
    value = address.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in read_text(path).splitlines() if line.strip()]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def signature_counts(rows: list[dict[str, str]]) -> tuple[int, int]:
    commented = sum(1 for row in rows if row.get("comment", "").strip())
    strict_clean = sum(
        1
        for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not re.search(r"\bparam_\d+\b", row.get("signature", ""))
    )
    return commented, strict_clean


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 6,
        "pre-tags.tsv": 6,
        "pre-xrefs.tsv": 8,
        "pre-instructions.tsv": 1326,
        "pre-callsite-instructions.tsv": 204,
        "pre-helper-metadata.tsv": 8,
        "pre-decompile/index.tsv": 6,
        "post-metadata.tsv": 6,
        "post-tags.tsv": 6,
        "post-xrefs.tsv": 8,
        "post-instructions.tsv": 1326,
        "post-callsite-instructions.tsv": 204,
        "post-helper-metadata.tsv": 8,
        "post-decompile/index.tsv": 6,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs = {}
    for row in read_tsv(BASE / "post-xrefs.tsv"):
        xrefs.setdefault(normalize_address(row["target_addr"]), []).append(row)
    helpers = {row["name"] for row in read_tsv(BASE / "post-helper-metadata.tsv")}

    for address, signature in TARGET_SIGNATURES.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row:
            require(row.get("name") == TARGET_NAMES[address], f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in COMMENT_TOKENS[address]:
                require(token in row.get("comment", ""), f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"tags missing at {address}: {COMMON_TAGS - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        require(address in xrefs, f"missing xrefs for {address}", failures)
        if address in xrefs:
            require(
                any(normalize_address(row.get("from_addr", "")) == TARGET_XREFS[address] for row in xrefs[address]),
                f"missing expected xref for {address}: {TARGET_XREFS[address]}",
                failures,
            )

    require(HELPER_NAMES.issubset(helpers), f"missing helper metadata: {HELPER_NAMES - helpers}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=6 comment_only_updated=6 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=6 skipped=0 renamed=0 would_rename=0 signature_updated=6 comment_only_updated=6 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=6 found=6 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=6 missing=0",
        "post-xrefs.log": "Wrote 8 rows",
        "post-instructions.log": "Wrote 1326 instruction rows",
        "post-callsite-instructions.log": "Wrote 204 instruction rows",
        "post-helper-metadata.log": "targets=8 found=8 missing=0",
        "post-decompile.log": "targets=6 dumped=6 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6098 commented_functions=5612",
        "queue-probe.log": "Commentless functions: 486",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave819.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave819_queue_probe.log",
    }
    for relative, token in expected.items():
        path = log_aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)
    require("REPORT: Save succeeded" in read_text(BASE / "apply.log"), "missing apply save success", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 486, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5612, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5612, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x004bc2e0", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CExplosionInitThing__ClearCostGridBoundsAndBuildPath", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 171412359 or backup.get("totalBytes") == 171412359.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = [
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        WORLD_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in CORE_ANCHORS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-world-occupancy-bitplanes-wave819")
        == r"py -3 tools\ghidra_world_occupancy_bitplanes_wave819_probe.py --check",
        "missing package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave819 world occupancy bitplanes" for row in ledger_rows), "missing Wave819 ledger row", failures)
    require(
        any(row.get("task") == "Wave819 world occupancy bitplanes" and row.get("attempt_id") == 20474 for row in attempts),
        "missing Wave819 attempt row",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs(failures)
    check_queue_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave819 world occupancy bitplanes probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave819 world occupancy bitplanes probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
