#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Verify the CMech-family definition-record +0x130 field lifecycle.

This is a read-only, pristine-specimen proof. It joins the current 8,329-row
function geometry to strict MSVC RTTI, then checks the exact allocation,
default, property-apply, based-on copy, runtime attachment, consumers, and
registry teardown anchors for the Unit-definition dword at +0x130.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable

import capstone
from capstone.x86 import X86_OP_MEM

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import re_rtti_vtables as rtti  # noqa: E402

PRISTINE_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
NAME_TABLE_RELATIVE = Path("reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv")
NAME_TABLE_SHA256 = "4590dff93f4ee85c5a5c3450139b2e696118646af3401f6eb9719dc4237d3213"
NAME_TABLE_ROWS = 8_329
FIELD_OFFSET = 0x130
CONTROL_OFFSET = 0x128

BODY_RANGES = {
    "definition_factory": (
        0x0042EE90,
        0x0042EFC0,
        "f973f476ac611c1ea48da273705ac6cfa93fd4e7fbaf96de6e3f4d6dc7970529",
    ),
    "definition_defaults": (
        0x0042EFD0,
        0x0042F218,
        "88bf8da7dd8127b968e62e7400a299a13ae8d1fa4041cb7311dea8d95e9e21e7",
    ),
    "shatter_apply": (
        0x00432DC0,
        0x00432DE8,
        "6b590373f8453f12d09b426aa69ca4404c5ff2c54bbad6b34fbdb46a2a3d2016",
    ),
    "based_on_apply": (
        0x004332E0,
        0x00433383,
        "cf5deef1f9dd35ab06aca9ed2586439eabbd1515b81bad89b84c1429cea60b10",
    ),
    "based_on_copy": (
        0x00433390,
        0x00433CD3,
        "f41c3a1dd0d000032b4868bbdda3a3d5811ba94be54fa4c23250ce3669193cb5",
    ),
    "slot71_consumer": (
        0x0049FDB0,
        0x004A009F,
        "78edc91a031827e359f3ae74a65d9a30bcd1d7d42fb47fcf87d86d2519fc0004",
    ),
    "slot50_consumer": (
        0x004A00A0,
        0x004A0119,
        "949f82f92d813ddce68a84141f495e1a7b3528a27feb14052c5259b99c3ee007",
    ),
    "unit_constructor": (
        0x004F7E90,
        0x004F8132,
        "2cab5cde89e806bd13d6a24f625f47bf2a532aa2ea367ef0ae5d4253d12a80f6",
    ),
    "unit_init": (
        0x004F86D0,
        0x004F91F1,
        "dc3c02ae147e701c9840db77698dd0277501cab30f94f897179c06c762f7b7fd",
    ),
    "definition_registry_clear": (
        0x00510A90,
        0x00510E57,
        "e6ff0006d600346466010a998298ee40773022273f440c9edc8421b161aff890",
    ),
    "definition_entry_free": (
        0x005110F0,
        0x00511392,
        "39f1fcfa67567931cc054b0753019f45cc4c0a08d6188420144d5918a3aa4cce",
    ),
}

EXACT_BYTES = {
    "allocation_size_0x1ac": (0x0042EEB3, "68ac010000"),
    "default_zero": (0x0042F18A, "89ab30010000"),
    "shatter_true": (0x00432DCB, "c7803001000001000000"),
    "shatter_false": (0x00432DDC, "c7813001000000000000"),
    "based_on_read": (0x00433B4D, "8b8530010000"),
    "based_on_write": (0x00433B53, "898330010000"),
    "slot71_read": (0x0049FDDD, "39b830010000"),
    "slot50_read": (0x004A00AA, "8b8830010000"),
    "unit_profile_clear": (0x004F8051, "89be64010000"),
    "unit_profile_source": (0x004F8700, "8b8fbc030000"),
    "unit_profile_attach": (0x004F870D, "898b64010000"),
    "shatter_factory_vptr": (0x00432361, "c700349b5d00"),
    "shatter_factory_type_0x41": (0x00432367, "c7400441000000"),
    "shatter_payload_default": (0x0043236E, "894808"),
    "shatter_factory_case_0x41_dispatch": (0x00432A08, "42234300"),
    "shatter_payload_size": (0x004DB8C0, "b804000000c3"),
    "shatter_payload_read": (0x00434B60, "83c1086a04518b4c240ce8013a1100c20400"),
    "unit_based_on_registry": (0x004332EB, "8b0dfc538500"),
    "unit_based_on_null_copy_call": (0x00433365, "e826000000"),
    "unit_based_on_source_copy_call": (0x00433378, "e813000000"),
    "registry_unit_list_test": (0x00510C03, "393dfc538500"),
    "registry_unit_entry_free_call": (0x00510C2E, "e8bd040000"),
    "registry_unit_record_free_call": (0x00510C39, "e8e2850300"),
    "registry_unit_set_zero": (0x00510DE9, "893dfc538500"),
    "control_indiscriminate_true": (0x00432D9B, "c7802801000001000000"),
    "control_indiscriminate_false": (0x00432DAC, "c7812801000000000000"),
}

EXPECTED_SLOTS = {
    ("CUnitShatter", 0x005D9B34, 0): 0x00434100,
    ("CUnitShatter", 0x005D9B34, 1): 0x00432DC0,
    ("CUnitShatter", 0x005D9B34, 2): 0x004DB8C0,
    ("CUnitShatter", 0x005D9B34, 3): 0x00434B60,
    ("CUnitIndiscriminate", 0x005D98F0, 1): 0x00432D90,
    ("CWarspite", 0x005E0684, 50): 0x004A00A0,
    ("CWarspite", 0x005E0684, 71): 0x0049FDB0,
    ("CGillM", 0x005E0B30, 50): 0x004A00A0,
    ("CGillM", 0x005E0B30, 71): 0x0049FDB0,
    ("CThunderHead", 0x005E0FE0, 50): 0x004A00A0,
    ("CThunderHead", 0x005E0FE0, 71): 0x0049FDB0,
    ("CMech", 0x005E3074, 50): 0x004A00A0,
    ("CMech", 0x005E3074, 71): 0x0049FDB0,
}

EXPECTED_PROFILE_FIELD_SITES = {
    0x0042F18A,
    0x00432DCB,
    0x00432DDC,
    0x00433B4D,
    0x00433B53,
    0x0049FDDD,
    0x004A00AA,
}
TARGET_PROFILE_FIELD_SITES_BY_FUNCTION = {
    "CUnitAI__InitDefaults": {0x0042F18A},
    "CUnitShatter__VFunc_1_00432dc0": {0x00432DCB, 0x00432DDC},
    "CComponentBasedOn__CopyFrom": {0x00433B4D, 0x00433B53},
    "CMech__VFunc_71_SpawnGenericMeshBreakEffects_0049fdb0": {0x0049FDDD},
    "CMech__VFunc_50_004a00a0": {0x004A00AA},
}
EXPECTED_DISPLACEMENT_130_INSTRUCTIONS = 116
EXPECTED_RAW_130_OCCURRENCES = 156
EXPECTED_RAW_130_BY_SECTION = {".text": 155, ".data": 1}


class EvidenceError(ValueError):
    """The measured image or tracked geometry violates a proof invariant."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise EvidenceError(message)


def va_bytes(image: rtti.PEImage, va: int, size: int) -> bytes:
    offset = image.va_to_file(va, size)
    if offset is None:
        raise EvidenceError(f"unmapped bytes at 0x{va:08x} size {size}")
    return image.data[offset : offset + size]


def body_bytes(image: rtti.PEImage, start: int, end: int) -> bytes:
    return va_bytes(image, start, end - start + 1)


def parse_name_table(path: Path) -> tuple[list[tuple[int, int, str]], dict[str, object]]:
    data = path.read_bytes()
    require(sha256_bytes(data) == NAME_TABLE_SHA256, "current name-table hash differs")
    lines = (line for line in data.decode("utf-8").splitlines() if not line.startswith("#"))
    reader = csv.DictReader(lines, delimiter="\t")
    rows = []
    for row in reader:
        rows.append((int(row["bodyMin"], 16), int(row["bodyMax"], 16), row["name"]))
    require(len(rows) == NAME_TABLE_ROWS, "current name-table row count differs")
    require(len({start for start, _end, _name in rows}) == NAME_TABLE_ROWS, "duplicate function entry")
    return rows, {
        "path": NAME_TABLE_RELATIVE.as_posix(),
        "rows": len(rows),
        "sha256": sha256_bytes(data),
    }


def decoded_displacement_sites(
    image: rtti.PEImage,
    rows: Iterable[tuple[int, int, str]],
    displacement: int,
) -> list[dict[str, object]]:
    decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    decoder.detail = True
    sites = []
    for start, end, name in rows:
        for instruction in decoder.disasm(body_bytes(image, start, end), start):
            if any(
                operand.type == X86_OP_MEM and operand.mem.disp == displacement
                for operand in instruction.operands
            ):
                sites.append(
                    {
                        "va": instruction.address,
                        "function": name,
                        "mnemonic": instruction.mnemonic,
                        "operands": instruction.op_str,
                    }
                )
    return sites


def raw_needle_census(image: rtti.PEImage, needle: bytes) -> tuple[int, dict[str, int]]:
    hits = []
    cursor = 0
    while True:
        hit = image.data.find(needle, cursor)
        if hit < 0:
            break
        hits.append(hit)
        cursor = hit + 1
    by_section: Counter[str] = Counter()
    for hit in hits:
        for section in image.sections:
            if section.raw_offset <= hit < section.raw_offset + section.raw_size:
                by_section[section.name] += 1
                break
    return len(hits), dict(sorted(by_section.items()))


def partition_decoded_sites(sites: list[dict[str, object]]) -> dict[str, object]:
    output = []
    counts: Counter[str] = Counter()
    for row in sites:
        va = int(row["va"])
        operands = str(row["operands"])
        if va in EXPECTED_PROFILE_FIELD_SITES:
            classification = "TARGET_PROFILE_FIELD"
        elif str(row["mnemonic"]) == "call" and "+ 0x130]" in operands:
            classification = "VTABLE_SLOT_76"
        elif "[esp" in operands:
            classification = "STACK_FRAME"
        else:
            classification = "OTHER_OBJECT_LAYOUT"
        counts[classification] += 1
        output.append(
            {
                "va": f"0x{va:08x}",
                "function": row["function"],
                "mnemonic": row["mnemonic"],
                "operands": operands,
                "classification": classification,
            }
        )
    require(len(output) == sum(counts.values()), "decoded +0x130 partition is not exhaustive")
    require(
        {int(row["va"], 16) for row in output if row["classification"] == "TARGET_PROFILE_FIELD"}
        == EXPECTED_PROFILE_FIELD_SITES,
        "target profile-field partition differs",
    )
    return {"counts": dict(sorted(counts.items())), "sites": output}


def validate_exact_bytes(image: rtti.PEImage) -> dict[str, str]:
    observed = {}
    for label, (va, expected_hex) in EXACT_BYTES.items():
        expected = bytes.fromhex(expected_hex)
        actual = va_bytes(image, va, len(expected))
        require(actual == expected, f"{label} bytes differ at 0x{va:08x}")
        observed[label] = f"0x{va:08x}"
    return observed


def validate_bodies(image: rtti.PEImage) -> dict[str, dict[str, object]]:
    output = {}
    for label, (start, end, expected_hash) in BODY_RANGES.items():
        data = body_bytes(image, start, end)
        actual_hash = sha256_bytes(data)
        require(actual_hash == expected_hash, f"{label} body hash differs")
        output[label] = {
            "start": f"0x{start:08x}",
            "endInclusive": f"0x{end:08x}",
            "bytes": len(data),
            "sha256": actual_hash,
        }
    return output


def validate_rtti(data: bytes) -> dict[str, object]:
    census = rtti.parse_rtti(data)
    rtti.validate_pristine_census(census)
    slots = {(row.class_name, row.vtable_va, row.slot): row.function_va for row in census.slots}
    for key, expected in EXPECTED_SLOTS.items():
        require(slots.get(key) == expected, f"strict RTTI slot differs: {key}")

    hierarchy_rows = {
        hierarchy.root_class: [row.descriptor.class_name for row in hierarchy.rows]
        for hierarchy in census.hierarchies.values()
        if hierarchy.root_class in {"CUnitShatter", "CWarspite", "CGillM", "CThunderHead", "CMech"}
    }
    require(
        hierarchy_rows.get("CUnitShatter") == ["CUnitShatter", "CPhysicsUnitValue"],
        "CUnitShatter hierarchy differs",
    )
    for receiver in ("CWarspite", "CGillM", "CThunderHead"):
        require(hierarchy_rows[receiver][:4] == [receiver, "CMech", "CGroundUnit", "CUnit"], f"{receiver} hierarchy differs")
    require(hierarchy_rows["CMech"][:3] == ["CMech", "CGroundUnit", "CUnit"], "CMech hierarchy differs")

    slot_rows = []
    for (class_name, vtable, slot), function in sorted(EXPECTED_SLOTS.items()):
        slot_rows.append(
            {
                "class": class_name,
                "vtable": f"0x{vtable:08x}",
                "slot": slot,
                "function": f"0x{function:08x}",
            }
        )
    return {"counts": census.counts(), "slots": slot_rows, "hierarchies": hierarchy_rows}


def analyze_bytes(data: bytes, name_table: Path, *, verify_identity: bool = True) -> dict[str, object]:
    specimen_hash = sha256_bytes(data)
    if verify_identity:
        require(specimen_hash == PRISTINE_SHA256, "not the pristine specimen")
    image = rtti.PEImage(data)
    rows, names = parse_name_table(name_table)
    exact = validate_exact_bytes(image)
    bodies = validate_bodies(image)

    decoded = decoded_displacement_sites(image, rows, FIELD_OFFSET)
    require(len(decoded) == EXPECTED_DISPLACEMENT_130_INSTRUCTIONS, "decoded +0x130 census differs")
    for function, expected_sites in TARGET_PROFILE_FIELD_SITES_BY_FUNCTION.items():
        observed_sites = {int(row["va"]) for row in decoded if row["function"] == function}
        require(observed_sites == expected_sites, f"{function} +0x130 site set differs")
    partition = partition_decoded_sites(decoded)

    slot50_start, slot50_end, _slot50_hash = BODY_RANGES["slot50_consumer"]
    slot71_start, slot71_end, _slot71_hash = BODY_RANGES["slot71_consumer"]
    slot50_sites = [row for row in decoded if slot50_start <= int(row["va"]) <= slot50_end]
    slot71_sites = [row for row in decoded if slot71_start <= int(row["va"]) <= slot71_end]
    require([row["va"] for row in slot50_sites] == [0x004A00AA], "slot-50 +0x130 access set differs")
    require([row["va"] for row in slot71_sites] == [0x0049FDDD], "slot-71 +0x130 access set differs")

    raw_count, raw_by_section = raw_needle_census(image, FIELD_OFFSET.to_bytes(4, "little"))
    require(raw_count == EXPECTED_RAW_130_OCCURRENCES, "whole-image raw +0x130 operand census differs")
    require(raw_by_section == EXPECTED_RAW_130_BY_SECTION, "whole-image raw +0x130 section split differs")

    control_decoded = decoded_displacement_sites(image, rows, CONTROL_OFFSET)
    control_addresses = {int(row["va"]) for row in control_decoded}
    require({0x00432D9B, 0x00432DAC} <= control_addresses, "adverse-control +0x128 writer missing")

    return {
        "schema": "bea.cmech-profile-field-static.v1",
        "specimen": {"bytes": len(data), "sha256": specimen_hash},
        "nameTable": names,
        "wholeImageOperandCensus": {
            "rawLittleEndian0130Occurrences": raw_count,
            "rawBySection": raw_by_section,
            "decodedCurrentFunctionRangeInstructions": len(decoded),
            "decodedPartition": partition,
        },
        "profileField": {
            "recordOwner": "Unit/definition record in DAT_008553fc",
            "offset": "0x130",
            "authoredPropertyEvidence": "strict RTTI CUnitShatter; exact member spelling unavailable",
            "serializedUnitValueType": "0x41",
            "payloadBytes": 4,
            "inputEquivalenceClasses": ["zero", "nonzero"],
            "storedDomain": [0, 1],
            "default": 0,
            "directLifecycleSites": [f"0x{va:08x}" for va in sorted(EXPECTED_PROFILE_FIELD_SITES)],
            "consumers": {
                "slot71GenericMeshBreakEffectsGate": "0x0049fddd",
                "slot50DestructionContinuationGate": "0x004a00aa",
            },
        },
        "runtimeAttachment": {
            "constructorClearsUnitPlus164": exact["unit_profile_clear"],
            "initReadsInitPlus3bc": exact["unit_profile_source"],
            "initStoresUnitPlus164": exact["unit_profile_attach"],
        },
        "ownership": {
            "allocation": exact["allocation_size_0x1ac"],
            "initialization": exact["default_zero"],
            "propertyFactoryDispatch": exact["shatter_factory_case_0x41_dispatch"],
            "propertyApply": [exact["shatter_true"], exact["shatter_false"]],
            "basedOnDispatch": [
                exact["unit_based_on_registry"],
                exact["unit_based_on_null_copy_call"],
                exact["unit_based_on_source_copy_call"],
            ],
            "basedOnCopy": [exact["based_on_read"], exact["based_on_write"]],
            "registryEntryTeardown": exact["registry_unit_entry_free_call"],
            "recordFree": exact["registry_unit_record_free_call"],
            "registryZero": exact["registry_unit_set_zero"],
        },
        "adverseControl": {
            "offset": "0x128",
            "propertyClass": "CUnitIndiscriminate",
            "writer": "0x00432d90",
            "sites": [exact["control_indiscriminate_true"], exact["control_indiscriminate_false"]],
            "notMergedWithTarget": True,
        },
        "bodies": bodies,
        "rtti": validate_rtti(data),
    }


def analyze(specimen: Path, name_table: Path) -> dict[str, object]:
    return analyze_bytes(specimen.read_bytes(), name_table)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("specimen", type=Path)
    parser.add_argument("--name-table", type=Path, default=ROOT / NAME_TABLE_RELATIVE)
    parser.add_argument("--out-json", type=Path)
    args = parser.parse_args()
    try:
        result = analyze(args.specimen, args.name_table)
        rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
        if args.out_json:
            args.out_json.parent.mkdir(parents=True, exist_ok=True)
            args.out_json.write_text(rendered, encoding="utf-8", newline="\n")
            print(f"wrote: {args.out_json}")
        else:
            print(rendered, end="")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
