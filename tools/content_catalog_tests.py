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


if __name__ == "__main__":
    unittest.main()
