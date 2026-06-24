#!/usr/bin/env python3
"""Validate Wave485 CPlane hit/animation correction evidence."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave485-unitai-hit-004d1f10"

HIT = "0x004d1f10"
WING_OPEN = "0x004d1f90"
WING_CLOSE = "0x004d1fd0"
ATTACK_LAUNCH = "0x004d2010"

EXPECTED_SUMMARIES = {
    "apply_plane_hit_animation_wave485_dry.log": {
        "updated": 0,
        "skipped": 4,
        "created": 0,
        "would_create": 0,
        "renamed": 0,
        "would_rename": 4,
        "missing": 0,
        "bad": 0,
    },
    "apply_plane_hit_animation_wave485_apply.log": {
        "updated": 4,
        "skipped": 0,
        "created": 0,
        "would_create": 0,
        "renamed": 4,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    },
    "apply_plane_hit_animation_wave485_verify_dry.log": {
        "updated": 0,
        "skipped": 4,
        "created": 0,
        "would_create": 0,
        "renamed": 0,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    },
}

TARGETS = {
    HIT: {
        "name": "CPlane__Hit_CheckFatalDamageAndDie",
        "signature": "void __thiscall CPlane__Hit_CheckFatalDamageAndDie(void * this, void * hit_thing, void * hit_context)",
        "tags": {
            "comment-hardened",
            "cplane",
            "damage",
            "hit",
            "plane-wave485",
            "renamed",
            "retail-binary-evidence",
            "signature-corrected",
            "static-reaudit",
            "vtable-readback",
        },
        "comment_tokens": [
            "CPlane vtable 0x005e1930 slot 39",
            "CDiveBomber, CGroundAttackAircraft, and CBomber use different slot-39 hit handlers",
            "this+0x164->0x11c",
            "hit_thing+0x34 flags",
            "+0x138 ownership/team comparison",
            "hit_thing vfunc +0x194",
            "CExplosionInitThing__ctor_like_004fd230",
            "this vfunc +0x38",
            "CThing__Hit_TriggerDieOnUnitOrTypeMask02100000(this, hit_thing, hit_context)",
            "Plane.cpp/CPlane source body is absent",
            "runtime hit/death behavior",
            "rebuild parity remain unproven",
        ],
        "decompile_tokens": [
            "void __thiscall CPlane__Hit_CheckFatalDamageAndDie(void *this,void *hit_thing,void *hit_context)",
            "*(int *)((int)this + 0x164) + 0x11c",
            "*(uint *)((int)hit_thing + 0x34)",
            "*(int *)((int)hit_thing + 0x138) != *(int *)((int)this + 0x138)",
            "(**(code **)(*(int *)hit_thing + 0x194))(this)",
            "CExplosionInitThing__ctor_like_004fd230(this)",
            "CThing__Hit_TriggerDieOnUnitOrTypeMask02100000(this,hit_thing,hit_context)",
        ],
    },
    WING_OPEN: {
        "name": "CPlane__PlayWingOpenAnimationOnce",
        "signature": "void __fastcall CPlane__PlayWingOpenAnimationOnce(void * this)",
        "tags": {
            "animation",
            "comment-hardened",
            "cplane",
            "plane-wave485",
            "renamed",
            "retail-binary-evidence",
            "signature-corrected",
            "static-reaudit",
            "wing-open",
        },
        "comment_tokens": [
            "raw caller instruction context passes [ESI+0x8] in ECX",
            "this+0x27c from 1 to 2",
            "wingopen at 0x00624420",
            "CMesh__FindAnimationIndexByName",
            "this vfunc +0xf0",
            "Plane.cpp/CPlane source body is absent",
            "runtime animation behavior",
            "rebuild parity remain unproven",
        ],
        "decompile_tokens": [
            "void __fastcall CPlane__PlayWingOpenAnimationOnce(void *this)",
            "*(int *)((int)this + 0x27c) == 1",
            "s_wingopen_00624420",
            "CMesh__FindAnimationIndexByName",
            "*(undefined4 *)((int)this + 0x27c) = 2",
        ],
    },
    WING_CLOSE: {
        "name": "CPlane__PlayWingCloseAnimationOnce",
        "signature": "void __fastcall CPlane__PlayWingCloseAnimationOnce(void * this)",
        "tags": {
            "animation",
            "comment-hardened",
            "cplane",
            "plane-wave485",
            "renamed",
            "retail-binary-evidence",
            "signature-corrected",
            "static-reaudit",
            "wing-close",
        },
        "comment_tokens": [
            "raw caller instruction context passes [ESI+0x8] in ECX",
            "this+0x27c from 4 to 3",
            "wingclose at 0x0062442c",
            "CMesh__FindAnimationIndexByName",
            "this vfunc +0xf0",
            "Plane.cpp/CPlane source body is absent",
            "runtime animation behavior",
            "rebuild parity remain unproven",
        ],
        "decompile_tokens": [
            "void __fastcall CPlane__PlayWingCloseAnimationOnce(void *this)",
            "*(int *)((int)this + 0x27c) == 4",
            "s_wingclose_0062442c",
            "CMesh__FindAnimationIndexByName",
            "*(undefined4 *)((int)this + 0x27c) = 3",
        ],
    },
    ATTACK_LAUNCH: {
        "name": "CPlane__UpdateAttackLaunchAnimationState",
        "signature": "int __fastcall CPlane__UpdateAttackLaunchAnimationState(void * this)",
        "tags": {
            "animation",
            "attack-launch",
            "comment-hardened",
            "cplane",
            "plane-wave485",
            "renamed",
            "retail-binary-evidence",
            "signature-corrected",
            "static-reaudit",
            "vtable-readback",
        },
        "comment_tokens": [
            "CPlane vtable 0x005e1930 slot 59",
            "CDiveBomber, CGroundAttackAircraft, and CBomber use different slot-59 animation handlers",
            "this+0x8 through vfunc +0x58",
            "this+0x27c from 2 to 4",
            "attack string 0x00624438",
            "from 3 to 1",
            "launch string 0x006243f8",
            "CMesh__FindAnimationIndexByName",
            "function returns 0",
            "Plane.cpp/CPlane source body is absent",
            "runtime animation behavior",
            "rebuild parity remain unproven",
        ],
        "decompile_tokens": [
            "int __fastcall CPlane__UpdateAttackLaunchAnimationState(void *this)",
            "*(int *)((int)this + 8) + 0x58",
            "*(int *)((int)this + 0x27c) == 2",
            "s_attack_00624438",
            "*(undefined4 *)((int)this + 0x27c) = 4",
            "*(int *)((int)this + 0x27c) == 3",
            "s_launch_006243f8",
            "*(undefined4 *)((int)this + 0x27c) = 1",
            "return 0",
        ],
    },
}

STALE_NAMES = (
    "CUnitAI__Hit_CheckFatalDamageAndDie",
    "CExplosionInitThing__PlayWingOpenAnimationOnce",
    "CExplosionInitThing__PlayWingCloseAnimationOnce",
    "CExplosionInitThing__UpdateAttackLaunchAnimationState",
)

OVERCLAIMS = (
    "fully re'ed",
    "source identity proven",
    "runtime behavior proven",
    "runtime hit/death behavior proven",
    "runtime animation behavior proven",
    "exact class layout proven",
    "animation-state layout proven",
    "rebuild parity proven",
)

EXPECTED_INSTRUCTIONS = {
    "0x004d1f14": ("MOV", "EDI, dword ptr [ESP + 0xc]"),
    "0x004d1f18": ("MOV", "[ESI + 0x164]"),
    "0x004d1f28": ("MOV", "[EDI + 0x34]"),
    "0x004d1f34": ("MOV", "[EDI + 0x138]"),
    "0x004d1f4b": ("TEST", "0x2100000"),
    "0x004d1f5b": ("CALL", "[EDX + 0x194]"),
    "0x004d1f63": ("CALL", "0x004fd230"),
    "0x004d1f6c": ("CALL", "[EAX + 0x38]"),
    "0x004d1f77": ("CALL", "0x00403ba0"),
    "0x004d1f7e": ("RET", "0x8"),
    "0x004d1f93": ("CMP", "[ESI + 0x27c], 0x1"),
    "0x004d1fa8": ("PUSH", "0x624420"),
    "0x004d1fb2": ("CALL", "0x004aa630"),
    "0x004d1fc0": ("MOV", "[ESI + 0x27c], 0x2"),
    "0x004d1fd3": ("CMP", "[ESI + 0x27c], 0x4"),
    "0x004d1fe8": ("PUSH", "0x62442c"),
    "0x004d1ff2": ("CALL", "0x004aa630"),
    "0x004d2000": ("MOV", "[ESI + 0x27c], 0x3"),
    "0x004d201a": ("CALL", "[EAX + 0x58]"),
    "0x004d203b": ("PUSH", "0x6243f8"),
    "0x004d2053": ("MOV", "[ESI + 0x27c], 0x1"),
    "0x004d206d": ("PUSH", "0x624438"),
    "0x004d2085": ("MOV", "[ESI + 0x27c], 0x4"),
}


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


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def unescape(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        for key in (
            "address",
            "target_addr",
            "from_addr",
            "function_entry",
            "vtable",
            "slot_addr",
            "pointer_addr",
            "instruction_addr",
        ):
            if key in row and row[key]:
                row[key] = normalize_address(row[key])
        if "comment" in row:
            row["comment"] = unescape(row["comment"])
    return rows


def parse_summary(path: Path) -> dict[str, int]:
    text = read_text(path)
    match = re.search(
        r"updated=(?P<updated>\d+)\s+skipped=(?P<skipped>\d+)\s+created=(?P<created>\d+)\s+"
        r"would_create=(?P<would_create>\d+)\s+renamed=(?P<renamed>\d+)\s+"
        r"would_rename=(?P<would_rename>\d+)\s+missing=(?P<missing>\d+)\s+bad=(?P<bad>\d+)",
        text,
    )
    if not match:
        return {}
    return {key: int(value) for key, value in match.groupdict().items()}


def check_summaries(base: Path, failures: list[str]) -> None:
    for filename, expected in EXPECTED_SUMMARIES.items():
        path = base / filename
        actual = parse_summary(path)
        if actual != expected:
            failures.append(f"{filename}: expected summary {expected}, got {actual or '<missing>'}")
        if "REPORT: Save succeeded" not in read_text(path):
            failures.append(f"{filename}: missing REPORT: Save succeeded")


def check_metadata(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_metadata.tsv")
    tag_rows = read_tsv(base / "post_tags.tsv")
    names = {row.get("name", "") for row in rows}
    stale = sorted(name for name in names if name in STALE_NAMES)
    if stale:
        failures.append(f"post_metadata.tsv: stale names remain {stale}")

    for address, expected in TARGETS.items():
        row = next((r for r in rows if r.get("address") == address), None)
        if row is None:
            failures.append(f"{address}: missing metadata row")
            continue
        if row.get("name") != expected["name"]:
            failures.append(f"{address}: expected name {expected['name']}, got {row.get('name')}")
        if compact(row.get("signature", "")) != compact(expected["signature"]):
            failures.append(f"{address}: expected signature {expected['signature']}, got {row.get('signature')}")
        comment = row.get("comment", "")
        for token in expected["comment_tokens"]:
            if not token_present(comment, token):
                failures.append(f"{address}: comment missing token {token!r}")
        for overclaim in OVERCLAIMS:
            if token_present(comment, overclaim):
                failures.append(f"{address}: comment contains overclaim {overclaim!r}")

        tag_row = next((r for r in tag_rows if r.get("address") == address), None)
        if tag_row is None:
            failures.append(f"{address}: missing tag row")
        else:
            actual_tags = set(filter(None, re.split(r"[;,]\s*", tag_row.get("tags", ""))))
            missing_tags = expected["tags"] - actual_tags
            if missing_tags:
                failures.append(f"{address}: missing tags {sorted(missing_tags)}")


def check_decompile(base: Path, failures: list[str]) -> None:
    for address, expected in TARGETS.items():
        path = base / "post-decomp" / f"{address[2:]}_{expected['name']}.c"
        text = read_text(path)
        if not text:
            failures.append(f"{address}: missing decompile file {path.name}")
            continue
        for token in expected["decompile_tokens"]:
            if not token_present(text, token):
                failures.append(f"{address}: decompile missing token {token!r}")
        for stale_name in STALE_NAMES:
            if token_present(text, stale_name):
                failures.append(f"{address}: stale decompile name {stale_name!r}")


def check_xrefs(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_xrefs.tsv")
    expected = {
        HIT: ("0x005e19cc", "DATA"),
        WING_OPEN: ("0x004d229f", "UNCONDITIONAL_CALL"),
        WING_CLOSE: ("0x004d2400", "UNCONDITIONAL_CALL"),
        ATTACK_LAUNCH: ("0x005e1a1c", "DATA"),
    }
    for target, (from_addr, ref_type) in expected.items():
        row = next((r for r in rows if r.get("target_addr") == target and r.get("from_addr") == from_addr), None)
        if row is None:
            failures.append(f"{target}: missing xref from {from_addr}")
        elif row.get("ref_type") != ref_type:
            failures.append(f"{target}: expected {ref_type} xref from {from_addr}, got {row.get('ref_type')}")


def check_vtables(base: Path, failures: list[str]) -> None:
    slot_rows = read_tsv(base / "post_vtable_slots.tsv")
    type_rows = read_tsv(base / "post_vtable_types.tsv")
    expected_types = {
        "0x005e1930": "CPlane",
        "0x005e123c": "CDiveBomber",
        "0x005e2bcc": "CGroundAttackAircraft",
        "0x005e2e20": "CBomber",
        "0x005d8d1c": "CUnitAI",
    }
    for vtable, expected_type in expected_types.items():
        row = next((r for r in type_rows if r.get("vtable") == vtable), None)
        if row is None:
            failures.append(f"{vtable}: missing RTTI type row")
        elif row.get("demangled_type_name") != expected_type:
            failures.append(f"{vtable}: expected RTTI type {expected_type}, got {row.get('demangled_type_name')}")

    cplane_expectations = {
        "39": (HIT, "CPlane__Hit_CheckFatalDamageAndDie"),
        "59": (ATTACK_LAUNCH, "CPlane__UpdateAttackLaunchAnimationState"),
        "68": ("0x004d20a0", "CPlane__VFunc_68_CrashIfNoAirSupport"),
        "69": ("0x0047bf60", "CPlane__VFunc_69_CrashIfNoSupportModes"),
    }
    for slot, (pointer, function_name) in cplane_expectations.items():
        row = next(
            (
                r
                for r in slot_rows
                if r.get("vtable") == "0x005e1930" and r.get("slot_index") == slot and r.get("pointer_addr") == pointer
            ),
            None,
        )
        if row is None:
            failures.append(f"0x005e1930 slot {slot}: missing pointer {pointer}")
        elif row.get("function_name") != function_name:
            failures.append(f"0x005e1930 slot {slot}: expected {function_name}, got {row.get('function_name')}")

    sibling_slots = {
        ("0x005e123c", "39"): "CThing__Hit_TriggerDieOnUnitOrTypeMask02100000",
        ("0x005e123c", "59"): "CUnitAI__AdvanceOpenCloseShootAnimationState",
        ("0x005e2bcc", "39"): "CThing__Hit_TriggerDieOnUnitOrTypeMask02100000",
        ("0x005e2bcc", "59"): "CGroundAttackAircraft__AdvanceCloseShootAnimationState",
        ("0x005e2e20", "39"): "CThing__Hit_TriggerDieOnTypeMask00100000",
        ("0x005e2e20", "59"): "CUnitAI__HandleDeployAndFireAnimationCompletion",
    }
    for (vtable, slot), expected_name in sibling_slots.items():
        row = next((r for r in slot_rows if r.get("vtable") == vtable and r.get("slot_index") == slot), None)
        if row is None:
            failures.append(f"{vtable} slot {slot}: missing sibling slot row")
        elif row.get("function_name") != expected_name:
            failures.append(f"{vtable} slot {slot}: expected sibling {expected_name}, got {row.get('function_name')}")


def check_instructions(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_instructions.tsv")
    by_addr = {row.get("instruction_addr"): row for row in rows}
    for address, (mnemonic, operand_token) in EXPECTED_INSTRUCTIONS.items():
        row = by_addr.get(address)
        if row is None:
            failures.append(f"{address}: missing instruction row")
            continue
        if row.get("mnemonic") != mnemonic or not token_present(row.get("operands", ""), operand_token):
            failures.append(f"{address}: expected {mnemonic} {operand_token}, got {row.get('mnemonic')} {row.get('operands')}")


def check_raw_callers(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_caller_instructions.tsv")
    expectations = {
        "0x004d229c": ("MOV", "[ESI + 0x8]"),
        "0x004d229f": ("CALL", "0x004d1f90"),
        "0x004d23fd": ("MOV", "[ESI + 0x8]"),
        "0x004d2400": ("CALL", "0x004d1fd0"),
    }
    by_addr = {row.get("instruction_addr"): row for row in rows}
    for address, (mnemonic, operand_token) in expectations.items():
        row = by_addr.get(address)
        if row is None:
            failures.append(f"{address}: missing raw caller instruction row")
            continue
        if row.get("function_entry") != "<none>" or row.get("function_name") != "<no_function>":
            failures.append(f"{address}: expected raw no_function caller context, got {row.get('function_entry')} {row.get('function_name')}")
        if row.get("mnemonic") != mnemonic or not token_present(row.get("operands", ""), operand_token):
            failures.append(f"{address}: expected caller {mnemonic} {operand_token}, got {row.get('mnemonic')} {row.get('operands')}")


def run(base: Path = DEFAULT_BASE) -> list[str]:
    failures: list[str] = []
    check_summaries(base, failures)
    check_metadata(base, failures)
    check_decompile(base, failures)
    check_xrefs(base, failures)
    check_vtables(base, failures)
    check_instructions(base, failures)
    check_raw_callers(base, failures)
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    failures = run(args.base)
    if failures:
        print("FAIL Wave485 plane hit/animation probe")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("PASS Wave485 plane hit/animation probe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
