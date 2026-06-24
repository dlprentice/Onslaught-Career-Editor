#!/usr/bin/env python3
"""Validate Wave572 D3D application-shell Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave572-d3d-application-shell-00528f80"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_d3d_application_shell_wave572_2026-05-19.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
DISPLAY_SETTINGS = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "display-settings.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"

COMMON_TAGS = {
    "static-reaudit",
    "d3d-application-shell-wave572",
    "retail-binary-evidence",
    "signature-corrected",
    "comment-hardened",
    "display",
    "d3d-application",
}

TARGETS = {
    "0x00528f80": {
        "raw": "00528f80",
        "name": "CD3DApplication__Init",
        "signature": "void * __thiscall CD3DApplication__Init(void * this)",
        "tags": COMMON_TAGS | {"constructor"},
        "comment_tokens": ("constructs ten adapter-info blocks", "DAT_0089c0f4", "640x480"),
        "decompile_file": "00528f80_CD3DApplication__Init.c",
        "decompile_tokens": ("DAT_0089c0f4 = this", "0x330bc", "0x330c0"),
    },
    "0x005290a0": {
        "raw": "005290a0",
        "name": "CD3DApplication__Create",
        "signature": "int __thiscall CD3DApplication__Create(void * this, void * hinstance)",
        "tags": COMMON_TAGS | {"window-create"},
        "comment_tokens": ("RET 0x4 confirms", "Direct3DCreate9(0x1f)", "initializes the 3D environment"),
        "decompile_file": "005290a0_CD3DApplication__Create.c",
        "decompile_tokens": ("Direct3DCreate9(0x1f)", "RegisterClassA", "CreateWindowExA", "CD3DApplication__Initialize3DEnvironment(this,false)"),
    },
    "0x00529350": {
        "raw": "00529350",
        "name": "CD3DApplication__BuildDeviceList",
        "signature": "int __thiscall CD3DApplication__BuildDeviceList(void * this)",
        "tags": COMMON_TAGS | {"device-enumeration", "mode-list"},
        "comment_tokens": ("adapter/device/mode enumeration", "DAT_0089c0ac", "DisplayErrorMsg"),
        "decompile_file": "00529350_CD3DApplication__BuildDeviceList.c",
        "decompile_tokens": ("s_D3D_>GetAdapterCount", "DAT_0089c0ac", "CD3DApplication__DisplayErrorMsg"),
    },
    "0x0052af00": {
        "raw": "0052af00",
        "name": "CD3DApplication__Initialize3DEnvironment",
        "signature": "int __thiscall CD3DApplication__Initialize3DEnvironment(void * this, bool reuse_existing_device)",
        "tags": COMMON_TAGS | {"cardid", "device-create-reset"},
        "comment_tokens": ("RET 0x4 confirms", "cardid.txt/CVar tweaks", "falls back from lockable backbuffer/multisampling"),
        "decompile_file": "0052af00_CD3DApplication__Initialize3DEnvironment.c",
        "decompile_tokens": ("CD3DApplication__LoadCardIdAndApplyVendorTweaks", "g_TryLockableBackbuffer", "s_Falling_back_to_no_multisampling", "CD3DApplication__SetDeviceCursorFromIcon"),
    },
    "0x0052b760": {
        "raw": "0052b760",
        "name": "CD3DApplication__Resize3DEnvironment",
        "signature": "int __thiscall CD3DApplication__Resize3DEnvironment(void * this)",
        "tags": COMMON_TAGS | {"device-reset"},
        "comment_tokens": ("ECX-only resize/reset helper", "this+0x32e58", "perf timer"),
        "decompile_file": "0052b760_CD3DApplication__Resize3DEnvironment.c",
        "decompile_tokens": ("CD3DApplication__SetDeviceCursorFromIcon", "CD3DApplication__PerfTimerCommand(1)", "CD3DApplication__PerfTimerCommand(2)"),
    },
    "0x0052b840": {
        "raw": "0052b840",
        "name": "CD3DApplication__ToggleFullscreen",
        "signature": "int __thiscall CD3DApplication__ToggleFullscreen(void * this)",
        "tags": COMMON_TAGS | {"fullscreen-toggle"},
        "comment_tokens": ("ECX-only fullscreen/windowed toggle", "ForceWindowed", "g_ScreenShape"),
        "decompile_file": "0052b840_CD3DApplication__ToggleFullscreen.c",
        "decompile_tokens": ("CD3DApplication__ForceWindowed(this,true)", "CD3DApplication__Resize3DEnvironment(this)", "SetWindowPos", "0x32e44"),
    },
    "0x0052ba50": {
        "raw": "0052ba50",
        "name": "CD3DApplication__ForceWindowed",
        "signature": "int __thiscall CD3DApplication__ForceWindowed(void * this, bool target_windowed_state)",
        "tags": COMMON_TAGS | {"force-windowed"},
        "comment_tokens": ("RET 0x4 proves", "target_windowed_state", "Initialize3DEnvironment"),
        "decompile_file": "0052ba50_CD3DApplication__ForceWindowed.c",
        "decompile_tokens": ("CD3DApplication__Initialize3DEnvironment(this,true)", "CD3DApplication__DisplayErrorMsg", "target_windowed_state"),
    },
    "0x0052bb80": {
        "raw": "0052bb80",
        "name": "CD3DApplication__Reset3DEnvironment",
        "signature": "int __thiscall CD3DApplication__Reset3DEnvironment(void * this, bool show_device_dialog, int reset_context)",
        "tags": COMMON_TAGS | {"device-reset", "dialog"},
        "comment_tokens": ("RET 0x8 proves", "SelectDeviceProc dialog", "reset_context"),
        "decompile_file": "0052bb80_CD3DApplication__Reset3DEnvironment.c",
        "decompile_tokens": ("DialogBoxParamA", "CD3DApplication__SelectDeviceProc", "CD3DApplication__Initialize3DEnvironment(this,true)"),
    },
    "0x0052bc80": {
        "raw": "0052bc80",
        "name": "CD3DApplication__SelectDeviceProc",
        "signature": "int __stdcall CD3DApplication__SelectDeviceProc(int dialog_hwnd, int message, int wparam, int lparam)",
        "tags": COMMON_TAGS | {"device-dialog", "stdcall-callback"},
        "comment_tokens": ("RET 0x10 confirms", "WM_INITDIALOG", "DAT_0089c048"),
        "decompile_file": "0052bc80_CD3DApplication__SelectDeviceProc.c",
        "decompile_tokens": ("GetDlgItem", "SendMessageA", "EndDialog", "DAT_0089c048"),
    },
    "0x0052c430": {
        "raw": "0052c430",
        "name": "CD3DApplication__Cleanup3DEnvironment",
        "signature": "void __thiscall CD3DApplication__Cleanup3DEnvironment(void * this)",
        "tags": COMMON_TAGS | {"cleanup"},
        "comment_tokens": ("ECX-only D3D cleanup helper", "DebugTrace", "D3D interfaces"),
        "decompile_file": "0052c430_CD3DApplication__Cleanup3DEnvironment.c",
        "decompile_tokens": ("DebugTrace", "DAT_0089c04c", "d3ddev"),
    },
    "0x0052c4f0": {
        "raw": "0052c4f0",
        "name": "CD3DApplication__DisplayErrorMsg",
        "signature": "int __stdcall CD3DApplication__DisplayErrorMsg(int error_code, int message_type)",
        "tags": COMMON_TAGS | {"error-dispatch"},
        "comment_tokens": ("RET 0x8 confirms", "localized string ids 0xb6-0xc5", "message_type"),
        "decompile_file": "0052c4f0_CD3DApplication__DisplayErrorMsg.c",
        "decompile_tokens": ("FatalError_LocalizedStringId", "0xc5", "return error_code"),
    },
    "0x0052c730": {
        "raw": "0052c730",
        "name": "CD3DApplication__SetResolution",
        "signature": "void __thiscall CD3DApplication__SetResolution(void * this, int width, int height)",
        "tags": COMMON_TAGS | {"resolution"},
        "comment_tokens": ("RET 0x8 confirms", "without an in-function clamp", "CLIParams__ParseCommandLine"),
        "decompile_file": "0052c730_CD3DApplication__SetResolution.c",
        "decompile_tokens": ("0x330bc) = width", "0x330c0) = height", "without an in-function clamp"),
    },
    "0x0052c780": {
        "raw": "0052c780",
        "name": "ScreenShape_UpdateAspectScale",
        "signature": "void __fastcall ScreenShape_UpdateAspectScale(void * d3d_app)",
        "tags": COMMON_TAGS | {"aspect-scale"},
        "comment_tokens": ("ECX-carried aspect-scale helper", "g_ScreenShape", "1.7777778"),
        "decompile_file": "0052c780_ScreenShape_UpdateAspectScale.c",
        "decompile_tokens": ("g_ScreenShape", "0x32e90", "0x3f800000"),
    },
    "0x0052c8d0": {
        "raw": "0052c8d0",
        "name": "CD3DApplication__SetDeviceCursorFromIcon",
        "signature": "int __cdecl CD3DApplication__SetDeviceCursorFromIcon(void * d3d_device, int icon_handle)",
        "tags": COMMON_TAGS | {"cursor"},
        "comment_tokens": ("icon-to-D3D cursor helper", "ICONINFO", "GDI"),
        "decompile_file": "0052c8d0_CD3DApplication__SetDeviceCursorFromIcon.c",
        "decompile_tokens": ("GetIconInfo", "GetDIBits", "hbmMask", "hbmColor"),
    },
    "0x0052cd20": {
        "raw": "0052cd20",
        "name": "CD3DApplication__PerfTimerCommand",
        "signature": "double __stdcall CD3DApplication__PerfTimerCommand(int command)",
        "tags": COMMON_TAGS | {"perf-timer"},
        "comment_tokens": ("RET 0x4 confirms", "QueryPerformanceCounter", "timeGetTime"),
        "decompile_file": "0052cd20_CD3DApplication__PerfTimerCommand.c",
        "decompile_tokens": ("double CD3DApplication__PerfTimerCommand", "QueryPerformanceCounter", "timeGetTime", "return (double)"),
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

    require_log_summary(
        BASE / "apply_dry_after_timer_return_fix.log",
        {"updated": 0, "skipped": 15, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "apply_after_timer_return_fix.log",
        {"updated": 15, "skipped": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "apply_verify_dry_after_timer_return_fix.log",
        {"updated": 0, "skipped": 15, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )

    expected_counts = {
        "post_metadata.tsv": 15,
        "post_tags.tsv": 15,
        "post_xrefs.tsv": 41,
        "post_target_instructions.tsv": 1815,
        "post_decompile/index.tsv": 15,
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

    overclaim_tokens = (
        "runtime behavior proven",
        "runtime D3D behavior proven",
        "source identity proven",
        "rebuild parity proven",
        "fully RE'ed",
        "fully REed",
    )
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
                    failures.append(f"{address} has forbidden tag {forbidden}")

        decomp_row = decomp_index.get(address)
        if decomp_row is None:
            failures.append(f"{address} missing from post_decompile/index.tsv")
        else:
            if decomp_row["signature"] != spec["signature"]:
                failures.append(f"{address} decompile index signature mismatch")
            decomp_text = read_text(BASE / "post_decompile" / spec["decompile_file"])
            require_tokens(f"{address} decompile", decomp_text, spec["decompile_tokens"], failures)

        if spec["raw"] not in instructions:
            failures.append(f"{address} missing from post_target_instructions.tsv")
        if spec["name"] not in xrefs and address not in xrefs:
            failures.append(f"{address} missing from post_xrefs.tsv")

    queue = json.loads(read_text(QUEUE_JSON))
    expected_queue = {
        "totalFunctions": 6093,
        "commentlessFunctionCount": 3230,
        "undefinedSignatureCount": 1479,
        "paramSignatureCount": 1144,
    }
    if queue.get("status") != "PASS":
        failures.append(f"queue status mismatch: {queue.get('status')}")
    if queue.get("totalFunctions") != expected_queue["totalFunctions"]:
        failures.append(f"queue totalFunctions mismatch: {queue.get('totalFunctions')}")
    signals = queue.get("qualitySignals", {})
    for key, expected in expected_queue.items():
        if key == "totalFunctions":
            continue
        actual = signals.get(key)
        if actual != expected:
            failures.append(f"queue {key} mismatch: {actual} != {expected}")
    head = queue.get("priorityQueues", {}).get("commentlessHighSignal", [{}])[0]
    if head.get("address") != "0x0052d040" or head.get("name") != "CAsmInstruction__GetAttributeValue":
        failures.append(f"queue head mismatch: {head}")

    require_doc_tokens(
        PUBLIC_NOTE,
        (
            "Ghidra D3D Application Shell Wave572 Readiness Note",
            "double __stdcall CD3DApplication__PerfTimerCommand(int command)",
            "without an in-function clamp",
            "BEA_20260519-003701_post_wave572_d3d_application_shell_verified",
            "2863 / 6093 = 46.99%",
            "2812 / 6093 = 46.15%",
        ),
        failures,
    )
    require_doc_tokens(
        GHIDRA_REFERENCE,
        (
            "Current Signature Caveat: D3D Application Shell (2026-05-19)",
            "Wave572 D3D application-shell hardened fifteen adjacent rows",
            "double __stdcall CD3DApplication__PerfTimerCommand(int command)",
            "runtime D3D behavior",
        ),
        failures,
    )
    require_doc_tokens(
        CAMPAIGN,
        (
            "Fresh headless export on 2026-05-19 after Wave572",
            "Current D3D application-shell follow-up",
            "Wave 572: D3D Application Shell",
            "2863/6093 = 46.99%",
        ),
        failures,
    )
    require_doc_tokens(
        FUNCTION_INDEX,
        (
            "Latest saved-correction note: Wave572",
            "CD3DApplication__Initialize3DEnvironment",
            "CD3DApplication__PerfTimerCommand",
            "Post-Wave572 queue telemetry",
        ),
        failures,
    )
    require_doc_tokens(
        DISPLAY_SETTINGS,
        (
            "Wave572 D3D Application Shell",
            "CD3DApplication__SetResolution",
            "does not clamp",
            "Runtime D3D behavior",
        ),
        failures,
    )
    require_doc_tokens(
        BACKLOG,
        (
            "Ghidra D3D application shell Wave572 signature/comment hardening",
            "apply_after_timer_return_fix",
            "160140167",
        ),
        failures,
    )
    require_doc_tokens(
        LEDGER,
        (
            "Ghidra D3D application shell Wave572 signature/comment hardening",
            "CD3DApplication__PerfTimerCommand",
            "BEA_20260519-003701_post_wave572_d3d_application_shell_verified",
        ),
        failures,
    )

    return failures


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate artifacts and exit nonzero on drift.")
    parser.add_argument("--json", action="store_true", help="Emit JSON result.")
    args = parser.parse_args(argv)

    failures = run_check()
    result = {
        "status": "PASS" if not failures else "FAIL",
        "failureCount": len(failures),
        "failures": failures,
    }
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif failures:
        print("FAIL: Wave572 D3D application-shell probe found drift:")
        for failure in failures:
            print(f"- {failure}")
    else:
        print("PASS: Wave572 D3D application-shell artifacts validated.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
