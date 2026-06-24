#!/usr/bin/env python3
"""Validate the saved UnitAI indexed-entry and motion-controller boundary tranche."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


DEFAULT_ROOT = Path("subagents/ghidra-static-reaudit/unitai-indexed-entry-wave354/current")
OUTPUT_NAME = "unitai-indexed-entry-boundary.json"

COMMON_TAGS = {
    "static-reaudit",
    "unitai-indexed-entry-wave354",
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
    "0x00444f00": target(
        "CUnitAI__CallIndexedEntryVFunc10",
        "int __thiscall CUnitAI__CallIndexedEntryVFunc10(void * this, int entryIndex)",
        ["indexed entry", "vfunc slot +0x10", "retail evidence only", "remain unproven"],
        ["entryIndex", "+ 0x10"],
        ["unitai-system", "signature-hardened", "indexed-entry"],
    ),
    "0x00444f20": target(
        "CUnitAI__CanUseIndexedSegmentEntry",
        "bool __thiscall CUnitAI__CanUseIndexedSegmentEntry(void * this, int entryIndex)",
        ["indexed segment", "core-child", "eligibility", "remain unproven"],
        ["entryIndex", "CDestroyableCoreSegment__AreCoreChildrenDestroyed", "CDestroyableSegment__SumActiveValueRecursive"],
        ["unitai-system", "signature-hardened", "indexed-entry"],
    ),
    "0x00494fa0": target(
        "SharedMotionController__VFunc_UpdateUnitAIIndexedEntryFlag",
        "void __thiscall SharedMotionController__VFunc_UpdateUnitAIIndexedEntryFlag(void * this, void * stateContext, int * outFlags)",
        ["CMCBuggy slot 17", "CMCHiveBoss slot 6", "outFlags", "remain unproven"],
        ["stateContext", "outFlags", "CUnitAI__CanUseIndexedSegmentEntry"],
        ["motion-controller", "function-boundary", "vtable-slot", "shared-vfunc"],
    ),
    "0x00494ff0": target(
        "SharedMotionController__VFunc_CallUnitAIIndexedEntryVFunc10",
        "int __thiscall SharedMotionController__VFunc_CallUnitAIIndexedEntryVFunc10(void * this, void * stateContext)",
        ["CMCBuggy slot 18", "CMCHiveBoss slot 7", "CUnitAI__CallIndexedEntryVFunc10", "remain unproven"],
        ["stateContext", "CUnitAI__CallIndexedEntryVFunc10"],
        ["motion-controller", "function-boundary", "vtable-slot", "shared-vfunc"],
    ),
    "0x00495020": target(
        "CMCBuggy__VFunc_GetUnitAIEntryTableRoot",
        "void * __thiscall CMCBuggy__VFunc_GetUnitAIEntryTableRoot(void * this)",
        ["CMCBuggy vtable slot 19", "field +0x0c", "first pointer", "remain unproven"],
        ["return", "+ 0xc"],
        ["motion-controller", "function-boundary", "vtable-slot", "cmcbuggy"],
    ),
}

XREF_EVIDENCE = [
    ("0x00444f00", "0x0049500d", "UNCONDITIONAL_CALL"),
    ("0x00444f20", "0x00494fc2", "UNCONDITIONAL_CALL"),
    ("0x00494fa0", "0x005dc294", "DATA"),
    ("0x00494fa0", "0x005dc3a0", "DATA"),
    ("0x00494ff0", "0x005dc298", "DATA"),
    ("0x00494ff0", "0x005dc3a4", "DATA"),
    ("0x00495020", "0x005dc29c", "DATA"),
]

VTABLE_EVIDENCE = [
    ("0x005dc250", "17", "0x005dc294", "0x00494fa0"),
    ("0x005dc250", "18", "0x005dc298", "0x00494ff0"),
    ("0x005dc250", "19", "0x005dc29c", "0x00495020"),
    ("0x005dc388", "6", "0x005dc3a0", "0x00494fa0"),
    ("0x005dc388", "7", "0x005dc3a4", "0x00494ff0"),
]

VTABLE_OWNER_EVIDENCE = [
    ("0x005dc250", "CMCBuggy"),
    ("0x005dc388", "CMCHiveBoss"),
]

INSTRUCTION_EVIDENCE = [
    ("0x00444f00", "0x00444f18", "RET", "0x4"),
    ("0x00444f20", "0x00444f4b", "RET", "0x4"),
    ("0x00494fa0", "0x00494fc2", "CALL", "0x00444f20"),
    ("0x00494fa0", "0x00494fd6", "RET", "0x8"),
    ("0x00494ff0", "0x0049500d", "CALL", "0x00444f00"),
    ("0x00494ff0", "0x00495012", "RET", "0x4"),
    ("0x00495020", "0x00495025", "RET", ""),
]

STALE_TOKENS = ["<none>", "<no_function>", "MISSING", "undefined ", "param_1", "param_2"]
OVERCLAIM_TOKENS = [
    "runtime behavior proven",
    "source identity proven",
    "exact source virtual name proven",
    "layout proven",
]


def norm_addr(value: object) -> str:
    text = str(value or "").strip().lower()
    if text.startswith("0x"):
        text = text[2:]
    if not text or text.startswith("<"):
        return text
    return "0x" + text.zfill(8)


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def parse_summary(log_text: str) -> dict[str, object]:
    result: dict[str, object] = {}
    match = re.search(r"targets=(\d+)\s+changed_or_would_change=(\d+)\s+failed=(\d+)\s+dry=(true|false)", log_text)
    if match:
        result["targets"] = int(match.group(1))
        result["changedOrWouldChange"] = int(match.group(2))
        result["failed"] = int(match.group(3))
        result["dry"] = match.group(4) == "true"
    return result


def row_by_addr(rows: list[dict[str, str]], key: str = "address") -> dict[str, dict[str, str]]:
    return {norm_addr(row.get(key, "")): row for row in rows}


def any_row(rows: list[dict[str, str]], predicate) -> bool:
    return any(predicate(row) for row in rows)


def decompile_for(decompile_dir: Path, address: str, name: str) -> str:
    exact = decompile_dir / f"{address[2:]}_{name}.c"
    if exact.exists():
        return read_text(exact)
    matches = sorted(decompile_dir.glob(f"{address[2:]}_*.c"))
    return "\n".join(read_text(path) for path in matches)


def build_report(
    *,
    root: Path = DEFAULT_ROOT,
    dry_log_path: Path | None = None,
    apply_log_path: Path | None = None,
    metadata_path: Path | None = None,
    tags_path: Path | None = None,
    xrefs_path: Path | None = None,
    instructions_path: Path | None = None,
    vtable_path: Path | None = None,
    vtable_owner_path: Path | None = None,
    decompile_dir: Path | None = None,
) -> dict[str, object]:
    dry_log_path = dry_log_path or root / "unitai_indexed_entry_boundary_dry.log"
    apply_log_path = apply_log_path or root / "unitai_indexed_entry_boundary_apply.log"
    metadata_path = metadata_path or root / "metadata_after.tsv"
    tags_path = tags_path or root / "tags_after.tsv"
    xrefs_path = xrefs_path or root / "xrefs_after.tsv"
    instructions_path = instructions_path or root / "instructions_after.tsv"
    vtable_path = vtable_path or root / "vtable_slots_after.tsv"
    vtable_owner_path = vtable_owner_path or root / "vtable_owner_candidates_after.tsv"
    decompile_dir = decompile_dir or root / "decompile_after"

    failures: list[str] = []
    dry_summary = parse_summary(read_text(dry_log_path))
    apply_summary = parse_summary(read_text(apply_log_path))
    if dry_summary.get("targets") != len(TARGETS) or dry_summary.get("failed") != 0 or dry_summary.get("dry") is not True:
        failures.append(f"dry summary mismatch: {dry_summary}")
    if apply_summary.get("targets") != len(TARGETS) or apply_summary.get("failed") != 0 or apply_summary.get("dry") is not False:
        failures.append(f"apply summary mismatch: {apply_summary}")

    metadata = row_by_addr(read_tsv(metadata_path))
    tags = row_by_addr(read_tsv(tags_path))
    xrefs = read_tsv(xrefs_path)
    instructions = read_tsv(instructions_path)
    vtables = read_tsv(vtable_path)
    owners = read_tsv(vtable_owner_path)

    for address, spec in TARGETS.items():
        row = metadata.get(address)
        if not row:
            failures.append(f"{address} metadata missing")
            continue
        if row.get("status") != "OK":
            failures.append(f"{address} metadata status is {row.get('status')}")
        if row.get("name") != spec["name"]:
            failures.append(f"{address} name mismatch: {row.get('name')} != {spec['name']}")
        if row.get("signature") != spec["signature"]:
            failures.append(f"{address} signature mismatch: {row.get('signature')} != {spec['signature']}")
        comment = row.get("comment", "")
        for token in spec["commentTokens"]:  # type: ignore[index]
            if str(token) not in comment:
                failures.append(f"{address} comment missing token: {token}")
        for token in OVERCLAIM_TOKENS:
            if token in comment:
                failures.append(f"{address} comment overclaim token present: {token}")

        tag_row = tags.get(address)
        tag_text = tag_row.get("tags", "") if tag_row else ""
        for tag in sorted(COMMON_TAGS | set(spec["tags"])):  # type: ignore[arg-type]
            if tag not in tag_text:
                failures.append(f"{address} tag missing: {tag}")

        decompile = decompile_for(decompile_dir, address, str(spec["name"]))
        if not decompile:
            failures.append(f"{address} decompile missing")
        for token in spec["decompileTokens"]:  # type: ignore[index]
            if str(token) not in decompile:
                failures.append(f"{address} decompile missing token: {token}")
        for token in STALE_TOKENS:
            if token in row.get("signature", "") or token in decompile:
                failures.append(f"{address} stale token present: {token}")

    xref_hits = 0
    for target_addr, from_addr, ref_type in XREF_EVIDENCE:
        if any_row(
            xrefs,
            lambda row, target_addr=target_addr, from_addr=from_addr, ref_type=ref_type: (
                norm_addr(row.get("target_addr")) == norm_addr(target_addr)
                and norm_addr(row.get("from_addr")) == norm_addr(from_addr)
                and row.get("ref_type") == ref_type
            ),
        ):
            xref_hits += 1
        else:
            failures.append(f"xref evidence missing: {target_addr} from {from_addr} {ref_type}")

    instruction_hits = 0
    for target_addr, instr_addr, mnemonic, operand_token in INSTRUCTION_EVIDENCE:
        if any_row(
            instructions,
            lambda row, target_addr=target_addr, instr_addr=instr_addr, mnemonic=mnemonic, operand_token=operand_token: (
                norm_addr(row.get("target_addr")) == norm_addr(target_addr)
                and norm_addr(row.get("instruction_addr")) == norm_addr(instr_addr)
                and row.get("mnemonic") == mnemonic
                and (not operand_token or operand_token in row.get("operands", ""))
            ),
        ):
            instruction_hits += 1
        else:
            failures.append(f"instruction evidence missing: {target_addr} {instr_addr} {mnemonic} {operand_token}")

    vtable_hits = 0
    for vtable, slot, slot_addr, pointer_addr in VTABLE_EVIDENCE:
        if any_row(
            vtables,
            lambda row, vtable=vtable, slot=slot, slot_addr=slot_addr, pointer_addr=pointer_addr: (
                norm_addr(row.get("vtable")) == norm_addr(vtable)
                and row.get("slot_index") == slot
                and norm_addr(row.get("slot_addr")) == norm_addr(slot_addr)
                and norm_addr(row.get("pointer_addr")) == norm_addr(pointer_addr)
                and norm_addr(row.get("function_entry")) == norm_addr(pointer_addr)
                and row.get("status") == "OK"
            ),
        ):
            vtable_hits += 1
        else:
            failures.append(f"vtable evidence missing: {vtable} slot {slot} -> {pointer_addr}")

    owner_hits = 0
    for vtable, owner in VTABLE_OWNER_EVIDENCE:
        if any_row(
            owners,
            lambda row, vtable=vtable, owner=owner: (
                norm_addr(row.get("vtable")) == norm_addr(vtable)
                and row.get("demangled_type_name") == owner
            ),
        ):
            owner_hits += 1
        else:
            failures.append(f"vtable owner evidence missing: {vtable} {owner}")

    return {
        "schema": "unitai-indexed-entry-boundary.v1",
        "status": "PASS" if not failures else "FAIL",
        "summary": {
            "targets": len(TARGETS),
            "xrefEvidenceHits": xref_hits,
            "instructionEvidenceHits": instruction_hits,
            "vtableEvidenceHits": vtable_hits,
            "vtableOwnerEvidenceHits": owner_hits,
        },
        "artifacts": {
            "root": str(root),
            "dryLog": str(dry_log_path),
            "applyLog": str(apply_log_path),
            "metadata": str(metadata_path),
            "tags": str(tags_path),
            "xrefs": str(xrefs_path),
            "instructions": str(instructions_path),
            "vtableSlots": str(vtable_path),
            "vtableOwners": str(vtable_owner_path),
            "decompileDir": str(decompile_dir),
        },
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    report = build_report(root=args.root)
    out_path = args.out or args.root / OUTPUT_NAME
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"{report['status']}: wrote {out_path}")
    if args.check and report["status"] != "PASS":
        for failure in report["failures"]:
            print(f"FAIL: {failure}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
