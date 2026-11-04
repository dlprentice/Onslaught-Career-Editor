#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""The compiled physics script (data/default physics.dat), statement by statement and value by value.

CPhysicsScript::Load reads a 16-bit version, then statements until a type of -1. A statement stores its type, a size
that retail does not use for the nine known types, a zero-terminated name and a value list; a value stores its id, its
size and its body, followed by a word that is zero when another value follows and -1 when the list ends.

Each value id of each statement belongs to one value class, whose Load reads exactly the value's stored size. The
tables below give every class's body as a signature (i int, f float, s zero-terminated string; an empty signature is a
value with no body) and the catalogue role of what a string names. They come from the rebuild's typed reader
(rebuild/OnslaughtRebuild.Parity/Physics/PhysicsRegistry.cs and PhysicsRegistry.Families.cs), which applies each value
as the game's Create*Value classes do and throws when a body is not read exactly.

An id no class knows is skipped by the game: it stays in the result as unread bytes, not as a guess.

Run:  python ./tools/physics_values_decode.py --game GAME_FOLDER    (prints counts only; the install is only read)
"""
from __future__ import annotations

import argparse
import collections
import os
import struct
import sys
from pathlib import Path

SUPPORTED_VERSION = 18
MAX_STATEMENTS = 10_000
MAX_VALUES = 1_024
MAX_VALUE_BYTES = 1_048_576

STATEMENT_KINDS = {1: "unit", 2: "weapon", 3: "weapon-mode", 4: "round", 5: "spawner", 6: "explosion", 7: "component",
                   8: "feature", 9: "hazard"}

# Roles of a value's strings, in signature order: what each string names. None names nothing in the catalogue.
MESH, PARTICLE, SOUND, ICON, EXPLOSION, WEAPON, MODE, ROUND, SPAWNER, COMPONENT, THING, BASED_ON, MOUNT = (
    "mesh", "particle-effect", "sound-effect", "icon", "explosion", "weapon", "weapon-mode", "round", "spawner",
    "component", "thing", "based-on", "mount")

_FLOATS = "f"
UNIT = {
    1: ("f", "velocity"), 2: ("f", "velocity"), 3: ("f", "life"), 4: ("f", "airShields"), 5: ("f", "turnRate"),
    6: ("f", "turnRate"), 7: ("ssi", "weapon", (WEAPON, MOUNT)), 8: ("i", "behaviour"), 9: ("s", "mesh", (MESH,)),
    10: ("s", "explosion", (EXPLOSION,)), 11: ("i", "allegiance"), 12: ("s", "trails", (PARTICLE,)),
    13: ("s", "thrusters", (PARTICLE,)), 14: ("s", "smoke", (PARTICLE,)), 15: ("f", "groundShields"),
    16: ("f", "airShieldRegeneration"), 17: ("f", "groundShieldRegeneration"), 18: ("ssi", "spawner", (SPAWNER, MOUNT)),
    19: ("f", "threat"), 20: ("f", "importance"), 21: ("f", "soundMaterial"), 22: ("f", "strafeChange"),
    23: ("f", "maxTargetRange"), 24: ("s", "shieldEffect", (PARTICLE,)), 25: ("i", "navigationMap"),
    26: ("i", "multipleSpawn"), 27: ("si", "component", (COMPONENT,)), 28: ("f", "stealth"), 29: ("fi", "attackPriority"),
    30: ("f", "bodyMotion"), 31: ("f", "legSpeed"), 32: ("f", "legPlacementArea"), 33: ("f", "detonationDelay"),
    34: ("f", "bounceFactor"), 35: ("s", "waterWake", (PARTICLE,)), 36: ("s", "dust", (PARTICLE,)),
    37: ("s", "dust", (PARTICLE,)), 38: ("s", "vent", (PARTICLE,)), 39: ("s", "basedOn", (BASED_ON,)),
    40: ("f", "minThrusterHeight"), 41: ("f", "maxThrusterHeight"), 42: ("f", "minAltitude"),
    43: ("i", "buildingNumber"), 44: ("i", "buildingMeshType"), 45: ("i", "parachute"), 46: ("i", "knockTrees"),
    47: ("f", "turretTurnRate"), 48: ("f", "hover"), 50: ("i", "deploy"), 51: ("s", "activationEffect", (PARTICLE,)),
    52: ("i", "retreat"), 53: ("i", "wingman"), 54: ("s", "noise", (SOUND,)), 55: ("s", "afterburner", (PARTICLE,)),
    56: ("i", "big"), 57: ("s", "smallExplosion", (EXPLOSION,)), 58: ("s", "stompExplosion", (EXPLOSION,)),
    59: ("f", "deployDamageMultiplier"), 60: ("f", "standingLegPlacementArea"), 61: ("f", "maxLegsLifted"),
    62: ("i", "indiscriminate"), 63: ("s", "spawnNoise", (SOUND,)), 64: ("s", "groundWake", (PARTICLE,)),
    65: ("i", "shatter"), 66: ("i", "canBeLocked"), 67: ("i", "sweeping"), 68: ("i", "ignoreThreats"),
    69: ("i", "animatedCollision"), 70: ("i", "icon"),
}
WEAPON_VALUES = {
    1: ("is", "chargeMode", (MODE,)), 2: ("f", "chargeRate"), 3: ("i", "ammoStore"), 4: ("f", "consumption"),
    5: ("s", "icon", (ICON,)), 6: ("f", "smart"), 7: ("f", "adjustAim"), 8: ("i", "zoomMode"),
    9: ("i", "allowMovement"), 10: ("i", "placement"), 11: ("i", "languageName"), 12: ("i", "rating"),
    13: ("i", "rating"), 14: ("i", "rating"),
}
WEAPON_MODE = {
    1: ("f", "inaccuracy"), 2: ("s", "round", (ROUND,)), 3: ("f", "reloadTime"), 4: ("f", "burstSize"),
    5: ("f", "burstDelay"), 6: ("s", "muzzleEffect", (PARTICLE,)), 8: ("ff", "launchSequence"), 9: ("f", "minRange"),
    10: ("f", "maxRange"), 11: ("f", "minDeflection"), 12: ("f", "maxDeflection"), 13: ("f", "preFireDelay"),
    14: ("f", "postFireDelay"), 15: ("s", "clip", (MODE,)), 16: ("f", "lockTime"), 17: ("f", "lockDeflection"),
    18: ("s", "preFireEffect", (PARTICLE,)), 19: ("i", "lockMode"), 20: ("i", "lockUnit"), 21: ("f", "lockRange"),
    22: ("f", "maxLocks"), 23: ("f", "lockRadius"), 24: ("s", "launchSound", (SOUND,)),
    25: ("s", "weaponBasedOn", (WEAPON,)), 26: ("f", "minTargetHeight"), 27: ("f", "maxTargetHeight"),
    28: ("f", "volleySize"), 29: ("f", "track"), 30: ("f", "yawTolerance"), 31: ("fff", "launchAngle"), 32: ("f", "power"),
    33: ("f", "predictive"), 34: ("s", "preFireSound", (SOUND,)), 35: ("f", "soundPerBurst"),
    36: ("s", "postFireSound", (SOUND,)), 37: ("i", "muzzleLight"), 38: ("f", "muzzleLightRadius"),
}
ROUND_VALUES = {
    1: ("f", "lifeSpan"), 2: ("f", "damage"), 3: ("f", "speed"), 4: ("i", "seek"), 5: ("f", "turnRate"),
    6: ("f", "gravity"), 7: ("f", "bounceFactor"), 8: ("s", "effect", (PARTICLE,)), 9: ("s", "explosion", (EXPLOSION,)),
    10: ("f", "seekDelay"), 11: ("f", "wiggle"), 12: ("f", "radius"), 13: ("", "flak"), 14: ("f", "flakInaccuracy"),
    15: ("f", "seekAngle"), 16: ("", "beam"), 17: ("f", "soundMaterial"), 18: ("", "weirdoSeek"), 19: ("f", "rearm"),
    20: ("s", "basedOn", (BASED_ON,)), 21: ("f", "seekTerminationTime"), 22: ("f", "missile"), 23: ("f", "proximity"),
    24: ("f", "gridOfFear"), 25: ("f", "canGoUnderWater"), 26: ("f", "groundHugging"), 27: ("f", "passiveCollision"),
    28: ("f", "jumps"), 29: ("f", "jumpRange"), 30: ("f", "jumpDelay"), 31: ("i", "explode"), 32: ("f", "torpedo"),
    33: ("s", "waterEffect", (PARTICLE,)), 34: ("f", "fire"), 35: ("i", "treeCollision"), 36: ("s", "mesh", (MESH,)),
    37: ("f", "smart"), 38: ("f", "length"),
}
SPAWNER_VALUES = {
    1: ("s", "thing", (THING,)), 2: ("f", "delay"), 3: ("i", "amount"), 4: ("f", "seekDelay"), 5: ("", "recall"),
    6: ("f", "minRange"), 7: ("f", "maxRange"), 8: ("f", "preSpawnDelay"), 9: ("f", "postSpawnDelay"),
    10: ("s", "basedOn", (BASED_ON,)), 11: ("i", "squadSize"), 12: ("f", "squadDelay"), 13: ("i", "infinite"),
    14: ("i", "conditions"),
}
EXPLOSION_VALUES = {
    1: ("s", "basedOn", (BASED_ON,)), 2: ("s", "airEffect", (PARTICLE,)), 3: ("f", "radius"), 4: ("f", "damage"),
    5: ("s", "groundEffect", (PARTICLE,)), 6: ("s", "waterEffect", (PARTICLE,)), 7: ("s", "unitEffect", (PARTICLE,)),
    8: ("i", "volumetric"), 9: ("i", "time"), 10: ("s", "sound", (SOUND,)), 11: ("i", "smart"), 12: ("i", "light"),
    13: ("i", "oriented"), 14: ("f", "shockwave"), 15: ("s", "waterSound", (SOUND,)),
}
COMPONENT_VALUES = {
    1: ("f", "life"), 2: ("ssi", "weapon", (WEAPON, MOUNT)), 3: ("s", "mesh", (MESH,)),
    4: ("s", "explosion", (EXPLOSION,)), 6: ("f", "maxTargetRange"), 7: ("f", "maxTurretYaw"), 8: ("f", "maxYaw"),
    9: ("f", "turnRate"), 10: ("s", "basedOn", (BASED_ON,)), 11: ("f", "turretTurnRate"), 12: ("s", "noise", (SOUND,)),
    13: ("f", "big"), 14: ("s", "smallExplosion", (EXPLOSION,)), 15: ("f", "indiscriminate"), 16: ("f", "deploy"),
    17: ("f", "deployDamageMultiplier"), 18: ("f", "tentacle"), 19: ("ssi", "spawner", (SPAWNER, MOUNT)),
    20: ("fi", "attackPriority"), 21: ("f", "detach"), 22: ("f", "canBeLocked"), 23: ("f", "sweeping"),
    24: ("f", "passOnHitEffect"), 25: ("s", "vent", (PARTICLE,)),
}
FEATURE_VALUES = {
    1: ("f", "life"), 2: ("s", "mesh", (MESH,)), 3: ("s", "explosion", (EXPLOSION,)), 4: ("f", "invincible"),
    5: ("s", "sound", (SOUND,)), 6: ("f", "lockable"), 7: ("i", "icon"),
}
HAZARD_VALUES = {
    1: ("f", "radius"), 2: ("s", "particle", (PARTICLE,)), 3: ("f", "damage"), 4: ("s", "sound", (SOUND,)),
}
VALUE_TABLES = {"unit": UNIT, "weapon": WEAPON_VALUES, "weapon-mode": WEAPON_MODE, "round": ROUND_VALUES,
                "spawner": SPAWNER_VALUES, "explosion": EXPLOSION_VALUES, "component": COMPONENT_VALUES,
                "feature": FEATURE_VALUES, "hazard": HAZARD_VALUES}


class PhysicsError(ValueError):
    """The file's framing cannot be walked; nothing past the failure is read."""


def read_body(body: bytes, signature: str) -> list:
    """A value's arguments, read in its signature's order; the body must be consumed exactly."""
    out, at = [], 0
    for letter in signature:
        if letter == "s":
            end = body.find(b"\0", at)
            if end < 0:
                raise ValueError("unterminated string")
            out.append(body[at:end].decode("latin-1"))
            at = end + 1
        else:
            if at + 4 > len(body):
                raise ValueError("body shorter than its signature")
            out.append(struct.unpack_from("<i" if letter == "i" else "<f", body, at)[0])
            at += 4
    if at != len(body):
        raise ValueError(f"body has {len(body) - at} unread bytes")
    return out


def named_references(kind: str, value_id: int, args: list) -> list[tuple[str, str]]:
    """(role, name) for each string of a value that names something; an empty string names nothing."""
    row = VALUE_TABLES[kind].get(value_id)
    if row is None or len(row) < 3:
        return []
    strings = [a for a, letter in zip(args, row[0]) if letter == "s"]
    return [(role, name) for role, name in zip(row[2], strings) if name]


def parse_physics(data: bytes) -> dict:
    """Every statement and value with its byte coordinates; PhysicsError when the framing does not hold."""
    if len(data) < 6:
        raise PhysicsError("shorter than a version and a terminator")
    (version,) = struct.unpack_from("<H", data, 0)
    if version != SUPPORTED_VERSION:
        raise PhysicsError(f"unsupported version {version}")

    def word(at: int, fmt: str = "<i") -> int:
        if at + 4 > len(data):
            raise PhysicsError("framing runs past the end of the file")
        return struct.unpack_from(fmt, data, at)[0]

    offset = 2
    statements = []
    while True:
        at = offset
        kind_id = word(offset)
        offset += 4
        if kind_id == -1:
            break
        if len(statements) >= MAX_STATEMENTS:
            raise PhysicsError("statement limit exceeded")
        kind = STATEMENT_KINDS.get(kind_id)
        if kind is None:
            raise PhysicsError(f"unknown statement type {kind_id}")
        declared = word(offset)
        offset += 4
        end = data.find(b"\0", offset)
        if end < 0:
            raise PhysicsError("unterminated statement name")
        name = data[offset:end].decode("latin-1")
        offset = end + 1
        values = []
        while True:
            if len(values) >= MAX_VALUES:
                raise PhysicsError("value limit exceeded")
            value_at = offset
            value_id = word(offset)
            size = word(offset + 4)
            offset += 8
            if not 0 <= size <= MAX_VALUE_BYTES or offset + size + 4 > len(data):
                raise PhysicsError(f"value {value_id} of {name!r} overruns the file")
            body = data[offset:offset + size]
            row = VALUE_TABLES[kind].get(value_id)
            entry = {"id": value_id, "offset": value_at, "bodyOffset": offset, "size": size,
                     "field": row[1] if row else None, "status": "unknown-id" if row is None else "read"}
            if row is not None:
                try:
                    entry["args"] = read_body(body, row[0])
                except ValueError as error:
                    entry["status"], entry["reason"] = "mis-sized", str(error)
            values.append(entry)
            offset += size
            marker = word(offset)
            offset += 4
            if marker == -1:
                break
            if marker != 0:
                raise PhysicsError(f"value list of {name!r} has an invalid continuation word")
        statements.append({"kind": kind, "name": name, "offset": at, "declaredSize": declared, "end": offset,
                           "values": values})
    return {"version": version, "statements": statements, "end": offset, "trailingBytes": len(data) - offset}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--game", type=Path, default=os.environ.get("BEA_GAME"), help="the game folder, only read")
    args = parser.parse_args(argv)
    if args.game is None:
        parser.error("name the game folder with --game or BEA_GAME")
    parsed = parse_physics((Path(args.game) / "data" / "default physics.dat").read_bytes())
    kinds = collections.Counter(s["kind"] for s in parsed["statements"])
    status = collections.Counter(v["status"] for s in parsed["statements"] for v in s["values"])
    roles = collections.Counter(role for s in parsed["statements"] for v in s["values"] if v["status"] == "read"
                                for role, _name in named_references(s["kind"], v["id"], v["args"]))
    print(f"statements {len(parsed['statements'])} {dict(sorted(kinds.items()))}")
    print(f"values {sum(status.values())} {dict(sorted(status.items()))}; trailing bytes {parsed['trailingBytes']}")
    print(f"named references {dict(sorted(roles.items()))}")
    return 1 if status["mis-sized"] or status["unknown-id"] or parsed["trailingBytes"] else 0


if __name__ == "__main__":
    sys.exit(main())
