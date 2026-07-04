#!/usr/bin/env python3
"""Validate Wave966 GeneralVolume active-reader/input read-only review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave966-generalvolume-active-reader-input-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_generalvolume_active_reader_input_review_wave966_2026-05-28.md"
PACKAGE_JSON = ROOT / "package.json"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GENERALVOLUME_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "GeneralVolume.cpp" / "_index.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUALITY_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260528-151637_post_wave966_generalvolume_active_reader_input_review_verified"

EXPECTED_METADATA = {
    "0x00402020": ("CGeneralVolume__ResetCooldownTimestamp", "void __thiscall CGeneralVolume__ResetCooldownTimestamp(void * this, void * activeReaderTarget)"),
    "0x0040b100": ("CGeneralVolume__ctor_base", "void __fastcall CGeneralVolume__ctor_base(void * generalVolume)"),
    "0x0040c720": ("CGeneralVolume__ResetAndSetActiveReader", "void __thiscall CGeneralVolume__ResetAndSetActiveReader(void * this, void * activeReaderTarget)"),
    "0x00412830": ("CGeneralVolume__DisableLinkedEntriesByNameAndReselect", "void __thiscall CGeneralVolume__DisableLinkedEntriesByNameAndReselect(void * this, char * entry_name)"),
    "0x00413660": ("CGeneralVolume__ApplyYawInputByWeaponClass", "void __thiscall CGeneralVolume__ApplyYawInputByWeaponClass(void * this, int axis_input)"),
    "0x004136e0": ("CGeneralVolume__ApplyPitchInputByWeaponClass", "void __thiscall CGeneralVolume__ApplyPitchInputByWeaponClass(void * this, int axis_input)"),
    "0x0040dc60": ("CBattleEngine__DisableVolumeEntryGroupsByNameAndReselect", "void __thiscall CBattleEngine__DisableVolumeEntryGroupsByNameAndReselect(void * this, void * entryName)"),
    "0x00411e70": ("CBattleEngineJetPart__ChangeWeapon", "void __thiscall CBattleEngineJetPart__ChangeWeapon(void * this)"),
}

COMMENT_TOKENS = {
    "0x00402020": ("ret 0x4", "activeReaderTarget", "DAT_00672fd0", "this+0xd4"),
    "0x0040b100": ("CGeneralVolume vtable", "0x005d892c"),
    "0x0040c720": ("CGenericActiveReader__SetReader", "CGeneralVolume__ResetCooldownTimestamp"),
    "0x00412830": ("entry_name", "entry +0xa4", "entry +0x9c", "0x00411e70"),
    "0x00413660": ("0x004d337b", "0xb/0xc", "DAT_005d8cd8", "+0x278"),
    "0x004136e0": ("0x004d3390", "0xb/0xc", "DAT_005d8c90", "+0x280"),
}

UNTAGGED_PRIMARY = {"0x00402020", "0x0040b100", "0x0040c720"}
TAGGED_PRIMARY = {"0x00412830", "0x00413660", "0x004136e0"}

XREF_EVIDENCE = (
    ("0x00402020", "0x0040c73c", "UNCONDITIONAL_CALL"),
    ("0x0040b100", "0x0040af55", "UNCONDITIONAL_CALL"),
    ("0x0040b100", "0x004bcf19", "UNCONDITIONAL_CALL"),
    ("0x0040c720", "0x005d8adc", "DATA"),
    ("0x00412830", "0x0040dc7b", "UNCONDITIONAL_CALL"),
    ("0x00413660", "0x004d337b", "UNCONDITIONAL_CALL"),
    ("0x004136e0", "0x004d3390", "UNCONDITIONAL_CALL"),
    ("0x00411e70", "0x004128cd", "UNCONDITIONAL_CALL"),
)

BODY_EVIDENCE = (
    ("0x00402020", "0x00402025", "MOV", "[ECX + 0xd4]"),
    ("0x0040b100", "0x0040b10d", "MOV", "[EAX]"),
    ("0x0040c720", "0x0040c724", "CALL", "0x00406460"),
    ("0x0040c720", "0x0040c734", "CALL", "0x00401000"),
    ("0x0040c720", "0x0040c73c", "CALL", "0x00402020"),
    ("0x00412830", "0x004128cd", "CALL", "0x00411e70"),
    ("0x00413660", "0x004136ab", "CALL", "0x00409e60"),
    ("0x004136e0", "0x00413728", "CALL", "0x00409e60"),
)

CORE_TOKENS = (
    "Wave966",
    "generalvolume-active-reader-input-review-wave966",
    "0x00402020 CGeneralVolume__ResetCooldownTimestamp",
    "0x0040b100 CGeneralVolume__ctor_base",
    "0x0040c720 CGeneralVolume__ResetAndSetActiveReader",
    "0x00412830 CGeneralVolume__DisableLinkedEntriesByNameAndReselect",
    "0x00413660 CGeneralVolume__ApplyYawInputByWeaponClass",
    "0x004136e0 CGeneralVolume__ApplyPitchInputByWeaponClass",
    "0x005d892c",
    "tag gap documented",
    "340/1408 = 24.15%",
    "6152/6152 = 100.00%",
    BACKUP_PATH,
    "no mutation",
)

OVERCLAIMS = (
    "runtime active-reader behavior proven",
    "runtime selected-weapon behavior proven",
    "runtime yaw behavior proven",
    "runtime pitch behavior proven",
    "layout proven",
    "patching proven",
    "rebuild parity proven",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def norm(address: str) -> str:
    value = (address or "").strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    if value in {"", "<none>", "none"}:
        return value
    return "0x" + value.zfill(8)


def contains_token(text: str, token: str) -> bool:
    stripped = text.replace("`", "")
    return token in text or token in stripped or token.replace("\\", "\\\\") in text or token.replace("\\", "\\\\") in stripped


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


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


def check_counts(failures: list[str]) -> None:
    expected = {
        "pre-metadata.tsv": 13,
        "pre-tags.tsv": 13,
        "pre-xrefs.tsv": 68,
        "pre-instructions.tsv": 2465,
        "pre-body-instructions.tsv": 728,
        "pre-decompile/index.tsv": 13,
        "pre-vtable-slots.tsv": 128,
        "pre-global-xrefs.tsv": 400,
    }
    for relative, count in expected.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == count, f"{relative} row count mismatch: {actual} != {count}", failures)


def check_artifacts(failures: list[str]) -> None:
    metadata = {norm(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    tags = {norm(row["address"]): row for row in read_tsv(BASE / "pre-tags.tsv")}
    decompile = {norm(row["address"]): row for row in read_tsv(BASE / "pre-decompile" / "index.tsv")}
    xrefs = read_tsv(BASE / "pre-xrefs.tsv")
    body = read_tsv(BASE / "pre-body-instructions.tsv")
    vtable = read_tsv(BASE / "pre-vtable-slots.tsv")
    global_xrefs = read_tsv(BASE / "pre-global-xrefs.tsv")

    for address, (name, signature) in EXPECTED_METADATA.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row:
            require(row.get("name") == name, f"name mismatch at {address}: {row.get('name')}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in COMMENT_TOKENS.get(address, ()):
                require(token in row.get("comment", ""), f"missing comment token at {address}: {token}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row for {address}", failures)
        if dec:
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    for address in UNTAGGED_PRIMARY:
        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tag export row for {address}", failures)
        if tag_row:
            require(tag_row.get("tags", "") == "", f"expected documented tag gap at {address}", failures)

    for address in TAGGED_PRIMARY:
        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tag export row for {address}", failures)
        if tag_row:
            actual = set(tag_row.get("tags", "").split(";"))
            for token in ("static-reaudit", "general-volume", "retail-binary-evidence", "signature-corrected"):
                require(token in actual, f"missing tag at {address}: {token}", failures)

    for target, source, ref_type in XREF_EVIDENCE:
        require(
            any(norm(row.get("target_addr", "")) == target and norm(row.get("from_addr", "")) == source and row.get("ref_type") == ref_type for row in xrefs),
            f"missing xref evidence {source} -> {target} {ref_type}",
            failures,
        )

    for function, address, mnemonic, operand in BODY_EVIDENCE:
        require(
            any(
                norm(row.get("function_entry", "")) == function
                and norm(row.get("instruction_addr", "")) == address
                and row.get("mnemonic") == mnemonic
                and operand in row.get("operands", "")
                for row in body
            ),
            f"missing body instruction evidence {function} {address} {mnemonic} {operand}",
            failures,
        )

    require(any(row.get("vtable", "").lower() == "005d892c" and row.get("slot_index") == "56" and row.get("function_name") == "CActor__StickToGround" for row in vtable), "missing CGeneralVolume vtable continuity row", failures)
    require(sum(1 for row in global_xrefs if norm(row.get("target_addr", "")) == "0x00672fd0") == 396, "global time xref count mismatch", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "pre-metadata.log": "targets=13 found=13 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=13 missing=0",
        "pre-xrefs.log": "Wrote 68 rows",
        "pre-instructions.log": "targets=17 missing=0",
        "pre-body-instructions.log": "targets=13 missing=0",
        "pre-decompile.log": "targets=13 dumped=13 missing=0 failed=0",
        "pre-vtable-slots.log": "ExportVtableSlots complete: targets=1 rows=128",
        "pre-global-xrefs.log": "Wrote 400 rows",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6152, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    rows = read_tsv(QUALITY_TSV)
    commented, strict_clean = signature_counts(rows)
    require(len(rows) == 6152, "quality TSV row count mismatch", failures)
    require(commented == 6152, "quality TSV commented count mismatch", failures)
    require(strict_clean == 6152, "strict clean-signature count mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 173542279, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        NOTE,
        CAMPAIGN,
        GHIDRA_REFERENCE,
        FUNCTION_INDEX,
        GENERALVOLUME_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in docs:
        text = read_text(path)
        for token in CORE_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:ghidra-generalvolume-active-reader-input-review-wave966")
        == r"py -3 tools\ghidra_generalvolume_active_reader_input_review_wave966_probe.py --check",
        "missing package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_counts(failures)
    check_artifacts(failures)
    check_logs(failures)
    check_queue_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave966 GeneralVolume active-reader/input probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave966 GeneralVolume active-reader/input probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
