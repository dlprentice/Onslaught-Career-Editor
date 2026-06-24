#!/usr/bin/env python3
"""Validate Wave859 FEPScreenPos core read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave859-fepscreenpos-core"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_fepscreenpos_core_wave859_2026-05-25.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FEPSCREENPOS_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FEPScreenPos.cpp" / "_index.md"
FEPOPTIONS_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FEPOptions.cpp" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

TASK = "Wave859 CFEPScreenPos core"
BACKUP_PATH = r"G:\GhidraBackups\BEA_20260525-131538_post_wave859_fepscreenpos_core_verified"
NEXT_HEAD = "0x0051ff90 CFEPVirtualKeyboard__Init"
STRICT_PROXY = "5784/6105 = 94.74%"

TARGET_SIGNATURES = {
    "0x0051f9f0": ("CFEPScreenPos__Init", "int __fastcall CFEPScreenPos__Init(void * this)"),
    "0x0051fa00": ("CFEPScreenPos__ButtonPressed", "void __thiscall CFEPScreenPos__ButtonPressed(void * this, int button, float val)"),
    "0x0051fb60": ("CFEPScreenPos__RenderPreCommon", "void __stdcall CFEPScreenPos__RenderPreCommon(float transition, int dest)"),
    "0x0051fb90": ("CFEPScreenPos__Render", "void __stdcall CFEPScreenPos__Render(float transition, int dest)"),
    "0x0051fd50": ("CFEPScreenPos__TransitionNotification", "void __fastcall CFEPScreenPos__TransitionNotification(void * this, int from_page)"),
}

COMMENT_TOKENS = {
    "0x0051f9f0": ("Wave859 static read-back", "vtable 0x005db858 slot 0", "this+0x04", "this+0x08"),
    "0x0051fa00": ("Wave859 static read-back", "0x2a/0x2b", "CCareer__SetKillCounterTopByte_23F8", "0x36/0x37", "CFEPOptions__SetKillCounterTopBytes_23F4_23F8"),
    "0x0051fb60": ("Wave859 static read-back/signature correction", "RET 0x8", "CFrontEnd__RenderPreCommonFade", "stale extra first parameter"),
    "0x0051fb90": ("Wave859 static read-back/signature correction", "0x0063fcf0", "0x0063fcc8", "0x0063fcb0", "stale extra first parameter"),
    "0x0051fd50": ("Wave859 static read-back", "PLATFORM__GetSysTimeFloat", "CFEPOptions__GetKillCounterTopBytes_23F4_23F8", "this+0x10/0x14"),
}

COMMON_TAGS = {
    "static-reaudit",
    "fepscreenpos-core-wave859",
    "wave859-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "frontend",
    "fepscreenpos",
    "screen-position",
}

EXPECTED_XREFS = {
    ("0x0051f9f0", "0x005db858", "DATA"),
    ("0x0051fa00", "0x005db864", "DATA"),
    ("0x0051fb60", "0x005db868", "DATA"),
    ("0x0051fb90", "0x005db86c", "DATA"),
    ("0x0051fd50", "0x005db870", "DATA"),
}

STRING_EXPECTATIONS = {
    "post-string-00629db8.tsv": ".?AVCFEPScreenPos@@",
    "post-string-0063fcb0.tsv": "Adjust Screen Position",
    "post-string-0063fcc8.tsv": "correctly centered on your television.",
    "post-string-0063fcf0.tsv": "Adjust Screen Position until display is",
}

CORE_ANCHORS = (
    TASK,
    "fepscreenpos-core-wave859",
    "0x0051f9f0 CFEPScreenPos__Init",
    "0x0051fa00 CFEPScreenPos__ButtonPressed",
    "0x0051fb60 CFEPScreenPos__RenderPreCommon",
    "0x0051fb90 CFEPScreenPos__Render",
    "0x0051fd50 CFEPScreenPos__TransitionNotification",
    "Adjust Screen Position",
    "important frontend/screen-position connective",
    NEXT_HEAD,
    STRICT_PROXY,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime screen-position calibration behavior proven",
    "runtime frontend/render/input behavior proven",
    "exact cfepscreenpos layout proven",
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
        "pre-metadata.tsv": 5,
        "pre-tags.tsv": 5,
        "pre-xrefs.tsv": 5,
        "pre-instructions.tsv": 225,
        "pre-decompile/index.tsv": 5,
        "pre-context-metadata.tsv": 13,
        "pre-context-decompile/index.tsv": 13,
        "pre-vtable.tsv": 18,
        "post-metadata.tsv": 5,
        "post-tags.tsv": 5,
        "post-xrefs.tsv": 5,
        "post-instructions.tsv": 225,
        "post-decompile/index.tsv": 5,
        "post-context-metadata.tsv": 13,
        "post-context-decompile/index.tsv": 13,
        "post-vtable.tsv": 18,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs = {(normalize_address(row["target_addr"]), normalize_address(row["from_addr"]), row["ref_type"]) for row in read_tsv(BASE / "post-xrefs.tsv")}

    for address, (name, signature) in TARGET_SIGNATURES.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in COMMENT_TOKENS[address]:
                require(token in row.get("comment", ""), f"missing comment token at {address}: {token}", failures)

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

    for expected in EXPECTED_XREFS:
        require(expected in xrefs, f"missing xref row: {expected}", failures)

    for relative, expected in STRING_EXPECTATIONS.items():
        rows = read_tsv(BASE / relative)
        require(rows and rows[0].get("cstring") == expected, f"{relative} string mismatch", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=5 skipped=0 renamed=0 would_rename=0 signature_updated=2 comment_only_updated=3 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=5 skipped=0 renamed=0 would_rename=0 signature_updated=2 comment_only_updated=3 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=5 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=5 found=5 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=5 missing=0",
        "post-xrefs.log": "Wrote 5 rows",
        "post-instructions.log": "Wrote 225 instruction rows",
        "post-decompile.log": "targets=5 dumped=5 missing=0 failed=0",
        "post-context-metadata.log": "targets=13 found=13 missing=0",
        "post-context-decompile.log": "targets=13 dumped=13 missing=0 failed=0",
        "post-vtable.log": "ExportVtableSlots complete: targets=2 rows=18",
        "quality-refresh.log": "total_functions=6105 commented_functions=5784",
        "queue-probe.log": "Commentless functions: 321",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave859.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave859_queue_probe.log",
    }
    for relative, token in expected.items():
        path = log_aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIG", "BADCOMMENT", "BADTAGS", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6105, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 321, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(len(queue["priorityQueues"]["commentlessHighSignal"]) == 0, "high-signal queue should be empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6105, "quality TSV row count mismatch", failures)
    require(commented == 5784, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5784, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x0051ff90", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CFEPVirtualKeyboard__Init", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 172198791 or backup.get("totalBytes") == 172198791.0, "backup byte count mismatch", failures)
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

    function_docs = {
        FEPSCREENPOS_DOC: CORE_ANCHORS,
        FEPOPTIONS_DOC: ("Wave859", "fepscreenpos-core-wave859", "CFEPOptions__GetKillCounterTopBytes_23F4_23F8", BACKUP_PATH),
    }
    for path, tokens in function_docs.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(scripts.get("test:ghidra-fepscreenpos-core-wave859") == r"py -3 tools\ghidra_fepscreenpos_core_wave859_probe.py --check", "missing package script", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == TASK for row in ledger_rows), "missing Wave859 ledger row", failures)
    require(any(row.get("task") == TASK and row.get("attempt_id") == 20514 for row in attempts), "missing Wave859 attempt row", failures)


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
        print("Wave859 FEPScreenPos core probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave859 FEPScreenPos core probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
