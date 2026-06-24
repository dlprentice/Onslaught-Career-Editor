#!/usr/bin/env python3
"""Validate copied-file save/options byte-preservation proof artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PRIVATE_DIR = ROOT / "subagents" / "static-to-proof" / "save-options-controller-byte-preservation-copied-file-proof"
PRIVATE_SUMMARY = PRIVATE_DIR / "evidence-summary.private.json"

SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "save-options-controller-byte-preservation-copied-file.v1.json"
LORE_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "save-options-controller-byte-preservation-copied-file.v1.json"
PROOF = ROOT / "reverse-engineering" / "binary-analysis" / "save-options-controller-byte-preservation-copied-file-proof.md"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "save-options-controller-byte-preservation-copied-file-proof.md"
PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "save-options-controller-byte-preservation-proof-plan.md"
READINESS = ROOT / "release" / "readiness" / "save_options_controller_byte_preservation_copied_file_proof_2026-06-08.md"

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
CAREER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Career.cpp" / "_index.md"
LORE_CAREER_DOC = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "functions" / "Career.cpp" / "_index.md"
PACKAGE_JSON = ROOT / "package.json"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"

EXPECTED_SIZE = 10004
VERSION_WORD = 0x4BD1
KILL_AIRCRAFT_OFFSET = 0x23F6
KILL_AIRCRAFT_META_OFFSET = 0x23F9
KILL_LOWER24_ALLOWED = tuple(range(0x23F6, 0x23F9))
GOODIE_RESERVED_RANGE = (0x22EA, 0x23F6)
TECH_SLOTS_RANGE = (0x240A, 0x248A)
OPTIONS_ENTRIES_RANGE = (0x24BE, 0x26BE)
OPTIONS_TAIL_RANGE = (0x26BE, 0x2714)
LEGACY_TRAPS = (0x23A4, 0x22D4, 0x240C)

PROOF_LINK = "save-options-controller-byte-preservation-copied-file-proof.md"
SCHEMA_LINK = "save-options-controller-byte-preservation-copied-file.v1.json"
PLAN_LINK = "save-options-controller-byte-preservation-proof-plan.md"
PRIVATE_EVIDENCE_ROOT = "subagents/static-to-proof/save-options-controller-byte-preservation-copied-file-proof/"
LATEST_GHIDRA_BACKUP = r"G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified"

FORBIDDEN_PUBLIC_TOKENS = (
    "C:\\Users",
    "Program Files",
    ".env",
    "save-attempts",
    "onslaught_codex_directive",
    "password",
    "token=",
)

FORBIDDEN_OVERCLAIMS = (
    "runtime save/load behavior proven",
    "runtime defaultoptions boot behavior proven",
    "runtime menu behavior proven",
    "runtime controller remap/input behavior proven",
    "runtime goodies wall behavior proven",
    "exact source-layout parity proven",
    "bea patching behavior proven",
    "visual qa complete",
    "godot parity proven",
    "rebuild parity proven",
    "no-noticeable-difference parity proven",
    "runtime proof complete",
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


def version_word(data: bytes) -> int:
    return int.from_bytes(data[0:2], "little")


def read_u32(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset : offset + 4], "little")


def write_u32(buffer: bytearray, offset: int, value: int) -> None:
    buffer[offset : offset + 4] = value.to_bytes(4, "little")


def changed_offsets(before: bytes, after: bytes) -> list[int]:
    if len(before) != len(after):
        raise ValueError("cannot diff buffers with different lengths")
    return [index for index, (left, right) in enumerate(zip(before, after)) if left != right]


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def require_container(label: str, data: bytes) -> None:
    if len(data) != EXPECTED_SIZE:
        raise ValueError(f"{label}: expected {EXPECTED_SIZE} bytes, got {len(data)}")
    actual_version = version_word(data)
    if actual_version != VERSION_WORD:
        raise ValueError(f"{label}: expected version 0x{VERSION_WORD:04X}, got 0x{actual_version:04X}")


def range_unchanged(before: bytes, after: bytes, start: int, end: int) -> bool:
    return before[start:end] == after[start:end]


def summarize_copy(label: str, relative_path: str, data: bytes) -> dict[str, Any]:
    return {
        "label": label,
        "relativePath": relative_path,
        "size": len(data),
        "versionWord": f"0x{version_word(data):04X}",
        "sha256": sha256(data),
    }


def generate_private_evidence(career_source: Path, defaultoptions_source: Path) -> dict[str, Any]:
    PRIVATE_DIR.mkdir(parents=True, exist_ok=True)

    career_source = career_source.resolve()
    defaultoptions_source = defaultoptions_source.resolve()
    career_data = read_bytes(career_source)
    defaultoptions_data = read_bytes(defaultoptions_source)
    require_container("career source", career_data)
    require_container("defaultoptions source", defaultoptions_data)

    career_baseline = PRIVATE_DIR / "career-baseline.bes"
    defaultoptions_baseline = PRIVATE_DIR / "defaultoptions-baseline.bea"
    career_noop = PRIVATE_DIR / "career-noop.bes"
    defaultoptions_noop = PRIVATE_DIR / "defaultoptions-noop.bea"
    career_edit = PRIVATE_DIR / "career-aircraft-kill-lower24-edit.bes"

    shutil.copyfile(career_source, career_baseline)
    shutil.copyfile(defaultoptions_source, defaultoptions_baseline)
    shutil.copyfile(career_baseline, career_noop)
    shutil.copyfile(defaultoptions_baseline, defaultoptions_noop)

    edit_buffer = bytearray(read_bytes(career_baseline))
    old_raw = read_u32(edit_buffer, KILL_AIRCRAFT_OFFSET)
    old_lower24 = old_raw & 0x00FFFFFF
    new_lower24 = (old_lower24 + 1) & 0x00FFFFFF
    if new_lower24 == old_lower24:
        new_lower24 = (old_lower24 + 2) & 0x00FFFFFF
    new_raw = (old_raw & 0xFF000000) | new_lower24
    write_u32(edit_buffer, KILL_AIRCRAFT_OFFSET, new_raw)
    career_edit.write_bytes(bytes(edit_buffer))

    career_baseline_data = read_bytes(career_baseline)
    defaultoptions_baseline_data = read_bytes(defaultoptions_baseline)
    career_noop_data = read_bytes(career_noop)
    defaultoptions_noop_data = read_bytes(defaultoptions_noop)
    career_edit_data = read_bytes(career_edit)

    for label, data in (
        ("career baseline", career_baseline_data),
        ("defaultoptions baseline", defaultoptions_baseline_data),
        ("career noop", career_noop_data),
        ("defaultoptions noop", defaultoptions_noop_data),
        ("career edit", career_edit_data),
    ):
        require_container(label, data)

    career_noop_diffs = changed_offsets(career_baseline_data, career_noop_data)
    defaultoptions_noop_diffs = changed_offsets(defaultoptions_baseline_data, defaultoptions_noop_data)
    edit_diffs = changed_offsets(career_baseline_data, career_edit_data)
    unexpected = [offset for offset in edit_diffs if offset not in KILL_LOWER24_ALLOWED]
    trap_hits = [offset for offset in edit_diffs if offset in LEGACY_TRAPS]

    summary = {
        "schemaVersion": "save-options-controller-byte-preservation-private-evidence.v1",
        "status": "PASS",
        "evidenceRoot": PRIVATE_EVIDENCE_ROOT,
        "sourcePathDisclosure": "private evidence only; public schema omits source paths and source hashes",
        "inputs": [
            {
                "label": "real career .bes baseline",
                "sourcePath": str(career_source),
                "size": len(career_data),
                "versionWord": f"0x{version_word(career_data):04X}",
                "sha256": sha256(career_data),
            },
            {
                "label": "real defaultoptions.bea baseline",
                "sourcePath": str(defaultoptions_source),
                "size": len(defaultoptions_data),
                "versionWord": f"0x{version_word(defaultoptions_data):04X}",
                "sha256": sha256(defaultoptions_data),
            },
        ],
        "copiedArtifacts": [
            summarize_copy("career baseline", "career-baseline.bes", career_baseline_data),
            summarize_copy("defaultoptions baseline", "defaultoptions-baseline.bea", defaultoptions_baseline_data),
            summarize_copy("career noop", "career-noop.bes", career_noop_data),
            summarize_copy("defaultoptions noop", "defaultoptions-noop.bea", defaultoptions_noop_data),
            summarize_copy("career aircraft kill lower24 edit", "career-aircraft-kill-lower24-edit.bes", career_edit_data),
        ],
        "noOpPreservation": {
            "careerDiffCount": len(career_noop_diffs),
            "defaultoptionsDiffCount": len(defaultoptions_noop_diffs),
        },
        "scopedCareerEdit": {
            "field": "Aircraft kill counter lower-24 payload",
            "baseOffset": hex_offset(KILL_AIRCRAFT_OFFSET),
            "metadataOffset": hex_offset(KILL_AIRCRAFT_META_OFFSET),
            "allowedOffsets": [hex_offset(offset) for offset in KILL_LOWER24_ALLOWED],
            "changedOffsets": [hex_offset(offset) for offset in edit_diffs],
            "changedOffsetCount": len(edit_diffs),
            "unexpectedOffsets": [hex_offset(offset) for offset in unexpected],
            "unexpectedDiffCount": len(unexpected),
            "legacyTrapHits": [hex_offset(offset) for offset in trap_hits],
            "legacyTrapHitCount": len(trap_hits),
            "metadataBytePreserved": career_baseline_data[KILL_AIRCRAFT_META_OFFSET] == career_edit_data[KILL_AIRCRAFT_META_OFFSET],
            "lower24Changed": (old_raw & 0x00FFFFFF) != (read_u32(career_edit_data, KILL_AIRCRAFT_OFFSET) & 0x00FFFFFF),
            "topByteBefore": f"0x{(old_raw >> 24) & 0xFF:02X}",
            "topByteAfter": f"0x{(read_u32(career_edit_data, KILL_AIRCRAFT_OFFSET) >> 24) & 0xFF:02X}",
            "goodieReservedRangeUnchanged": range_unchanged(career_baseline_data, career_edit_data, *GOODIE_RESERVED_RANGE),
            "techSlotsRangeUnchanged": range_unchanged(career_baseline_data, career_edit_data, *TECH_SLOTS_RANGE),
            "optionsEntriesUnchanged": range_unchanged(career_baseline_data, career_edit_data, *OPTIONS_ENTRIES_RANGE),
            "optionsTailUnchanged": range_unchanged(career_baseline_data, career_edit_data, *OPTIONS_TAIL_RANGE),
            "fileSizePreserved": len(career_baseline_data) == len(career_edit_data) == EXPECTED_SIZE,
            "versionWordPreserved": version_word(career_baseline_data) == version_word(career_edit_data) == VERSION_WORD,
        },
        "negativeGuards": {
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
    scoped = summary["scopedCareerEdit"]
    return {
        "schemaVersion": "save-options-controller-byte-preservation-copied-file.v1",
        "status": "PASS",
        "scope": "copied-file byte-preservation proof for save/options/controller clean-room planning",
        "source": {
            "privateEvidenceRoot": PRIVATE_EVIDENCE_ROOT,
            "sourcePathsPublic": False,
            "sourceHashesPublic": False,
            "runtimeExecution": False,
            "gameLaunch": False,
            "ghidraMutation": False,
            "installedGameMutation": False,
            "saveSynthesis": False,
            "proofInputs": ["one real career .bes baseline", "one real defaultoptions.bea baseline"],
        },
        "staticContext": {
            "staticFunctionQuality": "6411/6411 = 100.00%",
            "staticDebt": "0 / 0 / 0",
            "expandedStaticSurface": "1560/1560 = 100.00%",
            "currentRiskFocused": "1179/1179 = 100.00%",
            "remainingActiveFocusedWork": 0,
            "latestGhidraBackup": LATEST_GHIDRA_BACKUP,
        },
        "container": {
            "expectedSize": EXPECTED_SIZE,
            "expectedSizeHex": "0x2714",
            "versionWord": "0x4BD1",
            "trueViewRule": "file_offset = 0x0002 + career_offset",
            "careerBase": "0x0002",
        },
        "baselineEvidence": {
            "copiedInputClasses": ["real career .bes baseline", "real defaultoptions.bea baseline"],
            "copiedArtifactCount": 5,
            "allContainersValidated": True,
            "sourcePathDisclosure": "private evidence only; public schema omits source paths and source hashes",
        },
        "noOpPreservation": summary["noOpPreservation"],
        "scopedCareerEdit": {
            "field": scoped["field"],
            "baseOffset": scoped["baseOffset"],
            "metadataOffset": scoped["metadataOffset"],
            "allowedOffsets": scoped["allowedOffsets"],
            "changedOffsets": scoped["changedOffsets"],
            "changedOffsetCount": scoped["changedOffsetCount"],
            "unexpectedDiffCount": scoped["unexpectedDiffCount"],
            "legacyTrapHitCount": scoped["legacyTrapHitCount"],
            "metadataBytePreserved": scoped["metadataBytePreserved"],
            "lower24Changed": scoped["lower24Changed"],
            "goodieReservedRangeUnchanged": scoped["goodieReservedRangeUnchanged"],
            "techSlotsRangeUnchanged": scoped["techSlotsRangeUnchanged"],
            "optionsEntriesUnchanged": scoped["optionsEntriesUnchanged"],
            "optionsTailUnchanged": scoped["optionsTailUnchanged"],
            "fileSizePreserved": scoped["fileSizePreserved"],
            "versionWordPreserved": scoped["versionWordPreserved"],
        },
        "preservationGuards": {
            "goodieBase": "0x1F46",
            "reservedGoodies": "233-299",
            "killCountersBase": "0x23F6",
            "killPayloadRule": "preserve top-byte metadata; edit only value & 0x00FFFFFF when intentionally changing kills",
            "techSlotsBase": "0x240A",
            "optionsEntriesRange": "0x24BE-0x26BD",
            "optionsEntryCount": 16,
            "optionsTailRange": "0x26BE-0x2713",
            "defaultoptionsFlag0": "CCareer__Load(..., flag=0) applies entries/tail",
            "careerSaveFlag1": "CCareer__Load(..., flag=1) skips immediate entries/tail application",
            "controllerConfigValues": "mControllerConfigurationNum 1..4",
            "directBindingPatchCaveat": "direct binding proofs must force or record g_ControlSchemeIndex=0",
            "legacyAlignedViewTrapOffsets": ["0x23A4", "0x22D4", "0x240C"],
        },
        "claims": [
            "The copied career .bes and copied defaultoptions.bea baselines validate as 10004-byte containers with version word 0x4BD1.",
            "No-op copies preserve both copied baselines byte-for-byte with DiffCount=0.",
            "A scoped copied career-save edit can change only the allowlisted Aircraft kill-counter lower-24 payload bytes at 0x23F6-0x23F8.",
            "The scoped edit preserves the kill-counter metadata byte at 0x23F9, file size, version word, reserved Goodies range, tech slots, options entries, and options tail.",
            "Legacy aligned-view trap offsets 0x23A4, 0x22D4, and 0x240C were not touched.",
        ],
        "notClaimed": [
            "runtime save/load behavior",
            "runtime defaultoptions boot behavior",
            "runtime menu behavior",
            "runtime controller remap/input behavior",
            "runtime Goodies wall behavior",
            "exact source-layout parity",
            "BEA patching behavior",
            "visual QA",
            "Godot parity",
            "rebuild parity",
            "no-noticeable-difference parity",
        ],
    }


def validate_private_summary(summary: dict[str, Any], failures: list[str], check_files: bool = False) -> None:
    require(summary.get("schemaVersion") == "save-options-controller-byte-preservation-private-evidence.v1", "private summary schema mismatch", failures)
    require(summary.get("status") == "PASS", "private summary status mismatch", failures)
    require(summary.get("evidenceRoot") == PRIVATE_EVIDENCE_ROOT, "private evidence root mismatch", failures)
    require(summary["noOpPreservation"]["careerDiffCount"] == 0, "career no-op diff mismatch", failures)
    require(summary["noOpPreservation"]["defaultoptionsDiffCount"] == 0, "defaultoptions no-op diff mismatch", failures)
    scoped = summary["scopedCareerEdit"]
    require(scoped["unexpectedDiffCount"] == 0, "unexpected scoped edit diff count", failures)
    require(scoped["legacyTrapHitCount"] == 0, "legacy trap hit count", failures)
    require(scoped["metadataBytePreserved"] is True, "metadata byte not preserved", failures)
    require(scoped["lower24Changed"] is True, "lower24 payload was not changed", failures)
    require(scoped["goodieReservedRangeUnchanged"] is True, "reserved Goodies range changed", failures)
    require(scoped["techSlotsRangeUnchanged"] is True, "tech slots changed", failures)
    require(scoped["optionsEntriesUnchanged"] is True, "options entries changed", failures)
    require(scoped["optionsTailUnchanged"] is True, "options tail changed", failures)
    require(scoped["fileSizePreserved"] is True, "file size not preserved", failures)
    require(scoped["versionWordPreserved"] is True, "version word not preserved", failures)
    require(set(scoped["changedOffsets"]).issubset(set(scoped["allowedOffsets"])), "changed offsets exceed allowlist", failures)

    if not check_files:
        return

    artifacts = {row["relativePath"]: row for row in summary.get("copiedArtifacts", [])}
    expected_files = (
        "career-baseline.bes",
        "defaultoptions-baseline.bea",
        "career-noop.bes",
        "defaultoptions-noop.bea",
        "career-aircraft-kill-lower24-edit.bes",
    )
    for relative in expected_files:
        path = PRIVATE_DIR / relative
        require(path.is_file(), f"missing private artifact: {relative}", failures)
        if path.is_file():
            data = path.read_bytes()
            require(len(data) == EXPECTED_SIZE, f"{relative} size mismatch", failures)
            require(version_word(data) == VERSION_WORD, f"{relative} version mismatch", failures)
            require(artifacts.get(relative, {}).get("sha256") == sha256(data), f"{relative} hash mismatch", failures)

    career_baseline = read_bytes(PRIVATE_DIR / "career-baseline.bes")
    defaultoptions_baseline = read_bytes(PRIVATE_DIR / "defaultoptions-baseline.bea")
    career_noop = read_bytes(PRIVATE_DIR / "career-noop.bes")
    defaultoptions_noop = read_bytes(PRIVATE_DIR / "defaultoptions-noop.bea")
    career_edit = read_bytes(PRIVATE_DIR / "career-aircraft-kill-lower24-edit.bes")
    require(changed_offsets(career_baseline, career_noop) == [], "career no-op file has diffs", failures)
    require(changed_offsets(defaultoptions_baseline, defaultoptions_noop) == [], "defaultoptions no-op file has diffs", failures)
    edit_diffs = changed_offsets(career_baseline, career_edit)
    require([hex_offset(offset) for offset in edit_diffs] == scoped["changedOffsets"], "scoped edit changed-offset mismatch", failures)
    require(all(offset in KILL_LOWER24_ALLOWED for offset in edit_diffs), "scoped edit touched non-allowlisted byte", failures)
    require(career_baseline[KILL_AIRCRAFT_META_OFFSET] == career_edit[KILL_AIRCRAFT_META_OFFSET], "metadata byte changed on disk", failures)
    require(range_unchanged(career_baseline, career_edit, *OPTIONS_ENTRIES_RANGE), "options entries changed on disk", failures)
    require(range_unchanged(career_baseline, career_edit, *OPTIONS_TAIL_RANGE), "options tail changed on disk", failures)


def write_public_schema() -> dict[str, Any]:
    summary = read_json(PRIVATE_SUMMARY)
    schema = public_schema_from_summary(summary)
    write_json(SCHEMA, schema)
    write_json(LORE_SCHEMA, schema)
    return schema


def check_no_public_bad_tokens(path: Path, failures: list[str]) -> None:
    text = read_text(path)
    lower = text.lower()
    for token in FORBIDDEN_PUBLIC_TOKENS:
        require(token not in text, f"{path.relative_to(ROOT)} leaks public-forbidden token: {token}", failures)
    for phrase in FORBIDDEN_OVERCLAIMS:
        require(phrase not in lower, f"{path.relative_to(ROOT)} overclaims: {phrase}", failures)


def check_no_overclaims(path: Path, failures: list[str]) -> None:
    text = read_text(path)
    lower = text.lower()
    for phrase in FORBIDDEN_OVERCLAIMS:
        require(phrase not in lower, f"{path.relative_to(ROOT)} overclaims: {phrase}", failures)


def check_schema(failures: list[str]) -> None:
    summary = read_json(PRIVATE_SUMMARY)
    validate_private_summary(summary, failures, check_files=True)
    expected = public_schema_from_summary(summary)
    for path in (SCHEMA, LORE_SCHEMA):
        actual = read_json(path)
        require(actual == expected, f"{path.relative_to(ROOT)} does not match private-evidence-derived schema", failures)
        require(actual["noOpPreservation"]["careerDiffCount"] == 0, "schema career no-op diff mismatch", failures)
        require(actual["noOpPreservation"]["defaultoptionsDiffCount"] == 0, "schema defaultoptions no-op diff mismatch", failures)
        require(actual["scopedCareerEdit"]["unexpectedDiffCount"] == 0, "schema unexpected diff mismatch", failures)
        require(actual["scopedCareerEdit"]["metadataBytePreserved"] is True, "schema metadata preservation mismatch", failures)
        require(actual["source"]["sourcePathsPublic"] is False, "schema source path disclosure mismatch", failures)
        check_no_public_bad_tokens(path, failures)


def check_progress(failures: list[str]) -> None:
    progress = read_json(PROGRESS)
    quality = progress["functionQuality"]
    require(quality["totalFunctions"] == 6411, "progress total function mismatch", failures)
    require(quality["commentedFunctions"] == 6411, "progress commented function mismatch", failures)
    require(quality["commentlessFunctions"] == 0, "progress commentless mismatch", failures)
    require(quality["undefinedSignatures"] == 0, "progress undefined mismatch", failures)
    require(quality["paramSignatures"] == 0, "progress param_N mismatch", failures)
    current = progress["post100Reaudit"]["currentRiskRank"]
    require(current["focusedReviewed"] == 1179, "current-risk reviewed mismatch", failures)
    require(current["remainingFocusedAfterLatestReview"] == 0, "current-risk remaining mismatch", failures)
    require(current["isWave911Reconstruction"] is False, "Wave911 reconstruction flag mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_tokens = (
        "Save / Options Controller Byte-Preservation Copied-File Proof",
        PROOF_LINK,
        SCHEMA_LINK,
        PLAN_LINK,
        "Status: copied-file byte-preservation proof complete, not runtime proof",
        "10004",
        "0x4BD1",
        "file_offset = 0x0002 + career_offset",
        "0x23F6-0x23F8",
        "0x23F9",
        "DiffCount=0",
        "0x24BE-0x26BD",
        "0x26BE-0x2713",
        "0x23A4",
        "0x22D4",
        "0x240C",
        "6411/6411 = 100.00%",
        "1179/1179 = 100.00%",
        PRIVATE_EVIDENCE_ROOT,
    )
    for path in (PROOF, LORE_PROOF, READINESS):
        text = read_text(path)
        for token in core_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing token: {token}", failures)
        check_no_public_bad_tokens(path, failures)
    require(read_text(PROOF) == read_text(LORE_PROOF), "proof lore mirror mismatch", failures)

    front_door_tokens = (PROOF_LINK, SCHEMA_LINK, "Save / Options Controller Byte-Preservation Copied-File Proof")
    for path in (BACKLOG, LORE_BACKLOG, MAPPED, LORE_MAPPED, BIN_INDEX, LORE_BIN_INDEX, RE_INDEX, LORE_RE_INDEX, SAVE_INDEX, LORE_SAVE_INDEX, SAVE_FORMAT, LORE_SAVE_FORMAT, CAREER_DOC, LORE_CAREER_DOC):
        text = read_text(path)
        for token in front_door_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing copied-file proof token: {token}", failures)
        check_no_overclaims(path, failures)

    require(read_text(BACKLOG) == read_text(LORE_BACKLOG), "backlog lore mirror mismatch", failures)
    require(read_text(MAPPED) == read_text(LORE_MAPPED), "mapped systems lore mirror mismatch", failures)
    require(read_text(BIN_INDEX) == read_text(LORE_BIN_INDEX), "binary index lore mirror mismatch", failures)
    require(read_text(RE_INDEX) == read_text(LORE_RE_INDEX), "RE index lore mirror mismatch", failures)
    require(read_text(SAVE_INDEX) == read_text(LORE_SAVE_INDEX), "save index lore mirror mismatch", failures)
    require(read_text(SAVE_FORMAT) == read_text(LORE_SAVE_FORMAT), "save format lore mirror mismatch", failures)
    require(read_text(CAREER_DOC) == read_text(LORE_CAREER_DOC), "Career doc lore mirror mismatch", failures)

    package = read_json(PACKAGE_JSON)
    expected_script = r"py -3 tools\save_options_controller_byte_preservation_copied_file_probe.py --check"
    actual_script = package.get("scripts", {}).get("test:save-options-controller-byte-preservation-copied-file")
    require(actual_script == expected_script, "package script mismatch", failures)


def run_check() -> list[str]:
    failures: list[str] = []
    check_schema(failures)
    check_progress(failures)
    check_docs(failures)
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="validate existing copied-file proof artifacts")
    parser.add_argument("--write-private-evidence", action="store_true", help="generate ignored private copied-file evidence")
    parser.add_argument("--write-schema", action="store_true", help="write public schema from private evidence summary")
    parser.add_argument("--career-source", type=Path, help="real career .bes baseline for private evidence generation")
    parser.add_argument("--defaultoptions-source", type=Path, help="real defaultoptions.bea baseline for private evidence generation")
    args = parser.parse_args()

    if args.write_private_evidence:
        if args.career_source is None or args.defaultoptions_source is None:
            parser.error("--write-private-evidence requires --career-source and --defaultoptions-source")
        summary = generate_private_evidence(args.career_source, args.defaultoptions_source)
        print(f"Wrote {PRIVATE_SUMMARY.relative_to(ROOT)}")
        print(f"Private evidence status: {summary['status']}")

    if args.write_schema:
        schema = write_public_schema()
        print(f"Wrote {SCHEMA.relative_to(ROOT)}")
        print(f"Wrote {LORE_SCHEMA.relative_to(ROOT)}")
        print(f"Public schema status: {schema['status']}")

    if args.check or not (args.write_private_evidence or args.write_schema):
        failures = run_check()
        if failures:
            print("Save / Options controller byte-preservation copied-file probe: FAIL")
            for failure in failures:
                print(f"- {failure}")
            return 1
        print("Save / Options controller byte-preservation copied-file probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
