#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Authored imposter framing and view-metadata controls; no game files required."""
import math
import struct
import unittest

import imposter_records as reader


def chunk(tag, body):
    return tag + struct.pack("<I", len(body)) + body


def label(name=b"Authored tree"):
    return bytes(4) + name.ljust(64, b"\0") + bytes(8)


def views(*rows):
    return b"".join(struct.pack("<6f", *row) for row in (rows or ((0, .5, 0, 1, 2, 4),)))


def record(*, mesh=7, name=b"Authored tree", view_data=None, extra=b""):
    return chunk(b"IMPT", chunk(b"CIMP", label(name)) + chunk(b"IMSH", struct.pack("<i", mesh))
                 + chunk(b"VIEW", views() if view_data is None else view_data) + extra)


def collection(*records, count=None, before=b"", after=b""):
    return chunk(b"IMPS", before + chunk(b"DATA", bytes(8)) + chunk(b"BTXT", b"Authored atlas")
                 + chunk(b"IMPO", struct.pack("<I", len(records) if count is None else count) + b"".join(records)) + after)


class ImposterReaderTests(unittest.TestCase):
    def test_identity_positions_hashable_record_and_view_fields(self):
        authored = record()
        data = collection(authored)
        result = reader.parse_imposter_set(data)
        [item] = result["records"]
        self.assertEqual(data[item["offset"]:item["offset"] + item["length"]], authored)
        self.assertEqual((item["ordinal"], item["meshResourceId"], item["storedLabel"], item["labelStatus"]),
                         (0, 7, "Authored tree", "terminated-latin1"))
        self.assertEqual(item["viewMetadata"], {"status": "parsed", "countByLength": 1, "reason": None,
                         "views": [{"ordinal": 0, "left": 0., "right": .5, "top": 0., "bottom": 1.,
                                    "width": 2., "height": 4.}]})
        atlas = result["atlas"]
        self.assertEqual(data[atlas["offset"]:atlas["offset"] + atlas["length"]], b"Authored atlas")
        self.assertEqual([s["field"] for s in item["uninterpreted"]], ["CIMP/prefix", "CIMP/tail"])

    def test_empty_set_and_multiple_records_preserve_order(self):
        self.assertEqual(reader.parse_imposter_set(collection())["records"], [])
        rows = reader.parse_imposter_set(collection(record(mesh=9), record(mesh=3)))["records"]
        self.assertEqual([r["meshResourceId"] for r in rows], [9, 3])
        self.assertLess(rows[0]["offset"], rows[1]["offset"])

    def test_never_searches_opaque_payload_for_record_tags(self):
        fake = chunk(b"IMPO", struct.pack("<I", 1) + record(mesh=90))
        result = reader.parse_imposter_set(collection(record(mesh=7), before=chunk(b"JUNK", fake)))
        self.assertEqual([r["meshResourceId"] for r in result["records"]], [7])
        self.assertIn("JUNK", [s["field"] for s in result["uninterpreted"]])

    def test_truncation_count_and_trailing_data_are_refused(self):
        good = collection(record())
        bad = [good[:-1], good + b"x", collection(record(), count=2), collection(count=2**32 - 1),
               chunk(b"IMPS", chunk(b"IMPO", b"x")), chunk(b"JUNK", b""),
               chunk(b"IMPS", chunk(b"IMPO", struct.pack("<I", 1) + chunk(b"JUNK", b"")))]
        for data in bad:
            with self.subTest(length=len(data)), self.assertRaises(reader.ImposterFormatError):
                reader.parse_imposter_set(data)

    def test_duplicate_structural_fields_are_ambiguous(self):
        for extra in [chunk(b"IMSH", struct.pack("<i", 8)), chunk(b"CIMP", label()), chunk(b"VIEW", views())]:
            with self.subTest(extra=extra[:4]), self.assertRaises(reader.ImposterFormatError):
                reader.parse_imposter_set(collection(record(extra=extra)))
        for extra in [chunk(b"BTXT", b"other"), chunk(b"IMPO", bytes(4))]:
            with self.subTest(extra=extra[:4]), self.assertRaises(reader.ImposterFormatError):
                reader.parse_imposter_set(collection(record(), after=extra))

    def test_mesh_id_is_required_and_not_read_from_other_fields(self):
        for body in [chunk(b"JUNK", chunk(b"IMSH", bytes(4))), chunk(b"IMSH", bytes(8))]:
            with self.assertRaises(reader.ImposterFormatError):
                reader.parse_imposter_set(collection(chunk(b"IMPT", body)))

    def test_bad_view_array_retains_identity_without_a_valid_prefix(self):
        bad_rows = [(0, 1, 0, 1, math.inf, 1), (0, 1, 0, 1, 1, math.nan), (-.1, .5, 0, 1, 1, 1),
                    (.5, .5, 0, 1, 1, 1), (0, 1, 1, 0, 1, 1), (0, 1, 0, 1, 0, 1), (0, 1, 0, 1, 1, -1)]
        for row in bad_rows:
            with self.subTest(row=row):
                [item] = reader.parse_imposter_set(collection(record(view_data=views((0, 1, 0, 1, 1, 1), row))))["records"]
                self.assertEqual(item["meshResourceId"], 7)
                self.assertEqual(item["viewMetadata"]["status"], "unparsed")
                self.assertEqual(item["viewMetadata"]["countByLength"], 2)
                self.assertEqual(item["viewMetadata"]["views"], [])
                self.assertNotIn(str(row), item["viewMetadata"]["reason"])

    def test_view_tail_and_empty_array_are_not_invented_frames(self):
        for body in [b"", bytes(23), views() + b"x"]:
            [item] = reader.parse_imposter_set(collection(record(view_data=body)))["records"]
            self.assertIsNone(item["viewMetadata"]["countByLength"])
            self.assertEqual(item["viewMetadata"]["views"], [])

    def test_label_terminator_must_be_inside_its_own_buffer(self):
        [item] = reader.parse_imposter_set(collection(record(name=b"A" * 64)))["records"]
        self.assertIsNone(item["storedLabel"])
        self.assertEqual(item["labelStatus"], "unterminated")
        self.assertIn("CIMP/label", [s["field"] for s in item["uninterpreted"]])
        [empty] = reader.parse_imposter_set(collection(record(name=b"")))["records"]
        self.assertEqual((empty["storedLabel"], empty["labelStatus"]), ("", "empty"))

    def test_missing_optional_metadata_is_explicit(self):
        [item] = reader.parse_imposter_set(collection(chunk(b"IMPT", chunk(b"IMSH", bytes(4)))))["records"]
        self.assertEqual(item["labelStatus"], "missing")
        self.assertEqual(item["viewMetadata"]["status"], "unparsed")

    def test_truncated_label_and_unknown_fields_remain_uninterpreted(self):
        body = chunk(b"CIMP", bytes(10)) + chunk(b"IMSH", bytes(4)) + chunk(b"NEWF", b"unknown")
        [item] = reader.parse_imposter_set(collection(chunk(b"IMPT", body)))["records"]
        self.assertEqual(item["labelStatus"], "truncated")
        self.assertEqual([s["field"] for s in item["uninterpreted"]], ["CIMP", "NEWF"])


if __name__ == "__main__":
    unittest.main()
