#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Checks tools/named_things.py on authored world bodies (no game bytes): each loader rule that decides which things
join WORLD.mNamedThings, in which order, and which thing a name finds. The bodies are written by
tools/world_resources_encode.py and read back by tools/world_resources_decode.py, so the slots are the decoder's."""
from __future__ import annotations

import contextlib
import io
import struct
import tempfile
import unittest
import zlib
from pathlib import Path
from unittest.mock import patch

import cmsh_animation_usage_census_tests as mesh_fixtures
import content_catalog_gate as gate
import game_tables_decode_tests as tables
import named_things as nt
import world_resources_decode as wrd
import world_resources_encode as wre

# Unit definitions by behaviour (EUnitBehaviour): MECH and INFANTRY make a relaxed squad, AIRCRAFT, GROUND_UNIT and
# WARSPITE a normal one, TURRET none, JEEP none and no unit either.
BEHAVIOURS = {"Walker": 0, "Plane": 1, "Tank": 2, "Trooper": 3, "Turret": 4, "Jeep": 11, "Warspite": 21}
NATIVE_INDEX = {name: index for index, (name, _types) in enumerate(wrd.SCRIPT_NATIVES)}


def physics() -> dict:
    return {"units": set(BEHAVIOURS), "features": {"Rock"}, "hazards": {"Mine Field"},
            "squadless": {n for n, b in BEHAVIOURS.items() if nt.squad_class(b) is None}}


def init(name: str = "", *, script: str = "", attach: int = 0, **extra) -> dict:
    row = {"position": [0.0, 0.0, 0.0], "orientation": [0.0, 0.0, 0.0], "meshNumber": 0, "allegiance": 1,
           "target": -1, "script": script, "name": name, "spawnScript": "", "active": 1, "attachScriptsToUnits": attach}
    row.update(extra)
    return row


def unit(definition: str, name: str = "", *, dies_on: int = -1, oid: int = 8) -> dict:
    return {"oid": oid, "init": init(name), "definition": definition, "diesOn": dies_on}


def squad(definition: str, name: str = "", *, amount: int = 1, attach: int = 0, dies_on: int = -1) -> dict:
    return {"oid": 28, "init": init(name, attach=attach, squad={"amount": amount, "mode": 0}),
            "definition": definition, "diesOn": dies_on}


EXTRA = {
    7: {"tree": {"treeType": "pine"}},
    15: {"start": {"planeMode": 0, "playerNumber": 1}},
    19: {"spawner": {"amount": 1, "delay": 0.0, "squadDelay": 0.0, "initialDelay": 0.0, "squadSize": 1,
                     "spawnUnit": "Tank", "spawnerSpawnScript": ""}},
    26: {"cutscene": {"file": "intro", "linkTo": ""}},
    36: {"sphereTrigger": {"radius": 5.0}},
}


def marker(oid: int, name: str = "", *, script: str = "") -> dict:
    return {"oid": oid, "init": init(name, script=script, **EXTRA.get(oid, {}))}


def script(name: str, calls: list[tuple[str, list]]) -> dict:
    """A compiled script that pushes each call's arguments as constants (a str a string, a list a position; None: a
    variable, which holds no stored value and so is not a literal) and calls."""
    symbols, code = [], []
    for native, args in calls:
        for value in args:
            if value is None:
                symbols.append({"name": f"v{len(symbols)}", "dataType": 0, "value": None, "symbolType": 0, "index": 0,
                                "flag": 0})
            elif isinstance(value, list):
                symbols.append({"name": f"p{len(symbols)}", "dataType": 6, "value": value, "symbolType": 0,
                                "index": 0, "flag": 0})
            else:
                symbols.append({"name": f"s{len(symbols)}", "dataType": 3, "value": value, "symbolType": 0,
                                "index": 0, "flag": 0})
            code.append([wrd.OP_PUSH, len(symbols) - 1])
        code.append([wrd.OP_CALL, NATIVE_INDEX[native] | len(args) << 8])
    return {"name": name, "trailer": "00" * 10,
            "code": {"instructions": code, "eventPCs": [-1] * wrd.NUM_SCRIPT_EVENTS, "symbols": symbols,
                     "nextSymbolIndex": len(symbols), "eventFunctions": [], "tail": [0, 0]}}


def world_model(things: list[dict], *, version: int = 50, scripts: tuple = (), base_level: int = -1) -> dict:
    model = {"format": wre.MODEL_FORMAT, "version": version,
             "header": {"headerVersion": 3, "unused": [0, 0], "battleEngineConfigurations": [], "v2Words": [0, 0, 0],
                        "worldType": 0},
             "baseLevel": base_level, "scripts": list(scripts), "mapNumber": 0, "namedMeshes": [], "things": things,
             "treeGroups": [], "treeTypes": [],
             "influenceMap": {"version": 0, "nodes": 0, "nodeBytes": wre.blob(b""), "links": 0,
                              "linkBytes": wre.blob(b"")},
             "waypointPaths": [],
             "timings": {"oldF": 0.0, "oldG": 0.0, "oldH": 0.0, "preRun": 0.0, "pan": 0.0, "sGrade": 0, "dGrade": 0,
                         "timeLimit": 0.0, "fullScoreTime": 0.0, "percentageScoreTime": 0.0, "scorePercentage": 0.0}}
    if 45 <= version < 48:
        model["legacyTimings"] = [0, 0, 0, 0.0, 0.0]
    if version >= 47:
        model["occupancyGrids"] = [{"version": 0, "data": wre.blob(b"")} for _ in range(3)]
        if version < 50:
            model["legacyGridWords"] = [0] * 5
    if version >= 49:
        model["levelStartTime"] = 0.0
    return model


def body(things: list[dict], **kw) -> bytes:
    return wre.write_world_body(world_model(things, **kw))


def decode(things: list[dict], *, base: bool = False, **kw) -> dict:
    return wrd.parse_world_body(body(things, **kw), physics(), base=base)


def registry(real: list[dict] | None = None, base: list[dict] | None = None) -> dict:
    worlds = {}
    if base is not None:
        worlds["BSWD"] = decode(base, base=True)
    if real is not None:
        worlds["RLWD"] = decode(real)
    return nt.build_registry(worlds, BEHAVIOURS)


def where(entry: dict | None) -> tuple | None:
    return None if entry is None else (entry["world"], entry["slot"], entry["member"])


class OrderTests(unittest.TestCase):
    def test_the_most_recent_name_is_found_and_earlier_ones_are_shadowed(self) -> None:
        reg = registry(real=[unit("Turret", "Gun"), unit("Turret", "Gun")])
        found = nt.find(reg["entries"], "Gun")
        self.assertEqual(found["status"], "resolved")
        self.assertEqual([where(e) for e in found["candidates"]], [("RLWD", 1, None), ("RLWD", 0, None)])
        self.assertEqual(where(nt.find_by_walk(reg["entries"], "Gun")), ("RLWD", 1, None))

    def test_the_base_world_joins_before_the_real_world(self) -> None:
        reg = registry(base=[unit("Turret", "Gun"), unit("Turret", "Depot")], real=[unit("Turret", "Gun")])
        self.assertEqual([(e["world"], e["name"]) for e in reg["entries"]],
                         [("BSWD", "Gun"), ("BSWD", "Depot"), ("RLWD", "Gun")])
        found = nt.find(reg["entries"], "Gun")
        self.assertEqual((found["status"], where(found["entry"])), ("resolved", ("RLWD", 0, None)))
        self.assertEqual(where(found["candidates"][1]), ("BSWD", 0, None))

    def test_a_name_only_the_base_world_has_depends_on_the_career(self) -> None:
        reg = registry(base=[unit("Turret", "Depot"), unit("Turret", "Depot")], real=[unit("Turret", "Gun")])
        found = nt.find(reg["entries"], "Depot")
        self.assertEqual(found["status"], "career-dependent")
        self.assertEqual([where(e) for e in found["candidates"]], [("BSWD", 1, None), ("BSWD", 0, None)])
        self.assertTrue(all(e["conditional"] for e in found["candidates"]))
        dropped_last = nt.find_by_walk(reg["entries"], "Depot", kept=lambda e: e["slot"] != 1)
        self.assertEqual(where(dropped_last), ("BSWD", 0, None))
        self.assertIsNone(nt.find_by_walk(reg["entries"], "Depot", kept=lambda e: not e["conditional"]))

    def test_names_compare_as_c_strings(self) -> None:
        reg = registry(real=[unit("Turret", "Tank 1")])
        self.assertEqual(nt.find(reg["entries"], "tank 1")["status"], "unresolved")
        self.assertEqual(nt.find(reg["entries"], "Tank 1\0after the terminator")["status"], "resolved")
        self.assertEqual(nt.find(reg["entries"], "Tank")["status"], "unresolved")
        self.assertEqual(nt.find(reg["entries"], "")["status"], "unresolved")
        self.assertIsNone(nt.find_by_walk(reg["entries"], "tank 1"))
        self.assertIsNotNone(nt.find_by_walk(reg["entries"], "Tank 1\0x"))

    def test_the_walk_and_the_lookup_agree_on_every_name(self) -> None:
        reg = registry(base=[unit("Turret", "A"), squad("Trooper", "B", amount=2), unit("Turret", "C")],
                       real=[unit("Turret", "A"), marker(19, "B"), squad("Tank", "D", amount=3, attach=1),
                             marker(18, "C")])
        keeps = (lambda e: True, lambda e: not e["conditional"], lambda e: e["slot"] != 1)
        for name in ("A", "B", "C", "D", "E", "a"):
            found = nt.find(reg["entries"], name)
            self.assertIs(found["entry"], nt.find_by_walk(reg["entries"], name), name)
            for kept in keeps:
                walk = nt.find_by_walk(reg["entries"], name, kept)
                first_kept = next((e for e in found["candidates"] if kept(e)), None)
                self.assertIs(walk, first_kept, name)


class WhoJoinsTests(unittest.TestCase):
    def test_trees_and_waypoints_never_join(self) -> None:
        reg = registry(real=[marker(18, "Way"), marker(7, "Pine")])
        self.assertEqual(reg["entries"], [])
        for ordinal in (0, 1):
            outcome = reg["outcomes"][("RLWD", ordinal)]
            self.assertEqual((outcome["joins"], outcome["reason"]), (0, "not-a-complex-thing"))
        self.assertEqual(nt.find(reg["entries"], "Way")["status"], "unresolved")

    def test_a_record_without_a_slot_never_joins(self) -> None:
        reg = registry(base=[marker(15, "Start"), unit("Ghost", "Spook")], real=[unit("Ghost", "Spook")])
        self.assertEqual(reg["entries"], [])
        for key in (("BSWD", 0), ("BSWD", 1), ("RLWD", 0)):
            self.assertEqual(reg["outcomes"][key]["reason"], "no-slot", key)

    def test_every_other_named_kind_joins_as_itself(self) -> None:
        things = [marker(15, "Start"), marker(19, "Spawner"), marker(26, "Film"), marker(27, "Level"),
                  marker(36, "Zone"), unit("Rock", "Boulder", oid=35), unit("Mine Field", "Mines", oid=39),
                  unit("Turret", "Gun"), unit("Turret", "Hangar", oid=25)]
        reg = registry(real=things)
        self.assertEqual([(e["name"], e["object"], e["slot"]) for e in reg["entries"]],
                         [(t["init"]["name"], "thing", n) for n, t in enumerate(things)])

    def test_unnamed_records_are_not_outcomes(self) -> None:
        reg = registry(real=[unit("Turret"), marker(19)])
        self.assertEqual((reg["entries"], reg["outcomes"]), ([], {}))


class SquadTests(unittest.TestCase):
    def test_a_unit_whose_behaviour_has_a_squad_names_its_member(self) -> None:
        reg = registry(real=[unit("Walker", "Mech"), unit("Plane", "Wing"), unit("Turret", "Gun")])
        self.assertEqual([(e["name"], e["object"], e["member"]) for e in reg["entries"]],
                         [("Mech", "squad-member", 0), ("Wing", "squad-member", 0), ("Gun", "thing", None)])
        self.assertEqual([reg["outcomes"][("RLWD", n)].get("squad") for n in range(3)], ["relaxed", "normal", None])

    def test_a_relaxed_squad_names_each_member_and_the_last_is_found(self) -> None:
        reg = registry(real=[squad("Trooper", "Platoon", amount=3)])
        self.assertEqual([(e["object"], e["member"]) for e in reg["entries"]],
                         [("squad-members", 0), ("squad-members", 1), ("squad-members", 2)])
        self.assertEqual(nt.find(reg["entries"], "Platoon")["entry"]["member"], 2)

    def test_a_relaxed_squad_names_its_members_even_without_attached_scripts(self) -> None:
        for attach in (0, 1):
            reg = registry(real=[squad("Walker", "Lance", amount=2, attach=attach)])
            self.assertEqual([e["object"] for e in reg["entries"]], ["squad-members"] * 2, attach)

    def test_a_normal_squad_keeps_its_name_unless_it_attaches_scripts_to_units(self) -> None:
        kept = registry(real=[squad("Tank", "Column", amount=2, attach=0)])
        self.assertEqual([(e["object"], e["member"]) for e in kept["entries"]], [("squad", None)])
        given = registry(real=[squad("Tank", "Column", amount=2, attach=1)])
        self.assertEqual([(e["object"], e["member"]) for e in given["entries"]],
                         [("squad-members", 0), ("squad-members", 1)])

    def test_the_attach_flag_a_version_45_world_lacks_is_false(self) -> None:
        worlds = {"RLWD": wrd.parse_world_body(body([squad("Tank", "Column", amount=2)], version=45), physics(),
                                               base=False)}
        self.assertIsNone(worlds["RLWD"]["things"][0]["init"]["attachScriptsToUnits"])
        self.assertEqual([e["object"] for e in nt.build_registry(worlds, BEHAVIOURS)["entries"]], ["squad"])

    def test_an_empty_squad_names_nothing(self) -> None:
        for amount in (0, -2):
            reg = registry(real=[squad("Trooper", "Nobody", amount=amount)])
            self.assertEqual((reg["entries"], reg["outcomes"][("RLWD", 0)]["joins"]), ([], 0))

    def test_a_squad_whose_unit_has_no_squad_takes_no_slot(self) -> None:
        reg = registry(real=[squad("Turret", "Battery", amount=2)])
        self.assertEqual(reg["outcomes"][("RLWD", 0)]["reason"], "no-slot")

    def test_a_jeep_takes_a_slot_but_nothing_is_made(self) -> None:
        reg = registry(real=[unit("Jeep", "Car"), unit("Turret", "Gun")])
        outcome = reg["outcomes"][("RLWD", 0)]
        self.assertEqual((outcome["slot"], outcome["joins"], outcome["reason"]), (0, 0, "no-object"))
        self.assertEqual([e["slot"] for e in reg["entries"]], [1])


class BaseKeepTests(unittest.TestCase):
    def test_dies_on_at_a_slot_is_the_last_value_written_there(self) -> None:
        reg = registry(base=[unit("Ghost", dies_on=400), marker(19, "Watch"), unit("Turret", "Gun", dies_on=410),
                             marker(19, "Fresh"), unit("Ghost", dies_on=420), unit("Turret", "Own")])
        keep = {o["ordinal"]: o["keep"] for o in reg["outcomes"].values()}
        self.assertEqual(keep[1], {"careerBit": 0, "careerBitInRange": True, "diesOn": 400})
        self.assertEqual(keep[2]["diesOn"], 410)
        self.assertEqual(keep[3]["diesOn"], -1)
        self.assertEqual((keep[5]["careerBit"], keep[5]["diesOn"]), (3, -1))  # its own word replaces the failed one's
        self.assertTrue(all("keep" in e for e in reg["entries"]))

    def test_the_career_holds_288_base_thing_bits(self) -> None:
        things = [marker(18) for _ in range(287)] + [marker(19, "Last In"), marker(19, "First Out")]
        reg = registry(base=things)
        bits = {e["name"]: e["keep"] for e in reg["entries"]}
        self.assertEqual((bits["Last In"]["careerBit"], bits["Last In"]["careerBitInRange"]), (287, True))
        self.assertEqual((bits["First Out"]["careerBit"], bits["First Out"]["careerBitInRange"]), (288, False))

    def test_real_world_entries_are_unconditional(self) -> None:
        reg = registry(base=[unit("Turret", "A")], real=[unit("Turret", "B")])
        self.assertEqual([(e["name"], e["conditional"], "keep" in e) for e in reg["entries"]],
                         [("A", True, True), ("B", False, False)])

    def test_slots_out_of_loader_order_are_refused(self) -> None:
        world = decode([unit("Turret", "A"), unit("Turret", "B")])
        world["things"][1]["slot"] = 5
        with self.assertRaises(ValueError):
            nt.build_registry({"RLWD": world}, BEHAVIOURS)

    def test_registry_limit_counts_expansions_across_both_worlds_and_never_returns_a_partial_result(self) -> None:
        with patch.object(nt, "MAX_NAMED_REGISTRY_ENTRIES", 3):
            reg = registry(base=[squad("Trooper", "Base", amount=2)], real=[unit("Turret", "Real")])
            self.assertEqual([(e["name"], e["member"]) for e in reg["entries"]],
                             [("Base", 0), ("Base", 1), ("Real", None)])
            with self.assertRaisesRegex(nt.RegistryLimitError, "RLWD thing 0.*limit of 3"):
                registry(base=[squad("Trooper", "Base", amount=2)],
                         real=[squad("Trooper", "Real", amount=2)])
            with self.assertRaisesRegex(nt.RegistryLimitError, "limit of 3"):
                registry(real=[squad("Trooper", "Too many", amount=2_000_000_000)])
            # Nameless and non-joining records do not expand a named registry.
            self.assertEqual(len(registry(real=[squad("Trooper", "", amount=2_000_000_000),
                                                marker(18, "Waypoint")])["entries"]), 0)


class TableTests(unittest.TestCase):
    def test_squad_class_follows_spawn_squad(self) -> None:
        relaxed, normal = {0, 3}, {1, 2, 21}
        for behaviour in range(26):
            expected = "relaxed" if behaviour in relaxed else "normal" if behaviour in normal else None
            self.assertEqual(nt.squad_class(behaviour), expected, behaviour)
        self.assertEqual(nt.squad_class(26), "normal")  # SpawnSquad's default arm
        self.assertIsNone(nt.squad_class(None))

    def test_the_first_definition_of_a_name_decides(self) -> None:
        rows = [{"definition": "Twin", "factorySelector": 4}, {"definition": "Twin", "factorySelector": 0},
                {"definition": "Solo", "factorySelector": 3}]
        self.assertEqual(nt.first_behaviours(rows), {"Twin": 4, "Solo": 3})

    def test_runtime_names_are_the_literal_set_name_calls(self) -> None:
        code = decode([], scripts=(script("Namer", [("SetName", ["Later"]), ("SetName", [None]),
                                                     ("GetThingRef", ["Later"])]),))["scripts"][0]["code"]
        rows = nt.runtime_names(wrd.analyse_script(code)["calls"])
        self.assertEqual(rows, [{"pc": 1, "name": "Later"}, {"pc": 3, "name": None}])


def level_archive(base: bytes | None, real: bytes, level: int = 201, base_level: int = 10) -> bytes:
    """An authored level archive: one zlib member holding LVLR, TARG, AYAD and WRES/WRLD (WDAT, the bodies)."""
    def chunk(tag: bytes, payload: bytes) -> bytes:
        return tag + struct.pack("<I", len(payload)) + payload
    wrld = chunk(b"WDAT", struct.pack("<ii", base_level if base is not None else -1, level))
    wrld += (chunk(b"BSWD", base) if base is not None else b"") + chunk(b"RLWD", real)
    raw = (chunk(b"LVLR", struct.pack("<I", 103)) + chunk(b"TARG", struct.pack("<I", 1)) + chunk(b"AYAD", bytes(24))
           + chunk(b"WRES", chunk(b"WRLD", wrld)))
    member = zlib.compress(raw)
    return struct.pack("<I", len(member)) + member


# Serialized behaviour types (tools/cmsh_animation_usage_census.py UNIT_BEHAVIOR_SELECTOR_BY_SERIALIZED_TYPE): 5 is
# UB_TURRET, 3 UB_GROUND_UNIT, 2 UB_JEEP.
GATE_PHYSICS = mesh_fixtures._physics_fixture((1, "Turret", {8: struct.pack("<I", 5)}),
                                              (1, "Tank", {8: struct.pack("<I", 3)}),
                                              (1, "Jeep", {8: struct.pack("<I", 2)}))


class GateTests(unittest.TestCase):
    def run_gate(self, archives: dict[int, bytes]) -> tuple[int, str]:
        with tempfile.TemporaryDirectory() as temp:
            game = Path(temp)
            (game / "data" / "resources").mkdir(parents=True)
            (game / "data" / "default physics.dat").write_bytes(GATE_PHYSICS)
            tables.write_tables(game)
            for level, data in archives.items():
                (game / "data" / "resources" / f"{level:03d}_res_PC.aya").write_bytes(data)
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = gate.main(["--game", str(game), "--table"])
        return code, out.getvalue()

    def test_a_sound_level_passes_and_its_lookups_are_counted(self) -> None:
        finder = script("Finder", [("GetThingRef", ["Gun"]), ("GetThingRef", ["Depot"]), ("Teleport", ["Nobody"])])
        real = body([unit("Turret", "Gun"), marker(27, script="Finder")], scripts=(finder,), base_level=10)
        base = body([unit("Turret", "Gun"), unit("Turret", "Depot"), squad("Tank", "Column", amount=2, attach=1)])
        code, out = self.run_gate({201: level_archive(base, real)})
        self.assertEqual(code, 0, out)
        for line in ("literal GetThingRef resolved: 1", "literal GetThingRef career-dependent: 1",
                     "literal Teleport unresolved: 1", "entries BSWD squad-members: 2", "levels: 1",
                     "content catalogue gate: passed"):
            self.assertIn(line, out)

    def test_a_jeep_that_takes_a_slot_fails(self) -> None:
        code, out = self.run_gate({201: level_archive(None, body([unit("Jeep")]))})
        self.assertEqual(code, 1)
        self.assertIn("UB_JEEP", out)

    def test_a_registry_over_the_tool_limit_fails_the_gate_explicitly(self) -> None:
        with patch.object(nt, "MAX_NAMED_REGISTRY_ENTRIES", 2):
            code, out = self.run_gate({201: level_archive(None, body([squad("Tank", "Column", amount=3, attach=1)]))})
        self.assertEqual(code, 1)
        self.assertIn("201: the registry does not build", out)
        self.assertIn("limit of 2 entries", out)
        self.assertIn("content catalogue gate: failed", out)

    def test_a_named_base_slot_beyond_the_career_bits_fails(self) -> None:
        base = body([marker(18) for _ in range(288)] + [marker(19, "Far")])
        code, out = self.run_gate({201: level_archive(base, body([]))})
        self.assertEqual(code, 1)
        self.assertIn("has no career bit", out)

    def test_a_world_body_that_does_not_decode_fails(self) -> None:
        code, out = self.run_gate({201: level_archive(None, body([unit("Turret", "Gun")]) + b"\0")})
        self.assertEqual(code, 1)
        self.assertIn("do not decode", out)

    def test_a_folder_without_level_archives_fails(self) -> None:
        code, out = self.run_gate({})
        self.assertEqual(code, 1)
        self.assertIn("no level archive was checked", out)


if __name__ == "__main__":
    unittest.main()
