#!/usr/bin/env python3
"""Validate Wave1168 unit target-reader tail read-only artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1168-unit-target-reader-tail-current-risk-review"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1168-unit-target-reader-tail-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1168-unit-target-reader-tail-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1168_unit_target_reader_tail_current_risk_review_2026-06-06.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
RANK = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
SQUAD_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "SquadNormal.cpp" / "_index.md"
UNIT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Unit.cpp" / "_index.md"
UNITAI_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "UnitAI.cpp" / "_index.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260606-052300_post_wave1168_unit_target_reader_tail_current_risk_review_verified"

TARGETS = {
    "0x004fb3d0": ("CSquadNormal__IsValidLinkedSupportForTarget", "int __thiscall CSquadNormal__IsValidLinkedSupportForTarget"),
    "0x004fb650": ("CUnit__ForwardAimTransformAndAttachTargetReader", "void __thiscall CUnit__ForwardAimTransformAndAttachTargetReader"),
    "0x004fc3a0": ("CUnit__SetSpawnCooldownState3", "void __thiscall CUnit__SetSpawnCooldownState3"),
    "0x004fce40": ("CUnit__ForwardAttachedNodeVFunc14IfPresent", "int __thiscall CUnit__ForwardAttachedNodeVFunc14IfPresent"),
    "0x004fce80": ("CUnit__ForwardAttachedNodeVFunc18IfPresent", "int __thiscall CUnit__ForwardAttachedNodeVFunc18IfPresent"),
    "0x004fcec0": ("CUnit__ForwardAttachedNodeVFunc1CIfPresent", "int __thiscall CUnit__ForwardAttachedNodeVFunc1CIfPresent"),
    "0x004fd5e0": ("CUnit__VFunc26_GetRecentSegmentDamageMeter", "int __thiscall CUnit__VFunc26_GetRecentSegmentDamageMeter"),
    "0x004fd6a0": ("CUnit__VFunc22_ActivateLinkedTargetsAndChildren", "void __fastcall CUnit__VFunc22_ActivateLinkedTargetsAndChildren"),
    "0x004fd700": ("CUnit__VFunc23_DeactivateLinkedTargetsAndChildren", "void __fastcall CUnit__VFunc23_DeactivateLinkedTargetsAndChildren"),
    "0x004fea30": ("SharedUnitAI__CheckField24TargetState_004fea30", "int __thiscall SharedUnitAI__CheckField24TargetState_004fea30"),
    "0x004feac0": ("SharedUnitAI__CheckField24RangeAgainstCandidate_004feac0", "int __thiscall SharedUnitAI__CheckField24RangeAgainstCandidate_004feac0"),
    "0x004ffbb0": ("SharedUnitAI__UpdateField28TargetReaderGate_004ffbb0", "int __thiscall SharedUnitAI__UpdateField28TargetReaderGate_004ffbb0"),
}

COMMENT_TOKENS = {
    "0x004fb3d0": ("Wave523", "support", "target"),
    "0x004fb650": ("Wave523", "OID__UpdateAimTransformAndAttachTargetReader"),
    "0x004fc3a0": ("Wave837", "CSpawnerThng__ProcessSpawnWave", "cooldown_delay"),
    "0x004fce40": ("Wave838", "vfunc +0x14"),
    "0x004fce80": ("Wave838", "vfunc +0x18"),
    "0x004fcec0": ("Wave838", "vfunc +0x1c"),
    "0x004fd5e0": ("Wave540", "damage"),
    "0x004fd6a0": ("Wave540", "Activate"),
    "0x004fd700": ("Wave540", "Deactivate"),
    "0x004fea30": ("Wave1082", "this+0x24"),
    "0x004feac0": ("Wave1082", "candidate"),
    "0x004ffbb0": ("Wave1082", "this+0x28", "target virtual slots"),
}

DOC_TOKENS = (
    "Wave1168",
    "wave1168-unit-target-reader-tail-current-risk-review",
    "648/1179 = 54.96%",
    "12 CUnit / CSquadNormal / SharedUnitAI target-reader tail current-risk rows",
    "current focused candidates: 1178",
    "live regenerated current focused candidates: 1178",
    "remaining active focused work: 531",
    "current risk candidates: 6166",
    "fresh Ghidra export",
    "read-only review",
    "no mutation",
    "Codex read-only consult used",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "191 xref rows",
    "618 instruction rows",
    "CSquadNormal__IsValidLinkedSupportForTarget",
    "CUnit__ForwardAimTransformAndAttachTargetReader",
    "CUnit__SetSpawnCooldownState3",
    "CUnit__ForwardAttachedNodeVFunc14IfPresent",
    "CUnit__VFunc22_ActivateLinkedTargetsAndChildren",
    "SharedUnitAI__UpdateField28TargetReaderGate_004ffbb0",
    "CSpawnerThng__ProcessSpawnWave",
    "OID__UpdateAimTransformAndAttachTargetReader",
    BACKUP,
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
)

OVERCLAIMS = (
    "runtime targeting behavior proven",
    "runtime squad ai behavior proven",
    "runtime attached-node behavior proven",
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
        "pre-metadata.tsv": 12,
        "pre-tags.tsv": 12,
        "pre-xrefs.tsv": 191,
        "pre-instructions.tsv": 618,
        "pre-decompile/index.tsv": 12,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    decompile = {normalize(row["address"]): row for row in read_tsv(BASE / "pre-decompile" / "index.tsv")}
    tags = {normalize(row["address"]): row for row in read_tsv(BASE / "pre-tags.tsv")}
    xrefs = {normalize(row["target_addr"]): row for row in read_tsv(BASE / "pre-xrefs.tsv")}

    for address, (name, signature_prefix) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata {address}", failures)
        if row:
            require(row.get("name") == name, f"name mismatch {address}", failures)
            require(row.get("signature", "").startswith(signature_prefix), f"signature mismatch {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
            comment = row.get("comment", "")
            for token in COMMENT_TOKENS[address]:
                require(token in comment, f"missing comment token {address}: {token}", failures)
        dec = decompile.get(address)
        require(dec is not None and dec.get("name") == name and dec.get("status") == "OK", f"decompile mismatch {address}", failures)
        tag_row = tags.get(address)
        require(tag_row is not None and tag_row.get("status") == "OK" and "static-reaudit" in tag_row.get("tags", ""), f"tag mismatch {address}", failures)
        require(address in xrefs, f"missing xref row for {address}", failures)


def check_logs_backup_progress(failures: list[str]) -> None:
    expected_logs = {
        "pre-metadata.log": "targets=12 found=12 missing=0",
        "pre-tags.log": "rows=12 missing=0",
        "pre-xrefs.log": "Wrote 191 rows",
        "pre-instructions.log": "Wrote 618 function-body instruction rows",
        "pre-decompile.log": "targets=12 dumped=12 missing=0 failed=0",
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
    require(latest.get("wave") == "Wave1168 unit target-reader tail current-risk review", "latest progress wave mismatch", failures)
    require(latest.get("tag") == "wave1168-unit-target-reader-tail-current-risk-review", "latest progress tag mismatch", failures)
    current = progress.get("post100Reaudit", {}).get("currentRiskRank", {})
    require(current.get("focusedReviewed") == 648, "current focused reviewed mismatch", failures)
    require(current.get("focusedReviewedPercent") == "54.96%", "current focused percent mismatch", failures)
    require(current.get("remainingFocusedAfterLatestReview") == 531, "remaining focused mismatch", failures)


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
        SQUAD_DOC,
        UNIT_DOC,
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

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1168 note mirror mismatch", failures)
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:wave1168-unit-target-reader-tail-current-risk-review")
        == r"py -3 tools\wave1168_unit_target_reader_tail_current_risk_review.py --check",
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
        print("Wave1168 unit target-reader tail probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1168 unit target-reader tail probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
