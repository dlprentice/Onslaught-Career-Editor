#!/usr/bin/env python3
"""Validate Wave824 MenuItem/PauseMenu raw-head read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave824-menuitem-pausemenu-raw-head"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_menuitem_pausemenu_raw_head_wave824_2026-05-24.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
MENUITEM_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "MenuItem.cpp" / "_index.md"
PAUSEMENU_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "PauseMenu.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260524-190751_post_wave824_menuitem_pausemenu_raw_head_verified"
NEXT_HEAD = "0x004d6240 StrCopyN"

TARGET_NAMES = {
    "0x004cf050": "CMenuItem__Destructor_Thunk",
    "0x004d04d0": "CPauseMenu__ReloadSharedBlankTexture",
    "0x004d05c0": "CMenuItemRange__IsBindingActive",
    "0x004d0de0": "CPauseMenu__GetBindingCapacityWarningText",
}

TARGET_SIGNATURES = {
    "0x004cf050": "void __thiscall CMenuItem__Destructor_Thunk(void * this)",
    "0x004d04d0": "void __cdecl CPauseMenu__ReloadSharedBlankTexture(void)",
    "0x004d05c0": "int __thiscall CMenuItemRange__IsBindingActive(void * this)",
    "0x004d0de0": "short * __cdecl CPauseMenu__GetBindingCapacityWarningText(void)",
}

COMMENT_TOKENS = {
    "0x004cf050": (
        "Wave824 static read-back/name correction",
        "single-instruction jump thunk",
        "0x004a3730 CMenuItem__Destructor",
        "0x004cf030 CMouseSensitivityMenuItem__scalar_deleting_dtor",
        "+0x1c",
        "+0x20",
        "+0x34",
        "not the destructor body itself",
    ),
    "0x004d04d0": (
        "Wave824 static read-back/signature hardening",
        "DAT_0082b490",
        "CTexture__DecrementRefCountFromNameField",
        "FrontEnd_v2/FE_Blank.tga",
        "CTexture__FindTexture",
    ),
    "0x004d05c0": (
        "Wave824 static read-back/comment hardening",
        "CMenuItemRange__Render",
        "this+0x08",
        "context+0x08",
        "returns 0",
    ),
    "0x004d0de0": (
        "Wave824 static read-back/name/signature correction",
        "Controls__FindFirstFreeBindingSlot(0)",
        "Localization__GetStringById(0xe8)",
        "CGame__IsMultiplayer(&DAT_008a9a98)",
        "Localization__GetStringById(0xe9)",
        "CPauseMenu__ButtonPressed",
    ),
}

TARGET_XREFS = {
    "0x004cf050": {"0x004cf033"},
    "0x004d04d0": {"0x004a3e30"},
    "0x004d05c0": {"0x004a4aea", "0x004a4b95"},
    "0x004d0de0": {"0x004d087d"},
}

COMMON_TAGS = {
    "static-reaudit",
    "menuitem-pausemenu-raw-head-wave824",
    "wave824-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "menuitem",
    "pause-menu",
}

EXTRA_TAGS = {
    "0x004cf050": {"name-corrected", "jump-thunk", "menuitem-destructor"},
    "0x004d04d0": {"pause-texture-cache", "blank-texture"},
    "0x004d05c0": {"binding-context", "predicate"},
    "0x004d0de0": {"name-corrected", "binding-capacity", "localized-warning"},
}

HELPER_NAMES = {
    "CMenuItem__Destructor",
    "CTexture__DecrementRefCountFromNameField",
    "CTexture__FindTexture",
    "Controls__FindFirstFreeBindingSlot",
    "Localization__GetStringById",
    "CGame__IsMultiplayer",
    "CMenuItemDropdown__Render",
    "CMenuItemRange__Render",
    "CPauseMenu__ButtonPressed",
}

CORE_ANCHORS = (
    "Wave824 MenuItem/PauseMenu raw-head",
    "menuitem-pausemenu-raw-head-wave824",
    "0x004cf050 CMenuItem__Destructor_Thunk",
    "0x004d04d0 CPauseMenu__ReloadSharedBlankTexture",
    "0x004d05c0 CMenuItemRange__IsBindingActive",
    "0x004d0de0 CPauseMenu__GetBindingCapacityWarningText",
    "5632/6098 = 92.36%",
    NEXT_HEAD,
    BACKUP_PATH,
)

OWNER_DOC_TOKENS = {
    MENUITEM_DOC: (
        "Wave824",
        "menuitem-pausemenu-raw-head-wave824",
        "0x004cf050 CMenuItem__Destructor_Thunk",
        "0x004d05c0 CMenuItemRange__IsBindingActive",
        "CMenuItemRange__Render",
        BACKUP_PATH,
    ),
    PAUSEMENU_DOC: (
        "Wave824",
        "menuitem-pausemenu-raw-head-wave824",
        "0x004d04d0 CPauseMenu__ReloadSharedBlankTexture",
        "0x004d0de0 CPauseMenu__GetBindingCapacityWarningText",
        "Localization__GetStringById(0xe8)",
        "Localization__GetStringById(0xe9)",
        BACKUP_PATH,
    ),
}

OVERCLAIM_TOKENS = (
    "runtime frontend behavior proven",
    "runtime pause-menu rendering behavior proven",
    "runtime controller remapping behavior proven",
    "fully reverse-engineered",
    "rebuild parity proven",
)


def normalize_address(address: str) -> str:
    value = address.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in read_text(path).splitlines() if line.strip()]


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


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


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 4,
        "pre-tags.tsv": 4,
        "pre-xrefs.tsv": 5,
        "pre-instructions.tsv": 964,
        "pre-decompile/index.tsv": 4,
        "pre-helper-metadata.tsv": 9,
        "pre-helper-instructions.tsv": 1629,
        "pre-caller-decompile/index.tsv": 4,
        "pre-caller-instructions.tsv": 684,
        "post-metadata.tsv": 4,
        "post-tags.tsv": 4,
        "post-xrefs.tsv": 5,
        "post-instructions.tsv": 964,
        "post-decompile/index.tsv": 4,
        "post-helper-metadata.tsv": 9,
        "post-helper-instructions.tsv": 1629,
        "post-caller-decompile/index.tsv": 4,
        "post-caller-instructions.tsv": 684,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    helper_names = {row["name"] for row in read_tsv(BASE / "post-helper-metadata.tsv")}
    xrefs: dict[str, set[str]] = {}
    for row in read_tsv(BASE / "post-xrefs.tsv"):
        xrefs.setdefault(normalize_address(row["target_addr"]), set()).add(normalize_address(row["from_addr"]))

    require(HELPER_NAMES.issubset(helper_names), f"missing helper rows: {HELPER_NAMES - helper_names}", failures)

    for address, name in TARGET_NAMES.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == TARGET_SIGNATURES[address], f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            comment = row.get("comment", "")
            for token in COMMENT_TOKENS[address]:
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            required = COMMON_TAGS | EXTRA_TAGS[address]
            require(required.issubset(actual_tags), f"tags missing at {address}: {required - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == TARGET_SIGNATURES[address], f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        require(TARGET_XREFS[address].issubset(xrefs.get(address, set())), f"xrefs missing at {address}", failures)

    destructor_decompile = read_text(BASE / "post-decompile" / "004cf050_CMenuItem__Destructor_Thunk.c")
    for token in ("CMenuItem__Destructor_Thunk", "CMenuItem__Destructor"):
        require(token in destructor_decompile, f"missing destructor thunk decompile token: {token}", failures)

    warning_decompile = read_text(BASE / "post-decompile" / "004d0de0_CPauseMenu__GetBindingCapacityWarningText.c")
    for token in ("Controls__FindFirstFreeBindingSlot", "Localization__GetStringById(0xe8)", "Localization__GetStringById(0xe9)"):
        require(token in warning_decompile, f"missing binding warning decompile token: {token}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=4 renamed=0 would_rename=2 signature_updated=3 comment_only_updated=1 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=4 skipped=0 renamed=2 would_rename=0 signature_updated=2 comment_only_updated=2 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=4 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=4 found=4 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=4 missing=0",
        "post-xrefs.log": "Wrote 5 rows",
        "post-instructions.log": "Wrote 964 instruction rows",
        "post-decompile.log": "targets=4 dumped=4 missing=0 failed=0",
        "post-helper-metadata.log": "targets=9 found=9 missing=0",
        "post-helper-instructions.log": "Wrote 1629 instruction rows",
        "post-caller-decompile.log": "targets=4 dumped=4 missing=0 failed=0",
        "post-caller-instructions.log": "Wrote 684 instruction rows",
        "quality-refresh.log": "total_functions=6098 commented_functions=5632",
        "queue-probe.log": "Commentless functions: 466",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave824.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave824_queue_probe.log",
    }
    for relative, token in expected.items():
        path = log_aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIG:", "BADCOMMENT:", "BADTAGS:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    apply_text = read_text(BASE / "apply.log")
    for token in (
        "READBACK_OK: 0x004cf050 void __thiscall CMenuItem__Destructor_Thunk(void * this)",
        "READBACK_OK: 0x004d0de0 short * __cdecl CPauseMenu__GetBindingCapacityWarningText(void)",
    ):
        require(token in apply_text, f"missing apply readback token: {token}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 466, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(queue["priorityQueues"]["commentlessHighSignal"] == [], "high-signal queue should be empty", failures)
    require(queue["priorityQueues"]["signature"] == [], "signature queue should be empty", failures)
    require(queue["priorityQueues"]["nameConfidence"] == [], "name-confidence queue should be empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5632, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5632, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x004d6240", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "StrCopyN", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 171576199 or backup.get("totalBytes") == 171576199.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = [
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in CORE_ANCHORS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    for path, tokens in OWNER_DOC_TOKENS.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-menuitem-pausemenu-raw-head-wave824")
        == r"py -3 tools\ghidra_menuitem_pausemenu_raw_head_wave824_probe.py --check",
        "missing package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave824 MenuItem/PauseMenu raw head" for row in ledger_rows), "missing Wave824 ledger row", failures)
    require(
        any(row.get("task") == "Wave824 MenuItem/PauseMenu raw head" and row.get("attempt_id") == 20479 for row in attempts),
        "missing Wave824 attempt row",
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
        print("Wave824 MenuItem/PauseMenu raw-head probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave824 MenuItem/PauseMenu raw-head probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
