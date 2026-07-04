#!/usr/bin/env python3
"""Validate Wave907 frontend/input/game-loop static-review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave907-frontend-input-game-loop-static-review"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
PACKAGE_JSON = ROOT / "package.json"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_frontend_input_game_loop_static_review_wave907_2026-05-26.md"
REVIEW_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "frontend-input-game-loop-static-review-2026-05-26.md"
STATIC_SYSTEM = ROOT / "reverse-engineering" / "binary-analysis" / "static-system-review-2026-05-26.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"

FUNCTION_DOCS = {
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "game.cpp" / "_index.md": (
        "Wave907",
        "frontend-input-game-loop-static-review-wave907",
        "CGame__MainLoop",
        "CGame__RunLevel",
        "CGame__ReceiveButtonAction",
    ),
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FrontEnd.cpp" / "_index.md": (
        "Wave907",
        "frontend-input-game-loop-static-review-wave907",
        "CFrontEnd__Run",
        "CFrontEnd__SetPage",
        "CFrontEnd__ReceiveButtonAction",
    ),
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Controller.cpp" / "_index.md": (
        "Wave907",
        "frontend-input-game-loop-static-review-wave907",
        "CController__DoMappings",
        "PlatformInput__InitDirectInput",
        "CPCController__ReadControllerState",
    ),
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FEPOptions.cpp" / "_index.md": (
        "Wave907",
        "frontend-input-game-loop-static-review-wave907",
        "CFEPOptions__WriteDefaultOptionsFile",
        "CPauseMenu__ResumeGameAndPersistOptions",
    ),
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FEPGoodies.cpp" / "_index.md": (
        "Wave907",
        "frontend-input-game-loop-static-review-wave907",
        "CFEPGoodies__Process",
    ),
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FEPMultiplayerStart.cpp" / "_index.md": (
        "Wave907",
        "frontend-input-game-loop-static-review-wave907",
        "CFEPMultiplayerStart__Init",
        "CFEPMultiplayerStart__ButtonPressed",
    ),
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "PauseMenu.cpp" / "_index.md": (
        "Wave907",
        "frontend-input-game-loop-static-review-wave907",
        "CPauseMenu__ResumeGameAndPersistOptions",
        "CPauseMenu__ButtonPressed",
    ),
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "MessageBox.cpp" / "_index.md": (
        "Wave907",
        "frontend-input-game-loop-static-review-wave907",
        "CMessageBox__StartVoiceOrFallbackTextReveal",
    ),
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Player.cpp" / "_index.md": (
        "Wave907",
        "frontend-input-game-loop-static-review-wave907",
        "CPlayer__AssignBattleEngine",
    ),
}

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260526-111432_post_wave907_frontend_input_game_loop_static_review_verified"

EXPECTED_FAMILIES = {
    "CGame": 56,
    "CFrontEnd": 41,
    "CFEPMultiplayerStart": 40,
    "CMenuItem": 25,
    "CController": 18,
    "CFEPBEConfig": 16,
    "PlatformInput": 15,
    "CPCController": 15,
    "CMessageBox": 14,
    "CDXFrontEndVideo": 13,
    "CPauseMenu": 13,
    "CFEPVirtualKeyboard": 13,
    "CPlayer": 13,
    "CFEPOptions": 13,
    "CMenuItemRange": 12,
    "CFEPLevelSelect": 11,
    "CFEPMain": 11,
    "CMenuItemDropdown": 11,
    "CMessageLog": 11,
    "CFEPDevelopment": 9,
    "CFEPSaveGame": 9,
    "CFEPDirectory": 8,
    "CFEPGoodies": 7,
    "CFEPWingmen": 7,
    "CFEPLanguageTest": 6,
    "CFEPLoadGame": 5,
    "CFEPCredits": 5,
    "CFEPScreenPos": 5,
    "CFEPCommon": 4,
    "CFEPDemoMain": 4,
    "CMenuItemSlider": 3,
    "CFEPDebriefing": 2,
    "CFEPBriefing": 1,
}

EXPECTED_CLUSTERS = {
    "frontend-pages": 176,
    "game-loop-player": 69,
    "frontend-core-render": 54,
    "menu-widgets": 51,
    "input-controller": 48,
    "pause-message": 38,
}

REQUIRED_ANCHORS = (
    "CGame__MainLoop",
    "CGame__RunLevel",
    "CGame__ReceiveButtonAction",
    "CGame__Pause",
    "CGame__UnPause",
    "CGame__LoadLevel",
    "CFrontEnd__Run",
    "CFrontEnd__SetPage",
    "CFrontEnd__ReceiveButtonAction",
    "CFrontEnd__RenderCursorEndSceneAndAsyncSave",
    "CFEPMultiplayerStart__Init",
    "CFEPMultiplayerStart__ButtonPressed",
    "CFEPOptions__WriteDefaultOptionsFile",
    "CFEPGoodies__Process",
    "CFEPLevelSelect__ButtonPressed",
    "CFEPMain__DoAction",
    "CFEPSaveGame__CreateSave",
    "CFEPLoadGame__DoLoad",
    "CMenuItem__ButtonPressed",
    "CController__DoMappings",
    "CController__SendButtonAction",
    "PlatformInput__InitDirectInput",
    "PlatformInput__PollPadState",
    "CPCController__ReadControllerState",
    "CPauseMenu__ResumeGameAndPersistOptions",
    "CPauseMenu__ButtonPressed",
    "CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance",
    "CMessageBox__StartVoiceOrFallbackTextReveal",
    "CMessageLog__HandleInputCommand",
    "CDXFrontEndVideo__Open",
    "CDXFrontEndVideo__Render",
    "CPlayer__AssignBattleEngine",
)

CORE_ANCHORS = (
    "Wave907",
    "frontend-input-game-loop-static-review-wave907",
    "static-coherent frontend/input/game-loop core",
    "6113/6113 = 100.00%",
    "436",
    "33",
    "CGame",
    "56",
    "CFrontEnd",
    "41",
    "CFEPMultiplayerStart",
    "40",
    "CMenuItem",
    "25",
    "CController",
    "18",
    "PlatformInput",
    "15",
    "CPCController",
    "15",
    "CMessageBox",
    "14",
    "CDXFrontEndVideo",
    "13",
    "CPauseMenu",
    "13",
    "CFEPOptions",
    "13",
    *REQUIRED_ANCHORS,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime menu behavior proven",
    "runtime input behavior proven",
    "runtime video behavior proven",
    "runtime visual qa proven",
    "all frontend layouts proven",
    "all systems complete",
    "every system is complete",
    "rebuild parity proven",
)


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


def clean_signature(signature: str) -> bool:
    return bool(signature) and not signature.startswith("undefined ") and not re.search(r"\bparam_\d+\b", signature)


def check_queue(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6113, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(queue["priorityQueues"]["commentlessHighSignal"] == [], "high-signal queue not empty", failures)

    rows = read_tsv(QUEUE_TSV)
    require(len(rows) == 6113, "quality TSV row count mismatch", failures)
    require(all(row.get("comment", "").strip() for row in rows), "quality TSV has commentless row", failures)
    require(all(clean_signature(row.get("signature", "")) for row in rows), "quality TSV has unclean signature", failures)


def check_artifacts(failures: list[str]) -> None:
    baseline = read_json(BASE / "frontend-input-game-loop-baseline.json")
    require(baseline.get("tag") == "frontend-input-game-loop-static-review-wave907", "baseline tag mismatch", failures)
    require(baseline.get("classification") == "static-coherent frontend/input/game-loop core", "baseline classification mismatch", failures)
    require(baseline.get("selectedRows") == 436, "baseline selected rows mismatch", failures)
    require(baseline.get("selectedFamilies") == 33, "baseline family count mismatch", failures)
    require(baseline.get("commentedRows") == 436, "baseline commented rows mismatch", failures)
    require(baseline.get("cleanSignatureRows") == 436, "baseline clean rows mismatch", failures)
    require(baseline.get("missingRequiredAnchors") == [], "baseline missing anchors", failures)
    require(baseline.get("clusterCounts") == EXPECTED_CLUSTERS, "baseline cluster counts mismatch", failures)
    require(baseline.get("familyCounts") == EXPECTED_FAMILIES, "baseline family counts mismatch", failures)

    family_rows = read_tsv(BASE / "frontend-input-game-loop-family-summary.tsv")
    cluster_rows = read_tsv(BASE / "frontend-input-game-loop-cluster-summary.tsv")
    anchor_rows = read_tsv(BASE / "frontend-input-game-loop-function-anchors.tsv")
    require({row["family"]: int(row["rows"]) for row in family_rows} == EXPECTED_FAMILIES, "family summary mismatch", failures)
    require({row["cluster"]: int(row["rows"]) for row in cluster_rows} == EXPECTED_CLUSTERS, "cluster summary mismatch", failures)
    require(len(anchor_rows) == 436, "anchor row count mismatch", failures)
    require(all(row.get("status") == "OK" for row in anchor_rows), "anchor status not OK", failures)
    require(all(row.get("comment", "").strip() for row in anchor_rows), "anchor missing comment", failures)
    require(all(clean_signature(row.get("signature", "")) for row in anchor_rows), "anchor unclean signature", failures)
    anchor_names = {row["name"] for row in anchor_rows}
    for name in REQUIRED_ANCHORS:
        require(name in anchor_names, f"missing required anchor: {name}", failures)


def check_backup(failures: list[str]) -> None:
    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 173247367, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = [
        PUBLIC_NOTE,
        REVIEW_DOC,
        STATIC_SYSTEM,
        MAPPED_SYSTEMS,
        BINARY_INDEX,
        RE_INDEX,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in CORE_ANCHORS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    for path, tokens in FUNCTION_DOCS.items():
        text = read_text(path)
        for token in tokens + (BACKUP_PATH,):
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:ghidra-frontend-input-game-loop-static-review-wave907")
        == r"py -3 tools\ghidra_frontend_input_game_loop_static_review_wave907_probe.py --check",
        "missing package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_queue(failures)
    check_artifacts(failures)
    check_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave907 frontend/input/game-loop static-review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Wave907 frontend/input/game-loop static-review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
