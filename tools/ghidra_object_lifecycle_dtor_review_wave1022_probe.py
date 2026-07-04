#!/usr/bin/env python3
"""Validate Wave1022 object-lifecycle destructor review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1022-object-lifecycle-dtor-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_object_lifecycle_dtor_review_wave1022_2026-05-31.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1022_recheck_2026-05-31.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
SPAWNER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "SpawnerThng.cpp" / "_index.md"
ROCKET_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Rocket.cpp" / "_index.md"
WAYPOINT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "WaypointManager.cpp" / "_index.md"
SPHERE_TRIGGER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "SphereTrigger.cpp" / "_index.md"
ESCAPE_POD_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "EscapePod.cpp" / "_index.md"
THING_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "thing.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
TRACKING_STATE = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUALITY_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260531-230345_post_wave1022_object_lifecycle_dtor_review_verified"

RENAMED_TARGETS = {
    "0x004bfd80": (
        "CSpawnerThng__scalar_deleting_dtor",
        "void * __thiscall CSpawnerThng__scalar_deleting_dtor(void * this, byte flags)",
        ("Wave1022 owner-prefix normalization", "0x005dd16c", "CSpawnerThng__dtor_base", "RET 0x4"),
    ),
    "0x004bfed0": (
        "CSpawnerThng__dtor_base",
        "void __fastcall CSpawnerThng__dtor_base(void * this)",
        ("Wave1022 owner-prefix normalization", "+0x7c", "CSPtrSet__Remove", "CComplexThing__dtor_base"),
    ),
}

PRIMARY_TARGETS = {
    "0x004bfe10": "CRocket__dtor_base",
    "0x004bfe70": "CWaypoint__dtor_base",
    "0x004bfed0": "CSpawnerThng__dtor_base",
    "0x004bff30": "CComplexThing__dtor_base_Thunk_004bff30",
    "0x004bff40": "CSphereTrigger__dtor_base",
    "0x004bffa0": "CWingmanStart__dtor_base",
    "0x004c0000": "CEscapePod__dtor_base",
}

WRAPPER_TARGETS = {
    "0x004bfd40": "CRocket__scalar_deleting_dtor",
    "0x004bfd60": "CWaypoint__scalar_deleting_dtor",
    "0x004bfd80": "CSpawnerThng__scalar_deleting_dtor",
    "0x004bfda0": "CSphereTrigger__scalar_deleting_dtor",
    "0x004bfdc0": "CWingmanStart__scalar_deleting_dtor",
    "0x004bfde0": "CEscapePod__scalar_deleting_dtor",
    "0x004e5e50": "SharedComplexThing__ScalarDeletingDestructor",
}

DOC_TOKENS = (
    "Wave1022",
    "object-lifecycle-dtor-review-wave1022",
    "0x004bfd80 CSpawnerThng__scalar_deleting_dtor",
    "0x004bfed0 CSpawnerThng__dtor_base",
    "0x004bfe10 CRocket__dtor_base",
    "0x004bfe70 CWaypoint__dtor_base",
    "0x004bff40 CSphereTrigger__dtor_base",
    "0x004c0000 CEscapePod__dtor_base",
    "539/1408 = 38.28%",
    "768/1493 = 51.44%",
    "467/500 = 93.40%",
    "6238/6238 = 100.00%",
    BACKUP_PATH,
    "renamed=2",
)

OWNER_DOC_TOKENS = {
    SPAWNER_DOC: ("Wave1022", "object-lifecycle-dtor-review-wave1022", "0x004bfd80 CSpawnerThng__scalar_deleting_dtor", "0x004bfed0 CSpawnerThng__dtor_base", "0x005dd16c", BACKUP_PATH),
    ROCKET_DOC: ("Wave1022", "object-lifecycle-dtor-review-wave1022", "0x004bfe10 CRocket__dtor_base", BACKUP_PATH),
    WAYPOINT_DOC: ("Wave1022", "object-lifecycle-dtor-review-wave1022", "0x004bfe70 CWaypoint__dtor_base", BACKUP_PATH),
    SPHERE_TRIGGER_DOC: ("Wave1022", "object-lifecycle-dtor-review-wave1022", "0x004bff40 CSphereTrigger__dtor_base", BACKUP_PATH),
    ESCAPE_POD_DOC: ("Wave1022", "object-lifecycle-dtor-review-wave1022", "0x004c0000 CEscapePod__dtor_base", BACKUP_PATH),
    THING_DOC: ("Wave1022", "object-lifecycle-dtor-review-wave1022", "0x004bff30 CComplexThing__dtor_base_Thunk_004bff30", "CComplexThing__dtor_base", BACKUP_PATH),
}

OVERCLAIMS = (
    "runtime cleanup behavior proven",
    "runtime spawner cleanup behavior proven",
    "runtime object cleanup behavior proven",
    "exact source-body identity proven",
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


def rows_by(rows: list[dict[str, str]], field: str) -> dict[str, dict[str, str]]:
    return {normalize_address(row.get(field, "")): row for row in rows}


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    normalized = text.replace("\\\\\\\\", "\\").replace("\\\\", "\\")
    return token in text or token.replace("\\", "\\\\") in text or token in normalized


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "primary-metadata.tsv": 7,
        "primary-tags.tsv": 7,
        "primary-xrefs.tsv": 11,
        "primary-instructions.tsv": 152,
        "primary-decompile/index.tsv": 7,
        "context-metadata.tsv": 16,
        "context-xrefs.tsv": 76,
        "context-instructions.tsv": 809,
        "context-decompile/index.tsv": 16,
        "wrapper-metadata.tsv": 7,
        "wrapper-xrefs.tsv": 10,
        "wrapper-instructions.tsv": 77,
        "wrapper-decompile/index.tsv": 7,
        "vtable-slots.tsv": 160,
        "post-primary-metadata.tsv": 7,
        "post-primary-tags.tsv": 7,
        "post-primary-xrefs.tsv": 11,
        "post-primary-instructions.tsv": 152,
        "post-primary-decompile/index.tsv": 7,
        "post-wrapper-metadata.tsv": 7,
        "post-wrapper-tags.tsv": 7,
        "post-wrapper-xrefs.tsv": 10,
        "post-wrapper-instructions.tsv": 77,
        "post-wrapper-decompile/index.tsv": 7,
        "post-vtable-slots.tsv": 160,
    }
    for relative, expected in expected_counts.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == expected, f"{relative} row count {actual} != {expected}", failures)

    primary = rows_by(read_tsv(BASE / "post-primary-metadata.tsv"), "address")
    wrapper = rows_by(read_tsv(BASE / "post-wrapper-metadata.tsv"), "address")
    primary_tags = rows_by(read_tsv(BASE / "post-primary-tags.tsv"), "address")
    wrapper_tags = rows_by(read_tsv(BASE / "post-wrapper-tags.tsv"), "address")
    primary_decompile = rows_by(read_tsv(BASE / "post-primary-decompile" / "index.tsv"), "address")
    wrapper_decompile = rows_by(read_tsv(BASE / "post-wrapper-decompile" / "index.tsv"), "address")

    for address, name in PRIMARY_TARGETS.items():
        row = primary.get(address)
        require(row is not None, f"missing post-primary metadata {address}", failures)
        if row:
            require(row.get("name") == name, f"post-primary name mismatch {address}: {row.get('name')}", failures)
            require(row.get("status") == "OK", f"post-primary status mismatch {address}", failures)
        dec = primary_decompile.get(address)
        require(dec is not None, f"missing post-primary decompile {address}", failures)
        if dec:
            require(dec.get("status") == "OK", f"post-primary decompile status mismatch {address}", failures)

    for address, name in WRAPPER_TARGETS.items():
        row = wrapper.get(address)
        require(row is not None, f"missing post-wrapper metadata {address}", failures)
        if row:
            require(row.get("name") == name, f"post-wrapper name mismatch {address}: {row.get('name')}", failures)
            require(row.get("status") == "OK", f"post-wrapper status mismatch {address}", failures)
        dec = wrapper_decompile.get(address)
        require(dec is not None, f"missing post-wrapper decompile {address}", failures)
        if dec:
            require(dec.get("status") == "OK", f"post-wrapper decompile status mismatch {address}", failures)

    for address, (name, signature, tokens) in RENAMED_TARGETS.items():
        table = wrapper if address == "0x004bfd80" else primary
        tag_table = wrapper_tags if address == "0x004bfd80" else primary_tags
        row = table.get(address)
        require(row is not None, f"missing renamed metadata {address}", failures)
        if row:
            require(row.get("name") == name, f"renamed name mismatch {address}", failures)
            require(row.get("signature") == signature, f"renamed signature mismatch {address}: {row.get('signature')}", failures)
            for token in tokens:
                require(token in row.get("comment", ""), f"missing renamed comment token {address}: {token}", failures)
        tag_row = tag_table.get(address)
        require(tag_row is not None, f"missing renamed tag row {address}", failures)
        if tag_row:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            for token in ("object-lifecycle-dtor-review-wave1022", "wave1022-readback-verified", "owner-prefix-normalized", "retail-binary-evidence"):
                require(token in actual_tags, f"missing tag {address}: {token}", failures)

    vtable_rows = read_tsv(BASE / "post-vtable-slots.tsv")
    by_vtable_slot = {(row.get("vtable"), row.get("slot_index")): row for row in vtable_rows}
    for slot, expected_name in {
        "1": "CSpawnerThng__scalar_deleting_dtor",
        "2": "CSpawnerThng__Shutdown",
        "9": "CSpawnerThng__Init",
    }.items():
        row = by_vtable_slot.get(("005dd16c", slot))
        require(row is not None, f"missing SpawnerThng vtable slot {slot}", failures)
        if row:
            require(row.get("function_name") == expected_name, f"SpawnerThng vtable slot {slot} mismatch: {row.get('function_name')}", failures)
            require(row.get("status") == "OK", f"SpawnerThng vtable slot {slot} status mismatch", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected_log_tokens = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=2 renamed=0 would_rename=2 comment_only_updated=0 tags_added=9 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=2 skipped=0 renamed=2 would_rename=0 comment_only_updated=0 tags_added=9 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=2 renamed=0 would_rename=0 comment_only_updated=0 tags_added=0 missing=0 bad=0",
        "post-primary-metadata.log": "targets=7 found=7 missing=0",
        "post-primary-tags.log": "ExportFunctionTagsByAddress complete: rows=7 missing=0",
        "post-primary-xrefs.log": "Wrote 11 rows",
        "post-primary-instructions.log": "Wrote 152 function-body instruction rows",
        "post-primary-decompile.log": "targets=7 dumped=7 missing=0 failed=0",
        "post-wrapper-metadata.log": "targets=7 found=7 missing=0",
        "post-wrapper-tags.log": "ExportFunctionTagsByAddress complete: rows=7 missing=0",
        "post-wrapper-xrefs.log": "Wrote 10 rows",
        "post-wrapper-instructions.log": "Wrote 77 function-body instruction rows",
        "post-wrapper-decompile.log": "targets=7 dumped=7 missing=0 failed=0",
        "context-metadata.log": "targets=16 found=16 missing=0",
        "context-xrefs.log": "Wrote 76 rows",
        "context-instructions.log": "Wrote 809 function-body instruction rows",
        "context-decompile.log": "targets=16 dumped=16 missing=0 failed=0",
        "post-vtable-slots.log": "ExportVtableSlots complete: targets=10 rows=160",
    }
    for relative, token in expected_log_tokens.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR:", "BADNAME:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") in (173968263, 173968263.0), "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_queue(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6238, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    rows = rows_by(read_tsv(QUALITY_TSV), "address")
    for address, (name, signature, _) in RENAMED_TARGETS.items():
        row = rows.get(address)
        require(row is not None, f"missing quality row {address}", failures)
        if row:
            require(row.get("name") == name, f"quality name mismatch {address}: {row.get('name')}", failures)
            require(row.get("signature") == signature, f"quality signature mismatch {address}", failures)
            require("CSpawnerThing__" not in row.get("name", ""), f"stale quality name {address}", failures)
            require(row.get("comment", "").strip(), f"missing quality comment {address}", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = [
        NOTE,
        AGGREGATE_NOTE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
        TRACKING_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    for path, tokens in OWNER_DOC_TOKENS.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing owner-doc token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:ghidra-object-lifecycle-dtor-review-wave1022")
        == r"py -3 tools\ghidra_object_lifecycle_dtor_review_wave1022_probe.py --check",
        "missing focused package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1022-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1022 --check",
        "missing aggregate package script",
        failures,
    )

    ledger = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1022 object lifecycle destructor review" for row in ledger), "missing Wave1022 ledger row", failures)
    require(
        any(row.get("task") == "Wave1022 object lifecycle destructor review" and row.get("attempt_id") == 20604 for row in attempts),
        "missing Wave1022 attempt row",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_queue(failures)
    check_docs(failures)

    if failures:
        print("Wave1022 object-lifecycle destructor review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1022 object-lifecycle destructor review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
