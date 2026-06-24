#!/usr/bin/env python3
"""Validate the MissionScript command-effect rebuild-interface rollup."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-command-effect-rebuild-interface-rollup.md"
RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-command-effect-rebuild-interface-rollup.v1.json"
LORE_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-command-effect-rebuild-interface-rollup.md"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-command-effect-rebuild-interface-rollup.v1.json"
READINESS = ROOT / "release" / "readiness" / "missionscript_command_effect_rebuild_interface_rollup_2026-06-09.md"

BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
LORE_MAPPED = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
LORE_BIN_INDEX = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
LORE_RE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"
PACKAGE_JSON = ROOT / "package.json"

DESCRIPTOR_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-command-descriptor-schema.v1.json"
DESCRIPTOR_PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-command-descriptor-schema-proof.md"

THIS_SLICE = "MissionScript Command-Effect Rebuild Interface Rollup Proof Plan"
PREVIOUS_SLICE = "World / Thing / Spawn Static-To-Rebuild Contract Crosswalk Proof Plan"
NEXT_SLICE = "MissionScript Command-Effect Rebuild Fixture Selection Proof Plan"
COMPLETED_SLOT_FIXTURE_SLICE = "MissionScript Slot Bitset/Save Rebuild Fixture Proof Plan"
COMPLETED_DETERMINISTIC_SLICE = "MissionScript Slot Bitset/Save Deterministic Codec Proof Plan"
COMPLETED_CLEAN_ROOM_SLICE = "MissionScript Slot Bitset/Save Clean-Room Codec Interface Proof Plan"
ACTIVE_SLICE = "Save / Options Byte-Preservation AppCore Implementation Contract Proof Plan"
COMPLETION_ROLLUP_SLICE = "MissionScript Command-Effect Fixture Family Completion Rollup Proof Plan"
POST_ROLLUP_NEXT_SLICE = "Static-To-Proof Rebuild Transition Post-Command-Effect Fixture Next Safe Slice Selection Refresh Proof Plan"
STATUS_TOKEN = "missionscript-command-effect-rebuild-interface-rollup-complete-static-interface-contract-not-runtime-proof"

SOURCE_SCHEMAS = (
    {
        "familyId": "slot",
        "schema": ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-slot-command-effect.v1.json",
        "proof": ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-slot-command-effect-static-proof.md",
        "script": "test:missionscript-slot-command-effect-static",
        "entries": 3,
        "indices": (122, 123, 132),
        "waves": 3,
        "claims": 3,
        "notClaimed": 20,
    },
    {
        "familyId": "objective-outcome",
        "schema": ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-objective-outcome-command-effect.v1.json",
        "proof": ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-objective-outcome-command-effect-static-proof.md",
        "script": "test:missionscript-objective-outcome-command-effect-static",
        "entries": 7,
        "indices": (7, 8, 82, 83, 86, 87, 105),
        "waves": 4,
        "claims": 3,
        "notClaimed": 19,
    },
    {
        "familyId": "message-audio",
        "schema": ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-message-audio-command-effect.v1.json",
        "proof": ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-message-audio-command-effect-static-proof.md",
        "script": "test:missionscript-message-audio-command-effect-static",
        "entries": 12,
        "indices": (9, 15, 16, 27, 33, 34, 35, 89, 90, 111, 112, 117),
        "waves": 4,
        "claims": 5,
        "notClaimed": 19,
    },
    {
        "familyId": "goodie-state",
        "schema": ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-goodie-state-command-effect.v1.json",
        "proof": ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-goodie-state-command-effect-static-proof.md",
        "script": "test:missionscript-goodie-state-command-effect-static",
        "entries": 3,
        "indices": (84, 118, 119),
        "waves": 3,
        "claims": 5,
        "notClaimed": 17,
    },
    {
        "familyId": "cutscene-pan-camera-position",
        "schema": ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-cutscene-pan-camera-position-command-effect.v1.json",
        "proof": ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-cutscene-pan-camera-position-command-effect-static-proof.md",
        "script": "test:missionscript-cutscene-pan-camera-position-command-effect-static",
        "entries": 4,
        "indices": (65, 113, 114, 115),
        "waves": 3,
        "claims": 5,
        "notClaimed": 20,
    },
    {
        "familyId": "vector-range",
        "schema": ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-vector-range-command-effect.v1.json",
        "proof": ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-vector-range-command-effect-static-proof.md",
        "script": "test:missionscript-vector-range-command-effect-static",
        "entries": 9,
        "indices": (56, 57, 58, 59, 60, 61, 104, 105, 108),
        "waves": 3,
        "claims": 0,
        "notClaimed": 11,
    },
    {
        "familyId": "thing-value-engine-helper",
        "schema": ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-thing-value-engine-helper-command-effect.v1.json",
        "proof": ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-thing-value-engine-helper-command-effect-static-proof.md",
        "script": "test:missionscript-thing-value-engine-helper-command-effect-static",
        "entries": 6,
        "indices": (41, 98, 99, 138, 140, 141),
        "waves": 3,
        "claims": 0,
        "notClaimed": 19,
    },
    {
        "familyId": "hud-display",
        "schema": ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-hud-display-command-effect.v1.json",
        "proof": ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-hud-display-command-effect-static-proof.md",
        "script": "test:missionscript-hud-display-command-effect-static",
        "entries": 5,
        "indices": (33, 34, 75, 76, 77),
        "waves": 6,
        "claims": 4,
        "notClaimed": 19,
    },
    {
        "familyId": "player-state-score",
        "schema": ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-player-state-score-command-effect.v1.json",
        "proof": ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-player-state-score-command-effect-static-proof.md",
        "script": "test:missionscript-player-state-score-command-effect-static",
        "entries": 3,
        "indices": (84, 136, 137),
        "waves": 5,
        "claims": 4,
        "notClaimed": 21,
    },
)

TRUE_GUARDS = (
    "rollupOnly",
    "staticPublicSafeOnly",
    "sourceSchemaValidationOnly",
    "mirrorValidationOnly",
    "frontDoorDocValidationOnly",
    "rebuildInterfaceVocabularyOnly",
    "existingTrackedArtifactsOnly",
)

FALSE_GUARDS = (
    "programFilesInputUsed",
    "liveLooseMslLoading",
    "packedResourceScriptSelectionProven",
    "runtimeExecution",
    "runtimeMissionScriptExecutionProven",
    "runtimeCommandEffectsProven",
    "runtimeLevel100CommandEffectsProven",
    "runtimeEventOutcomesProven",
    "runtimeHudBehaviorProven",
    "runtimeMessageDisplayProven",
    "runtimeMessageAudioBehaviorProven",
    "runtimeVoicePlaybackProven",
    "runtimeAudioPlaybackProven",
    "runtimeQueueOrderingProven",
    "runtimeObjectiveOutcomeBehaviorProven",
    "runtimeGoodieStateMutationProven",
    "runtimeSaveBehaviorProven",
    "runtimeSlotPersistenceProven",
    "runtimeScoreBehaviorProven",
    "runtimeCockpitBehaviorProven",
    "runtimeStealthBehaviorProven",
    "runtimeVectorRangeBehaviorProven",
    "runtimeThingValueEngineHelperBehaviorProven",
    "runtimeCameraSwitchingProven",
    "runtimeCutscenePlaybackProven",
    "runtimeObjectIdentityProven",
    "runtimeSpawnThingBehaviorProven",
    "runtimeGetThingRefBehaviorProven",
    "runtimeWorldLoadingProven",
    "runtimeSpawnerBehaviorProven",
    "beLaunch",
    "newLaunch",
    "screenshotCapture",
    "newCapture",
    "privateFrameReviewPerformed",
    "rowObservation",
    "exactTextOcrPerformed",
    "rawDialoguePublished",
    "visibleTextExcerptPublished",
    "exactVisibleTokenIdentityClaim",
    "exactVisibleTokenIdentityProven",
    "sourceSelectionObserved",
    "sourceSelectionProven",
    "nativeInput",
    "debuggerAttachment",
    "godotWork",
    "ghidraMutation",
    "executablePatching",
    "rebuildImplementation",
    "rebuildParityProven",
    "noNoticeableDifferenceParityProven",
    "exactCommandDescriptorLayoutProven",
    "exactCommandArityProven",
    "exactArgumentTypeSchemaProven",
    "exactDatatypeLayoutProven",
    "exactHandlerAddressProven",
    "exactSourceBodyIdentityProven",
    "addScoreHandlerBodyProven",
    "toggleCockpitHandlerBodyProven",
    "setStealthHandlerBodyProven",
)

ZERO_COUNTERS = (
    "runtimeObservationRows",
    "missionScriptRuntimeEvidenceRows",
    "runtimeCommandEffectRows",
    "runtimeEventOutcomeRows",
    "runtimeHudMessageAudioRows",
    "privateFrameRowsObserved",
    "rowObservationRows",
    "sourceObservedRows",
    "sourceRuntimeObservationRows",
    "sourceRowStatusChangedCount",
    "newLaunchRows",
    "captureRows",
    "ocrRows",
    "rawDialogueRows",
    "ghidraMutationRows",
    "executablePatchRows",
    "rebuildImplementationRows",
    "beProcessesAfterRollup",
    "publicAbsolutePathLeakCount",
    "publicSha256ValueLeakCount",
    "publicWindowIdentifierLeakCount",
    "publicProcessIdentifierLeakCount",
    "privatePathLeakCount",
    "rawArtifactLeakCount",
    "rawDialogueLeakCount",
)

EXPECTED_DUPLICATE_INDICES = {
    33: "HighlightHudPart",
    34: "UnHighlightHudPart",
    84: "AddScore",
    105: "LevelLostString",
}

FORBIDDEN_PUBLIC_PATTERNS = (
    (re.compile(r"\b[A-Za-z]:[\\/]"), "machine-local absolute path"),
    (re.compile(r"\b[a-fA-F0-9]{64}\b"), "raw digest-like value"),
    (re.compile(r"(?i)c:[\\/]users"), "user profile path"),
    (re.compile(r"(?i)g:[\\/]"), "private backup path"),
    (re.compile(r"(?i)program files"), "installed game path"),
    (re.compile(r"(?i)steamapps"), "installed game path"),
    (re.compile(r"(?i)subagents[\\/]"), "subagent artifact path"),
    (re.compile(r"(?i)save-attempts"), "private save path"),
    (re.compile(r"(?i)onslaught_codex_directive"), "operator directive marker"),
    (re.compile(r"(?i)password|token="), "secret-like marker"),
    (re.compile(r"(?i)hwnd"), "window identifier"),
    (re.compile(r"(?i)capturepath|framepath|capturehash|framehash|framesha256|framebytelength"), "private frame locator/hash field"),
    (re.compile(r"(?i)\.private\.png"), "private frame filename"),
    (re.compile(r"(?i)level100-clean-materialized-[0-9]"), "copied-profile concrete identifier"),
)

FORBIDDEN_OVERCLAIMS = (
    "runtime missionscript execution proven",
    "runtime command effects proven",
    "runtime level100 command effects proven",
    "runtime message display proven",
    "runtime hud behavior proven",
    "runtime voice playback proven",
    "runtime audio playback proven",
    "runtime queue ordering proven",
    "runtime objective behavior proven",
    "runtime level outcome proven",
    "runtime goodie state proven",
    "runtime save behavior proven",
    "runtime slot persistence proven",
    "runtime score behavior proven",
    "runtime cockpit behavior proven",
    "runtime stealth behavior proven",
    "weapon-fire/stealth interaction proven",
    "runtime vector behavior proven",
    "runtime range behavior proven",
    "runtime camera switching proven",
    "runtime cutscene playback proven",
    "runtime object identity proven",
    "runtime spawnthing proven",
    "runtime getthingref proven",
    "live loose-msl loading proven",
    "packed-resource script selection proven",
    "private-frame review complete",
    "source-selection observation complete",
    "exact visible token identity proven",
    "exact command descriptor layout proven",
    "exact arity proven",
    "exact argument type schema proven",
    "bea patching behavior proven",
    "visual qa complete",
    "godot parity proven",
    "rebuild implementation complete",
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


def mirror_for(path: Path) -> Path:
    rel = path.relative_to(ROOT)
    return ROOT / "lore-book" / rel


def count_collection(value: Any) -> int:
    if isinstance(value, dict):
        return len(value)
    if isinstance(value, list):
        return len(value)
    return 0


def descriptor_count(schema: dict[str, Any]) -> int:
    if "descriptorSlots" in schema:
        return count_collection(schema["descriptorSlots"])
    if "descriptorRecords" in schema:
        return count_collection(schema["descriptorRecords"])
    return 0


def source_descriptor_indices(schema: dict[str, Any]) -> list[int]:
    records = schema.get("descriptorSlots", schema.get("descriptorRecords", []))
    if isinstance(records, dict):
        iterable = records.values()
    else:
        iterable = records
    indices: list[int] = []
    for record in iterable:
        if isinstance(record, dict) and "index" in record:
            indices.append(int(record["index"]))
    return indices


def source_claim_count(schema: dict[str, Any]) -> int:
    return count_collection(schema.get("claims", []))


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
    descriptor = read_json(DESCRIPTOR_SCHEMA)

    require(result["schemaVersion"] == "missionscript-command-effect-rebuild-interface-rollup.v1", "schema version mismatch", failures)
    require(result["status"] == "PASS", "status mismatch", failures)
    require(result["rollupStatus"] == STATUS_TOKEN, "rollup status mismatch", failures)
    require(result["missionScriptCommandEffectRebuildInterfaceRollupStatus"] == STATUS_TOKEN, "named status mismatch", failures)
    require(result["previousSlice"] == PREVIOUS_SLICE, "previous slice mismatch", failures)
    require(result["selectedChildLane"] == NEXT_SLICE, "selected child lane mismatch", failures)
    require(result["selectedNextSlice"] == NEXT_SLICE, "selected next slice mismatch", failures)

    source = result["source"]
    for key in TRUE_GUARDS:
        require(source[key] is True, f"source true guard mismatch: {key}", failures)
    for key in ("programFilesInputUsed", "liveLooseMslLoading", "packedResourceScriptSelectionProven", "runtimeExecution", "godotWork", "ghidraMutation", "executablePatching", "rebuildImplementation"):
        require(source[key] is False, f"source false guard mismatch: {key}", failures)

    static = result["staticContext"]
    require(static["staticFunctionQuality"] == "6411/6411 = 100.00%", "static function quality mismatch", failures)
    require(static["staticDebt"] == "0 / 0 / 0", "static debt mismatch", failures)
    require(static["expandedStaticSurface"] == "1560/1560 = 100.00%", "expanded surface mismatch", failures)
    require(static["currentRiskFocused"] == "1179/1179 = 100.00%", "current-risk mismatch", failures)
    require(static["remainingActiveFocusedWork"] == 0, "remaining work mismatch", failures)
    require(static["latestGhidraBackupClass"] == "verified-static-backup-redacted", "backup class mismatch", failures)

    descriptor_table = descriptor["descriptorTable"]
    require(descriptor["status"] == "PASS", "descriptor source status mismatch", failures)
    require(descriptor["source"]["runtimeExecution"] is False, "descriptor runtime guard mismatch", failures)
    require(descriptor["source"]["ghidraMutation"] is False, "descriptor mutation guard mismatch", failures)
    require(descriptor_table["declaredSlots"] == 144, "descriptor declared slots mismatch", failures)
    require(descriptor_table["strideBytes"] == 64, "descriptor stride mismatch", failures)
    require(descriptor_table["slotsWithAssignments"] == 144, "descriptor assignment count mismatch", failures)
    require(descriptor_table["observedNameAssignments"] == 143, "descriptor observed names mismatch", failures)
    descriptor_records = descriptor["records"]
    require(len(descriptor_records) == 144, "descriptor records count mismatch", failures)
    require(sum(1 for row in descriptor_records if row.get("commandName")) == 129, "descriptor named record count mismatch", failures)
    require(len(descriptor["selectedExamples"]) == 12, "descriptor selected example count mismatch", failures)
    require(descriptor_table["finalSlotBoundary"]["index"] == 143, "descriptor final slot index mismatch", failures)
    require(descriptor_table["finalSlotBoundary"]["nameStatus"] == "not-written-in-decompile", "descriptor final slot status mismatch", failures)

    accounting = result["sourceSchemaAccounting"]
    require(accounting["descriptorSchemaCount"] == 1, "descriptor schema count mismatch", failures)
    require(accounting["commandEffectSchemaCount"] == 9, "command-effect schema count mismatch", failures)
    require(accounting["sourceSchemaCount"] == 10, "source schema count mismatch", failures)
    require(accounting["sourceMirrorPairCount"] == 20, "source mirror pair count mismatch", failures)
    require(accounting["descriptorDeclaredSlots"] == 144, "rollup descriptor declared slots mismatch", failures)
    require(accounting["descriptorStrideBytes"] == 64, "rollup descriptor stride mismatch", failures)
    require(accounting["descriptorSlotsWithAssignments"] == 144, "rollup descriptor assignment mismatch", failures)
    require(accounting["descriptorObservedNameAssignments"] == 143, "rollup observed name mismatch", failures)
    require(accounting["descriptorNamedRecordCount"] == 129, "rollup named record mismatch", failures)
    require(accounting["descriptorSelectedExampleCount"] == 12, "rollup selected example mismatch", failures)

    rollup = result["rollupAccounting"]
    require(rollup["selectedSourceProofCount"] == 9, "selected source proof count mismatch", failures)
    require(rollup["sourceProofCount"] == 9, "source proof count mismatch", failures)
    require(rollup["sourceSchemaCount"] == 10, "rollup source schema count mismatch", failures)
    require(rollup["commandFamilyCount"] == 9, "command family count mismatch", failures)
    require(rollup["descriptorRecordCount"] == 52, "descriptor record count mismatch", failures)
    require(rollup["uniqueDescriptorTokenCount"] == 48, "unique descriptor token count mismatch", failures)
    require(rollup["duplicateDescriptorTokenCount"] == 4, "duplicate descriptor token count mismatch", failures)
    require(rollup["notClaimedTokenTotal"] == 165, "not-claimed total mismatch", failures)
    require(rollup["sourceClaimsCount"] == 29, "claims total mismatch", failures)
    require(rollup["uniqueEvidenceWaveCount"] == 16, "evidence wave count mismatch", failures)
    require(rollup["interfaceRowCount"] == 9, "interface row count mismatch", failures)
    require(rollup["rollupTrueGuardCount"] == len(TRUE_GUARDS), "true guard count mismatch", failures)
    require(rollup["falseGuardCount"] == len(FALSE_GUARDS), "false guard count mismatch", failures)
    require(rollup["zeroCounterCount"] == len(ZERO_COUNTERS), "zero counter count mismatch", failures)
    require(rollup["publicLeakCheck"] == "PASS", "public leak check mismatch", failures)

    descriptor_coverage = result["descriptorCoverage"]
    require(descriptor_coverage["schemaVersion"] == descriptor["schemaVersion"], "descriptor coverage schema version mismatch", failures)
    require(descriptor_coverage["declaredSlots"] == descriptor_table["declaredSlots"], "descriptor coverage slots mismatch", failures)
    require(descriptor_coverage["loreSchemaMirrorMatch"] is True, "descriptor lore schema mirror flag mismatch", failures)
    require(descriptor_coverage["loreProofMirrorMatch"] is True, "descriptor lore proof mirror flag mismatch", failures)

    source_rows = {row["familyId"]: row for row in result["sourceSchemas"]}
    require(len(source_rows) == len(SOURCE_SCHEMAS), "source schema row count mismatch", failures)

    all_indices: list[int] = []
    unique_waves: set[str] = set()
    claims_total = 0
    not_claimed_total = 0
    for expected in SOURCE_SCHEMAS:
        family = expected["familyId"]
        source_schema = read_json(expected["schema"])
        row = source_rows.get(family)
        require(row is not None, f"missing source row: {family}", failures)
        if row is None:
            continue
        require(source_schema["status"] == "PASS", f"source status mismatch: {family}", failures)
        require(source_schema["source"]["runtimeExecution"] is False, f"source runtime guard mismatch: {family}", failures)
        require(source_schema["source"]["ghidraMutation"] is False, f"source mutation guard mismatch: {family}", failures)
        require(row["status"] == "PASS", f"rollup row status mismatch: {family}", failures)
        require(row["schemaVersion"] == source_schema["schemaVersion"], f"schema version mismatch: {family}", failures)
        require(row["descriptorEntryCount"] == expected["entries"], f"rollup descriptor count mismatch: {family}", failures)
        require(descriptor_count(source_schema) == expected["entries"], f"source descriptor count mismatch: {family}", failures)
        require(tuple(source_descriptor_indices(source_schema)) == expected["indices"], f"source descriptor indices mismatch: {family}", failures)
        require(tuple(row["descriptorIndices"]) == expected["indices"], f"rollup descriptor indices mismatch: {family}", failures)
        require(row["uniqueDescriptorIndexCount"] == len(set(expected["indices"])), f"unique descriptor count mismatch: {family}", failures)
        require(len(source_schema["source"]["evidenceWaves"]) == expected["waves"], f"evidence wave count mismatch: {family}", failures)
        require(row["evidenceWaveCount"] == expected["waves"], f"rollup evidence wave count mismatch: {family}", failures)
        require(source_claim_count(source_schema) == expected["claims"], f"source claims count mismatch: {family}", failures)
        require(row["claimsCount"] == expected["claims"], f"rollup claims count mismatch: {family}", failures)
        require(len(source_schema["notClaimed"]) == expected["notClaimed"], f"source not-claimed mismatch: {family}", failures)
        require(row["notClaimedCount"] == expected["notClaimed"], f"rollup not-claimed mismatch: {family}", failures)
        require(row["runtimeExecution"] is False, f"rollup runtime guard mismatch: {family}", failures)
        require(row["ghidraMutation"] is False, f"rollup mutation guard mismatch: {family}", failures)
        require(row["loreSchemaMirrorMatch"] is True, f"lore schema mirror flag mismatch: {family}", failures)
        require(row["loreProofMirrorMatch"] is True, f"lore proof mirror flag mismatch: {family}", failures)
        all_indices.extend(expected["indices"])
        unique_waves.update(source_schema["source"]["evidenceWaves"])
        claims_total += expected["claims"]
        not_claimed_total += expected["notClaimed"]

    require(len(all_indices) == 52, "computed descriptor entry total mismatch", failures)
    require(len(set(all_indices)) == 48, "computed unique descriptor index mismatch", failures)
    duplicate_indices = {index: all_indices.count(index) for index in set(all_indices) if all_indices.count(index) > 1}
    require(set(duplicate_indices) == set(EXPECTED_DUPLICATE_INDICES), "duplicate descriptor indices mismatch", failures)
    require(all(count == 2 for count in duplicate_indices.values()), "duplicate descriptor counts mismatch", failures)
    require(result["descriptorIndexAccounting"]["totalCommandEffectDescriptorEntries"] == 52, "descriptor accounting total mismatch", failures)
    require(result["descriptorIndexAccounting"]["uniqueCommandEffectDescriptorIndices"] == 48, "descriptor accounting unique mismatch", failures)
    require({int(key): value["token"] for key, value in result["descriptorIndexAccounting"]["duplicateDescriptorIndices"].items()} == EXPECTED_DUPLICATE_INDICES, "duplicate descriptor token mismatch", failures)
    require(len(unique_waves) == 16, "computed evidence wave unique count mismatch", failures)
    require(claims_total == 29, "computed claims total mismatch", failures)
    require(not_claimed_total == 165, "computed not-claimed total mismatch", failures)
    require(len(result["interfaceFamilies"]) == 9, "interface family count mismatch", failures)

    guards = result["guardSummary"]
    for key in TRUE_GUARDS:
        require(guards["trueGuards"][key] is True, f"true guard mismatch: {key}", failures)
    for key in FALSE_GUARDS:
        require(guards["falseGuards"][key] is False, f"false guard mismatch: {key}", failures)
    for key in ZERO_COUNTERS:
        require(guards["zeroCounters"][key] == 0, f"zero counter mismatch: {key}", failures)


def check_mirrors(failures: list[str]) -> None:
    mirror_sources = [DESCRIPTOR_SCHEMA, DESCRIPTOR_PROOF]
    for source in SOURCE_SCHEMAS:
        mirror_sources.append(source["schema"])
        mirror_sources.append(source["proof"])
    require(len(mirror_sources) == 20, "mirror source count mismatch", failures)
    for path in mirror_sources:
        mirror = mirror_for(path)
        require(mirror.is_file(), f"missing lore mirror: {mirror.relative_to(ROOT)}", failures)
        if mirror.is_file():
            require(read_text(path) == read_text(mirror), f"lore mirror mismatch: {path.relative_to(ROOT)}", failures)
    require(read_text(LORE_PLAN) == read_text(PLAN), "rollup lore plan mirror mismatch", failures)
    require(read_text(LORE_RESULT) == read_text(RESULT), "rollup lore result mirror mismatch", failures)


def check_docs(failures: list[str]) -> None:
    required_tokens = (
        THIS_SLICE,
        PREVIOUS_SLICE,
        NEXT_SLICE,
        "missionscript-command-effect-rebuild-interface-rollup.md",
        "missionscript-command-effect-rebuild-interface-rollup.v1.json",
        f"rollupStatus={STATUS_TOKEN}",
        f"missionScriptCommandEffectRebuildInterfaceRollupStatus={STATUS_TOKEN}",
        "descriptorSchemaCount=1",
        "commandEffectSchemaCount=9",
        "sourceSchemaCount=10",
        "sourceMirrorPairCount=20",
        "descriptorDeclaredSlots=144",
        "descriptorStrideBytes=64",
        "descriptorSlotsWithAssignments=144",
        "descriptorObservedNameAssignments=143",
        "descriptorNamedRecordCount=129",
        "descriptorSelectedExampleCount=12",
        "descriptorRecordCount=52",
        "uniqueDescriptorTokenCount=48",
        "duplicateDescriptorTokenCount=4",
        "notClaimedTokenTotal=165",
        "sourceClaimsCount=29",
        "uniqueEvidenceWaveCount=16",
        "rollupTrueGuardCount=7",
        "falseGuardCount=60",
        "zeroCounterCount=25",
        "publicLeakCheck=PASS",
        "latestGhidraBackupClass=verified-static-backup-redacted",
        "selectedNextSlice=MissionScript Command-Effect Rebuild Fixture Selection Proof Plan",
        "33 HighlightHudPart",
        "34 UnHighlightHudPart",
        "84 AddScore",
        "105 LevelLostString",
    )
    for path in (PLAN, READINESS):
        text = read_text(path)
        for token in required_tokens:
            require(token in text, f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        check_no_bad_public_content(path, failures)
    check_no_bad_public_content(RESULT, failures)
    check_no_bad_public_content(LORE_PLAN, failures)
    check_no_bad_public_content(LORE_RESULT, failures)

    front_door_tokens = (
        THIS_SLICE,
        NEXT_SLICE,
        "missionscript-command-effect-rebuild-interface-rollup.md",
        "missionscript-command-effect-rebuild-interface-rollup.v1.json",
        f"rollupStatus={STATUS_TOKEN}",
        "sourceSchemaCount=10",
        "descriptorRecordCount=52",
        "uniqueDescriptorTokenCount=48",
        "falseGuardCount=60",
        "zeroCounterCount=25",
    )
    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX):
        text = read_text(path)
        for token in front_door_tokens:
            require(token in text, f"missing front-door token in {path.relative_to(ROOT)}: {token}", failures)

    require(read_text(LORE_BACKLOG) == read_text(BACKLOG), "lore backlog mirror mismatch", failures)
    require(read_text(LORE_MAPPED) == read_text(MAPPED), "lore mapped-systems mirror mismatch", failures)
    require(read_text(LORE_BIN_INDEX) == read_text(BIN_INDEX), "lore binary index mirror mismatch", failures)
    require(read_text(LORE_RE_INDEX) == read_text(RE_INDEX), "lore RE index mirror mismatch", failures)

    backlog = read_text(BACKLOG)
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed rollup slice", failures)
    require(f"The selected active static-to-proof slice is {THIS_SLICE}. Status: selected" not in backlog, "backlog still marks rollup active", failures)
    require(f"Completed {NEXT_SLICE}" in backlog, "backlog missing completed fixture selection slice", failures)
    require(f"The selected active static-to-proof slice is {NEXT_SLICE}. Status: selected" not in backlog, "backlog still marks fixture selection active", failures)
    require(f"Completed {COMPLETED_SLOT_FIXTURE_SLICE}" in backlog, "backlog missing completed slot fixture plan", failures)
    require(f"The selected active static-to-proof slice is {COMPLETED_SLOT_FIXTURE_SLICE}. Status: selected" not in backlog, "backlog still marks slot fixture plan active", failures)
    require(f"Completed {COMPLETED_DETERMINISTIC_SLICE}" in backlog, "backlog missing completed deterministic codec slice", failures)
    require(f"The selected active static-to-proof slice is {COMPLETED_DETERMINISTIC_SLICE}. Status: selected" not in backlog, "backlog still marks deterministic codec active", failures)
    require(f"Completed {COMPLETED_CLEAN_ROOM_SLICE.replace(' Proof Plan', ' Proof')}" in backlog, "backlog missing completed clean-room codec interface slice", failures)
    require(f"The selected active static-to-proof slice is {COMPLETED_CLEAN_ROOM_SLICE}. Status: selected" not in backlog, "backlog still marks clean-room codec interface active", failures)
    require(f"Completed {COMPLETION_ROLLUP_SLICE}" in backlog, "backlog missing completed fixture-family completion rollup slice", failures)
    require(f"The selected active static-to-proof slice is {COMPLETION_ROLLUP_SLICE}. Status: selected" not in backlog, "backlog still marks fixture-family completion rollup active", failures)
    require(f"The selected active static-to-proof slice is {POST_ROLLUP_NEXT_SLICE}. Status: selected" in backlog, "backlog missing active post-rollup selection refresh slice", failures)
    require("selectedNextSlice=MissionScript Command-Effect Rebuild Interface Rollup Proof Plan" in backlog, "backlog missing predecessor selected-next token", failures)


def check_package(failures: list[str]) -> None:
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(scripts.get("test:missionscript-command-descriptor-schema") == r"py -3 tools\missionscript_command_descriptor_schema_probe.py --check", "missing descriptor package script", failures)
    for source in SOURCE_SCHEMAS:
        script_name = str(source["script"])
        require(script_name in scripts, f"missing source package script: {script_name}", failures)
    require(scripts.get("test:missionscript-command-effect-rebuild-interface-rollup") == r"py -3 tools\missionscript_command_effect_rebuild_interface_rollup_probe.py --check", "missing rollup package script", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_result(failures)
    check_mirrors(failures)
    check_docs(failures)
    check_package(failures)
    require(no_bea_process_running(), "BEA.exe process is running after rollup", failures)

    if failures:
        print("MissionScript command-effect rebuild-interface rollup probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("MissionScript command-effect rebuild-interface rollup probe: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
