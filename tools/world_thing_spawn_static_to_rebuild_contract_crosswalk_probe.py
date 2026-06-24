#!/usr/bin/env python3
"""Validate the World / Thing / Spawn static-to-rebuild crosswalk."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "world-thing-spawn-static-to-rebuild-contract-crosswalk.md"
RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "world-thing-spawn-static-to-rebuild-contract-crosswalk.v1.json"
LORE_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "world-thing-spawn-static-to-rebuild-contract-crosswalk.md"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "world-thing-spawn-static-to-rebuild-contract-crosswalk.v1.json"
READINESS = ROOT / "release" / "readiness" / "world_thing_spawn_static_to_rebuild_contract_crosswalk_2026-06-09.md"

BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
LORE_MAPPED = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
LORE_BIN_INDEX = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
LORE_RE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"
PACKAGE_JSON = ROOT / "package.json"

CORPUS = ROOT / "reverse-engineering" / "game-assets" / "world-thing-spawn-copied-corpus-schema.v1.json"
SPAWNER = ROOT / "reverse-engineering" / "binary-analysis" / "world-thing-spawn-spawner-handoff-static.v1.json"
GETTHINGREF = ROOT / "reverse-engineering" / "binary-analysis" / "world-thing-spawn-getthingref-object-reference-static.v1.json"

THIS_SLICE = "World / Thing / Spawn Static-To-Rebuild Contract Crosswalk Proof Plan"
PREVIOUS_SLICE = "Static-To-Proof Rebuild Transition Next Safe Slice Selection Proof Plan"
NEXT_SLICE = "MissionScript Command-Effect Rebuild Interface Rollup Proof Plan"
ACTIVE_SLICE = "MissionScript Command-Effect Rebuild Fixture Selection Proof Plan"
STATUS_TOKEN = "world-thing-spawn-static-to-rebuild-contract-crosswalk-complete-static-contract-not-runtime-proof"

TRUE_GUARDS = (
    "crosswalkOnly",
    "staticPublicSafeOnly",
    "copiedAppOwnedInputOnly",
    "trackedLooseMslCorpusOnly",
    "fieldRolesStaticOnly",
)

FALSE_GUARDS = (
    "programFilesInputUsed",
    "liveLooseMslLoading",
    "packedResourceScriptSelectionProven",
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
    "sourceSelectionProven",
    "nativeInput",
    "debuggerAttachment",
    "godotWork",
    "ghidraMutation",
    "executablePatching",
    "rebuildImplementation",
    "runtimeObjectIdentityProven",
    "runtimeObjectLookupByNameProven",
    "runtimeSpawnThingBehaviorProven",
    "runtimeGetThingRefBehaviorProven",
    "runtimeWorldLoadingProven",
    "runtimeSpawnerBehaviorProven",
    "runtimeUnitBattleEngineSpawnBehaviorProven",
    "runtimeMissionScriptExecutionProven",
    "runtimeCommandEffectsProven",
    "exactDescriptorLayoutProven",
    "exactHandlerAddressProven",
    "exactVmObjectCodeWorldThingSpawnerUnitLayoutsProven",
    "exactSourceBodyIdentityProven",
    "rebuildParityProven",
    "noNoticeableDifferenceParityProven",
)

ZERO_COUNTS = (
    "runtimeObservationRows",
    "missionScriptRuntimeEvidenceRows",
    "privateFrameRowsObserved",
    "sourceObservedRows",
    "sourceRuntimeObservationRows",
    "sourceRowStatusChangedCount",
    "ghidraMutationRows",
    "rebuildImplementationRows",
    "beProcessesAfterCrosswalk",
    "publicAbsolutePathLeakCount",
    "publicSha256ValueLeakCount",
    "publicWindowIdentifierLeakCount",
    "publicProcessIdentifierLeakCount",
    "privatePathLeakCount",
    "rawArtifactLeakCount",
    "rawDialogueLeakCount",
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
    "runtime unit/battleengine spawn behavior proven",
    "live loose-msl loading proven",
    "packed-resource script selection proven",
    "exact layouts proven",
    "source-body identity proven",
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
    corpus = read_json(CORPUS)
    spawner = read_json(SPAWNER)
    getthingref = read_json(GETTHINGREF)

    require(result["schemaVersion"] == "world-thing-spawn-static-to-rebuild-contract-crosswalk.v1", "schema version mismatch", failures)
    require(result["status"] == "PASS", "result status mismatch", failures)
    require(result["crosswalkStatus"] == STATUS_TOKEN, "crosswalk status mismatch", failures)
    require(result["worldThingSpawnStaticToRebuildContractCrosswalkStatus"] == STATUS_TOKEN, "named status mismatch", failures)
    require(result["selectedChildLane"] == NEXT_SLICE, "selected child lane mismatch", failures)
    require(result["selectedNextSlice"] == NEXT_SLICE, "selected next slice mismatch", failures)

    source = result["source"]
    for key in TRUE_GUARDS[:4]:
        require(source[key] is True, f"source guard must be true: {key}", failures)
    for key in ("programFilesInputUsed", "liveLooseMslLoading", "packedResourceScriptSelectionProven", "runtimeExecution", "ghidraMutation", "rebuildImplementation"):
        require(source[key] is False, f"source guard must be false: {key}", failures)

    static = result["staticContext"]
    require(static["staticFunctionQuality"] == "6411/6411 = 100.00%", "static function quality mismatch", failures)
    require(static["staticDebt"] == "0 / 0 / 0", "static debt mismatch", failures)
    require(static["expandedStaticSurface"] == "1560/1560 = 100.00%", "expanded surface mismatch", failures)
    require(static["currentRiskFocused"] == "1179/1179 = 100.00%", "current-risk mismatch", failures)
    require(static["remainingActiveFocusedWork"] == 0, "remaining active work mismatch", failures)
    require(static["latestGhidraBackupClass"] == "verified-static-backup-redacted", "backup class mismatch", failures)

    accounting = result["contractAccounting"]
    require(accounting["selectedSourceProofCount"] == 3, "selected source proof count mismatch", failures)
    require(accounting["sourceSchemaCount"] == 3, "source schema count mismatch", failures)
    require(accounting["contractSectionCount"] == 9, "contract section count mismatch", failures)
    require(accounting["contractFalseGuardCount"] == len(FALSE_GUARDS), "false guard count mismatch", failures)
    require(accounting["contractZeroCounterCount"] == len(ZERO_COUNTS), "zero counter count mismatch", failures)
    require(accounting["publicLeakCheck"] == "PASS", "public leak check mismatch", failures)

    require(len(result["sourceProofs"]) == 3, "source proof count mismatch", failures)
    require(len(result["contractRows"]) == 9, "contract row count mismatch", failures)
    require(len(result["fieldRoles"]) == 12, "field role count mismatch", failures)

    corpus_counts = result["corpusCounts"]
    source_evidence = result["sourceEvidence"]
    require(corpus_counts == corpus["corpusCounts"], "corpus count carry-forward mismatch", failures)
    require(source_evidence["copiedCorpus"]["rawGetThingRefRows"] == corpus["corpusCounts"]["rawDetailedCallRows"]["GetThingRef"] == 574, "raw GetThingRef mismatch", failures)
    require(source_evidence["copiedCorpus"]["rawSpawnThingRows"] == corpus["corpusCounts"]["rawDetailedCallRows"]["SpawnThing"] == 70, "raw SpawnThing mismatch", failures)
    require(source_evidence["copiedCorpus"]["rawTotalRows"] == corpus["corpusCounts"]["rawDetailedCallRows"]["total"] == 644, "raw total mismatch", failures)
    require(source_evidence["copiedCorpus"]["uniqueObjectReferenceRowsTotal"] == corpus["corpusCounts"]["uniqueObjectReferenceRows"]["total"] == 436, "unique total mismatch", failures)
    require(source_evidence["copiedCorpus"]["spawnPreservingRowsTotal"] == corpus["corpusCounts"]["uniqueSpawnPreservingSpawnerRows"]["total"] == 447, "spawn-preserving total mismatch", failures)

    selected_spawn = result["selectedSpawnFamily"]
    require(selected_spawn["name"] == corpus["selectedFamily"]["name"] == spawner["selectedFamily"]["name"] == "training-target-spawn-family", "selected SpawnThing family mismatch", failures)
    require(selected_spawn["rawRows"] == corpus["selectedFamily"]["rawRows"] == spawner["selectedFamily"]["rawRows"] == 34, "selected SpawnThing raw mismatch", failures)
    require(selected_spawn["uniqueObjectReferenceRows"] == corpus["selectedFamily"]["uniqueObjectReferenceRows"] == spawner["selectedFamily"]["uniqueObjectReferenceRows"] == 6, "selected SpawnThing unique mismatch", failures)
    require(selected_spawn["uniqueThingLabels"] == corpus["selectedFamily"]["uniqueThingLabels"] == spawner["selectedFamily"]["uniqueThingLabels"] == 4, "selected SpawnThing label mismatch", failures)
    require(selected_spawn["uniqueFileThingSpawnerRows"] == corpus["selectedFamily"]["uniqueFileThingSpawnerRows"] == spawner["selectedFamily"]["uniqueFileThingSpawnerRows"] == 8, "selected SpawnThing file/thing/spawner mismatch", failures)

    selected_get = result["selectedGetThingRefFamily"]
    require(selected_get["name"] == getthingref["selectedFamily"]["name"] == "training-target-zone-getthingref-family", "selected GetThingRef family mismatch", failures)
    require(selected_get["rawRows"] == getthingref["selectedFamily"]["rawRows"] == 9, "selected GetThingRef raw mismatch", failures)
    require(selected_get["uniqueObjectReferenceRows"] == getthingref["selectedFamily"]["uniqueObjectReferenceRows"] == 8, "selected GetThingRef unique mismatch", failures)
    require(selected_get["duplicateCallRows"] == getthingref["selectedFamily"]["duplicateCallRows"] == 1, "selected GetThingRef duplicate mismatch", failures)
    require(selected_get["emptySpawnerRows"] == getthingref["selectedFamily"]["emptySpawnerRows"] == 9, "selected GetThingRef empty-spawner mismatch", failures)
    require(selected_get["linkageLayerCount"] == len(getthingref["linkageLayers"]) == 4, "selected GetThingRef linkage mismatch", failures)

    handoff = source_evidence["spawnerHandoff"]
    require(handoff["handoffLayerCount"] == len(spawner["handoffLayers"]) == 8, "spawner layer count mismatch", failures)
    require(handoff["staticFieldRoleCount"] == len(spawner["fieldRoleEvidence"]) == 12, "field role count mismatch", failures)
    for token in (
        "DAT_008553f4",
        "0x0050f970 CWorldPhysicsManager__CreateSpawner",
        "0x004e3c60 CSpawnerThng__DoSpawn",
        "CUnit__VFunc08_InitAndAddToWorld",
        "0x004fc3a0 CUnit__SetSpawnCooldownState3",
    ):
        require(token in json.dumps(result), f"schema missing anchor: {token}", failures)

    guard = result["guardSummary"]
    for key in TRUE_GUARDS:
        require(guard[key] is True, f"guard must be true: {key}", failures)
    for key in FALSE_GUARDS:
        require(guard[key] is False, f"guard must be false: {key}", failures)
    for key in ZERO_COUNTS:
        require(guard[key] == 0, f"guard count must be zero: {key}", failures)

    require("the selected contract is public-safe and static-only" in result["claimBoundary"]["proves"], "claim boundary missing public-safe proof", failures)
    for token in (
        "runtime SpawnThing",
        "runtime GetThingRef",
        "runtime MissionScript execution",
        "runtime world loading",
        "runtime spawner behavior",
        "Godot parity",
        "rebuild implementation",
        "rebuild parity",
        "no-noticeable-difference parity",
    ):
        require(token in result["claimBoundary"]["doesNotProve"], f"claim boundary missing not-proven token: {token}", failures)

    require(read_json(LORE_RESULT) == result, "lore schema mirror mismatch", failures)
    require(no_bea_process_running(), "BEA process still running after crosswalk validation", failures)


def check_docs(failures: list[str]) -> None:
    require(read_text(LORE_PLAN) == read_text(PLAN), "lore plan mirror mismatch", failures)
    required_tokens = (
        THIS_SLICE,
        PREVIOUS_SLICE,
        NEXT_SLICE,
        "world-thing-spawn-static-to-rebuild-contract-crosswalk.md",
        "world-thing-spawn-static-to-rebuild-contract-crosswalk.v1.json",
        f"crosswalkStatus={STATUS_TOKEN}",
        f"worldThingSpawnStaticToRebuildContractCrosswalkStatus={STATUS_TOKEN}",
        "selectedSourceProofCount=3",
        "sourceSchemaCount=3",
        "contractSectionCount=9",
        "contractFalseGuardCount=35",
        "contractZeroCounterCount=16",
        "publicLeakCheck=PASS",
        "selectedNextSlice=MissionScript Command-Effect Rebuild Interface Rollup Proof Plan",
        "latestGhidraBackupClass=verified-static-backup-redacted",
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
        "runtimeExecution=false",
        "beLaunch=false",
        "screenshotCapture=false",
        "ghidraMutation=false",
        "rebuildImplementation=false",
        "runtimeObservationRows=0",
        "beProcessesAfterCrosswalk=0",
    )
    for path in (PLAN, READINESS):
        text = read_text(path)
        for token in required_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing token: {token}", failures)
        check_no_bad_public_content(path, failures)

    for path in (RESULT, LORE_PLAN, LORE_RESULT):
        check_no_bad_public_content(path, failures)

    front_door_tokens = (
        THIS_SLICE,
        "world-thing-spawn-static-to-rebuild-contract-crosswalk.md",
        "world-thing-spawn-static-to-rebuild-contract-crosswalk.v1.json",
        STATUS_TOKEN,
        "selectedSourceProofCount=3",
        "contractSectionCount=9",
        "contractFalseGuardCount=35",
        "contractZeroCounterCount=16",
        "publicLeakCheck=PASS",
        NEXT_SLICE,
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
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed crosswalk slice", failures)
    require(f"The selected active static-to-proof slice is {THIS_SLICE}. Status: selected" not in backlog, "backlog still marks crosswalk active", failures)
    require(f"Completed {NEXT_SLICE}" in backlog, "backlog missing completed MissionScript rollup slice", failures)
    require(f"The selected active static-to-proof slice is {NEXT_SLICE}. Status: selected" not in backlog, "backlog still marks MissionScript rollup active", failures)
    require(f"The selected active static-to-proof slice is {ACTIVE_SLICE}. Status: selected" in backlog, "backlog missing active fixture-selection slice", failures)


def check_package(failures: list[str]) -> None:
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:world-thing-spawn-static-to-rebuild-contract-crosswalk")
        == r"py -3 tools\world_thing_spawn_static_to_rebuild_contract_crosswalk_probe.py --check",
        "missing package crosswalk test script",
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
        print("World/Thing/Spawn static-to-rebuild crosswalk probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("World/Thing/Spawn static-to-rebuild crosswalk probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
