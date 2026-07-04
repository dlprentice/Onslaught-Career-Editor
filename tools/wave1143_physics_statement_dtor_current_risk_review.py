#!/usr/bin/env python3
"""Validate Wave1143 PhysicsScript statement destructor review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1143-physics-statement-dtor-current-risk-review"
FOCUSED_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-focused-candidates.json"
RISK_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-risk-ranked-functions.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1143-physics-statement-dtor-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1143-physics-statement-dtor-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1143_physics_statement_dtor_current_risk_review_2026-06-05.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
MAPPED_SYSTEMS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
WAVE1108_NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
WAVE1108_READINESS = ROOT / "release" / "readiness" / "wave1108_current_risk_rank_2026-06-04.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
PHYSICS_STATEMENTS_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "CPhysicsScriptStatements.cpp.md"
PHYSICS_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-static-contract.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PROGRESS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260605-161338_post_wave1143_physics_statement_dtor_current_risk_review_verified"
PRIOR_BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260605-153716_post_wave1142_mixed_score22_current_risk_review_verified"

TARGETS = {
    "0x0042f510": ("CUnitStatement__dtor", "0x0042f4f3", "CUnitStatement__scalar_deleting_dtor", "0x005d9878"),
    "0x0042f9e0": ("CWeaponStatement__dtor", "0x0042f9c3", "CWeaponStatement__scalar_deleting_dtor", "0x005d9850"),
    "0x0042ff00": ("CWeaponModeStatement__dtor", "0x0042fee3", "CWeaponModeStatement__scalar_deleting_dtor", "0x005d9864"),
    "0x00430470": ("CRoundStatement__dtor", "0x00430453", "CRoundStatement__scalar_deleting_dtor", "0x005d983c"),
    "0x00430940": ("CSpawnerStatement__dtor", "0x00430923", "CSpawnerStatement__scalar_deleting_dtor", "0x005d9828"),
    "0x00430dc0": ("CExplosionStatement__dtor", "0x00430da3", "CExplosionStatement__scalar_deleting_dtor", "0x005d9814"),
    "0x004312b0": ("CComponentStatement__dtor", "0x00431293", "CComponentStatement__scalar_deleting_dtor", "0x005d9800"),
    "0x00431700": ("CFeatureStatement__dtor", "0x004316e3", "CFeatureStatement__scalar_deleting_dtor", "0x005d97ec"),
    "0x00431b50": ("CHazardStatement__dtor", "0x00431b33", "CHazardStatement__scalar_deleting_dtor", "0x005d97d8"),
}

COMMON_TAGS = {
    "destructor",
    "physics-script",
    "statement-tranche",
    "static-reaudit",
    "retail-binary-evidence",
}

COMMON_COMMENT_TOKENS = (
    "Name/signature correction",
    "child pointer at +0x10c",
    "restores the CPhysicsScriptStatement base vtable",
    "Exact layout and runtime lifetime behavior remain unproven",
)

DOC_TOKENS = (
    "Wave1143",
    "wave1143-physics-statement-dtor-current-risk-review",
    "270/1179 = 22.90%",
    "9 current-risk rows",
    "current focused candidates: 1178",
    "live regenerated current focused candidates: 1178",
    "remaining active focused work: 909",
    "current risk candidates: 6166",
    "PhysicsScript statement destructor current-risk review",
    "fresh Ghidra export",
    "statement destructor bodies",
    "scalar-deleting wrapper xrefs",
    "read-only review",
    "no mutation",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "CUnitStatement__dtor",
    "CWeaponStatement__dtor",
    "CWeaponModeStatement__dtor",
    "CRoundStatement__dtor",
    "CSpawnerStatement__dtor",
    "CExplosionStatement__dtor",
    "CComponentStatement__dtor",
    "CFeatureStatement__dtor",
    "CHazardStatement__dtor",
    BACKUP,
    PRIOR_BACKUP,
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
)

OVERCLAIM_TOKENS = (
    "runtime physicsscript behavior proven",
    "runtime statement destruction behavior proven",
    "serialized file-format completeness proven",
    "mission-script outcomes proven",
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


def operand_has_address(operand: str, address: str) -> bool:
    full = address.lower()
    short = "0x" + full[2:].lstrip("0")
    value = (operand or "").lower()
    return full in value or short in value


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
        "pre-xrefs.tsv": 9,
        "pre-instructions.tsv": 207,
        "pre-decompile/index.tsv": 9,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-decompile" / "index.tsv")}
    xrefs = {normalize_address(row["target_addr"]): row for row in read_tsv(BASE / "pre-xrefs.tsv")}
    instruction_rows = read_tsv(BASE / "pre-instructions.tsv")

    for address, (name, from_addr, from_function, derived_vtable) in TARGETS.items():
        signature = f"void __fastcall {name}(void * this)"
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in COMMON_COMMENT_TOKENS:
                require(token in row.get("comment", ""), f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"tags missing at {address}: {COMMON_TAGS - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        xref = xrefs.get(address)
        require(xref is not None, f"missing xref for {address}", failures)
        if xref is not None:
            require(normalize_address(xref.get("from_addr", "")) == from_addr, f"xref source mismatch at {address}", failures)
            require(xref.get("from_function") == from_function, f"xref function mismatch at {address}", failures)
            require(xref.get("ref_type") == "UNCONDITIONAL_CALL", f"xref type mismatch at {address}", failures)

        operands = [
            instruction.get("operands", "")
            for instruction in instruction_rows
            if normalize_address(instruction.get("target_addr", "")) == address
        ]
        require(any(operand_has_address(operand, derived_vtable) for operand in operands), f"missing derived vtable store at {address}: {derived_vtable}", failures)
        require(any(operand_has_address(operand, "0x005d9894") for operand in operands), f"missing base vtable restore at {address}", failures)
        require(
            any(
                normalize_address(instruction.get("target_addr", "")) == address
                and instruction.get("mnemonic") == "MOV"
                and instruction.get("operands") == "ECX, dword ptr [ESI + 0x10c]"
                for instruction in instruction_rows
            ),
            f"missing child pointer load at {address}",
            failures,
        )
        require(
            any(
                normalize_address(instruction.get("target_addr", "")) == address
                and instruction.get("mnemonic") == "CALL"
                and instruction.get("operands") == "dword ptr [EAX]"
                for instruction in instruction_rows
            ),
            f"missing child slot call at {address}",
            failures,
        )


def check_logs(failures: list[str]) -> None:
    expected = {
        "pre-metadata.log": "targets=9 found=9 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=9 missing=0",
        "pre-xrefs.log": "Wrote 9 rows",
        "pre-instructions.log": "Wrote 207 function-body instruction rows",
        "pre-decompile.log": "targets=9 dumped=9 missing=0 failed=0",
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
    require(progress["latestWave"]["wave"] == "Wave1143 PhysicsScript statement destructor current-risk review", "progress latest wave mismatch", failures)
    require(progress["latestWave"]["backup"] == BACKUP, "progress latest backup mismatch", failures)
    require(progress["functionQuality"]["totalFunctions"] == 6411, "progress function total mismatch", failures)
    require(progress["functionQuality"]["strictCleanSignatureProxy"] == "6411/6411 = 100.00%", "progress strict proxy mismatch", failures)
    require(current["focusedReviewed"] == 270, "progress focused reviewed mismatch", failures)
    require(current["focusedReviewedPercent"] == "22.90%", "progress focused percent mismatch", failures)
    require(current["remainingFocusedAfterLatestReview"] == 909, "progress remaining mismatch", failures)
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
        WAVE1108_NOTE,
        WAVE1108_READINESS,
        BINARY_INDEX,
        RE_INDEX,
        FUNCTION_COVERAGE,
        FUNCTION_INDEX,
        PHYSICS_STATEMENTS_DOC,
        PHYSICS_CONTRACT,
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
        lower = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:wave1143-physics-statement-dtor-current-risk-review") == r"py -3 tools\wave1143_physics_statement_dtor_current_risk_review.py --check",
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
        print("Wave1143 PhysicsScript statement destructor current-risk probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1143 PhysicsScript statement destructor current-risk probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
