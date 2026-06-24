#!/usr/bin/env python3
"""Validate Wave495 projectile/round spawn-tail static RE evidence."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave495-projectile-spawn-tail-004d9f30"

COMMON_TAGS = {
    "static-reaudit",
    "round-wave495",
    "retail-binary-evidence",
    "signature-corrected",
    "comment-hardened",
}

TARGETS = {
    "0x004d9ef0": {
        "name": "CRound__UpdateRoundAndTriggerLaunchEffect",
        "signature": "void __fastcall CRound__UpdateRoundAndTriggerLaunchEffect(void * this)",
        "tags": COMMON_TAGS
        | {"round", "projectile", "name-corrected", "launch-effect", "vtable-referenced"},
        "comment_tokens": (
            "Wave495 corrective owner/comment update",
            "CRound__ArmProjectileAndSpawnTrailEffect",
            "vtable/data references at 0x005de940 and 0x005e3cb8",
            "this+0xf0+0x5c and +0x6c",
            "virtual slot +0xc8",
            "runtime launch/effect behavior",
            "rebuild parity remain unproven",
        ),
        "decompile_tokens": (
            "CRound__ArmProjectileAndSpawnTrailEffect(this)",
            "CUnit__ResetFieldD0ToGlobalThreshold(this)",
            "CRound__UpdateEffectTransformByMode_004d9f30(this,2",
            "+ 200",
        ),
    },
    "0x004d9f30": {
        "name": "CRound__UpdateEffectTransformByMode_004d9f30",
        "signature": (
            "void __thiscall CRound__UpdateEffectTransformByMode_004d9f30"
            "(void * this, int effectMode, void * context, void * targetOrOwner)"
        ),
        "tags": COMMON_TAGS
        | {
            "round",
            "projectile",
            "name-corrected",
            "effect-transform",
            "cinitthing-payload",
            "mode-dispatch",
        },
        "comment_tokens": (
            "RET 0x0c plus ECX receiver",
            "effectMode, context, and target/owner stack arguments",
            "not a CExplosionInitThing constructor",
            "CInitThing/CExplosionInitThing-like stack payload",
            "mode 0/1/3 transform paths",
            "runtime effect behavior",
        ),
        "decompile_tokens": (
            "CInitThing__ctor(local_438)",
            "effectMode == 0",
            "effectMode == 1",
            "effectMode != 3",
            "CParticleManager__CreateEffect",
            "CParticleDescriptor__Load12DwordsAndMarkDirty",
        ),
    },
    "0x004daa20": {
        "name": "CEngine__FindPresetIndexByName",
        "signature": "int __cdecl CEngine__FindPresetIndexByName(char * presetName)",
        "tags": COMMON_TAGS | {"round", "projectile", "preset-list", "name-lookup"},
        "comment_tokens": (
            "cdecl helper with one presetName stack argument",
            "DAT_008553f8",
            "entry name at +0x30",
            "zero-based ordinal or -1",
            "runtime preset behavior",
        ),
        "decompile_tokens": (
            "int __cdecl CEngine__FindPresetIndexByName(char *presetName)",
            "presetName != (char *)0x0",
            "DAT_008553f8",
            "return iVar6",
            "return -1",
        ),
    },
    "0x004daab0": {
        "name": "CRound__SetTargetReaderIfAllowed",
        "signature": (
            "void __thiscall CRound__SetTargetReaderIfAllowed"
            "(void * this, void * targetReader, int replaceExisting)"
        ),
        "tags": COMMON_TAGS | {"round", "projectile", "name-corrected", "active-reader", "targeting"},
        "comment_tokens": (
            "RET 0x8 plus ECX receiver",
            "targetReader and replaceExisting stack arguments",
            "this+0xf0+0x48/+0x1c",
            "DAT_008551a0",
            "CGenericActiveReader__SetReader",
            "runtime targeting behavior",
        ),
        "decompile_tokens": (
            "targetReader != (void *)0x0",
            "replaceExisting != 0",
            "CMonitor__RemoveActiveReaderById",
            "CGenericActiveReader__SetReader((void *)((int)this + 0xe8),targetReader)",
            "CSPtrSet__AddToHead(&DAT_008551a0,this)",
        ),
    },
    "0x004dab50": {
        "name": "CRound__RemoveActiveReaderById",
        "signature": "void __fastcall CRound__RemoveActiveReaderById(void * this)",
        "tags": COMMON_TAGS | {"round", "projectile", "active-reader", "targeting"},
        "comment_tokens": (
            "register-only ECX receiver",
            "this+0xe8",
            "owner monitor at this+0xec",
            "DAT_008551a0",
            "CGenericActiveReader at this+0xe8",
            "rebuild parity remain unproven",
        ),
        "decompile_tokens": (
            "CMonitor__RemoveActiveReaderById(this_00",
            "CSPtrSet__Remove(&DAT_008551a0,this)",
            "CGenericActiveReader__SetReader((void *)((int)this + 0xe8),(void *)0x0)",
        ),
    },
    "0x004daba0": {
        "name": "CRound__FindNearbyHostileWithinProjectileRadius",
        "signature": "void * __fastcall CRound__FindNearbyHostileWithinProjectileRadius(void * this)",
        "tags": COMMON_TAGS
        | {"round", "projectile", "name-corrected", "targeting", "mapwho", "radius-query"},
        "comment_tokens": (
            "register-only ECX receiver is a CRound-style helper",
            "CMapWho around this+0x1c/0x20/0x24",
            "this+0xf0+0x90",
            "candidate flag bit 0x10",
            "flag bit 0x04",
            "runtime targeting behavior",
        ),
        "decompile_tokens": (
            "CMapWho__GetFirstEntryWithinRadius",
            "CMapWhoEntry__GetOwner",
            "CUnitAI__GetWorldPositionForTargeting",
            "CMapWho__GetNextEntryWithinRadius",
            "return pvVar4",
        ),
    },
    "0x004dac90": {
        "name": "CRound__SelectBestTargetReaderAndSyncAimState",
        "signature": (
            "void __thiscall CRound__SelectBestTargetReaderAndSyncAimState"
            "(void * this, void * eventPayload, void * unusedContext)"
        ),
        "tags": COMMON_TAGS
        | {"round", "projectile", "active-reader", "targeting", "event-scheduling", "aim-state"},
        "comment_tokens": (
            "RET 0x8 plus ECX receiver prove two stack arguments",
            "eventPayload is observed reaching CEventManager__AddEvent_AtTime",
            "DAT_008550d0",
            "CBattleEngine__IsWeaponModeCompatibleWithMountState",
            "this+0x108..0x114",
            "event 0xfa3",
        ),
        "decompile_tokens": (
            "CSPtrSet__First(&DAT_008550d0)",
            "CBattleEngine__IsWeaponModeCompatibleWithMountState",
            "CRound__RemoveActiveReaderById(this)",
            "CGenericActiveReader__SetReader(this_00,readerCell)",
            "CEventManager__AddEvent_AtTime(&EVENT_MANAGER,0xfa3",
        ),
    },
    "0x004db090": {
        "name": "CRound__GetPresetScalarByConfigName",
        "signature": "double __fastcall CRound__GetPresetScalarByConfigName(void * this)",
        "tags": COMMON_TAGS | {"round", "projectile", "name-corrected", "preset-list", "x87-return"},
        "comment_tokens": (
            "register-only ECX receiver",
            "this+0xf0+0x08",
            "DAT_008553f8",
            "matched entry scalar at +0x38",
            "x87",
            "runtime projectile behavior",
        ),
        "decompile_tokens": (
            "double __fastcall CRound__GetPresetScalarByConfigName(void *this)",
            "pbVar2 = *(byte **)(*(int *)((int)this + 0xf0) + 8)",
            "DAT_008553f8",
            "return (double)*(float *)(iVar6 + 0x38)",
            "return (double)_DAT_005d856c",
        ),
    },
    "0x004db150": {
        "name": "CRound__SpawnConfiguredProjectile",
        "signature": "void __fastcall CRound__SpawnConfiguredProjectile(void * this)",
        "tags": COMMON_TAGS
        | {"round", "projectile", "name-corrected", "projectile-spawn", "targeting", "croundinitthing-payload"},
        "comment_tokens": (
            "register-only ECX receiver is a CRound-style spawn helper",
            "CRound__FindNearbyHostileWithinProjectileRadius",
            "CWorldPhysicsManager__CreateProjectile(this+0xf0)",
            "CRoundInitThing-like stack payload",
            "target reader",
            "runtime projectile behavior",
        ),
        "decompile_tokens": (
            "CRound__FindNearbyHostileWithinProjectileRadius(this)",
            "CWorldPhysicsManager__CreateProjectile",
            "CInitThing__ctor(&local_3dc)",
            "PTR_CInitThing__CopyFrom_005de9b4",
            "CRound__RemoveActiveReaderById(this_00)",
            "(**(code **)(*this_00 + 0x24))(&local_3dc)",
        ),
    },
    "0x004db630": {
        "name": "CRound__ArmProjectileAndSpawnTrailEffect",
        "signature": "void __fastcall CRound__ArmProjectileAndSpawnTrailEffect(void * this)",
        "tags": COMMON_TAGS
        | {"round", "projectile", "name-corrected", "launch-effect", "particle-effect", "velocity"},
        "comment_tokens": (
            "register-only ECX receiver",
            "this+0x12c is clear",
            "round-config +0x6c",
            "config +0x2c",
            "config +0x04",
            "runtime launch/trail behavior",
        ),
        "decompile_tokens": (
            "if ((*(int *)((int)this + 300) == 0)",
            "ParticleEffectLink__SetHandleStateAndClear((void *)((int)this + 0xe0),0)",
            "CParticleManager__CreateEffect",
            "*(undefined4 *)(iVar1 + 0xa0) = 1",
        ),
    },
}

EXPECTED_SUMMARIES = {
    "apply_projectile_spawn_tail_wave495_dry.log": {
        "updated": 0,
        "skipped": 9,
        "renamed": 0,
        "would_rename": 6,
        "missing": 0,
        "bad": 0,
    },
    "apply_projectile_spawn_tail_wave495_apply.log": {
        "updated": 9,
        "skipped": 0,
        "renamed": 6,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    },
    "apply_projectile_spawn_tail_wave495_verify_dry.log": {
        "updated": 0,
        "skipped": 9,
        "renamed": 0,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    },
    "apply_projectile_spawn_tail_wave495_corrective_dry.log": {
        "updated": 0,
        "skipped": 10,
        "renamed": 0,
        "would_rename": 1,
        "missing": 0,
        "bad": 0,
    },
    "apply_projectile_spawn_tail_wave495_corrective_apply.log": {
        "updated": 1,
        "skipped": 9,
        "renamed": 1,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    },
    "apply_projectile_spawn_tail_wave495_corrective_verify_dry.log": {
        "updated": 0,
        "skipped": 10,
        "renamed": 0,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    },
}

VTABLE_EXPECTATIONS = (
    ("005de940", "0", "004d9ef0", "CRound__UpdateRoundAndTriggerLaunchEffect"),
    ("005e3cb8", "0", "004d9ef0", "CRound__UpdateRoundAndTriggerLaunchEffect"),
)

XREF_EXPECTATIONS = (
    ("004d9ef0", "005de940", "DATA"),
    ("004d9ef0", "005e3cb8", "DATA"),
    ("004d9f30", "004d9f1b", "UNCONDITIONAL_CALL"),
    ("004daa20", "004da51b", "UNCONDITIONAL_CALL"),
    ("004daab0", "005074d3", "UNCONDITIONAL_CALL"),
    ("004dab50", "004dae78", "UNCONDITIONAL_CALL"),
    ("004daba0", "004db15a", "UNCONDITIONAL_CALL"),
    ("004dac90", "004d8a27", "UNCONDITIONAL_CALL"),
    ("004db090", "00489691", "UNCONDITIONAL_CALL"),
    ("004db150", "004d9960", "UNCONDITIONAL_CALL"),
    ("004db630", "004d9ef3", "UNCONDITIONAL_CALL"),
)

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "source identity proven",
    "fully re'ed",
    "100% re",
)


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


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
        for key in ("address", "target_addr", "from_addr", "vtable", "pointer_addr", "function_entry"):
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


def decompile_text_for(directory: Path, address: str, expected_name: str) -> str:
    if not directory.is_dir():
        return ""
    matches = sorted(directory.glob(f"{normalize_address(address)[2:]}_*.c"))
    if not matches:
        return ""
    for match in matches:
        if expected_name in match.name:
            return read_text(match)
    return read_text(matches[0])


def parse_summary(text: str) -> dict[str, int]:
    pattern = re.compile(
        r"updated=(?P<updated>\d+)\s+skipped=(?P<skipped>\d+)\s+"
        r"created=(?P<created>\d+)\s+would_create=(?P<would_create>\d+)\s+"
        r"renamed=(?P<renamed>\d+)\s+would_rename=(?P<would_rename>\d+)\s+"
        r"missing=(?P<missing>\d+)\s+bad=(?P<bad>\d+)"
    )
    match = pattern.search(text)
    if not match:
        return {}
    return {key: int(value) for key, value in match.groupdict().items()}


def build_report(base: Path = DEFAULT_BASE) -> dict[str, object]:
    base = resolve(base)
    metadata_rows = read_tsv(base / "post_metadata.tsv")
    tag_rows = read_tsv(base / "post_tags.tsv")
    xref_rows = read_tsv(base / "post_xrefs.tsv")
    vtable_rows = read_tsv(base / "post_vtable.tsv")
    decompile_dir = base / "post-decomp"

    failures: list[str] = []

    for address, spec in TARGETS.items():
        metadata = row_by_address(metadata_rows, address)
        if metadata is None:
            failures.append(f"missing metadata row for {address}")
            continue
        if metadata.get("status") != "OK":
            failures.append(f"{address} metadata status is {metadata.get('status')}")
        if metadata.get("name") != spec["name"]:
            failures.append(f"{address} name {metadata.get('name')} != {spec['name']}")
        if metadata.get("signature") != spec["signature"]:
            failures.append(f"{address} signature {metadata.get('signature')} != {spec['signature']}")
        comment = metadata.get("comment", "")
        for token in spec["comment_tokens"]:
            if not token_present(comment, token):
                failures.append(f"{address} comment missing token: {token}")
        for token in OVERCLAIM_TOKENS:
            if token_present(comment, token):
                failures.append(f"{address} comment contains overclaim token: {token}")

        tag_row = row_by_address(tag_rows, address)
        if tag_row is None:
            failures.append(f"missing tag row for {address}")
        else:
            tags = set(filter(None, tag_row.get("tags", "").split(";")))
            missing_tags = sorted(spec["tags"] - tags)
            if missing_tags:
                failures.append(f"{address} missing tags: {', '.join(missing_tags)}")

        decompile = decompile_text_for(decompile_dir, address, spec["name"])
        if not decompile:
            failures.append(f"missing decompile for {address}")
        else:
            for token in spec["decompile_tokens"]:
                if not token_present(decompile, token):
                    failures.append(f"{address} decompile missing token: {token}")

    for logfile, expected in EXPECTED_SUMMARIES.items():
        text = read_text(base / logfile)
        if not text:
            failures.append(f"missing log {logfile}")
            continue
        summary = parse_summary(text)
        if not summary:
            failures.append(f"missing summary in {logfile}")
            continue
        for key, value in expected.items():
            if summary.get(key) != value:
                failures.append(f"{logfile} {key} {summary.get(key)} != {value}")
        if "REPORT: Save succeeded" not in text:
            failures.append(f"{logfile} missing save success")

    for vtable, slot_index, pointer_addr, function_name in VTABLE_EXPECTATIONS:
        found = False
        for row in vtable_rows:
            if (
                row.get("vtable") == normalize_address(vtable)
                and row.get("slot_index") == slot_index
                and row.get("pointer_addr") == normalize_address(pointer_addr)
                and row.get("function_name") == function_name
                and row.get("status") == "OK"
            ):
                found = True
                break
        if not found:
            failures.append(f"missing vtable expectation {vtable} slot {slot_index} -> {pointer_addr} {function_name}")

    for target, from_addr, ref_type in XREF_EXPECTATIONS:
        found = False
        for row in xref_rows:
            if (
                row.get("target_addr") == normalize_address(target)
                and row.get("from_addr") == normalize_address(from_addr)
                and row.get("ref_type") == ref_type
            ):
                found = True
                break
        if not found:
            failures.append(f"missing xref {from_addr} -> {target} {ref_type}")

    return {
        "schema": "ghidra-projectile-spawn-tail-wave495-probe.v1",
        "base": str(base.relative_to(ROOT)),
        "targets": sorted(TARGETS),
        "targetCount": len(TARGETS),
        "failures": failures,
        "status": "PASS" if not failures else "FAIL",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    report = build_report(args.base)
    if args.check:
        if report["status"] == "PASS":
            print(f"Wave495 projectile/round spawn-tail probe: PASS ({report['targetCount']} targets)")
            return 0
        print("Wave495 projectile/round spawn-tail probe: FAIL", file=sys.stderr)
        for failure in report["failures"]:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print(report)
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
