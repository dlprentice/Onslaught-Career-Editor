#!/usr/bin/env python3
"""Validate Wave844 CWorld__LoadWorld read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave844-cworld-load-world"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cworld_load_world_wave844_2026-05-25.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
WORLD_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "World.cpp" / "_index.md"
LOADWORLD_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "World.cpp" / "CWorld__LoadWorld.md"
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

ADDRESS = "0x0050b9c0"
NAME = "CWorld__LoadWorld"
SIGNATURE = "bool __thiscall CWorld__LoadWorld(void * this, void * levelName)"
BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260525-050626_post_wave844_cworld_load_world_verified"
NEXT_HEAD = "0x0050f680"

COMMON_TAGS = {
    "static-reaudit",
    "cworld-load-world-wave844",
    "wave844-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-readback-verified",
    "cworld",
    "world-load",
    "level-loading",
    "occupancy-finalization",
    "ret0c",
}

COMMENT_TOKENS = (
    "Wave844 static read-back",
    "CWorld__LoadWorldFile at 0x0050b720",
    "0x38cc-byte stack frame",
    "RET 0xc",
    "CWorld__LoadWorldHeader",
    "CWorld__LoadScriptEvents",
    "CWorldPhysicsManager__CreateSquad",
    "CWorldPhysicsManager__CreateThingByType",
    "CWorldPhysicsManager__CreateEffect",
    "CWorldPhysicsManager__CreateTrigger",
    "CWorldMeshList__Add",
    "CInfluenceMapManager__SkipLoad",
    "CWaypointManager__LoadWaypoints",
    "CWorld__SpawnInitialThings",
    "CWorld__ApplyStaticMaskToOccupancyBitplanes",
    "CWorld__RebuildOccupancyGridFromDynamicSet",
    "Static retail Ghidra evidence only",
)

INSTRUCTION_TOKENS = {
    "0x0050b9da": "0x0055def0",
    "0x0050ba7a": "0x0050d580",
    "0x0050baed": "0x0050d4c0",
    "0x0050bbde": "0x0050ac70",
    "0x0050bbf5": "0x0050b520",
    "0x0050bc29": "0x00490f50",
    "0x0050bc34": "0x00449dc0",
    "0x0050bd8a": "0x0050f4b0",
    "0x0050bf56": "0x00510060",
    "0x0050c146": "0x00510150",
    "0x0050ca98": "0x0050df80",
    "0x0050cad1": "0x0050d9e0",
    "0x0050cf23": "0x0048b660",
    "0x0050cf38": "0x0048b010",
    "0x0050d187": "0x00505ae0",
    "0x0050d331": "0x004bdff0",
    "0x0050d363": "0x004be050",
    "0x0050d386": "0x004be170",
    "0x0050d431": "0x0050dcb0",
    "0x0050d456": "0x004bc8d0",
    "0x0050d473": "0x004bcbf0",
    "0x0050d47a": "0x004bcd60",
}

DOC_TOKENS = (
    "Wave844 CWorld LoadWorld",
    "cworld-load-world-wave844",
    "0x0050b9c0 CWorld__LoadWorld",
    SIGNATURE,
    "0x0050b720",
    "0x38cc-byte stack frame",
    "RET 0xc",
    "CWorldPhysicsManager__CreateThingByType",
    "CWaypointManager__LoadWaypoints",
    "CWorld__ApplyStaticMaskToOccupancyBitplanes",
    "CWorld__RebuildOccupancyGridFromDynamicSet",
    "5668/6098 = 92.95%",
    "0x0050f680 CSpawnerThng__IsSpawnTypeAllowed",
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime load behavior proven",
    "fully reverse-engineered",
    "rebuild parity proven",
    "world-buffer schema proven",
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
        "pre-xrefs.tsv": 1,
        "pre-instructions.tsv": 901,
        "pre-instructions-complete.tsv": 3201,
        "pre-context-metadata.tsv": 11,
        "pre-context-tags.tsv": 11,
        "pre-decompile/index.tsv": 1,
        "post-metadata.tsv": 1,
        "post-tags.tsv": 1,
        "post-xrefs.tsv": 1,
        "post-instructions-complete.tsv": 3201,
        "post-context-metadata.tsv": 11,
        "post-context-tags.tsv": 11,
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

    xref = read_tsv(BASE / "post-xrefs.tsv")[0]
    require(normalize_address(xref["target_addr"]) == ADDRESS, "xref target mismatch", failures)
    require(normalize_address(xref["from_addr"]) == "0x0050b720", "xref caller mismatch", failures)
    require(xref["from_function"] == "CWorld__LoadWorldFile", "xref caller name mismatch", failures)
    require(xref["ref_type"] == "UNCONDITIONAL_CALL", "xref type mismatch", failures)

    decompile = read_tsv(BASE / "post-decompile" / "index.tsv")[0]
    require(normalize_address(decompile["address"]) == ADDRESS, "decompile address mismatch", failures)
    require(decompile["signature"] == SIGNATURE, "decompile signature mismatch", failures)
    require(decompile["status"] == "OK", "decompile status mismatch", failures)

    instructions = read_tsv(BASE / "post-instructions-complete.tsv")
    body_rows = [row for row in instructions if row.get("function_name") == NAME]
    require(len(body_rows) == 2023, "function body instruction row count mismatch", failures)
    by_addr = {normalize_address(row["instruction_addr"]): row for row in body_rows}
    for address, operand in INSTRUCTION_TOKENS.items():
        row = by_addr.get(address)
        require(row is not None, f"missing instruction row: {address}", failures)
        if row is not None:
            require(row.get("mnemonic") == "CALL", f"instruction mnemonic mismatch at {address}", failures)
            require(row.get("operands") == operand, f"instruction operand mismatch at {address}", failures)
    tail = by_addr.get("0x0050d4af")
    require(tail is not None and tail.get("mnemonic") == "RET" and tail.get("operands") == "0xc", "missing RET 0xc tail", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=1 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=1 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=1 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=1 found=1 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=1 missing=0",
        "post-xrefs.log": "Wrote 1 rows",
        "post-instructions-complete.log": "Wrote 3201 instruction rows",
        "post-context-metadata.log": "targets=11 found=11 missing=0",
        "post-context-tags.log": "ExportFunctionTagsByAddress complete: rows=11 missing=0",
        "post-decompile.log": "targets=1 dumped=1 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6098 commented_functions=5668",
        "queue-probe.log": "Commentless functions: 430",
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave844.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave844_queue_probe.log",
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
    require(quality["commentlessFunctionCount"] == 430, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(queue["priorityQueues"]["commentlessHighSignal"] == [], "high-signal queue should remain empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5668, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5668, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and normalize_address(raw_commentless.get("address", "")) == NEXT_HEAD, "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CSpawnerThng__IsSpawnTypeAllowed", "raw commentless head name mismatch", failures)

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
        WORLD_DOC,
        LOADWORLD_DOC,
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
        scripts.get("test:ghidra-cworld-load-world-wave844") == r"py -3 tools\ghidra_cworld_load_world_wave844_probe.py --check",
        "missing package script",
        failures,
    )

    require(any(row.get("task") == "Wave844 CWorld LoadWorld" for row in read_jsonl(LEDGER)), "missing Wave844 ledger row", failures)
    require(any(row.get("task") == "Wave844 CWorld LoadWorld" for row in read_jsonl(ATTEMPT_LOG)), "missing Wave844 attempt row", failures)


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
        print("Wave844 CWorld LoadWorld probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave844 CWorld LoadWorld probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
