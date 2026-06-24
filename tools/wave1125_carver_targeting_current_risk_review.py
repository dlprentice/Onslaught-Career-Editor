#!/usr/bin/env python3
"""Validate Wave1125 Carver targeting current-risk review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

import wave1108_current_risk_rank
import wave1124_repairpad_current_risk_review as wave1124


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1125-carver-targeting-current-risk-review"
FOCUSED_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-focused-candidates.tsv"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1125-carver-targeting-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1125-carver-targeting-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1125_carver_targeting_current_risk_review_2026-06-05.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
MAPPED_SYSTEMS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
CARVER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Carver.cpp.md"
CARVER_DOC_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "functions" / "Carver.cpp.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PROGRESS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"G:\GhidraBackups\BEA_20260605-053504_post_wave1125_carver_targeting_current_risk_review_verified"
PRIOR_BACKUP = r"G:\GhidraBackups\BEA_20260605-050726_post_wave1124_repairpad_current_risk_review_verified"

TARGETS = {
    "0x00422db0": (
        "CCarverAI__CheckNearbyEnemies",
        "void __fastcall CCarverAI__CheckNearbyEnemies(void * this)",
        ("map-who entries", "last-attack timestamp", "runtime AI behavior"),
        ("0x00422ba7", "CCarverAI__UpdateAttackAndReschedule", "UNCONDITIONAL_CALL"),
        ("CMapWho", "CMapWhoEntry__GetOwner", "CCarverAI__SetLastAttackTime"),
        (
            "static-reaudit",
            "wave1125-carver-targeting-current-risk-review",
            "wave1125-readback-verified",
            "retail-binary-evidence",
            "tag-normalized",
            "comment-hardened",
            "carver-targeting",
            "carver-ai",
            "nearby-enemy-scan",
            "mapwho-scan",
            "last-attack-timestamp",
        ),
    ),
    "0x00423510": (
        "CCarverGuide__AcquireNearestTargetReader",
        "void __fastcall CCarverGuide__AcquireNearestTargetReader(void * this)",
        ("active reader at +0x2c", "45.0-radius", "runtime targeting behavior"),
        ("0x004234ad", "CCarverGuide__HandleEvent", "UNCONDITIONAL_CALL"),
        ("CGenericActiveReader__SetReader", "CMapWho", "45.0"),
        (
            "static-reaudit",
            "wave1125-carver-targeting-current-risk-review",
            "wave1125-readback-verified",
            "retail-binary-evidence",
            "tag-normalized",
            "comment-hardened",
            "carver-targeting",
            "carver-guide",
            "active-reader",
            "nearest-target-reader",
            "mapwho-scan",
        ),
    ),
}

DOC_TOKENS = (
    "Wave1125",
    "wave1125-carver-targeting-current-risk-review",
    "135/1179 = 11.45%",
    "2 rows",
    "current focused candidates: 1179",
    "score-23 Carver targeting current-risk cluster",
    "fresh Ghidra export",
    "tag-only normalization",
    "22 tags",
    "0 / 0 / 0",
    "Wave915",
    "Wave965",
    "Wave989",
    BACKUP,
    PRIOR_BACKUP,
)

OVERCLAIM_TOKENS = (
    "runtime carver ai behavior proven",
    "runtime carverguide navigation behavior proven",
    "target acquisition correctness proven",
    "exact source-body identity proven",
    "concrete layout proven",
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


def prior_accounted_addresses() -> set[str]:
    accounted = set(wave1124.prior_accounted_addresses())
    accounted.update(wave1124.TARGETS)
    return accounted


def row_map(path: Path, key: str = "address") -> dict[str, dict[str, str]]:
    return {normalize_address(row.get(key, "")): row for row in read_tsv(path)}


def unescape_tsv(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def check_wave1108_head(failures: list[str]) -> None:
    wave1108_current_risk_rank.generate()
    rows = read_tsv(FOCUSED_TSV)
    accounted = prior_accounted_addresses()
    remaining = [row for row in rows if normalize_address(row.get("address", "")) not in accounted]
    expected = list(TARGETS)
    window = [normalize_address(row.get("address", "")) for row in remaining[:15]]

    require(len(rows) == 1179, "Wave1108 focused row count mismatch", failures)
    require(len(accounted) == 133, f"prior accounted count mismatch: {len(accounted)}", failures)
    require(len(remaining) == 1046, f"remaining focused count mismatch: {len(remaining)}", failures)
    require(all(address in window for address in expected), "Wave1125 targets are not in the next score-23 Wave1108 focused window", failures)
    for row in remaining[:11]:
        require(row.get("score") == "23", f"Wave1108 score mismatch: {row.get('address')}", failures)


def check_exports(failures: list[str]) -> None:
    counts = {
        "pre-metadata.tsv": 2,
        "pre-tags.tsv": 2,
        "pre-xrefs.tsv": 2,
        "pre-instructions.tsv": 190,
        "pre-decompile/index.tsv": 2,
        "post-metadata.tsv": 2,
        "post-tags.tsv": 2,
        "post-xrefs.tsv": 2,
        "post-instructions.tsv": 190,
        "post-decompile/index.tsv": 2,
    }
    for relative, expected in counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    log_tokens = {
        "pre-metadata.log": "targets=2 found=2 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=2 missing=0",
        "pre-xrefs.log": "Wrote 2 rows",
        "pre-instructions.log": "targets=2 missing=0",
        "pre-decompile.log": "targets=2 dumped=2 missing=0 failed=0",
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 tags_added=22 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=2 skipped=0 tags_added=22 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=2 tags_added=0 missing=0 bad=0",
        "post-metadata.log": "targets=2 found=2 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=2 missing=0",
        "post-xrefs.log": "Wrote 2 rows",
        "post-instructions.log": "targets=2 missing=0",
        "post-decompile.log": "targets=2 dumped=2 missing=0 failed=0",
    }
    for relative, token in log_tokens.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR", "BADNAME", "BADSIG", "VERIFY_MISSING_TAG", "missing=1", "failed=1", "bad=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_target_rows(failures: list[str]) -> None:
    metadata = row_map(BASE / "post-metadata.tsv")
    pre_tags = row_map(BASE / "pre-tags.tsv")
    post_tags = row_map(BASE / "post-tags.tsv")
    decompile = row_map(BASE / "post-decompile" / "index.tsv")
    xrefs = read_tsv(BASE / "post-xrefs.tsv")
    queue = row_map(QUEUE_TSV)

    for address, expected in TARGETS.items():
        name, signature, comment_tokens, xref, decompile_tokens, expected_tags = expected
        for label, rows in (("metadata", metadata), ("current queue", queue)):
            row = rows.get(address)
            require(row is not None, f"{label} missing: {address}", failures)
            if row is not None:
                comment = unescape_tsv(row.get("comment", ""))
                require(row.get("name") == name, f"{label} name mismatch at {address}", failures)
                require(row.get("signature") == signature, f"{label} signature mismatch at {address}", failures)
                require(row.get("status") == "OK", f"{label} status mismatch at {address}", failures)
                for token in comment_tokens:
                    require(token in comment, f"{label} missing comment token at {address}: {token}", failures)

        pre_tag_row = pre_tags.get(address)
        require(pre_tag_row is not None and not pre_tag_row.get("tags", ""), f"pre-tags were not empty at {address}", failures)

        post_tag_row = post_tags.get(address)
        require(post_tag_row is not None, f"missing post-tags for {address}", failures)
        if post_tag_row is not None:
            require(post_tag_row.get("name") == name, f"post-tag name mismatch at {address}", failures)
            require(post_tag_row.get("status") == "OK", f"post-tag status mismatch at {address}", failures)
            tag_text = post_tag_row.get("tags", "")
            for token in expected_tags:
                require(token in tag_text, f"missing post-tag token at {address}: {token}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row for {address}", failures)
        if dec is not None:
            require(dec.get("name") == name, f"decompile name mismatch at {address}", failures)
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)
            dec_text = read_text(BASE / "post-decompile" / f"{address[2:]}_{name}.c")
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
    require(int(backup.get("totalBytes")) == 175737735, "backup byte count mismatch", failures)
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
        CARVER_DOC,
        CARVER_DOC_MIRROR,
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

    progress = read_json(PROGRESS)
    mirror = read_json(PROGRESS_MIRROR)
    commit_pattern = re.compile(r"^(pending Wave1125 artifact commit|[0-9a-f]{40})$")
    for label, data in (("progress", progress), ("progress mirror", mirror)):
        current = data["post100Reaudit"]["currentRiskRank"]
        require(data["latestWave"]["wave"] == "Wave1125 Carver targeting current-risk review", f"{label} latest wave mismatch", failures)
        require(data["latestWave"]["tag"] == "wave1125-carver-targeting-current-risk-review", f"{label} latest tag mismatch", failures)
        require(data["latestWave"]["backup"] == BACKUP, f"{label} backup mismatch", failures)
        require(bool(commit_pattern.match(data["latestWave"].get("artifactCommit", ""))), f"{label} artifact commit mismatch", failures)
        require(current["focusedReviewed"] == 135, f"{label} focused reviewed mismatch", failures)
        require(current["focusedReviewedPercent"] == "11.45%", f"{label} focused percent mismatch", failures)
        require(current["latestReviewTag"] == "wave1125-carver-targeting-current-risk-review", f"{label} review tag mismatch", failures)

    package = read_json(PACKAGE_JSON)
    expected_script = r"py -3 tools\wave1125_carver_targeting_current_risk_review.py --check"
    require(package["scripts"].get("test:wave1125-carver-targeting-current-risk-review") == expected_script, "missing package script", failures)


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
        print("Wave1125 Carver targeting current-risk review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1125 Carver targeting current-risk review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
