#!/usr/bin/env python3
"""Validate Wave829 render-state world-reset read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave829-renderstate-world-reset"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_renderstate_world_reset_wave829_2026-05-24.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
ENGINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "engine.cpp" / "_index.md"
VBUFTEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "vbuftexture.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260524-213733_post_wave829_renderstate_world_reset_verified"
TARGET = "0x004eb1e0"
TARGET_NAME = "D3DStateCache__UseDefaultRenderState"
TARGET_SIGNATURE = "void D3DStateCache__UseDefaultRenderState(void)"
NEXT_HEAD = "0x004ef100 CUnit__RunTransitionStepThreeTimes"

TARGETS = {
    "0x004eb1e0": ("D3DStateCache__UseDefaultRenderState", "void D3DStateCache__UseDefaultRenderState(void)"),
    "0x00513600": ("D3DStateCache__ResetSentinelTable", "void D3DStateCache__ResetSentinelTable(void)"),
    "0x00513a50": ("CEngine__SetRenderStateCached", "void __thiscall CEngine__SetRenderStateCached(void * this, int state_id, int value)"),
    "0x00513c20": ("RenderState_SetRaw", "void __stdcall RenderState_SetRaw(int render_state, int value)"),
    "0x00513d90": ("RenderState_SetAlphaRefCached", "void __stdcall RenderState_SetAlphaRefCached(int alpha_ref)"),
    "0x00513dd0": ("RenderState_SetAlphaRefRaw", "void __stdcall RenderState_SetAlphaRefRaw(int alpha_ref)"),
    "0x00514030": ("RenderState_Set_23_8C_Compat", "void __stdcall RenderState_Set_23_8C_Compat(char enable)"),
    "0x00550d50": ("CDXEngine__ApplyPendingRenderState", "void __thiscall CDXEngine__ApplyPendingRenderState(void * this, char force_raw)"),
    "0x00558fb0": ("CVBufTexture__SetupRenderStates", "void __thiscall CVBufTexture__SetupRenderStates(void * this, char enable_overlay)"),
}

COMMON_TAGS = {
    "static-reaudit",
    "renderstate-world-reset-wave829",
    "wave829-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "render-state",
}

CORE_ANCHORS = (
    "Wave829 render-state world reset",
    "renderstate-world-reset-wave829",
    "0x004eb1e0 D3DStateCache__UseDefaultRenderState",
    "D3DStateCache__UseDefaultRenderState",
    "STATE.UseDefault()",
    "0x00513600 D3DStateCache__ResetSentinelTable",
    "0x00513a50 CEngine__SetRenderStateCached",
    "0x00513c20 RenderState_SetRaw",
    "0x00550d50 CDXEngine__ApplyPendingRenderState",
    "0x00558fb0 CVBufTexture__SetupRenderStates",
    "5650/6098 = 92.65%",
    NEXT_HEAD,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime render behavior proven",
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


def count_strict_clean(rows: list[dict[str, str]]) -> int:
    return sum(
        1
        for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not re.search(r"\bparam_\d+\b", row.get("signature", ""))
    )


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-context-metadata.tsv": 10,
        "pre-context-tags.tsv": 10,
        "pre-context-xrefs.tsv": 651,
        "pre-context-instructions.tsv": 370,
        "pre-context-decompile/index.tsv": 10,
        "pre-helper-metadata.tsv": 9,
        "pre-helper-instructions.tsv": 333,
        "pre-helper-decompile/index.tsv": 9,
        "pre-target-caller-metadata.tsv": 5,
        "pre-target-caller-decompile/index.tsv": 5,
        "post-metadata.tsv": 9,
        "post-tags.tsv": 9,
        "post-xrefs.tsv": 237,
        "post-instructions.tsv": 333,
        "post-decompile/index.tsv": 9,
        "post-target-caller-decompile/index.tsv": 5,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    for address, (name, signature) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            comment = row.get("comment", "")
            require("Wave829 static read-back" in comment, f"missing Wave829 comment at {address}", failures)
            require("Static retail" in comment, f"missing static-evidence boundary at {address}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"tags missing at {address}: {COMMON_TAGS - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    target_text = read_text(BASE / "post-decompile" / "004eb1e0_D3DStateCache__UseDefaultRenderState.c")
    for token in ("D3DStateCache__ResetSentinelTable", "RenderState_SetRaw", "RenderState_Set_23_8C_Compat", "D3DStateCache__SetState114Cached"):
        require(token in target_text, f"missing target decompile token: {token}", failures)

    caller_files = (
        "0053e220_CDXEngine__PreRender.c",
        "0053e2e0_CDXEngine__Render.c",
        "00540f70_CDXFrontEnd__RenderStart.c",
        "0042c810_CConsole__RenderLoadingScreen.c",
        "00470650_CGame__DrawDebugStuff.c",
    )
    total_calls = 0
    for relative in caller_files:
        text = read_text(BASE / "post-target-caller-decompile" / relative)
        total_calls += text.count(TARGET_NAME)
        require("CGame__ResetRenderStateForWorldRender" not in text, f"stale caller name remains in {relative}", failures)
    require(total_calls >= 5, "caller decompile call count mismatch", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=9 renamed=0 would_rename=1 signature_updated=0 comment_only_updated=9 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=9 skipped=0 renamed=1 would_rename=0 signature_updated=0 comment_only_updated=9 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=9 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=9 found=9 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=9 missing=0",
        "post-xrefs.log": "Wrote 237 rows",
        "post-instructions.log": "Wrote 333 instruction rows",
        "post-decompile.log": "targets=9 dumped=9 missing=0 failed=0",
        "post-target-caller-decompile.log": "targets=5 dumped=5 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("MISSING:", "BADNAME:", "FAIL:", "missing=1", "bad=1", "failed=1", "LockException"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    apply_text = read_text(BASE / "apply.log")
    require("READBACK_OK: 0x004eb1e0 D3DStateCache__UseDefaultRenderState" in apply_text, "missing apply target readback", failures)
    require("Unable to lock due to active transaction" in apply_text, "missing documented first-apply redundant-save issue", failures)
    final_text = read_text(BASE / "apply-final-dry.log")
    require("ERROR REPORT SCRIPT ERROR" not in final_text, "final dry has script error", failures)

    quality_log = read_text(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave829.log")
    queue_log = read_text(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave829_queue_probe.log")
    require("total_functions=6098 commented_functions=5650" in quality_log, "missing Wave829 quality export token", failures)
    require("Commentless functions: 448" in queue_log, "missing Wave829 queue probe token", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 448, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(queue["priorityQueues"]["commentlessHighSignal"] == [], "high-signal queue should be empty", failures)
    require(queue["priorityQueues"]["signature"] == [], "signature queue should be empty", failures)
    require(queue["priorityQueues"]["nameConfidence"] == [], "name-confidence queue should be empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented = sum(1 for row in rows if row.get("comment", "").strip())
    strict_clean = count_strict_clean(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5650, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5650, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x004ef100", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CUnit__RunTransitionStepThreeTimes", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 171641735 or backup.get("totalBytes") == 171641735.0, "backup byte count mismatch", failures)
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
        ENGINE_DOC,
        VBUFTEXTURE_DOC,
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
        scripts.get("test:ghidra-renderstate-world-reset-wave829")
        == r"py -3 tools\ghidra_renderstate_world_reset_wave829_probe.py --check",
        "missing package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave829 render-state world reset" for row in ledger_rows), "missing Wave829 ledger row", failures)
    require(
        any(row.get("task") == "Wave829 render-state world reset" and row.get("attempt_id") == 20484 for row in attempts),
        "missing Wave829 attempt row",
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
        print("Wave829 render-state world-reset probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave829 render-state world-reset probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
