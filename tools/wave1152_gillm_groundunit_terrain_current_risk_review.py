#!/usr/bin/env python3
"""Validate Wave1152 GillM/GroundUnit terrain current-risk artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1152-gillm-groundunit-terrain-current-risk-review"
FOCUSED_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-focused-candidates.json"
RISK_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-risk-ranked-functions.json"
FOCUSED_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-focused-candidates.tsv"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1152-gillm-groundunit-terrain-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1152-gillm-groundunit-terrain-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1152_gillm_groundunit_terrain_current_risk_review_2026-06-05.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PROGRESS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"G:\GhidraBackups\BEA_20260605-203535_post_wave1152_gillm_groundunit_terrain_current_risk_review_verified"
PRIOR_BACKUP = r"G:\GhidraBackups\BEA_20260605-201419_post_wave1151_mixed_score21_current_risk_review_verified"

TARGETS = {
    "0x00479f30": (
        "CGillM__ComputeTerrainClearanceNoiseScale",
        "double __fastcall CGillM__ComputeTerrainClearanceNoiseScale(void * this)",
        ("0x274", "0x244", "static-shadow"),
    ),
    "0x0047a0b0": (
        "CGillM__ComputeLateralSlopeAlignment",
        "double __fastcall CGillM__ComputeLateralSlopeAlignment(void * this)",
        ("0x114", "heightfield normal", "lateral slope"),
    ),
    "0x0047c970": (
        "CGroundUnit__UpdateLinkedEffectsByHeightClearance",
        "void __fastcall CGroundUnit__UpdateLinkedEffectsByHeightClearance(void * this)",
        ("0x1d4", "0x1e4", "CUnit__UpdateMotionAttachmentsAndEffects"),
    ),
    "0x0047ce80": (
        "CGroundUnit__MarkDestroyedAndResetState",
        "int __fastcall CGroundUnit__MarkDestroyedAndResetState(void * this)",
        ("CUnit__MarkDestroyedAndCleanupLinks", "0x25c", "returns 1"),
    ),
    "0x0047cea0": (
        "CGroundUnit__ClearLinkedThingFlagsAndResetCounter",
        "void __fastcall CGroundUnit__ClearLinkedThingFlagsAndResetCounter(void * this)",
        ("0x1d4", "ParticleEffectLink__SetHandleStateAndClear", "0x1e4"),
    ),
}

DOC_TOKENS = (
    "Wave1152",
    "wave1152-gillm-groundunit-terrain-current-risk-review",
    "373/1179 = 31.64%",
    "5 current-risk rows",
    "current focused candidates: 1178",
    "live regenerated current focused candidates: 1178",
    "remaining active focused work: 806",
    "current risk candidates: 6166",
    "GillM/GroundUnit terrain current-risk review",
    "fresh Ghidra export",
    "read-only review",
    "no mutation",
    "no Codex subagent",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "CGillM__ComputeTerrainClearanceNoiseScale",
    "CGillM__ComputeLateralSlopeAlignment",
    "CGroundUnit__UpdateLinkedEffectsByHeightClearance",
    "CGroundUnit__MarkDestroyedAndResetState",
    "CGroundUnit__ClearLinkedThingFlagsAndResetCounter",
    BACKUP,
    PRIOR_BACKUP,
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
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
        "pre-metadata.tsv": 5,
        "pre-tags.tsv": 5,
        "pre-xrefs.tsv": 21,
        "pre-instructions.tsv": 584,
        "pre-decompile/index.tsv": 5,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-decompile" / "index.tsv")}
    xref_targets = {normalize_address(row["target_addr"]) for row in read_tsv(BASE / "pre-xrefs.tsv")}
    evidence = "\n".join(row.get("comment", "") for row in metadata.values())
    evidence += "\n" + "\n".join(read_text(path) for path in (BASE / "pre-decompile").glob("*.c"))
    evidence += "\n" + "\n".join(
        f"{row.get('mnemonic','')} {row.get('operands','')}" for row in read_tsv(BASE / "pre-instructions.tsv")
    )
    compact = evidence.lower().replace(" ", "")

    for address, (name, signature, tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in tokens:
                require(token.lower().replace(" ", "") in compact or token in evidence, f"missing evidence token at {address}: {token}", failures)
        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)
        require(address in xref_targets, f"missing xrefs for {address}", failures)


def check_logs_backup_queue(failures: list[str]) -> None:
    expected = {
        "pre-metadata.log": "targets=5 found=5 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=5 missing=0",
        "pre-xrefs.log": "Wrote 21 rows",
        "pre-instructions.log": "Wrote 584 function-body instruction rows",
        "pre-decompile.log": "targets=5 dumped=5 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "SCRIPT ERROR", "BADADDR", "MISSING:", "BADNAME:", "BADSIG:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 175967111, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)

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
    require(read_json(RISK_JSON).get("candidateFunctions") == 6166, "current risk candidate mismatch", failures)
    require(read_json(FOCUSED_JSON).get("candidateFunctions") == 1178, "focused candidate mismatch", failures)
    focused_addresses = {normalize_address(row["address"]) for row in read_tsv(FOCUSED_TSV)}
    for address in TARGETS:
        require(address in focused_addresses, f"target absent from focused list: {address}", failures)


def check_docs_progress(failures: list[str]) -> None:
    progress = read_json(PROGRESS)
    current = progress["post100Reaudit"]["currentRiskRank"]
    latest = progress["latestWave"]
    require(latest["wave"] == "Wave1152 GillM/GroundUnit terrain current-risk review", "progress latest wave mismatch", failures)
    require(latest["tag"] == "wave1152-gillm-groundunit-terrain-current-risk-review", "progress latest tag mismatch", failures)
    require(latest["backup"] == BACKUP, "progress backup mismatch", failures)
    require(current["focusedReviewed"] == 373, "progress focused reviewed mismatch", failures)
    require(current["focusedReviewedPercent"] == "31.64%", "progress focused percent mismatch", failures)
    require(current["remainingFocusedAfterLatestReview"] == 806, "progress remaining mismatch", failures)
    require(current["liveFocusedCandidatesAfterLatestReview"] == 1178, "progress live focused mismatch", failures)

    core_docs = [
        NOTE,
        NOTE_MIRROR,
        READINESS,
        ROOT / "README.md",
        ROOT / "AGENTS.md",
        ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md",
        ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md",
        ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md",
        ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md",
        ROOT / "release" / "readiness" / "wave1108_current_risk_rank_2026-06-04.md",
        ROOT / "developer_agent_state.json",
        ROOT / "documentation_agent_state.json",
        ROOT / "re_orchestrator_state.json",
    ]
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)

    owner_docs = {
        ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "GillM.cpp" / "_index.md": (
            "Wave1152",
            "wave1152-gillm-groundunit-terrain-current-risk-review",
            "CGillM__ComputeTerrainClearanceNoiseScale",
            "CGillM__ComputeLateralSlopeAlignment",
            BACKUP,
            "Runtime behavior, exact layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity remain separate proof.",
        ),
        ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "GroundUnit.cpp" / "_index.md": (
            "Wave1152",
            "wave1152-gillm-groundunit-terrain-current-risk-review",
            "CGroundUnit__UpdateLinkedEffectsByHeightClearance",
            "CGroundUnit__MarkDestroyedAndResetState",
            "CGroundUnit__ClearLinkedThingFlagsAndResetCounter",
            BACKUP,
            "Runtime behavior, exact layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity remain separate proof.",
        ),
    }
    for path, tokens in owner_docs.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1152 note mirror mismatch", failures)
    require(read_text(PROGRESS) == read_text(PROGRESS_MIRROR), "progress mirror mismatch", failures)
    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:wave1152-gillm-groundunit-terrain-current-risk-review")
        == r"py -3 tools\wave1152_gillm_groundunit_terrain_current_risk_review.py --check",
        "missing package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()
    failures: list[str] = []
    check_artifacts(failures)
    check_logs_backup_queue(failures)
    check_docs_progress(failures)
    if failures:
        print("Wave1152 GillM/GroundUnit terrain current-risk probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1152 GillM/GroundUnit terrain current-risk probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
