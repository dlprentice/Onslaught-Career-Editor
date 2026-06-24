#!/usr/bin/env python3
"""Validate the saved destructable bridge Ghidra signature/boundary tranche."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


DEFAULT_ROOT = Path("subagents/ghidra-static-reaudit/destructable-bridge-wave351/current")
OUTPUT_NAME = "destructable-bridge-signature-boundary-tranche.json"

COMMON_TAGS = {
    "static-reaudit",
    "destructable-bridge-wave351",
    "destructable-segments",
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
    "0x00444620": target(
        "CDestructableSegmentsController__SetAllSegmentsActiveFlagAndRefreshMetric",
        "void __thiscall CDestructableSegmentsController__SetAllSegmentsActiveFlagAndRefreshMetric(void * this, int activeFlag)",
        ["Bulk controller active-flag helper", "segment field +0x1c", "older CExplosionInitThing owner label", "remain unproven"],
        ["activeFlag", "CDestroyableSegment__SumActiveValueRecursive", "0x1c"],
        ["owner-correction", "bulk-setter", "active-flag", "cache-refresh", "signature-correction"],
    ),
    "0x00444940": target(
        "CDestroyableSegmentComponent__scalar_deleting_dtor",
        "void * __thiscall CDestroyableSegmentComponent__scalar_deleting_dtor(void * this, int flags)",
        ["Component scalar-deleting destructor wrapper", "flags bit 0", "returns this", "remain unproven"],
        ["CDestroyableSegmentComponent__dtor_base", "OID__FreeObject", "flags"],
        ["destructor", "vtable-slot", "signature-correction"],
    ),
    "0x00444960": target(
        "CDestroyableSegmentComponent__dtor_base",
        "void __fastcall CDestroyableSegmentComponent__dtor_base(void * this)",
        ["Component destructor body", "owner-link cell", "0x00442660", "remain unproven"],
        ["CSPtrSet__Remove", "0x40", "CDestroyableSegment__dtor_base"],
        ["destructor", "owner-link", "signature-correction"],
    ),
    "0x00444be0": target(
        "CDestroyableSegmentVariant__scalar_deleting_dtor",
        "void * __thiscall CDestroyableSegmentVariant__scalar_deleting_dtor(void * this, int flags)",
        ["Recovered shared scalar-deleting destructor boundary", "0x005db0e4", "0x005db118", "0x005db14c", "remain unproven"],
        ["CDestroyableSegment__dtor_base_thunk", "OID__FreeObject", "flags"],
        ["function-boundary", "destructor", "vtable-slot", "shared-variant", "signature-correction"],
    ),
    "0x00444c00": target(
        "CDestroyableSegment__dtor_base_thunk",
        "void __fastcall CDestroyableSegment__dtor_base_thunk(void * this)",
        ["Small tail thunk", "canonical CDestroyableSegment__dtor_base body", "0x00442660", "remain unproven"],
        ["CSPtrSet__Remove", "CMonitor__Shutdown"],
        ["destructor", "thunk", "name-correction", "signature-correction"],
    ),
}

XREF_EVIDENCE = [
    ("0x00444620", "0x005343b7", "UNCONDITIONAL_CALL"),
    ("0x00444940", "0x005db0b0", "DATA"),
    ("0x00444960", "0x00444943", "UNCONDITIONAL_CALL"),
    ("0x00444be0", "0x005db14c", "DATA"),
    ("0x00444be0", "0x005db118", "DATA"),
    ("0x00444be0", "0x005db0e4", "DATA"),
    ("0x00444c00", "0x00444be3", "UNCONDITIONAL_CALL"),
]

INSTRUCTION_EVIDENCE = [
    ("0x00444620", "0x0044463a", "MOV", "[EAX + 0x1c]"),
    ("0x00444620", "0x0044464c", "CALL", "0x00442890"),
    ("0x00444620", "0x00444655", "RET", "0x4"),
    ("0x00444940", "0x00444943", "CALL", "0x00444960"),
    ("0x00444960", "0x004449a8", "CALL", "0x00442660"),
    ("0x00444be0", "0x00444be3", "CALL", "0x00444c00"),
    ("0x00444be0", "0x00444bfd", "RET", "0x4"),
    ("0x00444c00", "0x00444c00", "JMP", "0x00442660"),
]

VTABLE_EVIDENCE = [
    ("0x005db0ac", "1", "0x005db0b0", "0x00444940", "0x00444940"),
    ("0x005db0e0", "1", "0x005db0e4", "0x00444be0", "0x00444be0"),
    ("0x005db114", "1", "0x005db118", "0x00444be0", "0x00444be0"),
    ("0x005db148", "1", "0x005db14c", "0x00444be0", "0x00444be0"),
]

STALE_TOKENS = [
    "undefined ",
    "param_",
    "CExplosionInitThing__SetChildStateAndRefreshSegmentMetric",
    "CDestroyableSegmentComponent__VFunc_01_00444940",
    "CDestroyableSegmentComponent__RemoveOwnerLinkAndResetBase",
]

OVERCLAIM_TOKENS = [
    "runtime destruction behavior proven",
    "source identity proven",
    "exact class layout proven",
    "rebuild parity proven",
]


def normalize_address(value: str) -> str:
    value = (value or "").strip().lower()
    if value in {"", "<none>", "<no_function>"}:
        return value
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def compact(value: str) -> str:
    return "".join((value or "").lower().split())


def token_present(text: str, token: str) -> bool:
    return compact(token) in compact(text)


def split_tags(value: str) -> set[str]:
    return {tag.strip() for tag in re.split(r"[;,]", value or "") if tag.strip()}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def decompile_file_for(decompile_dir: Path, address: str) -> Path | None:
    if not decompile_dir.is_dir():
        return None
    matches = sorted(decompile_dir.glob(f"{normalize_address(address)[2:]}_*.c"))
    return matches[0] if matches else None


def parse_summary(log_text: str) -> dict[str, int]:
    match = re.search(r"targets=(\d+)\s+changed_or_would_change=(\d+)\s+failed=(\d+)", log_text)
    if not match:
        return {"targets": -1, "changed": -1, "failed": -1}
    return {"targets": int(match.group(1)), "changed": int(match.group(2)), "failed": int(match.group(3))}


def xref_match(rows: list[dict[str, str]], target: str, source: str, ref_type: str) -> bool:
    target_norm = normalize_address(target)
    source_norm = normalize_address(source)
    for row in rows:
        if (
            normalize_address(row.get("target_addr", "")) == target_norm
            and normalize_address(row.get("from_addr", "")) == source_norm
            and row.get("ref_type", "") == ref_type
        ):
            return True
    return False


def instruction_match(rows: list[dict[str, str]], target: str, addr: str, mnemonic: str, operand_token: str) -> bool:
    target_norm = normalize_address(target)
    addr_norm = normalize_address(addr)
    for row in rows:
        if normalize_address(row.get("target_addr", "")) != target_norm:
            continue
        if normalize_address(row.get("instruction_addr", "")) != addr_norm:
            continue
        if (row.get("mnemonic", "") or "").upper() != mnemonic:
            continue
        if token_present(row.get("operands", ""), operand_token):
            return True
    return False


def vtable_match(rows: list[dict[str, str]], evidence: tuple[str, str, str, str, str]) -> bool:
    vtable, slot, slot_addr, pointer_raw, pointer_addr = evidence
    for row in rows:
        if (
            normalize_address(row.get("vtable", "")) == normalize_address(vtable)
            and row.get("slot_index", "") == slot
            and normalize_address(row.get("slot_addr", "")) == normalize_address(slot_addr)
            and normalize_address(row.get("pointer_raw", "")) == normalize_address(pointer_raw)
            and normalize_address(row.get("pointer_addr", "")) == normalize_address(pointer_addr)
            and row.get("status", "") == "OK"
        ):
            return True
    return False


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
    decompile_dir: Path | None = None,
) -> dict[str, object]:
    root = Path(root)
    dry_log_path = dry_log_path or root / "destructable_bridge_dry.log"
    apply_log_path = apply_log_path or root / "destructable_bridge_apply.log"
    metadata_path = metadata_path or root / "metadata_final.tsv"
    tags_path = tags_path or root / "tags_final.tsv"
    xrefs_path = xrefs_path or root / "xrefs_final.tsv"
    instructions_path = instructions_path or root / "instructions_final.tsv"
    vtable_path = vtable_path or root / "vtable_slots_final.tsv"
    decompile_dir = decompile_dir or root / "decompile_final"

    failures: list[str] = []
    metadata = read_tsv(metadata_path)
    tags = read_tsv(tags_path)
    xrefs = read_tsv(xrefs_path)
    instructions = read_tsv(instructions_path)
    vtables = read_tsv(vtable_path)
    dry_summary = parse_summary(read_text(dry_log_path))
    apply_summary = parse_summary(read_text(apply_log_path))

    if dry_summary["targets"] != len(TARGETS) or dry_summary["failed"] != 0:
        failures.append(f"dry-run summary unexpected: {dry_summary}")
    if apply_summary["targets"] != len(TARGETS) or apply_summary["failed"] != 0:
        failures.append(f"apply summary unexpected: {apply_summary}")

    metadata_by_addr = {normalize_address(row.get("address", "")): row for row in metadata}
    tags_by_addr = {normalize_address(row.get("address", "")): row for row in tags}

    decompile_hits = 0
    stale_hits = 0
    comment_overclaims = 0
    for address, spec in TARGETS.items():
        row = metadata_by_addr.get(normalize_address(address))
        if not row:
            failures.append(f"missing metadata row for {address}")
            continue
        if row.get("name") != spec["name"]:
            failures.append(f"{address} name {row.get('name')} != {spec['name']}")
        if row.get("signature") != spec["signature"]:
            failures.append(f"{address} signature mismatch: {row.get('signature')} != {spec['signature']}")
        combined = row.get("name", "") + " " + row.get("signature", "")
        for stale in STALE_TOKENS:
            if stale in combined:
                stale_hits += 1
                failures.append(f"{address} stale token remains: {stale}")

        comment = row.get("comment", "")
        for token in spec["commentTokens"]:
            if not token_present(comment, str(token)):
                failures.append(f"{address} comment missing token: {token}")
        for token in OVERCLAIM_TOKENS:
            if token_present(comment, token):
                comment_overclaims += 1
                failures.append(f"{address} comment overclaim token: {token}")

        tag_row = tags_by_addr.get(normalize_address(address))
        if not tag_row:
            failures.append(f"missing tags row for {address}")
        else:
            expected_tags = COMMON_TAGS | set(spec["tags"])
            actual_tags = split_tags(tag_row.get("tags", ""))
            missing = sorted(expected_tags - actual_tags)
            if missing:
                failures.append(f"{address} missing tags: {missing}")

        decompile_path = decompile_file_for(decompile_dir, address)
        if not decompile_path:
            failures.append(f"missing decompile file for {address}")
        else:
            decompile_text = read_text(decompile_path)
            missing_tokens = [str(token) for token in spec["decompileTokens"] if not token_present(decompile_text, str(token))]
            if missing_tokens:
                failures.append(f"{address} decompile missing tokens: {missing_tokens}")
            else:
                decompile_hits += 1

    xref_hits = 0
    for target_addr, source_addr, ref_type in XREF_EVIDENCE:
        if xref_match(xrefs, target_addr, source_addr, ref_type):
            xref_hits += 1
        else:
            failures.append(f"missing xref evidence: {target_addr} <- {source_addr} {ref_type}")

    instruction_hits = 0
    for target_addr, instruction_addr, mnemonic, operand_token in INSTRUCTION_EVIDENCE:
        if instruction_match(instructions, target_addr, instruction_addr, mnemonic, operand_token):
            instruction_hits += 1
        else:
            failures.append(f"missing instruction evidence: {target_addr} {instruction_addr} {mnemonic} {operand_token}")

    vtable_hits = 0
    for evidence in VTABLE_EVIDENCE:
        if vtable_match(vtables, evidence):
            vtable_hits += 1
        else:
            failures.append(f"missing vtable evidence: {evidence}")

    summary = {
        "targets": len(TARGETS),
        "metadataRows": len(metadata),
        "tagRows": len(tags),
        "xrefRows": len(xrefs),
        "instructionRows": len(instructions),
        "vtableRows": len(vtables),
        "decompileHits": decompile_hits,
        "xrefEvidenceHits": xref_hits,
        "instructionEvidenceHits": instruction_hits,
        "vtableEvidenceHits": vtable_hits,
        "staleTokenHits": stale_hits,
        "commentOverclaims": comment_overclaims,
    }
    status = "PASS" if not failures else "FAIL"
    return {"status": status, "summary": summary, "failures": failures}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    report = build_report(root=args.root)
    args.root.mkdir(parents=True, exist_ok=True)
    out_path = args.root / OUTPUT_NAME
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {out_path}")
    print(json.dumps(report["summary"], sort_keys=True))
    if args.check and report["status"] != "PASS":
        for failure in report["failures"]:
            print(f"FAIL: {failure}")
        return 1
    print(report["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
