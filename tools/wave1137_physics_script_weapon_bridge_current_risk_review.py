#!/usr/bin/env python3
"""Validate Wave1137 PhysicsScript weapon bridge current-risk artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

import wave1108_current_risk_rank


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1137-physics-script-weapon-bridge-current-risk-review"
FOCUSED_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-focused-candidates.tsv"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1137-physics-script-weapon-bridge-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1137-physics-script-weapon-bridge-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1137_physics_script_weapon_bridge_current_risk_review_2026-06-05.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
MAPPED_SYSTEMS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
PHYSICS_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "CPhysicsScriptStatements.cpp.md"
PHYSICS_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-static-contract.md"
UNIT_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "unit-battleengine-gameplay-static-contract.md"
BATTLEENGINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "BattleEngine.cpp" / "_index.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PROGRESS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"G:\GhidraBackups\BEA_20260605-122130_post_wave1137_physics_script_weapon_bridge_review_verified"
PRIOR_BACKUP = r"G:\GhidraBackups\BEA_20260605-114652_post_wave1136_pausemenu_current_risk_review_verified"

TARGETS = {
    "0x0040d0f0": (
        "CWeaponStatement__UsesBallisticArcNoLocks",
        "int __thiscall CWeaponStatement__UsesBallisticArcNoLocks(void * this, void * weaponStatement)",
        ("projectile gravity", "+0x50/+0x6c", "OID aim/fire"),
        (
            ("0x005096c1", "CUnit__ComputeMinBallisticTravelDistance", "UNCONDITIONAL_CALL"),
            ("0x005099c1", "CUnit__ComputeMaxBallisticTravelDistance", "UNCONDITIONAL_CALL"),
            ("0x00507dd4", "OID__CanFireAtTarget_BallisticArcA", "UNCONDITIONAL_CALL"),
            ("0x0050919a", "OID__UpdateAimTransformAndAttachTargetReader", "UNCONDITIONAL_CALL"),
            ("0x0040caca", "CBattleEngine__GetLaunchPosition", "UNCONDITIONAL_CALL"),
        ),
        (),
    ),
    "0x0042f2b0": (
        "CUnitStatement__LoadFromMemBuffer",
        "void __thiscall CUnitStatement__LoadFromMemBuffer(void * this, void * memBuffer)",
        ("CDXMemBuffer", "CreateStatementType2", "Exact file format"),
        (("0x005d9884", "<no_function>", "DATA"),),
        ("physics-script", "statement-load", "statement-boundary", "static-reaudit"),
    ),
    "0x0042f780": (
        "CWeaponStatement__LoadFromMemBuffer",
        "void __thiscall CWeaponStatement__LoadFromMemBuffer(void * this, void * memBuffer)",
        ("CDXMemBuffer", "CreateStatementType3", "CPhysicsWeaponValueList"),
        (("0x005d985c", "<no_function>", "DATA"),),
        ("physics-script", "statement-load", "statement-boundary", "static-reaudit"),
    ),
    "0x0042f8a0": (
        "CPhysicsWeaponValueList__LoadFromMemBuffer",
        "void __thiscall CPhysicsWeaponValueList__LoadFromMemBuffer(void * this, void * memBuffer)",
        ("CreateStatementType3", "recursively loads", "Exact node layout"),
        (("0x0042f86a", "CWeaponStatement__LoadFromMemBuffer", "UNCONDITIONAL_CALL"),),
        ("physics-script", "statement-load", "value-list", "static-reaudit"),
    ),
    "0x0042fca0": (
        "CWeaponModeStatement__LoadFromMemBuffer",
        "void __thiscall CWeaponModeStatement__LoadFromMemBuffer(void * this, void * memBuffer)",
        ("CDXMemBuffer", "CreateStatementType4", "CPhysicsWeaponModeValueList"),
        (("0x005d9870", "<no_function>", "DATA"),),
        ("physics-script", "statement-load", "statement-boundary", "static-reaudit"),
    ),
    "0x0042fdc0": (
        "CPhysicsWeaponModeValueList__LoadFromMemBuffer",
        "void __thiscall CPhysicsWeaponModeValueList__LoadFromMemBuffer(void * this, void * memBuffer)",
        ("CreateStatementType4", "recursively loads", "Exact node layout"),
        (("0x0042fd8a", "CWeaponModeStatement__LoadFromMemBuffer", "UNCONDITIONAL_CALL"),),
        ("physics-script", "statement-load", "value-list", "static-reaudit"),
    ),
    "0x00435010": (
        "CPhysicsScriptStatements__CreateStatementType4",
        "void * __cdecl CPhysicsScriptStatements__CreateStatementType4(int valueType)",
        ("type-4/weapon-mode value factory", "0x1 through 0x26", "Exact value classes"),
        (("0x0042fd16", "CWeaponModeStatement__LoadFromMemBuffer", "UNCONDITIONAL_CALL"),),
        ("physics-script", "value-factory", "weapon-mode-value", "static-reaudit"),
    ),
    "0x004359c0": (
        "CPhysicsWeaponModeValue__dtor_base",
        "void __fastcall CPhysicsWeaponModeValue__dtor_base(void * this)",
        ("superseding the Wave336 constructor-base wording", "scalar-deleting destructor", "vtable"),
        (("0x00437083", "CPhysicsWeaponModeValue__scalar_deleting_dtor", "UNCONDITIONAL_CALL"),),
        ("physics-script", "destructor", "weapon-mode-value", "static-reaudit"),
    ),
    "0x00437080": (
        "CPhysicsWeaponModeValue__scalar_deleting_dtor",
        "void * __thiscall CPhysicsWeaponModeValue__scalar_deleting_dtor(void * this, int flags)",
        ("flags bit 0", "OID__FreeObject", "returns this"),
        (("0x005d9f94", "<no_function>", "DATA"),),
        ("physics-script", "destructor", "weapon-mode-value", "static-reaudit"),
    ),
    "0x00437fe0": (
        "CPhysicsRoundValue__SetOwnedAuxStringAt0C",
        "void __thiscall CPhysicsRoundValue__SetOwnedAuxStringAt0C(void * this, char * sourceString)",
        ("this+0xc", "0x23c", "owned string"),
        (("0x00437f6a", "<no_function>", "UNCONDITIONAL_CALL"),),
        ("physics-script", "owned-string-copy", "round-value", "static-reaudit"),
    ),
}

CONTEXT_TARGETS = {
    "0x0042e950": "CPhysicsScript__Load",
    "0x0042eb90": "CPhysicsScript__CreateStatement",
    "0x0042f3d0": "CPhysicsUnitValueList__LoadFromMemBuffer",
    "0x0042f570": "CPhysicsScriptStatement__dtor",
    "0x0042f5b0": "CWeaponStatement__CreateWeaponAndRecurse",
    "0x0042f5f0": "CWeaponStatement__Create",
    "0x0042fa40": "CWeaponModeStatement__CreateWeaponModeAndRecurse",
    "0x0042fa80": "CWeaponModeStatement__Create",
    "0x00430210": "CRoundStatement__LoadFromMemBuffer",
    "0x00430330": "CPhysicsRoundValueList__LoadFromMemBuffer",
    "0x00434300": "CPhysicsScriptStatements__CreateStatementType3",
    "0x00437490": "CPhysicsScriptStatements__CreateStatementType5",
    "0x00438050": "CPhysicsRoundValue__SetOwnedValueStringAt08",
}

DOC_TOKENS = (
    "Wave1137",
    "wave1137-physics-script-weapon-bridge-current-risk-review",
    "214/1179 = 18.15%",
    "10 rows",
    "current focused candidates: 1178",
    "live regenerated current focused candidates: 1178",
    "remaining active focused work: 965",
    "PhysicsScript weapon/weapon-mode bridge current-risk cluster",
    "fresh Ghidra export",
    "read-only review",
    "no mutation",
    "0 / 0 / 0",
    BACKUP,
    PRIOR_BACKUP,
)

OVERCLAIM_TOKENS = (
    "runtime weapon behavior proven",
    "runtime weapon-mode behavior proven",
    "runtime physics-script behavior proven",
    "runtime weapon-fire behavior proven",
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


def check_wave1108_accounting(failures: list[str]) -> None:
    counts = wave1108_current_risk_rank.generate()
    require(counts["total"] == 6410, "Wave1108 total mismatch", failures)
    require(counts["risk"] == 6165, "Wave1108 risk mismatch", failures)
    require(counts["focused"] == 1178, "Wave1108 focused mismatch", failures)
    focused = {normalize_address(row["address"]): row for row in read_tsv(FOCUSED_TSV)}
    for address in TARGETS:
        require(address in focused, f"target missing from current focused TSV: {address}", failures)


def check_logs_and_counts(failures: list[str]) -> None:
    expected_logs = {
        "pre-metadata.log": "targets=10 found=10 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=10 missing=0",
        "pre-xrefs.log": "Wrote 57 rows",
        "pre-instructions.log": "Wrote 1048 function-body instruction rows",
        "pre-decompile.log": "targets=10 dumped=10 missing=0 failed=0",
        "context-metadata.log": "targets=13 found=13 missing=0",
        "context-tags.log": "ExportFunctionTagsByAddress complete: rows=13 missing=0",
        "context-xrefs.log": "Wrote 29 rows",
        "context-instructions.log": "Wrote 1407 function-body instruction rows",
        "context-decompile.log": "targets=13 dumped=13 missing=0 failed=0",
    }
    for relative, token in expected_logs.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIG:", "VERIFY_MISSING", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    expected_counts = {
        "pre-metadata.tsv": 10,
        "pre-tags.tsv": 10,
        "pre-xrefs.tsv": 57,
        "pre-instructions.tsv": 1048,
        "pre-decompile/index.tsv": 10,
        "context-metadata.tsv": 13,
        "context-tags.tsv": 13,
        "context-xrefs.tsv": 29,
        "context-instructions.tsv": 1407,
        "context-decompile/index.tsv": 13,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)


def check_target_rows(failures: list[str]) -> None:
    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-decompile" / "index.tsv")}
    xrefs = read_tsv(BASE / "pre-xrefs.tsv")
    context = {normalize_address(row["address"]): row for row in read_tsv(BASE / "context-metadata.tsv")}

    for address, (name, signature, comment_tokens, xref_specs, tag_tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch for {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch for {address}", failures)
            comment = row.get("comment", "")
            for token in comment_tokens:
                require(token in comment, f"missing comment token for {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual = set(filter(None, tag_row.get("tags", "").split(";")))
            for token in tag_tokens:
                require(token in actual, f"missing tag for {address}: {token}", failures)

        dec = decompile.get(address)
        require(dec is not None and dec.get("signature") == signature and dec.get("status") == "OK", f"decompile mismatch for {address}", failures)
        require((BASE / "pre-decompile" / f"{address[2:]}_{name}.c").is_file(), f"missing decompile file for {address}", failures)

        for from_addr, from_function, ref_type in xref_specs:
            require(
                any(
                    normalize_address(row.get("target_addr", "")) == address
                    and normalize_address(row.get("from_addr", "")) == normalize_address(from_addr)
                    and row.get("from_function") == from_function
                    and row.get("ref_type") == ref_type
                    for row in xrefs
                ),
                f"missing xref for {address}: {(from_addr, from_function, ref_type)}",
                failures,
            )

    for address, name in CONTEXT_TARGETS.items():
        row = context.get(address)
        require(row is not None, f"missing context metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"context name mismatch for {address}", failures)


def check_backup(failures: list[str]) -> None:
    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 175967111, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


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
        PHYSICS_DOC,
        PHYSICS_CONTRACT,
        UNIT_CONTRACT,
        BATTLEENGINE_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    address_tokens = tuple(f"{address} {target[0]}" for address, target in TARGETS.items())
    context_tokens = tuple(f"context {address} {name}" for address, name in CONTEXT_TARGETS.items())
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS + address_tokens:
            require(contains_token(text, token), f"missing doc token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad.lower() not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    note_text = read_text(NOTE)
    for token in context_tokens:
        require(contains_token(note_text, token), f"missing context token in note: {token}", failures)

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "wave1137 note mirror mismatch", failures)
    require(read_text(MAPPED_SYSTEMS) == read_text(MAPPED_SYSTEMS_MIRROR), "mapped-systems mirror mismatch", failures)

    for label, data in (("progress", read_json(PROGRESS)), ("progress mirror", read_json(PROGRESS_MIRROR))):
        latest = data["latestWave"]
        current = data["post100Reaudit"]["currentRiskRank"]
        sample = data["latestSample"]
        require(latest["wave"] == "Wave1137 PhysicsScript weapon bridge current-risk review", f"{label} latest wave mismatch", failures)
        require(latest["tag"] == "wave1137-physics-script-weapon-bridge-current-risk-review", f"{label} latest tag mismatch", failures)
        require(latest["backup"] == BACKUP, f"{label} backup mismatch", failures)
        artifact_commit = latest.get("artifactCommit")
        require(
            artifact_commit == "pending Wave1137 artifact commit" or bool(re.fullmatch(r"[0-9a-f]{40}", str(artifact_commit or ""))),
            f"{label} artifact commit mismatch",
            failures,
        )
        require(current["focusedReviewed"] == 214, f"{label} focused reviewed mismatch", failures)
        require(current["focusedCandidates"] == 1179, f"{label} focused denominator mismatch", failures)
        require(current["focusedReviewedPercent"] == "18.15%", f"{label} focused percent mismatch", failures)
        require(current["latestReviewTag"] == "wave1137-physics-script-weapon-bridge-current-risk-review", f"{label} review tag mismatch", failures)
        require(current.get("liveFocusedCandidatesAfterLatestReview") == 1178, f"{label} live focused count mismatch", failures)
        require(current.get("remainingFocusedAfterLatestReview") == 965, f"{label} remaining focused count mismatch", failures)
        require(sample.get("wave") == "Wave1137" and sample.get("ok") == 10 and sample.get("total") == 10, f"{label} sample mismatch", failures)

    package = read_json(PACKAGE_JSON)
    expected_script = r"py -3 tools\wave1137_physics_script_weapon_bridge_current_risk_review.py --check"
    require(package["scripts"].get("test:wave1137-physics-script-weapon-bridge-current-risk-review") == expected_script, "missing package script", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_wave1108_accounting(failures)
    check_logs_and_counts(failures)
    check_target_rows(failures)
    check_backup(failures)
    check_docs_and_state(failures)
    if failures:
        print("Wave1137 PhysicsScript weapon bridge current-risk review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1137 PhysicsScript weapon bridge current-risk review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
