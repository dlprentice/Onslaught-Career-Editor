#!/usr/bin/env python3
"""Validate the MissionScript Level100 copied-profile preparation plan."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-preparation-proof-plan.md"
LORE_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-preparation-proof-plan.md"
RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-preparation.v1.json"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-preparation.v1.json"
DRY_RUN_PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-manifest-dry-run-validation-proof-plan.md"
DRY_RUN_RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-manifest-dry-run-validation.v1.json"
READINESS = ROOT / "release" / "readiness" / "missionscript_level100_tutorial_copied_profile_runtime_observation_copied_profile_preparation_proof_plan_2026-06-08.md"
BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
LORE_MAPPED = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
LORE_BIN_INDEX = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
LORE_RE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified"
PLAN_LINK = "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-preparation-proof-plan.md"
RESULT_LINK = "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-preparation.v1.json"
DRY_RUN_PLAN_LINK = "missionscript-level100-tutorial-copied-profile-runtime-observation-manifest-dry-run-validation-proof-plan.md"
DRY_RUN_RESULT_LINK = "missionscript-level100-tutorial-copied-profile-runtime-observation-manifest-dry-run-validation.v1.json"
THIS_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Copied-Profile Preparation Proof Plan"
NEXT_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Copied-Profile Materialization Proof Plan"

PREPARATION_CLASSES = (
    "source_specimen_policy.v1",
    "copied_profile_manifest.v1",
    "copied_directory_plan.v1",
    "specimen_byte_check_plan.v1",
    "save_options_baseline_policy.v1",
    "artifact_root_policy.v1",
    "public_redaction_policy.v1",
    "launch_block_policy.v1",
)

PLACEHOLDERS = (
    "<COPIED_PROFILE_ID_PENDING>",
    "<APP_OWNED_ARTIFACT_ROOT_PENDING>",
    "<PRIVATE_PATH_REDACTED>",
    "<PRIVATE_ARTIFACT_PATH_REDACTED>",
)

FORBIDDEN_PUBLIC_TOKENS = (
    "C:\\Users",
    "Program Files",
    ".env",
    "save-attempts",
    "onslaught_codex_directive",
    "password",
    "token=",
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
    lore = read_json(LORE_RESULT)
    require(result == lore, "lore preparation result mirror mismatch", failures)
    require(read_json(DRY_RUN_RESULT)["nextStaticSlice"] == THIS_SLICE, "dry-run result does not point to preparation slice", failures)

    require(result["schemaVersion"] == "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-preparation.v1", "preparation schemaVersion mismatch", failures)
    require(result["status"] == "PASS", "preparation status mismatch", failures)
    require(result["preparationKind"] == "public-safe-copied-profile-preparation-plan", "preparation kind mismatch", failures)

    source = result["source"]
    for key in (
        "runtimeExecution",
        "copiedProfileCreated",
        "copiedExecutableCreated",
        "beLaunch",
        "executablePatch",
        "screenshotCapture",
        "nativeInput",
        "debuggerAttachment",
        "godotWork",
        "rawDialogueIncluded",
        "privatePathsIncluded",
    ):
        require(source.get(key) is False, f"source flag must be false: {key}", failures)
    require(source.get("preparationPlanComplete") is True, "preparationPlanComplete must be true", failures)

    selected = result["selectedMission"]
    require(selected["mission"] == "level100", "selected mission mismatch", failures)
    require(selected["entryScript"] == "LevelScript.msl", "entry script mismatch", failures)
    require(selected["fileCount"] == 25, "Level100 file count mismatch", failures)
    require(selected["extraScriptCount"] == 24, "extra script count mismatch", failures)
    require(selected["totalMslLines"] == 1469, "MSL line count mismatch", failures)

    summary = result["preparationSummary"]
    for key in (
        "allPreparationOnly",
        "allRuntimeExecutionFalse",
        "allContainsPrivatePathFalse",
        "allContainsRawArtifactFalse",
        "allStatusesPlannedNotCreated",
        "allRedactionPoliciesPublicSafe",
    ):
        require(summary.get(key) is True, f"summary flag must be true: {key}", failures)
    for key in (
        "copiedProfileCreated",
        "copiedExecutableCreated",
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
        require(summary.get(key) is False, f"summary guard flag must be false: {key}", failures)
    require(summary["preparationClassCount"] == len(PREPARATION_CLASSES), "preparation class count mismatch", failures)
    require(summary["runtimeEvidenceRows"] == 0, "runtime evidence row count mismatch", failures)
    require(summary["privatePathLeakCount"] == 0, "private path leak count mismatch", failures)
    require(summary["rawArtifactLeakCount"] == 0, "raw artifact leak count mismatch", failures)
    require(summary["publicLeakCheck"] == "PASS", "public leak check mismatch", failures)

    rows = result["preparationRows"]
    require([row["preparationClass"] for row in rows] == list(PREPARATION_CLASSES), "preparation row order mismatch", failures)
    for row in rows:
        require(row["status"] == "planned-not-created", f"row status mismatch: {row['preparationClass']}", failures)
        require(row["preparationOnly"] is True, f"row must be preparationOnly: {row['preparationClass']}", failures)
        require(row["runtimeExecution"] is False, f"row runtimeExecution must be false: {row['preparationClass']}", failures)
        require(row["containsPrivatePath"] is False, f"row containsPrivatePath must be false: {row['preparationClass']}", failures)
        require(row["containsRawArtifact"] is False, f"row containsRawArtifact must be false: {row['preparationClass']}", failures)
        require(row["redactionPolicy"] == "public-safe-placeholder-only", f"row redaction policy mismatch: {row['preparationClass']}", failures)

    copy_plan = result["copyPlan"]
    for placeholder in PLACEHOLDERS:
        require(placeholder in json.dumps(copy_plan), f"missing preparation placeholder: {placeholder}", failures)
    require(copy_plan["expectedCleanSha256"] == "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750", "copy-plan specimen hash mismatch", failures)
    require(copy_plan["publicInclusionPolicy"] == "deny-raw-private-artifact", "public inclusion policy mismatch", failures)

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

    guards = result["guardPlan"]
    require(guards["expectedCleanSha256"] == "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750", "guard specimen hash mismatch", failures)
    for key in (
        "installedGameMutation",
        "originalExecutableMutation",
        "copiedProfileCreated",
        "copiedExecutableCreated",
        "beLaunch",
        "launchArmed",
        "executablePatch",
        "screenshotCapture",
        "nativeInput",
        "debuggerAttachment",
        "godotWork",
    ):
        require(guards[key] is False, f"guard flag must be false: {key}", failures)
    require(result["nextStaticSlice"] == NEXT_SLICE, "next static slice mismatch", failures)
    check_no_bad_tokens(RESULT, failures)
    check_no_bad_tokens(LORE_RESULT, failures)


def check_docs(failures: list[str]) -> None:
    require(read_text(LORE_PLAN) == read_text(PLAN), "lore preparation plan mirror mismatch", failures)
    require(read_text(LORE_RESULT) == read_text(RESULT), "lore preparation result mirror mismatch", failures)

    core_tokens = (
        THIS_SLICE,
        "copied-profile preparation planning complete, not copied-profile creation or runtime proof",
        PLAN_LINK,
        RESULT_LINK,
        DRY_RUN_PLAN_LINK,
        DRY_RUN_RESULT_LINK,
        "planned-not-created",
        "preparationOnly=true",
        "runtimeExecution=false",
        "containsPrivatePath=false",
        "containsRawArtifact=false",
        "redactionPolicy=public-safe-placeholder-only",
        "preparationPlanComplete=true",
        "copiedProfileCreated=false",
        "copiedExecutableCreated=false",
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
        "<COPIED_PROFILE_ID_PENDING>",
        "<APP_OWNED_ARTIFACT_ROOT_PENDING>",
        "<PRIVATE_PATH_REDACTED>",
        "<PRIVATE_ARTIFACT_PATH_REDACTED>",
        "source_specimen_policy.v1",
        "copied_profile_manifest.v1",
        "copied_directory_plan.v1",
        "specimen_byte_check_plan.v1",
        "save_options_baseline_policy.v1",
        "artifact_root_policy.v1",
        "public_redaction_policy.v1",
        "launch_block_policy.v1",
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
        "0",
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
        "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750",
        BACKUP,
        NEXT_SLICE,
    )
    for path in (PLAN, READINESS):
        text = read_text(path)
        for token in core_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing token: {token}", failures)
        check_no_bad_tokens(path, failures)

    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX, DRY_RUN_PLAN):
        text = read_text(path)
        for token in (PLAN_LINK, RESULT_LINK, THIS_SLICE, NEXT_SLICE):
            require(token in text, f"{path.relative_to(ROOT)} missing preparation token: {token}", failures)
        check_no_bad_tokens(path, failures)

    for source, mirror in (
        (BACKLOG, LORE_BACKLOG),
        (MAPPED, LORE_MAPPED),
        (BIN_INDEX, LORE_BIN_INDEX),
        (RE_INDEX, LORE_RE_INDEX),
    ):
        require(read_text(source) == read_text(mirror), f"lore mirror mismatch for {source.relative_to(ROOT)}", failures)

    backlog = read_text(BACKLOG)
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed preparation slice", failures)
    require(f"The selected active static-to-proof slice is {NEXT_SLICE}" in backlog, "backlog missing materialization next slice", failures)
    require(f"The selected active static-to-proof slice is {THIS_SLICE}" not in backlog, "backlog still marks preparation slice active", failures)


def check_package(failures: list[str]) -> None:
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-preparation")
        == r"py -3 tools\missionscript_level100_tutorial_copied_profile_runtime_observation_copied_profile_preparation_probe.py --check",
        "missing package copied-profile preparation test script",
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
        print("MissionScript Level100 copied-profile preparation probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("MissionScript Level100 copied-profile preparation probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
