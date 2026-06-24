#!/usr/bin/env python3
"""Validate the saved Ghidra Console signature/comment/tag tranche."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "console-wave326" / "current"

COMMON_TAGS = ["static-reaudit", "console-wave326", "console-system", "signature-hardened"]
MENU_TAGS = COMMON_TAGS + ["console-menu"]
BEHAVIOR_TAGS = MENU_TAGS + ["behavior-named"]

TARGETS = {
    "0x00429bc0": {
        "name": "CConsole__Init",
        "signature": "void __fastcall CConsole__Init(void * this)",
        "comment": ["command/variable list heads", "line/history buffers", "startup console text", "remain unproven"],
        "tags": COMMON_TAGS,
    },
    "0x00429ef0": {
        "name": "CConsole__RegisterBuiltinCommands",
        "signature": "void __fastcall CConsole__RegisterBuiltinCommands(void * this)",
        "comment": ["built-in console commands", "cg_consolealpha", "callback identities", "remain unproven"],
        "tags": COMMON_TAGS,
    },
    "0x0042a410": {
        "name": "CConsole__ResetLayoutForWindowHeight",
        "signature": "void __fastcall CConsole__ResetLayoutForWindowHeight(void * this)",
        "comment": ["PLATFORM__GetWindowHeight", "layout metrics", "loading-screen stride", "remain unproven"],
        "tags": COMMON_TAGS,
    },
    "0x0042a4f0": {
        "name": "CConsole__ExecuteBufferedCommandSlot",
        "signature": "void __thiscall CConsole__ExecuteBufferedCommandSlot(void * this, char slotIndex, int bankSelector)",
        "comment": ["buffered command line slot", "this+0x23bc", "CConsole__ExecuteCommandLine", "remain unproven"],
        "tags": COMMON_TAGS,
    },
    "0x0042a540": {
        "name": "CConsoleVar__GetTypeName",
        "signature": "void __stdcall CConsoleVar__GetTypeName(void * var, char * outTypeName)",
        "comment": ["CConsoleVar type enum", "printable type label", "unknown fallback", "remain unproven"],
        "tags": COMMON_TAGS,
    },
    "0x0042a5f0": {
        "name": "CConsoleVar__FormatValueToString",
        "signature": "void __stdcall CConsoleVar__FormatValueToString(void * var, char * outValueText)",
        "comment": ["formats a CConsoleVar value", "value pointer", "boolean True/False", "remain unproven"],
        "tags": COMMON_TAGS,
    },
    "0x0042a770": {
        "name": "CConsole__FindCommandByName",
        "signature": "char * __thiscall CConsole__FindCommandByName(void * this, char * commandName)",
        "comment": ["command list", "this+0x2394", "case-insensitive", "remain unproven"],
        "tags": COMMON_TAGS,
    },
    "0x0042ae70": {
        "name": "CConsole__ShutdownAndFreeAllLists",
        "signature": "void __fastcall CConsole__ShutdownAndFreeAllLists(void * this)",
        "comment": ["frees command and variable linked lists", "aux menu/list pointers", "teardown", "remain unproven"],
        "tags": COMMON_TAGS,
    },
    "0x0042af20": {
        "name": "CConsole__ClearCommandAndVariableLists",
        "signature": "void __fastcall CConsole__ClearCommandAndVariableLists(void * this)",
        "comment": ["Console command and variable linked lists", "leaving the auxiliary menu/list pointers", "remain unproven"],
        "tags": COMMON_TAGS,
    },
    "0x0042af80": {
        "name": "CConsole__RegisterCommand",
        "signature": "void __thiscall CConsole__RegisterCommand(void * this, char * name, char * description, void * callback, char flags)",
        "comment": ["CConsoleCmd", "0xac", "callback at +0xa0", "remain unproven"],
        "tags": COMMON_TAGS,
    },
    "0x0042b040": {
        "name": "CConsole__RegisterVariable",
        "signature": "void __thiscall CConsole__RegisterVariable(void * this, char * name, char * description, int varType, void * valuePtr, char flags1, char flags2)",
        "comment": ["CConsoleVar", "0xb0", "type/value pointer", "remain unproven"],
        "tags": COMMON_TAGS,
    },
    "0x0042ba90": {
        "name": "CConsole__MenuUp",
        "signature": "bool __fastcall CConsole__MenuUp(void * this)",
        "comment": ["menu active flag", "selection index", "clamp", "remain unproven"],
        "tags": MENU_TAGS,
    },
    "0x0042bac0": {
        "name": "CConsole__MenuDown",
        "signature": "bool __fastcall CConsole__MenuDown(void * this)",
        "comment": ["menu active flag", "selection index", "child/action count", "remain unproven"],
        "tags": MENU_TAGS,
    },
    "0x0042bb30": {
        "name": "CConsole__MenuSelect",
        "signature": "bool __fastcall CConsole__MenuSelect(void * this)",
        "comment": ["current menu node", "selected child node", "vtable slot 0x0c", "remain unproven"],
        "tags": MENU_TAGS,
    },
    "0x0042c420": {
        "name": "CConsoleMenu__ctor_like_0042c420",
        "signature": "void * __fastcall CConsoleMenu__ctor_like_0042c420(void * this)",
        "comment": ["menu node vtable", "first-child", "parent", "remain unproven"],
        "tags": MENU_TAGS,
    },
    "0x0042c440": {
        "name": "CConsoleMenu__LinkChildAtHead",
        "signature": "void __thiscall CConsoleMenu__LinkChildAtHead(void * this, void * child)",
        "comment": ["links a child menu node", "parent pointer", "child count", "remain unproven"],
        "tags": BEHAVIOR_TAGS,
    },
}

EXPECTED_QUEUE = {
    "totalFunctions": 5884,
    "commentlessFunctionCount": 5095,
    "undefinedSignatureCount": 1989,
    "paramSignatureCount": 2276,
}

DEFAULT_METADATA_FINAL = BASE / "metadata_final.tsv"
DEFAULT_INDEX = BASE / "decompile_final" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_final"
DEFAULT_XREFS = BASE / "xrefs_final.tsv"
DEFAULT_INSTRUCTIONS = BASE / "instructions_final.tsv"
DEFAULT_TAGS = BASE / "tags_final.tsv"
DEFAULT_QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
DEFAULT_OUT = BASE / "console-signature-tranche.json"

OVERCLAIM_TOKENS = ("runtime behavior proven", "source identity proven", "fully re'ed", "100% re", "exact source identity proven")


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if not value or value.startswith("<"):
        return value
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def compact(value: str) -> str:
    return "".join(value.lower().split())


def token_present(text: str, token: str) -> bool:
    return compact(token) in compact(text)


def unescape(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def read_json(path: Path) -> dict[str, object]:
    if not path.is_file():
        return {}
    return json.loads(read_text(path))


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        for key in ("address", "target_addr", "from_addr", "from_function_addr", "function_entry", "target_raw", "instruction_addr"):
            if key in row and row[key]:
                row[key] = normalize_address(row[key])
        if "comment" in row:
            row["comment"] = unescape(row["comment"])
    return rows


def row_by_address(rows: list[dict[str, str]], address: str, key: str = "address") -> dict[str, str] | None:
    wanted = normalize_address(address)
    for row in rows:
        if normalize_address(row.get(key, "")) == wanted:
            return row
    return None


def rows_for_address(rows: list[dict[str, str]], address: str, key: str) -> list[dict[str, str]]:
    wanted = normalize_address(address)
    return [row for row in rows if normalize_address(row.get(key, "")) == wanted]


def decompile_text_for(directory: Path, address: str) -> str:
    if not directory.is_dir():
        return ""
    matches = sorted(directory.glob(f"{normalize_address(address)[2:]}_*.c"))
    if not matches:
        return ""
    return read_text(matches[0])


def parse_tags(value: str) -> set[str]:
    return {part.strip() for part in value.split(";") if part.strip()}


def queue_signal(report: dict[str, object], name: str) -> int | None:
    if name in report and isinstance(report[name], int):
        return int(report[name])
    signals = report.get("qualitySignals", {})
    if isinstance(signals, dict) and isinstance(signals.get(name), int):
        return int(signals[name])
    return None


def build_report(
    *,
    metadata_final_path: Path = DEFAULT_METADATA_FINAL,
    decompile_index_path: Path = DEFAULT_INDEX,
    decompile_dir: Path = DEFAULT_DECOMPILE_DIR,
    xrefs_path: Path = DEFAULT_XREFS,
    instructions_path: Path = DEFAULT_INSTRUCTIONS,
    tags_path: Path = DEFAULT_TAGS,
    queue_json_path: Path = DEFAULT_QUEUE_JSON,
) -> dict[str, object]:
    metadata_final_path = resolve(metadata_final_path)
    decompile_index_path = resolve(decompile_index_path)
    decompile_dir = resolve(decompile_dir)
    xrefs_path = resolve(xrefs_path)
    instructions_path = resolve(instructions_path)
    tags_path = resolve(tags_path)
    queue_json_path = resolve(queue_json_path)

    failures: list[str] = []
    for path, label in (
        (metadata_final_path, "metadata_final"),
        (decompile_index_path, "decompile_index"),
        (xrefs_path, "xrefs"),
        (instructions_path, "instructions"),
        (tags_path, "tags"),
        (queue_json_path, "queue_json"),
    ):
        if not path.is_file():
            failures.append(f"missing {label}: {relative(path)}")

    final_rows = read_tsv(metadata_final_path)
    index_rows = read_tsv(decompile_index_path)
    xref_rows = read_tsv(xrefs_path)
    instruction_rows = read_tsv(instructions_path)
    tag_rows = read_tsv(tags_path)
    queue = read_json(queue_json_path)

    target_summaries: list[dict[str, object]] = []
    renamed_targets = 0
    undefined_fixed_targets = 0
    for address, expected in TARGETS.items():
        final = row_by_address(final_rows, address)
        index = row_by_address(index_rows, address)
        tag_row = row_by_address(tag_rows, address)
        decompile_text = decompile_text_for(decompile_dir, address)
        xrefs = rows_for_address(xref_rows, address, "target_addr")
        instructions = rows_for_address(instruction_rows, address, "target_addr")

        if final is None:
            failures.append(f"{address} missing from metadata_final")
            continue
        if index is None:
            failures.append(f"{address} missing from decompile index")
        if tag_row is None:
            failures.append(f"{address} missing from tags")
            tags = set()
        else:
            tags = parse_tags(tag_row.get("tags", ""))

        name = final.get("name", "")
        signature = final.get("signature", "")
        comment = final.get("comment", "")

        if name != expected["name"]:
            failures.append(f"{address} name mismatch: {name} != {expected['name']}")
        if signature != expected["signature"]:
            failures.append(f"{address} signature mismatch: {signature} != {expected['signature']}")
        if "undefined" in signature.lower():
            failures.append(f"{address} still has undefined signature: {signature}")
        for token in expected["comment"]:
            if not token_present(comment, token):
                failures.append(f"{address} comment missing token: {token}")
        for tag in expected["tags"]:
            if tag not in tags:
                failures.append(f"{address} missing tag: {tag}")
        for token in OVERCLAIM_TOKENS:
            if token_present(comment, token) or token_present(decompile_text, token):
                failures.append(f"{address} overclaim token present: {token}")
        if not decompile_text:
            failures.append(f"{address} missing decompile text")
        elif expected["name"] not in decompile_text:
            failures.append(f"{address} decompile missing expected name {expected['name']}")
        if len(instructions) == 0:
            failures.append(f"{address} has no instruction rows")
        if len(xrefs) == 0:
            failures.append(f"{address} has no xref rows")

        if address == "0x0042c440":
            if name == "VFuncSlot_05_0042c440":
                failures.append("0x0042c440 still has generic VFuncSlot name")
            if len(xrefs) < 7:
                failures.append(f"0x0042c440 expected at least 7 xrefs, saw {len(xrefs)}")
            if not any(row.get("ref_type") == "DATA" for row in xrefs):
                failures.append("0x0042c440 missing vtable DATA xrefs")
            renamed_targets += 1

        if address in {"0x00429bc0", "0x00429ef0", "0x0042af80", "0x0042b040"}:
            undefined_fixed_targets += 1

        target_summaries.append(
            {
                "address": address,
                "name": name,
                "signature": signature,
                "tagCount": len(tags),
                "xrefCount": len(xrefs),
                "instructionCount": len(instructions),
            }
        )

    if queue.get("status") != "PASS":
        failures.append(f"queue status is not PASS: {queue.get('status')}")
    for key, expected_value in EXPECTED_QUEUE.items():
        actual = queue_signal(queue, key)
        if actual != expected_value:
            failures.append(f"queue {key} mismatch: {actual} != {expected_value}")

    report = {
        "schema": 1,
        "status": "PASS" if not failures else "FAIL",
        "generatedAtUtc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "targetCount": len(TARGETS),
        "renamedTargetCount": renamed_targets,
        "undefinedFixedTargetCount": undefined_fixed_targets,
        "queueTotalFunctions": queue_signal(queue, "totalFunctions"),
        "queueCommentlessFunctions": queue_signal(queue, "commentlessFunctionCount"),
        "queueUndefinedSignatures": queue_signal(queue, "undefinedSignatureCount"),
        "queueParamSignatures": queue_signal(queue, "paramSignatureCount"),
        "targets": target_summaries,
        "failures": failures,
        "inputs": {
            "metadataFinal": relative(metadata_final_path),
            "decompileIndex": relative(decompile_index_path),
            "xrefs": relative(xrefs_path),
            "instructions": relative(instructions_path),
            "tags": relative(tags_path),
            "queue": relative(queue_json_path),
        },
    }
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metadata-final", type=Path, default=DEFAULT_METADATA_FINAL)
    parser.add_argument("--decompile-index", type=Path, default=DEFAULT_INDEX)
    parser.add_argument("--decompile-dir", type=Path, default=DEFAULT_DECOMPILE_DIR)
    parser.add_argument("--xrefs", type=Path, default=DEFAULT_XREFS)
    parser.add_argument("--instructions", type=Path, default=DEFAULT_INSTRUCTIONS)
    parser.add_argument("--tags", type=Path, default=DEFAULT_TAGS)
    parser.add_argument("--queue-json", type=Path, default=DEFAULT_QUEUE_JSON)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--check", action="store_true", help="Return a non-zero exit code if the report fails.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(
        metadata_final_path=args.metadata_final,
        decompile_index_path=args.decompile_index,
        decompile_dir=args.decompile_dir,
        xrefs_path=args.xrefs,
        instructions_path=args.instructions,
        tags_path=args.tags,
        queue_json_path=args.queue_json,
    )
    out_path = resolve(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    if args.check and report["status"] != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
