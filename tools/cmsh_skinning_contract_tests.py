# SPDX-License-Identifier: GPL-3.0-only

from __future__ import annotations

import sys
from pathlib import Path
import hashlib
import os
import struct
import unittest
from unittest import mock

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


def tiny_pe(body: bytes) -> contract.PeImage:
    """A PE32 image of one section that holds `body` (authored bytes, not game code) at 0x401000, image base 0x400000."""
    assert len(body) <= 0x100
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
    image[0x200:0x200 + len(body)] = body
    return contract.PeImage(bytes(image))


class PeImageTests(unittest.TestCase):
    def test_pe_image_maps_virtual_ranges_and_decodes_rel32_calls(self) -> None:
        body = bytes.fromhex("e8fb00000090")
        pe = tiny_pe(body)

        self.assertEqual(body, pe.read_va(0x401000, len(body)))
        self.assertEqual(0x401100, pe.rel32_call_target(0x401000))
        self.assertEqual(
            hashlib.sha256(body).hexdigest(),
            pe.range_sha256(0x401000, len(body)),
        )


class CodePinTests(unittest.TestCase):
    """The contract names code of the pristine executable by address, length and digest. These use authored bytes."""

    BODY = bytes(range(0x20, 0x60))

    def pin(self, offset: int, length: int) -> contract.CodePin:
        return contract.CodePin("authored", 0x401000 + offset, length, hashlib.sha256(self.BODY[offset:offset + length]).hexdigest())

    def test_a_pin_holds_for_its_bytes_and_for_nothing_else(self) -> None:
        pin = self.pin(4, 12)
        self.assertTrue(contract.code_pin_holds(tiny_pe(self.BODY), pin))
        for at in range(12):  # one byte changed anywhere inside the pin
            changed = bytearray(self.BODY)
            changed[4 + at] ^= 0x01
            self.assertFalse(contract.code_pin_holds(tiny_pe(bytes(changed)), pin), f"byte {at}")
        for outside in (3, 16):  # a byte changed next to it does not matter
            changed = bytearray(self.BODY)
            changed[outside] ^= 0x01
            self.assertTrue(contract.code_pin_holds(tiny_pe(bytes(changed)), pin), f"byte {outside}")
        self.assertFalse(contract.code_pin_holds(tiny_pe(self.BODY), pin._replace(va=pin.va + 1)), "another address")
        self.assertFalse(contract.code_pin_holds(tiny_pe(self.BODY), pin._replace(length=11)), "another length")
        with self.assertRaisesRegex(ValueError, "outside mapped sections"):
            contract.code_pin_holds(tiny_pe(self.BODY), pin._replace(va=0x500000))

    def test_windows_are_counted_where_they_overlap(self) -> None:
        digest = hashlib.sha256(b"abab").hexdigest()
        self.assertEqual(3, contract.count_hashed_windows(b"abababab", 4, digest))
        self.assertEqual(1, contract.count_hashed_windows(b"xxabab", 4, digest))
        self.assertEqual(0, contract.count_hashed_windows(b"abababab", 4, hashlib.sha256(b"cdcd").hexdigest()))
        self.assertEqual(0, contract.count_hashed_windows(b"aba", 4, digest), "a window longer than the block")
        self.assertEqual(0, contract.count_hashed_windows(b"", 4, digest))

    def test_a_loop_pin_must_occur_once_and_where_it_says(self) -> None:
        body = b"wxyz" + bytes(range(0x30, 0x40)) + b"wxyz" + bytes(range(0x50, 0x58))
        pe = tiny_pe(body)
        twice = contract.CodePin("authored", 0x401000, 4, hashlib.sha256(b"wxyz").hexdigest())
        self.assertFalse(contract.loop_pin_holds(pe, body, twice), "the same bytes twice in the block")
        once = contract.CodePin("authored", 0x401004, 4, hashlib.sha256(body[4:8]).hexdigest())
        self.assertTrue(contract.loop_pin_holds(pe, body, once))
        self.assertFalse(contract.loop_pin_holds(pe, body, once._replace(va=0x401005)), "once in the block but not at the address")
        self.assertFalse(contract.loop_pin_holds(pe, body[:4] + body[8:], once), "not in the block at all")

    def test_the_contracts_pins_are_lengths_and_digests_and_the_tool_quotes_no_bytes(self) -> None:
        digests = [contract.RENDERER_FMUL_SHA256, contract.DIAG_STORE_PREFIX_SHA256]
        for pin in (*contract.RENDERER_LOOP_PINS, *contract.OPCODE_PINS):
            self.assertGreater(pin.length, 0, pin.role)
            self.assertTrue(0x400000 <= pin.va < 0x700000, pin.role)
            digests.append(pin.sha256)
        for digest in digests:
            self.assertRegex(digest, r"^[0-9a-f]{64}$")
        self.assertEqual(len(digests), len(set(digests)), "no two pins share a digest")
        source = Path(contract.__file__).read_text(encoding="utf-8")
        self.assertNotIn("fromhex(", source, "the tool names code by digest and quotes none of it")


@unittest.skipUnless(os.environ.get("ONSLAUGHT_PRISTINE_EXE"), "pristine executable not configured")
class PristineCodePinTests(unittest.TestCase):
    """The pins against the pristine executable itself: each holds, and one changed byte inside any of them fails the contract."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.pe = contract.PeImage(contract._read(Path(os.environ["ONSLAUGHT_PRISTINE_EXE"])))

    def drifted(self, target_va: int):
        pristine = self.pe

        class DriftedPe:
            def read_va(self, va: int, size: int) -> bytes:
                payload = bytearray(pristine.read_va(va, size))
                if va <= target_va < va + size:
                    payload[target_va - va] ^= 0x01
                return bytes(payload)

        return DriftedPe()

    def test_the_pins_hold(self) -> None:
        contract.verify_renderer_palette_scale(self.pe)
        self.assertEqual(2, len(contract.verify_opcode_pins(self.pe)))
        contract.verify_diag_stores(self.pe)

    def test_each_pin_notices_a_change_even_when_the_block_hashes_are_made_to_match(self) -> None:
        # The loop and scale blocks are pinned as a whole first, so a change inside them fails there. With those two digests set to
        # the changed blocks' own, only the pins inside the blocks are left to notice it: each must.
        scale_end = contract.RENDERER_PALETTE_SCALE_VA + contract.RENDERER_PALETTE_SCALE_BYTES
        targets = [(pin.role, pin.va + at) for pin in contract.RENDERER_LOOP_PINS for at in range(pin.length)]
        scale = self.pe.read_va(contract.RENDERER_PALETTE_SCALE_VA, contract.RENDERER_PALETTE_SCALE_BYTES)
        targets += [("one-third multiply", contract.RENDERER_PALETTE_SCALE_VA + start + at)
                    for start in range(len(scale) - contract.RENDERER_FMUL_LENGTH + 1)
                    if hashlib.sha256(scale[start:start + contract.RENDERER_FMUL_LENGTH]).hexdigest() == contract.RENDERER_FMUL_SHA256
                    for at in range(contract.RENDERER_FMUL_LENGTH)]
        self.assertGreater(len(targets), 100)
        for role, va in targets:
            drift = self.drifted(va)
            loop = drift.read_va(contract.RENDERER_PALETTE_LOOP_VA, contract.RENDERER_PALETTE_LOOP_BYTES)
            changed_scale = drift.read_va(contract.RENDERER_PALETTE_SCALE_VA, contract.RENDERER_PALETTE_SCALE_BYTES)
            with mock.patch.object(contract, "RENDERER_PALETTE_LOOP_SHA256", hashlib.sha256(loop).hexdigest()), \
                    mock.patch.object(contract, "RENDERER_PALETTE_SCALE_SHA256", hashlib.sha256(changed_scale).hexdigest()):
                with self.assertRaisesRegex(ValueError, "renderer palette-scale block", msg=f"{role} at 0x{va:08x} (scale ends 0x{scale_end:08x})"):
                    contract.verify_renderer_palette_scale(drift)

    def test_one_changed_byte_in_any_pin_fails_the_contract(self) -> None:
        for pin in contract.RENDERER_LOOP_PINS:
            for at in range(pin.length):
                with self.assertRaisesRegex(ValueError, "renderer palette-scale block", msg=f"{pin.role} byte {at}"):
                    contract.verify_renderer_palette_scale(self.drifted(pin.va + at))
        scale = self.pe.read_va(contract.RENDERER_PALETTE_SCALE_VA, contract.RENDERER_PALETTE_SCALE_BYTES)
        multiplies = [start for start in range(len(scale) - contract.RENDERER_FMUL_LENGTH + 1)
                      if hashlib.sha256(scale[start:start + contract.RENDERER_FMUL_LENGTH]).hexdigest() == contract.RENDERER_FMUL_SHA256]
        self.assertEqual(16, len(multiplies))
        for start in multiplies:
            for at in range(contract.RENDERER_FMUL_LENGTH):
                with self.assertRaisesRegex(ValueError, "renderer palette-scale", msg=f"multiply at +{start} byte {at}"):
                    contract.verify_renderer_palette_scale(self.drifted(contract.RENDERER_PALETTE_SCALE_VA + start + at))
        for pin in contract.OPCODE_PINS:
            for at in range(pin.length):
                with self.assertRaisesRegex(ValueError, "opcode mismatch", msg=f"{pin.role} byte {at}"):
                    contract.verify_opcode_pins(self.drifted(pin.va + at))
        for va in contract.DIAG_STORE_VAS:
            for at in (*range(contract.DIAG_STORE_PREFIX_LENGTH), *range(contract.DIAG_STORE_LENGTH - 4, contract.DIAG_STORE_LENGTH)):
                with self.assertRaisesRegex(ValueError, "diag", msg=f"store 0x{va:08x} byte {at}"):
                    contract.verify_diag_stores(self.drifted(va + at))
            # the displacement between them differs from site to site and is not pinned
            contract.verify_diag_stores(self.drifted(va + contract.DIAG_STORE_PREFIX_LENGTH))


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
    def test_renderer_palette_scale_pin_rejects_targeted_fmul_drift(self) -> None:
        pristine = contract.PeImage(
            contract._read(Path(os.environ["ONSLAUGHT_PRISTINE_EXE"]))
        )

        class DriftedPe:
            def read_va(self, va: int, size: int) -> bytes:
                payload = bytearray(pristine.read_va(va, size))
                target_va = 0x0054B0CA
                if va <= target_va < va + size:
                    payload[target_va - va] ^= 0x01
                return bytes(payload)

        with self.assertRaisesRegex(ValueError, "renderer palette-scale block"):
            contract.verify_renderer_palette_scale(DriftedPe())

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
                "owner": "CMeshRenderer__RenderMeshCore",
                "constantVa": "0x005d8608",
                "constantBits": "0x3eaaaaab",
                "scaleInstructionCount": 16,
                "matrixElementsPerPaletteEntry": 16,
                "destinationGlobalVa": "0x009c69d4",
            },
            {
                key: report["staticRuntime"]["rendererPaletteScale"][key]
                for key in (
                    "owner",
                    "constantVa",
                    "constantBits",
                    "scaleInstructionCount",
                    "matrixElementsPerPaletteEntry",
                    "destinationGlobalVa",
                )
            },
        )
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
        self.assertIn(
            "renderer=0x0054b0ad..0x0054b224; constant=0x005d8608/0x3eaaaaab; 16 FMULs",
            tsv,
        )
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
