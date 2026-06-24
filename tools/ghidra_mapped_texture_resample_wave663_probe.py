#!/usr/bin/env python3
"""Validate Wave663 mapped-texture resample setup read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave663-mapped-texture-resample-setup"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_mapped_texture_resample_wave663_2026-05-21.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
DXTEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXTexture.cpp" / "_index.md"
FASTVB_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FastVB.cpp" / "_index.md"
MATH_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Math.cpp" / "_index.md"
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
    "mapped-texture-resample-wave663",
    "wave663-readback-verified",
    "static-reaudit",
    "retail-binary-evidence",
    "signature-hardened",
    "comment-hardened",
}

TARGETS = {
    "0x0057c7a4": {
        "name": "CMeshCollisionVolume__LoadMappedTextureResourcesByMode",
        "signature": "int __thiscall CMeshCollisionVolume__LoadMappedTextureResourcesByMode(void * this, void * mapped_resource_name_or_path, int output_mode, int open_mode_flags, int unused_arg3)",
        "tags": {"mapped-texture", "mode-dispatch", "surface-conversion"},
        "comment_tokens": ("format descriptor list", "BMP/JPEG/DDS-style writes", "exact mode enum"),
        "decompile": "0057c7a4_CMeshCollisionVolume__LoadMappedTextureResourcesByMode.c",
    },
    "0x0057cc7b": {
        "name": "Math__FloorFloatToDouble",
        "signature": "double __stdcall Math__FloorFloatToDouble(float value)",
        "tags": {"floor", "math", "resample-helper"},
        "comment_tokens": ("casts the input float to double", "0x0055dfe7", "exact rounding"),
        "decompile": "0057cc7b_Math__FloorFloatToDouble.c",
    },
    "0x0057cc8e": {
        "name": "CFastVB__ClearTripleDword",
        "signature": "void __fastcall CFastVB__ClearTripleDword(void * triple_dword)",
        "tags": {"initializer", "resample-helper", "triple-dword"},
        "comment_tokens": ("zeroes three consecutive dwords", "dual-profile conversion paths", "callback ABI"),
        "decompile": "0057cc8e_CFastVB__ClearTripleDword.c",
    },
    "0x0057cca4": {
        "name": "CFastVB__BuildResampleKernelBuckets",
        "signature": "int * __stdcall CFastVB__BuildResampleKernelBuckets(uint output_count, int source_count, int clamp_edges)",
        "tags": {"bucket-table", "dual-profile-conversion", "resample-kernel"},
        "comment_tokens": ("variable-length resample bucket table", "per-source weights", "kernel-table layout"),
        "decompile": "0057cca4_CFastVB__BuildResampleKernelBuckets.c",
    },
}

DOC_TOKENS = (
    "Wave663 mapped texture resample setup",
    "mapped-texture-resample-wave663",
    "0x0057c7a4 CMeshCollisionVolume__LoadMappedTextureResourcesByMode",
    "0x0057cca4 CFastVB__BuildResampleKernelBuckets",
    "0x0057d216 CFastVB__DispatchMmxKernel_00657974",
)

OVERCLAIM_TOKENS = (
    "fully reverse-engineered",
    "fully recovered",
    "runtime texture export behavior proven",
    "runtime resampling quality proven",
    "exact resample kernel table layout proven",
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
        require("Wave663 static read-back" in comment, f"missing Wave663 comment at {address}", failures)
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
        "apply-wave663-dry.log": "SUMMARY: updated=0 skipped=4 renamed=0 would_rename=0 signature_updated=4 missing=0 bad=0",
        "apply-wave663-apply.log": "SUMMARY: updated=4 skipped=0 renamed=0 would_rename=0 signature_updated=4 missing=0 bad=0",
        "apply-wave663-final-dry.log": "SUMMARY: updated=0 skipped=4 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=4 found=4 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=4 missing=0",
        "post-decompile.log": "targets=4 dumped=4 missing=0 failed=0",
        "post-instructions.log": "targets=4 missing=0",
        "post-xrefs.log": "Wrote 9 rows",
    }
    for filename, token in expected_exact.items():
        text = read_text(BASE / filename)
        require(token in text, f"log token missing in {filename}: {token}", failures)
        require("REPORT: Save succeeded" in text, f"save report missing in {filename}", failures)
        require("LockException" not in text, f"LockException found in {filename}", failures)
        require("ERROR REPORT SCRIPT ERROR" not in text, f"script error found in {filename}", failures)
        require("BAD:" not in text and "BADNAME:" not in text and "MISSING:" not in text, f"bad/missing marker found in {filename}", failures)

    instructions = read_text(BASE / "post-instructions.log")
    require("Wrote 148 instruction rows" in instructions, "instruction row count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    package = read_json(PACKAGE_JSON)
    require("test:ghidra-mapped-texture-resample-wave663" in package.get("scripts", {}), "package script missing", failures)

    for path in (PUBLIC_NOTE, FUNCTION_INDEX, DXTEXTURE_DOC, FASTVB_DOC, MATH_DOC, GHIDRA_REFERENCE, CAMPAIGN, BACKLOG):
        text = read_text(path)
        for token in DOC_TOKENS:
            require(token in text, f"{token!r} missing from {path.relative_to(ROOT)}", failures)
        for token in OVERCLAIM_TOKENS:
            require(token not in text, f"overclaim token {token!r} found in {path.relative_to(ROOT)}", failures)

    for path in (LEDGER, ATTEMPT_LOG):
        text = read_text(path)
        require("Wave663 mapped texture resample setup" in text, f"Wave663 missing from {path.relative_to(ROOT)}", failures)
        require("mapped-texture-resample-wave663" in text, f"Wave663 tag missing from {path.relative_to(ROOT)}", failures)


def check_state(failures: list[str]) -> None:
    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("diffCount") == 0, "backup diffCount mismatch", failures)
    require(backup.get("fileCount") == 19, "backup fileCount mismatch", failures)
    require(backup.get("byteCount") == 163515271, "backup byteCount mismatch", failures)
    require("post_wave663_mapped_texture_resample_verified" in backup.get("backupPath", ""), "backup path mismatch", failures)

    queue = read_json(QUEUE_JSON)
    require(queue.get("totalFunctions") == 6098, "queue total mismatch", failures)
    signals = queue.get("qualitySignals", {})
    require(signals.get("commentlessFunctionCount") == 2450, "queue commentless mismatch", failures)
    require(signals.get("undefinedSignatureCount") == 1217, "queue undefined-signature mismatch", failures)
    require(signals.get("paramSignatureCount") == 669, "queue param_N mismatch", failures)
    head = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(head.get("address") == "0x0057d216", f"queue head address mismatch: {head}", failures)
    require(head.get("name") == "CFastVB__DispatchMmxKernel_00657974", f"queue head name mismatch: {head}", failures)

    ledger = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(ledger[-1].get("task") == "Wave663 mapped texture resample setup", "ledger last row mismatch", failures)
    require(attempts[-1].get("task") == "Wave663 mapped texture resample setup", "attempt task mismatch", failures)
    require(attempts[-1].get("attempt_id") == 20318, "attempt id mismatch", failures)
    require(len(ledger) == 1059, "ledger row count mismatch", failures)
    require(len(attempts) == 20319, "attempt row count mismatch", failures)

    tracking = read_json(TRACKING)
    counters = tracking.get("counters", {})
    require(tracking.get("current_focus", "").startswith("Wave663 mapped texture resample setup"), "tracking current_focus mismatch", failures)
    require(counters.get("ledger_rows") == 1059, "tracking ledger_rows mismatch", failures)
    require(counters.get("attempt_rows") == 20319, "tracking attempt_rows mismatch", failures)
    require(counters.get("completed") == 1050, "tracking completed mismatch", failures)
    require(counters.get("pending") == 9, "tracking pending mismatch", failures)
    require(tracking.get("next_attempt_id") == 20319, "tracking next_attempt_id mismatch", failures)

    for path in (DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE):
        text = read_text(path)
        require("Wave663 mapped texture resample setup" in text, f"Wave663 missing from {path.name}", failures)
        require("mapped-texture-resample-wave663" in text, f"Wave663 tag missing from {path.name}", failures)


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
    print("Ghidra mapped-texture resample Wave663 probe")
    print(f"Status: {status}")
    print(f"Targets: {len(TARGETS)}")
    print(f"Evidence root: {BASE.relative_to(ROOT)}")
    if failures:
        for failure in failures:
            print(f"- {failure}")
    return 1 if failures and args.check else 0


if __name__ == "__main__":
    raise SystemExit(main())
