#!/usr/bin/env python3
"""Validate Wave590 CClouds Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave590-cclouds-head-0053b900"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cclouds_head_wave590_2026-05-19.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
DXCLOUDS_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXClouds.cpp.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
BACKUP_SUMMARY = BASE / "wave590_backup_summary.json"

COMMON_TAGS = {
    "static-reaudit",
    "cclouds-head-wave590",
    "retail-binary-evidence",
    "cclouds",
    "dx-render",
    "signature-corrected",
    "comment-hardened",
}

TARGETS = {
    "0x0053b900": (
        "CClouds__Constructor",
        "void * __fastcall CClouds__Constructor(void * this)",
        {"constructor", "atmospherics", "cloud-texture", "cg-cloudwidth", "vtable-005e4f9c", "ecx-only", "renamed"},
        ("Atmospherics__Init", "0x005e4f9c", "cg_cloudwidth"),
    ),
    "0x0053ba20": (
        "CClouds__Shutdown",
        "void __fastcall CClouds__Shutdown(void * this)",
        {"shutdown", "vtable-slot", "slot-4", "resource-release", "cloud-texture", "ecx-only", "renamed"},
        ("vtable 0x005e4f9c slot 4", "CHud__DecrementCounter9C", "CVBufTexture"),
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


def read_tsv(path: Path, key: str = "address") -> dict[str, dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    return {normalize_address(row[key]): row for row in rows}


def read_tsv_rows(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def row_count(path: Path) -> int:
    return len(read_tsv_rows(path))


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
        BASE / "logs" / "wave590_apply_dry.log",
        {"updated": 0, "skipped": 2, "renamed": 0, "would_rename": 2, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "logs" / "wave590_apply.log",
        {"updated": 2, "skipped": 0, "renamed": 2, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "logs" / "wave590_apply_final_dry.log",
        {"updated": 0, "skipped": 2, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )


def check_post_exports(failures: list[str]) -> None:
    metadata = read_tsv(BASE / "post" / "metadata.tsv")
    tags = read_tsv(BASE / "post" / "tags.tsv")
    if len(metadata) != 2:
        failures.append(f"metadata row count mismatch: {len(metadata)}")
    if len(tags) != 2:
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
        expected_tags = COMMON_TAGS | extra_tags
        missing = expected_tags - actual_tags
        if missing:
            failures.append(f"{address} missing tags: {sorted(missing)}")

    expected_counts = {
        "xrefs.tsv": row_count(BASE / "post" / "xrefs.tsv"),
        "instructions.tsv": row_count(BASE / "post" / "instructions.tsv"),
        "decompile/index.tsv": row_count(BASE / "post" / "decompile" / "index.tsv"),
        "vtables.tsv": row_count(BASE / "post" / "vtables.tsv"),
        "callsite_instructions.tsv": row_count(BASE / "post" / "callsite_instructions.tsv"),
        "proof_instructions.tsv": row_count(BASE / "post" / "proof_instructions.tsv"),
        "shutdown_instructions.tsv": row_count(BASE / "post" / "shutdown_instructions.tsv"),
    }
    if expected_counts["xrefs.tsv"] != 2:
        failures.append("post xref row count mismatch")
    if expected_counts["instructions.tsv"] != 522:
        failures.append("post instruction row count mismatch")
    if expected_counts["decompile/index.tsv"] != 2:
        failures.append("post decompile row count mismatch")
    if expected_counts["vtables.tsv"] != 12:
        failures.append("post vtable row count mismatch")
    if expected_counts["callsite_instructions.tsv"] != 30:
        failures.append("post callsite instruction row count mismatch")
    if expected_counts["proof_instructions.tsv"] != 99:
        failures.append("post proof instruction row count mismatch")
    if expected_counts["shutdown_instructions.tsv"] != 81:
        failures.append("post shutdown instruction row count mismatch")


def check_xrefs(failures: list[str]) -> None:
    rows = read_tsv_rows(BASE / "post" / "xrefs.tsv")
    actual = {
        (
            normalize_address(row["target_addr"]),
            row["target_name"],
            normalize_address(row["from_addr"]),
            normalize_address(row["from_function_addr"]),
            row["from_function"],
            row["ref_type"],
        )
        for row in rows
    }
    expected = {
        ("0x0053b900", "CClouds__Constructor", "0x00404acf", "0x00404a00", "Atmospherics__Init", "UNCONDITIONAL_CALL"),
        ("0x0053ba20", "CClouds__Shutdown", "0x005e4fac", "<none>", "<no_function>", "DATA"),
    }
    missing = expected - actual
    if missing:
        failures.append(f"missing expected xrefs: {sorted(missing)}")


def check_instructions_and_vtable(failures: list[str]) -> None:
    proof_rows = read_tsv_rows(BASE / "post" / "proof_instructions.tsv")
    proof = {
        (normalize_address(row["instruction_addr"]), row["mnemonic"], row["operands"])
        for row in proof_rows
    }
    expected_proof = {
        ("0x0053b91f", "CALL", "0x00404920"),
        ("0x0053b93b", "MOV", "dword ptr [ESI], 0x5e4f9c"),
        ("0x0053b941", "CALL", "0x004f27f0"),
        ("0x0053b95c", "CALL", "0x005490e0"),
        ("0x0053b9c2", "CALL", "0x0042b040"),
        ("0x0053b9d8", "RET", ""),
        ("0x0053ba20", "PUSH", "ESI"),
        ("0x0053ba2e", "CALL", "0x004f27e0"),
        ("0x0053ba43", "CALL", "0x00500460"),
        ("0x0053ba4e", "CALL", "0x00549220"),
        ("0x0053ba5c", "RET", ""),
    }
    missing = expected_proof - proof
    if missing:
        failures.append(f"missing expected proof instructions: {sorted(missing)}")

    callsite_rows = read_tsv_rows(BASE / "post" / "callsite_instructions.tsv")
    callsite = {
        (normalize_address(row["instruction_addr"]), row["mnemonic"], row["operands"])
        for row in callsite_rows
    }
    expected_callsite = {
        ("0x00404ab8", "CALL", "0x005490e0"),
        ("0x00404acd", "MOV", "ECX, EAX"),
        ("0x00404acf", "CALL", "0x0053b900"),
    }
    missing = expected_callsite - callsite
    if missing:
        failures.append(f"missing expected callsite instructions: {sorted(missing)}")

    shutdown_rows = read_tsv_rows(BASE / "post" / "shutdown_instructions.tsv")
    shutdown = {
        (normalize_address(row["instruction_addr"]), row["mnemonic"], row["operands"])
        for row in shutdown_rows
    }
    if ("0x00404c3e", "CALL", "dword ptr [EAX + 0x10]") not in shutdown:
        failures.append("missing Atmospherics__Shutdown virtual +0x10 dispatch")

    vtables = read_tsv_rows(BASE / "post" / "vtables.tsv")
    slot4 = next((row for row in vtables if row["vtable"] == "005e4f9c" and row["slot_index"] == "4"), None)
    if slot4 is None:
        failures.append("missing CClouds vtable slot 4")
    elif slot4["function_entry"] != "0053ba20" or slot4["function_name"] != "CClouds__Shutdown":
        failures.append(f"CClouds vtable slot 4 mismatch: {slot4}")


def check_queue_and_docs(failures: list[str]) -> None:
    queue = json.loads(read_text(QUEUE_JSON))
    quality = queue["qualitySignals"]
    expected = {
        "commentlessFunctionCount": 3072,
        "undefinedSignatureCount": 1347,
        "paramSignatureCount": 1112,
    }
    for key, expected_value in expected.items():
        if quality.get(key) != expected_value:
            failures.append(f"queue {key} mismatch: {quality.get(key)} != {expected_value}")
    if queue.get("totalFunctions") != 6093:
        failures.append(f"queue total mismatch: {queue.get('totalFunctions')}")
    head = queue["priorityQueues"]["commentlessHighSignal"][0]
    if head["address"] != "0x0053bb50" or head["name"] != "CDXEngine__RenderOptionalFullscreenEffectPass":
        failures.append(f"unexpected queue head: {head}")

    for label, path, tokens in (
        ("public note", PUBLIC_NOTE, ("Wave590", "CClouds", "0x0053bb50", "DiffCount=0")),
        ("function index", FUNCTION_INDEX, ("DXClouds.cpp", "Wave590", "CClouds__Shutdown")),
        ("DXClouds doc", DXCLOUDS_DOC, ("Wave590", "CClouds__Constructor", "cg_cloudwidth")),
        ("ghidra reference", GHIDRA_REFERENCE, ("Wave590", "CClouds__Constructor", "0x005e4f9c[4]")),
        ("campaign", CAMPAIGN, ("Wave 590", "CClouds head", "3021")),
        ("backlog", BACKLOG, ("Wave590", "cclouds-head-wave590")),
    ):
        text = read_text(path)
        require_tokens(label, text, tokens, failures)
        lowered = text.lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"{label} overclaims: {token}")

    ledger_text = read_text(LEDGER)
    require_tokens("ledger", ledger_text, ("Wave590", "0x0053b900", "CClouds__Shutdown"), failures)
    attempt_text = read_text(ATTEMPT_LOG)
    require_tokens("attempt log", attempt_text, ("wave590", "ApplyCCloudsHeadWave590.java", "updated=2"), failures)


def check_backup(failures: list[str]) -> None:
    summary = json.loads(read_text(BACKUP_SUMMARY))
    expected = {
        "FileCount": 19,
        "TotalBytes": 160926599,
        "MissingCount": 0,
        "ExtraCount": 0,
        "DiffCount": 0,
        "ManifestHash": "31163c5c5f3d19d64d073d764769b9625270631f11a06d2ac1d6a9462f0cc898",
    }
    for key, expected_value in expected.items():
        if summary.get(key) != expected_value:
            failures.append(f"backup {key} mismatch: {summary.get(key)} != {expected_value}")
    if "BEA_20260519-122425_post_wave590_cclouds_head_verified" not in summary.get("BackupPath", ""):
        failures.append(f"unexpected backup path: {summary.get('BackupPath')}")


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
        check_xrefs(failures)
        check_instructions_and_vtable(failures)
        check_queue_and_docs(failures)
        check_backup(failures)
    except Exception as exc:  # noqa: BLE001
        failures.append(f"{exc.__class__.__name__}: {exc}")

    if failures:
        print("Wave590 CClouds head probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Wave590 CClouds head probe: PASS")
    print("Verified 2 metadata/tag rows, xrefs, instruction evidence, queue counts, docs, logs, and backup summary.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
