#!/usr/bin/env python3
"""Validate the Wave402 CFEPDemoMain Ghidra correction tranche."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "fepdemo-wave402" / "current"

COMMON_TAGS = {"static-reaudit", "fepdemo-wave402", "frontend", "retail-binary-evidence"}


def target(
    name: str,
    signature: str,
    comment_tokens: list[str],
    decompile_tokens: list[str],
    instruction_tokens: list[str],
    tags: list[str],
    xref_tokens: list[str],
) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "commentTokens": comment_tokens,
        "decompileTokens": decompile_tokens,
        "instructionTokens": instruction_tokens,
        "tags": sorted(COMMON_TAGS | set(tags)),
        "xrefTokens": xref_tokens,
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x00457ec0": target(
        "CFEPDemoMain__GetMenuType",
        "int __cdecl CFEPDemoMain__GetMenuType(void)",
        [
            "no-argument menu-type getter",
            "returns constant 3",
            "CFEPDemoMain vtable slice",
            "runtime frontend behavior",
            "rebuild parity remain unproven",
        ],
        ["return 3"],
        ["MOV\tEAX, 0x3"],
        ["fepdemo", "menu-type", "signature-corrected", "comment-hardened"],
        ["005db7d0", "005e4a78"],
    ),
    "0x00457ed0": target(
        "CFEPDemoMain__GetActionCount",
        "int __stdcall CFEPDemoMain__GetActionCount(int menu_state)",
        [
            "one stack argument",
            "returns constant 1",
            "demo-menu action count",
            "runtime frontend behavior",
            "rebuild parity remain unproven",
        ],
        ["return 1"],
        ["MOV\tEAX, 0x1", "RET\t0x4"],
        ["fepdemo", "action-count", "signature-corrected", "comment-hardened"],
        ["005db7cc"],
    ),
    "0x00457ee0": target(
        "CFEPDemoMain__DoAction",
        "void __fastcall CFEPDemoMain__DoAction(void * this)",
        [
            "this+0x8 action state",
            "falls back to CFEPMain__DoAction",
            "CFrontEnd__SetPage",
            "DAT_008a956c",
            "runtime action behavior",
            "rebuild parity remain unproven",
        ],
        ["CFEPMain__DoAction(this)", "CFrontEnd__SetPage", "0xc9", "0xffffffff"],
        ["MOV\tEAX, dword ptr [ECX + 0x8]", "JMP\t0x004623e0", "CALL\t0x00466ae0"],
        ["fepdemo", "action", "comment-hardened"],
        ["005db7d4"],
    ),
    "0x00457f20": target(
        "CFEPDemoMain__Update",
        "void __stdcall CFEPDemoMain__Update(int menu_state)",
        [
            "stack-only menu_state helper",
            "FrontEndText tokens 0/6/8",
            "fallback token 8",
            "runtime localization behavior",
            "rebuild parity remain unproven",
        ],
        [
            "FrontEndText__GetLocalizedOrFallbackTextByToken(0)",
            "FrontEndText__GetLocalizedOrFallbackTextByToken(6)",
            "FrontEndText__GetLocalizedOrFallbackTextByToken(8)",
        ],
        ["MOV\tEAX, dword ptr [ESP + 0x4]", "PUSH\t0x8", "PUSH\t0x6", "PUSH\t0x0", "RET\t0x4"],
        ["fepdemo", "localization", "signature-corrected", "comment-hardened"],
        ["005db7d8"],
    ),
}

EXPECTED_VTABLE_TOKENS = (
    "005db7c0\t3\t005db7cc\t0x00457ed0",
    "005db7c0\t4\t005db7d0\t0x00457ec0",
    "005db7c0\t5\t005db7d4\t0x00457ee0",
    "005db7c0\t6\t005db7d8\t0x00457f20",
    "005e4a70\t2\t005e4a78\t0x00457ec0",
)

EXPECTED_PUBLIC_NOTE_TOKENS = (
    "0x00457ec0",
    "0x00457ed0",
    "0x00457ee0",
    "0x00457f20",
    "CFEPDemoMain__GetMenuType",
    "CFEPDemoMain__GetActionCount",
    "CFEPDemoMain__DoAction",
    "CFEPDemoMain__Update",
    "0x005db7c0",
    "0x005e4a78 is an extra data-table xref to CFEPDemoMain__GetMenuType",
    "FEPDemoMain source file was not found in the current Stuart source snapshot",
    "does not prove runtime frontend behavior",
    "does not prove exact source identity",
    "does not prove rebuild parity",
)

EXPECTED_DRY = {"updated": 0, "skipped": 4, "created": 0, "would_create": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}
EXPECTED_APPLY = {"updated": 4, "skipped": 0, "created": 0, "would_create": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}

OVERCLAIM_TOKENS = (
    "runtime proof",
    "runtime frontend behavior proven",
    "runtime action behavior proven",
    "runtime localization behavior proven",
    "source identity proven",
    "exact source identity proven",
    "rebuild parity proven",
    "fully re'ed",
    "100% re",
)


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
        for key in ("address", "target_addr", "from_addr", "from_function_addr", "function_entry", "entry_addr"):
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


def decompile_text_for(directory: Path, address: str) -> str:
    if not directory.is_dir():
        return ""
    matches = sorted(directory.glob(f"{normalize_address(address)[2:]}_*.c"))
    if not matches:
        return ""
    return read_text(matches[0])


def parse_summary(path: Path) -> dict[str, int] | None:
    text = read_text(path)
    match = re.search(
        r"SUMMARY updated=(\d+) skipped=(\d+) created=(\d+) would_create=(\d+) "
        r"renamed=(\d+) would_rename=(\d+) missing=(\d+) bad=(\d+)",
        text,
    )
    if not match:
        return None
    keys = ("updated", "skipped", "created", "would_create", "renamed", "would_rename", "missing", "bad")
    return {key: int(value) for key, value in zip(keys, match.groups(), strict=True)}


def validate(args: argparse.Namespace) -> tuple[dict[str, object], int]:
    failures: list[str] = []
    metadata_rows = read_tsv(args.metadata)
    tag_rows = read_tsv(args.tags)
    xrefs_text = read_text(args.xrefs)
    instructions_text = read_text(args.instructions)
    vtables_text = read_text(args.vtables)
    public_note = read_text(args.public_note)

    if not metadata_rows:
        failures.append(f"missing metadata rows: {args.metadata}")
    if not tag_rows:
        failures.append(f"missing tag rows: {args.tags}")
    if not xrefs_text:
        failures.append(f"missing xref text: {args.xrefs}")
    if not instructions_text:
        failures.append(f"missing instruction text: {args.instructions}")
    if not vtables_text:
        failures.append(f"missing vtable text: {args.vtables}")
    if not public_note:
        failures.append(f"missing public note: {args.public_note}")

    target_reports: dict[str, dict[str, object]] = {}
    for address, spec in TARGETS.items():
        row = row_by_address(metadata_rows, address)
        target_failures: list[str] = []
        if row is None:
            target_failures.append("missing metadata row")
        else:
            if row.get("name") != spec["name"]:
                target_failures.append(f"expected name {spec['name']}, saw {row.get('name')}")
            if row.get("signature") != spec["signature"]:
                target_failures.append(f"expected signature {spec['signature']}, saw {row.get('signature')}")
            comment = row.get("comment", "")
            for token in spec["commentTokens"]:  # type: ignore[index]
                if not token_present(comment, str(token)):
                    target_failures.append(f"missing comment token: {token}")
            for token in OVERCLAIM_TOKENS:
                if token_present(comment, token):
                    target_failures.append(f"comment overclaim token present: {token}")

        tag_row = row_by_address(tag_rows, address)
        tag_text = tag_row.get("tags", "") if tag_row else ""
        for tag in spec["tags"]:  # type: ignore[index]
            if not token_present(tag_text.replace(";", " "), str(tag)):
                target_failures.append(f"missing tag: {tag}")

        decompile_text = decompile_text_for(args.decompile_dir, address)
        if not decompile_text:
            target_failures.append("missing decompile export")
        for token in spec["decompileTokens"]:  # type: ignore[index]
            if not token_present(decompile_text, str(token)):
                target_failures.append(f"missing decompile token: {token}")

        for token in spec["instructionTokens"]:  # type: ignore[index]
            if not token_present(instructions_text, str(token)):
                target_failures.append(f"missing instruction token: {token}")

        for token in spec["xrefTokens"]:  # type: ignore[index]
            if not token_present(xrefs_text, str(token)):
                target_failures.append(f"missing xref token: {token}")

        if target_failures:
            failures.extend(f"{address} {failure}" for failure in target_failures)
        target_reports[address] = {
            "name": spec["name"],
            "signature": spec["signature"],
            "failures": target_failures,
        }

    for token in EXPECTED_VTABLE_TOKENS:
        if not token_present(vtables_text, token):
            failures.append(f"missing vtable token: {token}")

    for token in EXPECTED_PUBLIC_NOTE_TOKENS:
        if not token_present(public_note, token):
            failures.append(f"public note missing token: {token}")
    for token in OVERCLAIM_TOKENS:
        if token_present(public_note, token):
            failures.append(f"public note overclaim token present: {token}")

    dry_summary = parse_summary(args.dry_log)
    apply_summary = parse_summary(args.apply_log)
    if dry_summary != EXPECTED_DRY:
        failures.append(f"dry summary mismatch: expected {EXPECTED_DRY}, saw {dry_summary}")
    if apply_summary != EXPECTED_APPLY:
        failures.append(f"apply summary mismatch: expected {EXPECTED_APPLY}, saw {apply_summary}")
    if "REPORT: Save succeeded" not in read_text(args.apply_log):
        failures.append("apply log missing REPORT: Save succeeded")

    report: dict[str, object] = {
        "schema": "ghidra-fepdemo-wave402-probe-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "FAIL" if failures else "PASS",
        "target_count": len(TARGETS),
        "targets": target_reports,
        "failures": failures,
        "inputs": {
            "metadata": str(args.metadata),
            "tags": str(args.tags),
            "xrefs": str(args.xrefs),
            "instructions": str(args.instructions),
            "vtables": str(args.vtables),
            "decompile_dir": str(args.decompile_dir),
            "public_note": str(args.public_note),
            "dry_log": str(args.dry_log),
            "apply_log": str(args.apply_log),
        },
    }

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    return report, 1 if failures else 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metadata", type=Path, default=BASE / "metadata_after.tsv")
    parser.add_argument("--tags", type=Path, default=BASE / "tags_after.tsv")
    parser.add_argument("--xrefs", type=Path, default=BASE / "xrefs_after.tsv")
    parser.add_argument("--instructions", type=Path, default=BASE / "instructions_after.tsv")
    parser.add_argument("--vtables", type=Path, default=BASE / "vtable_slots_after.tsv")
    parser.add_argument("--decompile-dir", type=Path, default=BASE / "decompile_after.tsv")
    parser.add_argument("--public-note", type=Path, default=ROOT / "release" / "readiness" / "ghidra_fepdemo_wave402_2026-05-14.md")
    parser.add_argument("--dry-log", type=Path, default=BASE / "apply_fepdemo_wave402_dry.log")
    parser.add_argument("--apply-log", type=Path, default=BASE / "apply_fepdemo_wave402_apply.log")
    parser.add_argument("--out", type=Path, default=BASE / "fepdemo-wave402-probe.json")
    parser.add_argument("--check", action="store_true", help="Compatibility flag; validation is always performed.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    report, status = validate(args)
    print(json.dumps({"status": report["status"], "target_count": report["target_count"], "failure_count": len(report["failures"])}, indent=2))
    if status != 0:
        for failure in report["failures"]:  # type: ignore[index]
            print(f"FAIL: {failure}", file=sys.stderr)
    return status


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
