#!/usr/bin/env python3
"""Validate Wave1095 render-state/matrix support review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1095-render-state-matrix-support-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_render_state_matrix_support_review_wave1095_2026-06-04.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1095_recheck_2026-06-04.md"
PACKAGE_JSON = ROOT / "package.json"
PROGRESS_JSON = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
ENGINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "engine.cpp" / "_index.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
TRACKING_STATE = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
README = ROOT / "README.MD"
CAPABILITIES = ROOT / "CURRENT_CAPABILITIES.md"
AGENTS = ROOT / "AGENTS.md"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260604-171413_post_wave1095_render_state_matrix_support_review_verified"
WAVE_TAG = "render-state-matrix-support-review-wave1095"
TARGET = "0x00513af0"
TARGET_NAME = "D3DStateCache__SetSlotMode4or5"
TARGET_SIGNATURE = "void __stdcall D3DStateCache__SetSlotMode4or5(int state_slot)"
TARGET_COMMENT = (
    "Frontend/game-state toggle helper: updates per-slot state array DAT_008557f4 "
    "(mode 4 or 5 based on DAT_008554fc) and notifies DAT_00888a50 via vfunc +0x10c "
    "when state changes."
)

TARGET_TAGS = {
    "static-reaudit",
    WAVE_TAG,
    "wave1095-readback-verified",
    "retail-binary-evidence",
    "tag-normalized",
    "comment-hardened",
    "d3d-state-cache",
    "direct3d-device",
    "render-state",
    "state-cache",
    "mode-toggle",
    "mode-4-or-5",
    "vtable-0x10c",
}

CONTEXT_TARGETS = {
    "0x00513820": ("D3DStateCache__SetStateCached", "void __stdcall D3DStateCache__SetStateCached(int state_slot, int state_id, int value)", ("Wave849", "cached texture-stage")),
    "0x00513870": ("D3DStateCache__SetStateRaw", "void __stdcall D3DStateCache__SetStateRaw(int state_slot, int state_id, int value)", ("Wave849", "raw state")),
    "0x00513b60": ("D3DStateCache__ForceSlotMode4or5", "void __stdcall D3DStateCache__ForceSlotMode4or5(int state_slot)", ("Wave850", "force")),
    "0x00550b10": ("CDXEngine__SetProjectionMatrix", "void __thiscall CDXEngine__SetProjectionMatrix(void * this, float near_z, float far_z, float viewport_w, float viewport_h)", ("Wave868", "projection")),
    "0x00550ca0": ("CDXEngine__SetWorldMatrixElements", "void __thiscall CDXEngine__SetWorldMatrixElements(void * this, float m00, float m01, float m02, float m03, float m10, float m11, float m12, float m13, float m20, float m21, float m22, float m23, float m30, float m31, float m32, float m33)", ("Wave868", "world")),
    "0x00550d50": ("CDXEngine__ApplyPendingRenderState", "void __thiscall CDXEngine__ApplyPendingRenderState(void * this, char force_raw)", ("Wave829", "pending render-state")),
    "0x00551200": ("CDXEngine__ApplyCachedLight", "void __thiscall CDXEngine__ApplyCachedLight(void * this, int light_index, int enabled)", ("Wave869", "cached light")),
}

DOC_TOKENS = (
    "Wave1095",
    WAVE_TAG,
    "0x00513af0 D3DStateCache__SetSlotMode4or5",
    "0x00513820 D3DStateCache__SetStateCached",
    "0x00513b60 D3DStateCache__ForceSlotMode4or5",
    "0x00550b10 CDXEngine__SetProjectionMatrix",
    "0x00550ca0 CDXEngine__SetWorldMatrixElements",
    "0x00550d50 CDXEngine__ApplyPendingRenderState",
    "0x00551200 CDXEngine__ApplyCachedLight",
    "1560/1560 = 100.00%",
    "812/1408 = 57.67%",
    "500/500 = 100.00%",
    "6410/6410 = 100.00%",
    BACKUP_PATH,
    "tag-only normalization",
)

OVERCLAIMS = (
    "runtime behavior proven",
    "runtime render-state behavior proven",
    "runtime rendering behavior proven",
    "runtime proof complete",
    "patch behavior proven",
    "rebuild parity proven",
    "all systems complete",
    "every system is complete",
    "fully reverse-engineered",
    "fully reverse engineered",
    "exact source-layout identity proven",
    "exact source layout identity proven",
)


def normalize_address(value: str) -> str:
    text = value.strip().lower()
    if text.startswith("0x"):
        text = text[2:]
    return "0x" + text.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig", errors="replace").replace("\x00", "")


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


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "metadata.tsv": 21,
        "tags.tsv": 21,
        "xrefs.tsv": 1025,
        "instructions.tsv": 1388,
        "decompile/index.tsv": 21,
        "post-metadata.tsv": 21,
        "post-tags.tsv": 21,
        "post-xrefs.tsv": 1025,
        "post-instructions.tsv": 1388,
        "post-decompile/index.tsv": 21,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs = read_tsv(BASE / "post-xrefs.tsv")

    target_row = metadata.get(TARGET)
    require(target_row is not None, f"missing metadata at {TARGET}", failures)
    if target_row is not None:
        require(target_row.get("name") == TARGET_NAME, "target name mismatch", failures)
        require(target_row.get("signature") == TARGET_SIGNATURE, f"target signature mismatch: {target_row.get('signature')}", failures)
        require(target_row.get("comment") == TARGET_COMMENT, "target comment mismatch", failures)
        require(target_row.get("status") == "OK", "target metadata status mismatch", failures)

    tag_row = tags.get(TARGET)
    require(tag_row is not None, f"missing tags at {TARGET}", failures)
    if tag_row is not None:
        actual = set(tag_row.get("tags", "").split(";"))
        require(TARGET_TAGS.issubset(actual), f"target tags missing: {sorted(TARGET_TAGS - actual)}", failures)
        require(tag_row.get("status") == "OK", "target tag status mismatch", failures)

    dec = decompile.get(TARGET)
    require(dec is not None, f"missing decompile at {TARGET}", failures)
    if dec is not None:
        require(dec.get("name") == TARGET_NAME, "target decompile name mismatch", failures)
        require(dec.get("signature") == TARGET_SIGNATURE, "target decompile signature mismatch", failures)
        require(dec.get("status") == "OK", "target decompile status mismatch", failures)

    for address, (name, signature, comment_tokens) in CONTEXT_TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing context metadata at {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"context name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"context signature mismatch at {address}", failures)
            comment = row.get("comment", "")
            for token in comment_tokens:
                require(token in comment, f"context comment token missing at {address}: {token}", failures)

    target_callers = {
        row.get("from_function", "")
        for row in xrefs
        if normalize_address(row.get("target_addr", "")) == TARGET
    }
    require(len(target_callers) >= 10, "target caller count too low", failures)
    for caller in (
        "CConsole__RenderLoadingScreen",
        "CFrontEnd__Render",
        "CHud__RenderOverlay",
        "CDXLandscape__RenderTerrain",
        "CMeshRenderer__RenderMeshCore",
        "CRenderQueue__BeginFrame",
        "CVBufTexture__DrawSpriteEx",
        "CDXTrees__Render",
    ):
        require(caller in target_callers, f"missing caller xref: {caller}", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=13 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=1 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=13 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0",
        "post-metadata.log": "targets=21 found=21 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=21 missing=0",
        "post-xrefs.log": "Wrote 1025 rows",
        "post-instructions.log": "Wrote 1388 function-body instruction rows",
        "post-decompile.log": "targets=21 dumped=21 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR:", "BADNAME:", "BADSIG:", "BADCOMMENT:", "BADTAGS:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)
    require("REPORT: Save succeeded" in read_text(BASE / "apply.log"), "apply did not report save succeeded", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 175541127 or backup.get("totalBytes") == 175541127.0, "backup bytes mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs_and_state(failures: list[str]) -> None:
    core_docs = [
        NOTE,
        AGGREGATE_NOTE,
        PROGRESS_JSON,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        ENGINE_DOC,
        BACKLOG,
        TRACKING_STATE,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
        README,
        CAPABILITIES,
        AGENTS,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing doc token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    progress = read_json(PROGRESS_JSON)
    require(progress["latestWave"]["wave"] == "Wave1095 render-state matrix support review", "progress latest wave mismatch", failures)
    require(progress["latestWave"]["status"] in {"validation_pending", "validated_pending_commit", "committed"}, "progress status mismatch", failures)
    require(progress["latestWave"]["backup"] == BACKUP_PATH, "progress backup mismatch", failures)
    require(progress["functionQuality"]["totalFunctions"] == 6410, "progress total mismatch", failures)
    require(progress["post100Reaudit"]["expandedStaticSurface"]["completed"] == 1560, "expanded count mismatch", failures)
    require(progress["post100Reaudit"]["wave911Focused"]["completed"] == 812, "wave911 focused mismatch", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(scripts.get("test:ghidra-render-state-matrix-support-review-wave1095") == r"py -3 tools\ghidra_render_state_matrix_support_review_wave1095_probe.py --check", "missing focused package script", failures)
    require(scripts.get("test:ghidra-wave900-plus-through-wave1095-recheck") == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1095 --check", "missing aggregate package script", failures)

    ledger = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1095 render-state matrix support review" for row in ledger), "missing Wave1095 ledger row", failures)
    require(any(row.get("task") == "Wave1095 render-state matrix support review" and row.get("attempt_id") == 20675 for row in attempts), "missing Wave1095 attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_docs_and_state(failures)

    if failures:
        print("Wave1095 render-state matrix support review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1095 render-state matrix support review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
