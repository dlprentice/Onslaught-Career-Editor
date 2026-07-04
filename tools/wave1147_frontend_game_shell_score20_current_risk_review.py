#!/usr/bin/env python3
"""Validate Wave1147 frontend/game-shell score20 current-risk artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1147-frontend-game-shell-score20-current-risk-review"
FOCUSED_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-focused-candidates.json"
FOCUSED_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-focused-candidates.tsv"
RISK_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-risk-ranked-functions.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1147-frontend-game-shell-score20-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1147-frontend-game-shell-score20-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1147_frontend_game_shell_score20_current_risk_review_2026-06-05.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
MAPPED_SYSTEMS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
WAVE1108_NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
WAVE1108_READINESS = ROOT / "release" / "readiness" / "wave1108_current_risk_rank_2026-06-04.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FEPBE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FEPBEConfig.cpp" / "_index.md"
FEPCOMMON_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FEPCommon.cpp" / "_index.md"
FEPDEBRIEFING_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FEPDebriefing.cpp" / "_index.md"
DXFONT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXFont.cpp" / "_index.md"
FRONTEND_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FrontEnd.cpp" / "_index.md"
GAME_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "game.cpp" / "_index.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PROGRESS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
README = ROOT / "README.md"
AGENTS = ROOT / "AGENTS.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
TRACKING_STATE = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260605-182213_post_wave1147_frontend_game_shell_score20_current_risk_review_verified"
PRIOR_BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260605-174520_post_wave1146_mixed_engine_score20_current_risk_review_verified"

TARGETS = {
    "0x00451a40": ("FEPBEConfig__FindSelectedEntryByGlobalId", "int * __fastcall FEPBEConfig__FindSelectedEntryByGlobalId(void * list_state)"),
    "0x00452ce0": ("CFrontEnd__RenderVideoQuadScaledToWindow", "void __stdcall CFrontEnd__RenderVideoQuadScaledToWindow(float scale, int argb, float center_x, float center_y)"),
    "0x00456830": ("GlobalListNode__ClearField4AndPushGlobalList", "void * __thiscall GlobalListNode__ClearField4AndPushGlobalList(void * this)"),
    "0x004659a0": ("CDXFont__DrawTextScaledWithShadow", "int __thiscall CDXFont__DrawTextScaledWithShadow(void * this, float x, float y, uint packed_argb, short * text, uint flags, float depth_z, float x_scale, float y_scale)"),
    "0x004662a0": ("CFrontEnd__Init", "int __thiscall CFrontEnd__Init(void * this, int entry, int in_loaded_system)"),
    "0x004679e0": ("CFrontEnd__RenderPreCommonFade", "void __stdcall CFrontEnd__RenderPreCommonFade(float transition, uint argb, int destination_page)"),
    "0x0046c210": ("CGame__ctor", "void * __fastcall CGame__ctor(void * this)"),
    "0x0046c2d0": ("CGame__dtor", "void __fastcall CGame__dtor(void * this)"),
    "0x004729e0": ("CGameInterface__ResetMenuState", "void __fastcall CGameInterface__ResetMenuState(void * this)"),
    "0x00472ad0": ("CGameInterface__AdvanceMenuSelectionWithWrap", "void __fastcall CGameInterface__AdvanceMenuSelectionWithWrap(void * this)"),
}

DOC_TOKENS = (
    "Wave1147",
    "wave1147-frontend-game-shell-score20-current-risk-review",
    "316/1179 = 26.80%",
    "10 current-risk rows",
    "current focused candidates: 1178",
    "live regenerated current focused candidates: 1178",
    "remaining active focused work: 863",
    "current risk candidates: 6166",
    "frontend/game shell score20 current-risk review",
    "fresh Ghidra export",
    "one saved comment/tag correction",
    "ParticleEffectLink__PushGlobalList",
    "0x004cb040",
    "read-back verified",
    "no rename",
    "no signature change",
    "no Codex subagent",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "FEPBEConfig__FindSelectedEntryByGlobalId",
    "CFrontEnd__RenderVideoQuadScaledToWindow",
    "GlobalListNode__ClearField4AndPushGlobalList",
    "CDXFont__DrawTextScaledWithShadow",
    "CFrontEnd__Init",
    "CFrontEnd__RenderPreCommonFade",
    "CGame__ctor",
    "CGame__dtor",
    "CGameInterface__ResetMenuState",
    "CGameInterface__AdvanceMenuSelectionWithWrap",
    BACKUP,
    PRIOR_BACKUP,
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
)

OVERCLAIM_TOKENS = (
    "runtime frontend behavior proven",
    "runtime video behavior proven",
    "runtime fade behavior proven",
    "runtime font output proven",
    "runtime gameinterface behavior proven",
    "runtime cgame lifecycle proven",
    "exact layouts proven",
    "rebuild parity proven",
)


def normalize_address(address: str) -> str:
    value = (address or "").strip().lower()
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
        "pre-metadata.tsv": 10,
        "pre-tags.tsv": 10,
        "pre-xrefs.tsv": 64,
        "pre-instructions.tsv": 708,
        "pre-decompile/index.tsv": 10,
        "post-metadata.tsv": 10,
        "post-tags.tsv": 10,
        "post-xrefs.tsv": 64,
        "post-instructions.tsv": 708,
        "post-decompile/index.tsv": 10,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    pre_metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    post_metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    post_tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    post_decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs = {normalize_address(row["target_addr"]): [] for row in read_tsv(BASE / "post-xrefs.tsv")}
    for row in read_tsv(BASE / "post-xrefs.tsv"):
        xrefs.setdefault(normalize_address(row["target_addr"]), []).append(row)

    for address, (name, signature) in TARGETS.items():
        pre = pre_metadata.get(address)
        post = post_metadata.get(address)
        require(pre is not None, f"missing pre metadata for {address}", failures)
        require(post is not None, f"missing post metadata for {address}", failures)
        if post is not None:
            require(post.get("name") == name, f"name mismatch at {address}", failures)
            require(post.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(post.get("status") == "OK", f"metadata status mismatch at {address}", failures)
        dec = post_decompile.get(address)
        require(dec is not None, f"missing post decompile for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)
        require(address in xrefs, f"missing xrefs for {address}", failures)

    pre_comment = pre_metadata["0x00456830"].get("comment", "")
    post_comment = post_metadata["0x00456830"].get("comment", "")
    require("CWorldPhysicsManager__PushNodeGlobalList" in pre_comment, "pre comment did not capture stale callee wording", failures)
    for token in ("Wave1147 static read-back correction", "ParticleEffectLink__PushGlobalList", "0x004cb040", "older CWorldPhysicsManager-only callee wording"):
        require(token in post_comment, f"missing corrected comment token: {token}", failures)

    tags = set(post_tags["0x00456830"].get("tags", "").split(";"))
    for tag in ("wave1147-frontend-game-shell-score20-current-risk-review", "wave1147-readback-verified", "particle-effect-link-callee", "comment-hardened"):
        require(tag in tags, f"missing tag on 0x00456830: {tag}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 175967111 or backup.get("totalBytes") == 175967111.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff mismatch", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=1 comment_only_updated=1 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=1 skipped=0 comment_only_updated=1 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=1 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=10 found=10 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=10 missing=0",
        "post-xrefs.log": "Wrote 64 rows",
        "post-instructions.log": "Wrote 708 function-body instruction rows",
        "post-decompile.log": "targets=10 dumped=10 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6411 commented_functions=6411",
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave1147.log",
    }
    for relative, token in expected.items():
        path = aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIG:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_progress(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6411, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(quality["uncertainOwnerNameCount"] == 0, "uncertain owner count mismatch", failures)
    require(quality["helperAddressNameCount"] == 0, "helper address count mismatch", failures)
    require(quality["wrapperAddressNameCount"] == 0, "wrapper address count mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    require(len(rows) == 6411, "quality TSV row count mismatch", failures)
    require(commented == 6411, "quality TSV commented count mismatch", failures)
    require(strict_clean == 6411, "strict clean-signature count mismatch", failures)

    focused = read_json(FOCUSED_JSON)
    ranked = read_json(RISK_JSON)
    focused_rows = read_tsv(FOCUSED_TSV)
    require(focused["candidateFunctions"] == 1178, "focused candidate count mismatch", failures)
    require(ranked["candidateFunctions"] == 6166, "risk candidate count mismatch", failures)
    require(len(focused_rows) == 1178, "focused TSV row count mismatch", failures)
    target_addresses = {normalize_address(row["address"]) for row in focused_rows}
    for address in TARGETS:
        require(address in target_addresses, f"target absent from regenerated focused list: {address}", failures)

    progress = read_json(PROGRESS)
    current = progress["post100Reaudit"]["currentRiskRank"]
    require(progress["latestWave"]["tag"] == "wave1147-frontend-game-shell-score20-current-risk-review", "progress latest tag mismatch", failures)
    require(progress["latestWave"]["backup"] == BACKUP, "progress backup mismatch", failures)
    require(progress["functionQuality"]["strictCleanSignatureProxy"] == "6411/6411 = 100.00%", "progress strict proxy mismatch", failures)
    require(current["focusedReviewed"] == 316, "progress focused reviewed mismatch", failures)
    require(current["focusedReviewedPercent"] == "26.80%", "progress focused percent mismatch", failures)
    require(current["remainingFocusedAfterLatestReview"] == 863, "progress remaining mismatch", failures)
    require(current["liveFocusedCandidatesAfterLatestReview"] == 1178, "progress live focused mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = [
        NOTE,
        NOTE_MIRROR,
        READINESS,
        MAPPED_SYSTEMS,
        MAPPED_SYSTEMS_MIRROR,
        CAMPAIGN,
        WAVE1108_NOTE,
        WAVE1108_READINESS,
        BINARY_INDEX,
        RE_INDEX,
        FUNCTION_COVERAGE,
        FUNCTION_INDEX,
        PROGRESS,
        PROGRESS_MIRROR,
        README,
        AGENTS,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    owner_docs = {
        FEPBE_DOC: ("Wave1147", "wave1147-frontend-game-shell-score20-current-risk-review", "FEPBEConfig__FindSelectedEntryByGlobalId", BACKUP),
        FEPCOMMON_DOC: ("Wave1147", "wave1147-frontend-game-shell-score20-current-risk-review", "CFrontEnd__RenderVideoQuadScaledToWindow", "CFrontEnd__RenderPreCommonFade", BACKUP),
        FEPDEBRIEFING_DOC: ("Wave1147", "wave1147-frontend-game-shell-score20-current-risk-review", "GlobalListNode__ClearField4AndPushGlobalList", "ParticleEffectLink__PushGlobalList", "0x004cb040", BACKUP),
        DXFONT_DOC: ("Wave1147", "wave1147-frontend-game-shell-score20-current-risk-review", "CDXFont__DrawTextScaledWithShadow", BACKUP),
        FRONTEND_DOC: ("Wave1147", "wave1147-frontend-game-shell-score20-current-risk-review", "CFrontEnd__Init", BACKUP),
        GAME_DOC: ("Wave1147", "wave1147-frontend-game-shell-score20-current-risk-review", "CGame__ctor", "CGame__dtor", "CGameInterface__ResetMenuState", "CGameInterface__AdvanceMenuSelectionWithWrap", BACKUP),
    }
    for path, tokens in owner_docs.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    script = package.get("scripts", {}).get("test:wave1147-frontend-game-shell-score20-current-risk-review")
    require(script == r"py -3 tools\wave1147_frontend_game_shell_score20_current_risk_review.py --check", "missing package script", failures)

    attempts = read_jsonl(ATTEMPT_LOG)
    ledger = read_jsonl(LEDGER)
    require(any(row.get("attempt_id") == 20677 and row.get("task") == "Wave1147 frontend/game shell score20 current-risk review" for row in attempts), "missing Wave1147 attempt row", failures)
    require(any(row.get("task") == "Wave1147 frontend/game shell score20 current-risk review" for row in ledger), "missing Wave1147 ledger row", failures)
    tracking = read_json(TRACKING_STATE)
    require(tracking.get("next_attempt_id") == 20678, "tracking next_attempt_id mismatch", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs(failures)
    check_queue_and_progress(failures)
    check_docs(failures)

    if failures:
        print("Wave1147 frontend/game shell score20 current-risk probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1147 frontend/game shell score20 current-risk probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
