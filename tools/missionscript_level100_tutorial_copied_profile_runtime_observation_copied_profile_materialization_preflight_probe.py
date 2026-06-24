#!/usr/bin/env python3
"""Validate the MissionScript Level100 copied-profile materialization preflight."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-materialization-preflight-proof.md"
LORE_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-materialization-preflight-proof.md"
RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-materialization-preflight.v1.json"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-materialization-preflight.v1.json"
PREPARATION = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-preparation-proof-plan.md"
PREPARATION_RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-preparation.v1.json"
READINESS = ROOT / "release" / "readiness" / "missionscript_level100_tutorial_copied_profile_runtime_observation_copied_profile_materialization_preflight_2026-06-08.md"
BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
LORE_MAPPED = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
LORE_BIN_INDEX = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
LORE_RE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"
PACKAGE_JSON = ROOT / "package.json"

EXPECTED_SHA = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
OBSERVED_SHA = "e78818292a1dbe31dc6987c71665857de3a8cf3e7619745689d74c7da829c918"
BACKUP = r"G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified"
THIS_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Copied-Profile Materialization Preflight"
PREVIOUS_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Copied-Profile Preparation Proof Plan"
NEXT_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Clean Source Specimen Resolution Proof Plan"
ACTIVE_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Copied-Profile Materialization Proof Plan"
FOLLOWUP_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Copied-Executable Patch Proof Plan"
PLAN_LINK = "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-materialization-preflight-proof.md"
RESULT_LINK = "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-materialization-preflight.v1.json"
PREPARATION_LINK = "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-preparation-proof-plan.md"
PREPARATION_RESULT_LINK = "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-preparation.v1.json"

FORBIDDEN_PUBLIC_TOKENS = (
    "C:\\Users",
    "Program Files",
    ".env",
    "save-attempts",
    "onslaught_codex_directive",
    "password",
    "token=",
    "<PRIVATE_PATH_REDACTED>\\",
)

FORBIDDEN_OVERCLAIMS = (
    "runtime missionscript execution proven",
    "runtime command effects proven",
    "runtime event outcomes proven",
    "live loose-msl loading proven",
    "packed-vs-loose script selection proven",
    "runtime level100 mission outcome proven",
    "runtime text/audio behavior proven",
    "runtime hud flashing proven",
    "copied profile exists proven",
    "copied executable exists proven",
    "copied specimen hash checked proven",
    "runtime observation proof complete",
    "bea launch proof complete",
    "bea launch authorized",
    "screenshot proof complete",
    "native input proof complete",
    "debugger observation proven",
    "bea patching behavior proven",
    "visual qa complete",
    "godot parity proven",
    "rebuild parity proven",
    "no-noticeable-difference parity proven",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> Any:
    return json.loads(read_text(path))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def check_no_bad_tokens(path: Path, failures: list[str]) -> None:
    text = read_text(path)
    lower = text.lower()
    for token in FORBIDDEN_PUBLIC_TOKENS:
        require(token not in text, f"{path.relative_to(ROOT)} leaks public-forbidden token: {token}", failures)
    for phrase in FORBIDDEN_OVERCLAIMS:
        require(phrase not in lower, f"{path.relative_to(ROOT)} overclaims: {phrase}", failures)


def check_result(failures: list[str]) -> None:
    result = read_json(RESULT)
    require(result == read_json(LORE_RESULT), "lore materialization preflight result mirror mismatch", failures)
    require(read_json(PREPARATION_RESULT)["nextStaticSlice"] == "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Copied-Profile Materialization Proof Plan", "preparation result does not point to materialization lane", failures)

    require(result["schemaVersion"] == "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-materialization-preflight.v1", "schemaVersion mismatch", failures)
    require(result["status"] == "DEFERRED", "status mismatch", failures)
    require(result["preflightKind"] == "source-specimen-hash-mismatch", "preflightKind mismatch", failures)
    require(result["deferReason"] == "source-specimen-hash-mismatch", "deferReason mismatch", failures)

    static = result["staticContext"]
    require(static["staticFunctionQuality"] == "6411/6411 = 100.00%", "static function-quality mismatch", failures)
    require(static["staticDebt"] == "0 / 0 / 0", "static debt mismatch", failures)
    require(static["expandedStaticSurface"] == "1560/1560 = 100.00%", "expanded static surface mismatch", failures)
    require(static["currentRiskFocused"] == "1179/1179 = 100.00%", "current-risk mismatch", failures)
    require(static["remainingActiveFocusedWork"] == 0, "remaining focused work mismatch", failures)
    require(static["latestGhidraBackup"] == BACKUP, "latest Ghidra backup mismatch", failures)

    specimen = result["specimenPreflight"]
    require(specimen["expectedCleanSha256"] == EXPECTED_SHA, "expected hash mismatch", failures)
    require(specimen["observedSourceSha256"] == OBSERVED_SHA, "observed hash mismatch", failures)
    require(specimen["observedSourceSize"] == 2506752, "observed source size mismatch", failures)
    require(specimen["hashClass"] == "mismatch-unrecognized", "hash class mismatch", failures)
    require(specimen["sourceSpecimenMatchesExpected"] is False, "sourceSpecimenMatchesExpected must be false", failures)
    require(specimen["sourceSpecimenRecognized"] is False, "sourceSpecimenRecognized must be false", failures)
    require(specimen["trackedAuthoritySearch"] == "observed hash not found in tracked repo specimen authority", "tracked authority search mismatch", failures)
    require(specimen["publicPathPolicy"] == "no-local-path-in-public-evidence", "public path policy mismatch", failures)

    summary = result["materializationSummary"]
    for key in (
        "materializationAttempted",
        "copiedProfileCreated",
        "copiedExecutableCreated",
        "copiedSpecimenHashChecked",
        "installedGameMutation",
        "originalExecutableMutation",
        "launchArmed",
        "beLaunch",
        "executablePatch",
        "screenshotCapture",
        "nativeInput",
        "debuggerAttachment",
        "godotWork",
    ):
        require(summary[key] is False, f"summary guard flag must be false: {key}", failures)
    require(summary["runtimeEvidenceRows"] == 0, "runtime evidence rows mismatch", failures)
    require(summary["privatePathLeakCount"] == 0, "private path leak count mismatch", failures)
    require(summary["rawArtifactLeakCount"] == 0, "raw artifact leak count mismatch", failures)
    require(summary["publicLeakCheck"] == "PASS", "public leak check mismatch", failures)

    selected = result["selectedMission"]
    require(selected["mission"] == "level100", "selected mission mismatch", failures)
    require(selected["entryScript"] == "LevelScript.msl", "entry script mismatch", failures)
    require(selected["fileCount"] == 25, "Level100 file count mismatch", failures)
    require(selected["extraScriptCount"] == 24, "extra script count mismatch", failures)
    require(selected["totalMslLines"] == 1469, "MSL line count mismatch", failures)

    anchors = result["level100StaticAnchors"]
    for token in ("0x00539dc0", "0x00539ca0", "this+0x20", "this+0x124", "CDXMemBuffer__InitFromFile"):
        require(token in anchors["sourceSelectionAnchors"], f"missing source-selection anchor: {token}", failures)
    require(anchors["uniqueEventNames"] == 26, "event count mismatch", failures)
    require(anchors["handlers"] == 34, "handler count mismatch", failures)
    require(anchors["postEventCallsites"] == 41, "PostEvent count mismatch", failures)
    require(anchors["playCharMessageRows"] == 45, "message row count mismatch", failures)
    require(anchors["messageTokens"] == 43, "message token count mismatch", failures)
    require(anchors["addHelpMessageTokens"] == 6, "help token count mismatch", failures)
    require(anchors["resolvedStaticTokens"] == "68/68", "resolved token count mismatch", failures)
    require(anchors["missingReferences"] == 0, "missing reference count mismatch", failures)
    require(anchors["highlightHudPart"] == 7, "HighlightHudPart count mismatch", failures)
    require(anchors["unhighlightHudPart"] == 7, "UnHighlightHudPart count mismatch", failures)
    require(anchors["getThingRefRaw"] == 18, "GetThingRef raw count mismatch", failures)
    require(anchors["getThingRefUnique"] == 15, "GetThingRef unique count mismatch", failures)
    require(anchors["spawnThingRows"] == 20, "SpawnThing count mismatch", failures)
    require(anchors["getSlot"] == 4, "GetSlot count mismatch", failures)
    require(anchors["setSlotSave"] == 4, "SetSlotSave count mismatch", failures)

    stop = result["stopConditionTriggered"]
    require(stop["name"] == "source specimen hash mismatch", "stop condition name mismatch", failures)
    require(stop["result"] == "defer materialization before copy", "stop condition result mismatch", failures)
    require(result["nextStaticSlice"] == NEXT_SLICE, "next static slice mismatch", failures)
    check_no_bad_tokens(RESULT, failures)
    check_no_bad_tokens(LORE_RESULT, failures)


def check_docs(failures: list[str]) -> None:
    require(read_text(LORE_PLAN) == read_text(PLAN), "lore materialization preflight plan mirror mismatch", failures)
    require(read_text(LORE_RESULT) == read_text(RESULT), "lore materialization preflight result mirror mismatch", failures)

    core_tokens = (
        THIS_SLICE,
        "deferred because source specimen hash does not match the canonical clean retail specimen",
        PLAN_LINK,
        RESULT_LINK,
        PREVIOUS_SLICE,
        PREPARATION_LINK,
        PREPARATION_RESULT_LINK,
        "status=DEFERRED",
        "deferReason=source-specimen-hash-mismatch",
        "hashClass=mismatch-unrecognized",
        EXPECTED_SHA,
        OBSERVED_SHA,
        "observedSourceSize=2506752",
        "materializationAttempted=false",
        "sourceSpecimenMatchesExpected=false",
        "sourceSpecimenRecognized=false",
        "copiedProfileCreated=false",
        "copiedExecutableCreated=false",
        "copiedSpecimenHashChecked=false",
        "installedGameMutation=false",
        "originalExecutableMutation=false",
        "beLaunch=false",
        "launchArmed=false",
        "executablePatch=false",
        "screenshotCapture=false",
        "nativeInput=false",
        "debuggerAttachment=false",
        "godotWork=false",
        "runtimeEvidenceRows=0",
        "privatePathLeakCount=0",
        "rawArtifactLeakCount=0",
        "publicLeakCheck=PASS",
        "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750",
        "e78818292a1dbe31dc6987c71665857de3a8cf3e7619745689d74c7da829c918",
        "level100",
        "LevelScript.msl",
        "25",
        "24",
        "1469",
        "26",
        "34",
        "41",
        "Destroyed Friendly Building",
        "Friendly Building Destroyed",
        "45",
        "43",
        "6",
        "68/68",
        "P_TATIANA",
        "P_KRAMER",
        "P_TECHNICIAN",
        "HUD_BATTLE_LINE_MAP",
        "HUD_RADAR",
        "18",
        "15",
        "20",
        "Target Drone",
        "Air Trainer",
        "Target Tank",
        "Target Truck",
        "4` `GetSlot",
        "4` `SetSlotSave",
        "0x00539dc0",
        "0x00539ca0",
        "this+0x20",
        "this+0x124",
        "CDXMemBuffer__InitFromFile",
        BACKUP,
        NEXT_SLICE,
    )
    for path in (PLAN, READINESS):
        text = read_text(path)
        for token in core_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing token: {token}", failures)
        check_no_bad_tokens(path, failures)

    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX):
        text = read_text(path)
        for token in (PLAN_LINK, RESULT_LINK, THIS_SLICE, NEXT_SLICE, "source-specimen-hash-mismatch", "mismatch-unrecognized"):
            require(token in text, f"{path.relative_to(ROOT)} missing materialization preflight token: {token}", failures)
        check_no_bad_tokens(path, failures)

    for source, mirror in (
        (BACKLOG, LORE_BACKLOG),
        (MAPPED, LORE_MAPPED),
        (BIN_INDEX, LORE_BIN_INDEX),
        (RE_INDEX, LORE_RE_INDEX),
    ):
        require(read_text(source) == read_text(mirror), f"lore mirror mismatch for {source.relative_to(ROOT)}", failures)

    backlog = read_text(BACKLOG)
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed materialization preflight slice", failures)
    require(f"Completed {NEXT_SLICE}" in backlog, "backlog missing completed clean source specimen resolution slice", failures)
    require(f"Completed {ACTIVE_SLICE}" in backlog, "backlog missing completed copied-profile materialization slice", failures)
    require(f"The selected active static-to-proof slice is {FOLLOWUP_SLICE}" in backlog, "backlog missing active copied-executable patch slice", failures)


def check_package(failures: list[str]) -> None:
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-materialization-preflight")
        == r"py -3 tools\missionscript_level100_tutorial_copied_profile_runtime_observation_copied_profile_materialization_preflight_probe.py --check",
        "missing package copied-profile materialization preflight test script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_result(failures)
    check_docs(failures)
    check_package(failures)

    if failures:
        print("MissionScript Level100 copied-profile materialization preflight probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("MissionScript Level100 copied-profile materialization preflight probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
