#!/usr/bin/env python3
"""Validate Wave1091 credits renderer review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1091-credits-renderer-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_credits_renderer_review_wave1091_2026-06-04.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1091_recheck_2026-06-04.md"
PACKAGE_JSON = ROOT / "package.json"
PROGRESS_JSON = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
CREDITS_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Credits.cpp" / "_index.md"
FEPCREDITS_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FEPCredits.cpp" / "_index.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
README = ROOT / "README.MD"
CAPABILITIES = ROOT / "CURRENT_CAPABILITIES.md"
AGENTS = ROOT / "AGENTS.md"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260604-143442_post_wave1091_credits_renderer_review_verified"
WAVE_TAG = "credits-renderer-review-wave1091"

TARGETS = {
    "0x00518bf0": (
        "CCredits__BuildDefaultEntries",
        "void CCredits__BuildDefaultEntries(void)",
        ("DAT_00896ca8", "0x00518be0", "localized text IDs"),
        ("credits-table", "startup-thunk", "localized-text"),
    ),
    "0x00519ff0": (
        "CCredits__WriteEntry_TextId",
        "void __thiscall CCredits__WriteEntry_TextId(void * this, int section, int text_id, int style)",
        ("{section,text_id,0,style}", "CCredits__BuildDefaultEntries"),
        ("credits-row-writer", "localized-text"),
    ),
    "0x0051a010": (
        "CCredits__WriteEntry_String",
        "void __thiscall CCredits__WriteEntry_String(void * this, int section, char * text, int style)",
        ("{section,-1,text_ptr,style}", "CCredits__BuildDefaultEntries"),
        ("credits-row-writer", "literal-text"),
    ),
    "0x0051a030": (
        "CCredits__RenderCredits",
        "bool __stdcall CCredits__RenderCredits(float elapsed, int alpha)",
        ("0x00472801", "0x0051a92b", "CDXFont__DrawTextDynamic"),
        ("credits-render-loop", "frontend-credits", "game-outro"),
    ),
    "0x0046d9f0": (
        "CGame__RunOutroFMV",
        "void __fastcall CGame__RunOutroFMV(void * this)",
        ("0x2e5", "800", "CGame__RollCredits"),
        ("game-outro", "credits-caller", "source-backed-context"),
    ),
    "0x004726b0": (
        "CGame__RollCredits",
        "void CGame__RollCredits(void)",
        ("0x00472801", "CCredits__RenderCredits", "0xff"),
        ("game-outro", "credits-caller", "source-backed-context"),
    ),
    "0x0051a7f0": (
        "CFEPCredits__ButtonPressed",
        "void __stdcall CFEPCredits__ButtonPressed(void * this, int button, float val)",
        ("0x005db88c", "button 0x2e", "page 0x11"),
        ("frontend-credits", "credits-page", "vtable-slot", "button-handler"),
    ),
    "0x0051a820": (
        "CFEPCredits__Process",
        "void __thiscall CFEPCredits__Process(void * this, int state)",
        ("0x005db888", "this+0x08", "prompt code 0x2e"),
        ("frontend-credits", "credits-page", "vtable-slot", "completion-flag"),
    ),
    "0x0051a880": (
        "CFEPCredits__RenderPreCommon",
        "void __stdcall CFEPCredits__RenderPreCommon(void * this, float transition, int dest)",
        ("0x005db890", "FUN_004679e0", "1.0"),
        ("frontend-credits", "credits-page", "vtable-slot", "pre-common-render"),
    ),
    "0x0051a8b0": (
        "CFEPCredits__Render",
        "void __thiscall CFEPCredits__Render(void * this, float transition, int dest)",
        ("0x005db894", "0x0051a92b", "this+0x08"),
        ("frontend-credits", "credits-page", "vtable-slot", "completion-flag"),
    ),
    "0x0051a970": (
        "CFEPCredits__TransitionNotification",
        "void __fastcall CFEPCredits__TransitionNotification(void * this, int from_page)",
        ("0x005db898", "CMusic__PlaySelection", "RET 0x4"),
        ("frontend-credits", "credits-page", "vtable-slot", "transition-notification", "credits-music", "completion-flag"),
    ),
}

PRIMARY = ("0x00518bf0", "0x00519ff0", "0x0051a010", "0x0051a030")
CONTEXT = (
    "0x0046d9f0",
    "0x004726b0",
    "0x0051a7f0",
    "0x0051a820",
    "0x0051a880",
    "0x0051a8b0",
    "0x0051a970",
)
VTABLE_SLOTS = {
    "2": "CFEPCredits__Process",
    "3": "CFEPCredits__ButtonPressed",
    "4": "CFEPCredits__RenderPreCommon",
    "5": "CFEPCredits__Render",
    "6": "CFEPCredits__TransitionNotification",
}

DOC_TOKENS = (
    "Wave1091",
    WAVE_TAG,
    "0x00518bf0 CCredits__BuildDefaultEntries",
    "0x0051a030 CCredits__RenderCredits",
    "0x004726b0 CGame__RollCredits",
    "0x0051a8b0 CFEPCredits__Render",
    "0x0051a970 CFEPCredits__TransitionNotification",
    "0x005db880",
    "0x00472801",
    "0x0051a92b",
    "DAT_00896ca8",
    "CDXFont__DrawTextDynamic",
    "CMusic__PlaySelection",
    "1545/1560 = 99.04%",
    "812/1408 = 57.67%",
    "500/500 = 100.00%",
    "6410/6410 = 100.00%",
    BACKUP_PATH,
    "comment/tag normalization",
)

OVERCLAIMS = (
    "runtime behavior proven",
    "runtime credits rendering proven",
    "runtime proof complete",
    "patch behavior proven",
    "rebuild parity proven",
    "all systems complete",
    "every system is complete",
    "fully reverse-engineered",
    "fully reverse engineered",
    "exact source-layout identity proven",
    "exact source layout identity proven",
)


def normalize_address(value: str) -> str:
    text = value.strip().lower()
    if text.startswith("0x"):
        text = text[2:]
    return "0x" + text.zfill(8)


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


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "primary-metadata.tsv": 4,
        "primary-tags.tsv": 4,
        "primary-xrefs.tsv": 88,
        "primary-instructions.tsv": 1135,
        "primary-decompile/index.tsv": 4,
        "context-metadata.tsv": 7,
        "context-tags.tsv": 7,
        "context-xrefs.tsv": 7,
        "context-instructions.tsv": 381,
        "context-decompile/index.tsv": 7,
        "around-instructions.tsv": 546,
        "vtable-slots.tsv": 9,
        "post-primary-metadata.tsv": 4,
        "post-primary-tags.tsv": 4,
        "post-primary-xrefs.tsv": 88,
        "post-primary-instructions.tsv": 1135,
        "post-primary-decompile/index.tsv": 4,
        "post-context-metadata.tsv": 7,
        "post-context-tags.tsv": 7,
        "post-context-xrefs.tsv": 7,
        "post-context-instructions.tsv": 381,
        "post-context-decompile/index.tsv": 7,
        "post-around-instructions.tsv": 546,
        "post-vtable-slots.tsv": 9,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata: dict[str, dict[str, str]] = {}
    tags: dict[str, dict[str, str]] = {}
    decompile: dict[str, dict[str, str]] = {}
    for prefix, addresses in (("post-primary", PRIMARY), ("post-context", CONTEXT)):
        metadata.update({normalize_address(row["address"]): row for row in read_tsv(BASE / f"{prefix}-metadata.tsv")})
        tags.update({normalize_address(row["address"]): row for row in read_tsv(BASE / f"{prefix}-tags.tsv")})
        decompile.update(
            {normalize_address(row["address"]): row for row in read_tsv(BASE / f"{prefix}-decompile" / "index.tsv")}
        )
        for address in addresses:
            name, signature, comment_tokens, tag_tokens = TARGETS[address]
            row = metadata.get(address)
            require(row is not None, f"missing metadata at {address}", failures)
            if row is not None:
                require(row.get("name") == name, f"name mismatch at {address}", failures)
                require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
                require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
                comment = row.get("comment", "")
                require("Wave1091 static read-back" in comment, f"missing Wave1091 comment at {address}", failures)
                for token in comment_tokens:
                    require(token in comment, f"missing comment token at {address}: {token}", failures)
                require("runtime credits presentation" in comment, f"missing boundary token at {address}", failures)

            tag_row = tags.get(address)
            require(tag_row is not None, f"missing tags at {address}", failures)
            if tag_row is not None:
                tag_text = tag_row.get("tags", "")
                for token in ("static-reaudit", WAVE_TAG, "wave1091-readback-verified", "retail-binary-evidence", "comment-hardened", "credits-renderer", *tag_tokens):
                    require(token in tag_text, f"missing tag at {address}: {token}", failures)

            dec = decompile.get(address)
            require(dec is not None, f"missing decompile at {address}", failures)
            if dec is not None:
                require(dec.get("name") == name, f"decompile name mismatch at {address}", failures)
                require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
                require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    xrefs = read_tsv(BASE / "post-primary-xrefs.tsv")
    require(any(normalize_address(row["target_addr"]) == "0x0051a030" and normalize_address(row["from_addr"]) == "0x00472801" for row in xrefs), "missing CGame__RollCredits callsite xref", failures)
    require(any(normalize_address(row["target_addr"]) == "0x0051a030" and normalize_address(row["from_addr"]) == "0x0051a92b" for row in xrefs), "missing CFEPCredits__Render callsite xref", failures)
    require(any(normalize_address(row["target_addr"]) == "0x00518bf0" and normalize_address(row["from_addr"]) == "0x00518be0" for row in xrefs), "missing startup thunk xref", failures)

    slots = read_tsv(BASE / "post-vtable-slots.tsv")
    for slot, name in VTABLE_SLOTS.items():
        row = next((candidate for candidate in slots if candidate.get("slot_index") == slot), None)
        require(row is not None, f"missing vtable slot {slot}", failures)
        if row is not None:
            require(row.get("function_name") == name, f"vtable slot {slot} mismatch: {row.get('function_name')}", failures)
            require(row.get("status") == "OK", f"vtable slot {slot} status mismatch", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=11 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=11 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=11 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=11 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=11 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-primary-metadata.log": "targets=4 found=4 missing=0",
        "post-primary-tags.log": "ExportFunctionTagsByAddress complete: rows=4 missing=0",
        "post-primary-xrefs.log": "Wrote 88 rows",
        "post-primary-instructions.log": "Wrote 1135 function-body instruction rows",
        "post-primary-decompile.log": "targets=4 dumped=4 missing=0 failed=0",
        "post-context-metadata.log": "targets=7 found=7 missing=0",
        "post-context-tags.log": "ExportFunctionTagsByAddress complete: rows=7 missing=0",
        "post-context-xrefs.log": "Wrote 7 rows",
        "post-context-instructions.log": "Wrote 381 function-body instruction rows",
        "post-context-decompile.log": "targets=7 dumped=7 missing=0 failed=0",
        "post-around-instructions.log": "targets=14 missing=0",
        "post-vtable-slots.log": "ExportVtableSlots complete: targets=1 rows=9",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR:", "BADNAME:", "BADSIG:", "BADCOMMENT:", "BADTAGS:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)
    require("REPORT: Save succeeded" in read_text(BASE / "apply.log"), "apply did not report save succeeded", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 175541127 or backup.get("totalBytes") == 175541127.0, "backup bytes mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs_and_state(failures: list[str]) -> None:
    core_docs = [
        NOTE,
        AGGREGATE_NOTE,
        PROGRESS_JSON,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        CREDITS_DOC,
        FEPCREDITS_DOC,
        BACKLOG,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
        README,
        CAPABILITIES,
        AGENTS,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing doc token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    progress = read_json(PROGRESS_JSON)
    require(progress["latestWave"]["wave"] == "Wave1091 credits renderer review", "progress latest wave mismatch", failures)
    require(progress["latestWave"]["status"] in {"validated_pending_commit", "committed"}, "progress status mismatch", failures)
    require(progress["latestWave"]["backup"] == BACKUP_PATH, "progress backup mismatch", failures)
    require(progress["functionQuality"]["totalFunctions"] == 6410, "progress total mismatch", failures)
    require(progress["post100Reaudit"]["expandedStaticSurface"]["completed"] == 1545, "expanded count mismatch", failures)
    require(progress["post100Reaudit"]["expandedStaticSurface"]["percent"] == "99.04%", "expanded percent mismatch", failures)
    require(progress["post100Reaudit"]["wave911Focused"]["completed"] == 812, "wave911 focused mismatch", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(scripts.get("test:ghidra-credits-renderer-review-wave1091") == r"py -3 tools\ghidra_credits_renderer_review_wave1091_probe.py --check", "missing focused package script", failures)
    require(scripts.get("test:ghidra-wave900-plus-through-wave1091-recheck") == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1091 --check", "missing aggregate package script", failures)

    ledger = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1091 credits renderer review" for row in ledger), "missing Wave1091 ledger row", failures)
    require(any(row.get("task") == "Wave1091 credits renderer review" and row.get("attempt_id") == 20671 for row in attempts), "missing Wave1091 attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_docs_and_state(failures)

    if failures:
        print("Wave1091 credits renderer review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1091 credits renderer review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
