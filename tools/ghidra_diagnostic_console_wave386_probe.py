#!/usr/bin/env python3
"""Validate the Wave386 diagnostic/fatal/console Ghidra correction tranche."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "diagnostic-console-wave386" / "current"

COMMON_TAGS = {"static-reaudit", "diagnostic-console-wave386", "retail-binary-evidence"}


def target(
    name: str,
    signature: str,
    comment_tokens: list[str],
    decompile_tokens: list[str],
    tags: list[str],
    min_xrefs: int,
) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "commentTokens": comment_tokens,
        "decompileTokens": decompile_tokens,
        "tags": sorted(COMMON_TAGS | set(tags)),
        "minXrefs": min_xrefs,
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x0040c640": target(
        "DebugTrace",
        "void __cdecl DebugTrace(char * message)",
        [
            "Wave386 diagnostic correction",
            "body is a single RET stub",
            "hundreds of logging callsites",
            "Runtime debug trace output, exact original implementation, and rebuild parity remain unproven",
        ],
        ["DebugTrace", "return;"],
        ["diagnostic-trace", "ret-stub", "comment-hardened", "signature-hardened"],
        300,
    ),
    "0x0042cfa0": target(
        "FatalError__ExitProcess",
        "noreturn void __cdecl FatalError__ExitProcess(char * message, int code)",
        [
            "Wave386 fatal-error correction",
            "prints the supplied message/code through CConsole__Printf",
            "shuts down mouse input",
            "ends through ExitProcess",
            "Runtime fatal behavior, exact UI/error presentation, and rebuild parity remain unproven",
        ],
        ["CConsole__Printf", "PlatformInput__ShutdownMouse", "Localization__GetStringById(0xcb)", "ExitProcess(1)"],
        ["fatal-error", "process-exit", "no-return", "comment-hardened", "signature-hardened"],
        3,
    ),
    "0x0042d080": target(
        "FatalError_LocalizedStringId",
        "void __stdcall FatalError_LocalizedStringId(char gate, int stringId, int code)",
        [
            "Wave386 fatal-error correction",
            "guard byte is zero",
            "loads a localized string",
            "forwards the message/code pair to FatalError__ExitProcess",
            "Runtime fatal behavior, caller intent for the guard byte, and rebuild parity remain unproven",
        ],
        ["if (gate == '\\0')", "Localization__GetStringById(stringId)", "FatalError__ExitProcess"],
        ["fatal-error", "localized-string", "guard-gated", "comment-hardened", "signature-hardened"],
        40,
    ),
    "0x00441740": target(
        "CConsole__Printf",
        "void __cdecl CConsole__Printf(void * console, char * format, ...)",
        [
            "Wave386 console correction",
            "variadic console print sink",
            "mirrors the formatted text and newline through DebugTrace",
            "advances the 30-slot status/history ring",
            "Runtime console output, exact layout names, buffer safety, and rebuild parity remain unproven",
        ],
        ["vsprintf", "DebugTrace", "fprintf", "StrCopyN", "DAT_00672fd0"],
        ["console-system", "variadic", "status-history", "comment-hardened", "signature-hardened"],
        300,
    ),
    "0x004418a0": target(
        "CConsole__PrintfNoNewline",
        "void __cdecl CConsole__PrintfNoNewline(void * console, char * format, ...)",
        [
            "Wave386 console correction",
            "variadic no-newline console print sink",
            "writes the formatted text without the DebugTrace newline mirror",
            "advances the same 30-slot status/history ring",
            "Runtime console output, exact layout names, buffer safety, and rebuild parity remain unproven",
        ],
        ["vsprintf", "fprintf", "StrCopyN", "DAT_00672fd0"],
        ["console-system", "variadic", "status-history", "no-newline", "comment-hardened", "signature-hardened"],
        1,
    ),
}

INSTRUCTION_EVIDENCE = [
    ("0x0040c640", "0x0040c640", "RET", "", "c3"),
    ("0x0042cfa0", "0x0042cfc2", "CALL", "0x00441740", "e8 79 47 01 00"),
    ("0x0042cfa0", "0x0042cfca", "CALL", "0x0042d3b0", "e8 e1 03 00 00"),
    ("0x0042cfa0", "0x0042d064", "CALL", "dword ptr [0x005d81e8]", "ff 15 e8 81 5d 00"),
    ("0x0042d080", "0x0042d0a1", "CALL", "0x0042cfa0", "e8 fa fe ff ff"),
    ("0x0042d080", "0x0042d0a9", "RET", "0xc", "c2 0c 00"),
    ("0x00441740", "0x0044175a", "CALL", "0x0055e38c", "e8 2d cc 11 00"),
    ("0x00441740", "0x00441767", "CALL", "0x0040c640", "e8 d4 ae fc ff"),
    ("0x00441740", "0x0044185c", "CALL", "0x004d6240", "e8 df 49 09 00"),
    ("0x004418a0", "0x004418a0", "SUB", "ESP, 0x100", "81 ec 00 01 00 00"),
    ("0x004418a0", "0x004418cd", "CALL", "0x0055e490", "e8 be cb 11 00"),
]

EXPECTED_DRY = {"updated": 0, "skipped": 5, "renamed": 0, "varargs": 0, "noreturn": 0, "missing": 0, "bad": 0}
EXPECTED_APPLY = {"updated": 5, "skipped": 0, "renamed": 0, "varargs": 2, "noreturn": 1, "missing": 0, "bad": 0}

DEFAULT_DRY = BASE / "diagnostic_console_wave386_dry.log"
DEFAULT_APPLY = BASE / "diagnostic_console_wave386_apply.log"
DEFAULT_METADATA = BASE / "metadata_after.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_after"
DEFAULT_XREFS = BASE / "xrefs_after.tsv"
DEFAULT_INSTRUCTIONS = BASE / "instructions_after.tsv"
DEFAULT_TAGS = BASE / "tags_after.tsv"
DEFAULT_OUT = BASE / "diagnostic-console-wave386.json"

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "runtime proof",
    "source identity proven",
    "fully re'ed",
    "100% re",
    "rebuild parity proven",
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


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        for key in ("address", "target_addr", "instruction_addr", "function_entry", "target_raw"):
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
    match = re.search(
        r"updated=(\d+)\s+skipped=(\d+)\s+renamed=(\d+)\s+varargs=(\d+)\s+noreturn=(\d+)\s+missing=(\d+)\s+bad=(\d+)",
        log_text,
    )
    if not match:
        return {"updated": -1, "skipped": -1, "renamed": -1, "varargs": -1, "noreturn": -1, "missing": -1, "bad": -1}
    return {
        "updated": int(match.group(1)),
        "skipped": int(match.group(2)),
        "renamed": int(match.group(3)),
        "varargs": int(match.group(4)),
        "noreturn": int(match.group(5)),
        "missing": int(match.group(6)),
        "bad": int(match.group(7)),
    }


def instruction_hit(rows: list[dict[str, str]], target: str, instruction_addr: str, mnemonic: str, operands: str, bytes_: str) -> bool:
    target_norm = normalize_address(target)
    instruction_norm = normalize_address(instruction_addr)
    return any(
        (
            normalize_address(row.get("target_addr", "")) == target_norm
            or normalize_address(row.get("function_entry", "")) == target_norm
        )
        and normalize_address(row.get("instruction_addr", "")) == instruction_norm
        and row.get("mnemonic", "") == mnemonic
        and row.get("operands", "") == operands
        and row.get("bytes", "") == bytes_
        for row in rows
    )


def build_report(
    *,
    dry_log_path: Path = DEFAULT_DRY,
    apply_log_path: Path = DEFAULT_APPLY,
    metadata_path: Path = DEFAULT_METADATA,
    decompile_dir: Path = DEFAULT_DECOMPILE_DIR,
    xrefs_path: Path = DEFAULT_XREFS,
    instructions_path: Path = DEFAULT_INSTRUCTIONS,
    tags_path: Path = DEFAULT_TAGS,
) -> dict[str, object]:
    dry_log_path = resolve(dry_log_path)
    apply_log_path = resolve(apply_log_path)
    metadata_path = resolve(metadata_path)
    decompile_dir = resolve(decompile_dir)
    xrefs_path = resolve(xrefs_path)
    instructions_path = resolve(instructions_path)
    tags_path = resolve(tags_path)

    failures: list[str] = []
    for path, label in (
        (dry_log_path, "dry_log"),
        (apply_log_path, "apply_log"),
        (metadata_path, "metadata"),
        (xrefs_path, "xrefs"),
        (instructions_path, "instructions"),
        (tags_path, "tags"),
    ):
        if not path.is_file():
            failures.append(f"missing {label}: {relative(path)}")
    if not decompile_dir.is_dir():
        failures.append(f"missing decompile_dir: {relative(decompile_dir)}")

    dry_log = read_text(dry_log_path)
    apply_log = read_text(apply_log_path)
    dry_summary = parse_summary(dry_log)
    apply_summary = parse_summary(apply_log)
    if dry_summary != EXPECTED_DRY:
        failures.append(f"dry summary mismatch: {dry_summary} != {EXPECTED_DRY}")
    if apply_summary != EXPECTED_APPLY:
        failures.append(f"apply summary mismatch: {apply_summary} != {EXPECTED_APPLY}")
    if "REPORT: Save succeeded" not in apply_log:
        failures.append("apply log missing save-success marker")
    if "varArgs=true" not in apply_log:
        failures.append("apply log missing varargs read-back")
    if "noReturn=true" not in apply_log:
        failures.append("apply log missing no-return read-back")

    metadata_rows = read_tsv(metadata_path)
    xref_rows = read_tsv(xrefs_path)
    instruction_rows = read_tsv(instructions_path)
    tag_rows = read_tsv(tags_path)

    instruction_hits = 0
    for target_addr, instruction_addr, mnemonic, operands, bytes_ in INSTRUCTION_EVIDENCE:
        if instruction_hit(instruction_rows, target_addr, instruction_addr, mnemonic, operands, bytes_):
            instruction_hits += 1
        else:
            failures.append(f"missing instruction evidence {target_addr} {instruction_addr} {mnemonic} {operands} {bytes_}")

    for address, expected in TARGETS.items():
        row = row_by_address(metadata_rows, address)
        if row is None:
            failures.append(f"missing metadata row for {address}")
            continue
        if row.get("name") != expected["name"]:
            failures.append(f"{address} name mismatch: {row.get('name')} != {expected['name']}")
        if row.get("signature") != expected["signature"]:
            failures.append(f"{address} signature mismatch: {row.get('signature')} != {expected['signature']}")

        comment = row.get("comment", "")
        for token in expected["commentTokens"]:  # type: ignore[index]
            if not token_present(comment, str(token)):
                failures.append(f"{address} missing comment token: {token}")
        for token in OVERCLAIM_TOKENS:
            if token_present(comment, token):
                failures.append(f"{address} comment overclaim token: {token}")

        decompile_text = decompile_text_for(decompile_dir, address)
        for token in expected["decompileTokens"]:  # type: ignore[index]
            if not token_present(decompile_text, str(token)):
                failures.append(f"{address} missing decompile token: {token}")

        tag_row = row_by_address(tag_rows, address)
        if tag_row is None:
            failures.append(f"missing tag row for {address}")
        else:
            actual_tags = parse_tags(tag_row.get("tags", ""))
            for tag in expected["tags"]:  # type: ignore[index]
                if str(tag) not in actual_tags:
                    failures.append(f"{address} missing tag: {tag}")

        xref_count = len(rows_for_address(xref_rows, address, "target_addr"))
        min_xrefs = int(expected["minXrefs"])
        if xref_count < min_xrefs:
            failures.append(f"{address} xref count too low: {xref_count} < {min_xrefs}")

    status = "PASS" if not failures else "FAIL"
    return {
        "schema": "ghidra-diagnostic-console-wave386.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "failures": failures,
        "targetCount": len(TARGETS),
        "instructionEvidenceHits": instruction_hits,
        "xrefsByTarget": {
            address: len(rows_for_address(xref_rows, address, "target_addr"))
            for address in TARGETS
        },
        "inputs": {
            "dryLog": relative(dry_log_path),
            "applyLog": relative(apply_log_path),
            "metadata": relative(metadata_path),
            "decompileDir": relative(decompile_dir),
            "xrefs": relative(xrefs_path),
            "instructions": relative(instructions_path),
            "tags": relative(tags_path),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--dry-log", type=Path, default=DEFAULT_DRY)
    parser.add_argument("--apply-log", type=Path, default=DEFAULT_APPLY)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--decompile-dir", type=Path, default=DEFAULT_DECOMPILE_DIR)
    parser.add_argument("--xrefs", type=Path, default=DEFAULT_XREFS)
    parser.add_argument("--instructions", type=Path, default=DEFAULT_INSTRUCTIONS)
    parser.add_argument("--tags", type=Path, default=DEFAULT_TAGS)
    args = parser.parse_args()

    report = build_report(
        dry_log_path=args.dry_log,
        apply_log_path=args.apply_log,
        metadata_path=args.metadata,
        decompile_dir=args.decompile_dir,
        xrefs_path=args.xrefs,
        instructions_path=args.instructions,
        tags_path=args.tags,
    )
    out_path = resolve(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"status={report['status']} targets={report['targetCount']} instruction_hits={report['instructionEvidenceHits']}")
    if args.check and report["status"] != "PASS":
        for failure in report["failures"]:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
