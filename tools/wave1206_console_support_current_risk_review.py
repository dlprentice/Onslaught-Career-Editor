#!/usr/bin/env python3
"""Validate Wave1206 console-support current-risk review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1206-console-support-current-risk-review"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1206-console-support-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1206-console-support-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1206_console_support_current_risk_review_2026-06-07.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-current-risk-ledger.json"
ACCOUNTING = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-accounting-guard.md"
MEASUREMENT_REGISTER = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-measurement-register.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
RANK = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
OWNER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "console.cpp" / "_index.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER_JSONL = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPTS = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
README = ROOT / "README.MD"

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260607-023000_post_wave1206_console_support_current_risk_review_verified"

TARGETS = {
    "0x00429bc0": ("CConsole__Init", "void __fastcall CConsole__Init(void * this)"),
    "0x0042a540": ("CConsoleVar__GetTypeName", "void __stdcall CConsoleVar__GetTypeName(void * var, char * outTypeName)"),
    "0x0042af80": ("CConsole__RegisterCommand", "void __thiscall CConsole__RegisterCommand(void * this, char * name, char * description, void * callback, char flags)"),
    "0x0042c750": ("FatalError__ExitWithLocalizedPrefix_A", "noreturn void __stdcall FatalError__ExitWithLocalizedPrefix_A(char * message, int callerContext)"),
    "0x0042d0b0": ("FatalError__ExitWithLocalizedPrefix_B", "noreturn void __stdcall FatalError__ExitWithLocalizedPrefix_B(char * message)"),
    "0x00441740": ("CConsole__Printf", "void __cdecl CConsole__Printf(void * console, char * format, ...)"),
    "0x004418a0": ("CConsole__PrintfNoNewline", "void __cdecl CConsole__PrintfNoNewline(void * console, char * format, ...)"),
}

TAG_TOKENS = {
    "0x00429bc0": ("static-reaudit", "console-system", "console-wave326"),
    "0x0042a540": ("static-reaudit", "console-system", "console-wave326"),
    "0x0042af80": ("static-reaudit", "console-system", "console-wave326"),
    "0x0042c750": ("static-reaudit", "fatal-error", "localized-prefix", "wave998-readback-verified"),
    "0x0042d0b0": ("static-reaudit", "fatal-error", "localized-prefix", "wave998-readback-verified"),
    "0x00441740": ("static-reaudit", "console-system", "diagnostic-console-wave386", "variadic"),
    "0x004418a0": ("static-reaudit", "console-system", "diagnostic-console-wave386", "no-newline", "variadic"),
}

COMMENT_TOKENS = {
    "0x00429bc0": ("command/variable list heads", "key-name table", "runtime console behavior"),
    "0x0042a540": ("type enum at +0xa0", "DWORD", "fmatrix"),
    "0x0042af80": ("0xac-byte command node", "callback at +0xa0", "flags at +0xa4"),
    "0x0042c750": ("localization id 0xcc", "FatalError__ExitProcess", "two stack arguments"),
    "0x0042d0b0": ("single message stack argument", "mesh/resource deserialize", "FatalError__ExitProcess"),
    "0x00441740": ("700-byte stack buffer", "DebugTrace", "status/history ring"),
    "0x004418a0": ("256-byte stack buffer", "no-newline", "status/history ring"),
}

DECOMPILE_TOKENS = (
    "CConsole__InitKeyNameTable",
    "Registry__SetStringValue_HKCU",
    "s_DWORD_00625044",
    "s_string_0062503c",
    "s_float_0062502c",
    "s_fvector_00625024",
    "s_fmatrix_0062501c",
    "FatalError__ExitProcess",
    "Localization__GetStringById",
    "vsprintf",
    "DebugTrace",
    "StrCopyN",
    "fopen",
    "fprintf",
)

DOC_TOKENS = (
    "Wave1206",
    "wave1206-console-support-current-risk-review",
    "7 CConsole support current-risk rows",
    "1083/1179 = 91.86%",
    "current focused candidates: 1141",
    "live regenerated current focused candidates: 1141",
    "remaining active focused work: 96",
    "legacy additive counter is deprecated",
    "1114/1179",
    "26 duplicate-address overcount",
    "Wave1145 arithmetic overcount: 5",
    "current risk candidates: 6166",
    "fresh Ghidra export",
    "read-only review",
    "no mutation",
    "no rename",
    "no signature change",
    "no comment change",
    "no tag change",
    "no function-boundary change",
    "no executable-byte change",
    "Codex read-only consults used",
    "CConsole__Init",
    "CConsoleVar__GetTypeName",
    "CConsole__RegisterCommand",
    "FatalError__ExitWithLocalizedPrefix_A",
    "FatalError__ExitWithLocalizedPrefix_B",
    "CConsole__Printf",
    "CConsole__PrintfNoNewline",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "426 xref rows",
    "630 instruction rows",
    "7 decompile rows",
    BACKUP,
    "static-reaudit-current-risk-ledger.json",
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "continuity denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
    "rebuild-grade static contracts",
    "no noticeable difference",
)

OVERCLAIMS = (
    "runtime behavior proven",
    "runtime console behavior proven",
    "runtime fatal behavior proven",
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
        "pre-metadata.tsv": 7,
        "pre-tags.tsv": 7,
        "pre-xrefs.tsv": 426,
        "pre-instructions.tsv": 630,
        "pre-decompile/index.tsv": 7,
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
            require("runtime" in comment.lower() or "rebuild parity" in comment.lower(), f"missing runtime/rebuild boundary at {address}", failures)
            for token in COMMENT_TOKENS[address]:
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual = set(tag_row.get("tags", "").split(";"))
            for token in TAG_TOKENS[address]:
                require(token in actual, f"missing tag at {address}: {token}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    xref_targets = {normalize_address(row["target_addr"]) for row in xrefs}
    for address in TARGETS:
        require(address in xref_targets, f"missing xref coverage for {address}", failures)

    callers = {row.get("from_function", "") for row in xrefs}
    for caller in (
        "CLTShell__InitializeRuntimeAndLoadCoreResources",
        "CConsoleVarMenu__GetEntry",
        "CConsole__RegisterBuiltinCommands",
        "CGame__InitRestartLoop",
        "CSoundManager__Init",
        "CDXEngine__Init",
        "CGame__RunLevel",
        "CGame__PumpBinkVoiceSampleQueue",
        "CText__Init",
        "CTexture__FindTexture",
        "CWorldPhysicsManager__ReloadDefaultPhysicsAndBattleEngineData",
        "CMesh__Deserialize",
        "CScriptObjectCode__Run",
    ):
        require(caller in callers, f"missing xref caller: {caller}", failures)

    decompile_text = "\n".join(path.read_text(encoding="utf-8-sig") for path in (BASE / "pre-decompile").glob("*.c"))
    for token in DECOMPILE_TOKENS:
        require(token in decompile_text, f"missing decompile token: {token}", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected = {
        "pre-metadata.log": "targets=7 found=7 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=7 missing=0",
        "pre-xrefs.log": "Wrote 426 rows",
        "pre-instructions.log": "Wrote 630 function-body instruction rows",
        "pre-decompile.log": "targets=7 dumped=7 missing=0 failed=0",
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
    require(current.get("focusedReviewed") == 1083, "focused reviewed mismatch", failures)
    require(current.get("focusedReviewedPercent") == "91.86%", "focused reviewed percent mismatch", failures)
    require(current.get("remainingFocusedAfterLatestReview") == 96, "remaining focused mismatch", failures)
    require(current.get("liveFocusedCandidatesAfterLatestReview") == 1141, "live focused mismatch", failures)
    require(current.get("legacyAdditiveReviewedDeprecated") == 1114, "legacy additive mismatch", failures)
    require(current.get("duplicateAddressOvercountCorrected") == 26, "duplicate overcount mismatch", failures)
    require(current.get("wave1145ArithmeticOvercountCorrected") == 5, "Wave1145 overcount mismatch", failures)

    ledger = read_json(LEDGER)
    require(ledger.get("correctedUniqueReviewed") == 1083, "ledger unique mismatch", failures)
    require(ledger.get("correctedUniquePercent") == "91.86%", "ledger percent mismatch", failures)
    require(ledger.get("remainingUnique") == 96, "ledger remaining mismatch", failures)
    require(ledger.get("countedRowsThroughWave1206") == 1109, "ledger counted row mismatch", failures)

    prose_docs = [
        NOTE,
        NOTE_MIRROR,
        READINESS,
        MAPPED,
        CAMPAIGN,
        RANK,
        BINARY_INDEX,
        RE_INDEX,
        BACKLOG,
        OWNER_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
        PROGRESS,
        LEDGER,
        ACCOUNTING,
        MEASUREMENT_REGISTER,
    ]
    for path in prose_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIMS:
            require(bad not in text.lower(), f"overclaim in {path.relative_to(ROOT)}: {bad}", failures)

    readme_text = read_text(README)
    require("static-reaudit-measurement-register.md" in readme_text, "README missing measurement-register pointer", failures)
    for bad in ("Current static snapshot after Wave", "Latest completed backup:", "/1179"):
        require(bad not in readme_text, f"README still duplicates active static metric: {bad}", failures)

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1206 note mirror mismatch", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:wave1206-console-support-current-risk-review")
        == r"py -3 tools\wave1206_console_support_current_risk_review.py --check",
        "missing package script",
        failures,
    )

    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    require(queue.get("totalFunctions") == 6411, "queue total mismatch", failures)
    require(quality.get("commentlessFunctionCount") == 0, "queue commentless mismatch", failures)
    require(quality.get("undefinedSignatureCount") == 0, "queue undefined mismatch", failures)
    require(quality.get("paramSignatureCount") == 0, "queue param_N mismatch", failures)

    task = "Wave1206 console support current-risk review"
    ledger_rows = read_jsonl(LEDGER_JSONL)
    attempt_rows = read_jsonl(ATTEMPTS)
    require(any(row.get("task") == task for row in ledger_rows), "missing Wave1206 ledger row", failures)
    require(any(row.get("task") == task and row.get("result") == "success" for row in attempt_rows), "missing Wave1206 attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_progress_and_docs(failures)

    if failures:
        print("Wave1206 console-support current-risk review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1206 console-support current-risk review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
