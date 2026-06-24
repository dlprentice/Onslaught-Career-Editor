#!/usr/bin/env python3
"""Validate Wave456 Mine/Missile/MotionController static metadata corrections."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave456-mine-missile-current"
COMMON_TAGS = {"static-reaudit", "mine-missile-wave456", "retail-binary-evidence"}

EXPECTED_DRY = {
    "updated": 0,
    "skipped": 8,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 6,
    "missing": 0,
    "bad": 0,
}
EXPECTED_APPLY = {
    "updated": 8,
    "skipped": 0,
    "created": 0,
    "would_create": 0,
    "renamed": 6,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}
EXPECTED_VERIFY_DRY = {
    "updated": 0,
    "skipped": 8,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}


def target(
    name: str,
    signature: str,
    comment_tokens: list[str],
    tags: list[str],
    decompile_tokens: list[str],
) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "commentTokens": comment_tokens,
        "tags": sorted(COMMON_TAGS | set(tags)),
        "decompileTokens": decompile_tokens,
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x004ba150": target(
        "CMine__Init",
        "void __thiscall CMine__Init(void * this, void * init)",
        [
            "init+0x70",
            "heading at init+0x44",
            "heightfield normal",
            "CMCMine controller",
            "this+0x70",
            "runtime mine placement/water behavior remains unproven",
        ],
        ["mine", "init", "signature-corrected", "comment-hardened"],
        [
            "CMonitor__SampleHeightfieldNormalAtXY",
            "CGroundUnit__Init",
            "CMCMine__Constructor",
            "s_C__dev_ONSLAUGHT2_Mine_cpp_006309a4",
            "0x260",
            "0x264",
        ],
    ),
    "0x004ba490": target(
        "CMine__VFunc02_CleanupLinkedParticleAndForward",
        "void __fastcall CMine__VFunc02_CleanupLinkedParticleAndForward(void * this)",
        [
            "this+0x264",
            "CUnit__FinalizeLinkedUnitStateAndClear",
            "particle manager/global list",
            "VFuncSlot_02_004f95d0",
            "exact virtual slot and runtime cleanup behavior remain unproven",
        ],
        ["mine", "cleanup", "name-corrected", "signature-corrected", "comment-hardened"],
        [
            "0x264",
            "CUnit__FinalizeLinkedUnitStateAndClear",
            "CParticleManager__RemoveFromGlobalList",
            "VFuncSlot_02_004f95d0",
        ],
    ),
    "0x004ba9d0": target(
        "CMine__TryDestroyedResetAndDispatchVFunc1D4",
        "int __fastcall CMine__TryDestroyedResetAndDispatchVFunc1D4(void * this)",
        [
            "CMine-adjacent vtable data xref",
            "0x005e1c4c",
            "CGroundUnit__MarkDestroyedAndResetState",
            "vfunc +0x1d4",
            "exact virtual slot/runtime lifecycle remains unproven",
        ],
        ["mine", "groundunit", "owner-corrected", "name-corrected", "signature-corrected", "comment-hardened"],
        [
            "CGroundUnit__MarkDestroyedAndResetState",
            "+ 0x1d4",
            "return 1",
        ],
    ),
    "0x004baae0": target(
        "CMissile__Init",
        "void __thiscall CMissile__Init(void * this, void * init)",
        [
            "this+0xf0",
            "allocates a 0x428 descriptor object",
            "OID type 0x61",
            "CResourceDescriptor",
            "PCRTID__CreateObject",
            "this+0x30",
            "runtime missile payload behavior remains unproven",
        ],
        ["missile", "init", "signature-corrected", "comment-hardened"],
        [
            "OID__AllocObject(0x428,0x61",
            "CResourceDescriptor__ctor",
            "PCRTID__CreateObject",
            "CRound__Init",
        ],
    ),
    "0x004bac10": target(
        "CMissile__DispatchLinkedObjectVFunc68AndPostHook",
        "void __thiscall CMissile__DispatchLinkedObjectVFunc68AndPostHook(void * this, int arg0, int arg1)",
        [
            "RET 0x8",
            "this+0x30",
            "vfunc +0x68",
            "SharedVFunc__NoOp_Ret08",
            "CMissile-adjacent vtable data xref",
            "exact virtual slot/source identity remains unproven",
        ],
        ["missile", "dispatch", "owner-corrected", "name-corrected", "signature-corrected", "comment-hardened"],
        [
            "+ 0x30",
            "+ 0x68",
            "arg0",
            "arg1",
            "SharedVFunc__NoOp_Ret08",
        ],
    ),
    "0x004bae10": target(
        "CMotionController__scalar_deleting_dtor",
        "void * __thiscall CMotionController__scalar_deleting_dtor(void * this, byte flags)",
        [
            "scalar-deleting destructor wrapper",
            "RET 0x4",
            "CMotionController__dtor_base",
            "flags bit 0",
            "runtime ownership remains unproven",
        ],
        ["motion-controller", "destructor", "name-corrected", "signature-corrected", "comment-hardened"],
        [
            "CMotionController__dtor_base",
            "flags",
            "CDXMemoryManager__Free",
            "return this",
        ],
    ),
    "0x004bae30": target(
        "CMotionController__ctor_base",
        "void __fastcall CMotionController__ctor_base(void * this)",
        [
            "base vtable 0x005dc778",
            "clears +0x04/+0x08",
            "instruction read-back",
            "concrete list semantics remain unproven",
        ],
        ["motion-controller", "constructor", "name-corrected", "signature-corrected", "comment-hardened"],
        [
            "PTR_SharedVFunc__NoOpOneArg_004014c0_005dc778",
            "+ 4) = 0",
            "+ 8) = 0",
        ],
    ),
    "0x004bae50": target(
        "CMotionController__dtor_base",
        "void __fastcall CMotionController__dtor_base(void * this)",
        [
            "base vtable 0x005dc778",
            "tails CMonitor__Shutdown",
            "runtime ownership remains unproven",
        ],
        ["motion-controller", "destructor", "name-corrected", "signature-corrected", "comment-hardened"],
        [
            "PTR_SharedVFunc__NoOpOneArg_004014c0_005dc778",
            "CMonitor__Shutdown",
        ],
    ),
}

EXPECTED_XREF_EDGES = [
    ("0x004ba150", "0x005e1ba8", "<no_function>"),
    ("0x004ba490", "0x005e1b8c", "<no_function>"),
    ("0x004ba9d0", "0x005e1c4c", "<no_function>"),
    ("0x004baae0", "0x005e3bc8", "<no_function>"),
    ("0x004bac10", "0x005e3cc0", "<no_function>"),
    ("0x004bae10", "0x005dc77c", "<no_function>"),
    ("0x004bae30", "0x004983d0", "CMCMech__Constructor"),
    ("0x004bae30", "0x0049c3e3", "CMCMine__Constructor"),
    ("0x004bae30", "0x0049c5d3", "CMCSentinel__Constructor"),
    ("0x004bae50", "0x004bae13", "CMotionController__scalar_deleting_dtor"),
    ("0x004bae50", "0x0049c434", "CMCMine__Destructor"),
    ("0x004bae50", "0x0049c62d", "CMCSentinel__Destructor"),
]

EXPECTED_VTABLE_ROWS = [
    ("0x005e1c4c", "0", "0x004ba9d0", "CMine__TryDestroyedResetAndDispatchVFunc1D4"),
    ("0x005e3cc0", "0", "0x004bac10", "CMissile__DispatchLinkedObjectVFunc68AndPostHook"),
]

INSTRUCTION_TOKENS = {
    "0x004ba150": [
        "0x004ba150\tCMine__Init\tOR\tEBX, 0x20",
        "0x004ba150\tCMine__Init\tCALL\t0x0047ec60",
        "0x004ba490\tCMine__Init\tCALL\t0x0047c730",
        "0x004ba490\tCMine__Init\tCALL\t0x0049c3e0",
        "0x004ba490\tCMine__Init\tMOV\tdword ptr [ESI + 0x260], EBX",
    ],
    "0x004ba490": [
        "0x004ba490\tCMine__VFunc02_CleanupLinkedParticleAndForward\tMOV\tECX, dword ptr [ESI + 0x264]",
        "0x004ba490\tCMine__VFunc02_CleanupLinkedParticleAndForward\tCALL\t0x004cb0b0",
        "0x004ba490\tCMine__VFunc02_CleanupLinkedParticleAndForward\tCALL\t0x004cb050",
        "0x004ba490\tCMine__VFunc02_CleanupLinkedParticleAndForward\tCALL\t0x004f95d0",
    ],
    "0x004ba9d0": [
        "0x004ba9d0\tCMine__TryDestroyedResetAndDispatchVFunc1D4\tCALL\t0x0047ce80",
        "0x004ba9d0\tCMine__TryDestroyedResetAndDispatchVFunc1D4\tCALL\tdword ptr [EAX + 0x1d4]",
        "0x004ba9d0\tCMine__TryDestroyedResetAndDispatchVFunc1D4\tMOV\tEAX, 0x1",
    ],
    "0x004baae0": [
        "0x004baae0\tCMissile__Init\tCALL\t0x005490e0",
        "0x004baae0\tCMissile__Init\tCALL\t0x0055dc20",
        "0x004baae0\tCMissile__Init\tCALL\t0x00516580",
        "0x004baae0\tCMissile__Init\tCALL\t0x004d8410",
    ],
    "0x004bac10": [
        "0x004bac10\tCMissile__DispatchLinkedObjectVFunc68AndPostHook\tMOV\tECX, dword ptr [ESI + 0x30]",
        "0x004bac10\tCMissile__DispatchLinkedObjectVFunc68AndPostHook\tCALL\tdword ptr [EAX + 0x68]",
        "0x004bac10\tCMissile__DispatchLinkedObjectVFunc68AndPostHook\tCALL\t0x00452da0",
        "0x004bac10\tCMissile__DispatchLinkedObjectVFunc68AndPostHook\tRET\t0x8",
    ],
    "0x004bae10": [
        "0x004bae10\tCMotionController__scalar_deleting_dtor\tCALL\t0x004bae50",
        "0x004bae10\tCMotionController__scalar_deleting_dtor\tTEST\tbyte ptr [ESP + 0x8], 0x1",
        "0x004bae10\tCMotionController__scalar_deleting_dtor\tCALL\t0x00549220",
        "0x004bae10\tCMotionController__scalar_deleting_dtor\tRET\t0x4",
    ],
    "0x004bae30": [
        "0x004bae30\tCMotionController__ctor_base\tXOR\tECX, ECX",
        "0x004bae30\tCMotionController__ctor_base\tMOV\tdword ptr [EAX + 0x4], ECX",
        "0x004bae30\tCMotionController__ctor_base\tMOV\tdword ptr [EAX], 0x5dc778",
        "0x004bae30\tCMotionController__ctor_base\tMOV\tdword ptr [EAX + 0x8], ECX",
    ],
    "0x004bae50": [
        "0x004bae50\tCMotionController__dtor_base\tMOV\tdword ptr [ECX], 0x5dc778",
        "0x004bae50\tCMotionController__dtor_base\tJMP\t0x004bac40",
    ],
}

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "runtime cleanup behavior proven",
    "runtime mine placement proven",
    "runtime missile payload proven",
    "source identity proven",
    "exact virtual slot proven",
    "concrete layout proven",
    "rebuild parity proven",
    "fully re'ed",
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
        for key in ("address", "target_addr", "from_addr", "from_function_addr", "function_entry", "pointer_addr", "slot_addr", "vtable"):
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


def decompile_text_for(base: Path, address: str) -> str:
    directory = base / "post-decomp"
    if not directory.is_dir():
        return ""
    prefix = normalize_address(address)[2:]
    matches = sorted(directory.glob(f"{prefix}_*.c"))
    return read_text(matches[0]) if matches else ""


def parse_summary(text: str) -> dict[str, int] | None:
    match = re.search(
        r"SUMMARY\s+updated=(\d+)\s+skipped=(\d+)\s+created=(\d+)\s+would_create=(\d+)\s+renamed=(\d+)\s+would_rename=(\d+)\s+missing=(\d+)\s+bad=(\d+)",
        text,
    )
    if not match:
        return None
    keys = ["updated", "skipped", "created", "would_create", "renamed", "would_rename", "missing", "bad"]
    return {key: int(value) for key, value in zip(keys, match.groups(), strict=True)}


def check_log(base: Path, filename: str, expected: dict[str, int], failures: list[str]) -> None:
    text = read_text(base / filename)
    if not text:
        failures.append(f"{filename}: missing or empty")
        return
    summary = parse_summary(text)
    if summary != expected:
        failures.append(f"{filename}: summary mismatch expected {expected}, got {summary}")
    for token in ("FAIL:", "Exception", "LockException"):
        if token in text:
            failures.append(f"{filename}: unexpected failure token {token!r}")
    if "REPORT: Save succeeded" not in text:
        failures.append(f"{filename}: missing Ghidra save-success marker")


def check_metadata(base: Path, failures: list[str]) -> None:
    metadata = read_tsv(base / "post_metadata.tsv")
    tags = read_tsv(base / "post_tags.tsv")
    if len(metadata) != len(TARGETS):
        failures.append(f"post_metadata.tsv: expected {len(TARGETS)} rows, got {len(metadata)}")
    for address, spec in TARGETS.items():
        row = row_by_address(metadata, address)
        if row is None:
            failures.append(f"{address}: missing post_metadata row")
            continue
        if row.get("name") != spec["name"]:
            failures.append(f"{address}: name mismatch {row.get('name')!r}")
        if row.get("signature") != spec["signature"]:
            failures.append(f"{address}: signature mismatch {row.get('signature')!r}")
        comment = row.get("comment", "")
        for token in spec["commentTokens"]:  # type: ignore[index]
            if not token_present(comment, str(token)):
                failures.append(f"{address}: missing comment token {token!r}")
        lowered = comment.lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"{address}: overclaim token {token!r} in comment")

        tag_row = row_by_address(tags, address)
        if tag_row is None:
            failures.append(f"{address}: missing post_tags row")
            continue
        actual_tags = {tag for tag in tag_row.get("tags", "").split(";") if tag}
        for tag in spec["tags"]:  # type: ignore[index]
            if str(tag) not in actual_tags:
                failures.append(f"{address}: missing tag {tag!r}")


def check_decompiles(base: Path, failures: list[str]) -> None:
    index_rows = read_tsv(base / "post-decomp" / "index.tsv")
    ok_rows = [row for row in index_rows if row.get("status") == "OK"]
    if len(ok_rows) != len(TARGETS):
        failures.append(f"post-decomp/index.tsv: expected {len(TARGETS)} OK rows, got {len(ok_rows)}")
    for address, spec in TARGETS.items():
        text = decompile_text_for(base, address)
        if not text:
            failures.append(f"{address}: missing post decompile text")
            continue
        for token in spec["decompileTokens"]:  # type: ignore[index]
            if not token_present(text, str(token)):
                failures.append(f"{address}: missing decompile token {token!r}")


def check_xrefs(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_xrefs.tsv")
    if len(rows) < len(EXPECTED_XREF_EDGES):
        failures.append(f"post_xrefs.tsv: expected at least {len(EXPECTED_XREF_EDGES)} rows, got {len(rows)}")
    edges = {
        (row.get("target_addr", ""), row.get("from_addr", ""), row.get("from_function", ""))
        for row in rows
    }
    for address, from_addr, caller in EXPECTED_XREF_EDGES:
        edge = (normalize_address(address), normalize_address(from_addr), caller)
        if edge not in edges:
            failures.append(f"{address}: missing xref from {caller} at {from_addr}")


def check_vtables(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_vtable_slots.tsv")
    indexed = {
        (row.get("vtable", ""), row.get("slot_index", ""), row.get("pointer_addr", ""), row.get("function_name", ""))
        for row in rows
    }
    for vtable, slot, pointer, function_name in EXPECTED_VTABLE_ROWS:
        entry = (normalize_address(vtable), slot, normalize_address(pointer), function_name)
        if entry not in indexed:
            failures.append(f"{vtable}: missing vtable slot {slot} -> {function_name} at {pointer}")


def check_instructions(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_instructions.tsv")
    text = "\n".join(
        "\t".join(
            [
                row.get("target_addr", ""),
                row.get("function_name", ""),
                row.get("mnemonic", ""),
                row.get("operands", ""),
                row.get("flow_type", ""),
            ]
        )
        for row in rows
    )
    for address, tokens in INSTRUCTION_TOKENS.items():
        for token in tokens:
            if token not in text:
                failures.append(f"{address}: missing instruction token {token!r}")


def run_checks(base: Path = BASE) -> tuple[str, list[str]]:
    failures: list[str] = []
    if not base.is_dir():
        failures.append(f"missing evidence directory: {base}")
        return "FAIL", failures
    check_log(base, "apply_dry.log", EXPECTED_DRY, failures)
    check_log(base, "apply.log", EXPECTED_APPLY, failures)
    check_log(base, "apply_verify_dry.log", EXPECTED_VERIFY_DRY, failures)
    check_metadata(base, failures)
    check_decompiles(base, failures)
    check_xrefs(base, failures)
    check_vtables(base, failures)
    check_instructions(base, failures)
    return ("PASS" if not failures else "FAIL"), failures


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default=str(BASE), help="Wave456 evidence directory")
    parser.add_argument("--check", action="store_true", help="Return non-zero on failure")
    args = parser.parse_args(argv)

    base = Path(args.base)
    status, failures = run_checks(base)
    print(f"Wave456 Mine/Missile/MotionController probe: {status}")
    print(f"Base: {base}")
    print(f"Targets: {len(TARGETS)}")
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
    return 1 if args.check and failures else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
