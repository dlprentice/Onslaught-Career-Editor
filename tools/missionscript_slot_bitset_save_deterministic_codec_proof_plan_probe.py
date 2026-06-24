#!/usr/bin/env python3
"""Validate MissionScript slot bitset/save deterministic codec proof-plan artifacts."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-slot-bitset-save-deterministic-codec-proof-plan.md"
RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-slot-bitset-save-deterministic-codec-proof-plan.v1.json"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-slot-bitset-save-deterministic-codec-proof-plan.md"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-slot-bitset-save-deterministic-codec-proof-plan.v1.json"
READINESS = ROOT / "release" / "readiness" / "missionscript_slot_bitset_save_deterministic_codec_proof_plan_2026-06-09.md"

FIXTURE_PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-slot-bitset-save-rebuild-fixture-proof-plan.v1.json"
SLOT_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-slot-command-effect.v1.json"
SAVE_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "save-options-controller-byte-preservation-copied-file.v1.json"

BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
LORE_MAPPED = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
LORE_BIN_INDEX = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
LORE_RE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"
PACKAGE_JSON = ROOT / "package.json"

THIS_SLICE = "MissionScript Slot Bitset/Save Deterministic Codec Proof Plan"
PREVIOUS_SLICE = "MissionScript Slot Bitset/Save Rebuild Fixture Proof Plan"
NEXT_SLICE = "MissionScript Slot Bitset/Save Copied-File Byte-Diff Proof Plan"
STATUS_TOKEN = "missionscript-slot-bitset-save-deterministic-codec-proof-plan-complete-pure-codec-not-runtime-proof"
FIXTURE_STATUS = "missionscript-slot-bitset-save-rebuild-fixture-proof-plan-complete-deterministic-codec-selected"

FALSE_GUARDS = (
    "programFilesInputUsed",
    "installedGameMutation",
    "originalExecutableMutation",
    "copiedFileMutation",
    "saveSynthesis",
    "liveLooseMslLoading",
    "packedResourceScriptSelectionProven",
    "runtimeExecution",
    "runtimeMissionScriptExecutionProven",
    "runtimeCommandEffectsProven",
    "runtimeSlotPersistenceProven",
    "runtimeSaveBehaviorProven",
    "runtimeSaveLoadBehaviorProven",
    "runtimeDefaultoptionsBehaviorProven",
    "runtimeTutorialProgressionProven",
    "runtimeLevel500BranchProven",
    "runtimeFenrirStateProven",
    "beLaunch",
    "newLaunch",
    "screenshotCapture",
    "privateFrameReviewPerformed",
    "rowObservation",
    "exactTextOcrPerformed",
    "rawDialoguePublished",
    "sourceSelectionObserved",
    "nativeInput",
    "debuggerAttachment",
    "godotWork",
    "ghidraMutation",
    "executablePatching",
    "rebuildImplementation",
    "exactCommandDescriptorLayoutProven",
    "exactCommandArityProven",
    "exactArgumentTypeSchemaProven",
    "exactCGameLayoutProven",
    "exactCCareerLayoutProven",
    "runtimeMenuBehaviorProven",
    "runtimeControllerBehaviorProven",
    "rebuildParityProven",
    "noNoticeableDifferenceParityProven",
)

ZERO_COUNTERS = (
    "runtimeObservationRows",
    "missionScriptRuntimeEvidenceRows",
    "runtimeCommandEffectRows",
    "runtimeSlotEvidenceRows",
    "runtimeSaveRows",
    "copiedFileMutationRows",
    "copiedFileDiffRows",
    "saveCodecWriteRows",
    "privateFrameRowsObserved",
    "rowObservationRows",
    "sourceObservedRows",
    "sourceRuntimeObservationRows",
    "sourceRowStatusChangedCount",
    "newLaunchRows",
    "captureRows",
    "ocrRows",
    "rawDialogueRows",
    "ghidraMutationRows",
    "executablePatchRows",
    "rebuildImplementationRows",
    "godotProjectRows",
    "beProcessesAfterCodec",
    "publicAbsolutePathLeakCount",
    "publicSha256ValueLeakCount",
    "publicWindowIdentifierLeakCount",
    "publicProcessIdentifierLeakCount",
    "privatePathLeakCount",
    "rawArtifactLeakCount",
    "rawDialogueLeakCount",
)

EXPECTED_VECTOR_SLOTS = (0, 31, 32, 61, 62)
EXPECTED_SOURCE_CLASSES = {
    0: "derived-boundary-vector",
    31: "derived-boundary-vector",
    32: "derived-boundary-vector",
    61: "public-loose-msl-SetSlot-seed",
    62: "public-loose-msl-SetSlot-seed",
}

FORBIDDEN_PUBLIC_PATTERNS = (
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
    "runtime slot persistence proven",
    "runtime save behavior proven",
    "runtime save/load behavior proven",
    "runtime tutorial progression proven",
    "runtime level500 branch proven",
    "runtime fenrir state proven",
    "live loose-msl loading proven",
    "packed-resource script selection proven",
    "private-frame review complete",
    "source-selection observation complete",
    "exact descriptor layout proven",
    "exact arity proven",
    "exact argument type schema proven",
    "exact cgame layout proven",
    "exact ccareer layout proven",
    "copied-file mutation complete",
    "source baseline read complete",
    "private artifact materialization complete",
    "save synthesis complete",
    "visual qa complete",
    "godot parity proven",
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


def hex32(value: int) -> str:
    return f"0x{value:08X}"


def hex16(value: int) -> str:
    return f"0x{value:04X}"


def byte_hex(value: int) -> str:
    return f"0x{value:02X}"


def vector_for_slot(slot: int) -> dict[str, Any]:
    dword_index = slot >> 5
    bit_index = slot & 31
    bit_mask = 1 << bit_index
    true_view = 0x240A + (4 * dword_index)
    byte_offset = true_view + (bit_index >> 3)
    byte_mask = 1 << (bit_index & 7)
    return {
        "slot": slot,
        "sourceClass": EXPECTED_SOURCE_CLASSES[slot],
        "dwordIndex": dword_index,
        "bitIndex": bit_index,
        "bitMask": hex32(bit_mask),
        "trueViewOffset": hex16(true_view),
        "trueViewDwordRange": f"{hex16(true_view)}-{hex16(true_view + 3)}",
        "littleEndianByteOffset": hex16(byte_offset),
        "littleEndianByteMask": byte_hex(byte_mask),
        "zeroDwordBytesLittleEndian": [byte_hex(part) for part in bit_mask.to_bytes(4, "little")],
    }


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
    for pattern, category in FORBIDDEN_PUBLIC_PATTERNS:
        require(pattern.search(text) is None, f"{path.relative_to(ROOT)} leaks forbidden public category: {category}", failures)
    for phrase in FORBIDDEN_OVERCLAIMS:
        require(phrase not in lower, f"{path.relative_to(ROOT)} overclaims forbidden category: {phrase}", failures)
    require("0x2486" not in text, f"{path.relative_to(ROOT)} contains stale slot-255 dword range 0x2486", failures)
    require("slot `255`" not in text, f"{path.relative_to(ROOT)} contains stale slot 255 vector", failures)


def check_result(failures: list[str]) -> None:
    result = read_json(RESULT)
    fixture = read_json(FIXTURE_PLAN)
    slot = read_json(SLOT_SCHEMA)
    save = read_json(SAVE_SCHEMA)

    require(result["schemaVersion"] == "missionscript-slot-bitset-save-deterministic-codec-proof-plan.v1", "schema version mismatch", failures)
    require(result["status"] == "PASS", "status mismatch", failures)
    require(result["slotBitsetSaveDeterministicCodecProofPlanStatus"] == STATUS_TOKEN, "status token mismatch", failures)
    require(result["previousSlice"] == PREVIOUS_SLICE, "previous slice mismatch", failures)
    require(result["selectedNextSlice"] == NEXT_SLICE, "selected next slice mismatch", failures)
    require(result["selectedFixtureFamily"] == "slot-bitset-save", "selected fixture family mismatch", failures)
    require(result["selectedFixturePath"] == "slot-bitset-save-core-handler-and-career-bridge", "selected fixture path mismatch", failures)

    static = result["staticContext"]
    require(static["staticFunctionQuality"] == "6411/6411 = 100.00%", "static function quality mismatch", failures)
    require(static["staticDebt"] == "0 / 0 / 0", "static debt mismatch", failures)
    require(static["expandedStaticSurface"] == "1560/1560 = 100.00%", "expanded static surface mismatch", failures)
    require(static["currentRiskFocused"] == "1179/1179 = 100.00%", "current-risk mismatch", failures)
    require(static["remainingActiveFocusedWork"] == 0, "remaining work mismatch", failures)
    require(static["latestGhidraBackupClass"] == "verified-static-backup-redacted", "backup class mismatch", failures)

    accounting = result["codecAccounting"]
    require(accounting["sourceProofCount"] == 4, "source proof count mismatch", failures)
    require(accounting["descriptorEntryCount"] == 3, "descriptor count mismatch", failures)
    require(accounting["handlerAnchorCount"] == 3, "handler count mismatch", failures)
    require(accounting["helperAnchorCount"] == 3, "helper count mismatch", failures)
    require(accounting["deterministicBitsetVectorCount"] == len(EXPECTED_VECTOR_SLOTS), "vector count mismatch", failures)
    require(accounting["publicCorpusNumericSeedCount"] == 2, "numeric seed count mismatch", failures)
    require(accounting["selectedLooseCorpusRows"] == 18, "loose corpus row mismatch", failures)
    require(accounting["selectedLevelRows"] == 6, "level row mismatch", failures)
    require(accounting["selectedCommandCounts"] == {"GetSlot": 6, "SetSlot": 8, "SetSlotSave": 4}, "command counts mismatch", failures)
    require(accounting["usedSlotDwords"] == 8, "used slot dword count mismatch", failures)
    require(accounting["reservedSlotStorageDwords"] == 32, "reserved slot dword count mismatch", failures)
    require(accounting["falseGuardCount"] == len(FALSE_GUARDS), "false guard count mismatch", failures)
    require(accounting["zeroCounterCount"] == len(ZERO_COUNTERS), "zero counter count mismatch", failures)
    require(accounting["publicLeakCheck"] == "PASS", "public leak check mismatch", failures)

    require(fixture["slotBitsetSaveFixturePlanStatus"] == FIXTURE_STATUS, "fixture plan prerequisite mismatch", failures)
    require(fixture["selectedNextSlice"] == THIS_SLICE, "fixture plan selected next-slice mismatch", failures)
    require(slot["status"] == "PASS", "slot schema prerequisite mismatch", failures)
    require(save["status"] == "PASS", "save schema prerequisite mismatch", failures)
    require(save["container"]["expectedSize"] == 10004, "save expected size mismatch", failures)
    require(save["container"]["versionWord"] == "0x4BD1", "save version mismatch", failures)
    require(save["container"]["trueViewRule"] == "file_offset = 0x0002 + career_offset", "save true-view rule mismatch", failures)

    model = result["codecModel"]
    require(model["slotRange"] == "0..255", "slot range mismatch", failures)
    require(model["usedSlotDwords"] == 8, "model used slot dwords mismatch", failures)
    require(model["reservedSlotStorageDwords"] == 32, "model reserved slot dwords mismatch", failures)
    require(model["slotStorageDwords"] == 32, "model storage dwords mismatch", failures)
    require(model["slotStorageBytes"] == 128, "model storage bytes mismatch", failures)
    require(model["runtimeSlotArray"] == "CGame+0x308", "runtime slot array mismatch", failures)
    require(model["careerSlotsBase"] == "0x240A", "career slot base mismatch", failures)
    require(model["careerSlotsEndExclusive"] == "0x248A", "career slot end mismatch", failures)
    require(model["dwordIndexExpression"] == "slot >> 5", "dword expression mismatch", failures)
    require(model["bitIndexExpression"] == "slot & 31", "bit-index expression mismatch", failures)
    require(model["bitMaskExpression"] == "1 << (slot & 31)", "bit-mask expression mismatch", failures)
    require(model["trueViewOffsetExpression"] == "0x240A + (4 * (slot >> 5))", "true-view expression mismatch", failures)

    expected_vectors = [vector_for_slot(slot_value) for slot_value in EXPECTED_VECTOR_SLOTS]
    require(result["deterministicBitsetVectors"] == expected_vectors, "deterministic vectors do not match recomputed formulas", failures)
    require(all(row["slot"] != 255 for row in result["deterministicBitsetVectors"]), "stale slot 255 vector present", failures)
    require(all(row["dwordIndex"] != 31 for row in result["deterministicBitsetVectors"]), "stale dword 31 vector present", failures)

    combined = result["combinedSeedVector"]
    require(combined["slots"] == [61, 62], "combined seed slots mismatch", failures)
    require(combined["dwordIndex"] == 1, "combined dword mismatch", failures)
    require(combined["combinedMask"] == "0x60000000", "combined mask mismatch", failures)
    require(combined["trueViewOffset"] == "0x240E", "combined true-view offset mismatch", failures)
    require(combined["trueViewDwordRange"] == "0x240E-0x2411", "combined dword range mismatch", failures)
    require(combined["littleEndianByteOffsets"] == ["0x2411"], "combined LE byte offset mismatch", failures)
    require(combined["littleEndianByteMask"] == "0x60", "combined LE byte mask mismatch", failures)
    require(combined["zeroDwordBytesLittleEndian"] == ["0x00", "0x00", "0x00", "0x60"], "combined LE bytes mismatch", failures)
    require(combined["comparisonMode"] == "little-endian dword XOR mask subset, not single-byte expectation", "combined comparison mode mismatch", failures)

    gate = result["deferredCopiedFileProofGate"]
    require(gate["selectedNextSlice"] == NEXT_SLICE, "deferred gate next-slice mismatch", failures)
    require(gate["copiedFileMutationPerformed"] is False, "deferred gate copied-file mutation mismatch", failures)
    require(gate["sourceBaselineRead"] is False, "deferred gate source baseline read mismatch", failures)
    require(gate["privateArtifactMaterialized"] is False, "deferred gate private artifact mismatch", failures)
    require(gate["requiresCopiedRealBaseline"] is True, "deferred gate copied real baseline mismatch", failures)
    require(gate["saveSynthesisAllowed"] is False, "deferred gate save synthesis mismatch", failures)
    require(gate["allowedDwordRange"] == "0x240E-0x2411", "deferred gate allowed dword range mismatch", failures)
    require(gate["allowedDwordXorMask"] == "0x60000000", "deferred gate allowed dword XOR mask mismatch", failures)
    require(gate["slot61Mask"] == "0x20000000", "slot 61 mask mismatch", failures)
    require(gate["slot62Mask"] == "0x40000000", "slot 62 mask mismatch", failures)
    require(gate["unexpectedDiffCount"] == 0, "unexpected diff count mismatch", failures)
    require(gate["legacyTrapHitCount"] == 0, "legacy trap count mismatch", failures)

    guards = result["guardSummary"]
    for key in FALSE_GUARDS:
        require(guards["falseGuards"][key] is False, f"false guard mismatch: {key}", failures)
    for key in ZERO_COUNTERS:
        require(guards["zeroCounters"][key] == 0, f"zero counter mismatch: {key}", failures)
    require("copied-file mutation" in result["claimBoundary"]["doesNotProve"], "claim boundary missing copied-file deferral", failures)
    require("pure deterministic slot bitset codec math for slots 0, 31, 32, 61, and 62" in result["claimBoundary"]["proves"], "claim boundary missing deterministic proof", failures)


def check_docs(failures: list[str]) -> None:
    required_tokens = (
        THIS_SLICE,
        PREVIOUS_SLICE,
        NEXT_SLICE,
        "missionscript-slot-bitset-save-deterministic-codec-proof-plan.v1.json",
        f"slotBitsetSaveDeterministicCodecProofPlanStatus={STATUS_TOKEN}",
        "selectedFixtureFamily=slot-bitset-save",
        "selectedFixturePath=slot-bitset-save-core-handler-and-career-bridge",
        "selectedNextSlice=MissionScript Slot Bitset/Save Copied-File Byte-Diff Proof Plan",
        "sourceProofCount=4",
        "descriptorEntryCount=3",
        "handlerAnchorCount=3",
        "helperAnchorCount=3",
        "deterministicBitsetVectorCount=5",
        "publicCorpusNumericSeedCount=2",
        "selectedLooseCorpusRows=18",
        "selectedLevelRows=6",
        "selectedCommandCounts=GetSlot:6/SetSlot:8/SetSlotSave:4",
        "usedSlotDwords=8",
        "reservedSlotStorageDwords=32",
        "slotStorageDwords=32",
        "slotStorageBytes=128",
        "falseGuardCount=40",
        "zeroCounterCount=29",
        "publicLeakCheck=PASS",
        "latestGhidraBackupClass=verified-static-backup-redacted",
        "0x0052ff30 ScriptCommandRegistry__InitBuiltins",
        "0x0064ce50",
        "0x0064ecd0",
        "0x0064ed10",
        "0x0064ef50",
        "0x005338d0 IScript__SetSlot",
        "0x00533900 IScript__SetSlotSave",
        "0x005339a0 IScript__GetSlotBitValue",
        "0x0046d3a0 CGame__SetSlot",
        "0x0046d410 CGame__GetSlot",
        "0x004214e0 CCareer__SetSlot",
        "0x240A-0x240D",
        "0x240E-0x2411",
        "0x2411",
        "0x00000001",
        "0x80000000",
        "0x20000000",
        "0x40000000",
        "0x60000000",
        "little-endian dword XOR mask subset, not single-byte expectation",
        "unexpectedDiffCount=0",
        "legacyTrapHitCount=0",
        "copiedFileMutation=false",
        "sourceBaselineRead=false",
        "privateArtifactMaterialized=false",
        "saveSynthesis=false",
    )
    for path in (PROOF, READINESS):
        text = read_text(path)
        for token in required_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing token: {token}", failures)
        check_no_bad_public_content(path, failures)
    check_no_bad_public_content(RESULT, failures)

    require(read_text(LORE_PROOF) == read_text(PROOF), "lore proof mirror mismatch", failures)
    require(read_json(LORE_RESULT) == read_json(RESULT), "lore schema mirror mismatch", failures)

    front_door_tokens = (
        THIS_SLICE,
        NEXT_SLICE,
        "missionscript-slot-bitset-save-deterministic-codec-proof-plan.md",
        "missionscript-slot-bitset-save-deterministic-codec-proof-plan.v1.json",
        f"slotBitsetSaveDeterministicCodecProofPlanStatus={STATUS_TOKEN}",
        "selectedFixtureFamily=slot-bitset-save",
        "selectedNextSlice=MissionScript Slot Bitset/Save Copied-File Byte-Diff Proof Plan",
        "deterministicBitsetVectorCount=5",
        "usedSlotDwords=8",
        "reservedSlotStorageDwords=32",
        "falseGuardCount=40",
        "zeroCounterCount=29",
        "publicLeakCheck=PASS",
    )
    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX):
        text = read_text(path)
        for token in front_door_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing front-door token: {token}", failures)
        require(
            f"Active next static child lane: {THIS_SLICE}" not in text,
            f"{path.relative_to(ROOT)} still has stale active deterministic child-lane wording",
            failures,
        )
        require(
            f"The selected active static-to-proof slice is {THIS_SLICE}. Status: selected" not in text,
            f"{path.relative_to(ROOT)} still marks deterministic codec active",
            failures,
        )
        require(
            "Completed MissionScript Slot Bitset/Save Clean-Room Codec Interface Proof" in text,
            f"{path.relative_to(ROOT)} missing completed clean-room codec interface lane",
            failures,
        )
        require(
            "The selected active static-to-proof slice is MissionScript Slot Bitset/Save Clean-Room Codec Interface Proof Plan. Status: selected" not in text,
            f"{path.relative_to(ROOT)} still marks clean-room codec interface active",
            failures,
        )
        require(
            "The selected active static-to-proof slice is Save / Options Byte-Preservation AppCore Implementation Contract Proof Plan. Status: selected" in text
            or "active next static child lane: Save / Options Byte-Preservation AppCore Implementation Contract Proof Plan" in text,
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
        scripts.get("test:missionscript-slot-bitset-save-deterministic-codec-proof-plan")
        == r"py -3 tools\missionscript_slot_bitset_save_deterministic_codec_proof_plan_probe.py --check",
        "missing package deterministic codec proof-plan test script",
        failures,
    )
    for script in (
        "test:missionscript-slot-command-effect-static",
        "test:save-options-controller-byte-preservation-copied-file",
        "test:missionscript-slot-bitset-save-rebuild-fixture-proof-plan",
    ):
        require(script in scripts, f"missing source package script: {script}", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_result(failures)
    check_docs(failures)
    check_package(failures)
    require(no_bea_process_running(), "BEA.exe process is running after deterministic codec proof", failures)

    if failures:
        print("MissionScript slot bitset/save deterministic codec proof-plan probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
        print("MissionScript slot bitset/save deterministic codec proof-plan probe: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
