#!/usr/bin/env python3
"""Validate MissionScript Goodie-state/save AppCore copied-baseline codec harness proof."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

HARNESS_PROJECT = ROOT / "tools" / "MissionScriptGoodieStateSaveCodecHarness" / "MissionScriptGoodieStateSaveCodecHarness.csproj"
HARNESS_SOURCE = ROOT / "tools" / "MissionScriptGoodieStateSaveCodecHarness" / "Program.cs"
APPCORE_CODEC = ROOT / "OnslaughtCareerEditor.AppCore" / "MissionScriptGoodieStateSaveCodec.cs"
APPCORE_TESTS = ROOT / "OnslaughtCareerEditor.AppCore.Tests" / "MissionScriptGoodieStateSaveCodecTests.cs"

PRIVATE_DIR = ROOT / "subagents" / "static-to-proof" / "missionscript-goodie-state-save-appcore-copied-baseline-codec-harness-proof"
PRIVATE_SUMMARY = PRIVATE_DIR / "evidence-summary.private.json"

PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-goodie-state-save-appcore-copied-baseline-codec-harness-proof.md"
RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-goodie-state-save-appcore-copied-baseline-codec-harness.v1.json"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-goodie-state-save-appcore-copied-baseline-codec-harness-proof.md"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-goodie-state-save-appcore-copied-baseline-codec-harness.v1.json"
READINESS = ROOT / "release" / "readiness" / "missionscript_goodie_state_save_appcore_copied_baseline_codec_harness_2026-06-09.md"

CLEAN_ROOM_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-goodie-state-save-clean-room-codec-interface-proof.v1.json"
COPIED_PROOF_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-goodie-state-save-copied-baseline-byte-diff-fixture-proof.v1.json"
GOODIE_PLAN_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-goodie-state-save-command-effect-fixture-proof-plan.v1.json"
SAVE_COPIED_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "save-options-controller-byte-preservation-copied-file.v1.json"

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

THIS_SLICE = "MissionScript Goodie State / Save AppCore Copied-Baseline Codec Harness Proof"
THIS_ACTIVE_SLICE = "MissionScript Goodie State / Save AppCore Copied-Baseline Codec Harness Proof Plan"
THIS_STATUS = "missionscript-goodie-state-save-appcore-copied-baseline-codec-harness-complete-appcore-copied-real-baseline-byte-preservation-not-runtime-proof"
PREVIOUS_SLICE = "MissionScript Goodie State / Save Clean-Room Codec Interface Proof"
PREVIOUS_STATUS = "missionscript-goodie-state-save-clean-room-codec-interface-proof-complete-pure-appcore-buffer-codec-not-runtime-proof"
NEXT_SLICE = "MissionScript Goodie State / Save Runtime-Proof Readiness Gate Plan"
FIXTURE_FAMILY = "goodie-state-save"
FIXTURE_PATH = "goodie-state-save-index-state-byte-preservation"

EXPECTED_PRIVATE_FILES = {
    "career-goodie-codec-baseline.bes",
    "defaultoptions-goodie-codec-baseline.bea",
    "career-goodie-codec-noop.bes",
    "defaultoptions-goodie-codec-noop.bea",
    "career-goodie-codec-script-boundary-set.bes",
    "career-goodie-codec-idempotent-set.bes",
    "career-goodie-codec-roundtrip-original-states.bes",
}

EXPECTED_SCRIPT_INDICES = [1, 51, 53, 68, 71, 233]
EXPECTED_SAVE_INDICES = [0, 50, 52, 67, 70, 232]
EXPECTED_RANGES = ["0x1F46-0x1F49", "0x200E-0x2011", "0x2016-0x2019", "0x2052-0x2055", "0x205E-0x2061", "0x22E6-0x22E9"]
EXPECTED_CHANGED = ["0x1F46", "0x200E", "0x2016", "0x2052", "0x205E", "0x22E6"]

PUBLIC_FORBIDDEN_TOKENS = (
    "C:\\Users",
    "Program Files",
    "steamapps",
    "save-attempts",
    "subagents/",
    "subagents\\",
    '"relativePath":',
    '"sha256":',
    "career-goodie-codec-",
    "defaultoptions-goodie-codec-",
    "HWND",
    "window handle",
    "process id",
    "onslaught_codex_directive",
    "password",
    "token=",
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
    "godot parity proven",
    "ghidra mutation complete",
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
    clean = read_json(CLEAN_ROOM_SCHEMA)
    copied = read_json(COPIED_PROOF_SCHEMA)
    goodie_plan = read_json(GOODIE_PLAN_SCHEMA)
    save = read_json(SAVE_COPIED_SCHEMA)

    require(clean["missionScriptGoodieStateSaveCleanRoomCodecInterfaceProofStatus"] == PREVIOUS_STATUS, "clean-room prerequisite status mismatch", failures)
    require(clean["selectedNextSlice"] == THIS_ACTIVE_SLICE, "clean-room prerequisite next-slice mismatch", failures)
    require(clean["implementation"]["interfaceKind"] == "pure AppCore in-memory buffer codec", "clean-room interface kind mismatch", failures)
    require(clean["implementation"]["appCoreCodecUsed"] is True, "clean-room codec-use guard mismatch", failures)
    require(clean["implementation"]["appCorePatcherUsed"] is False, "clean-room patcher-use guard mismatch", failures)
    require(copied["missionScriptGoodieStateSaveCopiedBaselineByteDiffFixtureProofStatus"].endswith("not-runtime-proof"), "copied-baseline prerequisite mismatch", failures)
    require(copied["selectedNextSlice"] == "MissionScript Goodie State / Save Clean-Room Codec Interface Proof Plan", "copied-baseline next-slice mismatch", failures)
    require(copied["byteDiff"]["changedOffsets"] == EXPECTED_CHANGED, "copied-baseline changed offsets mismatch", failures)
    require(copied["byteDiff"]["unexpectedDiffCount"] == 0, "copied-baseline unexpected diff mismatch", failures)
    require(copied["negativeGuards"]["runtimeExecution"] is False, "copied-baseline runtime guard mismatch", failures)
    require(goodie_plan["selectedFixtureFamily"] == FIXTURE_FAMILY, "Goodie fixture family mismatch", failures)
    require(goodie_plan["selectedFixturePath"] == FIXTURE_PATH, "Goodie fixture path mismatch", failures)
    require(save["container"]["expectedSize"] == 10004, "save prerequisite size mismatch", failures)
    require(save["container"]["versionWord"] == "0x4BD1", "save prerequisite version mismatch", failures)


def check_harness_source(failures: list[str]) -> None:
    project = read_text(HARNESS_PROJECT)
    source = read_text(HARNESS_SOURCE)
    codec = read_text(APPCORE_CODEC)
    tests = read_text(APPCORE_TESTS)
    require("ProjectReference Include=\"..\\..\\OnslaughtCareerEditor.AppCore\\OnslaughtCareerEditor.AppCore.csproj\"" in project, "harness project missing AppCore reference", failures)
    for token in (
        "MissionScriptGoodieStateSaveCodec.SetDisplayableStatesByScriptIndex(patched, newStatesByScriptIndex)",
        "MissionScriptGoodieStateSaveCodec.SetDisplayableStatesByScriptIndex(idempotent, newStatesByScriptIndex)",
        "MissionScriptGoodieStateSaveCodec.SetDisplayableStatesByScriptIndex(roundtrip, originalStatesByScriptIndex)",
        "MissionScriptGoodieStateSaveCodec.GetStateByScriptIndex(patched, target.ScriptIndex)",
        "MissionScriptGoodieStateSaveCodec.GetDisplayableVectorFromScriptIndex(scriptIndex)",
        "AppCoreCodecUsed = true",
        "AppCorePatcherUsed = false",
        "ManualGoodieDwordWriteInHarness = false",
        "AppCoreCodecFileIo = false",
    ):
        require(token in source, f"harness source missing AppCore token: {token}", failures)
    for forbidden in (
        "BinaryPrimitives.WriteUInt32LittleEndian",
        "BesFilePatcher.PatchGoodieStates",
        "Program Files",
        "steamapps",
        "BEA.exe",
    ):
        require(forbidden not in source, f"harness source contains forbidden token: {forbidden}", failures)
    require("File." not in codec, "AppCore codec gained file I/O", failures)
    require("public static MissionScriptGoodieStateVector[] SetDisplayableStatesByScriptIndex" in codec, "AppCore codec missing batch setter", failures)
    require("MissionScriptGoodieStateSaveCodecTests" in tests, "AppCore tests missing codec test class", failures)


def validate_private_summary(summary: dict[str, Any], failures: list[str], check_files: bool) -> None:
    require(summary["schemaVersion"] == "missionscript-goodie-state-save-appcore-copied-baseline-codec-harness-private-evidence.v1", "private schema mismatch", failures)
    require(summary["status"] == "PASS", "private status mismatch", failures)
    source = summary["source"]
    for key in ("sourcePathsPublic", "sourceHashesPublic", "artifactPathsPublic", "artifactHashesPublic", "rawBytesPublic"):
        require(source[key] is False, f"private source disclosure guard mismatch: {key}", failures)
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
    require(container["goodieStorageEntryCount"] == 300, "Goodie count mismatch", failures)
    require(container["displayableGoodieCount"] == 233, "displayable Goodie count mismatch", failures)
    require(container["reservedPreserveEntryCount"] == 67, "reserved Goodie count mismatch", failures)
    require(container["fileSizePreserved"] is True, "file-size preservation mismatch", failures)
    require(container["versionWordPreserved"] is True, "version preservation mismatch", failures)
    operation = summary["operation"]
    require(operation["scriptIndexing"] == "1-based", "script indexing mismatch", failures)
    require(operation["scriptIndices"] == EXPECTED_SCRIPT_INDICES, "script indices mismatch", failures)
    require(operation["saveGoodieIndices"] == EXPECTED_SAVE_INDICES, "save indices mismatch", failures)
    require(operation["targetOffsetRanges"] == EXPECTED_RANGES, "target ranges mismatch", failures)
    require(operation["changedOffsets"] == EXPECTED_CHANGED, "changed offsets mismatch", failures)
    require(operation["changedOffsetCount"] == 6, "changed offset count mismatch", failures)
    require(operation["unexpectedDiffCount"] == 0, "unexpected diff count mismatch", failures)
    require(operation["legacyTrapHitCount"] == 0, "legacy trap count mismatch", failures)
    require(operation["allTargetReadbacksMatch"] is True, "target readback mismatch", failures)
    require(len(operation["targets"]) == 6, "target row count mismatch", failures)
    roundtrip = summary["noOpAndRoundTrip"]
    for key in ("careerNoopDiffCount", "defaultOptionsNoopDiffCount", "patchToIdempotentDiffCount", "roundtripToBaselineDiffCount"):
        require(roundtrip[key] == 0, f"roundtrip mismatch: {key}", failures)
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
    require(summary["negativeGuards"]["legacyTrapHitCount"] == 0, "legacy trap guard mismatch", failures)

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
    return {
        "schemaVersion": "missionscript-goodie-state-save-appcore-copied-baseline-codec-harness.v1",
        "status": "PASS",
        "goodieStateSaveAppCoreCopiedBaselineCodecHarnessStatus": THIS_STATUS,
        "previousSlice": PREVIOUS_SLICE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedFixtureFamily": FIXTURE_FAMILY,
        "selectedFixturePath": FIXTURE_PATH,
        "implementation": {
            "toolProjectPath": "tools/MissionScriptGoodieStateSaveCodecHarness/MissionScriptGoodieStateSaveCodecHarness.csproj",
            "appCoreCodecPath": "OnslaughtCareerEditor.AppCore/MissionScriptGoodieStateSaveCodec.cs",
            "interfaceKind": "AppCore Goodie codec applied by proof-only copied-baseline harness",
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
            "copiedArtifactCount": 7,
            "copiedDefaultOptionsValidationOnly": True,
            "copyBeforeWrite": True,
            "sourceAndOutputPathsDistinct": True,
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
            "fileSizePreserved": summary["container"]["fileSizePreserved"],
            "versionWordPreserved": summary["container"]["versionWordPreserved"],
        },
        "operation": {
            "scriptIndexing": "1-based",
            "mappingFormula": "save_goodie_index = script_index - 1",
            "offsetFormula": "0x1F46 + (script_index - 1) * 4",
            "reservedWritePolicy": "displayable-only-default-rejects-reserved",
            "scriptIndices": summary["operation"]["scriptIndices"],
            "saveGoodieIndices": summary["operation"]["saveGoodieIndices"],
            "targetOffsetRanges": summary["operation"]["targetOffsetRanges"],
            "targetDwordWriteCount": summary["operation"]["targetDwordWriteCount"],
            "changedOffsets": summary["operation"]["changedOffsets"],
            "changedOffsetCount": summary["operation"]["changedOffsetCount"],
            "unexpectedDiffCount": summary["operation"]["unexpectedDiffCount"],
            "legacyTrapHitCount": summary["operation"]["legacyTrapHitCount"],
            "targetReadbackMismatchCount": 0,
            "allTargetReadbacksMatch": summary["operation"]["allTargetReadbacksMatch"],
        },
        "noOpAndRoundTrip": summary["noOpAndRoundTrip"],
        "preservation": summary["preservation"],
        "rejections": summary["rejections"],
        "negativeGuards": summary["negativeGuards"],
        "claimBoundary": {
            "proves": [
                "the proof-only C# harness applies MissionScriptGoodieStateSaveCodec to copied real career/defaultoptions baselines",
                "one-based MissionScript Goodie script indices map to zero-based save Goodie indices through the AppCore codec",
                "six selected displayable Goodie dwords change only at expected true-view file offsets",
                "the AppCore codec readback path confirms all selected target states after mutation",
                "copied source preservation, no-op, idempotent, roundtrip, reserved Goodie, kill counter, tech slot, options entry, options tail, and rejection guards satisfy the byte-preservation contract",
            ],
            "doesNotProve": [
                "runtime MissionScript execution",
                "runtime command effects",
                "runtime Goodie state mutation",
                "runtime save/load behavior",
                "runtime defaultoptions behavior",
                "runtime Goodies wall behavior",
                "runtime score behavior",
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
        require(actual["goodieStateSaveAppCoreCopiedBaselineCodecHarnessStatus"] == THIS_STATUS, "public status mismatch", failures)
        require(actual["selectedNextSlice"] == NEXT_SLICE, "public next-slice mismatch", failures)
        require(actual["implementation"]["appCoreCodecUsed"] is True, "public AppCore codec use mismatch", failures)
        require(actual["implementation"]["appCorePatcherUsed"] is False, "public patcher guard mismatch", failures)
        require(actual["implementation"]["manualGoodieDwordWriteInHarness"] is False, "public manual write guard mismatch", failures)
        require(actual["privateEvidence"]["sourcePathsPublic"] is False, "public source disclosure mismatch", failures)
        require(actual["privateEvidence"]["artifactHashesPublic"] is False, "public hash disclosure mismatch", failures)
        require(actual["operation"]["changedOffsets"] == EXPECTED_CHANGED, "public changed offset mismatch", failures)
        require(actual["operation"]["targetReadbackMismatchCount"] == 0, "public readback mismatch", failures)
        require(actual["negativeGuards"]["runtimeGoodieStateMutationProven"] is False, "public runtime Goodie guard mismatch", failures)
        check_no_public_leaks(path, failures)


def check_docs(failures: list[str]) -> None:
    required_tokens = (
        THIS_SLICE,
        THIS_STATUS,
        PREVIOUS_SLICE,
        NEXT_SLICE,
        "missionscript-goodie-state-save-appcore-copied-baseline-codec-harness.v1.json",
        "toolProjectPath=tools/MissionScriptGoodieStateSaveCodecHarness/MissionScriptGoodieStateSaveCodecHarness.csproj",
        "appCoreCodecPath=OnslaughtCareerEditor.AppCore/MissionScriptGoodieStateSaveCodec.cs",
        "interfaceKind=AppCore Goodie codec applied by proof-only copied-baseline harness",
        "appCoreCodecUsed=true",
        "appCorePatcherUsed=false",
        "manualGoodieDwordWriteInHarness=false",
        "appCoreCodecFileIo=false",
        "harnessFileIo=true",
        "productUiWired=false",
        "sourceBaselineRead=true",
        "privateArtifactMaterialized=true",
        "copiedArtifactCount=7",
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
        "fileSizePreserved=true",
        "versionWordPreserved=true",
        "scriptIndexing=1-based",
        "mappingFormula=save_goodie_index = script_index - 1",
        "offsetFormula=0x1F46 + (script_index - 1) * 4",
        "reservedWritePolicy=displayable-only-default-rejects-reserved",
        "scriptIndices=1,51,53,68,71,233",
        "saveGoodieIndices=0,50,52,67,70,232",
        "changedOffsets=0x1F46,0x200E,0x2016,0x2052,0x205E,0x22E6",
        "unexpectedDiffCount=0",
        "legacyTrapHitCount=0",
        "targetReadbackMismatchCount=0",
        "careerNoopDiffCount=0",
        "defaultOptionsNoopDiffCount=0",
        "patchToIdempotentDiffCount=0",
        "roundtripToBaselineDiffCount=0",
        "nonTargetGoodiesUnchanged=true",
        "reservedGoodiesUnchanged=true",
        "killCountersUnchanged=true",
        "techSlotsUnchanged=true",
        "optionsEntriesUnchanged=true",
        "optionsTailUnchanged=true",
        "reservedIndex234Rejected=true",
        "invalidState4Rejected=true",
        "emptyOverrideRejected=true",
        "invalidMixedBatchLeavesBufferUnchanged=true",
        "wrongSizeRejected=true",
        "wrongVersionRejected=true",
        "saveSynthesis=false",
        "defaultoptionsMutation=false",
        "runtimeExecution=false",
        "runtimeGoodieStateMutationProven=false",
        "runtimeSaveBehaviorProven=false",
        "ghidraMutation=false",
        "executablePatching=false",
        "godotWork=false",
        "productUiWired=false",
        "rebuildImplementation=false",
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
        "missionscript-goodie-state-save-appcore-copied-baseline-codec-harness-proof.md",
        "missionscript-goodie-state-save-appcore-copied-baseline-codec-harness.v1.json",
        "appCoreCodecUsed=true",
        "appCorePatcherUsed=false",
        "manualGoodieDwordWriteInHarness=false",
        "changedOffsets=0x1F46,0x200E,0x2016,0x2052,0x205E,0x22E6",
        "targetReadbackMismatchCount=0",
        "roundtripToBaselineDiffCount=0",
        f"selectedNextSlice={NEXT_SLICE}",
    )
    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX, MISSION_CONTRACT, GOODIES_DOC, SAVE_FORMAT):
        text = read_text(path)
        for token in front_door_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing front-door token: {token}", failures)
        require(
            f"The selected active static-to-proof slice is {THIS_ACTIVE_SLICE}. Status: selected" not in text,
            f"{path.relative_to(ROOT)} still marks Goodie AppCore copied-baseline harness lane as active",
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
        scripts.get("test:missionscript-goodie-state-save-appcore-copied-baseline-codec-harness")
        == r"py -3 tools\missionscript_goodie_state_save_appcore_copied_baseline_codec_harness_probe.py --check",
        "missing AppCore copied-baseline Goodie codec harness package script",
        failures,
    )
    for script in (
        "test:missionscript-goodie-state-save-clean-room-codec-interface",
        "test:missionscript-goodie-state-save-copied-baseline-byte-diff-fixture-proof",
        "test:missionscript-goodie-state-save-command-effect-fixture-proof-plan",
    ):
        require(script in scripts, f"missing prerequisite package script: {script}", failures)


def run_check() -> list[str]:
    failures: list[str] = []
    check_prerequisites(failures)
    check_harness_source(failures)
    check_public_schema(failures)
    check_docs(failures)
    check_package(failures)
    require(no_bea_process_running(), "BEA.exe process is running after Goodie AppCore copied-baseline codec harness proof", failures)
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
            print("MissionScript Goodie-state/save AppCore copied-baseline codec harness proof probe: FAIL")
            for failure in failures:
                print(f"- {failure}")
            return 1
        print("MissionScript Goodie-state/save AppCore copied-baseline codec harness proof probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
