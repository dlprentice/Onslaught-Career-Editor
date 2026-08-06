#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Freeze the retail CConsole file/ring/overlay and shared-RET topology."""

from __future__ import annotations

import argparse
from collections import Counter
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
from typing import Iterable, Mapping, Sequence

import capstone
from capstone import Cs, CS_ARCH_X86, CS_MODE_32
from capstone.x86 import X86_INS_CALL, X86_INS_JMP, X86_OP_IMM


SCHEMA = "bea.re.console-output-topology.v2"
STATUS = "READY"
SPECIMEN_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
SPECIMEN_MD5 = "3b456964020070efe696d2cc09464a55"
SPECIMEN_BYTES = 2_506_752
IMAGE_BASE = 0x00400000
TEXT_VA = 0x00401000
TEXT_VIRTUAL_BYTES = 0x001D6F9D
CAPSTONE_VERSION = "5.0.7"

PARITY_READY_SHA256 = "4e4dd5cb1262cbb4f3e616aa02619beee1aa7373629737f58a7cb1f577dab310"
PARITY_BODY_RANGES_SHA256 = "ece12c7ce659aa23f8e8fa36b694ef7b2425212ff4ffd4b233535c4a51d00ad5"
PARITY_DIRECT_CALLS_SHA256 = "fd3f744762d11ba40acc194fd69d8c55e855ddd07a80b7cf008c4df841143d00"
RTTI_READY_SHA256 = "772630978cdbb2a6b4a95613f425136002381f348917041a9289dff818dbe4d2"
RTTI_VTABLES_SHA256 = "2f1602d4c7ffffa9c2b5116c60a23d23b2f8bf923495feded54ebb67aff1f178"

PARITY_SOURCE_NAMES = {
    "inputs/ghidra-parity.ready.json": "after-parity-graph.ready.json",
    "inputs/ghidra-body-ranges.tsv": "after-body-ranges.tsv",
    "inputs/ghidra-direct-calls.tsv": "after-direct-calls.tsv",
}
RTTI_SOURCE_NAMES = {
    "inputs/rtti.ready.json": "READY.json",
    "inputs/rtti-vtables.tsv": "vtables.tsv",
}
INPUT_NAMES = tuple((*PARITY_SOURCE_NAMES, *RTTI_SOURCE_NAMES))
INPUT_HASHES = {
    "inputs/ghidra-parity.ready.json": PARITY_READY_SHA256,
    "inputs/ghidra-body-ranges.tsv": PARITY_BODY_RANGES_SHA256,
    "inputs/ghidra-direct-calls.tsv": PARITY_DIRECT_CALLS_SHA256,
    "inputs/rtti.ready.json": RTTI_READY_SHA256,
    "inputs/rtti-vtables.tsv": RTTI_VTABLES_SHA256,
}

PRINTF = 0x00441740
PRINTF_NO_NEWLINE = 0x004418A0
OVERLAY = 0x004419E0
SHARED_RET_STUB = 0x0040C640
DORMANT_RECEIVER = 0x0066F580
SETUP_RECEIVER = 0x0066EB90

BODY_SPECS = (
    ("dormantInitializer", 0x004415B0, 0x0044161A, "b8d3733698fdf2dc4629f49f76065a750b45dde855f566cdfd1a7a5e81002ab9"),
    ("setupInitializer", 0x00441630, 0x0044169A, "40bfb4406d6f093bfbfe78458e5f169b891d7e0b52f0409ca106b97cbb2e9a8a"),
    ("historyReset", 0x004416E0, 0x0044172C, "8db54021cf9db6b1c1f5d2faaca0cfa222ef536fa4448707b1e43a12435b2263"),
    ("printf", 0x00441740, 0x0044189D, "cb622f67e3677725ac8165dbb2d43414d938eb31aaad4d4177e8618a373b9ef9"),
    ("printfNoNewline", 0x004418A0, 0x004419D8, "141cf301bf36745f46d178f9f4bd3e8b34f41ee2257cb05a0a42befdb7f20bce"),
    ("renderStatusHistoryOverlay", 0x004419E0, 0x00441B02, "4a6f91edfd44dcc1ae80029f6cdf0a43d193d3fa81881801903549d488e8145e"),
    ("sharedRetStubBody", 0x0040C640, 0x0040C641, "ae3f4619b0413d70d3004b9131c3752153074e45725be13b9a148978895e359e"),
)
SHARED_RET_ALIGNMENT_SPAN = (
    0x0040C640,
    0x0040C650,
    "499f1f307c1cb989f968a6b7fcaec591e1828877223d0b0e7e8e8b76cde8c9ca",
)

RESIDUAL_PRINTF_SITES = {0x004F22FA, 0x005351F0, 0x00536BA9}
RESIDUAL_STUB_JMPS = {
    0x004EF9E5: (0x004EF9E0, 0x004EF9EA, "c03512488968d4597ca4833b1f2effeaed6a7aca6a09682fd4be788bff2321c6"),
    0x005446F9: (0x005446E0, 0x005446FF, "83ff4e89f3102ff7c24a871af4e4cdf267eacea239aa0c773ba01214e515eba4"),
}

EXACT_BYTES = {
    0x004415BA: "c60588f5660000",
    0x004415C1: "c7056cff660000000000",
    0x004415D5: "b989f56600",
    0x0044163A: "c60598eb660000",
    0x00441641: "c7057cf5660001000000",
    0x00441655: "b999eb6600",
    0x004416E1: "8d816c090000",
    0x004416E7: "8d5109",
    0x004416EA: "be1e000000",
    0x004416F8: "83c004",
    0x004416FB: "83c250",
    0x00441701: "c781e409000000000000",
    0x0044170B: "c781e80900000000c8c2",
    0x00441725: "8981ec090000",
    0x00441767: "e8d4aefcff",
    0x00441774: "e8c7aefcff",
    0x0044178B: "0f8403010000",
    0x004417FE: "0f8490000000",
    0x00441823: "8b8ee4090000",
    0x00441835: "83f81d",
    0x00441881: "898ee8090000",
    0x004418B7: "0f8412010000",
    0x0044192B: "0f849e000000",
    0x0044195F: "8b8ee4090000",
    0x00441971: "83f81d",
    0x004419E6: "d825c08b5d00",
    0x004419F2: "d89be8090000",
    0x00441AEE: "83ff06",
    0x0047181D: "b980f56600",
    0x0047182C: "e8af01fdff",
    0x00539B17: "6880f56600",
    0x00539B1C: "e87f7df0ff",
}

HELPER_EDGES = (
    ("printfFormat", 0x0044175A, 0x0055E38C),
    ("printfOpenCreate", 0x004417A1, 0x0055E490),
    ("printfOpenFallback", 0x004417D9, 0x0055E490),
    ("printfOpenAppend", 0x004417F2, 0x0055E490),
    ("printfWriteText", 0x0044180A, 0x0055E520),
    ("printfWriteNewline", 0x00441818, 0x0055E520),
    ("printfClose", 0x0044181E, 0x0055E4A3),
    ("printfRingCopy", 0x0044185C, 0x004D6240),
    ("noNewlineOpenCreate", 0x004418CD, 0x0055E490),
    ("noNewlineOpenFallback", 0x00441906, 0x0055E490),
    ("noNewlineOpenAppend", 0x0044191F, 0x0055E490),
    ("noNewlineFormat", 0x00441946, 0x0055E38C),
    ("noNewlineWrite", 0x00441954, 0x0055E520),
    ("noNewlineClose", 0x0044195A, 0x0055E4A3),
    ("noNewlineRingCopy", 0x00441998, 0x004D6240),
    ("overlayAsciiToWide", 0x00441AB8, 0x004F7BF0),
    ("overlayFont", 0x00441AD7, 0x00515A70),
    ("overlayDrawText", 0x00441ADE, 0x00540640),
)

CALL_COLUMNS = (
    "targetKind", "siteKind", "siteVa", "mappingState",
    "ownerAddress", "ownerName", "receiverVa", "receiverChannel",
)
DATA_COLUMNS = (
    "targetKind", "referenceKind", "referenceVa", "className", "vtableVa", "slot",
)
OUTPUT_NAMES = (
    "console-output-topology-owner.py",
    "direct-transfer-sites.tsv",
    "folded-stub-vtable-slots.tsv",
    "console-output-topology.json",
)
CLAIM_BOUNDARY = (
    "This is a pristine-byte and pinned-Ghidra/RTTI static topology: it proves decoded direct transfers, exact bodies and spans, mapped-versus-residual ownership, branch destinations, object offsets, and exact vtable slots, not runtime visibility or successful disk output.",
    "File-open success is a shared precondition for the static write, close, and 30-slot ring-update path; the write helper's return is not checked, so this owner does not prove a successful write.",
    "The six newest history slots remain statically eligible for the draw loop until the unresolved float timebase exceeds the single last-line value by 16.0; this is one global comparison, not per-entry expiration, and no visual capture is claimed.",
    "The 380-call denominator names the pinned graph target CConsole__Printf only; CConsole__PrintfNoNewline has one additional dormant-instance direct caller.",
    "Address 0x0040c640 is a one-byte shared RET target, not an established DebugTrace implementation: 291 rel32 CALLs, 10 rel32 tail JMPs, and 22 RTTI vtable slots reconcile the historical 323-reference fanout and prove mixed call shapes. Only 0x00441767 and 0x00441774 are the exact Printf-to-stub subset.",
    "A global patch of the shared RET target is rejected: it would affect mixed direct and indirect call shapes and forwarding it to Printf would recurse through Printf's two exact stub calls.",
    "This owner changes neither the specimen nor Ghidra and authorizes no function name, signature, runtime patch, visual-parity claim, or rebuild promotion by itself.",
)


class TopologyError(ValueError):
    """A specimen, derivation, or READY boundary failed closed."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise TopologyError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def render_tsv(columns: Sequence[str], rows: Iterable[Mapping[str, object]]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=list(columns), delimiter="\t", lineterminator="\n", extrasaction="raise")
    writer.writeheader()
    for row in rows:
        require(set(row) == set(columns), "TSV columns differ")
        rendered = {column: str(row[column]) for column in columns}
        require(not any(any(char in value for char in "\t\r\n") for value in rendered.values()), "TSV cell has framing characters")
        writer.writerow(rendered)
    return output.getvalue().encode("utf-8")


def parse_tsv(data: bytes, label: str) -> list[dict[str, str]]:
    try:
        lines = [line for line in data.decode("utf-8").splitlines() if line and not line.startswith("#")]
    except UnicodeError as exc:
        raise TopologyError(f"{label} is not UTF-8: {exc}") from exc
    require(lines, f"{label} has no TSV rows")
    reader = csv.DictReader(lines, delimiter="\t")
    require(reader.fieldnames is not None and len(reader.fieldnames) == len(set(reader.fieldnames)), f"{label} header differs")
    rows = list(reader)
    require(all(None not in row for row in rows), f"{label} has malformed rows")
    return rows


def is_linklike(path: Path) -> bool:
    if path.is_symlink():
        return True
    junction = getattr(path, "is_junction", None)
    if junction is not None and junction():
        return True
    attributes = getattr(path.lstat(), "st_file_attributes", 0)
    return bool(attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))


def parse_pe(data: bytes) -> dict[str, object]:
    require(len(data) >= 0x100 and data[:2] == b"MZ", "specimen is not MZ")
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    require(data[pe:pe + 4] == b"PE\0\0", "PE signature differs")
    count = struct.unpack_from("<H", data, pe + 6)[0]
    optional_size = struct.unpack_from("<H", data, pe + 20)[0]
    optional = pe + 24
    require(struct.unpack_from("<H", data, optional)[0] == 0x10B, "specimen is not PE32")
    image_base = struct.unpack_from("<I", data, optional + 28)[0]
    sections = []
    table = optional + optional_size
    for index in range(count):
        offset = table + index * 40
        name = data[offset:offset + 8].split(b"\0", 1)[0].decode("ascii")
        virtual_size, rva, raw_size, raw_offset = struct.unpack_from("<IIII", data, offset + 8)
        sections.append({"name": name, "va": image_base + rva, "virtualBytes": virtual_size, "rawBytes": raw_size, "rawOffset": raw_offset})
    return {"imageBase": image_base, "sections": sections}


def section(pe: Mapping[str, object], name: str) -> Mapping[str, object]:
    rows = [row for row in pe["sections"] if row["name"] == name]
    require(len(rows) == 1, f"section {name} is not unique")
    return rows[0]


def va_to_offset(pe: Mapping[str, object], address: int, size: int = 1) -> int:
    for row in pe["sections"]:
        start = int(row["va"])
        span = max(int(row["virtualBytes"]), int(row["rawBytes"]))
        if start <= address and address + size <= start + span:
            relative = address - start
            require(relative + size <= int(row["rawBytes"]), f"VA is not file-backed: {address:#x}+{size}")
            return int(row["rawOffset"]) + relative
    raise TopologyError(f"VA is unmapped: {address:#x}+{size}")


def va_bytes(data: bytes, pe: Mapping[str, object], address: int, size: int) -> bytes:
    offset = va_to_offset(pe, address, size)
    return data[offset:offset + size]


def rel32_sites(text: bytes, text_va: int, target: int, opcode: int) -> list[int]:
    sites = []
    for index in range(len(text) - 4):
        if text[index] != opcode:
            continue
        displacement = struct.unpack_from("<i", text, index + 1)[0]
        if (text_va + index + 5 + displacement) & 0xFFFFFFFF == target:
            sites.append(text_va + index)
    return sites


def read_ascii(data: bytes, pe: Mapping[str, object], address: int) -> str:
    offset = va_to_offset(pe, address)
    end = data.find(b"\0", offset, offset + 512)
    require(end >= 0, f"unterminated ASCII string at {address:#x}")
    raw = data[offset:end]
    require(raw and all(0x20 <= value <= 0x7E for value in raw), f"non-ASCII path at {address:#x}")
    return raw.decode("ascii")


def decode_exact_transfer(data: bytes, pe: Mapping[str, object], site: int, instruction_id: int, target: int) -> None:
    md = Cs(CS_ARCH_X86, CS_MODE_32)
    md.detail = True
    instructions = list(md.disasm(va_bytes(data, pe, site, 15), site, count=1))
    require(len(instructions) == 1, f"transfer does not decode at {site:#x}")
    instruction = instructions[0]
    require(instruction.address == site and instruction.size == 5 and instruction.id == instruction_id, f"transfer shape differs at {site:#x}")
    require(len(instruction.operands) == 1 and instruction.operands[0].type == X86_OP_IMM, f"transfer is not direct at {site:#x}")
    require((instruction.operands[0].imm & 0xFFFFFFFF) == target, f"transfer target differs at {site:#x}")


def receiver_before(data: bytes, pe: Mapping[str, object], call_site: int, target: int) -> int:
    md = Cs(CS_ARCH_X86, CS_MODE_32)
    md.detail = True
    for distance in range(5, 33):
        push = call_site - distance
        raw = va_bytes(data, pe, push, distance + 5)
        if raw[0] != 0x68:
            continue
        receiver = struct.unpack_from("<I", raw, 1)[0]
        if receiver not in {DORMANT_RECEIVER, SETUP_RECEIVER}:
            continue
        instructions = list(md.disasm(raw, push))
        cursor = push
        for instruction in instructions:
            if instruction.address != cursor:
                break
            cursor += instruction.size
        if cursor != call_site + 5 or not instructions or instructions[-1].address != call_site:
            continue
        instruction = instructions[-1]
        if instruction.id != X86_INS_CALL or instruction.size != 5 or instruction.operands[0].type != X86_OP_IMM:
            continue
        if (instruction.operands[0].imm & 0xFFFFFFFF) == target:
            return receiver
    raise TopologyError(f"no exact receiver push before formatter call {call_site:#x}")


def parse_hex(value: str, label: str) -> int:
    try:
        return int(value, 16)
    except ValueError as exc:
        raise TopologyError(f"invalid {label}: {value!r}") from exc


def owner_for_site(site: int, body_rows: Sequence[Mapping[str, str]]) -> Mapping[str, str] | None:
    matches = [
        row for row in body_rows
        if parse_hex(row["rangeMin"], "rangeMin") <= site
        and site + 5 <= parse_hex(row["rangeEndExclusive"], "rangeEndExclusive")
    ]
    require(len(matches) <= 1, f"site belongs to overlapping Ghidra ranges: {site:#x}")
    return matches[0] if matches else None


def decoded_range_transfers(data: bytes, pe: Mapping[str, object], row: Mapping[str, str]) -> dict[int, tuple[int, int, int]]:
    start = parse_hex(row["rangeMin"], "rangeMin")
    end = parse_hex(row["rangeEndExclusive"], "rangeEndExclusive")
    md = Cs(CS_ARCH_X86, CS_MODE_32)
    md.detail = True
    result = {}
    for instruction in md.disasm(va_bytes(data, pe, start, end - start), start):
        if instruction.id not in {X86_INS_CALL, X86_INS_JMP} or not instruction.operands or instruction.operands[0].type != X86_OP_IMM:
            continue
        result[instruction.address] = (instruction.id, instruction.size, instruction.operands[0].imm & 0xFFFFFFFF)
    return result


def validate_mapped_transfer(
    data: bytes,
    pe: Mapping[str, object],
    site: int,
    instruction_id: int,
    target: int,
    owner: Mapping[str, str],
    cache: dict[tuple[str, str, str], dict[int, tuple[int, int, int]]],
) -> None:
    key = (owner["functionAddress"], owner["rangeMin"], owner["rangeEndExclusive"])
    transfers = cache.setdefault(key, decoded_range_transfers(data, pe, owner))
    require(transfers.get(site) == (instruction_id, 5, target), f"raw candidate is not a sequentially decoded transfer at {site:#x}")


def validate_frozen_inputs(inputs: Mapping[str, bytes]) -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    require(set(inputs) == set(INPUT_NAMES), "frozen input names differ")
    for name, expected_hash in INPUT_HASHES.items():
        require(sha256_bytes(inputs[name]) == expected_hash, f"frozen input hash differs: {name}")
    try:
        parity_ready = json.loads(inputs["inputs/ghidra-parity.ready.json"].decode("utf-8"))
        rtti_ready = json.loads(inputs["inputs/rtti.ready.json"].decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise TopologyError(f"frozen READY input is invalid: {exc}") from exc
    require(parity_ready["program"]["executableMd5"] == SPECIMEN_MD5, "parity specimen MD5 differs")
    require(parity_ready["bodyRanges"]["sha256"] == PARITY_BODY_RANGES_SHA256, "parity body pin differs")
    require(parity_ready["directCalls"]["sha256"] == PARITY_DIRECT_CALLS_SHA256, "parity graph pin differs")
    require(rtti_ready["specimen"]["sha256"] == SPECIMEN_SHA256, "RTTI specimen pin differs")
    require(rtti_ready["artifacts"]["vtables.tsv"]["sha256"] == RTTI_VTABLES_SHA256, "RTTI vtable pin differs")
    body_rows = parse_tsv(inputs["inputs/ghidra-body-ranges.tsv"], "Ghidra body ranges")
    graph_rows = parse_tsv(inputs["inputs/ghidra-direct-calls.tsv"], "Ghidra direct graph")
    vtable_rows = parse_tsv(inputs["inputs/rtti-vtables.tsv"], "RTTI vtables")
    require(len(body_rows) == 7712, "Ghidra body-range count differs")
    require(len(graph_rows) == 14191, "Ghidra direct-edge count differs")
    require(len(vtable_rows) == 11777, "RTTI vtable-slot count differs")
    return body_rows, graph_rows, vtable_rows


def graph_counter(graph_rows: Sequence[Mapping[str, str]], target: int) -> Counter[tuple[str, str]]:
    selected = [row for row in graph_rows if parse_hex(row["calleeAddress"], "calleeAddress") == target]
    require(all(row["edgeKind"] == "STATIC_DIRECT" for row in selected), f"non-static graph edge reaches {target:#x}")
    return Counter({(row["callerAddress"], row["callerName"]): int(row["callSiteCount"]) for row in selected})


def mapped_row_counter(rows: Sequence[Mapping[str, object]], target_kind: str) -> Counter[tuple[str, str]]:
    result: Counter[tuple[str, str]] = Counter()
    for row in rows:
        if row["targetKind"] == target_kind and row["mappingState"] == "GHIDRA_FUNCTION_RANGE":
            result[(str(row["ownerAddress"]), str(row["ownerName"]))] += 1
    return result


def derive_bytes(data: bytes, inputs: Mapping[str, bytes]) -> tuple[bytes, bytes, bytes, dict[str, object]]:
    require(capstone.__version__ == CAPSTONE_VERSION, "Capstone version differs")
    body_rows, graph_rows, vtable_rows = validate_frozen_inputs(inputs)
    pe = parse_pe(data)
    require(pe["imageBase"] == IMAGE_BASE, "image base differs")
    text_row = section(pe, ".text")
    require(text_row["va"] == TEXT_VA and text_row["virtualBytes"] == TEXT_VIRTUAL_BYTES, ".text identity differs")
    text = data[int(text_row["rawOffset"]):int(text_row["rawOffset"]) + int(text_row["virtualBytes"])]

    bodies = {}
    for name, start, end, expected_hash in BODY_SPECS:
        body = va_bytes(data, pe, start, end - start)
        require(sha256_bytes(body) == expected_hash, f"{name} body hash differs")
        bodies[name] = {"startVa": f"0x{start:08x}", "endExclusiveVa": f"0x{end:08x}", "bytes": len(body), "sha256": expected_hash}
    span_start, span_end, span_hash = SHARED_RET_ALIGNMENT_SPAN
    require(sha256_bytes(va_bytes(data, pe, span_start, span_end - span_start)) == span_hash, "shared RET alignment-span hash differs")
    alignment_span = {"startVa": f"0x{span_start:08x}", "endExclusiveVa": f"0x{span_end:08x}", "bytes": span_end - span_start, "sha256": span_hash}
    for address, expected_hex in EXACT_BYTES.items():
        expected = bytes.fromhex(expected_hex)
        require(va_bytes(data, pe, address, len(expected)) == expected, f"exact instruction bytes differ at {address:#x}")
    require(va_bytes(data, pe, 0x005D8BC0, 4) == b"\x00\x00\x80\x41", "overlay 16.0 constant differs")
    require(read_ascii(data, pe, 0x00628418) == r"c:\debug.log", "dormant logger path differs")
    require(read_ascii(data, pe, 0x006244F4) == "setuphistory.txt", "setup logger path differs")
    helper_rows = []
    for label, site, target in HELPER_EDGES:
        decode_exact_transfer(data, pe, site, X86_INS_CALL, target)
        helper_rows.append({"label": label, "siteVa": f"0x{site:08x}", "targetVa": f"0x{target:08x}"})

    groups = (
        ("CConsole__Printf", PRINTF, X86_INS_CALL, 0xE8, 380, RESIDUAL_PRINTF_SITES),
        ("CConsole__PrintfNoNewline", PRINTF_NO_NEWLINE, X86_INS_CALL, 0xE8, 1, set()),
        ("CConsole__RenderStatusHistoryOverlay", OVERLAY, X86_INS_CALL, 0xE8, 1, set()),
        ("SharedRetStub_0040c640", SHARED_RET_STUB, X86_INS_CALL, 0xE8, 291, set()),
        ("SharedRetStub_0040c640", SHARED_RET_STUB, X86_INS_JMP, 0xE9, 10, set(RESIDUAL_STUB_JMPS)),
    )
    transfer_rows: list[dict[str, object]] = []
    range_cache: dict[tuple[str, str, str], dict[int, tuple[int, int, int]]] = {}
    receiver_counts = Counter()
    for target_kind, target, instruction_id, opcode, expected_count, allowed_residuals in groups:
        sites = rel32_sites(text, TEXT_VA, target, opcode)
        require(len(sites) == expected_count, f"{target_kind} {opcode:#x} candidate count differs")
        actual_residuals = set()
        for site in sites:
            owner = owner_for_site(site, body_rows)
            if owner is None:
                actual_residuals.add(site)
                require(site in allowed_residuals, f"unexpected residual transfer at {site:#x}")
                if site in RESIDUAL_STUB_JMPS:
                    frame_start, frame_end, frame_hash = RESIDUAL_STUB_JMPS[site]
                    require(sha256_bytes(va_bytes(data, pe, frame_start, frame_end - frame_start)) == frame_hash, f"residual frame hash differs at {site:#x}")
                    decode_exact_transfer(data, pe, site, instruction_id, target)
                else:
                    receiver_before(data, pe, site, target)
                owner_address = ""
                owner_name = ""
                mapping_state = "TEXT_RESIDUAL"
            else:
                validate_mapped_transfer(data, pe, site, instruction_id, target, owner, range_cache)
                owner_address = owner["functionAddress"]
                owner_name = owner["functionName"]
                mapping_state = "GHIDRA_FUNCTION_RANGE"
            receiver = ""
            receiver_channel = ""
            if target in {PRINTF, PRINTF_NO_NEWLINE}:
                receiver_value = receiver_before(data, pe, site, target)
                receiver_counts[(target, receiver_value)] += 1
                receiver = f"0x{receiver_value:08x}"
                receiver_channel = "DORMANT_INSTANCE" if receiver_value == DORMANT_RECEIVER else "SETUP_INSTANCE"
            elif target == OVERLAY:
                receiver = f"0x{DORMANT_RECEIVER:08x}"
                receiver_channel = "DORMANT_INSTANCE"
            transfer_rows.append({
                "targetKind": target_kind,
                "siteKind": "REL32_CALL" if instruction_id == X86_INS_CALL else "REL32_TAIL_JMP",
                "siteVa": f"0x{site:08x}",
                "mappingState": mapping_state,
                "ownerAddress": owner_address,
                "ownerName": owner_name,
                "receiverVa": receiver,
                "receiverChannel": receiver_channel,
            })
        require(actual_residuals == set(allowed_residuals), f"residual set differs for {target_kind} {opcode:#x}")

    require(receiver_counts[(PRINTF, DORMANT_RECEIVER)] == 253, "Printf dormant-instance split differs")
    require(receiver_counts[(PRINTF, SETUP_RECEIVER)] == 127, "Printf setup-instance split differs")
    require(receiver_counts[(PRINTF_NO_NEWLINE, DORMANT_RECEIVER)] == 1, "PrintfNoNewline receiver differs")

    graph_targets = {
        "CConsole__Printf": PRINTF,
        "CConsole__PrintfNoNewline": PRINTF_NO_NEWLINE,
        "CConsole__RenderStatusHistoryOverlay": OVERLAY,
        "SharedRetStub_0040c640": SHARED_RET_STUB,
    }
    for target_kind, target in graph_targets.items():
        require(mapped_row_counter(transfer_rows, target_kind) == graph_counter(graph_rows, target), f"decoded sites do not reconcile with pinned Ghidra graph for {target_kind}")

    rdata = section(pe, ".rdata")
    rdata_bytes = data[int(rdata["rawOffset"]):int(rdata["rawOffset"]) + int(rdata["virtualBytes"])]
    needle = struct.pack("<I", SHARED_RET_STUB)
    pointer_sites = [int(rdata["va"]) + index for index in range(len(rdata_bytes) - 3) if rdata_bytes[index:index + 4] == needle]
    require(len(pointer_sites) == 22, "shared RET .rdata pointer count differs")
    vtable_matches = []
    for row in vtable_rows:
        if parse_hex(row["function_va"], "function_va") != SHARED_RET_STUB:
            continue
        reference = parse_hex(row["vtable_va"], "vtable_va") + int(row["slot"]) * 4
        vtable_matches.append((reference, row))
    require(len(vtable_matches) == 22 and {reference for reference, _row in vtable_matches} == set(pointer_sites), "shared RET pointers do not reconcile with RTTI vtable slots")
    data_rows = [
        {
            "targetKind": "SharedRetStub_0040c640",
            "referenceKind": "RTTI_VTABLE_SLOT",
            "referenceVa": f"0x{reference:08x}",
            "className": row["class"],
            "vtableVa": row["vtable_va"],
            "slot": row["slot"],
        }
        for reference, row in sorted(vtable_matches, key=lambda item: (item[0], item[1]["class"], int(item[1]["slot"])))
    ]

    call_bytes = render_tsv(CALL_COLUMNS, transfer_rows)
    data_bytes = render_tsv(DATA_COLUMNS, data_rows)
    counts = {
        "printfDirectCalls": 380,
        "printfMappedCalls": 377,
        "printfResidualCalls": 3,
        "printfDormantReceiverCalls": 253,
        "printfSetupReceiverCalls": 127,
        "printfNoNewlineDirectCalls": 1,
        "overlayDirectCalls": 1,
        "foldedStubRel32Calls": 291,
        "foldedStubTailJumps": 10,
        "foldedStubMappedTransfers": 299,
        "foldedStubResidualTailJumps": 2,
        "foldedStubRttiVtableSlots": 22,
        "foldedStubTotalReferences": 323,
        "historySlots": 30,
        "overlayDrawLoopIterations": 6,
    }
    topology = {
        "schema": SCHEMA,
        "specimen": {"bytes": SPECIMEN_BYTES, "md5": SPECIMEN_MD5, "sha256": SPECIMEN_SHA256},
        "decoder": {"name": "capstone", "version": CAPSTONE_VERSION},
        "text": {"startVa": f"0x{TEXT_VA:08x}", "virtualBytes": TEXT_VIRTUAL_BYTES},
        "counts": counts,
        "bodies": bodies,
        "sharedRetAlignmentSpan": alignment_span,
        "instances": {
            "dormant": {"address": "0x0066f580", "path": r"c:\debug.log", "initialEnabled": 0, "gateImmediateFileOffset": "0x000415c7"},
            "setup": {"address": "0x0066eb90", "path": "setuphistory.txt", "initialEnabled": 1},
        },
        "layout": {
            "vtableOffset": 0, "pathOffset": 4, "openedOffset": 8,
            "historyOffset": 9, "historySlots": 30, "historySlotBytes": 80,
            "timestampsOffset": 0x96C, "indexOffset": 0x9E4,
            "lastLineTimeOffset": 0x9E8, "enabledOffset": 0x9EC,
            "minimumObjectBytes": 0x9F0,
        },
        "coupling": {
            "printf": {"gateSkipVa": "0x0044178b", "fileOpenFailureSkipVa": "0x004417fe", "sharedExitVa": "0x00441894", "ringUpdateVa": "0x00441823"},
            "printfNoNewline": {"gateSkipVa": "0x004418b7", "fileOpenFailureSkipVa": "0x0044192b", "sharedExitVa": "0x004419cf", "ringUpdateVa": "0x0044195f"},
            "helperEdges": helper_rows,
        },
        "overlay": {
            "address": "0x004419e0", "receiverLoadVa": "0x0047181d", "callerVa": "0x0047182c",
            "unresolvedTimebaseVa": "0x00672fd0", "windowConstant": 16.0,
            "drawLoopIterations": 6, "storedSlots": 30, "visualCaptureStatus": "NOT_PROVED",
        },
        "sharedRetStub": {
            "address": "0x0040c640", "semanticCallee": "UNRESOLVED_SHARED_RET_STUB",
            "printfSubsetSites": ["0x00441767", "0x00441774"],
            "globalPatchVerdict": "REJECT_SHARED_TARGET_MIXED_CALL_SHAPES_AND_RECURSIVE_PRINT_PATH",
            "referenceClasses": {"rel32Calls": 291, "rel32TailJumps": 10, "rttiVtableSlots": 22, "total": 323},
        },
        "directTransferSitesSha256": sha256_bytes(call_bytes),
        "foldedStubVtableSlotsSha256": sha256_bytes(data_bytes),
        "claimBoundary": list(CLAIM_BOUNDARY),
    }
    return call_bytes, data_bytes, canonical_json(topology), topology


def derive(specimen: Path, inputs: Mapping[str, bytes]) -> tuple[bytes, bytes, bytes, dict[str, object]]:
    require(specimen.is_file() and not is_linklike(specimen), "specimen is not one plain file")
    require(specimen.stat().st_size == SPECIMEN_BYTES and sha256_file(specimen) == SPECIMEN_SHA256, "specimen identity differs")
    return derive_bytes(specimen.read_bytes(), inputs)


def load_external_inputs(parity: Path, rtti: Path) -> dict[str, bytes]:
    require(parity.is_dir() and not is_linklike(parity), "parity input is not one plain directory")
    require(rtti.is_dir() and not is_linklike(rtti), "RTTI input is not one plain directory")
    result = {}
    for frozen_name, source_name in PARITY_SOURCE_NAMES.items():
        path = parity / source_name
        require(path.is_file() and not is_linklike(path), f"parity input is not one plain file: {source_name}")
        result[frozen_name] = path.read_bytes()
    for frozen_name, source_name in RTTI_SOURCE_NAMES.items():
        path = rtti / source_name
        require(path.is_file() and not is_linklike(path), f"RTTI input is not one plain file: {source_name}")
        result[frozen_name] = path.read_bytes()
    validate_frozen_inputs(result)
    return result


def output_bytes(owner: Path, specimen: Path, inputs: Mapping[str, bytes]) -> tuple[dict[str, bytes], dict[str, object]]:
    calls, data_slots, topology_bytes, topology = derive(specimen, inputs)
    return {
        "console-output-topology-owner.py": owner.read_bytes(),
        "direct-transfer-sites.tsv": calls,
        "folded-stub-vtable-slots.tsv": data_slots,
        "console-output-topology.json": topology_bytes,
    }, topology


def stamp_bytes(name: str, data: bytes) -> dict[str, object]:
    return {"path": name, "bytes": len(data), "sha256": sha256_bytes(data)}


def validate_bundle_tree(bundle: Path) -> None:
    require(bundle.is_dir() and not is_linklike(bundle), "bundle is not one plain directory or is a reparse point")
    root_expected = {"READY.json", "inputs", *OUTPUT_NAMES}
    root_actual = {path.name for path in bundle.iterdir()}
    require(root_actual == root_expected, f"bundle members differ: {sorted(root_actual ^ root_expected)}")
    for name in {"READY.json", *OUTPUT_NAMES}:
        path = bundle / name
        require(path.is_file() and not is_linklike(path), f"bundle member is not one plain file: {name}")
    inputs = bundle / "inputs"
    require(inputs.is_dir() and not is_linklike(inputs), "bundle inputs is not one plain directory")
    expected_input_files = {Path(name).name for name in INPUT_NAMES}
    actual_input_files = {path.name for path in inputs.iterdir()}
    require(actual_input_files == expected_input_files, f"bundle input members differ: {sorted(actual_input_files ^ expected_input_files)}")
    for name in expected_input_files:
        path = inputs / name
        require(path.is_file() and not is_linklike(path), f"bundle input is not one plain file: {name}")


def read_bundle_inputs(bundle: Path) -> dict[str, bytes]:
    return {name: (bundle / name).read_bytes() for name in INPUT_NAMES}


def expected_ready(inputs: Mapping[str, bytes], outputs: Mapping[str, bytes], topology: Mapping[str, object]) -> dict[str, object]:
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "specimen": {"bytes": SPECIMEN_BYTES, "md5": SPECIMEN_MD5, "sha256": SPECIMEN_SHA256},
        "counts": topology["counts"],
        "inputs": {name: stamp_bytes(name, inputs[name]) for name in INPUT_NAMES},
        "outputs": {name: stamp_bytes(name, outputs[name]) for name in OUTPUT_NAMES},
        "claimBoundary": list(CLAIM_BOUNDARY),
    }


def verify(bundle: Path, specimen: Path) -> dict[str, object]:
    validate_bundle_tree(bundle)
    owner = Path(__file__).resolve()
    require((bundle / "console-output-topology-owner.py").read_bytes() == owner.read_bytes(), "frozen owner differs from executing owner")
    raw_ready = (bundle / "READY.json").read_bytes()
    try:
        ready = json.loads(raw_ready.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise TopologyError(f"READY is invalid JSON: {exc}") from exc
    require(raw_ready == canonical_json(ready), "READY is not canonical JSON")
    inputs = read_bundle_inputs(bundle)
    outputs, topology = output_bytes(owner, specimen, inputs)
    require(ready == expected_ready(inputs, outputs, topology), "READY semantics differ")
    for name, content in outputs.items():
        require((bundle / name).read_bytes() == content, f"derived output differs: {name}")
    return {"schema": SCHEMA, "status": STATUS, "readySha256": sha256_file(bundle / "READY.json"), "counts": ready["counts"]}


def build(specimen: Path, parity: Path, rtti: Path, out: Path) -> dict[str, object]:
    require(not out.exists() and out.parent.is_dir(), "output must be a new child of an existing directory")
    owner = Path(__file__).resolve()
    inputs = load_external_inputs(parity, rtti)
    outputs, topology = output_bytes(owner, specimen, inputs)
    ready = expected_ready(inputs, outputs, topology)
    staging = Path(tempfile.mkdtemp(prefix=f".{out.name}-", dir=out.parent))
    try:
        (staging / "inputs").mkdir()
        for name, content in inputs.items():
            (staging / name).write_bytes(content)
        for name, content in outputs.items():
            (staging / name).write_bytes(content)
        (staging / "READY.json").write_bytes(canonical_json(ready))
        verify(staging, specimen)
        os.rename(staging, out)
        return ready
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    subparsers = result.add_subparsers(dest="command", required=True)
    build_parser = subparsers.add_parser("build")
    build_parser.add_argument("--specimen", required=True, type=Path)
    build_parser.add_argument("--parity", required=True, type=Path)
    build_parser.add_argument("--rtti", required=True, type=Path)
    build_parser.add_argument("--out", required=True, type=Path)
    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument("--specimen", required=True, type=Path)
    verify_parser.add_argument("--bundle", required=True, type=Path)
    return result


def main(argv: Sequence[str] | None = None) -> int:
    arguments = parser().parse_args(argv)
    try:
        if arguments.command == "build":
            ready = build(arguments.specimen.resolve(), arguments.parity.resolve(), arguments.rtti.resolve(), arguments.out.resolve())
            result = {"schema": SCHEMA, "status": STATUS, "out": str(arguments.out.resolve()), "counts": ready["counts"]}
        else:
            result = verify(arguments.bundle.absolute(), arguments.specimen.resolve())
        print(json.dumps(result, sort_keys=True))
    except (TopologyError, OSError, ValueError, KeyError) as exc:
        print(f"UNSCORED: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
