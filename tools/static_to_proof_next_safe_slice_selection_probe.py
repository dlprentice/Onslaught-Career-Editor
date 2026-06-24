#!/usr/bin/env python3
"""Validate the static-to-proof next-safe-slice selection proof."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "static-to-proof-next-safe-slice-selection.md"
RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "static-to-proof-next-safe-slice-selection.v1.json"
LORE_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-to-proof-next-safe-slice-selection.md"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-to-proof-next-safe-slice-selection.v1.json"
READINESS = ROOT / "release" / "readiness" / "static_to_proof_next_safe_slice_selection_2026-06-09.md"

BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
LORE_MAPPED = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
LORE_BIN_INDEX = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
LORE_RE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"
PACKAGE_JSON = ROOT / "package.json"

SUMMARY = ROOT / "reverse-engineering" / "binary-analysis" / "level100-message-public-safe-result-summary.v1.json"
CORPUS = ROOT / "reverse-engineering" / "game-assets" / "world-thing-spawn-copied-corpus-schema.v1.json"
SPAWNER = ROOT / "reverse-engineering" / "binary-analysis" / "world-thing-spawn-spawner-handoff-static.v1.json"
GETTHINGREF = ROOT / "reverse-engineering" / "binary-analysis" / "world-thing-spawn-getthingref-object-reference-static.v1.json"

THIS_SLICE = "Static-To-Proof Rebuild Transition Next Safe Slice Selection Proof Plan"
PREVIOUS_SLICE = "MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Runtime Message Display Observation Public-Safe Result Summary Proof Plan"
NEXT_SLICE = "World / Thing / Spawn Static-To-Rebuild Contract Crosswalk Proof Plan"
COMPLETED_ROLLUP_SLICE = "MissionScript Command-Effect Rebuild Interface Rollup Proof Plan"
COMPLETED_FIXTURE_SELECTION_SLICE = "MissionScript Command-Effect Rebuild Fixture Selection Proof Plan"
COMPLETED_SLOT_FIXTURE_SLICE = "MissionScript Slot Bitset/Save Rebuild Fixture Proof Plan"
COMPLETED_DETERMINISTIC_SLICE = "MissionScript Slot Bitset/Save Deterministic Codec Proof Plan"
COMPLETED_CLEAN_ROOM_SLICE = "MissionScript Slot Bitset/Save Clean-Room Codec Interface Proof Plan"
ACTIVE_SLICE = "Static-To-Proof Rebuild Transition Next Safe Slice Selection Refresh Proof Plan"
REFRESH_SELECTED_CHILD = "MissionScript Vector/Range Command-Effect Deterministic Helper Fixture Proof Plan"
STATUS_TOKEN = "static-to-proof-next-safe-slice-selection-complete-world-thing-spawn-rebuild-contract-crosswalk-selected"
LEVEL100_STATUS = "direct-level100-runtime-message-display-observation-public-safe-result-summary-complete-private-frame-review-deferred"

FALSE_GUARDS = (
    "runtimeExecution",
    "beLaunch",
    "newLaunch",
    "screenshotCapture",
    "privateFrameReviewPerformed",
    "rowObservation",
    "exactTextOcrPerformed",
    "rawDialoguePublished",
    "visibleTextExcerptPublished",
    "sourceSelectionObserved",
    "nativeInput",
    "debuggerAttachment",
    "godotWork",
    "ghidraMutation",
    "executablePatching",
    "rebuildImplementation",
    "runtimeMessageDisplayProven",
    "rebuildParityProven",
    "noNoticeableDifferenceParityProven",
)

ZERO_COUNTS = (
    "missionScriptRuntimeEvidenceRows",
    "runtimeObservationRows",
    "privateFrameRowsObserved",
    "sourceRowStatusChangedCount",
    "publicAbsolutePathLeakCount",
    "publicSha256ValueLeakCount",
    "publicWindowIdentifierLeakCount",
    "publicProcessIdentifierLeakCount",
    "privatePathLeakCount",
    "rawArtifactLeakCount",
    "rawDialogueLeakCount",
    "beProcessesAfterSelection",
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
    (re.compile(r"(?i)level100-clean-materialized-[0-9]"), "copied-profile concrete identifier"),
    (re.compile(r"(?i)save-attempts"), "private save path"),
    (re.compile(r"(?i)onslaught_codex_directive"), "operator directive marker"),
    (re.compile(r"(?i)password|token="), "secret-like marker"),
)

FORBIDDEN_OVERCLAIMS = (
    "runtime object identity proven",
    "runtime spawnthing proven",
    "runtime getthingref proven",
    "runtime missionscript execution proven",
    "runtime world loading proven",
    "runtime spawner behavior proven",
    "runtime message display proven",
    "private-frame review complete",
    "source-selection observation complete",
    "visual qa complete",
    "executable patching behavior proven",
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
        require(phrase not in lower, f"{path.relative_to(ROOT)} overclaims forbidden category: {phrase}", failures)


def check_result(failures: list[str]) -> None:
    result = read_json(RESULT)
    summary = read_json(SUMMARY)
    corpus = read_json(CORPUS)
    spawner = read_json(SPAWNER)
    getthingref = read_json(GETTHINGREF)

    require(result["schemaVersion"] == "static-to-proof-next-safe-slice-selection.v1", "schema version mismatch", failures)
    require(result["status"] == "PASS", "status mismatch", failures)
    require(result["selectionStatus"] == STATUS_TOKEN, "selection status mismatch", failures)
    require(result["previousSlice"] == PREVIOUS_SLICE, "previous slice mismatch", failures)
    require(result["selectedChildLane"] == NEXT_SLICE, "selected child lane mismatch", failures)
    require(result["selectedChildScope"] == "world-thing-spawn-static-to-rebuild-contract-crosswalk", "selected child scope mismatch", failures)

    static = result["staticContext"]
    require(static["staticFunctionQuality"] == "6411/6411 = 100.00%", "static function quality mismatch", failures)
    require(static["staticDebt"] == "0 / 0 / 0", "static debt mismatch", failures)
    require(static["expandedStaticSurface"] == "1560/1560 = 100.00%", "expanded surface mismatch", failures)
    require(static["currentRiskFocused"] == "1179/1179 = 100.00%", "current-risk focused mismatch", failures)
    require(static["remainingActiveFocusedWork"] == 0, "remaining active focused work mismatch", failures)
    require(static["latestGhidraBackupClass"] == "verified-static-backup-redacted", "backup class mismatch", failures)

    parent = result["parentBlocker"]
    require(summary["directLevel100RuntimeMessageDisplayObservationPublicSafeResultSummaryStatus"] == LEVEL100_STATUS, "source summary status mismatch", failures)
    require(parent["sourceStatus"] == LEVEL100_STATUS, "embedded parent status mismatch", failures)
    require(parent["publicSummaryOnly"] is True, "parent summary-only mismatch", failures)
    require(parent["sourceChecklistRowsMaterialized"] == 9, "parent source row count mismatch", failures)
    require(parent["sourceNotRunRows"] == 9, "parent not-run count mismatch", failures)
    require(parent["sourceUnobservedRows"] == 9, "parent unobserved count mismatch", failures)
    require(parent["sourceObservedRows"] == 0, "parent observed count mismatch", failures)
    require(parent["sourceRuntimeObservationRows"] == 0, "parent runtime observation mismatch", failures)
    require(parent["sourceRowStatusChangedCount"] == 0, "parent row-status changed mismatch", failures)
    require(parent["privateFrameReviewDeferred"] is True, "parent private-frame deferred mismatch", failures)
    require(parent["blockedByMissingExplicitOperatorArm"] is True, "parent missing-arm blocker mismatch", failures)
    require(parent["futureReviewRequiresExplicitOperatorArm"] is True, "parent future-arm mismatch", failures)
    require(parent["runtimeMessageDisplayProven"] is False, "parent runtime-message guard mismatch", failures)
    require(parent["sourceSelectionProven"] is False, "parent source-selection guard mismatch", failures)

    accounting = result["selectionAccounting"]
    require(accounting["consultCount"] == 2, "consult count mismatch", failures)
    require(accounting["candidateCount"] == 4, "candidate count mismatch", failures)
    require(accounting["selectedCandidateRank"] == 1, "selected candidate rank mismatch", failures)
    require(accounting["selectedSourceProofCount"] == 3, "selected source proof count mismatch", failures)
    require(accounting["selectionFalseGuardCount"] == len(FALSE_GUARDS), "false guard count mismatch", failures)
    require(accounting["selectionZeroCounterCount"] == len(ZERO_COUNTS), "zero count mismatch", failures)
    require(accounting["publicLeakCheck"] == "PASS", "public leak check mismatch", failures)

    ranks = result["candidateRanking"]
    require(len(ranks) == 4, "candidate ranking length mismatch", failures)
    require(ranks[0]["rank"] == 1 and ranks[0]["decision"] == "selected", "selected rank mismatch", failures)
    require(ranks[0]["lane"] == NEXT_SLICE, "selected lane row mismatch", failures)

    selected = result["selectedSourceEvidence"]
    require(corpus["corpusCounts"]["rawDetailedCallRows"]["GetThingRef"] == 574, "source corpus GetThingRef mismatch", failures)
    require(corpus["corpusCounts"]["rawDetailedCallRows"]["SpawnThing"] == 70, "source corpus SpawnThing mismatch", failures)
    require(corpus["corpusCounts"]["rawDetailedCallRows"]["total"] == 644, "source corpus total mismatch", failures)
    require(corpus["selectedFamily"]["rawRows"] == 34, "source selected SpawnThing raw mismatch", failures)
    require(selected["copiedCorpusSchema"]["rawGetThingRefRows"] == 574, "embedded copied-corpus GetThingRef mismatch", failures)
    require(selected["copiedCorpusSchema"]["rawSpawnThingRows"] == 70, "embedded copied-corpus SpawnThing mismatch", failures)
    require(selected["copiedCorpusSchema"]["rawTotalRows"] == 644, "embedded copied-corpus total mismatch", failures)
    require(selected["copiedCorpusSchema"]["uniqueObjectReferenceRowsTotal"] == 436, "embedded copied-corpus unique total mismatch", failures)
    require(selected["copiedCorpusSchema"]["spawnPreservingRowsTotal"] == 447, "embedded copied-corpus spawn-preserving mismatch", failures)
    require(selected["copiedCorpusSchema"]["selectedSpawnRawRows"] == 34, "embedded selected SpawnThing raw mismatch", failures)

    require(len(spawner["handoffLayers"]) == 8, "source spawner layer count mismatch", failures)
    require(len(spawner["fieldRoleEvidence"]) == 12, "source spawner field-role count mismatch", failures)
    require(selected["spawnerHandoff"]["handoffLayerCount"] == 8, "embedded spawner layer count mismatch", failures)
    require(selected["spawnerHandoff"]["fieldRoleCount"] == 12, "embedded spawner field-role count mismatch", failures)

    require(getthingref["selectedFamily"]["rawRows"] == 9, "source GetThingRef selected raw mismatch", failures)
    require(getthingref["selectedFamily"]["uniqueObjectReferenceRows"] == 8, "source GetThingRef selected unique mismatch", failures)
    require(getthingref["selectedFamily"]["duplicateCallRows"] == 1, "source GetThingRef duplicate count mismatch", failures)
    require(getthingref["selectedFamily"]["emptySpawnerRows"] == 9, "source GetThingRef empty-spawner count mismatch", failures)
    require(len(getthingref["linkageLayers"]) == 4, "source GetThingRef linkage layer count mismatch", failures)
    require(selected["getThingRefObjectReference"]["selectedGetThingRefRawRows"] == 9, "embedded GetThingRef selected raw mismatch", failures)
    require(selected["getThingRefObjectReference"]["selectedGetThingRefUniqueObjectReferenceRows"] == 8, "embedded GetThingRef unique mismatch", failures)
    require(selected["getThingRefObjectReference"]["selectedDuplicateCallRows"] == 1, "embedded GetThingRef duplicate count mismatch", failures)
    require(selected["getThingRefObjectReference"]["selectedEmptySpawnerRows"] == 9, "embedded GetThingRef empty-spawner count mismatch", failures)
    require(selected["getThingRefObjectReference"]["linkageLayerCount"] == 4, "embedded GetThingRef linkage count mismatch", failures)

    guard = result["guardSummary"]
    for key in FALSE_GUARDS:
        require(guard[key] is False, f"guard must be false: {key}", failures)
    for key in ZERO_COUNTS:
        require(guard[key] == 0, f"guard count must be zero: {key}", failures)

    require(len(result["stopConditions"]) == 6, "stop condition count mismatch", failures)
    require("runtime object identity" in result["claimBoundary"]["doesNotProve"], "claim boundary missing runtime object identity", failures)
    require("the selected next child lane is a static, public-safe, implementation-facing World / Thing / Spawn crosswalk" in result["claimBoundary"]["proves"], "claim boundary missing selected child proof", failures)
    require(read_json(LORE_RESULT) == result, "lore schema mirror mismatch", failures)
    require(no_bea_process_running(), "BEA process still running after selection probe", failures)


def check_docs(failures: list[str]) -> None:
    require(read_text(LORE_PLAN) == read_text(PLAN), "lore proof mirror mismatch", failures)
    required_tokens = (
        THIS_SLICE,
        PREVIOUS_SLICE,
        NEXT_SLICE,
        "static-to-proof-next-safe-slice-selection.v1.json",
        f"selectionStatus={STATUS_TOKEN}",
        "selectedChildLane=World / Thing / Spawn Static-To-Rebuild Contract Crosswalk Proof Plan",
        "selectedChildScope=world-thing-spawn-static-to-rebuild-contract-crosswalk",
        "consultCount=2",
        "candidateCount=4",
        "selectedCandidateRank=1",
        "selectedSourceProofCount=3",
        "selectionFalseGuardCount=19",
        "selectionZeroCounterCount=12",
        "publicLeakCheck=PASS",
        "privateFrameReviewDeferred=true",
        "blockedByMissingExplicitOperatorArm=true",
        "futureReviewRequiresExplicitOperatorArm=true",
        "sourceObservedRows=0",
        "sourceRuntimeObservationRows=0",
        "sourceRowStatusChangedCount=0",
        "runtimeExecution=false",
        "beLaunch=false",
        "screenshotCapture=false",
        "privateFrameReviewPerformed=false",
        "sourceSelectionObserved=false",
        "nativeInput=false",
        "debuggerAttachment=false",
        "godotWork=false",
        "ghidraMutation=false",
        "rebuildImplementation=false",
        "rebuildParityProven=false",
        "noNoticeableDifferenceParityProven=false",
        "missionScriptRuntimeEvidenceRows=0",
        "runtimeObservationRows=0",
        "beProcessesAfterSelection=0",
        "574",
        "70",
        "644",
        "436",
        "447",
        "training-target-spawn-family",
        "training-target-zone-getthingref-family",
        "DAT_008553f4",
        "0x0050f970 CWorldPhysicsManager__CreateSpawner",
        "0x004e3c60 CSpawnerThng__DoSpawn",
        "CUnit__VFunc08_InitAndAddToWorld",
        "0x004fc3a0 CUnit__SetSpawnCooldownState3",
        "latestGhidraBackupClass=verified-static-backup-redacted",
    )
    for path in (PLAN, READINESS):
        text = read_text(path)
        for token in required_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing token: {token}", failures)
        check_no_bad_public_content(path, failures)

    front_door_tokens = (
        THIS_SLICE,
        NEXT_SLICE,
        "static-to-proof-next-safe-slice-selection.md",
        "static-to-proof-next-safe-slice-selection.v1.json",
        STATUS_TOKEN,
        "complete next safe slice selection",
        "consultCount=2",
        "candidateCount=4",
        "selectedCandidateRank=1",
        "selectedSourceProofCount=3",
        "selectionFalseGuardCount=19",
        "selectionZeroCounterCount=12",
        "publicLeakCheck=PASS",
        "privateFrameReviewDeferred=true",
        "blockedByMissingExplicitOperatorArm=true",
        "World / Thing / Spawn Copied-Corpus Schema Proof",
        "World / Thing / Spawn Spawner Handoff Static Proof",
        "World / Thing / Spawn GetThingRef Object-Reference Static Proof",
    )
    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX):
        text = read_text(path)
        for token in front_door_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing front-door token: {token}", failures)

    for source, mirror in (
        (BACKLOG, LORE_BACKLOG),
        (MAPPED, LORE_MAPPED),
        (BIN_INDEX, LORE_BIN_INDEX),
        (RE_INDEX, LORE_RE_INDEX),
    ):
        require(read_text(source) == read_text(mirror), f"lore mirror mismatch for {source.relative_to(ROOT)}", failures)

    backlog = read_text(BACKLOG)
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed next safe slice selection", failures)
    require(f"Completed {NEXT_SLICE}" in backlog, "backlog missing completed World/Thing/Spawn crosswalk slice", failures)
    require(f"Completed {COMPLETED_ROLLUP_SLICE}" in backlog, "backlog missing completed MissionScript command-effect rollup slice", failures)
    require(f"Completed {COMPLETED_FIXTURE_SELECTION_SLICE}" in backlog, "backlog missing completed MissionScript fixture-selection slice", failures)
    require(f"Completed {COMPLETED_SLOT_FIXTURE_SLICE}" in backlog, "backlog missing completed MissionScript slot fixture plan", failures)
    require(f"Completed {COMPLETED_DETERMINISTIC_SLICE}" in backlog, "backlog missing completed MissionScript deterministic codec slice", failures)
    require(f"Completed {COMPLETED_CLEAN_ROOM_SLICE.replace(' Proof Plan', ' Proof')}" in backlog, "backlog missing completed MissionScript clean-room codec interface slice", failures)
    require(f"The selected active static-to-proof slice is {THIS_SLICE}. Status: selected" not in backlog, "backlog still marks next-safe selection active", failures)
    require(f"The selected active static-to-proof slice is {NEXT_SLICE}. Status: selected" not in backlog, "backlog still marks World/Thing/Spawn crosswalk active", failures)
    require(f"The selected active static-to-proof slice is {COMPLETED_ROLLUP_SLICE}. Status: selected" not in backlog, "backlog still marks MissionScript command-effect rollup active", failures)
    require(f"The selected active static-to-proof slice is {COMPLETED_FIXTURE_SELECTION_SLICE}. Status: selected" not in backlog, "backlog still marks MissionScript fixture-selection active", failures)
    require(f"The selected active static-to-proof slice is {COMPLETED_SLOT_FIXTURE_SLICE}. Status: selected" not in backlog, "backlog still marks MissionScript slot fixture plan active", failures)
    require(f"The selected active static-to-proof slice is {COMPLETED_DETERMINISTIC_SLICE}. Status: selected" not in backlog, "backlog still marks MissionScript deterministic codec lane active", failures)
    require(f"The selected active static-to-proof slice is {COMPLETED_CLEAN_ROOM_SLICE}. Status: selected" not in backlog, "backlog still marks MissionScript clean-room codec interface lane active", failures)
    require("The selected active static-to-proof slice is Save / Options Byte-Preservation Runtime-Proof Readiness Gate Plan. Status: selected" not in backlog, "backlog still marks Save / Options runtime-proof readiness gate lane active", failures)
    require("The selected active static-to-proof slice is Save / Options Byte-Preservation AppCore Fixture Matrix Proof Plan. Status: selected" not in backlog, "backlog still marks Save / Options AppCore fixture-matrix lane active", failures)
    require(f"Completed {ACTIVE_SLICE}" in backlog, "backlog missing completed next-slice selection refresh lane", failures)
    require(f"The selected active static-to-proof slice is {ACTIVE_SLICE}. Status: selected" not in backlog, "backlog still marks next-slice selection refresh lane active", failures)
    require(f"The selected active static-to-proof slice is {REFRESH_SELECTED_CHILD}. Status: selected" in backlog, "backlog missing active vector/range helper fixture lane", failures)


def check_package(failures: list[str]) -> None:
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:static-to-proof-next-safe-slice-selection")
        == r"py -3 tools\static_to_proof_next_safe_slice_selection_probe.py --check",
        "missing package next-safe-slice selection test script",
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
        print("Static-to-proof next safe slice selection probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Static-to-proof next safe slice selection probe: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
