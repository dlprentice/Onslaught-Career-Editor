#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Prove the five current PC function-body fragment repairs.

The output is evidence for a disposable Ghidra range repair.  It does not
authorize mutation of the live or tracked project and it does not assign new
names, signatures, comments, tags, or semantics.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import capstone
from capstone import CS_ARCH_X86, CS_MODE_32, Cs


RETAIL_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
DEMO_SHA256 = "d8637dd755b21c720c0cb8f71923f94d2a04a184d90f5343c2e868ce8606e5c2"
CAPSTONE_VERSION = "5.0.7"

EXPECTED_INPUTS = {
    "body_ranges": (1198388, "0101e6e8b34eaea8bd646a0fa9a8e4e448bef586c8b2b898c78241befde3aa6b"),
    "gap_classification": (834976, "6f32e827bed3094b4a78511c0493460f60d0c6b711e0ee06bc36914898f070b5"),
    "inbound_references": (257316, "98d227955cdbf674cdc94fb680d7dd0ef8662055b148a9b222b5b020d7b45499"),
    "loose_instructions": (1247670, "01aa0b268fe078ca66289384ccb5ae6db202b6ca6885506b33abc780d4af9c30"),
    "function_map": (1314885, "cdb26380bb6b29e82edd601bb95dfc215f62813d925e2f4c4c78452a7af7c68a"),
    "runtime_parent": (9063, "624c2e9c670445c2a606b54aa9ba3bc0b9f39da4ae704f0363c659032e947134"),
    "runtime_switch_base": (5170, "0f42db8d02e42435be8fb27046b2c93d8a025e9acbfa924eb7c6f91c3ec19070"),
    "runtime_switch_extension": (5613, "97852e4dbacf08920f065a08ac87052ccd62e7bceba312f7e5cbf45217438ea7"),
    "runtime_range": (14784, "0d311f5f5a972e1fb028c4b6c3e936fb8dfa5cd3bc2f6d6359fc1c6ecdff5501"),
    "coverage_join": (194696, "865238e8531c8a9d1b34b397c0694888b91e6bae28e6b23c2c681ba06f68417f"),
    "source_game": (103727, "7f6932e001f0c57938dd49aba07ab1cd05239e7a038096fb25310a34e9a4ef4e"),
}


class ProofError(ValueError):
    pass


def require(value: bool, message: str) -> None:
    if not value:
        raise ProofError(message)


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stamp(path: Path) -> dict[str, Any]:
    return {"path": path.name, "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def check_stamp(path: Path, role: str) -> None:
    require(path.is_file(), f"missing {role}: {path}")
    actual = (path.stat().st_size, sha256_file(path))
    require(actual == EXPECTED_INPUTS[role], f"{role} identity mismatch: {actual}")


def read_tsv(path: Path, comments: bool = False) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        lines: Iterable[str] = stream
        if comments:
            lines = (line for line in stream if not line.startswith("#"))
        return list(csv.DictReader(lines, delimiter="\t"))


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def va(value: int) -> str:
    return f"0x{value:08x}"


def canonical_ranges(ranges: Iterable[tuple[int, int]]) -> str:
    return ";".join(f"{va(start)}-{va(end)}" for start, end in ranges)


def merge_ranges(ranges: Iterable[tuple[int, int]]) -> tuple[tuple[int, int], ...]:
    ordered = sorted(ranges)
    result: list[list[int]] = []
    for start, end in ordered:
        require(start < end, "empty range")
        if not result or start > result[-1][1]:
            result.append([start, end])
        else:
            require(start >= result[-1][0], "range order")
            result[-1][1] = max(result[-1][1], end)
    return tuple((start, end) for start, end in result)


class PEImage:
    def __init__(self, raw: bytes):
        self.raw = raw
        pe = struct.unpack_from("<I", raw, 0x3C)[0]
        require(raw[pe : pe + 4] == b"PE\0\0", "invalid PE signature")
        section_count = struct.unpack_from("<H", raw, pe + 6)[0]
        optional_size = struct.unpack_from("<H", raw, pe + 20)[0]
        optional = pe + 24
        self.image_base = struct.unpack_from("<I", raw, optional + 28)[0]
        table = optional + optional_size
        self.sections: list[tuple[str, int, int, int, int]] = []
        for index in range(section_count):
            off = table + 40 * index
            name = raw[off : off + 8].rstrip(b"\0").decode("ascii", "replace")
            virtual_size, rva, raw_size, raw_offset = struct.unpack_from("<IIII", raw, off + 8)
            self.sections.append((name, rva, virtual_size, raw_offset, raw_size))

    def bytes_at(self, address: int, size: int) -> bytes:
        rva = address - self.image_base
        for _name, start, virtual_size, raw_offset, raw_size in self.sections:
            extent = max(virtual_size, raw_size)
            if start <= rva and rva + size <= start + extent:
                delta = rva - start
                require(delta + size <= raw_size, f"range is not file-backed: {va(address)}+{size}")
                return self.raw[raw_offset + delta : raw_offset + delta + size]
        raise ProofError(f"unmapped VA: {va(address)}+{size}")

    def dwords(self, address: int, count: int) -> tuple[int, ...]:
        return struct.unpack("<" + "I" * count, self.bytes_at(address, count * 4))


@dataclass(frozen=True)
class Fragment:
    owner: int
    name: str
    envelope_start: int
    envelope_end: int
    repair_end: int
    demo_owner: int
    demo_start: int
    demo_end: int
    next_retail: int
    next_demo: int
    pre_ranges: tuple[tuple[int, int], ...]
    owner_ref_count: int
    runtime_grade: str

    @property
    def repair(self) -> tuple[int, int]:
        return (self.envelope_start, self.repair_end)

    @property
    def post_ranges(self) -> tuple[tuple[int, int], ...]:
        return merge_ranges((*self.pre_ranges, self.repair))


FRAGMENTS = (
    Fragment(
        0x00462640,
        "CFEPMain__Process",
        0x0046282B,
        0x00462B70,
        0x00462B64,
        0x00462650,
        0x0046283B,
        0x00462B74,
        0x00462B70,
        0x00462B80,
        ((0x00462640, 0x0046282B),),
        3,
        "RUNTIME_RANGE_HIT_NONREADY_WRAPPER",
    ),
    Fragment(
        0x0046FF10,
        "CGame__HandleEvent",
        0x004700DA,
        0x004700F0,
        0x004700F0,
        0x0046FDE0,
        0x0046FFAA,
        0x0046FFC0,
        0x00470120,
        0x0046FFF0,
        (
            (0x0046FF10, 0x0047004A),
            (0x0047005D, 0x004700DA),
            (0x004700F0, 0x004700F6),
        ),
        1,
        "NO_RETAINED_FRAGMENT_RUNTIME_HIT",
    ),
    Fragment(
        0x00482590,
        "CHud__RenderTargetIndicatorOverlay",
        0x00482725,
        0x00482741,
        0x00482741,
        0x00482380,
        0x00482515,
        0x00482531,
        0x00483530,
        0x00483320,
        ((0x00482590, 0x00482725), (0x00482741, 0x00483505)),
        1,
        "RUNTIME_JMP_TABLE_CASE_HIT_READY",
    ),
    Fragment(
        0x004BE420,
        "CExplosionInitThing__SelectNextPathStepDirection",
        0x004BE82D,
        0x004BE93D,
        0x004BE93D,
        0x004BE330,
        0x004BE73D,
        0x004BE84D,
        0x004BE970,
        0x004BE880,
        ((0x004BE420, 0x004BE82D), (0x004BE93D, 0x004BE94C)),
        5,
        "RUNTIME_FULL_FRAGMENT_COVERED_READY",
    ),
    Fragment(
        0x00559410,
        "CDXTexture__CreateMipmaps",
        0x0055954C,
        0x005595BB,
        0x005595BB,
        0x00559AB0,
        0x00559BEC,
        0x00559C5B,
        0x00559BE0,
        0x0055A280,
        ((0x00559410, 0x0055954C), (0x005595BB, 0x00559B6A)),
        2,
        "NO_RETAINED_FRAGMENT_RUNTIME_HIT",
    ),
)


TABLES = (
    (0x00483508, (0x00482725, 0x0048272C, 0x00482733, 0x0048273A),
     0x004832F8, (0x00482515, 0x0048251C, 0x00482523, 0x0048252A)),
    (0x004BE94C, (0x004BE82D, 0x004BE883, 0x004BE8B1, 0x004BE8DF, 0x004BE90E),
     0x004BE85C, (0x004BE73D, 0x004BE793, 0x004BE7C1, 0x004BE7EF, 0x004BE81E)),
    (0x004BE960, (0x004BE857, 0x004BE86D, 0x004BE862, 0x004BE878),
     0x004BE870, (0x004BE767, 0x004BE77D, 0x004BE772, 0x004BE788)),
    (0x00559B98,
     (0x00559592, 0x0055954C, 0x00559553, 0x0055955A, 0x00559561, 0x00559568,
      0x0055956F, 0x00559576, 0x0055957D, 0x00559584, 0x0055958B),
     0x0055A238,
     (0x00559C32, 0x00559BEC, 0x00559BF3, 0x00559BFA, 0x00559C01, 0x00559C08,
      0x00559C0F, 0x00559C16, 0x00559C1D, 0x00559C24, 0x00559C2B)),
)


def decode_exact(decoder: Cs, raw: bytes, start: int) -> tuple[Any, ...]:
    instructions = tuple(decoder.disasm(raw, start))
    require(bool(instructions), f"empty decode at {va(start)}")
    cursor = start
    for instruction in instructions:
        require(instruction.address == cursor, f"decode gap at {va(cursor)}")
        cursor += instruction.size
    require(cursor == start + len(raw), f"decode did not cover range at {va(start)}")
    return instructions


def normalized(instruction: Any) -> bytes:
    raw = bytearray(instruction.bytes)
    for offset, size in (
        (instruction.encoding.imm_offset, instruction.encoding.imm_size),
        (instruction.encoding.disp_offset, instruction.encoding.disp_size),
    ):
        if offset and size:
            raw[offset : offset + size] = b"\0" * size
    return bytes(raw)


def instruction_identity(instructions: Iterable[Any]) -> tuple[tuple[int, str, bytes], ...]:
    return tuple((item.size, item.mnemonic, normalized(item)) for item in instructions)


def identity_sha256(identity: Iterable[tuple[int, str, bytes]]) -> str:
    digest = hashlib.sha256()
    for size, mnemonic, raw in identity:
        digest.update(bytes([size]))
        digest.update(mnemonic.encode("ascii"))
        digest.update(b"\0")
        digest.update(raw)
    return digest.hexdigest()


def instruction_layout_sha256(instructions: Iterable[Any], start: int) -> str:
    digest = hashlib.sha256()
    for instruction in instructions:
        digest.update(
            f"{instruction.address - start:08x}:{instruction.size}:{bytes(instruction.bytes).hex()}\n".encode(
                "ascii"
            )
        )
    return digest.hexdigest()


def unique_demo_match(
    decoder: Cs,
    retail_identity: tuple[tuple[int, str, bytes], ...],
    image: PEImage,
    start: int,
    end: int,
    size: int,
) -> tuple[int, ...]:
    matches: list[int] = []
    first_byte = retail_identity[0][2][0]
    for address in range(start, end - size + 1):
        raw = image.bytes_at(address, size)
        if raw[0] != first_byte:
            continue
        try:
            candidate = decode_exact(decoder, raw, address)
        except ProofError:
            continue
        if instruction_identity(candidate) == retail_identity:
            matches.append(address)
    return tuple(matches)


def parse_range_rows(rows: list[dict[str, str]]) -> tuple[dict[int, list[tuple[int, int]]], int]:
    grouped: dict[int, list[tuple[int, int]]] = {}
    intervals: list[tuple[int, int]] = []
    for row in rows:
        entry = int(row["functionAddress"], 16)
        start = int(row["rangeMin"], 16)
        end = int(row["rangeEndExclusive"], 16)
        grouped.setdefault(entry, []).append((start, end))
        intervals.append((start, end))
    require(len(grouped) == 8280 and len(rows) == 8400, "current function/range count drift")
    cursor = 0
    owned = 0
    for start, end in sorted(intervals):
        require(start >= cursor, f"current body overlap at {va(start)}")
        cursor = end
        owned += end - start
    require(owned == 1794212, f"current ownership drift: {owned}")
    return grouped, owned


def coverage_intersections(
    join_path: Path,
    local_root: Path,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    join = read_json(join_path)
    stamps = join.get("coverageStamps")
    require(isinstance(stamps, list) and len(stamps) >= 80, "coverage stamp census missing")
    union: dict[int, list[tuple[int, int]]] = {item.owner: [] for item in FRAGMENTS}
    hit_files: dict[int, set[str]] = {item.owner: set() for item in FRAGMENTS}
    verified = 0
    missing = 0
    for source in stamps:
        logical = source["path"]
        path = Path(logical)
        if not path.is_absolute():
            path = local_root / path
        if not path.is_file():
            missing += 1
            continue
        require(path.stat().st_size == source["bytes"], f"coverage byte drift: {logical}")
        require(sha256_file(path) == source["sha256"], f"coverage hash drift: {logical}")
        verified += 1
        with path.open("r", encoding="utf-8") as stream:
            for line in stream:
                if '"kind":"range"' not in line:
                    continue
                row = json.loads(line)
                low = int(row["va_start"], 16)
                high = int(row["va_end_exclusive"], 16)
                for fragment in FRAGMENTS:
                    start, end = fragment.repair
                    a, b = max(low, start), min(high, end)
                    if a < b:
                        union[fragment.owner].append((a, b))
                        hit_files[fragment.owner].add(logical.replace("\\", "/"))
    rows: list[dict[str, Any]] = []
    for fragment in FRAGMENTS:
        merged = merge_ranges(union[fragment.owner]) if union[fragment.owner] else ()
        covered = sum(end - start for start, end in merged)
        rows.append(
            {
                "owner": va(fragment.owner),
                "name": fragment.name,
                "repair_ranges": canonical_ranges((fragment.repair,)),
                "repair_bytes": fragment.repair_end - fragment.envelope_start,
                "covered_bytes_union": covered,
                "covered_ranges_union": canonical_ranges(merged),
                "coverage_files_with_hits": len(hit_files[fragment.owner]),
                "runtime_grade": fragment.runtime_grade,
            }
        )
    return rows, {"stamps": len(stamps), "verified": verified, "missing": missing}


def verify_runtime(
    parent_path: Path,
    base_path: Path,
    extension_path: Path,
    range_path: Path,
) -> None:
    parent = read_json(parent_path)
    base = read_json(base_path)
    extension = read_json(extension_path)
    ranges = read_json(range_path)
    require(parent["status"] == base["status"] == extension["status"] == ranges["status"] == "MEASURED", "runtime status drift")
    union = {int(row["entryVa"], 16): row for row in parent["unionBest"]["targets"]}
    require(union[0x00462640]["grade"] == "RUNTIME_CALL_ENTRY", "FEP parent runtime drift")
    require(union[0x00482590]["grade"] == "RUNTIME_CALL_ENTRY", "HUD parent runtime drift")
    require(union[0x004BE420]["grade"] == "RUNTIME_CALL_ENTRY", "explosion parent runtime drift")
    ready = {int(row["entryVa"], 16): row for row in parent["unionBestReadyOnly"]["targets"]}
    require(ready[0x00462640]["grade"] == "RUNTIME_UNREACHED", "FEP READY limitation drift")
    require(ready[0x00482590]["grade"] == "RUNTIME_CALL_ENTRY", "HUD READY parent drift")
    require(ready[0x004BE420]["grade"] == "RUNTIME_CALL_ENTRY", "explosion READY parent drift")
    base_rows = {int(row["candidateVa"], 16): row for row in base["results"]}
    require(base_rows[0x004BE82D]["level521"]["runtimeGrade"] == "RUNTIME_JMP_TABLE_CASE_HIT", "explosion case runtime drift")
    extension_rows = {int(row["entryVa"], 16): row for row in extension["union4Targets"]}
    require(extension_rows[0x00482725]["grade"] == "RUNTIME_JMP_TABLE_CASE_HIT", "HUD case runtime drift")
    fep = [row for row in ranges["recoveries"] if row.get("prevFunc") == "CFEPMain__Process"]
    require([int(row["residualVa"], 16) for row in fep] == [0x0046282B, 0x00462906, 0x00462953, 0x00462A09, 0x00462AC4], "FEP residual runtime set drift")


def write_tsv(path: Path, rows: list[dict[str, Any]]) -> None:
    require(rows, f"empty TSV output: {path}")
    require(not path.exists(), f"refusing to overwrite {path}")
    with path.open("x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, value: Any) -> None:
    require(not path.exists(), f"refusing to overwrite {path}")
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--retail", required=True, type=Path)
    parser.add_argument("--demo", required=True, type=Path)
    for role in EXPECTED_INPUTS:
        if role == "source_game":
            parser.add_argument("--source-game", required=True, type=Path)
        else:
            parser.add_argument("--" + role.replace("_", "-"), required=True, type=Path)
    parser.add_argument("--coverage-local-root", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    require(capstone.__version__ == CAPSTONE_VERSION, "Capstone version drift")
    for role in EXPECTED_INPUTS:
        check_stamp(getattr(args, role), role)
    retail_raw = args.retail.read_bytes()
    demo_raw = args.demo.read_bytes()
    require(sha256_bytes(retail_raw) == RETAIL_SHA256, "retail specimen identity mismatch")
    require(sha256_bytes(demo_raw) == DEMO_SHA256, "demo specimen identity mismatch")
    retail = PEImage(retail_raw)
    demo = PEImage(demo_raw)
    require(retail.image_base == demo.image_base == 0x00400000, "image base drift")

    output = args.output_dir
    require(not output.exists(), f"refusing existing output directory: {output}")
    output.mkdir(parents=True)

    body_rows = read_tsv(args.body_ranges, comments=True)
    bodies, owned_before = parse_range_rows(body_rows)
    gaps = read_tsv(args.gap_classification)
    candidates = [row for row in gaps if row["classification"] == "FUNCTION_FRAGMENT_CANDIDATE"]
    require(len(candidates) == 5, f"fragment candidate count drift: {len(candidates)}")
    expected_envelopes = {(item.envelope_start, item.envelope_end) for item in FRAGMENTS}
    actual_envelopes = {(int(row["start"], 16), int(row["endExclusive"], 16)) for row in candidates}
    require(actual_envelopes == expected_envelopes, "candidate set is not the exact five")

    refs = read_tsv(args.inbound_references)
    loose = read_tsv(args.loose_instructions)
    map_rows = read_tsv(args.function_map)
    mapping = {int(row["retail_va"], 16): int(row["demo_va"], 16) for row in map_rows}
    require(len(mapping) == 8086, f"current mapped-function cardinality drift: {len(mapping)}")

    decoder = Cs(CS_ARCH_X86, CS_MODE_32)
    decoder.detail = True
    manifest_rows: list[dict[str, Any]] = []
    proof_rows: list[dict[str, Any]] = []
    added_bytes = 0
    for fragment in FRAGMENTS:
        require(mapping[fragment.owner] == fragment.demo_owner, f"demo owner map drift at {va(fragment.owner)}")
        require(mapping[fragment.next_retail] == fragment.next_demo, f"next demo bracket drift at {va(fragment.owner)}")
        current = tuple(sorted(bodies[fragment.owner]))
        require(current == fragment.pre_ranges, f"PRE ranges drift at {va(fragment.owner)}: {current}")
        for start, end in current:
            require(end <= fragment.envelope_start or start >= fragment.repair_end, f"repair overlaps PRE at {va(fragment.owner)}")

        candidate = next(row for row in candidates if int(row["start"], 16) == fragment.envelope_start)
        require(int(candidate["functionJumpOwnerCount"]) == 1, "fragment owner count drift")
        require(candidate["functionJumpOwners"] == va(fragment.owner), "fragment owner identity drift")
        owner_refs = [
            row
            for row in refs
            if row["fromFunction"] == va(fragment.owner)
            and fragment.envelope_start <= int(row["to"], 16) < fragment.repair_end
            and row["type"] in {"CONDITIONAL_JUMP", "UNCONDITIONAL_JUMP", "COMPUTED_JUMP"}
        ]
        require(len(owner_refs) == fragment.owner_ref_count, f"owner edge count drift at {va(fragment.owner)}")
        calls_into_fragment = [
            row for row in refs
            if fragment.envelope_start <= int(row["to"], 16) < fragment.repair_end
            and "CALL" in row["type"]
        ]
        require(not calls_into_fragment, f"call-entry evidence appeared inside {fragment.name}")

        size = fragment.repair_end - fragment.envelope_start
        retail_bytes = retail.bytes_at(fragment.envelope_start, size)
        demo_bytes = demo.bytes_at(fragment.demo_start, size)
        retail_instructions = decode_exact(decoder, retail_bytes, fragment.envelope_start)
        demo_instructions = decode_exact(decoder, demo_bytes, fragment.demo_start)
        retail_identity = instruction_identity(retail_instructions)
        demo_identity = instruction_identity(demo_instructions)
        require(retail_identity == demo_identity, f"demo normalized mismatch at {va(fragment.owner)}")
        matches = unique_demo_match(
            decoder, retail_identity, demo, fragment.demo_owner, fragment.next_demo, size
        )
        require(matches == (fragment.demo_start,), f"demo match is not unique at {va(fragment.owner)}: {matches}")

        if fragment.owner == 0x00462640:
            padding = retail.bytes_at(fragment.repair_end, fragment.envelope_end - fragment.repair_end)
            require(padding == b"\x90" * 12, "FEP trailing alignment is not exact NOP padding")
            require(retail_instructions[-1].mnemonic == "ret", "FEP repair does not end at RET")

        loose_rows = [
            row for row in loose
            if fragment.envelope_start <= int(row["address"], 16) < fragment.envelope_end
        ]
        raw_diff = sum(a != b for a, b in zip(retail_bytes, demo_bytes))
        added_bytes += size
        manifest_rows.append(
            {
                "entry": va(fragment.owner),
                "current_name": fragment.name,
                "pre_body_ranges": canonical_ranges(fragment.pre_ranges),
                "repair_ranges": canonical_ranges((fragment.repair,)),
                "post_body_ranges": canonical_ranges(fragment.post_ranges),
                "repair_bytes": size,
                "repair_sha256": sha256_bytes(retail_bytes),
                "repair_instruction_count": len(retail_instructions),
                "repair_instruction_layout_sha256": instruction_layout_sha256(
                    retail_instructions, fragment.envelope_start
                ),
                "normalized_sha256": identity_sha256(retail_identity),
                "demo_entry": va(fragment.demo_owner),
                "demo_repair_ranges": canonical_ranges(((fragment.demo_start, fragment.demo_end),)),
                "demo_repair_sha256": sha256_bytes(demo_bytes),
                "demo_raw_diff_bytes": raw_diff,
                "owner_jump_rows": len(owner_refs),
                "loose_instruction_rows_pre": len(loose_rows),
                "runtime_grade": fragment.runtime_grade,
                "mutation_scope": "BODY_RANGE_AND_BOUNDED_DISASSEMBLY_ONLY",
            }
        )
        proof_rows.append(
            {
                "entry": va(fragment.owner),
                "name": fragment.name,
                "envelope": canonical_ranges(((fragment.envelope_start, fragment.envelope_end),)),
                "repair": canonical_ranges((fragment.repair,)),
                "post_ranges": canonical_ranges(fragment.post_ranges),
                "retail_instructions": len(retail_instructions),
                "demo_start": va(fragment.demo_start),
                "demo_instructions": len(demo_instructions),
                "unique_demo_matches": len(matches),
                "normalized_equal": "true",
                "owner_edges": len(owner_refs),
                "call_entries": 0,
            }
        )

    require(added_bytes == 1258, f"repair byte total drift: {added_bytes}")
    for retail_table, retail_targets, demo_table, demo_targets in TABLES:
        require(retail.dwords(retail_table, len(retail_targets)) == retail_targets, f"retail table drift at {va(retail_table)}")
        require(demo.dwords(demo_table, len(demo_targets)) == demo_targets, f"demo table drift at {va(demo_table)}")

    verify_runtime(
        args.runtime_parent,
        args.runtime_switch_base,
        args.runtime_switch_extension,
        args.runtime_range,
    )
    runtime_rows, coverage_counts = coverage_intersections(args.coverage_join, args.coverage_local_root)
    runtime_by_owner = {int(row["owner"], 16): row for row in runtime_rows}
    require(runtime_by_owner[0x0046FF10]["covered_bytes_union"] == 0, "CGame runtime limitation drift")
    require(runtime_by_owner[0x00559410]["covered_bytes_union"] == 0, "texture runtime limitation drift")
    require(runtime_by_owner[0x004BE420]["covered_bytes_union"] == 272, "explosion full runtime coverage drift")
    require(runtime_by_owner[0x00482590]["covered_bytes_union"] == 14, "HUD bounded runtime union drift")
    require(runtime_by_owner[0x00462640]["covered_bytes_union"] == 431, "FEP bounded runtime union drift")

    source = args.source_game.read_text(encoding="utf-8", errors="strict")
    require("void CGame::HandleEvent(CEvent* event)" in source, "source HandleEvent anchor missing")
    require("SOUND.SetGameSoundsMasterVolume(mHackCurrentGameMasterVolume)" in source, "source volume writer anchor missing")
    require("SOUND.UpdateVolumeForAllSoundEvents()" in source, "source volume update anchor missing")

    manifest_path = output / "fragment-manifest.tsv"
    proof_path = output / "static-proof.tsv"
    runtime_path = output / "runtime-coverage.tsv"
    write_tsv(manifest_path, manifest_rows)
    write_tsv(proof_path, proof_rows)
    write_tsv(runtime_path, runtime_rows)

    owned_after = owned_before + added_bytes
    receipt = {
        "schema": "bea.pc.function-body-fragment-proof.v1",
        "status": "READY_FOR_SCRATCH_ONLY",
        "policy": "LIVE_FORBIDDEN",
        "specimens": {
            "retail": {"bytes": len(retail_raw), "sha256": RETAIL_SHA256},
            "demo": {"bytes": len(demo_raw), "sha256": DEMO_SHA256},
        },
        "currentGhidra": {
            "functions": 8280,
            "ranges": 8400,
            "ownedBytes": owned_before,
            "db": "db.18613.gbf",
        },
        "repair": {
            "owners": 5,
            "addedBodyBytes": added_bytes,
            "postOwnedBytes": owned_after,
            "postOwnershipPercent": owned_after * 100.0 / 1929117,
            "postFunctionCount": 8280,
            "postBodyRangeCount": 8396,
            "namesSignaturesCommentsTagsAuthorized": False,
        },
        "exhaustiveness": {
            "mechanicalClass": "FUNCTION_FRAGMENT_CANDIDATE",
            "candidateRows": 5,
            "exactSet": [canonical_ranges(((item.envelope_start, item.envelope_end),)) for item in FRAGMENTS],
        },
        "demo": {"normalizedEqual": 5, "uniqueWithinMappedOwnerBracket": 5},
        "runtimeCoverage": coverage_counts,
        "source": {
            "commit": "5352a81cdb838b145a57f7febc5d9fc4b0129ebb",
            "anchor": "game.cpp:3035 CGame::HandleEvent",
            "role": "source-informed corroboration, not proof of retail identity",
        },
        "limitations": [
            "The 12 bytes at 0x00462B64..0x00462B70 are NOP alignment and are deliberately not added to CFEPMain__Process.",
            "No retained coverage range intersects the CGame tail or CDXTexture repair; their body ownership rests on static CFG plus unique normalized demo twins.",
            "CFEPMain runtime coverage is retained but its parent CALL_ENTRY wrapper was not READY; it is corroboration only.",
            "This proof assigns no new semantics and authorizes no live or tracked Ghidra mutation.",
        ],
        "inputs": {role: stamp(getattr(args, role)) for role in EXPECTED_INPUTS},
        "outputs": {
            "manifest": stamp(manifest_path),
            "staticProof": stamp(proof_path),
            "runtimeCoverage": stamp(runtime_path),
        },
    }
    write_json(output / "result.ready.json", receipt)
    print(
        "FUNCTION_FRAGMENT_PROOF_READY "
        f"owners=5 bytes={added_bytes} post_owned={owned_after} "
        f"demo_normalized=5 runtime_full=1"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
