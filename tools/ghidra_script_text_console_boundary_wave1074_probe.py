#!/usr/bin/env python3
"""Validate Wave1074 script text console boundary read-back artifacts."""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1074-script-text-console-boundary"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_script_text_console_boundary_wave1074_2026-06-02.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1074_recheck_2026-06-02.md"
PACKAGE_JSON = ROOT / "package.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
BACKUP_PATH = r"G:\GhidraBackups\BEA_20260602-052830_post_wave1074_script_text_console_boundary_verified"
BACKUP_SUMMARY = BASE / "backup-summary.json"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"

TARGET = "0x00537c40"
TARGET_NAME = "IScript__PrintText"
TARGET_SIGNATURE = "void __stdcall IScript__PrintText(void * script_args, void * unused_state, void * out_result)"
COMMON_TAGS = {
    "static-reaudit",
    "script-text-console-boundary-wave1074",
    "wave1074-readback-verified",
    "retail-binary-evidence",
    "function-boundary-recovered",
    "mission-script",
    "script-command",
    "print-text",
    "text-lookup",
    "console-output",
    "signature-hardened",
    "comment-hardened",
}

CORE_DOCS = [
    PUBLIC_NOTE,
    AGGREGATE_NOTE,
    ROOT / "README.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md",
    ROOT / "developer_agent_state.json",
    ROOT / "documentation_agent_state.json",
    ROOT / "re_orchestrator_state.json",
]

OWNER_DOCS = [
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "IScript.cpp.md",
]

DOC_TOKENS = (
    "Wave1074",
    "script-text-console-boundary-wave1074",
    "0x00537c40 IScript__PrintText",
    "s_PrintText_0064f984",
    "0x0064d220",
    "0x0064d250",
    "0x00537c69",
    "0x00537c70",
    "CText__GetStringById",
    "CConsole__Printf",
    "812/1408 = 57.67%",
    "1358/1560 = 87.05%",
    "500/500 = 100.00%",
    "6247/6247 = 100.00%",
    BACKUP_PATH,
)

OWNER_DOC_TOKENS = DOC_TOKENS + (
    "PrintText",
    "void __stdcall IScript__PrintText",
)

OVERCLAIMS = (
    "runtime behavior proven",
    "runtime missionscript dispatch behavior proven",
    "runtime console behavior proven",
    "exact command descriptor schema proven",
    "exact source-body identity proven",
    "rebuild parity proven",
    "fully reverse-engineered",
    "all systems complete",
)


def norm(address: str) -> str:
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


def strict_clean_count(rows: list[dict[str, str]]) -> int:
    total = 0
    for row in rows:
        comment = row.get("comment", "").strip()
        signature = row.get("signature", "")
        if comment and not signature.startswith("undefined ") and not re.search(r"\bparam_\d+\b", signature):
            total += 1
    return total


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-diagnose.tsv": 1,
        "pre-metadata.tsv": 1,
        "pre-xrefs.tsv": 1,
        "pre-instructions.tsv": 228,
        "pre-decompile/index.tsv": 1,
        "context-metadata.tsv": 5,
        "context-xrefs.tsv": 704,
        "context-instructions.tsv": 185,
        "context-decompile/index.tsv": 5,
        "post-diagnose.tsv": 1,
        "post-metadata.tsv": 1,
        "post-tags.tsv": 1,
        "post-xrefs.tsv": 1,
        "post-body-instructions.tsv": 13,
        "post-decompile/index.tsv": 1,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    pre_diag = read_tsv(BASE / "pre-diagnose.tsv")[0]
    require(pre_diag.get("status") == "INSTRUCTION_NO_FUNCTION", "pre diagnose status mismatch", failures)
    pre_meta = read_tsv(BASE / "pre-metadata.tsv")[0]
    require(pre_meta.get("status") == "MISSING", "pre metadata should be missing", failures)
    pre_dec = read_tsv(BASE / "pre-decompile" / "index.tsv")[0]
    require(pre_dec.get("status") == "MISSING", "pre decompile should be missing", failures)

    strings = {
        "string-0064fda4.tsv": "%w",
        "string-0066f580.tsv": "",
    }
    for relative, expected in strings.items():
        rows = read_tsv(BASE / relative)
        require(rows and rows[0].get("cstring") == expected, f"{relative} string mismatch", failures)

    context = {norm(row["address"]): row for row in read_tsv(BASE / "context-metadata.tsv")}
    for address, name in {
        "0x0052ff30": "ScriptCommandRegistry__InitBuiltins",
        "0x005362a0": "IScript__GetTextWidth",
        "0x00537410": "IScript__PlaySound",
        "0x004f2580": "CText__GetStringById",
        "0x00441740": "CConsole__Printf",
    }.items():
        row = context.get(address)
        require(row is not None, f"missing context metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"context name mismatch for {address}", failures)
            require(row.get("status") == "OK", f"context status mismatch for {address}", failures)

    registry_decompile = read_text(BASE / "context-decompile" / "0052ff30_ScriptCommandRegistry__InitBuiltins.c")
    for token in ("_DAT_0064d250 = &LAB_00537c40", "_DAT_0064d220 = s_PrintText_0064f984"):
        require(token in registry_decompile, f"missing registry decompile token: {token}", failures)

    metadata = read_tsv(BASE / "post-metadata.tsv")[0]
    require(norm(metadata.get("address", "")) == TARGET, "post metadata address mismatch", failures)
    require(metadata.get("name") == TARGET_NAME, "post metadata name mismatch", failures)
    require(metadata.get("signature") == TARGET_SIGNATURE, "post metadata signature mismatch", failures)
    require(metadata.get("status") == "OK", "post metadata status mismatch", failures)
    comment = metadata.get("comment", "")
    for token in ("Wave1074 boundary recovery", "s_PrintText_0064f984", "0x0064d250", "CText__GetStringById", "CConsole__Printf", "separate proof"):
        require(token in comment, f"missing post comment token: {token}", failures)

    tags = set(read_tsv(BASE / "post-tags.tsv")[0].get("tags", "").split(";"))
    require(COMMON_TAGS.issubset(tags), f"post tags missing: {COMMON_TAGS - tags}", failures)

    xref = read_tsv(BASE / "post-xrefs.tsv")[0]
    require(norm(xref.get("target_addr", "")) == TARGET, "post xref target mismatch", failures)
    require(norm(xref.get("from_addr", "")) == "0x00530483", "post xref from mismatch", failures)
    require(xref.get("from_function") == "ScriptCommandRegistry__InitBuiltins", "post xref function mismatch", failures)
    require(xref.get("ref_type") == "DATA", "post xref type mismatch", failures)

    body = read_tsv(BASE / "post-body-instructions.tsv")
    require(body[0].get("instruction_addr") == "0x00537c40", "post body start mismatch", failures)
    require(body[-1].get("instruction_addr") == "0x00537c69", "post body end mismatch", failures)
    require(all(row.get("function_name") == TARGET_NAME for row in body), "post body function name mismatch", failures)
    require(not any(row.get("instruction_addr") == "0x00537c70" for row in body), "post body absorbed next raw command", failures)

    decompile = read_tsv(BASE / "post-decompile" / "index.tsv")[0]
    require(decompile.get("name") == TARGET_NAME, "post decompile name mismatch", failures)
    require(decompile.get("signature") == TARGET_SIGNATURE, "post decompile signature mismatch", failures)
    require(decompile.get("status") == "OK", "post decompile status mismatch", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "pre-diagnose.log": "DiagnoseAddressListingState complete: rows=1",
        "pre-metadata.log": "targets=1 found=0 missing=1",
        "pre-xrefs.log": "Wrote 1 rows",
        "pre-instructions.log": "Wrote 228 instruction rows",
        "pre-decompile.log": "targets=1 dumped=0 missing=1 failed=0",
        "context-metadata.log": "targets=5 found=5 missing=0",
        "context-xrefs.log": "Wrote 704 rows",
        "context-instructions.log": "Wrote 185 instruction rows",
        "context-decompile.log": "targets=5 dumped=5 missing=0 failed=0",
        "apply-dry.log": "SUMMARY: updated=1 skipped=0 created=0 would_create=1 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=1 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=1 skipped=0 created=1 would_create=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=1 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-diagnose.log": "DiagnoseAddressListingState complete: rows=1",
        "post-metadata.log": "targets=1 found=1 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=1 missing=0",
        "post-xrefs.log": "Wrote 1 rows",
        "post-body-instructions.log": "Wrote 13 function-body instruction rows",
        "post-decompile.log": "targets=1 dumped=1 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR", "BADNAME", "FAIL:", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6247, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented = sum(1 for row in rows if row.get("comment", "").strip())
    by_address = {norm(row["address"]): row for row in rows}
    require(len(rows) == 6247, "quality TSV row count mismatch", failures)
    require(commented == 6247, "quality TSV commented count mismatch", failures)
    require(strict_clean_count(rows) == 6247, "quality TSV strict clean count mismatch", failures)
    require(by_address.get(TARGET, {}).get("name") == TARGET_NAME, "quality TSV target name mismatch", failures)
    require(by_address.get(TARGET, {}).get("signature") == TARGET_SIGNATURE, "quality TSV target signature mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 174721927 or backup.get("totalBytes") == 174721927.0, "backup bytes mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    for path in CORE_DOCS:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    for path in OWNER_DOCS:
        text = read_text(path)
        for token in OWNER_DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(scripts.get("test:ghidra-script-text-console-boundary-wave1074") == r"py -3 tools\ghidra_script_text_console_boundary_wave1074_probe.py --check", "missing focused package script", failures)
    require(scripts.get("test:ghidra-wave900-plus-through-wave1074-recheck") == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1074 --check", "missing aggregate package script", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1074 script text console boundary" for row in ledger_rows), "missing Wave1074 ledger row", failures)
    require(any(row.get("task") == "Wave1074 script text console boundary" and row.get("attempt_id") == 20656 for row in attempts), "missing Wave1074 attempt row", failures)


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
        print("Wave1074 script text console boundary probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1074 script text console boundary probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
