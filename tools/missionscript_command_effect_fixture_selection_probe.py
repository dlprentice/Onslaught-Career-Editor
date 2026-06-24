#!/usr/bin/env python3
"""Validate the MissionScript command-effect fixture-selection proof."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-command-effect-fixture-selection.md"
RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-command-effect-fixture-selection.v1.json"
LORE_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-command-effect-fixture-selection.md"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-command-effect-fixture-selection.v1.json"
READINESS = ROOT / "release" / "readiness" / "missionscript_command_effect_fixture_selection_2026-06-09.md"

ROLLUP = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-command-effect-rebuild-interface-rollup.v1.json"
SLOT_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-slot-command-effect.v1.json"
SAVE_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "save-options-controller-byte-preservation-copied-file.v1.json"

BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
LORE_MAPPED = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
LORE_BIN_INDEX = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
LORE_RE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"
PACKAGE_JSON = ROOT / "package.json"

THIS_SLICE = "MissionScript Command-Effect Rebuild Fixture Selection Proof Plan"
PREVIOUS_SLICE = "MissionScript Command-Effect Rebuild Interface Rollup Proof Plan"
NEXT_SLICE = "MissionScript Slot Bitset/Save Rebuild Fixture Proof Plan"
COMPLETED_DETERMINISTIC_SLICE = "MissionScript Slot Bitset/Save Deterministic Codec Proof Plan"
COMPLETED_CLEAN_ROOM_SLICE = "MissionScript Slot Bitset/Save Clean-Room Codec Interface Proof Plan"
CUTSCENE_FIXTURE_SLICE = "MissionScript Cutscene Pan-Camera / Position Command-Effect Deterministic Fixture Proof Plan"
OBJECTIVE_FIXTURE_SLICE = "MissionScript Objective/Outcome Command-Effect Fixture Proof Plan"
MESSAGE_AUDIO_FIXTURE_SLICE = "MissionScript Message/Audio Command-Effect Fixture Proof Plan"
HUD_DISPLAY_FIXTURE_SLICE = "MissionScript HUD / Display Command-Effect Fixture Proof Plan"
ACTIVE_SLICE = "MissionScript Thing Value / Engine Helper Command-Effect Fixture Proof Plan"
NEXT_ACTIVE_SLICE = "MissionScript Player-State / Score Command-Effect Fixture Proof Plan"
COMPLETION_ROLLUP_SLICE = "MissionScript Command-Effect Fixture Family Completion Rollup Proof Plan"
POST_ROLLUP_NEXT_SLICE = "Static-To-Proof Rebuild Transition Post-Command-Effect Fixture Next Safe Slice Selection Refresh Proof Plan"
POST_GOODIE_SELECTION_SLICE = "MissionScript Command-Effect Post-Goodie Selection Refresh Proof Plan"
STATUS_TOKEN = "missionscript-command-effect-fixture-selection-complete-slot-bitset-save-selected"
ROLLUP_STATUS = "missionscript-command-effect-rebuild-interface-rollup-complete-static-interface-contract-not-runtime-proof"

FALSE_GUARDS = (
    "programFilesInputUsed",
    "liveLooseMslLoading",
    "packedResourceScriptSelectionProven",
    "runtimeExecution",
    "runtimeMissionScriptExecutionProven",
    "runtimeCommandEffectsProven",
    "runtimeSlotPersistenceProven",
    "runtimeSaveBehaviorProven",
    "runtimeTutorialProgressionProven",
    "runtimeLevel500BranchProven",
    "runtimeFenrirStateProven",
    "beLaunch",
    "newLaunch",
    "screenshotCapture",
    "privateFrameReviewPerformed",
    "rowObservation",
    "exactTextOcrPerformed",
    "rawDialoguePublished",
    "sourceSelectionObserved",
    "nativeInput",
    "debuggerAttachment",
    "godotWork",
    "ghidraMutation",
    "executablePatching",
    "rebuildImplementation",
    "exactCommandDescriptorLayoutProven",
    "exactCommandArityProven",
    "exactArgumentTypeSchemaProven",
    "exactCGameLayoutProven",
    "exactCCareerLayoutProven",
    "runtimeDefaultoptionsBehaviorProven",
    "runtimeMenuBehaviorProven",
    "rebuildParityProven",
    "noNoticeableDifferenceParityProven",
)

ZERO_COUNTERS = (
    "runtimeObservationRows",
    "missionScriptRuntimeEvidenceRows",
    "runtimeCommandEffectRows",
    "runtimeSlotEvidenceRows",
    "runtimeSaveRows",
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
    "beProcessesAfterSelection",
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
    "runtime slot persistence proven",
    "runtime save behavior proven",
    "runtime tutorial progression proven",
    "runtime level500 branch proven",
    "runtime fenrir state proven",
    "live loose-msl loading proven",
    "packed-resource script selection proven",
    "private-frame review complete",
    "source-selection observation complete",
    "exact descriptor layout proven",
    "exact arity proven",
    "exact argument type schema proven",
    "exact cgame layout proven",
    "exact ccareer layout proven",
    "visual qa complete",
    "godot parity proven",
    "executable patching behavior proven",
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
    rollup = read_json(ROLLUP)
    slot = read_json(SLOT_SCHEMA)
    save = read_json(SAVE_SCHEMA)

    require(result["schemaVersion"] == "missionscript-command-effect-fixture-selection.v1", "schema version mismatch", failures)
    require(result["status"] == "PASS", "status mismatch", failures)
    require(result["fixtureSelectionStatus"] == STATUS_TOKEN, "fixture selection status mismatch", failures)
    require(result["previousSlice"] == PREVIOUS_SLICE, "previous slice mismatch", failures)
    require(result["selectedChildLane"] == NEXT_SLICE, "selected child lane mismatch", failures)
    require(result["selectedChildScope"] == "missionscript-slot-bitset-save-rebuild-fixture-proof-plan", "selected child scope mismatch", failures)
    require(result["selectedFixtureFamily"] == "slot-bitset-save", "selected fixture family mismatch", failures)
    require(result["selectedFixturePath"] == "slot-bitset-save-core-handler-and-career-bridge", "selected fixture path mismatch", failures)

    static = result["staticContext"]
    require(static["staticFunctionQuality"] == "6411/6411 = 100.00%", "static function quality mismatch", failures)
    require(static["staticDebt"] == "0 / 0 / 0", "static debt mismatch", failures)
    require(static["expandedStaticSurface"] == "1560/1560 = 100.00%", "expanded surface mismatch", failures)
    require(static["currentRiskFocused"] == "1179/1179 = 100.00%", "current-risk mismatch", failures)
    require(static["remainingActiveFocusedWork"] == 0, "remaining work mismatch", failures)
    require(static["latestGhidraBackupClass"] == "verified-static-backup-redacted", "backup class mismatch", failures)

    accounting = result["selectionAccounting"]
    require(accounting["candidateFamilyCount"] == 9, "candidate family count mismatch", failures)
    require(accounting["selectedCandidateRank"] == 1, "selected candidate rank mismatch", failures)
    require(accounting["selectedSourceProofCount"] == 3, "selected source proof count mismatch", failures)
    require(accounting["selectedDescriptorEntryCount"] == 3, "selected descriptor count mismatch", failures)
    require(accounting["selectedLooseCorpusRows"] == 18, "selected corpus row count mismatch", failures)
    require(accounting["selectedLevelRows"] == 6, "selected level row count mismatch", failures)
    require(accounting["falseGuardCount"] == len(FALSE_GUARDS), "false guard count mismatch", failures)
    require(accounting["zeroCounterCount"] == len(ZERO_COUNTERS), "zero counter count mismatch", failures)
    require(accounting["publicLeakCheck"] == "PASS", "public leak check mismatch", failures)

    require(rollup["rollupStatus"] == ROLLUP_STATUS, "source rollup status mismatch", failures)
    require(rollup["rollupAccounting"]["commandFamilyCount"] == 9, "source rollup family count mismatch", failures)
    require(rollup["rollupAccounting"]["descriptorRecordCount"] == 52, "source rollup descriptor count mismatch", failures)
    require(rollup["rollupAccounting"]["uniqueDescriptorTokenCount"] == 48, "source rollup unique descriptor mismatch", failures)
    require(result["sourceEvidence"]["rollup"]["rollupStatus"] == ROLLUP_STATUS, "embedded rollup status mismatch", failures)

    require(slot["status"] == "PASS", "source slot schema status mismatch", failures)
    require(slot["source"]["runtimeExecution"] is False, "slot runtime guard mismatch", failures)
    require(slot["source"]["ghidraMutation"] is False, "slot mutation guard mismatch", failures)
    require([row["index"] for row in result["selectedFixture"]["descriptorRows"]] == [122, 123, 132], "selected descriptor indices mismatch", failures)
    require(result["sourceEvidence"]["slotCommandEffect"]["descriptorEntryCount"] == 3, "embedded slot descriptor count mismatch", failures)
    require(result["sourceEvidence"]["slotCommandEffect"]["descriptorIndices"] == [122, 123, 132], "embedded slot descriptor indices mismatch", failures)
    require(result["sourceEvidence"]["slotCommandEffect"]["commandCounts"] == {"GetSlot": 6, "SetSlot": 8, "SetSlotSave": 4}, "embedded slot command counts mismatch", failures)
    require(slot["missionSlotCorpus"]["levelRows"] == 6, "source slot level rows mismatch", failures)
    require(slot["missionSlotCorpus"]["detailedCallRows"] == 18, "source slot detailed rows mismatch", failures)
    require(slot["missionSlotCorpus"]["commandCounts"] == {"GetSlot": 6, "SetSlot": 8, "SetSlotSave": 4}, "source slot command counts mismatch", failures)

    require(save["status"] == "PASS", "source save schema status mismatch", failures)
    require(save["source"]["runtimeExecution"] is False, "save runtime guard mismatch", failures)
    require(save["source"]["saveSynthesis"] is False, "save synthesis guard mismatch", failures)
    require(save["container"]["expectedSize"] == 10004, "save expected size mismatch", failures)
    require(save["container"]["versionWord"] == "0x4BD1", "save version mismatch", failures)
    require(save["container"]["trueViewRule"] == "file_offset = 0x0002 + career_offset", "save true-view rule mismatch", failures)
    require(save["preservationGuards"]["techSlotsBase"] == "0x240A", "save slot base mismatch", failures)
    require(result["sourceEvidence"]["saveBytePreservation"]["careerSlotsBase"] == "0x240A", "embedded career slot base mismatch", failures)

    seeds = result["selectedFixture"]["slotModel"]["selectedNumericSeeds"]
    require(seeds == [
        {"slot": 61, "dwordIndex": 1, "bitIndex": 29, "bitMask": "0x20000000", "trueViewOffset": "0x240E"},
        {"slot": 62, "dwordIndex": 1, "bitIndex": 30, "bitMask": "0x40000000", "trueViewOffset": "0x240E"},
    ], "selected numeric seed bitset math mismatch", failures)
    require(result["selectedFixture"]["slotModel"]["slotRange"] == "0..255", "slot range mismatch", failures)
    require(result["selectedFixture"]["slotModel"]["slotStorageDwords"] == 32, "slot storage dword count mismatch", failures)

    ranking = result["candidateRanking"]
    require(len(ranking) == 9, "candidate ranking count mismatch", failures)
    require(ranking[0]["family"] == "slot-bitset-save" and ranking[0]["decision"] == "selected", "selected ranking mismatch", failures)
    require(any(row["family"] == "message-audio-console" and row["decision"] == "deferred" for row in ranking), "missing message/audio deferral", failures)
    require(any(row["family"] == "player-state-score" and row["decision"] == "deferred" for row in ranking), "missing player-state deferral", failures)
    require(len(result["futureEvidenceRequirements"]) == 6, "future evidence requirement count mismatch", failures)

    guards = result["guardSummary"]
    for key in FALSE_GUARDS:
        require(guards["falseGuards"][key] is False, f"false guard mismatch: {key}", failures)
    for key in ZERO_COUNTERS:
        require(guards["zeroCounters"][key] == 0, f"zero counter mismatch: {key}", failures)
    require("runtime slot persistence" in result["claimBoundary"]["doesNotProve"], "claim boundary missing runtime slot persistence", failures)
    require("slot-bitset-save has the safest first-fixture evidence shape among the nine command-effect families" in result["claimBoundary"]["proves"], "claim boundary missing selected fixture proof", failures)


def check_docs(failures: list[str]) -> None:
    required_tokens = (
        THIS_SLICE,
        PREVIOUS_SLICE,
        NEXT_SLICE,
        "missionscript-command-effect-fixture-selection.v1.json",
        f"fixtureSelectionStatus={STATUS_TOKEN}",
        "selectedFixtureFamily=slot-bitset-save",
        "selectedFixturePath=slot-bitset-save-core-handler-and-career-bridge",
        "selectedCandidateRank=1",
        "candidateFamilyCount=9",
        "selectedSourceProofCount=3",
        "selectedDescriptorEntryCount=3",
        "selectedLooseCorpusRows=18",
        "selectedLevelRows=6",
        "selectedCommandCounts=GetSlot:6/SetSlot:8/SetSlotSave:4",
        "slotRange=0..255",
        "slotStorageDwords=32",
        "runtimeSlotArray=CGame+0x308",
        "careerSlotsBase=0x240A",
        "falseGuardCount=34",
        "zeroCounterCount=25",
        "publicLeakCheck=PASS",
        "latestGhidraBackupClass=verified-static-backup-redacted",
        "0x005338d0 IScript__SetSlot",
        "0x00533900 IScript__SetSlotSave",
        "0x005339a0 IScript__GetSlotBitValue",
        "0x0046d3a0 CGame__SetSlot",
        "0x0046d410 CGame__GetSlot",
        "0x004214e0 CCareer__SetSlot",
        "SetSlot(61)",
        "SetSlot(62)",
        "0x20000000",
        "0x40000000",
        "0x240E",
        "message-audio-console",
        "player-state-score",
    )
    for path in (PLAN, READINESS):
        text = read_text(path)
        for token in required_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing token: {token}", failures)
        check_no_bad_public_content(path, failures)
    check_no_bad_public_content(RESULT, failures)

    front_door_tokens = (
        THIS_SLICE,
        NEXT_SLICE,
        "missionscript-command-effect-fixture-selection.md",
        "missionscript-command-effect-fixture-selection.v1.json",
        f"fixtureSelectionStatus={STATUS_TOKEN}",
        "selectedFixtureFamily=slot-bitset-save",
        "selectedChildLane=MissionScript Slot Bitset/Save Rebuild Fixture Proof Plan",
        "selectedLooseCorpusRows=18",
        "falseGuardCount=34",
        "zeroCounterCount=25",
        "publicLeakCheck=PASS",
    )
    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX):
        text = read_text(path)
        for token in front_door_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing front-door token: {token}", failures)

    require(read_text(LORE_PLAN) == read_text(PLAN), "lore proof mirror mismatch", failures)
    require(read_json(LORE_RESULT) == read_json(RESULT), "lore schema mirror mismatch", failures)
    for source, mirror in (
        (BACKLOG, LORE_BACKLOG),
        (MAPPED, LORE_MAPPED),
        (BIN_INDEX, LORE_BIN_INDEX),
        (RE_INDEX, LORE_RE_INDEX),
    ):
        require(read_text(source) == read_text(mirror), f"lore mirror mismatch for {source.relative_to(ROOT)}", failures)

    backlog = read_text(BACKLOG)
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed fixture selection", failures)
    require(f"The selected active static-to-proof slice is {THIS_SLICE}. Status: selected" not in backlog, "backlog still marks fixture selection active", failures)
    require(f"Completed {NEXT_SLICE}" in backlog, "backlog missing completed slot fixture plan", failures)
    require(f"The selected active static-to-proof slice is {NEXT_SLICE}. Status: selected" not in backlog, "backlog still marks slot fixture plan active", failures)
    require(f"Completed {COMPLETED_DETERMINISTIC_SLICE}" in backlog, "backlog missing completed deterministic codec lane", failures)
    require(f"The selected active static-to-proof slice is {COMPLETED_DETERMINISTIC_SLICE}. Status: selected" not in backlog, "backlog still marks deterministic codec lane active", failures)
    require(f"Completed {COMPLETED_CLEAN_ROOM_SLICE.replace(' Proof Plan', ' Proof')}" in backlog, "backlog missing completed clean-room codec interface lane", failures)
    require(f"The selected active static-to-proof slice is {COMPLETED_CLEAN_ROOM_SLICE}. Status: selected" not in backlog, "backlog still marks clean-room codec interface lane active", failures)
    require(f"Completed {POST_GOODIE_SELECTION_SLICE}" in backlog, "backlog missing completed post-Goodie selection refresh lane", failures)
    require(f"Completed {CUTSCENE_FIXTURE_SLICE}" in backlog, "backlog missing completed cutscene pan-camera/position fixture lane", failures)
    require(f"The selected active static-to-proof slice is {CUTSCENE_FIXTURE_SLICE}. Status: selected" not in backlog, "backlog still marks cutscene pan-camera/position fixture lane active", failures)
    require(f"Completed {OBJECTIVE_FIXTURE_SLICE}" in backlog, "backlog missing completed objective/outcome fixture lane", failures)
    require(f"The selected active static-to-proof slice is {OBJECTIVE_FIXTURE_SLICE}. Status: selected" not in backlog, "backlog still marks objective/outcome fixture lane active", failures)
    require(f"Completed {MESSAGE_AUDIO_FIXTURE_SLICE}" in backlog, "backlog missing completed message/audio fixture lane", failures)
    require(f"The selected active static-to-proof slice is {MESSAGE_AUDIO_FIXTURE_SLICE}. Status: selected" not in backlog, "backlog still marks message/audio fixture lane active", failures)
    require(f"Completed {HUD_DISPLAY_FIXTURE_SLICE}" in backlog, "backlog missing completed HUD/display fixture lane", failures)
    require(f"The selected active static-to-proof slice is {HUD_DISPLAY_FIXTURE_SLICE}. Status: selected" not in backlog, "backlog still marks HUD/display fixture lane active", failures)
    require(
        f"Completed {ACTIVE_SLICE}" in backlog
        or f"The selected active static-to-proof slice is {ACTIVE_SLICE}. Status: selected" in backlog,
        "backlog missing active-or-completed Thing Value / Engine Helper fixture lane",
        failures,
    )
    require(
        f"The selected active static-to-proof slice is {NEXT_ACTIVE_SLICE}. Status: selected" in backlog
        or f"The selected active static-to-proof slice is {ACTIVE_SLICE}. Status: selected" in backlog
        or f"Completed {NEXT_ACTIVE_SLICE}" in backlog,
        "backlog missing active-or-completed Thing Value or Player-State / Score fixture lane",
        failures,
    )
    require(
        f"Completed {COMPLETION_ROLLUP_SLICE}" in backlog,
        "backlog missing completed fixture-family completion rollup lane",
        failures,
    )
    require(
        f"The selected active static-to-proof slice is {COMPLETION_ROLLUP_SLICE}. Status: selected" not in backlog,
        "backlog still marks fixture-family completion rollup lane active",
        failures,
    )
    require(
        f"The selected active static-to-proof slice is {POST_ROLLUP_NEXT_SLICE}. Status: selected" in backlog,
        "backlog missing active post-rollup selection refresh lane",
        failures,
    )


def check_package(failures: list[str]) -> None:
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:missionscript-command-effect-fixture-selection")
        == r"py -3 tools\missionscript_command_effect_fixture_selection_probe.py --check",
        "missing package fixture-selection test script",
        failures,
    )
    for script in (
        "test:missionscript-command-effect-rebuild-interface-rollup",
        "test:missionscript-slot-command-effect-static",
        "test:save-options-controller-byte-preservation-copied-file",
    ):
        require(script in scripts, f"missing source package script: {script}", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_result(failures)
    check_docs(failures)
    check_package(failures)
    require(no_bea_process_running(), "BEA.exe process is running after fixture selection", failures)

    if failures:
        print("MissionScript command-effect fixture-selection probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("MissionScript command-effect fixture-selection probe: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
