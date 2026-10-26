#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only

from __future__ import annotations

import collections
import hashlib
import json
import os
from pathlib import Path
import struct
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch
import zlib

import cmsh_animation_usage_census as census
import cmsh_static_preview_tests as mesh_fixtures


class MotionClassificationTests(unittest.TestCase):
    @staticmethod
    def part(name: str, frame_map: tuple[int, ...], hierarchy_frames: int) -> SimpleNamespace:
        return SimpleNamespace(
            name=name,
            track=SimpleNamespace(
                frame_map=frame_map,
                hierarchy=tuple(object() for _ in range(hierarchy_frames)),
            ),
        )

    def test_motion_classes_keep_mixed_closing_tracks_distinct(self) -> None:
        cases = (
            ("no-nontrivial-frame-map", (self.part("static", (0, 0), 1),)),
            ("all-moving-maps-close", (self.part("loop", (0, 1, 0), 2),)),
            ("no-moving-map-closes", (self.part("one-shot", (0, 1, 1), 2),)),
            (
                "mixed-moving-map-closure",
                (
                    self.part("loop", (0, 1, 0), 2),
                    self.part("one-shot", (0, 1, 1), 2),
                ),
            ),
        )
        for expected, parts in cases:
            with self.subTest(expected=expected):
                actual, _moving = census._motion_class(parts)
                self.assertEqual(expected, actual)

    def test_frame_map_index_must_fit_the_hierarchy_pose_table(self) -> None:
        with self.assertRaisesRegex(ValueError, "outside HORI/HPOS"):
            census._motion_class((self.part("bad", (0, 2), 2),))


class MissionAnimationCallTests(unittest.TestCase):
    def test_active_calls_are_counted_without_comment_false_positives(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            data = Path(temporary)
            scripts = data / "MissionScripts" / "level001"
            scripts.mkdir(parents=True)
            (scripts / "Actor.msl").write_text(
                "// PlayAnimation(\"comment\", TRUE, TRUE);\n"
                "PlayAnimation(\"Idle\", FALSE, TRUE); // active\n"
                "PlayAnimationWait(\"Hit\", FALSE, FALSE);\n",
                encoding="utf-8",
            )

            report = census._animation_calls(data / "MissionScripts")

        self.assertEqual(2, report["sites"])
        self.assertEqual(1, report["files"])
        self.assertEqual(1, report["levels"])
        self.assertEqual({"playanimation": 1, "playanimationwait": 1}, report["commandCounts"])
        self.assertEqual({"Idle": 1, "Hit": 1}, report["tokenCounts"])


def _chunk(tag: bytes, payload: bytes) -> bytes:
    return tag + struct.pack("<I", len(payload)) + payload


def _catalog_part(
    ordinal: int = 0, *, name: str = "Hull", parent: int | None = None,
    children: tuple[int, ...] = (), reference: int | None = None,
    damage_next: int | None = None, geometry: bool = False, hfov_bits: int | None = None,
) -> bytes:
    """Small authored stream, reusing the parser owner's authored builders."""
    cmsp = bytearray(mesh_fixtures._cmsp(
        part=ordinal, children=len(children), base_position=(1.0, 2.0, 3.0), rotated=False,
    ))
    encoded = name.encode("ascii")
    cmsp[8 + 0xdc:8 + 0xdc + len(encoded)] = encoded
    if damage_next is not None:
        struct.pack_into("<III", cmsp, 8 + 0x9c, 1, 1, 0)
    records = bytes(cmsp)
    if children:
        records += _chunk(b"CHLD", struct.pack(f"<{len(children)}I", *children))
    if parent is not None:
        records += _chunk(b"PRNT", struct.pack("<I", parent))
    if damage_next is not None:
        records += _chunk(b"NMIC", struct.pack("<I", damage_next))
    records += mesh_fixtures._bbox() + _chunk(b"VHFM", b"\0")
    records += _chunk(b"HORI", bytes(48)) + _chunk(b"HPOS", bytes(16))
    if hfov_bits is not None:
        records += _chunk(b"HFOV", struct.pack("<I", hfov_bits))
    elif reference is None:
        records += _chunk(b"PBKT", b"authored opaque bytes")
    records += _chunk(b"CPOS", bytes(16))
    if damage_next is None:
        records += _chunk(b"CORI", bytes(48))
    if reference is not None:
        records += _chunk(b"REFR", struct.pack("<I", reference))
    slots = ((0, 0xffffffff, 9, 0, 0, 0), (0, 0, 0, 0, 0, 0))
    records += mesh_fixtures._pmvb(populated=geometry, texrs=slots)
    return _chunk(b"MESP", records)


def _catalog_stream(
    *, name: str = "AuthoredMesh", parts: list[bytes] | None = None,
    animations: bytes | None = None, animation_count: int = 0,
    emitters: bytes | None = None, emitter_count: int = 0,
    lod: bytes | None = None, lod_tag: bytes = b"PMS2", next_marker: bool = False,
) -> bytes:
    selected = parts if parts is not None else [_catalog_part(geometry=True)]
    header = bytearray(372)
    struct.pack_into("<I", header, 4, 1)
    struct.pack_into("<I", header, 8, int(next_marker))
    struct.pack_into("<I", header, 0x14, animation_count)
    struct.pack_into("<I", header, 0x1c, emitter_count)
    struct.pack_into("<I", header, 0x15c, len(selected))
    header[0x24:0x24 + len(name)] = name.encode("ascii")
    cmst = bytearray(36)
    struct.pack_into("<I", cmst, 8, 1)
    texture = struct.pack("<5f", 1.0, 0.0, 0.25, 1.0, 1.0) + b"Skin.dds".ljust(128, b"\0")
    stream = _chunk(b"CMSH", bytes(header)) + _chunk(b"CMST", bytes(cmst))
    stream += _chunk(b"MSHT", _chunk(b"TEXB", texture)) + b"".join(selected)
    if animations is not None:
        stream += _chunk(b"CAMD", animations)
    stream += mesh_fixtures._bbox()
    if emitters is not None:
        stream += _chunk(b"CEMT", emitters)
    if lod is not None:
        stream += _chunk(lod_tag, lod)
    return stream


def _catalog_animation(name: str, *, rate_bits: int = 0x3dcccccd) -> bytes:
    return name.encode("ascii").ljust(16, b"\0") + struct.pack("<4iI", 7, 10, 20, 10, rate_bits)


class ModelMetadataTests(unittest.TestCase):
    def row(self, stream: bytes, **kwargs: object) -> tuple[dict[str, object], object]:
        arguments = dict(source_path="resources/meshes/authored.msh.aya", archive_sha256="a" * 64,
                         source_universe_id="authored-fixture-v1", platform="pc")
        arguments.update(kwargs)
        return census.mesh_record_from_stream(stream, **arguments)

    def test_exact_content_and_occurrence_are_separate_and_do_not_use_names(self) -> None:
        stream = _catalog_stream()
        first, _ = self.row(stream)
        second, _ = self.row(stream, source_path="other/authored.msh.aya")
        offset, _ = self.row(stream, payload_offset=100, chunk_path=(2, 0))
        other_scope, _ = self.row(stream, source_universe_id="other-edition")
        changed, _ = self.row(_catalog_stream(name="AuthoredMesh2"))
        identity = first["modelMetadata"]["identity"]
        self.assertEqual(hashlib.sha256(stream).hexdigest(), identity["payloadSha256"])
        self.assertEqual(len(stream), identity["payloadBytes"])
        for other in (second, offset, other_scope):
            other_id = other["modelMetadata"]["identity"]
            self.assertEqual(identity["contentId"], other_id["contentId"])
            self.assertNotEqual(identity["occurrenceId"], other_id["occurrenceId"])
        self.assertNotEqual(identity["contentId"], changed["modelMetadata"]["identity"]["contentId"])
        self.assertIn("not independently verified", identity["scopeProvenance"])
        self.assertEqual(first, self.row(stream)[0])

    def test_original_topology_and_material_slots_preserve_absent_and_unresolved(self) -> None:
        row, mesh = self.row(_catalog_stream())
        self.assertIsNotNone(mesh)
        metadata = row["modelMetadata"]
        self.assertEqual("parsed", metadata["status"])
        part = metadata["parts"][0]
        self.assertEqual("Hull", part["name"])
        self.assertEqual(0, part["partNumber"])
        self.assertEqual([0x03020100], part["boundingBoxWords"][:1])
        geometry = part["geometry"]
        self.assertEqual((4, 36, 0x152, 4, "triangle-strip"),
                         (geometry["originalVertexCount"], geometry["stride"], geometry["fvf"],
                          geometry["primitiveCode"], geometry["primitiveMeaning"]))
        first, second = geometry["pieces"]
        self.assertEqual((5, 3, 1, 2), (first["indexCount"], first["stripPrimitiveCount"],
                                      first["distinctIndexTriangleCount"], first["repeatedIndexTriangleCount"]))
        self.assertEqual(["resolved-slot", "absent", "unresolved-slot"],
                         [r["status"] for r in first["materialBindings"][:3]])
        self.assertEqual(0, second["vertexBufferOwnerPiece"])
        self.assertEqual("Skin.dds", metadata["textures"][0]["name"])
        self.assertEqual([0x3f800000, 0, 0x3e800000, 0x3f800000, 0x3f800000],
                         metadata["textures"][0]["storedLaneWords"])
        self.assertIsNone(metadata["description"]["text"])

    def test_original_reference_and_damage_edges_are_not_lod_or_expanded_geometry(self) -> None:
        parts = [
            _catalog_part(0, name="root", children=(1, 2)),
            _catalog_part(1, name="Hull", parent=0, damage_next=2, geometry=True),
            _catalog_part(2, name="Hull_damaged", parent=0, reference=1),
        ]
        row, mesh = self.row(_catalog_stream(parts=parts))
        self.assertIsNotNone(mesh)
        metadata = row["modelMetadata"]
        root, original, ref = metadata["parts"]
        self.assertEqual([1, 2], root["relations"]["childOrdinals"])
        self.assertEqual(2, original["relations"]["nextDamagePartOrdinal"])
        self.assertEqual(1, ref["relations"]["referenceGeometryOrdinal"])
        self.assertEqual(0, ref["relations"]["parentOrdinal"])
        self.assertEqual(4, len(mesh.parts[2].vertices))  # preview expands REFR
        self.assertEqual(0, ref["geometry"]["originalVertexCount"])
        self.assertEqual([], ref["geometry"]["pieces"])
        self.assertEqual([], metadata["lodChildren"])

    def test_animation_raw_bits_and_rate_do_not_claim_fps_or_runtime_playback(self) -> None:
        stream = _catalog_stream(animations=_catalog_animation("Fly", rate_bits=0x7fc01234), animation_count=1)
        row, _ = self.row(stream)
        animations = row["modelMetadata"]["animations"]
        clip = animations["rows"][0]
        self.assertEqual(("Fly", 7, 10, 20, 10, 0x7fc01234),
                         (clip["name"], clip["mode"], clip["start"], clip["last"], clip["frameScaler"], clip["rateBits"]))
        self.assertEqual("normalized-mode-increment-per-game-tick", clip["rateSemantics"])
        self.assertIn("unknown", animations["runtimeScheduling"])
        json.dumps(row, allow_nan=False)

    def test_emitters_preserve_duplicate_name_number_and_separate_contexts(self) -> None:
        payload = mesh_fixtures.MeshEmitterBindingTests._payload(
            ("GunA", 7, 0), ("guna", 7, 0), ("GunA", 2, None),
        )
        row, _ = self.row(_catalog_stream(emitters=payload, emitter_count=3))
        emitters = row["modelMetadata"]["emitters"]["rows"]
        self.assertEqual([0, 1, 2], [e["ordinal"] for e in emitters])
        self.assertEqual([7, 7, 2], [e["number"] for e in emitters])
        self.assertEqual([2, 2, 1], [e["localNameNumberMultiplicity"] for e in emitters])
        self.assertIsNone(emitters[2]["partOrdinal"])
        self.assertIn("cockpit", emitters[0]["usageContext"])
        self.assertIn("exterior", emitters[0]["usageContext"])
        self.assertIn("not established", emitters[0]["worldMuzzle"])
        self.assertEqual(12, len(emitters[0]["orientationWords"]))

    def test_lod_relationship_has_its_own_exact_occurrence_coordinates(self) -> None:
        child = _catalog_stream(name="LowDetail")
        stream = _catalog_stream(lod=bytes(309) + child, next_marker=True)
        row, _ = self.row(stream, payload_offset=512, chunk_path=(8,))
        metadata = row["modelMetadata"]
        edge = metadata["lodChildren"][0]
        self.assertEqual("mesh-lod", edge["relationship"])
        child_meta = edge["model"]
        self.assertEqual(1, child_meta["lodOrdinal"])
        self.assertEqual(hashlib.sha256(child).hexdigest(), child_meta["identity"]["payloadSha256"])
        self.assertEqual(512 + len(stream) - len(child), child_meta["identity"]["payloadOffset"])
        self.assertEqual(8, child_meta["identity"]["chunkPath"][0])
        self.assertNotEqual(metadata["identity"]["occurrenceId"], child_meta["identity"]["occurrenceId"])

    def test_pmsh_wrapper_and_unproven_chain_are_not_silently_dropped(self) -> None:
        child = _catalog_stream(name="LowDetail")
        wrapped = _chunk(b"PMS2", bytes(309) + child)
        row, _ = self.row(_catalog_stream(lod=wrapped, lod_tag=b"PMSH", next_marker=True))
        self.assertEqual("parsed", row["modelMetadata"]["lodChildren"][0]["model"]["status"])
        for payload in (_chunk(b"ZZZZ", b"unknown"), b"malformed"):
            with self.subTest(payload=payload):
                row, _ = self.row(_catalog_stream(lod=payload, lod_tag=b"PMSH", next_marker=True))
                edge = row["modelMetadata"]["lodChildren"][0]
                self.assertEqual("unresolved-nested-mesh", edge["relationship"])
                self.assertEqual("unparsed", edge["model"]["status"])
                self.assertEqual(hashlib.sha256(payload).hexdigest(), edge["model"]["identity"]["payloadSha256"])
        row, _ = self.row(_catalog_stream(lod=bytes(309) + child, next_marker=False))
        self.assertEqual("unresolved-nested-mesh", row["modelMetadata"]["lodChildren"][0]["relationship"])

    def test_unknown_input_and_malformed_subsections_remain_explicit_rows(self) -> None:
        for stream in (b"not CMSH", _catalog_stream()[:-1]):
            with self.subTest(stream=stream[:8]):
                row, mesh = self.row(stream)
                self.assertIsNone(mesh)
                self.assertEqual("unparsed", row["modelMetadata"]["status"])
                self.assertEqual(hashlib.sha256(stream).hexdigest(), row["modelMetadata"]["identity"]["payloadSha256"])
        bad_animation = _catalog_stream(animations=_catalog_animation("Fly")[:-1], animation_count=1)
        bad_emitter = _catalog_stream(emitters=struct.pack("<I", 335), emitter_count=1)
        absent_animation = _catalog_stream(animation_count=1)
        for stream, lane in ((bad_animation, "animations"), (bad_emitter, "emitters"), (absent_animation, "animations")):
            with self.subTest(lane=lane):
                row, mesh = self.row(stream)
                self.assertIsNotNone(mesh)
                self.assertEqual("partial", row["modelMetadata"]["status"])
                self.assertEqual("unparsed", row["modelMetadata"][lane]["status"])
                self.assertTrue(row["modelMetadata"][lane]["falsifier"])

    def test_duplicate_animation_names_and_modes_are_not_deduplicated(self) -> None:
        clips = _catalog_animation("Fly") + _catalog_animation("fly")
        row, _ = self.row(_catalog_stream(animations=clips, animation_count=2))
        rows = row["modelMetadata"]["animations"]["rows"]
        self.assertEqual(["Fly", "fly"], [clip["name"] for clip in rows])
        self.assertEqual([2, 2], [clip["localNameMultiplicity"] for clip in rows])
        self.assertEqual([2, 2], [clip["localModeMultiplicity"] for clip in rows])

    def test_bone_palette_is_original_part_indices_not_fabricated_weights(self) -> None:
        stream = mesh_fixtures.build_skinned_fixture_stream()
        # These parser fixtures deliberately use VHFM=1 as carried data; the
        # census also validates frame-map membership, so make that authored
        # single-pose lane select its sole valid index.
        stream = stream.replace(_chunk(b"VHFM", b"\1"), _chunk(b"VHFM", b"\0"))
        row, mesh = self.row(stream)
        self.assertIsNotNone(mesh)
        part = row["modelMetadata"]["parts"][1]
        self.assertEqual([0, 2], part["skinning"]["bonePartOrdinals"])
        self.assertEqual({"0", "1"}, set(part["skinning"]["boneSlotUse"]))
        self.assertIn("not inferred", part["skinning"]["weightSemantics"])
        self.assertEqual((48, 0), (part["geometry"]["stride"], part["geometry"]["fvf"]))

    def test_nonfinite_hfov_is_preserved_as_words_without_nonstandard_json_numbers(self) -> None:
        parts = [_catalog_part(0, children=(1,)), _catalog_part(1, parent=0, hfov_bits=0x7fc01234)]
        row, mesh = self.row(_catalog_stream(parts=parts))
        self.assertIsNotNone(mesh)
        self.assertIsNone(row["hfov"][0]["values"])
        self.assertEqual([0x7fc01234], row["hfov"][0]["rawWords"])
        self.assertEqual([0x7fc01234], row["modelMetadata"]["parts"][1]["frameLanes"]["hfovWords"])
        json.dumps(row, allow_nan=False)

    def test_lod_depth_and_missing_children_are_explicit_unknowns(self) -> None:
        child = _catalog_stream(name="LowDetail")
        with patch.object(census, "MAX_LOD_DEPTH", 0):
            row, _ = self.row(_catalog_stream(lod=bytes(309) + child, next_marker=True))
        metadata = row["modelMetadata"]
        self.assertEqual("partial", metadata["status"])
        self.assertEqual("limit exceeded", metadata["lodChildren"][0]["model"]["reason"]["category"])
        row, _ = self.row(_catalog_stream(next_marker=True))
        self.assertIn("LOD presence marker and decoded child disagree", row["modelMetadata"]["unknowns"])
        row, _ = self.row(_catalog_stream(lod=child, next_marker=True))
        self.assertEqual("unresolved-nested-mesh", row["modelMetadata"]["lodChildren"][0]["relationship"])

    def test_selected_census_keeps_unknown_rows_outside_legacy_joins(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            meshes = root / "resources" / "meshes"
            meshes.mkdir(parents=True)
            (root / "MissionScripts").mkdir()
            (root / "default physics.dat").write_bytes(_physics_fixture())
            compressed = zlib.compress(_catalog_stream())
            (meshes / "authored.msh.aya").write_bytes(struct.pack("<I", len(compressed)) + compressed)
            (meshes / "unsupported.msh.aya").write_bytes(b"authored invalid envelope")
            report = census.build_census(root)
            with patch.object(census, "parse_top_level_chunks_bounded", side_effect=ValueError("authored metadata refusal")):
                refused_metadata = census.build_census(root)
        self.assertEqual(2, len(report["meshes"]))
        coverage = report["modelMetadataCoverage"]
        self.assertEqual((2, 1), (coverage["selectedOccurrences"], coverage["legacyJoinEligible"]))
        self.assertEqual({"parsed": 1, "unparsed": 1}, coverage["outcomeCounts"])
        self.assertEqual(1, len(coverage["unknownOccurrences"]))
        self.assertEqual(1, report["meshSummary"]["parts"])
        json.dumps(report, allow_nan=False)
        self.assertEqual(1, refused_metadata["modelMetadataCoverage"]["legacyJoinEligible"])
        self.assertEqual({"unparsed": 2}, refused_metadata["modelMetadataCoverage"]["outcomeCounts"])
        self.assertEqual(2, len(refused_metadata["modelMetadataCoverage"]["unknownOccurrences"]))

    def test_absolute_escaping_and_ambiguous_source_coordinates_are_rejected(self) -> None:
        for logical in ("/tmp/source.aya", "../source.aya", "a/../source.aya", "a//b.aya", "a/./b.aya", "C:/source.aya", "a\\b.aya"):
            with self.subTest(logical=logical), self.assertRaises(ValueError):
                self.row(_catalog_stream(), source_path=logical)
        for bad in (dict(archive_sha256="not a digest"), dict(payload_offset=-1), dict(chunk_path=(True,)), dict(platform="")):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                self.row(_catalog_stream(), **bad)
        with self.assertRaisesRegex(ValueError, "immutable"):
            self.row(bytearray(_catalog_stream()))

    def test_file_wrapper_hashes_and_parses_the_same_held_bytes_once(self) -> None:
        stream = _catalog_stream()
        packed = zlib.compress(stream)
        source = struct.pack("<I", len(packed)) + packed
        path = Path("/authored/data/resources/meshes/authored.msh.aya")
        with patch.object(census, "read_held_archive", return_value=source) as read:
            row, _ = census._mesh_record(path, source_root=Path("/authored/data"))
        read.assert_called_once_with(path)
        identity = row["modelMetadata"]["identity"]
        self.assertEqual("resources/meshes/authored.msh.aya", identity["sourcePath"])
        self.assertEqual(hashlib.sha256(source).hexdigest(), identity["archiveSha256"])
        self.assertEqual(hashlib.sha256(stream).hexdigest(), identity["payloadSha256"])
        with patch.object(census, "read_held_archive", return_value=b"bad envelope"):
            row, mesh = census._mesh_record(path)
        self.assertIsNone(mesh)
        self.assertEqual("unparsed", row["modelMetadata"]["status"])
        self.assertIsNone(row["modelMetadata"]["identity"]["payloadSha256"])


def _physics_fixture(*records: tuple[int, str, dict[int, bytes]]) -> bytes:
    output = bytearray(struct.pack("<H", 0x12))
    for record_type, name, fields in records:
        body = bytearray(name.encode("ascii") + b"\0")
        for index, (field_id, value) in enumerate(fields.items()):
            body.extend(struct.pack("<II", field_id, len(value)))
            body.extend(value)
            body.extend(struct.pack("<i", -1 if index + 1 == len(fields) else 0))
        output.extend(struct.pack("<II", record_type, len(body)))
        output.extend(body)
    output.extend(struct.pack("<i", -1))
    return bytes(output)


def _world_instance(
    thing_type: int,
    definition: str,
    *,
    name: str,
    script: str,
    active: int = 1,
) -> bytes:
    return b"".join(
        (
            struct.pack(
                "<i6f3i",
                thing_type,
                1.25,
                2.5,
                -3.75,
                0.5,
                0.0,
                0.0,
                0,
                2,
                -1,
            ),
            script.encode("ascii") + b"\0",
            name.encode("ascii") + b"\0",
            b"\0",
            struct.pack("<iiB", active, 0, len(definition)),
            definition.encode("ascii"),
            struct.pack("<i", -1),
        )
    )


class WorldInstanceParsingTests(unittest.TestCase):
    def test_physics_unit_and_feature_mesh_fields_keep_their_owners_distinct(self) -> None:
        data = _physics_fixture(
            (1, "Building", {8: struct.pack("<I", 8), 9: b"tower.msh\0"}),
            (8, "Ice", {2: b"iceberg1.msh\0"}),
        )

        parsed = census._physics_mesh_definitions(data)

        self.assertEqual(2, parsed["recordCount"])
        self.assertEqual(
            {
                "Building": [
                    {
                        "behaviorSerializedType": 8,
                        "factorySelector": 7,
                        "mesh": "tower.msh",
                        "meshFieldId": 9,
                        "memberShell": "CBuilding",
                        "physicsRecordType": 1,
                        "unitDefinitionOrdinal": 0,
                        "wresThingType": 8,
                    }
                ],
                "Ice": [
                    {
                        "mesh": "iceberg1.msh",
                        "meshFieldId": 2,
                        "physicsRecordType": 8,
                        "wresThingType": 35,
                    }
                ],
            },
            parsed["definitions"],
        )
        self.assertEqual(
            [
                {
                    "behaviorSerializedType": 8,
                    "definition": "Building",
                    "factorySelector": 7,
                    "memberShell": "CBuilding",
                    "mesh": "tower.msh",
                    "unitDefinitionOrdinal": 0,
                }
            ],
            parsed["unitDefinitions"],
        )
        self.assertEqual(
            (0, 11, *range(2, 11), *range(12, 26)),
            census.UNIT_BEHAVIOR_SELECTOR_BY_SERIALIZED_TYPE,
        )

    def test_definition_instance_scan_recovers_transform_names_and_script(self) -> None:
        definitions = census._physics_mesh_definitions(
            _physics_fixture(
                (1, "Building", {8: struct.pack("<I", 8), 9: b"tower.msh\0"}),
                (8, "Ice", {2: b"iceberg1.msh\0"}),
            )
        )["definitions"]
        prefix = b"not a record\0"
        body = prefix + _world_instance(8, "Building", name="Tower 01", script="Tower")
        body += _world_instance(35, "Ice", name="", script="")
        body += b"\x08Building"  # marker-shaped noise must not become an instance

        scanned = census._scan_wres_definition_instances(body, definitions, "123", "RLWD")

        self.assertEqual(3, scanned["markerCandidates"])
        self.assertEqual(1, scanned["rejectedCandidates"])
        self.assertEqual(2, len(scanned["instances"]))
        building, feature = scanned["instances"]
        self.assertEqual(len(prefix), building["recordOffset"])
        self.assertEqual([1.25, 2.5, -3.75], building["position"])
        self.assertEqual([0.5, 0.0, 0.0], building["orientation"])
        self.assertEqual("Tower 01", building["name"])
        self.assertEqual("Tower", building["script"])
        self.assertEqual(8, building["thingType"])
        self.assertEqual(35, feature["thingType"])

    def test_anonymous_mesh_body_requires_one_structural_pms2_owner(self) -> None:
        cmsh = b"CMSH" + struct.pack("<I", 372) + (b"\0" * 372)
        payload = _chunk(b"PMSH", _chunk(b"PMS2", (b"\0" * 309) + cmsh))

        self.assertEqual(cmsh, census._direct_embedded_cmsh(payload))
        with self.assertRaisesRegex(ValueError, "exactly one direct embedded CMSH"):
            census._direct_embedded_cmsh(
                payload + _chunk(b"PMSH", _chunk(b"PMS2", (b"\0" * 309) + cmsh))
            )


class OutputBoundaryTests(unittest.TestCase):
    def test_generated_report_must_stay_under_an_ignored_output_root(self) -> None:
        self.assertTrue(census._output_is_ignored(census.ROOT / "local-lab/run/census.json"))
        self.assertTrue(census._output_is_ignored(census.ROOT / ".artifacts/census.json"))
        self.assertFalse(census._output_is_ignored(census.ROOT / "tools/census.json"))
        self.assertFalse(census._output_is_ignored(Path("C:/elsewhere/local-lab/census.json")))


DATA_ROOT = Path(
    os.environ.get(
        "ONSLAUGHT_GAME_DATA",
        census.ROOT / "local-lab" / "safe-copy-bea-pristine" / "data",
    )
)
INDEX_PATH = Path(
    os.environ.get(
        "ONSLAUGHT_ASSET_INDEX",
        census.ROOT / "local-lab/inputs/asset-mirror/INDEX.jsonl",
    )
)


@unittest.skipUnless(
    (DATA_ROOT / "resources" / "meshes").is_dir() and INDEX_PATH.is_file(),
    "the hash-pinned retail data and mirror index are not materialised locally",
)
class ShippedAnimationUsageCensusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = census.build_census(DATA_ROOT, INDEX_PATH)
        cls.meshes = {row["file"]: row for row in cls.report["meshes"]}

    def test_all_selected_inputs_match_the_mirror_index(self) -> None:
        verification = self.report["inputVerification"]
        self.assertEqual(census.INDEX_SCHEMA, verification["schema"])
        self.assertEqual(
            "c45722aeed52e77788c7886cb30b813900d3516b1c387983c442d2b02d4fe4b9",
            verification["indexSha256"],
        )
        self.assertEqual(1_013, verification["verifiedFiles"])

    def test_loose_animation_lane_population_is_exact(self) -> None:
        self.assertEqual(
            {
                "meshes": 213,
                "parts": 3_774,
                "meshesWithNontrivialFrameMaps": 64,
                "partsWithNontrivialFrameMaps": 659,
                "motionClassCounts": {
                    "all-moving-maps-close": 15,
                    "mixed-moving-map-closure": 12,
                    "no-moving-map-closes": 37,
                    "no-nontrivial-frame-map": 149,
                },
                "boneMeshes": 7,
                "boneCarriers": 7,
                "hfovMeshes": 17,
                "hfovParts": 17,
                "aFrameValueCounts": {"0": 1_987, "1": 1_760, "2": 27},
            },
            self.report["meshSummary"],
        )
        self.assertEqual(501, max(row["maxVirtualFrames"] for row in self.meshes.values()))
        self.assertEqual(250, max(row["maxHierarchyFrames"] for row in self.meshes.values()))

    def test_bone_arrays_name_mesh_parts_and_every_slot_is_used(self) -> None:
        expected_names = {
            "m_f_dtroop.msh.aya": (
                "Bip01 R Thigh", "Bip01 L Thigh", "Bip01 Spine", "Bip01 Pelvis",
                "Bip01 Spine1", "Bip01 Head", "Bip01 R Toe0", "Bip01 R Foot",
                "Bip01 R Calf", "Bip01 R UpperArm", "Bip01 R Forearm", "Bip01 R Hand",
                "Bip01 L Toe0", "Bip01 L Foot", "Bip01 L Calf", "Bip01 L UpperArm",
                "Bip01 L Hand", "Bip01 L Forearm",
            ),
            "m_ftrooper.msh.aya": (
                "Bip01 R Thigh", "Bip01 L Thigh", "Bip01 Spine", "Bip01 Pelvis",
                "Bip01 Spine1", "Bip01 Head", "Bip01 R Toe0", "Bip01 R Foot",
                "Bip01 R Calf", "Bip01 R UpperArm", "Bip01 R Forearm", "Bip01 R Hand",
                "Bip01 L Toe0", "Bip01 L Foot", "Bip01 L Calf", "Bip01 L UpperArm",
                "Bip01 L Hand", "Bip01 L Forearm",
            ),
            "m_mcommando.msh.aya": (
                "Bip01 R Thigh", "Bip01 L Thigh", "Bip01 Spine", "Bip01 Pelvis",
                "Bip01 Spine1", "Bip01 Head", "Bip01 R Toe0", "Bip01 R Foot",
                "Bip01 R Calf", "Bip01 R UpperArm", "Bip01 R Forearm", "Bip01 R Hand",
                "Bip01 L Toe0", "Bip01 L Foot", "Bip01 L Calf", "Bip01 L UpperArm",
                "Bip01 L Forearm", "Bip01 L Hand",
            ),
            "m_mfiredude.msh.aya": (
                "Bip01 L Thigh", "Bip01 R Thigh", "Bip01 Spine", "Bip01 Pelvis",
                "Bip01 Spine1", "Bip01 Head", "Bip01 L Toe0", "Bip01 L Foot",
                "Bip01 L Calf", "Bip01 L UpperArm", "Bip01 L Forearm", "Bip01 L Hand",
                "Bip01 R Toe0", "Bip01 R Foot", "Bip01 R Calf", "Bip01 R UpperArm",
                "Bip01 R Forearm", "Bip01 L Clavicle", "Bip01 R Clavicle",
            ),
            "m_mgrunt.msh.aya": (
                "Bip01 L Thigh", "Bip01 R Thigh", "Bip01 Spine", "Bip01 Pelvis",
                "Bip01 Spine1", "Bip01 Head", "Bip01 L Toe0", "Bip01 L Foot",
                "Bip01 L Calf", "Bip01 L UpperArm", "Bip01 L Forearm", "Bip01 L Hand",
                "Bip01 R Toe0", "Bip01 R Foot", "Bip01 R Calf", "Bip01 R UpperArm",
                "Bip01 R Forearm", "Bip01 L Clavicle", "Bip01 R Clavicle",
            ),
            "m_Sentinel Arm Big.msh.aya": (
                "Bone01", "Bone02", "Bone03", "Bone04", "Bone05", "Bone06", "Bone07",
                "Bone08", "Bone09", "Bone10", "Bone12", "Bone11", "Bone13", "Bone14",
            ),
            "m_Sentinel Arm Small.msh.aya": tuple(f"Bone{index:02d}" for index in range(1, 15)),
        }
        actual = {}
        for file_name, mesh in self.meshes.items():
            carriers = mesh["boneCarriers"]
            if not carriers:
                continue
            self.assertEqual(1, len(carriers), file_name)
            carrier = carriers[0]
            self.assertEqual(1, carrier["partIndex"], file_name)
            self.assertEqual(
                set(range(len(carrier["bonePartNames"]))),
                {int(value) for value in carrier["boneSlotUse"]},
                file_name,
            )
            actual[file_name] = tuple(carrier["bonePartNames"])
        self.assertEqual(expected_names, actual)

    def test_hfov_is_one_float_on_each_of_seventeen_camera_parts(self) -> None:
        values = []
        names = []
        for mesh in self.meshes.values():
            for record in mesh["hfov"]:
                names.append(record["partName"])
                self.assertEqual(1, len(record["values"]))
                values.extend(record["values"])
        self.assertEqual(["Camera01"] * 17, names)
        self.assertEqual(
            collections.Counter(
                {
                    180.0: 2,
                    90.0: 13,
                    75.78888702392578: 1,
                    34.70261001586914: 1,
                }
            ),
            collections.Counter(values),
        )

    def test_numeric_lvlr_mesh_membership_joins_to_the_loose_shelf(self) -> None:
        membership = self.report["levelMeshMembership"]
        self.assertEqual(66, membership["archives"])
        self.assertEqual(3_485, membership["meshChunks"])
        self.assertEqual(3_432, membership["resolvedOccurrences"])
        self.assertEqual(205, membership["uniqueResolvedLooseMeshes"])
        self.assertEqual(53, membership["unresolvedOccurrences"])
        self.assertEqual({"": 53}, membership["unresolvedNames"])
        absent = sorted(set(self.meshes) - set(membership["levelsByLooseMesh"]))
        self.assertEqual(
            [
                "m_PS2_Normal_Logo3.MSH.aya",
                "m_be_trans.msh.aya",
                "m_be_transm.msh.aya",
                "m_default.msh.aya",
                "m_f_truck.msh.aya",
                "m_m_battleship.msh.aya",
                "m_m_truck.msh.aya",
                "m_panorama.msh.aya",
            ],
            absent,
        )
        self.assertEqual(["800"], membership["levelsByLooseMesh"]["m_Sentinel Arm Big.msh.aya"])
        self.assertEqual(["800"], membership["levelsByLooseMesh"]["m_Sentinel Arm Small.msh.aya"])

    def test_msl_animation_call_population_is_exact(self) -> None:
        calls = self.report["missionAnimationCalls"]
        self.assertEqual(56, calls["sites"])
        self.assertEqual(15, calls["files"])
        self.assertEqual(9, calls["levels"])
        self.assertEqual({"playanimation": 32, "playanimationwait": 24}, calls["commandCounts"])
        self.assertEqual(
            {
                "open": 12,
                "opening": 12,
                "closed": 10,
                "closing": 8,
                "Idle": 8,
                "Hit": 2,
                "Activate": 1,
                "Activated": 1,
                "Opening": 1,
                "Open": 1,
            },
            calls["tokenCounts"],
        )
        self.assertEqual(
            {
                "FALSE,FALSE": 2,
                "FALSE,TRUE": 8,
                "TRUE,FALSE": 22,
                "TRUE,TRUE": 24,
            },
            calls["flagCounts"],
        )

    def test_wres_definition_instances_join_physics_lvlr_loose_cmsh_and_pose(self) -> None:
        joined = self.report["worldInstanceJoin"]
        self.assertEqual(
            {
                "activeInstances": 4_029,
                "archives": 66,
                "boneCarrierInstances": 0,
                "directScriptInstances": 730,
                "instances": 4_090,
                "instancesByKind": {"BSWD": 2_731, "RLWD": 1_359},
                "instancesByThingType": {"8": 3_578, "35": 512},
                "meshNumberCounts": {"0": 4_090},
                "motionClassCounts": {
                    "all-moving-maps-close": 129,
                    "mixed-moving-map-closure": 1,
                    "no-moving-map-closes": 1_182,
                    "no-nontrivial-frame-map": 2_778,
                },
                "physicsDefinitionNames": 201,
                "physicsRecords": 777,
                "resolvedNamedLevelMeshInstances": 4_090,
                "uniqueDefinitions": 134,
                "uniqueLooseMeshes": 115,
                "unresolvedResourceInstances": 0,
                "unresolvedScriptInstances": 85,
            },
            joined["summary"],
        )
        level100 = [row for row in joined["instances"] if row["level"] == "100"]
        self.assertEqual(38, len(level100))
        self.assertEqual({"BSWD": 33, "RLWD": 5}, collections.Counter(row["worldKind"] for row in level100))

    def test_unit_wres_instances_retain_ordinal_behavior_and_factory_identity(self) -> None:
        self.assertEqual("onslaught.cmsh-animation-usage-census.v3", self.report["schema"])
        joined = self.report["worldInstanceJoin"]["unitBehaviorJoin"]
        self.assertEqual(
            {
                "definitions": 160,
                "levels": 65,
                "placedDefinitions": 105,
                "placements": 3_578,
                "placementsByKind": {"BSWD": 2_324, "RLWD": 1_254},
                "selectorsWithPlacements": 19,
                "unplacedDefinitions": 55,
            },
            joined["summary"],
        )
        self.assertEqual(["857"], joined["levelsWithoutUnitPlacements"])
        self.assertEqual(
            [
                (0, 6, 0, 0, 0, 0, 0),
                (1, 0, 0, 0, 0, 0, 0),
                (2, 20, 2, 17, 11, 0, 17),
                (3, 8, 0, 0, 0, 0, 0),
                (4, 11, 10, 751, 51, 527, 224),
                (5, 9, 8, 127, 36, 0, 127),
                (6, 3, 3, 8, 8, 0, 8),
                (7, 58, 46, 987, 50, 918, 69),
                (8, 11, 9, 346, 46, 0, 346),
                (9, 5, 5, 59, 21, 0, 59),
                (10, 2, 1, 1, 1, 0, 1),
                (11, 0, 0, 0, 0, 0, 0),
                (12, 5, 5, 88, 19, 0, 88),
                (13, 2, 2, 214, 7, 0, 214),
                (14, 1, 1, 2, 2, 0, 2),
                (15, 1, 1, 4, 4, 0, 4),
                (16, 3, 3, 34, 12, 0, 34),
                (17, 1, 1, 2, 2, 0, 2),
                (18, 2, 1, 2, 2, 0, 2),
                (19, 1, 0, 0, 0, 0, 0),
                (20, 1, 1, 1, 1, 0, 1),
                (21, 1, 0, 0, 0, 0, 0),
                (22, 3, 1, 2, 2, 0, 2),
                (23, 1, 1, 5, 5, 5, 0),
                (24, 1, 0, 0, 0, 0, 0),
                (25, 4, 4, 928, 32, 874, 54),
            ],
            [
                (
                    row["selector"],
                    row["authoredDefinitions"],
                    row["placedDefinitions"],
                    row["placements"],
                    row["levels"],
                    row["placementsByKind"]["BSWD"],
                    row["placementsByKind"]["RLWD"],
                )
                for row in joined["selectorRows"]
            ],
        )
        unit_rows = [
            row
            for row in self.report["worldInstanceJoin"]["instances"]
            if row["physicsRecordType"] == 1
        ]
        self.assertTrue(
            all(
                key in row
                for row in unit_rows
                for key in (
                    "behaviorSerializedType",
                    "factorySelector",
                    "memberShell",
                    "unitDefinitionOrdinal",
                )
            )
        )

    def test_empty_lvlr_names_are_anonymous_embedded_cmsh_not_loose_aliases(self) -> None:
        anonymous = self.report["worldInstanceJoin"]["anonymousEmbedded"]
        self.assertEqual(
            {
                "archives": 53,
                "boneCarrierRows": 41,
                "internalNameCounts": {"": 53},
                "looseCoreMatches": 0,
                "motionClassCounts": {
                    "mixed-moving-map-closure": 41,
                    "no-nontrivial-frame-map": 12,
                },
                "partCountCounts": {"1": 12, "23": 19, "25": 17, "27": 3, "28": 2},
                "rows": 53,
                "uniqueCoreHashes": 52,
                "uniqueStreamHashes": 53,
            },
            anonymous["summary"],
        )
        self.assertTrue(all(not row["displayName"] for row in anonymous["rows"]))
        self.assertTrue(all(not row["internalName"] for row in anonymous["rows"]))
        self.assertTrue(all(not row["looseCoreMatches"] for row in anonymous["rows"]))

    def test_wres_join_bounds_animation_calls_and_the_eight_absent_loose_meshes(self) -> None:
        joined = self.report["worldInstanceJoin"]
        self.assertEqual(
            {
                "authoredCallFiles": 15,
                "authoredCallSites": 56,
                "directInstanceCallFiles": 3,
                "directInstanceCallSites": 22,
                "directInstances": 3,
                "unjoinedCallFiles": 12,
                "unjoinedCallSites": 34,
            },
            joined["animationJoin"]["summary"],
        )
        self.assertEqual(
            [
                "m_PS2_Normal_Logo3.MSH.aya",
                "m_be_trans.msh.aya",
                "m_be_transm.msh.aya",
                "m_default.msh.aya",
                "m_f_truck.msh.aya",
                "m_m_battleship.msh.aya",
                "m_m_truck.msh.aya",
                "m_panorama.msh.aya",
            ],
            joined["looseMeshesWithoutNamedMembership"],
        )
        self.assertEqual(
            {name: [] for name in joined["looseMeshesWithoutNamedMembership"]},
            joined["absentLooseWresInstances"],
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
