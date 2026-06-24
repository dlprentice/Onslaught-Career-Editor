#!/usr/bin/env python3
"""Validate Wave880 CRT runtime-tail read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave880-crt-runtime-tail"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_crt_runtime_tail_wave880_2026-05-25.md"
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

TASK = "Wave880 CRT runtime tail"
BACKUP_PATH = r"G:\GhidraBackups\BEA_20260525-233022_post_wave880_crt_runtime_tail_verified"
NEXT_HEAD = "0x005602d2 CRT__SehDispatchWithScopeTable"
STRICT_PROXY = "5924/6113 = 96.91%"

TARGETS = {
    "0x0055ecb1": ("CRT__UnlockHeapLock9_0055ecb1", "void CRT__UnlockHeapLock9_0055ecb1(void)", ("CRT__UnlockByIndex", "CRT__HeapAllocBase")),
    "0x0055ed10": ("CRT__UnlockHeapLock9_0055ed10", "void CRT__UnlockHeapLock9_0055ed10(void)", ("CRT__UnlockByIndex", "CRT__HeapAllocBase")),
    "0x0055f0ef": ("CRT__UnlockHeapLock", "void CRT__UnlockHeapLock(void)", ("CRT__UnlockByIndex", "CRT__FreeBase")),
    "0x0055f147": ("CRT__UnlockHeapLock_Alt", "void CRT__UnlockHeapLock_Alt(void)", ("CRT__UnlockByIndex", "CRT__FreeBase")),
    "0x0055f16e": ("fwrite", "int __cdecl fwrite(void * ptr, int size, int count, void * file)", ("CRT__FWriteCore", "PCPlatform__WriteSaveFile")),
    "0x0055f2a7": ("CRT__WcsStr", "short * __cdecl CRT__WcsStr(short * haystack, short * needle)", ("owner-corrected", "CDropship__FindSubstringW", "CMessageBox__SelectPortraitIndex")),
    "0x0055f380": ("CRT__AcosClassifyAndDispatch", "void CRT__AcosClassifyAndDispatch(void)", ("CRT__AcosCoreWithFpuGuards", "CStaticShadows__RayTriangleIntersect")),
    "0x0055f4d7": ("fread", "int __cdecl fread(void * ptr, int size, int count, void * file)", ("CRT__FReadCore", "PCPlatform__ReadSaveFile")),
    "0x0055fa40": ("CRT__PowDispatch_ST0_ST1", "void CRT__PowDispatch_ST0_ST1(void)", ("CRT__PowCoreWithFpuGuards", "PCPlatform__UpdateAsyncMusicStreamVolume")),
    "0x0055fc35": ("CRT__IsFloat10Integral_0055fc35", "void CRT__IsFloat10Integral_0055fc35(void)", ("integral-test", "CRT__PowCoreWithFpuGuards")),
}

COMMON_TAGS = {
    "static-reaudit",
    "crt-runtime-tail-wave880",
    "wave880-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-verified",
    "important-crt-runtime-infrastructure",
    "high-importance-low-local-evidence-density",
    "compiler-runtime",
    "crt-stdio",
    "crt-math",
    "raw-commentless-head",
}

XREF_COUNTS = {
    "0x0055ecb1": 1,
    "0x0055ed10": 1,
    "0x0055f0ef": 1,
    "0x0055f147": 1,
    "0x0055f16e": 11,
    "0x0055f2a7": 1,
    "0x0055f380": 5,
    "0x0055f4d7": 7,
    "0x0055fa40": 5,
    "0x0055fc35": 2,
}

CORE_ANCHORS = (
    TASK,
    "crt-runtime-tail-wave880",
    "0x0055ecb1 CRT__UnlockHeapLock9_0055ecb1",
    "0x0055f16e fwrite",
    "0x0055f2a7 CRT__WcsStr",
    "CDropship__FindSubstringW",
    "0x0055f380 CRT__AcosClassifyAndDispatch",
    "0x0055f4d7 fread",
    "0x0055fa40 CRT__PowDispatch_ST0_ST1",
    "0x0055fc35 CRT__IsFloat10Integral_0055fc35",
    NEXT_HEAD,
    STRICT_PROXY,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime file i/o behavior proven",
    "runtime heap behavior proven",
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
        "pre-metadata.tsv": 10,
        "pre-tags.tsv": 10,
        "pre-xrefs.tsv": 35,
        "pre-instructions.tsv": 114,
        "pre-decompile/index.tsv": 10,
        "pre-context-metadata.tsv": 10,
        "pre-context-decompile/index.tsv": 10,
        "post-metadata.tsv": 10,
        "post-tags.tsv": 10,
        "post-xrefs.tsv": 35,
        "post-instructions.tsv": 114,
        "post-decompile/index.tsv": 10,
        "post-context-metadata.tsv": 10,
        "post-context-decompile/index.tsv": 10,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    xref_counts: dict[str, int] = {}
    for row in read_tsv(BASE / "post-xrefs.tsv"):
        address = normalize_address(row["target_addr"])
        xref_counts[address] = xref_counts.get(address, 0) + 1

    for address, (name, signature, comment_tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            comment = row.get("comment", "")
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            require("Wave880 static read-back" in comment, f"missing Wave880 comment at {address}", failures)
            for token in comment_tokens:
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"tags missing at {address}: {COMMON_TAGS - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        require(xref_counts.get(address) == XREF_COUNTS[address], f"xref count mismatch at {address}", failures)

    context = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-context-decompile" / "index.tsv")}
    require(context.get("0x0055fa62", {}).get("status") == "FAILED", "expected pow core context decompile failure missing", failures)
    require(context.get("0x0055f19d", {}).get("status") == "OK", "missing FWriteCore context decompile", failures)
    require(context.get("0x0055f506", {}).get("status") == "OK", "missing FReadCore context decompile", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=10 renamed=0 would_rename=1 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=10 skipped=0 renamed=1 would_rename=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=10 renamed=0 would_rename=0 missing=0 bad=0",
        "post-metadata.log": "targets=10 found=10 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=10 missing=0",
        "post-xrefs.log": "Wrote 35 rows",
        "post-instructions.log": "Wrote 114 function-body instruction rows",
        "post-decompile.log": "targets=10 dumped=10 missing=0 failed=0",
        "post-context-metadata.log": "targets=10 found=10 missing=0",
        "post-context-decompile.log": "targets=10 dumped=9 missing=0 failed=1",
        "quality-refresh.log": "total_functions=6113 commented_functions=5924",
        "queue-probe.log": "Commentless functions: 189",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave880.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave880_queue_probe.log",
    }
    for relative, token in expected.items():
        path = log_aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BAD:", "missing=1", "bad=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6113, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 189, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6113, "quality TSV row count mismatch", failures)
    require(commented == 5924, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5924, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x005602d2", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CRT__SehDispatchWithScopeTable", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 172755847 or backup.get("totalBytes") == 172755847.0, "backup byte count mismatch", failures)
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
    require(scripts.get("test:ghidra-crt-runtime-tail-wave880") == r"py -3 tools\ghidra_crt_runtime_tail_wave880_probe.py --check", "missing package script", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == TASK for row in ledger_rows), "missing Wave880 ledger row", failures)
    require(any(row.get("task") == TASK and row.get("attempt_id") == 20535 for row in attempts), "missing Wave880 attempt row", failures)


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
        print("Wave880 CRT runtime-tail probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave880 CRT runtime-tail probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
