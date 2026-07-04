#!/usr/bin/env python3
"""Validate final static re-audit closeout and system-map currentness."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "reverse-engineering" / "binary-analysis"
LORE_BIN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis"

PROGRESS = BIN / "static-reaudit-progress.json"
LEDGER = BIN / "static-reaudit-current-risk-ledger.json"
QUEUE = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
RANK_NOTE = BIN / "wave1108-current-risk-rank.md"
MAPPED_SYSTEMS = BIN / "mapped-systems.md"
QUICK_REFERENCE = ROOT / "reverse-engineering" / "quick-reference" / "_index.md"
PACKAGE_JSON = ROOT / "package.json"

STATE_FILES = [
    ROOT / "developer_agent_state.json",
    ROOT / "documentation_agent_state.json",
    ROOT / "re_orchestrator_state.json",
]

CONTRACT_DOCS = [
    BIN / "unit-battleengine-gameplay-static-contract.md",
    BIN / "hud-frontend-overlay-static-contract.md",
    BIN / "mesh-resource-render-static-contract.md",
    BIN / "texture-resource-decode-static-contract.md",
    BIN / "physics-script-static-contract.md",
    BIN / "destroyable-segments-static-contract.md",
]

STATUS_DOCS = [
    BIN / "wave1205-destroyable-segment-current-risk-review.md",
    BIN / "wave1206-console-support-current-risk-review.md",
    BIN / "wave1207-d3d-render-resource-lifecycle-current-risk-review.md",
    BIN / "wave1210-waypoint-wingman-lifecycle-current-risk-review.md",
    BIN / "wave1212-options-detail-tweak-current-risk-review.md",
    BIN / "wave1213-render-resource-lifecycle-tail-current-risk-review.md",
    BIN / "wave1217-lifecycle-cleanup-tail-current-risk-review.md",
    BIN / "wave1218-generic-shared-vfunc-thunk-tail-current-risk-review.md",
    ROOT / "release" / "readiness" / "wave1205_destroyable_segment_current_risk_review_2026-06-07.md",
    ROOT / "release" / "readiness" / "wave1206_console_support_current_risk_review_2026-06-07.md",
    ROOT / "release" / "readiness" / "wave1207_d3d_render_resource_lifecycle_current_risk_review_2026-06-07.md",
    ROOT / "release" / "readiness" / "wave1210_waypoint_wingman_lifecycle_current_risk_review_2026-06-07.md",
    ROOT / "release" / "readiness" / "wave1212_options_detail_tweak_current_risk_review_2026-06-07.md",
    ROOT / "release" / "readiness" / "wave1213_render_resource_lifecycle_tail_current_risk_review_2026-06-07.md",
    ROOT / "release" / "readiness" / "wave1217_lifecycle_cleanup_tail_current_risk_review_2026-06-07.md",
    ROOT / "release" / "readiness" / "wave1218_generic_shared_vfunc_thunk_tail_current_risk_review_2026-06-07.md",
    ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1031_recheck_2026-06-01.md",
    ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1032_recheck_2026-06-01.md",
    ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1033_recheck_2026-06-01.md",
    ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1034_recheck_2026-06-01.md",
]

WAVE1219_BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified"
CLOSEOUT_TOKEN = (
    "Wave1220 static closeout acceptance: active current-risk focused accounting is "
    "`1179/1179 = 100.00%`; remaining active focused work: 0"
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def check_core_counters(failures: list[str]) -> None:
    progress = read_json(PROGRESS)
    ledger = read_json(LEDGER)

    quality = progress["functionQuality"]
    require(quality["totalFunctions"] == 6411, "progress total function mismatch", failures)
    require(quality["commentedFunctions"] == 6411, "progress commented function mismatch", failures)
    require(quality["commentlessFunctions"] == 0, "progress commentless mismatch", failures)
    require(quality["undefinedSignatures"] == 0, "progress undefined mismatch", failures)
    require(quality["paramSignatures"] == 0, "progress param_N mismatch", failures)

    current = progress["post100Reaudit"]["currentRiskRank"]
    require(current["focusedReviewed"] == 1179, "current-risk reviewed mismatch", failures)
    require(current["focusedReviewedPercent"] == "100.00%", "current-risk percent mismatch", failures)
    require(current["remainingFocusedAfterLatestReview"] == 0, "current-risk remaining mismatch", failures)
    require(current["liveFocusedCandidatesAfterLatestReview"] == 1117, "live focused count mismatch", failures)
    require(current["completionTarget"] == "1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence", "completion target mismatch", failures)
    require(current["isWave911Reconstruction"] is False, "Wave911 reconstruction flag mismatch", failures)

    require(ledger["correctedUniqueReviewed"] == 1179, "ledger reviewed mismatch", failures)
    require(ledger["correctedUniquePercent"] == "100.00%", "ledger percent mismatch", failures)
    require(ledger["remainingUnique"] == 0, "ledger remaining mismatch", failures)
    require(ledger["liveFocusedCandidatesAfterLatestReview"] == 1117, "ledger live focused mismatch", failures)

    if QUEUE.is_file():
        queue = read_json(QUEUE)
        require(queue["status"] == "PASS", "queue status mismatch", failures)
        require(queue["totalFunctions"] == 6411, "queue total mismatch", failures)
        signals = queue["qualitySignals"]
        require(signals["commentlessFunctionCount"] == 0, "queue commentless mismatch", failures)
        require(signals["undefinedSignatureCount"] == 0, "queue undefined mismatch", failures)
        require(signals["paramSignatureCount"] == 0, "queue param_N mismatch", failures)
    else:
        require(
            quality.get("source") == "subagents/ghidra-static-reaudit/queue/current/static-reaudit-queue.json",
            "progress missing static re-audit queue provenance",
            failures,
        )


def check_current_docs(failures: list[str]) -> None:
    rank_text = read_text(RANK_NOTE)
    for token in (
        "Latest current-risk update: Wave1219",
        "Wave1108 current focused accounting is now `1179/1179 = 100.00%`",
        "remaining active focused work: 0",
        WAVE1219_BACKUP,
    ):
        require(contains_token(rank_text, token), f"wave1108 rank missing current token: {token}", failures)
    for bad in (
        "Latest current-risk update: Wave1212",
        "Wave1108 current focused accounting is now `1119/1179 = 94.91%`",
        "remaining active focused work: 60",
    ):
        require(bad not in rank_text, f"wave1108 rank stale current token: {bad}", failures)

    mapped = read_text(MAPPED_SYSTEMS)
    for token in (
        CLOSEOUT_TOKEN,
        "Static closeout acceptance",
        "unit-battleengine-gameplay-static-contract.md",
        "hud-frontend-overlay-static-contract.md",
        "destroyable-segments-static-contract.md",
        "mesh-resource-render-static-contract.md",
        "texture-resource-decode-static-contract.md",
        "physics-script-static-contract.md",
    ):
        require(contains_token(mapped, token), f"mapped systems missing token: {token}", failures)
    require("not as global static completion while the Wave1108 current-risk denominator remains below `1179/1179`" not in mapped, "mapped systems still says current-risk is below 1179/1179", failures)

    quick = read_text(QUICK_REFERENCE)
    require(CLOSEOUT_TOKEN in quick, "quick reference missing Wave1220 closeout token", failures)
    require("The current post-100 static-risk lane is Wave1154" not in quick, "quick reference still points at Wave1154 as current", failures)


def check_contract_docs(failures: list[str]) -> None:
    for path in CONTRACT_DOCS:
        text = read_text(path)
        relative = path.relative_to(ROOT)
        require(CLOSEOUT_TOKEN in text, f"{relative} missing Wave1220 closeout token", failures)
        for token in (
            "runtime",
            "exact layout",
            "source",
            "rebuild",
        ):
            require(token in text.lower(), f"{relative} missing boundary vocabulary: {token}", failures)


def check_status_docs_and_state(failures: list[str]) -> None:
    for path in STATUS_DOCS:
        text = read_text(path)
        relative = path.relative_to(ROOT)
        first_lines = "\n".join(text.splitlines()[:6]).lower()
        require("validation pending" not in first_lines, f"{relative} still has validation pending status", failures)
        require("commit and push pending" not in first_lines, f"{relative} still has commit/push pending status", failures)
        require("later validation passed" in first_lines or "validation passed" in first_lines, f"{relative} missing resolved status wording", failures)

    for path in STATE_FILES:
        text = read_text(path)
        relative = path.relative_to(ROOT)
        require("closed_pending_push" not in text, f"{relative} still has closed_pending_push phase", failures)
        require("push pending" not in text.lower(), f"{relative} still says push pending", failures)
        require("push/final branch verification remain" not in text, f"{relative} still says branch verification remains", failures)
        require(CLOSEOUT_TOKEN.replace("`", "")[:80] in text.replace("`", ""), f"{relative} missing closeout acceptance text", failures)


def check_mirrors_and_package(failures: list[str]) -> None:
    for path in [
        MAPPED_SYSTEMS,
        BIN / "static-reaudit-progress.json",
        BIN / "static-reaudit-measurement-register.md",
        BIN / "static-reaudit-accounting-guard.md",
        RANK_NOTE,
        *CONTRACT_DOCS,
    ]:
        mirror = LORE_BIN / path.name
        if path.parent.name != "binary-analysis":
            continue
        require(mirror.is_file(), f"missing mirror for {path.relative_to(ROOT)}", failures)
        require(read_text(path) == read_text(mirror), f"mirror mismatch for {path.name}", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package["scripts"].get("test:static-reaudit-final-closeout-wave1220")
        == r"py -3 tools\static_reaudit_final_closeout_wave1220.py --check",
        "missing package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_core_counters(failures)
    check_current_docs(failures)
    check_contract_docs(failures)
    check_status_docs_and_state(failures)
    check_mirrors_and_package(failures)

    if failures:
        print("Static re-audit final closeout Wave1220 probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Static re-audit final closeout Wave1220 probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
