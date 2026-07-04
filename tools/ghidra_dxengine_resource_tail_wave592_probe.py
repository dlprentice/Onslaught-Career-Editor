#!/usr/bin/env python3
"""Validate Wave592 CDXEngine resource-tail Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave592-dxengine-render-tail-0053d3a0"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_dxengine_resource_tail_wave592_2026-05-19.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
ENGINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "engine.cpp" / "_index.md"
LTSHELL_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "ltshell.cpp" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
BACKUP_SUMMARY = BASE / "wave592_backup_summary.json"

COMMON_TAGS = {
    "static-reaudit",
    "dxengine-resource-tail-wave592",
    "retail-binary-evidence",
    "cdxengine",
    "resource-lifecycle",
    "signature-corrected",
    "comment-hardened",
}

TARGETS = {
    "0x0053d3a0": (
        "CDXEngine__ReleaseDefaultTextureAndMeshRefs",
        "void __fastcall CDXEngine__ReleaseDefaultTextureAndMeshRefs(void * this)",
        {"owner-corrected", "resource-release", "default-texture", "default-mesh", "ecx-only", "renamed"},
        ("CLTShell shutdown", "this+0x4e4", "this+0x28 + 0x170"),
    ),
    "0x0053d3e0": (
        "CDXEngine__Shutdown",
        "void __fastcall CDXEngine__Shutdown(void * this)",
        {"vtable-slot-2", "resource-release", "texture-release", "patch-manager", "ecx-only", "renamed"},
        ("vtable slot 2", "CEngine__Shutdown", "CDXPatchManager"),
    ),
    "0x0053d4c0": (
        "CDXEngine__UploadScaledRgbLookupTable",
        "void __thiscall CDXEngine__UploadScaledRgbLookupTable(void * this, float gammaScale)",
        {"gamma-ramp", "rgb-lookup-table", "setgammabias", "ret-0x4"},
        ("SetGammaBias", "RET 0x4", "device vfunc at +0x54"),
    ),
    "0x0053d5f0": (
        "CDXEngine__Init",
        "int __fastcall CDXEngine__Init(void * this)",
        {"vtable-slot-0", "init", "console-command", "console-variable", "patch-manager", "ecx-only", "renamed"},
        ("vtable slot 0", "CGame__Init", "SetGammaBias"),
    ),
    "0x0053d6d0": (
        "CDXEngine__InitResources",
        "void __fastcall CDXEngine__InitResources(void * this)",
        {"vtable-slot-1", "resource-load", "default-texture", "default-mesh", "sun-sprite", "ecx-only", "renamed"},
        ("vtable slot 1", "CGame__RunLevel", "Sun_Sprite"),
    ),
}

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "source identity proven",
    "rebuild parity proven",
    "fully recovered",
    "fully re'ed",
    "fully reverse-engineered",
)


def normalize_address(address: str) -> str:
    value = address.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    if value.startswith("<"):
        return value
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


def read_tsv(path: Path, key: str = "address") -> dict[str, dict[str, str]]:
    return {normalize_address(row[key]): row for row in read_tsv_rows(path)}


def row_count(path: Path) -> int:
    return len(read_tsv_rows(path))


def require_tokens(label: str, text: str, tokens: tuple[str, ...] | set[str], failures: list[str]) -> None:
    normalized_text = text.replace("\\\\", "\\")
    for token in tokens:
        if token == "runtime":
            if token not in text.lower():
                failures.append(f"{label} missing token: {token}")
            continue
        if token not in normalized_text:
            failures.append(f"{label} missing token: {token}")


def require_log_summary(path: Path, expected: dict[str, int], failures: list[str]) -> None:
    text = read_text(path)
    match = re.search(r"SUMMARY\s+([^\r\n]+)", text)
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
        BASE / "logs" / "wave592_apply_dry.log",
        {"updated": 0, "skipped": 5, "renamed": 0, "would_rename": 4, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "logs" / "wave592_apply.log",
        {"updated": 5, "skipped": 0, "renamed": 4, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "logs" / "wave592_apply_final_dry.log",
        {"updated": 0, "skipped": 5, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )


def check_post_exports(failures: list[str]) -> None:
    metadata = read_tsv(BASE / "post" / "metadata.tsv")
    tags = read_tsv(BASE / "post" / "tags.tsv")
    if len(metadata) != 5:
        failures.append(f"metadata row count mismatch: {len(metadata)}")
    if len(tags) != 5:
        failures.append(f"tag row count mismatch: {len(tags)}")

    for address, (name, signature, extra_tags, comment_tokens) in TARGETS.items():
        row = metadata.get(address)
        if row is None:
            failures.append(f"{address} missing from post metadata")
            continue
        if row["name"] != name:
            failures.append(f"{address} name mismatch: {row['name']} != {name}")
        if row["signature"] != signature:
            failures.append(f"{address} signature mismatch: {row['signature']} != {signature}")
        if row["status"] != "OK":
            failures.append(f"{address} metadata status mismatch: {row['status']}")
        require_tokens(f"{address} comment", row["comment"], comment_tokens, failures)
        lowered = row["comment"].lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"{address} comment overclaims: {token}")

        tag_row = tags.get(address)
        if tag_row is None:
            failures.append(f"{address} missing from post tags")
            continue
        actual_tags = set(filter(None, tag_row["tags"].split(";")))
        missing = (COMMON_TAGS | extra_tags) - actual_tags
        if missing:
            failures.append(f"{address} missing tags: {sorted(missing)}")

    expected_counts = {
        "xrefs.tsv": 8,
        "instructions.tsv": 1305,
        "decompile/index.tsv": 5,
        "decompile/callers/index.tsv": 3,
        "callsite_instructions.tsv": 205,
        "proof_instructions.tsv": 1305,
        "vtable.tsv": 3,
    }
    actual_counts = {
        "xrefs.tsv": row_count(BASE / "post" / "xrefs.tsv"),
        "instructions.tsv": row_count(BASE / "post" / "instructions.tsv"),
        "decompile/index.tsv": row_count(BASE / "post" / "decompile" / "index.tsv"),
        "decompile/callers/index.tsv": row_count(BASE / "post" / "decompile" / "callers" / "index.tsv"),
        "callsite_instructions.tsv": row_count(BASE / "post" / "callsite_instructions.tsv"),
        "proof_instructions.tsv": row_count(BASE / "post" / "proof_instructions.tsv"),
        "vtable.tsv": row_count(BASE / "post" / "vtable.tsv"),
    }
    for label, expected in expected_counts.items():
        if actual_counts[label] != expected:
            failures.append(f"post {label} row count mismatch: {actual_counts[label]} != {expected}")


def check_xrefs_and_slots(failures: list[str]) -> None:
    xrefs = {
        (
            normalize_address(row["target_addr"]),
            row["target_name"],
            normalize_address(row["from_addr"]),
            normalize_address(row["from_function_addr"]),
            row["from_function"],
            row["ref_type"],
        )
        for row in read_tsv_rows(BASE / "post" / "xrefs.tsv")
    }
    expected_xrefs = {
        ("0x0053d3a0", "CDXEngine__ReleaseDefaultTextureAndMeshRefs", "0x004f01b0", "0x004f00e0", "CLTShell__ShutdownRuntimeAndReleaseResources", "UNCONDITIONAL_CALL"),
        ("0x0053d3e0", "CDXEngine__Shutdown", "0x005e4fd0", "<none>", "<no_function>", "DATA"),
        ("0x0053d4c0", "CDXEngine__UploadScaledRgbLookupTable", "0x0053d4b9", "<none>", "<no_function>", "UNCONDITIONAL_CALL"),
        ("0x0053d5f0", "CDXEngine__Init", "0x0046c39f", "0x0046c360", "CGame__Init", "UNCONDITIONAL_CALL"),
        ("0x0053d6d0", "CDXEngine__InitResources", "0x0046e335", "0x0046e240", "CGame__RunLevel", "UNCONDITIONAL_CALL"),
    }
    missing = expected_xrefs - xrefs
    if missing:
        failures.append(f"missing expected xrefs: {sorted(missing)}")

    slots = {
        (row["slot_index"], normalize_address(row["slot_addr"]), row["function_name"], row["status"])
        for row in read_tsv_rows(BASE / "post" / "vtable.tsv")
    }
    expected_slots = {
        ("0", "0x005e4fc8", "CDXEngine__Init", "OK"),
        ("1", "0x005e4fcc", "CDXEngine__InitResources", "OK"),
        ("2", "0x005e4fd0", "CDXEngine__Shutdown", "OK"),
    }
    missing_slots = expected_slots - slots
    if missing_slots:
        failures.append(f"missing expected vtable slots: {sorted(missing_slots)}")


def check_instruction_evidence(failures: list[str]) -> None:
    rows = read_tsv_rows(BASE / "post" / "instructions.tsv") + read_tsv_rows(BASE / "post" / "callsite_instructions.tsv")
    instructions = {
        (normalize_address(row["instruction_addr"]), row["function_name"], row["mnemonic"], row["operands"])
        for row in rows
    }
    expected = {
        ("0x004f01b0", "CLTShell__ShutdownRuntimeAndReleaseResources", "CALL", "0x0053d3a0"),
        ("0x0046c39f", "CGame__Init", "CALL", "0x0053d5f0"),
        ("0x0046e335", "CGame__RunLevel", "CALL", "0x0053d6d0"),
        ("0x0053d4b9", "<no_function>", "CALL", "0x0053d4c0"),
        ("0x0053d5e3", "CDXEngine__UploadScaledRgbLookupTable", "RET", "0x4"),
        ("0x0053d6d0", "CDXEngine__InitResources", "PUSH", "ESI"),
    }
    missing = expected - instructions
    if missing:
        failures.append(f"missing instruction evidence: {sorted(missing)}")


def check_queue_and_backup(failures: list[str]) -> None:
    queue = json.loads(read_text(QUEUE_JSON))
    signals = queue.get("qualitySignals", {})
    expected = {
        "commentlessFunctionCount": 3061,
        "undefinedSignatureCount": 1347,
        "paramSignatureCount": 1101,
    }
    for key, value in expected.items():
        if signals.get(key) != value:
            failures.append(f"queue {key} mismatch: {signals.get(key)} != {value}")
    first = queue.get("priorityQueues", {}).get("commentlessHighSignal", [{}])[0]
    if first.get("address") != "0x0053d760" or first.get("name") != "CThing__RenderDebugVolumeOverlay":
        failures.append(f"unexpected queue head: {first}")

    backup = json.loads(read_text(BACKUP_SUMMARY))
    if backup.get("BackupPath") != "[maintainer-local-ghidra-backup-root]\\BEA_20260519-134212_post_wave592_dxengine_resource_tail_verified":
        failures.append("backup path mismatch")
    for key, expected_value in {
        "FileCount": 19,
        "TotalBytes": 160992135,
        "MissingCount": 0,
        "ExtraCount": 0,
        "DiffCount": 0,
    }.items():
        if backup.get(key) != expected_value:
            failures.append(f"backup {key} mismatch: {backup.get(key)} != {expected_value}")
    if backup.get("ManifestHash") != "de15221c47eb97780dca8330a7a1decf858f621f3b267da86e4d8650488d7415":
        failures.append("backup manifest hash mismatch")


def check_docs_and_logs(failures: list[str]) -> None:
    docs = {
        "public note": read_text(PUBLIC_NOTE),
        "function index": read_text(FUNCTION_INDEX),
        "engine doc": read_text(ENGINE_DOC),
        "ltshell doc": read_text(LTSHELL_DOC),
        "ghidra reference": read_text(GHIDRA_REFERENCE),
        "campaign": read_text(CAMPAIGN),
        "backlog": read_text(BACKLOG),
        "ledger": read_text(LEDGER),
        "attempt log": read_text(ATTEMPT_LOG),
    }
    required_tokens = (
        "Wave592",
        "CDXEngine__ReleaseDefaultTextureAndMeshRefs",
        "CDXEngine__Shutdown",
        "CDXEngine__UploadScaledRgbLookupTable",
        "CDXEngine__Init",
        "CDXEngine__InitResources",
        "0x0053d760 CThing__RenderDebugVolumeOverlay",
        "[maintainer-local-ghidra-backup-root]\\BEA_20260519-134212_post_wave592_dxengine_resource_tail_verified",
        "runtime",
        "unproven",
    )
    for label, text in docs.items():
        require_tokens(label, text, required_tokens[:6], failures)
        if label in {"public note", "campaign", "backlog", "ledger", "attempt log"}:
            require_tokens(label, text, required_tokens[6:], failures)
        lowered = text.lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"{label} overclaims: {token}")


def run_check() -> tuple[bool, dict[str, object]]:
    failures: list[str] = []
    check_logs(failures)
    check_post_exports(failures)
    check_xrefs_and_slots(failures)
    check_instruction_evidence(failures)
    check_queue_and_backup(failures)
    check_docs_and_logs(failures)
    return not failures, {"status": "PASS" if not failures else "FAIL", "failures": failures}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Return nonzero if validation fails.")
    parser.add_argument("--json", action="store_true", help="Print JSON result.")
    args = parser.parse_args()

    ok, result = run_check()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(result["status"])
        for failure in result["failures"]:
            print(f"- {failure}")
    return 0 if ok or not args.check else 1


if __name__ == "__main__":
    raise SystemExit(main())
