#!/usr/bin/env python3
"""Validate MissionScript slot bitset/save copied-file byte-diff proof artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PREVIOUS_PRIVATE_DIR = ROOT / "subagents" / "static-to-proof" / "save-options-controller-byte-preservation-copied-file-proof"
SOURCE_COPIED_BASELINE = PREVIOUS_PRIVATE_DIR / "career-baseline.bes"
PRIVATE_DIR = ROOT / "subagents" / "static-to-proof" / "missionscript-slot-bitset-save-copied-file-byte-diff-proof"
PRIVATE_SUMMARY = PRIVATE_DIR / "evidence-summary.private.json"

PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-slot-bitset-save-copied-file-byte-diff-proof.md"
RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-slot-bitset-save-copied-file-byte-diff.v1.json"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-slot-bitset-save-copied-file-byte-diff-proof.md"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-slot-bitset-save-copied-file-byte-diff.v1.json"
READINESS = ROOT / "release" / "readiness" / "missionscript_slot_bitset_save_copied_file_byte_diff_2026-06-09.md"

DETERMINISTIC_PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-slot-bitset-save-deterministic-codec-proof-plan.md"
DETERMINISTIC_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-slot-bitset-save-deterministic-codec-proof-plan.v1.json"
SAVE_COPIED_FILE_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "save-options-controller-byte-preservation-copied-file.v1.json"
SLOT_COMMAND_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-slot-command-effect.v1.json"

BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
LORE_MAPPED = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
LORE_BIN_INDEX = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
LORE_RE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"
PACKAGE_JSON = ROOT / "package.json"

THIS_SLICE = "MissionScript Slot Bitset/Save Copied-File Byte-Diff Proof"
THIS_STATUS = "missionscript-slot-bitset-save-copied-file-byte-diff-complete-copied-real-baseline-not-runtime-proof"
PREVIOUS_SLICE = "MissionScript Slot Bitset/Save Deterministic Codec Proof Plan"
PREVIOUS_STATUS = "missionscript-slot-bitset-save-deterministic-codec-proof-plan-complete-pure-codec-not-runtime-proof"
NEXT_SLICE = "MissionScript Slot Bitset/Save Clean-Room Codec Interface Proof Plan"
ACTIVE_SLICE = "Save / Options Byte-Preservation AppCore Implementation Contract Proof Plan"

EXPECTED_SIZE = 10004
EXPECTED_SIZE_HEX = "0x2714"
VERSION_WORD = 0x4BD1
VERSION_WORD_HEX = "0x4BD1"
TRUE_VIEW_RULE = "file_offset = 0x0002 + career_offset"
SLOT_DWORD0_OFFSET = 0x240A
SLOT_DWORD1_OFFSET = 0x240E
SLOT_DWORD1_END_EXCLUSIVE = 0x2412
TARGET_MASK = 0x60000000
SLOT61_MASK = 0x20000000
SLOT62_MASK = 0x40000000
EXPECTED_CHANGED_OFFSETS = (0x2411,)
LEGACY_TRAPS = (0x23A4, 0x22D4, 0x240C)

PRESERVE_RANGES = {
    "killCountersAndPreSlotTail": (0x23F6, 0x240A),
    "slotDword0": (0x240A, 0x240E),
    "remainingSlotDwordsAfterTarget": (0x2412, 0x248A),
    "postSlotFieldsThroughPreOptions": (0x248A, 0x24BE),
    "optionsEntries": (0x24BE, 0x26BE),
    "optionsTail": (0x26BE, 0x2714),
}

PRIVATE_FILES = {
    "baseline": "career-slot-baseline.bes",
    "noop": "career-slot-noop.bes",
    "set": "career-slot61-62-set.bes",
    "idempotent": "career-slot61-62-idempotent-set.bes",
    "clear": "career-slot61-62-clear-roundtrip.bes",
}

PUBLIC_FORBIDDEN_TOKENS = (
    "C:\\Users",
    "Program Files",
    "steamapps",
    "save-attempts",
    "game\\savegames",
    '"sourcePath":',
    '"sourcePaths":',
    "sha256",
    "f6581d041e444a8d836f089af1a5dbba6222cca79fe4917e9323fd43a357de50",
    "37ae23d38bfc35f3ed91f64bc3925533e73f583d8d2aa43d2ed6dae9a4f8ce6c",
    "onslaught_codex_directive",
    "password",
    "token=",
)

FORBIDDEN_OVERCLAIMS = (
    "runtime missionscript execution proven",
    "runtime command effects proven",
    "runtime slot persistence proven",
    "runtime save/load behavior proven",
    "tutorial progression proven",
    "live loose-msl loading proven",
    "packed-resource script selection proven",
    "defaultoptions mutation complete",
    "installed game mutation proven",
    "original executable mutation",
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


def read_bytes(path: Path) -> bytes:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_bytes()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hex_offset(value: int) -> str:
    return f"0x{value:04X}"


def hex32(value: int) -> str:
    return f"0x{value:08X}"


def version_word(data: bytes) -> int:
    return int.from_bytes(data[0:2], "little")


def read_u32(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset : offset + 4], "little")


def write_u32(buffer: bytearray, offset: int, value: int) -> None:
    buffer[offset : offset + 4] = value.to_bytes(4, "little")


def changed_offsets(before: bytes, after: bytes) -> list[int]:
    if len(before) != len(after):
        raise ValueError("cannot diff buffers with different lengths")
    return [idx for idx, (left, right) in enumerate(zip(before, after)) if left != right]


def range_unchanged(before: bytes, after: bytes, start: int, end: int) -> bool:
    return before[start:end] == after[start:end]


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def require_container(label: str, data: bytes) -> None:
    if len(data) != EXPECTED_SIZE:
        raise ValueError(f"{label}: expected {EXPECTED_SIZE}, got {len(data)}")
    actual = version_word(data)
    if actual != VERSION_WORD:
        raise ValueError(f"{label}: expected version {VERSION_WORD_HEX}, got 0x{actual:04X}")


def file_row(label: str, relative: str, data: bytes) -> dict[str, Any]:
    return {
        "label": label,
        "relativePath": relative,
        "size": len(data),
        "versionWord": f"0x{version_word(data):04X}",
        "sha256": sha256(data),
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


def write_private_evidence() -> dict[str, Any]:
    PRIVATE_DIR.mkdir(parents=True, exist_ok=True)

    source_data = read_bytes(SOURCE_COPIED_BASELINE)
    require_container("source copied career baseline", source_data)

    baseline_path = PRIVATE_DIR / PRIVATE_FILES["baseline"]
    noop_path = PRIVATE_DIR / PRIVATE_FILES["noop"]
    set_path = PRIVATE_DIR / PRIVATE_FILES["set"]
    idempotent_path = PRIVATE_DIR / PRIVATE_FILES["idempotent"]
    clear_path = PRIVATE_DIR / PRIVATE_FILES["clear"]

    shutil.copyfile(SOURCE_COPIED_BASELINE, baseline_path)
    shutil.copyfile(baseline_path, noop_path)

    baseline = read_bytes(baseline_path)
    source_copy_diff = changed_offsets(source_data, baseline)
    before_dword = read_u32(baseline, SLOT_DWORD1_OFFSET)
    baseline_selected_mask_clear = (before_dword & TARGET_MASK) == 0
    set_dword = before_dword | TARGET_MASK
    set_buffer = bytearray(baseline)
    write_u32(set_buffer, SLOT_DWORD1_OFFSET, set_dword)
    set_path.write_bytes(bytes(set_buffer))

    set_data = read_bytes(set_path)
    idempotent_buffer = bytearray(set_data)
    write_u32(idempotent_buffer, SLOT_DWORD1_OFFSET, read_u32(idempotent_buffer, SLOT_DWORD1_OFFSET) | TARGET_MASK)
    idempotent_path.write_bytes(bytes(idempotent_buffer))

    clear_buffer = bytearray(set_data)
    write_u32(clear_buffer, SLOT_DWORD1_OFFSET, read_u32(clear_buffer, SLOT_DWORD1_OFFSET) & ~TARGET_MASK)
    clear_path.write_bytes(bytes(clear_buffer))

    noop = read_bytes(noop_path)
    set_data = read_bytes(set_path)
    idempotent = read_bytes(idempotent_path)
    clear = read_bytes(clear_path)
    source_after = read_bytes(SOURCE_COPIED_BASELINE)

    for label, data in (
        ("baseline", baseline),
        ("noop", noop),
        ("set", set_data),
        ("idempotent", idempotent),
        ("clear", clear),
    ):
        require_container(label, data)

    baseline_to_noop = changed_offsets(baseline, noop)
    baseline_to_set = changed_offsets(baseline, set_data)
    set_to_idempotent = changed_offsets(set_data, idempotent)
    set_to_clear = changed_offsets(set_data, clear)
    clear_to_baseline = changed_offsets(clear, baseline)
    observed_xor = read_u32(baseline, SLOT_DWORD1_OFFSET) ^ read_u32(set_data, SLOT_DWORD1_OFFSET)
    clear_xor = read_u32(set_data, SLOT_DWORD1_OFFSET) ^ read_u32(clear, SLOT_DWORD1_OFFSET)

    unexpected = [
        offset
        for offset in baseline_to_set
        if not (SLOT_DWORD1_OFFSET <= offset < SLOT_DWORD1_END_EXCLUSIVE)
    ]
    trap_hits = [offset for offset in baseline_to_set if offset in LEGACY_TRAPS]

    preservation = {
        name: range_unchanged(baseline, set_data, start, end)
        for name, (start, end) in PRESERVE_RANGES.items()
    }

    summary = {
        "schemaVersion": "missionscript-slot-bitset-save-copied-file-byte-diff-private-evidence.v1",
        "status": "PASS",
        "evidenceRoot": "subagents/static-to-proof/missionscript-slot-bitset-save-copied-file-byte-diff-proof/",
        "sourceCopiedBaseline": {
            "class": "validated copied real career .bes baseline from prior ignored evidence",
            "relativePath": "subagents/static-to-proof/save-options-controller-byte-preservation-copied-file-proof/career-baseline.bes",
            "size": len(source_data),
            "versionWord": f"0x{version_word(source_data):04X}",
            "sha256": sha256(source_data),
        },
        "provenance": {
            "copyBeforeWrite": True,
            "sourceAndOutputPathsDistinct": SOURCE_COPIED_BASELINE.resolve() != baseline_path.resolve(),
            "sourceToNewBaselineDiffCount": len(source_copy_diff),
            "sourceUnchanged": source_data == source_after,
        },
        "copiedArtifacts": [
            file_row("slot baseline", PRIVATE_FILES["baseline"], baseline),
            file_row("slot noop", PRIVATE_FILES["noop"], noop),
            file_row("slot61/62 set", PRIVATE_FILES["set"], set_data),
            file_row("slot61/62 idempotent set", PRIVATE_FILES["idempotent"], idempotent),
            file_row("slot61/62 clear roundtrip", PRIVATE_FILES["clear"], clear),
        ],
        "container": {
            "expectedSize": EXPECTED_SIZE,
            "expectedSizeHex": EXPECTED_SIZE_HEX,
            "versionWord": VERSION_WORD_HEX,
            "trueViewRule": TRUE_VIEW_RULE,
            "fileSizePreserved": all(len(data) == EXPECTED_SIZE for data in (baseline, noop, set_data, idempotent, clear)),
            "versionWordPreserved": all(version_word(data) == VERSION_WORD for data in (baseline, noop, set_data, idempotent, clear)),
        },
        "slotWrite": {
            "slots": [61, 62],
            "dwordIndex": 1,
            "allowedDwordRange": "0x240E-0x2411",
            "allowedDwordXorMask": "0x60000000",
            "slot61Mask": "0x20000000",
            "slot62Mask": "0x40000000",
            "comparisonMode": "little-endian dword XOR mask subset, not single-byte expectation",
            "baselineDword1Before": hex32(before_dword),
            "baselineSelectedMaskInitiallyClear": baseline_selected_mask_clear,
            "setDword1After": hex32(read_u32(set_data, SLOT_DWORD1_OFFSET)),
            "observedDwordXorMask": hex32(observed_xor),
            "clearDwordXorMask": hex32(clear_xor),
            "baselineToSetChangedOffsets": [hex_offset(offset) for offset in baseline_to_set],
            "baselineToSetChangedOffsetCount": len(baseline_to_set),
            "expectedChangedOffsets": [hex_offset(offset) for offset in EXPECTED_CHANGED_OFFSETS],
            "unexpectedOffsets": [hex_offset(offset) for offset in unexpected],
            "unexpectedDiffCount": len(unexpected),
            "legacyTrapHits": [hex_offset(offset) for offset in trap_hits],
            "legacyTrapHitCount": len(trap_hits),
            "setChangedTargetBits": observed_xor == TARGET_MASK,
            "preservedNonTargetBitsInDword": (before_dword & ~TARGET_MASK) == (read_u32(set_data, SLOT_DWORD1_OFFSET) & ~TARGET_MASK),
        },
        "noOpAndRoundTrip": {
            "baselineToNoopDiffCount": len(baseline_to_noop),
            "setToIdempotentDiffCount": len(set_to_idempotent),
            "setToClearChangedOffsets": [hex_offset(offset) for offset in set_to_clear],
            "setToClearDiffCount": len(set_to_clear),
            "setToClearDwordXorMask": hex32(clear_xor),
            "clearToBaselineDiffCount": len(clear_to_baseline),
        },
        "preservation": preservation,
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
            "legacyAlignedViewTrapOffsets": [hex_offset(offset) for offset in LEGACY_TRAPS],
            "legacyTrapHitCount": len(trap_hits),
        },
    }

    failures: list[str] = []
    validate_private_summary(summary, failures, check_files=True)
    if failures:
        raise ValueError("; ".join(failures))
    write_json(PRIVATE_SUMMARY, summary)
    return summary


def public_schema_from_summary(summary: dict[str, Any]) -> dict[str, Any]:
    slot = summary["slotWrite"]
    roundtrip = summary["noOpAndRoundTrip"]
    return {
        "schemaVersion": "missionscript-slot-bitset-save-copied-file-byte-diff.v1",
        "status": "PASS",
        "slotBitsetSaveCopiedFileByteDiffStatus": THIS_STATUS,
        "previousSlice": PREVIOUS_SLICE,
        "selectedNextSlice": NEXT_SLICE,
        "selectedFixtureFamily": "slot-bitset-save",
        "selectedFixturePath": "slot-bitset-save-core-handler-and-career-bridge",
        "privateEvidence": {
            "privateEvidenceRootPublic": False,
            "sourcePathsPublic": False,
            "sourceHashesPublic": False,
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
            "expectedSize": EXPECTED_SIZE,
            "expectedSizeHex": EXPECTED_SIZE_HEX,
            "versionWord": VERSION_WORD_HEX,
            "trueViewRule": TRUE_VIEW_RULE,
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
                "a copied real career .bes baseline can be copied, no-oped, and modified without changing file size or version word",
                "setting slots 61 and 62 changes only the true-view target dword range 0x240E-0x2411",
                "the observed little-endian dword XOR mask for the set operation is 0x60000000",
                "slot dword 0, non-target slot storage, post-slot fields, options entries, options tail, and legacy trap offsets are preserved",
                "reapplying the set operation is idempotent and clearing the target bits roundtrips to the copied baseline",
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
                "defaultoptions mutation",
                "installed game mutation",
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
    schema = public_schema_from_summary(summary)
    write_json(RESULT, schema)
    write_json(LORE_RESULT, schema)
    return schema


def validate_private_summary(summary: dict[str, Any], failures: list[str], check_files: bool = False) -> None:
    require(summary.get("schemaVersion") == "missionscript-slot-bitset-save-copied-file-byte-diff-private-evidence.v1", "private schema mismatch", failures)
    require(summary.get("status") == "PASS", "private status mismatch", failures)
    require(summary["container"]["fileSizePreserved"] is True, "private file-size preservation mismatch", failures)
    require(summary["container"]["versionWordPreserved"] is True, "private version preservation mismatch", failures)
    require(summary["provenance"]["copyBeforeWrite"] is True, "private copy-before-write mismatch", failures)
    require(summary["provenance"]["sourceAndOutputPathsDistinct"] is True, "private path distinctness mismatch", failures)
    require(summary["provenance"]["sourceToNewBaselineDiffCount"] == 0, "private source-to-baseline copy mismatch", failures)
    require(summary["provenance"]["sourceUnchanged"] is True, "private source unchanged mismatch", failures)
    slot = summary["slotWrite"]
    require(slot["slots"] == [61, 62], "private slots mismatch", failures)
    require(slot["dwordIndex"] == 1, "private dword index mismatch", failures)
    require(slot["allowedDwordRange"] == "0x240E-0x2411", "private range mismatch", failures)
    require(slot["allowedDwordXorMask"] == "0x60000000", "private target mask mismatch", failures)
    require(slot["baselineSelectedMaskInitiallyClear"] is True, "private target mask precondition mismatch", failures)
    require(slot["observedDwordXorMask"] == "0x60000000", "private observed XOR mismatch", failures)
    require(slot["baselineToSetChangedOffsets"] == ["0x2411"], "private changed offsets mismatch", failures)
    require(slot["unexpectedDiffCount"] == 0, "private unexpected diff mismatch", failures)
    require(slot["legacyTrapHitCount"] == 0, "private trap hit mismatch", failures)
    require(slot["setChangedTargetBits"] is True, "private target bits were not changed", failures)
    require(slot["preservedNonTargetBitsInDword"] is True, "private non-target bits not preserved", failures)
    roundtrip = summary["noOpAndRoundTrip"]
    require(roundtrip["baselineToNoopDiffCount"] == 0, "private noop diff mismatch", failures)
    require(roundtrip["setToIdempotentDiffCount"] == 0, "private idempotent diff mismatch", failures)
    require(roundtrip["setToClearDwordXorMask"] == "0x60000000", "private clear XOR mismatch", failures)
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
    ):
        require(summary["negativeGuards"][key] is False, f"private guard mismatch: {key}", failures)

    if not check_files:
        return

    artifacts = {row["relativePath"]: row for row in summary["copiedArtifacts"]}
    for relative in PRIVATE_FILES.values():
        path = PRIVATE_DIR / relative
        require(path.is_file(), f"missing private artifact: {relative}", failures)
        if path.is_file():
            data = path.read_bytes()
            require(len(data) == EXPECTED_SIZE, f"{relative} size mismatch", failures)
            require(version_word(data) == VERSION_WORD, f"{relative} version mismatch", failures)
            require(artifacts.get(relative, {}).get("sha256") == sha256(data), f"{relative} hash mismatch", failures)


def check_public_schema(failures: list[str]) -> None:
    summary = read_json(PRIVATE_SUMMARY)
    validate_private_summary(summary, failures, check_files=True)
    expected = public_schema_from_summary(summary)
    for path in (RESULT, LORE_RESULT):
        actual = read_json(path)
        require(actual == expected, f"{path.relative_to(ROOT)} does not match private-evidence-derived public schema", failures)
        require(actual["slotBitsetSaveCopiedFileByteDiffStatus"] == THIS_STATUS, "public status token mismatch", failures)
        require(actual["selectedNextSlice"] == NEXT_SLICE, "public next slice mismatch", failures)
        require(actual["privateEvidence"]["sourcePathsPublic"] is False, "public source path disclosure mismatch", failures)
        require(actual["privateEvidence"]["sourceHashesPublic"] is False, "public source hash disclosure mismatch", failures)
        require(actual["privateEvidence"]["artifactHashesPublic"] is False, "public artifact hash disclosure mismatch", failures)
        require(actual["privateEvidence"]["rawBeforeAfterDwordsPublic"] is False, "public raw dword disclosure mismatch", failures)
        require(actual["privateEvidence"]["copyBeforeWrite"] is True, "public copy-before-write mismatch", failures)
        require(actual["privateEvidence"]["sourceAndOutputPathsDistinct"] is True, "public path distinctness mismatch", failures)
        require(actual["privateEvidence"]["sourceToNewBaselineDiffCount"] == 0, "public source-to-baseline copy mismatch", failures)
        require(actual["privateEvidence"]["sourceUnchanged"] is True, "public source unchanged mismatch", failures)
        require(actual["slotWrite"]["observedDwordXorMask"] == "0x60000000", "public observed XOR mismatch", failures)
        require(actual["slotWrite"]["baselineSelectedMaskInitiallyClear"] is True, "public target mask precondition mismatch", failures)
        require(actual["slotWrite"]["baselineToSetChangedOffsets"] == ["0x2411"], "public changed offset mismatch", failures)
        require(actual["slotWrite"]["unexpectedDiffCount"] == 0, "public unexpected diff mismatch", failures)
        require(actual["slotWrite"]["legacyTrapHitCount"] == 0, "public trap hit mismatch", failures)
        require(actual["noOpAndRoundTrip"]["baselineToNoopDiffCount"] == 0, "public noop mismatch", failures)
        require(actual["noOpAndRoundTrip"]["setToIdempotentDiffCount"] == 0, "public idempotent mismatch", failures)
        require(actual["noOpAndRoundTrip"]["clearToBaselineDiffCount"] == 0, "public clear roundtrip mismatch", failures)
        check_no_public_leaks(path, failures)


def check_no_public_leaks(path: Path, failures: list[str]) -> None:
    text = read_text(path)
    lower = text.lower()
    for token in PUBLIC_FORBIDDEN_TOKENS:
        require(token.lower() not in lower, f"{path.relative_to(ROOT)} leaks forbidden public token: {token}", failures)
    for phrase in FORBIDDEN_OVERCLAIMS:
        require(phrase not in lower, f"{path.relative_to(ROOT)} overclaims forbidden category: {phrase}", failures)


def check_source_prerequisites(failures: list[str]) -> None:
    deterministic = read_json(DETERMINISTIC_SCHEMA)
    save = read_json(SAVE_COPIED_FILE_SCHEMA)
    slot = read_json(SLOT_COMMAND_SCHEMA)
    require(deterministic["slotBitsetSaveDeterministicCodecProofPlanStatus"] == PREVIOUS_STATUS, "deterministic prerequisite mismatch", failures)
    require(deterministic["deferredCopiedFileProofGate"]["selectedNextSlice"] == "MissionScript Slot Bitset/Save Copied-File Byte-Diff Proof Plan", "deterministic next-slice mismatch", failures)
    require(deterministic["deferredCopiedFileProofGate"]["allowedDwordRange"] == "0x240E-0x2411", "deterministic allowed range mismatch", failures)
    require(deterministic["deferredCopiedFileProofGate"]["allowedDwordXorMask"] == "0x60000000", "deterministic target mask mismatch", failures)
    require(save["status"] == "PASS", "save copied-file prerequisite mismatch", failures)
    require(save["container"]["expectedSize"] == EXPECTED_SIZE, "save copied-file size mismatch", failures)
    require(save["container"]["versionWord"] == VERSION_WORD_HEX, "save copied-file version mismatch", failures)
    require(save["container"]["trueViewRule"] == TRUE_VIEW_RULE, "save copied-file true-view mismatch", failures)
    require(slot["status"] == "PASS", "slot command-effect prerequisite mismatch", failures)


def check_docs(failures: list[str]) -> None:
    required_tokens = (
        THIS_SLICE,
        THIS_STATUS,
        PREVIOUS_SLICE,
        NEXT_SLICE,
        "missionscript-slot-bitset-save-copied-file-byte-diff.v1.json",
        "selectedFixtureFamily=slot-bitset-save",
        "selectedFixturePath=slot-bitset-save-core-handler-and-career-bridge",
        "selectedNextSlice=MissionScript Slot Bitset/Save Clean-Room Codec Interface Proof Plan",
        "copiedArtifactCount=5",
        "sourcePathsPublic=false",
        "sourceHashesPublic=false",
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
        "baselineSelectedMaskInitiallyClear=true",
        "baselineToSetChangedOffsets=0x2411",
        "unexpectedDiffCount=0",
        "legacyTrapHitCount=0",
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
        "missionscript-slot-bitset-save-copied-file-byte-diff-proof.md",
        "missionscript-slot-bitset-save-copied-file-byte-diff.v1.json",
        "observedDwordXorMask=0x60000000",
        "baselineToSetChangedOffsets=0x2411",
        "clearToBaselineDiffCount=0",
        "selectedNextSlice=MissionScript Slot Bitset/Save Clean-Room Codec Interface Proof Plan",
    )
    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX):
        text = read_text(path)
        for token in front_door_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing front-door token: {token}", failures)
        require(
            "The selected active static-to-proof slice is MissionScript Slot Bitset/Save Copied-File Byte-Diff Proof Plan. Status: selected" not in text,
            f"{path.relative_to(ROOT)} still marks copied-file byte-diff lane as active",
            failures,
        )
        require(
            "Completed MissionScript Slot Bitset/Save Clean-Room Codec Interface Proof" in text,
            f"{path.relative_to(ROOT)} missing completed clean-room codec interface lane",
            failures,
        )
        require(
            f"The selected active static-to-proof slice is {NEXT_SLICE}. Status: selected" not in text,
            f"{path.relative_to(ROOT)} still marks clean-room codec interface lane active",
            failures,
        )
        require(
            f"The selected active static-to-proof slice is {ACTIVE_SLICE}. Status: selected" in text
            or f"active next static child lane: {ACTIVE_SLICE}" in text,
            f"{path.relative_to(ROOT)} missing active AppCore copied-baseline codec harness lane",
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
        scripts.get("test:missionscript-slot-bitset-save-copied-file-byte-diff")
        == r"py -3 tools\missionscript_slot_bitset_save_copied_file_byte_diff_probe.py --check",
        "missing copied-file byte-diff package script",
        failures,
    )
    for script in (
        "test:missionscript-slot-bitset-save-deterministic-codec-proof-plan",
        "test:save-options-controller-byte-preservation-copied-file",
        "test:missionscript-slot-command-effect-static",
    ):
        require(script in scripts, f"missing prerequisite package script: {script}", failures)


def run_check() -> list[str]:
    failures: list[str] = []
    check_source_prerequisites(failures)
    check_public_schema(failures)
    check_docs(failures)
    check_package(failures)
    require(no_bea_process_running(), "BEA.exe process is running after copied-file byte-diff proof", failures)
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write-private-evidence", action="store_true")
    parser.add_argument("--write-schema", action="store_true")
    args = parser.parse_args()

    if args.write_private_evidence:
        summary = write_private_evidence()
        print(f"Wrote {PRIVATE_SUMMARY.relative_to(ROOT)}")
        print(f"Private evidence status: {summary['status']}")

    if args.write_schema:
        schema = write_public_schema()
        print(f"Wrote {RESULT.relative_to(ROOT)}")
        print(f"Wrote {LORE_RESULT.relative_to(ROOT)}")
        print(f"Public schema status: {schema['status']}")

    if args.check or not (args.write_private_evidence or args.write_schema):
        failures = run_check()
        if failures:
            print("MissionScript slot bitset/save copied-file byte-diff proof probe: FAIL")
            for failure in failures:
                print(f"- {failure}")
            return 1
        print("MissionScript slot bitset/save copied-file byte-diff proof probe: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
