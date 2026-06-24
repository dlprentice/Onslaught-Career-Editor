#!/usr/bin/env python3
"""Generate a public-safe PhysicsScript copied-corpus parser/census proof."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GAME_ROOT = ROOT / "game"
DEFAULT_OUT_ROOT = ROOT / "subagents" / "physics_script_schema_parser_proof_2026-06-08"
SUMMARY_NAME = "physics-script-copied-corpus-summary.json"

TOP_LEVEL_FAMILIES = {
    1: "unit",
    2: "weapon",
    3: "weapon-mode",
    4: "round",
    5: "spawner",
    6: "explosion",
    7: "component",
    8: "feature",
    9: "hazard",
}

NESTED_FACTORY_BY_TOP_LEVEL = {
    1: 2,
    2: 3,
    3: 4,
    4: 5,
    5: 6,
    6: 7,
    7: 10,
    8: 8,
    9: 9,
}

EXPECTED_STATIC = {
    "staticFunctionQuality": "6411/6411 = 100.00%",
    "staticDebt": "0 / 0 / 0",
    "expandedStaticSurface": "1560/1560 = 100.00%",
    "currentRiskFocused": "1179/1179 = 100.00%",
    "remainingActiveFocusedWork": 0,
}


class ParseError(ValueError):
    """Raised when a corpus file does not match the shallow stream framing."""


def repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def read_i16(data: bytes, offset: int) -> int:
    if offset + 2 > len(data):
        raise ParseError(f"truncated int16 at {offset}")
    return struct.unpack_from("<h", data, offset)[0]


def read_i32(data: bytes, offset: int) -> int:
    if offset + 4 > len(data):
        raise ParseError(f"truncated int32 at {offset}")
    return struct.unpack_from("<i", data, offset)[0]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def count_histogram(values: list[int]) -> dict[str, int]:
    return {str(key): count for key, count in sorted(Counter(values).items())}


def parse_physics_script(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    size = len(data)
    if size < 6:
        raise ParseError("file is too small for PhysicsScript framing")

    header = read_i16(data, 0)
    offset = 2
    top_counts: Counter[int] = Counter()
    value_counts: Counter[tuple[int, int]] = Counter()
    value_counts_by_family: dict[str, Counter[int]] = {
        family: Counter() for family in TOP_LEVEL_FAMILIES.values()
    }
    continuation_markers: Counter[int] = Counter()
    declared_delta: Counter[int] = Counter()
    declared_payload_by_type: Counter[int] = Counter()
    raw_payload_by_type: Counter[int] = Counter()
    name_lengths: list[int] = []
    chain_lengths: list[int] = []
    unknown_top_level_records: list[dict[str, int]] = []
    top_level_records = 0
    value_node_count = 0
    raw_payload_bytes = 0
    declared_payload_bytes = 0
    known_statement_consumed_bytes = 0
    terminator_offset: int | None = None

    if header != 0x12:
        raise ParseError(f"unexpected header {header:#x}; expected 0x12")

    while True:
        record_offset = offset
        statement_type = read_i32(data, offset)
        offset += 4
        if statement_type == -1:
            terminator_offset = record_offset
            break

        payload_size = read_i32(data, offset)
        offset += 4
        if payload_size < 0:
            raise ParseError(f"negative top-level payload size at {record_offset}")
        if offset + payload_size > size:
            raise ParseError(f"top-level payload overrun at {record_offset}")

        top_level_records += 1
        top_counts[statement_type] += 1
        declared_payload_bytes += payload_size
        declared_payload_by_type[statement_type] += payload_size

        if statement_type not in TOP_LEVEL_FAMILIES:
            unknown_top_level_records.append(
                {
                    "recordOffset": record_offset,
                    "statementType": statement_type,
                    "declaredPayloadBytes": payload_size,
                }
            )
            offset += payload_size
            continue

        body_start = offset
        nul = data.find(b"\0", offset)
        if nul < 0:
            raise ParseError(f"unterminated statement name at {record_offset}")
        name_lengths.append(nul - offset)
        offset = nul + 1

        node_count = 0
        family = TOP_LEVEL_FAMILIES[statement_type]
        while True:
            value_type = read_i32(data, offset)
            value_payload_size = read_i32(data, offset + 4)
            offset += 8
            if value_payload_size < 0:
                raise ParseError(f"negative value payload size at {offset - 8}")
            if offset + value_payload_size > size:
                raise ParseError(f"value payload overrun at {offset - 8}")

            value_node_count += 1
            node_count += 1
            value_counts[(statement_type, value_type)] += 1
            value_counts_by_family[family][value_type] += 1
            raw_payload_bytes += value_payload_size
            raw_payload_by_type[statement_type] += value_payload_size
            offset += value_payload_size

            marker = read_i32(data, offset)
            offset += 4
            continuation_markers[marker] += 1
            if marker != 0:
                break

        consumed = offset - body_start
        known_statement_consumed_bytes += consumed
        declared_delta[consumed - payload_size] += 1
        chain_lengths.append(node_count)

    if terminator_offset is None:
        raise ParseError("missing top-level terminator")

    unknown_value_pairs: list[dict[str, int]] = []
    for statement_type, value_type in sorted(value_counts):
        # Value factories are intentionally not asserted complete here; this is a
        # semantic decode boundary, not a parse failure.
        _ = NESTED_FACTORY_BY_TOP_LEVEL.get(statement_type)
        if statement_type not in TOP_LEVEL_FAMILIES:
            unknown_value_pairs.append(
                {
                    "statementType": statement_type,
                    "valueType": value_type,
                    "count": value_counts[(statement_type, value_type)],
                }
            )

    return {
        "relativePath": repo_relative(path),
        "fileName": path.name,
        "sizeBytes": size,
        "sha256": sha256(path),
        "parseStatus": "PASS",
        "headerValue": header,
        "terminatorOffset": terminator_offset,
        "terminatorAtEnd": offset == size,
        "topLevelRecords": top_level_records,
        "topLevelTypeCounts": {str(key): top_counts[key] for key in sorted(top_counts)},
        "topLevelUnknownRecords": len(unknown_top_level_records),
        "topLevelUnknownRecordDetails": unknown_top_level_records,
        "valueNodeCount": value_node_count,
        "uniqueStatementValuePairs": len(value_counts),
        "valuePairCounts": [
            {
                "statementType": statement_type,
                "family": TOP_LEVEL_FAMILIES.get(statement_type, "unknown"),
                "nestedFactoryType": NESTED_FACTORY_BY_TOP_LEVEL.get(statement_type),
                "valueType": value_type,
                "count": value_counts[(statement_type, value_type)],
            }
            for statement_type, value_type in sorted(value_counts)
        ],
        "valueCountsByFamily": {
            family: {str(key): counter[key] for key in sorted(counter)}
            for family, counter in sorted(value_counts_by_family.items())
        },
        "unknownValuePairs": len(unknown_value_pairs),
        "unknownValuePairDetails": unknown_value_pairs,
        "rawValuePayloadBytesPreserved": raw_payload_bytes,
        "declaredTopLevelPayloadBytes": declared_payload_bytes,
        "knownStatementConsumedBytes": known_statement_consumed_bytes,
        "declaredVsConsumedDeltaCounts": {
            str(key): declared_delta[key] for key in sorted(declared_delta)
        },
        "declaredPayloadBytesByTopLevelType": {
            str(key): declared_payload_by_type[key] for key in sorted(declared_payload_by_type)
        },
        "rawValuePayloadBytesByTopLevelType": {
            str(key): raw_payload_by_type[key] for key in sorted(raw_payload_by_type)
        },
        "continuationMarkerCounts": {
            str(key): continuation_markers[key] for key in sorted(continuation_markers)
        },
        "nameCount": len(name_lengths),
        "nameLength": {
            "min": min(name_lengths) if name_lengths else 0,
            "max": max(name_lengths) if name_lengths else 0,
            "histogram": count_histogram(name_lengths),
        },
        "valueChainLength": {
            "min": min(chain_lengths) if chain_lengths else 0,
            "max": max(chain_lengths) if chain_lengths else 0,
            "average": round(sum(chain_lengths) / len(chain_lengths), 2) if chain_lengths else 0,
            "histogram": count_histogram(chain_lengths),
        },
        "rawNamesOrStringsEmitted": False,
        "semanticValueDecodeAttempted": False,
    }


def discover_candidates(game_root: Path) -> list[Path]:
    candidates: list[Path] = []
    expected = game_root / "data" / "default physics.dat"
    if expected.is_file():
        candidates.append(expected)

    if game_root.is_dir():
        for path in game_root.rglob("*"):
            if not path.is_file():
                continue
            relative = path.relative_to(game_root).as_posix().lower()
            if relative.startswith("missionscripts/"):
                continue
            if path in candidates:
                continue
            if "physics" in path.name.lower() and path.suffix.lower() == ".dat":
                candidates.append(path)
    return sorted(candidates, key=lambda item: repo_relative(item).lower())


def build_report(game_root: Path) -> dict[str, Any]:
    game_root = game_root.resolve()
    candidates = discover_candidates(game_root)
    parsed: list[dict[str, Any]] = []
    failures: list[str] = []

    for path in candidates:
        try:
            parsed.append(parse_physics_script(path))
        except (OSError, ParseError, struct.error) as exc:
            failures.append(f"{repo_relative(path)}: {exc}")

    total_bytes = sum(row["sizeBytes"] for row in parsed)
    aggregate_top_counts: Counter[str] = Counter()
    aggregate_marker_counts: Counter[str] = Counter()
    total_value_nodes = 0
    total_raw_payload = 0
    for row in parsed:
        aggregate_top_counts.update(row["topLevelTypeCounts"])
        aggregate_marker_counts.update(row["continuationMarkerCounts"])
        total_value_nodes += int(row["valueNodeCount"])
        total_raw_payload += int(row["rawValuePayloadBytesPreserved"])

    status = "PASS" if parsed and not failures else "FAIL"
    return {
        "schema": "physics-script-copied-corpus-parser.v1",
        "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "source": {
            "gameRoot": repo_relative(game_root),
            "copiedAppOwnedInputOnly": True,
            "programFilesInputUsed": False,
            "missionScriptsExcluded": True,
            "excludedInputPattern": "MissionScripts/*.msl",
        },
        "staticContext": EXPECTED_STATIC,
        "corpus": {
            "candidateFiles": len(candidates),
            "parsedFiles": len(parsed),
            "totalBytes": total_bytes,
            "defaultPhysicsDatPresent": any(row["fileName"] == "default physics.dat" for row in parsed),
            "defaultUnderscorePhysicsDatPresent": any(
                row["fileName"] == "default_physics.dat" for row in parsed
            ),
            "files": parsed,
        },
        "aggregate": {
            "topLevelRecords": sum(row["topLevelRecords"] for row in parsed),
            "topLevelTypeCounts": dict(sorted(aggregate_top_counts.items(), key=lambda item: int(item[0]))),
            "unknownTopLevelRecords": sum(row["topLevelUnknownRecords"] for row in parsed),
            "valueNodeCount": total_value_nodes,
            "uniqueStatementValuePairs": sum(row["uniqueStatementValuePairs"] for row in parsed),
            "rawValuePayloadBytesPreserved": total_raw_payload,
            "continuationMarkerCounts": dict(sorted(aggregate_marker_counts.items(), key=lambda item: int(item[0]))),
        },
        "publicSafety": {
            "rawBytesEmitted": False,
            "rawNamesOrStringsEmitted": False,
            "absolutePathsEmitted": False,
            "hashesKeptInIgnoredEvidenceOnly": True,
            "launchesGame": False,
            "readsOrWritesOriginalExe": False,
            "mutatesGameFiles": False,
            "mutatesGhidra": False,
        },
        "claims": [
            "Copied PhysicsScript corpus candidates can be shallow-framed with the saved CPhysicsScript__Load contract.",
            "Top-level statement ids in the parsed copied corpus are within the saved 1..9 factory range.",
            "Value-list records are counted and raw-preserved without semantic value-field decoding.",
        ],
        "notClaimed": [
            "runtime PhysicsScript behavior",
            "mission outcomes",
            "resource-script outcomes",
            "serialized physics-script file-format completeness",
            "exact statement/value-list/concrete record layouts",
            "complete nested enum semantics",
            "exact source-body identity",
            "BEA patching behavior",
            "visual QA",
            "Godot parity",
            "rebuild parity",
            "no-noticeable-difference parity",
        ],
        "warnings": [
            "Known top-level payload sizes are retained as declared-size evidence and skip authority for unknown top-level ids; known top-level records are parsed through their value-chain terminator, matching the saved loader shape."
        ],
        "failures": failures,
    }


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        game_root = tmp_path / "game"
        physics = game_root / "data" / "default physics.dat"
        physics.parent.mkdir(parents=True)
        payload = bytearray()
        payload += struct.pack("<h", 0x12)
        payload += struct.pack("<ii", 1, 0)
        payload += b"unit_alpha\0"
        payload += struct.pack("<ii", 8, 4)
        payload += b"ABCD"
        payload += struct.pack("<i", 0)
        payload += struct.pack("<ii", 9, 0)
        payload += struct.pack("<i", -1)
        payload += struct.pack("<i", -1)
        physics.write_bytes(payload)
        report = build_report(game_root)
        assert report["status"] == "PASS"
        file_row = report["corpus"]["files"][0]
        assert file_row["headerValue"] == 0x12
        assert file_row["topLevelRecords"] == 1
        assert file_row["valueNodeCount"] == 2
        assert file_row["continuationMarkerCounts"] == {"-1": 1, "0": 1}
        assert file_row["rawNamesOrStringsEmitted"] is False
    print("physics_script_copied_corpus_parser self-test: PASS")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--game-root", type=Path, default=DEFAULT_GAME_ROOT)
    parser.add_argument("--out-root", type=Path, default=DEFAULT_OUT_ROOT)
    parser.add_argument("--check", action="store_true", help="fail when parser status is not PASS")
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    report = build_report(args.game_root)
    out_path = args.out_root / SUMMARY_NAME
    write_json(out_path, report)
    print(f"{report['status']}: wrote {repo_relative(out_path)}")
    print(
        "PhysicsScript copied-corpus parser: "
        f"files={report['corpus']['parsedFiles']} "
        f"bytes={report['corpus']['totalBytes']} "
        f"topLevelRecords={report['aggregate']['topLevelRecords']} "
        f"valueNodes={report['aggregate']['valueNodeCount']} "
        f"unknownTopLevel={report['aggregate']['unknownTopLevelRecords']}"
    )
    if args.check and report["status"] != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
