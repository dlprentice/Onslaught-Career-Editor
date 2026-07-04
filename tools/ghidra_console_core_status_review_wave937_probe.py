#!/usr/bin/env python3
"""Validate Wave937 CConsole core/status read-only review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave937-console-core-status-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_console_core_status_review_wave937_2026-05-28.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
CONSOLE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "console.cpp" / "_index.md"
PACKAGE_JSON = ROOT / "package.json"
STATE_FILES = [
    ROOT / "developer_agent_state.json",
    ROOT / "documentation_agent_state.json",
    ROOT / "re_orchestrator_state.json",
]

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260528-015348_post_wave937_console_core_status_review_verified"
SCRIPT_NAME = "test:ghidra-console-core-status-review-wave937"
SCRIPT_VALUE = r"py -3 tools\ghidra_console_core_status_review_wave937_probe.py --check"

TARGETS = {
    "0x00429bc0": (
        "CConsole__Init",
        "void __fastcall CConsole__Init(void * this)",
        ("command/variable list heads", "key-name table", "startup console text"),
    ),
    "0x00429ef0": (
        "CConsole__RegisterBuiltinCommands",
        "void __fastcall CConsole__RegisterBuiltinCommands(void * this)",
        ("built-in console commands", "cg_consolealpha", "callback pointers"),
    ),
    "0x0042a410": (
        "CConsole__ResetLayoutForWindowHeight",
        "void __fastcall CConsole__ResetLayoutForWindowHeight(void * this)",
        ("PLATFORM__GetWindowHeight", "layout metrics", "loading-screen stride"),
    ),
    "0x0042a540": (
        "CConsoleVar__GetTypeName",
        "void __stdcall CConsoleVar__GetTypeName(void * var, char * outTypeName)",
        ("+0xa0", "DWORD", "fmatrix"),
    ),
    "0x004416e0": (
        "CConsole__ResetStatusHistoryBuffer",
        "void __fastcall CConsole__ResetStatusHistoryBuffer(void * console)",
        ("30 0x50-byte text slots", "+0x9e4", "+0x9ec"),
    ),
    "0x00441740": (
        "CConsole__Printf",
        "void __cdecl CConsole__Printf(void * console, char * format, ...)",
        ("700-byte stack buffer", "DebugTrace", "status/history ring"),
    ),
    "0x004418a0": (
        "CConsole__PrintfNoNewline",
        "void __cdecl CConsole__PrintfNoNewline(void * console, char * format, ...)",
        ("256-byte stack buffer", "DebugTrace newline mirror", "status/history ring"),
    ),
}

CONTEXT = {
    "0x0040c640": (
        "DebugTrace",
        "void __cdecl DebugTrace(char * message)",
        ("RET stub", "diagnostic", "logging callsites"),
    ),
    "0x004419e0": (
        "CConsole__RenderStatusHistoryOverlay",
        "void __fastcall CConsole__RenderStatusHistoryOverlay(void * console)",
        ("Text__AsciiToWideScratch", "CDXFont__DrawText", "+0x9e8"),
    ),
    "0x0042a5f0": (
        "CConsoleVar__FormatValueToString",
        "void __stdcall CConsoleVar__FormatValueToString(void * var, char * outValueText)",
        ("type enum", "value pointer", "True/False"),
    ),
    "0x0042af80": (
        "CConsole__RegisterCommand",
        "void __thiscall CConsole__RegisterCommand(void * this, char * name, char * description, void * callback, char flags)",
        ("0xac-byte command node", "+0xa0", "+0xa8"),
    ),
    "0x0042b040": (
        "CConsole__RegisterVariable",
        "void __thiscall CConsole__RegisterVariable(void * this, char * name, char * description, int varType, void * valuePtr, char flags1, char flags2)",
        ("0xb0-byte variable node", "type/value pointer", "+0xac"),
    ),
    "0x0042b840": (
        "CConsole__AddString",
        "void __cdecl CConsole__AddString(void * this, char * format)",
        ("variadic console-line sink", "DebugTrace", "newline-delimited"),
    ),
    "0x0042bcf0": (
        "CConsole__InitKeyNameTable",
        "void __fastcall CConsole__InitKeyNameTable(void * this)",
        ("key-name lookup table", "Backspace", "Return"),
    ),
    "0x00515db0": (
        "Registry__SetStringValue_HKCU",
        "void __stdcall Registry__SetStringValue_HKCU(char * value_name, uchar * value_text)",
        ("HKEY_CURRENT_USER", "Software\\\\Lost Toys\\\\Battle Engine Aquila", "RegSetValueExA"),
    ),
}

EXPECTED_XREFS = {
    ("0x00429bc0", "0x004efbc7", "CLTShell__InitializeRuntimeAndLoadCoreResources", "UNCONDITIONAL_CALL"),
    ("0x00429ef0", "0x0046c385", "CGame__Init", "UNCONDITIONAL_CALL"),
    ("0x0042a410", "0x004eff37", "CLTShell__InitializeRuntimeAndLoadCoreResources", "UNCONDITIONAL_CALL"),
    ("0x0042a540", "0x004296db", "<no_function>", "UNCONDITIONAL_CALL"),
    ("0x0042a540", "0x0042c66a", "<no_function>", "UNCONDITIONAL_CALL"),
    ("0x004416e0", "0x004efb65", "CLTShell__InitializeRuntimeAndLoadCoreResources", "UNCONDITIONAL_CALL"),
    ("0x004416e0", "0x004efb6f", "CLTShell__InitializeRuntimeAndLoadCoreResources", "UNCONDITIONAL_CALL"),
    ("0x00441740", "0x0042cfc2", "FatalError__ExitProcess", "UNCONDITIONAL_CALL"),
    ("0x00441740", "0x004a1a28", "CMemoryHeap__Alloc", "UNCONDITIONAL_CALL"),
    ("0x00441740", "0x0041b7dc", "CCareer__Blank", "UNCONDITIONAL_CALL"),
    ("0x004418a0", "0x00539b1c", "CScriptObjectCode__Run", "UNCONDITIONAL_CALL"),
}

EXPECTED_CONTEXT_XREFS = {
    ("0x0040c640", "0x00441767", "CConsole__Printf", "UNCONDITIONAL_CALL"),
    ("0x0040c640", "0x0042b892", "CConsole__AddString", "UNCONDITIONAL_CALL"),
    ("0x004419e0", "0x0047182c", "CGame__DrawGameStuff", "UNCONDITIONAL_CALL"),
    ("0x0042a5f0", "0x004297b3", "<no_function>", "UNCONDITIONAL_CALL"),
    ("0x0042af80", "0x0042a33a", "CConsole__RegisterBuiltinCommands", "UNCONDITIONAL_CALL"),
    ("0x0042af80", "0x0046c813", "CGame__InitRestartLoop", "UNCONDITIONAL_CALL"),
    ("0x0042b040", "0x0042a400", "CConsole__RegisterBuiltinCommands", "UNCONDITIONAL_CALL"),
    ("0x0042b040", "0x004054b7", "CBattleEngine__Init", "UNCONDITIONAL_CALL"),
    ("0x0042b840", "0x00429e1b", "CConsole__Init", "UNCONDITIONAL_CALL"),
    ("0x0042b840", "0x0042ad5d", "CConsole__ExecScript", "UNCONDITIONAL_CALL"),
    ("0x0042bcf0", "0x00429d38", "CConsole__Init", "UNCONDITIONAL_CALL"),
    ("0x00515db0", "0x00429c59", "CConsole__Init", "UNCONDITIONAL_CALL"),
    ("0x00515db0", "0x0042b9a1", "CConsole__AddString", "UNCONDITIONAL_CALL"),
}

EXPECTED_INSTRUCTIONS = {
    ("instructions.tsv", "0x00429bd1", "MOV", "0x2394", "CConsole__Init"),
    ("instructions.tsv", "0x00429bd7", "MOV", "0x2398", "CConsole__Init"),
    ("instructions.tsv", "0x00429bdd", "MOV", "0xc8", "CConsole__Init"),
    ("instructions.tsv", "0x00429c59", "CALL", "0x00515db0", "CConsole__Init"),
    ("instructions.tsv", "0x00429d38", "CALL", "0x0042bcf0", "CConsole__Init"),
    ("instructions.tsv", "0x00429e1b", "CALL", "0x0042b840", "CConsole__Init"),
    ("instructions.tsv", "0x00429e2d", "RET", "", "CConsole__Init"),
    ("instructions.tsv", "0x0042a33a", "CALL", "0x0042af80", "CConsole__RegisterBuiltinCommands"),
    ("instructions.tsv", "0x0042a400", "CALL", "0x0042b040", "CConsole__RegisterBuiltinCommands"),
    ("instructions.tsv", "0x0042a40a", "RET", "", "CConsole__RegisterBuiltinCommands"),
    ("instructions.tsv", "0x0042a458", "RET", "", "CConsole__ResetLayoutForWindowHeight"),
    ("instructions.tsv", "0x0042a546", "MOV", "0xa0", "CConsoleVar__GetTypeName"),
    ("instructions.tsv", "0x0042a5be", "RET", "0x8", "CConsoleVar__GetTypeName"),
    ("instructions.tsv", "0x00441701", "MOV", "0x9e4", "CConsole__ResetStatusHistoryBuffer"),
    ("instructions.tsv", "0x0044170b", "MOV", "0x9e8", "CConsole__ResetStatusHistoryBuffer"),
    ("instructions.tsv", "0x00441715", "MOV", "0x00662dd0", "CConsole__ResetStatusHistoryBuffer"),
    ("instructions.tsv", "0x00441725", "MOV", "0x9ec", "CConsole__ResetStatusHistoryBuffer"),
    ("instructions.tsv", "0x0044172b", "RET", "", "CConsole__ResetStatusHistoryBuffer"),
    ("instructions.tsv", "0x0044175a", "CALL", "0x0055e38c", "CConsole__Printf"),
    ("instructions.tsv", "0x00441767", "CALL", "0x0040c640", "CConsole__Printf"),
    ("instructions.tsv", "0x00441774", "CALL", "0x0040c640", "CConsole__Printf"),
    ("instructions.tsv", "0x00441783", "MOV", "0x9ec", "CConsole__Printf"),
    ("instructions.tsv", "0x00441896", "ADD", "0x2bc", "CConsole__Printf"),
    ("instructions.tsv", "0x0044189c", "RET", "", "CConsole__Printf"),
    ("instructions.tsv", "0x004418af", "MOV", "0x9ec", "CConsole__PrintfNoNewline"),
    ("instructions.tsv", "0x00441946", "CALL", "0x0055e38c", "CConsole__PrintfNoNewline"),
    ("instructions.tsv", "0x004419d7", "RET", "", "CConsole__PrintfNoNewline"),
    ("context-instructions.tsv", "0x0040c640", "RET", "", "DebugTrace"),
    ("context-instructions.tsv", "0x00441a1a", "MOV", "0x9e4", "CConsole__RenderStatusHistoryOverlay"),
    ("context-instructions.tsv", "0x00441a78", "FLD", "0x005db020", "CConsole__RenderStatusHistoryOverlay"),
    ("context-instructions.tsv", "0x0042b089", "CALL", "0x005490e0", "CConsole__RegisterVariable"),
    ("context-instructions.tsv", "0x0042b892", "CALL", "0x0040c640", "CConsole__AddString"),
    ("context-instructions.tsv", "0x00515ded", "PUSH", "ECX", "Registry__SetStringValue_HKCU"),
}

DECOMPILE_TOKENS = {
    "decompile/00429bc0_CConsole__Init.c": ("Registry__SetStringValue_HKCU", "CConsole__InitKeyNameTable", "CConsole__AddString", "0x2394", "0x2398"),
    "decompile/00429ef0_CConsole__RegisterBuiltinCommands.c": ("CConsole__RegisterCommand", "CConsole__RegisterVariable", "cg_consolealpha"),
    "decompile/0042a410_CConsole__ResetLayoutForWindowHeight.c": ("PLATFORM__GetWindowHeight", "0x2388", "0xb3cc"),
    "decompile/0042a540_CConsoleVar__GetTypeName.c": ("DWORD", "string", "fmatrix"),
    "decompile/004416e0_CConsole__ResetStatusHistoryBuffer.c": ("0x9e4", "0x9e8", "0x9ec"),
    "decompile/00441740_CConsole__Printf.c": ("vsprintf", "DebugTrace", "StrCopyN", "0x9e4"),
    "decompile/004418a0_CConsole__PrintfNoNewline.c": ("vsprintf", "StrCopyN", "0x9e4"),
    "context-decompile/0040c640_DebugTrace.c": ("DebugTrace", "return;"),
    "context-decompile/004419e0_CConsole__RenderStatusHistoryOverlay.c": ("Text__AsciiToWideScratch", "CDXFont__DrawText", "0x9e4"),
    "context-decompile/0042a5f0_CConsoleVar__FormatValueToString.c": ("True/False", "False", "s_Unknown_type"),
    "context-decompile/0042af80_CConsole__RegisterCommand.c": ("CDXMemoryManager__Alloc", "stricmp", "0xa8"),
    "context-decompile/0042b040_CConsole__RegisterVariable.c": ("CDXMemoryManager__Alloc", "stricmp", "0xac"),
    "context-decompile/0042b840_CConsole__AddString.c": ("DebugTrace", "Registry__SetStringValue_HKCU", "vsprintf"),
    "context-decompile/0042bcf0_CConsole__InitKeyNameTable.c": ("Backspace", "Return", "Shift"),
    "context-decompile/00515db0_Registry__SetStringValue_HKCU.c": ("RegCreateKeyExA", "RegSetValueExA", "Battle Engine Aquila"),
}

CORE_TOKENS = (
    "Wave937",
    "console-core-status-review-wave937",
    "161/1408 = 11.43%",
    "6113/6113 = 100.00%",
    BACKUP,
    "0x00429bc0 CConsole__Init",
    "0x00429ef0 CConsole__RegisterBuiltinCommands",
    "0x0042a410 CConsole__ResetLayoutForWindowHeight",
    "0x0042a540 CConsoleVar__GetTypeName",
    "0x004416e0 CConsole__ResetStatusHistoryBuffer",
    "0x00441740 CConsole__Printf",
    "0x004418a0 CConsole__PrintfNoNewline",
    "0x0040c640 DebugTrace",
    "0x004419e0 CConsole__RenderStatusHistoryOverlay",
    "0x0042a5f0 CConsoleVar__FormatValueToString",
    "0x0042af80 CConsole__RegisterCommand",
    "0x0042b040 CConsole__RegisterVariable",
    "0x0042b840 CConsole__AddString",
    "0x0042bcf0 CConsole__InitKeyNameTable",
    "0x00515db0 Registry__SetStringValue_HKCU",
    "no mutation",
)

OVERCLAIMS = (
    "runtime console behavior proven",
    "runtime status overlay behavior proven",
    "runtime registry side effects proven",
    "runtime file logging behavior proven",
    "fully reverse-engineered",
    "rebuild parity proven",
)


def normalize_address(value: str) -> str:
    text = (value or "").strip().lower()
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


def row_by_address(rows: list[dict[str, str]], address: str) -> dict[str, str]:
    want = normalize_address(address)
    for row in rows:
        if normalize_address(row.get("address", "")) == want:
            return row
    return {}


def check_counts_and_logs(failures: list[str]) -> None:
    expected_counts = {
        "metadata.tsv": 7,
        "tags.tsv": 7,
        "xrefs.tsv": 388,
        "instructions.tsv": 872,
        "decompile/index.tsv": 7,
        "context-metadata.tsv": 8,
        "context-tags.tsv": 8,
        "context-xrefs.tsv": 482,
        "context-instructions.tsv": 1189,
        "context-decompile/index.tsv": 8,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    expected_logs = {
        "metadata.log": "targets=7 found=7 missing=0",
        "tags.log": "rows=7 missing=0",
        "xrefs.log": "Wrote 388 rows",
        "instructions.log": "Wrote 872 function-body instruction rows",
        "decompile.log": "targets=7 dumped=7 missing=0 failed=0",
        "context-metadata.log": "targets=8 found=8 missing=0",
        "context-tags.log": "rows=8 missing=0",
        "context-xrefs.log": "Wrote 482 rows",
        "context-instructions.log": "Wrote 1189 function-body instruction rows",
        "context-decompile.log": "targets=8 dumped=8 missing=0 failed=0",
    }
    for relative, token in expected_logs.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_metadata_and_decompile(failures: list[str]) -> None:
    metadata = read_tsv(BASE / "metadata.tsv")
    decompile = read_tsv(BASE / "decompile" / "index.tsv")
    tags = read_tsv(BASE / "tags.tsv")
    context_metadata = read_tsv(BASE / "context-metadata.tsv")
    context_decompile = read_tsv(BASE / "context-decompile" / "index.tsv")
    context_tags = read_tsv(BASE / "context-tags.tsv")

    for address, (name, signature, comment_tokens) in TARGETS.items():
        row = row_by_address(metadata, address)
        require(row.get("name") == name, f"name mismatch at {address}", failures)
        require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
        require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
        for token in comment_tokens:
            require(token in row.get("comment", ""), f"missing comment token at {address}: {token}", failures)
        drow = row_by_address(decompile, address)
        require(drow.get("name") == name, f"decompile name mismatch at {address}", failures)
        require(drow.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
        require(drow.get("status") == "OK", f"decompile status mismatch at {address}", failures)
        require(row_by_address(tags, address).get("status") == "OK", f"tag status mismatch at {address}", failures)

    for address, (name, signature, comment_tokens) in CONTEXT.items():
        row = row_by_address(context_metadata, address)
        require(row.get("name") == name, f"context name mismatch at {address}", failures)
        require(row.get("signature") == signature, f"context signature mismatch at {address}", failures)
        require(row.get("status") == "OK", f"context metadata status mismatch at {address}", failures)
        for token in comment_tokens:
            require(token in row.get("comment", ""), f"missing context comment token at {address}: {token}", failures)
        drow = row_by_address(context_decompile, address)
        require(drow.get("name") == name, f"context decompile name mismatch at {address}", failures)
        require(drow.get("signature") == signature, f"context decompile signature mismatch at {address}", failures)
        require(drow.get("status") == "OK", f"context decompile status mismatch at {address}", failures)
        require(row_by_address(context_tags, address).get("status") == "OK", f"context tag status mismatch at {address}", failures)


def xref_set(path: Path) -> set[tuple[str, str, str, str]]:
    rows = read_tsv(path)
    return {
        (
            normalize_address(row["target_addr"]),
            normalize_address(row["from_addr"]),
            row.get("from_function", ""),
            row.get("ref_type", ""),
        )
        for row in rows
    }


def check_xrefs_instructions_and_decompiles(failures: list[str]) -> None:
    xrefs = xref_set(BASE / "xrefs.tsv")
    context_xrefs = xref_set(BASE / "context-xrefs.tsv")

    for expected in EXPECTED_XREFS:
        require((normalize_address(expected[0]), normalize_address(expected[1]), expected[2], expected[3]) in xrefs, f"missing xref: {expected}", failures)
    for expected in EXPECTED_CONTEXT_XREFS:
        require((normalize_address(expected[0]), normalize_address(expected[1]), expected[2], expected[3]) in context_xrefs, f"missing context xref: {expected}", failures)

    instruction_cache: dict[str, list[dict[str, str]]] = {}
    for relative, address, mnemonic, operand_token, function_name in EXPECTED_INSTRUCTIONS:
        rows = instruction_cache.setdefault(relative, read_tsv(BASE / relative))
        found = any(
            normalize_address(row.get("instruction_addr", "")) == normalize_address(address)
            and row.get("mnemonic", "") == mnemonic
            and row.get("function_name", "") == function_name
            and (not operand_token or operand_token in row.get("operands", ""))
            for row in rows
        )
        require(found, f"missing instruction: {relative} {address} {mnemonic} {operand_token} {function_name}", failures)

    for relative, tokens in DECOMPILE_TOKENS.items():
        text = read_text(BASE / relative)
        for token in tokens:
            require(token in text, f"missing decompile token in {relative}: {token}", failures)


def check_backup(failures: list[str]) -> None:
    backup = json.loads(read_text(BASE / "backup-summary.json"))
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes", -1)) == 173247367, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs_and_state(failures: list[str]) -> None:
    for path in [NOTE, CAMPAIGN, CONSOLE_DOC, *STATE_FILES]:
        text = read_text(path)
        for token in CORE_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = json.loads(read_text(PACKAGE_JSON))
    require(package.get("scripts", {}).get(SCRIPT_NAME) == SCRIPT_VALUE, "missing package script", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_counts_and_logs(failures)
    check_metadata_and_decompile(failures)
    check_xrefs_instructions_and_decompiles(failures)
    check_backup(failures)
    check_docs_and_state(failures)

    if failures:
        print("Wave937 CConsole core/status review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave937 CConsole core/status review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
