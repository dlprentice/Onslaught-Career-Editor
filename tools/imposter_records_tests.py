#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Authored imposter framing and view-metadata controls; no game files required."""
import math
import struct
import unittest

import imposter_records as reader


def chunk(tag, body):
    return tag + struct.pack("<I", len(body)) + body


def label(name=b"Authored tree", *, unk30=1, alt=0, unk38=1, views_count=1, num_frames=1, animated=0):
    buf = bytearray(76)
    buf[4:4 + len(name)] = name
    struct.pack_into("<3i", buf, 0x30, unk30, alt, unk38)
    struct.pack_into("<3i", buf, 0x40, views_count, num_frames, animated)
    return bytes(buf)


def views(*rows):
    return b"".join(struct.pack("<6f", *row) for row in (rows or ((0, .5, 0, 1, 2, 4),)))


def record(*, mesh=7, name=b"Authored tree", view_data=None, extra=b""):
    return chunk(b"IMPT", chunk(b"CIMP", label(name)) + chunk(b"IMSH", struct.pack("<i", mesh))
                 + chunk(b"VIEW", views() if view_data is None else view_data) + extra)


def collection(*records, count=None, before=b"", after=b"", atlas_size=(1024, 512)):
    data_payload = struct.pack("<2i", *atlas_size) if atlas_size is not None else bytes(8)
    return chunk(b"IMPS", before + chunk(b"DATA", data_payload) + chunk(b"BTXT", b"Authored atlas")
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
        self.assertEqual(item["cimpFields"], {"unknown30": 1, "alt": False, "unknown38": 1,
                                              "views": 1, "numFrames": 1, "animated": False})
        self.assertIs(item["viewCountMatchesCimp"], True)
        self.assertEqual(result["atlasSize"], {"width": 1024, "height": 512})
        self.assertEqual(item["viewMetadata"], {"status": "parsed", "countByLength": 1, "reason": None,
                         "views": [{"ordinal": 0, "left": 0., "right": .5, "top": 0., "bottom": 1.,
                                    "width": 2., "height": 4.}]})
        atlas = result["atlas"]
        self.assertEqual(data[atlas["offset"]:atlas["offset"] + atlas["length"]], b"Authored atlas")
        self.assertEqual([s["field"] for s in item["uninterpreted"]],
                         ["CIMP/mNext", "CIMP/mMesh", "CIMP/mUnknown28", "CIMP/mFrames"])

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
        # CDXImposter::mName is 32 bytes (+0x04..+0x24); a NUL past byte 32 must not terminate the name.
        [item] = reader.parse_imposter_set(collection(record(name=b"A" * 32)))["records"]
        self.assertIsNone(item["storedLabel"])
        self.assertEqual(item["labelStatus"], "unterminated")
        self.assertIn("CIMP/label", [s["field"] for s in item["uninterpreted"]])
        [at_limit] = reader.parse_imposter_set(collection(record(name=b"B" * 31)))["records"]
        self.assertEqual((at_limit["storedLabel"], at_limit["labelStatus"]), ("B" * 31, "terminated-latin1"))
        [empty] = reader.parse_imposter_set(collection(record(name=b"")))["records"]
        self.assertEqual((empty["storedLabel"], empty["labelStatus"]), ("", "empty"))

    def test_cimp_animated_and_view_count_agreement(self):
        cimp = label(b"Anim.msh", alt=1, views_count=2, num_frames=3, animated=1)
        six_views = views(*([(0, .5, 0, 1, 2, 4)] * 6))
        body = chunk(b"CIMP", cimp) + chunk(b"IMSH", struct.pack("<i", 11)) + chunk(b"VIEW", six_views)
        [ok] = reader.parse_imposter_set(collection(chunk(b"IMPT", body)))["records"]
        self.assertEqual(ok["cimpFields"], {"unknown30": 1, "alt": True, "unknown38": 1,
                                            "views": 2, "numFrames": 3, "animated": True})
        self.assertIs(ok["viewCountMatchesCimp"], True)
        bad_body = chunk(b"CIMP", cimp) + chunk(b"IMSH", struct.pack("<i", 11)) + chunk(b"VIEW", views())
        [mismatch] = reader.parse_imposter_set(collection(chunk(b"IMPT", bad_body)))["records"]
        self.assertIs(mismatch["viewCountMatchesCimp"], False)
        zero_data = reader.parse_imposter_set(collection(chunk(b"IMPT", body), atlas_size=(0, 0)))
        self.assertIsNone(zero_data["atlasSize"])
        self.assertIn("DATA", [s["field"] for s in zero_data["uninterpreted"]])

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
