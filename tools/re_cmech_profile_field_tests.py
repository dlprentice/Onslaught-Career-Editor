#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OWNER_PATH = ROOT / "tools/re_cmech_profile_field.py"
SPEC = importlib.util.spec_from_file_location("re_cmech_profile_field", OWNER_PATH)
assert SPEC is not None and SPEC.loader is not None
owner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(owner)

SPECIMEN_CANDIDATES = (
    ROOT / "local-lab/safe-copy-bea-pristine/BEA.exe.original.backup",
    ROOT.parents[1] / "local-lab/safe-copy-bea-pristine/BEA.exe.original.backup",
)
SPECIMEN = next((path for path in SPECIMEN_CANDIDATES if path.is_file()), SPECIMEN_CANDIDATES[0])
NAME_TABLE = ROOT / owner.NAME_TABLE_RELATIVE


class CMechProfileFieldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not SPECIMEN.is_file():
            raise unittest.SkipTest("pristine local specimen is unavailable")
        cls.data = SPECIMEN.read_bytes()
        cls.result = owner.analyze_bytes(cls.data, NAME_TABLE)

    def test_field_domain_lifecycle_and_consumers_are_exact(self) -> None:
        field = self.result["profileField"]
        self.assertEqual("Unit/definition record in DAT_008553fc", field["recordOwner"])
        self.assertEqual("0x130", field["offset"])
        self.assertEqual("0x41", field["serializedUnitValueType"])
        self.assertEqual(4, field["payloadBytes"])
        self.assertEqual(["zero", "nonzero"], field["inputEquivalenceClasses"])
        self.assertEqual([0, 1], field["storedDomain"])
        self.assertEqual(0, field["default"])
        self.assertEqual(
            [
                "0x0042f18a",
                "0x00432dcb",
                "0x00432ddc",
                "0x00433b4d",
                "0x00433b53",
                "0x0049fddd",
                "0x004a00aa",
            ],
            field["directLifecycleSites"],
        )
        self.assertEqual(
            {
                "slot71GenericMeshBreakEffectsGate": "0x0049fddd",
                "slot50DestructionContinuationGate": "0x004a00aa",
            },
            field["consumers"],
        )

    def test_receiver_and_property_rtti_closure_is_exact(self) -> None:
        slots = {
            (row["class"], row["vtable"], row["slot"]): row["function"]
            for row in self.result["rtti"]["slots"]
        }
        for class_name, vtable in {
            "CWarspite": "0x005e0684",
            "CGillM": "0x005e0b30",
            "CThunderHead": "0x005e0fe0",
            "CMech": "0x005e3074",
        }.items():
            self.assertEqual("0x004a00a0", slots[(class_name, vtable, 50)])
            self.assertEqual("0x0049fdb0", slots[(class_name, vtable, 71)])
        self.assertEqual("0x00432dc0", slots[("CUnitShatter", "0x005d9b34", 1)])
        self.assertEqual("0x004db8c0", slots[("CUnitShatter", "0x005d9b34", 2)])
        self.assertEqual("0x00434b60", slots[("CUnitShatter", "0x005d9b34", 3)])
        self.assertEqual(
            ["CUnitShatter", "CPhysicsUnitValue"],
            self.result["rtti"]["hierarchies"]["CUnitShatter"],
        )

    def test_current_geometry_and_whole_image_census_are_exact(self) -> None:
        self.assertEqual(owner.NAME_TABLE_ROWS, self.result["nameTable"]["rows"])
        self.assertEqual(owner.NAME_TABLE_SHA256, self.result["nameTable"]["sha256"])
        census = self.result["wholeImageOperandCensus"]
        self.assertEqual(156, census["rawLittleEndian0130Occurrences"])
        self.assertEqual({".data": 1, ".text": 155}, census["rawBySection"])
        self.assertEqual(116, census["decodedCurrentFunctionRangeInstructions"])
        self.assertEqual(
            owner.PRISTINE_SHA256,
            self.result["specimen"]["sha256"],
        )
        for label, (_start, _end, expected_hash) in owner.BODY_RANGES.items():
            self.assertEqual(expected_hash, self.result["bodies"][label]["sha256"])

    def test_json_is_byte_identical_across_checkout_roots(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            roots = [Path(tmp) / "ordinary-main", Path(tmp) / ".worktrees/cmech-candidate"]
            tables = []
            for root in roots:
                table = root / owner.NAME_TABLE_RELATIVE
                table.parent.mkdir(parents=True)
                table.write_bytes(NAME_TABLE.read_bytes())
                tables.append(table)

            results = [
                {**self.result, "nameTable": owner.parse_name_table(table)[1]}
                for table in tables
            ]
            rendered = [
                (json.dumps(result, indent=2, sort_keys=True) + "\n").encode("utf-8")
                for result in results
            ]

            self.assertEqual(rendered[0], rendered[1])
            decoded = rendered[0].decode("utf-8")
            self.assertEqual(owner.NAME_TABLE_RELATIVE.as_posix(), json.loads(decoded)["nameTable"]["path"])
            for root in roots:
                self.assertNotIn(root.resolve().as_posix(), decoded)

    def test_decoded_field_census_is_exhaustively_partitioned(self) -> None:
        census = self.result["wholeImageOperandCensus"]
        self.assertIn("decodedPartition", census)
        partition = census["decodedPartition"]
        self.assertEqual(116, sum(partition["counts"].values()))
        self.assertEqual(7, partition["counts"]["TARGET_PROFILE_FIELD"])
        self.assertEqual(116, len(partition["sites"]))
        self.assertEqual(
            {
                "0x0042f18a",
                "0x00432dcb",
                "0x00432ddc",
                "0x00433b4d",
                "0x00433b53",
                "0x0049fddd",
                "0x004a00aa",
            },
            {
                row["va"]
                for row in partition["sites"]
                if row["classification"] == "TARGET_PROFILE_FIELD"
            },
        )

    def test_adverse_control_is_separate_adjacent_property(self) -> None:
        self.assertEqual(
            {
                "offset": "0x128",
                "propertyClass": "CUnitIndiscriminate",
                "writer": "0x00432d90",
                "sites": ["0x00432d9b", "0x00432dac"],
                "notMergedWithTarget": True,
            },
            self.result["adverseControl"],
        )

    def test_target_site_mutation_is_refused_before_claim(self) -> None:
        mutated = bytearray(self.data)
        image = owner.rtti.PEImage(self.data)
        offset = image.va_to_file(0x00432DCB, 10)
        assert offset is not None
        mutated[offset + 6] = 2
        with self.assertRaisesRegex(owner.EvidenceError, "shatter_true bytes differ"):
            owner.analyze_bytes(bytes(mutated), NAME_TABLE, verify_identity=False)

    def test_adverse_control_mutation_is_refused(self) -> None:
        mutated = bytearray(self.data)
        image = owner.rtti.PEImage(self.data)
        offset = image.va_to_file(0x00432D9B, 10)
        assert offset is not None
        mutated[offset + 2] = 0x30
        with self.assertRaisesRegex(owner.EvidenceError, "control_indiscriminate_true bytes differ"):
            owner.analyze_bytes(bytes(mutated), NAME_TABLE, verify_identity=False)

    def test_factory_dispatch_mutation_is_refused(self) -> None:
        mutated = bytearray(self.data)
        image = owner.rtti.PEImage(self.data)
        offset = image.va_to_file(0x00432A08, 4)
        assert offset is not None
        mutated[offset] ^= 1
        with self.assertRaisesRegex(owner.EvidenceError, "shatter_factory_case_0x41_dispatch bytes differ"):
            owner.validate_exact_bytes(owner.rtti.PEImage(bytes(mutated)))

    def test_based_on_registry_and_dispatch_mutations_are_refused(self) -> None:
        image = owner.rtti.PEImage(self.data)
        for address, label in (
            (0x004332EB, "unit_based_on_registry"),
            (0x00433365, "unit_based_on_null_copy_call"),
            (0x00433378, "unit_based_on_source_copy_call"),
        ):
            with self.subTest(address=f"0x{address:08x}"):
                mutated = bytearray(self.data)
                offset = image.va_to_file(address, 1)
                assert offset is not None
                mutated[offset] ^= 1
                with self.assertRaisesRegex(owner.EvidenceError, f"{label} bytes differ"):
                    owner.validate_exact_bytes(owner.rtti.PEImage(bytes(mutated)))

    def test_nonpristine_identity_and_name_table_drift_are_refused(self) -> None:
        mutated = bytearray(self.data)
        mutated[-1] ^= 1
        with self.assertRaisesRegex(owner.EvidenceError, "not the pristine specimen"):
            owner.analyze_bytes(bytes(mutated), NAME_TABLE)

        with tempfile.TemporaryDirectory() as tmp:
            drift = Path(tmp) / NAME_TABLE.name
            drift.write_bytes(NAME_TABLE.read_bytes() + b"\n")
            with self.assertRaisesRegex(owner.EvidenceError, "name-table hash differs"):
                owner.analyze_bytes(self.data, drift)


if __name__ == "__main__":
    unittest.main()
