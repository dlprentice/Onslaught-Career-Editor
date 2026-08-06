#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Join shipped ``__FILE__`` plates to memory types and allocation operands.

This owner is intentionally specimen- and evidence-bound.  It consumes the
frozen source-unit and copied-runtime memory-dump censuses, re-decodes every
plate from the pristine executable, and publishes an atomic READY bundle.  It
does not infer types from names, function hulls, or decompiler text.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import stat
import struct
import sys
import tempfile
from typing import Any, Iterable, Mapping, Sequence

from capstone import (
    Cs,
    CS_ARCH_X86,
    CS_GRP_INT,
    CS_GRP_IRET,
    CS_GRP_JUMP,
    CS_GRP_RET,
    CS_MODE_32,
    CS_OP_IMM,
    CS_OP_REG,
)


SCHEMA = "bea.re.source-allocation-census.v1"
STATUS = "READY"
SPECIMEN_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
SPECIMEN_BYTES = 2_506_752
SOURCE_READY_SHA256 = "63099dbf88d031bcbc186303627f6692e157cc80a270670018a5ed68744ff2b4"
SOURCE_SITES_SHA256 = "8a3b0f26182162a57e00059c2882297d041ada4ed88938117adc9d4d0a7dc3a1"
MEMORY_READY_SHA256 = "f096a0b88c10999ff69615564483761a87fc3a36fe63c23e8cff06278a3ad6cd"
MEMORY_TYPES_SHA256 = "a8067835e57bc5012df56a6959a50c1aea9dfebf59aeebc80b174bbeb2e29e5f"
MEMORY_TABLE_VA = 0x0062E140
MEMORY_TABLE_RECORDS = 129
MEMORY_TABLE_STRIDE = 0x28
MEMORY_TABLE_SHA256 = "13db2e30b23320dc98e5d59d9e45333b309408b714eb43f3bb5895703ba35ec9"
MEMORY_CTOR_START = 0x00548D70
MEMORY_CTOR_END = 0x00548EBD
MEMORY_CTOR_SHA256 = "ed431d0f9e100a859a8891b205ebb4244faa5f6686216d3efb2edf53563b8b08"
PRIMARY_TARGETS = frozenset((0x005490E0, 0x004A1810))
FREE_TARGET = 0x00449D40

EXPECTED_COUNTS = {
    "sites": 1870,
    "primary": 1377,
    "unwind": 493,
    "immediateTypes": 1867,
    "localConstantTypes": 1,
    "dynamicTypes": 2,
    "runtimeLabeledTypes": 1868,
    "semanticNamedTypes": 1860,
    "fallbackTypeSites": 8,
    "primaryImmediateTypes": 1374,
    "primaryRegisterTypes": 3,
    "primaryImmediateSizes": 1060,
    "primaryRegisterSizes": 317,
    "unwindImmediateTypes": 493,
    "type41Sites": 2,
    "type42Sites": 8,
    "functionOwnedSites": 1845,
    "residualOwnedSites": 25,
    "ownerBoundaryCrossings": 1,
}

SOURCE_COLUMNS = (
    "siteKey", "siteVa", "siteRva", "fileOffset", "pathStringKey",
    "canonicalPathKey", "canonicalRelativePath", "pathKind", "pathPushBytes",
    "instructionVerdict", "lineInstructionVa", "lineEncoding", "lineValue",
    "lineVerdict", "firstDirectCallVa", "firstDirectCallTargetVa",
    "callOffsetBytes", "plateClass", "plateStartVa", "plateEndExclusiveVa",
    "plateBytesSha256", "pathOwnerKind", "pathOwnerEntityKey",
    "pathOwnerIntervalStartVa", "pathOwnerIntervalEndVa", "pathFunctionEntryVa",
    "pathFunctionName", "pathFunctionBodyRangeSetSha256",
    "pathResidualObservationState", "pathResidualClassification", "callOwnerKind",
    "callOwnerEntityKey", "callOwnerIntervalStartVa", "callOwnerIntervalEndVa",
    "ownerBoundaryCrossing", "evidenceGrade",
)
MEMORY_COLUMNS = (
    "snapshot", "memoryTypeIndex", "memoryTypeName", "blockCount",
    "payloadBytes", "accountedBytes", "reportedDeltaBytes",
    "reportedFlagZeroBlockCount", "reportedFlagZeroPayloadBytes",
    "reportedFlagZeroAccountedBytes", "reportedFlagNonzeroBlockCount",
    "reportedFlagNonzeroPayloadBytes", "reportedFlagNonzeroAccountedBytes",
)
SITE_COLUMNS = (
    "siteKey", "siteVa", "canonicalRelativePath", "lineValue", "plateClass",
    "callTargetVa", "pathOwnerKind", "pathOwnerEntityKey", "pathFunctionEntryVa",
    "pathFunctionName", "callOwnerKind", "callOwnerEntityKey",
    "ownerBoundaryCrossing", "typeOperandKind", "typeOperand", "typeValue",
    "typeResolution", "logicalTypeName", "sizeOperandKind", "sizeOperand",
    "sizeValue", "pointerOperandKind", "pointerOperand", "plateBytesSha256",
)
PHYSICAL_COLUMNS = (
    "physicalOrdinal", "recordVa", "memoryTypeIndex", "memoryTypeName", "maxSize",
)
LOGICAL_COLUMNS = (
    "memoryTypeIndex", "memoryTypeName", "physicalOrdinal", "mappingDisposition",
    "primaryPlateCount", "unwindPlateCount",
)
OWNER_COLUMNS = (
    "ownerKind", "ownerEntityKey", "functionEntryVa", "functionName",
    "primaryPlateCount", "unwindPlateCount", "immediateTypeCount",
    "localConstantTypeCount", "dynamicTypeCount", "distinctResolvedTypeIndices",
    "immediateSizeCount", "registerSizeCount", "ownerBoundaryCrossingCount",
)

OUTPUT_NAMES = (
    "source-allocation-owner.py",
    "memory-type-physical.tsv",
    "memory-type-logical.tsv",
    "source-allocation-sites.tsv",
    "owner-allocation-evidence.tsv",
    "allocation-census-summary.json",
)
INPUT_NAMES = (
    "source-unit-census.ready.json",
    "source-sites.tsv",
    "memory-dump-census.ready.json",
    "memory-types.tsv",
)
CLAIM_BOUNDARY = (
    "Immediate operands are exact shipped constants; register operands remain dynamic unless a no-entry, call-free linear interval has one dominating full-register immediate definition.",
    "The logical type names are corroborated by two frozen copied-runtime DumpMem snapshots; the physical table alone does not prove constructor search order.",
    "Logical type 42 has no physical table row and renders the runtime fallback 'Name not found'; its eight sites are runtime-labeled but not semantically named.",
    "Allocation size constants are requested byte counts, not recovered C++ sizeof identities or proof that allocation succeeded.",
    "Source paths and line plates are direct call-site evidence, not automatic translation-unit ownership for neighboring functions.",
    "The 0x00437a2c plate whose call crosses into residual 0x00437a3a remains evidence for a body-range repair, not authority to create a new function.",
    "This census mutates neither the specimen nor Ghidra and authorizes no function, name, signature, or rebuild promotion by itself.",
)


class CensusError(ValueError):
    """An input, derivation, or READY boundary failed closed."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CensusError(message)


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def stamp(path: Path, root: Path | None = None) -> dict[str, object]:
    require(path.is_file() and not is_linklike(path), f"not one plain file: {path}")
    label = path.resolve().relative_to(root.resolve()).as_posix() if root else str(path.resolve())
    return {"path": label, "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def render_tsv(columns: Sequence[str], rows: Iterable[Mapping[str, object]]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=list(columns), delimiter="\t", lineterminator="\n", extrasaction="raise")
    writer.writeheader()
    for row in rows:
        require(set(row) == set(columns), f"TSV column drift: {sorted(set(row) ^ set(columns))}")
        rendered = {key: str(row[key]) for key in columns}
        require(not any(any(c in value for c in "\t\r\n") for value in rendered.values()), "TSV cell contains a control separator")
        writer.writerow(rendered)
    return output.getvalue().encode("utf-8")


def read_tsv(path: Path, columns: Sequence[str], label: str) -> list[dict[str, str]]:
    content = path.read_bytes()
    require(content.endswith(b"\n") and not content.startswith(b"\xef\xbb\xbf"), f"{label} framing drift")
    reader = csv.DictReader(io.StringIO(content.decode("utf-8"), newline=""), delimiter="\t")
    require(tuple(reader.fieldnames or ()) == tuple(columns), f"{label} header drift")
    rows = list(reader)
    require(all(None not in row for row in rows), f"{label} row width drift")
    return rows


def read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise CensusError(f"cannot read {label}: {exc}") from exc
    require(isinstance(value, dict), f"{label} is not an object")
    return value


def is_linklike(path: Path) -> bool:
    """Identify symlinks, junctions, and other Windows reparse points."""
    if path.is_symlink():
        return True
    junction = getattr(path, "is_junction", None)
    if junction is not None and junction():
        return True
    attributes = getattr(path.lstat(), "st_file_attributes", 0)
    return bool(attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))


def validate_bundle_tree(bundle: Path) -> None:
    """Require the READY bundle to contain exactly its declared plain tree."""
    require(bundle.is_dir() and not is_linklike(bundle), "bundle is not one plain directory or is a reparse point")
    expected_root = {"READY.json", "inputs", *OUTPUT_NAMES}
    actual_root = {path.name for path in bundle.iterdir()}
    require(actual_root == expected_root, f"bundle root entry set differs: {sorted(actual_root ^ expected_root)}")
    inputs = bundle / "inputs"
    require(inputs.is_dir() and not is_linklike(inputs), "bundle inputs is not one plain directory or is a reparse point")
    actual_inputs = {path.name for path in inputs.iterdir()}
    require(actual_inputs == set(INPUT_NAMES), f"bundle input entry set differs: {sorted(actual_inputs ^ set(INPUT_NAMES))}")
    for name in ("READY.json", *OUTPUT_NAMES):
        path = bundle / name
        require(path.is_file() and not is_linklike(path), f"bundle entry is not one plain file: {name}")
    for name in INPUT_NAMES:
        path = inputs / name
        require(path.is_file() and not is_linklike(path), f"bundle input is not one plain file: {name}")


def parse_pe(data: bytes) -> dict[str, Any]:
    require(len(data) >= 0x100 and data[:2] == b"MZ", "specimen is not PE/MZ")
    pe_offset = struct.unpack_from("<I", data, 0x3C)[0]
    require(data[pe_offset:pe_offset + 4] == b"PE\0\0", "PE signature differs")
    section_count = struct.unpack_from("<H", data, pe_offset + 6)[0]
    optional_size = struct.unpack_from("<H", data, pe_offset + 20)[0]
    optional = pe_offset + 24
    require(struct.unpack_from("<H", data, optional)[0] == 0x10B, "specimen is not PE32")
    image_base = struct.unpack_from("<I", data, optional + 28)[0]
    section_table = optional + optional_size
    sections = []
    for index in range(section_count):
        offset = section_table + index * 40
        name = data[offset:offset + 8].split(b"\0", 1)[0].decode("ascii")
        virtual_size, rva, raw_size, raw_offset = struct.unpack_from("<IIII", data, offset + 8)
        sections.append((name, image_base + rva, virtual_size, raw_offset, raw_size))
    return {"imageBase": image_base, "sections": sections}


def va_to_offset(pe: Mapping[str, Any], address: int, size: int = 1) -> int:
    require(size >= 0, "negative mapped size")
    for _name, start, virtual_size, raw_offset, raw_size in pe["sections"]:
        span = max(virtual_size, raw_size)
        if start <= address and address + size <= start + span:
            relative = address - start
            require(relative + size <= raw_size, f"VA range is not file-backed: {address:#x}+{size}")
            return raw_offset + relative
    raise CensusError(f"VA range is unmapped: {address:#x}+{size}")


def validate_upstream(source_ready_path: Path, source_sites_path: Path, memory_ready_path: Path, memory_types_path: Path) -> None:
    require(sha256_file(source_ready_path) == SOURCE_READY_SHA256, "source READY hash differs")
    require(sha256_file(source_sites_path) == SOURCE_SITES_SHA256, "source-sites hash differs")
    source = read_json(source_ready_path, "source READY")
    require(source.get("schema") == "bea.re.source-unit-census.v1" and source.get("status") == "READY", "source READY identity differs")
    require(source.get("specimen", {}).get("sha256") == SPECIMEN_SHA256, "source READY specimen differs")
    source_stamp = source.get("outputs", {}).get("source-sites.tsv", {})
    require(source_stamp.get("bytes") == source_sites_path.stat().st_size and source_stamp.get("sha256") == SOURCE_SITES_SHA256, "source READY does not authenticate source-sites")

    require(sha256_file(memory_ready_path) == MEMORY_READY_SHA256, "memory READY hash differs")
    require(sha256_file(memory_types_path) == MEMORY_TYPES_SHA256, "memory-types hash differs")
    memory = read_json(memory_ready_path, "memory READY")
    require(memory.get("schema") == "bea.re.memory-dump-census-ready.v1" and memory.get("status") == "READY", "memory READY identity differs")
    memory_stamp = memory.get("outputs", {}).get("memory-types.tsv", {})
    require(memory_stamp.get("bytes") == memory_types_path.stat().st_size and memory_stamp.get("sha256") == MEMORY_TYPES_SHA256, "memory READY does not authenticate memory-types")


def parse_runtime_type_names(path: Path) -> tuple[str, ...]:
    rows = read_tsv(path, MEMORY_COLUMNS, "memory-types")
    require(len(rows) == 258, "memory-types must contain two 129-row snapshots")
    snapshots: dict[str, dict[int, str]] = defaultdict(dict)
    for row in rows:
        snapshot = row["snapshot"]
        index = int(row["memoryTypeIndex"])
        require(snapshot in {"BEFORE", "AFTER"} and 0 <= index < 129, "memory-types identity drift")
        require(index not in snapshots[snapshot], "duplicate runtime type index")
        snapshots[snapshot][index] = row["memoryTypeName"]
    require(set(snapshots) == {"BEFORE", "AFTER"}, "memory snapshot set differs")
    before = tuple(snapshots["BEFORE"][index] for index in range(129))
    after = tuple(snapshots["AFTER"][index] for index in range(129))
    require(before == after, "runtime memory-type names differ between snapshots")
    return before


def extract_memory_table(data: bytes, pe: Mapping[str, Any], runtime_names: Sequence[str]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    size = MEMORY_TABLE_RECORDS * MEMORY_TABLE_STRIDE
    offset = va_to_offset(pe, MEMORY_TABLE_VA, size + MEMORY_TABLE_STRIDE)
    raw = data[offset:offset + size]
    require(sha256_bytes(raw) == MEMORY_TABLE_SHA256, "physical memory-type table hash differs")
    physical: list[dict[str, object]] = []
    first: dict[int, tuple[int, str]] = {}
    for ordinal in range(MEMORY_TABLE_RECORDS):
        record = raw[ordinal * MEMORY_TABLE_STRIDE:(ordinal + 1) * MEMORY_TABLE_STRIDE]
        index = struct.unpack_from("<I", record, 0)[0]
        name_raw = record[4:36].split(b"\0", 1)[0]
        require(name_raw and all(0x20 <= value <= 0x7E for value in name_raw), f"physical type name is not strict ASCII at {ordinal}")
        name = name_raw.decode("ascii")
        maximum = struct.unpack_from("<I", record, 36)[0]
        require(maximum == 0xFFFFFFFF and index < 129, f"physical type record differs at {ordinal}")
        physical.append({
            "physicalOrdinal": ordinal,
            "recordVa": f"0x{MEMORY_TABLE_VA + ordinal * MEMORY_TABLE_STRIDE:08x}",
            "memoryTypeIndex": index,
            "memoryTypeName": name,
            "maxSize": "0xffffffff",
        })
        first.setdefault(index, (ordinal, name))
    sentinel = data[offset + size:offset + size + MEMORY_TABLE_STRIDE]
    require(struct.unpack_from("<I", sentinel, 0)[0] == 129 and sentinel[4:36].split(b"\0", 1)[0] == b"" and struct.unpack_from("<I", sentinel, 36)[0] == 0xFFFFFFFF, "memory-type sentinel differs")
    require(Counter(int(row["memoryTypeIndex"]) for row in physical)[41] == 2 and 42 not in first, "physical duplicate/missing lineage differs")
    logical = []
    for index, runtime_name in enumerate(runtime_names):
        if index in first:
            ordinal, name = first[index]
            require(runtime_name == name, f"runtime/first-physical type name differs at {index}")
            disposition = "FIRST_PHYSICAL_MATCH_RUNTIME_CORROBORATED"
            physical_ordinal: object = ordinal
        else:
            require(index == 42 and runtime_name == "Name not found", "unexpected runtime fallback type")
            disposition = "NO_PHYSICAL_ROW_RUNTIME_FALLBACK"
            physical_ordinal = ""
        logical.append({
            "memoryTypeIndex": index,
            "memoryTypeName": runtime_name,
            "physicalOrdinal": physical_ordinal,
            "mappingDisposition": disposition,
            "primaryPlateCount": 0,
            "unwindPlateCount": 0,
        })
    return physical, logical


def decode_exact(md: Cs, data: bytes, pe: Mapping[str, Any], start: int, end: int) -> list[Any]:
    require(start < end, "empty decode interval")
    offset = va_to_offset(pe, start, end - start)
    instructions = list(md.disasm(data[offset:offset + end - start], start))
    cursor = start
    for instruction in instructions:
        require(instruction.address == cursor and instruction.size > 0, f"decode gap at {cursor:#x}")
        cursor += instruction.size
    require(cursor == end, f"decode did not cover interval {start:#x}-{end:#x}")
    return instructions


def operand_value(md: Cs, instruction: Any) -> tuple[str, str, int | None]:
    require(instruction.mnemonic == "push" and len(instruction.operands) == 1, "operand owner is not one push")
    operand = instruction.operands[0]
    if operand.type == CS_OP_IMM:
        value = int(operand.imm) & 0xFFFFFFFF
        return "IMMEDIATE", f"0x{value:x}", value
    if operand.type == CS_OP_REG:
        name = md.reg_name(operand.reg)
        require(bool(name), "register operand has no name")
        return "REGISTER", name, None
    raise CensusError(f"unsupported push operand at {instruction.address:#x}: {instruction.op_str}")


def resolve_local_constant(md: Cs, instructions: Sequence[Any], register_name: str, use_address: int) -> tuple[int | None, str]:
    use = next(instruction for instruction in instructions if instruction.address == use_address)
    wanted = use.operands[0].reg
    wanted_name = md.reg_name(wanted)
    require(wanted_name == register_name, "register name/id drift")
    families = (
        {"eax", "ax", "al", "ah"}, {"ebx", "bx", "bl", "bh"},
        {"ecx", "cx", "cl", "ch"}, {"edx", "dx", "dl", "dh"},
        {"esi", "si"}, {"edi", "di"}, {"esp", "sp"}, {"ebp", "bp"},
    )
    family = next((names for names in families if wanted_name in names), {wanted_name})
    definition = None
    value = None
    for instruction in reversed([item for item in instructions if item.address < use_address]):
        _read, written = instruction.regs_access()
        written_names = {md.reg_name(register) for register in written}
        if family.isdisjoint(written_names):
            continue
        definition = instruction
        if instruction.mnemonic == "mov" and len(instruction.operands) == 2 and instruction.operands[0].type == CS_OP_REG and instruction.operands[0].reg == wanted and instruction.operands[1].type == CS_OP_IMM:
            value = int(instruction.operands[1].imm) & 0xFFFFFFFF
        elif instruction.mnemonic == "xor" and len(instruction.operands) == 2 and instruction.operands[0].type == CS_OP_REG and instruction.operands[1].type == CS_OP_REG and instruction.operands[0].reg == wanted == instruction.operands[1].reg:
            value = 0
        else:
            return None, (
                "DYNAMIC_REGISTER_NONCONSTANT_DEFINITION"
                if wanted_name in written_names
                else "DYNAMIC_REGISTER_ALIASED_WRITE"
            )
        break
    if definition is None or value is None:
        return None, "DYNAMIC_REGISTER"
    for instruction in instructions:
        if instruction.address >= use_address:
            continue
        if definition.address < instruction.address and instruction.mnemonic == "call":
            return None, "DYNAMIC_REGISTER_CALL_CLOBBER"
        if definition.address < instruction.address and (
            instruction.group(CS_GRP_RET)
            or instruction.group(CS_GRP_INT)
            or instruction.group(CS_GRP_IRET)
            or instruction.mnemonic in {"hlt", "ud2"}
        ):
            return None, "DYNAMIC_REGISTER_NONFALLTHROUGH"
        is_jump = instruction.group(CS_GRP_JUMP) or instruction.mnemonic.startswith("j")
        if not is_jump:
            continue
        if instruction.operands and instruction.operands[0].type == CS_OP_IMM:
            target = int(instruction.operands[0].imm) & 0xFFFFFFFF
            if definition.address < target <= use_address:
                return None, "DYNAMIC_REGISTER_BRANCH_ENTRY"
        else:
            return None, "DYNAMIC_REGISTER_INDIRECT_CONTROL_FLOW"
        if definition.address < instruction.address:
            return None, "DYNAMIC_REGISTER_CONTROL_FLOW"
    return value, "LOCAL_NO_ENTRY_LINEAR_IMMEDIATE"


def derive_sites(data: bytes, pe: Mapping[str, Any], source_rows: Sequence[Mapping[str, str]], runtime_names: Sequence[str]) -> list[dict[str, object]]:
    md = Cs(CS_ARCH_X86, CS_MODE_32)
    md.detail = True
    output = []
    for row in source_rows:
        site = int(row["siteVa"], 16)
        call = int(row["firstDirectCallVa"], 16)
        target = int(row["firstDirectCallTargetVa"], 16)
        plate_start = int(row["plateStartVa"], 16)
        end = int(row["plateEndExclusiveVa"], 16)
        require(end == call + 5 and target in PRIMARY_TARGETS | {FREE_TARGET}, "source call identity drift")
        require(
            int(row["fileOffset"], 16) == va_to_offset(pe, site),
            f"source file offset differs at {site:#x}",
        )
        plate_offset = va_to_offset(pe, plate_start, end - plate_start)
        require(
            sha256_bytes(data[plate_offset:plate_offset + end - plate_start])
            == row["plateBytesSha256"],
            f"source plate hash differs at {site:#x}",
        )
        instructions = decode_exact(md, data, pe, site, end)
        require(instructions[0].mnemonic == "push" and bytes(instructions[0].bytes).hex() == row["pathPushBytes"], "path push differs")
        require(instructions[-1].address == call and instructions[-1].mnemonic == "call" and instructions[-1].operands[0].type == CS_OP_IMM and (int(instructions[-1].operands[0].imm) & 0xFFFFFFFF) == target, "plate call differs")
        pushes = [instruction for instruction in instructions[1:-1] if instruction.mnemonic == "push"]
        require(len(pushes) == 2 and not any(instruction.mnemonic in {"call", "ret", "retf", "jmp"} for instruction in instructions[1:-1]), "plate does not have exactly two straight-line argument pushes")
        type_kind, type_operand, type_value = operand_value(md, pushes[0])
        if type_value is not None:
            require(type_value < len(runtime_names), f"type immediate out of range at {site:#x}")
            type_resolution = "IMMEDIATE"
        else:
            interval_start = int(row["pathOwnerIntervalStartVa"], 16)
            require(row["pathOwnerKind"] == "FUNCTION" and interval_start < site, "register type is not function-owned")
            owner_instructions = decode_exact(
                md, data, pe, interval_start, pushes[0].address + pushes[0].size
            )
            type_value, type_resolution = resolve_local_constant(md, owner_instructions, type_operand, pushes[0].address)
            if type_value is not None:
                require(type_value < len(runtime_names), f"resolved type out of range at {site:#x}")
        type_name = runtime_names[type_value] if type_value is not None else ""
        second_kind, second_operand, second_value = operand_value(md, pushes[1])
        primary = target in PRIMARY_TARGETS
        output.append({
            "siteKey": row["siteKey"], "siteVa": row["siteVa"],
            "canonicalRelativePath": row["canonicalRelativePath"], "lineValue": row["lineValue"],
            "plateClass": row["plateClass"], "callTargetVa": row["firstDirectCallTargetVa"],
            "pathOwnerKind": row["pathOwnerKind"], "pathOwnerEntityKey": row["pathOwnerEntityKey"],
            "pathFunctionEntryVa": row["pathFunctionEntryVa"], "pathFunctionName": row["pathFunctionName"],
            "callOwnerKind": row["callOwnerKind"], "callOwnerEntityKey": row["callOwnerEntityKey"],
            "ownerBoundaryCrossing": row["ownerBoundaryCrossing"], "typeOperandKind": type_kind,
            "typeOperand": type_operand, "typeValue": "" if type_value is None else type_value,
            "typeResolution": type_resolution, "logicalTypeName": type_name,
            "sizeOperandKind": second_kind if primary else "", "sizeOperand": second_operand if primary else "",
            "sizeValue": ("" if second_value is None else second_value) if primary else "",
            "pointerOperandKind": second_kind if not primary else "", "pointerOperand": second_operand if not primary else "",
            "plateBytesSha256": row["plateBytesSha256"],
        })
    return output


def aggregate(site_rows: Sequence[Mapping[str, object]], logical_rows: list[dict[str, object]]) -> tuple[list[dict[str, object]], dict[str, object]]:
    type_primary = Counter()
    type_unwind = Counter()
    owners: dict[tuple[str, str], list[Mapping[str, object]]] = defaultdict(list)
    for row in site_rows:
        owners[(str(row["pathOwnerKind"]), str(row["pathOwnerEntityKey"]))].append(row)
        if row["typeValue"] != "":
            target = type_primary if row["plateClass"] == "PRIMARY_ALLOC_SOURCE_PLATE" else type_unwind
            target[int(row["typeValue"])] += 1
    for row in logical_rows:
        index = int(row["memoryTypeIndex"])
        row["primaryPlateCount"] = type_primary[index]
        row["unwindPlateCount"] = type_unwind[index]

    owner_rows = []
    for (kind, entity), rows in sorted(owners.items(), key=lambda item: (item[0][0], item[0][1])):
        resolved = sorted({int(row["typeValue"]) for row in rows if row["typeValue"] != ""})
        owner_rows.append({
            "ownerKind": kind, "ownerEntityKey": entity,
            "functionEntryVa": rows[0]["pathFunctionEntryVa"], "functionName": rows[0]["pathFunctionName"],
            "primaryPlateCount": sum(row["plateClass"] == "PRIMARY_ALLOC_SOURCE_PLATE" for row in rows),
            "unwindPlateCount": sum(row["plateClass"] == "UNWIND_FREE_SOURCE_PLATE" for row in rows),
            "immediateTypeCount": sum(row["typeResolution"] == "IMMEDIATE" for row in rows),
            "localConstantTypeCount": sum(str(row["typeResolution"]).startswith("LOCAL_") for row in rows),
            "dynamicTypeCount": sum(str(row["typeResolution"]).startswith("DYNAMIC_") for row in rows),
            "distinctResolvedTypeIndices": ",".join(str(value) for value in resolved),
            "immediateSizeCount": sum(row["plateClass"] == "PRIMARY_ALLOC_SOURCE_PLATE" and row["sizeOperandKind"] == "IMMEDIATE" for row in rows),
            "registerSizeCount": sum(row["plateClass"] == "PRIMARY_ALLOC_SOURCE_PLATE" and row["sizeOperandKind"] == "REGISTER" for row in rows),
            "ownerBoundaryCrossingCount": sum(row["ownerBoundaryCrossing"] == "True" for row in rows),
        })

    counts = {
        "sites": len(site_rows),
        "primary": sum(row["plateClass"] == "PRIMARY_ALLOC_SOURCE_PLATE" for row in site_rows),
        "unwind": sum(row["plateClass"] == "UNWIND_FREE_SOURCE_PLATE" for row in site_rows),
        "immediateTypes": sum(row["typeResolution"] == "IMMEDIATE" for row in site_rows),
        "localConstantTypes": sum(str(row["typeResolution"]).startswith("LOCAL_") for row in site_rows),
        "dynamicTypes": sum(str(row["typeResolution"]).startswith("DYNAMIC_") for row in site_rows),
        "runtimeLabeledTypes": sum(row["logicalTypeName"] != "" for row in site_rows),
        "semanticNamedTypes": sum(row["logicalTypeName"] not in {"", "Name not found"} for row in site_rows),
        "fallbackTypeSites": sum(row["logicalTypeName"] == "Name not found" for row in site_rows),
        "primaryImmediateTypes": sum(row["plateClass"] == "PRIMARY_ALLOC_SOURCE_PLATE" and row["typeOperandKind"] == "IMMEDIATE" for row in site_rows),
        "primaryRegisterTypes": sum(row["plateClass"] == "PRIMARY_ALLOC_SOURCE_PLATE" and row["typeOperandKind"] == "REGISTER" for row in site_rows),
        "primaryImmediateSizes": sum(row["plateClass"] == "PRIMARY_ALLOC_SOURCE_PLATE" and row["sizeOperandKind"] == "IMMEDIATE" for row in site_rows),
        "primaryRegisterSizes": sum(row["plateClass"] == "PRIMARY_ALLOC_SOURCE_PLATE" and row["sizeOperandKind"] == "REGISTER" for row in site_rows),
        "unwindImmediateTypes": sum(row["plateClass"] == "UNWIND_FREE_SOURCE_PLATE" and row["typeOperandKind"] == "IMMEDIATE" for row in site_rows),
        "type41Sites": sum(row["typeValue"] == 41 for row in site_rows),
        "type42Sites": sum(row["typeValue"] == 42 for row in site_rows),
        "functionOwnedSites": sum(row["pathOwnerKind"] == "FUNCTION" for row in site_rows),
        "residualOwnedSites": sum(row["pathOwnerKind"] == "RESIDUAL" for row in site_rows),
        "ownerBoundaryCrossings": sum(row["ownerBoundaryCrossing"] == "True" for row in site_rows),
    }
    require(counts == EXPECTED_COUNTS, f"source allocation counts drift: {counts}")
    return owner_rows, counts


def derive(specimen: Path, source_sites: Path, memory_types: Path) -> dict[str, object]:
    require(specimen.is_file() and not specimen.is_symlink(), "specimen is not one plain file")
    require(specimen.stat().st_size == SPECIMEN_BYTES and sha256_file(specimen) == SPECIMEN_SHA256, "specimen identity differs")
    data = specimen.read_bytes()
    pe = parse_pe(data)
    runtime_names = parse_runtime_type_names(memory_types)
    physical, logical = extract_memory_table(data, pe, runtime_names)
    ctor_offset = va_to_offset(pe, MEMORY_CTOR_START, MEMORY_CTOR_END - MEMORY_CTOR_START)
    require(sha256_bytes(data[ctor_offset:ctor_offset + MEMORY_CTOR_END - MEMORY_CTOR_START]) == MEMORY_CTOR_SHA256, "memory constructor hash differs")
    source_rows = read_tsv(source_sites, SOURCE_COLUMNS, "source-sites")
    site_rows = derive_sites(data, pe, source_rows, runtime_names)
    owner_rows, counts = aggregate(site_rows, logical)
    summary = {
        "schema": SCHEMA,
        "specimenSha256": SPECIMEN_SHA256,
        "counts": counts,
        "memoryTypeTable": {
            "baseVa": f"0x{MEMORY_TABLE_VA:08x}", "records": MEMORY_TABLE_RECORDS,
            "stride": MEMORY_TABLE_STRIDE, "bytes": MEMORY_TABLE_RECORDS * MEMORY_TABLE_STRIDE,
            "sha256": MEMORY_TABLE_SHA256, "duplicatePhysicalIndex": 41,
            "missingPhysicalIndex": 42, "logical42Name": runtime_names[42],
        },
        "memoryManagerConstructor": {
            "startVa": f"0x{MEMORY_CTOR_START:08x}", "endExclusiveVa": f"0x{MEMORY_CTOR_END:08x}",
            "bytes": MEMORY_CTOR_END - MEMORY_CTOR_START, "sha256": MEMORY_CTOR_SHA256,
        },
        "dynamicTypeSites": [row["siteVa"] for row in site_rows if str(row["typeResolution"]).startswith("DYNAMIC_")],
        "localConstantTypeSites": [row["siteVa"] for row in site_rows if str(row["typeResolution"]).startswith("LOCAL_")],
        "boundaryCrossings": [row["siteVa"] for row in site_rows if row["ownerBoundaryCrossing"] == "True"],
        "claimBoundary": list(CLAIM_BOUNDARY),
    }
    return {"physical": physical, "logical": logical, "sites": site_rows, "owners": owner_rows, "summary": summary}


def output_bytes(owner_path: Path, result: Mapping[str, object]) -> dict[str, bytes]:
    return {
        "source-allocation-owner.py": owner_path.read_bytes(),
        "memory-type-physical.tsv": render_tsv(PHYSICAL_COLUMNS, result["physical"]),
        "memory-type-logical.tsv": render_tsv(LOGICAL_COLUMNS, result["logical"]),
        "source-allocation-sites.tsv": render_tsv(SITE_COLUMNS, result["sites"]),
        "owner-allocation-evidence.tsv": render_tsv(OWNER_COLUMNS, result["owners"]),
        "allocation-census-summary.json": canonical_json(result["summary"]),
    }


def build(specimen: Path, source_bundle: Path, memory_bundle: Path, out: Path) -> dict[str, object]:
    require(not out.exists() and out.parent.is_dir(), "output must be a new child of an existing directory")
    source_ready = source_bundle / "source-unit-census.ready.json"
    source_sites = source_bundle / "source-sites.tsv"
    memory_ready = memory_bundle / "READY.json"
    memory_types = memory_bundle / "memory-types.tsv"
    validate_upstream(source_ready, source_sites, memory_ready, memory_types)
    result = derive(specimen, source_sites, memory_types)
    temporary = Path(tempfile.mkdtemp(prefix=f".{out.name}-", dir=out.parent))
    try:
        inputs = temporary / "inputs"
        inputs.mkdir()
        for source, name in (
            (source_ready, INPUT_NAMES[0]), (source_sites, INPUT_NAMES[1]),
            (memory_ready, INPUT_NAMES[2]), (memory_types, INPUT_NAMES[3]),
        ):
            shutil.copyfile(source, inputs / name)
        files = output_bytes(Path(__file__), result)
        for name, content in files.items():
            (temporary / name).write_bytes(content)
        ready = {
            "schema": SCHEMA, "status": STATUS,
            "specimen": stamp(specimen),
            "inputs": {name: stamp(inputs / name, temporary) for name in INPUT_NAMES},
            "outputs": {name: stamp(temporary / name, temporary) for name in OUTPUT_NAMES},
            "counts": result["summary"]["counts"],
            "evidence": {
                "memoryTypeTable": result["summary"]["memoryTypeTable"],
                "memoryManagerConstructor": result["summary"]["memoryManagerConstructor"],
            },
            "claimBoundary": list(CLAIM_BOUNDARY),
        }
        (temporary / "READY.json").write_bytes(canonical_json(ready))
        verify(temporary, specimen)
        os.rename(temporary, out)
        return ready
    except BaseException:
        shutil.rmtree(temporary, ignore_errors=True)
        raise


def verify(bundle: Path, specimen: Path) -> dict[str, object]:
    validate_bundle_tree(bundle)
    bundled_owner = bundle / "source-allocation-owner.py"
    executing_owner = Path(__file__).resolve()
    require(
        bundled_owner.read_bytes() == executing_owner.read_bytes(),
        "bundled owner differs from executing owner",
    )
    ready = read_json(bundle / "READY.json", "READY")
    require((bundle / "READY.json").read_bytes() == canonical_json(ready), "READY is not canonical JSON")
    require(set(ready) == {"schema", "status", "specimen", "inputs", "outputs", "counts", "evidence", "claimBoundary"}, "READY shape differs")
    require(ready["schema"] == SCHEMA and ready["status"] == STATUS and ready["claimBoundary"] == list(CLAIM_BOUNDARY), "READY identity differs")
    inputs = bundle / "inputs"
    validate_upstream(inputs / INPUT_NAMES[0], inputs / INPUT_NAMES[1], inputs / INPUT_NAMES[2], inputs / INPUT_NAMES[3])
    require(ready["specimen"] == stamp(specimen), "READY specimen stamp differs")
    require(ready["inputs"] == {name: stamp(inputs / name, bundle) for name in INPUT_NAMES}, "READY input stamps differ")
    result = derive(specimen, inputs / INPUT_NAMES[1], inputs / INPUT_NAMES[3])
    expected = output_bytes(bundle / "source-allocation-owner.py", result)
    for name, content in expected.items():
        require((bundle / name).read_bytes() == content, f"derived output differs: {name}")
    require(ready["outputs"] == {name: stamp(bundle / name, bundle) for name in OUTPUT_NAMES}, "READY output stamps differ")
    require(ready["counts"] == result["summary"]["counts"], "READY counts differ")
    require(ready["evidence"] == {
        "memoryTypeTable": result["summary"]["memoryTypeTable"],
        "memoryManagerConstructor": result["summary"]["memoryManagerConstructor"],
    }, "READY evidence differs")
    return {"schema": SCHEMA, "status": STATUS, "bundle": str(bundle.resolve()), "readySha256": sha256_file(bundle / "READY.json"), "counts": ready["counts"]}


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    subparsers = result.add_subparsers(dest="command", required=True)
    build_parser = subparsers.add_parser("build")
    build_parser.add_argument("--specimen", required=True, type=Path)
    build_parser.add_argument("--source-bundle", required=True, type=Path)
    build_parser.add_argument("--memory-bundle", required=True, type=Path)
    build_parser.add_argument("--out", required=True, type=Path)
    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument("--bundle", required=True, type=Path)
    verify_parser.add_argument("--specimen", required=True, type=Path)
    return result


def main(argv: Sequence[str] | None = None) -> int:
    arguments = parser().parse_args(argv)
    try:
        if arguments.command == "build":
            value = build(arguments.specimen.resolve(), arguments.source_bundle.resolve(), arguments.memory_bundle.resolve(), arguments.out.resolve())
            print(json.dumps({"schema": SCHEMA, "status": STATUS, "out": str(arguments.out.resolve()), "counts": value["counts"]}, sort_keys=True))
        else:
            print(json.dumps(verify(arguments.bundle.absolute(), arguments.specimen.resolve()), sort_keys=True))
    except (CensusError, OSError, UnicodeError, ValueError) as exc:
        print(f"UNSCORED: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
