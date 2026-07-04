#!/usr/bin/env python3
"""Validate Wave875 CVBufTexture DrawSprite read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave875-cvbuftexture-drawsprite"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cvbuftexture_drawsprite_wave875_2026-05-25.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
VBUFTEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "vbuftexture.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

TASK = "Wave875 CVBufTexture DrawSprite"
ADDRESS = "0x00555be0"
NAME = "CVBufTexture__DrawSpriteEx"
SIGNATURE = (
    "void __cdecl CVBufTexture__DrawSpriteEx(float screen_x, float screen_y, float depth_z, "
    "void * texture, int anchor_or_blend_mode, int uv_mode, float uv_or_tile_scale, "
    "float rotation_radians, float argb_tint_bits, float width_scale, float height_scale, "
    "float u0, float u1, float v0, float v1)"
)
BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260525-205138_post_wave875_cvbuftexture_drawsprite_verified"
NEXT_HEAD = "0x00556cc0 CTexture__ctor"
STRICT_PROXY = "5873/6113 = 96.07%"

COMMON_TAGS = {
    "static-reaudit",
    "cvbuftexture-drawsprite-wave875",
    "wave875-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-corrected",
    "important-renderer-infrastructure",
    "high-importance-low-local-evidence-density",
    "cvbuftexture",
    "sprite-renderer",
    "hud-renderer",
    "frontend-renderer",
    "fastvb",
    "raw-commentless-head",
    "xrefs-91",
    "texture-fields-0xac-0xb0-0xb2",
    "triangle-strip",
}

COMMENT_TOKENS = (
    "Wave875 static read-back",
    "CVBufTexture central sprite quad emitter",
    "91 callers",
    "texture+0xac/+0xb0/+0xb2",
    "anchor/alignment cases 1-8",
    "uv_mode cases 0-4",
    "CFastVB__RenderTriangleStripImmediate",
    "high-importance renderer/HUD/frontend connective infrastructure with low local evidence density, not low-importance filler",
)

XREF_CALLERS = (
    "CConsole__RenderLoadingScreen",
    "CGameInterface__Render",
    "CHud__RenderTargetIndicatorOverlay",
    "HudOverlay__DrawSpriteQuad",
    "CLevelBriefingLog__Render",
    "CDXEngine__RenderMouseCursorSprite",
    "CMessageLog__Render",
    "CPauseMenu__Render",
    "CMenuItemDropdown__Render",
    "CDXBattleLine__Render",
    "CDXCompass__Render",
    "CDXImposter__RenderAll",
    "CDXSurf__RenderSurface",
    "CMenuItem__RenderValueBar",
)

CORE_ANCHORS = (
    TASK,
    "cvbuftexture-drawsprite-wave875",
    "0x00555be0 CVBufTexture__DrawSpriteEx",
    SIGNATURE,
    "91 xrefs",
    "texture+0xac",
    "texture+0xb0",
    "texture+0xb2",
    "CFastVB__RenderTriangleStripImmediate",
    "high-importance renderer/HUD/frontend connective infrastructure with low local evidence density, not low-importance filler",
    NEXT_HEAD,
    STRICT_PROXY,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime visual output proven",
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
        "pre-xrefs.tsv": 91,
        "pre-instructions.tsv": 516,
        "pre-decompile/index.tsv": 1,
        "pre-context-metadata.tsv": 7,
        "pre-context-decompile/index.tsv": 7,
        "post-metadata.tsv": 1,
        "post-tags.tsv": 1,
        "post-xrefs.tsv": 91,
        "post-instructions.tsv": 516,
        "post-decompile/index.tsv": 1,
        "post-context-metadata.tsv": 7,
        "post-context-decompile/index.tsv": 7,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    row = metadata.get(ADDRESS)
    require(row is not None, f"missing post metadata for {ADDRESS}", failures)
    if row is not None:
        require(row.get("name") == NAME, "metadata name mismatch", failures)
        require(row.get("signature") == SIGNATURE, f"metadata signature mismatch: {row.get('signature')}", failures)
        require(row.get("status") == "OK", "metadata status mismatch", failures)
        for token in COMMENT_TOKENS:
            require(contains_token(row.get("comment", ""), token), f"missing comment token: {token}", failures)

    tag_row = tags.get(ADDRESS)
    require(tag_row is not None, f"missing post tags for {ADDRESS}", failures)
    if tag_row is not None:
        actual_tags = set(tag_row.get("tags", "").split(";"))
        require(COMMON_TAGS.issubset(actual_tags), f"tags missing: {COMMON_TAGS - actual_tags}", failures)
        require(tag_row.get("status") == "OK", "tag status mismatch", failures)

    dec = decompile.get(ADDRESS)
    require(dec is not None, f"missing post decompile index for {ADDRESS}", failures)
    if dec is not None:
        require(dec.get("signature") == SIGNATURE, f"decompile signature mismatch: {dec.get('signature')}", failures)
        require(dec.get("status") == "OK", "decompile status mismatch", failures)

    xref_text = read_text(BASE / "post-xrefs.tsv")
    for caller in XREF_CALLERS:
        require(caller in xref_text, f"missing xref caller: {caller}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=1 skipped=0 renamed=0 would_rename=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 missing=0 bad=0",
        "post-metadata.log": "targets=1 found=1 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=1 missing=0",
        "post-xrefs.log": "Wrote 91 rows",
        "post-instructions.log": "Wrote 516 function-body instruction rows",
        "post-decompile.log": "targets=1 dumped=1 missing=0 failed=0",
        "post-context-metadata.log": "targets=7 found=7 missing=0",
        "post-context-decompile.log": "targets=7 dumped=7 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6113 commented_functions=5873",
        "queue-probe.log": "Commentless functions: 240",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave875.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave875_queue_probe.log",
    }
    for relative, token in expected.items():
        path = log_aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("Input file not found", "LockException", "BADADDR", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6113, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 240, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(queue["priorityQueues"]["commentlessHighSignal"] == [], "high-signal queue should be empty", failures)
    require(queue["priorityQueues"]["signature"] == [], "signature queue should be empty", failures)
    require(queue["priorityQueues"]["nameConfidence"] == [], "name-confidence queue should be empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6113, "quality TSV row count mismatch", failures)
    require(commented == 5873, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5873, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x00556cc0", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CTexture__ctor", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes", 0)) == 172624775, "backup byte count mismatch", failures)
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
        VBUFTEXTURE_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in CORE_ANCHORS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-cvbuftexture-drawsprite-wave875")
        == r"py -3 tools\ghidra_cvbuftexture_drawsprite_wave875_probe.py --check",
        "missing package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == TASK for row in ledger_rows), "missing Wave875 ledger row", failures)
    require(any(row.get("task") == TASK and row.get("attempt_id") == 20530 for row in attempts), "missing Wave875 attempt row", failures)


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
        print("Wave875 CVBufTexture DrawSprite probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave875 CVBufTexture DrawSprite probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
