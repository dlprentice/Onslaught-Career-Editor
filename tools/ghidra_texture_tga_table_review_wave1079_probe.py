#!/usr/bin/env python3
"""Validate Wave1079 Texture/TGA table-boundary read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1079-terrainguide-tga-table-review"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_texture_tga_table_review_wave1079_2026-06-02.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
TGALOADER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "tgaloader.cpp" / "_index.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

TARGET = "0x004f2cc0"
TARGET_RAW = "004f2cc0"
TARGET_NAME = "CTGALoader__HasNonzeroStatusOut_004f2cc0"
SIGNATURE = "bool __thiscall CTGALoader__HasNonzeroStatusOut_004f2cc0(void * this)"
BACKUP_PATH = r"G:\GhidraBackups\BEA_20260602-085858_post_wave1079_texture_tga_table_review_verified"

COMMON_TAGS = {
    "static-reaudit",
    "texture-tga-table-review-wave1079",
    "wave1079-readback-verified",
    "retail-binary-evidence",
    "function-boundary-recovered",
    "signature-hardened",
    "comment-hardened",
    "tgaloader",
    "image-loader",
    "vtable-slot",
    "slot-8",
    "status-out",
    "table-boundary",
}

DOC_TOKENS = (
    "Wave1079",
    "texture-tga-table-review-wave1079",
    f"{TARGET} {TARGET_NAME}",
    "0x005df518",
    "0x005df538",
    "0x004f2ce0 CTGALoader__Load",
    "0x00616dd0",
    "812/1408 = 57.67%",
    "1373/1560 = 88.01%",
    "500/500 = 100.00%",
    "6262/6262 = 100.00%",
    BACKUP_PATH,
    "boundary recovery",
)

OVERCLAIM_TOKENS = (
    "runtime tga/image-loading behavior proven",
    "runtime image-loading behavior proven",
    "fully reverse-engineered",
    "rebuild parity proven",
)


def normalize_address(value: str) -> str:
    value = value.strip().lower()
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
        "pre-vtable-slots.tsv": 48,
        "pre-metadata.tsv": 18,
        "pre-tags.tsv": 18,
        "pre-xrefs.tsv": 16,
        "pre-instructions.tsv": 641,
        "pre-decompile/index.tsv": 18,
        "string-00616dd0.tsv": 1,
        "suspect-diagnose.tsv": 10,
        "suspect-instructions-around.tsv": 88,
        "suspect-xrefs.tsv": 164,
        "post-metadata.tsv": 1,
        "post-tags.tsv": 1,
        "post-xrefs.tsv": 2,
        "post-instructions.tsv": 9,
        "post-decompile/index.tsv": 1,
        "post-vtable-slots.tsv": 48,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    string_rows = read_tsv(BASE / "string-00616dd0.tsv")
    require(string_rows and string_rows[0].get("target_addr") == "00616dd0", "string target mismatch", failures)
    require(string_rows and string_rows[0].get("cstring", "") == "", "expected empty string at 0x00616dd0", failures)

    pre_slot = next(
        (
            row
            for row in read_tsv(BASE / "pre-vtable-slots.tsv")
            if row.get("vtable") == "005df518" and row.get("slot_index") == "8"
        ),
        None,
    )
    require(pre_slot is not None, "missing pre CTGALoader slot 8", failures)
    if pre_slot:
        require(pre_slot.get("slot_addr") == "005df538", "pre slot address mismatch", failures)
        require(pre_slot.get("pointer_addr") == TARGET_RAW, "pre slot pointer mismatch", failures)
        require(pre_slot.get("status") == "NO_FUNCTION_AT_POINTER", "pre slot status mismatch", failures)

    post_slot = next(
        (
            row
            for row in read_tsv(BASE / "post-vtable-slots.tsv")
            if row.get("vtable") == "005df518" and row.get("slot_index") == "8"
        ),
        None,
    )
    require(post_slot is not None, "missing post CTGALoader slot 8", failures)
    if post_slot:
        require(post_slot.get("slot_addr") == "005df538", "post slot address mismatch", failures)
        require(post_slot.get("pointer_addr") == TARGET_RAW, "post slot pointer mismatch", failures)
        require(post_slot.get("function_name") == TARGET_NAME, "post slot function name mismatch", failures)
        require(post_slot.get("status") == "OK", "post slot status mismatch", failures)

    metadata = read_tsv(BASE / "post-metadata.tsv")[0]
    require(normalize_address(metadata.get("address", "")) == TARGET, "metadata address mismatch", failures)
    require(metadata.get("name") == TARGET_NAME, "metadata name mismatch", failures)
    require(metadata.get("signature") == SIGNATURE, f"metadata signature mismatch: {metadata.get('signature')}", failures)
    require(metadata.get("status") == "OK", "metadata status mismatch", failures)
    for token in ("Wave1079", "0x005df518", "0x005df538", "this+0x118", "0x004f2ce0 CTGALoader__Load"):
        require(token in metadata.get("comment", ""), f"missing metadata comment token: {token}", failures)

    tag_row = read_tsv(BASE / "post-tags.tsv")[0]
    require(normalize_address(tag_row.get("address", "")) == TARGET, "tag address mismatch", failures)
    require(COMMON_TAGS.issubset(set(tag_row.get("tags", "").split(";"))), "post tags missing Wave1079 tags", failures)

    xrefs = read_tsv(BASE / "post-xrefs.tsv")
    require(
        any(
            normalize_address(row.get("target_addr", "")) == TARGET
            and normalize_address(row.get("from_addr", "")) == "0x005df538"
            and row.get("ref_type") == "DATA"
            for row in xrefs
        ),
        "missing DATA xref from 0x005df538 to target",
        failures,
    )

    instructions = read_tsv(BASE / "post-instructions.tsv")
    joined = "\n".join(f"{row.get('instruction_addr')} {row.get('mnemonic')} {row.get('operands')}" for row in instructions)
    for token in ("0x004f2cc0 MOV EAX, dword ptr [ECX + 0x118]", "CMP dword ptr [EAX], 0x0", "0x004f2cd7 RET"):
        require(token in joined, f"missing instruction token: {token}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 created=0 would_create=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=1 skipped=0 created=1 would_create=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=1 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=1 found=1 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=1 missing=0",
        "post-xrefs.log": "Wrote 2 rows",
        "post-instructions.log": "Wrote 9 function-body instruction rows",
        "post-decompile.log": "targets=1 dumped=1 missing=0 failed=0",
        "post-vtable-slots.log": "rows=48",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BADNAME:", "FAIL:", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    quality_text = read_text(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave1079.log")
    queue_text = read_text(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave1079_queue_probe.log")
    require("total_functions=6262 commented_functions=6262" in quality_text, "quality refresh token mismatch", failures)
    require("Total functions: 6262" in queue_text, "queue probe total mismatch", failures)
    require("Commentless functions: 0" in queue_text, "queue probe commentless mismatch", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6262, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "queue commentless mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "queue undefined mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "queue param_N mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    require(len(rows) == 6262, "quality TSV row count mismatch", failures)
    require(commented == 6262, "quality TSV commented mismatch", failures)
    require(strict_clean == 6262, "quality TSV strict-clean mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 174754695, "backup byte count mismatch", failures)
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
        TGALOADER_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1079-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1079 --check",
        "missing Wave1079 cumulative recheck script",
        failures,
    )
    require(
        scripts.get("test:ghidra-texture-tga-table-review-wave1079")
        == r"py -3 tools\ghidra_texture_tga_table_review_wave1079_probe.py --check",
        "missing Wave1079 focused package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1079 Texture/TGA table review" for row in ledger_rows), "missing Wave1079 ledger row", failures)
    require(
        any(row.get("task") == "Wave1079 Texture/TGA table review" and row.get("attempt_id") == 20661 for row in attempts),
        "missing Wave1079 attempt row",
        failures,
    )


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
        print("Wave1079 Texture/TGA table review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1079 Texture/TGA table review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
