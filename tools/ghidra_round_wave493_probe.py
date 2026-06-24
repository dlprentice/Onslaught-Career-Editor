#!/usr/bin/env python3
"""Validate Wave493 CRound static RE evidence."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave493-round-core-004d81e0"

TARGETS = {
    "0x004d81e0": {
        "name": "CRound__ctor",
        "signature": "void * __thiscall CRound__ctor(void * this, void * init)",
        "tags": {
            "static-reaudit",
            "round-wave493",
            "round",
            "projectile",
            "retail-binary-evidence",
            "signature-corrected",
            "comment-hardened",
            "name-corrected",
            "constructor",
        },
        "comment_tokens": (
            "CWorldPhysicsManager__CreateProjectile allocates 0x134 bytes",
            "RET 0x4 plus ECX/stack use",
            "CThing__ctor_like_004f3e10",
            "CRound vtable 0x005de82c",
            "this+0xf0",
            "this+0x130 to 1",
            "runtime projectile creation behavior",
            "rebuild parity remain unproven",
        ),
        "decompile_tokens": (
            "CThing__ctor_like_004f3e10(this)",
            "PTR_LAB_005de82c",
            "PTR_CActor__GetRenderPos_005de7b4",
            "this + 0xf0",
            "DAT_00672fd0",
        ),
    },
    "0x004d82a0": {
        "name": "VFuncSlot_15_004d82a0",
        "signature": "double __fastcall VFuncSlot_15_004d82a0(void * this)",
        "tags": {
            "static-reaudit",
            "round-wave493",
            "round",
            "projectile",
            "retail-binary-evidence",
            "signature-corrected",
            "comment-hardened",
            "shared-vfunc",
            "config-scalar",
        },
        "comment_tokens": (
            "CRound vtable 0x005de82c slot 15",
            "CMissile-style vtable 0x005e3ba4 slot 15",
            "Register-only ECX receiver",
            "virtual slot +0xb4",
            "0x005dc568",
            "this+0xf0 plus offset 0x2c",
            "exact source virtual name",
        ),
        "decompile_tokens": (
            "+ 0xb4",
            "_DAT_005dc568",
            "(int)this + 0xf0",
            "+ 0x2c",
        ),
    },
    "0x004d8350": {
        "name": "CRound__scalar_deleting_dtor",
        "signature": "void * __thiscall CRound__scalar_deleting_dtor(void * this, int flags)",
        "tags": {
            "static-reaudit",
            "round-wave493",
            "round",
            "projectile",
            "retail-binary-evidence",
            "signature-corrected",
            "comment-hardened",
            "name-corrected",
            "destructor",
            "scalar-deleting-dtor",
        },
        "comment_tokens": (
            "CRound vtable 0x005de82c slot 1",
            "RET 0x8 plus ECX/stack use",
            "CRound__ShutdownAndDetachReaders(this)",
            "CDXMemoryManager__Free",
            "flags bit 0",
            "destructor side-effect completeness",
        ),
        "decompile_tokens": (
            "CRound__ShutdownAndDetachReaders(this)",
            "CDXMemoryManager__Free",
            "return this",
        ),
    },
    "0x004d8370": {
        "name": "CRound__ShutdownAndDetachReaders",
        "signature": "void __fastcall CRound__ShutdownAndDetachReaders(void * this)",
        "tags": {
            "static-reaudit",
            "round-wave493",
            "round",
            "projectile",
            "retail-binary-evidence",
            "signature-corrected",
            "comment-hardened",
            "destructor",
            "active-reader",
            "particle-effect",
        },
        "comment_tokens": (
            "called by CRound__scalar_deleting_dtor",
            "Register-only ECX receiver",
            "this+0xec",
            "this+0xe8",
            "CSPtrSet__Remove",
            "this+0xe0",
            "CActor__dtor_base",
        ),
        "decompile_tokens": (
            "CSPtrSet__Remove",
            "CParticleManager__RemoveFromGlobalList",
            "CActor__dtor_base",
        ),
    },
    "0x004d8410": {
        "name": "CRound__Init",
        "signature": "void __thiscall CRound__Init(void * this, void * init)",
        "tags": {
            "static-reaudit",
            "round-wave493",
            "round",
            "projectile",
            "retail-binary-evidence",
            "signature-corrected",
            "comment-hardened",
            "init",
            "collision-setup",
            "event-scheduling",
            "particle-effect",
        },
        "comment_tokens": (
            "CRound vtable 0x005de82c slot 9",
            "CMissile__Init delegates here",
            "RET 0x4 plus ECX/stack use",
            "init+0x3bc..0x3d8",
            "this+0x108..0x118",
            "Round.cpp debug-path sites",
            "CActor__Init",
            "schedules event 4000",
            "CRound__SelectBestTargetReaderAndSyncAimState",
        ),
        "decompile_tokens": (
            "CActor__Init(this,init)",
            "CEventManager__AddEvent_AtTime",
            "CParticleManager__CreateEffect",
            "CHeightField__TraceLineAgainstHeightfield",
            "CRound__SelectBestTargetReaderAndSyncAimState",
        ),
    },
}

EXPECTED_SUMMARIES = {
    "apply_round_wave493_dry.log": {
        "updated": 0,
        "skipped": 5,
        "renamed": 0,
        "would_rename": 2,
        "missing": 0,
        "bad": 0,
    },
    "apply_round_wave493_apply.log": {
        "updated": 5,
        "skipped": 0,
        "renamed": 2,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    },
    "apply_round_wave493_verify_dry.log": {
        "updated": 0,
        "skipped": 5,
        "renamed": 0,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    },
}

VTABLE_EXPECTATIONS = {
    ("005de82c", "1"): ("004d8350", "CRound__scalar_deleting_dtor"),
    ("005de82c", "9"): ("004d8410", "CRound__Init"),
    ("005de82c", "15"): ("004d82a0", "VFuncSlot_15_004d82a0"),
    ("005e3ba4", "15"): ("004d82a0", "VFuncSlot_15_004d82a0"),
}

XREF_TOKENS = (
    ("004d81e0", "0050f7a0", "CWorldPhysicsManager__CreateProjectile"),
    ("004d8370", "004d8350", "CRound__scalar_deleting_dtor"),
    ("004d8410", "004baae0", "CMissile__Init"),
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def fail(message: str) -> None:
    raise AssertionError(message)


def normalize_address(address: str) -> str:
    value = address.strip().lower()
    if not value.startswith("0x"):
        value = "0x" + value
    return value


def check_metadata(base: Path) -> None:
    rows = {normalize_address(row["address"]): row for row in read_tsv(base / "post_metadata.tsv")}
    for address, spec in TARGETS.items():
        row = rows.get(address)
        if row is None:
            fail(f"missing metadata row for {address}")
        if row.get("status") != "OK":
            fail(f"metadata status for {address} is {row.get('status')!r}")
        if row.get("name") != spec["name"]:
            fail(f"name mismatch for {address}: {row.get('name')!r}")
        if row.get("signature") != spec["signature"]:
            fail(f"signature mismatch for {address}: {row.get('signature')!r}")
        comment = row.get("comment", "")
        for token in spec["comment_tokens"]:
            if token not in comment:
                fail(f"comment token {token!r} missing for {address}")


def check_tags(base: Path) -> None:
    rows = {normalize_address(row["address"]): row for row in read_tsv(base / "post_tags.tsv")}
    for address, spec in TARGETS.items():
        row = rows.get(address)
        if row is None:
            fail(f"missing tags row for {address}")
        tags = {tag for tag in row.get("tags", "").split(";") if tag}
        missing = spec["tags"] - tags
        if missing:
            fail(f"missing tags for {address}: {sorted(missing)}")


def decompile_file(base: Path, address: str) -> Path:
    bare = address.removeprefix("0x")
    matches = sorted((base / "post-decomp").glob(f"{bare}_*.c"))
    if not matches:
        fail(f"missing decompile output for {address}")
    return matches[0]


def check_decompile(base: Path) -> None:
    index_rows = {normalize_address(row["address"]): row for row in read_tsv(base / "post-decomp" / "index.tsv")}
    for address, spec in TARGETS.items():
        row = index_rows.get(address)
        if row is None:
            fail(f"missing decompile index row for {address}")
        if row.get("status") != "OK":
            fail(f"decompile status for {address} is {row.get('status')!r}")
        if row.get("name") != spec["name"]:
            fail(f"decompile name mismatch for {address}: {row.get('name')!r}")
        text = decompile_file(base, address).read_text(encoding="utf-8", errors="replace")
        for token in spec["decompile_tokens"]:
            if token not in text:
                fail(f"decompile token {token!r} missing for {address}")


def parse_summary(log_text: str) -> dict[str, int]:
    pattern = re.compile(
        r"updated=(?P<updated>\d+)\s+skipped=(?P<skipped>\d+)\s+created=(?P<created>\d+)\s+"
        r"would_create=(?P<would_create>\d+)\s+renamed=(?P<renamed>\d+)\s+"
        r"would_rename=(?P<would_rename>\d+)\s+missing=(?P<missing>\d+)\s+bad=(?P<bad>\d+)"
    )
    matches = list(pattern.finditer(log_text))
    if not matches:
        fail("summary line not found in apply log")
    return {key: int(value) for key, value in matches[-1].groupdict().items()}


def check_logs(base: Path) -> None:
    for filename, expected in EXPECTED_SUMMARIES.items():
        text = (base / filename).read_text(encoding="utf-8", errors="replace")
        if "REPORT: Save succeeded" not in text:
            fail(f"save success missing from {filename}")
        summary = parse_summary(text)
        for key, value in expected.items():
            if summary.get(key) != value:
                fail(f"{filename} summary {key}={summary.get(key)} expected {value}")
        if "MISSING:" in text or "BADNAME:" in text:
            fail(f"{filename} contains MISSING/BADNAME")


def check_vtable(base: Path) -> None:
    rows = read_tsv(base / "post_vtable.tsv")
    by_key = {(row["vtable"].lower(), row["slot_index"]): row for row in rows}
    for key, (expected_entry, expected_name) in VTABLE_EXPECTATIONS.items():
        row = by_key.get(key)
        if row is None:
            fail(f"missing vtable row for {key}")
        if row.get("function_entry", "").lower() != expected_entry:
            fail(f"vtable {key} entry {row.get('function_entry')!r} expected {expected_entry}")
        if row.get("function_name") != expected_name:
            fail(f"vtable {key} name {row.get('function_name')!r} expected {expected_name}")
        if row.get("status") != "OK":
            fail(f"vtable {key} status {row.get('status')!r}")


def check_xrefs(base: Path) -> None:
    rows = read_tsv(base / "post_xrefs.tsv")
    haystack = {
        (row["target_addr"].lower(), row["from_function_addr"].lower(), row["from_function"])
        for row in rows
    }
    for target, from_addr, from_name in XREF_TOKENS:
        if (target, from_addr, from_name) not in haystack:
            fail(f"missing xref {target} from {from_addr} {from_name}")


def run(base: Path) -> None:
    check_metadata(base)
    check_tags(base)
    check_decompile(base)
    check_logs(base)
    check_vtable(base)
    check_xrefs(base)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    run(args.base)
    print(f"Wave493 CRound evidence probe PASS: {args.base}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
