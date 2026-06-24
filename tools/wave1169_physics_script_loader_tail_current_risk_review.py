#!/usr/bin/env python3
"""Validate Wave1169 PhysicsScript loader-tail read-only artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1169-physics-script-loader-tail-current-risk-review"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1169-physics-script-loader-tail-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1169-physics-script-loader-tail-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1169_physics_script_loader_tail_current_risk_review_2026-06-06.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
RANK = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
PHYSICS_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-static-contract.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"G:\GhidraBackups\BEA_20260606-055200_post_wave1169_physics_script_loader_tail_current_risk_review_verified"

TARGETS = {
    "0x00430210": ("CRoundStatement__LoadFromMemBuffer", "void __thiscall CRoundStatement__LoadFromMemBuffer"),
    "0x00430330": ("CPhysicsRoundValueList__LoadFromMemBuffer", "void __thiscall CPhysicsRoundValueList__LoadFromMemBuffer"),
    "0x004306e0": ("CSpawnerStatement__LoadFromMemBuffer", "void __thiscall CSpawnerStatement__LoadFromMemBuffer"),
    "0x00430800": ("CPhysicsSpawnerValueList__LoadFromMemBuffer", "void __thiscall CPhysicsSpawnerValueList__LoadFromMemBuffer"),
    "0x00430b60": ("CExplosionStatement__LoadFromMemBuffer", "void __thiscall CExplosionStatement__LoadFromMemBuffer"),
    "0x00430c80": ("CPhysicsExplosionValueList__LoadFromMemBuffer", "void __thiscall CPhysicsExplosionValueList__LoadFromMemBuffer"),
    "0x00431050": ("CComponentStatement__LoadFromMemBuffer", "void __thiscall CComponentStatement__LoadFromMemBuffer"),
    "0x00431170": ("CPhysicsComponentValueList__LoadFromMemBuffer", "void __thiscall CPhysicsComponentValueList__LoadFromMemBuffer"),
    "0x004314a0": ("CFeatureStatement__LoadFromMemBuffer", "void __thiscall CFeatureStatement__LoadFromMemBuffer"),
    "0x004315c0": ("CPhysicsFeatureValueList__LoadFromMemBuffer", "void __thiscall CPhysicsFeatureValueList__LoadFromMemBuffer"),
    "0x004318f0": ("CHazardStatement__LoadFromMemBuffer", "void __thiscall CHazardStatement__LoadFromMemBuffer"),
    "0x00431a10": ("CPhysicsHazardValueList__LoadFromMemBuffer", "void __thiscall CPhysicsHazardValueList__LoadFromMemBuffer"),
}

COMMENT_TOKENS = {
    "0x00430210": ("CRoundStatement", "CPhysicsRoundValueList"),
    "0x00430330": ("CPhysicsRoundValueList", "CreateStatementType5"),
    "0x004306e0": ("CSpawnerStatement", "CPhysicsSpawnerValueList"),
    "0x00430800": ("CPhysicsSpawnerValueList", "CreateStatementType6"),
    "0x00430b60": ("CExplosionStatement", "CPhysicsExplosionValueList"),
    "0x00430c80": ("CPhysicsExplosionValueList", "CreateStatementType7"),
    "0x00431050": ("CComponentStatement", "CPhysicsComponentValueList"),
    "0x00431170": ("CPhysicsComponentValueList", "CreateStatementType10"),
    "0x004314a0": ("CFeatureStatement", "CPhysicsFeatureValueList"),
    "0x004315c0": ("CPhysicsFeatureValueList", "CreateStatementType8"),
    "0x004318f0": ("CHazardStatement", "CPhysicsHazardValueList"),
    "0x00431a10": ("CPhysicsHazardValueList", "CreateStatementType9"),
}

DOC_TOKENS = (
    "Wave1169",
    "wave1169-physics-script-loader-tail-current-risk-review",
    "660/1179 = 55.98%",
    "12 PhysicsScript loader tail current-risk rows",
    "current focused candidates: 1178",
    "live regenerated current focused candidates: 1178",
    "remaining active focused work: 519",
    "current risk candidates: 6166",
    "fresh Ghidra export",
    "read-only review",
    "no mutation",
    "Codex read-only consult used",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "30 xref rows",
    "1134 instruction rows",
    "CRoundStatement__LoadFromMemBuffer",
    "CPhysicsRoundValueList__LoadFromMemBuffer",
    "CSpawnerStatement__LoadFromMemBuffer",
    "CPhysicsSpawnerValueList__LoadFromMemBuffer",
    "CExplosionStatement__LoadFromMemBuffer",
    "CPhysicsExplosionValueList__LoadFromMemBuffer",
    "CComponentStatement__LoadFromMemBuffer",
    "CPhysicsComponentValueList__LoadFromMemBuffer",
    "CFeatureStatement__LoadFromMemBuffer",
    "CPhysicsFeatureValueList__LoadFromMemBuffer",
    "CHazardStatement__LoadFromMemBuffer",
    "CPhysicsHazardValueList__LoadFromMemBuffer",
    "Wave1043",
    "physics-script-static-contract.md",
    BACKUP,
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
)

OVERCLAIMS = (
    "runtime physicsscript behavior proven",
    "serialized file-format completeness proven",
    "runtime round behavior proven",
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
        "pre-xrefs.tsv": 30,
        "pre-instructions.tsv": 1134,
        "pre-decompile/index.tsv": 12,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    decompile = {normalize(row["address"]): row for row in read_tsv(BASE / "pre-decompile" / "index.tsv")}
    tags = {normalize(row["address"]): row for row in read_tsv(BASE / "pre-tags.tsv")}
    xrefs = {normalize(row["target_addr"]): [] for row in read_tsv(BASE / "pre-xrefs.tsv")}
    for row in read_tsv(BASE / "pre-xrefs.tsv"):
        xrefs.setdefault(normalize(row["target_addr"]), []).append(row)

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
        require(tag_row is not None and tag_row.get("status") == "OK" and "physics-script" in tag_row.get("tags", ""), f"tag mismatch {address}", failures)
        require(address in xrefs, f"missing xref row for {address}", failures)


def check_logs_backup_progress(failures: list[str]) -> None:
    expected_logs = {
        "pre-metadata.log": "targets=12 found=12 missing=0",
        "pre-tags.log": "rows=12 missing=0",
        "pre-xrefs.log": "Wrote 30 rows",
        "pre-instructions.log": "Wrote 1134 function-body instruction rows",
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
    require(latest.get("wave") == "Wave1169 PhysicsScript loader tail current-risk review", "latest progress wave mismatch", failures)
    require(latest.get("tag") == "wave1169-physics-script-loader-tail-current-risk-review", "latest progress tag mismatch", failures)
    current = progress.get("post100Reaudit", {}).get("currentRiskRank", {})
    require(current.get("focusedReviewed") == 660, "current focused reviewed mismatch", failures)
    require(current.get("focusedReviewedPercent") == "55.98%", "current focused percent mismatch", failures)
    require(current.get("remainingFocusedAfterLatestReview") == 519, "remaining focused mismatch", failures)


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
        PHYSICS_CONTRACT,
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

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1169 note mirror mismatch", failures)
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:wave1169-physics-script-loader-tail-current-risk-review")
        == r"py -3 tools\wave1169_physics_script_loader_tail_current_risk_review.py --check",
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
        print("Wave1169 PhysicsScript loader-tail probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1169 PhysicsScript loader-tail probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
