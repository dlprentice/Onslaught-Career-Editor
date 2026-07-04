#!/usr/bin/env python3
"""Validate Wave951 CGame/GameInterface lifecycle read-only artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave951-game-interface-lifecycle-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_game_interface_lifecycle_wave951_2026-05-28.md"
PACKAGE_JSON = ROOT / "package.json"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
GAME_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "game.cpp" / "_index.md"
FRONTEND_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FrontEnd.cpp" / "_index.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260528-083735_post_wave951_game_interface_lifecycle_review_verified"

TARGETS = {
    "0x0046c210": ("CGame__ctor", "void * __fastcall CGame__ctor(void * this)"),
    "0x0046c2d0": ("CGame__dtor", "void __fastcall CGame__dtor(void * this)"),
    "0x004729d0": ("CGameInterface__ctor_base", "void __fastcall CGameInterface__ctor_base(void * this)"),
    "0x004729e0": ("CGameInterface__ResetMenuState", "void __fastcall CGameInterface__ResetMenuState(void * this)"),
    "0x00472ad0": ("CGameInterface__AdvanceMenuSelectionWithWrap", "void __fastcall CGameInterface__AdvanceMenuSelectionWithWrap(void * this)"),
}

COMMENT_TOKENS = {
    "0x0046c210": ("Wave385", "0x005dbbb4", "CGame settings"),
    "0x0046c2d0": ("Wave385", "active-reader", "CMonitor__Shutdown"),
    "0x004729d0": ("0x005dbc2c", "GAMEINTERFACE source call context", "runtime menu behavior"),
    "0x004729e0": ("CGame::Init", "six menu entries", "menu mode 1"),
    "0x00472ad0": ("wrap-around", "disabled entry flags", "frontend move sound"),
}

COMMON_TAGS = {"static-reaudit", "comment-hardened", "signature-hardened", "retail-binary-evidence"}
TARGET_TAGS = {
    "0x0046c210": {"game-dxgame-wave385", "cgame", "constructor", "owner-corrected"},
    "0x0046c2d0": {"game-dxgame-wave385", "cgame", "destructor", "owner-corrected"},
    "0x004729d0": {"game-interface-wave382", "game-interface", "constructor", "name-corrected"},
    "0x004729e0": {"game-interface-wave382", "game-interface", "menu-state", "pause-menu", "name-corrected"},
    "0x00472ad0": {"game-interface-wave382", "game-interface", "selection", "pause-menu", "name-corrected"},
}

TARGET_XREFS = {
    ("0x0046c210", "0x00541f13", "UNCONDITIONAL_CALL"),
    ("0x0046c2d0", "0x0046c2b3", "UNCONDITIONAL_CALL"),
    ("0x0046c2d0", "0x00541f00", "UNCONDITIONAL_JUMP"),
    ("0x004729d0", "0x004729a5", "UNCONDITIONAL_CALL"),
    ("0x004729e0", "0x0046c3ce", "UNCONDITIONAL_CALL"),
    ("0x004729e0", "0x0046c5b7", "UNCONDITIONAL_CALL"),
    ("0x00472ad0", "0x00472de2", "UNCONDITIONAL_CALL"),
}

CONTEXT_NAMES = {
    "0x0046c2b0": "CGame__scalar_deleting_dtor",
    "0x00541f00": "CDXGame__dtor_thunk",
    "0x00541f10": "CDXGame__ctor",
    "0x00541f30": "CDXGame__scalar_deleting_dtor",
    "0x0046c360": "CGame__Init",
    "0x0046c430": "CGame__InitRestartLoop",
    "0x00472a10": "CGameInterface__InitResources",
    "0x00472a50": "CGameInterface__Shutdown",
    "0x00472a90": "CGameInterface__ToggleMenuDisplay",
    "0x00472b40": "CGameInterface__HandleMenuSelection",
    "0x00472f10": "CGameInterface__Render",
}

DECOMPILE_TOKENS = {
    "0x0046c210": ("PTR_CGame__HandleEvent_005dbbb4", "+ 0x9f8", "+ 0xa04"),
    "0x0046c2d0": ("CSPtrSet__Remove", "CMonitor__Shutdown", "PTR_CGame__HandleEvent_005dbbb4"),
    "0x004729d0": ("PTR_SharedVFunc__NoOpOneArg_004014c0_005dbc2c", "+ 4"),
    "0x004729e0": ("iVar1 = 6", "+ 0x44", "+ 0x2c"),
    "0x00472ad0": ("CFrontEnd__PlaySound(0)", "+ 0x44", "+ 0x20"),
}

VTABLE_TOKENS = {
    ("005dbc2c", "2", "CGameInterface__Shutdown"),
    ("005e509c", "0", "CGame__HandleEvent"),
    ("005e509c", "1", "CDXGame__scalar_deleting_dtor"),
    ("005e509c", "3", "CGame__ReceiveButtonAction"),
}

CORE_TOKENS = (
    "Wave951",
    "game-interface-lifecycle-wave951",
    "0x0046c210 CGame__ctor",
    "0x0046c2d0 CGame__dtor",
    "0x004729d0 CGameInterface__ctor_base",
    "0x004729e0 CGameInterface__ResetMenuState",
    "0x00472ad0 CGameInterface__AdvanceMenuSelectionWithWrap",
    "0x0046c360 CGame__Init",
    "0x0046c430 CGame__InitRestartLoop",
    "271/1408 = 19.25%",
    "6150/6150 = 100.00%",
    BACKUP_PATH,
    "no mutation",
)

OVERCLAIMS = (
    "runtime pause/menu behavior proven",
    "runtime input behavior proven",
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
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def check_artifacts(failures: list[str]) -> None:
    counts = {
        "pre-metadata.tsv": 5,
        "pre-tags.tsv": 5,
        "pre-xrefs.tsv": 7,
        "pre-instructions.tsv": 146,
        "pre-decompile/index.tsv": 5,
        "context-metadata.tsv": 11,
        "context-tags.tsv": 11,
        "context-xrefs.tsv": 15,
        "context-instructions.tsv": 2080,
        "context-decompile/index.tsv": 11,
        "vtables.tsv": 64,
    }
    for relative, expected in counts.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == expected, f"{relative} row count mismatch: {actual} != {expected}", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-tags.tsv")}
    decompile_index = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-decompile" / "index.tsv")}
    xrefs = {
        (normalize_address(row["target_addr"]), normalize_address(row["from_addr"]), row["ref_type"])
        for row in read_tsv(BASE / "pre-xrefs.tsv")
    }
    context = {normalize_address(row["address"]): row for row in read_tsv(BASE / "context-metadata.tsv")}

    for address, (name, signature) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            comment = row.get("comment", "")
            for token in COMMENT_TOKENS[address]:
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            required_tags = COMMON_TAGS | TARGET_TAGS[address]
            require(required_tags.issubset(actual_tags), f"tags missing at {address}: {required_tags - actual_tags}", failures)

        dec = decompile_index.get(address)
        require(dec is not None and dec.get("status") == "OK", f"decompile index missing/failed at {address}", failures)
        if dec:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
        decompile = read_text(BASE / "pre-decompile" / f"{address[2:]}_{name}.c")
        for token in DECOMPILE_TOKENS[address]:
            require(token in decompile, f"missing decompile token in {name}: {token}", failures)

    for expected in TARGET_XREFS:
        require(expected in xrefs, f"missing xref {expected}", failures)

    for address, expected_name in CONTEXT_NAMES.items():
        row = context.get(address)
        require(row is not None, f"missing context metadata for {address}", failures)
        if row:
            require(row.get("name") == expected_name, f"context name mismatch at {address}", failures)
            require(row.get("status") == "OK", f"context status mismatch at {address}", failures)

    vtable_hits = {
        (row["vtable"].lower(), row["slot_index"], row["function_name"])
        for row in read_tsv(BASE / "vtables.tsv")
        if row.get("status") == "OK"
    }
    for token in VTABLE_TOKENS:
        require(token in vtable_hits, f"missing vtable token {token}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "pre-metadata.log": "targets=5 found=5 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=5 missing=0",
        "pre-xrefs.log": "Wrote 7 rows",
        "pre-instructions.log": "Wrote 146 function-body instruction rows",
        "pre-decompile.log": "targets=5 dumped=5 missing=0 failed=0",
        "context-metadata.log": "targets=11 found=11 missing=0",
        "context-tags.log": "ExportFunctionTagsByAddress complete: rows=11 missing=0",
        "context-xrefs.log": "Wrote 15 rows",
        "context-instructions.log": "Wrote 2080 function-body instruction rows",
        "context-decompile.log": "targets=11 dumped=11 missing=0 failed=0",
        "vtables.log": "ExportVtableSlots complete: targets=2 rows=64",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR", "FAIL:", "missing=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6150, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes", 0)) == 173542279, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [NOTE, CAMPAIGN, GAME_DOC, FRONTEND_DOC, DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE]
    for path in docs:
        text = read_text(path)
        for token in CORE_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-game-interface-lifecycle-wave951")
        == r"py -3 tools\ghidra_game_interface_lifecycle_wave951_probe.py --check",
        "missing package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs(failures)
    check_queue_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave951 game-interface lifecycle probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave951 game-interface lifecycle probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
