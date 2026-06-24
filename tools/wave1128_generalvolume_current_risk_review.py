#!/usr/bin/env python3
"""Validate Wave1128 GeneralVolume current-risk review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

import wave1108_current_risk_rank
import wave1127_mixed_score23_current_risk_review as wave1127


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1128-generalvolume-current-risk-review"
FOCUSED_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-focused-candidates.tsv"
RISK_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-risk-ranked-functions.tsv"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
QUALITY_LOG = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave1128.log"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1128-generalvolume-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1128-generalvolume-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1128_generalvolume_current_risk_review_2026-06-05.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
MAPPED_SYSTEMS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GENERALVOLUME_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "GeneralVolume.cpp" / "_index.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PROGRESS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"G:\GhidraBackups\BEA_20260605-072044_post_wave1128_generalvolume_current_risk_review_verified"
PRIOR_BACKUP = r"G:\GhidraBackups\BEA_20260605-071212_post_wave1127_mixed_score23_current_risk_review_verified"

TARGETS = {
    "0x00402020": (
        "CGeneralVolume__ResetCooldownTimestamp",
        "void __thiscall CGeneralVolume__ResetCooldownTimestamp(void * this, void * activeReaderTarget)",
        ("stores DAT_00672fd0 into this+0xd4", "activeReaderTarget", "concrete layout"),
        ("0x0040c73c", "CGeneralVolume__ResetAndSetActiveReader", "UNCONDITIONAL_CALL"),
        ("DAT_00672fd0", "0xd4"),
        ("active-reader-target", "comment-normalized", "cooldown-reset"),
    ),
    "0x0040b100": (
        "CGeneralVolume__ctor_base",
        "void __fastcall CGeneralVolume__ctor_base(void * generalVolume)",
        ("installs the CGeneralVolume vtable", "+0x4/+0x8/+0xc", "0x005d892c"),
        ("0x0040af55", "CBattleEngine__CalcUnitOverCrossHair", "UNCONDITIONAL_CALL"),
        ("PTR_LAB_005d892c", "0xc"),
        ("comment-normalized", "constructor", "vtable"),
    ),
    "0x0040c720": (
        "CGeneralVolume__ResetAndSetActiveReader",
        "void __thiscall CGeneralVolume__ResetAndSetActiveReader(void * this, void * activeReaderTarget)",
        ("swaps reader state", "CGenericActiveReader__SetReader", "CGeneralVolume__ResetCooldownTimestamp"),
        ("0x005d8adc", "<no_function>", "DATA"),
        ("CBattleEngine__SwapPrimarySecondaryPartReadersForState", "CGenericActiveReader__SetReader", "CGeneralVolume__ResetCooldownTimestamp"),
        ("active-reader", "comment-normalized", "reader-reset"),
    ),
    "0x00412830": (
        "CGeneralVolume__DisableLinkedEntriesByNameAndReselect",
        "void __thiscall CGeneralVolume__DisableLinkedEntriesByNameAndReselect(void * this, char * entry_name)",
        ("entry +0xa4", "clears entry +0x9c", "0x00411e70"),
        ("0x0040dc7b", "CBattleEngine__DisableVolumeEntryGroupsByNameAndReselect", "UNCONDITIONAL_CALL"),
        ("0xa4", "0x9c", "CBattleEngineJetPart__ChangeWeapon"),
        ("entry-selection", "string-compare", "weapon-selection"),
    ),
    "0x00413660": (
        "CGeneralVolume__ApplyYawInputByWeaponClass",
        "void __thiscall CGeneralVolume__ApplyYawInputByWeaponClass(void * this, int axis_input)",
        ("caller 0x004d337b", "DAT_005d8cd8", "owner yaw field +0x278"),
        ("0x004d337b", "CPlayer__ReceiveButtonAction", "UNCONDITIONAL_CALL"),
        ("DAT_00889304", "0xc", "0xb", "0x278", "_DAT_005d8cd8"),
        ("axis-input", "yaw", "weapon-class-control"),
    ),
    "0x004136e0": (
        "CGeneralVolume__ApplyPitchInputByWeaponClass",
        "void __thiscall CGeneralVolume__ApplyPitchInputByWeaponClass(void * this, int axis_input)",
        ("caller 0x004d3390", "DAT_005d8c90", "owner pitch field +0x280"),
        ("0x004d3390", "CPlayer__ReceiveButtonAction", "UNCONDITIONAL_CALL"),
        ("DAT_00889304", "0xc", "0xb", "0x280", "_DAT_005d8c90"),
        ("axis-input", "pitch", "weapon-class-control"),
    ),
}

COMMON_TAGS = (
    "wave1128-generalvolume-current-risk-review",
    "wave1128-readback-verified",
    "current-risk-review",
    "score-22-current-risk",
    "general-volume",
    "tag-normalized",
)

DOC_TOKENS = (
    "Wave1128",
    "wave1128-generalvolume-current-risk-review",
    "150/1179 = 12.72%",
    "6 rows",
    "current focused candidates: 1178",
    "remaining active focused work: 1029",
    "score-22",
    "CGeneralVolume",
    "fresh Ghidra export",
    "comment/tag normalization",
    "51 tags",
    "0 / 0 / 0",
    BACKUP,
    PRIOR_BACKUP,
)

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
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
    accounted = set(wave1127.prior_accounted_addresses())
    accounted.update(wave1127.TARGETS)
    return accounted


def row_map(path: Path, key: str = "address") -> dict[str, dict[str, str]]:
    return {normalize_address(row.get(key, "")): row for row in read_tsv(path)}


def unescape_tsv(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


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


def check_wave1108_accounting(failures: list[str]) -> None:
    wave1108_current_risk_rank.generate()
    focused_rows = read_tsv(FOCUSED_TSV)
    risk_rows = read_tsv(RISK_TSV)
    focused = {normalize_address(row.get("address", "")) for row in focused_rows}
    risk = {normalize_address(row.get("address", "")): row for row in risk_rows}
    accounted = prior_accounted_addresses()
    reviewed = accounted | set(TARGETS)

    require(len(focused_rows) == 1178, f"live focused row count mismatch: {len(focused_rows)}", failures)
    require(len(accounted) == 144, f"prior accounted count mismatch: {len(accounted)}", failures)
    require(len(reviewed) == 150, f"reviewed continuity count mismatch: {len(reviewed)}", failures)
    require(1179 - len(reviewed) == 1029, "continuity remaining focused count mismatch", failures)
    require(len(focused - reviewed) == 1029, f"live remaining focused count mismatch: {len(focused - reviewed)}", failures)
    for address in TARGETS:
        require(address in focused, f"target missing from live focused rows: {address}", failures)
        require(address in risk, f"target missing from live broad risk rows: {address}", failures)
        if address in risk:
            require(risk[address].get("score") == "22", f"live risk score mismatch at {address}", failures)


def check_exports(failures: list[str]) -> None:
    counts = {
        "pre-metadata.tsv": 6,
        "pre-tags.tsv": 6,
        "pre-xrefs.tsv": 54,
        "pre-instructions.tsv": 170,
        "pre-decompile/index.tsv": 6,
        "post-metadata.tsv": 6,
        "post-tags.tsv": 6,
        "post-xrefs.tsv": 54,
        "post-instructions.tsv": 170,
        "post-decompile/index.tsv": 6,
    }
    for relative, expected in counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    require(read_text(BASE / "pre-instructions.tsv") == read_text(BASE / "post-instructions.tsv"), "pre/post instruction drift", failures)

    log_tokens = {
        "pre-metadata.log": "targets=6 found=6 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=6 missing=0",
        "pre-xrefs.log": "Wrote 54 rows",
        "pre-instructions.log": "targets=6 missing=0",
        "pre-decompile.log": "targets=6 dumped=6 missing=0 failed=0",
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=3 tags_added=51 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=6 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=3 tags_added=51 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0",
        "post-metadata.log": "targets=6 found=6 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=6 missing=0",
        "post-xrefs.log": "Wrote 54 rows",
        "post-instructions.log": "targets=6 missing=0",
        "post-decompile.log": "targets=6 dumped=6 missing=0 failed=0",
    }
    for relative, token in log_tokens.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR", "BADNAME", "BADSIG", "VERIFY_MISSING", "missing=1", "failed=1", "bad=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    quality_text = read_text(QUALITY_LOG)
    require("total_functions=6410 commented_functions=6410" in quality_text, "missing Wave1128 quality refresh token", failures)


def check_target_rows(failures: list[str]) -> None:
    metadata = row_map(BASE / "post-metadata.tsv")
    post_tags = row_map(BASE / "post-tags.tsv")
    decompile = row_map(BASE / "post-decompile" / "index.tsv")
    xrefs = read_tsv(BASE / "post-xrefs.tsv")
    queue = row_map(QUEUE_TSV)
    queue_rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(queue_rows)

    require(len(queue_rows) == 6410, "queue TSV row count mismatch", failures)
    require(commented == 6410, "queue TSV commented count mismatch", failures)
    require(strict_clean == 6410, "queue TSV strict clean count mismatch", failures)

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
                if address in {"0x00402020", "0x0040b100", "0x0040c720"}:
                    require("tags" not in comment.lower(), f"{label} stale tag-gap wording at {address}", failures)

        post_tag_row = post_tags.get(address)
        require(post_tag_row is not None, f"missing post-tags for {address}", failures)
        if post_tag_row is not None:
            require(post_tag_row.get("name") == name, f"post-tag name mismatch at {address}", failures)
            require(post_tag_row.get("status") == "OK", f"post-tag status mismatch at {address}", failures)
            tag_text = post_tag_row.get("tags", "")
            for token in COMMON_TAGS + expected_tags:
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
    require(int(backup.get("totalBytes")) == 175934343, "backup byte count mismatch", failures)
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
        GENERALVOLUME_DOC,
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
    commit_pattern = re.compile(r"^(pending Wave1128 artifact commit|[0-9a-f]{40})$")
    for label, data in (("progress", progress), ("progress mirror", mirror)):
        current = data["post100Reaudit"]["currentRiskRank"]
        require(data["latestWave"]["wave"] == "Wave1128 GeneralVolume current-risk review", f"{label} latest wave mismatch", failures)
        require(data["latestWave"]["tag"] == "wave1128-generalvolume-current-risk-review", f"{label} latest tag mismatch", failures)
        require(data["latestWave"]["backup"] == BACKUP, f"{label} backup mismatch", failures)
        require(bool(commit_pattern.match(data["latestWave"].get("artifactCommit", ""))), f"{label} artifact commit mismatch", failures)
        require(current["focusedReviewed"] == 150, f"{label} focused reviewed mismatch", failures)
        require(current["focusedCandidates"] == 1179, f"{label} focused denominator mismatch", failures)
        require(current["focusedReviewedPercent"] == "12.72%", f"{label} focused percent mismatch", failures)
        require(current["latestReviewTag"] == "wave1128-generalvolume-current-risk-review", f"{label} review tag mismatch", failures)
        require(current.get("liveFocusedCandidatesAfterLatestReview") == 1178, f"{label} live focused count mismatch", failures)
        require(current.get("remainingFocusedAfterLatestReview") == 1029, f"{label} remaining focused count mismatch", failures)

    package = read_json(PACKAGE_JSON)
    expected_script = r"py -3 tools\wave1128_generalvolume_current_risk_review.py --check"
    require(package["scripts"].get("test:wave1128-generalvolume-current-risk-review") == expected_script, "missing package script", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_wave1108_accounting(failures)
    check_exports(failures)
    check_target_rows(failures)
    check_backup(failures)
    check_docs_and_state(failures)
    if failures:
        print("Wave1128 GeneralVolume current-risk review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1128 GeneralVolume current-risk review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
