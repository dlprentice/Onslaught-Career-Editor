#!/usr/bin/env python3
"""Validate Wave839 Warspite transition read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave839-warspite-transition"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_warspite_transition_wave839_2026-05-25.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
WARSPITE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Warspite.cpp" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

ADDRESS = "0x004fde70"
NAME = "CWarspite__TransitionToUndeploying"
SIGNATURE = "void __thiscall CWarspite__TransitionToUndeploying(void * this)"
BACKUP_PATH = r"G:\GhidraBackups\BEA_20260525-023901_post_wave839_warspite_transition_verified"
NEXT_HEAD = "0x005016b0 InitShaderCapabilityFlagsAndCVar"

EXPECTED_TAGS = {
    "static-reaudit",
    "warspite-transition-wave839",
    "wave839-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "cwarspite",
    "warspite",
    "state-machine",
    "animation-transition",
    "undeploying",
}

COMMENT_TOKENS = (
    "Wave839 static read-back/comment hardening",
    "this+0x244 equals 4",
    "writes state 5",
    "this+0x30",
    "s_undeploying_006239d8",
    "CMesh__FindAnimationIndexByName",
    "vfunc +0xf0",
    "0x004ff2ae",
    "CWarspite__Update",
    "runtime AI/animation behavior",
)

INSTRUCTION_EXPECTATIONS = (
    ("0x004fde73", "CMP", "dword ptr [ESI + 0x244], 0x4"),
    ("0x004fde82", "MOV", "dword ptr [ESI + 0x244], 0x5"),
    ("0x004fde92", "PUSH", "0x6239d8"),
    ("0x004fde97", "CALL", "dword ptr [EAX + 0x24]"),
    ("0x004fde9c", "CALL", "0x004aa630"),
    ("0x004fdea4", "CALL", "dword ptr [EDI + 0xf0]"),
)

CORE_DOC_TOKENS = (
    "Wave839 Warspite Transition",
    "warspite-transition-wave839",
    "0x004fde70 CWarspite__TransitionToUndeploying",
    "this+0x244 equals 4",
    "writes state 5",
    "s_undeploying_006239d8",
    "CMesh__FindAnimationIndexByName",
    "0x004ff2ae CWarspite__Update",
    "5663/6098 = 92.87%",
    NEXT_HEAD,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "runtime ai/animation behavior proven",
    "state enum proven",
    "animation behavior proven",
    "fully reverse-engineered",
    "rebuild parity proven",
)


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


def normalize_address(address: str) -> str:
    value = address.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


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
        "pre-xrefs.tsv": 6,
        "pre-instructions.tsv": 121,
        "pre-target-deep-instructions.tsv": 221,
        "pre-xref-site-instructions.tsv": 438,
        "pre-decompile/index.tsv": 1,
        "pre-context-metadata.tsv": 10,
        "pre-context-decompile/index.tsv": 10,
        "post-metadata.tsv": 1,
        "post-tags.tsv": 1,
        "post-xrefs.tsv": 6,
        "post-instructions.tsv": 121,
        "post-target-deep-instructions.tsv": 221,
        "post-xref-site-instructions.tsv": 438,
        "post-decompile/index.tsv": 1,
        "post-context-metadata.tsv": 10,
        "post-context-decompile/index.tsv": 10,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = read_tsv(BASE / "post-metadata.tsv")[0]
    require(normalize_address(metadata.get("address", "")) == ADDRESS, "metadata address mismatch", failures)
    require(metadata.get("name") == NAME, "metadata name mismatch", failures)
    require(metadata.get("signature") == SIGNATURE, "metadata signature mismatch", failures)
    require(metadata.get("status") == "OK", "metadata status mismatch", failures)
    comment = metadata.get("comment", "")
    for token in COMMENT_TOKENS:
        require(token in comment, f"missing comment token: {token}", failures)

    tags = read_tsv(BASE / "post-tags.tsv")[0]
    require(normalize_address(tags.get("address", "")) == ADDRESS, "tag address mismatch", failures)
    actual_tags = set(tags.get("tags", "").split(";"))
    require(EXPECTED_TAGS.issubset(actual_tags), f"missing tags: {EXPECTED_TAGS - actual_tags}", failures)

    xrefs = read_tsv(BASE / "post-xrefs.tsv")
    xref_from = {normalize_address(row.get("from_addr", "")) for row in xrefs}
    for expected in ("0x004ff2ae", "0x00534f99", "0x00416870", "0x0044655f", "0x00446671", "0x0044671a"):
        require(expected in xref_from, f"missing xref source {expected}", failures)

    instructions = {
        normalize_address(row.get("instruction_addr", "")): row
        for row in read_tsv(BASE / "post-target-deep-instructions.tsv")
    }
    for address, mnemonic, operands in INSTRUCTION_EXPECTATIONS:
        row = instructions.get(address)
        require(row is not None, f"missing instruction row: {address}", failures)
        if row is not None:
            require(row.get("mnemonic") == mnemonic, f"instruction mnemonic mismatch at {address}", failures)
            require(row.get("operands") == operands, f"instruction operands mismatch at {address}", failures)

    decompile_rows = read_tsv(BASE / "post-decompile" / "index.tsv")
    require(decompile_rows[0].get("signature") == SIGNATURE, "decompile signature mismatch", failures)
    require(decompile_rows[0].get("status") == "OK", "decompile status mismatch", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=1 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=1 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=1 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=1 found=1 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=1 missing=0",
        "post-xrefs.log": "Wrote 6 rows",
        "post-instructions.log": "Wrote 121 instruction rows",
        "post-target-deep-instructions.log": "Wrote 221 instruction rows",
        "post-xref-site-instructions.log": "Wrote 438 instruction rows",
        "post-decompile.log": "targets=1 dumped=1 missing=0 failed=0",
        "post-context-metadata.log": "targets=10 found=10 missing=0",
        "post-context-decompile.log": "targets=10 dumped=10 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6098 commented_functions=5663",
        "queue-probe.log": "Commentless functions: 435",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave839.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave839_queue_probe.log",
    }
    for relative, token in expected.items():
        path = log_aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 435, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5663, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5663, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x005016b0", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "InitShaderCapabilityFlagsAndCVar", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes", 0)) == 171838343, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        WARSPITE_DOC,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in docs:
        text = read_text(path)
        for token in CORE_DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-warspite-transition-wave839")
        == r"py -3 tools\ghidra_warspite_transition_wave839_probe.py --check",
        "missing package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempt_rows = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave839 Warspite Transition" for row in ledger_rows), "missing Wave839 ledger row", failures)
    require(
        any(row.get("task") == "Wave839 Warspite Transition" and row.get("attempt_id") == 20494 for row in attempt_rows),
        "missing Wave839 attempt row",
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
        print("Wave839 Warspite transition probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave839 Warspite transition probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
