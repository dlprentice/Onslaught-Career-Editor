#!/usr/bin/env python3
"""Validate Wave1174 Building / NamedMesh current-risk read-only artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1174-building-namedmesh-current-risk-review"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1174-building-namedmesh-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1174-building-namedmesh-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1174_building_namedmesh_current_risk_review_2026-06-06.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
RANK = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
BUILDING_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Building.cpp" / "_index.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"G:\GhidraBackups\BEA_20260606-075804_post_wave1174_building_namedmesh_current_risk_review_verified"

TARGETS = {
    "0x00418450": (
        "CBuildingNamedMesh__VFuncSlot_02_RemoveFromWorldAndForwardNamedMesh",
        "void __fastcall CBuildingNamedMesh__VFuncSlot_02_RemoveFromWorldAndForwardNamedMesh(void * this)",
        ("0x005d9114", "world occupancy grid", "CNamedMesh slot 2"),
    ),
    "0x004178a0": (
        "CBuilding__ProcessClosingAndUnshuttingAnimations",
        "void __fastcall CBuilding__ProcessClosingAndUnshuttingAnimations(void * this)",
        ("CBuilding vtable DATA xref", "+0x254", "+0x268", "closing/unshutting"),
    ),
    "0x004bbcd0": (
        "CNamedMesh__VFunc_09_004bbcd0",
        "void __thiscall CNamedMesh__VFunc_09_004bbcd0(void * this, void * init_record, void * unused_slot_arg)",
        ("Wave796", "CActor__Init", "event 3000", "occupancy/static-shadow"),
    ),
    "0x00418120": (
        "CBuilding__AdvanceOpenCloseAnimationState",
        "int __fastcall CBuilding__AdvanceOpenCloseAnimationState(void * this)",
        ("CBuilding vtable DATA xref", "vfunc +0x58", "vfunc +0xf0", "+0x254/+0x264"),
    ),
    "0x004183d0": (
        "CBuildingNamedMesh__dtor_base",
        "void __fastcall CBuildingNamedMesh__dtor_base(void * this)",
        ("0x005d910c", "CBuildingNamedMesh", "CActor__dtor_base"),
    ),
}

DECOMPILE_TOKENS = {
    "0x00418450": ("CWorld__RemoveUnitFromOccupancyGrid_Thunk", "CNamedMesh__VFunc02_RemoveFromOccupancyAndForward"),
    "0x004178a0": ("CUnit__UpdateClosingAndUnshuttingState", "s_closing_00623b80", "s_unshutting_00623b74"),
    "0x004bbcd0": ("CActor__Init", "3000", "CWorld__AddUnitToOccupancyGridAndRebuildShadows_Thunk"),
    "0x00418120": ("s_closing_00623b80", "s_unshutting_00623b74", "CMesh__FindAnimationIndexByName"),
    "0x004183d0": ("CActor__dtor_base",),
}

EXPECTED_XREFS = (
    ("0x00418450", "0x005d9114", "DATA"),
    ("0x004178a0", "0x005d8fbc", "DATA"),
    ("0x004bbcd0", "0x005dd614", "DATA"),
    ("0x004bbcd0", "0x004183a8", "UNCONDITIONAL_CALL"),
    ("0x00418120", "0x005d8fa0", "DATA"),
    ("0x004183d0", "0x00418433", "UNCONDITIONAL_CALL"),
)

DOC_TOKENS = (
    "Wave1174",
    "wave1174-building-namedmesh-current-risk-review",
    "680/1179 = 57.68%",
    "5 Building/CBuildingNamedMesh/CNamedMesh current-risk rows",
    "current focused candidates: 1178",
    "live regenerated current focused candidates: 1178",
    "remaining active focused work: 499",
    "current risk candidates: 6166",
    "fresh Ghidra export",
    "read-only review",
    "no mutation",
    "Codex read-only consult used",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "6 xref rows",
    "288 instruction rows",
    "CBuildingNamedMesh__VFuncSlot_02_RemoveFromWorldAndForwardNamedMesh",
    "CBuilding__ProcessClosingAndUnshuttingAnimations",
    "CNamedMesh__VFunc_09_004bbcd0",
    "CBuilding__AdvanceOpenCloseAnimationState",
    "CBuildingNamedMesh__dtor_base",
    "Wave944",
    "building-namedmesh-lifecycle-review-wave944",
    "Wave1111",
    "wave1111-cnamedmesh-current-risk-supersession",
    "0x005d8fbc",
    "0x005d8fa0",
    "0x005d910c",
    "0x005d9114",
    "0x005dd5f0",
    BACKUP,
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
)

OVERCLAIMS = (
    "runtime building animation behavior proven",
    "runtime namedmesh/world-occupancy behavior proven",
    "exact source virtual names proven",
    "exact source-body identity proven",
    "rebuild parity proven",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def normalize(address: str) -> str:
    value = (address or "").strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 5,
        "pre-tags.tsv": 5,
        "pre-xrefs.tsv": 6,
        "pre-instructions.tsv": 288,
        "pre-decompile/index.tsv": 5,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    tags = {normalize(row["address"]): row for row in read_tsv(BASE / "pre-tags.tsv")}
    decompile = {normalize(row["address"]): row for row in read_tsv(BASE / "pre-decompile" / "index.tsv")}
    xrefs = read_tsv(BASE / "pre-xrefs.tsv")

    for address, (name, signature, comment_tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata {address}", failures)
        if row:
            require(row.get("name") == name, f"name mismatch {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
            for token in comment_tokens:
                require(token in row.get("comment", ""), f"missing comment token {address}: {token}", failures)
        tag_row = tags.get(address)
        require(tag_row is not None and tag_row.get("status") == "OK", f"tag status mismatch {address}", failures)
        dec = decompile.get(address)
        require(
            dec is not None and dec.get("name") == name and dec.get("signature") == signature and dec.get("status") == "OK",
            f"decompile mismatch {address}",
            failures,
        )
        if dec is not None:
            decompile_path = BASE / "pre-decompile" / f"{address[2:]}_{name}.c"
            decompile_text = read_text(decompile_path)
            for token in DECOMPILE_TOKENS[address]:
                require(token in decompile_text, f"missing decompile token {address}: {token}", failures)

    for target, from_addr, ref_type in EXPECTED_XREFS:
        require(
            any(
                normalize(row.get("target_addr", "")) == target
                and normalize(row.get("from_addr", "")) == from_addr
                and row.get("ref_type") == ref_type
                for row in xrefs
            ),
            f"missing xref {target} <- {from_addr} {ref_type}",
            failures,
        )


def check_logs_backup_progress(failures: list[str]) -> None:
    expected_logs = {
        "pre-metadata.log": "targets=5 found=5 missing=0",
        "pre-tags.log": "rows=5 missing=0",
        "pre-xrefs.log": "Wrote 6 rows",
        "pre-instructions.log": "Wrote 288 function-body instruction rows",
        "pre-decompile.log": "targets=5 dumped=5 missing=0 failed=0",
    }
    for relative, token in expected_logs.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 176065415, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)

    progress = read_json(PROGRESS)
    latest = progress.get("latestWave", {})
    require(latest.get("wave") == "Wave1174 Building NamedMesh Current-Risk Review", "latest progress wave mismatch", failures)
    require(latest.get("tag") == "wave1174-building-namedmesh-current-risk-review", "latest progress tag mismatch", failures)
    require(latest.get("backup") == BACKUP, "latest progress backup mismatch", failures)
    current = progress.get("post100Reaudit", {}).get("currentRiskRank", {})
    require(current.get("focusedReviewed") == 680, "current focused reviewed mismatch", failures)
    require(current.get("focusedReviewedPercent") == "57.68%", "current focused percent mismatch", failures)
    require(current.get("remainingFocusedAfterLatestReview") == 499, "remaining focused mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        NOTE,
        NOTE_MIRROR,
        READINESS,
        PROGRESS,
        MAPPED,
        CAMPAIGN,
        RANK,
        FUNCTION_COVERAGE,
        FUNCTION_INDEX,
        BUILDING_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1174 note mirror mismatch", failures)
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:wave1174-building-namedmesh-current-risk-review")
        == r"py -3 tools\wave1174_building_namedmesh_current_risk_review.py --check",
        "missing package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_backup_progress(failures)
    check_docs(failures)

    if failures:
        print("Wave1174 Building / NamedMesh probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1174 Building / NamedMesh probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
