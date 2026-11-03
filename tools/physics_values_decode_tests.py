#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Checks tools/physics_values_decode.py on authored physics scripts (no game bytes), and checks its value tables
against the rebuild's typed reader they were taken from, so the two cannot drift apart unnoticed."""
from __future__ import annotations

import re
import struct
import unittest
from pathlib import Path

import physics_values_decode as physics

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "rebuild" / "OnslaughtRebuild.Parity" / "Physics"
FUNCTIONS = {"ApplyUnitValue": "unit", "ApplyFeatureValue": "feature", "ApplyHazardValue": "hazard",
             "ApplyWeaponValue": "weapon", "ApplyWeaponModeValue": "weapon-mode", "ApplyRoundValue": "round",
             "ApplySpawnerValue": "spawner", "ApplyExplosionValue": "explosion", "ApplyComponentValue": "component"}


def script(*statements: tuple[int, str, list[tuple[int, bytes]]], version: int = 18, tail: bytes = b"") -> bytes:
    out = bytearray(struct.pack("<H", version))
    for kind, name, values in statements:
        body = bytearray(name.encode("ascii") + b"\0")
        for number, (value_id, value) in enumerate(values):
            body += struct.pack("<II", value_id, len(value)) + value
            body += struct.pack("<i", -1 if number + 1 == len(values) else 0)
        out += struct.pack("<II", kind, len(body)) + body
    return bytes(out + struct.pack("<i", -1) + tail)


def text(value: str) -> bytes:
    return value.encode("ascii") + b"\0"


class ParseTests(unittest.TestCase):
    def test_values_read_by_their_classes(self):
        data = script((1, "Tank", [(9, text("tank.msh")), (3, struct.pack("<f", 50.0)),
                                   (7, text("Cannon") + text("GunA") + struct.pack("<i", 2)), (54, text("rumble"))]),
                      (6, "Boom", [(2, text("fire")), (10, text("bang"))]),
                      (2, "Cannon", [(5, text("cannon_icon"))]),
                      (4, "Shell", [(13, b""), (8, text("trail"))]))
        parsed = physics.parse_physics(data)
        self.assertEqual(parsed["trailingBytes"], 0)
        self.assertEqual([s["kind"] for s in parsed["statements"]], ["unit", "explosion", "weapon", "round"])
        tank = parsed["statements"][0]["values"]
        self.assertEqual([v["status"] for v in tank], ["read"] * 4)
        self.assertEqual(tank[2]["args"], ["Cannon", "GunA", 2])
        refs = [(s["kind"], role, name) for s in parsed["statements"] for v in s["values"]
                for role, name in physics.named_references(s["kind"], v["id"], v["args"])]
        self.assertEqual(refs, [("unit", "mesh", "tank.msh"), ("unit", "weapon", "Cannon"), ("unit", "mount", "GunA"),
                                ("unit", "sound-effect", "rumble"), ("explosion", "particle-effect", "fire"),
                                ("explosion", "sound-effect", "bang"), ("weapon", "icon", "cannon_icon"),
                                ("round", "particle-effect", "trail")])
        self.assertEqual(parsed["statements"][3]["values"][0]["args"], [])

    def test_a_value_no_class_knows_stays_unread(self):
        parsed = physics.parse_physics(script((8, "Rock", [(99, b"\1\2\3\4"), (2, text("rock.msh"))])))
        self.assertEqual([v["status"] for v in parsed["statements"][0]["values"]], ["unknown-id", "read"])
        self.assertNotIn("args", parsed["statements"][0]["values"][0])

    def test_a_body_its_class_does_not_consume_exactly_is_mis_sized(self):
        parsed = physics.parse_physics(script((9, "Mud", [(1, struct.pack("<f", 1.0) + b"x"), (2, b"no terminator"),
                                                          (3, b"ab")])))
        values = parsed["statements"][0]["values"]
        self.assertEqual([v["status"] for v in values], ["mis-sized"] * 3)
        self.assertEqual([v["reason"] for v in values],
                         ["body has 1 unread bytes", "unterminated string", "body shorter than its signature"])

    def test_empty_strings_name_nothing(self):
        self.assertEqual(physics.named_references("feature", 2, [""]), [])
        self.assertEqual(physics.named_references("feature", 99, ["x"]), [])
        self.assertEqual(physics.named_references("unit", 3, [1.0]), [])

    def test_trailing_bytes_are_counted(self):
        self.assertEqual(physics.parse_physics(script((8, "Rock", [(1, struct.pack("<f", 1.0))]), tail=b"xy"))
                         ["trailingBytes"], 2)

    def test_refusals(self):
        good = script((8, "Rock", [(1, struct.pack("<f", 1.0))]))
        cases = {
            "shorter than a version and a terminator": b"\x12\0",
            "unsupported version 17": script(version=17),
            "framing runs past the end of the file": good[:-4],
            "unknown statement type 42": script((42, "x", [(1, b"")])),
            "unterminated statement name": struct.pack("<HII", 18, 8, 0) + b"Rock",
            "value 1 of 'Rock' overruns the file": good[:2 + 8 + 5] + struct.pack("<II", 1, 999) + good[2 + 8 + 5 + 8:],
            "value list of 'Rock' has an invalid continuation word": good[:-8] + struct.pack("<i", 5) + good[-4:],
        }
        for reason, data in cases.items():
            with self.subTest(reason=reason):
                with self.assertRaises(physics.PhysicsError) as caught:
                    physics.parse_physics(data)
                self.assertEqual(str(caught.exception), reason)

    def test_the_limits_hold(self):
        many = script(*[(8, f"R{n}", [(1, struct.pack("<f", 1.0))]) for n in range(3)])
        statements, values = physics.MAX_STATEMENTS, physics.MAX_VALUES
        try:
            physics.MAX_STATEMENTS = 2
            with self.assertRaisesRegex(physics.PhysicsError, "statement limit exceeded"):
                physics.parse_physics(many)
            physics.MAX_STATEMENTS, physics.MAX_VALUES = statements, 1
            with self.assertRaisesRegex(physics.PhysicsError, "value limit exceeded"):
                physics.parse_physics(script((8, "R", [(1, struct.pack("<f", 1.0)), (4, struct.pack("<f", 0.0))])))
        finally:
            physics.MAX_STATEMENTS, physics.MAX_VALUES = statements, values


def rebuild_signatures() -> dict[str, dict[int, str]]:
    """Each Apply*Value's case ids and the reads it makes, from the rebuild's C#: Int i, Float f, String s, and the
    unit helpers UnitString (one string) and UnitFlag (one int)."""
    source = "\n".join(path.read_text(encoding="utf-8") for path in sorted(REGISTRY.glob("PhysicsRegistry*.cs")))
    out: dict[str, dict[int, str]] = {}
    for match in re.finditer(r"private (?:static )?bool (Apply\w+Value)\([^)]*\)\s*\{(.*?)\n    \}\n", source, re.S):
        family = FUNCTIONS.get(match.group(1))
        if family is None:
            continue
        rows: dict[int, str] = {}
        cases = list(re.finditer(r"case (\d+(?: or \d+)*):", match.group(2)))
        for number, case in enumerate(cases):
            end = cases[number + 1].start() if number + 1 < len(cases) else match.group(2).find("default:")
            body = match.group(2)[case.end():end]
            reads = re.findall(r"r\.(Int|Float|String)\(\)|(UnitString)\(|(UnitFlag)\(", body)
            signature = "".join("s" if s else "i" if flag else kind[0].lower() for kind, s, flag in reads)
            for value_id in case.group(1).split(" or "):
                rows[int(value_id)] = signature
        out[family] = rows
    return out


@unittest.skipUnless(REGISTRY.is_dir(), "the rebuild's physics reader is not in this checkout")
class RebuildTableTests(unittest.TestCase):
    def test_every_value_class_reads_what_the_rebuild_reads(self):
        signatures = rebuild_signatures()
        self.assertEqual(sorted(signatures), sorted(physics.VALUE_TABLES))
        for family, table in physics.VALUE_TABLES.items():
            with self.subTest(family=family):
                ours = {value_id: row[0] for value_id, row in table.items()}
                self.assertEqual(ours, signatures[family])

    def test_every_string_has_a_role_and_no_role_names_a_number(self):
        for family, table in physics.VALUE_TABLES.items():
            for value_id, row in table.items():
                roles = row[2] if len(row) > 2 else ()
                self.assertLessEqual(len(roles), row[0].count("s"), f"{family} {value_id}")


if __name__ == "__main__":
    unittest.main()
