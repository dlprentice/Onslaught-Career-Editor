#!/usr/bin/env python3
"""Validate Wave1131 HeightField current-risk review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

import wave1108_current_risk_rank


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1131-heightfield-current-risk-review"
FOCUSED_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-focused-candidates.tsv"
QUALITY_LOG = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave1131.log"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1131-heightfield-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1131-heightfield-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1131_heightfield_current_risk_review_2026-06-05.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
MAPPED_SYSTEMS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
HEIGHTFIELD_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "HeightField.cpp" / "_index.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PROGRESS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"G:\GhidraBackups\BEA_20260605-090018_post_wave1131_heightfield_current_risk_review_verified"
PRIOR_BACKUP = r"G:\GhidraBackups\BEA_20260605-082438_post_wave1130_dive_dropship_current_risk_review_verified"

TARGETS = {
    "0x0047e870": (
        "CHeightField__ResetCoreBuffersAndFlags",
        "void * __fastcall CHeightField__ResetCoreBuffersAndFlags(void * this)",
        ("Wave426", "supersedes the older CUnitAI owner label", "+0x1028"),
        ("0x00490e13", "CHeightField__Constructor", "UNCONDITIONAL_CALL"),
        ("wave1131-heightfield-current-risk-review", "wave1131-readback-verified", "score-20-current-risk", "owned-buffer-state"),
    ),
    "0x0047e8a0": (
        "CHeightField__FreeOwnedBuffers_24_1028",
        "void __fastcall CHeightField__FreeOwnedBuffers_24_1028(void * this)",
        ("Wave426", "OID__FreeObject", "+0x1028"),
        ("0x00490e20", "CHeightField__FreeOwnedBuffers_Thunk", "UNCONDITIONAL_CALL"),
        ("wave1131-heightfield-current-risk-review", "wave1131-readback-verified", "score-20-current-risk", "owned-buffer-free"),
    ),
    "0x0047ef20": (
        "CHeightField__RecomputeGridExtentsAndHeightRange",
        "void * __fastcall CHeightField__RecomputeGridExtentsAndHeightRange(void * this)",
        ("Wave396", "CDXBattleLine", "+0x10bc", "+0x1034"),
        ("0x0053a602", "CDXBattleLine__BuildMesh", "UNCONDITIONAL_CALL"),
        ("wave1131-heightfield-current-risk-review", "wave1131-readback-verified", "score-22-current-risk", "battleline-caller"),
    ),
    "0x00490e20": (
        "CHeightField__FreeOwnedBuffers_Thunk",
        "void __fastcall CHeightField__FreeOwnedBuffers_Thunk(void * this)",
        ("Wave426", "global MAP destructor thunk", "tail-calls"),
        ("0x00490a35", "<no_function>", "UNCONDITIONAL_CALL"),
        ("wave1131-heightfield-current-risk-review", "wave1131-readback-verified", "score-21-current-risk", "destructor-thunk"),
    ),
    "0x00490f10": (
        "CHeightField__InitAndClearMapLoadFlags",
        "int __fastcall CHeightField__InitAndClearMapLoadFlags(void * this)",
        ("Wave426", "CGame::Init", "+0x93e0", "+0x93e4"),
        ("0x0046c38f", "CGame__Init", "UNCONDITIONAL_CALL"),
        ("wave1131-heightfield-current-risk-review", "wave1131-readback-verified", "score-20-current-risk", "map-load-flags"),
    ),
    "0x00490f40": (
        "CHeightField__ShutdownAndDestroyMixerMap",
        "void __fastcall CHeightField__ShutdownAndDestroyMixerMap(void * this)",
        ("Wave426", "CGame shutdown", "CMixerMap__Destroy"),
        ("0x0046ca0e", "CGame__Shutdown", "UNCONDITIONAL_CALL"),
        ("wave1131-heightfield-current-risk-review", "wave1131-readback-verified", "score-20-current-risk", "mixer-map"),
    ),
    "0x00490f50": (
        "CHeightField__TraceMapLoadRequestAndCheckLoadedFlags",
        "int __thiscall CHeightField__TraceMapLoadRequestAndCheckLoadedFlags(void * this, int map_number, int load_geometry, int load_properties)",
        ("Wave426", "Loading map %d", "+0x93e0", "+0x93e4"),
        ("0x0050bc29", "CWorld__LoadWorld", "UNCONDITIONAL_CALL"),
        ("wave1131-heightfield-current-risk-review", "wave1131-readback-verified", "score-20-current-risk", "world-load-caller"),
    ),
}

DOC_TOKENS = (
    "Wave1131",
    "wave1131-heightfield-current-risk-review",
    "168/1179 = 14.25%",
    "7 rows",
    "current focused candidates: 1178",
    "live regenerated current focused candidates: 1178",
    "remaining active focused work: 1011",
    "HeightField MAP current-risk cluster",
    "fresh Ghidra export",
    "tag-only normalization",
    "40 tags",
    "0 / 0 / 0",
    BACKUP,
    PRIOR_BACKUP,
)

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "runtime terrain behavior proven",
    "runtime map-load behavior proven",
    "rebuild parity proven",
)


def normalize_address(address: str) -> str:
    value = address.strip().lower()
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


def check_wave1108_accounting(failures: list[str]) -> None:
    counts = wave1108_current_risk_rank.generate()
    require(counts["total"] == 6410, "Wave1108 total mismatch", failures)
    require(counts["risk"] == 6165, "Wave1108 risk mismatch", failures)
    require(counts["focused"] == 1178, "Wave1108 focused mismatch", failures)
    focused = {normalize_address(row["address"]): row for row in read_tsv(FOCUSED_TSV)}
    for address in TARGETS:
        require(address in focused, f"target missing from current focused TSV: {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=40 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=7 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=40 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=7 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0",
        "post-metadata.log": "targets=7 found=7 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=7 missing=0",
        "post-xrefs.log": "Wrote 9 rows",
        "post-instructions.log": "Wrote 220 function-body instruction rows",
        "post-decompile.log": "targets=7 dumped=7 missing=0 failed=0",
        "context-metadata.log": "targets=7 found=7 missing=0",
        "context-tags.log": "ExportFunctionTagsByAddress complete: rows=7 missing=0",
        "context-xrefs.log": "Wrote 30 rows",
        "context-instructions.log": "Wrote 703 function-body instruction rows",
        "context-decompile.log": "targets=7 dumped=7 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIG:", "VERIFY_MISSING", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    quality = read_text(QUALITY_LOG)
    require("total_functions=6410 commented_functions=6410" in quality, "quality refresh mismatch", failures)


def check_exports(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 7,
        "pre-tags.tsv": 7,
        "pre-xrefs.tsv": 9,
        "pre-instructions.tsv": 220,
        "pre-decompile/index.tsv": 7,
        "context-metadata.tsv": 7,
        "context-tags.tsv": 7,
        "context-xrefs.tsv": 30,
        "context-instructions.tsv": 703,
        "context-decompile/index.tsv": 7,
        "post-metadata.tsv": 7,
        "post-tags.tsv": 7,
        "post-xrefs.tsv": 9,
        "post-instructions.tsv": 220,
        "post-decompile/index.tsv": 7,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    for stem in ("metadata", "xrefs", "instructions"):
        require(read_text(BASE / f"pre-{stem}.tsv") == read_text(BASE / f"post-{stem}.tsv"), f"pre/post {stem} drift", failures)


def check_target_rows(failures: list[str]) -> None:
    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs = read_tsv(BASE / "post-xrefs.tsv")

    for address, (name, signature, comment_tokens, xref, tag_tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch for {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch for {address}", failures)
            for token in comment_tokens:
                require(token.lower() in row.get("comment", "").lower(), f"missing comment token for {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual = set(tag_row.get("tags", "").split(";"))
            for token in tag_tokens + ("current-risk-review", "heightfield-current-risk-review"):
                require(token in actual, f"missing tag for {address}: {token}", failures)

        dec = decompile.get(address)
        require(dec is not None and dec.get("signature") == signature and dec.get("status") == "OK", f"decompile mismatch for {address}", failures)

        from_addr, from_function, ref_type = xref
        require(
            any(
                normalize_address(row.get("target_addr", "")) == address
                and normalize_address(row.get("from_addr", "")) == normalize_address(from_addr)
                and row.get("from_function") == from_function
                and row.get("ref_type") == ref_type
                for row in xrefs
            ),
            f"missing xref for {address}: {xref}",
            failures,
        )


def check_backup(failures: list[str]) -> None:
    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 175967111, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


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
        HEIGHTFIELD_DOC,
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
    commit_pattern = re.compile(r"^(pending Wave1131 artifact commit|[0-9a-f]{40})$")
    for label, data in (("progress", progress), ("progress mirror", mirror)):
        current = data["post100Reaudit"]["currentRiskRank"]
        require(data["latestWave"]["wave"] == "Wave1131 HeightField current-risk review", f"{label} latest wave mismatch", failures)
        require(data["latestWave"]["tag"] == "wave1131-heightfield-current-risk-review", f"{label} latest tag mismatch", failures)
        require(data["latestWave"]["backup"] == BACKUP, f"{label} backup mismatch", failures)
        require(bool(commit_pattern.match(data["latestWave"].get("artifactCommit", ""))), f"{label} artifact commit mismatch", failures)
        require(current["focusedReviewed"] == 168, f"{label} focused reviewed mismatch", failures)
        require(current["focusedCandidates"] == 1179, f"{label} focused denominator mismatch", failures)
        require(current["focusedReviewedPercent"] == "14.25%", f"{label} focused percent mismatch", failures)
        require(current["latestReviewTag"] == "wave1131-heightfield-current-risk-review", f"{label} review tag mismatch", failures)
        require(current.get("liveFocusedCandidatesAfterLatestReview") == 1178, f"{label} live focused count mismatch", failures)
        require(current.get("remainingFocusedAfterLatestReview") == 1011, f"{label} remaining focused count mismatch", failures)

    package = read_json(PACKAGE_JSON)
    expected_script = r"py -3 tools\wave1131_heightfield_current_risk_review.py --check"
    require(package["scripts"].get("test:wave1131-heightfield-current-risk-review") == expected_script, "missing package script", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_wave1108_accounting(failures)
    check_logs(failures)
    check_exports(failures)
    check_target_rows(failures)
    check_backup(failures)
    check_docs_and_state(failures)
    if failures:
        print("Wave1131 HeightField current-risk review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1131 HeightField current-risk review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
