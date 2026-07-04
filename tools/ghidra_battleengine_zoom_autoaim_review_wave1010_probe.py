#!/usr/bin/env python3
"""Validate Wave1010 BattleEngine zoom / auto-aim review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1010-battleengine-zoom-autoaim-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_battleengine_zoom_autoaim_review_wave1010_2026-05-31.md"
RECHECK_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1010_recheck_2026-05-31.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
BATTLEENGINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "BattleEngine.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260531-163000_post_wave1010_battleengine_zoom_autoaim_review_verified"

TARGETS = {
    "0x00409e80": ("CBattleEngine__AutoZoomOut", "void __thiscall CBattleEngine__AutoZoomOut(void * this)"),
    "0x00409e90": ("CBattleEngine__ZoomOut", "void __thiscall CBattleEngine__ZoomOut(void * this)"),
    "0x00409ec0": ("CBattleEngine__ZoomIn", "void __thiscall CBattleEngine__ZoomIn(void * this)"),
    "0x00409f70": ("CBattleEngine__ChangeWeapon", "void __fastcall CBattleEngine__ChangeWeapon(void * battleEngine)"),
    "0x0040ac50": ("CBattleEngine__Rearm", "void __thiscall CBattleEngine__Rearm(void * this, float inAmount)"),
    "0x0040acc0": (
        "CBattleEngine__CalcUnitOverCrossHair",
        "void * __thiscall CBattleEngine__CalcUnitOverCrossHair(void * this, void * event, int useMeshCollision, int updateReaders)",
    ),
    "0x0040b120": ("CBattleEngine__UpdateAutoAim", "void __fastcall CBattleEngine__UpdateAutoAim(void * battleEngine)"),
    "0x0040b6d0": ("CBattleEngine__HandleAutoAim", "void __thiscall CBattleEngine__HandleAutoAim(void * this, void * event)"),
    "0x0040c180": ("CBattleEngine__HandleEvent", "void __thiscall CBattleEngine__HandleEvent(void * this, void * event)"),
}

HANDLE_EVENT_TAGS = {
    "static-reaudit",
    "battleengine-weapon-autoaim-review-wave1010",
    "wave1010-readback-verified",
    "retail-binary-evidence",
    "function-boundary-recovered",
    "source-parity",
    "battleengine",
    "event-dispatch",
    "auto-aim",
    "signature-hardened",
    "comment-hardened",
}

DOC_TOKENS = (
    "Wave1010",
    "battleengine-weapon-autoaim-review-wave1010",
    "0x00409e80 CBattleEngine__AutoZoomOut",
    "0x00409e90 CBattleEngine__ZoomOut",
    "0x00409ec0 CBattleEngine__ZoomIn",
    "0x00409f70 CBattleEngine__ChangeWeapon",
    "0x0040ac50 CBattleEngine__Rearm",
    "0x0040acc0 CBattleEngine__CalcUnitOverCrossHair",
    "0x0040b120 CBattleEngine__UpdateAutoAim",
    "0x0040b6d0 CBattleEngine__HandleAutoAim",
    "0x0040c180 CBattleEngine__HandleEvent",
    "505/1408 = 35.87%",
    "701/1489 = 47.08%",
    "409/500 = 81.80%",
    "6234/6234 = 100.00%",
    BACKUP_PATH,
)

OVERCLAIMS = (
    "runtime behavior proven",
    "runtime zoom behavior proven",
    "runtime auto-aim behavior proven",
    "runtime event behavior proven",
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
        "metadata.tsv": 8,
        "tags.tsv": 8,
        "xrefs.tsv": 11,
        "instructions.tsv": 1951,
        "decompile/index.tsv": 8,
        "raw-caller-around.tsv": 196,
        "raw-handleevent-around.tsv": 546,
        "pre-boundary-metadata.tsv": 1,
        "pre-boundary-xrefs.tsv": 1,
        "vtable-slots.tsv": 192,
        "vtable-types.tsv": 4,
        "post-metadata.tsv": 9,
        "post-tags.tsv": 9,
        "post-xrefs.tsv": 12,
        "post-instructions.tsv": 2044,
        "post-decompile/index.tsv": 9,
    }
    for relative, expected in expected_counts.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == expected, f"{relative} row count {actual} != {expected}", failures)

    pre_boundary = read_tsv(BASE / "pre-boundary-metadata.tsv")
    require(pre_boundary[0].get("status") == "MISSING", "pre-boundary metadata did not show missing function", failures)
    pre_xref = read_tsv(BASE / "pre-boundary-xrefs.tsv")[0]
    require(normalize_address(pre_xref.get("target_addr", "")) == "0x0040c180", "pre-boundary xref target mismatch", failures)
    require(normalize_address(pre_xref.get("from_addr", "")) == "0x005d89c4", "pre-boundary xref source mismatch", failures)
    require(pre_xref.get("ref_type") == "DATA", "pre-boundary xref type mismatch", failures)

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
        dec = row_by_address(decompile_index, address)
        require(dec is not None, f"post decompile missing {address}", failures)
        if dec:
            require(dec.get("name") == name, f"decompile name mismatch {address}", failures)
            require(dec.get("signature") == signature, f"decompile signature mismatch {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch {address}", failures)

    handle = row_by_address(metadata, "0x0040c180")
    if handle:
        comment = handle.get("comment", "")
        for token in (
            "Wave1010 boundary recovery",
            "CBattleEngine::HandleEvent",
            "0x005d89c4",
            "0x0040c17b RET",
            "0x0040c2e0",
            "CBattleEngine__HandleAutoAim",
            "CBattleEngine__CalcUnitOverCrossHair",
            "CGenericActiveReader__SetReader",
            "Static retail Ghidra evidence only",
        ):
            require(token in comment, f"HandleEvent comment missing token: {token}", failures)

    tag_row = row_by_address(tags, "0x0040c180")
    require(tag_row is not None, "HandleEvent tags missing", failures)
    if tag_row:
        actual_tags = set(filter(None, tag_row.get("tags", "").split(";")))
        missing_tags = HANDLE_EVENT_TAGS - actual_tags
        require(not missing_tags, f"HandleEvent tags missing: {sorted(missing_tags)}", failures)
        require(tag_row.get("status") == "OK", "HandleEvent tag status mismatch", failures)

    expected_xrefs = {
        ("0x0040c180", "0x005d89c4", "DATA"),
        ("0x0040b6d0", "0x0040c2ad", "UNCONDITIONAL_CALL"),
        ("0x0040acc0", "0x0040c2c3", "UNCONDITIONAL_CALL"),
    }
    actual_xrefs = {
        (normalize_address(row.get("target_addr", "")), normalize_address(row.get("from_addr", "")), row.get("ref_type", ""))
        for row in xrefs
    }
    for expected in expected_xrefs:
        require(expected in actual_xrefs, f"missing post xref {expected}", failures)


def check_logs_queue_backup(failures: list[str]) -> None:
    expected_log_tokens = {
        "metadata.log": "targets=8 found=8 missing=0",
        "tags.log": "ExportFunctionTagsByAddress complete: rows=8 missing=0",
        "xrefs.log": "Wrote 11 rows",
        "instructions.log": "Wrote 1951 function-body instruction rows",
        "decompile.log": "targets=8 dumped=8 missing=0 failed=0",
        "raw-caller-around.log": "Wrote 196 instruction rows",
        "raw-handleevent-around.log": "Wrote 546 instruction rows",
        "pre-boundary-metadata.log": "targets=1 found=0 missing=1",
        "pre-boundary-xrefs.log": "Wrote 1 rows",
        "vtable-slots.log": "targets=4 rows=192",
        "vtable-types.log": "rows=4",
        "apply-dry.log": "SUMMARY: updated=1 skipped=0 created=0 would_create=1 renamed=0 would_rename=0 signature_updated=1 comment_updated=1 tag_updated=1 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=1 skipped=0 created=1 would_create=0 renamed=0 would_rename=0 signature_updated=1 comment_updated=1 tag_updated=1 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=1 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_updated=0 tag_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=9 found=9 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=9 missing=0",
        "post-xrefs.log": "Wrote 12 rows",
        "post-instructions.log": "Wrote 2044 function-body instruction rows",
        "post-decompile.log": "targets=9 dumped=9 missing=0 failed=0",
    }
    for relative, token in expected_log_tokens.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR", "BADNAME", "FAIL:", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)
        if relative != "pre-boundary-metadata.log":
            require("missing=1" not in text, f"unexpected missing=1 in {relative}", failures)

    queue_log = read_text(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave1010.log")
    require("total_functions=6234 commented_functions=6234" in queue_log, "quality-refresh token missing", failures)
    queue_probe = read_text(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave1010_queue_probe.log")
    require("Status: PASS" in queue_probe, "queue probe PASS token missing", failures)
    require("Commentless functions: 0" in queue_probe, "queue probe commentless token missing", failures)

    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    require(queue.get("status") == "PASS", "queue status mismatch", failures)
    require(queue.get("totalFunctions") == 6234, "queue total mismatch", failures)
    require(quality.get("commentlessFunctionCount") == 0, "queue commentless mismatch", failures)
    require(quality.get("undefinedSignatureCount") == 0, "queue undefined mismatch", failures)
    require(quality.get("paramSignatureCount") == 0, "queue param_N mismatch", failures)
    require(len(read_tsv(QUEUE_TSV)) == 6234, "queue TSV row count mismatch", failures)

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
        FUNCTION_COVERAGE,
        BACKLOG,
        BATTLEENGINE_DOC,
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
        scripts.get("test:ghidra-battleengine-zoom-autoaim-review-wave1010")
        == r"py -3 tools\ghidra_battleengine_zoom_autoaim_review_wave1010_probe.py --check",
        "missing Wave1010 package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1010-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1010 --check",
        "missing Wave1010 aggregate recheck script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1010 BattleEngine zoom auto-aim review" for row in ledger_rows), "missing Wave1010 ledger row", failures)
    require(
        any(row.get("task") == "Wave1010 BattleEngine zoom auto-aim review" and row.get("attempt_id") == 20592 for row in attempts),
        "missing Wave1010 attempt row",
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
        print("Wave1010 BattleEngine zoom auto-aim review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1010 BattleEngine zoom auto-aim review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
