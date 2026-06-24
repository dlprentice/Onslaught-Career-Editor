#!/usr/bin/env python3
"""Validate Wave486 engine option / CPOD / CUnit ballistic evidence."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave486-engine-option-motion-004d3020"

OPTION = "0x004d3020"
CPOD_SLOT66 = "0x004d3630"
BALLISTIC_INIT = "0x004d36c0"
BALLISTIC_COMPUTE = "0x004d3730"

EXPECTED_SUMMARIES = {
    "apply_engine_pod_ballistic_wave486_dry.log": {
        "updated": 0,
        "skipped": 4,
        "created": 0,
        "would_create": 0,
        "renamed": 0,
        "would_rename": 1,
        "missing": 0,
        "bad": 0,
    },
    "apply_engine_pod_ballistic_wave486_apply.log": {
        "updated": 4,
        "skipped": 0,
        "created": 0,
        "would_create": 0,
        "renamed": 1,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    },
    "apply_engine_pod_ballistic_wave486_verify_dry.log": {
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
    OPTION: {
        "name": "CEngine__SetOptionValueAndNotifyTarget",
        "signature": "void __thiscall CEngine__SetOptionValueAndNotifyTarget(void * this, int option_value)",
        "tags": {
            "comment-hardened",
            "engine-option",
            "engine-pod-ballistic-wave486",
            "god-mode-adjacent",
            "retail-binary-evidence",
            "signature-corrected",
            "static-reaudit",
        },
        "comment_tokens": [
            "RET 0x4",
            "stale extra float parameter",
            "this+0x20",
            "0x00662ab0",
            "this+0x1c",
            "vfunc +0xe0",
            "vfunc +0x154",
            "0x004d113a/0x004d114a",
            "runtime behavior",
            "rebuild parity remain unproven",
        ],
        "decompile_tokens": [
            "void __thiscall CEngine__SetOptionValueAndNotifyTarget(void *this,int option_value)",
            "*(int *)((int)this + 0x20) = option_value",
            "0x154",
            "option_value != 0",
        ],
    },
    CPOD_SLOT66: {
        "name": "CPod__VFunc_66_UpdateMotionAndAccumulateScalar",
        "signature": "void __fastcall CPod__VFunc_66_UpdateMotionAndAccumulateScalar(void * this)",
        "tags": {
            "comment-hardened",
            "cpod",
            "engine-pod-ballistic-wave486",
            "motion",
            "renamed",
            "retail-binary-evidence",
            "signature-corrected",
            "static-reaudit",
            "vfunc-slot-66",
            "vtable-readback",
        },
        "comment_tokens": [
            "CPOD RTTI resolves vtable 0x005dff8c",
            "slot 66",
            "0x005e0094",
            "stale CEngine owner label",
            "CUnit__UpdateMotionAttachmentsAndEffects(this)",
            "vfunc +0xb4",
            "this+0x84",
            "CPod source/body text is absent",
            "runtime motion behavior",
            "rebuild parity remain unproven",
        ],
        "decompile_tokens": [
            "void __fastcall CPod__VFunc_66_UpdateMotionAndAccumulateScalar(void *this)",
            "CUnit__UpdateMotionAttachmentsAndEffects(this)",
            "*(int *)this + 0xb4",
            "*(float *)((int)this + 0x84)",
        ],
    },
    BALLISTIC_INIT: {
        "name": "CUnit__InitBallisticAimState",
        "signature": "void __thiscall CUnit__InitBallisticAimState(void * this, float target_x, float target_y, float target_z, float target_w)",
        "tags": {
            "ballistic",
            "comment-hardened",
            "cunit",
            "engine-pod-ballistic-wave486",
            "raw-caller-readback",
            "retail-binary-evidence",
            "signature-corrected",
            "static-reaudit",
        },
        "comment_tokens": [
            "RET 0x10",
            "this+0x254",
            "this+0x258..0x264",
            "CStaticShadows__SampleShadowHeightBilinear",
            "CUnit__ComputeBallisticLaunchVelocity(this)",
            "0x005344f0",
            "runtime aim behavior",
            "rebuild parity remain unproven",
        ],
        "decompile_tokens": [
            "CUnit__InitBallisticAimState(void *this,float target_x,float target_y,float target_z,float target_w)",
            "*(int *)((int)this + 0x254) == 0",
            "CStaticShadows__SampleShadowHeightBilinear(&DAT_006fadc8,&target_x)",
            "CUnit__ComputeBallisticLaunchVelocity(this)",
        ],
    },
    BALLISTIC_COMPUTE: {
        "name": "CUnit__ComputeBallisticLaunchVelocity",
        "signature": "void __fastcall CUnit__ComputeBallisticLaunchVelocity(void * this)",
        "tags": {
            "ballistic",
            "comment-hardened",
            "cunit",
            "engine-pod-ballistic-wave486",
            "retail-binary-evidence",
            "signature-corrected",
            "static-reaudit",
        },
        "comment_tokens": [
            "ECX is the unit pointer",
            "this+0x258/0x25c",
            "this+0x164+0xb4",
            "0x005d8584",
            "0x005d85c8",
            "0x005d8cb8",
            "CSquadNormal__BuildOrientationMatrixFromEuler",
            "this+0x7c/0x80/0x84",
            "runtime projectile/aim behavior",
            "rebuild parity remain unproven",
        ],
        "decompile_tokens": [
            "void __fastcall CUnit__ComputeBallisticLaunchVelocity(void *this)",
            "fpatan",
            "*(int *)((int)this + 0x164) + 0xb4",
            "_DAT_005d8584",
            "_DAT_005d85c8",
            "_DAT_005d8cb8",
            "CSquadNormal__BuildOrientationMatrixFromEuler",
            "*(float *)((int)this + 0x7c)",
            "*(float *)((int)this + 0x84)",
        ],
    },
}

STALE_TOKENS = (
    "CEngine__AdvanceAndAccumulateMotionScalar",
    "float param_2",
    "int CUnit__InitBallisticAimState(void)",
    "param_1",
)

OVERCLAIMS = (
    "fully re'ed",
    "source identity proven",
    "runtime behavior proven",
    "exact layout proven",
    "rebuild parity proven",
)


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
        for stale in STALE_TOKENS:
            if stale != "param_1" and token_present(text, stale):
                failures.append(f"{address}: stale decompile token {stale!r}")
        if address in (CPOD_SLOT66, BALLISTIC_INIT, BALLISTIC_COMPUTE) and token_present(text, "param_1"):
            failures.append(f"{address}: stale param_1 remains in decompile")


def check_xrefs(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_xrefs.tsv")
    expectations = {
        OPTION: {
            ("0x0046e108", "CGame__RestartLoopRunLevel", "UNCONDITIONAL_CALL"),
            ("0x00472d09", "CGameInterface__HandleMenuSelection", "UNCONDITIONAL_CALL"),
            ("0x004d0b3a", "CPauseMenu__ButtonPressed", "UNCONDITIONAL_CALL"),
            ("0x004d113a", "<no_function>", "UNCONDITIONAL_CALL"),
            ("0x004d114a", "<no_function>", "UNCONDITIONAL_CALL"),
        },
        CPOD_SLOT66: {("0x005e0094", "<no_function>", "DATA")},
        BALLISTIC_INIT: {("0x005344f0", "<no_function>", "UNCONDITIONAL_CALL")},
        BALLISTIC_COMPUTE: {("0x004d3708", "CUnit__InitBallisticAimState", "UNCONDITIONAL_CALL")},
    }
    for target, refs in expectations.items():
        for from_addr, from_fn, ref_type in refs:
            row = next((r for r in rows if r.get("target_addr") == target and r.get("from_addr") == from_addr), None)
            if row is None:
                failures.append(f"{target}: missing xref from {from_addr}")
            else:
                if row.get("from_function") != from_fn:
                    failures.append(f"{target}: xref {from_addr} expected function {from_fn}, got {row.get('from_function')}")
                if row.get("ref_type") != ref_type:
                    failures.append(f"{target}: xref {from_addr} expected {ref_type}, got {row.get('ref_type')}")


def check_vtable(base: Path, failures: list[str]) -> None:
    type_rows = read_tsv(base / "pre_vtable_scan_types.tsv")
    cpod_type = next((r for r in type_rows if r.get("vtable") == "0x005dff8c"), None)
    if cpod_type is None or cpod_type.get("demangled_type_name") != "CPod":
        failures.append("0x005dff8c: missing CPOD RTTI row")
    slot_rows = read_tsv(base / "post_vtable_window.tsv")
    row = next((r for r in slot_rows if r.get("slot_addr") == "0x005e0094"), None)
    if row is None:
        failures.append("0x005e0094: missing vtable slot row")
    elif row.get("pointer_addr") != CPOD_SLOT66 or row.get("function_name") != TARGETS[CPOD_SLOT66]["name"]:
        failures.append(f"0x005e0094: expected {TARGETS[CPOD_SLOT66]['name']}, got {row.get('pointer_addr')} {row.get('function_name')}")


def check_callers_and_instructions(base: Path, failures: list[str]) -> None:
    caller_rows = read_tsv(base / "post_caller_instructions.tsv")
    caller_expectations = {
        "0x004d1138": ("PUSH", "0x0"),
        "0x004d113a": ("CALL", "0x004d3020"),
        "0x004d1148": ("PUSH", "0x1"),
        "0x004d114a": ("CALL", "0x004d3020"),
        "0x005344ed": ("MOV", "[ESI + 0x10]"),
        "0x005344f0": ("CALL", "0x004d36c0"),
    }
    by_addr = {row.get("instruction_addr"): row for row in caller_rows}
    for address, (mnemonic, operand_token) in caller_expectations.items():
        row = by_addr.get(address)
        if row is None:
            failures.append(f"{address}: missing caller instruction row")
            continue
        if row.get("mnemonic") != mnemonic or not token_present(row.get("operands", ""), operand_token):
            failures.append(f"{address}: expected {mnemonic} {operand_token}, got {row.get('mnemonic')} {row.get('operands')}")

    instr_rows = read_tsv(base / "post_instructions.tsv")
    instruction_expectations = {
        "0x004d302e": ("MOV", "0x662ab0"),
        "0x004d3075": ("RET", "0x4"),
        "0x004d3633": ("CALL", "0x004fa8d0"),
        "0x004d3648": ("FSTP", "[ESI + 0x84]"),
        "0x004d3722": ("RET", "0x10"),
        "0x004d3708": ("CALL", "0x004d3730"),
        "0x004d383b": ("CALL", "0x004062d0"),
        "0x004d3886": ("RET", ""),
    }
    by_addr = {row.get("instruction_addr"): row for row in instr_rows}
    for address, (mnemonic, operand_token) in instruction_expectations.items():
        row = by_addr.get(address)
        if row is None:
            failures.append(f"{address}: missing instruction row")
            continue
        if row.get("mnemonic") != mnemonic or (operand_token and not token_present(row.get("operands", ""), operand_token)):
            failures.append(f"{address}: expected {mnemonic} {operand_token}, got {row.get('mnemonic')} {row.get('operands')}")


def run(base: Path = DEFAULT_BASE) -> list[str]:
    failures: list[str] = []
    check_summaries(base, failures)
    check_metadata(base, failures)
    check_decompile(base, failures)
    check_xrefs(base, failures)
    check_vtable(base, failures)
    check_callers_and_instructions(base, failures)
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    failures = run(args.base)
    if failures:
        print("FAIL Wave486 engine/pod/ballistic probe")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("PASS Wave486 engine/pod/ballistic probe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
