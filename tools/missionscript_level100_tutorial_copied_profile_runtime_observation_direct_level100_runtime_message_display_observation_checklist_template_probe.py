#!/usr/bin/env python3
"""Validate the MissionScript Level100 runtime message-display checklist template."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-runtime-message-display-observation-checklist-template-proof-plan.md"
LORE_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-runtime-message-display-observation-checklist-template-proof-plan.md"
RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-runtime-message-display-observation-checklist-template.v1.json"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-runtime-message-display-observation-checklist-template.v1.json"
BOUNDARY_RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-runtime-message-display-boundary.v1.json"
READINESS = ROOT / "release" / "readiness" / "missionscript_level100_tutorial_copied_profile_runtime_observation_direct_level100_runtime_message_display_observation_checklist_template_2026-06-09.md"
BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
LORE_MAPPED = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
LORE_BIN_INDEX = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
LORE_RE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"
PACKAGE_JSON = ROOT / "package.json"

THIS_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Runtime Message Display Observation Checklist Template Proof Plan"
PREVIOUS_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Runtime Message Display Boundary Proof Plan"
NEXT_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Runtime Message Display Observation Checklist Dry-Run Validation Proof Plan"
ACTIVE_AFTER_NEXT_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Runtime Message Display Observation Checklist Private-Frame Review Arm Boundary Proof Plan"
PLAN_LINK = "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-runtime-message-display-observation-checklist-template-proof-plan.md"
RESULT_LINK = "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-runtime-message-display-observation-checklist-template.v1.json"
BOUNDARY_LINK = "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-runtime-message-display-boundary-proof-plan.md"
BOUNDARY_RESULT_LINK = "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-runtime-message-display-boundary.v1.json"
STATUS_TOKEN = "direct-level100-runtime-message-display-observation-checklist-template-defined-no-runtime-message-proof"
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

FALSE_GUARDS = (
    "runtimeExecution",
    "profileIdPublished",
    "privateProofAssetPublished",
    "privateCaptureLocatorIncluded",
    "privateArtifactHashIncluded",
    "privateArtifactBytesIncluded",
    "privateWindowIdentifiersIncluded",
    "publicMachinePathIncluded",
    "newLaunch",
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


def check_no_bad_tokens(path: Path, failures: list[str]) -> None:
    text = read_text(path)
    lower = text.lower()
    for token in FORBIDDEN_PUBLIC_TOKENS:
        require(token not in lower, f"{path.relative_to(ROOT)} leaks public-forbidden token: {token}", failures)
    for phrase in FORBIDDEN_OVERCLAIMS:
        require(phrase not in lower, f"{path.relative_to(ROOT)} overclaims: {phrase}", failures)
    require(re.search(r"\b[a-fA-F0-9]{64}\b", text) is None, f"{path.relative_to(ROOT)} leaks a raw SHA-256-like value", failures)
    require(re.search(r"\b[A-Za-z]:[\\/]", text) is None, f"{path.relative_to(ROOT)} leaks a machine-local absolute path", failures)


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


def require_not_run_statuses(value: Any, failures: list[str], path: str = "root") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in {"status", "defaultStatus", "panelClassStatus", "glyphClassStatus", "speakerPortraitClassStatus", "orderClassificationStatus"}:
                require(child == "not-run", f"status field must be not-run at {path}.{key}", failures)
            if key == "observationStatus":
                require(child == "unobserved", f"observationStatus must be unobserved at {path}", failures)
            require_not_run_statuses(child, failures, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            require_not_run_statuses(child, failures, f"{path}[{index}]")


def check_result(failures: list[str]) -> None:
    result = read_json(RESULT)
    boundary = read_json(BOUNDARY_RESULT)
    parent = result["parentBoundary"]
    source = result["templateSource"]
    bundle = result["templateBundle"]
    guard = result["guardSummary"]

    require(result["schemaVersion"] == "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-runtime-message-display-observation-checklist-template.v1", "schema version mismatch", failures)
    require(result["status"] == "PASS", "status mismatch", failures)
    require(result["directLevel100RuntimeMessageDisplayObservationChecklistTemplateStatus"] == STATUS_TOKEN, "status token mismatch", failures)
    require(result["staticContext"]["staticFunctionQuality"] == "6411/6411 = 100.00%", "static function quality mismatch", failures)
    require(result["staticContext"]["staticDebt"] == "0 / 0 / 0", "static debt mismatch", failures)
    require(result["staticContext"]["expandedStaticSurface"] == "1560/1560 = 100.00%", "expanded static surface mismatch", failures)
    require(result["staticContext"]["currentRiskFocused"] == "1179/1179 = 100.00%", "current risk mismatch", failures)
    require(result["staticContext"]["remainingActiveFocusedWork"] == 0, "remaining focused work mismatch", failures)
    require(result["staticContext"]["staticAccountingSource"] == "static-reaudit-measurement-register.md", "static accounting source mismatch", failures)
    require(result["staticContext"]["latestGhidraBackupClass"] == "verified-static-backup-redacted", "backup class mismatch", failures)
    require(result["staticContext"]["legacyStaticCounterRejected"] == "6113/6113", "legacy static counter mismatch", failures)

    boundary_proof = boundary["messageDisplayBoundaryProof"]
    require(boundary["status"] == "PASS", "parent boundary status mismatch", failures)
    require(boundary["directLevel100RuntimeMessageDisplayBoundaryStatus"] == BOUNDARY_STATUS_TOKEN, "parent boundary token mismatch", failures)
    require(parent["directLevel100RuntimeMessageDisplayBoundaryStatus"] == BOUNDARY_STATUS_TOKEN, "embedded parent boundary token mismatch", failures)
    for key in (
        "profileIdClass",
        "profileIdPublished",
        "sourceProgressionCorrelationStatus",
        "sourceTimedFrameSetCaptureStatus",
        "sourceTextOverlayCorrelationStatus",
        "sourceStaticTextSpeakerStatus",
        "sourceStaticWalkthroughStatus",
        "selectedRoute",
        "launchArguments",
        "boundaryMethod",
        "messageDisplayBoundaryRows",
        "messageDisplayCandidateFrameRows",
        "textOverlayProgressionRows",
        "progressionCorrelationRows",
        "publicFrameClassBuckets",
        "timedFrameSetTextOverlayProgressionClass",
        "bottomTutorialTextPanelVisibleFrameRows",
        "tutorialTextGlyphsVisibleFrameRows",
        "speakerPortraitVisibleFrameRows",
        "textOverlayChangedAcrossFrameSetClass",
        "tokenUniverseClass",
        "relevantStaticTokensResolved",
        "relevantStaticTokenCount",
        "missingReferenceTokens",
        "messageRows",
        "messageUnique",
        "helpRows",
        "helpUnique",
        "objectiveRows",
        "objectiveUnique",
        "lossRows",
        "lossUnique",
        "speakerRows",
        "speakerUnique",
        "speakerTokens",
        "speakerCounts",
        "requiredFutureProofArtifactCount",
        "requiredFutureProofArtifacts",
        "publicAllowedOutputs",
        "publicLeakCheck",
    ):
        require(parent[key] == boundary_proof[key], f"embedded parent mismatch: {key}", failures)

    require(parent["messageDisplayBoundaryRows"] == 3, "parent boundary row count mismatch", failures)
    require(parent["messageDisplayCandidateFrameRows"] == 3, "parent candidate frame count mismatch", failures)
    require(parent["progressionCorrelationRows"] == 4, "parent progression row count mismatch", failures)
    require(parent["requiredFutureProofArtifactCount"] == 5, "parent required artifact count mismatch", failures)
    require(parent["requiredFutureProofArtifacts"] == list(ARTIFACT_KEYS), "parent artifact list mismatch", failures)
    require(parent["publicAllowedOutputs"] == ["class-counts", "status-tokens", "claim-boundary", "no-raw-dialogue", "no-private-paths", "no-frame-hashes"], "parent public output mismatch", failures)

    require(source["templateOnly"] is True, "templateOnly must be true", failures)
    require(guard["templateOnly"] is True, "guard templateOnly must be true", failures)
    for key in FALSE_GUARDS:
        require(source[key] is False, f"source guard must be false: {key}", failures)
        require(guard[key] is False, f"guard must be false: {key}", failures)
    for key in ZERO_COUNTS:
        require(source[key] == 0, f"source count must be zero: {key}", failures)
        require(guard[key] == 0, f"guard count must be zero: {key}", failures)
    require(source["defaultStatus"] == "not-run", "default status mismatch", failures)
    require(source["observationStatus"] == "unobserved", "observation status mismatch", failures)
    require(source["redactionPolicy"] == "public-safe-placeholder-only", "redaction policy mismatch", failures)
    require(source["publicLeakCheck"] == "PASS", "source leak check mismatch", failures)
    require(guard["publicLeakCheck"] == "PASS", "guard leak check mismatch", failures)

    require(bundle["templateClassCount"] == 5, "template class count mismatch", failures)
    require(bundle["privateFrameMessageObservationChecklistRows"] == 3, "private frame checklist row count mismatch", failures)
    require(bundle["sourceSelectionBoundaryRows"] == 1, "source-selection row count mismatch", failures)
    require(bundle["messageDisplayClassificationRows"] == 3, "message classification row count mismatch", failures)
    require(bundle["timingOrderClassificationRows"] == 1, "timing-order row count mismatch", failures)
    require(bundle["publicSafeResultSummaryRows"] == 1, "public summary row count mismatch", failures)
    require(guard["templateClassCount"] == 5, "guard template class count mismatch", failures)
    require(guard["privateFrameMessageObservationChecklistRows"] == 3, "guard private frame checklist count mismatch", failures)
    require(bundle["allowedRowStatuses"] == ["not-run", "observed", "inconclusive", "blocked", "out-of-scope"], "allowed row statuses mismatch", failures)

    templates = bundle["templates"]
    require([row["templateClass"] for row in templates] == list(TEMPLATE_CLASSES), "template class order mismatch", failures)
    require([row["artifactKey"] for row in templates] == list(ARTIFACT_KEYS), "artifact key order mismatch", failures)
    for row in templates:
        require(row["templateOnly"] is True, f"templateOnly mismatch: {row['templateClass']}", failures)
        require(row["runtimeExecution"] is False, f"runtimeExecution mismatch: {row['templateClass']}", failures)
        require(row["containsPrivatePath"] is False, f"containsPrivatePath mismatch: {row['templateClass']}", failures)
        require(row["containsRawArtifact"] is False, f"containsRawArtifact mismatch: {row['templateClass']}", failures)
        require(row["defaultStatus"] == "not-run", f"default status mismatch: {row['templateClass']}", failures)
        require(row["observationStatus"] == "unobserved", f"observation status mismatch: {row['templateClass']}", failures)
        require(row["redactionPolicy"] == "public-safe-placeholder-only", f"redaction policy mismatch: {row['templateClass']}", failures)
        require_not_run_statuses(row, failures, row["templateClass"])

    private_rows = templates[0]["rows"]
    require(len(private_rows) == 3, "private frame template row count mismatch", failures)
    for row in private_rows:
        require(row["frameClassExpected"] == "cockpit-hud-tutorial-overlay", f"private frame class mismatch: {row['rowId']}", failures)
        require(row["rawDialogueIncluded"] is False, f"private frame raw dialogue guard mismatch: {row['rowId']}", failures)
        require(row["visibleTextExcerptPublished"] is False, f"private frame visible excerpt guard mismatch: {row['rowId']}", failures)
        require(row["exactTextOcrPerformed"] is False, f"private frame OCR guard mismatch: {row['rowId']}", failures)

    source_selection = templates[1]["fields"]
    require(source_selection["sourceSelectionObserved"] is False, "source-selection observed guard mismatch", failures)
    require(source_selection["missionScriptRuntimeEvidenceRows"] == 0, "source-selection runtime evidence count mismatch", failures)
    for token in ("0x00539dc0", "0x00539ca0", "this+0x20", "this+0x124", "CDXMemBuffer__InitFromFile"):
        require(token in source_selection["staticAnchors"], f"missing source-selection static anchor: {token}", failures)

    message = templates[2]["fields"]
    require(message["messageDisplayClassificationRows"] == 3, "message classification count mismatch", failures)
    require(message["runtimeMessageDisplayClaim"] is False, "message display claim guard mismatch", failures)
    require(message["runtimeMessageDisplayProven"] is False, "message display proven guard mismatch", failures)
    require(message["relevantStaticTokensResolved"] == "68/68", "message token resolution mismatch", failures)
    require(message["missingReferenceTokens"] == 0, "missing token count mismatch", failures)
    require(message["speakerTokens"] == ["P_TATIANA", "P_KRAMER", "P_TECHNICIAN"], "speaker tokens mismatch", failures)

    timing = templates[3]["fields"]
    require(timing["progressionCorrelationRows"] == 4, "timing progression count mismatch", failures)
    require(timing["messageDisplayCandidateFrameRows"] == 3, "timing candidate frame count mismatch", failures)
    require(timing["timingCorrectnessClaim"] is False, "timing claim guard mismatch", failures)
    require(timing["timingCorrectnessProven"] is False, "timing proven guard mismatch", failures)

    summary = templates[4]["fields"]
    require(summary["publicAllowedOutputs"] == source["publicAllowedOutputs"], "public summary allowed output mismatch", failures)
    require(summary["publicLeakCheck"] == "PASS", "public summary leak check mismatch", failures)
    require("runtime message display behavior" in summary["unprovenList"], "public summary missing runtime message display unproven boundary", failures)

    require(result["nextStaticSlice"] == NEXT_SLICE, "next static slice mismatch", failures)
    require(no_bea_process_running(), "BEA process still running after checklist-template proof", failures)
    check_no_bad_tokens(RESULT, failures)
    check_no_bad_tokens(LORE_RESULT, failures)


def check_docs(failures: list[str]) -> None:
    core_tokens = (
        THIS_SLICE,
        PREVIOUS_SLICE,
        NEXT_SLICE,
        PLAN_LINK,
        RESULT_LINK,
        BOUNDARY_LINK,
        BOUNDARY_RESULT_LINK,
        f"directLevel100RuntimeMessageDisplayObservationChecklistTemplateStatus={STATUS_TOKEN}",
        f"directLevel100RuntimeMessageDisplayBoundaryStatus={BOUNDARY_STATUS_TOKEN}",
        "templateOnly=true",
        "runtimeExecution=false",
        "profileIdPublished=false",
        "privateProofAssetPublished=false",
        "privateCaptureLocatorIncluded=false",
        "privateArtifactHashIncluded=false",
        "privateArtifactBytesIncluded=false",
        "privateWindowIdentifiersIncluded=false",
        "publicMachinePathIncluded=false",
        "newLaunch=false",
        "newScreenshotCapture=false",
        "newPrivateFrameReview=false",
        "messageObservationPerformed=false",
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
        "defaultStatus=not-run",
        "observationStatus=unobserved",
        "redactionPolicy=public-safe-placeholder-only",
        "templateClassCount=5",
        "privateFrameMessageObservationChecklistRows=3",
        "sourceSelectionBoundaryRows=1",
        "messageDisplayClassificationRows=3",
        "timingOrderClassificationRows=1",
        "publicSafeResultSummaryRows=1",
        "messageDisplayBoundaryRows=3",
        "messageDisplayCandidateFrameRows=3",
        "progressionCorrelationRows=4",
        "publicFrameClassBuckets=exterior-world-no-tutorial-panel:1/cockpit-hud-tutorial-overlay:3",
        "timedFrameSetTextOverlayProgressionClass=exterior-world-to-cockpit-hud-tutorial-overlay-change-class",
        "relevantStaticTokensResolved=68/68",
        "missingReferenceTokens=0",
        "requiredFutureProofArtifactCount=5",
        "requiredFutureProofArtifacts=private-frame-message-observation-checklist/source-selection-boundary-row/message-display-classification-row/timing-order-classification-row/public-safe-result-summary",
        "publicAllowedOutputs=class-counts/status-tokens/claim-boundary/no-raw-dialogue/no-private-paths/no-frame-hashes",
        "publicAbsolutePathLeakCount=0",
        "publicSha256ValueLeakCount=0",
        "publicWindowIdentifierLeakCount=0",
        "publicProcessIdentifierLeakCount=0",
        "privatePathLeakCount=0",
        "rawArtifactLeakCount=0",
        "rawDialogueLeakCount=0",
        "publicLeakCheck=PASS",
        "staticAccountingSource=static-reaudit-measurement-register.md",
        "latestGhidraBackupClass=verified-static-backup-redacted",
        "legacyStaticCounterRejected=6113/6113",
        "private_frame_message_observation_checklist.v1",
        "source_selection_boundary_row.v1",
        "message_display_classification_row.v1",
        "timing_order_classification_row.v1",
        "public_safe_result_summary.v1",
    )
    for path in (PLAN, READINESS):
        text = read_text(path)
        for token in core_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing token: {token}", failures)
        check_no_bad_tokens(path, failures)

    front_door_tokens = (
        PLAN_LINK,
        RESULT_LINK,
        THIS_SLICE,
        PREVIOUS_SLICE,
        NEXT_SLICE,
        ACTIVE_AFTER_NEXT_SLICE,
        STATUS_TOKEN,
        BOUNDARY_STATUS_TOKEN,
        "templateClassCount=5",
        "privateFrameMessageObservationChecklistRows=3",
        "messageDisplayClassificationRows=3",
        "defaultStatus=not-run",
        "observationStatus=unobserved",
        "runtimeMessageDisplayClaim=false",
        "runtimeMessageDisplayProven=false",
        "sourceSelectionObserved=false",
        "missionScriptRuntimeEvidenceRows=0",
        "publicLeakCheck=PASS",
    )
    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX):
        text = read_text(path)
        for token in front_door_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing checklist-template token: {token}", failures)

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
    require(f"Completed {PREVIOUS_SLICE}" in backlog, "backlog missing completed boundary slice", failures)
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed checklist-template slice", failures)
    require(f"Completed {NEXT_SLICE}" in backlog, "backlog missing completed checklist dry-run slice", failures)
    require(
        f"The selected active static-to-proof slice is {ACTIVE_AFTER_NEXT_SLICE}" in backlog
        or f"Completed {ACTIVE_AFTER_NEXT_SLICE}" in backlog,
        "backlog missing active/completed private-frame arm-boundary slice",
        failures,
    )
    require(f"The selected active static-to-proof slice is {THIS_SLICE}. Status: selected" not in backlog, "backlog still marks checklist-template slice active", failures)
    require(f"The selected active static-to-proof slice is {PREVIOUS_SLICE}. Status: selected" not in backlog, "backlog still marks boundary slice active", failures)
    require(f"The selected active static-to-proof slice is {NEXT_SLICE}. Status: selected" not in backlog, "backlog still marks checklist dry-run slice active", failures)


def check_package(failures: list[str]) -> None:
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-runtime-message-display-observation-checklist-template")
        == r"py -3 tools\missionscript_level100_tutorial_copied_profile_runtime_observation_direct_level100_runtime_message_display_observation_checklist_template_probe.py --check",
        "missing package direct Level100 runtime message display checklist-template test script",
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
        print("MissionScript Level100 runtime message display checklist-template probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("MissionScript Level100 runtime message display checklist-template probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
