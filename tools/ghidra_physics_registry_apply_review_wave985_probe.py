#!/usr/bin/env python3
"""Validate Wave985 PhysicsScript registry/apply read-only review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave985-physics-registry-apply-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_physics_registry_apply_review_wave985_2026-05-31.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
PHYSICS_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "CPhysicsScriptStatements.cpp.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260531-013725_post_wave985_physics_registry_apply_review_verified"

TARGETS = {
    "0x00430510": ("CSpawnerData__CreateAndRegisterByName", "void __cdecl CSpawnerData__CreateAndRegisterByName(char * name)"),
    "0x004309e0": ("CExplosionStatement__Create", "void __cdecl CExplosionStatement__Create(char * name)"),
    "0x00430e60": ("CComponentStatement__CreateAndRegisterByName", "void __cdecl CComponentStatement__CreateAndRegisterByName(char * name)"),
    "0x00431350": ("CFeatureStatement__CreateAndRegisterByName", "void __cdecl CFeatureStatement__CreateAndRegisterByName(char * name)"),
    "0x004317a0": ("CHazardStatement__CreateAndRegisterByName", "void __cdecl CHazardStatement__CreateAndRegisterByName(char * name)"),
    "0x00439e70": ("CSpawnerBasedOn__ApplyToSpawnerByName", "void __thiscall CSpawnerBasedOn__ApplyToSpawnerByName(void * this, char * spawnerName)"),
    "0x0043a080": ("CSpawnerUnit__ApplyToSpawnerByName", "void __thiscall CSpawnerUnit__ApplyToSpawnerByName(void * this, char * spawnerName)"),
    "0x0043abd0": ("CExplosionBasedOn__ApplyToExplosionByName", "void __thiscall CExplosionBasedOn__ApplyToExplosionByName(void * this, char * explosionName)"),
}

LOG_TOKENS = {
    "ExportFunctionMetadataByAddress.log": ("targets=8 found=8 missing=0",),
    "ExportFunctionTagsByAddress.log": ("ExportFunctionTagsByAddress complete: rows=8 missing=0",),
    "ExportXrefsForAddresses.log": ("Wrote 8 rows",),
    "ExportFunctionBodyInstructionsByAddress.log": ("Wrote 936 function-body instruction rows", "targets=8 missing=0"),
    "ExportFunctionsByAddressDecompile.log": ("targets=8 dumped=8 missing=0 failed=0",),
}

DECOMPILE_TOKENS = {
    "00430510_CSpawnerData__CreateAndRegisterByName.c": ("0x3c", "DAT_008553f4", "CSPtrSet__AddToTail"),
    "004309e0_CExplosionStatement__Create.c": ("0x50", "DAT_008553f8", "CSPtrSet__AddToTail"),
    "00430e60_CComponentStatement__CreateAndRegisterByName.c": ("0x1ac", "DAT_00855400", "CUnitAI__InitDefaults", "Fenrir"),
    "00431350_CFeatureStatement__CreateAndRegisterByName.c": ("0x24", "DAT_00855404", "CSPtrSet__AddToTail"),
    "004317a0_CHazardStatement__CreateAndRegisterByName.c": ("0x1c", "DAT_00855408", "CSPtrSet__AddToTail"),
    "00439e70_CSpawnerBasedOn__ApplyToSpawnerByName.c": ("DAT_008553f4", "spawnerName"),
    "0043a080_CSpawnerUnit__ApplyToSpawnerByName.c": ("DAT_008553f4", "spawnerName"),
    "0043abd0_CExplosionBasedOn__ApplyToExplosionByName.c": ("DAT_008553f8", "explosionName"),
}

DOC_TOKENS = (
    "Wave985",
    "physics-registry-apply-review-wave985",
    "0x00430510 CSpawnerData__CreateAndRegisterByName",
    "0x004309e0 CExplosionStatement__Create",
    "0x00430e60 CComponentStatement__CreateAndRegisterByName",
    "0x00431350 CFeatureStatement__CreateAndRegisterByName",
    "0x004317a0 CHazardStatement__CreateAndRegisterByName",
    "0x00439e70 CSpawnerBasedOn__ApplyToSpawnerByName",
    "0x0043a080 CSpawnerUnit__ApplyToSpawnerByName",
    "0x0043abd0 CExplosionBasedOn__ApplyToExplosionByName",
    "399/1408 = 28.34%",
    "459/1478 = 31.06%",
    "6222/6222 = 100.00%",
    BACKUP_PATH,
)

OVERCLAIMS = (
    "runtime physics-script behavior proven",
    "runtime physics script behavior proven",
    "exact record layouts proven",
    "rebuild parity proven",
    "msl asset behavior proven",
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
        "metadata.tsv": 8,
        "tags.tsv": 8,
        "xrefs.tsv": 8,
        "instructions.tsv": 936,
        "decompile/index.tsv": 8,
    }
    for relative, expected in expected_counts.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == expected, f"{relative} row count {actual} != {expected}", failures)

    metadata = read_tsv(BASE / "metadata.tsv")
    tags = read_tsv(BASE / "tags.tsv")
    decompile_index = read_tsv(BASE / "decompile" / "index.tsv")
    for address, (name, signature) in TARGETS.items():
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

    xrefs = read_tsv(BASE / "xrefs.tsv")
    expected_xrefs = {
        "0x00430510": ("0x004304d8", "CSpawnerStatement__CreateSpawnerAndRecurse"),
        "0x004309e0": ("0x004309a8", "CExplosionStatement__CreateExplosionAndRecurse"),
        "0x00430e60": ("0x00430e28", "CComponentStatement__CreateComponentAndRecurse"),
        "0x00431350": ("0x00431318", "CFeatureStatement__CreateFeatureAndRecurse"),
        "0x004317a0": ("0x00431768", "CHazardStatement__CreateHazardAndRecurse"),
        "0x00439e70": ("0x005da5c4", "<no_function>"),
        "0x0043a080": ("0x005da6a0", "<no_function>"),
        "0x0043abd0": ("0x005da7e0", "<no_function>"),
    }
    for target, (from_addr, from_function) in expected_xrefs.items():
        require(
            any(
                normalize_address(row.get("target_addr", "")) == target
                and normalize_address(row.get("from_addr", "")) == from_addr
                and row.get("from_function") == from_function
                for row in xrefs
            ),
            f"xref mismatch for {target}",
            failures,
        )


def check_logs(failures: list[str]) -> None:
    bad_tokens = ("LockException", "ERROR REPORT SCRIPT ERROR", "MISSING:", "BADNAME:", "BADSIG:", "missing=1", "bad=1", "failed=1")
    for relative, tokens in LOG_TOKENS.items():
        text = read_text(BASE / relative)
        for token in tokens:
            require(token in text, f"{relative} missing token: {token}", failures)
        for bad in bad_tokens:
            require(bad not in text, f"{relative} contains bad token: {bad}", failures)


def check_decompile_backup_docs(failures: list[str]) -> None:
    for filename, tokens in DECOMPILE_TOKENS.items():
        text = read_text(BASE / "decompile" / filename)
        for token in tokens:
            require(token in text, f"{filename} missing token: {token}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes", 0)) == 173837191, "backup byte count mismatch", failures)
    for key in ("missingCount", "extraCount", "diffCount", "hashDiffCount"):
        require(backup.get(key) == 0, f"backup {key} mismatch", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:ghidra-physics-registry-apply-review-wave985")
        == r"py -3 tools\ghidra_physics_registry_apply_review_wave985_probe.py --check",
        "package script mismatch",
        failures,
    )

    docs = [
        NOTE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        PHYSICS_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
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
    check_logs(failures)
    check_decompile_backup_docs(failures)

    if failures:
        print("Wave985 PhysicsScript registry/apply review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Wave985 PhysicsScript registry/apply review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
