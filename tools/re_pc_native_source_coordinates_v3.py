#!/usr/bin/env python3
"""Recover byte-backed PC __FILE__/__LINE__ allocator coordinates.

The frozen 2026-08-12 scanner required adjacent ``push line; push path``
instructions.  This successor resolves the four arguments present at each
proven allocator/free consumer over bounded concrete CFG predecessor paths. It
accepts stack-stable scheduling, predecessor-carried line values,
register-carried constants, and explicit ESP-relative argument stores only when
dataflow places an exact NUL-terminated source path and a bounded line number in
the consumer's path/line slots.

Inputs are explicit, and both predecessor coordinate tables are pinned by
exact hash, schema, row count, and function count.  The pristine specimen is
read only, no Ghidra project is opened, historical tables are never rewritten,
and generated manifests are immutable: use ``--check`` or a fresh output
directory for a second replay.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import pathlib
import re
import struct
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, replace

from capstone import (
    CS_ARCH_X86,
    CS_GRP_CALL,
    CS_GRP_IRET,
    CS_GRP_JUMP,
    CS_GRP_RET,
    CS_MODE_32,
    Cs,
    CsError,
)
from capstone.x86 import X86_OP_IMM, X86_OP_MEM, X86_OP_REG


EXPECTED_SPECIMEN_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)
SOURCE_PATH_BYTES_RE = re.compile(
    rb"(?P<path>[A-Za-z]:\\[\x20-\x7e]*?\.(?:cpp|hpp|inl|c|h))\x00",
    re.IGNORECASE,
)
LEGACY_PRINTABLE_RUN_RE = re.compile(rb"[\x20-\x7e]{6,}")
SOURCE_PATH_TEXT_RE = re.compile(
    r"^[A-Za-z]:\\.*\.(?:cpp|hpp|inl|c|h)$",
    re.IGNORECASE,
)
CONTROL_GROUPS = {CS_GRP_CALL, CS_GRP_JUMP, CS_GRP_RET, CS_GRP_IRET}
MAX_BACKWARD_INSTRUCTIONS = 128
MAX_BACKWARD_PATHS = 1024
CONSUMERS = {
    0x00449D40: "OID__FreeObject_Callback",
    0x004A1810: "CMemoryHeap__Alloc",
    0x005490E0: "CDXMemoryManager__Alloc",
}
OUTPUT_NAMES = (
    "candidate-manifest.json",
    "candidate-manifest.tsv",
    "rejected-consumer-calls.tsv",
    "scan.ready.json",
)
FROZEN_OUTPUT_NAMES = {
    "pc-native-source-coordinates-2026-08-12.tsv",
    "ghidra-function-name-table-2026-08-13.tsv",
}
ARGUMENT_OFFSETS = {
    "sizeOrObject": 0,
    "allocationType": 4,
    "sourcePath": 8,
    "sourceLine": 12,
}
FULL_REGISTERS = {"eax", "ebx", "ecx", "edx", "esi", "edi", "ebp", "esp"}
REGISTER_ROOTS = {
    "eax": "eax", "ax": "eax", "al": "eax", "ah": "eax",
    "ebx": "ebx", "bx": "ebx", "bl": "ebx", "bh": "ebx",
    "ecx": "ecx", "cx": "ecx", "cl": "ecx", "ch": "ecx",
    "edx": "edx", "dx": "edx", "dl": "edx", "dh": "edx",
    "esi": "esi", "si": "esi",
    "edi": "edi", "di": "edi",
    "ebp": "ebp", "bp": "ebp",
    "esp": "esp", "sp": "esp",
}
CONFIDENCE = "HIGH_STATIC_DIRECT_CALL_ARGUMENT_DATAFLOW"
FALSIFIER = (
    "Falsified if the named pristine bytes differ, the path VA is not the start "
    "of the recorded NUL-terminated source path, dataflow no longer places path "
    "and line at consumer-entry [ESP+0x08]/[ESP+0x0C], or the direct consumer's "
    "four-argument debug contract is disproved."
)


class CoordinateScanError(RuntimeError):
    """An input identity, schema, or deterministic-output check failed."""


@dataclass(frozen=True)
class CoordinateTablePin:
    label: str
    sha256: str
    schema: tuple[str, ...]
    data_rows: int
    functions: int


BASELINE_COORDINATE_PIN = CoordinateTablePin(
    label="frozen 2026-08-12 coordinate owner",
    sha256="eb2abec9ca8532e11ed89e4f0f1b39fbbf84501d7e93d297717cfaa996bca90f",
    schema=(
        "sourcePath", "sourceLine", "functionVa", "functionName",
        "pushLineAt", "pushPathAt",
    ),
    data_rows=1_559,
    functions=827,
)
PROVISIONAL_COORDINATE_PIN = CoordinateTablePin(
    label="reviewed 2026-08-13 stack-stable intermediate",
    sha256="2da8d84135b3b1e4881af62cbf73f202656c091c98bda02e4969ff4efec18a76",
    schema=(
        "sourcePath", "sourceLine", "functionVa", "functionName",
        "pushLineAt", "pushPathAt", "pairingMode", "interveningInstructions",
        "consumerAt", "consumerVa", "consumerName",
    ),
    data_rows=1_840,
    functions=993,
)


@dataclass(frozen=True)
class Section:
    name: str
    virtual_address: int
    virtual_span: int
    raw_pointer: int
    raw_size: int
    characteristics: int


class PeImage:
    """Small PE32 mapper sufficient for deterministic VA reads."""

    def __init__(self, path: pathlib.Path):
        self.path = path
        self.data = path.read_bytes()
        if len(self.data) < 0x40:
            raise CoordinateScanError(f"truncated image: {path}")
        pe_offset = struct.unpack_from("<I", self.data, 0x3C)[0]
        if self.data[pe_offset : pe_offset + 4] != b"PE\0\0":
            raise CoordinateScanError(f"not a PE image: {path}")
        coff = pe_offset + 4
        section_count = struct.unpack_from("<H", self.data, coff + 2)[0]
        optional_size = struct.unpack_from("<H", self.data, coff + 16)[0]
        optional = coff + 20
        if struct.unpack_from("<H", self.data, optional)[0] != 0x10B:
            raise CoordinateScanError("expected a PE32 optional header")
        self.image_base = struct.unpack_from("<I", self.data, optional + 28)[0]
        section_table = optional + optional_size
        sections: list[Section] = []
        for index in range(section_count):
            offset = section_table + index * 40
            name = self.data[offset : offset + 8].rstrip(b"\0").decode(
                "ascii", errors="replace"
            )
            virtual_size, virtual_address, raw_size, raw_pointer = struct.unpack_from(
                "<IIII", self.data, offset + 8
            )
            characteristics = struct.unpack_from("<I", self.data, offset + 36)[0]
            sections.append(
                Section(
                    name=name,
                    virtual_address=virtual_address,
                    virtual_span=max(virtual_size, raw_size),
                    raw_pointer=raw_pointer,
                    raw_size=raw_size,
                    characteristics=characteristics,
                )
            )
        self.sections = tuple(sections)

    def read_va(self, va: int, size: int) -> bytes:
        if size < 0:
            raise CoordinateScanError("negative VA read")
        rva = va - self.image_base
        for section in self.sections:
            relative = rva - section.virtual_address
            if 0 <= relative and relative + size <= section.raw_size:
                start = section.raw_pointer + relative
                return self.data[start : start + size]
        raise CoordinateScanError(
            f"VA range is not backed by specimen bytes: 0x{va:08X}+0x{size:X}"
        )

    def raw_offset_to_va(self, raw_offset: int) -> int | None:
        for section in self.sections:
            relative = raw_offset - section.raw_pointer
            if 0 <= relative < section.raw_size:
                return self.image_base + section.virtual_address + relative
        return None


@dataclass(frozen=True)
class FunctionRange:
    va: int
    name: str
    body_min: int
    body_max: int


@dataclass(frozen=True)
class SymbolicValue:
    kind: str
    constant: int | None = None
    stack_offset: int | None = None
    origin_at: int | None = None
    witnesses: tuple[int, ...] = ()
    reason: str = ""

    @staticmethod
    def unknown(reason: str) -> "SymbolicValue":
        return SymbolicValue("UNKNOWN", reason=reason)

    @staticmethod
    def constant_value(value: int, at: int) -> "SymbolicValue":
        return SymbolicValue(
            "CONSTANT",
            constant=value & 0xFFFFFFFF,
            origin_at=at,
            witnesses=(at,),
        )

    @staticmethod
    def stack_address(offset: int, at: int) -> "SymbolicValue":
        return SymbolicValue(
            "STACK_ADDRESS",
            stack_offset=offset,
            origin_at=at,
            witnesses=(at,),
        )

    def carried_at(self, at: int) -> "SymbolicValue":
        if self.kind == "UNKNOWN":
            return self
        if at in self.witnesses:
            return self
        return replace(self, witnesses=(*self.witnesses, at))


@dataclass(frozen=True)
class StackCell:
    value: SymbolicValue
    written_at: int
    write_kind: str


@dataclass(frozen=True)
class Candidate:
    source_path: str
    source_path_va: int
    source_line: int
    function_va: int
    function_name: str
    line_origin_at: int
    line_argument_at: int
    path_origin_at: int
    path_argument_at: int
    argument_mode: str
    pairing_mode: str
    intervening_instructions: int
    consumer_at: int
    consumer_va: int
    consumer_name: str
    witness_start_at: int
    witness_end_at: int
    ordered_witness_bytes_sha256: str
    instruction_witness: tuple[str, ...]
    confidence: str = CONFIDENCE
    falsifier: str = FALSIFIER
    novelty: str = "UNCLASSIFIED"


@dataclass(frozen=True)
class Rejection:
    function_va: int
    function_name: str
    consumer_at: int
    consumer_va: int
    consumer_name: str
    block_start_at: int
    reason: str
    arguments: tuple[str, str, str, str]
    instruction_witness: tuple[str, ...]


@dataclass
class AbstractState:
    esp: int
    registers: dict[str, SymbolicValue]
    stack: dict[int, StackCell]
    valid: bool = True
    failure: str = ""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_projection(path: pathlib.Path) -> list[FunctionRange]:
    lines = [
        line
        for line in path.read_text(encoding="utf-8").splitlines()
        if line and not line.startswith("#")
    ]
    reader = csv.DictReader(lines, delimiter="\t")
    expected = {"address", "name", "bodyMin", "bodyMax"}
    if set(reader.fieldnames or ()) != expected:
        raise CoordinateScanError(
            f"unexpected projection schema in {path}: {reader.fieldnames}"
        )
    functions: list[FunctionRange] = []
    seen: set[int] = set()
    for row in reader:
        va = int(row["address"], 16)
        if va in seen:
            raise CoordinateScanError(f"duplicate projection address: 0x{va:08X}")
        seen.add(va)
        body_min = int(row["bodyMin"], 16)
        body_max = int(row["bodyMax"], 16)
        if body_max < body_min:
            raise CoordinateScanError(f"inverted range at 0x{va:08X}")
        functions.append(FunctionRange(va, row["name"], body_min, body_max))
    return sorted(functions, key=lambda row: row.va)


def discover_source_path_offsets(data: bytes) -> dict[int, str]:
    """Find drive-rooted NUL-terminated paths even after printable binary bytes."""

    paths: dict[int, str] = {}
    for match in SOURCE_PATH_BYTES_RE.finditer(data):
        text = match.group("path").decode("ascii")
        if not SOURCE_PATH_TEXT_RE.fullmatch(text):
            continue
        offset = match.start("path")
        prior = paths.get(offset)
        if prior is not None and prior != text:
            raise CoordinateScanError(f"ambiguous source path at raw 0x{offset:X}")
        paths[offset] = text
    return paths


def find_source_paths(image: PeImage) -> dict[int, str]:
    paths: dict[int, str] = {}
    for raw_offset, text in discover_source_path_offsets(image.data).items():
        va = image.raw_offset_to_va(raw_offset)
        if va is not None:
            paths[va] = text
    return paths


def find_source_paths_legacy(image: PeImage) -> dict[int, str]:
    """Reproduce the provisional maximal-printable-run path index for audit."""

    paths: dict[int, str] = {}
    for match in LEGACY_PRINTABLE_RUN_RE.finditer(image.data):
        text = match.group().decode("ascii")
        if not SOURCE_PATH_TEXT_RE.fullmatch(text):
            continue
        va = image.raw_offset_to_va(match.start())
        if va is not None:
            paths[va] = text
    return paths


def is_control_transfer(ins) -> bool:
    return any(group in CONTROL_GROUPS for group in ins.groups)


def instruction_text(ins) -> str:
    rendered = f"{ins.mnemonic} {ins.op_str}".rstrip()
    return f"0x{ins.address:08X}: {bytes(ins.bytes).hex()} {rendered}"


def register_name(ins, register_id: int) -> str:
    return ins.reg_name(register_id).lower() if register_id else ""


def register_root(ins, register_id: int) -> str | None:
    return REGISTER_ROOTS.get(register_name(ins, register_id))


def full_register_operand(ins, operand) -> str | None:
    if operand.type != X86_OP_REG:
        return None
    name = register_name(ins, operand.reg)
    return name if name in FULL_REGISTERS else None


def invalidate_stack_range(state: AbstractState, start: int, size: int) -> None:
    end = start + max(size, 1)
    for address in list(state.stack):
        if address < end and address + 4 > start:
            del state.stack[address]


def stack_address_for_operand(ins, operand, state: AbstractState) -> int | None:
    if operand.type != X86_OP_MEM:
        return None
    memory = operand.mem
    if memory.base:
        base_name = register_name(ins, memory.base)
        if base_name == "esp":
            address = state.esp
        else:
            root = register_root(ins, memory.base)
            base = state.registers.get(root or "", SymbolicValue.unknown("base"))
            if base.kind != "STACK_ADDRESS" or base.stack_offset is None:
                return None
            address = base.stack_offset
    else:
        return None
    if memory.index:
        root = register_root(ins, memory.index)
        index = state.registers.get(root or "", SymbolicValue.unknown("index"))
        if index.kind != "CONSTANT" or index.constant is None:
            return None
        address += index.constant * memory.scale
    return address + memory.disp


def resolve_operand(ins, operand, state: AbstractState) -> SymbolicValue:
    if operand.type == X86_OP_IMM:
        return SymbolicValue.constant_value(operand.imm, ins.address)
    if operand.type == X86_OP_REG:
        full = full_register_operand(ins, operand)
        if full is None:
            return SymbolicValue.unknown("partial-register-read")
        return state.registers.get(full, SymbolicValue.unknown("register-unresolved"))
    if operand.type == X86_OP_MEM:
        address = stack_address_for_operand(ins, operand, state)
        if address is None or operand.size != 4:
            return SymbolicValue.unknown("memory-unresolved")
        cell = state.stack.get(address)
        if cell is None:
            return SymbolicValue.unknown("stack-value-unresolved")
        return cell.value
    return SymbolicValue.unknown("unsupported-operand")


def assign_register(
    ins,
    destination,
    value: SymbolicValue,
    state: AbstractState,
) -> bool:
    full = full_register_operand(ins, destination)
    if full is None or full == "esp":
        return False
    state.registers[full] = value.carried_at(ins.address)
    return True


def store_stack(
    ins,
    destination,
    value: SymbolicValue,
    state: AbstractState,
    write_kind: str,
) -> bool:
    address = stack_address_for_operand(ins, destination, state)
    if address is None:
        return False
    invalidate_stack_range(state, address, destination.size or 4)
    if destination.size == 4:
        state.stack[address] = StackCell(
            value=value.carried_at(ins.address),
            written_at=ins.address,
            write_kind=write_kind,
        )
    return True


def invalidate_written_registers(ins, state: AbstractState, preserved: set[str]) -> None:
    try:
        _read, written = ins.regs_access()
    except CsError:
        written = ()
    for register_id in written:
        root = register_root(ins, register_id)
        if root is None or root in preserved:
            continue
        if root == "esp":
            state.valid = False
            state.failure = f"unhandled ESP write at 0x{ins.address:08X}"
        else:
            state.registers[root] = SymbolicValue.unknown("register-clobbered")


def execute_instruction(ins, state: AbstractState) -> None:
    mnemonic = ins.mnemonic.lower()
    operands = ins.operands
    preserved: set[str] = set()

    if mnemonic == "push" and operands:
        value = resolve_operand(ins, operands[0], state).carried_at(ins.address)
        state.esp -= 4
        state.stack[state.esp] = StackCell(
            value=value,
            written_at=ins.address,
            write_kind=(
                "PUSH_IMMEDIATE"
                if operands[0].type == X86_OP_IMM
                else "PUSH_REGISTER"
                if operands[0].type == X86_OP_REG
                else "PUSH_MEMORY"
            ),
        )
        preserved.add("esp")
    elif mnemonic == "pop" and operands:
        value = state.stack.get(
            state.esp,
            StackCell(SymbolicValue.unknown("pop-source-unresolved"), ins.address, "POP"),
        ).value
        if operands[0].type == X86_OP_REG:
            assigned = assign_register(ins, operands[0], value, state)
            if assigned:
                preserved.add(full_register_operand(ins, operands[0]) or "")
        state.esp += 4
        preserved.add("esp")
    elif mnemonic in {"mov", "movzx", "movsx"} and len(operands) >= 2:
        value = resolve_operand(ins, operands[1], state)
        if operands[0].type == X86_OP_REG:
            assigned = assign_register(ins, operands[0], value, state)
            if assigned:
                preserved.add(full_register_operand(ins, operands[0]) or "")
        elif operands[0].type == X86_OP_MEM:
            if store_stack(ins, operands[0], value, state, "ESP_RELATIVE_STORE"):
                preserved.add("esp")
    elif mnemonic == "lea" and len(operands) >= 2 and operands[0].type == X86_OP_REG:
        memory = operands[1]
        value = SymbolicValue.unknown("lea-unresolved")
        address = stack_address_for_operand(ins, memory, state)
        if address is not None:
            value = SymbolicValue.stack_address(address, ins.address)
        elif memory.type == X86_OP_MEM:
            base_value = 0
            known = True
            if memory.mem.base:
                root = register_root(ins, memory.mem.base)
                base = state.registers.get(root or "", SymbolicValue.unknown("lea-base"))
                if base.kind == "CONSTANT" and base.constant is not None:
                    base_value = base.constant
                else:
                    known = False
            if memory.mem.index:
                root = register_root(ins, memory.mem.index)
                index = state.registers.get(root or "", SymbolicValue.unknown("lea-index"))
                if index.kind == "CONSTANT" and index.constant is not None:
                    base_value += index.constant * memory.mem.scale
                else:
                    known = False
            if known:
                value = SymbolicValue.constant_value(
                    base_value + memory.mem.disp,
                    ins.address,
                )
        if assign_register(ins, operands[0], value, state):
            preserved.add(full_register_operand(ins, operands[0]) or "")
    elif mnemonic in {"add", "sub"} and len(operands) >= 2:
        destination = full_register_operand(ins, operands[0])
        source = resolve_operand(ins, operands[1], state)
        if destination == "esp" and source.kind == "CONSTANT" and source.constant is not None:
            amount = source.constant
            if mnemonic == "sub":
                state.esp -= amount
            else:
                state.esp += amount
            preserved.add("esp")
        elif destination is not None and destination != "esp":
            current = state.registers.get(
                destination, SymbolicValue.unknown("arithmetic-destination")
            )
            if (
                current.kind == "CONSTANT"
                and current.constant is not None
                and source.kind == "CONSTANT"
                and source.constant is not None
            ):
                result = (
                    current.constant + source.constant
                    if mnemonic == "add"
                    else current.constant - source.constant
                )
                value = SymbolicValue(
                    "CONSTANT",
                    constant=result & 0xFFFFFFFF,
                    origin_at=current.origin_at,
                    witnesses=(*current.witnesses, *source.witnesses, ins.address),
                )
            else:
                value = SymbolicValue.unknown("arithmetic-unresolved")
            state.registers[destination] = value
            preserved.add(destination)
    elif mnemonic in {"inc", "dec"} and operands:
        destination = full_register_operand(ins, operands[0])
        if destination and destination != "esp":
            current = state.registers.get(destination, SymbolicValue.unknown("incdec"))
            if current.kind == "CONSTANT" and current.constant is not None:
                delta = 1 if mnemonic == "inc" else -1
                state.registers[destination] = replace(
                    current,
                    constant=(current.constant + delta) & 0xFFFFFFFF,
                    witnesses=(*current.witnesses, ins.address),
                )
            else:
                state.registers[destination] = SymbolicValue.unknown("incdec-unresolved")
            preserved.add(destination)
    elif mnemonic == "xor" and len(operands) >= 2:
        left = full_register_operand(ins, operands[0])
        right = full_register_operand(ins, operands[1])
        if left is not None and left == right and left != "esp":
            state.registers[left] = SymbolicValue.constant_value(0, ins.address)
            preserved.add(left)
    else:
        if operands and operands[0].type == X86_OP_MEM:
            address = stack_address_for_operand(ins, operands[0], state)
            if address is not None:
                invalidate_stack_range(state, address, operands[0].size or 4)
                preserved.add("esp")

    invalidate_written_registers(ins, state, preserved)


def direct_target(ins) -> int | None:
    if (
        ins.mnemonic == "call"
        and ins.operands
        and ins.operands[0].type == X86_OP_IMM
    ):
        return ins.operands[0].imm & 0xFFFFFFFF
    return None


def instruction_predecessors(instructions: list) -> dict[int, tuple[int, ...]]:
    """Build a bounded intraprocedural predecessor map without crossing calls."""

    address_to_index = {ins.address: index for index, ins in enumerate(instructions)}
    branch_predecessors: dict[int, list[int]] = defaultdict(list)
    for index, ins in enumerate(instructions):
        if CS_GRP_JUMP not in ins.groups:
            continue
        if not ins.operands or ins.operands[0].type != X86_OP_IMM:
            continue
        target_index = address_to_index.get(ins.operands[0].imm & 0xFFFFFFFF)
        if target_index is not None:
            branch_predecessors[target_index].append(index)

    result: dict[int, tuple[int, ...]] = {}
    for index in range(len(instructions)):
        predecessors = list(branch_predecessors.get(index, ()))
        if index > 0:
            previous = instructions[index - 1]
            previous_is_call = CS_GRP_CALL in previous.groups
            previous_terminates = (
                CS_GRP_RET in previous.groups
                or CS_GRP_IRET in previous.groups
                or previous.mnemonic.lower() in {"jmp", "ljmp"}
            )
            if not previous_is_call and not previous_terminates:
                predecessors.append(index - 1)
        result[index] = tuple(sorted(set(predecessors)))
    return result


def cell_description(cell: StackCell | None) -> str:
    if cell is None:
        return "UNASSIGNED"
    value = cell.value
    if value.kind == "CONSTANT" and value.constant is not None:
        return f"0x{value.constant:08X}@0x{cell.written_at:08X}"
    if value.kind == "STACK_ADDRESS" and value.stack_offset is not None:
        return f"STACK({value.stack_offset:+#x})@0x{cell.written_at:08X}"
    return f"UNKNOWN({value.reason})@0x{cell.written_at:08X}"


def candidate_mode(line_cell: StackCell, path_cell: StackCell) -> str:
    kinds = {line_cell.write_kind, path_cell.write_kind}
    if "ESP_RELATIVE_STORE" in kinds:
        return "ESP_RELATIVE"
    if kinds == {"PUSH_IMMEDIATE"}:
        return "PUSH_IMMEDIATE"
    if "PUSH_REGISTER" in kinds or "PUSH_MEMORY" in kinds:
        return "REGISTER_OR_STACK_CARRIED"
    return "DATAFLOW_OTHER"


def candidate_key(candidate: Candidate) -> tuple:
    return (
        candidate.source_path.lower(),
        candidate.source_line,
        candidate.function_va,
        candidate.line_argument_at,
        candidate.path_argument_at,
    )


def evaluate_argument_path(
    instructions: list,
    path_indexes: tuple[int, ...],
    call_index: int,
    paths: dict[int, str],
    function_va: int,
    function_name: str,
) -> tuple[str, Candidate | None, str, tuple[str, str, str, str]]:
    """Evaluate one concrete predecessor path ending at a proven consumer."""

    call = instructions[call_index]
    target = direct_target(call)
    assert target in CONSUMERS
    state = AbstractState(esp=0, registers={}, stack={})
    for index in path_indexes:
        execute_instruction(instructions[index], state)
        if not state.valid:
            break
    cells = {
        name: state.stack.get(state.esp + offset)
        for name, offset in ARGUMENT_OFFSETS.items()
    }
    descriptions = tuple(
        cell_description(cells[name])
        for name in ("sizeOrObject", "allocationType", "sourcePath", "sourceLine")
    )
    if not state.valid:
        return "TERMINAL", None, state.failure, descriptions
    if any(cells[name] is None for name in ARGUMENT_OFFSETS):
        return "NEED_MORE", None, "four consumer argument slots unresolved", descriptions

    path_cell = cells["sourcePath"]
    line_cell = cells["sourceLine"]
    assert path_cell is not None and line_cell is not None
    path_value = path_cell.value
    line_value = line_cell.value
    if path_value.kind != "CONSTANT" or path_value.constant is None:
        return "NEED_MORE", None, "source-path argument unresolved", descriptions
    if path_value.constant not in paths:
        return (
            "TERMINAL",
            None,
            "source-path argument is not a NUL-terminated authored source path",
            descriptions,
        )
    if line_value.kind != "CONSTANT" or line_value.constant is None:
        return "NEED_MORE", None, "source-line argument unresolved", descriptions
    if not 0 < line_value.constant < 100_000:
        return "TERMINAL", None, "source-line argument is outside 1..99999", descriptions

    line_origin = line_value.origin_at or line_cell.written_at
    path_origin = path_value.origin_at or path_cell.written_at
    path_position = {
        instructions[index].address: position
        for position, index in enumerate(path_indexes)
    }
    line_position = path_position[line_cell.written_at]
    path_position_index = path_position[path_cell.written_at]
    mode = candidate_mode(line_cell, path_cell)
    between_start = min(line_position, path_position_index)
    between_end = max(line_position, path_position_index)
    crosses_control = any(
        is_control_transfer(instructions[path_indexes[position]])
        for position in range(between_start + 1, between_end)
    )
    if crosses_control:
        pairing = "DATAFLOW_CFG_PREDECESSOR"
    elif mode == "PUSH_IMMEDIATE" and path_position_index == line_position + 1:
        pairing = "ADJACENT"
    elif mode == "PUSH_IMMEDIATE":
        pairing = "STACK_STABLE_GAP"
    elif mode == "ESP_RELATIVE":
        pairing = "DATAFLOW_ESP_RELATIVE"
    else:
        pairing = "DATAFLOW_REGISTER_OR_STACK"
    intervening = max(abs(path_position_index - line_position) - 1, 0)
    relevant_positions = [line_position, path_position_index]
    if line_origin in path_position:
        relevant_positions.append(path_position[line_origin])
    if path_origin in path_position:
        relevant_positions.append(path_position[path_origin])
    witness_start_position = min(relevant_positions)
    witness_indexes = path_indexes[witness_start_position:]
    path_witness_instructions = [instructions[index] for index in witness_indexes]
    witness_instructions = [*path_witness_instructions, call]
    witness_bytes = b"".join(bytes(ins.bytes) for ins in witness_instructions)
    candidate = Candidate(
        source_path=paths[path_value.constant],
        source_path_va=path_value.constant,
        source_line=line_value.constant,
        function_va=function_va,
        function_name=function_name,
        line_origin_at=line_origin,
        line_argument_at=line_cell.written_at,
        path_origin_at=path_origin,
        path_argument_at=path_cell.written_at,
        argument_mode=mode,
        pairing_mode=pairing,
        intervening_instructions=intervening,
        consumer_at=call.address,
        consumer_va=target,
        consumer_name=CONSUMERS[target],
        witness_start_at=path_witness_instructions[0].address,
        witness_end_at=call.address + call.size - 1,
        ordered_witness_bytes_sha256=sha256_bytes(witness_bytes),
        instruction_witness=tuple(instruction_text(ins) for ins in witness_instructions),
    )
    return "ACCEPT", candidate, "", descriptions


def scan_decoded_function(
    instructions: list,
    paths: dict[int, str],
    function_va: int,
    function_name: str,
) -> tuple[list[Candidate], list[Rejection], list[tuple[int, str, str]]]:
    """Resolve consumer arguments over bounded concrete CFG predecessor paths."""

    if not instructions:
        return [], [], []
    predecessors = instruction_predecessors(instructions)
    candidates: list[Candidate] = []
    rejections: list[Rejection] = []
    path_references: list[tuple[int, str, str]] = []

    for ins in instructions:
        for operand in ins.operands:
            value = None
            if operand.type == X86_OP_IMM:
                value = operand.imm & 0xFFFFFFFF
            elif (
                operand.type == X86_OP_MEM
                and operand.mem.base == 0
                and operand.mem.index == 0
            ):
                value = operand.mem.disp & 0xFFFFFFFF
            if value in paths:
                operand_kind = (
                    "IMMEDIATE" if operand.type == X86_OP_IMM else "ABSOLUTE_MEMORY"
                )
                path_references.append(
                    (ins.address, paths[value], f"{ins.mnemonic}:{operand_kind}")
                )

    for call_index, call in enumerate(instructions):
        target = direct_target(call)
        if target not in CONSUMERS:
            continue
        work: list[tuple[tuple[int, ...], frozenset[int]]] = [
            ((), frozenset({call_index}))
        ]
        explored = 0
        accepted: dict[tuple, Candidate] = {}
        terminal_reasons: Counter[str] = Counter()
        last_descriptions = ("UNASSIGNED",) * 4
        last_path: tuple[int, ...] = ()
        while work and explored < MAX_BACKWARD_PATHS:
            suffix, visited = work.pop()
            frontier = suffix[0] if suffix else call_index
            for predecessor in reversed(predecessors.get(frontier, ())):
                if predecessor in visited:
                    continue
                path_indexes = (predecessor, *suffix)
                explored += 1
                status, candidate, reason, descriptions = evaluate_argument_path(
                    instructions,
                    path_indexes,
                    call_index,
                    paths,
                    function_va,
                    function_name,
                )
                last_descriptions = descriptions
                last_path = path_indexes
                if status == "ACCEPT":
                    assert candidate is not None
                    accepted[candidate_key(candidate)] = candidate
                    continue
                if status == "TERMINAL":
                    terminal_reasons[reason] += 1
                    continue
                if len(path_indexes) >= MAX_BACKWARD_INSTRUCTIONS:
                    terminal_reasons["backward dataflow instruction bound reached"] += 1
                    continue
                work.append((path_indexes, visited | {predecessor}))
                if explored >= MAX_BACKWARD_PATHS:
                    break
        if accepted:
            candidates.extend(accepted.values())
            continue
        if explored >= MAX_BACKWARD_PATHS:
            terminal_reasons["backward dataflow path bound reached"] += 1
        reason = (
            terminal_reasons.most_common(1)[0][0]
            if terminal_reasons
            else "no predecessor path proved four exact arguments"
        )
        witness_indexes = last_path[-12:]
        witness = tuple(
            instruction_text(instructions[index]) for index in witness_indexes
        ) + (instruction_text(call),)
        block_start_at = (
            instructions[last_path[0]].address if last_path else call.address
        )
        rejections.append(
            Rejection(
                function_va=function_va,
                function_name=function_name,
                consumer_at=call.address,
                consumer_va=target,
                consumer_name=CONSUMERS[target],
                block_start_at=block_start_at,
                reason=reason,
                arguments=last_descriptions,
                instruction_witness=witness,
            )
        )
    return candidates, rejections, path_references


def scan_projection(
    image: PeImage,
    functions: list[FunctionRange],
    paths: dict[int, str],
) -> tuple[list[Candidate], list[Rejection], list[tuple[int, int, str, str]]]:
    disassembler = Cs(CS_ARCH_X86, CS_MODE_32)
    disassembler.detail = True
    candidates: list[Candidate] = []
    rejections: list[Rejection] = []
    references: list[tuple[int, int, str, str]] = []
    for function in functions:
        size = function.body_max - function.body_min + 1
        instructions = list(
            disassembler.disasm(image.read_va(function.body_min, size), function.body_min)
        )
        function_candidates, function_rejections, function_references = (
            scan_decoded_function(
                instructions,
                paths,
                function.va,
                function.name,
            )
        )
        candidates.extend(function_candidates)
        rejections.extend(function_rejections)
        references.extend(
            (function.va, address, path, form)
            for address, path, form in function_references
        )
    candidates.sort(key=candidate_key)
    rejections.sort(key=lambda row: (row.function_va, row.consumer_at))
    references.sort()
    keys = [candidate_key(row) for row in candidates]
    if len(keys) != len(set(keys)):
        raise CoordinateScanError("duplicate candidate keys in current projection")
    return candidates, rejections, references


def load_coordinate_keys(
    path: pathlib.Path,
    pin: CoordinateTablePin,
) -> tuple[list[dict[str, str]], set[tuple]]:
    encoded = path.read_bytes()
    observed_hash = sha256_bytes(encoded)
    if observed_hash != pin.sha256:
        raise CoordinateScanError(
            f"{pin.label} hash mismatch: observed {observed_hash}"
        )
    reader = csv.DictReader(
        io.StringIO(encoded.decode("utf-8"), newline=""),
        delimiter="\t",
    )
    observed_schema = tuple(reader.fieldnames or ())
    if observed_schema != pin.schema:
        raise CoordinateScanError(
            f"{pin.label} schema mismatch: observed {observed_schema}"
        )
    rows = list(reader)
    if len(rows) != pin.data_rows:
        raise CoordinateScanError(
            f"{pin.label} row-count mismatch: observed {len(rows)}"
        )
    function_count = len({int(row["functionVa"], 16) for row in rows})
    if function_count != pin.functions:
        raise CoordinateScanError(
            f"{pin.label} function-count mismatch: observed {function_count}"
        )
    keys = {
        (
            row["sourcePath"].lower(),
            int(row["sourceLine"]),
            int(row["functionVa"], 16),
            int(row["pushLineAt"], 16),
            int(row["pushPathAt"], 16),
        )
        for row in rows
    }
    if len(keys) != len(rows):
        raise CoordinateScanError(f"duplicate coordinate keys in {path}")
    return rows, keys


def classify_novelty(
    candidates: list[Candidate],
    owner_keys: set[tuple],
    provisional_keys: set[tuple],
    legacy_path_vas: set[int],
) -> list[Candidate]:
    classified: list[Candidate] = []
    for candidate in candidates:
        key = candidate_key(candidate)
        if key in owner_keys:
            novelty = "OWNER_2026_08_12"
        elif key in provisional_keys:
            novelty = (
                "CURRENT_PROJECTION_ADJACENT"
                if candidate.pairing_mode == "ADJACENT"
                else "STACK_STABLE_GAP"
            )
        elif candidate.source_path_va not in legacy_path_vas:
            novelty = "PATH_INDEX_RECOVERY"
        else:
            novelty = "DATAFLOW_RECOVERY"
        classified.append(replace(candidate, novelty=novelty))
    return classified


def is_real_name(name: str) -> bool:
    return bool(name) and not (
        name.startswith("FUN_")
        or name.startswith("Unwind@")
        or name.startswith("LAB_")
        or name.startswith("thunk_")
        or name in {"<none>", "<no_function>"}
    )


def hex_address(value: int) -> str:
    return f"0x{value:08X}"


def candidate_dict(candidate: Candidate) -> dict[str, object]:
    return {
        "sourcePath": candidate.source_path,
        "sourcePathVa": hex_address(candidate.source_path_va),
        "sourceLine": candidate.source_line,
        "functionVa": hex_address(candidate.function_va),
        "functionName": candidate.function_name,
        "lineOriginAt": hex_address(candidate.line_origin_at),
        "lineArgumentAt": hex_address(candidate.line_argument_at),
        "pathOriginAt": hex_address(candidate.path_origin_at),
        "pathArgumentAt": hex_address(candidate.path_argument_at),
        "argumentMode": candidate.argument_mode,
        "pairingMode": candidate.pairing_mode,
        "interveningInstructions": candidate.intervening_instructions,
        "consumerAt": hex_address(candidate.consumer_at),
        "consumerVa": hex_address(candidate.consumer_va),
        "consumerName": candidate.consumer_name,
        "witnessStartAt": hex_address(candidate.witness_start_at),
        "witnessEndAt": hex_address(candidate.witness_end_at),
        "orderedWitnessBytesSha256": candidate.ordered_witness_bytes_sha256,
        "instructionWitness": list(candidate.instruction_witness),
        "confidence": candidate.confidence,
        "falsifier": candidate.falsifier,
        "novelty": candidate.novelty,
    }


TSV_FIELDS = (
    "sourcePath", "sourcePathVa", "sourceLine", "functionVa", "functionName",
    "lineOriginAt", "lineArgumentAt", "pathOriginAt", "pathArgumentAt",
    "argumentMode", "pairingMode", "interveningInstructions", "consumerAt",
    "consumerVa", "consumerName", "witnessStartAt", "witnessEndAt",
    "orderedWitnessBytesSha256", "confidence", "novelty", "falsifier",
)


def render_candidate_tsv(candidates: list[Candidate]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(
        output,
        fieldnames=TSV_FIELDS,
        delimiter="\t",
        lineterminator="\n",
    )
    writer.writeheader()
    for candidate in candidates:
        row = candidate_dict(candidate)
        writer.writerow({field: row[field] for field in TSV_FIELDS})
    return output.getvalue().encode("utf-8")


REJECTION_FIELDS = (
    "functionVa", "functionName", "consumerAt", "consumerVa", "consumerName",
    "blockStartAt", "reason", "sizeOrObject", "allocationType", "sourcePath",
    "sourceLine", "instructionWitness",
)


def render_rejection_tsv(rejections: list[Rejection]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(
        output,
        fieldnames=REJECTION_FIELDS,
        delimiter="\t",
        lineterminator="\n",
    )
    writer.writeheader()
    for rejection in rejections:
        writer.writerow(
            {
                "functionVa": hex_address(rejection.function_va),
                "functionName": rejection.function_name,
                "consumerAt": hex_address(rejection.consumer_at),
                "consumerVa": hex_address(rejection.consumer_va),
                "consumerName": rejection.consumer_name,
                "blockStartAt": hex_address(rejection.block_start_at),
                "reason": rejection.reason,
                "sizeOrObject": rejection.arguments[0],
                "allocationType": rejection.arguments[1],
                "sourcePath": rejection.arguments[2],
                "sourceLine": rejection.arguments[3],
                "instructionWitness": " | ".join(rejection.instruction_witness),
            }
        )
    return output.getvalue().encode("utf-8")


def json_bytes(payload: object) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def build_outputs(
    image: PeImage,
    specimen_hash: str,
    projection_path: pathlib.Path,
    functions: list[FunctionRange],
    paths: dict[int, str],
    legacy_paths: dict[int, str],
    candidates: list[Candidate],
    rejections: list[Rejection],
    references: list[tuple[int, int, str, str]],
    owner_path: pathlib.Path,
    owner_rows: list[dict[str, str]],
    owner_keys: set[tuple],
    provisional_path: pathlib.Path,
    provisional_rows: list[dict[str, str]],
    provisional_keys: set[tuple],
) -> dict[str, bytes]:
    candidate_keys = {candidate_key(row) for row in candidates}
    missing_owner = owner_keys - candidate_keys
    missing_provisional = provisional_keys - candidate_keys
    if missing_owner:
        raise CoordinateScanError(
            f"current scan lost {len(missing_owner)} frozen owner coordinates"
        )
    if missing_provisional:
        raise CoordinateScanError(
            f"current scan lost {len(missing_provisional)} provisional coordinates"
        )
    reference_sites = {
        (function_va, address) for function_va, address, _path, _form in references
    }
    candidate_reference_sites = {
        (candidate.function_va, candidate.path_origin_at) for candidate in candidates
    }
    unmatched_references = reference_sites - candidate_reference_sites
    if unmatched_references:
        raise CoordinateScanError(
            f"{len(unmatched_references)} exact source-path references lack a candidate"
        )

    manifest = {
        "schemaVersion": "bea.re.pc-native-source-coordinate-candidates.v3",
        "specimen": {
            "bytes": len(image.data),
            "sha256": specimen_hash,
        },
        "projection": {
            "functions": len(functions),
            "sha256": sha256_bytes(projection_path.read_bytes()),
        },
        "sourcePathStringsInImage": len(paths),
        "candidates": [candidate_dict(row) for row in candidates],
    }
    candidate_json = json_bytes(manifest)
    candidate_tsv = render_candidate_tsv(candidates)
    rejection_tsv = render_rejection_tsv(rejections)

    owner_functions = {int(row["functionVa"], 16) for row in owner_rows}
    provisional_functions = {
        int(row["functionVa"], 16) for row in provisional_rows
    }
    candidate_functions = {row.function_va for row in candidates}
    dataflow_candidates = [
        row for row in candidates if row.novelty == "DATAFLOW_RECOVERY"
    ]
    accepted_call_sites = {
        (row.function_va, row.consumer_at) for row in candidates
    }
    rejected_call_sites = {
        (row.function_va, row.consumer_at) for row in rejections
    }
    receipt = {
        "schemaVersion": "bea.re.pc-native-source-coordinate-scan-ready.v3",
        "specimenSha256": specimen_hash,
        "specimenBytes": len(image.data),
        "projectionSha256": sha256_bytes(projection_path.read_bytes()),
        "projectionFunctions": len(functions),
        "ownerSha256": sha256_bytes(owner_path.read_bytes()),
        "ownerSchema": list(BASELINE_COORDINATE_PIN.schema),
        "ownerDataRows": len(owner_rows),
        "ownerPhysicalLines": len(owner_rows) + 1,
        "ownerFunctions": len(owner_functions),
        "provisionalSha256": sha256_bytes(provisional_path.read_bytes()),
        "provisionalSchema": list(PROVISIONAL_COORDINATE_PIN.schema),
        "provisionalCoordinates": len(provisional_rows),
        "provisionalFunctions": len(provisional_functions),
        "sourcePathStringsInImage": len(paths),
        "legacySourcePathStringsInImage": len(legacy_paths),
        "newlyIndexedSourcePaths": [
            {"va": hex_address(va), "path": paths[va]}
            for va in sorted(set(paths) - set(legacy_paths))
        ],
        "coordinateCount": len(candidates),
        "distinctSourcePaths": len({row.source_path for row in candidates}),
        "distinctFunctions": len(candidate_functions),
        "realNamedFunctions": len(
            {row.function_va for row in candidates if is_real_name(row.function_name)}
        ),
        "pairingModeHistogram": dict(
            sorted(Counter(row.pairing_mode for row in candidates).items())
        ),
        "argumentModeHistogram": dict(
            sorted(Counter(row.argument_mode for row in candidates).items())
        ),
        "consumerHistogram": dict(
            sorted(Counter(row.consumer_name for row in candidates).items())
        ),
        "noveltyHistogram": dict(
            sorted(Counter(row.novelty for row in candidates).items())
        ),
        "deltaVsOwner": {
            "coordinates": len(candidate_keys - owner_keys),
            "netDistinctFunctions": len(candidate_functions) - len(owner_functions),
            "ownerFullyContained": not missing_owner,
        },
        "deltaVsProvisional": {
            "coordinates": len(candidate_keys - provisional_keys),
            "netDistinctFunctions": (
                len(candidate_functions) - len(provisional_functions)
            ),
            "touchedFunctions": len(
                {
                    row.function_va
                    for row in candidates
                    if candidate_key(row) not in provisional_keys
                }
            ),
            "provisionalFullyContained": not missing_provisional,
        },
        "dataflowExtension": {
            "maximumBackwardInstructions": MAX_BACKWARD_INSTRUCTIONS,
            "maximumBackwardPathsPerConsumer": MAX_BACKWARD_PATHS,
            "registerOrEspRetailCandidates": sum(
                row.argument_mode != "PUSH_IMMEDIATE" for row in candidates
            ),
            "genuinelyNewDataflowCandidates": len(dataflow_candidates),
            "claim": (
                "Register-carried and ESP-relative argument recovery is enabled and "
                "covered by can-fail tests; the named retail projection contributes "
                "zero such exact-path candidates."
            ),
        },
        "pathReferenceAudit": {
            "exactReferencesInProjection": len(references),
            "uniqueInstructionSites": len(reference_sites),
            "unmatchedExactReferences": len(unmatched_references),
            "instructionFormHistogram": dict(
                sorted(Counter(form for _fn, _at, _path, form in references).items())
            ),
        },
        "negativeControls": {
            "directConsumerCalls": len(accepted_call_sites | rejected_call_sites),
            "acceptedCallSites": len(accepted_call_sites),
            "acceptedCoordinateCandidates": len(candidates),
            "rejectedCallSites": len(rejected_call_sites),
            "rejectionReasonHistogram": dict(
                sorted(Counter(row.reason for row in rejections).items())
            ),
            "nonPathSentinel662b2cRejected": any(
                "0x00662B2C" in row.arguments[2] for row in rejections
            ),
        },
        "outputs": {
            "candidate-manifest.json": {
                "bytes": len(candidate_json),
                "sha256": sha256_bytes(candidate_json),
            },
            "candidate-manifest.tsv": {
                "bytes": len(candidate_tsv),
                "sha256": sha256_bytes(candidate_tsv),
            },
            "rejected-consumer-calls.tsv": {
                "bytes": len(rejection_tsv),
                "sha256": sha256_bytes(rejection_tsv),
            },
        },
        "method": (
            "At each direct call to one of three proven consumers, enumerate bounded "
            "concrete intraprocedural predecessor paths without crossing another call, "
            "then execute each path in an abstract stack/register domain. Accept only "
            "when four assigned stack slots place an exact indexed NUL-terminated "
            "source path at [ESP+8] and a line in 1..99999 at [ESP+12]."
        ),
        "claimBoundary": (
            "A row proves the compiler emitted that coordinate as consumer arguments "
            "at the recorded instruction plate. Inlining may cross source files. The "
            "row proves no whole-function source ownership, signature, semantics, "
            "runtime behavior, or rebuild parity."
        ),
    }
    ready = json_bytes(receipt)
    return {
        "candidate-manifest.json": candidate_json,
        "candidate-manifest.tsv": candidate_tsv,
        "rejected-consumer-calls.tsv": rejection_tsv,
        "scan.ready.json": ready,
    }


def validate_output_directory(output_dir: pathlib.Path) -> None:
    resolved = output_dir.resolve()
    for target in (resolved / name for name in OUTPUT_NAMES):
        if target.name.lower() in FROZEN_OUTPUT_NAMES:
            raise CoordinateScanError(f"refusing frozen output target: {target}")
    lowered = str(resolved).replace("\\", "/").lower()
    if "/reverse-engineering/ghidra" in lowered:
        raise CoordinateScanError("refusing output beneath tracked/live Ghidra owners")


def publish_or_check(
    output_dir: pathlib.Path,
    outputs: dict[str, bytes],
    check: bool,
) -> None:
    validate_output_directory(output_dir)
    if check:
        mismatches = []
        for name, expected in outputs.items():
            target = output_dir / name
            if not target.is_file() or target.read_bytes() != expected:
                mismatches.append(name)
        if mismatches:
            raise CoordinateScanError(
                "deterministic output mismatch: " + ", ".join(mismatches)
            )
        return
    existing = [name for name in outputs if (output_dir / name).exists()]
    if existing:
        raise CoordinateScanError(
            "refusing to overwrite immutable outputs: " + ", ".join(existing)
        )
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, content in outputs.items():
        (output_dir / name).write_bytes(content)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--specimen", type=pathlib.Path, required=True)
    parser.add_argument("--projection", type=pathlib.Path, required=True)
    parser.add_argument("--baseline-coordinates", type=pathlib.Path, required=True)
    parser.add_argument("--provisional-coordinates", type=pathlib.Path, required=True)
    parser.add_argument("--output-dir", type=pathlib.Path, required=True)
    parser.add_argument(
        "--expected-specimen-sha256",
        default=EXPECTED_SPECIMEN_SHA256,
    )
    parser.add_argument("--expected-projection-sha256")
    parser.add_argument("--expected-projection-functions", type=int)
    parser.add_argument(
        "--check",
        action="store_true",
        help="compare deterministic bytes with an immutable output directory",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    arguments = parse_args(argv)
    try:
        image = PeImage(arguments.specimen)
        specimen_hash = sha256_bytes(image.data)
        if specimen_hash.lower() != arguments.expected_specimen_sha256.lower():
            raise CoordinateScanError(
                f"specimen hash mismatch: observed {specimen_hash}"
            )
        projection_hash = sha256_bytes(arguments.projection.read_bytes())
        if (
            arguments.expected_projection_sha256
            and projection_hash.lower()
            != arguments.expected_projection_sha256.lower()
        ):
            raise CoordinateScanError(
                f"projection hash mismatch: observed {projection_hash}"
            )
        functions = load_projection(arguments.projection)
        if (
            arguments.expected_projection_functions is not None
            and len(functions) != arguments.expected_projection_functions
        ):
            raise CoordinateScanError(
                f"projection count mismatch: observed {len(functions)}"
            )
        owner_rows, owner_keys = load_coordinate_keys(
            arguments.baseline_coordinates,
            BASELINE_COORDINATE_PIN,
        )
        provisional_rows, provisional_keys = load_coordinate_keys(
            arguments.provisional_coordinates,
            PROVISIONAL_COORDINATE_PIN,
        )
        paths = find_source_paths(image)
        legacy_paths = find_source_paths_legacy(image)
        candidates, rejections, references = scan_projection(image, functions, paths)
        candidates = classify_novelty(
            candidates,
            owner_keys,
            provisional_keys,
            set(legacy_paths),
        )
        outputs = build_outputs(
            image,
            specimen_hash,
            arguments.projection,
            functions,
            paths,
            legacy_paths,
            candidates,
            rejections,
            references,
            arguments.baseline_coordinates,
            owner_rows,
            owner_keys,
            arguments.provisional_coordinates,
            provisional_rows,
            provisional_keys,
        )
        publish_or_check(arguments.output_dir, outputs, arguments.check)
        receipt = json.loads(outputs["scan.ready.json"])
        receipt["operation"] = "CHECK_PASS" if arguments.check else "WRITE_COMPLETE"
        print(json.dumps(receipt, indent=2, sort_keys=True))
        return 0
    except (CoordinateScanError, FileNotFoundError, ValueError, struct.error) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
