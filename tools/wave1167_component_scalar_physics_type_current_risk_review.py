#!/usr/bin/env python3
"""Validate Wave1167 component scalar / physics type read-only evidence."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1167-component-scalar-physics-type-current-risk-review"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1167-component-scalar-physics-type-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1167-component-scalar-physics-type-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1167_component_scalar_physics_type_current_risk_review_2026-06-06.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PHYSICS_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "CPhysicsScriptStatements.cpp.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
RANK = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"G:\GhidraBackups\BEA_20260606-050232_post_wave1167_component_scalar_physics_type_current_risk_review_verified"

TARGETS = {
    "0x0043ca70": "CComponentScalarD8__ApplyToComponentByName",
    "0x0043cb40": "CComponentScalarDC__ApplyToComponentByName",
    "0x0043cbe0": "CComponentScalarC0__ApplyToComponentByName",
    "0x0043cc80": "CComponentScalar158__ApplyToComponentByName",
    "0x0043cd20": "CComponentScalarB8__ApplyToComponentByName",
    "0x0043cdc0": "CComponentScalarBC__ApplyToComponentByName",
    "0x0043d460": "CComponentScalar160__ApplyToComponentByName",
    "0x0043ddb0": "CPhysicsSeekType__dtor_base",
    "0x0043e300": "CPhysicsBehaviourType__dtor_base",
    "0x0043e3c0": "CPhysicsAlligenceType__dtor_base",
    "0x0043e530": "CPhysicsNavMapType__dtor_base",
    "0x0043e620": "CPhysicsStateType__dtor_base",
}

SIGNATURE_PREFIXES = {
    "0x0043ca70": "void __thiscall CComponentScalarD8__ApplyToComponentByName",
    "0x0043cb40": "void __thiscall CComponentScalarDC__ApplyToComponentByName",
    "0x0043cbe0": "void __thiscall CComponentScalarC0__ApplyToComponentByName",
    "0x0043cc80": "void __thiscall CComponentScalar158__ApplyToComponentByName",
    "0x0043cd20": "void __thiscall CComponentScalarB8__ApplyToComponentByName",
    "0x0043cdc0": "void __thiscall CComponentScalarBC__ApplyToComponentByName",
    "0x0043d460": "void __thiscall CComponentScalar160__ApplyToComponentByName",
    "0x0043ddb0": "void __fastcall CPhysicsSeekType__dtor_base",
    "0x0043e300": "void __fastcall CPhysicsBehaviourType__dtor_base",
    "0x0043e3c0": "void __fastcall CPhysicsAlligenceType__dtor_base",
    "0x0043e530": "void __fastcall CPhysicsNavMapType__dtor_base",
    "0x0043e620": "void __fastcall CPhysicsStateType__dtor_base",
}

COMMENT_TOKENS = {
    "0x0043ca70": ("Wave1039", "DAT_00855400", "+0xd8"),
    "0x0043cb40": ("Wave1039", "DAT_00855400", "+0xdc"),
    "0x0043cbe0": ("Wave1039", "DAT_00855400", "+0xc0"),
    "0x0043cc80": ("Wave1039", "DAT_00855400", "+0x158"),
    "0x0043cd20": ("Wave1039", "DAT_00855400", "+0xb8"),
    "0x0043cdc0": ("Wave1039", "DAT_00855400", "+0xbc"),
    "0x0043d460": ("Wave1039", "DAT_00855400", "+0x160"),
    "0x0043ddb0": ("type-11-seek", "0x005dab20"),
    "0x0043e300": ("type-12-behaviour", "0x005dac58"),
    "0x0043e3c0": ("type-13-alligence", "0x005dac88"),
    "0x0043e530": ("type-14-navmap", "0x005dacc4"),
    "0x0043e620": ("type-15-state", "0x005dacf4"),
}

XREF_EXPECTATIONS = {
    "0x0043ca70": ("0x005daac4", "DATA"),
    "0x0043cb40": ("0x005daab0", "DATA"),
    "0x0043cbe0": ("0x005daa9c", "DATA"),
    "0x0043cc80": ("0x005daa88", "DATA"),
    "0x0043cd20": ("0x005daa38", "DATA"),
    "0x0043cdc0": ("0x005daa10", "DATA"),
    "0x0043d460": ("0x005da998", "DATA"),
    "0x0043ddb0": ("0x0043dd93", "UNCONDITIONAL_CALL"),
    "0x0043e300": ("0x0043e2b3", "UNCONDITIONAL_CALL"),
    "0x0043e3c0": ("0x0043e3a3", "UNCONDITIONAL_CALL"),
    "0x0043e530": ("0x0043e4e3", "UNCONDITIONAL_CALL"),
    "0x0043e620": ("0x0043e5d3", "UNCONDITIONAL_CALL"),
}

DOC_TOKENS = (
    "Wave1167",
    "wave1167-component-scalar-physics-type-current-risk-review",
    "636/1179 = 53.94%",
    "12 component scalar / physics type current-risk rows",
    "current focused candidates: 1178",
    "live regenerated current focused candidates: 1178",
    "remaining active focused work: 543",
    "current risk candidates: 6166",
    "fresh Ghidra export",
    "read-only review",
    "no mutation",
    "no Wave1167-specific Codex consult",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "12 xref rows",
    "472 instruction rows",
    "CComponentScalarD8__ApplyToComponentByName",
    "CComponentScalar160__ApplyToComponentByName",
    "CPhysicsSeekType__dtor_base",
    "CPhysicsStateType__dtor_base",
    "DAT_00855400",
    "0x005daac4",
    "0x005dacf4",
    BACKUP,
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
)

OVERCLAIMS = (
    "runtime physicsscript behavior proven",
    "runtime component scalar behavior proven",
    "serialized file-format completeness proven",
    "mission-script outcomes proven",
    "exact component/type concrete layouts proven",
    "rebuild parity proven",
)


def normalize_address(address: str) -> str:
    value = address.strip().lower()
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


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 12,
        "pre-tags.tsv": 12,
        "pre-xrefs.tsv": 12,
        "pre-instructions.tsv": 472,
        "pre-decompile/index.tsv": 12,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-decompile" / "index.tsv")}
    xrefs = {normalize_address(row["target_addr"]): row for row in read_tsv(BASE / "pre-xrefs.tsv")}

    for address, name in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature", "").startswith(SIGNATURE_PREFIXES[address]), f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            comment = row.get("comment", "")
            for token in COMMENT_TOKENS[address]:
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            tag_text = tag_row.get("tags", "")
            require("static-reaudit" in tag_text, f"missing static-reaudit tag at {address}", failures)
            require("physics-script" in tag_text, f"missing physics-script tag at {address}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row for {address}", failures)
        if dec is not None:
            require(dec.get("name") == name, f"decompile name mismatch at {address}", failures)
            require(dec.get("signature", "").startswith(SIGNATURE_PREFIXES[address]), f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        xref = xrefs.get(address)
        require(xref is not None, f"missing xref row for {address}", failures)
        if xref is not None:
            expected_from, expected_type = XREF_EXPECTATIONS[address]
            require(normalize_address(xref.get("from_addr", "")) == expected_from, f"xref source mismatch at {address}", failures)
            require(xref.get("ref_type") == expected_type, f"xref type mismatch at {address}", failures)


def check_logs_backup_progress(failures: list[str]) -> None:
    expected_logs = {
        "pre-metadata.log": "targets=12 found=12 missing=0",
        "pre-tags.log": "rows=12 missing=0",
        "pre-xrefs.log": "Wrote 12 rows",
        "pre-instructions.log": "Wrote 472 function-body instruction rows",
        "pre-decompile.log": "targets=12 dumped=12 missing=0 failed=0",
    }
    for relative, token in expected_logs.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR", "MISSING:", "FAIL:", "missing=1", "failed=1"):
            require(bad not in text, f"unexpected log failure token in {relative}: {bad}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 176065415 or backup.get("totalBytes") == 176065415.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)

    progress = read_json(PROGRESS)
    latest = progress.get("latestWave", {})
    require(latest.get("wave") == "Wave1167 component scalar / physics type current-risk review", "latest progress wave mismatch", failures)
    require(latest.get("tag") == "wave1167-component-scalar-physics-type-current-risk-review", "latest progress tag mismatch", failures)
    current = progress.get("post100Reaudit", {}).get("currentRiskRank", {})
    require(current.get("focusedReviewed") == 636, "current focused reviewed mismatch", failures)
    require(current.get("focusedReviewedPercent") == "53.94%", "current focused percent mismatch", failures)
    require(current.get("remainingFocusedAfterLatestReview") == 543, "remaining focused mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        NOTE,
        NOTE_MIRROR,
        READINESS,
        PROGRESS,
        PHYSICS_DOC,
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

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1167 note mirror mismatch", failures)
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:wave1167-component-scalar-physics-type-current-risk-review")
        == r"py -3 tools\wave1167_component_scalar_physics_type_current_risk_review.py --check",
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
        print("Wave1167 component scalar / physics type probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1167 component scalar / physics type probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
