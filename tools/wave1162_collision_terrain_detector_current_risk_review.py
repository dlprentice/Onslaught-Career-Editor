#!/usr/bin/env python3
"""Validate Wave1162 collision/terrain detector current-risk review evidence."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1162-collision-terrain-detector-current-risk-review"
FOCUSED_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-focused-candidates.json"
RISK_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-risk-ranked-functions.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1162-collision-terrain-detector-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1162-collision-terrain-detector-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1162_collision_terrain_detector_current_risk_review_2026-06-06.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PROGRESS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260606-021413_post_wave1162_collision_terrain_detector_current_risk_review_verified"
EXPECTED_SOURCE_ROOT = str(Path.home() / "Ghidra" / "Projects")

TARGETS = {
    "0x00425a10": ("CCollisionSeekingInfantryBloke__CheckMountStateOrCollisionFlags", "bool __thiscall CCollisionSeekingInfantryBloke__CheckMountStateOrCollisionFlags(void * this, void * candidateRound)", ("infantry-bloke collision-seeking filter helper", "mount-state compatibility", "CCollisionSeekingRound__CheckCollisionFlags")),
    "0x00479020": ("CMeshCollisionVolume__IsDirectionInsideTrianglePrism", "int __cdecl CMeshCollisionVolume__IsDirectionInsideTrianglePrism(void * vertex0, void * vertex1, void * vertex2, void * vertex3, void * direction)", ("signed edge/plane dot tests", "CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore")),
    "0x0047ea20": ("CHeightField__GetHeightSamplePacked16", "uint __fastcall CHeightField__GetHeightSamplePacked16(void * this, uint x_packed, uint z_packed)", ("packed 16-bit height data", "+0x1028")),
    "0x0047ef20": ("CHeightField__RecomputeGridExtentsAndHeightRange", "void * __fastcall CHeightField__RecomputeGridExtentsAndHeightRange(void * this)", ("+0x10bc/+0x10c0", "height min/max sentinels")),
    "0x00490e20": ("CHeightField__FreeOwnedBuffers_Thunk", "void __fastcall CHeightField__FreeOwnedBuffers_Thunk(void * this)", ("CHeightField__FreeOwnedBuffers_24_1028",)),
    "0x004ac6e0": ("CMeshCollisionVolume__VFunc_03_004ac6e0", "int __thiscall CMeshCollisionVolume__VFunc_03_004ac6e0(void * this, void * query_arg0, float * motion_record, void * query_arg2, void * contact_record)", ("vtable slot 3", "up to six contact candidates")),
    "0x004ad830": ("CMeshCollisionVolume__VFunc_04_004ad830", "int __thiscall CMeshCollisionVolume__VFunc_04_004ad830(void * this, void * query_arg0, void * state_record, void * segment_offsets, void * contact_record)", ("vtable slot 4", "line-triangle bucket helpers")),
    "0x00480a30": ("CHLCollisionDetector__ScanNeighborSectorsAndDispatchCollisions", "void __thiscall CHLCollisionDetector__ScanNeighborSectorsAndDispatchCollisions(void * this, void * collision_component)", ("neighbor MapWho sectors", "dispatches collision pairs")),
    "0x00480c90": ("CHLCollisionDetector__HandleCollisionEnter", "void __thiscall CHLCollisionDetector__HandleCollisionEnter(void * this, void * candidate_component)", ("enter-event callback", "scheduled collision context")),
    "0x00480db0": ("CHLCollisionDetector__HandleCollisionExit", "void __thiscall CHLCollisionDetector__HandleCollisionExit(void * this, void * candidate_component)", ("exit-event callback", "mutual collision filters")),
    "0x00480e10": ("CHLCollisionDetector__TraverseQuadNodeAndDispatchCollisions", "void __thiscall CHLCollisionDetector__TraverseQuadNodeAndDispatchCollisions(void * this, void * mapwho_entry_or_quad_node)", ("recursively traverses four child pointers", "dispatches collision pairs")),
    "0x00480ed0": ("CHLCollisionDetector__DispatchCollisionEventForPair", "void __thiscall CHLCollisionDetector__DispatchCollisionEventForPair(void * this, void * candidate_component)", ("EVENT_MANAGER event 2000", "saved event pointer at +0xc")),
    "0x00481060": ("CHLCollisionDetector__ProcessMapWhoCollisionSweep", "void __thiscall CHLCollisionDetector__ProcessMapWhoCollisionSweep(void * this, void * previous_sector, void * current_sector)", ("map/who sweep", "dispatches candidate pair collisions")),
    "0x004812d0": ("CHLCollisionDetector__HandleScheduledCollisionEvent", "void __thiscall CHLCollisionDetector__HandleScheduledCollisionEvent(void * this, void * event)", ("event number 2000", "candidate collision component")),
}

COMMON_TAGS = {"static-reaudit", "retail-binary-evidence", "comment-hardened"}
DOCS = [
    NOTE,
    NOTE_MIRROR,
    READINESS,
    PROGRESS,
    PROGRESS_MIRROR,
    ROOT / "AGENTS.md",
    ROOT / "README.MD",
    ROOT / "CURRENT_CAPABILITIES.md",
    ROOT / "reverse-engineering" / "RE-INDEX.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "unit-battleengine-gameplay-static-contract.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "CollisionSeekingRound.cpp" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "MeshCollisionVolume.cpp" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "HeightField.cpp" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "HLCollisionDetector.cpp" / "_index.md",
    ROOT / "developer_agent_state.json",
    ROOT / "documentation_agent_state.json",
    ROOT / "re_orchestrator_state.json",
]
DOC_TOKENS = (
    "Wave1162",
    "wave1162-collision-terrain-detector-current-risk-review",
    "547/1179 = 46.40%",
    "14 collision/terrain detector current-risk rows",
    "current focused candidates: 1178",
    "live regenerated current focused candidates: 1178",
    "remaining active focused work: 632",
    "current risk candidates: 6166",
    "fresh Ghidra export",
    "read-only review",
    "no mutation",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "41 xref rows",
    "2104 instruction rows",
    "CCollisionSeekingInfantryBloke__CheckMountStateOrCollisionFlags",
    "CMeshCollisionVolume__IsDirectionInsideTrianglePrism",
    "CHeightField__GetHeightSamplePacked16",
    "CHLCollisionDetector__ScanNeighborSectorsAndDispatchCollisions",
    "CHLCollisionDetector__ProcessMapWhoCollisionSweep",
    "CHLCollisionDetector__HandleScheduledCollisionEvent",
    BACKUP,
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
)
OVERCLAIMS = (
    "runtime behavior proven",
    "runtime collision behavior proven",
    "runtime terrain behavior proven",
    "runtime projectile behavior proven",
    "exact layout proven",
    "source identity proven",
    "rebuild parity proven",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def normalize_address(address: str) -> str:
    value = (address or "").strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def signature_counts(rows: list[dict[str, str]]) -> tuple[int, int]:
    commented = sum(1 for row in rows if row.get("comment", "").strip())
    strict_clean = sum(
        1
        for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not re.search(r"\bparam_\d+\b", row.get("signature", ""))
    )
    return commented, strict_clean


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 14,
        "pre-tags.tsv": 14,
        "pre-xrefs.tsv": 41,
        "pre-instructions.tsv": 2104,
        "pre-decompile/index.tsv": 14,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-decompile" / "index.tsv")}
    xrefs = read_tsv(BASE / "pre-xrefs.tsv")

    for address, (name, signature, comment_tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            comment = row.get("comment", "")
            for token in comment_tokens:
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"tags missing at {address}: {COMMON_TAGS - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    ref_types = [row.get("ref_type") for row in xrefs]
    require(ref_types.count("UNCONDITIONAL_CALL") == 37, "UNCONDITIONAL_CALL xref count mismatch", failures)
    require(ref_types.count("DATA") == 4, "DATA xref count mismatch", failures)
    require(set(ref_types).issubset({"UNCONDITIONAL_CALL", "DATA"}), f"unexpected xref types: {set(ref_types)}", failures)


def check_logs_backup_queue(failures: list[str]) -> None:
    expected = {
        "pre-metadata.log": "targets=14 found=14 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=14 missing=0",
        "pre-xrefs.log": "Wrote 41 rows",
        "pre-instructions.log": "Wrote 2104 function-body instruction rows",
        "pre-decompile.log": "targets=14 dumped=14 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "SCRIPT ERROR", "BADADDR", "MISSING:", "BADNAME:", "BADSIG:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("sourceRoot") == EXPECTED_SOURCE_ROOT, "backup source root mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 175967111, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)

    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6411, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    require(len(rows) == 6411, "quality TSV row count mismatch", failures)
    require(commented == 6411, "quality TSV commented count mismatch", failures)
    require(strict_clean == 6411, "strict clean-signature count mismatch", failures)
    require(read_json(RISK_JSON).get("candidateFunctions") == 6166, "current risk candidate mismatch", failures)
    require(read_json(FOCUSED_JSON).get("candidateFunctions") == 1178, "focused candidate mismatch", failures)


def check_docs_progress(failures: list[str]) -> None:
    progress = read_json(PROGRESS)
    latest = progress.get("latestWave", {})
    current = progress.get("post100Reaudit", {}).get("currentRiskRank", {})
    require(latest.get("wave") == "Wave1162 collision/terrain detector current-risk review", "latest wave mismatch", failures)
    require(latest.get("tag") == "wave1162-collision-terrain-detector-current-risk-review", "latest tag mismatch", failures)
    require(latest.get("backup") == BACKUP, "latest backup mismatch", failures)
    require(current.get("focusedReviewed") == 547, "progress focused reviewed mismatch", failures)
    require(current.get("focusedReviewedPercent") == "46.40%", "progress focused percent mismatch", failures)
    require(current.get("remainingFocusedAfterLatestReview") == 632, "progress remaining mismatch", failures)
    require(current.get("liveFocusedCandidatesAfterLatestReview") == 1178, "progress live focused mismatch", failures)
    require(current.get("latestReviewWave") == "Wave1162 collision/terrain detector current-risk review", "progress latest review mismatch", failures)

    for path in DOCS:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1162 note mirror mismatch", failures)
    require(read_text(PROGRESS) == read_text(PROGRESS_MIRROR), "progress mirror mismatch", failures)
    require(
        read_json(PACKAGE_JSON).get("scripts", {}).get("test:wave1162-collision-terrain-detector-current-risk-review")
        == r"py -3 tools\wave1162_collision_terrain_detector_current_risk_review.py --check",
        "missing package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()
    failures: list[str] = []
    check_artifacts(failures)
    check_logs_backup_queue(failures)
    check_docs_progress(failures)
    if failures:
        print("Wave1162 collision/terrain detector current-risk probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1162 collision/terrain detector current-risk probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
