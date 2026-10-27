#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Inspect one explicitly identified compiled mission-script record without executing it.

The structural owner is onslaught-decomp's src/MissionScript/ScriptObjectCode.cpp
(CMissionScriptObjectCode file constructor 00538ec0), AsmInstruction.cpp (Spawn
0052d3d0), Symtab.cpp (CSymbol/CSymbolTable file constructors 00539770),
DataType.cpp/.h (Create 0052ec60 and counted-string constructor 0052f790), and
EventFunction.cpp (file constructor 0052fa70). The existing Godot ScriptObjectCode
reader independently exposes the same stored fields. This is a Python inspection
surface for future mission tools, not a compiler, interpreter, mission editor,
runtime-effect proof or complete level parser.

Reports contain record identities, offsets, counts, event entry points, symbol
identifiers and event-name hashes. Literal string values, instruction operands
and payload byte arrays are never emitted. Keep generated retail reports private.
Unsupported data and trailing bytes retain explicit offset/length/hash records;
the tool never scans for a plausible start or silently discards unknown fields.

    python tools/mission_script_inspect.py RECORD --source-sha256 SHA --record-sha256 SHA
    python tools/mission_script_inspect.py SOURCE --offset N --length N \
        --source-sha256 SHA --record-sha256 SHA

The CLI reads only its selected input and prints metadata to stdout. It writes
no files, invokes no game and follows no links. A caller must select the record
boundary from an existing container reader, not by searching for matching bytes.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import struct
import sys

SCHEMA = "onslaught.compiled-mission-script-inspection.v1"
EVENT_COUNT = 13
VALUE_TYPES = {0: "none", 1: "int", 2: "float", 3: "string", 4: "bool", 5: "thing-pointer", 6: "position"}
SHA = re.compile(r"[0-9a-f]{64}\Z")
IDENTIFIER = re.compile(rb"[A-Za-z_][A-Za-z_0-9]{0,127}\Z")


class InspectionError(ValueError):
    """Invocation, identity or held-source failure, not a parsed format verdict."""


@dataclass(frozen=True)
class Limits:
    source_bytes: int = 4 * 1024 * 1024
    record_bytes: int = 2 * 1024 * 1024
    instructions: int = 65536
    symbols: int = 8192
    event_functions: int = 4096
    parameters_per_function: int = 1024
    total_parameters: int = 16384
    string_bytes: int = 65536
    total_string_bytes: int = 1024 * 1024

    def __post_init__(self):
        ceilings = (4*1024*1024, 2*1024*1024, 65536, 8192, 4096, 1024, 16384, 65536, 1024*1024)
        for name, ceiling in zip(self.__dataclass_fields__, ceilings):
            value = getattr(self, name)
            if type(value) is not int or not 1 <= value <= ceiling:
                raise ValueError(f"{name} must be an integer in 1..{ceiling}")


class _Stop(Exception):
    def __init__(self, status, code, offset):
        self.status, self.code, self.offset = status, code, offset


class _Reader:
    def __init__(self, source, begin, end, limits):
        self.source, self.begin, self.end, self.position, self.limits = source, begin, end, begin, limits
        self.strings = 0

    def take(self, length):
        if length < 0 or length > self.end - self.position:
            raise _Stop("malformed", "truncated-field", self.position)
        start = self.position
        self.position += length
        return memoryview(self.source)[start:self.position]

    def i32(self):
        return struct.unpack("<i", self.take(4))[0]

    def count(self, limit, minimum_size, kind):
        at = self.position
        value = self.i32()
        if value < 0:
            raise _Stop("malformed", "negative-" + kind, at)
        if value > limit:
            raise _Stop("unsupported", "profile-limit-" + kind, at)
        if value * minimum_size > self.end - self.position:
            raise _Stop("malformed", "truncated-" + kind, at)
        return value

    def string(self):
        length = self.count(self.limits.string_bytes, 1, "string-length")
        self.strings += length
        if self.strings > self.limits.total_string_bytes:
            raise _Stop("unsupported", "profile-limit-total-string-bytes", self.position)
        return self.position, self.take(length)


def _range(source, start, end):
    return {"offset": start, "length": end-start, "sha256": hashlib.sha256(memoryview(source)[start:end]).hexdigest()}


def _string_metadata(value):
    # Native CString consumers compare bytes before the first NUL. Preserve the
    # whole stored identity too; do not decode arbitrary literal mission text.
    raw = bytes(value)
    cstring = raw.split(b"\0", 1)[0]
    return {"length": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
            "cstringSha256": hashlib.sha256(cstring).hexdigest(),
            "containsNul": b"\0" in raw,
            "identifier": cstring.decode("ascii") if IDENTIFIER.fullmatch(cstring) else None}


def inspect_script(source: bytes, *, source_sha256: str, record_sha256: str,
                   offset: int = 0, length: int | None = None, limits: Limits | None = None) -> dict:
    """Inspect one exact selected record/range. No instruction or native call runs.

    Header/field counters are admitted before loops or allocations. Engineering
    caps are not alleged game-format limits. Unknown opcode/value layouts stop at
    that field and preserve the remainder's identity; no guessed skip is used.
    ``complete`` means only that the admitted wire layout consumed the range.
    Invalid event PCs, duplicate names or bad event-symbol references are reported
    as findings, not silently repaired or presented as executable validity.
    """
    limits = Limits() if limits is None else limits
    if type(source) is not bytes or not isinstance(limits, Limits):
        raise TypeError("immutable source bytes and Limits required")
    if len(source) > limits.source_bytes:
        raise InspectionError("source-byte-limit")
    if not isinstance(source_sha256, str) or not SHA.fullmatch(source_sha256) or hashlib.sha256(source).hexdigest() != source_sha256:
        raise InspectionError("source-identity-mismatch")
    if type(offset) is not int or offset < 0 or offset > len(source):
        raise InspectionError("invalid-record-offset")
    length = len(source)-offset if length is None else length
    if type(length) is not int or not 0 < length <= limits.record_bytes or length > len(source)-offset:
        raise InspectionError("record-range-or-byte-limit")
    end = offset + length
    record = _range(source, offset, end)
    if not isinstance(record_sha256, str) or not SHA.fullmatch(record_sha256) or record["sha256"] != record_sha256:
        raise InspectionError("record-identity-mismatch")
    result = {"schema": SCHEMA, "sourceIdentity": {"size": len(source), "sha256": source_sha256},
              "recordIdentity": record, "status": "malformed", "findings": [], "symbols": [], "eventFunctions": [],
              "eventEntryPcs": [], "opcodeCounts": {}, "unknownFields": [],
              "limits": dict(limits.__dict__),
              "claimBoundary": "Stored structure only; no script execution, native effects, reachability, full world/campaign coverage or editor-writing support."}
    reader = _Reader(source, offset, end, limits)
    try:
        instruction_count = reader.count(limits.instructions, 8, "instruction-count")
        result["declaredInstructionCount"] = instruction_count
        opcodes = Counter()
        result["opcodeCounts"] = opcodes
        result["supportedInstructionCount"] = 0
        for _ in range(instruction_count):
            at = reader.position
            opcode = reader.i32()
            reader.take(4)  # Every known Spawn case reads one attribute word; not emitted here.
            if not 0 <= opcode <= 26:
                raise _Stop("unsupported", "unknown-opcode-layout", at)
            opcodes[str(opcode)] += 1
            result["supportedInstructionCount"] += 1
        result["opcodeCounts"] = dict(sorted(opcodes.items(), key=lambda item: int(item[0])))
        for event in range(EVENT_COUNT):
            at = reader.position
            pc = reader.i32()
            result["eventEntryPcs"].append({"eventOrdinal": event, "entryPc": pc, "offset": at})
            if pc != -1 and not 0 <= pc < instruction_count:
                result["findings"].append({"code": "event-pc-outside-instructions", "eventOrdinal": event, "entryPc": pc})
        symbol_count = reader.count(limits.symbols, 20, "symbol-count")
        names = {}
        for ordinal in range(symbol_count):
            at = reader.position
            name_offset, name = reader.string()
            name_metadata = _string_metadata(name)
            value_at = reader.position
            value_type = reader.i32()
            if value_type not in VALUE_TYPES:
                raise _Stop("unsupported", "unknown-symbol-value-layout", value_at)
            value = {"storedType": value_type, "typeName": VALUE_TYPES[value_type]}
            if value_type == 3:
                string_offset, text = reader.string()
                value.update(storedStringIdentity=_range(source, string_offset, reader.position))
            elif value_type:
                reader.take(12 if value_type == 6 else 4)
            value["storedRange"] = _range(source, value_at, reader.position)
            compiler_type, stored_index = reader.i32(), reader.i32()
            opaque_at = reader.position
            reader.take(4)
            row = {"ordinal": ordinal, "recordRange": _range(source, at, reader.position),
                   "nameOffset": name_offset, "name": name_metadata, "value": value,
                   "compilerTypeRaw": compiler_type, "storedIndexRaw": stored_index,
                   "unknownField": _range(source, opaque_at, reader.position)}
            result["symbols"].append(row)
            prior = names.setdefault(name_metadata["cstringSha256"], ordinal)
            if prior != ordinal:
                result["findings"].append({"code": "duplicate-cstring-symbol-name", "symbolOrdinal": ordinal, "firstOrdinal": prior})
        result["nextSymbolIndexRaw"] = reader.i32()
        functions = reader.count(limits.event_functions, 8, "event-function-count")
        parameters = 0
        for ordinal in range(functions):
            at = reader.position
            pc = reader.i32()
            count = reader.count(limits.parameters_per_function, 4, "event-parameter-count")
            parameters += count
            if parameters > limits.total_parameters:
                raise _Stop("unsupported", "profile-limit-total-event-parameters", reader.position)
            references = []
            for _ in range(count):
                symbol = reader.i32()
                ref = {"symbolOrdinal": symbol, "status": "invalid-reference"}
                if 0 <= symbol < len(result["symbols"]):
                    value = result["symbols"][symbol]["value"]
                    ref["status"] = "resolved-string" if value["storedType"] == 3 else "non-string-value"
                    if value["storedType"] == 3:
                        ref["eventNameIdentity"] = value["storedStringIdentity"]
                if ref["status"] != "resolved-string":
                    result["findings"].append({"code": "event-name-reference-" + ref["status"], "eventFunctionOrdinal": ordinal, "symbolOrdinal": symbol})
                references.append(ref)
            if not 0 <= pc < instruction_count:
                result["findings"].append({"code": "event-function-pc-outside-instructions", "eventFunctionOrdinal": ordinal, "entryPc": pc})
            result["eventFunctions"].append({"ordinal": ordinal, "entryPc": pc, "parameterReferences": references,
                                              "recordRange": _range(source, at, reader.position)})
        opaque_at = reader.position
        reader.take(8)  # mUnknown60 then mUnknown5c; no semantics inferred here.
        result["unknownFields"].append({"kind": "two-trailing-stored-words", **_range(source, opaque_at, reader.position)})
        result["status"] = "complete" if reader.position == end else "trailing-data"
        if reader.position != end:
            result["findings"].append({"code": "unparsed-trailing-data"})
    except _Stop as error:
        result["status"] = error.status
        result["findings"].append({"code": error.code, "offset": error.offset})
        reader.position = error.offset
    result["parsedRange"] = _range(source, offset, reader.position)
    result["unparsedRange"] = _range(source, reader.position, end)
    return result


def _open_nofollow(path):
    current = os.open(path.anchor, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
    try:
        for index, name in enumerate(path.parts[1:]):
            flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK
            if index < len(path.parts)-2:
                flags |= os.O_DIRECTORY
            child = os.open(name, flags, dir_fd=current)
            os.close(current)
            current = child
        return current
    except BaseException:
        os.close(current)
        raise


def inspect_file(path: Path, *, source_sha256: str, record_sha256: str, offset=0, length=None, limits=None) -> dict:
    """Read one bounded regular file once; retain the FD through parsing and path revalidation."""
    limits = Limits() if limits is None else limits
    if not isinstance(limits, Limits):
        raise TypeError("Limits required")
    if not all(isinstance(value,str) and SHA.fullmatch(value) for value in (source_sha256,record_sha256)):
        raise InspectionError("explicit-source-and-record-sha256-required")
    if not hasattr(os, "O_NOFOLLOW"):
        raise InspectionError("descriptor-safe-file-reading-unavailable; use immutable-bytes API")
    path = Path(os.path.abspath(path))
    stamp = lambda s: (s.st_dev, s.st_ino, s.st_mode, s.st_size, s.st_mtime_ns, s.st_ctime_ns, s.st_nlink)
    fd = _open_nofollow(path)
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_size > limits.source_bytes:
            raise InspectionError("input-type-or-source-byte-limit")
        chunks, size = [], 0
        while True:
            chunk = os.read(fd, min(1024*1024, limits.source_bytes-size+1))
            if not chunk:
                break
            size += len(chunk)
            if size > limits.source_bytes:
                raise InspectionError("source-grew-past-byte-limit")
            chunks.append(chunk)
        result = inspect_script(b"".join(chunks), source_sha256=source_sha256, record_sha256=record_sha256,
                                offset=offset, length=length, limits=limits)
        if size != before.st_size or stamp(before) != stamp(os.fstat(fd)):
            raise InspectionError("input-changed-during-inspection")
        check = _open_nofollow(path)
        try:
            if stamp(before) != stamp(os.fstat(check)):
                raise InspectionError("input-path-replaced-during-inspection")
        finally:
            os.close(check)
        return result
    finally:
        os.close(fd)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--record-sha256", required=True)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--length", type=int)
    args = parser.parse_args(argv)
    try:
        result = inspect_file(args.source, source_sha256=args.source_sha256, record_sha256=args.record_sha256,
                              offset=args.offset, length=args.length)
    except (InspectionError, OSError) as error:
        print("Mission-script inspection refused: " + str(error), file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0 if result["status"] == "complete" else 1


if __name__ == "__main__":
    sys.exit(main())
