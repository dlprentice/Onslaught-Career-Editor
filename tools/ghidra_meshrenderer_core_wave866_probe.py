#!/usr/bin/env python3
"""Validate Wave866 MeshRenderer core read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave866-meshrenderer-core"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_meshrenderer_core_wave866_2026-05-25.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
MESH_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "MeshRenderer.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

TASK = "Wave866 mesh renderer core"
ADDRESS = "0x00549570"
NAME = "CMeshRenderer__RenderMeshCore"
FULL_ANCHOR = f"{ADDRESS} {NAME}"
SIGNATURE = (
    "void __cdecl CMeshRenderer__RenderMeshCore(float world_position_x, float world_position_y, "
    "float world_position_z, float world_position_w, float * transform_matrix12, void * mesh_part, "
    "void * render_context, void * effect_owner, int render_slot_or_mode, int render_flags, "
    "int reserved_zero, void * world_position_vec4)"
)
BACKUP_PATH = r"G:\GhidraBackups\BEA_20260525-162911_post_wave866_meshrenderer_core_verified"
NEXT_HEAD = "0x005501d0 CVBufTexture__GetVertexWriteCursorPlusOne"
STRICT_PROXY = "5820/6105 = 95.33%"

COMMON_TAGS = {
    "static-reaudit",
    "meshrenderer-core-wave866",
    "wave866-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "important-connective-infrastructure",
    "mesh-renderer",
    "render-core",
    "caller-cleaned-0x30",
    "large-stack-frame",
    "cvbuftexture",
    "mesh-layer-pass",
    "animated-pose",
}

CORE_ANCHORS = (
    TASK,
    "meshrenderer-core-wave866",
    FULL_ANCHOR,
    SIGNATURE,
    "caller-cleaned",
    "0x004b6a82",
    "0x30",
    "0x1e54-byte stack frame",
    "CMCMech__BuildInterpolatedPoseAndAnchor",
    "CVBufTexture",
    "CMeshRenderer__RenderMeshWithLayerPasses",
    "0x0054a4b6",
    "0x0054b265",
    "high-importance connective renderer infrastructure",
    NEXT_HEAD,
    STRICT_PROXY,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime rendering behavior proven",
    "visual rendering behavior proven",
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
        "pre-instructions.tsv": 2093,
        "pre-decompile/index.tsv": 1,
        "pre-xref-site-instructions.tsv": 121,
        "pre-caller-decompile/index.tsv": 1,
        "pre-caller-instructions.tsv": 614,
        "post-metadata.tsv": 1,
        "post-tags.tsv": 1,
        "post-xrefs.tsv": 1,
        "post-instructions.tsv": 2093,
        "post-decompile/index.tsv": 1,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs = {normalize_address(row["target_addr"]): row for row in read_tsv(BASE / "post-xrefs.tsv")}

    row = metadata.get(ADDRESS)
    require(row is not None, "missing post metadata", failures)
    if row is not None:
        require(row.get("name") == NAME, "metadata name mismatch", failures)
        require(row.get("signature") == SIGNATURE, f"metadata signature mismatch: {row.get('signature')}", failures)
        require(row.get("status") == "OK", "metadata status mismatch", failures)
        for token in ("Wave866 mesh-renderer-core static read-back", "caller cleans 0x30", "0x1e54-byte stack frame", "high-importance connective renderer infrastructure"):
            require(token in row.get("comment", ""), f"missing metadata comment token: {token}", failures)

    tag_row = tags.get(ADDRESS)
    require(tag_row is not None, "missing post tags", failures)
    if tag_row is not None:
        actual_tags = set(tag_row.get("tags", "").split(";"))
        require(COMMON_TAGS.issubset(actual_tags), f"tags missing: {COMMON_TAGS - actual_tags}", failures)
        require(tag_row.get("status") == "OK", "tag status mismatch", failures)

    dec = decompile.get(ADDRESS)
    require(dec is not None, "missing post decompile index", failures)
    if dec is not None:
        require(dec.get("signature") == SIGNATURE, f"decompile signature mismatch: {dec.get('signature')}", failures)
        require(dec.get("status") == "OK", "decompile status mismatch", failures)

    xref = xrefs.get(ADDRESS)
    require(xref is not None, "missing xref row", failures)
    if xref is not None:
        require(normalize_address(xref.get("from_addr", "")) == "0x004b6a82", "xref source mismatch", failures)
        require(xref.get("from_function") == "CMeshRenderer__RenderMesh", "xref function mismatch", failures)
        require(xref.get("ref_type") == "UNCONDITIONAL_CALL", "xref type mismatch", failures)

    site_rows = read_tsv(BASE / "pre-xref-site-instructions.tsv")
    site_text = "\n".join("\t".join(row.values()) for row in site_rows)
    for token in ("0x004b6a82", "CALL", "0x00549570", "ADD\tESP, 0x30"):
        require(token in site_text, f"missing callsite token: {token}", failures)

    post_decompile = read_text(BASE / "post-decompile" / "00549570_CMeshRenderer__RenderMeshCore.c")
    for token in ("CMeshRenderer__RenderMeshWithLayerPasses", "CVBufTexture__RenderBatchList", "RenderState_Set(0x1b,1)"):
        require(token in post_decompile, f"missing decompile token: {token}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=1 skipped=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=1 found=1 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=1 missing=0",
        "post-xrefs.log": "Wrote 1 rows",
        "post-instructions.log": "Wrote 2093 function-body instruction rows",
        "post-decompile.log": "targets=1 dumped=1 missing=0 failed=0",
        "pre-xref-site-instructions.log": "Wrote 121 instruction rows",
        "pre-caller-instructions.log": "Wrote 614 function-body instruction rows",
        "quality-refresh.log": "total_functions=6105 commented_functions=5820",
        "queue-probe.log": "Commentless functions: 285",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave866.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave866_queue_probe.log",
    }
    for relative, token in expected.items():
        path = log_aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "READBACK_BAD", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)
    require(read_text(BASE / "apply.log").count("READBACK_OK:") == 1, "apply readback count mismatch", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6105, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 285, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    for name in ("commentlessHighSignal", "signature", "nameConfidence"):
        require(queue["priorityQueues"][name] == [], f"{name} queue should be empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6105, "quality TSV row count mismatch", failures)
    require(commented == 5820, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5820, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x005501d0", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CVBufTexture__GetVertexWriteCursorPlusOne", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 172329863 or backup.get("totalBytes") == 172329863.0, "backup byte count mismatch", failures)
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
        MESH_DOC,
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
    require(scripts.get("test:ghidra-meshrenderer-core-wave866") == r"py -3 tools\ghidra_meshrenderer_core_wave866_probe.py --check", "missing package script", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == TASK for row in ledger_rows), "missing Wave866 ledger row", failures)
    require(any(row.get("task") == TASK and row.get("attempt_id") == 20521 for row in attempts), "missing Wave866 attempt row", failures)


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
        print("Wave866 MeshRenderer core probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave866 MeshRenderer core probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
