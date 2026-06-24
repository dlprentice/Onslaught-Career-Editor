#!/usr/bin/env python3
"""Validate Wave868 CDXEngine matrix-state read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave868-cdxengine-matrix-state"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cdxengine_matrix_state_wave868_2026-05-25.md"
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

TASK = "Wave868 CDXEngine matrix state"
BACKUP_PATH = r"G:\GhidraBackups\BEA_20260525-171842_post_wave868_cdxengine_matrix_state_verified"
NEXT_HEAD = "0x00551200 CDXEngine__ApplyCachedLight"
STRICT_PROXY = "5828/6105 = 95.46%"

TARGETS = {
    "0x005508a0": {
        "name": "CDXEngine__ClearMatrixBlock",
        "signature": "void __fastcall CDXEngine__ClearMatrixBlock(void * dest)",
        "tokens": ("0x58-byte matrix/cache block", "+0x10", "+0x20", "0x009c65c0", "0x0055088e"),
        "tags": {"matrix-block-clear", "global-render-state"},
    },
    "0x005508e0": {
        "name": "CDXEngine__InitTransformCaches",
        "signature": "void __fastcall CDXEngine__InitTransformCaches(void * this)",
        "tokens": ("this+0x354", "this+0x394", "this+0x3d4", "this+0x414", "this+0xe28 through this+0xe2e"),
        "tags": {"transform-cache-init", "identity-matrix", "global-render-state"},
    },
    "0x00550b10": {
        "name": "CDXEngine__SetProjectionMatrix",
        "signature": "void __thiscall CDXEngine__SetProjectionMatrix(void * this, float near_z, float far_z, float viewport_w, float viewport_h)",
        "tokens": ("RET 0x10", "this+0xe2a", "near_z/viewport_w", "far_z/(far_z-near_z)", "CFEPBEConfig"),
        "tags": {"projection-matrix", "depth-matrix", "render-overlay"},
    },
    "0x00550be0": {
        "name": "CDXEngine__SetViewAndProjection",
        "signature": "void __thiscall CDXEngine__SetViewAndProjection(void * this, float * view_matrix, float * proj_matrix)",
        "tokens": ("RET 0x8", "CVertexShader__DispatchTableCall_656f78", "this+0xe29", "this+0x394", "CRenderQueue__RenderAll"),
        "tags": {"view-projection-matrix", "render-queue", "camera-render-state"},
    },
    "0x00550ca0": {
        "name": "CDXEngine__SetWorldMatrixElements",
        "signature": "void __thiscall CDXEngine__SetWorldMatrixElements(void * this, float m00, float m01, float m02, float m03, float m10, float m11, float m12, float m13, float m20, float m21, float m22, float m23, float m30, float m31, float m32, float m33)",
        "tokens": ("RET 0x40", "this+0xe28", "this+0x354", "CMeshRenderer__RenderMesh", "CWaterRenderSystem", "unit shadow probes"),
        "tags": {"world-matrix", "render-transform-hub", "mesh-renderer", "water-render", "landscape-render"},
    },
}

COMMON_TAGS = {
    "static-reaudit",
    "cdxengine-matrix-state-wave868",
    "wave868-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-reviewed",
    "important-connective-infrastructure",
    "cdxengine",
    "renderer-state",
    "matrix-state",
    "transform-cache",
}

CORE_ANCHORS = (
    TASK,
    "cdxengine-matrix-state-wave868",
    "0x005508a0 CDXEngine__ClearMatrixBlock",
    "void __fastcall CDXEngine__ClearMatrixBlock(void * dest)",
    "0x005508e0 CDXEngine__InitTransformCaches",
    "void __fastcall CDXEngine__InitTransformCaches(void * this)",
    "0x00550b10 CDXEngine__SetProjectionMatrix",
    "void __thiscall CDXEngine__SetProjectionMatrix(void * this, float near_z, float far_z, float viewport_w, float viewport_h)",
    "0x00550be0 CDXEngine__SetViewAndProjection",
    "void __thiscall CDXEngine__SetViewAndProjection(void * this, float * view_matrix, float * proj_matrix)",
    "0x00550ca0 CDXEngine__SetWorldMatrixElements",
    "void __thiscall CDXEngine__SetWorldMatrixElements(void * this, float m00, float m01, float m02, float m03, float m10, float m11, float m12, float m13, float m20, float m21, float m22, float m23, float m30, float m31, float m32, float m33)",
    "high-importance, low local-evidence-density renderer infrastructure",
    NEXT_HEAD,
    STRICT_PROXY,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime rendering behavior proven",
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
        "pre-metadata.tsv": 5,
        "pre-tags.tsv": 5,
        "pre-xrefs.tsv": 50,
        "pre-instructions.tsv": 256,
        "pre-decompile/index.tsv": 5,
        "pre-xref-site-instructions.tsv": 1350,
        "post-metadata.tsv": 5,
        "post-tags.tsv": 5,
        "post-xrefs.tsv": 50,
        "post-instructions.tsv": 256,
        "post-decompile/index.tsv": 5,
        "post-xref-site-instructions.tsv": 1350,
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
            for token in ("Wave868 CDXEngine matrix-state static read-back", "high-importance, low local-evidence-density renderer infrastructure", *expected["tokens"]):
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
        "CDXEngine__Render",
        "CHud__RenderTargetIndicatorOverlay",
        "CDXCompass__RenderWorldSpaceOverlay",
        "CFrontEnd__RenderStart",
        "CRenderQueue__RenderAll",
        "CMeshRenderer__RenderMesh",
        "CDXLandscape__Render",
        "CDXTrees__Render",
        "CWaterRenderSystem__RenderMainPass",
        "CDXImposter__RenderAll",
    ):
        require(token in xref_text, f"missing xref token: {token}", failures)

    site_text = "\n".join("\t".join(row.values()) for row in read_tsv(BASE / "post-xref-site-instructions.tsv"))
    for token in ("0x0055087e", "CALL\t0x005508a0", "0x0055088e", "CALL\t0x005508e0", "0x00550ca0", "CALL\t0x00550ca0"):
        require(token in site_text, f"missing xref-site token: {token}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=5 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=5 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=5 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=5 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=5 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=5 found=5 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=5 missing=0",
        "post-xrefs.log": "Wrote 50 rows",
        "post-instructions.log": "Wrote 256 function-body instruction rows",
        "post-decompile.log": "targets=5 dumped=5 missing=0 failed=0",
        "pre-xref-site-instructions.log": "Wrote 1350 instruction rows",
        "post-xref-site-instructions.log": "Wrote 1350 instruction rows",
        "quality-refresh.log": "total_functions=6105 commented_functions=5828",
        "queue-probe.log": "Commentless functions: 277",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave868.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave868_queue_probe.log",
    }
    for relative, token in expected.items():
        path = log_aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "READBACK_BAD", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)
    require(read_text(BASE / "apply.log").count("READBACK_OK:") == 5, "apply readback count mismatch", failures)
    require("REPORT: Save succeeded" in read_text(BASE / "apply.log"), "missing save success token", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6105, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 277, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    for name in ("commentlessHighSignal", "signature", "nameConfidence"):
        require(queue["priorityQueues"][name] == [], f"{name} queue should be empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6105, "quality TSV row count mismatch", failures)
    require(commented == 5828, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5828, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x00551200", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CDXEngine__ApplyCachedLight", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 172362631 or backup.get("totalBytes") == 172362631.0, "backup byte count mismatch", failures)
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
    require(scripts.get("test:ghidra-cdxengine-matrix-state-wave868") == r"py -3 tools\ghidra_cdxengine_matrix_state_wave868_probe.py --check", "missing package script", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == TASK for row in ledger_rows), "missing Wave868 ledger row", failures)
    require(any(row.get("task") == TASK and row.get("attempt_id") == 20523 for row in attempts), "missing Wave868 attempt row", failures)


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
        print("Wave868 CDXEngine matrix-state probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave868 CDXEngine matrix-state probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
