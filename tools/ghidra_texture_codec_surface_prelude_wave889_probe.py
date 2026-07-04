#!/usr/bin/env python3
"""Validate Wave889 texture-codec/surface prelude read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave889-texture-codec-surface-prelude"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_texture_codec_surface_prelude_wave889_2026-05-26.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
DXTEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXTexture.cpp" / "_index.md"
TEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "texture.cpp" / "_index.md"
FASTVB_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FastVB.cpp" / "_index.md"
MATH_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Math.cpp" / "_index.md"
VERTEX_SHADER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "VertexShader.cpp" / "_index.md"
MESH_COLLISION_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "MeshCollisionVolume.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

TASK = "Wave889 texture codec surface prelude"
TAG = "texture-codec-surface-prelude-wave889"
BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260526-040930_post_wave889_texture_codec_surface_prelude_verified"
STRICT_PROXY = "6054/6113 = 99.03%"
NEXT_HEAD = "0x0057d0ee CWaypointManager__BoxBlurPackedColorRows_Scalar"

TARGETS = {
    "0x00579a9a": ("CVertexShader__CompileScriptWithDirectiveParser", "int CVertexShader__CompileScriptWithDirectiveParser(void)", ("directive parser", "script compile")),
    "0x00579b39": ("CDXTexture__LookupNamedFormatDescriptor", "int __stdcall CDXTexture__LookupNamedFormatDescriptor(void * format_name, uint required_flags, void * out_descriptor_or_null)", ("0x005e9340", "descriptor")),
    "0x00579bd5": ("CDXTexture__SetD3D9DebugMute", "void __stdcall CDXTexture__SetD3D9DebugMute(int mute_enabled)", ("DebugSetMute", "D3DXDoNotMute")),
    "0x00579cbe": ("CDXTexture__FreeSurfaceNodeTree", "void __fastcall CDXTexture__FreeSurfaceNodeTree(void * surface_node)", ("recursive", "ownership")),
    "0x00579e08": ("CDXTexture__DecodeBmpDibFromMemory", "int __thiscall CDXTexture__DecodeBmpDibFromMemory(void * this, void * dib_bytes, uint byte_count, void * unused_context)", ("BMP DIB", "surface-node")),
    "0x0057af0a": ("CDXTexture__DecodeJpegFromMemory", "int __stdcall CDXTexture__DecodeJpegFromMemory(void * encoded_bytes, int byte_count)", ("JPEG", "decode")),
    "0x0057b9ce": ("CDXTexture__DecodePngFromMemory", "int __stdcall CDXTexture__DecodePngFromMemory(void * encoded_bytes, int byte_count)", ("PNG", "decode")),
    "0x0057bf1f": ("CDXTexture__BuildDdsSurfaceNodeTree", "int __thiscall CDXTexture__BuildDdsSurfaceNodeTree(void * this, void * dds_bytes, uint byte_count, void * unused_context)", ("DDS", "surface-node")),
    "0x0057c7a4": ("CMeshCollisionVolume__LoadMappedTextureResourcesByMode", "int __thiscall CMeshCollisionVolume__LoadMappedTextureResourcesByMode(void * this, void * mapped_resource_name_or_path, int output_mode, int open_mode_flags, int unused_arg3)", ("output_mode", "BMP/JPEG/DDS")),
    "0x0057ca6a": ("CDXTexture__DecodeFromMemory_WithFallbackCodecs", "int CDXTexture__DecodeFromMemory_WithFallbackCodecs(void)", ("BMP, PPM, DDS, JPEG, PNG, TGA, and DIB", "stack-locked")),
    "0x0057cca4": ("CFastVB__BuildResampleKernelBuckets", "int * __stdcall CFastVB__BuildResampleKernelBuckets(uint output_count, int source_count, int clamp_edges)", ("resample", "bucket")),
    "0x0057cf60": ("CDXTexture__CopyDxtBlockRegion", "int __fastcall CDXTexture__CopyDxtBlockRegion(void * copy_context)", ("DXT", "4x4")),
}

ALL_TARGET_COUNT = 27
COMMON_TAGS = {
    "static-reaudit",
    TAG,
    "wave889-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-verified",
    "texture-codec-surface-prelude",
    "important-render-infrastructure",
    "raw-commentless-tail",
}

CORE_ANCHORS = (
    TASK,
    TAG,
    "0x00579a9a CVertexShader__CompileScriptWithDirectiveParser",
    "0x00579b39 CDXTexture__LookupNamedFormatDescriptor",
    "0x00579e08 CDXTexture__DecodeBmpDibFromMemory",
    "0x0057ca6a CDXTexture__DecodeFromMemory_WithFallbackCodecs",
    "0x0057c7a4 CMeshCollisionVolume__LoadMappedTextureResourcesByMode",
    "0x0057cca4 CFastVB__BuildResampleKernelBuckets",
    "0x0057cf60 CDXTexture__CopyDxtBlockRegion",
    NEXT_HEAD,
    STRICT_PROXY,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "fully reverse-engineered",
    "rebuild parity proven",
    "exact texture layout proven",
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
        "targets-snapshot.tsv": ALL_TARGET_COUNT,
        "pre-metadata.tsv": ALL_TARGET_COUNT,
        "pre-tags.tsv": ALL_TARGET_COUNT,
        "pre-xrefs.tsv": 74,
        "pre-instructions.tsv": 4329,
        "pre-decompile/index.tsv": ALL_TARGET_COUNT,
        "post-metadata.tsv": ALL_TARGET_COUNT,
        "post-tags.tsv": ALL_TARGET_COUNT,
        "post-xrefs.tsv": 74,
        "post-instructions.tsv": 4329,
        "post-decompile/index.tsv": ALL_TARGET_COUNT,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    for address, (name, signature, tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            comment = row.get("comment", "")
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in ("Wave889 static read-back", "Static retail Ghidra evidence only", "remain unproven", *tokens):
                require(token in comment, f"missing comment token at {address}: {token}", failures)

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


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=27 renamed=0 would_rename=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=27 skipped=0 renamed=0 would_rename=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=27 renamed=0 would_rename=0 missing=0 bad=0",
        "post-metadata.log": "targets=27 found=27 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=27 missing=0",
        "post-xrefs.log": "Wrote 74 rows",
        "post-instructions.log": "Wrote 4329 function-body instruction rows",
        "post-decompile.log": "targets=27 dumped=27 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6113 commented_functions=6054",
        "queue-probe.log": "Commentless functions: 59",
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave889.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave889_queue_probe.log",
    }
    for relative, token in expected.items():
        path = aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BAD:", "MISSING:", "BADNAME:", "BADSIG:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6113, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 59, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(commented == 6054, "quality TSV commented count mismatch", failures)
    require(strict_clean == 6054, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x0057d0ee", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CWaypointManager__BoxBlurPackedColorRows_Scalar", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 173149063, "backup byte count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        DXTEXTURE_DOC,
        TEXTURE_DOC,
        FASTVB_DOC,
        MATH_DOC,
        VERTEX_SHADER_DOC,
        MESH_COLLISION_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in docs:
        text = read_text(path)
        for token in CORE_ANCHORS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:ghidra-texture-codec-surface-prelude-wave889")
        == r"py -3 tools\ghidra_texture_codec_surface_prelude_wave889_probe.py --check",
        "missing package script",
        failures,
    )
    require(any(row.get("task") == TASK for row in read_jsonl(LEDGER)), "missing Wave889 ledger row", failures)
    require(any(row.get("task") == TASK and row.get("attempt_id") == 20544 for row in read_jsonl(ATTEMPT_LOG)), "missing Wave889 attempt row", failures)


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
        print("Wave889 texture-codec/surface prelude probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave889 texture-codec/surface prelude probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
