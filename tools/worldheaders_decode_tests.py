#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Authored level-header metadata controls; no game assets or runtime."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import worldheaders_decode as headers
from battle_engine_config_decode_tests import _record as config_record


def fixture(*records: tuple[int, list[str], tuple[int, int, int, int]]) -> bytes:
    rows = []
    for world, configs, raw in records:
        payload = struct.pack("<ii", world, len(configs))
        payload += b"".join(bytes([len(name)]) + name.encode("ascii") for name in configs)
        payload += struct.pack("<4i", *raw)
        rows.append(struct.pack("<ii", 3, len(payload)) + payload)
    return struct.pack("<ii", 1, len(rows)) + b"".join(rows)


def configs(*names: str) -> bytes:
    if len(names) != 6:
        raise ValueError("existing authored configuration profile requires six records")
    return struct.pack("<i", 6) + b"".join(config_record(i, name.encode("ascii")) for i, name in enumerate(names))


class LevelMetadataTests(unittest.TestCase):
    def test_round_trip_source_and_original_record_coordinates_are_exact(self) -> None:
        data = fixture((100, ["Standard"], (1, -2, 0x12345678, 0)), (852, ["Racer", "Laser"], (0, 1, -1, 2)))
        report = headers.project_level_metadata(data)
        self.assertEqual("projected", report["status"])
        self.assertEqual("byte-exact", report["roundTrip"])
        self.assertEqual(hashlib.sha256(data).hexdigest(), report["source"]["sha256"])
        self.assertEqual(len(data), report["source"]["bytes"])
        rows = report["records"]
        self.assertEqual([0, 1], [row["ordinal"] for row in rows])
        self.assertEqual(8, rows[0]["offset"])
        self.assertEqual(rows[0]["endOffset"], rows[1]["offset"])
        self.assertEqual(len(data), rows[-1]["endOffset"])
        self.assertNotEqual(0, rows[1]["offset"] % 4)  # no invented four-byte alignment
        for row in rows:
            self.assertEqual(hashlib.sha256(data[row["offset"]:row["endOffset"]]).hexdigest(), row["recordSha256"])
        self.assertEqual(dict(field_a=1, field_b=-2, field_c=0x12345678, field_d=0), rows[0]["rawTrailing"])
        self.assertEqual(["field_a", "field_b", "field_c"], rows[0]["uninterpretedFields"])
        self.assertEqual(report, headers.project_level_metadata(data))

    def test_stored_world_mode_and_numeric_game_predicate_are_independent(self) -> None:
        data = fixture((100, [], (0, 0, 0, 1)), (852, [], (0, 0, 0, 0)), (888, [], (0, 0, 0, 2)),
                       (899, [], (0, 0, 0, 1)), (900, [], (0, 0, 0, 1)), (849, [], (0, 0, 0, -37)))
        rows = headers.project_level_metadata(data)["records"]
        self.assertEqual(["cooperative-multiplayer", "single-player", "versus-multiplayer", "cooperative-multiplayer",
                          "cooperative-multiplayer", None], [r["worldMode"]["name"] for r in rows])
        self.assertEqual([False, True, True, True, False, False], [r["retailGameMultiplayerLevelPredicate"] for r in rows])
        self.assertEqual([False, False, True, True, False, None], [r["modeAndLevelPredicateAgreement"] for r in rows])
        self.assertEqual(-37, rows[-1]["worldMode"]["raw"])
        self.assertEqual("unknown-enum-value", rows[-1]["worldMode"]["status"])
        self.assertTrue(all("not established" in r["ceNetworkAdmission"] for r in rows))
        self.assertTrue(all(r["missionScript"] == {"status": "not-in-this-input", "path": None} for r in rows))
        first = headers.project_level_metadata(fixture((850, [], (0, 0, 0, 1))))["records"][0]
        self.assertTrue(first["retailGameMultiplayerLevelPredicate"])

    def test_same_world_and_configuration_names_keep_all_occurrences(self) -> None:
        data = fixture((852, ["Standard", "Standard"], (1, 0, 0, 2)), (852, ["Standard"], (0, 0, 0, 2)))
        report = headers.project_level_metadata(data)
        self.assertEqual([852], report["duplicateWorldIds"])
        first, second = report["records"]
        self.assertEqual((2, 2), (first["worldIdMultiplicity"], second["worldIdMultiplicity"]))
        self.assertNotEqual(first["occurrenceId"], second["occurrenceId"])
        self.assertEqual([2, 2], [c["localNameMultiplicity"] for c in first["configurations"]])
        self.assertNotEqual(first["configurations"][0]["occurrenceId"], first["configurations"][1]["occurrenceId"])
        self.assertEqual(["not-checked"] * 2, [c["resolution"] for c in first["configurations"]])

    def test_configuration_join_is_exact_case_sensitive_and_never_falls_back(self) -> None:
        configuration = configs("Standard", "Racer", "Laser", "Blaster", "Prototype", "Sniper")
        data = fixture((852, ["Standard", "standard", " Standard", "Unknown"], (0, 0, 0, 2)))
        report = headers.project_level_metadata(data, configuration_data=configuration)
        rows = report["records"][0]["configurations"]
        self.assertEqual(["unique-name-match", "missing", "missing", "missing"], [r["resolution"] for r in rows])
        self.assertEqual([1, 0, 0, 0], [len(r["candidateOccurrenceIds"]) for r in rows])
        self.assertEqual(hashlib.sha256(configuration).hexdigest(), report["configurationInput"]["source"]["sha256"])

    def test_duplicate_registry_names_are_ambiguous_with_every_candidate_preserved(self) -> None:
        configuration = configs("Same", "Other", "Same", "Third", "Fourth", "Fifth")
        data = fixture((852, ["Same"], (0, 0, 0, 2)))
        report = headers.project_level_metadata(data, configuration_data=configuration)
        row = report["records"][0]["configurations"][0]
        self.assertEqual("ambiguous", row["resolution"])
        self.assertEqual(2, len(set(row["candidateOccurrenceIds"])))
        self.assertEqual(6, len(report["configurationInput"]["records"]))

    def test_unsupported_configuration_input_does_not_discard_valid_world_rows(self) -> None:
        data = fixture((100, ["Standard"], (0, 0, 0, 0)))
        report = headers.project_level_metadata(data, configuration_data=b"unsupported authored configuration")
        self.assertEqual("projected", report["status"])
        self.assertEqual("unparsed", report["configurationInput"]["status"])
        self.assertEqual("unparsed-configuration-input", report["records"][0]["configurations"][0]["resolution"])

    def test_native_signed_length_empty_and_embedded_nul_names_are_unresolved(self) -> None:
        data = fixture((100, ["", "A\0B", "X" * 128], (0, 0, 0, 0)))
        report = headers.project_level_metadata(data)
        rows = report["records"][0]["configurations"]
        self.assertEqual(["", "A\0B", "X" * 128], [r["name"] for r in rows])
        self.assertTrue(all(r["resolution"] == "unresolved-native-name" for r in rows))

    def test_different_payload_and_source_path_change_occurrence_identity(self) -> None:
        data = fixture((100, ["Standard"], (0, 0, 0, 0)))
        original = headers.project_level_metadata(data)
        path = headers.project_level_metadata(data, source_path="alternate/worldheaders.dat")
        changed = headers.project_level_metadata(fixture((100, ["Standard"], (1, 0, 0, 0))))
        self.assertEqual(original["records"][0]["recordSha256"], path["records"][0]["recordSha256"])
        self.assertEqual(3, len({r["records"][0]["occurrenceId"] for r in (original, path, changed)}))
        self.assertNotEqual(original["source"]["sha256"], changed["source"]["sha256"])

    def test_untrusted_source_coordinates_and_mutable_input_are_rejected(self) -> None:
        for path in ("/home/player/secret.dat", "C:/file.dat", "a\\b", "a/../b", "a//b", "./b", "a\0b"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                headers.project_level_metadata(fixture(), source_path=path)
        with self.assertRaisesRegex(ValueError, "immutable"):
            headers.project_level_metadata(bytearray(fixture()))

    def test_malformed_bytes_retain_full_source_hash_with_no_interpreted_rows(self) -> None:
        valid = fixture((100, ["Standard"], (0, 0, 0, 0)))
        cases = [b"", valid[:-1], valid + b"unframed", struct.pack("<ii", 1, -1)]
        wrong_size = bytearray(valid);struct.pack_into("<i", wrong_size, 12, 999)
        bad_ascii = bytearray(valid);bad_ascii[25] = 0xff
        cases.extend([bytes(wrong_size), bytes(bad_ascii)])
        for data in cases:
            with self.subTest(data=data[:16]):
                report = headers.project_level_metadata(data)
                self.assertEqual("unparsed", report["status"])
                self.assertEqual([], report["records"])
                self.assertEqual(hashlib.sha256(data).hexdigest(), report["source"]["sha256"])

    def test_future_versions_and_profile_limits_are_not_silently_interpreted(self) -> None:
        original = fixture((100, [], (0, 0, 0, 0)))
        for off in (0, 8):
            data = bytearray(original);struct.pack_into("<i", data, off, 4)
            report = headers.project_level_metadata(bytes(data))
            self.assertEqual("unsupported", report["status"])
            self.assertEqual([], report["records"])
        with patch.object(headers, "MAX_METADATA_BYTES", len(original) - 1):
            self.assertEqual("unparsed", headers.project_level_metadata(original)["status"])
        with patch.object(headers, "MAX_METADATA_RECORDS", 0):
            self.assertEqual("unparsed", headers.project_level_metadata(original)["status"])

    def test_per_record_amplification_is_refused_before_names_are_decoded(self) -> None:
        # Reproduce the reviewer's 4,136-byte case, without any maximal run.
        data = fixture((100, [""] * 4096, (0, 0, 0, 0)))
        self.assertEqual(4136, len(data))
        with patch.object(headers, "parse_worldheaders", side_effect=AssertionError("legacy allocation before preflight")):
            report = headers.project_level_metadata(data)
        self.assertEqual("unparsed", report["status"])
        self.assertEqual("per-record configuration count exceeds metadata profile", report["reason"])
        self.assertEqual([], report["records"])
        self.assertEqual(hashlib.sha256(data).hexdigest(), report["source"]["sha256"])
        # Count admission wins even when no encoded name or trailing words are
        # present: the decoder must not enter the name loop to discover EOF.
        truncated = data[:24]
        report = headers.project_level_metadata(truncated)
        self.assertEqual("per-record configuration count exceeds metadata profile", report["reason"])
        self.assertEqual(hashlib.sha256(truncated).hexdigest(), report["source"]["sha256"])
        with patch.object(headers, "WorldHeaderRecord", side_effect=AssertionError("record allocation before count admission")):
            with self.assertRaisesRegex(headers.WorldHeadersProfileLimit, "per-record"):
                headers.parse_worldheaders(data, max_configs_per_record=128, max_config_references=8192)

    def test_aggregate_limit_refuses_many_individually_admitted_worlds_without_partial_output(self) -> None:
        data = fixture((100, ["A", "B"], (0, 0, 0, 0)), (110, ["A", "B"], (0, 0, 0, 0)))
        with patch.object(headers, "MAX_METADATA_CONFIGS_PER_RECORD", 2), patch.object(headers, "MAX_METADATA_CONFIG_REFERENCES", 3), \
                patch.object(headers, "parse_worldheaders", side_effect=AssertionError("legacy allocation before aggregate preflight")):
            report = headers.project_level_metadata(data)
        self.assertEqual("unparsed", report["status"])
        self.assertEqual("aggregate configuration references exceed metadata profile", report["reason"])
        self.assertEqual([], report["records"])
        self.assertEqual(hashlib.sha256(data).hexdigest(), report["source"]["sha256"])
        # A causal opposite limit admits all four references, proving this is
        # count admission rather than unrelated framing or content failure.
        with patch.object(headers, "MAX_METADATA_CONFIGS_PER_RECORD", 2), patch.object(headers, "MAX_METADATA_CONFIG_REFERENCES", 4):
            admitted = headers.project_level_metadata(data)
        self.assertEqual("projected", admitted["status"])
        self.assertEqual(4, sum(len(row["configurations"]) for row in admitted["records"]))

    def test_exact_count_boundaries_are_admitted_and_next_reference_refuses(self) -> None:
        bound = headers.MAX_METADATA_CONFIGS_PER_RECORD
        data = fixture((100, ["A"] * bound, (0, 0, 0, 0)))
        self.assertEqual(bound, len(headers.project_level_metadata(data)["records"][0]["configurations"]))
        data = fixture((100, ["A"] * (bound + 1), (0, 0, 0, 0)))
        self.assertEqual("per-record configuration count exceeds metadata profile", headers.project_level_metadata(data)["reason"])
        # Two small declarations demonstrate independent aggregate enforcement.
        with self.assertRaisesRegex(headers.WorldHeadersProfileLimit, "aggregate"):
            headers.parse_worldheaders(fixture((1, ["A"], (0, 0, 0, 0)), (2, ["B"], (0, 0, 0, 0))),
                                       max_configs_per_record=1, max_config_references=1)

    def test_legacy_reader_remains_exact_while_metadata_profile_is_bounded(self) -> None:
        data = fixture((100, [""] * 129, (0, 0, 0, 0)))
        parsed = headers.parse_worldheaders(data)
        self.assertEqual(129, len(parsed.records[0].configs))
        self.assertEqual(data, headers.encode_worldheaders(parsed))
        self.assertEqual("unparsed", headers.project_level_metadata(data)["status"])
        for bad in (-1, True, 1.5):
            with self.subTest(limit=bad), self.assertRaises(ValueError):
                headers.parse_worldheaders(data, max_config_references=bad)

    def test_configuration_input_cap_precedes_existing_span_decoder(self) -> None:
        data = fixture((100, ["Standard"], (0, 0, 0, 0)))
        config = b"X" * (headers.MAX_METADATA_CONFIGURATION_BYTES + 1)
        with patch("battle_engine_config_decode.parse_config", side_effect=AssertionError("configuration spans allocated before size admission")):
            report = headers.project_level_metadata(data, configuration_data=config)
        self.assertEqual("projected", report["status"])
        self.assertEqual("unparsed", report["configurationInput"]["status"])
        self.assertEqual(hashlib.sha256(config).hexdigest(), report["configurationInput"]["source"]["sha256"])
        self.assertIn("byte limit", report["configurationInput"]["reason"])
        self.assertEqual("unparsed-configuration-input", report["records"][0]["configurations"][0]["resolution"])

    def test_metadata_contains_no_input_record_bytes_or_host_paths(self) -> None:
        report = headers.project_level_metadata(fixture((100, ["Standard"], (-1, -2, -3, 0))))
        encoded = json.dumps(report, allow_nan=False)
        self.assertNotIn("/home/", encoded)
        self.assertNotIn("/var/tmp/", encoded)
        self.assertNotIn("base64", encoded)
        self.assertNotIn("rawBytes", encoded)
        self.assertTrue(report["sourceEvidence"])


class MetadataCliTests(unittest.TestCase):
    def run_tool(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, str(Path(headers.__file__)), *arguments],
                              capture_output=True, text=True, timeout=15)

    def test_cli_is_read_only_and_uses_only_logical_source_labels(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "authored-headers.dat"
            data = fixture((100, ["Standard"], (0, 0, 0, 0)));path.write_bytes(data)
            proc = self.run_tool(str(path), "--metadata-json")
            self.assertEqual(0, proc.returncode, proc.stderr)
            self.assertEqual("projected", json.loads(proc.stdout)["status"])
            self.assertNotIn(temporary, proc.stdout)
            self.assertEqual(data, path.read_bytes())
            self.assertEqual([path], list(Path(temporary).iterdir()))

    def test_cli_missing_symlink_and_malformed_are_explicit_refusals(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "bad.dat";path.write_bytes(b"authored invalid bytes")
            link = Path(temporary) / "link.dat";link.symlink_to(path.name)
            for candidate in (path, link, Path(temporary) / "absent.dat"):
                proc = self.run_tool(str(candidate), "--metadata-json")
                self.assertEqual(1, proc.returncode)
                self.assertIn(json.loads(proc.stdout)["status"], ("unparsed", "unavailable", "unsupported"))
                self.assertNotIn(temporary, proc.stdout)

    def test_missing_optional_configuration_preserves_the_header_projection(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "headers.dat"
            path.write_bytes(fixture((100, ["Standard"], (0, 0, 0, 0))))
            absent = Path(temporary) / "absent.dat"
            proc = self.run_tool(str(path), "--metadata-json", "--configurations", str(absent))
            self.assertEqual(0, proc.returncode, proc.stderr)
            report = json.loads(proc.stdout)
            self.assertEqual("projected", report["status"])
            self.assertEqual("unavailable", report["configurationInput"]["status"])
            self.assertEqual("unparsed-configuration-input", report["records"][0]["configurations"][0]["resolution"])
            self.assertNotIn(temporary, proc.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
