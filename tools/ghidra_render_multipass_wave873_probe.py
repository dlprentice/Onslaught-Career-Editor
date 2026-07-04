#!/usr/bin/env python3
"""Validate Wave873 render multipass read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave873-render-multipass"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_render_multipass_wave873_2026-05-25.md"
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

TASK = "Wave873 render multipass"
BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260525-193607_post_wave873_render_multipass_verified"
NEXT_HEAD = "0x00554f80 CAtmosphericsProfile__ctor"
STRICT_PROXY = "5862/6106 = 96.00%"

TARGETS = {
    "0x00553960": {
        "name": "CRenderQueue__RenderMultipassLayerA",
        "signature": "void __fastcall CRenderQueue__RenderMultipassLayerA(void * this)",
        "tokens": ("0x0053e692", "0x009c7550", "CDXLandscape__RenderTileRange", "owner prefix to CRenderQueue"),
        "tags": {"layer-a", "owner-corrected-from-cdxengine", "landscape-tile-range", "state-restore", "global-tint"},
    },
    "0x00554170": {
        "name": "CRenderQueue__RenderMultipassLayerB",
        "signature": "void __fastcall CRenderQueue__RenderMultipassLayerB(void * this)",
        "tokens": ("0x0053e6af", "0x009c7550", "this+0x5b0", "D3D device draw slot +0x14c"),
        "tags": {"layer-b", "owner-corrected-from-cdxengine", "d3d-draw-slot-14c", "state-restore", "global-matrix-state"},
    },
    "0x005545d0": {
        "name": "CRenderQueue__BuildProjectedSprites",
        "signature": "void __thiscall CRenderQueue__BuildProjectedSprites(void * this, void * unit)",
        "tokens": ("0x004773ab", "0x004779b3", "CStaticShadows__SampleShadowHeightBilinear", "0x02000000"),
        "tags": {"projected-sprites", "owner-corrected-from-cdxengine", "dynamic-unit-render", "static-shadow", "duplicate-queue-skip"},
    },
    "0x00554750": {
        "name": "CRenderQueue__EmitBillboardStrip",
        "signature": "void __thiscall CRenderQueue__EmitBillboardStrip(void * this, float x, float y, int z_bits, int w_bits, float scale, int count)",
        "tokens": ("this+0x594", "this+0x598", "CVBufTexture__AddVertices", "CVBufTexture__AddIndices"),
        "tags": {"projected-sprites", "owner-corrected-from-cdxengine", "billboard-strip", "static-shadow", "vbuftexture-write"},
    },
    "0x00554df0": {
        "name": "CRenderQueue__RenderVBufTextureWithStateToggle",
        "signature": "void __fastcall CRenderQueue__RenderVBufTextureWithStateToggle(void * this)",
        "tokens": ("0x0053e846", "0x009c7550", "CVBufTexture__Render(*(this+0x5b8), reset_after_render=1)", "stale CVBufTexture owner"),
        "tags": {"owner-corrected-from-cvbuftexture", "vbuftexture-render", "state-toggle", "field-5b8"},
    },
}

COMMON_TAGS = {
    "static-reaudit",
    "render-multipass-wave873",
    "wave873-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-reviewed",
    "owner-corrected",
    "important-renderer-infrastructure",
    "high-importance-low-local-evidence-density",
    "render-queue",
    "multipass-render",
}

CORE_ANCHORS = (
    TASK,
    "render-multipass-wave873",
    "0x00553960 CRenderQueue__RenderMultipassLayerA",
    "0x00554170 CRenderQueue__RenderMultipassLayerB",
    "0x005545d0 CRenderQueue__BuildProjectedSprites",
    "0x00554750 CRenderQueue__EmitBillboardStrip",
    "0x00554df0 CRenderQueue__RenderVBufTextureWithStateToggle",
    "0x009c7550",
    "0x004773ab",
    "0x004779b3",
    "CVBufTexture__RenderDynamicUnitPass",
    "high-importance, low local-evidence-density renderer infrastructure, not low-importance filler",
    NEXT_HEAD,
    STRICT_PROXY,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime multipass render behavior proven",
    "runtime projected-sprite visual behavior proven",
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
        "pre-xrefs.tsv": 6,
        "pre-instructions.tsv": 1385,
        "pre-decompile/index.tsv": 5,
        "pre-xref-site-instructions.tsv": 426,
        "pre-helper-metadata.tsv": 8,
        "post-metadata.tsv": 5,
        "post-tags.tsv": 5,
        "post-xrefs.tsv": 6,
        "post-instructions.tsv": 1385,
        "post-decompile/index.tsv": 5,
        "post-xref-site-instructions.tsv": 426,
        "post-helper-metadata.tsv": 8,
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
            for token in ("Wave873 render multipass static read-back", *expected["tokens"]):
                require(contains_token(row.get("comment", ""), token), f"missing comment token at {address}: {token}", failures)

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
    for token in ("0053e692", "0053e6af", "004773ab", "004779b3", "0055473a", "0053e846"):
        require(token in xref_text, f"missing xref token: {token}", failures)

    site_text = "\n".join("\t".join(row.values()) for row in read_tsv(BASE / "post-xref-site-instructions.tsv"))
    for token in ("MOV\tECX, 0x9c7550", "CALL\t0x00553960", "CALL\t0x00554170", "CALL\t0x005545d0", "CALL\t0x00554df0"):
        require(token in site_text, f"missing callsite token: {token}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=5 renamed=0 would_rename=5 signature_updated=3 comment_only_updated=2 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=5 skipped=0 renamed=5 would_rename=0 signature_updated=3 comment_only_updated=2 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=5 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=5 found=5 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=5 missing=0",
        "post-xrefs.log": "Wrote 6 rows",
        "post-instructions.log": "Wrote 1385 function-body instruction rows",
        "post-decompile.log": "targets=5 dumped=5 missing=0 failed=0",
        "post-xref-site-instructions.log": "targets=6 missing=0",
        "post-helper-metadata.log": "targets=8 found=8 missing=0",
        "quality-refresh.log": "total_functions=6106 commented_functions=5862",
        "queue-probe.log": "Commentless functions: 244",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave873.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave873_queue_probe.log",
    }
    for relative, token in expected.items():
        path = log_aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BADNAME:", "READBACK_BAD", "FAIL:", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)
    require(read_text(BASE / "apply.log").count("ApplyRenderMultipassWave873.java> READBACK_OK:") == 5, "apply readback count mismatch", failures)
    require("REPORT: Save succeeded" in read_text(BASE / "apply.log"), "missing save success token", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6106, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 244, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    for name in ("commentlessHighSignal", "signature", "nameConfidence"):
        require(queue["priorityQueues"][name] == [], f"{name} queue should be empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6106, "quality TSV row count mismatch", failures)
    require(commented == 5862, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5862, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x00554f80", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CAtmosphericsProfile__ctor", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 172526471 or backup.get("totalBytes") == 172526471.0, "backup byte count mismatch", failures)
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
    require(scripts.get("test:ghidra-render-multipass-wave873") == r"py -3 tools\ghidra_render_multipass_wave873_probe.py --check", "missing package script", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == TASK for row in ledger_rows), "missing Wave873 ledger row", failures)
    require(any(row.get("task") == TASK and row.get("attempt_id") == 20528 for row in attempts), "missing Wave873 attempt row", failures)


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
        print("Wave873 render multipass probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave873 render multipass probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
