#!/usr/bin/env python3
"""Validate Wave860 CFEPVirtualKeyboard core read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave860-fepvirtualkeyboard-core"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_fepvirtualkeyboard_core_wave860_2026-05-25.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FEPVIRTUALKEYBOARD_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FEPVirtualKeyboard.cpp" / "_index.md"
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

TASK = "Wave860 CFEPVirtualKeyboard core"
BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260525-134150_post_wave860_fepvirtualkeyboard_core_verified"
NEXT_HEAD = "0x00523a70 CDXEngine__RenderMouseCursorSprite"
STRICT_PROXY = "5792/6105 = 94.87%"

TARGET_SIGNATURES = {
    "0x0051ff90": ("CFEPVirtualKeyboard__Init", "int __fastcall CFEPVirtualKeyboard__Init(void * this)"),
    "0x0051ffd0": ("CFEPVirtualKeyboard__Shutdown", "void __fastcall CFEPVirtualKeyboard__Shutdown(void * this)"),
    "0x0051fff0": (
        "CFEPVirtualKeyboard__SeedUniqueDefaultSaveName",
        "void __fastcall CFEPVirtualKeyboard__SeedUniqueDefaultSaveName(void * this)",
    ),
    "0x00520130": (
        "CFEPVirtualKeyboard__TransitionNotification",
        "void __thiscall CFEPVirtualKeyboard__TransitionNotification(void * this, int from_page)",
    ),
    "0x005202d0": ("CFEPVirtualKeyboard__Process", "void __thiscall CFEPVirtualKeyboard__Process(void * this, int state)"),
    "0x00520370": (
        "CFEPVirtualKeyboard__ButtonPressed",
        "void __thiscall CFEPVirtualKeyboard__ButtonPressed(void * this, int button, float val)",
    ),
    "0x00521100": (
        "CFEPVirtualKeyboard__Render",
        "void __thiscall CFEPVirtualKeyboard__Render(void * this, float transition, int dest)",
    ),
    "0x005214d0": (
        "CFEPVirtualKeyboard__IsSpecialKeyBlocked",
        "int __thiscall CFEPVirtualKeyboard__IsSpecialKeyBlocked(void * this)",
    ),
}

COMMENT_TOKENS = {
    "0x0051ff90": ("Wave860 static read-back", "vtable 0x005db830 slot 0", "this+0x6f4", "CFEPVirtualKeyboard__InitKeyboardLayout"),
    "0x0051ffd0": ("Wave860 static read-back/signature correction", "PlatformInput__SetKeySinkCore", "DAT_0051feb0", "stale cdecl"),
    "0x0051fff0": ("Wave860 static read-back/name correction", "supersedes stale CFEPOptions__EnumerateSaveFiles", "0x0063fd34", "0x00629314", "0x1001"),
    "0x00520130": ("Wave860 static read-back", "from_page 0, 9, or 0xe", "BEA plus numeric suffix", "this+0x6e4..0x6ec"),
    "0x005202d0": ("Wave860 static read-back", "CFEPDirectory__RefreshSaveFileList", "PlatformInput__SetKeySinkCore", "PCPlatform__GetStorageDeviceInfo"),
    "0x00520370": ("Wave860 static read-back", "0x2a/0x2b", "CFEPVirtualKeyboard__HandleKeyToken", "CFEPVirtualKeyboard__IsSpecialKeyBlocked"),
    "0x00521100": ("Wave860 static read-back", "CFEPDirectory__RenderSaveFileList", "CRT__WcsNcpyZeroPad", "CFEPVirtualKeyboard__DrawPanel"),
    "0x005214d0": ("Wave860 static read-back", "tokens 4 and 5", "token 9", "only spaces"),
}

COMMON_TAGS = {
    "static-reaudit",
    "fepvirtualkeyboard-core-wave860",
    "wave860-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "frontend",
    "fepvirtualkeyboard",
    "virtual-keyboard",
    "save-name",
}

EXPECTED_XREFS = {
    ("0x0051ff90", "0x005db830", "DATA"),
    ("0x0051ffd0", "0x005db834", "DATA"),
    ("0x0051fff0", "0x0046241c", "UNCONDITIONAL_CALL"),
    ("0x0051fff0", "0x00462a28", "UNCONDITIONAL_CALL"),
    ("0x00520130", "0x005db848", "DATA"),
    ("0x005202d0", "0x005db838", "DATA"),
    ("0x00520370", "0x005db83c", "DATA"),
    ("0x00521100", "0x005db844", "DATA"),
    ("0x005214d0", "0x00521089", "UNCONDITIONAL_CALL"),
    ("0x005214d0", "0x00520494", "UNCONDITIONAL_CALL"),
    ("0x005214d0", "0x005204eb", "UNCONDITIONAL_CALL"),
}

STRING_EXPECTATIONS = {
    "post-string-00629d18.tsv": ".?AVCFEPVirtualKeyboard@@",
    "post-string-0063fd34.tsv": "BEA",
    "post-string-00629314.tsv": " %d",
}

CORE_ANCHORS = (
    TASK,
    "fepvirtualkeyboard-core-wave860",
    "0x0051ff90 CFEPVirtualKeyboard__Init",
    "0x0051ffd0 CFEPVirtualKeyboard__Shutdown",
    "0x0051fff0 CFEPVirtualKeyboard__SeedUniqueDefaultSaveName",
    "0x00520130 CFEPVirtualKeyboard__TransitionNotification",
    "0x005202d0 CFEPVirtualKeyboard__Process",
    "0x00520370 CFEPVirtualKeyboard__ButtonPressed",
    "0x00521100 CFEPVirtualKeyboard__Render",
    "0x005214d0 CFEPVirtualKeyboard__IsSpecialKeyBlocked",
    "important frontend/virtual-keyboard connective infrastructure",
    NEXT_HEAD,
    STRICT_PROXY,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime virtual-keyboard behavior proven",
    "runtime save-name behavior proven",
    "runtime filesystem behavior proven",
    "exact cfepscreenpos layout proven",
    "exact cfepvirtualkeyboard layout proven",
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
        "pre-metadata.tsv": 8,
        "pre-tags.tsv": 8,
        "pre-xrefs.tsv": 11,
        "pre-instructions.tsv": 392,
        "pre-decompile/index.tsv": 8,
        "pre-context-metadata.tsv": 13,
        "pre-context-decompile/index.tsv": 13,
        "pre-vtable.tsv": 18,
        "pre-callsite-instructions.tsv": 66,
        "post-metadata.tsv": 8,
        "post-tags.tsv": 8,
        "post-xrefs.tsv": 11,
        "post-instructions.tsv": 648,
        "post-decompile/index.tsv": 8,
        "post-context-metadata.tsv": 13,
        "post-context-decompile/index.tsv": 13,
        "post-vtable.tsv": 18,
        "post-callsite-instructions.tsv": 74,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs = {
        (normalize_address(row["target_addr"]), normalize_address(row["from_addr"]), row["ref_type"])
        for row in read_tsv(BASE / "post-xrefs.tsv")
    }

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

    vtable_text = read_text(BASE / "post-vtable.tsv")
    for token in (
        "005db830\t0\t005db830\t0x0051ff90",
        "005db830\t5\t005db844\t0x00521100",
        "005db830\t6\t005db848\t0x00520130",
        "005db8a8\t0\t005db8a8\t0x0051f4b0",
    ):
        require(token in vtable_text, f"missing vtable token: {token}", failures)

    for relative, expected in STRING_EXPECTATIONS.items():
        rows = read_tsv(BASE / relative)
        require(rows and rows[0].get("cstring") == expected, f"{relative} string mismatch", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=8 skipped=0 renamed=0 would_rename=1 signature_updated=2 comment_only_updated=6 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=8 skipped=0 renamed=1 would_rename=1 signature_updated=2 comment_only_updated=6 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=8 found=8 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=8 missing=0",
        "post-xrefs.log": "Wrote 11 rows",
        "post-instructions.log": "Wrote 648 instruction rows",
        "post-decompile.log": "targets=8 dumped=8 missing=0 failed=0",
        "post-context-metadata.log": "targets=13 found=13 missing=0",
        "post-context-decompile.log": "targets=13 dumped=13 missing=0 failed=0",
        "post-vtable.log": "ExportVtableSlots complete: targets=2 rows=18",
        "post-callsite-instructions.log": "Wrote 74 instruction rows",
        "quality-refresh.log": "total_functions=6105 commented_functions=5792",
        "queue-probe.log": "Commentless functions: 313",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave860.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave860_queue_probe.log",
    }
    for relative, token in expected.items():
        path = log_aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR:", "BADSIG:", "BADCOMMENT:", "BADTAGS:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6105, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 313, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(queue["priorityQueues"]["commentlessHighSignal"] == [], "high-signal queue should be empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6105, "quality TSV row count mismatch", failures)
    require(commented == 5792, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5792, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x00523a70", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CDXEngine__RenderMouseCursorSprite", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 172231559 or backup.get("totalBytes") == 172231559.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = [
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        FEPVIRTUALKEYBOARD_DOC,
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

    fepoptions_text = read_text(FEPOPTIONS_DOC)
    for token in (
        "Wave860",
        "supersedes stale `CFEPOptions__EnumerateSaveFiles`",
        "0x0051fff0 CFEPVirtualKeyboard__SeedUniqueDefaultSaveName",
        BACKUP_PATH,
    ):
        require(contains_token(fepoptions_text, token), f"missing token in {FEPOPTIONS_DOC.relative_to(ROOT)}: {token}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-fepvirtualkeyboard-core-wave860")
        == r"py -3 tools\ghidra_fepvirtualkeyboard_core_wave860_probe.py --check",
        "missing package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == TASK for row in ledger_rows), "missing Wave860 ledger row", failures)
    require(any(row.get("task") == TASK and row.get("attempt_id") == 20515 for row in attempts), "missing Wave860 attempt row", failures)


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
        print("Wave860 CFEPVirtualKeyboard core probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave860 CFEPVirtualKeyboard core probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
