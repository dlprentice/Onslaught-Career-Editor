#!/usr/bin/env python3
"""Validate the Level100 public-safe result-summary deferred proof."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "level100-message-public-safe-result-summary.md"
RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "level100-message-public-safe-result-summary.v1.json"
LORE_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "level100-message-public-safe-result-summary.md"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "level100-message-public-safe-result-summary.v1.json"
READINESS = ROOT / "release" / "readiness" / "level100_message_public_safe_result_summary_2026-06-09.md"
BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
LORE_MAPPED = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
LORE_BIN_INDEX = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
LORE_RE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"
PACKAGE_JSON = ROOT / "package.json"

POPULATION_RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "level100-message-private-frame-checklist-population.v1.json"
ARM_RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "level100-message-private-frame-arm-boundary.v1.json"

THIS_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Runtime Message Display Observation Public-Safe Result Summary Proof Plan"
PREVIOUS_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Runtime Message Display Observation Checklist Private-Frame Review Checklist Population Proof Plan"
NEXT_SLICE = "Static-To-Proof Rebuild Transition Next Safe Slice Selection Proof Plan"
COMPLETED_CROSSWALK_SLICE = "World / Thing / Spawn Static-To-Rebuild Contract Crosswalk Proof Plan"
COMPLETED_ROLLUP_SLICE = "MissionScript Command-Effect Rebuild Interface Rollup Proof Plan"
ACTIVE_SLICE = "MissionScript Command-Effect Rebuild Fixture Selection Proof Plan"

STATUS_TOKEN = "direct-level100-runtime-message-display-observation-public-safe-result-summary-complete-private-frame-review-deferred"
POPULATION_STATUS_TOKEN = "direct-level100-runtime-message-display-observation-checklist-private-frame-review-checklist-population-deferred-pending-explicit-operator-arm"
ARM_STATUS_TOKEN = "direct-level100-runtime-message-display-observation-checklist-private-frame-review-arm-boundary-defined-no-private-frame-review-performed"

FALSE_GUARDS = (
    "operatorArmRecorded",
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
    "publicResultTreatsSummaryAsRuntimeProof",
    "ghidraMutation",
    "templateMutation",
    "rowStatusMutationPerformed",
)

ZERO_COUNTS = (
    "missionScriptRuntimeEvidenceRows",
    "runtimeObservationRows",
    "publicAbsolutePathLeakCount",
    "publicSha256ValueLeakCount",
    "publicWindowIdentifierLeakCount",
    "publicProcessIdentifierLeakCount",
    "privatePathLeakCount",
    "rawArtifactLeakCount",
    "rawDialogueLeakCount",
    "beProcessesAfterSummary",
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
    population = read_json(POPULATION_RESULT)
    arm = read_json(ARM_RESULT)
    static = result["staticContext"]
    source = result["sourceChecklistPopulation"]
    summary = result["publicSafeSummary"]
    guard = result["guardSummary"]

    require(result["schemaVersion"] == "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-runtime-message-display-observation-public-safe-result-summary.v1", "schema version mismatch", failures)
    require(result["status"] == "PASS", "result status mismatch", failures)
    require(result["directLevel100RuntimeMessageDisplayObservationPublicSafeResultSummaryStatus"] == STATUS_TOKEN, "status token mismatch", failures)
    require(result["nextStaticSlice"] == NEXT_SLICE, "next static slice mismatch", failures)

    require(static["staticFunctionQuality"] == "6411/6411 = 100.00%", "static function quality mismatch", failures)
    require(static["staticDebt"] == "0 / 0 / 0", "static debt mismatch", failures)
    require(static["expandedStaticSurface"] == "1560/1560 = 100.00%", "expanded static surface mismatch", failures)
    require(static["currentRiskFocused"] == "1179/1179 = 100.00%", "current-risk focused mismatch", failures)
    require(static["remainingActiveFocusedWork"] == 0, "remaining active focused work mismatch", failures)
    require(static["staticAccountingSource"] == "static-reaudit-measurement-register.md", "static accounting source mismatch", failures)
    require(static["latestGhidraBackupClass"] == "verified-static-backup-redacted", "backup class mismatch", failures)
    require(static["legacyStaticCounterRejected"] == "6113/6113", "legacy static counter mismatch", failures)

    require(population["directLevel100RuntimeMessageDisplayObservationChecklistPrivateFrameReviewChecklistPopulationStatus"] == POPULATION_STATUS_TOKEN, "parent population token mismatch", failures)
    require(arm["directLevel100RuntimeMessageDisplayObservationChecklistPrivateFrameReviewArmBoundaryStatus"] == ARM_STATUS_TOKEN, "parent arm token mismatch", failures)
    require(source["sourceChecklistPopulationStatus"] == POPULATION_STATUS_TOKEN, "embedded population token mismatch", failures)
    require(source["sourceArmBoundaryStatus"] == ARM_STATUS_TOKEN, "embedded arm token mismatch", failures)
    require(source["sourceChecklistRowsMaterialized"] == 9, "source row count mismatch", failures)
    require(source["sourceChecklistFamilyCount"] == 5, "source family count mismatch", failures)
    require(source["sourceNotRunRows"] == 9, "source not-run count mismatch", failures)
    require(source["sourceUnobservedRows"] == 9, "source unobserved count mismatch", failures)
    require(source["sourceObservedRows"] == 0, "source observed count mismatch", failures)
    require(source["sourceRuntimeObservationRows"] == 0, "source runtime observations mismatch", failures)
    require(source["sourceRowStatusChangedCount"] == 0, "source row-status changed count mismatch", failures)
    require(source["sourceFalseGuardCount"] == 47, "source false guard count mismatch", failures)
    require(source["sourceZeroCounterCount"] == 19, "source zero counter count mismatch", failures)
    require(source["blockedByMissingExplicitOperatorArm"] is True, "source missing-arm blocker mismatch", failures)
    require(source["futureReviewRequiresExplicitOperatorArm"] is True, "source future arm guard mismatch", failures)
    require(source["publicLeakCheck"] == "PASS", "source public leak check mismatch", failures)

    require(summary["publicSummaryOnly"] is True, "summary-only flag mismatch", failures)
    require(summary["summaryRows"] == 1, "summary row count mismatch", failures)
    require(summary["privateFrameReviewDeferred"] is True, "summary deferred flag mismatch", failures)
    require(summary["blockedByMissingExplicitOperatorArm"] is True, "summary missing-arm blocker mismatch", failures)
    require(summary["futureReviewRequiresExplicitOperatorArm"] is True, "summary future arm guard mismatch", failures)
    require(summary["summaryFalseGuardCount"] == 45, "summary false guard count mismatch", failures)
    require(summary["summaryZeroCounterCount"] == 12, "summary zero counter count mismatch", failures)
    require(summary["summaryClass"] == "public-safe-class-count-status-token-summary", "summary class mismatch", failures)
    require("no runtime message-display behavior" in summary["summaryFinding"], "summary finding must preserve no-runtime-proof boundary", failures)

    for key in FALSE_GUARDS:
        require(guard[key] is False, f"guard must be false: {key}", failures)
    for key in ZERO_COUNTS:
        require(guard[key] == 0, f"guard count must be zero: {key}", failures)
    require(guard["publicSummaryOnly"] is True, "guard summary-only mismatch", failures)
    require(guard["privateFrameReviewDeferred"] is True, "guard deferred mismatch", failures)
    require(guard["blockedByMissingExplicitOperatorArm"] is True, "guard missing-arm blocker mismatch", failures)
    require(guard["futureReviewRequiresExplicitOperatorArm"] is True, "guard future arm mismatch", failures)
    require(guard["falseGuardCount"] == len(FALSE_GUARDS), "false guard count mismatch", failures)
    require(guard["zeroCounterCount"] == len(ZERO_COUNTS), "zero counter count mismatch", failures)
    require(guard["publicLeakCheck"] == "PASS", "guard public leak check mismatch", failures)

    proves = result["claimBoundary"]["proves"]
    unproven = result["claimBoundary"]["doesNotProve"]
    require("the Level100 message-display observation chain has a public-safe summary of its current deferred state" in proves, "claim boundary missing summary proof", failures)
    require("the chain has reached a real blocker because explicit private-frame review arming is absent" in proves, "claim boundary missing blocker proof", failures)
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

    require(no_bea_process_running(), "BEA process still running after public-safe summary validation", failures)
    for path in (PLAN, LORE_PLAN, RESULT, LORE_RESULT, READINESS):
        check_no_bad_public_content(path, failures)


def check_docs(failures: list[str]) -> None:
    core_tokens = (
        THIS_SLICE,
        PREVIOUS_SLICE,
        NEXT_SLICE,
        "level100-message-public-safe-result-summary.md",
        "level100-message-public-safe-result-summary.v1.json",
        f"directLevel100RuntimeMessageDisplayObservationPublicSafeResultSummaryStatus={STATUS_TOKEN}",
        f"directLevel100RuntimeMessageDisplayObservationChecklistPrivateFrameReviewChecklistPopulationStatus={POPULATION_STATUS_TOKEN}",
        "publicSummaryOnly=true",
        "summaryRows=1",
        "sourceChecklistRowsMaterialized=9",
        "sourceChecklistFamilyCount=5",
        "sourceNotRunRows=9",
        "sourceUnobservedRows=9",
        "sourceObservedRows=0",
        "sourceRuntimeObservationRows=0",
        "sourceRowStatusChangedCount=0",
        "sourceFalseGuardCount=47",
        "sourceZeroCounterCount=19",
        "privateFrameReviewDeferred=true",
        "blockedByMissingExplicitOperatorArm=true",
        "futureReviewRequiresExplicitOperatorArm=true",
        "runtimeMessageDisplayClaim=false",
        "runtimeMessageDisplayProven=false",
        "sourceSelectionObserved=false",
        "sourceSelectionProven=false",
        "missionScriptRuntimeEvidenceRows=0",
        "summaryFalseGuardCount=45",
        "summaryZeroCounterCount=12",
        "falseGuardCount=45",
        "zeroCounterCount=12",
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
        "level100-message-public-safe-result-summary.md",
        "level100-message-public-safe-result-summary.v1.json",
        "publicSummaryOnly=true",
        "summaryRows=1",
        "sourceChecklistRowsMaterialized=9",
        "sourceNotRunRows=9",
        "sourceUnobservedRows=9",
        "sourceObservedRows=0",
        "sourceRowStatusChangedCount=0",
        "privateFrameReviewDeferred=true",
        "blockedByMissingExplicitOperatorArm=true",
        "runtimeMessageDisplayProven=false",
        "sourceSelectionProven=false",
        "publicLeakCheck=PASS",
        NEXT_SLICE,
    )
    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX):
        text = read_text(path)
        for token in front_door_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing public-safe summary token: {token}", failures)

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
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed public-safe summary slice", failures)
    require(f"The selected active static-to-proof slice is {THIS_SLICE}. Status: selected" not in backlog, "backlog still marks public-safe summary active", failures)
    require(f"Completed {NEXT_SLICE}" in backlog, "backlog missing completed next-safe selection slice", failures)
    require(f"The selected active static-to-proof slice is {NEXT_SLICE}. Status: selected" not in backlog, "backlog still marks next-safe selection active", failures)
    require(f"Completed {COMPLETED_CROSSWALK_SLICE}" in backlog, "backlog missing completed World/Thing/Spawn crosswalk slice", failures)
    require(f"The selected active static-to-proof slice is {COMPLETED_CROSSWALK_SLICE}. Status: selected" not in backlog, "backlog still marks World/Thing/Spawn crosswalk active", failures)
    require(f"Completed {COMPLETED_ROLLUP_SLICE}" in backlog, "backlog missing completed MissionScript command-effect rollup slice", failures)
    require(f"The selected active static-to-proof slice is {COMPLETED_ROLLUP_SLICE}. Status: selected" not in backlog, "backlog still marks MissionScript command-effect rollup active", failures)
    require(f"The selected active static-to-proof slice is {ACTIVE_SLICE}. Status: selected" in backlog, "backlog missing active MissionScript fixture-selection slice", failures)


def check_package(failures: list[str]) -> None:
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:level100-message-public-safe-result-summary")
        == r"py -3 tools\level100_message_public_safe_result_summary_probe.py --check",
        "missing package Level100 public-safe result summary test script",
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
        print("Level100 public-safe result summary probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Level100 public-safe result summary probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
