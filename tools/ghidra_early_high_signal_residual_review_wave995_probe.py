#!/usr/bin/env python3
"""Validate Wave995 early-high-signal residual read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave995-early-high-signal-residual-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_early_high_signal_residual_review_wave995_2026-05-31.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
DAMAGE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "damage.cpp" / "_index.md"
GAME_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "game.cpp" / "_index.md"
SOUNDMANAGER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "SoundManager.cpp" / "_index.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
TRACKING_STATE = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260531-073718_post_wave995_early_high_signal_residual_review_verified"

TARGETS = {
    "0x00440b70": ("CDamage__ctor_clear_head_and_init_flag", "void __fastcall CDamage__ctor_clear_head_and_init_flag(void * damage)"),
    "0x00441490": ("CDXEngine__UpdateWrappedThingPositionsAndDistance", "void __cdecl CDXEngine__UpdateWrappedThingPositionsAndDistance(float camera_x, float camera_y, float camera_z)"),
    "0x004416e0": ("CConsole__ResetStatusHistoryBuffer", "void __fastcall CConsole__ResetStatusHistoryBuffer(void * console)"),
    "0x004419e0": ("CConsole__RenderStatusHistoryOverlay", "void __fastcall CConsole__RenderStatusHistoryOverlay(void * console)"),
    "0x00441e50": ("CDebugMarkers__Shutdown", "void __fastcall CDebugMarkers__Shutdown(void * * head_ref)"),
    "0x00441ea0": ("CDebugMarkers__Render", "void __fastcall CDebugMarkers__Render(void * debug_markers)"),
    "0x004422d0": ("CDebugMarker__ctor", "void * __fastcall CDebugMarker__ctor(void * this)"),
    "0x00442380": ("CDebugMarker__UnlinkFromGlobalList", "void __fastcall CDebugMarker__UnlinkFromGlobalList(void * this)"),
}

WAVE995_TARGET = "0x00441e50"
WAVE995_TAGS = {
    "static-reaudit",
    "early-high-signal-wave364",
    "early-high-signal-residual-review-wave995",
    "wave995-readback-verified",
    "debug-marker",
    "comment-corrected",
    "allocator-corrected",
    "wave364-normalized",
    "retail-binary-evidence",
}

DOC_TOKENS = (
    "Wave995",
    "early-high-signal-residual-review-wave995",
    "0x00441e50 CDebugMarkers__Shutdown",
    "CDXMemoryManager__Free",
    "0x00549220",
    "0x009c3df0",
    "stale Wave364",
    "464/1408 = 32.95%",
    "569/1478 = 38.50%",
    "6222/6222 = 100.00%",
    BACKUP_PATH,
)

OVERCLAIMS = (
    "runtime marker behavior proven",
    "exact layout proven",
    "source identity proven",
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


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "metadata.tsv": 8,
        "tags.tsv": 8,
        "xrefs.tsv": 10,
        "instructions.tsv": 586,
        "decompile/index.tsv": 8,
        "post-metadata.tsv": 8,
        "post-tags.tsv": 8,
        "post-xrefs.tsv": 10,
        "post-instructions.tsv": 586,
        "post-decompile/index.tsv": 8,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    for address, (name, signature) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing post metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)

    target = metadata[WAVE995_TARGET]
    comment = target.get("comment", "")
    for token in (
        "Wave995 early high-signal residual review",
        "CDXMemoryManager__Free",
        "0x00549220",
        "0x009c3df0",
        "stale Wave364",
        "OID__FreeObject",
        "CGame__ShutdownRestartLoop",
        "Static retail Ghidra evidence only",
    ):
        require(token in comment, f"missing target comment token: {token}", failures)

    tag_row = tags.get(WAVE995_TARGET)
    require(tag_row is not None, "missing Wave995 tag row", failures)
    if tag_row is not None:
        actual_tags = set(tag_row.get("tags", "").split(";"))
        require(WAVE995_TAGS.issubset(actual_tags), f"Wave995 tags missing: {WAVE995_TAGS - actual_tags}", failures)

    instructions = read_tsv(BASE / "post-instructions.tsv")
    target_instructions = [row for row in instructions if normalize_address(row.get("target_addr", "")) == WAVE995_TARGET]
    require(any(row.get("instruction_addr") == "0x00441e81" and row.get("mnemonic") == "MOV" and row.get("operands") == "ECX, 0x9c3df0" for row in target_instructions), "missing memory-manager context MOV", failures)
    require(any(row.get("instruction_addr") == "0x00441e86" and row.get("mnemonic") == "CALL" and row.get("operands") == "0x00549220" for row in target_instructions), "missing CDXMemoryManager__Free call", failures)

    xrefs = read_tsv(BASE / "post-xrefs.tsv")
    expected_xrefs = {
        ("0x00441e50", "0x0046cbe4", "CGame__ShutdownRestartLoop"),
        ("0x00441ea0", "0x0053e826", "CDXEngine__Render"),
        ("0x004422d0", "0x004e1ca2", "CSoundManager__UpdateStatus"),
        ("0x00442380", "0x004e1dcd", "CSoundManager__UpdateStatus"),
        ("0x00442380", "0x004e2b5f", "CSoundEvent__DestructorBody"),
    }
    actual_xrefs = {
        (normalize_address(row.get("target_addr", "")), normalize_address(row.get("from_addr", "")), row.get("from_function", ""))
        for row in xrefs
    }
    for expected in expected_xrefs:
        require(expected in actual_xrefs, f"missing xref row: {expected}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "metadata.log": "targets=8 found=8 missing=0",
        "tags.log": "ExportFunctionTagsByAddress complete: rows=8 missing=0",
        "xrefs.log": "Wrote 10 rows",
        "instructions.log": "Wrote 586 function-body instruction rows",
        "decompile.log": "targets=8 dumped=8 missing=0 failed=0",
        "apply-dry.log": "SUMMARY: updated=0 skipped=1 comment_only_updated=1 tags_added=5 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=1 skipped=0 comment_only_updated=1 tags_added=5 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=1 comment_only_updated=0 tags_added=0 missing=0 bad=0",
        "post-metadata.log": "targets=8 found=8 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=8 missing=0",
        "post-xrefs.log": "Wrote 10 rows",
        "post-instructions.log": "Wrote 586 function-body instruction rows",
        "post-decompile.log": "targets=8 dumped=8 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6222 commented_functions=6222",
        "queue-probe.log": "Status: PASS",
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave995.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave995_queue_probe.log",
    }
    for relative, token in expected.items():
        path = aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIG:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)
        if relative in {"apply-dry.log", "apply.log", "apply-final-dry.log"}:
            require("REPORT: Save succeeded" in text, f"missing save report in {relative}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    require(queue.get("totalFunctions") == 6222, "queue total mismatch", failures)
    require(quality.get("commentlessFunctionCount") == 0, "commentless count mismatch", failures)
    require(quality.get("undefinedSignatureCount") == 0, "undefined count mismatch", failures)
    require(quality.get("paramSignatureCount") == 0, "param_N count mismatch", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes", 0)) == 173869959, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = [
        NOTE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        DAMAGE_DOC,
        GAME_DOC,
        SOUNDMANAGER_DOC,
        BACKLOG,
        TRACKING_STATE,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-early-high-signal-residual-review-wave995")
        == r"py -3 tools\ghidra_early_high_signal_residual_review_wave995_probe.py --check",
        "missing package Wave995 script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave995-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 995 --check",
        "missing package Wave995 recheck script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave995 early high-signal residual review" for row in ledger_rows), "missing Wave995 ledger row", failures)
    require(any(row.get("task") == "Wave995 early high-signal residual review" and row.get("attempt_id") == 20581 for row in attempts), "missing Wave995 attempt row", failures)


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
        print("Wave995 early-high-signal residual review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave995 early-high-signal residual review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
