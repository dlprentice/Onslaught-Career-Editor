#!/usr/bin/env python3
"""Validate Wave845 CSpawnerThng spawn-type predicate read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave845-spawner-type-allowed"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_spawner_type_allowed_wave845_2026-05-25.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
SPAWNER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "SpawnerThng.cpp" / "_index.md"
WPM_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "WorldPhysicsManager.cpp" / "_index.md"
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

ADDRESS = "0x0050f680"
NAME = "CSpawnerThng__IsSpawnTypeAllowed"
SIGNATURE = "bool __cdecl CSpawnerThng__IsSpawnTypeAllowed(int spawn_type)"
BACKUP_PATH = r"G:\GhidraBackups\BEA_20260525-053251_post_wave845_spawner_type_allowed_verified"
NEXT_HEAD = "0x00510520"

COMMON_TAGS = {
    "static-reaudit",
    "spawner-type-allowed-wave845",
    "wave845-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "cspawnerthng",
    "spawn-type-gate",
    "predicate",
    "jump-table",
}

COMMENT_TOKENS = (
    "Wave845 static read-back",
    "CSpawnerThng__Init at 0x004e32cc",
    "CSpawnerThng__Constructor at 0x004e39b2",
    "TEST EAX,EAX",
    "0x0050f6a4/0x0050f6ac",
    "4 through 0x14 and 0x16 through 0x18",
    "unlisted 0x15 slot",
    "Static retail Ghidra evidence only",
)

DOC_TOKENS = (
    "Wave845 CSpawner Type Allowed",
    "spawner-type-allowed-wave845",
    "0x0050f680 CSpawnerThng__IsSpawnTypeAllowed",
    SIGNATURE,
    "0x004e32cc",
    "0x004e39b2",
    "0x0050f6a4/0x0050f6ac",
    "4 through 0x14 and 0x16 through 0x18",
    "5669/6098 = 92.96%",
    "0x00510520 CWorldPhysicsManager__ResolveLoadedDefinitionReferences",
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime spawn admission behavior proven",
    "fully reverse-engineered",
    "rebuild parity proven",
    "exact enum names proven",
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
        "pre-xrefs.tsv": 2,
        "pre-instructions.tsv": 241,
        "pre-xref-site-instructions.tsv": 98,
        "pre-context-metadata.tsv": 7,
        "pre-context-tags.tsv": 7,
        "pre-decompile/index.tsv": 1,
        "post-metadata.tsv": 1,
        "post-tags.tsv": 1,
        "post-xrefs.tsv": 2,
        "post-instructions.tsv": 241,
        "post-xref-site-instructions.tsv": 98,
        "post-context-metadata.tsv": 7,
        "post-context-tags.tsv": 7,
        "post-decompile/index.tsv": 1,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = read_tsv(BASE / "post-metadata.tsv")[0]
    require(normalize_address(metadata["address"]) == ADDRESS, "metadata address mismatch", failures)
    require(metadata["name"] == NAME, "metadata name mismatch", failures)
    require(metadata["signature"] == SIGNATURE, "metadata signature mismatch", failures)
    require(metadata["status"] == "OK", "metadata status mismatch", failures)
    for token in COMMENT_TOKENS:
        require(token in metadata.get("comment", ""), f"missing metadata comment token: {token}", failures)

    tags = set(read_tsv(BASE / "post-tags.tsv")[0].get("tags", "").split(";"))
    require(COMMON_TAGS.issubset(tags), f"missing tags: {COMMON_TAGS - tags}", failures)

    xrefs = {(normalize_address(row["from_addr"]), row["from_function"], row["ref_type"]) for row in read_tsv(BASE / "post-xrefs.tsv")}
    require(("0x004e32cc", "CSpawnerThng__Init", "UNCONDITIONAL_CALL") in xrefs, "missing Init xref", failures)
    require(("0x004e39b2", "CSpawnerThng__Constructor", "UNCONDITIONAL_CALL") in xrefs, "missing Constructor xref", failures)

    decompile = read_tsv(BASE / "post-decompile" / "index.tsv")[0]
    require(normalize_address(decompile["address"]) == ADDRESS, "decompile address mismatch", failures)
    require(decompile["signature"] == SIGNATURE, "decompile signature mismatch", failures)
    require(decompile["status"] == "OK", "decompile status mismatch", failures)
    decompile_text = read_text(BASE / "post-decompile" / "0050f680_CSpawnerThng__IsSpawnTypeAllowed.c")
    for token in ("return false;", "return true;", "case 0x18:", "bool __cdecl"):
        require(token in decompile_text, f"missing decompile token: {token}", failures)

    target_rows = [row for row in read_tsv(BASE / "post-instructions.tsv") if row.get("function_name") == NAME]
    require(len(target_rows) == 11, "target instruction row count mismatch", failures)
    by_addr = {normalize_address(row["instruction_addr"]): row for row in target_rows}
    expected_instr = {
        "0x0050f680": ("MOV", "EAX, dword ptr [ESP + 0x4]"),
        "0x0050f68a": ("JA", "0x0050f69e"),
        "0x0050f694": ("JMP", "dword ptr [ECX*0x4 + 0x50f6a4]"),
        "0x0050f69b": ("XOR", "EAX, EAX"),
        "0x0050f69e": ("MOV", "EAX, 0x1"),
        "0x0050f6a3": ("RET", ""),
    }
    for address, (mnemonic, operands) in expected_instr.items():
        row = by_addr.get(address)
        require(row is not None, f"missing instruction row: {address}", failures)
        if row is not None:
            require(row.get("mnemonic") == mnemonic, f"mnemonic mismatch at {address}", failures)
            require(row.get("operands") == operands, f"operand mismatch at {address}", failures)

    xref_text = read_text(BASE / "post-xref-site-instructions.tsv")
    for token in ("0x004e32cc", "0x004e39b2", "TEST\tEAX, EAX", "JNZ"):
        require(token in xref_text, f"missing xref-site token: {token}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=1 skipped=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=1 found=1 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=1 missing=0",
        "post-xrefs.log": "Wrote 2 rows",
        "post-instructions.log": "Wrote 241 instruction rows",
        "post-xref-site-instructions.log": "Wrote 98 instruction rows",
        "post-context-metadata.log": "targets=7 found=7 missing=0",
        "post-context-tags.log": "ExportFunctionTagsByAddress complete: rows=7 missing=0",
        "post-decompile.log": "targets=1 dumped=1 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6098 commented_functions=5669",
        "queue-probe.log": "Commentless functions: 429",
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave845.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave845_queue_probe.log",
    }
    for relative, token in expected.items():
        path = aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "READBACK_BAD", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 429, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(queue["priorityQueues"]["commentlessHighSignal"] == [], "high-signal queue should remain empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5669, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5669, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and normalize_address(raw_commentless.get("address", "")) == NEXT_HEAD, "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CWorldPhysicsManager__ResolveLoadedDefinitionReferences", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 171871111, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        SPAWNER_DOC,
        WPM_DOC,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:ghidra-spawner-type-allowed-wave845") == r"py -3 tools\ghidra_spawner_type_allowed_wave845_probe.py --check",
        "missing package script",
        failures,
    )

    require(any(row.get("task") == "Wave845 CSpawner Type Allowed" for row in read_jsonl(LEDGER)), "missing Wave845 ledger row", failures)
    require(any(row.get("task") == "Wave845 CSpawner Type Allowed" for row in read_jsonl(ATTEMPT_LOG)), "missing Wave845 attempt row", failures)


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
        print("Wave845 CSpawner Type Allowed probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave845 CSpawner Type Allowed probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
