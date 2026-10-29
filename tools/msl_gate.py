#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""The retail gate for tools/msl_compile.py: compile every mission script source an installed game holds and compare it with the compiled
script its level's world file ships.

For each world body of each installed level archive the gate takes every compiled script, finds its source at
data/MissionScripts/level<NNN>/<name>.msl (the real level for the real world, the base level for the base world; folder and file names in
any case) and compiles it with the compile session's counters taken from the shipped script (a constant's name, `const dataN`, comes from
a counter the source cannot give). A script is

  exact            every field of the record equal, and the record writes to the same bytes
  exact, assisted  the same, after an #include the game folder does not hold (a few sources name files only the developers had) is
                   treated as empty and the names it would have defined are taken from the shipped constants at their positions
  stale source     different, and listed in STALE_SOURCES: the installed .msl is not the source of the shipped script. Each entry says
                   how it differs; an entry that compiles exact (or is not found) fails, so the list cannot rot
  anything else    a failure: a difference nobody explained, a refusal, a script with no source

The gate reads the game folder and writes nothing. It needs an installed game (the Steam copy or a read-only view of it); the exit code is
0 only when no script falls under "anything else".

    python3 tools/msl_gate.py --game GAME [--table] [--level N]
"""
from __future__ import annotations

import argparse
import collections
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))

import msl_compile as mc  # noqa: E402
import world_resources_encode as wre  # noqa: E402

# (folder level, script name) -> how the installed source differs from the shipped script. Found by reading each difference: the shipped
# script has statements, variables or handlers the file lacks (or the reverse), so the file is another revision. Described by structure;
# the scripts themselves stay out of the repository.
STALE_SOURCES = {
    (201, "EnemyLander"): "the shipped script has a variable and a started_dying handler where the file has a died handler, and posts different events",
    (201, "EnemyLander2"): "the shipped script has a variable and a started_dying handler where the file has a died handler",
    (201, "LevelScript"): "the shipped script has a variable, different print statements and a different message call",
    (720, "battleline"): "the shipped script has an objective check (a lookup, an Exists call and an objective-complete call) the file lacks",
    (731, "Fenrir"): "the shipped script makes three more components invulnerable before its waypoint call than the file does (7 against 4), and none after it",
    (732, "Fenrir"): "the shipped script makes three more components invulnerable before its waypoint call than the file does (7 against 4), and none after it",
    (720, "Level720script"): "one message call names a different speaker than the file does",
}


def bytes_of(code: dict) -> bytes:
    writer = wre.Writer()
    wre.write_code(writer, code)
    return writer.bytes()


def scripts_of(game: Path, only_level: int | None = None):
    """(archive level, body tag, folder level, record) for each compiled script of each world body, in archive order."""
    for level, path in wre.level_archives(game).items():
        if only_level is not None and level != only_level:
            continue
        worlds = wre.level_worlds(b"".join(wre.inflate(wre.read_members(wre.read_retail(path)))))
        for tag, body in sorted(worlds["bodies"].items()):
            folder_level = worlds["realLevel"] if tag == "RLWD" else worlds["baseLevel"]
            for record in wre.read_world_model(body)["scripts"]:
                yield level, tag, folder_level, record


def assisted_resolver(record: dict):
    """Names a missing header would have defined: the shipped script's constant at the position where the compiler needs one."""
    symbols = record["code"]["symbols"]

    def resolve(_name: str, index: int):
        if index < len(symbols) and symbols[index]["name"].startswith("const data") and symbols[index]["dataType"] in mc.DT_NAME:
            return mc.DT_NAME[symbols[index]["dataType"]], symbols[index]["value"]
        return None

    return resolve


def judge(game: Path, read_include, folder_level: int, record: dict) -> tuple[str, str]:
    """(status, detail) for one shipped script."""
    name = record["name"]
    try:
        source = mc.read_game_source(game, f"data\\MissionScripts\\level{folder_level:03d}\\{name}.msl")
    except mc.MissingInclude as error:
        return "no source", f"{error.path} is not in the game folder"
    except mc.CompileError as error:
        return "no source", str(error)
    try:
        starts = (mc.const_start_of(record), mc.do_once_start_of(record))
    except mc.CompileError as error:
        return "refused", str(error)
    status = "exact"
    try:
        compiled = mc.compile_script(name, source, read_include, *starts)
    except mc.MissingInclude as error:
        status = "exact, assisted"
        missing = [error.path]

        def read_missing_as_empty(include: str) -> str:
            try:
                return read_include(include)
            except mc.MissingInclude as inner:
                if inner.path not in missing:
                    missing.append(inner.path)
                return ""

        try:
            compiled = mc.compile_script(name, source, read_missing_as_empty, *starts, resolve=assisted_resolver(record))
        except mc.CompileError as inner:
            return "refused", f"{inner} (without {', '.join(missing)})"
    except mc.CompileError as error:
        return "refused", str(error)
    difference = mc.first_difference(compiled, record)
    if difference is not None:
        return "different", difference
    if bytes_of(compiled["code"]) != bytes_of(record["code"]):
        return "different", "the compiled record writes to other bytes"
    return status, ""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--game", required=True, type=Path, help="an installed game folder (read only)")
    parser.add_argument("--table", action="store_true", help="print one tab-separated row per script")
    parser.add_argument("--level", type=int, help="only the archive of this level")
    args = parser.parse_args(argv)
    game = wre.selected_game_root(args.game)
    read_include = mc.includes_from(game)
    counts: collections.Counter = collections.Counter()
    failures: list[str] = []
    seen_stale: set = set()
    rows = []
    for level, tag, folder_level, record in scripts_of(game, args.level):
        status, detail = judge(game, read_include, folder_level, record)
        key = (folder_level, record["name"])
        if status == "different" and key in STALE_SOURCES:
            status, detail = "stale source", STALE_SOURCES[key]
            seen_stale.add(key)
        elif key in STALE_SOURCES:
            failures.append(f"{key[0]} {key[1]}: listed as a stale source but it is {status}")
            seen_stale.add(key)
        counts[status] += 1
        rows.append((level, tag, record["name"], status, detail))
        if status not in ("exact", "exact, assisted", "stale source"):
            failures.append(f"{level:03d} {tag} {record['name']}: {status}: {detail}")
    if not rows:
        failures.append("no compiled scripts were found to compare: choose a game folder whose data/resources holds level archives")
    if args.level is None:
        for key in sorted(set(STALE_SOURCES) - seen_stale):
            failures.append(f"{key[0]} {key[1]}: listed as a stale source but no such script was met")
    if args.table:
        print("level\tbody\tscript\tstatus\tdetail")
        for row in rows:
            print("\t".join(str(part) for part in row))
    print(f"{sum(counts.values())} scripts: " + ", ".join(f"{n} {status}" for status, n in sorted(counts.items())))
    for line in failures:
        print("FAIL", line)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
