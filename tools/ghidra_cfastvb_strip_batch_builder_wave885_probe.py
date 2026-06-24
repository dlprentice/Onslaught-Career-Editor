#!/usr/bin/env python3
"""Validate Wave885 CFastVB strip-batch builder read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave885-cfastvb-strip-emit-u16-batch"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cfastvb_strip_batch_builder_wave885_2026-05-26.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
DXMESHVB_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXMeshVB.cpp" / "_index.md"
FASTVB_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FastVB.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

TASK = "Wave885 CFastVB strip-batch builder"
TAG = "cfastvb-strip-batch-builder-wave885"
TARGET_ADDR = "0x005715b0"
TARGET_NAME = "CFastVB__BuildStripBatchesFromIndexBuffer"
TARGET_SIG = "int CFastVB__BuildStripBatchesFromIndexBuffer(void)"
CALLER_ADDR = "0x0056ecaa"
CALLER_NAME = "CDXMeshVB__BuildStripBatchesAndEmitIndexBuffer"
NEXT_HEAD = "0x00573d80 CTexture__InsertNodeIntoTree"
STRICT_PROXY = "5968/6113 = 97.63%"
BACKUP_PATH = r"G:\GhidraBackups\BEA_20260526-015531_post_wave885_cfastvb_strip_batch_builder_verified"

COMMON_TAGS = {
    "static-reaudit",
    TAG,
    "wave885-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-verified",
    "stack-locked-abi",
    "hidden-register-context",
    "important-render-infrastructure",
    "high-importance-low-local-evidence-density",
    "raw-commentless-head",
    "cfastvb-strip-pipeline",
    "strip-batch-builder",
    "index-word-span",
    "triangle-adjacency",
    "candidate-generation",
    "batch-merge-order",
    "ret-0x18",
}

COMMENT_TOKENS = (
    "Wave885 static read-back",
    "CFastVB strip-batch builder",
    CALLER_NAME,
    CALLER_ADDR,
    "16-bit index-word span",
    "CFastVB__BuildTriangleAdjacency",
    "CFastVB__GenerateStripCandidatesFromAdjacency",
    "CFastVB__MergeAndOrderStripBatches",
    "candidate, edge-bucket, overflow, and local span buffers",
    "ECX receiver context",
    "RET 0x18",
    "locked/hidden parameter storage",
    "preserves the current signature display",
)

CORE_ANCHORS = (
    TASK,
    TAG,
    f"{TARGET_ADDR} {TARGET_NAME}",
    CALLER_NAME,
    "CFastVB__BuildTriangleAdjacency",
    "CFastVB__GenerateStripCandidatesFromAdjacency",
    "CFastVB__MergeAndOrderStripBatches",
    "RET 0x18",
    "locked/hidden parameter storage",
    NEXT_HEAD,
    STRICT_PROXY,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime strip quality proven",
    "concrete d3d index-buffer behavior proven",
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
        "pre-metadata.tsv": 1,
        "pre-tags.tsv": 1,
        "pre-xrefs.tsv": 1,
        "pre-instructions.tsv": 239,
        "pre-decompile/index.tsv": 1,
        "pre-context-metadata.tsv": 7,
        "pre-context-tags.tsv": 7,
        "pre-context-xrefs.tsv": 15,
        "pre-context-instructions.tsv": 2093,
        "pre-context-decompile/index.tsv": 7,
        "post-metadata.tsv": 1,
        "post-tags.tsv": 1,
        "post-xrefs.tsv": 1,
        "post-instructions.tsv": 239,
        "post-decompile/index.tsv": 1,
        "post-context-metadata.tsv": 7,
        "post-context-decompile/index.tsv": 7,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    pre = read_tsv(BASE / "pre-metadata.tsv")[0]
    require(normalize_address(pre["address"]) == TARGET_ADDR, "pre target address mismatch", failures)
    require(pre["name"] == TARGET_NAME, "pre target name mismatch", failures)
    require(pre["signature"] == TARGET_SIG, "pre target signature mismatch", failures)
    require(not pre.get("comment", "").strip(), "pre target unexpectedly had a comment", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    row = metadata.get(TARGET_ADDR)
    require(row is not None, "missing post target metadata", failures)
    if row is not None:
        comment = row.get("comment", "")
        require(row.get("name") == TARGET_NAME, "post target name mismatch", failures)
        require(row.get("signature") == TARGET_SIG, f"post target signature mismatch: {row.get('signature')}", failures)
        require(row.get("status") == "OK", "post metadata status mismatch", failures)
        for token in COMMENT_TOKENS:
            require(token in comment, f"missing post comment token: {token}", failures)

    tag_row = read_tsv(BASE / "post-tags.tsv")[0]
    actual_tags = set(tag_row.get("tags", "").split(";"))
    require(COMMON_TAGS.issubset(actual_tags), f"post tags missing: {COMMON_TAGS - actual_tags}", failures)
    require(tag_row.get("status") == "OK", "post tag status mismatch", failures)

    dec = read_tsv(BASE / "post-decompile" / "index.tsv")[0]
    require(normalize_address(dec["address"]) == TARGET_ADDR, "post decompile address mismatch", failures)
    require(dec["name"] == TARGET_NAME, "post decompile name mismatch", failures)
    require(dec["signature"] == TARGET_SIG, "post decompile signature mismatch", failures)
    decompile_text = read_text(BASE / "post-decompile" / "005715b0_CFastVB__BuildStripBatchesFromIndexBuffer.c")
    for token in (
        "in_ECX",
        "in_stack_00000004",
        "CFastVB__BuildTriangleAdjacency",
        "CFastVB__GenerateStripCandidatesFromAdjacency",
        "CFastVB__MergeAndOrderStripBatches",
        "CFastVB__ReleaseBufferAndResetTriplet_0056f260",
        "CFastVB__CountWordElements",
    ):
        require(token in decompile_text, f"post decompile missing token: {token}", failures)

    instructions = read_tsv(BASE / "post-instructions.tsv")
    last = instructions[-1]
    require(last["instruction_addr"] == "0x00571869", "last instruction address mismatch", failures)
    require(last["mnemonic"] == "RET", "last instruction mnemonic mismatch", failures)
    require(last["operands"] == "0x18", "RET operand mismatch", failures)
    require(any(row["mnemonic"] == "CALL" and row["operands"] == "0x0056f620" for row in instructions), "missing adjacency call instruction", failures)
    require(any(row["mnemonic"] == "CALL" and row["operands"] == "0x005725e0" for row in instructions), "missing candidate-generation call instruction", failures)
    require(any(row["mnemonic"] == "CALL" and row["operands"] == "0x005718c0" for row in instructions), "missing merge/order call instruction", failures)

    xref = read_tsv(BASE / "post-xrefs.tsv")[0]
    require(normalize_address(xref["target_addr"]) == TARGET_ADDR, "xref target mismatch", failures)
    require(normalize_address(xref["from_addr"]) == CALLER_ADDR, "xref caller address mismatch", failures)
    require(normalize_address(xref["from_function_addr"]) == "0x0056eb90", "xref caller function address mismatch", failures)
    require(xref["from_function"] == CALLER_NAME, "xref caller function mismatch", failures)
    require(xref["ref_type"] == "UNCONDITIONAL_CALL", "xref ref type mismatch", failures)

    context_names = {row["name"] for row in read_tsv(BASE / "post-context-metadata.tsv")}
    for name in {
        CALLER_NAME,
        "CFastVB__EmitTriangleStripIndexBuffer",
        "CFastVB__HasDuplicateTriangleIndices32",
        "CFastVB__HasDuplicateTriangleIndices16",
        "CFastVB__MergeAndOrderStripBatches",
        "CFastVB__SeedVertexCacheFromTriangleRefs",
    }:
        require(name in context_names, f"missing context metadata: {name}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=1 skipped=0 renamed=0 would_rename=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 missing=0 bad=0",
        "post-metadata.log": "targets=1 found=1 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=1 missing=0",
        "post-xrefs.log": "Wrote 1 rows",
        "post-instructions.log": "Wrote 239 function-body instruction rows",
        "post-decompile.log": "targets=1 dumped=1 missing=0 failed=0",
        "post-context-metadata.log": "targets=7 found=7 missing=0",
        "post-context-decompile.log": "targets=7 dumped=7 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6113 commented_functions=5968",
        "queue-probe.log": "Commentless functions: 145",
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave885.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave885_queue_probe.log",
    }
    for relative, token in expected.items():
        path = aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "Input file not found", "Script not found", "MISSING:", "BADNAME:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    badpath_expectations = {
        "badpath-pre-metadata.log": "Input file not found",
        "badpath-pre-tags.log": "Input file not found",
        "badpath-pre-xrefs.log": "Script not found",
    }
    for relative, token in badpath_expectations.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing preserved badpath token in {relative}: {token}", failures)
        require("LockException" not in text, f"unexpected LockException in {relative}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6113, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 145, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(queue["priorityQueues"]["commentlessHighSignal"] == [], "high-signal queue not empty", failures)
    require(queue["priorityQueues"]["signature"] == [], "signature queue not empty", failures)
    require(queue["priorityQueues"]["nameConfidence"] == [], "name-confidence queue not empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6113, "quality TSV row count mismatch", failures)
    require(commented == 5968, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5968, "quality TSV strict count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x00573d80", "raw head address mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CTexture__InsertNodeIntoTree", "raw head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 172821383 or backup.get("totalBytes") == 172821383.0, "backup byte count mismatch", failures)
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
        DXMESHVB_DOC,
        FASTVB_DOC,
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
    require(scripts.get("test:ghidra-cfastvb-strip-batch-builder-wave885") == r"py -3 tools\ghidra_cfastvb_strip_batch_builder_wave885_probe.py --check", "missing package script", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == TASK for row in ledger_rows), "missing Wave885 ledger row", failures)
    require(any(row.get("task") == TASK and row.get("attempt_id") == 20540 for row in attempts), "missing Wave885 attempt row", failures)


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
        print("Wave885 CFastVB strip-batch builder probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave885 CFastVB strip-batch builder probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
