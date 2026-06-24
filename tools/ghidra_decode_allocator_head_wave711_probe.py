#!/usr/bin/env python3
"""Validate Wave711 decode allocator head read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave711-decode-allocator-head"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_decode_allocator_head_wave711_2026-05-21.md"
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

BASE_TAGS = {
    "static-reaudit",
    "decode-allocator-head-wave711",
    "wave711-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "decode-allocator-head",
}

TARGETS = {
    "0x0059bae0": (
        "CDXTexture__AllocFromBank_SplitBlock",
        "int __stdcall CDXTexture__AllocFromBank_SplitBlock(void * allocator_owner, int bank_index, uint requested_size_bytes)",
        ("RET 0xc", "split-block list", "CDXTexture__AllocAligned16 still decompiles through extraout_EAX"),
        BASE_TAGS | {"split-bank-allocator", "ret-0xc", "helper-return-abi-open", "tranche-head"},
    ),
    "0x0059bc10": (
        "CDXTexture__AllocLinearBlockAndTrack",
        "int __stdcall CDXTexture__AllocLinearBlockAndTrack(void * allocator_owner, int bank_index, uint requested_size_bytes)",
        ("RET 0xc", "links the block into allocator state +0x3c", "CDXTexture__AllocAligned16 still decompiles through extraout_EAX"),
        BASE_TAGS | {"linear-bank-allocator", "ret-0xc", "helper-return-abi-open"},
    ),
    "0x0059bcc0": (
        "CDXTexture__AllocRowPointerTableAndRows",
        "int __stdcall CDXTexture__AllocRowPointerTableAndRows(void * allocator_owner, int bank_index, uint row_stride_bytes, uint row_count)",
        ("RET 0x10", "row pointer table", "linear path"),
        BASE_TAGS | {"row-pointer-table", "linear-row-batches", "ret-0x10"},
    ),
    "0x0059bd60": (
        "CDXTexture__AllocMcuRowPointerTableAndRows",
        "int __stdcall CDXTexture__AllocMcuRowPointerTableAndRows(void * allocator_owner, int bank_index, int mcu_units_per_row, uint row_count)",
        ("RET 0x10", "mcu_units_per_row*0x80", "row pointer table"),
        BASE_TAGS | {"mcu-row-pointer-table", "linear-row-batches", "ret-0x10"},
    ),
    "0x0059c3f0": (
        "CDXTexture__ReleaseDecodeBankLists",
        "void __stdcall CDXTexture__ReleaseDecodeBankLists(void * allocator_owner, int bank_index)",
        ("RET 0x8", "descriptor callbacks", "drains the linear tracked-block list"),
        BASE_TAGS | {"decode-bank-release", "tracked-list-drain", "ret-0x8"},
    ),
    "0x0059c510": (
        "CDXTexture__InitDecodeAllocatorVtable",
        "void __stdcall CDXTexture__InitDecodeAllocatorVtable(void * allocator_owner)",
        ("RET 0x4", "0x54 decode allocator state", "stale no-op helper label"),
        BASE_TAGS | {"allocator-vtable-init", "decode-budget", "helper-return-abi-open", "ret-0x4"},
    ),
    "0x0059c5d0": (
        "CDXTexture__PumpDecodeAllocatorAndSetStage",
        "void __stdcall CDXTexture__PumpDecodeAllocatorAndSetStage(void * decode_state)",
        ("RET 0x4", "vtable slot +0x24", "stage +0x14"),
        BASE_TAGS | {"allocator-stage-pump", "decode-stage", "ret-0x4", "tranche-tail"},
    ),
}

DEFERRED_ABI = {
    "0x0059be00": ("CDXTexture__CreateDecodeJobDescriptor", "in_stack_"),
    "0x0059be70": ("CDXTexture__AllocDecodeBlockAndLink", "in_stack_"),
    "0x0059c070": ("CTexture__ProcessRowBatchesLinearStride", "unaff_ESI"),
    "0x0059c110": ("CTexture__ProcessRowBatchesMcuStride128", "unaff_ESI"),
}

DOC_TOKENS = (
    "Wave711 decode allocator head",
    "decode-allocator-head-wave711",
    "0x0059bae0 CDXTexture__AllocFromBank_SplitBlock",
    "0x0059c5d0 CDXTexture__PumpDecodeAllocatorAndSetStage",
    "0x0059c070 CTexture__ProcessRowBatchesLinearStride",
    "0x0042f220 CSPtrSet__Clear",
    "G:\\GhidraBackups\\BEA_20260521-225104_post_wave711_decode_allocator_head_verified",
)

OVERCLAIM_TOKENS = (
    "runtime image decode behavior proven",
    "runtime texture behavior proven",
    "allocator-state layout proven",
    "decode-state layout proven",
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
        "pre-candidate-metadata.tsv": 11,
        "pre-candidate-tags.tsv": 11,
        "pre-candidate-xrefs.tsv": 25,
        "pre-candidate-instructions.tsv": 407,
        "decompile-candidate-pre/index.tsv": 11,
        "pre-metadata.tsv": 7,
        "pre-tags.tsv": 7,
        "pre-xrefs.tsv": 19,
        "pre-instructions.tsv": 1687,
        "decompile-pre/index.tsv": 7,
        "post-metadata.tsv": 7,
        "post-tags.tsv": 7,
        "post-xrefs.tsv": 19,
        "post-instructions.tsv": 1687,
        "decompile-post/index.tsv": 7,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    candidate_index = {normalize_address(row["address"]): row for row in read_tsv(BASE / "decompile-candidate-pre" / "index.tsv")}
    for address, (name, abi_token) in DEFERRED_ABI.items():
        require(address in candidate_index, f"deferred candidate missing from candidate index: {address}", failures)
        require(address not in metadata, f"deferred candidate unexpectedly appears in post metadata: {address}", failures)
        candidate_file = BASE / "decompile-candidate-pre" / f"{address[2:]}_{name}.c"
        require(candidate_file.is_file(), f"deferred candidate decompile missing: {address}", failures)
        if candidate_file.is_file():
            text = read_text(candidate_file)
            require(abi_token in text, f"deferred ABI token missing for {address}: {abi_token}", failures)

    for address, (name, signature, comment_tokens, expected_tags) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is None:
            continue
        require(row.get("name") == name, f"name mismatch at {address}", failures)
        require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
        require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
        comment = row.get("comment", "")
        require("Wave711 static read-back" in comment, f"missing Wave711 comment at {address}", failures)
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


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=7 renamed=0 would_rename=0 signature_updated=7 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=7 skipped=0 renamed=0 would_rename=0 signature_updated=7 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=7 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0",
        "export-pre-candidate-metadata.log": "targets=11 found=11 missing=0",
        "export-pre-candidate-tags.log": "ExportFunctionTagsByAddress complete: rows=11 missing=0",
        "export-pre-candidate-xrefs.log": "Wrote 25 rows",
        "export-pre-candidate-instructions.log": "Wrote 407 instruction rows",
        "export-pre-candidate-decompile.log": "targets=11 dumped=11 missing=0 failed=0",
        "export-pre-metadata.log": "targets=7 found=7 missing=0",
        "export-pre-tags.log": "ExportFunctionTagsByAddress complete: rows=7 missing=0",
        "export-pre-xrefs.log": "Wrote 19 rows",
        "export-pre-instructions.log": "Wrote 1687 instruction rows",
        "export-pre-decompile.log": "targets=7 dumped=7 missing=0 failed=0",
        "export-post-metadata.log": "targets=7 found=7 missing=0",
        "export-post-tags.log": "ExportFunctionTagsByAddress complete: rows=7 missing=0",
        "export-post-xrefs.log": "Wrote 19 rows",
        "export-post-instructions.log": "Wrote 1687 instruction rows",
        "export-post-decompile.log": "targets=7 dumped=7 missing=0 failed=0",
        "export-queue-refresh.log": "total_functions=6098 commented_functions=4132",
    }
    for log_name, token in expected.items():
        text = read_text(BASE / log_name)
        require(token in text, f"missing log token in {log_name}: {token}", failures)
        require("LockException" not in text, f"LockException in {log_name}", failures)
        require("BADNAME:" not in text and "MISSING:" not in text and "FAIL:" not in text, f"bad marker in {log_name}", failures)
    require("REPORT: Analysis succeeded for file: /BEA.exe" in read_text(BASE / "export-pre-metadata.log"), "pre-metadata auto-analysis note missing", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    signals = queue.get("qualitySignals", {})
    require(queue.get("status") == "PASS", "queue status not PASS", failures)
    require(queue.get("totalFunctions") == 6098, "queue total mismatch", failures)
    require(signals.get("commentlessFunctionCount") == 1966, "queue commentless mismatch", failures)
    require(signals.get("undefinedSignatureCount") == 1216, "queue undefined mismatch", failures)
    require(signals.get("paramSignatureCount") == 203, "queue param mismatch", failures)
    head = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(head["address"] == "0x0059c070", "high-signal head mismatch", failures)
    require(head["name"] == "CTexture__ProcessRowBatchesLinearStride", "high-signal head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == r"G:\GhidraBackups\BEA_20260521-225104_post_wave711_decode_allocator_head_verified", "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes", 0)) == 165776263, "backup byte count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    package = read_json(PACKAGE_JSON)
    require(package["scripts"].get("test:ghidra-decode-allocator-head-wave711") == "py -3 tools\\ghidra_decode_allocator_head_wave711_probe.py --check", "package script missing", failures)

    for path in (PUBLIC_NOTE, FUNCTION_INDEX, DXTEXTURE_DOC, GHIDRA_REFERENCE, CAMPAIGN, BACKLOG, DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE):
        text = read_text(path)
        normalized_text = text.replace("\\\\", "\\")
        for token in DOC_TOKENS:
            require(token in normalized_text, f"{path.relative_to(ROOT)} missing token: {token}", failures)
        lowered = text.lower()
        for token in OVERCLAIM_TOKENS:
            require(token not in lowered, f"{path.relative_to(ROOT)} has overclaim token: {token}", failures)

    for path in (LEDGER, ATTEMPT_LOG):
        rows = read_jsonl(path)
        require(any(row.get("task") == "Wave711 decode allocator head" for row in rows), f"{path.relative_to(ROOT)} missing Wave711 row", failures)

    tracking = read_json(TRACKING)
    require("Wave711 decode allocator head" in read_text(TRACKING), "tracking missing Wave711", failures)
    require(tracking.get("counters", {}).get("ledger_rows") == 1107, "tracking ledger row count mismatch", failures)
    require(tracking.get("counters", {}).get("attempt_rows") == 20367, "tracking attempt row count mismatch", failures)


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
        print("Wave711 decode allocator head probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave711 decode allocator head probe: PASS")
    print("Targets: 7")
    print("Queue: 6098 total, 4132 commented, 1966 commentless, 1216 undefined, 203 param_N")
    print("Backup: G:\\GhidraBackups\\BEA_20260521-225104_post_wave711_decode_allocator_head_verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
