#!/usr/bin/env python3
"""Synthetic tests for the nested AYA texture-fidelity census."""

from __future__ import annotations

import csv
import struct
import tempfile
import unittest
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()
