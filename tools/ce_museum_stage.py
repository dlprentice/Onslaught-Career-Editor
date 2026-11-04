#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Stage an experimental, authored CE exhibition from locally owned resources.

The manifest binds exact source records, but does not carry source actors or scripts
into the exhibition. Generated world files use owned resource bindings and stay private.
This adapter is a content experiment, not a playable-room acceptance certificate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import struct
import sys

import world_resources_encode as world
from world_mod_stage import ModStageError, check_identity, stage_mod

FORMAT = "onslaught.ce.museum.v1"
MAX_PROJECT_BYTES = 128 * 1024
MAX_EXHIBITS = 64
MAX_ARCHIVE_BYTES = 64 * 1024 * 1024
SHA = re.compile(r"[0-9a-f]{64}")
ID = re.compile(r"[a-z0-9][a-z0-9_-]{0,47}")
LEVEL_RESOURCE_VERSION = 103


class MuseumError(ValueError):
    pass


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def record_digest(record: dict) -> str:
    """A decoded record's content identity; never a label or basename guess."""
    return digest(json.dumps(record, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=True, allow_nan=False).encode("ascii"))


def fields(value: object, expected: set[str], label: str) -> dict:
    if not isinstance(value, dict) or set(value) != expected:
        raise MuseumError(f"{label}: expected the documented fields only")
    return value


def number(value: object, low: int, high: int, label: str) -> int:
    if type(value) is not int or not low <= value <= high:
        raise MuseumError(f"{label}: expected an integer from {low} to {high}")
    return value


def vector(value: object, label: str) -> list[float]:
    if not isinstance(value, list) or len(value) != 3 or any(
        type(x) not in (int, float) or not math.isfinite(x) or abs(x) > 8192 for x in value
    ):
        raise MuseumError(f"{label}: expected three finite components within the room bounds")
    return [struct.unpack("<f", struct.pack("<f", x))[0] for x in value]


def pin(value: object, label: str) -> str:
    if not isinstance(value, str) or not SHA.fullmatch(value):
        raise MuseumError(f"{label}: expected a lowercase SHA-256")
    return value


def validate(project: object) -> dict:
    p = fields(project, {"format", "id", "name", "carrier", "start", "exhibits"}, "project")
    if p["format"] != FORMAT:
        raise MuseumError("unsupported museum project format")
    if not isinstance(p["id"], str) or not ID.fullmatch(p["id"]):
        raise MuseumError("project id is not a simple lowercase identifier")
    check_identity(p["id"], p["name"], "1")
    carrier = fields(p["carrier"], {"level", "sha256"}, "carrier")
    number(carrier["level"], 0, 849, "carrier level")
    pin(carrier["sha256"], "carrier hash")
    if not isinstance(p["exhibits"], list) or not 1 <= len(p["exhibits"]) <= MAX_EXHIBITS:
        raise MuseumError("an exhibition needs one to 64 exhibits")
    ids = set()
    for index, item in enumerate([p["start"], *p["exhibits"]]):
        keys = {"source", "offset", "orientation"} | ({"id"} if index else set())
        fields(item, keys, "placement")
        source = fields(item["source"], {"world", "ordinal", "sha256"}, "source binding")
        if source["world"] not in ("BSWD", "RLWD"):
            raise MuseumError("source world must be BSWD or RLWD")
        number(source["ordinal"], 0, 999, "source ordinal")
        pin(source["sha256"], "source record hash")
        vector(item["offset"], "offset")
        vector(item["orientation"], "orientation")
        if index:
            ident = item["id"]
            if not isinstance(ident, str) or not ID.fullmatch(ident) or ident in ids:
                raise MuseumError("exhibit identifiers must be unique simple lowercase identifiers")
            ids.add(ident)
    return p


def bound_record(models: dict, binding: dict, kind: str) -> dict:
    source = models.get(binding["world"])
    if source is None or binding["ordinal"] >= len(source["things"]):
        raise MuseumError("source record is absent")
    record = source["things"][binding["ordinal"]]
    if record.get("kind") != kind or record_digest(record) != binding["sha256"]:
        raise MuseumError("source record kind or content changed")
    return record


def authored_init(name: str, position: list, orientation: list, *, start: bool = False) -> dict:
    init = {"position": position, "orientation": orientation, "meshNumber": 0,
            "allegiance": 0, "target": 0, "script": "", "name": name,
            "spawnScript": "", "active": 1, "attachScriptsToUnits": 0}
    if start:
        # World starts use one-based player identities; zero is not the visitor.
        init["start"] = {"planeMode": 0, "playerNumber": 1}
    return init


def empty_world(source: dict, level: int) -> dict:
    configs = source["header"]["battleEngineConfigurations"]
    if len(configs) != 1 or not isinstance(configs[0], str) or not configs[0]:
        raise MuseumError("the carrier must bind exactly one player configuration")
    return {"format": world.MODEL_FORMAT, "version": 50,
            "header": {"headerVersion": 3, "unused": [0, 0],
                       "battleEngineConfigurations": list(configs), "v2Words": [0, 0, 0], "worldType": 0},
            "baseLevel": level, "scripts": [], "mapNumber": source["mapNumber"], "namedMeshes": [],
            "things": [], "treeGroups": [], "treeTypes": [],
            "influenceMap": {"version": 1, "nodes": 0, "nodeBytes": "", "links": 0, "linkBytes": ""},
            "waypointPaths": [],
            "timings": {"oldF": 0.0, "oldG": 0.0, "oldH": 0.0, "preRun": 0.0, "pan": 0.0,
                        "sGrade": 0, "dGrade": 0, "timeLimit": 0.0, "fullScoreTime": 0.0,
                        "percentageScoreTime": 0.0, "scorePercentage": 0.0},
            "occupancyGrids": [{"version": 0, "data": ""} for _ in range(3)], "levelStartTime": 0.0}


def make_worlds(project: dict, models: dict, base_level: int) -> dict[str, bytes]:
    validate(project)
    start = bound_record(models, project["start"]["source"], "start")
    if start["init"].get("start", {}).get("playerNumber") != 1:
        raise MuseumError("the visitor must bind the carrier's primary-player start")
    source = models[project["start"]["source"]["world"]]
    anchor = vector(start["init"]["position"], "source start")
    model = empty_world(source, base_level)

    def location(placement: dict) -> list:
        return vector([a + b for a, b in zip(anchor, vector(placement["offset"], "offset"))], "position")

    model["things"].append({"oid": start["oid"], "kind": "start",
                             "init": authored_init("ce.museum.visitor", location(project["start"]),
                                                   vector(project["start"]["orientation"], "orientation"), start=True)})
    for placement in project["exhibits"]:
        original = bound_record(models, placement["source"], "feature")
        if not isinstance(original.get("definition"), str) or not original["definition"]:
            raise MuseumError("an exhibit must bind a named static-feature definition")
        model["things"].append({"oid": original["oid"], "kind": "feature",
                                 "definition": original["definition"], "diesOn": 0,
                                 "init": authored_init("ce.museum." + placement["id"], location(placement),
                                                       vector(placement["orientation"], "orientation"))})
    # The base body is empty too: no inherited actors, scripts, paths or mesh auto-spawns.
    return {"BSWD": world.write_world_body(empty_world(source, -1)),
            "RLWD": world.write_world_body(model)}


def audit_worlds(project: dict, bodies: dict[str, bytes], base_level: int) -> dict:
    """Inspect encoded output independently of the composition path."""
    if set(bodies) != {"BSWD", "RLWD"}:
        raise MuseumError("generated content contains unexpected world bodies")
    actors = 0
    for tag in ("BSWD", "RLWD"):
        model = world.read_world_model(bodies[tag])
        expected_base = -1 if tag == "BSWD" else base_level
        if model["baseLevel"] != expected_base or model["header"].get("worldType") != 0:
            raise MuseumError("generated world has an unexpected progression or multiplayer binding")
        for field in ("scripts", "namedMeshes", "treeGroups", "treeTypes", "waypointPaths"):
            if model[field]:
                raise MuseumError("generated world retained source scripts, navigation or automatic spawns")
        if model["influenceMap"]["nodes"] or model["influenceMap"]["links"] or any(
            g["data"] for g in model["occupancyGrids"]
        ):
            raise MuseumError("generated world retained source navigation state")
        expected = [] if tag == "BSWD" else [("start", "ce.museum.visitor")] + [
            ("feature", "ce.museum." + item["id"]) for item in project["exhibits"]
        ]
        actual = [(t["kind"], t["init"]["name"]) for t in model["things"]]
        if actual != expected:
            raise MuseumError("generated world contains an unexpected actor")
        for thing in model["things"]:
            init = thing["init"]
            if init["script"] or init["spawnScript"] or init["attachScriptsToUnits"]:
                raise MuseumError("generated actor contains a script attachment")
            if thing["kind"] == "start" and init.get("start") != {"planeMode": 0, "playerNumber": 1}:
                raise MuseumError("generated visitor has an unsupported player configuration")
        actors += len(actual)
    return {"actors": actors, "sourceScriptsCarried": 0, "sourceActorsCarried": 0}


def build(project: dict, carrier: bytes) -> tuple[dict[int, bytes], dict]:
    validate(project)
    if not 0 < len(carrier) <= MAX_ARCHIVE_BYTES:
        raise MuseumError("carrier archive exceeds the content-stage bound")
    if digest(carrier) != project["carrier"]["sha256"]:
        raise MuseumError("carrier content changed")
    raw = b"".join(world.inflate(world.read_members(carrier)))
    headers = [(at, size) for tag, at, size in world.chunks(raw) if tag == "LVLR"]
    if len(headers) != 1 or headers[0][1] != 4 or struct.unpack_from("<I", raw, headers[0][0])[0] != LEVEL_RESOURCE_VERSION:
        raise MuseumError("unsupported carrier resource format")
    if sum(tag == "WRES" for tag, _, _ in world.chunks(raw)) != 1:
        raise MuseumError("carrier needs exactly one world section")
    extracted = world.level_worlds(raw)
    base_level = number(extracted.get("baseLevel"), 0, 999, "carrier base world")
    real_level = number(extracted.get("realLevel"), 0, 999, "carrier real world")
    if base_level == real_level or real_level != project["carrier"]["level"]:
        raise MuseumError("carrier world filenames must be distinct and match the selected level")
    if set(extracted["bodies"]) != {"BSWD", "RLWD"}:
        raise MuseumError("carrier needs one base and one real world body")
    models = {tag: world.read_world_model(body) for tag, body in extracted["bodies"].items()}
    if models["BSWD"]["baseLevel"] >= 0 or models["RLWD"]["baseLevel"] != base_level:
        raise MuseumError("carrier's parent-world bindings are unsupported")
    bodies = make_worlds(project, models, base_level)
    inspected = audit_worlds(project, bodies, base_level)
    return {base_level: bodies["BSWD"], real_level: bodies["RLWD"]}, {
                     "route": "isolated-carrier-world-overrides", "launchLevel": real_level,
                     "exhibits": len(project["exhibits"]), **inspected,
                     "worldBytes": sum(len(body) for body in bodies.values()),
                     "scope": "authored content staging; runtime and career acceptance are separate"}


def stage(project: dict, game: Path, parent: Path) -> dict:
    validate(project)
    game = world.selected_game_root(game)
    carrier = world.level_archives(game).get(project["carrier"]["level"])
    if carrier is None:
        raise MuseumError("selected carrier archive is absent")
    bodies, summary = build(project, world.read_retail(carrier))
    try:
        result = stage_mod(parent, game, project["id"], bodies, name=project["name"], version="1",
                           description="Experimental museum on existing terrain; enable only in a separate museum user folder.",
                           ce_min="0.1.13")
    except ModStageError as error:
        raise MuseumError("could not publish the generated museum folder safely") from error
    return {**summary, **result}


def load_project(path: Path) -> dict:
    data = world.read_retail(path)
    if len(data) > MAX_PROJECT_BYTES:
        raise MuseumError("museum project is too large")
    def pairs(items):
        out = {}
        for key, value in items:
            if key in out:
                raise MuseumError("duplicate project field")
            out[key] = value
        return out
    return validate(json.loads(data, object_pairs_hook=pairs,
                               parse_constant=lambda _: (_ for _ in ()).throw(MuseumError("non-finite project number"))))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--game", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    try:
        result = stage(load_project(args.project), args.game, args.out)
    except (ValueError, OSError, KeyError, struct.error) as error:
        print(f"museum staging refused: {type(error).__name__}", file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
