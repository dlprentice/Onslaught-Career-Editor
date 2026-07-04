#!/usr/bin/env python3
"""Validate Wave1165 CFastVB dispatch-slot tail read-only evidence."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1165-cfastvb-dispatch-slot-tail-current-risk-review"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1165-cfastvb-dispatch-slot-tail-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1165-cfastvb-dispatch-slot-tail-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1165_cfastvb_dispatch_slot_tail_current_risk_review_2026-06-06.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
FASTVB_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FastVB.cpp" / "_index.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
RANK = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260606-040830_post_wave1165_cfastvb_dispatch_slot_tail_current_risk_review_verified"

TARGETS = {
    "0x005a77bc": ("CFastVB__DispatchOp_SlotA4_005a77bc", "0x005985c2"),
    "0x005a923f": ("CFastVB__DispatchOp_Slot10_005a923f", "0x00598658"),
    "0x005a996b": ("CFastVB__DispatchOp_Slot48_005a996b", "0x00598506"),
    "0x005a9987": ("CFastVB__DispatchOp_Slot04_005a9987", "0x00598496"),
    "0x005a9abe": ("CFastVB__DispatchOp_SlotCC_005a9abe", "0x005985f4"),
    "0x005a9b2f": ("CFastVB__DispatchOp_SlotC4_005a9b2f", "0x0059861c"),
    "0x005a9c03": ("CFastVB__DispatchOp_SlotC8_005a9c03", "0x0059864e"),
    "0x005aa5c0": ("CFastVB__DispatchOp_SlotE4_005aa5c0", "0x00598673"),
    "0x005aa82d": ("CFastVB__DispatchOp_Slot44_005aa82d", "0x005984ff"),
    "0x005aa8c5": ("CFastVB__DispatchOp_SlotC0_005aa8c5", "0x005985fe"),
    "0x005aa90e": ("CFastVB__DispatchOp_SlotB8_005aa90e", "0x00598608"),
    "0x005aa951": ("CFastVB__DispatchOp_SlotBC_005aa951", "0x00598644"),
    "0x005aa9fc": ("CFastVB__DispatchOp_Slot08_005aa9fc", "0x0059849d"),
    "0x005aaa7e": ("CFastVB__DispatchOp_Slot20_005aaa7e", "0x005984c0"),
    "0x005aaadd": ("CFastVB__DispatchOp_Slot40_005aaadd", "0x005984f8"),
    "0x005aac0f": ("CFastVB__DispatchOp_SlotD8_005aac0f", "0x005985ea"),
    "0x005aac80": ("CFastVB__DispatchOp_SlotD0_005aac80", "0x00598612"),
    "0x005aad48": ("CFastVB__DispatchOp_SlotD4_005aad48", "0x0059863a"),
    "0x005aae26": ("CFastVB__DispatchOp_Slot30_005aae26", "0x005984dc"),
    "0x005aae69": ("CFastVB__DispatchOp_Slot34_005aae69", "0x005984e3"),
    "0x005aaf4d": ("CFastVB__DispatchOp_Slot58_005aaf4d", "0x00598522"),
}

DOC_TOKENS = (
    "Wave1165",
    "wave1165-cfastvb-dispatch-slot-tail-current-risk-review",
    "604/1179 = 51.23%",
    "21 CFastVB dispatch-slot tail current-risk rows",
    "current focused candidates: 1178",
    "live regenerated current focused candidates: 1178",
    "remaining active focused work: 575",
    "current risk candidates: 6166",
    "fresh Ghidra export",
    "read-only review",
    "no mutation",
    "Codex read-only consult used",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "21 xref rows",
    "1417 instruction rows",
    "CFastVB__DispatchOp_SlotA4_005a77bc",
    "CFastVB__DispatchOp_Slot10_005a923f",
    "CFastVB__DispatchOp_SlotCC_005a9abe",
    "CFastVB__DispatchOp_SlotC0_005aa8c5",
    "CFastVB__DispatchOp_SlotD8_005aac0f",
    "CFastVB__DispatchOp_Slot58_005aaf4d",
    "CFastVB__InitDispatchOpsFromFeatureFlags",
    BACKUP,
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
)

OVERCLAIMS = (
    "runtime cpu dispatch/math/render behavior proven",
    "runtime behavior proven",
    "exact dispatch-table slot schema proven",
    "hidden mmx/sse/register/stack abi completeness proven",
    "source identity proven",
    "rebuild parity proven",
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


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 21,
        "pre-tags.tsv": 21,
        "pre-xrefs.tsv": 21,
        "pre-instructions.tsv": 1417,
        "pre-decompile/index.tsv": 21,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-tags.tsv")}
    xrefs = {normalize_address(row["target_addr"]): row for row in read_tsv(BASE / "pre-xrefs.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-decompile" / "index.tsv")}

    for address, (name, xref_from) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == f"int {name}(void)", f"signature mismatch at {address}", failures)
            comment = row.get("comment", "")
            for token in ("Wave971 CFastVB dispatch-slot boundary sweep", "CFastVB__InitDispatchOpsFromFeatureFlags", "Static retail Ghidra evidence only"):
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags at {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            for tag in ("cfastvb", "cfastvb-dispatch-slot-boundary-sweep-wave971", "dispatch-table-target", "stack-locked"):
                require(tag in actual_tags, f"missing tag at {address}: {tag}", failures)

        xref = xrefs.get(address)
        require(xref is not None, f"missing xref at {address}", failures)
        if xref is not None:
            require(normalize_address(xref.get("from_addr", "")) == xref_from, f"xref source mismatch at {address}", failures)
            require(xref.get("from_function") == "CFastVB__InitDispatchOpsFromFeatureFlags", f"xref function mismatch at {address}", failures)
            require(xref.get("ref_type") == "DATA", f"xref type mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row at {address}", failures)
        if dec is not None:
            require(dec.get("signature") == f"int {name}(void)", f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)


def check_logs_backup_progress(failures: list[str]) -> None:
    expected_logs = {
        "pre-metadata.log": "targets=21 found=21 missing=0",
        "pre-tags.log": "rows=21 missing=0",
        "pre-xrefs.log": "Wrote 21 rows",
        "pre-instructions.log": "Wrote 1417 function-body instruction rows",
        "pre-decompile.log": "targets=21 dumped=21 missing=0 failed=0",
    }
    for relative, token in expected_logs.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR:", "FAIL:", "missing=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes", 0)) == 176032647, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff mismatch", failures)

    progress = read_json(PROGRESS)
    latest = progress.get("latestWave", {})
    require(latest.get("wave") == "Wave1165 CFastVB dispatch-slot tail current-risk review", "latest progress wave mismatch", failures)
    require(latest.get("tag") == "wave1165-cfastvb-dispatch-slot-tail-current-risk-review", "latest progress tag mismatch", failures)
    current = progress.get("post100Reaudit", {}).get("currentRiskRank", {})
    require(current.get("focusedReviewed") == 604, "current focused reviewed mismatch", failures)
    require(current.get("focusedReviewedPercent") == "51.23%", "current focused percent mismatch", failures)
    require(current.get("remainingFocusedAfterLatestReview") == 575, "remaining focused mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        NOTE,
        NOTE_MIRROR,
        READINESS,
        PROGRESS,
        FASTVB_DOC,
        MAPPED,
        CAMPAIGN,
        RANK,
        FUNCTION_COVERAGE,
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

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1165 note mirror mismatch", failures)
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:wave1165-cfastvb-dispatch-slot-tail-current-risk-review")
        == r"py -3 tools\wave1165_cfastvb_dispatch_slot_tail_current_risk_review.py --check",
        "missing Wave1165 package script",
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
        print("Wave1165 CFastVB dispatch-slot tail probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1165 CFastVB dispatch-slot tail probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
