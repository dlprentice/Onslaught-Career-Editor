#!/usr/bin/env python3
"""Validate Wave877 water-render tail read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave877-water-render-tail"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_water_render_tail_wave877_2026-05-25.md"
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

TASK = "Wave877 water render tail"
BACKUP_PATH = r"G:\GhidraBackups\BEA_20260525-215011_post_wave877_water_render_tail_verified"
NEXT_HEAD = "0x0055d731 CRT__SehDispatchWithScopeTable_Thunk_0055d731"
STRICT_PROXY = "5893/6113 = 96.40%"

TARGETS = {
    "0x0055b0e0": ("CWaterRenderSystem__ctor", "void * __fastcall CWaterRenderSystem__ctor(void * this)", ("CWaterRenderSystem constructor", "CEngine__Init", "this+0x3ab8")),
    "0x0055b140": ("CWaterRenderSystem__scalar_deleting_dtor", "void * __thiscall CWaterRenderSystem__scalar_deleting_dtor(void * this, int free_flag)", ("vtable DATA row 0x005e5a70", "CDXMemoryManager__Free")),
    "0x0055b160": ("CWaterRenderSystem__dtor", "void __fastcall CWaterRenderSystem__dtor(void * this)", ("DAT_009cc21c", "CShaderBase__UnlinkFromRenderObjectLists", "DeviceObject__dtor_body")),
    "0x0055b230": ("CWaterRenderSystem__LoadTextures", "void __fastcall CWaterRenderSystem__LoadTextures(void * this)", ("mixers\\reflection%.2d.tga", "mixers\\caustic%.2d.tga", "sunreflect.tga")),
    "0x0055b330": ("CWaterRenderSystem__ReloadTextures", "void __fastcall CWaterRenderSystem__ReloadTextures(void * this, void * reload_target)", ("CEngine__SetWater", "reload_target/EDX", "CWaterRenderSystem__LoadTextures")),
    "0x0055b440": ("CWaterRenderSystem__BuildGridVBuf", "void __stdcall CWaterRenderSystem__BuildGridVBuf(int world_matrix, int texture_a, float p3, float p4, float p5)", ("Creating water VBuf", "0x18 by 0x18 grid", "25x25 vertex grid")),
    "0x0055b660": ("CWaterRenderSystem__RenderShadowPass", "void __thiscall CWaterRenderSystem__RenderShadowPass(void * this)", ("CDXLandscape__RenderShadowMap", "CVBufTexture__RenderIndexedNoValidate")),
    "0x0055b6c0": ("CWaterRenderSystem__RenderMainPass", "void __fastcall CWaterRenderSystem__RenderMainPass(void * this)", ("CDXEngine__Render", "CDXTexture__GetAnimatedFrame", "CVBufTexture__RenderIndexed")),
}

COMMON_TAGS = {
    "static-reaudit",
    "water-render-tail-wave877",
    "wave877-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-verified",
    "important-water-render-infrastructure",
    "high-importance-low-local-evidence-density",
    "water-render",
    "render-resource",
    "raw-commentless-head",
}

STRING_EXPECTATIONS = {
    "string-00652a54.tsv": r"mixers\reflection%.2d.tga",
    "string-00652a3c.tsv": r"mixers\caustic%.2d.tga",
    "string-00652a30.tsv": "sunblob.tga",
    "string-00652a20.tsv": "sunreflect.tga",
    "string-00652f50.tsv": r"Creating water VBuf\x0a",
}

XREF_EXPECTATIONS = {
    "0x0055b0e0": ("0x00449b7f", "CEngine__Init"),
    "0x0055b140": ("0x005e5a70", "<no_function>"),
    "0x0055b160": ("0x0055b143", "CWaterRenderSystem__scalar_deleting_dtor"),
    "0x0055b230": ("0x0055b38b", "CWaterRenderSystem__ReloadTextures"),
    "0x0055b330": ("0x0044a2c8", "CEngine__SetWater"),
    "0x0055b440": ("0x0055b674", "CWaterRenderSystem__RenderShadowPass"),
    "0x0055b660": ("0x00546795", "CDXLandscape__RenderShadowMap"),
    "0x0055b6c0": ("0x0053e6f1", "CDXEngine__Render"),
}

CORE_ANCHORS = (
    TASK,
    "water-render-tail-wave877",
    "0x0055b0e0 CWaterRenderSystem__ctor",
    "0x0055b230 CWaterRenderSystem__LoadTextures",
    "0x0055b440 CWaterRenderSystem__BuildGridVBuf",
    "0x0055b6c0 CWaterRenderSystem__RenderMainPass",
    r"mixers\reflection%.2d.tga",
    "sunreflect.tga",
    "high-importance water/render connector rows with low local evidence density, not low-importance filler",
    NEXT_HEAD,
    STRICT_PROXY,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime water visual behavior proven",
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
        "pre-metadata.tsv": 8,
        "pre-tags.tsv": 8,
        "pre-xrefs.tsv": 12,
        "pre-instructions.tsv": 2371,
        "pre-decompile/index.tsv": 8,
        "pre-context-metadata.tsv": 9,
        "pre-context-decompile/index.tsv": 9,
        "post-metadata.tsv": 8,
        "post-tags.tsv": 8,
        "post-xrefs.tsv": 12,
        "post-instructions.tsv": 2371,
        "post-decompile/index.tsv": 8,
        "post-context-metadata.tsv": 9,
        "post-context-decompile/index.tsv": 9,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    for relative, expected in STRING_EXPECTATIONS.items():
        rows = read_tsv(BASE / relative)
        require(rows and rows[0].get("cstring") == expected, f"{relative} string mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    for address, (name, signature, tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing post metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            require("Wave877 static read-back" in row.get("comment", ""), f"missing Wave877 comment at {address}", failures)
            for token in tokens:
                require(contains_token(row.get("comment", ""), token), f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing post tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"tags missing at {address}: {COMMON_TAGS - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing post decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    xrefs = read_tsv(BASE / "post-xrefs.tsv")
    xref_text = read_text(BASE / "post-xrefs.tsv")
    for address, (from_addr, from_function) in XREF_EXPECTATIONS.items():
        require(
            any(normalize_address(row.get("target_addr", "")) == address and normalize_address(row.get("from_addr", "")) == from_addr for row in xrefs),
            f"missing xref {from_addr} -> {address}",
            failures,
        )
        require(from_function in xref_text, f"missing xref function token: {from_function}", failures)
    for token in ("0x0055c1a8", "0x0055cf00", "0x0055d0ad", "0x0053e803"):
        require(token[2:] in xref_text, f"missing secondary xref token: {token}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=8 renamed=0 would_rename=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=8 skipped=0 renamed=0 would_rename=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=8 renamed=0 would_rename=0 missing=0 bad=0",
        "post-metadata.log": "targets=8 found=8 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=8 missing=0",
        "post-xrefs.log": "Wrote 12 rows",
        "post-instructions.log": "Wrote 2371 function-body instruction rows",
        "post-decompile.log": "targets=8 dumped=8 missing=0 failed=0",
        "post-context-metadata.log": "targets=9 found=9 missing=0",
        "post-context-decompile.log": "targets=9 dumped=9 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6113 commented_functions=5893",
        "queue-probe.log": "Commentless functions: 220",
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave877.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave877_queue_probe.log",
    }
    for relative, token in expected.items():
        path = aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6113, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 220, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    rows = read_tsv(QUEUE_TSV)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x0055d731", "raw head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CRT__SehDispatchWithScopeTable_Thunk_0055d731", "raw head name mismatch", failures)

    commented, strict_clean = signature_counts(rows)
    require(len(rows) == 6113, "quality TSV row count mismatch", failures)
    require(commented == 5893, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5893, "strict clean count mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 172690311 or backup.get("totalBytes") == 172690311.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
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
    for path in docs:
        text = read_text(path)
        for token in CORE_ANCHORS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(scripts.get("test:ghidra-water-render-tail-wave877") == r"py -3 tools\ghidra_water_render_tail_wave877_probe.py --check", "missing package script", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == TASK for row in ledger_rows), "missing Wave877 ledger row", failures)
    require(any(row.get("task") == TASK for row in attempts), "missing Wave877 attempt row", failures)


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
        print("Wave877 water-render tail probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave877 water-render tail probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
