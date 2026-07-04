#!/usr/bin/env python3
"""Validate the MissionScript Level100 copied-profile manifest dry-run result."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-manifest-dry-run-validation-proof-plan.md"
LORE_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-manifest-dry-run-validation-proof-plan.md"
RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-manifest-dry-run-validation.v1.json"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-manifest-dry-run-validation.v1.json"
TEMPLATE_PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-manifest-template-generation-proof-plan.md"
TEMPLATES = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-manifest-templates.v1.json"
READINESS = ROOT / "release" / "readiness" / "missionscript_level100_tutorial_copied_profile_runtime_observation_manifest_dry_run_validation_proof_plan_2026-06-08.md"
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
PLAN_LINK = "missionscript-level100-tutorial-copied-profile-runtime-observation-manifest-dry-run-validation-proof-plan.md"
RESULT_LINK = "missionscript-level100-tutorial-copied-profile-runtime-observation-manifest-dry-run-validation.v1.json"
TEMPLATE_PLAN_LINK = "missionscript-level100-tutorial-copied-profile-runtime-observation-manifest-template-generation-proof-plan.md"
TEMPLATES_LINK = "missionscript-level100-tutorial-copied-profile-runtime-observation-manifest-templates.v1.json"
NEXT_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Copied-Profile Preparation Proof Plan"
FOLLOWUP_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Copied-Profile Materialization Proof Plan"

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
    "runtime hud flashing proven",
    "runtime observation proof complete",
    "bea launch proof complete",
    "bea launch authorized",
    "copied profile created",
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
    templates = read_json(TEMPLATES)
    result = read_json(RESULT)
    lore = read_json(LORE_RESULT)
    require(result == lore, "lore dry-run result mirror mismatch", failures)

    require(result["schemaVersion"] == "missionscript-level100-tutorial-copied-profile-runtime-observation-manifest-dry-run-validation.v1", "dry-run schemaVersion mismatch", failures)
    require(result["status"] == "PASS", "dry-run status mismatch", failures)
    source = result["source"]
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
        require(source.get(key) is False, f"dry-run source flag must be false: {key}", failures)
    require(source.get("templateBundleValidated") is True, "templateBundleValidated must be true", failures)

    selected = result["selectedMission"]
    require(selected["mission"] == "level100", "selected mission mismatch", failures)
    require(selected["entryScript"] == "LevelScript.msl", "entry script mismatch", failures)
    require(selected["fileCount"] == 25, "Level100 file count mismatch", failures)
    require(selected["extraScriptCount"] == 24, "extra script count mismatch", failures)
    require(selected["totalMslLines"] == 1469, "MSL line count mismatch", failures)

    summary = result["dryRunSummary"]
    expected_true = (
        "allTemplateOnly",
        "allRuntimeExecutionFalse",
        "allContainsPrivatePathFalse",
        "allContainsRawArtifactFalse",
        "allDefaultStatusNotRun",
        "allRedactionPoliciesPublicSafe",
        "privatePathsRedactedInPublic",
    )
    for key in expected_true:
        require(summary.get(key) is True, f"dry-run summary flag must be true: {key}", failures)
    for key in ("launchArmed", "installedGameMutation"):
        require(summary.get(key) is False, f"dry-run guard flag must be false: {key}", failures)
    require(summary["templateClassCount"] == len(MANIFEST_CLASSES), "template class count mismatch", failures)
    require(summary["sourceSelectionStatus"] == "unobserved", "source-selection status mismatch", failures)
    require(summary["observedRowCount"] == 0, "observed row count mismatch", failures)
    require(summary["runtimeEvidenceRows"] == 0, "runtime evidence row count mismatch", failures)
    require(summary["privatePathLeakCount"] == 0, "private path leak count mismatch", failures)
    require(summary["rawArtifactLeakCount"] == 0, "raw artifact leak count mismatch", failures)
    require(summary["publicLeakCheck"] == "PASS", "public leak check mismatch", failures)

    rows = result["templateValidationRows"]
    require([row["templateClass"] for row in rows] == list(MANIFEST_CLASSES), "template validation row order mismatch", failures)
    template_by_class = {entry["templateClass"]: entry for entry in templates["templates"]}
    for row in rows:
        name = row["templateClass"]
        source_template = template_by_class[name]
        require(row["status"] == "validated-empty-template", f"dry-run row status mismatch: {name}", failures)
        for key in ("templateOnly", "runtimeExecution", "containsPrivatePath", "containsRawArtifact", "defaultStatus", "redactionPolicy"):
            require(row[key] == source_template[key], f"dry-run row does not match template {name}: {key}", failures)

    checklist = result["checklistValidation"]
    require(checklist["allStatuses"] == "not-run", "all checklist statuses mismatch", failures)
    require(checklist["allowedRowStatuses"] == ["not-run", "observed", "inconclusive", "blocked", "out-of-scope"], "allowed row statuses mismatch", failures)
    require(checklist["observedRowCount"] == 0, "checklist observed row count mismatch", failures)
    require(checklist["sourceSelection"]["observationStatus"] == "unobserved", "checklist source-selection observation mismatch", failures)
    for token in ("0x00539dc0", "0x00539ca0", "this+0x20", "this+0x124", "CDXMemBuffer__InitFromFile"):
        require(token in checklist["sourceSelection"]["anchors"], f"missing source-selection anchor: {token}", failures)
    require(checklist["eventIngress"]["uniqueEventNames"] == 26, "event count mismatch", failures)
    require(checklist["eventIngress"]["handlers"] == 34, "handler count mismatch", failures)
    require(checklist["eventIngress"]["postEventCallsites"] == 41, "PostEvent count mismatch", failures)
    require(checklist["messageTextSpeaker"]["playCharMessageRows"] == 45, "message row count mismatch", failures)
    require(checklist["messageTextSpeaker"]["messageTokens"] == 43, "message token count mismatch", failures)
    require(checklist["messageTextSpeaker"]["addHelpMessageTokens"] == 6, "help token count mismatch", failures)
    require(checklist["messageTextSpeaker"]["resolvedStaticTokens"] == "68/68", "resolved token count mismatch", failures)
    require(checklist["messageTextSpeaker"]["missingReferences"] == 0, "missing reference count mismatch", failures)
    require(checklist["hudDisplay"]["highlightHudPart"] == 7, "HighlightHudPart count mismatch", failures)
    require(checklist["hudDisplay"]["unhighlightHudPart"] == 7, "UnHighlightHudPart count mismatch", failures)
    require(checklist["objectLookup"]["getThingRefRaw"] == 18, "GetThingRef raw count mismatch", failures)
    require(checklist["objectLookup"]["getThingRefUnique"] == 15, "GetThingRef unique count mismatch", failures)
    require(checklist["spawnHandoff"]["spawnThingRows"] == 20, "SpawnThing count mismatch", failures)
    require(checklist["slotObjective"]["getSlot"] == 4, "GetSlot count mismatch", failures)
    require(checklist["slotObjective"]["setSlotSave"] == 4, "SetSlotSave count mismatch", failures)

    placeholders = result["placeholderValidation"]
    for placeholder in PLACEHOLDERS:
        require(placeholder in json.dumps(placeholders), f"missing dry-run placeholder: {placeholder}", failures)

    guards = result["guardValidation"]
    require(guards["expectedCleanSha256"] == "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750", "guard specimen hash mismatch", failures)
    for key in ("launchArmed", "installedGameMutation", "copiedProfileCreated", "beLaunch", "executablePatch", "screenshotCapture", "nativeInput", "debuggerAttachment", "godotWork"):
        require(guards[key] is False, f"guard flag must be false: {key}", failures)
    require(result["nextStaticSlice"] == NEXT_SLICE, "next static slice mismatch", failures)
    check_no_bad_tokens(RESULT, failures)
    check_no_bad_tokens(LORE_RESULT, failures)


def check_docs(failures: list[str]) -> None:
    require(read_text(LORE_PLAN) == read_text(PLAN), "lore dry-run plan mirror mismatch", failures)
    require(read_text(LORE_RESULT) == read_text(RESULT), "lore dry-run result mirror mismatch", failures)

    core_tokens = (
        "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Manifest Dry-Run Validation Proof Plan",
        "dry-run validation complete, not runtime proof",
        PLAN_LINK,
        RESULT_LINK,
        TEMPLATE_PLAN_LINK,
        TEMPLATES_LINK,
        "validated-empty-template",
        "templateOnly=true",
        "runtimeExecution=false",
        "containsPrivatePath=false",
        "containsRawArtifact=false",
        "redactionPolicy=public-safe-placeholder-only",
        "launchArmed=false",
        "installedGameMutation=false",
        "privatePathsRedactedInPublic=true",
        "copiedProfileCreated=false",
        "beLaunch=false",
        "executablePatch=false",
        "screenshotCapture=false",
        "nativeInput=false",
        "debuggerAttachment=false",
        "godotWork=false",
        "observedRowCount=0",
        "runtimeEvidenceRows=0",
        "privatePathLeakCount=0",
        "rawArtifactLeakCount=0",
        "publicLeakCheck=PASS",
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

    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX, TEMPLATE_PLAN):
        text = read_text(path)
        for token in (PLAN_LINK, RESULT_LINK, "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Manifest Dry-Run Validation", NEXT_SLICE, FOLLOWUP_SLICE):
            require(token in text, f"{path.relative_to(ROOT)} missing dry-run token: {token}", failures)
        check_no_bad_tokens(path, failures)

    for source, mirror in (
        (BACKLOG, LORE_BACKLOG),
        (MAPPED, LORE_MAPPED),
        (BIN_INDEX, LORE_BIN_INDEX),
        (RE_INDEX, LORE_RE_INDEX),
    ):
        require(read_text(source) == read_text(mirror), f"lore mirror mismatch for {source.relative_to(ROOT)}", failures)

    backlog = read_text(BACKLOG)
    active_next = f"The selected active static-to-proof slice is {NEXT_SLICE}" in backlog
    completed_next = f"Completed {NEXT_SLICE}" in backlog
    active_followup = f"The selected active static-to-proof slice is {FOLLOWUP_SLICE}" in backlog
    require("Completed MissionScript Level100 Tutorial Copied-Profile Runtime Observation Manifest Dry-Run Validation Proof Plan" in backlog, "backlog missing completed dry-run slice", failures)
    require(active_next or (completed_next and active_followup), "backlog missing copied-profile preparation/materialization handoff", failures)
    require("The selected active static-to-proof slice is MissionScript Level100 Tutorial Copied-Profile Runtime Observation Manifest Dry-Run Validation Proof Plan" not in backlog, "backlog still marks dry-run slice active", failures)


def check_package(failures: list[str]) -> None:
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:missionscript-level100-tutorial-copied-profile-runtime-observation-manifest-dry-run-validation")
        == r"py -3 tools\missionscript_level100_tutorial_copied_profile_runtime_observation_manifest_dry_run_validation_probe.py --check",
        "missing package manifest dry-run validation test script",
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
        print("MissionScript Level100 copied-profile runtime observation manifest dry-run validation probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("MissionScript Level100 copied-profile runtime observation manifest dry-run validation probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
