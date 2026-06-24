#!/usr/bin/env python3
"""Validate Wave664 texture downsample kernel read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave664-texture-downsample-kernels"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_texture_downsample_kernels_wave664_2026-05-21.md"
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
    "texture-downsample-wave664",
    "wave664-readback-verified",
    "static-reaudit",
    "retail-binary-evidence",
    "signature-hardened",
    "comment-hardened",
    "texture-downsample",
}

TARGETS = {
    "0x0057d216": {
        "name": "CFastVB__DispatchMmxKernel_00657974",
        "signature": "void __fastcall CFastVB__DispatchMmxKernel_00657974(void * downsample_context)",
        "tags": {"mmx-dispatch", "cpu-dispatch"},
        "comment_tokens": ("two-slot downsample context", "0x00657974", "CPU dispatch identity"),
        "decompile": "0057d216_CFastVB__DispatchMmxKernel_00657974.c",
    },
    "0x0057d4ad": {
        "name": "CFastVB__DispatchMmxKernel_00657978",
        "signature": "void __fastcall CFastVB__DispatchMmxKernel_00657978(void * downsample_context)",
        "tags": {"mmx-dispatch", "cpu-dispatch"},
        "comment_tokens": ("two-slot downsample context", "0x00657978", "CPU dispatch identity"),
        "decompile": "0057d4ad_CFastVB__DispatchMmxKernel_00657978.c",
    },
    "0x0057d4db": {
        "name": "CDXTexture__Average2x2Block_RGB565",
        "signature": "int __fastcall CDXTexture__Average2x2Block_RGB565(void * downsample_context)",
        "tags": {"average2x2", "rgb565"},
        "comment_tokens": ("2x2 packed 16-bit", "0xf81f/0x07e0", "runtime filter quality"),
        "decompile": "0057d4db_CDXTexture__Average2x2Block_RGB565.c",
    },
    "0x0057d62b": {
        "name": "CDXTexture__Average2x2Block_RGB555",
        "signature": "int __fastcall CDXTexture__Average2x2Block_RGB555(void * downsample_context)",
        "tags": {"average2x2", "rgb555"},
        "comment_tokens": ("2x2 packed 16-bit", "0x7c1f/0x03e0", "runtime filter quality"),
        "decompile": "0057d62b_CDXTexture__Average2x2Block_RGB555.c",
    },
    "0x0057d74f": {
        "name": "CDXTexture__Average2x2Block_ARGB1555",
        "signature": "int __fastcall CDXTexture__Average2x2Block_ARGB1555(void * downsample_context)",
        "tags": {"average2x2", "argb1555"},
        "comment_tokens": ("2x2 packed 16-bit", "0x83e0/0x7c1f", "exact alpha handling"),
        "decompile": "0057d74f_CDXTexture__Average2x2Block_ARGB1555.c",
    },
    "0x0057d89e": {
        "name": "CDXTexture__Average2x2Block_A4R4G4B4",
        "signature": "int __fastcall CDXTexture__Average2x2Block_A4R4G4B4(void * downsample_context)",
        "tags": {"average2x2", "a4r4g4b4"},
        "comment_tokens": ("2x2 packed 16-bit", "0xf0f0/0x0f0f", "runtime filter quality"),
        "decompile": "0057d89e_CDXTexture__Average2x2Block_A4R4G4B4.c",
    },
    "0x0057d9f1": {
        "name": "CFastVB__Downsample2x1_R5G6B5",
        "signature": "int __fastcall CFastVB__Downsample2x1_R5G6B5(void * downsample_context)",
        "tags": {"downsample2x1", "packed-byte"},
        "comment_tokens": ("retained-name byte-lane helper", "0xe3/0x1c", "owner identity"),
        "decompile": "0057d9f1_CFastVB__Downsample2x1_R5G6B5.c",
    },
    "0x0057db30": {
        "name": "CFastVB__Downsample2x1_L8",
        "signature": "int __fastcall CFastVB__Downsample2x1_L8(void * downsample_context)",
        "tags": {"downsample2x1", "l8"},
        "comment_tokens": ("byte-luminance helper", "rounded +2 bias", "owner identity"),
        "decompile": "0057db30_CFastVB__Downsample2x1_L8.c",
    },
    "0x0057dbcb": {
        "name": "CFastVB__Downsample2x1_A1R5G5B5",
        "signature": "int __fastcall CFastVB__Downsample2x1_A1R5G5B5(void * downsample_context)",
        "tags": {"downsample2x1", "a1r5g5b5"},
        "comment_tokens": ("packed 16-bit source texels", "0xe3/0xff1c", "A1R5G5B5 contract"),
        "decompile": "0057dbcb_CFastVB__Downsample2x1_A1R5G5B5.c",
    },
    "0x0057dd17": {
        "name": "CDXTexture__Average2x2Block_RGB444",
        "signature": "int __fastcall CDXTexture__Average2x2Block_RGB444(void * downsample_context)",
        "tags": {"average2x2", "rgb444"},
        "comment_tokens": ("2x2 packed 16-bit", "0x0f0f/0x00f0", "runtime filter quality"),
        "decompile": "0057dd17_CDXTexture__Average2x2Block_RGB444.c",
    },
    "0x0057de38": {
        "name": "CDXTexture__Average2x2Block_A8L8",
        "signature": "int __fastcall CDXTexture__Average2x2Block_A8L8(void * downsample_context)",
        "tags": {"average2x2", "a8l8"},
        "comment_tokens": ("A8L8-style", "low and high byte lanes", "runtime filter quality"),
        "decompile": "0057de38_CDXTexture__Average2x2Block_A8L8.c",
    },
    "0x0057df84": {
        "name": "CDXTexture__Average2x2Block_A4L4",
        "signature": "int __fastcall CDXTexture__Average2x2Block_A4L4(void * downsample_context)",
        "tags": {"average2x2", "a4l4"},
        "comment_tokens": ("packed byte source samples", "0xf0/0x0f", "runtime filter quality"),
        "decompile": "0057df84_CDXTexture__Average2x2Block_A4L4.c",
    },
}

DOC_TOKENS = (
    "Wave664 texture downsample kernels",
    "texture-downsample-wave664",
    "0x0057d216 CFastVB__DispatchMmxKernel_00657974",
    "0x0057df84 CDXTexture__Average2x2Block_A4L4",
    "0x0057e0c3 CDXTexture__ConvertSurfaceDirectCopyOrDxtCopy",
)

OVERCLAIM_TOKENS = (
    "fully reverse-engineered",
    "fully recovered",
    "runtime downsample behavior proven",
    "runtime filter quality proven",
    "exact surface/context layout proven",
    "CPU dispatch identity proven",
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
        require("Wave664 static read-back" in comment, f"missing Wave664 comment at {address}", failures)
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
        "apply-wave664-dry.log": "SUMMARY: updated=0 skipped=12 renamed=0 would_rename=0 signature_updated=12 missing=0 bad=0",
        "apply-wave664-apply.log": "SUMMARY: updated=12 skipped=0 renamed=0 would_rename=0 signature_updated=12 missing=0 bad=0",
        "apply-wave664-final-dry.log": "SUMMARY: updated=0 skipped=12 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=12 found=12 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=12 missing=0",
        "post-decompile.log": "targets=12 dumped=12 missing=0 failed=0",
        "post-instructions.log": "targets=12 missing=0",
        "post-xrefs.log": "Wrote 12 rows",
    }
    for filename, token in expected_exact.items():
        text = read_text(BASE / filename)
        require(token in text, f"log token missing in {filename}: {token}", failures)
        require("REPORT: Save succeeded" in text, f"save report missing in {filename}", failures)
        require("LockException" not in text, f"LockException found in {filename}", failures)
        require("ERROR REPORT SCRIPT ERROR" not in text, f"script error found in {filename}", failures)
        require("BAD:" not in text and "BADNAME:" not in text and "MISSING:" not in text, f"bad/missing marker found in {filename}", failures)

    instructions = read_text(BASE / "post-instructions.log")
    require("Wrote 444 instruction rows" in instructions, "instruction row count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    package = read_json(PACKAGE_JSON)
    require("test:ghidra-texture-downsample-kernels-wave664" in package.get("scripts", {}), "package script missing", failures)

    for path in (PUBLIC_NOTE, FUNCTION_INDEX, DXTEXTURE_DOC, FASTVB_DOC, GHIDRA_REFERENCE, CAMPAIGN, BACKLOG):
        text = read_text(path)
        for token in DOC_TOKENS:
            require(token in text, f"{token!r} missing from {path.relative_to(ROOT)}", failures)
        for token in OVERCLAIM_TOKENS:
            require(token not in text, f"overclaim token {token!r} found in {path.relative_to(ROOT)}", failures)

    for path in (LEDGER, ATTEMPT_LOG):
        text = read_text(path)
        require("Wave664 texture downsample kernels" in text, f"Wave664 missing from {path.relative_to(ROOT)}", failures)
        require("texture-downsample-wave664" in text, f"Wave664 tag missing from {path.relative_to(ROOT)}", failures)


def check_state(failures: list[str]) -> None:
    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("diffCount") == 0, "backup diffCount mismatch", failures)
    require(backup.get("fileCount") == 19, "backup fileCount mismatch", failures)
    require(backup.get("byteCount") == 163548039, "backup byteCount mismatch", failures)
    require("post_wave664_texture_downsample_verified" in backup.get("backupPath", ""), "backup path mismatch", failures)

    queue = read_json(QUEUE_JSON)
    require(queue.get("totalFunctions") == 6098, "queue total mismatch", failures)
    signals = queue.get("qualitySignals", {})
    require(signals.get("commentlessFunctionCount") == 2438, "queue commentless mismatch", failures)
    require(signals.get("undefinedSignatureCount") == 1217, "queue undefined-signature mismatch", failures)
    require(signals.get("paramSignatureCount") == 657, "queue param_N mismatch", failures)
    head = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(head.get("address") == "0x0057e0c3", f"queue head address mismatch: {head}", failures)
    require(head.get("name") == "CDXTexture__ConvertSurfaceDirectCopyOrDxtCopy", f"queue head name mismatch: {head}", failures)

    ledger = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(ledger[-1].get("task") == "Wave664 texture downsample kernels", "ledger last row mismatch", failures)
    require(attempts[-1].get("task") == "Wave664 texture downsample kernels", "attempt task mismatch", failures)
    require(attempts[-1].get("attempt_id") == 20319, "attempt id mismatch", failures)
    require(len(ledger) == 1060, "ledger row count mismatch", failures)
    require(len(attempts) == 20320, "attempt row count mismatch", failures)

    tracking = read_json(TRACKING)
    counters = tracking.get("counters", {})
    require(tracking.get("current_focus", "").startswith("Wave664 texture downsample kernels"), "tracking current_focus mismatch", failures)
    require(counters.get("ledger_rows") == 1060, "tracking ledger_rows mismatch", failures)
    require(counters.get("attempt_rows") == 20320, "tracking attempt_rows mismatch", failures)
    require(counters.get("completed") == 1051, "tracking completed mismatch", failures)
    require(counters.get("pending") == 9, "tracking pending mismatch", failures)
    require(tracking.get("next_attempt_id") == 20320, "tracking next_attempt_id mismatch", failures)

    for path in (DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE):
        text = read_text(path)
        require("Wave664 texture downsample kernels" in text, f"Wave664 missing from {path.name}", failures)
        require("texture-downsample-wave664" in text, f"Wave664 tag missing from {path.name}", failures)


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
    print("Ghidra texture downsample kernels Wave664 probe")
    print(f"Status: {status}")
    print(f"Targets: {len(TARGETS)}")
    print(f"Evidence root: {BASE.relative_to(ROOT)}")
    if failures:
        for failure in failures:
            print(f"- {failure}")
    return 1 if failures and args.check else 0


if __name__ == "__main__":
    raise SystemExit(main())
