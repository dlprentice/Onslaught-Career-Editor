#!/usr/bin/env python3
"""Validate Wave1116 door-wing AI current-risk review."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import sys
from pathlib import Path

import wave1108_current_risk_rank


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1116-door-wing-ai-current-risk-review"
FOCUSED_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-focused-candidates.tsv"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1116-door-wing-ai-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1116-door-wing-ai-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1116_door_wing_ai_current_risk_review_2026-06-05.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
MAPPED_SYSTEMS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PROGRESS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"G:\GhidraBackups\BEA_20260605-011935_post_wave1116_door_wing_ai_current_risk_review_verified"
PRIOR_BACKUP = r"G:\GhidraBackups\BEA_20260605-010428_post_wave1115_unitai_carver_motion_activation_current_risk_review_verified"

PRIOR_PROBES = (
    "wave1109_cfastvb_current_risk_head_supersession.py",
    "wave1110_cfastvb_wave1053_remainder_supersession.py",
    "wave1111_cnamedmesh_current_risk_supersession.py",
    "wave1112_animal_wave1016_current_risk_supersession.py",
    "wave1113_battleengine_wave936_wave1010_current_risk_supersession.py",
    "wave1114_mixed_score27_current_risk_head_supersession.py",
    "wave1115_unitai_carver_motion_activation_current_risk_review.py",
)

TARGETS = {
    "0x00438050": ("CPhysicsRoundValue__SetOwnedValueStringAt08", "void __thiscall CPhysicsRoundValue__SetOwnedValueStringAt08(void * this, char * sourceString)", ("stale CUnitAI owner", "this+0x8", "sourceString"), ("0x00437f5f", "<no_function>", "UNCONDITIONAL_CALL"), ("free", "sourceString", "0x8")),
    "0x004453a0": ("CDiveBomberAI__dtor_base", "void __fastcall CDiveBomberAI__dtor_base(void * this)", ("destructor-base", "+0x28/+0x24/+0x0c", "CMonitor__Shutdown"), ("0x00445383", "CDiveBomberAI__scalar_deleting_dtor", "UNCONDITIONAL_CALL"), ("CSPtrSet__Remove", "CMonitor__Shutdown", "0x28")),
    "0x00445460": ("CDiveBomberGuide__dtor_base", "void __fastcall CDiveBomberGuide__dtor_base(void * this)", ("destructor-base", "+0x2c", "CMonitor__Shutdown"), ("0x00445443", "CDiveBomberGuide__scalar_deleting_dtor", "UNCONDITIONAL_CALL"), ("CSPtrSet__Remove", "CMonitor__Shutdown", "0x2c")),
    "0x00445570": ("CUnitAI__PlayOpenAnimationIfState1Or3", "void __fastcall CUnitAI__PlayOpenAnimationIfState1Or3(void * unitAI)", ("+0x280", "states 1 or 3", "open animation"), ("0x00445d84", "CUnitAI__UpdateDoorWingEngagement_CloseRange", "UNCONDITIONAL_CALL"), ("0x280", "0xf0", "open")),
    "0x004455c0": ("CUnitAI__PlayCloseAnimationIfState0Or2", "void __fastcall CUnitAI__PlayCloseAnimationIfState0Or2(void * unitAI)", ("+0x280", "states 0 or 2", "close animation"), ("0x00445c3a", "CUnitAI__UpdateDoorWingEngagement_CloseRange", "UNCONDITIONAL_CALL"), ("0x280", "0xf0", "close")),
    "0x00445610": ("CUnitAI__AdvanceOpenCloseShootAnimationState", "int __fastcall CUnitAI__AdvanceOpenCloseShootAnimationState(void * unitAI)", ("shoot/close/open-style animation names", "+0xf0", "+0x280"), ("0x005e1328", "<no_function>", "DATA"), ("0x280", "0xf0")),
    "0x00445ad0": ("CUnitAI__UpdateDoorWingEngagement_CloseRange", "double __fastcall CUnitAI__UpdateDoorWingEngagement_CloseRange(void * doorWingAI)", ("close-range door-wing engagement", "+0x64/+0x68", "+0xf4"), ("0x00445a8e", "<no_function>", "UNCONDITIONAL_CALL"), ("0x64", "0x68", "0xf4")),
    "0x00445f40": ("CUnitAI__UpdateDoorWingEngagement_MidRange", "double __fastcall CUnitAI__UpdateDoorWingEngagement_MidRange(void * doorWingAI)", ("mid-range door-wing engagement", "+0x6c", "+0xf4"), ("0x00445a85", "<no_function>", "UNCONDITIONAL_CALL"), ("0x6c", "0xf4")),
    "0x00446150": ("CUnitAI__UpdateDoorWingEngagement_LongRange", "double __fastcall CUnitAI__UpdateDoorWingEngagement_LongRange(void * doorWingAI)", ("long-range door-wing engagement", "+0x68/+0x70", "CUnitAI__EnterDoorWingOpenTrackingState"), ("0x00445a7c", "<no_function>", "UNCONDITIONAL_CALL"), ("0x68", "0x70", "CUnitAI__EnterDoorWingOpenTrackingState")),
    "0x00446400": ("CUnitAI__EnterDoorWingOpenTrackingState", "void __fastcall CUnitAI__EnterDoorWingOpenTrackingState(void * doorWingAI)", ("open tracking", "+0x68", "+0x70"), ("0x004463b6", "CUnitAI__UpdateDoorWingEngagement_LongRange", "UNCONDITIONAL_CALL"), ("0x68", "0x70", "CUnitAI__PlayOpenAnimationIfState1Or3")),
    "0x00447060": ("CDropshipAI__dtor_base", "void __fastcall CDropshipAI__dtor_base(void * this)", ("destructor-base", "+0x28/+0x24/+0x0c", "CMonitor__Shutdown"), ("0x00447043", "CDropshipAI__scalar_deleting_dtor", "UNCONDITIONAL_CALL"), ("CSPtrSet__Remove", "CMonitor__Shutdown", "0x28")),
    "0x00447100": ("CDropship__dtor_base", "void __fastcall CDropship__dtor_base(void * this)", ("CWorld__RemoveUnitFromOccupancyGrid_Thunk", "CAirUnit__dtor_base"), ("0x005e1de0", "<no_function>", "DATA"), ("CWorld__RemoveUnitFromOccupancyGrid_Thunk", "CAirUnit__dtor_base")),
    "0x00447a40": ("CUnitAI__SetDoorWingState2AndClampYawDelta", "void __fastcall CUnitAI__SetDoorWingState2AndClampYawDelta(void * unitAI)", ("+0x290/+0x294", "+0x27c", "+0x2a0"), ("0x005e1fb0", "<no_function>", "DATA"), ("0x290", "0x294", "0x27c")),
    "0x00447ac0": ("CUnitAI__PlayWingFoldedAnimationAndSetState3", "void __fastcall CUnitAI__PlayWingFoldedAnimationAndSetState3(void * unitAI)", ("wingfolded animation", "+0x27c", "occupancy/shadow"), ("0x005e1fb4", "<no_function>", "DATA"), ("0x27c", "wingfolded", "CWorld__AddUnitToOccupancyGridAndRebuildShadows_Thunk")),
    "0x00447b10": ("CUnitAI__PlayWingUnfoldedAnimationAndSetState5", "void __fastcall CUnitAI__PlayWingUnfoldedAnimationAndSetState5(void * unitAI)", ("wingunfolded", "+0x27c", "occupancy grid"), ("0x005e1fb8", "<no_function>", "DATA"), ("wingunfolded", "0x27c", "CWorld__RemoveUnitFromOccupancyGrid_Thunk")),
    "0x00447b60": ("CUnitAI__HasReachedCachedAnchorPoint", "int __fastcall CUnitAI__HasReachedCachedAnchorPoint(void * unitAI)", ("cached anchor flag +0x290", "+0x280/+0x284", "distance threshold"), ("0x0044866d", "CDropshipAI__VFunc_09_00448580", "UNCONDITIONAL_CALL"), ("0x290", "0x280", "0x284")),
    "0x00447bb0": ("CUnitAI__GetOrGenerateCachedAnchorPoint", "void __thiscall CUnitAI__GetOrGenerateCachedAnchorPoint(void * this, void * outAnchorPoint)", ("outAnchorPoint", "+0x280/+0x28c", "CUnitAI__IsCachedAnchorPointValid"), ("0x00448690", "CDropshipAI__VFunc_09_00448580", "UNCONDITIONAL_CALL"), ("0x280", "0x28c", "CUnitAI__IsCachedAnchorPointValid")),
    "0x00447d50": ("CUnitAI__IsCachedAnchorPointValid", "int __fastcall CUnitAI__IsCachedAnchorPointValid(void * unitAI)", ("CMapWho", "collision/height context", "occupancy bitmask"), ("0x00447a57", "CUnitAI__SetDoorWingState2AndClampYawDelta", "UNCONDITIONAL_CALL"), ("CMapWho", "0x27c", "0x280")),
    "0x00447fa0": ("CUnitAI__AdvanceDoorWingAnimationState", "int __fastcall CUnitAI__AdvanceDoorWingAnimationState(void * unitAI)", ("dooropening", "doorclosing", "wingfolded"), ("0x005e1ec4", "<no_function>", "DATA"), ("dooropening", "doorclosing", "wingfolded", "wingunfolded")),
    "0x00448110": ("CUnitAI__SetDoorWingState6", "void __fastcall CUnitAI__SetDoorWingState6(void * unitAI)", ("state +0x27c to 6",), ("0x004486dc", "CDropshipAI__VFunc_09_00448580", "UNCONDITIONAL_CALL"), ("0x27c", "6")),
    "0x00448120": ("CUnitAI__SetDoorWingState7AndMirrorYawOffset", "void __fastcall CUnitAI__SetDoorWingState7AndMirrorYawOffset(void * unitAI)", ("state +0x27c to 7", "+0x2a4"), ("0x00448737", "CDropshipAI__VFunc_09_00448580", "UNCONDITIONAL_CALL"), ("0x27c", "7", "0x2a4")),
}

DOC_TOKENS = (
    "Wave1116",
    "wave1116-door-wing-ai-current-risk-review",
    "77/1179 = 6.53%",
    "21 rows",
    "current focused candidates: 1179",
    "score-26 PhysicsRoundValue plus door-wing AI head",
    "fresh read-only Ghidra export",
    "no mutation",
    BACKUP,
    PRIOR_BACKUP,
)

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "runtime ai behavior proven",
    "runtime door-wing behavior proven",
    "runtime dropship behavior proven",
    "exact layout proven",
    "source-body identity proven",
    "rebuild parity proven",
    "fully reverse-engineered",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig", errors="replace").replace("\x00", "")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def normalize_address(address: str) -> str:
    value = (address or "").strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def contains_token(text: str, token: str) -> bool:
    normalized = text.replace("\\\\\\\\", "\\").replace("\\\\", "\\")
    return token in text or token.replace("\\", "\\\\") in text or token in normalized


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def import_probe(path: Path):
    if str(TOOLS) not in sys.path:
        sys.path.insert(0, str(TOOLS))
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def extract_probe_addresses(module) -> set[str]:
    addresses: set[str] = set()
    for attr in ("TOP15", "REMAINDER", "TARGETS"):
        if not hasattr(module, attr):
            continue
        value = getattr(module, attr)
        if isinstance(value, dict):
            addresses.update(normalize_address(address) for address in value)
        elif isinstance(value, (list, tuple, set)):
            for item in value:
                if isinstance(item, str):
                    addresses.add(normalize_address(item))
                elif isinstance(item, (list, tuple)) and item and isinstance(item[0], str):
                    addresses.add(normalize_address(item[0]))
    if hasattr(module, "ADDRESS"):
        addresses.add(normalize_address(getattr(module, "ADDRESS")))
    return addresses


def prior_accounted_addresses() -> set[str]:
    accounted: set[str] = set()
    for name in PRIOR_PROBES:
        accounted.update(extract_probe_addresses(import_probe(TOOLS / name)))
    return accounted


def row_map(path: Path, key: str = "address") -> dict[str, dict[str, str]]:
    return {normalize_address(row.get(key, "")): row for row in read_tsv(path)}


def check_wave1108_head(failures: list[str]) -> None:
    wave1108_current_risk_rank.generate()
    rows = read_tsv(FOCUSED_TSV)
    accounted = prior_accounted_addresses()
    remaining = [row for row in rows if normalize_address(row.get("address", "")) not in accounted]
    require(len(rows) == 1179, "Wave1108 focused row count mismatch", failures)
    require(len(accounted) == 56, f"prior accounted count mismatch: {len(accounted)}", failures)
    require(len(remaining) == 1123, f"remaining focused count mismatch: {len(remaining)}", failures)
    require([normalize_address(row.get("address", "")) for row in remaining[:21]] == list(TARGETS), "Wave1116 targets are not the next twenty-one unaccounted Wave1108 focused rows", failures)
    for row in remaining[:21]:
        require(row.get("score") == "26", f"Wave1108 score mismatch: {row.get('address')}", failures)


def check_exports(failures: list[str]) -> None:
    counts = {
        "metadata.tsv": 21,
        "tags.tsv": 21,
        "xrefs.tsv": 25,
        "instructions.tsv": 2037,
        "decompile/index.tsv": 21,
    }
    for relative, expected in counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)
    log_tokens = {
        "metadata.log": "targets=21 found=21 missing=0",
        "tags.log": "ExportFunctionTagsByAddress complete: rows=21 missing=0",
        "xrefs.log": "Wrote 25 rows",
        "instructions.log": "targets=21 missing=0",
        "decompile.log": "targets=21 dumped=21 missing=0 failed=0",
    }
    for relative, token in log_tokens.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR", "MISSING\t", "missing=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_target_rows(failures: list[str]) -> None:
    metadata = row_map(BASE / "metadata.tsv")
    tags = row_map(BASE / "tags.tsv")
    decompile = row_map(BASE / "decompile" / "index.tsv")
    xrefs = read_tsv(BASE / "xrefs.tsv")
    instructions = read_tsv(BASE / "instructions.tsv")
    queue = row_map(QUEUE_TSV)

    for address, expected in TARGETS.items():
        name, signature, comment_tokens, xref, decompile_tokens = expected
        for label, rows in (("metadata", metadata), ("current queue", queue)):
            row = rows.get(address)
            require(row is not None, f"{label} missing: {address}", failures)
            if row is not None:
                require(row.get("name") == name, f"{label} name mismatch: {address}", failures)
                require(row.get("signature") == signature, f"{label} signature mismatch: {address}", failures)
                require(row.get("status") == "OK", f"{label} status mismatch: {address}", failures)
                for token in comment_tokens[:2]:
                    require(token in row.get("comment", ""), f"{label} missing comment token {address}: {token}", failures)
        tag_row = tags.get(address)
        require(tag_row is not None and tag_row.get("name") == name and tag_row.get("status") == "OK", f"tag row mismatch: {address}", failures)
        dec = decompile.get(address)
        require(dec is not None and dec.get("name") == name and dec.get("signature") == signature and dec.get("status") == "OK", f"decompile index mismatch: {address}", failures)
        from_addr, from_function, ref_type = xref
        require(
            any(
                normalize_address(row.get("target_addr", "")) == address
                and normalize_address(row.get("from_addr", "")) == normalize_address(from_addr)
                and row.get("from_function") == from_function
                and row.get("ref_type") == ref_type
                for row in xrefs
            ),
            f"missing xref {from_addr} -> {address}",
            failures,
        )
        require(any(normalize_address(row.get("target_addr", "")) == address and row.get("function_name") == name for row in instructions), f"missing instruction rows: {address}", failures)
        files = list((BASE / "decompile").glob(f"{address[2:]}_*.c"))
        require(len(files) == 1, f"decompile file count mismatch: {address}", failures)
        if files:
            text = read_text(files[0])
            for token in decompile_tokens:
                require(token in text, f"decompile missing token {address}: {token}", failures)


def check_backup(failures: list[str]) -> None:
    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes", -1)) == 175541127, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = {
        "wave1116 note": read_text(NOTE),
        "wave1116 readiness": read_text(READINESS),
        "mapped systems": read_text(MAPPED_SYSTEMS),
        "campaign": read_text(CAMPAIGN),
        "binary index": read_text(BINARY_INDEX),
        "RE index": read_text(RE_INDEX),
        "progress": read_text(PROGRESS),
        "developer state": read_text(DEVELOPER_STATE),
        "documentation state": read_text(DOCUMENTATION_STATE),
        "re state": read_text(RE_STATE),
    }
    for name, text in docs.items():
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {name}: {token}", failures)
        for address, expected in TARGETS.items():
            require(f"{address} {expected[0]}" in text, f"missing target in {name}: {address}", failures)
        lowered = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lowered, f"overclaim token in {name}: {bad}", failures)
    require(read_text(NOTE) == read_text(NOTE_MIRROR), "wave1116 note mirror mismatch", failures)
    require(read_text(MAPPED_SYSTEMS) == read_text(MAPPED_SYSTEMS_MIRROR), "mapped-systems mirror mismatch", failures)
    require(read_text(PROGRESS) == read_text(PROGRESS_MIRROR), "static progress mirror mismatch", failures)
    progress = read_json(PROGRESS)
    latest = progress.get("latestWave", {})
    require(latest.get("wave") == "Wave1116 door-wing AI current-risk review", "latest wave mismatch", failures)
    require(latest.get("tag") == "wave1116-door-wing-ai-current-risk-review", "latest tag mismatch", failures)
    require(latest.get("backup") == BACKUP, "latest backup mismatch", failures)
    current = progress.get("post100Reaudit", {}).get("currentRiskRank", {})
    require(current.get("focusedReviewed") == 77, "focusedReviewed mismatch", failures)
    require(current.get("focusedReviewedPercent") == "6.53%", "focusedReviewedPercent mismatch", failures)
    package = read_json(PACKAGE_JSON)
    require(package.get("scripts", {}).get("test:wave1116-door-wing-ai-current-risk-review") == r"py -3 tools\wave1116_door_wing_ai_current_risk_review.py --check", "missing package script", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()
    failures: list[str] = []
    check_wave1108_head(failures)
    check_exports(failures)
    check_target_rows(failures)
    check_backup(failures)
    check_docs(failures)
    if failures:
        print("Wave1116 door-wing AI current-risk review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1116 door-wing AI current-risk review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
