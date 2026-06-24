#!/usr/bin/env python3
"""Validate Wave714 PNG scanline / pass head read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave714-png-scanline-pass-head"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_png_scanline_pass_head_wave714_2026-05-22.md"
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
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

COMMON_TAGS = {
    "static-reaudit",
    "png-scanline-pass-head-wave714",
    "wave714-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "png-scanline-pass-head",
}

TARGETS = {
    "0x0059ce20": (
        "CDXTexture__ExpandPackedPixelsToScanline",
        "void __stdcall CDXTexture__ExpandPackedPixelsToScanline(void * png_decode_state, void * output_scanline, uint pass_pixel_mask)",
        ("RET 0xc", "pass-pixel-mask", "0xff", "packed pixels"),
        COMMON_TAGS | {"png", "scanline", "packed-pixels", "pass-mask", "ret-0xc", "tranche-head"},
    ),
    "0x0059d036": (
        "CDXTexture__ExpandAdam7PassRowInPlace",
        "void __stdcall CDXTexture__ExpandAdam7PassRowInPlace(void * row_layout_descriptor, void * row_buffer, int adam7_pass_index)",
        ("RET 0xc", "DAT_005f39d8", "backward", "byte-count"),
        COMMON_TAGS | {"png", "adam7", "row-expansion", "packed-pixels", "ret-0xc"},
    ),
    "0x0059d301": (
        "CDXTexture__ApplyPngScanlineFilter",
        "void __stdcall CDXTexture__ApplyPngScanlineFilter(void * png_decode_state, void * row_layout_descriptor, void * current_scanline, void * previous_scanline, int filter_type)",
        ("RET 0x14", "Sub, Up, Average", "Paeth-style", "unknown filter"),
        COMMON_TAGS | {"png", "scanline-filter", "paeth", "filter-type", "ret-0x14"},
    ),
    "0x0059d47a": (
        "CDXTexture__InitPngImageBuffersAndPassGeometry",
        "void __stdcall CDXTexture__InitPngImageBuffersAndPassGeometry(void * png_decode_state)",
        ("RET 0x4", "post-decode transforms", "Adam7 pass dimensions", "CDXTexture__AllocOrThrow"),
        COMMON_TAGS | {"png", "decode-buffer", "pass-geometry", "allocation", "ret-0x4"},
    ),
    "0x0059d614": (
        "CDXTexture__FinalizePngChunkAndVerifyCrc",
        "int __stdcall CDXTexture__FinalizePngChunkAndVerifyCrc(void * png_decode_state, uint remaining_chunk_bytes)",
        ("RET 0x8", "CRC error", "nonzero status", "remaining chunk payload"),
        COMMON_TAGS | {"png", "crc", "chunk-finalize", "chunk-read", "ret-0x8", "tranche-tail"},
    ),
}

DOC_TOKENS = (
    "Wave714 PNG scanline / pass head",
    "png-scanline-pass-head-wave714",
    "0x0059ce20 CDXTexture__ExpandPackedPixelsToScanline",
    "0x0059d614 CDXTexture__FinalizePngChunkAndVerifyCrc",
    "extraout_var",
    "0x0059d699 CDXTexture__ParsePngChunk_IHDR",
    "0x0042f220 CSPtrSet__Clear",
    r"G:\GhidraBackups\BEA_20260522-002212_post_wave714_png_scanline_pass_head_verified",
)

OVERCLAIM_TOKENS = (
    "runtime png behavior proven",
    "runtime decode/image fidelity proven",
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


def check_metadata(failures: list[str]) -> None:
    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "decompile-post" / "index.tsv")}

    expected_counts = {
        "candidate-metadata.tsv": 5,
        "candidate-tags.tsv": 5,
        "candidate-xrefs.tsv": 22,
        "candidate-instructions.tsv": 185,
        "decompile-candidate-pre/index.tsv": 5,
        "pre-metadata.tsv": 5,
        "pre-tags.tsv": 5,
        "pre-xrefs.tsv": 22,
        "pre-instructions.tsv": 185,
        "decompile-pre/index.tsv": 5,
        "post-metadata.tsv": 5,
        "post-tags.tsv": 5,
        "post-xrefs.tsv": 22,
        "post-instructions.tsv": 185,
        "decompile-post/index.tsv": 5,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    for address, (name, signature, comment_tokens, expected_tags) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is None:
            continue
        require(row.get("name") == name, f"name mismatch at {address}", failures)
        require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
        require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
        comment = row.get("comment", "")
        require("Wave714 static read-back" in comment, f"missing Wave714 comment at {address}", failures)
        require("Static metadata only" in comment, f"missing uncertainty clause at {address}", failures)
        for token in comment_tokens:
            require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(expected_tags.issubset(actual_tags), f"tags missing at {address}: {expected_tags - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)
        decompile_file = BASE / "decompile-post" / f"{address[2:]}_{name}.c"
        require(decompile_file.is_file(), f"missing decompile file for {address}", failures)
        if decompile_file.is_file():
            text = read_text(decompile_file)
            for token in ("param_", "unaff_", "in_stack_", "in_ECX"):
                require(token not in text, f"{token} survived in post decompile for {address}", failures)
            if address == "0x0059d614":
                require("extraout_var" in text, "expected extraout_var gap missing for 0x0059d614", failures)
            else:
                require("extraout_" not in text, f"unexpected extraout_ token survived for {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=5 renamed=0 would_rename=0 signature_updated=5 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=5 skipped=0 renamed=0 would_rename=0 signature_updated=5 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=5 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "export-candidate-metadata.log": "targets=5 found=5 missing=0",
        "export-candidate-tags.log": "ExportFunctionTagsByAddress complete: rows=5 missing=0",
        "export-candidate-xrefs.log": "Wrote 22 rows",
        "export-candidate-instructions.log": "Wrote 185 instruction rows",
        "export-candidate-decompile.log": "targets=5 dumped=5 missing=0 failed=0",
        "export-pre-metadata.log": "targets=5 found=5 missing=0",
        "export-pre-tags.log": "ExportFunctionTagsByAddress complete: rows=5 missing=0",
        "export-pre-xrefs.log": "Wrote 22 rows",
        "export-pre-instructions.log": "Wrote 185 instruction rows",
        "export-pre-decompile.log": "targets=5 dumped=5 missing=0 failed=0",
        "export-post-metadata.log": "targets=5 found=5 missing=0",
        "export-post-tags.log": "ExportFunctionTagsByAddress complete: rows=5 missing=0",
        "export-post-xrefs.log": "Wrote 22 rows",
        "export-post-instructions.log": "Wrote 185 instruction rows",
        "export-post-decompile.log": "targets=5 dumped=5 missing=0 failed=0",
        "export-queue-refresh.log": "total_functions=6098 commented_functions=4159",
    }
    for log_name, token in expected.items():
        text = read_text(BASE / log_name)
        require(token in text, f"missing log token in {log_name}: {token}", failures)
        require("LockException" not in text, f"LockException in {log_name}", failures)
        require("BADNAME:" not in text and "MISSING:" not in text and "FAIL:" not in text, f"bad marker in {log_name}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    signals = queue.get("qualitySignals", {})
    require(queue.get("status") == "PASS", "queue status not PASS", failures)
    require(queue.get("totalFunctions") == 6098, "queue total mismatch", failures)
    require(signals.get("commentlessFunctionCount") == 1939, "queue commentless mismatch", failures)
    require(signals.get("undefinedSignatureCount") == 1216, "queue undefined mismatch", failures)
    require(signals.get("paramSignatureCount") == 178, "queue param mismatch", failures)
    high = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(high["address"] == "0x0059d699", "high-signal head mismatch", failures)
    require(high["name"] == "CDXTexture__ParsePngChunk_IHDR", "high-signal head name mismatch", failures)

    quality_rows = read_tsv(QUEUE_TSV)
    raw_head = next(row for row in quality_rows if not row.get("comment", "").strip())
    require(raw_head["address"] == "0x0042f220", "raw commentless head mismatch", failures)
    require(raw_head["name"] == "CSPtrSet__Clear", "raw commentless head name mismatch", failures)
    strict = [
        row for row in quality_rows
        if row.get("comment", "").strip()
        and not re.search(r"\bundefined\b", row.get("signature", ""))
        and not re.search(r"\bparam_\d+\b", row.get("signature", ""))
    ]
    require(len(strict) == 4103, "strict clean-signature proxy mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    backup_path = backup.get("backup_path") or backup.get("backupPath")
    file_count = backup.get("file_count") or backup.get("fileCount")
    total_bytes = backup.get("total_bytes") or backup.get("totalBytes")
    diff_count = backup.get("diff_count") if "diff_count" in backup else backup.get("diffCount")
    require(backup_path == r"G:\GhidraBackups\BEA_20260522-002212_post_wave714_png_scanline_pass_head_verified", "backup path mismatch", failures)
    require(file_count == 19, "backup file count mismatch", failures)
    require(int(total_bytes or 0) == 165972871, "backup byte count mismatch", failures)
    require(diff_count == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    package = read_json(PACKAGE_JSON)
    require(package["scripts"].get("test:ghidra-png-scanline-pass-head-wave714") == "py -3 tools\\ghidra_png_scanline_pass_head_wave714_probe.py --check", "package script missing", failures)

    doc_paths = (
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        DXTEXTURE_DOC,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
        TRACKING,
    )
    for path in doc_paths:
        text = read_text(path)
        normalized_text = text.replace("\\\\", "\\")
        for token in DOC_TOKENS:
            require(token in normalized_text, f"{path.relative_to(ROOT)} missing token: {token}", failures)
        lowered = text.lower()
        for token in OVERCLAIM_TOKENS:
            require(token not in lowered, f"{path.relative_to(ROOT)} has overclaim token: {token}", failures)

    for path in (LEDGER, ATTEMPT_LOG):
        rows = read_jsonl(path)
        require(any(row.get("task") == "Wave714 PNG scanline / pass head" for row in rows), f"{path.relative_to(ROOT)} missing Wave714 row", failures)

    tracking = read_json(TRACKING)
    require(tracking.get("counters", {}).get("ledger_rows") == 1110, "tracking ledger row count mismatch", failures)
    require(tracking.get("counters", {}).get("attempt_rows") == 20370, "tracking attempt row count mismatch", failures)
    require(tracking.get("next_attempt_id") == 20370, "tracking next attempt mismatch", failures)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.check:
        parser.error("expected --check")

    failures: list[str] = []
    check_metadata(failures)
    check_logs(failures)
    check_queue_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave714 PNG scanline / pass head probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave714 PNG scanline / pass head probe: PASS")
    print("Targets: 5")
    print("Queue: 6098 total, 4159 commented, 1939 commentless, 1216 undefined, 178 param_N")
    print("Backup: G:\\GhidraBackups\\BEA_20260522-002212_post_wave714_png_scanline_pass_head_verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
