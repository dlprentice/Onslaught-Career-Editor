#!/usr/bin/env python3
"""Validate Wave1173 CFastVB strip-candidate read-only artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1173-cfastvb-strip-candidate-current-risk-review"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1173-cfastvb-strip-candidate-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1173-cfastvb-strip-candidate-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1173_cfastvb_strip_candidate_current_risk_review_2026-06-06.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
RANK = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
DXMESHVB_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXMeshVB.cpp" / "_index.md"
FASTVB_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FastVB.cpp" / "_index.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260606-073137_post_wave1173_cfastvb_strip_candidate_current_risk_review_verified"

TARGETS = {
    "0x0056ff40": (
        "CFastVB__TriangleListContainsVertexTriplet_0056ff40",
        "uint __stdcall CFastVB__TriangleListContainsVertexTriplet_0056ff40(void * triangle_list_span, void * triangle)",
        ("Wave651", "triangle-record", "three vertex ids"),
    ),
    "0x005708a0": (
        "CFastVB__InsertStripCandidatesIntoBuffer_005708a0",
        "void __thiscall CFastVB__InsertStripCandidatesIntoBuffer_005708a0(void * this, void * primary_candidate_span, void * secondary_candidate_span, void * edi_context)",
        ("Wave651", "secondary strip candidates", "primary candidates"),
    ),
    "0x00570be0": (
        "CFastVB__InitializeCandidateParentLinks_00570be0",
        "void __stdcall CFastVB__InitializeCandidateParentLinks_00570be0(void * out_candidate_span, void * selected_candidate_bucket)",
        ("Wave651", "parent field", "child triangle records"),
    ),
}

EXPECTED_XREFS = {
    "0x0056ff40": ("0x005705ac", "0x00570000", "CFastVB__BuildTriangleStripFromSeedRecord"),
    "0x005708a0": ("0x00570810", "0x00570000", "CFastVB__BuildTriangleStripFromSeedRecord"),
    "0x00570be0": ("0x00572cc9", "0x005725e0", "CFastVB__GenerateStripCandidatesFromAdjacency"),
}

DOC_TOKENS = (
    "Wave1173",
    "wave1173-cfastvb-strip-candidate-current-risk-review",
    "675/1179 = 57.25%",
    "3 CFastVB strip-candidate current-risk rows",
    "current focused candidates: 1178",
    "live regenerated current focused candidates: 1178",
    "remaining active focused work: 504",
    "current risk candidates: 6166",
    "fresh Ghidra export",
    "read-only review",
    "no mutation",
    "Codex read-only consult spawned",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "3 xref rows",
    "339 instruction rows",
    "CFastVB__TriangleListContainsVertexTriplet_0056ff40",
    "CFastVB__InsertStripCandidatesIntoBuffer_005708a0",
    "CFastVB__InitializeCandidateParentLinks_00570be0",
    BACKUP,
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
)

OVERCLAIMS = (
    "runtime strip quality proven",
    "concrete d3d index-buffer/render output proven",
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
        "pre-metadata.tsv": 3,
        "pre-tags.tsv": 3,
        "pre-xrefs.tsv": 3,
        "pre-instructions.tsv": 339,
        "pre-decompile/index.tsv": 3,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    tags = {normalize(row["address"]): row for row in read_tsv(BASE / "pre-tags.tsv")}
    decompile = {normalize(row["address"]): row for row in read_tsv(BASE / "pre-decompile" / "index.tsv")}
    xrefs = {normalize(row["target_addr"]): row for row in read_tsv(BASE / "pre-xrefs.tsv")}
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
        if tag_row:
            for token in ("static-reaudit", "retail-binary-evidence", "cfastvb-strip-selection-wave651"):
                require(token in tag_row.get("tags", ""), f"missing tag {address}: {token}", failures)
        dec = decompile.get(address)
        require(dec is not None and dec.get("name") == name and dec.get("signature") == signature and dec.get("status") == "OK", f"decompile mismatch {address}", failures)
        xref = xrefs.get(address)
        require(xref is not None, f"missing xref {address}", failures)
        if xref:
            from_addr, from_func, from_name = EXPECTED_XREFS[address]
            require(normalize(xref.get("from_addr", "")) == from_addr, f"xref from_addr mismatch {address}", failures)
            require(normalize(xref.get("from_function_addr", "")) == from_func, f"xref from function mismatch {address}", failures)
            require(xref.get("from_function") == from_name, f"xref from function name mismatch {address}", failures)
            require(xref.get("ref_type") == "UNCONDITIONAL_CALL", f"xref type mismatch {address}", failures)


def check_logs_backup_progress(failures: list[str]) -> None:
    expected_logs = {
        "pre-metadata.log": "targets=3 found=3 missing=0",
        "pre-tags.log": "rows=3 missing=0",
        "pre-xrefs.log": "Wrote 3 rows",
        "pre-instructions.log": "Wrote 339 function-body instruction rows",
        "pre-decompile.log": "targets=3 dumped=3 missing=0 failed=0",
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
    require(latest.get("wave") == "Wave1173 CFastVB Strip-Candidate Current-Risk Review", "latest progress wave mismatch", failures)
    require(latest.get("tag") == "wave1173-cfastvb-strip-candidate-current-risk-review", "latest progress tag mismatch", failures)
    require(latest.get("backup") == BACKUP, "latest progress backup mismatch", failures)
    current = progress.get("post100Reaudit", {}).get("currentRiskRank", {})
    require(current.get("focusedReviewed") == 675, "current focused reviewed mismatch", failures)
    require(current.get("focusedReviewedPercent") == "57.25%", "current focused percent mismatch", failures)
    require(current.get("remainingFocusedAfterLatestReview") == 504, "remaining focused mismatch", failures)


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
        DXMESHVB_DOC,
        FASTVB_DOC,
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

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1173 note mirror mismatch", failures)
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:wave1173-cfastvb-strip-candidate-current-risk-review")
        == r"py -3 tools\wave1173_cfastvb_strip_candidate_current_risk_review.py --check",
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
        print("Wave1173 CFastVB strip-candidate probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1173 CFastVB strip-candidate probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
