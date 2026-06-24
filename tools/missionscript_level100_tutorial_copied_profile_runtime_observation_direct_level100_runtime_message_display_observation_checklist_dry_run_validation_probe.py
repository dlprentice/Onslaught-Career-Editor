#!/usr/bin/env python3
"""Validate the MissionScript Level100 runtime message-display checklist dry-run."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "level100-message-checklist-dry-run-validation.md"
LORE_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "level100-message-checklist-dry-run-validation.md"
RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "level100-message-checklist-dry-run-validation.v1.json"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "level100-message-checklist-dry-run-validation.v1.json"
TEMPLATE_RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-runtime-message-display-observation-checklist-template.v1.json"
BOUNDARY_RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-runtime-message-display-boundary.v1.json"
READINESS = ROOT / "release" / "readiness" / "missionscript_level100_tutorial_copied_profile_runtime_observation_direct_level100_runtime_message_display_observation_checklist_dry_run_validation_2026-06-09.md"
BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
LORE_MAPPED = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
LORE_BIN_INDEX = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
LORE_RE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"
PACKAGE_JSON = ROOT / "package.json"

THIS_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Runtime Message Display Observation Checklist Dry-Run Validation Proof Plan"
PREVIOUS_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Runtime Message Display Observation Checklist Template Proof Plan"
NEXT_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Runtime Message Display Observation Checklist Private-Frame Review Arm Boundary Proof Plan"
PLAN_LINK = "level100-message-checklist-dry-run-validation.md"
RESULT_LINK = "level100-message-checklist-dry-run-validation.v1.json"
TEMPLATE_LINK = "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-runtime-message-display-observation-checklist-template-proof-plan.md"
TEMPLATE_RESULT_LINK = "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-runtime-message-display-observation-checklist-template.v1.json"
STATUS_TOKEN = "direct-level100-runtime-message-display-observation-checklist-dry-run-validation-pass-no-runtime-message-proof"
TEMPLATE_STATUS_TOKEN = "direct-level100-runtime-message-display-observation-checklist-template-defined-no-runtime-message-proof"
BOUNDARY_STATUS_TOKEN = "direct-level100-runtime-message-display-boundary-defined-no-runtime-message-proof"

TEMPLATE_CLASSES = (
    "private_frame_message_observation_checklist.v1",
    "source_selection_boundary_row.v1",
    "message_display_classification_row.v1",
    "timing_order_classification_row.v1",
    "public_safe_result_summary.v1",
)

ARTIFACT_KEYS = (
    "private-frame-message-observation-checklist",
    "source-selection-boundary-row",
    "message-display-classification-row",
    "timing-order-classification-row",
    "public-safe-result-summary",
)

TEMPLATE_ROW_COUNTS = {
    "private-frame-message-observation-checklist": 3,
    "source-selection-boundary-row": 1,
    "message-display-classification-row": 3,
    "timing-order-classification-row": 1,
    "public-safe-result-summary": 1,
}

FALSE_GUARDS = (
    "runtimeExecution",
    "templateMutation",
    "profileIdPublished",
    "privateProofAssetPublished",
    "privateCaptureLocatorIncluded",
    "privateArtifactHashIncluded",
    "privateArtifactBytesIncluded",
    "privateWindowIdentifiersIncluded",
    "publicMachinePathIncluded",
    "newLaunch",
    "beLaunch",
    "launchArmed",
    "screenshotCapture",
    "newScreenshotCapture",
    "newPrivateFrameReview",
    "messageObservationPerformed",
    "exactTextOcrPerformed",
    "rawDialogueIncluded",
    "rawDialoguePublished",
    "visibleTextExcerptPublished",
    "exactVisibleTokenIdentityClaim",
    "exactVisibleTokenIdentityProven",
    "perFrameTokenIdentityClaim",
    "perFrameSpeakerIdentityClaim",
    "runtimeMessageDisplayClaim",
    "runtimeMessageDisplayProven",
    "sourceSelectionObserved",
    "sourceSelectionProven",
    "messageDisplayClassificationProven",
    "timingOrderProven",
    "nativeInput",
    "debuggerAttachment",
    "godotWork",
)

ZERO_COUNTS = (
    "missionScriptRuntimeEvidenceRows",
    "publicAbsolutePathLeakCount",
    "publicSha256ValueLeakCount",
    "publicWindowIdentifierLeakCount",
    "publicProcessIdentifierLeakCount",
    "privatePathLeakCount",
    "rawArtifactLeakCount",
    "rawDialogueLeakCount",
    "beProcessesAfterDryRun",
)

FORBIDDEN_PUBLIC_TOKENS = (
    "c:\\users",
    "c:/users",
    "g:\\",
    "program files",
    "steamapps",
    "subagents\\",
    "subagents/",
    "private_runtime_evidence",
    "hwnd",
    "capture source hint",
    "capturepath",
    "framepath",
    "capturehash",
    "framehash",
    "framesha256",
    "framebytelength",
    ".private.png",
    "frame-05s",
    "frame-10s",
    "frame-15s",
    "frame-25s",
    "20260609-",
    "level100-clean-materialized-20260608-214752",
    "save-attempts",
    "onslaught_codex_directive",
    "password",
    "token=",
)

FORBIDDEN_OVERCLAIMS = (
    "runtime message display behavior proven",
    "runtime message display proven",
    "runtime missionscript execution proven",
    "level100 script source selection proven",
    "runtime command effects proven",
    "runtime event outcomes proven",
    "exact visible text identity proven",
    "ocr identity proven",
    "per-frame token identity proven",
    "per-frame speaker identity proven",
    "source selection proven",
    "audio behavior proven",
    "visual correctness proven",
    "timing correctness proven",
    "native input behavior proven",
    "debugger observation proven",
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


def no_bea_process_running() -> bool:
    result = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            "if (Get-Process -Name BEA -ErrorAction SilentlyContinue) { exit 1 } else { exit 0 }",
        ],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def check_no_bad_tokens(path: Path, failures: list[str]) -> None:
    text = read_text(path)
    lower = text.lower()
    for token in FORBIDDEN_PUBLIC_TOKENS:
        require(token not in lower, f"{path.relative_to(ROOT)} leaks public-forbidden token: {token}", failures)
    for phrase in FORBIDDEN_OVERCLAIMS:
        require(phrase not in lower, f"{path.relative_to(ROOT)} overclaims: {phrase}", failures)
    require(re.search(r"\b[a-fA-F0-9]{64}\b", text) is None, f"{path.relative_to(ROOT)} leaks a raw SHA-256-like value", failures)
    require(re.search(r"\b[A-Za-z]:[\\/]", text) is None, f"{path.relative_to(ROOT)} leaks a machine-local absolute path", failures)


def check_result(failures: list[str]) -> None:
    result = read_json(RESULT)
    template = read_json(TEMPLATE_RESULT)
    boundary = read_json(BOUNDARY_RESULT)
    parent = result["parentTemplate"]
    dry_run = result["dryRunValidation"]
    rows = result["dryRunRows"]
    guard = result["guardSummary"]
    continuity = result["parentBoundaryContinuity"]

    require(result["schemaVersion"] == "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-runtime-message-display-observation-checklist-dry-run-validation.v1", "schema version mismatch", failures)
    require(result["status"] == "PASS", "result status mismatch", failures)
    require(result["directLevel100RuntimeMessageDisplayObservationChecklistDryRunValidationStatus"] == STATUS_TOKEN, "result status token mismatch", failures)
    require(result["nextStaticSlice"] == NEXT_SLICE, "next static slice mismatch", failures)

    static = result["staticContext"]
    require(static["staticFunctionQuality"] == "6411/6411 = 100.00%", "static function quality mismatch", failures)
    require(static["staticDebt"] == "0 / 0 / 0", "static debt mismatch", failures)
    require(static["expandedStaticSurface"] == "1560/1560 = 100.00%", "expanded static surface mismatch", failures)
    require(static["currentRiskFocused"] == "1179/1179 = 100.00%", "current-risk focused mismatch", failures)
    require(static["remainingActiveFocusedWork"] == 0, "remaining active focused work mismatch", failures)
    require(static["staticAccountingSource"] == "static-reaudit-measurement-register.md", "static accounting source mismatch", failures)
    require(static["latestGhidraBackupClass"] == "verified-static-backup-redacted", "backup class mismatch", failures)
    require(static["legacyStaticCounterRejected"] == "6113/6113", "legacy static counter mismatch", failures)

    require(template["status"] == "PASS", "parent template status mismatch", failures)
    require(template["directLevel100RuntimeMessageDisplayObservationChecklistTemplateStatus"] == TEMPLATE_STATUS_TOKEN, "parent template token mismatch", failures)
    require(boundary["status"] == "PASS", "parent boundary status mismatch", failures)
    require(boundary["directLevel100RuntimeMessageDisplayBoundaryStatus"] == BOUNDARY_STATUS_TOKEN, "parent boundary token mismatch", failures)
    require(parent["directLevel100RuntimeMessageDisplayObservationChecklistTemplateStatus"] == TEMPLATE_STATUS_TOKEN, "embedded template token mismatch", failures)
    require(parent["directLevel100RuntimeMessageDisplayBoundaryStatus"] == BOUNDARY_STATUS_TOKEN, "embedded boundary token mismatch", failures)
    require(parent["templateOnly"] is True, "parent templateOnly mismatch", failures)
    require(parent["runtimeExecution"] is False, "parent runtimeExecution mismatch", failures)
    require(parent["templateClassCount"] == 5, "parent template class count mismatch", failures)
    require(parent["privateFrameMessageObservationChecklistRows"] == 3, "parent private-frame count mismatch", failures)
    require(parent["sourceSelectionBoundaryRows"] == 1, "parent source-selection count mismatch", failures)
    require(parent["messageDisplayClassificationRows"] == 3, "parent message classification count mismatch", failures)
    require(parent["timingOrderClassificationRows"] == 1, "parent timing-order count mismatch", failures)
    require(parent["publicSafeResultSummaryRows"] == 1, "parent public summary count mismatch", failures)
    require(parent["requiredFutureProofArtifactCount"] == 5, "parent required artifact count mismatch", failures)
    require(parent["requiredFutureProofArtifacts"] == list(ARTIFACT_KEYS), "parent artifact key order mismatch", failures)
    require(parent["publicAllowedOutputs"] == ["class-counts", "status-tokens", "claim-boundary", "no-raw-dialogue", "no-private-paths", "no-frame-hashes"], "parent public outputs mismatch", failures)
    require(parent["defaultStatus"] == "not-run", "parent default status mismatch", failures)
    require(parent["observationStatus"] == "unobserved", "parent observation status mismatch", failures)
    require(parent["redactionPolicy"] == "public-safe-placeholder-only", "parent redaction policy mismatch", failures)
    require(parent["publicLeakCheck"] == "PASS", "parent public leak check mismatch", failures)

    require(dry_run["dryRunValidationOnly"] is True, "dry-run validation-only flag mismatch", failures)
    require(dry_run["templateOnly"] is True, "dry-run templateOnly mismatch", failures)
    require(dry_run["runtimeExecution"] is False, "dry-run runtimeExecution mismatch", failures)
    require(dry_run["validationMethod"] == "schema-and-guard-dry-run-no-private-frame-review", "dry-run method mismatch", failures)
    require(dry_run["templateMutation"] is False, "template mutation guard mismatch", failures)
    require(dry_run["templateClassCount"] == 5, "dry-run template class count mismatch", failures)
    require(dry_run["dryRunTemplateClassCount"] == 5, "dry-run template count mismatch", failures)
    require(dry_run["dryRunArtifactKeyCount"] == 5, "dry-run artifact key count mismatch", failures)
    require(dry_run["dryRunRowFamilyCount"] == 5, "dry-run row family count mismatch", failures)
    require(dry_run["dryRunValidationRows"] == 9, "dry-run validation row count mismatch", failures)
    require(dry_run["allowedRowStatusesCount"] == 5, "allowed status count mismatch", failures)
    require(dry_run["allowedRowStatuses"] == ["not-run", "observed", "inconclusive", "blocked", "out-of-scope"], "allowed statuses mismatch", failures)
    require(dry_run["defaultStatusesNotRun"] is True, "default status validation mismatch", failures)
    require(dry_run["observationStatusesUnobserved"] is True, "observation status validation mismatch", failures)
    require(dry_run["falseGuardCount"] == len(FALSE_GUARDS), "false guard count mismatch", failures)
    require(dry_run["zeroCounterCount"] == len(ZERO_COUNTS), "zero counter count mismatch", failures)
    require(dry_run["allActionGuardsFalse"] is True, "all action guards false mismatch", failures)
    require(dry_run["allLeakCountersZero"] is True, "all leak counters zero mismatch", failures)
    require(dry_run["publicAllowedOutputsMatched"] is True, "public allowed outputs mismatch", failures)
    require(dry_run["requiredFutureProofArtifactCount"] == 5, "required future artifact count mismatch", failures)
    require(dry_run["requiredFutureProofArtifactDryRunCount"] == 5, "required future artifact dry-run count mismatch", failures)
    require(dry_run["requiredFutureProofArtifacts"] == list(ARTIFACT_KEYS), "required future artifact list mismatch", failures)
    require(dry_run["publicAllowedOutputs"] == parent["publicAllowedOutputs"], "dry-run public output list mismatch", failures)

    require(len(rows) == 5, "dry-run row family length mismatch", failures)
    require([row["artifactKey"] for row in rows] == list(ARTIFACT_KEYS), "dry-run artifact key order mismatch", failures)
    require([row["templateClass"] for row in rows] == list(TEMPLATE_CLASSES), "dry-run template class order mismatch", failures)
    require(sum(row["dryRunRows"] for row in rows) == 9, "dry-run row total mismatch", failures)
    for row in rows:
        key = row["artifactKey"]
        require(row["templateRows"] == TEMPLATE_ROW_COUNTS[key], f"template row count mismatch: {key}", failures)
        require(row["dryRunRows"] == TEMPLATE_ROW_COUNTS[key], f"dry-run row count mismatch: {key}", failures)
        require(row["dryRunStatus"] == "PASS", f"dry-run row status mismatch: {key}", failures)
        require(row["defaultStatusValidated"] is True, f"default status not validated: {key}", failures)
        require(row["observationStatusValidated"] is True, f"observation status not validated: {key}", failures)
        require(row["actionGuardsFalse"] is True, f"action guard mismatch: {key}", failures)
        require(row["leakCountersZero"] is True, f"leak counter mismatch: {key}", failures)
        require(row["runtimeObservationRows"] == 0, f"runtime observation rows not zero: {key}", failures)

    require(continuity["messageDisplayBoundaryRows"] == 3, "continuity boundary row count mismatch", failures)
    require(continuity["messageDisplayCandidateFrameRows"] == 3, "continuity candidate frame count mismatch", failures)
    require(continuity["progressionCorrelationRows"] == 4, "continuity progression count mismatch", failures)
    require(continuity["publicFrameClassBuckets"] == "exterior-world-no-tutorial-panel:1/cockpit-hud-tutorial-overlay:3", "frame class bucket mismatch", failures)
    require(continuity["timedFrameSetTextOverlayProgressionClass"] == "exterior-world-to-cockpit-hud-tutorial-overlay-change-class", "progression class mismatch", failures)
    require(continuity["relevantStaticTokensResolved"] == "68/68", "static token resolution mismatch", failures)
    require(continuity["missingReferenceTokens"] == 0, "missing reference token mismatch", failures)
    require(continuity["speakerTokens"] == ["P_TATIANA", "P_KRAMER", "P_TECHNICIAN"], "speaker token list mismatch", failures)

    require(guard["dryRunValidationOnly"] is True, "guard dryRunValidationOnly mismatch", failures)
    require(guard["templateOnly"] is True, "guard templateOnly mismatch", failures)
    for key in FALSE_GUARDS:
        require(guard[key] is False, f"guard must be false: {key}", failures)
    for key in ZERO_COUNTS:
        require(guard[key] == 0, f"guard count must be zero: {key}", failures)
    require(guard["publicLeakCheckMode"] == "regex-and-field-scan", "public leak check mode mismatch", failures)
    require(guard["forbiddenPublicRegexesChecked"] is True, "forbidden public regex check flag mismatch", failures)
    require(guard["publicLeakCheck"] == "PASS", "guard public leak check mismatch", failures)

    proves = result["claimBoundary"]["proves"]
    unproven = result["claimBoundary"]["doesNotProve"]
    require("the runtime message-display observation checklist template can be dry-run validated as a five-class, nine-row-family public-safe contract" in proves, "claim boundary missing dry-run proof", failures)
    for token in (
        "runtime MissionScript execution",
        "Level100 script source selection",
        "runtime message display behavior",
        "exact visible text identity",
        "OCR identity",
        "raw dialogue text",
        "Godot parity",
        "rebuild parity",
        "no-noticeable-difference parity",
    ):
        require(token in unproven, f"claim boundary missing unproven token: {token}", failures)

    require(no_bea_process_running(), "BEA process still running after dry-run validation", failures)
    for path in (PLAN, LORE_PLAN, RESULT, LORE_RESULT, READINESS):
        check_no_bad_tokens(path, failures)


def check_docs(failures: list[str]) -> None:
    core_tokens = (
        THIS_SLICE,
        PREVIOUS_SLICE,
        NEXT_SLICE,
        PLAN_LINK,
        RESULT_LINK,
        TEMPLATE_LINK,
        TEMPLATE_RESULT_LINK,
        f"directLevel100RuntimeMessageDisplayObservationChecklistDryRunValidationStatus={STATUS_TOKEN}",
        f"directLevel100RuntimeMessageDisplayObservationChecklistTemplateStatus={TEMPLATE_STATUS_TOKEN}",
        f"directLevel100RuntimeMessageDisplayBoundaryStatus={BOUNDARY_STATUS_TOKEN}",
        "dryRunValidationOnly=true",
        "templateOnly=true",
        "runtimeExecution=false",
        "validationMethod=schema-and-guard-dry-run-no-private-frame-review",
        "templateMutation=false",
        "templateClassCount=5",
        "dryRunTemplateClassCount=5",
        "dryRunArtifactKeyCount=5",
        "dryRunRowFamilyCount=5",
        "dryRunValidationRows=9",
        "allowedRowStatuses=not-run/observed/inconclusive/blocked/out-of-scope",
        "defaultStatusesNotRun=true",
        "observationStatusesUnobserved=true",
        "falseGuardCount=33",
        "zeroCounterCount=9",
        "messageDisplayBoundaryRows=3",
        "messageDisplayCandidateFrameRows=3",
        "progressionCorrelationRows=4",
        "publicFrameClassBuckets=exterior-world-no-tutorial-panel:1/cockpit-hud-tutorial-overlay:3",
        "timedFrameSetTextOverlayProgressionClass=exterior-world-to-cockpit-hud-tutorial-overlay-change-class",
        "relevantStaticTokensResolved=68/68",
        "missingReferenceTokens=0",
        "messageObservationPerformed=false",
        "beLaunch=false",
        "launchArmed=false",
        "screenshotCapture=false",
        "exactTextOcrPerformed=false",
        "rawDialogueIncluded=false",
        "rawDialoguePublished=false",
        "visibleTextExcerptPublished=false",
        "exactVisibleTokenIdentityClaim=false",
        "exactVisibleTokenIdentityProven=false",
        "perFrameTokenIdentityClaim=false",
        "perFrameSpeakerIdentityClaim=false",
        "runtimeMessageDisplayClaim=false",
        "runtimeMessageDisplayProven=false",
        "sourceSelectionObserved=false",
        "sourceSelectionProven=false",
        "messageDisplayClassificationProven=false",
        "timingOrderProven=false",
        "missionScriptRuntimeEvidenceRows=0",
        "nativeInput=false",
        "debuggerAttachment=false",
        "godotWork=false",
        "publicLeakCheckMode=regex-and-field-scan",
        "publicAbsolutePathLeakCount=0",
        "publicSha256ValueLeakCount=0",
        "publicWindowIdentifierLeakCount=0",
        "publicProcessIdentifierLeakCount=0",
        "privatePathLeakCount=0",
        "rawArtifactLeakCount=0",
        "rawDialogueLeakCount=0",
        "beProcessesAfterDryRun=0",
        "publicLeakCheck=PASS",
        "staticAccountingSource=static-reaudit-measurement-register.md",
        "latestGhidraBackupClass=verified-static-backup-redacted",
        "legacyStaticCounterRejected=6113/6113",
    )
    for path in (PLAN, READINESS):
        text = read_text(path)
        for token in core_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing token: {token}", failures)

    front_door_tokens = (
        PLAN_LINK,
        RESULT_LINK,
        THIS_SLICE,
        PREVIOUS_SLICE,
        NEXT_SLICE,
        STATUS_TOKEN,
        TEMPLATE_STATUS_TOKEN,
        "dryRunValidationRows=9",
        "falseGuardCount=33",
        "zeroCounterCount=9",
        "beLaunch=false",
        "launchArmed=false",
        "screenshotCapture=false",
        "runtimeMessageDisplayClaim=false",
        "runtimeMessageDisplayProven=false",
        "sourceSelectionObserved=false",
        "missionScriptRuntimeEvidenceRows=0",
        "publicLeakCheck=PASS",
    )
    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX):
        text = read_text(path)
        for token in front_door_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing dry-run token: {token}", failures)

    for source, mirror in (
        (PLAN, LORE_PLAN),
        (RESULT, LORE_RESULT),
        (BACKLOG, LORE_BACKLOG),
        (MAPPED, LORE_MAPPED),
        (BIN_INDEX, LORE_BIN_INDEX),
        (RE_INDEX, LORE_RE_INDEX),
    ):
        require(read_text(source) == read_text(mirror), f"lore mirror mismatch for {source.relative_to(ROOT)}", failures)

    backlog = read_text(BACKLOG)
    require(f"Completed {PREVIOUS_SLICE}" in backlog, "backlog missing completed checklist-template slice", failures)
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed dry-run slice", failures)
    require(
        f"The selected active static-to-proof slice is {NEXT_SLICE}" in backlog
        or f"Completed {NEXT_SLICE}" in backlog,
        "backlog missing active/completed private-frame arm-boundary slice",
        failures,
    )
    require(f"The selected active static-to-proof slice is {THIS_SLICE}. Status: selected" not in backlog, "backlog still marks dry-run slice active", failures)
    require(f"The selected active static-to-proof slice is {PREVIOUS_SLICE}. Status: selected" not in backlog, "backlog still marks checklist-template slice active", failures)


def check_package(failures: list[str]) -> None:
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-runtime-message-display-observation-checklist-dry-run-validation")
        == r"py -3 tools\missionscript_level100_tutorial_copied_profile_runtime_observation_direct_level100_runtime_message_display_observation_checklist_dry_run_validation_probe.py --check",
        "missing package direct Level100 runtime message display checklist dry-run test script",
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
        print("MissionScript Level100 runtime message display checklist dry-run validation probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("MissionScript Level100 runtime message display checklist dry-run validation probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
