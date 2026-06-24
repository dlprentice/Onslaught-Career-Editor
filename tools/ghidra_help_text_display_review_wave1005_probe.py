#!/usr/bin/env python3
"""Validate Wave1005 HelpTextDisplay review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1005-help-text-display-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_help_text_display_review_wave1005_2026-05-31.md"
RECHECK_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1005_recheck_2026-05-31.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
HELP_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "HelpText.cpp" / "_index.md"
DXFONT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXFont.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260531-132023_post_wave1005_help_text_display_review_verified"

TARGETS = {
    "0x0047fab0": ("CHelpTextDisplay__ctor", "void * __thiscall CHelpTextDisplay__ctor(void * this)"),
    "0x0047fad0": ("CHelpTextDisplay__scalar_deleting_dtor", "void * __thiscall CHelpTextDisplay__scalar_deleting_dtor(void * this, byte flags)"),
    "0x0047fb00": ("CHelpTextDisplay__QueueMessageWithTimestamp", "void __thiscall CHelpTextDisplay__QueueMessageWithTimestamp(void * this, void * message)"),
    "0x0047fb50": ("CHelpTextDisplay__RenderQueuedMessages", "void __fastcall CHelpTextDisplay__RenderQueuedMessages(void * this)"),
    "0x004659a0": ("CDXFont__DrawTextScaledWithShadow", "int __thiscall CDXFont__DrawTextScaledWithShadow(void * this, float x, float y, uint packed_argb, short * text, uint flags, float depth_z, float x_scale, float y_scale)"),
}

CONTEXT_TARGETS = {
    "0x00465710": ("CDXFont__DrawTextDynamic", "void __stdcall CDXFont__DrawTextDynamic(void * this, float x, float y, float z, float scale_x, float scale_y, int color, short * text, float transition, int fade_out, int flags)"),
    "0x00465a20": ("TextLayout__WrapWideTextToFixedLines", "int __stdcall TextLayout__WrapWideTextToFixedLines(short * line_buffer, short * wide_text, float max_width)"),
    "0x0048f620": ("CLevelBriefingLog__Render", "void __thiscall CLevelBriefingLog__Render(void * this, void * viewport)"),
    "0x0053ecc0": ("CDXEngine__PostRender", "int __thiscall CDXEngine__PostRender(void * this, void * viewport)"),
}

DOC_TOKENS = (
    "Wave1005",
    "help-text-display-review-wave1005",
    "0x0047fab0 CHelpTextDisplay__ctor",
    "0x0047fad0 CHelpTextDisplay__scalar_deleting_dtor",
    "0x0047fb00 CHelpTextDisplay__QueueMessageWithTimestamp",
    "0x0047fb50 CHelpTextDisplay__RenderQueuedMessages",
    "0x004659a0 CDXFont__DrawTextScaledWithShadow",
    "0x00465710 CDXFont__DrawTextDynamic",
    "0x00465a20 TextLayout__WrapWideTextToFixedLines",
    "485/1408 = 34.45%",
    "659/1478 = 44.59%",
    "384/500 = 76.80%",
    "6223/6223 = 100.00%",
    BACKUP_PATH,
)

OVERCLAIMS = (
    "runtime help text behavior proven",
    "runtime text rendering proven",
    "runtime visual behavior proven",
    "exact source-body identity proven",
    "exact source-layout identity proven",
    "exact layout proven",
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


def row_by_address(rows: list[dict[str, str]], address: str, field: str = "address") -> dict[str, str] | None:
    target = normalize_address(address)
    for row in rows:
        if normalize_address(row.get(field, "")) == target:
            return row
    return None


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return (
        token in text
        or token.replace("\\", "\\\\") in text
        or token.replace("\\", "\\\\\\\\") in text
        or token.replace("\\\\", "\\") in text.replace("\\\\\\\\", "\\").replace("\\\\", "\\")
    )


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 5,
        "pre-tags.tsv": 5,
        "pre-xrefs.tsv": 47,
        "pre-instructions.tsv": 232,
        "pre-decompile/index.tsv": 5,
        "context-metadata.tsv": 4,
        "context-decompile/index.tsv": 4,
        "context-instructions.tsv": 1252,
    }
    for relative, expected in expected_counts.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == expected, f"{relative} row count {actual} != {expected}", failures)

    metadata = read_tsv(BASE / "pre-metadata.tsv")
    tags = read_tsv(BASE / "pre-tags.tsv")
    decompile_index = read_tsv(BASE / "pre-decompile" / "index.tsv")
    for address, (name, signature) in TARGETS.items():
        row = row_by_address(metadata, address)
        require(row is not None, f"metadata missing {address}", failures)
        if row:
            require(row.get("name") == name, f"metadata name mismatch {address}", failures)
            require(row.get("signature") == signature, f"metadata signature mismatch {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)

        dec = row_by_address(decompile_index, address)
        require(dec is not None, f"decompile missing {address}", failures)
        if dec:
            require(dec.get("name") == name, f"decompile name mismatch {address}", failures)
            require(dec.get("signature") == signature, f"decompile signature mismatch {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch {address}", failures)

        tag_row = row_by_address(tags, address)
        require(tag_row is not None, f"tags missing {address}", failures)
        if tag_row:
            actual_tags = set(filter(None, tag_row.get("tags", "").split(";")))
            for tag in ("static-reaudit", "retail-binary-evidence", "comment-hardened", "signature-corrected"):
                require(tag in actual_tags, f"missing tag {address}: {tag}", failures)

    context = read_tsv(BASE / "context-metadata.tsv")
    context_index = read_tsv(BASE / "context-decompile" / "index.tsv")
    for address, (name, signature) in CONTEXT_TARGETS.items():
        row = row_by_address(context, address)
        require(row is not None, f"context metadata missing {address}", failures)
        if row:
            require(row.get("name") == name, f"context name mismatch {address}", failures)
            require(row.get("signature") == signature, f"context signature mismatch {address}", failures)
            require(row.get("status") == "OK", f"context status mismatch {address}", failures)
        dec = row_by_address(context_index, address)
        require(dec is not None, f"context decompile missing {address}", failures)
        if dec:
            require(dec.get("name") == name, f"context decompile name mismatch {address}", failures)
            require(dec.get("signature") == signature, f"context decompile signature mismatch {address}", failures)
            require(dec.get("status") == "OK", f"context decompile status mismatch {address}", failures)

    xrefs = read_tsv(BASE / "pre-xrefs.tsv")
    expected_xrefs = (
        ("0x0047fab0", "0x0046c769", "UNCONDITIONAL_CALL"),
        ("0x0047fad0", "0x005dbdf8", "DATA"),
        ("0x0047fb00", "0x00533b5d", "UNCONDITIONAL_CALL"),
        ("0x0047fb50", "0x00487b83", "UNCONDITIONAL_CALL"),
    )
    for target, source, ref_type in expected_xrefs:
        require(
            any(
                normalize_address(row.get("target_addr", "")) == target
                and normalize_address(row.get("from_addr", "")) == source
                and row.get("ref_type") == ref_type
                for row in xrefs
            ),
            f"missing xref {source} -> {target} {ref_type}",
            failures,
        )
    require(
        sum(1 for row in xrefs if normalize_address(row.get("target_addr", "")) == "0x004659a0") == 43,
        "CDXFont__DrawTextScaledWithShadow xref count mismatch",
        failures,
    )

    help_render = read_text(BASE / "pre-decompile" / "0047fb50_CHelpTextDisplay__RenderQueuedMessages.c")
    for token in ("TextLayout__WrapWideTextToFixedLines", "CDXFont__DrawTextDynamic", "CPlatform__Font"):
        require(token in help_render, f"HelpText render decompile missing token: {token}", failures)

    dynamic_draw = read_text(BASE / "context-decompile" / "00465710_CDXFont__DrawTextDynamic.c")
    require(dynamic_draw.count("CDXFont__DrawTextScaled") >= 2, "dynamic draw decompile missing scaled draw calls", failures)

    shadow_draw = read_text(BASE / "pre-decompile" / "004659a0_CDXFont__DrawTextScaledWithShadow.c")
    for token in ("x + _DAT_005d8568", "packed_argb & 0xff000000", "CDXFont__DrawTextScaled"):
        require(token in shadow_draw, f"shadow draw decompile missing token: {token}", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected_log_tokens = {
        "pre-metadata.log": "targets=5 found=5 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=5 missing=0",
        "pre-xrefs.log": "Wrote 47 rows",
        "pre-instructions.log": "Wrote 232 function-body instruction rows",
        "pre-decompile.log": "targets=5 dumped=5 missing=0 failed=0",
        "context-metadata.log": "targets=4 found=4 missing=0",
        "context-decompile.log": "targets=4 dumped=4 missing=0 failed=0",
        "context-instructions.log": "Wrote 1252 function-body instruction rows",
    }
    for relative, token in expected_log_tokens.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR", "MISSING:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 173869959 or backup.get("totalBytes") == 173869959.0, "backup byte count mismatch", failures)
    for key in ("missingCount", "extraCount", "diffCount", "hashDiffCount"):
        require(backup.get(key) == 0, f"backup {key} mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = (
        NOTE,
        RECHECK_NOTE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    )
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIMS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    doc_specific = {
        HELP_DOC: ("Wave1005", "0x0047fb50 CHelpTextDisplay__RenderQueuedMessages", "0x00487b83", BACKUP_PATH),
        DXFONT_DOC: ("Wave1005", "0x00465710 CDXFont__DrawTextDynamic", "0x004659a0 CDXFont__DrawTextScaledWithShadow", BACKUP_PATH),
    }
    for path, tokens in doc_specific.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-help-text-display-review-wave1005")
        == r"py -3 tools\ghidra_help_text_display_review_wave1005_probe.py --check",
        "missing Wave1005 package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1005-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1005 --check",
        "missing Wave1005 aggregate recheck script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1005 HelpTextDisplay review" for row in ledger_rows), "missing Wave1005 ledger row", failures)
    require(any(row.get("task") == "Wave1005 HelpTextDisplay review" and row.get("attempt_id") == 20587 for row in attempts), "missing Wave1005 attempt row", failures)

    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    require(queue.get("totalFunctions") == 6223, "queue total mismatch", failures)
    require(quality.get("commentlessFunctionCount") == 0, "queue commentless mismatch", failures)
    require(quality.get("undefinedSignatureCount") == 0, "queue undefined mismatch", failures)
    require(quality.get("paramSignatureCount") == 0, "queue param_N mismatch", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_docs(failures)
    if failures:
        print("Wave1005 HelpTextDisplay review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1005 HelpTextDisplay review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
