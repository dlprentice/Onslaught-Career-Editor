#!/usr/bin/env python3
"""Validate Wave1110 CFastVB Wave1053 remainder supersession evidence."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import wave1108_current_risk_rank


ROOT = Path(__file__).resolve().parents[1]
WAVE1108_DIR = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank"
FOCUSED_TSV = WAVE1108_DIR / "wave1108-current-focused-candidates.tsv"
WAVE1053_BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1053-cfastvb-stacklocked-transform-review"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1110-cfastvb-wave1053-remainder-supersession.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1110-cfastvb-wave1053-remainder-supersession.md"
READINESS = ROOT / "release" / "readiness" / "wave1110_cfastvb_wave1053_remainder_supersession_2026-06-04.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
FASTVB_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FastVB.cpp" / "_index.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

WAVE1053_BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260601-162015_post_wave1053_cfastvb_stacklocked_transform_review_verified"
LATEST_BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified"

REMAINDER = [
    ("0x0059f857", "CFastVB__DispatchOp_TransformVec4Batch_0059f857"),
    ("0x0059fa5d", "CFastVB__DispatchOp_TransformVec4BatchW_0059fa5d"),
    ("0x0059fbeb", "CFastVB__DispatchOp_TransformProjectVec4Batch_0059fbeb"),
    ("0x0059fd51", "CFastVB__DispatchOp_TransformVec4Batch_NoOffset_0059fd51"),
    ("0x0059fe61", "CFastVB__DispatchOp_TransformVec4Batch_Perspective_0059fe61"),
    ("0x005a009f", "CFastVB__DispatchOp_TransformVec3WBatch_005a009f"),
    ("0x005a026f", "CFastVB__DispatchOp_TransformProjectVec3WBatch_005a026f"),
    ("0x005a04a0", "CFastVB__DispatchOp_WeightedMatrixBlendBatch_005a04a0"),
    ("0x005a7617", "CFastVB__DispatchOp_BuildRotationMatrixFromEulerAngles"),
]

DOC_TOKENS = (
    "wave1110-cfastvb-wave1053-remainder-supersession",
    "24/1179 = 2.04%",
    "9 rows",
    "current focused candidates: 1179",
    "Wave1053",
    "cfastvb-stacklocked-transform-review-wave1053",
    "0x0059f857 CFastVB__DispatchOp_TransformVec4Batch_0059f857",
    "0x005a7617 CFastVB__DispatchOp_BuildRotationMatrixFromEulerAngles",
    WAVE1053_BACKUP,
    LATEST_BACKUP,
    "no new Ghidra export",
    "no mutation",
)

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "runtime gameplay behavior proven",
    "rebuild parity proven",
    "exact layout proven",
    "hidden abi proven",
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


def normalize_address(address: str) -> str:
    value = address.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def check_wave1108_membership(failures: list[str]) -> None:
    wave1108_current_risk_rank.generate()
    focused = {normalize_address(row.get("address", "")): row for row in read_tsv(FOCUSED_TSV)}
    require(len(focused) == 1179, "Wave1108 focused row count mismatch", failures)
    for address, name in REMAINDER:
        row = focused.get(address)
        require(row is not None, f"Wave1108 focused row missing: {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"Wave1108 name mismatch at {address}", failures)


def check_wave1053_artifacts(failures: list[str]) -> None:
    metadata = {normalize_address(row["address"]): row for row in read_tsv(WAVE1053_BASE / "metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(WAVE1053_BASE / "tags.tsv")}
    xref_text = read_text(WAVE1053_BASE / "xrefs.tsv")
    for address, name in REMAINDER:
        row = metadata.get(address)
        require(row is not None, f"missing Wave1053 metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"Wave1053 name mismatch at {address}", failures)
            require(row.get("status") == "OK", f"Wave1053 status mismatch at {address}", failures)
            comment = row.get("comment", "")
            require("Static " in comment and "Ghidra" in comment and "evidence only" in comment, f"missing static-boundary wording at {address}", failures)
        tag_row = tags.get(address)
        require(tag_row is not None, f"missing Wave1053 tags for {address}", failures)
        if tag_row is not None:
            require("static-reaudit" in tag_row.get("tags", ""), f"missing static-reaudit tag at {address}", failures)
        require(address[2:] in xref_text.lower(), f"missing Wave1053 xref text for {address}", failures)

    backup = read_json(WAVE1053_BASE / "backup-summary.json")
    require(backup.get("backupPath") == WAVE1053_BACKUP, "Wave1053 backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "Wave1053 backup file count mismatch", failures)
    require(backup.get("diffCount") == 0, "Wave1053 backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "Wave1053 backup hash diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = {
        "wave1110 note": read_text(NOTE),
        "wave1110 readiness": read_text(READINESS),
        "mapped systems": read_text(MAPPED_SYSTEMS),
        "campaign": read_text(CAMPAIGN),
        "binary index": read_text(BINARY_INDEX),
        "RE index": read_text(RE_INDEX),
        "progress": read_text(PROGRESS),
        "FastVB index": read_text(FASTVB_INDEX),
        "developer state": read_text(DEVELOPER_STATE),
        "documentation state": read_text(DOCUMENTATION_STATE),
        "re state": read_text(RE_STATE),
    }
    for name, text in docs.items():
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {name}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lowered, f"overclaim token in {name}: {bad}", failures)

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "wave1110 note mirror mismatch", failures)
    current = read_json(PROGRESS).get("post100Reaudit", {}).get("currentRiskRank", {})
    require(current.get("focusedReviewed") == 24, "progress focusedReviewed mismatch", failures)
    require(current.get("focusedReviewedPercent") == "2.04%", "progress focusedReviewedPercent mismatch", failures)
    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:wave1110-cfastvb-wave1053-remainder-supersession")
        == r"py -3 tools\wave1110_cfastvb_wave1053_remainder_supersession.py --check",
        "missing package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_wave1108_membership(failures)
    check_wave1053_artifacts(failures)
    check_docs(failures)

    if failures:
        print("Wave1110 CFastVB Wave1053 remainder supersession probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1110 CFastVB Wave1053 remainder supersession probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
