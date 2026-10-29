#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Authored world-body and level-archive vectors for the Companion's level data layer, and the reference dump they are
compared by.

The Companion's C# `WorldBody` and `LevelArchive` (companion/OnslaughtToolkit.Godot/Levels) are checked against this
Toolkit's Python reference (tools/world_resources_encode.py: read_world_model, write_world_body, level_worlds) on authored
data, never on game bytes. This script builds that data, reads every body with the reference, and writes
companion/OnslaughtToolkit.Godot/Tests/LevelVectors.g.cs:

- valid bodies, each with the reference dump of every field the reference reader read (a leaf per line, see dump_lines);
- bodies the reference refuses, each of which the C# reader must refuse;
- edits (move or rotate or rename a thing) with the bytes the reference writes after making the same edit;
- authored level archives with the level numbers and bodies the reference finds in them, and archives it refuses;
- mods the reference stager (tools/world_mod_stage.py) writes: the bytes of mod.json and the files of each folder, and the inputs it refuses.

    python tools/level_editor_vectors.py --check                  fail if the committed C# file is not what --write writes
    python tools/level_editor_vectors.py --write                  rewrite the C# file
    python tools/level_editor_vectors.py gate-table --game DIR --stdout
                                                                   one line per world body of an installed game: its size, its
                                                                   SHA-256 and the SHA-256 of its reference dump (hashes only;
                                                                   the local retail conformance gate reads it)

The dump is one `path = value` line per leaf of the reference model: integers in decimal, floats as the four stored bytes
in hex (`f32:0000803f`, so a NaN payload and a negative zero are compared exactly), strings in double quotes with every
byte outside printable ASCII written `\\xNN` (the bodies hold Latin-1), the byte regions the loader only skips as
`bytes(LENGTH):SHA256`. Lines are sorted; the dump's hash is the SHA-256 of the lines joined by newlines, with a final one.
"""
from __future__ import annotations

import sys

if __name__ == "__main__":
    sys.dont_write_bytecode = True

import argparse
import base64
import copy
from decimal import Decimal, localcontext
import hashlib
import json
import math
import re
import struct
import tempfile
import zlib
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))

import content_catalog_tests as fixtures  # noqa: E402  the hand-assembled authored body and archive
import world_mod_stage as stager  # noqa: E402
import heightfield_lookup as heights  # noqa: E402  the terrain lookup the C# Heightfield is checked against
import heightfield_lookup_tests as terrain_fixtures  # noqa: E402  the authored terrain chunk
import world_edit_move as mover  # noqa: E402  the move tool, whose coordinate reader the page's reader is checked against
import world_resources_decode as wrd  # noqa: E402
import world_resources_encode as enc  # noqa: E402

OUTPUT = ROOT / "companion/OnslaughtToolkit.Godot/Tests/LevelVectors.g.cs"
BLOB_HEX_KEYS = {"trailer"}
BLOB_B64_KEYS = {"nodeBytes", "linkBytes", "data"}
FULL_DUMP_LINES = 4000  # a longer dump is carried as its hash and line count only
READABLE_OIDS = sorted(wrd.SPAWNTHING_MAKES | enc.DEFINED)


# ------------------------------------------------------------------------------------------------------- the dump
def quote(text: str) -> str:
    out = ['"']
    for byte in text.encode("latin-1"):
        char = chr(byte)
        out.append(char if 0x20 <= byte <= 0x7E and char not in '"\\' else f"\\x{byte:02x}")
    out.append('"')
    return "".join(out)


def f32_hex(value) -> str:
    return enc.f32_out(value).hex()


def blob_line(path: str, data: bytes) -> str:
    return f"{path} = bytes({len(data)}):{hashlib.sha256(data).hexdigest()}"


def dump_lines(model: dict) -> list[str]:
    """The reference dump of a read_world_model model: one sorted `path = value` line per leaf."""
    lines: list[str] = []

    def walk(path: str, value, key: str | None = None) -> None:
        if isinstance(value, dict):
            if set(value) == {"f32bits"}:
                lines.append(f"{path} = f32:{value['f32bits'].lower()}")
                return
            for name, inner in value.items():
                if not path and name == "format":
                    continue
                walk(f"{path}.{name}" if path else name, inner, name)
        elif isinstance(value, list):
            for index, inner in enumerate(value):
                walk(f"{path}[{index}]", inner)
        elif value is None:
            lines.append(f"{path} = null")
        elif isinstance(value, str):
            if key in BLOB_HEX_KEYS:
                lines.append(blob_line(path, bytes.fromhex(value)))
            elif key in BLOB_B64_KEYS:
                lines.append(blob_line(path, enc.unblob(value)))
            else:
                lines.append(f"{path} = {quote(value)}")
        elif isinstance(value, bool):
            raise AssertionError(f"{path}: the model holds no booleans")
        elif isinstance(value, int):
            lines.append(f"{path} = {value}")
        elif isinstance(value, float):
            lines.append(f"{path} = f32:{f32_hex(value)}")
        else:
            raise AssertionError(f"{path}: unexpected {type(value)}")

    walk("", model)
    return sorted(lines)


def dump_hash(lines: list[str]) -> str:
    return hashlib.sha256(("\n".join(lines) + "\n").encode("ascii")).hexdigest()


# ------------------------------------------------------------------------------------------------------ builders
def authored_model() -> dict:
    """The hand-assembled authored body (tools/content_catalog_tests.py), read by the reference reader."""
    return enc.read_world_model(fixtures.world_body())


def patterned(size: int, seed: int) -> bytes:
    """Distinct bytes that repeat every 251 positions (a prime, so a shifted copy differs) and compress well."""
    cycle = bytes((seed * 31 + i * 7) & 0xFF for i in range(251))
    return (cycle * (size // 251 + 1))[:size]


def at_version(model: dict, version: int) -> dict:
    """The model rewritten at another world version: the fields LoadWorld reads only for that version."""
    out = copy.deepcopy(model)
    out["version"] = version
    for index, thing in enumerate(out["things"]):
        init = thing["init"]
        if version > 45:
            init.setdefault("attachScriptsToUnits", index % 3)
        else:
            init.pop("attachScriptsToUnits", None)
        if "spawner" in init:
            if version > 43:
                init["spawner"].setdefault("spawnerSpawnScript", "spawned")
            else:
                init["spawner"].pop("spawnerSpawnScript", None)
    if 45 <= version < 48:
        out["legacyTimings"] = [1, -2, 3, 0.5, 0.25]
    else:
        out.pop("legacyTimings", None)
    if version >= 47:
        out["occupancyGrids"] = [{"version": 1, "data": enc.blob(patterned(0x8000, 1))},
                                 {"version": 2, "data": enc.blob(patterned(0x2000, 2))}, {"version": 0, "data": ""}]
    else:
        out.pop("occupancyGrids", None)
    if 47 <= version < 50:
        out["legacyGridWords"] = [5, 4, -3, 2, 1]
    else:
        out.pop("legacyGridWords", None)
    if version >= 49:
        out["levelStartTime"] = 12.5
    else:
        out.pop("levelStartTime", None)
    return out


def make_thing(oid: int, index: int = 0, version: int = 50) -> dict:
    """A complete thing record of a kind, with distinctive field values."""
    cls = enc.thing_class(oid)
    init = {"position": [10.5 + index, 20.25 - index, -3.0], "orientation": [0.0, 1.5, -0.25], "meshNumber": index,
            "allegiance": 1 + index % 3, "target": -1 - index, "script": f"s{oid}", "name": f"{wrd.OID_NAMES.get(oid, 'x')}-{index}",
            "spawnScript": f"on{oid}" if oid % 2 else "", "active": index % 2}
    if version > 45:
        init["attachScriptsToUnits"] = index % 4
    if cls == "spawner":
        init["spawner"] = {"amount": 5, "delay": 1.5, "squadDelay": 2.5, "initialDelay": 0.125, "squadSize": 3,
                           "spawnUnit": "Tank"}
        if version > 43:
            init["spawner"]["spawnerSpawnScript"] = "spawned"
    elif cls == "squad":
        init["squad"] = {"amount": 4, "mode": 2}
    elif cls == "cutscene":
        init["cutscene"] = {"file": "intro", "linkTo": "next"}
    elif cls == "start":
        init["start"] = {"planeMode": 1, "playerNumber": 0 if oid == 15 else 1}
    elif cls == "tree":
        init["tree"] = {"treeType": "pine"}
    elif cls == "sphere-trigger":
        init["sphereTrigger"] = {"radius": 37.5}
    thing = {"oid": oid, "kind": wrd.OID_NAMES.get(oid, f"oid-{oid}"), "init": init}
    if oid in enc.DEFINED:
        thing["definition"] = ["Tank", "Rock", "Squad", "Hut", "Mine"][oid % 5]
        thing["diesOn"] = -1 if oid % 2 else 7
    return thing


def empty_model(version: int = 50) -> dict:
    model = {"format": enc.MODEL_FORMAT, "version": version,
             "header": {"headerVersion": 0, "unused": [0, 0], "battleEngineConfigurations": []}, "baseLevel": 0, "scripts": [],
             "mapNumber": 0, "namedMeshes": [], "things": [], "treeGroups": [], "treeTypes": [],
             "influenceMap": {"version": 0, "nodes": 0, "nodeBytes": "", "links": 0, "linkBytes": ""}, "waypointPaths": [],
             "timings": {"oldF": 0.0, "oldG": 0.0, "oldH": 0.0, "preRun": 0.0, "pan": 0.0, "sGrade": 0, "dGrade": 0,
                         "timeLimit": 0.0, "fullScoreTime": 0.0, "percentageScoreTime": 0.0, "scorePercentage": 0.0}}
    return at_version(model, version)


def rich_script(name: str) -> dict:
    """A script that uses every symbol data type, an event function with parameters and distinctive words everywhere."""
    symbols = [
        {"name": "none", "dataType": 0, "value": None, "symbolType": 1, "index": 0, "flag": 0},
        {"name": "count", "dataType": 1, "value": -42, "symbolType": 2, "index": 1, "flag": 1},
        {"name": "ratio", "dataType": 2, "value": 0.75, "symbolType": 3, "index": 2, "flag": 0},
        {"name": "label", "dataType": 3, "value": "a label", "symbolType": 4, "index": 3, "flag": 0},
        {"name": "switch", "dataType": 4, "value": 7, "symbolType": 5, "index": 4, "flag": 1},
        {"name": "thing", "dataType": 5, "value": 12, "symbolType": 6, "index": 5, "flag": 0},
        {"name": "where", "dataType": 6, "value": [1.5, -2.5, 3.25], "symbolType": 7, "index": 6, "flag": 0},
        {"name": "", "dataType": 3, "value": "", "symbolType": 0, "index": -1, "flag": -1},
    ]
    return {"name": name,
            "code": {"instructions": [[5, 0], [5, 1], [24, 515], [23, 0], [0, 0]],
                     "eventPCs": [-1, 0, 2, -1, 4, -1, -1, -1, 3, -1, -1, -1, 1], "symbols": symbols, "nextSymbolIndex": 9,
                     "eventFunctions": [{"entryPC": 0, "params": [1, 2, 3]}, {"entryPC": 3, "params": []}],
                     "tail": [-5, 6]},
            "trailer": bytes(range(10, 20)).hex()}


# --------------------------------------------------------------------------------------------- the valid vectors
def valid_vectors() -> list[tuple[str, str, dict | bytes]]:
    """(name, note, model or raw body): a model is written with the reference writer, a body is used as it is."""
    out: list[tuple[str, str, dict | bytes]] = []
    base = authored_model()
    out.append(("authored-v50", "the hand-assembled authored body, as the reference reads it", fixtures.world_body()))
    for version in range(43, 50):
        out.append((f"authored-v{version}", f"the authored body at world version {version}", at_version(base, version)))
    for version in (43, 44, 45, 46, 47, 49, 50):
        model = at_version(base, version)
        model["things"] = [make_thing(oid, index, version) for index, oid in enumerate(READABLE_OIDS)]
        out.append((f"kinds-v{version}", f"one record of every readable object id at version {version}", model))

    for header_version in (0, 1, 2, 3):
        model = at_version(base, 50)
        header = model["header"]
        header["headerVersion"] = header_version
        header["unused"] = [-1, 2 ** 31 - 1]
        header["battleEngineConfigurations"] = ["", "Paladin", "x" * 127, "Warspite"]
        header.pop("v2Words", None)
        header.pop("worldType", None)
        if header_version >= 2:
            header["v2Words"] = [11, -12, 13]
        if header_version >= 3:
            header["worldType"] = -9
        model["baseLevel"] = 100
        model["mapNumber"] = -2
        out.append((f"header-{header_version}", f"header version {header_version} with its fields and long names", model))

    model = at_version(base, 50)
    model["scripts"] = [rich_script("first"), {"name": "", "code": {"instructions": [], "eventPCs": [-1] * 13, "symbols": [],
                                                                    "nextSymbolIndex": 0, "eventFunctions": [], "tail": [0, 0]},
                                              "trailer": "00" * 10}, rich_script("x" * 300)]
    out.append(("scripts-rich", "scripts using every symbol data type, an event function with parameters, an empty script", model))

    model = at_version(base, 50)
    model["treeGroups"] = [{"y0": 1.5, "x0": 2.5, "y1": 3.5, "x1": 4.5, "count": 9, "treeType": "pine", "seed": 77},
                           {"y0": -1.0, "x0": -2.0, "y1": 100.0, "x1": 200.0, "count": 0, "treeType": "", "seed": -1}]
    model["treeTypes"] = [{"name": "pine", "positions": [[1.5, 2.5, 3], [4.5, 5.5, -6]]}, {"name": "oak", "positions": []}]
    model["namedMeshes"] = ["", "a.msh", "m" * 255]
    out.append(("trees-meshes", "tree groups and types and named meshes, including an empty and a 255-byte name", model))

    for version in (0, 1):
        model = at_version(base, 50)
        nodes, links = (3, 2) if version == 0 else (2, 3)
        model["influenceMap"] = {"version": version, "nodes": nodes,
                                 "nodeBytes": enc.blob(patterned(nodes * enc_node(version), 3)), "links": links,
                                 "linkBytes": enc.blob(patterned(links * enc_link(version), 4))}
        out.append((f"influence-v{version}", f"influence map version {version} with nodes and links", model))

    model = at_version(base, 50)
    model["waypointPaths"] = [{"name": "route", "slots": [0, 1, 2, -1, 32767, -32768]}, {"name": "", "slots": []},
                              {"name": "long " * 20, "slots": [3]}]
    model["timings"] = {"oldF": 1.25, "oldG": -2.5, "oldH": 3.75, "preRun": 4.0, "pan": 5.5, "sGrade": -6, "dGrade": 7,
                        "timeLimit": 600.0, "fullScoreTime": 300.5, "percentageScoreTime": 450.25, "scorePercentage": 0.5}
    out.append(("paths-timings", "waypoint paths with negative and extreme slots, and distinctive timings", model))

    model = at_version(base, 50)
    nan_quiet, nan_payload, nan_signaling = {"f32bits": "0000c07f"}, {"f32bits": "0100c07f"}, {"f32bits": "0000a07f"}
    inf_pos, inf_neg = {"f32bits": "0000807f"}, {"f32bits": "000080ff"}
    model["things"][0]["init"]["position"] = [nan_quiet, inf_pos, inf_neg]
    model["things"][0]["init"]["orientation"] = [nan_payload, nan_signaling, -0.0]
    model["things"][1]["init"]["position"] = [1.401298464324817e-45, 3.4028234663852886e+38, -3.4028234663852886e+38]
    model["timings"]["pan"] = nan_signaling
    model["timings"]["timeLimit"] = inf_neg
    model["scripts"][0]["code"]["symbols"][6]["value"] = nan_payload  # s6 is the authored script's float symbol
    model["levelStartTime"] = -0.0
    out.append(("special-floats", "NaN payloads, infinities, negative zero, the smallest denormal and the largest float", model))

    model = at_version(base, 50)
    model["things"][0]["init"]["name"] = "".join(chr(c) for c in range(0x80, 0x80 + 60))
    model["things"][0]["init"]["script"] = "s" * 255
    model["things"][0]["definition"] = "".join(chr(0x80 + i * 5 % 128) for i in range(127))
    model["things"][1]["init"]["name"] = ""
    model["header"]["battleEngineConfigurations"] = ["\xe9\xff\x80"]
    out.append(("strings-latin1", "bytes above 0x7F, an empty string and the longest strings the length fields hold", model))

    model = at_version(base, 50)
    model["things"] = [make_thing(8 if i % 3 else 18, i) for i in range(1000)]
    out.append(("things-1000", "the thing array's full 1000 records", model))

    out.append(("empty-v50", "a body with no scripts, things, trees or paths", empty_model(50)))
    out.append(("empty-v43", "a body with no scripts, things, trees or paths at version 43", empty_model(43)))
    return out


def enc_node(version: int) -> int:
    return 12 if version == 0 else 16


def enc_link(version: int) -> int:
    return 8 if version == 0 else 12


# -------------------------------------------------------------------------------------------- the refused vectors
PHYSICS = {"units": {"Tank"}, "features": {"Rock"}, "hazards": set(), "squadless": set()}


def refused_vectors(valid: dict[str, bytes]) -> list[tuple[str, str, bytes]]:
    """Bodies the reference refuses. Each is a valid body with one thing wrong (so that a reader which stopped checking that
    one thing would accept it, rather than refuse it further on for another reason)."""
    base, v43, empty, rich = valid["authored-v50"], valid["authored-v43"], valid["empty-v50"], valid["scripts-rich"]
    parsed = wrd.parse_world_body(base, PHYSICS, base=False)
    first, waypoint, last = parsed["things"][0], parsed["things"][2], parsed["things"][-1]
    assert waypoint["oid"] == 18
    script_at = parsed["scripts"][0]["offset"]
    tree_groups_at = last["offset"] + last["length"]
    influence_at = tree_groups_at + 2 + 4  # past the tree group and tree type counts
    name_at = first["offset"] + 4 + 6 * 4 + 3 * 4  # the first thing's script string, past its object id, six floats and three words
    none_symbol = struct.pack("<i", 4) + b"none" + struct.pack("<i", 0)  # a symbol with no value: its data type follows its name
    rich_dtype_at = rich.index(none_symbol) + 8
    empty_paths_at = 52  # the empty body: version, header, counts, influence map; the waypoint path count follows
    assert struct.unpack_from("<h", empty, empty_paths_at) == (0,) and struct.unpack_from("<i", empty, 14) == (0,)
    config_at = base.index(b"\x07Paladin")
    out: list[tuple[str, str, bytes]] = []

    def patched(body: bytes, at: int, data: bytes) -> bytes:
        return body[:at] + data + body[at + len(data):]

    out.append(("empty-input", "no bytes", b""))
    out.append(("version-42", "a version 43 body that says 42", patched(v43, 0, struct.pack("<H", 42))))
    out.append(("version-51", "a version 50 body that says 51", patched(base, 0, struct.pack("<H", 51))))
    out.append(("trailing-byte", "one byte after the last field", base + b"\0"))
    out.append(("config-count-negative", "a negative battle-engine configuration count", patched(empty, 14, struct.pack("<i", -1))))
    over = (1 << 20) + 1  # one more empty string than the framing limit: the count is the only thing wrong
    out.append(("config-count-over-limit", "a count one above the framing limit, followed by that many empty strings",
                empty[:14] + struct.pack("<i", over) + b"\0" * over + empty[18:]))
    out.append(("config-count-huge", "a count at the limit that passes the end of the body", patched(empty, 14, struct.pack("<i", 1 << 20))))
    out.append(("unknown-oid", "a waypoint with an object id SpawnThing does not make", patched(base, waypoint["offset"], struct.pack("<i", 99))))
    out.append(("wall-oid", "a waypoint with the wall's object id, which LoadWorld does not read", patched(base, waypoint["offset"], struct.pack("<i", 33))))
    out.append(("influence-version-2", "an influence map version other than 0 or 1", patched(base, influence_at, struct.pack("<H", 2))))
    out.append(("script-dtype-unknown", "a script symbol with no value and an unknown data type", patched(rich, rich_dtype_at, struct.pack("<i", 9))))
    out.append(("script-dtype-negative", "a script symbol with no value and a negative data type", patched(rich, rich_dtype_at, struct.pack("<i", -1))))
    out.append(("script-name-negative", "a negative script name length", patched(base, script_at, struct.pack("<i", -1))))
    out.append(("cstring-unterminated", "a thing's script string with no NUL for 300 bytes", base[:name_at] + b"A" * 300 + base[name_at + 5:]))
    out.append(("cstring-256", "a thing's script string of 256 characters, one more than the loader's loop reads",
                base[:name_at] + b"A" * 256 + b"\0" + base[name_at + 5:]))
    out.append(("lstring-negative", "a signed-byte string length of -128 (128 bytes follow, so an unsigned length would read them)",
                base[:config_at] + b"\x80" + b"x" * 128 + base[config_at + 1 + 7:]))
    out.append(("tree-group-count-negative", "a negative tree group count", patched(base, tree_groups_at, struct.pack("<h", -1))))
    out.append(("path-count-negative", "a negative waypoint path count", patched(empty, empty_paths_at, struct.pack("<h", -1))))
    out.append(("grid-short", "a body that ends inside the last grid words", base[:-6]))
    return out


# ------------------------------------------------------------------------------------------------- edit vectors
def edit_vectors(models: dict[str, dict]) -> list[tuple[str, str, list[tuple], dict]]:
    """(name, from vector, steps, edited model): the same steps are applied to the C# model and compared byte for byte."""
    specs = [
        ("move-v50", "authored-v50", [("move", 0, 12.5, -40.0, 3.0)]),
        ("move-two-v50", "authored-v50", [("move", 2, 100.0, 200.0, -10.5), ("move", 4, 0.0, 0.0, 0.0)]),
        ("rotate-v50", "authored-v50", [("rotate", 1, 0.5, 1.5, -2.5)]),
        ("rename-v50", "authored-v50", [("rename", 0, "A much longer name than the old one")]),
        ("move-v43", "authored-v43", [("move", 0, 12.5, -40.0, 3.0)]),
        ("move-v47", "authored-v47", [("move", 3, 1.0, 2.0, 3.0)]),
        ("move-kinds-v50", "kinds-v50", [("move", 5, -1.5, 2.5, -3.5), ("rename", 9, ""), ("rotate", 17, 1.0, 2.0, 3.0)]),
        ("move-negative-zero", "authored-v50", [("move", 0, -0.0, -0.0, -0.0)]),
    ]
    out = []
    for name, source, steps in specs:
        model = copy.deepcopy(models[source])
        for step in steps:
            op, index = step[0], step[1]
            init = model["things"][index]["init"]
            if op == "move":
                init["position"] = [step[2], step[3], step[4]]
            elif op == "rotate":
                init["orientation"] = [step[2], step[3], step[4]]
            elif op == "rename":
                init["name"] = step[2]
            else:
                raise AssertionError(op)
        out.append((name, source, steps, model))
    return out


# ------------------------------------------------------------------------------------------------- archives
def archive_file(parts: list[bytes]) -> bytes:
    return b"".join(fixtures.aya(part) for part in parts)


def framed_member(member: bytes) -> bytes:
    """A packed member as the file holds it: its length, then its bytes."""
    return struct.pack("<I", len(member)) + member


def needs_dictionary(stream: bytes) -> bytes:
    """A zlib stream whose header sets FDICT: it can only be inflated with the preset dictionary its checksum names."""
    packer = zlib.compressobj(6, zlib.DEFLATED, 15, 8, zlib.Z_DEFAULT_STRATEGY, b"a dictionary the archive does not carry")
    return packer.compress(stream) + packer.flush()


def split(data: bytes, count: int) -> list[bytes]:
    """The stream in count pieces: one byte each, and the rest in the last."""
    return [data[i:i + 1] for i in range(count - 1)] + [data[count - 1:]]


def level_stream(wdat: bytes | None, bodies: list[tuple[bytes, bytes]], terrain: bytes | None = None, later_eres: bytes | None = None) -> bytes:
    """The authored level stream; its ERES chunk is 40 zero bytes (not a terrain) unless `terrain` gives one, and `later_eres` adds a second."""
    wrld = (fixtures.chunk(b"WDAT", wdat) if wdat is not None else b"") + b"".join(fixtures.chunk(tag, body) for tag, body in bodies)
    return (fixtures.chunk(b"LVLR", struct.pack("<I", 103)) + fixtures.chunk(b"TARG", struct.pack("<I", 1))
            + fixtures.chunk(b"AYAD", bytes(24)) + fixtures.chunk(b"ERES", terrain if terrain is not None else b"\0" * 40)
            + (fixtures.chunk(b"ERES", later_eres) if later_eres is not None else b"")
            + fixtures.chunk(b"WRES", fixtures.chunk(b"WRLD", wrld)) + fixtures.chunk(b"LNDS", b""))


def padded_level_stream(total: int, real: bytes) -> bytes:
    """A level stream of exactly `total` bytes: an unused chunk (before the trailing LNDS chunk) takes up the difference."""
    stream = level_stream(struct.pack("<ii", -1, 400), [(b"RLWD", real)])
    padding = total - len(stream) - 8
    assert padding >= 0, "the stream is longer than the size asked for"
    return stream[:-8] + fixtures.chunk(b"PADD", bytes(padding)) + stream[-8:]


def stored_member(compressed_len: int, data_len: int, real: bytes) -> bytes:
    """One member of exactly `compressed_len` bytes that inflates to the `data_len`-byte padded level stream: a zlib stream of stored
    blocks (2 header bytes, 5 bytes of overhead per block, the data, 4 checksum bytes), the blocks of near equal size. It reaches the
    game's pack buffer, which no zlib-compressed member of an authored level does."""
    blocks, rest = divmod(compressed_len - 6 - data_len, 5)
    assert rest == 0 and blocks >= 1 and data_len <= enc.MAX_INFLATED_MEMBER_BYTES, (compressed_len, data_len)
    data = padded_level_stream(data_len, real)
    out = bytearray(b"\x78\x01")
    at = 0
    for index in range(blocks):
        size = data_len // blocks + (1 if index < data_len % blocks else 0)
        assert 0 < size <= 0xFFFF
        out += bytes([1 if index == blocks - 1 else 0]) + struct.pack("<HH", size, size ^ 0xFFFF) + data[at:at + size]
        at += size
    out += struct.pack(">I", zlib.adler32(data))
    assert at == data_len and len(out) == compressed_len
    return bytes(out)


def stored_pack_buffer_member(delta: int, real: bytes) -> bytes:
    """A stored-block member of PACK_BUFFER_SIZE + delta compressed bytes, inflating to as much as the 1 MiB bound allows."""
    target = enc.PACK_BUFFER_SIZE + delta
    data_len = enc.MAX_INFLATED_MEMBER_BYTES - (enc.MAX_INFLATED_MEMBER_BYTES - (target - 6)) % 5
    return stored_member(target, data_len, real)


def cut_short_member(stream: bytes) -> bytes:
    """A zlib stream that inflates to exactly `stream` but never ends, and whose last four bytes are the Adler-32 of what it
    inflates to: a stored block holding the stream, then the checksum where a complete stream would end after its last block.
    A reader that takes "the last four bytes are the checksum" for "the stream is complete" accepts it. The checksum's own first
    byte starts the next block header, so a stream is only left waiting for input (not broken) when that byte is a stored block's:
    the stream is padded, a byte at a time, until it is."""
    for pad in range(64):
        data = stream[:-8] + fixtures.chunk(b"PADD", bytes(pad)) + stream[-8:] if pad else stream
        assert len(data) <= 0xFFFF, "a stored block holds at most 65535 bytes"
        member = b"\x78\x01" + b"\x00" + struct.pack("<HH", len(data), len(data) ^ 0xFFFF) + data + struct.pack(">I", zlib.adler32(data))
        decoder = zlib.decompressobj()
        try:
            inflated = decoder.decompress(member)
        except zlib.error:
            continue
        if inflated == data and not decoder.eof:
            return member
    raise AssertionError("no padding leaves the cut-short stream waiting for input")


def archive_vectors(valid: dict[str, bytes]) -> list[tuple[str, str, bytes, dict]]:
    real, base = valid["authored-v50"], valid["kinds-v46"]
    out: list[tuple[str, str, bytes, dict]] = []
    one = level_stream(struct.pack("<ii", -1, 200), [(b"RLWD", real)])
    out.append(("real-only", "one member, the level's own world only", archive_file([one])))
    out.append(("level-100", "a level that names itself as its world's level, as the level editor's tests need",
                archive_file([level_stream(struct.pack("<ii", -1, 100), [(b"RLWD", real)])])))
    terrain_stream = level_stream(struct.pack("<ii", -1, 100), [(b"RLWD", real)], terrain=authored_terrain().eres)
    third = len(terrain_stream) // 3 + 1
    out.append(("level-100-terrain", "a level 100 whose ERES chunk is the authored terrain, split over three members under the 1 MiB bound",
                archive_file([terrain_stream[i:i + third] for i in range(0, len(terrain_stream), third)])))
    two_terrains = level_stream(struct.pack("<ii", -1, 100), [(b"RLWD", real)], terrain=authored_terrain().eres, later_eres=b"\0" * 40)
    third_two = len(two_terrains) // 3 + 1
    out.append(("level-100-two-terrains", "a level 100 with two top-level ERES chunks, the authored terrain and then 40 zero bytes, split over three members: the reader keeps the first",
                archive_file([two_terrains[i:i + third_two] for i in range(0, len(two_terrains), third_two)])))
    two = level_stream(struct.pack("<ii", 100, 200), [(b"BSWD", base), (b"RLWD", real)])
    out.append(("base-and-real", "a base world and a real world", archive_file([two])))
    third = len(two) // 3
    out.append(("three-members", "the same stream split over three members", archive_file([two[:third], two[third:2 * third], two[2 * third:]])))
    catalogue = zlib.decompress(fixtures.world_archive()[4:])  # the catalogue tests' authored level: 1.1 MB inflated, one member
    cuts = list(range(0, len(catalogue), 400_000)) + [len(catalogue)]
    out.append(("catalogue-archive-split", "the catalogue tests' authored level archive re-split into members under the 1 MiB bound",
                archive_file([catalogue[a:b] for a, b in zip(cuts, cuts[1:])])))
    out.append(("wdat-longer", "a WDAT chunk longer than its two words",
                archive_file([level_stream(struct.pack("<iii", 7, 8, 9), [(b"RLWD", real)])])))
    wrld = (fixtures.chunk(b"ZZZZ", b"abc") + fixtures.chunk(b"WDAT", struct.pack("<ii", -1, 300)) + fixtures.chunk(b"YYYY", b"")
            + fixtures.chunk(b"RLWD", real))
    out.append(("other-chunks", "chunks the reader does not use before and inside the world",
                archive_file([fixtures.chunk(b"LVLR", struct.pack("<I", 103)) + fixtures.chunk(b"WRES", fixtures.chunk(b"PAD0", b"12345")
                                                                                              + fixtures.chunk(b"WRLD", wrld))])))
    stream = level_stream(struct.pack("<ii", -1, 400), [(b"RLWD", real)])
    stream = stream[:-8] + fixtures.chunk(b"PADD", bytes(6000)) + stream[-8:]  # before the trailing LNDS chunk
    out.append(("members-4096", "a stream split into 4096 members, the most the reader accepts", archive_file(split(stream, 4096))))
    out.append(("member-exactly-1mib", "one member that inflates to exactly the 1 MiB a member may",
                archive_file([padded_level_stream(enc.MAX_INFLATED_MEMBER_BYTES, real)])))
    out.append(("member-exactly-pack-buffer", "one member of exactly the pack buffer's compressed bytes (stored blocks), the most the reader accepts",
                framed_member(stored_pack_buffer_member(0, real))))
    out.append(("member-one-under-pack-buffer", "one member of one byte fewer than the pack buffer (stored blocks)",
                framed_member(stored_pack_buffer_member(-1, real))))
    results = []
    for name, note, data in out:
        worlds = enc.level_worlds(b"".join(enc.inflate(enc.read_members(data))))
        results.append((name, note, data, {"baseLevel": worlds["baseLevel"], "realLevel": worlds["realLevel"],
                                           "bodies": {tag: hashlib.sha256(body).hexdigest() for tag, body in worlds["bodies"].items()}}))
    return results


def refused_archives(valid: dict[str, bytes]) -> list[tuple[str, str, bytes]]:
    real = valid["authored-v50"]
    good = level_stream(struct.pack("<ii", -1, 200), [(b"RLWD", real)])
    no_wres = fixtures.chunk(b"LVLR", struct.pack("<I", 103)) + fixtures.chunk(b"WXXX", b"\0" * 8)
    no_wrld = fixtures.chunk(b"WRES", fixtures.chunk(b"XXXX", b"\0" * 8))
    truncated_header = fixtures.chunk(b"LVLR", struct.pack("<I", 103)) + b"WRE" + b"\0" * 2  # five bytes where a chunk header begins
    wrld = fixtures.chunk(b"WDAT", struct.pack("<ii", -1, 200)) + fixtures.chunk(b"RLWD", real) + struct.pack("<4sI", b"XXXX", 1 << 20) + b"\0" * 16
    overrun = fixtures.chunk(b"WRES", fixtures.chunk(b"WRLD", wrld))  # a chunk inside the world that claims more than the world holds
    short_wdat = level_stream(b"\0" * 4, [(b"RLWD", real)])
    no_wdat = level_stream(None, [(b"RLWD", real)])
    member = zlib.compress(good)
    adler = member[-4:]  # the stream's own Adler-32, big-endian: the last four bytes of every complete zlib stream
    framed = lambda body: struct.pack("<I", len(body)) + body
    return [
        ("no-bytes", "an empty file", b""),
        ("length-only", "a file that ends inside a member length", b"\x05\x00"),
        ("zero-member", "a member of length zero", struct.pack("<I", 0)),
        ("member-overruns", "a member length past the end of the file", struct.pack("<I", len(member) + 1) + member),
        ("not-zlib", "a member that is not a zlib stream", struct.pack("<I", 8) + b"notzlib!"),
        ("member-truncated", "a zlib stream cut short", struct.pack("<I", len(member) - 5) + member[:-5]),
        ("member-trailing-data", "bytes after the end of a zlib stream", struct.pack("<I", len(member) + 4) + member + b"junk"),
        ("member-adler-repeated", "a complete zlib stream followed by a second copy of its own Adler-32", framed(member + adler)),
        ("member-adler-after-gap", "a complete zlib stream, four zero bytes and a second copy of its own Adler-32", framed(member + bytes(4) + adler)),
        ("member-adler-after-junk", "a complete zlib stream, four bytes of junk and a second copy of its own Adler-32", framed(member + b"junk" + adler)),
        ("member-cut-short-before-adler", "a stored block holding the stream, then its Adler-32 where a complete zlib stream would have ended: cut short",
         framed(cut_short_member(good))),
        ("member-pack-buffer-plus-one", "one member of one byte more than the pack buffer's compressed bytes (stored blocks)",
         framed_member(stored_pack_buffer_member(1, real))),
        ("member-needs-dictionary", "a zlib stream that asks for a preset dictionary the archive does not have",
         framed(needs_dictionary(good))),
        ("member-over-1mib", "one member that inflates past the game's 1 MiB pack buffer", fixtures.world_archive()),
        ("member-1mib-plus-one", "one member that inflates to one byte more than the 1 MiB a member may",
         archive_file([padded_level_stream(enc.MAX_INFLATED_MEMBER_BYTES + 1, real)])),
        ("no-wres", "no WRES chunk", archive_file([no_wres])),
        ("no-wrld", "a WRES chunk with no WRLD chunk", archive_file([no_wrld])),
        ("truncated-chunk-header", "a chunk header cut short", archive_file([truncated_header])),
        ("chunk-overruns-parent", "a chunk inside the world that is larger than the world", archive_file([overrun])),
        ("members-4097", "a stream split into 4097 members, one more than the reader accepts",
         archive_file(split(level_stream(struct.pack("<ii", -1, 400), [(b"RLWD", real)])[:-8] + fixtures.chunk(b"PADD", bytes(6000)) + level_stream(struct.pack("<ii", -1, 400), [(b"RLWD", real)])[-8:], 4097))),
        ("wdat-short", "a WDAT chunk shorter than two words", archive_file([short_wdat])),
        ("wdat-missing", "a world with no WDAT chunk", archive_file([no_wdat])),
    ]


# ------------------------------------------------------------------------------------------------- terrain vectors
def xorshift(seed: int):
    """A stream of numbers that is the same in every Python (xorshift32), for authored data."""
    state = seed & 0xFFFFFFFF
    while True:
        state ^= (state << 13) & 0xFFFFFFFF
        state ^= state >> 17
        state ^= (state << 5) & 0xFFFFFFFF
        yield state


class AuthoredTerrain:
    """An authored terrain chunk and what the Python lookup (tools/heightfield_lookup.py) answers on it."""

    def __init__(self) -> None:
        draw = xorshift(0x2026_1029).__next__
        samples = [0] * heights.SAMPLE_COUNT
        # A hill on every edge of the square and around its middle: tiles of noise and extremes, the rest flat at 0.
        for tile_x, tile_y in ((0, 0), (63, 0), (0, 63), (63, 63), (31, 31), (31, 32), (32, 31), (32, 32), (10, 50), (50, 10), (5, 2), (2, 5), (1, 0), (0, 1), (62, 62)):
            for row in range(9):
                for column in range(9):
                    samples[terrain_fixtures.at(tile_x, tile_y, row, column)] = draw() % 60001 - 30000
        samples[terrain_fixtures.at(0, 0, 0, 0)], samples[terrain_fixtures.at(0, 0, 0, 1)] = 32767, -32768  # the extremes of a step
        samples[terrain_fixtures.at(63, 63, 8, 8)] = -32768
        self.scale = heights.f32(0.0009155832)
        self.water = heights.f32(-8.84)
        self.eres = terrain_fixtures.eres_with_heightfield(samples, self.scale, self.water, mixer_data=True)  # with the optional mixer data the loader reads
        self.field = heights.read_heightfield(self.eres)


_TERRAIN: AuthoredTerrain | None = None


def authored_terrain() -> AuthoredTerrain:
    global _TERRAIN
    if _TERRAIN is None:
        _TERRAIN = AuthoredTerrain()
    return _TERRAIN


TERRAIN_COORDINATES = [-math.inf, -1e30, -600.0, -513.0, -8.0, -1.0, -0.5, -0.002, -0.001953125, -0.0, 0.0, 1e-9, 0.001953125, 0.5, 1.0, 7.998, 8.0, 8.001, 9.0,
                       63.5, 64.0, 100.25, 255.998, 256.0, 300.5, 504.0, 511.0, 511.99, 511.998, 511.99609375, 512.0, 512.001, 513.0, 1000.0, 1024.0, 2048.0, 4096.0,
                       8192.0, 16383.99, 16384.0, 20000.0, 3e38, math.inf, math.nan]


def float_bits(value: float) -> int:
    return struct.unpack("<I", struct.pack("<f", value))[0]


def terrain_vectors() -> dict:
    """The authored terrain and what the lookup answers at the edges and at random: every pair of the listed coordinates (the
    square's edges, tile and sample boundaries, negative and fractional input, far outside it) and 600 positions in and around the
    square, each as the 32 bits of its coordinates and of the height."""
    terrain = authored_terrain()
    draw = xorshift(0x7E57_1029).__next__
    positions = [(x, y) for x in TERRAIN_COORDINATES for y in TERRAIN_COORDINATES]
    for _ in range(600):
        x = (draw() % 540_000) / 1000 - 14.0
        y = (draw() % 540_000) / 1000 - 14.0
        positions.append((x, y))
    records = b""
    for x, y in positions:
        x, y = (heights.f32(x) if math.isfinite(x) else x), (heights.f32(y) if math.isfinite(y) else y)
        records += struct.pack("<III", float_bits(x), float_bits(y), heights.height_bits(terrain.field, x, y))
    return {"eres": terrain.eres, "samplesSha256": terrain.field.samples_sha256(), "scaleBits": float_bits(terrain.scale),
            "waterBits": float_bits(terrain.water), "probes": records, "count": len(positions)}


# ----------------------------------------------------------------------------------------------- coordinate vectors
def double_rounding_texts() -> list[str]:
    """Decimals just beside the midpoint of two neighbouring float32 values, close enough that the nearest double is the midpoint
    itself: the move tool rounds to the double first and then (to even) to float32, so it goes to the even neighbour, where
    rounding the decimal to float32 in one step would go to the other. Reading with a one-step float32 parser fails these."""
    texts = []
    for low_bits in (0x3F800000, 0x3F800001, 0x42FA0000, 0x00800001, 0x7F7FFFFE):
        low, high = (struct.unpack("<f", struct.pack("<I", bits))[0] for bits in (low_bits, low_bits + 1))
        with localcontext() as context:
            context.prec = 400
            midpoint = (Decimal(low) + Decimal(high)) / 2  # exact: a float32 midpoint has 25 significant bits
            unit = Decimal(1).scaleb(midpoint.adjusted() - 25)  # a relative 1e-25 beside it, far inside half a double's spacing
            for value in (midpoint + unit, midpoint - unit):
                text = format(value, "E") if midpoint < Decimal("1E-5") else format(value, "f")
                if float(Decimal(text)) != float(midpoint):
                    raise AssertionError(f"{text} does not round to the midpoint as a double")
                texts.append(text)
    return texts


COORDINATE_TEXTS = [
    # ordinary numbers, the acceptance edit's among them
    "276.49", "265.07", "-12.1", "0", "-0", "+0", "0.0", "-0.0", "0e5", "-0e5", "1", "-1", "+1.5", "512", "511.99997", "0.1", "-0.1", "0.5", "16777216", "16777217", "-16777217",
    "123456789", "1e3", "1E3", "1e+3", "1e-3", "-.5e1", "5.", ".5", "+.5", "00012", "0.000001", "1e-10", "1e0", "1e-0", "1e+0000000000000000000005",
    # the edges of float32: largest, the halfway to infinity, denormals, underflow to zero
    "3.4028234663852886e38", "3.4028235e38", "3.4028235677973362e38", "3.4028235677973366e38", "3.5e38", "1e39", "-3.4028235e38", "-3.4028235677973366e38", "-1e39",
    "1.1754943508222875e-38", "1.401298464324817e-45", "1e-45", "7e-46", "7.1e-46", "1e-46", "-1e-46", "1e-50", "-1e-50", "1e-60", "-1e-60", "1e-400", "-1e-400", "0.000000000000000000000000000000000000000000001",
    # exponents the tool's decimal reader takes or refuses
    "0e999999999999999999", "1e999999999999999999", "1e1000000000000000000", "1e-999999999999999999", "0e1000000000000000000", "1e-1000000000000000000",
    # length (the tool refuses text over 128 characters, spaces included)
    "1" * 127, "1" * 128, "1" * 129, "0." + "0" * 120 + "1", "1" + "0" * 126, "7" + " " * 127, " " * 127 + "7", " " * 128 + "7", "  7  ", " 7", "7 ",
    # what is not a number
    "", " ", "-", "+", ".", "e5", "1e", "1e+", "1e-", "--1", "1-", "1.2.3", "1,5", "0x10", "1 2", "inf", "-inf", "Infinity", "-Infinity", "NaN", "nan", "sNaN", "1e5.5", "(1)",
    # what the tool's decimal reader takes and the page's does not: digit separators, other digits, other whitespace
    "1_000", "1_0.5_5", "\u0663", "\u0661\u0662\u0663", "\uff11\uff12", "\t7", "\u00a07", "7\n", "\n7", "7\r", "\u20077", "\x0b7",
]


def in_page_grammar(text: str) -> bool:
    """Whether the text is in the form the page's reader (CoordinateInput) accepts: at most 128 characters, a sign, ASCII digits
    with a point, an exponent of at most 18 digits once leading zeros are dropped, and ASCII spaces around it."""
    if len(text) > 128:
        return False
    match = re.fullmatch(r"[+-]?([0-9]*)(?:\.([0-9]*))?(?:[eE][+-]?([0-9]+))?", text.strip(" "), flags=re.ASCII)
    if not match or len(match.group(1) or "") + len(match.group(2) or "") == 0:
        return False
    return match.group(3) is None or len(match.group(3).lstrip("0")) <= 18


def coordinate_vectors() -> list[dict]:
    """Each text with what the move tool (world_edit_move._coordinates) makes of it: refused, or the float32 it stores (the four
    bytes in hex), whether that is not exactly the decimal typed, and its exact decimal value. The page's reader is stricter in
    what text it takes (grammar says whether the text is in its form) and must match the tool in everything it does take."""
    out = []
    for text in [*COORDINATE_TEXTS, *double_rounding_texts()]:
        try:
            _, details = mover._coordinates([text, "0", "0"], True)
        except mover.MoveError:
            out.append({"text": text, "ok": False, "hex": "", "rounded": False, "exact": "", "grammar": in_page_grammar(text)})
            continue
        stored = details[0]["stored"]
        out.append({"text": text, "ok": True, "hex": details[0]["float32LittleEndianHex"], "rounded": details[0]["rounded"],
                    "exact": format(Decimal(stored), "f"), "grammar": in_page_grammar(text)})
    return out


# ---------------------------------------------------------------------------------------------------- stage vectors
BIG_WORLD = 4 << 20


def stage_specs() -> list[dict]:
    """Inputs for the reference stager. A world is a body vector (from), an edit vector's body (edit) or repeated bytes."""
    def spec(name, mod_id, mod_name, worlds, **extra):
        return {"name": name, "id": mod_id, "modName": mod_name, "version": "1", "author": "", "description": "", "ceMin": None,
                "ceMax": None, "worlds": worlds, **extra}

    from_ = lambda level, source: {"level": level, "from": source}
    edit = lambda level, source: {"level": level, "edit": source}
    repeat = lambda level, byte, size: {"level": level, "repeat": byte, "size": size}
    return [
        spec("minimal", "ce-edit", "Edit", [from_(100, "authored-v50")]),
        spec("full-metadata", "moved-target-tank-1", "Moved Target Tank", [edit(100, "move-v50"), from_(1, "authored-v43")],
             version="0.1.11", author="The Toolkit", description="A Target Tank moved with the level editor.", ceMin="0.1.11", ceMax="1.0"),
        spec("quotes-and-backslash", "quotes", 'Say "hi" \\ bye', [from_(5, "authored-v46")], description='a "quoted" \\path\\ here', author='O"Neil'),
        spec("max-lengths", "a" * 48, "N" * 64, [from_(100, "authored-v50")], version="V" * 32, author="A" * 64, description="D" * 1024),
        spec("worlds-sorted-by-path", "three-worlds", "Three", [from_(999, "authored-v50"), from_(7, "authored-v44"), from_(100, "authored-v45")]),
        spec("version-numbers", "ver", "Versions", [from_(100, "authored-v50")], ceMin="1.2.3.4", ceMax="65535.0.0"),
        spec("edit-one-version-only", "only-min", "Only min", [from_(100, "authored-v50")], ceMin="0"),
        spec("range-of-one-version", "one-version", "One version", [from_(100, "authored-v50")], ceMin="0.1.11", ceMax="0.1.11"),
        spec("range-in-numeric-order", "numeric-order", "Numeric order", [from_(100, "authored-v50")], ceMin="1.9", ceMax="1.10"),
        spec("range-equal-after-padding", "padded", "Padded", [from_(100, "authored-v50")], ceMin="1.2.0", ceMax="1.2"),
        spec("world-of-4-mib", "big-world", "Big", [repeat(100, 0x77, BIG_WORLD)]),
        spec("world-of-one-byte", "tiny-world", "Tiny", [repeat(0, 0x01, 1)]),
        spec("levels-zero-and-999", "ends", "Ends", [from_(0, "authored-v50"), from_(999, "authored-v43")]),
        spec("moved-twice", "moved-twice", "Moved twice", [edit(200, "move-two-v50"), edit(201, "move-v47")]),
        spec("editor-save", "level-100-edit", "Level 100 edit", [edit(100, "move-v50")], author="Test Pilot", description="Moved by typing coordinates."),
    ]


def refused_stage_specs() -> list[dict]:
    base = stage_specs()[0]
    out = []

    def bad(name, why, **change):
        out.append({**{k: v for k, v in base.items() if k != "name"}, "name": name, "why": why, **change})

    def slug(text: str) -> str:
        return f"{len(text)}-chars" if len(text) > 12 else (re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "empty")

    for text in ("", "UPPER", "has space", "x" * 49, "caf\u00e9", "dot.dot", "slash/x", "ok\n", "back\\slash", "tab\tid"):
        bad("id-" + slug(text), f"the mod id {text if len(text) <= 12 else str(len(text)) + ' characters'!r}", id=text)
    for label, text in (("empty", ""), ("65-chars", "x" * 65), ("non-ascii", "caf\u00e9"), ("tab", "a\tb"), ("del", "a\x7fb"), ("newline", "a\nb")):
        bad("name-" + label, f"the name is {label}", modName=text)
    for label, text in (("empty", ""), ("33-chars", "v" * 33), ("non-ascii", "1\u2013")):
        bad("version-" + label, f"the version is {label}", version=text)
    bad("author-65-chars", "an author of 65 characters", author="A" * 65)
    bad("author-non-ascii", "a non-ASCII author", author="Ren\u00e9")
    bad("description-1025-chars", "a description of 1025 characters", description="D" * 1025)
    bad("description-newline", "a newline in the description", description="two\nlines")
    for index, text in enumerate(("1.2.3.4.5", "a.b", "123456", "1..2", ".1", "1.", "", " 1", "1.2.3.4.", "-1", "1e3")):
        bad(f"ce-min-{index}", f"ce_min {text!r}", ceMin=text)
    bad("ce-max-bad", "ce_max that is not a version", ceMax="x")
    for index, (low, high) in enumerate((("1.2", "1.1"), ("0.1.11", "0.1.10"), ("1.10", "1.9"), ("2", "1.99999"), ("1.2.0.1", "1.2"))):
        bad(f"ce-range-{index}", f"ce_min {low} after ce_max {high}", ceMin=low, ceMax=high)
    bad("no-worlds", "a mod with no world files", worlds=[])
    bad("level-minus-one", "a level below 0", worlds=[{"level": -1, "from": "authored-v50"}])
    bad("level-1000", "a level above 999", worlds=[{"level": 1000, "from": "authored-v50"}])
    bad("empty-world", "a world file of no bytes", worlds=[{"level": 100, "repeat": 0x77, "size": 0}])
    bad("world-over-4-mib", "a world file of 4 MiB and one byte", worlds=[{"level": 100, "repeat": 0x77, "size": BIG_WORLD + 1}])
    return out


def spec_worlds(spec: dict, bodies: dict[str, bytes], edited: dict[str, bytes]) -> dict[int, bytes]:
    out = {}
    for world in spec["worlds"]:
        if "from" in world:
            out[world["level"]] = bodies[world["from"]]
        elif "edit" in world:
            out[world["level"]] = edited[world["edit"]]
        else:
            out[world["level"]] = bytes([world["repeat"]]) * world["size"]
    return out


def stage_vectors(bodies: dict[str, bytes], edited: dict[str, bytes]) -> tuple[list[dict], list[dict]]:
    """Runs the reference stager on every spec, into a scratch folder, and reads the folder back."""
    stages, refused = [], []
    for spec in stage_specs():
        worlds = spec_worlds(spec, bodies, edited)
        with tempfile.TemporaryDirectory() as tmp:
            parent, game = Path(tmp) / "mods", Path(tmp) / "game"
            parent.mkdir()
            game.mkdir()
            stager.stage_mod(parent, game, spec["id"], worlds, name=spec["modName"], version=spec["version"], author=spec["author"],
                             description=spec["description"], ce_min=spec["ceMin"], ce_max=spec["ceMax"])
            root = parent / spec["id"]
            manifest = (root / "mod.json").read_bytes()
            files = sorted((p.relative_to(root).as_posix(), p.stat().st_size, hashlib.sha256(p.read_bytes()).hexdigest())
                           for p in root.rglob("*") if p.is_file() and p.name != "mod.json")
            expected = {stager.world_path(level): body for level, body in worlds.items()}
            if [f[0] for f in files] != sorted(expected) or any(hashlib.sha256(expected[f[0]]).hexdigest() != f[2] for f in files):
                raise AssertionError(f"{spec['name']}: the reference stager wrote other files than its input")
            if manifest != stager.build_manifest(spec["id"], spec["modName"], spec["version"], expected, author=spec["author"],
                                                  description=spec["description"], ce_min=spec["ceMin"], ce_max=spec["ceMax"]):
                raise AssertionError(f"{spec['name']}: mod.json is not what build_manifest returns")
            json.loads(manifest)
            stages.append({**spec, "manifest": manifest, "manifestSha256": hashlib.sha256(manifest).hexdigest(), "files": files})
    for spec in refused_stage_specs():
        with tempfile.TemporaryDirectory() as tmp:
            parent, game = Path(tmp) / "mods", Path(tmp) / "game"
            parent.mkdir()
            game.mkdir()
            try:
                stager.stage_mod(parent, game, spec["id"], spec_worlds(spec, bodies, edited), name=spec["modName"], version=spec["version"],
                                 author=spec["author"], description=spec["description"], ce_min=spec["ceMin"], ce_max=spec["ceMax"])
            except stager.ModStageError:
                if list(parent.iterdir()):
                    raise AssertionError(f"{spec['name']}: the reference stager wrote something before refusing")
                refused.append(spec)
            else:
                raise AssertionError(f"{spec['name']}: the reference stager accepts an input that must be refused")
    return stages, refused


# ------------------------------------------------------------------------------------------------------ rendering
def deflate_b64(data: bytes) -> str:
    return base64.b64encode(zlib.compress(data, 9)).decode("ascii")


def cs_text(text: str) -> str:
    out = ['"']
    for char in text:
        code = ord(char)
        if char in '\\"':
            out.append("\\" + char)
        elif 0x20 <= code < 0x7F:
            out.append(char)
        else:
            out.append(f"\\u{code:04x}")
    out.append('"')
    return "".join(out)


def cs_raw(text: str, indent: str) -> str:
    """A raw string literal of base64, wrapped at 100 characters."""
    if not text:
        return '""'
    rows = [text[i:i + 100] for i in range(0, len(text), 100)]
    inner = indent + "    "
    return '"""\n' + "\n".join(inner + row for row in rows) + "\n" + inner + '"""'


def cs_float(value: float) -> str:
    out = enc.f32_out(value)
    if struct.unpack("<f", out)[0] != value or not math.isfinite(value):
        raise AssertionError(f"{value!r} is not an exact float32")
    if value == 0 and math.copysign(1, value) < 0:
        return "-0.0f"
    return f"{value!r}f"


def build() -> dict:
    """Everything the C# file holds, computed with the reference (asserting the reference's own round trips)."""
    valid_models: dict[str, dict] = {}
    valid_bodies: dict[str, bytes] = {}
    valids = []
    for name, note, source in valid_vectors():
        body = source if isinstance(source, bytes) else enc.write_world_body(source)
        model = enc.read_world_model(body)
        if enc.write_world_body(json.loads(json.dumps(model))) != body:
            raise AssertionError(f"{name}: the reference does not round-trip its own vector")
        lines = dump_lines(model)
        valid_models[name], valid_bodies[name] = model, body
        valids.append({"name": name, "note": note, "body": body, "lines": len(lines), "hash": dump_hash(lines),
                       "dump": "\n".join(lines) if len(lines) <= FULL_DUMP_LINES else ""})
    refused = []
    for name, why, body in refused_vectors(valid_bodies):
        try:
            enc.read_world_model(body)
        except (wrd.DecodeError, enc.EncodeError, struct.error):
            refused.append({"name": name, "why": why, "body": body})
        else:
            raise AssertionError(f"{name}: the reference accepts a vector that must be refused")
    edits = []
    for name, source, steps, model in edit_vectors(valid_models):
        edits.append({"name": name, "from": source, "steps": steps, "body": enc.write_world_body(model)})
    archives = [{"name": name, "note": note, "file": data, "info": info}
                for name, note, data, info in archive_vectors(valid_bodies)]
    bad_archives = []
    for name, why, data in refused_archives(valid_bodies):
        try:
            worlds = enc.level_worlds(b"".join(enc.inflate(enc.read_members(data))))
        except (enc.EncodeError, struct.error):
            pass
        else:
            if "baseLevel" in worlds:  # a world with no WDAT is the one vector the reference returns without level numbers
                raise AssertionError(f"{name}: the reference accepts an archive that must be refused")
        bad_archives.append({"name": name, "why": why, "file": data})
    edited = {e["name"]: e["body"] for e in edits}
    stages, bad_stages = stage_vectors(valid_bodies, edited)
    return {"valids": valids, "refused": refused, "edits": edits, "archives": archives, "badArchives": bad_archives,
            "stages": stages, "badStages": bad_stages, "coordinates": coordinate_vectors(), "terrain": terrain_vectors()}


def render(data: dict) -> str:
    pad = "        "
    out = ["// SPDX-License-Identifier: GPL-3.0-only",
           "// <auto-generated>",
           "// Written by tools/level_editor_vectors.py from the Toolkit's reference world-body reader and writer; do not edit.",
           "// Authored data only: no game bytes. Bodies and files are zlib streams in base64.",
           "// </auto-generated>",
           "#nullable enable",
           "namespace OnslaughtToolkit.Companion.Tests;", "",
           "internal static class LevelVectors", "{",
           "    /// <summary>A body the reference reads: its bytes and its reference dump (the dump's hash and line count when it is long).</summary>",
           "    internal sealed record WorldVector(string Name, string Note, string Body, int Lines, string DumpSha256, string Dump);", "",
           "    /// <summary>A body the reference refuses.</summary>",
           "    internal sealed record RefusedVector(string Name, string Why, string Body);", "",
           "    /// <summary>Steps applied to a vector's thing records and the bytes the reference writes afterwards.</summary>",
           "    internal sealed record EditVector(string Name, string From, EditStep[] Steps, string Body);", "",
           "    internal sealed record EditStep(string Op, int Thing, string Text, float X, float Y, float Z);", "",
           "    /// <summary>A level archive file and what the reference finds in it.</summary>",
           "    internal sealed record ArchiveVector(string Name, string Note, string File, int BaseLevel, int RealLevel, string? BaseSha256, string? RealSha256);", "",
           "    internal sealed record RefusedArchive(string Name, string Why, string File);", "",
           "    /// <summary>A world file of a staged mod: a body vector, an edit vector's body, or repeated bytes.</summary>",
           "    internal sealed record StageWorld(int Level, string From, string Edit, int Repeat, int Size);", "",
           "    internal sealed record StageFile(string Path, long Size, string Sha256);", "",
           "    /// <summary>Inputs the reference stager accepts, with the bytes of the mod.json and the files it wrote.</summary>",
           "    internal sealed record StageVector(string Name, string Id, string ModName, string Version, string Author, string Description, string? CeMin, string? CeMax, StageWorld[] Worlds, string Manifest, string ManifestSha256, StageFile[] Files);", "",
           "    /// <summary>Inputs the reference stager refuses.</summary>",
           "    internal sealed record RefusedStage(string Name, string Why, string Id, string ModName, string Version, string Author, string Description, string? CeMin, string? CeMax, StageWorld[] Worlds);", "",
           "    /// <summary>The reference's archive limits (tools/world_resources_encode.py), which LevelArchive holds to as well.</summary>",
           "    internal static class ReferenceLimits", "    {",
           f"        internal const int MaxFileBytes = {enc.MAX_ARCHIVE_BYTES}, MaxInflatedBytes = {enc.MAX_ARCHIVE_INFLATED_BYTES}, MaxMembers = {enc.MAX_ARCHIVE_MEMBERS},",
           f"            PackBufferBytes = {enc.PACK_BUFFER_SIZE}, MaxMemberInflatedBytes = {enc.MAX_INFLATED_MEMBER_BYTES};",
           "    }", "",
           "    /// <summary>A coordinate text and what the move tool makes of it; Grammar says whether the text is in the form the page's reader accepts.</summary>",
           "    internal sealed record CoordinateVector(string Text, bool Ok, string Hex, bool Rounded, string Exact, bool Grammar);", "",
           "    /// <summary>An authored terrain chunk (ERES), what the reference reads in it, and what its lookup answers at each probe: the 32 bits of X, of Y and of the height (little-endian, in a zlib stream).</summary>",
           "    internal sealed record TerrainVector(string Eres, string SamplesSha256, uint ScaleBits, uint WaterBits, int Count, string Probes);", "",
           "    internal static readonly WorldVector[] Valid =", "    ["]
    for v in data["valids"]:
        out.append(f"        new({cs_text(v['name'])}, {cs_text(v['note'])},")
        out.append(f"            {cs_raw(deflate_b64(v['body']), pad)},")
        out.append(f"            {v['lines']}, {cs_text(v['hash'])},")
        dump = cs_raw(deflate_b64(v["dump"].encode("ascii")), pad) if v["dump"] else '""'
        out.append(f"            {dump}),")
    out += ["    ];", "", "    internal static readonly RefusedVector[] Refused =", "    ["]
    for v in data["refused"]:
        body = cs_raw(deflate_b64(v["body"]), pad) if v["body"] else '""'
        out.append(f"        new({cs_text(v['name'])}, {cs_text(v['why'])}, {body}),")
    out += ["    ];", "", "    internal static readonly EditVector[] Edits =", "    ["]
    for v in data["edits"]:
        steps = []
        for step in v["steps"]:
            if step[0] == "rename":
                steps.append(f'new("rename", {step[1]}, {cs_text(step[2])}, 0f, 0f, 0f)')
            else:
                steps.append(f'new("{step[0]}", {step[1]}, "", {cs_float(step[2])}, {cs_float(step[3])}, {cs_float(step[4])})')
        out.append(f"        new({cs_text(v['name'])}, {cs_text(v['from'])}, [{', '.join(steps)}],")
        out.append(f"            {cs_raw(deflate_b64(v['body']), pad)}),")
    out += ["    ];", "", "    internal static readonly ArchiveVector[] Archives =", "    ["]
    for v in data["archives"]:
        info = v["info"]
        base, real = info["bodies"].get("BSWD"), info["bodies"].get("RLWD")
        out.append(f"        new({cs_text(v['name'])}, {cs_text(v['note'])},")
        out.append(f"            {cs_raw(deflate_b64(v['file']), pad)},")
        out.append(f"            {info['baseLevel']}, {info['realLevel']}, {cs_text(base) if base else 'null'}, {cs_text(real) if real else 'null'}),")
    out += ["    ];", "", "    internal static readonly RefusedArchive[] RefusedArchives =", "    ["]
    for v in data["badArchives"]:
        file = cs_raw(deflate_b64(v["file"]), pad) if v["file"] else '""'
        out.append(f"        new({cs_text(v['name'])}, {cs_text(v['why'])}, {file}),")
    out += ["    ];", "", "    internal static readonly StageVector[] Stages =", "    ["]

    def worlds_cs(worlds: list[dict]) -> str:
        return "[" + ", ".join(f'new({w["level"]}, {cs_text(w.get("from", ""))}, {cs_text(w.get("edit", ""))}, {w.get("repeat", 0)}, {w.get("size", 0)})'
                              for w in worlds) + "]"

    def opt(value) -> str:
        return "null" if value is None else cs_text(value)

    for v in data["stages"]:
        out.append(f"        new({cs_text(v['name'])}, {cs_text(v['id'])}, {cs_text(v['modName'])}, {cs_text(v['version'])}, {cs_text(v['author'])}, {cs_text(v['description'])},")
        out.append(f"            {opt(v['ceMin'])}, {opt(v['ceMax'])}, {worlds_cs(v['worlds'])},")
        out.append(f"            {cs_raw(deflate_b64(v['manifest']), pad)},")
        files = ", ".join(f"new({cs_text(f[0])}, {f[1]}, {cs_text(f[2])})" for f in v["files"])
        out.append(f"            {cs_text(v['manifestSha256'])}, [{files}]),")
    out += ["    ];", "", "    internal static readonly RefusedStage[] RefusedStages =", "    ["]
    for v in data["badStages"]:
        out.append(f"        new({cs_text(v['name'])}, {cs_text(v['why'])}, {cs_text(v['id'])}, {cs_text(v['modName'])}, {cs_text(v['version'])}, {cs_text(v['author'])}, {cs_text(v['description'])},")
        out.append(f"            {opt(v['ceMin'])}, {opt(v['ceMax'])}, {worlds_cs(v['worlds'])}),")
    out += ["    ];", "", "    internal static readonly CoordinateVector[] Coordinates =", "    ["]
    for v in data["coordinates"]:
        out.append(f"        new({cs_text(v['text'])}, {'true' if v['ok'] else 'false'}, {cs_text(v['hex'])}, {'true' if v['rounded'] else 'false'}, "
                   f"{cs_text(v['exact'])}, {'true' if v['grammar'] else 'false'}),")
    terrain = data["terrain"]
    out += ["    ];", "", "    internal static readonly TerrainVector Terrain =",
            f"        new({cs_raw(deflate_b64(terrain['eres']), pad)}, {cs_text(terrain['samplesSha256'])}, 0x{terrain['scaleBits']:08X}u, 0x{terrain['waterBits']:08X}u, {terrain['count']},",
            f"            {cs_raw(deflate_b64(terrain['probes']), pad)});", "}", ""]
    return "\n".join(out)


# --------------------------------------------------------------------------------------------------- retail table
def cmd_gate_table(args) -> int:
    if not args.stdout:
        raise SystemExit("choose --stdout explicitly")
    game = enc.selected_game_root(args.game)
    rows = ["level\ttag\tbytes\tsha256\tdumpLines\tdumpSha256"]
    bodies = terrains = 0
    for level, path in enc.level_archives(game).items():
        stream = b"".join(enc.inflate(enc.read_members(enc.read_retail(path))))
        worlds = enc.level_worlds(stream)
        for tag, body in sorted(worlds["bodies"].items()):
            lines = dump_lines(enc.read_world_model(body))
            rows.append(f"{level:03d}\t{tag}\t{len(body)}\t{hashlib.sha256(body).hexdigest()}\t{len(lines)}\t{dump_hash(lines)}")
            bodies += 1
        # The terrain: the heightfield's samples, scale and water, and the lookup's heights at a grid and at every thing of the level's own world.
        eres = next((stream[at:at + size] for tag, at, size in enc.chunks(stream) if tag == "ERES"), None)
        if eres is not None and "RLWD" in worlds["bodies"]:
            try:
                field = heights.read_heightfield(eres)
            except heights.DecodeError:
                # A chunk the loader's order does not read: the row says so, and the C# gate must refuse it too.
                rows.append(f"{level:03d}\tTERRAIN\trefused\t-\t0\t-")
                terrains += 1
                continue
            positions = terrain_gate_positions(enc.read_world_model(worlds["bodies"]["RLWD"]))
            digest = hashlib.sha256(b"".join(struct.pack("<I", heights.height_bits(field, x, y)) for x, y in positions)).hexdigest()
            rows.append(f"{level:03d}\tTERRAIN\t{float_bits(field.scale):08x}:{float_bits(field.water):08x}\t{field.samples_sha256()}\t{len(positions)}\t{digest}")
            terrains += 1
    print("\n".join(rows))
    print(f"world bodies: {bodies}; terrains: {terrains}", file=sys.stderr)
    return 0 if bodies else 1


def terrain_gate_positions(model: dict) -> list[tuple[float, float]]:
    """The positions the retail terrain gate asks the lookup about: a 33 x 33 grid reaching past the square, then every thing's X and Y."""
    grid = [(heights.f32(i * 16 + 0.37), heights.f32(j * 16 + 0.71)) for j in range(33) for i in range(33)]
    return grid + [(thing["init"]["position"][0], thing["init"]["position"][1]) for thing in model["things"]]


def shown(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def canonical(text: str) -> list[str]:
    """The file's text with each compressed blob replaced by the SHA-256 of what it inflates to, so that the check does not
    depend on which zlib compressed it."""
    parts = re.split(r'"""\n(.*?)\n\s*"""', text, flags=re.S)
    out = []
    for index, part in enumerate(parts):
        if index % 2:
            data = zlib.decompress(base64.b64decode("".join(part.split())))
            out.append("blob:" + hashlib.sha256(data).hexdigest())
        else:
            out.append(part)
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", nargs="?", choices=("gate-table",))
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--game", type=Path)
    ap.add_argument("--stdout", action="store_true")
    args = ap.parse_args(argv)
    if args.command == "gate-table":
        if args.game is None:
            ap.error("gate-table needs --game")
        return cmd_gate_table(args)
    if args.write == args.check:
        ap.error("choose --write or --check")
    text = render(build())
    if args.write:
        OUTPUT.write_text(text, encoding="utf-8", newline="\n")
        print(f"wrote {shown(OUTPUT)} ({len(text)} characters)")
        return 0
    current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.is_file() else ""
    if canonical(current) != canonical(text):
        print(f"{shown(OUTPUT)} is not what this script writes; run it with --write", file=sys.stderr)
        return 1
    print(f"{shown(OUTPUT)} is current")
    return 0


if __name__ == "__main__":
    sys.exit(main())
