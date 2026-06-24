#!/usr/bin/env python3
"""Validate Wave1092 D3D application shell review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1092-d3d-application-shell-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_d3d_application_shell_review_wave1092_2026-06-04.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1092_recheck_2026-06-04.md"
PACKAGE_JSON = ROOT / "package.json"
PROGRESS_JSON = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
DISPLAY_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "display-settings.md"
D3DAPP_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "d3dapp.cpp" / "_index.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
README = ROOT / "README.MD"
CAPABILITIES = ROOT / "CURRENT_CAPABILITIES.md"
AGENTS = ROOT / "AGENTS.md"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260604-152017_post_wave1092_d3d_application_shell_review_verified"
WAVE_TAG = "d3d-application-shell-review-wave1092"

TARGETS = {
    "0x00528f80": (
        "CD3DApplication__Init",
        "void * __thiscall CD3DApplication__Init(void * this)",
        ("DAT_0089c0f4", "640x480", "D3D8 Application"),
    ),
    "0x005290a0": (
        "CD3DApplication__Create",
        "int __thiscall CD3DApplication__Create(void * this, void * hinstance)",
        ("Direct3DCreate9(0x1f)", "D3D Window", "perf timer"),
    ),
    "0x00529350": (
        "CD3DApplication__BuildDeviceList",
        "int __thiscall CD3DApplication__BuildDeviceList(void * this)",
        ("DAT_0089c0ac", "DisplayErrorMsg", "multisample"),
    ),
    "0x0052af00": (
        "CD3DApplication__Initialize3DEnvironment",
        "int __thiscall CD3DApplication__Initialize3DEnvironment(void * this, bool reuse_existing_device)",
        ("cardid.txt", "presentation", "REF device"),
    ),
    "0x0052b760": (
        "CD3DApplication__Resize3DEnvironment",
        "int __thiscall CD3DApplication__Resize3DEnvironment(void * this)",
        ("presentation parameters", "fullscreen cursor", "perf timer"),
    ),
    "0x0052b840": (
        "CD3DApplication__ToggleFullscreen",
        "int __thiscall CD3DApplication__ToggleFullscreen(void * this)",
        ("ForceWindowed", "g_ScreenShape", "saved window bounds"),
    ),
    "0x0052ba50": (
        "CD3DApplication__ForceWindowed",
        "int __thiscall CD3DApplication__ForceWindowed(void * this, bool target_windowed_state)",
        ("windowable", "Initialize3DEnvironment", "DisplayErrorMsg"),
    ),
    "0x0052bb80": (
        "CD3DApplication__Reset3DEnvironment",
        "int __thiscall CD3DApplication__Reset3DEnvironment(void * this, bool show_device_dialog, int reset_context)",
        ("SelectDeviceProc", "IDOK", "reset_context"),
    ),
    "0x0052bc80": (
        "CD3DApplication__SelectDeviceProc",
        "int __stdcall CD3DApplication__SelectDeviceProc(int dialog_hwnd, int message, int wparam, int lparam)",
        ("WM_INITDIALOG", "WM_COMMAND", "DAT_0089c048"),
    ),
    "0x0052c430": (
        "CD3DApplication__Cleanup3DEnvironment",
        "void __thiscall CD3DApplication__Cleanup3DEnvironment(void * this)",
        ("DebugTrace", "refcount", "final-cleanup"),
    ),
    "0x0052c4f0": (
        "CD3DApplication__DisplayErrorMsg",
        "int __stdcall CD3DApplication__DisplayErrorMsg(int error_code, int message_type)",
        ("0xb6", "0xc5", "message_type"),
    ),
    "0x0052c730": (
        "CD3DApplication__SetResolution",
        "void __thiscall CD3DApplication__SetResolution(void * this, int width, int height)",
        ("this+0x330bc", "this+0x330c0", "without an in-function clamp"),
    ),
    "0x0052c780": (
        "ScreenShape_UpdateAspectScale",
        "void __fastcall ScreenShape_UpdateAspectScale(void * d3d_app)",
        ("g_ScreenShape", "16:9", "1.3333334"),
    ),
    "0x0052c8d0": (
        "CD3DApplication__SetDeviceCursorFromIcon",
        "int __cdecl CD3DApplication__SetDeviceCursorFromIcon(void * d3d_device, int icon_handle)",
        ("ICONINFO", "GDI", "cursor surface"),
    ),
    "0x0052cd20": (
        "CD3DApplication__PerfTimerCommand",
        "double __stdcall CD3DApplication__PerfTimerCommand(int command)",
        ("QueryPerformanceCounter", "timeGetTime", "elapsed time"),
    ),
}

DOC_TOKENS = (
    "Wave1092",
    WAVE_TAG,
    "0x00528f80 CD3DApplication__Init",
    "0x005290a0 CD3DApplication__Create",
    "0x00529350 CD3DApplication__BuildDeviceList",
    "0x0052af00 CD3DApplication__Initialize3DEnvironment",
    "0x0052b840 CD3DApplication__ToggleFullscreen",
    "0x0052ba50 CD3DApplication__ForceWindowed",
    "0x0052bc80 CD3DApplication__SelectDeviceProc",
    "0x0052cd20 CD3DApplication__PerfTimerCommand",
    "0x005e4ad0",
    "1560/1560 = 100.00%",
    "812/1408 = 57.67%",
    "500/500 = 100.00%",
    "6410/6410 = 100.00%",
    BACKUP_PATH,
    "no mutation",
)

OVERCLAIMS = (
    "runtime behavior proven",
    "runtime direct3d behavior proven",
    "runtime proof complete",
    "patch behavior proven",
    "rebuild parity proven",
    "all systems complete",
    "every system is complete",
    "fully reverse-engineered",
    "fully reverse engineered",
    "exact source-layout identity proven",
    "exact source layout identity proven",
)


def normalize_address(value: str) -> str:
    text = value.strip().lower()
    if text.startswith("0x"):
        text = text[2:]
    return "0x" + text.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig", errors="replace").replace("\x00", "")


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


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "primary-metadata.tsv": 15,
        "primary-tags.tsv": 15,
        "primary-xrefs.tsv": 41,
        "primary-instructions.tsv": 4022,
        "primary-decompile/index.tsv": 15,
        "context-metadata.tsv": 6,
        "context-tags.tsv": 6,
        "context-xrefs.tsv": 79,
        "context-instructions.tsv": 877,
        "context-decompile/index.tsv": 6,
        "vtable-slots.tsv": 6,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "primary-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "primary-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "primary-decompile" / "index.tsv")}

    for address, (name, signature, comment_tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata at {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            comment = row.get("comment", "")
            require("Wave572 signature" in comment, f"missing Wave572 comment at {address}", failures)
            for token in comment_tokens:
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags at {address}", failures)
        if tag_row is not None:
            tag_text = tag_row.get("tags", "")
            for token in ("static-reaudit", "d3d-application-shell-wave572", "d3d-application", "display", "retail-binary-evidence"):
                require(token in tag_text, f"missing tag at {address}: {token}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile at {address}", failures)
        if dec is not None:
            require(dec.get("name") == name, f"decompile name mismatch at {address}", failures)
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    slots = read_tsv(BASE / "vtable-slots.tsv")
    require(len(slots) == 6, "vtable slot count mismatch", failures)
    for slot, expected_name in {"4": "CD3DApplication__Create", "5": "CD3DApplication__MsgProc"}.items():
        row = next((candidate for candidate in slots if candidate.get("slot_index") == slot), None)
        require(row is not None, f"missing vtable slot {slot}", failures)
        if row is not None:
            require(row.get("function_name") == expected_name, f"vtable slot {slot} mismatch", failures)
            require(row.get("status") == "OK", f"vtable slot {slot} status mismatch", failures)
    require(all(row.get("status") == "OK" for row in slots), "vtable has non-OK slot", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected = {
        "primary-metadata.log": "targets=15 found=15 missing=0",
        "primary-tags.log": "ExportFunctionTagsByAddress complete: rows=15 missing=0",
        "primary-xrefs.log": "Wrote 41 rows",
        "primary-instructions.log": "Wrote 4022 function-body instruction rows",
        "primary-decompile.log": "targets=15 dumped=15 missing=0 failed=0",
        "context-metadata.log": "targets=6 found=6 missing=0",
        "context-tags.log": "ExportFunctionTagsByAddress complete: rows=6 missing=0",
        "context-xrefs.log": "Wrote 79 rows",
        "context-instructions.log": "Wrote 877 function-body instruction rows",
        "context-decompile.log": "targets=6 dumped=6 missing=0 failed=0",
        "vtable-slots.log": "ExportVtableSlots complete: targets=1 rows=6",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR:", "BADNAME:", "BADSIG:", "BADCOMMENT:", "BADTAGS:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 175541127 or backup.get("totalBytes") == 175541127.0, "backup bytes mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs_and_state(failures: list[str]) -> None:
    core_docs = [
        NOTE,
        AGGREGATE_NOTE,
        PROGRESS_JSON,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        DISPLAY_DOC,
        D3DAPP_DOC,
        BACKLOG,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
        README,
        CAPABILITIES,
        AGENTS,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing doc token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    progress = read_json(PROGRESS_JSON)
    require(progress["latestWave"]["wave"] == "Wave1092 D3D application shell review", "progress latest wave mismatch", failures)
    require(progress["latestWave"]["status"] in {"validation_pending", "validated_pending_commit", "committed"}, "progress status mismatch", failures)
    require(progress["latestWave"]["backup"] == BACKUP_PATH, "progress backup mismatch", failures)
    require(progress["functionQuality"]["totalFunctions"] == 6410, "progress total mismatch", failures)
    require(progress["post100Reaudit"]["expandedStaticSurface"]["completed"] == 1560, "expanded count mismatch", failures)
    require(progress["post100Reaudit"]["expandedStaticSurface"]["percent"] == "100.00%", "expanded percent mismatch", failures)
    require(progress["post100Reaudit"]["wave911Focused"]["completed"] == 812, "wave911 focused mismatch", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(scripts.get("test:ghidra-d3d-application-shell-review-wave1092") == r"py -3 tools\ghidra_d3d_application_shell_review_wave1092_probe.py --check", "missing focused package script", failures)
    require(scripts.get("test:ghidra-wave900-plus-through-wave1092-recheck") == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1092 --check", "missing aggregate package script", failures)

    ledger = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1092 D3D application shell review" for row in ledger), "missing Wave1092 ledger row", failures)
    require(any(row.get("task") == "Wave1092 D3D application shell review" and row.get("attempt_id") == 20672 for row in attempts), "missing Wave1092 attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_docs_and_state(failures)

    if failures:
        print("Wave1092 D3D application shell review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1092 D3D application shell review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
