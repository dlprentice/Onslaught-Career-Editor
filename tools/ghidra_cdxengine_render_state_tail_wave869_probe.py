#!/usr/bin/env python3
"""Validate Wave869 CDXEngine render-state tail read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave869-cdxengine-render-state-tail"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cdxengine_render_state_tail_wave869_2026-05-25.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
ENGINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "engine.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

TASK = "Wave869 CDXEngine render-state tail"
BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260525-174243_post_wave869_cdxengine_render_state_tail_verified"
NEXT_HEAD = "0x005515a0 CDXEngine__InitConsoleVar_UseRenderQueue"
STRICT_PROXY = "5838/6105 = 95.63%"

TARGETS = {
    "0x00551200": {
        "name": "CDXEngine__ApplyCachedLight",
        "signature": "void __thiscall CDXEngine__ApplyCachedLight(void * this, int light_index, int enabled)",
        "tokens": ("0x5c-byte cached light record", "0xcc", "CDXLandscape__Render", "CDXEngine__ApplyPendingRenderState"),
        "tags": {"cached-light", "landscape-render", "pending-render-state"},
    },
    "0x005512f0": {
        "name": "CDXEngine__SetFieldE18",
        "signature": "void __thiscall CDXEngine__SetFieldE18(void * this, int value)",
        "tokens": ("this+0xe18", "CMeshRenderer__RenderMeshCore", "conservative field-based name"),
        "tags": {"field-e18", "mesh-renderer", "conservative-name"},
    },
    "0x00551300": {
        "name": "CDXEngine__PushTransformState",
        "signature": "void __thiscall CDXEngine__PushTransformState(void * this, int slot, int mode, float * matrix)",
        "tokens": ("this+0x354", "this+0x394", "this+0x3d4", "CHud__RenderTargetMarkers3D", "CHud__RenderWorldTargetSprites"),
        "tags": {"transform-state", "hud-world-marker", "matrix-snapshot"},
    },
    "0x005513d0": {
        "name": "CDXEngine__SetVertexFormatDeferred",
        "signature": "void __thiscall CDXEngine__SetVertexFormatDeferred(void * this, int format)",
        "tokens": ("this+0xe2d", "this+0x2f0", "CDXEngine__Render"),
        "tags": {"vertex-format", "deferred-render-state", "cdxengine-render"},
    },
    "0x005513f0": {
        "name": "CDXEngine__SetShaderMode",
        "signature": "void __thiscall CDXEngine__SetShaderMode(void * this, int mode)",
        "tokens": ("this+0xe58", "this+0xe14", "CEngine__SetVertexShaderHandleRaw", "RenderState_Set_23_8C_Compat"),
        "tags": {"shader-mode", "vertex-shader", "unnamed-caller-xref"},
    },
    "0x00551420": {
        "name": "D3DStateCache__SetMipFilterByGlobalToggle",
        "signature": "void __cdecl D3DStateCache__SetMipFilterByGlobalToggle(int stage)",
        "tokens": ("g_DisallowMipMapping", "D3DStateCache__SetState114Cached(stage, 7", "sampler policy"),
        "tags": {"mip-filter", "global-toggle", "sampler-state"},
    },
    "0x00551460": {
        "name": "D3DStateCache__SetMipFilterLinear",
        "signature": "void __cdecl D3DStateCache__SetMipFilterLinear(int stage)",
        "tokens": ("D3DStateCache__SetState114Cached(stage, 7, 2)", "CHud__RenderOverlay", "landscape"),
        "tags": {"mip-filter", "linear-filter", "sampler-state"},
    },
    "0x00551480": {
        "name": "D3DStateCache__SetMipFilterPoint",
        "signature": "void __cdecl D3DStateCache__SetMipFilterPoint(int stage)",
        "tokens": ("D3DStateCache__SetState114Cached(stage, 7, 0)", "HudRenderState__ApplyOverlaySpriteState", "CLevelBriefingLog__Render"),
        "tags": {"mip-filter", "point-filter", "sampler-state", "hud-render"},
    },
    "0x005514a0": {
        "name": "CDXEngine__SetProjectionDepthBiasIndex",
        "signature": "void __thiscall CDXEngine__SetProjectionDepthBiasIndex(void * this, int bias_index)",
        "tokens": ("this+0xe24", "0x009c742c", "0xb0", "this+0xe2a", "CWaterRenderSystem__RenderMainPass"),
        "tags": {"projection-depth-bias", "water-render", "device-transform"},
    },
    "0x00551510": {
        "name": "CDXEngine__GetProjectionWithDepthBias",
        "signature": "void __thiscall CDXEngine__GetProjectionWithDepthBias(void * this, float * out_matrix)",
        "tokens": ("this+0x3d4", "out_matrix[0xe]", "CVertexShader__ApplyRenderStateShaderConstants"),
        "tags": {"projection-depth-bias", "vertex-shader-constants", "matrix-copy"},
    },
}

COMMON_TAGS = {
    "static-reaudit",
    "cdxengine-render-state-tail-wave869",
    "wave869-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-reviewed",
    "important-connective-infrastructure",
    "cdxengine",
    "renderer-state",
    "lighting-state",
    "d3d-state-cache",
}

CORE_ANCHORS = (
    TASK,
    "cdxengine-render-state-tail-wave869",
    "0x00551200 CDXEngine__ApplyCachedLight",
    "void __thiscall CDXEngine__ApplyCachedLight(void * this, int light_index, int enabled)",
    "0x005512f0 CDXEngine__SetFieldE18",
    "0x00551300 CDXEngine__PushTransformState",
    "0x005513d0 CDXEngine__SetVertexFormatDeferred",
    "0x005513f0 CDXEngine__SetShaderMode",
    "0x00551420 D3DStateCache__SetMipFilterByGlobalToggle",
    "0x00551460 D3DStateCache__SetMipFilterLinear",
    "0x00551480 D3DStateCache__SetMipFilterPoint",
    "0x005514a0 CDXEngine__SetProjectionDepthBiasIndex",
    "0x00551510 CDXEngine__GetProjectionWithDepthBias",
    "high-importance, low local-evidence-density renderer infrastructure",
    NEXT_HEAD,
    STRICT_PROXY,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime rendering behavior proven",
    "runtime lighting behavior proven",
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
        "pre-metadata.tsv": 10,
        "pre-tags.tsv": 10,
        "pre-xrefs.tsv": 47,
        "pre-instructions.tsv": 237,
        "pre-decompile/index.tsv": 10,
        "pre-xref-site-instructions.tsv": 1269,
        "post-metadata.tsv": 10,
        "post-tags.tsv": 10,
        "post-xrefs.tsv": 47,
        "post-instructions.tsv": 237,
        "post-decompile/index.tsv": 10,
        "post-xref-site-instructions.tsv": 1269,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    for address, expected in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing post metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == expected["name"], f"metadata name mismatch at {address}", failures)
            require(row.get("signature") == expected["signature"], f"metadata signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in ("Wave869 CDXEngine render-state tail static read-back", *expected["tokens"]):
                require(token in row.get("comment", ""), f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing post tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            required = COMMON_TAGS | set(expected["tags"])
            require(required.issubset(actual_tags), f"tags missing at {address}: {required - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing post decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == expected["signature"], f"decompile signature mismatch at {address}: {dec.get('signature')}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    xref_text = "\n".join("\t".join(row.values()) for row in read_tsv(BASE / "post-xrefs.tsv"))
    for token in (
        "CDXLandscape__Render",
        "CDXEngine__ApplyPendingRenderState",
        "CMeshRenderer__RenderMeshCore",
        "CHud__RenderTargetMarkers3D",
        "CHud__RenderWorldTargetSprites",
        "CDXEngine__Render",
        "D3DStateCache__UseDefaultRenderState",
        "CDXEngine__PostRender",
        "HudRenderState__ApplyOverlaySpriteState",
        "CWaterRenderSystem__RenderMainPass",
        "CVertexShader__ApplyRenderStateShaderConstants",
    ):
        require(token in xref_text, f"missing xref token: {token}", failures)

    site_text = "\n".join("\t".join(row.values()) for row in read_tsv(BASE / "post-xref-site-instructions.tsv"))
    for token in ("CALL\t0x00551200", "CALL\t0x00551300", "CALL\t0x00551420", "CALL\t0x005514a0", "CALL\t0x00551510"):
        require(token in site_text, f"missing xref-site token: {token}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=10 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=10 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=10 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=10 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=10 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=10 found=10 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=10 missing=0",
        "post-xrefs.log": "Wrote 47 rows",
        "post-instructions.log": "Wrote 237 function-body instruction rows",
        "post-decompile.log": "targets=10 dumped=10 missing=0 failed=0",
        "pre-xref-site-instructions.log": "Wrote 1269 instruction rows",
        "post-xref-site-instructions.log": "Wrote 1269 instruction rows",
        "quality-refresh.log": "total_functions=6105 commented_functions=5838",
        "queue-probe.log": "Commentless functions: 267",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave869.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave869_queue_probe.log",
    }
    for relative, token in expected.items():
        path = log_aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "READBACK_BAD", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)
    require(read_text(BASE / "apply.log").count("READBACK_OK:") == 10, "apply readback count mismatch", failures)
    require("REPORT: Save succeeded" in read_text(BASE / "apply.log"), "missing save success token", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6105, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 267, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    for name in ("commentlessHighSignal", "signature", "nameConfidence"):
        require(queue["priorityQueues"][name] == [], f"{name} queue should be empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6105, "quality TSV row count mismatch", failures)
    require(commented == 5838, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5838, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x005515a0", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CDXEngine__InitConsoleVar_UseRenderQueue", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 172395399 or backup.get("totalBytes") == 172395399.0, "backup byte count mismatch", failures)
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
    require(scripts.get("test:ghidra-cdxengine-render-state-tail-wave869") == r"py -3 tools\ghidra_cdxengine_render_state_tail_wave869_probe.py --check", "missing package script", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == TASK for row in ledger_rows), "missing Wave869 ledger row", failures)
    require(any(row.get("task") == TASK and row.get("attempt_id") == 20524 for row in attempts), "missing Wave869 attempt row", failures)


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
        print("Wave869 CDXEngine render-state tail probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave869 CDXEngine render-state tail probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
