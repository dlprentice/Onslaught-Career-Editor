#!/usr/bin/env python3
"""Validate Wave999 FEPBEConfig helper read-only review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave999-fepbeconfig-helper-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_fepbeconfig_helper_review_wave999_2026-05-31.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FEP_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FEPBEConfig.cpp" / "_index.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260531-094628_post_wave999_fepbeconfig_helper_review_verified"

TARGETS = {
    "0x0044eab0": ("CFEPMultiplayerStart__GetConfigIdByIndex", "int __cdecl CFEPMultiplayerStart__GetConfigIdByIndex(int config_index)"),
    "0x0044eb30": ("CFEPMultiplayerStart__SetConfigDescriptionByIndex", "void __cdecl CFEPMultiplayerStart__SetConfigDescriptionByIndex(int config_index)"),
    "0x0044ecf0": ("CFEPMultiplayerStart__GetConfigCount", "int __cdecl CFEPMultiplayerStart__GetConfigCount(void)"),
    "0x0044f030": ("CFEPBEConfig__GetWeaponProperty", "int __cdecl CFEPBEConfig__GetWeaponProperty(void * config, int weapon_index, int property_index)"),
    "0x0044f300": ("CFEPBEConfig__GetWeaponPropertyAlt", "int __cdecl CFEPBEConfig__GetWeaponPropertyAlt(void * config, int weapon_index, int property_index)"),
    "0x0044f530": ("CFEPBEConfig__PlayWeaponSound", "void __cdecl CFEPBEConfig__PlayWeaponSound(void * config, int weapon_index)"),
    "0x0044f830": ("CFEPBEConfig__PlayWeaponSoundAlt", "void __cdecl CFEPBEConfig__PlayWeaponSoundAlt(void * config, int weapon_index)"),
    "0x00450090": ("CFEPBEConfig__ButtonPressed", "void __thiscall CFEPBEConfig__ButtonPressed(void * this, int button, int player_index)"),
    "0x004505b0": ("CFEPBEConfig__Render", "void __thiscall CFEPBEConfig__Render(void * this, float transition, int dest)"),
    "0x00451930": ("CFEPBEConfig__FindEntryByName", "void * __cdecl CFEPBEConfig__FindEntryByName(char * entry_name)"),
    "0x00451a40": ("FEPBEConfig__FindSelectedEntryByGlobalId", "int * __fastcall FEPBEConfig__FindSelectedEntryByGlobalId(void * list_state)"),
}

COMMENT_TOKENS = {
    "0x0044eb30": ("Unknown Configuration", "maps type ids"),
    "0x0044f530": ("Unknown Weapon", "weapon-record field +0x0f"),
    "0x0044f830": ("alternate weapon-name list", "+0x50/+0x58"),
    "0x00451a40": ("Owner correction from CUnitAI to FEPBEConfig", "DAT_0089d94c"),
}

DOC_TOKENS = (
    "Wave999",
    "fepbeconfig-helper-review-wave999",
    "0x0044eb30 CFEPMultiplayerStart__SetConfigDescriptionByIndex",
    "0x0044f530 CFEPBEConfig__PlayWeaponSound",
    "0x0044f830 CFEPBEConfig__PlayWeaponSoundAlt",
    "0x00451a40 FEPBEConfig__FindSelectedEntryByGlobalId",
    "467/1408 = 33.17%",
    "596/1478 = 40.32%",
    "343/500 = 68.60%",
    "6222/6222 = 100.00%",
    BACKUP_PATH,
)

OVERCLAIMS = (
    "runtime frontend behavior proven",
    "runtime audio behavior proven",
    "runtime text presentation proven",
    "exact source identity proven",
    "exact layout proven",
    "rebuild parity proven",
)

EXPECTED_LOG_TOKENS = {
    "pre-metadata.log": ("targets=11 found=11 missing=0", "REPORT: Save succeeded"),
    "pre-tags.log": ("ExportFunctionTagsByAddress complete: rows=11 missing=0", "REPORT: Save succeeded"),
    "pre-xrefs.log": ("Wrote 31 rows", "REPORT: Save succeeded"),
    "pre-instructions.log": ("Wrote 3001 function-body instruction rows", "targets=11 missing=0", "REPORT: Save succeeded"),
    "pre-decompile.log": ("targets=11 dumped=11 missing=0 failed=0", "REPORT: Save succeeded"),
}


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


def contains_token(text: str, token: str) -> bool:
    if token in text or token.replace("\\", "\\\\") in text or token.replace("\\", "\\\\\\\\") in text:
        return True
    previous = None
    current = text
    token_current = token
    while previous != current:
        previous = current
        current = current.replace("\\\\\\\\", "\\").replace("\\\\", "\\")
        token_current = token_current.replace("\\\\\\\\", "\\").replace("\\\\", "\\")
    return token_current in current


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 11,
        "pre-tags.tsv": 11,
        "pre-xrefs.tsv": 31,
        "pre-instructions.tsv": 3001,
        "pre-decompile/index.tsv": 11,
    }
    for relative, expected in expected_counts.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == expected, f"{relative} row count {actual} != {expected}", failures)

    metadata = read_tsv(BASE / "pre-metadata.tsv")
    tags = read_tsv(BASE / "pre-tags.tsv")
    decompile_index = read_tsv(BASE / "pre-decompile" / "index.tsv")

    for address, (name, signature) in TARGETS.items():
        row = row_by_address(metadata, address)
        require(row is not None, f"metadata missing {address}", failures)
        if row:
            require(row.get("name") == name, f"metadata name mismatch {address}", failures)
            require(row.get("signature") == signature, f"metadata signature mismatch {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
            require(row.get("comment", "").strip() != "", f"comment missing {address}", failures)
            for token in COMMENT_TOKENS.get(address, ("Static retail evidence only",)):
                require(token in row.get("comment", ""), f"comment token missing {address}: {token}", failures)

        dec = row_by_address(decompile_index, address)
        require(dec is not None, f"decompile missing {address}", failures)
        if dec:
            require(dec.get("name") == name, f"decompile name mismatch {address}", failures)
            require(dec.get("signature") == signature, f"decompile signature mismatch {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch {address}", failures)

        tag_row = row_by_address(tags, address)
        require(tag_row is not None, f"tags missing {address}", failures)
        if tag_row:
            actual_tags = set(filter(None, tag_row.get("tags", "").split(";")))
            require("static-reaudit" in actual_tags, f"missing static-reaudit tag {address}", failures)
            require("retail-binary-evidence" in actual_tags, f"missing retail-binary-evidence tag {address}", failures)

    xrefs = read_tsv(BASE / "pre-xrefs.tsv")
    expected_xrefs = (
        ("0x0044eb30", "0x0051efa8", "CFEPMultiplayerStart__Render"),
        ("0x0044f530", "0x00451044", "CFEPBEConfig__Render"),
        ("0x0044f830", "0x0045117f", "CFEPBEConfig__Render"),
        ("0x00451a40", "0x00450da1", "CFEPBEConfig__Render"),
        ("0x00451a40", "0x0045139b", "CFEPBEConfig__Render"),
        ("0x00451a40", "0x00451638", "CFEPBEConfig__Render"),
    )
    for target, source, function_name in expected_xrefs:
        require(
            any(
                normalize_address(row.get("target_addr", "")) == target
                and normalize_address(row.get("from_addr", "")) == source
                and row.get("from_function") == function_name
                and row.get("ref_type") == "UNCONDITIONAL_CALL"
                for row in xrefs
            ),
            f"missing xref {source} -> {target} {function_name}",
            failures,
        )

    instructions = read_tsv(BASE / "pre-instructions.tsv")
    instruction_checks = (
        ("0x0044eb30", "0x0044eb4c", "MOV", "EDX, dword ptr [0x0089d94c]"),
        ("0x0044eb30", "0x0044ebf1", "MOV", "EAX, dword ptr [EDI + 0xa8]"),
        ("0x0044f530", "0x0044f6a1", "MOV", "EBP, dword ptr [EDI + 0x60]"),
        ("0x0044f530", "0x0044f6c0", "MOV", "ECX, dword ptr [0x008553e8]"),
        ("0x0044f830", "0x0044f999", "MOV", "EAX, dword ptr [EDI + 0x50]"),
        ("0x0044f830", "0x0044f9a0", "MOV", "dword ptr [EDI + 0x58], EAX"),
        ("0x00451a40", "0x00451a55", "MOV", "EDX, dword ptr [0x0089d94c]"),
    )
    for target, instr_addr, mnemonic, operand in instruction_checks:
        require(
            any(
                normalize_address(row.get("target_addr", "")) == target
                and row.get("instruction_addr") == instr_addr
                and row.get("mnemonic") == mnemonic
                and row.get("operands") == operand
                for row in instructions
            ),
            f"missing instruction {target} {instr_addr} {mnemonic} {operand}",
            failures,
        )


def check_logs_and_backup(failures: list[str]) -> None:
    for relative, tokens in EXPECTED_LOG_TOKENS.items():
        text = read_text(BASE / relative)
        for token in tokens:
            require(token in text, f"missing log token {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR", "FAIL:", "missing=1", "failed=1"):
            require(bad not in text, f"bad log token {relative}: {bad}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 173869959 or backup.get("totalBytes") == 173869959.0, "backup bytes mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = (NOTE, GHIDRA_REFERENCE, CAMPAIGN, FUNCTION_COVERAGE, FEP_DOC, DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE)
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing doc token {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lowered, f"overclaim token {path.relative_to(ROOT)}: {bad}", failures)

    function_index_text = read_text(FUNCTION_INDEX)
    for token in ("Wave999", "FEPBEConfig.cpp", "0x0044eb30", "0x00451a40", BACKUP_PATH):
        require(contains_token(function_index_text, token), f"missing doc token {FUNCTION_INDEX.relative_to(ROOT)}: {token}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-fepbeconfig-helper-review-wave999")
        == r"py -3 tools\ghidra_fepbeconfig_helper_review_wave999_probe.py --check",
        "missing Wave999 package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave999-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 999 --check",
        "missing Wave999 recheck script",
        failures,
    )

    queue = read_json(QUEUE_JSON)
    require(queue.get("totalFunctions") == 6222, "queue total mismatch", failures)
    quality = queue.get("qualitySignals", {})
    require(quality.get("commentlessFunctionCount") == 0, "queue commentless mismatch", failures)
    require(quality.get("undefinedSignatureCount") == 0, "queue undefined mismatch", failures)
    require(quality.get("paramSignatureCount") == 0, "queue param mismatch", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave999 FEPBEConfig helper review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave999 FEPBEConfig helper review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
