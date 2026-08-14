#!/usr/bin/env python3
"""Verify the reviewed 31-row .text-gap boundary preparation package.

This is deliberately a read-only preparation verifier.  It joins the frozen
machine-local recovery evidence to the current tracked 8,170-row name
projection and exact 8,287-range body export, then verifies the tracked
half-open manifest byte-for-byte.  It neither creates Ghidra functions nor
writes any output.
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
from collections import Counter
from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence


ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFEST = (
    ROOT
    / "reverse-engineering"
    / "binary-analysis"
    / "text-gap-missing-function-boundaries-2026-08-13.tsv"
)


@dataclass(frozen=True)
class FilePin:
    size: int
    sha256: str


EVIDENCE_PINS: Mapping[str, FilePin] = {
    "analyze.py": FilePin(
        46_070,
        "3154cf5ac92ad4008f92414f68f299b6c8b1b31bcb90e23307aa4134ea983022",
    ),
    "artifact-manifest.sha256.tsv": FilePin(
        740,
        "b3c93237939952ace27fd2d9b2ab8b9742fd5926d5b47325671884456c1da98e",
    ),
    "callback-installs.tsv": FilePin(
        436,
        "8efbbdfa796850a9bf2c5eb37e131d59a1b2983aa7705309321489f56f66ba5d",
    ),
    "candidate-manifest.tsv": FilePin(
        11_919,
        "c3f05aa719f11f8b1a760c0d41450dde9c679a78bbbde82efee5fcb60dc3d024",
    ),
    "library-signatures.tsv": FilePin(
        1_559,
        "abbca75e76a16cab27b42639126967b4f156b53a2bf304808030e90159616c10",
    ),
    "range-classification.tsv": FilePin(
        4_567,
        "f0c94f13e5eca5cf27b26570637daa63c7fbde439ca736740b9d070183b0a4db",
    ),
    "REPORT.md": FilePin(
        5_595,
        "eebbd16faab1cfa81a9d51c54bab2afdfc43090db2987ebb80ab06f61641d645",
    ),
    "result.ready.json": FilePin(
        36_410,
        "a3df9d044754981e65eec7f16b0a5dab3b0275f6089a20958798e97873e19a11",
    ),
    "same-function-fragments.tsv": FilePin(
        8_555,
        "c79818dc722eade780227032bb99137de83df1d988e8f00a9af1410f14ec9330",
    ),
}

CURRENT_PROJECTION_PIN = FilePin(
    503_177,
    "d61f9866d9dbf67bae817a710d50a1a136b7c2156ec6eb7f862d82dea70f26fd",
)
MISSION_VOCABULARY_PIN = FilePin(
    3_417,
    "6154fb4bd4ae398b02d783fb50cd18381c1d224e2ac4c6f9dc1d26abb4d1ddc1",
)
BODY_RANGES_PIN = FilePin(
    1_183_469,
    "6703b759ac18528d61c4ad6f646f0fd6933eaf2a8892617f3ecc24b0ef8e0aae",
)
RETAIL_PIN = FilePin(
    2_506_752,
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750",
)
DEMO_PIN = FilePin(
    2_510_848,
    "d8637dd755b21c720c0cb8f71923f94d2a04a184d90f5343c2e868ce8606e5c2",
)
CRT_PIN = FilePin(
    809_504,
    "d72870f695fc49e1cb9f4fc3f45e202a7effa26474067b0e328ce31affd4a437",
)

EXPECTED_GAPS: tuple[tuple[int, int, int, int, int, str], ...] = (
    (
        0x00563C7A,
        0x00564486,
        14,
        2_054,
        6,
        "5040965744e37e2b78c0d8a905901d1cf00b9c2c90c63e074abe6b5ca5d35acb",
    ),
    (
        0x005B87B7,
        0x005B8CA0,
        12,
        1_018,
        239,
        "9ed7f13ef7ef76a190dc698989ea58629163e911eb3e48d734394f728d53ea62",
    ),
    (
        0x005B8E9E,
        0x005BB9B0,
        5,
        10_977,
        49,
        "c1017a4686ce1efec6a5e8dc1bf9e2f3a8e5e199fe5b5ac28a08c68e632420a4",
    ),
)

EXPECTED_CHECKS: Mapping[str, object] = {
    "alignment8BFFClassificationCrossCheckedAgainstSavedInventory": True,
    "allCandidateBodiesAbsentFromCurrentGhidraFunctions": True,
    "allCandidateBodySetsPairwiseDisjoint": True,
    "allCandidateCfgsReachApprovedTerminal": True,
    "allCandidateDemoTwinsNormalizedEqual": True,
    "allGapHashesExact": True,
    "allInputsHashPinned": True,
    "allNonBodyBytesAreKnownPadding": True,
    "allPaddingBytesRawEqualInDemo": True,
    "callbackImmediateEntries": 3,
    "callbackPropagatedReferences": 3,
    "crossCandidateFlowReferences": 0,
    "crtDispatchTargetsClassifiedAsFragments": 64,
    "crtReferenceCandidatesNormalizedEqual": 14,
    "crtReferenceCandidatesRawEqual": 12,
    "inGapDataOrTableBytes": 0,
}

EXPECTED_CURRENT_INVENTORY: Mapping[str, object] = {
    "candidateBodyIntersectionBytes": 0,
    "currentLooseBytesInPriorityGaps": 10_296,
    "looseBytesExactlyEqualCallbackBodies": True,
    "savedEntriesPrecededBy8BFF": 2,
    "savedEntriesStartingWith8BFF": 0,
    "savedGhidraBodyRanges": 8_287,
    "savedGhidraFunctions": 8_170,
}

DARK_QUESTION_BY_COHORT: Mapping[str, str] = {
    "CRT_REFERENCE_PACKAGE": "OPEN_ORIGINAL_RETAIL_SYMBOL_AND_RUNTIME_CONTRACT",
    "PACKED_MATH_QUEUE_A": "OPEN_EXACT_LIBRARY_PARTITION_SYMBOL_AND_RUNTIME_CONTRACT",
    "PACKED_MATH_QUEUE_B": "OPEN_EXACT_LIBRARY_PARTITION_SYMBOL_AND_RUNTIME_CONTRACT",
    "CALLBACK_QUEUE": "OPEN_CALLBACK_SELECTOR_ROLE_SEMANTIC_IDENTITY_AND_RUNTIME_CONTRACT",
}

MANIFEST_FIELDS: tuple[str, ...] = (
    "candidateId",
    "cohort",
    "retailEntry",
    "retailExtentEndExclusive",
    "retailBodyRangesHalfOpen",
    "extentBytes",
    "bodyBytes",
    "paddingBytesWithinExtent",
    "instructionCount",
    "bodyRangeSha256",
    "bodyBytesSha256",
    "demoEntry",
    "demoExtentEndExclusive",
    "demoDelta",
    "demoNormalizedEqual",
    "normalizedBodySha256",
    "currentProjectionState",
    "currentName",
    "semanticName",
    "darkQuestion",
    "admissionState",
)

RANGE_RE = re.compile(r"^0x([0-9A-Fa-f]{8})-0x([0-9A-Fa-f]{8})$")


class VerificationError(RuntimeError):
    """A bounded preparation invariant failed."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def file_facts(path: pathlib.Path) -> FilePin:
    data = path.read_bytes()
    return FilePin(len(data), hashlib.sha256(data).hexdigest())


def verify_pin(path: pathlib.Path, pin: FilePin, label: str) -> None:
    require(path.is_file(), f"missing {label}: {path}")
    actual = file_facts(path)
    require(
        actual == pin,
        f"{label} identity differs: expected {pin}, got {actual} at {path}",
    )


def read_tsv(path: pathlib.Path, *, comments: bool = False) -> list[dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    lines: Iterable[str] = text.splitlines()
    if comments:
        lines = (line for line in lines if line and not line.startswith("#"))
    reader = csv.DictReader(lines, delimiter="\t")
    require(reader.fieldnames is not None, f"missing TSV header: {path}")
    rows = [dict(row) for row in reader]
    require(all(None not in row for row in rows), f"extra TSV fields: {path}")
    return rows


def parse_hex(value: str, label: str) -> int:
    require(bool(re.fullmatch(r"0x[0-9A-Fa-f]{8}", value)), f"bad {label}: {value}")
    return int(value, 16)


def parse_ranges(value: str, label: str) -> list[tuple[int, int]]:
    require(bool(value), f"empty range set: {label}")
    result: list[tuple[int, int]] = []
    for item in value.split(";"):
        match = RANGE_RE.fullmatch(item)
        require(match is not None, f"bad half-open range in {label}: {item}")
        start, end = int(match.group(1), 16), int(match.group(2), 16)
        require(start < end, f"empty or reversed half-open range in {label}: {item}")
        if result:
            require(result[-1][1] < start, f"unordered/overlapping/adjacent range in {label}: {item}")
        result.append((start, end))
    return result


def canonical_ranges(ranges: Sequence[tuple[int, int]]) -> str:
    return ";".join(f"0x{start:08X}-0x{end:08X}" for start, end in ranges)


def body_range_sha256(ranges: Sequence[tuple[int, int]]) -> str:
    # Matches Ghidra's AddressRange min:maxInclusive; digest convention.
    payload = "".join(f"{start:08x}:{end - 1:08x};" for start, end in ranges)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def ranges_intersect(left: tuple[int, int], right: tuple[int, int]) -> bool:
    return left[0] < right[1] and right[0] < left[1]


class PeImage:
    """The tiny PE32 reader needed to hash named virtual ranges."""

    def __init__(self, path: pathlib.Path):
        self.path = path
        self.data = path.read_bytes()
        require(self.data[:2] == b"MZ", f"not an MZ image: {path}")
        pe_offset = struct.unpack_from("<I", self.data, 0x3C)[0]
        require(self.data[pe_offset : pe_offset + 4] == b"PE\0\0", f"not a PE image: {path}")
        coff = pe_offset + 4
        section_count = struct.unpack_from("<H", self.data, coff + 2)[0]
        optional_size = struct.unpack_from("<H", self.data, coff + 16)[0]
        optional = coff + 20
        require(struct.unpack_from("<H", self.data, optional)[0] == 0x10B, f"not PE32: {path}")
        self.image_base = struct.unpack_from("<I", self.data, optional + 28)[0]
        table = optional + optional_size
        self.sections: list[tuple[int, int, int, int]] = []
        for index in range(section_count):
            offset = table + index * 40
            virtual_size, rva, raw_size, raw_offset = struct.unpack_from(
                "<IIII", self.data, offset + 8
            )
            self.sections.append((rva, max(virtual_size, raw_size), raw_offset, raw_size))
        self.mapped_min_va = self.image_base + min(section[0] for section in self.sections)

    def read(self, va: int, size: int) -> bytes:
        require(size >= 0, f"negative PE read at 0x{va:08X}")
        rva = va - self.image_base
        for section_rva, section_span, raw_offset, raw_size in self.sections:
            if section_rva <= rva and rva + size <= section_rva + section_span:
                relative = rva - section_rva
                require(relative + size <= raw_size, f"virtual-only PE read at 0x{va:08X}")
                return self.data[raw_offset + relative : raw_offset + relative + size]
        raise VerificationError(f"unmapped PE read at 0x{va:08X} size={size}")

    def ranges_bytes(self, ranges: Sequence[tuple[int, int]]) -> bytes:
        return b"".join(self.read(start, end - start) for start, end in ranges)


def verify_evidence_seal(evidence_root: pathlib.Path) -> None:
    for name, pin in EVIDENCE_PINS.items():
        verify_pin(evidence_root / name, pin, f"frozen evidence {name}")

    manifest_rows = read_tsv(evidence_root / "artifact-manifest.sha256.tsv")
    expected_names = set(EVIDENCE_PINS) - {"artifact-manifest.sha256.tsv"}
    require({row["path"] for row in manifest_rows} == expected_names, "evidence artifact set differs")
    for row in manifest_rows:
        pin = EVIDENCE_PINS[row["path"]]
        require(int(row["bytes"]) == pin.size, f"artifact byte count differs: {row['path']}")
        require(row["sha256"] == pin.sha256, f"artifact digest differs: {row['path']}")


def verify_primary_result(
    evidence_root: pathlib.Path,
    retail: PeImage,
) -> tuple[list[dict[str, str]], dict[str, list[tuple[int, int]]]]:
    candidates = read_tsv(evidence_root / "candidate-manifest.tsv")
    result = json.loads((evidence_root / "result.ready.json").read_text(encoding="utf-8"))

    require(result["schemaVersion"] == "bea.re.text-missing-function-recovery.v1", "schema differs")
    require(result["status"] == "READY", "frozen recovery is not READY")
    require(result["checks"] == EXPECTED_CHECKS, "frozen recovery check set differs")
    require(result["currentInventory"] == EXPECTED_CURRENT_INVENTORY, "frozen inventory facts differ")
    require(
        result["lowerBound"]
        == {
            "additionalFirstGapEntries": 14,
            "inventoryArithmetic": "8170 + 31 = 8201",
            "isFinalCeiling": False,
            "minimumRetailFunctionEntries": 8201,
            "newCandidateEntries": 31,
            "provisionalArithmetic": "12 + 5 = 17",
            "provisionalSeventeenReproduced": True,
        },
        "lower-bound arithmetic differs",
    )
    require(len(candidates) == len(result["candidates"]) == 31, "candidate count differs")
    require(
        [row["candidateId"] for row in candidates]
        == [f"CF-{index:03d}" for index in range(1, 32)],
        "candidate IDs/order differ",
    )
    require(
        Counter(row["cohort"] for row in candidates)
        == Counter(
            {
                "CRT_REFERENCE_PACKAGE": 14,
                "PACKED_MATH_QUEUE_A": 12,
                "PACKED_MATH_QUEUE_B": 2,
                "CALLBACK_QUEUE": 3,
            }
        ),
        "candidate cohort counts differ",
    )

    ranges_by_id: dict[str, list[tuple[int, int]]] = {}
    all_ranges: list[tuple[int, int, str]] = []
    body_total = 0
    padding_total = 0
    for row in candidates:
        candidate_id = row["candidateId"]
        require(row["cohort"] in DARK_QUESTION_BY_COHORT, f"unknown cohort: {candidate_id}")
        require(row["semanticName"] == "UNASSIGNED", f"semantic name leaked: {candidate_id}")
        require(row["demoNormalizedEqual"] == "true", f"demo twin differs: {candidate_id}")
        entry = parse_hex(row["retailEntry"], f"{candidate_id} entry")
        extent_end = parse_hex(row["retailExtentEndExclusive"], f"{candidate_id} extent end")
        ranges = parse_ranges(row["retailBodyRanges"], f"{candidate_id} body")
        require(entry == ranges[0][0], f"entry is not first body byte: {candidate_id}")
        require(all(entry <= start < end <= extent_end for start, end in ranges), f"body escapes extent: {candidate_id}")
        extent_bytes = extent_end - entry
        body_bytes = sum(end - start for start, end in ranges)
        padding_bytes = int(row["paddingBytesWithinExtent"])
        require(extent_bytes == int(row["extentBytes"]), f"extent bytes differ: {candidate_id}")
        require(body_bytes == int(row["bodyBytes"]), f"body bytes differ: {candidate_id}")
        require(body_bytes + padding_bytes == extent_bytes, f"extent does not tile: {candidate_id}")
        actual_body_hash = hashlib.sha256(retail.ranges_bytes(ranges)).hexdigest()
        require(actual_body_hash == row["retailBodySha256"], f"retail body hash differs: {candidate_id}")
        ranges_by_id[candidate_id] = ranges
        all_ranges.extend((start, end, candidate_id) for start, end in ranges)
        body_total += body_bytes
        padding_total += padding_bytes

    ordered_ranges = sorted(all_ranges)
    for left, right in zip(ordered_ranges, ordered_ranges[1:]):
        require(left[1] <= right[0], f"candidate bodies overlap: {left[2]} / {right[2]}")
    require(body_total == 14_049, f"body total differs: {body_total}")
    require(padding_total == 45, f"in-candidate padding total differs: {padding_total}")

    classification = read_tsv(evidence_root / "range-classification.tsv")
    class_ranges: list[tuple[int, int, str, str]] = []
    callable_by_id: dict[str, list[tuple[int, int]]] = {}
    for row in classification:
        start = parse_hex(row["retailStart"], "classification start")
        end = parse_hex(row["retailEndExclusive"], "classification end")
        require(end - start == int(row["bytes"]), "classification byte count differs")
        kind = row["classification"]
        require(kind in {"CALLABLE_BODY", "PADDING"}, f"unexpected classification: {kind}")
        owner = row["ownerCandidate"]
        if kind == "CALLABLE_BODY":
            require(owner in ranges_by_id, f"unknown callable owner: {owner}")
            callable_by_id.setdefault(owner, []).append((start, end))
        else:
            require(not owner, "padding row has an owner")
        class_ranges.append((start, end, kind, owner))
    require(callable_by_id == ranges_by_id, "classification/body range sets differ")

    cursor_index = 0
    for gap_start, gap_end, count, body_bytes, padding_bytes, gap_sha in EXPECTED_GAPS:
        rows: list[tuple[int, int, str, str]] = []
        cursor = gap_start
        while cursor_index < len(class_ranges) and class_ranges[cursor_index][0] < gap_end:
            item = class_ranges[cursor_index]
            require(item[0] == cursor and item[1] <= gap_end, "classification does not tile a gap")
            rows.append(item)
            cursor = item[1]
            cursor_index += 1
        require(cursor == gap_end, f"classification leaves gap bytes at 0x{cursor:08X}")
        owners = {owner for _, _, kind, owner in rows if kind == "CALLABLE_BODY"}
        actual_body = sum(end - start for start, end, kind, _ in rows if kind == "CALLABLE_BODY")
        actual_padding = sum(end - start for start, end, kind, _ in rows if kind == "PADDING")
        require(len(owners) == count, f"candidate count differs in gap 0x{gap_start:08X}")
        require((actual_body, actual_padding) == (body_bytes, padding_bytes), f"gap accounting differs at 0x{gap_start:08X}")
        require(
            hashlib.sha256(retail.read(gap_start, gap_end - gap_start)).hexdigest() == gap_sha,
            f"gap hash differs at 0x{gap_start:08X}",
        )
    require(cursor_index == len(class_ranges), "classification has out-of-gap rows")
    require(sum(item[4] for item in EXPECTED_GAPS) == 294, "padding total differs")

    fragments = read_tsv(evidence_root / "same-function-fragments.tsv")
    dispatch = [row for row in fragments if row["candidateId"] == "CF-002"]
    require(len(dispatch) == 64, "CF-002 dispatcher target count differs")
    require(len({row["retailTarget"] for row in dispatch}) == 64, "CF-002 dispatcher targets repeat")
    require(all(row["classification"] == "SAME_FUNCTION_FRAGMENT" for row in dispatch), "dispatcher classification differs")

    callbacks = read_tsv(evidence_root / "callback-installs.tsv")
    require(
        [(row["selector"], row["candidateId"], row["classification"]) for row in callbacks]
        == [
            ("0", "CF-031", "CALLBACK_ENTRY_INSTALL"),
            ("1", "CF-030", "CALLBACK_ENTRY_INSTALL"),
            ("2", "CF-029", "CALLBACK_ENTRY_INSTALL"),
        ],
        "callback installation rows differ",
    )

    preceded_8bff = [
        row
        for row in candidates
        if parse_hex(row["retailEntry"], "candidate entry") % 16 == 0
        and retail.read(parse_hex(row["retailEntry"], "candidate entry") - 2, 2) == b"\x8b\xff"
    ]
    require(len(preceded_8bff) == 7, "candidate 8B FF padding convention differs")
    return candidates, ranges_by_id


def verify_current_projection(
    projection_path: pathlib.Path,
    mission_vocabulary_path: pathlib.Path,
    body_ranges_path: pathlib.Path,
    candidates: Sequence[dict[str, str]],
    candidate_ranges: Mapping[str, Sequence[tuple[int, int]]],
    retail: PeImage,
) -> None:
    verify_pin(projection_path, CURRENT_PROJECTION_PIN, "current 8,170-row name projection")
    verify_pin(mission_vocabulary_path, MISSION_VOCABULARY_PIN, "34-row Mission vocabulary")
    verify_pin(body_ranges_path, BODY_RANGES_PIN, "current exact body-range export")

    projection = read_tsv(projection_path, comments=True)
    require(len(projection) == 8_170, f"current projection count differs: {len(projection)}")
    by_address = {parse_hex(row["address"], "projection address"): row for row in projection}
    require(len(by_address) == len(projection), "duplicate current projection address")

    mission = read_tsv(mission_vocabulary_path, comments=True)
    require(len(mission) == 34, f"Mission vocabulary count differs: {len(mission)}")
    for row in mission:
        address = parse_hex(row["handlerVa"], "Mission handler")
        require(address in by_address, f"Mission handler absent from projection: {row['handlerVa']}")
        require(
            by_address[address]["name"] == row["proposedName"],
            f"Mission current name differs at {row['handlerVa']}",
        )

    entries = [parse_hex(row["retailEntry"], "candidate entry") for row in candidates]
    collisions = [entry for entry in entries if entry in by_address]
    if collisions:
        raise VerificationError(
            f"candidate already has current function/name: 0x{collisions[0]:08X}"
        )

    exact_rows = read_tsv(body_ranges_path, comments=True)
    require(len(exact_rows) == 8_287, f"current exact range count differs: {len(exact_rows)}")
    function_entries = {parse_hex(row["functionAddress"], "body-range owner") for row in exact_rows}
    require(len(function_entries) == 8_170, f"current exact function count differs: {len(function_entries)}")
    exact_ranges = [
        (
            parse_hex(row["rangeMin"], "current range minimum"),
            parse_hex(row["rangeEndExclusive"], "current range end"),
        )
        for row in exact_rows
    ]
    for candidate_id, ranges in candidate_ranges.items():
        for candidate_range in ranges:
            require(
                not any(ranges_intersect(candidate_range, current_range) for current_range in exact_ranges),
                f"current exact body overlaps {candidate_id} at 0x{candidate_range[0]:08X}",
            )

    saved_starts = [entry for entry in function_entries if retail.read(entry, 2) == b"\x8b\xff"]
    saved_preceded = [
        entry
        for entry in function_entries
        if entry >= retail.mapped_min_va + 2 and retail.read(entry - 2, 2) == b"\x8b\xff"
    ]
    require(not saved_starts, "a current saved function begins on 8B FF")
    require(len(saved_preceded) == 2, "current saved 8B FF predecessor count differs")


def render_manifest(candidates: Sequence[dict[str, str]]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=MANIFEST_FIELDS, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    for row in candidates:
        ranges = parse_ranges(row["retailBodyRanges"], f"{row['candidateId']} body")
        writer.writerow(
            {
                "candidateId": row["candidateId"],
                "cohort": row["cohort"],
                "retailEntry": row["retailEntry"],
                "retailExtentEndExclusive": row["retailExtentEndExclusive"],
                "retailBodyRangesHalfOpen": canonical_ranges(ranges),
                "extentBytes": row["extentBytes"],
                "bodyBytes": row["bodyBytes"],
                "paddingBytesWithinExtent": row["paddingBytesWithinExtent"],
                "instructionCount": row["instructionCount"],
                "bodyRangeSha256": body_range_sha256(ranges),
                "bodyBytesSha256": row["retailBodySha256"],
                "demoEntry": row["demoEntry"],
                "demoExtentEndExclusive": row["demoExtentEndExclusive"],
                "demoDelta": row["demoDelta"],
                "demoNormalizedEqual": row["demoNormalizedEqual"],
                "normalizedBodySha256": row["normalizedBodySha256"],
                "currentProjectionState": "ABSENT_FROM_CURRENT_8170_FUNCTION_CENSUS",
                "currentName": "NO_CURRENT_FUNCTION",
                "semanticName": "UNASSIGNED",
                "darkQuestion": DARK_QUESTION_BY_COHORT[row["cohort"]],
                "admissionState": "PREPARATION_ONLY_NOT_ADMITTED",
            }
        )
    return output.getvalue().encode("utf-8")


def verify_manifest(path: pathlib.Path, expected: bytes) -> None:
    require(path.is_file(), f"missing tracked boundary manifest: {path}")
    actual = path.read_bytes()
    require(actual == expected, f"tracked boundary manifest differs byte-for-byte: {path}")


def verify(args: argparse.Namespace) -> dict[str, object]:
    evidence_root = args.evidence_root.resolve()
    verify_evidence_seal(evidence_root)
    verify_pin(args.retail.resolve(), RETAIL_PIN, "pristine retail specimen")
    verify_pin(args.demo.resolve(), DEMO_PIN, "PC demo specimen")
    verify_pin(args.crt_reference.resolve(), CRT_PIN, "32-bit CRT reference")
    retail = PeImage(args.retail.resolve())
    candidates, ranges_by_id = verify_primary_result(evidence_root, retail)
    verify_current_projection(
        args.current_projection.resolve(),
        args.mission_vocabulary.resolve(),
        args.body_ranges.resolve(),
        candidates,
        ranges_by_id,
        retail,
    )
    expected_manifest = render_manifest(candidates)
    verify_manifest(args.manifest.resolve(), expected_manifest)
    return {
        "bodyBytes": 14_049,
        "candidateFunctions": 31,
        "currentFunctionRows": 8_170,
        "currentOverlapBytes": 0,
        "demoNormalizedTwins": 31,
        "manifestBytes": len(expected_manifest),
        "manifestSha256": hashlib.sha256(expected_manifest).hexdigest(),
        "minimumRetailFunctionEntriesIfAdmitted": 8_201,
        "paddingBytes": 294,
        "status": "READY_FOR_SCRATCH_ADMISSION_REVIEW_ONLY",
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-root", type=pathlib.Path, required=True)
    parser.add_argument("--retail", type=pathlib.Path, required=True)
    parser.add_argument("--demo", type=pathlib.Path, required=True)
    parser.add_argument("--crt-reference", type=pathlib.Path, required=True)
    parser.add_argument("--body-ranges", type=pathlib.Path, required=True)
    parser.add_argument(
        "--current-projection",
        type=pathlib.Path,
        default=ROOT / "reverse-engineering" / "binary-analysis" / "ghidra-function-name-table-2026-08-13.tsv",
    )
    parser.add_argument(
        "--mission-vocabulary",
        type=pathlib.Path,
        default=ROOT
        / "reverse-engineering"
        / "binary-analysis"
        / "mission-script-registry-new-function-vocabulary-normalization-2026-08-13.tsv",
    )
    parser.add_argument("--manifest", type=pathlib.Path, default=MANIFEST)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    try:
        summary = verify(build_parser().parse_args(argv))
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError, VerificationError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
