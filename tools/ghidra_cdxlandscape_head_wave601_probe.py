#!/usr/bin/env python3
"""Validate Wave601 CDXLandscape head Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave601-cdxlandscape-head-00544770"
PRE = BASE / "pre"
POST = BASE / "post"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cdxlandscape_head_wave601_2026-05-19.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
DXLANDSCAPE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXLandscape.cpp" / "_index.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
TRACKING = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

EXPECTED_SIGNATURES = {
    "0x00544770": (
        "CDXLandscape__ReleaseOwnedResources",
        "void __fastcall CDXLandscape__ReleaseOwnedResources(void * resource_record)",
    ),
    "0x005447d0": (
        "CDXLandscape__FreeObjectCallback",
        "void __fastcall CDXLandscape__FreeObjectCallback(void * object_record)",
    ),
    "0x005447e0": (
        "CDXLandscape__CreateMipLevels",
        "void __thiscall CDXLandscape__CreateMipLevels(void * this, int mip_level_count)",
    ),
    "0x00544a00": (
        "CDXLandscape__Constructor",
        "void * __fastcall CDXLandscape__Constructor(void * this)",
    ),
    "0x00544a40": (
        "CDXLandscape__ScalarDeletingDestructor",
        "void * __thiscall CDXLandscape__ScalarDeletingDestructor(void * this, byte flags)",
    ),
    "0x00544a60": (
        "CDXLandscape__Destructor",
        "void __fastcall CDXLandscape__Destructor(void * this)",
    ),
    "0x00544af0": (
        "CDXLandscape__Init",
        "int __thiscall CDXLandscape__Init(void * this, void * init_context)",
    ),
    "0x00544eb0": (
        "CDXLandscape__ReleaseBuffers",
        "int __fastcall CDXLandscape__ReleaseBuffers(void * this)",
    ),
    "0x00544f10": (
        "CDXLandscape__Shutdown",
        "void __fastcall CDXLandscape__Shutdown(void * this)",
    ),
}

EXPECTED_TAGS = {
    "0x00544770": {"cdxlandscape", "resource-array", "texture-mip-records", "callback-release", "param-renamed"},
    "0x005447d0": {"cdxlandscape", "resource-array", "free-callback", "param-renamed"},
    "0x005447e0": {"cdxlandscape", "mip-levels", "landscape-texture", "resource-array", "ret-0x4"},
    "0x00544a00": {"cdxlandscape", "constructor", "vtable", "hud-marker"},
    "0x00544a40": {"cdxlandscape", "scalar-deleting-dtor", "vtable", "flags", "ret-0x4"},
    "0x00544a60": {"cdxlandscape", "destructor", "shader-list", "hud-marker"},
    "0x00544af0": {"cdxlandscape", "init", "landscape-texture", "vertex-index-buffer", "ret-0x4"},
    "0x00544eb0": {"cdxlandscape", "release-buffers", "vtable-slot-4", "device-resources"},
    "0x00544f10": {"cdxlandscape", "shutdown", "resource-array", "surface-texture"},
}

COMMENT_TOKENS = {
    "0x00544770": ("resource_record", "+0 slot", "+0x08", "0xc-byte", "CDXLandscape__FreeObjectCallback", "Static retail evidence only"),
    "0x005447d0": ("object_record+0", "CDXMemoryManager__Free", "mip-level allocation cleanup", "Static retail evidence only"),
    "0x005447e0": ("RET 0x4", "mip_level_count", "DXLandscape.cpp line 0x5f", "DXLandscape.h line 0xaa", "0x14000", "0xff"),
    "0x00544a00": ("0x40-byte object", "0x005e50d0", "+0x08", "+0x24/+0x28/+0x2c/+0x30/+0x38", "+0x3c"),
    "0x00544a40": ("vtable slot 0", "flags bit 0", "RET 0x4", "CDXMemoryManager__Free"),
    "0x00544a60": ("0x005e50d0", "CShaderBase", "+0x18", "IUnknown__ReleaseAndNull", "pending HUD marker"),
    "0x00544af0": ("CEngine__Init", "engine+0x49c", "RET 0x4", "+0x20", "BuildLandscapeCache", "LandscapeShader"),
    "0x00544eb0": ("vtable slot 4", "+0x08", "+0x10", "+0x0c", "+0x14", "IUnknown__ReleaseAndNull", "returns 0"),
    "0x00544f10": ("CEngine__Shutdown", "engine+0x10", "+0x24 array", "0x34-byte", "+0x28/+0x2c/+0x30", "CDXSurf"),
}

COMMON_TAGS = {
    "static-reaudit",
    "cdxlandscape-head-wave601",
    "retail-binary-evidence",
    "signature-corrected",
    "comment-hardened",
}
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
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict:
    if not path.is_file():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_tsv_rows(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
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
    for bad_token in ("LockException", "Function not found", "Input file not found", "Read-back signature mismatch"):
        if bad_token in text:
            failures.append(f"{path.name} contains {bad_token}")


def check_logs(failures: list[str]) -> None:
    require_log_summary(BASE / "apply_dry.log", {"updated": 0, "skipped": 9, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}, failures)
    require_log_summary(BASE / "apply_apply.log", {"updated": 9, "skipped": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}, failures)
    require_log_summary(BASE / "apply_final_dry.log", {"updated": 0, "skipped": 9, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}, failures)


def check_post_exports(failures: list[str]) -> None:
    metadata_rows = {normalize_address(row["address"]): row for row in read_tsv_rows(POST / "metadata_after.tsv")}
    tag_rows = {normalize_address(row["address"]): row for row in read_tsv_rows(POST / "tags_after.tsv")}
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
        require_tokens(f"{address} comment", row["comment"], ("BEA patching", "rebuild parity remain unproven"), failures)
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
        "post/xrefs_after.tsv": 25,
        "post/instructions_after.tsv": 2061,
        "post/decomp_after/index.tsv": 9,
    }
    actual_counts = {
        "post/xrefs_after.tsv": row_count(POST / "xrefs_after.tsv"),
        "post/instructions_after.tsv": row_count(POST / "instructions_after.tsv"),
        "post/decomp_after/index.tsv": row_count(POST / "decomp_after" / "index.tsv"),
    }
    for label, expected in expected_counts.items():
        if actual_counts[label] != expected:
            failures.append(f"{label} row count mismatch: {actual_counts[label]} != {expected}")


def check_xrefs_and_instructions(failures: list[str]) -> None:
    xrefs = {
        (
            normalize_address(row["target_addr"]),
            row["target_name"],
            normalize_address(row["from_addr"]),
            normalize_address(row["from_function_addr"]),
            row["from_function"],
            row["ref_type"],
        )
        for row in read_tsv_rows(POST / "xrefs_after.tsv")
    }
    expected_xrefs = {
        ("0x00544770", "CDXLandscape__ReleaseOwnedResources", "0x00544f39", "0x00544f10", "CDXLandscape__Shutdown", "DATA"),
        ("0x005447d0", "CDXLandscape__FreeObjectCallback", "0x00544793", "0x00544770", "CDXLandscape__ReleaseOwnedResources", "DATA"),
        ("0x005447e0", "CDXLandscape__CreateMipLevels", "0x0054512b", "0x00545070", "CDXLandscape__Reset", "UNCONDITIONAL_CALL"),
        ("0x00544a00", "CDXLandscape__Constructor", "0x00449bd2", "0x004499d0", "CEngine__Init", "UNCONDITIONAL_CALL"),
        ("0x00544a40", "CDXLandscape__ScalarDeletingDestructor", "0x005e50d0", "<none>", "<no_function>", "DATA"),
        ("0x00544a60", "CDXLandscape__Destructor", "0x00544a43", "0x00544a40", "CDXLandscape__ScalarDeletingDestructor", "UNCONDITIONAL_CALL"),
        ("0x00544af0", "CDXLandscape__Init", "0x00449c04", "0x004499d0", "CEngine__Init", "UNCONDITIONAL_CALL"),
        ("0x00544eb0", "CDXLandscape__ReleaseBuffers", "0x005e50e0", "<none>", "<no_function>", "DATA"),
        ("0x00544f10", "CDXLandscape__Shutdown", "0x004498da", "0x00449890", "CEngine__Shutdown", "UNCONDITIONAL_CALL"),
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
        for row in read_tsv_rows(POST / "instructions_after.tsv")
    }
    expected_instructions = {
        ("0x00544793", "CDXLandscape__ReleaseOwnedResources", "PUSH", "0x5447d0"),
        ("0x005448c1", "CDXLandscape__CreateMipLevels", "PUSH", "0x5447d0"),
        ("0x00544997", "CDXLandscape__CreateMipLevels", "RET", "0x4"),
        ("0x00544a3d", "CDXLandscape__Constructor", "RET", ""),
        ("0x00544a5d", "CDXLandscape__ScalarDeletingDestructor", "RET", "0x4"),
        ("0x00544cb6", "CDXLandscape__Init", "RET", "0x4"),
        ("0x00544ebf", "CDXLandscape__ReleaseBuffers", "PUSH", "EAX"),
        ("0x00544eff", "CDXLandscape__ReleaseBuffers", "CALL", "0x00514010"),
        ("0x00544f08", "CDXLandscape__ReleaseBuffers", "RET", ""),
        ("0x00544f39", "CDXLandscape__Shutdown", "PUSH", "0x544770"),
        ("0x00544f42", "CDXLandscape__Shutdown", "CALL", "0x0055db0a"),
        ("0x00544fa4", "CDXLandscape__Shutdown", "RET", ""),
    }
    missing_instr = expected_instructions - instructions
    if missing_instr:
        failures.append(f"missing expected instructions: {sorted(missing_instr)}")

    caller_instructions = {
        (
            normalize_address(row["instruction_addr"]),
            row["function_name"],
            row["mnemonic"],
            row["operands"],
        )
        for row in read_tsv_rows(PRE / "instructions_callers_focus.tsv")
    }
    expected_callers = {
        ("0x00449bd2", "CEngine__Init", "CALL", "0x00544a00"),
        ("0x00449c01", "CEngine__Init", "PUSH", "ECX"),
        ("0x00449c04", "CEngine__Init", "CALL", "0x00544af0"),
        ("0x004498da", "CEngine__Shutdown", "CALL", "0x00544f10"),
        ("0x00544a43", "CDXLandscape__ScalarDeletingDestructor", "CALL", "0x00544a60"),
        ("0x00544a48", "CDXLandscape__ScalarDeletingDestructor", "TEST", "byte ptr [ESP + 0x8], 0x1"),
    }
    missing_callers = expected_callers - caller_instructions
    if missing_callers:
        failures.append(f"missing expected caller/proof instructions: {sorted(missing_callers)}")


def check_docs_and_ledgers(failures: list[str]) -> None:
    texts = {
        "public note": read_text(PUBLIC_NOTE),
        "function index": read_text(FUNCTION_INDEX),
        "DXLandscape doc": read_text(DXLANDSCAPE_DOC),
        "campaign": read_text(CAMPAIGN),
        "backlog": read_text(BACKLOG),
        "ledger": read_text(LEDGER),
        "attempt log": read_text(ATTEMPT_LOG),
    }
    common_tokens = (
        "Wave601",
        "CDXLandscape",
        "0x00544770",
        "0x005447d0",
        "0x005447e0",
        "0x00544a00",
        "0x00544a40",
        "0x00544a60",
        "0x00544af0",
        "0x00544eb0",
        "0x00544f10",
        "3005",
        "1324",
        "1073",
        "3043/6093 = 49.94%",
        "0x00544fc0 CDXLandscape__BuildVertexBuffer",
        "[maintainer-local-ghidra-backup-root]\\BEA_20260519-181626_post_wave601_cdxlandscape_head_verified",
    )
    for label, text in texts.items():
        require_tokens(label, text, common_tokens[:9], failures)
        require_tokens(label, text, ("Wave601", "CDXLandscape", "0x00544fc0 CDXLandscape__BuildVertexBuffer"), failures)
        lowered = text.lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"{label} overclaims: {token}")

    require_tokens("public note", texts["public note"], common_tokens, failures)
    require_tokens("function index", texts["function index"], common_tokens, failures)
    require_tokens("DXLandscape doc", texts["DXLandscape doc"], ("engine+0x49c", "0x005e50d0", "vtable slot `4`", "DXLandscape.h", "line `0xaa`"), failures)
    require_tokens("campaign", texts["campaign"], common_tokens, failures)
    require_tokens("backlog", texts["backlog"], ("updated=9 skipped=0 renamed=0 would_rename=0 missing=0 bad=0", "2061"), failures)
    require_tokens("ledger", texts["ledger"], ("Wave601", "2061 instruction rows"), failures)
    require_tokens("attempt log", texts["attempt log"], ("\"attempt_id\":20256", "headless_java_apply_signature_comment_tags_no_renames"), failures)


def check_queue_tracking_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    expected_quality = {
        "commentlessFunctionCount": 3005,
        "undefinedSignatureCount": 1324,
        "paramSignatureCount": 1073,
        "legacyWeakNameCount": 0,
        "uncertainOwnerNameCount": 0,
    }
    if queue.get("status") != "PASS":
        failures.append(f"queue status mismatch: {queue.get('status')}")
    if queue.get("totalFunctions") != 6093:
        failures.append(f"queue total mismatch: {queue.get('totalFunctions')}")
    for key, expected in expected_quality.items():
        actual = quality.get(key)
        if actual != expected:
            failures.append(f"queue {key} mismatch: {actual} != {expected}")
    head = queue["priorityQueues"]["commentlessHighSignal"][0]
    if head.get("address") != "0x00544fc0" or head.get("name") != "CDXLandscape__BuildVertexBuffer":
        failures.append(f"queue head mismatch: {head}")

    tracking = read_json(TRACKING)
    expected_counters = {"ledger_rows": 997, "attempt_rows": 20257, "completed": 988, "pending": 9}
    for key, expected in expected_counters.items():
        actual = tracking["counters"].get(key)
        if actual != expected:
            failures.append(f"tracking counter {key} mismatch: {actual} != {expected}")
    if tracking.get("next_attempt_id") != 20257:
        failures.append(f"tracking next_attempt_id mismatch: {tracking.get('next_attempt_id')}")
    require_tokens("tracking notes", "\n".join(tracking.get("notes", [])), ("Wave601", "0x00544fc0 CDXLandscape__BuildVertexBuffer"), failures)

    backup = read_json(BACKUP_SUMMARY)
    expected_backup = {
        "sourcePath": str(Path.home() / "Ghidra" / "Projects"),
        "backupPath": "[maintainer-local-ghidra-backup-root]\\BEA_20260519-181626_post_wave601_cdxlandscape_head_verified",
        "fileCount": 19,
        "totalBytes": 161221511,
        "missingCount": 0,
        "extraCount": 0,
        "diffCount": 0,
        "manifestHash": "85163222f6735243e7c38d289b7f40795f8c9ab1952f39c6c21dfc3fd8312657",
    }
    for key, expected in expected_backup.items():
        actual = backup.get(key)
        if actual != expected:
            failures.append(f"backup {key} mismatch: {actual} != {expected}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.check:
        parser.error("expected --check")

    failures: list[str] = []
    try:
        check_logs(failures)
        check_post_exports(failures)
        check_xrefs_and_instructions(failures)
        check_docs_and_ledgers(failures)
        check_queue_tracking_backup(failures)
    except Exception as exc:  # pragma: no cover - command-line diagnostics
        failures.append(f"probe exception: {exc}")

    if failures:
        print("Wave601 CDXLandscape head probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Wave601 CDXLandscape head probe: PASS")
    print("Verified 9 signatures/comments/tags, 25 xrefs, 2061 instruction rows, 9 decompile rows, queue telemetry, docs, ledgers, and backup summary.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
