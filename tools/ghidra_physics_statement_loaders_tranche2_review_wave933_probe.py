#!/usr/bin/env python3
"""Validate Wave933 PhysicsScript loader tranche read-only review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave933-physics-statement-loaders-tranche2-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_physics_statement_loaders_tranche2_review_wave933_2026-05-28.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
PHYSICS_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "CPhysicsScriptStatements.cpp.md"
PACKAGE_JSON = ROOT / "package.json"
STATE_FILES = [
    ROOT / "developer_agent_state.json",
    ROOT / "documentation_agent_state.json",
    ROOT / "re_orchestrator_state.json",
]

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260528-003302_post_wave933_physics_statement_loaders_tranche2_review_verified"
SCRIPT_NAME = "test:ghidra-physics-statement-loaders-tranche2-review-wave933"
SCRIPT_VALUE = r"py -3 tools\ghidra_physics_statement_loaders_tranche2_review_wave933_probe.py --check"

TARGETS = {
    "0x004306e0": ("CSpawnerStatement__LoadFromMemBuffer", "void __thiscall CSpawnerStatement__LoadFromMemBuffer(void * this, void * memBuffer)", "CPhysicsScriptStatements__CreateStatementType6"),
    "0x00430800": ("CPhysicsSpawnerValueList__LoadFromMemBuffer", "void __thiscall CPhysicsSpawnerValueList__LoadFromMemBuffer(void * this, void * memBuffer)", "CPhysicsScriptStatements__CreateStatementType6"),
    "0x00430b60": ("CExplosionStatement__LoadFromMemBuffer", "void __thiscall CExplosionStatement__LoadFromMemBuffer(void * this, void * memBuffer)", "CPhysicsScriptStatements__CreateStatementType7"),
    "0x00430c80": ("CPhysicsExplosionValueList__LoadFromMemBuffer", "void __thiscall CPhysicsExplosionValueList__LoadFromMemBuffer(void * this, void * memBuffer)", "CPhysicsScriptStatements__CreateStatementType7"),
    "0x00431050": ("CComponentStatement__LoadFromMemBuffer", "void __thiscall CComponentStatement__LoadFromMemBuffer(void * this, void * memBuffer)", "CPhysicsScriptStatements__CreateStatementType10"),
    "0x00431170": ("CPhysicsComponentValueList__LoadFromMemBuffer", "void __thiscall CPhysicsComponentValueList__LoadFromMemBuffer(void * this, void * memBuffer)", "CPhysicsScriptStatements__CreateStatementType10"),
    "0x004314a0": ("CFeatureStatement__LoadFromMemBuffer", "void __thiscall CFeatureStatement__LoadFromMemBuffer(void * this, void * memBuffer)", "CPhysicsScriptStatements__CreateStatementType8"),
    "0x004315c0": ("CPhysicsFeatureValueList__LoadFromMemBuffer", "void __thiscall CPhysicsFeatureValueList__LoadFromMemBuffer(void * this, void * memBuffer)", "CPhysicsScriptStatements__CreateStatementType8"),
    "0x004318f0": ("CHazardStatement__LoadFromMemBuffer", "void __thiscall CHazardStatement__LoadFromMemBuffer(void * this, void * memBuffer)", "CPhysicsScriptStatements__CreateStatementType9"),
    "0x00431a10": ("CPhysicsHazardValueList__LoadFromMemBuffer", "void __thiscall CPhysicsHazardValueList__LoadFromMemBuffer(void * this, void * memBuffer)", "CPhysicsScriptStatements__CreateStatementType9"),
}

CONTEXT = {
    "0x00439b40": ("CPhysicsScriptStatements__CreateStatementType6", "void * __cdecl CPhysicsScriptStatements__CreateStatementType6(int valueType)"),
    "0x0043a860": ("CPhysicsScriptStatements__CreateStatementType7", "void * __cdecl CPhysicsScriptStatements__CreateStatementType7(int valueType)"),
    "0x0043b990": ("CPhysicsScriptStatements__CreateStatementType8", "void * __cdecl CPhysicsScriptStatements__CreateStatementType8(int valueType)"),
    "0x0043c0b0": ("CPhysicsScriptStatements__CreateStatementType9", "void * __cdecl CPhysicsScriptStatements__CreateStatementType9(int valueType)"),
    "0x0043c500": ("CPhysicsScriptStatements__CreateStatementType10", "void * __cdecl CPhysicsScriptStatements__CreateStatementType10(int valueType)"),
    "0x00430660": ("CSpawnerStatement__GetSerializedSize", "int __fastcall CSpawnerStatement__GetSerializedSize(void * this)"),
    "0x004306b0": ("CPhysicsSpawnerValueList__GetSerializedSize", "int __fastcall CPhysicsSpawnerValueList__GetSerializedSize(void * this)"),
    "0x00430ae0": ("CExplosionStatement__GetSerializedSize", "int __fastcall CExplosionStatement__GetSerializedSize(void * this)"),
    "0x00430b30": ("CPhysicsExplosionValueList__GetSerializedSize", "int __fastcall CPhysicsExplosionValueList__GetSerializedSize(void * this)"),
    "0x00430fd0": ("CComponentStatement__GetSerializedSize", "int __fastcall CComponentStatement__GetSerializedSize(void * this)"),
    "0x00431020": ("CPhysicsComponentValueList__GetSerializedSize", "int __fastcall CPhysicsComponentValueList__GetSerializedSize(void * this)"),
    "0x00431420": ("CFeatureStatement__GetSerializedSize", "int __fastcall CFeatureStatement__GetSerializedSize(void * this)"),
    "0x00431470": ("CPhysicsFeatureValueList__GetSerializedSize", "int __fastcall CPhysicsFeatureValueList__GetSerializedSize(void * this)"),
    "0x00431870": ("CHazardStatement__GetSerializedSize", "int __fastcall CHazardStatement__GetSerializedSize(void * this)"),
    "0x004318c0": ("CPhysicsHazardValueList__GetSerializedSize", "int __fastcall CPhysicsHazardValueList__GetSerializedSize(void * this)"),
    "0x0043e630": ("CFlexArray__SkipBytesFromMemBuffer", "void __cdecl CFlexArray__SkipBytesFromMemBuffer(void * memBuffer, int byteCount)"),
    "0x00430210": ("CRoundStatement__LoadFromMemBuffer", "void __thiscall CRoundStatement__LoadFromMemBuffer(void * this, void * memBuffer)"),
    "0x00430330": ("CPhysicsRoundValueList__LoadFromMemBuffer", "void __thiscall CPhysicsRoundValueList__LoadFromMemBuffer(void * this, void * memBuffer)"),
}

EXPECTED_XREFS = {
    "0x004306e0": {("0x005d9834", "<no_function>", "DATA")},
    "0x00430800": {("0x004307ca", "CSpawnerStatement__LoadFromMemBuffer", "UNCONDITIONAL_CALL"), ("0x004308ac", "CPhysicsSpawnerValueList__LoadFromMemBuffer", "UNCONDITIONAL_CALL")},
    "0x00430b60": {("0x005d9820", "<no_function>", "DATA")},
    "0x00430c80": {("0x00430c4a", "CExplosionStatement__LoadFromMemBuffer", "UNCONDITIONAL_CALL"), ("0x00430d2c", "CPhysicsExplosionValueList__LoadFromMemBuffer", "UNCONDITIONAL_CALL")},
    "0x00431050": {("0x005d980c", "<no_function>", "DATA")},
    "0x00431170": {("0x0043113a", "CComponentStatement__LoadFromMemBuffer", "UNCONDITIONAL_CALL"), ("0x0043121c", "CPhysicsComponentValueList__LoadFromMemBuffer", "UNCONDITIONAL_CALL")},
    "0x004314a0": {("0x005d97f8", "<no_function>", "DATA")},
    "0x004315c0": {("0x0043158a", "CFeatureStatement__LoadFromMemBuffer", "UNCONDITIONAL_CALL"), ("0x0043166c", "CPhysicsFeatureValueList__LoadFromMemBuffer", "UNCONDITIONAL_CALL")},
    "0x004318f0": {("0x005d97e4", "<no_function>", "DATA")},
    "0x00431a10": {("0x004319da", "CHazardStatement__LoadFromMemBuffer", "UNCONDITIONAL_CALL"), ("0x00431abc", "CPhysicsHazardValueList__LoadFromMemBuffer", "UNCONDITIONAL_CALL")},
}

CORE_TOKENS = (
    "Wave933",
    "physics-statement-loaders-tranche2-review-wave933",
    "140/1408 = 9.94%",
    "6113/6113 = 100.00%",
    BACKUP,
    "0x004306e0 CSpawnerStatement__LoadFromMemBuffer",
    "0x00430800 CPhysicsSpawnerValueList__LoadFromMemBuffer",
    "0x00430b60 CExplosionStatement__LoadFromMemBuffer",
    "0x00430c80 CPhysicsExplosionValueList__LoadFromMemBuffer",
    "0x00431050 CComponentStatement__LoadFromMemBuffer",
    "0x00431170 CPhysicsComponentValueList__LoadFromMemBuffer",
    "0x004314a0 CFeatureStatement__LoadFromMemBuffer",
    "0x004315c0 CPhysicsFeatureValueList__LoadFromMemBuffer",
    "0x004318f0 CHazardStatement__LoadFromMemBuffer",
    "0x00431a10 CPhysicsHazardValueList__LoadFromMemBuffer",
    "0x0043e630 CFlexArray__SkipBytesFromMemBuffer",
    "no mutation",
)

OVERCLAIMS = (
    "runtime physics-script behavior proven",
    "serialized physics-script format complete",
    "fully reverse-engineered",
    "rebuild parity proven",
)


def normalize_address(value: str) -> str:
    text = value.strip().lower()
    if text.startswith("0x"):
        text = text[2:]
    return "0x" + text.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8-sig", errors="replace")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def check_counts_and_logs(failures: list[str]) -> None:
    expected_counts = {
        "metadata.tsv": 10,
        "tags.tsv": 10,
        "xrefs.tsv": 25,
        "instructions.tsv": 945,
        "decompile/index.tsv": 10,
        "context-metadata.tsv": 18,
        "context-tags.tsv": 18,
        "context-xrefs.tsv": 31,
        "context-instructions.tsv": 1305,
        "context-decompile/index.tsv": 18,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    expected_logs = {
        "metadata.log": "targets=10 found=10 missing=0",
        "tags.log": "rows=10 missing=0",
        "xrefs.log": "Wrote 25 rows",
        "instructions.log": "Wrote 945 function-body instruction rows",
        "decompile.log": "targets=10 dumped=10 missing=0 failed=0",
        "context-metadata.log": "targets=18 found=18 missing=0",
        "context-tags.log": "rows=18 missing=0",
        "context-xrefs.log": "Wrote 31 rows",
        "context-instructions.log": "Wrote 1305 function-body instruction rows",
        "context-decompile.log": "targets=18 dumped=18 missing=0 failed=0",
    }
    for relative, token in expected_logs.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_metadata_and_tags(relative: str, expected: dict[str, tuple[str, str] | tuple[str, str, str]], failures: list[str]) -> None:
    rows = {normalize_address(row["address"]): row for row in read_tsv(BASE / relative)}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / relative.replace("metadata", "tags"))}
    for address, values in expected.items():
        name, signature = values[0], values[1]
        row = rows.get(address)
        require(row is not None, f"missing metadata {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
            require(row.get("comment", "").strip(), f"missing comment {address}", failures)
        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags {address}", failures)
        if tag_row is not None:
            require(tag_row.get("status") == "OK", f"tag status mismatch {address}", failures)
            require("static-reaudit" in tag_row.get("tags", ""), f"missing static-reaudit tag {address}", failures)


def check_xrefs(failures: list[str]) -> None:
    actual: dict[str, set[tuple[str, str, str]]] = {}
    for row in read_tsv(BASE / "xrefs.tsv"):
        actual.setdefault(normalize_address(row["target_addr"]), set()).add(
            (normalize_address(row["from_addr"]), row["from_function"], row["ref_type"])
        )
    for target, expected in EXPECTED_XREFS.items():
        require(expected.issubset(actual.get(target, set())), f"xref mismatch for {target}", failures)

    context = read_text(BASE / "context-xrefs.tsv")
    for token in (
        "CPhysicsScriptStatements__CreateStatementType6",
        "CPhysicsScriptStatements__CreateStatementType7",
        "CPhysicsScriptStatements__CreateStatementType8",
        "CPhysicsScriptStatements__CreateStatementType9",
        "CPhysicsScriptStatements__CreateStatementType10",
        "CFlexArray__SkipBytesFromMemBuffer",
        "CRoundStatement__LoadFromMemBuffer",
    ):
        require(token in context, f"missing context xref token: {token}", failures)


def check_decompile_tokens(failures: list[str]) -> None:
    for address, (name, _signature, factory) in TARGETS.items():
        path = BASE / "decompile" / f"{address[2:]}_{name}.c"
        text = read_text(path)
        require(text, f"missing decompile file {path.name}", failures)
        tokens = ["CDXMemBuffer__Read", factory, "LoadFromMemBuffer"]
        if "ValueList__LoadFromMemBuffer" not in name:
            tokens.append("0x10c")
        for token in tokens:
            require(token in text, f"missing decompile token {path.name}: {token}", failures)

    for relative, tokens in {
        "context-decompile/0043e630_CFlexArray__SkipBytesFromMemBuffer.c": ("CDXMemBuffer__Read", "byteCount"),
        "context-decompile/00439b40_CPhysicsScriptStatements__CreateStatementType6.c": ("valueType", "0xe"),
        "context-decompile/0043c500_CPhysicsScriptStatements__CreateStatementType10.c": ("valueType", "0x19"),
        "context-decompile/00430210_CRoundStatement__LoadFromMemBuffer.c": ("CPhysicsScriptStatements__CreateStatementType5", "0x10c"),
    }.items():
        text = read_text(BASE / relative)
        require(text, f"missing decompile file {relative}", failures)
        for token in tokens:
            require(token in text, f"missing decompile token {relative}: {token}", failures)


def check_docs_state_backup(failures: list[str]) -> None:
    package = json.loads(read_text(PACKAGE_JSON))
    require(package.get("scripts", {}).get(SCRIPT_NAME) == SCRIPT_VALUE, "missing package script", failures)
    for path in [NOTE, CAMPAIGN, PHYSICS_DOC, *STATE_FILES]:
        text = read_text(path)
        require(text, f"missing doc/state {path.relative_to(ROOT)}", failures)
        for token in CORE_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    backup = json.loads(read_text(BASE / "backup-summary.json"))
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 173247367, "backup bytes mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff mismatch", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_counts_and_logs(failures)
    check_metadata_and_tags("metadata.tsv", TARGETS, failures)
    check_metadata_and_tags("context-metadata.tsv", CONTEXT, failures)
    check_xrefs(failures)
    check_decompile_tokens(failures)
    check_docs_state_backup(failures)

    if failures:
        print("Wave933 PhysicsScript loader tranche review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave933 PhysicsScript loader tranche review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
