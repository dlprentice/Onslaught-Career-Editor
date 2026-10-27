#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""
Decode BEA `data/worldheaders.dat` byte-exactly.

WHY THIS EXISTS
---------------
`worldheaders.dat` is authored content: a per-world table that names which
`battle engine configurations.dat` entries a world offers, plus four small
per-world integer flags. Before this tool the repository had no reader for it
at all (`grep -rli worldheaders --include=*.py --include=*.cs --include=*.ps1 .`
returned nothing), so a file that needs no reverse engineering was nonetheless
unreadable to every lane that wanted it.

LAYOUT (all little-endian; every claim below is proven by the round trip)
------------------------------------------------------------------------
File header, 8 bytes:
    0x0000  i32  file_version            = 1
    0x0004  i32  record_count            = 97

Then `record_count` records, back to back, first at 0x0008, last ending at
0x12AF == EOF (4,783 bytes). Each record:
    +0x00   i32  version                 = 3 in every shipped record
    +0x04   i32  payload_size            = bytes that follow this field
    +0x08   i32  world_id                (0, 1, 2, ... 961)
    +0x0C   i32  config_count
    +0x10   config_count Pascal strings: ONE u8 length byte, then that many
            ASCII bytes. NOT NUL-terminated, NOT padded, NOT aligned. Records
            after the first are therefore usually misaligned relative to 4.
    then    i32  field_a                 (version >= 2)
            i32  field_b                 (version >= 2)
            i32  field_c                 (version >= 2)
            i32  field_d                 (version >= 3)

`payload_size` == 24 + sum(1 + len(s) for s in configs) in all 97 records: the
24 is world_id + config_count + the four trailing i32s. It is a skip length,
letting a reader step to a target world without decoding the strings.

That record shape is the exact read sequence of retail
`CWorld::LoadWorldHeader` @ 0x0050D4C0 -- version, two i32s, then
`UBattleEngineConfigurations::Load/Skip` @ 0x0040F180/0x0040F260 (which reads
`i32 count` then `u8`-prefixed strings), then three i32s gated on version > 1
and one more gated on version > 2. The last one is stored to CWorld + 0x27C.
This file is a standalone concatenation of the same header blocks that head a
world archive.

MEANING vs LAYOUT
-----------------
Layout above is checked by byte-exact re-encode. That alone does not prove
field meanings. `world_id`,
`config_count` and the string contents are self-evident (the strings are
verbatim names from `battle engine configurations.dat`). The four trailing
i32s keep the legacy field_a..field_d names. The optional level metadata
projection additionally identifies field_d as CWorld::mType from the decompilation's
LoadHeader and EWorldType declarations; field_a..field_c remain uninterpreted.
This stored world type is separate from CGame::IsMultiplayer's numeric level
range, and neither establishes campaign co-op support.

WHAT THIS TOOL REFUSES TO DO
----------------------------
- It never writes to, patches, or mutates a Battle Engine Aquila installation.
  The file is opened read-only and the encoder's output is only ever compared
  in memory. There is no output-file option, by design.
- It does not synthesize records or repair a file that does not round-trip; a
  mismatch is reported as a failure, not silently normalized.

USAGE
-----
    python tools/worldheaders_decode.py --self-test
    python tools/worldheaders_decode.py --world 100
    python tools/worldheaders_decode.py --dump-json
    python tools/worldheaders_decode.py <input> --metadata-json --configurations <config-input>
    python tools/worldheaders_decode.py "<path to worldheaders.dat>"

The byte-exact round-trip assertion runs on EVERY invocation, not only under
--self-test.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import re
import struct
import sys
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

DEFAULT_PATH = Path(
    r"C:\Program Files (x86)\Steam\steamapps\common"
    r"\Battle Engine Aquila\data\worldheaders.dat"
)

FILE_HEADER_SIZE = 0x08
RECORD_PREFIX_SIZE = 0x08  # version + payload_size
TRAILING_FIELD_COUNT = 4
# world_id + config_count + four trailing i32s
FIXED_PAYLOAD_BYTES = 4 + 4 + 4 * TRAILING_FIELD_COUNT  # 24
LEVEL_METADATA_SCHEMA = "onslaught.level-header-metadata.v1"
MAX_METADATA_BYTES = 16 * 1024 * 1024
MAX_METADATA_RECORDS = 65_536
# Engineering projection bounds, not universal authored-format limits or
# the native runtime's separate 20-slot configuration array capacity.
MAX_METADATA_CONFIGS_PER_RECORD = 128
MAX_METADATA_CONFIG_REFERENCES = 8_192
MAX_METADATA_CONFIGURATION_BYTES = 64 * 1024
WORLD_MODE_NAMES = {0: "single-player", 1: "cooperative-multiplayer", 2: "versus-multiplayer"}
# Source-function pins describe the exact source used to derive these labels,
# not attestation of an input file or of a later build's runtime behavior.
LEVEL_METADATA_EVIDENCE = (
    {"source": "onslaught-decomp:src/world.cpp", "function": "CWorld::LoadHeader", "address": "0x0050d4c0",
     "functionSha256": "fa20f33b01caa1fcb7dc5a22e8a57fe499ac4aac065732b99f03c4063f41a690"},
    {"source": "onslaught-decomp:src/world.h", "declaration": "CWorld::EWorldType",
     "declarationSha256": "d4ad290340991717f6f4e48d53685efa689fdc3dc2766cc18eb83c398bf301d2"},
    {"source": "onslaught-decomp:src/game.cpp", "function": "CGame::IsMultiplayer", "address": "0x004725d0",
     "functionSha256": "06042e6bf074c23eaf60218f082f76f2eb2aa09c8b32a5881b9345f2361cdc8b"},
    {"source": "onslaught-decomp:src/BattleEngineConfigurations.cpp", "function": "UBattleEngineConfigurations::Load", "address": "0x0040f180",
     "functionSha256": "448c55496d7bdd705b86e444bacb29f3c0b3053a21366c84d3ea38e9a93c9a73"},
    {"source": "onslaught-decomp:src/FEPBEConfig.cpp", "function": "CFEPBEConfig::Load",
     "functionSha256": "e674b5e416f79e2b18511b047ccbd55be7d6826d5d5a8c9c8447f08aa1631fdc"},
    {"source": "onslaught-decomp:src/BattleEngineDataManager.h", "function": "UBattleEngineDataManager::GetConfiguration(char*)",
     "functionSha256": "babba77e33e630fd09a2841e62df63ebde60ea4662651fa46dc25564c24ebf42"},
)


def _i32(data: bytes, off: int) -> int:
    return struct.unpack_from("<i", data, off)[0]


@dataclass
class WorldHeaderRecord:
    offset: int  # absolute file offset of this record's `version` field
    version: int
    payload_size: int  # as stored, NOT recomputed
    world_id: int
    configs: list[str]
    trailing: list[int]  # field_a, field_b, field_c, field_d

    @property
    def computed_payload_size(self) -> int:
        return FIXED_PAYLOAD_BYTES + sum(1 + len(s) for s in self.configs)

    def to_dict(self) -> dict[str, object]:
        return {
            "offset": self.offset,
            "offset_hex": f"0x{self.offset:04X}",
            "version": self.version,
            "payload_size": self.payload_size,
            "world_id": self.world_id,
            "configs": list(self.configs),
            "field_a": self.trailing[0],
            "field_b": self.trailing[1],
            "field_c": self.trailing[2],
            "field_d": self.trailing[3],
        }


@dataclass
class WorldHeaders:
    file_version: int
    record_count: int
    records: list[WorldHeaderRecord] = field(default_factory=list)

    def by_world(self, world_id: int) -> WorldHeaderRecord | None:
        for r in self.records:
            if r.world_id == world_id:
                return r
        return None


class WorldHeadersError(ValueError):
    """Raised when the file does not match the proven layout."""


class WorldHeadersProfileLimit(WorldHeadersError):
    """A declared metadata count exceeded a bound before list allocation."""


class WorldHeadersUnsupportedVersion(WorldHeadersError):
    """No record fields are interpreted from an unadmitted record version."""


def _metadata_count_preflight(data: bytes, record_count: int) -> None:
    """Scalar framing/count admission, before the legacy parser allocates.

    Skip length-delimited record bodies; do not decode or collect names here.
    The existing parser still owns all string/body/round-trip validation.
    """
    offset = FILE_HEADER_SIZE
    references = 0
    for _ordinal in range(record_count):
        if offset + RECORD_PREFIX_SIZE + 8 > len(data):
            raise WorldHeadersError("truncated metadata record prefix")
        version, size, _world_id, count = struct.unpack_from("<4i", data, offset)
        if version != 3:
            raise WorldHeadersUnsupportedVersion("only record version 3 is admitted by this projection")
        if count < 0:
            raise WorldHeadersError("negative metadata configuration count")
        if count > MAX_METADATA_CONFIGS_PER_RECORD:
            raise WorldHeadersProfileLimit("per-record configuration count exceeds metadata profile")
        if count > MAX_METADATA_CONFIG_REFERENCES - references:
            raise WorldHeadersProfileLimit("aggregate configuration references exceed metadata profile")
        if size < 8 or size > len(data) - offset - RECORD_PREFIX_SIZE:
            raise WorldHeadersError("invalid metadata record size")
        references += count
        offset += RECORD_PREFIX_SIZE + size
    if offset != len(data):
        raise WorldHeadersError("unaccounted metadata record framing")


def parse_worldheaders(
    data: bytes, *, max_configs_per_record: int | None = None,
    max_config_references: int | None = None,
) -> WorldHeaders:
    for value in (max_configs_per_record, max_config_references):
        if value is not None and (type(value) is not int or value < 0):
            raise ValueError("configuration count limits must be nonnegative integers or None")
    if len(data) < FILE_HEADER_SIZE:
        raise WorldHeadersError(f"too small: {len(data)} bytes")

    file_version = _i32(data, 0x00)
    record_count = _i32(data, 0x04)
    if record_count < 0:
        raise WorldHeadersError(f"negative record_count {record_count}")

    off = FILE_HEADER_SIZE
    records: list[WorldHeaderRecord] = []
    configuration_references = 0

    for index in range(record_count):
        rec_off = off
        if off + RECORD_PREFIX_SIZE > len(data):
            raise WorldHeadersError(
                f"record {index}: truncated prefix at 0x{off:X}"
            )
        version = _i32(data, off + 0x00)
        payload_size = _i32(data, off + 0x04)
        off += RECORD_PREFIX_SIZE
        payload_start = off

        if version < 3:
            # Every shipped record is version 3. Lower versions would carry
            # fewer trailing fields (see CWorld::LoadWorldHeader); this decoder
            # refuses rather than guessing at a shape it has never observed.
            raise WorldHeadersError(
                f"record {index} at 0x{rec_off:X}: unsupported version {version}"
            )

        if payload_start + 8 > len(data):
            raise WorldHeadersError(f"record {index}: truncated payload")
        world_id = _i32(data, off + 0x00)
        config_count = _i32(data, off + 0x04)
        off += 8
        if config_count < 0:
            raise WorldHeadersError(
                f"record {index}: negative config_count {config_count}"
            )
        # Both checks precede the names list and decoding loop. The aggregate
        # bound also rejects many individually small records before projection
        # can expand their references into dictionaries. Never truncate.
        if max_configs_per_record is not None and config_count > max_configs_per_record:
            raise WorldHeadersProfileLimit("per-record configuration count exceeds metadata profile")
        if max_config_references is not None and config_count > max_config_references - configuration_references:
            raise WorldHeadersProfileLimit("aggregate configuration references exceed metadata profile")
        configuration_references += config_count

        configs: list[str] = []
        for s_index in range(config_count):
            if off >= len(data):
                raise WorldHeadersError(
                    f"record {index}: truncated string {s_index}"
                )
            length = data[off]
            off += 1
            if off + length > len(data):
                raise WorldHeadersError(
                    f"record {index}: string {s_index} runs past EOF"
                )
            raw = data[off : off + length]
            off += length
            configs.append(raw.decode("ascii"))

        if off + 4 * TRAILING_FIELD_COUNT > len(data):
            raise WorldHeadersError(f"record {index}: truncated trailing fields")
        trailing = [
            _i32(data, off + 4 * i) for i in range(TRAILING_FIELD_COUNT)
        ]
        off += 4 * TRAILING_FIELD_COUNT

        consumed = off - payload_start
        if consumed != payload_size:
            raise WorldHeadersError(
                f"record {index} at 0x{rec_off:X}: payload_size {payload_size} "
                f"but consumed {consumed}"
            )

        records.append(
            WorldHeaderRecord(
                offset=rec_off,
                version=version,
                payload_size=payload_size,
                world_id=world_id,
                configs=configs,
                trailing=trailing,
            )
        )

    if off != len(data):
        raise WorldHeadersError(
            f"{len(data) - off} unaccounted trailing bytes at 0x{off:X}"
        )

    return WorldHeaders(
        file_version=file_version, record_count=record_count, records=records
    )


def encode_worldheaders(wh: WorldHeaders) -> bytes:
    """Re-encode. Emits payload_size AS STORED so a wrong width surfaces."""
    out = bytearray()
    out += struct.pack("<ii", wh.file_version, wh.record_count)
    for r in wh.records:
        out += struct.pack("<ii", r.version, r.payload_size)
        out += struct.pack("<ii", r.world_id, len(r.configs))
        for s in r.configs:
            raw = s.encode("ascii")
            if len(raw) > 0xFF:
                raise WorldHeadersError(f"config name too long: {s!r}")
            out.append(len(raw))
            out += raw
        for v in r.trailing:
            out += struct.pack("<i", v)
    return bytes(out)


def assert_round_trip(data: bytes, wh: WorldHeaders) -> None:
    """Byte-exact round trip. Raises with the first differing offset."""
    again = encode_worldheaders(wh)
    if again == data:
        return
    if len(again) != len(data):
        raise WorldHeadersError(
            f"round trip length differs: {len(again)} vs {len(data)}"
        )
    for i, (a, b) in enumerate(zip(again, data)):
        if a != b:
            raise WorldHeadersError(
                f"round trip differs at 0x{i:X}: encoded 0x{a:02X} "
                f"!= original 0x{b:02X}"
            )
    raise WorldHeadersError("round trip differs (unlocated)")


def _metadata_source(data: bytes, logical_path: str) -> dict[str, object]:
    """Describe immutable held bytes without recording a machine pathname."""
    if not isinstance(data, bytes):
        raise ValueError("metadata inputs must be immutable held bytes")
    if (not logical_path or "\0" in logical_path or "\\" in logical_path
            or PurePosixPath(logical_path).is_absolute() or re.match(r"^[A-Za-z]:", logical_path)
            or any(part in ("", ".", "..") for part in logical_path.split("/"))):
        raise ValueError("metadata source paths must be normalized logical relative paths")
    return {"path": logical_path, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def _occurrence_id(source: dict[str, object], ordinal: int, offset: int, record_sha: str) -> str:
    coordinate = [source["path"], source["sha256"], ordinal, offset, record_sha]
    encoded = json.dumps(coordinate, ensure_ascii=True, separators=(",", ":")).encode("ascii")
    return "level-header:" + hashlib.sha256(b"onslaught.level-header-occurrence.v1\0" + encoded).hexdigest()


def _configuration_metadata(data: bytes | None, logical_path: str) -> tuple[dict[str, object], list[dict[str, object]]]:
    if data is None:
        return {"status": "not-supplied"}, []
    source = _metadata_source(data, logical_path)
    if len(data) > MAX_METADATA_CONFIGURATION_BYTES:
        return {"source": source, "status": "unparsed", "reason": "configuration input exceeds metadata byte limit"}, []
    # One existing six-record/version-12 parser owns configuration framing and
    # unknown spans. No new configuration format or runtime fallback is modeled.
    from battle_engine_config_decode import BattleEngineConfigError, encode_config, parse_config
    try:
        parsed = parse_config(data)
        if encode_config(parsed) != data:
            raise BattleEngineConfigError("configuration round trip differs")
    except (BattleEngineConfigError, UnicodeError, struct.error):
        return {"source": source, "status": "unparsed",
                "reason": "input is outside the existing configuration decoder profile",
                "falsifier": "provide a bounded six-record version-12 input accepted by battle_engine_config_decode"}, []
    rows = []
    for record in parsed.records:
        record_sha = hashlib.sha256(data[record.offset:record.end_offset]).hexdigest()
        rows.append({"ordinal": record.index, "offset": record.offset, "endOffset": record.end_offset,
                     "name": record.configuration_name, "recordSha256": record_sha,
                     "occurrenceId": "configuration:" + hashlib.sha256(
                         json.dumps([source["path"], source["sha256"], record.index, record.offset, record_sha],
                                    separators=(",", ":")).encode("ascii")
                     ).hexdigest()})
    return {"source": source, "status": "projected", "records": rows,
            "limit": "name membership only; not gameplay parameter or loaded-object validation"}, rows


def project_level_metadata(
    data: bytes, *, source_path: str = "data/worldheaders.dat",
    configuration_data: bytes | None = None,
    configuration_source_path: str = "data/battle engine configurations.dat",
) -> dict[str, object]:
    """Source-free private metadata from the existing version-3 decoder.

    Hashes bind the held bytes actually parsed. Names/ordinals/raw integers
    are retained, but no original records, scripts or assets are emitted.
    Stored world mode, the separate retail numeric multiplayer predicate,
    configuration name membership and CE support are deliberately distinct.
    Malformed/unsupported input remains an explicit hashed source outcome.
    This function never reads a game installation or changes any input.
    """
    source = _metadata_source(data, source_path)
    configs, config_rows = _configuration_metadata(configuration_data, configuration_source_path)
    report: dict[str, object] = {
        "schema": LEVEL_METADATA_SCHEMA, "profile": "PC-file-version-1-record-version-3",
        "source": source, "status": "unparsed", "records": [],
        "configurationInput": configs, "sourceEvidence": [dict(row) for row in LEVEL_METADATA_EVIDENCE],
        "metadataLimits": {"sourceBytes": MAX_METADATA_BYTES, "worldRecords": MAX_METADATA_RECORDS,
                           "configurationsPerRecord": MAX_METADATA_CONFIGS_PER_RECORD,
                           "configurationReferences": MAX_METADATA_CONFIG_REFERENCES,
                           "configurationInputBytes": MAX_METADATA_CONFIGURATION_BYTES,
                           "meaning": "engineering projection bounds; not authored format or native runtime maxima"},
        "evidenceClass": "bounded static metadata; source-derived meanings, not runtime acceptance",
        "limits": ["selected header/configuration inputs only; no level archive or mission-script completeness claim",
                   "stored cooperative mode does not establish CE campaign co-op, networking or player readiness",
                   "unknown fields are retained as integers without inferred editor semantics"],
    }
    if len(data) > MAX_METADATA_BYTES:
        report["reason"] = "world-header input exceeds metadata byte limit"
        return report
    if len(data) < FILE_HEADER_SIZE:
        report["reason"] = "truncated world-header file header"
        return report
    file_version, record_count = struct.unpack_from("<ii", data)
    report.update(fileVersion=file_version, declaredRecords=record_count)
    if file_version != 1:
        report.update(status="unsupported", reason="only file version 1 is admitted by this projection")
        return report
    if not 0 <= record_count <= MAX_METADATA_RECORDS:
        report["reason"] = "world-header record count exceeds metadata profile"
        return report
    try:
        _metadata_count_preflight(data, record_count)
        parsed = parse_worldheaders(data, max_configs_per_record=MAX_METADATA_CONFIGS_PER_RECORD,
                                   max_config_references=MAX_METADATA_CONFIG_REFERENCES)
        assert_round_trip(data, parsed)
    except WorldHeadersUnsupportedVersion as error:
        report.update(status="unsupported", reason=str(error))
        return report
    except WorldHeadersProfileLimit as error:
        report.update(reason=str(error),
                      falsifier="select an input within the declared metadata count bounds; no records were truncated")
        return report
    except (WorldHeadersError, UnicodeError, struct.error):
        report.update(reason="malformed or unsupported world-header record framing",
                      falsifier="check record versions, declared sizes, ASCII names, counts and exact EOF with the existing decoder")
        return report
    unsupported = [ordinal for ordinal, record in enumerate(parsed.records) if record.version != 3]
    if unsupported:
        report.update(status="unsupported", reason="only record version 3 is admitted by this projection",
                      unsupportedRecordOrdinals=unsupported)
        return report
    world_multiplicity = Counter(record.world_id for record in parsed.records)
    config_lookup: dict[str, list[dict[str, object]]] = {}
    for record in config_rows:
        config_lookup.setdefault(str(record["name"]), []).append(record)
    rows = []
    for ordinal, record in enumerate(parsed.records):
        end = record.offset + RECORD_PREFIX_SIZE + record.payload_size
        digest = hashlib.sha256(data[record.offset:end]).hexdigest()
        identity = _occurrence_id(source, ordinal, record.offset, digest)
        name_multiplicity = Counter(record.configs)
        configurations = []
        for index, name in enumerate(record.configs):
            # Native Pascal length is a signed char, and native name lookup
            # uses strcmp. Preserve unsafe/unresolved names; never case-fold,
            # trim, choose an alias or apply the game's fallback profile.
            safe_name = bool(name) and len(name) <= 127 and name.isascii() and name.isprintable()
            matches = config_lookup.get(name, []) if safe_name else []
            status = ("unresolved-native-name" if not safe_name else "not-checked" if configs["status"] == "not-supplied"
                      else "unparsed-configuration-input" if configs["status"] != "projected"
                      else "missing" if not matches else "unique-name-match" if len(matches) == 1 else "ambiguous")
            configurations.append({"ordinal": index, "name": name, "localNameMultiplicity": name_multiplicity[name],
                                   "occurrenceId": identity + "/configuration:" + str(index),
                                   "resolution": status, "candidateOccurrenceIds": [row["occurrenceId"] for row in matches]})
        mode = record.trailing[3]
        rows.append({
            "ordinal": ordinal, "occurrenceId": identity, "offset": record.offset, "endOffset": end,
            "recordSha256": digest, "version": record.version, "payloadBytes": record.payload_size,
            "worldId": record.world_id, "worldIdMultiplicity": world_multiplicity[record.world_id],
            "configurations": configurations,
            "rawTrailing": dict(zip(("field_a", "field_b", "field_c", "field_d"), record.trailing)),
            "worldMode": {"raw": mode, "name": WORLD_MODE_NAMES.get(mode),
                          "status": "source-enum" if mode in WORLD_MODE_NAMES else "unknown-enum-value"},
            "retailGameMultiplayerLevelPredicate": 850 <= record.world_id < 900,
            "modeAndLevelPredicateAgreement": None if mode not in WORLD_MODE_NAMES else ((mode in (1, 2)) == (850 <= record.world_id < 900)),
            "uninterpretedFields": ["field_a", "field_b", "field_c"],
            "ceNetworkAdmission": "not established by this metadata",
            "missionScript": {"status": "not-in-this-input", "path": None},
        })
    report.update(status="projected", roundTrip="byte-exact", records=rows,
                  duplicateWorldIds=sorted(world for world, count in world_multiplicity.items() if count > 1))
    return report


def run_self_test(path: Path) -> int:
    data = path.read_bytes()
    wh = parse_worldheaders(data)

    checks: list[tuple[str, bool, str]] = []

    checks.append(
        ("record_count matches records parsed",
         wh.record_count == len(wh.records),
         f"{wh.record_count} == {len(wh.records)}")
    )

    total_bytes = len(encode_worldheaders(wh))
    checks.append(
        ("every byte accounted for",
         total_bytes == len(data),
         f"{total_bytes} == {len(data)}")
    )

    size_ok = all(r.payload_size == r.computed_payload_size for r in wh.records)
    checks.append(
        ("stored payload_size == 24 + string bytes, all records",
         size_ok, "97/97" if size_ok else "MISMATCH")
    )

    ver_ok = all(r.version == 3 for r in wh.records)
    checks.append(("every record version == 3", ver_ok, ""))

    ascii_ok = all(
        s.isprintable() and s.isascii() for r in wh.records for s in r.configs
    )
    n_strings = sum(len(r.configs) for r in wh.records)
    checks.append(
        ("all config names printable ASCII", ascii_ok, f"{n_strings} strings")
    )

    round_trip_ok = True
    round_trip_detail = "byte-exact"
    try:
        assert_round_trip(data, wh)
    except WorldHeadersError as exc:
        round_trip_ok = False
        round_trip_detail = str(exc)
    checks.append(
        ("re-encode is byte-identical to the original file",
         round_trip_ok, round_trip_detail)
    )

    failed = 0
    print(f"self-test: {path}")
    print(f"size: {len(data)} bytes")
    for name, ok, detail in checks:
        mark = "PASS" if ok else "FAIL"
        suffix = f"  ({detail})" if detail else ""
        print(f"  [{mark}] {name}{suffix}")
        if not ok:
            failed += 1
    print("")
    print("SELF-TEST FAILED" if failed else "SELF-TEST PASSED")
    return 1 if failed else 0


def _print_record(r: WorldHeaderRecord) -> None:
    configs = ", ".join(r.configs) if r.configs else "(none)"
    print(
        f"0x{r.offset:04X}  world={r.world_id:<4d} ver={r.version} "
        f"size={r.payload_size:<3d} "
        f"fields=[{r.trailing[0]},{r.trailing[1]},{r.trailing[2]},"
        f"{r.trailing[3]}]  configs[{len(r.configs)}]: {configs}"
    )


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description="Byte-exact decoder for BEA data/worldheaders.dat "
        "(read-only; never writes to the game install)."
    )
    ap.add_argument(
        "path",
        type=Path,
        nargs="?",
        default=DEFAULT_PATH,
        help=f"Path to worldheaders.dat (default: {DEFAULT_PATH})",
    )
    ap.add_argument(
        "--self-test",
        action="store_true",
        help="Run the layout invariants + byte-exact round-trip test and exit",
    )
    ap.add_argument(
        "--world", type=int, action="append", default=[],
        help="Only show this world_id (repeatable)",
    )
    ap.add_argument("--dump-json", action="store_true", help="Dump as JSON")
    ap.add_argument("--metadata-json", action="store_true",
                    help="Private source-free level metadata with exact input/record hashes; stdout only")
    ap.add_argument("--source-path", default="data/worldheaders.dat",
                    help="Logical relative source label used only by --metadata-json")
    ap.add_argument("--configurations", type=Path,
                    help="Optional selected configuration input for exact case-sensitive name membership")
    ap.add_argument("--configuration-source-path", default="data/battle engine configurations.dat",
                    help="Logical relative label for the optional configuration input")
    args = ap.parse_args(argv)

    if args.metadata_json:
        if args.self_test or args.dump_json or args.world:
            ap.error("--metadata-json requires the complete selected input, without --world/--dump-json/--self-test")
        from aya_archive_inventory import ArchiveObservationError, read_held_archive
        try:
            # Reuse the existing retained-handle, identity-revalidated reader.
            # Metadata admission then enforces its smaller format byte bound.
            data = read_held_archive(args.path)
            config_unavailable = False
            config_data = None
            if args.configurations is not None:
                _metadata_source(b"", args.configuration_source_path)  # validate label even when the file is unavailable
                try:
                    config_data = read_held_archive(args.configurations)
                except ArchiveObservationError:
                    config_unavailable = True
            report = project_level_metadata(data, source_path=args.source_path,
                                            configuration_data=config_data,
                                            configuration_source_path=args.configuration_source_path)
            if config_unavailable:
                report["configurationInput"] = {"status": "unavailable", "path": args.configuration_source_path,
                                                "reason": "selected optional configuration input was refused"}
                for row in report["records"]:
                    for configuration in row["configurations"]:
                        if configuration["resolution"] == "not-checked":
                            configuration["resolution"] = "unparsed-configuration-input"
        except (ArchiveObservationError, ValueError):
            print(json.dumps({"schema": LEVEL_METADATA_SCHEMA, "status": "unavailable",
                              "reason": "selected metadata inputs or logical source labels were refused"}))
            return 1
        print(json.dumps(report, indent=2, allow_nan=False))
        return 0 if report["status"] == "projected" else 1
    if args.configurations is not None:
        ap.error("--configurations is only used by --metadata-json")

    if not args.path.exists():
        raise SystemExit(f"not found: {args.path}")

    if args.self_test:
        return run_self_test(args.path)

    data = args.path.read_bytes()
    wh = parse_worldheaders(data)
    # The round trip runs on every invocation, not only under --self-test.
    assert_round_trip(data, wh)

    selected = wh.records
    if args.world:
        wanted = set(args.world)
        selected = [r for r in wh.records if r.world_id in wanted]
        missing = wanted - {r.world_id for r in wh.records}
        if missing:
            raise SystemExit(f"no such world_id: {sorted(missing)}")

    if args.dump_json:
        print(json.dumps(
            {
                "path": str(args.path),
                "size": len(data),
                "file_version": wh.file_version,
                "record_count": wh.record_count,
                "round_trip": "byte-exact",
                "records": [r.to_dict() for r in selected],
            },
            indent=2,
        ))
        return 0

    print(f"path: {args.path}")
    print(f"size: 0x{len(data):X} ({len(data)} bytes)")
    print(f"file_version: {wh.file_version} (at 0x00)")
    print(f"record_count: {wh.record_count} (at 0x04)")
    print("round_trip: byte-exact")
    print("")
    for r in selected:
        _print_record(r)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
