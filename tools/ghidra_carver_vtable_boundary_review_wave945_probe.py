#!/usr/bin/env python3
"""Validate Wave945 CCarver vtable-boundary read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave945-carver-init-combat-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_carver_vtable_boundary_review_wave945_2026-05-28.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CARVER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Carver.cpp.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
PACKAGE_JSON = ROOT / "package.json"
STATE_FILES = [
    ROOT / "developer_agent_state.json",
    ROOT / "documentation_agent_state.json",
    ROOT / "re_orchestrator_state.json",
]

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260528-054358_post_wave945_carver_vtable_boundary_review_verified"
SCRIPT_NAME = "test:ghidra-carver-vtable-boundary-review-wave945"
SCRIPT_VALUE = r"py -3 tools\ghidra_carver_vtable_boundary_review_wave945_probe.py --check"

TARGETS = {
    "0x00422750": (
        "CCarver__Thunk_CallGuideVFunc08",
        "void __fastcall CCarver__Thunk_CallGuideVFunc08(void * this)",
        ("slot 63", "this+0x208", "vtable byte offset +0x20", "slot 8"),
    ),
    "0x004228b0": (
        "CCarver__VFunc35_RenderWithFadeGlobal",
        "void __thiscall CCarver__VFunc35_RenderWithFadeGlobal(void * this, uint render_flags)",
        ("slot 35", "this+0x280", "0x005d856c", "0x0063012c", "CThing__Render", "RET 0x4"),
    ),
    "0x00422910": (
        "CCarver__VFunc104_IsWingBlendAboveThreshold",
        "int __fastcall CCarver__VFunc104_IsWingBlendAboveThreshold(void * this)",
        ("slot 104", "this+0x280", "0x005d856c", "returns 1"),
    ),
}

EXPECTED_XREFS = {
    ("0x00422750", "0x005e0e8c", "DATA"),
    ("0x004228b0", "0x005e0e1c", "DATA"),
    ("0x00422910", "0x005e0f30", "DATA"),
}

EXPECTED_VTABLE_SLOTS = {
    ("005e0d90", "35", "004228b0", "CCarver__VFunc35_RenderWithFadeGlobal"),
    ("005e0d90", "63", "00422750", "CCarver__Thunk_CallGuideVFunc08"),
    ("005e0d90", "104", "00422910", "CCarver__VFunc104_IsWingBlendAboveThreshold"),
}

DECOMPILE_TOKENS = {
    "boundary-decompile/00422750_CCarver__Thunk_CallGuideVFunc08.c": ("0x208",),
    "boundary-decompile/004228b0_CCarver__VFunc35_RenderWithFadeGlobal.c": ("CThing__Render", "0063012c", "render_flags"),
    "boundary-decompile/00422910_CCarver__VFunc104_IsWingBlendAboveThreshold.c": ("0x280",),
}

CORE_TOKENS = (
    "Wave945",
    "carver-vtable-boundary-wave945",
    "CCarver__Thunk_CallGuideVFunc08",
    "CCarver__VFunc35_RenderWithFadeGlobal",
    "CCarver__VFunc104_IsWingBlendAboveThreshold",
    "0x00422750 CCarver__Thunk_CallGuideVFunc08",
    "0x004228b0 CCarver__VFunc35_RenderWithFadeGlobal",
    "0x00422910 CCarver__VFunc104_IsWingBlendAboveThreshold",
    "6116/6116 = 100.00%",
    "206/1408 = 14.63%",
    BACKUP,
)

OVERCLAIMS = (
    "runtime wing behavior proven",
    "runtime guide behavior proven",
    "runtime render behavior proven",
    "exact source virtual names proven",
    "fully reverse-engineered",
    "rebuild parity proven",
)


def normalize_address(value: str) -> str:
    text = (value or "").strip().lower()
    if text.startswith("0x"):
        text = text[2:]
    return "0x" + text.zfill(8)


def normalize_raw(value: str) -> str:
    return normalize_address(value)[2:]


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8-sig", errors="replace")


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    for line in read_text(path).splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def rows_by_address(path: Path) -> dict[str, dict[str, str]]:
    return {normalize_address(row["address"]): row for row in read_tsv(path)}


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "primary-metadata.tsv": 11,
        "primary-tags.tsv": 11,
        "primary-xrefs.tsv": 14,
        "primary-instructions.tsv": 300,
        "primary-decompile/index.tsv": 11,
        "context-metadata.tsv": 14,
        "context-tags.tsv": 14,
        "context-xrefs.tsv": 28,
        "context-instructions.tsv": 1189,
        "context-decompile/index.tsv": 14,
        "boundary-metadata.tsv": 3,
        "boundary-tags.tsv": 3,
        "boundary-xrefs.tsv": 4,
        "boundary-instructions.tsv": 33,
        "boundary-decompile/index.tsv": 3,
        "vtable-slots-128-post.tsv": 128,
    }
    for rel, count in expected_counts.items():
        require(len(read_tsv(BASE / rel)) == count, f"{rel} row count mismatch", failures)

    metadata = rows_by_address(BASE / "boundary-metadata.tsv")
    tags = rows_by_address(BASE / "boundary-tags.tsv")
    decompile = rows_by_address(BASE / "boundary-decompile" / "index.tsv")
    for address, (name, signature, comment_tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata {address}", failures)
        if row:
            require(row.get("name") == name, f"name mismatch {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
            for token in comment_tokens:
                require(token in row.get("comment", ""), f"missing comment token {address}: {token}", failures)
        tag_row = tags.get(address)
        require(tag_row is not None and tag_row.get("status") == "OK", f"tag status mismatch {address}", failures)
        if tag_row:
            for tag in ("carver-vtable-boundary-wave945", "wave945-readback-verified", "function-boundary-recovered"):
                require(tag in tag_row.get("tags", ""), f"missing tag {address}: {tag}", failures)
        dec = decompile.get(address)
        require(dec is not None and dec.get("signature") == signature and dec.get("status") == "OK", f"decompile mismatch {address}", failures)

    xrefs = read_tsv(BASE / "boundary-xrefs.tsv")
    for target, from_addr, ref_type in EXPECTED_XREFS:
        require(
            any(
                normalize_address(row.get("target_addr", "")) == normalize_address(target)
                and normalize_address(row.get("from_addr", "")) == normalize_address(from_addr)
                and row.get("ref_type") == ref_type
                for row in xrefs
            ),
            f"missing xref {(target, from_addr, ref_type)}",
            failures,
        )

    vtable_rows = read_tsv(BASE / "vtable-slots-128-post.tsv")
    for vtable, slot, pointer, function_name in EXPECTED_VTABLE_SLOTS:
        require(
            any(
                normalize_raw(row.get("vtable", "")) == normalize_raw(vtable)
                and row.get("slot_index") == slot
                and normalize_raw(row.get("pointer_addr", "")) == normalize_raw(pointer)
                and row.get("function_name") == function_name
                and row.get("status") == "OK"
                for row in vtable_rows
            ),
            f"missing vtable slot {(vtable, slot, pointer, function_name)}",
            failures,
        )

    for rel, tokens in DECOMPILE_TOKENS.items():
        text = read_text(BASE / rel)
        for token in tokens:
            require(token in text, f"missing decompile token {rel}: {token}", failures)


def check_logs_queue_backup(failures: list[str]) -> None:
    expected_logs = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 created=0 would_create=3 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=3 skipped=0 created=3 would_create=0 renamed=0 would_rename=0 signature_updated=3 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=3 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "boundary-metadata.log": "targets=3 found=3 missing=0",
        "boundary-tags.log": "ExportFunctionTagsByAddress complete: rows=3 missing=0",
        "boundary-xrefs.log": "Wrote 4 rows",
        "boundary-instructions.log": "Wrote 33 function-body instruction rows",
        "boundary-decompile.log": "targets=3 dumped=3 missing=0 failed=0",
        "vtable-slots-128-post.log": "ExportVtableSlots complete: targets=1 rows=128",
    }
    for rel, token in expected_logs.items():
        text = read_text(BASE / rel)
        require(token in text, f"missing log token {rel}: {token}", failures)
        require("REPORT: Save succeeded" in text, f"missing save marker {rel}", failures)
        for bad in ("LockException", "BADADDR:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token {rel}: {bad}", failures)

    quality_log = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave945.log"
    queue_log = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave945_queue_probe.log"
    require("total_functions=6116 commented_functions=6116" in read_text(quality_log), "quality refresh mismatch", failures)
    require("Total functions: 6116" in read_text(queue_log), "queue probe total mismatch", failures)

    queue = read_json(QUEUE_JSON)
    signals = queue.get("qualitySignals", {})
    require(queue.get("totalFunctions") == 6116, "queue total mismatch", failures)
    require(signals.get("commentlessFunctionCount") == 0, "queue commentless mismatch", failures)
    require(signals.get("undefinedSignatureCount") == 0, "queue undefined mismatch", failures)
    require(signals.get("paramSignatureCount") == 0, "queue param mismatch", failures)
    require(len(read_tsv(QUEUE_TSV)) == 6116, "queue TSV row count mismatch", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes", 0)) == 173312903, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    package = read_json(PACKAGE_JSON)
    require(package.get("scripts", {}).get(SCRIPT_NAME) == SCRIPT_VALUE, "missing package script", failures)

    docs = [NOTE, CAMPAIGN, GHIDRA_REFERENCE, CARVER_DOC, BACKLOG, *STATE_FILES]
    for path in docs:
        text = read_text(path)
        for token in CORE_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempt_rows = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave945 Carver vtable boundary review" for row in ledger_rows), "missing ledger row", failures)
    require(any(row.get("task") == "Wave945 Carver vtable boundary review" for row in attempt_rows), "missing attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_queue_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave945 CCarver vtable boundary review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave945 CCarver vtable boundary review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
