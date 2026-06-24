#!/usr/bin/env python3
"""Validate MissionScript Goodie-state/save copied-baseline boundary corpus proof."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

HARNESS_PROJECT = ROOT / "tools" / "MissionScriptGoodieStateSaveBoundaryCorpusHarness" / "MissionScriptGoodieStateSaveBoundaryCorpusHarness.csproj"
HARNESS_SOURCE = ROOT / "tools" / "MissionScriptGoodieStateSaveBoundaryCorpusHarness" / "Program.cs"
APPCORE_CODEC = ROOT / "OnslaughtCareerEditor.AppCore" / "MissionScriptGoodieStateSaveCodec.cs"
APPCORE_TESTS = ROOT / "OnslaughtCareerEditor.AppCore.Tests" / "MissionScriptGoodieStateSaveCodecTests.cs"

PRIVATE_DIR = ROOT / "subagents" / "static-to-proof" / "missionscript-goodie-state-save-appcore-copied-baseline-boundary-corpus-harness-proof"
PRIVATE_SUMMARY = PRIVATE_DIR / "evidence-summary.private.json"

PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-goodie-state-save-appcore-copied-baseline-boundary-corpus-harness-proof.md"
RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-goodie-state-save-appcore-copied-baseline-boundary-corpus-harness.v1.json"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-goodie-state-save-appcore-copied-baseline-boundary-corpus-harness-proof.md"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-goodie-state-save-appcore-copied-baseline-boundary-corpus-harness.v1.json"
READINESS = ROOT / "release" / "readiness" / "missionscript_goodie_state_save_appcore_copied_baseline_boundary_corpus_harness_2026-06-09.md"

BOUNDARY_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-goodie-state-save-appcore-boundary-corpus-fixture-matrix.v1.json"
CODEC_HARNESS_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-goodie-state-save-appcore-copied-baseline-codec-harness.v1.json"

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

THIS_SLICE = "MissionScript Goodie State / Save AppCore Copied-Baseline Boundary Corpus Harness Proof"
THIS_ACTIVE_SLICE = "MissionScript Goodie State / Save AppCore Copied-Baseline Boundary Corpus Harness Proof Plan"
THIS_STATUS = "missionscript-goodie-state-save-appcore-copied-baseline-boundary-corpus-harness-complete-copied-real-baseline-boundary-corpus-not-runtime-proof"
PREVIOUS_SLICE = "MissionScript Goodie State / Save AppCore Boundary-Corpus Fixture Matrix Proof"
PREVIOUS_STATUS = "missionscript-goodie-state-save-appcore-boundary-corpus-fixture-matrix-complete-651-appcore-cases-not-runtime-proof"
NEXT_SLICE = "MissionScript Command-Effect Post-Goodie Selection Refresh Proof Plan"

EXPECTED_PRIVATE_FILES = {
    "career-goodie-boundary-corpus-baseline.bes",
    "defaultoptions-goodie-boundary-corpus-baseline.bea",
    "career-goodie-boundary-corpus-noop.bes",
    "defaultoptions-goodie-boundary-corpus-noop.bea",
    "career-goodie-boundary-corpus-script-001-sample.bes",
    "career-goodie-boundary-corpus-script-002-sample.bes",
    "career-goodie-boundary-corpus-script-051-sample.bes",
    "career-goodie-boundary-corpus-script-053-sample.bes",
    "career-goodie-boundary-corpus-script-068-sample.bes",
    "career-goodie-boundary-corpus-script-071-sample.bes",
    "career-goodie-boundary-corpus-script-232-sample.bes",
    "career-goodie-boundary-corpus-script-233-sample.bes",
}
EXPECTED_BOUNDARY_INDICES = [1, 2, 51, 53, 68, 71, 232, 233]
EXPECTED_BOUNDARY_OFFSETS = ["0x1F46", "0x1F4A", "0x200E", "0x2016", "0x2052", "0x205E", "0x22E2", "0x22E6"]
EXPECTED_TRAPS = ["0x23A4", "0x22D4", "0x240C"]

PUBLIC_FORBIDDEN_TOKENS = (
    "C:\\Users",
    "C:/Users",
    "G:\\",
    "Program Files",
    "steamapps",
    "save-attempts",
    "subagents/",
    "subagents\\",
    "game/",
    "game\\",
    "media/",
    "media\\",
    '"relativePath":',
    '"sha256":',
    "career-goodie-boundary-corpus-",
    "defaultoptions-goodie-boundary-corpus-",
    "HWND",
    "window handle",
    "process id",
    "password",
    "token=",
    "PatchResult.Message",
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


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def version_word(data: bytes) -> str:
    return f"0x{int.from_bytes(data[0:2], 'little'):04X}"


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


def run_harness() -> None:
    subprocess.run(
        [
            "dotnet",
            "run",
            "--project",
            str(HARNESS_PROJECT.relative_to(ROOT)),
            "--",
            "--repo-root",
            ".",
        ],
        cwd=ROOT,
        check=True,
    )


def check_no_public_leaks(path: Path, failures: list[str]) -> None:
    text = read_text(path)
    lower = text.lower()
    for token in PUBLIC_FORBIDDEN_TOKENS:
        require(token.lower() not in lower, f"{path.relative_to(ROOT)} leaks forbidden public token: {token}", failures)
    for phrase in FORBIDDEN_OVERCLAIMS:
        require(phrase not in lower, f"{path.relative_to(ROOT)} overclaims forbidden category: {phrase}", failures)
    require(re.search(r"\b[a-f0-9]{64}\b", lower) is None, f"{path.relative_to(ROOT)} leaks raw 64-hex digest", failures)


def check_prerequisites(failures: list[str]) -> None:
    boundary = read_json(BOUNDARY_SCHEMA)
    harness = read_json(CODEC_HARNESS_SCHEMA)
    require(boundary["missionScriptGoodieStateSaveAppCoreBoundaryCorpusFixtureMatrixStatus"] == PREVIOUS_STATUS, "boundary fixture prerequisite status mismatch", failures)
    require(boundary["selectedNextSlice"] == THIS_ACTIVE_SLICE, "boundary fixture prerequisite next-slice mismatch", failures)
    require(boundary["implementation"]["fileIoPerformed"] is False, "boundary fixture file-I/O guard mismatch", failures)
    require(boundary["corpus"]["xunitTestCaseCount"] == 651, "boundary fixture xUnit count mismatch", failures)
    require(boundary["corpus"]["storageVectorCaseCount"] == 300, "boundary fixture storage count mismatch", failures)
    require(boundary["corpus"]["displayableRoundTripCaseCount"] == 233, "boundary fixture displayable count mismatch", failures)
    require(boundary["corpus"]["reservedMutationRejectionCaseCount"] == 67, "boundary fixture reserved count mismatch", failures)
    require(boundary["corpus"]["displayableBoundaryStateMatrixCaseCount"] == 32, "boundary fixture matrix count mismatch", failures)
    require(harness["goodieStateSaveAppCoreCopiedBaselineCodecHarnessStatus"].endswith("not-runtime-proof"), "copied-baseline codec harness prerequisite status mismatch", failures)
    require(harness["implementation"]["appCoreCodecUsed"] is True, "copied-baseline codec harness AppCore guard mismatch", failures)
    require(harness["implementation"]["appCorePatcherUsed"] is False, "copied-baseline codec harness patcher guard mismatch", failures)
    require(harness["privateEvidence"]["sourcePathsPublic"] is False, "copied-baseline codec harness source disclosure mismatch", failures)


def check_harness_source(failures: list[str]) -> None:
    project = read_text(HARNESS_PROJECT)
    source = read_text(HARNESS_SOURCE)
    codec = read_text(APPCORE_CODEC)
    tests = read_text(APPCORE_TESTS)
    require("ProjectReference Include=\"..\\..\\OnslaughtCareerEditor.AppCore\\OnslaughtCareerEditor.AppCore.csproj\"" in project, "harness project missing AppCore reference", failures)
    for token in (
        "SchemaVersion = \"missionscript-goodie-state-save-appcore-copied-baseline-boundary-corpus-private-evidence.v1\"",
        "BoundaryScriptIndices = [1, 2, 51, 53, 68, 71, 232, 233]",
        "ReadAllStorageStates",
        "RunDisplayableRoundTrips",
        "RunReservedRejections",
        "RunBoundaryStateMatrix",
        "MissionScriptGoodieStateSaveCodec.GetStateByScriptIndex(baseline, scriptIndex)",
        "MissionScriptGoodieStateSaveCodec.SetDisplayableStateByScriptIndex(toggled, scriptIndex, next)",
        "MissionScriptGoodieStateSaveCodec.SetDisplayableStateByScriptIndex(candidate, scriptIndex, state)",
        "AppCoreCodecUsed = true",
        "AppCorePatcherUsed = false",
        "ManualGoodieDwordWriteInHarness = false",
        "AppCoreCodecFileIo = false",
    ):
        require(token in source, f"harness source missing boundary token: {token}", failures)
    for forbidden in (
        "BinaryPrimitives.WriteUInt32LittleEndian",
        "BesFilePatcher.PatchGoodieStates",
        "Program Files",
        "steamapps",
        "BEA.exe",
    ):
        require(forbidden not in source, f"harness source contains forbidden token: {forbidden}", failures)
    require("File." not in codec, "AppCore codec gained file I/O", failures)
    require("GetVectorFromScriptIndex_ForEveryStorageScriptIndex_MatchesTrueViewOffsetAndRange" in tests, "AppCore tests missing storage corpus", failures)


def validate_private_summary(summary: dict[str, Any], failures: list[str], check_files: bool) -> None:
    require(summary["schemaVersion"] == "missionscript-goodie-state-save-appcore-copied-baseline-boundary-corpus-private-evidence.v1", "private schema mismatch", failures)
    require(summary["status"] == "PASS", "private status mismatch", failures)
    source = summary["source"]
    for key in ("sourcePathsPublic", "sourceHashesPublic", "artifactPathsPublic", "artifactHashesPublic", "rawBytesPublic"):
        require(source[key] is False, f"private source disclosure mismatch: {key}", failures)
    require(source["copiedDefaultOptionsValidationOnly"] is True, "defaultoptions validation-only guard mismatch", failures)

    harness = summary["harness"]
    for key in ("appCoreCodecUsed", "harnessFileIo", "sourceBaselineRead", "privateArtifactMaterialized"):
        require(harness[key] is True, f"private harness guard mismatch: {key}", failures)
    for key in ("appCorePatcherUsed", "manualGoodieDwordWriteInHarness", "appCoreCodecFileIo", "productUiWired"):
        require(harness[key] is False, f"private harness guard mismatch: {key}", failures)

    provenance = summary["provenance"]
    for key in ("copyBeforeWrite", "sourcesUnderPriorPrivateEvidenceRoot", "outputsUnderProofPrivateEvidenceRoot", "sourceAndOutputPathsDistinct", "careerSourceUnchanged", "defaultOptionsSourceUnchanged"):
        require(provenance[key] is True, f"private provenance mismatch: {key}", failures)
    require(provenance["careerSourceToInputDiffCount"] == 0, "career source-to-input diff mismatch", failures)
    require(provenance["defaultOptionsSourceToInputDiffCount"] == 0, "defaultoptions source-to-input diff mismatch", failures)

    container = summary["container"]
    require(container["expectedSize"] == 10004, "container size mismatch", failures)
    require(container["versionWord"] == "0x4BD1", "container version mismatch", failures)
    require(container["trueViewGoodieBase"] == "0x1F46", "container Goodie base mismatch", failures)
    require(container["goodieStorageEntryCount"] == 300, "Goodie storage count mismatch", failures)
    require(container["displayableGoodieCount"] == 233, "displayable count mismatch", failures)
    require(container["reservedPreserveEntryCount"] == 67, "reserved count mismatch", failures)
    require(container["goodieStorageEndExclusive"] == "0x23F6", "Goodie end mismatch", failures)
    require(container["fileSizePreserved"] is True, "file-size preservation mismatch", failures)
    require(container["versionWordPreserved"] is True, "version preservation mismatch", failures)

    corpus = summary["corpus"]
    require(corpus["previousInMemoryBoundaryCorpusXunitCaseCount"] == 651, "prior xUnit count mismatch", failures)
    require(corpus["storageVectorCopiedBaselineReadCaseCount"] == 300, "storage read count mismatch", failures)
    require(corpus["displayableCopiedBaselineRoundTripCaseCount"] == 233, "displayable roundtrip count mismatch", failures)
    require(corpus["reservedCopiedBaselineRejectionCaseCount"] == 67, "reserved rejection count mismatch", failures)
    require(corpus["boundaryStateCopiedBaselineMatrixCaseCount"] == 32, "boundary matrix count mismatch", failures)
    require(corpus["copiedBaselineBoundaryCorpusCaseCount"] == 632, "copied-baseline corpus count mismatch", failures)
    require(corpus["sampleBoundaryArtifactCount"] == 8, "sample artifact count mismatch", failures)
    require(corpus["boundaryScriptIndices"] == EXPECTED_BOUNDARY_INDICES, "boundary indices mismatch", failures)
    require(corpus["boundaryStateValues"] == [0, 1, 2, 3], "boundary states mismatch", failures)
    require(corpus["boundaryOffsets"] == EXPECTED_BOUNDARY_OFFSETS, "boundary offsets mismatch", failures)
    for key in (
        "allStorageScriptIndicesReadFromCopiedBaseline",
        "allStorageStateValuesWithinKnownRange",
        "allDisplayableCopiedBaselineRoundTrip",
        "toggleTouchesOnlyExpectedByteForAllDisplayable",
        "toggleIdempotentForAllDisplayable",
        "restoreToBaselineForAllDisplayable",
        "allReservedCopiedBaselineRejectionsLeaveBufferUnchanged",
        "allBoundaryStatesRoundTripOnCopiedBaseline",
        "allBoundaryStatesRestoreToBaseline",
    ):
        require(corpus[key] is True, f"corpus guard mismatch: {key}", failures)
    require(corpus["targetReadbackMismatchCount"] == 0, "target readback mismatch", failures)
    require(corpus["unexpectedDiffCount"] == 0, "unexpected diff mismatch", failures)
    require(corpus["legacyTrapHitCount"] == 0, "legacy trap mismatch", failures)
    require(corpus["legacyAlignedViewTrapOffsets"] == EXPECTED_TRAPS, "legacy trap offset mismatch", failures)

    require(summary["noOp"]["careerNoopDiffCount"] == 0, "career no-op diff mismatch", failures)
    require(summary["noOp"]["defaultOptionsNoopDiffCount"] == 0, "defaultoptions no-op diff mismatch", failures)
    for key, value in summary["preservation"].items():
        require(value is True, f"preservation mismatch: {key}", failures)
    for key, value in summary["rejections"].items():
        require(value is True, f"rejection mismatch: {key}", failures)
    for key in (
        "saveSynthesis",
        "installedGameMutation",
        "originalExecutableMutation",
        "defaultoptionsMutation",
        "runtimeExecution",
        "beLaunch",
        "ghidraMutation",
        "executablePatching",
        "godotWork",
        "productUiWired",
        "rebuildImplementation",
        "runtimeGoodieStateMutationProven",
        "runtimeSaveBehaviorProven",
        "runtimeGoodiesWallBehaviorProven",
        "runtimeScoreBehaviorProven",
    ):
        require(summary["negativeGuards"][key] is False, f"negative guard mismatch: {key}", failures)
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
        require(summary["negativeGuards"][key] == 0, f"zero guard mismatch: {key}", failures)

    if not check_files:
        return
    seen = {Path(row["relativePath"]).name: row for row in summary["copiedArtifacts"]}
    require(set(seen) == EXPECTED_PRIVATE_FILES, "private artifact name set mismatch", failures)
    for name, row in seen.items():
        path = PRIVATE_DIR / name
        require(path.is_file(), f"missing private artifact file: {name}", failures)
        if path.is_file():
            data = path.read_bytes()
            require(len(data) == 10004, f"{name} size mismatch", failures)
            require(version_word(data) == "0x4BD1", f"{name} version mismatch", failures)
            require(row["sha256"] == sha256(data), f"{name} hash mismatch", failures)


def public_schema_from_private(summary: dict[str, Any]) -> dict[str, Any]:
    corpus = summary["corpus"]
    return {
        "schemaVersion": "missionscript-goodie-state-save-appcore-copied-baseline-boundary-corpus-harness.v1",
        "status": "PASS",
        "goodieStateSaveAppCoreCopiedBaselineBoundaryCorpusHarnessStatus": THIS_STATUS,
        "previousSlice": PREVIOUS_SLICE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedFixtureFamily": "goodie-state-save",
        "selectedFixturePath": "goodie-state-save-index-state-byte-preservation",
        "implementation": {
            "toolProjectPath": "tools/MissionScriptGoodieStateSaveBoundaryCorpusHarness/MissionScriptGoodieStateSaveBoundaryCorpusHarness.csproj",
            "appCoreCodecPath": "OnslaughtCareerEditor.AppCore/MissionScriptGoodieStateSaveCodec.cs",
            "interfaceKind": "AppCore Goodie codec boundary corpus applied by proof-only copied-baseline harness",
            "appCoreCodecUsed": True,
            "appCorePatcherUsed": False,
            "manualGoodieDwordWriteInHarness": False,
            "appCoreCodecFileIo": False,
            "harnessFileIo": True,
            "productUiWired": False,
            "sourceBaselineRead": True,
            "privateArtifactMaterialized": True,
        },
        "privateEvidence": {
            "privateEvidenceRootPublic": False,
            "sourcePathsPublic": False,
            "sourceHashesPublic": False,
            "artifactPathsPublic": False,
            "artifactHashesPublic": False,
            "rawSaveBytesPublic": False,
            "copiedRealBaselineClass": "validated copied real career .bes and defaultoptions.bea baselines from prior ignored evidence",
            "copiedDefaultOptionsValidationOnly": True,
            "copiedArtifactCount": len(summary["copiedArtifacts"]),
            "sampleBoundaryArtifactCount": corpus["sampleBoundaryArtifactCount"],
            "copyBeforeWrite": summary["provenance"]["copyBeforeWrite"],
            "sourceAndOutputPathsDistinct": summary["provenance"]["sourceAndOutputPathsDistinct"],
            "careerSourceToInputDiffCount": summary["provenance"]["careerSourceToInputDiffCount"],
            "defaultOptionsSourceToInputDiffCount": summary["provenance"]["defaultOptionsSourceToInputDiffCount"],
            "careerSourceUnchanged": summary["provenance"]["careerSourceUnchanged"],
            "defaultOptionsSourceUnchanged": summary["provenance"]["defaultOptionsSourceUnchanged"],
        },
        "staticContext": {
            "staticFunctionQuality": "6411/6411 = 100.00%",
            "staticDebt": "0 / 0 / 0",
            "expandedStaticSurface": "1560/1560 = 100.00%",
            "currentRiskFocused": "1179/1179 = 100.00%",
            "remainingActiveFocusedWork": 0,
            "latestGhidraBackupClass": "verified-static-backup-redacted",
        },
        "container": {
            "expectedSize": 10004,
            "expectedSizeHex": "0x2714",
            "versionWord": "0x4BD1",
            "trueViewRule": "file_offset = 0x0002 + career_offset",
            "trueViewGoodieBase": "0x1F46",
            "goodieStorageEntryCount": 300,
            "displayableGoodieCount": 233,
            "reservedPreserveEntryCount": 67,
            "goodieStorageEndExclusive": "0x23F6",
            "fileSizePreserved": summary["container"]["fileSizePreserved"],
            "versionWordPreserved": summary["container"]["versionWordPreserved"],
        },
        "corpus": {
            "previousInMemoryBoundaryCorpusXunitCaseCount": corpus["previousInMemoryBoundaryCorpusXunitCaseCount"],
            "storageVectorCopiedBaselineReadCaseCount": corpus["storageVectorCopiedBaselineReadCaseCount"],
            "displayableCopiedBaselineRoundTripCaseCount": corpus["displayableCopiedBaselineRoundTripCaseCount"],
            "reservedCopiedBaselineRejectionCaseCount": corpus["reservedCopiedBaselineRejectionCaseCount"],
            "boundaryStateCopiedBaselineMatrixCaseCount": corpus["boundaryStateCopiedBaselineMatrixCaseCount"],
            "copiedBaselineBoundaryCorpusCaseCount": corpus["copiedBaselineBoundaryCorpusCaseCount"],
            "sampleBoundaryArtifactCount": corpus["sampleBoundaryArtifactCount"],
            "boundaryScriptIndices": corpus["boundaryScriptIndices"],
            "boundaryStateValues": corpus["boundaryStateValues"],
            "boundaryOffsets": corpus["boundaryOffsets"],
            "allStorageScriptIndicesReadFromCopiedBaseline": corpus["allStorageScriptIndicesReadFromCopiedBaseline"],
            "allStorageStateValuesWithinKnownRange": corpus["allStorageStateValuesWithinKnownRange"],
            "allDisplayableCopiedBaselineRoundTrip": corpus["allDisplayableCopiedBaselineRoundTrip"],
            "toggleTouchesOnlyExpectedByteForAllDisplayable": corpus["toggleTouchesOnlyExpectedByteForAllDisplayable"],
            "toggleIdempotentForAllDisplayable": corpus["toggleIdempotentForAllDisplayable"],
            "restoreToBaselineForAllDisplayable": corpus["restoreToBaselineForAllDisplayable"],
            "allReservedCopiedBaselineRejectionsLeaveBufferUnchanged": corpus["allReservedCopiedBaselineRejectionsLeaveBufferUnchanged"],
            "allBoundaryStatesRoundTripOnCopiedBaseline": corpus["allBoundaryStatesRoundTripOnCopiedBaseline"],
            "allBoundaryStatesRestoreToBaseline": corpus["allBoundaryStatesRestoreToBaseline"],
            "targetReadbackMismatchCount": corpus["targetReadbackMismatchCount"],
            "unexpectedDiffCount": corpus["unexpectedDiffCount"],
            "legacyTrapHitCount": corpus["legacyTrapHitCount"],
            "legacyAlignedViewTrapOffsets": corpus["legacyAlignedViewTrapOffsets"],
        },
        "noOp": summary["noOp"],
        "preservation": summary["preservation"],
        "rejections": summary["rejections"],
        "negativeGuards": summary["negativeGuards"],
        "claimBoundary": {
            "proves": [
                "the proof-only C# harness applies MissionScriptGoodieStateSaveCodec boundary/corpus checks to copied real career/defaultoptions baselines",
                "all 300 stored Goodie script indices read through the AppCore codec against copied baseline bytes",
                "all 233 displayable Goodie script indices roundtrip through AppCore against copied baseline bytes and restore to baseline",
                "all 67 reserved Goodie script indices reject mutation and leave copied baseline bytes unchanged",
                "the eight boundary/corpus script indices roundtrip states 0..3 against copied baseline bytes",
                "no-op, non-target Goodies, reserved Goodies, kill counters, tech slots, options entries, options tail, readback, and legacy trap guards satisfy the byte-preservation contract",
            ],
            "doesNotProve": [
                "runtime MissionScript execution",
                "runtime command effects",
                "runtime Goodie state mutation",
                "runtime save/load behavior",
                "runtime defaultoptions behavior",
                "runtime Goodies wall behavior",
                "runtime score behavior",
                "source selection",
                "private-frame review",
                "screenshot or frame interpretation",
                "native input",
                "debugger behavior",
                "installed game mutation",
                "product UI behavior",
                "Ghidra mutation",
                "executable patching",
                "Godot parity",
                "rebuild implementation",
                "rebuild parity",
                "no-noticeable-difference parity",
            ],
        },
    }


def write_public_schema() -> dict[str, Any]:
    summary = read_json(PRIVATE_SUMMARY)
    failures: list[str] = []
    validate_private_summary(summary, failures, check_files=True)
    if failures:
        raise ValueError("; ".join(failures))
    schema = public_schema_from_private(summary)
    write_json(RESULT, schema)
    write_json(LORE_RESULT, schema)
    return schema


def check_public_schema(failures: list[str]) -> None:
    summary = read_json(PRIVATE_SUMMARY)
    validate_private_summary(summary, failures, check_files=True)
    expected = public_schema_from_private(summary)
    for path in (RESULT, LORE_RESULT):
        actual = read_json(path)
        require(actual == expected, f"{path.relative_to(ROOT)} does not match private-evidence-derived schema", failures)
        require(actual["goodieStateSaveAppCoreCopiedBaselineBoundaryCorpusHarnessStatus"] == THIS_STATUS, "public status mismatch", failures)
        require(actual["selectedNextSlice"] == NEXT_SLICE, "public next-slice mismatch", failures)
        require(actual["implementation"]["appCoreCodecUsed"] is True, "public AppCore guard mismatch", failures)
        require(actual["implementation"]["appCorePatcherUsed"] is False, "public patcher guard mismatch", failures)
        require(actual["implementation"]["manualGoodieDwordWriteInHarness"] is False, "public manual write guard mismatch", failures)
        require(actual["privateEvidence"]["sourcePathsPublic"] is False, "public source path disclosure mismatch", failures)
        require(actual["privateEvidence"]["artifactHashesPublic"] is False, "public artifact hash disclosure mismatch", failures)
        require(actual["corpus"]["copiedBaselineBoundaryCorpusCaseCount"] == 632, "public corpus count mismatch", failures)
        require(actual["negativeGuards"]["runtimeExecution"] is False, "public runtime guard mismatch", failures)
        check_no_public_leaks(path, failures)


def check_docs(failures: list[str]) -> None:
    required_tokens = (
        THIS_SLICE,
        THIS_STATUS,
        PREVIOUS_SLICE,
        NEXT_SLICE,
        "missionscript-goodie-state-save-appcore-copied-baseline-boundary-corpus-harness.v1.json",
        "toolProjectPath=tools/MissionScriptGoodieStateSaveBoundaryCorpusHarness/MissionScriptGoodieStateSaveBoundaryCorpusHarness.csproj",
        "appCoreCodecPath=OnslaughtCareerEditor.AppCore/MissionScriptGoodieStateSaveCodec.cs",
        "interfaceKind=AppCore Goodie codec boundary corpus applied by proof-only copied-baseline harness",
        "appCoreCodecUsed=true",
        "appCorePatcherUsed=false",
        "manualGoodieDwordWriteInHarness=false",
        "appCoreCodecFileIo=false",
        "harnessFileIo=true",
        "productUiWired=false",
        "sourceBaselineRead=true",
        "privateArtifactMaterialized=true",
        "copiedArtifactCount=12",
        "sampleBoundaryArtifactCount=8",
        "sourcePathsPublic=false",
        "sourceHashesPublic=false",
        "artifactPathsPublic=false",
        "artifactHashesPublic=false",
        "rawSaveBytesPublic=false",
        "copiedDefaultOptionsValidationOnly=true",
        "copyBeforeWrite=true",
        "sourceAndOutputPathsDistinct=true",
        "careerSourceToInputDiffCount=0",
        "defaultOptionsSourceToInputDiffCount=0",
        "careerSourceUnchanged=true",
        "defaultOptionsSourceUnchanged=true",
        "expectedSize=10004",
        "versionWord=0x4BD1",
        "trueViewGoodieBase=0x1F46",
        "goodieStorageEntryCount=300",
        "displayableGoodieCount=233",
        "reservedPreserveEntryCount=67",
        "goodieStorageEndExclusive=0x23F6",
        "storageVectorCopiedBaselineReadCaseCount=300",
        "displayableCopiedBaselineRoundTripCaseCount=233",
        "reservedCopiedBaselineRejectionCaseCount=67",
        "boundaryStateCopiedBaselineMatrixCaseCount=32",
        "copiedBaselineBoundaryCorpusCaseCount=632",
        "boundaryScriptIndices=1,2,51,53,68,71,232,233",
        "boundaryOffsets=0x1F46,0x1F4A,0x200E,0x2016,0x2052,0x205E,0x22E2,0x22E6",
        "allStorageScriptIndicesReadFromCopiedBaseline=true",
        "allDisplayableCopiedBaselineRoundTrip=true",
        "toggleTouchesOnlyExpectedByteForAllDisplayable=true",
        "allReservedCopiedBaselineRejectionsLeaveBufferUnchanged=true",
        "allBoundaryStatesRoundTripOnCopiedBaseline=true",
        "targetReadbackMismatchCount=0",
        "unexpectedDiffCount=0",
        "legacyTrapHitCount=0",
        "careerNoopDiffCount=0",
        "defaultOptionsNoopDiffCount=0",
        "nonTargetGoodiesUnchangedForAllDisplayableRoundTrips=true",
        "reservedGoodiesUnchangedForAllDisplayableRoundTrips=true",
        "killCountersUnchangedForAllDisplayableRoundTrips=true",
        "techSlotsUnchangedForAllDisplayableRoundTrips=true",
        "optionsEntriesUnchangedForAllDisplayableRoundTrips=true",
        "optionsTailUnchangedForAllDisplayableRoundTrips=true",
        "invalidScriptIndex0Rejected=true",
        "invalidScriptIndex301Rejected=true",
        "reservedScriptIndex234Rejected=true",
        "invalidState4Rejected=true",
        "invalidStateUintMaxRejected=true",
        "emptyOverrideRejected=true",
        "invalidMixedBatchLeavesBufferUnchanged=true",
        "wrongSizeRejected=true",
        "wrongVersionRejected=true",
        "saveSynthesis=false",
        "defaultoptionsMutation=false",
        "runtimeExecution=false",
        "beLaunch=false",
        "ghidraMutation=false",
        "executablePatching=false",
        "godotWork=false",
        "productUiWired=false",
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
        check_no_public_leaks(path, failures)
    require(read_text(LORE_PROOF) == read_text(PROOF), "lore proof mirror mismatch", failures)
    require(read_json(LORE_RESULT) == read_json(RESULT), "lore schema mirror mismatch", failures)

    front_door_tokens = (
        THIS_SLICE,
        THIS_STATUS,
        "missionscript-goodie-state-save-appcore-copied-baseline-boundary-corpus-harness-proof.md",
        "missionscript-goodie-state-save-appcore-copied-baseline-boundary-corpus-harness.v1.json",
        f"selectedNextSlice={NEXT_SLICE}",
        "copiedArtifactCount=12",
        "copiedBaselineBoundaryCorpusCaseCount=632",
        "storageVectorCopiedBaselineReadCaseCount=300",
        "displayableCopiedBaselineRoundTripCaseCount=233",
        "reservedCopiedBaselineRejectionCaseCount=67",
        "boundaryStateCopiedBaselineMatrixCaseCount=32",
        "sampleBoundaryArtifactCount=8",
        "allDisplayableCopiedBaselineRoundTrip=true",
        "allReservedCopiedBaselineRejectionsLeaveBufferUnchanged=true",
        "sourceBaselineRead=true",
        "privateArtifactMaterialized=true",
        "runtimeExecution=false",
        "beLaunch=false",
    )
    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX, MISSION_CONTRACT, GOODIES_DOC, SAVE_FORMAT):
        text = read_text(path)
        for token in front_door_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing front-door token: {token}", failures)
        require(NEXT_SLICE in text, f"{path.relative_to(ROOT)} missing next static child lane", failures)

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
        scripts.get("test:missionscript-goodie-state-save-appcore-copied-baseline-boundary-corpus-harness")
        == r"py -3 tools\missionscript_goodie_state_save_appcore_copied_baseline_boundary_corpus_harness_probe.py --check",
        "missing AppCore copied-baseline boundary corpus harness package script",
        failures,
    )


def run_check() -> list[str]:
    failures: list[str] = []
    check_prerequisites(failures)
    check_harness_source(failures)
    check_public_schema(failures)
    check_docs(failures)
    check_package(failures)
    require(no_bea_process_running(), "BEA.exe process is running after Goodie copied-baseline boundary corpus harness proof", failures)
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write-private-evidence", action="store_true")
    parser.add_argument("--write-schema", action="store_true")
    args = parser.parse_args()

    if args.write_private_evidence:
        run_harness()
        print(f"Wrote {PRIVATE_SUMMARY.relative_to(ROOT)}")

    if args.write_schema:
        schema = write_public_schema()
        print(f"Wrote {RESULT.relative_to(ROOT)}")
        print(f"Wrote {LORE_RESULT.relative_to(ROOT)}")
        print(f"Public schema status: {schema['status']}")

    if args.check or not (args.write_private_evidence or args.write_schema):
        failures = run_check()
        if failures:
            print("MissionScript Goodie-state/save AppCore copied-baseline boundary corpus harness proof probe: FAIL")
            for failure in failures:
                print(f"- {failure}")
            return 1
        print("MissionScript Goodie-state/save AppCore copied-baseline boundary corpus harness proof probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
