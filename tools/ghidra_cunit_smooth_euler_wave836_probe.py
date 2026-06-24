#!/usr/bin/env python3
"""Validate Wave836 CUnit Smooth Euler read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave836-cunit-smooth-euler"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cunit_smooth_euler_wave836_2026-05-25.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
UNIT_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Unit.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260525-010821_post_wave836_cunit_smooth_euler_verified"
TARGET_ADDR = "0x004fa4b0"
TARGET_NAME = "CUnit__SmoothEulerTowardTargetAndBuildMatrix"
TARGET_SIGNATURE = (
    "void __thiscall CUnit__SmoothEulerTowardTargetAndBuildMatrix("
    "void * this, float * current_euler_xyz, float * target_euler_xyz, "
    "float * max_step_xyz, float * out_matrix3x4)"
)
NEXT_HEAD = "0x004fc3a0 CSpawnerThng__SetCooldownState3"
ATTEMPT_ID = 20491

DATA_SLOTS = {
    "0x005d8af8", "0x005d8fe8", "0x005dd8bc", "0x005dfacc", "0x005dfe70",
    "0x005e00c0", "0x005e0310", "0x005e0564", "0x005e07b8", "0x005e0a14",
    "0x005e0c64", "0x005e0ec0", "0x005e1114", "0x005e1370", "0x005e15c4",
    "0x005e1814", "0x005e1a64", "0x005e1cb8", "0x005e1f0c", "0x005e216c",
    "0x005e23c0", "0x005e2610", "0x005e2860", "0x005e2ab0", "0x005e2d00",
    "0x005e2f54", "0x005e31a8", "0x005e3408", "0x005e3658", "0x005e38ac",
}
CALLSITE = "0x00428c21"

COMMON_TAGS = {
    "static-reaudit",
    "cunit-smooth-euler-wave836",
    "wave836-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "cunit",
    "unit-motion",
    "orientation-matrix",
    "matrix-build",
    "euler-smoothing",
    "angle-wrap",
    "vtable-slot",
    "shared-vtable-target",
    "cunitai-callsite",
}

COMMENT_TOKENS = (
    "Wave836 static read-back",
    "important shared CUnit motion/orientation infrastructure",
    "lower direct source-body evidence density",
    "not low-importance code",
    "RET 0x10 at 0x004fa7fc",
    "0x00428c15-0x00428c21",
    "current_euler_xyz",
    "target_euler_xyz",
    "max_step_xyz",
    "out_matrix3x4",
    "Thirty DATA slots",
    "vfunc +0x60",
    "frame-scale/time scalar",
    "0x005d85c0",
    "0x005d85dc",
    "0x005d85e0",
    "0x005d85e4",
    "0x005d85e8",
    "+/- pi-like boundary",
    "copies twelve floats",
)

DECOMPILE_TOKENS = (
    TARGET_SIGNATURE,
    "current_euler_xyz",
    "target_euler_xyz",
    "max_step_xyz",
    "out_matrix3x4",
    "fcos",
    "fsin",
    "_DAT_005d85c0",
    "_DAT_005d85dc",
    "_DAT_005d85e0",
    "_DAT_005d85e4",
    "_DAT_005d85e8",
    "for (iVar5 = 0xc; iVar5 != 0;",
)

CORE_ANCHORS = (
    "Wave836 CUnit Smooth Euler",
    "cunit-smooth-euler-wave836",
    TARGET_ADDR + " " + TARGET_NAME,
    TARGET_SIGNATURE,
    "important shared CUnit motion/orientation infrastructure",
    "lower direct source-body evidence density",
    "not low-importance code",
    "RET 0x10",
    "0x004fa7fc",
    "0x00428c15-0x00428c21",
    "30 DATA",
    "vfunc +0x60",
    "0x005d85c0",
    "5658/6098 = 92.78%",
    NEXT_HEAD,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "fully reverse-engineered",
    "runtime motion behavior proven",
    "runtime orientation behavior proven",
    "matrix convention proven",
    "rebuild parity proven",
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
        "pre-metadata.tsv": 1,
        "pre-tags.tsv": 1,
        "pre-xrefs.tsv": 31,
        "pre-instructions.tsv": 141,
        "pre-target-deep-instructions.tsv": 361,
        "pre-xref-site-instructions.tsv": 55,
        "pre-decompile/index.tsv": 1,
        "pre-context-metadata.tsv": 7,
        "pre-context-decompile/index.tsv": 7,
        "post-metadata.tsv": 1,
        "post-tags.tsv": 1,
        "post-xrefs.tsv": 31,
        "post-instructions.tsv": 141,
        "post-target-deep-instructions.tsv": 361,
        "post-xref-site-instructions.tsv": 55,
        "post-decompile/index.tsv": 1,
        "post-context-metadata.tsv": 7,
        "post-context-decompile/index.tsv": 7,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    row = metadata.get(TARGET_ADDR)
    require(row is not None, "missing post metadata row", failures)
    if row is not None:
        require(row.get("name") == TARGET_NAME, "target name mismatch", failures)
        require(row.get("signature") == TARGET_SIGNATURE, f"target signature mismatch: {row.get('signature')}", failures)
        require(row.get("status") == "OK", "metadata status mismatch", failures)
        comment = row.get("comment", "")
        for token in COMMENT_TOKENS:
            require(token in comment, f"missing comment token: {token}", failures)
        require("low-signal" not in comment.lower(), "comment contains low-signal wording", failures)

    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    tag_row = tags.get(TARGET_ADDR)
    require(tag_row is not None, "missing post tags row", failures)
    if tag_row is not None:
        actual = set(tag_row.get("tags", "").split(";"))
        require(COMMON_TAGS.issubset(actual), f"missing tags: {COMMON_TAGS - actual}", failures)
        require(tag_row.get("status") == "OK", "tag status mismatch", failures)

    xrefs = read_tsv(BASE / "post-xrefs.tsv")
    actual_slots = {normalize_address(row["from_addr"]) for row in xrefs if row.get("ref_type") == "DATA"}
    actual_calls = {normalize_address(row["from_addr"]) for row in xrefs if row.get("ref_type") == "UNCONDITIONAL_CALL"}
    require(DATA_SLOTS == actual_slots, "DATA slot xref set mismatch", failures)
    require(actual_calls == {CALLSITE}, "callsite xref set mismatch", failures)

    deep = read_tsv(BASE / "post-target-deep-instructions.tsv")
    require(
        any(
            normalize_address(row.get("instruction_addr", "")) == "0x004fa7fc"
            and row.get("mnemonic") == "RET"
            and row.get("operands") == "0x10"
            for row in deep
        ),
        "missing RET 0x10 instruction evidence",
        failures,
    )

    call_rows = read_tsv(BASE / "post-xref-site-instructions.tsv")
    require(
        any(
            row.get("role") == "TARGET"
            and normalize_address(row.get("instruction_addr", "")) == CALLSITE
            and row.get("mnemonic") == "CALL"
            and row.get("operands") == TARGET_ADDR
            for row in call_rows
        ),
        "missing target call row",
        failures,
    )
    for addr, mnemonic, operands in (
        ("0x00428c19", "PUSH", "EAX"),
        ("0x00428c1e", "PUSH", "EAX"),
        ("0x00428c1f", "PUSH", "ESI"),
        ("0x00428c20", "PUSH", "EDX"),
        ("0x00428c27", "RET", "0x10"),
    ):
        require(
            any(
                normalize_address(row.get("instruction_addr", "")) == addr
                and row.get("mnemonic") == mnemonic
                and row.get("operands") == operands
                for row in call_rows
            ),
            f"missing caller-stub instruction {addr} {mnemonic} {operands}",
            failures,
        )

    decompile = read_text(BASE / "post-decompile" / "004fa4b0_CUnit__SmoothEulerTowardTargetAndBuildMatrix.c")
    for token in DECOMPILE_TOKENS:
        require(token in decompile, f"missing decompile token: {token}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=1 skipped=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=1 found=1 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=1 missing=0",
        "post-xrefs.log": "Wrote 31 rows",
        "post-instructions.log": "Wrote 141 instruction rows",
        "post-target-deep-instructions.log": "Wrote 361 instruction rows",
        "post-xref-site-instructions.log": "Wrote 55 instruction rows",
        "post-decompile.log": "targets=1 dumped=1 missing=0 failed=0",
        "post-context-metadata.log": "targets=7 found=7 missing=0",
        "post-context-decompile.log": "targets=7 dumped=7 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6098 commented_functions=5658",
        "queue-probe.log": "Commentless functions: 440",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave836.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave836_queue_probe.log",
    }
    for relative, token in expected.items():
        path = log_aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BAD: readback", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 440, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(queue["priorityQueues"]["commentlessHighSignal"] == [], "high-signal queue should be empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5658, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5658, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and normalize_address(raw_commentless.get("address", "")) == "0x004fc3a0", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CSpawnerThng__SetCooldownState3", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 171838343, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = [
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        UNIT_INDEX,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in CORE_ANCHORS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)
        if path in (PUBLIC_NOTE, UNIT_INDEX, DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE):
            require("low-signal" not in text.lower(), f"low-signal wording in {path.relative_to(ROOT)}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(scripts.get("test:ghidra-cunit-smooth-euler-wave836") == r"py -3 tools\ghidra_cunit_smooth_euler_wave836_probe.py --check", "missing package script", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave836 CUnit Smooth Euler" for row in ledger_rows), "missing Wave836 ledger row", failures)
    require(any(row.get("task") == "Wave836 CUnit Smooth Euler" and row.get("attempt_id") == ATTEMPT_ID for row in attempts), "missing Wave836 attempt row", failures)


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
        print("Wave836 CUnit Smooth Euler probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave836 CUnit Smooth Euler probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
