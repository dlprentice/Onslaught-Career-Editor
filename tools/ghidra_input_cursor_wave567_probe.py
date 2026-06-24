#!/usr/bin/env python3
"""Validate Wave567 input/cursor Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave567-input-cursor-005234e0"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_input_cursor_wave567_2026-05-18.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
INPUT_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Input.cpp" / "_index.md"
PLATFORM_INPUT_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "PlatformInput.cpp" / "_index.md"
FRONTEND_CURSOR = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FrontEnd.cpp" / "CFrontEnd__GetCursorStateInRect.md"
FRONTEND_CLICK = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FrontEnd.cpp" / "CFrontEnd__GetClickStateInRect.md"
FRONTEND_CONSUME = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FrontEnd.cpp" / "CFEPDirectory__GetCursorStateInRectAndConsumeIfMouseReady.md"
GAME_MAIN = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "game.cpp" / "CGame__MainLoop.md"
VBUFTEXTURE_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "vbuftexture.cpp" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"


TARGETS = {
    "0x005234d0": {
        "raw": "005234d0",
        "name": "PlatformInput__SetGlobalInputState",
        "signature": "void __cdecl PlatformInput__SetGlobalInputState(int global_input_state)",
        "tags": {
            "static-reaudit",
            "input-cursor-wave567",
            "retail-binary-evidence",
            "comment-hardened",
            "platform-input",
            "mouse-state",
            "signature-confirmed",
        },
        "comment_tokens": ("PlatformInput__InitMouse pushes 1", "PlatformInput__ShutdownMouse pushes 0", "DAT_0089bdf0"),
        "decompile_tokens": (
            "PlatformInput__SetGlobalInputState(int global_input_state)",
            "DAT_0089bdf0 = global_input_state;",
        ),
    },
    "0x005234e0": {
        "raw": "005234e0",
        "name": "Input__HandleMouseWindowMessage",
        "signature": "int __stdcall Input__HandleMouseWindowMessage(uint message, uint wparam, uint lparam)",
        "tags": {
            "static-reaudit",
            "input-cursor-wave567",
            "retail-binary-evidence",
            "comment-hardened",
            "mouse-message",
            "windows-message",
            "signature-corrected",
        },
        "comment_tokens": ("Windows mouse messages 0x200..0x20a", "LOWORD/HIWORD(lparam)", "HIWORD(wparam)"),
        "decompile_tokens": (
            "Input__HandleMouseWindowMessage(uint message,uint wparam,uint lparam)",
            "switch(message)",
            "case 0x200:",
            "case 0x20a:",
            "DAT_0089bda8 = lparam & 0xffff;",
            "DAT_0089bda4 = lparam >> 0x10;",
            "DAT_0089be48 = DAT_0089be48 + sVar4;",
        ),
    },
    "0x00523b50": {
        "raw": "00523b50",
        "name": "CDXEngine__GetCursorStateInRect",
        "signature": "int __cdecl CDXEngine__GetCursorStateInRect(float left, float top, float right, float bottom)",
        "tags": {
            "static-reaudit",
            "input-cursor-wave567",
            "retail-binary-evidence",
            "comment-hardened",
            "cursor-rect",
            "frontend-input",
            "signature-corrected",
        },
        "comment_tokens": ("four-float rectangle predicate", "[left,right)", "[top,bottom)"),
        "decompile_tokens": (
            "CDXEngine__GetCursorStateInRect(float left,float top,float right,float bottom)",
            "if (DAT_0089bdf4 == '\\0')",
            "left <= (float)DAT_0089bda8",
            "(float)DAT_0089bda8 < right",
            "top <= (float)DAT_0089bda4",
            "(float)DAT_0089bda4 < bottom",
        ),
    },
    "0x00523bc0": {
        "raw": "00523bc0",
        "name": "Input__DispatchClickInRect",
        "signature": "uint __cdecl Input__DispatchClickInRect(float left, float top, float right, float bottom, int button_action)",
        "tags": {
            "static-reaudit",
            "input-cursor-wave567",
            "retail-binary-evidence",
            "comment-hardened",
            "click-rect",
            "frontend-input",
            "button-dispatch",
            "signature-corrected",
        },
        "comment_tokens": ("button-action value", "DAT_0089bdfc", "CFrontEnd__ReceiveButtonAction"),
        "decompile_tokens": (
            "Input__DispatchClickInRect(float left,float top,float right,float bottom,int button_action)",
            "DAT_0089bdfc = 0;",
            "CFrontEnd__ReceiveButtonAction(&DAT_0089d758,DAT_008a9564,button_action,1.0);",
        ),
    },
    "0x00523cc0": {
        "raw": "00523cc0",
        "name": "Input__GetClickStateInRect",
        "signature": "uint __cdecl Input__GetClickStateInRect(float left, float top, float right, float bottom)",
        "tags": {
            "static-reaudit",
            "input-cursor-wave567",
            "retail-binary-evidence",
            "comment-hardened",
            "click-rect",
            "frontend-input",
            "consume-click",
            "signature-corrected",
        },
        "comment_tokens": ("click rectangle predicate", "consumes DAT_0089bdfc", "returns the result in AL"),
        "decompile_tokens": (
            "Input__GetClickStateInRect(float left,float top,float right,float bottom)",
            "DAT_0089bdfc = 0;",
            "return CONCAT31",
        ),
    },
    "0x00523d40": {
        "raw": "00523d40",
        "name": "Input__GetCursorStateInRectAndConsume",
        "signature": "uint __cdecl Input__GetCursorStateInRectAndConsume(float left, float top, float right, float bottom)",
        "tags": {
            "static-reaudit",
            "input-cursor-wave567",
            "retail-binary-evidence",
            "comment-hardened",
            "cursor-rect",
            "frontend-input",
            "consume-cursor",
            "signature-corrected",
        },
        "comment_tokens": ("cursor rectangle predicate", "consumes DAT_0089bdf4", "returns the result in AL"),
        "decompile_tokens": (
            "Input__GetCursorStateInRectAndConsume(float left,float top,float right,float bottom)",
            "DAT_0089bdf4 = 0;",
            "return CONCAT31",
        ),
    },
    "0x00523db0": {
        "raw": "00523db0",
        "name": "Input__ResetMouseTransientState",
        "signature": "void __cdecl Input__ResetMouseTransientState(void)",
        "tags": {
            "static-reaudit",
            "input-cursor-wave567",
            "retail-binary-evidence",
            "comment-hardened",
            "mouse-state",
            "transient-reset",
            "owner-corrected",
            "signature-corrected",
            "renamed",
        },
        "comment_tokens": ("supersedes the misleading CProfiler__ResetAll label", "0x0053f2dc/0x0053f306", "not exact source identity"),
        "decompile_tokens": (
            "Input__ResetMouseTransientState(void)",
            "DAT_00640054._0_1_ = 0xff;",
            "DAT_0089bdf8 = 0;",
            "DAT_0089be28 = 0;",
            "DAT_0089bdfc = 0;",
            "DAT_0089bdf4 = 0;",
            "DAT_0089be48 = 0;",
        ),
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


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")


def require_tokens(label: str, text: str, tokens: tuple[str, ...] | set[str], failures: list[str]) -> None:
    for token in tokens:
        if token not in text:
            failures.append(f"{label} missing token: {token}")


def run_check() -> list[str]:
    failures: list[str] = []
    metadata = read_tsv(BASE / "post_metadata.tsv")
    tags = read_tsv(BASE / "post_tags.tsv")
    decomp_index = read_tsv(BASE / "post_decompile" / "index.tsv")
    xrefs = read_text(BASE / "post_xrefs.tsv")
    instructions = read_text(BASE / "post_target_instructions.tsv")
    callsites = read_text(BASE / "post_input_callsite_instructions.tsv")

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

        tag_row = tags.get(address)
        if tag_row is None:
            failures.append(f"{address} missing from post_tags.tsv")
        else:
            present = set(filter(None, tag_row["tags"].split(";")))
            missing_tags = set(spec["tags"]) - present
            if missing_tags:
                failures.append(f"{address} missing tags: {sorted(missing_tags)}")
            if "source-parity" in present:
                failures.append(f"{address} unexpectedly has source-parity tag")

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
            "005234e0\tInput__HandleMouseWindowMessage\t00512f83\t<none>\t<no_function>\tUNCONDITIONAL_CALL",
            "00523b50\tCDXEngine__GetCursorStateInRect\t004693f5\t004693d0\tCFrontEnd__GetCursorStateInRect",
            "00523bc0\tInput__DispatchClickInRect\t004693ba\t00469390\tCFrontEnd__ProcessMouseReadyOrDispatchVBufTexture",
            "00523cc0\tInput__GetClickStateInRect\t00469425\t00469400\tCFrontEnd__GetClickStateInRect",
            "00523d40\tInput__GetCursorStateInRectAndConsume\t00469455\t00469430\tCFEPDirectory__GetCursorStateInRectAndConsumeIfMouseReady",
            "00523db0\tInput__ResetMouseTransientState\t0042d36e\t0042d310\tPlatformInput__InitMouse",
            "00523db0\tInput__ResetMouseTransientState\t0053f2dc\t<none>\t<no_function>\tUNCONDITIONAL_CALL",
        ),
        failures,
    )
    require_tokens(
        "instructions",
        instructions,
        (
            "0x005234d0\t0x005234d0\tAFTER\t7\t0x005234eb\t0x005234e0\tInput__HandleMouseWindowMessage\tRET\t0xc",
            "0x00523db0\t0x00523db0\tTARGET\t0\t0x00523db0\t0x00523db0\tInput__ResetMouseTransientState\tXOR\tEAX, EAX",
            "0x00523db0\t0x00523db0\tAFTER\t8\t0x00523dd7\t0x00523db0\tInput__ResetMouseTransientState\tMOV\t[0x0089bdf4], AL",
            "0x00523db0\t0x00523db0\tAFTER\t9\t0x00523ddc\t0x00523db0\tInput__ResetMouseTransientState\tMOV\t[0x0089be48], EAX",
        ),
        failures,
    )
    require_tokens(
        "input callsites",
        callsites,
        (
            "0x0042d397\t0x0042d397\tTARGET\t0\t0x0042d397\t0x0042d310\tPlatformInput__InitMouse\tCALL\t0x005234d0",
            "0x0042d3c4\t0x0042d3c4\tTARGET\t0\t0x0042d3c4\t0x0042d3b0\tPlatformInput__ShutdownMouse\tCALL\t0x005234d0",
            "0x00512f83\t0x00512f83\tTARGET\t0\t0x00512f83\t<none>\t<no_function>\tCALL\t0x005234e0",
            "0x0053f2dc\t0x0053f2dc\tTARGET\t0\t0x0053f2dc\t<none>\t<no_function>\tCALL\t0x00523db0",
            "0x0053f306\t0x0053f306\tTARGET\t0\t0x0053f306\t<none>\t<no_function>\tCALL\t0x00523db0",
        ),
        failures,
    )

    queue = json.loads(read_text(BASE / "post_static_reaudit_queue.json"))
    quality = queue.get("qualitySignals", {})
    expected_quality = {
        "commentlessFunctionCount": 3272,
        "undefinedSignatureCount": 1494,
        "paramSignatureCount": 1174,
    }
    if queue.get("status") != "PASS":
        failures.append(f"queue status is {queue.get('status')}")
    if queue.get("totalFunctions") != 6089:
        failures.append(f"queue totalFunctions mismatch: {queue.get('totalFunctions')} != 6089")
    for key, expected in expected_quality.items():
        if quality.get(key) != expected:
            failures.append(f"queue {key} mismatch: {quality.get(key)} != {expected}")

    docs = {
        "public note": (PUBLIC_NOTE, ("Wave567", "Input__HandleMouseWindowMessage", "Input__ResetMouseTransientState", "3272")),
        "function index": (FUNCTION_INDEX, ("Wave567", "Input__HandleMouseWindowMessage", "Input__ResetMouseTransientState")),
        "input index": (INPUT_INDEX, ("Wave567", "Input__DispatchClickInRect", "Input__ResetMouseTransientState")),
        "platform input index": (PLATFORM_INPUT_INDEX, ("Wave567", "PlatformInput__SetGlobalInputState", "DAT_0089bdf0")),
        "frontend cursor doc": (FRONTEND_CURSOR, ("Wave567", "left/top/right/bottom", "CDXEngine__GetCursorStateInRect")),
        "frontend click doc": (FRONTEND_CLICK, ("Wave567", "left/top/right/bottom", "Input__GetClickStateInRect")),
        "frontend consume doc": (FRONTEND_CONSUME, ("Wave567", "left/top/right/bottom", "Input__GetCursorStateInRectAndConsume")),
        "game main doc": (GAME_MAIN, ("Wave567", "Input__ResetMouseTransientState", "CProfiler__ResetAll")),
        "vbuftexture index": (VBUFTEXTURE_INDEX, ("Wave567", "Input__ResetMouseTransientState", "CVBufTexture::ResetAll")),
        "ghidra reference": (GHIDRA_REFERENCE, ("Wave567", "Input__HandleMouseWindowMessage", "Input__ResetMouseTransientState")),
        "campaign": (CAMPAIGN, ("Wave567", "2817", "3272", "OggVorbisStream__InitDecoder")),
        "backlog": (BACKLOG, ("Wave567", "Input__HandleMouseWindowMessage", "Input__ResetMouseTransientState")),
        "ledger": (LEDGER, ("Wave567", "0x005234d0,0x005234e0,0x00523b50", "comment-backed proxy 2817/6089")),
    }
    for label, (path, tokens) in docs.items():
        require_tokens(label, read_text(path), tokens, failures)

    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation and exit nonzero on failure")
    args = parser.parse_args()

    failures = run_check()
    print("Ghidra input/cursor Wave567 probe")
    if failures:
        print("Status: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1 if args.check else 0
    print("Status: PASS")
    print(f"Artifacts: {BASE}")
    print("Targets: 7")
    print("Queue: 6089 total, 2817 commented, 3272 commentless, 1494 undefined signatures, 1174 param_N signatures")
    return 0


if __name__ == "__main__":
    sys.exit(main())
