#!/usr/bin/env python3
"""Validate Wave1161 collision-seeking/mesh-collision current-risk review evidence."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1161-collision-seeking-round-current-risk-review"
FOCUSED_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-focused-candidates.json"
RISK_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-risk-ranked-functions.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1161-collision-seeking-round-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1161-collision-seeking-round-current-risk-review.md"
CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "unit-battleengine-gameplay-static-contract.md"
CONTRACT_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "unit-battleengine-gameplay-static-contract.md"
READINESS = ROOT / "release" / "readiness" / "wave1161_collision_seeking_round_current_risk_review_2026-06-06.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PROGRESS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260606-014548_post_wave1161_collision_seeking_round_current_risk_review_verified"
EXPECTED_SOURCE_ROOT = str(Path.home() / "Ghidra" / "Projects")

TARGETS = {
    "0x00425b50": ("CCollisionSeekingRound__InitCollisionLineAndSound", "void __thiscall CCollisionSeekingRound__InitCollisionLineAndSound(void * this, void * roundConfig)", ("CLine-style helper", "InitWithSound")),
    "0x00425e30": ("CCollisionSeekingRound__UpdatePrimarySeekerLeadVector", "void * __fastcall CCollisionSeekingRound__UpdatePrimarySeekerLeadVector(void * this)", ("primary seeker", "lead vector")),
    "0x00426150": ("CCollisionSeekingRound__Init", "void __thiscall CCollisionSeekingRound__Init(void * this, void * roundConfig)", ("primary CLine-style seeker", "secondary CMeshCollisionVolume-style seeker")),
    "0x00426300": ("CMeshCollisionVolume__ScalarDeletingDestructor_00426300", "void * __thiscall CMeshCollisionVolume__ScalarDeletingDestructor_00426300(void * this, int deleteFlags)", ("scalar-deleting destructor", "CMeshCollisionVolume")),
    "0x00426340": ("CLine__ScalarDeletingDestructor_00426340", "void * __thiscall CLine__ScalarDeletingDestructor_00426340(void * this, int deleteFlags)", ("CLine-style collision helper", "BattleEngine helper lines")),
    "0x00426360": ("CLine__SetBaseVtable_00426360", "void __fastcall CLine__SetBaseVtable_00426360(void * this)", ("CLine-style helper vtable reset", "broader than CollisionSeekingRound")),
    "0x00426370": ("CCollisionSeekingRound__ReplacePrimarySeekerAndRefreshOffset", "void __thiscall CCollisionSeekingRound__ReplacePrimarySeekerAndRefreshOffset(void * this, void * newSeeker)", ("primary seeker pointer", "owner-relative offset")),
    "0x004264a0": ("CCollisionSeekingRound__ResolveRoundCollisionResponse", "void __thiscall CCollisionSeekingRound__ResolveRoundCollisionResponse(void * this, void * otherRound)", ("delayed-ready flag 0x400", "response callbacks")),
    "0x00426900": ("CCollisionSeekingRound__CheckCollisionFlags", "bool __thiscall CCollisionSeekingRound__CheckCollisionFlags(void * this, void * candidateRound)", ("candidate owner's thing flags", "collision mask")),
    "0x00426a00": ("CCollisionSeekingRound__ProcessMapWhoCollisionSweep", "void __thiscall CCollisionSeekingRound__ProcessMapWhoCollisionSweep(void * this, void * startOrContext, void * endOrContext)", ("CHLCollisionDetector__ProcessMapWhoCollisionSweep", "sweep arguments")),
    "0x00426a20": ("CCollisionSeekingRound__MarkDelayedCollisionReady", "void __thiscall CCollisionSeekingRound__MarkDelayedCollisionReady(void * this, void * event)", ("3000ms", "flag 0x400")),
    "0x004abe50": ("CMeshCollisionVolume__VFunc_02_004abe50", "int __thiscall CMeshCollisionVolume__VFunc_02_004abe50(void * this, void * query_arg0, void * query_arg1, void * source_sphere_record, void * contact_record)", ("vtable slot 2", "RET 0x10")),
    "0x004ac4a0": ("CMeshCollisionVolume__TestSweptSphereAgainstMeshPart", "int __stdcall CMeshCollisionVolume__TestSweptSphereAgainstMeshPart(void * part_context, void * mesh_part, float * sphere_start, float * sweep_delta, float * sphere_radius, void * contact_record)", ("mesh-part triangle bucket", "TestSweptSphereAgainstTriangleCore")),
    "0x004acf30": ("CMeshCollisionVolume__ResolveContactNormalAndPlane", "int __stdcall CMeshCollisionVolume__ResolveContactNormalAndPlane(float * contact_record, float hit_x, float hit_y, float hit_z, float hit_w, float normal_x, float normal_y, float normal_z, float normal_w, float unused_source_w, float * out_contact_point, float * out_contact_normal)", ("contact_record", "out_contact_point")),
    "0x004262e0": ("CMeshCollisionVolume__VFunc_05_004262e0", "int __thiscall CMeshCollisionVolume__VFunc_05_004262e0(void * this, void * query_arg0, void * query_arg1, void * delegate_object, void * query_arg3)", ("vtable slot 5", "RET 0x10")),
    "0x004d8a70": ("CCollisionSeekingRound__ShutdownMonitorAndDestruct", "void __fastcall CCollisionSeekingRound__ShutdownMonitorAndDestruct(void * this)", ("CMonitor__Shutdown", "Destructor")),
    "0x005d3980": ("CMeshCollisionVolume__SetPartBounds_Unwind", "void __cdecl CMeshCollisionVolume__SetPartBounds_Unwind(void)", ("MeshCollisionVolume.cpp", "0x0061c5ec")),
}

COMMON_TAGS = {"static-reaudit", "retail-binary-evidence", "comment-hardened"}
DOCS = [
    NOTE,
    NOTE_MIRROR,
    CONTRACT,
    CONTRACT_MIRROR,
    READINESS,
    PROGRESS,
    PROGRESS_MIRROR,
    ROOT / "README.md",
    ROOT / "CURRENT_CAPABILITIES.md",
    ROOT / "AGENTS.md",
    ROOT / "reverse-engineering" / "RE-INDEX.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "CollisionSeekingRound.cpp" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "MeshCollisionVolume.cpp" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Round.cpp" / "_index.md",
    ROOT / "developer_agent_state.json",
    ROOT / "documentation_agent_state.json",
    ROOT / "re_orchestrator_state.json",
]
DOC_TOKENS = (
    "Wave1161",
    "wave1161-collision-seeking-round-current-risk-review",
    "533/1179 = 45.21%",
    "17 collision-seeking/mesh-collision current-risk rows",
    "current focused candidates: 1178",
    "live regenerated current focused candidates: 1178",
    "remaining active focused work: 646",
    "current risk candidates: 6166",
    "fresh Ghidra export",
    "read-only review",
    "no mutation",
    "Codex read-only consults used",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "74 xref rows",
    "1567 instruction rows",
    "CCollisionSeekingRound__InitCollisionLineAndSound",
    "CCollisionSeekingRound__ResolveRoundCollisionResponse",
    "CCollisionSeekingRound__ProcessMapWhoCollisionSweep",
    "CMeshCollisionVolume__TestSweptSphereAgainstMeshPart",
    "CMeshCollisionVolume__ResolveContactNormalAndPlane",
    "CCollisionSeekingRound__ShutdownMonitorAndDestruct",
    BACKUP,
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
)
OVERCLAIMS = (
    "runtime behavior proven",
    "runtime collision behavior proven",
    "runtime projectile behavior proven",
    "rebuild parity proven",
    "exact layout proven",
    "source identity proven",
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
        "pre-metadata.tsv": 17,
        "pre-tags.tsv": 17,
        "pre-xrefs.tsv": 74,
        "pre-instructions.tsv": 1567,
        "pre-decompile/index.tsv": 17,
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

    actual_ref_types = {row.get("ref_type") for row in xrefs}
    require(
        actual_ref_types.issubset({"UNCONDITIONAL_CALL", "COMPUTED_CALL", "DATA"}),
        f"unexpected xref types: {actual_ref_types}",
        failures,
    )


def check_logs_backup_queue(failures: list[str]) -> None:
    expected = {
        "pre-metadata.log": "targets=17 found=17 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=17 missing=0",
        "pre-xrefs.log": "Wrote 74 rows",
        "pre-instructions.log": "Wrote 1567 function-body instruction rows",
        "pre-decompile.log": "targets=17 dumped=17 missing=0 failed=0",
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
    require(latest.get("wave") == "Wave1161 collision-seeking round current-risk review", "latest wave mismatch", failures)
    require(latest.get("tag") == "wave1161-collision-seeking-round-current-risk-review", "latest tag mismatch", failures)
    require(latest.get("backup") == BACKUP, "latest backup mismatch", failures)
    require(current.get("focusedReviewed") == 533, "progress focused reviewed mismatch", failures)
    require(current.get("focusedReviewedPercent") == "45.21%", "progress focused percent mismatch", failures)
    require(current.get("remainingFocusedAfterLatestReview") == 646, "progress remaining mismatch", failures)
    require(current.get("liveFocusedCandidatesAfterLatestReview") == 1178, "progress live focused mismatch", failures)
    require(current.get("latestReviewWave") == "Wave1161 collision-seeking round current-risk review", "progress latest review mismatch", failures)

    for path in DOCS:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1161 note mirror mismatch", failures)
    require(read_text(CONTRACT) == read_text(CONTRACT_MIRROR), "unit/BattleEngine contract mirror mismatch", failures)
    require(read_text(PROGRESS) == read_text(PROGRESS_MIRROR), "progress mirror mismatch", failures)
    require(
        read_json(PACKAGE_JSON).get("scripts", {}).get("test:wave1161-collision-seeking-round-current-risk-review")
        == r"py -3 tools\wave1161_collision_seeking_round_current_risk_review.py --check",
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
        print("Wave1161 collision-seeking round current-risk probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1161 collision-seeking round current-risk probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
