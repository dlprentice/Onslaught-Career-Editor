#!/usr/bin/env python3
"""Engine-neutral evidence tooling for Battle Engine Aquila parity research.

The tool deliberately keeps raw captures authoritative.  It creates deterministic,
queryable projections with hashes and explicit health/comparability states:

* ``coverage-diff`` parses text ``drcov`` logs, normalizes module offsets to RVAs,
  joins exact Ghidra function body ranges, and contrasts repeated idle/action runs.
* ``capture-bundle`` losslessly indexes D3D9 proxy logs, TTD query evidence, and
  exact TTD Replay coverage/receipts into SQLite without copying large traces.
* ``ttd-coverage-diff`` performs byte-exact set algebra over matched Replay
  windows and maps every resulting byte back to exact Ghidra body fragments.
* ``symbol-map`` turns a Ghidra inventory into an ASLR-safe RVA map consumed by
  ``bea_ttd_symbols.dll``.
* ``symbol-proof`` verifies one current map/extension pair against a TTD query
  and emits a hash-bound receipt for every input and debugger artifact.
* ``query`` executes read-only SQL against a generated bundle.
* ``verify`` re-hashes every referenced artifact and checks parse accounting.

No command opens or mutates a Ghidra project, patches an executable, drives the
game, or writes beside a retail installation.
"""

from __future__ import annotations

import argparse
import base64
import bisect
import csv
import dataclasses
import datetime as dt
import hashlib
import json
import os
import pathlib
import re
import sqlite3
import sys
import uuid
from collections import Counter, defaultdict
from typing import Any, Iterable, Iterator, Sequence


TOOL_VERSION = "bea-parity-lab.v1"
BUNDLE_SCHEMA = "bea-parity-capture-bundle.v1"
COVERAGE_SCHEMA = "bea-differential-coverage.v2"
SYMBOL_MAP_SCHEMA = "bea-debugger-symbol-map.v1"
SYMBOL_PROOF_SCHEMA = "bea-ttd-symbol-proof.v1"
_OPEN_DATABASES: list[sqlite3.Connection] = []

FUN_RE = re.compile(r"^FUN_[0-9A-Fa-f]{8}$")
DRCOV_BB_RE = re.compile(
    r"^module\[\s*(?P<module>\d+)\]:\s*"
    r"0x(?P<start>[0-9A-Fa-f]+),\s*(?P<size>\d+)\s*$"
)
D3D_DRAW_RE = re.compile(r"^D\s+(?P<frame>\d+)\s+(?P<draw>\d+)\s+(?P<op>\S+)\s*(?P<tail>.*)$")
D3D_VERTEX_RE = re.compile(
    r"^V\s+(?P<frame>\d+)\s+(?P<draw>\d+)\s+(?P<ordinal>\S+)\s*(?P<tail>.*)$"
)
D3D_INDEX_RE = re.compile(r"^I\s+(?P<frame>\d+)\s+(?P<draw>\d+)\s+(?P<tail>.*)$")
D3D_FRAME_RE = re.compile(r"^(?P<kind>[PSCG!])\s+(?P<frame>\d+)(?:\s+(?P<tail>.*))?$")
D3D_LOCK_RE = re.compile(r"^(?P<kind>[LU])\s+(?P<buffer>VB|IB)\s+(?P<tail>.*)$")
D3D_RESOURCE_RE = re.compile(r"^(?P<buffer>VB|IB)\s+(?P<event>\S+)\s*(?P<tail>.*)$")
D3D_REFUSAL_TOTAL_RE = re.compile(r"^# refusals total=(?P<refusals>\d+) warnings=(?P<warnings>\d+)")
TTD_MARKER_RE = re.compile(r"###(?P<kind>[A-Za-z0-9_.:-]+)(?:\s+(?P<body>.*))?")
BEASYM_SUMMARY_RE = re.compile(
    r'^BEASYM_OK module=(?P<module>\S+) base=0x(?P<base>[0-9A-Fa-f]+) '
    r'size=0x(?P<size>[0-9A-Fa-f]+) rows=(?P<rows>\d+) '
    r'added=(?P<added>\d+) retryRecovered=(?P<retry>\d+) '
    r'rejected=(?P<rejected>\d+) malformed=(?P<malformed>\d+) '
    r'outOfModule=(?P<outside>\d+) map="(?P<map>.+)"$'
)
TTD_SYMBOL_CALL_RE = re.compile(
    r'^@\$cursession\.TTD\.Calls\("(?P<symbol>[^"]+)"\)\.Count\(\) : '
    r'0x(?P<count>[0-9A-Fa-f]+)$'
)
TTD_NUMERIC_CALL_RE = re.compile(
    r'^@\$cursession\.TTD\.Calls\((?P<address>0x[0-9A-Fa-f]+)\)'
    r'\.Count\(\) : 0x(?P<count>[0-9A-Fa-f]+)$'
)

KNOWN_STATIC_TARGET_DERIVATIONS: dict[
    tuple[str, str], dict[str, Any]
] = {
    (
        "74154BFAE14DDC8ECB87A0766F5BC381C7B7F1AB334ED7A753040EDA1E1E7750",
        "E1436EF7E0AD9CCBDDD43AAACA952F6E84D4B1A282835CEAD745EFCFC32FADF4",
    ): {
        "id": "bea-pristine-to-reviewed-safe-runtime-v1",
        "ranges": [
            {
                "fileOffsetStart": "0x0012A644",
                "fileOffsetEndExclusive": "0x0012A648",
                "bytes": 4,
                "staticHex": "a1f02d66",
                "targetHex": "b8010000",
            }
        ],
    }
}


class ParityLabError(RuntimeError):
    """A fail-closed input, provenance, or parse error."""


@dataclasses.dataclass(frozen=True)
class DrcovModule:
    module_id: int
    containing_id: int
    start: int
    end: int
    entry: int
    offset: int
    preferred_base: int | None
    checksum: int | None
    timestamp: int | None
    path: str


@dataclasses.dataclass(frozen=True)
class DrcovBlock:
    module_id: int
    start: int
    size: int


@dataclasses.dataclass
class DrcovLog:
    path: pathlib.Path
    version: int
    flavor: str
    module_table_version: int
    declared_module_count: int
    declared_bb_count: int
    modules: dict[int, DrcovModule]
    blocks: list[DrcovBlock]


@dataclasses.dataclass
class FunctionRecord:
    address: int
    name: str
    body_min: int
    body_max: int
    body_bytes: int
    body_range_count: int | None
    name_source: str
    tags: str
    ranges: list[tuple[int, int]]
    range_quality: str


@dataclasses.dataclass(frozen=True)
class CallEdge:
    caller: int
    callee: int
    count: int


@dataclasses.dataclass
class ParsedD3D9:
    total_lines: int
    recognized_data: int
    recognized_comments: int
    unknown_records: int
    malformed_records: int
    encoding_errors: int
    footer_seen: bool
    declared_refusals: int | None
    declared_warnings: int | None
    observed_refusals: int
    observed_warnings: int
    present_draw_mismatches: int
    record_counts: Counter[str]
    header: dict[str, Any]
    diagnostics: list[dict[str, Any]]

    @property
    def accounted_lines(self) -> int:
        return (
            self.recognized_data
            + self.recognized_comments
            + self.unknown_records
            + self.malformed_records
        )

    @property
    def health(self) -> str:
        if self.accounted_lines != self.total_lines:
            return "ERROR"
        if self.malformed_records or self.encoding_errors:
            return "ERROR"
        if (
            self.unknown_records
            or not self.footer_seen
            or self.header.get("format") != "bea-d3d9-proxy v1"
            or self.present_draw_mismatches
            or self.record_counts.get("GRAB_DIAGNOSTIC", 0)
        ):
            return "PARTIAL"
        if (
            self.declared_refusals is not None
            and self.declared_refusals != self.observed_refusals
        ):
            return "PARTIAL"
        if (
            self.declared_warnings is not None
            and self.declared_warnings != self.observed_warnings
        ):
            return "PARTIAL"
        return "COMPLETE"


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def parse_int(value: str | int | None, *, field: str = "value") -> int:
    if isinstance(value, int):
        return value
    if value is None:
        raise ParityLabError(f"Missing integer for {field}")
    text = str(value).strip()
    try:
        if text.lower().startswith("0x"):
            return int(text, 16)
        if re.fullmatch(r"[0-9A-Fa-f]{8,16}", text) and re.search(r"[A-Fa-f]", text):
            return int(text, 16)
        return int(text, 10)
    except ValueError as exc:
        raise ParityLabError(f"Invalid integer for {field}: {value!r}") from exc


def parse_hex_int(value: str | int | None, *, field: str = "value") -> int:
    """Parse a field whose producer defines bare digits as hexadecimal."""
    if isinstance(value, int):
        return value
    if value is None:
        raise ParityLabError(f"Missing hexadecimal integer for {field}")
    text = str(value).strip()
    if text.lower().startswith("0x"):
        text = text[2:]
    if not re.fullmatch(r"[0-9A-Fa-f]+", text):
        raise ParityLabError(f"Invalid hexadecimal integer for {field}: {value!r}")
    return int(text, 16)


def parse_ttd_position(value: Any, *, field: str) -> tuple[int, int]:
    if not isinstance(value, str):
        raise ParityLabError(f"TTD position {field} must be a string")
    match = re.fullmatch(
        r"0x(?P<sequence>[0-9A-Fa-f]+):0x(?P<steps>[0-9A-Fa-f]+)",
        value,
    )
    if match is None:
        raise ParityLabError(f"Invalid TTD position for {field}: {value!r}")
    sequence = int(match.group("sequence"), 16)
    steps = int(match.group("steps"), 16)
    if sequence > 0xFFFFFFFFFFFFFFFF or steps > 0xFFFFFFFFFFFFFFFF:
        raise ParityLabError(f"TTD position exceeds uint64 for {field}: {value!r}")
    return sequence, steps


def sha256_file(path: pathlib.Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(chunk_size)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest().upper()


def md5_file(path: pathlib.Path, chunk_size: int = 1024 * 1024) -> str:
    # MD5 is used only to bind a local file to Ghidra's import identity field.
    digest = hashlib.md5(usedforsecurity=False)
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(chunk_size)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest().lower()


def artifact_facts(path: pathlib.Path, kind: str) -> dict[str, Any]:
    resolved = path.resolve()
    if not resolved.is_file():
        raise ParityLabError(f"No such {kind} artifact: {resolved}")
    stat = resolved.stat()
    return {
        "kind": kind,
        "path": str(resolved),
        "bytes": stat.st_size,
        "sha256": sha256_file(resolved),
    }


def assert_artifact_unchanged(path: pathlib.Path, facts: dict[str, Any]) -> None:
    current = artifact_facts(path, str(facts["kind"]))
    if current["bytes"] != facts["bytes"] or current["sha256"] != facts["sha256"]:
        raise ParityLabError(
            f"Artifact changed while it was being parsed: {path.resolve()}"
        )


def pe_facts(path: pathlib.Path) -> dict[str, Any]:
    raw = path.read_bytes()
    if len(raw) < 0x100 or raw[:2] != b"MZ":
        raise ParityLabError(f"Not a PE executable: {path}")
    pe_offset = int.from_bytes(raw[0x3C:0x40], "little")
    if pe_offset + 0x78 > len(raw) or raw[pe_offset : pe_offset + 4] != b"PE\0\0":
        raise ParityLabError(f"Invalid PE header: {path}")
    coff = pe_offset + 4
    machine = int.from_bytes(raw[coff : coff + 2], "little")
    timestamp = int.from_bytes(raw[coff + 4 : coff + 8], "little")
    optional_size = int.from_bytes(raw[coff + 16 : coff + 18], "little")
    optional = coff + 20
    if optional + optional_size > len(raw):
        raise ParityLabError(f"Truncated PE optional header: {path}")
    magic = int.from_bytes(raw[optional : optional + 2], "little")
    if magic != 0x10B:
        raise ParityLabError(f"Expected PE32 executable, got magic 0x{magic:04X}: {path}")
    image_base = int.from_bytes(raw[optional + 0x1C : optional + 0x20], "little")
    size_of_image = int.from_bytes(raw[optional + 0x38 : optional + 0x3C], "little")
    checksum = int.from_bytes(raw[optional + 0x40 : optional + 0x44], "little")
    return {
        "machine": f"0x{machine:04X}",
        "timestamp": f"0x{timestamp:08X}",
        "timestampInteger": timestamp,
        "optionalMagic": f"0x{magic:04X}",
        "imageBase": f"0x{image_base:08X}",
        "imageBaseInteger": image_base,
        "sizeOfImage": f"0x{size_of_image:08X}",
        "sizeOfImageInteger": size_of_image,
        "checksum": f"0x{checksum:08X}",
        "checksumInteger": checksum,
    }


def image_derivation(static_path: pathlib.Path, target_path: pathlib.Path) -> dict[str, Any]:
    static_facts = artifact_facts(static_path, "static-specimen-executable")
    target_facts = artifact_facts(target_path, "runtime-target-executable")
    static_raw = static_path.read_bytes()
    target_raw = target_path.read_bytes()
    if (
        len(static_raw) != static_facts["bytes"]
        or hashlib.sha256(static_raw).hexdigest().upper() != static_facts["sha256"]
        or len(target_raw) != target_facts["bytes"]
        or hashlib.sha256(target_raw).hexdigest().upper() != target_facts["sha256"]
    ):
        raise ParityLabError("Static/runtime executable changed while being read")
    static_pe = pe_facts(static_path)
    target_pe = pe_facts(target_path)
    if len(static_raw) != len(target_raw):
        raise ParityLabError(
            f"Static/runtime executables differ in length: {len(static_raw)} != {len(target_raw)}"
        )
    identity_keys = (
        "machine",
        "timestamp",
        "optionalMagic",
        "imageBase",
        "sizeOfImage",
        "checksum",
    )
    mismatches = [
        key for key in identity_keys if static_pe[key] != target_pe[key]
    ]
    if mismatches:
        raise ParityLabError(
            "Static/runtime PE layout identity differs: " + ", ".join(mismatches)
        )
    ranges: list[dict[str, Any]] = []
    index = 0
    while index < len(static_raw):
        if static_raw[index] == target_raw[index]:
            index += 1
            continue
        start = index
        while index < len(static_raw) and static_raw[index] != target_raw[index]:
            index += 1
        ranges.append(
            {
                "fileOffsetStart": f"0x{start:08X}",
                "fileOffsetEndExclusive": f"0x{index:08X}",
                "bytes": index - start,
                "staticHex": static_raw[start:index].hex(),
                "targetHex": target_raw[start:index].hex(),
            }
        )
    if ranges:
        known = KNOWN_STATIC_TARGET_DERIVATIONS.get(
            (static_facts["sha256"], target_facts["sha256"])
        )
        if known is None or known["ranges"] != ranges:
            raise ParityLabError(
                "Static/runtime executable byte derivation is not reviewed: "
                f"{static_facts['sha256']} -> {target_facts['sha256']}"
            )
        derivation_policy = known["id"]
    else:
        derivation_policy = "byte-identical"
    assert_artifact_unchanged(static_path, static_facts)
    assert_artifact_unchanged(target_path, target_facts)
    return {
        "static": {
            **static_facts,
            "md5": hashlib.md5(static_raw).hexdigest(),
            "pe": static_pe,
        },
        "target": {
            **target_facts,
            "md5": hashlib.md5(target_raw).hexdigest(),
            "pe": target_pe,
        },
        "layoutCompatible": True,
        "derivationPolicy": derivation_policy,
        "differentByteCount": sum(row["bytes"] for row in ranges),
        "differenceRanges": ranges,
    }


def write_json(path: pathlib.Path, payload: Any) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def write_jsonl(path: pathlib.Path, rows: Iterable[dict[str, Any]]) -> int:
    count = 0
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")))
            handle.write("\n")
            count += 1
    return count


def create_output_dir(path: pathlib.Path) -> pathlib.Path:
    resolved = path.resolve()
    if resolved.exists():
        if not resolved.is_dir():
            raise ParityLabError(f"Output exists and is not a directory: {resolved}")
        if any(resolved.iterdir()):
            raise ParityLabError(f"Refusing to overwrite non-empty output directory: {resolved}")
    else:
        resolved.mkdir(parents=True)
    return resolved


def open_database(path: pathlib.Path) -> sqlite3.Connection:
    connection = sqlite3.connect(path)
    _OPEN_DATABASES.append(connection)
    connection.execute("PRAGMA foreign_keys=ON")
    connection.execute("PRAGMA journal_mode=DELETE")
    connection.execute("PRAGMA synchronous=FULL")
    connection.executescript(
        """
        CREATE TABLE meta (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        CREATE TABLE artifact (
            artifact_id INTEGER PRIMARY KEY,
            kind TEXT NOT NULL,
            path TEXT NOT NULL,
            bytes INTEGER NOT NULL,
            sha256 TEXT NOT NULL,
            schema_version TEXT,
            health TEXT,
            UNIQUE(kind, path)
        );
        CREATE TABLE d3d9_event (
            event_id INTEGER PRIMARY KEY,
            artifact_id INTEGER NOT NULL REFERENCES artifact(artifact_id),
            sequence INTEGER NOT NULL,
            byte_offset INTEGER NOT NULL,
            byte_length INTEGER NOT NULL,
            line_number INTEGER NOT NULL,
            record_type TEXT NOT NULL,
            frame INTEGER,
            draw INTEGER,
            ordinal TEXT,
            status TEXT,
            raw TEXT NOT NULL
        );
        CREATE TABLE d3d9_field (
            event_id INTEGER NOT NULL REFERENCES d3d9_event(event_id),
            key TEXT NOT NULL,
            value_text TEXT,
            value_integer INTEGER,
            value_real REAL,
            provenance TEXT NOT NULL,
            PRIMARY KEY(event_id, key)
        );
        CREATE TABLE ttd_capture (
            capture_id INTEGER PRIMARY KEY,
            artifact_id INTEGER NOT NULL REFERENCES artifact(artifact_id),
            name TEXT,
            target_sha256 TEXT,
            trace_path TEXT,
            trace_bytes INTEGER,
            recorder_version TEXT,
            guest_outcome TEXT,
            guest_ran_cleanly INTEGER,
            recorded_at_utc TEXT,
            raw_json TEXT NOT NULL
        );
        CREATE TABLE ttd_query (
            query_id INTEGER PRIMARY KEY,
            artifact_id INTEGER NOT NULL REFERENCES artifact(artifact_id),
            trace_path TEXT,
            trace_bytes INTEGER,
            schema_version TEXT,
            ok INTEGER NOT NULL,
            timed_out INTEGER NOT NULL,
            problems_json TEXT NOT NULL,
            raw_json TEXT NOT NULL
        );
        CREATE TABLE ttd_line (
            query_id INTEGER NOT NULL REFERENCES ttd_query(query_id),
            ordinal INTEGER NOT NULL,
            marker_kind TEXT,
            marker_body TEXT,
            text TEXT NOT NULL,
            PRIMARY KEY(query_id, ordinal)
        );
        CREATE TABLE ttd_exec_coverage (
            coverage_id INTEGER PRIMARY KEY,
            artifact_id INTEGER NOT NULL REFERENCES artifact(artifact_id),
            trace_path TEXT NOT NULL,
            trace_bytes TEXT NOT NULL,
            module_name TEXT NOT NULL,
            module_base INTEGER NOT NULL,
            module_size INTEGER NOT NULL,
            module_timestamp INTEGER NOT NULL,
            module_checksum INTEGER NOT NULL,
            replay_mode TEXT NOT NULL,
            requested_from TEXT NOT NULL,
            requested_to TEXT NOT NULL,
            range_count INTEGER NOT NULL,
            covered_bytes TEXT NOT NULL,
            -- NULL when the producer quarantined its replay counters.  The
            -- column is deliberately nullable so a consumer that wants a
            -- number gets nothing rather than a wrong one.
            callback_hits TEXT,
            counters_quarantined INTEGER NOT NULL,
            stop_reason TEXT NOT NULL,
            -- 1 when the wrapper adjudicated a non-base terminal stop for the
            -- trace class the caller declared (#153).  Mirrors
            -- counters_quarantined: the ranges stay valid and the reason the
            -- collector's own clause was overruled stays queryable.
            stop_reason_adjudicated INTEGER NOT NULL,
            replay_complete INTEGER NOT NULL,
            marker_assertions_passed INTEGER NOT NULL,
            collector_checks_passed INTEGER NOT NULL,
            metadata_json TEXT NOT NULL,
            gap_json TEXT NOT NULL,
            summary_json TEXT NOT NULL
        );
        CREATE TABLE ttd_exec_range (
            coverage_id INTEGER NOT NULL REFERENCES ttd_exec_coverage(coverage_id),
            ordinal INTEGER NOT NULL,
            rva_start INTEGER NOT NULL,
            rva_end_exclusive INTEGER NOT NULL,
            va_start INTEGER NOT NULL,
            va_end_exclusive INTEGER NOT NULL,
            byte_count INTEGER NOT NULL,
            PRIMARY KEY(coverage_id, ordinal)
        );
        CREATE TABLE ttd_exec_assertion (
            coverage_id INTEGER NOT NULL REFERENCES ttd_exec_coverage(coverage_id),
            ordinal INTEGER NOT NULL,
            expectation TEXT NOT NULL,
            rva INTEGER NOT NULL,
            va INTEGER NOT NULL,
            observed INTEGER NOT NULL,
            pass INTEGER NOT NULL,
            PRIMARY KEY(coverage_id, ordinal)
        );
        CREATE TABLE shot_sample (
            artifact_id INTEGER NOT NULL REFERENCES artifact(artifact_id),
            ordinal INTEGER NOT NULL,
            frame INTEGER,
            written INTEGER,
            file TEXT,
            width INTEGER,
            height INTEGER,
            d3d_format INTEGER,
            mean_r REAL,
            mean_g REAL,
            mean_b REAL,
            max_cell_delta REAL,
            raw_json TEXT NOT NULL,
            PRIMARY KEY(artifact_id, ordinal)
        );
        CREATE TABLE shot_comment (
            artifact_id INTEGER NOT NULL REFERENCES artifact(artifact_id),
            line_number INTEGER NOT NULL,
            text TEXT NOT NULL,
            fields_json TEXT NOT NULL,
            PRIMARY KEY(artifact_id, line_number)
        );
        CREATE TABLE coverage_run (
            run_id INTEGER PRIMARY KEY,
            role TEXT NOT NULL,
            campaign_id TEXT,
            sequence_index INTEGER,
            artifact_id INTEGER NOT NULL REFERENCES artifact(artifact_id),
            drcov_version INTEGER NOT NULL,
            flavor TEXT NOT NULL,
            module_table_version INTEGER NOT NULL,
            module_path TEXT NOT NULL,
            module_preferred_base INTEGER,
            declared_blocks INTEGER NOT NULL,
            unique_module_blocks INTEGER NOT NULL
        );
        CREATE TABLE coverage_function (
            function_address INTEGER PRIMARY KEY,
            function_rva INTEGER NOT NULL,
            name TEXT NOT NULL,
            name_source TEXT,
            tags TEXT,
            body_min INTEGER NOT NULL,
            body_max INTEGER NOT NULL,
            body_bytes INTEGER NOT NULL,
            body_range_count INTEGER,
            range_quality TEXT NOT NULL,
            naming_risk TEXT NOT NULL
        );
        CREATE TABLE coverage_observation (
            run_id INTEGER NOT NULL REFERENCES coverage_run(run_id),
            function_address INTEGER NOT NULL REFERENCES coverage_function(function_address),
            block_count INTEGER NOT NULL,
            PRIMARY KEY(run_id, function_address)
        );
        CREATE TABLE coverage_block (
            run_id INTEGER NOT NULL REFERENCES coverage_run(run_id),
            rva INTEGER NOT NULL,
            size INTEGER NOT NULL,
            va INTEGER NOT NULL,
            function_address INTEGER,
            mapping_quality TEXT NOT NULL,
            PRIMARY KEY(run_id, rva)
        );
        CREATE TABLE coverage_candidate (
            function_address INTEGER PRIMARY KEY REFERENCES coverage_function(function_address),
            classification TEXT NOT NULL,
            scorable INTEGER NOT NULL,
            baseline_support INTEGER NOT NULL,
            action_support INTEGER NOT NULL,
            baseline_runs INTEGER NOT NULL,
            action_runs INTEGER NOT NULL,
            action_novel_blocks INTEGER NOT NULL,
            stable_action_novel_blocks INTEGER NOT NULL,
            rank_ordinal INTEGER NOT NULL,
            callers_json TEXT NOT NULL,
            callees_json TEXT NOT NULL
        );
        CREATE TABLE coverage_delta_block (
            rva INTEGER PRIMARY KEY,
            size INTEGER NOT NULL,
            va INTEGER NOT NULL,
            baseline_support INTEGER NOT NULL,
            action_support INTEGER NOT NULL,
            stable_action_novel INTEGER NOT NULL,
            function_address INTEGER,
            mapping_quality TEXT NOT NULL
        );
        CREATE INDEX d3d9_event_frame_draw ON d3d9_event(frame, draw, record_type);
        CREATE INDEX d3d9_field_key_text ON d3d9_field(key, value_text);
        CREATE INDEX ttd_exec_range_rva ON ttd_exec_range(rva_start, rva_end_exclusive);
        CREATE INDEX coverage_block_function ON coverage_block(function_address);
        CREATE INDEX coverage_candidate_class ON coverage_candidate(classification, rank_ordinal);
        """
    )
    connection.executemany(
        "INSERT INTO meta(key, value) VALUES (?, ?)",
        [
            ("toolVersion", TOOL_VERSION),
            ("createdAtUtc", utc_now()),
        ],
    )
    return connection


def add_artifact(
    connection: sqlite3.Connection,
    facts: dict[str, Any],
    *,
    schema_version: str | None = None,
    health: str | None = None,
) -> int:
    cursor = connection.execute(
        """
        INSERT INTO artifact(kind, path, bytes, sha256, schema_version, health)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            facts["kind"],
            facts["path"],
            facts["bytes"],
            facts["sha256"],
            schema_version,
            health,
        ),
    )
    return int(cursor.lastrowid)


def _split_drcov_csv(line: str, column_count: int) -> list[str]:
    # Module paths are not quoted and can theoretically contain a comma.  Split
    # only the fixed leading fields; the final field owns the remainder.
    parts = line.split(",", maxsplit=max(column_count - 1, 0))
    return [part.strip() for part in parts]


def parse_drcov(path: pathlib.Path) -> DrcovLog:
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ParityLabError(
            f"{path} is not a text drcov log; record with drcov -dump_text"
        ) from exc
    lines = text.splitlines()
    if len(lines) < 5:
        raise ParityLabError(f"Truncated drcov log: {path}")

    version_match = re.fullmatch(r"DRCOV VERSION:\s*(\d+)", lines[0].strip())
    flavor_match = re.fullmatch(r"DRCOV FLAVOR:\s*(\S+)", lines[1].strip())
    module_match = re.fullmatch(
        r"Module Table:\s*version\s*(\d+),\s*count\s*(\d+)", lines[2].strip()
    )
    if not version_match or not flavor_match or not module_match:
        raise ParityLabError(f"Unsupported drcov header in {path}")
    version = int(version_match.group(1))
    flavor = flavor_match.group(1)
    module_table_version = int(module_match.group(1))
    declared_modules = int(module_match.group(2))
    if not lines[3].startswith("Columns:"):
        raise ParityLabError(f"Missing drcov module columns in {path}")
    columns = [value.strip() for value in lines[3][len("Columns:") :].split(",")]

    modules: dict[int, DrcovModule] = {}
    index = 4
    for _ in range(declared_modules):
        if index >= len(lines):
            raise ParityLabError(f"Truncated drcov module table in {path}")
        values = _split_drcov_csv(lines[index], len(columns))
        index += 1
        if len(values) != len(columns):
            raise ParityLabError(
                f"Malformed drcov module row {index} in {path}: "
                f"{len(values)} values for {len(columns)} columns"
            )
        row = dict(zip(columns, values))
        module_id = parse_int(row.get("id"), field="module id")
        containing_id = parse_int(
            row.get("containing_id", row.get("id")), field="containing module id"
        )
        preferred = row.get("preferred_base")
        module = DrcovModule(
            module_id=module_id,
            containing_id=containing_id,
            start=parse_int(row.get("start"), field="module start"),
            end=parse_int(row.get("end"), field="module end"),
            entry=parse_int(row.get("entry"), field="module entry"),
            # drcov module-table v5 prints this 64-bit hexadecimal field
            # without a 0x prefix (for example 0000000000001000).
            offset=parse_hex_int(row.get("offset", "0"), field="module offset"),
            preferred_base=parse_int(preferred, field="preferred base") if preferred else None,
            checksum=parse_int(row["checksum"], field="checksum") if row.get("checksum") else None,
            timestamp=parse_int(row["timestamp"], field="timestamp") if row.get("timestamp") else None,
            path=row.get("path", ""),
        )
        if module_id in modules:
            raise ParityLabError(f"Duplicate drcov module id {module_id} in {path}")
        modules[module_id] = module

    if index >= len(lines):
        raise ParityLabError(f"Missing BB table in {path}")
    bb_header = re.fullmatch(r"BB Table:\s*(\d+)\s+bbs", lines[index].strip())
    if not bb_header:
        raise ParityLabError(f"Missing text BB table in {path}; use -dump_text")
    declared_bbs = int(bb_header.group(1))
    index += 1
    if index >= len(lines) or lines[index].strip() != "module id, start, size:":
        raise ParityLabError(f"Binary or unsupported BB table in {path}; use -dump_text")
    index += 1

    blocks: list[DrcovBlock] = []
    for line_number, line in enumerate(lines[index:], start=index + 1):
        if not line.strip():
            continue
        match = DRCOV_BB_RE.fullmatch(line.strip())
        if not match:
            raise ParityLabError(f"Malformed drcov BB row {line_number} in {path}")
        module_id = int(match.group("module"))
        if module_id not in modules and module_id != 0xFFFF:
            raise ParityLabError(
                f"BB row {line_number} references unknown module {module_id} in {path}"
            )
        blocks.append(
            DrcovBlock(
                module_id=module_id,
                start=int(match.group("start"), 16),
                size=int(match.group("size")),
            )
        )
    if len(blocks) != declared_bbs:
        raise ParityLabError(
            f"drcov BB count mismatch in {path}: declared {declared_bbs}, parsed {len(blocks)}"
        )
    return DrcovLog(
        path=path.resolve(),
        version=version,
        flavor=flavor,
        module_table_version=module_table_version,
        declared_module_count=declared_modules,
        declared_bb_count=declared_bbs,
        modules=modules,
        blocks=blocks,
    )


def _read_tsv_rows(path: pathlib.Path) -> tuple[list[str] | None, list[list[str]]]:
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    data = [line for line in lines if line.strip() and not line.startswith("#")]
    if not data:
        raise ParityLabError(f"No data rows in TSV: {path}")
    first = data[0].split("\t")
    header = first if first[0].strip().lower() in {
        "address",
        "functionaddress",
        "calleraddress",
        "program",
    } else None
    body = data[1:] if header else data
    return header, [line.split("\t") for line in body]


def read_tsv_metadata(path: pathlib.Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if not line.startswith("#"):
            continue
        body = line[1:].strip()
        if "=" not in body:
            continue
        key, value = body.split("=", 1)
        if key and key not in result:
            result[key] = value
    return result


def load_body_ranges(path: pathlib.Path) -> dict[int, list[tuple[int, int]]]:
    header, rows = _read_tsv_rows(path)
    if not header:
        raise ParityLabError(f"Body-range TSV requires a header: {path}")
    lower = {name.lower(): index for index, name in enumerate(header)}

    def column(*names: str) -> int:
        for name in names:
            if name.lower() in lower:
                return lower[name.lower()]
        raise ParityLabError(f"Body-range TSV missing one of {names}: {path}")

    address_col = column("functionAddress", "address")
    minimum_col = column("rangeMin", "min")
    maximum_col = column("rangeMax", "max")
    result: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for row_number, row in enumerate(rows, start=2):
        try:
            address = parse_int(row[address_col], field="function address")
            minimum = parse_int(row[minimum_col], field="range min")
            maximum = parse_int(row[maximum_col], field="range max")
        except (IndexError, ParityLabError) as exc:
            raise ParityLabError(f"Malformed body-range row {row_number} in {path}") from exc
        if maximum < minimum:
            raise ParityLabError(f"Reversed body range at row {row_number} in {path}")
        result[address].append((minimum, maximum))
    for ranges in result.values():
        ranges.sort()
    return dict(result)


def load_functions(
    path: pathlib.Path, body_ranges_path: pathlib.Path | None
) -> list[FunctionRecord]:
    header, rows = _read_tsv_rows(path)
    exact_ranges = load_body_ranges(body_ranges_path) if body_ranges_path else {}
    functions: list[FunctionRecord] = []
    if header:
        lower = {name.lower(): index for index, name in enumerate(header)}

        def optional(row: list[str], name: str, default: str = "") -> str:
            index = lower.get(name.lower())
            return row[index] if index is not None and index < len(row) else default

        for row_number, row in enumerate(rows, start=2):
            try:
                address = parse_int(optional(row, "address"), field="address")
                name = optional(row, "name")
                body_min = parse_int(optional(row, "bodyMin"), field="bodyMin")
                body_max = parse_int(optional(row, "bodyMax"), field="bodyMax")
                body_bytes_text = optional(row, "bodyBytes")
                body_bytes = (
                    parse_int(body_bytes_text, field="bodyBytes")
                    if body_bytes_text
                    else body_max - body_min + 1
                )
                ranges_text = optional(row, "bodyRanges")
                range_count = parse_int(ranges_text, field="bodyRanges") if ranges_text else None
            except ParityLabError as exc:
                raise ParityLabError(f"Malformed function row {row_number} in {path}") from exc
            supplied = exact_ranges.get(address)
            if supplied:
                ranges = supplied
                quality = "EXACT_GHIDRA_RANGES"
                if range_count is not None and range_count != len(ranges):
                    raise ParityLabError(
                        f"Range-count mismatch for 0x{address:08X}: "
                        f"inventory {range_count}, sidecar {len(ranges)}"
                    )
            elif range_count == 1:
                ranges = [(body_min, body_max)]
                quality = "EXACT_CONTIGUOUS_INVENTORY"
            elif range_count and range_count > 1:
                ranges = [(body_min, body_max)]
                quality = "BOUNDING_FRAGMENTED_UNSCORABLE"
            else:
                ranges = [(body_min, body_max)]
                quality = "BOUNDING_UNKNOWN_UNSCORABLE"
            functions.append(
                FunctionRecord(
                    address=address,
                    name=name,
                    body_min=body_min,
                    body_max=body_max,
                    body_bytes=body_bytes,
                    body_range_count=range_count,
                    name_source=optional(row, "nameSource"),
                    tags=optional(row, "tags"),
                    ranges=ranges,
                    range_quality=quality,
                )
            )
    else:
        for row_number, row in enumerate(rows, start=1):
            if len(row) < 4:
                raise ParityLabError(f"Malformed four-column function row {row_number} in {path}")
            address = parse_int(row[0], field="address")
            body_min = parse_int(row[2], field="bodyMin")
            body_max = parse_int(row[3], field="bodyMax")
            supplied = exact_ranges.get(address)
            functions.append(
                FunctionRecord(
                    address=address,
                    name=row[1],
                    body_min=body_min,
                    body_max=body_max,
                    body_bytes=sum(end - start + 1 for start, end in supplied)
                    if supplied
                    else body_max - body_min + 1,
                    body_range_count=len(supplied) if supplied else None,
                    name_source="",
                    tags="",
                    ranges=supplied or [(body_min, body_max)],
                    range_quality=(
                        "EXACT_GHIDRA_RANGES" if supplied else "BOUNDING_UNKNOWN_UNSCORABLE"
                    ),
                )
            )
    addresses = [function.address for function in functions]
    if len(addresses) != len(set(addresses)):
        raise ParityLabError(f"Duplicate function addresses in {path}")
    if exact_ranges:
        known = set(addresses)
        orphaned = sorted(set(exact_ranges) - known)
        if orphaned:
            raise ParityLabError(
                f"Body-range sidecar contains {len(orphaned)} orphan function(s); "
                f"first is 0x{orphaned[0]:08X}"
            )
        for function in functions:
            supplied = exact_ranges.get(function.address)
            if not supplied:
                raise ParityLabError(
                    f"Body-range sidecar omits function 0x{function.address:08X}"
                )
            previous_max: int | None = None
            for minimum, maximum in supplied:
                if previous_max is not None and minimum <= previous_max:
                    raise ParityLabError(
                        f"Overlapping exact ranges for 0x{function.address:08X}"
                    )
                previous_max = maximum
            if not any(
                minimum <= function.address <= maximum
                for minimum, maximum in supplied
            ):
                raise ParityLabError(
                    f"Function entry 0x{function.address:08X} is outside its exact ranges"
                )
            if supplied[0][0] != function.body_min or supplied[-1][1] != function.body_max:
                raise ParityLabError(
                    f"Exact range envelope disagrees for 0x{function.address:08X}"
                )
            supplied_bytes = sum(maximum - minimum + 1 for minimum, maximum in supplied)
            if supplied_bytes != function.body_bytes:
                raise ParityLabError(
                    f"Exact range bytes disagree for 0x{function.address:08X}: "
                    f"{supplied_bytes} != {function.body_bytes}"
                )
    functions.sort(key=lambda function: function.address)
    return functions


def load_call_edges(path: pathlib.Path | None) -> list[CallEdge]:
    if not path:
        return []
    header, rows = _read_tsv_rows(path)
    if not header:
        raise ParityLabError(f"Call-edge TSV requires a header: {path}")
    lower = {name.lower(): index for index, name in enumerate(header)}
    try:
        caller_col = lower["calleraddress"]
        callee_col = lower["calleeaddress"]
    except KeyError as exc:
        raise ParityLabError(f"Call-edge TSV missing callerAddress/calleeAddress: {path}") from exc
    count_col = lower.get("callsitecount")
    edges: list[CallEdge] = []
    for row_number, row in enumerate(rows, start=2):
        try:
            edges.append(
                CallEdge(
                    caller=parse_int(row[caller_col], field="callerAddress"),
                    callee=parse_int(row[callee_col], field="calleeAddress"),
                    count=parse_int(row[count_col], field="callSiteCount") if count_col is not None else 1,
                )
            )
        except (IndexError, ParityLabError) as exc:
            raise ParityLabError(f"Malformed call-edge row {row_number} in {path}") from exc
    return edges


def validate_graph_receipt(
    receipt_path: pathlib.Path,
    body_ranges_path: pathlib.Path,
    call_edges_path: pathlib.Path,
    functions: Sequence[FunctionRecord],
    edges: Sequence[CallEdge],
) -> dict[str, Any]:
    receipt_facts = artifact_facts(
        receipt_path, "ghidra-parity-graph-ready-receipt"
    )
    payload = json.loads(receipt_path.read_text(encoding="utf-8"))
    if payload.get("schemaVersion") != "bea-ghidra-parity-graph-receipt.v2":
        raise ParityLabError(
            f"Unsupported Ghidra parity-graph READY receipt: {receipt_path}"
        )

    resolved_receipt = receipt_path.resolve(strict=True)
    resolved_ranges = body_ranges_path.resolve(strict=True)
    resolved_calls = call_edges_path.resolve(strict=True)
    if not (
        resolved_receipt.parent
        == resolved_ranges.parent
        == resolved_calls.parent
    ):
        raise ParityLabError(
            "Ghidra parity-graph receipt and data files must share one directory"
        )

    def verify_member(key: str, path: pathlib.Path, kind: str) -> dict[str, Any]:
        declared = payload.get(key)
        if not isinstance(declared, dict):
            raise ParityLabError(
                f"Ghidra parity-graph receipt lacks {key}: {receipt_path}"
            )
        declared_name = str(declared.get("file", ""))
        if (
            not declared_name
            or pathlib.PureWindowsPath(declared_name).name != declared_name
            or pathlib.PurePosixPath(declared_name).name != declared_name
            or declared_name != path.name
        ):
            raise ParityLabError(
                f"Ghidra parity-graph receipt names the wrong {key} file"
            )
        facts = artifact_facts(path, kind)
        try:
            declared_bytes = int(declared["bytes"])
            declared_hash = str(declared["sha256"]).upper()
        except (KeyError, TypeError, ValueError) as exc:
            raise ParityLabError(
                f"Malformed Ghidra parity-graph {key} artifact facts"
            ) from exc
        if facts["bytes"] != declared_bytes or facts["sha256"] != declared_hash:
            raise ParityLabError(
                f"Ghidra parity-graph {key} hash/size disagrees with READY receipt"
            )
        return declared

    range_declaration = verify_member(
        "bodyRanges", resolved_ranges, "ghidra-body-ranges"
    )
    call_declaration = verify_member(
        "directCalls", resolved_calls, "ghidra-call-edges"
    )
    range_metadata = read_tsv_metadata(resolved_ranges)
    call_metadata = read_tsv_metadata(resolved_calls)
    required_metadata = (
        "schema",
        "executableMd5",
        "executablePath",
        "imageBase",
        "language",
        "compilerSpec",
    )
    for key in required_metadata:
        if not range_metadata.get(key) or range_metadata.get(key) != call_metadata.get(key):
            raise ParityLabError(
                f"Ghidra parity-graph pair has missing/mismatched {key} metadata"
            )
    if range_metadata["schema"] != "bea-ghidra-parity-graph.v2":
        raise ParityLabError("Ghidra parity-graph data files are not schema v2")
    program = payload.get("program")
    if not isinstance(program, dict):
        raise ParityLabError("Ghidra parity-graph receipt lacks program identity")
    program_bindings = {
        "executableMd5": "executableMd5",
        "executablePath": "executablePath",
        "imageBase": "imageBase",
        "language": "language",
        "compilerSpec": "compilerSpec",
    }
    for receipt_key, metadata_key in program_bindings.items():
        if str(program.get(receipt_key, "")) != range_metadata[metadata_key]:
            raise ParityLabError(
                f"Ghidra parity-graph receipt/program mismatch for {receipt_key}"
            )

    range_count = sum(len(function.ranges) for function in functions)
    expected_counts = (
        (range_declaration, "functionCount", len(functions)),
        (range_declaration, "rangeCount", range_count),
        (call_declaration, "directEdgeCount", len(edges)),
        (
            call_declaration,
            "directCallSiteCount",
            sum(edge.count for edge in edges),
        ),
    )
    for declaration, key, observed in expected_counts:
        try:
            expected = int(declaration[key])
        except (KeyError, TypeError, ValueError) as exc:
            raise ParityLabError(
                f"Ghidra parity-graph receipt lacks a valid {key}"
            ) from exc
        if expected != observed:
            raise ParityLabError(
                f"Ghidra parity-graph {key} mismatch: receipt {expected}, parsed {observed}"
            )
    assert_artifact_unchanged(receipt_path, receipt_facts)
    return receipt_facts


class FunctionIntervalIndex:
    def __init__(self, functions: Sequence[FunctionRecord]) -> None:
        intervals: list[tuple[int, int, FunctionRecord, str]] = []
        for function in functions:
            if function.range_quality not in {
                "EXACT_GHIDRA_RANGES",
                "EXACT_CONTIGUOUS_INVENTORY",
            }:
                continue
            for minimum, maximum in function.ranges:
                intervals.append((minimum, maximum, function, function.range_quality))
        intervals.sort(key=lambda item: (item[0], item[1], item[2].address))
        self.intervals = intervals
        self.starts = [item[0] for item in intervals]
        self.prefix_max: list[int] = []
        running = -1
        for _, maximum, _, _ in intervals:
            running = max(running, maximum)
            self.prefix_max.append(running)

    def lookup(self, address: int) -> tuple[FunctionRecord | None, str]:
        index = bisect.bisect_right(self.starts, address) - 1
        matches: list[tuple[FunctionRecord, str]] = []
        while index >= 0 and self.prefix_max[index] >= address:
            minimum, maximum, function, quality = self.intervals[index]
            if minimum <= address <= maximum:
                matches.append((function, quality))
            index -= 1
        unique = {match[0].address: match for match in matches}
        if not unique:
            return None, "UNMAPPED"
        if len(unique) > 1:
            return None, "AMBIGUOUS_OVERLAP"
        function, quality = next(iter(unique.values()))
        return function, quality


def naming_risk(function: FunctionRecord) -> str:
    name = function.name
    if FUN_RE.fullmatch(name):
        return "LITERAL_FUN"
    if "__VFunc_" in name or name.startswith("VFunc_"):
        return "PROVISIONAL_VFUNC"
    if re.search(r"(?:^|__)Unk(?:_|$)", name, re.IGNORECASE):
        return "WEAK_UNKNOWN_TOKEN"
    if name.startswith(("Shared", "Thunk", "LAB_")):
        return "GENERIC_OR_SHARED"
    if function.name_source.upper() == "DEFAULT":
        return "DEFAULT_METADATA"
    return "HUMAN_LABEL"


def _module_rva(log: DrcovLog, module: DrcovModule, block: DrcovBlock) -> int:
    # DRCOV v3 changed starts to segment-relative.  The module-table offset is
    # the segment's RVA within the containing image.  v2 starts are image-relative.
    return block.start + module.offset if log.version >= 3 else block.start


def select_module_blocks(
    log: DrcovLog, module_name: str
) -> tuple[list[tuple[int, int]], list[DrcovModule]]:
    selected = [
        module
        for module in log.modules.values()
        if pathlib.PureWindowsPath(module.path).name.casefold() == module_name.casefold()
    ]
    if not selected:
        raise ParityLabError(f"{module_name} is absent from drcov log {log.path}")
    ids = {module.module_id for module in selected}
    blocks = {
        (_module_rva(log, log.modules[block.module_id], block), block.size)
        for block in log.blocks
        if block.module_id in ids
    }
    return sorted(blocks), sorted(selected, key=lambda module: module.module_id)


def windows_path_key(value: str | pathlib.Path) -> str:
    return os.path.normcase(os.path.normpath(str(value))).casefold()


def validate_embedded_file_facts(
    payload: Any,
    *,
    label: str,
) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ParityLabError(f"{label} facts are not an object")
    required = {"path": str, "bytes": int, "sha256": str, "lastWriteUtc": str}
    for key, expected_type in required.items():
        if not isinstance(payload.get(key), expected_type):
            raise ParityLabError(f"{label} facts have invalid or missing {key}")
    path = pathlib.Path(payload["path"])
    if not path.is_file():
        raise ParityLabError(f"{label} file is missing: {path}")
    current = artifact_facts(path, label)
    if (
        int(payload["bytes"]) != current["bytes"]
        or payload["sha256"].upper() != current["sha256"].upper()
    ):
        raise ParityLabError(f"{label} facts no longer match the file: {path}")
    return payload


def load_embedded_json(
    payload: Any,
    *,
    label: str,
) -> tuple[pathlib.Path, dict[str, Any]]:
    facts = validate_embedded_file_facts(payload, label=label)
    path = pathlib.Path(facts["path"])
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ParityLabError(f"{label} is not valid JSON: {path}") from exc
    if not isinstance(value, dict):
        raise ParityLabError(f"{label} JSON is not an object: {path}")
    return path, value


def parse_utc_timestamp(value: Any, *, label: str) -> dt.datetime:
    if not isinstance(value, str) or not value:
        raise ParityLabError(f"{label} is missing")
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = dt.datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ParityLabError(f"{label} is not an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None:
        raise ParityLabError(f"{label} has no UTC offset")
    return parsed.astimezone(dt.timezone.utc)


def validate_cursor_globals(
    payload: Any,
    *,
    expected_x: int,
    expected_y: int,
    label: str,
) -> None:
    if not isinstance(payload, dict):
        raise ParityLabError(f"{label} cursor globals are missing")
    expected = {
        "a": ("0x0089BDA8", expected_x),
        "b": ("0x0089BDA4", expected_y),
        "mouseGate": ("0x0089BDF0", 0),
    }
    for key, (address, value) in expected.items():
        row = payload.get(key)
        if (
            not isinstance(row, dict)
            or row.get("address") != address
            or row.get("asInt32") != value
        ):
            raise ParityLabError(f"{label} {key} does not match the cursor contract")


def validate_window_input_receipt(
    facts: Any,
    *,
    expected_kind: str,
    expected_x: int,
    expected_y: int,
    target_process_id: int,
    target_hwnd: str,
    target_path: str,
    working_directory: str,
    label: str,
) -> None:
    _, payload = load_embedded_json(facts, label=label)
    expected_events = 3 if expected_kind == "click" else 1
    if (
        payload.get("schemaVersion") != "game-window-input.v1"
        or payload.get("processName") != "BEA.exe"
        or payload.get("processId") != target_process_id
        or str(payload.get("hwndHex", "")).casefold() != target_hwnd.casefold()
        or payload.get("status") != "sent"
        or payload.get("plannedOnly") is not False
        or payload.get("backgroundWindowMessagesAllowed") is not True
        or payload.get("transport") != "messages"
        or payload.get("actionCount") != 1
        or payload.get("windowMessageEventsSent") != expected_events
        or payload.get("mouseEventsSent") != expected_events
        or payload.get("keyEventsSent") != 0
        or payload.get("sendInputEventsSent") != 0
        or payload.get("scanKeybdEventsSent") != 0
        or payload.get("deliveryFailure") is not None
        or payload.get("releaseFailures") != []
        or payload.get("unconfirmedReleaseKeys") != []
        or payload.get("sendInputFailures") != []
    ):
        raise ParityLabError(f"{label} did not prove the exact bounded message input")
    for occlusion_key in ("occlusionBefore", "occlusionAfter"):
        occlusion = payload.get(occlusion_key)
        if (
            not isinstance(occlusion, dict)
            or occlusion.get("probed") is not True
            or occlusion.get("unoccluded") is not True
            or occlusion.get("mask") != 0
        ):
            raise ParityLabError(f"{label} lacks {occlusion_key} evidence")
    actions = payload.get("actions")
    expected_action = {
        "kind": expected_kind,
        "x": expected_x,
        "y": expected_y,
    }
    if (
        not isinstance(actions, list)
        or len(actions) != 1
        or not isinstance(actions[0], dict)
        or any(actions[0].get(key) != value for key, value in expected_action.items())
    ):
        raise ParityLabError(f"{label} action differs from the protocol")
    probes = payload.get("cursorProbes")
    if not isinstance(probes, list) or len(probes) != 1:
        raise ParityLabError(f"{label} lacks one cursor probe")
    probe = probes[0]
    if (
        not isinstance(probe, dict)
        or probe.get("step") != expected_kind
        or probe.get("postedClientX") != expected_x
        or probe.get("postedClientY") != expected_y
        or probe.get("matchedX") != ["0x0089BDA8"]
        or probe.get("matchedY") != ["0x0089BDA4"]
    ):
        raise ParityLabError(f"{label} cursor probe differs from the protocol")
    validate_cursor_globals(
        probe.get("globals"),
        expected_x=expected_x,
        expected_y=expected_y,
        label=label,
    )
    selected = payload.get("selectedWindow")
    if (
        not isinstance(selected, dict)
        or selected.get("processId") != target_process_id
        or selected.get("processName") != "BEA.exe"
        or selected.get("minimized") is not False
        or str(selected.get("hwndHex", "")).casefold() != target_hwnd.casefold()
        or windows_path_key(selected.get("executablePath", ""))
        != windows_path_key(target_path)
        or windows_path_key(selected.get("workingDirectory", ""))
        != windows_path_key(working_directory)
    ):
        raise ParityLabError(f"{label} selected-window identity drifted")
    parse_utc_timestamp(payload.get("generatedAt"), label=f"{label} generatedAt")


def validate_options_click_receipt(
    facts: Any,
    *,
    target_process_id: int,
    target_hwnd: str,
    label: str,
) -> None:
    _, payload = load_embedded_json(facts, label=label)
    if (
        payload.get("schemaVersion") != "bea-options-click-receipt.v1"
        or payload.get("processId") != target_process_id
        or str(payload.get("hwndHex", "")).casefold() != target_hwnd.casefold()
        or payload.get("transport") != "PostMessage-button-only"
        or payload.get("precondition")
        != {"page": 0, "cursorX": 219, "cursorY": 404, "mouseGate": 0}
        or payload.get("action")
        != {
            "clientX": 219,
            "clientY": 404,
            "mouseMovePosted": False,
            "buttonDownPosted": True,
            "buttonUpPosted": True,
        }
    ):
        raise ParityLabError(f"{label} does not prove the isolated Options click")
    parse_utc_timestamp(
        payload.get("generatedAtUtc"), label=f"{label} generatedAtUtc"
    )


def validate_stable_page(
    payload: Any,
    *,
    expected: int,
    label: str,
) -> None:
    if not isinstance(payload, dict):
        raise ParityLabError(f"{label} is not an object")
    if payload.get("expected") != expected or payload.get("stable") is not True:
        raise ParityLabError(f"{label} does not prove stable page {expected}")
    required_samples = payload.get("requiredSamples")
    samples = payload.get("samples")
    if not isinstance(required_samples, int) or required_samples < 2:
        raise ParityLabError(f"{label} has an invalid stable-sample count")
    if not isinstance(samples, list) or len(samples) < required_samples:
        raise ParityLabError(f"{label} has too few page samples")
    tail = samples[-required_samples:]
    if any(not isinstance(row, dict) or row.get("value") != expected for row in tail):
        raise ParityLabError(f"{label} stable tail does not match page {expected}")


def validate_save_corpus(payload: Any, *, label: str) -> None:
    if not isinstance(payload, dict):
        raise ParityLabError(f"{label} is not an object")
    root = pathlib.Path(str(payload.get("root", "")))
    files = payload.get("files")
    if not root.is_dir() or not isinstance(files, list):
        raise ParityLabError(f"{label} root/files are invalid")
    if payload.get("fileCount") != len(files):
        raise ParityLabError(f"{label} file count does not close")
    canonical_rows: list[str] = []
    total_bytes = 0
    previous_key: str | None = None
    for index, row in enumerate(files):
        if not isinstance(row, dict):
            raise ParityLabError(f"{label} row {index} is not an object")
        relative = row.get("relativePath")
        size = row.get("bytes")
        sha256 = row.get("sha256")
        last_write = row.get("lastWriteUtc")
        if (
            not isinstance(relative, str)
            or not isinstance(size, int)
            or not isinstance(sha256, str)
            or not isinstance(last_write, str)
            or "\\" in relative
            or pathlib.PurePosixPath(relative).is_absolute()
            or ".." in pathlib.PurePosixPath(relative).parts
        ):
            raise ParityLabError(f"{label} row {index} is malformed")
        key = relative.casefold()
        if previous_key is not None and key < previous_key:
            raise ParityLabError(f"{label} rows are not sorted")
        previous_key = key
        current = root.joinpath(*pathlib.PurePosixPath(relative).parts)
        if not current.is_file():
            raise ParityLabError(f"{label} file is missing: {current}")
        facts = artifact_facts(current, f"{label} file")
        if facts["bytes"] != size or facts["sha256"].upper() != sha256.upper():
            raise ParityLabError(f"{label} file facts drifted: {current}")
        total_bytes += size
        canonical_rows.append(f"{relative}\t{size}\t{sha256}\t{last_write}")
    if payload.get("totalBytes") != total_bytes:
        raise ParityLabError(f"{label} byte count does not close")
    aggregate = hashlib.sha256("\n".join(canonical_rows).encode("utf-8")).hexdigest()
    if aggregate.upper() != str(payload.get("aggregateSha256", "")).upper():
        raise ParityLabError(f"{label} aggregate hash mismatch")


def validate_options_drcov_receipt_v2(
    payload: dict[str, Any],
    *,
    path: pathlib.Path,
) -> None:
    if payload.get("scenario") != "options-main-to-options.v1":
        raise ParityLabError(f"Unsupported drcov v2 scenario: {path}")
    if payload.get("campaignId") not in {"C1", "C2"}:
        raise ParityLabError(f"Invalid Options campaign in {path}")
    if not isinstance(payload.get("sequenceIndex"), int):
        raise ParityLabError(f"Invalid Options sequence index in {path}")
    sequence = int(payload["sequenceIndex"])
    if not 1 <= sequence <= 6:
        raise ParityLabError(f"Options sequence index is out of range in {path}")
    expected_tokens = {
        "C1": ("B1", "A1", "A2", "B2", "B3", "A3"),
        "C2": ("A4", "B4", "B5", "A5", "A6", "B6"),
    }
    expected_token = expected_tokens[payload["campaignId"]][sequence - 1]
    if payload.get("orderToken") != expected_token:
        raise ParityLabError(f"Options order token disagrees with sequence in {path}")
    expected_role = "baseline" if expected_token.startswith("B") else "action"
    if payload.get("role") != expected_role:
        raise ParityLabError(f"Options role disagrees with order token in {path}")
    if payload.get("protocolVersion") != "bea-options-drcov-protocol.v1":
        raise ParityLabError(f"Unknown Options protocol in {path}")
    protocol = payload.get("protocol")
    if not isinstance(protocol, dict):
        raise ParityLabError(f"Options protocol payload is missing in {path}")
    protocol_text = json.dumps(protocol, separators=(",", ":"), ensure_ascii=False)
    if hashlib.sha256(protocol_text.encode("utf-8")).hexdigest().upper() != str(
        payload.get("protocolSha256", "")
    ).upper():
        raise ParityLabError(f"Options protocol hash mismatch in {path}")
    requested_seconds = payload.get("requestedCaptureSeconds")
    game_arguments = payload.get("gameArguments")
    if (
        not isinstance(requested_seconds, int)
        or requested_seconds < 5
        or not isinstance(game_arguments, list)
        or any(not isinstance(value, str) for value in game_arguments)
    ):
        raise ParityLabError(f"Options timing/arguments are malformed in {path}")
    expected_protocol = {
        "version": "bea-options-drcov-protocol.v1",
        "scenario": "options-main-to-options.v1",
        "activePageAddress": "0x0089D950",
        "cursorXAddress": "0x0089BDA8",
        "cursorYAddress": "0x0089BDA4",
        "mouseGateAddress": "0x0089BDF0",
        "clickToStartPage": 12,
        "mainMenuPage": 0,
        "optionsPage": 17,
        "sharedClick": {"x": 320, "y": 240},
        "optionsCursor": {"x": 219, "y": 404},
        "pageStableSamples": 4,
        "pageSampleIntervalMilliseconds": 125,
        "mainMenuSettleMilliseconds": 1000,
        "observationSeconds": requested_seconds,
        "gameArguments": game_arguments,
        "actionCanaries": [
            "0x004623E0",
            "0x0051F7E0",
            "0x0051F6D0",
        ],
        "sharedCanaries": [
            "0x0051B660",
            "0x00464520",
            "0x00462D40",
        ],
        "campaignSchedules": {
            "C1": ["B1", "A1", "A2", "B2", "B3", "A3"],
            "C2": ["A4", "B4", "B5", "A5", "A6", "B6"],
        },
    }
    if protocol != expected_protocol:
        raise ParityLabError(f"Options protocol contract drift in {path}")

    artifacts = payload.get("artifacts")
    if not isinstance(artifacts, dict):
        raise ParityLabError(f"Options artifact facts are missing in {path}")
    for before_key, after_key, label in (
        ("targetBefore", "targetAfter", "target"),
        ("drrunBefore", "drrunAfter", "drrun"),
        ("recorderBefore", "recorderAfter", "recorder"),
        ("inputSenderBefore", "inputSenderAfter", "input sender"),
    ):
        before = validate_embedded_file_facts(
            artifacts.get(before_key), label=f"{label} before"
        )
        after = validate_embedded_file_facts(
            artifacts.get(after_key), label=f"{label} after"
        )
        if before != after:
            raise ParityLabError(f"{label} changed during capture: {path}")
    if (
        windows_path_key(payload.get("targetPath", ""))
        != windows_path_key(artifacts["targetBefore"]["path"])
        or str(payload.get("targetSha256", "")).upper()
        != artifacts["targetBefore"]["sha256"].upper()
        or windows_path_key(payload.get("drrunPath", ""))
        != windows_path_key(artifacts["drrunBefore"]["path"])
        or str(payload.get("drrunSha256", "")).upper()
        != artifacts["drrunBefore"]["sha256"].upper()
        or payload.get("targetUnchanged") is not True
    ):
        raise ParityLabError(f"Options top-level artifact identity drift in {path}")
    if pathlib.Path(str(payload.get("workingDirectory", ""))).resolve() != pathlib.Path(
        artifacts["targetBefore"]["path"]
    ).resolve().parent:
        raise ParityLabError(f"Options working directory mismatch in {path}")
    if (
        payload.get("tool") != "DynamoRIO drcov"
        or not isinstance(payload.get("toolVersion"), str)
        or not payload["toolVersion"]
        or payload.get("gameArguments") != protocol["gameArguments"]
        or payload.get("requestedCaptureSeconds") != protocol["observationSeconds"]
    ):
        raise ParityLabError(f"Options tool/timing identity is incomplete in {path}")

    precondition = payload.get("precondition")
    if not isinstance(precondition, dict) or precondition.get("passed") is not True:
        raise ParityLabError(f"Options precondition did not pass in {path}")
    if precondition.get("viewport") != {"width": 640, "height": 480}:
        raise ParityLabError(f"Options viewport is not 640x480 in {path}")
    contract = precondition.get("contract")
    if not isinstance(contract, dict):
        raise ParityLabError(f"Options precondition contract is missing in {path}")
    expected_contract = {
        "activePageAddress": "0x0089D950",
        "clickToStartPage": 12,
        "mainMenuPage": 0,
        "sharedClick": {"x": 320, "y": 240},
        "optionsCursor": {"x": 219, "y": 404},
        "stableSamples": 4,
        "sampleIntervalMilliseconds": 125,
        "settleMilliseconds": 1000,
    }
    if contract != expected_contract:
        raise ParityLabError(f"Options precondition contract drift in {path}")
    validate_stable_page(
        precondition.get("startPage"), expected=12, label=f"{path} start page"
    )
    validate_stable_page(
        precondition.get("mainPage"), expected=0, label=f"{path} main page"
    )
    validate_stable_page(
        precondition.get("settledMainPage"),
        expected=0,
        label=f"{path} settled main page",
    )
    if precondition.get("settledCursor") != {"x": 219, "y": 404, "mouseGate": 0}:
        raise ParityLabError(f"Options cursor precondition drift in {path}")
    shared_click_facts = validate_embedded_file_facts(
        precondition.get("sharedClickReceipt"),
        label=f"{path} sharedClickReceipt",
    )
    options_cursor_facts = validate_embedded_file_facts(
        precondition.get("optionsCursorReceipt"),
        label=f"{path} optionsCursorReceipt",
    )

    outcome = payload.get("outcome")
    expected_page = 0 if expected_role == "baseline" else 17
    if not isinstance(outcome, dict) or outcome.get("passed") is not True:
        raise ParityLabError(f"Options outcome did not pass in {path}")
    if outcome.get("expectedPage") != expected_page:
        raise ParityLabError(f"Options final page contract mismatch in {path}")
    validate_stable_page(
        outcome.get("initialPage"),
        expected=expected_page,
        label=f"{path} initial outcome",
    )
    validate_stable_page(
        outcome.get("finalPage"),
        expected=expected_page,
        label=f"{path} final outcome",
    )
    observation_samples = outcome.get("observationSamples")
    if not isinstance(observation_samples, list) or not observation_samples:
        raise ParityLabError(f"Options observation samples are missing in {path}")
    if any(
        not isinstance(row, dict) or row.get("value") != expected_page
        for row in observation_samples
    ):
        raise ParityLabError(f"Options page changed during observation in {path}")
    action_input = outcome.get("actionInputReceipt")
    if expected_role == "action":
        action_input_facts = validate_embedded_file_facts(
            action_input, label=f"{path} isolated action input"
        )
    elif action_input is not None:
        raise ParityLabError(f"Options baseline carries an action receipt: {path}")
    else:
        action_input_facts = None

    corpus = payload.get("corpus")
    if not isinstance(corpus, dict) or corpus.get("unchanged") is not True:
        raise ParityLabError(f"Options corpus changed during capture: {path}")
    for before_key, after_key, label in (
        ("defaultOptionsBefore", "defaultOptionsAfter", "default options"),
        ("saveCorpusBefore", "saveCorpusAfter", "save corpus"),
    ):
        before = corpus.get(before_key)
        after = corpus.get(after_key)
        if not isinstance(before, dict) or before != after:
            raise ParityLabError(f"{label} changed during capture: {path}")
    validate_embedded_file_facts(
        corpus["defaultOptionsBefore"], label=f"{path} default options"
    )
    validate_save_corpus(corpus["saveCorpusBefore"], label=f"{path} save corpus")

    process = payload.get("process")
    if not isinstance(process, dict):
        raise ParityLabError(f"Options process facts are missing in {path}")
    target_process_id = process.get("targetProcessId")
    drrun_process_id = process.get("drrunProcessId")
    target_hwnd = process.get("targetHwndHex")
    if (
        process.get("moduleBase") != "0x00400000"
        or not isinstance(target_process_id, int)
        or target_process_id <= 0
        or not isinstance(drrun_process_id, int)
        or drrun_process_id <= 0
        or target_process_id == drrun_process_id
        or not isinstance(process.get("targetParentProcessId"), int)
        or process["targetParentProcessId"] <= 0
        or process.get("targetDescendsFromDrrun") is not True
        or not isinstance(target_hwnd, str)
        or not target_hwnd.lower().startswith("0x")
        or process.get("targetExitCode") != 0
        or process.get("drrunExitCode") != 0
        or process.get("observationCompleted") is not True
        or process.get("guestExitedBeforeWindow") is not False
        or process.get("forcedTermination") is not False
    ):
        raise ParityLabError(f"Options process outcome is unhealthy in {path}")
    started = parse_utc_timestamp(
        payload.get("startedAtUtc"), label=f"{path} startedAtUtc"
    )
    finished = parse_utc_timestamp(
        payload.get("finishedAtUtc"), label=f"{path} finishedAtUtc"
    )
    process_started = parse_utc_timestamp(
        process.get("startedAtUtc"), label=f"{path} process.startedAtUtc"
    )
    appeared = parse_utc_timestamp(
        process.get("gameAppearedAtUtc"), label=f"{path} gameAppearedAtUtc"
    )
    common_epoch = parse_utc_timestamp(
        precondition.get("commonEpochAtUtc"), label=f"{path} commonEpochAtUtc"
    )
    observation_started = parse_utc_timestamp(
        process.get("observationStartedAtUtc"),
        label=f"{path} observationStartedAtUtc",
    )
    observation_end = parse_utc_timestamp(
        process.get("observationEndAtUtc"), label=f"{path} observationEndAtUtc"
    )
    if not (
        started == process_started
        and started <= appeared <= common_epoch <= observation_started
        < observation_end <= finished
    ):
        raise ParityLabError(f"Options capture timestamps are inconsistent in {path}")
    observed_seconds = (observation_end - observation_started).total_seconds()
    if abs(observed_seconds - requested_seconds) > 0.001:
        raise ParityLabError(f"Options observation duration drift in {path}")
    sample_times = [
        parse_utc_timestamp(row.get("atUtc"), label=f"{path} observation sample")
        for row in observation_samples
    ]
    if sample_times != sorted(sample_times):
        raise ParityLabError(f"Options observation samples are out of order in {path}")
    if (
        sample_times[0] < observation_started - dt.timedelta(milliseconds=250)
        or sample_times[-1] > observation_end + dt.timedelta(milliseconds=250)
        or sample_times[-1] - sample_times[0]
        < dt.timedelta(seconds=requested_seconds - 0.5)
    ):
        raise ParityLabError(f"Options observation samples do not span the window in {path}")
    validate_window_input_receipt(
        shared_click_facts,
        expected_kind="click",
        expected_x=320,
        expected_y=240,
        target_process_id=target_process_id,
        target_hwnd=target_hwnd,
        target_path=payload["targetPath"],
        working_directory=payload["workingDirectory"],
        label=f"{path} shared click",
    )
    validate_window_input_receipt(
        options_cursor_facts,
        expected_kind="move",
        expected_x=219,
        expected_y=404,
        target_process_id=target_process_id,
        target_hwnd=target_hwnd,
        target_path=payload["targetPath"],
        working_directory=payload["workingDirectory"],
        label=f"{path} Options cursor",
    )
    if action_input_facts is not None:
        validate_options_click_receipt(
            action_input_facts,
            target_process_id=target_process_id,
            target_hwnd=target_hwnd,
            label=f"{path} isolated action input",
        )
    cleanup = payload.get("cleanup")
    if not isinstance(cleanup, dict) or (
        cleanup.get("matchingProcessScanPerformed") is not True
        or cleanup.get("extraMatchingTargetsDetected") != 0
        or cleanup.get("extraMatchingDrrunsDetected") != 0
        or cleanup.get("targetSurvivorCount") != 0
        or cleanup.get("drrunSurvivorCount") != 0
        or cleanup.get("problems") != []
    ):
        raise ParityLabError(f"Options cleanup is unhealthy in {path}")
    if payload.get("failure") is not None:
        raise ParityLabError(f"Options receipt carries a failure in {path}")


def options_drcov_comparison_projection(payload: dict[str, Any]) -> dict[str, Any]:
    artifacts = payload["artifacts"]
    corpus = payload["corpus"]
    precondition = payload["precondition"]
    return {
        "scenario": payload["scenario"],
        "protocolVersion": payload["protocolVersion"],
        "protocolSha256": payload["protocolSha256"],
        "protocol": payload["protocol"],
        "targetPath": payload["targetPath"],
        "targetSha256": payload["targetSha256"],
        "drrunPath": payload["drrunPath"],
        "drrunSha256": payload["drrunSha256"],
        "tool": payload["tool"],
        "toolVersion": payload["toolVersion"],
        "gameArguments": payload["gameArguments"],
        "workingDirectory": payload["workingDirectory"],
        "requestedCaptureSeconds": payload["requestedCaptureSeconds"],
        "target": artifacts["targetBefore"],
        "drrun": artifacts["drrunBefore"],
        "recorder": artifacts["recorderBefore"],
        "inputSender": artifacts["inputSenderBefore"],
        "preconditionContract": precondition["contract"],
        "viewport": precondition["viewport"],
        "defaultOptions": corpus["defaultOptionsBefore"],
        "saveCorpus": corpus["saveCorpusBefore"],
    }


def load_drcov_receipt(
    path: pathlib.Path,
    *,
    expected_role: str,
    expected_log: pathlib.Path,
    log_facts: dict[str, Any],
    target_facts: dict[str, Any],
) -> dict[str, Any]:
    facts = artifact_facts(path, f"drcov-{expected_role}-receipt")
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    assert_artifact_unchanged(path, facts)
    if not isinstance(payload, dict):
        raise ParityLabError(f"drcov receipt is not an object: {path}")
    required = {
        "schemaVersion": str,
        "runId": str,
        "role": str,
        "logPath": str,
        "logSha256": str,
        "targetSha256": str,
        "captureComplete": bool,
        "actionStatus": str,
        "tool": str,
        "toolVersion": str,
        "actionProtocol": str,
    }
    for key, expected_type in required.items():
        if not isinstance(payload.get(key), expected_type):
            raise ParityLabError(
                f"drcov receipt {path} has invalid or missing {key}"
            )
    schema = payload["schemaVersion"]
    if schema not in {
        "bea-drcov-capture-receipt.v1",
        "bea-drcov-capture-receipt.v2",
    }:
        raise ParityLabError(f"Unsupported drcov receipt schema: {path}")
    if payload["role"] != expected_role:
        raise ParityLabError(
            f"drcov receipt role mismatch: {payload['role']} != {expected_role}"
        )
    if windows_path_key(payload["logPath"]) != windows_path_key(expected_log.resolve()):
        raise ParityLabError(f"drcov receipt log path mismatch: {path}")
    if payload["logSha256"].upper() != str(log_facts["sha256"]).upper():
        raise ParityLabError(f"drcov receipt log hash mismatch: {path}")
    if payload["targetSha256"].upper() != str(target_facts["sha256"]).upper():
        raise ParityLabError(f"drcov receipt target hash mismatch: {path}")
    if payload["captureComplete"] is not True:
        raise ParityLabError(f"drcov receipt does not mark capture complete: {path}")
    # Schema v1 records what the launcher or its caller said about delivery,
    # but carries no independently verifiable observation artifact. Retain
    # legacy values for old-capture readability; never promote them to proof.
    allowed_status = {
        "NONE_BASELINE",
        "POSTED_NOT_ACKNOWLEDGED",
        "OBSERVED",
        "MECHANICALLY_VERIFIED",
    }
    if payload["actionStatus"] not in allowed_status:
        raise ParityLabError(f"Unknown drcov actionStatus in {path}")
    if expected_role == "baseline" and payload["actionStatus"] != "NONE_BASELINE":
        raise ParityLabError(f"Baseline receipt carries an action status: {path}")
    if expected_role == "action" and payload["actionStatus"] == "NONE_BASELINE":
        raise ParityLabError(f"Action receipt carries baseline status: {path}")
    if schema == "bea-drcov-capture-receipt.v2":
        validate_options_drcov_receipt_v2(payload, path=path)
        action_verified = expected_role == "action"
        verification_source = (
            "STABLE_OPTIONS_PAGE_V2"
            if action_verified
            else "NONE_BASELINE_V2"
        )
    else:
        action_verified = False
        verification_source = "NONE_STRUCTURED_IN_V1"
    return {
        **facts,
        "payload": payload,
        "actionVerified": action_verified,
        "actionVerificationSource": verification_source,
    }


def classify_candidate(
    *,
    baseline_support: int,
    action_support: int,
    baseline_runs: int,
    action_runs: int,
    any_novel: int,
    stable_novel: int,
    scorable: bool,
) -> str:
    if not scorable:
        return "UNSCORED_MAPPING"
    if action_support == action_runs and baseline_support == 0:
        return "ACTION_ONLY_STABLE_FUNCTION"
    if stable_novel > 0:
        return "SHARED_WITH_STABLE_ACTION_BLOCKS"
    if action_support > 0 and baseline_support == 0:
        return "ACTION_ONLY_UNSTABLE_FUNCTION"
    left = action_support * baseline_runs
    right = baseline_support * action_runs
    if left > right:
        return "ACTION_ENRICHED_RECURRENCE"
    if any_novel > 0:
        return "SHARED_WITH_UNSTABLE_ACTION_BLOCKS"
    return "SHARED_OR_NO_OBSERVED_DELTA"


CLASS_PRIORITY = {
    "ACTION_ONLY_STABLE_FUNCTION": 0,
    "SHARED_WITH_STABLE_ACTION_BLOCKS": 1,
    "ACTION_ONLY_UNSTABLE_FUNCTION": 2,
    "ACTION_ENRICHED_RECURRENCE": 3,
    "SHARED_WITH_UNSTABLE_ACTION_BLOCKS": 4,
    "UNSCORED_MAPPING": 5,
    "SHARED_OR_NO_OBSERVED_DELTA": 6,
}


def run_coverage_diff(args: argparse.Namespace) -> int:
    if len(args.baseline) != len(args.baseline_receipt):
        raise ParityLabError("Every --baseline log needs one --baseline-receipt")
    if len(args.action) != len(args.action_receipt):
        raise ParityLabError("Every --action log needs one --action-receipt")
    if getattr(args, "options_contract", False) and (
        args.scenario != "options-main-to-options.v1"
    ):
        raise ParityLabError(
            "The Options contract requires scenario options-main-to-options.v1"
        )

    output = create_output_dir(pathlib.Path(args.out))
    database_path = output / "coverage.sqlite"
    connection = open_database(database_path)
    connection.execute("INSERT INTO meta(key, value) VALUES (?, ?)", ("schema", COVERAGE_SCHEMA))
    connection.execute("INSERT INTO meta(key, value) VALUES (?, ?)", ("scenario", args.scenario))

    ghidra_path = pathlib.Path(args.ghidra)
    body_ranges_path = pathlib.Path(args.body_ranges) if args.body_ranges else None
    call_edges_path = pathlib.Path(args.call_edges) if args.call_edges else None
    graph_receipt_path = (
        pathlib.Path(args.graph_receipt) if args.graph_receipt else None
    )
    if bool(call_edges_path) != bool(graph_receipt_path):
        raise ParityLabError(
            "--call-edges and --graph-receipt must be supplied together"
        )
    if call_edges_path and not body_ranges_path:
        raise ParityLabError("--call-edges requires --body-ranges")
    functions = load_functions(ghidra_path, body_ranges_path)
    functions_by_address = {function.address: function for function in functions}
    interval_index = FunctionIntervalIndex(functions)
    edges = load_call_edges(call_edges_path)
    graph_receipt_facts = (
        validate_graph_receipt(
            graph_receipt_path,
            body_ranges_path,
            call_edges_path,
            functions,
            edges,
        )
        if graph_receipt_path and body_ranges_path and call_edges_path
        else None
    )
    image_base = parse_int(args.image_base, field="image base")
    static_path = pathlib.Path(args.static_exe)
    target_path = pathlib.Path(args.target_exe)
    derivation = image_derivation(static_path, target_path)
    static_facts = derivation["static"]
    target_facts = derivation["target"]
    if image_base != static_facts["pe"]["imageBaseInteger"]:
        raise ParityLabError(
            f"--image-base 0x{image_base:08X} disagrees with static PE "
            f"{static_facts['pe']['imageBase']}"
        )
    if body_ranges_path:
        range_metadata = read_tsv_metadata(body_ranges_path)
        imported_md5 = range_metadata.get("executableMd5", "").lower()
        if not imported_md5:
            raise ParityLabError(
                "Exact body-range TSV lacks Ghidra executableMd5 metadata"
            )
        if imported_md5 != static_facts["md5"]:
            raise ParityLabError(
                f"Ghidra/static specimen mismatch: {imported_md5} != "
                f"{static_facts['md5']}"
            )
        exported_base = parse_int(
            range_metadata.get("imageBase"), field="Ghidra imageBase"
        )
        if exported_base != image_base:
            raise ParityLabError("Ghidra body ranges use a different image base")

    input_artifacts = [
        artifact_facts(ghidra_path, "ghidra-function-inventory"),
        static_facts,
        target_facts,
    ]
    if body_ranges_path:
        input_artifacts.append(artifact_facts(body_ranges_path, "ghidra-body-ranges"))
    if call_edges_path:
        input_artifacts.append(artifact_facts(call_edges_path, "ghidra-call-edges"))
    if graph_receipt_facts:
        input_artifacts.append(graph_receipt_facts)
    for artifact in input_artifacts:
        add_artifact(connection, artifact)
    for function in functions:
        connection.execute(
            """
            INSERT INTO coverage_function(
                function_address, function_rva, name, name_source, tags,
                body_min, body_max, body_bytes, body_range_count,
                range_quality, naming_risk
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                function.address,
                function.address - image_base,
                function.name,
                function.name_source,
                function.tags,
                function.body_min,
                function.body_max,
                function.body_bytes,
                function.body_range_count,
                function.range_quality,
                naming_risk(function),
            ),
        )

    run_specs: list[tuple[str, pathlib.Path, pathlib.Path]] = [
        *[
            ("baseline", pathlib.Path(log), pathlib.Path(receipt))
            for log, receipt in zip(args.baseline, args.baseline_receipt)
        ],
        *[
            ("action", pathlib.Path(log), pathlib.Path(receipt))
            for log, receipt in zip(args.action, args.action_receipt)
        ],
    ]
    run_block_sets: dict[int, set[int]] = {}
    run_function_blocks: dict[int, dict[int, set[int]]] = {}
    run_roles: dict[int, str] = {}
    run_receipts: dict[int, dict[str, Any]] = {}
    run_rows: list[dict[str, Any]] = []
    block_json_rows: list[dict[str, Any]] = []
    receipt_rows: list[dict[str, Any]] = []
    observed_sizes: dict[int, set[int]] = defaultdict(set)

    for role, path, receipt_path in run_specs:
        facts = artifact_facts(path, f"drcov-{role}")
        receipt = load_drcov_receipt(
            receipt_path,
            expected_role=role,
            expected_log=path,
            log_facts=facts,
            target_facts=target_facts,
        )
        input_artifacts.append(facts)
        input_artifacts.append(
            {key: receipt[key] for key in ("kind", "path", "bytes", "sha256")}
        )
        artifact_id = add_artifact(connection, facts, schema_version="drcov-text")
        add_artifact(
            connection,
            receipt,
            schema_version=receipt["payload"]["schemaVersion"],
            health="COMPLETE",
        )
        log = parse_drcov(path)
        assert_artifact_unchanged(path, facts)
        module_blocks, modules = select_module_blocks(log, args.module)
        expected_target_path = windows_path_key(target_path.resolve())
        bad_paths = [
            module.path
            for module in modules
            if windows_path_key(module.path) != expected_target_path
        ]
        if bad_paths:
            raise ParityLabError(
                f"drcov module path does not identify the hashed target in {path}: "
                + " | ".join(bad_paths)
            )
        bad_timestamps = [
            module.timestamp
            for module in modules
            if module.timestamp is not None
            and module.timestamp != target_facts["pe"]["timestampInteger"]
        ]
        if bad_timestamps:
            raise ParityLabError(f"drcov module timestamp mismatch in {path}")
        preferred_bases = {module.preferred_base for module in modules if module.preferred_base is not None}
        preferred_base = next(iter(preferred_bases)) if len(preferred_bases) == 1 else None
        if preferred_base != image_base:
            raise ParityLabError(
                f"drcov preferred base mismatch in {path}: {preferred_base!r}"
            )
        module_paths = sorted({module.path for module in modules})
        cursor = connection.execute(
            """
            INSERT INTO coverage_run(
                role, campaign_id, sequence_index, artifact_id,
                drcov_version, flavor, module_table_version,
                module_path, module_preferred_base, declared_blocks, unique_module_blocks
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                role,
                receipt["payload"].get("campaignId"),
                receipt["payload"].get("sequenceIndex"),
                artifact_id,
                log.version,
                log.flavor,
                log.module_table_version,
                " | ".join(module_paths),
                preferred_base,
                log.declared_bb_count,
                len(module_blocks),
            ),
        )
        run_id = int(cursor.lastrowid)
        run_roles[run_id] = role
        run_receipts[run_id] = receipt
        run_block_sets[run_id] = {rva for rva, _ in module_blocks}
        per_function: dict[int, set[int]] = defaultdict(set)
        for rva, size in module_blocks:
            observed_sizes[rva].add(size)
            va = image_base + rva
            function, quality = interval_index.lookup(va)
            function_address = function.address if function else None
            if function:
                per_function[function.address].add(rva)
            connection.execute(
                """
                INSERT INTO coverage_block(run_id, rva, size, va, function_address, mapping_quality)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (run_id, rva, size, va, function_address, quality),
            )
            block_json_rows.append(
                {
                    "runId": run_id,
                    "role": role,
                    "rva": f"0x{rva:08X}",
                    "va": f"0x{va:08X}",
                    "size": size,
                    "functionAddress": (
                        f"0x{function_address:08X}" if function_address is not None else None
                    ),
                    "functionName": function.name if function else None,
                    "mappingQuality": quality,
                }
            )
        run_function_blocks[run_id] = dict(per_function)
        for address, block_set in per_function.items():
            connection.execute(
                """
                INSERT INTO coverage_observation(run_id, function_address, block_count)
                VALUES (?, ?, ?)
                """,
                (run_id, address, len(block_set)),
            )
        run_rows.append(
            {
                "runId": run_id,
                "role": role,
                "campaignId": receipt["payload"].get("campaignId"),
                "sequenceIndex": receipt["payload"].get("sequenceIndex"),
                "orderToken": receipt["payload"].get("orderToken"),
                "path": str(path.resolve()),
                "sha256": facts["sha256"],
                "drcovVersion": log.version,
                "moduleTableVersion": log.module_table_version,
                "declaredAllModuleBlocks": log.declared_bb_count,
                "uniqueSelectedModuleBlocks": len(module_blocks),
                "selectedModulePaths": module_paths,
                "selectedModulePreferredBase": (
                    f"0x{preferred_base:08X}" if preferred_base is not None else None
                ),
                "receipt": {
                    "path": receipt["path"],
                    "sha256": receipt["sha256"],
                    "runId": receipt["payload"]["runId"],
                    "actionStatus": receipt["payload"]["actionStatus"],
                    "actionVerified": receipt["actionVerified"],
                    "actionVerificationSource": receipt[
                        "actionVerificationSource"
                    ],
                    "actionProtocol": receipt["payload"]["actionProtocol"],
                },
            }
        )
        receipt_rows.append(receipt)

    conflicting_sizes = {
        rva: sizes for rva, sizes in observed_sizes.items() if len(sizes) > 1
    }
    if conflicting_sizes:
        first_rva = min(conflicting_sizes)
        raise ParityLabError(
            f"drcov size conflict at RVA 0x{first_rva:08X}: "
            f"{sorted(conflicting_sizes[first_rva])}"
        )

    baseline_run_ids = [run_id for run_id, role in run_roles.items() if role == "baseline"]
    action_run_ids = [run_id for run_id, role in run_roles.items() if role == "action"]
    baseline_union = set().union(*(run_block_sets[run_id] for run_id in baseline_run_ids))
    action_union = set().union(*(run_block_sets[run_id] for run_id in action_run_ids))
    action_intersection = set.intersection(
        *(run_block_sets[run_id] for run_id in action_run_ids)
    )
    stable_novel_global = action_intersection - baseline_union
    any_novel_global = action_union - baseline_union
    options_contract = bool(getattr(args, "options_contract", False))
    campaign_sets: dict[str, dict[str, Any]] = {}
    campaign_delta_rows: list[dict[str, Any]] = []
    if options_contract:
        if len(run_receipts) != 12:
            raise ParityLabError(
                "The Options contract requires exactly 12 runs: two 3+3 campaigns"
            )
        if any(
            row["payload"].get("schemaVersion")
            != "bea-drcov-capture-receipt.v2"
            for row in run_receipts.values()
        ):
            raise ParityLabError("The Options contract requires only v2 receipts")
        projections = [
            options_drcov_comparison_projection(row["payload"])
            for row in run_receipts.values()
        ]
        reference_projection = projections[0]
        if any(row != reference_projection for row in projections[1:]):
            raise ParityLabError(
                "Options target/tool/protocol/precondition/corpus facts drift across runs"
            )
        grouped: dict[str, list[tuple[int, dict[str, Any]]]] = defaultdict(list)
        for run_id, receipt in run_receipts.items():
            grouped[str(receipt["payload"]["campaignId"])].append((run_id, receipt))
        if set(grouped) != {"C1", "C2"}:
            raise ParityLabError("Options receipts must contain campaigns C1 and C2")
        expected_roles = {
            "C1": ("baseline", "action", "action", "baseline", "baseline", "action"),
            "C2": ("action", "baseline", "baseline", "action", "action", "baseline"),
        }
        for campaign_id in ("C1", "C2"):
            ordered = sorted(
                grouped[campaign_id],
                key=lambda item: int(item[1]["payload"]["sequenceIndex"]),
            )
            indices = [
                int(receipt["payload"]["sequenceIndex"]) for _, receipt in ordered
            ]
            roles = [str(receipt["payload"]["role"]) for _, receipt in ordered]
            if indices != list(range(1, 7)):
                raise ParityLabError(
                    f"Options {campaign_id} sequence indices are incomplete or duplicated"
                )
            if tuple(roles) != expected_roles[campaign_id]:
                raise ParityLabError(
                    f"Options {campaign_id} order is not counterbalanced as specified"
                )
            starts = [
                parse_utc_timestamp(
                    receipt["payload"]["startedAtUtc"],
                    label=f"Options {campaign_id} sequence start",
                )
                for _, receipt in ordered
            ]
            finishes = [
                parse_utc_timestamp(
                    receipt["payload"]["finishedAtUtc"],
                    label=f"Options {campaign_id} sequence finish",
                )
                for _, receipt in ordered
            ]
            if any(
                finishes[index] > starts[index + 1]
                for index in range(len(ordered) - 1)
            ):
                raise ParityLabError(
                    f"Options {campaign_id} receipts overlap or are not chronological"
                )
            campaign_baselines = [
                run_id for run_id, receipt in ordered
                if receipt["payload"]["role"] == "baseline"
            ]
            campaign_actions = [
                run_id for run_id, receipt in ordered
                if receipt["payload"]["role"] == "action"
            ]
            if len(campaign_baselines) != 3 or len(campaign_actions) != 3:
                raise ParityLabError(
                    f"Options {campaign_id} does not contain exactly 3+3 runs"
                )
            campaign_baseline_union = set().union(
                *(run_block_sets[run_id] for run_id in campaign_baselines)
            )
            campaign_action_union = set().union(
                *(run_block_sets[run_id] for run_id in campaign_actions)
            )
            campaign_action_intersection = set.intersection(
                *(run_block_sets[run_id] for run_id in campaign_actions)
            )
            campaign_stable = (
                campaign_action_intersection - campaign_baseline_union
            )
            campaign_any = campaign_action_union - campaign_baseline_union
            campaign_sets[campaign_id] = {
                "baselineRunIds": campaign_baselines,
                "actionRunIds": campaign_actions,
                "baselineUnion": campaign_baseline_union,
                "actionUnion": campaign_action_union,
                "actionIntersection": campaign_action_intersection,
                "stable": campaign_stable,
                "any": campaign_any,
            }
        durable = campaign_sets["C1"]["stable"] & campaign_sets["C2"]["stable"]
        if durable != stable_novel_global:
            raise ParityLabError(
                "Cross-campaign stable intersection disagrees with the global invariant"
            )
        for campaign_id, sets in campaign_sets.items():
            for rva in sorted(sets["any"]):
                function, mapping_quality = interval_index.lookup(image_base + rva)
                campaign_delta_rows.append(
                    {
                        "campaignId": campaign_id,
                        "rva": f"0x{rva:08X}",
                        "va": f"0x{image_base + rva:08X}",
                        "stableActionNovel": rva in sets["stable"],
                        "durableAcrossCampaigns": rva in durable,
                        "functionAddress": (
                            f"0x{function.address:08X}"
                            if function is not None else None
                        ),
                        "functionName": function.name if function is not None else None,
                        "mappingQuality": mapping_quality,
                    }
                )
    any_novel_by_function: dict[int, set[int]] = defaultdict(set)
    stable_novel_by_function: dict[int, set[int]] = defaultdict(set)
    delta_block_rows: list[dict[str, Any]] = []
    for rva in any_novel_global:
        function, mapping_quality = interval_index.lookup(image_base + rva)
        baseline_support = sum(
            1 for run_id in baseline_run_ids if rva in run_block_sets[run_id]
        )
        action_support = sum(
            1 for run_id in action_run_ids if rva in run_block_sets[run_id]
        )
        size = next(iter(observed_sizes[rva]))
        row = {
            "rva": f"0x{rva:08X}",
            "va": f"0x{image_base + rva:08X}",
            "size": size,
            "baselineSupport": baseline_support,
            "baselineRuns": len(baseline_run_ids),
            "actionSupport": action_support,
            "actionRuns": len(action_run_ids),
            "stableActionNovel": rva in stable_novel_global,
            "functionAddress": (
                f"0x{function.address:08X}" if function is not None else None
            ),
            "functionName": function.name if function is not None else None,
            "mappingQuality": mapping_quality,
        }
        delta_block_rows.append(row)
        connection.execute(
            """
            INSERT INTO coverage_delta_block(
                rva, size, va, baseline_support, action_support,
                stable_action_novel, function_address, mapping_quality
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                rva,
                size,
                image_base + rva,
                baseline_support,
                action_support,
                int(rva in stable_novel_global),
                function.address if function is not None else None,
                mapping_quality,
            ),
        )
        if function is not None:
            any_novel_by_function[function.address].add(rva)
            if rva in stable_novel_global:
                stable_novel_by_function[function.address].add(rva)
    delta_block_rows.sort(
        key=lambda row: (
            0 if row["stableActionNovel"] else 1,
            0 if row["mappingQuality"] in {"UNMAPPED", "AMBIGUOUS_OVERLAP"} else 1,
            row["rva"],
        )
    )

    caller_map: dict[int, list[CallEdge]] = defaultdict(list)
    callee_map: dict[int, list[CallEdge]] = defaultdict(list)
    for edge in edges:
        caller_map[edge.callee].append(edge)
        callee_map[edge.caller].append(edge)

    candidate_rows: list[dict[str, Any]] = []
    for function in functions:
        address = function.address
        baseline_support = sum(
            1 for run_id in baseline_run_ids if address in run_function_blocks[run_id]
        )
        action_support = sum(
            1 for run_id in action_run_ids if address in run_function_blocks[run_id]
        )
        # Map each novel block once through the interval index.  The previous
        # function-by-block scan was O(functions * novel blocks), which becomes
        # prohibitive on real whole-game coverage.
        any_novel = len(any_novel_by_function.get(address, ()))
        stable_novel = len(stable_novel_by_function.get(address, ()))
        if (
            baseline_support == 0
            and action_support == 0
            and not any_novel
            and not stable_novel
        ):
            continue
        scorable = function.range_quality in {
            "EXACT_GHIDRA_RANGES",
            "EXACT_CONTIGUOUS_INVENTORY",
        }
        classification = classify_candidate(
            baseline_support=baseline_support,
            action_support=action_support,
            baseline_runs=len(baseline_run_ids),
            action_runs=len(action_run_ids),
            any_novel=any_novel,
            stable_novel=stable_novel,
            scorable=scorable,
        )

        def edge_rows(items: Sequence[CallEdge], direction: str) -> list[dict[str, Any]]:
            rows: list[dict[str, Any]] = []
            for edge in sorted(items, key=lambda item: (-item.count, item.caller, item.callee)):
                other_address = edge.caller if direction == "caller" else edge.callee
                other = functions_by_address.get(other_address)
                rows.append(
                    {
                        "address": f"0x{other_address:08X}",
                        "name": other.name if other else None,
                        "callSiteCount": edge.count,
                    }
                )
            return rows

        callers = edge_rows(caller_map.get(address, []), "caller")
        callees = edge_rows(callee_map.get(address, []), "callee")
        candidate_rows.append(
            {
                "functionAddress": f"0x{address:08X}",
                "functionRva": f"0x{address - image_base:08X}",
                "name": function.name,
                "namingRisk": naming_risk(function),
                "rangeQuality": function.range_quality,
                "scorable": scorable,
                "classification": classification,
                "baselineSupport": baseline_support,
                "baselineRuns": len(baseline_run_ids),
                "actionSupport": action_support,
                "actionRuns": len(action_run_ids),
                "actionNovelBlocks": any_novel,
                "stableActionNovelBlocks": stable_novel,
                "bodyBytes": function.body_bytes,
                "callers": callers,
                "callees": callees,
            }
        )

    candidate_rows.sort(
        key=lambda row: (
            CLASS_PRIORITY[row["classification"]],
            0 if row["namingRisk"] == "LITERAL_FUN" else 1,
            -row["stableActionNovelBlocks"],
            -row["actionNovelBlocks"],
            -row["actionSupport"],
            row["functionAddress"],
        )
    )
    for ordinal, row in enumerate(candidate_rows, start=1):
        row["rankOrdinal"] = ordinal
        address = int(row["functionAddress"], 16)
        connection.execute(
            """
            INSERT INTO coverage_candidate(
                function_address, classification, scorable,
                baseline_support, action_support, baseline_runs, action_runs,
                action_novel_blocks, stable_action_novel_blocks, rank_ordinal,
                callers_json, callees_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                address,
                row["classification"],
                int(row["scorable"]),
                row["baselineSupport"],
                row["actionSupport"],
                row["baselineRuns"],
                row["actionRuns"],
                row["actionNovelBlocks"],
                row["stableActionNovelBlocks"],
                ordinal,
                json.dumps(row["callers"], sort_keys=True),
                json.dumps(row["callees"], sort_keys=True),
            ),
        )

    connection.commit()
    connection.execute("VACUUM")
    connection.close()

    write_jsonl(output / "blocks.jsonl", block_json_rows)
    write_jsonl(output / "delta-blocks.jsonl", delta_block_rows)
    write_jsonl(output / "functions.jsonl", candidate_rows)
    if options_contract:
        write_jsonl(
            output / "campaign-delta-blocks.jsonl",
            sorted(
                campaign_delta_rows,
                key=lambda row: (row["campaignId"], row["rva"]),
            ),
        )
    classification_counts = Counter(row["classification"] for row in candidate_rows)
    literal_fun_candidates = [
        row for row in candidate_rows if row["namingRisk"] == "LITERAL_FUN"
    ]
    unscorable_functions = sum(
        1
        for function in functions
        if function.range_quality not in {"EXACT_GHIDRA_RANGES", "EXACT_CONTIGUOUS_INVENTORY"}
    )
    stable_mapping_counts = Counter(
        row["mappingQuality"]
        for row in delta_block_rows
        if row["stableActionNovel"]
    )
    if sum(stable_mapping_counts.values()) != len(stable_novel_global):
        raise ParityLabError("Stable novel block mapping accounting does not close")
    run_ids = [row["payload"]["runId"] for row in receipt_rows]
    duplicate_run_ids = len(run_ids) != len(set(run_ids))
    log_paths = [
        windows_path_key(row["payload"]["logPath"]) for row in receipt_rows
    ]
    duplicate_log_paths = len(log_paths) != len(set(log_paths))
    run_hashes = [row["sha256"] for row in receipt_rows]
    duplicate_receipt_hashes = len(run_hashes) != len(set(run_hashes))
    log_hashes = [
        artifact["sha256"]
        for artifact in input_artifacts
        if str(artifact.get("kind", "")).startswith("drcov-")
        and not str(artifact.get("kind", "")).endswith("-receipt")
    ]
    duplicate_log_hashes = len(log_hashes) != len(set(log_hashes))
    receipt_actions_verified = all(
        row["actionVerified"]
        for row in receipt_rows
        if row["payload"]["role"] == "action"
    )
    action_canary_results: list[dict[str, Any]] = []
    for value in args.action_canary:
        address = parse_int(value, field="action canary")
        function = functions_by_address.get(address)
        if function is None:
            raise ParityLabError(
                f"Action canary is not a Ghidra function entry: 0x{address:08X}"
            )
        baseline_hits = sum(
            1 for run_id in baseline_run_ids
            if address - image_base in run_block_sets[run_id]
        )
        action_hits = sum(
            1 for run_id in action_run_ids
            if address - image_base in run_block_sets[run_id]
        )
        passed = baseline_hits == 0 and action_hits == len(action_run_ids)
        action_canary_results.append(
            {
                "address": f"0x{address:08X}",
                "name": function.name,
                "baselineHits": baseline_hits,
                "baselineRuns": len(baseline_run_ids),
                "actionHits": action_hits,
                "actionRuns": len(action_run_ids),
                "passed": passed,
            }
        )
    canaries_verify_actions = bool(action_canary_results) and all(
        row["passed"] for row in action_canary_results
    )
    shared_canary_results: list[dict[str, Any]] = []
    for value in args.shared_canary:
        address = parse_int(value, field="shared canary")
        function = functions_by_address.get(address)
        if function is None:
            raise ParityLabError(
                f"Shared canary is not a Ghidra function entry: 0x{address:08X}"
            )
        hits = sum(
            1 for run_id in run_roles
            if address - image_base in run_block_sets[run_id]
        )
        shared_canary_results.append(
            {
                "address": f"0x{address:08X}",
                "name": function.name,
                "hits": hits,
                "runs": len(run_roles),
                "passed": hits == len(run_roles),
            }
        )
    shared_canaries_pass = bool(shared_canary_results) and all(
        row["passed"] for row in shared_canary_results
    )
    campaign_summaries: list[dict[str, Any]] = []
    options_canaries_pass = False
    if options_contract:
        expected_action_canaries = {
            0x004623E0,
            0x0051F7E0,
            0x0051F6D0,
        }
        expected_shared_canaries = {
            0x0051B660,
            0x00464520,
            0x00462D40,
        }
        supplied_action_canaries = {
            parse_int(value, field="action canary") for value in args.action_canary
        }
        supplied_shared_canaries = {
            parse_int(value, field="shared canary") for value in args.shared_canary
        }
        if (
            supplied_action_canaries != expected_action_canaries
            or len(args.action_canary) != 3
        ):
            raise ParityLabError(
                "Options requires the exact three measured action-only canaries"
            )
        if (
            supplied_shared_canaries != expected_shared_canaries
            or len(args.shared_canary) != 3
        ):
            raise ParityLabError(
                "Options requires the exact three measured shared-setup canaries"
            )
        campaign_canaries_pass = True
        for campaign_id in ("C1", "C2"):
            sets = campaign_sets[campaign_id]
            campaign_action_canaries: list[dict[str, Any]] = []
            for address in sorted(expected_action_canaries):
                baseline_hits = sum(
                    1 for run_id in sets["baselineRunIds"]
                    if address - image_base in run_block_sets[run_id]
                )
                action_hits = sum(
                    1 for run_id in sets["actionRunIds"]
                    if address - image_base in run_block_sets[run_id]
                )
                passed = baseline_hits == 0 and action_hits == 3
                campaign_action_canaries.append(
                    {
                        "address": f"0x{address:08X}",
                        "baselineHits": baseline_hits,
                        "actionHits": action_hits,
                        "passed": passed,
                    }
                )
                campaign_canaries_pass = campaign_canaries_pass and passed
            campaign_shared_canaries: list[dict[str, Any]] = []
            campaign_run_ids = sets["baselineRunIds"] + sets["actionRunIds"]
            for address in sorted(expected_shared_canaries):
                hits = sum(
                    1 for run_id in campaign_run_ids
                    if address - image_base in run_block_sets[run_id]
                )
                passed = hits == 6
                campaign_shared_canaries.append(
                    {
                        "address": f"0x{address:08X}",
                        "hits": hits,
                        "runs": 6,
                        "passed": passed,
                    }
                )
                campaign_canaries_pass = campaign_canaries_pass and passed
            stable_mapping = Counter(
                interval_index.lookup(image_base + rva)[1]
                for rva in sets["stable"]
            )
            any_mapping = Counter(
                interval_index.lookup(image_base + rva)[1]
                for rva in sets["any"]
            )
            if sum(stable_mapping.values()) != len(sets["stable"]):
                raise ParityLabError(
                    f"Options {campaign_id} stable mapping accounting does not close"
                )
            if sum(any_mapping.values()) != len(sets["any"]):
                raise ParityLabError(
                    f"Options {campaign_id} novel mapping accounting does not close"
                )
            campaign_summaries.append(
                {
                    "campaignId": campaign_id,
                    "baselineRuns": 3,
                    "actionRuns": 3,
                    "baselineUnionBlockCount": len(sets["baselineUnion"]),
                    "actionUnionBlockCount": len(sets["actionUnion"]),
                    "actionIntersectionBlockCount": len(
                        sets["actionIntersection"]
                    ),
                    "anyActionNovelBlockCount": len(sets["any"]),
                    "stableActionNovelBlockCount": len(sets["stable"]),
                    "stableMappingCounts": dict(sorted(stable_mapping.items())),
                    "anyMappingCounts": dict(sorted(any_mapping.items())),
                    "actionCanaries": campaign_action_canaries,
                    "sharedCanaries": campaign_shared_canaries,
                }
            )
        options_canaries_pass = (
            campaign_canaries_pass
            and canaries_verify_actions
            and shared_canaries_pass
        )
    all_actions_verified = receipt_actions_verified or canaries_verify_actions
    comparison_ready = (
        len(baseline_run_ids) >= 2
        and len(action_run_ids) >= 2
        and unscorable_functions == 0
        and not duplicate_run_ids
        and not duplicate_receipt_hashes
        and not duplicate_log_paths
        and (options_contract or not duplicate_log_hashes)
        and all_actions_verified
    )
    if options_contract:
        comparison_ready = (
            comparison_ready
            and len(baseline_run_ids) == 6
            and len(action_run_ids) == 6
            and receipt_actions_verified
            and options_canaries_pass
        )
    comparison_status = (
        "COMPARABLE"
        if comparison_ready
        else ("UNSCORED" if options_contract else "CORRELATED")
    )
    status_connection = sqlite3.connect(database_path)
    try:
        status_connection.executemany(
            "INSERT OR REPLACE INTO meta(key, value) VALUES (?, ?)",
            [
                ("captureHealth", "COMPLETE"),
                ("comparability", comparison_status),
                ("targetSha256", target_facts["sha256"]),
                ("staticSpecimenSha256", static_facts["sha256"]),
            ],
        )
        status_connection.commit()
    finally:
        status_connection.close()
    manifest = {
        "schemaVersion": COVERAGE_SCHEMA,
        "toolVersion": TOOL_VERSION,
        "generatedAtUtc": utc_now(),
        "scenario": args.scenario,
        "question": args.question,
        "module": args.module,
        "imageBase": f"0x{image_base:08X}",
        "target": target_facts,
        "imageDerivation": derivation,
        "inputs": input_artifacts,
        "runs": run_rows,
        "functionInventoryCount": len(functions),
        "literalFunInventoryCount": sum(1 for function in functions if FUN_RE.fullmatch(function.name)),
        "unscorableFunctionRangeCount": unscorable_functions,
        "callEdgeCount": len(edges),
        "baselineUnionBlockCount": len(baseline_union),
        "actionUnionBlockCount": len(action_union),
        "actionIntersectionBlockCount": len(action_intersection),
        "anyActionNovelBlockCount": len(any_novel_global),
        "stableActionNovelBlockCount": len(stable_novel_global),
        "stableActionNovelMappingCounts": dict(sorted(stable_mapping_counts.items())),
        "candidateFunctionCount": len(candidate_rows),
        "literalFunCandidateCount": len(literal_fun_candidates),
        "classificationCounts": dict(sorted(classification_counts.items())),
        "actionCanaries": action_canary_results,
        "sharedCanaries": shared_canary_results,
        "actionVerifiedBy": (
            "RECEIPT_AND_COVERAGE_CANARY"
            if options_contract and receipt_actions_verified and options_canaries_pass
            else (
            "RECEIPT"
            if receipt_actions_verified
            else ("COVERAGE_CANARY" if canaries_verify_actions else "NONE")
            )
        ),
        "optionsCampaignContract": options_contract,
        "campaigns": campaign_summaries,
        "crossCampaign": (
            {
                "durableStableBlockCount": len(stable_novel_global),
                "campaign1OnlyStableBlockCount": len(
                    campaign_sets["C1"]["stable"] - campaign_sets["C2"]["stable"]
                ),
                "campaign2OnlyStableBlockCount": len(
                    campaign_sets["C2"]["stable"] - campaign_sets["C1"]["stable"]
                ),
                "durableMappingCounts": dict(sorted(stable_mapping_counts.items())),
            }
            if options_contract else None
        ),
        "evidenceSemantics": {
            "coverage": "A hit proves observation in a run; a miss proves only non-observation.",
            "frequency": (
                "Support counts are recurrence across distinct capture-receipt run IDs, "
                "not dynamic call counts; independence beyond the recorded protocol is not assumed."
            ),
            "stableNovel": "Basic-block start present in every action run and no baseline run.",
            "purpose": "Candidates prioritize TTD/static review; coverage alone never justifies a function name.",
        },
        "captureHealth": "COMPLETE",
        "comparability": comparison_status,
        "hypothesisVerdict": "UNKNOWN",
        "warnings": [
            *(
                [
                    f"{unscorable_functions} functions lack exact/contiguous body ranges; "
                    "their mappings are UNSCORED."
                ]
                if unscorable_functions
                else []
            ),
            *(
                ["Use at least two baseline and two action runs; three paired repetitions are preferred."]
                if len(baseline_run_ids) < 2 or len(action_run_ids) < 2
                else []
            ),
            *(["One or more action receipts are not independently verified."]
              if not all_actions_verified else []),
            *(["One or more Options campaign canaries failed."]
              if options_contract and not options_canaries_pass else []),
            *(["Duplicate run IDs prevent an independence claim."]
              if duplicate_run_ids else []),
            *(["Duplicate capture receipts prevent an independence claim."]
              if duplicate_receipt_hashes else []),
            *(["Duplicate drcov log paths prevent an independence claim."]
              if duplicate_log_paths else []),
            *(
                ["Duplicate drcov log content prevents an independence claim."]
                if duplicate_log_hashes and not options_contract else []
            ),
        ],
        "outputs": {
            "database": artifact_facts(database_path, "coverage-database"),
            "blocksJsonl": artifact_facts(output / "blocks.jsonl", "coverage-blocks-jsonl"),
            "deltaBlocksJsonl": artifact_facts(
                output / "delta-blocks.jsonl", "coverage-delta-blocks-jsonl"
            ),
            "functionsJsonl": artifact_facts(
                output / "functions.jsonl", "coverage-functions-jsonl"
            ),
            **(
                {
                    "campaignDeltaBlocksJsonl": artifact_facts(
                        output / "campaign-delta-blocks.jsonl",
                        "coverage-campaign-delta-blocks-jsonl",
                    )
                }
                if options_contract else {}
            ),
        },
    }
    write_json(output / "manifest.json", manifest)
    write_coverage_report(output / "report.md", manifest, candidate_rows)
    print(
        f"coverage diff: {len(candidate_rows)} candidate functions; "
        f"{len(literal_fun_candidates)} literal FUN_; "
        f"{len(stable_novel_global)} stable novel blocks"
    )
    print(output / "report.md")
    return 0


def write_coverage_report(
    path: pathlib.Path, manifest: dict[str, Any], candidates: Sequence[dict[str, Any]]
) -> None:
    lines = [
        f"# Differential coverage: {manifest['scenario']}",
        "",
        f"Generated: `{manifest['generatedAtUtc']}`  ",
        f"Schema: `{manifest['schemaVersion']}`  ",
        f"Question: {manifest['question'] or 'not supplied'}",
        "",
        "## Verdict boundary",
        "",
        "This report identifies code observed preferentially during the action runs. "
        "It does **not** prove that a candidate caused the action, that an unobserved "
        "function is unused, or that any proposed name is correct.",
        "",
        "## Exact accounting",
        "",
        "| Measure | Value |",
        "| --- | ---: |",
        f"| Baseline runs | {sum(1 for run in manifest['runs'] if run['role'] == 'baseline')} |",
        f"| Action runs | {sum(1 for run in manifest['runs'] if run['role'] == 'action')} |",
        f"| Ghidra functions | {manifest['functionInventoryCount']} |",
        f"| Literal `FUN_*` inventory | {manifest['literalFunInventoryCount']} |",
        f"| Baseline-union block starts | {manifest['baselineUnionBlockCount']} |",
        f"| Action-union block starts | {manifest['actionUnionBlockCount']} |",
        f"| Stable action-only block starts | {manifest['stableActionNovelBlockCount']} |",
        f"| Candidate functions | {manifest['candidateFunctionCount']} |",
        f"| Literal `FUN_*` candidates | {manifest['literalFunCandidateCount']} |",
        f"| Unscorable function ranges | {manifest['unscorableFunctionRangeCount']} |",
        f"| Comparability | {manifest['comparability']} |",
        "",
        f"Action verification route: `{manifest['actionVerifiedBy']}`. "
        + (
            "Canaries: "
            + ", ".join(
                f"`{row['name']}` {row['actionHits']}/{row['actionRuns']} action, "
                f"{row['baselineHits']}/{row['baselineRuns']} baseline"
                for row in manifest["actionCanaries"]
            )
            + "."
            if manifest["actionCanaries"]
            else "No action coverage canary was supplied."
        ),
        "",
        "Stable action-only block mapping closes as: "
        + ", ".join(
            f"`{key}`={value}"
            for key, value in manifest["stableActionNovelMappingCounts"].items()
        )
        + ". Unmapped and ambiguous rows remain in `delta-blocks.jsonl`; they are "
        "not silently discarded.",
        "",
        "## Highest-priority literal `FUN_*` candidates",
        "",
        "| Rank | Address | Name | Class | Idle | Action | Stable novel BBs | Range |",
        "| ---: | --- | --- | --- | ---: | ---: | ---: | --- |",
    ]
    literal = [row for row in candidates if row["namingRisk"] == "LITERAL_FUN"][:100]
    for row in literal:
        lines.append(
            "| {rank} | `{address}` | `{name}` | `{classification}` | "
            "{baselineSupport}/{baselineRuns} | {actionSupport}/{actionRuns} | "
            "{stableActionNovelBlocks} | `{rangeQuality}` |".format(**row, rank=row["rankOrdinal"], address=row["functionAddress"])
        )
    if not literal:
        lines.append("| — | — | — | — | — | — | — | — |")
    lines.extend(
        [
            "",
            "## All leading candidates",
            "",
            "| Rank | Address | Name | Naming risk | Class | Idle | Action | Novel BBs |",
            "| ---: | --- | --- | --- | --- | ---: | ---: | ---: |",
        ]
    )
    for row in candidates[:200]:
        lines.append(
            "| {rankOrdinal} | `{functionAddress}` | `{name}` | `{namingRisk}` | "
            "`{classification}` | {baselineSupport}/{baselineRuns} | "
            "{actionSupport}/{actionRuns} | {actionNovelBlocks} |".format(**row)
        )
    lines.extend(
        [
            "",
            "## Next adjudication",
            "",
            "For each leading candidate: inspect exact Ghidra callers/callees and bytes; "
            "query the address in one short TTD trace; observe arguments, object pointers, "
            "writes, and return value; require a positive and negative runtime control; "
            "then record a reviewed candidate name. Coverage is a queue generator, not a "
            "rename oracle.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


TTD_DIFF_CLASS_PRIORITY = {
    "ACTION_ONLY_STABLE_FUNCTION": 0,
    "SHARED_WITH_STABLE_ACTION_BYTES": 1,
    "ACTION_ONLY_UNSTABLE_FUNCTION": 2,
    "ACTION_ENRICHED_RECURRENCE": 3,
    "SHARED_WITH_UNSTABLE_ACTION_BYTES": 4,
    "UNSCORED_MAPPING": 5,
    "SHARED_OR_NO_OBSERVED_DELTA": 6,
}


def classify_ttd_candidate(
    *,
    baseline_support: int,
    action_support: int,
    baseline_runs: int,
    action_runs: int,
    any_novel_bytes: int,
    stable_novel_bytes: int,
    scorable: bool,
) -> str:
    if not scorable:
        return "UNSCORED_MAPPING"
    if action_support == action_runs and baseline_support == 0:
        return "ACTION_ONLY_STABLE_FUNCTION"
    if stable_novel_bytes:
        return "SHARED_WITH_STABLE_ACTION_BYTES"
    if action_support and baseline_support == 0:
        return "ACTION_ONLY_UNSTABLE_FUNCTION"
    if action_support * baseline_runs > baseline_support * action_runs:
        return "ACTION_ENRICHED_RECURRENCE"
    if any_novel_bytes:
        return "SHARED_WITH_UNSTABLE_ACTION_BYTES"
    return "SHARED_OR_NO_OBSERVED_DELTA"


def _embedded_artifact_facts(
    value: Any, *, kind: str, context: str
) -> dict[str, Any]:
    if (
        not isinstance(value, dict)
        or not isinstance(value.get("path"), str)
        or type(value.get("bytes")) is not int
        or not isinstance(value.get("sha256"), str)
    ):
        raise ParityLabError(f"{context} lacks immutable artifact facts")
    measured = artifact_facts(pathlib.Path(value["path"]), kind)
    if (
        measured["bytes"] != value["bytes"]
        or measured["sha256"].upper() != str(value["sha256"]).upper()
    ):
        raise ParityLabError(f"{context} no longer matches its bundle manifest")
    return measured


def _load_ttd_bundle_run(
    manifest_path: pathlib.Path,
    *,
    expected_role: str,
    expected_scenario: str,
    target_facts: dict[str, Any],
) -> dict[str, Any]:
    manifest_facts = artifact_facts(manifest_path, f"ttd-{expected_role}-bundle")
    payload = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    assert_artifact_unchanged(manifest_path, manifest_facts)
    if not isinstance(payload, dict) or payload.get("schemaVersion") != BUNDLE_SCHEMA:
        raise ParityLabError(f"Unsupported capture bundle: {manifest_path}")
    scenario = payload.get("scenario")
    if not isinstance(scenario, dict):
        raise ParityLabError(f"Capture bundle lacks scenario identity: {manifest_path}")
    if scenario.get("id") != expected_scenario or scenario.get("role") != expected_role:
        raise ParityLabError(
            f"Capture bundle scenario/role mismatch: {manifest_path}"
        )
    if payload.get("captureHealth") != "COMPLETE":
        raise ParityLabError(f"Capture bundle is not COMPLETE: {manifest_path}")
    if payload.get("targetMismatches") or payload.get("linkageMismatches"):
        raise ParityLabError(f"Capture bundle reports identity mismatch: {manifest_path}")
    target = payload.get("target")
    if (
        not isinstance(target, dict)
        or windows_path_key(str(target.get("path", "")))
        != windows_path_key(str(target_facts["path"]))
        or target.get("bytes") != target_facts["bytes"]
        or str(target.get("sha256", "")).upper()
        != str(target_facts["sha256"]).upper()
    ):
        raise ParityLabError(f"Capture bundle target hash mismatch: {manifest_path}")
    coverage_rows = payload.get("ttdCoverage")
    receipt_rows = payload.get("ttdCoverageReceipts")
    if (
        not isinstance(coverage_rows, list)
        or len(coverage_rows) != 1
        or not isinstance(receipt_rows, list)
        or len(receipt_rows) != 1
    ):
        raise ParityLabError(
            f"Each differential bundle must contain one TTD coverage and receipt: "
            f"{manifest_path}"
        )
    embedded_coverage = _embedded_artifact_facts(
        coverage_rows[0],
        kind="ttd-exec-coverage",
        context=f"TTD coverage in {manifest_path}",
    )
    embedded_receipt = _embedded_artifact_facts(
        receipt_rows[0],
        kind="ttd-exec-coverage-receipt",
        context=f"TTD receipt in {manifest_path}",
    )
    coverage_path = pathlib.Path(embedded_coverage["path"])
    receipt_path = pathlib.Path(embedded_receipt["path"])
    connection = open_database(":memory:")  # type: ignore[arg-type]
    try:
        coverage, _ = ingest_ttd_exec_coverage(connection, coverage_path)
        receipt, _ = ingest_ttd_exec_receipt(connection, receipt_path)
        ranges = [
            (int(row[0]), int(row[1]))
            for row in connection.execute(
                """
                SELECT rva_start, rva_end_exclusive
                FROM ttd_exec_range
                ORDER BY ordinal
                """
            )
        ]
    finally:
        connection.close()
    if coverage["health"] != "COMPLETE" or receipt["health"] != "COMPLETE":
        raise ParityLabError(f"TTD coverage/receipt is not COMPLETE: {manifest_path}")
    if not coverage["acceptancePassed"] or not receipt["acceptancePassed"]:
        raise ParityLabError(
            f"TTD coverage/receipt controls did not pass: {manifest_path}"
        )
    if coverage["sha256"].upper() != receipt["coverageSha256"].upper():
        raise ParityLabError(f"TTD coverage/receipt hash mismatch: {manifest_path}")
    if (
        windows_path_key(str(coverage["trace"]))
        != windows_path_key(str(receipt["trace"]))
        or coverage["traceBytes"] != receipt["traceBytes"]
        or windows_path_key(str(coverage["moduleName"]))
        != windows_path_key(str(receipt["target"]))
    ):
        raise ParityLabError(f"TTD coverage/receipt linkage mismatch: {manifest_path}")
    if receipt["targetSha256"].upper() != str(target_facts["sha256"]).upper():
        raise ParityLabError(f"TTD receipt target mismatch: {manifest_path}")
    return {
        "bundleId": payload.get("bundleId"),
        "role": expected_role,
        "manifest": manifest_facts,
        "coverage": coverage,
        "receipt": receipt,
        "ranges": ranges,
    }


def _ranges_to_bitmap(
    module_size: int, ranges: Sequence[tuple[int, int]]
) -> bytearray:
    bitmap = bytearray(module_size)
    previous_end = 0
    for start, end in ranges:
        if start < previous_end or start >= end or end > module_size:
            raise ParityLabError("Invalid TTD range while constructing bitmap")
        bitmap[start:end] = b"\x01" * (end - start)
        previous_end = end
    return bitmap


def _bitmap_ranges(bitmap: bytearray) -> list[tuple[int, int]]:
    result: list[tuple[int, int]] = []
    cursor = 0
    while True:
        start = bitmap.find(b"\x01", cursor)
        if start < 0:
            break
        end = bitmap.find(b"\x00", start)
        if end < 0:
            end = len(bitmap)
        result.append((start, end))
        cursor = end
    return result


def ttd_independence_summary(
    baseline_runs: Sequence[dict[str, Any]],
    action_runs: Sequence[dict[str, Any]],
) -> dict[str, Any]:
    baseline_trace_hashes = {
        run["receipt"]["traceSha256"] for run in baseline_runs
    }
    action_trace_hashes = {
        run["receipt"]["traceSha256"] for run in action_runs
    }
    return {
        "baselineWindowCount": len(baseline_runs),
        "actionWindowCount": len(action_runs),
        "baselineDistinctTraceCount": len(baseline_trace_hashes),
        "actionDistinctTraceCount": len(action_trace_hashes),
        "minimumDistinctTracesPerRoleForComparable": 3,
        "independentlyReplicated": (
            len(baseline_trace_hashes) >= 3 and len(action_trace_hashes) >= 3
        ),
    }


def run_ttd_coverage_diff(args: argparse.Namespace) -> int:
    output = create_output_dir(pathlib.Path(args.out))
    ghidra_path = pathlib.Path(args.ghidra)
    body_ranges_path = pathlib.Path(args.body_ranges)
    call_edges_path = pathlib.Path(args.call_edges) if args.call_edges else None
    graph_receipt_path = (
        pathlib.Path(args.graph_receipt) if args.graph_receipt else None
    )
    if bool(call_edges_path) != bool(graph_receipt_path):
        raise ParityLabError(
            "--call-edges and --graph-receipt must be supplied together"
        )
    static_path = pathlib.Path(args.static_exe)
    target_path = pathlib.Path(args.target_exe)
    image_base = parse_int(args.image_base, field="image base")
    derivation = image_derivation(static_path, target_path)
    static_facts = derivation["static"]
    target_facts = derivation["target"]
    if image_base != static_facts["pe"]["imageBaseInteger"]:
        raise ParityLabError("TTD diff image base disagrees with static PE")
    range_metadata = read_tsv_metadata(body_ranges_path)
    if range_metadata.get("executableMd5", "").lower() != static_facts["md5"]:
        raise ParityLabError("TTD diff Ghidra/static specimen MD5 mismatch")
    if parse_int(range_metadata.get("imageBase"), field="Ghidra image base") != image_base:
        raise ParityLabError("TTD diff Ghidra body ranges use another image base")

    functions = load_functions(ghidra_path, body_ranges_path)
    functions_by_address = {function.address: function for function in functions}
    interval_index = FunctionIntervalIndex(functions)
    edges = load_call_edges(call_edges_path)
    graph_receipt_facts = (
        validate_graph_receipt(
            graph_receipt_path,
            body_ranges_path,
            call_edges_path,
            functions,
            edges,
        )
        if graph_receipt_path and call_edges_path
        else None
    )
    run_specs = [
        *[
            ("baseline", pathlib.Path(path))
            for path in args.baseline_bundle
        ],
        *[("action", pathlib.Path(path)) for path in args.action_bundle],
    ]
    runs = [
        _load_ttd_bundle_run(
            path,
            expected_role=role,
            expected_scenario=args.scenario,
            target_facts=target_facts,
        )
        for role, path in run_specs
    ]
    module_sizes = {parse_hex_int(run["coverage"]["moduleSize"]) for run in runs}
    module_timestamps = {
        parse_hex_int(run["coverage"]["moduleTimestamp"]) for run in runs
    }
    module_checksums = {
        parse_hex_int(run["coverage"]["moduleChecksum"]) for run in runs
    }
    collector_hashes = {run["receipt"]["collectorSha256"] for run in runs}
    replay_identities = {
        (
            run["receipt"]["replayRuntimeVersion"],
            run["receipt"]["replaySha256"],
            run["receipt"]["replayCpuSha256"],
        )
        for run in runs
    }
    replay_modes = {run["coverage"]["replayMode"] for run in runs}
    if (
        len(module_sizes) != 1
        or len(module_timestamps) != 1
        or len(module_checksums) != 1
        or len(collector_hashes) != 1
        or len(replay_identities) != 1
        or len(replay_modes) != 1
    ):
        raise ParityLabError(
            "TTD differential inputs disagree on module/collector/runtime/replay mode"
        )
    module_size = next(iter(module_sizes))
    if (
        module_size != target_facts["pe"]["sizeOfImageInteger"]
        or next(iter(module_timestamps))
        != target_facts["pe"]["timestampInteger"]
        or next(iter(module_checksums)) != target_facts["pe"]["checksumInteger"]
    ):
        raise ParityLabError("TTD differential module tuple disagrees with target PE")
    run_keys = [
        (
            run["receipt"]["traceSha256"],
            run["coverage"]["requestedFrom"],
            run["coverage"]["requestedTo"],
        )
        for run in runs
    ]
    if len(run_keys) != len(set(run_keys)):
        raise ParityLabError("Duplicate trace/window input prevents independence")
    role_trace_keys = [
        (run["role"], run["receipt"]["traceSha256"]) for run in runs
    ]
    if len(role_trace_keys) != len(set(role_trace_keys)):
        raise ParityLabError(
            "A differential role may consume at most one window from each trace; "
            "same-trace windows are pseudoreplicates"
        )

    for run in runs:
        run["bitmap"] = _ranges_to_bitmap(module_size, run["ranges"])
    baseline_runs = [run for run in runs if run["role"] == "baseline"]
    action_runs = [run for run in runs if run["role"] == "action"]
    baseline_bits = 0
    for run in baseline_runs:
        baseline_bits |= int.from_bytes(run["bitmap"], "little")
    action_union_bits = 0
    action_intersection_bits: int | None = None
    for run in action_runs:
        bits = int.from_bytes(run["bitmap"], "little")
        action_union_bits |= bits
        action_intersection_bits = (
            bits if action_intersection_bits is None else action_intersection_bits & bits
        )
    assert action_intersection_bits is not None
    baseline_union = bytearray(baseline_bits.to_bytes(module_size, "little"))
    action_union = bytearray(action_union_bits.to_bytes(module_size, "little"))
    stable_novel = bytearray(
        (action_intersection_bits & ~baseline_bits).to_bytes(module_size, "little")
    )
    any_novel = bytearray(
        (action_union_bits & ~baseline_bits).to_bytes(module_size, "little")
    )

    def map_delta(
        bitmap: bytearray, *, retain_segments: bool
    ) -> tuple[Counter[int], Counter[str], list[dict[str, Any]]]:
        by_function: Counter[int] = Counter()
        by_quality: Counter[str] = Counter()
        segments: list[dict[str, Any]] = []
        for start, end in _bitmap_ranges(bitmap):
            segment_start = start
            current_key: tuple[int | None, str, str | None] | None = None
            for rva in range(start, end):
                function, quality = interval_index.lookup(image_base + rva)
                address = function.address if function else None
                key = (address, quality, function.name if function else None)
                if current_key is None:
                    current_key = key
                elif key != current_key:
                    if retain_segments:
                        segments.append(
                            {
                                "rvaStart": f"0x{segment_start:08X}",
                                "rvaEndExclusive": f"0x{rva:08X}",
                                "byteCount": rva - segment_start,
                                "mappingQuality": current_key[1],
                                "functionAddress": (
                                    f"0x{current_key[0]:08X}"
                                    if current_key[0] is not None
                                    else None
                                ),
                                "functionName": current_key[2],
                            }
                        )
                    segment_start = rva
                    current_key = key
                by_quality[quality] += 1
                if address is not None:
                    by_function[address] += 1
            if current_key is not None and retain_segments:
                segments.append(
                    {
                        "rvaStart": f"0x{segment_start:08X}",
                        "rvaEndExclusive": f"0x{end:08X}",
                        "byteCount": end - segment_start,
                        "mappingQuality": current_key[1],
                        "functionAddress": (
                            f"0x{current_key[0]:08X}"
                            if current_key[0] is not None
                            else None
                        ),
                        "functionName": current_key[2],
                    }
                )
        return by_function, by_quality, segments

    any_by_function, _, _ = map_delta(any_novel, retain_segments=False)
    stable_by_function, stable_mapping, delta_segments = map_delta(
        stable_novel, retain_segments=True
    )
    stable_novel_bytes = sum(stable_novel)
    if sum(stable_mapping.values()) != stable_novel_bytes:
        raise ParityLabError("TTD stable novel byte mapping accounting does not close")

    def function_observed(bitmap: bytearray, function: FunctionRecord) -> bool:
        if function.range_quality not in {
            "EXACT_GHIDRA_RANGES",
            "EXACT_CONTIGUOUS_INVENTORY",
        }:
            return False
        for minimum, maximum in function.ranges:
            start = minimum - image_base
            end = maximum - image_base + 1
            if start < 0 or end > len(bitmap):
                raise ParityLabError(
                    f"Ghidra function lies outside TTD module: 0x{function.address:08X}"
                )
            if bitmap.find(b"\x01", start, end) >= 0:
                return True
        return False

    caller_map: dict[int, list[CallEdge]] = defaultdict(list)
    callee_map: dict[int, list[CallEdge]] = defaultdict(list)
    for edge in edges:
        caller_map[edge.callee].append(edge)
        callee_map[edge.caller].append(edge)

    def edge_rows(items: Sequence[CallEdge], direction: str) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for edge in sorted(
            items, key=lambda item: (-item.count, item.caller, item.callee)
        ):
            other_address = edge.caller if direction == "caller" else edge.callee
            other = functions_by_address.get(other_address)
            rows.append(
                {
                    "address": f"0x{other_address:08X}",
                    "name": other.name if other else None,
                    "callSiteCount": edge.count,
                }
            )
        return rows

    candidates: list[dict[str, Any]] = []
    for function in functions:
        baseline_support = sum(
            function_observed(run["bitmap"], function) for run in baseline_runs
        )
        action_support = sum(
            function_observed(run["bitmap"], function) for run in action_runs
        )
        any_bytes = any_by_function.get(function.address, 0)
        stable_bytes = stable_by_function.get(function.address, 0)
        if not baseline_support and not action_support and not any_bytes:
            continue
        scorable = function.range_quality in {
            "EXACT_GHIDRA_RANGES",
            "EXACT_CONTIGUOUS_INVENTORY",
        }
        candidates.append(
            {
                "functionAddress": f"0x{function.address:08X}",
                "functionRva": f"0x{function.address - image_base:08X}",
                "name": function.name,
                "namingRisk": naming_risk(function),
                "rangeQuality": function.range_quality,
                "scorable": scorable,
                "classification": classify_ttd_candidate(
                    baseline_support=baseline_support,
                    action_support=action_support,
                    baseline_runs=len(baseline_runs),
                    action_runs=len(action_runs),
                    any_novel_bytes=any_bytes,
                    stable_novel_bytes=stable_bytes,
                    scorable=scorable,
                ),
                "baselineSupport": baseline_support,
                "baselineRuns": len(baseline_runs),
                "actionSupport": action_support,
                "actionRuns": len(action_runs),
                "actionNovelBytes": any_bytes,
                "stableActionNovelBytes": stable_bytes,
                "bodyBytes": function.body_bytes,
                "callers": edge_rows(caller_map.get(function.address, []), "caller"),
                "callees": edge_rows(callee_map.get(function.address, []), "callee"),
            }
        )
    candidates.sort(
        key=lambda row: (
            TTD_DIFF_CLASS_PRIORITY[row["classification"]],
            0 if row["namingRisk"] == "LITERAL_FUN" else 1,
            -row["stableActionNovelBytes"],
            -row["actionNovelBytes"],
            -row["actionSupport"],
            row["functionAddress"],
        )
    )
    for ordinal, row in enumerate(candidates, start=1):
        row["rankOrdinal"] = ordinal

    canaries: list[dict[str, Any]] = []
    for value in args.action_canary:
        address = parse_int(value, field="TTD action canary")
        function = functions_by_address.get(address)
        if function is None:
            raise ParityLabError(
                f"TTD action canary is not a Ghidra entry: 0x{address:08X}"
            )
        rva = address - image_base
        if rva < 0 or rva >= module_size:
            raise ParityLabError("TTD action canary lies outside the module")
        baseline_hits = sum(run["bitmap"][rva] == 1 for run in baseline_runs)
        action_hits = sum(run["bitmap"][rva] == 1 for run in action_runs)
        canaries.append(
            {
                "address": f"0x{address:08X}",
                "name": function.name,
                "baselineHits": baseline_hits,
                "baselineRuns": len(baseline_runs),
                "actionHits": action_hits,
                "actionRuns": len(action_runs),
                "passed": baseline_hits == 0 and action_hits == len(action_runs),
            }
        )
    canaries_passed = bool(canaries) and all(row["passed"] for row in canaries)
    independence = ttd_independence_summary(baseline_runs, action_runs)
    independently_replicated = bool(independence["independentlyReplicated"])
    comparability = (
        "COMPARABLE"
        if canaries_passed and independently_replicated
        else ("CORRELATED" if canaries_passed else "UNSCORED")
    )

    run_rows = [
        {
            "bundleId": run["bundleId"],
            "role": run["role"],
            "manifest": run["manifest"],
            "coverage": {
                key: run["coverage"][key]
                for key in (
                    "kind",
                    "path",
                    "bytes",
                    "sha256",
                    "trace",
                    "traceBytes",
                    "requestedFrom",
                    "requestedTo",
                    "rangeCount",
                    "coveredBytes",
                    "callbackHits",
                    "replayMode",
                )
            },
            "receipt": {
                key: run["receipt"][key]
                for key in (
                    "kind",
                    "path",
                    "bytes",
                    "sha256",
                    "traceSha256",
                    "targetSha256",
                    "collectorSha256",
                    "replayRuntimeVersion",
                    "replaySha256",
                    "replayCpuSha256",
                )
            },
        }
        for run in runs
    ]
    write_jsonl(output / "runs.jsonl", run_rows)
    write_jsonl(output / "delta-ranges.jsonl", delta_segments)
    write_jsonl(output / "functions.jsonl", candidates)

    database_path = output / "ttd-diff.sqlite"
    connection = sqlite3.connect(database_path)
    try:
        connection.executescript(
            """
            CREATE TABLE meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE delta_range(
                ordinal INTEGER PRIMARY KEY,
                rva_start INTEGER NOT NULL,
                rva_end_exclusive INTEGER NOT NULL,
                byte_count INTEGER NOT NULL,
                mapping_quality TEXT NOT NULL,
                function_address INTEGER,
                function_name TEXT
            );
            CREATE TABLE candidate(
                rank_ordinal INTEGER PRIMARY KEY,
                function_address INTEGER NOT NULL,
                name TEXT NOT NULL,
                naming_risk TEXT NOT NULL,
                classification TEXT NOT NULL,
                baseline_support INTEGER NOT NULL,
                action_support INTEGER NOT NULL,
                action_novel_bytes INTEGER NOT NULL,
                stable_action_novel_bytes INTEGER NOT NULL,
                body_bytes INTEGER NOT NULL,
                callers_json TEXT NOT NULL,
                callees_json TEXT NOT NULL
            );
            """
        )
        connection.executemany(
            "INSERT INTO meta(key, value) VALUES (?, ?)",
            [
                ("schema", "bea-ttd-differential-coverage.v1"),
                ("scenario", args.scenario),
                ("comparability", comparability),
            ],
        )
        for ordinal, row in enumerate(delta_segments):
            connection.execute(
                """
                INSERT INTO delta_range(
                    ordinal, rva_start, rva_end_exclusive, byte_count,
                    mapping_quality, function_address, function_name
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    ordinal,
                    int(row["rvaStart"], 16),
                    int(row["rvaEndExclusive"], 16),
                    row["byteCount"],
                    row["mappingQuality"],
                    (
                        int(row["functionAddress"], 16)
                        if row["functionAddress"]
                        else None
                    ),
                    row["functionName"],
                ),
            )
        for row in candidates:
            connection.execute(
                """
                INSERT INTO candidate(
                    rank_ordinal, function_address, name, naming_risk,
                    classification, baseline_support, action_support,
                    action_novel_bytes, stable_action_novel_bytes, body_bytes,
                    callers_json, callees_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["rankOrdinal"],
                    int(row["functionAddress"], 16),
                    row["name"],
                    row["namingRisk"],
                    row["classification"],
                    row["baselineSupport"],
                    row["actionSupport"],
                    row["actionNovelBytes"],
                    row["stableActionNovelBytes"],
                    row["bodyBytes"],
                    json.dumps(row["callers"], sort_keys=True),
                    json.dumps(row["callees"], sort_keys=True),
                ),
            )
        connection.commit()
        connection.execute("VACUUM")
    finally:
        connection.close()

    input_artifacts = [
        artifact_facts(ghidra_path, "ghidra-function-inventory"),
        artifact_facts(body_ranges_path, "ghidra-body-ranges"),
        static_facts,
        target_facts,
        *(
            [artifact_facts(call_edges_path, "ghidra-call-edges")]
            if call_edges_path
            else []
        ),
        *([graph_receipt_facts] if graph_receipt_facts else []),
    ]
    manifest = {
        "schemaVersion": "bea-ttd-differential-coverage.v1",
        "toolVersion": TOOL_VERSION,
        "generatedAtUtc": utc_now(),
        "scenario": args.scenario,
        "question": args.question,
        "comparability": comparability,
        "hypothesisVerdict": "UNKNOWN",
        "actionVerifiedBy": (
            "TTD_COVERAGE_CANARY" if canaries_passed else "NONE"
        ),
        "actionCanaries": canaries,
        "independence": independence,
        "staticRuntimeDerivation": derivation,
        "inputArtifacts": input_artifacts,
        "runs": run_rows,
        "functionInventoryCount": len(functions),
        "literalFunInventoryCount": sum(
            1 for function in functions if FUN_RE.fullmatch(function.name)
        ),
        "baselineUnionBytes": sum(baseline_union),
        "actionUnionBytes": sum(action_union),
        "anyActionNovelBytes": sum(any_novel),
        "stableActionNovelBytes": stable_novel_bytes,
        "stableActionNovelMappingBytes": dict(sorted(stable_mapping.items())),
        "candidateFunctionCount": len(candidates),
        "literalFunCandidateCount": sum(
            row["namingRisk"] == "LITERAL_FUN" for row in candidates
        ),
        "moduleIdentity": {
            "sizeOfImage": f"0x{module_size:X}",
            "timestamp": f"0x{next(iter(module_timestamps)):X}",
            "checksum": f"0x{next(iter(module_checksums)):X}",
        },
        "collectorIdentity": {
            "collectorSha256": next(iter(collector_hashes)),
            "replay": {
                "version": next(iter(replay_identities))[0],
                "replaySha256": next(iter(replay_identities))[1],
                "replayCpuSha256": next(iter(replay_identities))[2],
            },
            "replayMode": next(iter(replay_modes)),
            "moduleInstancePolicy": "exactly-one-active-for-window",
        },
        "limits": [
            "Execution bytes prove presence only; absence is scoped to the recorded window.",
            "TTD Replay coverage has no per-address frequency in schema v1.",
            "Function attribution uses exact Ghidra body fragments; ambiguous and "
            "unmapped bytes remain explicit.",
            "Coverage ranks candidates and never authorizes a name or Ghidra mutation.",
            "Multiple windows from one trace are correlated observations, not "
            "independent replications; COMPARABLE requires three distinct trace "
            "content hashes in each role.",
        ],
    }
    write_ttd_diff_report(output / "report.md", manifest, candidates)
    manifest["outputs"] = {
        "database": artifact_facts(database_path, "ttd-diff-database"),
        "runsJsonl": artifact_facts(output / "runs.jsonl", "ttd-diff-runs-jsonl"),
        "deltaRangesJsonl": artifact_facts(
            output / "delta-ranges.jsonl", "ttd-diff-ranges-jsonl"
        ),
        "functionsJsonl": artifact_facts(
            output / "functions.jsonl", "ttd-diff-functions-jsonl"
        ),
        "report": artifact_facts(output / "report.md", "ttd-diff-report"),
    }
    write_json(output / "manifest.json", manifest)
    print(
        f"TTD coverage diff: {stable_novel_bytes} stable novel byte(s), "
        f"{len(candidates)} candidate function(s), comparability={comparability}"
    )
    print(output / "report.md")
    return 0


def write_ttd_diff_report(
    path: pathlib.Path,
    manifest: dict[str, Any],
    candidates: Sequence[dict[str, Any]],
) -> None:
    lines = [
        f"# TTD differential coverage: {manifest['scenario']}",
        "",
        f"Question: {manifest['question'] or 'not supplied'}  ",
        f"Comparability: **{manifest['comparability']}**  ",
        "Hypothesis: **UNKNOWN**",
        "",
        "TTD Replay records exact executed instruction bytes in the requested "
        "windows. This report is a presence-based candidate queue, not causal "
        "proof and not a naming oracle.",
        "",
        "| Measure | Value |",
        "| --- | ---: |",
        f"| Baseline runs | {sum(row['role'] == 'baseline' for row in manifest['runs'])} |",
        f"| Action runs | {sum(row['role'] == 'action' for row in manifest['runs'])} |",
        f"| Distinct baseline traces | {manifest['independence']['baselineDistinctTraceCount']} |",
        f"| Distinct action traces | {manifest['independence']['actionDistinctTraceCount']} |",
        f"| Baseline-union bytes | {manifest['baselineUnionBytes']} |",
        f"| Action-union bytes | {manifest['actionUnionBytes']} |",
        f"| Any action-only bytes | {manifest['anyActionNovelBytes']} |",
        f"| Stable action-only bytes | {manifest['stableActionNovelBytes']} |",
        f"| Candidate functions | {manifest['candidateFunctionCount']} |",
        f"| Literal `FUN_*` candidates | {manifest['literalFunCandidateCount']} |",
        "",
        "Stable-byte mapping: "
        + ", ".join(
            f"`{key}`={value}"
            for key, value in manifest["stableActionNovelMappingBytes"].items()
        )
        + ".",
        "",
        "| Rank | Address | Name | Risk | Class | Idle | Action | Stable bytes |",
        "| ---: | --- | --- | --- | --- | ---: | ---: | ---: |",
    ]
    for row in candidates[:250]:
        lines.append(
            "| {rankOrdinal} | `{functionAddress}` | `{name}` | `{namingRisk}` | "
            "`{classification}` | {baselineSupport}/{baselineRuns} | "
            "{actionSupport}/{actionRuns} | {stableActionNovelBytes} |".format(**row)
        )
    lines.extend(
        [
            "",
            "Adjudicate leading rows with stacks, arguments, memory writes, source/BSim "
            "candidates, and a negative control before promoting any semantic name.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def parse_kv_tokens(text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for token in text.split():
        if "=" not in token:
            continue
        key, value = token.split("=", 1)
        if key and key not in fields:
            fields[key] = value
    return fields


def value_projection(
    value: str, *, key: str | None = None
) -> tuple[str, int | None, float | None, str]:
    provenance = "OBSERVED"
    base = value
    if value.endswith("~"):
        provenance = "D3D_DEFAULT"
        base = value[:-1]
    elif key == "cov" and value.endswith("?"):
        provenance = "PROVISIONAL_COVERAGE"
        base = value[:-1]
    elif value == "?" or value.endswith("?"):
        provenance = "UNKNOWN"
        base = value[:-1] if value != "?" else ""
    integer: int | None = None
    real: float | None = None
    try:
        if re.fullmatch(r"-?(?:0x[0-9A-Fa-f]+|\d+)", base):
            integer = int(base, 0)
        elif re.fullmatch(r"-?(?:\d+\.\d*|\d*\.\d+)(?:[eE][+-]?\d+)?", base):
            real = float(base)
    except ValueError:
        pass
    return value, integer, real, provenance


def insert_d3d9_event(
    connection: sqlite3.Connection,
    artifact_id: int,
    *,
    sequence: int,
    byte_offset: int,
    byte_length: int,
    line_number: int,
    record_type: str,
    frame: int | None,
    draw: int | None,
    ordinal: str | None,
    status: str | None,
    raw: str,
    fields: dict[str, str],
) -> int:
    cursor = connection.execute(
        """
        INSERT INTO d3d9_event(
            artifact_id, sequence, byte_offset, byte_length, line_number,
            record_type, frame, draw, ordinal, status, raw
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            artifact_id,
            sequence,
            byte_offset,
            byte_length,
            line_number,
            record_type,
            frame,
            draw,
            ordinal,
            status,
            raw,
        ),
    )
    event_id = int(cursor.lastrowid)
    for key, value in fields.items():
        text, integer, real, provenance = value_projection(value, key=key)
        connection.execute(
            """
            INSERT INTO d3d9_field(
                event_id, key, value_text, value_integer, value_real, provenance
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (event_id, key, text, integer, real, provenance),
        )
    return event_id


def parse_d3d9_log(
    path: pathlib.Path, connection: sqlite3.Connection, artifact_id: int
) -> ParsedD3D9:
    raw = path.read_bytes()
    lines = raw.splitlines(keepends=True)
    counts: Counter[str] = Counter()
    diagnostics: list[dict[str, Any]] = []
    header: dict[str, Any] = {}
    recognized_data = 0
    recognized_comments = 0
    unknown = 0
    malformed = 0
    encoding_errors = 0
    offset = 0
    footer_seen = False
    declared_refusals: int | None = None
    declared_warnings: int | None = None
    observed_refusals = 0
    observed_warnings = 0
    draws_per_frame: Counter[int] = Counter()
    presents: dict[int, int] = {}

    for sequence, raw_line in enumerate(lines, start=1):
        byte_length = len(raw_line)
        content_bytes = raw_line.rstrip(b"\r\n")
        try:
            line = content_bytes.decode("ascii")
            encoding_ok = True
        except UnicodeDecodeError:
            line = content_bytes.decode("ascii", errors="backslashreplace")
            encoding_ok = False
            encoding_errors += 1
        token = line.split(None, 1)[0] if line.strip() else ""
        record_type = ""
        frame: int | None = None
        draw: int | None = None
        ordinal: str | None = None
        status: str | None = None
        fields: dict[str, str] = {}
        recognized = False
        malformed_known = False

        if not line.strip():
            record_type = "BLANK"
            recognized = True
        elif line.startswith("#"):
            record_type = "COMMENT"
            recognized = True
            recognized_comments += 1
            if line == "# bea-d3d9-proxy v1":
                header["format"] = "bea-d3d9-proxy v1"
            footer_match = D3D_REFUSAL_TOTAL_RE.match(line)
            if footer_match:
                footer_seen = True
                declared_refusals = int(footer_match.group("refusals"))
                declared_warnings = int(footer_match.group("warnings"))
            if line.startswith("# time="):
                header.update(parse_kv_tokens(line[2:]))
            elif line.startswith("# exe="):
                header["exe"] = line[len("# exe=") :]
            elif line.startswith("# real="):
                header["real"] = line[len("# real=") :]
            elif line.startswith("# cfg "):
                header["cfg"] = parse_kv_tokens(line[len("# cfg ") :])
        elif token == "D":
            match = D3D_DRAW_RE.match(line)
            if match:
                recognized = True
                record_type = "DRAW"
                frame = int(match.group("frame"))
                draw = int(match.group("draw"))
                ordinal = match.group("op")
                fields = parse_kv_tokens(match.group("tail"))
                draws_per_frame[frame] += 1
            else:
                malformed_known = True
        elif token == "V":
            match = D3D_VERTEX_RE.match(line)
            if match:
                recognized = True
                record_type = "VERTEX"
                frame = int(match.group("frame"))
                draw = int(match.group("draw"))
                ordinal = match.group("ordinal")
                tail = match.group("tail")
                fields = parse_kv_tokens(tail)
                if ordinal == "-":
                    parts = tail.split(None, 1)
                    status = parts[0] if parts else "malformed"
                    fields["reason"] = parts[1] if len(parts) > 1 else ""
                    if status == "none":
                        observed_refusals += 1
                    elif status == "warn":
                        observed_warnings += 1
            else:
                malformed_known = True
        elif token == "I":
            match = D3D_INDEX_RE.match(line)
            if match:
                recognized = True
                record_type = "INDEX"
                frame = int(match.group("frame"))
                draw = int(match.group("draw"))
                tail = match.group("tail")
                fields = parse_kv_tokens(tail)
                if tail.startswith("- "):
                    parts = tail[2:].split(None, 1)
                    status = parts[0] if parts else "malformed"
                    fields["reason"] = parts[1] if len(parts) > 1 else ""
                    if status == "none":
                        observed_refusals += 1
                    elif status == "warn":
                        observed_warnings += 1
            else:
                malformed_known = True
        elif token == "G" and not re.match(r"^G\s+\d+(?:\s|$)", line):
            recognized = True
            tail = line[2:] if line.startswith("G ") else ""
            ordinal = tail.split(None, 1)[0] if tail else ""
            if tail.startswith(("fail ", "disabled ")):
                record_type = "GRAB_DIAGNOSTIC"
                status = ordinal
            else:
                record_type = "GRAB_META"
            fields = parse_kv_tokens(tail)
            fields["message"] = tail
        elif token in {"P", "S", "C", "G", "!"}:
            match = D3D_FRAME_RE.match(line)
            if match:
                recognized = True
                frame = int(match.group("frame"))
                record_type = {
                    "P": "PRESENT",
                    "S": "SCENE",
                    "C": "CLEAR",
                    "G": "GRAB",
                    "!": "STATE_BLOCK",
                }[token]
                tail = match.group("tail") or ""
                fields = parse_kv_tokens(tail)
                if token == "P" and "draws" in fields:
                    try:
                        presents[frame] = int(fields["draws"], 0)
                    except ValueError:
                        malformed_known = True
                        recognized = False
            else:
                malformed_known = True
        elif token in {"L", "U"}:
            match = D3D_LOCK_RE.match(line)
            if match:
                recognized = True
                record_type = "LOCK" if token == "L" else "UNLOCK"
                ordinal = match.group("buffer")
                fields = parse_kv_tokens(match.group("tail"))
            else:
                malformed_known = True
        elif token in {"VB", "IB"}:
            match = D3D_RESOURCE_RE.match(line)
            if match:
                recognized = True
                record_type = f"{token}_{match.group('event').upper()}"
                ordinal = match.group("event")
                fields = parse_kv_tokens(match.group("tail"))
            else:
                malformed_known = True
        elif token in {"D3D9", "DEV"}:
            recognized = True
            record_type = "DEVICE"
            ordinal = token
            fields = parse_kv_tokens(line.split(None, 1)[1] if " " in line else "")

        if not encoding_ok:
            malformed_known = True
            recognized = False
        if malformed_known:
            malformed += 1
            record_type = f"MALFORMED_{token or 'BLANK'}"
            diagnostics.append(
                {
                    "line": sequence,
                    "byteOffset": offset,
                    "kind": "MALFORMED",
                    "recordToken": token,
                    "rawBase64": base64.b64encode(content_bytes).decode("ascii"),
                }
            )
        elif recognized:
            if record_type != "COMMENT":
                recognized_data += 1
            counts[record_type] += 1
        else:
            unknown += 1
            record_type = f"UNKNOWN_{token or 'BLANK'}"
            diagnostics.append(
                {
                    "line": sequence,
                    "byteOffset": offset,
                    "kind": "UNKNOWN",
                    "recordToken": token,
                    "raw": line,
                }
            )

        insert_d3d9_event(
            connection,
            artifact_id,
            sequence=sequence,
            byte_offset=offset,
            byte_length=byte_length,
            line_number=sequence,
            record_type=record_type,
            frame=frame,
            draw=draw,
            ordinal=ordinal,
            status=status,
            raw=line,
            fields=fields,
        )
        offset += byte_length

    present_draw_mismatches = sum(
        1 for frame, declared in presents.items() if draws_per_frame.get(frame, 0) != declared
    )
    result = ParsedD3D9(
        total_lines=len(lines),
        recognized_data=recognized_data,
        recognized_comments=recognized_comments,
        unknown_records=unknown,
        malformed_records=malformed,
        encoding_errors=encoding_errors,
        footer_seen=footer_seen,
        declared_refusals=declared_refusals,
        declared_warnings=declared_warnings,
        observed_refusals=observed_refusals,
        observed_warnings=observed_warnings,
        present_draw_mismatches=present_draw_mismatches,
        record_counts=counts,
        header=header,
        diagnostics=diagnostics,
    )
    if result.accounted_lines != result.total_lines:
        raise ParityLabError(
            f"Internal D3D9 line-accounting error: {result.accounted_lines} != {result.total_lines}"
        )
    return result


def ingest_ttd_receipt(
    connection: sqlite3.Connection, path: pathlib.Path
) -> tuple[dict[str, Any], int]:
    facts = artifact_facts(path, "ttd-receipt")
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise ParityLabError(f"TTD receipt is not an object: {path}")
    schema = str(payload.get("schemaVersion", ""))
    if schema not in {
        "ttd-record-receipt.v1",
        "ttd-record-receipt.v2",
        "ttd-record-receipt.v3",
    }:
        raise ParityLabError(f"Unsupported TTD receipt schema in {path}: {schema!r}")
    trace_value = payload.get("traceFile")
    trace_bytes = payload.get("traceBytes")
    if not isinstance(trace_value, str) or not isinstance(trace_bytes, int):
        raise ParityLabError(f"TTD receipt lacks typed traceFile/traceBytes: {path}")
    trace_path = pathlib.Path(trace_value)
    trace_exists = trace_path.is_file()
    trace_size_matches = trace_exists and trace_path.stat().st_size == trace_bytes
    declared_trace_hash = str(payload.get("traceSha256") or "").upper()
    trace_hash_declared = bool(re.fullmatch(r"[0-9A-F]{64}", declared_trace_hash))
    # A DEFERRED HASH IS AN HONEST ABSENCE, NOT A MATCH.
    #
    # tools/ttd_record.ps1 writes a receipt with traceSha256 = null when the
    # trace was demonstrably finished but TTD still held the file at the end of
    # the unlock budget.  Refusing that receipt outright would put us back where
    # the defect started - a valid trace with no pipeline record - so it is
    # ingested, but it can never be COMPLETE and its null can never satisfy a
    # hash comparison.  The deferral must be DECLARED: a v3 receipt whose hash is
    # merely missing is still a malformed receipt and is still refused.
    hash_state = str(payload.get("traceHashState") or "").strip()
    deferral = payload.get("hashDeferred")
    trace_hash_deferred = hash_state == "deferred"
    if trace_hash_deferred and trace_hash_declared:
        raise ParityLabError(
            f"TTD receipt declares a deferred trace hash and carries one too: {path}"
        )
    if trace_hash_deferred and not isinstance(deferral, dict):
        raise ParityLabError(
            f"TTD receipt defers its trace hash without a hashDeferred block: {path}"
        )
    if not trace_hash_deferred and isinstance(deferral, dict):
        raise ParityLabError(
            "TTD receipt carries a hashDeferred block without "
            f"traceHashState 'deferred': {path}"
        )
    if (
        schema == "ttd-record-receipt.v3"
        and not trace_hash_declared
        and not trace_hash_deferred
    ):
        raise ParityLabError(f"TTD v3 receipt lacks a valid traceSha256: {path}")
    current_trace_hash = sha256_file(trace_path) if trace_size_matches else ""
    trace_hash_matches = (
        trace_hash_declared
        and not trace_hash_deferred
        and current_trace_hash == declared_trace_hash
    )
    trace_artifact = (
        {
            "kind": "ttd-trace",
            "path": str(trace_path.resolve()),
            "bytes": trace_bytes,
            "sha256": declared_trace_hash,
        }
        if trace_hash_declared
        else None
    )
    max_file_mb = payload.get("maxFileMB")
    stopped_at_cap = (
        isinstance(max_file_mb, (int, float))
        and max_file_mb > 0
        and trace_bytes >= int(float(max_file_mb) * 1024 * 1024)
    )
    requested = payload.get("requestedSeconds")
    actual = payload.get("actualRecordSeconds")
    runaway_duration = (
        isinstance(requested, (int, float))
        and requested > 0
        and isinstance(actual, (int, float))
        and actual > max(float(requested) * 2.0, float(requested) + 120.0)
    )
    health = (
        "COMPLETE"
        if (
            payload.get("guestRanCleanly") is True
            and trace_size_matches
            and trace_hash_matches
            and not trace_hash_deferred
            and not stopped_at_cap
            and not runaway_duration
        )
        else (
            "ERROR"
            if trace_hash_declared and not trace_hash_matches
            else "PARTIAL"
        )
    )
    artifact_id = add_artifact(connection, facts, schema_version=schema, health=health)
    cursor = connection.execute(
        """
        INSERT INTO ttd_capture(
            artifact_id, name, target_sha256, trace_path, trace_bytes,
            recorder_version, guest_outcome, guest_ran_cleanly,
            recorded_at_utc, raw_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            artifact_id,
            payload.get("name"),
            payload.get("targetSha256"),
            trace_value,
            trace_bytes,
            payload.get("recorderVersion"),
            payload.get("guestOutcome"),
            int(bool(payload.get("guestRanCleanly"))),
            payload.get("recordedAtUtc"),
            json.dumps(payload, sort_keys=True),
        ),
    )
    summary = {
        **facts,
        "schemaVersion": schema,
        "health": health,
        "captureId": int(cursor.lastrowid),
        "targetSha256": payload.get("targetSha256"),
        "guestOutcome": payload.get("guestOutcome"),
        "traceFile": payload.get("traceFile"),
        "traceBytes": payload.get("traceBytes"),
        "traceExists": trace_exists,
        "traceSizeMatches": trace_size_matches,
        "traceSha256": declared_trace_hash or None,
        "traceHashDeclared": trace_hash_declared,
        "traceHashMatches": trace_hash_matches,
        "traceHashState": (
            hash_state or ("present" if trace_hash_declared else "absent")
        ),
        "traceHashDeferred": trace_hash_deferred,
        "traceHashDeferredReason": (
            str(deferral.get("reason")) if isinstance(deferral, dict) else None
        ),
        "traceArtifact": trace_artifact,
        "stoppedAtOrBeyondCap": stopped_at_cap,
        "runawayDuration": runaway_duration,
    }
    return summary, artifact_id


def ingest_ttd_result(
    connection: sqlite3.Connection, path: pathlib.Path
) -> tuple[dict[str, Any], int]:
    facts = artifact_facts(path, "ttd-query-result")
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise ParityLabError(f"TTD result is not an object: {path}")
    schema = str(payload.get("schemaVersion", ""))
    if schema not in {
        "ttd-query-result.v1",
        "ttd-query-result.v2",
        "ttd-query-result.v3",
    }:
        raise ParityLabError(f"Unsupported TTD query schema in {path}: {schema!r}")
    ok = payload.get("ok") is True
    timed_out = payload.get("timedOut") is True
    trace_value = payload.get("trace")
    trace_bytes = payload.get("traceBytes")
    if not isinstance(trace_value, str) or not isinstance(trace_bytes, int):
        raise ParityLabError(f"TTD result lacks typed trace/traceBytes: {path}")
    trace_path = pathlib.Path(trace_value)
    trace_exists = trace_path.is_file()
    trace_size_matches = trace_exists and trace_path.stat().st_size == trace_bytes
    declared_trace_hash = str(payload.get("traceSha256", "")).upper()
    trace_hash_declared = bool(re.fullmatch(r"[0-9A-F]{64}", declared_trace_hash))
    if schema == "ttd-query-result.v3" and not trace_hash_declared:
        raise ParityLabError(f"TTD v3 query lacks a valid traceSha256: {path}")
    current_trace_hash = sha256_file(trace_path) if trace_size_matches else ""
    trace_hash_matches = (
        trace_hash_declared and current_trace_hash == declared_trace_hash
    )
    trace_artifact = (
        {
            "kind": "ttd-trace",
            "path": str(trace_path.resolve()),
            "bytes": trace_bytes,
            "sha256": declared_trace_hash,
        }
        if trace_hash_declared
        else None
    )
    known_answer = payload.get("knownAnswer")
    negative_control = payload.get("negativeControl")
    known_passed = (
        isinstance(known_answer, dict) and known_answer.get("AllAgree") is True
    )
    negative_passed = (
        isinstance(negative_control, dict)
        and negative_control.get("Passed") is True
    )
    controls_passed = known_passed and negative_passed
    output = payload.get("output")
    if not isinstance(output, list):
        raise ParityLabError(f"TTD result output is not an array: {path}")
    health = (
        "COMPLETE"
        if (
            ok
            and not timed_out
            and trace_size_matches
            and trace_hash_matches
            and controls_passed
            and output
        )
        else (
            "PARTIAL"
            if (
                ok
                and not timed_out
                and trace_size_matches
                and not (trace_hash_declared and not trace_hash_matches)
            )
            else "ERROR"
        )
    )
    artifact_id = add_artifact(connection, facts, schema_version=schema, health=health)
    cursor = connection.execute(
        """
        INSERT INTO ttd_query(
            artifact_id, trace_path, trace_bytes, schema_version,
            ok, timed_out, problems_json, raw_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            artifact_id,
            trace_value,
            trace_bytes,
            schema,
            int(ok),
            int(timed_out),
            json.dumps(payload.get("problems", []), sort_keys=True),
            json.dumps(payload, sort_keys=True),
        ),
    )
    query_id = int(cursor.lastrowid)
    marker_count = 0
    for ordinal, value in enumerate(output):
        text = str(value)
        marker = TTD_MARKER_RE.search(text)
        marker_kind = marker.group("kind") if marker else None
        marker_body = marker.group("body") if marker else None
        if marker:
            marker_count += 1
        connection.execute(
            """
            INSERT INTO ttd_line(query_id, ordinal, marker_kind, marker_body, text)
            VALUES (?, ?, ?, ?, ?)
            """,
            (query_id, ordinal, marker_kind, marker_body, text),
        )
    return (
        {
            **facts,
            "schemaVersion": schema,
            "health": health,
            "queryId": query_id,
            "ok": ok,
            "timedOut": timed_out,
            "problemCount": len(payload.get("problems", [])),
            "outputLineCount": len(output),
            "markerCount": marker_count,
            "trace": payload.get("trace"),
            "traceBytes": trace_bytes,
            "traceExists": trace_exists,
            "traceSizeMatches": trace_size_matches,
            "traceSha256": declared_trace_hash or None,
            "traceHashDeclared": trace_hash_declared,
            "traceHashMatches": trace_hash_matches,
            "traceArtifact": trace_artifact,
            "knownAnswerPassed": known_passed,
            "negativeControlPassed": negative_passed,
            "controlsPassed": controls_passed,
            "knownAnswerSha256": (
                known_answer.get("Sha256") if isinstance(known_answer, dict) else None
            ),
        },
        artifact_id,
    )


# A terminal event the collector's own acceptance clause refuses, but which the
# wrapper may adjudicate for a declared trace class.  The level-opening corpus
# was recorded by stopping the recorder on a timer with the guest still alive,
# so its replays end on a Thread event rather than a Process exit.  Widening is
# per-reason and opt-in: nothing else joins this set without its own evidence.
TTD_ADJUDICABLE_STOP_REASONS = frozenset({"Thread"})

TTD_ADJUDICATING_RECEIPT_SCHEMA = "bea-ttd-exec-coverage-receipt.v2"


def _load_stop_reason_adjudication(
    path: pathlib.Path, coverage_sha256: str
) -> dict[str, Any] | None:
    """Find the wrapper receipt that adjudicated THIS coverage file's stop.

    The collector never knows the trace class; it only reports the terminal
    event it saw.  The adjudication is the wrapper's, written to the receipt
    beside the coverage file, and it is bound to that file by the coverage
    hash - a receipt describing some other run cannot vouch for this one.
    """

    directory = path.parent
    candidates = [directory / "receipt.json", directory / f"{path.stem}-receipt.json"]
    candidates += sorted(
        candidate
        for candidate in directory.glob("*receipt*.json")
        if candidate not in candidates
    )
    for candidate in candidates:
        if not candidate.is_file():
            continue
        try:
            payload = json.loads(candidate.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError):
            continue
        if not isinstance(payload, dict):
            continue
        if payload.get("schemaVersion") != TTD_ADJUDICATING_RECEIPT_SCHEMA:
            continue
        coverage = payload.get("coverage")
        if not isinstance(coverage, dict):
            continue
        if str(coverage.get("sha256", "")).upper() != coverage_sha256.upper():
            continue
        return {"path": candidate, "payload": payload}
    return None


def _adjudicated_stop_evidence(
    path: pathlib.Path,
    coverage_sha256: str,
    stop_reason: str,
    summary: dict[str, Any],
    metadata: dict[str, Any],
    *,
    counters_quarantined: bool,
    replay_complete: bool,
    marker_assertions_passed: bool,
) -> dict[str, Any]:
    """Accept a non-base terminal stop only on the wrapper's own adjudication.

    Mirrors the #149 quarantine: the ranges stay valid because they were
    collected by our bitmap and independently recomputed, and the thing the
    collector refused is surfaced rather than smoothed over.  Three ways to
    fail: no adjudication at all, an adjudication whose expectation was never
    declared, and an adjudication that contradicts the summary it describes.
    """

    if stop_reason not in TTD_ADJUDICABLE_STOP_REASONS:
        raise ParityLabError(f"TTD summary has unsupported stop reason: {path}")

    found = _load_stop_reason_adjudication(path, coverage_sha256)
    if found is None:
        raise ParityLabError(
            f"TTD {stop_reason} stop has no wrapper adjudication receipt "
            f"bound to this coverage: {path}"
        )
    payload = found["payload"]
    terminal = payload.get("terminalStop")
    if payload.get("stopReasonAdjudicated") is not True or not isinstance(
        terminal, dict
    ):
        raise ParityLabError(
            f"TTD {stop_reason} stop has no wrapper adjudication receipt "
            f"bound to this coverage: {path}"
        )

    invocation = payload.get("invocation")
    declared = isinstance(invocation, dict) and invocation.get(
        "expectAliveAtStop"
    ) is True
    if not declared or terminal.get("aliveAtStopExpected") is not True:
        raise ParityLabError(
            "TTD stop-reason adjudication was not declared from a recorder "
            f"receipt: {path}"
        )

    # An adjudication that disagrees with the summary it claims to explain is
    # worth less than no adjudication: one of the two is wrong and neither can
    # be trusted.  The resolved exit code is checked against the same rule the
    # wrapper applies (Resolve-CoverageExitCode): a quarantine survives
    # adjudication, so it lands on 11 rather than 0.
    accepted = terminal.get("acceptedStopReasons")
    contradictions = (
        (terminal.get("stopReason") != stop_reason, "stop reason"),
        (terminal.get("baseStopReasonMet") is not False, "baseStopReasonMet"),
        (terminal.get("stopReasonAccepted") is not True, "stopReasonAccepted"),
        (terminal.get("terminalStopAccepted") is not True, "terminalStopAccepted"),
        (terminal.get("positionReached") is not True, "positionReached"),
        (
            not isinstance(accepted, list) or stop_reason not in accepted,
            "acceptedStopReasons",
        ),
        (
            terminal.get("markerAssertionsPassed") != marker_assertions_passed,
            "markerAssertionsPassed",
        ),
        (terminal.get("replayComplete") != replay_complete, "replayComplete"),
        (
            terminal.get("finalPosition") != summary.get("final_position"),
            "finalPosition",
        ),
        (
            terminal.get("requestedTo") != metadata.get("requested_to"),
            "requestedTo",
        ),
        (payload.get("collectorExitCode") != 10, "collectorExitCode"),
        (
            payload.get("countersQuarantined") != counters_quarantined,
            "countersQuarantined",
        ),
        (
            payload.get("exitCode") != (11 if counters_quarantined else 0),
            "exitCode",
        ),
    )
    for contradicted, field in contradictions:
        if contradicted:
            raise ParityLabError(
                "TTD stop-reason adjudication contradicts its own coverage "
                f"({field}): {path}"
            )

    return {
        "receiptPath": str(found["path"]),
        "stopReason": stop_reason,
        "baseTerminalReason": terminal.get("baseTerminalReason"),
        "acceptedStopReasons": list(accepted),
        "exitCode": payload.get("exitCode"),
        "collectorExitCode": payload.get("collectorExitCode"),
    }


def ingest_ttd_exec_coverage(
    connection: sqlite3.Connection, path: pathlib.Path
) -> tuple[dict[str, Any], int]:
    """Validate and index native TTD Replay execute-coverage JSONL."""

    facts = artifact_facts(path, "ttd-exec-coverage")
    metadata: dict[str, Any] | None = None
    gap_summary: dict[str, Any] | None = None
    summary: dict[str, Any] | None = None
    ranges: list[dict[str, Any]] = []
    assertions: list[dict[str, Any]] = []
    kinds: list[str] = []

    with path.open("r", encoding="utf-8", newline="") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            text = raw_line.rstrip("\r\n")
            if not text:
                raise ParityLabError(
                    f"Blank line in TTD execute coverage {path}:{line_number}"
                )
            row = json.loads(text)
            if not isinstance(row, dict):
                raise ParityLabError(
                    f"Non-object TTD execute coverage row {path}:{line_number}"
                )
            if row.get("schema") != "bea.ttd.exec-coverage.v1":
                raise ParityLabError(
                    f"Unexpected TTD execute coverage schema {path}:{line_number}"
                )
            kind = row.get("kind")
            if not isinstance(kind, str):
                raise ParityLabError(
                    f"Missing TTD execute coverage kind {path}:{line_number}"
                )
            kinds.append(kind)
            if kind == "metadata":
                if metadata is not None:
                    raise ParityLabError(f"Duplicate TTD coverage metadata: {path}")
                metadata = row
            elif kind == "range":
                ranges.append(row)
            elif kind == "assertion":
                assertions.append(row)
            elif kind == "gap-summary":
                if gap_summary is not None:
                    raise ParityLabError(f"Duplicate TTD gap summary: {path}")
                gap_summary = row
            elif kind == "summary":
                if summary is not None:
                    raise ParityLabError(f"Duplicate TTD coverage summary: {path}")
                summary = row
            else:
                raise ParityLabError(
                    f"Unsupported TTD execute coverage kind {kind!r}: {path}"
                )

    if not kinds or kinds[0] != "metadata" or kinds[-1] != "summary":
        raise ParityLabError(
            f"TTD coverage must begin with metadata and end with summary: {path}"
        )
    if metadata is None or gap_summary is None or summary is None:
        raise ParityLabError(
            f"TTD coverage lacks metadata, gap-summary, or summary: {path}"
        )
    if kinds.count("gap-summary") != 1:
        raise ParityLabError(f"TTD coverage must contain one gap summary: {path}")

    def decimal_string(row: dict[str, Any], key: str) -> tuple[str, int]:
        value = row.get(key)
        if not isinstance(value, str) or not re.fullmatch(r"[0-9]+", value):
            raise ParityLabError(
                f"TTD coverage field {key} must be a decimal string: {path}"
            )
        return value, int(value, 10)

    def typed_bool(row: dict[str, Any], key: str) -> bool:
        value = row.get(key)
        if type(value) is not bool:
            raise ParityLabError(
                f"TTD coverage field {key} must be boolean: {path}"
            )
        return value

    if metadata.get("uint64_encoding") != "decimal-string":
        raise ParityLabError(f"Unsupported TTD uint64 encoding: {path}")
    if metadata.get("range_semantics") != "half-open-byte-ranges":
        raise ParityLabError(f"Unsupported TTD range semantics: {path}")
    if metadata.get("window_semantics") != "inclusive-position-bounds":
        raise ParityLabError(f"Unsupported TTD window semantics: {path}")
    replay_mode = metadata.get("replay_mode")
    if replay_mode not in {"parallel", "sequential"}:
        raise ParityLabError(f"Unsupported TTD replay mode: {path}")
    trace_path = metadata.get("trace")
    module_name = metadata.get("module_name")
    module_requested = metadata.get("module_requested")
    module_load_sequence_text = metadata.get("module_load_sequence")
    module_unload_sequence_text = metadata.get("module_unload_sequence")
    lifetime_min_text = metadata.get("lifetime_min")
    lifetime_max_text = metadata.get("lifetime_max")
    requested_from = metadata.get("requested_from")
    requested_to = metadata.get("requested_to")
    for key, value in {
        "trace": trace_path,
        "module_name": module_name,
        "module_requested": module_requested,
        "module_load_sequence": module_load_sequence_text,
        "module_unload_sequence": module_unload_sequence_text,
        "lifetime_min": lifetime_min_text,
        "lifetime_max": lifetime_max_text,
        "requested_from": requested_from,
        "requested_to": requested_to,
    }.items():
        if not isinstance(value, str) or not value:
            raise ParityLabError(f"Missing TTD metadata string {key}: {path}")
    trace_bytes_text, trace_bytes = decimal_string(metadata, "trace_bytes")
    module_base = parse_hex_int(metadata.get("module_base"), field="module_base")
    module_size = parse_hex_int(metadata.get("module_size"), field="module_size")
    module_timestamp = parse_hex_int(
        metadata.get("module_timestamp"), field="module_timestamp"
    )
    module_checksum = parse_hex_int(
        metadata.get("module_checksum"), field="module_checksum"
    )
    module_load_sequence = parse_hex_int(
        module_load_sequence_text, field="module_load_sequence"
    )
    module_unload_sequence = parse_hex_int(
        module_unload_sequence_text, field="module_unload_sequence"
    )
    if module_size <= 0 or module_timestamp > 0xFFFFFFFF or module_checksum > 0xFFFFFFFF:
        raise ParityLabError(f"Invalid TTD module identity tuple: {path}")
    if (
        module_load_sequence > 0xFFFFFFFFFFFFFFFF
        or module_unload_sequence > 0xFFFFFFFFFFFFFFFF
        or metadata.get("watchpoint_access") != "execute"
        or metadata.get("collector") != "parallel-safe-atomic-byte-bitmap"
    ):
        raise ParityLabError(f"Invalid TTD module-instance/collector metadata: {path}")
    lifetime_min = parse_ttd_position(lifetime_min_text, field="lifetime_min")
    lifetime_max = parse_ttd_position(lifetime_max_text, field="lifetime_max")
    requested_from_position = parse_ttd_position(
        requested_from, field="requested_from"
    )
    requested_to_position = parse_ttd_position(requested_to, field="requested_to")
    if not (
        lifetime_min
        <= requested_from_position
        <= requested_to_position
        <= lifetime_max
    ):
        raise ParityLabError(f"TTD requested window lies outside trace lifetime: {path}")
    if (
        requested_from_position[0] < module_load_sequence
        or requested_to_position[0] >= module_unload_sequence
    ):
        raise ParityLabError(
            f"TTD requested window lies outside selected module-instance lifetime: {path}"
        )

    covered_from_ranges = 0
    previous_end = 0
    for ordinal, row in enumerate(ranges):
        if type(row.get("index")) is not int or row["index"] != ordinal:
            raise ParityLabError(
                f"TTD range index is not dense at ordinal {ordinal}: {path}"
            )
        start = parse_hex_int(row.get("rva_start"), field="rva_start")
        end = parse_hex_int(
            row.get("rva_end_exclusive"), field="rva_end_exclusive"
        )
        va_start = parse_hex_int(row.get("va_start"), field="va_start")
        va_end = parse_hex_int(
            row.get("va_end_exclusive"), field="va_end_exclusive"
        )
        byte_count = row.get("byte_count")
        if type(byte_count) is not int:
            raise ParityLabError(f"TTD range byte_count must be integer: {path}")
        if (
            start < previous_end
            or start >= end
            or end > module_size
            or byte_count != end - start
            or va_start != module_base + start
            or va_end != module_base + end
        ):
            raise ParityLabError(
                f"Invalid/overlapping TTD range at ordinal {ordinal}: {path}"
            )
        previous_end = end
        covered_from_ranges += byte_count

    assertion_passes: list[bool] = []
    for ordinal, row in enumerate(assertions):
        expectation = row.get("expectation")
        if expectation not in {"hit", "miss"}:
            raise ParityLabError(f"Invalid TTD assertion expectation: {path}")
        observed = typed_bool(row, "observed")
        passed = typed_bool(row, "pass")
        rva = parse_hex_int(row.get("rva"), field="assertion rva")
        va = parse_hex_int(row.get("va"), field="assertion va")
        expected_pass = observed if expectation == "hit" else not observed
        covered_by_ranges = any(
            parse_hex_int(item.get("rva_start")) <= rva
            < parse_hex_int(item.get("rva_end_exclusive"))
            for item in ranges
        )
        if (
            rva >= module_size
            or va != module_base + rva
            or observed != covered_by_ranges
            or passed != expected_pass
        ):
            raise ParityLabError(
                f"Inconsistent TTD assertion at ordinal {ordinal}: {path}"
            )
        assertion_passes.append(passed)

    gap_total_text, gap_total = decimal_string(gap_summary, "total")
    gap_kinds = [
        decimal_string(gap_summary, key)[1]
        for key in (
            "kind_no_gap",
            "kind_context_switch",
            "kind_unrecorded",
            "kind_large",
        )
    ]
    gap_events = [
        decimal_string(gap_summary, key)[1]
        for key in sorted(gap_summary)
        if key.startswith("event_")
    ]
    if len(gap_events) != 17 or sum(gap_kinds) != gap_total or sum(gap_events) != gap_total:
        raise ParityLabError(f"TTD gap accounting does not close: {path}")

    range_count = summary.get("range_count")
    if type(range_count) is not int or range_count != len(ranges):
        raise ParityLabError(f"TTD summary range count mismatch: {path}")
    covered_bytes_text, covered_bytes = decimal_string(summary, "covered_bytes")
    if covered_bytes != covered_from_ranges:
        raise ParityLabError(f"TTD coverage summary accounting mismatch: {path}")

    # A producer may quarantine its replay counters when the replay engine's
    # own accounting is impossible (TTD Replay 1.11.584.0 stops advancing its
    # step counter on some traces).  Such a receipt stays fully valid for
    # ranges - they are collected by our own bitmap and were independently
    # recomputed - and is simply unscored for anything counter-derived.
    counters_quarantined = summary.get("counters_quarantined", False)
    if type(counters_quarantined) is not bool:
        raise ParityLabError(
            f"TTD coverage counters_quarantined must be a boolean: {path}"
        )
    counter_keys = ("callback_hits", "instructions_executed", "steps_executed")
    callback_hits_text: str | None = None
    callback_hits: int | None = None
    quarantined_counters: dict[str, Any] | None = None
    if counters_quarantined:
        leaked = [key for key in counter_keys if key in summary]
        if leaked:
            raise ParityLabError(
                "TTD coverage summary is quarantined but still carries "
                f"top-level counters {sorted(leaked)}: {path}"
            )
        quarantined_counters = summary.get("quarantined_counters")
        if not isinstance(quarantined_counters, dict):
            raise ParityLabError(
                f"TTD quarantined coverage lacks quarantined_counters: {path}"
            )
        for key in counter_keys:
            decimal_string(quarantined_counters, key)
        reason = quarantined_counters.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            raise ParityLabError(
                f"TTD quarantined counters lack a reason: {path}"
            )
    else:
        callback_hits_text, callback_hits = decimal_string(
            summary, "callback_hits"
        )
        steps_executed = decimal_string(summary, "steps_executed")[1]
        instructions_executed = decimal_string(
            summary, "instructions_executed"
        )[1]
        if (
            callback_hits < len(ranges)
            or callback_hits > instructions_executed
            or instructions_executed > steps_executed
        ):
            raise ParityLabError(
                f"TTD coverage summary accounting mismatch: {path}"
            )
    replay_complete = typed_bool(summary, "replay_complete")
    marker_assertions_passed = typed_bool(summary, "marker_assertions_passed")
    collector_checks_passed = typed_bool(summary, "collector_checks_passed")
    if marker_assertions_passed != all(assertion_passes):
        raise ParityLabError(f"TTD marker summary does not match assertions: {path}")
    if collector_checks_passed != (
        replay_complete and marker_assertions_passed
    ):
        raise ParityLabError(f"TTD collector-check summary is inconsistent: {path}")
    stop_reason = summary.get("stop_reason")
    stop_reason_adjudication: dict[str, Any] | None = None
    if stop_reason not in {"Position", "Process"}:
        # #153: an alive-at-stop trace ends on a Thread event, and the wrapper
        # adjudicates that for the trace class its caller declared.  Accepted
        # here on the wrapper's evidence, never on the stop reason alone.
        stop_reason_adjudication = _adjudicated_stop_evidence(
            path,
            facts["sha256"],
            str(stop_reason),
            summary,
            metadata,
            counters_quarantined=counters_quarantined,
            replay_complete=replay_complete,
            marker_assertions_passed=marker_assertions_passed,
        )
    stop_reason_adjudicated = stop_reason_adjudication is not None
    final_position = parse_ttd_position(
        summary.get("final_position"), field="final_position"
    )
    # An adjudicated stop is held to the whole-lifetime rule the Process branch
    # applies: the run was asked for everything and reached everything it was
    # asked for.  Only the terminal EVENT was ever in dispute.
    whole_lifetime_reached = (
        requested_to_position == lifetime_max
        and final_position >= requested_to_position
    )
    if (
        (stop_reason == "Position" and final_position != requested_to_position)
        or (stop_reason == "Process" and not whole_lifetime_reached)
        or (stop_reason_adjudicated and not whole_lifetime_reached)
    ):
        raise ParityLabError(f"TTD final position disagrees with stop reason: {path}")

    # Capture completeness and scenario-marker truth are independent.  The
    # producer's legacy collector_checks_passed field is an acceptance
    # conjunction (replay complete AND markers pass), not a health signal.
    #
    # replay_complete stays honestly false on an adjudicated trace - the guest
    # really was still running - so completeness is read from the pair the
    # wrapper resolved, not from that flag.  For every other trace the two
    # expressions below are identical to what they have always been.
    health = "COMPLETE" if (replay_complete or stop_reason_adjudicated) else "ERROR"
    acceptance_passed = marker_assertions_passed and (
        replay_complete or stop_reason_adjudicated
    )
    artifact_id = add_artifact(
        connection,
        facts,
        schema_version="bea.ttd.exec-coverage.v1",
        health=health,
    )
    cursor = connection.execute(
        """
        INSERT INTO ttd_exec_coverage(
            artifact_id, trace_path, trace_bytes, module_name, module_base,
            module_size, module_timestamp, module_checksum, replay_mode,
            requested_from, requested_to, range_count, covered_bytes,
            callback_hits, counters_quarantined, stop_reason,
            stop_reason_adjudicated, replay_complete,
            marker_assertions_passed, collector_checks_passed,
            metadata_json, gap_json, summary_json
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
        """,
        (
            artifact_id,
            trace_path,
            trace_bytes_text,
            module_name,
            module_base,
            module_size,
            module_timestamp,
            module_checksum,
            replay_mode,
            requested_from,
            requested_to,
            range_count,
            covered_bytes_text,
            callback_hits_text,
            int(counters_quarantined),
            stop_reason,
            int(stop_reason_adjudicated),
            int(replay_complete),
            int(marker_assertions_passed),
            int(collector_checks_passed),
            json.dumps(metadata, sort_keys=True),
            json.dumps(gap_summary, sort_keys=True),
            json.dumps(summary, sort_keys=True),
        ),
    )
    coverage_id = int(cursor.lastrowid)
    for ordinal, row in enumerate(ranges):
        connection.execute(
            """
            INSERT INTO ttd_exec_range(
                coverage_id, ordinal, rva_start, rva_end_exclusive,
                va_start, va_end_exclusive, byte_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                coverage_id,
                ordinal,
                parse_hex_int(row["rva_start"]),
                parse_hex_int(row["rva_end_exclusive"]),
                parse_hex_int(row["va_start"]),
                parse_hex_int(row["va_end_exclusive"]),
                row["byte_count"],
            ),
        )
    for ordinal, row in enumerate(assertions):
        connection.execute(
            """
            INSERT INTO ttd_exec_assertion(
                coverage_id, ordinal, expectation, rva, va, observed, pass
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                coverage_id,
                ordinal,
                row["expectation"],
                parse_hex_int(row["rva"]),
                parse_hex_int(row["va"]),
                int(row["observed"]),
                int(row["pass"]),
            ),
        )
    assert_artifact_unchanged(path, facts)
    return (
        {
            **facts,
            "artifactId": artifact_id,
            "coverageId": coverage_id,
            "schemaVersion": "bea.ttd.exec-coverage.v1",
            "health": health,
            "trace": trace_path,
            "traceBytes": trace_bytes,
            "moduleName": module_name,
            "moduleBase": f"0x{module_base:X}",
            "moduleSize": f"0x{module_size:X}",
            "moduleTimestamp": f"0x{module_timestamp:X}",
            "moduleChecksum": f"0x{module_checksum:X}",
            "moduleRequested": module_requested,
            "moduleLoadSequence": f"0x{module_load_sequence:X}",
            "moduleUnloadSequence": f"0x{module_unload_sequence:X}",
            "lifetimeMin": lifetime_min_text,
            "lifetimeMax": lifetime_max_text,
            "moduleInstancePolicy": "exactly-one-active-for-window",
            "replayMode": replay_mode,
            "requestedFrom": requested_from,
            "requestedTo": requested_to,
            "rangeCount": range_count,
            "coveredBytes": covered_bytes,
            "callbackHits": callback_hits,
            "countersQuarantined": counters_quarantined,
            "quarantinedCounters": quarantined_counters,
            "counterScoring": "unscored" if counters_quarantined else "scored",
            "assertionCount": len(assertions),
            "gapCount": gap_total,
            "stopReason": stop_reason,
            "stopReasonAdjudicated": stop_reason_adjudicated,
            "stopReasonAdjudication": stop_reason_adjudication,
            "replayComplete": replay_complete,
            "markerAssertionsPassed": marker_assertions_passed,
            "collectorChecksPassed": collector_checks_passed,
            "acceptancePassed": acceptance_passed,
        },
        artifact_id,
    )


def ingest_ttd_exec_receipt(
    connection: sqlite3.Connection, path: pathlib.Path
) -> tuple[dict[str, Any], int]:
    """Validate the identity receipt emitted around a Replay coverage run."""

    facts = artifact_facts(path, "ttd-exec-coverage-receipt")
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise ParityLabError(f"TTD execute receipt is not an object: {path}")
    schema = payload.get("schemaVersion")
    if schema not in {
        "bea-ttd-exec-coverage-receipt.v1",
        "bea-ttd-exec-coverage-receipt.v2",
    }:
        raise ParityLabError(f"Unsupported TTD execute receipt schema: {path}")

    def nested_facts(key: str) -> dict[str, Any]:
        value = payload.get(key)
        if not isinstance(value, dict):
            raise ParityLabError(f"TTD execute receipt lacks {key}: {path}")
        if not isinstance(value.get("path"), str):
            raise ParityLabError(f"TTD execute receipt {key} lacks a path: {path}")
        if type(value.get("bytes")) is not int or not isinstance(
            value.get("sha256"), str
        ):
            raise ParityLabError(
                f"TTD execute receipt {key} lacks typed size/hash: {path}"
            )
        return value

    trace = nested_facts("trace")
    target = nested_facts("target")
    collector = nested_facts("collector")
    coverage = nested_facts("coverage")
    replay_runtime = payload.get("replayRuntime")
    if not isinstance(replay_runtime, dict) or not isinstance(
        replay_runtime.get("version"), str
    ):
        raise ParityLabError(f"TTD execute receipt lacks replay runtime: {path}")
    replay = replay_runtime.get("replay")
    replay_cpu = replay_runtime.get("replayCpu")
    if not isinstance(replay, dict) or not isinstance(replay_cpu, dict):
        raise ParityLabError(f"TTD execute receipt runtime lacks DLL facts: {path}")
    for label, value in (("replay", replay), ("replayCpu", replay_cpu)):
        if (
            not isinstance(value.get("path"), str)
            or type(value.get("bytes")) is not int
            or not isinstance(value.get("sha256"), str)
        ):
            raise ParityLabError(
                f"TTD execute receipt runtime {label} facts are invalid: {path}"
            )
    target_pe = target.get("pe")
    if not isinstance(target_pe, dict):
        raise ParityLabError(f"TTD execute receipt target lacks PE identity: {path}")
    for pe_key in ("timestamp", "sizeOfImage", "checksum"):
        parse_hex_int(target_pe.get(pe_key), field=f"target PE {pe_key}")
    trace_path = pathlib.Path(trace["path"])
    trace_facts = artifact_facts(trace_path, "ttd-exec-trace")
    trace_exists = True
    trace_size_matches = trace_facts["bytes"] == trace["bytes"]
    trace_hash_matches = (
        trace_facts["sha256"].upper() == trace_or_hash(trace["sha256"])
    )
    trace_sha256 = trace_or_hash(trace["sha256"])

    target_path = pathlib.Path(target["path"])
    target_facts = artifact_facts(target_path, "ttd-exec-target")
    target_matches = (
        target_facts["bytes"] == target["bytes"]
        and target_facts["sha256"].upper() == trace_or_hash(target["sha256"])
    )
    coverage_path = pathlib.Path(coverage["path"])
    coverage_facts = artifact_facts(coverage_path, "ttd-exec-coverage-linked")
    coverage_matches = (
        coverage_facts["bytes"] == coverage["bytes"]
        and coverage_facts["sha256"].upper() == trace_or_hash(coverage["sha256"])
    )
    collector_path = pathlib.Path(collector["path"])
    collector_facts = artifact_facts(collector_path, "ttd-exec-collector")
    collector_matches = (
        collector_facts["bytes"] == collector["bytes"]
        and collector_facts["sha256"].upper() == trace_or_hash(collector["sha256"])
    )
    replay_facts = artifact_facts(
        pathlib.Path(replay["path"]), "ttd-exec-replay-runtime"
    )
    replay_cpu_facts = artifact_facts(
        pathlib.Path(replay_cpu["path"]), "ttd-exec-replay-cpu-runtime"
    )
    replay_matches = (
        replay_facts["bytes"] == replay["bytes"]
        and replay_facts["sha256"].upper() == trace_or_hash(replay["sha256"])
    )
    replay_cpu_matches = (
        replay_cpu_facts["bytes"] == replay_cpu["bytes"]
        and replay_cpu_facts["sha256"].upper()
        == trace_or_hash(replay_cpu["sha256"])
    )
    build_receipt_result: dict[str, Any] | None = None
    build_receipt_matches = True
    if schema == "bea-ttd-exec-coverage-receipt.v2":
        build_receipt = payload.get("buildReceipt")
        if (
            not isinstance(build_receipt, dict)
            or not isinstance(build_receipt.get("path"), str)
            or type(build_receipt.get("bytes")) is not int
            or not isinstance(build_receipt.get("sha256"), str)
        ):
            raise ParityLabError(
                f"TTD execute v2 receipt lacks immutable build receipt facts: {path}"
            )
        measured_build = artifact_facts(
            pathlib.Path(build_receipt["path"]), "ttd-exec-build-receipt"
        )
        build_receipt_matches = (
            measured_build["bytes"] == build_receipt["bytes"]
            and measured_build["sha256"].upper()
            == trace_or_hash(build_receipt["sha256"])
        )
        build_payload = json.loads(
            pathlib.Path(build_receipt["path"]).read_text(encoding="utf-8-sig")
        )
        build_schema = (
            build_payload.get("schemaVersion")
            if isinstance(build_payload, dict)
            else None
        )
        build_reproducibility_verified = False
        if build_schema == "bea-ttd-exec-coverage-build.v2":
            reproducibility = build_payload.get("reproducibility")
            isolated_builds = (
                reproducibility.get("isolatedBuilds")
                if isinstance(reproducibility, dict)
                else None
            )
            build_reproducibility_verified = (
                isinstance(isolated_builds, list)
                and len(isolated_builds) == 2
                and reproducibility.get("buildCount") == 2
                and reproducibility.get("byteIdentical") is True
                and reproducibility.get("distinctOutputRoots") is True
                and reproducibility.get("allSelfTestsPassed") is True
                and reproducibility.get("pdbAlternatePath")
                == "ttd_exec_coverage.pdb"
                and isolated_builds[0].get("root")
                != isolated_builds[1].get("root")
                and all(
                    row.get("bytes") == collector["bytes"]
                    and str(row.get("sha256", "")).upper()
                    == collector["sha256"].upper()
                    and row.get("selfTest") == "PASS"
                    for row in isolated_builds
                    if isinstance(row, dict)
                )
                and all(isinstance(row, dict) for row in isolated_builds)
            )
        if (
            not isinstance(build_payload, dict)
            or build_schema
            not in {
                "bea-ttd-exec-coverage-build.v1",
                "bea-ttd-exec-coverage-build.v2",
            }
            or str(build_payload.get("collector", {}).get("sha256", "")).upper()
            != collector["sha256"].upper()
            or str(build_payload.get("runtime", {}).get("replaySha256", "")).upper()
            != replay["sha256"].upper()
            or str(
                build_payload.get("runtime", {}).get("replayCpuSha256", "")
            ).upper()
            != replay_cpu["sha256"].upper()
            or (
                build_schema == "bea-ttd-exec-coverage-build.v2"
                and not build_reproducibility_verified
            )
        ):
            build_receipt_matches = False
        build_receipt_result = {
            **measured_build,
            "schemaVersion": build_schema,
            "reproducibilityVerified": build_reproducibility_verified,
        }
    replay_complete = payload.get("replayComplete")
    markers_passed = payload.get("markerAssertionsPassed")
    acceptance_passed = payload.get("collectorChecksPassed")
    status_values = [replay_complete, markers_passed, acceptance_passed]
    if any(type(value) is not bool for value in status_values):
        raise ParityLabError(f"TTD execute receipt status fields are not booleans: {path}")
    if acceptance_passed != (replay_complete and markers_passed):
        raise ParityLabError(f"TTD execute receipt acceptance fields disagree: {path}")
    expected_exit_code = 0 if acceptance_passed else 10
    if payload.get("collectorExitCode") != expected_exit_code:
        raise ParityLabError(f"TTD execute receipt exit code is inconsistent: {path}")

    # #153: the wrapper may adjudicate a terminal stop the collector refused,
    # for the trace class its caller declared from the recorder receipt.  The
    # collector's own verdict is preserved beside it - collectorExitCode stays
    # 10 and collectorChecksPassed stays false - so the claim is only honoured
    # when the receipt's adjudication agrees with the rest of the receipt.
    stop_reason_adjudicated = payload.get("stopReasonAdjudicated", False)
    if type(stop_reason_adjudicated) is not bool:
        raise ParityLabError(
            f"TTD execute receipt stopReasonAdjudicated is not a boolean: {path}"
        )
    terminal_stop = payload.get("terminalStop")
    counters_quarantined = payload.get("countersQuarantined", False)
    if stop_reason_adjudicated:
        invocation = payload.get("invocation")
        declared = isinstance(invocation, dict) and invocation.get(
            "expectAliveAtStop"
        ) is True
        if not isinstance(terminal_stop, dict) or not declared:
            raise ParityLabError(
                "TTD stop-reason adjudication was not declared from a recorder "
                f"receipt: {path}"
            )
        for contradicted, field in (
            (terminal_stop.get("aliveAtStopExpected") is not True, "aliveAtStopExpected"),
            (terminal_stop.get("baseStopReasonMet") is not False, "baseStopReasonMet"),
            (terminal_stop.get("stopReasonAccepted") is not True, "stopReasonAccepted"),
            (
                terminal_stop.get("terminalStopAccepted") is not True,
                "terminalStopAccepted",
            ),
            (terminal_stop.get("positionReached") is not True, "positionReached"),
            (terminal_stop.get("replayComplete") != replay_complete, "replayComplete"),
            (
                terminal_stop.get("markerAssertionsPassed") != markers_passed,
                "markerAssertionsPassed",
            ),
            (
                terminal_stop.get("stopReason")
                not in TTD_ADJUDICABLE_STOP_REASONS,
                "stopReason",
            ),
            (
                payload.get("exitCode") != (11 if counters_quarantined else 0),
                "exitCode",
            ),
        ):
            if contradicted:
                raise ParityLabError(
                    "TTD stop-reason adjudication contradicts its own receipt "
                    f"({field}): {path}"
                )
    health = (
        "COMPLETE"
        if (
            (replay_complete or stop_reason_adjudicated)
            and trace_size_matches
            and trace_hash_matches
            and target_matches
            and coverage_matches
            and collector_matches
            and replay_matches
            and replay_cpu_matches
            and build_receipt_matches
        )
        else "ERROR"
    )
    artifact_id = add_artifact(
        connection, facts, schema_version=str(schema), health=health
    )
    assert_artifact_unchanged(path, facts)
    return (
        {
            **facts,
            "artifactId": artifact_id,
            "schemaVersion": schema,
            "health": health,
            "trace": trace["path"],
            "traceBytes": trace["bytes"],
            "traceSha256": trace_sha256,
            "traceArtifact": trace_facts,
            "traceExists": trace_exists,
            "traceSizeMatches": trace_size_matches,
            "traceHashMatches": trace_hash_matches,
            "target": target["path"],
            "targetBytes": target["bytes"],
            "targetSha256": target["sha256"].upper(),
            "targetMatches": target_matches,
            "targetPe": target_pe,
            "coverage": coverage["path"],
            "coverageBytes": coverage["bytes"],
            "coverageSha256": coverage["sha256"].upper(),
            "coverageMatches": coverage_matches,
            "collectorSha256": collector["sha256"].upper(),
            "collectorMatches": collector_matches,
            "replayRuntimeVersion": replay_runtime["version"],
            "replaySha256": replay["sha256"].upper(),
            "replayCpuSha256": replay_cpu["sha256"].upper(),
            "replayRuntimeMatches": replay_matches and replay_cpu_matches,
            "buildReceipt": build_receipt_result,
            "buildReceiptMatches": build_receipt_matches,
            "assertionCount": coverage.get("assertionCount"),
            "replayComplete": payload["replayComplete"],
            "markerAssertionsPassed": payload["markerAssertionsPassed"],
            "collectorChecksPassed": payload["collectorChecksPassed"],
            # The collector's raw verdict stays above, untouched.  Acceptance
            # is the resolved one: markers passed, and the replay either ran to
            # the end or its terminal stop was adjudicated for this class.
            "acceptancePassed": markers_passed
            and (replay_complete or stop_reason_adjudicated),
            "stopReasonAdjudicated": stop_reason_adjudicated,
            "stopReason": (
                terminal_stop.get("stopReason")
                if isinstance(terminal_stop, dict)
                else None
            ),
            "collectorExitCode": payload["collectorExitCode"],
            "exitCode": payload.get("exitCode", payload["collectorExitCode"]),
        },
        artifact_id,
    )


def trace_or_hash(value: Any) -> str:
    text = str(value).upper()
    if not re.fullmatch(r"[0-9A-F]{64}", text):
        raise ParityLabError(f"Invalid SHA-256 in TTD execute receipt: {value!r}")
    return text


def ingest_shot_manifest(
    connection: sqlite3.Connection, path: pathlib.Path
) -> dict[str, Any]:
    facts = artifact_facts(path, "d3d9-shot-manifest")
    artifact_id = add_artifact(connection, facts, schema_version="d3d9-shot-manifest.csv")
    data_rows = 0
    comment_rows = 0
    malformed_rows = 0
    missing_images: list[str] = []
    image_artifacts: list[dict[str, Any]] = []
    footer: dict[str, str] | None = None
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        lines = handle.readlines()
    header_index = next(
        (index for index, line in enumerate(lines) if line.lower().startswith("frame,")), None
    )
    if header_index is None:
        raise ParityLabError(f"Shot manifest has no CSV header: {path}")
    for line_number, raw_line in enumerate(lines[:header_index], start=1):
        stripped = raw_line.rstrip("\r\n")
        if not stripped.startswith("#"):
            malformed_rows += 1
            continue
        comment_rows += 1
        fields = parse_kv_tokens(stripped[1:].strip())
        connection.execute(
            """
            INSERT INTO shot_comment(artifact_id, line_number, text, fields_json)
            VALUES (?, ?, ?, ?)
            """,
            (artifact_id, line_number, stripped, json.dumps(fields, sort_keys=True)),
        )
    required = {
        "frame",
        "written",
        "file",
        "w",
        "h",
        "d3dfmt",
        "meanR",
        "meanG",
        "meanB",
        "maxCellDelta",
    }
    header = next(csv.reader([lines[header_index].rstrip("\r\n")]))
    if not required.issubset(header):
        raise ParityLabError(f"Unexpected shot manifest columns in {path}")
    for line_number, raw_line in enumerate(lines[header_index + 1 :], start=header_index + 2):
        stripped = raw_line.rstrip("\r\n")
        if not stripped:
            continue
        if stripped.startswith("#"):
            comment_rows += 1
            fields = parse_kv_tokens(stripped[1:].strip())
            connection.execute(
                """
                INSERT INTO shot_comment(artifact_id, line_number, text, fields_json)
                VALUES (?, ?, ?, ?)
                """,
                (artifact_id, line_number, stripped, json.dumps(fields, sort_keys=True)),
            )
            if {"written", "dead", "leaked-surface"}.issubset(fields):
                footer = fields
            continue
        try:
            values = next(csv.reader([stripped]))
            if len(values) != len(header):
                raise ValueError("column count")
            row = dict(zip(header, values))
            ordinal = data_rows
            connection.execute(
                """
                INSERT INTO shot_sample(
                    artifact_id, ordinal, frame, written, file, width, height,
                    d3d_format, mean_r, mean_g, mean_b, max_cell_delta, raw_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    artifact_id,
                    ordinal,
                    int(row["frame"]),
                    int(row["written"]),
                    row["file"],
                    int(row["w"]),
                    int(row["h"]),
                    int(row["d3dfmt"]),
                    float(row["meanR"]),
                    float(row["meanG"]),
                    float(row["meanB"]),
                    float(row["maxCellDelta"]),
                    json.dumps(row, sort_keys=True),
                ),
            )
            if int(row["written"]) == 1:
                image_path = (path.parent / row["file"]).resolve()
                if not image_path.is_file():
                    missing_images.append(str(image_path))
                else:
                    image_facts = artifact_facts(image_path, "d3d9-shot-image")
                    add_artifact(
                        connection,
                        image_facts,
                        schema_version="png",
                        health="COMPLETE",
                    )
                    image_artifacts.append(image_facts)
            data_rows += 1
        except (KeyError, TypeError, ValueError):
            malformed_rows += 1
    footer_written: int | None = None
    footer_dead: int | None = None
    if footer is not None:
        try:
            footer_written = int(footer["written"])
            footer_dead = int(footer["dead"])
        except (KeyError, ValueError):
            malformed_rows += 1
    written_rows = len(image_artifacts) + len(missing_images)
    footer_mismatch = footer_written is None or footer_written != written_rows
    health = (
        "COMPLETE"
        if (
            malformed_rows == 0
            and not missing_images
            and not footer_mismatch
            and footer_dead == 0
        )
        else "ERROR"
    )
    connection.execute(
        "UPDATE artifact SET health=? WHERE artifact_id=?", (health, artifact_id)
    )
    assert_artifact_unchanged(path, facts)
    return {
        **facts,
        "artifactId": artifact_id,
        "schemaVersion": "d3d9-shot-manifest.csv",
        "health": health,
        "dataRows": data_rows,
        "commentRows": comment_rows,
        "malformedRows": malformed_rows,
        "footer": footer,
        "footerWrittenMatches": not footer_mismatch,
        "missingImages": missing_images,
        "imageArtifacts": image_artifacts,
    }


def run_capture_bundle(args: argparse.Namespace) -> int:
    output = create_output_dir(pathlib.Path(args.out))
    database_path = output / "capture.sqlite"
    connection = open_database(database_path)
    connection.execute("INSERT INTO meta(key, value) VALUES (?, ?)", ("schema", BUNDLE_SCHEMA))
    connection.execute("INSERT INTO meta(key, value) VALUES (?, ?)", ("scenario", args.scenario))
    connection.execute("INSERT INTO meta(key, value) VALUES (?, ?)", ("role", args.role))

    target = artifact_facts(pathlib.Path(args.target_exe), "target-executable") if args.target_exe else None
    artifacts: list[dict[str, Any]] = []
    d3d9_results: list[dict[str, Any]] = []
    ttd_receipts: list[dict[str, Any]] = []
    ttd_results: list[dict[str, Any]] = []
    ttd_coverages: list[dict[str, Any]] = []
    ttd_coverage_receipts: list[dict[str, Any]] = []
    shot_results: list[dict[str, Any]] = []
    if target:
        add_artifact(connection, target)
        connection.execute(
            "INSERT INTO meta(key, value) VALUES (?, ?)",
            ("targetSha256", target["sha256"]),
        )

    for value in args.d3d9_log:
        path = pathlib.Path(value)
        facts = artifact_facts(path, "d3d9-proxy-log")
        artifact_id = add_artifact(
            connection, facts, schema_version="bea-d3d9-proxy.v1", health="PENDING"
        )
        parsed = parse_d3d9_log(path, connection, artifact_id)
        assert_artifact_unchanged(path, facts)
        connection.execute(
            "UPDATE artifact SET health=? WHERE artifact_id=?",
            (parsed.health, artifact_id),
        )
        result = {
            **facts,
            "artifactId": artifact_id,
            "schemaVersion": "bea-d3d9-proxy.v1",
            "health": parsed.health,
            "parseAccounting": {
                "totalLines": parsed.total_lines,
                "recognizedData": parsed.recognized_data,
                "recognizedComments": parsed.recognized_comments,
                "unknownRecords": parsed.unknown_records,
                "malformedRecords": parsed.malformed_records,
                "accountedLines": parsed.accounted_lines,
                "encodingErrors": parsed.encoding_errors,
            },
            "recordCounts": dict(sorted(parsed.record_counts.items())),
            "footerSeen": parsed.footer_seen,
            "declaredRefusals": parsed.declared_refusals,
            "observedRefusals": parsed.observed_refusals,
            "declaredWarnings": parsed.declared_warnings,
            "observedWarnings": parsed.observed_warnings,
            "presentDrawMismatches": parsed.present_draw_mismatches,
            "header": parsed.header,
            "diagnostics": parsed.diagnostics,
        }
        d3d9_results.append(result)
        artifacts.append(result)

    for value in args.ttd_receipt:
        result, _ = ingest_ttd_receipt(connection, pathlib.Path(value))
        ttd_receipts.append(result)
        artifacts.append(result)
    for value in args.ttd_result:
        result, _ = ingest_ttd_result(connection, pathlib.Path(value))
        ttd_results.append(result)
        artifacts.append(result)
    for value in args.ttd_coverage:
        result, _ = ingest_ttd_exec_coverage(connection, pathlib.Path(value))
        ttd_coverages.append(result)
        artifacts.append(result)
    for value in args.ttd_coverage_receipt:
        result, _ = ingest_ttd_exec_receipt(connection, pathlib.Path(value))
        ttd_coverage_receipts.append(result)
        artifacts.append(result)
    for value in args.shot_manifest:
        result = ingest_shot_manifest(connection, pathlib.Path(value))
        shot_results.append(result)
        artifacts.append(result)

    target_mismatches: list[str] = []
    if target:
        target_hash = target["sha256"].upper()
        for receipt in ttd_receipts:
            receipt_hash = str(receipt.get("targetSha256") or "").upper()
            if receipt_hash and receipt_hash != target_hash:
                target_mismatches.append(
                    f"TTD receipt {receipt['path']} targets {receipt_hash}, not {target_hash}"
                )
        for result in ttd_results:
            query_hash = str(result.get("knownAnswerSha256") or "").upper()
            if query_hash and query_hash != target_hash:
                target_mismatches.append(
                    f"TTD query {result['path']} known-answer targets "
                    f"{query_hash}, not {target_hash}"
                )
        for receipt in ttd_coverage_receipts:
            receipt_hash = str(receipt.get("targetSha256") or "").upper()
            if receipt_hash and receipt_hash != target_hash:
                target_mismatches.append(
                    f"TTD coverage receipt {receipt['path']} targets "
                    f"{receipt_hash}, not {target_hash}"
                )
        for result in d3d9_results:
            logged_exe = result.get("header", {}).get("exe")
            if logged_exe:
                try:
                    same = pathlib.Path(logged_exe).resolve() == pathlib.Path(args.target_exe).resolve()
                except OSError:
                    same = False
                if not same:
                    target_mismatches.append(
                        f"D3D9 log {result['path']} names executable {logged_exe}"
                    )

    linkage_mismatches: list[str] = []
    if ttd_receipts and ttd_results:
        receipt_traces = {
            (
                windows_path_key(row["traceFile"]),
                int(row["traceBytes"]),
                str(row.get("traceSha256") or "").upper(),
            )
            for row in ttd_receipts
            if row.get("traceFile") and isinstance(row.get("traceBytes"), int)
        }
        # A deferred receipt carries no hash, so it can never key-match a query
        # result (which always carries one).  That already fails closed; naming
        # the deferral turns an opaque linkage failure into a one-command fix.
        deferred_receipt_traces = {
            windows_path_key(row["traceFile"])
            for row in ttd_receipts
            if row.get("traceHashDeferred") and row.get("traceFile")
        }
        for result in ttd_results:
            key = (
                windows_path_key(str(result.get("trace", ""))),
                int(result.get("traceBytes", -1)),
                str(result.get("traceSha256") or "").upper(),
            )
            if key not in receipt_traces:
                if windows_path_key(str(result.get("trace", ""))) in (
                    deferred_receipt_traces
                ):
                    linkage_mismatches.append(
                        f"TTD query {result['path']} names a trace whose recorder "
                        "receipt defers its hash; complete it with "
                        "tools/ttd_record.ps1 -HashOnly before linking"
                    )
                else:
                    linkage_mismatches.append(
                        f"TTD query {result['path']} is not linked to an ingested receipt"
                    )

    coverage_receipts_by_hash: dict[str, list[dict[str, Any]]] = defaultdict(list)
    coverages_by_hash: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for receipt in ttd_coverage_receipts:
        coverage_receipts_by_hash[str(receipt["coverageSha256"]).upper()].append(receipt)
    for coverage in ttd_coverages:
        coverages_by_hash[str(coverage["sha256"]).upper()].append(coverage)
    for coverage in ttd_coverages:
        matches = coverage_receipts_by_hash.get(str(coverage["sha256"]).upper(), [])
        if len(matches) != 1:
            linkage_mismatches.append(
                f"TTD coverage {coverage['path']} has {len(matches)} matching receipt(s)"
            )
            continue
        receipt = matches[0]
        if (
            windows_path_key(str(coverage["trace"]))
            != windows_path_key(str(receipt["trace"]))
            or int(coverage["traceBytes"]) != int(receipt["traceBytes"])
            or int(coverage["assertionCount"])
            != int(receipt.get("assertionCount", -1))
            or coverage["replayComplete"] != receipt["replayComplete"]
            or coverage["markerAssertionsPassed"]
            != receipt["markerAssertionsPassed"]
            or coverage["acceptancePassed"] != receipt["acceptancePassed"]
        ):
            linkage_mismatches.append(
                f"TTD coverage {coverage['path']} trace/assertion/status identity "
                "disagrees with receipt"
            )
        if (
            windows_path_key(str(coverage["moduleName"]))
            != windows_path_key(str(receipt["target"]))
        ):
            linkage_mismatches.append(
                f"TTD coverage {coverage['path']} module path disagrees with target receipt"
            )
        target_pe = receipt["targetPe"]
        if (
            parse_hex_int(coverage["moduleSize"])
            != parse_hex_int(target_pe["sizeOfImage"])
            or parse_hex_int(coverage["moduleTimestamp"])
            != parse_hex_int(target_pe["timestamp"])
            or parse_hex_int(coverage["moduleChecksum"])
            != parse_hex_int(target_pe["checksum"])
        ):
            linkage_mismatches.append(
                f"TTD coverage {coverage['path']} PE identity disagrees with receipt"
            )
    for receipt in ttd_coverage_receipts:
        matches = coverages_by_hash.get(str(receipt["coverageSha256"]).upper(), [])
        if len(matches) != 1:
            linkage_mismatches.append(
                f"TTD coverage receipt {receipt['path']} has "
                f"{len(matches)} matching coverage artifact(s)"
            )

    connection.commit()
    connection.execute("VACUUM")
    connection.close()

    health_order = {"COMPLETE": 0, "PARTIAL": 1, "ERROR": 2, "REJECTED": 3}
    health_values = [str(artifact.get("health", "PARTIAL")) for artifact in artifacts]
    capture_health = (
        max(health_values, key=lambda value: health_order.get(value, 2))
        if health_values
        else "REJECTED"
    )
    if target_mismatches or linkage_mismatches:
        capture_health = "REJECTED"
    controlled_queries = bool(ttd_results) and all(
        result.get("health") == "COMPLETE"
        and result.get("controlsPassed") is True
        and result.get("traceHashMatches") is True
        for result in ttd_results
    ) and (
        not ttd_receipts
        or all(
            receipt.get("health") == "COMPLETE"
            and receipt.get("traceHashMatches") is True
            for receipt in ttd_receipts
        )
    )
    controlled_coverage = (
        bool(ttd_coverages)
        and bool(ttd_coverage_receipts)
        and all(
            result.get("acceptancePassed") is True
            and result.get("assertionCount", 0) > 0
            for result in ttd_coverages
        )
        and all(
            receipt.get("health") == "COMPLETE"
            and receipt.get("acceptancePassed") is True
            and isinstance(receipt.get("assertionCount"), int)
            and receipt["assertionCount"] > 0
            for receipt in ttd_coverage_receipts
        )
        and not linkage_mismatches
    )
    comparability = (
        "CORRELATED"
        if (controlled_queries or controlled_coverage)
        and capture_health in {"COMPLETE", "PARTIAL"}
        and not target_mismatches
        and not linkage_mismatches
        else "UNSCORED"
    )
    status_connection = sqlite3.connect(database_path)
    try:
        status_connection.executemany(
            "INSERT OR REPLACE INTO meta(key, value) VALUES (?, ?)",
            [
                ("captureHealth", capture_health),
                ("comparability", comparability),
                ("hypothesisVerdict", "UNKNOWN"),
            ],
        )
        status_connection.commit()
    finally:
        status_connection.close()
    manifest = {
        "schemaVersion": BUNDLE_SCHEMA,
        "toolVersion": TOOL_VERSION,
        "bundleId": args.bundle_id,
        "generatedAtUtc": utc_now(),
        "scenario": {
            "id": args.scenario,
            "role": args.role,
            "question": args.question,
            "action": args.action,
            "positiveControl": args.positive_control,
        },
        "target": target,
        "correlation": (
            "SCENARIO_ONLY"
            if d3d9_results
            and (ttd_receipts or ttd_results or ttd_coverages)
            else "SINGLE_INSTRUMENT"
        ),
        "artifacts": artifacts,
        "d3d9": d3d9_results,
        "ttdReceipts": ttd_receipts,
        "ttdResults": ttd_results,
        "ttdCoverage": ttd_coverages,
        "ttdCoverageReceipts": ttd_coverage_receipts,
        "shotManifests": shot_results,
        "captureHealth": capture_health,
        "comparability": comparability,
        "hypothesisVerdict": "UNKNOWN",
        "targetMismatches": target_mismatches,
        "linkageMismatches": linkage_mismatches,
        "limits": [
            "Raw artifacts remain authority; SQLite is a deterministic query projection.",
            "TTD and D3D9 captures in one bundle are separate runs unless an exact shared capture is explicitly proven.",
            "No absent event is evidence of absence when capture health is not COMPLETE.",
            "This schema records no exact cross-instrument time alignment.",
            "Free-text positive-control descriptions never upgrade comparability; "
            "only parsed TTD known-answer and negative-control results do.",
            "TTD execute ranges prove byte execution presence, not per-address frequency.",
            "A TTD execute receipt binds trace/target/collector hashes; bundle import "
            "rechecks target/collector/coverage hashes and rehashes trace content; "
            "the wrapper also proves the trace stayed unchanged during collection.",
        ],
        "outputs": {
            "database": artifact_facts(database_path, "capture-database"),
        },
    }
    write_json(output / "bundle.json", manifest)
    write_bundle_report(output / "report.md", manifest)
    print(
        f"capture bundle: health={capture_health} comparability={comparability} "
        f"artifacts={len(artifacts)}"
    )
    print(output / "bundle.json")
    return 0 if capture_health != "REJECTED" else 1


def write_bundle_report(path: pathlib.Path, manifest: dict[str, Any]) -> None:
    scenario = manifest["scenario"]
    lines = [
        f"# Capture bundle: {manifest['bundleId']}",
        "",
        f"Scenario: `{scenario['id']}` / `{scenario['role']}`  ",
        f"Capture health: **{manifest['captureHealth']}**  ",
        f"Comparability: **{manifest['comparability']}**  ",
        f"Hypothesis verdict: **{manifest['hypothesisVerdict']}**",
        "",
        "## Evidence boundary",
        "",
        "The raw artifacts named and hashed in `bundle.json` remain authoritative. "
        "The SQLite database is a lossless line/event index where supported and "
        "retains unknown or malformed D3D9 records explicitly.",
        "",
        "## Artifacts",
        "",
        "| Kind | Bytes | SHA-256 | Health | Path |",
        "| --- | ---: | --- | --- | --- |",
    ]
    for artifact in manifest["artifacts"]:
        lines.append(
            f"| `{artifact['kind']}` | {artifact['bytes']} | "
            f"`{artifact['sha256']}` | `{artifact.get('health', '')}` | "
            f"`{artifact['path']}` |"
        )
    lines.extend(
        [
            "",
            "## Status separation",
            "",
            f"- Capture health: `{manifest['captureHealth']}`",
            f"- Comparability: `{manifest['comparability']}`",
            f"- Hypothesis: `{manifest['hypothesisVerdict']}`",
            "",
            "These are independent. A complete capture can leave the hypothesis "
            "unknown; an unscored comparison is never a pass.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def sanitize_symbol_name(name: str, address: int) -> str:
    result = re.sub(r"[^A-Za-z0-9_?$@]", "_", name)
    result = re.sub(r"_+", "_", result).strip("_")
    if not result:
        result = f"Function_{address:08X}"
    if result[0].isdigit():
        result = f"Function_{result}"
    return result


def bounded_symbol_name(
    prefix: str, suffix: str, *, address: int, maximum: int = 220
) -> str:
    clean_prefix = sanitize_symbol_name(prefix, address)
    clean_suffix = sanitize_symbol_name(suffix, address)
    separator = "_"
    if len(clean_suffix) + len(separator) >= maximum:
        raise ParityLabError("Symbol identity suffix exceeds debugger name limit")
    return (
        clean_prefix[: maximum - len(separator) - len(clean_suffix)]
        + separator
        + clean_suffix
    )


def run_symbol_map(args: argparse.Namespace) -> int:
    inventory = pathlib.Path(args.ghidra)
    body_ranges = pathlib.Path(args.body_ranges)
    inventory_facts = artifact_facts(inventory, "ghidra-function-inventory")
    body_range_facts = artifact_facts(body_ranges, "ghidra-body-ranges")
    output = pathlib.Path(args.out).resolve()
    if output.exists():
        raise ParityLabError(f"Refusing to overwrite symbol map: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    image_base = parse_int(args.image_base, field="image base")
    derivation = image_derivation(
        pathlib.Path(args.static_exe), pathlib.Path(args.target_exe)
    )
    static_facts = derivation["static"]
    target_facts = derivation["target"]
    metadata = read_tsv_metadata(body_ranges)
    imported_md5 = metadata.get("executableMd5", "").lower()
    if imported_md5 != static_facts["md5"]:
        raise ParityLabError(
            f"Ghidra/static specimen mismatch: {imported_md5!r} != "
            f"{static_facts['md5']!r}"
        )
    if image_base != static_facts["pe"]["imageBaseInteger"]:
        raise ParityLabError("Symbol-map image base disagrees with the static PE")
    functions = load_functions(inventory, body_ranges)
    rows: list[list[str]] = []
    fragmented = 0
    for function in functions:
        if len(function.ranges) > 1:
            fragmented += 1
        entry_rva = function.address - image_base
        base_name = bounded_symbol_name(
            f"gh_{naming_risk(function)}__{function.name}",
            f"__RVA_{entry_rva:06X}",
            address=function.address,
        )
        for ordinal, (minimum, maximum) in enumerate(function.ranges, start=1):
            if minimum < image_base:
                raise ParityLabError(
                    f"Function range lies below image base: 0x{minimum:08X}"
                )
            range_rva = minimum - image_base
            if range_rva >= target_facts["pe"]["sizeOfImageInteger"]:
                raise ParityLabError(
                    f"Function range lies outside SizeOfImage: 0x{minimum:08X}"
                )
            if maximum >= image_base + target_facts["pe"]["sizeOfImageInteger"]:
                raise ParityLabError(
                    f"Function range crosses SizeOfImage: "
                    f"0x{minimum:08X}-0x{maximum:08X}"
                )
            is_entry = minimum <= function.address <= maximum
            name = (
                base_name
                if is_entry
                else bounded_symbol_name(
                    f"gh_{naming_risk(function)}__{function.name}",
                    f"__RVA_{entry_rva:06X}_fragment_{ordinal}"
                    f"_RVA_{range_rva:06X}",
                    address=function.address,
                )
            )
            rows.append(
                [
                    f"0x{range_rva:08X}",
                    str(maximum - minimum + 1),
                    name,
                    f"0x{minimum:08X}",
                    f"0x{function.address:08X}",
                    function.name,
                    str(ordinal),
                    "ENTRY" if is_entry else "FRAGMENT",
                    function.range_quality,
                ]
            )
    assert_artifact_unchanged(inventory, inventory_facts)
    assert_artifact_unchanged(body_ranges, body_range_facts)
    inventory_hash = inventory_facts["sha256"]
    body_range_hash = body_range_facts["sha256"]
    symbol_names = [row[2] for row in rows]
    if len(symbol_names) != len(set(symbol_names)):
        raise ParityLabError("Synthetic symbol names are not unique")
    temporary = output.with_name(
        f"{output.name}.tmp-{os.getpid()}-{uuid.uuid4().hex}"
    )
    try:
        with temporary.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(f"# schema={SYMBOL_MAP_SCHEMA}\n")
            handle.write(f"# imageBase=0x{image_base:08X}\n")
            handle.write(f"# inventorySha256={inventory_hash}\n")
            handle.write(f"# bodyRangesSha256={body_range_hash}\n")
            handle.write(f"# ghidraExecutableMd5={imported_md5}\n")
            handle.write(f"# staticSpecimenSha256={static_facts['sha256']}\n")
            handle.write(f"# runtimeTargetSha256={target_facts['sha256']}\n")
            handle.write(
                f"# runtimeDifferenceBytes={derivation['differentByteCount']}\n"
            )
            handle.write(
                "rva\tsize\tname\trangeAddress\tfunctionAddress\toriginalName"
                "\trangeOrdinal\trangeRole\trangeQuality\n"
            )
            writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
            writer.writerows(rows)
        os.link(temporary, output)
    finally:
        temporary.unlink(missing_ok=True)
    print(
        f"symbol map: {len(rows)} exact-range symbols for {len(functions)} functions; "
        f"{fragmented} fragmented functions"
    )
    print(output)
    return 0


def parse_expected_call(value: str) -> dict[str, Any]:
    fields = value.rsplit(",", 2)
    if len(fields) != 3:
        raise ParityLabError("--expect-call must be SYMBOL,ADDRESS,COUNT")
    symbol = fields[0].strip()
    address = parse_int(fields[1].strip(), field="expected call address")
    try:
        count = int(fields[2].strip(), 0)
    except ValueError as exc:
        raise ParityLabError(f"Invalid expected call count: {fields[2]!r}") from exc
    if not symbol or address < 0 or count < 0:
        raise ParityLabError("Expected call values must be non-negative")
    return {"symbol": symbol, "address": address, "expectedCount": count}


def run_symbol_proof(args: argparse.Namespace) -> int:
    query_path = pathlib.Path(args.query_result)
    map_path = pathlib.Path(args.symbol_map)
    dll_path = pathlib.Path(args.dll)
    repro_dll_path = pathlib.Path(args.repro_dll)
    input_command_path = pathlib.Path(args.command_file)
    output = create_output_dir(pathlib.Path(args.out))

    query_facts = artifact_facts(query_path, "ttd-query-result")
    map_facts = artifact_facts(map_path, "debugger-symbol-map")
    dll_facts = artifact_facts(dll_path, "debugger-symbol-extension")
    repro_dll_facts = artifact_facts(
        repro_dll_path, "debugger-symbol-extension-repro-build"
    )
    input_command_facts = artifact_facts(
        input_command_path, "ttd-symbol-proof-input-commands"
    )
    if windows_path_key(dll_path.resolve()) == windows_path_key(repro_dll_path.resolve()):
        raise ParityLabError("Independent extension artifacts must use distinct paths")
    if (
        dll_facts["bytes"] != repro_dll_facts["bytes"]
        or dll_facts["sha256"] != repro_dll_facts["sha256"]
    ):
        raise ParityLabError("Independent symbol-extension builds are not byte-identical")

    query = json.loads(query_path.read_text(encoding="utf-8-sig"))
    if not isinstance(query, dict) or query.get("schemaVersion") != "ttd-query-result.v3":
        raise ParityLabError("Symbol proof requires a ttd-query-result.v3 object")
    if query.get("ok") is not True or query.get("timedOut") is not False:
        raise ParityLabError("TTD query did not complete successfully")
    if query.get("problems") != []:
        raise ParityLabError("TTD query contains reported problems")
    known_answer = query.get("knownAnswer")
    negative_control = query.get("negativeControl")
    if not isinstance(known_answer, dict) or known_answer.get("AllAgree") is not True:
        raise ParityLabError("TTD known-answer PE checks did not all agree")
    if (
        not isinstance(negative_control, dict)
        or negative_control.get("Passed") is not True
    ):
        raise ParityLabError("TTD negative control did not pass")

    output_lines = query.get("output")
    if not isinstance(output_lines, list) or not all(
        isinstance(line, str) for line in output_lines
    ):
        raise ParityLabError("TTD query output is not a string array")
    summary_matches = [
        match
        for line in output_lines
        if (match := BEASYM_SUMMARY_RE.fullmatch(line))
    ]
    if len(summary_matches) != 1:
        raise ParityLabError(
            f"Expected exactly one current BEASYM summary, found {len(summary_matches)}"
        )
    summary = summary_matches[0].groupdict()
    if windows_path_key(pathlib.Path(summary["map"]).resolve()) != windows_path_key(
        map_path.resolve()
    ):
        raise ParityLabError("BEASYM loaded a different symbol map than requested")
    map_metadata = read_tsv_metadata(map_path)
    if map_metadata.get("schema") != SYMBOL_MAP_SCHEMA:
        raise ParityLabError("Symbol map does not declare the current schema")
    try:
        map_image_base = int(map_metadata["imageBase"], 0)
    except (KeyError, ValueError) as exc:
        raise ParityLabError("Symbol map lacks a valid imageBase") from exc
    map_rows: list[dict[str, str]] = []
    with map_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(
            (line for line in handle if not line.startswith("#")),
            delimiter="\t",
        )
        if reader.fieldnames is None or not {"rva", "size", "name"}.issubset(
            reader.fieldnames
        ):
            raise ParityLabError("Symbol map lacks required rva/size/name columns")
        map_rows = list(reader)
    row_count = len(map_rows)
    map_by_name: dict[str, dict[str, str]] = {}
    map_rvas: set[int] = set()
    for row in map_rows:
        name = row["name"]
        rva = parse_int(row["rva"], field="symbol-map RVA")
        size = parse_int(row["size"], field="symbol-map size")
        if not name or size <= 0 or name in map_by_name or rva in map_rvas:
            raise ParityLabError("Symbol map contains an empty, zero-size, or duplicate row")
        map_by_name[name] = row
        map_rvas.add(rva)
    summary_numbers = {
        key: int(summary[key])
        for key in ("rows", "added", "retry", "rejected", "malformed", "outside")
    }
    if (
        summary_numbers["rows"] != row_count
        or summary_numbers["added"] != row_count
        or summary_numbers["rejected"] != 0
        or summary_numbers["malformed"] != 0
        or summary_numbers["outside"] != 0
    ):
        raise ParityLabError(
            "BEASYM accounting is not closed: "
            + json.dumps(summary_numbers, sort_keys=True)
        )

    load_pattern = re.compile(r"^\d+:\d+(?::x86)?> \.load (?P<path>.+)$")
    loaded_dlls = [
        pathlib.Path(match.group("path")).resolve()
        for line in output_lines
        if (match := load_pattern.fullmatch(line))
    ]
    if len(loaded_dlls) != 1 or windows_path_key(
        loaded_dlls[0]
    ) != windows_path_key(dll_path.resolve()):
        raise ParityLabError("TTD query did not load exactly the requested extension DLL")

    generated_command_path = pathlib.Path(str(query.get("commandScript", "")))
    generated_commands = generated_command_path.read_text(encoding="ascii").splitlines()
    input_commands = [
        line
        for line in input_command_path.read_text(encoding="ascii").splitlines()
        if line.strip()
    ]
    begin_command = ".echo === TTDQUERY BEGIN ==="
    end_command = ".echo === TTDQUERY OUTPUT END ==="
    if (
        generated_commands.count(begin_command) != 1
        or generated_commands.count(end_command) != 1
    ):
        raise ParityLabError("Generated debugger script has ambiguous body markers")
    generated_body = generated_commands[
        generated_commands.index(begin_command) + 1 : generated_commands.index(end_command)
    ]
    if generated_body != input_commands:
        raise ParityLabError("Generated debugger query body differs from the requested commands")

    symbolic_rows: defaultdict[str, list[int]] = defaultdict(list)
    numeric_rows: defaultdict[int, list[int]] = defaultdict(list)
    for line in output_lines:
        if match := TTD_SYMBOL_CALL_RE.fullmatch(line):
            symbolic_rows[match.group("symbol")].append(
                int(match.group("count"), 16)
            )
        if match := TTD_NUMERIC_CALL_RE.fullmatch(line):
            numeric_rows[int(match.group("address"), 16)].append(
                int(match.group("count"), 16)
            )
    expected_calls = [parse_expected_call(value) for value in args.expect_call]
    if not expected_calls:
        raise ParityLabError("At least one --expect-call is required")
    if len({row["symbol"] for row in expected_calls}) != len(expected_calls):
        raise ParityLabError("Expected call symbols must be unique")
    if len({row["address"] for row in expected_calls}) != len(expected_calls):
        raise ParityLabError("Expected call addresses must be unique")
    call_results: list[dict[str, Any]] = []
    positive_count = 0
    zero_count = 0
    for expected in expected_calls:
        symbolic_values = symbolic_rows[expected["symbol"]]
        numeric_values = numeric_rows[expected["address"]]
        if len(symbolic_values) != 1 or len(numeric_values) != 1:
            raise ParityLabError(
                f"Expected one symbolic and numeric result for {expected['symbol']}, "
                f"found {len(symbolic_values)}/{len(numeric_values)}"
            )
        symbolic = symbolic_values[0]
        numeric = numeric_values[0]
        wanted = expected["expectedCount"]
        map_name = expected["symbol"].split("!", 1)[-1]
        map_row = map_by_name.get(map_name)
        if map_row is None:
            raise ParityLabError(
                f"Expected call symbol is absent from the supplied map: {map_name}"
            )
        map_address = map_image_base + parse_int(
            map_row["rva"], field="expected symbol RVA"
        )
        if map_address != expected["address"]:
            raise ParityLabError(
                f"Expected call address disagrees with map for {map_name}: "
                f"0x{expected['address']:08X} != 0x{map_address:08X}"
            )
        if symbolic != numeric or symbolic != wanted:
            raise ParityLabError(
                f"Call count mismatch for {expected['symbol']}: "
                f"symbolic={symbolic}, numeric={numeric}, expected={wanted}"
            )
        positive_count += int(wanted > 0)
        zero_count += int(wanted == 0)
        call_results.append(
            {
                **expected,
                "address": f"0x{expected['address']:08X}",
                "symbolicCount": symbolic,
                "numericCount": numeric,
                "agree": True,
            }
        )
    if positive_count < 2 or zero_count < 1:
        raise ParityLabError(
            "Symbol proof requires at least two positive pairs and one zero pair"
        )

    trace_path = pathlib.Path(str(query.get("trace", "")))
    trace_facts = artifact_facts(trace_path, "ttd-trace")
    if (
        trace_facts["bytes"] != query.get("traceBytes")
        or trace_facts["sha256"] != str(query.get("traceSha256", "")).upper()
    ):
        raise ParityLabError("Query trace identity no longer matches the trace artifact")
    known_image_path = pathlib.Path(str(known_answer.get("Image", "")))
    known_image_facts = artifact_facts(known_image_path, "known-answer-executable")
    if known_image_facts["sha256"] != str(known_answer.get("Sha256", "")).upper():
        raise ParityLabError("Known-answer executable hash does not match query receipt")
    if map_metadata.get("runtimeTargetSha256", "").upper() != known_image_facts["sha256"]:
        raise ParityLabError(
            "Symbol map runtime target does not match the known-answer executable"
        )
    known_module = str(known_answer.get("Module", ""))
    if summary["module"].casefold() != known_module.casefold():
        raise ParityLabError("BEASYM module disagrees with the known-answer module")
    read_at_base = parse_int(
        str(known_answer.get("ReadAtBase", "")), field="known-answer read base"
    )
    if int(summary["base"], 16) != read_at_base or map_image_base != read_at_base:
        raise ParityLabError("BEASYM/map base disagrees with known-answer read base")
    checks = known_answer.get("Checks")
    size_checks = [
        row
        for row in checks
        if isinstance(row, dict) and row.get("Name") == "SizeOfImage"
    ] if isinstance(checks, list) else []
    if len(size_checks) != 1 or int(summary["size"], 16) != int(
        size_checks[0].get("FromTrace", -1)
    ):
        raise ParityLabError("BEASYM module size disagrees with recorded SizeOfImage")

    debugger_artifacts = {
        "cdb": artifact_facts(pathlib.Path(str(query.get("cdb", ""))), "cdb"),
        "generatedCommands": artifact_facts(
            generated_command_path, "ttd-generated-commands"
        ),
        "log": artifact_facts(pathlib.Path(str(query.get("logPath", ""))), "cdb-log"),
        "stdout": artifact_facts(
            pathlib.Path(str(query.get("stdoutPath", ""))), "cdb-stdout"
        ),
        "stderr": artifact_facts(
            pathlib.Path(str(query.get("stderrPath", ""))), "cdb-stderr"
        ),
    }
    for path, facts in (
        (query_path, query_facts),
        (map_path, map_facts),
        (dll_path, dll_facts),
        (repro_dll_path, repro_dll_facts),
        (input_command_path, input_command_facts),
    ):
        assert_artifact_unchanged(path, facts)
    receipt = {
        "schemaVersion": SYMBOL_PROOF_SCHEMA,
        "toolVersion": TOOL_VERSION,
        "bridgeVerdict": "PASS",
        "captureProvenance": "PARTIAL",
        "captureProvenanceLimitation": (
            "The historical recording has no trace-hashed v3 producer receipt. "
            "This proof binds the current trace bytes and verifies the recorded PE "
            "header, but does not prove every recorded target byte against the "
            "known-answer executable SHA-256."
        ),
        "loadAccounting": {
            "module": summary["module"],
            "base": f"0x{int(summary['base'], 16):08X}",
            "size": f"0x{int(summary['size'], 16):08X}",
            **summary_numbers,
            "closed": True,
        },
        "buildComparison": {
            "verdict": "TWO_DISTINCT_ARTIFACTS_BYTE_IDENTICAL",
            "limitation": (
                "Distinct output paths and byte identity are proven here. "
                "Compiler invocation and independent build roots are not receipt-bound."
            ),
        },
        "callPairs": call_results,
        "controls": {
            "knownAnswerPassed": True,
            "negativeControlPassed": True,
            "positivePairCount": positive_count,
            "zeroPairCount": zero_count,
        },
        "artifacts": {
            "trace": trace_facts,
            "knownAnswerExecutable": known_image_facts,
            "queryResult": query_facts,
            "symbolMap": map_facts,
            "extensionDll": dll_facts,
            "reproducibilityDll": repro_dll_facts,
            "inputCommands": input_command_facts,
            **debugger_artifacts,
        },
    }
    write_json(output / "receipt.json", receipt)
    print(
        f"PASS: {row_count} symbols; "
        f"{len(call_results)} symbolic/numeric call pairs"
    )
    print(output / "receipt.json")
    return 0


def run_query(args: argparse.Namespace) -> int:
    database = pathlib.Path(args.database).resolve()
    if not database.is_file():
        raise ParityLabError(f"No such database: {database}")
    statement = args.sql.strip()
    first = re.match(r"^(?:--[^\n]*\n|\s)*(?P<word>[A-Za-z]+)", statement)
    allowed = {"SELECT", "WITH", "PRAGMA", "EXPLAIN"}
    if not first or first.group("word").upper() not in allowed:
        raise ParityLabError("Only read-only SELECT/WITH/PRAGMA/EXPLAIN queries are allowed")
    uri = f"{database.as_uri()}?mode=ro"
    connection = sqlite3.connect(uri, uri=True)
    connection.row_factory = sqlite3.Row
    try:
        cursor = connection.execute(statement)
        columns = [description[0] for description in cursor.description or []]
        rows = cursor.fetchmany(args.limit + 1)
    finally:
        connection.close()
    truncated = len(rows) > args.limit
    rows = rows[: args.limit]
    payload = {
        "schemaVersion": "bea-parity-query-result.v1",
        "database": str(database),
        "databaseSha256": sha256_file(database),
        "sql": statement,
        "columns": columns,
        "rows": [dict(row) for row in rows],
        "rowCountReturned": len(rows),
        "truncated": truncated,
        "limit": args.limit,
    }
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("\t".join(columns))
        for row in payload["rows"]:
            print("\t".join("" if row[column] is None else str(row[column]) for column in columns))
        if truncated:
            print(f"... truncated at {args.limit} rows", file=sys.stderr)
    return 0


def run_verify(args: argparse.Namespace) -> int:
    manifest_path = pathlib.Path(args.manifest).resolve()
    payload = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    problems: list[str] = []

    def visit(value: Any) -> Iterator[dict[str, Any]]:
        if isinstance(value, dict):
            if {"path", "bytes", "sha256"}.issubset(value):
                yield value
            for child in value.values():
                yield from visit(child)
        elif isinstance(value, list):
            for child in value:
                yield from visit(child)

    seen: dict[str, tuple[int, str, str]] = {}
    checked = 0
    for artifact in visit(payload):
        try:
            path = pathlib.Path(str(artifact["path"]))
            declared_bytes = int(artifact["bytes"])
            declared_hash = str(artifact["sha256"]).upper()
        except (TypeError, ValueError) as exc:
            problems.append(f"malformed artifact facts: {artifact!r}: {exc}")
            continue
        key = windows_path_key(path.resolve())
        declared = (
            declared_bytes,
            declared_hash,
            str(artifact.get("kind", "")),
        )
        if key in seen:
            prior = seen[key]
            if declared[:2] != prior[:2]:
                problems.append(
                    f"contradictory artifact facts: {path}: "
                    f"{prior[0]}/{prior[1]} versus {declared[0]}/{declared[1]}"
                )
            continue
        seen[key] = declared
        if not path.is_file():
            problems.append(f"missing: {path}")
            continue
        stat = path.stat()
        if stat.st_size != declared_bytes:
            problems.append(
                f"size mismatch: {path}: manifest {artifact['bytes']}, current {stat.st_size}"
            )
            continue
        current_hash = sha256_file(path)
        if current_hash.upper() != declared_hash:
            problems.append(
                f"hash mismatch: {path}: manifest {artifact['sha256']}, current {current_hash}"
            )
        checked += 1

    for d3d9 in payload.get("d3d9", []):
        accounting = d3d9.get("parseAccounting", {})
        if accounting:
            total = int(accounting.get("totalLines", -1))
            accounted = int(accounting.get("accountedLines", -2))
            if total != accounted:
                problems.append(
                    f"D3D9 parse accounting mismatch for {d3d9.get('path')}: {accounted}/{total}"
                )
    result = {
        "schemaVersion": "bea-parity-verification.v1",
        "manifest": str(manifest_path),
        "manifestSha256": sha256_file(manifest_path),
        "artifactsChecked": checked,
        "ok": not problems,
        "problems": problems,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not problems else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Engine-neutral BEA coverage, capture-bundle, and symbol tooling"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    coverage = subparsers.add_parser(
        "coverage-diff", help="diff repeated text drcov logs and join them to Ghidra"
    )
    coverage.add_argument("--baseline", action="append", required=True)
    coverage.add_argument("--baseline-receipt", action="append", required=True)
    coverage.add_argument("--action", action="append", required=True)
    coverage.add_argument("--action-receipt", action="append", required=True)
    coverage.add_argument("--ghidra", required=True, help="Ghidra function inventory TSV")
    coverage.add_argument("--body-ranges", help="exact Ghidra body-range TSV")
    coverage.add_argument("--call-edges", help="optional Ghidra direct-call edge TSV")
    coverage.add_argument(
        "--graph-receipt",
        help="required READY receipt when --call-edges is supplied",
    )
    coverage.add_argument("--module", default="BEA.exe")
    coverage.add_argument("--image-base", default="0x00400000")
    coverage.add_argument(
        "--static-exe",
        required=True,
        help="exact executable imported into Ghidra",
    )
    coverage.add_argument(
        "--target-exe",
        required=True,
        help="exact runtime executable named by every capture receipt",
    )
    coverage.add_argument("--scenario", required=True)
    coverage.add_argument("--question", default="")
    coverage.add_argument(
        "--action-canary",
        action="append",
        default=[],
        help=(
            "Ghidra function entry required in every action run and no baseline run; "
            "repeat for independent action-delivery controls"
        ),
    )
    coverage.add_argument(
        "--shared-canary",
        action="append",
        default=[],
        help="Ghidra function entry required in every run",
    )
    coverage.add_argument(
        "--options-contract",
        action="store_true",
        help=(
            "require two exact counterbalanced v2 Options campaigns and emit "
            "their independently closed intersection"
        ),
    )
    coverage.add_argument("--out", required=True)
    coverage.set_defaults(func=run_coverage_diff)

    ttd_diff = subparsers.add_parser(
        "ttd-coverage-diff",
        help="diff identity-linked TTD Replay coverage bundles and join Ghidra",
    )
    ttd_diff.add_argument("--baseline-bundle", action="append", required=True)
    ttd_diff.add_argument("--action-bundle", action="append", required=True)
    ttd_diff.add_argument("--ghidra", required=True)
    ttd_diff.add_argument("--body-ranges", required=True)
    ttd_diff.add_argument("--call-edges")
    ttd_diff.add_argument(
        "--graph-receipt",
        help="required READY receipt when --call-edges is supplied",
    )
    ttd_diff.add_argument("--static-exe", required=True)
    ttd_diff.add_argument("--target-exe", required=True)
    ttd_diff.add_argument("--image-base", default="0x00400000")
    ttd_diff.add_argument("--scenario", required=True)
    ttd_diff.add_argument("--question", default="")
    ttd_diff.add_argument("--action-canary", action="append", default=[])
    ttd_diff.add_argument("--out", required=True)
    ttd_diff.set_defaults(func=run_ttd_coverage_diff)

    bundle = subparsers.add_parser(
        "capture-bundle", help="normalize D3D9 and TTD evidence into a queryable bundle"
    )
    bundle.add_argument("--bundle-id", required=True)
    bundle.add_argument("--scenario", required=True)
    bundle.add_argument(
        "--role", choices=["baseline", "action", "reference", "experiment"], required=True
    )
    bundle.add_argument("--question", default="")
    bundle.add_argument("--action", default="")
    bundle.add_argument("--positive-control", default="")
    bundle.add_argument("--target-exe")
    bundle.add_argument("--d3d9-log", action="append", default=[])
    bundle.add_argument("--ttd-receipt", action="append", default=[])
    bundle.add_argument("--ttd-result", action="append", default=[])
    bundle.add_argument("--ttd-coverage", action="append", default=[])
    bundle.add_argument("--ttd-coverage-receipt", action="append", default=[])
    bundle.add_argument("--shot-manifest", action="append", default=[])
    bundle.add_argument("--out", required=True)
    bundle.set_defaults(func=run_capture_bundle)

    symbols = subparsers.add_parser(
        "symbol-map", help="emit an RVA-safe synthetic-symbol map from Ghidra TSV"
    )
    symbols.add_argument("--ghidra", required=True)
    symbols.add_argument("--body-ranges", required=True)
    symbols.add_argument("--static-exe", required=True)
    symbols.add_argument("--target-exe", required=True)
    symbols.add_argument("--image-base", default="0x00400000")
    symbols.add_argument("--out", required=True)
    symbols.set_defaults(func=run_symbol_map)

    symbol_proof = subparsers.add_parser(
        "symbol-proof",
        help="hash-bind and validate one current map/extension TTD proof",
    )
    symbol_proof.add_argument("--query-result", required=True)
    symbol_proof.add_argument("--symbol-map", required=True)
    symbol_proof.add_argument("--dll", required=True)
    symbol_proof.add_argument("--repro-dll", required=True)
    symbol_proof.add_argument("--command-file", required=True)
    symbol_proof.add_argument(
        "--expect-call",
        action="append",
        required=True,
        help="expected SYMBOL,ADDRESS,COUNT; repeat for independent controls",
    )
    symbol_proof.add_argument("--out", required=True)
    symbol_proof.set_defaults(func=run_symbol_proof)

    query = subparsers.add_parser("query", help="run read-only SQL against a bundle")
    query.add_argument("--database", required=True)
    query.add_argument("--sql", required=True)
    query.add_argument("--limit", type=int, default=5000)
    query.add_argument("--json", action="store_true")
    query.set_defaults(func=run_query)

    verify = subparsers.add_parser("verify", help="re-hash and verify a bundle manifest")
    verify.add_argument("--manifest", required=True)
    verify.set_defaults(func=run_verify)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if getattr(args, "limit", 1) < 1:
        parser.error("--limit must be positive")
    try:
        return int(args.func(args))
    except (ParityLabError, json.JSONDecodeError, sqlite3.Error, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    finally:
        # Commands build SQLite evidence incrementally. A fail-closed
        # validation can abort before an owner reaches its explicit close.
        # Close registered handles here so partial databases remain inspectable
        # without retaining Windows file locks or ResourceWarnings.
        for connection in _OPEN_DATABASES:
            try:
                connection.close()
            except sqlite3.Error:
                pass
        _OPEN_DATABASES.clear()


if __name__ == "__main__":
    raise SystemExit(main())
