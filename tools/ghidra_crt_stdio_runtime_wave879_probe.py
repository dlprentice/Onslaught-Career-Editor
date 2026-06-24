#!/usr/bin/env python3
"""Validate Wave879 CRT/stdio runtime read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave879-crt-stdio-runtime"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_crt_stdio_runtime_wave879_2026-05-25.md"
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

TASK = "Wave879 CRT/stdio runtime"
BACKUP_PATH = r"G:\GhidraBackups\BEA_20260525-225409_post_wave879_crt_stdio_runtime_verified"
NEXT_HEAD = "0x0055ecb1 CRT__UnlockHeapLock9_0055ecb1"
STRICT_PROXY = "5914/6113 = 96.74%"

TARGETS = {
    "0x0055dcb0": (
        "CRT__AcosDispatch_ST0",
        "void CRT__AcosDispatch_ST0(void)",
        ("owner-corrected", "OID__AcosWrapper", "CRT__Acos", "41 gameplay/world/math callsites"),
    ),
    "0x0055dd7b": (
        "CRT__RunStaticInitRangesWithOptionalCallback",
        "void CRT__RunStaticInitRangesWithOptionalCallback(void)",
        ("owner-corrected", "CFastVB__RunStaticInitRangesWithOptionalCallback", "CRT__InvokeFunctionPointerRange", "entry"),
    ),
    "0x0055de6f": (
        "CRT__Lock_0x0D",
        "void CRT__Lock_0x0D(void)",
        ("CRT__LockByIndex(0x0d)", "CRT__DoExit", "shutdown"),
    ),
    "0x0055de78": (
        "CRT__Unlock_0x0D",
        "void CRT__Unlock_0x0D(void)",
        ("CRT__UnlockByIndex(0x0d)", "CRT__DoExit", "shutdown"),
    ),
    "0x0055de9b": (
        "sprintf",
        "int __cdecl sprintf(char * dst, char * format)",
        ("CRT sprintf-family", "CRT__FormatOutputToStream", "304 callsites"),
    ),
    "0x0055def0": (
        "CRT__AllocaProbe",
        "void CRT__AllocaProbe(void)",
        ("stack-probe", "0x1000-byte pages", "40 compiler/runtime callers"),
    ),
    "0x0055e38c": (
        "vsprintf",
        "int __cdecl vsprintf(char * dst, char * format, void * args)",
        ("CRT vsprintf-family", "CRT__FormatOutputToStream", "Log__WriteFormatted"),
    ),
    "0x0055e3ea": (
        "CRT__FpuIntrinsicDispatch2Thunk",
        "void __cdecl CRT__FpuIntrinsicDispatch2Thunk(void)",
        ("owner-corrected", "CPDSimpleSprite__FpuDispatchStub", "__cintrindisp2", "44 broad math"),
    ),
    "0x0055e42a": (
        "Win32__CaptureSystemTimeAsFileTimeTicks",
        "void Win32__CaptureSystemTimeAsFileTimeTicks(void)",
        ("GetSystemTimeAsFileTime", "0x009d0900", "DATA xref 0x00622b18"),
    ),
    "0x0055e490": (
        "fopen",
        "void * __cdecl fopen(char * path, char * mode)",
        ("CRT fopen wrapper", "CRT__OpenFileByModeString_AutoUnlock", "29 file-opening callsites"),
    ),
    "0x0055e4a3": (
        "fclose",
        "int __cdecl fclose(void * file)",
        ("CRT fclose wrapper", "__fclose_lk", "29 matching close callsites"),
    ),
    "0x0055e520": (
        "fprintf",
        "int __cdecl fprintf(void * file, char * format)",
        ("CRT fprintf-family", "CRT__FormatOutputToStream", "Log__WriteFormatted"),
    ),
    "0x0055e607": (
        "WcsLen",
        "int __cdecl WcsLen(short * wstr)",
        ("16-bit wide-string length helper", "23 UI/text conversion callsites", "FromWCHAR"),
    ),
}

COMMON_TAGS = {
    "static-reaudit",
    "crt-stdio-runtime-wave879",
    "wave879-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-verified",
    "important-crt-runtime-infrastructure",
    "high-importance-low-local-evidence-density",
    "compiler-runtime",
    "crt-stdio",
    "raw-commentless-head",
}

XREF_COUNTS = {
    "0x0055dcb0": 41,
    "0x0055dd7b": 1,
    "0x0055de6f": 2,
    "0x0055de78": 2,
    "0x0055de9b": 304,
    "0x0055def0": 40,
    "0x0055e38c": 4,
    "0x0055e3ea": 44,
    "0x0055e42a": 1,
    "0x0055e490": 29,
    "0x0055e4a3": 29,
    "0x0055e520": 3,
    "0x0055e607": 23,
}

CONTEXT_EXPECTATIONS = {
    "0x0055dccd": ("CRT__Acos", "CRT__AcosDispatch_ST0"),
    "0x0055da76": ("CRT__InitRuntimeFromStoredFrameGlobals", "CRT__RunStaticInitRangesWithOptionalCallback"),
    "0x0055de81": ("CRT__InvokeFunctionPointerRange", "CRT__RunStaticInitRangesWithOptionalCallback"),
}

CORE_ANCHORS = (
    TASK,
    "crt-stdio-runtime-wave879",
    "0x0055dcb0 CRT__AcosDispatch_ST0",
    "0x0055dd7b CRT__RunStaticInitRangesWithOptionalCallback",
    "0x0055de9b sprintf",
    "0x0055def0 CRT__AllocaProbe",
    "0x0055e3ea CRT__FpuIntrinsicDispatch2Thunk",
    "0x0055e490 fopen",
    "0x0055e4a3 fclose",
    "0x0055e520 fprintf",
    "0x0055e607 WcsLen",
    "high-importance CRT/stdio/runtime connector rows with low local evidence density, not low-importance filler",
    NEXT_HEAD,
    STRICT_PROXY,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime file i/o behavior proven",
    "runtime formatting behavior proven",
    "runtime fpu behavior proven",
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
        "pre-metadata.tsv": 13,
        "pre-tags.tsv": 13,
        "pre-xrefs.tsv": 523,
        "pre-instructions.tsv": 195,
        "pre-decompile/index.tsv": 13,
        "pre-context-metadata.tsv": 12,
        "pre-context-decompile/index.tsv": 12,
        "post-metadata.tsv": 13,
        "post-tags.tsv": 13,
        "post-xrefs.tsv": 523,
        "post-instructions.tsv": 195,
        "post-decompile/index.tsv": 13,
        "post-context-metadata.tsv": 12,
        "post-context-decompile/index.tsv": 12,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    for address, (name, signature, tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing post metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            require("Wave879 static read-back" in row.get("comment", ""), f"missing Wave879 comment at {address}", failures)
            for token in tokens:
                require(contains_token(row.get("comment", ""), token), f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing post tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"tags missing at {address}: {COMMON_TAGS - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing post decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    context = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-context-metadata.tsv")}
    for address, (name, token) in CONTEXT_EXPECTATIONS.items():
        row = context.get(address)
        require(row is not None, f"missing context row for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"context name mismatch at {address}", failures)
            require("Wave879 context refresh" in row.get("comment", ""), f"missing context refresh at {address}", failures)
            require(token in row.get("comment", ""), f"missing context token at {address}: {token}", failures)

    xrefs = read_tsv(BASE / "post-xrefs.tsv")
    for address, expected_count in XREF_COUNTS.items():
        count = sum(1 for row in xrefs if normalize_address(row.get("target_addr", "")) == address)
        require(count == expected_count, f"xref count mismatch at {address}: {count} != {expected_count}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=16 renamed=0 would_rename=3 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=16 skipped=0 renamed=3 would_rename=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=16 renamed=0 would_rename=0 missing=0 bad=0",
        "post-metadata.log": "targets=13 found=13 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=13 missing=0",
        "post-xrefs.log": "Wrote 523 rows",
        "post-instructions.log": "Wrote 195 function-body instruction rows",
        "post-decompile.log": "targets=13 dumped=13 missing=0 failed=0",
        "post-context-metadata.log": "targets=12 found=12 missing=0",
        "post-context-decompile.log": "targets=12 dumped=12 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6113 commented_functions=5914",
        "queue-probe.log": "Commentless functions: 199",
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave879.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave879_queue_probe.log",
    }
    for relative, token in expected.items():
        path = aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6113, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 199, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x0055ecb1", "raw head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CRT__UnlockHeapLock9_0055ecb1", "raw head name mismatch", failures)

    commented, strict_clean = signature_counts(rows)
    require(len(rows) == 6113, "quality TSV row count mismatch", failures)
    require(commented == 5914, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5914, "strict clean count mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 172723079 or backup.get("totalBytes") == 172723079.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
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
    for path in docs:
        text = read_text(path)
        for token in CORE_ANCHORS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-crt-stdio-runtime-wave879")
        == r"py -3 tools\ghidra_crt_stdio_runtime_wave879_probe.py --check",
        "missing package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == TASK for row in ledger_rows), "missing Wave879 ledger row", failures)
    require(any(row.get("task") == TASK and row.get("attempt_id") == 20534 for row in attempts), "missing Wave879 attempt row", failures)


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
        print("Wave879 CRT/stdio runtime probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave879 CRT/stdio runtime probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
