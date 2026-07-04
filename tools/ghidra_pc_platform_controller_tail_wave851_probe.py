#!/usr/bin/env python3
"""Validate Wave851 PC platform/controller tail read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave851-pc-platform-controller-tail"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_pc_platform_controller_tail_wave851_2026-05-25.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
ENGINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "engine.cpp" / "_index.md"
CONTROLLER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Controller.cpp" / "_index.md"
PCPLATFORM_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "PCPlatform.cpp" / "_index.md"
PLATFORMINPUT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "PlatformInput.cpp" / "_index.md"
MUSIC_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Music.cpp" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

TASK = "Wave851 PC platform/controller tail"
BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260525-085618_post_wave851_pc_platform_controller_tail_verified"
NEXT_HEAD = "0x00515ab0 D3DDevice__SetViewport"

TARGETS = {
    "0x005140e0": {
        "name": "CDXEngine__CaptureAviFrame",
        "signature": "void CDXEngine__CaptureAviFrame(void)",
        "tokens": ("Wave851 static read-back", "AVIStreamWrite", "DAT_008892d5", "DAT_00889188"),
        "tags": {"pc-runtime", "avi-capture", "post-render"},
    },
    "0x00514210": {
        "name": "OptionsEntries__InitDefaultSingleBindingsTable",
        "signature": "void __cdecl OptionsEntries__InitDefaultSingleBindingsTable(void)",
        "tokens": ("Wave851 static read-back", "47 OptionsEntries__InitSingleBindingEntry", "DAT_008898b8"),
        "tags": {"controller", "options-bindings", "source-pccontroller"},
    },
    "0x00514620": {
        "name": "CPCController__scalar_deleting_dtor",
        "signature": "void * __thiscall CPCController__scalar_deleting_dtor(void * this, uchar free_flag)",
        "tokens": ("Wave851 static read-back", "CController__dtor_Thunk", "CDXMemoryManager__Free"),
        "tags": {"controller", "destructor", "vtable"},
    },
    "0x00514640": {
        "name": "CPCController__GetJoyAnalogueLeftX",
        "signature": "float __stdcall CPCController__GetJoyAnalogueLeftX(int pad_number)",
        "tokens": ("vtable slot 9", "field +0x00", "0.001 constant"),
        "tags": {"controller", "analogue-input", "source-pccontroller"},
    },
    "0x00514670": {
        "name": "CPCController__GetJoyAnalogueLeftY",
        "signature": "float __stdcall CPCController__GetJoyAnalogueLeftY(int pad_number)",
        "tokens": ("vtable slot 10", "field +0x04", "0.001 constant"),
        "tags": {"controller", "analogue-input", "source-pccontroller"},
    },
    "0x005146a0": {
        "name": "CPCController__GetJoyAnalogueRightX",
        "signature": "float __stdcall CPCController__GetJoyAnalogueRightX(int pad_number)",
        "tokens": ("vtable slot 11", "field +0x08", "0.001 constant"),
        "tags": {"controller", "analogue-input", "source-pccontroller"},
    },
    "0x005146d0": {
        "name": "CPCController__GetJoyAnalogueRightY",
        "signature": "float __stdcall CPCController__GetJoyAnalogueRightY(int pad_number)",
        "tokens": ("vtable slot 12", "field +0x14", "32768"),
        "tags": {"controller", "analogue-input", "source-pccontroller"},
    },
    "0x005147b0": {
        "name": "CPCController__GetJoyButtonOnce",
        "signature": "bool __stdcall CPCController__GetJoyButtonOnce(int pad_number, int button)",
        "tokens": ("vtable slot 3", "old==0/current!=0", "LT.JoyButtonOnce"),
        "tags": {"controller", "button-input", "source-pccontroller"},
    },
    "0x005147f0": {
        "name": "CPCController__GetJoyButtonOn",
        "signature": "bool __stdcall CPCController__GetJoyButtonOn(int pad_number, int button)",
        "tokens": ("vtable slot 4", "current pad-state", "LT.JoyButtonOn"),
        "tags": {"controller", "button-input", "source-pccontroller"},
    },
    "0x00514810": {
        "name": "CPCController__GetJoyButtonRelease",
        "signature": "bool __stdcall CPCController__GetJoyButtonRelease(int pad_number, int button)",
        "tokens": ("vtable slot 5", "old!=0/current==0", "LT.JoyButtonRelease"),
        "tags": {"controller", "button-input", "source-pccontroller"},
    },
    "0x00514850": {
        "name": "CPCController__GetKeyOnce",
        "signature": "bool __stdcall CPCController__GetKeyOnce(int key)",
        "tokens": ("vtable slot 6", "PlatformInput__GetKeyOnceCore", "PLATFORM.KeyOnce"),
        "tags": {"controller", "keyboard-input", "source-pccontroller", "wave850-bridge"},
    },
    "0x00514870": {
        "name": "CPCController__GetKeyState3",
        "signature": "bool __stdcall CPCController__GetKeyState3(int key)",
        "tokens": ("vtable slot 8", "PlatformInput__GetKeyState3Core", "held-state"),
        "tags": {"controller", "keyboard-input", "wave850-bridge"},
    },
    "0x00514890": {
        "name": "CPCController__GetKeyOn",
        "signature": "bool __stdcall CPCController__GetKeyOn(int key)",
        "tokens": ("vtable slot 7", "PlatformInput__GetKeyOn", "PLATFORM.KeyOn"),
        "tags": {"controller", "keyboard-input", "source-pccontroller"},
    },
    "0x005148b0": {
        "name": "CPCController__GetJoyPovX",
        "signature": "float __stdcall CPCController__GetJoyPovX(int pad_number)",
        "tokens": ("vtable slot 13", "sin(POV", "0.00017453294"),
        "tags": {"controller", "pov-input"},
    },
    "0x00514900": {
        "name": "CPCController__GetJoyPovY",
        "signature": "float __stdcall CPCController__GetJoyPovY(int pad_number)",
        "tokens": ("vtable slot 14", "-cos(POV", "0.00017453294"),
        "tags": {"controller", "pov-input"},
    },
    "0x00514950": {
        "name": "PCPlatform__GetStorageDeviceCount",
        "signature": "int __stdcall PCPlatform__GetStorageDeviceCount(int * out_count)",
        "tokens": ("single PC storage device", "*out_count=1", "returns 0"),
        "tags": {"pc-platform", "save-storage", "frontend-storage"},
    },
    "0x00514960": {
        "name": "PCPlatform__GetStorageDeviceInfo",
        "signature": "int __stdcall PCPlatform__GetStorageDeviceInfo(int device, int * out_inserted, int * out_formatted, int * out_free_bytes, int * out_total_bytes)",
        "tokens": ("inserted=1", "formatted=1", "0x7fffffff"),
        "tags": {"pc-platform", "save-storage", "frontend-storage"},
    },
    "0x005149a0": {
        "name": "PCPlatform__GetStorageDeviceDisplayName",
        "signature": "int __stdcall PCPlatform__GetStorageDeviceDisplayName(int device, ushort * out_name)",
        "tokens": ("localization string id 0x28", "CRT__WStrCpy", "returns 0"),
        "tags": {"pc-platform", "save-storage", "localization"},
    },
    "0x00514be0": {
        "name": "EnumerateSaveFiles_Main",
        "signature": "int __stdcall EnumerateSaveFiles_Main(int device, short * save_name, int * out_index, int allowed_overwrite)",
        "tokens": ("Win32 wrappers", "returns 6", "attributes mask 0x16"),
        "tags": {"pc-platform", "save-storage", "save-enumeration"},
    },
    "0x00515190": {
        "name": "PCPlatform__CopyStorageDeviceId",
        "signature": "int __stdcall PCPlatform__CopyStorageDeviceId(int device, int * out_device)",
        "tokens": ("*out_device", "input device id", "returns 0"),
        "tags": {"pc-platform", "save-storage", "frontend-storage"},
    },
    "0x00515320": {
        "name": "PCPlatform__InitMusicPlaylist",
        "signature": "void __fastcall PCPlatform__InitMusicPlaylist(void * this)",
        "tokens": ("PCPlatform__InitAsyncMusicStream", "CMusic__LoadPlaylistFromDir", "Music.cpp"),
        "tags": {"music", "pc-platform", "playlist"},
    },
    "0x00515970": {
        "name": "PlatformInput__GetKeyOn",
        "signature": "uchar __stdcall PlatformInput__GetKeyOn(int key)",
        "tokens": ("DAT_00888c94[key]", "LT.xKeyOn", "CController__DoMappings"),
        "tags": {"platform-input", "keyboard-input", "source-pcplatform"},
    },
    "0x00515980": {
        "name": "PlatformInput__ConsumeKeyOnce",
        "signature": "uchar __stdcall PlatformInput__ConsumeKeyOnce(int key)",
        "tokens": ("DAT_00888d94[key]", "clears that byte", "LT.xKeyOnce"),
        "tags": {"platform-input", "keyboard-input", "source-pcplatform"},
    },
    "0x005159b0": {
        "name": "PlatformInput__ResetKeyStateTables",
        "signature": "void PlatformInput__ResetKeyStateTables(void)",
        "tokens": ("PlatformInput__ClearAllKeyStateTables", "frontend init", "FMV"),
        "tags": {"platform-input", "keyboard-input", "reset"},
    },
    "0x005159c0": {
        "name": "PLATFORM__SetKeySink",
        "signature": "void __stdcall PLATFORM__SetKeySink(void * key_sink)",
        "tokens": ("PlatformInput__SetKeySinkCore", "SetKeytrap", "key-sink"),
        "tags": {"platform-input", "key-sink", "controls-remap", "wave848-bridge"},
    },
}

COMMON_TAGS = {
    "static-reaudit",
    "pc-platform-controller-tail-wave851",
    "wave851-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-verified",
}

CORE_DOC_TOKENS = (
    TASK,
    "pc-platform-controller-tail-wave851",
    "0x005140e0 CDXEngine__CaptureAviFrame",
    "0x00514210 OptionsEntries__InitDefaultSingleBindingsTable",
    "0x00514620 CPCController__scalar_deleting_dtor",
    "0x00514640 CPCController__GetJoyAnalogueLeftX",
    "0x00514960 PCPlatform__GetStorageDeviceInfo",
    "0x00514be0 EnumerateSaveFiles_Main",
    "0x00515320 PCPlatform__InitMusicPlaylist",
    "0x00515970 PlatformInput__GetKeyOn",
    "0x005159c0 PLATFORM__SetKeySink",
    "5729/6098 = 93.95%",
    NEXT_HEAD,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime capture output proven",
    "runtime input behavior proven",
    "runtime save behavior proven",
    "runtime audio playback proven",
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


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in read_text(path).splitlines() if line.strip()]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


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
        "pre-metadata.tsv": 25,
        "pre-tags.tsv": 25,
        "pre-xrefs.tsv": 74,
        "pre-instructions.tsv": 1625,
        "pre-decompile/index.tsv": 25,
        "pre-context-metadata.tsv": 15,
        "pre-context-decompile/index.tsv": 15,
        "pre-cpccontroller-vtable.tsv": 20,
        "pre-music-vtable.tsv": 16,
        "post-metadata.tsv": 25,
        "post-tags.tsv": 25,
        "post-xrefs.tsv": 74,
        "post-instructions.tsv": 1625,
        "post-decompile/index.tsv": 25,
        "post-context-metadata.tsv": 15,
        "post-context-decompile/index.tsv": 15,
        "post-cpccontroller-vtable.tsv": 20,
        "post-music-vtable.tsv": 16,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    strings = {
        "string-0063df40.tsv": "AVIStreamWrite() failed!\\x0a",
        "string-0063df7c.tsv": r"savegames\*.bes",
        "string-0063df8c.tsv": ".bes",
        "string-0063df94.tsv": "savegames\\",
        "string-0063dff0.tsv": r"data\music",
    }
    for relative, expected in strings.items():
        rows = read_tsv(BASE / relative)
        require(rows and rows[0].get("cstring") == expected, f"{relative} string mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    for address, expected in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            comment = row.get("comment", "")
            require(row.get("name") == expected["name"], f"name mismatch at {address}", failures)
            require(row.get("signature") == expected["signature"], f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in expected["tokens"]:
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"common tags missing at {address}", failures)
            require(set(expected["tags"]).issubset(actual_tags), f"specific tags missing at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == expected["signature"], f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    vtable = read_text(BASE / "post-cpccontroller-vtable.tsv")
    for token in ("CPCController__GetJoyAnalogueLeftX", "CPCController__GetJoyButtonOnce", "CController__DoMappings", "CPCController__ReadControllerState"):
        require(token in vtable, f"missing CPCController vtable token: {token}", failures)
    music_vtable = read_text(BASE / "post-music-vtable.tsv")
    require("PCPlatform__InitMusicPlaylist" in music_vtable and "CMusic__Play" in music_vtable, "music vtable token mismatch", failures)

    source = read_text(BASE / "source-context.txt")
    for token in ("PCController.cpp", "GetJoyAnalogueLeftX", "PCPlatform.cpp", "LT.xKeyOn", "LT.xKeyOnce", "Music.cpp"):
        require(token in source, f"missing source context token: {token}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=25 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=25 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=25 found=25 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=25 missing=0",
        "post-xrefs.log": "Wrote 74 rows",
        "post-instructions.log": "Wrote 1625 instruction rows",
        "post-decompile.log": "targets=25 dumped=25 missing=0 failed=0",
        "post-context-metadata.log": "targets=15 found=15 missing=0",
        "post-context-decompile.log": "targets=15 dumped=15 missing=0 failed=0",
        "post-cpccontroller-vtable.log": "ExportVtableSlots complete: targets=1 rows=20",
        "post-music-vtable.log": "ExportVtableSlots complete: targets=1 rows=16",
        "quality-refresh.log": "total_functions=6098 commented_functions=5729",
        "queue-probe.log": '"commentlessFunctionCount": 369',
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave851.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave851_queue_probe.log",
    }
    for relative, token in expected.items():
        path = aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIG:", "BADCOMMENT:", "BADTAGS:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 369, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(queue["priorityQueues"]["commentlessHighSignal"] == [], "high-signal queue not empty", failures)
    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5729, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5729, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x00515ab0", "raw head address mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "D3DDevice__SetViewport", "raw head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 172034951, "backup byte count mismatch", failures)
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
        for token in CORE_DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    common_owner_tokens = (TASK, "pc-platform-controller-tail-wave851", "5729/6098 = 93.95%", NEXT_HEAD, BACKUP_PATH)
    owner_docs = {
        ENGINE_DOC: (
            "0x005140e0 CDXEngine__CaptureAviFrame",
            "AVIStreamWrite",
            "DAT_008892d5",
        ),
        CONTROLLER_DOC: (
            "0x00514210 OptionsEntries__InitDefaultSingleBindingsTable",
            "0x00514620 CPCController__scalar_deleting_dtor",
            "0x00514640 CPCController__GetJoyAnalogueLeftX",
            "CPCController__GetJoyButtonOnce",
        ),
        PCPLATFORM_DOC: (
            "0x00514960 PCPlatform__GetStorageDeviceInfo",
            "0x00514be0 EnumerateSaveFiles_Main",
            "0x00515320 PCPlatform__InitMusicPlaylist",
            "savegames\\*.bes",
        ),
        PLATFORMINPUT_DOC: (
            "0x00515970 PlatformInput__GetKeyOn",
            "0x005159c0 PLATFORM__SetKeySink",
            "PlatformInput__ConsumeKeyOnce",
            "PlatformInput__ResetKeyStateTables",
        ),
        MUSIC_DOC: (
            "0x00515320 PCPlatform__InitMusicPlaylist",
            "CMusic__LoadPlaylistFromDir",
            "data\\music",
        ),
    }
    for path, tokens in owner_docs.items():
        text = read_text(path)
        for token in common_owner_tokens + tokens:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:ghidra-pc-platform-controller-tail-wave851")
        == r"py -3 tools\ghidra_pc_platform_controller_tail_wave851_probe.py --check",
        "missing package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == TASK for row in ledger_rows), "missing Wave851 ledger row", failures)
    require(any(row.get("task") == TASK and row.get("attempt_id") == 20506 for row in attempts), "missing Wave851 attempt row", failures)


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
        print("Wave851 PC platform/controller tail probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave851 PC platform/controller tail probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
