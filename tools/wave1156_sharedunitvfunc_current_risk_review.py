#!/usr/bin/env python3
"""Validate Wave1156 SharedUnitVFunc current-risk review evidence."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1156-sharedunitvfunc-current-risk-review"
FOCUSED_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-focused-candidates.json"
RISK_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-risk-ranked-functions.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1156-sharedunitvfunc-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1156-sharedunitvfunc-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1156_sharedunitvfunc_current_risk_review_2026-06-05.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PROGRESS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260605-231547_post_wave1156_sharedunitvfunc_current_risk_review_verified"
EXPECTED_SOURCE_ROOT = str(Path.home() / "Ghidra" / "Projects")

TARGETS = {
    "0x00401550": ("SharedUnitVFunc__WriteVector1cMinus8cToOut_00401550", "void __thiscall SharedUnitVFunc__WriteVector1cMinus8cToOut_00401550(void * this, void * outVector)"),
    "0x00401900": ("SharedUnitVFunc__ForwardArgToThingBridge_00401900", "void __thiscall SharedUnitVFunc__ForwardArgToThingBridge_00401900(void * this, void * arg)"),
    "0x00401910": ("SharedUnitVFunc__CopyTransformAndNotify_00401910", "void __thiscall SharedUnitVFunc__CopyTransformAndNotify_00401910(void * this, void * sourceBlock)"),
    "0x00405d90": ("SharedUnitVFunc__ReturnField130ColorMask_00405d90", "int __thiscall SharedUnitVFunc__ReturnField130ColorMask_00405d90(void * this)"),
    "0x00405de0": ("SharedUnitVFunc__TestField168Or214OrFlag2c_00405de0", "int __thiscall SharedUnitVFunc__TestField168Or214OrFlag2c_00405de0(void * this)"),
    "0x00405e10": ("SharedUnitVFunc__SetField1f0One_00405e10", "void __thiscall SharedUnitVFunc__SetField1f0One_00405e10(void * this)"),
    "0x00405e20": ("SharedUnitVFunc__ClearField1f0_00405e20", "void __thiscall SharedUnitVFunc__ClearField1f0_00405e20(void * this)"),
    "0x00405e30": ("SharedUnitVFunc__SetField15c_00405e30", "void __thiscall SharedUnitVFunc__SetField15c_00405e30(void * this, int value)"),
    "0x00405e40": ("SharedUnitVFunc__ReturnField15c_00405e40", "int __thiscall SharedUnitVFunc__ReturnField15c_00405e40(void * this)"),
    "0x00405e50": ("SharedUnitVFunc__ReturnField210_00405e50", "int __thiscall SharedUnitVFunc__ReturnField210_00405e50(void * this)"),
    "0x00405e70": ("SharedUnitVFunc__IsField168Null_00405e70", "int __thiscall SharedUnitVFunc__IsField168Null_00405e70(void * this)"),
    "0x004175c0": ("SharedUnitVFunc__ReturnField164FloatF4_004175c0", "float __thiscall SharedUnitVFunc__ReturnField164FloatF4_004175c0(void * this)"),
    "0x004175d0": ("SharedUnitVFunc__ReturnField164FloatF8_004175d0", "float __thiscall SharedUnitVFunc__ReturnField164FloatF8_004175d0(void * this)"),
    "0x004175e0": ("SharedUnitVFunc__ReturnField13cCOrZero_004175e0", "int __thiscall SharedUnitVFunc__ReturnField13cCOrZero_004175e0(void * this)"),
    "0x00417600": ("SharedUnitVFunc__SetField160_00417600", "void __thiscall SharedUnitVFunc__SetField160_00417600(void * this, int value)"),
    "0x00417610": ("SharedUnitVFunc__ReturnField164E4_00417610", "int __thiscall SharedUnitVFunc__ReturnField164E4_00417610(void * this)"),
    "0x00417620": ("SharedUnitVFunc__ReturnField164Float154_00417620", "float __thiscall SharedUnitVFunc__ReturnField164Float154_00417620(void * this)"),
    "0x00417630": ("SharedUnitVFunc__ReturnObject114OrOne_00417630", "int __thiscall SharedUnitVFunc__ReturnObject114OrOne_00417630(void * this)"),
    "0x004f9220": ("SharedUnitVFunc__CountNestedThingListAndDispatch_004f9220", "void __thiscall SharedUnitVFunc__CountNestedThingListAndDispatch_004f9220(void * this, void * thing)"),
    "0x004f9a10": ("SharedUnitVFunc__ReturnField178Or164C0Float_004f9a10", "float __thiscall SharedUnitVFunc__ReturnField178Or164C0Float_004f9a10(void * this)"),
    "0x004fb270": ("SharedUnitVFunc__ReturnField114Float_004fb270", "float __thiscall SharedUnitVFunc__ReturnField114Float_004fb270(void * this)"),
    "0x004fce00": ("SharedUnitVFunc__ForwardField208Slot10_004fce00", "void __thiscall SharedUnitVFunc__ForwardField208Slot10_004fce00(void * this, void * arg0, void * arg1, void * arg2, void * arg3, void * arg4)"),
    "0x004fd440": ("SharedUnitVFunc__TestField17c19cReadiness_004fd440", "int __thiscall SharedUnitVFunc__TestField17c19cReadiness_004fd440(void * this)"),
    "0x004fdc90": ("SharedUnitVFunc__IsField13cNotMode2_004fdc90", "int __thiscall SharedUnitVFunc__IsField13cNotMode2_004fdc90(void * this)"),
    "0x004fdd60": ("SharedUnitVFunc__PropagateNameToField18c19c_004fdd60", "void __thiscall SharedUnitVFunc__PropagateNameToField18c19c_004fdd60(void * this, void * name)"),
    "0x004fe4a0": ("SharedUnitVFunc__CopySourceVectors114120AndRefresh_004fe4a0", "void __thiscall SharedUnitVFunc__CopySourceVectors114120AndRefresh_004fe4a0(void * this, void * source)"),
    "0x004fe5c0": ("SharedUnitVFunc__ReturnField164B4ScaledByMode_004fe5c0", "float __thiscall SharedUnitVFunc__ReturnField164B4ScaledByMode_004fe5c0(void * this)"),
    "0x004fda90": ("SharedUnitVFunc__FindActiveMemberByField18c_004fda90", "int __thiscall SharedUnitVFunc__FindActiveMemberByField18c_004fda90(void * this)"),
    "0x004fe310": ("SharedUnitVFunc__TestField17cEntryNameMatch_004fe310", "int __thiscall SharedUnitVFunc__TestField17cEntryNameMatch_004fe310(void * this, void * name)"),
}

COMMON_TAGS = {
    "comment-hardened",
    "signature-hardened",
    "static-reaudit",
    "retail-binary-evidence",
    "shared-vfunc",
    "function-boundary-recovered",
    "unit-family-vtable",
}

DOCS = [
    NOTE,
    NOTE_MIRROR,
    READINESS,
    PROGRESS,
    PROGRESS_MIRROR,
    ROOT / "README.md",
    ROOT / "CURRENT_CAPABILITIES.md",
    ROOT / "AGENTS.md",
    ROOT / "reverse-engineering" / "RE-INDEX.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "unit-battleengine-gameplay-static-contract.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Unit.cpp" / "_index.md",
    ROOT / "developer_agent_state.json",
    ROOT / "documentation_agent_state.json",
    ROOT / "re_orchestrator_state.json",
]

DOC_TOKENS = (
    "Wave1156",
    "wave1156-sharedunitvfunc-current-risk-review",
    "453/1179 = 38.42%",
    "29 SharedUnitVFunc current-risk rows",
    "current focused candidates: 1178",
    "live regenerated current focused candidates: 1178",
    "remaining active focused work: 726",
    "current risk candidates: 6166",
    "fresh Ghidra export",
    "read-only review",
    "no mutation",
    "Codex read-only consults used",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "951 DATA xrefs",
    "442 instruction rows",
    "wave1083-readback-verified=6",
    "wave1085-readback-verified=23",
    "SharedUnitVFunc__WriteVector1cMinus8cToOut_00401550",
    "SharedUnitVFunc__TestField17c19cReadiness_004fd440",
    "SharedUnitVFunc__CopySourceVectors114120AndRefresh_004fe4a0",
    "SharedUnitVFunc__ForwardField208Slot10_004fce00",
    "SharedUnitVFunc__TestField17cEntryNameMatch_004fe310",
    BACKUP,
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
)

OVERCLAIMS = (
    "runtime behavior proven",
    "runtime gameplay behavior proven",
    "rebuild parity proven",
    "exact layout proven",
    "source identity proven",
    "hidden abi proven",
)

STALE_CURRENT = (
    "Current Ghidra RE status: Wave1155",
    "Latest related current-risk review: Wave1140",
    "Wave1108 current focused accounting | `238/1179 = 20.19%`",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def normalize_address(address: str) -> str:
    value = (address or "").strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


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
        "pre-metadata.tsv": 29,
        "pre-tags.tsv": 29,
        "pre-xrefs.tsv": 951,
        "pre-instructions.tsv": 442,
        "pre-decompile/index.tsv": 29,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-decompile" / "index.tsv")}
    xrefs = read_tsv(BASE / "pre-xrefs.tsv")
    xref_targets = {normalize_address(row.get("target_addr", "")) for row in xrefs}

    for address, (name, signature) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            comment = row.get("comment", "")
            for token in ("Static retail Ghidra", "runtime behavior", "rebuild parity"):
                require(token in comment, f"missing comment boundary token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"tags missing at {address}: {COMMON_TAGS - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        require(address in xref_targets, f"missing xrefs for {address}", failures)

    require(all(row.get("ref_type") == "DATA" for row in xrefs), "non-DATA xref found", failures)
    all_tags = ";".join(row.get("tags", "") for row in tags.values())
    require(all_tags.count("wave1083-readback-verified") == 6, "wave1083 tag count mismatch", failures)
    require(all_tags.count("wave1085-readback-verified") == 23, "wave1085 tag count mismatch", failures)


def check_logs_backup_queue(failures: list[str]) -> None:
    expected = {
        "pre-metadata.log": "targets=29 found=29 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=29 missing=0",
        "pre-xrefs.log": "Wrote 951 rows",
        "pre-instructions.log": "Wrote 442 function-body instruction rows",
        "pre-decompile.log": "targets=29 dumped=29 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "SCRIPT ERROR", "BADADDR", "MISSING:", "BADNAME:", "BADSIG:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("sourceRoot") == EXPECTED_SOURCE_ROOT, "backup source root mismatch", failures)
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


def check_docs_progress(failures: list[str]) -> None:
    progress = read_json(PROGRESS)
    latest = progress.get("latestWave", {})
    current = progress.get("post100Reaudit", {}).get("currentRiskRank", {})
    require(latest.get("wave") == "Wave1156 SharedUnitVFunc current-risk review", "latest wave mismatch", failures)
    require(latest.get("tag") == "wave1156-sharedunitvfunc-current-risk-review", "latest tag mismatch", failures)
    require(latest.get("backup") == BACKUP, "latest backup mismatch", failures)
    require(current.get("focusedReviewed") == 453, "progress focused reviewed mismatch", failures)
    require(current.get("focusedReviewedPercent") == "38.42%", "progress focused percent mismatch", failures)
    require(current.get("remainingFocusedAfterLatestReview") == 726, "progress remaining mismatch", failures)
    require(current.get("liveFocusedCandidatesAfterLatestReview") == 1178, "progress live focused mismatch", failures)
    require(current.get("latestReviewWave") == "Wave1156 SharedUnitVFunc current-risk review", "progress latest review mismatch", failures)

    for path in DOCS:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)
        for stale in STALE_CURRENT:
            require(stale not in text, f"stale current token in {path.relative_to(ROOT)}: {stale}", failures)

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1156 note mirror mismatch", failures)
    require(read_text(PROGRESS) == read_text(PROGRESS_MIRROR), "progress mirror mismatch", failures)
    require(
        read_json(PACKAGE_JSON).get("scripts", {}).get("test:wave1156-sharedunitvfunc-current-risk-review")
        == r"py -3 tools\wave1156_sharedunitvfunc_current_risk_review.py --check",
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
        print("Wave1156 SharedUnitVFunc current-risk probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1156 SharedUnitVFunc current-risk probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
