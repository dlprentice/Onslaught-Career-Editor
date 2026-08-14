#!/usr/bin/env python3
"""Focused fail-closed tests for re_text_gap_boundary_prep.py."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import io
import pathlib
import sys
import tempfile
import unittest
from unittest import mock


TOOL = pathlib.Path(__file__).with_name("re_text_gap_boundary_prep.py")
SPEC = importlib.util.spec_from_file_location("re_text_gap_boundary_prep", TOOL)
assert SPEC is not None and SPEC.loader is not None
prep = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = prep
SPEC.loader.exec_module(prep)


def write_tsv(path: pathlib.Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    path.write_text(output.getvalue(), encoding="utf-8", newline="")


def pin(path: pathlib.Path) -> prep.FilePin:
    data = path.read_bytes()
    return prep.FilePin(len(data), hashlib.sha256(data).hexdigest())


class FakeRetail:
    image_base = 0x00400000
    mapped_min_va = 0x00401000

    def __init__(self, starts_with_8bff: set[int] | None = None):
        self.starts_with_8bff = starts_with_8bff or set()

    def read(self, address: int, size: int) -> bytes:
        if size == 2 and address in self.starts_with_8bff:
            return b"\x8b\xff"
        return b"\x90" * size


class RangeAndManifestTests(unittest.TestCase):
    def test_half_open_parser_rejects_empty_overlap_and_unmerged_adjacency(self) -> None:
        for value in (
            "0x00500000-0x00500000",
            "0x00500010-0x00500000",
            "0x00500000-0x00500010;0x00500008-0x00500020",
            "0x00500000-0x00500010;0x00500010-0x00500020",
            "00500000-00500010",
        ):
            with self.subTest(value=value):
                with self.assertRaises(prep.VerificationError):
                    prep.parse_ranges(value, "adverse")

    def test_range_digest_matches_ghidra_min_max_inclusive_convention(self) -> None:
        ranges = [(0x00500000, 0x00500002), (0x00500010, 0x00500011)]
        expected = hashlib.sha256(b"00500000:00500001;00500010:00500010;").hexdigest()
        self.assertEqual(prep.body_range_sha256(ranges), expected)

    def test_manifest_keeps_current_name_semantic_name_and_dark_question_separate(self) -> None:
        row = {
            "candidateId": "CF-001",
            "cohort": "CRT_REFERENCE_PACKAGE",
            "retailEntry": "0x00500000",
            "retailExtentEndExclusive": "0x00500004",
            "retailBodyRanges": "0x00500000-0x00500002;0x00500003-0x00500004",
            "extentBytes": "4",
            "bodyBytes": "3",
            "paddingBytesWithinExtent": "1",
            "instructionCount": "2",
            "retailBodySha256": "a" * 64,
            "demoEntry": "0x00500700",
            "demoExtentEndExclusive": "0x00500704",
            "demoDelta": "+0x700",
            "demoNormalizedEqual": "true",
            "normalizedBodySha256": "b" * 64,
        }
        rendered = prep.render_manifest([row]).decode("utf-8")
        parsed = list(csv.DictReader(rendered.splitlines(), delimiter="\t"))[0]
        self.assertEqual(parsed["currentName"], "NO_CURRENT_FUNCTION")
        self.assertEqual(parsed["semanticName"], "UNASSIGNED")
        self.assertEqual(
            parsed["darkQuestion"],
            "OPEN_ORIGINAL_RETAIL_SYMBOL_AND_RUNTIME_CONTRACT",
        )
        self.assertEqual(parsed["admissionState"], "PREPARATION_ONLY_NOT_ADMITTED")
        self.assertEqual(
            parsed["retailBodyRangesHalfOpen"],
            "0x00500000-0x00500002;0x00500003-0x00500004",
        )

    def test_manifest_verification_is_byte_exact(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = pathlib.Path(temporary) / "manifest.tsv"
            path.write_bytes(b"a\tb\n1\t2\n")
            prep.verify_manifest(path, b"a\tb\n1\t2\n")
            with self.assertRaises(prep.VerificationError):
                prep.verify_manifest(path, b"a\tb\n1\t3\n")


class CurrentProjectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        root = pathlib.Path(self.temporary.name)
        self.projection = root / "projection.tsv"
        self.mission = root / "mission.tsv"
        self.body = root / "body.tsv"
        self.projection_rows = [
            {
                "address": f"0x{0x00401000 + index * 4:08X}",
                "name": f"Current_{index:04d}",
                "bodyMin": f"0x{0x00401000 + index * 4:08X}",
                "bodyMax": f"0x{0x00401000 + index * 4:08X}",
            }
            for index in range(8_170)
        ]
        self.mission_rows = [
            {
                "index": str(index),
                "command": f"Command{index}",
                "handlerVa": self.projection_rows[index]["address"],
                "registryRecordVa": f"0x{0x00600000 + index * 4:08X}",
                "cohort": "MISSION_SCRIPT_REGISTRY_MISSING_FUNCTION",
                "expectedPreName": f"FUN_{index:08x}",
                "proposedName": self.projection_rows[index]["name"],
                "expectedNameSource": "USER_DEFINED",
            }
            for index in range(34)
        ]
        self.body_rows: list[dict[str, str]] = []
        ordinal = 0
        for index, projection_row in enumerate(self.projection_rows):
            address = int(projection_row["address"], 16)
            self.body_rows.append(
                {
                    "functionAddress": projection_row["address"],
                    "functionName": projection_row["name"],
                    "rangeOrdinal": "0",
                    "rangeMin": f"0x{address:08X}",
                    "rangeMax": f"0x{address:08X}",
                    "rangeEndExclusive": f"0x{address + 1:08X}",
                    "rangeBytes": "1",
                    "rangeSha256": f"{ordinal:064x}",
                }
            )
            ordinal += 1
            if index < 117:
                self.body_rows.append(
                    {
                        "functionAddress": projection_row["address"],
                        "functionName": projection_row["name"],
                        "rangeOrdinal": "1",
                        "rangeMin": f"0x{address + 2:08X}",
                        "rangeMax": f"0x{address + 2:08X}",
                        "rangeEndExclusive": f"0x{address + 3:08X}",
                        "rangeBytes": "1",
                        "rangeSha256": f"{ordinal:064x}",
                    }
                )
                ordinal += 1
        self._write_all()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _write_all(self) -> None:
        write_tsv(
            self.projection,
            ["address", "name", "bodyMin", "bodyMax"],
            self.projection_rows,
        )
        write_tsv(
            self.mission,
            [
                "index",
                "command",
                "handlerVa",
                "registryRecordVa",
                "cohort",
                "expectedPreName",
                "proposedName",
                "expectedNameSource",
            ],
            self.mission_rows,
        )
        write_tsv(
            self.body,
            [
                "functionAddress",
                "functionName",
                "rangeOrdinal",
                "rangeMin",
                "rangeMax",
                "rangeEndExclusive",
                "rangeBytes",
                "rangeSha256",
            ],
            self.body_rows,
        )

    def _verify(
        self,
        *,
        candidate_entry: str = "0x00500000",
        candidate_range: tuple[int, int] = (0x00500000, 0x00500010),
        retail: FakeRetail | None = None,
    ) -> None:
        candidates = [{"retailEntry": candidate_entry}]
        ranges = {"CF-001": [candidate_range]}
        if retail is None:
            retail = FakeRetail(
                {
                    int(self.projection_rows[1]["address"], 16) - 2,
                    int(self.projection_rows[2]["address"], 16) - 2,
                }
            )
        with (
            mock.patch.object(prep, "CURRENT_PROJECTION_PIN", pin(self.projection)),
            mock.patch.object(prep, "MISSION_VOCABULARY_PIN", pin(self.mission)),
            mock.patch.object(prep, "BODY_RANGES_PIN", pin(self.body)),
        ):
            prep.verify_current_projection(
                self.projection,
                self.mission,
                self.body,
                candidates,
                ranges,
                retail,
            )

    def test_current_projection_join_passes_with_absent_candidate(self) -> None:
        self._verify()

    def test_candidate_entry_collision_fails_closed(self) -> None:
        with self.assertRaisesRegex(prep.VerificationError, "already has current function"):
            self._verify(candidate_entry=self.projection_rows[0]["address"])

    def test_candidate_body_overlap_fails_closed(self) -> None:
        address = int(self.projection_rows[100]["address"], 16)
        with self.assertRaisesRegex(prep.VerificationError, "current exact body overlaps"):
            self._verify(candidate_range=(address, address + 1))

    def test_mission_name_mismatch_fails_closed_even_when_file_is_re_pinned(self) -> None:
        self.mission_rows[0]["proposedName"] = "WrongCurrentName"
        self._write_all()
        with self.assertRaisesRegex(prep.VerificationError, "Mission current name differs"):
            self._verify()

    def test_stale_projection_bytes_fail_before_semantic_join(self) -> None:
        original_pin = pin(self.projection)
        with self.projection.open("a", encoding="utf-8", newline="") as stream:
            stream.write("# drift\n")
        with (
            mock.patch.object(prep, "CURRENT_PROJECTION_PIN", original_pin),
            mock.patch.object(prep, "MISSION_VOCABULARY_PIN", pin(self.mission)),
            mock.patch.object(prep, "BODY_RANGES_PIN", pin(self.body)),
        ):
            with self.assertRaisesRegex(prep.VerificationError, "projection.*identity differs"):
                prep.verify_current_projection(
                    self.projection,
                    self.mission,
                    self.body,
                    [{"retailEntry": "0x00500000"}],
                    {"CF-001": [(0x00500000, 0x00500010)]},
                    FakeRetail(),
                )

    def test_saved_function_starting_on_8bff_fails_closed(self) -> None:
        bad = int(self.projection_rows[10]["address"], 16)
        with self.assertRaisesRegex(prep.VerificationError, "begins on 8B FF"):
            self._verify(retail=FakeRetail({bad}))


class EvidenceSealTests(unittest.TestCase):
    def test_sealed_artifact_drift_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            payload = root / "payload.tsv"
            payload.write_bytes(b"pinned\n")
            payload_pin = pin(payload)
            artifact = root / "artifact-manifest.sha256.tsv"
            write_tsv(
                artifact,
                ["path", "bytes", "sha256"],
                [
                    {
                        "path": "payload.tsv",
                        "bytes": str(payload_pin.size),
                        "sha256": payload_pin.sha256,
                    }
                ],
            )
            evidence_pins = {
                "artifact-manifest.sha256.tsv": pin(artifact),
                "payload.tsv": payload_pin,
            }
            with mock.patch.object(prep, "EVIDENCE_PINS", evidence_pins):
                prep.verify_evidence_seal(root)
                payload.write_bytes(b"drifted\n")
                with self.assertRaisesRegex(prep.VerificationError, "payload.tsv identity differs"):
                    prep.verify_evidence_seal(root)


if __name__ == "__main__":
    unittest.main(verbosity=2)
