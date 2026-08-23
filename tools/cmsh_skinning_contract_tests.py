# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import sys
from pathlib import Path
import hashlib
import os
import struct
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "rebuild" / "tools"))

import cmsh_skinning_contract as contract
import cmsh_static_preview as preview
import cmsh_static_preview_tests as preview_fixtures


class SlotPatternTests(unittest.TestCase):
    def test_classify_slot_pattern_covers_every_three_slot_equality_shape(self) -> None:
        cases = {
            (4, 4, 4): "AAA",
            (4, 4, 9): "AAB",
            (4, 9, 4): "ABA",
            (9, 4, 4): "BAA",
            (4, 9, 12): "ABC",
        }

        self.assertEqual(
            cases,
            {slots: contract.classify_slot_pattern(slots) for slots in cases},
        )


class ShaderSignatureTests(unittest.TestCase):
    def test_classify_shader_tokens_requires_the_executed_slot_zero_dead_core(self) -> None:
        retail_core = (
            0x00000001, 0x80080000, 0xA0000000,
            0x00000001, 0xB0010000, 0x9000000B,
            0x00000009, 0x80010000, 0x90E40000, 0xA0E4200A,
            0x00000009, 0x80020000, 0x90E40000, 0xA0E4200B,
            0x00000009, 0x80040000, 0x90E40000, 0xA0E4200C,
            0x00000001, 0xB0010000, 0x9055000B,
            0x00000009, 0x80010000, 0x90E40000, 0xA0E4200A,
            0x00000009, 0x80020000, 0x90E40000, 0xA0E4200B,
            0x00000009, 0x80040000, 0x90E40000, 0xA0E4200C,
            0x00000002, 0x800F0001, 0x80E40000, 0x80E40000,
            0x00000001, 0xB0010000, 0x90AA000B,
            0x00000009, 0x80010000, 0x90E40000, 0xA0E4200A,
            0x00000009, 0x80020000, 0x90E40000, 0xA0E4200B,
            0x00000009, 0x80040000, 0x90E40000, 0xA0E4200C,
            0x00000002, 0x800F0001, 0x80E40001, 0x80E40000,
            0x00000001, 0x80080001, 0xA0550000,
        )
        wrapped = (0xFFFE0101, 0xDEADBEEF, *retail_core, 0x0000FFFF)
        symmetric = list(wrapped)
        symmetric[symmetric.index(0x80E40000, 35)] = 0x80E40001

        self.assertEqual("RETAIL_SLOT0_DEAD", contract.classify_shader_tokens(wrapped))
        self.assertIsNone(contract.classify_shader_tokens(tuple(symmetric)))

    def test_parse_capture_text_counts_linked_shaders_and_rejects_dword_drift(self) -> None:
        skin = (0xFFFE0101, *contract.RETAIL_SKINNING_CORE_TOKENS, 0x0000FFFF)
        plain = (0xFFFE0101, 0x0000FFFF)
        text = (
            f"VS create ptr=0x1 dwords={len(skin)} tok="
            + ",".join(f"{value:08X}" for value in skin)
            + "\n"
            + f"VS create ptr=0x2 dwords={len(plain)} tok="
            + ",".join(f"{value:08X}" for value in plain)
            + "\n"
        )

        parsed = contract.parse_capture_text(text)

        self.assertEqual(2, parsed["shaderCreates"])
        self.assertEqual(1, parsed["retailSkinningShaders"])
        self.assertEqual(1, parsed["uniqueRetailSkinningShaders"])
        with self.assertRaisesRegex(ValueError, "declared dword count"):
            contract.parse_capture_text(text.replace(f"dwords={len(skin)}", "dwords=1", 1))

    def test_parse_capture_text_measures_complete_third_scaled_palette_blocks(self) -> None:
        lines = [
            "VSC 400 vs=0x0 reg=7 count=1 v=0.333333343,0,0,0",
            "VSC 400 vs=0x0 reg=8 count=1 v=0,0.333333343,0,0",
            "VSC 400 vs=0x0 reg=9 count=1 v=0,0,0.333333343,0",
        ]
        basis = (
            "0.333333343,0,0,1",
            "0,0.333333343,0,2",
            "0,0,0.333333343,3",
        )
        for register in range(10, 52):
            lines.append(
                f"VSC 400 vs=0x0 reg={register} count=1 v={basis[(register - 10) % 3]}"
            )

        parsed = contract.parse_capture_text("\n".join(lines) + "\n")

        self.assertEqual(1, parsed["paletteBlocks"])
        self.assertEqual(42, parsed["paletteRows"])
        self.assertAlmostEqual(1 / 3, parsed["paletteLinearRowNormMin"], places=7)
        self.assertAlmostEqual(1 / 3, parsed["paletteLinearRowNormMax"], places=7)

    def test_validate_capture_metrics_rejects_a_subsequence_only_shader_match(self) -> None:
        parsed = {
            "shaderCreates": 48,
            "retailSkinningShaders": 2,
            "uniqueRetailSkinningShaders": 2,
            "retailSkinningShaderSha256": ["0" * 64, "1" * 64],
            "paletteBlocks": 0,
            "paletteRows": 0,
        }

        with self.assertRaisesRegex(ValueError, "linked skinning shader identity"):
            contract.validate_capture_metrics(parsed, expected_palette_blocks=0)


class MeshSummaryTests(unittest.TestCase):
    def test_summarize_parsed_meshes_classifies_every_skinned_vertex_and_field_word(self) -> None:
        mesh = preview.parse_cmsh_stream(preview_fixtures.build_skinned_fixture_stream())

        summary = contract.summarize_parsed_meshes(
            [("fixture.msh.aya", "a" * 64, mesh)]
        )

        self.assertEqual(1, summary["summary"]["skinnedMeshes"])
        self.assertEqual(4, summary["summary"]["skinnedVertices"])
        self.assertEqual(
            {"AAA": 2, "AAB": 1, "ABA": 1, "BAA": 0, "ABC": 0},
            summary["summary"]["slotPatternCounts"],
        )
        self.assertEqual(12, summary["summary"]["classifiedFieldWordsPerVertex"])
        self.assertEqual(0, summary["summary"]["unclassifiedFieldWordsPerVertex"])
        with self.assertRaisesRegex(ValueError, "mesh-family denominator"):
            contract.validate_exact_mesh_summary(summary["summary"])

    def test_compare_runtime_vertex_rows_checks_all_twelve_words_and_static_buffer(self) -> None:
        mesh = preview.parse_cmsh_stream(preview_fixtures.build_skinned_fixture_stream())
        vertices = mesh.file_parts()[1].vertices
        lines = [
            "D 400 1 DIP prim=TRISTRIP primc=2 verts=4 fvf=0x15A "
            "decl=0x0 vs=0x1 s0=(vb=0x2,off=0,stride=48)",
            "G 400 1 vb real=0x2 gen=1 off=0 n=4 bytes=192 h=ABC "
            "unlocks=1 lastunlock=1 stride=48 PROVISIONAL",
        ]
        for index, vertex in enumerate(vertices):
            slots = tuple(float(slot * 3) for slot in vertex.bone_slots or ())
            lines.append(
                f"V 400 1 {index} xyzb3=({','.join(map(str, (*vertex.position, *slots)))}) "
                f"n=({','.join(map(str, vertex.normal or ()))}) "
                f"diff=0x{vertex.raw_color_u32:08X} "
                f"t0=({','.join(map(str, vertex.uv or ()))})"
            )

        result = contract.compare_runtime_vertex_rows(
            "\n".join(lines) + "\n",
            {4: ("fixture.msh.aya", vertices)},
            allowed_shader_pointers={"0X1"},
        )

        self.assertEqual(4, result["matchedVertices"])
        self.assertEqual(48, result["testedFieldWords"])
        self.assertEqual(0, result["mismatchedFieldWords"])
        self.assertEqual(1, result["staticVertexBuffers"])
        with self.assertRaisesRegex(ValueError, "pinned skinning shader"):
            contract.compare_runtime_vertex_rows(
                "\n".join(lines) + "\n",
                {4: ("fixture.msh.aya", vertices)},
                allowed_shader_pointers={"0X9"},
            )


class PeImageTests(unittest.TestCase):
    def test_pe_image_maps_virtual_ranges_and_decodes_rel32_calls(self) -> None:
        image = bytearray(0x400)
        struct.pack_into("<I", image, 0x3C, 0x80)
        image[0x80:0x84] = b"PE\0\0"
        struct.pack_into("<HHIIIHH", image, 0x84, 0x14C, 1, 0, 0, 0, 0xE0, 0)
        optional = 0x98
        struct.pack_into("<H", image, optional, 0x10B)
        struct.pack_into("<I", image, optional + 28, 0x400000)
        section = optional + 0xE0
        image[section:section + 8] = b".text\0\0\0"
        struct.pack_into("<IIII", image, section + 8, 0x100, 0x1000, 0x100, 0x200)
        body = bytes.fromhex("e8fb00000090")
        image[0x200:0x200 + len(body)] = body
        pe = contract.PeImage(bytes(image))

        self.assertEqual(body, pe.read_va(0x401000, len(body)))
        self.assertEqual(0x401100, pe.rel32_call_target(0x401000))
        self.assertEqual(
            hashlib.sha256(body).hexdigest(),
            pe.range_sha256(0x401000, len(body)),
        )


class OutputBoundaryTests(unittest.TestCase):
    def test_output_guard_allows_only_ignored_receipt_roots(self) -> None:
        root = Path(__file__).resolve().parents[1]

        self.assertTrue(contract.output_is_local(root / ".artifacts" / "skinning" / "report.json"))
        self.assertTrue(contract.output_is_local(root / "local-lab" / "skinning" / "report.json"))
        self.assertFalse(
            contract.output_is_local(
                root / "reverse-engineering" / "asset-formats" / "report.json"
            )
        )


_SPECIMEN_VARS = (
    "ONSLAUGHT_GAME_DATA",
    "ONSLAUGHT_ASSET_INDEX",
    "ONSLAUGHT_PRISTINE_EXE",
    "ONSLAUGHT_SKIN_LOG_VSDUMP800",
    "ONSLAUGHT_SKIN_LOG_VSKIN800",
    "ONSLAUGHT_SKIN_LOG_VSDUMP611",
)


@unittest.skipUnless(all(os.environ.get(name) for name in _SPECIMEN_VARS), "local skinning corpus not configured")
class SpecimenBoundTests(unittest.TestCase):
    def test_build_contract_closes_the_exact_bounded_family(self) -> None:
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

        self.assertEqual("onslaught.cmsh-matrix-palette-skinning.v1", report["schema"])
        self.assertEqual(
            {
                "meshesScanned": 213,
                "skinnedMeshes": 7,
                "rigidControlMeshes": 206,
                "boneCarriers": 7,
                "skinnedVertices": 3203,
                "slotWords": 9609,
                "slotPatternCounts": {"AAA": 2252, "AAB": 135, "ABA": 809, "BAA": 0, "ABC": 7},
                "executedVsMultiplicityDiscriminators": 816,
                "classifiedFieldWordsPerVertex": 12,
                "unclassifiedFieldWordsPerVertex": 0,
                "classifiedFieldWords": 38436,
                "unusedBoneSlots": 0,
            },
            report["meshFamily"]["summary"],
        )
        self.assertEqual(144, report["runtimeCaptures"]["summary"]["shaderCreates"])
        self.assertEqual(6, report["runtimeCaptures"]["summary"]["retailSkinningShaders"])
        self.assertEqual(32, report["runtimeCaptures"]["summary"]["paletteBlocks"])
        self.assertEqual(1344, report["runtimeCaptures"]["summary"]["paletteRows"])
        self.assertEqual(467, report["runtimeVertexReadback"]["matchedVertices"])
        self.assertEqual(5604, report["runtimeVertexReadback"]["testedFieldWords"])
        self.assertEqual(0, report["runtimeVertexReadback"]["mismatchedFieldWords"])
        self.assertEqual(2, report["runtimeVertexReadback"]["staticVertexBuffers"])
        self.assertEqual(0, report["completion"]["unclassifiedTestedFields"])
        self.assertTrue(any("normal" in value.casefold() for value in report["unknowns"]))
        tsv = contract.render_tsv(report)
        self.assertTrue(tsv.startswith("row_id\trow_kind\tsubject\t"))
        self.assertIn("FORMULA-EXECUTED\tformula\tthree-slot position combine", tsv)
        self.assertIn("BIND-CURRENT\tbind-current\tretail palette construction", tsv)
        self.assertNotIn("C:/", tsv)
        self.assertNotIn("G:/", tsv)
        self.assertTrue(tsv.endswith("\n"))
        canonical = (
            Path(__file__).resolve().parents[1]
            / "reverse-engineering"
            / "asset-formats"
            / "cmsh-matrix-palette-skinning.tsv"
        ).read_text(encoding="utf-8")
        self.assertEqual(canonical, tsv)


if __name__ == "__main__":
    unittest.main()
