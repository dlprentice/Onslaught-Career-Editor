#!/usr/bin/env python3
"""Validate Wave1000 CGillM grounded movement read-only review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1000-gillm-grounded-movement-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_gillm_grounded_movement_review_wave1000_2026-05-31.md"
RECHECK_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1000_recheck_2026-05-31.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
GILLM_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "GillM.cpp" / "_index.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
WAVE409_PROBE = ROOT / "tools" / "ghidra_gillm_start_state_vector_wave409_probe.py"
RECHECK_TOOL = ROOT / "tools" / "ghidra_wave900_plus_through_wave983_recheck.py"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260531-101059_post_wave1000_gillm_grounded_movement_review_verified"

TARGETS = {
    "0x004799c0": ("CGillM__VFunc09_InitGroundedSpawnState", "void __thiscall CGillM__VFunc09_InitGroundedSpawnState(void * this, void * spawn_state)"),
    "0x00479a50": ("CGillM__InitLegMotion", "void __thiscall CGillM__InitLegMotion(void * this, void * init_data)"),
    "0x00479b60": ("CGillM__InitGillMAIComponent", "void __thiscall CGillM__InitGillMAIComponent(void * this, void * init_data)"),
    "0x00479bf0": ("CGillMAI__ScalarDeletingDestructor", "void * __thiscall CGillMAI__ScalarDeletingDestructor(void * this, byte flags)"),
    "0x00479cb0": ("CGillM__InitTerrainGuideComponent", "void __fastcall CGillM__InitTerrainGuideComponent(void * this)"),
    "0x00479d10": ("CGillM__UpdateGroundedVerticalDrift", "void __fastcall CGillM__UpdateGroundedVerticalDrift(void * this)"),
    "0x00479db0": ("CGillM__TriggerRandomArmHitAnimationIfReady", "void __fastcall CGillM__TriggerRandomArmHitAnimationIfReady(void * this)"),
    "0x00479f30": ("CGillM__ComputeTerrainClearanceNoiseScale", "double __fastcall CGillM__ComputeTerrainClearanceNoiseScale(void * this)"),
    "0x0047a0b0": ("CGillM__ComputeLateralSlopeAlignment", "double __fastcall CGillM__ComputeLateralSlopeAlignment(void * this)"),
    "0x0047a160": ("CGillM__StartState1WithStoredMotionVector", "void __thiscall CGillM__StartState1WithStoredMotionVector(void * this)"),
}

COMMENT_TOKENS = {
    "0x004799c0": ("CGillM RTTI vtable 0x005e0b30 slot 9", "+0x274", "+0x278"),
    "0x00479a50": ("LegMotion", "0xf0-byte CMCGillM", "this+0x70"),
    "0x00479b60": ("0x60-byte object", "CGillMAI RTTI vtable 0x005dbcb4", "this+0x13c"),
    "0x00479cb0": ("0x20-byte object", "CTerrainGuide__ctor", "this+0x208"),
    "0x00479d10": ("slot 66", "+0x274", "+0x244"),
    "0x00479db0": ("Gill_M_Left_Arm", "Gill_M_Right_Arm", "+0x26c"),
    "0x00479f30": ("older CUnitAI label", "+0x274", "+0x244"),
    "0x0047a0b0": ("older CUnitAI label", "+0x114", "heightfield normal"),
    "0x0047a160": ("vtable 0x005e0b30 slot 100", "+0x278", "+0xf4"),
}

DOC_TOKENS = (
    "Wave1000",
    "gillm-grounded-movement-review-wave1000",
    "0x004799c0 CGillM__VFunc09_InitGroundedSpawnState",
    "0x00479d10 CGillM__UpdateGroundedVerticalDrift",
    "0x00479db0 CGillM__TriggerRandomArmHitAnimationIfReady",
    "0x00479f30 CGillM__ComputeTerrainClearanceNoiseScale",
    "0x0047a0b0 CGillM__ComputeLateralSlopeAlignment",
    "0x0047a160 CGillM__StartState1WithStoredMotionVector",
    "467/1408 = 33.17%",
    "606/1478 = 41.00%",
    "350/500 = 70.00%",
    "6222/6222 = 100.00%",
    BACKUP_PATH,
)

OVERCLAIMS = (
    "runtime gillm movement behavior proven",
    "runtime terrain/grounding behavior proven",
    "runtime arm-hit animation behavior proven",
    "exact source-body identity proven",
    "exact layout proven",
    "rebuild parity proven",
)

EXPECTED_LOG_TOKENS = {
    "pre-metadata.log": ("targets=10 found=10 missing=0", "REPORT: Save succeeded"),
    "pre-tags.log": ("ExportFunctionTagsByAddress complete: rows=10 missing=0", "REPORT: Save succeeded"),
    "pre-xrefs.log": ("Wrote 10 rows", "REPORT: Save succeeded"),
    "pre-instructions.log": ("Wrote 526 function-body instruction rows", "targets=10 missing=0", "REPORT: Save succeeded"),
    "pre-decompile.log": ("targets=10 dumped=10 missing=0 failed=0", "REPORT: Save succeeded"),
    "pre-vtable-slots.log": ("ExportVtableSlots complete: targets=1 rows=128", "REPORT: Save succeeded"),
}


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig", errors="replace").replace("\x00", "")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def row_by_address(rows: list[dict[str, str]], address: str, field: str = "address") -> dict[str, str] | None:
    target = normalize_address(address)
    for row in rows:
        if normalize_address(row.get(field, "")) == target:
            return row
    return None


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    if token in text or token.replace("\\", "\\\\") in text or token.replace("\\", "\\\\\\\\") in text:
        return True
    previous = None
    current = text
    token_current = token
    while previous != current:
        previous = current
        current = current.replace("\\\\\\\\", "\\").replace("\\\\", "\\")
        token_current = token_current.replace("\\\\\\\\", "\\").replace("\\\\", "\\")
    return token_current in current


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 10,
        "pre-tags.tsv": 10,
        "pre-xrefs.tsv": 10,
        "pre-instructions.tsv": 526,
        "pre-decompile/index.tsv": 10,
        "pre-vtable-slots.tsv": 128,
    }
    for relative, expected in expected_counts.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == expected, f"{relative} row count {actual} != {expected}", failures)

    metadata = read_tsv(BASE / "pre-metadata.tsv")
    tags = read_tsv(BASE / "pre-tags.tsv")
    decompile_index = read_tsv(BASE / "pre-decompile" / "index.tsv")

    for address, (name, signature) in TARGETS.items():
        row = row_by_address(metadata, address)
        require(row is not None, f"metadata missing {address}", failures)
        if row:
            require(row.get("name") == name, f"metadata name mismatch {address}", failures)
            require(row.get("signature") == signature, f"metadata signature mismatch {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
            require(row.get("comment", "").strip() != "", f"comment missing {address}", failures)
            for token in COMMENT_TOKENS.get(address, ("Static retail evidence only",)):
                require(token in row.get("comment", ""), f"comment token missing {address}: {token}", failures)

        dec = row_by_address(decompile_index, address)
        require(dec is not None, f"decompile missing {address}", failures)
        if dec:
            require(dec.get("name") == name, f"decompile name mismatch {address}", failures)
            require(dec.get("signature") == signature, f"decompile signature mismatch {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch {address}", failures)

        tag_row = row_by_address(tags, address)
        require(tag_row is not None, f"tags missing {address}", failures)
        if tag_row:
            actual_tags = set(filter(None, tag_row.get("tags", "").split(";")))
            require("static-reaudit" in actual_tags, f"missing static-reaudit tag {address}", failures)
            require("retail-binary-evidence" in actual_tags, f"missing retail-binary-evidence tag {address}", failures)
            if address != "0x0047a160":
                require("gillm-family-wave389" in actual_tags, f"missing Wave389 tag {address}", failures)
            if address == "0x0047a160":
                require("gillm-start-state-vector-wave409" in actual_tags, "missing Wave409 tag 0x0047a160", failures)

    xrefs = read_tsv(BASE / "pre-xrefs.tsv")
    expected_xrefs = (
        ("0x004799c0", "0x005e0b54", "DATA"),
        ("0x00479a50", "0x005e0d04", "DATA"),
        ("0x00479b60", "0x005e0d08", "DATA"),
        ("0x00479bf0", "0x005dbcb8", "DATA"),
        ("0x00479cb0", "0x005e0d0c", "DATA"),
        ("0x00479d10", "0x005e0c38", "DATA"),
        ("0x00479db0", "0x0047a392", "UNCONDITIONAL_CALL"),
        ("0x00479f30", "0x004963ae", "UNCONDITIONAL_CALL"),
        ("0x0047a0b0", "0x004963ce", "UNCONDITIONAL_CALL"),
        ("0x0047a160", "0x005e0cc0", "DATA"),
    )
    for target, source, ref_type in expected_xrefs:
        require(
            any(
                normalize_address(row.get("target_addr", "")) == target
                and normalize_address(row.get("from_addr", "")) == source
                and row.get("ref_type") == ref_type
                for row in xrefs
            ),
            f"missing xref {source} -> {target} {ref_type}",
            failures,
        )

    instructions = read_tsv(BASE / "pre-instructions.tsv")
    instruction_checks = (
        ("0x004799c0", "0x004799d8", "MOV", "dword ptr [ESI + 0x270], EAX"),
        ("0x004799c0", "0x00479a14", "MOV", "dword ptr [ESI + 0x274], 0x1"),
        ("0x00479a50", "0x00479ace", "MOV", "dword ptr [ESI + 0x70], ECX"),
        ("0x00479b60", "0x00479bb2", "MOV", "dword ptr [EDI + 0x13c], ESI"),
        ("0x00479cb0", "0x00479cfe", "MOV", "dword ptr [ESI + 0x208], EAX"),
        ("0x00479f30", "0x00479f36", "CMP", "dword ptr [ESI + 0x274], 0x1"),
        ("0x0047a0b0", "0x0047a0b3", "MOV", "EAX, dword ptr [ECX + 0x114]"),
        ("0x0047a160", "0x0047a176", "LEA", "ECX, [ESI + 0x278]"),
        ("0x0047a160", "0x0047a1a1", "MOV", "dword ptr [ESI + 0x244], 0x1"),
    )
    for target, instr_addr, mnemonic, operand in instruction_checks:
        require(
            any(
                normalize_address(row.get("target_addr", "")) == target
                and row.get("instruction_addr") == instr_addr
                and row.get("mnemonic") == mnemonic
                and row.get("operands") == operand
                for row in instructions
            ),
            f"missing instruction {target} {instr_addr} {mnemonic} {operand}",
            failures,
        )

    vtable_slots = read_tsv(BASE / "pre-vtable-slots.tsv")
    expected_slots = (
        ("9", "0x005e0b54", "0x004799c0", "CGillM__VFunc09_InitGroundedSpawnState"),
        ("66", "0x005e0c38", "0x00479d10", "CGillM__UpdateGroundedVerticalDrift"),
        ("100", "0x005e0cc0", "0x0047a160", "CGillM__StartState1WithStoredMotionVector"),
        ("117", "0x005e0d04", "0x00479a50", "CGillM__InitLegMotion"),
        ("118", "0x005e0d08", "0x00479b60", "CGillM__InitGillMAIComponent"),
        ("119", "0x005e0d0c", "0x00479cb0", "CGillM__InitTerrainGuideComponent"),
    )
    for slot, slot_addr, pointer, name in expected_slots:
        require(
            any(
                row.get("vtable") == "005e0b30"
                and row.get("slot_index") == slot
                and normalize_address(row.get("slot_addr", "")) == slot_addr
                and normalize_address(row.get("pointer_addr", "")) == pointer
                and row.get("function_name") == name
                and row.get("status") == "OK"
                for row in vtable_slots
            ),
            f"missing CGillM vtable slot {slot} -> {name}",
            failures,
        )

    decompile_text = "\n".join(path.read_text(encoding="utf-8-sig", errors="replace") for path in (BASE / "pre-decompile").glob("*.c"))
    for token in ("Gill_M_Left_Arm", "Gill_M_Right_Arm", "+ 0x244", "+ 0x278"):
        require(token in decompile_text, f"missing decompile token: {token}", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    for relative, tokens in EXPECTED_LOG_TOKENS.items():
        text = read_text(BASE / relative)
        for token in tokens:
            require(token in text, f"missing log token {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR", "FAIL:", "missing=1", "failed=1"):
            require(bad not in text, f"bad log token {relative}: {bad}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 173869959 or backup.get("totalBytes") == 173869959.0, "backup bytes mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = (
        NOTE,
        RECHECK_NOTE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_COVERAGE,
        GILLM_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    )
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing doc token {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lowered, f"overclaim token {path.relative_to(ROOT)}: {bad}", failures)

    function_index_text = read_text(FUNCTION_INDEX)
    for token in ("Wave1000", "GillM.cpp", "0x004799c0", "0x0047a160", BACKUP_PATH):
        require(contains_token(function_index_text, token), f"missing doc token {FUNCTION_INDEX.relative_to(ROOT)}: {token}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-gillm-grounded-movement-review-wave1000")
        == r"py -3 tools\ghidra_gillm_grounded_movement_review_wave1000_probe.py --check",
        "missing Wave1000 package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1000-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1000 --check",
        "missing Wave1000 recheck script",
        failures,
    )

    queue = read_json(QUEUE_JSON)
    require(queue.get("totalFunctions") == 6222, "queue total mismatch", failures)
    quality = queue.get("qualitySignals", {})
    require(quality.get("commentlessFunctionCount") == 0, "queue commentless mismatch", failures)
    require(quality.get("undefinedSignatureCount") == 0, "queue undefined mismatch", failures)
    require(quality.get("paramSignatureCount") == 0, "queue param mismatch", failures)

    wave409_text = read_text(WAVE409_PROBE)
    for token in (
        "current queue totalFunctions expected 6222",
        "current queue commentlessFunctionCount expected 0",
        "current queue undefinedSignatureCount expected 0",
        "current queue paramSignatureCount expected 0",
    ):
        require(token in wave409_text, f"missing Wave409 current-queue normalization token: {token}", failures)

    recheck_text = read_text(RECHECK_TOOL)
    require(r"(?:wave|post_wave)(9\d\d|1\d{3})" in recheck_text, "Wave900+ recheck regex does not support Wave1000+", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave1000 CGillM grounded movement review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1000 CGillM grounded movement review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
