#!/usr/bin/env python3
"""Validate the Wave385 CGame/CDXGame Ghidra correction tranche."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

DEFAULT_ROOT = Path("subagents/ghidra-static-reaudit/game-dxgame-wave385/current")
OUTPUT_NAME = "game-dxgame-wave385.json"

COMMON_TAGS = {
    "static-reaudit",
    "game-dxgame-wave385",
    "retail-binary-evidence",
}


def target(
    name: str,
    signature: str,
    comment_tokens: list[str],
    decompile_tokens: list[str],
    tags: list[str],
    stale_names: list[str],
) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "commentTokens": comment_tokens,
        "decompileTokens": decompile_tokens,
        "tags": tags,
        "staleNames": stale_names,
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x0046c210": target(
        "CGame__ctor",
        "void * __fastcall CGame__ctor(void * this)",
        [
            "Wave385 owner correction",
            "CGame constructor",
            "starts from the IController vtable",
            "installs the CGame vtable",
            "exact layout, runtime behavior, and rebuild parity remain unproven",
        ],
        ["CGame__ctor", "PTR_SharedVFunc__NoOpOneArg_004014c0_005d9388", "PTR_CGame__HandleEvent_005dbbb4"],
        ["cgame", "constructor", "owner-corrected", "signature-hardened", "comment-hardened"],
        ["IController__ctor_like_0046c210"],
    ),
    "0x0046c2b0": target(
        "CGame__scalar_deleting_dtor",
        "void * __thiscall CGame__scalar_deleting_dtor(void * this, byte flags)",
        [
            "Wave385 owner correction",
            "scalar-deleting destructor wrapper",
            "calls CGame__dtor",
            "optionally frees this through OID__FreeObject",
            "runtime deletion behavior and rebuild parity remain unproven",
        ],
        ["CGame__scalar_deleting_dtor", "CGame__dtor(this)", "OID__FreeObject(this)"],
        ["cgame", "destructor", "scalar-deleting-dtor", "owner-corrected", "signature-hardened", "comment-hardened"],
        ["CGame__VFunc_01_0046c2b0"],
    ),
    "0x0046c2d0": target(
        "CGame__dtor",
        "void __fastcall CGame__dtor(void * this)",
        [
            "Wave385 owner correction",
            "CGame destructor body",
            "unregisters active-reader style links",
            "calls CMonitor__Shutdown",
            "exact layout, runtime shutdown behavior, and rebuild parity remain unproven",
        ],
        ["CGame__dtor", "CSPtrSet__Remove", "CMonitor__Shutdown(this)"],
        ["cgame", "destructor", "owner-corrected", "signature-hardened", "comment-hardened"],
        ["CGame__ctor_like_0046c2d0"],
    ),
    "0x00541f00": target(
        "CDXGame__dtor_thunk",
        "void __fastcall CDXGame__dtor_thunk(void * this)",
        [
            "Wave385 owner correction",
            "CDXGame destructor thunk",
            "unconditional jump to CGame__dtor",
            "CDXGame derives from CGame",
            "runtime destruction behavior and rebuild parity remain unproven",
        ],
        ["CDXGame__dtor_thunk", "CGame__dtor"],
        ["dxgame", "destructor", "jump-thunk", "owner-corrected", "signature-hardened", "comment-hardened"],
        ["CGame__ctor_like_0046c2d0"],
    ),
    "0x00541f10": target(
        "CDXGame__ctor",
        "void * __fastcall CDXGame__ctor(void * this)",
        [
            "Wave385 owner correction",
            "CDXGame constructor",
            "calls CGame__ctor",
            "installs the CDXGame secondary vtable",
            "runtime DirectX game construction and rebuild parity remain unproven",
        ],
        ["CDXGame__ctor", "CGame__ctor(this)", "PTR_CGame__HandleEvent_005e509c"],
        ["dxgame", "constructor", "owner-corrected", "signature-hardened", "comment-hardened"],
        ["CFrontEndVideo__CFrontEndVideo"],
    ),
    "0x00541f30": target(
        "CDXGame__scalar_deleting_dtor",
        "void * __thiscall CDXGame__scalar_deleting_dtor(void * this, byte flags)",
        [
            "Wave385 owner correction",
            "scalar-deleting destructor wrapper for CDXGame",
            "calls CDXGame__dtor_thunk",
            "optionally frees this through OID__FreeObject",
            "runtime deletion behavior and rebuild parity remain unproven",
        ],
        ["CDXGame__scalar_deleting_dtor", "CDXGame__dtor_thunk(this)", "OID__FreeObject(this)"],
        ["dxgame", "destructor", "scalar-deleting-dtor", "owner-corrected", "signature-hardened", "comment-hardened"],
        ["CFrontEndVideo__scalar_dtor"],
    ),
    "0x00541120": target(
        "CBinkOpenThread__ctor",
        "void * __fastcall CBinkOpenThread__ctor(void * this)",
        [
            "Wave385 owner correction",
            "CBinkOpenThread constructor",
            "calls the CWaitingThread constructor",
            "installs vtable 0x005e5078",
            "adjacent vtable-slot body at 0x00541140",
            "runtime Bink thread behavior, and rebuild parity remain unproven",
        ],
        ["CBinkOpenThread__ctor", "CWaitingThread__ctor_like_00528bc0(this)", "PTR_LAB_005e5078"],
        ["bink-open-thread", "constructor", "owner-corrected", "signature-hardened", "comment-hardened"],
        ["CFrontEndVideo__dtor"],
    ),
}

INSTRUCTION_EVIDENCE = [
    ("0x0046c210", "0x0046c219", "MOV", "dword ptr [EAX], 0x5d9388", "c7 00 88 93 5d 00"),
    ("0x0046c210", "0x0046c25e", "MOV", "dword ptr [EAX], 0x5dbbb4", "c7 00 b4 bb 5d 00"),
    ("0x0046c2b0", "0x0046c2b3", "CALL", "0x0046c2d0", "e8 18 00 00 00"),
    ("0x0046c2b0", "0x0046c2cd", "RET", "0x4", "c2 04 00"),
    ("0x0046c2d0", "0x0046c315", "CALL", "0x004e5bd0", "e8 b6 98 07 00"),
    ("0x0046c2d0", "0x0046c348", "CALL", "0x004bac40", "e8 f3 e8 04 00"),
    ("0x00541f00", "0x00541f00", "JMP", "0x0046c2d0", "e9 cb a3 f2 ff"),
    ("0x00541f10", "0x00541f13", "CALL", "0x0046c210", "e8 f8 a2 f2 ff"),
    ("0x00541f10", "0x00541f18", "MOV", "dword ptr [ESI], 0x5e509c", "c7 06 9c 50 5e 00"),
    ("0x00541f30", "0x00541f33", "CALL", "0x00541f00", "e8 c8 ff ff ff"),
    ("0x00541f30", "0x00541f4d", "RET", "0x4", "c2 04 00"),
    ("0x00541120", "0x00541123", "CALL", "0x00528bc0", "e8 98 7a fe ff"),
    ("0x00541120", "0x00541128", "MOV", "dword ptr [ESI], 0x5e5078", "c7 06 78 50 5e 00"),
]

VTABLE_TYPES = {
    "0x005dbbb4": "CGame",
    "0x005d9388": "IController",
    "0x005e509c": "CDXGame",
    "0x005e5078": "CBinkOpenThread",
}

VTABLE_SLOT_EVIDENCE = [
    ("0x005dbbb4", "1", "0x0046c2b0", "CGame__scalar_deleting_dtor"),
    ("0x005e509c", "1", "0x00541f30", "CDXGame__scalar_deleting_dtor"),
]

DEFERRED_BOUNDARIES = {
    "0x00541140": "CBinkOpenThread vtable slot body remains deferred and must not be claimed as repaired by Wave385",
}

OVERCLAIM_TOKENS = [
    "runtime behavior proven",
    "runtime proof",
    "rebuild parity proven",
    "exact layout proven",
    "fully recovered",
]


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    if not value or value in {"<none>", "none"}:
        return value
    return "0x" + value.zfill(8)


def unescape_tsv(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        for key, value in list(row.items()):
            row[key] = unescape_tsv(value or "")
    return rows


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def decompile_text_for(decompile_dir: Path, address: str) -> str:
    prefix = normalize_address(address)[2:]
    return "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in decompile_dir.glob(f"{prefix}_*.c")
    )


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def has_summary(text: str, *, updated: int | None = None, bad: int = 0, missing: int = 0) -> bool:
    match = re.search(r"SUMMARY: (?P<body>.+)", text)
    if not match:
        return False
    fields: dict[str, int] = {}
    for part in match.group("body").split():
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        try:
            fields[key] = int(value)
        except ValueError:
            return False
    if updated is not None and fields.get("updated") != updated:
        return False
    return fields.get("bad") == bad and fields.get("missing") == missing


def instruction_hit(rows: list[dict[str, str]], target: str, instruction_addr: str, mnemonic: str, operands: str, bytes_: str) -> bool:
    target_norm = normalize_address(target)
    instruction_norm = normalize_address(instruction_addr)
    return any(
        normalize_address(row.get("target_addr", "")) == target_norm
        and normalize_address(row.get("instruction_addr", "")) == instruction_norm
        and row.get("mnemonic", "") == mnemonic
        and row.get("operands", "") == operands
        and row.get("bytes", "") == bytes_
        for row in rows
    )


def build_report(
    *,
    root: Path = DEFAULT_ROOT,
    dry_log_path: Path | None = None,
    apply_log_path: Path | None = None,
    metadata_path: Path | None = None,
    tags_path: Path | None = None,
    instructions_path: Path | None = None,
    decompile_dir: Path | None = None,
    vtable_type_path: Path | None = None,
    secondary_vtable_type_path: Path | None = None,
    vtable_slots_path: Path | None = None,
    secondary_vtable_slots_path: Path | None = None,
    bink_boundary_metadata_path: Path | None = None,
) -> dict[str, object]:
    dry_log_path = dry_log_path or root / "game_dxgame_wave385_dry.log"
    apply_log_path = apply_log_path or root / "game_dxgame_wave385_apply.log"
    metadata_path = metadata_path or root / "metadata_after.tsv"
    tags_path = tags_path or root / "tags_after.tsv"
    instructions_path = instructions_path or root / "instructions_after.tsv"
    decompile_dir = decompile_dir or root / "decompile_after"
    vtable_type_path = vtable_type_path or root / "vtable_type_names_after.tsv"
    secondary_vtable_type_path = secondary_vtable_type_path or root / "secondary_vtable_type_names_after.tsv"
    vtable_slots_path = vtable_slots_path or root / "vtable_slots_after.tsv"
    secondary_vtable_slots_path = secondary_vtable_slots_path or root / "secondary_vtable_slots_after.tsv"
    bink_boundary_metadata_path = bink_boundary_metadata_path or root / "bink_deferred_boundary_after.tsv"

    failures: list[str] = []
    dry_log = read_text(dry_log_path)
    apply_log = read_text(apply_log_path)
    metadata_rows = read_tsv(metadata_path)
    tag_rows = read_tsv(tags_path)
    instruction_rows = read_tsv(instructions_path)
    vtable_type_rows = read_tsv(vtable_type_path) + read_tsv(secondary_vtable_type_path)
    vtable_slot_rows = read_tsv(vtable_slots_path) + read_tsv(secondary_vtable_slots_path)
    bink_boundary_rows = read_tsv(bink_boundary_metadata_path)

    if dry_log and not has_summary(dry_log):
        failures.append("dry log missing clean SUMMARY")
    if not has_summary(apply_log, updated=len(TARGETS)):
        failures.append("apply log missing expected clean SUMMARY")
    if "REPORT: Save succeeded" not in apply_log:
        failures.append("apply log missing Ghidra save success")

    metadata_by_addr = {normalize_address(row.get("address", "")): row for row in metadata_rows}
    tags_by_addr = {normalize_address(row.get("address", "")): row for row in tag_rows}

    for address, spec in TARGETS.items():
        row = metadata_by_addr.get(normalize_address(address))
        if row is None:
            failures.append(f"metadata missing {address}")
            continue
        if row.get("status") != "OK":
            failures.append(f"metadata status mismatch {address}: {row.get('status')}")
        if row.get("name") != spec["name"]:
            failures.append(f"name mismatch {address}: {row.get('name')} != {spec['name']}")
        if row.get("signature") != spec["signature"]:
            failures.append(f"signature mismatch {address}: {row.get('signature')} != {spec['signature']}")
        comment = row.get("comment", "")
        for token in spec["commentTokens"]:  # type: ignore[index]
            if str(token) not in comment:
                failures.append(f"comment token missing {address}: {token}")
        for token in OVERCLAIM_TOKENS:
            if token in comment:
                failures.append(f"comment overclaim {address}: {token}")
        for stale_name in spec["staleNames"]:  # type: ignore[index]
            if row.get("name") == stale_name or stale_name in comment:
                failures.append(f"stale name still present {address}: {stale_name}")

        tag_row = tags_by_addr.get(normalize_address(address))
        if tag_row is None:
            failures.append(f"tags missing {address}")
        else:
            actual_tags = set(filter(None, tag_row.get("tags", "").split(";")))
            expected_tags = COMMON_TAGS | set(str(tag) for tag in spec["tags"])  # type: ignore[arg-type]
            missing_tags = expected_tags - actual_tags
            if missing_tags:
                failures.append(f"tag mismatch {address}: missing {sorted(missing_tags)}")

        decompile_text = decompile_text_for(decompile_dir, address)
        if not decompile_text:
            failures.append(f"decompile missing {address}")
        for token in spec["decompileTokens"]:  # type: ignore[index]
            if str(token) not in decompile_text:
                failures.append(f"decompile token missing {address}: {token}")
        for stale_name in spec["staleNames"]:  # type: ignore[index]
            if stale_name in decompile_text:
                failures.append(f"stale decompile name {address}: {stale_name}")

    instruction_hits = 0
    for target_addr, instruction_addr, mnemonic, operands, bytes_ in INSTRUCTION_EVIDENCE:
        if instruction_hit(instruction_rows, target_addr, instruction_addr, mnemonic, operands, bytes_):
            instruction_hits += 1
        else:
            failures.append(f"instruction evidence missing {target_addr} {instruction_addr} {mnemonic} {operands}")

    type_by_vtable = {normalize_address(row.get("vtable", "")): row.get("demangled_type_name", "") for row in vtable_type_rows}
    for vtable, expected_type in VTABLE_TYPES.items():
        actual_type = type_by_vtable.get(normalize_address(vtable))
        if actual_type != expected_type:
            failures.append(f"vtable type mismatch {vtable}: {actual_type} != {expected_type}")

    slot_hits = 0
    for vtable, slot_index, pointer, name in VTABLE_SLOT_EVIDENCE:
        found = any(
            normalize_address(row.get("vtable", "")) == normalize_address(vtable)
            and row.get("slot_index") == slot_index
            and normalize_address(row.get("pointer_addr", "")) == normalize_address(pointer)
            and row.get("function_name") == name
            for row in vtable_slot_rows
        )
        if found:
            slot_hits += 1
        else:
            failures.append(f"vtable slot evidence missing {vtable} slot {slot_index} -> {name}")

    boundary_by_addr = {normalize_address(row.get("address", "")): row for row in bink_boundary_rows}
    for address, reason in DEFERRED_BOUNDARIES.items():
        row = boundary_by_addr.get(normalize_address(address))
        if row is not None and row.get("status") != "MISSING":
            failures.append(f"deferred boundary unexpectedly present {address}: {reason}")

    report: dict[str, object] = {
        "status": "PASS" if not failures else "FAIL",
        "root": relative(root),
        "summary": {
            "targets": len(TARGETS),
            "instructionEvidenceHits": instruction_hits,
            "vtableTypeHits": sum(1 for v, t in VTABLE_TYPES.items() if type_by_vtable.get(normalize_address(v)) == t),
            "vtableSlotHits": slot_hits,
            "deferredBoundaries": len(DEFERRED_BOUNDARIES),
            "metadataRows": len(metadata_rows),
            "tagRows": len(tag_rows),
        },
        "files": {
            "metadata": relative(metadata_path),
            "tags": relative(tags_path),
            "instructions": relative(instructions_path),
            "decompileDir": relative(decompile_dir),
            "vtableTypes": [relative(vtable_type_path), relative(secondary_vtable_type_path)],
            "vtableSlots": [relative(vtable_slots_path), relative(secondary_vtable_slots_path)],
            "binkDeferredBoundary": relative(bink_boundary_metadata_path),
            "dryLog": relative(dry_log_path),
            "applyLog": relative(apply_log_path),
        },
        "failures": failures,
    }
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    report = build_report(root=args.root)
    args.root.mkdir(parents=True, exist_ok=True)
    (args.root / OUTPUT_NAME).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(
            f"Wave385 CGame/CDXGame probe: {report['status']} "
            f"targets={report['summary']['targets']} "
            f"instruction_hits={report['summary']['instructionEvidenceHits']} "
            f"vtable_type_hits={report['summary']['vtableTypeHits']} "
            f"vtable_slot_hits={report['summary']['vtableSlotHits']}"
        )
        if report["failures"]:
            for failure in report["failures"]:
                print(f"FAIL: {failure}", file=sys.stderr)

    return 0 if report["status"] == "PASS" or not args.check else 1


if __name__ == "__main__":
    raise SystemExit(main())
