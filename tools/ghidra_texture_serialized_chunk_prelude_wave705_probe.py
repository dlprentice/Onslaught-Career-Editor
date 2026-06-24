#!/usr/bin/env python3
"""Validate Wave705 texture serialized-chunk prelude read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave705-texture-serialized-chunk-prelude"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_texture_serialized_chunk_prelude_wave705_2026-05-21.md"
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
QUALITY_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BASE_SIGNATURE_TAGS = {
    "static-reaudit",
    "texture-serialized-chunk-prelude-wave705",
    "wave705-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
}
BASE_COMMENT_TAGS = {
    "static-reaudit",
    "texture-serialized-chunk-prelude-wave705",
    "wave705-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "comment-only",
}

TARGETS = {
    "0x0059902a": (
        "CDXTexture__RegisterSerializedChunk",
        "int CDXTexture__RegisterSerializedChunk(void)",
        ("hidden-ECX", "0xffffffff", "optional output offset"),
        BASE_COMMENT_TAGS | {"serialized-chunk", "chunk-registry", "dedupe", "hidden-ecx", "locked-storage", "tranche-head"},
    ),
    "0x00599161": (
        "CTexture__ComputeDebugChunkDwordCount",
        "int __fastcall CTexture__ComputeDebugChunkDwordCount(void * chunk_builder)",
        ("debug chunk dword count", "0xfffe", "chunk_builder"),
        BASE_SIGNATURE_TAGS | {"serialized-chunk", "debug-chunk", "dword-count", "fastcall-param-named"},
    ),
    "0x0059916d": (
        "CTexture__SerializeDebugChunkSymbolRecords",
        "int __thiscall CTexture__SerializeDebugChunkSymbolRecords(void * this, uint * out_chunk_dwords, uint max_dword_count)",
        ("0xfffe", "0xabababab", "RET 0x8"),
        BASE_SIGNATURE_TAGS | {"serialized-chunk", "debug-chunk", "symbol-records", "padding", "phantom-param-removed"},
    ),
    "0x00599258": (
        "CFastVB__ComputeNodeSpanAndStride",
        "int __stdcall CFastVB__ComputeNodeSpanAndStride(void * node_tree, uint * out_span, uint * out_stride)",
        ("node kinds 8, 7, and 1", "A null out_stride", "span and stride"),
        BASE_SIGNATURE_TAGS | {"node-tree", "span-stride", "recursive", "stdcall-params-named"},
    ),
    "0x0059930d": (
        "CTexture__ValidateConstantRegisterDeclarationType",
        "int __thiscall CTexture__ValidateConstantRegisterDeclarationType(void * this, void * match_template_words32, void * register_decl, uint * out_component_count)",
        ("0xb54", "0xb55", "RET 0xc"),
        BASE_SIGNATURE_TAGS | {"constant-register", "node-tree", "diagnostic", "phantom-param-removed"},
    ),
    "0x00599406": (
        "CDXTexture__SerializeFloatGridChunk",
        "int __stdcall CDXTexture__SerializeFloatGridChunk(void * chunk_builder, uint row_count, uint column_count, void * value_source, uint * out_chunk_offset)",
        ("float-grid", "chunk kind 6", "RET 0x14"),
        BASE_SIGNATURE_TAGS | {"serialized-chunk", "float-grid", "chunk-kind-6", "ret-0x14", "arity-restored"},
    ),
    "0x005994c4": (
        "CDXTexture__ProcessTextureChunkAndEmitBindings",
        "int CDXTexture__ProcessTextureChunkAndEmitBindings(void)",
        ("locked-storage", "8191", "output header fields"),
        BASE_COMMENT_TAGS | {"texture-binding", "constant-register", "serialized-chunk", "hidden-stack", "locked-storage", "tranche-tail"},
    ),
}

DOC_TOKENS = (
    "Wave705 texture serialized-chunk prelude",
    "texture-serialized-chunk-prelude-wave705",
    "0x0059902a CDXTexture__RegisterSerializedChunk",
    "0x005994c4 CDXTexture__ProcessTextureChunkAndEmitBindings",
    "0x0042f220 CSPtrSet__Clear",
    "0x005997a5 CFastVB__InitNodeType17",
)

OVERCLAIM_TOKENS = (
    "runtime shader/texture behavior proven",
    "runtime vertex-buffer behavior proven",
    "chunk-builder layout proven",
    "binding record layout proven",
    "node/declaration layout proven",
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
        "pre-metadata.tsv": 7,
        "pre-tags.tsv": 7,
        "pre-xrefs.tsv": 29,
        "pre-instructions.tsv": 847,
        "decompile-pre/index.tsv": 7,
        "post-metadata.tsv": 7,
        "post-tags.tsv": 7,
        "post-xrefs.tsv": 29,
        "post-instructions.tsv": 847,
        "decompile-post/index.tsv": 7,
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
        require("Wave705 static read-back" in comment, f"missing Wave705 comment at {address}", failures)
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
        require((BASE / "decompile-post" / f"{address[2:]}_{name}.c").is_file(), f"missing decompile file for {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-wave705-dry2.log": "SUMMARY: updated=0 skipped=7 renamed=0 would_rename=0 signature_updated=5 comment_only_updated=2 missing=0 bad=0",
        "apply-wave705-apply.log": "SUMMARY: updated=7 skipped=0 renamed=0 would_rename=0 signature_updated=5 comment_only_updated=2 missing=0 bad=0",
        "apply-wave705-final-dry.log": "SUMMARY: updated=0 skipped=7 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "export-pre-metadata.log": "targets=7 found=7 missing=0",
        "export-pre-tags.log": "ExportFunctionTagsByAddress complete: rows=7 missing=0",
        "export-pre-xrefs.log": "Wrote 29 rows",
        "export-pre-instructions.log": "Wrote 847 instruction rows",
        "export-pre-decompile.log": "targets=7 dumped=7 missing=0 failed=0",
        "export-post-metadata.log": "targets=7 found=7 missing=0",
        "export-post-tags.log": "ExportFunctionTagsByAddress complete: rows=7 missing=0",
        "export-post-xrefs.log": "Wrote 29 rows",
        "export-post-instructions.log": "Wrote 847 instruction rows",
        "export-post-decompile.log": "targets=7 dumped=7 missing=0 failed=0",
    }
    for filename, token in expected.items():
        text = read_text(BASE / filename)
        require(token in text, f"log token missing in {filename}: {token}", failures)
        require("REPORT: Save succeeded" in text, f"save report missing in {filename}", failures)
        require("Input file not found" not in text, f"bad input path found in {filename}", failures)
        require("LockException" not in text, f"LockException found in {filename}", failures)
        require("ERROR REPORT SCRIPT ERROR" not in text, f"script error found in accepted log {filename}", failures)
        require("BAD:" not in text and "BADNAME:" not in text and "MISSING:" not in text, f"bad/missing marker found in {filename}", failures)

    queue_refresh = read_text(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave705.log")
    require("total_functions=6098 commented_functions=4095" in queue_refresh, "queue refresh count mismatch", failures)
    require("REPORT: Save succeeded" in queue_refresh, "queue refresh save report missing", failures)
    queue_probe = read_text(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave705_queue_probe.log")
    require("Status: PASS" in queue_probe, "queue probe did not pass", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    require(queue.get("status") == "PASS", "queue status not PASS", failures)
    require(queue.get("totalFunctions") == 6098, f"queue total mismatch: {queue.get('totalFunctions')}", failures)
    require(quality.get("commentlessFunctionCount") == 2003, f"commentless mismatch: {quality.get('commentlessFunctionCount')}", failures)
    require(quality.get("undefinedSignatureCount") == 1216, f"undefined mismatch: {quality.get('undefinedSignatureCount')}", failures)
    require(quality.get("paramSignatureCount") == 238, f"param mismatch: {quality.get('paramSignatureCount')}", failures)
    high_signal_head = queue.get("priorityQueues", {}).get("commentlessHighSignal", [{}])[0]
    require(high_signal_head.get("address") == "0x005997a5", f"high-signal head address mismatch: {high_signal_head}", failures)
    require(high_signal_head.get("name") == "CFastVB__InitNodeType17", f"high-signal head name mismatch: {high_signal_head}", failures)

    rows = read_tsv(QUALITY_TSV)
    param_re = re.compile(r"\bparam_\d+\b")
    clean = [
        row for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not param_re.search(row.get("signature", ""))
    ]
    require(len(clean) == 4041, f"strict clean proxy mismatch: {len(clean)}", failures)

    commentless = [row for row in rows if not row.get("comment", "").strip()]
    require(bool(commentless), "no commentless rows found", failures)
    if commentless:
        require(normalize_address(commentless[0].get("address", "")) == "0x0042f220", f"raw commentless head mismatch: {commentless[0]}", failures)
        require(commentless[0].get("name") == "CSPtrSet__Clear", f"raw commentless head name mismatch: {commentless[0]}", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == "G:\\GhidraBackups\\BEA_20260521-194929_post_wave705_texture_serialized_chunk_prelude_verified", "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, f"backup file count mismatch: {backup.get('fileCount')}", failures)
    require(int(backup.get("totalBytes", -1)) == 165448583, f"backup byte count mismatch: {backup.get('totalBytes')}", failures)
    require(backup.get("diffCount") == 0, f"backup diff count mismatch: {backup.get('diffCount')}", failures)


def check_docs(failures: list[str]) -> None:
    doc_paths = [
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        DXTEXTURE_DOC,
        FASTVB_DOC,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in doc_paths:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(token in text, f"missing doc token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for token in OVERCLAIM_TOKENS:
            require(token not in lowered, f"overclaim token found in {path.relative_to(ROOT)}: {token}", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:ghidra-texture-serialized-chunk-prelude-wave705")
        == "py -3 tools\\ghidra_texture_serialized_chunk_prelude_wave705_probe.py --check",
        "package script missing",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempt_rows = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave705 texture serialized-chunk prelude" for row in ledger_rows), "ledger row missing", failures)
    require(
        any(
            row.get("attempt_id") == 20360
            and row.get("task") == "Wave705 texture serialized-chunk prelude"
            and row.get("readback") == "verified"
            for row in attempt_rows
        ),
        "attempt row missing",
        failures,
    )
    tracking = read_json(TRACKING)
    require(tracking.get("next_attempt_id") == 20361, f"next_attempt_id mismatch: {tracking.get('next_attempt_id')}", failures)
    counters = tracking.get("counters", {})
    require(counters.get("ledger_rows") == 1101, f"ledger_rows mismatch: {counters.get('ledger_rows')}", failures)
    require(counters.get("attempt_rows") == 20361, f"attempt_rows mismatch: {counters.get('attempt_rows')}", failures)
    require(counters.get("completed") == 1092, f"completed mismatch: {counters.get('completed')}", failures)


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
        print("Wave705 texture serialized-chunk prelude probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Wave705 texture serialized-chunk prelude probe: PASS")
    print("Targets: 7")
    print("Queue: 6098 total, 4095 commented, 2003 commentless, 1216 exact-undefined, 238 param_N")
    print("Strict clean-signature proxy: 4041/6098 = 66.27%")
    print("Raw commentless head: 0x0042f220 CSPtrSet__Clear")
    print("High-signal head: 0x005997a5 CFastVB__InitNodeType17")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
