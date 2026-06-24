#!/usr/bin/env python3
"""Validate Wave998 fatal-error spine no-return correction artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave998-fatal-error-spine-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_fatal_error_spine_review_wave998_2026-05-31.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
CONSOLE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "console.cpp" / "_index.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
TRACKING_STATE = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260531-091151_post_wave998_fatal_error_spine_review_verified"

TARGETS = {
    "0x0042c750": (
        "FatalError__ExitWithLocalizedPrefix_A",
        "noreturn void __stdcall FatalError__ExitWithLocalizedPrefix_A(char * message, int callerContext)",
        ("Wave998 fatal-error spine correction", "0x00624624", "FatalError__ExitProcess", "RET 0x8"),
        {"fatal-error-spine-review-wave998", "wave998-readback-verified", "no-return", "localized-prefix", "two-argument-wrapper"},
    ),
    "0x0042d0b0": (
        "FatalError__ExitWithLocalizedPrefix_B",
        "noreturn void __stdcall FatalError__ExitWithLocalizedPrefix_B(char * message)",
        ("Wave998 fatal-error spine correction", "mesh/resource deserialize", "FatalError__ExitProcess", "RET 0x4"),
        {"fatal-error-spine-review-wave998", "wave998-readback-verified", "no-return", "localized-prefix", "single-argument-wrapper"},
    ),
    "0x0042cfa0": (
        "FatalError__ExitProcess",
        "noreturn void __cdecl FatalError__ExitProcess(char * message, int code)",
        ("Wave386 fatal-error correction", "ExitProcess"),
        {"fatal-error", "no-return", "process-exit"},
    ),
    "0x0042d080": (
        "FatalError_LocalizedStringId",
        "void __stdcall FatalError_LocalizedStringId(char gate, int stringId, int code)",
        ("Wave386 fatal-error correction", "guard byte"),
        {"fatal-error", "guard-gated", "localized-string"},
    ),
}

DOC_TOKENS = (
    "Wave998",
    "fatal-error-spine-review-wave998",
    "0x0042c750 FatalError__ExitWithLocalizedPrefix_A",
    "noreturn void __stdcall FatalError__ExitWithLocalizedPrefix_A(char * message, int callerContext)",
    "0x0042d0b0 FatalError__ExitWithLocalizedPrefix_B",
    "noreturn void __stdcall FatalError__ExitWithLocalizedPrefix_B(char * message)",
    "0x0042cfa0 FatalError__ExitProcess",
    "0x0042d080 FatalError_LocalizedStringId",
    "467/1408 = 33.17%",
    "585/1478 = 39.58%",
    "6222/6222 = 100.00%",
    BACKUP_PATH,
)

OVERCLAIMS = (
    "runtime fatal behavior proven",
    "runtime fatal ui proven",
    "exact source identity proven",
    "exact layout proven",
    "rebuild parity proven",
)

EXPECTED_LOG_TOKENS = {
    "apply-dry.log": ("SUMMARY: updated=0 skipped=2 no_return_updated=2 comment_only_updated=0 tags_added=12 missing=0 bad=0", "REPORT: Save succeeded"),
    "apply.log": ("SUMMARY: updated=2 skipped=0 no_return_updated=2 comment_only_updated=0 tags_added=12 missing=0 bad=0", "REPORT: Save succeeded"),
    "apply-final-dry.log": ("SUMMARY: updated=0 skipped=2 no_return_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0", "REPORT: Save succeeded"),
    "post-metadata.log": ("targets=4 found=4 missing=0", "REPORT: Save succeeded"),
    "post-tags.log": ("ExportFunctionTagsByAddress complete: rows=4 missing=0", "REPORT: Save succeeded"),
    "post-xrefs.log": ("Wrote 71 rows", "REPORT: Save succeeded"),
    "post-instructions.log": ("Wrote 209 function-body instruction rows", "targets=4 missing=0", "REPORT: Save succeeded"),
    "post-decompile.log": ("targets=4 dumped=4 missing=0 failed=0", "REPORT: Save succeeded"),
}


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
    if token in text or token.replace("\\", "\\\\") in text or token.replace("\\", "\\\\\\\\") in text:
        return True
    def collapse_backslashes(value: str) -> str:
        previous = None
        current = value
        while previous != current:
            previous = current
            current = current.replace("\\\\\\\\", "\\").replace("\\\\", "\\")
        return current
    return collapse_backslashes(token) in collapse_backslashes(text)


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 4,
        "pre-tags.tsv": 4,
        "pre-xrefs.tsv": 71,
        "pre-instructions.tsv": 209,
        "pre-decompile/index.tsv": 4,
        "post-metadata.tsv": 4,
        "post-tags.tsv": 4,
        "post-xrefs.tsv": 71,
        "post-instructions.tsv": 209,
        "post-decompile/index.tsv": 4,
    }
    for relative, expected in expected_counts.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == expected, f"{relative} row count {actual} != {expected}", failures)

    metadata = read_tsv(BASE / "post-metadata.tsv")
    tags = read_tsv(BASE / "post-tags.tsv")
    decompile_index = read_tsv(BASE / "post-decompile" / "index.tsv")
    for address, (name, signature, comment_tokens, expected_tags) in TARGETS.items():
        row = row_by_address(metadata, address)
        require(row is not None, f"metadata missing {address}", failures)
        if row:
            require(row.get("name") == name, f"metadata name mismatch {address}", failures)
            require(row.get("signature") == signature, f"metadata signature mismatch {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
            comment = row.get("comment", "")
            for token in comment_tokens:
                require(token in comment, f"comment token missing {address}: {token}", failures)

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
            require(expected_tags.issubset(actual_tags), f"tags missing {address}: {expected_tags - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch {address}", failures)

    xrefs = read_tsv(BASE / "post-xrefs.tsv")
    expected_xrefs = (
        ("0x0042c750", "0x004b7e05", "CGame__PumpBinkVoiceSampleQueue"),
        ("0x0042c750", "0x004f28af", "CTexture__FindTexture"),
        ("0x0042c750", "0x005480d0", "CDXMemBuffer__InitFromFile"),
        ("0x0042cfa0", "0x0042c7ef", "FatalError__ExitWithLocalizedPrefix_A"),
        ("0x0042cfa0", "0x0042d14f", "FatalError__ExitWithLocalizedPrefix_B"),
        ("0x0042d0b0", "0x004aad6c", "CMesh__Deserialize"),
        ("0x0042d080", "0x005139ff", "CEngine__CreateTextureOrFatal"),
        ("0x0042d080", "0x0052b035", "CD3DApplication__Initialize3DEnvironment"),
    )
    for target, source, function_name in expected_xrefs:
        require(
            any(
                normalize_address(row.get("target_addr", "")) == target
                and normalize_address(row.get("from_addr", "")) == source
                and row.get("from_function") == function_name
                and row.get("ref_type") == "UNCONDITIONAL_CALL"
                for row in xrefs
            ),
            f"missing xref {source} -> {target} {function_name}",
            failures,
        )

    instructions = read_tsv(BASE / "post-instructions.tsv")
    instruction_checks = (
        ("0x0042c750", "0x0042c759", "PUSH", "0xcc"),
        ("0x0042c750", "0x0042c794", "MOV", "EDI, 0x624624"),
        ("0x0042c750", "0x0042c7ef", "CALL", "0x0042cfa0"),
        ("0x0042d0b0", "0x0042d0b9", "PUSH", "0xcc"),
        ("0x0042d0b0", "0x0042d0f4", "MOV", "EDI, 0x624624"),
        ("0x0042d0b0", "0x0042d14f", "CALL", "0x0042cfa0"),
    )
    for target, instr_addr, mnemonic, operands in instruction_checks:
        require(
            any(
                normalize_address(row.get("target_addr", "")) == target
                and row.get("instruction_addr") == instr_addr
                and row.get("mnemonic") == mnemonic
                and row.get("operands") == operands
                for row in instructions
            ),
            f"missing instruction {target} {instr_addr} {mnemonic} {operands}",
            failures,
        )


def check_logs_and_backup(failures: list[str]) -> None:
    for relative, tokens in EXPECTED_LOG_TOKENS.items():
        text = read_text(BASE / relative)
        for token in tokens:
            require(token in text, f"missing log token {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR", "FAIL:", "missing=1", "failed=1", "bad=1"):
            require(bad not in text, f"bad log token {relative}: {bad}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 173869959 or backup.get("totalBytes") == 173869959.0, "backup bytes mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_docs_and_state(failures: list[str]) -> None:
    core_docs = (
        NOTE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        CONSOLE_DOC,
        BACKLOG,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
        TRACKING_STATE,
    )
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing doc token {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lowered, f"overclaim token {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-fatal-error-spine-review-wave998")
        == r"py -3 tools\ghidra_fatal_error_spine_review_wave998_probe.py --check",
        "missing focused package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave998-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 998 --check",
        "missing wave900+ recheck package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempt_rows = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave998 fatal-error spine no-return correction" for row in ledger_rows), "missing Wave998 ledger row", failures)
    require(
        any(
            row.get("attempt_id") == 20582
            and row.get("task") == "Wave998 fatal-error spine no-return correction"
            and row.get("updated") == 2
            and row.get("signature_updated") == 2
            for row in attempt_rows
        ),
        "missing Wave998 attempt row",
        failures,
    )

    tracking = read_json(TRACKING_STATE)
    require(tracking.get("next_attempt_id") == 20583, "tracking next_attempt_id mismatch", failures)
    counters = tracking.get("counters", {})
    require(counters.get("ledger_rows") == 1322, "tracking ledger_rows mismatch", failures)
    require(counters.get("attempt_rows") == 20582, "tracking attempt_rows mismatch", failures)
    require(tracking.get("last_completed", {}).get("wave") == "Wave998 fatal-error spine review", "tracking last_completed mismatch", failures)

    queue = read_json(QUEUE_JSON)
    require(queue.get("totalFunctions") == 6222, "queue total mismatch", failures)
    quality = queue.get("qualitySignals", {})
    require(quality.get("commentlessFunctionCount") == 0, "queue commentless mismatch", failures)
    require(quality.get("undefinedSignatureCount") == 0, "queue undefined mismatch", failures)
    require(quality.get("paramSignatureCount") == 0, "queue param mismatch", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_docs_and_state(failures)

    if failures:
        print("Wave998 fatal-error spine review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave998 fatal-error spine review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
