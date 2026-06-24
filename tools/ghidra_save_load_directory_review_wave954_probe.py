#!/usr/bin/env python3
"""Validate Wave954 save/load/directory review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave954-save-load-directory-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_save_load_directory_review_wave954_2026-05-28.md"
PACKAGE_JSON = ROOT / "package.json"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FEPLOAD_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FEPLoadGame.cpp" / "_index.md"
FEPSAVE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FEPSaveGame.cpp" / "_index.md"
FEPDIRECTORY_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FEPDirectory.cpp" / "_index.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260528-100717_post_wave954_save_load_directory_review_verified"

EXPECTED_METADATA = {
    "0x00461c40": ("CFEPLoadGame__Init", "bool __thiscall CFEPLoadGame__Init(void * this)"),
    "0x00464620": ("CFEPSaveGame__Init", "bool __thiscall CFEPSaveGame__Init(void * this)"),
    "0x0051ad30": ("CFEPDirectory__RefreshSaveFileList", "void __thiscall CFEPDirectory__RefreshSaveFileList(void * this, int force_refresh)"),
    "0x00514ec0": ("PCPlatform__DeleteSaveFile", "bool __stdcall PCPlatform__DeleteSaveFile(int device, int slot, short * save_name)"),
    "0x00461e20": ("CFEPLoadGame__DoLoad", "void __fastcall CFEPLoadGame__DoLoad(void * this)"),
    "0x00464c50": ("CFEPSaveGame__CreateSave", "void __fastcall CFEPSaveGame__CreateSave(void * this)"),
    "0x0051ac40": ("CFEPDirectory__Process", "void __thiscall CFEPDirectory__Process(void * this, int state)"),
    "0x0051f680": ("CFEPOptions__WriteDefaultOptionsFile", "void __cdecl CFEPOptions__WriteDefaultOptionsFile(void * data, int size)"),
}

DECOMPILE_TOKENS = {
    "00461e20_CFEPLoadGame__DoLoad.c": ("PCPlatform__ReadSaveFile", "CFEPOptions__WriteDefaultOptionsFile"),
    "00464c50_CFEPSaveGame__CreateSave.c": ("EnumerateSaveFiles_Main", "PCPlatform__WriteSaveFile", "PCPlatform__DeleteSaveFile"),
    "0051ac40_CFEPDirectory__Process.c": ("CFEPDirectory__RefreshSaveFileList", "PCPlatform__DeleteSaveFile"),
    "0051ad30_CFEPDirectory__RefreshSaveFileList.c": ("PCPlatform__GetStorageDeviceInfo", "EnumerateSaveFiles_1", "EnumerateSaveFiles_2"),
    "005202d0_CFEPVirtualKeyboard__Process.c": ("CFEPDirectory__RefreshSaveFileList", "CFEPSaveGame__RemovedMUWhinge"),
}

VTABLE_EXPECTED = {
    ("005db800", "2", "CFEPDirectory__Init"),
    ("005db800", "4", "CFEPDirectory__Process"),
    ("005db800", "5", "CFEPDirectory__ButtonPressed"),
    ("005db800", "7", "CFEPDirectory__Render"),
    ("005db920", "0", "CFEPSaveGame__Init"),
    ("005db920", "2", "CFEPSaveGame__Process"),
    ("005db920", "3", "CFEPSaveGame__ButtonPressed"),
    ("005db920", "5", "CFEPSaveGame__Render"),
    ("005db920", "6", "FEPSaveLoad__TransitionNotification"),
    ("005db948", "0", "CFEPLoadGame__Init"),
    ("005db948", "2", "CFEPLoadGame__Process"),
    ("005db948", "3", "CFEPLoadGame__ButtonPressed"),
    ("005db948", "5", "CFEPLoadGame__Render"),
    ("005db948", "6", "FEPSaveLoad__TransitionNotification"),
}

CORE_TOKENS = (
    "Wave954",
    "save-load-directory-review-wave954",
    "0x00461c40 CFEPLoadGame__Init",
    "0x00464620 CFEPSaveGame__Init",
    "0x0051ad30 CFEPDirectory__RefreshSaveFileList",
    "0x00514ec0 PCPlatform__DeleteSaveFile",
    "C:\\dev\\ONSLAUGHT2\\FEPSaveGame.cpp",
    "C:\\dev\\ONSLAUGHT2\\FEPDirectory.cpp",
    "283/1408 = 20.10%",
    "6151/6151 = 100.00%",
    BACKUP_PATH,
    "no mutation",
)

OVERCLAIMS = (
    "runtime save/load behavior proven",
    "runtime filesystem behavior proven",
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
    return "0x" + value.zfill(8)


def contains_token(text: str, token: str) -> bool:
    stripped = text.replace("`", "")
    return token in text or token in stripped or token.replace("\\", "\\\\") in text or token.replace("\\", "\\\\") in stripped


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def check_artifacts(failures: list[str]) -> None:
    counts = {
        "pre-metadata.tsv": 30,
        "pre-tags.tsv": 30,
        "pre-xrefs.tsv": 76,
        "pre-instructions.tsv": 2994,
        "pre-decompile/index.tsv": 30,
        "pre-vtables.tsv": 36,
    }
    for relative, expected in counts.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == expected, f"{relative} row count mismatch: {actual} != {expected}", failures)

    metadata = {norm(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    decompile_index = {norm(row["address"]): row for row in read_tsv(BASE / "pre-decompile" / "index.tsv")}
    for address, (name, signature) in EXPECTED_METADATA.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
        dec = decompile_index.get(address)
        require(dec is not None and dec.get("status") == "OK", f"decompile missing/failed at {address}", failures)

    require("0x00514cc0" not in metadata, "stale 0x00514cc0 target still exported as metadata target", failures)

    strings = {
        "string-00629a78.tsv": r"C:\dev\ONSLAUGHT2\FEPSaveGame.cpp",
        "string-0063fb4c.tsv": r"C:\dev\ONSLAUGHT2\FEPDirectory.cpp",
    }
    for relative, expected in strings.items():
        rows = read_tsv(BASE / relative)
        require(rows and rows[0].get("cstring") == expected, f"{relative} mismatch", failures)

    for filename, tokens in DECOMPILE_TOKENS.items():
        text = read_text(BASE / "pre-decompile" / filename)
        for token in tokens:
            require(token in text, f"missing decompile token in {filename}: {token}", failures)

    vtable_rows = {
        (row.get("vtable", "").lower(), row.get("slot_index", ""), row.get("function_name", ""))
        for row in read_tsv(BASE / "pre-vtables.tsv")
        if row.get("status") == "OK"
    }
    for expected in VTABLE_EXPECTED:
        require(expected in vtable_rows, f"missing vtable row: {expected}", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected_logs = {
        "pre-metadata.log": "targets=30 found=30 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=30 missing=0",
        "pre-xrefs.log": "Wrote 76 rows",
        "pre-instructions.log": "Wrote 2994 function-body instruction rows",
        "pre-decompile.log": "targets=30 dumped=30 missing=0 failed=0",
        "pre-vtables.log": "ExportVtableSlots complete: targets=3 rows=36",
    }
    for relative, token in expected_logs.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR", "Invalid script", "missing=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes", 0)) == 173542279, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs_and_state(failures: list[str]) -> None:
    docs = [NOTE, CAMPAIGN, FUNCTION_INDEX, FEPLOAD_DOC, FEPSAVE_DOC, FEPDIRECTORY_DOC, DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE]
    for path in docs:
        text = read_text(path)
        for token in CORE_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    fepdirectory = read_text(FEPDIRECTORY_DOC)
    require("0x00514cc0` | `PCPlatform__DeleteSaveFile" not in fepdirectory, "stale delete helper address remains in FEPDirectory doc", failures)
    require("0x00514ec0` | `PCPlatform__DeleteSaveFile" in fepdirectory, "correct delete helper address missing in FEPDirectory doc", failures)

    queue = read_json(QUEUE_JSON)
    require(queue.get("totalFunctions") == 6151, "queue total mismatch", failures)
    quality = queue.get("qualitySignals", {})
    require(quality.get("commentlessFunctionCount") == 0, "commentless count mismatch", failures)
    require(quality.get("undefinedSignatureCount") == 0, "undefined count mismatch", failures)
    require(quality.get("paramSignatureCount") == 0, "param_N count mismatch", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:ghidra-save-load-directory-review-wave954")
        == r"py -3 tools\ghidra_save_load_directory_review_wave954_probe.py --check",
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
        print("Wave954 save/load/directory probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave954 save/load/directory probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
