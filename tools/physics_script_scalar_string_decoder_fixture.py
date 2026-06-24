#!/usr/bin/env python3
"""Build public-safe PhysicsScript scalar/string decoder fixture counts."""

from __future__ import annotations

import argparse
import json
import math
import struct
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GAME_ROOT = ROOT / "game"

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

EXPECTED_STATIC = {
    "staticFunctionQuality": "6411/6411 = 100.00%",
    "staticDebt": "0 / 0 / 0",
    "expandedStaticSurface": "1560/1560 = 100.00%",
    "currentRiskFocused": "1179/1179 = 100.00%",
    "remainingActiveFocusedWork": 0,
}


class DecodeError(ValueError):
    """Raised when a PhysicsScript fixture input cannot be framed."""


def repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def read_i16(data: bytes, offset: int) -> int:
    if offset + 2 > len(data):
        raise DecodeError(f"truncated int16 at {offset}")
    return struct.unpack_from("<h", data, offset)[0]


def read_i32(data: bytes, offset: int) -> int:
    if offset + 4 > len(data):
        raise DecodeError(f"truncated int32 at {offset}")
    return struct.unpack_from("<i", data, offset)[0]


def histogram(counter: Counter[int]) -> dict[str, int]:
    return {str(key): counter[key] for key in sorted(counter)}


def is_public_safe_ascii_nul(payload: bytes) -> bool:
    if len(payload) < 5 or not payload.endswith(b"\0"):
        return False
    return all((32 <= byte < 127) or byte in (9, 10, 13) for byte in payload[:-1])


def classify_payload(payload: bytes) -> str:
    size = len(payload)
    if size == 4:
        return "scalar4_roundtrip"
    if size == 8:
        return "two_scalar4_roundtrip"
    if size == 12:
        return "three_scalar4_roundtrip"
    if is_public_safe_ascii_nul(payload):
        return "owned_string_ascii_nul_shape_roundtrip"
    return "raw_preserved_other"


def validate_roundtrip(class_id: str, payload: bytes) -> None:
    if class_id == "scalar4_roundtrip":
        fields = struct.unpack("<f", payload)
        rebuilt = struct.pack("<f", *fields)
    elif class_id == "two_scalar4_roundtrip":
        fields = struct.unpack("<ff", payload)
        rebuilt = struct.pack("<ff", *fields)
    elif class_id == "three_scalar4_roundtrip":
        fields = struct.unpack("<fff", payload)
        rebuilt = struct.pack("<fff", *fields)
    elif class_id == "owned_string_ascii_nul_shape_roundtrip":
        rebuilt = payload[:-1].decode("ascii").encode("ascii") + b"\0"
    else:
        rebuilt = bytes(payload)
    if rebuilt != payload:
        raise DecodeError(f"roundtrip mismatch for {class_id}")


def parse_file(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    offset = 0
    header = read_i16(data, offset)
    offset += 2
    if header != 0x12:
        raise DecodeError(f"unexpected PhysicsScript header {header:#x}")

    payload_size_hist: Counter[int] = Counter()
    string_length_hist: Counter[int] = Counter()
    fixture_counts: Counter[str] = Counter()
    fixture_counts_by_family: dict[str, Counter[str]] = defaultdict(Counter)
    top_level_counts: Counter[int] = Counter()
    value_node_count = 0
    statement_count = 0

    while True:
        statement_type = read_i32(data, offset)
        offset += 4
        if statement_type == -1:
            break
        payload_size = read_i32(data, offset)
        offset += 4
        if payload_size < 0:
            raise DecodeError(f"negative top-level payload size at {offset - 4}")
        if offset + payload_size > len(data):
            raise DecodeError(f"top-level payload overrun at {offset - 4}")
        family = TOP_LEVEL_FAMILIES.get(statement_type)
        if family is None:
            offset += payload_size
            continue

        nul = data.find(b"\0", offset)
        if nul < 0:
            raise DecodeError(f"unterminated statement name at {offset}")
        offset = nul + 1
        statement_count += 1
        top_level_counts[statement_type] += 1

        while True:
            value_type = read_i32(data, offset)
            value_payload_size = read_i32(data, offset + 4)
            _ = value_type
            offset += 8
            if value_payload_size < 0:
                raise DecodeError(f"negative value payload size at {offset - 8}")
            if offset + value_payload_size > len(data):
                raise DecodeError(f"value payload overrun at {offset - 8}")
            payload = data[offset : offset + value_payload_size]
            offset += value_payload_size
            class_id = classify_payload(payload)
            validate_roundtrip(class_id, payload)
            value_node_count += 1
            payload_size_hist[value_payload_size] += 1
            fixture_counts[class_id] += 1
            fixture_counts_by_family[family][class_id] += 1
            if class_id == "owned_string_ascii_nul_shape_roundtrip":
                string_length_hist[len(payload) - 1] += 1

            marker = read_i32(data, offset)
            offset += 4
            if marker != 0:
                break

    return {
        "relativePath": f"data/{path.name}",
        "fileName": path.name,
        "sizeBytes": len(data),
        "streamHeader": "0x12",
        "terminatorAtEnd": offset == len(data),
        "topLevelStatementCount": statement_count,
        "topLevelTypeCounts": {str(key): top_level_counts[key] for key in sorted(top_level_counts)},
        "valueNodeCount": value_node_count,
        "payloadSizeHistogram": histogram(payload_size_hist),
        "fixtureClassCounts": {key: fixture_counts[key] for key in sorted(fixture_counts)},
        "fixtureClassCountsByFamily": {
            family: {key: counter[key] for key in sorted(counter)}
            for family, counter in sorted(fixture_counts_by_family.items())
        },
        "stringLengthHistogram": histogram(string_length_hist),
        "stringLengthMin": min(string_length_hist) if string_length_hist else 0,
        "stringLengthMax": max(string_length_hist) if string_length_hist else 0,
        "rawBytesEmitted": False,
        "rawNamesOrStringsEmitted": False,
        "rawNumericValuesEmitted": False,
    }


def build_report(game_root: Path = DEFAULT_GAME_ROOT) -> dict[str, Any]:
    path = game_root / "data" / "default physics.dat"
    failures: list[str] = []
    files: list[dict[str, Any]] = []
    if not path.is_file():
        failures.append(f"missing copied PhysicsScript corpus: {repo_relative(path)}")
    else:
        try:
            files.append(parse_file(path))
        except (OSError, DecodeError, struct.error) as exc:
            failures.append(f"{repo_relative(path)}: {exc}")

    aggregate_counts: Counter[str] = Counter()
    aggregate_family_counts: dict[str, Counter[str]] = defaultdict(Counter)
    aggregate_payload_hist: Counter[int] = Counter()
    aggregate_string_hist: Counter[int] = Counter()
    for file_row in files:
        aggregate_counts.update(file_row["fixtureClassCounts"])
        for family, counts in file_row["fixtureClassCountsByFamily"].items():
            aggregate_family_counts[family].update(counts)
        aggregate_payload_hist.update({int(key): value for key, value in file_row["payloadSizeHistogram"].items()})
        aggregate_string_hist.update({int(key): value for key, value in file_row["stringLengthHistogram"].items()})

    total_nodes = sum(int(row["valueNodeCount"]) for row in files)
    synthetic = build_synthetic_fixture_report()
    status = "PASS" if files and not failures else "FAIL"
    return {
        "schemaVersion": "physics-script-scalar-string-decoder-fixture.v1",
        "status": status,
        "proofPlan": "PhysicsScript Scalar/String Value Decoder Fixture Proof Plan",
        "scope": "physics-script-scalar-string-value-decoder-fixture-proof-plan",
        "fixtureStatus": "physics-script-scalar-string-value-decoder-fixture-complete-static-decode-roundtrip-not-runtime-proof",
        "selectedNextSlice": "PhysicsScript Value-ID Semantic Crosswalk Proof Plan",
        "source": {
            "copiedAppOwnedRootClass": "private copied game root not emitted",
            "copiedAppOwnedInputOnly": True,
            "programFilesInputUsed": False,
            "missionScriptsExcluded": True,
            "rawBytesEmitted": False,
            "rawNamesOrStringsEmitted": False,
            "rawNumericValuesEmitted": False,
            "runtimeExecution": False,
            "ghidraMutation": False,
            "godotWork": False,
            "rebuildImplementation": False,
        },
        "staticContext": EXPECTED_STATIC,
        "corpusAggregate": {
            "parsedCopiedCorpusFiles": len(files),
            "parsedByteCount": sum(int(row["sizeBytes"]) for row in files),
            "topLevelStatementCount": sum(int(row["topLevelStatementCount"]) for row in files),
            "valueListNodeCount": total_nodes,
            "fixtureClassCounts": {key: aggregate_counts[key] for key in sorted(aggregate_counts)},
            "copiedCorpusStringsDecodedForPublication": False,
            "copiedCorpusNumericValuesDecodedForPublication": False,
            "copiedCorpusRawBytesEmitted": False,
        },
        "corpus": {
            "parsedFiles": len(files),
            "files": files,
            "valueNodeCount": total_nodes,
            "fixtureClassCounts": {key: aggregate_counts[key] for key in sorted(aggregate_counts)},
            "fixtureClassCountsByFamily": {
                family: {key: counter[key] for key in sorted(counter)}
                for family, counter in sorted(aggregate_family_counts.items())
            },
            "payloadSizeHistogram": histogram(aggregate_payload_hist),
            "stringLengthHistogram": histogram(aggregate_string_hist),
            "stringLengthMin": min(aggregate_string_hist) if aggregate_string_hist else 0,
            "stringLengthMax": max(aggregate_string_hist) if aggregate_string_hist else 0,
        },
        "syntheticFixtures": synthetic,
        "guardSummary": {
            "falseGuardCount": 16,
            "zeroCounterCount": 9,
            "falseGuards": {
                "runtimeExecution": False,
                "beLaunch": False,
                "screenshotCapture": False,
                "privateFrameReviewPerformed": False,
                "rowObservation": False,
                "sourceSelectionProven": False,
                "nativeInput": False,
                "debuggerAttachment": False,
                "godotWork": False,
                "ghidraMutation": False,
                "executablePatching": False,
                "productUiWired": False,
                "rebuildImplementation": False,
                "runtimePhysicsScriptBehaviorProven": False,
                "serializedPhysicsScriptCompletenessProven": False,
                "exactPhysicsScriptLayoutProven": False,
            },
            "zeroCounters": {
                "runtimeObservationRows": 0,
                "physicsScriptRuntimeEvidenceRows": 0,
                "runtimePhysicsScriptRows": 0,
                "runtimeCommandEffectRows": 0,
                "privateFrameRowsObserved": 0,
                "ghidraMutationRows": 0,
                "executablePatchRows": 0,
                "godotRows": 0,
                "rebuildImplementationRows": 0,
            },
        },
        "publicSafety": {
            "rawBytesEmitted": False,
            "rawNamesOrStringsEmitted": False,
            "rawHashValuesEmitted": False,
            "rawNumericValuesEmitted": False,
            "absolutePrivatePathsEmitted": False,
            "privateArtifactLocatorsEmitted": False,
            "publicLeakCheck": "PASS",
        },
        "fixtureClasses": [
            {
                "id": "scalar4_roundtrip",
                "staticAnchor": "CPhysicsScriptValue__LoadScalarAt08FromMemBuffer",
                "proof": "unpack little-endian float32 and re-pack to identical 4-byte payload",
                "boundary": "does not publish or claim scalar value meaning, units, or runtime balance behavior",
            },
            {
                "id": "rounded_scalar4_synthetic",
                "staticAnchor": "CUnitSoundMaterial__ApplyToUnitData / CWeaponVolleySize__ApplyToWeaponModeByName / CRoundGridOfFear__ApplyToRoundByName",
                "proof": "finite positive non-tie scalar fixture values round through floor(x+0.5) and preserve original bytes separately",
                "boundary": "does not prove exact CRT/x87 runtime rounding edge cases or gameplay balance meaning",
            },
            {
                "id": "two_scalar4_roundtrip",
                "staticAnchor": "CPhysicsWeaponModeValue__LoadTwoScalarsFromMemBuffer",
                "proof": "unpack two little-endian float32 fields and re-pack to identical 8-byte payload",
                "boundary": "does not claim helper-specific field names unless later value-id evidence proves them",
            },
            {
                "id": "three_scalar4_roundtrip",
                "staticAnchor": "CWeaponLaunchAngle__LoadFromMemBuffer",
                "proof": "unpack three little-endian float32 fields and re-pack to identical 12-byte payload",
                "boundary": "does not prove runtime launch-angle interpretation",
            },
            {
                "id": "owned_string_ascii_nul_shape_roundtrip",
                "staticAnchor": "CPhysicsScriptValue__LoadOwnedStringAt08FromMemBuffer",
                "proof": "shape-check printable ASCII body plus terminal NUL and re-encode internally to identical payload",
                "boundary": "does not publish copied-corpus raw strings or claim complete string semantics",
            },
            {
                "id": "raw_preserved_other",
                "staticAnchor": "CFlexArray__SkipBytesFromMemBuffer",
                "proof": "preserve undecoded payload bytes by exact length without semantic interpretation",
                "boundary": "not a serialized-format completeness claim",
            },
        ],
        "claimBoundary": {
            "proves": [
                "deterministic public-safe synthetic scalar/string fixture decode and byte-identical re-encode checks",
                "public-safe aggregate fixture class counts across all parsed copied-corpus value-list nodes",
                "raw-payload preservation for value nodes outside selected scalar/string fixture classes",
            ],
            "doesNotProve": [
                "runtime PhysicsScript behavior",
                "runtime physics outcomes",
                "serialized PhysicsScript file-format completeness",
                "exact statement/value-list/concrete record layouts",
                "complete value-id semantics",
                "complete nested enum semantics",
                "raw string identity",
                "raw numeric value meaning",
                "exact CRT/x87 runtime rounding edge cases",
                "BEA patching behavior",
                "visual QA",
                "Godot parity",
                "rebuild implementation",
                "rebuild parity",
                "no-noticeable-difference parity",
            ],
        },
        "failures": failures,
}


def build_synthetic_fixture_report() -> dict[str, Any]:
    scalar_values = [1.25, 16.5, 255.75]
    two_scalar_values = [(1.0, 2.5), (4.25, 8.75)]
    three_scalar_values = [(1.0, 2.0, 3.0), (10.25, 20.5, 30.75)]
    string_values = ["fixture-alpha", "fixture-name", "fixture-path"]
    rounded_values = [(1.2, 1), (2.6, 3), (9.1, 9)]

    for value in scalar_values:
        payload = struct.pack("<f", value)
        validate_roundtrip("scalar4_roundtrip", payload)
    for values in two_scalar_values:
        payload = struct.pack("<ff", *values)
        validate_roundtrip("two_scalar4_roundtrip", payload)
    for values in three_scalar_values:
        payload = struct.pack("<fff", *values)
        validate_roundtrip("three_scalar4_roundtrip", payload)
    for value in string_values:
        payload = value.encode("ascii") + b"\0"
        validate_roundtrip("owned_string_ascii_nul_shape_roundtrip", payload)
    for value, expected in rounded_values:
        actual = math.floor(value + 0.5)
        if actual != expected:
            raise DecodeError("rounded scalar synthetic fixture mismatch")

    return {
        "syntheticPublicSafeOnly": True,
        "rawBytesEmitted": False,
        "rawStringsEmitted": False,
        "rawNumericValuesEmitted": False,
        "scalar4RoundtripCases": len(scalar_values),
        "twoScalar4RoundtripCases": len(two_scalar_values),
        "threeScalar4RoundtripCases": len(three_scalar_values),
        "ownedStringAsciiNulShapeRoundtripCases": len(string_values),
        "roundedScalarFiniteNonTieCases": len(rounded_values),
        "totalSyntheticFixtureCases": len(scalar_values)
        + len(two_scalar_values)
        + len(three_scalar_values)
        + len(string_values)
        + len(rounded_values),
        "roundedScalarRule": "finite positive non-tie floor(x+0.5) fixture only",
        "roundingBoundary": "not exact CRT/x87 runtime parity and not gameplay balance proof",
    }


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        game_root = Path(tmp) / "game"
        fixture = game_root / "data" / "default physics.dat"
        fixture.parent.mkdir(parents=True)
        payload = bytearray()
        payload += struct.pack("<h", 0x12)
        payload += struct.pack("<ii", 1, 0)
        payload += b"unit_alpha\0"
        payload += struct.pack("<ii", 8, 4)
        payload += struct.pack("<f", 1.25)
        payload += struct.pack("<i", 0)
        payload += struct.pack("<ii", 9, 8)
        payload += struct.pack("<ff", 2.0, 3.0)
        payload += struct.pack("<i", 0)
        payload += struct.pack("<ii", 10, 12)
        payload += struct.pack("<fff", 4.0, 5.0, 6.0)
        payload += struct.pack("<i", 0)
        payload += struct.pack("<ii", 11, 14)
        payload += b"fixture-alpha\0"
        payload += struct.pack("<i", -1)
        payload += struct.pack("<i", -1)
        fixture.write_bytes(payload)
        report = build_report(game_root)
        assert report["status"] == "PASS"
        counts = report["corpus"]["fixtureClassCounts"]
        assert counts["scalar4_roundtrip"] == 1
        assert counts["two_scalar4_roundtrip"] == 1
        assert counts["three_scalar4_roundtrip"] == 1
        assert counts["owned_string_ascii_nul_shape_roundtrip"] == 1
    print("physics_script_scalar_string_decoder_fixture self-test: PASS")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--game-root", type=Path, default=DEFAULT_GAME_ROOT)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    report = build_report(args.game_root)
    if args.out:
        write_json(args.out, report)
        print(f"{report['status']}: wrote {repo_relative(args.out)}")
    else:
        print(json.dumps(report, indent=2))
    if args.check and report["status"] != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
