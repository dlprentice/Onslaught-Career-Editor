#!/usr/bin/env python3
"""Validate Wave1134 console current-risk review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

import wave1108_current_risk_rank


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1134-console-current-risk-review"
FOCUSED_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-focused-candidates.tsv"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1134-console-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1134-console-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1134_console_current_risk_review_2026-06-05.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
MAPPED_SYSTEMS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
CONSOLE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "console.cpp" / "_index.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PROGRESS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260605-104845_post_wave1134_console_current_risk_review_verified"
PRIOR_BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260605-100620_post_wave1133_feature_pickup_current_risk_review_verified"

TARGETS = {
    "0x00429ef0": (
        "CConsole__RegisterBuiltinCommands",
        "void __fastcall CConsole__RegisterBuiltinCommands(void * this)",
        ("built-in console commands", "cg_consolealpha", "callback"),
        (("0x0046c385", "CGame__Init", "UNCONDITIONAL_CALL"),),
        (
            "CConsole__FindCommandByName",
            "CDXMemoryManager__Alloc",
            "s_ShowCmds_00624fd8",
            "s_ShowVars_00624fa8",
            "s_ListBinds_00624f0c",
            "s_cg_consolealpha_00624d74",
        ),
        ("console-system", "console-wave326", "signature-hardened", "static-reaudit"),
    ),
    "0x0042a410": (
        "CConsole__ResetLayoutForWindowHeight",
        "void __fastcall CConsole__ResetLayoutForWindowHeight(void * this)",
        ("PLATFORM__GetWindowHeight", "visible line window bounds", "loading-screen stride"),
        (("0x004eff37", "CLTShell__InitializeRuntimeAndLoadCoreResources", "UNCONDITIONAL_CALL"),),
        ("PLATFORM__GetWindowHeight", "0x2388", "0x2384", "0xb3cc"),
        ("console-system", "console-wave326", "signature-hardened", "static-reaudit"),
    ),
}

CONTEXT_TARGETS = {
    "0x00429bc0": ("CConsole__Init", "void __fastcall CConsole__Init(void * this)"),
    "0x0042a540": ("CConsoleVar__GetTypeName", "void __stdcall CConsoleVar__GetTypeName(void * var, char * outTypeName)"),
    "0x004416e0": ("CConsole__ResetStatusHistoryBuffer", "void __fastcall CConsole__ResetStatusHistoryBuffer(void * console)"),
    "0x00441740": ("CConsole__Printf", "void __cdecl CConsole__Printf(void * console, char * format, ...)"),
    "0x004418a0": ("CConsole__PrintfNoNewline", "void __cdecl CConsole__PrintfNoNewline(void * console, char * format, ...)"),
    "0x004419e0": ("CConsole__RenderStatusHistoryOverlay", "void __fastcall CConsole__RenderStatusHistoryOverlay(void * console)"),
    "0x0042af80": ("CConsole__RegisterCommand", "void __thiscall CConsole__RegisterCommand(void * this, char * name, char * description, void * callback, char flags)"),
    "0x0042b040": ("CConsole__RegisterVariable", "void __thiscall CConsole__RegisterVariable(void * this, char * name, char * description, int varType, void * valuePtr, char flags1, char flags2)"),
}

DOC_TOKENS = (
    "Wave1134",
    "wave1134-console-current-risk-review",
    "186/1179 = 15.78%",
    "2 rows",
    "current focused candidates: 1178",
    "live regenerated current focused candidates: 1178",
    "remaining active focused work: 993",
    "console registration/layout cluster",
    "fresh Ghidra export",
    "read-only review",
    "no mutation",
    "0 / 0 / 0",
    BACKUP,
    PRIOR_BACKUP,
)

OVERCLAIM_TOKENS = (
    "runtime console command behavior proven",
    "runtime cvar behavior proven",
    "runtime layout behavior proven",
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


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def check_wave1108_accounting(failures: list[str]) -> None:
    counts = wave1108_current_risk_rank.generate()
    require(counts["total"] == 6410, "Wave1108 total mismatch", failures)
    require(counts["risk"] == 6165, "Wave1108 risk mismatch", failures)
    require(counts["focused"] == 1178, "Wave1108 focused mismatch", failures)
    focused = {normalize_address(row["address"]): row for row in read_tsv(FOCUSED_TSV)}
    for address in TARGETS:
        require(address in focused, f"target missing from current focused TSV: {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "pre-metadata.log": "targets=2 found=2 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=2 missing=0",
        "pre-xrefs.log": "Wrote 2 rows",
        "pre-instructions.log": "Wrote 418 function-body instruction rows",
        "pre-decompile.log": "targets=2 dumped=2 missing=0 failed=0",
        "context-metadata.log": "targets=8 found=8 missing=0",
        "context-tags.log": "ExportFunctionTagsByAddress complete: rows=8 missing=0",
        "context-xrefs.log": "Wrote 470 rows",
        "context-instructions.log": "Wrote 679 function-body instruction rows",
        "context-decompile.log": "targets=8 dumped=8 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIG:", "VERIFY_MISSING", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_exports(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 2,
        "pre-tags.tsv": 2,
        "pre-xrefs.tsv": 2,
        "pre-instructions.tsv": 418,
        "pre-decompile/index.tsv": 2,
        "context-metadata.tsv": 8,
        "context-tags.tsv": 8,
        "context-xrefs.tsv": 470,
        "context-instructions.tsv": 679,
        "context-decompile/index.tsv": 8,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)


def check_target_rows(failures: list[str]) -> None:
    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-decompile" / "index.tsv")}
    xrefs = read_tsv(BASE / "pre-xrefs.tsv")

    for address, (name, signature, comment_tokens, xref_specs, decompile_tokens, tag_tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch for {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch for {address}", failures)
            comment = row.get("comment", "").lower()
            for token in comment_tokens:
                require(token.lower() in comment, f"missing comment token for {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual = set(tag_row.get("tags", "").split(";"))
            for token in tag_tokens:
                require(token in actual, f"missing tag for {address}: {token}", failures)

        dec = decompile.get(address)
        require(dec is not None and dec.get("signature") == signature and dec.get("status") == "OK", f"decompile mismatch for {address}", failures)
        decompile_text = read_text(BASE / "pre-decompile" / f"{address[2:]}_{name}.c")
        for token in decompile_tokens:
            require(token in decompile_text, f"missing decompile token for {address}: {token}", failures)

        for from_addr, from_function, ref_type in xref_specs:
            require(
                any(
                    normalize_address(row.get("target_addr", "")) == address
                    and normalize_address(row.get("from_addr", "")) == normalize_address(from_addr)
                    and row.get("from_function") == from_function
                    and row.get("ref_type") == ref_type
                    for row in xrefs
                ),
                f"missing xref for {address}: {(from_addr, from_function, ref_type)}",
                failures,
            )


def check_context_rows(failures: list[str]) -> None:
    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "context-metadata.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "context-decompile" / "index.tsv")}
    for address, (name, signature) in CONTEXT_TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing context metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"context name mismatch for {address}", failures)
            require(row.get("signature") == signature, f"context signature mismatch for {address}", failures)
        dec = decompile.get(address)
        require(dec is not None and dec.get("signature") == signature and dec.get("status") == "OK", f"context decompile mismatch for {address}", failures)


def check_backup(failures: list[str]) -> None:
    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 175967111, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_docs_and_state(failures: list[str]) -> None:
    core_docs = [
        NOTE,
        NOTE_MIRROR,
        READINESS,
        MAPPED_SYSTEMS,
        MAPPED_SYSTEMS_MIRROR,
        CAMPAIGN,
        BINARY_INDEX,
        RE_INDEX,
        FUNCTION_COVERAGE,
        FUNCTION_INDEX,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    address_tokens = tuple(f"{address} {target[0]}" for address, target in TARGETS.items())
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS + address_tokens:
            require(contains_token(text, token), f"missing doc token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad.lower() not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    owner_text = read_text(CONSOLE_DOC)
    for token in DOC_TOKENS + address_tokens + tuple(f"context {address} {name_sig[0]}" for address, name_sig in CONTEXT_TARGETS.items()):
        require(contains_token(owner_text, token), f"missing console owner-doc token: {token}", failures)

    progress = read_json(PROGRESS)
    mirror = read_json(PROGRESS_MIRROR)
    for label, data in (("progress", progress), ("progress mirror", mirror)):
        current = data["post100Reaudit"]["currentRiskRank"]
        require(data["latestWave"]["wave"] == "Wave1134 Console current-risk review", f"{label} latest wave mismatch", failures)
        require(data["latestWave"]["tag"] == "wave1134-console-current-risk-review", f"{label} latest tag mismatch", failures)
        require(data["latestWave"]["backup"] == BACKUP, f"{label} backup mismatch", failures)
        artifact_commit = data["latestWave"].get("artifactCommit")
        require(
            artifact_commit == "pending Wave1134 artifact commit" or bool(re.fullmatch(r"[0-9a-f]{40}", str(artifact_commit or ""))),
            f"{label} artifact commit mismatch",
            failures,
        )
        require(current["focusedReviewed"] == 186, f"{label} focused reviewed mismatch", failures)
        require(current["focusedCandidates"] == 1179, f"{label} focused denominator mismatch", failures)
        require(current["focusedReviewedPercent"] == "15.78%", f"{label} focused percent mismatch", failures)
        require(current["latestReviewTag"] == "wave1134-console-current-risk-review", f"{label} review tag mismatch", failures)
        require(current.get("liveFocusedCandidatesAfterLatestReview") == 1178, f"{label} live focused count mismatch", failures)
        require(current.get("remainingFocusedAfterLatestReview") == 993, f"{label} remaining focused count mismatch", failures)

    package = read_json(PACKAGE_JSON)
    expected_script = r"py -3 tools\wave1134_console_current_risk_review.py --check"
    require(package["scripts"].get("test:wave1134-console-current-risk-review") == expected_script, "missing package script", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_wave1108_accounting(failures)
    check_logs(failures)
    check_exports(failures)
    check_target_rows(failures)
    check_context_rows(failures)
    check_backup(failures)
    check_docs_and_state(failures)
    if failures:
        print("Wave1134 console current-risk review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1134 console current-risk review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
