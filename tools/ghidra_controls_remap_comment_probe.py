#!/usr/bin/env python3
"""Validate the Wave372 controls-remap Ghidra comment/tag tranche."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

DEFAULT_ROOT = Path("subagents/ghidra-static-reaudit/controls-remap-wave372/current")
OUTPUT_NAME = "controls-remap-comment.json"

COMMON_TAGS = {
    "static-reaudit",
    "controls-remap-wave372",
    "retail-binary-evidence",
}


def target(name: str, signature: str, comment_tokens: list[str], tags: list[str]) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "commentTokens": comment_tokens,
        "tags": tags,
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x00453f50": target(
        "Controls__DispatchRemap",
        "void __cdecl Controls__DispatchRemap(int action_code, int key_or_value, void * callback)",
        ["action_code 0x3b..0x4c", "callback(key_or_value, entryId, bindingType)", "runtime remap behavior", "remain unproven"],
        ["controls", "frontend-controls", "remap", "dispatch-helper", "comment-hardened"],
    ),
    "0x004541e0": target(
        "Controls__RemapKey",
        "void __cdecl Controls__RemapKey(int action_code, int key_code)",
        ["g_ControlRemapVkScanPacked", "g_ControlRemapBindingType", "Controls__ApplyPreset", "remain unproven"],
        ["controls", "frontend-controls", "remap", "input-binding", "comment-hardened"],
    ),
    "0x00454e00": target(
        "Controls__GetDeviceCategory",
        "int __cdecl Controls__GetDeviceCategory(int device_code)",
        ["category values 1..7", "remap conflict logic", "runtime input behavior", "remain unproven"],
        ["controls", "frontend-controls", "remap", "device-category", "comment-hardened"],
    ),
    "0x00454e90": target(
        "Controls__ClearDuplicateBinding",
        "void __cdecl Controls__ClearDuplicateBinding(int key_code, short scan_code, int device_code)",
        ["0x20-byte options entry table", "both 12-byte binding slots", "key_code to -1", "remain unproven"],
        ["controls", "frontend-controls", "remap", "duplicate-binding", "options-table", "comment-hardened"],
    ),
    "0x00456650": target(
        "Controls__FindFirstFreeBindingSlot",
        "uint __cdecl Controls__FindFirstFreeBindingSlot(int slot_index)",
        ["entry+0x08+0x0c*slot_index", "pointer-tagged entry result", "caller semantics", "remain unproven"],
        ["controls", "frontend-controls", "remap", "free-binding-slot", "options-table", "comment-hardened"],
    ),
}

XREF_EVIDENCE = [
    ("0x00453f50", "0x00453e69", "CControllerDefinition__RenderBindingsAndPollRemapInput", "UNCONDITIONAL_CALL"),
    ("0x00453f50", "0x004544d9", "Controls__RemapKey", "UNCONDITIONAL_CALL"),
    ("0x00453f50", "0x00455191", "ControlsUI__RenderBindingsList", "UNCONDITIONAL_CALL"),
    ("0x004541e0", "0x00453ee1", "CControllerDefinition__RenderBindingsAndPollRemapInput", "UNCONDITIONAL_CALL"),
    ("0x00454e00", "0x0045449b", "Controls__RemapKey", "UNCONDITIONAL_CALL"),
    ("0x00454e90", "0x0045450e", "Controls__RemapKey", "UNCONDITIONAL_CALL"),
    ("0x00454e90", "0x0045658a", "<no_function>", "UNCONDITIONAL_CALL"),
    ("0x00456650", "0x004d0299", "CControllerBackMenuItem__VFunc_04_004d0290", "UNCONDITIONAL_CALL"),
    ("0x00456650", "0x004d0de2", "CPauseMenu__GetBindingCapacityError", "UNCONDITIONAL_CALL"),
    ("0x00456650", "0x0051d0d9", "<no_function>", "UNCONDITIONAL_CALL"),
]

INSTRUCTION_EVIDENCE = [
    ("0x00453f50", "0x00453f54", "ADD", "-0x3b"),
    ("0x00453f50", "0x00453f60", "JMP", "0x454074"),
    ("0x00453f50", "0x00453f6d", "PUSH", "0x1f"),
    ("0x004541e0", "0x004541e3", "MOV", "[0x00677876]"),
    ("0x004541e0", "0x004541e9", "MOV", "[0x00677870]"),
    ("0x004541e0", "0x004544d9", "CALL", "0x00453f50"),
    ("0x004541e0", "0x0045450e", "CALL", "0x00454e90"),
    ("0x00454e00", "0x00454e09", "JMP", "0x454e3c"),
    ("0x00454e00", "0x00454e2e", "MOV", "0x7"),
    ("0x00454e90", "0x00454e90", "CMP", "[0x008892dc]"),
    ("0x00454e90", "0x00454eba", "LEA", "[EDI + 0x4]"),
    ("0x00454e90", "0x00454f57", "MOV", "0xffffffff"),
    ("0x00456650", "0x00456650", "MOV", "[0x008892dc]"),
    ("0x00456650", "0x0045666f", "CMP", "[EAX + ESI*0x4 + 0x8]"),
    ("0x00456650", "0x00456680", "MOV", "AL, 0x1"),
    ("0x00456650", "0x00456684", "XOR", "AL, AL"),
]

STALE_TOKENS = [
    "param_",
    "unaff_",
]
OVERCLAIM_TOKENS = [
    "fully re'ed",
    "100% re",
    "runtime behavior proven",
    "source identity proven",
    "rebuild parity proven",
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


def unescape_tsv(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def read_tsv(path: Path, *, unescape_comment: bool = False) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if unescape_comment:
        for row in rows:
            row["comment"] = unescape_tsv(row.get("comment", ""))
    return rows


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def parse_summary(log_text: str) -> dict[str, object]:
    match = re.search(r"targets=(\d+)\s+changed_or_would_change=(\d+)\s+failed=(\d+)\s+dry=(true|false)", log_text)
    if not match:
        return {}
    return {
        "targets": int(match.group(1)),
        "changed_or_would_change": int(match.group(2)),
        "failed": int(match.group(3)),
        "dry": match.group(4) == "true",
    }


def row_by_addr(rows: list[dict[str, str]], key: str = "address") -> dict[str, dict[str, str]]:
    return {norm_addr(row.get(key, "")): row for row in rows}


def any_row(rows: list[dict[str, str]], predicate) -> bool:
    return any(predicate(row) for row in rows)


def build_report(
    *,
    root: Path = DEFAULT_ROOT,
    dry_log_path: Path | None = None,
    apply_log_path: Path | None = None,
    metadata_path: Path | None = None,
    tags_path: Path | None = None,
    instructions_path: Path | None = None,
    xrefs_path: Path | None = None,
) -> dict[str, object]:
    root = Path(root)
    dry_log_path = dry_log_path or root / "controls_remap_comment_dry.log"
    apply_log_path = apply_log_path or root / "controls_remap_comment_apply.log"
    metadata_path = metadata_path or root / "metadata_after.tsv"
    tags_path = tags_path or root / "tags_after.tsv"
    instructions_path = instructions_path or root / "instructions_after.tsv"
    xrefs_path = xrefs_path or root / "xrefs_after.tsv"

    failures: list[str] = []
    expected_count = len(TARGETS)
    dry_summary = parse_summary(read_text(dry_log_path))
    apply_summary = parse_summary(read_text(apply_log_path))
    if dry_summary != {"targets": expected_count, "changed_or_would_change": expected_count, "failed": 0, "dry": True}:
        failures.append(f"unexpected dry summary: {dry_summary}")
    if apply_summary != {"targets": expected_count, "changed_or_would_change": expected_count, "failed": 0, "dry": False}:
        failures.append(f"unexpected apply summary: {apply_summary}")

    metadata = row_by_addr(read_tsv(metadata_path, unescape_comment=True))
    tags = row_by_addr(read_tsv(tags_path))
    instruction_rows = read_tsv(instructions_path)
    xref_rows = read_tsv(xrefs_path)

    stale_hits = 0
    overclaim_hits = 0
    for address, spec in TARGETS.items():
        row = metadata.get(norm_addr(address))
        if row is None:
            failures.append(f"missing metadata for {address}")
            continue
        if row.get("status") != "OK":
            failures.append(f"metadata status mismatch for {address}: {row.get('status')}")
        if row.get("name") != spec["name"]:
            failures.append(f"name mismatch for {address}: {row.get('name')} != {spec['name']}")
        if row.get("signature") != spec["signature"]:
            failures.append(f"signature mismatch for {address}: {row.get('signature')} != {spec['signature']}")
        comment = row.get("comment", "")
        for token in spec["commentTokens"]:
            if not token_present(comment, str(token)):
                failures.append(f"comment token missing for {address}: {token}")
        text = "\n".join([row.get("name", ""), row.get("signature", ""), comment])
        for token in STALE_TOKENS:
            if token_present(text, token):
                stale_hits += 1
                failures.append(f"stale token for {address}: {token}")
        for token in OVERCLAIM_TOKENS:
            if token_present(text, token):
                overclaim_hits += 1
                failures.append(f"overclaim token for {address}: {token}")

        tag_row = tags.get(norm_addr(address))
        if tag_row is None or tag_row.get("status") != "OK":
            failures.append(f"missing tag row for {address}")
        else:
            found_tags = {tag.strip() for tag in tag_row.get("tags", "").split(";") if tag.strip()}
            expected_tags = COMMON_TAGS | set(spec["tags"])
            missing = sorted(expected_tags - found_tags)
            if missing:
                failures.append(f"missing tags for {address}: {missing}")

    xref_hits = 0
    for target_addr, from_addr, from_function, ref_type in XREF_EVIDENCE:
        if any_row(
            xref_rows,
            lambda row, target_addr=target_addr, from_addr=from_addr, from_function=from_function, ref_type=ref_type: (
                norm_addr(row.get("target_addr")) == norm_addr(target_addr)
                and norm_addr(row.get("from_addr")) == norm_addr(from_addr)
                and row.get("from_function") == from_function
                and row.get("ref_type") == ref_type
            ),
        ):
            xref_hits += 1
        else:
            failures.append(f"missing xref evidence {from_addr} -> {target_addr} {from_function} {ref_type}")

    instruction_hits = 0
    for target_addr, instruction_addr, mnemonic, operand_token in INSTRUCTION_EVIDENCE:
        if any_row(
            instruction_rows,
            lambda row, target_addr=target_addr, instruction_addr=instruction_addr, mnemonic=mnemonic, operand_token=operand_token: (
                norm_addr(row.get("function_entry")) == norm_addr(target_addr)
                and norm_addr(row.get("instruction_addr")) == norm_addr(instruction_addr)
                and row.get("mnemonic") == mnemonic
                and token_present(row.get("operands", ""), operand_token)
            ),
        ):
            instruction_hits += 1
        else:
            failures.append(f"missing instruction evidence {target_addr} {instruction_addr} {mnemonic} {operand_token}")

    return {
        "status": "PASS" if not failures else "FAIL",
        "summary": {
            "targets": expected_count,
            "xrefEvidenceHits": xref_hits,
            "instructionEvidenceHits": instruction_hits,
            "staleTokenHits": stale_hits,
            "overclaimHits": overclaim_hits,
        },
        "paths": {
            "root": str(root),
            "metadata": str(metadata_path),
            "tags": str(tags_path),
            "instructions": str(instructions_path),
            "xrefs": str(xrefs_path),
        },
        "failures": failures,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    report = build_report(root=args.root)
    args.root.mkdir(parents=True, exist_ok=True)
    output_path = args.root / OUTPUT_NAME
    output_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"{report['status']}: wrote {output_path}")
    print(json.dumps(report["summary"], sort_keys=True))
    if args.check and report["status"] != "PASS":
        for failure in report["failures"]:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
