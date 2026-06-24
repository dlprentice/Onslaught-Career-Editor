#!/usr/bin/env python3
"""Validate Wave662 CDXTexture image-codec read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave662-cdxtexture-image-codec"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cdxtexture_image_codec_wave662_2026-05-21.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
DXTEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXTexture.cpp" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
TRACKING = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"

COMMON_TAGS = {
    "cdxtexture-image-codec-wave662",
    "wave662-readback-verified",
    "static-reaudit",
    "retail-binary-evidence",
    "signature-hardened",
    "comment-hardened",
}

TARGETS = {
    "0x00579b39": {
        "name": "CDXTexture__LookupNamedFormatDescriptor",
        "signature": "int __stdcall CDXTexture__LookupNamedFormatDescriptor(void * format_name, uint required_flags, void * out_descriptor_or_null)",
        "tags": {"binary-search", "format-descriptor"},
        "comment_tokens": ("named format descriptor table", "requested flag mask", "D3D-style success/failure codes"),
        "decompile": "00579b39_CDXTexture__LookupNamedFormatDescriptor.c",
    },
    "0x00579bd5": {
        "name": "CDXTexture__SetD3D9DebugMute",
        "signature": "void __stdcall CDXTexture__SetD3D9DebugMute(int mute_enabled)",
        "tags": {"d3d-debug", "debugsetmute"},
        "comment_tokens": ("DebugSetMute", "d3d9.dll/d3d9d.dll", "registry/config flag"),
        "decompile": "00579bd5_CDXTexture__SetD3D9DebugMute.c",
    },
    "0x00579ca5": {
        "name": "CDXTexture__InitSurfaceNodeZeroed",
        "signature": "void __fastcall CDXTexture__InitSurfaceNodeZeroed(void * surface_node)",
        "tags": {"initializer", "surface-node"},
        "comment_tokens": ("surface-node root pointers", "ownership flags", "child links"),
        "decompile": "00579ca5_CDXTexture__InitSurfaceNodeZeroed.c",
    },
    "0x00579cbe": {
        "name": "CDXTexture__FreeSurfaceNodeTree",
        "signature": "void __fastcall CDXTexture__FreeSurfaceNodeTree(void * surface_node)",
        "tags": {"recursive-free", "surface-node"},
        "comment_tokens": ("owned primary/secondary buffers", "ownership flags", "recursively frees"),
        "decompile": "00579cbe_CDXTexture__FreeSurfaceNodeTree.c",
    },
    "0x00579d17": {
        "name": "CDXTexture__SurfaceNode_scalar_deleting_dtor",
        "signature": "void * __thiscall CDXTexture__SurfaceNode_scalar_deleting_dtor(void * this, uint delete_flags, int unused_arg1)",
        "tags": {"scalar-deleting-dtor", "surface-node"},
        "comment_tokens": ("scalar-deleting destructor wrapper", "bit 0 of delete_flags", "second recovered argument is unused"),
        "decompile": "00579d17_CDXTexture__SurfaceNode_scalar_deleting_dtor.c",
    },
    "0x00579d33": {
        "name": "CDXTexture__InitSurfaceFormatInfoFromDescriptor",
        "signature": "int __thiscall CDXTexture__InitSurfaceFormatInfoFromDescriptor(void * this, void * descriptor_row, void * unused_context)",
        "tags": {"format-descriptor", "surface-node"},
        "comment_tokens": ("copies descriptor identity", "six extent/stride fields", "recomputes width/height/depth"),
        "decompile": "00579d33_CDXTexture__InitSurfaceFormatInfoFromDescriptor.c",
    },
    "0x00579e08": {
        "name": "CDXTexture__DecodeBmpDibFromMemory",
        "signature": "int __thiscall CDXTexture__DecodeBmpDibFromMemory(void * this, void * dib_bytes, uint byte_count, void * unused_context)",
        "tags": {"bmp", "dib-decode", "surface-node"},
        "comment_tokens": ("BMP DIB header", "palette data", "decoded pixel/palette buffers"),
        "decompile": "00579e08_CDXTexture__DecodeBmpDibFromMemory.c",
    },
    "0x0057a934": {
        "name": "CDXTexture__WriteSurfaceAsBmpToHandle",
        "signature": "int __thiscall CDXTexture__WriteSurfaceAsBmpToHandle(void * this, void * file_handle, int write_enabled, int unused_arg2)",
        "tags": {"bmp", "surface-export", "writefile"},
        "comment_tokens": ("BMP file/DIB headers", "optional palette/header/pixel rows", "WriteFile"),
        "decompile": "0057a934_CDXTexture__WriteSurfaceAsBmpToHandle.c",
    },
    "0x0057af0a": {
        "name": "CDXTexture__DecodeJpegFromMemory",
        "signature": "int __stdcall CDXTexture__DecodeJpegFromMemory(void * encoded_bytes, int byte_count)",
        "tags": {"jpeg", "memory-decode"},
        "comment_tokens": ("JPEG decode pipeline", "memory input callbacks", "scanlines"),
        "decompile": "0057af0a_CDXTexture__DecodeJpegFromMemory.c",
    },
    "0x0057b182": {
        "name": "CDXTexture__DecodeTgaFromMemory",
        "signature": "int __thiscall CDXTexture__DecodeTgaFromMemory(void * this, void * encoded_bytes, uint byte_count, uint unused_context)",
        "tags": {"tga", "memory-decode", "surface-node"},
        "comment_tokens": ("TGA header/type/depth fields", "palette and direct-color cases", "origin/orientation bits"),
        "decompile": "0057b182_CDXTexture__DecodeTgaFromMemory.c",
    },
    "0x0057b6fa": {
        "name": "CDXTexture__DecodePpmFromMemory",
        "signature": "uint __thiscall CDXTexture__DecodePpmFromMemory(void * this, void * encoded_bytes, uint byte_count, uint unused_context)",
        "tags": {"ppm", "memory-decode", "surface-node"},
        "comment_tokens": ("P3/P6 PPM headers", "declared max value", "opaque alpha"),
        "decompile": "0057b6fa_CDXTexture__DecodePpmFromMemory.c",
    },
    "0x0057b9ce": {
        "name": "CDXTexture__DecodePngFromMemory",
        "signature": "int __stdcall CDXTexture__DecodePngFromMemory(void * encoded_bytes, int byte_count)",
        "tags": {"png", "memory-decode"},
        "comment_tokens": ("PNG signature", "PNG/inflate decode contexts", "bit-depth/palette/gamma/alpha transforms"),
        "decompile": "0057b9ce_CDXTexture__DecodePngFromMemory.c",
    },
    "0x0057bf1f": {
        "name": "CDXTexture__BuildDdsSurfaceNodeTree",
        "signature": "int __thiscall CDXTexture__BuildDdsSurfaceNodeTree(void * this, void * dds_bytes, uint byte_count, void * unused_context)",
        "tags": {"dds", "mip-chain", "surface-node"},
        "comment_tokens": ("DDS magic/header fields", "format descriptor", "linked surface-node tree"),
        "decompile": "0057bf1f_CDXTexture__BuildDdsSurfaceNodeTree.c",
    },
    "0x0057c28b": {
        "name": "CDXTexture__WriteDdsSurfaceChainToHandle",
        "signature": "int __thiscall CDXTexture__WriteDdsSurfaceChainToHandle(void * this, void * file_handle, int write_enabled)",
        "tags": {"dds", "surface-export", "writefile"},
        "comment_tokens": ("surface-node chain levels/faces", "DDS magic/header", "surface row/block"),
        "decompile": "0057c28b_CDXTexture__WriteDdsSurfaceChainToHandle.c",
    },
    "0x0057c57d": {
        "name": "CDXTexture__FlushStreamWriteBufferChunk",
        "signature": "int __stdcall CDXTexture__FlushStreamWriteBufferChunk(void * stream_context)",
        "tags": {"jpeg", "stream-write", "writefile"},
        "comment_tokens": ("0x1000-byte stream buffer", "WriteFile", "remaining-byte fields"),
        "decompile": "0057c57d_CDXTexture__FlushStreamWriteBufferChunk.c",
    },
    "0x0057c5b2": {
        "name": "CDXTexture__FlushStreamWriteBufferTail",
        "signature": "void __stdcall CDXTexture__FlushStreamWriteBufferTail(void * stream_context)",
        "tags": {"jpeg", "stream-write", "writefile"},
        "comment_tokens": ("pending tail bytes", "stream buffer", "partially filled"),
        "decompile": "0057c5b2_CDXTexture__FlushStreamWriteBufferTail.c",
    },
    "0x0057c5dc": {
        "name": "CDXTexture__EncodeRgbBufferToJpegStream",
        "signature": "int __thiscall CDXTexture__EncodeRgbBufferToJpegStream(void * this, void * file_handle, int unused_arg1)",
        "tags": {"jpeg", "stream-encode", "writefile"},
        "comment_tokens": ("JPEG encoder callbacks", "WriteFile-backed stream", "RGB triples"),
        "decompile": "0057c5dc_CDXTexture__EncodeRgbBufferToJpegStream.c",
    },
    "0x0057ca3a": {
        "name": "CDXTexture__DecodeBmpFromMemory",
        "signature": "int __thiscall CDXTexture__DecodeBmpFromMemory(void * this, void * bmp_bytes, uint byte_count, uint unused_context)",
        "tags": {"bmp", "memory-decode"},
        "comment_tokens": ("BMP file header", "payload length", "DecodeBmpDibFromMemory"),
        "decompile": "0057ca3a_CDXTexture__DecodeBmpFromMemory.c",
    },
    "0x0057cc53": {
        "name": "CDXTexture__InitMappedFileContext",
        "signature": "void __fastcall CDXTexture__InitMappedFileContext(void * surface_pair)",
        "tags": {"initializer", "surface-pair"},
        "comment_tokens": ("two-pointer surface-pair", "mapped-file context", "clearing both interface slots"),
        "decompile": "0057cc53_CDXTexture__InitMappedFileContext.c",
    },
    "0x0057cc5d": {
        "name": "CDXTexture__ReleaseSurfacePairIfPresent",
        "signature": "void __fastcall CDXTexture__ReleaseSurfacePairIfPresent(void * surface_pair)",
        "tags": {"release", "surface-pair"},
        "comment_tokens": ("two observed interface slots", "vtable slot 0", "exact COM/interface identity"),
        "decompile": "0057cc5d_CDXTexture__ReleaseSurfacePairIfPresent.c",
    },
    "0x0057cf60": {
        "name": "CDXTexture__CopyDxtBlockRegion",
        "signature": "int __fastcall CDXTexture__CopyDxtBlockRegion(void * copy_context)",
        "tags": {"block-copy", "dxt"},
        "comment_tokens": ("DXT block alignment", "DXT1 8-byte or DXT2-5 16-byte blocks", "row/depth strides"),
        "decompile": "0057cf60_CDXTexture__CopyDxtBlockRegion.c",
    },
}

DOC_TOKENS = (
    "Wave662 CDXTexture image codec hardening",
    "cdxtexture-image-codec-wave662",
    "0x00579b39 CDXTexture__LookupNamedFormatDescriptor",
    "0x0057cf60 CDXTexture__CopyDxtBlockRegion",
    "0x0057c7a4 CMeshCollisionVolume__LoadMappedTextureResourcesByMode",
)

OVERCLAIM_TOKENS = (
    "fully reverse-engineered",
    "fully recovered",
    "runtime image fidelity proven",
    "runtime upload behavior proven",
    "runtime export behavior proven",
    "exact CDXTexture layout proven",
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
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    for line in read_text(path).splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def check_metadata(failures: list[str]) -> None:
    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile_index = {normalize_address(row["address"]): row for row in read_tsv(BASE / "decompile-post" / "index.tsv")}

    require(len(metadata) == len(TARGETS), f"metadata row count is {len(metadata)}", failures)
    require(len(tags) == len(TARGETS), f"tag row count is {len(tags)}", failures)
    require(len(decompile_index) == len(TARGETS), f"decompile index row count is {len(decompile_index)}", failures)

    for address, expected in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is None:
            continue
        require(row.get("name") == expected["name"], f"name mismatch at {address}: {row.get('name')}", failures)
        require(row.get("signature") == expected["signature"], f"signature mismatch at {address}: {row.get('signature')}", failures)
        require(row.get("status") == "OK", f"metadata status mismatch at {address}: {row.get('status')}", failures)
        comment = row.get("comment", "")
        require("Wave662 static read-back" in comment, f"missing Wave662 comment at {address}", failures)
        require("Static metadata only" in comment, f"missing uncertainty clause at {address}", failures)
        for token in expected["comment_tokens"]:
            require(token in comment, f"comment token {token!r} missing at {address}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"common tags missing at {address}: {actual_tags}", failures)
            require(expected["tags"].issubset(actual_tags), f"specific tags missing at {address}: {actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}: {tag_row.get('status')}", failures)

        decompile_row = decompile_index.get(address)
        require(decompile_row is not None, f"missing decompile index for {address}", failures)
        if decompile_row is not None:
            require(decompile_row.get("signature") == expected["signature"], f"decompile signature mismatch at {address}", failures)
            require(decompile_row.get("status") == "OK", f"decompile status mismatch at {address}", failures)
        require((BASE / "decompile-post" / expected["decompile"]).is_file(), f"missing decompile file {expected['decompile']}", failures)


def check_logs(failures: list[str]) -> None:
    expected_exact = {
        "apply-wave662-dry2.log": "SUMMARY: updated=0 skipped=21 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0",
        "apply-wave662-apply2.log": "SUMMARY: updated=21 skipped=0 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0",
        "apply-wave662-final-dry.log": "SUMMARY: updated=0 skipped=21 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=21 found=21 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=21 missing=0",
        "post-decompile.log": "targets=21 dumped=21 missing=0 failed=0",
        "post-instructions.log": "targets=21 missing=0",
        "post-xrefs.log": "Wrote 59 rows",
    }
    for filename, token in expected_exact.items():
        text = read_text(BASE / filename)
        require(token in text, f"log token missing in {filename}: {token}", failures)
        require("REPORT: Save succeeded" in text, f"save report missing in {filename}", failures)
        require("LockException" not in text, f"LockException found in {filename}", failures)
        require("ERROR REPORT SCRIPT ERROR" not in text, f"script error found in {filename}", failures)
        require("BAD:" not in text and "BADNAME:" not in text and "MISSING:" not in text, f"bad/missing marker found in {filename}", failures)

    instructions = read_text(BASE / "post-instructions.log")
    require("Wrote 2793 instruction rows" in instructions, "instruction row count mismatch", failures)

    stale_apply = read_text(BASE / "apply-wave662-apply.log")
    require("bad=10" in stale_apply, "expected superseded apply log not found", failures)
    require("bad=10" not in read_text(BASE / "apply-wave662-apply2.log"), "accepted apply2 contains stale bad count", failures)


def check_docs(failures: list[str]) -> None:
    package = read_json(PACKAGE_JSON)
    require("test:ghidra-cdxtexture-image-codec-wave662" in package.get("scripts", {}), "package script missing", failures)

    for path in (PUBLIC_NOTE, FUNCTION_INDEX, DXTEXTURE_DOC, GHIDRA_REFERENCE, CAMPAIGN, BACKLOG):
        text = read_text(path)
        for token in DOC_TOKENS:
            require(token in text, f"{token!r} missing from {path.relative_to(ROOT)}", failures)
        for token in OVERCLAIM_TOKENS:
            require(token not in text, f"overclaim token {token!r} found in {path.relative_to(ROOT)}", failures)

    for path in (LEDGER, ATTEMPT_LOG):
        text = read_text(path)
        require("Wave662 CDXTexture image codec hardening" in text, f"Wave662 missing from {path.relative_to(ROOT)}", failures)
        require("cdxtexture-image-codec-wave662" in text, f"Wave662 tag missing from {path.relative_to(ROOT)}", failures)


def check_state(failures: list[str]) -> None:
    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("diffCount") == 0, "backup diffCount mismatch", failures)
    require(backup.get("fileCount") == 19, "backup fileCount mismatch", failures)
    require(backup.get("byteCount") == 163449735.0, "backup byteCount mismatch", failures)
    require("post_wave662_cdxtexture_image_codec_verified" in backup.get("backupPath", ""), "backup path mismatch", failures)

    queue = read_json(QUEUE_JSON)
    require(queue.get("totalFunctions") == 6098, "queue total mismatch", failures)
    signals = queue.get("qualitySignals", {})
    require(signals.get("commentlessFunctionCount") == 2454, "queue commentless mismatch", failures)
    require(signals.get("undefinedSignatureCount") == 1217, "queue undefined-signature mismatch", failures)
    require(signals.get("paramSignatureCount") == 673, "queue param_N mismatch", failures)
    head = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(head.get("address") == "0x0057c7a4", f"queue head address mismatch: {head}", failures)
    require(head.get("name") == "CMeshCollisionVolume__LoadMappedTextureResourcesByMode", f"queue head name mismatch: {head}", failures)

    ledger = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(ledger[-1].get("task") == "Wave662 CDXTexture image codec hardening", "ledger last row mismatch", failures)
    require(attempts[-1].get("task") == "Wave662 CDXTexture image codec hardening", "attempt task mismatch", failures)
    require(attempts[-1].get("attempt_id") == 20317, "attempt id mismatch", failures)
    require(len(ledger) == 1058, "ledger row count mismatch", failures)
    require(len(attempts) == 20318, "attempt row count mismatch", failures)

    tracking = read_json(TRACKING)
    counters = tracking.get("counters", {})
    require(tracking.get("current_focus", "").startswith("Wave662 CDXTexture image codec hardening"), "tracking current_focus mismatch", failures)
    require(counters.get("ledger_rows") == 1058, "tracking ledger_rows mismatch", failures)
    require(counters.get("attempt_rows") == 20318, "tracking attempt_rows mismatch", failures)
    require(counters.get("completed") == 1049, "tracking completed mismatch", failures)
    require(counters.get("pending") == 9, "tracking pending mismatch", failures)
    require(tracking.get("next_attempt_id") == 20318, "tracking next_attempt_id mismatch", failures)

    for path in (DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE):
        text = read_text(path)
        require("Wave662 CDXTexture image codec hardening" in text, f"Wave662 missing from {path.name}", failures)
        require("cdxtexture-image-codec-wave662" in text, f"Wave662 tag missing from {path.name}", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="return non-zero on validation failure")
    args = parser.parse_args()

    failures: list[str] = []
    try:
        check_metadata(failures)
        check_logs(failures)
        check_docs(failures)
        check_state(failures)
    except Exception as exc:  # noqa: BLE001
        failures.append(f"{type(exc).__name__}: {exc}")

    status = "PASS" if not failures else "FAIL"
    print("Ghidra CDXTexture image-codec Wave662 probe")
    print(f"Status: {status}")
    print(f"Targets: {len(TARGETS)}")
    print(f"Evidence root: {BASE.relative_to(ROOT)}")
    if failures:
        for failure in failures:
            print(f"- {failure}")
    return 1 if failures and args.check else 0


if __name__ == "__main__":
    raise SystemExit(main())
