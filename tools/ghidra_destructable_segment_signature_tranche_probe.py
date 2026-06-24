#!/usr/bin/env python3
"""Validate the saved destructable-segment Ghidra signature/comment tranche."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


DEFAULT_ROOT = Path("subagents/ghidra-static-reaudit/destructable-segment-wave348/current")
OUTPUT_NAME = "destructable-segment-signature-tranche.json"

COMMON_TAGS = {"static-reaudit", "destructable-segment-wave348", "destructable-segments", "retail-binary-evidence"}


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
    "0x004425a0": target(
        "CDestructableSegment__Init",
        "void * __thiscall CDestructableSegment__Init(void * this, void * controller, int segmentIndex, void * parentSegment, float segmentValue)",
        ["Base destructable-segment initializer", "DAT_00855180", "remain unproven"],
        ["CSPtrSet__Init", "CSPtrSet__AddToHead", "DAT_00855180"],
        ["init", "base-segment"],
    ),
    "0x00442640": target(
        "CDestroyableSegment__scalar_deleting_dtor",
        "void * __thiscall CDestroyableSegment__scalar_deleting_dtor(void * this, int flags)",
        ["Scalar-deleting destructor wrapper", "OID__FreeObject", "flags bit 0", "remain unproven"],
        ["CDestroyableSegment__dtor_base", "OID__FreeObject"],
        ["destructor", "vtable-slot", "name-correction"],
    ),
    "0x00442660": target(
        "CDestroyableSegment__dtor_base",
        "void __fastcall CDestroyableSegment__dtor_base(void * this)",
        ["Destructor body", "DAT_00855180", "CMonitor__Shutdown", "remain unproven"],
        ["CSPtrSet__Remove", "DAT_00855180", "CMonitor__Shutdown"],
        ["destructor", "name-correction"],
    ),
    "0x00442700": target(
        "CDestructableSegment__RegisterChild",
        "void __thiscall CDestructableSegment__RegisterChild(void * this, void * childSegment)",
        ["Registers a child segment", "this+0x24", "global monitor membership", "remain unproven"],
        ["CSPtrSet__AddToHead"],
        ["child-list", "name-correction"],
    ),
    "0x00442710": target(
        "CDestroyableSegment__SpawnConfiguredPickup",
        "int __fastcall CDestroyableSegment__SpawnConfiguredPickup(void * this)",
        ["configured pickup", "config+0xe8", "stale CExplosionInitThing", "remain unproven"],
        ["CWorldPhysicsManager__CreatePickup", "CInfluenceMap__Init"],
        ["pickup", "name-correction"],
    ),
    "0x00442890": target(
        "CDestroyableSegment__SumActiveValueRecursive",
        "float __thiscall CDestroyableSegment__SumActiveValueRecursive(void * this)",
        ["Recursively sums", "this+0x10", "child list", "remain unproven"],
        ["CDestroyableSegment__SumActiveValueRecursive"],
        ["recursive-sum", "health-metric"],
    ),
    "0x00442900": target(
        "CDestructableSegment__GetTotalHealth",
        "float __fastcall CDestructableSegment__GetTotalHealth(void * this)",
        ["Recursively sums total", "this+0x0c", "controller initialization", "remain unproven"],
        ["CDestructableSegment__GetTotalHealth"],
        ["recursive-sum", "health-metric"],
    ),
    "0x004429a0": target(
        "CDestructableSegment__DispatchChildDestructionEvents",
        "void __fastcall CDestructableSegment__DispatchChildDestructionEvents(void * this)",
        ["event 3000", "randomized delay", "remain unproven"],
        ["CEventManager__AddEvent_AtTime", "3000"],
        ["child-events", "event-3000"],
    ),
    "0x00442a80": target(
        "CDestructableSegment__SetSubtreeActiveFlagRecursive",
        "void __fastcall CDestructableSegment__SetSubtreeActiveFlagRecursive(void * this)",
        ["active flag", "this+0x1c", "remain unproven"],
        ["CDestructableSegment__SetSubtreeActiveFlagRecursive"],
        ["recursive", "active-flag"],
    ),
    "0x00442ac0": target(
        "CDestructableSegment__PropagateDamageToChildren",
        "void __thiscall CDestructableSegment__PropagateDamageToChildren(void * this, int damageArg, int unusedArg)",
        ["damage-style vfunc", "slot +0x0c", "second stack argument", "remain unproven"],
        ["0xc"],
        ["child-damage", "vtable-slot"],
    ),
    "0x00442b20": target(
        "CDestroyableSegment__VFunc_08_HandleSegmentBreak",
        "void __fastcall CDestroyableSegment__VFunc_08_HandleSegmentBreak(void * this)",
        ["vfunc slot 8", "marks the segment broken", "linked segment entries", "remain unproven"],
        ["CUnit__FinalizeLinkedUnitStateAndClear", "CDestroyableSegment__RemoveLinkedSegmentAndRelease", "CDestructableSegment__DispatchChildDestructionEvents"],
        ["break-handler", "vtable-slot", "name-correction"],
    ),
    "0x00442f60": target(
        "CDestroyableSegment__VFunc_10_SpawnRubbleEffects",
        "void __fastcall CDestroyableSegment__VFunc_10_SpawnRubbleEffects(void * this)",
        ["vfunc slot 10", "rubble/effects path", "configured pickup", "remain unproven"],
        ["Generic_Mesh", "CParticleManager__CreateEffect", "CDXEngine__ApplyLandscapeDamageStamp", "CDestroyableSegment__SpawnConfiguredPickup"],
        ["rubble", "particle-effects", "vtable-slot", "name-correction"],
    ),
}

STALE_TOKENS = [
    "ctor_like",
    "VFuncSlot_10_00442f60",
    "CDestroyableSegment__VFunc_08_00442b20",
    "CDestroyableSegment__VFunc_01_00442640",
    "CExplosionInitThing__ctor_like_00442710",
    "param_",
    "undefined ",
]
OVERCLAIM_TOKENS = [
    "runtime behavior proven",
    "source identity proven",
    "exact class layout proven",
    "rebuild parity proven",
]

EXPECTED_VTABLE_SLOTS = [
    ("0x005db02c", "1", "CDestroyableSegment__scalar_deleting_dtor"),
    ("0x005db02c", "8", "CDestroyableSegment__VFunc_08_HandleSegmentBreak"),
    ("0x005db02c", "10", "CDestroyableSegment__VFunc_10_SpawnRubbleEffects"),
    ("0x005db06c", "10", "CDestroyableSegment__VFunc_10_SpawnRubbleEffects"),
    ("0x005db114", "10", "CDestroyableSegment__VFunc_10_SpawnRubbleEffects"),
    ("0x005db148", "10", "CDestroyableSegment__VFunc_10_SpawnRubbleEffects"),
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


def build_report(
    *,
    root: Path = DEFAULT_ROOT,
    dry_log_path: Path | None = None,
    apply_log_path: Path | None = None,
    metadata_path: Path | None = None,
    tags_path: Path | None = None,
    xrefs_path: Path | None = None,
    vtable_slots_path: Path | None = None,
    instructions_path: Path | None = None,
    decompile_dir: Path | None = None,
    caller_decompile_dir: Path | None = None,
) -> dict[str, object]:
    root = Path(root)
    dry_log_path = dry_log_path or root / "destructable_segment_dry.log"
    apply_log_path = apply_log_path or root / "destructable_segment_apply.log"
    metadata_path = metadata_path or root / "metadata_final.tsv"
    tags_path = tags_path or root / "tags_final.tsv"
    xrefs_path = xrefs_path or root / "xrefs_final.tsv"
    vtable_slots_path = vtable_slots_path or root / "vtable_slots_final.tsv"
    instructions_path = instructions_path or root / "instructions_final.tsv"
    decompile_dir = decompile_dir or root / "decompile_final"
    caller_decompile_dir = caller_decompile_dir or root / "caller_decompile_final"

    failures: list[str] = []
    metadata = read_tsv(metadata_path)
    tags = read_tsv(tags_path)
    xrefs = read_tsv(xrefs_path)
    vtable_slots = read_tsv(vtable_slots_path)
    instructions = read_tsv(instructions_path)
    dry_summary = parse_summary(read_text(dry_log_path))
    apply_summary = parse_summary(read_text(apply_log_path))

    if dry_summary["targets"] != len(TARGETS) or dry_summary["failed"] != 0:
        failures.append(f"dry-run summary unexpected: {dry_summary}")
    if apply_summary["targets"] != len(TARGETS) or apply_summary["failed"] != 0:
        failures.append(f"apply summary unexpected: {apply_summary}")

    metadata_by_addr = {normalize_address(row.get("address", "")): row for row in metadata}
    tags_by_addr = {normalize_address(row.get("address", "")): row for row in tags}

    decompile_hits = 0
    comment_overclaims = 0
    stale_hits = 0
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
            missing = [token for token in spec["decompileTokens"] if not token_present(decompile_text, str(token))]
            if missing:
                failures.append(f"{address} decompile missing tokens: {missing}")
            else:
                decompile_hits += 1

    vtable_hits = 0
    for vtable, slot, name in EXPECTED_VTABLE_SLOTS:
        hit = any(
            normalize_address(row.get("vtable", "")) == normalize_address(vtable)
            and row.get("slot_index") == slot
            and row.get("function_name") == name
            and row.get("status") == "OK"
            for row in vtable_slots
        )
        if hit:
            vtable_hits += 1
        else:
            failures.append(f"missing vtable evidence: {vtable} slot {slot} -> {name}")

    xref_targets = {normalize_address(row.get("target_addr", "")) for row in xrefs}
    for address in TARGETS:
        if normalize_address(address) not in xref_targets:
            failures.append(f"missing xref row for {address}")

    ret_evidence = {
        "0x004425a0": "0x10",
        "0x00442640": "0x4",
    }
    ret_hits = 0
    for address, operand in ret_evidence.items():
        hit = any(
            normalize_address(row.get("function_entry", "")) == normalize_address(address)
            and row.get("mnemonic") == "RET"
            and row.get("operands") == operand
            for row in instructions
        )
        if hit:
            ret_hits += 1
        else:
            failures.append(f"missing RET {operand} evidence for {address}")

    caller_text = "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in sorted(caller_decompile_dir.glob("*.c"))) if caller_decompile_dir.is_dir() else ""
    for token in ["CDestructableSegmentsController__CreateSegment", "CDestructableSegmentsController__ProcessNode", "CDestructableSegment__RegisterChild"]:
        if not token_present(caller_text, token):
            failures.append(f"caller decompile missing token: {token}")

    return {
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "summary": {
            "targets": len(TARGETS),
            "metadataRows": len(metadata),
            "tagRows": len(tags),
            "xrefRows": len(xrefs),
            "instructionRows": len(instructions),
            "decompileHits": decompile_hits,
            "vtableEvidenceHits": vtable_hits,
            "retEvidenceHits": ret_hits,
            "commentOverclaims": comment_overclaims,
            "staleTokenHits": stale_hits,
            "drySummary": dry_summary,
            "applySummary": apply_summary,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report(root=args.root)
    args.root.mkdir(parents=True, exist_ok=True)
    (args.root / OUTPUT_NAME).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    if args.check and report["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
