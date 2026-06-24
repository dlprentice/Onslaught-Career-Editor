#!/usr/bin/env python3
"""Validate Wave991 round config bridge read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave991-round-config-bridge-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_round_config_bridge_review_wave991_2026-05-31.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
COLLISION_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "CollisionSeekingRound.cpp" / "_index.md"
PHYSICS_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "CPhysicsScriptStatements.cpp.md"
ROUND_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Round.cpp" / "_index.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
TRACKING_STATE = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260531-045300_post_wave991_round_config_bridge_review_verified"

TARGETS = {
    "0x00426150": ("CCollisionSeekingRound__Init", "void __thiscall CCollisionSeekingRound__Init(void * this, void * roundConfig)"),
    "0x00437fe0": ("CPhysicsRoundValue__SetOwnedAuxStringAt0C", "void __thiscall CPhysicsRoundValue__SetOwnedAuxStringAt0C(void * this, char * sourceString)"),
    "0x00438050": ("CPhysicsRoundValue__SetOwnedValueStringAt08", "void __thiscall CPhysicsRoundValue__SetOwnedValueStringAt08(void * this, char * sourceString)"),
    "0x00438b40": ("CRoundGridOfFear__ApplyToRoundByName", "void __thiscall CRoundGridOfFear__ApplyToRoundByName(void * this, char * roundName)"),
    "0x0042ffa0": ("CRoundStatement__Create", "void __cdecl CRoundStatement__Create(char * name)"),
    "0x00430210": ("CRoundStatement__LoadFromMemBuffer", "void __thiscall CRoundStatement__LoadFromMemBuffer(void * this, void * memBuffer)"),
    "0x00437490": ("CPhysicsScriptStatements__CreateStatementType5", "void * __cdecl CPhysicsScriptStatements__CreateStatementType5(int valueType)"),
    "0x004d8410": ("CRound__Init", "void __thiscall CRound__Init(void * this, void * init)"),
}

WAVE991_TAGS = {
    "static-reaudit",
    "round-config-bridge-review-wave991",
    "wave991-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "tag-corrected",
    "xref-verified",
    "projectile",
    "collision-seeking",
    "round-config",
}

DOC_TOKENS = (
    "Wave991",
    "round-config-bridge-review-wave991",
    "0x00426150 CCollisionSeekingRound__Init",
    "0x00437fe0 CPhysicsRoundValue__SetOwnedAuxStringAt0C",
    "0x00438050 CPhysicsRoundValue__SetOwnedValueStringAt08",
    "0x00438b40 CRoundGridOfFear__ApplyToRoundByName",
    "0x00430210 CRoundStatement__LoadFromMemBuffer",
    "0x00437490 CPhysicsScriptStatements__CreateStatementType5",
    "445/1408 = 31.61%",
    "525/1478 = 35.52%",
    "6222/6222 = 100.00%",
    BACKUP_PATH,
)

OVERCLAIMS = (
    "runtime projectile behavior proven",
    "runtime physics-script behavior proven",
    "exact layout proven",
    "source-body identity proven",
    "rebuild parity proven",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig", errors="replace").replace("\x00", "")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in read_text(path).splitlines() if line.strip()]


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def row_by_address(rows: list[dict[str, str]], address: str, field: str = "address") -> dict[str, str] | None:
    target = normalize_address(address)
    for row in rows:
        if normalize_address(row.get(field, "")) == target:
            return row
    return None


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_path_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text or token.replace("\\", "\\\\\\\\") in text


def check_exports(failures: list[str]) -> None:
    expected_counts = {
        "metadata.tsv": 8,
        "tags.tsv": 8,
        "xrefs.tsv": 12,
        "instructions.tsv": 1430,
        "decompile/index.tsv": 8,
        "post-metadata.tsv": 8,
        "post-tags.tsv": 8,
        "post-xrefs.tsv": 12,
        "post-instructions.tsv": 1430,
        "post-decompile/index.tsv": 8,
    }
    for relative, expected in expected_counts.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == expected, f"{relative} row count {actual} != {expected}", failures)

    metadata = read_tsv(BASE / "post-metadata.tsv")
    tags = read_tsv(BASE / "post-tags.tsv")
    decompile_index = read_tsv(BASE / "post-decompile" / "index.tsv")
    for address, (name, signature) in TARGETS.items():
        row = row_by_address(metadata, address)
        require(row is not None, f"metadata missing {address}", failures)
        if row:
            require(row.get("name") == name, f"metadata name mismatch {address}", failures)
            require(row.get("signature") == signature, f"metadata signature mismatch {address}", failures)
            require(row.get("comment", "").strip() != "", f"metadata comment missing {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
        dec = row_by_address(decompile_index, address)
        require(dec is not None, f"decompile missing {address}", failures)
        if dec:
            require(dec.get("name") == name, f"decompile name mismatch {address}", failures)
            require(dec.get("signature") == signature, f"decompile signature mismatch {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch {address}", failures)

    row = row_by_address(metadata, "0x00426150")
    tag_row = row_by_address(tags, "0x00426150")
    require(row is not None and "Wave991 round configuration bridge normalization" in row.get("comment", ""), "missing Wave991 comment", failures)
    require(row is not None and "tags, locals" not in row.get("comment", ""), "stale tags/locals caveat remains", failures)
    require(row is not None and "0x005d9614" in row.get("comment", ""), "missing vtable DATA ref in comment", failures)
    require(tag_row is not None, "tags missing 0x00426150", failures)
    if tag_row:
        actual_tags = set(filter(None, tag_row.get("tags", "").split(";")))
        require(WAVE991_TAGS.issubset(actual_tags), f"missing Wave991 tags: {WAVE991_TAGS - actual_tags}", failures)

    xrefs = read_tsv(BASE / "post-xrefs.tsv")
    expected_xrefs = (
        ("0x00426150", "0x004269b9", "CCollisionSeekingRound__InitWithSound"),
        ("0x00426150", "0x00426a63", "CCollisionSeekingRound__CreateEffect"),
        ("0x00426150", "0x005d9614", "<no_function>"),
        ("0x00437490", "0x00430286", "CRoundStatement__LoadFromMemBuffer"),
        ("0x00437490", "0x0043035c", "CPhysicsRoundValueList__LoadFromMemBuffer"),
        ("0x004d8410", "0x004babf6", "CMissile__Init"),
    )
    for target, source, owner in expected_xrefs:
        require(
            any(
                normalize_address(row.get("target_addr", "")) == target
                and normalize_address(row.get("from_addr", "")) == source
                and row.get("from_function") == owner
                for row in xrefs
            ),
            f"missing xref {source} -> {target} from {owner}",
            failures,
        )


def check_logs_queue_backup(failures: list[str]) -> None:
    expected_logs = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=1 comment_only_updated=1 tags_added=10 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=1 skipped=0 comment_only_updated=1 tags_added=10 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=1 comment_only_updated=0 tags_added=0 missing=0 bad=0",
        "post-metadata.log": "targets=8 found=8 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=8 missing=0",
        "post-xrefs.log": "Wrote 12 rows",
        "post-instructions.log": "targets=8 missing=0",
        "post-decompile.log": "targets=8 dumped=8 missing=0 failed=0",
    }
    for relative, token in expected_logs.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token {relative}: {token}", failures)
        for bad in ("LockException", "Script not found", "BADADDR", "BADNAME", "BADSIG", "BADCOMMENT", "BADTAGS", "FAIL:", "missing=1", "failed=1"):
            require(bad not in text, f"bad log token {relative}: {bad}", failures)

    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6222, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "queue commentless mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "queue undefined mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "queue param_N mismatch", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 173837191 or backup.get("totalBytes") == 173837191.0, "backup bytes mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = [
        NOTE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        BACKLOG,
        TRACKING_STATE,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_path_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIMS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    owner_docs = {
        COLLISION_DOC: DOC_TOKENS + ("0x004d8410 CRound__Init",),
        PHYSICS_DOC: DOC_TOKENS,
        ROUND_DOC: (
            "Wave991",
            "round-config-bridge-review-wave991",
            "0x00426150 CCollisionSeekingRound__Init",
            "0x00430210 CRoundStatement__LoadFromMemBuffer",
            "0x00437490 CPhysicsScriptStatements__CreateStatementType5",
            "0x004d8410 CRound__Init",
            "445/1408 = 31.61%",
            "525/1478 = 35.52%",
            "6222/6222 = 100.00%",
            BACKUP_PATH,
        ),
    }
    for path, tokens in owner_docs.items():
        text = read_text(path)
        for token in tokens:
            require(contains_path_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIMS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:ghidra-round-config-bridge-review-wave991")
        == r"py -3 tools\ghidra_round_config_bridge_review_wave991_probe.py --check",
        "missing package script",
        failures,
    )

    ledger = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave991 round config bridge normalization" for row in ledger), "missing Wave991 ledger row", failures)
    require(any(row.get("task") == "Wave991 round config bridge normalization" and row.get("attempt_id") == 20577 for row in attempts), "missing Wave991 attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_exports(failures)
    check_logs_queue_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave991 round config bridge probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave991 round config bridge probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
