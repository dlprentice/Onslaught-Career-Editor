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
- authored level archives with the level numbers and bodies the reference finds in them, and archives it refuses.

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
import hashlib
import json
import math
import re
import struct
import zlib
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))

import content_catalog_tests as fixtures  # noqa: E402  the hand-assembled authored body and archive
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


def split(data: bytes, count: int) -> list[bytes]:
    """The stream in count pieces: one byte each, and the rest in the last."""
    return [data[i:i + 1] for i in range(count - 1)] + [data[count - 1:]]


def level_stream(wdat: bytes | None, bodies: list[tuple[bytes, bytes]]) -> bytes:
    wrld = (fixtures.chunk(b"WDAT", wdat) if wdat is not None else b"") + b"".join(fixtures.chunk(tag, body) for tag, body in bodies)
    return (fixtures.chunk(b"LVLR", struct.pack("<I", 103)) + fixtures.chunk(b"TARG", struct.pack("<I", 1))
            + fixtures.chunk(b"AYAD", bytes(24)) + fixtures.chunk(b"ERES", b"\0" * 40)
            + fixtures.chunk(b"WRES", fixtures.chunk(b"WRLD", wrld)) + fixtures.chunk(b"LNDS", b""))


def archive_vectors(valid: dict[str, bytes]) -> list[tuple[str, str, bytes, dict]]:
    real, base = valid["authored-v50"], valid["kinds-v46"]
    out: list[tuple[str, str, bytes, dict]] = []
    one = level_stream(struct.pack("<ii", -1, 200), [(b"RLWD", real)])
    out.append(("real-only", "one member, the level's own world only", archive_file([one])))
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
    return [
        ("no-bytes", "an empty file", b""),
        ("length-only", "a file that ends inside a member length", b"\x05\x00"),
        ("zero-member", "a member of length zero", struct.pack("<I", 0)),
        ("member-overruns", "a member length past the end of the file", struct.pack("<I", len(member) + 1) + member),
        ("not-zlib", "a member that is not a zlib stream", struct.pack("<I", 8) + b"notzlib!"),
        ("member-truncated", "a zlib stream cut short", struct.pack("<I", len(member) - 5) + member[:-5]),
        ("member-trailing-data", "bytes after the end of a zlib stream", struct.pack("<I", len(member) + 4) + member + b"junk"),
        ("member-over-1mib", "one member that inflates past the game's 1 MiB pack buffer", fixtures.world_archive()),
        ("no-wres", "no WRES chunk", archive_file([no_wres])),
        ("no-wrld", "a WRES chunk with no WRLD chunk", archive_file([no_wrld])),
        ("truncated-chunk-header", "a chunk header cut short", archive_file([truncated_header])),
        ("chunk-overruns-parent", "a chunk inside the world that is larger than the world", archive_file([overrun])),
        ("members-4097", "a stream split into 4097 members, one more than the reader accepts",
         archive_file(split(level_stream(struct.pack("<ii", -1, 400), [(b"RLWD", real)])[:-8] + fixtures.chunk(b"PADD", bytes(6000)) + level_stream(struct.pack("<ii", -1, 400), [(b"RLWD", real)])[-8:], 4097))),
        ("wdat-short", "a WDAT chunk shorter than two words", archive_file([short_wdat])),
        ("wdat-missing", "a world with no WDAT chunk", archive_file([no_wdat])),
    ]


# ------------------------------------------------------------------------------------------------------ rendering
def deflate_b64(data: bytes) -> str:
    return base64.b64encode(zlib.compress(data, 9)).decode("ascii")


def cs_text(text: str) -> str:
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


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
    return {"valids": valids, "refused": refused, "edits": edits, "archives": archives, "badArchives": bad_archives}


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
    out += ["    ];", "}", ""]
    return "\n".join(out)


# --------------------------------------------------------------------------------------------------- retail table
def cmd_gate_table(args) -> int:
    if not args.stdout:
        raise SystemExit("choose --stdout explicitly")
    game = enc.selected_game_root(args.game)
    rows = ["level\ttag\tbytes\tsha256\tdumpLines\tdumpSha256"]
    bodies = 0
    for level, path in enc.level_archives(game).items():
        worlds = enc.level_worlds(b"".join(enc.inflate(enc.read_members(enc.read_retail(path)))))
        for tag, body in sorted(worlds["bodies"].items()):
            lines = dump_lines(enc.read_world_model(body))
            rows.append(f"{level:03d}\t{tag}\t{len(body)}\t{hashlib.sha256(body).hexdigest()}\t{len(lines)}\t{dump_hash(lines)}")
            bodies += 1
    print("\n".join(rows))
    print(f"world bodies: {bodies}", file=sys.stderr)
    return 0 if bodies else 1


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
