#!/usr/bin/env python3
"""Validate Wave942 destructable-segments motion review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave942-destructable-segments-motion-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_destructable_segments_motion_review_wave942_2026-05-28.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
DESTRUCTABLE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DestructableSegmentsController.cpp" / "_index.md"
HIVEBOSS_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "HiveBoss.cpp" / "_index.md"
PACKAGE_JSON = ROOT / "package.json"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
STATE_FILES = [
    ROOT / "developer_agent_state.json",
    ROOT / "documentation_agent_state.json",
    ROOT / "re_orchestrator_state.json",
]

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260528-040608_post_wave942_destructable_segments_motion_review_verified"
SCRIPT_NAME = "test:ghidra-destructable-segments-motion-review-wave942"
SCRIPT_VALUE = r"py -3 tools\ghidra_destructable_segments_motion_review_wave942_probe.py --check"

TARGETS = {
    "0x00494c60": (
        "CDestructableSegmentsMotionController__Ctor",
        "void * __thiscall CDestructableSegmentsMotionController__Ctor(void * this, void * segment_controller)",
        ("Wave942 comment normalization", "owner_hiveboss+0x178", "0x005dc27c", "Static retail Ghidra evidence only"),
    ),
    "0x00494ca0": (
        "CDestructableSegmentsMotionController__ScalarDeletingDestructor",
        "void * __thiscall CDestructableSegmentsMotionController__ScalarDeletingDestructor(void * this, byte delete_flags)",
        ("Wave942 read-back", "0x005dc27c slot 1", "CDestructableSegmentsMotionController__Destructor", "flags bit 0"),
    ),
    "0x00494cc0": (
        "CDestructableSegmentsMotionController__Destructor",
        "void __fastcall CDestructableSegmentsMotionController__Destructor(void * this)",
        ("Wave942 comment normalization", "0x005dc27c", "one-instruction JMP thunk", "Static retail Ghidra evidence only"),
    ),
    "0x00494ce0": (
        "CDestructableSegmentsMotionController__ApplyRumbleTransform",
        "void __thiscall CDestructableSegmentsMotionController__ApplyRumbleTransform(void * this, void * state_context, void * segment_state, void * transform)",
        ("Wave942 read-back", "RET 0x10", "CMCBuggy__GetTargetValueOrFallback", "CMCHiveBoss__VFunc_04_UpdateCylinderTransforms_004976d0"),
    ),
    "0x00497130": (
        "CDestructableSegmentsMotionController__DestructorThunk_00497130",
        "void __fastcall CDestructableSegmentsMotionController__DestructorThunk_00497130(void * this)",
        ("Wave942 read-back", "one-instruction JMP thunk", "0x00494cc0", "CMCHiveBoss__ScalarDeletingDestructor"),
    ),
    "0x00497140": (
        "CDestructableSegmentsMotionController__CacheNamedCollisionCylinders",
        "void __thiscall CDestructableSegmentsMotionController__CacheNamedCollisionCylinders(void * this, void * mesh_model)",
        ("Wave942 comment normalization", "RET 0x4", "+0x15c", "+0x160", "0x004976f1", "recovered CMCHiveBoss__VFunc_04_UpdateCylinderTransforms_004976d0 boundary"),
    ),
}

COMMON_TAGS = {
    "static-reaudit",
    "destructable-segments-motion-review-wave942",
    "wave942-readback-verified",
    "retail-binary-evidence",
    "comment-normalized",
    "comment-hardened",
    "destructable-segments",
    "motion-controller",
    "hiveboss-motion",
}

CONTEXT = {
    "0x00443fc0": "CDestructableSegmentsController__Ctor",
    "0x00444660": "CDestructableSegmentsController__Init",
    "0x00445010": "CMCBuggy__GetTargetValueOrFallback",
    "0x0047fe30": "CHiveBoss__Init",
    "0x00494c60": "CDestructableSegmentsMotionController__Ctor",
    "0x00494ce0": "CDestructableSegmentsMotionController__ApplyRumbleTransform",
    "0x00497090": "CMCHiveBoss__Constructor",
    "0x00497110": "CMCHiveBoss__ScalarDeletingDestructor",
    "0x004976d0": "CMCHiveBoss__VFunc_04_UpdateCylinderTransforms_004976d0",
}

EXPECTED_XREFS = {
    ("post-xrefs.tsv", "0x00494c60", "0x0049709f", "CMCHiveBoss__Constructor", "UNCONDITIONAL_CALL"),
    ("post-xrefs.tsv", "0x00494ca0", "0x005dc280", "<no_function>", "DATA"),
    ("post-xrefs.tsv", "0x00494cc0", "0x00494ca3", "CDestructableSegmentsMotionController__ScalarDeletingDestructor", "UNCONDITIONAL_CALL"),
    ("post-xrefs.tsv", "0x00494cc0", "0x00497130", "CDestructableSegmentsMotionController__DestructorThunk_00497130", "UNCONDITIONAL_JUMP"),
    ("post-xrefs.tsv", "0x00494ce0", "0x005dc28c", "<no_function>", "DATA"),
    ("post-xrefs.tsv", "0x00494ce0", "0x00497711", "CMCHiveBoss__VFunc_04_UpdateCylinderTransforms_004976d0", "UNCONDITIONAL_CALL"),
    ("post-xrefs.tsv", "0x00497130", "0x00497113", "CMCHiveBoss__ScalarDeletingDestructor", "UNCONDITIONAL_CALL"),
    ("post-xrefs.tsv", "0x00497140", "0x004976f1", "CMCHiveBoss__VFunc_04_UpdateCylinderTransforms_004976d0", "UNCONDITIONAL_CALL"),
}

EXPECTED_INSTRUCTIONS = {
    ("post-instructions.tsv", "0x00494c85", "RET", "0x4", "CDestructableSegmentsMotionController__Ctor"),
    ("post-instructions.tsv", "0x00494ca3", "CALL", "0x00494cc0", "CDestructableSegmentsMotionController__ScalarDeletingDestructor"),
    ("post-instructions.tsv", "0x00494cbd", "RET", "0x4", "CDestructableSegmentsMotionController__ScalarDeletingDestructor"),
    ("post-instructions.tsv", "0x00494cfa", "CALL", "0x00445010", "CDestructableSegmentsMotionController__ApplyRumbleTransform"),
    ("post-instructions.tsv", "0x00494f7c", "RET", "0x10", "CDestructableSegmentsMotionController__ApplyRumbleTransform"),
    ("post-instructions.tsv", "0x00497130", "JMP", "0x00494cc0", "CDestructableSegmentsMotionController__DestructorThunk_00497130"),
    ("post-instructions.tsv", "0x00497148", "MOV", "0x15c", "CDestructableSegmentsMotionController__CacheNamedCollisionCylinders"),
    ("post-instructions.tsv", "0x0049715d", "MOV", "0x160", "CDestructableSegmentsMotionController__CacheNamedCollisionCylinders"),
    ("post-instructions.tsv", "0x004976bb", "RET", "0x4", "CDestructableSegmentsMotionController__CacheNamedCollisionCylinders"),
    ("context-instructions.tsv", "0x0049709f", "CALL", "0x00494c60", "CMCHiveBoss__Constructor"),
    ("context-instructions.tsv", "0x00497113", "CALL", "0x00497130", "CMCHiveBoss__ScalarDeletingDestructor"),
    ("context-instructions.tsv", "0x004976f1", "CALL", "0x00497140", "CMCHiveBoss__VFunc_04_UpdateCylinderTransforms_004976d0"),
    ("context-instructions.tsv", "0x00497711", "CALL", "0x00494ce0", "CMCHiveBoss__VFunc_04_UpdateCylinderTransforms_004976d0"),
}

EXPECTED_VTABLE_SLOTS = {
    ("005dc27c", "1", "00494ca0", "CDestructableSegmentsMotionController__ScalarDeletingDestructor"),
    ("005dc27c", "4", "00494ce0", "CDestructableSegmentsMotionController__ApplyRumbleTransform"),
    ("005dc27c", "8", "00495020", "CMCBuggy__VFunc_GetUnitAIEntryTableRoot"),
    ("005dc388", "1", "00497110", "CMCHiveBoss__ScalarDeletingDestructor"),
    ("005dc388", "4", "004976d0", "CMCHiveBoss__VFunc_04_UpdateCylinderTransforms_004976d0"),
    ("005dc388", "11", "00498870", "CMCMech__VFunc_00_OnTimedResetEvent_00498870"),
}

DECOMPILE_TOKENS = {
    "post-decompile/00494c60_CDestructableSegmentsMotionController__Ctor.c": ("0x005dc27c", "owner_hiveboss+0x178"),
    "post-decompile/00494ce0_CDestructableSegmentsMotionController__ApplyRumbleTransform.c": ("CMCBuggy__GetTargetValueOrFallback", "CMCHiveBoss__VFunc_04_UpdateCylinderTransforms_004976d0"),
    "post-decompile/00497130_CDestructableSegmentsMotionController__DestructorThunk_00497130.c": ("0x005dc27c", "CDestructableSegmentsMotionController__DestructorThunk_00497130"),
    "post-decompile/00497140_CDestructableSegmentsMotionController__CacheNamedCollisionCylinders.c": ("0x15c", "0x160", "CMCHiveBoss__VFunc_04_UpdateCylinderTransforms_004976d0"),
    "context-decompile/00497090_CMCHiveBoss__Constructor.c": ("owner_hiveboss", "0x005dc388"),
    "context-decompile/004976d0_CMCHiveBoss__VFunc_04_UpdateCylinderTransforms_004976d0.c": ("CDestructableSegmentsMotionController__CacheNamedCollisionCylinders", "CDestructableSegmentsMotionController__ApplyRumbleTransform"),
}

CORE_TOKENS = (
    "Wave942",
    "destructable-segments-motion-review-wave942",
    "comment-only mutation",
    "180/1408 = 12.78%",
    "6113/6113 = 100.00%",
    BACKUP,
    "0x00494c60 CDestructableSegmentsMotionController__Ctor",
    "0x00494ca0 CDestructableSegmentsMotionController__ScalarDeletingDestructor",
    "0x00494cc0 CDestructableSegmentsMotionController__Destructor",
    "0x00494ce0 CDestructableSegmentsMotionController__ApplyRumbleTransform",
    "0x00497130 CDestructableSegmentsMotionController__DestructorThunk_00497130",
    "0x00497140 CDestructableSegmentsMotionController__CacheNamedCollisionCylinders",
    "0x00497090 CMCHiveBoss__Constructor",
    "0x00497110 CMCHiveBoss__ScalarDeletingDestructor",
    "0x004976d0 CMCHiveBoss__VFunc_04_UpdateCylinderTransforms_004976d0",
    "0x004976f1",
    "0x005dc27c",
    "0x005dc388",
)

OVERCLAIMS = (
    "runtime rumble behavior proven",
    "runtime cylinder behavior proven",
    "runtime hiveboss motion behavior proven",
    "rebuild parity proven",
)


def normalize_address(value: str) -> str:
    text = (value or "").strip().lower()
    if text.startswith("0x"):
        text = text[2:]
    return "0x" + text.zfill(8)


def normalize_raw_address(value: str) -> str:
    return normalize_address(value)[2:]


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8-sig", errors="replace")


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in read_text(path).splitlines() if line.strip()]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def row_map(path: Path, key: str = "address") -> dict[str, dict[str, str]]:
    return {normalize_address(row[key]): row for row in read_tsv(path)}


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def has_xref(expected: tuple[str, str, str, str, str]) -> bool:
    rel, target, from_addr, from_function, ref_type = expected
    for row in read_tsv(BASE / rel):
        if (
            normalize_address(row.get("target_addr", "")) == normalize_address(target)
            and normalize_address(row.get("from_addr", "")) == normalize_address(from_addr)
            and row.get("from_function") == from_function
            and row.get("ref_type") == ref_type
        ):
            return True
    return False


def has_instruction(expected: tuple[str, str, str, str, str]) -> bool:
    rel, address, mnemonic, operand_token, function_name = expected
    for row in read_tsv(BASE / rel):
        if (
            normalize_address(row.get("instruction_addr", "")) == normalize_address(address)
            and row.get("mnemonic") == mnemonic
            and operand_token in row.get("operands", "")
            and row.get("function_name") == function_name
        ):
            return True
    return False


def has_vtable_slot(expected: tuple[str, str, str, str]) -> bool:
    vtable, slot, pointer, function_name = expected
    for row in read_tsv(BASE / "post-vtable-slots.tsv"):
        if (
            normalize_raw_address(row.get("vtable", "")) == normalize_raw_address(vtable)
            and row.get("slot_index") == slot
            and normalize_raw_address(row.get("pointer_addr", "")) == normalize_raw_address(pointer)
            and row.get("function_name") == function_name
            and row.get("status") == "OK"
        ):
            return True
    return False


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "metadata.tsv": 6,
        "tags.tsv": 6,
        "xrefs.tsv": 8,
        "instructions.tsv": 826,
        "decompile/index.tsv": 6,
        "context-metadata.tsv": 9,
        "context-tags.tsv": 9,
        "context-xrefs.tsv": 10,
        "context-instructions.tsv": 1371,
        "context-decompile/index.tsv": 9,
        "vtable-slots.tsv": 24,
        "post-metadata.tsv": 6,
        "post-tags.tsv": 6,
        "post-xrefs.tsv": 8,
        "post-instructions.tsv": 826,
        "post-decompile/index.tsv": 6,
        "post-vtable-slots.tsv": 24,
    }
    for rel, count in expected_counts.items():
        require(len(read_tsv(BASE / rel)) == count, f"{rel} row count mismatch", failures)

    metadata = row_map(BASE / "post-metadata.tsv")
    tags = row_map(BASE / "post-tags.tsv")
    decomp = row_map(BASE / "post-decompile" / "index.tsv")
    for address, (name, signature, comment_tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing post metadata {address}", failures)
        if row:
            comment = row.get("comment", "")
            require(row.get("name") == name, f"name mismatch {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
            for token in comment_tokens:
                require(token in comment, f"missing comment token {address}: {token}", failures)
            for bad in ("currently missing-boundary", "CMCHiveBoss__VFunc_01_00497110", "ctor_like_00497090"):
                require(bad not in comment, f"stale comment token {address}: {bad}", failures)
        tag_row = tags.get(address)
        require(tag_row is not None, f"missing post tags {address}", failures)
        if tag_row:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"missing Wave942 tags {address}: {COMMON_TAGS - actual_tags}", failures)
        dec = decomp.get(address)
        require(
            dec is not None and dec.get("signature") == signature and dec.get("status") == "OK",
            f"decompile mismatch {address}",
            failures,
        )

    context_meta = row_map(BASE / "context-metadata.tsv")
    for address, name in CONTEXT.items():
        row = context_meta.get(address)
        require(row is not None and row.get("name") == name and row.get("status") == "OK", f"context metadata mismatch {address}", failures)

    for expected in EXPECTED_XREFS:
        require(has_xref(expected), f"missing xref {expected}", failures)
    for expected in EXPECTED_INSTRUCTIONS:
        require(has_instruction(expected), f"missing instruction {expected}", failures)
    for expected in EXPECTED_VTABLE_SLOTS:
        require(has_vtable_slot(expected), f"missing vtable slot {expected}", failures)
    for rel, tokens in DECOMPILE_TOKENS.items():
        text = read_text(BASE / rel)
        for token in tokens:
            require(token in text, f"missing decompile token {rel}: {token}", failures)


def check_logs_queue_and_backup(failures: list[str]) -> None:
    expected_logs = {
        "metadata.log": "targets=6 found=6 missing=0",
        "tags.log": "ExportFunctionTagsByAddress complete: rows=6 missing=0",
        "xrefs.log": "Wrote 8 rows",
        "instructions.log": "Wrote 826 function-body instruction rows",
        "decompile.log": "targets=6 dumped=6 missing=0 failed=0",
        "context-metadata.log": "targets=9 found=9 missing=0",
        "context-tags.log": "ExportFunctionTagsByAddress complete: rows=9 missing=0",
        "context-xrefs.log": "Wrote 10 rows",
        "context-instructions.log": "Wrote 1371 function-body instruction rows",
        "context-decompile.log": "targets=9 dumped=9 missing=0 failed=0",
        "vtable-slots.log": "ExportVtableSlots complete: targets=2 rows=24",
        "apply-dry.log": "SUMMARY updated=0 would_update=6 skipped=0 missing=0 bad=0",
        "apply.log": "SUMMARY updated=6 would_update=0 skipped=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY updated=0 would_update=0 skipped=6 missing=0 bad=0",
        "post-metadata.log": "targets=6 found=6 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=6 missing=0",
        "post-xrefs.log": "Wrote 8 rows",
        "post-instructions.log": "Wrote 826 function-body instruction rows",
        "post-decompile.log": "targets=6 dumped=6 missing=0 failed=0",
        "post-vtable-slots.log": "ExportVtableSlots complete: targets=2 rows=24",
    }
    for rel, token in expected_logs.items():
        text = read_text(BASE / rel)
        require(token in text, f"missing log token {rel}: {token}", failures)
        require("REPORT: Save succeeded" in text, f"missing save marker {rel}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIGNATURE:", "FAIL:", "failed=1", "missing=1", "bad=1"):
            require(bad not in text, f"unexpected log failure {rel}: {bad}", failures)

    quality_log = read_text(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave942.log")
    require("total_functions=6113 commented_functions=6113" in quality_log, "missing Wave942 quality refresh token", failures)
    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    require(queue.get("totalFunctions") == 6113, "queue total mismatch", failures)
    require(quality.get("commentlessFunctionCount") == 0, "queue commentless mismatch", failures)
    require(quality.get("undefinedSignatureCount") == 0, "queue undefined mismatch", failures)
    require(quality.get("paramSignatureCount") == 0, "queue param_N mismatch", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes", 0)) == 173280135, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    package = read_json(PACKAGE_JSON)
    require(package.get("scripts", {}).get(SCRIPT_NAME) == SCRIPT_VALUE, "missing package script", failures)

    docs = [NOTE, CAMPAIGN, GHIDRA_REFERENCE, DESTRUCTABLE_DOC, HIVEBOSS_DOC, BACKLOG, *STATE_FILES]
    for path in docs:
        text = read_text(path)
        for token in CORE_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    reference = read_text(GHIDRA_REFERENCE)
    require("currently missing-boundary callsite at `0x004976f1`" not in reference, "stale missing-boundary wording remains", failures)
    require("CMCHiveBoss__VFunc_01_00497110` at `0x00497113`" not in reference, "stale CMCHiveBoss vfunc-01 wording remains", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempt_rows = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave942 destructable segments motion review" for row in ledger_rows), "missing Wave942 ledger row", failures)
    require(
        any(row.get("task") == "Wave942 destructable segments motion review" and row.get("attempt_id") == 20557 for row in attempt_rows),
        "missing Wave942 attempt row",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_queue_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave942 destructable-segments motion review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave942 destructable-segments motion review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
