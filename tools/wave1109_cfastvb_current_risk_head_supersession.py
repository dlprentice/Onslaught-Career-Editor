#!/usr/bin/env python3
"""Validate Wave1109 CFastVB current-risk head supersession evidence."""

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
WAVE1053_NOTE = ROOT / "release" / "readiness" / "ghidra_cfastvb_stacklocked_transform_review_wave1053_2026-06-01.md"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1109-cfastvb-current-risk-head-supersession.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1109-cfastvb-current-risk-head-supersession.md"
READINESS = ROOT / "release" / "readiness" / "wave1109_cfastvb_current_risk_head_supersession_2026-06-04.md"
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

TOP15 = [
    ("0x005a0f50", "CFastVB__EvaluateCubicBasisVec3"),
    ("0x005a1002", "CFastVB__EvaluateCubicBasisVec2"),
    ("0x005a1087", "CFastVB__EvaluateCubicBasisVec4"),
    ("0x005a112c", "CFastVB__DispatchOp_CubicBlendVec3_005a112c"),
    ("0x005a11df", "CFastVB__DispatchOp_CubicBlendVec4_005a11df"),
    ("0x005a1279", "CFastVB__EvaluateCubicBasisDerivativeVec2"),
    ("0x005a13f7", "CFastVB__DispatchOp_InterpolateVec3ByReciprocal_005a13f7"),
    ("0x005a38c0", "CFastVB__DispatchOp_TransformVec4ArrayByMatrix4"),
    ("0x005a3980", "CFastVB__DispatchOp_TransformVec4ArrayByMatrix4_Alt_005a3980"),
    ("0x005a40c0", "CFastVB__DispatchOp_TransformVec3ArrayByMatrix4_WithTranslation_005a40c0"),
    ("0x005a4ecf", "CFastVB__DispatchOp_BlendQuaternionTriple_005a4ecf"),
    ("0x005a4f5c", "CFastVB__DispatchOp_BlendQuaternionControlPair_005a4f5c"),
    ("0x005a519e", "CFastVB__DispatchOp_BlendQuaternionSplineSegment_005a519e"),
    ("0x005a647f", "CFastVB__DispatchOp_ComposeTransformFromOptionalInputs_Core_005a647f"),
    ("0x005a7e09", "CFastVB__DispatchOp_ComposeMatrixFromOptionalTransforms"),
]

DOC_TOKENS = (
    "wave1109-cfastvb-current-risk-head-supersession",
    "15/1179 = 1.27%",
    "current focused candidates: 1179",
    "Wave1053",
    "cfastvb-stacklocked-transform-review-wave1053",
    "0x005a0f50 CFastVB__EvaluateCubicBasisVec3",
    "0x005a7e09 CFastVB__DispatchOp_ComposeMatrixFromOptionalTransforms",
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


def check_wave1108_head(failures: list[str]) -> None:
    wave1108_current_risk_rank.generate()
    focused = read_tsv(FOCUSED_TSV)
    require(len(focused) == 1179, "Wave1108 focused row count mismatch", failures)
    if len(focused) < len(TOP15):
        failures.append(f"Wave1108 focused TSV is shorter than expected head count: {len(focused)}")
        return
    for index, (address, name) in enumerate(TOP15):
        row = focused[index]
        require(normalize_address(row.get("address", "")) == address, f"Wave1108 top row address mismatch at {index}", failures)
        require(row.get("name") == name, f"Wave1108 top row name mismatch at {address}", failures)
        require(row.get("score") == "33", f"Wave1108 top row score mismatch at {address}", failures)


def check_wave1053_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "metadata.tsv": 24,
        "tags.tsv": 24,
        "xrefs.tsv": 34,
        "instructions.tsv": 4682,
        "decompile/index.tsv": 24,
        "context-metadata.tsv": 12,
        "context-tags.tsv": 12,
        "context-xrefs.tsv": 49,
        "context-instructions.tsv": 949,
        "context-decompile/index.tsv": 12,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(WAVE1053_BASE / relative)) == expected, f"Wave1053 {relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(WAVE1053_BASE / "metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(WAVE1053_BASE / "tags.tsv")}
    for address, name in TOP15:
        row = metadata.get(address)
        require(row is not None, f"missing Wave1053 metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"Wave1053 name mismatch at {address}", failures)
            require(row.get("status") == "OK", f"Wave1053 metadata status mismatch at {address}", failures)
            require("Static retail Ghidra" in row.get("comment", ""), f"missing static-boundary wording at {address}", failures)
        tag_row = tags.get(address)
        require(tag_row is not None, f"missing Wave1053 tags for {address}", failures)
        if tag_row is not None:
            require("static-reaudit" in tag_row.get("tags", ""), f"missing static-reaudit tag at {address}", failures)

    backup = read_json(WAVE1053_BASE / "backup-summary.json")
    require(backup.get("backupPath") == WAVE1053_BACKUP, "Wave1053 backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "Wave1053 backup file count mismatch", failures)
    require(backup.get("diffCount") == 0, "Wave1053 backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "Wave1053 backup hash diff count mismatch", failures)

    note = read_text(WAVE1053_NOTE)
    for token in ("Wave1053", "cfastvb-stacklocked-transform-review-wave1053", "no mutation", WAVE1053_BACKUP):
        require(contains_token(note, token), f"missing Wave1053 note token: {token}", failures)


def check_docs(failures: list[str]) -> None:
    docs = {
        "wave1109 note": read_text(NOTE),
        "wave1109 readiness": read_text(READINESS),
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

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "wave1109 note mirror mismatch", failures)
    progress = read_json(PROGRESS)
    current = progress.get("post100Reaudit", {}).get("currentRiskRank", {})
    require(current.get("focusedReviewed") == 15, "progress focusedReviewed mismatch", failures)
    require(current.get("focusedReviewedPercent") == "1.27%", "progress focusedReviewedPercent mismatch", failures)
    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:wave1109-cfastvb-current-risk-head-supersession")
        == r"py -3 tools\wave1109_cfastvb_current_risk_head_supersession.py --check",
        "missing package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_wave1108_head(failures)
    check_wave1053_artifacts(failures)
    check_docs(failures)

    if failures:
        print("Wave1109 CFastVB current-risk head supersession probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1109 CFastVB current-risk head supersession probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
