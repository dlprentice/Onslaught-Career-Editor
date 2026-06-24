#!/usr/bin/env python3
"""Validate Wave1178 Carver current-risk consolidation artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1178-carver-current-risk-consolidation-review"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1178-carver-current-risk-consolidation-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1178-carver-current-risk-consolidation-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1178_carver_current_risk_consolidation_review_2026-06-06.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
RANK = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
CARVER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Carver.cpp.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"G:\GhidraBackups\BEA_20260606-095003_post_wave1178_carver_current_risk_consolidation_review_verified"

TARGETS = {
    "0x00422440": ("CCarver__Init", "void __thiscall CCarver__Init(void * this, void * init)"),
    "0x00422580": ("CCarverAI__dtor_base", "void __fastcall CCarverAI__dtor_base(void * this)"),
    "0x00422620": ("CCarver__UpdateMotionAndWingPose", "void __fastcall CCarver__UpdateMotionAndWingPose(void * this)"),
    "0x00422760": ("CCarverAI__OpenWings", "void __fastcall CCarverAI__OpenWings(void * this)"),
    "0x004227a0": ("CCarverAI__CloseWings", "void __fastcall CCarverAI__CloseWings(void * this)"),
    "0x004227e0": ("CCarverAI__OnHit", "void __thiscall CCarverAI__OnHit(void * this, void * otherThing, void * collisionReport)"),
    "0x00422820": ("CCarverAI__Fire", "int __fastcall CCarverAI__Fire(void * this)"),
    "0x00422930": ("CCarverAI__SetLastAttackTime", "void __fastcall CCarverAI__SetLastAttackTime(void * this)"),
    "0x00422940": ("CCarverAI__IsRecentlyAttacked", "int __fastcall CCarverAI__IsRecentlyAttacked(void * this)"),
    "0x00422970": ("CCarverAI__CanStartAttack", "int __fastcall CCarverAI__CanStartAttack(void * this)"),
    "0x004229b0": ("CarverAimGlobals__ResetVector", "void __cdecl CarverAimGlobals__ResetVector(void)"),
    "0x004229d0": ("CarverAimGlobals__InitMatrix", "void __cdecl CarverAimGlobals__InitMatrix(void)"),
    "0x00422aa0": ("CCarverAI__RefreshTargetReaderAndScheduleMove", "void __thiscall CCarverAI__RefreshTargetReaderAndScheduleMove(void * this, void * event)"),
    "0x00422b90": ("CCarverAI__UpdateAttackAndReschedule", "void __thiscall CCarverAI__UpdateAttackAndReschedule(void * this, void * event)"),
    "0x00422db0": ("CCarverAI__CheckNearbyEnemies", "void __fastcall CCarverAI__CheckNearbyEnemies(void * this)"),
    "0x00422f90": ("CCarverGuide__ctor", "void * __thiscall CCarverGuide__ctor(void * this, void * guideTarget)"),
    "0x00422fd0": ("CCarverGuide__dtor_base", "void __fastcall CCarverGuide__dtor_base(void * this)"),
    "0x00423490": ("CCarverGuide__HandleEvent", "void __thiscall CCarverGuide__HandleEvent(void * this, void * event)"),
    "0x00423510": ("CCarverGuide__AcquireNearestTargetReader", "void __fastcall CCarverGuide__AcquireNearestTargetReader(void * this)"),
    "0x0050f340": ("CCarver__Destructor_VFunc01", "void __fastcall CCarver__Destructor_VFunc01(void * this)"),
}

COMMON_TAGS = {
    "static-reaudit",
    "wave1178-carver-current-risk-consolidation-review",
    "wave1178-readback-verified",
    "retail-binary-evidence",
    "current-risk-review",
    "carver-current-risk",
    "tag-normalized",
    "comment-hardened",
}

DOC_TOKENS = (
    "Wave1178",
    "wave1178-carver-current-risk-consolidation-review",
    "715/1179 = 60.64%",
    "20 Carver current-risk rows",
    "current focused candidates: 1178",
    "live regenerated current focused candidates: 1178",
    "remaining active focused work: 464",
    "current risk candidates: 6166",
    "fresh Ghidra export",
    "tag-only normalization",
    "updated=20 skipped=0",
    "tags_added=206",
    "no rename",
    "no signature change",
    "no comment change",
    "no function-boundary change",
    "no executable-byte change",
    "Codex read-only consult used",
    "Codex root final judgment",
    "consult narrowed to 11 rows",
    "root widened to 20-row coherent Carver slice",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "23 xref rows",
    "873 instruction rows",
    "CCarver__Init",
    "CCarverAI__dtor_base",
    "CCarver__UpdateMotionAndWingPose",
    "CCarverAI__OpenWings",
    "CCarverAI__CloseWings",
    "CCarverAI__Fire",
    "CCarverAI__CheckNearbyEnemies",
    "CCarverGuide__AcquireNearestTargetReader",
    "CCarver__Destructor_VFunc01",
    BACKUP,
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
)

OVERCLAIMS = (
    "runtime carver behavior proven",
    "runtime wing timing proven",
    "runtime attack/target selection behavior proven",
    "runtime guide/navigation behavior proven",
    "exact ccarver layout proven",
    "exact ccarverai layout proven",
    "exact ccarverguide layout proven",
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
        "pre-metadata.tsv": 20,
        "pre-tags.tsv": 20,
        "pre-xrefs.tsv": 23,
        "pre-instructions.tsv": 873,
        "pre-decompile/index.tsv": 20,
        "post-metadata.tsv": 20,
        "post-tags.tsv": 20,
        "post-xrefs.tsv": 23,
        "post-instructions.tsv": 873,
        "post-decompile/index.tsv": 20,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    for address, (name, signature) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
            require("remain unproven" in row.get("comment", ""), f"missing bounded comment token {address}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"missing Wave1178 tags {address}: {COMMON_TAGS - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row {address}", failures)
        if dec is not None:
            require(dec.get("name") == name, f"decompile name mismatch {address}", failures)
            require(dec.get("signature") == signature, f"decompile signature mismatch {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch {address}", failures)


def check_logs_backup_progress(failures: list[str]) -> None:
    expected_logs = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=206 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=20 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=206 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=20 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0",
        "post-metadata.log": "targets=20 found=20 missing=0",
        "post-tags.log": "rows=20 missing=0",
        "post-xrefs.log": "Wrote 23 rows",
        "post-instructions.log": "Wrote 873 function-body instruction rows",
        "post-decompile.log": "targets=20 dumped=20 missing=0 failed=0",
    }
    for relative, token in expected_logs.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIG:", "VERIFY_MISSING", "FAIL:", "missing=1", "bad=1", "failed=1"):
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
    require(latest.get("wave") == "Wave1178 Carver Current-Risk Consolidation Review", "latest progress wave mismatch", failures)
    require(latest.get("tag") == "wave1178-carver-current-risk-consolidation-review", "latest progress tag mismatch", failures)
    require(latest.get("backup") == BACKUP, "latest progress backup mismatch", failures)
    current = progress.get("post100Reaudit", {}).get("currentRiskRank", {})
    require(current.get("focusedReviewed") == 715, "current focused reviewed mismatch", failures)
    require(current.get("focusedReviewedPercent") == "60.64%", "current focused percent mismatch", failures)
    require(current.get("remainingFocusedAfterLatestReview") == 464, "remaining focused mismatch", failures)


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
        CARVER_DOC,
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

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1178 note mirror mismatch", failures)
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:wave1178-carver-current-risk-consolidation-review")
        == r"py -3 tools\wave1178_carver_current_risk_consolidation_review.py --check",
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
        print("Wave1178 Carver current-risk probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1178 Carver current-risk probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
