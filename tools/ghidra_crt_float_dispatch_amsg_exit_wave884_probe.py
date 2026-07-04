#!/usr/bin/env python3
"""Validate Wave884 CRT float-dispatch amsg-exit read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave884-crt-invalid-parameter-abort"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_crt_float_dispatch_amsg_exit_wave884_2026-05-26.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
CRT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "crt-seh.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

TASK = "Wave884 CRT float-dispatch amsg-exit"
TAG = "crt-float-dispatch-amsg-exit-wave884"
TARGET_ADDR = "0x00569cb8"
TARGET_NAME = "CRT__FloatDispatchAmsgExitCode2Thunk"
TARGET_SIG = "void CRT__FloatDispatchAmsgExitCode2Thunk(void)"
OLD_NAME = "ControlsUI__AbortInvalidParameter"
NEXT_HEAD = "0x005715b0 CFastVB__BuildStripBatchesFromIndexBuffer"
STRICT_PROXY = "5967/6113 = 97.61%"
BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260526-012542_post_wave884_crt_float_dispatch_amsg_exit_verified"

COMMON_TAGS = {
    "static-reaudit",
    TAG,
    "wave884-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-verified",
    "owner-corrected",
    "name-corrected",
    "important-crt-runtime-infrastructure",
    "high-importance-low-local-evidence-density",
    "compiler-runtime",
    "crt-runtime",
    "raw-commentless-head",
    "float-conversion-dispatch",
    "format-runtime",
    "input-runtime",
    "amsg-exit-code-2",
    "default-abort-thunk",
}

COMMENT_TOKENS = (
    "Wave884 static read-back",
    "stale ControlsUI label",
    "runtime error code 2",
    "__amsg_exit",
    "CRT__FormatOutputToStream",
    "CRT__InputFormatCore",
    "ControlsUI__FormatWideStringCore",
    "0x00653658 through 0x0065366c",
    "CRT__InitFloatConversionDispatchTable",
    "__cfltcvt",
    "__fassign",
    "CRT__InsertDecimalSeparatorBeforeExponent",
)

CORE_ANCHORS = (
    TASK,
    TAG,
    f"{TARGET_ADDR} {TARGET_NAME}",
    OLD_NAME,
    "__amsg_exit(2)",
    "0x00560289 __amsg_exit",
    "0x00561834 CRT__FormatOutputToStream",
    "0x00562cef CRT__InputFormatCore",
    "0x00565083 ControlsUI__FormatWideStringCore",
    "0x0055da8d CRT__InitFloatConversionDispatchTable",
    NEXT_HEAD,
    STRICT_PROXY,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime error/report/exit behavior proven",
    "exact float-dispatch table semantics proven",
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
        "pre-xrefs.tsv": 13,
        "pre-instructions.tsv": 4,
        "pre-decompile/index.tsv": 1,
        "pre-context-metadata.tsv": 5,
        "pre-context-tags.tsv": 5,
        "pre-context-xrefs.tsv": 20,
        "pre-context-instructions.tsv": 2102,
        "pre-context-decompile/index.tsv": 5,
        "post-metadata.tsv": 1,
        "post-tags.tsv": 1,
        "post-xrefs.tsv": 13,
        "post-instructions.tsv": 4,
        "post-decompile/index.tsv": 1,
        "post-context-metadata.tsv": 5,
        "post-context-decompile/index.tsv": 5,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    pre = read_tsv(BASE / "pre-metadata.tsv")[0]
    require(normalize_address(pre["address"]) == TARGET_ADDR, "pre target address mismatch", failures)
    require(pre["name"] == OLD_NAME, "pre target stale name mismatch", failures)
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
    decompile_text = read_text(BASE / "post-decompile" / "00569cb8_CRT__FloatDispatchAmsgExitCode2Thunk.c")
    require("__amsg_exit(2)" in decompile_text, "post decompile missing __amsg_exit(2)", failures)

    instructions = read_tsv(BASE / "post-instructions.tsv")
    require([row["mnemonic"] for row in instructions] == ["PUSH", "CALL", "POP", "RET"], "instruction mnemonic sequence mismatch", failures)
    require(instructions[0]["operands"] == "0x2", "first instruction operand mismatch", failures)
    require(instructions[1]["operands"] == "0x00560289", "call target mismatch", failures)

    xrefs = read_tsv(BASE / "post-xrefs.tsv")
    from_functions = {row["from_function"] for row in xrefs}
    for name in {"CRT__FormatOutputToStream", "CRT__InputFormatCore", "ControlsUI__FormatWideStringCore"}:
        require(name in from_functions, f"missing xref source function: {name}", failures)
    data_refs = {normalize_address(row["from_addr"]) for row in xrefs if row["ref_type"] == "DATA"}
    for address in ("0x00653658", "0x0065365c", "0x00653660", "0x00653664", "0x00653668", "0x0065366c"):
        require(address in data_refs, f"missing DATA table xref: {address}", failures)

    context_names = {row["name"] for row in read_tsv(BASE / "post-context-metadata.tsv")}
    for name in {"__amsg_exit", "CRT__InitFloatConversionDispatchTable", "CRT__FormatOutputToStream", "CRT__InputFormatCore", "ControlsUI__FormatWideStringCore"}:
        require(name in context_names, f"missing context metadata: {name}", failures)
    context_text = read_text(BASE / "post-context-decompile" / "0055da8d_CRT__InitFloatConversionDispatchTable.c")
    require("PTR_CRT__FloatDispatchAmsgExitCode2Thunk_00653658" in context_text, "context decompile missing renamed data label", failures)
    require("PTR_ControlsUI__AbortInvalidParameter" not in context_text, "context decompile retained stale data label", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=1 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=1 skipped=0 renamed=1 would_rename=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 missing=0 bad=0",
        "post-metadata.log": "targets=1 found=1 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=1 missing=0",
        "post-xrefs.log": "Wrote 13 rows",
        "post-instructions.log": "Wrote 4 function-body instruction rows",
        "post-decompile.log": "targets=1 dumped=1 missing=0 failed=0",
        "post-context-metadata.log": "targets=5 found=5 missing=0",
        "post-context-decompile.log": "targets=5 dumped=5 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6113 commented_functions=5967",
        "queue-probe.log": "Commentless functions: 146",
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave884.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave884_queue_probe.log",
    }
    for relative, token in expected.items():
        path = aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6113, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 146, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6113, "quality TSV row count mismatch", failures)
    require(commented == 5967, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5967, "quality TSV strict count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x005715b0", "raw head address mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CFastVB__BuildStripBatchesFromIndexBuffer", "raw head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 172788615 or backup.get("totalBytes") == 172788615.0, "backup byte count mismatch", failures)
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
        CRT_DOC,
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
    require(scripts.get("test:ghidra-crt-float-dispatch-amsg-exit-wave884") == r"py -3 tools\ghidra_crt_float_dispatch_amsg_exit_wave884_probe.py --check", "missing package script", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == TASK for row in ledger_rows), "missing Wave884 ledger row", failures)
    require(any(row.get("task") == TASK and row.get("attempt_id") == 20539 for row in attempts), "missing Wave884 attempt row", failures)


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
        print("Wave884 CRT float-dispatch amsg-exit probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave884 CRT float-dispatch amsg-exit probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
