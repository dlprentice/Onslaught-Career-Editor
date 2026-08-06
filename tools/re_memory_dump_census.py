#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Build and replay a strict census of the preserved Level 100 memory dumps.

The retail ``DumpMem`` command emits an ASCII structural inventory, not raw
allocation payloads.  This owner parses the exact preserved format, compares
records by reported address, joins the adjacent ``MemStats`` observation, and
tests the preregistered shipped-source-path transport hypothesis without using
decimal substrings as evidence.

The command is intentionally specimen/pilot specific.  Every input is supplied
independently on the command line but must match the hashes pinned below.  A
published bundle contains a frozen copy of this owner and can be replayed only
against those five independently supplied inputs.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from dataclasses import dataclass
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import struct
import sys
import tempfile
from typing import Iterable, Mapping, Sequence


SCHEMA = "bea.re.memory-dump-census.v1"
READY_SCHEMA = "bea.re.memory-dump-census-ready.v1"
STATUS = "READY"
EXPECTED_MEMORY_TYPES = 129
EXPECTED_HEAPS = 4
EXPECTED_SPECIMEN_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)

PINNED_INPUT_SHA256 = {
    "beforeDump": "b21875bd1886d9e1341efcde4adf3d96d9f7d42591168f7512e264d24334aa95",
    "afterDump": "6f0c8ba4dc1dcf0b8ad703e8c3effab77492783ba802e67a73e4552faadd2067",
    "memStats": "783cab5a1b0f17a9cbb820fc3b2a84927e3249d711d44dc7638ee50865b0e479",
    "sourcePaths": "9b6f198e9380346c31ee2eb6ae305f9e91b4cc297421c01359ad6a59d0b29ff3",
    "sourceReady": "63099dbf88d031bcbc186303627f6692e157cc80a270670018a5ed68744ff2b4",
}

PINNED_OUTCOMES = {
    "beforeBlocks": 28097,
    "afterBlocks": 28371,
    "addedAddresses": 274,
    "removedAddresses": 0,
    "changedAddresses": 4,
    "unchangedAddresses": 28093,
    "sourceRows": 166,
    "canonicalSourcePaths": 162,
    "littleEndianVaHits": 0,
    "exactDecimalLineHits": 0,
    "fullPathTextHits": 0,
}

OWNER_NAME = "memory-dump-census-owner.py"
OUTPUT_NAMES = (
    OWNER_NAME,
    "memory-types.tsv",
    "size-cohorts.tsv",
    "address-delta.tsv",
    "memstats-join.tsv",
    "source-path-scan.tsv",
    "census-summary.json",
)

TYPE_COLUMNS = (
    "snapshot", "memoryTypeIndex", "memoryTypeName", "blockCount",
    "payloadBytes", "accountedBytes", "reportedDeltaBytes",
    "reportedFlagZeroBlockCount", "reportedFlagZeroPayloadBytes",
    "reportedFlagZeroAccountedBytes", "reportedFlagNonzeroBlockCount",
    "reportedFlagNonzeroPayloadBytes", "reportedFlagNonzeroAccountedBytes",
)
COHORT_COLUMNS = (
    "snapshot", "heapIndex", "heapName", "memoryTypeIndex",
    "memoryTypeName", "recordState", "payloadBytes", "accountedBytes",
    "reportedDeltaBytes", "reportedFlag", "reportedLabel", "reportedLine",
    "blockCount", "minAddressDecimal", "minAddressHex",
    "maxAddressDecimal", "maxAddressHex",
)
DELTA_COLUMNS = (
    "addressDecimal", "addressHex", "disposition", "changedFields",
    "beforeHeapIndex", "beforeBlockSerial", "beforeRecordState",
    "beforePayloadBytes", "beforeAccountedBytes", "beforeMemoryTypeIndex",
    "beforeMemoryTypeName", "beforeReportedFlag", "beforeReportedLabel",
    "beforeReportedLine", "afterHeapIndex", "afterBlockSerial",
    "afterRecordState", "afterPayloadBytes", "afterAccountedBytes",
    "afterMemoryTypeIndex", "afterMemoryTypeName", "afterReportedFlag",
    "afterReportedLabel", "afterReportedLine",
)
MEMSTATS_COLUMNS = (
    "memoryTypeIndex", "memoryTypeName", "memStatsBytes",
    "memStatsBlockCount", "beforeBlockCount", "beforePayloadBytes",
    "beforeAccountedBytes", "beforeReportedFlagZeroBlockCount",
    "beforeReportedFlagZeroPayloadBytes",
    "beforeReportedFlagZeroAccountedBytes", "beforeJoinDisposition",
    "afterBlockCount", "afterPayloadBytes", "afterAccountedBytes",
    "afterReportedFlagZeroBlockCount", "afterReportedFlagZeroPayloadBytes",
    "afterReportedFlagZeroAccountedBytes", "afterJoinDisposition",
)
SOURCE_SCAN_COLUMNS = (
    "pathStringKey", "stringVa", "stringVaDecimal", "rawPath",
    "canonicalPathKey", "beforeLittleEndianVaHits",
    "afterLittleEndianVaHits", "beforeExactDecimalLineHits",
    "afterExactDecimalLineHits", "beforeFullPathTextHits",
    "afterFullPathTextHits", "totalLittleEndianVaHits",
    "totalExactDecimalLineHits", "totalFullPathTextHits",
)
SOURCE_PATH_COLUMNS = (
    "pathStringKey", "stringVa", "stringRva", "fileOffset", "sectionName",
    "rawPath", "canonicalPathKey", "canonicalWindowsPath",
    "canonicalRelativePath", "pathKind", "extension",
    "canonicalAliasCount", "pushSiteCount", "primaryPlateSiteCount",
    "unwindFreePlateSiteCount", "mappedFunctionSiteCount", "residualSiteCount",
)

UNSIGNED_DECIMAL = re.compile(r"(?:0|[1-9][0-9]*)\Z")
MEMSTATS_TOTAL = re.compile(r"(Used|Free|Total): ([0-9]+) bytes\Z")
MEMSTATS_ROW = re.compile(
    r"(.+?\S) +: +([0-9]+) bytes +: +([0-9]+) blocks\Z"
)
HEX_VA = re.compile(r"0x[0-9a-f]{8}\Z")


class CensusError(ValueError):
    """An input or publication violates the memory-dump proof contract."""


@dataclass(frozen=True)
class DumpBlock:
    heap_index: int
    heap_name: str
    block_serial: int
    record_state: int
    payload_bytes: int
    accounted_bytes: int
    address: int
    memory_type_index: int
    reported_flag: int
    reported_label: str
    reported_line: int

    def comparison_values(self) -> tuple[object, ...]:
        """Fields compared at a stable address; emitted serial is navigation only."""
        return (
            self.heap_index,
            self.record_state,
            self.payload_bytes,
            self.accounted_bytes,
            self.memory_type_index,
            self.reported_flag,
            self.reported_label,
            self.reported_line,
        )


@dataclass(frozen=True)
class DumpHeap:
    index: int
    name: str
    reported_size: int
    blocks: tuple[DumpBlock, ...]


@dataclass(frozen=True)
class MemoryDump:
    trace_name: str
    memory_types: tuple[str, ...]
    heaps: tuple[DumpHeap, ...]
    num_tags: int
    blocks: tuple[DumpBlock, ...]


@dataclass(frozen=True)
class MemStatsRow:
    memory_type_index: int
    memory_type_name: str
    reported_bytes: int
    reported_blocks: int


@dataclass(frozen=True)
class MemStats:
    used_bytes: int
    free_bytes: int
    total_bytes: int
    rows: tuple[MemStatsRow, ...]


@dataclass(frozen=True)
class SourcePath:
    key: str
    va: int
    va_text: str
    raw_path: str
    canonical_key: str


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    ).encode("utf-8")


def render_tsv(columns: Sequence[str], rows: Iterable[Mapping[str, object]]) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(
        buffer,
        fieldnames=list(columns),
        delimiter="\t",
        lineterminator="\n",
        extrasaction="raise",
    )
    writer.writeheader()
    for row in rows:
        rendered = {column: row.get(column, "") for column in columns}
        for column, value in rendered.items():
            if "\t" in str(value) or "\r" in str(value) or "\n" in str(value):
                raise CensusError(f"TSV cell contains a forbidden control: {column}")
        writer.writerow(rendered)
    return buffer.getvalue().encode("utf-8")


def parse_json_strict(data: bytes, role: str) -> object:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise CensusError(f"{role} is not UTF-8: {error}") from error

    def no_duplicates(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise CensusError(f"{role} contains duplicate JSON key: {key}")
            result[key] = value
        return result

    try:
        return json.loads(text, object_pairs_hook=no_duplicates)
    except json.JSONDecodeError as error:
        raise CensusError(f"invalid {role}: {error}") from error


def read_plain_file(path: Path, role: str) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise CensusError(f"{role} is not a plain file: {path}")
    return path.read_bytes()


def strict_lf_ascii_lines(data: bytes, role: str) -> list[str]:
    if not data or not data.endswith(b"\n"):
        raise CensusError(f"{role} must be nonempty and end with LF")
    if b"\r" in data:
        raise CensusError(f"{role} contains CR; exact format is LF-only")
    try:
        text = data.decode("ascii")
    except UnicodeDecodeError as error:
        raise CensusError(f"{role} is not strict ASCII: {error}") from error
    return text[:-1].split("\n")


def parse_unsigned(text: str, role: str, maximum: int | None = None) -> int:
    if not UNSIGNED_DECIMAL.fullmatch(text):
        raise CensusError(f"{role} is not canonical unsigned decimal: {text!r}")
    value = int(text)
    if maximum is not None and value > maximum:
        raise CensusError(f"{role} exceeds {maximum}: {value}")
    return value


class LineCursor:
    def __init__(self, lines: Sequence[str], role: str):
        self.lines = lines
        self.role = role
        self.index = 0

    def take(self) -> str:
        if self.index >= len(self.lines):
            raise CensusError(f"{self.role} ended at line {self.index + 1}")
        value = self.lines[self.index]
        self.index += 1
        return value

    def expect(self, expected: str) -> None:
        actual = self.take()
        if actual != expected:
            raise CensusError(
                f"{self.role} line {self.index}: expected {expected!r}, got {actual!r}"
            )

    def finish(self) -> None:
        if self.index != len(self.lines):
            raise CensusError(
                f"{self.role} has {len(self.lines) - self.index} trailing lines"
            )


def parse_dump(data: bytes, role: str) -> MemoryDump:
    lines = strict_lf_ascii_lines(data, role)
    cursor = LineCursor(lines, role)
    cursor.expect("#Trace name")
    trace_name = cursor.take()
    if not trace_name:
        raise CensusError(f"{role} has an empty trace name")
    cursor.expect("#MemTypes")
    type_count = parse_unsigned(cursor.take(), f"{role} #MemTypes")
    if type_count != EXPECTED_MEMORY_TYPES:
        raise CensusError(
            f"{role} has {type_count} memory types, expected {EXPECTED_MEMORY_TYPES}"
        )
    memory_types = tuple(cursor.take() for _ in range(type_count))
    if any(not name for name in memory_types) or len(set(memory_types)) != type_count:
        raise CensusError(f"{role} memory type names must be nonempty and unique")
    cursor.expect("#Heaps")
    heap_count = parse_unsigned(cursor.take(), f"{role} #Heaps")
    if heap_count != EXPECTED_HEAPS:
        raise CensusError(f"{role} has {heap_count} heaps, expected {EXPECTED_HEAPS}")

    heaps: list[DumpHeap] = []
    all_blocks: list[DumpBlock] = []
    addresses: set[int] = set()
    for heap_index in range(heap_count):
        cursor.expect(f"# Heap {heap_index}")
        heap_name = cursor.take()
        if not heap_name:
            raise CensusError(f"{role} heap {heap_index} has an empty name")
        cursor.expect("# Size")
        reported_size = parse_unsigned(
            cursor.take(), f"{role} heap {heap_index} # Size"
        )
        cursor.expect("# NumBlocks")
        block_count = parse_unsigned(
            cursor.take(), f"{role} heap {heap_index} # NumBlocks"
        )
        blocks: list[DumpBlock] = []
        for offset in range(block_count):
            block_serial = block_count + offset
            cursor.expect(f"# Heap {heap_index} Block {block_serial}")
            record_state = parse_unsigned(
                cursor.take(), f"{role} block {block_serial} record state"
            )
            payload_bytes = parse_unsigned(
                cursor.take(), f"{role} block {block_serial} payload"
            )
            accounted_bytes = parse_unsigned(
                cursor.take(), f"{role} block {block_serial} accounted"
            )
            address = parse_unsigned(
                cursor.take(), f"{role} block {block_serial} address", 0xFFFFFFFF
            )
            memory_type_index = parse_unsigned(
                cursor.take(), f"{role} block {block_serial} memory type"
            )
            if memory_type_index >= type_count:
                raise CensusError(
                    f"{role} block {block_serial} memory type is out of range: "
                    f"{memory_type_index}"
                )
            reported_flag = parse_unsigned(
                cursor.take(), f"{role} block {block_serial} reported flag"
            )
            reported_label = cursor.take()
            if not reported_label:
                raise CensusError(f"{role} block {block_serial} has an empty label")
            reported_line = parse_unsigned(
                cursor.take(), f"{role} block {block_serial} reported line"
            )
            if accounted_bytes < payload_bytes:
                raise CensusError(
                    f"{role} block {block_serial} accounted bytes are below payload"
                )
            if address in addresses:
                raise CensusError(f"{role} repeats block address {address}")
            addresses.add(address)
            block = DumpBlock(
                heap_index,
                heap_name,
                block_serial,
                record_state,
                payload_bytes,
                accounted_bytes,
                address,
                memory_type_index,
                reported_flag,
                reported_label,
                reported_line,
            )
            blocks.append(block)
            all_blocks.append(block)
        heaps.append(DumpHeap(heap_index, heap_name, reported_size, tuple(blocks)))

    cursor.expect("# NumTags")
    num_tags = parse_unsigned(cursor.take(), f"{role} # NumTags")
    if num_tags != 0:
        raise CensusError(
            f"{role} has {num_tags} tags; the preserved exact tag grammar is zero-tag"
        )
    cursor.finish()
    return MemoryDump(
        trace_name,
        memory_types,
        tuple(heaps),
        num_tags,
        tuple(all_blocks),
    )


def parse_memstats(data: bytes, memory_types: Sequence[str], role: str) -> MemStats:
    lines = strict_lf_ascii_lines(data, role)
    if len(lines) != 4 + len(memory_types):
        raise CensusError(
            f"{role} has {len(lines)} lines, expected {4 + len(memory_types)}"
        )
    totals: dict[str, int] = {}
    for index, key in enumerate(("Used", "Free", "Total")):
        match = MEMSTATS_TOTAL.fullmatch(lines[index])
        if match is None or match.group(1) != key:
            raise CensusError(f"{role} line {index + 1} is not exact {key} total")
        totals[key] = int(match.group(2))
    if lines[3] != "":
        raise CensusError(f"{role} line 4 must be blank")
    by_name = {name: index for index, name in enumerate(memory_types)}
    rows_by_index: dict[int, MemStatsRow] = {}
    for row_offset, line in enumerate(lines[4:]):
        line_number = 5 + row_offset
        match = MEMSTATS_ROW.fullmatch(line)
        if match is None:
            raise CensusError(f"{role} line {line_number} is not a MemStats row")
        name = match.group(1)
        if name not in by_name:
            raise CensusError(f"{role} line {line_number} has unknown type {name!r}")
        type_index = by_name[name]
        if type_index in rows_by_index:
            raise CensusError(f"{role} repeats memory type {name!r}")
        rows_by_index[type_index] = MemStatsRow(
            type_index, name, int(match.group(2)), int(match.group(3))
        )
    if len(rows_by_index) != len(memory_types):
        missing = [
            name for index, name in enumerate(memory_types)
            if index not in rows_by_index
        ]
        raise CensusError(f"{role} is missing memory types: {missing}")
    rows = [rows_by_index[index] for index in range(len(memory_types))]
    if totals["Used"] + totals["Free"] != totals["Total"]:
        raise CensusError(f"{role} Used + Free does not equal Total")
    if sum(row.reported_bytes for row in rows) != totals["Used"]:
        raise CensusError(f"{role} category bytes do not sum to Used")
    return MemStats(totals["Used"], totals["Free"], totals["Total"], tuple(rows))


def validate_source_ready(
    ready_data: bytes, source_path_data: bytes, role: str
) -> dict[str, object]:
    parsed = parse_json_strict(ready_data, role)
    if not isinstance(parsed, dict):
        raise CensusError(f"{role} root must be an object")
    if parsed.get("schema") != "bea.re.source-unit-census.v1" or parsed.get("status") != "READY":
        raise CensusError(f"{role} is not a READY source-unit census")
    specimen = parsed.get("specimen")
    if not isinstance(specimen, dict) or specimen.get("sha256") != EXPECTED_SPECIMEN_SHA256:
        raise CensusError(f"{role} does not bind the pristine specimen")
    outputs = parsed.get("outputs")
    if not isinstance(outputs, dict):
        raise CensusError(f"{role} outputs are missing")
    source_entry = outputs.get("source-path-strings.tsv")
    if not isinstance(source_entry, dict):
        raise CensusError(f"{role} does not authenticate source-path-strings.tsv")
    if source_entry.get("bytes") != len(source_path_data) or source_entry.get("sha256") != sha256_bytes(source_path_data):
        raise CensusError(f"{role} source-path-strings.tsv attestation differs")
    return parsed


def parse_source_paths(data: bytes, role: str) -> tuple[SourcePath, ...]:
    if not data or not data.endswith(b"\n") or b"\r" in data:
        raise CensusError(f"{role} must be nonempty canonical LF TSV")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise CensusError(f"{role} is not UTF-8: {error}") from error
    reader = csv.DictReader(io.StringIO(text, newline=""), delimiter="\t")
    if tuple(reader.fieldnames or ()) != SOURCE_PATH_COLUMNS:
        raise CensusError(f"{role} header differs from source-unit schema")
    paths: list[SourcePath] = []
    keys: set[str] = set()
    vas: set[int] = set()
    for row_number, row in enumerate(reader, start=2):
        if None in row or any(value is None for value in row.values()):
            raise CensusError(f"{role} row {row_number} has a shifted field count")
        va_text = row["stringVa"]
        if not HEX_VA.fullmatch(va_text):
            raise CensusError(f"{role} row {row_number} has noncanonical stringVa")
        key = row["pathStringKey"]
        va = int(va_text, 16)
        raw_path = row["rawPath"]
        canonical_key = row["canonicalPathKey"]
        if not key or not raw_path or not canonical_key:
            raise CensusError(f"{role} row {row_number} has an empty identity field")
        if key in keys or va in vas:
            raise CensusError(f"{role} row {row_number} repeats key or VA")
        try:
            raw_path.encode("ascii")
        except UnicodeEncodeError as error:
            raise CensusError(f"{role} row {row_number} rawPath is not ASCII") from error
        keys.add(key)
        vas.add(va)
        paths.append(SourcePath(key, va, va_text, raw_path, canonical_key))
    if not paths:
        raise CensusError(f"{role} has no source paths")
    return tuple(paths)


def count_overlapping(haystack: bytes, needle: bytes) -> int:
    if not needle:
        raise CensusError("empty scan needle")
    count = 0
    start = 0
    while True:
        found = haystack.find(needle, start)
        if found < 0:
            return count
        count += 1
        start = found + 1


def aggregate_type(blocks: Iterable[DumpBlock], type_index: int) -> dict[str, int]:
    selected = [block for block in blocks if block.memory_type_index == type_index]
    flag_zero = [block for block in selected if block.reported_flag == 0]
    flag_nonzero = [block for block in selected if block.reported_flag != 0]
    return {
        "blockCount": len(selected),
        "payloadBytes": sum(block.payload_bytes for block in selected),
        "accountedBytes": sum(block.accounted_bytes for block in selected),
        "reportedDeltaBytes": sum(block.accounted_bytes - block.payload_bytes for block in selected),
        "reportedFlagZeroBlockCount": len(flag_zero),
        "reportedFlagZeroPayloadBytes": sum(block.payload_bytes for block in flag_zero),
        "reportedFlagZeroAccountedBytes": sum(block.accounted_bytes for block in flag_zero),
        "reportedFlagNonzeroBlockCount": len(flag_nonzero),
        "reportedFlagNonzeroPayloadBytes": sum(block.payload_bytes for block in flag_nonzero),
        "reportedFlagNonzeroAccountedBytes": sum(block.accounted_bytes for block in flag_nonzero),
    }


def join_disposition(stats_row: MemStatsRow, metrics: Mapping[str, int]) -> str:
    if (
        stats_row.reported_blocks == metrics["reportedFlagZeroBlockCount"]
        and stats_row.reported_bytes == metrics["reportedFlagZeroAccountedBytes"]
    ):
        return "EXACT_REPORTED_FLAG_ZERO"
    if (
        stats_row.reported_blocks == 0
        and stats_row.reported_bytes == 0
        and metrics["blockCount"] > 0
    ):
        return "MEMSTATS_ZERO_DUMP_NONZERO"
    return "DIVERGENT"


def address_row(
    address: int,
    disposition: str,
    changed_fields: str,
    before: DumpBlock | None,
    after: DumpBlock | None,
    memory_types: Sequence[str],
) -> dict[str, object]:
    row: dict[str, object] = {
        "addressDecimal": address,
        "addressHex": f"0x{address:08x}",
        "disposition": disposition,
        "changedFields": changed_fields,
    }
    for prefix, block in (("before", before), ("after", after)):
        if block is None:
            for field in (
                "HeapIndex", "BlockSerial", "RecordState", "PayloadBytes",
                "AccountedBytes", "MemoryTypeIndex", "MemoryTypeName",
                "ReportedFlag", "ReportedLabel", "ReportedLine",
            ):
                row[prefix + field] = ""
            continue
        row.update({
            prefix + "HeapIndex": block.heap_index,
            prefix + "BlockSerial": block.block_serial,
            prefix + "RecordState": block.record_state,
            prefix + "PayloadBytes": block.payload_bytes,
            prefix + "AccountedBytes": block.accounted_bytes,
            prefix + "MemoryTypeIndex": block.memory_type_index,
            prefix + "MemoryTypeName": memory_types[block.memory_type_index],
            prefix + "ReportedFlag": block.reported_flag,
            prefix + "ReportedLabel": block.reported_label,
            prefix + "ReportedLine": block.reported_line,
        })
    return row


def derive(
    before_data: bytes,
    after_data: bytes,
    memstats_data: bytes,
    source_path_data: bytes,
    source_ready_data: bytes,
    *,
    input_pins: Mapping[str, str],
    expected_outcomes: Mapping[str, int] | None,
) -> tuple[dict[str, bytes], dict[str, object]]:
    supplied = {
        "beforeDump": before_data,
        "afterDump": after_data,
        "memStats": memstats_data,
        "sourcePaths": source_path_data,
        "sourceReady": source_ready_data,
    }
    if set(input_pins) != set(supplied):
        raise CensusError("input pin roles differ from the five-input contract")
    for role, data in supplied.items():
        actual = sha256_bytes(data)
        if actual != input_pins[role]:
            raise CensusError(
                f"{role} SHA-256 differs: expected {input_pins[role]}, got {actual}"
            )

    source_ready = validate_source_ready(source_ready_data, source_path_data, "sourceReady")
    before = parse_dump(before_data, "beforeDump")
    after = parse_dump(after_data, "afterDump")
    if before.memory_types != after.memory_types:
        raise CensusError("before/after memory type tables differ")
    before_heap_identity = tuple((heap.index, heap.name, heap.reported_size) for heap in before.heaps)
    after_heap_identity = tuple((heap.index, heap.name, heap.reported_size) for heap in after.heaps)
    if before_heap_identity != after_heap_identity:
        raise CensusError("before/after heap identity or reported size differs")
    for role, dump in (("beforeDump", before), ("afterDump", after)):
        bad = [
            block for block in dump.blocks
            if block.accounted_bytes - block.payload_bytes != 16
        ]
        if bad:
            first = bad[0]
            raise CensusError(
                f"{role} does not have reported 16-byte delta at address {first.address}"
            )

    memstats = parse_memstats(memstats_data, before.memory_types, "memStats")
    source_paths = parse_source_paths(source_path_data, "sourcePaths")

    type_rows: list[dict[str, object]] = []
    metrics_by_snapshot: dict[str, list[dict[str, int]]] = {}
    for snapshot, dump in (("BEFORE", before), ("AFTER", after)):
        metrics_list: list[dict[str, int]] = []
        for type_index, type_name in enumerate(dump.memory_types):
            metrics = aggregate_type(dump.blocks, type_index)
            metrics_list.append(metrics)
            type_rows.append({
                "snapshot": snapshot,
                "memoryTypeIndex": type_index,
                "memoryTypeName": type_name,
                **metrics,
            })
        metrics_by_snapshot[snapshot] = metrics_list

    cohorts: defaultdict[tuple[object, ...], list[int]] = defaultdict(list)
    for snapshot, dump in (("BEFORE", before), ("AFTER", after)):
        for block in dump.blocks:
            key = (
                snapshot,
                block.heap_index,
                block.heap_name,
                block.memory_type_index,
                dump.memory_types[block.memory_type_index],
                block.record_state,
                block.payload_bytes,
                block.accounted_bytes,
                block.accounted_bytes - block.payload_bytes,
                block.reported_flag,
                block.reported_label,
                block.reported_line,
            )
            cohorts[key].append(block.address)
    cohort_rows: list[dict[str, object]] = []
    for key in sorted(cohorts, key=lambda value: (value[0] != "BEFORE", *value[1:])):
        addresses = cohorts[key]
        cohort_rows.append({
            **dict(zip(COHORT_COLUMNS[:12], key)),
            "blockCount": len(addresses),
            "minAddressDecimal": min(addresses),
            "minAddressHex": f"0x{min(addresses):08x}",
            "maxAddressDecimal": max(addresses),
            "maxAddressHex": f"0x{max(addresses):08x}",
        })

    before_by_address = {block.address: block for block in before.blocks}
    after_by_address = {block.address: block for block in after.blocks}
    comparison_fields = (
        "heapIndex", "recordState", "payloadBytes", "accountedBytes",
        "memoryTypeIndex", "reportedFlag", "reportedLabel", "reportedLine",
    )
    delta_rows: list[dict[str, object]] = []
    disposition_counts: Counter[str] = Counter()
    for address in sorted(before_by_address.keys() | after_by_address.keys()):
        before_block = before_by_address.get(address)
        after_block = after_by_address.get(address)
        changed = ""
        if before_block is None:
            disposition = "ADDED"
        elif after_block is None:
            disposition = "REMOVED"
        elif before_block.comparison_values() == after_block.comparison_values():
            disposition = "UNCHANGED"
        else:
            disposition = "CHANGED"
            changed = ",".join(
                name for name, old, new in zip(
                    comparison_fields,
                    before_block.comparison_values(),
                    after_block.comparison_values(),
                ) if old != new
            )
        disposition_counts[disposition] += 1
        delta_rows.append(address_row(
            address,
            disposition,
            changed,
            before_block,
            after_block,
            before.memory_types,
        ))

    memstats_rows: list[dict[str, object]] = []
    before_join_counts: Counter[str] = Counter()
    after_join_counts: Counter[str] = Counter()
    for stats_row in memstats.rows:
        before_metrics = metrics_by_snapshot["BEFORE"][stats_row.memory_type_index]
        after_metrics = metrics_by_snapshot["AFTER"][stats_row.memory_type_index]
        before_disposition = join_disposition(stats_row, before_metrics)
        after_disposition = join_disposition(stats_row, after_metrics)
        before_join_counts[before_disposition] += 1
        after_join_counts[after_disposition] += 1
        memstats_rows.append({
            "memoryTypeIndex": stats_row.memory_type_index,
            "memoryTypeName": stats_row.memory_type_name,
            "memStatsBytes": stats_row.reported_bytes,
            "memStatsBlockCount": stats_row.reported_blocks,
            "beforeBlockCount": before_metrics["blockCount"],
            "beforePayloadBytes": before_metrics["payloadBytes"],
            "beforeAccountedBytes": before_metrics["accountedBytes"],
            "beforeReportedFlagZeroBlockCount": before_metrics["reportedFlagZeroBlockCount"],
            "beforeReportedFlagZeroPayloadBytes": before_metrics["reportedFlagZeroPayloadBytes"],
            "beforeReportedFlagZeroAccountedBytes": before_metrics["reportedFlagZeroAccountedBytes"],
            "beforeJoinDisposition": before_disposition,
            "afterBlockCount": after_metrics["blockCount"],
            "afterPayloadBytes": after_metrics["payloadBytes"],
            "afterAccountedBytes": after_metrics["accountedBytes"],
            "afterReportedFlagZeroBlockCount": after_metrics["reportedFlagZeroBlockCount"],
            "afterReportedFlagZeroPayloadBytes": after_metrics["reportedFlagZeroPayloadBytes"],
            "afterReportedFlagZeroAccountedBytes": after_metrics["reportedFlagZeroAccountedBytes"],
            "afterJoinDisposition": after_disposition,
        })

    before_lines = Counter(strict_lf_ascii_lines(before_data, "beforeDump"))
    after_lines = Counter(strict_lf_ascii_lines(after_data, "afterDump"))
    source_scan_rows: list[dict[str, object]] = []
    hit_totals = Counter()
    for source_path in source_paths:
        le_bytes = struct.pack("<I", source_path.va)
        decimal = str(source_path.va)
        path_bytes = source_path.raw_path.encode("ascii")
        before_le = count_overlapping(before_data, le_bytes)
        after_le = count_overlapping(after_data, le_bytes)
        before_decimal = before_lines[decimal]
        after_decimal = after_lines[decimal]
        before_path = count_overlapping(before_data, path_bytes)
        after_path = count_overlapping(after_data, path_bytes)
        hit_totals["littleEndianVaHits"] += before_le + after_le
        hit_totals["exactDecimalLineHits"] += before_decimal + after_decimal
        hit_totals["fullPathTextHits"] += before_path + after_path
        source_scan_rows.append({
            "pathStringKey": source_path.key,
            "stringVa": source_path.va_text,
            "stringVaDecimal": decimal,
            "rawPath": source_path.raw_path,
            "canonicalPathKey": source_path.canonical_key,
            "beforeLittleEndianVaHits": before_le,
            "afterLittleEndianVaHits": after_le,
            "beforeExactDecimalLineHits": before_decimal,
            "afterExactDecimalLineHits": after_decimal,
            "beforeFullPathTextHits": before_path,
            "afterFullPathTextHits": after_path,
            "totalLittleEndianVaHits": before_le + after_le,
            "totalExactDecimalLineHits": before_decimal + after_decimal,
            "totalFullPathTextHits": before_path + after_path,
        })

    canonical_source_paths = len({path.canonical_key for path in source_paths})
    observed = {
        "beforeBlocks": len(before.blocks),
        "afterBlocks": len(after.blocks),
        "addedAddresses": disposition_counts["ADDED"],
        "removedAddresses": disposition_counts["REMOVED"],
        "changedAddresses": disposition_counts["CHANGED"],
        "unchangedAddresses": disposition_counts["UNCHANGED"],
        "sourceRows": len(source_paths),
        "canonicalSourcePaths": canonical_source_paths,
        "littleEndianVaHits": hit_totals["littleEndianVaHits"],
        "exactDecimalLineHits": hit_totals["exactDecimalLineHits"],
        "fullPathTextHits": hit_totals["fullPathTextHits"],
    }
    if expected_outcomes is not None:
        for key, expected in expected_outcomes.items():
            if observed.get(key) != expected:
                raise CensusError(
                    f"pinned outcome {key} differs: expected {expected}, "
                    f"got {observed.get(key)}"
                )

    source_verdict = (
        "REFUTED_IN_TWO_BOUND_DUMPS"
        if all(hit_totals[key] == 0 for key in (
            "littleEndianVaHits", "exactDecimalLineHits", "fullPathTextHits"
        ))
        else "SURVIVED"
    )
    input_metadata = {
        role: {"bytes": len(data), "sha256": sha256_bytes(data)}
        for role, data in supplied.items()
    }
    input_metadata["sourceReady"].update({
        "schema": source_ready["schema"],
        "status": source_ready["status"],
    })
    summary = {
        "schema": SCHEMA,
        "status": STATUS,
        "inputs": input_metadata,
        "format": {
            "encoding": "ASCII",
            "lineEnding": "LF",
            "beforeTraceName": before.trace_name,
            "afterTraceName": after.trace_name,
            "memoryTypes": len(before.memory_types),
            "heaps": len(before.heaps),
            "fieldsPerBlock": 8,
            "blockFields": [
                "recordState", "payloadBytes", "accountedBytes", "address",
                "memoryTypeIndex", "reportedFlag", "reportedLabel", "reportedLine",
            ],
            "reportedDeltaBytes": {
                "definition": "accountedBytes-payloadBytes",
                "beforeDistinctValues": [16],
                "afterDistinctValues": [16],
                "beforeBlocksAt16": len(before.blocks),
                "afterBlocksAt16": len(after.blocks),
            },
            "numTagsBefore": before.num_tags,
            "numTagsAfter": after.num_tags,
            "heapIdentities": [
                {
                    "heapIndex": heap.index,
                    "heapName": heap.name,
                    "reportedSize": heap.reported_size,
                    "beforeBlocks": len(heap.blocks),
                    "afterBlocks": len(after.heaps[heap.index].blocks),
                }
                for heap in before.heaps
            ],
        },
        "counts": {
            **observed,
            "beforeTypesWithBlocks": sum(
                metrics["blockCount"] > 0 for metrics in metrics_by_snapshot["BEFORE"]
            ),
            "afterTypesWithBlocks": sum(
                metrics["blockCount"] > 0 for metrics in metrics_by_snapshot["AFTER"]
            ),
            "sizeCohorts": len(cohort_rows),
            "beforeMemStatsJoin": dict(sorted(before_join_counts.items())),
            "afterMemStatsJoin": dict(sorted(after_join_counts.items())),
        },
        "memStats": {
            "usedBytes": memstats.used_bytes,
            "freeBytes": memstats.free_bytes,
            "totalBytes": memstats.total_bytes,
            "categoryBytes": sum(row.reported_bytes for row in memstats.rows),
            "categoryBlocks": sum(row.reported_blocks for row in memstats.rows),
        },
        "sourcePathHypothesis": {
            "verdict": source_verdict,
            "littleEndianVaHits": hit_totals["littleEndianVaHits"],
            "exactDecimalLineHits": hit_totals["exactDecimalLineHits"],
            "fullPathTextHits": hit_totals["fullPathTextHits"],
            "decimalRule": "whole LF-delimited line equality only; substrings are never hits",
        },
        "claimBoundary": [
            "DumpMem serializes allocation metadata; these files do not contain allocation payload bytes.",
            "accountedBytes-payloadBytes is named reportedDeltaBytes. The observed value is 16 for every bound block, but it is not called a physical header without static allocator proof.",
            "reportedFlag, recordState, reportedLabel, and reportedLine preserve field position; their engine semantics are not inferred here.",
            "An address-delta row compares the eight reported fields plus heap identity at the same address; emitted block serials are navigation only.",
            "MemStats is joined as an adjacent observation. Equality to reportedFlag=0 is recorded, not assumed as a universal semantic rule.",
            "The source-plate transport hypothesis is refuted only for exact LE32 VAs, exact decimal lines, and exact full-path text in these two bound Level 100 dumps.",
            "The stronger positive is structural: heap, type, address, payload, accounted, reported-delta, and flag cohorts are exposed even for categories MemStats reports as zero.",
            "This census mutates neither the game nor Ghidra and authorizes no function naming or promotion.",
        ],
    }
    outputs = {
        "memory-types.tsv": render_tsv(TYPE_COLUMNS, type_rows),
        "size-cohorts.tsv": render_tsv(COHORT_COLUMNS, cohort_rows),
        "address-delta.tsv": render_tsv(DELTA_COLUMNS, delta_rows),
        "memstats-join.tsv": render_tsv(MEMSTATS_COLUMNS, memstats_rows),
        "source-path-scan.tsv": render_tsv(SOURCE_SCAN_COLUMNS, source_scan_rows),
        "census-summary.json": canonical_json(summary),
    }
    return outputs, summary


def expected_ready(
    owner: bytes,
    outputs: Mapping[str, bytes],
    summary: Mapping[str, object],
) -> dict[str, object]:
    published = {OWNER_NAME: owner, **outputs}
    return {
        "schema": READY_SCHEMA,
        "status": STATUS,
        "ownerSha256": sha256_bytes(owner),
        "censusSchema": summary["schema"],
        "inputs": summary["inputs"],
        "counts": summary["counts"],
        "sourcePathHypothesis": summary["sourcePathHypothesis"],
        "outputs": {
            name: {"bytes": len(data), "sha256": sha256_bytes(data)}
            for name, data in sorted(published.items())
        },
    }


def read_inputs(paths: Mapping[str, Path]) -> dict[str, bytes]:
    expected = set(PINNED_INPUT_SHA256)
    if set(paths) != expected:
        raise CensusError("exactly five independently supplied input roles are required")
    return {role: read_plain_file(path, role) for role, path in paths.items()}


def derive_from_paths(
    paths: Mapping[str, Path],
    *,
    input_pins: Mapping[str, str],
    expected_outcomes: Mapping[str, int] | None,
) -> tuple[dict[str, bytes], dict[str, object]]:
    data = read_inputs(paths)
    return derive(
        data["beforeDump"],
        data["afterDump"],
        data["memStats"],
        data["sourcePaths"],
        data["sourceReady"],
        input_pins=input_pins,
        expected_outcomes=expected_outcomes,
    )


def build_bundle(
    out: Path,
    owner_path: Path,
    input_paths: Mapping[str, Path],
    *,
    input_pins: Mapping[str, str] = PINNED_INPUT_SHA256,
    expected_outcomes: Mapping[str, int] | None = PINNED_OUTCOMES,
) -> dict[str, object]:
    if out.exists() or out.is_symlink():
        raise CensusError(f"output already exists: {out}")
    owner = read_plain_file(owner_path, "owner")
    outputs, summary = derive_from_paths(
        input_paths,
        input_pins=input_pins,
        expected_outcomes=expected_outcomes,
    )
    ready = expected_ready(owner, outputs, summary)
    out.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{out.name}-", dir=out.parent))
    try:
        (staging / OWNER_NAME).write_bytes(owner)
        for name, data in outputs.items():
            (staging / name).write_bytes(data)
        (staging / "READY.json").write_bytes(canonical_json(ready))
        os.replace(staging, out)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return ready


def verify_bundle(
    bundle: Path,
    owner_path: Path,
    input_paths: Mapping[str, Path],
    *,
    input_pins: Mapping[str, str] = PINNED_INPUT_SHA256,
    expected_outcomes: Mapping[str, int] | None = PINNED_OUTCOMES,
) -> dict[str, object]:
    if bundle.is_symlink() or not bundle.is_dir():
        raise CensusError(f"bundle is not a plain directory: {bundle}")
    expected_names = set(OUTPUT_NAMES) | {"READY.json"}
    members = list(bundle.iterdir())
    actual_names = {member.name for member in members}
    if actual_names != expected_names:
        raise CensusError(
            f"bundle members differ: missing={sorted(expected_names - actual_names)} "
            f"extra={sorted(actual_names - expected_names)}"
        )
    for member in members:
        if member.is_symlink() or not member.is_file():
            raise CensusError(f"bundle member is not a plain file: {member.name}")
    owner = read_plain_file(owner_path, "executed owner")
    if (bundle / OWNER_NAME).read_bytes() != owner:
        raise CensusError("frozen owner differs from the verifier being executed")
    ready_data = (bundle / "READY.json").read_bytes()
    published = parse_json_strict(ready_data, "READY.json")
    if not isinstance(published, dict) or canonical_json(published) != ready_data:
        raise CensusError("READY.json is not canonical JSON")
    outputs, summary = derive_from_paths(
        input_paths,
        input_pins=input_pins,
        expected_outcomes=expected_outcomes,
    )
    expected = expected_ready(owner, outputs, summary)
    if published != expected:
        raise CensusError("READY semantics differ from fresh canonical derivation")
    for name, data in {OWNER_NAME: owner, **outputs}.items():
        if (bundle / name).read_bytes() != data:
            raise CensusError(f"published output differs from fresh derivation: {name}")
    return expected


def cli_input_paths(arguments: argparse.Namespace) -> dict[str, Path]:
    return {
        "beforeDump": arguments.before.absolute(),
        "afterDump": arguments.after.absolute(),
        "memStats": arguments.memstats.absolute(),
        "sourcePaths": arguments.source_paths.absolute(),
        "sourceReady": arguments.source_ready.absolute(),
    }


def add_input_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--before", required=True, type=Path)
    parser.add_argument("--after", required=True, type=Path)
    parser.add_argument("--memstats", required=True, type=Path)
    parser.add_argument("--source-paths", required=True, type=Path)
    parser.add_argument("--source-ready", required=True, type=Path)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    build_parser = commands.add_parser("build")
    build_parser.add_argument("--out", required=True, type=Path)
    add_input_arguments(build_parser)
    verify_parser = commands.add_parser("verify")
    verify_parser.add_argument("--bundle", required=True, type=Path)
    add_input_arguments(verify_parser)
    arguments = parser.parse_args(argv)
    owner_path = Path(__file__).absolute()
    try:
        paths = cli_input_paths(arguments)
        if arguments.command == "build":
            result = build_bundle(arguments.out.absolute(), owner_path, paths)
        else:
            result = verify_bundle(arguments.bundle.absolute(), owner_path, paths)
    except (CensusError, OSError) as error:
        print(f"REFUSED: {error}", file=sys.stderr)
        return 2
    counts = result["counts"]
    print(
        f"READY: {counts['beforeBlocks']} -> {counts['afterBlocks']} blocks; "
        f"addresses +{counts['addedAddresses']} -{counts['removedAddresses']} "
        f"~{counts['changedAddresses']}; "
        f"source-path hypothesis {result['sourcePathHypothesis']['verdict']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
