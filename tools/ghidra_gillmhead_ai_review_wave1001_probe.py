#!/usr/bin/env python3
"""Validate Wave1001 GillMHeadAI review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1001-gillmhead-ai-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_gillmhead_ai_review_wave1001_2026-05-31.md"
RECHECK_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1001_recheck_2026-05-31.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
GILLMHEAD_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "GillMHead.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
RECHECK_TOOL = ROOT / "tools" / "ghidra_wave900_plus_through_wave983_recheck.py"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260531-104623_post_wave1001_gillmhead_ai_review_verified"

TARGETS = {
    "0x0047a760": ("CGillMHead__CreateGillMHeadAIComponent", "void __thiscall CGillMHead__CreateGillMHeadAIComponent(void * this, void * init_data)"),
    "0x0047a7f0": ("CGillMHeadAI__ScalarDeletingDestructor", "void * __thiscall CGillMHeadAI__ScalarDeletingDestructor(void * this, byte flags)"),
    "0x0047a810": ("CGillMHeadAI__Destructor", "void __fastcall CGillMHeadAI__Destructor(void * this)"),
    "0x0047a8b0": ("CGillMHeadAI__TryTransitionIdleToOpen", "int __fastcall CGillMHeadAI__TryTransitionIdleToOpen(void * this)"),
    "0x0047a900": ("CGillMHeadAI__AdvanceOpenAttackCloseState", "int __fastcall CGillMHeadAI__AdvanceOpenAttackCloseState(void * this)"),
    "0x0047afc0": ("CGillMHeadAI__UpdateAimTransformAndTargetReader", "void __fastcall CGillMHeadAI__UpdateAimTransformAndTargetReader(void * this)"),
    "0x0047b090": ("CGillMHeadAI__UpdateTargetBallisticArcFlags", "void __fastcall CGillMHeadAI__UpdateTargetBallisticArcFlags(void * this)"),
}

COMMENT_TOKENS = {
    "0x0047a760": ("0x64-byte type-0x16", "CGillMHeadAI RTTI vtable 0x005dbcec", "this+0x13c"),
    "0x0047a7f0": ("CGillMHeadAI vtable 0x005dbcec slot 1", "CGillMHeadAI__Destructor", "flags bit 0"),
    "0x0047a810": ("CUnitAI base vtable 0x005d8d1c", "+0x28", "CMonitor__Shutdown"),
    "0x0047a8b0": ("pointer table 0x005e42d8 slot 30", "idle", "open"),
    "0x0047a900": ("Wave1001 GillMHeadAI review", "CUnit__HasAnyLinkedUnitBeforeTargetTimeout", "SharedUnitAnimation__PlayAnimationByNameIfPresent"),
    "0x0047afc0": ("Wave1001 GillMHeadAI review", "CUnit__ForwardAimTransformAndAttachTargetReader", "stale Wave390 wording"),
    "0x0047b090": ("CGillMHeadAI vtable 0x005dbcec slot 4", "CUnit__CanFireAtTarget_BallisticArcB/A", "stale target reader"),
}

DOC_TOKENS = (
    "Wave1001",
    "gillmhead-ai-review-wave1001",
    "0x0047a760 CGillMHead__CreateGillMHeadAIComponent",
    "0x0047a900 CGillMHeadAI__AdvanceOpenAttackCloseState",
    "CUnit__HasAnyLinkedUnitBeforeTargetTimeout",
    "0x0047afc0 CGillMHeadAI__UpdateAimTransformAndTargetReader",
    "CUnit__ForwardAimTransformAndAttachTargetReader",
    "472/1408 = 33.52%",
    "613/1478 = 41.47%",
    "355/500 = 71.00%",
    "6222/6222 = 100.00%",
    BACKUP_PATH,
)

OVERCLAIMS = (
    "runtime gillmhead animation behavior proven",
    "runtime gillmhead targeting behavior proven",
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
    return token.replace("\\\\", "\\") in text.replace("\\\\\\\\", "\\").replace("\\\\", "\\")


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 7,
        "post-metadata.tsv": 7,
        "pre-tags.tsv": 7,
        "post-tags.tsv": 7,
        "pre-xrefs.tsv": 7,
        "post-xrefs.tsv": 7,
        "pre-instructions.tsv": 320,
        "post-instructions.tsv": 320,
        "pre-decompile/index.tsv": 7,
        "post-decompile/index.tsv": 7,
        "pre-vtable-slots.tsv": 16,
        "post-vtable-slots.tsv": 16,
        "pre-vtable-types.tsv": 2,
        "post-vtable-types.tsv": 2,
        "pre-pointer-table-005e42d8.tsv": 64,
        "post-pointer-table-005e42d8.tsv": 64,
    }
    for relative, expected in expected_counts.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == expected, f"{relative} row count {actual} != {expected}", failures)

    metadata = read_tsv(BASE / "post-metadata.tsv")
    tags = read_tsv(BASE / "post-tags.tsv")
    decompile_index = read_tsv(BASE / "post-decompile" / "index.tsv")

    for address, (name, signature) in TARGETS.items():
        row = row_by_address(metadata, address)
        require(row is not None, f"metadata missing {address}", failures)
        if row:
            require(row.get("name") == name, f"metadata name mismatch {address}", failures)
            require(row.get("signature") == signature, f"metadata signature mismatch {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
            for token in COMMENT_TOKENS[address]:
                require(token in row.get("comment", ""), f"comment token missing {address}: {token}", failures)

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
            for tag in ("static-reaudit", "retail-binary-evidence", "gillmhead-ai-wave390"):
                require(tag in actual_tags, f"missing tag {address}: {tag}", failures)
            if address in ("0x0047a900", "0x0047afc0"):
                for tag in ("gillmhead-ai-review-wave1001", "wave1001-readback-verified", "comment-corrected"):
                    require(tag in actual_tags, f"missing Wave1001 tag {address}: {tag}", failures)

    xrefs = read_tsv(BASE / "post-xrefs.tsv")
    expected_xrefs = (
        ("0x0047a760", "0x005e43d4", "DATA"),
        ("0x0047a7f0", "0x005dbcf0", "DATA"),
        ("0x0047a810", "0x0047a7f3", "UNCONDITIONAL_CALL"),
        ("0x0047a8b0", "0x005e4350", "DATA"),
        ("0x0047a900", "0x005e42e4", "DATA"),
        ("0x0047afc0", "0x005dbcf8", "DATA"),
        ("0x0047b090", "0x005dbcfc", "DATA"),
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

    vtable_slots = read_tsv(BASE / "post-vtable-slots.tsv")
    for slot, slot_addr, pointer, name in (
        ("1", "0x005dbcf0", "0x0047a7f0", "CGillMHeadAI__ScalarDeletingDestructor"),
        ("3", "0x005dbcf8", "0x0047afc0", "CGillMHeadAI__UpdateAimTransformAndTargetReader"),
        ("4", "0x005dbcfc", "0x0047b090", "CGillMHeadAI__UpdateTargetBallisticArcFlags"),
    ):
        require(
            any(
                row.get("vtable") == "005dbcec"
                and row.get("slot_index") == slot
                and normalize_address(row.get("slot_addr", "")) == slot_addr
                and normalize_address(row.get("pointer_addr", "")) == pointer
                and row.get("function_name") == name
                and row.get("status") == "OK"
                for row in vtable_slots
            ),
            f"missing CGillMHeadAI vtable slot {slot} -> {name}",
            failures,
        )

    pointer_table = read_tsv(BASE / "post-pointer-table-005e42d8.tsv")
    for slot, pointer, name in (
        ("3", "0x0047a900", "CGillMHeadAI__AdvanceOpenAttackCloseState"),
        ("30", "0x0047a8b0", "CGillMHeadAI__TryTransitionIdleToOpen"),
        ("63", "0x0047a760", "CGillMHead__CreateGillMHeadAIComponent"),
    ):
        require(
            any(
                row.get("slot") == slot
                and normalize_address(row.get("ptr", "")) == pointer
                and row.get("ptr_name") == name
                for row in pointer_table
            ),
            f"missing pointer-table slot {slot} -> {name}",
            failures,
        )


def check_logs_and_backup(failures: list[str]) -> None:
    expected_log_tokens = {
        "apply-dry.log": ("SUMMARY: updated=0 skipped=2 comment_only_updated=2 tags_added=8 missing=0 bad=0", "REPORT: Save succeeded"),
        "apply.log": ("SUMMARY: updated=2 skipped=0 comment_only_updated=2 tags_added=8 missing=0 bad=0", "REPORT: Save succeeded"),
        "apply-final-dry.log": ("SUMMARY: updated=0 skipped=2 comment_only_updated=0 tags_added=0 missing=0 bad=0", "REPORT: Save succeeded"),
        "post-metadata.log": ("targets=7 found=7 missing=0", "REPORT: Save succeeded"),
        "post-tags.log": ("ExportFunctionTagsByAddress complete: rows=7 missing=0", "REPORT: Save succeeded"),
        "post-xrefs.log": ("Wrote 7 rows", "REPORT: Save succeeded"),
        "post-instructions.log": ("Wrote 320 function-body instruction rows", "targets=7 missing=0", "REPORT: Save succeeded"),
        "post-decompile.log": ("targets=7 dumped=7 missing=0 failed=0", "REPORT: Save succeeded"),
        "post-vtable-slots.log": ("ExportVtableSlots complete: targets=2 rows=16", "REPORT: Save succeeded"),
        "post-vtable-types.log": ("ResolveVtableTypeNames complete: rows=2", "REPORT: Save succeeded"),
        "post-pointer-table-005e42d8.log": ("DumpPointerTable complete: rows=64", "REPORT: Save succeeded"),
    }
    for relative, tokens in expected_log_tokens.items():
        text = read_text(BASE / relative)
        for token in tokens:
            require(token in text, f"missing log token {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR", "MISSING:", "BADNAME:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"bad log token {relative}: {bad}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 173869959 or backup.get("totalBytes") == 173869959.0, "backup bytes mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = (
        NOTE,
        RECHECK_NOTE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        GILLMHEAD_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
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
        scripts.get("test:ghidra-gillmhead-ai-review-wave1001")
        == r"py -3 tools\ghidra_gillmhead_ai_review_wave1001_probe.py --check",
        "missing Wave1001 package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1001-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1001 --check",
        "missing Wave1001 recheck package script",
        failures,
    )

    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    require(queue.get("totalFunctions") == 6222, "queue total mismatch", failures)
    require(quality.get("commentlessFunctionCount") == 0, "queue commentless mismatch", failures)
    require(quality.get("undefinedSignatureCount") == 0, "queue undefined mismatch", failures)
    require(quality.get("paramSignatureCount") == 0, "queue param mismatch", failures)

    recheck_text = read_text(RECHECK_TOOL)
    require('glob("Apply*Wave*.java")' in recheck_text, "Wave900+ recheck does not scan Wave1000+ apply scripts", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1001 GillMHeadAI review" for row in ledger_rows), "missing Wave1001 ledger row", failures)
    require(any(row.get("task") == "Wave1001 GillMHeadAI review" and row.get("attempt_id") == 20583 for row in attempts), "missing Wave1001 attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave1001 GillMHeadAI review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1001 GillMHeadAI review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
