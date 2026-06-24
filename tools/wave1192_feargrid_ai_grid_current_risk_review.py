#!/usr/bin/env python3
"""Validate Wave1192 FearGrid/AI-grid current-risk artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1192-feargrid-ai-grid-current-risk-review"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1192-feargrid-ai-grid-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1192-feargrid-ai-grid-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1192_feargrid_ai_grid_current_risk_review_2026-06-06.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
RANK = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
FEARGRID_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FearGrid.cpp" / "_index.md"
UNITAI_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "UnitAI.cpp" / "_index.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
APPLY_SCRIPT = ROOT / "tools" / "ApplyFearGridAiGridCurrentRiskWave1192.java"

BACKUP = r"G:\GhidraBackups\BEA_20260606-183042_post_wave1192_feargrid_ai_grid_current_risk_review_verified"

TARGETS = {
    "0x0040dda0": (
        "CUnitAI__RefreshGridCooldownFromOccupiedCells",
        "void __thiscall CUnitAI__RefreshGridCooldownFromOccupiedCells(void * this)",
        ("DAT_008a9d7c", "DAT_008a9d80", "this+0x2e8"),
        "cooldown-refresh",
    ),
    "0x0044c3d0": (
        "CFearGrid__ctor_base",
        "void * __thiscall CFearGrid__ctor_base(void * this, int grid_id)",
        ("vtable 0x005db2a4", "this+0x8008", "RET 0x4"),
        "constructor",
    ),
    "0x0044c440": (
        "CFearGrid__RebuildOccupancyAndScheduleTick",
        "void __thiscall CFearGrid__RebuildOccupancyAndScheduleTick(void * this)",
        ("this+0x08", "this+0x4008", "event 1000"),
        "grid-refresh",
    ),
    "0x0044c720": (
        "CFearGrid__GetOccupancyAtWorldVector",
        "int __thiscall CFearGrid__GetOccupancyAtWorldVector(void * this, float vector_x, float vector_y, float vector_z, float vector_w)",
        ("16-byte world vector", "8-unit 64x64", "RET 0x10"),
        "occupancy",
    ),
    "0x0044c780": (
        "CFearGrid__ReadClearanceAtWorldVectorIfAboveTerrainDelta",
        "int __thiscall CFearGrid__ReadClearanceAtWorldVectorIfAboveTerrainDelta(void * this, float vector_x, float vector_y, float vector_z, float vector_w)",
        ("CStaticShadows__SampleShadowHeightBilinear", "0x005db2b0", "this+0x4008"),
        "clearance",
    ),
    "0x0044c810": (
        "CFearGrid__FindNearestFreeCellSpiral",
        "void __thiscall CFearGrid__FindNearestFreeCellSpiral(void * this, void * inout_world_vector)",
        ("spirals through the occupancy plane", "0x005d8c44", "RET 0x4"),
        "free-cell-search",
    ),
    "0x004daff0": (
        "FearGridTrackedObject__LookupFearWeightByArchetype",
        "double __thiscall FearGridTrackedObject__LookupFearWeightByArchetype(void * this)",
        ("DAT_008553f8", "entry+0x30", "_DAT_005d856c"),
        "context-row",
    ),
}

COMMON_TAGS = {
    "static-reaudit",
    "wave1192-feargrid-ai-grid-current-risk-review",
    "wave1192-readback-verified",
    "retail-binary-evidence",
    "current-risk-review",
    "fear-grid",
    "ai-grid",
    "source-identity-deferred",
    "exact-layout-deferred",
    "runtime-behavior-deferred",
    "rebuild-grade-static-contract",
    "no-noticeable-difference-boundary",
    "comment-hardened",
    "tag-normalized",
}

DOC_TOKENS = (
    "Wave1192",
    "wave1192-feargrid-ai-grid-current-risk-review",
    "832/1179 = 70.57%",
    "6 FearGrid/AI-grid current-risk rows",
    "context row FearGridTrackedObject__LookupFearWeightByArchetype",
    "current focused candidates: 1167",
    "live regenerated current focused candidates: 1167",
    "remaining active focused work: 347",
    "current risk candidates: 6166",
    "fresh Ghidra export",
    "comment/tag normalization",
    "updated=7 skipped=0",
    "comment_only_updated=7",
    "tags_added=93",
    "final dry updated=0 skipped=7",
    "no rename",
    "no signature change",
    "no function-boundary change",
    "no executable-byte change",
    "Codex read-only consults used",
    "no Cursor/Composer",
    "CUnitAI__RefreshGridCooldownFromOccupiedCells",
    "CFearGrid__ctor_base",
    "CFearGrid__RebuildOccupancyAndScheduleTick",
    "CFearGrid__GetOccupancyAtWorldVector",
    "CFearGrid__ReadClearanceAtWorldVectorIfAboveTerrainDelta",
    "CFearGrid__FindNearestFreeCellSpiral",
    "FearGridTrackedObject__LookupFearWeightByArchetype",
    "DAT_008a9d7c",
    "DAT_008a9d80",
    "DAT_008553f8",
    "event 1000",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "14 xref rows",
    "570 instruction rows",
    "7 decompile rows",
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
    "runtime fear-grid behavior proven",
    "runtime ai behavior proven",
    "runtime pathing behavior proven",
    "exact cfeargrid layout proven",
    "exact cunitai layout proven",
    "exact tracked-object layout proven",
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
        "metadata.tsv": 7,
        "tags.tsv": 7,
        "xrefs.tsv": 14,
        "instructions.tsv": 570,
        "decompile/index.tsv": 7,
        "post-metadata.tsv": 7,
        "post-tags.tsv": 7,
        "post-xrefs.tsv": 14,
        "post-instructions.tsv": 570,
        "post-decompile/index.tsv": 7,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs = read_tsv(BASE / "post-xrefs.tsv")

    for address, (name, signature, comment_tokens, specific_tag) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            comment = row.get("comment", "")
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in ("Wave1192 static current-risk", "Static rebuild", "clean-room/no-noticeable-difference parity remain separate proof"):
                require(token in comment, f"missing common comment token at {address}: {token}", failures)
            for token in comment_tokens:
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual), f"missing common tags at {address}: {COMMON_TAGS - actual}", failures)
            require(specific_tag in actual, f"missing specific tag at {address}: {specific_tag}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        rows = [row for row in xrefs if normalize_address(row.get("target_addr", "")) == address]
        require(rows, f"missing xrefs for {address}", failures)

    require(any(row.get("from_function") == "CHud__RenderObjectiveStatusPanel" for row in xrefs), "missing HUD objective xref", failures)
    require(any(row.get("from_function") == "CGame__InitRestartLoop" for row in xrefs), "missing CGame init xref", failures)
    require(any(row.get("from_function") == "CSquadNormal__Process" for row in xrefs), "missing CSquadNormal xref", failures)
    require(any(row.get("from_function") == "OID__CanFireAtTarget_BallisticArcA" for row in xrefs), "missing OID ballistic xref", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=7 tags_added=93 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=7 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=7 tags_added=93 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=7 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0",
        "post-metadata.log": "targets=7 found=7 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=7 missing=0",
        "post-xrefs.log": "Wrote 14 rows",
        "post-instructions.log": "Wrote 570 function-body instruction rows",
        "post-decompile.log": "targets=7 dumped=7 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIG:", "VERIFY_", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_progress_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6411, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    progress = read_json(PROGRESS)
    current = progress["post100Reaudit"]["currentRiskRank"]
    require(current["focusedReviewed"] == 832, "focused reviewed mismatch", failures)
    require(current["focusedReviewedPercent"] == "70.57%", "focused percent mismatch", failures)
    require(current["remainingFocusedAfterLatestReview"] == 347, "remaining focused mismatch", failures)
    require(current["liveFocusedCandidatesAfterLatestReview"] == 1167, "live focused mismatch", failures)
    require(current["broadRiskCandidates"] == 6166, "risk candidate mismatch", failures)
    require(progress["latestWave"]["artifactCommit"] in ("pending Wave1192 artifact commit",) or len(progress["latestWave"]["artifactCommit"]) == 40, "artifact commit field mismatch", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 176229255 or backup.get("totalBytes") == 176229255.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1192 note mirror mismatch", failures)
    docs = [
        NOTE,
        READINESS,
        PROGRESS,
        MAPPED,
        CAMPAIGN,
        RANK,
        FUNCTION_COVERAGE,
        FUNCTION_INDEX,
        BINARY_INDEX,
        RE_INDEX,
        FEARGRID_DOC,
        UNITAI_DOC,
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
        package.get("scripts", {}).get("test:wave1192-feargrid-ai-grid-current-risk-review")
        == r"py -3 tools\wave1192_feargrid_ai_grid_current_risk_review.py --check",
        "missing package script",
        failures,
    )
    require(APPLY_SCRIPT.is_file(), "missing Wave1192 apply script", failures)


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
        print("Wave1192 FearGrid/AI-grid current-risk probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1192 FearGrid/AI-grid current-risk probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
