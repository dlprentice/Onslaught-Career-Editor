#!/usr/bin/env python3
"""Validate Wave856 FEPDirectory page read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave856-fepdirectory-page"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_fepdirectory_page_wave856_2026-05-25.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FEPDIRECTORY_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FEPDirectory.cpp" / "_index.md"
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

TASK = "Wave856 FEPDirectory page"
BACKUP_PATH = r"G:\GhidraBackups\BEA_20260525-114000_post_wave856_fepdirectory_page_verified"
NEXT_HEAD = "0x0051b600 CFEPMultiplayerStart__SubObj4034__ctor"

TARGET_SIGNATURES = {
    "0x0051aa90": ("CFEPDirectory__Init", "int __fastcall CFEPDirectory__Init(void * this)"),
    "0x0051aac0": ("CFEPDirectory__Shutdown", "void __fastcall CFEPDirectory__Shutdown(void * this)"),
    "0x0051aaf0": ("CFEPDirectory__ButtonPressed", "void __thiscall CFEPDirectory__ButtonPressed(void * this, int button, float val)"),
    "0x0051ac40": ("CFEPDirectory__Process", "void __thiscall CFEPDirectory__Process(void * this, int state)"),
    "0x0051ad30": ("CFEPDirectory__RefreshSaveFileList", "void __thiscall CFEPDirectory__RefreshSaveFileList(void * this, int force_refresh)"),
    "0x0051b460": ("CFEPDirectory__Render", "void __thiscall CFEPDirectory__Render(void * this, float transition, int dest)"),
}

COMMENT_TOKENS = {
    "0x0051aa90": ("Wave856 static read-back", "vtable slot 2", "0x005db808", "this+0x4004", "this+0x4008"),
    "0x0051aac0": ("Wave856 static read-back", "vtable slot 3", "0x005db80c", "CDXMemoryManager__Free"),
    "0x0051aaf0": ("Wave856 static read-back", "vtable slot 5", "0x005db814", "button 0x2c", "DAT_008a1168"),
    "0x0051ac40": ("Wave856 static read-back", "vtable slot 4", "0x005db810", "PCPlatform__DeleteSaveFile"),
    "0x0051ad30": ("Wave856 static read-back", "CFEPVirtualKeyboard__Process", "PCPlatform__GetStorageDeviceInfo", "EnumerateSaveFiles_1", "0x0063fb4c"),
    "0x0051b460": ("Wave856 static read-back", "vtable slot 7", "0x005db81c", "CFEPDirectory__RenderSaveFileList", "CFrontEnd__RenderOverlayEffects"),
}

COMMON_TAGS = {
    "static-reaudit",
    "fepdirectory-page-wave856",
    "wave856-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "frontend",
    "fepdirectory",
    "save-file-list",
    "directory-page",
}

EXPECTED_XREFS = {
    ("0x0051aa90", "0x005db808", "DATA"),
    ("0x0051aac0", "0x005db80c", "DATA"),
    ("0x0051ac40", "0x005db810", "DATA"),
    ("0x0051aaf0", "0x005db814", "DATA"),
    ("0x0051ad30", "0x0051ac51", "UNCONDITIONAL_CALL"),
    ("0x0051ad30", "0x005202e1", "UNCONDITIONAL_CALL"),
    ("0x0051b460", "0x005db81c", "DATA"),
}

CORE_ANCHORS = (
    TASK,
    "fepdirectory-page-wave856",
    "0x0051aa90 CFEPDirectory__Init",
    "0x0051aac0 CFEPDirectory__Shutdown",
    "0x0051aaf0 CFEPDirectory__ButtonPressed",
    "0x0051ac40 CFEPDirectory__Process",
    "0x0051ad30 CFEPDirectory__RefreshSaveFileList",
    "0x0051b460 CFEPDirectory__Render",
    "CFEPDirectory__RenderSaveFileList",
    "PCPlatform__DeleteSaveFile",
    NEXT_HEAD,
    "5762/6098 = 94.49%",
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime frontend save-directory behavior proven",
    "runtime filesystem/delete behavior proven",
    "exact cfepdirectory layout proven",
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
        "pre-metadata.tsv": 6,
        "pre-tags.tsv": 6,
        "pre-xrefs.tsv": 7,
        "pre-instructions.tsv": 222,
        "pre-decompile/index.tsv": 6,
        "pre-context-metadata.tsv": 16,
        "pre-context-decompile/index.tsv": 16,
        "pre-vtable.tsv": 12,
        "post-metadata.tsv": 6,
        "post-tags.tsv": 6,
        "post-xrefs.tsv": 7,
        "post-instructions.tsv": 222,
        "post-decompile/index.tsv": 6,
        "post-context-metadata.tsv": 16,
        "post-context-decompile/index.tsv": 16,
        "post-vtable.tsv": 12,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
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

    actual_xrefs = {
        (normalize_address(row.get("target_addr", "")), normalize_address(row.get("from_addr", "")), row.get("ref_type", ""))
        for row in read_tsv(BASE / "post-xrefs.tsv")
    }
    require(EXPECTED_XREFS.issubset(actual_xrefs), f"xrefs missing: {EXPECTED_XREFS - actual_xrefs}", failures)

    vtable = read_tsv(BASE / "post-vtable.tsv")
    slot_names = {int(row["slot_index"]): row["function_name"] for row in vtable if row.get("slot_index", "").isdigit()}
    for slot, name in {
        2: "CFEPDirectory__Init",
        3: "CFEPDirectory__Shutdown",
        4: "CFEPDirectory__Process",
        5: "CFEPDirectory__ButtonPressed",
        7: "CFEPDirectory__Render",
    }.items():
        require(slot_names.get(slot) == name, f"vtable slot {slot} mismatch", failures)

    string_rows = read_tsv(BASE / "post-string-0063fb4c.tsv")
    require(string_rows and string_rows[0].get("cstring") == r"C:\dev\ONSLAUGHT2\FEPDirectory.cpp", "FEPDirectory.cpp string mismatch", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=6 renamed=0 would_rename=0 signature_checked=6 comment_only_updated=6 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=6 skipped=0 renamed=0 would_rename=0 signature_checked=6 comment_only_updated=6 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=6 renamed=0 would_rename=0 signature_checked=6 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=6 found=6 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=6 missing=0",
        "post-xrefs.log": "Wrote 7 rows",
        "post-instructions.log": "Wrote 222 instruction rows",
        "post-decompile.log": "targets=6 dumped=6 missing=0 failed=0",
        "post-context-metadata.log": "targets=16 found=16 missing=0",
        "post-context-decompile.log": "targets=16 dumped=16 missing=0 failed=0",
        "post-vtable.log": "ExportVtableSlots complete: targets=1 rows=12",
        "post-string-0063fb4c.log": r"DumpCStringAtAddress complete: input=0063fb4c target=0063fb4c text=C:\dev\ONSLAUGHT2\FEPDirectory.cpp",
        "quality-refresh.log": "total_functions=6098 commented_functions=5762",
        "queue-probe.log": "Commentless functions: 336",
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave856.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave856_queue_probe.log",
    }
    for relative, token in expected.items():
        path = aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIG:", "BADCOMMENT:", "BADTAGS:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 336, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(queue["priorityQueues"]["commentlessHighSignal"] == [], "high-signal queue should be empty", failures)
    require(queue["priorityQueues"]["signature"] == [], "signature queue should be empty", failures)
    require(queue["priorityQueues"]["nameConfidence"] == [], "name-confidence queue should be empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5762, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5762, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x0051b600", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CFEPMultiplayerStart__SubObj4034__ctor", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 172166023, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [PUBLIC_NOTE, FUNCTION_INDEX, FEPDIRECTORY_DOC, GHIDRA_REFERENCE, CAMPAIGN, BACKLOG, DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE]
    for path in docs:
        text = read_text(path)
        for token in CORE_ANCHORS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:ghidra-fepdirectory-page-wave856")
        == r"py -3 tools\ghidra_fepdirectory_page_wave856_probe.py --check",
        "missing package script",
        failures,
    )

    ledger = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == TASK for row in ledger), "missing Wave856 ledger row", failures)
    require(any(row.get("task") == TASK and row.get("attempt_id") == 20511 for row in attempts), "missing Wave856 attempt row", failures)


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
        print("Wave856 FEPDirectory page probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave856 FEPDirectory page probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
