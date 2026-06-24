#!/usr/bin/env python3
"""Validate Wave956 CFEPDemoMain review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave956-cfepdemo-main-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_cfepdemo_main_review_wave956_2026-05-28.md"
PACKAGE_JSON = ROOT / "package.json"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FEPDEMO_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FEPDemoMain.cpp.md"
FRONTEND_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FrontEnd.cpp" / "_index.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260528-105733_post_wave956_cfepdemo_main_review_verified"

EXPECTED_METADATA = {
    "0x00457ec0": ("CFEPDemoMain__GetMenuType", "int __cdecl CFEPDemoMain__GetMenuType(void)"),
    "0x00457ed0": ("CFEPDemoMain__GetActionCount", "int __stdcall CFEPDemoMain__GetActionCount(int menu_state)"),
    "0x00457ee0": ("CFEPDemoMain__DoAction", "void __fastcall CFEPDemoMain__DoAction(void * this)"),
    "0x00457f20": ("CFEPDemoMain__Update", "void __stdcall CFEPDemoMain__Update(int menu_state)"),
    "0x004621b0": ("CFEPMain__Init", "int __fastcall CFEPMain__Init(void * this)"),
    "0x004623e0": ("CFEPMain__DoAction", "void __fastcall CFEPMain__DoAction(void * this)"),
    "0x004644d0": ("CFEPMain__TransitionNotification", "void __fastcall CFEPMain__TransitionNotification(void * this, int from)"),
    "0x00464520": ("CFEPMain__ActiveNotification", "void __fastcall CFEPMain__ActiveNotification(void * this, int from_page)"),
    "0x00466ae0": ("CFrontEnd__SetPage", "void __thiscall CFrontEnd__SetPage(void * this, int page, int time)"),
    "0x004679e0": ("CFrontEnd__RenderPreCommonFade", "void __stdcall CFrontEnd__RenderPreCommonFade(float transition, uint argb, int destination_page)"),
    "0x00468770": ("CFrontEnd__PlaySound", "void __cdecl CFrontEnd__PlaySound(int sound)"),
}

PRIMARY_TAGS = {
    "0x00457ec0": {"fepdemo-wave402", "frontend", "menu-type", "signature-corrected", "comment-hardened", "static-reaudit"},
    "0x00457ed0": {"fepdemo-wave402", "frontend", "action-count", "signature-corrected", "comment-hardened", "static-reaudit"},
    "0x00457ee0": {"fepdemo-wave402", "frontend", "action", "comment-hardened", "static-reaudit"},
    "0x00457f20": {"fepdemo-wave402", "frontend", "localization", "signature-corrected", "comment-hardened", "static-reaudit"},
}

DECOMPILE_TOKENS = {
    "00457ec0_CFEPDemoMain__GetMenuType.c": ("return 3;",),
    "00457ed0_CFEPDemoMain__GetActionCount.c": ("return 1;",),
    "00457ee0_CFEPDemoMain__DoAction.c": (
        "_DAT_008a956c = 0xc9",
        "CFEPMain__DoAction(this)",
        "_DAT_008a956c = 0xffffffff",
        "CFrontEnd__SetPage(&DAT_0089d758,0x11,0x46)",
    ),
    "00457f20_CFEPDemoMain__Update.c": (
        "FrontEndText__GetLocalizedOrFallbackTextByToken(0)",
        "FrontEndText__GetLocalizedOrFallbackTextByToken(8)",
        "FrontEndText__GetLocalizedOrFallbackTextByToken(6)",
    ),
}

VTABLE_EXPECTED = {
    ("005db7c0", "0", "CFEPMain__TransitionNotification"),
    ("005db7c0", "1", "CFEPMain__ActiveNotification"),
    ("005db7c0", "2", "CFrontEndPage__DeActiveNotification"),
    ("005db7c0", "3", "CFEPDemoMain__GetActionCount"),
    ("005db7c0", "4", "CFEPDemoMain__GetMenuType"),
    ("005db7c0", "5", "CFEPDemoMain__DoAction"),
    ("005db7c0", "6", "CFEPDemoMain__Update"),
    ("005e4a70", "2", "CFEPDemoMain__GetMenuType"),
}

CORE_TOKENS = (
    "Wave956",
    "cfepdemo-main-review-wave956",
    "0x00457ec0 CFEPDemoMain__GetMenuType",
    "0x00457ed0 CFEPDemoMain__GetActionCount",
    "0x00457ee0 CFEPDemoMain__DoAction",
    "0x00457f20 CFEPDemoMain__Update",
    "0x005db7c0",
    "0x005e4a78",
    "290/1408 = 20.60%",
    "6151/6151 = 100.00%",
    BACKUP_PATH,
    "no mutation",
)

OVERCLAIMS = (
    "runtime demo-menu behavior proven",
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
    return "0x" + value.zfill(8)


def contains_token(text: str, token: str) -> bool:
    stripped = text.replace("`", "")
    return token in text or token in stripped or token.replace("\\", "\\\\") in text or token.replace("\\", "\\\\") in stripped


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def check_artifacts(failures: list[str]) -> None:
    counts = {
        "pre-metadata.tsv": 11,
        "pre-tags.tsv": 11,
        "pre-xrefs.tsv": 220,
        "pre-instructions.tsv": 404,
        "pre-decompile/index.tsv": 11,
        "pre-vtables.tsv": 20,
    }
    for relative, expected in counts.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == expected, f"{relative} row count mismatch: {actual} != {expected}", failures)

    metadata = {norm(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    decompile_index = {norm(row["address"]): row for row in read_tsv(BASE / "pre-decompile" / "index.tsv")}
    tags = {norm(row["address"]): row for row in read_tsv(BASE / "pre-tags.tsv")}

    for address, (name, signature) in EXPECTED_METADATA.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
        dec = decompile_index.get(address)
        require(dec is not None and dec.get("status") == "OK", f"decompile missing/failed at {address}", failures)

    for address, expected_tags in PRIMARY_TAGS.items():
        row = tags.get(address)
        observed = set((row or {}).get("tags", "").split(";"))
        missing = expected_tags - observed
        require(not missing, f"primary tags missing at {address}: {sorted(missing)}", failures)

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
        require(expected in vtable_rows, f"missing vtable/data-table row: {expected}", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected_logs = {
        "pre-metadata.log": "targets=11 found=11 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=11 missing=0",
        "pre-xrefs.log": "Wrote 220 rows",
        "pre-instructions.log": "Wrote 404 function-body instruction rows",
        "pre-decompile.log": "targets=11 dumped=11 missing=0 failed=0",
        "pre-vtables.log": "ExportVtableSlots complete: targets=2 rows=20",
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
    docs = [
        NOTE,
        CAMPAIGN,
        GHIDRA_REFERENCE,
        FUNCTION_INDEX,
        FEPDEMO_DOC,
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
        scripts.get("test:ghidra-cfepdemo-main-review-wave956")
        == r"py -3 tools\ghidra_cfepdemo_main_review_wave956_probe.py --check",
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
        print("Wave956 CFEPDemoMain review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave956 CFEPDemoMain review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
