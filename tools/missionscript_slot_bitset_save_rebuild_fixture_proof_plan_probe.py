#!/usr/bin/env python3
"""Validate the MissionScript slot bitset/save rebuild-fixture proof plan."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-slot-bitset-save-rebuild-fixture-proof-plan.md"
RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-slot-bitset-save-rebuild-fixture-proof-plan.v1.json"
LORE_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-slot-bitset-save-rebuild-fixture-proof-plan.md"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-slot-bitset-save-rebuild-fixture-proof-plan.v1.json"
READINESS = ROOT / "release" / "readiness" / "missionscript_slot_bitset_save_rebuild_fixture_proof_plan_2026-06-09.md"

FIXTURE_SELECTION = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-command-effect-fixture-selection.v1.json"
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

THIS_SLICE = "MissionScript Slot Bitset/Save Rebuild Fixture Proof Plan"
PREVIOUS_SLICE = "MissionScript Command-Effect Rebuild Fixture Selection Proof Plan"
NEXT_SLICE = "MissionScript Slot Bitset/Save Deterministic Codec Proof Plan"
COMPLETED_CLEAN_ROOM_SLICE = "MissionScript Slot Bitset/Save Clean-Room Codec Interface Proof Plan"
ACTIVE_SLICE = "Save / Options Byte-Preservation AppCore Implementation Contract Proof Plan"
COMPLETION_ROLLUP_SLICE = "MissionScript Command-Effect Fixture Family Completion Rollup Proof Plan"
POST_ROLLUP_NEXT_SLICE = "Static-To-Proof Rebuild Transition Post-Command-Effect Fixture Next Safe Slice Selection Refresh Proof Plan"
STATUS_TOKEN = "missionscript-slot-bitset-save-rebuild-fixture-proof-plan-complete-deterministic-codec-selected"

FALSE_GUARDS = (
    "programFilesInputUsed",
    "installedGameMutation",
    "originalExecutableMutation",
    "copiedFileMutation",
    "saveSynthesis",
    "liveLooseMslLoading",
    "packedResourceScriptSelectionProven",
    "runtimeExecution",
    "runtimeMissionScriptExecutionProven",
    "runtimeCommandEffectsProven",
    "runtimeSlotPersistenceProven",
    "runtimeSaveBehaviorProven",
    "runtimeSaveLoadBehaviorProven",
    "runtimeDefaultoptionsBehaviorProven",
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
    "runtimeMenuBehaviorProven",
    "runtimeControllerBehaviorProven",
    "rebuildParityProven",
    "noNoticeableDifferenceParityProven",
)

ZERO_COUNTERS = (
    "runtimeObservationRows",
    "missionScriptRuntimeEvidenceRows",
    "runtimeCommandEffectRows",
    "runtimeSlotEvidenceRows",
    "runtimeSaveRows",
    "copiedFileMutationRows",
    "copiedFileDiffRows",
    "saveCodecWriteRows",
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
    "godotProjectRows",
    "beProcessesAfterPlan",
    "publicAbsolutePathLeakCount",
    "publicSha256ValueLeakCount",
    "publicWindowIdentifierLeakCount",
    "publicProcessIdentifierLeakCount",
    "privatePathLeakCount",
    "rawArtifactLeakCount",
    "rawDialogueLeakCount",
)

EXPECTED_VECTORS = [
    {"slot": 0, "sourceClass": "derived-boundary-vector", "dwordIndex": 0, "bitIndex": 0, "bitMask": "0x00000001", "trueViewOffset": "0x240A"},
    {"slot": 31, "sourceClass": "derived-boundary-vector", "dwordIndex": 0, "bitIndex": 31, "bitMask": "0x80000000", "trueViewOffset": "0x240A"},
    {"slot": 32, "sourceClass": "derived-boundary-vector", "dwordIndex": 1, "bitIndex": 0, "bitMask": "0x00000001", "trueViewOffset": "0x240E"},
    {"slot": 61, "sourceClass": "public-loose-msl-SetSlot-seed", "dwordIndex": 1, "bitIndex": 29, "bitMask": "0x20000000", "trueViewOffset": "0x240E"},
    {"slot": 62, "sourceClass": "public-loose-msl-SetSlot-seed", "dwordIndex": 1, "bitIndex": 30, "bitMask": "0x40000000", "trueViewOffset": "0x240E"},
]

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
)

FORBIDDEN_OVERCLAIMS = (
    "runtime missionscript execution proven",
    "runtime command effects proven",
    "runtime slot persistence proven",
    "runtime save behavior proven",
    "runtime save/load behavior proven",
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
    "copied-file mutation complete",
    "save synthesis complete",
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
    fixture = read_json(FIXTURE_SELECTION)
    slot = read_json(SLOT_SCHEMA)
    save = read_json(SAVE_SCHEMA)

    require(result["schemaVersion"] == "missionscript-slot-bitset-save-rebuild-fixture-proof-plan.v1", "schema version mismatch", failures)
    require(result["status"] == "PASS", "status mismatch", failures)
    require(result["slotBitsetSaveFixturePlanStatus"] == STATUS_TOKEN, "fixture plan status mismatch", failures)
    require(result["previousSlice"] == PREVIOUS_SLICE, "previous slice mismatch", failures)
    require(result["selectedNextSlice"] == NEXT_SLICE, "selected next slice mismatch", failures)
    require(result["selectedFixtureFamily"] == "slot-bitset-save", "selected fixture family mismatch", failures)
    require(result["selectedFixturePath"] == "slot-bitset-save-core-handler-and-career-bridge", "selected fixture path mismatch", failures)

    static = result["staticContext"]
    require(static["staticFunctionQuality"] == "6411/6411 = 100.00%", "static function quality mismatch", failures)
    require(static["staticDebt"] == "0 / 0 / 0", "static debt mismatch", failures)
    require(static["expandedStaticSurface"] == "1560/1560 = 100.00%", "expanded surface mismatch", failures)
    require(static["currentRiskFocused"] == "1179/1179 = 100.00%", "current-risk mismatch", failures)
    require(static["remainingActiveFocusedWork"] == 0, "remaining work mismatch", failures)
    require(static["latestGhidraBackupClass"] == "verified-static-backup-redacted", "backup class mismatch", failures)

    accounting = result["planAccounting"]
    require(accounting["sourceProofCount"] == 4, "source proof count mismatch", failures)
    require(accounting["descriptorEntryCount"] == 3, "descriptor count mismatch", failures)
    require(accounting["handlerAnchorCount"] == 3, "handler anchor count mismatch", failures)
    require(accounting["helperAnchorCount"] == 3, "helper anchor count mismatch", failures)
    require(accounting["deterministicBitsetVectorCount"] == len(EXPECTED_VECTORS), "vector count mismatch", failures)
    require(accounting["publicCorpusNumericSeedCount"] == 2, "numeric seed count mismatch", failures)
    require(accounting["selectedLooseCorpusRows"] == 18, "corpus row count mismatch", failures)
    require(accounting["selectedLevelRows"] == 6, "level row count mismatch", failures)
    require(accounting["baseFalseGuardCount"] == 34, "base false guard count mismatch", failures)
    require(accounting["addedFixtureFalseGuardCount"] == 6, "added false guard count mismatch", failures)
    require(accounting["falseGuardCount"] == len(FALSE_GUARDS), "false guard count mismatch", failures)
    require(accounting["baseZeroCounterCount"] == 25, "base zero counter count mismatch", failures)
    require(accounting["addedFixtureZeroCounterCount"] == 4, "added zero counter count mismatch", failures)
    require(accounting["zeroCounterCount"] == len(ZERO_COUNTERS), "zero counter count mismatch", failures)
    require(accounting["publicLeakCheck"] == "PASS", "public leak check mismatch", failures)

    require(fixture["fixtureSelectionStatus"] == "missionscript-command-effect-fixture-selection-complete-slot-bitset-save-selected", "fixture selection prerequisite mismatch", failures)
    require(fixture["selectedChildLane"] == THIS_SLICE, "fixture selection child-lane mismatch", failures)
    require(slot["status"] == "PASS", "slot schema prerequisite mismatch", failures)
    require(slot["missionSlotCorpus"]["commandCounts"] == {"GetSlot": 6, "SetSlot": 8, "SetSlotSave": 4}, "slot source command counts mismatch", failures)
    require(save["status"] == "PASS", "save schema prerequisite mismatch", failures)
    require(save["container"]["expectedSize"] == 10004, "save size mismatch", failures)
    require(save["container"]["versionWord"] == "0x4BD1", "save version mismatch", failures)
    require(save["container"]["trueViewRule"] == "file_offset = 0x0002 + career_offset", "save true-view rule mismatch", failures)

    rows = result["fixtureModel"]["descriptorRows"]
    table = result["fixtureModel"]["descriptorTable"]
    require(table["initFunction"] == "0x0052ff30 ScriptCommandRegistry__InitBuiltins", "descriptor table init mismatch", failures)
    require(table["tableBase"] == "0x0064ce50", "descriptor table base mismatch", failures)
    require(table["strideBytes"] == 64, "descriptor stride mismatch", failures)
    require(table["declaredSlots"] == 144, "descriptor declared slot count mismatch", failures)
    require([row["index"] for row in rows] == [122, 123, 132], "descriptor index list mismatch", failures)
    require([row["recordAddress"] for row in rows] == ["0x0064ecd0", "0x0064ed10", "0x0064ef50"], "descriptor address list mismatch", failures)
    model = result["fixtureModel"]["slotModel"]
    require(model["slotRange"] == "0..255", "slot range mismatch", failures)
    require(model["slotStorageDwords"] == 32, "slot dword count mismatch", failures)
    require(model["slotStorageBytes"] == 128, "slot byte count mismatch", failures)
    require(model["runtimeSlotArray"] == "CGame+0x308", "runtime slot array mismatch", failures)
    require(model["careerSlotsBase"] == "0x240A", "career slot base mismatch", failures)
    require(model["trueViewOffsetExpression"] == "0x240A + (4 * (slot >> 5))", "true-view expression mismatch", failures)
    require(result["fixtureModel"]["deterministicBitsetVectors"] == EXPECTED_VECTORS, "deterministic vector mismatch", failures)
    require(len(result["childLanePlan"]) == 7, "child lane plan row count mismatch", failures)

    copied = result["deferredCopiedFileWriteGuards"]
    require(copied["allowedDwordRange"] == "0x240E-0x2411", "deferred copied-file allowed range mismatch", failures)
    require(copied["comparisonMode"] == "little-endian dword XOR mask subset, not single-byte expectation", "deferred copied-file comparison mode mismatch", failures)
    require(copied["slot61Mask"] == "0x20000000", "deferred slot 61 mask mismatch", failures)
    require(copied["slot62Mask"] == "0x40000000", "deferred slot 62 mask mismatch", failures)
    require(copied["unexpectedDiffCount"] == 0, "deferred unexpected diff count mismatch", failures)
    require(copied["legacyTrapHitCount"] == 0, "deferred legacy trap count mismatch", failures)
    require(copied["fileSizePreserved"] is True, "deferred file-size guard mismatch", failures)
    require(copied["versionWordPreserved"] is True, "deferred version guard mismatch", failures)

    guards = result["guardSummary"]
    for key in FALSE_GUARDS:
        require(guards["falseGuards"][key] is False, f"false guard mismatch: {key}", failures)
    for key in ZERO_COUNTERS:
        require(guards["zeroCounters"][key] == 0, f"zero counter mismatch: {key}", failures)
    require("copied-file mutation" in result["claimBoundary"]["doesNotProve"], "claim boundary missing copied-file mutation deferral", failures)
    require("the next child lane can begin with pure bitset and true-view offset math before copied-file mutation or runtime proof" in result["claimBoundary"]["proves"], "claim boundary missing next child proof", failures)


def check_docs(failures: list[str]) -> None:
    required_tokens = (
        THIS_SLICE,
        PREVIOUS_SLICE,
        NEXT_SLICE,
        "missionscript-slot-bitset-save-rebuild-fixture-proof-plan.v1.json",
        f"slotBitsetSaveFixturePlanStatus={STATUS_TOKEN}",
        "selectedFixtureFamily=slot-bitset-save",
        "selectedFixturePath=slot-bitset-save-core-handler-and-career-bridge",
        "selectedNextSlice=MissionScript Slot Bitset/Save Deterministic Codec Proof Plan",
        "sourceProofCount=4",
        "descriptorEntryCount=3",
        "handlerAnchorCount=3",
        "helperAnchorCount=3",
        "deterministicBitsetVectorCount=5",
        "publicCorpusNumericSeedCount=2",
        "selectedLooseCorpusRows=18",
        "selectedLevelRows=6",
        "selectedCommandCounts=GetSlot:6/SetSlot:8/SetSlotSave:4",
        "descriptorTableInit=0x0052ff30 ScriptCommandRegistry__InitBuiltins",
        "descriptorTableBase=0x0064ce50",
        "descriptorStrideBytes=64",
        "descriptorDeclaredSlots=144",
        "slotRange=0..255",
        "slotStorageDwords=32",
        "slotStorageBytes=128",
        "runtimeSlotArray=CGame+0x308",
        "careerSlotsBase=0x240A",
        "baseFalseGuardCount=34",
        "addedFixtureFalseGuardCount=6",
        "falseGuardCount=40",
        "baseZeroCounterCount=25",
        "addedFixtureZeroCounterCount=4",
        "zeroCounterCount=29",
        "publicLeakCheck=PASS",
        "latestGhidraBackupClass=verified-static-backup-redacted",
        "0x0064ecd0",
        "0x0064ed10",
        "0x0064ef50",
        "0x0052ff30 ScriptCommandRegistry__InitBuiltins",
        "0x0064ce50",
        "0x005338d0 IScript__SetSlot",
        "0x00533900 IScript__SetSlotSave",
        "0x005339a0 IScript__GetSlotBitValue",
        "0x0046d3a0 CGame__SetSlot",
        "0x0046d410 CGame__GetSlot",
        "0x004214e0 CCareer__SetSlot",
        "0x00000001",
        "0x80000000",
        "0x20000000",
        "0x40000000",
        "0x240A",
        "0x240E",
        "0x240E-0x2411",
        "little-endian dword",
        "unexpectedDiffCount=0",
        "legacyTrapHitCount=0",
        "copiedFileMutation=false",
        "saveSynthesis=false",
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
        "missionscript-slot-bitset-save-rebuild-fixture-proof-plan.md",
        "missionscript-slot-bitset-save-rebuild-fixture-proof-plan.v1.json",
        f"slotBitsetSaveFixturePlanStatus={STATUS_TOKEN}",
        "selectedFixtureFamily=slot-bitset-save",
        "selectedNextSlice=MissionScript Slot Bitset/Save Deterministic Codec Proof Plan",
        "deterministicBitsetVectorCount=5",
        "falseGuardCount=40",
        "zeroCounterCount=29",
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
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed slot fixture plan", failures)
    require(f"The selected active static-to-proof slice is {THIS_SLICE}. Status: selected" not in backlog, "backlog still marks slot fixture plan active", failures)
    require(f"Completed {NEXT_SLICE}" in backlog, "backlog missing completed deterministic codec lane", failures)
    require(f"The selected active static-to-proof slice is {NEXT_SLICE}. Status: selected" not in backlog, "backlog still marks deterministic codec lane active", failures)
    require(f"Completed {COMPLETED_CLEAN_ROOM_SLICE.replace(' Proof Plan', ' Proof')}" in backlog, "backlog missing completed clean-room codec interface lane", failures)
    require(f"The selected active static-to-proof slice is {COMPLETED_CLEAN_ROOM_SLICE}. Status: selected" not in backlog, "backlog still marks clean-room codec interface lane active", failures)
    require(f"Completed {COMPLETION_ROLLUP_SLICE}" in backlog, "backlog missing completed fixture-family completion rollup lane", failures)
    require(f"The selected active static-to-proof slice is {COMPLETION_ROLLUP_SLICE}. Status: selected" not in backlog, "backlog still marks fixture-family completion rollup lane active", failures)
    require(f"The selected active static-to-proof slice is {POST_ROLLUP_NEXT_SLICE}. Status: selected" in backlog, "backlog missing active post-rollup selection refresh lane", failures)


def check_package(failures: list[str]) -> None:
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:missionscript-slot-bitset-save-rebuild-fixture-proof-plan")
        == r"py -3 tools\missionscript_slot_bitset_save_rebuild_fixture_proof_plan_probe.py --check",
        "missing package slot bitset/save fixture-plan test script",
        failures,
    )
    for script in (
        "test:missionscript-command-effect-fixture-selection",
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
    require(no_bea_process_running(), "BEA.exe process is running after slot fixture plan", failures)

    if failures:
        print("MissionScript slot bitset/save rebuild fixture proof-plan probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
        print("MissionScript slot bitset/save rebuild fixture proof-plan probe: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
