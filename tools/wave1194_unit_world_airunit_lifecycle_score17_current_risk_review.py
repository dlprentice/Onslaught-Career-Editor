#!/usr/bin/env python3
"""Validate Wave1194 unit/world/airunit lifecycle current-risk artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1194-unit-world-airunit-lifecycle-score17-current-risk-review"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1194-unit-world-airunit-lifecycle-score17-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1194-unit-world-airunit-lifecycle-score17-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1194_unit_world_airunit_lifecycle_score17_current_risk_review_2026-06-06.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
RANK = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
UNIT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Unit.cpp" / "_index.md"
WORLD_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "World.cpp" / "_index.md"
AIRUNIT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "AirUnit.cpp" / "_index.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
APPLY_SCRIPT = ROOT / "tools" / "ApplyUnitWorldAirunitLifecycleScore17Wave1194.java"

BACKUP = r"G:\GhidraBackups\BEA_20260606-193734_post_wave1194_unit_world_airunit_lifecycle_score17_current_risk_review_verified"

TARGETS = {
    "0x004dfa40": ("CUnit__VFunc08_InitAndAddToWorld", "void __thiscall CUnit__VFunc08_InitAndAddToWorld(void * this, void * init)", ("CUnit__Init", "CWorld__AddUnitToOccupancyGridAndRebuildShadows_Thunk")),
    "0x004dfd10": ("CUnit__VFunc18_SyncOldVectorAndClampHeight", "void __thiscall CUnit__VFunc18_SyncOldVectorAndClampHeight(void * this)", ("CActor__StickToGround", "0x006fbdfc")),
    "0x0050b010": ("CWorld__AddUnitToOccupancyGridAndRebuildShadows_Thunk", "void __stdcall CWorld__AddUnitToOccupancyGridAndRebuildShadows_Thunk(void * unit)", ("CWorld__AddUnitToOccupancyGridAndRebuildShadows", "static-shadow")),
    "0x0050b020": ("CWorld__RemoveUnitFromOccupancyGrid_Thunk", "void __stdcall CWorld__RemoveUnitFromOccupancyGrid_Thunk(void * unit)", ("CWorld__RemoveUnitFromOccupancyGrid", "cleanup/remove paths")),
    "0x0050f130": ("CGroundAttackAircraft__Destructor_VFunc01", "void __fastcall CGroundAttackAircraft__Destructor_VFunc01(void * this)", ("this+0x26c", "CUnit__dtor_base")),
    "0x0050f1f0": ("CDropship__Destructor_VFunc01", "void __fastcall CDropship__Destructor_VFunc01(void * this)", ("this+0x26c", "CUnit__dtor_base")),
    "0x0050f260": ("CPlane__Destructor_VFunc01", "void __fastcall CPlane__Destructor_VFunc01(void * this)", ("this+0x26c", "CUnit__dtor_base")),
    "0x0050f2d0": ("CDiveBomber__Destructor_VFunc01", "void __fastcall CDiveBomber__Destructor_VFunc01(void * this)", ("this+0x26c", "CUnit__dtor_base")),
    "0x0050f3b0": ("CFenrir__Destructor_VFunc01", "void __fastcall CFenrir__Destructor_VFunc01(void * this)", ("this+0x26c", "CUnit__dtor_base")),
}

COMMON_TAGS = {
    "static-reaudit",
    "wave1194-unit-world-airunit-lifecycle-score17-current-risk-review",
    "wave1194-readback-verified",
    "retail-binary-evidence",
    "current-risk-review",
    "score17",
    "unit-world-airunit-lifecycle",
    "source-identity-deferred",
    "exact-layout-deferred",
    "runtime-behavior-deferred",
    "rebuild-grade-static-contract",
    "no-noticeable-difference-boundary",
    "comment-hardened",
    "tag-normalized",
}

DOC_TOKENS = (
    "Wave1194",
    "wave1194-unit-world-airunit-lifecycle-score17-current-risk-review",
    "865/1179 = 73.37%",
    "9 unit/world/airunit lifecycle score17 current-risk rows",
    "current focused candidates: 1154",
    "live regenerated current focused candidates: 1154",
    "remaining active focused work: 314",
    "current risk candidates: 6166",
    "fresh Ghidra export",
    "comment/tag normalization",
    "updated=9 skipped=0",
    "comment_only_updated=9",
    "tags_added=132",
    "final dry updated=0 skipped=9",
    "no rename",
    "no signature change",
    "no function-boundary change",
    "no executable-byte change",
    "Codex read-only consult used",
    "no Cursor/Composer",
    "CUnit__VFunc08_InitAndAddToWorld",
    "CUnit__VFunc18_SyncOldVectorAndClampHeight",
    "CWorld__AddUnitToOccupancyGridAndRebuildShadows_Thunk",
    "CWorld__RemoveUnitFromOccupancyGrid_Thunk",
    "CGroundAttackAircraft__Destructor_VFunc01",
    "CDropship__Destructor_VFunc01",
    "CPlane__Destructor_VFunc01",
    "CDiveBomber__Destructor_VFunc01",
    "CFenrir__Destructor_VFunc01",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "26 xref rows",
    "177 instruction rows",
    "9 decompile rows",
    BACKUP,
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
    "rebuild-grade static contracts",
    "no noticeable difference",
    "rebuild-grade specification",
)

OVERCLAIMS = (
    "runtime behavior proven",
    "runtime cleanup behavior proven",
    "runtime occupancy behavior proven",
    "runtime aircraft teardown behavior proven",
    "exact layout proven",
    "exact source identity proven",
    "rebuild parity proven",
    "no-noticeable-difference parity proven",
)


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 9,
        "pre-tags.tsv": 9,
        "pre-xrefs.tsv": 26,
        "pre-instructions.tsv": 177,
        "pre-decompile/index.tsv": 9,
        "post-metadata.tsv": 9,
        "post-tags.tsv": 9,
        "post-xrefs.tsv": 26,
        "post-instructions.tsv": 177,
        "post-decompile/index.tsv": 9,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs = read_tsv(BASE / "post-xrefs.tsv")

    for address, (name, signature, comment_tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            comment = row.get("comment", "")
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in (
                "Wave1194 static current-risk read-back",
                "Static rebuild contract only",
                "clean-room/no-noticeable-difference parity remain separate proof",
            ):
                require(token in comment, f"missing common comment token at {address}: {token}", failures)
            for token in comment_tokens:
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual), f"missing common tags at {address}: {COMMON_TAGS - actual}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        rows = [row for row in xrefs if normalize_address(row.get("target_addr", "")) == address]
        require(rows, f"missing xrefs for {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=9 tags_added=132 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=9 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=9 tags_added=132 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=9 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0",
        "post-metadata.log": "targets=9 found=9 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=9 missing=0",
        "post-xrefs.log": "Wrote 26 rows",
        "post-instructions.log": "Wrote 177 function-body instruction rows",
        "post-decompile.log": "targets=9 dumped=9 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIG:", "VERIFY_", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)
    require("REPORT: Save succeeded" in read_text(BASE / "apply.log"), "apply save report missing", failures)


def check_progress_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6411, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    progress = read_json(PROGRESS)
    current = progress["post100Reaudit"]["currentRiskRank"]
    require(current["focusedReviewed"] == 865, "focused reviewed mismatch", failures)
    require(current["focusedReviewedPercent"] == "73.37%", "focused percent mismatch", failures)
    require(current["remainingFocusedAfterLatestReview"] == 314, "remaining focused mismatch", failures)
    require(current["liveFocusedCandidatesAfterLatestReview"] == 1154, "live focused mismatch", failures)
    require(current["broadRiskCandidates"] == 6166, "risk candidate mismatch", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 176327559 or backup.get("totalBytes") == 176327559.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1194 note mirror mismatch", failures)
    docs = [
        NOTE,
        READINESS,
        PROGRESS,
        MAPPED,
        CAMPAIGN,
        RANK,
        GHIDRA_REFERENCE,
        FUNCTION_COVERAGE,
        FUNCTION_INDEX,
        BINARY_INDEX,
        RE_INDEX,
        UNIT_DOC,
        WORLD_DOC,
        AIRUNIT_DOC,
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

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:wave1194-unit-world-airunit-lifecycle-score17-current-risk-review")
        == r"py -3 tools\wave1194_unit_world_airunit_lifecycle_score17_current_risk_review.py --check",
        "missing package script",
        failures,
    )
    require(APPLY_SCRIPT.is_file(), "missing Wave1194 apply script", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs(failures)
    check_progress_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave1194 unit/world/airunit lifecycle current-risk probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1194 unit/world/airunit lifecycle current-risk probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
