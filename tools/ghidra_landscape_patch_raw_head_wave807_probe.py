#!/usr/bin/env python3
"""Validate Wave807 landscape-patch raw-head read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave807-landscape-patch-raw-head"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_landscape_patch_raw_head_wave807_2026-05-24.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
DXPATCH_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXPatchManager.cpp.md"
DXLANDSCAPE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXLandscape.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

ADDRESS = "0x0048f2f0"
PRE_NAME = "CDXLandscape__SetUpdateBoundsAndRebuildVB"
NAME = "CDXPatch__SetGridOriginStepAndRebuild"
SIGNATURE = "void __thiscall CDXPatch__SetGridOriginStepAndRebuild(void * this, int grid_origin_x, int grid_origin_z, int grid_step, int tile_metadata)"
BACKUP_PATH = r"G:\GhidraBackups\BEA_20260524-105819_post_wave807_landscape_patch_raw_head_verified"

COMMON_TAGS = {
    "static-reaudit",
    "landscape-patch-raw-head-wave807",
    "wave807-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "cdxpatch",
    "dx-landscape",
    "terrain-lod",
    "height-grid",
    "renamed",
    "tranche-head",
}

COMMENT_TOKENS = (
    "Wave807 static read-back correction",
    "RET 0x10",
    "0x00546fe6",
    "CDXPatchManager__AllocatePatchSlot",
    "grid_step derived as 4 >> lod_slot",
    "[ESI+0x0b]",
    "CDXPatch__RebuildHeightGridVertexBuffer",
    "runtime terrain rendering/GPU behavior",
)

CORE_ANCHORS = (
    "Wave807 landscape patch raw head",
    "landscape-patch-raw-head-wave807",
    "0x0048f2f0 CDXPatch__SetGridOriginStepAndRebuild",
    "0x00546fe6",
    "CDXLandscape__UpdateLOD",
    "5582/6098 = 91.54%",
    "0x0048f620 CDXEngine__RenderPostMissionOverlayAndMenu",
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime terrain rendering proven",
    "runtime gpu behavior proven",
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
        "pre-metadata.tsv": 1,
        "pre-tags.tsv": 1,
        "pre-xrefs.tsv": 1,
        "pre-instructions.tsv": 213,
        "pre-decompile/index.tsv": 1,
        "pre-context-metadata.tsv": 7,
        "pre-context-instructions.tsv": 1295,
        "pre-context-decompile/index.tsv": 7,
        "pre-caller-metadata.tsv": 1,
        "pre-caller-instructions.tsv": 271,
        "pre-caller-decompile/index.tsv": 1,
        "pre-callsite-instructions.tsv": 76,
        "post-metadata.tsv": 1,
        "post-tags.tsv": 1,
        "post-xrefs.tsv": 1,
        "post-instructions.tsv": 211,
        "post-decompile/index.tsv": 1,
        "post-callsite-instructions.tsv": 76,
        "post-caller-decompile/index.tsv": 1,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    pre = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs = {normalize_address(row["target_addr"]): row for row in read_tsv(BASE / "post-xrefs.tsv")}

    require(pre.get(ADDRESS, {}).get("name") == PRE_NAME, "pre metadata name mismatch", failures)
    require(pre.get(ADDRESS, {}).get("signature") == f"int {PRE_NAME}(void)", "pre metadata signature mismatch", failures)

    row = metadata.get(ADDRESS)
    require(row is not None, "missing post metadata", failures)
    if row is not None:
        require(row.get("name") == NAME, "post metadata name mismatch", failures)
        require(row.get("signature") == SIGNATURE, "post metadata signature mismatch", failures)
        require(row.get("status") == "OK", "post metadata status mismatch", failures)
        for token in COMMENT_TOKENS:
            require(token in row.get("comment", ""), f"missing comment token: {token}", failures)

    tag_row = tags.get(ADDRESS)
    require(tag_row is not None, "missing post tags", failures)
    if tag_row is not None:
        actual_tags = set(tag_row.get("tags", "").split(";"))
        require(COMMON_TAGS.issubset(actual_tags), f"missing tags: {COMMON_TAGS - actual_tags}", failures)
        require(tag_row.get("status") == "OK", "post tag status mismatch", failures)

    dec = decompile.get(ADDRESS)
    require(dec is not None, "missing post decompile index row", failures)
    if dec is not None:
        require(dec.get("name") == NAME, "post decompile name mismatch", failures)
        require(dec.get("signature") == SIGNATURE, "post decompile signature mismatch", failures)
        require(dec.get("status") == "OK", "post decompile status mismatch", failures)

    xref = xrefs.get(ADDRESS)
    require(xref is not None, "missing post xref row", failures)
    if xref is not None:
        require(normalize_address(xref.get("from_addr", "")) == "0x00546fe6", "xref from_addr mismatch", failures)
        require(xref.get("from_function") == "CDXLandscape__UpdateLOD", "xref from_function mismatch", failures)
        require(xref.get("ref_type") == "UNCONDITIONAL_CALL", "xref ref_type mismatch", failures)

    callsite_text = read_text(BASE / "post-caller-decompile" / "00546b40_CDXLandscape__UpdateLOD.c")
    for token in (NAME, "iStack_c8 * 8", "iStack_c4 * 8", "4 >>", "*(int *)(pbVar16 + 0xb)"):
        require(token in callsite_text, f"missing callsite token: {token}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=1 signature_updated=1 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=1 skipped=0 renamed=1 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=1 found=1 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=1 missing=0",
        "post-xrefs.log": "Wrote 1 rows",
        "post-instructions.log": "Wrote 211 instruction rows",
        "post-decompile.log": "targets=1 dumped=1 missing=0 failed=0",
        "post-callsite-instructions.log": "Wrote 76 instruction rows",
        "post-caller-decompile.log": "targets=1 dumped=1 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6098 commented_functions=5582",
        "queue-probe.log": "Commentless functions: 516",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave807.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave807_queue_probe.log",
    }
    for relative, token in expected.items():
        path = log_aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BADNAME:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 516, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5582, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5582, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x0048f620", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CDXEngine__RenderPostMissionOverlayAndMenu", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 171314055, "backup byte count mismatch", failures)
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
        DXPATCH_DOC,
        DXLANDSCAPE_DOC,
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
        scripts.get("test:ghidra-landscape-patch-raw-head-wave807")
        == r"py -3 tools\ghidra_landscape_patch_raw_head_wave807_probe.py --check",
        "missing package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave807 landscape patch raw head" for row in ledger_rows), "missing Wave807 ledger row", failures)
    require(any(row.get("task") == "Wave807 landscape patch raw head" and row.get("attempt_id") == 20462 for row in attempts), "missing Wave807 attempt row", failures)


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
        print("Wave807 landscape-patch raw-head probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave807 landscape-patch raw-head probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
