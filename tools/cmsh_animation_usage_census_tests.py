#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import collections
import os
from pathlib import Path
import struct
from types import SimpleNamespace
import tempfile
import unittest

import cmsh_animation_usage_census as census


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
INDEX_PATH = Path(os.environ.get("ONSLAUGHT_ASSET_INDEX", "G:/bea-asset-mirror/INDEX.jsonl"))


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
