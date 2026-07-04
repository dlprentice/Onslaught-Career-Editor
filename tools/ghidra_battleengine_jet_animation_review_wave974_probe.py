#!/usr/bin/env python3
"""Validate Wave974 BattleEngine jet/animation read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave974-battleengine-jet-animation-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_battleengine_jet_animation_review_wave974_2026-05-28.md"
PACKAGE_JSON = ROOT / "package.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
PLAYER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Player.cpp" / "_index.md"
JET_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "BattleEngineJetPart.cpp" / "_index.md"
BATTLE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "BattleEngine.cpp" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260528-210511_post_wave974_battleengine_jet_animation_review_verified"

CORE_TOKENS = (
    "Wave974",
    "battleengine-jet-animation-review-wave974",
    "0x004d3110 CPlayer__ReceiveButtonAction",
    "0x00410310 CBattleEngineJetPart__Thrust",
    "0x00410490 CBattleEngineJetPart__Turn",
    "0x00410670 CBattleEngineJetPart__Pitch",
    "356/1408 = 25.28%",
    "415/1467 = 28.29%",
    "6211/6211 = 100.00%",
    BACKUP_PATH,
    "function-boundary recovery",
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


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in read_text(path).splitlines() if line.strip()]


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def check_artifacts(failures: list[str]) -> None:
    counts = {
        "metadata.tsv": 6,
        "tags.tsv": 6,
        "xrefs.tsv": 9,
        "instructions.tsv": 511,
        "decompile/index.tsv": 6,
        "post-metadata.tsv": 7,
        "post-tags.tsv": 7,
        "post-xrefs.tsv": 10,
        "post-instructions.tsv": 749,
        "post-decompile/index.tsv": 7,
    }
    for relative, expected in counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {row["address"].lower(): row for row in read_tsv(BASE / "post-metadata.tsv")}
    player = metadata.get("0x004d3110")
    require(player is not None, "missing post metadata for 0x004d3110", failures)
    if player:
        require(player.get("name") == "CPlayer__ReceiveButtonAction", "player name mismatch", failures)
        require(
            player.get("signature") == "void __thiscall CPlayer__ReceiveButtonAction(void * this, void * from_controller, int button, float value)",
            f"player signature mismatch: {player.get('signature')}",
            failures,
        )
        for token in ("Player.cpp lines 283-511", "RET 0x0c", "CBattleEngineJetPart__Turn/Pitch/YawLeft/YawRight/Thrust"):
            require(token in player.get("comment", ""), f"missing player comment token: {token}", failures)

    tags = {row["address"].lower(): row for row in read_tsv(BASE / "post-tags.tsv")}
    player_tags = set(tags.get("004d3110", {}).get("tags", "").split(";"))
    for token in (
        "battleengine-jet-animation-review-wave974",
        "wave974-readback-verified",
        "function-boundary-recovered",
        "player-input",
        "jet-control",
        "source-backed",
    ):
        require(token in player_tags, f"missing player tag: {token}", failures)

    xref_text = read_text(BASE / "post-xrefs.tsv")
    for token in ("004d33c1\t004d3110\tCPlayer__ReceiveButtonAction", "004d33d6\t004d3110\tCPlayer__ReceiveButtonAction", "005de77c\t<none>\t<no_function>\tDATA"):
        require(token in xref_text, f"missing xref token: {token}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 created=0 would_create=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=1 skipped=0 created=1 would_create=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=2 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=1 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=7 found=7 missing=0",
        "post-tags.log": "rows=7 missing=0",
        "post-xrefs.log": "Wrote 10 rows",
        "post-instructions.log": "Wrote 749 function-body instruction rows",
        "post-decompile.log": "targets=7 dumped=7 missing=0 failed=0",
        "queue-log": "total_functions=6211 commented_functions=6211",
        "queue-probe": "Total functions: 6211",
    }
    aliases = {
        "queue-log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave974.log",
        "queue-probe": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave974_queue_probe.log",
    }
    for relative, token in expected.items():
        path = aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BAD:", "failed=1", "missing=1", "bad=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_backup_docs(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    require(queue.get("totalFunctions") == 6211, "queue total mismatch", failures)
    quality = queue.get("qualitySignals", {})
    require(quality.get("commentlessFunctionCount") == 0, "commentless mismatch", failures)
    require(quality.get("undefinedSignatureCount") == 0, "undefined mismatch", failures)
    require(quality.get("paramSignatureCount") == 0, "param mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(int(backup.get("fileCount", -1)) == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes", -1)) == 173771655, "backup bytes mismatch", failures)
    require(int(backup.get("diffCount", -1)) == 0, "backup diff mismatch", failures)

    for path in (NOTE, GHIDRA_REFERENCE, CAMPAIGN, FUNCTION_INDEX, PLAYER_DOC, JET_DOC, BATTLE_DOC, FUNCTION_COVERAGE, DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE):
        text = read_text(path)
        for token in CORE_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:ghidra-battleengine-jet-animation-review-wave974")
        == r"py -3 tools\ghidra_battleengine_jet_animation_review_wave974_probe.py --check",
        "missing package script",
        failures,
    )
    require(any(row.get("task") == "Wave974 BattleEngine jet animation review" for row in read_jsonl(LEDGER)), "missing ledger row", failures)
    require(any(row.get("task") == "Wave974 BattleEngine jet animation review" and row.get("attempt_id") == 20570 for row in read_jsonl(ATTEMPT_LOG)), "missing attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs(failures)
    check_queue_backup_docs(failures)

    if failures:
        print("Wave974 BattleEngine jet/animation review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave974 BattleEngine jet/animation review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
