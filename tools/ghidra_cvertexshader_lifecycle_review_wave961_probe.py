#!/usr/bin/env python3
"""Validate Wave961 CVertexShader lifecycle boundary recovery artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave961-cvertexshader-lifecycle-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_cvertexshader_lifecycle_review_wave961_2026-05-28.md"
PACKAGE_JSON = ROOT / "package.json"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
VERTEXSHADER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "VertexShader.cpp" / "_index.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUALITY_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260528-125650_post_wave961_cvertexshader_lifecycle_review_verified"
TARGET = "0x00501a10"
TARGET_NAME = "CVertexShader__VFunc_02_00501a10"
TARGET_SIGNATURE = "int __thiscall CVertexShader__VFunc_02_00501a10(void * this)"

CORE_TOKENS = (
    "Wave961",
    "cvertexshader-lifecycle-review-wave961",
    "0x00501890 CVertexShader__scalar_deleting_dtor",
    "0x00501a10 CVertexShader__VFunc_02_00501a10",
    "0x005dfbc4 slot 2",
    "NO_FUNCTION_AT_POINTER",
    "CEngine__DeviceCall16C_CreateVertexShaderLike",
    "CVertexShader__LoadCompiledShaderBlobFromVSOFile",
    "0x80004005",
    "0xfffe0101",
    "DAT_00854e6c",
    "DAT_00888c8c",
    "306/1408 = 21.73%",
    "6152/6152 = 100.00%",
    BACKUP_PATH,
    "function-boundary recovery",
)

OVERCLAIMS = (
    "runtime shader behavior proven",
    "runtime shader compile/load/bind behavior proven",
    "driver behavior proven",
    "layout proven",
    "source method identity proven",
    "rebuild parity proven",
    "patching proven",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def norm(address: str) -> str:
    value = (address or "").strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    if value in {"", "<none>", "none"}:
        return value
    return "0x" + value.zfill(8)


def contains_token(text: str, token: str) -> bool:
    stripped = text.replace("`", "")
    return token in text or token in stripped or token.replace("\\", "\\\\") in text or token.replace("\\", "\\\\") in stripped


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def check_counts(failures: list[str]) -> None:
    expected = {
        "metadata.tsv": 27,
        "tags.tsv": 27,
        "xrefs.tsv": 106,
        "instructions.tsv": 2835,
        "body-instructions.tsv": 3239,
        "decompile/index.tsv": 27,
        "vtable-slots.tsv": 12,
        "slot2-instructions.tsv": 122,
        "post-metadata.tsv": 28,
        "post-tags.tsv": 28,
        "post-xrefs.tsv": 107,
        "post-instructions.tsv": 2940,
        "post-body-instructions.tsv": 3355,
        "post-decompile/index.tsv": 28,
        "post-vtable-slots.tsv": 12,
    }
    for relative, count in expected.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == count, f"{relative} row count mismatch: {actual} != {count}", failures)


def check_boundary_recovery(failures: list[str]) -> None:
    pre_slots = read_tsv(BASE / "vtable-slots.tsv")
    post_slots = read_tsv(BASE / "post-vtable-slots.tsv")

    pre_slot2 = next((row for row in pre_slots if row.get("vtable") == "005dfbc4" and row.get("slot_index") == "2"), None)
    post_slot2 = next((row for row in post_slots if row.get("vtable") == "005dfbc4" and row.get("slot_index") == "2"), None)
    require(pre_slot2 is not None, "missing pre vtable slot 2", failures)
    if pre_slot2:
        require(norm(pre_slot2.get("pointer_addr", "")) == TARGET, "pre slot 2 pointer mismatch", failures)
        require(pre_slot2.get("status") == "NO_FUNCTION_AT_POINTER", "pre slot 2 was not missing boundary", failures)
    require(post_slot2 is not None, "missing post vtable slot 2", failures)
    if post_slot2:
        require(norm(post_slot2.get("pointer_addr", "")) == TARGET, "post slot 2 pointer mismatch", failures)
        require(norm(post_slot2.get("function_entry", "")) == TARGET, "post slot 2 function entry mismatch", failures)
        require(post_slot2.get("function_name") == TARGET_NAME, "post slot 2 name mismatch", failures)
        require(post_slot2.get("status") == "OK", "post slot 2 status mismatch", failures)

    metadata = {norm(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    row = metadata.get(TARGET)
    require(row is not None, "missing post metadata for 0x00501a10", failures)
    if row:
        require(row.get("name") == TARGET_NAME, "target name mismatch", failures)
        require(row.get("signature") == TARGET_SIGNATURE, f"target signature mismatch: {row.get('signature')}", failures)
        require(row.get("status") == "OK", "target metadata status mismatch", failures)
        for token in (
            "Wave961 CVertexShader vtable slot-2 boundary recovery",
            "compiled-blob creation through CEngine__DeviceCall16C_CreateVertexShaderLike",
            "named-file fallback through CVertexShader__LoadCompiledShaderBlobFromVSOFile",
            "E_ABORT-style 0x80004005",
            "not a source method identity claim",
        ):
            require(contains_token(row.get("comment", ""), token), f"missing target comment token: {token}", failures)

    tag_row = {norm(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}.get(TARGET)
    require(tag_row is not None, "missing target tags", failures)
    if tag_row:
        tags = set(tag_row.get("tags", "").split(";"))
        for tag in (
            "static-reaudit",
            "cvertexshader-lifecycle-review-wave961",
            "wave961-readback-verified",
            "function-boundary-recovered",
            "signature-hardened",
            "comment-hardened",
            "vtable-slot-2",
        ):
            require(tag in tags, f"missing target tag: {tag}", failures)

    decompile = {norm(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    require(decompile.get(TARGET, {}).get("signature") == TARGET_SIGNATURE, "target decompile signature mismatch", failures)
    require(decompile.get(TARGET, {}).get("status") == "OK", "target decompile status mismatch", failures)


def check_instruction_and_xref_evidence(failures: list[str]) -> None:
    body = read_tsv(BASE / "post-body-instructions.tsv")
    instruction_checks = (
        ("0x00501a10", "MOV", "0x00888c8c"),
        ("0x00501a38", "CMP", "0xfffe0101"),
        ("0x00501a4c", "MOV", "0x00854e6c"),
        ("0x00501a53", "CALL", "0x00513ca0"),
        ("0x00501a88", "CALL", "0x00513ff0"),
        ("0x00501aa3", "MOV", "0x80004005"),
        ("0x00501adb", "CALL", "0x00513ff0"),
        ("0x00501af2", "MOV", "0x80004005"),
        ("0x00501b23", "CALL", "0x005027f0"),
        ("0x00501b2e", "MOV", "0x80004005"),
        ("0x00501b4c", "CALL", "0x00513ca0"),
    )
    for instr_addr, mnemonic, operand in instruction_checks:
        hit = any(
            norm(row.get("target_addr", "")) == TARGET
            and norm(row.get("instruction_addr", "")) == instr_addr
            and row.get("mnemonic") == mnemonic
            and operand in row.get("operands", "")
            for row in body
        )
        require(hit, f"missing instruction evidence: {instr_addr} {mnemonic} {operand}", failures)

    xrefs = read_tsv(BASE / "post-xrefs.tsv")
    xref_checks = (
        (TARGET, "0x005dfbcc", "<no_function>", "DATA"),
        ("0x00513ff0", "0x00501a88", TARGET_NAME, "UNCONDITIONAL_CALL"),
        ("0x00513ff0", "0x00501adb", TARGET_NAME, "UNCONDITIONAL_CALL"),
        ("0x005027f0", "0x00501b23", TARGET_NAME, "UNCONDITIONAL_CALL"),
    )
    for target, source, from_function, ref_type in xref_checks:
        hit = any(
            norm(row.get("target_addr", "")) == target
            and norm(row.get("from_addr", "")) == source
            and row.get("from_function") == from_function
            and row.get("ref_type") == ref_type
            for row in xrefs
        )
        require(hit, f"missing xref evidence: {source} -> {target} {from_function} {ref_type}", failures)

    decompile_text = read_text(BASE / "post-decompile" / "00501a10_CVertexShader__VFunc_02_00501a10.c")
    for token in (
        "DAT_00888c8c",
        "DAT_00854e6c",
        "CEngine__DeviceCall16C_CreateVertexShaderLike",
        "CVertexShader__LoadCompiledShaderBlobFromVSOFile",
        "-0x7fffbffb",
        "return 0",
    ):
        require(token in decompile_text, f"missing decompile token: {token}", failures)


def check_logs_queue_backup(failures: list[str]) -> None:
    logs = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 created=0 would_create=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=1 skipped=0 created=1 would_create=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=1 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "comment-dry.log": "comment_only_updated=1",
        "comment-apply.log": "SUMMARY: updated=1 skipped=0 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=1 missing=0 bad=0",
        "comment-final-dry.log": "SUMMARY: updated=0 skipped=1 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=28 found=28 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=28 missing=0",
        "post-xrefs.log": "Wrote 107 rows",
        "post-instructions.log": "Wrote 2940 instruction rows",
        "post-body-instructions.log": "Wrote 3355 function-body instruction rows",
        "post-decompile.log": "targets=28 dumped=28 missing=0 failed=0",
        "post-vtable-slots.log": "ExportVtableSlots complete: targets=1 rows=12",
    }
    for relative, token in logs.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR", "Invalid script", "Usage:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    quality_log = read_text(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave961.log")
    queue_log = read_text(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave961_queue_probe.log")
    require("total_functions=6152 commented_functions=6152" in quality_log, "quality refresh log mismatch", failures)
    require("Status: PASS" in queue_log and "Total functions: 6152" in queue_log, "queue probe log mismatch", failures)

    queue = read_json(QUEUE_JSON)
    require(queue.get("totalFunctions") == 6152, "queue total mismatch", failures)
    quality = queue.get("qualitySignals", {})
    require(quality.get("commentlessFunctionCount") == 0, "commentless count mismatch", failures)
    require(quality.get("undefinedSignatureCount") == 0, "undefined count mismatch", failures)
    require(quality.get("paramSignatureCount") == 0, "param_N count mismatch", failures)

    quality_rows = {norm(row["address"]): row for row in read_tsv(QUALITY_TSV)}
    target = quality_rows.get(TARGET)
    require(target is not None, "missing target row in quality TSV", failures)
    if target:
        require(target.get("name") == TARGET_NAME, "quality TSV target name mismatch", failures)
        require(target.get("signature") == TARGET_SIGNATURE, "quality TSV target signature mismatch", failures)
        require("compiled-blob creation" in target.get("comment", ""), "quality TSV missing refined comment", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes", 0)) == 173542279, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs_and_state(failures: list[str]) -> None:
    docs = [NOTE, CAMPAIGN, GHIDRA_REFERENCE, FUNCTION_INDEX, VERTEXSHADER_DOC, DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE]
    for path in docs:
        text = read_text(path)
        for token in CORE_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:ghidra-cvertexshader-lifecycle-review-wave961")
        == r"py -3 tools\ghidra_cvertexshader_lifecycle_review_wave961_probe.py --check",
        "missing package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_counts(failures)
    check_boundary_recovery(failures)
    check_instruction_and_xref_evidence(failures)
    check_logs_queue_backup(failures)
    check_docs_and_state(failures)
    if failures:
        print("Wave961 CVertexShader lifecycle review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave961 CVertexShader lifecycle review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
