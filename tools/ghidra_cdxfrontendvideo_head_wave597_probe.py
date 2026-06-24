#!/usr/bin/env python3
"""Validate Wave597 CDXFrontEndVideo Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave597-cdxfrontendvideo-head-00541200"
POST = BASE / "post_applied"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cdxfrontendvideo_head_wave597_2026-05-19.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
DXFEV_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXFrontEndVideo.cpp.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
TRACKING = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

EXPECTED_SIGNATURES = {
    "0x00541200": (
        "CDXFrontEndVideo__CDXFrontEndVideo",
        "void __fastcall CDXFrontEndVideo__CDXFrontEndVideo(void * this)",
    ),
    "0x00541220": (
        "CDXFrontEndVideo__scalar_deleting_dtor",
        "void * __thiscall CDXFrontEndVideo__scalar_deleting_dtor(void * this, byte delete_flags)",
    ),
    "0x00541240": (
        "CDXFrontEndVideo__SetDefaultSize",
        "int __fastcall CDXFrontEndVideo__SetDefaultSize(void * this)",
    ),
    "0x00541260": (
        "CDXFrontEndVideo__Close",
        "void __fastcall CDXFrontEndVideo__Close(void * this)",
    ),
    "0x005412e0": (
        "CDXFrontEndVideo__Open",
        "void __thiscall CDXFrontEndVideo__Open(void * this, char * video_path, int fallback_width, int fallback_height, int open_flags, int async_open, int callback_cookie)",
    ),
    "0x00541430": (
        "CDXFrontEndVideo__InitVideo",
        "void __fastcall CDXFrontEndVideo__InitVideo(void * this)",
    ),
    "0x00541650": (
        "CDXFrontEndVideo__CloseVideo",
        "void __fastcall CDXFrontEndVideo__CloseVideo(void * this)",
    ),
    "0x00541770": (
        "CDXFrontEndVideo__GetWidth",
        "int __fastcall CDXFrontEndVideo__GetWidth(void * this)",
    ),
    "0x00541780": (
        "CDXFrontEndVideo__GetHeight",
        "int __fastcall CDXFrontEndVideo__GetHeight(void * this)",
    ),
    "0x00541790": (
        "CDXFrontEndVideo__Render",
        "int __thiscall CDXFrontEndVideo__Render(void * this, float x, float y, float z, float scale_x, float scale_y, uint packed_argb, int centered)",
    ),
    "0x00541d30": (
        "CDXFrontEndVideo__Update",
        "int __thiscall CDXFrontEndVideo__Update(void * this, char wait_for_frame)",
    ),
}

EXPECTED_TAGS = {
    "0x00541200": {"cdxfrontendvideo-head-wave597", "cdxfrontendvideo", "constructor", "vtable-005e5084", "cdxfmv-embedded-object"},
    "0x00541220": {"cdxfrontendvideo-head-wave597", "cdxfrontendvideo", "scalar-deleting-dtor", "vtable-slot-0", "ret-0x4", "name-corrected"},
    "0x00541240": {"cdxfrontendvideo-head-wave597", "cdxfrontendvideo", "default-size", "fallback-dimensions", "returns-one"},
    "0x00541260": {"cdxfrontendvideo-head-wave597", "cdxfrontendvideo", "close", "bink-handle", "closevideo-wrapper"},
    "0x005412e0": {"cdxfrontendvideo-head-wave597", "cdxfrontendvideo", "open", "bink-open", "async-open", "ret-0x18", "pending-open-buffer"},
    "0x00541430": {"cdxfrontendvideo-head-wave597", "cdxfrontendvideo", "init-video", "bink-frame", "cumtexture", "double-buffer"},
    "0x00541650": {"cdxfrontendvideo-head-wave597", "cdxfrontendvideo", "close-video", "resource-release", "bink-summary", "cumtexture-release"},
    "0x00541770": {"cdxfrontendvideo-head-wave597", "cdxfrontendvideo", "get-width", "cached-fallback", "bink-dimensions"},
    "0x00541780": {"cdxfrontendvideo-head-wave597", "cdxfrontendvideo", "get-height", "cached-fallback", "bink-dimensions"},
    "0x00541790": {"cdxfrontendvideo-head-wave597", "cdxfrontendvideo", "render", "bink-copy-to-buffer", "double-buffer", "ret-0x1c", "packed-argb"},
    "0x00541d30": {"cdxfrontendvideo-head-wave597", "cdxfrontendvideo", "update", "bink-wait", "ret-0x4", "completion-check"},
}

COMMENT_TOKENS = {
    "0x00541200": ("CFEPMultiplayerStart__ctor", "CDXFMV__ctor_base", "vtable 0x005e5084", "Bink handle"),
    "0x00541220": ("vtable 0x005e5084 slot 0", "RET 0x4", "delete_flags bit 0", "returns this"),
    "0x00541240": ("0x200 by 0x200", "this+0x20", "this+0x24", "returns 1"),
    "0x00541260": ("CDXFrontEndVideo__CloseVideo", "this+0x08"),
    "0x005412e0": ("RET 0x18", "DAT_008a97d0", "CBinkOpenThread", "CDXFrontEndVideo__InitVideo"),
    "0x00541430": ("CBinkOpenThread", "DAT_008a9830", "CUMTexture", "power-of-two"),
    "0x00541650": ("active open thread", "CUMTexture", "Bink summary", "this+0x08"),
    "0x00541770": ("CDXFMV width", "this+0x20", "handle+0x00"),
    "0x00541780": ("CDXFMV height", "this+0x24", "handle+0x04"),
    "0x00541790": ("RET 0x1c", "CFrontEnd__RenderVideoQuadScaledToWindow", "meshtex_default.tga", "Direct3D device"),
    "0x00541d30": ("RET 0x4", "CFrontEnd__Process", "BinkWait", "BinkDoFrame/BinkNextFrame"),
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


def read_json(path: Path) -> dict:
    if not path.is_file():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8-sig"))


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
    require_log_summary(BASE / "dry.log", {"updated": 0, "skipped": 11, "renamed": 0, "would_rename": 1, "missing": 0, "bad": 0}, failures)
    require_log_summary(BASE / "apply.log", {"updated": 11, "skipped": 0, "renamed": 1, "would_rename": 0, "missing": 0, "bad": 0}, failures)
    require_log_summary(BASE / "final-dry.log", {"updated": 0, "skipped": 11, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}, failures)


def check_post_exports(failures: list[str]) -> None:
    metadata_rows = {normalize_address(row["address"]): row for row in read_tsv_rows(POST / "metadata.tsv")}
    tag_rows = {normalize_address(row["address"]): row for row in read_tsv_rows(POST / "tags.tsv")}
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
        "post_applied/xrefs.tsv": 27,
        "post_applied/instructions.tsv": 935,
        "post_applied/decompile/index.tsv": 11,
        "post/vtables.tsv": 48,
    }
    actual_counts = {
        "post_applied/xrefs.tsv": row_count(POST / "xrefs.tsv"),
        "post_applied/instructions.tsv": row_count(POST / "instructions.tsv"),
        "post_applied/decompile/index.tsv": row_count(POST / "decompile" / "index.tsv"),
        "post/vtables.tsv": row_count(BASE / "post" / "vtables.tsv"),
    }
    for label, expected in expected_counts.items():
        if actual_counts[label] != expected:
            failures.append(f"{label} row count mismatch: {actual_counts[label]} != {expected}")


def check_xrefs_instructions_vtables(failures: list[str]) -> None:
    xrefs = {
        (
            normalize_address(row["target_addr"]),
            row["target_name"],
            normalize_address(row["from_addr"]),
            normalize_address(row["from_function_addr"]),
            row["from_function"],
            row["ref_type"],
        )
        for row in read_tsv_rows(POST / "xrefs.tsv")
    }
    expected_xrefs = {
        ("0x00541200", "CDXFrontEndVideo__CDXFrontEndVideo", "0x00465f56", "0x00465f10", "CFEPMultiplayerStart__ctor", "UNCONDITIONAL_CALL"),
        ("0x00541200", "CDXFrontEndVideo__CDXFrontEndVideo", "0x0053f11f", "0x0053f0f0", "CDXFMV__ctor_base", "UNCONDITIONAL_CALL"),
        ("0x00541220", "CDXFrontEndVideo__scalar_deleting_dtor", "0x005e5084", "<none>", "<no_function>", "DATA"),
        ("0x00541240", "CDXFrontEndVideo__SetDefaultSize", "0x00466386", "0x004662a0", "CFrontEnd__Init", "UNCONDITIONAL_CALL"),
        ("0x005412e0", "CDXFrontEndVideo__Open", "0x00452dca", "0x00452db0", "CFEPCommon__StartVideo", "UNCONDITIONAL_CALL"),
        ("0x00541430", "CDXFrontEndVideo__InitVideo", "0x005416a7", "0x00541650", "CDXFrontEndVideo__CloseVideo", "UNCONDITIONAL_CALL"),
        ("0x00541650", "CDXFrontEndVideo__CloseVideo", "0x00452b38", "0x00452b30", "CFEPCommon__Shutdown", "UNCONDITIONAL_CALL"),
        ("0x00541790", "CDXFrontEndVideo__Render", "0x00452d94", "0x00452ce0", "CFrontEnd__RenderVideoQuadScaledToWindow", "UNCONDITIONAL_CALL"),
        ("0x00541d30", "CDXFrontEndVideo__Update", "0x00466c47", "0x00466ba0", "CFrontEnd__Process", "UNCONDITIONAL_CALL"),
    }
    missing = expected_xrefs - xrefs
    if missing:
        failures.append(f"missing expected xrefs: {sorted(missing)}")

    instructions = {
        (
            normalize_address(row["instruction_addr"]),
            row["function_name"],
            row["mnemonic"],
            row["operands"],
        )
        for row in read_tsv_rows(POST / "instructions.tsv")
    }
    expected_instructions = {
        ("0x0054123d", "CDXFrontEndVideo__scalar_deleting_dtor", "RET", "0x4"),
        ("0x00541373", "CDXFrontEndVideo__Open", "RET", "0x18"),
        ("0x005416a7", "CDXFrontEndVideo__CloseVideo", "CALL", "0x00541430"),
        ("0x0054177a", "CDXFrontEndVideo__GetWidth", "RET", ""),
        ("0x0054178e", "CDXFrontEndVideo__GetHeight", "RET", ""),
        ("0x00541d14", "CDXFrontEndVideo__Render", "RET", "0x1c"),
        ("0x00541d73", "CDXFrontEndVideo__Update", "RET", "0x4"),
        ("0x00541dd7", "CDXFrontEndVideo__Update", "RET", "0x4"),
    }
    missing_instr = expected_instructions - instructions
    if missing_instr:
        failures.append(f"missing expected instructions: {sorted(missing_instr)}")

    slots = {
        (normalize_address(row["vtable"]), int(row["slot_index"])): row
        for row in read_tsv_rows(BASE / "post" / "vtables.tsv")
    }
    row = slots.get(("0x005e5084", 0))
    if row is None:
        failures.append("missing CDXFrontEndVideo vtable slot 0")
    else:
        if normalize_address(row["function_entry"]) != "0x00541220":
            failures.append(f"CDXFrontEndVideo slot 0 entry mismatch: {row['function_entry']}")
        if row["function_name"] != "CDXFrontEndVideo__scalar_deleting_dtor":
            failures.append(f"CDXFrontEndVideo slot 0 name mismatch: {row['function_name']}")
        if row["status"] != "OK":
            failures.append(f"CDXFrontEndVideo slot 0 status mismatch: {row['status']}")


def check_docs_and_ledgers(failures: list[str]) -> None:
    public_note = read_text(PUBLIC_NOTE)
    function_index = read_text(FUNCTION_INDEX)
    dxfev_doc = read_text(DXFEV_DOC)
    campaign = read_text(CAMPAIGN)
    backlog = read_text(BACKLOG)
    ledger = read_text(LEDGER)
    attempt_log = read_text(ATTEMPT_LOG)
    tracking = read_json(TRACKING)

    required_tokens = (
        "Wave597",
        "CDXFrontEndVideo__scalar_deleting_dtor",
        "0x005412e0",
        "0x00541790",
        "3064",
        "3029",
        "1333",
        "1085",
        "3019/6093 = 49.55%",
        "0x00542740 CDXEngine__InitLandscapeTextureTables",
        "BEA_20260519-162129_post_wave597_cdxfrontendvideo_head_verified",
    )
    for label, text in (
        ("public note", public_note),
        ("function index", function_index),
        ("DXFrontEndVideo doc", dxfev_doc),
        ("campaign", campaign),
        ("backlog", backlog),
        ("ledger", ledger),
        ("attempt log", attempt_log),
    ):
        require_tokens(label, text, required_tokens[:4], failures)
        if label in {"public note", "function index", "campaign", "backlog", "ledger", "attempt log"}:
            require_tokens(label, text, required_tokens[4:], failures)
        lowered = text.lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"{label} overclaims: {token}")

    if tracking.get("next_attempt_id") != 20253:
        failures.append(f"tracking next_attempt_id mismatch: {tracking.get('next_attempt_id')}")
    counters = tracking.get("counters", {})
    if counters.get("ledger_rows") != 993 or counters.get("attempt_rows") != 20253 or counters.get("completed") != 984:
        failures.append(f"tracking counters mismatch: {counters}")


def check_backup_and_queue(failures: list[str]) -> None:
    summary = read_json(BACKUP_SUMMARY)
    expected_backup = "G:\\GhidraBackups\\BEA_20260519-162129_post_wave597_cdxfrontendvideo_head_verified"
    if summary.get("backupPath") != expected_backup:
        failures.append(f"backup path mismatch: {summary.get('backupPath')}")
    if summary.get("fileCount") != 19:
        failures.append(f"backup fileCount mismatch: {summary.get('fileCount')}")
    if int(summary.get("totalBytes", 0)) != 161123207:
        failures.append(f"backup totalBytes mismatch: {summary.get('totalBytes')}")
    for key in ("missingCount", "extraCount", "diffCount"):
        if summary.get(key) != 0:
            failures.append(f"backup {key} mismatch: {summary.get(key)}")
    if summary.get("manifestHash") != "614df28fbf49231fd4d2bd359d833564e4f64678cb240bd8a5ed2c1ed82c1506":
        failures.append(f"backup manifestHash mismatch: {summary.get('manifestHash')}")

    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    if queue.get("status") != "PASS":
        failures.append(f"queue status mismatch: {queue.get('status')}")
    expected_quality = {
        "commentlessFunctionCount": 3029,
        "undefinedSignatureCount": 1333,
        "paramSignatureCount": 1085,
    }
    if queue.get("totalFunctions") != 6093:
        failures.append(f"queue totalFunctions mismatch: {queue.get('totalFunctions')}")
    for key, expected in expected_quality.items():
        if quality.get(key) != expected:
            failures.append(f"queue {key} mismatch: {quality.get(key)} != {expected}")
    head = queue.get("priorityQueues", {}).get("commentlessHighSignal", [{}])[0]
    if head.get("address") != "0x00542740" or head.get("name") != "CDXEngine__InitLandscapeTextureTables":
        failures.append(f"queue head mismatch: {head}")


def run_check() -> list[str]:
    failures: list[str] = []
    check_logs(failures)
    check_post_exports(failures)
    check_xrefs_instructions_vtables(failures)
    check_docs_and_ledgers(failures)
    check_backup_and_queue(failures)
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.check:
        parser.error("expected --check")

    failures = run_check()
    if failures:
        print("Wave597 CDXFrontEndVideo probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave597 CDXFrontEndVideo probe: PASS")
    print("Verified 11 saved signatures/comments/tags, read-back exports, docs, ledgers, queue telemetry, and backup summary.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
