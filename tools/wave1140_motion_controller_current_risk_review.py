#!/usr/bin/env python3
"""Validate Wave1140 motion-controller current-risk review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1140-motion-controller-current-risk-review"
FOCUSED_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-focused-candidates.json"
RISK_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-risk-ranked-functions.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1140-motion-controller-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1140-motion-controller-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1140_motion_controller_current_risk_review_2026-06-05.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
MAPPED_SYSTEMS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
UNIT_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "unit-battleengine-gameplay-static-contract.md"
HIVEBOSS_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "HiveBoss.cpp" / "_index.md"
MINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Mine.cpp" / "_index.md"
SENTINEL_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Sentinel.cpp" / "_index.md"
MECH_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Mech.cpp" / "_index.md"
GROUNDUNIT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "GroundUnit.cpp" / "_index.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PROGRESS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260605-142515_post_wave1140_motion_controller_current_risk_review_verified"
PRIOR_BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260605-134608_post_wave1139_battleengine_jetpart_current_risk_review_verified"

TARGETS = {
    "0x00497090": (
        "CMCHiveBoss__Constructor",
        "void * __thiscall CMCHiveBoss__Constructor(void * this, void * owner_hiveboss)",
        ("Wave432 lifecycle correction", "owner_hiveboss+0x178", "vtable 0x005dc388"),
    ),
    "0x00497140": (
        "CDestructableSegmentsMotionController__CacheNamedCollisionCylinders",
        "void __thiscall CDestructableSegmentsMotionController__CacheNamedCollisionCylinders(void * this, void * mesh_model)",
        ("Wave942 comment normalization", "0x004976f1", "N/S/E/W mid/top/bot"),
    ),
    "0x00494fa0": (
        "SharedMotionController__VFunc_UpdateUnitAIIndexedEntryFlag",
        "void __thiscall SharedMotionController__VFunc_UpdateUnitAIIndexedEntryFlag(void * this, void * stateContext, int * outFlags)",
        ("CMCBuggy slot 17", "CMCHiveBoss slot 6", "CUnitAI__CanUseIndexedSegmentEntry"),
    ),
    "0x00494ff0": (
        "SharedMotionController__VFunc_CallUnitAIIndexedEntryVFunc10",
        "int __thiscall SharedMotionController__VFunc_CallUnitAIIndexedEntryVFunc10(void * this, void * stateContext)",
        ("CMCBuggy slot 18", "CMCHiveBoss slot 7", "CUnitAI__CallIndexedEntryVFunc10"),
    ),
    "0x0049c1d0": (
        "CMCMech__VFunc_05_WriteInterpolatedBoneFloat_0049c1d0",
        "void __thiscall CMCMech__VFunc_05_WriteInterpolatedBoneFloat_0049c1d0(void * this, void * mesh_part, void * out_value)",
        ("Wave433 vtable-slot correction", "CMCMech__Reset", "DAT_008a9e44"),
    ),
    "0x0049c3e0": (
        "CMCMine__Constructor",
        "void * __thiscall CMCMine__Constructor(void * this, void * owner_mine)",
        ("Wave434 lifecycle correction", "vtable 0x005dc3f4", "owner pointer at +0x08"),
    ),
    "0x0049c440": (
        "CMCMine__VFunc_04_UpdateInterpolatedHeightOffset_0049c440",
        "void __thiscall CMCMine__VFunc_04_UpdateInterpolatedHeightOffset_0049c440(void * this, void * mesh_part, void * transform_a, void * transform_b, int context_value)",
        ("CMCMine vtable 0x005dc3f4 slot 4", "owner +0x250/+0x254", "cached +0x0c"),
    ),
    "0x0049c5d0": (
        "CMCSentinel__Constructor",
        "void * __thiscall CMCSentinel__Constructor(void * this, void * owner_sentinel)",
        ("Wave434 lifecycle correction", "vtable 0x005dc420", "0xc479c000"),
    ),
    "0x0049f820": (
        "SharedGroundUnit__VFunc_09_InitGroundedMotionComponents_0049f820",
        "void __thiscall SharedGroundUnit__VFunc_09_InitGroundedMotionComponents_0049f820(void * this, void * init_context)",
        ("Wave436 shared slot-9 correction", "CGroundUnit__Init", "CDestroyableSegment__FindChildByNameI"),
    ),
}

EXPECTED_XREFS = {
    "0x00497090": ("0x0047fed8", "CHiveBoss__Init", "UNCONDITIONAL_CALL"),
    "0x00497140": ("0x004976f1", "CMCHiveBoss__VFunc_04_UpdateCylinderTransforms_004976d0", "UNCONDITIONAL_CALL"),
    "0x00494fa0": ("0x005dc294", "<no_function>", "DATA"),
    "0x00494ff0": ("0x005dc298", "<no_function>", "DATA"),
    "0x0049c1d0": ("0x005dc3c8", "<no_function>", "DATA"),
    "0x0049c3e0": ("0x004ba3d0", "CMine__Init", "UNCONDITIONAL_CALL"),
    "0x0049c440": ("0x005dc404", "<no_function>", "DATA"),
    "0x0049c5d0": ("0x004deafd", "CSentinel__Init", "UNCONDITIONAL_CALL"),
    "0x0049f820": ("0x004799fa", "CGillM__VFunc09_InitGroundedSpawnState", "UNCONDITIONAL_CALL"),
}

DOC_TOKENS = (
    "Wave1140",
    "wave1140-motion-controller-current-risk-review",
    "238/1179 = 20.19%",
    "9 current-risk rows",
    "current focused candidates: 1178",
    "live regenerated current focused candidates: 1178",
    "remaining active focused work: 941",
    "current risk candidates: 6166",
    "motion-controller residual current-risk cluster",
    "fresh Ghidra export",
    "read-only review",
    "no mutation",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    BACKUP,
    PRIOR_BACKUP,
)

OVERCLAIM_TOKENS = (
    "runtime motion-controller behavior proven",
    "runtime hiveboss motion behavior proven",
    "runtime mine motion behavior proven",
    "runtime sentinel motion behavior proven",
    "runtime grounded-unit behavior proven",
    "rebuild parity proven",
)


def normalize_address(address: str) -> str:
    value = (address or "").strip().lower()
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


def signature_counts(rows: list[dict[str, str]]) -> tuple[int, int]:
    commented = sum(1 for row in rows if row.get("comment", "").strip())
    strict_clean = sum(
        1
        for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not re.search(r"\bparam_\d+\b", row.get("signature", ""))
    )
    return commented, strict_clean


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 9,
        "pre-tags.tsv": 9,
        "pre-xrefs.tsv": 19,
        "pre-instructions.tsv": 823,
        "pre-decompile/index.tsv": 9,
        "context-metadata.tsv": 15,
        "context-tags.tsv": 15,
        "context-xrefs.tsv": 26,
        "context-instructions.tsv": 1388,
        "context-decompile/index.tsv": 15,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-decompile" / "index.tsv")}
    xrefs = read_tsv(BASE / "pre-xrefs.tsv")

    for address, (name, signature, comment_tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in comment_tokens:
                require(token in row.get("comment", ""), f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require("static-reaudit" in actual_tags, f"missing static-reaudit tag at {address}", failures)
            require("retail-binary-evidence" in actual_tags, f"missing retail-binary-evidence tag at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        from_addr, from_function, ref_type = EXPECTED_XREFS[address]
        require(
            any(
                normalize_address(row.get("target_addr", "")) == address
                and normalize_address(row.get("from_addr", "")) == from_addr
                and row.get("from_function") == from_function
                and row.get("ref_type") == ref_type
                for row in xrefs
            ),
            f"missing expected xref for {address}",
            failures,
        )

    context = {normalize_address(row["address"]): row for row in read_tsv(BASE / "context-metadata.tsv")}
    for address in (
        "0x00493020",
        "0x00496540",
        "0x004976d0",
        "0x0049cad0",
        "0x0049ef80",
        "0x0049fc10",
        "0x0049fdb0",
    ):
        require(address in context, f"missing context metadata row {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "pre-metadata.log": "targets=9 found=9 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=9 missing=0",
        "pre-xrefs.log": "Wrote 19 rows",
        "pre-instructions.log": "Wrote 823 function-body instruction rows",
        "pre-decompile.log": "targets=9 dumped=9 missing=0 failed=0",
        "context-metadata.log": "targets=15 found=15 missing=0",
        "context-tags.log": "ExportFunctionTagsByAddress complete: rows=15 missing=0",
        "context-xrefs.log": "Wrote 26 rows",
        "context-instructions.log": "Wrote 1388 function-body instruction rows",
        "context-decompile.log": "targets=15 dumped=15 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "SCRIPT ERROR", "BADADDR", "MISSING:", "BADNAME:", "BADSIG:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_progress_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6411, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    require(len(rows) == 6411, "quality TSV row count mismatch", failures)
    require(commented == 6411, "quality TSV commented count mismatch", failures)
    require(strict_clean == 6411, "strict clean-signature count mismatch", failures)

    risk = read_json(RISK_JSON)
    focused = read_json(FOCUSED_JSON)
    require(risk.get("totalFunctions") == 6411, "current risk total mismatch", failures)
    require(risk.get("candidateFunctions") == 6166, "current risk candidate mismatch", failures)
    require(focused.get("candidateFunctions") == 1178, "focused candidate mismatch", failures)

    progress = read_json(PROGRESS)
    current = progress["post100Reaudit"]["currentRiskRank"]
    require(progress["functionQuality"]["totalFunctions"] == 6411, "progress function total mismatch", failures)
    require(progress["functionQuality"]["strictCleanSignatureProxy"] == "6411/6411 = 100.00%", "progress strict proxy mismatch", failures)
    require(current["focusedReviewed"] == 238, "progress focused reviewed mismatch", failures)
    require(current["focusedReviewedPercent"] == "20.19%", "progress focused percent mismatch", failures)
    require(current["remainingFocusedAfterLatestReview"] == 941, "progress remaining mismatch", failures)
    require(current["broadRiskCandidates"] == 6166, "progress broad candidates mismatch", failures)
    require(current["liveFocusedCandidatesAfterLatestReview"] == 1178, "progress live focused mismatch", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 175967111, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
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
        UNIT_CONTRACT,
        HIVEBOSS_DOC,
        MINE_DOC,
        SENTINEL_DOC,
        MECH_DOC,
        GROUNDUNIT_DOC,
        PROGRESS,
        PROGRESS_MIRROR,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:wave1140-motion-controller-current-risk-review") == r"py -3 tools\wave1140_motion_controller_current_risk_review.py --check",
        "missing package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs(failures)
    check_queue_progress_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave1140 motion-controller current-risk probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1140 motion-controller current-risk probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
