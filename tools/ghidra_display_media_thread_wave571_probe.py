#!/usr/bin/env python3
"""Validate Wave571 display/media thread Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave571-display-media-thread-005286e0"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_display_media_thread_wave571_2026-05-19.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
DXTEXTURE_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXTexture.cpp" / "_index.md"
DISPLAY_SETTINGS = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "display-settings.md"
DXFEV = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXFrontEndVideo.cpp.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"


COMMON_TAGS = {"static-reaudit", "display-media-thread-wave571", "retail-binary-evidence", "signature-corrected", "comment-hardened"}

TARGETS = {
    "0x005286e0": {
        "raw": "005286e0",
        "name": "CD3DApplication__LoadCardIdAndApplyVendorTweaks",
        "signature": "void __cdecl CD3DApplication__LoadCardIdAndApplyVendorTweaks(void * cardid_path)",
        "tags": COMMON_TAGS | {"cardid", "display", "tweak-loader"},
        "comment_tokens": ("cardid.txt tweak loader", "DAT_0089c018", "Setting tweak", "runtime D3D behavior"),
        "decompile_tokens": ("fopen(cardid_path", "DAT_0089c018", "s_Setting_tweak__s_to__f"),
    },
    "0x00528aa0": {
        "raw": "00528aa0",
        "name": "CVar__Init",
        "signature": "void __thiscall CVar__Init(void * this, void * cvar_name, int initial_value)",
        "tags": COMMON_TAGS | {"constructor", "cvar"},
        "comment_tokens": ("RET 0x8 confirms", "DAT_0089c018", "initial_value at this+0x0c"),
        "decompile_tokens": ("DAT_0089c018 = this", "initial_value"),
    },
    "0x00528ad0": {
        "raw": "00528ad0",
        "name": "CVar__SetValueRounded",
        "signature": "void __thiscall CVar__SetValueRounded(void * this, float value)",
        "tags": COMMON_TAGS | {"cvar", "numeric-setter"},
        "comment_tokens": ("RET 0x4 confirms", "rounds value with FISTP", "this+0x0c"),
        "decompile_tokens": ("ROUND(value)", "this + 0xc"),
    },
    "0x00528af0": {
        "raw": "00528af0",
        "name": "CDXTexture__IsResourceHandleValid",
        "signature": "bool __thiscall CDXTexture__IsResourceHandleValid(void * this)",
        "tags": COMMON_TAGS | {"predicate", "resource-handle", "texture"},
        "comment_tokens": ("this+0x0c", "returns whether the handle is valid", "CDXTexture__LoadTextureFromFile"),
        "decompile_tokens": ("this + 0xc", "!= -1"),
    },
    "0x00528b00": {
        "raw": "00528b00",
        "name": "CEngine__InvokeCallbackIfStateMinusOne",
        "signature": "void __thiscall CEngine__InvokeCallbackIfStateMinusOne(void * this, int callback_value)",
        "tags": COMMON_TAGS | {"callback-gate"},
        "comment_tokens": ("old second stack parameter was phantom", "callback_value", "No owner rename"),
        "decompile_tokens": ("callback_value", "this + 0xc", "== -1"),
    },
    "0x00528b60": {
        "raw": "00528b60",
        "name": "CBinkOpenThread__WorkerMain",
        "signature": "int __stdcall CBinkOpenThread__WorkerMain(void * thread_obj)",
        "tags": COMMON_TAGS | {"bink-thread", "thread-proc"},
        "comment_tokens": ("Win32 thread proc", "running flag +0x15", "completion event +0x10"),
        "decompile_tokens": ("WaitForSingleObject", "ReleaseMutex", "SetEvent", "thread_obj + 0x15"),
    },
    "0x00528bc0": {
        "raw": "00528bc0",
        "name": "CWaitingThread__ctor_base",
        "signature": "void * __thiscall CWaitingThread__ctor_base(void * this)",
        "tags": COMMON_TAGS | {"constructor", "owner-corrected", "waiting-thread"},
        "comment_tokens": ("base waiting-thread constructor", "DAT_0089c01c", "COggLoader, CBinkOpenThread"),
        "decompile_tokens": ("DAT_0089c01c", "this + 0x18", "return this"),
    },
    "0x00528c70": {
        "raw": "00528c70",
        "name": "CBinkOpenThread__Init",
        "signature": "bool __thiscall CBinkOpenThread__Init(void * this)",
        "tags": COMMON_TAGS | {"bink-thread", "thread-init"},
        "comment_tokens": ("creates the mutex", "worker thread", "CBinkOpenThread__WorkerMain"),
        "decompile_tokens": ("CreateMutexA", "CreateEventA", "CreateThread", "CBinkOpenThread__WorkerMain"),
    },
    "0x00528d10": {
        "raw": "00528d10",
        "name": "CBinkOpenThread__WaitForThread",
        "signature": "void __thiscall CBinkOpenThread__WaitForThread(void * this)",
        "tags": COMMON_TAGS | {"bink-thread", "wait-helper"},
        "comment_tokens": ("Sleep(0)", "running flag +0x15", "front-end video open"),
        "decompile_tokens": ("CBinkOpenThread__Init(this)", "Sleep(0)", "WaitForSingleObject"),
    },
    "0x00528d50": {
        "raw": "00528d50",
        "name": "CBinkOpenThread__StartAsync",
        "signature": "void __thiscall CBinkOpenThread__StartAsync(void * this)",
        "tags": COMMON_TAGS | {"async-start", "bink-thread"},
        "comment_tokens": ("sets running flag +0x15", "signals work event +0x0c", "message-box voice"),
        "decompile_tokens": ("this + 0x15", "ReleaseMutex", "SetEvent"),
    },
    "0x00528d70": {
        "raw": "00528d70",
        "name": "CBinkOpenThread__RunSync",
        "signature": "void __thiscall CBinkOpenThread__RunSync(void * this)",
        "tags": COMMON_TAGS | {"bink-thread", "sync-run"},
        "comment_tokens": ("synchronous-run helper", "CDXFrontEndVideo__Open", "releases mutex +0x08"),
        "decompile_tokens": ("ReleaseMutex", "this + 8"),
    },
    "0x00528d90": {
        "raw": "00528d90",
        "name": "CBinkOpenThread__IsRunning",
        "signature": "bool __thiscall CBinkOpenThread__IsRunning(void * this)",
        "tags": COMMON_TAGS | {"bink-thread", "field-reader"},
        "comment_tokens": ("running-flag reader", "this+0x15", "Goodies loading polling"),
        "decompile_tokens": ("return (bool)", "this + 0x15"),
    },
    "0x00528da0": {
        "raw": "00528da0",
        "name": "CBinkOpenThread__Lock",
        "signature": "void __thiscall CBinkOpenThread__Lock(void * this)",
        "tags": COMMON_TAGS | {"bink-thread", "lock-helper"},
        "comment_tokens": ("ensures CBinkOpenThread__Init", "mutex +0x08", "CDXFrontEndVideo update"),
        "decompile_tokens": ("CBinkOpenThread__Init(this)", "WaitForSingleObject", "this + 8"),
    },
    "0x00528dc0": {
        "raw": "00528dc0",
        "name": "CBinkOpenThread__Unlock",
        "signature": "void __thiscall CBinkOpenThread__Unlock(void * this)",
        "tags": COMMON_TAGS | {"bink-thread", "unlock-helper"},
        "comment_tokens": ("releases mutex +0x08", "Goodies loading", "CDXFrontEndVideo"),
        "decompile_tokens": ("ReleaseMutex", "this + 8"),
    },
}


def normalize_address(address: str) -> str:
    value = address.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def read_tsv(path: Path, key: str = "address") -> dict[str, dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    return {normalize_address(row[key]): row for row in rows}


def row_count(path: Path) -> int:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8", newline="") as handle:
        return sum(1 for _ in csv.DictReader(handle, delimiter="\t"))


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")


def require_tokens(label: str, text: str, tokens: tuple[str, ...] | set[str], failures: list[str]) -> None:
    for token in tokens:
        if token not in text:
            failures.append(f"{label} missing token: {token}")


def require_log_summary(path: Path, expected: dict[str, int], failures: list[str]) -> None:
    text = read_text(path)
    match = re.search(r"SUMMARY\s+([^\r\n]+)", text)
    if not match:
        failures.append(f"{path.name} missing SUMMARY")
        return
    values: dict[str, int] = {}
    for key, value in re.findall(r"([a-z_]+)=([0-9]+)", match.group(1)):
        values[key] = int(value)
    for key, expected_value in expected.items():
        actual = values.get(key)
        if actual != expected_value:
            failures.append(f"{path.name} {key} mismatch: {actual} != {expected_value}")
    if "REPORT: Save succeeded" not in text:
        failures.append(f"{path.name} missing save-success report")
    for bad_token in ("FAIL:", "LockException", "Read-back mismatch", "Function not found", "Input file not found"):
        if bad_token in text:
            failures.append(f"{path.name} contains {bad_token}")


def require_doc_tokens(path: Path, tokens: tuple[str, ...], failures: list[str]) -> None:
    try:
        text = read_text(path)
    except FileNotFoundError:
        failures.append(f"missing doc: {path}")
        return
    require_tokens(str(path.relative_to(ROOT)), text, tokens, failures)


def run_check() -> list[str]:
    failures: list[str] = []

    require_log_summary(BASE / "apply_dry.log", {"updated": 0, "skipped": 14, "renamed": 0, "would_rename": 1, "missing": 0, "bad": 0}, failures)
    require_log_summary(BASE / "apply.log", {"updated": 14, "skipped": 0, "renamed": 1, "would_rename": 0, "missing": 0, "bad": 0}, failures)
    require_log_summary(BASE / "apply_verify_dry.log", {"updated": 0, "skipped": 14, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}, failures)

    expected_counts = {
        "post_metadata.tsv": 14,
        "post_tags.tsv": 14,
        "post_xrefs.tsv": 129,
        "post_target_instructions.tsv": 1134,
        "post_decompile/index.tsv": 14,
    }
    for relative_path, expected in expected_counts.items():
        actual = row_count(BASE / relative_path)
        if actual != expected:
            failures.append(f"{relative_path} row count mismatch: {actual} != {expected}")

    metadata = read_tsv(BASE / "post_metadata.tsv")
    tags = read_tsv(BASE / "post_tags.tsv")
    decomp_index = read_tsv(BASE / "post_decompile" / "index.tsv")
    xrefs = read_text(BASE / "post_xrefs.tsv")
    instructions = read_text(BASE / "post_target_instructions.tsv")

    overclaim_tokens = ("runtime behavior proven", "runtime D3D behavior proven", "source identity proven", "rebuild parity proven", "fully RE'ed", "fully REed")
    for address, spec in TARGETS.items():
        row = metadata.get(address)
        if row is None:
            failures.append(f"{address} missing from post_metadata.tsv")
            continue
        if row["status"] != "OK":
            failures.append(f"{address} metadata status is {row['status']}")
        if row["name"] != spec["name"]:
            failures.append(f"{address} name mismatch: {row['name']} != {spec['name']}")
        if row["signature"] != spec["signature"]:
            failures.append(f"{address} signature mismatch: {row['signature']} != {spec['signature']}")
        require_tokens(f"{address} comment", row["comment"], spec["comment_tokens"], failures)
        for bad_token in overclaim_tokens:
            if bad_token in row["comment"]:
                failures.append(f"{address} comment overclaims: {bad_token}")

        tag_row = tags.get(address)
        if tag_row is None:
            failures.append(f"{address} missing from post_tags.tsv")
        else:
            present = set(filter(None, tag_row["tags"].split(";")))
            missing_tags = set(spec["tags"]) - present
            if missing_tags:
                failures.append(f"{address} missing tags: {sorted(missing_tags)}")
            for forbidden in ("source-parity", "runtime-proven", "rebuild-parity"):
                if forbidden in present:
                    failures.append(f"{address} unexpectedly has {forbidden} tag")

        decomp_row = decomp_index.get(address)
        if decomp_row is None:
            failures.append(f"{address} missing from post_decompile index")
        elif decomp_row["status"] != "OK":
            failures.append(f"{address} decompile status is {decomp_row['status']}")
        else:
            decomp_file = next((BASE / "post_decompile").glob(f"{spec['raw']}_*.c"), None)
            if decomp_file is None:
                failures.append(f"{address} missing decompile file")
            else:
                require_tokens(f"{address} decompile", read_text(decomp_file), spec["decompile_tokens"], failures)

    require_tokens(
        "xrefs",
        xrefs,
        (
            "005286e0\tCD3DApplication__LoadCardIdAndApplyVendorTweaks\t0052af3f\t0052af00\tCD3DApplication__Initialize3DEnvironment\tUNCONDITIONAL_CALL",
            "00528bc0\tCWaitingThread__ctor_base\t004b6d4e\t004b6d30\tCOggLoader__ctor_base\tUNCONDITIONAL_CALL",
            "00528bc0\tCWaitingThread__ctor_base\t00541123\t00541120\tCBinkOpenThread__ctor\tUNCONDITIONAL_CALL",
            "00528d50\tCBinkOpenThread__StartAsync\t005413f6\t005412e0\tCDXFrontEndVideo__Open\tUNCONDITIONAL_CALL",
            "00528d90\tCBinkOpenThread__IsRunning\t004b7dbc\t004b7d90\tCGame__PumpBinkVoiceSampleQueue\tUNCONDITIONAL_CALL",
            "00528da0\tCBinkOpenThread__Lock\t00541d43\t00541d30\tCDXFrontEndVideo__Update\tUNCONDITIONAL_CALL",
            "00528dc0\tCBinkOpenThread__Unlock\t0045ccb8\t0045cc10\tCFEPGoodies__LoadingGoodyPoll\tUNCONDITIONAL_CALL",
        ),
        failures,
    )
    require_tokens(
        "instructions",
        instructions,
        (
            "0x00528aa0\t0x00528aa0\tAFTER\t10\t0x00528aca\t0x00528aa0\tCVar__Init\tRET\t0x8",
            "0x00528ad0\t0x00528ad0\tAFTER\t6\t0x00528ae5\t0x00528ad0\tCVar__SetValueRounded\tRET\t0x4",
            "0x00528af0\t0x00528af0\tAFTER\t2\t0x00528af5\t0x00528af0\tCDXTexture__IsResourceHandleValid\tCMP\tEDX, -0x1",
            "0x00528b00\t0x00528b00\tAFTER\t7\t0x00528b12\t0x00528b00\tCEngine__InvokeCallbackIfStateMinusOne\tRET\t0x4",
            "0x00528b60\t0x00528b60\tAFTER\t35\t0x00528baf\t0x00528b60\tCBinkOpenThread__WorkerMain\tRET\t0x4",
            "0x00528bc0\t0x00528bc0\tAFTER\t12\t0x00528be8\t0x00528bc0\tCWaitingThread__ctor_base\tMOV\t[0x0089c01c], EAX",
            "0x00528d50\t0x00528d50\tAFTER\t8\t0x00528d65\t0x00528d50\tCBinkOpenThread__StartAsync\tCALL\tdword ptr [0x005d8120]",
            "0x00528dc0\t0x00528dc0\tAFTER\t2\t0x00528dc4\t0x00528dc0\tCBinkOpenThread__Unlock\tCALL\tdword ptr [0x005d81c0]",
        ),
        failures,
    )

    require_doc_tokens(PUBLIC_NOTE, ("Wave571", "Display/Media Thread", "No runtime D3D/media/thread behavior was claimed", "Post-Wave571"), failures)
    require_doc_tokens(FUNCTION_INDEX, ("Wave571 display/media", "0x005286e0", "0x00528dc0"), failures)
    require_doc_tokens(DXTEXTURE_INDEX, ("Wave571", "CDXTexture__IsResourceHandleValid", "this+0x0c"), failures)
    require_doc_tokens(DISPLAY_SETTINGS, ("Wave571", "CD3DApplication__LoadCardIdAndApplyVendorTweaks", "DAT_0089c018"), failures)
    require_doc_tokens(DXFEV, ("Wave571", "CWaitingThread__ctor_base", "CBinkOpenThread__Lock"), failures)
    require_doc_tokens(GHIDRA_REFERENCE, ("Wave571 display/media", "0x005286e0", "0x00528dc0"), failures)
    require_doc_tokens(CAMPAIGN, ("Wave571", "display/media", "comment-backed proxy"), failures)
    require_doc_tokens(BACKLOG, ("Wave571", "CD3DApplication__LoadCardIdAndApplyVendorTweaks", "queued next"), failures)

    if not QUEUE_JSON.is_file():
        failures.append("missing current queue JSON")
    else:
        data = json.loads(QUEUE_JSON.read_text(encoding="utf-8"))
        if data.get("status") != "PASS":
            failures.append(f"queue status is {data.get('status')}")
        quality = data.get("qualitySignals", {})
        expected_quality = {
            "commentlessFunctionCount": 3244,
            "undefinedSignatureCount": 1485,
            "paramSignatureCount": 1153,
        }
        for key, expected in expected_quality.items():
            actual = quality.get(key)
            if actual != expected:
                failures.append(f"queue JSON {key} mismatch: {actual} != {expected}")
        first = (data.get("priorityQueues", {}).get("commentlessHighSignal") or [{}])[0]
        if first.get("address") != "0x00528f80":
            failures.append(f"queue head mismatch: {first.get('address')}")

    if not LEDGER.is_file():
        failures.append("missing mutation ledger")
    else:
        ledger_text = LEDGER.read_text(encoding="utf-8")
        require_tokens("ledger", ledger_text, ("Wave571", "display-media-thread-wave571", "0x005286e0", "0x00528dc0"), failures)

    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="validate Wave571 artifacts")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of text")
    args = parser.parse_args()
    failures = run_check()
    if args.json:
        print(json.dumps({"ok": not failures, "failures": failures}, indent=2))
    else:
        if failures:
            print("FAIL")
            for failure in failures:
                print(f"- {failure}")
        else:
            print("PASS Wave571 display/media thread probe")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
