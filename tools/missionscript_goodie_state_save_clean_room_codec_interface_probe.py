#!/usr/bin/env python3
"""Validate MissionScript Goodie-state/save clean-room codec interface proof."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

CODEC = ROOT / "OnslaughtCareerEditor.AppCore" / "MissionScriptGoodieStateSaveCodec.cs"
CODEC_TESTS = ROOT / "OnslaughtCareerEditor.AppCore.Tests" / "MissionScriptGoodieStateSaveCodecTests.cs"
APPCORE_PATCHER = ROOT / "OnslaughtCareerEditor.AppCore" / "BesFilePatcher.cs"

PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-goodie-state-save-clean-room-codec-interface-proof.md"
RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-goodie-state-save-clean-room-codec-interface-proof.v1.json"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-goodie-state-save-clean-room-codec-interface-proof.md"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-goodie-state-save-clean-room-codec-interface-proof.v1.json"
READINESS = ROOT / "release" / "readiness" / "missionscript_goodie_state_save_clean_room_codec_interface_proof_2026-06-09.md"

COPIED_PROOF_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-goodie-state-save-copied-baseline-byte-diff-fixture-proof.v1.json"
GOODIE_PLAN_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-goodie-state-save-command-effect-fixture-proof-plan.v1.json"

BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
LORE_MAPPED = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
LORE_BIN_INDEX = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
LORE_RE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"
MISSION_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-iscript-static-contract.md"
LORE_MISSION_CONTRACT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-iscript-static-contract.md"
GOODIES_DOC = ROOT / "reverse-engineering" / "save-file" / "goodies-system.md"
LORE_GOODIES_DOC = ROOT / "lore-book" / "reverse-engineering" / "save-file" / "goodies-system.md"
SAVE_FORMAT = ROOT / "reverse-engineering" / "save-file" / "save-format.md"
LORE_SAVE_FORMAT = ROOT / "lore-book" / "reverse-engineering" / "save-file" / "save-format.md"
PACKAGE_JSON = ROOT / "package.json"

THIS_SLICE = "MissionScript Goodie State / Save Clean-Room Codec Interface Proof"
THIS_ACTIVE_SLICE = "MissionScript Goodie State / Save Clean-Room Codec Interface Proof Plan"
THIS_STATUS = "missionscript-goodie-state-save-clean-room-codec-interface-proof-complete-pure-appcore-buffer-codec-not-runtime-proof"
PREVIOUS_SLICE = "MissionScript Goodie State / Save Copied-Baseline Byte-Diff Fixture Proof"
PREVIOUS_STATUS = "missionscript-goodie-state-save-copied-baseline-byte-diff-fixture-proof-complete-copied-real-baseline-appcore-byte-diff-not-runtime-proof"
NEXT_SLICE = "MissionScript Goodie State / Save AppCore Copied-Baseline Codec Harness Proof Plan"
NEXT_ACTIVE_SLICE = "MissionScript Cutscene Pan-Camera / Position Command-Effect Deterministic Fixture Proof Plan"
COMPLETED_GOODIE_BOUNDARY_SLICE = "MissionScript Goodie State / Save AppCore Copied-Baseline Boundary Corpus Harness Proof"
POST_GOODIE_SELECTION_SLICE = "MissionScript Command-Effect Post-Goodie Selection Refresh Proof Plan"
FIXTURE_FAMILY = "goodie-state-save"
FIXTURE_PATH = "goodie-state-save-index-state-byte-preservation"

EXPECTED_VECTORS = [
    (1, 0, "0x1F46", True, False),
    (51, 50, "0x200E", True, False),
    (53, 52, "0x2016", True, False),
    (68, 67, "0x2052", True, False),
    (71, 70, "0x205E", True, False),
    (233, 232, "0x22E6", True, False),
    (234, 233, "0x22EA", False, True),
    (300, 299, "0x23F2", False, True),
]

PUBLIC_FORBIDDEN_PATTERNS = (
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
)

FORBIDDEN_OVERCLAIMS = (
    "runtime missionscript execution proven",
    "runtime command effects proven",
    "runtime goodie state mutation proven",
    "runtime save/load behavior proven",
    "runtime defaultoptions behavior proven",
    "runtime goodies wall behavior proven",
    "runtime score behavior proven",
    "installed game mutation proven",
    "product ui behavior proven",
    "visual qa complete",
    "ghidra mutation complete",
    "executable patching behavior proven",
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
    for pattern, category in PUBLIC_FORBIDDEN_PATTERNS:
        require(pattern.search(text) is None, f"{path.relative_to(ROOT)} leaks forbidden public category: {category}", failures)
    for phrase in FORBIDDEN_OVERCLAIMS:
        require(phrase not in lower, f"{path.relative_to(ROOT)} overclaims forbidden category: {phrase}", failures)


def check_source_prerequisites(failures: list[str]) -> None:
    copied = read_json(COPIED_PROOF_SCHEMA)
    goodie_plan = read_json(GOODIE_PLAN_SCHEMA)
    require(copied["missionScriptGoodieStateSaveCopiedBaselineByteDiffFixtureProofStatus"] == PREVIOUS_STATUS, "copied baseline prerequisite status mismatch", failures)
    require(copied["selectedNextSlice"] == THIS_ACTIVE_SLICE, "copied baseline prerequisite next-slice mismatch", failures)
    require(copied["selectedFixtureFamily"] == FIXTURE_FAMILY, "copied baseline fixture family mismatch", failures)
    require(copied["selectedFixturePath"] == FIXTURE_PATH, "copied baseline fixture path mismatch", failures)
    require(copied["container"]["expectedSize"] == 10004, "copied baseline size mismatch", failures)
    require(copied["container"]["versionWord"] == "0x4BD1", "copied baseline version mismatch", failures)
    require(copied["container"]["trueViewGoodieBase"] == "0x1F46", "copied baseline Goodie base mismatch", failures)
    require(copied["implementation"]["appCorePatcherUsed"] is True, "copied baseline AppCore patcher guard mismatch", failures)
    require(copied["negativeGuards"]["runtimeExecution"] is False, "copied baseline runtime guard mismatch", failures)
    require(copied["negativeGuards"]["godotWork"] is False, "copied baseline Godot guard mismatch", failures)
    require(goodie_plan["selectedFixtureFamily"] == FIXTURE_FAMILY, "Goodie plan fixture family mismatch", failures)
    require(goodie_plan["fixtureAccounting"]["displayableGoodieCount"] == 233, "Goodie plan displayable count mismatch", failures)


def check_appcore_code(failures: list[str]) -> None:
    codec = read_text(CODEC)
    tests = read_text(CODEC_TESTS)
    patcher = read_text(APPCORE_PATCHER)

    codec_tokens = (
        "public enum MissionScriptGoodieState : uint",
        "Unknown = 0",
        "Instructions = 1",
        "New = 2",
        "Old = 3",
        "MissionScriptGoodieStateVector",
        "public const int ExpectedFileSize = 10004",
        "public const ushort VersionWord = 0x4BD1",
        "public const int GoodieBaseOffset = 0x1F46",
        "public const int GoodieStorageEntryCount = 300",
        "public const int DisplayableGoodieCount = 233",
        "public const int ReservedPreserveEntryCount = GoodieStorageEntryCount - DisplayableGoodieCount",
        "public const int GoodieStorageBytes = GoodieStorageEntryCount * 4",
        "public const int GoodieStorageEndExclusive = GoodieBaseOffset + GoodieStorageBytes",
        "public const uint MaxKnownStateValue = (uint)MissionScriptGoodieState.Old",
        "BinaryPrimitives.ReadUInt16LittleEndian(buffer.Slice(0, 2)) == VersionWord",
        "return GetVectorFromSaveIndex(scriptIndex - 1)",
        "int offset = GoodieBaseOffset + (saveGoodieIndex * 4)",
        "bool isDisplayable = saveGoodieIndex < DisplayableGoodieCount",
        "GetDisplayableVectorFromScriptIndex",
        "SetDisplayableStatesByScriptIndex",
        "MissionScriptGoodieStateVector[] vectors",
        "ValidateState(state)",
        "BinaryPrimitives.WriteUInt32LittleEndian(buffer.Slice(vector.TrueViewDwordOffset, 4), (uint)state)",
        "MissionScriptGoodieState.Unknown => \"Locked\"",
    )
    for token in codec_tokens:
        require(token in codec, f"codec source missing token: {token}", failures)

    forbidden_source_tokens = (
        "File.",
        "Directory.",
        "Process.",
        "Ghidra",
        "Godot",
        "BEA.exe",
        "Program Files",
        "steamapps",
    )
    for token in forbidden_source_tokens:
        require(token not in codec, f"codec source contains forbidden token: {token}", failures)

    test_tokens = (
        "GetVectorFromScriptIndex_MatchesStaticGoodieOffsetProof",
        "[InlineData(1, 0, 0x1F46, true, false)]",
        "[InlineData(51, 50, 0x200E, true, false)]",
        "[InlineData(53, 52, 0x2016, true, false)]",
        "[InlineData(68, 67, 0x2052, true, false)]",
        "[InlineData(71, 70, 0x205E, true, false)]",
        "[InlineData(233, 232, 0x22E6, true, false)]",
        "[InlineData(234, 233, 0x22EA, false, true)]",
        "[InlineData(300, 299, 0x23F2, false, true)]",
        "SetDisplayableStatesByScriptIndex_MatchesCopiedBaselineChangedOffsets",
        "0x1F46, 0x200E, 0x2016, 0x2052, 0x205E, 0x22E6",
        "SetDisplayableStatesByScriptIndex_InvalidMixedBatchLeavesBufferUnchanged",
        "SetDisplayableState_ForEveryDisplayableScriptIndex_TouchesOnlyExpectedDwordStartAndRoundtrips",
        "AllDisplayableScriptIndices",
        "scriptIndex <= MissionScriptGoodieStateSaveCodec.DisplayableGoodieCount",
        "CreateCodecBuffer",
        "MissionScriptGoodieStateSaveCodec.ExpectedFileSize",
        "MissionScriptGoodieStateSaveCodec.VersionWord",
    )
    for token in test_tokens:
        require(token in tests, f"codec tests missing token: {token}", failures)

    require("PatchGoodieStates" in patcher, "AppCore patcher prerequisite missing PatchGoodieStates", failures)


def check_schema(failures: list[str]) -> None:
    result = read_json(RESULT)
    lore = read_json(LORE_RESULT)
    require(lore == result, "lore schema mirror mismatch", failures)
    require(result["schemaVersion"] == "missionscript-goodie-state-save-clean-room-codec-interface-proof.v1", "schema version mismatch", failures)
    require(result["status"] == "PASS", "schema status mismatch", failures)
    require(result["missionScriptGoodieStateSaveCleanRoomCodecInterfaceProofStatus"] == THIS_STATUS, "schema status token mismatch", failures)
    require(result["previousSlice"] == PREVIOUS_SLICE, "schema previous slice mismatch", failures)
    require(result["selectedNextSlice"] == NEXT_SLICE, "schema selected next slice mismatch", failures)
    require(result["selectedFixtureFamily"] == FIXTURE_FAMILY, "schema fixture family mismatch", failures)
    require(result["selectedFixturePath"] == FIXTURE_PATH, "schema fixture path mismatch", failures)

    implementation = result["implementation"]
    require(implementation["appCoreCodecPath"] == "OnslaughtCareerEditor.AppCore/MissionScriptGoodieStateSaveCodec.cs", "codec path mismatch", failures)
    require(implementation["appCoreTestPath"] == "OnslaughtCareerEditor.AppCore.Tests/MissionScriptGoodieStateSaveCodecTests.cs", "test path mismatch", failures)
    require(implementation["interfaceKind"] == "pure AppCore in-memory buffer codec", "interface kind mismatch", failures)
    require(implementation["publicMethodCount"] == 10, "public method count mismatch", failures)
    for key in ("appCoreCodecUsed",):
        require(implementation[key] is True, f"implementation guard mismatch: {key}", failures)
    for key in ("appCorePatcherUsed", "fileIoPerformed", "harnessFileIo", "copiedFileMutationPerformed", "sourceBaselineRead", "privateArtifactMaterialized"):
        require(implementation[key] is False, f"implementation guard mismatch: {key}", failures)

    container = result["container"]
    require(container["expectedFileSize"] == 10004, "container expected size mismatch", failures)
    require(container["versionWord"] == "0x4BD1", "container version mismatch", failures)
    require(container["trueViewGoodieBase"] == "0x1F46", "container Goodie base mismatch", failures)
    require(container["goodieStorageEntryCount"] == 300, "container storage count mismatch", failures)
    require(container["displayableGoodieCount"] == 233, "container displayable count mismatch", failures)
    require(container["reservedPreserveEntryCount"] == 67, "container reserved count mismatch", failures)
    require(container["goodieStorageBytes"] == 1200, "container storage byte count mismatch", failures)
    require(container["goodieStorageEndExclusive"] == "0x23F6", "container end mismatch", failures)

    mapping = result["indexMapping"]
    require(mapping["scriptIndexing"] == "1-based", "script indexing mismatch", failures)
    require(mapping["mappingFormula"] == "save_goodie_index = script_index - 1", "mapping formula mismatch", failures)
    require(mapping["offsetFormula"] == "0x1F46 + (script_index - 1) * 4", "offset formula mismatch", failures)
    require(mapping["scriptIndexRange"] == "1..300", "script range mismatch", failures)
    require(mapping["displayableScriptIndexRange"] == "1..233", "displayable script range mismatch", failures)
    require(mapping["reservedWritePolicy"] == "displayable-only-default-rejects-reserved", "reserved policy mismatch", failures)
    require(mapping["stateValueRange"] == "0..3", "state range mismatch", failures)
    vectors = mapping["vectors"]
    require(len(vectors) == len(EXPECTED_VECTORS), "vector count mismatch", failures)
    for row, expected in zip(vectors, EXPECTED_VECTORS):
        script_index, save_index, offset, displayable, reserved = expected
        require(row["scriptIndex"] == script_index, f"script index mismatch: {script_index}", failures)
        require(row["saveGoodieIndex"] == save_index, f"save index mismatch: {script_index}", failures)
        require(row["trueViewDwordOffset"] == offset, f"offset mismatch: {script_index}", failures)
        require(row["displayable"] is displayable, f"displayable mismatch: {script_index}", failures)
        require(row["reservedPreserve"] is reserved, f"reserved mismatch: {script_index}", failures)

    validation = result["validation"]
    require(validation["dotnetFilter"] == "MissionScriptGoodieStateSaveCodecTests", "dotnet filter mismatch", failures)
    require(validation["xunitTestCaseCount"] == 249, "xUnit count mismatch", failures)
    require(validation["testMethodCount"] == 7, "test method count mismatch", failures)
    require(validation["allDisplayableScriptIndexCaseCount"] == 233, "displayable test count mismatch", failures)
    require(validation["changedOffsets"] == ["0x1F46", "0x200E", "0x2016", "0x2052", "0x205E", "0x22E6"], "changed offsets mismatch", failures)
    for key in (
        "invalidMixedBatchLeavesBufferUnchanged",
        "allDisplayableScriptIndicesRoundTrip",
        "allDisplayableScriptIndicesTouchOnlyExpectedDwordStart",
        "reservedIndexRejection",
        "invalidStateRejection",
        "wrongSizeRejected",
        "wrongVersionRejected",
        "emptyBatchRejected",
    ):
        require(validation[key] is True, f"validation guard mismatch: {key}", failures)
    require(validation["publicLeakCheck"] == "PASS", "public leak check mismatch", failures)

    guards = result["negativeGuards"]
    for key in (
        "syntheticBesFileWritten",
        "defaultoptionsGoodieMutation",
        "runtimeExecution",
        "beLaunch",
        "runtimeMissionScriptExecutionProven",
        "runtimeCommandEffectsProven",
        "runtimeGoodieStateMutationProven",
        "runtimeSaveBehaviorProven",
        "runtimeDefaultOptionsBehaviorProven",
        "runtimeGoodiesWallBehaviorProven",
        "runtimeScoreBehaviorProven",
        "ghidraMutation",
        "executablePatching",
        "godotWork",
        "productUiWired",
        "rebuildImplementation",
        "rebuildParityProven",
        "noNoticeableDifferenceParityProven",
    ):
        require(guards[key] is False, f"negative guard mismatch: {key}", failures)
    check_no_bad_public_content(RESULT, failures)


def check_docs(failures: list[str]) -> None:
    required_tokens = (
        THIS_SLICE,
        THIS_STATUS,
        PREVIOUS_SLICE,
        NEXT_SLICE,
        "missionscript-goodie-state-save-clean-room-codec-interface-proof.v1.json",
        "interfaceKind=pure AppCore in-memory buffer codec",
        "appCoreCodecPath=OnslaughtCareerEditor.AppCore/MissionScriptGoodieStateSaveCodec.cs",
        "appCoreTestPath=OnslaughtCareerEditor.AppCore.Tests/MissionScriptGoodieStateSaveCodecTests.cs",
        "appCoreCodecUsed=true",
        "appCorePatcherUsed=false",
        "publicMethodCount=10",
        "expectedFileSize=10004",
        "versionWord=0x4BD1",
        "trueViewGoodieBase=0x1F46",
        "goodieStorageEntryCount=300",
        "displayableGoodieCount=233",
        "reservedPreserveEntryCount=67",
        "goodieStorageBytes=1200",
        "goodieStorageEndExclusive=0x23F6",
        "scriptIndexing=1-based",
        "mappingFormula=save_goodie_index = script_index - 1",
        "offsetFormula=0x1F46 + (script_index - 1) * 4",
        "scriptIndexRange=1..300",
        "displayableScriptIndexRange=1..233",
        "saveGoodieIndexRange=0..299",
        "displayableSaveGoodieIndexRange=0..232",
        "reservedScriptIndexRange=234..300",
        "reservedWritePolicy=displayable-only-default-rejects-reserved",
        "stateValueRange=0..3",
        "dotnetFilter=MissionScriptGoodieStateSaveCodecTests",
        "xunitTestCaseCount=249",
        "testMethodCount=7",
        "allDisplayableScriptIndexCaseCount=233",
        "changedOffsets=0x1F46,0x200E,0x2016,0x2052,0x205E,0x22E6",
        "invalidMixedBatchLeavesBufferUnchanged=true",
        "allDisplayableScriptIndicesRoundTrip=true",
        "allDisplayableScriptIndicesTouchOnlyExpectedDwordStart=true",
        "reservedIndexRejection=true",
        "invalidStateRejection=true",
        "wrongSizeRejected=true",
        "wrongVersionRejected=true",
        "emptyBatchRejected=true",
        "fileIoPerformed=false",
        "harnessFileIo=false",
        "copiedFileMutationPerformed=false",
        "sourceBaselineRead=false",
        "privateArtifactMaterialized=false",
        "syntheticBesFileWritten=false",
        "defaultoptionsGoodieMutation=false",
        "runtimeExecution=false",
        "beLaunch=false",
        "ghidraMutation=false",
        "executablePatching=false",
        "godotWork=false",
        "productUiWired=false",
        "rebuildImplementation=false",
        "publicLeakCheck=PASS",
    )
    for path in (PROOF, READINESS):
        text = read_text(path)
        for token in required_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing token: {token}", failures)
        check_no_bad_public_content(path, failures)
    require(read_text(LORE_PROOF) == read_text(PROOF), "lore proof mirror mismatch", failures)

    front_door_tokens = (
        THIS_SLICE,
        THIS_STATUS,
        "missionscript-goodie-state-save-clean-room-codec-interface-proof.md",
        "missionscript-goodie-state-save-clean-room-codec-interface-proof.v1.json",
        "appCoreCodecPath=OnslaughtCareerEditor.AppCore/MissionScriptGoodieStateSaveCodec.cs",
        "appCoreTestPath=OnslaughtCareerEditor.AppCore.Tests/MissionScriptGoodieStateSaveCodecTests.cs",
        "interfaceKind=pure AppCore in-memory buffer codec",
        "appCoreCodecUsed=true",
        "appCorePatcherUsed=false",
        "scriptIndexing=1-based",
        "mappingFormula=save_goodie_index = script_index - 1",
        "offsetFormula=0x1F46 + (script_index - 1) * 4",
        "reservedWritePolicy=displayable-only-default-rejects-reserved",
        "xunitTestCaseCount=249",
        "testMethodCount=7",
        "allDisplayableScriptIndexCaseCount=233",
        "invalidMixedBatchLeavesBufferUnchanged=true",
        "fileIoPerformed=false",
        "copiedFileMutationPerformed=false",
        "sourceBaselineRead=false",
        "privateArtifactMaterialized=false",
        f"selectedNextSlice={NEXT_SLICE}",
    )
    front_docs = (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX, MISSION_CONTRACT, GOODIES_DOC, SAVE_FORMAT)
    for path in front_docs:
        text = read_text(path)
        for token in front_door_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing front-door token: {token}", failures)
        require(
            f"The selected active static-to-proof slice is {THIS_ACTIVE_SLICE}. Status: selected" not in text,
            f"{path.relative_to(ROOT)} still marks clean-room codec as active",
            failures,
        )
    require(
        f"Completed {COMPLETED_GOODIE_BOUNDARY_SLICE}" in read_text(BACKLOG),
        "backlog missing completed Goodie boundary corpus harness lane",
        failures,
    )
    require(
        f"Completed {POST_GOODIE_SELECTION_SLICE}" in read_text(BACKLOG),
        "backlog missing completed post-Goodie selection refresh lane",
        failures,
    )
    require(
        f"The selected active static-to-proof slice is {NEXT_ACTIVE_SLICE}. Status: selected" in read_text(BACKLOG),
        "backlog missing active cutscene pan-camera/position fixture lane",
        failures,
    )

    for source, mirror in (
        (BACKLOG, LORE_BACKLOG),
        (MAPPED, LORE_MAPPED),
        (BIN_INDEX, LORE_BIN_INDEX),
        (RE_INDEX, LORE_RE_INDEX),
        (MISSION_CONTRACT, LORE_MISSION_CONTRACT),
        (GOODIES_DOC, LORE_GOODIES_DOC),
        (SAVE_FORMAT, LORE_SAVE_FORMAT),
    ):
        require(read_text(source) == read_text(mirror), f"lore mirror mismatch for {source.relative_to(ROOT)}", failures)


def check_package(failures: list[str]) -> None:
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:missionscript-goodie-state-save-clean-room-codec-interface")
        == r"py -3 tools\missionscript_goodie_state_save_clean_room_codec_interface_probe.py --check",
        "missing package clean-room codec interface test script",
        failures,
    )
    for script in (
        "test:missionscript-goodie-state-save-copied-baseline-byte-diff-fixture-proof",
        "test:missionscript-goodie-state-save-command-effect-fixture-proof-plan",
        "test:static-to-proof-transition-backlog",
    ):
        require(script in scripts, f"missing source package script: {script}", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_source_prerequisites(failures)
    check_appcore_code(failures)
    check_schema(failures)
    check_docs(failures)
    check_package(failures)
    require(no_bea_process_running(), "BEA.exe process is running after clean-room codec proof", failures)

    if failures:
        print("MissionScript Goodie-state/save clean-room codec interface proof probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("MissionScript Goodie-state/save clean-room codec interface proof probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
