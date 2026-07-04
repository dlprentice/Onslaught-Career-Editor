#!/usr/bin/env python3
"""Validate Wave594 CVBufTexture/FMV Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave594-vbuftexture-fmv-head-0053f040"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_vbuftexture_fmv_head_wave594_2026-05-19.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
DXFMV_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXFMV.cpp.md"
DXFEV_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXFrontEndVideo.cpp.md"
VBUFTEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "vbuftexture.cpp" / "_index.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
BACKUP_SUMMARY = BASE / "wave594_backup_summary.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

EXPECTED_SIGNATURES = {
    "0x0053f040": (
        "CVBufTexture__SetStateCacheModeByFlag",
        "void __stdcall CVBufTexture__SetStateCacheModeByFlag(int state_cache_mode_flag)",
    ),
    "0x0053f0a0": (
        "CDXFMV__DestructorBody",
        "void __fastcall CDXFMV__DestructorBody(void * this)",
    ),
    "0x0053f0f0": (
        "CDXFMV__ctor_base",
        "void * __fastcall CDXFMV__ctor_base(void * this)",
    ),
    "0x0053f140": (
        "CDXFMV__scalar_deleting_dtor",
        "void * __thiscall CDXFMV__scalar_deleting_dtor(void * this, byte delete_flags)",
    ),
    "0x0053f160": (
        "VFuncSlot_01_0053f160",
        "void * __thiscall VFuncSlot_01_0053f160(void * this, byte delete_flags)",
    ),
    "0x0053f180": (
        "CDXFMV__VFunc_06_0053f180",
        "void __cdecl CDXFMV__VFunc_06_0053f180(void)",
    ),
}

EXPECTED_TAGS = {
    "0x0053f040": {"vbuftexture-fmv-head-wave594", "cvbuftexture", "d3d-state-cache", "ret-0x4"},
    "0x0053f0a0": {"vbuftexture-fmv-head-wave594", "dxfmv", "destructor-body", "monitor-shutdown"},
    "0x0053f0f0": {"vbuftexture-fmv-head-wave594", "dxfmv", "constructor", "global-fmv-object", "owner-corrected"},
    "0x0053f140": {"vbuftexture-fmv-head-wave594", "dxfmv", "scalar-deleting-dtor", "vtable-slot-1", "phantom-param-removed", "owner-corrected"},
    "0x0053f160": {"vbuftexture-fmv-head-wave594", "shared-vfunc-slot", "scalar-deleting-dtor-shape", "monitor-shutdown", "owner-unresolved"},
    "0x0053f180": {"vbuftexture-fmv-head-wave594", "dxfmv", "vtable-slot-6", "platform-input", "tail-jump", "no-params"},
}

COMMENT_TOKENS = {
    "0x0053f040": ("RET 0x4", "CVBufTexture__RenderAndRestoreStateFlag4", "D3DStateCache__ForceSlotMode4or5", "D3DStateCache__SetStateCached"),
    "0x0053f0a0": ("CDXFMV__scalar_deleting_dtor", "0x0053f090", "this+0x10", "CMonitor__Shutdown"),
    "0x0053f0f0": ("0x0053f070", "DAT_0089d690", "CFMV vtable 0x005e5018", "CDXFMV vtable 0x005e4fe4"),
    "0x0053f140": ("0x005e4fe4 slot 1", "delete_flags bit 0", "CDXMemoryManager__Free", "RET 0x4"),
    "0x0053f160": ("CFMV/base table at 0x005e5018", "CMonitor__Shutdown_Thunk", "delete_flags bit 0", "RET 0x4"),
    "0x0053f180": ("CLTShell__InitializeRuntimeAndLoadCoreResources", "FMV init timing", "PlatformInput__ResetKeyStateTables", "tail-jumping"),
}

COMMON_TAGS = {"static-reaudit", "retail-binary-evidence", "signature-corrected", "comment-hardened"}
OVERCLAIM_TOKENS = ("runtime behavior proven", "source identity proven", "rebuild parity proven", "fully recovered", "fully reverse-engineered")


def normalize_address(address: str) -> str:
    value = address.strip().lower()
    if value.startswith("<"):
        return value
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")


def read_tsv_rows(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def row_count(path: Path) -> int:
    return len(read_tsv_rows(path))


def require_tokens(label: str, text: str, tokens: tuple[str, ...] | set[str], failures: list[str]) -> None:
    normalized = text.replace("\\\\", "\\")
    for token in tokens:
        if token not in normalized:
            failures.append(f"{label} missing token: {token}")


def require_log_summary(path: Path, expected: dict[str, int], failures: list[str]) -> None:
    text = read_text(path)
    match = re.search(r"SUMMARY:\s+([^\r\n]+)", text)
    if not match:
        failures.append(f"{path.name} missing SUMMARY")
        return
    values = {key: int(value) for key, value in re.findall(r"([a-z_]+)=([0-9]+)", match.group(1))}
    for key, expected_value in expected.items():
        actual = values.get(key)
        if actual != expected_value:
            failures.append(f"{path.name} {key} mismatch: {actual} != {expected_value}")
    if "REPORT: Save succeeded" not in text:
        failures.append(f"{path.name} missing save-success report")
    for bad_token in ("FAIL:", "LockException", "Read-back mismatch", "Function not found", "Input file not found"):
        if bad_token in text:
            failures.append(f"{path.name} contains {bad_token}")


def check_logs(failures: list[str]) -> None:
    require_log_summary(
        BASE / "logs" / "apply_dry.log",
        {"updated": 0, "skipped": 6, "renamed": 0, "would_rename": 2, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "logs" / "apply.log",
        {"updated": 6, "skipped": 0, "renamed": 2, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "logs" / "apply_final_dry.log",
        {"updated": 0, "skipped": 6, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )


def check_post_exports(failures: list[str]) -> None:
    metadata_rows = {normalize_address(row["address"]): row for row in read_tsv_rows(BASE / "post_metadata.tsv")}
    tag_rows = {normalize_address(row["address"]): row for row in read_tsv_rows(BASE / "post_tags.tsv")}
    if set(metadata_rows) != set(EXPECTED_SIGNATURES):
        failures.append(f"metadata address set mismatch: {sorted(metadata_rows)}")
    if set(tag_rows) != set(EXPECTED_SIGNATURES):
        failures.append(f"tag address set mismatch: {sorted(tag_rows)}")

    for address, (name, signature) in EXPECTED_SIGNATURES.items():
        row = metadata_rows.get(address)
        if not row:
            continue
        if row["name"] != name:
            failures.append(f"{address} name mismatch: {row['name']} != {name}")
        if row["signature"] != signature:
            failures.append(f"{address} signature mismatch: {row['signature']} != {signature}")
        if row["status"] != "OK":
            failures.append(f"{address} metadata status mismatch: {row['status']}")
        require_tokens(f"{address} comment", row["comment"], COMMENT_TOKENS[address], failures)
        require_tokens(f"{address} comment", row["comment"], ("Static retail evidence only", "BEA patching", "rebuild parity remain unproven"), failures)
        lowered = row["comment"].lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"{address} comment overclaims: {token}")

        tag_row = tag_rows.get(address)
        if not tag_row:
            continue
        actual_tags = set(filter(None, tag_row["tags"].split(";")))
        missing = (COMMON_TAGS | EXPECTED_TAGS[address]) - actual_tags
        if tag_row["name"] != name:
            failures.append(f"{address} tag name mismatch: {tag_row['name']} != {name}")
        if tag_row["status"] != "OK":
            failures.append(f"{address} tag status mismatch: {tag_row['status']}")
        if missing:
            failures.append(f"{address} missing tags: {sorted(missing)}")

    expected_counts = {
        "post_xrefs.tsv": 27,
        "post_instructions.tsv": 1446,
        "post_decompile/targets/index.tsv": 6,
        "post_decompile/callers/index.tsv": 2,
        "post_callsite_instructions.tsv": 126,
        "post_vtable.tsv": 48,
    }
    actual_counts = {
        "post_xrefs.tsv": row_count(BASE / "post_xrefs.tsv"),
        "post_instructions.tsv": row_count(BASE / "post_instructions.tsv"),
        "post_decompile/targets/index.tsv": row_count(BASE / "post_decompile" / "targets" / "index.tsv"),
        "post_decompile/callers/index.tsv": row_count(BASE / "post_decompile" / "callers" / "index.tsv"),
        "post_callsite_instructions.tsv": row_count(BASE / "post_callsite_instructions.tsv"),
        "post_vtable.tsv": row_count(BASE / "post_vtable.tsv"),
    }
    for label, expected in expected_counts.items():
        if actual_counts[label] != expected:
            failures.append(f"{label} row count mismatch: {actual_counts[label]} != {expected}")


def check_xrefs_and_vtables(failures: list[str]) -> None:
    xrefs = {
        (
            normalize_address(row["target_addr"]),
            row["target_name"],
            normalize_address(row["from_addr"]),
            normalize_address(row["from_function_addr"]),
            row["from_function"],
            row["ref_type"],
        )
        for row in read_tsv_rows(BASE / "post_xrefs.tsv")
    }
    expected_xrefs = {
        ("0x0053f040", "CVBufTexture__SetStateCacheModeByFlag", "0x0050ab67", "0x0050ab60", "CVBufTexture__RenderAndRestoreStateFlag4", "UNCONDITIONAL_CALL"),
        ("0x0053f040", "CVBufTexture__SetStateCacheModeByFlag", "0x0050ab9d", "0x0050ab60", "CVBufTexture__RenderAndRestoreStateFlag4", "UNCONDITIONAL_CALL"),
        ("0x0053f0f0", "CDXFMV__ctor_base", "0x0053f075", "<none>", "<no_function>", "UNCONDITIONAL_CALL"),
        ("0x0053f0a0", "CDXFMV__DestructorBody", "0x0053f143", "0x0053f140", "CDXFMV__scalar_deleting_dtor", "UNCONDITIONAL_CALL"),
        ("0x0053f140", "CDXFMV__scalar_deleting_dtor", "0x005e4fe8", "<none>", "<no_function>", "DATA"),
        ("0x0053f180", "CDXFMV__VFunc_06_0053f180", "0x004efc4f", "0x004efb10", "CLTShell__InitializeRuntimeAndLoadCoreResources", "UNCONDITIONAL_CALL"),
        ("0x0053f180", "CDXFMV__VFunc_06_0053f180", "0x005e4ffc", "<none>", "<no_function>", "DATA"),
    }
    missing = expected_xrefs - xrefs
    if missing:
        failures.append(f"missing expected xrefs: {sorted(missing)}")

    vtable_rows = {
        (normalize_address(row["vtable"]), row["slot_index"], normalize_address(row["pointer_addr"]), row["function_name"], row["status"])
        for row in read_tsv_rows(BASE / "post_vtable.tsv")
    }
    expected_vtables = {
        ("0x005e4fe4", "1", "0x0053f140", "CDXFMV__scalar_deleting_dtor", "OK"),
        ("0x005e4fe4", "6", "0x0053f180", "CDXFMV__VFunc_06_0053f180", "OK"),
        ("0x005e5018", "1", "0x0053f160", "VFuncSlot_01_0053f160", "OK"),
    }
    missing_vtables = expected_vtables - vtable_rows
    if missing_vtables:
        failures.append(f"missing expected vtable slots: {sorted(missing_vtables)}")


def check_queue(failures: list[str]) -> None:
    rows = read_tsv_rows(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv")
    total = len(rows)
    commented = sum(1 for row in rows if row["comment"])
    commentless = total - commented
    exact_undefined = sum(1 for row in rows if "undefined" in row["signature"])
    param_n = sum(1 for row in rows if re.search(r"\bparam_[0-9]+\b", row["signature"]))
    strict = sum(1 for row in rows if row["comment"] and "undefined" not in row["signature"] and not re.search(r"\bparam_[0-9]+\b", row["signature"]))
    if (total, commented, commentless, exact_undefined, param_n, strict) != (6093, 3039, 3054, 1347, 1095, 2993):
        failures.append(f"queue metrics mismatch: {(total, commented, commentless, exact_undefined, param_n, strict)}")
    queue = json.loads(read_text(QUEUE_JSON))
    head = queue["priorityQueues"]["commentlessHighSignal"][0]
    if head["address"] != "0x0053f730" or head["name"] != "CDXBitmapFont__ctor_like_0053f730":
        failures.append(f"next queue head mismatch: {head}")


def check_docs_and_ledgers(failures: list[str]) -> None:
    docs = {
        "public note": PUBLIC_NOTE,
        "function index": FUNCTION_INDEX,
        "DXFMV doc": DXFMV_DOC,
        "DXFrontEndVideo doc": DXFEV_DOC,
        "vbuftexture doc": VBUFTEXTURE_DOC,
        "campaign": CAMPAIGN,
        "backlog": BACKLOG,
        "ledger": LEDGER,
        "attempt log": ATTEMPT_LOG,
    }
    common_full = (
        "Wave594",
        "CVBufTexture__SetStateCacheModeByFlag",
        "CDXFMV__ctor_base",
        "CDXFMV__scalar_deleting_dtor",
        "0x0053f730 CDXBitmapFont__ctor_like_0053f730",
        "[maintainer-local-ghidra-backup-root]\\BEA_20260519-144006_post_wave594_vbuftexture_fmv_head_verified",
    )
    expectations = {
        "public note": common_full,
        "function index": common_full,
        "DXFMV doc": (
            "Wave594",
            "CDXFMV__DestructorBody",
            "CDXFMV__ctor_base",
            "CDXFMV__scalar_deleting_dtor",
            "0x0053f730 CDXBitmapFont__ctor_like_0053f730",
        ),
        "DXFrontEndVideo doc": (
            "Wave594",
            "CDXFMV__ctor_base",
            "CDXFrontEndVideo",
            "this+0x10",
        ),
        "vbuftexture doc": (
            "Wave594",
            "CVBufTexture__SetStateCacheModeByFlag",
            "D3DStateCache__ForceSlotMode4or5",
            "D3DStateCache__SetStateCached",
        ),
        "campaign": common_full,
        "backlog": common_full,
        "ledger": common_full,
        "attempt log": common_full,
    }
    for label, path in docs.items():
        require_tokens(label, read_text(path), expectations[label], failures)


def check_backup(failures: list[str]) -> None:
    summary = json.loads(read_text(BACKUP_SUMMARY))
    expected = {
        "backupPath": "[maintainer-local-ghidra-backup-root]\\BEA_20260519-144006_post_wave594_vbuftexture_fmv_head_verified",
        "fileCount": 19,
        "totalBytes": 160992135,
        "diffCount": 0,
        "manifestHash": "400782d6d7e464d08e427016c204c16a21adee62210c259a4e0781e613a8db1a",
    }
    for key, expected_value in expected.items():
        if summary.get(key) != expected_value:
            failures.append(f"backup {key} mismatch: {summary.get(key)} != {expected_value}")


def run_checks() -> dict[str, object]:
    failures: list[str] = []
    check_logs(failures)
    check_post_exports(failures)
    check_xrefs_and_vtables(failures)
    check_queue(failures)
    check_backup(failures)
    check_docs_and_ledgers(failures)
    return {
        "schema": "ghidra-vbuftexture-fmv-head-wave594.v1",
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "whatIsProven": [
            "Wave594 Ghidra read-back artifacts contain six saved comments/signatures/tags for the CVBufTexture/FMV queue-head tranche.",
            "The mutation logs show clean dry/apply/final-dry summaries and saved-project reports.",
            "The refreshed queue and backup summary match the documented Wave594 counts.",
        ],
        "notProven": [
            "This does not prove runtime render, FMV, Bink, platform-input, or teardown behavior.",
            "This does not prove exact CFMV/CDXFMV/CDXFrontEndVideo/CVBufTexture layouts or full vtable boundaries.",
            "This does not prove BEA patching or rebuild parity.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Exit nonzero on validation failure.")
    parser.add_argument("--json", action="store_true", help="Print JSON result.")
    args = parser.parse_args()

    result = run_checks()
    if args.json:
        print(json.dumps(result, indent=2))
    elif result["status"] == "PASS":
        print("Wave594 CVBufTexture/FMV probe PASS")
    else:
        print("Wave594 CVBufTexture/FMV probe FAIL")
        for failure in result["failures"]:
            print(f"- {failure}")
    return 0 if result["status"] == "PASS" or not args.check else 1


if __name__ == "__main__":
    raise SystemExit(main())
