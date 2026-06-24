#!/usr/bin/env python3
"""Validate the Wave371 MenuItem base-vfunc Ghidra comment/tag tranche."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

DEFAULT_ROOT = Path("subagents/ghidra-static-reaudit/menuitem-base-wave371/current")
OUTPUT_NAME = "menuitem-base-comment.json"

COMMON_TAGS = {
    "static-reaudit",
    "menuitem-base-wave371",
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
    "0x00453a50": target(
        "CMenuItem__ButtonPressed_NoOp",
        "void __thiscall CMenuItem__ButtonPressed_NoOp(void * this, int from_controller, int button)",
        ["RET 0x0c", "0x005db440 slot 1", "runtime input behavior", "remain unproven"],
        ["menuitem", "frontend-menu", "no-op-vfunc", "comment-hardened"],
    ),
    "0x00453a60": target(
        "CMenuItem__IsEnabled",
        "int __thiscall CMenuItem__IsEnabled(void * this)",
        ["this+0x10", "0x005db440 slot 3", "0x005dc520 slot 3", "remain unproven"],
        ["menuitem", "frontend-menu", "vtable-slot", "comment-hardened"],
    ),
    "0x00453a70": target(
        "CMenuItem__GetRowHeight",
        "int __thiscall CMenuItem__GetRowHeight(void * this)",
        ["0x14", "0x28", "this+0x0c", "remain unproven"],
        ["menuitem", "frontend-menu", "layout", "comment-hardened"],
    ),
    "0x00453a80": target(
        "CMenuItem__DefaultFalseFlag",
        "byte __thiscall CMenuItem__DefaultFalseFlag(void * this)",
        ["returns zero", "slots 8, 9, and 10", "sibling menu-item vtables", "remain unproven"],
        ["menuitem", "frontend-menu", "shared-false-vfunc", "comment-hardened"],
    ),
    "0x00453a90": target(
        "CMenuItem__scalar_deleting_dtor",
        "void * __thiscall CMenuItem__scalar_deleting_dtor(void * this, byte flags)",
        ["vtable 0x005db440", "OID__FreeObject", "flags bit 0", "remain unproven"],
        ["menuitem", "frontend-menu", "destructor", "comment-hardened"],
    ),
}

PRIMARY_VTABLE_EVIDENCE = [
    ("0x005db440", "0", "0x005db440", "0x00453a90", "CMenuItem__scalar_deleting_dtor"),
    ("0x005db440", "1", "0x005db444", "0x00453a50", "CMenuItem__ButtonPressed_NoOp"),
    ("0x005db440", "3", "0x005db44c", "0x00453a60", "CMenuItem__IsEnabled"),
    ("0x005db440", "6", "0x005db458", "0x00453a70", "CMenuItem__GetRowHeight"),
    ("0x005db440", "8", "0x005db460", "0x00453a80", "CMenuItem__DefaultFalseFlag"),
    ("0x005db440", "9", "0x005db464", "0x00453a80", "CMenuItem__DefaultFalseFlag"),
    ("0x005db440", "10", "0x005db468", "0x00453a80", "CMenuItem__DefaultFalseFlag"),
]

SIBLING_VTABLE_EVIDENCE = [
    ("0x005dc520", "3", "0x005dc52c", "0x00453a60", "CMenuItem__IsEnabled"),
    ("0x005dc520", "6", "0x005dc538", "0x00453a70", "CMenuItem__GetRowHeight"),
    ("0x005dc520", "8", "0x005dc540", "0x00453a80", "CMenuItem__DefaultFalseFlag"),
    ("0x005dc520", "9", "0x005dc544", "0x00453a80", "CMenuItem__DefaultFalseFlag"),
    ("0x005dc520", "10", "0x005dc548", "0x00453a80", "CMenuItem__DefaultFalseFlag"),
]

XREF_EVIDENCE = [
    ("0x00453a90", "0x005db440", "DATA"),
    ("0x00453a50", "0x005db444", "DATA"),
    ("0x00453a60", "0x005db44c", "DATA"),
    ("0x00453a70", "0x005db458", "DATA"),
    ("0x00453a80", "0x005db460", "DATA"),
    ("0x00453a80", "0x005db464", "DATA"),
    ("0x00453a80", "0x005db468", "DATA"),
    ("0x00453a60", "0x005dc52c", "DATA"),
    ("0x00453a70", "0x005dc538", "DATA"),
    ("0x00453a80", "0x005dc540", "DATA"),
]

INSTRUCTION_EVIDENCE = [
    ("0x00453a50", "0x00453a50", "RET", "0xc"),
    ("0x00453a60", "0x00453a60", "MOV", "[ECX + 0x10]"),
    ("0x00453a70", "0x00453a70", "MOV", "[ECX + 0xc]"),
    ("0x00453a70", "0x00453a77", "AND", "0x14"),
    ("0x00453a70", "0x00453a7a", "ADD", "0x14"),
    ("0x00453a80", "0x00453a80", "XOR", "AL, AL"),
    ("0x00453a90", "0x00453a99", "MOV", "0x5db440"),
    ("0x00453a90", "0x00453aa7", "CALL", "0x00549220"),
    ("0x00453a90", "0x00453aaf", "RET", "0x4"),
]

STALE_TOKENS = [
    "undefined ",
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
    primary_vtable_path: Path | None = None,
    sibling_vtable_path: Path | None = None,
    instructions_path: Path | None = None,
    xrefs_path: Path | None = None,
) -> dict[str, object]:
    root = Path(root)
    dry_log_path = dry_log_path or root / "menuitem_base_comment_dry.log"
    apply_log_path = apply_log_path or root / "menuitem_base_comment_apply.log"
    metadata_path = metadata_path or root / "metadata_after.tsv"
    tags_path = tags_path or root / "tags_after.tsv"
    primary_vtable_path = primary_vtable_path or root / "primary_vtable_slots_after.tsv"
    sibling_vtable_path = sibling_vtable_path or root / "vtable_slots_after.tsv"
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
    primary_vtable_rows = read_tsv(primary_vtable_path)
    sibling_vtable_rows = read_tsv(sibling_vtable_path)
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

    primary_vtable_hits = count_vtable_hits(primary_vtable_rows, PRIMARY_VTABLE_EVIDENCE, failures)
    sibling_vtable_hits = count_vtable_hits(sibling_vtable_rows, SIBLING_VTABLE_EVIDENCE, failures)

    xref_hits = 0
    for target_addr, from_addr, ref_type in XREF_EVIDENCE:
        if any_row(
            xref_rows,
            lambda row, target_addr=target_addr, from_addr=from_addr, ref_type=ref_type: (
                norm_addr(row.get("target_addr")) == norm_addr(target_addr)
                and norm_addr(row.get("from_addr")) == norm_addr(from_addr)
                and row.get("ref_type") == ref_type
            ),
        ):
            xref_hits += 1
        else:
            failures.append(f"missing xref evidence {from_addr} -> {target_addr} {ref_type}")

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
            "primaryVtableEvidenceHits": primary_vtable_hits,
            "siblingVtableEvidenceHits": sibling_vtable_hits,
            "xrefEvidenceHits": xref_hits,
            "instructionEvidenceHits": instruction_hits,
            "staleTokenHits": stale_hits,
            "overclaimHits": overclaim_hits,
        },
        "paths": {
            "root": str(root),
            "metadata": str(metadata_path),
            "tags": str(tags_path),
            "primaryVtable": str(primary_vtable_path),
            "siblingVtable": str(sibling_vtable_path),
            "instructions": str(instructions_path),
            "xrefs": str(xrefs_path),
        },
        "failures": failures,
    }


def count_vtable_hits(
    rows: list[dict[str, str]],
    evidence: list[tuple[str, str, str, str, str]],
    failures: list[str],
) -> int:
    hits = 0
    for vtable_addr, slot, slot_addr, pointer, name in evidence:
        if any_row(
            rows,
            lambda row, vtable_addr=vtable_addr, slot=slot, slot_addr=slot_addr, pointer=pointer, name=name: (
                norm_addr(row.get("vtable")) == norm_addr(vtable_addr)
                and row.get("slot_index") == slot
                and norm_addr(row.get("slot_addr")) == norm_addr(slot_addr)
                and norm_addr(row.get("pointer_addr")) == norm_addr(pointer)
                and norm_addr(row.get("function_entry")) == norm_addr(pointer)
                and row.get("function_name") == name
                and row.get("status") == "OK"
            ),
        ):
            hits += 1
        else:
            failures.append(f"missing vtable evidence {vtable_addr} slot {slot} -> {pointer} {name}")
    return hits


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
