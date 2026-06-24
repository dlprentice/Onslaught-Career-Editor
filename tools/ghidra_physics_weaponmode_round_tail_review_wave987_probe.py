#!/usr/bin/env python3
"""Validate Wave987 PhysicsScript weapon-mode / round-tail review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave987-physics-weaponmode-round-tail-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_physics_weaponmode_round_tail_review_wave987_2026-05-31.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
PHYSICS_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "CPhysicsScriptStatements.cpp.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260531-023543_post_wave987_physics_weaponmode_round_tail_review_verified"

TARGETS = {
    "0x004359c0": "CPhysicsWeaponModeValue__dtor_base",
    "0x00435b20": "CPhysicsWeaponModeValue__LoadTwoScalarsFromMemBuffer",
    "0x00437080": "CPhysicsWeaponModeValue__scalar_deleting_dtor",
    "0x004370a0": "CWeaponRound__ApplyToWeaponModeByName",
    "0x004371c0": "CWeaponLaunchSound__ApplyToWeaponModeByName",
    "0x004372b0": "CWeaponPreFireSound__ApplyToWeaponModeByName",
    "0x004373a0": "CWeaponPostFireSound__ApplyToWeaponModeByName",
    "0x00437490": "CPhysicsScriptStatements__CreateStatementType5",
    "0x00437fe0": "CPhysicsRoundValue__SetOwnedAuxStringAt0C",
    "0x00438050": "CPhysicsRoundValue__SetOwnedValueStringAt08",
    "0x004380c0": "CPhysicsRoundValue__dtor_base",
    "0x004380d0": "CPhysicsRoundValue__scalar_deleting_dtor",
    "0x00438400": "CPhysicsRoundValueLeaf__shared_scalar_deleting_dtor",
    "0x00438b40": "CRoundGridOfFear__ApplyToRoundByName",
    "0x004394e0": "CRoundSeek__ApplyToRoundByName",
    "0x00439580": "CRoundSeek__LoadFromMemBuffer",
    "0x004395b0": "CRoundSeek__scalar_deleting_dtor",
    "0x004395d0": "CRoundSeek__dtor_base",
    "0x00439620": "CRoundMesh__ApplyToRoundByName",
    "0x00439710": "CRoundEffect__ApplyToRoundByName",
    "0x00439800": "CRoundWaterEffect__ApplyToRoundByName",
    "0x00439910": "CRoundExplosion__ApplyToRoundByName",
    "0x00439a00": "CRoundTreeCollision__ApplyToRoundByName",
    "0x00439aa0": "CRoundTreeCollision__LoadFromMemBuffer",
    "0x00439ad0": "CRoundTreeCollision__scalar_deleting_dtor",
    "0x00439af0": "CRoundTreeCollision__dtor_base",
}

EXPECTED_SIGNATURES = {
    "0x004359c0": "void __fastcall CPhysicsWeaponModeValue__dtor_base(void * this)",
    "0x00437080": "void * __thiscall CPhysicsWeaponModeValue__scalar_deleting_dtor(void * this, int flags)",
    "0x004380c0": "void __fastcall CPhysicsRoundValue__dtor_base(void * this)",
    "0x004380d0": "void * __thiscall CPhysicsRoundValue__scalar_deleting_dtor(void * this, int flags)",
    "0x00438400": "void * __thiscall CPhysicsRoundValueLeaf__shared_scalar_deleting_dtor(void * this, int flags)",
    "0x004395b0": "void * __thiscall CRoundSeek__scalar_deleting_dtor(void * this, int flags)",
    "0x004395d0": "void __fastcall CRoundSeek__dtor_base(void * this)",
    "0x00439ad0": "void * __thiscall CRoundTreeCollision__scalar_deleting_dtor(void * this, int flags)",
    "0x00439af0": "void __fastcall CRoundTreeCollision__dtor_base(void * this)",
}

REQUIRED_004359C0_TAGS = {
    "destructor",
    "physics-script-wave337",
    "physics-weaponmode-round-tail-review-wave987",
    "supersedes-wave336-ctor-label",
    "tag-corrected",
    "wave987-readback-verified",
    "weapon-mode-value",
}

DOC_TOKENS = (
    "Wave987",
    "physics-weaponmode-round-tail-review-wave987",
    "0x004359c0 CPhysicsWeaponModeValue__dtor_base",
    "0x00437080 CPhysicsWeaponModeValue__scalar_deleting_dtor",
    "0x004380c0 CPhysicsRoundValue__dtor_base",
    "0x004395d0 CRoundSeek__dtor_base",
    "0x00439af0 CRoundTreeCollision__dtor_base",
    "432/1408 = 30.68%",
    "492/1478 = 33.29%",
    "6222/6222 = 100.00%",
    BACKUP_PATH,
)

OVERCLAIMS = (
    "runtime physicsscript behavior proven",
    "runtime physics-script behavior proven",
    "exact source-body identity proven",
    "exact class layouts proven",
    "rebuild parity proven",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig", errors="replace").replace("\x00", "")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def row_by_address(rows: list[dict[str, str]], address: str, field: str = "address") -> dict[str, str] | None:
    target = normalize_address(address)
    for row in rows:
        if normalize_address(row.get(field, "")) == target:
            return row
    return None


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_path_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def check_exports(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 26,
        "pre-tags.tsv": 26,
        "pre-xrefs.tsv": 102,
        "pre-instructions.tsv": 1703,
        "pre-decompile/index.tsv": 26,
        "post-metadata.tsv": 26,
        "post-tags.tsv": 26,
        "post-xrefs.tsv": 102,
        "post-instructions.tsv": 1703,
        "post-decompile/index.tsv": 26,
    }
    for relative, expected in expected_counts.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == expected, f"{relative} row count {actual} != {expected}", failures)

    metadata = read_tsv(BASE / "post-metadata.tsv")
    tags = read_tsv(BASE / "post-tags.tsv")
    xrefs = read_tsv(BASE / "post-xrefs.tsv")
    decompile_index = read_tsv(BASE / "post-decompile" / "index.tsv")

    for address, name in TARGETS.items():
        row = row_by_address(metadata, address)
        require(row is not None, f"metadata missing {address}", failures)
        if row:
            require(row.get("name") == name, f"metadata name mismatch {address}: {row.get('name')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
            if address in EXPECTED_SIGNATURES:
                require(row.get("signature") == EXPECTED_SIGNATURES[address], f"signature mismatch {address}", failures)
            require("unproven" in row.get("comment", "").lower(), f"metadata boundary missing proof caveat {address}", failures)

        tag_row = row_by_address(tags, address)
        require(tag_row is not None and tag_row.get("status") == "OK", f"tag row missing/status mismatch {address}", failures)

        dec = row_by_address(decompile_index, address)
        require(dec is not None, f"decompile index missing {address}", failures)
        if dec:
            require(dec.get("name") == name, f"decompile name mismatch {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch {address}", failures)

    pre_tag = row_by_address(read_tsv(BASE / "pre-tags.tsv"), "0x004359c0")
    post_tag = row_by_address(tags, "0x004359c0")
    require(pre_tag is not None and "constructor" in pre_tag.get("tags", "").split(";"), "pre tag missing stale constructor", failures)
    require(post_tag is not None, "post tag missing 0x004359c0", failures)
    if post_tag:
        actual = set(post_tag.get("tags", "").split(";"))
        require("constructor" not in actual, "post tag still has constructor", failures)
        require(REQUIRED_004359C0_TAGS.issubset(actual), f"post tag missing {REQUIRED_004359C0_TAGS - actual}", failures)

    require(
        any(
            normalize_address(row.get("target_addr", "")) == "0x004359c0"
            and normalize_address(row.get("from_addr", "")) == "0x00437083"
            and row.get("from_function") == "CPhysicsWeaponModeValue__scalar_deleting_dtor"
            for row in xrefs
        ),
        "missing scalar-deleting destructor xref to 0x004359c0",
        failures,
    )
    require(
        not any(
            normalize_address(row.get("target_addr", "")) == "0x004359c0"
            and row.get("from_function") == "CPhysicsScriptStatements__CreateStatementType4"
            for row in xrefs
        ),
        "factory path unexpectedly xrefs 0x004359c0",
        failures,
    )
    for target, caller in (
        ("0x004380c0", "CPhysicsRoundValueLeaf__shared_scalar_deleting_dtor"),
        ("0x004395d0", "CRoundSeek__scalar_deleting_dtor"),
        ("0x00439af0", "CRoundTreeCollision__scalar_deleting_dtor"),
    ):
        require(
            any(normalize_address(row.get("target_addr", "")) == target and row.get("from_function") == caller for row in xrefs),
            f"missing destructor xref {caller} -> {target}",
            failures,
        )

    text_4359 = read_text(BASE / "post-decompile" / "004359c0_CPhysicsWeaponModeValue__dtor_base.c")
    require("PTR_LAB_005da278" in text_4359 or "005da278" in text_4359.lower(), "0x004359c0 decompile missing vtable restore", failures)


def check_logs_backup_docs(failures: list[str]) -> None:
    expected_logs = {
        "apply-dry.log": ("SUMMARY: updated=0 skipped=1 tag_removed=0 would_remove_tag=1 tags_added=3 missing=0 bad=0",),
        "apply.log": ("APPLY_OK: 0x004359c0 removedStaleConstructor=true tagsAdded=3", "SUMMARY: updated=1 skipped=0 tag_removed=1 would_remove_tag=0 tags_added=3 missing=0 bad=0"),
        "apply-final-dry.log": ("SUMMARY: updated=0 skipped=1 tag_removed=0 would_remove_tag=0 tags_added=0 missing=0 bad=0",),
        "post-metadata.log": ("targets=26 found=26 missing=0",),
        "post-tags.log": ("ExportFunctionTagsByAddress complete: rows=26 missing=0",),
        "post-xrefs.log": ("Wrote 102 rows",),
        "post-instructions.log": ("Wrote 1703 function-body instruction rows", "targets=26 missing=0"),
        "post-decompile.log": ("targets=26 dumped=26 missing=0 failed=0",),
    }
    bad_tokens = ("LockException", "ERROR REPORT SCRIPT ERROR", "MISSING:", "BADNAME:", "BADSIG:", "BADTAG:", "BADTAGS:", "FAIL:", "missing=1", "bad=1", "failed=1")
    for relative, tokens in expected_logs.items():
        text = read_text(BASE / relative)
        for token in tokens:
            require(token in text, f"{relative} missing token: {token}", failures)
        for bad in bad_tokens:
            require(bad not in text, f"{relative} contains bad token: {bad}", failures)
        require("REPORT: Save succeeded" in text, f"{relative} missing save succeeded", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes", 0)) == 173837191, "backup byte count mismatch", failures)
    for key in ("missingCount", "extraCount", "diffCount", "hashDiffCount"):
        require(backup.get(key) == 0, f"backup {key} mismatch", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:ghidra-physics-weaponmode-round-tail-review-wave987")
        == r"py -3 tools\ghidra_physics_weaponmode_round_tail_review_wave987_probe.py --check",
        "package script mismatch",
        failures,
    )

    docs = [NOTE, GHIDRA_REFERENCE, CAMPAIGN, FUNCTION_INDEX, FUNCTION_COVERAGE, PHYSICS_DOC, DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE]
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_path_token(text, token), f"{path.relative_to(ROOT)} missing token: {token}", failures)
        lower = text.lower()
        for token in OVERCLAIMS:
            require(token not in lower, f"{path.relative_to(ROOT)} contains overclaim token: {token}", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_exports(failures)
    check_logs_backup_docs(failures)

    if failures:
        print("Wave987 PhysicsScript weapon-mode / round-tail review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Wave987 PhysicsScript weapon-mode / round-tail review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
