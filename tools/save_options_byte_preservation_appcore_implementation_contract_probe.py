#!/usr/bin/env python3
"""Validate Save / Options AppCore implementation-contract proof artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

HARNESS_PROJECT = ROOT / "tools" / "SaveOptionsAppCoreContractHarness" / "SaveOptionsAppCoreContractHarness.csproj"
HARNESS_SOURCE = ROOT / "tools" / "SaveOptionsAppCoreContractHarness" / "Program.cs"
APPCORE_TEST = ROOT / "OnslaughtCareerEditor.AppCore.Tests" / "AppCoreSaveOptionsContractTests.cs"
SAVE_PATCHER = ROOT / "OnslaughtCareerEditor.AppCore" / "BesFilePatcher.cs"
SAVE_EDITOR = ROOT / "OnslaughtCareerEditor.AppCore" / "SaveEditorService.cs"
CONFIG_EDITOR = ROOT / "OnslaughtCareerEditor.AppCore" / "ConfigurationEditorService.cs"
SLOT_CODEC = ROOT / "OnslaughtCareerEditor.AppCore" / "MissionScriptSlotBitsetSaveCodec.cs"

PRIVATE_DIR = ROOT / "subagents" / "static-to-proof" / "save-options-byte-preservation-appcore-implementation-contract-proof"
PRIVATE_SUMMARY = PRIVATE_DIR / "evidence-summary.private.json"

RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "save-options-byte-preservation-appcore-implementation-contract.v1.json"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "save-options-byte-preservation-appcore-implementation-contract.v1.json"
PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "save-options-byte-preservation-appcore-implementation-contract-proof.md"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "save-options-byte-preservation-appcore-implementation-contract-proof.md"
READINESS = ROOT / "release" / "readiness" / "save_options_byte_preservation_appcore_implementation_contract_2026-06-09.md"

COPIED_FILE_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "save-options-controller-byte-preservation-copied-file.v1.json"
MISSION_BOUNDARY_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-slot-bitset-save-appcore-copied-baseline-boundary-corpus-harness.v1.json"
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

STATUS = "save-options-byte-preservation-appcore-implementation-contract-complete-copied-real-baseline-services-not-runtime-proof"
PREVIOUS_SLICE = "MissionScript Slot Bitset/Save AppCore Copied-Baseline Boundary Corpus Harness Proof"
NEXT_SLICE = "Save / Options Byte-Preservation Runtime-Proof Readiness Gate Plan"
RESULT_NAME = "save-options-byte-preservation-appcore-implementation-contract.v1.json"
PROOF_NAME = "save-options-byte-preservation-appcore-implementation-contract-proof.md"

EXPECTED_PRIVATE_FILES = {
    "career-appcore-service-input.bes",
    "career-appcore-aircraft-kill-service-output.bes",
    "defaultoptions-appcore-service-input.bea",
    "defaultoptions-appcore-sound-volume-output.bea",
    "defaultoptions-appcore-options-entries-source.bea",
    "defaultoptions-appcore-options-entries-output.bea",
    "defaultoptions-appcore-options-tail-source.bea",
    "defaultoptions-appcore-options-tail-output.bea",
    "defaultoptions-appcore-inplace-copy.bea",
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
    "password",
    "token=",
)

FORBIDDEN_OVERCLAIMS = (
    "runtime save/load behavior proven",
    "runtime defaultoptions boot behavior proven",
    "runtime menu behavior proven",
    "runtime controller remap/input behavior proven",
    "runtime goodies wall behavior proven",
    "runtime missionscript execution proven",
    "installed game mutation proven",
    "original executable mutation proven",
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
    require(summary.get("schemaVersion") == "save-options-byte-preservation-appcore-implementation-contract-private-evidence.v1", "private schema mismatch", failures)
    require(summary.get("status") == "PASS", "private status mismatch", failures)

    source = summary["source"]
    for key in ("sourcePathsPublic", "sourceHashesPublic", "artifactPathsPublic", "artifactHashesPublic", "rawBytesPublic"):
        require(source[key] is False, f"private disclosure guard mismatch: {key}", failures)

    implementation = summary["implementation"]
    require(implementation["appCoreServicesUsed"] is True, "private AppCore service use mismatch", failures)
    require(implementation["productUiWired"] is False, "private product UI guard mismatch", failures)
    require(implementation["harnessFileIo"] is True, "private harness file-I/O mismatch", failures)
    require(implementation["privateArtifactMaterialized"] is True, "private materialization mismatch", failures)

    provenance = summary["provenance"]
    for key in (
        "copyBeforeWrite",
        "sourcesUnderPriorPrivateEvidenceRoot",
        "outputsUnderProofPrivateEvidenceRoot",
        "sourceAndOutputPathsDistinct",
        "careerSourceUnchanged",
        "defaultOptionsSourceUnchanged",
    ):
        require(provenance[key] is True, f"private provenance mismatch: {key}", failures)
    require(provenance["careerSourceToInputDiffCount"] == 0, "career source copy diff mismatch", failures)
    require(provenance["defaultOptionsSourceToInputDiffCount"] == 0, "defaultoptions source copy diff mismatch", failures)

    container = summary["container"]
    require(container["expectedSize"] == 10004, "private expected size mismatch", failures)
    require(container["slotCodecExpectedSize"] == 10004, "private slot-codec size mismatch", failures)
    require(container["versionWord"] == "0x4BD1", "private version mismatch", failures)
    require(container["slotCodecVersionWord"] == "0x4BD1", "private slot-codec version mismatch", failures)
    require(container["careerSlotsBase"] == "0x240A", "private slot base mismatch", failures)
    require(container["careerSlotsEndExclusive"] == "0x248A", "private slot end mismatch", failures)
    require(container["allOutputsFileSizePreserved"] is True, "private output size preservation mismatch", failures)
    require(container["allOutputsVersionWordPreserved"] is True, "private output version preservation mismatch", failures)

    career = summary["careerServicePatch"]
    require(career["service"] == "SaveEditorService.PatchSave", "career service mismatch", failures)
    require(career["patchNodes"] is False and career["patchLinks"] is False and career["patchGoodies"] is False and career["patchKills"] is True, "career patch flags mismatch", failures)
    require(career["optionsLikeInputRejected"] is True, "career options-like rejection mismatch", failures)
    require(career["inPlaceRejected"] is True, "career in-place rejection mismatch", failures)
    require(career["allowedOffsets"] == ["0x23F6", "0x23F7", "0x23F8"], "career allowed offsets mismatch", failures)
    require(set(career["changedOffsets"]).issubset(set(career["allowedOffsets"])), "career changed offsets exceed allowlist", failures)
    require(career["unexpectedDiffCount"] == 0, "career unexpected diff mismatch", failures)
    require(career["metadataBytePreserved"] is True, "career metadata preservation mismatch", failures)
    require(career["lower24Changed"] is True, "career lower24 mismatch", failures)
    require(career["legacyTrapHitCount"] == 0, "career legacy trap mismatch", failures)
    require(career["techSlotsRangeUnchanged"] is True, "career tech slot preservation mismatch", failures)
    require(career["optionsEntriesUnchanged"] is True, "career options entries preservation mismatch", failures)
    require(career["optionsTailUnchanged"] is True, "career options tail preservation mismatch", failures)

    config = summary["configurationServicePatch"]
    require(config["service"] == "ConfigurationEditorService.PatchConfiguration", "config service mismatch", failures)
    require(config["optionsLikePathRequired"] is True, "config options-like path guard mismatch", failures)
    require(config["soundVolumeChangedOffsets"] == ["0x248E", "0x248F", "0x2490", "0x2491"], "sound volume offsets mismatch", failures)
    require(config["soundVolumeUnexpectedDiffCount"] == 0, "sound volume unexpected diff mismatch", failures)
    require(config["optionsEntriesCopyChangedOffsets"] == ["0x24BE"], "options entries copy offsets mismatch", failures)
    require(config["optionsEntriesCopyUnexpectedDiffCount"] == 0, "options entries unexpected diff mismatch", failures)
    require(config["optionsEntriesCopyTailUnchanged"] is True, "options entries tail preservation mismatch", failures)
    require(config["optionsTailCopyChangedOffsets"] == ["0x26BE"], "options tail copy offsets mismatch", failures)
    require(config["optionsTailCopyUnexpectedDiffCount"] == 0, "options tail unexpected diff mismatch", failures)
    require(config["optionsTailCopyEntriesUnchanged"] is True, "options tail entries preservation mismatch", failures)
    require(config["copiedInPlacePatchAllowedOnlyInProofRoot"] is True, "copied in-place root guard mismatch", failures)
    require(config["copiedInPlaceBackupCreated"] is True, "copied in-place backup mismatch", failures)
    require(config["copiedInPlaceBackupMatchesPrePatch"] is True, "copied in-place backup bytes mismatch", failures)
    require(config["copiedInPlaceChangedOffsets"] == ["0x2492", "0x2493", "0x2494", "0x2495"], "copied in-place offsets mismatch", failures)
    require(config["copiedInPlaceUnexpectedDiffCount"] == 0, "copied in-place unexpected diff mismatch", failures)

    slot = summary["slotCodecAlignment"]
    require(slot["codecExpectedSizeMatchesSavePatcher"] is True, "slot size alignment mismatch", failures)
    require(slot["codecVersionWordMatchesSavePatcher"] is True, "slot version alignment mismatch", failures)
    require(slot["slot61ToggleRoundTrip"] is True, "slot roundtrip mismatch", failures)
    require(slot["slot61ChangedOffsets"] == ["0x2411"], "slot changed offset mismatch", failures)
    require(slot["slotCodecFileIo"] is False, "slot codec file-I/O guard mismatch", failures)

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
        "runtimeSaveLoadProof",
        "runtimeDefaultOptionsProof",
    ):
        require(summary["negativeGuards"][key] is False, f"negative guard mismatch: {key}", failures)

    if not check_files:
        return
    seen = {Path(row["relativePath"]).name: row for row in summary["copiedArtifacts"]}
    require(EXPECTED_PRIVATE_FILES.issubset(set(seen)), "private artifact set missing expected files", failures)
    require(len(seen) == 10, "private artifact count mismatch", failures)
    for name, row in seen.items():
        path = PRIVATE_DIR / name
        if not path.is_file():
            candidates = list(PRIVATE_DIR.glob(name))
            path = candidates[0] if candidates else path
        require(path.is_file(), f"missing private artifact file: {name}", failures)
        if path.is_file():
            data = path.read_bytes()
            require(len(data) == 10004, f"{name} size mismatch", failures)
            require(version_word(data) == "0x4BD1", f"{name} version mismatch", failures)
            require(row["sha256"] == sha256(data), f"{name} hash mismatch", failures)


def public_schema_from_private(summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "save-options-byte-preservation-appcore-implementation-contract.v1",
        "status": "PASS",
        "saveOptionsBytePreservationAppCoreImplementationContractStatus": STATUS,
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
            "copyBeforeWrite": summary["provenance"]["copyBeforeWrite"],
            "sourceAndOutputPathsDistinct": summary["provenance"]["sourceAndOutputPathsDistinct"],
            "careerSourceUnchanged": summary["provenance"]["careerSourceUnchanged"],
            "defaultOptionsSourceUnchanged": summary["provenance"]["defaultOptionsSourceUnchanged"],
            "careerSourceToInputDiffCount": summary["provenance"]["careerSourceToInputDiffCount"],
            "defaultOptionsSourceToInputDiffCount": summary["provenance"]["defaultOptionsSourceToInputDiffCount"],
        },
        "container": {
            "expectedSize": 10004,
            "expectedSizeHex": "0x2714",
            "versionWord": "0x4BD1",
            "slotCodecExpectedSize": 10004,
            "slotCodecVersionWord": "0x4BD1",
            "trueViewRule": "file_offset = 0x0002 + career_offset",
            "careerSlotsBase": "0x240A",
            "careerSlotsEndExclusive": "0x248A",
            "allOutputsFileSizePreserved": True,
            "allOutputsVersionWordPreserved": True,
        },
        "appCoreServiceProof": {
            "appCoreServiceProofCaseCount": 8,
            "saveEditorPatchSaveUsed": True,
            "configurationEditorPatchConfigurationUsed": True,
            "besFilePatcherAnalyzeSaveUsed": True,
            "missionScriptSlotBitsetSaveCodecUsed": True,
            "careerService": {
                "patchNodes": False,
                "patchLinks": False,
                "patchGoodies": False,
                "patchKills": True,
                "optionsLikeInputRejected": True,
                "inPlaceRejected": True,
                "changedOffsets": summary["careerServicePatch"]["changedOffsets"],
                "allowedOffsets": ["0x23F6", "0x23F7", "0x23F8"],
                "unexpectedDiffCount": 0,
                "metadataBytePreserved": True,
                "lower24Changed": True,
                "legacyTrapHitCount": 0,
                "techSlotsRangeUnchanged": True,
                "optionsEntriesUnchanged": True,
                "optionsTailUnchanged": True,
            },
            "configurationService": {
                "optionsLikePathRequired": True,
                "soundVolumeChangedOffsets": ["0x248E", "0x248F", "0x2490", "0x2491"],
                "soundVolumeUnexpectedDiffCount": 0,
                "soundVolumeOptionsEntriesUnchanged": True,
                "soundVolumeOptionsTailUnchanged": True,
                "optionsEntriesCopyChangedOffsets": ["0x24BE"],
                "optionsEntriesCopyUnexpectedDiffCount": 0,
                "optionsEntriesCopyTailUnchanged": True,
                "optionsTailCopyChangedOffsets": ["0x26BE"],
                "optionsTailCopyUnexpectedDiffCount": 0,
                "optionsTailCopyEntriesUnchanged": True,
                "copiedInPlacePatchAllowedOnlyInProofRoot": True,
                "copiedInPlaceBackupCreated": True,
                "copiedInPlaceBackupMatchesPrePatch": True,
                "copiedInPlaceChangedOffsets": ["0x2492", "0x2493", "0x2494", "0x2495"],
                "copiedInPlaceUnexpectedDiffCount": 0,
            },
            "slotCodecAlignment": {
                "codecExpectedSizeMatchesSavePatcher": True,
                "codecVersionWordMatchesSavePatcher": True,
                "slot61ToggleRoundTrip": True,
                "slot61ChangedOffsets": ["0x2411"],
                "slotCodecFileIo": False,
            },
        },
        "negativeGuards": {
            "saveSynthesis": False,
            "installedGameMutation": False,
            "originalExecutableMutation": False,
            "runtimeExecution": False,
            "beLaunch": False,
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
                "AppCore career save patching can perform a copied-baseline lower-24 Aircraft kill edit while preserving metadata and non-target ranges",
                "AppCore common save patching rejects options-like inputs and in-place career output",
                "AppCore configuration patching can perform copied-baseline sound-volume, options-entry, options-tail, and copied in-place backup flows with bounded byte ranges",
                "MissionScript slot-bitset codec container constants remain aligned with the broader AppCore save patcher",
            ],
            "doesNotProve": [
                "runtime save/load behavior",
                "runtime defaultoptions boot behavior",
                "runtime menu behavior",
                "runtime controller remap/input behavior",
                "runtime Goodies wall behavior",
                "runtime MissionScript execution",
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
    test = read_text(APPCORE_TEST)
    save_patcher = read_text(SAVE_PATCHER)
    save_editor = read_text(SAVE_EDITOR)
    config_editor = read_text(CONFIG_EDITOR)
    slot_codec = read_text(SLOT_CODEC)

    require("ProjectReference Include=\"..\\..\\OnslaughtCareerEditor.AppCore\\OnslaughtCareerEditor.AppCore.csproj\"" in project, "harness project missing AppCore reference", failures)
    for token in (
        "SaveEditorService.PatchSave",
        "ConfigurationEditorService.PatchConfiguration",
        "BesFilePatcher.AnalyzeSave",
        "MissionScriptSlotBitsetSaveCodec.SetSlot",
        "OptionsEntriesStart = 0x24BE",
        "OptionsTailStart = 0x26BE",
        "CareerAircraftKillOffset = 0x23F6",
        "CareerAircraftKillMetadataOffset = 0x23F9",
        "SourceEvidenceRootRelative",
        "EvidenceRootRelative",
        "Directory.Delete(outRoot, recursive: true)",
        "ProductUiWired = false",
        "RuntimeExecution = false",
        "RuntimeDefaultOptionsProof = false",
    ):
        require(token in source, f"harness source missing token: {token}", failures)
    for forbidden in ("Program Files", "steamapps", "BEA.exe"):
        require(forbidden not in source, f"harness source contains forbidden token: {forbidden}", failures)

    for token in (
        "SaveAndSlotCodecsShareContainerConstants",
        "CommonSavePatchRejectsOptionsLikePaths",
        "ConfigurationPendingChangeDetectionRequiresExplicitMutationIntent",
    ):
        require(token in test, f"AppCore contract test missing token: {token}", failures)

    for token in (
        "public const int EXPECTED_FILE_SIZE = 10004",
        "public const ushort VERSION_WORD = 0x4BD1",
        "file_offset % 4 == 2",
        "In the true dword view, Goodie 228 is at 0x22D6 and mCareerInProgress is at 0x248A",
        "PatchFile(string inputPath, string outputPath)",
        "Refusing to patch in place",
        "stored_value = (meta << 24) | (kills & 0x00FFFFFF)",
        "Options copy requires matching options layout",
        "Force \"Custom\" scheme when patching bindings",
    ):
        require(token in save_patcher, f"BesFilePatcher missing contract token: {token}", failures)
    require("Save Editor common mode expects .bes career save paths only" in save_editor, "SaveEditorService options rejection token missing", failures)
    require("Configuration mode requires .bea/defaultoptions.bea input and output paths" in config_editor, "ConfigurationEditorService options path token missing", failures)
    require("File." not in slot_codec, "MissionScript slot codec gained file I/O", failures)


def check_schema(failures: list[str]) -> None:
    summary = read_json(PRIVATE_SUMMARY)
    validate_private_summary(summary, failures, check_files=True)
    expected = public_schema_from_private(summary)
    for path in (RESULT, LORE_RESULT):
        actual = read_json(path)
        require(actual == expected, f"{path.relative_to(ROOT)} does not match private-derived schema", failures)
        require(actual["saveOptionsBytePreservationAppCoreImplementationContractStatus"] == STATUS, "public status mismatch", failures)
        require(actual["selectedNextSlice"] == NEXT_SLICE, "public next-slice mismatch", failures)
        require(actual["appCoreServiceProof"]["appCoreServiceProofCaseCount"] == 8, "public service case count mismatch", failures)
        require(actual["privateEvidence"]["copiedArtifactCount"] == 10, "public artifact count mismatch", failures)
        check_no_public_leaks(path, failures)


def check_prerequisites(failures: list[str]) -> None:
    copied = read_json(COPIED_FILE_SCHEMA)
    mission = read_json(MISSION_BOUNDARY_SCHEMA)
    require(copied["status"] == "PASS", "copied-file prerequisite status mismatch", failures)
    require(copied["source"]["runtimeExecution"] is False, "copied-file prerequisite runtime guard mismatch", failures)
    require(copied["baselineEvidence"]["copiedArtifactCount"] == 5, "copied-file prerequisite artifact count mismatch", failures)
    require(mission["slotBitsetSaveAppCoreCopiedBaselineBoundaryCorpusHarnessStatus"].endswith("not-runtime-proof"), "MissionScript boundary prerequisite status mismatch", failures)
    require(mission["selectedNextSlice"] == "Save / Options Byte-Preservation AppCore Implementation Contract Proof Plan", "MissionScript boundary next-slice mismatch", failures)


def check_docs(failures: list[str]) -> None:
    required = (
        "Save / Options Byte-Preservation AppCore Implementation Contract Proof",
        STATUS,
        f"previousSlice={PREVIOUS_SLICE}",
        f"selectedNextSlice={NEXT_SLICE}",
        "toolProjectPath=tools/SaveOptionsAppCoreContractHarness/SaveOptionsAppCoreContractHarness.csproj",
        "appCoreSavePatchPath=OnslaughtCareerEditor.AppCore/BesFilePatcher.cs",
        "saveEditorServicePath=OnslaughtCareerEditor.AppCore/SaveEditorService.cs",
        "configurationEditorServicePath=OnslaughtCareerEditor.AppCore/ConfigurationEditorService.cs",
        "slotCodecPath=OnslaughtCareerEditor.AppCore/MissionScriptSlotBitsetSaveCodec.cs",
        "appCoreServicesUsed=true",
        "productUiWired=false",
        "harnessFileIo=true",
        "privateArtifactMaterialized=true",
        "copiedArtifactCount=10",
        "sourcePathsPublic=false",
        "sourceHashesPublic=false",
        "artifactPathsPublic=false",
        "artifactHashesPublic=false",
        "rawBytesPublic=false",
        "copyBeforeWrite=true",
        "sourceAndOutputPathsDistinct=true",
        "careerSourceUnchanged=true",
        "defaultOptionsSourceUnchanged=true",
        "careerSourceToInputDiffCount=0",
        "defaultOptionsSourceToInputDiffCount=0",
        "expectedSize=10004",
        "versionWord=0x4BD1",
        "slotCodecExpectedSize=10004",
        "slotCodecVersionWord=0x4BD1",
        "trueViewRule=file_offset = 0x0002 + career_offset",
        "careerSlotsBase=0x240A",
        "careerSlotsEndExclusive=0x248A",
        "appCoreServiceProofCaseCount=8",
        "SaveEditorService.PatchSave",
        "ConfigurationEditorService.PatchConfiguration",
        "BesFilePatcher.AnalyzeSave",
        "MissionScriptSlotBitsetSaveCodec",
        "optionsLikeInputRejected=true",
        "inPlaceRejected=true",
        "changedOffsets=0x23F6",
        "allowedOffsets=0x23F6,0x23F7,0x23F8",
        "metadataBytePreserved=true",
        "lower24Changed=true",
        "legacyTrapHitCount=0",
        "techSlotsRangeUnchanged=true",
        "optionsEntriesUnchanged=true",
        "optionsTailUnchanged=true",
        "soundVolumeChangedOffsets=0x248E,0x248F,0x2490,0x2491",
        "optionsEntriesCopyChangedOffsets=0x24BE",
        "optionsTailCopyChangedOffsets=0x26BE",
        "copiedInPlacePatchAllowedOnlyInProofRoot=true",
        "copiedInPlaceBackupCreated=true",
        "copiedInPlaceBackupMatchesPrePatch=true",
        "copiedInPlaceChangedOffsets=0x2492,0x2493,0x2494,0x2495",
        "slot61ChangedOffsets=0x2411",
        "slotCodecFileIo=false",
        "saveSynthesis=false",
        "installedGameMutation=false",
        "originalExecutableMutation=false",
        "runtimeExecution=false",
        "beLaunch=false",
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
    require(read_json(LORE_RESULT) == read_json(RESULT), "schema lore mirror mismatch", failures)

    front_tokens = (
        PROOF_NAME,
        RESULT_NAME,
        STATUS,
        f"selectedNextSlice={NEXT_SLICE}",
        "copiedArtifactCount=10",
        "appCoreServiceProofCaseCount=8",
        "runtimeExecution=false",
        "beLaunch=false",
        "godotWork=false",
    )
    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX, SAVE_INDEX, SAVE_FORMAT):
        text = read_text(path)
        for token in front_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing front-door token: {token}", failures)
        require(
            "The selected active static-to-proof slice is Save / Options Byte-Preservation AppCore Implementation Contract Proof Plan. Status: selected" not in text,
            f"{path.relative_to(ROOT)} still marks AppCore implementation-contract lane active",
            failures,
        )

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
        scripts.get("test:save-options-byte-preservation-appcore-implementation-contract")
        == r"py -3 tools\save_options_byte_preservation_appcore_implementation_contract_probe.py --check",
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
    require(no_bea_process_running(), "BEA.exe process is running after AppCore implementation-contract proof", failures)
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
            print("Save / Options AppCore implementation-contract probe: FAIL")
            for failure in failures:
                print(f"- {failure}")
            return 1
        print("Save / Options AppCore implementation-contract probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
