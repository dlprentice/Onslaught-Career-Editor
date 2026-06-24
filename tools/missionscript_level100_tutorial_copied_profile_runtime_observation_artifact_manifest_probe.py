#!/usr/bin/env python3
"""Validate the MissionScript Level100 copied-profile artifact-manifest plan."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-artifact-manifest-proof-plan.md"
LORE_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-artifact-manifest-proof-plan.md"
SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-artifact-manifest.v1.json"
LORE_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-artifact-manifest.v1.json"
READINESS = ROOT / "release" / "readiness" / "missionscript_level100_tutorial_copied_profile_runtime_observation_artifact_manifest_proof_plan_2026-06-08.md"
PRIOR_BOUNDARY = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-boundary-proof-plan.md"
BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
LORE_MAPPED = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
LORE_BIN_INDEX = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
LORE_RE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified"
PLAN_LINK = "missionscript-level100-tutorial-copied-profile-runtime-observation-artifact-manifest-proof-plan.md"
SCHEMA_LINK = "missionscript-level100-tutorial-copied-profile-runtime-observation-artifact-manifest.v1.json"
PRIOR_LINK = "missionscript-level100-tutorial-copied-profile-runtime-observation-boundary-proof-plan.md"
NEXT_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Manifest Template Generation Proof Plan"
FOLLOWUP_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Manifest Dry-Run Validation Proof Plan"
SECOND_FOLLOWUP_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Copied-Profile Preparation Proof Plan"
THIRD_FOLLOWUP_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Copied-Profile Materialization Proof Plan"

MANIFEST_CLASSES = (
    "copied_profile_manifest.v1",
    "specimen_byte_check.v1",
    "launch_command_manifest.v1",
    "source_selection_observation.v1",
    "level100_observation_checklist.v1",
    "private_artifact_inventory.v1",
    "public_safe_result_summary.v1",
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
    "runtime message display proven",
    "runtime hud flashing proven",
    "runtime object identity proven",
    "runtime spawnthing behavior proven",
    "runtime getthingref behavior proven",
    "bea launch proof complete",
    "bea launch authorized",
    "runtime observation proof complete",
    "runtime observation proven",
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


def check_schema(failures: list[str]) -> None:
    for path in (SCHEMA, LORE_SCHEMA):
        schema = read_json(path)
        source = schema["source"]
        require(schema["schemaVersion"] == "missionscript-level100-tutorial-copied-profile-runtime-observation-artifact-manifest.v1", "schemaVersion mismatch", failures)
        require(schema["status"] == "PASS", "schema status mismatch", failures)
        for key in (
            "runtimeExecution",
            "copiedProfileCreated",
            "beLaunch",
            "executablePatch",
            "screenshotCapture",
            "nativeInput",
            "debuggerAttachment",
            "godotWork",
            "templateFilesCreated",
            "rawDialogueIncluded",
            "privatePathsIncluded",
        ):
            require(source.get(key) is False, f"schema source flag must be false: {key}", failures)

        selected = schema["selectedMission"]
        require(selected["mission"] == "level100", "selected mission mismatch", failures)
        require(selected["entryScript"] == "LevelScript.msl", "entry script mismatch", failures)
        require(selected["fileCount"] == 25, "Level100 file count mismatch", failures)
        require(selected["extraScriptCount"] == 24, "extra script count mismatch", failures)
        require(selected["totalMslLines"] == 1469, "MSL line count mismatch", failures)

        classes = {entry["name"]: entry for entry in schema["manifestClasses"]}
        for name in MANIFEST_CLASSES:
            require(name in classes, f"missing manifest class: {name}", failures)
            require(classes[name].get("requiredFields"), f"manifest class missing required fields: {name}", failures)
        require(classes["specimen_byte_check.v1"]["expectedCleanSha256"] == "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750", "expected specimen hash mismatch", failures)
        require(classes["launch_command_manifest.v1"]["launchArmedDefault"] is False, "launchArmed default must be false", failures)

        counts = schema["checklistStaticCounts"]
        require(counts["uniqueEventNames"] == 26, "event count mismatch", failures)
        require(counts["handlers"] == 34, "handler count mismatch", failures)
        require(counts["postEventCallsites"] == 41, "PostEvent count mismatch", failures)
        require(counts["playCharMessageRows"] == 45, "message row count mismatch", failures)
        require(counts["messageTokens"] == 43, "message token count mismatch", failures)
        require(counts["addHelpMessageTokens"] == 6, "help token count mismatch", failures)
        require(counts["resolvedStaticTokens"] == "68/68", "resolved token count mismatch", failures)
        require(counts["missingReferences"] == 0, "missing token count mismatch", failures)
        require(counts["highlightHudPart"] == 7, "HighlightHudPart count mismatch", failures)
        require(counts["unhighlightHudPart"] == 7, "UnHighlightHudPart count mismatch", failures)
        require(counts["getThingRefRaw"] == 18, "GetThingRef raw count mismatch", failures)
        require(counts["getThingRefUnique"] == 15, "GetThingRef unique count mismatch", failures)
        require(counts["spawnThingRows"] == 20, "SpawnThing count mismatch", failures)
        require(counts["getSlot"] == 4, "GetSlot count mismatch", failures)
        require(counts["setSlotSave"] == 4, "SetSlotSave count mismatch", failures)
        require(schema["nextStaticSlice"] == NEXT_SLICE, "next static slice mismatch", failures)
        check_no_bad_tokens(path, failures)


def check_docs(failures: list[str]) -> None:
    require(read_text(LORE_PLAN) == read_text(PLAN), "lore artifact-manifest plan mirror mismatch", failures)
    require(read_text(LORE_SCHEMA) == read_text(SCHEMA), "lore artifact-manifest schema mirror mismatch", failures)

    core_tokens = (
        "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Artifact Manifest Proof Plan",
        "artifact-manifest planning complete, not runtime proof",
        PLAN_LINK,
        SCHEMA_LINK,
        PRIOR_LINK,
        "level100",
        "LevelScript.msl",
        "25",
        "24",
        "1469",
        "copied_profile_manifest.v1",
        "specimen_byte_check.v1",
        "launch_command_manifest.v1",
        "source_selection_observation.v1",
        "level100_observation_checklist.v1",
        "private_artifact_inventory.v1",
        "public_safe_result_summary.v1",
        "launchArmed=false",
        "not-run",
        "observed",
        "inconclusive",
        "blocked",
        "out-of-scope",
        "26",
        "34",
        "41",
        "Destroyed Friendly Building",
        "Friendly Building Destroyed",
        "45",
        "43",
        "6",
        "68/68",
        "0 missing",
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

    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX, PRIOR_BOUNDARY):
        text = read_text(path)
        for token in (PLAN_LINK, SCHEMA_LINK, "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Artifact Manifest"):
            require(token in text, f"{path.relative_to(ROOT)} missing artifact-manifest token: {token}", failures)
        check_no_bad_tokens(path, failures)

    for source, mirror in (
        (BACKLOG, LORE_BACKLOG),
        (MAPPED, LORE_MAPPED),
        (BIN_INDEX, LORE_BIN_INDEX),
        (RE_INDEX, LORE_RE_INDEX),
    ):
        require(read_text(source) == read_text(mirror), f"lore mirror mismatch for {source.relative_to(ROOT)}", failures)

    backlog = read_text(BACKLOG)
    require("Completed MissionScript Level100 Tutorial Copied-Profile Runtime Observation Artifact Manifest Proof Plan" in backlog, "backlog missing completed artifact-manifest slice", failures)
    active_next = f"The selected active static-to-proof slice is {NEXT_SLICE}" in backlog
    completed_next = f"Completed {NEXT_SLICE}" in backlog
    active_followup = f"The selected active static-to-proof slice is {FOLLOWUP_SLICE}" in backlog
    completed_followup = f"Completed {FOLLOWUP_SLICE}" in backlog
    active_second = f"The selected active static-to-proof slice is {SECOND_FOLLOWUP_SLICE}" in backlog
    completed_second = f"Completed {SECOND_FOLLOWUP_SLICE}" in backlog
    active_third = f"The selected active static-to-proof slice is {THIRD_FOLLOWUP_SLICE}" in backlog
    require(active_next or (completed_next and active_followup) or (completed_next and completed_followup and active_second) or (completed_next and completed_followup and completed_second and active_third), "backlog missing manifest-template/dry-run/preparation/materialization handoff", failures)
    require("The selected active static-to-proof slice is MissionScript Level100 Tutorial Copied-Profile Runtime Observation Artifact Manifest Proof Plan" not in backlog, "backlog still marks artifact-manifest slice active", failures)


def check_package(failures: list[str]) -> None:
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:missionscript-level100-tutorial-copied-profile-runtime-observation-artifact-manifest")
        == r"py -3 tools\missionscript_level100_tutorial_copied_profile_runtime_observation_artifact_manifest_probe.py --check",
        "missing package copied-profile runtime observation artifact-manifest test script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_schema(failures)
    check_docs(failures)
    check_package(failures)

    if failures:
        print("MissionScript Level100 copied-profile runtime observation artifact-manifest probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("MissionScript Level100 copied-profile runtime observation artifact-manifest probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
