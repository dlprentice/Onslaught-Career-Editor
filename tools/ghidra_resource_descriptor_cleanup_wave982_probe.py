#!/usr/bin/env python3
"""Validate Wave982 resource-descriptor cleanup correction artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave982-resource-descriptor-cleanup-review"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
NOTE = ROOT / "release" / "readiness" / "ghidra_resource_descriptor_cleanup_wave982_2026-05-30.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
DXLANDSCAPE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXLandscape.cpp" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"

TARGET = "0x00403ff0"
OLD_NAME = "CDXLandscape__DestroyResourceDescriptorArray_Thunk"
NEW_NAME = "CResourceDescriptorTable__DestroyEmbeddedDescriptor_Thunk"
SIGNATURE = f"void __thiscall {NEW_NAME}(void * this)"
BACKUP_PATH = r"G:\GhidraBackups\BEA_20260530-232843_post_wave982_resource_descriptor_cleanup_verified"

REQUIRED_TAGS = {
    "static-reaudit",
    "resource-descriptor-cleanup-wave982",
    "wave982-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-verified",
    "rename-corrected",
    "resource-descriptor",
    "compiler-unwind",
}

XREF_FUNCTIONS = {
    "Unwind@005d0fb0",
    "Unwind@005d1062",
    "Unwind@005d196b",
    "Unwind@005d2070",
    "Unwind@005d2470",
    "Unwind@005d2580",
    "Unwind@005d2760",
    "Unwind@005d4900",
    "Unwind@005d4bd0",
    "Unwind@005d52e0",
}

DOC_TOKENS = (
    "Wave982",
    "resource-descriptor-cleanup-wave982",
    "CResourceDescriptorTable__DestroyEmbeddedDescriptor_Thunk",
    "CDXLandscape__DestroyResourceDescriptorArray_Thunk",
    "6222/6222 = 100.00%",
    "376/1408 = 26.70%",
    "435/1478 = 29.43%",
    BACKUP_PATH,
)

OVERCLAIMS = (
    "runtime cleanup behavior proven",
    "exact source identity proven",
    "descriptor-table layout proven",
    "rebuild parity proven",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig", errors="replace").replace("\x00", "")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in read_text(path).splitlines() if line.strip()]


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def row_by_address(rows: list[dict[str, str]], address: str, field: str = "address") -> dict[str, str] | None:
    target = normalize_address(address)
    for row in rows:
        if normalize_address(row.get(field, "")) == target:
            return row
    return None


def check_counts(failures: list[str]) -> None:
    expected = {
        "metadata.tsv": 8,
        "tags.tsv": 8,
        "xrefs.tsv": 151,
        "instructions.tsv": 193,
        "decompile/index.tsv": 8,
        "post-metadata.tsv": 8,
        "post-tags.tsv": 8,
        "post-xrefs.tsv": 151,
        "post-instructions.tsv": 193,
        "post-decompile/index.tsv": 8,
    }
    for relative, count in expected.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == count, f"{relative} row count {actual} != {count}", failures)


def check_logs(failures: list[str]) -> None:
    expected_tokens = {
        "metadata.log": ("targets=8 found=8 missing=0",),
        "tags.log": ("ExportFunctionTagsByAddress complete: rows=8 missing=0",),
        "xrefs.log": ("Wrote 151 rows",),
        "instructions.log": ("Wrote 193 function-body instruction rows", "targets=8 missing=0"),
        "decompile.log": ("targets=8 dumped=8 missing=0 failed=0",),
        "apply-dry.log": ("would_rename=1", "signature_updated=1", "comment_only_updated=1", "missing=0 bad=0"),
        "apply.log": ("updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0", "REPORT: Save succeeded"),
        "apply-final-dry.log": ("updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0", "REPORT: Save succeeded"),
        "post-metadata.log": ("targets=8 found=8 missing=0",),
        "post-tags.log": ("ExportFunctionTagsByAddress complete: rows=8 missing=0",),
        "post-xrefs.log": ("Wrote 151 rows",),
        "post-instructions.log": ("Wrote 193 function-body instruction rows", "targets=8 missing=0"),
        "post-decompile.log": ("targets=8 dumped=8 missing=0 failed=0",),
    }
    bad_tokens = ("LockException", "ERROR REPORT SCRIPT ERROR", "MISSING:", "BADNAME:", "BADSIG:", "BADCOMMENT:", "BADTAGS:", "missing=1", "bad=1", "failed=1")
    for relative, tokens in expected_tokens.items():
        text = read_text(BASE / relative)
        for token in tokens:
            require(token in text, f"{relative} missing token: {token}", failures)
        for bad in bad_tokens:
            require(bad not in text, f"{relative} contains bad token: {bad}", failures)


def check_saved_row(failures: list[str]) -> None:
    pre = row_by_address(read_tsv(BASE / "metadata.tsv"), TARGET)
    post = row_by_address(read_tsv(BASE / "post-metadata.tsv"), TARGET)
    require(pre is not None and pre.get("name") == OLD_NAME, "pre metadata did not capture old saved name", failures)
    require(post is not None, "post metadata missing target", failures)
    if post:
        require(post.get("name") == NEW_NAME, "post metadata name mismatch", failures)
        require(post.get("signature") == SIGNATURE, "post metadata signature mismatch", failures)
        for token in ("Wave982 static re-audit correction", "element size 0x41c", "CResourceDescriptor__dtor", "exact source identity"):
            require(token in post.get("comment", ""), f"post comment missing {token}", failures)

    tag_row = row_by_address(read_tsv(BASE / "post-tags.tsv"), TARGET)
    require(tag_row is not None, "post tags missing target", failures)
    if tag_row:
        actual = set(tag_row.get("tags", "").split(";"))
        require(REQUIRED_TAGS.issubset(actual), f"post tags missing {sorted(REQUIRED_TAGS - actual)}", failures)

    quality_row = row_by_address(read_tsv(QUEUE_TSV), TARGET)
    require(quality_row is not None, "quality row missing target", failures)
    if quality_row:
        require(quality_row.get("name") == NEW_NAME, "quality row name mismatch", failures)
        require(quality_row.get("signature") == SIGNATURE, "quality row signature mismatch", failures)


def check_xrefs_instructions_decompile(failures: list[str]) -> None:
    xrefs = [row for row in read_tsv(BASE / "post-xrefs.tsv") if normalize_address(row.get("target_addr", "")) == TARGET]
    require(len(xrefs) == 12, f"target xref count {len(xrefs)} != 12", failures)
    functions = {row.get("from_function", "") for row in xrefs}
    require(XREF_FUNCTIONS.issubset(functions), f"missing xref functions: {sorted(XREF_FUNCTIONS - functions)}", failures)
    data_refs = {normalize_address(row.get("from_addr", "")) for row in xrefs if row.get("ref_type") == "DATA"}
    require({"0x00515f30", "0x00515f90"}.issubset(data_refs), "missing descriptor table DATA refs", failures)

    instructions = [row for row in read_tsv(BASE / "post-instructions.tsv") if normalize_address(row.get("target_addr", "")) == TARGET]
    observed = {(row.get("mnemonic", ""), row.get("operands", "").lower()) for row in instructions}
    for pair in (("PUSH", "0x403f80"), ("PUSH", "0x1"), ("ADD", "ecx, 0x8"), ("PUSH", "0x41c"), ("CALL", "0x0055db0a"), ("RET", "")):
        require(pair in observed, f"missing instruction {pair}", failures)

    index_row = row_by_address(read_tsv(BASE / "post-decompile" / "index.tsv"), TARGET)
    require(index_row is not None and index_row.get("name") == NEW_NAME and index_row.get("signature") == SIGNATURE, "decompile index mismatch", failures)
    decompile = read_text(BASE / "post-decompile" / f"00403ff0_{NEW_NAME}.c")
    for token in ("CRT__EhVectorDestructorIterator_WithUnwind", "CResourceDescriptor__dtor", "((int)this + 8)", "0x41c"):
        require(token in decompile, f"decompile missing {token}", failures)


def check_queue_backup_docs(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    require(queue.get("totalFunctions") == 6222, "queue total mismatch", failures)
    require(quality.get("commentlessFunctionCount") == 0, "queue commentless mismatch", failures)
    require(quality.get("undefinedSignatureCount") == 0, "queue undefined mismatch", failures)
    require(quality.get("paramSignatureCount") == 0, "queue param_N mismatch", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes", 0)) == 173837191, "backup byte count mismatch", failures)
    for key in ("missingCount", "extraCount", "diffCount", "hashDiffCount"):
        require(backup.get(key) == 0, f"backup {key} mismatch", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:ghidra-resource-descriptor-cleanup-wave982")
        == r"py -3 tools\ghidra_resource_descriptor_cleanup_wave982_probe.py --check",
        "package script mismatch",
        failures,
    )

    docs = [NOTE, GHIDRA_REFERENCE, CAMPAIGN, FUNCTION_INDEX, DXLANDSCAPE_DOC, FUNCTION_COVERAGE, BACKLOG, DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE]
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(token in text or token.replace("\\", "\\\\") in text, f"{path.relative_to(ROOT)} missing token: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lower, f"{path.relative_to(ROOT)} contains overclaim token: {bad}", failures)

    ledger = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave982 resource descriptor cleanup correction" and row.get("status") == "completed" for row in ledger), "missing Wave982 ledger row", failures)
    require(any(row.get("task") == "Wave982 resource descriptor cleanup correction" and row.get("attempt_id") == 20573 for row in attempts), "missing Wave982 attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    failures: list[str] = []
    check_counts(failures)
    check_logs(failures)
    check_saved_row(failures)
    check_xrefs_instructions_decompile(failures)
    check_queue_backup_docs(failures)

    if failures:
        print("Wave982 resource-descriptor cleanup probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1 if args.check else 0

    print("Wave982 resource-descriptor cleanup probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
