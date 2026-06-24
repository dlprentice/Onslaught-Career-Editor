#!/usr/bin/env python3
"""Validate Wave587 CScriptObjectCode Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave587-scriptobjectcode-core-00538ea0"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_scriptobjectcode_wave587_2026-05-19.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
SCRIPT_OBJECT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "ScriptObjectCode.cpp.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
BACKUP_SUMMARY = BASE / "wave587_backup_summary.json"

COMMON_TAGS = {
    "static-reaudit",
    "scriptobjectcode-wave587",
    "retail-binary-evidence",
    "mission-script",
    "script-object-code",
    "signature-corrected",
    "comment-hardened",
}

TARGETS = {
    "0x00538ea0": ("CScriptObjectCode__scalar_deleting_dtor", "void * __thiscall CScriptObjectCode__scalar_deleting_dtor(void * this, byte delete_flags)", {"destructor", "scalar-deleting-destructor", "ret-4", "vtable-slot"}, ("first observed CScriptObjectCode destructor/vtable slot", "not a proven full vtable boundary")),
    "0x00538ec0": ("CScriptObjectCode__CScriptObjectCode", "void * __thiscall CScriptObjectCode__CScriptObjectCode(void * this, void * bytecode_reader)", {"constructor", "ret-4", "world-load-script-events", "bytecode-reader"}, ("CWorld__LoadScriptEvents", "CAsmInstruction__SpawnFromOpcode", "CEventFunction")),
    "0x00539040": ("CScriptObjectCode__Clone", "void * __fastcall CScriptObjectCode__Clone(void * script_object_code)", {"clone", "ecx-only", "world-clone-script-object-code"}, ("CWorld__CloneScriptObjectCodeByName", "CScriptObjectCode__CloneSymbolTable", "CEventFunction__Clone")),
    "0x005391a0": ("CScriptObjectCode__Destructor", "void __fastcall CScriptObjectCode__Destructor(void * script_object_code)", {"destructor", "ecx-only", "symbol-table"}, ("CScriptObjectCode__ClearSymbolTable", "event functions")),
    "0x005392a0": ("CScriptObjectCode__CollectSpawnThings", "void __fastcall CScriptObjectCode__CollectSpawnThings(void * script_object_code)", {"spawn-thing-scan", "world-load", "ecx-only"}, ("opcode 0x18", "CWorldMeshList__Add")),
    "0x00539350": ("CScriptObjectCode__RestoreStack", "void * __thiscall CScriptObjectCode__RestoreStack(void * this, void * saved_stack)", {"stack-restore", "ret-4", "copy-state"}, ("CScriptObjectCode__CopyState", "saved_stack+0x200")),
    "0x005393e0": ("CScriptObjectCode__ClearStack", "void __fastcall CScriptObjectCode__ClearStack(void * stack)", {"stack-cleanup", "ecx-only", "vm-stack"}, ("CVM__Destructor", "stack+0x200")),
    "0x00539420": ("CScriptObjectCode__Push", "void __thiscall CScriptObjectCode__Push(void * this, void * value)", {"stack-push", "ret-4", "vm-stack"}, ("stack-out-of-memory", "128")),
    "0x00539470": ("CScriptObjectCode__Pop", "void * __fastcall CScriptObjectCode__Pop(void * stack)", {"stack-pop", "ecx-only", "vm-stack"}, ("pop-empty", "returns null")),
    "0x005394a0": ("CScriptObjectCode__RemoveTop", "void __fastcall CScriptObjectCode__RemoveTop(void * stack)", {"stack-remove-top", "ecx-only", "vm-stack"}, ("remove-top-empty", "destructs")),
    "0x005394e0": ("CScriptObjectCode__GetTop", "void * __thiscall CScriptObjectCode__GetTop(void * this, int offset_from_top)", {"stack-peek", "ret-4", "vm-stack"}, ("invalid-stack-item", "offset_from_top")),
    "0x00539510": ("CScriptObjectCode__ClearSymbolTable", "void __fastcall CScriptObjectCode__ClearSymbolTable(void * symbol_table)", {"symbol-table", "symbol-table-cleanup", "ecx-only"}, ("CStringDataType__Destructor", "flex-array storage")),
    "0x005395b0": ("CScriptObjectCode__CloneSymbolTable", "void * __fastcall CScriptObjectCode__CloneSymbolTable(void * symbol_table)", {"symbol-table", "symbol-table-clone", "ecx-only"}, ("0x14-byte table", "de-duplicates names")),
    "0x00539760": ("CScriptObjectCode__GetInstruction", "void * __thiscall CScriptObjectCode__GetInstruction(void * this, int instruction_index)", {"instruction-array", "ret-4", "accessor"}, ("instruction array/flex-array pointer", "not a full CScriptObjectCode instance")),
    "0x00539770": ("CScriptObjectCode__ReadSymbolTable", "void * __thiscall CScriptObjectCode__ReadSymbolTable(void * this, void * bytecode_reader)", {"symbol-table", "bytecode-reader", "ret-4"}, ("CDataType__CreateFromType", "three dwords")),
    "0x005398d0": ("CScriptObjectCode__InitRuntime", "void __fastcall CScriptObjectCode__InitRuntime(void * runtime_state)", {"runtime-state", "initializer", "ecx-only"}, ("0x005e4f1c", "full vtable boundary")),
    "0x00539910": ("CScriptObjectCode__CopyState", "void * __thiscall CScriptObjectCode__CopyState(void * this, void * source_state)", {"runtime-state", "copy-state", "ret-4"}, ("CScriptObjectCode__RestoreStack", "running flag")),
    "0x00539980": ("CScriptObjectCode__Reset", "void __fastcall CScriptObjectCode__Reset(void * stack)", {"runtime-state", "stack-cleanup", "ecx-only"}, ("game", "CScriptEventNB", "CScriptObjectCode__ClearStack")),
    "0x00539990": ("CScriptObjectCode__CallEvent", "void __thiscall CScriptObjectCode__CallEvent(void * this, void * script_object_code, int event_index, void * * params, int param_count)", {"runtime-state", "event-call", "ret-10", "vm-run"}, ("RET 0x10", "event_index", "runs the VM")),
    "0x00539a60": ("CScriptObjectCode__CallEventDirect", "void __thiscall CScriptObjectCode__CallEventDirect(void * this, void * script_object_code, int instruction_index, void * * params, int param_count)", {"runtime-state", "event-call-direct", "ret-10", "vm-run"}, ("CEventFunction__Execute", "RET 0x10", "runs the VM")),
    "0x00539ae0": ("CScriptObjectCode__GotoInstruction", "void __thiscall CScriptObjectCode__GotoInstruction(void * this, int instruction_index)", {"runtime-state", "goto-instruction", "ret-4", "vm-run"}, ("instruction_index", "CScriptObjectCode__Run")),
    "0x00539b00": ("CScriptObjectCode__Run", "void __fastcall CScriptObjectCode__Run(void * runtime_state)", {"runtime-state", "vm-run", "instruction-dispatch", "ecx-only"}, ("10000-instruction limit", "recursive runs", "remaining stack entries")),
}


def normalize_address(address: str) -> str:
    value = address.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
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


def row_count(path: Path) -> int:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8", newline="") as handle:
        return sum(1 for _ in csv.DictReader(handle, delimiter="\t"))


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


def get_ci(mapping: dict[str, object], key: str, default: object = None) -> object:
    if key in mapping:
        return mapping[key]
    lowered = {k.lower(): v for k, v in mapping.items()}
    return lowered.get(key.lower(), default)


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
        BASE / "logs" / "wave587_apply_dry.log",
        {"updated": 0, "skipped": 22, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "logs" / "wave587_apply.log",
        {"updated": 22, "skipped": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "logs" / "wave587_apply_final_dry.log",
        {"updated": 0, "skipped": 22, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )

    expected_counts = {
        "post/metadata.tsv": 22,
        "post/tags.tsv": 22,
        "post/xrefs.tsv": 105,
        "post/instructions.tsv": 2662,
        "post/decompile/index.tsv": 22,
        "post/vtables.tsv": 64,
    }
    for relative_path, expected in expected_counts.items():
        actual = row_count(BASE / relative_path)
        if actual != expected:
            failures.append(f"{relative_path} row count mismatch: {actual} != {expected}")

    metadata = read_tsv(BASE / "post" / "metadata.tsv")
    tags = read_tsv(BASE / "post" / "tags.tsv")
    decomp_index = read_tsv(BASE / "post" / "decompile" / "index.tsv")
    xrefs = read_text(BASE / "post" / "xrefs.tsv")
    instructions = read_text(BASE / "post" / "instructions.tsv")
    vtables = read_text(BASE / "post" / "vtables.tsv")

    require_tokens("xrefs", xrefs, ("CWorld__LoadScriptEvents", "CWorld__CloneScriptObjectCodeByName", "CEventFunction__Execute", "IScript__RestoreSavedStateAndGotoInstruction"), failures)
    require_tokens("instructions", instructions, ("RET\t0x10", "RET\t0x4", "CALL\t0x00539b00", "CALL\t0x00539420"), failures)
    require_tokens("vtables", vtables, ("0x00538ea0", "CScriptObjectCode__scalar_deleting_dtor", "CMissionScriptObjectCode__LoadAsync"), failures)

    overclaim_tokens = (
        "runtime behavior proven",
        "runtime mission-script behavior proven",
        "source identity proven",
        "rebuild parity proven",
        "full vtable boundary proven",
        "fully RE'ed",
        "fully REed",
    )
    for address, (name, signature, extra_tags, comment_tokens) in TARGETS.items():
        row = metadata.get(address)
        if row is None:
            failures.append(f"{address} missing from post_metadata.tsv")
            continue
        if row["status"] != "OK":
            failures.append(f"{address} metadata status is {row['status']}")
        if row["name"] != name:
            failures.append(f"{address} name mismatch: {row['name']} != {name}")
        if row["signature"] != signature:
            failures.append(f"{address} signature mismatch: {row['signature']} != {signature}")
        require_tokens(f"{address} comment", row["comment"], comment_tokens, failures)
        for bad_token in overclaim_tokens:
            if bad_token in row["comment"]:
                failures.append(f"{address} comment overclaims: {bad_token}")

        tag_row = tags.get(address)
        if tag_row is None:
            failures.append(f"{address} missing from post_tags.tsv")
        else:
            actual_tags = set(filter(None, tag_row["tags"].split(";")))
            missing = sorted((COMMON_TAGS | extra_tags) - actual_tags)
            if missing:
                failures.append(f"{address} missing tags: {missing}")

        decomp_row = decomp_index.get(address)
        if decomp_row is None or decomp_row["status"] != "OK":
            failures.append(f"{address} missing/failed decompile row")

    decompile_text = "\n".join(path.read_text(encoding="utf-8") for path in sorted((BASE / "post" / "decompile").glob("*.c")))
    require_tokens(
        "decompile exports",
        decompile_text,
        (
            "CAsmInstruction__SpawnFromOpcode",
            "CScriptObjectCode__CloneSymbolTable",
            "CWorldMeshList__Add",
            "CDataType__CreateFromType",
            "CScriptObjectCode__Run",
            "CScriptObjectCode__RemoveTop",
        ),
        failures,
    )

    queue = json.loads(read_text(QUEUE_JSON))
    if queue.get("status") != "PASS":
        failures.append("queue status is not PASS")
    if queue.get("totalFunctions") != 6093:
        failures.append(f"queue totalFunctions mismatch: {queue.get('totalFunctions')} != 6093")
    signals = queue.get("qualitySignals", {})
    for key, expected in {
        "commentlessFunctionCount": 3093,
        "undefinedSignatureCount": 1365,
        "paramSignatureCount": 1116,
    }.items():
        actual = signals.get(key)
        if actual != expected:
            failures.append(f"queue {key} mismatch: {actual} != {expected}")
    head = (queue.get("priorityQueues", {}).get("commentlessHighSignal") or [{}])[0]
    if head.get("address") != "0x00539c80" or head.get("name") != "CMissionScriptObjectCode__CMissionScriptObjectCode":
        failures.append(f"unexpected next queue head: {head}")

    backup = json.loads(read_text(BACKUP_SUMMARY))
    if get_ci(backup, "DiffCount") != 0 or get_ci(backup, "MissingCount") != 0 or get_ci(backup, "ExtraCount") != 0:
        failures.append(f"backup summary failed: {backup}")
    if get_ci(backup, "FileCount") != 19:
        failures.append(f"backup file count mismatch: {backup}")
    if int(get_ci(backup, "TotalBytes", 0)) != 160861063:
        failures.append(f"backup bytes mismatch: {get_ci(backup, 'TotalBytes')} != 160861063")
    require_tokens("backup destination", str(get_ci(backup, "BackupPath", "")), ("post_wave587_scriptobjectcode_verified",), failures)

    require_doc_tokens(
        PUBLIC_NOTE,
        ("Wave587", "CScriptObjectCode", "full vtable boundary remains unproven", "CMissionScriptObjectCode__CMissionScriptObjectCode"),
        failures,
    )
    require_doc_tokens(
        FUNCTION_INDEX,
        (
            "Wave587 CScriptObjectCode hardening",
            "Post-Wave587 queue telemetry is `6093` functions, `3000` commented, `3093` commentless, `1365` exact-undefined signatures, and `1116` `param_N` signatures.",
            "0x00539c80 CMissionScriptObjectCode__CMissionScriptObjectCode",
        ),
        failures,
    )
    require_doc_tokens(
        SCRIPT_OBJECT_DOC,
        (
            "## Wave587 Static Read-Back",
            "CScriptObjectCode core VM tranche",
            "CScriptObjectCode__CallEventDirect",
            "only slot `0x005e4f54[0]` is treated as proven",
        ),
        failures,
    )
    require_doc_tokens(
        GHIDRA_REFERENCE,
        (
            "Wave587 CScriptObjectCode",
            "CScriptObjectCode__CScriptObjectCode",
            "CScriptObjectCode__Run",
            "3000/6093 = 49.24%",
        ),
        failures,
    )
    require_doc_tokens(
        CAMPAIGN,
        (
            "Wave 587: CScriptObjectCode Core VM",
            "post_wave587_scriptobjectcode_verified",
            "strict clean-signature proxy `2954/6093 = 48.48%`",
        ),
        failures,
    )
    require_doc_tokens(BACKLOG, ("0x00538ea0,0x00538ec0,0x00539040", "Wave587"), failures)
    require_doc_tokens(LEDGER, ("Ghidra CScriptObjectCode Wave587", "post_wave587_scriptobjectcode_verified"), failures)
    require_doc_tokens(ATTEMPT_LOG, ("Ghidra CScriptObjectCode Wave587", '"attempt_id":20242'), failures)

    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Return non-zero on failure")
    parser.add_argument("--json", action="store_true", help="Emit JSON summary")
    args = parser.parse_args()

    failures = run_check()
    result = {
        "status": "PASS" if not failures else "FAIL",
        "failureCount": len(failures),
        "failures": failures,
    }
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("Wave587 CScriptObjectCode probe:", result["status"])
        for failure in failures:
            print(f"- {failure}")
    return 1 if args.check and failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
