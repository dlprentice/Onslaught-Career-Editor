#!/usr/bin/env python3
"""Validate Wave1011 round vtable-boundary recovery artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1011-battleengine-rearm-orphan-caller-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_round_vtable_boundary_review_wave1011_2026-05-31.md"
RECHECK_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1011_recheck_2026-05-31.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
ROUND_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Round.cpp" / "_index.md"
COLLISION_ROUND_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "CollisionSeekingRound.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260531-172337_post_wave1011_round_vtable_boundary_verified"

TARGETS = {
    "0x004d8ac0": ("VFuncSlot_16_004d8ac0", "double __fastcall VFuncSlot_16_004d8ac0(void * this)"),
    "0x004d8ae0": (
        "VFuncSlot_39_004d8ae0",
        "void __thiscall VFuncSlot_39_004d8ae0(void * this, void * other_thing, void * collision_report)",
    ),
}

TARGET_TAGS = {
    "0x004d8ac0": {
        "static-reaudit",
        "round-vtable-boundary-wave1011",
        "wave1011-readback-verified",
        "retail-binary-evidence",
        "function-boundary-recovered",
        "signature-hardened",
        "comment-hardened",
        "round",
        "shared-vfunc",
        "vtable-slot-16",
        "config-scalar",
    },
    "0x004d8ae0": {
        "static-reaudit",
        "round-vtable-boundary-wave1011",
        "wave1011-readback-verified",
        "retail-binary-evidence",
        "function-boundary-recovered",
        "signature-hardened",
        "comment-hardened",
        "round",
        "shared-vfunc",
        "vtable-slot-39",
        "hit-related",
        "impact-sound",
        "rearm-bridge",
        "event-scheduling",
    },
}

DOC_TOKENS = (
    "Wave1011",
    "round-vtable-boundary-wave1011",
    "0x004d8ac0 VFuncSlot_16_004d8ac0",
    "0x004d8ae0 VFuncSlot_39_004d8ae0",
    "0x0040ac50 CBattleEngine__Rearm",
    "0x004d8dc0 VFuncSlot_02_004d8dc0",
    "0x004d8e40",
    "505/1408 = 35.87%",
    "705/1491 = 47.28%",
    "409/500 = 81.80%",
    "6236/6236 = 100.00%",
    BACKUP_PATH,
)

OVERCLAIMS = (
    "runtime behavior proven",
    "runtime projectile behavior proven",
    "runtime collision behavior proven",
    "exact source-body identity proven",
    "exact layout proven",
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


def contains_token(text: str, token: str) -> bool:
    return (
        token in text
        or token.replace("\\", "\\\\") in text
        or token.replace("\\", "\\\\\\\\") in text
        or token.replace("\\\\", "\\") in text.replace("\\\\\\\\", "\\").replace("\\\\", "\\")
    )


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "metadata.tsv": 4,
        "xrefs.tsv": 5,
        "raw-caller-around.tsv": 145,
        "wide-caller-around.tsv": 644,
        "boundary-probe-around.tsv": 1687,
        "pre-metadata.tsv": 7,
        "pre-xrefs.tsv": 11,
        "body-function-instructions.tsv": 69,
        "post-metadata.tsv": 7,
        "post-tags.tsv": 2,
        "post-xrefs.tsv": 11,
        "post-body-instructions.tsv": 234,
        "post-decompile/index.tsv": 2,
    }
    for relative, expected in expected_counts.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == expected, f"{relative} row count {actual} != {expected}", failures)

    metadata = read_tsv(BASE / "post-metadata.tsv")
    tags = read_tsv(BASE / "post-tags.tsv")
    decompile_index = read_tsv(BASE / "post-decompile" / "index.tsv")
    xrefs = read_tsv(BASE / "post-xrefs.tsv")

    for address, (name, signature) in TARGETS.items():
        row = row_by_address(metadata, address)
        require(row is not None, f"post metadata missing {address}", failures)
        if row:
            require(row.get("name") == name, f"metadata name mismatch {address}", failures)
            require(row.get("signature") == signature, f"metadata signature mismatch {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
            comment = row.get("comment", "")
            for token in ("Wave1011 round vtable-boundary recovery", "Static retail Ghidra evidence only"):
                require(token in comment, f"comment missing token {address}: {token}", failures)

        dec = row_by_address(decompile_index, address)
        require(dec is not None, f"post decompile missing {address}", failures)
        if dec:
            require(dec.get("name") == name, f"decompile name mismatch {address}", failures)
            require(dec.get("signature") == signature, f"decompile signature mismatch {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch {address}", failures)

        tag_row = row_by_address(tags, address)
        require(tag_row is not None, f"post tags missing {address}", failures)
        if tag_row:
            actual_tags = set(filter(None, tag_row.get("tags", "").split(";")))
            missing = TARGET_TAGS[address] - actual_tags
            require(not missing, f"tags missing at {address}: {sorted(missing)}", failures)

    expected_xrefs = {
        ("0x0040ac50", "0x004d8d07", "UNCONDITIONAL_CALL"),
        ("0x004d8ac0", "0x005de86c", "DATA"),
        ("0x004d8ac0", "0x005e3be4", "DATA"),
        ("0x004d8ae0", "0x005de8c8", "DATA"),
        ("0x004d8ae0", "0x005e3c40", "DATA"),
        ("0x004d8dc0", "0x005de834", "DATA"),
        ("0x004d8dc0", "0x005e3bac", "DATA"),
        ("0x004d8e40", "0x005de934", "DATA"),
        ("0x004d8e40", "0x005e3cac", "DATA"),
    }
    actual_xrefs = {
        (normalize_address(row.get("target_addr", "")), normalize_address(row.get("from_addr", "")), row.get("ref_type", ""))
        for row in xrefs
        if row.get("ref_type")
    }
    for expected in expected_xrefs:
        require(expected in actual_xrefs, f"missing post xref {expected}", failures)

    deferred = row_by_address(metadata, "0x004d8e40")
    require(deferred is not None and deferred.get("status") == "MISSING", "deferred 0x004d8e40 status mismatch", failures)


def check_logs_queue_backup(failures: list[str]) -> None:
    expected_log_tokens = {
        "metadata.log": "targets=4 found=2 missing=2",
        "xrefs.log": "Wrote 5 rows",
        "raw-caller-around.log": "Wrote 145 instruction rows",
        "wide-caller-around.log": "Wrote 644 instruction rows",
        "boundary-probe-around.log": "Wrote 1687 instruction rows",
        "pre-metadata.log": "targets=7 found=2 missing=5",
        "pre-xrefs.log": "Wrote 11 rows",
        "body-function-instructions.log": "Wrote 69 function-body instruction rows",
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 created=0 would_create=2 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=2 skipped=0 created=2 would_create=0 renamed=0 would_rename=0 signature_updated=2 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=2 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=7 found=4 missing=3",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=2 missing=0",
        "post-xrefs.log": "Wrote 11 rows",
        "post-body-instructions.log": "Wrote 234 function-body instruction rows",
        "post-decompile.log": "targets=2 dumped=2 missing=0 failed=0",
    }
    expected_missing_logs = {"metadata.log", "pre-metadata.log", "post-metadata.log"}
    for relative, token in expected_log_tokens.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR", "BADNAME", "FAIL:", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)
        if relative not in expected_missing_logs:
            require("missing=1" not in text, f"unexpected missing=1 in {relative}", failures)

    queue_log = read_text(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave1011.log")
    require("total_functions=6236 commented_functions=6236" in queue_log, "quality-refresh token missing", failures)
    queue_probe = read_text(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave1011_queue_probe.log")
    require("Status: PASS" in queue_probe, "queue probe PASS token missing", failures)
    require("Commentless functions: 0" in queue_probe, "queue probe commentless token missing", failures)

    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    require(queue.get("status") == "PASS", "queue status mismatch", failures)
    require(queue.get("totalFunctions") == 6236, "queue total mismatch", failures)
    require(quality.get("commentlessFunctionCount") == 0, "queue commentless mismatch", failures)
    require(quality.get("undefinedSignatureCount") == 0, "queue undefined mismatch", failures)
    require(quality.get("paramSignatureCount") == 0, "queue param_N mismatch", failures)
    require(len(read_tsv(QUEUE_TSV)) == 6236, "queue TSV row count mismatch", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 173935495 or backup.get("totalBytes") == 173935495.0, "backup byte count mismatch", failures)
    for key in ("missingCount", "extraCount", "diffCount", "hashDiffCount"):
        require(backup.get(key) == 0, f"backup {key} mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = (
        NOTE,
        RECHECK_NOTE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        BACKLOG,
        ROUND_DOC,
        COLLISION_ROUND_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    )
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIMS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-round-vtable-boundary-review-wave1011")
        == r"py -3 tools\ghidra_round_vtable_boundary_review_wave1011_probe.py --check",
        "missing Wave1011 package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1011-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1011 --check",
        "missing Wave1011 aggregate recheck script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1011 round vtable boundary review" for row in ledger_rows), "missing Wave1011 ledger row", failures)
    require(
        any(row.get("task") == "Wave1011 round vtable boundary review" and row.get("attempt_id") == 20593 for row in attempts),
        "missing Wave1011 attempt row",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_queue_backup(failures)
    check_docs(failures)
    if failures:
        print("Wave1011 round vtable-boundary review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1011 round vtable-boundary review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
