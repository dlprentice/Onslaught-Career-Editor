#!/usr/bin/env python3
"""Validate MissionScript Goodie state/save AppCore boundary-corpus fixture matrix proof."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

CODEC = ROOT / "OnslaughtCareerEditor.AppCore" / "MissionScriptGoodieStateSaveCodec.cs"
TESTS = ROOT / "OnslaughtCareerEditor.AppCore.Tests" / "MissionScriptGoodieStateSaveCodecTests.cs"
PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-goodie-state-save-appcore-boundary-corpus-fixture-matrix-proof.md"
SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-goodie-state-save-appcore-boundary-corpus-fixture-matrix.v1.json"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-goodie-state-save-appcore-boundary-corpus-fixture-matrix-proof.md"
LORE_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-goodie-state-save-appcore-boundary-corpus-fixture-matrix.v1.json"
READINESS = ROOT / "release" / "readiness" / "missionscript_goodie_state_save_appcore_boundary_corpus_fixture_matrix_2026-06-09.md"

RUNTIME_GATE_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-goodie-state-save-runtime-proof-readiness-gate.v1.json"
BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
LORE_MAPPED = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
LORE_BIN_INDEX = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
LORE_RE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"
MISSIONSCRIPT_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-iscript-static-contract.md"
LORE_MISSIONSCRIPT_CONTRACT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-iscript-static-contract.md"
GOODIES_SYSTEM = ROOT / "reverse-engineering" / "save-file" / "goodies-system.md"
LORE_GOODIES_SYSTEM = ROOT / "lore-book" / "reverse-engineering" / "save-file" / "goodies-system.md"
SAVE_FORMAT = ROOT / "reverse-engineering" / "save-file" / "save-format.md"
LORE_SAVE_FORMAT = ROOT / "lore-book" / "reverse-engineering" / "save-file" / "save-format.md"
PACKAGE_JSON = ROOT / "package.json"

THIS_SLICE = "MissionScript Goodie State / Save AppCore Boundary-Corpus Fixture Matrix Proof"
THIS_PLAN = "MissionScript Goodie State / Save AppCore Boundary-Corpus Fixture Matrix Proof Plan"
THIS_STATUS = "missionscript-goodie-state-save-appcore-boundary-corpus-fixture-matrix-complete-651-appcore-cases-not-runtime-proof"
PREVIOUS_SLICE = "MissionScript Goodie State / Save Runtime-Proof Readiness Gate"
NEXT_SLICE = "MissionScript Goodie State / Save AppCore Copied-Baseline Boundary Corpus Harness Proof Plan"
SCHEMA_NAME = "missionscript-goodie-state-save-appcore-boundary-corpus-fixture-matrix.v1.json"
PROOF_NAME = "missionscript-goodie-state-save-appcore-boundary-corpus-fixture-matrix-proof.md"

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
    "runtime goodie mutation proven",
    "runtime goodie state mutation proven",
    "runtime save/load behavior proven",
    "runtime defaultoptions behavior proven",
    "runtime goodies wall behavior proven",
    "runtime score behavior proven",
    "copied-file boundary corpus behavior proven",
    "installed game mutation proven",
    "original executable mutation proven",
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


def check_prerequisite(failures: list[str]) -> None:
    gate = read_json(RUNTIME_GATE_SCHEMA)
    require(gate["missionScriptGoodieStateSaveRuntimeProofReadinessGateStatus"] == "missionscript-goodie-state-save-runtime-proof-readiness-gate-complete-runtime-deferred-no-launch", "runtime gate status mismatch", failures)
    require(gate["selectedNextSlice"] == THIS_PLAN, "runtime gate selected next slice mismatch", failures)
    require(gate["decision"]["runtimeDeferred"] is True, "runtime gate deferred flag mismatch", failures)
    require(gate["negativeGuards"]["runtimeExecution"] is False, "runtime gate runtime guard mismatch", failures)
    require(gate["negativeGuards"]["beLaunch"] is False, "runtime gate launch guard mismatch", failures)


def check_schema(failures: list[str]) -> None:
    schema = read_json(SCHEMA)
    lore = read_json(LORE_SCHEMA)
    require(lore == schema, "lore schema mirror mismatch", failures)
    require(schema["schemaVersion"] == "missionscript-goodie-state-save-appcore-boundary-corpus-fixture-matrix.v1", "schema version mismatch", failures)
    require(schema["status"] == "PASS", "schema status mismatch", failures)
    require(schema["missionScriptGoodieStateSaveAppCoreBoundaryCorpusFixtureMatrixStatus"] == THIS_STATUS, "schema status token mismatch", failures)
    require(schema["previousSlice"] == PREVIOUS_SLICE, "schema previous slice mismatch", failures)
    require(schema["selectedNextSlice"] == NEXT_SLICE, "schema selected next slice mismatch", failures)
    require(schema["selectedFixtureFamily"] == "goodie-state-save", "schema fixture family mismatch", failures)
    require(schema["selectedFixturePath"] == "goodie-state-save-index-state-byte-preservation", "schema fixture path mismatch", failures)

    implementation = schema["implementation"]
    require(implementation["interfaceKind"] == "pure AppCore in-memory buffer codec", "implementation kind mismatch", failures)
    for key in ("fileIoPerformed", "copiedFileMutationPerformed", "sourceBaselineRead", "privateArtifactMaterialized", "productUiWired"):
        require(implementation[key] is False, f"implementation guard mismatch: {key}", failures)

    context = schema["staticContext"]
    require(context["staticFunctionQuality"] == "6411/6411 = 100.00%", "static closure mismatch", failures)
    require(context["staticDebt"] == "0 / 0 / 0", "static debt mismatch", failures)
    require(context["currentRiskFocused"] == "1179/1179 = 100.00%", "current-risk mismatch", failures)

    contract = schema["codecContract"]
    require(contract["expectedFileSize"] == 10004, "expected size mismatch", failures)
    require(contract["versionWord"] == "0x4BD1", "version word mismatch", failures)
    require(contract["trueViewGoodieBase"] == "0x1F46", "Goodie base mismatch", failures)
    require(contract["goodieStorageEntryCount"] == 300, "storage count mismatch", failures)
    require(contract["displayableGoodieCount"] == 233, "displayable count mismatch", failures)
    require(contract["reservedPreserveEntryCount"] == 67, "reserved count mismatch", failures)
    require(contract["goodieStorageEndExclusive"] == "0x23F6", "storage end mismatch", failures)
    require(contract["mappingFormula"] == "save_goodie_index = script_index - 1", "mapping formula mismatch", failures)
    require(contract["offsetFormula"] == "0x1F46 + (script_index - 1) * 4", "offset formula mismatch", failures)
    require(contract["reservedWritePolicy"] == "displayable-only-default-rejects-reserved", "reserved policy mismatch", failures)

    corpus = schema["corpus"]
    require(corpus["previousCleanRoomXunitCaseCount"] == 249, "previous clean-room count mismatch", failures)
    require(corpus["storageVectorCaseCount"] == 300, "storage vector count mismatch", failures)
    require(corpus["displayableRoundTripCaseCount"] == 233, "displayable roundtrip count mismatch", failures)
    require(corpus["reservedMutationRejectionCaseCount"] == 67, "reserved rejection count mismatch", failures)
    require(corpus["displayableBoundaryStateMatrixCaseCount"] == 32, "boundary state matrix count mismatch", failures)
    require(corpus["invalidRawStateCaseCount"] == 3, "invalid raw state count mismatch", failures)
    require(corpus["xunitTestCaseCount"] == 651, "xUnit count mismatch", failures)
    require(corpus["boundaryScriptIndices"] == [1, 2, 51, 53, 68, 71, 232, 233], "boundary script indices mismatch", failures)
    require(corpus["boundaryOffsets"] == ["0x1F46", "0x1F4A", "0x200E", "0x2016", "0x2052", "0x205E", "0x22E2", "0x22E6"], "boundary offsets mismatch", failures)
    require(corpus["knownCopiedBaselineChangedOffsets"] == ["0x1F46", "0x200E", "0x2016", "0x2052", "0x205E", "0x22E6"], "known changed offsets mismatch", failures)
    for key in (
        "allStorageScriptIndicesVectorized",
        "allDisplayableScriptIndicesRoundTrip",
        "allReservedScriptIndicesRejected",
        "allReservedRejectionsLeaveBufferUnchanged",
        "allBoundaryStatesRoundTrip",
        "allBoundaryStatesRestoreToUnknownBaseline",
        "invalidRawStateRejected",
        "invalidMixedBatchLeavesBufferUnchanged",
        "wrongSizeRejected",
        "wrongVersionRejected",
    ):
        require(corpus[key] is True, f"corpus proof flag mismatch: {key}", failures)
    require(corpus["unexpectedDiffCount"] == 0, "unexpected diff count mismatch", failures)
    require(corpus["legacyTrapHitCount"] == 0, "legacy trap count mismatch", failures)

    validation = schema["dotnetValidation"]
    require(validation["dotnetFilter"] == "MissionScriptGoodieStateSaveCodecTests", "dotnet filter mismatch", failures)
    require(validation["passed"] is True, "dotnet pass flag mismatch", failures)
    require(validation["total"] == 651, "dotnet total mismatch", failures)
    require(validation["failed"] == 0, "dotnet failed mismatch", failures)
    require(validation["skipped"] == 0, "dotnet skipped mismatch", failures)

    guards = schema["negativeGuards"]
    for key in (
        "runtimeExecution",
        "beLaunch",
        "newLaunch",
        "screenshotCapture",
        "privateFrameReviewPerformed",
        "rowObservation",
        "nativeInput",
        "debuggerAttachment",
        "installedGameMutationAllowed",
        "originalExecutableMutationAllowed",
        "defaultoptionsMutation",
        "saveSynthesis",
        "ghidraMutation",
        "executablePatching",
        "godotWork",
        "productUiWired",
        "rebuildImplementation",
        "runtimeMissionScriptExecutionProven",
        "runtimeCommandEffectsProven",
        "runtimeGoodieStateMutationProven",
        "runtimeSaveLoadBehaviorProven",
        "runtimeDefaultoptionsBehaviorProven",
        "runtimeGoodiesWallBehaviorProven",
        "runtimeScoreBehaviorProven",
        "copiedFileBoundaryCorpusBehaviorProven",
        "rebuildParityProven",
        "noNoticeableDifferenceParityProven",
    ):
        require(guards[key] is False, f"negative guard mismatch: {key}", failures)
    for key in (
        "runtimeObservationRows",
        "missionScriptRuntimeEvidenceRows",
        "runtimeCommandEffectRows",
        "runtimeGoodieStateRows",
        "runtimeSaveRows",
        "runtimeDefaultOptionsRows",
        "runtimeGoodiesWallRows",
        "runtimeScoreRows",
    ):
        require(guards[key] == 0, f"zero guard mismatch: {key}", failures)
    require(guards["publicLeakCheck"] == "PASS", "public leak status mismatch", failures)
    check_no_bad_public_content(SCHEMA, failures)


def check_code_and_tests(failures: list[str]) -> None:
    codec = read_text(CODEC)
    tests = read_text(TESTS)
    for token in (
        "public const int ExpectedFileSize = 10004",
        "public const ushort VersionWord = 0x4BD1",
        "public const int GoodieBaseOffset = 0x1F46",
        "public const int GoodieStorageEntryCount = 300",
        "public const int DisplayableGoodieCount = 233",
        "public const int ReservedPreserveEntryCount = GoodieStorageEntryCount - DisplayableGoodieCount",
        "return GetVectorFromSaveIndex(scriptIndex - 1)",
        "int offset = GoodieBaseOffset + (saveGoodieIndex * 4)",
    ):
        require(token in codec, f"codec missing token: {token}", failures)
    for token in ("File.", "Directory.", "Process.", "Ghidra", "Godot", "Program Files", "steamapps"):
        require(token not in codec, f"codec contains forbidden token: {token}", failures)

    for token in (
        "GetVectorFromScriptIndex_ForEveryStorageScriptIndex_MatchesTrueViewOffsetAndRange",
        "SetDisplayableState_ForEveryReservedScriptIndex_IsRejectedAndLeavesBufferUnchanged",
        "SetDisplayableState_ForBoundaryStateMatrix_RoundtripsAndRestores",
        "GetStateByScriptIndex_RejectsRawStateOutsideKnownRange",
        "AllStorageScriptIndices",
        "AllReservedScriptIndices",
        "DisplayableBoundaryStateMatrix",
        "scriptIndex <= MissionScriptGoodieStateSaveCodec.GoodieStorageEntryCount",
        "scriptIndex <= MissionScriptGoodieStateSaveCodec.DisplayableGoodieCount",
        "new[] { 1, 2, 51, 53, 68, 71, 232, 233 }",
        "Enum.GetValues<MissionScriptGoodieState>()",
        "BinaryPrimitives.WriteUInt32LittleEndian(buffer.AsSpan(vector.TrueViewDwordOffset, 4), 4)",
    ):
        require(token in tests, f"test source missing token: {token}", failures)


def check_docs(failures: list[str]) -> None:
    required_tokens = (
        THIS_SLICE,
        THIS_STATUS,
        PREVIOUS_SLICE,
        NEXT_SLICE,
        PROOF_NAME,
        SCHEMA_NAME,
        "interfaceKind=pure AppCore in-memory buffer codec",
        "xunitTestCaseCount=651",
        "storageVectorCaseCount=300",
        "displayableRoundTripCaseCount=233",
        "reservedMutationRejectionCaseCount=67",
        "displayableBoundaryStateMatrixCaseCount=32",
        "invalidRawStateCaseCount=3",
        "boundaryScriptIndices=1,2,51,53,68,71,232,233",
        "boundaryOffsets=0x1F46,0x1F4A,0x200E,0x2016,0x2052,0x205E,0x22E2,0x22E6",
        "allStorageScriptIndicesVectorized=true",
        "allDisplayableScriptIndicesRoundTrip=true",
        "allReservedScriptIndicesRejected=true",
        "allReservedRejectionsLeaveBufferUnchanged=true",
        "allBoundaryStatesRoundTrip=true",
        "allBoundaryStatesRestoreToUnknownBaseline=true",
        "invalidRawStateRejected=true",
        "runtimeExecution=false",
        "beLaunch=false",
        "ghidraMutation=false",
        "executablePatching=false",
        "godotWork=false",
        "rebuildImplementation=false",
        "runtimeObservationRows=0",
        "missionScriptRuntimeEvidenceRows=0",
        "runtimeCommandEffectRows=0",
        "runtimeGoodieStateRows=0",
        "runtimeSaveRows=0",
        "runtimeDefaultOptionsRows=0",
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
        PROOF_NAME,
        SCHEMA_NAME,
        f"selectedNextSlice={NEXT_SLICE}",
        "xunitTestCaseCount=651",
        "storageVectorCaseCount=300",
        "reservedMutationRejectionCaseCount=67",
        "displayableBoundaryStateMatrixCaseCount=32",
        "invalidRawStateCaseCount=3",
        "runtimeExecution=false",
        "beLaunch=false",
        "publicLeakCheck=PASS",
    )
    front_docs = (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX, MISSIONSCRIPT_CONTRACT, GOODIES_SYSTEM, SAVE_FORMAT)
    for path in front_docs:
        text = read_text(path)
        for token in front_door_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing front-door token: {token}", failures)
        require(
            f"The selected active static-to-proof slice is {NEXT_SLICE}. Status: selected" in text
            or f"active next static child lane: {NEXT_SLICE}" in text,
            f"{path.relative_to(ROOT)} missing copied-baseline boundary corpus active lane",
            failures,
        )

    for source, mirror in (
        (BACKLOG, LORE_BACKLOG),
        (MAPPED, LORE_MAPPED),
        (BIN_INDEX, LORE_BIN_INDEX),
        (RE_INDEX, LORE_RE_INDEX),
        (MISSIONSCRIPT_CONTRACT, LORE_MISSIONSCRIPT_CONTRACT),
        (GOODIES_SYSTEM, LORE_GOODIES_SYSTEM),
        (SAVE_FORMAT, LORE_SAVE_FORMAT),
    ):
        require(read_text(source) == read_text(mirror), f"lore mirror mismatch for {source.relative_to(ROOT)}", failures)


def check_package(failures: list[str]) -> None:
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:missionscript-goodie-state-save-appcore-boundary-corpus-fixture-matrix")
        == r"py -3 tools\missionscript_goodie_state_save_appcore_boundary_corpus_fixture_matrix_probe.py --check",
        "missing package fixture matrix script",
        failures,
    )
    require("test:missionscript-goodie-state-save-runtime-proof-readiness-gate" in scripts, "missing runtime gate prerequisite script", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_prerequisite(failures)
    check_schema(failures)
    check_code_and_tests(failures)
    check_docs(failures)
    check_package(failures)
    require(no_bea_process_running(), "BEA.exe process is running after fixture matrix proof", failures)

    if failures:
        print("MissionScript Goodie state/save AppCore boundary-corpus fixture matrix probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("MissionScript Goodie state/save AppCore boundary-corpus fixture matrix probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
