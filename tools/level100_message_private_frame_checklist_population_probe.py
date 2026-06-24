#!/usr/bin/env python3
"""Validate the Level100 private-frame checklist-population deferred proof."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "level100-message-private-frame-checklist-population.md"
RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "level100-message-private-frame-checklist-population.v1.json"
LORE_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "level100-message-private-frame-checklist-population.md"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "level100-message-private-frame-checklist-population.v1.json"
READINESS = ROOT / "release" / "readiness" / "level100_message_private_frame_checklist_population_2026-06-09.md"
BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
LORE_MAPPED = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
LORE_BIN_INDEX = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
LORE_RE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"
PACKAGE_JSON = ROOT / "package.json"

ARM_RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "level100-message-private-frame-arm-boundary.v1.json"
DRY_RUN_RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "level100-message-checklist-dry-run-validation.v1.json"

THIS_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Runtime Message Display Observation Checklist Private-Frame Review Checklist Population Proof Plan"
PREVIOUS_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Runtime Message Display Observation Checklist Private-Frame Review Arm Boundary Proof Plan"
NEXT_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Runtime Message Display Observation Public-Safe Result Summary Proof Plan"

STATUS_TOKEN = "direct-level100-runtime-message-display-observation-checklist-private-frame-review-checklist-population-deferred-pending-explicit-operator-arm"
ARM_STATUS_TOKEN = "direct-level100-runtime-message-display-observation-checklist-private-frame-review-arm-boundary-defined-no-private-frame-review-performed"
DRY_RUN_STATUS_TOKEN = "direct-level100-runtime-message-display-observation-checklist-dry-run-validation-pass-no-runtime-message-proof"

ARTIFACT_KEYS = (
    "private-frame-message-observation-checklist",
    "source-selection-boundary-row",
    "message-display-classification-row",
    "timing-order-classification-row",
    "public-safe-result-summary",
)

FALSE_GUARDS = (
    "operatorArmRecorded",
    "privateFrameReviewArmPhraseRecorded",
    "privateFrameReviewMayProceed",
    "runtimeExecution",
    "newLaunch",
    "beLaunch",
    "launchArmed",
    "screenshotCapture",
    "newScreenshotCapture",
    "newPrivateFrameCapture",
    "privateFrameReviewArmed",
    "privateFrameReviewPerformed",
    "checklistObservationPerformed",
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
    "publicResultTreatsSkeletonAsObservation",
    "publicResultTreatsSummaryAsRuntimeProof",
    "ghidraMutation",
    "templateMutation",
    "rowStatusMutationPerformed",
)

ZERO_COUNTS = (
    "runtimeObservationRows",
    "missionScriptRuntimeEvidenceRows",
    "publicAbsolutePathLeakCount",
    "publicSha256ValueLeakCount",
    "publicWindowIdentifierLeakCount",
    "publicProcessIdentifierLeakCount",
    "privatePathLeakCount",
    "rawArtifactLeakCount",
    "rawDialogueLeakCount",
    "beProcessesAfterChecklistPopulation",
    "observedChecklistRows",
    "publishedPrivateFrameRows",
    "checklistRowsWithPrivateLocator",
    "checklistRowsWithPrivateDigest",
    "checklistRowsWithRawDialogue",
    "checklistRowsWithExactText",
    "checklistRowsWithOcrText",
    "checklistRowsWithWindowIdentifier",
    "checklistRowsWithProcessIdentifier",
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
    "runtime message display observed",
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
    "audio behavior proven",
    "objective ui proven",
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
    arm = read_json(ARM_RESULT)
    dry = read_json(DRY_RUN_RESULT)
    summary = result["checklistPopulationSummary"]
    auth = result["authorizationBoundary"]
    parent_arm = result["parentArmBoundary"]
    guard = result["guardSummary"]

    require(result["schemaVersion"] == "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-runtime-message-display-observation-checklist-private-frame-review-checklist-population.v1", "schema version mismatch", failures)
    require(result["status"] == "PASS", "result status mismatch", failures)
    require(result["directLevel100RuntimeMessageDisplayObservationChecklistPrivateFrameReviewChecklistPopulationStatus"] == STATUS_TOKEN, "status token mismatch", failures)
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

    require(arm["directLevel100RuntimeMessageDisplayObservationChecklistPrivateFrameReviewArmBoundaryStatus"] == ARM_STATUS_TOKEN, "parent arm result token mismatch", failures)
    require(dry["directLevel100RuntimeMessageDisplayObservationChecklistDryRunValidationStatus"] == DRY_RUN_STATUS_TOKEN, "parent dry-run result token mismatch", failures)
    require(parent_arm["directLevel100RuntimeMessageDisplayObservationChecklistPrivateFrameReviewArmBoundaryStatus"] == ARM_STATUS_TOKEN, "embedded arm token mismatch", failures)
    require(parent_arm["privateFrameReviewArmed"] is False, "embedded parent arm should be false", failures)
    require(parent_arm["privateFrameReviewPerformed"] is False, "embedded parent performed should be false", failures)
    require(parent_arm["futureReviewRequiresExplicitOperatorArm"] is True, "embedded future arm guard mismatch", failures)
    require(parent_arm["reviewablePrivateFrameRows"] == 3, "embedded reviewable private-frame rows mismatch", failures)
    require(parent_arm["armableChecklistRows"] == 9, "embedded armable checklist rows mismatch", failures)

    require(auth["operatorArmRecorded"] is False, "operator arm must not be recorded", failures)
    require(auth["privateFrameReviewArmPhraseRecorded"] is False, "private-frame arm phrase must not be recorded", failures)
    require(auth["privateFrameReviewMayProceed"] is False, "private-frame review may not proceed", failures)
    require(auth["blockedByMissingExplicitOperatorArm"] is True, "missing explicit operator arm blocker mismatch", failures)
    require(auth["allowedCurrentAction"] == "public-safe-checklist-row-skeleton-materialization-only", "allowed current action mismatch", failures)

    require(summary["checklistPopulationOnly"] is True, "population-only flag mismatch", failures)
    require(summary["publicSafeChecklistRowsMaterialized"] is True, "public-safe materialization flag mismatch", failures)
    require(summary["checklistFamilyCount"] == 5, "checklist family count mismatch", failures)
    require(summary["checklistRowsMaterialized"] == 9, "checklist row count mismatch", failures)
    require(summary["privateFrameMessageObservationChecklistRows"] == 3, "private-frame row count mismatch", failures)
    require(summary["sourceSelectionBoundaryRows"] == 1, "source-selection row count mismatch", failures)
    require(summary["messageDisplayClassificationRows"] == 3, "message-display row count mismatch", failures)
    require(summary["timingOrderClassificationRows"] == 1, "timing row count mismatch", failures)
    require(summary["publicSafeResultSummaryRows"] == 1, "summary row count mismatch", failures)
    require(summary["defaultStatus"] == "not-run", "default status mismatch", failures)
    require(summary["observationStatus"] == "unobserved", "observation status mismatch", failures)
    require(summary["notRunRows"] == 9, "not-run row count mismatch", failures)
    require(summary["unobservedRows"] == 9, "unobserved row count mismatch", failures)
    for key in ("observedRows", "inconclusiveRows", "blockedRows", "outOfScopeRows", "rowStatusChangedCount", "runtimeObservationRows", "publishedPrivateFrameRows"):
        require(summary[key] == 0, f"summary count must be zero: {key}", failures)
    require(summary["falseGuardCount"] == len(FALSE_GUARDS), "false guard count mismatch", failures)
    require(summary["zeroCounterCount"] == len(ZERO_COUNTS), "zero counter count mismatch", failures)

    rows = result["checklistRows"]
    require(len(rows) == 9, "checklistRows length mismatch", failures)
    family_counts: dict[str, int] = {}
    for row in rows:
        family_counts[row["artifactKey"]] = family_counts.get(row["artifactKey"], 0) + 1
        require(row["artifactKey"] in ARTIFACT_KEYS, f"unknown row artifact key: {row['artifactKey']}", failures)
        require(row["status"] == "not-run", f"row not in not-run: {row['rowId']}", failures)
        require(row["observationStatus"] == "unobserved", f"row not unobserved: {row['rowId']}", failures)
        require(row["blocker"] == "explicit-private-frame-review-arm-absent", f"row blocker mismatch: {row['rowId']}", failures)
        require(row["runtimeObservationRows"] == 0, f"row runtime observations must be zero: {row['rowId']}", failures)
        require(row["publicFrameClass"] == "direct-level100-cockpit-hud-tutorial-overlay-private-frame-class", f"row public frame class mismatch: {row['rowId']}", failures)
    require(family_counts == {
        "private-frame-message-observation-checklist": 3,
        "source-selection-boundary-row": 1,
        "message-display-classification-row": 3,
        "timing-order-classification-row": 1,
        "public-safe-result-summary": 1,
    }, "row family counts mismatch", failures)

    policy = result["rowPopulationPolicy"]
    require(policy["rowStatusMutationPerformed"] is False, "row status mutation policy mismatch", failures)
    require(policy["allCurrentRowsRemainNotRun"] is True, "all rows remain not-run policy mismatch", failures)
    require(policy["allCurrentObservationsRemainUnobserved"] is True, "all rows remain unobserved policy mismatch", failures)
    require(policy["artifactFamilies"] == list(ARTIFACT_KEYS), "policy artifact families mismatch", failures)

    redaction = result["redactionPolicy"]
    require(redaction["redactionPolicy"] == "public-safe-placeholder-only", "redaction policy mismatch", failures)
    require(redaction["redactedFieldCount"] == 14, "redacted field count mismatch", failures)
    require(len(redaction["redactedFields"]) == 14, "redacted fields length mismatch", failures)
    require(redaction["publicLeakCheck"] == "PASS", "redaction public leak check mismatch", failures)

    for key in FALSE_GUARDS:
        require(guard[key] is False, f"guard must be false: {key}", failures)
    for key in ZERO_COUNTS:
        require(guard[key] == 0, f"guard count must be zero: {key}", failures)
    require(guard["blockedByMissingExplicitOperatorArm"] is True, "guard missing-arm blocker mismatch", failures)
    require(guard["checklistPopulationOnly"] is True, "guard population-only mismatch", failures)
    require(guard["publicSafeChecklistRowsMaterialized"] is True, "guard materialized mismatch", failures)
    require(guard["publicLeakCheck"] == "PASS", "guard public leak check mismatch", failures)
    require(len(result["stopConditions"]) == 12, "stop condition count mismatch", failures)

    proves = result["claimBoundary"]["proves"]
    unproven = result["claimBoundary"]["doesNotProve"]
    require("the validated five-family checklist can be materialized as nine public-safe rows" in proves, "claim boundary missing row skeleton proof", failures)
    require("the missing explicit private-frame review arm is a real blocker for observation, not a reason to infer runtime behavior" in proves, "claim boundary missing blocker proof", failures)
    for token in (
        "exact visible text identity",
        "OCR identity",
        "raw dialogue text",
        "per-frame token identity",
        "per-frame speaker identity",
        "runtime MissionScript execution",
        "Level100 script source selection",
        "runtime message display behavior",
        "timing correctness",
        "Godot parity",
        "rebuild parity",
        "no-noticeable-difference parity",
    ):
        require(token in unproven, f"claim boundary missing unproven token: {token}", failures)

    require(no_bea_process_running(), "BEA process still running after checklist-population validation", failures)
    for path in (PLAN, LORE_PLAN, RESULT, LORE_RESULT, READINESS):
        check_no_bad_public_content(path, failures)


def check_docs(failures: list[str]) -> None:
    core_tokens = (
        THIS_SLICE,
        PREVIOUS_SLICE,
        NEXT_SLICE,
        "level100-message-private-frame-checklist-population.md",
        "level100-message-private-frame-checklist-population.v1.json",
        f"directLevel100RuntimeMessageDisplayObservationChecklistPrivateFrameReviewChecklistPopulationStatus={STATUS_TOKEN}",
        f"directLevel100RuntimeMessageDisplayObservationChecklistPrivateFrameReviewArmBoundaryStatus={ARM_STATUS_TOKEN}",
        "checklistPopulationOnly=true",
        "publicSafeChecklistRowsMaterialized=true",
        "checklistRowsMaterialized=9",
        "checklistFamilyCount=5",
        "privateFrameMessageObservationChecklistRows=3",
        "sourceSelectionBoundaryRows=1",
        "messageDisplayClassificationRows=3",
        "timingOrderClassificationRows=1",
        "publicSafeResultSummaryRows=1",
        "defaultStatus=not-run",
        "observationStatus=unobserved",
        "notRunRows=9",
        "unobservedRows=9",
        "observedRows=0",
        "rowStatusChangedCount=0",
        "blockedByMissingExplicitOperatorArm=true",
        "futureReviewRequiresExplicitOperatorArm=true",
        "privateFrameReviewArmed=false",
        "privateFrameReviewPerformed=false",
        "checklistObservationPerformed=false",
        "messageObservationPerformed=false",
        "runtimeMessageDisplayClaim=false",
        "runtimeMessageDisplayProven=false",
        "sourceSelectionObserved=false",
        "sourceSelectionProven=false",
        "missionScriptRuntimeEvidenceRows=0",
        "falseGuardCount=47",
        "zeroCounterCount=19",
        "publicLeakCheck=PASS",
        "latestGhidraBackupClass=verified-static-backup-redacted",
        "legacyStaticCounterRejected=6113/6113",
    )
    for path in (PLAN, READINESS):
        text = read_text(path)
        for token in core_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing token: {token}", failures)

    front_door_tokens = (
        THIS_SLICE,
        STATUS_TOKEN,
        "level100-message-private-frame-checklist-population.md",
        "level100-message-private-frame-checklist-population.v1.json",
        "checklistRowsMaterialized=9",
        "notRunRows=9",
        "observedRows=0",
        "blockedByMissingExplicitOperatorArm=true",
        "privateFrameReviewArmed=false",
        "runtimeMessageDisplayProven=false",
        "sourceSelectionProven=false",
        "publicLeakCheck=PASS",
    )
    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX):
        text = read_text(path)
        for token in front_door_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing checklist-population token: {token}", failures)

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
    require(f"Completed {PREVIOUS_SLICE}" in backlog, "backlog missing completed arm-boundary slice", failures)
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed checklist-population slice", failures)
    require(f"The selected active static-to-proof slice is {THIS_SLICE}. Status: selected" not in backlog, "backlog still marks checklist-population active", failures)


def check_package(failures: list[str]) -> None:
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:level100-message-private-frame-checklist-population")
        == r"py -3 tools\level100_message_private_frame_checklist_population_probe.py --check",
        "missing package Level100 private-frame checklist-population test script",
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
        print("Level100 private-frame checklist-population probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Level100 private-frame checklist-population probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
