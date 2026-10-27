#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Synthetic tests for the nested AYA texture-fidelity census."""

from __future__ import annotations

import csv
import hashlib
import json
import struct
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import aya_cross_platform_compare as cross
import aya_texture_fidelity_census as census


def chunk(tag: bytes, body: bytes) -> bytes:
    return tag + struct.pack("<I", len(body)) + body


def texture_payload(
    *,
    platform: str,
    name: str = "meshtex\\test.tga",
    width: int = 8,
    height: int = 8,
    format_code: int | None = None,
    frame_mips: tuple[int, ...] = (2,),
    fill: int = 0x35,
) -> bytes:
    if format_code is None:
        format_code = 1 if platform == "PC" else 6
    body = bytearray(census.CTEX_BODY_SIZE)
    encoded_name = name.encode("ascii") + b"\0"
    body[
        census.CTEX_NAME_OFFSET
        - census.CTEX_BODY_START : census.CTEX_NAME_OFFSET
        - census.CTEX_BODY_START
        + len(encoded_name)
    ] = encoded_name
    for outer_offset, value in (
        (census.CTEX_WIDTH_OFFSET, width),
        (census.CTEX_HEIGHT_OFFSET, height),
        (census.CTEX_FRAME_COUNT_OFFSET, len(frame_mips)),
        (census.CTEX_FORMAT_OFFSET, format_code),
    ):
        struct.pack_into("<I", body, outer_offset - census.CTEX_BODY_START, value)

    frames = []
    for mip_count in frame_mips:
        frame = bytearray(struct.pack("<I", mip_count))
        if platform == "XBOX":
            for level in range(mip_count):
                mip_width, mip_height = census.mip_extent(width, height, level)
                size = census.xbox_mip_size(format_code, mip_width, mip_height)
                frame.extend(chunk(b"TMIP", bytes([fill + level]) * size))
        frames.append(chunk(b"TFRM", bytes(frame)))
    return chunk(b"DXTX", chunk(b"CTEX", bytes(body)) + b"".join(frames))


def dds(
    *,
    width: int = 8,
    height: int = 8,
    mip_count: int = 2,
    storage: str = "DXT1",
) -> bytes:
    header = bytearray(census.DDS_HEADER_LENGTH)
    header[:4] = b"DDS "
    struct.pack_into("<I", header, 4, 124)
    struct.pack_into("<I", header, 12, height)
    struct.pack_into("<I", header, 16, width)
    struct.pack_into("<I", header, 28, mip_count if mip_count > 1 else 0)
    struct.pack_into("<I", header, 76, 32)
    if storage.startswith("DXT"):
        struct.pack_into("<I", header, 80, 0x4)
        header[84:88] = storage.encode("ascii")
    elif storage == "A8R8G8B8":
        struct.pack_into("<II", header, 80, 0x41, 0)
        struct.pack_into(
            "<IIIII",
            header,
            88,
            32,
            0x00FF0000,
            0x0000FF00,
            0x000000FF,
            0xFF000000,
        )
    else:
        raise AssertionError(storage)
    payload = bytearray()
    for level in range(mip_count):
        mip_width, mip_height = census.mip_extent(width, height, level)
        payload.extend(
            bytes([0x40 + level])
            * census.dds_mip_size(storage, mip_width, mip_height)
        )
    return bytes(header + payload)


class AyaTextureFidelityCensusTests(unittest.TestCase):
    def test_pc_dxtx_ctex_and_tfrm_are_fully_accounted(self) -> None:
        parsed = census.parse_serialized_texture(
            texture_payload(platform="PC", frame_mips=(2, 1)), platform="PC"
        )
        self.assertEqual("meshtex\\test.tga", parsed.normalized_name)
        self.assertEqual((8, 8, 1), (parsed.width, parsed.height, parsed.format_code))
        self.assertEqual([2, 1], [len(frame.mips) for frame in parsed.frames])
        self.assertTrue(all(not mip.data for frame in parsed.frames for mip in frame.mips))

    def test_xbox_tmips_are_fully_accounted_and_extent_checked(self) -> None:
        parsed = census.parse_serialized_texture(
            texture_payload(platform="XBOX", format_code=6, frame_mips=(2,)),
            platform="XBOX",
        )
        self.assertEqual([(8, 8, 32), (4, 4, 8)], [
            (mip.width, mip.height, len(mip.data)) for mip in parsed.frames[0].mips
        ])

    def test_nested_owner_length_disagreements_fail_closed(self) -> None:
        payload = bytearray(texture_payload(platform="PC"))
        struct.pack_into("<I", payload, 4, len(payload))
        with self.assertRaisesRegex(ValueError, "DXTX"):
            census.parse_serialized_texture(bytes(payload), platform="PC")

        payload = bytearray(texture_payload(platform="PC"))
        struct.pack_into("<I", payload, census.CTEX_START + 4, 343)
        with self.assertRaisesRegex(ValueError, "344"):
            census.parse_serialized_texture(bytes(payload), platform="PC")

    def test_wrong_tmip_extent_fails_closed(self) -> None:
        payload = bytearray(texture_payload(platform="XBOX", format_code=6))
        tmip_length_offset = census.CTEX_END + 8 + 4 + 4
        struct.pack_into("<I", payload, tmip_length_offset, 31)
        with self.assertRaisesRegex(ValueError, "TMIP length"):
            census.parse_serialized_texture(bytes(payload), platform="XBOX")

    def test_dds_compressed_mips_have_exact_extents(self) -> None:
        storage, width, height, mips = census.parse_dds(dds(storage="DXT1"))
        self.assertEqual(("DXT1", 8, 8), (storage, width, height))
        self.assertEqual([(8, 8, 32), (4, 4, 8)], [
            (mip.width, mip.height, len(mip.data)) for mip in mips
        ])

    def test_dds_uncompressed_mips_have_exact_extents(self) -> None:
        storage, width, height, mips = census.parse_dds(
            dds(storage="A8R8G8B8", width=4, height=2, mip_count=2)
        )
        self.assertEqual(("A8R8G8B8", 4, 2), (storage, width, height))
        self.assertEqual([32, 8], [len(mip.data) for mip in mips])

    def test_dds_trailing_bytes_fail_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "beyond"):
            census.parse_dds(dds() + b"extra")

    def test_filename_parser_uses_right_hand_frame_and_source_format(self) -> None:
        self.assertEqual(
            ("meshtex\\panel.tga", 3, 2, "A4R4G4B4"),
            census.parse_dds_filename(
                "meshtex%Panel.tga(3)A4R4G4B4.aya", mustbe=False
            ),
        )
        self.assertEqual(
            ("hud\\marker.tga", 0, 4, "A8R8G8B8"),
            census.parse_dds_filename(
                "mustbe_hud%marker.tga(0)A8R8G8B8.aya", mustbe=True
            ),
        )
        self.assertIsNone(
            census.parse_dds_filename("truncated.tga(0.aya", mustbe=False)
        )

    def test_topology_shift_accepts_only_a_pc_mip_suffix(self) -> None:
        pc = census.parse_serialized_texture(
            texture_payload(platform="PC", width=8, height=8, frame_mips=(3,)),
            platform="PC",
        )
        xbox = census.parse_serialized_texture(
            texture_payload(
                platform="XBOX",
                width=4,
                height=4,
                format_code=6,
                frame_mips=(2,),
            ),
            platform="XBOX",
        )
        self.assertEqual(1, census.topology_shift(pc, xbox))

    def test_basename_only_selection_refuses_source_variants(self) -> None:
        dxt2 = census.DdsFrame(
            logical_name="particle\\test.tga",
            frame_index=0,
            source_format_code=2,
            source_format_name="A4R4G4B4",
            storage_format="DXT2",
            width=4,
            height=4,
            mips=(census.MipRecord(4, 4, b"x" * 16),),
        )
        dxt1 = census.DdsFrame(
            logical_name="particle\\test.tga",
            frame_index=0,
            source_format_code=5,
            source_format_name="R5G6B5",
            storage_format="DXT1",
            width=4,
            height=4,
            mips=(census.MipRecord(4, 4, b"y" * 8),),
        )
        frames = {
            (dxt2.logical_name, 0, 2): dxt2,
            (dxt1.logical_name, 0, 5): dxt1,
        }
        with self.assertRaisesRegex(ValueError, "basename-only"):
            census.select_dds_frame(
                frames, dxt2.logical_name, 0, ctex_format_code=None
            )
        selected, candidates = census.select_dds_frame(
            frames, dxt2.logical_name, 0, ctex_format_code=2
        )
        self.assertIs(dxt2, selected)
        self.assertEqual((dxt2, dxt1), candidates)
        self.assertIs(
            dxt1, census.select_conservative_basename_candidate(candidates)
        )

    def test_source_variant_row_is_resolved_and_conservatively_counted(self) -> None:
        dxt2 = census.DdsFrame(
            logical_name="particle\\test.tga",
            frame_index=0,
            source_format_code=2,
            source_format_name="A4R4G4B4",
            storage_format="DXT2",
            width=4,
            height=4,
            mips=(census.MipRecord(4, 4, b"x" * 16),),
        )
        dxt1 = census.DdsFrame(
            logical_name=dxt2.logical_name,
            frame_index=0,
            source_format_code=5,
            source_format_name="R5G6B5",
            storage_format="DXT1",
            width=4,
            height=4,
            mips=(census.MipRecord(4, 4, b"y" * 8),),
        )
        xbox = census.TextureFrame((census.MipRecord(4, 4, b"x" * 16),))
        (
            comparable,
            equal,
            resolved,
            conservative_dds,
            conservative_equal,
            conservative,
        ) = census.classify_frame_comparison(
            dds=dxt2,
            candidates=(dxt2, dxt1),
            xbox_format_code=7,
            xbox_frame=xbox,
            shift=0,
        )
        self.assertTrue(comparable)
        self.assertTrue(equal)
        self.assertEqual("comparable-full-topology-exact", resolved)
        self.assertIs(dxt1, conservative_dds)
        self.assertIsNone(conservative_equal)
        self.assertEqual("source-variant-ambiguous", conservative)

    def test_conservative_duplicate_rule_compares_the_explicit_code5_file(self) -> None:
        code2 = census.DdsFrame(
            logical_name="particle\\test.tga",
            frame_index=0,
            source_format_code=2,
            source_format_name="A4R4G4B4",
            storage_format="DXT1",
            width=4,
            height=4,
            mips=(census.MipRecord(4, 4, b"x" * 8),),
        )
        code5 = census.DdsFrame(
            logical_name=code2.logical_name,
            frame_index=0,
            source_format_code=5,
            source_format_name="R5G6B5",
            storage_format="DXT1",
            width=4,
            height=4,
            mips=(census.MipRecord(4, 4, b"y" * 8),),
        )
        xbox = census.TextureFrame((census.MipRecord(4, 4, b"x" * 8),))
        result = census.classify_frame_comparison(
            dds=code2,
            candidates=(code2, code5),
            xbox_format_code=6,
            xbox_frame=xbox,
            shift=0,
        )
        self.assertEqual("comparable-full-topology-exact", result[2])
        self.assertIs(code5, result[3])
        self.assertFalse(result[4])
        self.assertEqual("comparable-full-topology-different", result[5])

    def test_geometry_reader_requires_reciprocal_paired_rows(self) -> None:
        fields = list(census.GEOMETRY_REQUIRED_FIELDS)
        base = {field: "" for field in fields}
        base.update(
            {
                "schemaVersion": cross.GEOMETRY_SCHEMA,
                "resourceId": "100",
                "archiveRawSha256": "a" * 64,
                "tag": "TEXT",
                "logicalKey": "meshtex\\test.tga",
                "logicalDisplay": "MeshTex\\Test.tga",
                "logicalKeyMethod": "DXTX/CTEX:name@0x18",
                "logicalOccurrence": "0",
                "joinConfidence": "unique-logical-key",
                "declaredSize": "1",
                "counterpartDeclaredSize": "2",
                "sameDeclaredSize": "0",
                "samePayloadSha256": "0",
            }
        )
        pc = dict(base)
        pc.update(
            {
                "platform": "PC",
                "chunkIndex": "3",
                "payloadSha256": "b" * 64,
                "counterpartIndex": "4",
                "counterpartPayloadSha256": "c" * 64,
            }
        )
        xbox = dict(base)
        xbox.update(
            {
                "platform": "XBOX",
                "chunkIndex": "4",
                "payloadSha256": "c" * 64,
                "counterpartIndex": "3",
                "counterpartPayloadSha256": "b" * 64,
            }
        )
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "geometry.tsv"
            with path.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(
                    stream, fieldnames=fields, delimiter="\t", lineterminator="\n"
                )
                writer.writeheader()
                writer.writerows((pc, xbox))
            pairs, summary = census.read_geometry_pairs(path)
        self.assertEqual(1, len(pairs))
        self.assertEqual(2, summary["rowCount"])


class SerializedTextureMetadataTests(unittest.TestCase):
    def project(self, payload: bytes, **kwargs):
        options = dict(platform="PC", source_path="data/resources/100_res_PC.aya",
                       archive_sha256="a" * 64, payload_offset=128, chunk_path=(4,))
        options.update(kwargs)
        return census.serialized_texture_metadata(payload, **options)

    def test_pc_formats_and_policy_are_distinct_raw_source_fields(self):
        payload = bytearray(texture_payload(platform="PC", format_code=2))
        struct.pack_into("<i", payload, census.CTEX_BODY_START + 0xA8, 4)
        struct.pack_into("<i", payload, census.CTEX_BODY_START + 0x148, -1)
        payload[census.CTEX_BODY_START + 0x154] = 3
        row = self.project(bytes(payload))
        self.assertEqual("parsed", row["status"])
        descriptor = row["descriptor"]
        self.assertEqual((4, 2, -1, 3), tuple(descriptor[k] for k in (
            "requestedFormatCode", "resourceFileFormatCode", "mipLevelsRaw", "compressibleRaw")))
        self.assertEqual("A4R4G4B4", descriptor["serializedFormatMeaning"])
        self.assertIsNone(descriptor["ddsStorageFormat"])
        self.assertFalse(row["runtimeSelectionEstablished"])

    def test_pc_multiframe_counts_do_not_invent_external_pixel_hashes(self):
        payload = texture_payload(platform="PC", frame_mips=(3, 1, 2))
        row = self.project(payload)
        self.assertEqual([3, 1, 2], [f["declaredMipCount"] for f in row["frames"]])
        self.assertEqual(3, row["descriptor"]["declaredFrameCount"])
        self.assertEqual([(8, 8), (4, 4), (2, 2)], [
            (m["width"], m["height"]) for m in row["frames"][0]["mips"]])
        for frame in row["frames"]:
            start = frame["offsetWithinPayload"]
            raw = payload[start:start + frame["byteLength"]]
            self.assertEqual(hashlib.sha256(raw).hexdigest(), frame["sha256"])
            for mip in frame["mips"]:
                self.assertEqual("external-DDS-not-selected", mip["storage"])
                self.assertIsNone(mip["sha256"])
                self.assertIsNone(mip["byteLength"])
                self.assertIsNone(mip["offsetWithinPayload"])

    def test_xbox_multiframe_hashes_only_actual_inline_bytes(self):
        payload = texture_payload(platform="XBOX", frame_mips=(2, 1))
        row = self.project(payload, platform="XBOX")
        self.assertEqual("parsed", row["status"])
        self.assertIsNone(row["descriptor"]["requestedFormatCode"])
        self.assertIsNone(row["descriptor"]["resourceFileFormatCode"])
        self.assertIsNone(row["descriptor"]["compressibleRaw"])
        self.assertEqual(6, row["descriptor"]["serializedFormatCode"])
        for frame in row["frames"]:
            for mip in frame["mips"]:
                start = mip["offsetWithinPayload"]
                data = payload[start:start + mip["byteLength"]]
                self.assertEqual(hashlib.sha256(data).hexdigest(), mip["sha256"])
                self.assertEqual("inline-TMIP", mip["storage"])
        self.assertNotIn('"data":', json.dumps(row))

    def test_exact_identity_and_occurrence_do_not_collapse_same_names(self):
        payload = texture_payload(platform="PC")
        base = self.project(payload)
        self.assertEqual(hashlib.sha256(payload).hexdigest(), base["identity"]["payloadSha256"])
        variants = [self.project(payload, source_path="data/resources/101_res_PC.aya"),
                    self.project(payload, archive_sha256="b" * 64),
                    self.project(payload, payload_offset=129),
                    self.project(payload, chunk_path=(5,))]
        changed = bytearray(payload)
        changed[census.CTEX_BODY_START + 0x94] ^= 1  # Uninterpreted saved field still binds exact identity.
        variants.append(self.project(bytes(changed)))
        ids = {row["identity"]["occurrenceId"] for row in [base, *variants]}
        self.assertEqual(6, len(ids))
        self.assertTrue(all(row["descriptor"]["name"] == base["descriptor"]["name"] for row in variants))
        self.assertEqual(base, self.project(payload))

    def test_unknown_requested_format_survives_without_guess(self):
        payload = bytearray(texture_payload(platform="PC"))
        struct.pack_into("<i", payload, census.CTEX_BODY_START + 0xA8, -123)
        self.assertEqual(-123, self.project(bytes(payload))["descriptor"]["requestedFormatCode"])

    def test_malformed_rows_keep_full_identity_and_no_partial_frame_rows(self):
        samples = [b"", texture_payload(platform="PC")[:-1],
                   texture_payload(platform="PC") + b"orphan"]
        malformed = bytearray(texture_payload(platform="XBOX"))
        struct.pack_into("<I", malformed, census.CTEX_END + 16, 31)
        samples.append(bytes(malformed))
        for index, payload in enumerate(samples):
            with self.subTest(index=index):
                row = self.project(payload, platform="XBOX" if index == 3 else "PC")
                self.assertEqual("unparsed", row["status"])
                self.assertEqual([], row["frames"])
                self.assertIsNone(row["descriptor"])
                self.assertEqual(len(payload), row["identity"]["payloadLength"])
                self.assertEqual(hashlib.sha256(payload).hexdigest(), row["identity"]["payloadSha256"])

    def test_unsupported_platform_is_hashed_without_parser(self):
        payload = texture_payload(platform="PC")
        with patch.object(census, "parse_serialized_texture", side_effect=AssertionError("must not run")):
            row = self.project(payload, platform="PS2")
        self.assertEqual("unsupported", row["status"])
        self.assertEqual([], row["frames"])
        self.assertEqual(hashlib.sha256(payload).hexdigest(), row["identity"]["payloadSha256"])

    def test_limits_refuse_before_legacy_parser_allocates(self):
        payload = texture_payload(platform="PC", frame_mips=(3, 2))
        cases = [dict(max_source_bytes=len(payload) - 1), dict(max_frames=1),
                 dict(max_mips_per_frame=2), dict(max_total_mips=4)]
        for settings in cases:
            with self.subTest(settings=settings), patch.object(
                    census, "parse_serialized_texture", side_effect=AssertionError("must not run")):
                row = self.project(payload, limits=census.TextureDescriptorLimits(**settings))
                self.assertEqual("unsupported", row["status"])
                self.assertEqual([], row["frames"])
                self.assertTrue(row["reason"].startswith("metadata limit:"))
                self.assertEqual(hashlib.sha256(payload).hexdigest(), row["identity"]["payloadSha256"])

    def test_exact_limit_boundaries_admit(self):
        payload = texture_payload(platform="PC", frame_mips=(3, 2))
        row = self.project(payload, limits=census.TextureDescriptorLimits(
            max_source_bytes=len(payload), max_frames=2,
            max_mips_per_frame=3, max_total_mips=5))
        self.assertEqual("parsed", row["status"])
        self.assertEqual(5, sum(len(f["mips"]) for f in row["frames"]))

    def test_default_aggregate_limit_admits_1024_and_refuses_1025_before_parser(self):
        allowed = texture_payload(platform="PC", frame_mips=(32,) * 32)
        self.assertEqual("parsed", self.project(allowed)["status"])
        excessive = texture_payload(platform="PC", frame_mips=(32,) * 32 + (1,))
        with patch.object(census, "parse_serialized_texture", side_effect=AssertionError("must not run")):
            row = self.project(excessive)
        self.assertEqual("metadata limit: aggregate mip count", row["reason"])
        self.assertEqual([], row["frames"])

    def test_bad_root_or_nested_owner_never_becomes_successful_metadata(self):
        for offset, value in ((0, b"NOPE"), (8, b"NOPE"),
                              (4, struct.pack("<I", 1)), (12, struct.pack("<I", 343))):
            payload = bytearray(texture_payload(platform="PC"))
            payload[offset:offset + len(value)] = value
            with self.subTest(offset=offset):
                row = self.project(bytes(payload))
                self.assertEqual("unparsed", row["status"])
                self.assertIsNone(row["descriptor"])
                self.assertEqual([], row["frames"])

    def test_large_count_is_refused_before_parser_and_malformed_small_count_is_not_truncated(self):
        payload = bytearray(texture_payload(platform="PC"))
        struct.pack_into("<I", payload, census.CTEX_FRAME_COUNT_OFFSET, 2**32 - 1)
        with patch.object(census, "parse_serialized_texture", side_effect=AssertionError("must not run")):
            self.assertEqual("unsupported", self.project(bytes(payload))["status"])
        struct.pack_into("<I", payload, census.CTEX_FRAME_COUNT_OFFSET, 2)
        self.assertEqual("unparsed", self.project(bytes(payload))["status"])

    def test_identity_inputs_refuse_host_paths_ambiguity_and_non_bytes(self):
        payload = texture_payload(platform="PC")
        for path in ("/home/player/data.aya", "../data.aya", "data//x.aya", "C:/data.aya", "data\\x.aya", "data/./x", "data\nfile"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                self.project(payload, source_path=path)
        for options in (dict(archive_sha256="A" * 64), dict(payload_offset=True),
                        dict(payload_offset=2**64 - 1), dict(chunk_path=(True,)),
                        dict(chunk_path=(0,) * 33), dict(platform="X" * 33)):
            with self.subTest(options=options), self.assertRaises(ValueError):
                self.project(payload, **options)
        with self.assertRaises(ValueError):
            self.project(bytearray(payload))

    def test_limits_are_positive_bounded_integers(self):
        for kwargs in (dict(max_source_bytes=0), dict(max_frames=True),
                       dict(max_mips_per_frame=33), dict(max_total_mips=1025)):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                census.TextureDescriptorLimits(**kwargs)


if __name__ == "__main__":
    unittest.main()
