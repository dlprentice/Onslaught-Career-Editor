#!/usr/bin/env python3
"""Validate Wave665 texture resample surface/volume read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave665-texture-resample-surface-volume"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_texture_resample_surface_volume_wave665_2026-05-21.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
DXTEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXTexture.cpp" / "_index.md"
FASTVB_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FastVB.cpp" / "_index.md"
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
    "texture-resample-wave665",
    "wave665-readback-verified",
    "static-reaudit",
    "retail-binary-evidence",
    "signature-hardened",
    "comment-hardened",
    "texture-resample",
}

TARGETS = {
    "0x0057e0c3": {
        "name": "CDXTexture__ConvertSurfaceDirectCopyOrDxtCopy",
        "signature": "int __fastcall CDXTexture__ConvertSurfaceDirectCopyOrDxtCopy(void * texture_resample_context)",
        "tags": {"direct-copy", "dxt-copy"},
        "comment_tokens": ("DXT block copying", "palette", "runtime copy behavior"),
        "decompile": "0057e0c3_CDXTexture__ConvertSurfaceDirectCopyOrDxtCopy.c",
    },
    "0x0057e200": {
        "name": "CFastVB__BlendEqualDimensionVolumeData",
        "signature": "int __fastcall CFastVB__BlendEqualDimensionVolumeData(void * texture_resample_context)",
        "tags": {"volume-copy", "equal-dimension"},
        "comment_tokens": ("vtable read slot +4", "vtable write slot +8", "runtime volume-copy behavior"),
        "decompile": "0057e200_CFastVB__BlendEqualDimensionVolumeData.c",
    },
    "0x0057e2de": {
        "name": "CFastVB__BlendClampedVolumeData",
        "signature": "int __fastcall CFastVB__BlendClampedVolumeData(void * texture_resample_context)",
        "tags": {"volume-copy", "clamped-volume"},
        "comment_tokens": ("mode byte 1", "zero-filled destination rows", "runtime padding behavior"),
        "decompile": "0057e2de_CFastVB__BlendClampedVolumeData.c",
    },
    "0x0057e4d3": {
        "name": "CDXTexture__ResampleSurfaceNearestNeighbor",
        "signature": "int __fastcall CDXTexture__ResampleSurfaceNearestNeighbor(void * texture_resample_context)",
        "tags": {"nearest-neighbor", "surface-resample"},
        "comment_tokens": ("mode byte 2", "16.16 stepping", "nearest-neighbor destination rows"),
        "decompile": "0057e4d3_CDXTexture__ResampleSurfaceNearestNeighbor.c",
    },
    "0x0057e6cc": {
        "name": "CDXTexture__DownsampleSurface2x2_WithFastPaths",
        "signature": "int __fastcall CDXTexture__DownsampleSurface2x2_WithFastPaths(void * texture_resample_context)",
        "tags": {"surface-downsample", "fast-path-dispatch"},
        "comment_tokens": ("mode byte 5", "Wave664 helpers", "vec4 2x2 average"),
        "decompile": "0057e6cc_CDXTexture__DownsampleSurface2x2_WithFastPaths.c",
    },
    "0x0057eadb": {
        "name": "CDXTexture__DownsampleVolume2x2x2",
        "signature": "int __fastcall CDXTexture__DownsampleVolume2x2x2(void * texture_resample_context)",
        "tags": {"volume-downsample", "average2x2x2"},
        "comment_tokens": ("3D half-size", "2x2x2 samples", "runtime downsample quality"),
        "decompile": "0057eadb_CDXTexture__DownsampleVolume2x2x2.c",
    },
    "0x0057ef10": {
        "name": "CFastVB__BuildResampleKernel1D",
        "signature": "void * __stdcall CFastVB__BuildResampleKernel1D(int wrap_edges)",
        "tags": {"resample-kernel", "bilinear-kernel"},
        "comment_tokens": ("caller registers", "wrap_edges", "allocation ownership"),
        "decompile": "0057ef10_CFastVB__BuildResampleKernel1D.c",
    },
    "0x0057f002": {
        "name": "CDXTexture__ResampleSurfaceBilinear",
        "signature": "int __fastcall CDXTexture__ResampleSurfaceBilinear(void * texture_resample_context)",
        "tags": {"bilinear", "surface-resample"},
        "comment_tokens": ("mode byte 3", "X/Y resample kernels", "runtime bilinear quality"),
        "decompile": "0057f002_CDXTexture__ResampleSurfaceBilinear.c",
    },
    "0x0057f391": {
        "name": "CDXTexture__ResampleVolumeTrilinear",
        "signature": "int __fastcall CDXTexture__ResampleVolumeTrilinear(void * texture_resample_context)",
        "tags": {"trilinear", "volume-resample"},
        "comment_tokens": ("X/Y/Z resample kernels", "four source row planes", "runtime trilinear quality"),
        "decompile": "0057f391_CDXTexture__ResampleVolumeTrilinear.c",
    },
}

DOC_TOKENS = (
    "Wave665 texture resample surface/volume",
    "texture-resample-wave665",
    "0x0057e0c3 CDXTexture__ConvertSurfaceDirectCopyOrDxtCopy",
    "0x0057f391 CDXTexture__ResampleVolumeTrilinear",
    "0x0057fa10 CFastVB__BlendWeightTable_scalar_deleting_dtor",
)

OVERCLAIM_TOKENS = (
    "fully reverse-engineered",
    "fully recovered",
    "runtime resample behavior proven",
    "runtime downsample behavior proven",
    "runtime bilinear quality proven",
    "runtime trilinear quality proven",
    "exact surface layout proven",
    "exact volume layout proven",
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
    return [json.loads(line) for line in read_text(path).splitlines() if line.strip()]


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
        require("Wave665 static read-back" in comment, f"missing Wave665 comment at {address}", failures)
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
        "apply-wave665-dry.log": "SUMMARY: updated=0 skipped=9 renamed=0 would_rename=0 signature_updated=9 missing=0 bad=0",
        "apply-wave665-apply.log": "SUMMARY: updated=9 skipped=0 renamed=0 would_rename=0 signature_updated=9 missing=0 bad=0",
        "apply-wave665-final-dry.log": "SUMMARY: updated=0 skipped=9 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=9 found=9 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=9 missing=0",
        "post-decompile.log": "targets=9 dumped=9 missing=0 failed=0",
        "post-instructions.log": "targets=9 missing=0",
        "post-xrefs.log": "Wrote 13 rows",
    }
    for filename, token in expected_exact.items():
        text = read_text(BASE / filename)
        require(token in text, f"log token missing in {filename}: {token}", failures)
        require("REPORT: Save succeeded" in text, f"save report missing in {filename}", failures)
        require("LockException" not in text, f"LockException found in {filename}", failures)
        require("ERROR REPORT SCRIPT ERROR" not in text, f"script error found in {filename}", failures)
        require("BAD:" not in text and "BADNAME:" not in text and "MISSING:" not in text, f"bad/missing marker found in {filename}", failures)

    instructions = read_text(BASE / "post-instructions.log")
    require("Wrote 333 instruction rows" in instructions, "instruction row count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    package = read_json(PACKAGE_JSON)
    require("test:ghidra-texture-resample-surface-volume-wave665" in package.get("scripts", {}), "package script missing", failures)

    for path in (PUBLIC_NOTE, FUNCTION_INDEX, DXTEXTURE_DOC, FASTVB_DOC, GHIDRA_REFERENCE, CAMPAIGN, BACKLOG):
        text = read_text(path)
        for token in DOC_TOKENS:
            require(token in text, f"{token!r} missing from {path.relative_to(ROOT)}", failures)
        for token in OVERCLAIM_TOKENS:
            require(token not in text, f"overclaim token {token!r} found in {path.relative_to(ROOT)}", failures)

    for path in (LEDGER, ATTEMPT_LOG):
        text = read_text(path)
        require("Wave665 texture resample surface/volume" in text, f"Wave665 missing from {path.relative_to(ROOT)}", failures)
        require("texture-resample-wave665" in text, f"Wave665 tag missing from {path.relative_to(ROOT)}", failures)


def check_state(failures: list[str]) -> None:
    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("diffCount") == 0, "backup diffCount mismatch", failures)
    require(backup.get("fileCount") == 19, "backup fileCount mismatch", failures)
    require(int(backup.get("byteCount", 0)) == 163580807, "backup byteCount mismatch", failures)
    require("post_wave665_texture_resample_verified" in backup.get("backupPath", ""), "backup path mismatch", failures)

    queue = read_json(QUEUE_JSON)
    require(queue.get("totalFunctions") == 6098, "queue total mismatch", failures)
    signals = queue.get("qualitySignals", {})
    require(signals.get("commentlessFunctionCount") == 2429, "queue commentless mismatch", failures)
    require(signals.get("undefinedSignatureCount") == 1217, "queue undefined-signature mismatch", failures)
    require(signals.get("paramSignatureCount") == 648, "queue param_N mismatch", failures)
    head = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(head.get("address") == "0x0057fa10", f"queue head address mismatch: {head}", failures)
    require(head.get("name") == "CFastVB__BlendWeightTable_scalar_deleting_dtor", f"queue head name mismatch: {head}", failures)

    ledger = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(ledger[-1].get("task") == "Wave665 texture resample surface/volume", "ledger last row mismatch", failures)
    require(attempts[-1].get("task") == "Wave665 texture resample surface/volume", "attempt task mismatch", failures)
    require(attempts[-1].get("attempt_id") == 20320, "attempt id mismatch", failures)
    require(len(ledger) == 1061, "ledger row count mismatch", failures)
    require(len(attempts) == 20321, "attempt row count mismatch", failures)

    tracking = read_json(TRACKING)
    counters = tracking.get("counters", {})
    require(tracking.get("current_focus", "").startswith("Wave665 texture resample surface/volume"), "tracking current_focus mismatch", failures)
    require(counters.get("ledger_rows") == 1061, "tracking ledger_rows mismatch", failures)
    require(counters.get("attempt_rows") == 20321, "tracking attempt_rows mismatch", failures)
    require(counters.get("completed") == 1052, "tracking completed mismatch", failures)
    require(counters.get("pending") == 9, "tracking pending mismatch", failures)
    require(tracking.get("next_attempt_id") == 20321, "tracking next_attempt_id mismatch", failures)

    for path in (DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE):
        text = read_text(path)
        require("Wave665 texture resample surface/volume" in text, f"Wave665 missing from {path.name}", failures)
        require("texture-resample-wave665" in text, f"Wave665 tag missing from {path.name}", failures)


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
    print("Ghidra texture resample surface/volume Wave665 probe")
    print(f"Status: {status}")
    print(f"Targets: {len(TARGETS)}")
    print(f"Evidence root: {BASE.relative_to(ROOT)}")
    if failures:
        for failure in failures:
            print(f"- {failure}")
    return 1 if failures and args.check else 0


if __name__ == "__main__":
    raise SystemExit(main())
