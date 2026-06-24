#!/usr/bin/env python3
"""Validate Wave820 explosion path cost-grid read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave820-explosion-path-cost-grid"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_explosion_path_cost_grid_wave820_2026-05-24.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
GUIDE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Guide.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260524-171120_post_wave820_explosion_path_cost_grid_verified"
NEXT_HEAD = "0x004c0c70 CPDSimpleSprite__EvalExpressionNode"

TARGET_SIGNATURES = {
    "0x004bc2e0": "int __thiscall CExplosionInitThing__ClearCostGridBoundsAndBuildPath(void * this, float start_x, float start_y, float start_z_lane, float start_w_lane, float goal_x, float goal_y, float goal_z_lane, float goal_w_lane, int search_flags, void * path_state)",
    "0x004be1d0": "int __cdecl CExplosionInitThing__BuildGridPathWithFallbackSearch(float start_x, float start_y, float start_z_lane, float start_w_lane, float goal_x, float goal_y, float goal_z_lane, float goal_w_lane, void * bitplane_base, int search_flags, void * path_state)",
    "0x004be420": "int __cdecl CExplosionInitThing__SelectNextPathStepDirection(void)",
    "0x004be9b0": "int __cdecl CExplosionInitThing__CanStepNorthFromCurrent(void)",
    "0x004bea10": "int __cdecl CExplosionInitThing__CanStepWestFromCurrent(void)",
    "0x004bea70": "int __cdecl CExplosionInitThing__CanStepSouthFromCurrent(void)",
    "0x004bead0": "int __cdecl CExplosionInitThing__CanStepEastFromCurrent(void)",
    "0x004beb30": "void __cdecl CExplosionInitThing__FindNearestVisitedGridCell(void)",
}

TARGET_NAMES = {
    "0x004bc2e0": "CExplosionInitThing__ClearCostGridBoundsAndBuildPath",
    "0x004be1d0": "CExplosionInitThing__BuildGridPathWithFallbackSearch",
    "0x004be420": "CExplosionInitThing__SelectNextPathStepDirection",
    "0x004be9b0": "CExplosionInitThing__CanStepNorthFromCurrent",
    "0x004bea10": "CExplosionInitThing__CanStepWestFromCurrent",
    "0x004bea70": "CExplosionInitThing__CanStepSouthFromCurrent",
    "0x004bead0": "CExplosionInitThing__CanStepEastFromCurrent",
    "0x004beb30": "CExplosionInitThing__FindNearestVisitedGridCell",
}

TARGET_XREFS = {
    "0x004bc2e0": {"0x004a0eab", "0x0047d9c1", "0x0048a880", "0x004e7696"},
    "0x004be1d0": {"0x004bc3c7"},
    "0x004be420": {"0x004be337"},
    "0x004be9b0": {"0x004be711", "0x004be759", "0x004be792", "0x004be7d4", "0x004be804"},
    "0x004bea10": {"0x004be6fe", "0x004be737", "0x004be814"},
    "0x004bea70": {"0x004be76c", "0x004be77f", "0x004be7e4", "0x004be7f4"},
    "0x004bead0": {"0x004be6d8", "0x004be6eb", "0x004be7a5", "0x004be7b5"},
    "0x004beb30": {"0x004be340"},
}

COMMENT_TOKENS = {
    "0x004bc2e0": ("Wave820 static read-back", "RET 0x28", "DAT_00809dc0", "CExplosionInitThing__BuildGridPathWithFallbackSearch"),
    "0x004be1d0": ("Wave820 static read-back", "0x2c stack bytes", "DAT_00809db8", "CExplosionInitThing__StepToLowestCostNeighbor8"),
    "0x004be420": ("Wave820 static read-back", "DAT_00829dc0", "DAT_00809dbc", "PTR_LAB_004be94c"),
    "0x004be9b0": ("Wave820 static read-back", "row above", "DAT_00809db8"),
    "0x004bea10": ("Wave820 static read-back", "column left", "DAT_00809db8"),
    "0x004bea70": ("Wave820 static read-back", "row below", "DAT_00809db8"),
    "0x004bead0": ("Wave820 static read-back", "column right", "DAT_00809db8"),
    "0x004beb30": ("Wave820 static read-back", "expanding rings", "DAT_00809dc0"),
}

COMMON_TAGS = {
    "static-reaudit",
    "explosion-path-cost-grid-wave820",
    "wave820-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
}

HELPER_NAMES = {
    "CExplosionInitThing__IsGridSegmentBlocked",
    "CExplosionInitThing__FindNearestSetBitInOccupancyGrid",
    "CExplosionInitThing__TestBitAtGridCoordPacked",
    "CExplosionInitThing__StepToLowestCostNeighbor8",
    "CExplosionInitThing__SimplifyGridPathByLineOfSight",
    "CWorld__ClearDynamicOccupancySet",
    "CWorld__ClearOccupancyBitsUsingHeightBands",
    "CWorld__ApplyStaticMaskToOccupancyBitplanes",
    "CWorld__RebuildOccupancyGridFromDynamicSet",
}

CORE_ANCHORS = (
    "Wave820 explosion path cost grid",
    "explosion-path-cost-grid-wave820",
    "0x004bc2e0 CExplosionInitThing__ClearCostGridBoundsAndBuildPath",
    "0x004be1d0 CExplosionInitThing__BuildGridPathWithFallbackSearch",
    "0x004be420 CExplosionInitThing__SelectNextPathStepDirection",
    "0x004be9b0 CExplosionInitThing__CanStepNorthFromCurrent",
    "0x004bea10 CExplosionInitThing__CanStepWestFromCurrent",
    "0x004bea70 CExplosionInitThing__CanStepSouthFromCurrent",
    "0x004bead0 CExplosionInitThing__CanStepEastFromCurrent",
    "0x004beb30 CExplosionInitThing__FindNearestVisitedGridCell",
    "DAT_00809dc0",
    "DAT_00809db8",
    "5620/6098 = 92.16%",
    NEXT_HEAD,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime guidance/pathing behavior proven",
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


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in read_text(path).splitlines() if line.strip()]


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
        "pre-metadata.tsv": 8,
        "pre-tags.tsv": 8,
        "pre-xrefs.tsv": 23,
        "pre-instructions.tsv": 2088,
        "pre-helper-metadata.tsv": 9,
        "pre-helper-instructions.tsv": 729,
        "pre-entry-callsite-instructions.tsv": 371,
        "pre-decompile/index.tsv": 8,
        "post-metadata.tsv": 8,
        "post-tags.tsv": 8,
        "post-xrefs.tsv": 23,
        "post-instructions.tsv": 2088,
        "post-helper-metadata.tsv": 9,
        "post-helper-instructions.tsv": 729,
        "post-entry-callsite-instructions.tsv": 371,
        "post-decompile/index.tsv": 8,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs: dict[str, set[str]] = {}
    for row in read_tsv(BASE / "post-xrefs.tsv"):
        xrefs.setdefault(normalize_address(row["target_addr"]), set()).add(normalize_address(row["from_addr"]))

    for address, name in TARGET_NAMES.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            comment = row.get("comment", "")
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == TARGET_SIGNATURES[address], f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in COMMENT_TOKENS[address]:
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"tags missing at {address}: {COMMON_TAGS - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == TARGET_SIGNATURES[address], f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        require(TARGET_XREFS[address].issubset(xrefs.get(address, set())), f"xref set mismatch at {address}", failures)

    helper_names = {row["name"] for row in read_tsv(BASE / "post-helper-metadata.tsv")}
    for name in HELPER_NAMES:
        require(name in helper_names, f"missing helper metadata row: {name}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=8 comment_only_updated=8 missing=0 bad=0",
        "apply.log": "BADSIG: 0x004bc2e0",
        "apply-corrected-dry.log": "SUMMARY: updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=1 missing=0 bad=0",
        "apply-corrected.log": "SUMMARY: updated=1 skipped=7 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=1 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=8 found=8 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=8 missing=0",
        "post-xrefs.log": "Wrote 23 rows",
        "post-instructions.log": "Wrote 2088 instruction rows",
        "post-helper-metadata.log": "targets=9 found=9 missing=0",
        "post-helper-instructions.log": "Wrote 729 instruction rows",
        "post-entry-callsite-instructions.log": "Wrote 371 instruction rows",
        "post-decompile.log": "targets=8 dumped=8 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6098 commented_functions=5620",
        "queue-probe.log": "Commentless functions: 478",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave820.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave820_queue_probe.log",
    }
    clean_logs = set(expected) - {"apply.log"}
    for relative, token in expected.items():
        path = log_aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        if relative in clean_logs:
            for bad in ("LockException", "MISSING:", "BADNAME:", "FAIL:", "missing=1", "bad=1", "failed=1"):
                require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)
    require("REPORT: Save succeeded" in read_text(BASE / "apply-corrected.log"), "missing corrected save success", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 478, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5620, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5620, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x004c0c70", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CPDSimpleSprite__EvalExpressionNode", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 171477895 or backup.get("totalBytes") == 171477895.0, "backup byte count mismatch", failures)
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
        GUIDE_DOC,
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
    require(scripts.get("test:ghidra-explosion-path-cost-grid-wave820") == r"py -3 tools\ghidra_explosion_path_cost_grid_wave820_probe.py --check", "missing package script", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave820 explosion path cost grid" for row in ledger_rows), "missing Wave820 ledger row", failures)
    require(any(row.get("task") == "Wave820 explosion path cost grid" and row.get("attempt_id") == 20475 for row in attempts), "missing Wave820 attempt row", failures)


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
        print("Wave820 explosion path cost-grid probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave820 explosion path cost-grid probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
