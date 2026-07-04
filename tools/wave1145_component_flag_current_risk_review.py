#!/usr/bin/env python3
"""Validate Wave1145 component flag current-risk review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1145-component-flag-current-risk-review"
FOCUSED_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-focused-candidates.json"
RISK_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-risk-ranked-functions.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1145-component-flag-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1145-component-flag-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1145_component_flag_current_risk_review_2026-06-05.md"
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

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260605-171711_post_wave1145_component_flag_current_risk_review_verified"
PRIOR_BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260605-165322_post_wave1144_physics_unit_weapon_value_current_risk_review_verified"

TARGETS = {
    "0x0043ce60": ("CComponentFlag124__ApplyToComponentByName", "+0x124", "0x005da9e8"),
    "0x0043cf20": ("CComponentFlag128__ApplyToComponentByName", "+0x128", "0x005da9d4"),
    "0x0043cfe0": ("CComponentFlag12C__ApplyToComponentByName", "+0x12c", "0x005da984"),
    "0x0043d0a0": ("CComponentFlag198__ApplyToComponentByName", "+0x198", "0x005da95c"),
    "0x0043d160": ("CComponentFlag114__ApplyToComponentByName", "+0x114", "0x005da948"),
    "0x0043d220": ("CComponentFlag19C__ApplyToComponentByName", "+0x19c", "0x005da934"),
    "0x0043d2e0": ("CComponentFlag134__ApplyToComponentByName", "+0x134", "0x005da920"),
    "0x0043d3a0": ("CComponentFlag108__ApplyToComponentByName", "+0x108", "0x005da9ac"),
}

COMMON_TAGS = {
    "comment-hardened",
    "component-apply",
    "component-scalar-flag-apply-review-wave1039",
    "component-value-tranche",
    "function-boundary",
    "offset-backed-flag",
    "physics-script",
    "physics-script-wave343",
    "retail-binary-evidence",
    "static-reaudit",
    "wave1039-readback-verified",
    "wave343-normalized",
}

DOC_TOKENS = (
    "Wave1145",
    "wave1145-component-flag-current-risk-review",
    "298/1179 = 25.28%",
    "8 current-risk rows",
    "current focused candidates: 1178",
    "live regenerated current focused candidates: 1178",
    "remaining active focused work: 881",
    "current risk candidates: 6166",
    "PhysicsScript component flag current-risk review",
    "fresh Ghidra export",
    "component flag apply helpers",
    "zero-comparison path",
    "DAT_00855400",
    "0x005d856c",
    "read-only review",
    "no mutation",
    "no Codex subagent",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "CComponentFlag124__ApplyToComponentByName",
    "CComponentFlag128__ApplyToComponentByName",
    "CComponentFlag12C__ApplyToComponentByName",
    "CComponentFlag198__ApplyToComponentByName",
    "CComponentFlag114__ApplyToComponentByName",
    "CComponentFlag19C__ApplyToComponentByName",
    "CComponentFlag134__ApplyToComponentByName",
    "CComponentFlag108__ApplyToComponentByName",
    BACKUP,
    PRIOR_BACKUP,
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
)

OVERCLAIM_TOKENS = (
    "runtime physicsscript behavior proven",
    "runtime component flag behavior proven",
    "serialized file-format completeness proven",
    "mission-script outcomes proven",
    "exact flag meaning proven",
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
        "pre-metadata.tsv": 8,
        "pre-tags.tsv": 8,
        "pre-xrefs.tsv": 8,
        "pre-instructions.tsv": 608,
        "pre-decompile/index.tsv": 8,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-decompile" / "index.tsv")}
    xrefs = {
        (normalize_address(row["from_addr"]), normalize_address(row["target_addr"]), row.get("ref_type", ""))
        for row in read_tsv(BASE / "pre-xrefs.tsv")
    }
    instructions = read_tsv(BASE / "pre-instructions.tsv")
    instruction_text = "\n".join(f"{row.get('mnemonic', '')} {row.get('operands', '')}" for row in instructions).lower()
    compact_instruction_text = instruction_text.replace(" ", "")

    for address, (name, field, data_xref) in TARGETS.items():
        signature = f"void __thiscall {name}(void * this, char * componentName)"
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            comment = row.get("comment", "")
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in ("DAT_00855400", "0x005d856c", field, "zero-comparison path", "1 otherwise"):
                require(token in comment, f"missing comment token at {address}: {token}", failures)

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

        require((data_xref, address, "DATA") in xrefs, f"missing DATA xref {data_xref}->{address}", failures)
        require(field.lower() in compact_instruction_text, f"missing instruction field token: {field}", failures)

    for token in ("0x00855400", "0x005d856c", "FCOMP", "MOV"):
        require(token.lower() in instruction_text, f"missing instruction token: {token}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "pre-metadata.log": "targets=8 found=8 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=8 missing=0",
        "pre-xrefs.log": "Wrote 8 rows",
        "pre-instructions.log": "Wrote 608 function-body instruction rows",
        "pre-decompile.log": "targets=8 dumped=8 missing=0 failed=0",
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
    require(risk.get("candidateFunctions") == 6166, "current risk candidate mismatch", failures)
    require(focused.get("candidateFunctions") == 1178, "focused candidate mismatch", failures)

    progress = read_json(PROGRESS)
    current = progress["post100Reaudit"]["currentRiskRank"]
    require(progress["latestWave"]["wave"] == "Wave1145 component flag current-risk review", "progress latest wave mismatch", failures)
    require(progress["latestWave"]["backup"] == BACKUP, "progress latest backup mismatch", failures)
    require(progress["functionQuality"]["strictCleanSignatureProxy"] == "6411/6411 = 100.00%", "progress strict proxy mismatch", failures)
    require(current["focusedReviewed"] == 298, "progress focused reviewed mismatch", failures)
    require(current["focusedReviewedPercent"] == "25.28%", "progress focused percent mismatch", failures)
    require(current["remainingFocusedAfterLatestReview"] == 881, "progress remaining mismatch", failures)
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

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1145 note mirror mismatch", failures)
    require(read_text(MAPPED_SYSTEMS) == read_text(MAPPED_SYSTEMS_MIRROR), "mapped-systems mirror mismatch", failures)
    require(read_text(PROGRESS) == read_text(PROGRESS_MIRROR), "progress mirror mismatch", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:wave1145-component-flag-current-risk-review") == r"py -3 tools\wave1145_component_flag_current_risk_review.py --check",
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
        print("Wave1145 component flag current-risk probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1145 component flag current-risk probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
