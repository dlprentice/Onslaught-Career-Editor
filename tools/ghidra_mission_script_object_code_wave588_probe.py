#!/usr/bin/env python3
"""Validate Wave588 CMissionScriptObjectCode Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave588-cmission-script-object-code-00539c80"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUALITY_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_mission_script_object_code_wave588_2026-05-19.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
SCRIPT_OBJECT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "ScriptObjectCode.cpp.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
BACKUP_SUMMARY = BASE / "wave588_backup_summary.json"

COMMON_TAGS = {
    "static-reaudit",
    "mission-script-object-code-wave588",
    "retail-binary-evidence",
    "mission-script",
    "mission-script-object-code",
    "signature-corrected",
    "comment-hardened",
}

TARGETS = {
    "0x00539c80": (
        "CMissionScriptObjectCode__CMissionScriptObjectCode",
        "void * __fastcall CMissionScriptObjectCode__CMissionScriptObjectCode(void * this)",
        {"constructor", "waiting-thread-base", "ecx-only"},
        ("CWaitingThread__ctor_base", "0x005e4f5c[0]", "full vtable boundary remains unproven"),
    ),
    "0x00539ca0": (
        "CMissionScriptObjectCode__LoadAsync",
        "void __thiscall CMissionScriptObjectCode__LoadAsync(void * this)",
        {"async-load", "vtable-slot", "cdx-mem-buffer", "thiscall"},
        ("CDXMemBuffer__InitFromFile", "DebugTrace", "Only slot 0x005e4f5c[0] is proven"),
    ),
    "0x00539dc0": (
        "CMissionScriptObjectCode__StartLoadAsync",
        "void __thiscall CMissionScriptObjectCode__StartLoadAsync(void * this, char * filename, int buffer_size)",
        {"async-start", "ret-8", "bink-open-thread", "filename-copy"},
        ("RET 0x8", "filename", "CBinkOpenThread__StartAsync"),
    ),
    "0x00539f00": (
        "CMissionScriptObjectCode__InitFields",
        "void __fastcall CMissionScriptObjectCode__InitFields(void * field_block)",
        {"field-block", "hud-init", "ecx-only"},
        ("CHud__Init", "field-block", "does not prove a full CMissionScriptObjectCode instance layout"),
    ),
    "0x00539f30": (
        "CMissionScriptObjectCode__ClearFields_Thunk",
        "void __fastcall CMissionScriptObjectCode__ClearFields_Thunk(void * field_block)",
        {"field-block", "hud-shutdown", "clear-fields-thunk", "jmp-thunk", "renamed"},
        ("one-instruction JMP thunk", "CHud__ShutDown", "0x00539f40"),
    ),
    "0x00539f40": (
        "CMissionScriptObjectCode__ClearFields",
        "void __fastcall CMissionScriptObjectCode__ClearFields(void * field_block)",
        {"field-block", "hud-shutdown", "free-object-if-present", "ecx-only"},
        ("CMissionScriptObjectCode__FreeObjectIfPresent", "CHud__DecrementCounter9C", "does not prove a full CMissionScriptObjectCode instance layout"),
    ),
}

OVERCLAIM_TOKENS = (
    "full vtable boundary proven",
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
        BASE / "logs" / "wave588_apply_dry.log",
        {"updated": 0, "skipped": 6, "renamed": 0, "would_rename": 1, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "logs" / "wave588_apply.log",
        {"updated": 6, "skipped": 0, "renamed": 1, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "logs" / "wave588_apply_final_dry.log",
        {"updated": 0, "skipped": 6, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )


def check_post_exports(failures: list[str]) -> None:
    metadata = read_tsv(BASE / "post" / "metadata.tsv")
    tags = read_tsv(BASE / "post" / "tags.tsv")
    if len(metadata) != 6:
        failures.append(f"metadata row count mismatch: {len(metadata)}")
    if len(tags) != 6:
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

    if row_count(BASE / "post" / "xrefs.tsv") != 7:
        failures.append("post xref row count mismatch")
    if row_count(BASE / "post" / "instructions.tsv") != 534:
        failures.append("post instruction row count mismatch")
    if row_count(BASE / "post" / "decompile" / "index.tsv") != 6:
        failures.append("post decompile row count mismatch")
    if row_count(BASE / "post" / "vtables.tsv") != 64:
        failures.append("post vtable row count mismatch")


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
        ("0x00539c80", "CMissionScriptObjectCode__CMissionScriptObjectCode", "0x00465ffb", "0x00465f10", "CFEPMultiplayerStart__ctor", "UNCONDITIONAL_CALL"),
        ("0x00539ca0", "CMissionScriptObjectCode__LoadAsync", "0x005e4f5c", "<none>", "<no_function>", "DATA"),
        ("0x00539dc0", "CMissionScriptObjectCode__StartLoadAsync", "0x0045cb5d", "0x0045c9f0", "CFEPGoodies__StartLoadingGoody", "UNCONDITIONAL_CALL"),
        ("0x00539f00", "CMissionScriptObjectCode__InitFields", "0x004814df", "0x00481450", "CHud__Init", "UNCONDITIONAL_CALL"),
        ("0x00539f30", "CMissionScriptObjectCode__ClearFields_Thunk", "0x00481b44", "0x00481b00", "CHud__ShutDown", "UNCONDITIONAL_CALL"),
        ("0x00539f40", "CMissionScriptObjectCode__ClearFields", "0x00481b0e", "0x00481b00", "CHud__ShutDown", "UNCONDITIONAL_CALL"),
        ("0x00539f40", "CMissionScriptObjectCode__ClearFields", "0x00539f30", "0x00539f30", "CMissionScriptObjectCode__ClearFields_Thunk", "UNCONDITIONAL_JUMP"),
    }
    missing = expected - actual
    if missing:
        failures.append(f"missing expected xrefs: {sorted(missing)}")


def check_instructions_and_vtable(failures: list[str]) -> None:
    rows = read_tsv_rows(BASE / "post" / "instructions.tsv")
    instructions = {
        (normalize_address(row["instruction_addr"]), row["mnemonic"], row["operands"])
        for row in rows
    }
    expected_instructions = {
        ("0x00539c83", "CALL", "0x00528bc0"),
        ("0x00539c88", "MOV", "dword ptr [ESI], 0x5e4f5c"),
        ("0x00539c8e", "MOV", "byte ptr [ESI + 0x20], 0x0"),
        ("0x00539c95", "RET", ""),
        ("0x00539e02", "RET", "0x8"),
        ("0x00539f24", "RET", ""),
        ("0x00539f30", "JMP", "0x00539f40"),
        ("0x00539f4f", "CALL", "0x004f7440"),
        ("0x0053a003", "RET", ""),
    }
    missing = expected_instructions - instructions
    if missing:
        failures.append(f"missing expected instructions: {sorted(missing)}")

    vtables = read_tsv_rows(BASE / "post" / "vtables.tsv")
    slot0 = next((row for row in vtables if row["vtable"] == "005e4f5c" and row["slot_index"] == "0"), None)
    if slot0 is None:
        failures.append("missing vtable slot 0")
    elif slot0["function_entry"] != "00539ca0" or slot0["function_name"] != "CMissionScriptObjectCode__LoadAsync":
        failures.append(f"unexpected vtable slot 0: {slot0}")
    slot2 = next((row for row in vtables if row["vtable"] == "005e4f5c" and row["slot_index"] == "2"), None)
    if slot2 is None or slot2["function_name"] != "CDXBattleLine__scalar_deleting_dtor":
        failures.append("vtable boundary guard missing adjacent CDXBattleLine evidence")


def check_decompile(failures: list[str]) -> None:
    text = "\n".join(path.read_text(encoding="utf-8") for path in (BASE / "post" / "decompile").glob("*.c"))
    require_tokens(
        "post decompile",
        text,
        (
            "CMissionScriptObjectCode__ClearFields_Thunk",
            "CMissionScriptObjectCode__LoadAsync",
            "CMissionScriptObjectCode__StartLoadAsync",
            "CWaitingThread__ctor_base",
            "CDXMemBuffer__InitFromFile",
            "CBinkOpenThread__WaitForThread",
            "CBinkOpenThread__StartAsync",
            "CMissionScriptObjectCode__FreeObjectIfPresent",
        ),
        failures,
    )
    for token in OVERCLAIM_TOKENS:
        if token in text.lower():
            failures.append(f"decompile contains overclaim token: {token}")


def check_queue_and_backup(failures: list[str]) -> None:
    queue = json.loads(read_text(QUEUE_JSON))
    if queue.get("totalFunctions") != 6093:
        failures.append(f"queue total mismatch: {queue.get('totalFunctions')}")
    signals = queue.get("qualitySignals", {})
    expected_signals = {
        "commentlessFunctionCount": 3087,
        "undefinedSignatureCount": 1359,
        "paramSignatureCount": 1116,
    }
    for key, expected in expected_signals.items():
        actual = signals.get(key)
        if actual != expected:
            failures.append(f"queue {key} mismatch: {actual} != {expected}")
    head = (queue.get("priorityQueues", {}).get("commentlessHighSignal") or [{}])[0]
    if head.get("address") != "0x0053a050" or head.get("name") != "CDXBattleLine__Constructor":
        failures.append(f"unexpected next queue head: {head}")

    rows = read_tsv_rows(QUALITY_TSV)
    strict = [
        row for row in rows
        if row["comment"].strip()
        and not row["signature"].startswith("undefined ")
        and not re.search(r"\bparam_[0-9]+", row["signature"])
    ]
    if len(strict) != 2960:
        failures.append(f"strict clean signature proxy mismatch: {len(strict)}")

    backup = json.loads(read_text(BACKUP_SUMMARY))
    expected_backup = {
        "FileCount": 19,
        "TotalBytes": 160893831,
        "MissingCount": 0,
        "ExtraCount": 0,
        "DiffCount": 0,
        "ManifestHash": "ef5cc4c7c0c7f5ef102a1a748647b231a36c39b430e5379fb06a627992982841",
    }
    for key, expected in expected_backup.items():
        actual = backup.get(key)
        if actual != expected:
            failures.append(f"backup {key} mismatch: {actual} != {expected}")
    if "post_wave588_cmission_script_object_code_verified" not in backup.get("BackupPath", ""):
        failures.append(f"unexpected backup path: {backup.get('BackupPath')}")


def check_docs(failures: list[str]) -> None:
    require_tokens(
        "release note",
        read_text(PUBLIC_NOTE),
        ("Wave588", "CMissionScriptObjectCode", "ClearFields_Thunk", "0x005e4f5c[0]", "CDXBattleLine__Constructor"),
        failures,
    )
    require_tokens(
        "function index",
        read_text(FUNCTION_INDEX),
        (
            "Wave588 CMissionScriptObjectCode hardening",
            "Post-Wave588 queue telemetry is `6093` functions, `3006` commented, `3087` commentless, `1359` exact-undefined signatures, and `1116` `param_N` signatures.",
            "0x0053a050 CDXBattleLine__Constructor",
        ),
        failures,
    )
    require_tokens(
        "ScriptObjectCode doc",
        read_text(SCRIPT_OBJECT_DOC),
        ("## Wave588 Static Read-Back", "CMissionScriptObjectCode__ClearFields_Thunk", "Only slot `0x005e4f5c[0]` is proven"),
        failures,
    )
    require_tokens(
        "GHIDRA reference",
        read_text(GHIDRA_REFERENCE),
        ("Wave588 CMissionScriptObjectCode", "CMissionScriptObjectCode__StartLoadAsync", "2960/6093 = 48.58%"),
        failures,
    )
    require_tokens(
        "campaign",
        read_text(CAMPAIGN),
        ("Wave 588: CMissionScriptObjectCode Async/Field Block", "post_wave588_cmission_script_object_code_verified", "strict clean-signature proxy `2960/6093 = 48.58%`"),
        failures,
    )
    require_tokens("backlog", read_text(BACKLOG), ("0x00539c80,0x00539ca0,0x00539dc0", "Wave588"), failures)
    require_tokens("ledger", read_text(LEDGER), ("Ghidra CMissionScriptObjectCode Wave588", "post_wave588_cmission_script_object_code_verified"), failures)
    require_tokens("attempt log", read_text(ATTEMPT_LOG), ("Ghidra CMissionScriptObjectCode Wave588", '"attempt_id":20243'), failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run Wave588 checks")
    args = parser.parse_args()
    if not args.check:
        parser.error("--check is required")

    failures: list[str] = []
    check_logs(failures)
    check_post_exports(failures)
    check_xrefs(failures)
    check_instructions_and_vtable(failures)
    check_decompile(failures)
    check_queue_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave588 CMissionScriptObjectCode probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave588 CMissionScriptObjectCode probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
