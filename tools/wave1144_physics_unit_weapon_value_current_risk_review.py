#!/usr/bin/env python3
"""Validate Wave1144 PhysicsScript unit/weapon value review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1144-physics-unit-weapon-value-current-risk-review"
FOCUSED_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-focused-candidates.json"
RISK_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-risk-ranked-functions.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1144-physics-unit-weapon-value-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1144-physics-unit-weapon-value-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1144_physics_unit_weapon_value_current_risk_review_2026-06-05.md"
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

BACKUP = r"G:\GhidraBackups\BEA_20260605-165322_post_wave1144_physics_unit_weapon_value_current_risk_review_verified"
PRIOR_BACKUP = r"G:\GhidraBackups\BEA_20260605-161338_post_wave1143_physics_statement_dtor_current_risk_review_verified"

TARGETS = {
    "0x00432a50": ("CUnitAlligence__scalar_deleting_dtor", "void * __thiscall CUnitAlligence__scalar_deleting_dtor(void * this, int flags)"),
    "0x00432a70": ("CUnitAlligence__dtor", "void __fastcall CUnitAlligence__dtor(void * this)"),
    "0x00432c00": ("CUnitSoundMaterial__ApplyToUnitData", "void __thiscall CUnitSoundMaterial__ApplyToUnitData(void * this, void * unitData, void * context)"),
    "0x00432c70": ("CUnitMaxLegsLifted__ApplyToUnitData", "void __thiscall CUnitMaxLegsLifted__ApplyToUnitData(void * this, void * unitData, void * context)"),
    "0x00432fa0": ("CUnitNavMap__scalar_deleting_dtor", "void * __thiscall CUnitNavMap__scalar_deleting_dtor(void * this, int flags)"),
    "0x00432fc0": ("CUnitNavMap__dtor", "void __fastcall CUnitNavMap__dtor(void * this)"),
    "0x004330b0": ("CUnitBehaviour__LoadFromMemBuffer", "void __thiscall CUnitBehaviour__LoadFromMemBuffer(void * this, void * memBuffer)"),
    "0x004330e0": ("CUnitBehaviour__scalar_deleting_dtor", "void * __thiscall CUnitBehaviour__scalar_deleting_dtor(void * this, int flags)"),
    "0x00433100": ("CUnitBehaviour__dtor", "void __fastcall CUnitBehaviour__dtor(void * this)"),
    "0x00434f20": ("CWeaponIconName__ApplyToWeaponByName", "void __thiscall CWeaponIconName__ApplyToWeaponByName(void * this, char * weaponName, void * context)"),
    "0x00435840": ("CWeaponBasedOn__ApplyToWeaponByName", "void __thiscall CWeaponBasedOn__ApplyToWeaponByName(void * this, char * weaponName)"),
    "0x0043a860": ("CPhysicsScriptStatements__CreateStatementType7", "void * __cdecl CPhysicsScriptStatements__CreateStatementType7(int valueType)"),
    "0x0043b990": ("CPhysicsScriptStatements__CreateStatementType8", "void * __cdecl CPhysicsScriptStatements__CreateStatementType8(int valueType)"),
    "0x0043c0b0": ("CPhysicsScriptStatements__CreateStatementType9", "void * __cdecl CPhysicsScriptStatements__CreateStatementType9(int valueType)"),
    "0x0043c500": ("CPhysicsScriptStatements__CreateStatementType10", "void * __cdecl CPhysicsScriptStatements__CreateStatementType10(int valueType)"),
}

EXPECTED_XREFS = {
    ("0x005d9d28", "0x00432a50", "DATA"),
    ("0x00432a53", "0x00432a70", "UNCONDITIONAL_CALL"),
    ("0x005d9cdc", "0x00432c00", "DATA"),
    ("0x005d9c14", "0x00432c70", "DATA"),
    ("0x005d9b98", "0x00432fa0", "DATA"),
    ("0x00432fa3", "0x00432fc0", "UNCONDITIONAL_CALL"),
    ("0x005d9d5c", "0x004330b0", "DATA"),
    ("0x005d9d50", "0x004330e0", "DATA"),
    ("0x004330e3", "0x00433100", "UNCONDITIONAL_CALL"),
    ("0x005d9f20", "0x00434f20", "DATA"),
    ("0x005da010", "0x00435840", "DATA"),
    ("0x00430bd6", "0x0043a860", "UNCONDITIONAL_CALL"),
    ("0x00430cac", "0x0043a860", "UNCONDITIONAL_CALL"),
    ("0x00431516", "0x0043b990", "UNCONDITIONAL_CALL"),
    ("0x004315ec", "0x0043b990", "UNCONDITIONAL_CALL"),
    ("0x00431966", "0x0043c0b0", "UNCONDITIONAL_CALL"),
    ("0x00431a3c", "0x0043c0b0", "UNCONDITIONAL_CALL"),
    ("0x004310c6", "0x0043c500", "UNCONDITIONAL_CALL"),
    ("0x0043119c", "0x0043c500", "UNCONDITIONAL_CALL"),
}

COMMENT_TOKENS = {
    "0x00432a50": ("CUnitAlligence", "scalar-deleting destructor", "Alligence spelling is retained"),
    "0x00432a70": ("CUnitAlligence destructor", "+0x8", "CPhysicsUnitValue base vtable"),
    "0x00432c00": ("CUnitSoundMaterial", "+0xe4"),
    "0x00432c70": ("CUnitMaxLegsLifted", "+0x140"),
    "0x00432fa0": ("CUnitNavMap", "scalar-deleting destructor"),
    "0x00432fc0": ("CUnitNavMap destructor", "+0x8", "CPhysicsUnitValue base vtable"),
    "0x004330b0": ("CUnitBehaviour load", "CreateStatementType12", "+0x8"),
    "0x004330e0": ("CUnitBehaviour", "scalar-deleting destructor"),
    "0x00433100": ("CUnitBehaviour destructor", "+0x8", "CPhysicsUnitValue base vtable"),
    "0x00434f20": ("CWeaponIconName", "DAT_008553e8", "icon string"),
    "0x00435840": ("looks up the target weapon", "DAT_008553e8", "copies selected weapon-record fields"),
    "0x0043a860": ("type-7 explosion-value factory", "0x1..0xf", "0x005da6c4"),
    "0x0043b990": ("type-8 feature-value factory", "0x1..0x7", "0x005da804"),
    "0x0043c0b0": ("type-9 hazard-value factory", "0x1..0x4", "0x005da8a4"),
    "0x0043c500": ("type-10 component-value factory", "0x1..0x19 except 0x5", "0x005da908"),
}

DOC_TOKENS = (
    "Wave1144",
    "wave1144-physics-unit-weapon-value-current-risk-review",
    "285/1179 = 24.17%",
    "15 current-risk rows",
    "current focused candidates: 1178",
    "live regenerated current focused candidates: 1178",
    "remaining active focused work: 894",
    "current risk candidates: 6166",
    "PhysicsScript unit/weapon value and factory current-risk review",
    "fresh Ghidra export",
    "unit/weapon value rows",
    "factory type 7-10 rows",
    "read-only review",
    "no mutation",
    "Codex read-only consult",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "CUnitAlligence__scalar_deleting_dtor",
    "CUnitAlligence__dtor",
    "CUnitSoundMaterial__ApplyToUnitData",
    "CUnitMaxLegsLifted__ApplyToUnitData",
    "CUnitNavMap__scalar_deleting_dtor",
    "CUnitNavMap__dtor",
    "CUnitBehaviour__LoadFromMemBuffer",
    "CUnitBehaviour__scalar_deleting_dtor",
    "CUnitBehaviour__dtor",
    "CWeaponIconName__ApplyToWeaponByName",
    "CWeaponBasedOn__ApplyToWeaponByName",
    "CPhysicsScriptStatements__CreateStatementType7",
    "CPhysicsScriptStatements__CreateStatementType8",
    "CPhysicsScriptStatements__CreateStatementType9",
    "CPhysicsScriptStatements__CreateStatementType10",
    BACKUP,
    PRIOR_BACKUP,
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
)

OVERCLAIM_TOKENS = (
    "runtime physicsscript behavior proven",
    "runtime unit/weapon value behavior proven",
    "runtime factory behavior proven",
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
        "pre-metadata.tsv": 15,
        "pre-tags.tsv": 15,
        "pre-xrefs.tsv": 19,
        "pre-instructions.tsv": 1037,
        "pre-decompile/index.tsv": 15,
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

    for address, (name, signature) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in COMMENT_TOKENS[address]:
                require(token in row.get("comment", ""), f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            for tag in ("physics-script", "static-reaudit", "retail-binary-evidence"):
                require(tag in actual_tags, f"missing common tag at {address}: {tag}", failures)
            if "dtor" in name:
                require("destructor" in actual_tags, f"missing destructor tag at {address}", failures)
            if name.startswith("CPhysicsScriptStatements__CreateStatementType"):
                require("value-factory" in actual_tags, f"missing value-factory tag at {address}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    for from_addr, target_addr, ref_type in EXPECTED_XREFS:
        require((from_addr, target_addr, ref_type) in xrefs, f"missing xref: {from_addr}->{target_addr} {ref_type}", failures)

    instruction_text = "\n".join(row.get("operands", "") for row in instructions)
    for token in ("0x008553e8", "0x5da6c4", "0x5da804", "0x5da8a4", "0x5da908"):
        require(token.lower() in instruction_text.lower(), f"missing instruction operand token: {token}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "pre-metadata.log": "targets=15 found=15 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=15 missing=0",
        "pre-xrefs.log": "Wrote 19 rows",
        "pre-instructions.log": "Wrote 1037 function-body instruction rows",
        "pre-decompile.log": "targets=15 dumped=15 missing=0 failed=0",
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
    require(progress["latestWave"]["wave"] == "Wave1144 PhysicsScript unit/weapon value current-risk review", "progress latest wave mismatch", failures)
    require(progress["latestWave"]["backup"] == BACKUP, "progress latest backup mismatch", failures)
    require(progress["functionQuality"]["totalFunctions"] == 6411, "progress function total mismatch", failures)
    require(progress["functionQuality"]["strictCleanSignatureProxy"] == "6411/6411 = 100.00%", "progress strict proxy mismatch", failures)
    require(current["focusedReviewed"] == 285, "progress focused reviewed mismatch", failures)
    require(current["focusedReviewedPercent"] == "24.17%", "progress focused percent mismatch", failures)
    require(current["remainingFocusedAfterLatestReview"] == 894, "progress remaining mismatch", failures)
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

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1144 note mirror mismatch", failures)
    require(read_text(MAPPED_SYSTEMS) == read_text(MAPPED_SYSTEMS_MIRROR), "mapped-systems mirror mismatch", failures)
    require(read_text(PROGRESS) == read_text(PROGRESS_MIRROR), "progress mirror mismatch", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:wave1144-physics-unit-weapon-value-current-risk-review") == r"py -3 tools\wave1144_physics_unit_weapon_value_current_risk_review.py --check",
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
        print("Wave1144 PhysicsScript unit/weapon value current-risk probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1144 PhysicsScript unit/weapon value current-risk probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
