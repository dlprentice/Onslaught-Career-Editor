#!/usr/bin/env python3
"""Validate Wave962 game-menu/options bridge read-only review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave962-game-menu-options-bridge-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_game_menu_options_bridge_review_wave962_2026-05-28.md"
PACKAGE_JSON = ROOT / "package.json"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
PAUSEMENU_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "PauseMenu.cpp" / "_index.md"
MENUITEM_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "MenuItem.cpp" / "_index.md"
ENGINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "engine.cpp" / "_index.md"
GAME_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "game.cpp" / "_index.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUALITY_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260528-132411_post_wave962_game_menu_options_bridge_review_verified"

EXPECTED_METADATA = {
    "0x0046c360": ("CGame__Init", "int __fastcall CGame__Init(void * this)"),
    "0x004729e0": ("CGameInterface__ResetMenuState", "void __fastcall CGameInterface__ResetMenuState(void * this)"),
    "0x00472b40": ("CGameInterface__HandleMenuSelection", "void __thiscall CGameInterface__HandleMenuSelection(void * this, void * controller)"),
    "0x00472d50": ("CGameInterface__VFunc_03_HandleMenuControlInput", "void __thiscall CGameInterface__VFunc_03_HandleMenuControlInput(void * this, void * control_context, int button_id, int button_context)"),
    "0x004d0290": ("CControllerBackMenuItem__RenderBindingCapacityWarning", "void __thiscall CControllerBackMenuItem__RenderBindingCapacityWarning(void * this, float x, float y, int render_flags)"),
    "0x004d06e0": ("CPauseMenu__ResumeGameAndPersistOptions", "void __fastcall CPauseMenu__ResumeGameAndPersistOptions(void * pause_menu)"),
    "0x004d0810": ("CPauseMenu__ButtonPressed", "void __thiscall CPauseMenu__ButtonPressed(void * this, void * menu_item, int button_context)"),
    "0x004d0db0": ("CPauseMenu__InitBindingPromptAction", "void * __thiscall CPauseMenu__InitBindingPromptAction(void * this, void * menu_item, void * pause_menu, int action_id)"),
    "0x004d0de0": ("CPauseMenu__GetBindingCapacityWarningText", "short * __cdecl CPauseMenu__GetBindingCapacityWarningText(void)"),
    "0x004d0e40": ("CGameMenu__InitBase", "void __fastcall CGameMenu__InitBase(void * game_menu)"),
    "0x004d0ff0": ("CPauseMenu__InitPauseSession", "void __thiscall CPauseMenu__InitPauseSession(void * this, int activate_control)"),
    "0x004d3020": ("CEngine__SetOptionValueAndNotifyTarget", "void __thiscall CEngine__SetOptionValueAndNotifyTarget(void * this, int option_value)"),
}

COMMENT_TOKENS = {
    "0x004d0290": ("Wave465", "0xe8/0xe9", "CMenuItem__RenderWithColor"),
    "0x004d0e40": ("Wave465", "PTR_SharedVFunc__NoOpOneArg_004014c0_005dc72c", "CMenuItemRangeVariant"),
    "0x004d3020": ("Wave486", "RET 0x4", "0x00662ab0", "vfunc +0xe0", "vfunc +0x154"),
}

TAG_TOKENS = {
    "0x004d0290": ("pausemenu-tail-wave465", "menu-item", "controller-back"),
    "0x004d0e40": ("pausemenu-tail-wave465", "game-menu", "constructor"),
    "0x004d3020": ("engine-pod-ballistic-wave486", "engine-option", "god-mode-adjacent"),
    "0x00472d50": ("game-interface-menu-control-boundary-wave952", "function-boundary-recovered", "menu-control-input"),
}

XREF_EVIDENCE = (
    ("0x004d0e40", "0x004d0917", "CPauseMenu__ButtonPressed", "UNCONDITIONAL_CALL"),
    ("0x004d0de0", "0x004d087d", "CPauseMenu__ButtonPressed", "UNCONDITIONAL_CALL"),
    ("0x004d3020", "0x00472d09", "CGameInterface__HandleMenuSelection", "UNCONDITIONAL_CALL"),
    ("0x004d3020", "0x004d0b3a", "CPauseMenu__ButtonPressed", "UNCONDITIONAL_CALL"),
    ("0x004d3020", "0x004d0b55", "CPauseMenu__ButtonPressed", "UNCONDITIONAL_CALL"),
    ("0x00472d50", "0x005dbc38", "<no_function>", "DATA"),
)

INSTRUCTION_EVIDENCE = (
    ("0x004d0290", "0x004d02a5", "PUSH", "0xe8"),
    ("0x004d0290", "0x004d02d7", "PUSH", "0xe9"),
    ("0x004d0290", "0x004d02ff", "CALL", "0x004a3290"),
    ("0x004d0290", "0x004d0306", "RET", "0xc"),
    ("0x004d0e40", "0x004d0e49", "MOV", "0x5dc72c"),
    ("0x004d0e40", "0x004d0e4f", "RET", ""),
    ("0x004d3020", "0x004d302e", "MOV", "0x662ab0"),
    ("0x004d3020", "0x004d3048", "CALL", "0xe0"),
    ("0x004d3020", "0x004d3066", "CALL", "0x154"),
    ("0x004d3020", "0x004d3075", "RET", "0x4"),
    ("0x004d0810", "0x004d087d", "CALL", "0x004d0de0"),
    ("0x004d0810", "0x004d0917", "CALL", "0x004d0e40"),
    ("0x004d0810", "0x004d0b3a", "CALL", "0x004d3020"),
    ("0x00472b40", "0x00472d09", "CALL", "0x004d3020"),
    ("0x00472d50", "0x00472df6", "CALL", "0x00472b40"),
    ("0x00472d50", "0x00472dfb", "RET", "0xc"),
)

VTABLE_EVIDENCE = (
    ("0x005dbc2c", "3", "0x00472d50", "CGameInterface__VFunc_03_HandleMenuControlInput"),
    ("0x005dc72c", "0", "0x004014c0", "SharedVFunc__NoOpOneArg_004014c0"),
    ("0x005db440", "0", "0x00453a90", "CMenuItem__scalar_deleting_dtor"),
    ("0x005dc650", "0", "0x004a4610", "CMenuItemRange__ScalarDestructor"),
    ("0x005dc664", "0", "0x004a4e60", "CMenuItemRangeVariant__ScalarDestructor"),
)

CORE_TOKENS = (
    "Wave962",
    "game-menu-options-bridge-review-wave962",
    "0x004d0290 CControllerBackMenuItem__RenderBindingCapacityWarning",
    "0x004d0e40 CGameMenu__InitBase",
    "0x004d3020 CEngine__SetOptionValueAndNotifyTarget",
    "0x00472d50 CGameInterface__VFunc_03_HandleMenuControlInput",
    "0x004d02a5 PUSH 0xe8",
    "0x004d02d7 PUSH 0xe9",
    "0x004d0e49 MOV [EAX], 0x5dc72c",
    "0x004d302e MOV [EAX*0x4 + 0x662ab0], EDI",
    "0x005dbc2c slot 3",
    "0x005dc72c",
    "309/1408 = 21.95%",
    "6152/6152 = 100.00%",
    BACKUP_PATH,
    "no mutation",
)

OVERCLAIMS = (
    "runtime pause-menu behavior proven",
    "runtime controller-binding behavior proven",
    "runtime options persistence behavior proven",
    "layout proven",
    "source-body identity proven",
    "rebuild parity proven",
    "patching proven",
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


def check_counts(failures: list[str]) -> None:
    expected = {
        "metadata.tsv": 12,
        "tags.tsv": 12,
        "xrefs.tsv": 25,
        "instructions.tsv": 444,
        "body-instructions.tsv": 956,
        "decompile/index.tsv": 12,
        "vtable-slots.tsv": 120,
    }
    for relative, count in expected.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == count, f"{relative} row count mismatch: {actual} != {count}", failures)


def check_artifacts(failures: list[str]) -> None:
    metadata = {norm(row["address"]): row for row in read_tsv(BASE / "metadata.tsv")}
    tags = {norm(row["address"]): row for row in read_tsv(BASE / "tags.tsv")}
    xrefs = read_tsv(BASE / "xrefs.tsv")
    body = read_tsv(BASE / "body-instructions.tsv")
    vtables = read_tsv(BASE / "vtable-slots.tsv")

    for address, (name, signature) in EXPECTED_METADATA.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row:
            require(row.get("name") == name, f"name mismatch at {address}: {row.get('name')}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in COMMENT_TOKENS.get(address, ()):
                require(token in row.get("comment", ""), f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row:
            tag_text = tag_row.get("tags", "")
            for token in TAG_TOKENS.get(address, ()):
                require(token in tag_text, f"missing tag token at {address}: {token}", failures)

    for target, from_addr, from_name, ref_type in XREF_EVIDENCE:
        require(
            any(
                norm(row.get("target_addr", "")) == target
                and norm(row.get("from_addr", "")) == from_addr
                and row.get("from_function", "") == from_name
                and row.get("ref_type", "") == ref_type
                for row in xrefs
            ),
            f"missing xref evidence: {target} from {from_addr}",
            failures,
        )

    for target, instr_addr, mnemonic, operand_token in INSTRUCTION_EVIDENCE:
        require(
            any(
                norm(row.get("target_addr", "")) == target
                and norm(row.get("instruction_addr", "")) == instr_addr
                and row.get("mnemonic", "") == mnemonic
                and operand_token in row.get("operands", "")
                for row in body
            ),
            f"missing instruction evidence: {target} {instr_addr} {mnemonic} {operand_token}",
            failures,
        )

    for vtable, slot, pointer, function_name in VTABLE_EVIDENCE:
        require(
            any(
                norm(row.get("vtable", "")) == vtable
                and row.get("slot_index", "") == slot
                and norm(row.get("pointer_addr", "")) == pointer
                and row.get("function_name", "") == function_name
                and row.get("status", "") == "OK"
                for row in vtables
            ),
            f"missing vtable evidence: {vtable} slot {slot}",
            failures,
        )


def check_logs(failures: list[str]) -> None:
    expected = {
        "metadata.log": "targets=12 found=12 missing=0",
        "tags.log": "ExportFunctionTagsByAddress complete: rows=12 missing=0",
        "xrefs.log": "Wrote 25 rows",
        "instructions.log": "Wrote 444 instruction rows",
        "body-instructions.log": "Wrote 956 function-body instruction rows",
        "decompile.log": "targets=12 dumped=12 missing=0 failed=0",
        "vtable-slots.log": "ExportVtableSlots complete: targets=5 rows=120",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR", "MISSING:", "FAIL:", "missing=1", "failed=1", "bad=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6152, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    rows = read_tsv(QUALITY_TSV)
    commented = sum(1 for row in rows if row.get("comment", "").strip())
    strict_clean = sum(
        1
        for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not re.search(r"\bparam_\d+\b", row.get("signature", ""))
    )
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
    core_docs = [
        NOTE,
        CAMPAIGN,
        GHIDRA_REFERENCE,
        FUNCTION_INDEX,
        PAUSEMENU_DOC,
        MENUITEM_DOC,
        ENGINE_DOC,
        GAME_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in CORE_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:ghidra-game-menu-options-bridge-review-wave962")
        == r"py -3 tools\ghidra_game_menu_options_bridge_review_wave962_probe.py --check",
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
        print("Wave962 game-menu/options bridge probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave962 game-menu/options bridge probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
