#!/usr/bin/env python3
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
Layout above is proved by byte-exact re-encode. MEANING is not. `world_id`,
`config_count` and the string contents are self-evident (the strings are
verbatim names from `battle engine configurations.dat`). The four trailing
i32s are named field_a..field_d deliberately: their semantics are NOT
established here, only their positions and values.

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
    python tools/worldheaders_decode.py "<path to worldheaders.dat>"

The byte-exact round-trip assertion runs on EVERY invocation, not only under
--self-test.
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_PATH = Path(
    r"C:\Program Files (x86)\Steam\steamapps\common"
    r"\Battle Engine Aquila\data\worldheaders.dat"
)

FILE_HEADER_SIZE = 0x08
RECORD_PREFIX_SIZE = 0x08  # version + payload_size
TRAILING_FIELD_COUNT = 4
# world_id + config_count + four trailing i32s
FIXED_PAYLOAD_BYTES = 4 + 4 + 4 * TRAILING_FIELD_COUNT  # 24


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


def parse_worldheaders(data: bytes) -> WorldHeaders:
    if len(data) < FILE_HEADER_SIZE:
        raise WorldHeadersError(f"too small: {len(data)} bytes")

    file_version = _i32(data, 0x00)
    record_count = _i32(data, 0x04)
    if record_count < 0:
        raise WorldHeadersError(f"negative record_count {record_count}")

    off = FILE_HEADER_SIZE
    records: list[WorldHeaderRecord] = []

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
    args = ap.parse_args(argv)

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
