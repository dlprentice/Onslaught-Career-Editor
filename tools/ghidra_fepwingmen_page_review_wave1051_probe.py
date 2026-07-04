#!/usr/bin/env python3
"""Validate Wave1051 FEPWingmen page-review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1051-fepwingmen-page-review"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_fepwingmen_page_review_wave1051_2026-06-01.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1051_recheck_2026-06-01.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
WINGMEN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FEPWingmen.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260601-150857_post_wave1051_fepwingmen_page_review_verified"

PRIMARY_SIGNATURES = {
    "0x00521650": ("CFEPWingmen__GetWingmenCount", "char CFEPWingmen__GetWingmenCount(void)"),
    "0x005216c0": ("CFEPWingmen__Init", "int __fastcall CFEPWingmen__Init(void * this)"),
    "0x00521a60": ("CFEPWingmen__Destroy", "void __fastcall CFEPWingmen__Destroy(void * this)"),
    "0x00521ae0": ("CFEPWingmen__Load", "void __thiscall CFEPWingmen__Load(void * this, void * stream)"),
    "0x00521c80": ("CFEPWingmen__Update", "void __thiscall CFEPWingmen__Update(void * this, int state)"),
    "0x00521d20": (
        "CFEPWingmen__ButtonPressed",
        "void __thiscall CFEPWingmen__ButtonPressed(void * this, int button, float val)",
    ),
    "0x00522160": (
        "CFEPWingmen__RenderPreCommon",
        "void __stdcall CFEPWingmen__RenderPreCommon(float transition, int dest)",
    ),
    "0x00522190": (
        "CFEPWingmen__Render",
        "void __thiscall CFEPWingmen__Render(void * this, float transition, int dest)",
    ),
    "0x005230c0": (
        "CFEPWingmen__TransitionNotification",
        "void __thiscall CFEPWingmen__TransitionNotification(void * this, int from_page)",
    ),
    "0x005230e0": (
        "CFEPWingmen__FindCurrentLevelRecord",
        "void * __thiscall CFEPWingmen__FindCurrentLevelRecord(void * this)",
    ),
    "0x0046baf0": (
        "CFEPWingmen__UpdateSpinnerTransformAndPulse",
        "void __thiscall CFEPWingmen__UpdateSpinnerTransformAndPulse(void * this)",
    ),
}

COMMON_TAGS = {
    "static-reaudit",
    "fepwingmen-page-review-wave1051",
    "wave1051-readback-verified",
    "retail-binary-evidence",
    "frontend-wingmen",
    "page-consolidation",
}

VTABLE_SLOTS = {
    "0": ("005216c0", "CFEPWingmen__Init", "OK"),
    "1": ("00521a60", "CFEPWingmen__Destroy", "OK"),
    "2": ("00521c80", "CFEPWingmen__Update", "OK"),
    "3": ("00521d20", "CFEPWingmen__ButtonPressed", "OK"),
    "4": ("00522160", "CFEPWingmen__RenderPreCommon", "OK"),
    "5": ("00522190", "CFEPWingmen__Render", "OK"),
    "6": ("005230c0", "CFEPWingmen__TransitionNotification", "OK"),
    "7": ("00452b60", "CFrontEndPage__Process_NoOp", "OK"),
    "8": ("0040c640", "DebugTrace", "OK"),
    "9": ("00521ae0", "CFEPWingmen__Load", "OK"),
    "10": ("006139a8", "<no_function>", "NO_FUNCTION_AT_POINTER"),
}

DOC_TOKENS = (
    "Wave1051",
    "fepwingmen-page-review-wave1051",
    "0x00521c80 CFEPWingmen__Update",
    "0x00521d20 CFEPWingmen__ButtonPressed",
    "0x00522190 CFEPWingmen__Render",
    "0x005230e0 CFEPWingmen__FindCurrentLevelRecord",
    "CFEPWingmen__UpdateSpinnerTransformAndPulse",
    "0x005dba10 CFEPWingmen_vtable",
    "0x006139a8",
    "NO_FUNCTION_AT_POINTER",
    r"[maintainer-local-source-export-root]\FEPWingmen.cpp",
    "744/1408 = 52.84%",
    "1032/1509 = 68.39%",
    "500/500 = 100.00%",
    "6246/6246 = 100.00%",
    BACKUP_PATH,
    "comment/tag normalization",
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
        "metadata.tsv": 11,
        "tags.tsv": 11,
        "xrefs.tsv": 27,
        "instructions.tsv": 1818,
        "decompile/index.tsv": 11,
        "post-metadata.tsv": 11,
        "post-tags.tsv": 11,
        "post-xrefs.tsv": 27,
        "post-instructions.tsv": 1818,
        "post-decompile/index.tsv": 11,
        "context-metadata.tsv": 15,
        "context-tags.tsv": 15,
        "context-xrefs.tsv": 321,
        "context-instructions.tsv": 3472,
        "context-decompile/index.tsv": 15,
        "vtable-slots.tsv": 11,
        "post-vtable-slots.tsv": 11,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    string_rows = read_tsv(BASE / "string-0063fd4c.tsv")
    require(
        bool(string_rows) and string_rows[0].get("cstring") == r"[maintainer-local-source-export-root]\FEPWingmen.cpp",
        "FEPWingmen debug-string dump mismatch",
        failures,
    )

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    for address, (name, signature) in PRIMARY_SIGNATURES.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    update = metadata.get("0x00521c80", {})
    update_comment = update.get("comment", "")
    for token in (
        "Wave1051 FEPWingmen page correction",
        "0x00521d20 CFEPWingmen__ButtonPressed",
        "older missing-boundary-deferred wording/tag is closed",
        "FEPWingmen.cpp source is absent",
    ):
        require(token in update_comment, f"missing update comment token: {token}", failures)

    record = metadata.get("0x005230e0", {})
    record_comment = record.get("comment", "")
    for token in (
        "Wave1051 FEPWingmen page normalization",
        "older deferred-callsite framing is superseded",
        "CFEPWingmen__ButtonPressed and CFEPWingmen__Render",
        "DAT_0089d94c",
    ):
        require(token in record_comment, f"missing record-helper comment token: {token}", failures)

    tags = {normalize_address(row["address"]): set(row.get("tags", "").split(";")) for row in read_tsv(BASE / "post-tags.tsv")}
    for address in PRIMARY_SIGNATURES:
        actual = tags.get(address, set())
        require(COMMON_TAGS.issubset(actual), f"missing common tags at {address}: {COMMON_TAGS - actual}", failures)
    update_tags = tags.get("0x00521c80", set())
    require("missing-boundary-deferred" not in update_tags, "stale missing-boundary-deferred tag remains", failures)

    context_missing = [row for row in read_tsv(BASE / "context-metadata.tsv") if row.get("status") == "MISSING"]
    require(len(context_missing) == 1 and normalize_address(context_missing[0].get("address", "")) == "0x0046a180", "context missing row mismatch", failures)

    vtable_rows = read_tsv(BASE / "post-vtable-slots.tsv")
    for slot, (pointer, expected_name, expected_status) in VTABLE_SLOTS.items():
        row = next((item for item in vtable_rows if item.get("slot_index") == slot), None)
        require(row is not None, f"missing vtable slot {slot}", failures)
        if row is not None:
            require(row.get("pointer_addr") == pointer, f"vtable slot {slot} pointer mismatch", failures)
            require(row.get("function_name") == expected_name, f"vtable slot {slot} name mismatch", failures)
            require(row.get("status") == expected_status, f"vtable slot {slot} status mismatch", failures)

    decompile_tokens = {
        "post-decompile/00521c80_CFEPWingmen__Update.c": (
            "CFEPWingmen__UpdateSpinnerTransformAndPulse",
            "CFEPWingmen__ButtonPressed",
        ),
        "post-decompile/00521d20_CFEPWingmen__ButtonPressed.c": (
            "CFEPWingmen__FindCurrentLevelRecord(&DAT_0089da44)",
            "CFrontEnd__PlaySound",
        ),
        "post-decompile/00522190_CFEPWingmen__Render.c": (
            "CFEPWingmen__FindCurrentLevelRecord(&DAT_0089da44)",
            "CDXSurf__RenderSurface",
            "CFrontEnd__RenderOverlayEffects",
        ),
        "post-decompile/005230e0_CFEPWingmen__FindCurrentLevelRecord.c": ("DAT_0089d94c",),
    }
    for relative, tokens in decompile_tokens.items():
        text = read_text(BASE / relative)
        for token in tokens:
            require(token in text, f"missing decompile token in {relative}: {token}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=11 comment_updated=2 tags_added=51 tags_removed=0 would_remove_tags=1 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=11 skipped=0 comment_updated=2 tags_added=51 tags_removed=1 would_remove_tags=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=11 comment_updated=0 tags_added=0 tags_removed=0 would_remove_tags=0 missing=0 bad=0",
        "metadata.log": "targets=11 found=11 missing=0",
        "tags.log": "ExportFunctionTagsByAddress complete: rows=11 missing=0",
        "xrefs.log": "Wrote 27 rows",
        "instructions.log": "Wrote 1818 function-body instruction rows",
        "decompile.log": "targets=11 dumped=11 missing=0 failed=0",
        "post-metadata.log": "targets=11 found=11 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=11 missing=0",
        "post-xrefs.log": "Wrote 27 rows",
        "post-instructions.log": "Wrote 1818 function-body instruction rows",
        "post-decompile.log": "targets=11 dumped=11 missing=0 failed=0",
        "context-metadata.log": "targets=15 found=14 missing=1",
        "context-tags.log": "ExportFunctionTagsByAddress complete: rows=14 missing=1",
        "context-xrefs.log": "Wrote 321 rows",
        "context-instructions.log": "Wrote 3472 function-body instruction rows",
        "context-decompile.log": "targets=15 dumped=14 missing=1 failed=0",
        "post-vtable-slots.log": "ExportVtableSlots complete: targets=1 rows=11",
        "quality-refresh.log": "total_functions=6246 commented_functions=6246",
        "queue-probe.log": "Status: PASS",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        require("LockException" not in text, f"unexpected LockException in {relative}", failures)
        require("BADADDR" not in text and "BADNAME" not in text and "FAIL:" not in text, f"unexpected bad/fail token in {relative}", failures)
        if relative not in {"context-metadata.log", "context-tags.log", "context-instructions.log", "context-decompile.log"}:
            require("missing=1" not in text and "bad=1" not in text and "failed=1" not in text, f"unexpected failure count in {relative}", failures)
        if relative != "queue-probe.log":
            require("REPORT: Save succeeded" in text, f"missing save success in {relative}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6246, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 174623623, "backup byte count mismatch", failures)
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
        WINGMEN_INDEX,
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
        scripts.get("test:ghidra-fepwingmen-page-review-wave1051")
        == r"py -3 tools\ghidra_fepwingmen_page_review_wave1051_probe.py --check",
        "missing focused package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1051-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1051 --check",
        "missing aggregate package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1051 fepwingmen page review" for row in ledger_rows), "missing Wave1051 ledger row", failures)
    require(
        any(row.get("task") == "Wave1051 fepwingmen page review" and row.get("attempt_id") == 20633 for row in attempts),
        "missing Wave1051 attempt row",
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
        print("Wave1051 FEPWingmen page-review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1051 FEPWingmen page-review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
