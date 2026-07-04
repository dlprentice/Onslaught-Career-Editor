#!/usr/bin/env python3
"""Validate Wave854 CFastVB render-immediate read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave854-cfastvb-render-immediate"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cfastvb_render_immediate_wave854_2026-05-25.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FASTVB_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FastVB.cpp" / "_index.md"
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

TASK = "Wave854 CFastVB render immediate"
BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260525-104123_post_wave854_cfastvb_render_immediate_verified"
TARGET = "0x0051a6a0"
TARGET_NAME = "CFastVB__RenderTriangleStripImmediate"
TARGET_SIGNATURE = "void __thiscall CFastVB__RenderTriangleStripImmediate(void * this)"
NEXT_HEAD = "0x0051a970 CFEPCredits__TransitionNotification"

COMMON_TAGS = {
    "static-reaudit",
    "cfastvb-render-immediate-wave854",
    "wave854-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "rename-corrected",
    "renderer",
    "cfastvb",
    "d3d-device",
    "non-indexed-triangle-strip",
    "fastvb-cpp-debug-string",
}

COMMENT_TOKENS = (
    "Wave854 static read-back",
    "non-indexed triangle-strip",
    "vtable +0x190",
    "stride 0x1c",
    "primitive type 5",
    "this+0x08-2",
    "CConsole__RenderLoadingScreen",
    "CRenderQueue__RenderAll",
    "CVBufTexture__DrawSpriteEx",
    "DAT_00897a90",
)

XREFS = {
    "0x0042cce6": "CConsole__RenderLoadingScreen",
    "0x00553250": "CRenderQueue__RenderAll",
    "0x005537d5": "CRenderQueue__RenderAll",
    "0x0055633a": "CVBufTexture__DrawSpriteEx",
}

CORE_ANCHORS = (
    TASK,
    "cfastvb-render-immediate-wave854",
    f"{TARGET} {TARGET_NAME}",
    "CFastVB__RenderIndexedImmediate",
    "CFastVB__RenderTriangleStripImmediate",
    NEXT_HEAD,
    "5755/6098 = 94.38%",
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime render output proven",
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
        "pre-xrefs.tsv": 4,
        "pre-instructions.tsv": 221,
        "pre-decompile/index.tsv": 1,
        "pre-context-metadata.tsv": 7,
        "pre-context-decompile/index.tsv": 7,
        "pre-caller-metadata.tsv": 3,
        "pre-caller-decompile/index.tsv": 3,
        "post-metadata.tsv": 1,
        "post-tags.tsv": 1,
        "post-xrefs.tsv": 4,
        "post-instructions.tsv": 221,
        "post-decompile/index.tsv": 1,
        "post-context-metadata.tsv": 7,
        "post-context-decompile/index.tsv": 7,
        "post-caller-metadata.tsv": 3,
        "post-caller-decompile/index.tsv": 3,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    string_rows = read_tsv(BASE / "string-0063fb24.tsv")
    require(string_rows and string_rows[0].get("cstring") == r"[maintainer-local-source-export-root]\FastVB.cpp", "FastVB.cpp string mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    row = metadata.get(TARGET)
    require(row is not None, "missing target metadata", failures)
    if row is not None:
        require(row.get("name") == TARGET_NAME, "target name mismatch", failures)
        require(row.get("signature") == TARGET_SIGNATURE, f"target signature mismatch: {row.get('signature')}", failures)
        require(row.get("status") == "OK", "target metadata status mismatch", failures)
        for token in COMMENT_TOKENS:
            require(token in row.get("comment", ""), f"missing comment token: {token}", failures)

    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    tag_row = tags.get(TARGET)
    require(tag_row is not None, "missing target tags", failures)
    if tag_row is not None:
        actual_tags = set(tag_row.get("tags", "").split(";"))
        require(COMMON_TAGS.issubset(actual_tags), f"tags missing: {COMMON_TAGS - actual_tags}", failures)

    xrefs = read_tsv(BASE / "post-xrefs.tsv")
    xref_pairs = {(normalize_address(row.get("from_addr", "")), row.get("from_function", "")) for row in xrefs}
    for from_addr, function_name in XREFS.items():
        require((from_addr, function_name) in xref_pairs, f"missing xref {from_addr} {function_name}", failures)

    decompile = read_text(BASE / "post-decompile" / "0051a6a0_CFastVB__RenderTriangleStripImmediate.c")
    for token in ("+0x144 with primitive type 5", "DAT_00897a90", "this+0x08-2"):
        require(token in decompile, f"missing decompile/comment token: {token}", failures)

    caller_text = "\n".join(path.read_text(encoding="utf-8-sig") for path in (BASE / "post-caller-decompile").glob("*.c"))
    for token in ("CFastVB__LockAligned", "CFastVB__Lock", TARGET_NAME):
        require(token in caller_text, f"missing caller token: {token}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=1 signature_updated=1 comment_only_updated=1 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=1 skipped=0 renamed=1 would_rename=1 signature_updated=1 comment_only_updated=1 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=1 found=1 missing=0",
        "post-tags.log": "rows=1 missing=0",
        "post-xrefs.log": "Wrote 4 rows",
        "post-instructions.log": "Wrote 221 instruction rows",
        "post-decompile.log": "targets=1 dumped=1 missing=0 failed=0",
        "post-context-metadata.log": "targets=7 found=7 missing=0",
        "post-context-decompile.log": "targets=7 dumped=7 missing=0 failed=0",
        "post-caller-metadata.log": "targets=3 found=3 missing=0",
        "post-caller-decompile.log": "targets=3 dumped=3 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6098 commented_functions=5755",
        "queue-probe.log": "Commentless functions: 343",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave854.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave854_queue_probe.log",
    }
    for relative, token in expected.items():
        text = read_text(log_aliases.get(relative, BASE / relative))
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 343, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5755, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5755, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x0051a970", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CFEPCredits__TransitionNotification", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 172166023, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = [
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        FASTVB_DOC,
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

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(scripts.get("test:ghidra-cfastvb-render-immediate-wave854") == r"py -3 tools\ghidra_cfastvb_render_immediate_wave854_probe.py --check", "missing package script", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == TASK for row in ledger_rows), "missing Wave854 ledger row", failures)
    require(any(row.get("task") == TASK and row.get("attempt_id") == 20509 for row in attempts), "missing Wave854 attempt row", failures)


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
        print("Wave854 CFastVB render-immediate probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave854 CFastVB render-immediate probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
