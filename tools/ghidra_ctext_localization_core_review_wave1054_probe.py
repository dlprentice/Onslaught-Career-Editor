#!/usr/bin/env python3
"""Validate Wave1054 CText localization-core review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1054-ctext-localization-core-review"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_ctext_localization_core_review_wave1054_2026-06-01.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1054_recheck_2026-06-01.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
TEXT_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "text.cpp" / "_index.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260601-165852_post_wave1054_ctext_localization_core_review_verified"

TARGETS = {
    "0x004f2140": "CText__ResetCoreFields",
    "0x004f2150": "CText__Ctor",
    "0x004f2170": "CText__FreeBuffer",
    "0x004f2190": "CText__GetLanguageName",
    "0x004f21f0": "CText__Init",
    "0x004f24b0": "CText__GetAudioNameById",
    "0x004f2500": "CText__GetStringByIdAfter",
    "0x004f2580": "CText__GetStringById",
}

CONTEXT = {
    "0x004f2660": "CText__CopyFrom",
    "0x00466ab0": "CFrontEnd__SetLanguage",
    "0x0046a1f0": "FrontEndText__GetLevelNameTextAfterCode",
    "0x0046a220": "FrontEndText__GetMultiplayerLevelDescriptionByType",
    "0x0046a2a0": "FrontEndText__GetLocalizedOrFallbackTextByToken",
    "0x0050d6a0": "CWorld__PushWorldTextSlot",
    "0x00412420": "CGeneralVolume__GetMode3CurrentEntryDisplayString",
    "0x004145a0": "CBattleEngineWalkerPart__GetWeaponName",
    "0x005482c0": "CDXMemBuffer__GetFileSize",
}

COMMON_TAGS = {
    "static-reaudit",
    "ctext-localization-core-review-wave1054",
    "wave1054-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "text-localization",
    "ctext-core",
}

DOC_TOKENS = (
    "Wave1054",
    "ctext-localization-core-review-wave1054",
    "0x004f2140 CText__ResetCoreFields",
    "0x004f21f0 CText__Init",
    "0x004f24b0 CText__GetAudioNameById",
    "0x004f2500 CText__GetStringByIdAfter",
    "0x004f2580 CText__GetStringById",
    "CText__CopyFrom",
    "CFrontEnd__SetLanguage",
    "CDXMemBuffer__GetFileSize",
    "769/1408 = 54.62%",
    "1065/1509 = 70.58%",
    "500/500 = 100.00%",
    "6246/6246 = 100.00%",
    BACKUP_PATH,
    "comment/tag correction",
)

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "runtime gameplay behavior proven",
    "runtime proof complete",
    "patch behavior proven",
    "rebuild parity proven",
    "all systems complete",
    "every system is complete",
    "fully reverse-engineered",
    "fully reverse engineered",
    "exact source-layout identity proven",
    "exact source layout identity proven",
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


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 8,
        "pre-tags.tsv": 8,
        "pre-xrefs.tsv": 340,
        "pre-instructions.tsv": 399,
        "pre-decompile/index.tsv": 8,
        "context-metadata.tsv": 9,
        "context-tags.tsv": 9,
        "context-xrefs.tsv": 100,
        "context-instructions.tsv": 986,
        "context-decompile/index.tsv": 9,
        "post-metadata.tsv": 8,
        "post-tags.tsv": 8,
        "post-xrefs.tsv": 340,
        "post-instructions.tsv": 399,
        "post-decompile/index.tsv": 8,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    for address, name in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            comment = row.get("comment", "")
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            require("Wave1054 CText localization-core read-back" in comment, f"missing Wave1054 comment at {address}", failures)
            require("Static retail Ghidra" in comment, f"missing static-boundary wording at {address}", failures)
            require("rebuild parity remain separate proof" in comment, f"missing proof-boundary wording at {address}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"missing common tags at {address}: {COMMON_TAGS - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("name") == name, f"decompile name mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    context = {normalize_address(row["address"]): row for row in read_tsv(BASE / "context-metadata.tsv")}
    for address, name in CONTEXT.items():
        row = context.get(address)
        require(row is not None, f"missing context metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"context name mismatch at {address}", failures)
            require(row.get("status") == "OK", f"context status mismatch at {address}", failures)

    evidence_text = "\n".join(
        [
            read_text(BASE / "post-metadata.tsv"),
            read_text(BASE / "post-tags.tsv"),
            read_text(BASE / "context-metadata.tsv"),
            *[path.read_text(encoding="utf-8-sig") for path in (BASE / "post-decompile").glob("*.c")],
            *[path.read_text(encoding="utf-8-sig") for path in (BASE / "context-decompile").glob("*.c")],
        ]
    )
    for token in ("data\\\\LANGUAGE", "0xffffffbb", "MultiByteToWideChar", "CText__CopyFrom", "CDXMemBuffer__GetFileSize"):
        require(token in evidence_text, f"missing artifact evidence token: {token}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=8 comment_updated=8 tags_added=80 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=8 skipped=0 comment_updated=8 tags_added=80 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=8 comment_updated=0 tags_added=0 missing=0 bad=0",
        "post-metadata.log": "targets=8 found=8 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=8 missing=0",
        "post-xrefs.log": "Wrote 340 rows",
        "post-instructions.log": "Wrote 399 function-body instruction rows",
        "post-decompile.log": "targets=8 dumped=8 missing=0 failed=0",
        "context-metadata.log": "targets=9 found=9 missing=0",
        "context-tags.log": "ExportFunctionTagsByAddress complete: rows=9 missing=0",
        "context-xrefs.log": "Wrote 100 rows",
        "context-instructions.log": "Wrote 986 function-body instruction rows",
        "context-decompile.log": "targets=9 dumped=9 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR", "BADNAME", "BADSIG", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6246, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    rows = read_tsv(QUEUE_TSV)
    require(len(rows) == 6246, "quality TSV row count mismatch", failures)
    require(all(row.get("comment", "").strip() for row in rows), "quality TSV contains commentless row", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 174656391 or backup.get("totalBytes") == 174656391.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        PUBLIC_NOTE,
        AGGREGATE_NOTE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        TEXT_INDEX,
        BACKLOG,
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
        scripts.get("test:ghidra-ctext-localization-core-review-wave1054")
        == r"py -3 tools\ghidra_ctext_localization_core_review_wave1054_probe.py --check",
        "missing package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1054 ctext localization core review" for row in ledger_rows), "missing Wave1054 ledger row", failures)
    require(
        any(row.get("task") == "Wave1054 ctext localization core review" and row.get("attempt_id") == 20636 for row in attempts),
        "missing Wave1054 attempt row",
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
        print("Wave1054 CText localization-core probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1054 CText localization-core probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
