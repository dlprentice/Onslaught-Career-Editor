#!/usr/bin/env python3
"""Validate the saved destructable-controller Ghidra signature/comment tranche."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


DEFAULT_ROOT = Path("subagents/ghidra-static-reaudit/destructable-controller-wave349/current")
OUTPUT_NAME = "destructable-controller-signature-tranche.json"

COMMON_TAGS = {
    "static-reaudit",
    "destructable-controller-wave349",
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
    "0x004433f0": target(
        "CDestroyableCoreSegment__AreCoreChildrenDestroyed",
        "int __fastcall CDestroyableCoreSegment__AreCoreChildrenDestroyed(void * this)",
        ["Core-segment helper", "child CSPtrSet", "Corrects the older controller-owner label", "remain unproven"],
        ["CConsole__Printf", "Warning__First_core_part", "0x14"],
        ["core-segment", "child-state", "name-correction"],
    ),
    "0x00443480": target(
        "CDestroyableCoreSegment__Init",
        "void * __thiscall CDestroyableCoreSegment__Init(void * this, void * controller, int segmentIndex, void * parentSegment, float segmentValue, int coreComponentOrdinal)",
        ["Core/primary destroyable-segment initializer", "vtable 0x005db06c", "remain unproven"],
        ["CDestructableSegment__Init", "PTR_LAB_005db06c"],
        ["init", "core-segment", "name-correction"],
    ),
    "0x004434d0": target(
        "CDestroyableCoreSegment__scalar_deleting_dtor",
        "void * __thiscall CDestroyableCoreSegment__scalar_deleting_dtor(void * this, int flags)",
        ["Scalar-deleting destructor wrapper", "CDestroyableCoreSegment__dtor_base", "flags bit 0", "remain unproven"],
        ["CDestroyableCoreSegment__dtor_base", "OID__FreeObject"],
        ["destructor", "core-segment", "vtable-slot", "name-correction"],
    ),
    "0x004434f0": target(
        "CDestroyableCoreSegment__dtor_base",
        "void __fastcall CDestroyableCoreSegment__dtor_base(void * this)",
        ["Destructor body", "DAT_00855180", "CMonitor__Shutdown", "remain unproven"],
        ["CSPtrSet__Remove", "DAT_00855180", "CMonitor__Shutdown"],
        ["destructor", "core-segment", "name-correction"],
    ),
    "0x004435f0": target(
        "CDestroyableCoreSegment__VFunc_03_ApplyDamage",
        "void __thiscall CDestroyableCoreSegment__VFunc_03_ApplyDamage(void * this, float damageAmount, void * damageSource)",
        ["damage-style vfunc slot 3", "DAT_00672fd0", "damageSource argument", "remain unproven"],
        ["DAT_00672fd0", "0x28", "0x20"],
        ["damage", "core-segment", "vtable-slot", "name-correction"],
    ),
    "0x00443780": target(
        "CDestroyableSwapSegment__VFunc_03_ApplyDamage",
        "void __thiscall CDestroyableSwapSegment__VFunc_03_ApplyDamage(void * this, float damageAmount, void * damageSource)",
        ["Swap-segment damage-style vfunc slot 3", "slot 0x10", "child-destruction", "remain unproven"],
        ["CDestructableSegment__DispatchChildDestructionEvents", "DAT_00672fd0"],
        ["damage", "swap-segment", "vtable-slot", "name-correction"],
    ),
    "0x00443810": target(
        "CDestroyableSwapSegment__VFunc_08_HandleSegmentBreak",
        "void __fastcall CDestroyableSwapSegment__VFunc_08_HandleSegmentBreak(void * this)",
        ["Swap-segment vfunc slot 8", "field +0x44", "CDestroyableSegment__VFunc_08_HandleSegmentBreak", "remain unproven"],
        ["CDestroyableSegment__VFunc_08_HandleSegmentBreak"],
        ["break-handler", "swap-segment", "vtable-slot", "name-correction"],
    ),
    "0x004439c0": target(
        "CDestroyableSegment__SharedVFunc_08_HandleChildBreak",
        "void __fastcall CDestroyableSegment__SharedVFunc_08_HandleChildBreak(void * this)",
        ["Shared vfunc slot 8", "leaf/end segment vtables", "base segment break handler", "remain unproven"],
        ["CDestroyableSegment__VFunc_08_HandleSegmentBreak"],
        ["break-handler", "shared-vfunc", "vtable-slot", "name-correction"],
    ),
    "0x00443fc0": target(
        "CDestructableSegmentsController__Ctor",
        "void * __thiscall CDestructableSegmentsController__Ctor(void * this, void * field10Value, void * field14Value, void * field24Value, void * field28Value)",
        ["Controller constructor-like initializer", "fields +0x10/+0x14/+0x24/+0x28", "remain unproven"],
        ["field10Value", "field28Value"],
        ["ctor", "controller", "signature-correction"],
    ),
    "0x00444000": target(
        "CDestructableSegmentsController__Dtor",
        "void __fastcall CDestructableSegmentsController__Dtor(void * this)",
        ["Controller destructor helper", "segment-array", "root segment", "remain unproven"],
        ["OID__FreeObject"],
        ["destructor", "controller", "signature-correction"],
    ),
    "0x00444030": target(
        "CDestructableSegmentsController__DamageSegmentByIndexAndUpdateThreshold",
        "void __thiscall CDestructableSegmentsController__DamageSegmentByIndexAndUpdateThreshold(void * this, int segmentIndex, float damageAmount, void * damageSource)",
        ["Controller indexed damage path", "damage-style vfunc", "one-shot threshold flag", "remain unproven"],
        ["CDestroyableCoreSegment__AreCoreChildrenDestroyed", "CDestroyableSegment__SumActiveValueRecursive"],
        ["damage", "threshold", "controller", "signature-correction"],
    ),
    "0x00444160": target(
        "CDestructableSegmentsController__ApplyRandomDamageBurstAndUpdateThreshold",
        "void __fastcall CDestructableSegmentsController__ApplyRandomDamageBurstAndUpdateThreshold(void * this)",
        ["random-damage burst", "temporary CSPtrSet", "large damage value", "remain unproven"],
        ["CSPtrSet__Init", "Random__NextLCGAbs", "0x47c35000"],
        ["damage", "random-burst", "threshold", "controller"],
    ),
    "0x004442d0": target(
        "CDestructableSegmentsController__GetSegmentLastDamageTimeByIndex",
        "float __thiscall CDestructableSegmentsController__GetSegmentLastDamageTimeByIndex(void * this, int segmentIndex)",
        ["field +0x14", "DAT_00672fd0", "older field-only label", "remain unproven"],
        ["0x14"],
        ["getter", "damage", "controller", "name-correction"],
    ),
    "0x00444300": target(
        "CDestructableSegmentsController__GetSegmentLastDamageAmountByIndex",
        "float __thiscall CDestructableSegmentsController__GetSegmentLastDamageAmountByIndex(void * this, int segmentIndex)",
        ["field +0x18", "raw damage amount", "older field-only label", "remain unproven"],
        ["0x18"],
        ["getter", "damage", "controller", "name-correction"],
    ),
    "0x00444330": target(
        "CDestructableSegmentsController__GetCurrentSubtreeHealthIfAnyActive",
        "float __fastcall CDestructableSegmentsController__GetCurrentSubtreeHealthIfAnyActive(void * this)",
        ["Controller health query", "CDestroyableSegment__SumActiveValueRecursive", "remain unproven"],
        ["CDestroyableSegment__SumActiveValueRecursive"],
        ["health-metric", "controller", "signature-correction"],
    ),
    "0x00444370": target(
        "CDestructableSegmentsController__GetRootSubtreeHealthIfAnyActive",
        "float __fastcall CDestructableSegmentsController__GetRootSubtreeHealthIfAnyActive(void * this)",
        ["root segment", "CDestructableSegment__GetTotalHealth", "remain unproven"],
        ["CDestructableSegment__GetTotalHealth"],
        ["health-metric", "controller", "signature-correction"],
    ),
    "0x004443b0": target(
        "CDestructableSegmentsController__GetCachedTotalHealthIfAnyActive",
        "float __fastcall CDestructableSegmentsController__GetCachedTotalHealthIfAnyActive(void * this)",
        ["cached total-health", "this+0x18", "remain unproven"],
        ["0x18"],
        ["health-metric", "controller", "signature-correction"],
    ),
    "0x004443f0": target(
        "CDestructableSegmentsController__TriggerCoreCascadeIfEligible",
        "void __fastcall CDestructableSegmentsController__TriggerCoreCascadeIfEligible(void * this)",
        ["cascade trigger", "large child-damage", "Renamed from the older threshold-exceeded label", "remain unproven"],
        ["CDestroyableCoreSegment__AreCoreChildrenDestroyed", "CDestructableSegment__PropagateDamageToChildren"],
        ["cascade", "threshold", "controller", "name-correction"],
    ),
}

STALE_TOKENS = [
    "ctor_like",
    "CDestructableSegmentsController__AreCoreChildrenDestroyed",
    "CDestructableSegment__InitPrimary",
    "CDestroyableCoreSegment__VFunc_01_004434d0",
    "CDestroyableSegment__ctor_like_004434f0",
    "CDestroyableCoreSegment__VFunc_03_004435f0",
    "CDestroyableSwapSegment__VFunc_03_00443780",
    "CDestroyableSwapSegment__VFunc_08_00443810",
    "VFuncSlot_08_004439c0",
    "CDestructableSegmentsController__GetSegmentField14ByIndex",
    "CDestructableSegmentsController__GetSegmentField18ByIndex",
    "CDestructableSegmentsController__TriggerCascadeIfThresholdExceeded",
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
    ("0x005db06c", "1", "CDestroyableCoreSegment__scalar_deleting_dtor"),
    ("0x005db06c", "3", "CDestroyableCoreSegment__VFunc_03_ApplyDamage"),
    ("0x005db148", "3", "CDestroyableSwapSegment__VFunc_03_ApplyDamage"),
    ("0x005db148", "8", "CDestroyableSwapSegment__VFunc_08_HandleSegmentBreak"),
    ("0x005db0e0", "8", "CDestroyableSegment__SharedVFunc_08_HandleChildBreak"),
    ("0x005db114", "8", "CDestroyableSegment__SharedVFunc_08_HandleChildBreak"),
]

RET_EVIDENCE = {
    "0x00443480": "0x14",
    "0x004434d0": "0x4",
    "0x00443780": "0x8",
    "0x00444030": "0xc",
    "0x004442d0": "0x4",
    "0x00444300": "0x4",
}


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
    dry_log_path = dry_log_path or root / "destructable_controller_dry.log"
    apply_log_path = apply_log_path or root / "destructable_controller_apply.log"
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

    ret_hits = 0
    for address, operand in RET_EVIDENCE.items():
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

    caller_text = (
        "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in sorted(caller_decompile_dir.glob("*.c")))
        if caller_decompile_dir.is_dir()
        else ""
    )
    for token in [
        "CDestructableSegmentsController__CreateSegment",
        "CDestructableSegmentsController__ProcessNode",
        "CDestroyableCoreSegment__Init",
    ]:
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
