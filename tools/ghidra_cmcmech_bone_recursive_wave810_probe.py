#!/usr/bin/env python3
"""Validate Wave810 CMCMech bone-recursive read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave810-cmcmech-bone-recursive"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cmcmech_bone_recursive_wave810_2026-05-24.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
MECH_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Mech.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"

ADDRESS = "0x0049bd50"
NAME = "CMCMech__UpdateBoneHierarchyRecursive"
SIGNATURE = "void CMCMech__UpdateBoneHierarchyRecursive(void)"
BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260524-123030_post_wave810_cmcmech_bone_recursive_verified"
NEXT_HEAD = "0x0049c2d0 CMeshPart__HasAnimationToken_623074"

COMMON_TAGS = {
    "static-reaudit",
    "cmcmech-bone-recursive-wave810",
    "wave810-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "large-stack-argument-contract",
    "by-value-stack-payload",
    "recursive-bone-update",
    "raw-commentless-tail",
    "tranche-head",
}

DOC_TOKENS = (
    "Wave810 CMCMech bone recursive",
    "cmcmech-bone-recursive-wave810",
    "0x0049bd50 CMCMech__UpdateBoneHierarchyRecursive",
    "RET 0x54",
    "0x00498ac6",
    "0x00498bad",
    "0x0049bddf",
    "5585/6098 = 91.59%",
    NEXT_HEAD,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime leg/bone animation behavior proven",
    "fully reverse-engineered",
    "rebuild parity proven",
)


def normalize_address(value: str) -> str:
    text = value.strip().lower()
    if text.startswith("0x"):
        text = text[2:]
    return "0x" + text.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


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


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def signature_counts(rows: list[dict[str, str]]) -> tuple[int, int]:
    commented = sum(1 for row in rows if row.get("comment", "").strip())
    strict = sum(
        1
        for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not re.search(r"\bparam_\d+\b", row.get("signature", ""))
    )
    return commented, strict


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 1,
        "pre-tags.tsv": 1,
        "pre-xrefs.tsv": 3,
        "pre-instructions.tsv": 261,
        "pre-decompile/index.tsv": 1,
        "pre-context-metadata.tsv": 7,
        "pre-context-decompile/index.tsv": 7,
        "pre-caller-metadata.tsv": 3,
        "pre-caller-decompile/index.tsv": 3,
        "pre-callsite-instructions.tsv": 201,
        "pre-vtable.tsv": 12,
        "post-metadata.tsv": 1,
        "post-tags.tsv": 1,
        "post-xrefs.tsv": 3,
        "post-instructions.tsv": 261,
        "post-decompile/index.tsv": 1,
        "post-context-metadata.tsv": 7,
        "post-context-decompile/index.tsv": 7,
        "post-caller-metadata.tsv": 3,
        "post-caller-decompile/index.tsv": 3,
        "post-callsite-instructions.tsv": 201,
        "post-vtable.tsv": 12,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    pre = read_tsv(BASE / "pre-metadata.tsv")[0]
    post = read_tsv(BASE / "post-metadata.tsv")[0]
    require(normalize_address(pre["address"]) == ADDRESS, "pre address mismatch", failures)
    require(pre["name"] == NAME, "pre name mismatch", failures)
    require(pre["signature"] == SIGNATURE, "pre signature mismatch", failures)
    require(not pre.get("comment", "").strip(), "pre row should be commentless", failures)
    require(normalize_address(post["address"]) == ADDRESS, "post address mismatch", failures)
    require(post["name"] == NAME, "post name mismatch", failures)
    require(post["signature"] == SIGNATURE, "post signature mismatch", failures)

    comment = post.get("comment", "")
    for token in (
        "Wave810 static read-back hardening",
        "comment/tag-only",
        "0x54-byte cleaned stack contract",
        "by-value vector/matrix payload",
        "0x00498ac6",
        "0x00498bad",
        "0x0049bddf",
        "mesh_part+0x90",
        "mesh_part+0x94",
        "CMCMech__UpdateBone",
        "runtime leg/bone animation behavior",
        "rebuild parity remain deferred",
    ):
        require(token in comment, f"missing post comment token: {token}", failures)

    tags = set(read_tsv(BASE / "post-tags.tsv")[0].get("tags", "").split(";"))
    require(COMMON_TAGS.issubset(tags), f"missing tags: {COMMON_TAGS - tags}", failures)

    decomp = read_tsv(BASE / "post-decompile" / "index.tsv")[0]
    require(decomp["name"] == NAME, "post decompile name mismatch", failures)
    require(decomp["signature"] == SIGNATURE, "post decompile signature mismatch", failures)
    require(decomp["status"] == "OK", "post decompile status mismatch", failures)

    decomp_text = read_text(BASE / "post-decompile" / "0049bd50_CMCMech__UpdateBoneHierarchyRecursive.c")
    for token in (
        "Unknown calling convention",
        "CMCMech__UpdateBone(",
        "in_stack_00000044 + 0x90",
        "CMCMech__UpdateBoneHierarchyRecursive();",
        "return;",
    ):
        require(token in decomp_text, f"missing decompile token: {token}", failures)

    instruction_rows = read_tsv(BASE / "post-instructions.tsv")
    by_addr = {normalize_address(row["instruction_addr"]): row for row in instruction_rows}
    require(by_addr.get("0x0049bd50", {}).get("mnemonic") == "PUSH", "missing target PUSH ECX row", failures)
    require(by_addr.get("0x0049bd81", {}).get("operands") == "EAX, dword ptr [EBP + 0x90]", "missing child-count load", failures)
    require(by_addr.get("0x0049bddf", {}).get("operands") == "0x0049bd50", "missing recursive call operand", failures)
    require(by_addr.get("0x0049bdf4", {}).get("mnemonic") == "RET", "missing RET row", failures)
    require(by_addr.get("0x0049bdf4", {}).get("operands") == "0x54", "missing RET 0x54 row", failures)

    xrefs = read_tsv(BASE / "post-xrefs.tsv")
    xref_from = {normalize_address(row["from_addr"]) for row in xrefs}
    for addr in ("0x00498ac6", "0x00498bad", "0x0049bddf"):
        require(addr in xref_from, f"missing xref from {addr}", failures)

    callsite_rows = read_tsv(BASE / "post-callsite-instructions.tsv")
    targets = [row for row in callsite_rows if row["role"] == "TARGET"]
    require(len(targets) == 3, "target callsite row count mismatch", failures)
    require(all(row["operands"] == "0x0049bd50" for row in targets), "callsite target operand mismatch", failures)

    callers = {row["name"] for row in read_tsv(BASE / "post-caller-metadata.tsv")}
    require({"CMCMech__Reset", NAME}.issubset(callers), "missing caller metadata", failures)

    vtable_names = {row["function_name"] for row in read_tsv(BASE / "post-vtable.tsv")}
    require("CMCMech__VFunc_04_UpdateInterpolatedBoneTransform_0049be00" in vtable_names, "missing CMCMech slot 4", failures)
    require("CMCMech__VFunc_05_WriteInterpolatedBoneFloat_0049c1d0" in vtable_names, "missing CMCMech slot 5", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=1 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=1 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=1 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=1 found=1 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=1 missing=0",
        "post-xrefs.log": "Wrote 3 rows",
        "post-instructions.log": "Wrote 261 instruction rows",
        "post-decompile.log": "targets=1 dumped=1 missing=0 failed=0",
        "post-context-metadata.log": "targets=7 found=7 missing=0",
        "post-context-decompile.log": "targets=7 dumped=7 missing=0 failed=0",
        "post-caller-metadata.log": "targets=3 found=3 missing=0",
        "post-caller-decompile.log": "targets=3 dumped=3 missing=0 failed=0",
        "post-callsite-instructions.log": "Wrote 201 instruction rows",
        "post-vtable.log": "ExportVtableSlots complete: targets=1 rows=12",
        "quality-refresh.log": "total_functions=6098 commented_functions=5585",
        "queue-probe.log": "Commentless functions: 513",
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave810.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave810_queue_probe.log",
    }
    for relative, token in expected.items():
        path = aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIG:", "BADCOMMENT:", "BADTAGS:", "FAIL:", "missing=1", "bad=1", "failed=1", "Input file not found", "SCRIPT ERROR"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 513, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict = signature_counts(rows)
    raw = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5585, "commented count mismatch", failures)
    require(strict == 5585, "strict count mismatch", failures)
    require(raw is not None and raw.get("address") == "0x0049c2d0", "raw head address mismatch", failures)
    require(raw is not None and raw.get("name") == "CMeshPart__HasAnimationToken_623074", "raw head name mismatch", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") in (171314055, 171314055.0), "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [PUBLIC_NOTE, FUNCTION_INDEX, GHIDRA_REFERENCE, CAMPAIGN, BACKLOG, MECH_DOC, DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE]
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:ghidra-cmcmech-bone-recursive-wave810")
        == r"py -3 tools\ghidra_cmcmech_bone_recursive_wave810_probe.py --check",
        "missing package script",
        failures,
    )
    require(any(row.get("task") == "Wave810 CMCMech bone recursive" for row in read_jsonl(LEDGER)), "missing Wave810 ledger row", failures)
    require(
        any(row.get("task") == "Wave810 CMCMech bone recursive" and row.get("attempt_id") == 20465 for row in read_jsonl(ATTEMPT_LOG)),
        "missing Wave810 attempt row",
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
        print("Wave810 CMCMech bone-recursive probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave810 CMCMech bone-recursive probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
