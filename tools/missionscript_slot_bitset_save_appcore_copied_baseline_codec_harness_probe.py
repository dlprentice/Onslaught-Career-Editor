#!/usr/bin/env python3
"""Validate MissionScript slot bitset/save AppCore copied-baseline harness proof."""

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
APPCORE_TESTS = ROOT / "OnslaughtCareerEditor.AppCore.Tests" / "MissionScriptSlotBitsetSaveCodecTests.cs"

SOURCE_BASELINE = ROOT / "subagents" / "static-to-proof" / "save-options-controller-byte-preservation-copied-file-proof" / "career-baseline.bes"
PRIVATE_DIR = ROOT / "subagents" / "static-to-proof" / "missionscript-slot-bitset-save-appcore-copied-baseline-codec-harness-proof"
PRIVATE_SUMMARY = PRIVATE_DIR / "evidence-summary.private.json"

PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-slot-bitset-save-appcore-copied-baseline-codec-harness-proof.md"
RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-slot-bitset-save-appcore-copied-baseline-codec-harness.v1.json"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-slot-bitset-save-appcore-copied-baseline-codec-harness-proof.md"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-slot-bitset-save-appcore-copied-baseline-codec-harness.v1.json"
READINESS = ROOT / "release" / "readiness" / "missionscript_slot_bitset_save_appcore_copied_baseline_codec_harness_2026-06-09.md"

CLEAN_ROOM_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-slot-bitset-save-clean-room-codec-interface.v1.json"
COPIED_FILE_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-slot-bitset-save-copied-file-byte-diff.v1.json"
DETERMINISTIC_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-slot-bitset-save-deterministic-codec-proof-plan.v1.json"
SLOT_COMMAND_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-slot-command-effect.v1.json"
SAVE_COPIED_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "save-options-controller-byte-preservation-copied-file.v1.json"

BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
LORE_MAPPED = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
LORE_BIN_INDEX = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
LORE_RE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"
PACKAGE_JSON = ROOT / "package.json"

THIS_SLICE = "MissionScript Slot Bitset/Save AppCore Copied-Baseline Codec Harness Proof"
THIS_ACTIVE_SLICE = "MissionScript Slot Bitset/Save AppCore Copied-Baseline Codec Harness Proof Plan"
THIS_STATUS = "missionscript-slot-bitset-save-appcore-copied-baseline-codec-harness-complete-appcore-copied-real-baseline-byte-preservation-not-runtime-proof"
PREVIOUS_SLICE = "MissionScript Slot Bitset/Save Clean-Room Codec Interface Proof"
PREVIOUS_STATUS = "missionscript-slot-bitset-save-clean-room-codec-interface-complete-appcore-pure-buffer-contract-not-runtime-proof"
NEXT_SLICE = "MissionScript Slot Bitset/Save Runtime-Proof Readiness Gate Plan"
ACTIVE_AFTER_NEXT_SLICE = "Save / Options Byte-Preservation AppCore Implementation Contract Proof Plan"

EXPECTED_PRIVATE_FILES = {
    "career-slot-appcore-baseline.bes",
    "career-slot-appcore-noop.bes",
    "career-slot-appcore-61-62-set.bes",
    "career-slot-appcore-61-62-idempotent-set.bes",
    "career-slot-appcore-61-62-clear-roundtrip.bes",
}

PUBLIC_FORBIDDEN_TOKENS = (
    "C:\\Users",
    "Program Files",
    "steamapps",
    "save-attempts",
    "subagents/",
    "subagents\\",
    "game\\savegames",
    '"sourcePath":',
    '"sourcePaths":',
    '"relativePath":',
    "sha256",
    "baselineDword1Before",
    "setDword1After",
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
    "runtime slot persistence proven",
    "runtime save/load behavior proven",
    "runtime defaultoptions behavior proven",
    "tutorial progression proven",
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
        "--source",
        str(SOURCE_BASELINE.relative_to(ROOT)),
        "--out-root",
        str(PRIVATE_DIR.relative_to(ROOT)),
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
    clean = read_json(CLEAN_ROOM_SCHEMA)
    copied = read_json(COPIED_FILE_SCHEMA)
    deterministic = read_json(DETERMINISTIC_SCHEMA)
    slot = read_json(SLOT_COMMAND_SCHEMA)
    save = read_json(SAVE_COPIED_SCHEMA)

    require(clean["slotBitsetSaveCleanRoomCodecInterfaceStatus"] == PREVIOUS_STATUS, "clean-room prerequisite status mismatch", failures)
    require(clean["selectedNextSlice"] == THIS_ACTIVE_SLICE, "clean-room prerequisite next-slice mismatch", failures)
    require(clean["implementation"]["interfaceKind"] == "pure AppCore in-memory buffer codec", "clean-room interface kind mismatch", failures)
    require(clean["guardSummary"]["fileIoRows"] == 0, "clean-room file-I/O guard mismatch", failures)
    require(copied["slotBitsetSaveCopiedFileByteDiffStatus"] == "missionscript-slot-bitset-save-copied-file-byte-diff-complete-copied-real-baseline-not-runtime-proof", "copied-file prerequisite mismatch", failures)
    require(copied["slotWrite"]["observedDwordXorMask"] == "0x60000000", "copied-file observed XOR mismatch", failures)
    require(copied["slotWrite"]["baselineToSetChangedOffsets"] == ["0x2411"], "copied-file changed offset mismatch", failures)
    require(copied["privateEvidence"]["sourcePathsPublic"] is False, "copied-file source disclosure mismatch", failures)
    require(deterministic["combinedSeedVector"]["combinedMask"] == "0x60000000", "deterministic mask mismatch", failures)
    require(slot["status"] == "PASS", "slot command prerequisite mismatch", failures)
    require(save["container"]["expectedSize"] == 10004, "save prerequisite size mismatch", failures)
    require(save["container"]["versionWord"] == "0x4BD1", "save prerequisite version mismatch", failures)


def check_harness_source(failures: list[str]) -> None:
    project = read_text(HARNESS_PROJECT)
    source = read_text(HARNESS_SOURCE)
    require("ProjectReference Include=\"..\\..\\OnslaughtCareerEditor.AppCore\\OnslaughtCareerEditor.AppCore.csproj\"" in project, "harness project missing AppCore reference", failures)
    for token in (
        "MissionScriptSlotBitsetSaveCodec.SetSlotsInSingleDword(set, TargetSlots, enabled: true)",
        "MissionScriptSlotBitsetSaveCodec.SetSlotsInSingleDword(idempotent, TargetSlots, enabled: true)",
        "MissionScriptSlotBitsetSaveCodec.SetSlotsInSingleDword(clear, TargetSlots, enabled: false)",
        "MissionScriptSlotBitsetSaveCodec.GetSlot(set, 61)",
        "MissionScriptSlotBitsetSaveCodec.GetSlot(set, 62)",
        "MissionScriptSlotBitsetSaveCodec.GetSlot(clear, 61)",
        "MissionScriptSlotBitsetSaveCodec.GetSlot(clear, 62)",
        "ManualSlotDwordWriteInHarness = false",
        "AppCoreCodecUsed = true",
    ):
        require(token in source, f"harness source missing AppCore token: {token}", failures)
    for forbidden in (
        "BinaryPrimitives.WriteUInt32LittleEndian",
        "WriteU32",
        "Program Files",
        "steamapps",
        "BEA.exe",
    ):
        require(forbidden not in source, f"harness source contains forbidden token: {forbidden}", failures)
    codec = read_text(APPCORE_CODEC)
    require("File." not in codec, "AppCore codec gained file I/O", failures)
    require("public static MissionScriptSlotBitsetMask SetSlotsInSingleDword" in codec, "AppCore codec missing SetSlotsInSingleDword", failures)
    require("MissionScriptSlotBitsetSaveCodecTests" in read_text(APPCORE_TESTS), "AppCore tests missing codec test class", failures)


def validate_private_summary(summary: dict[str, Any], failures: list[str], check_files: bool) -> None:
    require(summary.get("schemaVersion") == "missionscript-slot-bitset-save-appcore-copied-baseline-codec-harness-private-evidence.v1", "private schema mismatch", failures)
    require(summary.get("status") == "PASS", "private status mismatch", failures)
    harness = summary["harness"]
    require(harness["appCoreCodecUsed"] is True, "private AppCore codec use mismatch", failures)
    require(harness["manualSlotDwordWriteInHarness"] is False, "private manual dword write guard mismatch", failures)
    require(harness["productUiWired"] is False, "private product UI guard mismatch", failures)
    require(harness["appCoreCodecFileIo"] is False, "private AppCore file I/O guard mismatch", failures)
    require(harness["harnessFileIo"] is True, "private harness file I/O mismatch", failures)
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
    slot = summary["slotWrite"]
    require(slot["slots"] == [61, 62], "private slots mismatch", failures)
    require(slot["dwordIndex"] == 1, "private dword index mismatch", failures)
    require(slot["allowedDwordRange"] == "0x240E-0x2411", "private target range mismatch", failures)
    require(slot["allowedDwordXorMask"] == "0x60000000", "private target mask mismatch", failures)
    require(slot["observedDwordXorMask"] == "0x60000000", "private observed XOR mismatch", failures)
    require(slot["baselineToSetChangedOffsets"] == ["0x2411"], "private changed offset mismatch", failures)
    require(slot["unexpectedDiffCount"] == 0, "private unexpected diff mismatch", failures)
    require(slot["legacyTrapHitCount"] == 0, "private trap hit mismatch", failures)
    require(slot["setChangedTargetBits"] is True, "private target bits mismatch", failures)
    require(slot["preservedNonTargetBitsInDword"] is True, "private non-target dword mismatch", failures)
    require(slot["slot61AfterSet"] is True and slot["slot62AfterSet"] is True, "private set readback mismatch", failures)
    require(slot["slot61AfterClear"] is False and slot["slot62AfterClear"] is False, "private clear readback mismatch", failures)
    roundtrip = summary["noOpAndRoundTrip"]
    require(roundtrip["baselineToNoopDiffCount"] == 0, "private noop diff mismatch", failures)
    require(roundtrip["setToIdempotentDiffCount"] == 0, "private idempotent diff mismatch", failures)
    require(roundtrip["setToClearChangedOffsets"] == ["0x2411"], "private clear changed offset mismatch", failures)
    require(roundtrip["clearToBaselineDiffCount"] == 0, "private clear roundtrip mismatch", failures)
    for name, value in summary["preservation"].items():
        require(value is True, f"private preservation mismatch: {name}", failures)
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
    slot = summary["slotWrite"]
    roundtrip = summary["noOpAndRoundTrip"]
    return {
        "schemaVersion": "missionscript-slot-bitset-save-appcore-copied-baseline-codec-harness.v1",
        "status": "PASS",
        "slotBitsetSaveAppCoreCopiedBaselineCodecHarnessStatus": THIS_STATUS,
        "previousSlice": PREVIOUS_SLICE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedFixtureFamily": "slot-bitset-save",
        "selectedFixturePath": "slot-bitset-save-core-handler-and-career-bridge",
        "implementation": {
            "toolProjectPath": "tools/MissionScriptSlotBitsetSaveHarness/MissionScriptSlotBitsetSaveHarness.csproj",
            "appCoreCodecPath": "OnslaughtCareerEditor.AppCore/MissionScriptSlotBitsetSaveCodec.cs",
            "interfaceKind": "AppCore codec applied by proof-only copied-baseline harness",
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
            "copiedRealBaselineClass": "validated copied real career .bes baseline from prior ignored evidence",
            "copiedArtifactCount": 5,
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
        "slotWrite": {
            "slots": slot["slots"],
            "dwordIndex": slot["dwordIndex"],
            "allowedDwordRange": slot["allowedDwordRange"],
            "allowedDwordXorMask": slot["allowedDwordXorMask"],
            "slot61Mask": slot["slot61Mask"],
            "slot62Mask": slot["slot62Mask"],
            "comparisonMode": slot["comparisonMode"],
            "observedDwordXorMask": slot["observedDwordXorMask"],
            "baselineSelectedMaskInitiallyClear": slot["baselineSelectedMaskInitiallyClear"],
            "baselineToSetChangedOffsets": slot["baselineToSetChangedOffsets"],
            "baselineToSetChangedOffsetCount": slot["baselineToSetChangedOffsetCount"],
            "expectedChangedOffsets": slot["expectedChangedOffsets"],
            "unexpectedDiffCount": slot["unexpectedDiffCount"],
            "legacyTrapHitCount": slot["legacyTrapHitCount"],
            "setChangedTargetBits": slot["setChangedTargetBits"],
            "preservedNonTargetBitsInDword": slot["preservedNonTargetBitsInDword"],
            "slot61AfterSet": slot["slot61AfterSet"],
            "slot62AfterSet": slot["slot62AfterSet"],
            "slot61AfterClear": slot["slot61AfterClear"],
            "slot62AfterClear": slot["slot62AfterClear"],
        },
        "noOpAndRoundTrip": {
            "baselineToNoopDiffCount": roundtrip["baselineToNoopDiffCount"],
            "setToIdempotentDiffCount": roundtrip["setToIdempotentDiffCount"],
            "setToClearChangedOffsets": roundtrip["setToClearChangedOffsets"],
            "setToClearDiffCount": roundtrip["setToClearDiffCount"],
            "setToClearDwordXorMask": roundtrip["setToClearDwordXorMask"],
            "clearToBaselineDiffCount": roundtrip["clearToBaselineDiffCount"],
        },
        "preservation": summary["preservation"],
        "negativeGuards": summary["negativeGuards"],
        "claimBoundary": {
            "proves": [
                "the proof-only C# harness applies the AppCore MissionScript slot bitset/save codec to a copied real career baseline",
                "the AppCore codec set/readback path changes slots 61 and 62 through the true-view target dword range 0x240E-0x2411",
                "the observed little-endian dword XOR mask for the set operation remains 0x60000000",
                "the copied baseline, no-op, idempotent set, clear roundtrip, non-target ranges, options entries, options tail, and legacy trap offsets match the byte-preservation contract",
            ],
            "doesNotProve": [
                "runtime MissionScript execution",
                "runtime command effects",
                "runtime slot persistence",
                "runtime save/load behavior",
                "runtime defaultoptions behavior",
                "tutorial progression",
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
        require(actual["slotBitsetSaveAppCoreCopiedBaselineCodecHarnessStatus"] == THIS_STATUS, "public status mismatch", failures)
        require(actual["selectedNextSlice"] == NEXT_SLICE, "public next-slice mismatch", failures)
        require(actual["implementation"]["appCoreCodecUsed"] is True, "public AppCore use mismatch", failures)
        require(actual["implementation"]["manualSlotDwordWriteInHarness"] is False, "public manual dword write guard mismatch", failures)
        require(actual["privateEvidence"]["sourcePathsPublic"] is False, "public source path disclosure mismatch", failures)
        require(actual["privateEvidence"]["sourceHashesPublic"] is False, "public source hash disclosure mismatch", failures)
        require(actual["privateEvidence"]["artifactPathsPublic"] is False, "public artifact path disclosure mismatch", failures)
        require(actual["privateEvidence"]["artifactHashesPublic"] is False, "public artifact hash disclosure mismatch", failures)
        require(actual["slotWrite"]["slot61AfterSet"] is True and actual["slotWrite"]["slot62AfterSet"] is True, "public set readback mismatch", failures)
        require(actual["slotWrite"]["slot61AfterClear"] is False and actual["slotWrite"]["slot62AfterClear"] is False, "public clear readback mismatch", failures)
        check_no_public_leaks(path, failures)


def check_docs(failures: list[str]) -> None:
    required_tokens = (
        THIS_SLICE,
        THIS_STATUS,
        PREVIOUS_SLICE,
        NEXT_SLICE,
        "missionscript-slot-bitset-save-appcore-copied-baseline-codec-harness.v1.json",
        "toolProjectPath=tools/MissionScriptSlotBitsetSaveHarness/MissionScriptSlotBitsetSaveHarness.csproj",
        "appCoreCodecPath=OnslaughtCareerEditor.AppCore/MissionScriptSlotBitsetSaveCodec.cs",
        "interfaceKind=AppCore codec applied by proof-only copied-baseline harness",
        "appCoreCodecUsed=true",
        "manualSlotDwordWriteInHarness=false",
        "appCoreCodecFileIo=false",
        "harnessFileIo=true",
        "productUiWired=false",
        "sourceBaselineRead=true",
        "privateArtifactMaterialized=true",
        "copiedArtifactCount=5",
        "sourcePathsPublic=false",
        "sourceHashesPublic=false",
        "artifactPathsPublic=false",
        "artifactHashesPublic=false",
        "rawBeforeAfterDwordsPublic=false",
        "copyBeforeWrite=true",
        "sourceAndOutputPathsDistinct=true",
        "sourceToNewBaselineDiffCount=0",
        "sourceUnchanged=true",
        "expectedSize=10004",
        "versionWord=0x4BD1",
        "trueViewRule=file_offset = 0x0002 + career_offset",
        "slots=61,62",
        "allowedDwordRange=0x240E-0x2411",
        "allowedDwordXorMask=0x60000000",
        "observedDwordXorMask=0x60000000",
        "baselineToSetChangedOffsets=0x2411",
        "unexpectedDiffCount=0",
        "legacyTrapHitCount=0",
        "slot61AfterSet=true",
        "slot62AfterSet=true",
        "slot61AfterClear=false",
        "slot62AfterClear=false",
        "baselineToNoopDiffCount=0",
        "setToIdempotentDiffCount=0",
        "clearToBaselineDiffCount=0",
        "slotDword0Unchanged=true",
        "optionsEntriesUnchanged=true",
        "optionsTailUnchanged=true",
        "saveSynthesis=false",
        "runtimeExecution=false",
        "beLaunch=false",
        "ghidraMutation=false",
        "executablePatching=false",
        "godotWork=false",
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
        "missionscript-slot-bitset-save-appcore-copied-baseline-codec-harness-proof.md",
        "missionscript-slot-bitset-save-appcore-copied-baseline-codec-harness.v1.json",
        "appCoreCodecUsed=true",
        "manualSlotDwordWriteInHarness=false",
        "observedDwordXorMask=0x60000000",
        "baselineToSetChangedOffsets=0x2411",
        "clearToBaselineDiffCount=0",
        f"selectedNextSlice={NEXT_SLICE}",
    )
    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX):
        text = read_text(path)
        for token in front_door_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing front-door token: {token}", failures)
        require(
            f"The selected active static-to-proof slice is {THIS_ACTIVE_SLICE}. Status: selected" not in text,
            f"{path.relative_to(ROOT)} still marks AppCore copied-baseline harness lane as active",
            failures,
        )
        require(
            f"The selected active static-to-proof slice is {ACTIVE_AFTER_NEXT_SLICE}. Status: selected" in text
            or f"active next static child lane: {ACTIVE_AFTER_NEXT_SLICE}" in text,
            f"{path.relative_to(ROOT)} missing active boundary-slot corpus lane",
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
        scripts.get("test:missionscript-slot-bitset-save-appcore-copied-baseline-codec-harness")
        == r"py -3 tools\missionscript_slot_bitset_save_appcore_copied_baseline_codec_harness_probe.py --check",
        "missing AppCore copied-baseline harness package script",
        failures,
    )
    for script in (
        "test:missionscript-slot-bitset-save-clean-room-codec-interface",
        "test:missionscript-slot-bitset-save-copied-file-byte-diff",
        "test:missionscript-slot-bitset-save-deterministic-codec-proof-plan",
        "test:missionscript-slot-bitset-save-rebuild-fixture-proof-plan",
    ):
        require(script in scripts, f"missing prerequisite package script: {script}", failures)


def run_check() -> list[str]:
    failures: list[str] = []
    check_prerequisites(failures)
    check_harness_source(failures)
    check_public_schema(failures)
    check_docs(failures)
    check_package(failures)
    require(no_bea_process_running(), "BEA.exe process is running after AppCore copied-baseline harness proof", failures)
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
            print("MissionScript slot bitset/save AppCore copied-baseline codec harness proof probe: FAIL")
            for failure in failures:
                print(f"- {failure}")
            return 1
        print("MissionScript slot bitset/save AppCore copied-baseline codec harness proof probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
