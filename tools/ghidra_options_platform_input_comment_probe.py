#!/usr/bin/env python3
"""Validate the saved options/platform-input Ghidra comment tranche."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

DEFAULT_ROOT = Path("subagents/ghidra-static-reaudit/options-platform-input-wave363/current")
OUTPUT_NAME = "options-platform-input-comment.json"

COMMON_TAGS = {
    "static-reaudit",
    "options-platform-input-wave363",
    "retail-binary-evidence",
}


def target(
    name: str,
    signature: str,
    comment_tokens: list[str],
    decompile_tokens: list[str],
    tags: list[str],
) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "commentTokens": comment_tokens,
        "decompileTokens": decompile_tokens,
        "tags": tags,
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x0042d260": target(
        "OptionsEntries__InitSingleBindingEntry",
        "void * __thiscall OptionsEntries__InitSingleBindingEntry(void * this, byte active, int entry_id, int slot0_device_code, short slot0_scan, short slot0_vk)",
        ["RET 0x14", "active byte", "entry_id", "slot-0 device/scan/vk", "remain unproven"],
        ["*(byte *)this = active", "0xffffffff", "return this"],
        ["options-entry", "control-bindings"],
    ),
    "0x0042d2b0": target(
        "OptionsEntries__InitDualBindingEntry",
        "void * __thiscall OptionsEntries__InitDualBindingEntry(void * this, byte active, int entry_id, int slot0_device_code, short slot0_scan, int slot1_device_code, short slot1_scan, short slot0_vk, short slot1_vk)",
        ["RET 0x20", "dual-binding", "slot-0", "slot-1", "remain unproven"],
        ["slot1_device_code", "slot1_scan", "slot1_vk", "return this"],
        ["options-entry", "control-bindings"],
    ),
    "0x0042d300": target(
        "OptionsEntries__InitSentinelEntry",
        "void __thiscall OptionsEntries__InitSentinelEntry(void * this)",
        ["sentinel", "entry_id -1", "active byte", "remain unproven"],
        ["*(undefined1 *)this = 0", "0xffffffff"],
        ["options-entry", "control-bindings", "sentinel"],
    ),
    "0x0042d310": target(
        "PlatformInput__InitMouse",
        "int PlatformInput__InitMouse(void)",
        ["DirectInput mouse device", "data format", "cooperative level", "centers the cursor", "remain unproven"],
        ["DAT_00889028", "DAT_0066e950", "CProfiler__ResetAll", "PlatformInput__SetGlobalInputState(1)"],
        ["platform-input", "directinput", "mouse-input"],
    ),
    "0x0042d3b0": target(
        "PlatformInput__ShutdownMouse",
        "int PlatformInput__ShutdownMouse(void)",
        ["Unacquires/releases", "cursor position", "GetCursorPos", "remain unproven"],
        ["PlatformInput__SetGlobalInputState(0)", "GetCursorPos", "DAT_0066e950"],
        ["platform-input", "directinput", "mouse-input"],
    ),
    "0x0042d420": target(
        "PlatformInput__PollMouseMotion",
        "int PlatformInput__PollMouseMotion(void)",
        ["mouse deltas", "wheel", "reacquires", "0x8007001e", "remain unproven"],
        ["DAT_0066e8f0", "DAT_0089be48", "-0x7ff8ffe2"],
        ["platform-input", "directinput", "mouse-input", "input-poll"],
    ),
    "0x0042d4d0": target(
        "PlatformInput__PollMouseState",
        "int PlatformInput__PollMouseState(void)",
        ["button transitions", "left/right/middle", "0x80", "0x8000", "0x800000", "remain unproven"],
        ["DAT_0066e8fc & 0x80", "DAT_0066e8fc & 0x8000", "DAT_0089be10"],
        ["platform-input", "directinput", "mouse-input", "input-poll"],
    ),
}

XREF_EVIDENCE = [
    ("0x0042d260", "0x0051421f", "OptionsEntries__InitDefaultSingleBindingsTable", "UNCONDITIONAL_CALL"),
    ("0x0042d2b0", "0x00453475", "OptionsEntries__InitDefaultDualBindingsTable", "UNCONDITIONAL_CALL"),
    ("0x0042d300", "0x00453614", "OptionsEntries__InitDefaultDualBindingsTable", "UNCONDITIONAL_CALL"),
    ("0x0042d310", "0x00472ac6", "CGame__ToggleMouseInputState", "UNCONDITIONAL_CALL"),
    ("0x0042d3b0", "0x00472ac0", "CGame__ToggleMouseInputState", "UNCONDITIONAL_CALL"),
    ("0x0042d420", "0x0046e63e", "CGame__Render", "UNCONDITIONAL_CALL"),
    ("0x0042d4d0", "0x0046eb62", "CGame__Update", "UNCONDITIONAL_CALL"),
]

INSTRUCTION_EVIDENCE = [
    ("0x0042d260", "0x0042d29f", "RET", "0x14"),
    ("0x0042d2b0", "0x0042d2f9", "RET", "0x20"),
    ("0x0042d300", "0x0042d305", "MOV", "0xffffffff"),
    ("0x0042d310", "0x0042d324", "CALL", "dword ptr [ECX + 0xc]"),
    ("0x0042d3b0", "0x0042d3bf", "CALL", "dword ptr [ECX + 0x20]"),
    ("0x0042d420", "0x0042d469", "CMP", "0x8007001e"),
    ("0x0042d4d0", "0x0042d594", "TEST", "0x80"),
]

STALE_SIGNATURE_TOKENS = ["<none>", "<no_function>", "MISSING", "undefined ", "param_1", "param_2", "param_3"]
OVERCLAIM_TOKENS = [
    "runtime input proven",
    "runtime behavior proven",
    "source identity proven",
    "fully re'ed",
    "100% re",
    "layout proven",
]


def norm_addr(value: object) -> str:
    text = str(value or "").strip().lower()
    if text.startswith("0x"):
        text = text[2:]
    if not text or text.startswith("<"):
        return text
    return "0x" + text.zfill(8)


def compact(value: str) -> str:
    return "".join(value.lower().split())


def token_present(text: str, token: str) -> bool:
    return compact(token) in compact(text)


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def parse_summary(log_text: str) -> dict[str, object]:
    match = re.search(r"targets=(\d+)\s+updated=(\d+)\s+skipped=(\d+)\s+failed=(\d+)\s+dry=(true|false)", log_text)
    if not match:
        return {}
    return {
        "targets": int(match.group(1)),
        "updated": int(match.group(2)),
        "skipped": int(match.group(3)),
        "failed": int(match.group(4)),
        "dry": match.group(5) == "true",
    }


def row_by_addr(rows: list[dict[str, str]], key: str = "address") -> dict[str, dict[str, str]]:
    return {norm_addr(row.get(key, "")): row for row in rows}


def decompile_for(decompile_dir: Path, address: str) -> str:
    matches = sorted(decompile_dir.glob(f"{norm_addr(address)[2:]}_*.c"))
    return "\n".join(read_text(path) for path in matches)


def any_row(rows: list[dict[str, str]], predicate) -> bool:
    return any(predicate(row) for row in rows)


def build_report(
    *,
    root: Path = DEFAULT_ROOT,
    dry_log_path: Path | None = None,
    apply_log_path: Path | None = None,
    metadata_path: Path | None = None,
    tags_path: Path | None = None,
    xrefs_path: Path | None = None,
    instructions_path: Path | None = None,
    decompile_dir: Path | None = None,
) -> dict[str, object]:
    root = Path(root)
    dry_log_path = dry_log_path or root / "options_platform_input_comment_dry.log"
    apply_log_path = apply_log_path or root / "options_platform_input_comment_apply.log"
    metadata_path = metadata_path or root / "metadata_after.tsv"
    tags_path = tags_path or root / "tags_after.tsv"
    xrefs_path = xrefs_path or root / "xrefs_after.tsv"
    instructions_path = instructions_path or root / "instructions_after.tsv"
    decompile_dir = decompile_dir or root / "decompile_after"

    failures: list[str] = []
    metadata = row_by_addr(read_tsv(metadata_path))
    tags = row_by_addr(read_tsv(tags_path))
    xrefs = read_tsv(xrefs_path)
    instructions = read_tsv(instructions_path)

    expected_count = len(TARGETS)
    dry_summary = parse_summary(read_text(dry_log_path))
    apply_summary = parse_summary(read_text(apply_log_path))
    if dry_summary != {"targets": expected_count, "updated": 0, "skipped": expected_count, "failed": 0, "dry": True}:
        failures.append(f"unexpected dry summary: {dry_summary}")
    if apply_summary != {"targets": expected_count, "updated": expected_count, "skipped": 0, "failed": 0, "dry": False}:
        failures.append(f"unexpected apply summary: {apply_summary}")

    stale_signature_hits = 0
    overclaim_hits = 0

    for address, spec in TARGETS.items():
        row = metadata.get(address)
        if not row:
            failures.append(f"{address} metadata missing")
            continue
        name = row.get("name", "")
        signature = row.get("signature", "")
        if name != spec["name"]:
            failures.append(f"{address} name mismatch: {name} != {spec['name']}")
        if signature != spec["signature"]:
            failures.append(f"{address} signature mismatch: {signature} != {spec['signature']}")
        for token in STALE_SIGNATURE_TOKENS:
            if token in signature:
                stale_signature_hits += 1
                failures.append(f"{address} stale signature token present: {token}")

        comment = row.get("comment", "")
        for token in spec["commentTokens"]:  # type: ignore[index]
            if not token_present(comment, str(token)):
                failures.append(f"{address} comment missing token: {token}")
        for token in OVERCLAIM_TOKENS:
            if token in comment.lower():
                overclaim_hits += 1
                failures.append(f"{address} comment overclaim token: {token}")

        tag_text = tags.get(address, {}).get("tags", "")
        expected_tags = COMMON_TAGS | set(spec["tags"])  # type: ignore[arg-type]
        for tag in expected_tags:
            if tag not in tag_text:
                failures.append(f"{address} tag missing: {tag}")

        decompile_text = decompile_for(decompile_dir, address)
        for token in spec["decompileTokens"]:  # type: ignore[index]
            if not token_present(decompile_text, str(token)):
                failures.append(f"{address} decompile missing token: {token}")

    xref_hits = 0
    for target_addr, from_addr, from_name, ref_type in XREF_EVIDENCE:
        if any_row(
            xrefs,
            lambda row, target_addr=target_addr, from_addr=from_addr, from_name=from_name, ref_type=ref_type: (
                norm_addr(row.get("target_addr")) == target_addr
                and norm_addr(row.get("from_addr")) == from_addr
                and from_name in row.get("from_function", "")
                and row.get("ref_type") == ref_type
            ),
        ):
            xref_hits += 1
        else:
            failures.append(f"xref evidence missing: {target_addr} from {from_addr}")

    instruction_hits = 0
    for target_addr, instr_addr, mnemonic, operand_token in INSTRUCTION_EVIDENCE:
        if any_row(
            instructions,
            lambda row, target_addr=target_addr, instr_addr=instr_addr, mnemonic=mnemonic, operand_token=operand_token: (
                norm_addr(row.get("target_addr")) == target_addr
                and norm_addr(row.get("instruction_addr")) == instr_addr
                and row.get("mnemonic", "").upper() == mnemonic
                and token_present(row.get("operands", ""), operand_token)
            ),
        ):
            instruction_hits += 1
        else:
            failures.append(f"instruction evidence missing: {target_addr} {instr_addr}")

    return {
        "status": "PASS" if not failures else "FAIL",
        "summary": {
            "targets": expected_count,
            "metadataRows": len(metadata),
            "tagRows": len(tags),
            "xrefRows": len(xrefs),
            "instructionRows": len(instructions),
            "xrefEvidenceHits": xref_hits,
            "instructionEvidenceHits": instruction_hits,
            "staleSignatureHits": stale_signature_hits,
            "overclaimHits": overclaim_hits,
        },
        "failures": failures,
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--check", action="store_true", help="Exit non-zero on validation failure.")
    args = parser.parse_args(argv)

    report = build_report(root=args.root)
    args.root.mkdir(parents=True, exist_ok=True)
    (args.root / OUTPUT_NAME).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"status={report['status']}")
    print(json.dumps(report["summary"], sort_keys=True))
    if report["status"] != "PASS":
        for failure in report["failures"]:
            print(f"FAIL: {failure}")
        return 1 if args.check else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
