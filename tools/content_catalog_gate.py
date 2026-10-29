#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""The retail gate for the content catalogue's loader-rule decoders: run them over an installed game and check what
only the real data can show. tools/content_catalog_tests.py and tools/named_things_tests.py check the rules on
authored data; this checks that the shipped data meets the rules' assumptions and that the two ways of answering a
lookup agree on every real case.

named things (tools/named_things.py), for every level archive:
  - every world body decodes in CWorld::LoadWorld's order (tools/world_resources_decode.py) and its slots are the
    loader's (in record order, from 0)
  - every registry entry names a slotted record whose class reaches CComplexThing::Init (not a tree or waypoint), under
    that record's own name; the base world's entries come before the real world's; every base-world slot that joins
    has a career bit (the career keeps 288)
  - no record takes a slot with nothing made for it (a UB_JEEP unit), which LoadWorld would initialise as a null thing
  - for every literal thing name of every script of the level (GetThingRef, Teleport, PlayCutscene) and every
    cutscene's link-to name, the lookup (named_things.find) agrees with the loader's walk (named_things.find_by_walk)
    with every base-world thing kept, with none kept and with only every other one kept

The gate reads the game folder and writes nothing. It prints counts (and, with --table, one row per level, derived
from the game: keep it private); the exit code is 0 only when every check passes.

    python3 tools/content_catalog_gate.py --game GAME [--table] [--level N]
"""
from __future__ import annotations

import argparse
import collections
import struct
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(TOOLS.parent / "rebuild" / "tools"))

import cmsh_animation_usage_census as meshcensus  # noqa: E402
import content_catalog as cc  # noqa: E402
import named_things as nt  # noqa: E402
import world_resources_decode as wrd  # noqa: E402
import world_resources_encode as wre  # noqa: E402

KEEPS = {"all base things kept": lambda e: True, "no base thing kept": lambda e: not e["conditional"],
         "every other base slot kept": lambda e: not e["conditional"] or e["slot"] % 2 == 0}


def physics_of(game: Path) -> tuple[dict, dict]:
    """The definition lookups parse_world_body needs, and unit name -> behaviour (the first definition of a name)."""
    data = cc.read_install_file(game / "data" / "default physics.dat")
    names = cc.physics_names(data)
    behaviours = nt.first_behaviours(meshcensus._physics_mesh_definitions(data)["unitDefinitions"])
    lookup = {"units": set(names["unit"]), "features": set(names["feature"]), "hazards": set(names["hazard"]),
              "squadless": {n for n, b in behaviours.items() if nt.squad_class(b) is None}}
    return lookup, behaviours


def level_bodies(path: Path) -> dict:
    return wre.level_worlds(b"".join(wre.inflate(wre.read_members(wre.read_retail(path)))))


def thing_name_literals(worlds: dict) -> list[tuple[str, str, str, str]]:
    """(world, script, native, name) for each string literal a script passes as a thing name, and (world, cutscene
    ordinal, "cutscene link", name) for each cutscene's link-to name (CCutscene::Start looks it up)."""
    out = []
    for tag in ("RLWD", "BSWD"):
        for t in worlds.get(tag, {}).get("things", []):
            if t["init"].get("cutscene", {}).get("linkTo"):
                out.append((tag, f"cutscene {t['ordinal']}", "cutscene link", t["init"]["cutscene"]["linkTo"]))
    for tag in ("RLWD", "BSWD"):
        for s in worlds.get(tag, {}).get("scripts", []):
            for c in wrd.analyse_script(s["code"])["calls"]:
                for k, arg in enumerate(c["args"]):
                    if (wrd.ARG_ROLES.get((c["native"], k)) == "thing-name" and arg is not None
                            and isinstance(arg["value"], str)):
                        out.append((tag, s["name"], c["native"], arg["value"]))
    return out


def check_named_things(level: int, worlds: dict, behaviours: dict, counts: collections.Counter,
                       failures: list[str]) -> dict:
    """The named-things checks for one level's decoded worlds; returns the level's table row."""
    reg = nt.build_registry(worlds, behaviours)
    entries = reg["entries"]
    by_key = {(tag, t["ordinal"]): t for tag, w in worlds.items() for t in w["things"]}
    seen_real = False
    for n, e in enumerate(entries):
        t = by_key[(e["world"], e["ordinal"])]
        problems = []
        if e["order"] != n:
            problems.append("its order is not its place")
        if t["slot"] is None or t["oid"] in nt.NOT_COMPLEX:
            problems.append("its record takes no slot or is a tree or waypoint")
        if not e["name"] or e["name"] != t["init"]["name"]:
            problems.append("its name is not its record's")
        if e["world"] == "RLWD":
            seen_real = True
        elif seen_real:
            problems.append("a base-world entry after a real-world one")
        if e["conditional"] and not e["keep"]["careerBitInRange"]:
            problems.append(f"base slot {e['slot']} has no career bit (the career keeps {nt.CAREER_BASE_BITS})")
        for p in problems:
            failures.append(f"{level:03d} entry {n} ({e['world']} slot {e['slot']}): {p}")
    for (tag, _ordinal), t in by_key.items():
        if t["slot"] is not None and t["oid"] in (nt.OID_UNIT, nt.OID_BUILDING) \
                and behaviours.get(t["definition"]) == nt.UB_JEEP:
            failures.append(f"{level:03d} {tag} thing {t['ordinal']}: a UB_JEEP unit takes a slot, and LoadWorld would "
                            "initialise a null thing")
    runtime = {nt.strcmp_key(r["name"]) for tag in worlds for s in worlds[tag]["scripts"]
               for r in nt.runtime_names(wrd.analyse_script(s["code"])["calls"]) if r["name"]}
    statuses: collections.Counter = collections.Counter()
    named_records = {t["init"]["name"] for t in by_key.values() if t["init"]["name"]}
    for tag, script, native, name in thing_name_literals(worlds):
        found = nt.find(entries, name)
        status = found["status"]
        if status == "unresolved" and nt.strcmp_key(name) and nt.strcmp_key(name) in runtime:
            status = "runtime-name"
        statuses[status] += 1
        counts[f"literal {native} {status}"] += 1
        if status == "unresolved" and nt.strcmp_key(name) in named_records:
            counts["literal names a record that never joins"] += 1
        if status == "resolved" and len({(e["world"], e["ordinal"]) for e in found["candidates"]}) > 1:
            counts["literal finds one of several records"] += 1
        for label, kept in KEEPS.items():
            walk = nt.find_by_walk(entries, name, kept)
            expected = next((e for e in found["candidates"] if kept(e)), None)
            if walk is not expected:
                failures.append(f"{level:03d} {tag} {script} {native}: the lookup and the walk disagree ({label})")
    names = collections.Counter(e["name"] for e in entries)
    not_joined = collections.Counter(o.get("reason") or "empty squad" for o in reg["outcomes"].values()
                                     if not o["joins"])
    for e in entries:
        counts[f"entries {e['world']} {e['object']}"] += 1
    for reason, n in not_joined.items():
        counts[f"named records not joined: {reason}"] += n
    counts["levels"] += 1
    counts["names on several entries"] += sum(1 for c in names.values() if c > 1)
    counts["runtime names"] += len(runtime)
    return {"level": f"{level:03d}", "base": sum(e["conditional"] for e in entries),
            "real": sum(not e["conditional"] for e in entries), "names": len(names),
            "several": sum(1 for c in names.values() if c > 1), "notJoined": dict(sorted(not_joined.items())),
            "literals": dict(sorted(statuses.items()))}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--game", required=True, type=Path, help="an installed game folder (read only)")
    parser.add_argument("--table", action="store_true", help="print one tab-separated row per level")
    parser.add_argument("--level", type=int, help="only the archive of this level")
    args = parser.parse_args(argv)
    game = wre.selected_game_root(args.game)
    lookup, behaviours = physics_of(game)
    counts: collections.Counter = collections.Counter()
    failures: list[str] = []
    rows = []
    for level, path in wre.level_archives(game).items():
        if args.level is not None and level != args.level:
            continue
        try:
            raw = level_bodies(path)
            worlds = {tag: wrd.parse_world_body(body, lookup, base=tag == "BSWD")
                      for tag, body in sorted(raw["bodies"].items())}
        except (wre.EncodeError, wrd.DecodeError, struct.error, ValueError) as error:
            failures.append(f"{level:03d}: the world bodies do not decode: {error}")
            continue
        try:
            rows.append(check_named_things(level, worlds, behaviours, counts, failures))
        except ValueError as error:
            failures.append(f"{level:03d}: the registry does not build: {error}")
    if not rows:
        failures.append("no level archive was checked: choose a game folder whose data/resources holds level archives")
    if args.table:
        print("level\tbase entries\treal entries\tnames\tnames on several\tnot joined\tliterals")
        for r in rows:
            print("\t".join(str(r[k]) for k in ("level", "base", "real", "names", "several", "notJoined", "literals")))
    for key in sorted(counts):
        print(f"{key}: {counts[key]}")
    for line in failures:
        print("FAIL", line)
    print("content catalogue gate: " + ("failed" if failures else "passed") + f" ({len(failures)} failures)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
