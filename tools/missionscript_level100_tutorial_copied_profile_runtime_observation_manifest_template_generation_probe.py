#!/usr/bin/env python3
"""Validate the MissionScript Level100 copied-profile manifest-template bundle."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-manifest-template-generation-proof-plan.md"
LORE_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-manifest-template-generation-proof-plan.md"
TEMPLATES = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-manifest-templates.v1.json"
LORE_TEMPLATES = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-manifest-templates.v1.json"
READINESS = ROOT / "release" / "readiness" / "missionscript_level100_tutorial_copied_profile_runtime_observation_manifest_template_generation_proof_plan_2026-06-08.md"
PRIOR_ARTIFACT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-artifact-manifest-proof-plan.md"
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
PLAN_LINK = "missionscript-level100-tutorial-copied-profile-runtime-observation-manifest-template-generation-proof-plan.md"
TEMPLATES_LINK = "missionscript-level100-tutorial-copied-profile-runtime-observation-manifest-templates.v1.json"
PRIOR_LINK = "missionscript-level100-tutorial-copied-profile-runtime-observation-artifact-manifest-proof-plan.md"
NEXT_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Manifest Dry-Run Validation Proof Plan"
FOLLOWUP_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Copied-Profile Preparation Proof Plan"
SECOND_FOLLOWUP_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Copied-Profile Materialization Proof Plan"

MANIFEST_CLASSES = (
    "copied_profile_manifest.v1",
    "specimen_byte_check.v1",
    "launch_command_manifest.v1",
    "source_selection_observation.v1",
    "level100_observation_checklist.v1",
    "private_artifact_inventory.v1",
    "public_safe_result_summary.v1",
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


def require_all_status_not_run(value: Any, failures: list[str], path: str = "root") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "status":
                require(child == "not-run", f"checklist status must be not-run at {path}", failures)
            require_all_status_not_run(child, failures, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            require_all_status_not_run(child, failures, f"{path}[{index}]")


def check_templates(failures: list[str]) -> None:
    for path in (TEMPLATES, LORE_TEMPLATES):
        data = read_json(path)
        source = data["source"]
        require(data["schemaVersion"] == "missionscript-level100-tutorial-copied-profile-runtime-observation-manifest-templates.v1", "template schemaVersion mismatch", failures)
        require(data["status"] == "PASS", "template status mismatch", failures)
        for key in (
            "runtimeExecution",
            "copiedProfileCreated",
            "beLaunch",
            "executablePatch",
            "screenshotCapture",
            "nativeInput",
            "debuggerAttachment",
            "godotWork",
            "rawDialogueIncluded",
            "privatePathsIncluded",
        ):
            require(source.get(key) is False, f"template source flag must be false: {key}", failures)
        require(source.get("templateFilesCreated") is True, "templateFilesCreated must be true", failures)

        defaults = data["defaults"]
        require(defaults["launchArmed"] is False, "default launchArmed must be false", failures)
        require(defaults["installedGameMutation"] is False, "default installedGameMutation must be false", failures)
        require(defaults["privatePathsRedactedInPublic"] is True, "default privatePathsRedactedInPublic must be true", failures)
        require(defaults["rowStatus"] == "not-run", "default row status mismatch", failures)
        require(defaults["observationStatus"] == "unobserved", "default observation status mismatch", failures)
        for placeholder in PLACEHOLDERS:
            require(placeholder in json.dumps(data), f"missing placeholder: {placeholder}", failures)

        selected = data["selectedMission"]
        require(selected["mission"] == "level100", "selected mission mismatch", failures)
        require(selected["entryScript"] == "LevelScript.msl", "entry script mismatch", failures)
        require(selected["fileCount"] == 25, "Level100 file count mismatch", failures)
        require(selected["extraScriptCount"] == 24, "extra script count mismatch", failures)
        require(selected["totalMslLines"] == 1469, "MSL line count mismatch", failures)

        templates = {entry["templateClass"]: entry for entry in data["templates"]}
        require(tuple(templates) == MANIFEST_CLASSES, "manifest template class order mismatch", failures)
        for name in MANIFEST_CLASSES:
            entry = templates[name]
            require(entry["templateOnly"] is True, f"templateOnly mismatch: {name}", failures)
            require(entry["runtimeExecution"] is False, f"runtimeExecution mismatch: {name}", failures)
            require(entry["containsPrivatePath"] is False, f"containsPrivatePath mismatch: {name}", failures)
            require(entry["containsRawArtifact"] is False, f"containsRawArtifact mismatch: {name}", failures)
            require(entry["defaultStatus"] == "not-run", f"defaultStatus mismatch: {name}", failures)
            require(entry["redactionPolicy"] == "public-safe-placeholder-only", f"redactionPolicy mismatch: {name}", failures)

        copied = templates["copied_profile_manifest.v1"]["fields"]
        require(copied["sourceSpecimenSha256"] == "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750", "expected specimen hash mismatch", failures)
        require(copied["installedGameMutation"] is False, "copied profile installedGameMutation must be false", failures)
        require(copied["privatePathsRedactedInPublic"] is True, "copied profile redaction flag mismatch", failures)

        specimen = templates["specimen_byte_check.v1"]["fields"]
        require(specimen["expectedCleanSha256"] == "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750", "specimen expected hash mismatch", failures)
        require(specimen["copiedExecutableSha256Class"] == "not-run", "specimen copied hash class mismatch", failures)
        require(specimen["originalBytesVerified"] == "not-run", "specimen byte check status mismatch", failures)

        launch = templates["launch_command_manifest.v1"]["fields"]
        require(launch["launchArmed"] is False, "launchArmed must be false", failures)
        require(launch["argumentVector"] == [], "launch argument vector must be empty in template", failures)

        source_selection = templates["source_selection_observation.v1"]["fields"]
        require(source_selection["observationStatus"] == "unobserved", "source-selection status mismatch", failures)
        for token in ("0x00539dc0", "0x00539ca0", "this+0x20", "this+0x124", "CDXMemBuffer__InitFromFile"):
            require(token in source_selection["staticAnchors"], f"missing source-selection anchor: {token}", failures)

        checklist = templates["level100_observation_checklist.v1"]
        require_all_status_not_run(checklist["fields"], failures)
        allowed = checklist["allowedRowStatuses"]
        require(allowed == ["not-run", "observed", "inconclusive", "blocked", "out-of-scope"], "allowed row statuses mismatch", failures)
        fields = checklist["fields"]
        require(fields["eventIngress"]["uniqueEventNames"] == 26, "event count mismatch", failures)
        require(fields["eventIngress"]["handlers"] == 34, "handler count mismatch", failures)
        require(fields["eventIngress"]["postEventCallsites"] == 41, "PostEvent count mismatch", failures)
        require(fields["messageTextSpeaker"]["playCharMessageRows"] == 45, "message row count mismatch", failures)
        require(fields["messageTextSpeaker"]["messageTokens"] == 43, "message token count mismatch", failures)
        require(fields["messageTextSpeaker"]["addHelpMessageTokens"] == 6, "help token count mismatch", failures)
        require(fields["messageTextSpeaker"]["resolvedStaticTokens"] == "68/68", "resolved token count mismatch", failures)
        require(fields["messageTextSpeaker"]["missingReferences"] == 0, "missing token count mismatch", failures)
        require(fields["hudDisplay"]["highlightHudPart"] == 7, "HighlightHudPart count mismatch", failures)
        require(fields["hudDisplay"]["unhighlightHudPart"] == 7, "UnHighlightHudPart count mismatch", failures)
        require(fields["objectLookup"]["getThingRefRaw"] == 18, "GetThingRef raw count mismatch", failures)
        require(fields["objectLookup"]["getThingRefUnique"] == 15, "GetThingRef unique count mismatch", failures)
        require(fields["spawnHandoff"]["spawnThingRows"] == 20, "SpawnThing count mismatch", failures)
        require(fields["slotObjective"]["getSlot"] == 4, "GetSlot count mismatch", failures)
        require(fields["slotObjective"]["setSlotSave"] == 4, "SetSlotSave count mismatch", failures)
        require(data["nextStaticSlice"] == NEXT_SLICE, "next static slice mismatch", failures)
        check_no_bad_tokens(path, failures)


def check_docs(failures: list[str]) -> None:
    require(read_text(LORE_PLAN) == read_text(PLAN), "lore manifest-template plan mirror mismatch", failures)
    require(read_text(LORE_TEMPLATES) == read_text(TEMPLATES), "lore manifest-template bundle mirror mismatch", failures)

    core_tokens = (
        "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Manifest Template Generation Proof Plan",
        "manifest-template generation complete, not runtime proof",
        PLAN_LINK,
        TEMPLATES_LINK,
        PRIOR_LINK,
        "templateOnly=true",
        "runtimeExecution=false",
        "containsPrivatePath=false",
        "containsRawArtifact=false",
        "redactionPolicy=public-safe-placeholder-only",
        "launchArmed=false",
        "installedGameMutation=false",
        "privatePathsRedactedInPublic=true",
        "<COPIED_PROFILE_ID_PENDING>",
        "<APP_OWNED_ARTIFACT_ROOT_PENDING>",
        "<PRIVATE_PATH_REDACTED>",
        "<PRIVATE_ARTIFACT_PATH_REDACTED>",
        "not-run",
        "unobserved",
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

    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX, PRIOR_ARTIFACT):
        text = read_text(path)
        for token in (PLAN_LINK, TEMPLATES_LINK, "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Manifest Template Generation", NEXT_SLICE, FOLLOWUP_SLICE):
            require(token in text, f"{path.relative_to(ROOT)} missing manifest-template token: {token}", failures)
        check_no_bad_tokens(path, failures)

    for source, mirror in (
        (BACKLOG, LORE_BACKLOG),
        (MAPPED, LORE_MAPPED),
        (BIN_INDEX, LORE_BIN_INDEX),
        (RE_INDEX, LORE_RE_INDEX),
    ):
        require(read_text(source) == read_text(mirror), f"lore mirror mismatch for {source.relative_to(ROOT)}", failures)

    backlog = read_text(BACKLOG)
    require("Completed MissionScript Level100 Tutorial Copied-Profile Runtime Observation Manifest Template Generation Proof Plan" in backlog, "backlog missing completed manifest-template slice", failures)
    active_next = f"The selected active static-to-proof slice is {NEXT_SLICE}" in backlog
    completed_next = f"Completed {NEXT_SLICE}" in backlog
    active_followup = f"The selected active static-to-proof slice is {FOLLOWUP_SLICE}" in backlog
    completed_followup = f"Completed {FOLLOWUP_SLICE}" in backlog
    active_second = f"The selected active static-to-proof slice is {SECOND_FOLLOWUP_SLICE}" in backlog
    require(active_next or (completed_next and active_followup) or (completed_next and completed_followup and active_second), "backlog missing manifest dry-run/preparation/materialization handoff", failures)
    require("The selected active static-to-proof slice is MissionScript Level100 Tutorial Copied-Profile Runtime Observation Manifest Template Generation Proof Plan" not in backlog, "backlog still marks manifest-template slice active", failures)


def check_package(failures: list[str]) -> None:
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:missionscript-level100-tutorial-copied-profile-runtime-observation-manifest-template-generation")
        == r"py -3 tools\missionscript_level100_tutorial_copied_profile_runtime_observation_manifest_template_generation_probe.py --check",
        "missing package manifest-template-generation test script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_templates(failures)
    check_docs(failures)
    check_package(failures)

    if failures:
        print("MissionScript Level100 copied-profile runtime observation manifest-template probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("MissionScript Level100 copied-profile runtime observation manifest-template probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
