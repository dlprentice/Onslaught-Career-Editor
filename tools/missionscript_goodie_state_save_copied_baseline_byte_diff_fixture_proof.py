#!/usr/bin/env python3
"""Validate MissionScript Goodie-state/save copied-baseline byte-diff proof."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

HARNESS_PROJECT = ROOT / "tools" / "MissionScriptGoodieStateSaveHarness" / "MissionScriptGoodieStateSaveHarness.csproj"
HARNESS_SOURCE = ROOT / "tools" / "MissionScriptGoodieStateSaveHarness" / "Program.cs"
APPCORE_PATCHER = ROOT / "OnslaughtCareerEditor.AppCore" / "BesFilePatcher.cs"

PRIVATE_DIR = ROOT / "subagents" / "static-to-proof" / "missionscript-goodie-state-save-copied-baseline-byte-diff-fixture-proof"
PRIVATE_SUMMARY = PRIVATE_DIR / "evidence-summary.private.json"

PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-goodie-state-save-copied-baseline-byte-diff-fixture-proof.md"
RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-goodie-state-save-copied-baseline-byte-diff-fixture-proof.v1.json"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-goodie-state-save-copied-baseline-byte-diff-fixture-proof.md"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-goodie-state-save-copied-baseline-byte-diff-fixture-proof.v1.json"
READINESS = ROOT / "release" / "readiness" / "missionscript_goodie_state_save_copied_baseline_byte_diff_fixture_proof_2026-06-09.md"

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
GOODIES_DOC = ROOT / "reverse-engineering" / "save-file" / "goodies-system.md"
SAVE_FORMAT = ROOT / "reverse-engineering" / "save-file" / "save-format.md"
PACKAGE_JSON = ROOT / "package.json"

THIS_SLICE = "MissionScript Goodie State / Save Copied-Baseline Byte-Diff Fixture Proof"
THIS_ACTIVE_SLICE = "MissionScript Goodie State / Save Copied-Baseline Byte-Diff Fixture Proof Plan"
THIS_STATUS = "missionscript-goodie-state-save-copied-baseline-byte-diff-fixture-proof-complete-copied-real-baseline-appcore-byte-diff-not-runtime-proof"
PREVIOUS_SLICE = "MissionScript Goodie State / Save Command-Effect Fixture Proof Plan"
PREVIOUS_STATUS = "missionscript-goodie-state-save-command-effect-fixture-proof-plan-complete-static-offset-state-fixture-plan-not-runtime-proof"
NEXT_SLICE = "MissionScript Goodie State / Save Clean-Room Codec Interface Proof Plan"
NEXT_ACTIVE_SLICE = "MissionScript Cutscene Pan-Camera / Position Command-Effect Deterministic Fixture Proof Plan"
COMPLETED_GOODIE_CLEAN_ROOM_SLICE = "MissionScript Goodie State / Save Clean-Room Codec Interface Proof"
COMPLETED_GOODIE_BOUNDARY_SLICE = "MissionScript Goodie State / Save AppCore Copied-Baseline Boundary Corpus Harness Proof"
POST_GOODIE_SELECTION_SLICE = "MissionScript Command-Effect Post-Goodie Selection Refresh Proof Plan"
FIXTURE_FAMILY = "goodie-state-save"
FIXTURE_PATH = "goodie-state-save-index-state-byte-preservation"

EXPECTED_PRIVATE_FILES = {
    "career-goodie-baseline.bes",
    "defaultoptions-goodie-baseline.bea",
    "career-goodie-noop.bes",
    "defaultoptions-goodie-noop.bea",
    "career-goodie-script-boundary-patch.bes",
    "career-goodie-idempotent-patch.bes",
    "career-goodie-roundtrip-original-states.bes",
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
    "game\\",
    "game/",
    '"sourcePath":',
    '"sourcePaths":',
    '"relativePath":',
    '"sha256":',
    "PatchResult.Message",
    "career-goodie-baseline.bes",
    "defaultoptions-goodie-baseline.bea",
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
    "live loose-msl loading proven",
    "packed-resource script selection proven",
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
    goodie_plan = read_json(GOODIE_PLAN_SCHEMA)
    save_copied = read_json(SAVE_COPIED_SCHEMA)

    require(
        goodie_plan["missionScriptGoodieStateSaveCommandEffectFixtureProofPlanStatus"] == PREVIOUS_STATUS,
        "Goodie fixture-plan prerequisite status mismatch",
        failures,
    )
    require(goodie_plan["selectedFixtureFamily"] == FIXTURE_FAMILY, "Goodie fixture family mismatch", failures)
    require(goodie_plan["selectedFixturePath"] == FIXTURE_PATH, "Goodie fixture path mismatch", failures)
    require(goodie_plan["selectedNextSlice"] == THIS_ACTIVE_SLICE, "Goodie fixture next-slice mismatch", failures)
    require(goodie_plan["fixtureAccounting"]["trueViewGoodieBase"] == "0x1F46", "Goodie true-view base mismatch", failures)
    require(save_copied["container"]["expectedSize"] == 10004, "save copied-file prerequisite size mismatch", failures)
    require(save_copied["container"]["versionWord"] == "0x4BD1", "save copied-file prerequisite version mismatch", failures)
    require(save_copied["source"]["sourcePathsPublic"] is False, "save copied-file source disclosure mismatch", failures)


def check_harness_source(failures: list[str]) -> None:
    project = read_text(HARNESS_PROJECT)
    source = read_text(HARNESS_SOURCE)
    patcher = read_text(APPCORE_PATCHER)
    require("ProjectReference Include=\"..\\..\\OnslaughtCareerEditor.AppCore\\OnslaughtCareerEditor.AppCore.csproj\"" in project, "harness project missing AppCore reference", failures)
    for token in (
        "private static readonly int[] ScriptIndices = [1, 51, 53, 68, 71, 233]",
        "int saveIndex = scriptIndex - 1;",
        "BesFilePatcher.PatchGoodieStates(careerBaselinePath, patchedPath, newStatesByIndex)",
        "BesFilePatcher.PatchGoodieStates(patchedPath, idempotentPath, newStatesByIndex)",
        "BesFilePatcher.PatchGoodieStates(patchedPath, roundtripPath, originalStatesByIndex)",
        "new Dictionary<int, uint> { [233] = 3 }",
        "new Dictionary<int, uint> { [0] = 4 }",
        "BesFilePatcher.PatchGoodieStates(careerBaselinePath, rejectedInPlacePath",
        "BesFilePatcher.PatchGoodieStates(careerBaselinePath, rejectedEmptyPath, new Dictionary<int, uint>())",
        "ReservedGoodiesUnchanged = RangeUnchanged(careerBaseline, patched, ReservedGoodiesStart, GoodieEndExclusive)",
        "KillCountersUnchanged = RangeUnchanged(careerBaseline, patched, KillsBase, TechSlotsBase)",
        "OptionsTailUnchanged = RangeUnchanged(careerBaseline, patched, OptionsTailStart, OptionsTailEnd)",
        "RuntimeExecution = false",
        "GodotWork = false",
    ):
        require(token in source, f"harness source missing token: {token}", failures)
    for token in (
        "public static PatchResult PatchGoodieStates",
        "GOODIE_BASE + index * 4",
        "index < 0 || index >= GOODIE_DISPLAYABLE_COUNT",
        "state > GOODIE_OLD",
        "Refusing to patch in place. Please choose a different output path.",
    ):
        require(token in patcher, f"AppCore patcher missing token: {token}", failures)
    for forbidden in ("BinaryPrimitives.WriteUInt32LittleEndian", "Program Files", "steamapps", "BEA.exe.original"):
        require(forbidden not in source, f"harness source contains forbidden token: {forbidden}", failures)


def validate_private_summary(summary: dict[str, Any], failures: list[str], *, check_files: bool) -> None:
    require(summary["schemaVersion"] == "missionscript-goodie-state-save-copied-baseline-byte-diff-private-evidence.v1", "private schema mismatch", failures)
    require(summary["status"] == "PASS", "private status mismatch", failures)

    source = summary["source"]
    for key in ("sourcePathsPublic", "sourceHashesPublic", "artifactPathsPublic", "artifactHashesPublic", "rawBytesPublic"):
        require(source[key] is False, f"private source disclosure guard mismatch: {key}", failures)

    implementation = summary["implementation"]
    require(implementation["appCoreMethod"] == "BesFilePatcher.PatchGoodieStates", "private AppCore method mismatch", failures)
    require(implementation["appCoreServicesUsed"] is True, "private AppCore service guard mismatch", failures)
    require(implementation["productUiWired"] is False, "private product UI guard mismatch", failures)
    require(implementation["harnessFileIo"] is True, "private harness file I/O guard mismatch", failures)
    require(implementation["privateArtifactMaterialized"] is True, "private artifact materialization mismatch", failures)

    provenance = summary["provenance"]
    for key in ("copyBeforeWrite", "sourcesUnderPriorPrivateEvidenceRoot", "outputsUnderProofPrivateEvidenceRoot", "sourceAndOutputPathsDistinct", "careerSourceUnchanged", "defaultOptionsSourceUnchanged"):
        require(provenance[key] is True, f"private provenance mismatch: {key}", failures)
    require(provenance["careerSourceToInputDiffCount"] == 0, "career source-to-input diff mismatch", failures)
    require(provenance["defaultOptionsSourceToInputDiffCount"] == 0, "defaultoptions source-to-input diff mismatch", failures)

    container = summary["container"]
    require(container["expectedSize"] == 10004, "container size mismatch", failures)
    require(container["expectedSizeHex"] == "0x2714", "container size hex mismatch", failures)
    require(container["versionWord"] == "0x4BD1", "container version mismatch", failures)
    require(container["goodieBase"] == "0x1F46", "container Goodie base mismatch", failures)
    require(container["goodieStorageEntryCount"] == 300, "Goodie count mismatch", failures)
    require(container["displayableGoodieCount"] == 233, "displayable Goodie count mismatch", failures)
    require(container["reservedPreserveEntryCount"] == 67, "reserved Goodie count mismatch", failures)
    require(container["allOutputsFileSizePreserved"] is True, "file size preservation mismatch", failures)
    require(container["allOutputsVersionWordPreserved"] is True, "version preservation mismatch", failures)

    analysis = summary["analysis"]
    require(analysis["careerAnalysisValid"] is True, "career analysis validity mismatch", failures)
    require(analysis["goodieStateRowCount"] == 300, "Goodie analysis row count mismatch", failures)
    require(analysis["displayableGoodieCount"] == 233, "displayable analysis count mismatch", failures)
    require(analysis["reservedGoodieCount"] == 67, "reserved analysis count mismatch", failures)

    operation = summary["operation"]
    require(operation["service"] == "BesFilePatcher.PatchGoodieStates", "operation service mismatch", failures)
    require(operation["scriptIndices"] == EXPECTED_SCRIPT_INDICES, "script index vector mismatch", failures)
    require(operation["saveGoodieIndices"] == EXPECTED_SAVE_INDICES, "save index vector mismatch", failures)
    require(operation["targetDwordWriteCount"] == 6, "target write count mismatch", failures)
    require(operation["targetOffsetRanges"] == EXPECTED_RANGES, "target ranges mismatch", failures)
    require(operation["changedOffsets"] == EXPECTED_CHANGED, "changed offset list mismatch", failures)
    require(operation["changedOffsetCount"] == 6, "changed offset count mismatch", failures)
    require(operation["unexpectedDiffCount"] == 0, "unexpected diff count mismatch", failures)
    require(operation["legacyTrapHitCount"] == 0, "legacy trap count mismatch", failures)
    require(operation["allTargetReadbacksMatch"] is True, "target readback mismatch", failures)
    for target, script_index, save_index, offset in zip(operation["targets"], EXPECTED_SCRIPT_INDICES, EXPECTED_SAVE_INDICES, EXPECTED_CHANGED):
        require(target["scriptIndex"] == script_index, f"target script index mismatch: {script_index}", failures)
        require(target["saveGoodieIndex"] == save_index, f"target save index mismatch: {save_index}", failures)
        require(target["fileOffset"] == offset, f"target offset mismatch: {offset}", failures)
        require(target["readbackMatches"] is True, f"target readback mismatch: {offset}", failures)
        require(target["displayable"] is True, f"target displayable guard mismatch: {offset}", failures)

    roundtrip = summary["noOpAndRoundTrip"]
    require(roundtrip["careerNoopDiffCount"] == 0, "career no-op diff mismatch", failures)
    require(roundtrip["defaultOptionsNoopDiffCount"] == 0, "defaultoptions no-op diff mismatch", failures)
    require(roundtrip["patchToIdempotentDiffCount"] == 0, "idempotent diff mismatch", failures)
    require(roundtrip["roundtripToBaselineDiffCount"] == 0, "roundtrip diff mismatch", failures)

    for section, keys in (
        ("preservation", ("nonTargetGoodiesUnchanged", "reservedGoodiesUnchanged", "killCountersUnchanged", "techSlotsUnchanged", "optionsEntriesUnchanged", "optionsTailUnchanged")),
        ("rejections", ("reservedIndex233Rejected", "invalidState4Rejected", "inPlaceRejected", "emptyOverrideRejected")),
    ):
        for key in keys:
            require(summary[section][key] is True, f"{section} guard mismatch: {key}", failures)

    negative = summary["negativeGuards"]
    for key in (
        "saveSynthesis",
        "installedGameMutation",
        "originalExecutableMutation",
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
        require(negative[key] is False, f"negative guard mismatch: {key}", failures)

    artifacts = summary["copiedArtifacts"]
    require(len(artifacts) == 7, "private artifact count mismatch", failures)
    observed_names = {Path(row["relativePath"]).name for row in artifacts}
    require(observed_names == EXPECTED_PRIVATE_FILES, f"private artifact name mismatch: {observed_names}", failures)
    if check_files:
        for name in EXPECTED_PRIVATE_FILES:
            path = PRIVATE_DIR / name
            require(path.is_file(), f"missing private artifact: {name}", failures)
            if path.is_file():
                require(path.stat().st_size == 10004, f"private artifact size mismatch: {name}", failures)


def public_schema_from_private(summary: dict[str, Any]) -> dict[str, Any]:
    operation = summary["operation"]
    return {
        "schemaVersion": "missionscript-goodie-state-save-copied-baseline-byte-diff-fixture-proof.v1",
        "status": "PASS",
        "missionScriptGoodieStateSaveCopiedBaselineByteDiffFixtureProofStatus": THIS_STATUS,
        "previousSlice": PREVIOUS_SLICE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedFixtureFamily": FIXTURE_FAMILY,
        "selectedFixturePath": FIXTURE_PATH,
        "implementation": {
            "toolProjectPath": "tools/MissionScriptGoodieStateSaveHarness/MissionScriptGoodieStateSaveHarness.csproj",
            "appCorePatcherPath": "OnslaughtCareerEditor.AppCore/BesFilePatcher.cs",
            "appCoreService": "BesFilePatcher.PatchGoodieStates",
            "patcherInputIndexClass": "zero-based-save-goodie-index",
            "appCorePatcherUsed": True,
            "harnessFileIo": True,
            "productUiWired": False,
            "privateArtifactMaterialized": True,
            "defaultoptionsGoodieMutation": False,
        },
        "privateEvidence": {
            "privateEvidenceRootPublic": False,
            "sourcePathsPublic": False,
            "sourceHashesPublic": False,
            "artifactPathsPublic": False,
            "artifactHashesPublic": False,
            "rawSaveBytesPublic": False,
            "patchResultMessagePublic": False,
            "copiedRealBesBaselineUsed": True,
            "copiedDefaultOptionsValidationOnly": True,
            "acceptedFixturesDerivedFromCopiedBaselines": True,
            "copiedArtifactCount": 7,
            "copyBeforeWrite": True,
            "outputRootContainedInIgnoredEvidence": True,
            "sourceAndOutputPathsDistinct": True,
            "sourceBaselineMutation": False,
            "sourceBaselineBeforeAfterDiffCount": 0,
            "careerSourceToInputDiffCount": summary["provenance"]["careerSourceToInputDiffCount"],
            "defaultOptionsSourceToInputDiffCount": summary["provenance"]["defaultOptionsSourceToInputDiffCount"],
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
            "expectedSize": summary["container"]["expectedSize"],
            "expectedSizeHex": summary["container"]["expectedSizeHex"],
            "versionWord": summary["container"]["versionWord"],
            "trueViewRule": summary["container"]["trueViewRule"],
            "trueViewGoodieBase": summary["container"]["goodieBase"],
            "goodieStorageEntryCount": summary["container"]["goodieStorageEntryCount"],
            "displayableGoodieCount": summary["container"]["displayableGoodieCount"],
            "reservedPreserveEntryCount": summary["container"]["reservedPreserveEntryCount"],
            "allOutputsFileSizePreserved": summary["container"]["allOutputsFileSizePreserved"],
            "allOutputsVersionWordPreserved": summary["container"]["allOutputsVersionWordPreserved"],
        },
        "indexMapping": {
            "scriptIndexSaveIndexDisambiguated": True,
            "mappingFormula": "save_goodie_index = script_index - 1",
            "offsetFormula": "file_offset = 0x1F46 + save_goodie_index * 4",
            "scriptIndices": operation["scriptIndices"],
            "saveGoodieIndices": operation["saveGoodieIndices"],
            "targetOffsetRanges": operation["targetOffsetRanges"],
            "targetDwordWriteCount": operation["targetDwordWriteCount"],
            "targetReadbackMismatchCount": 0,
        },
        "byteDiff": {
            "changedOffsets": operation["changedOffsets"],
            "changedOffsetCount": operation["changedOffsetCount"],
            "expectedChangedOffsets": EXPECTED_CHANGED,
            "unexpectedDiffCount": operation["unexpectedDiffCount"],
            "legacyTrapHitCount": operation["legacyTrapHitCount"],
            "careerNoopDiffCount": summary["noOpAndRoundTrip"]["careerNoopDiffCount"],
            "defaultOptionsNoopDiffCount": summary["noOpAndRoundTrip"]["defaultOptionsNoopDiffCount"],
            "idempotentDiffCount": summary["noOpAndRoundTrip"]["patchToIdempotentDiffCount"],
            "roundtripToBaselineDiffCount": summary["noOpAndRoundTrip"]["roundtripToBaselineDiffCount"],
        },
        "preservation": summary["preservation"],
        "rejections": {
            "reservedIndexRejection": summary["rejections"]["reservedIndex233Rejected"],
            "invalidStateRejection": summary["rejections"]["invalidState4Rejected"],
            "inPlaceRejection": summary["rejections"]["inPlaceRejected"],
            "emptyOverrideRejection": summary["rejections"]["emptyOverrideRejected"],
        },
        "negativeGuards": {
            **summary["negativeGuards"],
            "syntheticAuthorityBufferUsed": False,
            "defaultoptionsGoodieMutation": False,
        },
        "claimBoundary": {
            "proves": [
                "AppCore PatchGoodieStates can apply selected Goodie state dwords to a copied real career baseline",
                "one-based MissionScript Goodie indices are translated to zero-based save Goodie indices before patching",
                "six selected displayable Goodie dwords change only at expected true-view file offsets",
                "defaultoptions is validated and copied/no-op compared only, not Goodie-mutated",
                "source baselines, reserved Goodies, kill counters, tech slots, options entries, options tail, idempotent patching, and roundtrip restore satisfy the byte-preservation contract",
            ],
            "doesNotProve": [
                "runtime MissionScript execution",
                "runtime command effects",
                "runtime Goodie state mutation",
                "runtime save/load behavior",
                "runtime defaultoptions behavior",
                "runtime Goodies wall behavior",
                "runtime score behavior",
                "live loose-MSL loading",
                "packed-resource script selection",
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
        require(actual["missionScriptGoodieStateSaveCopiedBaselineByteDiffFixtureProofStatus"] == THIS_STATUS, "public status mismatch", failures)
        require(actual["selectedNextSlice"] == NEXT_SLICE, "public next-slice mismatch", failures)
        require(actual["implementation"]["appCoreService"] == "BesFilePatcher.PatchGoodieStates", "public AppCore service mismatch", failures)
        require(actual["implementation"]["patcherInputIndexClass"] == "zero-based-save-goodie-index", "public index-class mismatch", failures)
        require(actual["indexMapping"]["scriptIndexSaveIndexDisambiguated"] is True, "public index-disambiguation mismatch", failures)
        require(actual["privateEvidence"]["sourcePathsPublic"] is False, "public source path disclosure mismatch", failures)
        require(actual["privateEvidence"]["artifactHashesPublic"] is False, "public artifact hash disclosure mismatch", failures)
        require(actual["byteDiff"]["unexpectedDiffCount"] == 0, "public unexpected diff mismatch", failures)
        require(actual["byteDiff"]["roundtripToBaselineDiffCount"] == 0, "public roundtrip mismatch", failures)
        require(actual["negativeGuards"]["runtimeGoodieStateMutationProven"] is False, "public runtime Goodie guard mismatch", failures)
        check_no_public_leaks(path, failures)


def check_docs(failures: list[str]) -> None:
    required_tokens = (
        THIS_SLICE,
        THIS_STATUS,
        PREVIOUS_SLICE,
        NEXT_SLICE,
        "missionscript-goodie-state-save-copied-baseline-byte-diff-fixture-proof.v1.json",
        "toolProjectPath=tools/MissionScriptGoodieStateSaveHarness/MissionScriptGoodieStateSaveHarness.csproj",
        "appCorePatcherPath=OnslaughtCareerEditor.AppCore/BesFilePatcher.cs",
        "appCoreService=BesFilePatcher.PatchGoodieStates",
        "patcherInputIndexClass=zero-based-save-goodie-index",
        "scriptIndexSaveIndexDisambiguated=true",
        "copiedRealBesBaselineUsed=true",
        "copiedDefaultOptionsValidationOnly=true",
        "acceptedFixturesDerivedFromCopiedBaselines=true",
        "privateArtifactMaterialized=true",
        "sourcePathsPublic=false",
        "sourceHashesPublic=false",
        "artifactPathsPublic=false",
        "artifactHashesPublic=false",
        "rawSaveBytesPublic=false",
        "patchResultMessagePublic=false",
        "copyBeforeWrite=true",
        "sourceAndOutputPathsDistinct=true",
        "sourceBaselineBeforeAfterDiffCount=0",
        "expectedSize=10004",
        "versionWord=0x4BD1",
        "trueViewGoodieBase=0x1F46",
        "scriptIndices=1,51,53,68,71,233",
        "saveGoodieIndices=0,50,52,67,70,232",
        "changedOffsets=0x1F46,0x200E,0x2016,0x2052,0x205E,0x22E6",
        "unexpectedDiffCount=0",
        "legacyTrapHitCount=0",
        "targetReadbackMismatchCount=0",
        "careerNoopDiffCount=0",
        "defaultOptionsNoopDiffCount=0",
        "idempotentDiffCount=0",
        "roundtripToBaselineDiffCount=0",
        "reservedGoodiesUnchanged=true",
        "killCountersUnchanged=true",
        "techSlotsUnchanged=true",
        "optionsEntriesUnchanged=true",
        "optionsTailUnchanged=true",
        "reservedIndexRejection=true",
        "invalidStateRejection=true",
        "inPlaceRejection=true",
        "emptyOverrideRejection=true",
        "syntheticAuthorityBufferUsed=false",
        "defaultoptionsGoodieMutation=false",
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
        "missionscript-goodie-state-save-copied-baseline-byte-diff-fixture-proof.md",
        "missionscript-goodie-state-save-copied-baseline-byte-diff-fixture-proof.v1.json",
        "appCoreService=BesFilePatcher.PatchGoodieStates",
        "scriptIndexSaveIndexDisambiguated=true",
        "patcherInputIndexClass=zero-based-save-goodie-index",
        "scriptIndices=1,51,53,68,71,233",
        "saveGoodieIndices=0,50,52,67,70,232",
        "changedOffsets=0x1F46,0x200E,0x2016,0x2052,0x205E,0x22E6",
        "unexpectedDiffCount=0",
        "roundtripToBaselineDiffCount=0",
        f"selectedNextSlice={NEXT_SLICE}",
    )
    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX, MISSION_CONTRACT, GOODIES_DOC, SAVE_FORMAT):
        text = read_text(path)
        for token in front_door_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing front-door token: {token}", failures)
        require(
            f"The selected active static-to-proof slice is {THIS_ACTIVE_SLICE}. Status: selected" not in text,
            f"{path.relative_to(ROOT)} still marks Goodie copied-baseline byte-diff lane as active",
            failures,
        )
        if path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX, GOODIES_DOC, SAVE_FORMAT):
            require(
                f"Completed {COMPLETED_GOODIE_CLEAN_ROOM_SLICE}" in text
                or "missionScriptGoodieStateSaveCleanRoomCodecInterfaceProofStatus=" in text,
                f"{path.relative_to(ROOT)} missing completed Goodie clean-room codec lane",
                failures,
            )
            require(
                f"Completed {COMPLETED_GOODIE_BOUNDARY_SLICE}" in text
                or "missionscript-goodie-state-save-appcore-copied-baseline-boundary-corpus-harness-complete" in text,
                f"{path.relative_to(ROOT)} missing completed Goodie boundary corpus harness lane",
                failures,
            )
            require(
                f"Completed {POST_GOODIE_SELECTION_SLICE}" in text
                or "missionscript-command-effect-post-goodie-selection-refresh-complete-cutscene-camera-position-selected" in text,
                f"{path.relative_to(ROOT)} missing completed post-Goodie selection refresh lane",
                failures,
            )
            require(
                f"Active next static child lane: {NEXT_ACTIVE_SLICE}" in text
                or f"active next static child lane: {NEXT_ACTIVE_SLICE}" in text
                or f"The selected active static-to-proof slice is {NEXT_ACTIVE_SLICE}. Status: selected" in text,
                f"{path.relative_to(ROOT)} missing active cutscene pan-camera/position fixture lane",
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
        scripts.get("test:missionscript-goodie-state-save-copied-baseline-byte-diff-fixture-proof")
        == r"py -3 tools\missionscript_goodie_state_save_copied_baseline_byte_diff_fixture_proof.py --check",
        "missing Goodie copied-baseline byte-diff package script",
        failures,
    )
    for script in (
        "test:missionscript-goodie-state-save-command-effect-fixture-proof-plan",
        "test:save-options-controller-byte-preservation-copied-file",
    ):
        require(script in scripts, f"missing prerequisite package script: {script}", failures)


def run_check() -> list[str]:
    failures: list[str] = []
    check_prerequisites(failures)
    check_harness_source(failures)
    check_public_schema(failures)
    check_docs(failures)
    check_package(failures)
    require(no_bea_process_running(), "BEA.exe process is running after Goodie copied-baseline byte-diff proof", failures)
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
            print("MissionScript Goodie-state/save copied-baseline byte-diff fixture proof probe: FAIL")
            for failure in failures:
                print(f"- {failure}")
            return 1
        print("MissionScript Goodie-state/save copied-baseline byte-diff fixture proof probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
