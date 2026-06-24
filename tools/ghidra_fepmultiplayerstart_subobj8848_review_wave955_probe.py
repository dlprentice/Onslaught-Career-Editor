#!/usr/bin/env python3
"""Validate Wave955 FEPMultiplayerStart SubObj8848 review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave955-fepmultiplayerstart-subobj8848-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_fepmultiplayerstart_subobj8848_review_wave955_2026-05-28.md"
PACKAGE_JSON = ROOT / "package.json"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FEPMULTI_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FEPMultiplayerStart.cpp" / "_index.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260528-103114_post_wave955_fepmultiplayerstart_subobj8848_review_verified"

EXPECTED_METADATA = {
    "0x00459920": ("CFEPMultiplayerStart__SubObj8848__ctor", "void * __thiscall CFEPMultiplayerStart__SubObj8848__ctor(void * this)"),
    "0x004599a0": ("CFEPMultiplayerStart__SubObj8848__Init", "int __thiscall CFEPMultiplayerStart__SubObj8848__Init(void * this)"),
    "0x00459e50": ("CFEPMultiplayerStart__SubObj8848__RenderPreCommon", "void __stdcall CFEPMultiplayerStart__SubObj8848__RenderPreCommon(float transition, int dest)"),
    "0x00459810": ("CFEPMultiplayerStart__SubObj39B8__QueuePageId", "void __thiscall CFEPMultiplayerStart__SubObj39B8__QueuePageId(void * this, int page_id)"),
    "0x00459a60": ("CFEPMultiplayerStart__SubObj8848__ActiveNotification", "void __thiscall CFEPMultiplayerStart__SubObj8848__ActiveNotification(void * this, int from_page)"),
    "0x00459aa0": ("CFEPMultiplayerStart__SubObj8848__TransitionNotification", "void __thiscall CFEPMultiplayerStart__SubObj8848__TransitionNotification(void * this, int from_page)"),
    "0x00459b00": ("CFEPMultiplayerStart__SubObj8848__Process", "void __thiscall CFEPMultiplayerStart__SubObj8848__Process(void * this, int menu_state)"),
    "0x00459c10": ("CFEPMultiplayerStart__SubObj8848__ButtonPressed", "void __thiscall CFEPMultiplayerStart__SubObj8848__ButtonPressed(void * this, int button)"),
    "0x00459ee0": ("CFEPMultiplayerStart__SubObj8848__Render", "void __thiscall CFEPMultiplayerStart__SubObj8848__Render(void * this, float transition, int dest)"),
    "0x00465f10": ("CFEPMultiplayerStart__ctor", "void * __fastcall CFEPMultiplayerStart__ctor(void * this)"),
    "0x004623e0": ("CFEPMain__DoAction", "void __fastcall CFEPMain__DoAction(void * this)"),
    "0x00466ae0": ("CFrontEnd__SetPage", "void __thiscall CFrontEnd__SetPage(void * this, int page, int time)"),
    "0x00452ce0": ("CFrontEnd__RenderVideoQuadScaledToWindow", "void __stdcall CFrontEnd__RenderVideoQuadScaledToWindow(float scale, int argb, float center_x, float center_y)"),
    "0x0051dba0": ("CFEPMultiplayerStart__Init", "int __fastcall CFEPMultiplayerStart__Init(void * this)"),
    "0x0051e120": ("CFEPMultiplayerStart__RenderPreCommon", "void __stdcall CFEPMultiplayerStart__RenderPreCommon(void * this, float transition, int dest)"),
}

DECOMPILE_TOKENS = {
    "00459920_CFEPMultiplayerStart__SubObj8848__ctor.c": ("PTR_CFEPMultiplayerStart__SubObj8848__Init_005db4fc", "0x345c", "300"),
    "004599a0_CFEPMultiplayerStart__SubObj8848__Init.c": ("DAT_0089d94c", "CRT__RoundDoubleWithFpuChecks", "PLATFORM__GetSysTimeFloat"),
    "00459b00_CFEPMultiplayerStart__SubObj8848__Process.c": ("CFrontEnd__SetPage", "0x2ee", "0xc"),
    "00459c10_CFEPMultiplayerStart__SubObj8848__ButtonPressed.c": ("case 0x2a", "case 0x2c", "DAT_0089d94c", "CFrontEnd__PlaySound"),
    "00459e50_CFEPMultiplayerStart__SubObj8848__RenderPreCommon.c": ("CFrontEnd__RenderVideoQuadScaledToWindow", "ROUND"),
    "00459ee0_CFEPMultiplayerStart__SubObj8848__Render.c": ("CFrontEnd__ResolveLevelNameTextByCode", "CFrontEnd__ResolveEpisodeNameTextByIndex", "s_E3_2002_Build"),
}

VTABLE_EXPECTED = {
    ("005db4fc", "0", "CFEPMultiplayerStart__SubObj8848__Init"),
    ("005db4fc", "2", "CFEPMultiplayerStart__SubObj8848__Process"),
    ("005db4fc", "3", "CFEPMultiplayerStart__SubObj8848__ButtonPressed"),
    ("005db4fc", "4", "CFEPMultiplayerStart__SubObj8848__RenderPreCommon"),
    ("005db4fc", "5", "CFEPMultiplayerStart__SubObj8848__Render"),
    ("005db4fc", "6", "CFEPMultiplayerStart__SubObj8848__TransitionNotification"),
    ("005db4fc", "7", "CFEPMultiplayerStart__SubObj8848__ActiveNotification"),
    ("005db4fc", "8", "CFrontEndPage__DeActiveNotification"),
    ("005db8d0", "0", "CFEPMultiplayerStart__Init"),
    ("005db8d0", "2", "CFEPMultiplayerStart__Process"),
    ("005db8d0", "3", "CFEPMultiplayerStart__ButtonPressed"),
    ("005db8d0", "4", "CFEPMultiplayerStart__RenderPreCommon"),
    ("005db8d0", "5", "CFEPMultiplayerStart__Render"),
    ("005db8d0", "6", "CFEPMultiplayerStart__TransitionNotification"),
}

CORE_TOKENS = (
    "Wave955",
    "fepmultiplayerstart-subobj8848-review-wave955",
    "0x00459920 CFEPMultiplayerStart__SubObj8848__ctor",
    "0x004599a0 CFEPMultiplayerStart__SubObj8848__Init",
    "0x00459e50 CFEPMultiplayerStart__SubObj8848__RenderPreCommon",
    "0x00459ee0 CFEPMultiplayerStart__SubObj8848__Render",
    "0x005db4fc",
    r"C:\dev\ONSLAUGHT2\FEPMultiplayerStart.cpp",
    "286/1408 = 20.31%",
    "6151/6151 = 100.00%",
    BACKUP_PATH,
    "no mutation",
)

OVERCLAIMS = (
    "runtime multiplayer-start behavior proven",
    "runtime frontend behavior proven",
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
        "pre-metadata.tsv": 15,
        "pre-tags.tsv": 15,
        "pre-xrefs.tsv": 73,
        "pre-instructions.tsv": 1581,
        "pre-decompile/index.tsv": 15,
        "pre-vtables.tsv": 20,
        "string-0063fc24.tsv": 1,
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

    rows = read_tsv(BASE / "string-0063fc24.tsv")
    require(rows and rows[0].get("cstring") == r"C:\dev\ONSLAUGHT2\FEPMultiplayerStart.cpp", "debug string mismatch", failures)

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
        "pre-metadata.log": "targets=15 found=15 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=15 missing=0",
        "pre-xrefs.log": "Wrote 73 rows",
        "pre-instructions.log": "Wrote 1581 function-body instruction rows",
        "pre-decompile.log": "targets=15 dumped=15 missing=0 failed=0",
        "pre-vtables.log": "ExportVtableSlots complete: targets=2 rows=20",
        "string-0063fc24.log": r"DumpCStringAtAddress complete: input=0063fc24 target=0063fc24 text=C:\dev\ONSLAUGHT2\FEPMultiplayerStart.cpp",
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
    docs = [NOTE, CAMPAIGN, FUNCTION_INDEX, FEPMULTI_DOC, DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE]
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
        scripts.get("test:ghidra-fepmultiplayerstart-subobj8848-review-wave955")
        == r"py -3 tools\ghidra_fepmultiplayerstart_subobj8848_review_wave955_probe.py --check",
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
        print("Wave955 FEPMultiplayerStart SubObj8848 probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave955 FEPMultiplayerStart SubObj8848 probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
