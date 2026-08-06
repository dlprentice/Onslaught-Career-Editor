#!/usr/bin/env python3
"""Emit a deliberately small, straight-line Battle Engine Aquila script object.

This is not an MSL compiler.  It serialises only the six VM operations whose
runtime roles are independently settled and whose compiler templates occur in
the shipped corpus:

    PUSH, GETTOP, POINTER, REMOVE_TOP, CALL, RETURN

The accepted recipe has only two statement forms:

    {"op":"let", "name":"target", "native":"GetThingRef",
     "args":[{"string":"Turret 01"}]}
    {"op":"call", "target":"target", "native":"Damage",
     "args":[{"float":1000.0}]}

No branches, jumps, arithmetic, raw opcodes, or nested expressions are
accepted.  Every native index, arity, return discipline, and argument type is
read from the specimen-derived 144-slot descriptor table and that ignored
table is pinned by SHA-256.  `GetThingRef` is the one body-proven argument-type
override used here: its descriptor says thing while its handler reads the
string accessor (RE-SCENARIO-PRIMITIVES-2026-08-02.md S2.3).

The enclosing archive writer and an independent parser live in
`probe_author.py` / `local-lab/msl/script_parse.py`.  This module only produces
one `string32 name + scriptObject + end_script` record.
"""
from __future__ import annotations

import hashlib
import json
import math
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SCHEMA = "bea.missionscript.straight-line-program.v1"
NATIVE_TABLE_REL = Path("scenario-primitives-2026-08-02/native_table.json")
NATIVE_TABLE_SHA256 = "ca4c0f64efe86f7a48c0469988d6ae67d17dfc132358b9096d28f47cb894f61e"
SENTINEL = b"end_script"

OP_PUSH = 0x05
OP_REMOVE_TOP = 0x0E
OP_GETTOP = 0x15
OP_POINTER = 0x16
OP_RETURN = 0x17
OP_CALL = 0x18

TYPE_NONE = 0
TYPE_INT = 1
TYPE_FLOAT = 2
TYPE_STRING = 3
TYPE_BOOL = 4
TYPE_THING = 5
TYPE_POSITION = 6
TYPE_ANY = 7

ARG_FIELD_KEYS = ("ret", "f10", "f14", "f18", "f1c", "f20")
TYPE_NAMES = {
    TYPE_NONE: "none",
    TYPE_INT: "int",
    TYPE_FLOAT: "float",
    TYPE_STRING: "string",
    TYPE_BOOL: "bool",
    TYPE_THING: "thing",
    TYPE_POSITION: "position",
    TYPE_ANY: "any",
}

# The descriptor for GetThingRef says thing, but the handler at 0x005367c0
# reads argument zero through CStringDataType::GetString.  The handler wins.
BODY_ARGUMENT_OVERRIDES = {"GetThingRef": (TYPE_STRING,)}

# These are not an alternate signature source.  They are load-bearing canaries
# for the pinned table's field interpretation (+04 argc, +08 returns,
# +0c..+24 args, +28 return type).  A shifted mapping must refuse loudly.
SIGNATURE_CANARIES = {
    "Pause": (4, (TYPE_FLOAT,), False, TYPE_NONE),
    "LevelLost": (8, (), False, TYPE_NONE),
    "GetThingRef": (14, (TYPE_THING,), True, TYPE_THING),
    "SetVulnerable": (32, (TYPE_BOOL,), False, TYPE_NONE),
    "SetHealth": (46, (TYPE_FLOAT,), False, TYPE_NONE),
    "Damage": (69, (TYPE_FLOAT,), False, TYPE_NONE),
}


class EmitError(ValueError):
    """The structured program cannot be emitted without exceeding evidence."""


@dataclass(frozen=True)
class Native:
    index: int
    name: str
    arg_types: tuple[int, ...]
    returns: bool
    return_type: int

    @property
    def effective_arg_types(self) -> tuple[int, ...]:
        return BODY_ARGUMENT_OVERRIDES.get(self.name, self.arg_types)


@dataclass(frozen=True)
class Symbol:
    name: str
    type_tag: int
    value: Any
    source_line: int


@dataclass(frozen=True)
class EmittedRecord:
    record: bytes
    instructions: tuple[tuple[int, int], ...]
    symbols: tuple[Symbol, ...]
    metadata: dict[str, Any]


def _plain_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise EmitError(f"{label} must be an integer")
    return value


def _latin1(value: Any, label: str) -> bytes:
    if not isinstance(value, str) or not value:
        raise EmitError(f"{label} must be a non-empty string")
    if "\x00" in value:
        raise EmitError(f"{label} contains NUL, which would truncate the engine's C string")
    try:
        raw = value.encode("latin-1")
    except UnicodeEncodeError as exc:
        raise EmitError(f"{label} is not representable as the engine's latin-1 string") from exc
    if len(raw) > 1 << 20:
        raise EmitError(f"{label} exceeds the reader's 1 MiB string bound")
    return raw


def _str32(value: str, label: str) -> bytes:
    raw = _latin1(value, label)
    return struct.pack("<i", len(raw)) + raw


def _signed_call(index: int, argc: int, returns: bool) -> int:
    if not 0 <= index <= 0xFF or not 0 <= argc <= 0xFF:
        raise EmitError(f"CALL fields do not fit: native={index}, argc={argc}")
    unsigned = index | (argc << 8) | ((1 if returns else 0) << 16)
    return struct.unpack("<i", struct.pack("<I", unsigned))[0]


def load_native_table(lab_root: str | Path) -> tuple[dict[str, Native], dict[str, Any]]:
    """Load and authenticate the descriptor table recovered from the specimen."""
    path = Path(lab_root) / NATIVE_TABLE_REL
    if not path.is_file():
        raise EmitError(f"specimen-derived native signature table is missing: {path}")
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != NATIVE_TABLE_SHA256:
        raise EmitError(
            "native signature table SHA-256 mismatch; refuse to emit CALL operands: "
            f"expected {NATIVE_TABLE_SHA256}, found {digest}"
        )
    try:
        rows = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise EmitError(f"native signature table is not JSON: {exc}") from exc
    if not isinstance(rows, list) or len(rows) != 144:
        raise EmitError(f"native signature table must contain 144 rows, found {len(rows) if isinstance(rows, list) else 'non-list'}")

    by_name: dict[str, Native] = {}
    seen_indices: set[int] = set()
    for ordinal, row in enumerate(rows):
        if not isinstance(row, dict):
            raise EmitError(f"native row {ordinal} is not an object")
        index = _plain_int(row.get("i"), f"native row {ordinal}.i")
        argc = _plain_int(row.get("argc"), f"native row {ordinal}.argc")
        returns_word = _plain_int(row.get("f08"), f"native row {ordinal}.f08")
        return_type = _plain_int(row.get("f28"), f"native row {ordinal}.f28")
        if index != ordinal or index in seen_indices:
            raise EmitError(f"native table ordinal/index mismatch at row {ordinal}: {index}")
        if not 0 <= argc <= len(ARG_FIELD_KEYS):
            raise EmitError(f"native {index} has impossible argc {argc}")
        if returns_word not in (0, 1):
            raise EmitError(f"native {index} has non-boolean return flag {returns_word}")
        if return_type not in TYPE_NAMES:
            raise EmitError(f"native {index} has unknown return type {return_type}")
        arg_types = tuple(_plain_int(row.get(key), f"native row {ordinal}.{key}") for key in ARG_FIELD_KEYS[:argc])
        if any(tag not in TYPE_NAMES for tag in arg_types):
            raise EmitError(f"native {index} has an unknown argument type in {arg_types}")
        seen_indices.add(index)
        name = row.get("name")
        if not name:
            continue
        _latin1(name, f"native row {ordinal}.name")
        if name in by_name:
            raise EmitError(f"duplicate native name {name!r}")
        by_name[name] = Native(index, name, arg_types, bool(returns_word), return_type)

    for name, expected in SIGNATURE_CANARIES.items():
        native = by_name.get(name)
        actual = None if native is None else (
            native.index, native.arg_types, native.returns, native.return_type
        )
        if actual != expected:
            raise EmitError(f"native signature canary {name} is {actual}, expected {expected}")

    return by_name, {
        "path": str(path.resolve()),
        "sha256": digest,
        "rows": len(rows),
        "namedRows": len(by_name),
    }


def _constant(arg: dict[str, Any], label: str) -> tuple[int, Any]:
    if not isinstance(arg, dict) or len(arg) != 1:
        raise EmitError(f"{label} must be exactly one typed value: int/float/string/bool/var")
    kind, value = next(iter(arg.items()))
    if kind == "int":
        value = _plain_int(value, label)
        if not -(1 << 31) <= value < (1 << 31):
            raise EmitError(f"{label} does not fit a signed dword")
        return TYPE_INT, value
    if kind == "float":
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise EmitError(f"{label} must be a finite number")
        value = float(value)
        if not math.isfinite(value):
            raise EmitError(f"{label} must be finite")
        try:
            struct.pack("<f", value)
        except OverflowError as exc:
            raise EmitError(f"{label} does not fit a 32-bit float") from exc
        return TYPE_FLOAT, value
    if kind == "string":
        _latin1(value, label)
        return TYPE_STRING, value
    if kind == "bool":
        if not isinstance(value, bool):
            raise EmitError(f"{label} must be JSON true or false")
        return TYPE_BOOL, value
    if kind == "var":
        if not isinstance(value, str) or not value:
            raise EmitError(f"{label}.var must name a variable")
        return -1, value
    raise EmitError(f"{label} has unsupported type {kind!r}; use int/float/string/bool/var")


def _compatible(actual: int, expected: int) -> bool:
    if expected == TYPE_ANY or actual == expected:
        return True
    # CIntDataType is the only shipped coercion: it overrides GetFloat/GetBool.
    return actual == TYPE_INT and expected in (TYPE_FLOAT, TYPE_BOOL)


def _symbol_bytes(symbol: Symbol, ordinal: int) -> bytes:
    out = bytearray(_str32(symbol.name, f"symbol {ordinal} name"))
    out += struct.pack("<i", symbol.type_tag)
    if symbol.type_tag == TYPE_NONE:
        pass
    elif symbol.type_tag == TYPE_INT:
        out += struct.pack("<i", symbol.value)
    elif symbol.type_tag == TYPE_FLOAT:
        out += struct.pack("<f", symbol.value)
    elif symbol.type_tag == TYPE_STRING:
        out += _str32(symbol.value, f"symbol {ordinal} value")
    elif symbol.type_tag == TYPE_BOOL:
        out += struct.pack("<i", 1 if symbol.value else 0)
    else:
        raise EmitError(
            f"refuse to serialise symbol type {symbol.type_tag}; thing/position values "
            "are runtime-only and tags 5/6 have no shipped serialised examples"
        )
    out += struct.pack("<iii", symbol.source_line, ordinal, 1)
    return bytes(out)


def emit_record(
    script_name: str,
    program: list[dict[str, Any]],
    natives: dict[str, Native],
    *,
    native_table_meta: dict[str, Any] | None = None,
) -> EmittedRecord:
    """Compile a straight-line recipe into one complete script record."""
    _latin1(script_name, "script name")
    if not isinstance(program, list) or not program:
        raise EmitError("program must be a non-empty list of straight-line statements")
    if len(program) > 1024:
        raise EmitError("program exceeds the 1,024-statement safety bound")

    # The shipped compiler declares variables before handler/native/constant
    # symbols.  Preserve that shape while still compiling statements in order.
    variable_names: list[str] = []
    for line, stmt in enumerate(program, 1):
        if not isinstance(stmt, dict):
            raise EmitError(f"statement {line} is not an object")
        if stmt.get("op") == "let":
            name = stmt.get("name")
            _latin1(name, f"statement {line}.name")
            if name in variable_names:
                raise EmitError(f"statement {line} redeclares variable {name!r}")
            variable_names.append(name)

    symbols: list[Symbol] = [Symbol(name, TYPE_NONE, None, 0) for name in variable_names]
    symbol_index = {symbol.name: i for i, symbol in enumerate(symbols)}
    symbols.append(Symbol("init", TYPE_NONE, None, 1))
    native_symbol_indices: dict[str, int] = {}
    variable_types: dict[str, int | None] = {name: None for name in variable_names}
    instructions: list[tuple[int, int]] = [(OP_RETURN, -1)]  # variable-init prologue
    calls: list[dict[str, Any]] = []
    constant_no = 0

    def add_native_symbol(native: Native, source_line: int) -> None:
        if native.name not in native_symbol_indices:
            native_symbol_indices[native.name] = len(symbols)
            symbols.append(Symbol(native.name, TYPE_NONE, None, source_line))

    def push_arg(arg: dict[str, Any], expected: int, source_line: int, arg_no: int) -> None:
        nonlocal constant_no
        actual, value = _constant(arg, f"statement {source_line}.args[{arg_no}]")
        if actual == -1:
            if value not in symbol_index:
                raise EmitError(f"statement {source_line} reads undeclared variable {value!r}")
            actual = variable_types[value]
            if actual is None:
                raise EmitError(f"statement {source_line} reads uninitialised variable {value!r}")
            index = symbol_index[value]
        else:
            index = len(symbols)
            symbols.append(Symbol(f"const probe{constant_no:04d}", actual, value, source_line))
            constant_no += 1
        if not _compatible(actual, expected):
            raise EmitError(
                f"statement {source_line} argument {arg_no} is {TYPE_NAMES[actual]}, "
                f"but the native consumes {TYPE_NAMES[expected]}"
            )
        instructions.append((OP_PUSH, index))

    for source_line, stmt in enumerate(program, 1):
        op = stmt.get("op")
        allowed = {"op", "native", "args", "target"}
        if op == "let":
            allowed.add("name")
        if op not in ("let", "call"):
            raise EmitError(f"statement {source_line} has unsupported op {op!r}; only let/call exist")
        unknown = set(stmt) - allowed
        missing = {"native", "args"} - set(stmt)
        if unknown or missing:
            raise EmitError(
                f"statement {source_line} schema mismatch: unknown={sorted(unknown)}, missing={sorted(missing)}"
            )
        if op == "call" and "name" in stmt:
            raise EmitError(f"statement {source_line} call cannot declare a variable")

        native_name = stmt.get("native")
        native = natives.get(native_name)
        if native is None:
            raise EmitError(f"statement {source_line} names unknown native {native_name!r}")
        add_native_symbol(native, source_line)

        target = stmt.get("target")
        if target is not None:
            if not isinstance(target, str) or target not in symbol_index:
                raise EmitError(f"statement {source_line} target {target!r} is not a declared variable")
            target_type = variable_types[target]
            if target_type is None:
                raise EmitError(f"statement {source_line} targets uninitialised variable {target!r}")
            if target_type != TYPE_THING:
                raise EmitError(
                    f"statement {source_line} target {target!r} is {TYPE_NAMES[target_type]}, not thing"
                )
            instructions.extend(((OP_PUSH, symbol_index[target]), (OP_POINTER, -1)))

        args = stmt.get("args")
        if not isinstance(args, list):
            raise EmitError(f"statement {source_line}.args must be a list")
        expected_types = native.effective_arg_types
        if len(args) != len(expected_types):
            raise EmitError(
                f"statement {source_line} calls {native.name} with {len(args)} args; "
                f"descriptor requires {len(expected_types)}"
            )
        for arg_no, (arg, expected) in enumerate(zip(args, expected_types)):
            push_arg(arg, expected, source_line, arg_no)

        instructions.append((OP_CALL, _signed_call(native.index, len(args), native.returns)))
        calls.append({
            "statement": source_line,
            "native": native.name,
            "nativeIndex": native.index,
            "argc": len(args),
            "returns": native.returns,
            "target": target or "SCRIPT_SELF",
        })
        if op == "let":
            name = stmt["name"]
            if not native.returns or native.return_type in (TYPE_NONE, TYPE_ANY):
                raise EmitError(
                    f"statement {source_line} cannot assign {native.name}: descriptor return is "
                    f"{'void' if not native.returns else TYPE_NAMES[native.return_type]}"
                )
            instructions.append((OP_GETTOP, symbol_index[name]))
            variable_types[name] = native.return_type
        instructions.append((OP_REMOVE_TOP, -1))

    instructions.append((OP_RETURN, -1))
    if len(instructions) > 4096 or len(symbols) > 4096:
        raise EmitError("emitted object exceeds the 4,096 instruction/symbol safety bound")

    obj = bytearray(struct.pack("<i", len(instructions)))
    for opcode, operand in instructions:
        obj += struct.pack("<ii", opcode, operand)
    obj += struct.pack("<13i", 1, *([-1] * 12))  # built-in init handler starts at #1
    obj += struct.pack("<i", len(symbols))
    for ordinal, symbol in enumerate(symbols):
        obj += _symbol_bytes(symbol, ordinal)
    obj += struct.pack("<i", len(symbols))  # symtabTail
    obj += struct.pack("<i", 0)             # named-event count
    obj += struct.pack("<ii", 0, 1)         # trailerA, init-prologue flag

    record = _str32(script_name, "script name") + bytes(obj) + SENTINEL
    canonical_program = json.dumps(program, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
    metadata = {
        "schema": SCHEMA,
        "script": script_name,
        "programSha256": hashlib.sha256(canonical_program).hexdigest(),
        "recordSha256": hashlib.sha256(record).hexdigest(),
        "recordBytes": len(record),
        "instructionCount": len(instructions),
        "symbolCount": len(symbols),
        "eventEntryInit": 1,
        "nativeCalls": calls,
        "nativeTable": native_table_meta or {},
        "restrictions": [
            "straight-line let/call statements only",
            "no branches, jumps, arithmetic, raw opcodes, or nested expressions",
            "serialized constants limited to shipped tags 1..4",
        ],
    }
    return EmittedRecord(record, tuple(instructions), tuple(symbols), metadata)


def emit_record_from_lab(script_name: str, program: list[dict[str, Any]], lab_root: str | Path) -> EmittedRecord:
    natives, meta = load_native_table(lab_root)
    return emit_record(script_name, program, natives, native_table_meta=meta)
