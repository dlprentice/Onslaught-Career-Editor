#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Checks the content catalogue on a small authored install (no game bytes): the survey, the loader-rule joins
(TEXT record -> loose DDS, MESH record -> loose mesh, mesh texture slot -> TEXT record), animations, audio and video
headers, the schema, and the generated-output boundary."""
from __future__ import annotations

import json
import struct
import tempfile
import unittest
import zlib
from pathlib import Path

import cmsh_animation_usage_census_tests as mesh_fixtures
import content_catalog as catalog
import public_allowlist_safety_check as safety


def aya(data: bytes) -> bytes:
    member = zlib.compress(data)
    return struct.pack("<I", len(member)) + member


def chunk(tag: bytes, payload: bytes) -> bytes:
    return tag + struct.pack("<I", len(payload)) + payload


def dds_dxt1_4x4() -> bytes:
    header = bytearray(128)
    header[:4] = b"DDS "
    struct.pack_into("<7I", header, 4, 124, 0x81007, 4, 4, 8, 0, 0)
    struct.pack_into("<2I", header, 76, 32, 0x4)
    header[84:88] = b"DXT1"
    struct.pack_into("<I", header, 108, 0x1000)
    return bytes(header) + struct.pack("<HHI", 0xFFFF, 0x0000, 0)


def text_record(name: str, *, tex_format: int = 1, requested: int = 1, compressible: int = 1) -> bytes:
    obj = bytearray(0x158)
    obj[0x08:0x08 + len(name)] = name.encode("ascii")
    struct.pack_into("<i", obj, 0x08 + 0xA0, requested)
    struct.pack_into("<i", obj, 0x08 + 0xA4, 4)
    struct.pack_into("<h", obj, 0x08 + 0xA8, 4)
    struct.pack_into("<i", obj, 0x138, 1)
    struct.pack_into("<i", obj, 0x144, tex_format)
    struct.pack_into("<i", obj, 0x148, -1)
    obj[0x154] = compressible
    body = chunk(b"CTEX", bytes(obj)) + chunk(b"TFRM", struct.pack("<I", 1))
    return chunk(b"TEXT", chunk(b"DXTX", body))


def named_mesh_record(name: str) -> bytes:
    header = name.encode("ascii").ljust(300, b"\0") + struct.pack("<ii", 7, 0) + b"\0"
    return chunk(b"MESH", chunk(b"PMSH", chunk(b"PMS2", header)))


def mesh_stream() -> bytes:
    stream = mesh_fixtures._catalog_stream(
        name="authored.msh", animations=mesh_fixtures._catalog_animation("walk"), animation_count=1)
    old = b"Skin.dds".ljust(128, b"\0")
    assert stream.count(old) == 1
    return stream.replace(old, b"meshtex\\Skin.tga".ljust(128, b"\0"))


def ogg_file() -> bytes:
    ident = b"\x01vorbis" + struct.pack("<IBIiii", 0, 1, 44100, 0, 64000, 0) + b"\xb8\x01"
    page1 = b"OggS\x00\x02" + struct.pack("<qIII", 0, 9, 0, 0) + bytes([1, len(ident)]) + ident
    page2 = b"OggS\x00\x04" + struct.pack("<qIII", 44100, 9, 1, 0) + bytes([1, 2]) + b"xy"
    return page1 + page2


def bink_file() -> bytes:
    return b"BIKi" + struct.pack("<9I", 0, 75, 0, 0, 201, 149, 25, 1, 0) + struct.pack("<I", 0) + bytes(8)


def authored_install(root: Path) -> None:
    files = {
        "data/resources/dxtntextures/meshtex%skin.tga(0)A1R5G5B5.aya": aya(dds_dxt1_4x4()),
        "data/resources/dxtntextures/unused.tga(0)A1R5G5B5.aya": aya(dds_dxt1_4x4()),
        "data/resources/meshes/m_authored.msh.aya": aya(mesh_stream()),
        "data/resources/100_res_PC.aya": aya(
            chunk(b"LVLR", struct.pack("<I", 103)) + chunk(b"TARG", struct.pack("<I", 1))
            + chunk(b"AYAD", bytes(24)) + text_record("meshtex\\skin.tga") + named_mesh_record("authored.msh")),
        "data/sounds/english/MessageBox/hello.ogg": ogg_file(),
        "data/video/briefings/PC_100_exact.vid": bink_file(),
        "data/MissionScripts/level100/main.msl": b"// authored\n",
        "BEA.exe": b"authored stand-in, never executed\n",
    }
    for rel, data in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


class AuthoredInstallTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with tempfile.TemporaryDirectory() as temp:
            game = Path(temp)
            authored_install(game)
            cls.catalog = catalog.build_catalog(game)
        cls.coverage = catalog.build_coverage(cls.catalog)
        cls.assets = {asset["id"]: asset for asset in cls.catalog["assets"]}

    def relation(self, asset_id: str, rtype: str) -> list[dict]:
        return [r for r in self.assets[asset_id]["relationships"] if r["type"] == rtype]

    def test_survey_classifies_every_file(self) -> None:
        survey = self.catalog["survey"]
        self.assertEqual(survey["unclassified"], [])
        counts = {f["family"]: f["files"] for f in survey["families"]}
        self.assertEqual(counts["dds-texture-dxtn"], 2)
        self.assertEqual(counts["mission-script-msl"], 1)
        self.assertEqual(counts["executable-code"], 1)

    def test_text_record_resolves_to_its_loose_dds_by_the_loader_path_rule(self) -> None:
        [desc] = [a for a in self.catalog["assets"] if a["type"] == "texture-descriptor"]
        [pixels] = [r for r in desc["relationships"] if r["type"] == "pixels-from"]
        self.assertEqual(pixels["status"], "resolved")
        self.assertEqual(pixels["target"], "texture:data/resources/dxtntextures/meshtex%skin.tga(0)a1r5g5b5.aya")
        self.assertIn("LoadFrame", pixels["evidence"][0]["source"])

    def test_named_mesh_record_resolves_to_the_loose_mesh(self) -> None:
        [loads] = self.relation("archive:data/resources/100_res_pc.aya", "loads-mesh")
        self.assertEqual((loads["status"], loads["target"]),
                         ("resolved", "mesh:data/resources/meshes/m_authored.msh.aya"))

    def test_mesh_slot_resolves_case_insensitively_to_the_archive_texture(self) -> None:
        [uses] = self.relation("mesh:data/resources/meshes/m_authored.msh.aya", "uses-texture")
        self.assertEqual(uses["status"], "resolved")
        self.assertTrue(uses["target"].startswith("texture-descriptor:meshtex\\skin.tga:"))
        texture = self.assets["texture:data/resources/dxtntextures/meshtex%skin.tga(0)a1r5g5b5.aya"]
        self.assertEqual(texture["referencedBy"], ["mesh:data/resources/meshes/m_authored.msh.aya"])
        unused = self.assets["texture:data/resources/dxtntextures/unused.tga(0)a1r5g5b5.aya"]
        self.assertNotIn("referencedBy", unused)
        self.assertEqual(unused["upscale"]["tiling"]["status"], "no-mesh-evidence")

    def test_animation_belongs_to_its_mesh(self) -> None:
        [anim] = [a for a in self.catalog["assets"] if a["type"] == "animation"]
        self.assertEqual(anim["name"], "walk")
        self.assertEqual((anim["animation"]["startFrame"], anim["animation"]["lastFrame"]), (10, 20))
        self.assertEqual(anim["relationships"][0]["target"], "mesh:data/resources/meshes/m_authored.msh.aya")

    def test_audio_and_video_headers(self) -> None:
        audio = self.assets["audio:data/sounds/english/messagebox/hello.ogg"]["audio"]
        self.assertEqual((audio["channels"], audio["sampleRate"], audio["seconds"], audio["languageLane"]),
                         (1, 44100, 1.0, "english"))
        video = self.assets["video:data/video/briefings/pc_100_exact.vid"]
        self.assertEqual(video["video"]["seconds"], 3.0)
        self.assertEqual(video["relationships"][0]["target"], "level:100")

    def test_every_relationship_carries_evidence(self) -> None:
        for asset in self.catalog["assets"]:
            for rel in asset["relationships"]:
                self.assertTrue(rel["evidence"], f"{asset['id']} {rel['type']}")
                for ev in rel["evidence"]:
                    self.assertIn(ev["kind"], ("loader-code", "data"))

    def test_records_match_the_published_schema(self) -> None:
        try:
            import jsonschema
        except ImportError:
            self.skipTest("jsonschema is not installed")
        schema = json.loads((catalog.TOOLS / "content_catalog.schema.json").read_text(encoding="utf-8"))
        validator = jsonschema.Draft202012Validator(schema)
        for asset in self.catalog["assets"]:
            errors = sorted(validator.iter_errors({**asset, catalog.GENERATED_MARKER: True}), key=str)
            self.assertEqual(errors, [], asset["id"])

    def test_coverage_counts(self) -> None:
        self.assertEqual(self.coverage["assetsByType"]["texture"], 2)
        self.assertEqual(self.coverage["textureFilesReferencedByADescriptor"], 1)
        self.assertEqual(self.coverage["relationshipStatus"]["uses-texture"], {"resolved": 1})


class BoundaryTests(unittest.TestCase):
    def test_self_test_passes(self) -> None:
        self.assertEqual(catalog.run_self_test(), 0)

    def test_generated_output_is_refused_by_the_public_safety_check(self) -> None:
        line = json.dumps({"id": "texture:x", catalog.GENERATED_MARKER: True})
        labels = {f.label for f in safety.content_signature_findings("notes/catalogue.jsonl", line)}
        self.assertIn("deny-generated-retail-catalogue", labels)
        labels = {f.label for f in safety.path_findings("local-data/content-catalog/assets.jsonl")}
        self.assertIn("deny-root", labels)


if __name__ == "__main__":
    unittest.main()
