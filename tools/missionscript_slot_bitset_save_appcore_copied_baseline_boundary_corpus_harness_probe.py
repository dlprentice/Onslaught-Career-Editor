#!/usr/bin/env python3
"""Validate MissionScript slot bitset/save copied-baseline boundary corpus proof."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

HARNESS_PROJECT = ROOT / "tools" / "MissionScriptSlotBitsetSaveHarness" / "MissionScriptSlotBitsetSaveHarness.csproj"
HARNESS_SOURCE = ROOT / "tools" / "MissionScriptSlotBitsetSaveHarness" / "Program.cs"
APPCORE_CODEC = ROOT / "OnslaughtCareerEditor.AppCore" / "MissionScriptSlotBitsetSaveCodec.cs"

SOURCE_BASELINE = ROOT / "subagents" / "static-to-proof" / "save-options-controller-byte-preservation-copied-file-proof" / "career-baseline.bes"
PRIVATE_DIR = ROOT / "subagents" / "static-to-proof" / "missionscript-slot-bitset-save-appcore-copied-baseline-boundary-corpus-harness-proof"
PRIVATE_SUMMARY = PRIVATE_DIR / "evidence-summary.private.json"

PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-slot-bitset-save-appcore-copied-baseline-boundary-corpus-harness-proof.md"
RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-slot-bitset-save-appcore-copied-baseline-boundary-corpus-harness.v1.json"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-slot-bitset-save-appcore-copied-baseline-boundary-corpus-harness-proof.md"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-slot-bitset-save-appcore-copied-baseline-boundary-corpus-harness.v1.json"
READINESS = ROOT / "release" / "readiness" / "missionscript_slot_bitset_save_appcore_copied_baseline_boundary_corpus_harness_2026-06-09.md"

BOUNDARY_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-slot-bitset-save-appcore-boundary-slot-corpus.v1.json"
CODEC_HARNESS_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-slot-bitset-save-appcore-copied-baseline-codec-harness.v1.json"

BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
LORE_MAPPED = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
LORE_BIN_INDEX = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
LORE_RE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"
PACKAGE_JSON = ROOT / "package.json"

THIS_SLICE = "MissionScript Slot Bitset/Save AppCore Copied-Baseline Boundary Corpus Harness Proof"
THIS_ACTIVE_SLICE = "MissionScript Slot Bitset/Save AppCore Copied-Baseline Boundary Corpus Harness Proof Plan"
THIS_STATUS = "missionscript-slot-bitset-save-appcore-copied-baseline-boundary-corpus-harness-complete-copied-real-baseline-boundary-corpus-not-runtime-proof"
PREVIOUS_SLICE = "MissionScript Slot Bitset/Save AppCore Boundary-Slot Corpus Proof"
PREVIOUS_STATUS = "missionscript-slot-bitset-save-appcore-boundary-slot-corpus-complete-273-appcore-cases-not-runtime-proof"
NEXT_SLICE = "Save / Options Byte-Preservation AppCore Implementation Contract Proof Plan"
FOLLOWUP_SLICE = "Save / Options Byte-Preservation Runtime-Proof Readiness Gate Plan"

BOUNDARY_OFFSETS = ("0x240A", "0x240E", "0x2412", "0x2416", "0x241A", "0x241E", "0x2422", "0x2426")
EXPECTED_PRIVATE_FILES = {
    "career-slot-boundary-corpus-baseline.bes",
    "career-slot-boundary-corpus-noop.bes",
    "career-slot-boundary-corpus-slot-063-toggle.bes",
    "career-slot-boundary-corpus-slot-064-toggle.bes",
    "career-slot-boundary-corpus-slot-224-toggle.bes",
    "career-slot-boundary-corpus-slot-255-toggle.bes",
}

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
    "sourceCopiedBaseline",
    "copiedArtifacts",
    "setDword",
    "HWND",
    "window handle",
    "process id",
    "password",
    "token=",
)

FORBIDDEN_OVERCLAIMS = (
    "runtime missionscript execution proven",
    "runtime command effects proven",
    "runtime slot persistence proven",
    "runtime save/load behavior proven",
    "runtime defaultoptions behavior proven",
    "copied-file runtime behavior proven",
    "tutorial progression proven",
    "source selection proven",
    "private-frame review complete",
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
    command = [
        "dotnet",
        "run",
        "--project",
        str(HARNESS_PROJECT.relative_to(ROOT)),
        "--",
        "--mode",
        "boundary-corpus",
        "--source",
        str(SOURCE_BASELINE.relative_to(ROOT)),
        "--repo-root",
        ".",
    ]
    subprocess.run(command, cwd=ROOT, check=True)


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
    require(boundary["slotBitsetSaveAppCoreBoundarySlotCorpusStatus"] == PREVIOUS_STATUS, "boundary-corpus prerequisite status mismatch", failures)
    require(boundary["selectedNextSlice"] == THIS_ACTIVE_SLICE, "boundary-corpus prerequisite next-slice mismatch", failures)
    require(boundary["implementation"]["fileIoPerformed"] is False, "boundary-corpus file-I/O guard mismatch", failures)
    require(boundary["corpus"]["singleSlotRoundTripCaseCount"] == 256, "boundary-corpus single-slot count mismatch", failures)
    require(boundary["corpus"]["boundaryPairMaskCaseCount"] == 8, "boundary-corpus pair count mismatch", failures)
    require(harness["slotBitsetSaveAppCoreCopiedBaselineCodecHarnessStatus"].endswith("not-runtime-proof"), "copied-baseline harness prerequisite status mismatch", failures)
    require(harness["implementation"]["appCoreCodecUsed"] is True, "copied-baseline harness AppCore guard mismatch", failures)
    require(harness["privateEvidence"]["sourcePathsPublic"] is False, "copied-baseline harness source disclosure mismatch", failures)


def check_harness_source(failures: list[str]) -> None:
    project = read_text(HARNESS_PROJECT)
    source = read_text(HARNESS_SOURCE)
    codec = read_text(APPCORE_CODEC)
    require("ProjectReference Include=\"..\\..\\OnslaughtCareerEditor.AppCore\\OnslaughtCareerEditor.AppCore.csproj\"" in project, "harness project missing AppCore reference", failures)
    for token in (
        "BoundarySchemaVersion",
        "BoundaryEvidenceRootRelative",
        "BoundaryVectorSlots = [63, 64, 224, 255]",
        "HarnessMode.BoundaryCorpus",
        "MaterializeBoundaryCorpusEvidence",
        "BuildBoundaryPairs",
        "RunSingleSlotRoundTrips",
        "BoundaryPairExpectedSetXorMode = \"(~baselineDword) & mask\"",
        "MissionScriptSlotBitsetSaveCodec.SetSlotsInSingleDword(set, pairSlots, enabled: true)",
        "MissionScriptSlotBitsetSaveCodec.SetSlot(toggled, slot, !original)",
        "ManualSlotDwordWriteInHarness = false",
        "AppCoreCodecUsed = true",
    ):
        require(token in source, f"harness source missing boundary token: {token}", failures)
    for forbidden in (
        "BinaryPrimitives.WriteUInt32LittleEndian",
        "WriteU32",
        "Program Files",
        "steamapps",
        "BEA.exe",
    ):
        require(forbidden not in source, f"harness source contains forbidden token: {forbidden}", failures)
    require("File." not in codec, "AppCore codec gained file I/O", failures)


def validate_private_summary(summary: dict[str, Any], failures: list[str], check_files: bool) -> None:
    require(summary.get("schemaVersion") == "missionscript-slot-bitset-save-appcore-copied-baseline-boundary-corpus-private-evidence.v1", "private schema mismatch", failures)
    require(summary.get("status") == "PASS", "private status mismatch", failures)
    harness = summary["harness"]
    require(harness["interfaceKind"] == "AppCore codec boundary corpus applied by proof-only copied-baseline harness", "private interface kind mismatch", failures)
    require(harness["appCoreCodecUsed"] is True, "private AppCore codec use mismatch", failures)
    require(harness["manualSlotDwordWriteInHarness"] is False, "private manual dword write guard mismatch", failures)
    require(harness["productUiWired"] is False, "private product UI guard mismatch", failures)
    require(harness["appCoreCodecFileIo"] is False, "private AppCore file-I/O guard mismatch", failures)
    require(harness["harnessFileIo"] is True, "private harness file-I/O mismatch", failures)
    require(harness["sourceBaselineRead"] is True, "private source read guard mismatch", failures)
    require(harness["privateArtifactMaterialized"] is True, "private artifact materialization mismatch", failures)

    provenance = summary["provenance"]
    require(provenance["copyBeforeWrite"] is True, "private copy-before-write mismatch", failures)
    require(provenance["sourceAndOutputPathsDistinct"] is True, "private path distinctness mismatch", failures)
    require(provenance["sourceToNewBaselineDiffCount"] == 0, "private source copy mismatch", failures)
    require(provenance["sourceUnchanged"] is True, "private source changed", failures)

    container = summary["container"]
    require(container["expectedSize"] == 10004, "private size mismatch", failures)
    require(container["versionWord"] == "0x4BD1", "private version mismatch", failures)
    require(container["fileSizePreserved"] is True, "private file-size preservation mismatch", failures)
    require(container["versionWordPreserved"] is True, "private version preservation mismatch", failures)

    corpus = summary["corpus"]
    require(corpus["existingSeedVectorCaseCount"] == 5, "private existing seed count mismatch", failures)
    require(corpus["boundaryPairMaskCaseCount"] == 8, "private boundary pair count mismatch", failures)
    require(corpus["singleSlotRoundTripCaseCount"] == 256, "private single-slot count mismatch", failures)
    require(corpus["boundaryVectorSlots"] == [63, 64, 224, 255], "private boundary vector mismatch", failures)
    require(corpus["boundaryPairMask"] == "0x80000001", "private pair mask mismatch", failures)
    require(corpus["boundaryPairExpectedSetXorMode"] == "(~baselineDword) & mask", "private baseline-aware XOR mode mismatch", failures)
    require(corpus["boundaryPairDwordOffsets"] == list(BOUNDARY_OFFSETS), "private pair offsets mismatch", failures)
    require(corpus["allBoundaryPairMasksMatch"] is True, "private pair mask guard mismatch", failures)
    require(corpus["allBoundaryPairSetXorMatchesBaselineState"] is True, "private baseline-aware XOR guard mismatch", failures)
    require(corpus["allBoundaryPairRestoresToBaseline"] is True, "private boundary pair restore mismatch", failures)
    require(corpus["allValidSlotsRoundTrip"] is True, "private all-slot roundtrip mismatch", failures)
    require(corpus["toggleTouchesOnlyExpectedByteForAllValidSlots"] is True, "private single-byte touch mismatch", failures)
    require(corpus["toggleIdempotentForAllValidSlots"] is True, "private idempotence mismatch", failures)
    require(corpus["restoreToBaselineForAllValidSlots"] is True, "private restore mismatch", failures)
    require(corpus["sampleBoundaryArtifactCount"] == 4, "private sample artifact count mismatch", failures)
    require(corpus["crossDwordMaskRejected"] is True, "private cross-dword reject mismatch", failures)
    require(corpus["slot256Rejected"] is True, "private slot256 reject mismatch", failures)
    require(corpus["wrongSizeRejected"] is True, "private wrong-size reject mismatch", failures)
    require(corpus["wrongVersionRejected"] is True, "private wrong-version reject mismatch", failures)

    noop = summary["noOp"]
    preservation = summary["preservation"]
    require(noop["baselineToNoopDiffCount"] == 0, "private noop diff mismatch", failures)
    require(preservation["reservedSlotTailAfterUsedDwordsUnchangedForAllValidSlots"] is True, "private reserved tail mismatch", failures)
    require(preservation["postSlotFieldsThroughPreOptionsUnchangedForAllValidSlots"] is True, "private post-slot field mismatch", failures)
    require(preservation["optionsEntriesUnchangedForAllValidSlots"] is True, "private options entries mismatch", failures)
    require(preservation["optionsTailUnchangedForAllValidSlots"] is True, "private options tail mismatch", failures)
    require(preservation["legacyTrapHitCount"] == 0, "private legacy trap mismatch", failures)
    require(preservation["unexpectedDiffCount"] == 0, "private unexpected diff mismatch", failures)

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
    ):
        require(summary["negativeGuards"][key] is False, f"private guard mismatch: {key}", failures)

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
    preservation = summary["preservation"]
    return {
        "schemaVersion": "missionscript-slot-bitset-save-appcore-copied-baseline-boundary-corpus-harness.v1",
        "status": "PASS",
        "slotBitsetSaveAppCoreCopiedBaselineBoundaryCorpusHarnessStatus": THIS_STATUS,
        "previousSlice": PREVIOUS_SLICE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedFixtureFamily": "slot-bitset-save",
        "selectedFixturePath": "slot-bitset-save-core-handler-and-career-bridge",
        "implementation": {
            "toolProjectPath": "tools/MissionScriptSlotBitsetSaveHarness/MissionScriptSlotBitsetSaveHarness.csproj",
            "appCoreCodecPath": "OnslaughtCareerEditor.AppCore/MissionScriptSlotBitsetSaveCodec.cs",
            "interfaceKind": "AppCore codec boundary corpus applied by proof-only copied-baseline harness",
            "appCoreCodecUsed": True,
            "manualSlotDwordWriteInHarness": False,
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
            "rawBeforeAfterDwordsPublic": False,
            "rawBoundaryPairXorMasksPublic": False,
            "rawSaveSlotStatePublic": False,
            "copiedRealBaselineClass": "validated copied real career .bes baseline from prior ignored evidence",
            "copiedArtifactCount": len(summary["copiedArtifacts"]),
            "sampleBoundaryArtifactCount": corpus["sampleBoundaryArtifactCount"],
            "copyBeforeWrite": summary["provenance"]["copyBeforeWrite"],
            "sourceAndOutputPathsDistinct": summary["provenance"]["sourceAndOutputPathsDistinct"],
            "sourceToNewBaselineDiffCount": summary["provenance"]["sourceToNewBaselineDiffCount"],
            "sourceUnchanged": summary["provenance"]["sourceUnchanged"],
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
            "fileSizePreserved": summary["container"]["fileSizePreserved"],
            "versionWordPreserved": summary["container"]["versionWordPreserved"],
        },
        "corpus": {
            "existingSeedVectorCaseCount": corpus["existingSeedVectorCaseCount"],
            "boundaryPairMaskCaseCount": corpus["boundaryPairMaskCaseCount"],
            "singleSlotCopiedBaselineRoundTripCaseCount": corpus["singleSlotRoundTripCaseCount"],
            "copiedBaselineHarnessCaseCount": corpus["boundaryPairMaskCaseCount"] + corpus["singleSlotRoundTripCaseCount"],
            "boundaryVectorSlots": corpus["boundaryVectorSlots"],
            "boundaryPairMask": corpus["boundaryPairMask"],
            "boundaryPairExpectedSetXorMode": corpus["boundaryPairExpectedSetXorMode"],
            "boundaryPairDwordOffsets": corpus["boundaryPairDwordOffsets"],
            "allBoundaryPairMasksMatch": corpus["allBoundaryPairMasksMatch"],
            "allBoundaryPairSetXorMatchesBaselineState": corpus["allBoundaryPairSetXorMatchesBaselineState"],
            "allBoundaryPairRestoresToBaseline": corpus["allBoundaryPairRestoresToBaseline"],
            "allValidSlotsRoundTrip": corpus["allValidSlotsRoundTrip"],
            "toggleTouchesOnlyExpectedByteForAllValidSlots": corpus["toggleTouchesOnlyExpectedByteForAllValidSlots"],
            "toggleIdempotentForAllValidSlots": corpus["toggleIdempotentForAllValidSlots"],
            "restoreToBaselineForAllValidSlots": corpus["restoreToBaselineForAllValidSlots"],
            "crossDwordMaskRejected": corpus["crossDwordMaskRejected"],
            "invalidSlotLowerBoundRejected": corpus["invalidSlotLowerBoundRejected"],
            "invalidSlotUpperBoundRejected": corpus["invalidSlotUpperBoundRejected"],
            "slot256Rejected": corpus["slot256Rejected"],
            "wrongSizeRejected": corpus["wrongSizeRejected"],
            "wrongVersionRejected": corpus["wrongVersionRejected"],
        },
        "noOp": {
            "baselineToNoopDiffCount": summary["noOp"]["baselineToNoopDiffCount"],
        },
        "preservation": {
            "reservedSlotTailAfterUsedDwordsUnchangedForAllValidSlots": preservation["reservedSlotTailAfterUsedDwordsUnchangedForAllValidSlots"],
            "postSlotFieldsThroughPreOptionsUnchangedForAllValidSlots": preservation["postSlotFieldsThroughPreOptionsUnchangedForAllValidSlots"],
            "optionsEntriesUnchangedForAllValidSlots": preservation["optionsEntriesUnchangedForAllValidSlots"],
            "optionsTailUnchangedForAllValidSlots": preservation["optionsTailUnchangedForAllValidSlots"],
            "unexpectedLegacyTrapHitCount": preservation["legacyTrapHitCount"],
            "unexpectedDiffCount": preservation["unexpectedDiffCount"],
        },
        "negativeGuards": {
            "saveSynthesis": False,
            "installedGameMutation": False,
            "originalExecutableMutation": False,
            "defaultoptionsMutation": False,
            "runtimeExecution": False,
            "beLaunch": False,
            "ghidraMutation": False,
            "executablePatching": False,
            "godotWork": False,
            "productUiWired": False,
            "rebuildImplementation": False,
            "runtimeObservationRows": 0,
            "missionScriptRuntimeEvidenceRows": 0,
            "runtimeCommandEffectRows": 0,
            "runtimeSaveRows": 0,
            "publicLeakCheck": "PASS",
        },
        "claimBoundary": {
            "proves": [
                "the proof-only C# harness applies the AppCore MissionScript slot bitset/save codec boundary corpus to a copied real career baseline",
                "all 256 valid saved slots toggle through AppCore against copied-baseline bytes and restore to baseline",
                "the first and last slot in each used saved dword use the expected 0x80000001 mask with baseline-aware set-XOR comparison",
                "the copied baseline, no-op, sample boundary artifacts, non-target ranges, options entries, options tail, and legacy trap offsets match the byte-preservation contract",
            ],
            "doesNotProve": [
                "runtime MissionScript execution",
                "runtime command effects",
                "runtime slot persistence",
                "runtime save/load behavior",
                "runtime defaultoptions behavior",
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
        require(actual["slotBitsetSaveAppCoreCopiedBaselineBoundaryCorpusHarnessStatus"] == THIS_STATUS, "public status mismatch", failures)
        require(actual["selectedNextSlice"] == NEXT_SLICE, "public next-slice mismatch", failures)
        require(actual["implementation"]["appCoreCodecUsed"] is True, "public AppCore use mismatch", failures)
        require(actual["implementation"]["manualSlotDwordWriteInHarness"] is False, "public manual dword guard mismatch", failures)
        require(actual["privateEvidence"]["sourcePathsPublic"] is False, "public source path disclosure mismatch", failures)
        require(actual["privateEvidence"]["sourceHashesPublic"] is False, "public source hash disclosure mismatch", failures)
        require(actual["privateEvidence"]["artifactPathsPublic"] is False, "public artifact path disclosure mismatch", failures)
        require(actual["privateEvidence"]["artifactHashesPublic"] is False, "public artifact hash disclosure mismatch", failures)
        require(actual["privateEvidence"]["rawBoundaryPairXorMasksPublic"] is False, "public raw XOR disclosure mismatch", failures)
        require(actual["corpus"]["singleSlotCopiedBaselineRoundTripCaseCount"] == 256, "public single-slot count mismatch", failures)
        require(actual["corpus"]["copiedBaselineHarnessCaseCount"] == 264, "public copied-baseline case count mismatch", failures)
        require(actual["preservation"]["unexpectedLegacyTrapHitCount"] == 0, "public legacy trap mismatch", failures)
        check_no_public_leaks(path, failures)


def check_docs(failures: list[str]) -> None:
    required_tokens = (
        THIS_SLICE,
        THIS_STATUS,
        PREVIOUS_SLICE,
        NEXT_SLICE,
        "missionscript-slot-bitset-save-appcore-copied-baseline-boundary-corpus-harness.v1.json",
        "toolProjectPath=tools/MissionScriptSlotBitsetSaveHarness/MissionScriptSlotBitsetSaveHarness.csproj",
        "appCoreCodecPath=OnslaughtCareerEditor.AppCore/MissionScriptSlotBitsetSaveCodec.cs",
        "interfaceKind=AppCore codec boundary corpus applied by proof-only copied-baseline harness",
        "appCoreCodecUsed=true",
        "manualSlotDwordWriteInHarness=false",
        "appCoreCodecFileIo=false",
        "harnessFileIo=true",
        "productUiWired=false",
        "sourceBaselineRead=true",
        "privateArtifactMaterialized=true",
        "copiedArtifactCount=6",
        "sampleBoundaryArtifactCount=4",
        "sourcePathsPublic=false",
        "sourceHashesPublic=false",
        "artifactPathsPublic=false",
        "artifactHashesPublic=false",
        "rawBeforeAfterDwordsPublic=false",
        "rawBoundaryPairXorMasksPublic=false",
        "rawSaveSlotStatePublic=false",
        "copyBeforeWrite=true",
        "sourceAndOutputPathsDistinct=true",
        "sourceToNewBaselineDiffCount=0",
        "sourceUnchanged=true",
        "expectedSize=10004",
        "versionWord=0x4BD1",
        "trueViewRule=file_offset = 0x0002 + career_offset",
        "existingSeedVectorCaseCount=5",
        "boundaryPairMaskCaseCount=8",
        "singleSlotCopiedBaselineRoundTripCaseCount=256",
        "copiedBaselineHarnessCaseCount=264",
        "boundaryPairMask=0x80000001",
        "boundaryPairExpectedSetXorMode=(~baselineDword) & mask",
        "boundaryVectorSlots=63,64,224,255",
        "boundaryPairDwordOffsets=0x240A,0x240E,0x2412,0x2416,0x241A,0x241E,0x2422,0x2426",
        "allBoundaryPairMasksMatch=true",
        "allBoundaryPairSetXorMatchesBaselineState=true",
        "allBoundaryPairRestoresToBaseline=true",
        "allValidSlotsRoundTrip=true",
        "toggleTouchesOnlyExpectedByteForAllValidSlots=true",
        "toggleIdempotentForAllValidSlots=true",
        "restoreToBaselineForAllValidSlots=true",
        "crossDwordMaskRejected=true",
        "slot256Rejected=true",
        "wrongSizeRejected=true",
        "wrongVersionRejected=true",
        "baselineToNoopDiffCount=0",
        "reservedSlotTailAfterUsedDwordsUnchangedForAllValidSlots=true",
        "postSlotFieldsThroughPreOptionsUnchangedForAllValidSlots=true",
        "optionsEntriesUnchangedForAllValidSlots=true",
        "optionsTailUnchangedForAllValidSlots=true",
        "unexpectedLegacyTrapHitCount=0",
        "unexpectedDiffCount=0",
        "saveSynthesis=false",
        "runtimeExecution=false",
        "beLaunch=false",
        "ghidraMutation=false",
        "executablePatching=false",
        "godotWork=false",
        "rebuildImplementation=false",
        "runtimeObservationRows=0",
        "missionScriptRuntimeEvidenceRows=0",
        "runtimeCommandEffectRows=0",
        "runtimeSaveRows=0",
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
        "missionscript-slot-bitset-save-appcore-copied-baseline-boundary-corpus-harness-proof.md",
        "missionscript-slot-bitset-save-appcore-copied-baseline-boundary-corpus-harness.v1.json",
        f"selectedNextSlice={NEXT_SLICE}",
        "copiedArtifactCount=6",
        "singleSlotCopiedBaselineRoundTripCaseCount=256",
        "copiedBaselineHarnessCaseCount=264",
        "allBoundaryPairSetXorMatchesBaselineState=true",
        "sourceBaselineRead=true",
        "privateArtifactMaterialized=true",
        "runtimeExecution=false",
        "beLaunch=false",
    )
    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX):
        text = read_text(path)
        for token in front_door_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing front-door token: {token}", failures)
        require(
            f"The selected active static-to-proof slice is {THIS_ACTIVE_SLICE}. Status: selected" not in text,
            f"{path.relative_to(ROOT)} still marks copied-baseline boundary corpus harness lane active",
            failures,
        )
        require(
            f"The selected active static-to-proof slice is {NEXT_SLICE}. Status: selected" in text
            or f"active next static child lane: {NEXT_SLICE}" in text
            or f"The selected active static-to-proof slice is {FOLLOWUP_SLICE}. Status: selected" in text
            or f"active next static child lane: {FOLLOWUP_SLICE}" in text,
            f"{path.relative_to(ROOT)} missing active Save / Options AppCore implementation contract or successor lane",
            failures,
        )

    for source, mirror in (
        (BACKLOG, LORE_BACKLOG),
        (MAPPED, LORE_MAPPED),
        (BIN_INDEX, LORE_BIN_INDEX),
        (RE_INDEX, LORE_RE_INDEX),
    ):
        require(read_text(source) == read_text(mirror), f"lore mirror mismatch for {source.relative_to(ROOT)}", failures)


def check_package(failures: list[str]) -> None:
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:missionscript-slot-bitset-save-appcore-copied-baseline-boundary-corpus-harness")
        == r"py -3 tools\missionscript_slot_bitset_save_appcore_copied_baseline_boundary_corpus_harness_probe.py --check",
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
    require(no_bea_process_running(), "BEA.exe process is running after copied-baseline boundary corpus harness proof", failures)
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
            print("MissionScript slot bitset/save AppCore copied-baseline boundary corpus harness proof probe: FAIL")
            for failure in failures:
                print(f"- {failure}")
            return 1
        print("MissionScript slot bitset/save AppCore copied-baseline boundary corpus harness proof probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
