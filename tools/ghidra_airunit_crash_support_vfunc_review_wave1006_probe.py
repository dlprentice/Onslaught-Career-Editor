#!/usr/bin/env python3
"""Validate Wave1006 air-unit crash/support vfunc review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1006-airunit-crash-support-vfunc-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_airunit_crash_support_vfunc_review_wave1006_2026-05-31.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
AIRUNIT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "AirUnit.cpp" / "_index.md"
PLANE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Plane.cpp" / "_index.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260531-135619_post_wave1006_airunit_crash_support_vfunc_review_verified"

TARGETS = {
    "0x00402fa0": ("CUnit__UpdateMotionAndTrailEffects", "void __thiscall CUnit__UpdateMotionAndTrailEffects(void * this)"),
    "0x00403730": ("CAirUnit__VFunc_68_TimestampAndCrashIfNoAirSupport", "void __thiscall CAirUnit__VFunc_68_TimestampAndCrashIfNoAirSupport(void * this)"),
    "0x00403760": ("CAirUnit__VFunc_69_ResetD0AndCrashIfNoSupportModes", "void __thiscall CAirUnit__VFunc_69_ResetD0AndCrashIfNoSupportModes(void * this)"),
    "0x00403a50": ("CAirUnit__VFunc_117_HasPositionDeltaWhileFlag4Clear", "int __thiscall CAirUnit__VFunc_117_HasPositionDeltaWhileFlag4Clear(void * this)"),
    "0x0047bf60": ("CPlane__VFunc_69_CrashIfNoSupportModes", "void __thiscall CPlane__VFunc_69_CrashIfNoSupportModes(void * this)"),
    "0x004d20a0": ("CPlane__VFunc_68_CrashIfNoAirSupport", "void __thiscall CPlane__VFunc_68_CrashIfNoAirSupport(void * this)"),
}

CONTEXT_TARGETS = {
    "0x00402d30": "CAirUnit__dtor_base",
    "0x00422620": "CCarver__UpdateMotionAndWingPose",
    "0x0050f0a0": "CAirUnit__ctor_base",
    "0x0050f420": "CAirUnit__scalar_deleting_dtor",
    "0x0050f440": "CAirUnit__ClearPtrSetsRemoveFromGlobalListAndDestruct",
}

EXPECTED_VTABLE_TYPES = {
    "005e0430": "CFenrir",
    "005e0d8c": "CCarver",
    "005e123c": "CDiveBomber",
    "005e1930": "CPlane",
    "005e2038": "CCarrier",
    "005e2bcc": "CGroundAttackAircraft",
    "005e2e20": "CBomber",
    "005e3524": "CBigAirUnit",
    "005e3778": "CAirUnit",
}

EXPECTED_SLOT_FUNCTIONS = {
    ("005e3524", "66"): "CUnit__UpdateMotionAndTrailEffects",
    ("005e3778", "66"): "CUnit__UpdateMotionAndTrailEffects",
    ("005e0430", "68"): "CAirUnit__VFunc_68_TimestampAndCrashIfNoAirSupport",
    ("005e0d8c", "68"): "CAirUnit__VFunc_68_TimestampAndCrashIfNoAirSupport",
    ("005e2038", "68"): "CAirUnit__VFunc_68_TimestampAndCrashIfNoAirSupport",
    ("005e3524", "68"): "CAirUnit__VFunc_68_TimestampAndCrashIfNoAirSupport",
    ("005e3778", "68"): "CAirUnit__VFunc_68_TimestampAndCrashIfNoAirSupport",
    ("005e0430", "69"): "CAirUnit__VFunc_69_ResetD0AndCrashIfNoSupportModes",
    ("005e0d8c", "69"): "CAirUnit__VFunc_69_ResetD0AndCrashIfNoSupportModes",
    ("005e2038", "69"): "CAirUnit__VFunc_69_ResetD0AndCrashIfNoSupportModes",
    ("005e3524", "69"): "CAirUnit__VFunc_69_ResetD0AndCrashIfNoSupportModes",
    ("005e3778", "69"): "CAirUnit__VFunc_69_ResetD0AndCrashIfNoSupportModes",
    ("005e123c", "68"): "CPlane__VFunc_68_CrashIfNoAirSupport",
    ("005e1930", "68"): "CPlane__VFunc_68_CrashIfNoAirSupport",
    ("005e2bcc", "68"): "CPlane__VFunc_68_CrashIfNoAirSupport",
    ("005e2e20", "68"): "CPlane__VFunc_68_CrashIfNoAirSupport",
    ("005e123c", "69"): "CPlane__VFunc_69_CrashIfNoSupportModes",
    ("005e1930", "69"): "CPlane__VFunc_69_CrashIfNoSupportModes",
    ("005e2bcc", "69"): "CPlane__VFunc_69_CrashIfNoSupportModes",
    ("005e2e20", "69"): "CPlane__VFunc_69_CrashIfNoSupportModes",
}

COMMON_TAGS = {
    "static-reaudit",
    "air-unit-crash-support-vfunc-review-wave1006",
    "wave1006-readback-verified",
    "retail-binary-evidence",
    "comment-normalized",
    "tag-normalized",
    "vtable-slot-evidence",
}

DOC_TOKENS = (
    "Wave1006",
    "air-unit-crash-support-vfunc-review-wave1006",
    "0x00402fa0 CUnit__UpdateMotionAndTrailEffects",
    "0x00403730 CAirUnit__VFunc_68_TimestampAndCrashIfNoAirSupport",
    "0x00403760 CAirUnit__VFunc_69_ResetD0AndCrashIfNoSupportModes",
    "0x00403a50 CAirUnit__VFunc_117_HasPositionDeltaWhileFlag4Clear",
    "0x0047bf60 CPlane__VFunc_69_CrashIfNoSupportModes",
    "0x004d20a0 CPlane__VFunc_68_CrashIfNoAirSupport",
    "485/1408 = 34.45%",
    "662/1478 = 44.79%",
    "384/500 = 76.80%",
    "6223/6223 = 100.00%",
    BACKUP_PATH,
)

OVERCLAIMS = (
    "runtime aircraft crash behavior proven",
    "runtime flight behavior proven",
    "runtime support-mode behavior proven",
    "exact source virtual names proven",
    "concrete layout proven",
    "exact source-body identity proven",
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


def normalize_vtable(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return value.zfill(8)


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
        "pre-metadata.tsv": 6,
        "pre-tags.tsv": 6,
        "pre-xrefs.tsv": 39,
        "pre-instructions.tsv": 570,
        "pre-decompile/index.tsv": 6,
        "context-metadata.tsv": 5,
        "context-decompile/index.tsv": 5,
        "context-instructions.tsv": 200,
        "vtable-slots.tsv": 1152,
        "vtable-types.tsv": 9,
        "post-metadata.tsv": 6,
        "post-tags.tsv": 6,
        "post-xrefs.tsv": 39,
        "post-instructions.tsv": 570,
        "post-decompile/index.tsv": 6,
    }
    for relative, expected in expected_counts.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == expected, f"{relative} row count {actual} != {expected}", failures)

    pre_tags = read_tsv(BASE / "pre-tags.tsv")
    for address in TARGETS:
        tag_row = row_by_address(pre_tags, address)
        require(tag_row is not None, f"pre-tags missing {address}", failures)
        if tag_row:
            require(tag_row.get("tags", "") == "", f"pre-tags unexpectedly nonempty {address}", failures)

    metadata = read_tsv(BASE / "post-metadata.tsv")
    tags = read_tsv(BASE / "post-tags.tsv")
    decompile_index = read_tsv(BASE / "post-decompile" / "index.tsv")
    for address, (name, signature) in TARGETS.items():
        row = row_by_address(metadata, address)
        require(row is not None, f"metadata missing {address}", failures)
        if row:
            require(row.get("name") == name, f"metadata name mismatch {address}", failures)
            require(row.get("signature") == signature, f"metadata signature mismatch {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
            for token in ("Wave1006 static re-audit metadata normalization", "Static retail Ghidra metadata/xref/decompile/vtable evidence only"):
                require(token in row.get("comment", ""), f"metadata comment missing {address}: {token}", failures)

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
            missing = COMMON_TAGS - actual_tags
            require(not missing, f"post-tags missing {address}: {sorted(missing)}", failures)

    context = read_tsv(BASE / "context-metadata.tsv")
    context_index = read_tsv(BASE / "context-decompile" / "index.tsv")
    for address, name in CONTEXT_TARGETS.items():
        row = row_by_address(context, address)
        require(row is not None, f"context metadata missing {address}", failures)
        if row:
            require(row.get("name") == name, f"context name mismatch {address}", failures)
            require(row.get("status") == "OK", f"context status mismatch {address}", failures)
        dec = row_by_address(context_index, address)
        require(dec is not None, f"context decompile missing {address}", failures)
        if dec:
            require(dec.get("name") == name, f"context decompile name mismatch {address}", failures)
            require(dec.get("status") == "OK", f"context decompile status mismatch {address}", failures)

    vtable_types = {normalize_vtable(row.get("vtable", "")): row for row in read_tsv(BASE / "vtable-types.tsv")}
    for vtable, type_name in EXPECTED_VTABLE_TYPES.items():
        row = vtable_types.get(vtable)
        require(row is not None, f"vtable type missing {vtable}", failures)
        if row:
            require(row.get("demangled_type_name") == type_name, f"vtable type mismatch {vtable}: {row.get('demangled_type_name')}", failures)

    slot_rows = {
        (normalize_vtable(row.get("vtable", "")), row.get("slot_index", "")): row
        for row in read_tsv(BASE / "vtable-slots.tsv")
    }
    for (vtable, slot), function_name in EXPECTED_SLOT_FUNCTIONS.items():
        row = slot_rows.get((vtable, slot))
        require(row is not None, f"vtable slot missing {vtable} slot {slot}", failures)
        if row:
            require(row.get("function_name") == function_name, f"vtable slot mismatch {vtable} slot {slot}: {row.get('function_name')}", failures)
            require(row.get("status") == "OK", f"vtable slot status mismatch {vtable} slot {slot}: {row.get('status')}", failures)
    for vtable in EXPECTED_VTABLE_TYPES:
        row = slot_rows.get((vtable, "117"))
        require(row is not None, f"slot 117 missing {vtable}", failures)
        if row:
            require(row.get("function_name") == "CAirUnit__VFunc_117_HasPositionDeltaWhileFlag4Clear", f"slot 117 mismatch {vtable}", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected_log_tokens = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=6 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=6 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=6 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=6 found=6 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=6 missing=0",
        "post-xrefs.log": "Wrote 39 rows",
        "post-instructions.log": "Wrote 570 function-body instruction rows",
        "post-decompile.log": "targets=6 dumped=6 missing=0 failed=0",
        "vtable-slots.log": "ExportVtableSlots complete: targets=9 rows=1152",
        "vtable-types.log": "ResolveVtableTypeNames complete: rows=9",
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
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        BACKLOG,
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
        AIRUNIT_DOC: ("Wave1006", "0x00402fa0 CUnit__UpdateMotionAndTrailEffects", "0x00403730 CAirUnit__VFunc_68_TimestampAndCrashIfNoAirSupport", "0x00403a50 CAirUnit__VFunc_117_HasPositionDeltaWhileFlag4Clear", BACKUP_PATH),
        PLANE_DOC: ("Wave1006", "0x0047bf60 CPlane__VFunc_69_CrashIfNoSupportModes", "0x004d20a0 CPlane__VFunc_68_CrashIfNoAirSupport", "0x005e1930", BACKUP_PATH),
    }
    for path, tokens in doc_specific.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-airunit-crash-support-vfunc-review-wave1006")
        == r"py -3 tools\ghidra_airunit_crash_support_vfunc_review_wave1006_probe.py --check",
        "missing Wave1006 package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1006-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1006 --check",
        "missing Wave1006 aggregate recheck script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1006 air-unit crash/support vfunc review" for row in ledger_rows), "missing Wave1006 ledger row", failures)
    require(any(row.get("task") == "Wave1006 air-unit crash/support vfunc review" and row.get("attempt_id") == 20588 for row in attempts), "missing Wave1006 attempt row", failures)

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
        print("Wave1006 air-unit crash/support vfunc review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1006 air-unit crash/support vfunc review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
