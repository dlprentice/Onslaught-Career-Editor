#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import collections
import os
from pathlib import Path
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
        self.assertEqual(1_012, verification["verifiedFiles"])

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


if __name__ == "__main__":
    unittest.main(verbosity=2)
