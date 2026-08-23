# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import sys
from pathlib import Path
import unittest
import os

sys.path.insert(0, str(Path(__file__).resolve().parent))

import cmsh_matrix_normal_contract as contract


class MatrixOrderTests(unittest.TestCase):
    def test_adverse_row_vector_chain_rejects_reversed_and_transposed_orders(self) -> None:
        bind_rotation = (
            1.0, 2.0, 0.0, 0.0,
            0.0, 1.0, 0.0, 0.0,
            0.0, 0.0, 2.0, 0.0,
            0.0, 0.0, 0.0, 1.0,
        )
        current_rotation = (
            0.0, 1.0, 0.0, 0.0,
            -1.0, 0.0, 0.0, 0.0,
            0.0, 0.0, 1.0, 0.0,
            0.0, 0.0, 0.0, 1.0,
        )
        bind_translation = (3.0, -2.0, 5.0)
        current_translation = (-7.0, 11.0, 13.0)

        control = contract.matrix_order_adverse_control(
            bind_rotation,
            bind_translation,
            current_rotation,
            current_translation,
        )

        self.assertEqual(
            "inverse(T_bind) * inverse(R_bind) * R_current * T_current",
            control["selectedFormula"],
        )
        self.assertEqual(16, len(control["selected"]))
        self.assertNotEqual(control["selected"], control["reversedProduct"])
        self.assertNotEqual(control["selected"], control["transposeMutation"])
        self.assertNotEqual(control["selected"], control["missingInverse"])

    def test_typed_operation_table_rejects_product_and_inverse_mutations(self) -> None:
        rows = [dict(row) for row in contract.MATRIX_OPERATION_TABLE]

        contract.validate_matrix_operation_table(rows)

        product_mutation = [dict(row) for row in rows]
        product_mutation[6]["left"], product_mutation[6]["right"] = (
            product_mutation[6]["right"],
            product_mutation[6]["left"],
        )
        with self.assertRaisesRegex(ValueError, "matrix product order"):
            contract.validate_matrix_operation_table(product_mutation)

        inverse_mutation = [dict(row) for row in rows]
        inverse_mutation[2]["operation"] = "transpose"
        with self.assertRaisesRegex(ValueError, "matrix inverse/transpose"):
            contract.validate_matrix_operation_table(inverse_mutation)

    def test_prior_position_law_rejects_symmetric_combine_and_wrong_scale_owner(self) -> None:
        scale = contract.float32_from_bits(0x3EAAAAAB)

        contract.validate_preserved_position_contract(
            [0.0, 2.0 * scale, scale],
            scale_owner="CMeshRenderer__RenderMeshCore",
            scale_bits=0x3EAAAAAB,
        )
        with self.assertRaisesRegex(ValueError, "symmetric slot combine"):
            contract.validate_preserved_position_contract(
                [scale, scale, scale],
                scale_owner="CMeshRenderer__RenderMeshCore",
                scale_bits=0x3EAAAAAB,
            )
        with self.assertRaisesRegex(ValueError, "palette scale owner"):
            contract.validate_preserved_position_contract(
                [0.0, 2.0 * scale, scale],
                scale_owner="CVertexShader__ApplyCustomRenderStateShaderConstants",
                scale_bits=0x3EAAAAAB,
            )


class NormalShaderTests(unittest.TestCase):
    def test_normal_block_has_two_direct_dp3_consumers_and_no_palette_deformation(self) -> None:
        result = contract.classify_normal_deformation_block(
            contract.RETAIL_NORMAL_TYPED_OPERATIONS
        )

        self.assertEqual(7, result["instructions"])
        self.assertEqual(28, result["tokens"])
        self.assertEqual(2, result["serializedNormalConsumers"])
        self.assertEqual([], result["paletteRows"])
        self.assertEqual([0.0, 0.0, 0.0], result["slotCoefficients"])
        self.assertEqual(0, result["normalizationInstructions"])
        self.assertFalse(result["translationIncluded"])

    def test_normal_block_rejects_translation_leakage_palette_reads_and_token_drift(self) -> None:
        dp4_mutation = [dict(row) for row in contract.RETAIL_NORMAL_TYPED_OPERATIONS]
        dp4_mutation[0]["opcode"] = "dp4"
        with self.assertRaisesRegex(ValueError, "normal translation leakage"):
            contract.classify_normal_deformation_block(dp4_mutation)

        palette_mutation = [dict(row) for row in contract.RETAIL_NORMAL_TYPED_OPERATIONS]
        palette_mutation[0]["sources"] = ["v3", "c[10+a0.x]"]
        with self.assertRaisesRegex(ValueError, "normal palette read"):
            contract.classify_normal_deformation_block(palette_mutation)

        with self.assertRaisesRegex(ValueError, "normal instruction drift"):
            contract.classify_normal_deformation_block(
                (*contract.RETAIL_NORMAL_TYPED_OPERATIONS, {"opcode": "nop"})
            )

    def test_vs11_decoder_accounts_for_every_token_and_instruction(self) -> None:
        tokens = (
            0xFFFE0101,
            0x0000001F, 0x80000003, 0x900F0003,
            0x00000008, 0x800F0000, 0x90E40003, 0xA0E40001,
            0x0000FFFF,
        )

        decoded = contract.decode_vs11_tokens(tokens)

        self.assertEqual(len(tokens), decoded["tokenCount"])
        self.assertEqual(2, decoded["instructionCount"])
        self.assertEqual(0, decoded["unclassifiedTokens"])
        self.assertEqual(0, decoded["unclassifiedInstructions"])
        self.assertEqual({"dcl": 1, "dp3": 1}, decoded["opcodeCounts"])

        unknown = list(tokens)
        unknown[4] = 0x00001234
        with self.assertRaisesRegex(ValueError, "unclassified shader opcode"):
            contract.decode_vs11_tokens(tuple(unknown))

    def test_synthetic_normal_interpreter_is_invariant_to_adverse_palette_translation(self) -> None:
        normal = (0.25, -0.5, 0.75)
        constants = {
            89: (1.0, 0.0, 0.0, 0.0),
            90: (0.2, 0.3, 0.4, 0.5),
            91: (0.0, 1.0, 0.0, 0.0),
            92: (0.7, 0.6, 0.5, 0.4),
        }
        base_palette = tuple((1.0, 0.0, 0.0, float(index)) for index in range(42))
        adverse_palette = tuple(
            (-row[0], row[1] + 9.0, row[2] - 11.0, row[3] + 1000.0)
            for row in base_palette
        )

        base = contract.interpret_normal_consumer_block(
            normal,
            constants,
            position_lighting_base=(0.1, 0.2, 0.3, 0.4),
            diffuse=(0.8, 0.7, 0.6, 0.5),
            palette=base_palette,
        )
        adverse = contract.interpret_normal_consumer_block(
            normal,
            constants,
            position_lighting_base=(0.1, 0.2, 0.3, 0.4),
            diffuse=(0.8, 0.7, 0.6, 0.5),
            palette=adverse_palette,
        )

        self.assertEqual(base, adverse)
        self.assertEqual((0.25, -0.5), base["normalDotProducts"])
        self.assertEqual(0, base["paletteReads"])


_SPECIMEN_VARS = (
    "ONSLAUGHT_GAME_DATA",
    "ONSLAUGHT_ASSET_INDEX",
    "ONSLAUGHT_PRISTINE_EXE",
    "ONSLAUGHT_SKIN_LOG_VSDUMP800",
    "ONSLAUGHT_SKIN_LOG_VSKIN800",
    "ONSLAUGHT_SKIN_LOG_VSDUMP611",
)


@unittest.skipUnless(
    all(os.environ.get(name) for name in _SPECIMEN_VARS),
    "local matrix/normal corpus not configured",
)
class SpecimenBoundTests(unittest.TestCase):
    def test_build_contract_closes_matrix_order_and_released_normal_law(self) -> None:
        report = contract.build_contract(
            Path(os.environ["ONSLAUGHT_GAME_DATA"]),
            Path(os.environ["ONSLAUGHT_ASSET_INDEX"]),
            Path(os.environ["ONSLAUGHT_PRISTINE_EXE"]),
            [
                Path(os.environ["ONSLAUGHT_SKIN_LOG_VSDUMP800"]),
                Path(os.environ["ONSLAUGHT_SKIN_LOG_VSKIN800"]),
                Path(os.environ["ONSLAUGHT_SKIN_LOG_VSDUMP611"]),
            ],
        )

        self.assertEqual("onslaught.cmsh-matrix-normal-deformation.v1", report["schema"])
        self.assertEqual(
            "inverse(T_bind) * inverse(R_bind) * R_current * T_current",
            report["matrixOrder"]["rowVectorFormula"],
        )
        self.assertEqual(10, len(report["matrixOrder"]["operationTable"]))
        self.assertEqual(6, report["linkedShaders"]["instances"])
        self.assertEqual(2, report["linkedShaders"]["uniqueShaders"])
        self.assertEqual(3, report["linkedShaders"]["normalBearingInstances"])
        self.assertEqual(3, report["linkedShaders"]["noNormalInstances"])
        self.assertEqual(0, report["linkedShaders"]["unclassifiedTokens"])
        self.assertEqual(0, report["linkedShaders"]["unclassifiedInstructions"])
        self.assertEqual([], report["normalLaw"]["paletteRows"])
        self.assertEqual([0.0, 0.0, 0.0], report["normalLaw"]["slotCoefficients"])
        self.assertEqual(0, report["normalLaw"]["normalizationInstructions"])
        self.assertTrue(report["normalControl"]["paletteInvariant"])
        self.assertEqual(0, report["normalControl"]["paletteReads"])
        self.assertEqual(0, report["priorPositionContract"]["slotCoefficients"][0])
        new_measurement = next(
            row for row in report["reuseLedger"] if row["disposition"] == "NEW_MEASUREMENT"
        )
        self.assertEqual(64, len(new_measurement["sha256"]))
        self.assertNotIn("SELF_HASH", new_measurement["sha256"])

        tsv = contract.render_tsv(report)
        self.assertNotIn("tok=", tsv)
        self.assertNotIn("G:/", tsv)
        self.assertNotIn("C:/", tsv)
        self.assertTrue(tsv.endswith("\n"))
        canonical = (
            Path(__file__).resolve().parents[1]
            / "reverse-engineering"
            / "asset-formats"
            / "cmsh-matrix-normal-deformation.tsv"
        ).read_text(encoding="utf-8")
        self.assertEqual(canonical, tsv)


if __name__ == "__main__":
    unittest.main()
