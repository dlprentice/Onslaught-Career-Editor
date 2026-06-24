#!/usr/bin/env python3
"""Validate Wave686 CTexture channel/constant-tail read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave686-ctexture-channel-constant-tail"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_ctexture_channel_constant_tail_wave686_2026-05-21.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
TEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "texture.cpp" / "_index.md"
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
    "ctexture-channel-constant-tail-wave686",
    "wave686-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
}

TARGETS = {
    "0x0058e256": (
        "CTexture__ParseChannelMaskStrict",
        "uint __thiscall CTexture__ParseChannelMaskStrict(void * this, void * token_record, int unused_context)",
        ("ordered x/y/z/w", "0xf0000", "diagnostic 0x7d3"),
        BASE_TAGS | {"channel-mask", "parser-token", "shader-component-mask", "diagnostic-0x7d3", "tranche-head"},
    ),
    "0x0058e309": (
        "CTexture__ParseSwizzleMask",
        "uint __thiscall CTexture__ParseSwizzleMask(void * this, void * token_record, int unused_context)",
        ("up to four swizzle characters", "0xe40000", "diagnostic 0x7d4"),
        BASE_TAGS | {"swizzle-mask", "parser-token", "shader-component-mask", "diagnostic-0x7d4", "shader-operand"},
    ),
    "0x0058e3c3": (
        "CTexture__FlushPendingConstantTableWrites",
        "int __thiscall CTexture__FlushPendingConstantTableWrites(void * this, void * source_location, int unused_context)",
        ("pending constant dwords", "writer vtable slot", "advances +0x64"),
        BASE_TAGS | {"constant-stream", "pending-constant-flush", "writer-vtable", "source-location", "error-flag"},
    ),
    "0x0058e413": (
        "CTexture__EnsurePendingConstantCapacity",
        "int __thiscall CTexture__EnsurePendingConstantCapacity(void * this, int additional_dword_count, int unused_context)",
        ("pending constant dword array", "0x100 dwords", "out-of-memory HRESULT"),
        BASE_TAGS | {"constant-stream", "capacity-growth", "pending-constant-buffer", "allocator", "hresult"},
    ),
    "0x0058e491": (
        "CTexture__AppendPendingConstantEntry",
        "int __thiscall CTexture__AppendPendingConstantEntry(void * this, int constant_dword, int unused_context)",
        ("ensures capacity", "constant_dword", "increments the pending count"),
        BASE_TAGS | {"constant-stream", "pending-constant-append", "capacity-growth", "shader-constant", "hresult"},
    ),
    "0x0058e4b5": (
        "CTexture__ValidateInstructionOperandsAndReserveConstantSlots",
        "int __thiscall CTexture__ValidateInstructionOperandsAndReserveConstantSlots(void * this, void * instruction_record, uint unused_context)",
        ("shader version", "relative-addressing", "0x7e3-0x7ea"),
        BASE_TAGS | {"constant-stream", "instruction-operand-validation", "shader-version-gates", "relative-addressing", "diagnostic-report"},
    ),
    "0x0058ecdb": (
        "CTexture__FinalizeSymbolTablesIntoConstantStream",
        "int __fastcall CTexture__FinalizeSymbolTablesIntoConstantStream(void * constant_stream_context)",
        ("FINF owned-node list", "0x14-byte records", "diagnostic 0x7ef"),
        BASE_TAGS | {"constant-stream", "symbol-table-finalize", "finf-chunk", "debug-comment", "serialized-chunk"},
    ),
}

DOC_TOKENS = (
    "Wave686 CTexture channel constant tail",
    "ctexture-channel-constant-tail-wave686",
    "0x0058e256 CTexture__ParseChannelMaskStrict",
    "0x0058ecdb CTexture__FinalizeSymbolTablesIntoConstantStream",
    "0x0058eefb CTexture__ParseDebugChunkAndRelocateBindings",
)

OVERCLAIM_TOKENS = (
    "runtime texture compiler behavior proven",
    "channel-mask enum proven",
    "swizzle enum proven",
    "constant-stream format proven",
    "shader ABI encoding proven",
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
    require(len(read_tsv(BASE / "post-xrefs.tsv")) == 13, "post xref row count mismatch", failures)
    require(len(read_tsv(BASE / "post-instructions.tsv")) == 511, "post instruction row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-metadata.tsv")) == 7, "pre metadata row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-tags.tsv")) == 7, "pre tag row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-xrefs.tsv")) == 13, "pre xref row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-instructions.tsv")) == 511, "pre instruction row count mismatch", failures)
    require(len(read_tsv(BASE / "decompile-pre" / "index.tsv")) == 7, "pre decompile row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-metadata-candidate.tsv")) == 11, "candidate metadata row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-tags-candidate.tsv")) == 11, "candidate tag row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-xrefs-candidate.tsv")) == 20, "candidate xref row count mismatch", failures)
    require(len(read_tsv(BASE / "pre-instructions-candidate.tsv")) == 803, "candidate instruction row count mismatch", failures)
    require(len(read_tsv(BASE / "decompile-candidate-pre" / "index.tsv")) == 11, "candidate decompile row count mismatch", failures)

    for address, (name, expected_signature, comment_tokens, expected_tags) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is None:
            continue
        require(row.get("name") == name, f"name mismatch at {address}: {row.get('name')}", failures)
        require(row.get("signature") == expected_signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
        require(row.get("status") == "OK", f"metadata status mismatch at {address}: {row.get('status')}", failures)
        comment = row.get("comment", "")
        require("Wave686 static read-back" in comment, f"missing Wave686 comment at {address}", failures)
        require("Static metadata only" in comment, f"missing uncertainty clause at {address}", failures)
        for token in comment_tokens:
            require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(expected_tags.issubset(actual_tags), f"tags missing at {address}: {expected_tags - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}: {tag_row.get('status')}", failures)

        decompile_row = decompile_index.get(address)
        require(decompile_row is not None, f"missing decompile index for {address}", failures)
        if decompile_row is not None:
            require(decompile_row.get("signature") == expected_signature, f"decompile signature mismatch at {address}", failures)
            require(decompile_row.get("status") == "OK", f"decompile status mismatch at {address}", failures)
        require((BASE / "decompile-post" / f"{address[2:]}_{name}.c").is_file(), f"missing decompile file for {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected_exact = {
        "apply-wave686-dry.log": "SUMMARY: updated=0 skipped=7 renamed=0 would_rename=0 signature_updated=7 varargs=0 missing=0 bad=0",
        "apply-wave686-apply.log": "SUMMARY: updated=7 skipped=0 renamed=0 would_rename=0 signature_updated=7 varargs=0 missing=0 bad=0",
        "apply-wave686-final-dry.log": "SUMMARY: updated=0 skipped=7 renamed=0 would_rename=0 signature_updated=0 varargs=0 missing=0 bad=0",
        "post-metadata.log": "targets=7 found=7 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=7 missing=0",
        "post-decompile.log": "targets=7 dumped=7 missing=0 failed=0",
        "post-instructions.log": "Wrote 511 instruction rows",
        "post-xrefs.log": "Wrote 13 rows",
        "pre-metadata.log": "targets=7 found=7 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=7 missing=0",
        "pre-decompile.log": "targets=7 dumped=7 missing=0 failed=0",
        "pre-instructions.log": "Wrote 511 instruction rows",
        "pre-xrefs.log": "Wrote 13 rows",
        "pre-metadata-candidate.log": "targets=11 found=11 missing=0",
        "pre-tags-candidate.log": "ExportFunctionTagsByAddress complete: rows=11 missing=0",
        "pre-decompile-candidate.log": "targets=11 dumped=11 missing=0 failed=0",
        "pre-instructions-candidate.log": "Wrote 803 instruction rows",
        "pre-xrefs-candidate.log": "Wrote 20 rows",
        "queue-refresh.log": "total_functions=6098 commented_functions=3926",
    }
    for filename, token in expected_exact.items():
        text = read_text(BASE / filename)
        require(token in text, f"log token missing in {filename}: {token}", failures)
        require("REPORT: Save succeeded" in text, f"save report missing in {filename}", failures)
        require("LockException" not in text, f"LockException found in {filename}", failures)
        require("ERROR REPORT SCRIPT ERROR" not in text, f"script error found in {filename}", failures)
        require("BAD:" not in text and "BADNAME:" not in text and "MISSING:" not in text, f"bad/missing marker found in {filename}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    require(queue.get("status") == "PASS", "queue status not PASS", failures)
    require(queue.get("totalFunctions") == 6098, f"queue total mismatch: {queue.get('totalFunctions')}", failures)
    require(quality.get("commentlessFunctionCount") == 2172, f"commentless mismatch: {quality.get('commentlessFunctionCount')}", failures)
    require(quality.get("undefinedSignatureCount") == 1216, f"undefined mismatch: {quality.get('undefinedSignatureCount')}", failures)
    require(quality.get("paramSignatureCount") == 395, f"param mismatch: {quality.get('paramSignatureCount')}", failures)
    head = queue.get("priorityQueues", {}).get("commentlessHighSignal", [{}])[0]
    require(head.get("address") == "0x0058eefb", f"next head address mismatch: {head}", failures)
    require(head.get("name") == "CTexture__ParseDebugChunkAndRelocateBindings", f"next head name mismatch: {head}", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backup_path") == "G:/GhidraBackups/BEA_20260521-105415_post_wave686_ctexture_channel_constant_tail_verified", "backup path mismatch", failures)
    require(backup.get("file_count") == 19, f"backup file count mismatch: {backup}", failures)
    require(int(backup.get("total_bytes")) == 164727687, f"backup bytes mismatch: {backup}", failures)
    require(backup.get("diff_count") == 0, f"backup diff mismatch: {backup}", failures)


def check_docs(failures: list[str]) -> None:
    for path in (
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        TEXTURE_DOC,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ):
        text = read_text(path)
        for token in DOC_TOKENS:
            require(token in text, f"{path.relative_to(ROOT)} missing {token}", failures)
        for token in OVERCLAIM_TOKENS:
            require(token not in text, f"{path.relative_to(ROOT)} contains overclaim token {token}", failures)

    package = json.loads(read_text(PACKAGE_JSON))
    require(
        package.get("scripts", {}).get("test:ghidra-ctexture-channel-constant-tail-wave686")
        == "py -3 tools\\ghidra_ctexture_channel_constant_tail_wave686_probe.py --check",
        "package script missing/mismatched",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempt_rows = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave686 CTexture channel constant tail" for row in ledger_rows), "ledger missing Wave686", failures)
    require(any(row.get("task") == "Wave686 CTexture channel constant tail" for row in attempt_rows), "attempt log missing Wave686", failures)
    tracking = read_json(TRACKING)
    require(tracking.get("next_attempt_id") == 20342, f"tracking next_attempt_id mismatch: {tracking.get('next_attempt_id')}", failures)
    require(any("Wave686 CTexture channel constant tail" in note for note in tracking.get("notes", [])), "tracking notes missing Wave686", failures)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if not args.check:
        parser.error("expected --check")

    failures: list[str] = []
    check_metadata(failures)
    check_logs(failures)
    check_queue_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave686 CTexture channel/constant-tail probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave686 CTexture channel/constant-tail probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
