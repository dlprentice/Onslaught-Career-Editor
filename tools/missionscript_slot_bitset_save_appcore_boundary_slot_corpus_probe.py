#!/usr/bin/env python3
"""Validate MissionScript slot bitset/save AppCore boundary-slot corpus proof."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

CODEC = ROOT / "OnslaughtCareerEditor.AppCore" / "MissionScriptSlotBitsetSaveCodec.cs"
TESTS = ROOT / "OnslaughtCareerEditor.AppCore.Tests" / "MissionScriptSlotBitsetSaveCodecTests.cs"
PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-slot-bitset-save-appcore-boundary-slot-corpus-proof.md"
SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-slot-bitset-save-appcore-boundary-slot-corpus.v1.json"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-slot-bitset-save-appcore-boundary-slot-corpus-proof.md"
LORE_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-slot-bitset-save-appcore-boundary-slot-corpus.v1.json"
READINESS = ROOT / "release" / "readiness" / "missionscript_slot_bitset_save_appcore_boundary_slot_corpus_2026-06-09.md"
RUNTIME_GATE_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-slot-bitset-save-runtime-proof-readiness-gate.v1.json"
APPCORE_HARNESS_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-slot-bitset-save-appcore-copied-baseline-codec-harness.v1.json"

BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
LORE_MAPPED = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
LORE_BIN_INDEX = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
LORE_RE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"
PACKAGE_JSON = ROOT / "package.json"

THIS_SLICE = "MissionScript Slot Bitset/Save AppCore Boundary-Slot Corpus Proof"
THIS_ACTIVE_SLICE = "MissionScript Slot Bitset/Save AppCore Boundary-Slot Corpus Proof Plan"
THIS_STATUS = "missionscript-slot-bitset-save-appcore-boundary-slot-corpus-complete-273-appcore-cases-not-runtime-proof"
PREVIOUS_SLICE = "MissionScript Slot Bitset/Save Runtime-Proof Readiness Gate"
PREVIOUS_STATUS = "missionscript-slot-bitset-save-runtime-proof-readiness-gate-complete-runtime-deferred-no-launch"
NEXT_SLICE = "MissionScript Slot Bitset/Save AppCore Copied-Baseline Boundary Corpus Harness Proof Plan"
ACTIVE_AFTER_NEXT_SLICE = "Save / Options Byte-Preservation AppCore Implementation Contract Proof Plan"

BOUNDARY_OFFSETS = ("0x240A", "0x240E", "0x2412", "0x2416", "0x241A", "0x241E", "0x2422", "0x2426")
BOUNDARY_PAIRS = tuple((index * 32, index * 32 + 31, index, BOUNDARY_OFFSETS[index]) for index in range(8))

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
    "private_runtime_evidence",
    "capturePath",
    "framePath",
    "frameSha256",
    "beforeDword",
    "afterDword",
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
    "copied-file boundary corpus behavior proven",
    "tutorial progression proven",
    "source selection proven",
    "private-frame review complete",
    "screenshot interpretation complete",
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
    require(re.search(r"\b[a-f0-9]{64}\b", lower) is None, f"{path.relative_to(ROOT)} leaks raw 64-hex digest", failures)


def expected_schema() -> dict[str, Any]:
    return {
        "schemaVersion": "missionscript-slot-bitset-save-appcore-boundary-slot-corpus.v1",
        "status": "PASS",
        "slotBitsetSaveAppCoreBoundarySlotCorpusStatus": THIS_STATUS,
        "previousSlice": PREVIOUS_SLICE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedFixtureFamily": "slot-bitset-save",
        "selectedFixturePath": "slot-bitset-save-core-handler-and-career-bridge",
        "implementation": {
            "appCoreCodecPath": "OnslaughtCareerEditor.AppCore/MissionScriptSlotBitsetSaveCodec.cs",
            "appCoreTestPath": "OnslaughtCareerEditor.AppCore.Tests/MissionScriptSlotBitsetSaveCodecTests.cs",
            "interfaceKind": "pure AppCore in-memory buffer codec",
            "fileIoPerformed": False,
            "copiedFileMutationPerformed": False,
            "sourceBaselineRead": False,
            "privateArtifactMaterialized": False,
            "productUiWired": False,
        },
        "staticContext": {
            "staticFunctionQuality": "6411/6411 = 100.00%",
            "staticDebt": "0 / 0 / 0",
            "expandedStaticSurface": "1560/1560 = 100.00%",
            "currentRiskFocused": "1179/1179 = 100.00%",
            "remainingActiveFocusedWork": 0,
            "latestGhidraBackupClass": "verified-static-backup-redacted",
        },
        "codecContract": {
            "expectedFileSize": 10004,
            "versionWord": "0x4BD1",
            "trueViewRule": "file_offset = 0x0002 + career_offset",
            "careerSlotsBase": "0x240A",
            "careerSlotsEndExclusive": "0x248A",
            "slotStorageDwords": 32,
            "slotStorageBytes": 128,
            "usedSlotDwords": 8,
            "usedSlotStorageBytes": 32,
            "reservedTailBytes": 96,
            "validSlotRange": "0..255",
            "firstValidSlot": 0,
            "lastValidSlot": 255,
            "firstUsedSlotOffset": "0x240A",
            "lastUsedSlotOffset": "0x2429",
            "reservedStorageEndExclusive": "0x248A",
        },
        "corpus": {
            "existingSeedVectorCaseCount": 5,
            "boundaryPairMaskCaseCount": 8,
            "singleSlotRoundTripCaseCount": 256,
            "xunitTestCaseCount": 273,
            "boundaryPairMask": "0x80000001",
            "boundaryVectorSlots": [63, 64, 224, 255],
            "boundaryPairDwordOffsets": list(BOUNDARY_OFFSETS),
            "boundaryPairs": [
                {"slots": [first, last], "dwordIndex": index, "trueViewDwordOffset": offset, "mask": "0x80000001"}
                for first, last, index, offset in BOUNDARY_PAIRS
            ],
            "allValidSlotsRoundTrip": True,
            "setSlotIdempotentForAllValidSlots": True,
            "clearRoundTripsForAllValidSlots": True,
            "touchesOnlyExpectedByteForAllValidSlots": True,
            "crossDwordMaskRejected": True,
            "invalidSlotLowerBoundRejected": True,
            "invalidSlotUpperBoundRejected": True,
            "slot256Rejected": True,
            "wrongSizeRejected": True,
            "wrongVersionRejected": True,
        },
        "dotnetValidation": {
            "command": "dotnet test OnslaughtCareerEditor.AppCore.Tests/OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter MissionScriptSlotBitsetSaveCodecTests",
            "dotnetFilter": "MissionScriptSlotBitsetSaveCodecTests",
            "passed": True,
            "total": 273,
            "failed": 0,
            "skipped": 0,
            "previewSdkMessageOnly": True,
        },
        "negativeGuards": {
            "runtimeExecution": False,
            "beLaunch": False,
            "newLaunch": False,
            "screenshotCapture": False,
            "privateFrameReviewPerformed": False,
            "rowObservation": False,
            "nativeInput": False,
            "debuggerAttachment": False,
            "installedGameMutationAllowed": False,
            "originalExecutableMutationAllowed": False,
            "defaultoptionsMutation": False,
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
                "the clean-room AppCore in-memory codec maps every valid saved MissionScript slot 0..255",
                "every valid saved slot set operation touches only the expected little-endian byte",
                "every valid saved slot set operation is idempotent and clears back to baseline",
                "the first and last slot in each used saved dword build the expected 0x80000001 mask",
            ],
            "doesNotProve": [
                "runtime MissionScript execution",
                "runtime command effects",
                "runtime slot persistence",
                "runtime save/load behavior",
                "runtime defaultoptions behavior",
                "copied-file boundary corpus behavior",
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


def check_prerequisites(failures: list[str]) -> None:
    runtime_gate = read_json(RUNTIME_GATE_SCHEMA)
    harness = read_json(APPCORE_HARNESS_SCHEMA)
    require(runtime_gate["slotBitsetSaveRuntimeProofReadinessGateStatus"] == PREVIOUS_STATUS, "runtime gate prerequisite status mismatch", failures)
    require(runtime_gate["selectedNextSlice"] == THIS_ACTIVE_SLICE, "runtime gate prerequisite next-slice mismatch", failures)
    require(runtime_gate["decision"]["runtimeDeferred"] is True, "runtime gate defer mismatch", failures)
    require(runtime_gate["negativeGuards"]["runtimeExecution"] is False, "runtime gate runtime guard mismatch", failures)
    require(harness["slotBitsetSaveAppCoreCopiedBaselineCodecHarnessStatus"].endswith("not-runtime-proof"), "harness prerequisite status mismatch", failures)
    require(harness["slotWrite"]["observedDwordXorMask"] == "0x60000000", "harness observed XOR mismatch", failures)


def check_code_and_tests(failures: list[str]) -> None:
    codec = read_text(CODEC)
    tests = read_text(TESTS)
    for token in (
        "public const int UsedSlotDwords = 8;",
        "public const int SlotStorageDwords = 32;",
        "public const int SlotCount = UsedSlotDwords * 32;",
        "CareerSlotsEndExclusive = CareerSlotsBaseOffset + SlotStorageBytes",
        "slot >> 5",
        "slot & 31",
        "1u << bitIndex",
        "ValidateSlot(slot)",
        "public static void SetSlot(Span<byte> buffer, int slot, bool enabled)",
    ):
        require(token in codec, f"codec missing token: {token}", failures)
    for forbidden in ("File.", "FileStream", "Directory.", "Process.", "Ghidra", "Godot", "defaultoptions"):
        require(forbidden not in codec, f"codec contains forbidden token: {forbidden}", failures)
    for token in (
        "BoundarySlotPairsInEachUsedDword",
        "AllValidSlots",
        "SetSlot_ForEveryValidSavedSlot_TouchesOnlyExpectedByteAndRoundtrips",
        "BuildSingleDwordMask_ForUsedDwordBoundaryPairs_MatchesExpectedMaskAndRange",
        "0x80000001u",
        "for (int dwordIndex = 0; dwordIndex < MissionScriptSlotBitsetSaveCodec.UsedSlotDwords; dwordIndex++)",
        "for (int slot = 0; slot < MissionScriptSlotBitsetSaveCodec.SlotCount; slot++)",
        "AssertSingleSlotRoundTrip(slot)",
        "Assert.Equal(new[] { vector.LittleEndianByteOffset }, changedAfterSet)",
        "Assert.Empty(ChangedOffsets(afterSet, buffer))",
        "Assert.Empty(ChangedOffsets(before, buffer))",
        "Assert.Throws<ArgumentException>(() => MissionScriptSlotBitsetSaveCodec.BuildSingleDwordMask(stackalloc int[] { 31, 32 }))",
    ):
        require(token in tests, f"tests missing token: {token}", failures)


def check_schema(failures: list[str]) -> None:
    expected = expected_schema()
    for path in (SCHEMA, LORE_SCHEMA):
        actual = read_json(path)
        require(actual == expected, f"{path.relative_to(ROOT)} schema mismatch", failures)
        check_no_public_leaks(path, failures)


def check_docs(failures: list[str]) -> None:
    required_tokens = (
        THIS_SLICE,
        THIS_STATUS,
        PREVIOUS_SLICE,
        NEXT_SLICE,
        "missionscript-slot-bitset-save-appcore-boundary-slot-corpus.v1.json",
        "appCoreCodecPath=OnslaughtCareerEditor.AppCore/MissionScriptSlotBitsetSaveCodec.cs",
        "appCoreTestPath=OnslaughtCareerEditor.AppCore.Tests/MissionScriptSlotBitsetSaveCodecTests.cs",
        "interfaceKind=pure AppCore in-memory buffer codec",
        "dotnetFilter=MissionScriptSlotBitsetSaveCodecTests",
        "xunitTestCaseCount=273",
        "passed=true",
        "existingSeedVectorCaseCount=5",
        "boundaryPairMaskCaseCount=8",
        "singleSlotRoundTripCaseCount=256",
        "validSlotRange=0..255",
        "usedSlotDwords=8",
        "slotStorageDwords=32",
        "usedSlotStorageBytes=32",
        "reservedSlotStorageBytes=128",
        "reservedTailBytes=96",
        "firstValidSlot=0",
        "lastValidSlot=255",
        "firstUsedSlotOffset=0x240A",
        "lastUsedSlotOffset=0x2429",
        "reservedStorageEndExclusive=0x248A",
        "boundaryPairMask=0x80000001",
        "boundaryVectorSlots=63,64,224,255",
        "boundaryPairDwordOffsets=0x240A,0x240E,0x2412,0x2416,0x241A,0x241E,0x2422,0x2426",
        "allValidSlotsRoundTrip=true",
        "setSlotIdempotentForAllValidSlots=true",
        "clearRoundTripsForAllValidSlots=true",
        "touchesOnlyExpectedByteForAllValidSlots=true",
        "crossDwordMaskRejected=true",
        "invalidSlotLowerBoundRejected=true",
        "invalidSlotUpperBoundRejected=true",
        "slot256Rejected=true",
        "wrongSizeRejected=true",
        "wrongVersionRejected=true",
        "fileIoPerformed=false",
        "copiedFileMutationPerformed=false",
        "sourceBaselineRead=false",
        "privateArtifactMaterialized=false",
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
    require(read_json(LORE_SCHEMA) == read_json(SCHEMA), "lore schema mirror mismatch", failures)

    front_door_tokens = (
        THIS_SLICE,
        THIS_STATUS,
        "missionscript-slot-bitset-save-appcore-boundary-slot-corpus-proof.md",
        "missionscript-slot-bitset-save-appcore-boundary-slot-corpus.v1.json",
        f"selectedNextSlice={NEXT_SLICE}",
        "xunitTestCaseCount=273",
        "singleSlotRoundTripCaseCount=256",
        "boundaryPairMaskCaseCount=8",
        "runtimeExecution=false",
        "beLaunch=false",
    )
    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX):
        text = read_text(path)
        for token in front_door_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing front-door token: {token}", failures)
        require(
            f"The selected active static-to-proof slice is {THIS_ACTIVE_SLICE}. Status: selected" not in text,
            f"{path.relative_to(ROOT)} still marks boundary-slot corpus lane active",
            failures,
        )
        require(
            f"The selected active static-to-proof slice is {ACTIVE_AFTER_NEXT_SLICE}. Status: selected" in text
            or f"active next static child lane: {ACTIVE_AFTER_NEXT_SLICE}" in text,
            f"{path.relative_to(ROOT)} missing active Save / Options AppCore implementation-contract lane",
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
        scripts.get("test:missionscript-slot-bitset-save-appcore-boundary-slot-corpus")
        == r"py -3 tools\missionscript_slot_bitset_save_appcore_boundary_slot_corpus_probe.py --check",
        "missing boundary-slot corpus package script",
        failures,
    )


def run_check() -> list[str]:
    failures: list[str] = []
    check_prerequisites(failures)
    check_code_and_tests(failures)
    check_schema(failures)
    check_docs(failures)
    check_package(failures)
    require(no_bea_process_running(), "BEA.exe process is running after boundary-slot corpus proof", failures)
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()
    failures = run_check()
    if failures:
        print("MissionScript slot bitset/save AppCore boundary-slot corpus probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("MissionScript slot bitset/save AppCore boundary-slot corpus probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
