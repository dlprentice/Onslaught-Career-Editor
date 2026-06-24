#!/usr/bin/env python3
"""Validate Wave802 frontend save/multiplayer read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave802-frontend-save-multiplayer"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_frontend_save_multiplayer_wave802_2026-05-24.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
FEPSAVE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FEPSaveGame.cpp" / "_index.md"
FEPLOAD_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FEPLoadGame.cpp" / "_index.md"
FRONTEND_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FrontEnd.cpp" / "_index.md"
FEPMULTI_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FEPMultiplayerStart.cpp" / "_index.md"
DXFMV_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXFMV.cpp.md"
GAME_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "game.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260524-081932_post_wave802_frontend_save_multiplayer_verified"
NEXT_RAW_HEAD = "0x0046d3a0"

TARGETS = {
    "0x0044d390": {
        "name": "FEMessBox__Create",
        "signature": "int __thiscall FEMessBox__Create(void * this, float x, float y, float wrap_width, float text_scale, short * wide_text, void * font, int fade_start, int fade_ticks, int prompt_mode, int option_mode, int question_id)",
        "comment": ("Wave802 static read-back", "RET 0x2c", "FEPSaveGame.cpp", "FEPLoadGame.cpp", "TextLayout__WrapWideTextToFixedLines"),
        "tags": {"femessbox", "message-box-create", "name-corrected", "signature-corrected", "ret-002c", "tranche-head"},
        "xrefs": 29,
    },
    "0x00465640": {
        "name": "CFMV__PlayFullscreenWithLoadingGate",
        "signature": "int __thiscall CFMV__PlayFullscreenWithLoadingGate(void * this, char * movie_path, int force_loading_gate, int use_language_index, int vfunc_arg3, int vfunc_arg4, int vfunc_arg5, int vfunc_arg6)",
        "comment": ("Wave802 static read-back", "RET 0x1c", "CController__SetNonInteractiveSection", "g_LanguageIndex", "FEPGoodies.cpp"),
        "tags": {"cfmv", "play-fullscreen", "loading-gate", "name-corrected", "signature-corrected", "ret-001c"},
        "xrefs": 16,
    },
    "0x00465f10": {
        "name": "CFEPMultiplayerStart__ctor",
        "signature": "void * __fastcall CFEPMultiplayerStart__ctor(void * this)",
        "comment": ("Wave802 static read-back", "CFEPMultiplayerStart constructor", "CMissionScriptObjectCode__CMissionScriptObjectCode", "SubObj8848"),
        "tags": {"fepmultiplayerstart", "frontend-page", "constructor", "embedded-subobjects"},
        "xrefs": 1,
    },
    "0x004661c0": {
        "name": "DeviceObject__dtor_thunk",
        "signature": "void __thiscall DeviceObject__dtor_thunk(void * this)",
        "comment": ("Wave802 static read-back", "one-instruction DeviceObject cleanup thunk", "JMP 0x00512d50", "DAT_00889074"),
        "tags": {"deviceobject", "dtor-thunk", "jmp-thunk", "name-corrected", "signature-corrected"},
        "xrefs": 4,
    },
    "0x004661f0": {
        "name": "CFEPMultiplayerStart__CleanupMissionScriptWaitingThread",
        "signature": "void __thiscall CFEPMultiplayerStart__CleanupMissionScriptWaitingThread(void * this)",
        "comment": ("Wave802 static read-back", "adds 0x0c to ECX", "CWaitingThread__dtor_body", "CMissionScriptObjectCode"),
        "tags": {"fepmultiplayerstart", "cleanup-thunk", "missionscriptobjectcode", "waitingthread", "name-corrected", "signature-corrected"},
        "xrefs": 1,
    },
    "0x00466290": {
        "name": "CWaitingThread__dtor_thunk",
        "signature": "void __thiscall CWaitingThread__dtor_thunk(void * this)",
        "comment": ("Wave802 static read-back", "one-instruction CWaitingThread cleanup thunk", "JMP 0x00528bf0"),
        "tags": {"waitingthread", "dtor-thunk", "jmp-thunk", "name-corrected", "signature-corrected"},
        "xrefs": 2,
    },
    "0x00512d50": {
        "name": "DeviceObject__dtor_body",
        "signature": "void __thiscall DeviceObject__dtor_body(void * this)",
        "comment": ("Wave802 static read-back", "DeviceObject cleanup body", "DAT_00889074", "DAT_00889078"),
        "tags": {"deviceobject", "dtor-body", "global-list-unlink", "name-corrected", "signature-corrected"},
        "xrefs": 31,
    },
    "0x00528bf0": {
        "name": "CWaitingThread__dtor_body",
        "signature": "void __thiscall CWaitingThread__dtor_body(void * this)",
        "comment": ("Wave802 static read-back", "CWaitingThread cleanup body", "signals shutdown", "DAT_0089c01c"),
        "tags": {"waitingthread", "dtor-body", "handle-cleanup", "global-list-unlink", "name-corrected", "signature-corrected", "tranche-tail"},
        "xrefs": 7,
    },
}

COMMON_TAGS = {
    "static-reaudit",
    "frontend-save-multiplayer-wave802",
    "wave802-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
}

CORE_ANCHORS = (
    "Wave802 frontend save/multiplayer",
    "frontend-save-multiplayer-wave802",
    "0x0044d390 FEMessBox__Create",
    "0x00465640 CFMV__PlayFullscreenWithLoadingGate",
    "0x00465f10 CFEPMultiplayerStart__ctor",
    "0x004661c0 DeviceObject__dtor_thunk",
    "0x004661f0 CFEPMultiplayerStart__CleanupMissionScriptWaitingThread",
    "0x00466290 CWaitingThread__dtor_thunk",
    "0x00512d50 DeviceObject__dtor_body",
    "0x00528bf0 CWaitingThread__dtor_body",
    "0x0046d3a0 CGame__SetSlot",
    "0 exact-undefined signatures",
    "0 param_N",
    "5572/6098 = 91.37%",
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime save/load dialog behavior proven",
    "runtime fmv playback proven",
    "runtime multiplayer frontend behavior proven",
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
        "candidate-pre-metadata.tsv": 6,
        "candidate-pre-tags.tsv": 6,
        "candidate-pre-xrefs.tsv": 53,
        "candidate-pre-instructions.tsv": 222,
        "candidate-pre-decompile/index.tsv": 6,
        "candidate-full-instructions.tsv": 1566,
        "helper-metadata.tsv": 6,
        "helper-instructions.tsv": 1086,
        "helper-decompile/index.tsv": 6,
        "candidate-callsite-wide-instructions.tsv": 1665,
        "post-metadata.tsv": 8,
        "post-tags.tsv": 8,
        "post-xrefs.tsv": 91,
        "post-instructions.tsv": 2088,
        "post-decompile/index.tsv": 8,
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
        require(dec is not None, f"missing decompile row: {address}", failures)
        if dec is not None:
            require(dec.get("signature") == expected["signature"], f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    xref_rows = read_tsv(BASE / "post-xrefs.tsv")
    for address, expected in TARGETS.items():
        actual_count = sum(1 for row in xref_rows if normalize_address(row["target_addr"]) == address)
        require(actual_count == expected["xrefs"], f"xref count mismatch at {address}: {actual_count}", failures)

    fmv_text = read_text(BASE / "post-decompile" / "00465640_CFMV__PlayFullscreenWithLoadingGate.c")
    for token in ("CController__SetNonInteractiveSection", "g_LanguageIndex", "vfunc_arg6"):
        require(token in fmv_text, f"missing CFMV decompile token: {token}", failures)

    waiting_text = read_text(BASE / "post-decompile" / "00528bf0_CWaitingThread__dtor_body.c")
    for token in ("CWaitingThread__dtor_body", "WaitForSingleObject", "DAT_0089c01c"):
        require(token in waiting_text, f"missing CWaitingThread decompile token: {token}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=8 renamed=0 would_rename=7 signature_updated=7 comment_only_updated=1 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=7 skipped=0 renamed=7 would_rename=0 signature_updated=5 comment_only_updated=3 missing=0 bad=1",
        "apply-corrective-dry.log": "SUMMARY: updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0",
        "apply-corrective.log": "SUMMARY: updated=1 skipped=7 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=8 found=8 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=8 missing=0",
        "post-xrefs.log": "Wrote 91 rows",
        "post-instructions.log": "Wrote 2088 instruction rows",
        "post-decompile.log": "targets=8 dumped=8 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6098 commented_functions=5572",
        "queue-probe.log": "Commentless functions: 526",
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave802.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave802_queue_probe.log",
    }
    for relative, token in expected.items():
        path = aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        if relative == "apply.log":
            require("Read-back signature mismatch at 0x004661f0" in text, "missing expected initial apply mismatch", failures)
            require("REPORT: Save succeeded" in text, "initial apply did not save partial state", failures)
            continue
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIG:", "FAIL:", "Script not found", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 526, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(queue["priorityQueues"]["commentlessHighSignal"] == [], "high-signal queue should be empty", failures)
    require(queue["priorityQueues"]["signature"] == [], "signature queue should be empty", failures)
    require(queue["priorityQueues"]["nameConfidence"] == [], "name-confidence queue should be empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5572, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5572, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and normalize_address(raw_commentless.get("address", "")) == NEXT_RAW_HEAD, "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CGame__SetSlot", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 171314055 or backup.get("totalBytes") == 171314055.0, "backup byte count mismatch", failures)
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

    function_docs = {
        FEPSAVE_DOC: ("Wave802", "frontend-save-multiplayer-wave802", "0x0044d390 FEMessBox__Create", BACKUP_PATH),
        FEPLOAD_DOC: ("Wave802", "frontend-save-multiplayer-wave802", "0x0044d390 FEMessBox__Create", BACKUP_PATH),
        FRONTEND_DOC: ("Wave802", "frontend-save-multiplayer-wave802", "0x0044d390 FEMessBox__Create", "0x00465640 CFMV__PlayFullscreenWithLoadingGate", BACKUP_PATH),
        FEPMULTI_DOC: ("Wave802", "frontend-save-multiplayer-wave802", "0x00465f10 CFEPMultiplayerStart__ctor", "0x004661f0 CFEPMultiplayerStart__CleanupMissionScriptWaitingThread", "0x00528bf0 CWaitingThread__dtor_body", BACKUP_PATH),
        DXFMV_DOC: ("Wave802", "frontend-save-multiplayer-wave802", "0x00465640 CFMV__PlayFullscreenWithLoadingGate", BACKUP_PATH),
        GAME_DOC: ("Wave802", "frontend-save-multiplayer-wave802", "0x00465640 CFMV__PlayFullscreenWithLoadingGate", BACKUP_PATH),
    }
    for path, tokens in function_docs.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(scripts.get("test:ghidra-frontend-save-multiplayer-wave802") == r"py -3 tools\ghidra_frontend_save_multiplayer_wave802_probe.py --check", "missing package script", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave802 frontend save/multiplayer" for row in ledger_rows), "missing Wave802 ledger row", failures)
    require(any(row.get("task") == "Wave802 frontend save/multiplayer" and row.get("attempt_id") == 20457 for row in attempts), "missing Wave802 attempt row", failures)


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
        print("Wave802 frontend save/multiplayer probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave802 frontend save/multiplayer probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
