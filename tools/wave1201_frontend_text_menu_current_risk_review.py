#!/usr/bin/env python3
"""Validate Wave1201 frontend/text/menu current-risk review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1201-frontend-text-menu-current-risk-review"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1201-frontend-text-menu-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1201-frontend-text-menu-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1201_frontend_text_menu_current_risk_review_2026-06-06.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-current-risk-ledger.json"
ACCOUNTING = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-accounting-guard.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
RANK = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER_JSONL = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPTS = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260606-235230_post_wave1201_frontend_text_menu_current_risk_review_verified"

TARGETS = {
    "0x00465a20": ("TextLayout__WrapWideTextToFixedLines", "int __stdcall TextLayout__WrapWideTextToFixedLines(short * line_buffer, short * wide_text, float max_width)"),
    "0x0046b1e0": ("FrontEndText__GetAsciiFallbackTextByToken", "short * __cdecl FrontEndText__GetAsciiFallbackTextByToken(int text_token)"),
    "0x00472d50": ("CGameInterface__VFunc_03_HandleMenuControlInput", "void __thiscall CGameInterface__VFunc_03_HandleMenuControlInput(void * this, void * control_context, int button_id, int button_context)"),
    "0x00452430": ("CFEPBriefing__TransitionNotification", "void __fastcall CFEPBriefing__TransitionNotification(void * this, int from_page)"),
    "0x00457ec0": ("CFEPDemoMain__GetMenuType", "int __cdecl CFEPDemoMain__GetMenuType(void)"),
    "0x00457ed0": ("CFEPDemoMain__GetActionCount", "int __stdcall CFEPDemoMain__GetActionCount(int menu_state)"),
    "0x00457f20": ("CFEPDemoMain__Update", "void __stdcall CFEPDemoMain__Update(int menu_state)"),
    "0x004584d0": ("CFEPDevelopment__Render", "void __thiscall CFEPDevelopment__Render(void * this, float transition, int dest)"),
    "0x00458ce0": ("CFEPDevelopment__ResolveActiveStorageDevice", "void __thiscall CFEPDevelopment__ResolveActiveStorageDevice(void * this, int unused_refresh_arg)"),
    "0x00459920": ("CFEPMultiplayerStart__SubObj8848__ctor", "void * __thiscall CFEPMultiplayerStart__SubObj8848__ctor(void * this)"),
    "0x004599a0": ("CFEPMultiplayerStart__SubObj8848__Init", "int __thiscall CFEPMultiplayerStart__SubObj8848__Init(void * this)"),
    "0x00459e50": ("CFEPMultiplayerStart__SubObj8848__RenderPreCommon", "void __stdcall CFEPMultiplayerStart__SubObj8848__RenderPreCommon(float transition, int dest)"),
    "0x00461c40": ("CFEPLoadGame__Init", "bool __thiscall CFEPLoadGame__Init(void * this)"),
    "0x004621d0": ("CFEPMain__GetMenuType", "int __cdecl CFEPMain__GetMenuType(void)"),
    "0x004621e0": ("CFEPMain__GetActionCount", "int __stdcall CFEPMain__GetActionCount(int menu_state)"),
    "0x00462b70": ("CFEPMain__RenderPreCommon", "void __stdcall CFEPMain__RenderPreCommon(float transition, int dest)"),
    "0x00462c90": ("CFEPMain__Update", "void __stdcall CFEPMain__Update(int menu_state)"),
    "0x00464620": ("CFEPSaveGame__Init", "bool __thiscall CFEPSaveGame__Init(void * this)"),
    "0x0048f540": ("CLevelBriefingLog__ctor", "void * __thiscall CLevelBriefingLog__ctor(void * this)"),
    "0x0048f5a0": ("CLevelBriefingLog__scalar_deleting_dtor", "void * __thiscall CLevelBriefingLog__scalar_deleting_dtor(void * this, byte flags)"),
    "0x004d01c0": ("CMenuItem__RestoreCompactVTable", "void __fastcall CMenuItem__RestoreCompactVTable(void * menu_item)"),
    "0x004d0490": ("CMenuItem__shared_compact_scalar_deleting_dtor", "void * __thiscall CMenuItem__shared_compact_scalar_deleting_dtor(void * this, int flags)"),
    "0x0051ad30": ("CFEPDirectory__RefreshSaveFileList", "void __thiscall CFEPDirectory__RefreshSaveFileList(void * this, int force_refresh)"),
    "0x00521c80": ("CFEPWingmen__Update", "void __thiscall CFEPWingmen__Update(void * this, int state)"),
    "0x004f2190": ("CText__GetLanguageName", "char * __fastcall CText__GetLanguageName(void * this)"),
}

COMMON_TAGS = {"static-reaudit", "comment-hardened", "retail-binary-evidence"}

DOC_TOKENS = (
    "Wave1201",
    "wave1201-frontend-text-menu-current-risk-review",
    "25 frontend/text/menu current-risk rows",
    "1042/1179 = 88.38%",
    "current focused candidates: 1141",
    "live regenerated current focused candidates: 1141",
    "remaining active focused work: 137",
    "legacy additive counter is deprecated",
    "1073/1179",
    "26 duplicate-address overcount",
    "Wave1145 arithmetic overcount: 5",
    "current risk candidates: 6166",
    "fresh Ghidra export",
    "read-only review",
    "no rename",
    "no signature change",
    "no comment change",
    "no tag change",
    "no function-boundary change",
    "no executable-byte change",
    "TextLayout__WrapWideTextToFixedLines",
    "CGameInterface__VFunc_03_HandleMenuControlInput",
    "CFEPMultiplayerStart__SubObj8848__ctor",
    "CFEPDirectory__RefreshSaveFileList",
    "CFEPWingmen__Update",
    "CText__GetLanguageName",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "78 xref rows",
    "1264 instruction rows",
    "25 decompile rows",
    BACKUP,
    "static-reaudit-current-risk-ledger.json",
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
    "rebuild-grade static contracts",
    "no noticeable difference",
)

OVERCLAIMS = (
    "runtime behavior proven",
    "runtime frontend behavior proven",
    "runtime text rendering proven",
    "visual parity proven",
    "exact layout proven",
    "exact source identity proven",
    "rebuild parity proven",
    "no-noticeable-difference parity proven",
)


def normalize_address(value: str) -> str:
    value = value.strip().lower()
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


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 25,
        "pre-tags.tsv": 25,
        "pre-xrefs.tsv": 78,
        "pre-instructions.tsv": 1264,
        "pre-decompile/index.tsv": 25,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-decompile" / "index.tsv")}
    xrefs = read_tsv(BASE / "pre-xrefs.tsv")

    for address, (name, signature) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            comment = row.get("comment", "")
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            require(comment.strip(), f"empty comment at {address}", failures)
            require("runtime" in comment.lower() or "static" in comment.lower(), f"missing static/runtime boundary at {address}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual), f"tags missing at {address}: {COMMON_TAGS - actual}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    xref_targets = {normalize_address(row["target_addr"]) for row in xrefs}
    for address in TARGETS:
        require(address in xref_targets, f"missing xref coverage for {address}", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected = {
        "pre-metadata.log": "targets=25 found=25 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=25 missing=0",
        "pre-xrefs.log": "Wrote 78 rows",
        "pre-instructions.log": "Wrote 1264 function-body instruction rows",
        "pre-decompile.log": "targets=25 dumped=25 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 176425863 or backup.get("totalBytes") == 176425863.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_progress_and_docs(failures: list[str]) -> None:
    progress = read_json(PROGRESS)
    current = progress["post100Reaudit"]["currentRiskRank"]
    require(current.get("focusedReviewed") == 1042, "focused reviewed mismatch", failures)
    require(current.get("focusedReviewedPercent") == "88.38%", "focused reviewed percent mismatch", failures)
    require(current.get("remainingFocusedAfterLatestReview") == 137, "remaining focused mismatch", failures)
    require(current.get("liveFocusedCandidatesAfterLatestReview") == 1141, "live focused mismatch", failures)
    require(current.get("legacyAdditiveReviewedDeprecated") == 1073, "legacy additive mismatch", failures)
    require(current.get("duplicateAddressOvercountCorrected") == 26, "duplicate overcount mismatch", failures)
    require(current.get("wave1145ArithmeticOvercountCorrected") == 5, "Wave1145 overcount mismatch", failures)

    ledger = read_json(LEDGER)
    require(ledger.get("correctedUniqueReviewed") == 1042, "ledger unique mismatch", failures)
    require(ledger.get("correctedUniquePercent") == "88.38%", "ledger percent mismatch", failures)
    require(ledger.get("remainingUnique") == 137, "ledger remaining mismatch", failures)
    require(ledger.get("countedRowsThroughWave1201") == 1068, "ledger counted row mismatch", failures)

    prose_docs = [
        NOTE,
        NOTE_MIRROR,
        READINESS,
        MAPPED,
        CAMPAIGN,
        RANK,
        BINARY_INDEX,
        RE_INDEX,
        FUNCTION_COVERAGE,
        FUNCTION_INDEX,
        BACKLOG,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
        PROGRESS,
        LEDGER,
        ACCOUNTING,
    ]
    for path in prose_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIMS:
            require(bad not in text.lower(), f"overclaim in {path.relative_to(ROOT)}: {bad}", failures)

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1201 note mirror mismatch", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:wave1201-frontend-text-menu-current-risk-review")
        == r"py -3 tools\wave1201_frontend_text_menu_current_risk_review.py --check",
        "missing package script",
        failures,
    )

    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    require(queue.get("totalFunctions") == 6411, "queue total mismatch", failures)
    require(quality.get("commentlessFunctionCount") == 0, "queue commentless mismatch", failures)
    require(quality.get("undefinedSignatureCount") == 0, "queue undefined mismatch", failures)
    require(quality.get("paramSignatureCount") == 0, "queue param_N mismatch", failures)

    task = "Wave1201 frontend text menu current-risk review"
    ledger_rows = read_jsonl(LEDGER_JSONL)
    attempt_rows = read_jsonl(ATTEMPTS)
    require(any(row.get("task") == task for row in ledger_rows), "missing Wave1201 ledger row", failures)
    require(any(row.get("task") == task and row.get("result") == "success" for row in attempt_rows), "missing Wave1201 attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_progress_and_docs(failures)

    if failures:
        print("Wave1201 frontend/text/menu current-risk review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1201 frontend/text/menu current-risk review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
