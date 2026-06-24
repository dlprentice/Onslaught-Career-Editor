#!/usr/bin/env python3
"""Validate Wave797 SPtrSet clear thunk read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave797-sptrset-clear"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_sptrset_clear_wave797_2026-05-24.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
SPTRSET_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "SPtrSet.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260524-054154_post_wave797_sptrset_clear_verified"
TARGET = "0x0042f220"
TARGET_NAME = "CSPtrSet__Clear"
TARGET_SIGNATURE = "void __fastcall CSPtrSet__Clear(void * this)"
NEXT_RAW_HEAD = "0x004404f0"

COMMON_TAGS = {
    "static-reaudit",
    "sptrset-clear-wave797",
    "wave797-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "sptrset",
    "thunk-wrapper",
    "free-list",
}

CORE_ANCHORS = (
    "Wave797 SPtrSet clear",
    "sptrset-clear-wave797",
    "0x0042f220 CSPtrSet__Clear",
    "0x004e5c60 CSPtrSet__Clear",
    "0x004404f0 CThing__NegateVec3ToOut",
    "0 exact-undefined signatures",
    "0 param_N signatures",
    "5545/6098 = 90.93%",
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime pool behavior proven",
    "runtime behavior proven",
    "fully reverse-engineered",
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
        "pre-xrefs.tsv": 164,
        "pre-instructions.tsv": 65,
        "pre-decompile/index.tsv": 1,
        "pre-helper-metadata.tsv": 12,
        "pre-helper-xrefs.tsv": 686,
        "pre-helper-decompile/index.tsv": 12,
        "post-metadata.tsv": 1,
        "post-tags.tsv": 1,
        "post-xrefs.tsv": 164,
        "post-instructions.tsv": 65,
        "post-decompile/index.tsv": 1,
        "post-helper-metadata.tsv": 12,
        "post-helper-xrefs.tsv": 686,
        "post-helper-decompile/index.tsv": 12,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    row = metadata.get(TARGET)
    require(row is not None, "missing post metadata target", failures)
    if row is not None:
        require(row.get("name") == TARGET_NAME, "target name mismatch", failures)
        require(row.get("signature") == TARGET_SIGNATURE, "target signature mismatch", failures)
        require(row.get("status") == "OK", "target metadata status mismatch", failures)
        comment = row.get("comment", "")
        for token in (
            "Wave797 static read-back",
            "5-byte unconditional JMP",
            "0x004e5c60",
            "g_SPtrSet_FreeListHead",
            "iterator field at +0x08",
            "rebuild parity remain unproven",
        ):
            require(token in comment, f"missing comment token: {token}", failures)

    tag_row = tags.get(TARGET)
    require(tag_row is not None, "missing target tags", failures)
    if tag_row is not None:
        actual_tags = set(tag_row.get("tags", "").split(";"))
        require(COMMON_TAGS.issubset(actual_tags), f"tags missing: {COMMON_TAGS - actual_tags}", failures)
        require(tag_row.get("status") == "OK", "target tag status mismatch", failures)

    dec = decompile.get(TARGET)
    require(dec is not None, "missing target decompile index", failures)
    if dec is not None:
        require(dec.get("signature") == TARGET_SIGNATURE, "decompile signature mismatch", failures)
        require(dec.get("status") == "OK", "decompile status mismatch", failures)

    instructions = read_tsv(BASE / "post-instructions.tsv")
    target_instr = next((row for row in instructions if row.get("role") == "TARGET"), None)
    require(target_instr is not None, "missing target instruction row", failures)
    if target_instr is not None:
        require(target_instr.get("mnemonic") == "JMP", "target instruction is not JMP", failures)
        require(target_instr.get("operands") == "0x004e5c60", "target jump operand mismatch", failures)
        require(target_instr.get("bytes") == "e9 3b 6a 0b 00", "target jump bytes mismatch", failures)

    helper_names = {row["name"] for row in read_tsv(BASE / "post-helper-metadata.tsv")}
    for name in (
        "CSPtrSet__Init",
        "CSPtrSet__CopyCtorFromSource",
        "CSPtrSet__operator_assign",
        "CSPtrSet__Shutdown",
        "CSPtrSet__ClearAnyDynamicCreatedNodes",
        "CSPtrSet__Initialise",
        "CSPtrSet__AddToHead",
        "CSPtrSet__AddToTail",
        "CSPtrSet__Remove",
        "CSPtrSet__Contains",
        "CSPtrSet__Clear",
        "CSPtrSet__At",
    ):
        require(name in helper_names, f"missing helper metadata row: {name}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=1 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=1 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=1 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=1 found=1 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=1 missing=0",
        "post-xrefs.log": "Wrote 164 rows",
        "post-instructions.log": "Wrote 65 instruction rows",
        "post-decompile.log": "targets=1 dumped=1 missing=0 failed=0",
        "post-helper-metadata.log": "targets=12 found=12 missing=0",
        "post-helper-xrefs.log": "Wrote 686 rows",
        "post-helper-decompile.log": "targets=12 dumped=12 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6098 commented_functions=5545",
        "queue-probe.log": "Commentless functions: 553",
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave797.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave797_queue_probe.log",
    }
    for relative, token in expected.items():
        path = aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIG:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 553, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(queue["priorityQueues"]["commentlessHighSignal"] == [], "commentless high-signal queue should be empty", failures)
    require(queue["priorityQueues"]["signature"] == [], "signature queue should be empty", failures)
    require(queue["priorityQueues"]["nameConfidence"] == [], "name-confidence queue should be empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5545, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5545, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == NEXT_RAW_HEAD, "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CThing__NegateVec3ToOut", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 171314055, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    broad_docs = [
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in broad_docs:
        text = read_text(path)
        for token in CORE_ANCHORS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    sptrset = read_text(SPTRSET_DOC)
    for token in (
        "Wave797 SPtrSet clear",
        "sptrset-clear-wave797",
        "0x0042f220 CSPtrSet__Clear",
        "0x004e5c60 CSPtrSet__Clear",
        "0x004404f0 CThing__NegateVec3ToOut",
        BACKUP_PATH,
    ):
        require(contains_token(sptrset, token), f"missing token in {SPTRSET_DOC.relative_to(ROOT)}: {token}", failures)
    for bad in OVERCLAIM_TOKENS:
        require(bad not in sptrset.lower(), f"overclaim token in {SPTRSET_DOC.relative_to(ROOT)}: {bad}", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(scripts.get("test:ghidra-sptrset-clear-wave797") == r"py -3 tools\ghidra_sptrset_clear_wave797_probe.py --check", "missing package script", failures)
    require(any(row.get("task") == "Wave797 SPtrSet clear thunk" for row in read_jsonl(LEDGER)), "missing Wave797 ledger row", failures)
    require(any(row.get("task") == "Wave797 SPtrSet clear thunk" and row.get("attempt_id") == 20452 for row in read_jsonl(ATTEMPT_LOG)), "missing Wave797 attempt row", failures)


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
        print("Wave797 SPtrSet-clear probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave797 SPtrSet-clear probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
