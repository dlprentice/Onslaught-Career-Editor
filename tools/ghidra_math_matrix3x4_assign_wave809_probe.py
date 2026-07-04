#!/usr/bin/env python3
"""Validate Wave809 math-matrix3x4 assign read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave809-math-matrix3x4-assign"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_math_matrix3x4_assign_wave809_2026-05-24.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
MATH_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Math.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"

ADDRESS = "0x004901e0"
NAME = "MathMatrix3x4__AssignFromEightScalars"
SIGNATURE = (
    "void __thiscall MathMatrix3x4__AssignFromEightScalars(void * this, "
    "float scalar_00, float scalar_14, float scalar_18, float scalar_1c, "
    "float scalar_20, float scalar_24, float scalar_28, float scalar_2c)"
)
BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260524-120255_post_wave809_math_matrix3x4_assign_verified"
NEXT_HEAD = "0x0049bd50 CMCMech__UpdateBoneHierarchyRecursive"

COMMON_TAGS = {
    "static-reaudit",
    "math-matrix3x4-assign-wave809",
    "wave809-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "math-matrix",
    "matrix3x4",
    "owner-neutral",
    "raw-commentless-tail",
    "tranche-head",
}

DOC_TOKENS = (
    "Wave809 math-matrix3x4 assign",
    "math-matrix3x4-assign-wave809",
    "0x004901e0 MathMatrix3x4__AssignFromEightScalars",
    "RET 0x20",
    "5584/6098 = 91.57%",
    NEXT_HEAD,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime render/math behavior proven",
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
        "pre-xrefs.tsv": 16,
        "pre-instructions.tsv": 125,
        "pre-decompile/index.tsv": 1,
        "pre-caller-metadata.tsv": 5,
        "pre-caller-decompile/index.tsv": 5,
        "pre-callsite-instructions.tsv": 432,
        "post-metadata.tsv": 1,
        "post-tags.tsv": 1,
        "post-xrefs.tsv": 16,
        "post-instructions.tsv": 125,
        "post-decompile/index.tsv": 1,
        "post-caller-decompile/index.tsv": 5,
        "post-callsite-instructions.tsv": 432,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    pre = read_tsv(BASE / "pre-metadata.tsv")[0]
    post = read_tsv(BASE / "post-metadata.tsv")[0]
    require(normalize_address(pre["address"]) == ADDRESS, "pre address mismatch", failures)
    require(pre["name"] == NAME, "pre name mismatch", failures)
    require(pre["signature"] == f"int {NAME}(void)", "pre signature mismatch", failures)
    require(not pre.get("comment", "").strip(), "pre row should be commentless", failures)
    require(normalize_address(post["address"]) == ADDRESS, "post address mismatch", failures)
    require(post["name"] == NAME, "post name mismatch", failures)
    require(post["signature"] == SIGNATURE, "post signature mismatch", failures)
    for token in (
        "Wave809 static read-back hardening",
        "CUnitAI__Unk_004901e0",
        "RET 0x20",
        "Sixteen observed callsites",
        "ignore EAX",
        "source identity",
        "rebuild parity remain deferred",
    ):
        require(token in post.get("comment", ""), f"missing post comment token: {token}", failures)

    tags = set(read_tsv(BASE / "post-tags.tsv")[0].get("tags", "").split(";"))
    require(COMMON_TAGS.issubset(tags), f"missing tags: {COMMON_TAGS - tags}", failures)

    decomp = read_tsv(BASE / "post-decompile" / "index.tsv")[0]
    require(decomp["name"] == NAME, "post decompile name mismatch", failures)
    require(decomp["signature"] == SIGNATURE, "post decompile signature mismatch", failures)
    require(decomp["status"] == "OK", "post decompile status mismatch", failures)

    decomp_text = read_text(BASE / "post-decompile" / "004901e0_MathMatrix3x4__AssignFromEightScalars.c")
    for token in (
        "*(float *)this = scalar_00;",
        "*(float *)((int)this + 0x14) = scalar_14;",
        "*(float *)((int)this + 0x2c) = scalar_2c;",
        "return;",
    ):
        require(token in decomp_text, f"missing decompile token: {token}", failures)

    xrefs = read_tsv(BASE / "post-xrefs.tsv")
    callers = {row["from_function"] for row in xrefs}
    for caller in (
        "CEngine__SetupLights",
        "CDXFrontEnd__SetupRenderMatricesAndProjection",
        "CFEPBEConfig__Render",
        "CRTTree__VFuncSlot02_BuildRenderOutputs",
        "CFEPMultiplayerStart__Render",
        "<no_function>",
    ):
        require(caller in callers, f"missing xref caller: {caller}", failures)

    callsite_rows = read_tsv(BASE / "post-callsite-instructions.tsv")
    targets = [row for row in callsite_rows if row["role"] == "TARGET"]
    require(len(targets) == 16, "target callsite row count mismatch", failures)
    require(all(row["operands"] == "0x004901e0" for row in targets), "callsite target operand mismatch", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=1 skipped=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=1 found=1 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=1 missing=0",
        "post-xrefs.log": "Wrote 16 rows",
        "post-instructions.log": "Wrote 125 instruction rows",
        "post-decompile.log": "targets=1 dumped=1 missing=0 failed=0",
        "post-caller-decompile.log": "targets=5 dumped=5 missing=0 failed=0",
        "post-callsite-instructions.log": "Wrote 432 instruction rows",
        "quality-refresh.log": "total_functions=6098 commented_functions=5584",
        "queue-probe.log": "Commentless functions: 514",
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave809.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave809_queue_probe.log",
    }
    for relative, token in expected.items():
        path = aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 514, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict = signature_counts(rows)
    raw = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5584, "commented count mismatch", failures)
    require(strict == 5584, "strict count mismatch", failures)
    require(raw is not None and raw.get("address") == "0x0049bd50", "raw head address mismatch", failures)
    require(raw is not None and raw.get("name") == "CMCMech__UpdateBoneHierarchyRecursive", "raw head name mismatch", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") in (171314055, 171314055.0), "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [PUBLIC_NOTE, FUNCTION_INDEX, GHIDRA_REFERENCE, CAMPAIGN, BACKLOG, MATH_DOC, DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE]
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:ghidra-math-matrix3x4-assign-wave809")
        == r"py -3 tools\ghidra_math_matrix3x4_assign_wave809_probe.py --check",
        "missing package script",
        failures,
    )
    require(any(row.get("task") == "Wave809 math-matrix3x4 assign" for row in read_jsonl(LEDGER)), "missing Wave809 ledger row", failures)
    require(
        any(row.get("task") == "Wave809 math-matrix3x4 assign" and row.get("attempt_id") == 20464 for row in read_jsonl(ATTEMPT_LOG)),
        "missing Wave809 attempt row",
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
        print("Wave809 math-matrix3x4 assign probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave809 math-matrix3x4 assign probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
