#!/usr/bin/env python3
"""Validate Wave803 game slot helper read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave803-game-slot-helpers"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_game_slot_helpers_wave803_2026-05-24.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
GAME_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "game.cpp" / "_index.md"
SCRIPT_SET_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Script.cpp" / "CGame__SetSlot.md"
SCRIPT_GET_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Script.cpp" / "CGame__GetSlot.md"
ISCRIPT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "IScript.cpp.md"
MISSION_SLOT_DOC = ROOT / "reverse-engineering" / "game-assets" / "mission-slot-usage.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260524-084656_post_wave803_game_slot_helpers_verified"
NEXT_RAW_HEAD = "0x00472e50"

TARGETS = {
    "0x0046d3a0": {
        "name": "CGame__SetSlot",
        "signature": "void __thiscall CGame__SetSlot(void * this, int slot, int val)",
        "comment": ("Wave803 static read-back", "0x0062434c", "this+0x308", "IScript__SetSlot", "IScript__SetSlotSave"),
        "tags": {"cgame", "runtime-slot-bitset", "setslot", "missionscript", "comment-only", "tranche-head"},
    },
    "0x0046d410": {
        "name": "CGame__GetSlot",
        "signature": "bool __thiscall CGame__GetSlot(void * this, int slot)",
        "comment": ("Wave803 static read-back", "0x00624318", "this+0x308", "IScript__GetSlotBitValue", "returning false"),
        "tags": {"cgame", "runtime-slot-bitset", "getslot", "missionscript", "comment-only", "tranche-tail"},
    },
}

COMMON_TAGS = {
    "static-reaudit",
    "game-slot-helpers-wave803",
    "wave803-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
}

CORE_ANCHORS = (
    "Wave803 game slot helpers",
    "game-slot-helpers-wave803",
    "0x0046d3a0 CGame__SetSlot",
    "0x0046d410 CGame__GetSlot",
    "0x00472e50 CVBufTexture__DrawSpriteWithDefaultTextureFallback",
    "0 exact-undefined signatures",
    "0 param_N",
    "5574/6098 = 91.41%",
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime mission-script behavior proven",
    "runtime save/update behavior proven",
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
        "pre-metadata.tsv": 2,
        "pre-tags.tsv": 2,
        "pre-xrefs.tsv": 3,
        "pre-instructions.tsv": 170,
        "pre-decompile/index.tsv": 2,
        "post-metadata.tsv": 2,
        "post-tags.tsv": 2,
        "post-xrefs.tsv": 3,
        "post-instructions.tsv": 170,
        "post-decompile/index.tsv": 2,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    for address, expected in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata row: {address}", failures)
        if row is not None:
            require(row.get("name") == expected["name"], f"name mismatch at {address}", failures)
            require(row.get("signature") == expected["signature"], f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in expected["comment"]:
                require(token in row.get("comment", ""), f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags row: {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            required = COMMON_TAGS | set(expected["tags"])
            require(required.issubset(actual_tags), f"tags missing at {address}: {required - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index row: {address}", failures)
        if dec is not None:
            require(dec.get("name") == expected["name"], f"decompile name mismatch at {address}", failures)
            require(dec.get("signature") == expected["signature"], f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=2 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=2 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=2 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=2 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=2 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=2 found=2 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=2 missing=0",
        "post-xrefs.log": "Wrote 3 rows",
        "post-instructions.log": "Wrote 170 instruction rows",
        "post-decompile.log": "targets=2 dumped=2 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6098 commented_functions=5574",
        "queue-probe.log": "Commentless functions: 524",
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave803.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave803_queue_probe.log",
    }
    for relative, token in expected.items():
        path = aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)
    initial = read_text(BASE / "apply-dry-initial-compile-fail.log")
    require("incompatible types: void cannot be converted to boolean" in initial, "initial compile-fail artifact not preserved", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 524, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    for key in ("commentlessHighSignal", "signature", "nameConfidence"):
        require(queue["priorityQueues"].get(key) == [], f"{key} queue not empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5574, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5574, "strict clean-signature count mismatch", failures)
    require(raw is not None and raw.get("address") == NEXT_RAW_HEAD, "raw commentless head mismatch", failures)
    require(raw is not None and raw.get("name") == "CVBufTexture__DrawSpriteWithDefaultTextureFallback", "raw commentless name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 171314055, "backup byte count mismatch", failures)
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

    targeted_docs = {
        GAME_DOC: ("Wave803", "game-slot-helpers-wave803", "0x0046d3a0 CGame__SetSlot", "0x0046d410 CGame__GetSlot", BACKUP_PATH),
        SCRIPT_SET_DOC: ("Wave803", "game-slot-helpers-wave803", "0x0046d3a0 CGame__SetSlot", "0x00472e50 CVBufTexture__DrawSpriteWithDefaultTextureFallback"),
        SCRIPT_GET_DOC: ("Wave803", "game-slot-helpers-wave803", "0x0046d410 CGame__GetSlot", "0x00472e50 CVBufTexture__DrawSpriteWithDefaultTextureFallback"),
        ISCRIPT_DOC: ("Wave803", "game-slot-helpers-wave803", "0x0046d3a0 CGame__SetSlot", "0x0046d410 CGame__GetSlot"),
        MISSION_SLOT_DOC: ("Wave803", "game-slot-helpers-wave803", "0x0046d3a0 CGame__SetSlot", "0x0046d410 CGame__GetSlot"),
    }
    for path, tokens in targeted_docs.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:ghidra-game-slot-helpers-wave803") == r"py -3 tools\ghidra_game_slot_helpers_wave803_probe.py --check",
        "missing package script",
        failures,
    )
    ledger_rows = read_jsonl(LEDGER)
    attempt_rows = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave803 game slot helpers" for row in ledger_rows), "missing Wave803 ledger row", failures)
    require(any(row.get("task") == "Wave803 game slot helpers" for row in attempt_rows), "missing Wave803 attempt row", failures)


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
        print("Wave803 game-slot-helpers probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave803 game-slot-helpers probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
