#!/usr/bin/env python3
"""Validate Save / Options AppCore fixture-matrix proof artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

HARNESS_PROJECT = ROOT / "tools" / "SaveOptionsAppCoreFixtureMatrixHarness" / "SaveOptionsAppCoreFixtureMatrixHarness.csproj"
HARNESS_SOURCE = ROOT / "tools" / "SaveOptionsAppCoreFixtureMatrixHarness" / "Program.cs"
APP_TEST = ROOT / "OnslaughtCareerEditor.AppCore.Tests" / "AppCoreSaveOptionsContractTests.cs"
SAVE_PATCHER = ROOT / "OnslaughtCareerEditor.AppCore" / "BesFilePatcher.cs"
SAVE_EDITOR = ROOT / "OnslaughtCareerEditor.AppCore" / "SaveEditorService.cs"
CONFIG_EDITOR = ROOT / "OnslaughtCareerEditor.AppCore" / "ConfigurationEditorService.cs"
SLOT_CODEC = ROOT / "OnslaughtCareerEditor.AppCore" / "MissionScriptSlotBitsetSaveCodec.cs"

PRIVATE_DIR = ROOT / "subagents" / "static-to-proof" / "save-options-byte-preservation-appcore-fixture-matrix-proof"
PRIVATE_SUMMARY = PRIVATE_DIR / "fixture-matrix-summary.private.json"

RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "save-options-byte-preservation-appcore-fixture-matrix.v1.json"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "save-options-byte-preservation-appcore-fixture-matrix.v1.json"
PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "save-options-byte-preservation-appcore-fixture-matrix-proof.md"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "save-options-byte-preservation-appcore-fixture-matrix-proof.md"
READINESS = ROOT / "release" / "readiness" / "save_options_byte_preservation_appcore_fixture_matrix_2026-06-09.md"

RUNTIME_GATE = ROOT / "reverse-engineering" / "binary-analysis" / "save-options-byte-preservation-runtime-proof-readiness-gate.v1.json"
IMPLEMENTATION_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "save-options-byte-preservation-appcore-implementation-contract.v1.json"
BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
LORE_MAPPED = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
LORE_BIN_INDEX = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
LORE_RE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"
SAVE_INDEX = ROOT / "reverse-engineering" / "save-file" / "_index.md"
LORE_SAVE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "save-file" / "_index.md"
SAVE_FORMAT = ROOT / "reverse-engineering" / "save-file" / "save-format.md"
LORE_SAVE_FORMAT = ROOT / "lore-book" / "reverse-engineering" / "save-file" / "save-format.md"
PACKAGE_JSON = ROOT / "package.json"

STATUS = "save-options-byte-preservation-appcore-fixture-matrix-complete-copied-real-baseline-services-not-runtime-proof"
PREVIOUS_SLICE = "Save / Options Byte-Preservation Runtime-Proof Readiness Gate"
NEXT_SLICE = "Static-To-Proof Rebuild Transition Next Safe Slice Selection Refresh Proof Plan"
RESULT_NAME = "save-options-byte-preservation-appcore-fixture-matrix.v1.json"
PROOF_NAME = "save-options-byte-preservation-appcore-fixture-matrix-proof.md"

EXPECTED_FAMILY_COUNTS = {
    "container-analyzer": 2,
    "career-kills": 5,
    "kill-boundaries": 3,
    "defaultoptions-settings": 10,
    "options-copy": 4,
    "controller-keybinds": 4,
    "slot-bitset": 4,
    "rejections-noop-legacy": 4,
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
    "fixture-matrix-summary.private",
    "password",
    "token=",
)

FORBIDDEN_OVERCLAIMS = (
    "runtime save/load behavior proven",
    "runtime defaultoptions boot behavior proven",
    "runtime menu behavior proven",
    "runtime controller remap/input behavior proven",
    "runtime goodies wall behavior proven",
    "installed game mutation proven",
    "original executable mutation proven",
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


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def version_word(data: bytes) -> str:
    return f"0x{int.from_bytes(data[:2], 'little'):04X}"


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


def validate_private_summary(summary: dict[str, Any], failures: list[str], check_files: bool) -> None:
    require(summary.get("schemaVersion") == "save-options-byte-preservation-appcore-fixture-matrix-private-evidence.v1", "private schema mismatch", failures)
    require(summary.get("status") == "PASS", "private status mismatch", failures)

    for key in ("sourcePathsPublic", "sourceHashesPublic", "artifactPathsPublic", "artifactHashesPublic", "rawBytesPublic"):
        require(summary["source"][key] is False, f"private disclosure guard mismatch: {key}", failures)

    implementation = summary["implementation"]
    require(implementation["toolProjectPath"] == "tools/SaveOptionsAppCoreFixtureMatrixHarness/SaveOptionsAppCoreFixtureMatrixHarness.csproj", "harness project path mismatch", failures)
    require(implementation["appCoreServicesUsed"] is True, "AppCore service-use mismatch", failures)
    require(implementation["productUiWired"] is False, "product UI guard mismatch", failures)
    require(implementation["harnessFileIo"] is True, "harness file-I/O mismatch", failures)
    require(implementation["privateArtifactMaterialized"] is True, "private materialization mismatch", failures)

    provenance = summary["provenance"]
    for key in ("copyBeforeWrite", "sourcesUnderPriorPrivateEvidenceRoot", "outputsUnderProofPrivateEvidenceRoot", "careerSourceUnchanged", "defaultOptionsSourceUnchanged"):
        require(provenance[key] is True, f"provenance mismatch: {key}", failures)
    require(provenance["careerSourceToInputDiffCount"] == 0, "career source copy diff mismatch", failures)
    require(provenance["defaultOptionsSourceToInputDiffCount"] == 0, "defaultoptions source copy diff mismatch", failures)

    container = summary["container"]
    require(container["expectedSize"] == 10004, "expected size mismatch", failures)
    require(container["versionWord"] == "0x4BD1", "version word mismatch", failures)
    require(container["trueViewRule"] == "file_offset = 0x0002 + career_offset", "true-view rule mismatch", failures)
    require(container["careerSlotsBase"] == "0x240A", "slot base mismatch", failures)
    require(container["careerSlotsEndExclusive"] == "0x248A", "slot end mismatch", failures)
    require(container["optionsEntriesRange"] == "0x24BE-0x26BD", "options entries range mismatch", failures)
    require(container["optionsTailRange"] == "0x26BE-0x2713", "options tail range mismatch", failures)
    require(container["allOutputsFileSizePreserved"] is True, "output size preservation mismatch", failures)
    require(container["allOutputsVersionWordPreserved"] is True, "output version preservation mismatch", failures)

    matrix = summary["matrix"]
    require(matrix["fixtureFamilyCount"] == 8, "fixture family count mismatch", failures)
    require(matrix["appCoreFixtureCaseCount"] == 36, "fixture case count mismatch", failures)
    require(matrix["outputCaseCount"] == 29, "output case count mismatch", failures)
    require(matrix["rejectionCaseCount"] == 5, "rejection case count mismatch", failures)
    require(matrix["noOpCaseCount"] == 1, "no-op case count mismatch", failures)
    require(matrix["noOpDiffCount"] == 0, "no-op diff count mismatch", failures)
    require(matrix["unexpectedDiffCount"] == 0, "unexpected diff count mismatch", failures)
    require(matrix["legacyTrapHitCountNonSlot"] == 0, "non-slot legacy trap mismatch", failures)
    require(matrix["allRejectionsOutputNotCreated"] is True, "rejection output guard mismatch", failures)
    require(matrix["keybindDiffsWithinOptionsEntriesAndTailControlScheme"] is True, "keybind diff-range guard mismatch", failures)
    require(matrix["slotRoundTripCaseCount"] == 4, "slot roundtrip count mismatch", failures)
    require(matrix["derivedInvalidFixtureCount"] == 2, "derived invalid fixture count mismatch", failures)

    cases = summary["cases"]
    require(len(cases) == 36, "private case row count mismatch", failures)
    for family, expected in EXPECTED_FAMILY_COUNTS.items():
        require(sum(1 for row in cases if row["family"] == family) == expected, f"case family count mismatch: {family}", failures)
    for row in cases:
        require(row["status"] == "PASS", f"case did not pass: {row['name']}", failures)
        require(row["unexpectedDiffCount"] == 0, f"case unexpected diff mismatch: {row['name']}", failures)
    require(any(row["name"] == "options-copy-same-source-noop" and row["noOpDiffCount"] == 0 for row in cases), "missing same-source no-op diff guard", failures)
    require(any(row["name"] == "keybind-invalid-token-rejected" and row["rejectionCase"] is True for row in cases), "missing invalid keybind rejection", failures)
    require(sum(1 for row in cases if row["rejectionCase"] is True and row["outputCreatedAfterRejection"] is False) == 5, "rejection output-created guard mismatch", failures)

    for key in (
        "saveSynthesis",
        "installedGameMutation",
        "originalExecutableMutation",
        "runtimeExecution",
        "beLaunch",
        "newLaunch",
        "screenshotCapture",
        "nativeInput",
        "debuggerAttachment",
        "copiedExecutablePatchApplied",
        "binaryPatchEngineUsed",
        "patchCatalogTouched",
        "ghidraMutation",
        "executablePatching",
        "godotWork",
        "productUiWired",
        "rebuildImplementation",
        "runtimeSaveLoadProof",
        "runtimeDefaultOptionsProof",
    ):
        require(summary["negativeGuards"][key] is False, f"negative guard mismatch: {key}", failures)

    if not check_files:
        return
    for row in summary["copiedArtifacts"]:
        path = ROOT / row["relativePath"]
        require(path.is_file(), f"missing private artifact file: {row['relativePath']}", failures)
        if path.is_file():
            data = path.read_bytes()
            require(len(data) == row["size"], f"private artifact size mismatch: {row['relativePath']}", failures)
            require(version_word(data) == row["versionWord"], f"private artifact version mismatch: {row['relativePath']}", failures)
            require(sha256(data) == row["sha256"], f"private artifact hash mismatch: {row['relativePath']}", failures)


def public_schema_from_private(summary: dict[str, Any]) -> dict[str, Any]:
    matrix = summary["matrix"]
    return {
        "schemaVersion": "save-options-byte-preservation-appcore-fixture-matrix.v1",
        "status": "PASS",
        "saveOptionsBytePreservationAppCoreFixtureMatrixStatus": STATUS,
        "previousSlice": PREVIOUS_SLICE,
        "selectedNextSlice": NEXT_SLICE,
        "implementation": {
            "toolProjectPath": summary["implementation"]["toolProjectPath"],
            "appCoreSavePatchPath": summary["implementation"]["appCoreSavePatchPath"],
            "saveEditorServicePath": summary["implementation"]["saveEditorServicePath"],
            "configurationEditorServicePath": summary["implementation"]["configurationEditorServicePath"],
            "slotCodecPath": summary["implementation"]["slotCodecPath"],
            "appCoreServicesUsed": True,
            "productUiWired": False,
            "harnessFileIo": True,
            "privateArtifactMaterialized": True,
        },
        "privateEvidence": {
            "sourcePathsPublic": False,
            "sourceHashesPublic": False,
            "artifactPathsPublic": False,
            "artifactHashesPublic": False,
            "rawBytesPublic": False,
            "copiedRealBaselineClass": "validated copied real career .bes and defaultoptions.bea baselines from prior ignored evidence",
            "copiedArtifactCount": len(summary["copiedArtifacts"]),
            "copyBeforeWrite": True,
            "careerSourceUnchanged": True,
            "defaultOptionsSourceUnchanged": True,
            "careerSourceToInputDiffCount": 0,
            "defaultOptionsSourceToInputDiffCount": 0,
            "acceptedFixturesDerivedFromCopiedBaselines": True,
            "invalidFixturesRejectionOnly": True,
            "derivedInvalidFixtureCount": matrix["derivedInvalidFixtureCount"],
        },
        "container": {
            "expectedSize": 10004,
            "expectedSizeHex": "0x2714",
            "versionWord": "0x4BD1",
            "trueViewRule": "file_offset = 0x0002 + career_offset",
            "careerSlotsBase": "0x240A",
            "careerSlotsEndExclusive": "0x248A",
            "optionsEntriesRange": "0x24BE-0x26BD",
            "optionsTailRange": "0x26BE-0x2713",
            "allOutputsFileSizePreserved": True,
            "allOutputsVersionWordPreserved": True,
        },
        "matrix": {
            "fixtureFamilyCount": matrix["fixtureFamilyCount"],
            "appCoreFixtureCaseCount": matrix["appCoreFixtureCaseCount"],
            "outputCaseCount": matrix["outputCaseCount"],
            "rejectionCaseCount": matrix["rejectionCaseCount"],
            "noOpCaseCount": matrix["noOpCaseCount"],
            "noOpDiffCount": matrix["noOpDiffCount"],
            "unexpectedDiffCount": matrix["unexpectedDiffCount"],
            "legacyTrapHitCountNonSlot": matrix["legacyTrapHitCountNonSlot"],
            "allRejectionsOutputNotCreated": matrix["allRejectionsOutputNotCreated"],
            "keybindDiffsWithinOptionsEntriesAndTailControlScheme": matrix["keybindDiffsWithinOptionsEntriesAndTailControlScheme"],
            "slotRoundTripCaseCount": matrix["slotRoundTripCaseCount"],
        },
        "familyCoverage": {
            "containerAnalyzerCaseCount": matrix["containerAnalyzerCaseCount"],
            "careerKillCategoryCaseCount": matrix["careerKillCategoryCaseCount"],
            "killBoundaryCaseCount": matrix["killBoundaryCaseCount"],
            "defaultOptionsSettingCaseCount": matrix["defaultOptionsSettingCaseCount"],
            "optionsCopyCaseCount": matrix["optionsCopyCaseCount"],
            "controllerKeybindCaseCount": matrix["controllerKeybindCaseCount"],
            "slotBitsetCaseCount": matrix["slotBitsetCaseCount"],
            "rejectionNoOpLegacyCaseCount": matrix["rejectionNoOpLegacyCaseCount"],
        },
        "caseAnchors": [
            "career-kill-aircraft",
            "career-kill-vehicles",
            "career-kill-emplacements",
            "career-kill-infantry",
            "career-kill-mechs",
            "kill-negative-clamps-zero",
            "kill-zero-boundary",
            "kill-overflow-clamps-max",
            "sound-volume",
            "music-volume",
            "walker-invert-p1",
            "walker-invert-p2",
            "flight-invert-p1",
            "flight-invert-p2",
            "vibration-p1",
            "vibration-p2",
            "controller-config-p1",
            "controller-config-p2",
            "options-copy-entries-only",
            "options-copy-tail-only",
            "options-copy-combined",
            "options-copy-same-source-noop",
            "keybind-look-mousex",
            "keybind-zoom-wheel",
            "keybind-fire-mouseleft-mirror",
            "keybind-invalid-token-rejected",
            "slot-bitset-pair-0-31",
            "slot-bitset-pair-32-63",
            "slot-bitset-pair-128-159",
            "slot-bitset-pair-224-255",
            "save-no-selected-sections-rejected",
            "config-no-pending-rejected",
            "wrong-size-derived-rejected",
            "wrong-version-derived-rejected",
        ],
        "negativeGuards": {
            "saveSynthesis": False,
            "installedGameMutation": False,
            "originalExecutableMutation": False,
            "runtimeExecution": False,
            "beLaunch": False,
            "newLaunch": False,
            "screenshotCapture": False,
            "nativeInput": False,
            "debuggerAttachment": False,
            "copiedExecutablePatchApplied": False,
            "binaryPatchEngineUsed": False,
            "patchCatalogTouched": False,
            "ghidraMutation": False,
            "executablePatching": False,
            "godotWork": False,
            "productUiWired": False,
            "rebuildImplementation": False,
            "runtimeSaveLoadProof": False,
            "runtimeDefaultOptionsProof": False,
            "publicLeakCheck": "PASS",
        },
        "claimBoundary": {
            "proves": [
                "Copied-real-baseline AppCore save/options fixture matrix coverage across eight bounded families",
                "All five kill categories stay inside their true-view lower-24 payload bytes while preserving metadata",
                "Defaultoptions scalar/controller/keybind/options-copy cases stay inside expected true-view fields or options ranges",
                "Representative copied-baseline slot-bitset cases round-trip inside expected saved dwords",
                "No-op and rejection cases are bounded and do not create unintended outputs",
            ],
            "doesNotProve": [
                "runtime save/load behavior",
                "runtime defaultoptions boot behavior",
                "runtime menu behavior",
                "runtime controller remap/input behavior",
                "runtime Goodies wall behavior",
                "installed game mutation",
                "original executable mutation",
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


def check_no_public_leaks(path: Path, failures: list[str]) -> None:
    text = read_text(path)
    lower = text.lower()
    for token in PUBLIC_FORBIDDEN_TOKENS:
        require(token.lower() not in lower, f"{path.relative_to(ROOT)} leaks forbidden public token: {token}", failures)
    for phrase in FORBIDDEN_OVERCLAIMS:
        require(phrase not in lower, f"{path.relative_to(ROOT)} overclaims: {phrase}", failures)
    require(re.search(r"\b[a-f0-9]{64}\b", lower) is None, f"{path.relative_to(ROOT)} leaks raw 64-hex digest", failures)


def check_source(failures: list[str]) -> None:
    project = read_text(HARNESS_PROJECT)
    source = read_text(HARNESS_SOURCE)
    app_test = read_text(APP_TEST)
    save_patcher = read_text(SAVE_PATCHER)
    save_editor = read_text(SAVE_EDITOR)
    config_editor = read_text(CONFIG_EDITOR)
    slot_codec = read_text(SLOT_CODEC)

    require("ProjectReference Include=\"..\\..\\OnslaughtCareerEditor.AppCore\\OnslaughtCareerEditor.AppCore.csproj\"" in project, "harness project missing AppCore reference", failures)
    for token in (
        "SchemaVersion = \"save-options-byte-preservation-appcore-fixture-matrix-private-evidence.v1\"",
        "SaveEditorService.PatchSave",
        "ConfigurationEditorService.PatchConfiguration",
        "ConfigurationEditorService.LoadKeybindRowsFromFile",
        "BesFilePatcher.AnalyzeSave",
        "MissionScriptSlotBitsetSaveCodec.SetSlotsInSingleDword",
        "FixtureFamilyCount != 8",
        "AppCoreFixtureCaseCount != 36",
        "LegacyTrapOffsets = [0x22D4, 0x23A4, 0x240C]",
        "OptionsEntriesStart = 0x24BE",
        "OptionsTailStart = 0x26BE",
        "ProductUiWired = false",
        "RuntimeExecution = false",
        "RuntimeDefaultOptionsProof = false",
    ):
        require(token in source, f"harness source missing token: {token}", failures)
    for forbidden in ("Program Files", "steamapps", "BEA.exe"):
        require(forbidden not in source, f"harness source contains forbidden token: {forbidden}", failures)

    require("CommonSavePatchRejectsOptionsLikePaths" in app_test, "AppCore save/options test anchor missing", failures)
    require("public const int EXPECTED_FILE_SIZE = 10004" in save_patcher, "BesFilePatcher expected-size anchor missing", failures)
    require("public const ushort VERSION_WORD = 0x4BD1" in save_patcher, "BesFilePatcher version anchor missing", failures)
    require("stored_value = (meta << 24) | (kills & 0x00FFFFFF)" in save_patcher, "kill metadata preservation anchor missing", failures)
    require("Save Editor common mode expects .bes career save paths only" in save_editor, "SaveEditorService options-like guard missing", failures)
    require("Configuration mode requires .bea/defaultoptions.bea input and output paths" in config_editor, "ConfigurationEditorService path guard missing", failures)
    require("File." not in slot_codec, "MissionScript slot codec gained file I/O", failures)


def check_prerequisites(failures: list[str]) -> None:
    runtime_gate = read_json(RUNTIME_GATE)
    implementation = read_json(IMPLEMENTATION_CONTRACT)
    require(runtime_gate["saveOptionsBytePreservationRuntimeProofReadinessGateStatus"].endswith("runtime-deferred-no-launch"), "runtime gate status mismatch", failures)
    require(runtime_gate["selectedNextSlice"] == "Save / Options Byte-Preservation AppCore Fixture Matrix Proof Plan", "runtime gate next-slice mismatch", failures)
    require(runtime_gate["negativeGuards"]["runtimeExecution"] is False, "runtime gate execution guard mismatch", failures)
    require(implementation["saveOptionsBytePreservationAppCoreImplementationContractStatus"].endswith("not-runtime-proof"), "implementation prerequisite status mismatch", failures)
    require(implementation["appCoreServiceProof"]["appCoreServiceProofCaseCount"] == 8, "implementation prerequisite case count mismatch", failures)


def check_schema(failures: list[str]) -> None:
    summary = read_json(PRIVATE_SUMMARY)
    validate_private_summary(summary, failures, check_files=True)
    expected = public_schema_from_private(summary)
    for path in (RESULT, LORE_RESULT):
        actual = read_json(path)
        require(actual == expected, f"{path.relative_to(ROOT)} does not match private-derived schema", failures)
        require(actual["saveOptionsBytePreservationAppCoreFixtureMatrixStatus"] == STATUS, "public status mismatch", failures)
        require(actual["selectedNextSlice"] == NEXT_SLICE, "public next-slice mismatch", failures)
        require(actual["matrix"]["appCoreFixtureCaseCount"] == 36, "public case count mismatch", failures)
        require(actual["matrix"]["unexpectedDiffCount"] == 0, "public unexpected diff mismatch", failures)
        require(actual["matrix"]["legacyTrapHitCountNonSlot"] == 0, "public legacy trap mismatch", failures)
        check_no_public_leaks(path, failures)


def check_docs(failures: list[str]) -> None:
    required = (
        "Save / Options Byte-Preservation AppCore Fixture Matrix Proof",
        STATUS,
        f"previousSlice={PREVIOUS_SLICE}",
        f"selectedNextSlice={NEXT_SLICE}",
        "toolProjectPath=tools/SaveOptionsAppCoreFixtureMatrixHarness/SaveOptionsAppCoreFixtureMatrixHarness.csproj",
        "appCoreSavePatchPath=OnslaughtCareerEditor.AppCore/BesFilePatcher.cs",
        "saveEditorServicePath=OnslaughtCareerEditor.AppCore/SaveEditorService.cs",
        "configurationEditorServicePath=OnslaughtCareerEditor.AppCore/ConfigurationEditorService.cs",
        "slotCodecPath=OnslaughtCareerEditor.AppCore/MissionScriptSlotBitsetSaveCodec.cs",
        "fixtureFamilyCount=8",
        "appCoreFixtureCaseCount=36",
        "containerAnalyzerCaseCount=2",
        "careerKillCategoryCaseCount=5",
        "killBoundaryCaseCount=3",
        "defaultOptionsSettingCaseCount=10",
        "optionsCopyCaseCount=4",
        "controllerKeybindCaseCount=4",
        "slotBitsetCaseCount=4",
        "rejectionNoOpLegacyCaseCount=4",
        "outputCaseCount=29",
        "rejectionCaseCount=5",
        "noOpCaseCount=1",
        "noOpDiffCount=0",
        "unexpectedDiffCount=0",
        "legacyTrapHitCountNonSlot=0",
        "allRejectionsOutputNotCreated=true",
        "keybindDiffsWithinOptionsEntriesAndTailControlScheme=true",
        "slotRoundTripCaseCount=4",
        "derivedInvalidFixtureCount=2",
        "expectedSize=10004",
        "versionWord=0x4BD1",
        "trueViewRule=file_offset = 0x0002 + career_offset",
        "careerSlotsBase=0x240A",
        "careerSlotsEndExclusive=0x248A",
        "optionsEntriesRange=0x24BE-0x26BD",
        "optionsTailRange=0x26BE-0x2713",
        "allOutputsFileSizePreserved=true",
        "allOutputsVersionWordPreserved=true",
        "sourcePathsPublic=false",
        "sourceHashesPublic=false",
        "artifactPathsPublic=false",
        "artifactHashesPublic=false",
        "rawBytesPublic=false",
        "acceptedFixturesDerivedFromCopiedBaselines=true",
        "invalidFixturesRejectionOnly=true",
        "saveSynthesis=false",
        "installedGameMutation=false",
        "originalExecutableMutation=false",
        "runtimeExecution=false",
        "beLaunch=false",
        "newLaunch=false",
        "screenshotCapture=false",
        "nativeInput=false",
        "debuggerAttachment=false",
        "copiedExecutablePatchApplied=false",
        "binaryPatchEngineUsed=false",
        "patchCatalogTouched=false",
        "ghidraMutation=false",
        "executablePatching=false",
        "godotWork=false",
        "rebuildImplementation=false",
        "runtimeSaveLoadProof=false",
        "runtimeDefaultOptionsProof=false",
        "publicLeakCheck=PASS",
    )
    for path in (PROOF, READINESS):
        text = read_text(path)
        for token in required:
            require(token in text, f"{path.relative_to(ROOT)} missing token: {token}", failures)
        check_no_public_leaks(path, failures)
    require(read_text(LORE_PROOF) == read_text(PROOF), "proof lore mirror mismatch", failures)

    front_tokens = (
        PROOF_NAME,
        RESULT_NAME,
        STATUS,
        f"selectedNextSlice={NEXT_SLICE}",
        "fixtureFamilyCount=8",
        "appCoreFixtureCaseCount=36",
        "unexpectedDiffCount=0",
        "legacyTrapHitCountNonSlot=0",
        "runtimeExecution=false",
        "beLaunch=false",
        "godotWork=false",
    )
    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX, SAVE_INDEX, SAVE_FORMAT):
        text = read_text(path)
        for token in front_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing front-door token: {token}", failures)

    backlog = read_text(BACKLOG)
    require("Completed Save / Options Byte-Preservation AppCore Fixture Matrix Proof Plan" in backlog, "backlog missing completed fixture-matrix row", failures)
    require(f"The selected active static-to-proof slice is {NEXT_SLICE}. Status: selected" in backlog, "backlog missing next active slice", failures)
    require("The selected active static-to-proof slice is Save / Options Byte-Preservation AppCore Fixture Matrix Proof Plan. Status: selected" not in backlog, "backlog still marks fixture matrix active", failures)

    for source, mirror in (
        (BACKLOG, LORE_BACKLOG),
        (MAPPED, LORE_MAPPED),
        (BIN_INDEX, LORE_BIN_INDEX),
        (RE_INDEX, LORE_RE_INDEX),
        (SAVE_INDEX, LORE_SAVE_INDEX),
        (SAVE_FORMAT, LORE_SAVE_FORMAT),
    ):
        require(read_text(source) == read_text(mirror), f"lore mirror mismatch for {source.relative_to(ROOT)}", failures)


def check_package(failures: list[str]) -> None:
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:save-options-byte-preservation-appcore-fixture-matrix")
        == r"py -3 tools\save_options_byte_preservation_appcore_fixture_matrix_probe.py --check",
        "missing package script",
        failures,
    )


def run_check() -> list[str]:
    failures: list[str] = []
    check_prerequisites(failures)
    check_source(failures)
    check_schema(failures)
    check_docs(failures)
    check_package(failures)
    require(no_bea_process_running(), "BEA.exe process is running after AppCore fixture-matrix proof", failures)
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
            print("Save / Options AppCore fixture-matrix probe: FAIL")
            for failure in failures:
                print(f"- {failure}")
            return 1
        print("Save / Options AppCore fixture-matrix probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
