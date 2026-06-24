#!/usr/bin/env python3
"""Validate Wave1124 RepairPadAI current-risk review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

import wave1108_current_risk_rank
import wave1123_airunit_plane_support_vfunc_review as wave1123


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1124-repairpad-current-risk-review"
FOCUSED_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-focused-candidates.tsv"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1124-repairpad-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1124-repairpad-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1124_repairpad_current_risk_review_2026-06-05.md"
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
BUILDING_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Building.cpp" / "_index.md"
BUILDING_DOC_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "functions" / "Building.cpp" / "_index.md"

BACKUP = r"G:\GhidraBackups\BEA_20260605-050726_post_wave1124_repairpad_current_risk_review_verified"
PRIOR_BACKUP = r"G:\GhidraBackups\BEA_20260605-052636_post_wave1123_airunit_plane_support_vfunc_review_verified"

TARGETS = {
    "0x0040c5e0": (
        "CRepairPadAI__HasAnySlotBelowThreshold",
        "int __thiscall CRepairPadAI__HasAnySlotBelowThreshold(void * this)",
        ("leaf helper", "CRepairPadAI__IsCompatibleDockCandidate", "+0x52c", "runtime repair behavior"),
        ("0x004d6e15", "CRepairPadAI__IsCompatibleDockCandidate", "UNCONDITIONAL_CALL"),
        ("0x52c", "0x4b0", "pfVar1[0xc]", "return 1"),
    ),
    "0x004d6e00": (
        "CRepairPadAI__IsCompatibleDockCandidate",
        "int __thiscall CRepairPadAI__IsCompatibleDockCandidate(void * this, void * candidate_unit, int unused_ctx)",
        ("compatibility gate", "repair-bounds", "slot-threshold", "+0x138"),
        ("0x004d6d77", "CRepairPadAI__VFunc_11_UpdateDockCandidateReader", "UNCONDITIONAL_CALL"),
        ("CRepairPadAI__IsWithinRepairBounds", "CRepairPadAI__HasAnySlotBelowThreshold", "0x138", "return 1"),
    ),
}

DOC_TOKENS = (
    "Wave1124",
    "wave1124-repairpad-current-risk-review",
    "133/1179 = 11.28%",
    "2 rows",
    "current focused candidates: 1179",
    "score-23 RepairPadAI dock-candidate helper cluster",
    "fresh read-only Ghidra export",
    "no mutation",
    "0 / 0 / 0",
    "Wave328",
    "Wave924",
    "Wave1119",
    BACKUP,
    PRIOR_BACKUP,
)

OVERCLAIM_TOKENS = (
    "runtime repair-pad docking behavior proven",
    "runtime repair behavior proven",
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
    accounted = set(wave1123.prior_accounted_addresses())
    accounted.update(wave1123.TARGETS)
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
    require(len(accounted) == 131, f"prior accounted count mismatch: {len(accounted)}", failures)
    require(len(remaining) == 1048, f"remaining focused count mismatch: {len(remaining)}", failures)
    require(all(address in window for address in expected), "Wave1124 targets are not in the next score-23 Wave1108 focused window", failures)
    for row in remaining[:13]:
        require(row.get("score") == "23", f"Wave1108 score mismatch: {row.get('address')}", failures)


def check_exports(failures: list[str]) -> None:
    counts = {
        "pre-metadata.tsv": 2,
        "pre-tags.tsv": 2,
        "pre-xrefs.tsv": 2,
        "pre-instructions.tsv": 73,
        "pre-decompile/index.tsv": 2,
    }
    for relative, expected in counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)
    log_tokens = {
        "pre-metadata.log": "targets=2 found=2 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=2 missing=0",
        "pre-xrefs.log": "Wrote 2 rows",
        "pre-instructions.log": "targets=2 missing=0",
        "pre-decompile.log": "targets=2 dumped=2 missing=0 failed=0",
    }
    for relative, token in log_tokens.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR", "MISSING\t", "missing=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_target_rows(failures: list[str]) -> None:
    metadata = row_map(BASE / "pre-metadata.tsv")
    tags = row_map(BASE / "pre-tags.tsv")
    decompile = row_map(BASE / "pre-decompile" / "index.tsv")
    xrefs = read_tsv(BASE / "pre-xrefs.tsv")
    queue = row_map(QUEUE_TSV)

    for address, expected in TARGETS.items():
        name, signature, comment_tokens, xref, decompile_tokens = expected
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

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            require(tag_row.get("name") == name, f"tag name mismatch at {address}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)
            for token in ("comment-hardened", "repairpad-ai", "repairpad-wave328", "static-reaudit"):
                require(token in tag_row.get("tags", ""), f"missing tag token at {address}: {token}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row for {address}", failures)
        if dec is not None:
            require(dec.get("name") == name, f"decompile name mismatch at {address}", failures)
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)
            dec_text = read_text(BASE / "pre-decompile" / f"{address[2:]}_{name}.c")
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

    for path in (BUILDING_DOC, BUILDING_DOC_MIRROR):
        text = read_text(path)
        for token in ("Wave1124", "0x0040c5e0 CRepairPadAI__HasAnySlotBelowThreshold", "0x004d6e00 CRepairPadAI__IsCompatibleDockCandidate", BACKUP):
            require(contains_token(text, token), f"missing Building doc token in {path.relative_to(ROOT)}: {token}", failures)

    progress = read_json(PROGRESS)
    mirror = read_json(PROGRESS_MIRROR)
    commit_pattern = re.compile(r"^(pending Wave1124 artifact commit|[0-9a-f]{40})$")
    for label, data in (("progress", progress), ("progress mirror", mirror)):
        current = data["post100Reaudit"]["currentRiskRank"]
        require(data["latestWave"]["wave"] == "Wave1124 RepairPad current-risk review", f"{label} latest wave mismatch", failures)
        require(data["latestWave"]["tag"] == "wave1124-repairpad-current-risk-review", f"{label} latest tag mismatch", failures)
        require(data["latestWave"]["backup"] == BACKUP, f"{label} backup mismatch", failures)
        require(bool(commit_pattern.match(data["latestWave"].get("artifactCommit", ""))), f"{label} artifact commit mismatch", failures)
        require(current["focusedReviewed"] == 133, f"{label} focused reviewed mismatch", failures)
        require(current["focusedReviewedPercent"] == "11.28%", f"{label} focused percent mismatch", failures)
        require(current["latestReviewTag"] == "wave1124-repairpad-current-risk-review", f"{label} review tag mismatch", failures)

    package = read_json(PACKAGE_JSON)
    expected_script = r"py -3 tools\wave1124_repairpad_current_risk_review.py --check"
    require(package["scripts"].get("test:wave1124-repairpad-current-risk-review") == expected_script, "missing package script", failures)


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
        print("Wave1124 RepairPad current-risk review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1124 RepairPad current-risk review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
