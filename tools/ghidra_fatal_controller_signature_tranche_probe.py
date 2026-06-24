#!/usr/bin/env python3
"""Validate the saved Ghidra fatal/controller signature/comment/tag tranche."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "fatal-controller-wave327" / "current"

FATAL_TAGS = ["static-reaudit", "fatal-controller-wave327", "fatal-error", "signature-hardened"]
CONTROLLER_TAGS = ["static-reaudit", "fatal-controller-wave327", "controller-system", "signature-hardened"]
SOURCE_PARITY_TAGS = CONTROLLER_TAGS + ["source-parity", "owner-corrected"]
COMPILER_TAGS = CONTROLLER_TAGS + ["compiler-wrapper", "behavior-named"]
INPUT_TAGS = ["static-reaudit", "fatal-controller-wave327", "input-system", "signature-hardened", "owner-corrected"]

TARGETS = {
    "0x0042c750": {
        "name": "FatalError__ExitWithLocalizedPrefix_A",
        "previous": [],
        "signature": ["void", "__stdcall", "FatalError__ExitWithLocalizedPrefix_A", "char * message", "int callerContext"],
        "comment": ["localized fatal-error message", "string id 0xcc", "second caller context/status", "remain unproven"],
        "tags": FATAL_TAGS,
        "decompile": ["Localization__GetStringById(0xcc)", "FatalError__ExitProcess"],
        "instruction": ["0x0042c800", "RET", "0x8"],
    },
    "0x0042d0b0": {
        "name": "FatalError__ExitWithLocalizedPrefix_B",
        "previous": [],
        "signature": ["void", "__stdcall", "FatalError__ExitWithLocalizedPrefix_B", "char * message"],
        "comment": ["single-argument localized fatal wrapper", "mesh/resource", "FatalError__ExitProcess", "remain unproven"],
        "tags": FATAL_TAGS,
        "decompile": ["Localization__GetStringById(0xcc)", "FatalError__ExitProcess"],
        "instruction": ["0x0042d160", "RET", "0x4"],
    },
    "0x0042d780": {
        "name": "CController__scalar_deleting_dtor",
        "previous": ["CController__VFunc_00_0042d780"],
        "signature": ["void *", "__thiscall", "CController__scalar_deleting_dtor", "void * this", "uint flags"],
        "comment": ["scalar deleting destructor", "CController__dtor", "OID__FreeObject", "not a gameplay virtual behavior"],
        "tags": COMPILER_TAGS,
        "decompile": ["CController__dtor(this)", "OID__FreeObject(this)"],
        "instruction": ["0x0042d79d", "RET", "0x4"],
    },
    "0x0042d7d0": {
        "name": "CController__SetNonInteractiveSection",
        "previous": ["CFrontEnd__SetLoadingTransitionGate"],
        "signature": ["void", "__cdecl", "CController__SetNonInteractiveSection", "bool nonInteractive"],
        "comment": ["CController::SetNonInteractiveSection", "inactivity timer", "attract-mode", "remain unproven"],
        "tags": SOURCE_PARITY_TAGS,
        "decompile": ["PLATFORM__GetSysTimeFloat", "DAT_0066e94c"],
        "instruction": ["0x0042d80e", "RET"],
    },
    "0x0042da00": {
        "name": "Input__UpdateCursorCenterWithWindowScale",
        "previous": ["CGame__UpdateCursorCenterWithWindowScale"],
        "signature": ["void", "__cdecl", "Input__UpdateCursorCenterWithWindowScale", "bool recenterNow"],
        "comment": ["cursor-center globals", "PLATFORM window dimensions", "dev mode", "remain unproven"],
        "tags": INPUT_TAGS,
        "decompile": ["PLATFORM__GetWindowWidth", "PLATFORM__GetWindowHeight", "DAT_0089bda8", "DAT_0089bda4"],
        "instruction": ["0x0042db0f", "RET"],
    },
    "0x0042e3d0": {
        "name": "CController__GetMappedInputValue",
        "previous": [],
        "signature": ["float", "__thiscall", "CController__GetMappedInputValue", "void * this", "int padNumber", "int inputCode"],
        "comment": ["CController__DoMappings", "Negative input codes", "non-negative codes", "remain unproven"],
        "tags": CONTROLLER_TAGS,
        "decompile": ["switch(inputCode)", "padNumber", "return 1.0"],
        "instruction": ["0x0042e491", "RET", "0x8"],
    },
    "0x0042e750": {
        "name": "CController__SetVibration",
        "previous": ["CGame__DispatchVibrationWithCareerGate"],
        "signature": ["void", "__thiscall", "CController__SetVibration", "void * this", "float inValue", "int playerIndex"],
        "comment": ["CController::SetVibration", "GAME_STATE_PLAYING", "CAREER vibration option", "remain unproven"],
        "tags": SOURCE_PARITY_TAGS,
        "decompile": ["CAREER_mVibration_P1", "DeviceSetVibration", "inValue"],
        "instruction": ["0x0042e78b", "RET", "0x8"],
    },
}

EXPECTED_DRY = {"updated": 0, "skipped": 7, "renamed": 0, "missing": 0, "bad": 0}
EXPECTED_APPLY = {"updated": 7, "skipped": 0, "renamed": 4, "missing": 0, "bad": 0}
EXPECTED_QUEUE = {
    "totalFunctions": 5884,
    "commentlessFunctionCount": 5088,
    "undefinedSignatureCount": 1989,
    "paramSignatureCount": 2269,
}

DEFAULT_DRY = BASE / "fatal_controller_signature_tranche_dry.log"
DEFAULT_APPLY = BASE / "fatal_controller_signature_tranche_apply.log"
DEFAULT_METADATA = BASE / "metadata_final.tsv"
DEFAULT_INDEX = BASE / "decompile_final" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_final"
DEFAULT_XREFS = BASE / "xrefs_final.tsv"
DEFAULT_INSTRUCTIONS = BASE / "instructions_final.tsv"
DEFAULT_TAGS = BASE / "tags_final.tsv"
DEFAULT_QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
DEFAULT_OUT = BASE / "fatal-controller-signature-tranche.json"

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "source identity proven",
    "exact source identity proven",
    "fully re'ed",
    "100% re",
)


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


def parse_summary(log_text: str) -> dict[str, int]:
    match = re.search(r"updated=(\d+)\s+skipped=(\d+)\s+renamed=(\d+)\s+missing=(\d+)\s+bad=(\d+)", log_text)
    if not match:
        return {"updated": -1, "skipped": -1, "renamed": -1, "missing": -1, "bad": -1}
    return {
        "updated": int(match.group(1)),
        "skipped": int(match.group(2)),
        "renamed": int(match.group(3)),
        "missing": int(match.group(4)),
        "bad": int(match.group(5)),
    }


def queue_signal(report: dict[str, object], name: str) -> int | None:
    if name in report and isinstance(report[name], int):
        return int(report[name])
    signals = report.get("qualitySignals", {})
    if isinstance(signals, dict) and isinstance(signals.get(name), int):
        return int(signals[name])
    return None


def build_report(
    *,
    dry_log_path: Path = DEFAULT_DRY,
    apply_log_path: Path = DEFAULT_APPLY,
    metadata_path: Path = DEFAULT_METADATA,
    decompile_index_path: Path = DEFAULT_INDEX,
    decompile_dir: Path = DEFAULT_DECOMPILE_DIR,
    xrefs_path: Path = DEFAULT_XREFS,
    instructions_path: Path = DEFAULT_INSTRUCTIONS,
    tags_path: Path = DEFAULT_TAGS,
    queue_json_path: Path = DEFAULT_QUEUE_JSON,
) -> dict[str, object]:
    dry_log_path = resolve(dry_log_path)
    apply_log_path = resolve(apply_log_path)
    metadata_path = resolve(metadata_path)
    decompile_index_path = resolve(decompile_index_path)
    decompile_dir = resolve(decompile_dir)
    xrefs_path = resolve(xrefs_path)
    instructions_path = resolve(instructions_path)
    tags_path = resolve(tags_path)
    queue_json_path = resolve(queue_json_path)

    failures: list[str] = []
    for path, label in (
        (dry_log_path, "dry_log"),
        (apply_log_path, "apply_log"),
        (metadata_path, "metadata"),
        (decompile_index_path, "decompile_index"),
        (xrefs_path, "xrefs"),
        (instructions_path, "instructions"),
        (tags_path, "tags"),
        (queue_json_path, "queue_json"),
    ):
        if not path.is_file():
            failures.append(f"missing {label}: {relative(path)}")

    dry_summary = parse_summary(read_text(dry_log_path))
    apply_summary = parse_summary(read_text(apply_log_path))
    if dry_summary != EXPECTED_DRY:
        failures.append(f"dry summary mismatch: {dry_summary} != {EXPECTED_DRY}")
    if apply_summary != EXPECTED_APPLY:
        failures.append(f"apply summary mismatch: {apply_summary} != {EXPECTED_APPLY}")

    metadata = read_tsv(metadata_path)
    index = read_tsv(decompile_index_path)
    xrefs = read_tsv(xrefs_path)
    instructions = read_tsv(instructions_path)
    tag_rows = read_tsv(tags_path)
    queue = read_json(queue_json_path)

    renamed_count = 0
    source_parity_count = 0
    for address, expected in TARGETS.items():
        meta_row = row_by_address(metadata, address)
        index_row = row_by_address(index, address)
        tag_row = row_by_address(tag_rows, address)
        decompile = decompile_text_for(decompile_dir, address)
        if meta_row is None:
            failures.append(f"{address}: missing metadata row")
            continue
        if index_row is None:
            failures.append(f"{address}: missing decompile index row")
            continue
        if tag_row is None:
            failures.append(f"{address}: missing tag row")
            continue

        if meta_row.get("name") != expected["name"]:
            failures.append(f"{address}: metadata name {meta_row.get('name')} != {expected['name']}")
        if index_row.get("name") != expected["name"]:
            failures.append(f"{address}: decompile index name {index_row.get('name')} != {expected['name']}")
        for prior in expected.get("previous", []):
            if prior and (prior in meta_row.get("name", "") or prior in decompile):
                failures.append(f"{address}: stale previous name still visible: {prior}")
        signature = meta_row.get("signature", "")
        for token in expected["signature"]:
            if not token_present(signature, token):
                failures.append(f"{address}: signature missing token {token!r}: {signature}")
        if "param_" in signature:
            failures.append(f"{address}: signature still contains param_N: {signature}")
        comment = meta_row.get("comment", "")
        for token in expected["comment"]:
            if not token_present(comment, token):
                failures.append(f"{address}: comment missing token {token!r}")
        for token in OVERCLAIM_TOKENS:
            if token_present(comment, token):
                failures.append(f"{address}: overclaim token in comment: {token}")
        tags = parse_tags(tag_row.get("tags", ""))
        for tag in expected["tags"]:
            if tag not in tags:
                failures.append(f"{address}: missing tag {tag}")
        for token in expected["decompile"]:
            if not token_present(decompile, token):
                failures.append(f"{address}: decompile missing token {token!r}")
        instr_rows = rows_for_address(instructions, address, "target_addr")
        instr_blob = "\n".join("\t".join(row.values()) for row in instr_rows)
        for token in expected["instruction"]:
            if not token_present(instr_blob, token):
                failures.append(f"{address}: instruction export missing token {token!r}")
        if expected.get("previous"):
            renamed_count += 1
        if "source-parity" in expected["tags"]:
            source_parity_count += 1

    for name, expected_value in EXPECTED_QUEUE.items():
        observed = queue_signal(queue, name)
        if observed != expected_value:
            failures.append(f"queue {name} {observed} != {expected_value}")

    status = "PASS" if not failures else "FAIL"
    return {
        "schema": "ghidra-fatal-controller-signature-tranche.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "targetCount": len(TARGETS),
        "renamedTargetCount": renamed_count,
        "sourceParityTargetCount": source_parity_count,
        "drySummary": dry_summary,
        "applySummary": apply_summary,
        "xrefRowCount": len(xrefs),
        "instructionRowCount": len(instructions),
        "inputs": {
            "dryLog": relative(dry_log_path),
            "applyLog": relative(apply_log_path),
            "metadata": relative(metadata_path),
            "decompileIndex": relative(decompile_index_path),
            "decompileDir": relative(decompile_dir),
            "xrefs": relative(xrefs_path),
            "instructions": relative(instructions_path),
            "tags": relative(tags_path),
            "queueJson": relative(queue_json_path),
        },
        "failures": failures,
        "whatIsProven": [
            "The selected fatal/controller tranche has saved Ghidra names, signatures, comments, and tags matching the read-back exports.",
            "CController__SetNonInteractiveSection and CController__SetVibration are owner-corrected/source-parity labels for the observed retail bodies.",
            "CController__scalar_deleting_dtor is a compiler destructor wrapper, not a gameplay virtual body.",
        ],
        "notProven": [
            "This does not prove runtime fatal, input, inactivity, cursor, or vibration behavior.",
            "This does not prove exact source identity for all selected functions or concrete class/global layouts.",
            "This does not launch, patch, or mutate BEA.exe or the installed game.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="exit non-zero unless the report passes")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--dry-log", type=Path, default=DEFAULT_DRY)
    parser.add_argument("--apply-log", type=Path, default=DEFAULT_APPLY)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--decompile-index", type=Path, default=DEFAULT_INDEX)
    parser.add_argument("--decompile-dir", type=Path, default=DEFAULT_DECOMPILE_DIR)
    parser.add_argument("--xrefs", type=Path, default=DEFAULT_XREFS)
    parser.add_argument("--instructions", type=Path, default=DEFAULT_INSTRUCTIONS)
    parser.add_argument("--tags", type=Path, default=DEFAULT_TAGS)
    parser.add_argument("--queue-json", type=Path, default=DEFAULT_QUEUE_JSON)
    args = parser.parse_args()

    report = build_report(
        dry_log_path=args.dry_log,
        apply_log_path=args.apply_log,
        metadata_path=args.metadata,
        decompile_index_path=args.decompile_index,
        decompile_dir=args.decompile_dir,
        xrefs_path=args.xrefs,
        instructions_path=args.instructions,
        tags_path=args.tags,
        queue_json_path=args.queue_json,
    )
    out = resolve(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("Ghidra fatal/controller signature tranche probe")
    print(f"Status: {report['status']}")
    print(f"Targets: {report['targetCount']}")
    print(f"Renamed targets: {report['renamedTargetCount']}")
    print(f"Source-parity targets: {report['sourceParityTargetCount']}")
    print(f"Xref rows: {report['xrefRowCount']}")
    print(f"Instruction rows: {report['instructionRowCount']}")
    print(f"Output: {relative(out)}")
    if report["failures"]:
        print("Failures:")
        for failure in report["failures"]:
            print(f"- {failure}")
    return 1 if args.check and report["status"] != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
