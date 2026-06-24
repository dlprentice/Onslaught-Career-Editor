#!/usr/bin/env python3
"""Validate the saved destructable vtable-tail Ghidra boundary tranche."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


DEFAULT_ROOT = Path("subagents/ghidra-static-reaudit/destructable-vtable-tail-wave353/current")
OUTPUT_NAME = "destructable-vtable-tail-boundary-tranche.json"

COMMON_TAGS = {
    "static-reaudit",
    "destructable-vtable-tail-wave353",
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
    "0x00442960": target(
        "CDestroyableSegment__VFunc_03_ApplyDamage",
        "void __thiscall CDestroyableSegment__VFunc_03_ApplyDamage(void * this, float damageAmount, void * sourceThing)",
        ["base vtable slot 3", "records last damage", "sourceThing", "remain unproven"],
        ["damageAmount", "+ 0x18", "+ 0x14"],
        ["function-boundary", "vtable-slot", "damage"],
    ),
    "0x0055df1f": target(
        "CRT__Purecall_0055df1f",
        "void __cdecl CRT__Purecall_0055df1f(void)",
        ["purecall-style CRT handler", "__amsg_exit", "0x19", "remain unproven"],
        ["__amsg_exit", "0x19"],
        ["function-boundary", "crt", "purecall"],
    ),
    "0x00442b00": target(
        "CDestroyableSegment__VFunc_06_CheckParentBreakGate",
        "int __fastcall CDestroyableSegment__VFunc_06_CheckParentBreakGate(void * this)",
        ["vtable slot 6", "parent segment", "slot +0x18", "remain unproven"],
        ["parentSegment", "+ 0x18"],
        ["function-boundary", "vtable-slot", "parent-gate"],
    ),
    "0x004bfc60": target(
        "SharedVFunc__ReturnFloatZero_004bfc60",
        "float __thiscall SharedVFunc__ReturnFloatZero_004bfc60(void * this)",
        ["shared vtable target", "returns float zero", "broad unrelated", "remain unproven"],
        ["return", "0.0"],
        ["function-boundary", "shared-vfunc", "return-float-zero"],
    ),
    "0x00405ee0": target(
        "SharedVFunc__Return3_00405ee0",
        "int __thiscall SharedVFunc__Return3_00405ee0(void * this)",
        ["shared vtable target", "returns 3", "segment-type", "remain unproven"],
        ["return", "3"],
        ["function-boundary", "shared-vfunc", "return-3"],
    ),
    "0x004059c0": target(
        "SharedVFunc__Return2_004059c0",
        "int __thiscall SharedVFunc__Return2_004059c0(void * this)",
        ["shared vtable target", "returns 2", "segment-type", "remain unproven"],
        ["return", "2"],
        ["function-boundary", "shared-vfunc", "return-2"],
    ),
    "0x004014a0": target(
        "SharedVFunc__Return1_004014a0",
        "int __thiscall SharedVFunc__Return1_004014a0(void * this)",
        ["shared vtable target", "returns 1", "segment-type", "remain unproven"],
        ["return", "1"],
        ["function-boundary", "shared-vfunc", "return-1"],
    ),
    "0x004436d0": target(
        "CDestroyableCoreSegment__VFunc_00_HandleEvent3000And3002Dispatch",
        "void __thiscall CDestroyableCoreSegment__VFunc_00_HandleEvent3000And3002Dispatch(void * this, void * eventRecord)",
        ["core vtable slot 0", "eventRecord code 3000/0x0bb8 and 3002/0x0bba", "fields +0x48/+0x44", "remain unproven"],
        ["eventRecord", "3002", "+ 0x48"],
        ["function-boundary", "vtable-slot", "event-3000", "event-3002"],
    ),
    "0x004435c0": target(
        "CDestroyableCoreSegment__VFunc_06_CheckParentBreakGate",
        "int __fastcall CDestroyableCoreSegment__VFunc_06_CheckParentBreakGate(void * this)",
        ["core vtable slot 6", "field +0x4c", "parent vtable slot +0x18", "remain unproven"],
        ["+ 0x4c", "+ 0x18"],
        ["function-boundary", "vtable-slot", "parent-gate", "core-segment"],
    ),
    "0x004434c0": target(
        "CDestroyableCoreSegment__VFunc_07_GetCoreField48",
        "float __fastcall CDestroyableCoreSegment__VFunc_07_GetCoreField48(void * this)",
        ["core vtable slot 7", "returns the float at this+0x48", "remain unproven"],
        ["+ 0x48"],
        ["function-boundary", "vtable-slot", "core-field-reader"],
    ),
    "0x00443660": target(
        "CDestroyableCoreSegment__VFunc_08_HandleCoreBreakOrCascade",
        "void __fastcall CDestroyableCoreSegment__VFunc_08_HandleCoreBreakOrCascade(void * this)",
        ["core vtable slot 8", "event 3002", "field +0x4c", "remain unproven"],
        ["3002", "+ 0x4c", "CDestroyableSegment__VFunc_08_HandleSegmentBreak"],
        ["function-boundary", "vtable-slot", "core-break"],
    ),
    "0x00443590": target(
        "CDestroyableCoreSegment__VFunc_11_RecomputeCoreDamageScaleFields",
        "void __thiscall CDestroyableCoreSegment__VFunc_11_RecomputeCoreDamageScaleFields(void * this, float scaleFactor, float divisor)",
        ["core vtable slot 11", "fields +0x0c/+0x10", "field +0x40", "remain unproven"],
        ["scaleFactor", "divisor", "+ 0x40"],
        ["function-boundary", "vtable-slot", "damage-scale"],
    ),
    "0x00442d40": target(
        "CDestroyableSegment__VFunc_09_UpdatePickupAndChildSlot09",
        "void __fastcall CDestroyableSegment__VFunc_09_UpdatePickupAndChildSlot09(void * this)",
        ["shared vtable slot 9", "configured pickup", "child slot 9", "remain unproven"],
        ["CDestroyableSegment__SpawnConfiguredPickup", "+ 0x24"],
        ["function-boundary", "vtable-slot", "pickup", "child-recursion"],
    ),
    "0x00442870": target(
        "CDestroyableSegment__VFunc_11_RecomputeDamageScaleFields",
        "void __thiscall CDestroyableSegment__VFunc_11_RecomputeDamageScaleFields(void * this, float scaleFactor, float divisor)",
        ["shared vtable slot 11", "fields +0x0c/+0x10", "this+0x34", "remain unproven"],
        ["scaleFactor", "divisor", "+ 0x34"],
        ["function-boundary", "vtable-slot", "damage-scale"],
    ),
    "0x00443ea0": target(
        "CDestroyableSegmentComponent__VFunc_08_HandleComponentBreak",
        "void __fastcall CDestroyableSegmentComponent__VFunc_08_HandleComponentBreak(void * this)",
        ["component vtable slot 8", "field +0x38", "owner callback", "remain unproven"],
        ["+ 0x38", "+ 0xc8"],
        ["function-boundary", "vtable-slot", "component-break"],
    ),
    "0x00443a20": target(
        "CDestroyableEndSegment__VFunc_10_SpawnEndRubbleEffects",
        "void __fastcall CDestroyableEndSegment__VFunc_10_SpawnEndRubbleEffects(void * this)",
        ["end-segment vtable slot 10", "calls the base rubble/effects path", "extra end-segment effect setup", "remain unproven"],
        ["CDestroyableSegment__VFunc_10_SpawnRubbleEffects", "Generic Mesh", "+ 0x50"],
        ["function-boundary", "vtable-slot", "rubble", "end-segment"],
    ),
    "0x004439f0": target(
        "CDestroyableEndSegment__VFunc_11_RecomputeEndDamageScaleFields",
        "void __thiscall CDestroyableEndSegment__VFunc_11_RecomputeEndDamageScaleFields(void * this, float scaleFactor, float divisor)",
        ["end-segment vtable slot 11", "controller component-count context", "fields +0x0c/+0x10", "remain unproven"],
        ["scaleFactor", "divisor", "+ 0x20"],
        ["function-boundary", "vtable-slot", "damage-scale", "end-segment"],
    ),
}


XREF_EVIDENCE = [
    ("0x00442960", "0x005db038", "DATA"),
    ("0x0055df1f", "0x005db040", "DATA"),
    ("0x00442b00", "0x005db044", "DATA"),
    ("0x004bfc60", "0x005db048", "DATA"),
    ("0x004436d0", "0x005db06c", "DATA"),
    ("0x004435c0", "0x005db084", "DATA"),
    ("0x004434c0", "0x005db088", "DATA"),
    ("0x00443660", "0x005db08c", "DATA"),
    ("0x00443ea0", "0x005db0cc", "DATA"),
    ("0x00443a20", "0x005db108", "DATA"),
]

INSTRUCTION_EVIDENCE = [
    ("0x00442960", "0x00442980", "MOV", "[ECX + 0x18]"),
    ("0x0055df1f", "0x0055df21", "CALL", "0x00560289"),
    ("0x00442b00", "0x00442b10", "JMP", "[EAX + 0x18]"),
    ("0x004bfc60", "0x004bfc60", "FLD", "0x005d856c"),
    ("0x00405ee0", "0x00405ee0", "MOV", "0x3"),
    ("0x004059c0", "0x004059c0", "MOV", "0x2"),
    ("0x004014a0", "0x004014a0", "MOV", "0x1"),
    ("0x004436d0", "0x004436db", "CMP", "0xbba"),
    ("0x004435c0", "0x004435c0", "MOV", "[ECX + 0x4c]"),
    ("0x004434c0", "0x004434c0", "FLD", "[ECX + 0x48]"),
    ("0x00443660", "0x004436ab", "PUSH", "0xbba"),
    ("0x00443590", "0x004435b2", "FST", "[ECX + 0xc]"),
    ("0x00442d40", "0x00442f22", "CALL", "0x00442710"),
    ("0x00442870", "0x0044287b", "FST", "[ECX + 0xc]"),
    ("0x00443ea0", "0x00443ebf", "JMP", "[EAX + 0xc8]"),
    ("0x00443a20", "0x00443a43", "CALL", "0x00442f60"),
    ("0x004439f0", "0x00443a0f", "FST", "[ECX + 0xc]"),
]

VTABLE_EVIDENCE = [
    ("0x005db02c", "3", "0x005db038", "0x00442960", "0x00442960"),
    ("0x005db02c", "5", "0x005db040", "0x0055df1f", "0x0055df1f"),
    ("0x005db148", "5", "0x005db15c", "0x004014a0", "0x004014a0"),
    ("0x005db114", "5", "0x005db128", "0x004059c0", "0x004059c0"),
    ("0x005db0e0", "5", "0x005db0f4", "0x00405ee0", "0x00405ee0"),
    ("0x005db02c", "6", "0x005db044", "0x00442b00", "0x00442b00"),
    ("0x005db02c", "7", "0x005db048", "0x004bfc60", "0x004bfc60"),
    ("0x005db06c", "0", "0x005db06c", "0x004436d0", "0x004436d0"),
    ("0x005db06c", "6", "0x005db084", "0x004435c0", "0x004435c0"),
    ("0x005db06c", "7", "0x005db088", "0x004434c0", "0x004434c0"),
    ("0x005db06c", "8", "0x005db08c", "0x00443660", "0x00443660"),
    ("0x005db06c", "11", "0x005db098", "0x00443590", "0x00443590"),
    ("0x005db148", "9", "0x005db16c", "0x00442d40", "0x00442d40"),
    ("0x005db148", "11", "0x005db174", "0x00442870", "0x00442870"),
    ("0x005db0ac", "8", "0x005db0cc", "0x00443ea0", "0x00443ea0"),
    ("0x005db0e0", "10", "0x005db108", "0x00443a20", "0x00443a20"),
    ("0x005db0e0", "11", "0x005db10c", "0x004439f0", "0x004439f0"),
]

STALE_TOKENS = ["<none>", "<no_function>", "MISSING", "undefined ", "param_"]
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
    return any(
        normalize_address(row.get("target_addr", "")) == target_norm
        and normalize_address(row.get("from_addr", "")) == source_norm
        and row.get("ref_type", "") == ref_type
        for row in rows
    )


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
        if not operand_token or token_present(row.get("operands", ""), operand_token):
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
    dry_log_path = dry_log_path or root / "destructable_vtable_tail_boundary_dry.log"
    apply_log_path = apply_log_path or root / "destructable_vtable_tail_boundary_apply.log"
    metadata_path = metadata_path or root / "metadata_after.tsv"
    tags_path = tags_path or root / "tags_after.tsv"
    xrefs_path = xrefs_path or root / "xrefs_after.tsv"
    instructions_path = instructions_path or root / "instructions_after.tsv"
    vtable_path = vtable_path or root / "vtable_slots_full_after.tsv"
    decompile_dir = decompile_dir or root / "decompile_after"

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
        if row.get("status") != "OK":
            failures.append(f"{address} metadata status {row.get('status')} != OK")
        if row.get("name") != spec["name"]:
            failures.append(f"{address} name {row.get('name')} != {spec['name']}")
        if row.get("signature") != spec["signature"]:
            failures.append(f"{address} signature mismatch: {row.get('signature')} != {spec['signature']}")

        combined = row.get("name", "") + " " + row.get("signature", "")
        for stale in STALE_TOKENS:
            if stale in combined:
                stale_hits += 1
                failures.append(f"{address} stale token in signature/name: {stale}")

        comment = row.get("comment", "")
        for token in spec["commentTokens"]:
            if not token_present(comment, str(token)):
                failures.append(f"{address} missing comment token: {token}")
        for overclaim in OVERCLAIM_TOKENS:
            if token_present(comment, overclaim):
                comment_overclaims += 1
                failures.append(f"{address} comment overclaim token: {overclaim}")

        tag_row = tags_by_addr.get(normalize_address(address))
        if not tag_row or tag_row.get("status") != "OK":
            failures.append(f"{address} missing tag row")
        else:
            expected_tags = COMMON_TAGS | set(spec["tags"])
            actual_tags = split_tags(tag_row.get("tags", ""))
            missing_tags = sorted(expected_tags - actual_tags)
            if missing_tags:
                failures.append(f"{address} missing tags: {missing_tags}")

        decompile_path = decompile_file_for(decompile_dir, address)
        if decompile_path is None:
            failures.append(f"{address} missing decompile file")
            continue
        decompile_text = read_text(decompile_path)
        if spec["name"] not in decompile_text:
            failures.append(f"{address} decompile missing function name")
        for token in spec["decompileTokens"]:
            if not token_present(decompile_text, str(token)):
                failures.append(f"{address} missing decompile token: {token}")
        decompile_hits += 1

    xref_hits = 0
    for evidence in XREF_EVIDENCE:
        if xref_match(xrefs, *evidence):
            xref_hits += 1
        else:
            failures.append(f"missing xref evidence: {evidence}")

    instruction_hits = 0
    for evidence in INSTRUCTION_EVIDENCE:
        if instruction_match(instructions, *evidence):
            instruction_hits += 1
        else:
            failures.append(f"missing instruction evidence: {evidence}")

    vtable_hits = 0
    for evidence in VTABLE_EVIDENCE:
        if vtable_match(vtables, evidence):
            vtable_hits += 1
        else:
            failures.append(f"missing vtable evidence: {evidence}")

    report = {
        "status": "PASS" if not failures else "FAIL",
        "summary": {
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
            "commentOverclaimHits": comment_overclaims,
            "drySummary": dry_summary,
            "applySummary": apply_summary,
        },
        "failures": failures,
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    report = build_report(root=args.root)
    out_path = args.root / OUTPUT_NAME
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], sort_keys=True))
    print(f"status={report['status']} output={out_path}")
    if args.check and report["status"] != "PASS":
        for failure in report["failures"]:
            print(f"FAIL: {failure}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
