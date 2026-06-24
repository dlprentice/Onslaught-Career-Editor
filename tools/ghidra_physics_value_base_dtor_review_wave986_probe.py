#!/usr/bin/env python3
"""Validate Wave986 PhysicsScript value base-destructor read-only review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave986-physics-value-base-dtor-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_physics_value_base_dtor_review_wave986_2026-05-31.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
PHYSICS_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "CPhysicsScriptStatements.cpp.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260531-015646_post_wave986_physics_value_base_dtor_review_verified"

TARGETS = {
    "0x00432cc0": ("CPhysicsUnitValue__dtor_base", "void __fastcall CPhysicsUnitValue__dtor_base(void * this)", "0x005d9e54"),
    "0x004347a0": ("CPhysicsWeaponValue__dtor_base", "void __fastcall CPhysicsWeaponValue__dtor_base(void * this)", "0x005d9f80"),
    "0x0043a040": ("CPhysicsSpawnerValue__dtor_base", "void __fastcall CPhysicsSpawnerValue__dtor_base(void * this)", "0x005da6b0"),
    "0x0043af80": ("CPhysicsExplosionValue__dtor_base", "void __fastcall CPhysicsExplosionValue__dtor_base(void * this)", "0x005da7f0"),
    "0x0043be00": ("CPhysicsFeatureValue__dtor_base", "void __fastcall CPhysicsFeatureValue__dtor_base(void * this)", "0x005da890"),
    "0x0043c310": ("CPhysicsHazardValue__dtor_base", "void __fastcall CPhysicsHazardValue__dtor_base(void * this)", "0x005da8f4"),
    "0x0043dcc0": ("CPhysicsComponentValue__dtor_base", "void __fastcall CPhysicsComponentValue__dtor_base(void * this)", "0x005daae8"),
}

EXPECTED_XREFS = {
    "0x00432cc0": ("0x00434103", "CPhysicsUnitValue__scalar_deleting_dtor"),
    "0x004347a0": ("0x00434a83", "CPhysicsWeaponValue__scalar_deleting_dtor"),
    "0x0043a040": ("0x0043a843", "CPhysicsSpawnerValueLeaf__shared_scalar_deleting_dtor"),
    "0x0043af80": ("0x0043b973", "CPhysicsExplosionValueLeaf__shared_scalar_deleting_dtor"),
    "0x0043be00": ("0x0043bff3", "CPhysicsFeatureValueLeaf__shared_scalar_deleting_dtor"),
    "0x0043c310": ("0x0043c233", "CPhysicsHazardValueLeaf__shared_scalar_deleting_dtor"),
    "0x0043dcc0": ("0x0043d5a3", "CPhysicsComponentValueLeaf__shared_scalar_deleting_dtor"),
}

DOC_TOKENS = (
    "Wave986",
    "physics-value-base-dtor-review-wave986",
    "0x00432cc0 CPhysicsUnitValue__dtor_base",
    "0x004347a0 CPhysicsWeaponValue__dtor_base",
    "0x0043a040 CPhysicsSpawnerValue__dtor_base",
    "0x0043af80 CPhysicsExplosionValue__dtor_base",
    "0x0043be00 CPhysicsFeatureValue__dtor_base",
    "0x0043c310 CPhysicsHazardValue__dtor_base",
    "0x0043dcc0 CPhysicsComponentValue__dtor_base",
    "406/1408 = 28.84%",
    "466/1478 = 31.53%",
    "6222/6222 = 100.00%",
    BACKUP_PATH,
)

OVERCLAIMS = (
    "runtime physics-script behavior proven",
    "runtime physics script behavior proven",
    "exact physicsscript class layouts proven",
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


def hex_tokens(value: str) -> tuple[str, str]:
    numeric = int(value, 16)
    return (f"{numeric:x}", f"{numeric:08x}")


def check_exports(failures: list[str]) -> None:
    expected_counts = {
        "metadata.tsv": 7,
        "tags.tsv": 7,
        "xrefs.tsv": 10,
        "instructions.tsv": 14,
        "decompile/index.tsv": 7,
    }
    for relative, expected in expected_counts.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == expected, f"{relative} row count {actual} != {expected}", failures)

    metadata = read_tsv(BASE / "metadata.tsv")
    tags = read_tsv(BASE / "tags.tsv")
    decompile_index = read_tsv(BASE / "decompile" / "index.tsv")
    instructions = read_tsv(BASE / "instructions.tsv")

    for address, (name, signature, vtable) in TARGETS.items():
        row = row_by_address(metadata, address)
        require(row is not None, f"metadata missing {address}", failures)
        if row:
            require(row.get("name") == name, f"metadata name mismatch {address}: {row.get('name')}", failures)
            require(row.get("signature") == signature, f"metadata signature mismatch {address}", failures)
            require("runtime" in row.get("comment", "").lower(), f"metadata boundary missing runtime caveat {address}", failures)

        tag_row = row_by_address(tags, address)
        require(tag_row is not None and tag_row.get("status") == "OK", f"tag row missing/status mismatch {address}", failures)

        dec = row_by_address(decompile_index, address)
        require(dec is not None, f"decompile index missing {address}", failures)
        if dec:
            require(dec.get("name") == name, f"decompile name mismatch {address}", failures)
            require(dec.get("signature") == signature, f"decompile signature mismatch {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch {address}", failures)

        ins = [row for row in instructions if normalize_address(row.get("target_addr", "")) == normalize_address(address)]
        require(len(ins) == 2, f"instruction count mismatch for {address}", failures)
        vtable_tokens = hex_tokens(vtable)
        require(
            any(
                row.get("mnemonic") == "MOV"
                and any(token in row.get("operands", "").lower() for token in vtable_tokens)
                for row in ins
            ),
            f"missing vtable restore instruction for {address}",
            failures,
        )
        require(any(row.get("mnemonic") == "RET" for row in ins), f"missing RET for {address}", failures)

        decompile_text = read_text(BASE / "decompile" / f"{address[2:]}_{name}.c")
        require(signature in decompile_text, f"decompile file missing signature {address}", failures)
        require(any(token in decompile_text.lower() for token in vtable_tokens), f"decompile file missing vtable {address}", failures)

    xrefs = read_tsv(BASE / "xrefs.tsv")
    for target, (from_addr, from_function) in EXPECTED_XREFS.items():
        require(
            any(
                normalize_address(row.get("target_addr", "")) == normalize_address(target)
                and normalize_address(row.get("from_addr", "")) == normalize_address(from_addr)
                and row.get("from_function") == from_function
                for row in xrefs
            ),
            f"xref mismatch for {target}",
            failures,
        )
    require(
        sum(1 for row in xrefs if normalize_address(row.get("target_addr", "")) == "0x00432cc0" and row.get("from_function", "").startswith("Unwind@")) == 3,
        "unit value dtor unwind xref count mismatch",
        failures,
    )


def check_logs_backup_docs(failures: list[str]) -> None:
    expected_logs = {
        "ExportFunctionMetadataByAddress.log": ("targets=7 found=7 missing=0",),
        "ExportFunctionTagsByAddress.log": ("ExportFunctionTagsByAddress complete: rows=7 missing=0",),
        "ExportXrefsForAddresses.log": ("Wrote 10 rows",),
        "ExportFunctionBodyInstructionsByAddress.log": ("Wrote 14 function-body instruction rows", "targets=7 missing=0"),
        "ExportFunctionsByAddressDecompile.log": ("targets=7 dumped=7 missing=0 failed=0",),
    }
    bad_tokens = ("LockException", "ERROR REPORT SCRIPT ERROR", "MISSING:", "BADNAME:", "BADSIG:", "missing=1", "bad=1", "failed=1")
    for relative, tokens in expected_logs.items():
        text = read_text(BASE / relative)
        for token in tokens:
            require(token in text, f"{relative} missing token: {token}", failures)
        for bad in bad_tokens:
            require(bad not in text, f"{relative} contains bad token: {bad}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes", 0)) == 173837191, "backup byte count mismatch", failures)
    for key in ("missingCount", "extraCount", "diffCount", "hashDiffCount"):
        require(backup.get(key) == 0, f"backup {key} mismatch", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:ghidra-physics-value-base-dtor-review-wave986")
        == r"py -3 tools\ghidra_physics_value_base_dtor_review_wave986_probe.py --check",
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
        print("Wave986 PhysicsScript value base-destructor review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Wave986 PhysicsScript value base-destructor review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
