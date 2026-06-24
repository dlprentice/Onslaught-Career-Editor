#!/usr/bin/env python3
"""Validate Wave1148 BattleEngine/walker-control current-risk artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1148-battleengine-walker-control-score20-current-risk-review"
FOCUSED_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-focused-candidates.json"
RISK_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-risk-ranked-functions.json"
FOCUSED_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-focused-candidates.tsv"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1148-battleengine-walker-control-score20-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1148-battleengine-walker-control-score20-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1148_battleengine_walker_control_score20_current_risk_review_2026-06-05.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
MAPPED_SYSTEMS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
WAVE1108_NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
WAVE1108_READINESS = ROOT / "release" / "readiness" / "wave1108_current_risk_rank_2026-06-04.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
BATTLEENGINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "BattleEngine.cpp" / "_index.md"
WALKER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "BattleEngineWalkerPart.cpp" / "_index.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PROGRESS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
README = ROOT / "README.md"
AGENTS = ROOT / "AGENTS.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"G:\GhidraBackups\BEA_20260605-185756_post_wave1148_battleengine_walker_control_score20_current_risk_review_verified"
PRIOR_BACKUP = r"G:\GhidraBackups\BEA_20260605-182213_post_wave1147_frontend_game_shell_score20_current_risk_review_verified"

TARGETS = {
    "0x00409e80": ("CBattleEngine__AutoZoomOut", "void __thiscall CBattleEngine__AutoZoomOut(void * this)", ("MAX_ZOOM_OUT", "+0x2cc")),
    "0x0040a580": ("CBattleEngine__Morph", "void __fastcall CBattleEngine__Morph(void * battleEngine)", ("Morph", "GetIsDoingSpecialWalkerMove", "Runtime behavior")),
    "0x0040ac50": ("CBattleEngine__Rearm", "void __thiscall CBattleEngine__Rearm(void * this, float inAmount)", ("Rearm", "inAmount", "clamping")),
    "0x0040acc0": ("CBattleEngine__CalcUnitOverCrossHair", "void * __thiscall CBattleEngine__CalcUnitOverCrossHair(void * this, void * event, int useMeshCollision, int updateReaders)", ("CalcUnitOverCrossHair", "0x1772")),
    "0x0040b120": ("CBattleEngine__UpdateAutoAim", "void __fastcall CBattleEngine__UpdateAutoAim(void * battleEngine)", ("UpdateAutoAim", "AngleDifference")),
    "0x0040dcc0": ("CBattleEngine__ClearFlag58CAndMorphIfState3", "void __thiscall CBattleEngine__ClearFlag58CAndMorphIfState3(void * this)", ("+0x58c", "CBattleEngine__Morph")),
    "0x0040de40": ("CBattleEngine__AugmentWeapon", "void __thiscall CBattleEngine__AugmentWeapon(void * this)", ("AugmentWeapon", "MAX_AUG_VALUE", "hud_weapon_augmented")),
    "0x0040eeb0": ("CBattleEngine__FinishedPlayingCurrentAnimation", "int __thiscall CBattleEngine__FinishedPlayingCurrentAnimation(void * this)", ("FinishedPlayingCurrentAnimation", "flytowalk", "walktofly")),
    "0x0040ef20": ("CBattleEngine__GroundParticleEffect", "void __thiscall CBattleEngine__GroundParticleEffect(void * this)", ("GroundParticleEffect", "water", "terrain")),
    "0x00412bc0": ("CBattleEngineWalkerPart__ctor", "void * __thiscall CBattleEngineWalkerPart__ctor(void * this, void * mainPart)", ("constructor", "ResetConfiguration", "g_dash_")),
    "0x004135d0": ("CBattleEngineWalkerPart__GetIsDoingSpecialWalkerMove", "int __thiscall CBattleEngineWalkerPart__GetIsDoingSpecialWalkerMove(void * this)", ("GetIsDoingSpecialWalkerMove", "+0x44")),
    "0x004135e0": ("CBattleEngineWalkerPart__ActivateLandingJets", "void __thiscall CBattleEngineWalkerPart__ActivateLandingJets(void * this)", ("ActivateLandingJets", "+0x638")),
    "0x00414030": ("CBattleEngineWalkerPart__GetCurrentWeapon", "void * __thiscall CBattleEngineWalkerPart__GetCurrentWeapon(void * this)", ("GetCurrentWeapon", "primary/augmented/fallback")),
}

DOC_TOKENS = (
    "Wave1148",
    "wave1148-battleengine-walker-control-score20-current-risk-review",
    "329/1179 = 27.91%",
    "13 current-risk rows",
    "current focused candidates: 1178",
    "live regenerated current focused candidates: 1178",
    "remaining active focused work: 850",
    "current risk candidates: 6166",
    "BattleEngine/walker-control score20 current-risk review",
    "fresh Ghidra export",
    "BattleEngine zoom/morph/rearm/crosshair/auto-aim/augment/transition/ground-effect helpers",
    "WalkerPart constructor/dash/landing-jets/current-weapon helpers",
    "read-only review",
    "no mutation",
    "no Codex subagent",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "CBattleEngine__AutoZoomOut",
    "CBattleEngine__Morph",
    "CBattleEngine__Rearm",
    "CBattleEngine__CalcUnitOverCrossHair",
    "CBattleEngine__UpdateAutoAim",
    "CBattleEngine__ClearFlag58CAndMorphIfState3",
    "CBattleEngine__AugmentWeapon",
    "CBattleEngine__FinishedPlayingCurrentAnimation",
    "CBattleEngine__GroundParticleEffect",
    "CBattleEngineWalkerPart__ctor",
    "CBattleEngineWalkerPart__GetIsDoingSpecialWalkerMove",
    "CBattleEngineWalkerPart__ActivateLandingJets",
    "CBattleEngineWalkerPart__GetCurrentWeapon",
    BACKUP,
    PRIOR_BACKUP,
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
)

OVERCLAIM_TOKENS = (
    "runtime battleengine behavior proven",
    "runtime walkerpart behavior proven",
    "runtime weapon behavior proven",
    "runtime zoom behavior proven",
    "runtime auto-aim behavior proven",
    "runtime morph behavior proven",
    "runtime landing-jets behavior proven",
    "runtime particle behavior proven",
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
        "pre-metadata.tsv": 13,
        "pre-tags.tsv": 13,
        "pre-xrefs.tsv": 48,
        "pre-instructions.tsv": 1436,
        "pre-decompile/index.tsv": 13,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-decompile" / "index.tsv")}
    xref_targets = {normalize_address(row["target_addr"]) for row in read_tsv(BASE / "pre-xrefs.tsv")}
    evidence = "\n".join(row.get("comment", "") for row in metadata.values())
    evidence += "\n" + "\n".join(read_text(path) for path in (BASE / "pre-decompile").glob("*.c"))
    evidence += "\n" + "\n".join(
        f"{row.get('mnemonic','')} {row.get('operands','')}" for row in read_tsv(BASE / "pre-instructions.tsv")
    )
    compact = evidence.lower().replace(" ", "")

    for address, (name, signature, tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in tokens:
                token_ok = token.lower().replace(" ", "") in compact or token in evidence
                require(token_ok, f"missing evidence token at {address}: {token}", failures)
        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)
        require(address in xref_targets, f"missing xrefs for {address}", failures)

    for token in ("0x004135d0", "0x0040a580", "0x004cb040", "0x004146b0"):
        require(token in evidence, f"missing global instruction/decompile token: {token}", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected = {
        "pre-metadata.log": "targets=13 found=13 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=13 missing=0",
        "pre-xrefs.log": "Wrote 48 rows",
        "pre-instructions.log": "Wrote 1436 function-body instruction rows",
        "pre-decompile.log": "targets=13 dumped=13 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "SCRIPT ERROR", "BADADDR", "MISSING:", "BADNAME:", "BADSIG:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 175967111, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_queue_progress(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6411, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    require(len(rows) == 6411, "quality TSV row count mismatch", failures)
    require(commented == 6411, "quality TSV commented count mismatch", failures)
    require(strict_clean == 6411, "strict clean-signature count mismatch", failures)
    require(read_json(RISK_JSON).get("candidateFunctions") == 6166, "current risk candidate mismatch", failures)
    require(read_json(FOCUSED_JSON).get("candidateFunctions") == 1178, "focused candidate mismatch", failures)
    focused_addresses = {normalize_address(row["address"]) for row in read_tsv(FOCUSED_TSV)}
    for address in TARGETS:
        require(address in focused_addresses, f"target absent from focused list: {address}", failures)

    progress = read_json(PROGRESS)
    current = progress["post100Reaudit"]["currentRiskRank"]
    latest = progress["latestWave"]
    require(latest["wave"] == "Wave1148 BattleEngine/walker-control score20 current-risk review", "progress latest wave mismatch", failures)
    require(latest["tag"] == "wave1148-battleengine-walker-control-score20-current-risk-review", "progress latest tag mismatch", failures)
    require(latest["backup"] == BACKUP, "progress backup mismatch", failures)
    require(current["focusedReviewed"] == 329, "progress focused reviewed mismatch", failures)
    require(current["focusedReviewedPercent"] == "27.91%", "progress focused percent mismatch", failures)
    require(current["remainingFocusedAfterLatestReview"] == 850, "progress remaining mismatch", failures)
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
        BATTLEENGINE_DOC,
        WALKER_DOC,
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
        lower = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1148 note mirror mismatch", failures)
    require(read_text(MAPPED_SYSTEMS) == read_text(MAPPED_SYSTEMS_MIRROR), "mapped-systems mirror mismatch", failures)
    require(read_text(PROGRESS) == read_text(PROGRESS_MIRROR), "progress mirror mismatch", failures)
    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:wave1148-battleengine-walker-control-score20-current-risk-review")
        == r"py -3 tools\wave1148_battleengine_walker_control_score20_current_risk_review.py --check",
        "missing package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_queue_progress(failures)
    check_docs(failures)
    if failures:
        print("Wave1148 BattleEngine/walker-control score20 current-risk probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1148 BattleEngine/walker-control score20 current-risk probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
