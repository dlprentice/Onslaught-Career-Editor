#!/usr/bin/env python3
"""Validate Wave1175 HelpTextDisplay current-risk read-only artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1175-helptext-display-current-risk-review"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1175-helptext-display-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1175-helptext-display-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1175_helptext_display_current_risk_review_2026-06-06.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
RANK = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
HELPTEXT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "HelpText.cpp" / "_index.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260606-082238_post_wave1175_helptext_display_current_risk_review_verified"

TARGETS = {
    "0x0047fab0": (
        "CHelpTextDisplay__ctor",
        "void * __thiscall CHelpTextDisplay__ctor(void * this)",
        ("Wave397", "zeroes the two queued-message slots", "HelpTextDisplay vtable", "CGame during restart/init setup"),
    ),
    "0x0047fb00": (
        "CHelpTextDisplay__QueueMessageWithTimestamp",
        "void __thiscall CHelpTextDisplay__QueueMessageWithTimestamp(void * this, void * message)",
        ("Wave397", "queues a message pointer", "global timestamp", "too many messages"),
    ),
    "0x0047fb50": (
        "CHelpTextDisplay__RenderQueuedMessages",
        "void __fastcall CHelpTextDisplay__RenderQueuedMessages(void * this)",
        ("Wave397", "TextLayout__WrapWideTextToFixedLines", "controller-config font state", "expires old slots"),
    ),
}

DECOMPILE_TOKENS = {
    "0x0047fab0": ("PTR_CHelpTextDisplay__scalar_deleting_dtor_005dbdf8", "return this"),
    "0x0047fb00": ("DAT_00672fd0", "CConsole__Printf", "s_ERROR__Added_too_many_messages_t_0062cc38"),
    "0x0047fb50": (
        "TextLayout__WrapWideTextToFixedLines",
        "CDXFont__DrawTextDynamic",
        "CDXFont__GetTextExtent",
        "CAREER_mControllerConfig_P1",
    ),
}

EXPECTED_XREFS = (
    ("0x0047fab0", "0x0046c769", "UNCONDITIONAL_CALL"),
    ("0x0047fb00", "0x00533b5d", "UNCONDITIONAL_CALL"),
    ("0x0047fb50", "0x00487b83", "UNCONDITIONAL_CALL"),
)

DOC_TOKENS = (
    "Wave1175",
    "wave1175-helptext-display-current-risk-review",
    "683/1179 = 57.93%",
    "3 HelpTextDisplay current-risk rows",
    "current focused candidates: 1178",
    "live regenerated current focused candidates: 1178",
    "remaining active focused work: 496",
    "current risk candidates: 6166",
    "fresh Ghidra export",
    "read-only review",
    "no mutation",
    "Codex root final judgment",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "3 xref rows",
    "169 instruction rows",
    "CHelpTextDisplay__ctor",
    "CHelpTextDisplay__QueueMessageWithTimestamp",
    "CHelpTextDisplay__RenderQueuedMessages",
    "CGame__InitRestartLoop",
    "CHud__RenderOverlayForViewpoint",
    "TextLayout__WrapWideTextToFixedLines",
    "CDXFont__DrawTextDynamic",
    "Wave397",
    "help-hive-wave397",
    "Wave1005",
    "help-text-display-review-wave1005",
    BACKUP,
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
)

OVERCLAIMS = (
    "runtime helptext behavior proven",
    "runtime hud/text rendering behavior proven",
    "exact source-body identity proven",
    "rebuild parity proven",
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


def normalize(address: str) -> str:
    value = (address or "").strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 3,
        "pre-tags.tsv": 3,
        "pre-xrefs.tsv": 3,
        "pre-instructions.tsv": 169,
        "pre-decompile/index.tsv": 3,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    tags = {normalize(row["address"]): row for row in read_tsv(BASE / "pre-tags.tsv")}
    decompile = {normalize(row["address"]): row for row in read_tsv(BASE / "pre-decompile" / "index.tsv")}
    xrefs = read_tsv(BASE / "pre-xrefs.tsv")

    for address, (name, signature, comment_tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata {address}", failures)
        if row:
            require(row.get("name") == name, f"name mismatch {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
            for token in comment_tokens:
                require(token in row.get("comment", ""), f"missing comment token {address}: {token}", failures)
        tag_row = tags.get(address)
        require(tag_row is not None and tag_row.get("status") == "OK", f"tag status mismatch {address}", failures)
        dec = decompile.get(address)
        require(
            dec is not None and dec.get("name") == name and dec.get("signature") == signature and dec.get("status") == "OK",
            f"decompile mismatch {address}",
            failures,
        )
        if dec is not None:
            decompile_path = BASE / "pre-decompile" / f"{address[2:]}_{name}.c"
            decompile_text = read_text(decompile_path)
            for token in DECOMPILE_TOKENS[address]:
                require(token in decompile_text, f"missing decompile token {address}: {token}", failures)

    for target, from_addr, ref_type in EXPECTED_XREFS:
        require(
            any(
                normalize(row.get("target_addr", "")) == target
                and normalize(row.get("from_addr", "")) == from_addr
                and row.get("ref_type") == ref_type
                for row in xrefs
            ),
            f"missing xref {target} <- {from_addr} {ref_type}",
            failures,
        )


def check_logs_backup_progress(failures: list[str]) -> None:
    expected_logs = {
        "pre-metadata.log": "targets=3 found=3 missing=0",
        "pre-tags.log": "rows=3 missing=0",
        "pre-xrefs.log": "Wrote 3 rows",
        "pre-instructions.log": "Wrote 169 function-body instruction rows",
        "pre-decompile.log": "targets=3 dumped=3 missing=0 failed=0",
    }
    for relative, token in expected_logs.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 176065415, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)

    progress = read_json(PROGRESS)
    latest = progress.get("latestWave", {})
    require(latest.get("wave") == "Wave1175 HelpTextDisplay Current-Risk Review", "latest progress wave mismatch", failures)
    require(latest.get("tag") == "wave1175-helptext-display-current-risk-review", "latest progress tag mismatch", failures)
    require(latest.get("backup") == BACKUP, "latest progress backup mismatch", failures)
    current = progress.get("post100Reaudit", {}).get("currentRiskRank", {})
    require(current.get("focusedReviewed") == 683, "current focused reviewed mismatch", failures)
    require(current.get("focusedReviewedPercent") == "57.93%", "current focused percent mismatch", failures)
    require(current.get("remainingFocusedAfterLatestReview") == 496, "remaining focused mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        NOTE,
        NOTE_MIRROR,
        READINESS,
        PROGRESS,
        MAPPED,
        CAMPAIGN,
        RANK,
        FUNCTION_COVERAGE,
        FUNCTION_INDEX,
        HELPTEXT_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1175 note mirror mismatch", failures)
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:wave1175-helptext-display-current-risk-review")
        == r"py -3 tools\wave1175_helptext_display_current_risk_review.py --check",
        "missing package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_backup_progress(failures)
    check_docs(failures)

    if failures:
        print("Wave1175 HelpTextDisplay probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1175 HelpTextDisplay probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
