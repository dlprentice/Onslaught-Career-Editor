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
  stale source     different, and the complete shipped/compiled record pair has the listed identity. Each entry describes the observed
                   difference; an exact, missing or changed pair fails. The identity does not establish why the sources differ.
  anything else    a failure: a difference nobody explained, a refusal, a script with no source

The gate reads the game folder and writes nothing. It needs an installed game (the Steam copy or a read-only view of it); the exit code is
0 only when no script falls under "anything else".

    python3 tools/msl_gate.py --game GAME [--table] [--level N]
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))

import msl_compile as mc  # noqa: E402
import world_resources_encode as wre  # noqa: E402

# (folder level, script name) -> how the installed source differs from the shipped script. Found by reading each difference: the shipped
# script has statements, variables or handlers the file lacks (or the reverse), so the file is another revision. Each description is paired
# with a SHA-256 identity of the complete ordered shipped/compiled records. The identity pins the observation, not the explanation; no record
# or source bytes are stored here.
STALE_SOURCES = {
    (201, "EnemyLander"): ("the shipped script has a variable and a started_dying handler where the file has a died handler, and posts different events", "6a9d252f0c13f5dbb59b6aa6ef76de8429807a7cf6f81569837da3113681ecd1"),
    (201, "EnemyLander2"): ("the shipped script has a variable and a started_dying handler where the file has a died handler", "e31cf5fcb62eb5449e56d51d3e466f21cd9e26896ef2530cd56a85274f9975ba"),
    (201, "LevelScript"): ("the shipped script has a variable, different print statements and a different message call", "1fce2f4f0f7196e207ece2858d9f6e3501882b32981385be641213f853985643"),
    (720, "battleline"): ("the shipped script has an objective check (a lookup, an Exists call and an objective-complete call) the file lacks", "4b2531f3a62a9167538d62e414ef355c92c6b234bc937d5a12fb78da63f7c089"),
    (731, "Fenrir"): ("the shipped script makes three more components invulnerable before its waypoint call than the file does (7 against 4), and none after it", "7de058fce0c57dc5268915aa7e0e5412e96e062eea5e6b4f0c62eae38c2e27fd"),
    (732, "Fenrir"): ("the shipped script makes three more components invulnerable before its waypoint call than the file does (7 against 4), and none after it", "1e904da457100866ded5140b05eb4195d4de0d21296bf02ecf683056f5d5482e"),
    (720, "Level720script"): ("one message call names a different speaker than the file does", "6c0ada717734b58333d42e74b20f5bcff81569e59fd92c276f33c0e8543eef5b"),
}


def bytes_of(code: dict) -> bytes:
    writer = wre.Writer()
    wre.write_code(writer, code)
    return writer.bytes()


def record_bytes(record: dict) -> bytes:
    """The complete stored record, used only in memory for an identity check."""
    writer = wre.Writer()
    writer.lstring(record["name"], "i")
    wre.write_code(writer, record["code"])
    trailer = bytes.fromhex(record["trailer"])
    if len(trailer) != 10:
        raise wre.EncodeError("a script trailer is 10 bytes")
    writer.raw(trailer)
    return writer.bytes()


def stale_identity(shipped: dict, compiled: dict) -> str:
    """A SHA-256 fingerprint of the ordered pair; it pins the observed difference, not its reason."""
    pair = hashlib.sha256(record_bytes(shipped)).digest() + hashlib.sha256(record_bytes(compiled)).digest()
    return hashlib.sha256(b"onslaught-stale-pair-v1\0" + pair).hexdigest()


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


def source_path(game: Path, folder_level: int, name: str) -> Path:
    return mc.game_file(game, f"data\\MissionScripts\\level{folder_level:03d}\\{name}.msl")


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
    status, detail, _compiled = judge_record(game, read_include, folder_level, record)
    return status, detail


def judge_record(game: Path, read_include, folder_level: int, record: dict) -> tuple[str, str, dict | None]:
    """As judge, also retaining the compiled record in memory for the stale-pair identity."""
    name = record["name"]
    try:
        path = source_path(game, folder_level, name)
    except mc.MissingInclude as error:
        return "no source", f"{error.path} is not in the game folder", None
    except mc.CompileError as error:
        return "no source", str(error), None
    source = mc.read_source(path)
    starts = (mc.const_start_of(record), mc.do_once_start_of(record))
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
            return "refused", f"{inner} (without {', '.join(missing)})", None
    except mc.CompileError as error:
        return "refused", str(error), None
    difference = mc.first_difference(compiled, record)
    if difference is not None:
        return "different", difference, compiled
    if bytes_of(compiled["code"]) != bytes_of(record["code"]):
        return "different", "the compiled record writes to other bytes", compiled
    return status, "", compiled


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
        status, detail, compiled = judge_record(game, read_include, folder_level, record)
        key = (folder_level, record["name"])
        if status == "different" and key in STALE_SOURCES:
            seen_stale.add(key)
            description, expected = STALE_SOURCES[key]
            try:
                matches = compiled is not None and stale_identity(record, compiled) == expected
            except (wre.EncodeError, ValueError, TypeError, KeyError, OverflowError):
                matches = False
            if matches:
                status, detail = "stale source", description
            else:
                detail = "the pinned stale source comparison changed or could not be checked"
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
