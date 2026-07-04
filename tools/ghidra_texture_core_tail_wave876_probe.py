#!/usr/bin/env python3
"""Validate Wave876 texture-core tail read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave876-texture-core-tail"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_texture_core_tail_wave876_2026-05-25.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
TEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "texture.cpp" / "_index.md"
DXTEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXTexture.cpp" / "_index.md"
VBUFTEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "vbuftexture.cpp" / "_index.md"
ENGINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "engine.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

TASK = "Wave876 texture core tail"
BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260525-212045_post_wave876_texture_core_tail_verified"
NEXT_HEAD = "0x0055b0e0 CWaterRenderSystem__ctor"
STRICT_PROXY = "5885/6113 = 96.27%"

TARGETS = {
    "0x00556cc0": ("CTexture__ctor", "void * __fastcall CTexture__ctor(void * this)", ("CTextureBase__Init", "CDXSurf__vtable", "Xrefs include CTexture__FindTexture")),
    "0x00556f50": ("CTexture__Release", "void __fastcall CTexture__Release(void * this)", ("cached render-state slots 0-3", "first vtable slot with delete/release flag 1")),
    "0x00557060": ("CTextureSequence__EnsureLoaded", "int __fastcall CTextureSequence__EnsureLoaded(void * this)", ("DAT_00888c8c", "this+0x14c", "creates the texture at this+0xb8")),
    "0x005572c0": ("CTextureSequence__ReleaseIfLoaded", "int __fastcall CTextureSequence__ReleaseIfLoaded(void * this)", ("this+0xb8", "vtable slot +0x08")),
    "0x00557a00": ("CDXTexture__FormatToString", "char * __cdecl CDXTexture__FormatToString(int format)", ("UNKNOWN", "A1R5G5B5", "Q8W8V8U8")),
    "0x00557a90": ("CDXTexture__LoadTextureFromFile_Core", "int __fastcall CDXTexture__LoadTextureFromFile_Core(void * this)", ("data\\Textures", "CDXTexture__DecodeMappedFileToTexture", "unaff_EBX")),
    "0x00558690": ("CDXTexture__GetAnimatedFrame", "void * __fastcall CDXTexture__GetAnimatedFrame(void * this)", ("53 xrefs", "this+0x138", "frame*4")),
    "0x00558870": ("CDXTexture__DumpAllTexturesToTga", "void __cdecl CDXTexture__DumpAllTexturesToTga(void)", ("TextureDump", "DAT_0083d9b0", "CDXTexture__DumpTextureToRGBA")),
    "0x005588f0": ("CVBufTexture__RenderModePass", "int __fastcall CVBufTexture__RenderModePass(void * this)", ("CVBufTexture__DrawSpriteEx", "modes 0-5", "D3DStateCache")),
    "0x00558ef0": ("CVBufTexture__SetupSecondaryBlend", "int __cdecl CVBufTexture__SetupSecondaryBlend(int alpha)", ("CDXTexture__IsResourceHandleValid", "DAT_009cc118", "alpha<<24")),
    "0x0055a0f0": ("CEngine__TextureFormatIndexToD3D", "int __cdecl CEngine__TextureFormatIndexToD3D(int format_index)", ("0x31545844", "0x32545844", "0x34545844")),
    "0x0055a170": ("CEngine__TextureFormatD3DToIndex", "int __cdecl CEngine__TextureFormatD3DToIndex(int d3d_format)", ("CEngine__TextureFormatField32FD4ToIndex", "indices 1-10")),
}

COMMON_TAGS = {
    "static-reaudit",
    "texture-core-tail-wave876",
    "wave876-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "important-texture-render-infrastructure",
    "high-importance-low-local-evidence-density",
    "texture-core",
    "render-resource",
    "raw-commentless-head",
}

CORE_ANCHORS = (
    TASK,
    "texture-core-tail-wave876",
    "0x00556cc0 CTexture__ctor",
    "0x00557a90 CDXTexture__LoadTextureFromFile_Core",
    "0x00558690 CDXTexture__GetAnimatedFrame",
    "0x005588f0 CVBufTexture__RenderModePass",
    "0x0055a0f0 CEngine__TextureFormatIndexToD3D",
    "high-importance texture/resource/render connector rows with low local evidence density, not low-importance filler",
    NEXT_HEAD,
    STRICT_PROXY,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime texture load/decode/animation/render/dump behavior proven",
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
        "pre-metadata.tsv": 12,
        "pre-tags.tsv": 12,
        "pre-xrefs.tsv": 86,
        "pre-instructions.tsv": 1491,
        "pre-decompile/index.tsv": 12,
        "pre-context-metadata.tsv": 10,
        "pre-context-decompile/index.tsv": 10,
        "post-metadata.tsv": 12,
        "post-tags.tsv": 12,
        "post-xrefs.tsv": 86,
        "post-instructions.tsv": 1491,
        "post-decompile/index.tsv": 12,
        "post-context-metadata.tsv": 10,
        "post-context-decompile/index.tsv": 10,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

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
            require("Wave876 static read-back" in row.get("comment", ""), f"missing Wave876 comment at {address}", failures)
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

    xref_text = read_text(BASE / "post-xrefs.tsv")
    for token in ("CTexture__FindTexture", "CDXBattleLine__Constructor", "CDXCompass__Init", "con_dumptextures", "CMeshRenderer__RenderMeshWithLayerPasses", "CWaterRenderSystem__RenderMainPass"):
        require(token in xref_text, f"missing xref token: {token}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=12 renamed=0 would_rename=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=12 skipped=0 renamed=0 would_rename=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=12 renamed=0 would_rename=0 missing=0 bad=0",
        "post-metadata.log": "targets=12 found=12 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=12 missing=0",
        "post-xrefs.log": "Wrote 86 rows",
        "post-instructions.log": "Wrote 1491 function-body instruction rows",
        "post-decompile.log": "targets=12 dumped=12 missing=0 failed=0",
        "post-context-metadata.log": "targets=10 found=10 missing=0",
        "post-context-decompile.log": "targets=10 dumped=10 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6113 commented_functions=5885",
        "queue-probe.log": "Commentless functions: 228",
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave876.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave876_queue_probe.log",
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
    require(quality["commentlessFunctionCount"] == 228, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    rows = read_tsv(QUEUE_TSV)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x0055b0e0", "raw head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CWaterRenderSystem__ctor", "raw head name mismatch", failures)

    commented, strict_clean = signature_counts(rows)
    require(len(rows) == 6113, "quality TSV row count mismatch", failures)
    require(commented == 5885, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5885, "strict clean count mismatch", failures)

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
        TEXTURE_DOC,
        DXTEXTURE_DOC,
        VBUFTEXTURE_DOC,
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
    require(scripts.get("test:ghidra-texture-core-tail-wave876") == r"py -3 tools\ghidra_texture_core_tail_wave876_probe.py --check", "missing package script", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == TASK for row in ledger_rows), "missing Wave876 ledger row", failures)
    require(any(row.get("task") == TASK for row in attempts), "missing Wave876 attempt row", failures)


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
        print("Wave876 texture-core tail probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave876 texture-core tail probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
