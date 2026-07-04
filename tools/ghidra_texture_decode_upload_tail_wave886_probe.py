#!/usr/bin/env python3
"""Validate Wave886 texture decode/upload tail read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave886-texture-decode-upload-tail"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_texture_decode_upload_tail_wave886_2026-05-26.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
DXTEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXTexture.cpp" / "_index.md"
TEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "texture.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

TASK = "Wave886 texture decode/upload tail"
TAG = "texture-decode-upload-tail-wave886"
STRICT_PROXY = "5978/6113 = 97.79%"
NEXT_HEAD = "0x005759b6 CFastVB__DispatchIndirect_00657014"
BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260526-023255_post_wave886_texture_decode_upload_tail_verified"

TARGETS = {
    "0x00573d80": {
        "name": "CTexture__InsertNodeIntoTree",
        "signature": "int CTexture__InsertNodeIntoTree(void)",
        "tokens": ("RB-tree insert helper", "CFastVB__InsertNodeIntoRBTreeWithHint_00573340", "0x00573530", "DAT_009d0c44", "0x14-byte node"),
        "tags": {"rb-tree-insert", "sentinel-tree", "dat-009d0c44", "oid-alloc-0x14", "ret-0x10"},
        "ret": "0x10",
    },
    "0x00574492": {
        "name": "CDXTexture__UploadDecodedBufferToSurface",
        "signature": "int CDXTexture__UploadDecodedBufferToSurface(void)",
        "tokens": ("decoded-buffer upload helper", "CDXTexture__UploadSurfaceRegionWithFallback", "CFastVB__InitDualTexelConversionPipeline", "0x80004"),
        "tags": {"decoded-buffer-upload", "surface-region-upload", "dual-texel-conversion", "ret-0x28"},
        "ret": "0x28",
    },
    "0x00574662": {
        "name": "CDXTexture__ConvertSurfaceWithActiveProfile",
        "signature": "int CDXTexture__ConvertSurfaceWithActiveProfile(void)",
        "tokens": ("active-profile surface conversion helper", "CDXTexture__CreateTexelCodecProfileFromSurfaceDesc", "six-dword descriptor", "CFastVB__InitDualTexelConversionPipeline"),
        "tags": {"surface-conversion", "active-profile", "texel-codec-profile", "dual-texel-conversion", "ret-0x2c"},
        "ret": "0x2c",
    },
    "0x0057473b": {
        "name": "CDXTexture__NormalizeTextureConversionParams",
        "signature": "int CDXTexture__NormalizeTextureConversionParams(void)",
        "tokens": ("texture conversion parameter normalizer", "CDXTexture__FindFormatDescriptorById", "CFastVB__SelectBestFormatHandler", "DXT1-DXT5", "vtable slot at +0x1c"),
        "tags": {"texture-param-normalizer", "format-selection", "dxt-block-align", "device-caps-query", "ret-0x20"},
        "ret": "0x20",
    },
    "0x00574ae5": {
        "name": "CDXTexture__DecodeMemoryAndUploadWithRect",
        "signature": "int CDXTexture__DecodeMemoryAndUploadWithRect(void)",
        "tokens": ("memory decode plus rectangle upload helper", "CDXTexture__DecodeFromMemory_WithFallbackCodecs", "validates a caller rectangle", "CDXTexture__UploadDecodedBufferToSurface"),
        "tags": {"memory-decode-upload", "fallback-codecs", "rect-validation", "surface-node-tree", "ret-0x24"},
        "forbidden_tags": {"ret-0x18"},
        "ret": "0x24",
    },
    "0x00574b9d": {
        "name": "CDXTexture__CopyOrUploadSurfaceRegionWithFallback",
        "signature": "int CDXTexture__CopyOrUploadSurfaceRegionWithFallback(void)",
        "tokens": ("surface-region copy helper", "CDXTexture__GenerateMipChainBySurfaceCopy", "D3D9 debug output", "CDXTexture__UploadDecodedBufferToSurface"),
        "tags": {"surface-copy-fallback", "d3d-copy-path", "d3d-debug-mute", "mip-chain-caller", "ret-0x20"},
        "ret": "0x20",
    },
    "0x00574da5": {
        "name": "CDXTexture__ConvertSurfaceRegionWithActiveProfile",
        "signature": "int CDXTexture__ConvertSurfaceRegionWithActiveProfile(void)",
        "tokens": ("compact surface-region conversion wrapper", "CDXTexture__GenerateMipChainBySurfaceCopy", "CDXTexture__CreateTexelCodecProfileFromSurfaceDesc", "CDXTexture__ConvertSurfaceWithActiveProfile"),
        "tags": {"surface-region-conversion", "active-profile-wrapper", "mip-chain-caller", "ret-0x20"},
        "forbidden_tags": {"ret-0x1c"},
        "ret": "0x20",
    },
    "0x0057511b": {
        "name": "Platform__OpenDecodeUploadMappedTexture",
        "signature": "int Platform__OpenDecodeUploadMappedTexture(void)",
        "tokens": ("platform mapped-file decode/upload bridge", "Platform__ProcessPendingScreenDump", "CDXTexture__OpenMappedFileReadOnly", "CDXTexture__DecodeMemoryAndUploadWithRect"),
        "tags": {"mapped-file-decode-upload", "platform-bridge", "read-only-open", "screen-dump-caller", "ret-0x20"},
        "forbidden_tags": {"ret-0x24"},
        "ret": "0x20",
    },
    "0x0057516c": {
        "name": "CDXTexture__DecodeMemoryToTextureObject",
        "signature": "int CDXTexture__DecodeMemoryToTextureObject(void)",
        "tokens": ("central memory-to-texture-object decode helper", "CDXTexture__DecodeMappedMemoryEntry", "CDXTexture__NormalizeTextureConversionParams", "CDXTexture__GenerateMipChainBySurfaceCopy", "device vtable slots"),
        "tags": {"memory-to-texture-object", "fallback-codecs", "palette-copy", "format-map", "texture-create-vtable", "mip-chain-generation", "ret-0x44"},
        "ret": "0x44",
    },
    "0x005758e6": {
        "name": "CDXTexture__DecodeMappedMemoryEntry",
        "signature": "void CDXTexture__DecodeMappedMemoryEntry(void)",
        "tokens": ("mapped-memory decode entry thunk", "CDXTexture__LoadTextureFromFile", "CDXTexture__DecodeMappedFileToTexture", "RET 0x3c"),
        "tags": {"mapped-memory-entry", "decode-thunk", "forwarded-stack-block", "ret-0x3c"},
        "ret": "0x3c",
    },
}

COMMON_TAGS = {
    "static-reaudit",
    TAG,
    "wave886-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-verified",
    "stack-locked-abi",
    "hidden-register-context",
    "important-render-infrastructure",
    "texture-decode-upload-tail",
    "raw-commentless-head",
}

EXPECTED_XREFS = {
    "0x00573d80": {"0x00573530"},
    "0x00574492": {"0x00574b90", "0x005756c4", "0x005757b8", "0x00574d53"},
    "0x00574662": {"0x0057572c", "0x005758dc", "0x00574e11"},
    "0x0057473b": {"0x00575516"},
    "0x00574ae5": {"0x00575156"},
    "0x00574b9d": {"0x0057501f"},
    "0x00574da5": {"0x00575073"},
    "0x0057511b": {"0x00441d4a"},
    "0x0057516c": {"0x0057591a"},
    "0x005758e6": {"0x005578d3", "0x00575970"},
}

CORE_ANCHORS = (
    TASK,
    TAG,
    "0x00573d80 CTexture__InsertNodeIntoTree",
    "0x00574492 CDXTexture__UploadDecodedBufferToSurface",
    "0x0057473b CDXTexture__NormalizeTextureConversionParams",
    "0x0057516c CDXTexture__DecodeMemoryToTextureObject",
    "0x005758e6 CDXTexture__DecodeMappedMemoryEntry",
    "CFastVB__InsertNodeIntoRBTreeWithHint_00573340",
    "CDXTexture__DecodeFromMemory_WithFallbackCodecs",
    "CFastVB__InitDualTexelConversionPipeline",
    "CDXTexture__GenerateMipChainBySurfaceCopy",
    NEXT_HEAD,
    STRICT_PROXY,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime texture decode behavior proven",
    "runtime texture upload behavior proven",
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
        "pre-xrefs.tsv": 16,
        "pre-instructions.tsv": 1767,
        "pre-decompile/index.tsv": 10,
        "pre-context-metadata.tsv": 17,
        "pre-context-tags.tsv": 17,
        "pre-context-xrefs.tsv": 28,
        "pre-context-instructions.tsv": 3684,
        "pre-context-decompile/index.tsv": 17,
        "post-metadata.tsv": 10,
        "post-tags.tsv": 10,
        "post-xrefs.tsv": 16,
        "post-instructions.tsv": 1767,
        "post-decompile/index.tsv": 10,
        "post-context-metadata.tsv": 17,
        "post-context-tags.tsv": 17,
        "post-context-xrefs.tsv": 28,
        "post-context-instructions.tsv": 3684,
        "post-context-decompile/index.tsv": 17,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs_by_target: dict[str, set[str]] = {address: set() for address in TARGETS}
    for row in read_tsv(BASE / "post-xrefs.tsv"):
        target = normalize_address(row["target_addr"])
        if target in xrefs_by_target:
            xrefs_by_target[target].add(normalize_address(row["from_addr"]))
            require(row["ref_type"] == "UNCONDITIONAL_CALL", f"xref type mismatch at {target}", failures)

    instructions = read_tsv(BASE / "post-instructions.tsv")
    ret_by_function = {
        normalize_address(row["function_entry"]): row["operands"]
        for row in instructions
        if row["mnemonic"] == "RET"
    }

    for address, spec in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing post metadata for {address}", failures)
        if row is not None:
            comment = row.get("comment", "")
            require(row.get("name") == spec["name"], f"name mismatch at {address}", failures)
            require(row.get("signature") == spec["signature"], f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            require("Wave886 static read-back" in comment, f"missing wave comment at {address}", failures)
            for token in spec["tokens"]:
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing post tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            expected_tags = COMMON_TAGS | set(spec["tags"])
            require(expected_tags.issubset(actual_tags), f"post tags missing at {address}: {expected_tags - actual_tags}", failures)
            for tag in spec.get("forbidden_tags", set()):
                require(tag not in actual_tags, f"stale tag still present at {address}: {tag}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index at {address}", failures)
        if dec is not None:
            require(dec["name"] == spec["name"], f"decompile name mismatch at {address}", failures)
            require(dec["signature"] == spec["signature"], f"decompile signature mismatch at {address}", failures)
            require(dec["status"] == "OK", f"decompile status mismatch at {address}", failures)

        require(EXPECTED_XREFS[address].issubset(xrefs_by_target[address]), f"xref set mismatch at {address}", failures)
        require(ret_by_function.get(address) == spec["ret"], f"RET operand mismatch at {address}: {ret_by_function.get(address)}", failures)

    decompile_text = "\n".join(read_text(path) for path in (BASE / "post-decompile").glob("*.c"))
    for token in (
        "OID__AllocObject_DefaultTag_00662b2c",
        "CDXTexture__DecodeFromMemory_WithFallbackCodecs",
        "CDXTexture__UploadSurfaceRegionWithFallback",
        "CFastVB__InitDualTexelConversionPipeline",
        "CDXTexture__NormalizeTextureConversionParams",
        "CDXTexture__GenerateMipChainBySurfaceCopy",
        "CDXTexture__DecodeMemoryToTextureObject",
    ):
        require(token in decompile_text, f"post decompile missing token: {token}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=10 renamed=0 would_rename=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=10 skipped=0 renamed=0 would_rename=0 missing=0 bad=0",
        "apply-correct-tags-dry.log": "SUMMARY: updated=0 skipped=10 renamed=0 would_rename=0 missing=0 bad=0",
        "apply-correct-tags.log": "SUMMARY: updated=3 skipped=7 renamed=0 would_rename=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=10 renamed=0 would_rename=0 missing=0 bad=0",
        "post-metadata.log": "targets=10 found=10 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=10 missing=0",
        "post-xrefs.log": "Wrote 16 rows",
        "post-instructions.log": "Wrote 1767 function-body instruction rows",
        "post-decompile.log": "targets=10 dumped=10 missing=0 failed=0",
        "post-context-metadata.log": "targets=17 found=17 missing=0",
        "post-context-tags.log": "ExportFunctionTagsByAddress complete: rows=17 missing=0",
        "post-context-xrefs.log": "Wrote 28 rows",
        "post-context-instructions.log": "Wrote 3684 function-body instruction rows",
        "post-context-decompile.log": "targets=17 dumped=17 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6113 commented_functions=5978",
        "queue-probe.log": "Commentless functions: 135",
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave886.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave886_queue_probe.log",
    }
    for relative, token in expected.items():
        path = aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)
        if relative.startswith("post") or relative in {"quality-refresh.log", "queue-probe.log"}:
            for bad in ("Input file not found", "Script not found"):
                require(bad not in text, f"unexpected path/script token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6113, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 135, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(queue["priorityQueues"]["commentlessHighSignal"] == [], "high-signal queue not empty", failures)
    require(queue["priorityQueues"]["signature"] == [], "signature queue not empty", failures)
    require(queue["priorityQueues"]["nameConfidence"] == [], "name-confidence queue not empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6113, "quality TSV row count mismatch", failures)
    require(commented == 5978, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5978, "quality TSV strict count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x005759b6", "raw head address mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CFastVB__DispatchIndirect_00657014", "raw head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 172854151 or backup.get("totalBytes") == 172854151.0, "backup byte count mismatch", failures)
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
        DXTEXTURE_DOC,
        TEXTURE_DOC,
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
    require(scripts.get("test:ghidra-texture-decode-upload-tail-wave886") == r"py -3 tools\ghidra_texture_decode_upload_tail_wave886_probe.py --check", "missing package script", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == TASK for row in ledger_rows), "missing Wave886 ledger row", failures)
    require(any(row.get("task") == TASK and row.get("attempt_id") == 20541 for row in attempts), "missing Wave886 attempt row", failures)


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
        print("Wave886 texture decode/upload tail probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave886 texture decode/upload tail probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
