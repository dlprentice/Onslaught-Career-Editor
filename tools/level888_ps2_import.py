#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Level 888 (Flagship Duel), the level the PC release cut, built on the player's machine from their own PS2 copy of Battle Engine Aquila.

The PS2 disc carries a level archive that the PC release does not: 888, a Fenrir against a Venturer. This tool reads that archive from the image the
player supplies (a plain ISO or a Redump zip: tools/ps2_disc.py, read only, nothing written), takes its world as it is (the units, the start points, the
waypoints and the three scripts the disc holds) and builds a CE mod from it and from this game's own files with the level 888 generator
(tools/level888_build.py: the PC game's terrain, the descriptors the ships need, and the Fenrir mesh converted from the disc, below). Nothing derived from the image is committed,
shipped or sent anywhere: the mod is written to a folder the player names, and `stage` copies it into the CE folder only when the player runs it.

    level888_ps2_import.py inspect SOURCE                           counts about the member and its world (never names or bytes)
    level888_ps2_import.py build SOURCE --game GAME --out PARENT --ce-min 0.1.13 [--id flagship-duel-ps2] [--strict-pins]
                                                                     PARENT/<id>/ (mod.json, data/resources/888_res_PC.aya; no game file is replaced)
    level888_ps2_import.py stage MODDIR [--user-dir DIR] [--into-my-real-folder] [--replace] [--dry-run]
                                                                     copy the mod into a FRESH CE user folder (your careers and settings stay where they are)
                                                                     and print the one line that starts the level in it

SOURCE is the image (a plain ISO, or a Redump zip whose one member is the ISO) or the extracted member itself (a file that starts with the tag LVLR).
The one mesh the PS2 copy names and the PC game has no file for (the multiplayer Fenrir) is converted from the disc (tools/ps2_mesh.py) and carried inside the
level archive as its one unnamed MESH chunk, so the mod replaces no game file and conflicts with no other mod; its terrain
is the PC game's level 857 (the disc's own terrain decodes equal to it) without that level's baked shadows, which the disc's own shadow chunk replaces (none); and CE adds no entry for the level (start it with -level 888 on
the game's command line). CE loads mods on Linux only, and keeps them off in replays, recordings, probes, virtual clocks, pilots and network sessions.

`stage` puts the mod in a fresh CE user folder (default: onslaught-ce-level888 beside CE's own) and prints the line that starts the level there
(BEA_USER_DIR=<folder> onslaught-ce -level 888): the level's end screen takes the single-player route and writes a career, until a CE build with the bonus-level
fence is the one that runs, so it must not run on your own careers. It refuses CE's own user folder (and the one BEA_USER_DIR names) unless --into-my-real-folder
is given, and always refuses a folder that holds one of them or lies inside it (by name, link or device and inode). It keeps an existing ce.ini as ce.ini.bak-<time> first,
edits the mods= line as CE reads it (two such lines are refused), never overwrites a mod folder (--replace moves the old one aside), puts nothing in place until the
copy has been checked against mod.json, puts everything back if a step fails, and does nothing while --dry-run is given. Close the game before it runs."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import shutil
import stat
import sys
import time
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))

import level888_build as lvl  # noqa: E402
import ps2_disc  # noqa: E402
import ps2_mesh  # noqa: E402
import world_resources_encode as enc  # noqa: E402

MOD_ID = "flagship-duel-ps2"
MOD_NAME = "Flagship duel (level 888, from your PS2 copy)"
FRESH_FOLDER = "onslaught-ce-level888"
STAND_IN_ID = lvl.MOD_ID                 # the generator's own mod, which adds the same archive: only one of the two can be active
MEMBER_TAG = b"LVLR"
ID_CHARS = set("abcdefghijklmnopqrstuvwxyz0123456789-_")
MAX_INI = 1 << 20


class ImportFailure(ValueError):
    """The source, the folder or the CE user folder cannot be used as asked; the message says why."""


# ---- the member ---------------------------------------------------------------------------------------------------------
def read_source(source: Path, *, strict_pins: bool = False) -> tuple[bytes, dict]:
    """The 888 member's bytes and a record of where they came from: an extracted member (a file that starts with the archive tag) or the member of an image."""
    try:
        fd = os.open(source, os.O_RDONLY | os.O_NONBLOCK | getattr(os, "O_CLOEXEC", 0))
    except OSError as error:
        raise ImportFailure(f"cannot read {source}: {error.strerror or error}") from None
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise ImportFailure(f"{source} is not a regular file")
        head = os.read(fd, 4)
    except OSError as error:
        raise ImportFailure(f"cannot read {source}: {error.strerror or error}") from None
    finally:
        os.close(fd)
    if head != MEMBER_TAG:
        try:
            member = ps2_disc.read_member(source, strict_pins=strict_pins)
        except ps2_disc.Ps2DiscError as error:
            raise ImportFailure(str(error)) from error
        return member.data, {"from": "image", "bytes": member.size, "sha256": member.sha256, "warnings": list(member.warnings),
                             "passes": member.passes}
    size = source.stat().st_size
    if size > ps2_disc.MAX_MEMBER_BYTES:
        raise ImportFailure(f"{source} is {size} bytes, more than the {ps2_disc.MAX_MEMBER_BYTES}-byte ceiling for a member")
    data = source.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    pin = ps2_disc.MEMBER_SHA256.get(ps2_disc.fold_member_path(ps2_disc.LEVEL_888_MEMBER))
    warnings = [] if digest == pin else [f"the member's SHA-256 is {digest}, not the pinned {pin}"]
    if warnings and strict_pins:
        raise ImportFailure("; ".join(warnings))
    return data, {"from": "member", "bytes": len(data), "sha256": digest, "warnings": warnings, "passes": 0}


def world_body(member: bytes) -> bytes:
    """The world of level 888 in the member: WDAT naming no base world and level 888, and one RLWD body, nothing else."""
    try:
        worlds = enc.level_worlds(member)
    except (enc.EncodeError, ValueError, KeyError, IndexError) as error:
        raise ImportFailure(f"the member has no readable world: {error}") from error
    if worlds["realLevel"] != lvl.LEVEL or worlds["baseLevel"] != -1:
        raise ImportFailure(f"the member's world is level {worlds['realLevel']} on base {worlds['baseLevel']}, not level {lvl.LEVEL} with no base")
    if sorted(worlds["bodies"]) != ["RLWD"]:
        raise ImportFailure(f"the member's world has the bodies {sorted(worlds['bodies'])}, not one RLWD")
    return worlds["bodies"]["RLWD"]


def shadow_chunk(member: bytes) -> bytes:
    """The member's one SSHD chunk (its static shadows: none, on the disc's level 888)."""
    found = [member[at:at + size] for tag, at, size in enc.chunks(member) if tag == "SSHD"]
    if len(found) != 1:
        raise ImportFailure(f"the member has {len(found)} shadow chunks, not one")
    return found[0]


def inspect(member: bytes) -> dict:
    """Counts only: the chunks by tag, the world's header fields, its things by kind, its scripts and waypoint paths. No name and no byte of the member."""
    tags: dict[str, int] = {}
    accounted = 0
    for tag, at, size in enc.chunks(member):
        tags[tag] = tags.get(tag, 0) + 1
        accounted += 8 + size
    body = world_body(member)
    model = enc.read_world_model(body)
    kinds: dict[str, int] = {}
    for thing in model["things"]:
        kinds[thing["kind"]] = kinds.get(thing["kind"], 0) + 1
    header = model["header"]
    return {"bytes": len(member), "sha256": hashlib.sha256(member).hexdigest(), "chunks": sum(tags.values()), "everyByteAccounted": accounted == len(member),
            "chunksByTag": dict(sorted(tags.items())), "world": {"version": model["version"], "bodyBytes": len(body), "shadowBytes": len(shadow_chunk(member)), "worldType": header.get("worldType"),
                                                                 "configurations": len(header.get("battleEngineConfigurations", [])),
                                                                 "things": len(model["things"]), "thingsByKind": dict(sorted(kinds.items())),
                                                                 "scripts": len(model["scripts"]), "waypointPaths": len(model["waypointPaths"]),
                                                                 "readsBackUnchanged": enc.write_world_body(model) == body}}


# ---- the build ----------------------------------------------------------------------------------------------------------
def build(source: Path, game: Path, out: Path, *, ce_min: str, mod_id: str = MOD_ID, name: str = MOD_NAME, version: str = "1", author: str = "",
          ce_max: str | None = None, strict_pins: bool = False) -> tuple[dict, dict]:
    """Read the member, build the mod with the disc's world and stage it as <out>/<mod_id>/. Returns (the staging summary, the build report with the source).
    The Fenrir the PS2 copy uses is converted (ps2_mesh.py) and carried in the level archive as an inline mesh; the physics file is left alone and no game file is
    replaced. A member without that mesh, or one the converter cannot read, is refused by name (there is no stand-in to fall back to)."""
    member, record = read_source(source, strict_pins=strict_pins)
    body = world_body(member)
    install = lvl.Install(game, strict_pins=strict_pins)
    try:
        inline = {lvl.FENRIR_FILELESS_MESH: ps2_mesh.convert_member_mesh(member, lvl.FENRIR_FILELESS_MESH)}
        result = lvl.build(install, world_body=body, shadows=shadow_chunk(member), inline_meshes=inline)
        summary = lvl.stage_build(result, enc.selected_game_root(game), out, ce_min=ce_min, mod_id=mod_id, name=name, version=version, author=author,
                                  ce_max=ce_max)
    except (lvl.BuildError, enc.EncodeError, ps2_mesh.Ps2MeshError) as error:
        raise ImportFailure(str(error)) from error
    report = dict(result.report) | {"member": record}
    report["warnings"] = list(result.warnings) + record["warnings"]
    return summary, report


# ---- stage ---------------------------------------------------------------------------------------------------------------
def ce_user_folder(env=os.environ) -> Path:
    """CE's user folder on Linux: $XDG_DATA_HOME/onslaught-ce, or ~/.local/share/onslaught-ce when that is unset."""
    base = env.get("XDG_DATA_HOME") or str(Path.home() / ".local" / "share")
    return Path(base) / "onslaught-ce"


def real_folders(env=os.environ) -> list[Path]:
    """Where the player's careers and settings are: CE's own user folder, and the folder BEA_USER_DIR names when it is set."""
    folders = [ce_user_folder(env)]
    if env.get("BEA_USER_DIR"):
        folders.append(Path(env["BEA_USER_DIR"]))
    return folders


def fresh_user_folder(env=os.environ) -> Path:
    """The default place for the mod and a career of its own: beside CE's own user folder, never inside it."""
    return ce_user_folder(env).with_name(FRESH_FOLDER)


def _stat(path: Path):
    try:
        return os.stat(path)
    except OSError:
        return None


def _chain(path: Path) -> list:
    """The folder (links followed) and each of its parents, with the stat of each that exists: identity is by device and inode as well as by name."""
    resolved = path.resolve()
    return [(p, _stat(p)) for p in (resolved, *resolved.parents)]


def _same(a: tuple, b: tuple) -> bool:
    return a[0] == b[0] or (a[1] is not None and b[1] is not None and os.path.samestat(a[1], b[1]))


def real_conflict(path: Path, env=os.environ) -> str | None:
    """How `path` relates to the player's own CE folders: "is" one, "is inside" one (a link or a bind mount counts), or "holds" one (it is a parent of it); None when it
    does not."""
    mine = _chain(path)
    for real in real_folders(env):
        theirs = _chain(real)
        if _same(mine[0], theirs[0]):
            return "is"
        if any(_same(parent, theirs[0]) for parent in mine[1:]):
            return "is inside"
        if any(_same(mine[0], parent) for parent in theirs[1:]):
            return "holds"
    return None


def is_real_folder(path: Path, env=os.environ) -> bool:
    return real_conflict(path, env) is not None


def check_mod_folder(moddir: Path, *, expect_name: str | None = None) -> dict:
    """mod.json and every file it lists, as the loader will check them: the folder is the id (or `expect_name`, for a copy not yet in its place), each file is there with
    its size and SHA-256, and nothing else is staged."""
    folder_name = moddir.name if expect_name is None else expect_name
    if moddir.is_symlink() or not moddir.is_dir():
        raise ImportFailure(f"{moddir} is not a folder of a mod")
    try:
        manifest = json.loads((moddir / "mod.json").read_bytes())
    except (OSError, ValueError) as error:
        raise ImportFailure(f"{moddir}/mod.json cannot be read: {error}") from None
    mod_id = manifest.get("id") if isinstance(manifest, dict) else None
    if not isinstance(mod_id, str) or not mod_id or not set(mod_id) <= ID_CHARS or mod_id != folder_name:
        raise ImportFailure(f"mod.json's id {mod_id!r} is not the folder's name {folder_name!r}")
    files = manifest.get("files")
    if not isinstance(files, list) or not files:
        raise ImportFailure("mod.json lists no files")
    listed = set()
    for entry in files:
        rel = entry.get("path") if isinstance(entry, dict) else None
        if not isinstance(rel, str) or rel.startswith("/") or ".." in rel.split("/") or "\\" in rel:
            raise ImportFailure(f"mod.json lists a path that is not inside the mod: {rel!r}")
        path = moddir / rel
        if path.is_symlink() or not path.is_file():
            raise ImportFailure(f"{rel} is missing from the mod folder or is not a plain file")
        data = path.read_bytes()
        if len(data) != entry.get("size") or hashlib.sha256(data).hexdigest() != entry.get("sha256"):
            raise ImportFailure(f"{rel} is not the file mod.json describes (size or SHA-256)")
        listed.add(rel)
    present = {p.relative_to(moddir).as_posix() for p in moddir.rglob("*") if p.is_file()} - {"mod.json"}
    if present != listed:
        raise ImportFailure(f"the mod folder holds files mod.json does not list: {sorted(present - listed)[:3]}")
    return manifest


MODS_VALUE_LIMIT = 2047                   # CE reads the mods= value into 2,048 bytes, the end mark included


def with_mod(ini: bytes, mod_id: str) -> tuple[bytes, list[str]]:
    """ce.ini's bytes with mod_id at the end of the mods= line, and the mods that line named before. CE reads a setting as CE_SettingGetText does: lines end at LF (a CR
    before it belongs to the ending), the key starts the line in exactly that case and the equals sign follows it at once (so MODS=, an indented mods= and mods = are not
    the setting), blanks around the value are dropped, two such lines make the setting unset, and so does a value with a control byte or of 2,048 bytes or more. So one line is
    edited and keeps its own ending, two are refused, an unreadable one is refused, and when there is none a line is added at the end in the file's line ending."""
    text = ini.decode("utf-8", "surrogateescape")
    lines = text.split("\n")
    at = [i for i, line in enumerate(lines) if line.startswith("mods=")]
    if len(at) > 1:
        raise ImportFailure("ce.ini has two mods= lines, which CE treats as none: keep one of them and run this again")
    if not at:
        newline = "\r\n" if "\r\n" in text else "\n"
        head = text if not text or text.endswith("\n") else text + newline
        return (head + f"mods={mod_id}" + newline).encode("utf-8", "surrogateescape"), []
    line = lines[at[0]]
    ending = "\r" if line.endswith("\r") else ""
    value = line[len("mods="):len(line) - len(ending)]
    if any(ord(c) < 0x20 or ord(c) == 0x7F for c in value.strip(" \t")):
        raise ImportFailure("the mods= line of ce.ini holds a control character, which CE treats as no mods at all: remove the character and run this again")
    before = [m.strip(" \t") for m in value.split(",") if m.strip(" \t")]
    new_value = ",".join([m for m in before if m != mod_id] + [mod_id])
    if len(new_value.encode("utf-8", "surrogateescape")) > MODS_VALUE_LIMIT:
        raise ImportFailure(f"the mods= line would be longer than the {MODS_VALUE_LIMIT} bytes CE reads: remove a mod from it and run this again")
    lines[at[0]] = "mods=" + new_value + ending
    return "\n".join(lines).encode("utf-8", "surrogateescape"), before


def stage(moddir: Path, user_dir: Path, *, into_real: bool = False, replace: bool = False, dry_run: bool = False, clock=time.gmtime,
          env=os.environ) -> dict:
    """Put the mod into <user_dir>/mods/<id>/ and name it on <user_dir>/ce.ini's mods= line. A folder that is not there is made (a fresh CE user folder); the
    player's own CE folder is refused unless `into_real`. An existing ce.ini is kept first. Nothing outside user_dir is touched."""
    manifest = check_mod_folder(moddir)
    mod_id = manifest["id"]
    relation = real_conflict(user_dir, env)
    real = relation == "is"
    if relation is not None and not (real and into_real):
        raise ImportFailure(f"{user_dir} {relation} your own CE folder (your careers and settings): stage into a fresh folder (the default is "
                            f"{fresh_user_folder(env)})" + (" or give --into-my-real-folder" if real else ""))
    if user_dir.is_symlink() or (user_dir.exists() and not user_dir.is_dir()):
        raise ImportFailure(f"{user_dir} is not a plain folder")
    if real and not user_dir.is_dir():
        raise ImportFailure(f"{user_dir} is not there: start CE once so that it makes its own folder")
    stamp = time.strftime("%Y%m%dT%H%M%SZ", clock())
    target, ini = user_dir / "mods" / mod_id, user_dir / "ce.ini"
    if ini.is_symlink() or (ini.exists() and not ini.is_file()):
        raise ImportFailure(f"{ini} is not a plain file")
    old = ini.read_bytes() if ini.exists() else b""
    if len(old) > MAX_INI:
        raise ImportFailure(f"{ini} is larger than {MAX_INI} bytes")
    mods = user_dir / "mods"
    if mods.is_symlink() or (mods.exists() and not mods.is_dir()):
        raise ImportFailure(f"{mods} is not a plain folder")
    if target.is_symlink():
        raise ImportFailure(f"{target} is a link: remove it yourself first")
    if target.exists() and not replace:
        raise ImportFailure(f"{target} exists already; give --replace to move it aside")
    new, before = with_mod(old, mod_id)
    plan = {"mod": mod_id, "userDir": str(user_dir), "target": str(target), "ini": str(ini), "created": not user_dir.exists(), "intoRealFolder": real,
            "iniBackup": str(user_dir / f"ce.ini.bak-{stamp}") if ini.exists() else None,
            "movedAside": str(user_dir / "mods" / f"{mod_id}.old-{stamp}") if target.exists() else None, "modsBefore": before,
            "standInAlsoNamed": STAND_IN_ID in before and STAND_IN_ID != mod_id, "dryRun": dry_run,
            "launch": ("" if real else f"BEA_USER_DIR={shlex.quote(str(user_dir))} ") + "onslaught-ce -level 888"}
    if dry_run:
        return plan
    user_dir.mkdir(parents=True, exist_ok=True)
    mods.mkdir(exist_ok=True)
    staging = mods / f".stage-{mod_id}-{stamp}"
    temporary = user_dir / f".ce.ini.new-{stamp}"
    made: list[Path] = []                       # files this call made, taken away again if a later step fails
    moved = placed = False
    try:
        shutil.copytree(moddir, staging)
        check_mod_folder(staging, expect_name=mod_id)            # what was copied is what mod.json describes, before it is put in its place
        with open(temporary, "xb") as handle:
            made.append(temporary)
            handle.write(new)
        if plan["iniBackup"]:
            with open(plan["iniBackup"], "xb") as handle:
                made.append(Path(plan["iniBackup"]))
                handle.write(old)
        if plan["movedAside"]:
            target.rename(plan["movedAside"])
            moved = True
        staging.rename(target)
        placed = True
        os.replace(temporary, ini)
    except BaseException as error:                               # a refusal, a full disk, Ctrl-C: leave what was there before
        if placed:
            shutil.rmtree(target, ignore_errors=True)
        if moved and not target.exists():
            os.replace(plan["movedAside"], target)
        shutil.rmtree(staging, ignore_errors=True)
        for path in made:
            path.unlink(missing_ok=True)
        if isinstance(error, OSError):
            raise ImportFailure(f"the mod could not be put in {target} (nothing was changed): {error.strerror or error}") from None
        raise
    return plan


# ---- command line --------------------------------------------------------------------------------------------------------
def option(value: str) -> Path:
    if not value:
        raise argparse.ArgumentTypeError("a non-empty path is required")
    return Path(value)


def cmd_inspect(args) -> int:
    member, record = read_source(args.source, strict_pins=args.strict_pins)
    print(json.dumps({"source": record, "member": inspect(member)}, indent=1))
    return 0


def cmd_build(args) -> int:
    summary, report = build(args.source, args.game, args.out, ce_min=args.ce_min, mod_id=args.id, name=args.name, version=args.version,
                            author=args.author or "", ce_max=args.ce_max, strict_pins=args.strict_pins)
    for warning in report["warnings"]:
        print(f"warning: {warning}", file=sys.stderr)
    print(f"built CE mod {args.id!r} in {summary['root']} from the PS2 copy ({report['member']['from']}), the world of {report['archive']['things']} things as the disc holds it")
    for entry in summary["files"]:
        print(f"  {entry['path']}  {entry['size']} bytes  sha256 {entry['sha256']}")
    print(f"  mod.json  sha256 {summary['manifestSha256']}")
    print(f"to stage it in a fresh CE folder of its own (your careers and settings stay untouched; close the game first): "
          f"python3 {shlex.quote(str(Path(__file__).resolve()))} stage {shlex.quote(str(summary['root']))}")
    return 0


def cmd_stage(args) -> int:
    user_dir = args.user_dir or (ce_user_folder() if args.into_my_real_folder else fresh_user_folder())
    plan = stage(args.moddir, user_dir, into_real=args.into_my_real_folder, replace=args.replace, dry_run=args.dry_run)
    print(("would stage " if args.dry_run else "staged ") + f"{plan['mod']!r} into {plan['target']}" + (" (a folder made for it)" if plan["created"] else ""))
    if plan["iniBackup"]:
        print(f"  ce.ini {'would be kept' if args.dry_run else 'kept'} as {plan['iniBackup']}")
    if plan["movedAside"]:
        print(f"  the earlier folder {'would move' if args.dry_run else 'moved'} to {plan['movedAside']}")
    print(f"  {plan['userDir']}/ce.ini names: {', '.join(plan['modsBefore'] + [plan['mod']] if plan['mod'] not in plan['modsBefore'] else plan['modsBefore'])}")
    if plan["standInAlsoNamed"]:
        print(f"  warning: ce.ini also names {STAND_IN_ID!r}, the generator's stand-in, which adds the same level archive: remove one of them from mods=")
    if plan["intoRealFolder"]:
        print("  warning: this is your own CE folder: the level's end screen writes a career there until a CE build with the bonus-level fence runs it")
    else:
        print("  your own CE folder, its careers and its settings are not touched; this folder has settings of its own (add the lines of yours that you want to its ce.ini, keeping its mods= line)")
    print(f"start the level with:  {plan['launch']}")
    print("mods load on Linux only and are off in replays and network play; close the game before staging")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    inspect_parser = sub.add_parser("inspect")
    build_parser = sub.add_parser("build")
    stage_parser = sub.add_parser("stage")
    for p in (inspect_parser, build_parser):
        p.add_argument("source", type=option, help="the image (an ISO or a Redump zip) or the extracted member")
        p.add_argument("--strict-pins", action="store_true", help="refuse a digest that is not the pinned one")
    build_parser.add_argument("--game", type=option, default=os.environ.get("BEA_GAME"), required="BEA_GAME" not in os.environ, help="the game folder (or BEA_GAME)")
    build_parser.add_argument("--out", type=option, required=True, help="the folder that receives the mod folder")
    build_parser.add_argument("--ce-min", required=True, help="the oldest CE version that can load an added level archive, such as 0.1.13")
    build_parser.add_argument("--ce-max", default=None)
    build_parser.add_argument("--id", default=MOD_ID)
    build_parser.add_argument("--name", default=MOD_NAME)
    build_parser.add_argument("--version", default="1")
    build_parser.add_argument("--author", default="")
    stage_parser.add_argument("moddir", type=option, help="the mod folder that build wrote")
    stage_parser.add_argument("--user-dir", type=option, default=None,
                              help=f"the CE user folder to put it in (made when missing; default: {FRESH_FOLDER} beside CE's own; CE's own folder and any folder that holds it or lies "
                                   f"inside it are refused)")
    stage_parser.add_argument("--into-my-real-folder", action="store_true", help="allow CE's own user folder (careers and settings are there; the level's end screen writes a career)")
    stage_parser.add_argument("--replace", action="store_true", help="move an existing folder of this mod aside instead of refusing")
    stage_parser.add_argument("--dry-run", action="store_true", help="say what would happen and change nothing")
    args = parser.parse_args(argv)
    return {"inspect": cmd_inspect, "build": cmd_build, "stage": cmd_stage}[args.command](args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ImportFailure, lvl.BuildError, enc.EncodeError, ps2_disc.Ps2DiscError) as error:
        print(f"level 888 import: {error}", file=sys.stderr)
        sys.exit(2)
