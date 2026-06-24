#!/usr/bin/env python3
"""Validate Wave1215 unit-targeting combat residual current-risk artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1215-unit-targeting-combat-residual-current-risk-review"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1215-unit-targeting-combat-residual-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1215-unit-targeting-combat-residual-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1215_unit_targeting_combat_residual_current_risk_review_2026-06-07.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-current-risk-ledger.json"
ACCOUNTING = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-accounting-guard.md"
MEASUREMENT_REGISTER = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-measurement-register.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
UNIT_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "unit-battleengine-gameplay-static-contract.md"
RANK = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
AIRUNIT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "AirUnit.cpp" / "_index.md"
COMPONENT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Component.cpp" / "_index.md"
DIVEBOMBER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DiveBomber.cpp" / "_index.md"
SQUADNORMAL_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "SquadNormal.cpp" / "_index.md"
SQUADRELAXED_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "SquadRelaxed.cpp" / "_index.md"
PACKAGE_JSON = ROOT / "package.json"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"

BACKUP = r"G:\GhidraBackups\BEA_20260607-090802_post_wave1215_unit_targeting_combat_residual_current_risk_review_verified"

TARGETS = {
    "0x004027c0": (
        "CAirGuide__AcquireNearestTargetReader",
        "void __fastcall CAirGuide__AcquireNearestTargetReader(void * this)",
        ("004026fa", "CAirGuide__HandleEvent", "+0x2c"),
    ),
    "0x00445070": (
        "CDiveBomber__SelectTarget",
        "void __thiscall CDiveBomber__SelectTarget(void * this, void * out_target_position)",
        ("004fd4e1", "CCannon__SelectTarget", "+0x15c/+0x160"),
    ),
    "0x0044e640": (
        "ComponentTargeting__ScanListsAndMaybeTriggerAction_0044e640",
        "bool __fastcall ComponentTargeting__ScanListsAndMaybeTriggerAction_0044e640(void * this)",
        ("005d96ac", "owner-deferred", "0x004ffdd0"),
    ),
    "0x00477cb0": (
        "CSquadNormal__SelectBestEngagementTarget",
        "void * __stdcall CSquadNormal__SelectBestEngagementTarget(void * squad)",
        ("004e815a", "DAT_00855090", "squad+0xa0"),
    ),
    "0x004ea8d0": (
        "CRelaxedSquad__CreateIterator",
        "void * __fastcall CRelaxedSquad__CreateIterator(void * this)",
        ("005e3b10", "CSPtrSet__AddToHead", "this+0xa4"),
    ),
}

TARGET_XREFS = {
    "0x004027c0": (("004026fa", "UNCONDITIONAL_CALL"),),
    "0x00445070": (("004fd4e1", "UNCONDITIONAL_CALL"),),
    "0x0044e640": (("005d96ac", "DATA"),),
    "0x00477cb0": (("004e815a", "UNCONDITIONAL_CALL"), ("004ea584", "UNCONDITIONAL_CALL")),
    "0x004ea8d0": (("005e3b10", "DATA"),),
}

DOC_TOKENS = (
    "Wave1215",
    "wave1215-unit-targeting-combat-residual-current-risk-review",
    "5 unit-targeting combat residual current-risk rows",
    "1138/1179 = 96.52%",
    "remaining active focused work: 41",
    "1169/1179",
    "26 duplicate-address overcount",
    "Wave1145 arithmetic overcount: 5",
    "current focused candidates: 1127",
    "live regenerated current focused candidates: 1127",
    "current risk candidates: 6166",
    "fresh Ghidra export",
    "read-only review",
    "no mutation",
    "no rename",
    "no signature change",
    "no comment change",
    "no tag change",
    "no function-boundary change",
    "no executable-byte change",
    "Codex read-only consults used",
    "no Cursor/Composer",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "6 xref rows",
    "794 instruction rows",
    "5 decompile rows",
    "425 context xref rows",
    "1123 context instruction rows",
    "15 context decompile rows",
    "1 data-slot xref row",
    "CAirGuide__AcquireNearestTargetReader",
    "CDiveBomber__SelectTarget",
    "ComponentTargeting__ScanListsAndMaybeTriggerAction_0044e640",
    "CSquadNormal__SelectBestEngagementTarget",
    "CRelaxedSquad__CreateIterator",
    BACKUP,
    "static-reaudit-current-risk-ledger.json",
    "static-reaudit-measurement-register.md",
    "unit-battleengine-gameplay-static-contract.md",
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "continuity denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
    "rebuild-grade static contracts",
    "no noticeable difference",
)

OWNER_DOC_TOKENS = {
    AIRUNIT_DOC: ("Wave1215", "CAirGuide__AcquireNearestTargetReader", "+0x2c", BACKUP),
    COMPONENT_DOC: ("Wave1215", "ComponentTargeting__ScanListsAndMaybeTriggerAction_0044e640", "owner-deferred", BACKUP),
    DIVEBOMBER_DOC: ("Wave1215", "CDiveBomber__SelectTarget", "CCannon__SelectTarget", BACKUP),
    SQUADNORMAL_DOC: ("Wave1215", "CSquadNormal__SelectBestEngagementTarget", "CSquadNormal__ScheduleTargetReaderRefresh", BACKUP),
    SQUADRELAXED_DOC: ("Wave1215", "CRelaxedSquad__CreateIterator", "CSPtrSet__AddToHead", BACKUP),
    UNIT_CONTRACT: ("Wave1215", "unit-targeting combat residual", "1179/1179", BACKUP),
}

OVERCLAIMS = (
    "runtime behavior proven",
    "runtime targeting behavior proven",
    "runtime squad ai behavior proven",
    "runtime component behavior proven",
    "exact layout proven",
    "exact source identity proven",
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
        "pre-metadata.tsv": 5,
        "pre-tags.tsv": 5,
        "pre-xrefs.tsv": 6,
        "pre-instructions.tsv": 794,
        "pre-decompile/index.tsv": 5,
        "context-metadata.tsv": 15,
        "context-tags.tsv": 15,
        "context-xrefs.tsv": 425,
        "context-instructions.tsv": 1123,
        "context-decompile/index.tsv": 15,
        "data-xrefs.tsv": 1,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-decompile" / "index.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-tags.tsv")}
    xrefs = read_tsv(BASE / "pre-xrefs.tsv")
    evidence_text = (
        read_text(BASE / "pre-metadata.tsv")
        + read_text(BASE / "pre-xrefs.tsv")
        + read_text(BASE / "pre-instructions.tsv")
        + read_text(BASE / "context-metadata.tsv")
        + read_text(BASE / "context-xrefs.tsv")
        + read_text(BASE / "context-instructions.tsv")
        + "".join(read_text(path) for path in sorted((BASE / "pre-decompile").glob("*.c")))
        + "".join(read_text(path) for path in sorted((BASE / "context-decompile").glob("*.c")))
    )

    for address, (name, signature, tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            bounded_tokens = ("Not concrete layout", "runtime targeting proof") if address == "0x004027c0" else ("Static", "evidence only")
            for token in bounded_tokens:
                require(token in row.get("comment", ""), f"missing bounded comment token at {address}: {token}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tag row for {address}", failures)
        if tag_row is not None:
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        for from_addr, ref_type in TARGET_XREFS[address]:
            require(
                any(
                    normalize_address(row.get("target_addr", "")) == address
                    and row.get("from_addr") == from_addr
                    and row.get("ref_type") == ref_type
                    for row in xrefs
                ),
                f"missing xref {from_addr} {ref_type} for {address}",
                failures,
            )
        for token in tokens:
            require(contains_token(evidence_text, token), f"missing evidence token for {address}: {token}", failures)

    data_rows = read_tsv(BASE / "data-xrefs.tsv")
    require(data_rows[0].get("target_addr") == "005d96ac", "data slot target mismatch", failures)
    require(data_rows[0].get("target_name") == "<no_function>", "data slot function mismatch", failures)
    require(data_rows[0].get("ref_type") == "<none>", "data slot ref type mismatch", failures)

    logs = {
        "pre-metadata.log": "targets=5 found=5 missing=0",
        "pre-tags.log": "rows=5 missing=0",
        "pre-xrefs.log": "Wrote 6 rows",
        "pre-instructions.log": "Wrote 794 function-body instruction rows",
        "pre-decompile.log": "targets=5 dumped=5 missing=0 failed=0",
        "context-metadata.log": "targets=15 found=15 missing=0",
        "context-tags.log": "rows=15 missing=0",
        "context-xrefs.log": "Wrote 425 rows",
        "context-instructions.log": "Wrote 1123 function-body instruction rows",
        "context-decompile.log": "targets=15 dumped=15 missing=0 failed=0",
        "data-xrefs.log": "Wrote 1 rows",
    }
    for relative, token in logs.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR", "MISSING", "FAIL", "missing=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_backup_and_progress(failures: list[str]) -> None:
    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 176425863 or backup.get("totalBytes") == 176425863.0, "backup bytes mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)

    progress = read_json(PROGRESS)
    current = progress["post100Reaudit"]["currentRiskRank"]
    require(current.get("focusedReviewed") == 1138, "progress focused reviewed mismatch", failures)
    require(current.get("focusedReviewedPercent") == "96.52%", "progress percent mismatch", failures)
    require(current.get("remainingFocusedAfterLatestReview") == 41, "progress remaining mismatch", failures)
    require(current.get("latestReviewTag") == "wave1215-unit-targeting-combat-residual-current-risk-review", "latest review tag mismatch", failures)

    ledger = read_json(LEDGER)
    require(ledger.get("correctedUniqueReviewed") == 1138, "ledger reviewed mismatch", failures)
    require(ledger.get("correctedUniquePercent") == "96.52%", "ledger percent mismatch", failures)
    require(ledger.get("remainingUnique") == 41, "ledger remaining mismatch", failures)
    require(ledger.get("latestWaveTag") == "wave1215-unit-targeting-combat-residual-current-risk-review", "ledger latest tag mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        NOTE,
        READINESS,
        PROGRESS,
        ACCOUNTING,
        MEASUREMENT_REGISTER,
        MAPPED,
        CAMPAIGN,
        UNIT_CONTRACT,
        RANK,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIMS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    for path, tokens in OWNER_DOC_TOKENS.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing owner-doc token in {path.relative_to(ROOT)}: {token}", failures)

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "wave note mirror mismatch", failures)
    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:wave1215-unit-targeting-combat-residual-current-risk-review")
        == r"py -3 tools\wave1215_unit_targeting_combat_residual_current_risk_review.py --check",
        "missing package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_backup_and_progress(failures)
    check_docs(failures)

    if failures:
        print("Wave1215 unit-targeting combat residual current-risk probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1215 unit-targeting combat residual current-risk probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
