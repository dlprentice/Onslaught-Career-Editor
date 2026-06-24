#!/usr/bin/env python3
"""Validate MissionScript slot bitset/save clean-room codec interface proof artifacts."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

APPCORE_CODEC = ROOT / "OnslaughtCareerEditor.AppCore" / "MissionScriptSlotBitsetSaveCodec.cs"
APPCORE_TESTS = ROOT / "OnslaughtCareerEditor.AppCore.Tests" / "MissionScriptSlotBitsetSaveCodecTests.cs"

PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-slot-bitset-save-clean-room-codec-interface-proof.md"
RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-slot-bitset-save-clean-room-codec-interface.v1.json"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-slot-bitset-save-clean-room-codec-interface-proof.md"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-slot-bitset-save-clean-room-codec-interface.v1.json"
READINESS = ROOT / "release" / "readiness" / "missionscript_slot_bitset_save_clean_room_codec_interface_2026-06-09.md"

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

THIS_SLICE = "MissionScript Slot Bitset/Save Clean-Room Codec Interface Proof"
THIS_ACTIVE_SLICE = "MissionScript Slot Bitset/Save Clean-Room Codec Interface Proof Plan"
THIS_STATUS = "missionscript-slot-bitset-save-clean-room-codec-interface-complete-appcore-pure-buffer-contract-not-runtime-proof"
PREVIOUS_SLICE = "MissionScript Slot Bitset/Save Copied-File Byte-Diff Proof"
PREVIOUS_STATUS = "missionscript-slot-bitset-save-copied-file-byte-diff-complete-copied-real-baseline-not-runtime-proof"
NEXT_SLICE = "MissionScript Slot Bitset/Save AppCore Copied-Baseline Codec Harness Proof Plan"
ACTIVE_SLICE = "Save / Options Byte-Preservation AppCore Implementation Contract Proof Plan"

EXPECTED_VECTORS = [
    (0, 0, 0, "0x00000001", "0x240A", "0x240A", "0x01"),
    (31, 0, 31, "0x80000000", "0x240A", "0x240D", "0x80"),
    (32, 1, 0, "0x00000001", "0x240E", "0x240E", "0x01"),
    (61, 1, 29, "0x20000000", "0x240E", "0x2411", "0x20"),
    (62, 1, 30, "0x40000000", "0x240E", "0x2411", "0x40"),
]

PUBLIC_FORBIDDEN_TOKENS = (
    "C:\\Users",
    "Program Files",
    "steamapps",
    "save-attempts",
    "subagents/",
    "subagents\\",
    "game\\savegames",
    "HWND",
    "window handle",
    "process id",
    "sha256",
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
    "copied-file appcore harness behavior proven",
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


def check_no_public_leaks(path: Path, failures: list[str]) -> None:
    text = read_text(path)
    lower = text.lower()
    for token in PUBLIC_FORBIDDEN_TOKENS:
        require(token.lower() not in lower, f"{path.relative_to(ROOT)} leaks forbidden public token: {token}", failures)
    for phrase in FORBIDDEN_OVERCLAIMS:
        require(phrase not in lower, f"{path.relative_to(ROOT)} overclaims forbidden category: {phrase}", failures)
    require(re.search(r"\b[a-f0-9]{64}\b", lower) is None, f"{path.relative_to(ROOT)} leaks a raw 64-hex digest", failures)


def check_source_prerequisites(failures: list[str]) -> None:
    copied = read_json(COPIED_FILE_SCHEMA)
    deterministic = read_json(DETERMINISTIC_SCHEMA)
    slot = read_json(SLOT_COMMAND_SCHEMA)
    save = read_json(SAVE_COPIED_SCHEMA)

    require(copied["slotBitsetSaveCopiedFileByteDiffStatus"] == PREVIOUS_STATUS, "copied-file prerequisite status mismatch", failures)
    require(copied["selectedNextSlice"] == THIS_ACTIVE_SLICE, "copied-file prerequisite next-slice mismatch", failures)
    require(copied["slotWrite"]["observedDwordXorMask"] == "0x60000000", "copied-file observed XOR mismatch", failures)
    require(copied["slotWrite"]["baselineToSetChangedOffsets"] == ["0x2411"], "copied-file changed offsets mismatch", failures)
    require(copied["privateEvidence"]["sourcePathsPublic"] is False, "copied-file source path disclosure mismatch", failures)
    require(copied["privateEvidence"]["sourceHashesPublic"] is False, "copied-file source hash disclosure mismatch", failures)
    require(copied["privateEvidence"]["artifactHashesPublic"] is False, "copied-file artifact hash disclosure mismatch", failures)
    require(copied["privateEvidence"]["rawBeforeAfterDwordsPublic"] is False, "copied-file raw dword disclosure mismatch", failures)

    require(
        deterministic["slotBitsetSaveDeterministicCodecProofPlanStatus"]
        == "missionscript-slot-bitset-save-deterministic-codec-proof-plan-complete-pure-codec-not-runtime-proof",
        "deterministic prerequisite status mismatch",
        failures,
    )
    require(deterministic["codecModel"]["slotRange"] == "0..255", "deterministic slot range mismatch", failures)
    require(deterministic["codecAccounting"]["usedSlotDwords"] == 8, "deterministic used slot dwords mismatch", failures)
    require(deterministic["codecAccounting"]["reservedSlotStorageDwords"] == 32, "deterministic reserved slot dwords mismatch", failures)
    require(deterministic["combinedSeedVector"]["combinedMask"] == "0x60000000", "deterministic combined mask mismatch", failures)
    require(slot["status"] == "PASS", "slot command schema status mismatch", failures)
    require(save["status"] == "PASS", "save copied-file schema status mismatch", failures)
    require(save["container"]["expectedSize"] == 10004, "save copied-file size mismatch", failures)
    require(save["container"]["versionWord"] == "0x4BD1", "save copied-file version mismatch", failures)


def check_appcore_code(failures: list[str]) -> None:
    codec = read_text(APPCORE_CODEC)
    tests = read_text(APPCORE_TESTS)

    for token in (
        "public static class MissionScriptSlotBitsetSaveCodec",
        "public const int ExpectedFileSize = 10004;",
        "public const ushort VersionWord = 0x4BD1;",
        "public const int CareerSlotsBaseOffset = 0x240A;",
        "public const int UsedSlotDwords = 8;",
        "public const int SlotStorageDwords = 32;",
        "public const int SlotStorageBytes = SlotStorageDwords * 4;",
        "public const int CareerSlotsEndExclusive = CareerSlotsBaseOffset + SlotStorageBytes;",
        "public const int SlotCount = UsedSlotDwords * 32;",
        "slot >> 5",
        "slot & 31",
        "1u << bitIndex",
        "GetVector",
        "BuildSingleDwordMask",
        "GetSlot",
        "SetSlot",
        "SetSlotsInSingleDword",
    ):
        require(token in codec, f"codec missing token: {token}", failures)

    for forbidden in ("File.", "FileStream", "Directory.", "Process.", "Ghidra", "Godot"):
        require(forbidden not in codec, f"codec contains forbidden runtime/file token: {forbidden}", failures)

    for slot, dword, bit, mask, dword_offset, byte_offset, byte_mask in EXPECTED_VECTORS:
        test_token = f"[InlineData({slot}, {dword}, {bit}, {mask}u, {dword_offset}, {byte_offset}, {byte_mask})]"
        require(test_token in tests, f"tests missing vector token: {test_token}", failures)

    for token in (
        "BuildSingleDwordMask_ForSlots61And62_MatchesCopiedFileProof",
        "SetSlotsInSingleDword_ForSlots61And62_TouchesOnlyExpectedByteInCleanVector",
        "SetSlotsInSingleDword_IsIdempotentAndClearRoundtrips",
        "Codec_RejectsInvalidSlotsAndContainers",
        "0x60000000u",
        "new[] { 0x2411 }",
        "Assert.Throws<ArgumentOutOfRangeException>",
        "Assert.Throws<ArgumentException>",
    ):
        require(token in tests, f"tests missing token: {token}", failures)


def check_public_schema(failures: list[str]) -> None:
    result = read_json(RESULT)
    lore = read_json(LORE_RESULT)
    require(lore == result, "lore schema mirror mismatch", failures)
    require(result["schemaVersion"] == "missionscript-slot-bitset-save-clean-room-codec-interface.v1", "schema version mismatch", failures)
    require(result["status"] == "PASS", "schema status mismatch", failures)
    require(result["slotBitsetSaveCleanRoomCodecInterfaceStatus"] == THIS_STATUS, "schema status token mismatch", failures)
    require(result["previousSlice"] == PREVIOUS_SLICE, "schema previous slice mismatch", failures)
    require(result["selectedNextSlice"] == NEXT_SLICE, "schema next slice mismatch", failures)
    require(result["selectedFixtureFamily"] == "slot-bitset-save", "schema fixture family mismatch", failures)
    require(result["selectedFixturePath"] == "slot-bitset-save-core-handler-and-career-bridge", "schema fixture path mismatch", failures)

    impl = result["implementation"]
    require(impl["appCoreCodecPath"] == "OnslaughtCareerEditor.AppCore/MissionScriptSlotBitsetSaveCodec.cs", "schema AppCore codec path mismatch", failures)
    require(impl["appCoreTestPath"] == "OnslaughtCareerEditor.AppCore.Tests/MissionScriptSlotBitsetSaveCodecTests.cs", "schema AppCore test path mismatch", failures)
    require(impl["interfaceKind"] == "pure AppCore in-memory buffer codec", "schema interface kind mismatch", failures)
    for key in ("productUiWired", "fileIoPerformed", "copiedFileMutationPerformed", "sourceBaselineRead", "privateArtifactMaterialized"):
        require(impl[key] is False, f"schema implementation guard mismatch: {key}", failures)

    source = result["sourceEvidence"]
    require(source["copiedFileByteDiff"]["status"] == PREVIOUS_STATUS, "schema copied-file source status mismatch", failures)
    require(source["copiedFileByteDiff"]["sourcePathsPublic"] is False, "schema source path disclosure mismatch", failures)
    require(source["copiedFileByteDiff"]["sourceHashesPublic"] is False, "schema source hash disclosure mismatch", failures)
    require(source["copiedFileByteDiff"]["artifactHashesPublic"] is False, "schema artifact hash disclosure mismatch", failures)
    require(source["copiedFileByteDiff"]["rawBeforeAfterDwordsPublic"] is False, "schema raw dword disclosure mismatch", failures)

    contract = result["codecContract"]
    require(contract["expectedFileSize"] == 10004, "contract size mismatch", failures)
    require(contract["versionWord"] == "0x4BD1", "contract version mismatch", failures)
    require(contract["trueViewRule"] == "file_offset = 0x0002 + career_offset", "contract true-view mismatch", failures)
    require(contract["careerSlotsBase"] == "0x240A", "contract slot base mismatch", failures)
    require(contract["careerSlotsEndExclusive"] == "0x248A", "contract slot end mismatch", failures)
    require(contract["usedSlotDwords"] == 8, "contract used dwords mismatch", failures)
    require(contract["reservedSlotStorageDwords"] == 32, "contract reserved dwords mismatch", failures)
    require(contract["slotStorageBytes"] == 128, "contract storage bytes mismatch", failures)
    require(contract["slotRange"] == "0..255", "contract slot range mismatch", failures)
    require(contract["interfaceOperationCount"] == 8, "contract operation count mismatch", failures)
    require(contract["publicMethodCount"] == 6, "contract public method count mismatch", failures)

    vectors = result["deterministicBitsetVectors"]
    require(len(vectors) == 5, "deterministic vector count mismatch", failures)
    for row, expected in zip(vectors, EXPECTED_VECTORS, strict=True):
        slot, dword, bit, mask, dword_offset, byte_offset, byte_mask = expected
        require(row["slot"] == slot, f"vector slot mismatch: {slot}", failures)
        require(row["dwordIndex"] == dword, f"vector dword mismatch: {slot}", failures)
        require(row["bitIndex"] == bit, f"vector bit mismatch: {slot}", failures)
        require(row["bitMask"] == mask, f"vector mask mismatch: {slot}", failures)
        require(row["trueViewOffset"] == dword_offset, f"vector offset mismatch: {slot}", failures)
        require(row["littleEndianByteOffset"] == byte_offset, f"vector byte offset mismatch: {slot}", failures)
        require(row["littleEndianByteMask"] == byte_mask, f"vector byte mask mismatch: {slot}", failures)

    combined = result["combinedSeedVector"]
    require(combined["slots"] == [61, 62], "combined slots mismatch", failures)
    require(combined["combinedMask"] == "0x60000000", "combined mask mismatch", failures)
    require(combined["observedDwordXorMask"] == "0x60000000", "combined observed XOR mismatch", failures)
    require(combined["baselineToSetChangedOffsets"] == ["0x2411"], "combined changed offset mismatch", failures)

    appcore = result["appCoreValidation"]
    require(appcore["dotnetFilter"] == "MissionScriptSlotBitsetSaveCodecTests", "AppCore filter mismatch", failures)
    require(appcore["testMethodCount"] == 5, "AppCore test method count mismatch", failures)
    require(appcore["xunitTestCaseCount"] == 9, "AppCore test case count mismatch", failures)
    require(appcore["passed"] is True, "AppCore passed mismatch", failures)
    require(appcore["inMemoryCodecBufferOnly"] is True, "AppCore buffer-only mismatch", failures)
    require(appcore["syntheticBesFileWritten"] is False, "AppCore synthetic file guard mismatch", failures)

    guard = result["guardSummary"]
    for key, value in guard.items():
        if isinstance(value, bool):
            require(value is False, f"guard bool mismatch: {key}", failures)
        elif isinstance(value, int):
            require(value == 0, f"guard counter mismatch: {key}", failures)
    require("runtime MissionScript execution" in result["claimBoundary"]["doesNotProve"], "claim boundary missing runtime MissionScript deferral", failures)
    require("the MissionScript slot-bitset/save fixture now has a clean-room AppCore pure-buffer codec interface" in result["claimBoundary"]["proves"], "claim boundary missing interface proof", failures)
    check_no_public_leaks(RESULT, failures)
    check_no_public_leaks(LORE_RESULT, failures)


def check_docs(failures: list[str]) -> None:
    required_tokens = (
        THIS_SLICE,
        THIS_STATUS,
        PREVIOUS_SLICE,
        NEXT_SLICE,
        "missionscript-slot-bitset-save-clean-room-codec-interface.v1.json",
        "appCoreCodecPath=OnslaughtCareerEditor.AppCore/MissionScriptSlotBitsetSaveCodec.cs",
        "appCoreTestPath=OnslaughtCareerEditor.AppCore.Tests/MissionScriptSlotBitsetSaveCodecTests.cs",
        "interfaceKind=pure AppCore in-memory buffer codec",
        "productUiWired=false",
        "fileIoPerformed=false",
        "copiedFileMutationPerformed=false",
        "sourceBaselineRead=false",
        "privateArtifactMaterialized=false",
        "expectedFileSize=10004",
        "versionWord=0x4BD1",
        "trueViewRule=file_offset = 0x0002 + career_offset",
        "careerSlotsBase=0x240A",
        "careerSlotsEndExclusive=0x248A",
        "interfaceOperationCount=8",
        "usedSlotDwords=8",
        "reservedSlotStorageDwords=32",
        "slotStorageBytes=128",
        "slotRange=0..255",
        "publicMethodCount=6",
        "deterministicBitsetVectorCount=5",
        "copiedFileSourceProofCount=1",
        "publicLeakCheck=PASS",
        "combinedMask=0x60000000",
        "observedDwordXorMask=0x60000000",
        "baselineToSetChangedOffsets=0x2411",
        "xunitTestCaseCount=9",
        "inMemoryCodecBufferOnly=true",
        "syntheticBesFileWritten=false",
        "runtimeExecution=false",
        "beLaunch=false",
        "ghidraMutation=false",
        "executablePatching=false",
        "godotWork=false",
        "rebuildImplementation=false",
    )
    for path in (PROOF, READINESS):
        text = read_text(path)
        for token in required_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing token: {token}", failures)
        check_no_public_leaks(path, failures)

    require(read_text(LORE_PROOF) == read_text(PROOF), "lore proof mirror mismatch", failures)

    front_door_tokens = (
        THIS_ACTIVE_SLICE,
        THIS_STATUS,
        "missionscript-slot-bitset-save-clean-room-codec-interface-proof.md",
        "missionscript-slot-bitset-save-clean-room-codec-interface.v1.json",
        "appCoreCodecPath=OnslaughtCareerEditor.AppCore/MissionScriptSlotBitsetSaveCodec.cs",
        "interfaceOperationCount=8",
        "xunitTestCaseCount=9",
        "selectedNextSlice=MissionScript Slot Bitset/Save AppCore Copied-Baseline Codec Harness Proof Plan",
    )
    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX):
        text = read_text(path)
        for token in front_door_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing front-door token: {token}", failures)
        require(
            f"The selected active static-to-proof slice is {THIS_ACTIVE_SLICE}. Status: selected" not in text,
            f"{path.relative_to(ROOT)} still marks clean-room codec interface lane as active",
            failures,
        )
        require(
            f"The selected active static-to-proof slice is {ACTIVE_SLICE}. Status: selected" in text
            or f"active next static child lane: {ACTIVE_SLICE}" in text,
            f"{path.relative_to(ROOT)} missing active MissionScript slot bitset/save runtime-proof readiness gate lane",
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
        scripts.get("test:missionscript-slot-bitset-save-clean-room-codec-interface")
        == r"py -3 tools\missionscript_slot_bitset_save_clean_room_codec_interface_probe.py --check",
        "missing clean-room codec interface package script",
        failures,
    )
    for script in (
        "test:missionscript-slot-bitset-save-copied-file-byte-diff",
        "test:missionscript-slot-bitset-save-deterministic-codec-proof-plan",
        "test:missionscript-slot-bitset-save-rebuild-fixture-proof-plan",
        "test:missionscript-slot-command-effect-static",
        "test:save-options-controller-byte-preservation-copied-file",
    ):
        require(script in scripts, f"missing prerequisite package script: {script}", failures)


def run_check() -> list[str]:
    failures: list[str] = []
    check_source_prerequisites(failures)
    check_appcore_code(failures)
    check_public_schema(failures)
    check_docs(failures)
    check_package(failures)
    require(no_bea_process_running(), "BEA.exe process is running after clean-room codec interface proof", failures)
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures = run_check()
    if failures:
        print("MissionScript slot bitset/save clean-room codec interface proof probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("MissionScript slot bitset/save clean-room codec interface proof probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
