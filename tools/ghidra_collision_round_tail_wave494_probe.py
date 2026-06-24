#!/usr/bin/env python3
"""Validate Wave494 collision/round tail static RE evidence."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave494-collision-round-tail-004d8a50"

TARGETS = {
    "0x004d8a50": {
        "name": "CCollisionSeekingRound__ScalarDeletingDestructor_004d8a50",
        "signature": "void * __thiscall CCollisionSeekingRound__ScalarDeletingDestructor_004d8a50(void * this, int deleteFlags)",
        "tags": {
            "static-reaudit",
            "round-wave494",
            "round",
            "projectile",
            "retail-binary-evidence",
            "signature-corrected",
            "comment-hardened",
            "name-corrected",
            "destructor",
            "scalar-deleting-dtor",
            "collision-seeking",
        },
        "comment_tokens": (
            "vtable 0x005de950 slot 1",
            "RET 0x4 plus ECX/stack use",
            "CCollisionSeekingRound__ShutdownMonitorAndDestruct(this)",
            "deleteFlags bit 0",
            "relationship to older recovered helper wrappers",
            "runtime collision/projectile teardown behavior",
            "rebuild parity remain unproven",
        ),
        "decompile_tokens": (
            "CCollisionSeekingRound__ShutdownMonitorAndDestruct(this)",
            "deleteFlags",
            "CDXMemoryManager__Free",
            "return this",
        ),
    },
    "0x004d8a70": {
        "name": "CCollisionSeekingRound__ShutdownMonitorAndDestruct",
        "signature": "void __fastcall CCollisionSeekingRound__ShutdownMonitorAndDestruct(void * this)",
        "tags": {
            "static-reaudit",
            "round-wave494",
            "round",
            "projectile",
            "retail-binary-evidence",
            "signature-corrected",
            "comment-hardened",
            "destructor",
            "monitor",
            "collision-seeking",
        },
        "comment_tokens": (
            "called by the 0x004d8a50 scalar-deleting wrapper",
            "Register-only ECX receiver",
            "this+0x24",
            "CMonitor__Shutdown",
            "CCollisionSeekingRound__Destructor(this)",
            "destructor side-effect completeness",
        ),
        "decompile_tokens": (
            "CMonitor__Shutdown((void *)((int)this + 0x24))",
            "CCollisionSeekingRound__Destructor(this)",
        ),
    },
    "0x004d8dc0": {
        "name": "VFuncSlot_02_004d8dc0",
        "signature": "void __fastcall VFuncSlot_02_004d8dc0(void * this)",
        "tags": {
            "static-reaudit",
            "round-wave494",
            "round",
            "projectile",
            "retail-binary-evidence",
            "signature-corrected",
            "comment-hardened",
            "shared-vfunc",
            "active-reader",
            "particle-effect",
        },
        "comment_tokens": (
            "CRound vtable 0x005de82c slot 2",
            "CMissile-style vtable 0x005e3ba4 slot 2",
            "Register-only ECX receiver",
            "round-config this+0xf0",
            "this+0xe0",
            "this+0xec/this+0xe8",
            "VFuncSlot_02_004f41b0",
        ),
        "decompile_tokens": (
            "ParticleEffectLink__SetHandleStateAndClear",
            "CMonitor__RemoveActiveReaderById",
            "CGenericActiveReader__SetReader",
            "VFuncSlot_02_004f41b0(this)",
        ),
    },
    "0x004d9d60": {
        "name": "CEngine__InitRoundLaunchStateDefaults",
        "signature": "void __fastcall CEngine__InitRoundLaunchStateDefaults(void * state)",
        "tags": {
            "static-reaudit",
            "round-wave494",
            "round",
            "projectile",
            "retail-binary-evidence",
            "signature-corrected",
            "comment-hardened",
            "launch-state",
            "config-defaults",
        },
        "comment_tokens": (
            "0x38-byte round launch/config state record",
            "sets 0x10 and 0x20 to 1",
            "sets 0x18 and 0x1c to 2",
            "-1.0f bits at 0x2c",
            "field names",
            "runtime projectile launch behavior",
        ),
        "decompile_tokens": (
            "(int)state + 0x10",
            "(int)state + 0x18",
            "(int)state + 0x2c",
            "0xbf800000",
        ),
    },
    "0x004d9da0": {
        "name": "CCSRay__ScalarDeletingDestructor_004d9da0",
        "signature": "void * __thiscall CCSRay__ScalarDeletingDestructor_004d9da0(void * this, int deleteFlags)",
        "tags": {
            "static-reaudit",
            "round-wave494",
            "round",
            "projectile",
            "retail-binary-evidence",
            "signature-corrected",
            "comment-hardened",
            "name-corrected",
            "destructor",
            "scalar-deleting-dtor",
            "ccsray",
            "collision-seeking",
        },
        "comment_tokens": (
            "CCSRay-style vtable 0x005de980 slot 1",
            "RET 0x4 plus ECX/stack use",
            "CCSRay__DestructorBody_004d9dc0(this)",
            "deleteFlags bit 0",
            "runtime ray/effect behavior",
        ),
        "decompile_tokens": (
            "CCSRay__DestructorBody_004d9dc0(this)",
            "deleteFlags",
            "CDXMemoryManager__Free",
            "return this",
        ),
    },
    "0x004d9dc0": {
        "name": "CCSRay__DestructorBody_004d9dc0",
        "signature": "void __fastcall CCSRay__DestructorBody_004d9dc0(void * this)",
        "tags": {
            "static-reaudit",
            "round-wave494",
            "round",
            "projectile",
            "retail-binary-evidence",
            "signature-corrected",
            "comment-hardened",
            "name-corrected",
            "destructor",
            "ccsray",
            "collision-seeking",
        },
        "comment_tokens": (
            "called by CCSRay__ScalarDeletingDestructor_004d9da0",
            "CCSRay-style vtable evidence",
            "vtable pointer 0x005d9608",
            "this+0x14 and this+0x18",
            "CMonitor__Shutdown(this)",
            "relationship to CCollisionSeekingRound helper layouts",
        ),
        "decompile_tokens": (
            "PTR_SharedVFunc__NoOpOneArg_004014c0_005d9608",
            "+ 0x14",
            "+ 0x18",
            "CMonitor__Shutdown(this)",
        ),
    },
    "0x004d9ef0": {
        "name": "CEngine__UpdateRoundAndTriggerLaunchEffect",
        "signature": "void __fastcall CEngine__UpdateRoundAndTriggerLaunchEffect(void * round)",
        "tags": {
            "static-reaudit",
            "round-wave494",
            "round",
            "projectile",
            "retail-binary-evidence",
            "signature-corrected",
            "comment-hardened",
            "launch-effect",
            "event-dispatch",
            "particle-effect",
        },
        "comment_tokens": (
            "vtable/data references at 0x005de940 and 0x005e3cb8",
            "CEngine__ArmProjectileAndSpawnTrailEffect(round)",
            "CUnit-style timestamp at +0xd0",
            "this+0xf0+0x5c and +0x6c",
            "CExplosionInitThing-like stack payload with type 2",
            "virtual slot +0xc8",
        ),
        "decompile_tokens": (
            "CEngine__ArmProjectileAndSpawnTrailEffect(round)",
            "CUnit__ResetFieldD0ToGlobalThreshold(round)",
            "+ 0x5c",
            "+ 0x6c",
            "CExplosionInitThing__ctor_like_004d9f30",
            "+ 0xc8",
        ),
    },
}

EXPECTED_SUMMARIES = {
    "apply_collision_round_tail_wave494_dry.log": {
        "updated": 0,
        "skipped": 7,
        "renamed": 0,
        "would_rename": 3,
        "missing": 0,
        "bad": 0,
    },
    "apply_collision_round_tail_wave494_apply.log": {
        "updated": 7,
        "skipped": 0,
        "renamed": 3,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    },
    "apply_collision_round_tail_wave494_verify_dry.log": {
        "updated": 0,
        "skipped": 7,
        "renamed": 0,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    },
}

VTABLE_EXPECTATIONS = (
    ("005de950", "1", "004d8a50", "CCollisionSeekingRound__ScalarDeletingDestructor_004d8a50"),
    ("005de82c", "2", "004d8dc0", "VFuncSlot_02_004d8dc0"),
    ("005e3ba4", "2", "004d8dc0", "VFuncSlot_02_004d8dc0"),
    ("005de980", "1", "004d9da0", "CCSRay__ScalarDeletingDestructor_004d9da0"),
)

XREF_EXPECTATIONS = (
    ("004d8a50", "005de954", "DATA"),
    ("004d8a70", "004d8a53", "UNCONDITIONAL_CALL"),
    ("004d8dc0", "005de834", "DATA"),
    ("004d8dc0", "005e3bac", "DATA"),
    ("004d9da0", "005de984", "DATA"),
    ("004d9dc0", "004d9da3", "UNCONDITIONAL_CALL"),
    ("004d9ef0", "005de940", "DATA"),
    ("004d9ef0", "005e3cb8", "DATA"),
)

OVERCLAIM_TOKENS = ("runtime behavior proven", "source identity proven", "fully re'ed", "100% re")


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


def decompile_text_for(directory: Path, address: str) -> str:
    if not directory.is_dir():
        return ""
    matches = sorted(directory.glob(f"{normalize_address(address)[2:]}_*.c"))
    if not matches:
        return ""
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

        decompile = decompile_text_for(decompile_dir, address)
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
        "schema": "ghidra-collision-round-tail-wave494-probe.v1",
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
            print(f"Wave494 collision/round tail probe: PASS ({report['targetCount']} targets)")
            return 0
        print("Wave494 collision/round tail probe: FAIL", file=sys.stderr)
        for failure in report["failures"]:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print(report)
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
