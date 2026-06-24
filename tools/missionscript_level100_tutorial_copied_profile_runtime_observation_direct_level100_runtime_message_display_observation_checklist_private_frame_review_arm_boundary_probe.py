#!/usr/bin/env python3
"""Validate the MissionScript Level100 private-frame review arm boundary."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "level100-message-private-frame-arm-boundary.md"
LORE_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "level100-message-private-frame-arm-boundary.md"
RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "level100-message-private-frame-arm-boundary.v1.json"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "level100-message-private-frame-arm-boundary.v1.json"
DRY_RUN_RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "level100-message-checklist-dry-run-validation.v1.json"
TEMPLATE_RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-runtime-message-display-observation-checklist-template.v1.json"
BOUNDARY_RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-runtime-message-display-boundary.v1.json"
READINESS = ROOT / "release" / "readiness" / "missionscript_level100_tutorial_copied_profile_runtime_observation_direct_level100_runtime_message_display_observation_checklist_private_frame_review_arm_boundary_2026-06-09.md"
BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
LORE_MAPPED = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
LORE_BIN_INDEX = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
LORE_RE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"
PACKAGE_JSON = ROOT / "package.json"

THIS_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Runtime Message Display Observation Checklist Private-Frame Review Arm Boundary Proof Plan"
PREVIOUS_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Runtime Message Display Observation Checklist Dry-Run Validation Proof Plan"
NEXT_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Runtime Message Display Observation Checklist Private-Frame Review Checklist Population Proof Plan"
PLAN_LINK = "level100-message-private-frame-arm-boundary.md"
RESULT_LINK = "level100-message-private-frame-arm-boundary.v1.json"
DRY_RUN_LINK = "level100-message-checklist-dry-run-validation.md"
DRY_RUN_RESULT_LINK = "level100-message-checklist-dry-run-validation.v1.json"
STATUS_TOKEN = "direct-level100-runtime-message-display-observation-checklist-private-frame-review-arm-boundary-defined-no-private-frame-review-performed"
DRY_RUN_STATUS_TOKEN = "direct-level100-runtime-message-display-observation-checklist-dry-run-validation-pass-no-runtime-message-proof"
TEMPLATE_STATUS_TOKEN = "direct-level100-runtime-message-display-observation-checklist-template-defined-no-runtime-message-proof"
BOUNDARY_STATUS_TOKEN = "direct-level100-runtime-message-display-boundary-defined-no-runtime-message-proof"

ARTIFACT_KEYS = (
    "private-frame-message-observation-checklist",
    "source-selection-boundary-row",
    "message-display-classification-row",
    "timing-order-classification-row",
    "public-safe-result-summary",
)

FALSE_GUARDS = (
    "runtimeExecution",
    "newLaunch",
    "beLaunch",
    "launchArmed",
    "screenshotCapture",
    "newScreenshotCapture",
    "newPrivateFrameCapture",
    "privateFrameReviewArmed",
    "privateFrameReviewPerformed",
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
    "privateProofAssetPublished",
    "privateCaptureLocatorIncluded",
    "privateArtifactHashIncluded",
    "privateArtifactBytesIncluded",
    "privateWindowIdentifiersIncluded",
    "publicMachinePathIncluded",
    "publicResultContainsPrivateFrameDetails",
    "publicResultContainsRawDialogue",
    "publicResultContainsExactText",
    "publicResultContainsOcrText",
    "publicResultContainsSourceSelectionClaim",
    "ghidraMutation",
    "templateMutation",
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
    "beProcessesAfterArmBoundary",
    "observedChecklistRows",
    "publishedPrivateFrameRows",
)

FORBIDDEN_PUBLIC_PATTERNS = (
    (re.compile(r"\b[A-Za-z]:[\\/]"), "machine-local absolute path"),
    (re.compile(r"\b[a-fA-F0-9]{64}\b"), "raw digest-like value"),
    (re.compile(r"(?i)c:[\\/]users"), "user profile path"),
    (re.compile(r"(?i)g:[\\/]"), "private backup path"),
    (re.compile(r"(?i)program files"), "installed game path"),
    (re.compile(r"(?i)steamapps"), "installed game path"),
    (re.compile(r"(?i)subagents[\\/]"), "subagent artifact path"),
    (re.compile(r"(?i)private_runtime_evidence"), "private runtime evidence marker"),
    (re.compile(r"(?i)hwnd"), "window identifier"),
    (re.compile(r"(?i)capture source hint"), "capture-source hint"),
    (re.compile(r"(?i)capturepath|framepath|capturehash|framehash|framesha256|framebytelength"), "private frame locator/hash field"),
    (re.compile(r"(?i)\.private\.png"), "private frame filename"),
    (re.compile(r"(?i)frame-05s|frame-10s|frame-15s|frame-25s"), "private frame filename"),
    (re.compile(r"(?i)level100-clean-materialized-[0-9]"), "copied-profile concrete identifier"),
    (re.compile(r"(?i)save-attempts"), "private save path"),
    (re.compile(r"(?i)onslaught_codex_directive"), "operator directive marker"),
    (re.compile(r"(?i)password|token="), "secret-like marker"),
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
    "timing correctness proven",
    "visual correctness proven",
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


def check_no_bad_public_content(path: Path, failures: list[str]) -> None:
    text = read_text(path)
    lower = text.lower()
    for pattern, category in FORBIDDEN_PUBLIC_PATTERNS:
        require(pattern.search(text) is None, f"{path.relative_to(ROOT)} leaks forbidden public category: {category}", failures)
    for phrase in FORBIDDEN_OVERCLAIMS:
        require(phrase not in lower, f"{path.relative_to(ROOT)} overclaims forbidden category", failures)


def check_result(failures: list[str]) -> None:
    result = read_json(RESULT)
    dry_run = read_json(DRY_RUN_RESULT)
    template = read_json(TEMPLATE_RESULT)
    boundary = read_json(BOUNDARY_RESULT)
    parent = result["parentDryRunValidation"]
    parent_template = result["parentTemplate"]
    continuity = result["parentBoundaryContinuity"]
    arm = result["armBoundaryDefinition"]
    policy = result["rowPopulationPolicy"]
    redaction = result["redactionPolicy"]
    guard = result["guardSummary"]

    require(result["schemaVersion"] == "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-runtime-message-display-observation-checklist-private-frame-review-arm-boundary.v1", "schema version mismatch", failures)
    require(result["status"] == "PASS", "result status mismatch", failures)
    require(result["directLevel100RuntimeMessageDisplayObservationChecklistPrivateFrameReviewArmBoundaryStatus"] == STATUS_TOKEN, "status token mismatch", failures)
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

    require(dry_run["status"] == "PASS", "parent dry-run result status mismatch", failures)
    require(dry_run["directLevel100RuntimeMessageDisplayObservationChecklistDryRunValidationStatus"] == DRY_RUN_STATUS_TOKEN, "parent dry-run status token mismatch", failures)
    require(template["directLevel100RuntimeMessageDisplayObservationChecklistTemplateStatus"] == TEMPLATE_STATUS_TOKEN, "parent template status token mismatch", failures)
    require(boundary["directLevel100RuntimeMessageDisplayBoundaryStatus"] == BOUNDARY_STATUS_TOKEN, "parent boundary status token mismatch", failures)

    require(parent["directLevel100RuntimeMessageDisplayObservationChecklistDryRunValidationStatus"] == DRY_RUN_STATUS_TOKEN, "embedded dry-run status mismatch", failures)
    require(parent["directLevel100RuntimeMessageDisplayObservationChecklistTemplateStatus"] == TEMPLATE_STATUS_TOKEN, "embedded template status mismatch", failures)
    require(parent["dryRunValidationOnly"] is True, "embedded dry-run flag mismatch", failures)
    require(parent["templateOnly"] is True, "embedded template-only flag mismatch", failures)
    require(parent["runtimeExecution"] is False, "embedded runtime flag mismatch", failures)
    require(parent["templateClassCount"] == 5, "embedded template class count mismatch", failures)
    require(parent["dryRunValidationRows"] == 9, "embedded dry-run validation row count mismatch", failures)
    require(parent["allowedRowStatuses"] == ["not-run", "observed", "inconclusive", "blocked", "out-of-scope"], "embedded status vocabulary mismatch", failures)
    require(parent["defaultStatusesNotRun"] is True, "embedded default status mismatch", failures)
    require(parent["observationStatusesUnobserved"] is True, "embedded observation status mismatch", failures)
    require(parent["publicLeakCheck"] == "PASS", "embedded public leak check mismatch", failures)
    require(parent_template["directLevel100RuntimeMessageDisplayObservationChecklistTemplateStatus"] == TEMPLATE_STATUS_TOKEN, "embedded parent template token mismatch", failures)
    require(parent_template["templateClassCount"] == 5, "embedded parent template class count mismatch", failures)
    require(parent_template["defaultStatus"] == "not-run", "embedded parent template default mismatch", failures)
    require(parent_template["observationStatus"] == "unobserved", "embedded parent template observation mismatch", failures)
    require(continuity["directLevel100RuntimeMessageDisplayBoundaryStatus"] == BOUNDARY_STATUS_TOKEN, "embedded parent boundary token mismatch", failures)
    require(continuity["directLevel100TimedFrameSetTextOverlayProgressionCorrelationStatus"] == "direct-level100-timed-frame-set-text-overlay-progression-correlated-to-static-level100-token-surface", "embedded progression token mismatch", failures)
    require(continuity["messageDisplayBoundaryRows"] == 3, "embedded boundary rows mismatch", failures)
    require(continuity["messageDisplayCandidateFrameRows"] == 3, "embedded candidate frame rows mismatch", failures)
    require(continuity["progressionCorrelationRows"] == 4, "embedded progression rows mismatch", failures)
    require(continuity["relevantStaticTokensResolved"] == "68/68", "embedded static token resolution mismatch", failures)
    require(continuity["missingReferenceTokens"] == 0, "embedded missing reference mismatch", failures)

    require(arm["armBoundaryOnly"] is True, "arm boundary-only flag mismatch", failures)
    require(arm["reviewArmBoundaryDefined"] is True, "review boundary-defined flag mismatch", failures)
    require(arm["runtimeExecution"] is False, "arm runtime flag mismatch", failures)
    require(arm["privateFrameReviewArmed"] is False, "private frame review must not be armed", failures)
    require(arm["privateFrameReviewPerformed"] is False, "private frame review must not be performed", failures)
    require(arm["futureReviewRequiresExplicitOperatorArm"] is True, "future operator arm requirement mismatch", failures)
    require(arm["armBoundaryMethod"] == "public-safe-policy-contract-from-dry-run-checklist", "arm boundary method mismatch", failures)
    require(arm["reviewablePrivateFrameClassCount"] == 1, "reviewable frame class count mismatch", failures)
    require(arm["reviewablePrivateFrameRows"] == 3, "reviewable frame row count mismatch", failures)
    require(arm["reviewablePrivateFrameClasses"] == ["direct-level100-cockpit-hud-tutorial-overlay-private-frame-class"], "reviewable frame class mismatch", failures)
    require(arm["armableArtifactKeyCount"] == 5, "armable artifact key count mismatch", failures)
    require(arm["armableArtifactKeys"] == list(ARTIFACT_KEYS), "armable artifact keys mismatch", failures)
    require(arm["armableChecklistRows"] == 9, "armable checklist rows mismatch", failures)
    require(arm["armablePrivateFrameRows"] == 3, "armable private frame rows mismatch", failures)
    require(arm["armableSourceSelectionRows"] == 1, "armable source selection rows mismatch", failures)
    require(arm["armableMessageDisplayClassificationRows"] == 3, "armable message display rows mismatch", failures)
    require(arm["armableTimingOrderRows"] == 1, "armable timing rows mismatch", failures)
    require(arm["armablePublicSummaryRows"] == 1, "armable public summary rows mismatch", failures)
    require(arm["allowedRowStatuses"] == ["not-run", "observed", "inconclusive", "blocked", "out-of-scope"], "arm status vocabulary mismatch", failures)
    require(arm["rowsAllowedToMoveOutOfNotRunOnlyAfterArm"] is True, "row movement arm guard mismatch", failures)
    require(arm["redactedFieldCount"] == 14, "redacted field count mismatch", failures)
    require(arm["stopConditionCount"] == 12, "stop condition count mismatch", failures)
    require(arm["falseGuardCount"] == len(FALSE_GUARDS), "false guard count mismatch", failures)
    require(arm["zeroCounterCount"] == len(ZERO_COUNTS), "zero counter count mismatch", failures)
    require(arm["publicAllowedOutputs"] == ["class-counts", "status-tokens", "claim-boundary", "no-raw-dialogue", "no-private-paths", "no-frame-hashes"], "public outputs mismatch", failures)
    require(policy["rowStatusMutationPerformed"] is False, "row status mutation guard mismatch", failures)
    require(policy["allCurrentRowsRemainNotRun"] is True, "current not-run row guard mismatch", failures)
    require(policy["allCurrentObservationsRemainUnobserved"] is True, "current unobserved guard mismatch", failures)
    require(len(policy["allowedLaterRowTransitions"]) == 4, "allowed later row transition count mismatch", failures)
    require(policy["artifactFamilies"] == list(ARTIFACT_KEYS), "row policy artifact families mismatch", failures)

    require(redaction["redactionPolicy"] == "public-safe-placeholder-only", "redaction policy mismatch", failures)
    require(len(redaction["redactedFields"]) == 14, "redacted fields length mismatch", failures)
    require(redaction["publicAllowedOutputs"] == arm["publicAllowedOutputs"], "redaction public outputs mismatch", failures)
    require(redaction["publicLeakCheck"] == "PASS", "redaction public leak check mismatch", failures)
    require(len(result["stopConditions"]) == 12, "stop condition length mismatch", failures)

    require(guard["armBoundaryOnly"] is True, "guard armBoundaryOnly mismatch", failures)
    require(guard["reviewArmBoundaryDefined"] is True, "guard reviewArmBoundaryDefined mismatch", failures)
    require(guard["futureReviewRequiresExplicitOperatorArm"] is True, "guard future arm mismatch", failures)
    for key in FALSE_GUARDS:
        require(guard[key] is False, f"guard must be false: {key}", failures)
    for key in ZERO_COUNTS:
        require(guard[key] == 0, f"guard count must be zero: {key}", failures)
    require(guard["publicLeakCheck"] == "PASS", "guard public leak check mismatch", failures)

    proves = result["claimBoundary"]["proves"]
    unproven = result["claimBoundary"]["doesNotProve"]
    require("the validated dry-run checklist has an explicit public-safe arm boundary for later private-frame review" in proves, "claim boundary missing arm-boundary proof", failures)
    for token in (
        "runtime MissionScript execution",
        "Level100 script source selection",
        "runtime message display behavior",
        "exact visible text identity",
        "OCR identity",
        "raw dialogue text",
        "timing correctness",
        "Godot parity",
        "rebuild parity",
        "no-noticeable-difference parity",
    ):
        require(token in unproven, f"claim boundary missing unproven token: {token}", failures)

    require(no_bea_process_running(), "BEA process still running after arm-boundary validation", failures)
    for path in (PLAN, LORE_PLAN, RESULT, LORE_RESULT, READINESS):
        check_no_bad_public_content(path, failures)


def check_docs(failures: list[str]) -> None:
    core_tokens = (
        THIS_SLICE,
        PREVIOUS_SLICE,
        NEXT_SLICE,
        PLAN_LINK,
        RESULT_LINK,
        DRY_RUN_LINK,
        DRY_RUN_RESULT_LINK,
        f"directLevel100RuntimeMessageDisplayObservationChecklistPrivateFrameReviewArmBoundaryStatus={STATUS_TOKEN}",
        f"directLevel100RuntimeMessageDisplayObservationChecklistDryRunValidationStatus={DRY_RUN_STATUS_TOKEN}",
        "armBoundaryOnly=true",
        "reviewArmBoundaryDefined=true",
        "runtimeExecution=false",
        "privateFrameReviewArmed=false",
        "privateFrameReviewPerformed=false",
        "futureReviewRequiresExplicitOperatorArm=true",
        "armBoundaryMethod=public-safe-policy-contract-from-dry-run-checklist",
        "reviewablePrivateFrameClassCount=1",
        "reviewablePrivateFrameRows=3",
        "armableArtifactKeyCount=5",
        "armableChecklistRows=9",
        "armablePrivateFrameRows=3",
        "armableSourceSelectionRows=1",
        "armableMessageDisplayClassificationRows=3",
        "armableTimingOrderRows=1",
        "armablePublicSummaryRows=1",
        "allowedRowStatuses=not-run/observed/inconclusive/blocked/out-of-scope",
        "rowsAllowedToMoveOutOfNotRunOnlyAfterArm=true",
        "redactedFieldCount=14",
        "stopConditionCount=12",
        "falseGuardCount=40",
        "zeroCounterCount=11",
        "beLaunch=false",
        "launchArmed=false",
        "screenshotCapture=false",
        "messageObservationPerformed=false",
        "runtimeMessageDisplayClaim=false",
        "runtimeMessageDisplayProven=false",
        "sourceSelectionObserved=false",
        "sourceSelectionProven=false",
        "missionScriptRuntimeEvidenceRows=0",
        "nativeInput=false",
        "debuggerAttachment=false",
        "godotWork=false",
        "ghidraMutation=false",
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
        DRY_RUN_STATUS_TOKEN,
        "armBoundaryOnly=true",
        "privateFrameReviewArmed=false",
        "privateFrameReviewPerformed=false",
        "futureReviewRequiresExplicitOperatorArm=true",
        "reviewablePrivateFrameClassCount=1",
        "reviewablePrivateFrameRows=3",
        "armableChecklistRows=9",
        "redactedFieldCount=14",
        "stopConditionCount=12",
        "falseGuardCount=40",
        "zeroCounterCount=11",
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
            require(token in text, f"{path.relative_to(ROOT)} missing arm-boundary token: {token}", failures)

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
    require(f"Completed {PREVIOUS_SLICE}" in backlog, "backlog missing completed dry-run slice", failures)
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed arm-boundary slice", failures)
    require(
        f"The selected active static-to-proof slice is {NEXT_SLICE}" in backlog
        or f"Completed {NEXT_SLICE}" in backlog,
        "backlog missing active/completed checklist-population slice",
        failures,
    )
    require(f"The selected active static-to-proof slice is {THIS_SLICE}. Status: selected" not in backlog, "backlog still marks arm-boundary slice active", failures)
    require(f"The selected active static-to-proof slice is {PREVIOUS_SLICE}. Status: selected" not in backlog, "backlog still marks dry-run slice active", failures)


def check_package(failures: list[str]) -> None:
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-runtime-message-display-observation-checklist-private-frame-review-arm-boundary")
        == r"py -3 tools\missionscript_level100_tutorial_copied_profile_runtime_observation_direct_level100_runtime_message_display_observation_checklist_private_frame_review_arm_boundary_probe.py --check",
        "missing package direct Level100 private-frame arm-boundary test script",
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
        print("MissionScript Level100 private-frame review arm-boundary probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("MissionScript Level100 private-frame review arm-boundary probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
