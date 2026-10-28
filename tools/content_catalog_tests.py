#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Checks the content catalogue on a small authored install (no game bytes): the survey, the loader-rule joins
(TEXT record -> loose DDS, MESH record -> loose mesh, mesh texture slot -> TEXT record), animations, audio and video
headers, the schema, and the generated-output boundary."""
from __future__ import annotations

import hashlib
import json
import struct
import tempfile
import unittest
import zlib
from pathlib import Path

import cmsh_animation_usage_census_tests as mesh_fixtures
import content_catalog as catalog
from dds_census_tests import dds as authored_dds
from dds_metadata_tests import rgb_dds as authored_rgb_dds
import mission_script_inspect as inspector
import public_allowlist_safety_check as safety
import world_resources_decode as worlddec


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


def text_record(name: str, *, tex_format: int = 1, requested: int = 1, compressible: int = 1, levels: int = -1,
                tag: bytes = b"TEXT") -> bytes:
    obj = bytearray(0x158)
    obj[0x08:0x08 + len(name)] = name.encode("ascii")
    struct.pack_into("<i", obj, 0x08 + 0xA0, requested)
    struct.pack_into("<i", obj, 0x08 + 0xA4, 4)
    struct.pack_into("<h", obj, 0x08 + 0xA8, 4)
    struct.pack_into("<i", obj, 0x138, 1)
    struct.pack_into("<i", obj, 0x144, tex_format)
    struct.pack_into("<i", obj, 0x148, levels)
    obj[0x154] = compressible
    body = chunk(b"CTEX", bytes(obj)) + chunk(b"TFRM", struct.pack("<I", 1))
    return chunk(tag, chunk(b"DXTX", body))


def imposter_chunk() -> bytes:
    texture = text_record("Imposters_100", tag=b"BTXT")
    label = bytearray(76)
    label[4:4 + 12] = b"authored.msh"
    impt = chunk(b"CIMP", bytes(label)) + chunk(b"IMSH", struct.pack("<i", 7)) + chunk(b"VIEW", bytes(144))
    impo = struct.pack("<I", 1) + chunk(b"IMPT", impt)
    return chunk(b"IMPS", chunk(b"DATA", bytes(8)) + texture + chunk(b"IMPO", impo))


def goodie_archive() -> bytes:
    gdat = struct.pack("<ii", 3, 0) + text_record("goodies\\art.tga")[8:]
    return aya(chunk(b"LVLR", struct.pack("<I", 103)) + chunk(b"TARG", struct.pack("<I", 1))
               + chunk(b"AYAD", bytes(24)) + chunk(b"GDIE", chunk(b"GDAT", gdat)))


PARTICLES = (
    "ParticleSystemEd_File_(C)2000_Lost_Toys_Ltd\n"
    "Particle_Descriptor_Type 1\nParticle_Descriptor_Name Spark\nBlend_Mode 1\n"
    "Texture C:\\dev\\Onslaught2\\data\\textures\\Particle\\spark.tga\n"
)


def named_mesh_record(name: str) -> bytes:
    header = name.encode("ascii").ljust(300, b"\0") + struct.pack("<ii", 7, 0) + b"\0"
    return chunk(b"MESH", chunk(b"PMSH", chunk(b"PMS2", header)))


def mesh_stream() -> bytes:
    stream = mesh_fixtures._catalog_stream(
        name="authored.msh", animations=mesh_fixtures._catalog_animation("walk"), animation_count=1)
    old = b"Skin.dds".ljust(128, b"\0")
    assert stream.count(old) == 1
    return stream.replace(old, b"meshtex\\Skin.tga".ljust(128, b"\0"))


def part_with_box(part: bytes, center: tuple[float, ...], axes: tuple[float, ...], flag: int, radius: float) -> bytes:
    # Non-coordinate vector words deliberately differ, so confusing padding
    # with the second vector or flag is caught by the assertions.
    box = chunk(b"BBOX", chunk(b"BBOX", struct.pack(
        "<3fI3fIif", *center, 0x11223344, *axes, 0x55667788, flag, radius)))
    original = mesh_fixtures.mesh_fixtures._bbox()
    assert part.count(original) == 1
    return part.replace(original, box, 1)


def catalog_authored_mesh(stream: bytes) -> dict:
    record, _, _ = catalog.catalog_mesh(
        stream, asset_id="mesh:authored", name="authored", container="resources/authored.aya",
        container_sha="a" * 64, envelope="authored", offset=0, chunk_path=[])
    return record


class StoredPartBoundsTests(unittest.TestCase):
    def test_catalog_keeps_each_part_box_and_hashes_without_exporting_payload(self) -> None:
        own = part_with_box(mesh_fixtures._catalog_part(0, name="Root", children=(1,), geometry=True),
                            (1.25, -2.5, 3.75), (0.5, 4.0, 8.0), -1, 9.0)
        # A referenced part still has its own stored box: do not use the box
        # of its resolved geometry owner or apply a hierarchy transform.
        ref = part_with_box(mesh_fixtures._catalog_part(1, name="Ref", parent=0, reference=0),
                            (-3.0, 4.5, 6.0), (2.0, 3.0, 4.0), 0, 5.0)
        stream = mesh_fixtures._catalog_stream(parts=[own, ref])
        before = hashlib.sha256(stream).hexdigest()
        record = catalog_authored_mesh(stream)
        self.assertEqual(record["mesh"]["status"], "parsed")
        first, second = record["mesh"]["hierarchy"]
        self.assertEqual(first["storedBounds"], {"center": [1.25, -2.5, 3.75],
                         "halfExtents": [0.5, 4.0, 8.0], "validFlag": -1, "radius": 9.0})
        self.assertEqual(second["storedBounds"], {"center": [-3.0, 4.5, 6.0],
                         "halfExtents": [2.0, 3.0, 4.0], "validFlag": 0, "radius": 5.0})
        for row, part in ((first, own), (second, ref)):
            self.assertEqual(row["partRecordSha256"], hashlib.sha256(part[16:332]).hexdigest())
            self.assertEqual(row["partPayloadSha256"], hashlib.sha256(part[8:]).hexdigest())
        self.assertEqual(record["sha256"], before)
        encoded = json.dumps(record, allow_nan=False)
        self.assertNotIn("authored opaque bytes", encoded)
        self.assertNotIn(str(0x11223344), encoded)
        self.assertNotIn(str(0x55667788), encoded)

    def test_nonfinite_bounds_are_null_and_do_not_break_strict_json(self) -> None:
        part = part_with_box(mesh_fixtures._catalog_part(0, geometry=True),
                             (float("nan"), float("inf"), -float("inf")),
                             (-1.25, 0.0, 2.0), 1, float("nan"))
        record = catalog_authored_mesh(mesh_fixtures._catalog_stream(parts=[part]))
        [row] = record["mesh"]["hierarchy"]
        self.assertEqual(row["storedBounds"], {"center": [None, None, None],
                         "halfExtents": [-1.25, 0.0, 2.0], "validFlag": 1, "radius": None})
        json.dumps(record, allow_nan=False)

    def test_malformed_part_box_is_not_reported_as_valid_bounds(self) -> None:
        part = mesh_fixtures._catalog_part(0, geometry=True)
        original = mesh_fixtures.mesh_fixtures._bbox()
        malformed = bytearray(original)
        struct.pack_into("<I", malformed, 12, 39)  # inner BBOX size must be 40
        self.assertEqual(part.count(original), 1)
        part = part.replace(original, bytes(malformed), 1)
        record = catalog_authored_mesh(mesh_fixtures._catalog_stream(parts=[part]))
        self.assertEqual(record["mesh"]["status"], "unparsed")
        self.assertEqual(record["mesh"]["hierarchy"], [])

    def test_schema_checks_bounds_and_hashes_without_invalidating_older_rows(self) -> None:
        try:
            import jsonschema
        except ImportError:
            self.skipTest("jsonschema is not installed")
        schema = json.loads((catalog.TOOLS / "content_catalog.schema.json").read_text(encoding="utf-8"))
        item_schema = {"$defs": schema["$defs"], **schema["properties"]["mesh"]["properties"]["hierarchy"]["items"]}
        validator = jsonschema.Draft202012Validator(item_schema)
        self.assertTrue(validator.is_valid({"ordinal": 0}))  # earlier v1 catalog
        good = {"partRecordSha256": "a" * 64, "partPayloadSha256": "b" * 64,
                "storedBounds": {"center": [0, None, 1], "halfExtents": [2, 3, 4],
                                 "validFlag": 1, "radius": 2}}
        self.assertTrue(validator.is_valid(good))
        self.assertFalse(validator.is_valid({**good, "partRecordSha256": "bad"}))
        self.assertFalse(validator.is_valid({**good, "storedBounds": {**good["storedBounds"], "center": [0, 1]}}))
        self.assertFalse(validator.is_valid({**good, "storedBounds": {**good["storedBounds"], "validFlag": 2**31}}))


class MeshChainCatalogTests(unittest.TestCase):
    def test_animation_offsets_point_to_each_camd_record_even_if_contents_repeat(self) -> None:
        clip = mesh_fixtures._catalog_animation("Walk")
        stream = mesh_fixtures._catalog_stream(animations=clip + clip, animation_count=2)
        [camd] = [c for c in catalog.aai.parse_top_level_chunks_bounded(stream) if c.tag == "CAMD"]
        _, animations, _ = catalog.catalog_mesh(stream, asset_id="mesh:authored", name="authored",
                                                container="authored.aya", container_sha="a" * 64,
                                                envelope="aya-zlib-members(cmsh)", offset=512, chunk_path=[])
        self.assertEqual([512 + camd.offset + 8, 512 + camd.offset + 8 + 36],
                         [a["source"]["offset"] for a in animations])
        self.assertEqual([36, 36], [a["source"]["length"] for a in animations])
        self.assertEqual([hashlib.sha256(clip).hexdigest()] * 2, [a["sha256"] for a in animations])

    def test_unparsed_root_counts_are_unknown_not_zero(self) -> None:
        record, _, _ = catalog.catalog_mesh(b"not a mesh", asset_id="mesh:authored", name="authored",
                                             container="authored.aya", container_sha="a" * 64,
                                             envelope="aya-zlib-members(cmsh)", offset=0, chunk_path=[])
        mesh = record["mesh"]
        self.assertEqual("unparsed", mesh["status"])
        for key in ("parts", "vertices", "stripPrimitives", "triangles", "skinnedParts", "boneParts",
                    "referenceParts", "partTypes", "lodChildren", "emitters"):
            with self.subTest(key=key):
                self.assertIsNone(mesh[key])
        self.assertTrue(mesh["reason"]["falsifier"])
        try:
            import jsonschema
        except ImportError:
            self.skipTest("jsonschema is not installed")
        schema = json.loads((catalog.TOOLS / "content_catalog.schema.json").read_text(encoding="utf-8"))
        self.assertTrue(jsonschema.Draft202012Validator(schema).is_valid({**record, catalog.GENERATED_MARKER: True}))

    def test_partial_mesh_keeps_unread_emitter_and_missing_chain_counts_unknown(self) -> None:
        broken_emitter = mesh_fixtures._catalog_stream(emitters=struct.pack("<I", 335), emitter_count=1)
        missing_child = mesh_fixtures._catalog_stream(next_marker=True)
        for stream, unknown_key in ((broken_emitter, "emitters"), (missing_child, "lodChildren")):
            with self.subTest(unknown_key=unknown_key):
                record, _, _ = catalog.catalog_mesh(stream, asset_id="mesh:authored", name="authored",
                                                     container="authored.aya", container_sha="a" * 64,
                                                     envelope="aya-zlib-members(cmsh)", offset=0, chunk_path=[])
                self.assertEqual("partial", record["mesh"]["status"])
                self.assertIsNone(record["mesh"][unknown_key])
                self.assertEqual(1, record["mesh"]["parts"])

    def test_loose_and_embedded_envelopes_select_their_own_chain_shape(self) -> None:
        child = mesh_fixtures._catalog_stream(name="Child")
        loose = mesh_fixtures._catalog_stream(lod=child, next_marker=True)
        embedded = mesh_fixtures._catalog_stream(
            lod=chunk(b"PMS2", bytes(309) + child), lod_tag=b"PMSH", next_marker=True)
        for stream, envelope, expected in ((loose, "aya-zlib-members(cmsh)", "parsed"),
                                            (embedded, "lvlr-chunk(MESH/PMSH/PMS2)", "parsed"),
                                            (loose, "lvlr-chunk(MESH/PMSH/PMS2)", "partial"),
                                            (embedded, "aya-zlib-members(cmsh)", "partial"),
                                            (loose, "unspecified", "partial")):
            with self.subTest(envelope=envelope, expected=expected):
                record, _, _ = catalog.catalog_mesh(stream, asset_id="mesh:authored", name="authored",
                                                     container="authored.aya", container_sha="a" * 64,
                                                     envelope=envelope, offset=0, chunk_path=[])
                self.assertEqual(expected, record["mesh"]["status"])
                self.assertEqual(1, record["mesh"]["lodChildren"])
                self.assertEqual([1], record["mesh"]["lodChildParts"])
                [detail] = record["mesh"]["nestedMeshDetails"]
                self.assertEqual("mesh-lod" if expected == "parsed" else "unresolved-nested-mesh",
                                 detail["relationship"])
                self.assertEqual(("parsed", 1, hashlib.sha256(child).hexdigest()),
                                 (detail["status"], detail["partCount"], detail["payloadSha256"]))
                self.assertIn("runtime loading not established", detail["scope"])
                self.assertEqual(expected != "parsed", detail["reason"] is not None)

    def test_catalog_retains_an_unparsed_nested_mesh_as_unknown(self) -> None:
        child = mesh_fixtures._catalog_stream(name="Child")[:-1]
        stream = mesh_fixtures._catalog_stream(lod=child, next_marker=True)
        record, _, _ = catalog.catalog_mesh(stream, asset_id="mesh:authored", name="authored",
                                             container="authored.aya", container_sha="a" * 64,
                                             envelope="aya-zlib-members(cmsh)", offset=0, chunk_path=[])
        [detail] = record["mesh"]["nestedMeshDetails"]
        self.assertEqual([None], record["mesh"]["lodChildParts"])
        self.assertEqual(("partial", "unresolved-nested-mesh", "unparsed", None),
                         (record["mesh"]["status"], detail["relationship"], detail["status"], detail["partCount"]))
        self.assertEqual(hashlib.sha256(child).hexdigest(), detail["payloadSha256"])
        self.assertEqual("nested CMSH did not parse", detail["reason"])


def ogg_file() -> bytes:
    ident = b"\x01vorbis" + struct.pack("<IBIiii", 0, 1, 44100, 0, 64000, 0) + b"\xb8\x01"
    page1 = b"OggS\x00\x02" + struct.pack("<qIII", 0, 9, 0, 0) + bytes([1, len(ident)]) + ident
    page2 = b"OggS\x00\x04" + struct.pack("<qIII", 44100, 9, 1, 0) + bytes([1, 2]) + b"xy"
    return page1 + page2


def bink_file() -> bytes:
    return b"BIKi" + struct.pack("<9I", 0, 75, 0, 0, 201, 149, 25, 1, 0) + struct.pack("<I", 0) + bytes(8)


# ------------------------------------------------------------------ phase 3: authored world body, ERES, SURF, SSHD
def lstr(text: str, fmt: str = "<b") -> bytes:
    return struct.pack(fmt, len(text)) + text.encode("ascii")


def script_symbol(name: str, dtype: int, value) -> bytes:
    out = lstr(name, "<i") + struct.pack("<i", dtype)
    if dtype == 3:
        out += lstr(value, "<i")
    elif dtype == 2:
        out += struct.pack("<f", value)
    elif dtype:
        out += struct.pack("<i", value)
    return out + struct.pack("<iii", 0, 0, 0)


def compiled_script(name: str) -> bytes:
    """SpawnThing("Tank", "Spawner", 1, "main"); PlayCharMessage(5, -6, 3.0) (a DWORD id stored as a signed int);
    FollowWaypoint("path a", 0);
    SetObjective(); GetThingRef("Tank 1"); one event function for "Go"."""
    symbols = [("s0", 3, "Tank"), ("s1", 3, "Spawner"), ("s2", 1, 1), ("s3", 3, "main"), ("s4", 1, 5), ("s5", 1, -6),
               ("s6", 2, 3.0), ("s7", 3, "path a"), ("s8", 1, 0), ("s9", 3, "Tank 1"), ("s10", 3, "Go")]
    push = lambda n: struct.pack("<ii", 5, n)
    call = lambda index, nargs: struct.pack("<ii", 24, index | nargs << 8)
    code = [push(0), push(1), push(2), push(3), call(3, 4), push(4), push(5), push(6), call(28, 3), push(7),
            push(8), call(0, 2), call(23, 0), push(9), call(14, 1)]
    body = struct.pack("<i", len(code)) + b"".join(code) + struct.pack("<13i", *([-1] * 13))
    body += struct.pack("<i", len(symbols)) + b"".join(script_symbol(*s) for s in symbols) + struct.pack("<i", 11)
    body += struct.pack("<iiii", 1, 0, 1, 10) + struct.pack("<ii", 0, 0)
    return lstr(name, "<i") + body + bytes(10)


def thing(oid: int, *, name: str = "", script: str = "", definition: str | None = None, extra: bytes = b"") -> bytes:
    init = struct.pack("<6f3i", 10.0, 20.0, 0.0, 0.0, 0.0, 0.0, 0, 1, -1)
    init += script.encode() + b"\0" + name.encode() + b"\0" + b"\0" + struct.pack("<ii", 1, 0)
    tail = (lstr(definition) + struct.pack("<i", -1)) if definition is not None else b""
    return struct.pack("<i", oid) + init + extra + tail


def world_body() -> bytes:
    things = [thing(8, name="Tank 1", script="main", definition="Tank"), thing(8, definition="Ghost"), thing(18),
              thing(18), thing(35, definition="Rock")]
    out = struct.pack("<H", 50) + struct.pack("<iii", 3, 0, 0) + struct.pack("<i", 1) + lstr("Paladin")
    out += struct.pack("<iii", 0, 0, 0) + struct.pack("<i", 0) + struct.pack("<i", -1)
    out += struct.pack("<i", 1) + compiled_script("main") + struct.pack("<i", -1) + struct.pack("<i", 0)
    out += struct.pack("<H", len(things)) + b"".join(things)
    out += struct.pack("<h", 0) + struct.pack("<i", 0) + struct.pack("<Hii", 0, 0, 0)
    out += struct.pack("<h", 1) + lstr("Path A") + struct.pack("<i", 3) + struct.pack("<3h", 1, 2, 0)
    out += struct.pack("<fffffiiffff", *([0.0] * 5), 1, 2, *([0.0] * 4))
    out += struct.pack("<3i", 0, 0, 0) + struct.pack("<f", 0.0)
    return out


def eres_payload() -> bytes:
    hdr = lambda tag, size=0: tag + struct.pack("<I", size)
    out = hdr(b"ENGN") + struct.pack("<i", 7)
    for _ in range(7):
        out += hdr(b"MTEX") + hdr(b"DATA") + struct.pack("<IiIhxxiii6i6i", 0, 0, 0, 3, 0, 0, 0, *([0] * 12))
    out += hdr(b"MAP ") + struct.pack("<i", 7) + hdr(b"HFLD") + hdr(b"DATA")
    hf = bytearray(0x13DC)
    struct.pack_into("<f", hf, 0x102C, 0.25)
    hf[0x1030] = 3
    hf[0x1078 + 0x18], hf[0x1078 + 0x1C], hf[0x1078 + 0x1D] = 2, 1, 4
    out += bytes(hf) + hdr(b"HGTS") + struct.pack("<h", 9) + bytes(64 * 64 * 81 * 2 - 2)
    out += hdr(b"MIXR") + (hdr(b"SLOT") + hdr(b"DATA") + bytes(0x14)) * 0x1000 + hdr(b"MMAP") + bytes(0x40000)
    return out


def surf_payload() -> bytes:
    return b"SURF" + struct.pack("<Ii", 0, 1) + b"STRP" + struct.pack("<Ii", 0, 1) + bytes(2 * 3 * 12)


def sshd_payload() -> bytes:
    hdr = lambda tag: tag + struct.pack("<I", 0)
    return (hdr(b"SHDS") + hdr(b"DATA") + struct.pack("<i", 1) + hdr(b"LIST") + hdr(b"SHAD")
            + struct.pack("<6i", 0, 0, 1, 1, 1, 9) + hdr(b"SMAP") + struct.pack("<5i", 0, 0, 1, 1, 1) + hdr(b"CELL")
            + struct.pack("<i", 1) + bytes(0x200))


def world_archive() -> bytes:
    wrld = chunk(b"WDAT", struct.pack("<ii", -1, 200)) + chunk(b"RLWD", world_body())
    return aya(chunk(b"LVLR", struct.pack("<I", 103)) + chunk(b"TARG", struct.pack("<I", 1))
               + chunk(b"AYAD", bytes(24)) + named_mesh_record("authored.msh")
               + text_record("cubes\\cube02_cent.tga", requested=0, levels=1)
               + text_record("mixers\\detail01.tga", requested=0, levels=-1)
               + text_record("hud\\speaker0.tga", requested=0, levels=1)
               + chunk(b"ERES", eres_payload()) + chunk(b"SURF", surf_payload()) + chunk(b"SSHD", sshd_payload())
               + chunk(b"LNDS", b"") + chunk(b"WRES", chunk(b"WRLD", wrld)))


def authored_install(root: Path) -> None:
    files = {
        "data/resources/dxtntextures/meshtex%skin.tga(0)A1R5G5B5.aya": aya(dds_dxt1_4x4()),
        "data/resources/dxtntextures/unused.tga(0)A1R5G5B5.aya": aya(dds_dxt1_4x4()),
        "data/resources/meshes/m_authored.msh.aya": aya(mesh_stream()),
        "data/resources/100_res_PC.aya": aya(
            chunk(b"LVLR", struct.pack("<I", 103)) + chunk(b"TARG", struct.pack("<I", 1))
            + chunk(b"AYAD", bytes(24)) + text_record("meshtex\\skin.tga") + named_mesh_record("authored.msh")
            + text_record("Particle\\spark.tga", requested=2, levels=1) + imposter_chunk()),
        "data/resources/goodie_03_res_PC.aya": goodie_archive(),
        "data/resources/dxtntextures/goodies%art.tga(0)A1R5G5B5.aya": aya(dds_dxt1_4x4()),
        "data/resources/dxtntextures/Particle%spark.tga(0)A1R5G5B5.aya": aya(dds_dxt1_4x4()),
        "data/resources/dxtntextures/Imposters_100(0)A1R5G5B5.aya": aya(dds_dxt1_4x4()),
        "data/ParticleSets/MainSet.par": PARTICLES.encode("latin-1"),
        "data/sounds/english/MessageBox/hello.ogg": ogg_file(),
        "data/video/briefings/PC_100_exact.vid": bink_file(),
        "data/MissionScripts/level100/main.msl": b"// authored\n",
        "data/MissionScripts/level200/main.msl": b"// authored\n",
        "data/resources/200_res_PC.aya": world_archive(),
        "data/default physics.dat": mesh_fixtures._physics_fixture(
            (1, "Tank", {8: struct.pack("<I", 3), 9: b"authored.msh\0"}), (8, "Rock", {2: b"authored.msh\0"})),
        "BEA.exe": b"authored stand-in, never executed\n",
    }
    for rel, data in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


class AuthoredInstallTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with tempfile.TemporaryDirectory() as temp, tempfile.TemporaryDirectory() as decomp_temp:
            game = Path(temp)
            authored_install(game)
            decomp = Path(decomp_temp)
            (decomp / "src").mkdir(parents=True)
            (decomp / "src" / "Hud.cpp").write_text(
                'void CHud::Init()\t// FUNCTION: 0x00401000\n{\n'
                '\tmTex = CDXTexture::FindTexture("Particle\\\\spark.tga", 2, 0, 1, 1, 1);\n'
                '\tmMesh = CMesh::GetMesh("authored.msh");\n}\n', encoding="latin-1")
            cls.catalog = catalog.build_catalog(game, decomp)
        cls.coverage = catalog.build_coverage(cls.catalog)
        cls.assets = {asset["id"]: asset for asset in cls.catalog["assets"]}

    def relation(self, asset_id: str, rtype: str) -> list[dict]:
        return [r for r in self.assets[asset_id]["relationships"] if r["type"] == rtype]

    def test_survey_classifies_every_file(self) -> None:
        survey = self.catalog["survey"]
        self.assertEqual(survey["unclassified"], [])
        counts = {f["family"]: f["files"] for f in survey["families"]}
        self.assertEqual(counts["dds-texture-dxtn"], 5)
        self.assertEqual(counts["mission-script-msl"], 2)
        self.assertEqual(counts["executable-code"], 1)

    def test_embedded_mesh_offset_comes_from_wrappers_not_a_duplicate_header(self) -> None:
        # The first 380 bytes also occur across the 309-byte resource header
        # and real CMSH. A byte search returns the decoy, not the framed body.
        leaf = mesh_fixtures._catalog_stream(name="Child")
        root = bytearray(mesh_fixtures._catalog_stream(
            name="", lod=chunk(b"PMS2", bytes(309) + leaf), lod_tag=b"PMSH", next_marker=True))
        root[48] = 1
        root[308:380] = root[:72]
        stream = bytes(root)
        prefix = b"\0" + stream[:308]
        payload = chunk(b"PMSH", chunk(b"PMS2", prefix + stream))
        self.assertEqual(17, payload.find(stream[:380]))
        self.assertEqual((stream, 325), catalog.meshcensus._direct_embedded_cmsh_with_offset(payload))
        intro = (chunk(b"LVLR", struct.pack("<I", 103)) + chunk(b"TARG", struct.pack("<I", 1))
                 + chunk(b"AYAD", bytes(24)))
        with tempfile.TemporaryDirectory() as temp:
            game = Path(temp)
            authored_install(game)
            archive = game / "data/resources/100_res_PC.aya"
            source = aya(intro + chunk(b"MESH", payload))
            archive.write_bytes(source)
            data = catalog.build_catalog(game)
            self.assertEqual(source, archive.read_bytes())
        [record] = [a for a in data["assets"] if a["id"] == "mesh:embedded:data/resources/100_res_pc.aya#3"]
        expected_offset = len(intro) + 8 + 325
        self.assertEqual(expected_offset, record["source"]["offset"])
        self.assertEqual(hashlib.sha256(stream).hexdigest(), record["sha256"])
        row, _ = catalog.meshcensus.mesh_record_from_stream(
            stream, source_path="data/resources/100_res_pc.aya", archive_sha256=hashlib.sha256(source).hexdigest(),
            payload_offset=expected_offset, chunk_path=(3,), source_context="embedded-mesh")
        edge = row["modelMetadata"]["lodChildren"][0]
        self.assertEqual(expected_offset + len(stream) - len(leaf), edge["model"]["identity"]["payloadOffset"])

    def test_text_record_resolves_to_its_loose_dds_by_the_loader_path_rule(self) -> None:
        [desc] = [a for a in self.catalog["assets"] if a["type"] == "texture-descriptor"
                  and a["name"] == "meshtex\\skin.tga"]
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

    def test_no_relationship_targets_an_absent_id(self) -> None:
        self.assertEqual(catalog.dangling_targets(self.catalog["assets"]), [])
        broken = [{"id": "a", "relationships": [{"target": "mesh:missing"}, {"target": None, "targets": ["a"]}]}]
        self.assertEqual(catalog.dangling_targets(broken), ["mesh:missing"])

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
        self.assertEqual(self.coverage["assetsByType"]["texture"], 5)
        self.assertEqual(self.coverage["textureFilesReferencedByADescriptor"], 4)
        self.assertEqual(self.coverage["textureFilesNotLoaded"],
                         ["data/resources/dxtntextures/unused.tga(0)A1R5G5B5.aya"])

    def test_imposter_texture_links_its_mesh_by_resource_id(self) -> None:
        [desc] = [a for a in self.catalog["assets"] if a["type"] == "texture-descriptor" and a["name"] == "Imposters_100"]
        [imp] = [r for r in desc["relationships"] if r["type"] == "imposter-of-mesh"]
        self.assertEqual((imp["status"], imp["target"]), ("resolved", "mesh:data/resources/meshes/m_authored.msh.aya"))
        self.assertEqual(desc["textureDescriptor"]["occurrences"][0]["via"], "IMPS")

    def test_goodie_image_shows_its_texture(self) -> None:
        goodie = self.assets["goodie:003"]
        self.assertEqual(goodie["goodie"]["goodieType"], "image")
        [shows] = self.relation("goodie:003", "shows-texture")
        desc = self.assets[shows["target"]]
        self.assertEqual(desc["name"], "goodies\\art.tga")
        self.assertIn(3, desc["usage"]["goodies"])

    def test_particle_texture_uses_blend_mode_plus_one_format(self) -> None:
        [effect] = [a for a in self.catalog["assets"] if a["type"] == "effect"]
        [uses] = effect["relationships"]
        self.assertEqual((uses["status"], uses["requestedFormat"], uses["targetName"]),
                         ("resolved", 2, "Particle\\spark.tga"))

    def test_code_literals_name_textures_and_meshes(self) -> None:
        refs = self.catalog["codeReferences"]
        self.assertEqual((refs["textureSites"], refs["meshSites"], refs["unresolvedTextureNames"]), (1, 1, []))
        mesh = self.assets["mesh:data/resources/meshes/m_authored.msh.aya"]
        self.assertEqual(mesh["usage"]["codeSites"], 1)
        [code] = [r for r in mesh["relationships"] if r["type"] == "named-by-code"]
        self.assertTrue(code["evidence"][0]["source"].endswith("src/Hud.cpp:4 CHud::Init @0x00401000"))

    # ---------------------------------------------------------------------------------------------- phase 3
    def test_world_things_take_loadworld_slots_and_split_into_placements_and_markers(self) -> None:
        placements = {a["name"]: a for a in self.catalog["assets"] if a["type"] == "placement"
                      and a["placement"]["level"] == 200}
        self.assertEqual(set(placements), {"Tank 1", "Ghost", "Rock"})
        self.assertEqual(placements["Tank 1"]["placement"]["slot"], 0)
        self.assertIsNone(placements["Ghost"]["placement"]["slot"])  # GetUnitData fails: no things[] slot
        self.assertEqual(placements["Rock"]["placement"]["slot"], 3)
        [inst] = [r for r in placements["Tank 1"]["relationships"] if r["type"] == "instance-of"]
        self.assertEqual((inst["status"], inst["target"]), ("resolved", "definition:tank"))
        [ghost] = [r for r in placements["Ghost"]["relationships"] if r["type"] == "instance-of"]
        self.assertEqual((ghost["status"], ghost["target"], ghost["targetName"]), ("unresolved", None, "Ghost"))
        markers = [a for a in self.catalog["assets"] if a["type"] == "marker"]
        self.assertEqual([m["marker"]["kind"] for m in markers], ["waypoint", "waypoint"])
        self.assertEqual([m["marker"]["slot"] for m in markers], [1, 2])

    def test_waypoint_path_keeps_only_waypoint_members_in_order(self) -> None:
        [path] = [a for a in self.catalog["assets"] if a["type"] == "waypoint-path"]
        self.assertEqual(path["name"], "Path A")
        self.assertEqual((path["waypointPath"]["members"], path["waypointPath"]["ignoredByLoader"]), (3, 1))
        members = [r for r in path["relationships"] if r["type"] == "path-member"]
        offsets = [self.assets[r["target"]]["source"]["offset"] for r in members]
        self.assertEqual([r["order"] for r in members], [0, 1])
        self.assertEqual(offsets, sorted(offsets))

    def test_compiled_script_literal_arguments_link_units_paths_scripts_and_things(self) -> None:
        sc = self.assets["script-code:200:rlwd#0"]
        code = sc["scriptCode"]
        self.assertEqual(code["units"], ["Tank"])
        self.assertEqual(code["textIds"], [5, 2**32 - 6])
        self.assertEqual(code["waypointPaths"], ["path a"])
        self.assertEqual([o["native"] for o in code["objectives"]], ["SetObjective"])
        self.assertEqual(code["handledEvents"], ["Go"])
        rel = {r["type"]: r for r in sc["relationships"]}
        self.assertEqual((rel["spawns-unit"]["status"], rel["spawns-unit"]["target"]), ("resolved", "definition:tank"))
        self.assertEqual((rel["sets-script"]["status"], rel["sets-script"]["target"]),
                         ("resolved", "script-code:200:rlwd#0"))
        self.assertEqual((rel["follows-path"]["status"], rel["follows-path"]["target"]),
                         ("resolved", "waypoint-path:200:rlwd#0"))  # _stricmp: "path a" finds "Path A"
        self.assertEqual(rel["names-thing"]["status"], "name-match")
        self.assertEqual(self.assets[rel["names-thing"]["target"]]["name"], "Tank 1")
        self.assertEqual((rel["compiled-from"]["status"], rel["compiled-from"]["target"]),
                         ("name-match", "script:data/missionscripts/level200/main.msl"))
        texts = [r for r in sc["relationships"] if r["type"] == "uses-text"]
        self.assertEqual(sorted((r["textId"], r["role"], r["status"]) for r in texts),
                         [(5, "text-speaker", "unresolved"), (2**32 - 6, "text", "unresolved")])  # no english.dat here

    def test_placement_runs_its_compiled_script_and_the_msl_lists_its_contents(self) -> None:
        [tank] = [a for a in self.catalog["assets"] if a["type"] == "placement" and a["name"] == "Tank 1"]
        [runs] = [r for r in tank["relationships"] if r["type"] == "runs-script"]
        self.assertEqual((runs["status"], runs["target"]), ("resolved", "script-code:200:rlwd#0"))
        msl = self.assets["script:data/missionscripts/level200/main.msl"]
        self.assertEqual([r["target"] for r in msl["relationships"] if r["type"] == "compiled-as"],
                         ["script-code:200:rlwd#0"])
        self.assertEqual(msl["file"]["compiled"]["units"], ["Tank"])
        self.assertEqual(msl["file"]["compiled"]["objectiveNatives"], ["SetObjective"])

    def test_level_payloads_decode_in_loader_order(self) -> None:
        decoded = {a["payload"]["tag"]: a["payload"] for a in self.catalog["assets"] if a["type"] == "level-payload"
                   and a["source"]["container"] == "data/resources/200_res_PC.aya"}
        self.assertEqual(decoded["ERES"]["decoded"]["status"], "decoded")
        self.assertEqual(decoded["SURF"]["decoded"]["strips"], 1)
        self.assertEqual(decoded["SURF"]["decoded"]["vertices"], 6)
        self.assertEqual((decoded["SSHD"]["decoded"]["shadows"], decoded["SSHD"]["decoded"]["cells"]), (1, 1))
        self.assertEqual(decoded["LNDS"]["decoded"]["status"], "skipped-by-pc-loader")
        terrain = self.assets["level:200"]["level"]["terrain"]
        hf = terrain["heightField"]
        self.assertEqual((hf["skyCube"], hf["mixerSet"], hf["detailMixer"], hf["water"]), (2, 3, 1, 4))
        self.assertEqual((hf["sampleCount"], hf["sampleMax"], hf["heightScale"]), (64 * 64 * 81, 9, 0.25))
        self.assertEqual(terrain["mapNumber"], 7)
        self.assertFalse(terrain["mixerTextureFiles"]["readFromDisk"])  # ERES already holds mixer set 3
        self.assertEqual(terrain["mixerTextureFiles"]["names"][0], "data\\textures\\mixers\\grass03.tga")
        self.assertEqual(self.assets["level:200"]["level"]["worlds"]["RLWD"]["thingsByKind"],
                         {"feature": 1, "unit": 2, "waypoint": 2})

    def test_sprintf_built_texture_names_resolve_by_the_format_rule(self) -> None:
        rules = {(r["role"], r["targetName"]): r for r in self.assets["level:200"]["relationships"]
                 if r["type"] == "texture-by-rule"}
        self.assertEqual(len(rules), 8)  # five sky-cube faces, reflection, caustic, detail
        self.assertEqual(rules[("sky-cube", "cubes\\cube02_cent.tga")]["status"], "resolved")
        self.assertEqual(rules[("sky-cube", "cubes\\cube02_up.tga")]["status"], "unresolved")
        self.assertEqual(rules[("terrain-detail", "mixers\\detail01.tga")]["status"], "resolved")
        self.assertEqual(rules[("water", "mixers\\reflection04.tga")]["status"], "unresolved")
        [speaker] = [a for a in self.catalog["assets"] if a["type"] == "texture-descriptor"
                     and a["name"] == "hud\\speaker0.tga"]
        [named] = [r for r in speaker["relationships"] if r["type"] == "named-by-code"]
        self.assertEqual((named["status"], named["role"]), ("code-rule", "hud-speaker"))
        self.assertIn("Hud.cpp", named["evidence"][0]["source"])

    def test_world_body_decoder_refuses_unread_bytes_and_unknown_things(self) -> None:
        physics = {"units": {"Tank"}, "features": {"Rock"}, "hazards": set(), "squadless": set()}
        self.assertEqual(len(worlddec.parse_world_body(world_body(), physics, base=False)["things"]), 5)
        with self.assertRaises(worlddec.DecodeError):
            worlddec.parse_world_body(world_body() + b"\0", physics, base=False)
        broken = world_body().replace(struct.pack("<i", 18), struct.pack("<i", 33), 1)  # a wall: SpawnThing NULL
        with self.assertRaises(worlddec.DecodeError):
            worlddec.parse_world_body(broken, physics, base=False)

    def test_object_code_reader_agrees_with_the_independent_record_inspector(self) -> None:
        record = compiled_script("main")
        code_bytes = record[8:-10]  # past the counted name, before LoadScripts' 10-byte pad
        reader = worlddec.Reader(code_bytes)
        code = worlddec.read_object_code(reader)
        self.assertEqual(reader.pos, len(code_bytes))
        sha = hashlib.sha256(code_bytes).hexdigest()
        report = inspector.inspect_script(code_bytes, source_sha256=sha, record_sha256=sha)
        self.assertEqual(report["status"], "complete")
        self.assertEqual(report["declaredInstructionCount"], len(code["instructions"]))
        self.assertEqual(len(report["symbols"]), len(code["symbols"]))
        self.assertEqual(len(report["eventFunctions"]), len(code["eventFunctions"]))


class BoundaryTests(unittest.TestCase):
    def test_self_test_passes(self) -> None:
        self.assertEqual(catalog.run_self_test(), 0)

    def test_generated_output_is_refused_by_the_public_safety_check(self) -> None:
        line = json.dumps({"id": "texture:x", catalog.GENERATED_MARKER: True})
        labels = {f.label for f in safety.content_signature_findings("notes/catalogue.jsonl", line)}
        self.assertIn("deny-generated-retail-catalogue", labels)
        labels = {f.label for f in safety.path_findings("local-data/content-catalog/assets.jsonl")}
        self.assertIn("deny-root", labels)


class TextureMipIdentityTests(unittest.TestCase):
    @staticmethod
    def dds(lower: bytes) -> bytes:
        # An authored two-level DXT1 texture: the top level has four blocks;
        # the 4x4 lower level has one. This fixture carries no game data.
        header = bytearray(dds_dxt1_4x4()[:128])
        struct.pack_into("<7I", header, 4, 124, 0xA1007, 8, 8, 32, 0, 2)
        struct.pack_into("<I", header, 108, 0x401008)
        return bytes(header) + b"TOP-MIP!" * 4 + lower

    def test_catalog_preserves_each_encoded_mip_identity_and_offset(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            game = Path(tmp)
            shelf = game / "data/resources/dxtntextures"
            shelf.mkdir(parents=True)
            first = self.dds(b"LOWER-1!")
            second = self.dds(b"LOWER-2!")
            paths = [shelf / "a.tga(0)A1R5G5B5.aya", shelf / "b.tga(0)A1R5G5B5.aya"]
            for path, data in zip(paths, (first, second)):
                path.write_bytes(aya(data))
            original = [path.read_bytes() for path in paths]
            files = [{"path": path.relative_to(game).as_posix(), "family": "dds-texture-dxtn"} for path in paths]
            records, _ = catalog.catalog_textures(game, files)
            repeated, _ = catalog.catalog_textures(game, files)
            self.assertEqual(records, repeated)
            mip0, mip1 = records[0]["texture"]["mips"]
            self.assertEqual(mip0, {"index": 0, "width": 8, "height": 8, "ddsOffset": 128, "length": 32,
                                    "sha256": hashlib.sha256(first[128:160]).hexdigest()})
            self.assertEqual(mip1, {"index": 1, "width": 4, "height": 4, "ddsOffset": 160, "length": 8,
                                    "sha256": hashlib.sha256(first[160:168]).hexdigest()})
            self.assertEqual(mip0["sha256"], records[1]["texture"]["mips"][0]["sha256"])
            self.assertNotEqual(mip1["sha256"], records[1]["texture"]["mips"][1]["sha256"])
            self.assertNotEqual(records[0]["sha256"], records[1]["sha256"])
            self.assertEqual([path.read_bytes() for path in paths], original)

    def test_malformed_dds_does_not_publish_partial_mip_identities(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            game = Path(tmp)
            path = game / "data/resources/dxtntextures/short.aya"
            path.parent.mkdir(parents=True)
            path.write_bytes(aya(self.dds(b"LOWER-1!")[:-1]))
            files = [{"path": path.relative_to(game).as_posix(), "family": "dds-texture-dxtn"}]
            [record], _ = catalog.catalog_textures(game, files)
            self.assertEqual(record["texture"]["status"], "malformed")
            self.assertEqual(record["texture"]["mips"], [])

    def test_raw_dds_header_fields_are_retained_without_guessing_original_art(self) -> None:
        rgba = bytearray(dds_dxt1_4x4()[:128])
        struct.pack_into("<7I", rgba, 4, 124, 0x100F, 1, 1, 4, 0, 0)
        struct.pack_into("<2I", rgba, 76, 32, 0x41)
        rgba[84:88] = b"\x13\x37\x00\xfe"  # raw bytes, unused when the fourCC flag is absent
        struct.pack_into("<5I", rgba, 88, 32, 0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000)
        struct.pack_into("<2I", rgba, 108, 0x1000, 0)
        rgba = bytes(rgba) + b"\x01\x02\x03\xff"
        dxt = self.dds(b"LOWER-1!")
        unsupported = dxt[:84] + b"DX10" + dxt[88:]
        with tempfile.TemporaryDirectory() as tmp:
            game = Path(tmp)
            shelf = game / "data/resources/dxtntextures"
            shelf.mkdir(parents=True)
            inputs = [("a.tga(0)A1R5G5B5.aya", dxt), ("b.tga(0)A8R8G8B8.aya", rgba),
                      ("short.aya", dxt[:-1]), ("unsupported.aya", unsupported), ("bad.aya", b"not a DDS")]
            for name, data in inputs:
                (shelf / name).write_bytes(aya(data))
            files = [{"path": (shelf / name).relative_to(game).as_posix(), "family": "dds-texture-dxtn"}
                     for name, _ in inputs]
            records, _ = catalog.catalog_textures(game, files)
            repeated, _ = catalog.catalog_textures(game, files)
        self.assertEqual(records, repeated)
        dxt_record, rgba_record, short, unsupported_record, bad = [r["texture"] for r in records]
        self.assertEqual(dxt_record["sourceFormatFromName"], "A1R5G5B5")
        self.assertEqual(dxt_record["storedFormat"], "DXT1")
        self.assertEqual(dxt_record["ddsHeader"], {
            "flags": 0xA1007, "pitchOrLinearSize": 32, "depth": 0, "declaredMipCount": 2,
            "caps1": 0x401008, "caps2": 0,
            "pixelFormat": {"flags": 4, "fourCCBytesHex": "44585431", "rgbBitCount": 0,
                            "rgbaMasks": [0, 0, 0, 0]},
        })
        self.assertEqual(rgba_record["status"], "valid")
        self.assertEqual(rgba_record["ddsHeader"]["pixelFormat"], {
            "flags": 0x41, "fourCCBytesHex": "133700fe", "rgbBitCount": 32,
            "rgbaMasks": [0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000],
        })
        self.assertEqual(short["status"], "malformed")
        self.assertEqual(short["ddsHeader"], dxt_record["ddsHeader"])
        self.assertEqual(short["mips"], [])
        self.assertEqual(unsupported_record["status"], "unsupported")
        self.assertEqual(unsupported_record["ddsHeader"]["pixelFormat"]["fourCCBytesHex"], "44583130")
        self.assertEqual(unsupported_record["mips"], [])
        self.assertIsNone(bad["ddsHeader"])
        self.assertFalse(any("authored for" in item for item in records[0]["upscale"]["suggestedTreatment"]))

    def test_header_schema_rejects_invalid_raw_fourcc_or_masks(self) -> None:
        try:
            import jsonschema
        except ImportError:
            self.skipTest("jsonschema is not installed")
        schema = json.loads((catalog.TOOLS / "content_catalog.schema.json").read_text(encoding="utf-8"))
        header = schema["properties"]["texture"]["properties"]["ddsHeader"]
        valid = {"flags": 1, "pitchOrLinearSize": 0, "depth": 0, "declaredMipCount": 0, "caps1": 0, "caps2": 0,
                 "pixelFormat": {"flags": 0, "fourCCBytesHex": "00000000", "rgbBitCount": 0,
                                 "rgbaMasks": [0, 0, 0, 0]}}
        validator = jsonschema.Draft202012Validator({"$defs": schema["$defs"], **header})
        self.assertTrue(validator.is_valid(valid))
        self.assertTrue(validator.is_valid(None))
        self.assertFalse(validator.is_valid({**valid, "pixelFormat": {**valid["pixelFormat"], "fourCCBytesHex": "bad"}}))
        self.assertFalse(validator.is_valid({**valid, "pixelFormat": {**valid["pixelFormat"], "fourCCBytesHex": "00000000\n"}}))
        self.assertFalse(validator.is_valid({**valid, "pixelFormat": {**valid["pixelFormat"], "rgbaMasks": [0, 0, -1, 0]}}))

    def test_schema_rejects_an_invalid_mip_hash(self) -> None:
        try:
            import jsonschema
        except ImportError:
            self.skipTest("jsonschema is not installed")
        schema = json.loads((catalog.TOOLS / "content_catalog.schema.json").read_text(encoding="utf-8"))
        mip_schema = schema["properties"]["texture"]["properties"]["mips"]["items"]
        # Resolve the same $defs used by the full asset schema.
        test_schema = {"$defs": schema["$defs"], **mip_schema}
        mip = {"index": 0, "width": 4, "height": 4, "ddsOffset": 128, "length": 8, "sha256": "bad"}
        self.assertFalse(jsonschema.Draft202012Validator(test_schema).is_valid(mip))


class TextureTreatmentSemanticsTests(unittest.TestCase):
    def test_alpha_association_is_the_admitted_format_convention_not_a_pixel_claim(self) -> None:
        for layout, expected in (("DXT1", None), ("DXT2", True), ("DXT3", False), ("DXT4", True), ("DXT5", False)):
            with self.subTest(layout=layout):
                meta = catalog.dds_census.texture_metadata(authored_dds(4, 4, fourcc=layout))
                self.assertEqual(meta["status"], "valid")
                upscale = catalog.texture_upscale(meta, None)
                self.assertIs(upscale["premultipliedAlpha"], expected)
                self.assertIs(upscale["compressed"], True)
                self.assertFalse(any("un-premultiply" in item for item in upscale["suggestedTreatment"]))
                if expected is True:
                    self.assertTrue(any("declares premultiplied alpha" in item for item in upscale["suggestedTreatment"]))
        for layout, payload in (("A1R5G5B5", bytes(2)), ("A8R8G8B8", bytes(4))):
            with self.subTest(layout=layout):
                meta = catalog.dds_census.texture_metadata(authored_rgb_dds(layout, 1, 1, payload))
                self.assertEqual(meta["status"], "valid")
                upscale = catalog.texture_upscale(meta, None)
                self.assertIsNone(upscale["premultipliedAlpha"])
                self.assertIs(upscale["compressed"], False)

    def test_rejected_formats_and_truncated_payloads_have_no_processing_recommendations(self) -> None:
        dxt1 = authored_dds(4, 4)
        cases = (("truncated DXT1", dxt1[:-1], "malformed"),
                 ("truncated DXT2", authored_dds(4, 4, fourcc="DXT2")[:-1], "malformed"),
                 ("DX10", dxt1[:84] + b"DX10" + dxt1[88:], "unsupported"),
                 ("unknown FourCC", dxt1[:84] + b"ZZZZ" + dxt1[88:], "unsupported"),
                 ("unsupported cube DXT4", authored_dds(4, 4, fourcc="DXT4")[:112]
                  + struct.pack("<I", 0x200) + authored_dds(4, 4, fourcc="DXT4")[116:], "unsupported"))
        for name, raw, status in cases:
            with self.subTest(case=name):
                meta = catalog.dds_census.texture_metadata(raw)
                self.assertEqual(meta["status"], status)
                upscale = catalog.texture_upscale(meta, "A1R5G5B5")
                self.assertIsNone(upscale["compressed"])
                self.assertIsNone(upscale["premultipliedAlpha"])
                self.assertEqual(upscale["alpha"], "unknown")
                self.assertEqual(upscale["mipLevels"], 0)
                self.assertEqual(upscale["suggestedTreatment"], [])

    def test_out_of_range_uv_does_not_recommend_processing_rejected_texture(self) -> None:
        meta = catalog.dds_census.texture_metadata(authored_dds(4, 4)[:-1])
        texture = {"id": "texture:test", "texture": {"status": meta["status"]},
                   "upscale": catalog.texture_upscale(meta, None)}
        desc = {"id": "desc:test", "relationships": [{"type": "pixels-from", "target": "texture:test"}]}
        mesh = {"id": "mesh:test", "relationships": [{"type": "uses-texture", "target": "desc:test", "slot": 0}],
                "mesh": {"textures": [{"slot": 0, "uvRange": [0., 0., 2., 2.]}]}}
        catalog.apply_tiling([mesh], [desc], [texture])
        self.assertEqual(texture["upscale"]["suggestedTreatment"], [])
        self.assertEqual(texture["upscale"]["tiling"]["uvRange"], [0., 0., 2., 2.])
        valid = catalog.dds_census.texture_metadata(authored_dds(4, 4))
        texture["texture"]["status"] = valid["status"]
        texture["upscale"] = catalog.texture_upscale(valid, None)
        catalog.apply_tiling([mesh], [desc], [texture])
        self.assertTrue(any("sampler address modes" in item for item in texture["upscale"]["suggestedTreatment"]))
        self.assertFalse(any("(wrap)" in item for item in texture["upscale"]["suggestedTreatment"]))

    def test_upscale_schema_admits_explicit_unknowns(self) -> None:
        try:
            import jsonschema
        except ImportError:
            self.skipTest("jsonschema is not installed")
        schema = json.loads((catalog.TOOLS / "content_catalog.schema.json").read_text(encoding="utf-8"))
        validator = jsonschema.Draft202012Validator({"$defs": schema["$defs"], **schema["properties"]["upscale"]})
        for raw in (authored_dds(4, 4)[:-1], authored_dds(4, 4, fourcc="DXT4"),
                    authored_rgb_dds("A8R8G8B8", 1, 1, bytes(4))):
            upscale = catalog.texture_upscale(catalog.dds_census.texture_metadata(raw), None)
            self.assertTrue(validator.is_valid(upscale), list(validator.iter_errors(upscale)))


if __name__ == "__main__":
    unittest.main()
