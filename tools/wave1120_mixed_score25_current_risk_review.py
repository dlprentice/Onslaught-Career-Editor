#!/usr/bin/env python3
"""Validate Wave1120 mixed score-25 current-risk review."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import re
import sys
from pathlib import Path

import wave1108_current_risk_rank


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1120-mixed-score25-current-risk-review"
FOCUSED_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-focused-candidates.tsv"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1120-mixed-score25-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1120-mixed-score25-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1120_mixed_score25_current_risk_review_2026-06-05.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
MAPPED_SYSTEMS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PROGRESS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

PARTICLE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "ParticleManager.cpp" / "_index.md"
PARTICLE_DOC_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "functions" / "ParticleManager.cpp" / "_index.md"
GENERAL_VOLUME_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "GeneralVolume.cpp" / "_index.md"
GENERAL_VOLUME_DOC_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "functions" / "GeneralVolume.cpp" / "_index.md"
UNIT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Unit.cpp" / "_index.md"
UNIT_DOC_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "functions" / "Unit.cpp" / "_index.md"
POD_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Pod.cpp" / "_index.md"
POD_DOC_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "functions" / "Pod.cpp" / "_index.md"
SCRIPT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Script.cpp" / "_index.md"
SCRIPT_DOC_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "functions" / "Script.cpp" / "_index.md"
FASTVB_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FastVB.cpp" / "_index.md"
FASTVB_DOC_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "functions" / "FastVB.cpp" / "_index.md"

BACKUP = r"G:\GhidraBackups\BEA_20260605-025952_post_wave1120_mixed_score25_current_risk_review_verified"
PRIOR_BACKUP = r"G:\GhidraBackups\BEA_20260605-022812_post_wave1119_mixed_score26_current_risk_review_verified"

PRIOR_PROBES = (
    "wave1109_cfastvb_current_risk_head_supersession.py",
    "wave1110_cfastvb_wave1053_remainder_supersession.py",
    "wave1111_cnamedmesh_current_risk_supersession.py",
    "wave1112_animal_wave1016_current_risk_supersession.py",
    "wave1113_battleengine_wave936_wave1010_current_risk_supersession.py",
    "wave1114_mixed_score27_current_risk_head_supersession.py",
    "wave1115_unitai_carver_motion_activation_current_risk_review.py",
    "wave1116_door_wing_ai_current_risk_review.py",
    "wave1117_cengine_current_risk_review.py",
    "wave1118_particle_message_current_risk_review.py",
    "wave1119_mixed_score26_current_risk_review.py",
)

TARGETS = {
    "0x00405d80": (
        "CParticleManager__RemoveFromGlobalList_Thunk",
        "void __fastcall CParticleManager__RemoveFromGlobalList_Thunk(void * node)",
        ("jump thunk", "CParticleManager__RemoveFromGlobalList", "exact source identity"),
        ("0x005d20f6", "Unwind@005d20f0", "UNCONDITIONAL_CALL"),
        ("CParticleManager__RemoveFromGlobalList(node)",),
    ),
    "0x0040dfb0": (
        "CGeneralVolume__SpawnPickupAndDispatch",
        "void __thiscall CGeneralVolume__SpawnPickupAndDispatch(void * this)",
        ("pickup spawn/dispatch", "CWorldPhysicsManager__CreatePickup", "runtime pickup behavior"),
        ("0x00408160", "CUnit__ProcessStateSwapAndDeathChecks", "UNCONDITIONAL_CALL"),
        ("CWorldPhysicsManager__CreatePickup",),
    ),
    "0x004bfe00": (
        "CUnit__dtor_base_Thunk_004bfe00",
        "void __fastcall CUnit__dtor_base_Thunk_004bfe00(void * this)",
        ("Wave460 correction", "CUnit__dtor_base", "jump thunk"),
        ("0x0050ee93", "CUnit__scalar_deleting_dtor", "UNCONDITIONAL_CALL"),
        ("CUnit__dtor_base(this)",),
    ),
    "0x004d3630": (
        "CPod__VFunc_66_UpdateMotionAndAccumulateScalar",
        "void __fastcall CPod__VFunc_66_UpdateMotionAndAccumulateScalar(void * this)",
        ("Wave486", "0x005dff8c", "slot 66", "this+0x84"),
        ("0x005e0094", "<no_function>", "DATA"),
        ("CUnit__UpdateMotionAttachmentsAndEffects", "+ 0xb4"),
    ),
    "0x004ef100": (
        "CUnit__VFunc64_SpawnConfiguredPickupThreeTimes",
        "void __fastcall CUnit__VFunc64_SpawnConfiguredPickupThreeTimes(void * this)",
        ("Wave830", "0x005e1610", "CUnit__SpawnConfiguredPickupIfAboveWater"),
        ("0x005e1610", "<no_function>", "DATA"),
        ("CUnit__SpawnConfiguredPickupIfAboveWater",),
    ),
    "0x0052d3d0": (
        "CAsmInstruction__SpawnFromOpcode",
        "void * __cdecl CAsmInstruction__SpawnFromOpcode(int opcode, void * bytecode_reader)",
        ("Wave573", "bytecode instruction factory", "fatal unknown-instruction"),
        ("0x00538f3e", "CScriptObjectCode__CScriptObjectCode", "UNCONDITIONAL_CALL"),
        ("switch(opcode)", "s_FATAL_ERROR__uknown_instruction"),
    ),
    "0x0052ec60": (
        "CDataType__CreateFromType",
        "void * __cdecl CDataType__CreateFromType(int type_id, void * bytecode_reader)",
        ("Wave575", "type_id 1..6", "CBoolDataType", "unknown-data-type"),
        ("0x00539818", "CScriptObjectCode__ReadSymbolTable", "UNCONDITIONAL_CALL"),
        ("switch(type_id)", "CFloatDataType", "unknown_data_type"),
    ),
    "0x00599d80": (
        "CFastVB__FlattenNodeTreeLeafByLinearIndex",
        "int __thiscall CFastVB__FlattenNodeTreeLeafByLinearIndex(void * this, void * node_tree, uint linear_leaf_index, void * out_leaf_scratch)",
        ("Wave709", "RET 0xc", "0x80004005", "node tree"),
        ("0x0059a4b3", "CFastVB__AreNodeTreesCompatible", "UNCONDITIONAL_CALL"),
        ("0x80004005", "linear_leaf_index", "out_leaf_scratch"),
    ),
}

EXPECTED_TAG_TOKENS = {
    "0x004bfe00": ("object-cleanup-wave460", "dtor-base", "thunk"),
    "0x004d3630": ("engine-pod-ballistic-wave486", "cpod", "vfunc-slot-66"),
    "0x004ef100": ("cunit-vfunc64-pickup-wave830", "wave830-readback-verified", "configured-pickup"),
    "0x0052d3d0": ("script-datatype-head-wave573", "mission-script", "opcode-factory"),
    "0x0052ec60": ("datatype-factory-float-head-wave575", "datatype-factory", "type-id-switch"),
    "0x00599d80": ("node-tree-compatibility-wave709", "wave709-readback-verified", "flatten-leaf-by-index"),
}

DOC_TOKENS = (
    "Wave1120",
    "wave1120-mixed-score25-current-risk-review",
    "118/1179 = 10.01%",
    "8 rows",
    "current focused candidates: 1179",
    "score-25 mixed current-risk head",
    "fresh read-only Ghidra export",
    "no mutation",
    "0 / 0 / 0",
    BACKUP,
    PRIOR_BACKUP,
)

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "runtime pickup behavior proven",
    "runtime unit behavior proven",
    "runtime missionScript behavior proven",
    "runtime fastvb parser/render behavior proven",
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
    require(len(accounted) == 110, f"prior accounted count mismatch: {len(accounted)}", failures)
    require(len(remaining) == 1069, f"remaining focused count mismatch: {len(remaining)}", failures)
    require([normalize_address(row.get("address", "")) for row in remaining[:8]] == list(TARGETS), "Wave1120 targets are not the next eight unaccounted Wave1108 focused rows", failures)
    for row in remaining[:8]:
        require(row.get("score") == "25", f"Wave1108 score mismatch: {row.get('address')}", failures)


def check_exports(failures: list[str]) -> None:
    counts = {
        "metadata.tsv": 8,
        "tags.tsv": 8,
        "xrefs.tsv": 59,
        "instructions.tsv": 936,
        "decompile/index.tsv": 8,
    }
    for relative, expected in counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)
    log_tokens = {
        "metadata.log": "targets=8 found=8 missing=0",
        "tags.log": "ExportFunctionTagsByAddress complete: rows=8 missing=0",
        "xrefs.log": "Wrote 59 rows",
        "instructions.log": "targets=8 missing=0",
        "decompile.log": "targets=8 dumped=8 missing=0 failed=0",
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
    queue = row_map(QUEUE_TSV)

    for address, expected in TARGETS.items():
        name, signature, comment_tokens, xref, decompile_tokens = expected
        for label, rows in (("metadata", metadata), ("current queue", queue)):
            row = rows.get(address)
            require(row is not None, f"{label} missing: {address}", failures)
            if row is not None:
                require(row.get("name") == name, f"{label} name mismatch at {address}", failures)
                require(row.get("signature") == signature, f"{label} signature mismatch at {address}", failures)
                require(row.get("status") == "OK", f"{label} status mismatch at {address}", failures)
                for token in comment_tokens:
                    require(token in row.get("comment", ""), f"{label} missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            require(tag_row.get("name") == name, f"tag name mismatch at {address}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)
            for token in EXPECTED_TAG_TOKENS.get(address, ()):
                require(token in tag_row.get("tags", ""), f"missing tag token at {address}: {token}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row for {address}", failures)
        if dec is not None:
            require(dec.get("name") == name, f"decompile name mismatch at {address}", failures)
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)
            dec_text = read_text(BASE / "decompile" / f"{address[2:]}_{name}.c")
            for token in decompile_tokens:
                require(token in dec_text, f"missing decompile token at {address}: {token}", failures)

        xref_from, xref_function, xref_type = xref
        require(
            any(
                normalize_address(row.get("target_addr", "")) == address
                and normalize_address(row.get("from_addr", "")) == normalize_address(xref_from)
                and row.get("from_function") == xref_function
                and row.get("ref_type") == xref_type
                for row in xrefs
            ),
            f"missing expected xref for {address}",
            failures,
        )


def check_backup(failures: list[str]) -> None:
    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 175541127, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs_and_state(failures: list[str]) -> None:
    core_docs = [
        NOTE,
        NOTE_MIRROR,
        READINESS,
        MAPPED_SYSTEMS,
        MAPPED_SYSTEMS_MIRROR,
        CAMPAIGN,
        BINARY_INDEX,
        RE_INDEX,
        FUNCTION_COVERAGE,
        FUNCTION_INDEX,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    address_tokens = tuple(f"{address} {target[0]}" for address, target in TARGETS.items())
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS + address_tokens:
            require(contains_token(text, token), f"missing doc token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad.lower() not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    owner_docs = {
        PARTICLE_DOC: ("Wave1120", "0x00405d80 CParticleManager__RemoveFromGlobalList_Thunk", BACKUP),
        PARTICLE_DOC_MIRROR: ("Wave1120", "0x00405d80 CParticleManager__RemoveFromGlobalList_Thunk", BACKUP),
        GENERAL_VOLUME_DOC: ("Wave1120", "0x0040dfb0 CGeneralVolume__SpawnPickupAndDispatch", "CWorldPhysicsManager__CreatePickup", BACKUP),
        GENERAL_VOLUME_DOC_MIRROR: ("Wave1120", "0x0040dfb0 CGeneralVolume__SpawnPickupAndDispatch", "CWorldPhysicsManager__CreatePickup", BACKUP),
        UNIT_DOC: ("Wave1120", "0x004bfe00 CUnit__dtor_base_Thunk_004bfe00", "0x004ef100 CUnit__VFunc64_SpawnConfiguredPickupThreeTimes", BACKUP),
        UNIT_DOC_MIRROR: ("Wave1120", "0x004bfe00 CUnit__dtor_base_Thunk_004bfe00", "0x004ef100 CUnit__VFunc64_SpawnConfiguredPickupThreeTimes", BACKUP),
        POD_DOC: ("Wave1120", "0x004d3630 CPod__VFunc_66_UpdateMotionAndAccumulateScalar", "0x005e0094", BACKUP),
        POD_DOC_MIRROR: ("Wave1120", "0x004d3630 CPod__VFunc_66_UpdateMotionAndAccumulateScalar", "0x005e0094", BACKUP),
        SCRIPT_DOC: ("Wave1120", "0x0052d3d0 CAsmInstruction__SpawnFromOpcode", "0x0052ec60 CDataType__CreateFromType", BACKUP),
        SCRIPT_DOC_MIRROR: ("Wave1120", "0x0052d3d0 CAsmInstruction__SpawnFromOpcode", "0x0052ec60 CDataType__CreateFromType", BACKUP),
        FASTVB_DOC: ("Wave1120", "0x00599d80 CFastVB__FlattenNodeTreeLeafByLinearIndex", "0x80004005", BACKUP),
        FASTVB_DOC_MIRROR: ("Wave1120", "0x00599d80 CFastVB__FlattenNodeTreeLeafByLinearIndex", "0x80004005", BACKUP),
    }
    for path, tokens in owner_docs.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing owner-doc token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad.lower() not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    progress = read_json(PROGRESS)
    mirror = read_json(PROGRESS_MIRROR)
    commit_pattern = re.compile(r"^(pending Wave1120 artifact commit|[0-9a-f]{40})$")
    for label, data in (("progress", progress), ("progress mirror", mirror)):
        current = data["post100Reaudit"]["currentRiskRank"]
        require(data["latestWave"]["wave"] == "Wave1120 mixed score-25 current-risk review", f"{label} latest wave mismatch", failures)
        require(data["latestWave"]["tag"] == "wave1120-mixed-score25-current-risk-review", f"{label} latest tag mismatch", failures)
        require(data["latestWave"]["backup"] == BACKUP, f"{label} backup mismatch", failures)
        require(bool(commit_pattern.match(data["latestWave"].get("artifactCommit", ""))), f"{label} artifact commit mismatch", failures)
        require(current["focusedReviewed"] == 118, f"{label} focused reviewed mismatch", failures)
        require(current["focusedReviewedPercent"] == "10.01%", f"{label} focused percent mismatch", failures)
        require(current["latestReviewTag"] == "wave1120-mixed-score25-current-risk-review", f"{label} review tag mismatch", failures)

    package = read_json(PACKAGE_JSON)
    expected_script = r"py -3 tools\wave1120_mixed_score25_current_risk_review.py --check"
    require(package["scripts"].get("test:wave1120-mixed-score25-current-risk-review") == expected_script, "missing package script", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_wave1108_head(failures)
    check_exports(failures)
    check_target_rows(failures)
    check_backup(failures)
    check_docs_and_state(failures)
    if failures:
        print("Wave1120 mixed score-25 current-risk review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1120 mixed score-25 current-risk review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
