#!/usr/bin/env python3
"""Validate Wave957 CFEPDevelopment world-list review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave957-cfepdevelopment-world-list-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_cfepdevelopment_world_list_review_wave957_2026-05-28.md"
PACKAGE_JSON = ROOT / "package.json"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FEPDEV_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FEPDevelopment.cpp.md"
FRONTEND_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FrontEnd.cpp" / "_index.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260528-111610_post_wave957_cfepdevelopment_world_list_review_verified"

EXPECTED_METADATA = {
    "0x004584d0": ("CFEPDevelopment__Render", "void __thiscall CFEPDevelopment__Render(void * this, float transition, int dest)", "OK"),
    "0x00458ce0": ("CFEPDevelopment__ResolveActiveStorageDevice", "void __thiscall CFEPDevelopment__ResolveActiveStorageDevice(void * this, int unused_refresh_arg)", "OK"),
    "0x00458050": ("CFEPDevelopment__CompareWorldFileNamePtrs", "int __cdecl CFEPDevelopment__CompareWorldFileNamePtrs(char * * left, char * * right)", "OK"),
    "0x00458090": ("CFEPDevelopment__EnumerateWorldFiles", "bool __fastcall CFEPDevelopment__EnumerateWorldFiles(void * this)", "OK"),
    "0x00458100": ("<none>", "<none>", "MISSING"),
    "0x004581e0": ("CFEPDevelopment__Shutdown", "void __fastcall CFEPDevelopment__Shutdown(void * this)", "OK"),
    "0x004583c0": ("CFEPDevelopment__RenderWorldListEntries", "void __fastcall CFEPDevelopment__RenderWorldListEntries(void * this)", "OK"),
    "0x00458710": ("CFEPDevelopment__RefreshWorldListCore", "bool __fastcall CFEPDevelopment__RefreshWorldListCore(void * this)", "OK"),
    "0x004589f0": ("CFEPDevelopment__RefreshWorldList", "void __fastcall CFEPDevelopment__RefreshWorldList(void * this)", "OK"),
    "0x00459580": ("CFEPDevelopment__ScheduleWorldListRefresh", "void __thiscall CFEPDevelopment__ScheduleWorldListRefresh(void * this, int ignored_arg)", "OK"),
    "0x004623e0": ("CFEPMain__DoAction", "void __fastcall CFEPMain__DoAction(void * this)", "OK"),
    "0x00466ae0": ("CFrontEnd__SetPage", "void __thiscall CFrontEnd__SetPage(void * this, int page, int time)", "OK"),
    "0x00468770": ("CFrontEnd__PlaySound", "void __cdecl CFrontEnd__PlaySound(int sound)", "OK"),
}

TAG_EXPECTATIONS = {
    "0x004584d0": {"fepdevelopment", "fepdevelopment-wave384", "rendering", "calling-convention-corrected", "signature-hardened", "comment-hardened", "static-reaudit"},
    "0x00458ce0": {"fepdevelopment", "fepdevelopment-wave384", "storage-device", "calling-convention-corrected", "signature-hardened", "comment-hardened", "static-reaudit"},
    "0x00458050": {"fepdevelopment", "fepdevelopment-wave384", "world-list", "sort-comparator", "function-boundary", "static-reaudit"},
    "0x00458090": {"fepdevelopment", "fepdevelopment-wave384", "world-list", "boundary-corrected", "function-boundary", "static-reaudit"},
    "0x00459580": {"fepdevelopment", "fepdevelopment-wave384", "storage-device", "timer", "calling-convention-corrected", "static-reaudit"},
}

DECOMPILE_TOKENS = {
    "00458050_CFEPDevelopment__CompareWorldFileNamePtrs.c": ("CFEPDevelopment__CompareWorldFileNamePtrs",),
    "00458090_CFEPDevelopment__EnumerateWorldFiles.c": ("FindFirstFileA", "FindNextFileA", "Sort__QuickSortGeneric", "CFEPDevelopment__CompareWorldFileNamePtrs"),
    "004583c0_CFEPDevelopment__RenderWorldListEntries.c": ("CFEPDevelopment__RenderWorldListEntries", "Text__AsciiToWideScratch"),
    "004584d0_CFEPDevelopment__Render.c": ("CFEPDevelopment__RenderWorldListEntries(this)",),
    "00458710_CFEPDevelopment__RefreshWorldListCore.c": ("PCPlatform__GetStorageDeviceInfo", "EnumerateSaveFiles_1", "CFrontEnd__PlaySound(1)", "CFrontEnd__SetPage(&DAT_0089d758,iVar3,0x46)"),
    "004589f0_CFEPDevelopment__RefreshWorldList.c": ("CFEPDevelopment__ResolveActiveStorageDevice(this,0)", "CFEPDevelopment__RefreshWorldListCore(this)"),
    "00458ce0_CFEPDevelopment__ResolveActiveStorageDevice.c": ("unused_refresh_arg", "PCPlatform__GetStorageDeviceInfo", "PCPlatform__GetStorageDeviceCount", "DAT_00677614 = 0"),
    "00459580_CFEPDevelopment__ScheduleWorldListRefresh.c": ("CFEPDevelopment__ResolveActiveStorageDevice(this,0)", "DAT_005d8ba0"),
    "004623e0_CFEPMain__DoAction.c": ("CFEPDevelopment__RefreshWorldList(&DAT_008a1110)", "CFrontEnd__SetPage"),
}

INSTRUCTION_EVIDENCE = (
    ("0x00458090", "0x00458100", "PUSH", "0x62921c", "68 1c 92 62 00"),
    ("0x00458090", "0x004581bd", "PUSH", "0x458050", "68 50 80 45 00"),
    ("0x004584d0", "0x0045851a", "CALL", "0x004583c0", "e8 a1 fe ff ff"),
    ("0x004584d0", "0x00458520", "RET", "0x8", "c2 08 00"),
    ("0x00458ce0", "0x00458df5", "RET", "0x4", "c2 04 00"),
    ("0x004589f0", "0x004589f3", "PUSH", "0x0", "6a 00"),
    ("0x004589f0", "0x004589f5", "CALL", "0x00458ce0", "e8 e6 02 00 00"),
    ("0x00459580", "0x00459583", "PUSH", "0x0", "6a 00"),
    ("0x00459580", "0x00459585", "CALL", "0x00458ce0", "e8 56 f7 ff ff"),
    ("0x00459580", "0x0045959e", "RET", "0x4", "c2 04 00"),
)

XREF_EVIDENCE = (
    ("0x004584d0", "0x005dbad0", "DATA"),
    ("0x00458050", "0x004581bd", "DATA"),
    ("0x00458090", "0x005dbabc", "DATA"),
    ("0x004583c0", "0x0045851a", "UNCONDITIONAL_CALL"),
    ("0x00458ce0", "0x004589f5", "UNCONDITIONAL_CALL"),
    ("0x00458ce0", "0x00459585", "UNCONDITIONAL_CALL"),
    ("0x004589f0", "0x0046242c", "UNCONDITIONAL_CALL"),
    ("0x004589f0", "0x004624ea", "UNCONDITIONAL_CALL"),
    ("0x004589f0", "0x00462556", "UNCONDITIONAL_CALL"),
    ("0x00459580", "0x005db988", "DATA"),
)

CORE_TOKENS = (
    "Wave957",
    "cfepdevelopment-world-list-review-wave957",
    "0x004584d0 CFEPDevelopment__Render",
    "0x00458ce0 CFEPDevelopment__ResolveActiveStorageDevice",
    "0x00458100",
    "0x00458710 CFEPDevelopment__RefreshWorldListCore",
    "mode-qualified",
    "292/1408 = 20.74%",
    "6151/6151 = 100.00%",
    BACKUP_PATH,
    "no mutation",
)

OVERCLAIMS = (
    "runtime development-menu reachability proven",
    "runtime storage-device behavior proven",
    "runtime frontend behavior proven",
    "source-body identity proven",
    "rebuild parity proven",
    "fully reverse-engineered",
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


def check_artifacts(failures: list[str]) -> None:
    counts = {
        "pre-metadata.tsv": 13,
        "pre-tags.tsv": 13,
        "pre-xrefs.tsv": 221,
        "pre-instructions.tsv": 877,
        "pre-decompile/index.tsv": 13,
    }
    for relative, expected in counts.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == expected, f"{relative} row count mismatch: {actual} != {expected}", failures)

    metadata = {norm(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    tags = {norm(row["address"]): row for row in read_tsv(BASE / "pre-tags.tsv")}
    decompile_index = {norm(row["address"]): row for row in read_tsv(BASE / "pre-decompile" / "index.tsv")}

    for address, (name, signature, status) in EXPECTED_METADATA.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == status, f"metadata status mismatch at {address}: {row.get('status')}", failures)
        dec = decompile_index.get(address)
        require(dec is not None and dec.get("status") == status, f"decompile status mismatch at {address}", failures)

    guard_row = next((row for row in read_tsv(BASE / "pre-instructions.tsv") if norm(row.get("target_addr", "")) == "0x00458100"), None)
    require(guard_row is not None and guard_row.get("status", "MISSING") == "MISSING", "missing instruction guard row for stale 0x00458100", failures)

    for address, expected_tags in TAG_EXPECTATIONS.items():
        row = tags.get(address)
        observed = set((row or {}).get("tags", "").split(";"))
        missing = expected_tags - observed
        require(not missing, f"tags missing at {address}: {sorted(missing)}", failures)

    for filename, tokens in DECOMPILE_TOKENS.items():
        text = read_text(BASE / "pre-decompile" / filename)
        for token in tokens:
            require(token in text, f"missing decompile token in {filename}: {token}", failures)

    instructions = read_tsv(BASE / "pre-instructions.tsv")
    for target, instruction, mnemonic, operands, bytes_ in INSTRUCTION_EVIDENCE:
        hit = any(
            norm(row.get("target_addr", "")) == target
            and norm(row.get("instruction_addr", "")) == instruction
            and row.get("mnemonic") == mnemonic
            and row.get("operands") == operands
            and row.get("bytes") == bytes_
            for row in instructions
        )
        require(hit, f"missing instruction evidence: {target} {instruction} {mnemonic} {operands}", failures)

    xrefs = read_tsv(BASE / "pre-xrefs.tsv")
    for target, source, ref_type in XREF_EVIDENCE:
        hit = any(
            norm(row.get("target_addr", "")) == target
            and norm(row.get("from_addr", "")) == source
            and row.get("ref_type") == ref_type
            for row in xrefs
        )
        require(hit, f"missing xref evidence: {source} -> {target} {ref_type}", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected_logs = {
        "pre-metadata.log": "targets=13 found=12 missing=1",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=12 missing=1",
        "pre-xrefs.log": "Wrote 221 rows",
        "pre-instructions.log": "Wrote 877 function-body instruction rows",
        "pre-decompile.log": "targets=13 dumped=12 missing=1 failed=0",
    }
    for relative, token in expected_logs.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR", "Invalid script", "missing=2", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    consult = read_text(BASE / "cursor-consult-wave957.txt")
    require("No structural Ghidra mutations look justified" in consult, "missing Cursor consult mutation boundary", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes", 0)) == 173542279, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs_and_state(failures: list[str]) -> None:
    docs = [
        NOTE,
        CAMPAIGN,
        GHIDRA_REFERENCE,
        FUNCTION_INDEX,
        FEPDEV_DOC,
        FRONTEND_DOC,
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

    queue = read_json(QUEUE_JSON)
    require(queue.get("totalFunctions") == 6151, "queue total mismatch", failures)
    quality = queue.get("qualitySignals", {})
    require(quality.get("commentlessFunctionCount") == 0, "commentless count mismatch", failures)
    require(quality.get("undefinedSignatureCount") == 0, "undefined count mismatch", failures)
    require(quality.get("paramSignatureCount") == 0, "param_N count mismatch", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:ghidra-cfepdevelopment-world-list-review-wave957")
        == r"py -3 tools\ghidra_cfepdevelopment_world_list_review_wave957_probe.py --check",
        "missing package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_docs_and_state(failures)
    if failures:
        print("Wave957 CFEPDevelopment world-list review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave957 CFEPDevelopment world-list review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
