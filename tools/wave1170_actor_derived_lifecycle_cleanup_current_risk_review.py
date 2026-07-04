#!/usr/bin/env python3
"""Validate Wave1170 actor-derived lifecycle cleanup read-only artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1170-actor-derived-lifecycle-cleanup-current-risk-review"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1170-actor-derived-lifecycle-cleanup-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1170-actor-derived-lifecycle-cleanup-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1170_actor_derived_lifecycle_cleanup_current_risk_review_2026-06-06.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
RANK = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
ROCKET_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Rocket.cpp" / "_index.md"
SPHERE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "SphereTrigger.cpp" / "_index.md"
ESCAPE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "EscapePod.cpp" / "_index.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260606-062008_post_wave1170_actor_derived_lifecycle_cleanup_current_risk_review_verified"

TARGETS = {
    "0x004bfd40": ("CRocket__scalar_deleting_dtor", "void * __thiscall CRocket__scalar_deleting_dtor(void * this, byte flags)", "0x005dd45c"),
    "0x004bfda0": ("CSphereTrigger__scalar_deleting_dtor", "void * __thiscall CSphereTrigger__scalar_deleting_dtor(void * this, byte flags)", "0x005dce68"),
    "0x004bfde0": ("CEscapePod__scalar_deleting_dtor", "void * __thiscall CEscapePod__scalar_deleting_dtor(void * this, byte flags)", "0x005dc834"),
    "0x004bfe10": ("CRocket__dtor_base", "void __fastcall CRocket__dtor_base(void * this)", "0x004bfd43"),
    "0x004bff40": ("CSphereTrigger__dtor_base", "void __fastcall CSphereTrigger__dtor_base(void * this)", "0x004bfda3"),
    "0x004c0000": ("CEscapePod__dtor_base", "void __fastcall CEscapePod__dtor_base(void * this)", "0x004bfde3"),
}

COMMENT_TOKENS = {
    "0x004bfd40": ("Wave459", "CRocket", "flags & 1", "RET 0x4"),
    "0x004bfda0": ("Wave459", "CSphereTrigger", "flags & 1", "RET 0x4"),
    "0x004bfde0": ("Wave459", "CEscapePod", "flags & 1", "RET 0x4"),
    "0x004bfe10": ("Wave460", "CParticleManager__RemoveFromGlobalList_Thunk", "CActor__dtor_base"),
    "0x004bff40": ("Wave460", "CSPtrSet", "CComplexThing__dtor_base"),
    "0x004c0000": ("Wave460", "CParticleManager__RemoveFromGlobalList", "CActor__dtor_base"),
}

DOC_TOKENS = (
    "Wave1170",
    "wave1170-actor-derived-lifecycle-cleanup-current-risk-review",
    "666/1179 = 56.49%",
    "6 actor-derived lifecycle cleanup current-risk rows",
    "current focused candidates: 1178",
    "live regenerated current focused candidates: 1178",
    "remaining active focused work: 513",
    "current risk candidates: 6166",
    "fresh Ghidra export",
    "read-only review",
    "no mutation",
    "Codex read-only consult used",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "6 xref rows",
    "100 instruction rows",
    "CRocket__scalar_deleting_dtor",
    "CSphereTrigger__scalar_deleting_dtor",
    "CEscapePod__scalar_deleting_dtor",
    "CRocket__dtor_base",
    "CSphereTrigger__dtor_base",
    "CEscapePod__dtor_base",
    "Wave459",
    "Wave460",
    "Wave1022",
    BACKUP,
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
)

OVERCLAIMS = (
    "runtime rocket cleanup behavior proven",
    "runtime sphere-trigger cleanup behavior proven",
    "runtime escape-pod cleanup behavior proven",
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
    value = address.strip().lower()
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
        "pre-metadata.tsv": 6,
        "pre-tags.tsv": 6,
        "pre-xrefs.tsv": 6,
        "pre-instructions.tsv": 100,
        "pre-decompile/index.tsv": 6,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    tags = {normalize(row["address"]): row for row in read_tsv(BASE / "pre-tags.tsv")}
    decompile = {normalize(row["address"]): row for row in read_tsv(BASE / "pre-decompile" / "index.tsv")}
    xrefs = {normalize(row["target_addr"]): row for row in read_tsv(BASE / "pre-xrefs.tsv")}

    for address, (name, signature, expected_xref) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata {address}", failures)
        if row:
            require(row.get("name") == name, f"name mismatch {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
            for token in COMMENT_TOKENS[address]:
                require(token in row.get("comment", ""), f"missing comment token {address}: {token}", failures)
        tag_row = tags.get(address)
        require(tag_row is not None and tag_row.get("status") == "OK" and "static-reaudit" in tag_row.get("tags", ""), f"tag mismatch {address}", failures)
        dec = decompile.get(address)
        require(dec is not None and dec.get("name") == name and dec.get("signature") == signature and dec.get("status") == "OK", f"decompile mismatch {address}", failures)
        xref = xrefs.get(address)
        require(xref is not None, f"missing xref {address}", failures)
        if xref:
            require(normalize(xref.get("from_addr", "")) == expected_xref, f"xref source mismatch {address}", failures)


def check_logs_backup_progress(failures: list[str]) -> None:
    expected_logs = {
        "pre-metadata.log": "targets=6 found=6 missing=0",
        "pre-tags.log": "rows=6 missing=0",
        "pre-xrefs.log": "Wrote 6 rows",
        "pre-instructions.log": "Wrote 100 function-body instruction rows",
        "pre-decompile.log": "targets=6 dumped=6 missing=0 failed=0",
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
    require(latest.get("wave") == "Wave1170 Actor-Derived Lifecycle Cleanup Current-Risk Review", "latest progress wave mismatch", failures)
    require(latest.get("tag") == "wave1170-actor-derived-lifecycle-cleanup-current-risk-review", "latest progress tag mismatch", failures)
    current = progress.get("post100Reaudit", {}).get("currentRiskRank", {})
    require(current.get("focusedReviewed") == 666, "current focused reviewed mismatch", failures)
    require(current.get("focusedReviewedPercent") == "56.49%", "current focused percent mismatch", failures)
    require(current.get("remainingFocusedAfterLatestReview") == 513, "remaining focused mismatch", failures)


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
        ROCKET_DOC,
        SPHERE_DOC,
        ESCAPE_DOC,
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

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1170 note mirror mismatch", failures)
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:wave1170-actor-derived-lifecycle-cleanup-current-risk-review")
        == r"py -3 tools\wave1170_actor_derived_lifecycle_cleanup_current_risk_review.py --check",
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
        print("Wave1170 actor-derived lifecycle cleanup probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1170 actor-derived lifecycle cleanup probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
