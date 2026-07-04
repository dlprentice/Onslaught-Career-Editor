#!/usr/bin/env python3
"""Validate Wave1119 mixed score-26 current-risk review."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1119-mixed-score26-current-risk-review"
FOCUSED_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-focused-candidates.tsv"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1119-mixed-score26-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1119-mixed-score26-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1119_mixed_score26_current_risk_review_2026-06-05.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
MAPPED_SYSTEMS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PROGRESS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

PAUSE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "PauseMenu.cpp" / "_index.md"
PAUSE_DOC_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "functions" / "PauseMenu.cpp" / "_index.md"
ENGINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "engine.cpp" / "_index.md"
ENGINE_DOC_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "functions" / "engine.cpp" / "_index.md"
BUILDING_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Building.cpp" / "_index.md"
BUILDING_DOC_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "functions" / "Building.cpp" / "_index.md"
SENTINEL_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Sentinel.cpp" / "_index.md"
SENTINEL_DOC_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "functions" / "Sentinel.cpp" / "_index.md"
UNIT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Unit.cpp" / "_index.md"
UNIT_DOC_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "functions" / "Unit.cpp" / "_index.md"
FASTVB_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FastVB.cpp" / "_index.md"
FASTVB_DOC_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "functions" / "FastVB.cpp" / "_index.md"
MATH_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Math.cpp" / "_index.md"
MATH_DOC_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "functions" / "Math.cpp" / "_index.md"

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260605-022812_post_wave1119_mixed_score26_current_risk_review_verified"
PRIOR_BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260605-021103_post_wave1118_particle_message_current_risk_review_verified"
ARTIFACT_COMMIT = "0474d555bb2d5ef1c4d88599e3eaee4aede11c7e"

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
)

TARGETS = {
    "0x004d05e0": (
        "CPauseMenu__dtor_base",
        "void __fastcall CPauseMenu__dtor_base(void * pause_menu)",
        ("Wave465 correction", "CMonitor__Shutdown", "pause textures"),
        ("0x004d04b3", "CPauseMenu__scalar_deleting_dtor", "UNCONDITIONAL_CALL"),
        ("CSPtrSet__Clear", "CMonitor__Shutdown", "DAT_0082b490"),
    ),
    "0x004d0e40": (
        "CGameMenu__InitBase",
        "void __fastcall CGameMenu__InitBase(void * game_menu)",
        ("Wave465 correction", "PTR_SharedVFunc__NoOpOneArg_004014c0_005dc72c", "CMenuItemRangeVariant"),
        ("0x004d0917", "CPauseMenu__ButtonPressed", "UNCONDITIONAL_CALL"),
        ("PTR_SharedVFunc__NoOpOneArg_004014c0_005dc72c", "game_menu + 4"),
    ),
    "0x004d1750": (
        "CSimpleGameMenu__dtor_base",
        "void __fastcall CSimpleGameMenu__dtor_base(void * simple_game_menu)",
        ("Wave474 correction", "active-reader nodes", "CMonitor base"),
        ("0x004d1733", "CSimpleGameMenu__scalar_deleting_dtor", "UNCONDITIONAL_CALL"),
        ("CGenericActiveReader__dtor", "CMenuItemRange__Destructor", "CMonitor__Shutdown"),
    ),
    "0x004d3020": (
        "CEngine__SetOptionValueAndNotifyTarget",
        "void __thiscall CEngine__SetOptionValueAndNotifyTarget(void * this, int option_value)",
        ("Wave486", "RET 0x4", "0x00662ab0", "god/options path"),
        ("0x00472d09", "CGameInterface__HandleMenuSelection", "UNCONDITIONAL_CALL"),
        ("CAREER_mMusicVolume", "0xe0", "0x154"),
    ),
    "0x004d6d10": (
        "CRepairPadAI__VFunc_11_UpdateDockCandidateReader",
        "void * __fastcall CRepairPadAI__VFunc_11_UpdateDockCandidateReader(void * this)",
        ("Wave491", "0x005d8e08 slot 11", "CMapWho", "CRepairPadAI__IsCompatibleDockCandidate"),
        ("0x005d8e34", "<no_function>", "DATA"),
        ("CMapWho__GetFirstEntryWithinRadius", "CRepairPadAI__IsCompatibleDockCandidate", "CGenericActiveReader__SetReader"),
    ),
    "0x004de1d0": (
        "CSafeSide__ShutdownAndUnlinkFactionAnchor",
        "void __fastcall CSafeSide__ShutdownAndUnlinkFactionAnchor(void * this)",
        ("Wave542", "0x005dcce4", "DAT_00855160", "CComplexThing__Shutdown"),
        ("0x005dcce4", "<no_function>", "DATA"),
        ("DAT_00855160", "CSPtrSet__Remove", "CComplexThing__Shutdown"),
    ),
    "0x004fc3c0": (
        "SharedUnitVFunc__ResolveField17cVectorContext_004fc3c0",
        "void __thiscall SharedUnitVFunc__ResolveField17cVectorContext_004fc3c0(void * this, void * candidate, void * outA, void * outB, void * arg3, void * arg4)",
        ("Wave1085", "this+0x17c list", "0x0044a850", "0x0044a930"),
        ("0x005d8fe0", "<no_function>", "DATA"),
        ("0x17c", "OID__GetAttachmentOrOriginTransform", "OID__GetAttachmentOrBaseOrientationMatrix"),
    ),
    "0x0050ee90": (
        "CUnit__scalar_deleting_dtor",
        "void * __thiscall CUnit__scalar_deleting_dtor(void * this, byte flags)",
        ("Wave460 correction", "CUnit__dtor_base_Thunk_004bfe00", "CDXMemoryManager__Free", "RET 0x4"),
        ("0x005dfd40", "<no_function>", "DATA"),
        ("CUnit__dtor_base_Thunk_004bfe00", "CDXMemoryManager__Free", "flags"),
    ),
    "0x005b85c0": (
        "Math__Atan2ApproxPacked",
        "int Math__Atan2ApproxPacked(void)",
        ("Wave737", "CFastVB__DispatchOp_InterpolateQuaternionPairCore", "0x0065ed98", "hidden MM0/MM1"),
        ("0x005a4e3d", "CFastVB__DispatchOp_InterpolateQuaternionPairCore_005a4d98", "UNCONDITIONAL_CALL"),
        ("PackedFloatingMAX", "DAT_0065ed98", "return in_EAX"),
    ),
    "0x005b86c0": (
        "CFastVB__FastAcosApprox_Scalar",
        "int CFastVB__FastAcosApprox_Scalar(void)",
        ("Wave737", "axis-angle extraction", "0x0065ed9c", "hidden MM0"),
        ("0x005a481a", "CFastVB__DispatchOp_ExtractAxisAndOptionalAngle", "UNCONDITIONAL_CALL"),
        ("PackedFloatingReciprocalSQRAprox", "DAT_0065ed9c", "return in_EAX"),
    ),
}

DOC_TOKENS = (
    "Wave1119",
    "wave1119-mixed-score26-current-risk-review",
    "110/1179 = 9.33%",
    "10 rows",
    "current focused candidates: 1179",
    "score-26 mixed current-risk head",
    "fresh read-only Ghidra export",
    "no mutation",
    BACKUP,
    PRIOR_BACKUP,
)

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "runtime ui behavior proven",
    "runtime repair behavior proven",
    "runtime faction-anchor behavior proven",
    "runtime math behavior proven",
    "runtime unit behavior proven",
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
    require(len(accounted) == 100, f"prior accounted count mismatch: {len(accounted)}", failures)
    require(len(remaining) == 1079, f"remaining focused count mismatch: {len(remaining)}", failures)
    require([normalize_address(row.get("address", "")) for row in remaining[:10]] == list(TARGETS), "Wave1119 targets are not the next ten unaccounted Wave1108 focused rows", failures)
    for row in remaining[:10]:
        require(row.get("score") == "26", f"Wave1108 score mismatch: {row.get('address')}", failures)


def check_exports(failures: list[str]) -> None:
    counts = {
        "metadata.tsv": 10,
        "tags.tsv": 10,
        "xrefs.tsv": 67,
        "instructions.tsv": 1170,
        "decompile/index.tsv": 10,
    }
    for relative, expected in counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)
    log_tokens = {
        "metadata.log": "targets=10 found=10 missing=0",
        "tags.log": "ExportFunctionTagsByAddress complete: rows=10 missing=0",
        "xrefs.log": "Wrote 67 rows",
        "instructions.log": "targets=10 missing=0",
        "decompile.log": "targets=10 dumped=10 missing=0 failed=0",
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
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing doc token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    owner_docs = {
        PAUSE_DOC: ("Wave1119", "wave1119-mixed-score26-current-risk-review", "0x004d05e0 CPauseMenu__dtor_base", "0x004d1750 CSimpleGameMenu__dtor_base", BACKUP),
        PAUSE_DOC_MIRROR: ("Wave1119", "wave1119-mixed-score26-current-risk-review", "0x004d05e0 CPauseMenu__dtor_base", "0x004d1750 CSimpleGameMenu__dtor_base", BACKUP),
        ENGINE_DOC: ("Wave1119", "0x004d3020 CEngine__SetOptionValueAndNotifyTarget", "0x00662ab0", BACKUP),
        ENGINE_DOC_MIRROR: ("Wave1119", "0x004d3020 CEngine__SetOptionValueAndNotifyTarget", "0x00662ab0", BACKUP),
        BUILDING_DOC: ("Wave1119", "0x004d6d10 CRepairPadAI__VFunc_11_UpdateDockCandidateReader", "0x005d8e08 slot 11", BACKUP),
        BUILDING_DOC_MIRROR: ("Wave1119", "0x004d6d10 CRepairPadAI__VFunc_11_UpdateDockCandidateReader", "0x005d8e08 slot 11", BACKUP),
        SENTINEL_DOC: ("Wave1119", "0x004de1d0 CSafeSide__ShutdownAndUnlinkFactionAnchor", "DAT_00855160", BACKUP),
        SENTINEL_DOC_MIRROR: ("Wave1119", "0x004de1d0 CSafeSide__ShutdownAndUnlinkFactionAnchor", "DAT_00855160", BACKUP),
        UNIT_DOC: ("Wave1119", "0x004fc3c0 SharedUnitVFunc__ResolveField17cVectorContext_004fc3c0", "0x0050ee90 CUnit__scalar_deleting_dtor", BACKUP),
        UNIT_DOC_MIRROR: ("Wave1119", "0x004fc3c0 SharedUnitVFunc__ResolveField17cVectorContext_004fc3c0", "0x0050ee90 CUnit__scalar_deleting_dtor", BACKUP),
        FASTVB_DOC: ("Wave1119", "0x005b85c0 Math__Atan2ApproxPacked", "0x005b86c0 CFastVB__FastAcosApprox_Scalar", BACKUP),
        FASTVB_DOC_MIRROR: ("Wave1119", "0x005b85c0 Math__Atan2ApproxPacked", "0x005b86c0 CFastVB__FastAcosApprox_Scalar", BACKUP),
        MATH_DOC: ("Wave1119", "0x005b85c0 Math__Atan2ApproxPacked", "0x005b86c0 CFastVB__FastAcosApprox_Scalar", BACKUP),
        MATH_DOC_MIRROR: ("Wave1119", "0x005b85c0 Math__Atan2ApproxPacked", "0x005b86c0 CFastVB__FastAcosApprox_Scalar", BACKUP),
    }
    for path, tokens in owner_docs.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing owner-doc token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    progress = read_json(PROGRESS)
    mirror = read_json(PROGRESS_MIRROR)
    for label, data in (("progress", progress), ("progress mirror", mirror)):
        current = data["post100Reaudit"]["currentRiskRank"]
        require(data["latestWave"]["wave"] == "Wave1119 mixed score-26 current-risk review", f"{label} latest wave mismatch", failures)
        require(data["latestWave"]["tag"] == "wave1119-mixed-score26-current-risk-review", f"{label} latest tag mismatch", failures)
        require(data["latestWave"]["backup"] == BACKUP, f"{label} backup mismatch", failures)
        require(data["latestWave"]["artifactCommit"] == ARTIFACT_COMMIT, f"{label} artifact commit mismatch", failures)
        require(current["focusedReviewed"] == 110, f"{label} focused reviewed mismatch", failures)
        require(current["focusedReviewedPercent"] == "9.33%", f"{label} focused percent mismatch", failures)
        require(current["latestReviewTag"] == "wave1119-mixed-score26-current-risk-review", f"{label} review tag mismatch", failures)

    package = read_json(PACKAGE_JSON)
    expected_script = r"py -3 tools\wave1119_mixed_score26_current_risk_review.py --check"
    require(package["scripts"].get("test:wave1119-mixed-score26-current-risk-review") == expected_script, "missing package script", failures)


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
        print("Wave1119 mixed score-26 current-risk review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1119 mixed score-26 current-risk review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
