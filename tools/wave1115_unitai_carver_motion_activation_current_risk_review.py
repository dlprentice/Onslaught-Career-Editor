#!/usr/bin/env python3
"""Validate Wave1115 UnitAI/Carver motion activation current-risk review."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1115-unitai-carver-motion-activation-current-risk-review"
WAVE1108_DIR = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank"
FOCUSED_TSV = WAVE1108_DIR / "wave1108-current-focused-candidates.tsv"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1115-unitai-carver-motion-activation-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1115-unitai-carver-motion-activation-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1115_unitai_carver_motion_activation_current_risk_review_2026-06-05.md"
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

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260605-010428_post_wave1115_unitai_carver_motion_activation_current_risk_review_verified"
LATEST_PRIOR_BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified"

PRIOR_PROBES = (
    "wave1109_cfastvb_current_risk_head_supersession.py",
    "wave1110_cfastvb_wave1053_remainder_supersession.py",
    "wave1111_cnamedmesh_current_risk_supersession.py",
    "wave1112_animal_wave1016_current_risk_supersession.py",
    "wave1113_battleengine_wave936_wave1010_current_risk_supersession.py",
    "wave1114_mixed_score27_current_risk_head_supersession.py",
)

TARGETS = {
    "0x00415140": {
        "name": "CUnitAI__HandleLandedStateTransition",
        "signature": "void __fastcall CUnitAI__HandleLandedStateTransition(void * unitAI)",
        "comment_tokens": ("landed-state transition", "+0x12c", "+0x264"),
        "xref": ("0x005e2400", "<no_function>", "DATA"),
        "decompile_tokens": ("landed", "0x12c", "0x264"),
    },
    "0x00415a50": {
        "name": "CUnitAI__CanCompleteDeployUndeployTransition",
        "signature": "int __fastcall CUnitAI__CanCompleteDeployUndeployTransition(void * unitAI)",
        "comment_tokens": ("transition predicate", "+0x10c", "+0x168"),
        "xref": ("0x005e23bc", "<no_function>", "DATA"),
        "decompile_tokens": ("0x10c", "0x168", "0x214", "0x2c"),
    },
    "0x00421c40": {
        "name": "CUnit__ApplyFlag4DampingAndScaleSpeed",
        "signature": "void __fastcall CUnit__ApplyFlag4DampingAndScaleSpeed(void * this)",
        "comment_tokens": ("flag-bit-4", "+0x11c", "CUnit__UpdateMotionAndTrailEffects"),
        "xref": ("0x005e2140", "<no_function>", "DATA"),
        "decompile_tokens": ("0x11c", "CUnit__UpdateMotionAndTrailEffects"),
    },
    "0x00422620": {
        "name": "CCarver__UpdateMotionAndWingPose",
        "signature": "void __fastcall CCarver__UpdateMotionAndWingPose(void * this)",
        "comment_tokens": ("Carver motion update", "wing/blend", "vfunc +0x70"),
        "xref": ("0x005e0e94", "<no_function>", "DATA"),
        "decompile_tokens": ("0x11c", "0x280", "CUnit__UpdateMotionAndTrailEffects"),
    },
    "0x00422fd0": {
        "name": "CCarverGuide__dtor_base",
        "signature": "void __fastcall CCarverGuide__dtor_base(void * this)",
        "comment_tokens": ("destructor-base", "+0x2c", "CMonitor__Shutdown"),
        "xref": ("0x00422fb3", "CCarverGuide__scalar_deleting_dtor", "UNCONDITIONAL_CALL"),
        "decompile_tokens": ("CMonitor__Shutdown", "0x2c"),
    },
    "0x00428110": {
        "name": "CUnitAI__UpdateActivationStateAndSpawnPickup",
        "signature": "void __fastcall CUnitAI__UpdateActivationStateAndSpawnPickup(void * this)",
        "comment_tokens": ("Gill_M_Claw_Hit", "CWorldPhysicsManager__CreatePickup", "cached-transform"),
        "xref": ("0x005e4300", "<no_function>", "DATA"),
        "decompile_tokens": ("Gill_M_Claw_Hit", "CWorldPhysicsManager__CreatePickup", "Activate"),
    },
    "0x00428500": {
        "name": "CUnitAI__RefreshCachedComponentTransform",
        "signature": "void __fastcall CUnitAI__RefreshCachedComponentTransform(void * this)",
        "comment_tokens": ("DAT_008a9aac", "Mat34__SetRows", "current tick"),
        "xref": ("0x004284d1", "CUnitAI__UpdateActivationStateAndSpawnPickup", "UNCONDITIONAL_CALL"),
        "decompile_tokens": ("DAT_008a9aac", "Mat34__SetRows", "0x26c"),
    },
    "0x00428800": {
        "name": "CUnitAI__HandleTriggerEventAndMoveToOffset",
        "signature": "bool __fastcall CUnitAI__HandleTriggerEventAndMoveToOffset(void * this)",
        "comment_tokens": ("marks the unit destroyed", "releases child units", "active reader"),
        "xref": ("0x005e42c0", "<no_function>", "DATA"),
        "decompile_tokens": ("CUnit__MarkDestroyedAndCleanupLinks", "0x26c"),
    },
    "0x004289b0": {
        "name": "CUnitAI__AdvanceActivationAnimationState",
        "signature": "bool __fastcall CUnitAI__AdvanceActivationAnimationState(void * this)",
        "comment_tokens": ("Hit/retract/normal/Activate/Activated/Deactivated", "animation state machine", "deploy/fire"),
        "xref": ("0x005e4088", "<no_function>", "DATA"),
        "decompile_tokens": ("Activate", "0x264"),
    },
    "0x00428b50": {
        "name": "CUnit__SetReaderAndComputeRelativeYaw",
        "signature": "void __thiscall CUnit__SetReaderAndComputeRelativeYaw(void * this, void * reader, void * readerContext, int unusedMode)",
        "comment_tokens": ("active-reader setter", "relative yaw", "0x100000"),
        "xref": ("0x004f8d7c", "CUnit__Init", "UNCONDITIONAL_CALL"),
        "decompile_tokens": ("0x26c", "0x274"),
    },
    "0x00428bc0": {
        "name": "CUnitAI__GetTargetHeadingWithOffset",
        "signature": "double __fastcall CUnitAI__GetTargetHeadingWithOffset(void * this)",
        "comment_tokens": ("active reader heading", "relative-yaw offset", "zero heading"),
        "xref": ("0x004292c7", "CUnitAI__UpdateHeadingTowardTargetClamped", "UNCONDITIONAL_CALL"),
        "decompile_tokens": ("0x26c", "return"),
    },
    "0x00428cb0": {
        "name": "CUnitAI__PlayHitAnimationAndSetFlag",
        "signature": "void __fastcall CUnitAI__PlayHitAnimationAndSetFlag(void * this)",
        "comment_tokens": ("Hit animation token", "+0x2bc", "ExplosionInitThing owner"),
        "xref": ("0x00479eb6", "CGillM__TriggerRandomArmHitAnimationIfReady", "UNCONDITIONAL_CALL"),
        "decompile_tokens": ("Hit", "0x2bc"),
    },
    "0x00429270": {
        "name": "CUnitAI__UpdateHeadingTowardTargetClamped",
        "signature": "void __fastcall CUnitAI__UpdateHeadingTowardTargetClamped(void * turnContext)",
        "comment_tokens": ("true entry at 0x00429270", "turn context", "turn-rate"),
        "xref": ("0x005d9660", "<no_function>", "DATA"),
        "decompile_tokens": ("0x00429270", "turnContext", "0x26c"),
    },
}

DOC_TOKENS = (
    "Wave1115",
    "wave1115-unitai-carver-motion-activation-current-risk-review",
    "56/1179 = 4.75%",
    "13 rows",
    "current focused candidates: 1179",
    "score-26 UnitAI/Carver motion/activation head",
    "fresh read-only Ghidra export",
    "no mutation",
    BACKUP,
    LATEST_PRIOR_BACKUP,
)

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "runtime ai behavior proven",
    "runtime movement behavior proven",
    "runtime steering behavior proven",
    "runtime carver behavior proven",
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
    if value in {"", "<none>"}:
        return value
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def contains_token(text: str, token: str) -> bool:
    normalized = text.replace("\\\\\\\\", "\\").replace("\\\\", "\\")
    return token in text or token.replace("\\", "\\\\") in text or token in normalized


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def row_map(path: Path, key: str = "address") -> dict[str, dict[str, str]]:
    return {normalize_address(row.get(key, "")): row for row in read_tsv(path)}


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


def check_wave1108_head(failures: list[str]) -> None:
    wave1108_current_risk_rank.generate()
    focused_rows = read_tsv(FOCUSED_TSV)
    require(len(focused_rows) == 1179, "Wave1108 focused row count mismatch", failures)
    focused = {normalize_address(row.get("address", "")): row for row in focused_rows}
    accounted = prior_accounted_addresses()
    require(len(accounted) == 43, f"prior accounted count mismatch: {len(accounted)}", failures)
    remaining = [row for row in focused_rows if normalize_address(row.get("address", "")) not in accounted]
    require(len(remaining) == 1136, f"remaining focused count mismatch: {len(remaining)}", failures)
    require(
        [normalize_address(row.get("address", "")) for row in remaining[:13]] == list(TARGETS),
        "Wave1115 targets are not the next thirteen unaccounted Wave1108 focused rows",
        failures,
    )
    for address, expected in TARGETS.items():
        row = focused.get(address)
        require(row is not None, f"Wave1108 focused row missing: {address}", failures)
        if row is None:
            continue
        require(row.get("name") == expected["name"], f"Wave1108 name mismatch: {address}", failures)
        require(row.get("score") == "26", f"Wave1108 score mismatch: {address}", failures)


def check_exports(failures: list[str]) -> None:
    counts = {
        "metadata.tsv": 13,
        "tags.tsv": 13,
        "xrefs.tsv": 20,
        "instructions.tsv": 1261,
        "decompile/index.tsv": 13,
    }
    for relative, expected in counts.items():
        path = BASE / relative
        require(path.is_file(), f"missing export {relative}", failures)
        if path.is_file():
            require(len(read_tsv(path)) == expected, f"{relative} row count mismatch", failures)

    log_tokens = {
        "metadata.log": "targets=13 found=13 missing=0",
        "tags.log": "ExportFunctionTagsByAddress complete: rows=13 missing=0",
        "xrefs.log": "Wrote 20 rows",
        "instructions.log": "targets=13 missing=0",
        "decompile.log": "targets=13 dumped=13 missing=0 failed=0",
    }
    for relative, token in log_tokens.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR", "MISSING\t", "failed=1", "missing=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_target_rows(failures: list[str]) -> None:
    metadata = row_map(BASE / "metadata.tsv")
    tags = row_map(BASE / "tags.tsv")
    decompile = row_map(BASE / "decompile" / "index.tsv")
    xrefs = read_tsv(BASE / "xrefs.tsv")
    instructions = read_tsv(BASE / "instructions.tsv")

    for address, expected in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"metadata missing: {address}", failures)
        if row is not None:
            require(row.get("name") == expected["name"], f"metadata name mismatch: {address}", failures)
            require(row.get("signature") == expected["signature"], f"metadata signature mismatch: {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch: {address}", failures)
            for token in expected["comment_tokens"]:
                require(token in row.get("comment", ""), f"metadata missing token {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"tags missing: {address}", failures)
        if tag_row is not None:
            require(tag_row.get("name") == expected["name"], f"tag name mismatch: {address}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch: {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"decompile index missing: {address}", failures)
        if dec is not None:
            require(dec.get("name") == expected["name"], f"decompile name mismatch: {address}", failures)
            require(dec.get("signature") == expected["signature"], f"decompile signature mismatch: {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch: {address}", failures)

        from_addr, from_function, ref_type = expected["xref"]
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
        require(
            any(
                normalize_address(row.get("target_addr", "")) == address
                and row.get("function_name") == expected["name"]
                for row in instructions
            ),
            f"missing instruction rows for {address}",
            failures,
        )
        decompile_files = list((BASE / "decompile").glob(f"{address[2:]}_*.c"))
        require(len(decompile_files) == 1, f"decompile file count mismatch for {address}", failures)
        if decompile_files:
            text = read_text(decompile_files[0])
            for token in expected["decompile_tokens"]:
                require(token in text, f"decompile missing token {address}: {token}", failures)


def check_current_queue(failures: list[str]) -> None:
    queue = row_map(QUEUE_TSV)
    for address, expected in TARGETS.items():
        row = queue.get(address)
        require(row is not None, f"current queue row missing: {address}", failures)
        if row is None:
            continue
        require(row.get("name") == expected["name"], f"current queue name mismatch: {address}", failures)
        require(row.get("signature") == expected["signature"], f"current queue signature mismatch: {address}", failures)
        require(row.get("status") == "OK", f"current queue status mismatch: {address}", failures)
        for token in expected["comment_tokens"][:2]:
            require(token in row.get("comment", ""), f"current queue missing comment token {address}: {token}", failures)


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
        "wave1115 note": read_text(NOTE),
        "wave1115 readiness": read_text(READINESS),
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
            require(f"{address} {expected['name']}" in text, f"missing target in {name}: {address}", failures)
        lowered = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lowered, f"overclaim token in {name}: {bad}", failures)
    require(read_text(NOTE) == read_text(NOTE_MIRROR), "wave1115 note mirror mismatch", failures)
    require(read_text(MAPPED_SYSTEMS) == read_text(MAPPED_SYSTEMS_MIRROR), "mapped-systems mirror mismatch", failures)
    require(read_text(PROGRESS) == read_text(PROGRESS_MIRROR), "static progress mirror mismatch", failures)

    progress = read_json(PROGRESS)
    latest = progress.get("latestWave", {})
    require(latest.get("wave") == "Wave1115 UnitAI/Carver motion activation current-risk review", "latest wave mismatch", failures)
    require(latest.get("tag") == "wave1115-unitai-carver-motion-activation-current-risk-review", "latest tag mismatch", failures)
    require(latest.get("backup") == BACKUP, "latest backup mismatch", failures)
    current = progress.get("post100Reaudit", {}).get("currentRiskRank", {})
    require(current.get("focusedReviewed") == 56, "progress focusedReviewed mismatch", failures)
    require(current.get("focusedReviewedPercent") == "4.75%", "progress focusedReviewedPercent mismatch", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:wave1115-unitai-carver-motion-activation-current-risk-review")
        == r"py -3 tools\wave1115_unitai_carver_motion_activation_current_risk_review.py --check",
        "missing package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_wave1108_head(failures)
    check_exports(failures)
    check_target_rows(failures)
    check_current_queue(failures)
    check_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave1115 UnitAI/Carver motion activation current-risk review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1115 UnitAI/Carver motion activation current-risk review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
