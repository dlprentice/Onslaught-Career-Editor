#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""The independent gate of the level 888 builder that takes the disc's world: tools/level888_ps2_import.py over tools/level888_build.py's build(world_body=...).

The builder makes a CE mod from the player's own PS2 copy (the member `888_res_PS2.aya`) and PC game folder: the disc's world body, byte for byte, in an archive whose terrain
and lists are the PC game's level 857, with the descriptors the units need and one mesh stand-in. This gate does not trust it. It reads the member and the game folder itself,
runs the builder as a library, and checks the OUTPUT FILES against the INPUT FILES with its own reading of them: counts, hashes and booleans only, and no game is run.

    level888_ps2_gate.py gate --game GAME SOURCE --work DIR [--strict-pins] [--ce-min 0.1.13] [--keep]

SOURCE is what the importer takes: the extracted member (a file that starts with the tag LVLR), or the player's image. DIR is a private folder for the staged copy the gate
makes (it is removed at the end unless --keep); the gate refuses a DIR inside the repository except under its ignored private folders (local-data, local-lab), because what it stages comes
from the player's disc. What it checks:

    the source        the member is the pinned one; its world is level 888 alone with no base world; its body reads back unchanged; it has one shadow chunk and the decoder reads it
    the builds        the library build twice gives the same bytes, and lives/ai-state have no part in it; the importer's staged mod is the library's files
    the archive       packed as the game's reader needs; the loader's structure walk; the world names level 888 alone; its RLWD is the member's body byte for byte;
                      the header is the worldheaders.dat record and the world type is 2; every script a thing names is one of the world's; the start points of players 1 and 2
    the closure       every definition placed is in the physics file; every mesh the units need has a descriptor, a loose file, and its textures have descriptors; the descriptors
                      gained are exactly the ones reported, with runtime ids after the donor's highest and none twice; the donor's chunks (terrain and lists) are kept in order,
                      its baked shadows replaced by the member's one shadow chunk, byte for byte
    the physics file  differs from the original in exactly one unit definition, in exactly its mesh name: the stand-in (the PC game has no file for the PS2 Fenrir's mesh)
    the report        its sizes, hashes, counts and world label are the files' own; its stand-ins are the replacements the physics file shows; its shadows are the member's chunk
    the mod folder    mod.json lists exactly the two files with their sizes and SHA-256, each re-hashed here; the folder is the id; nothing else is in it; the description says
                      what came from the PS2 copy and what from the game
    the folders       the game folder's files were not changed; no pinned file differs from what the recipe was checked against

Three checks (the world type, the scripts its things name, its start points) describe the disc's world, which the builder carries over byte for byte: when one of them does not
hold it is printed as a `note`, a finding about the input, and the exit code is unchanged. Exit 0 when no check of the builder failed, 1 when one did, 2 for a refusal. The gate is part of the builder's tests (tools/level888_ps2_gate_tests.py), where each kind of fault is shown to be found."""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import shutil
import struct
import sys
import tempfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))

import level888_build as lvl  # noqa: E402
import level888_ps2_import as imp  # noqa: E402
import world_mod_stage as stage  # noqa: E402
import world_resources_decode as wrd  # noqa: E402
import world_resources_encode as enc  # noqa: E402
import worldheaders_decode as headers  # noqa: E402
from aya_cross_platform_compare import logical_key, normalize_asset_name  # noqa: E402

BuildError = lvl.BuildError
LEVEL = lvl.LEVEL
PRIVATE_ROOTS = ("local-data", "local-lab")        # the places in the repository where what the disc yields may be staged

# Checks that describe the DISC'S WORLD, which the builder carries over byte for byte, and not the builder: when one fails it is a finding about the input (reported, with the
# verdict on the builder unchanged), not a fault of the builder.
FINDINGS = frozenset({
    "it is a versus world (world type 2)",
    "every script a thing names is one of the world's scripts",
    "the start points are those of players 1 and 2",
})


class GateRefusal(ValueError):
    """The gate cannot be run as asked; the message says why."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def private_folder(path: Path) -> None:
    """Refuse a folder inside the repository that is not one of its ignored private folders."""
    repo = TOOLS.parent.resolve()
    try:
        relative = Path(os.path.abspath(path)).resolve().relative_to(repo)
    except ValueError:
        return
    if not relative.parts or relative.parts[0] not in PRIVATE_ROOTS:
        raise GateRefusal(f"{path}: inside the repository, outside {' and '.join(PRIVATE_ROOTS)}; what the gate stages comes from the player's disc and stays private")


def chunk_list(unpacked: bytes) -> list[tuple[str, bytes]]:
    return [(tag, unpacked[at:at + size]) for tag, at, size in enc.chunks(unpacked)]


def member_shadows(member: bytes) -> bytes | None:
    """The member's one shadow chunk (SSHD), read here; None when it has none or several."""
    found = [member[at:at + size] for tag, at, size in enc.chunks(member) if tag == "SSHD"]
    return found[0] if len(found) == 1 else None


def shadow_counts(shadows: bytes) -> dict | None:
    """What the decoder reads in a shadow chunk (shadows, part maps, shadowed maps, cells), None when it cannot read it."""
    try:
        return wrd.parse_sshd(shadows)
    except wrd.DecodeError:
        return None


def mod_folder_problems(moddir: Path, expected: dict[str, bytes], mod_id: str) -> list[str]:
    """What is wrong with a staged mod folder, read here and not by the importer: mod.json's id is the folder's name, it lists exactly the expected files, each with the size and
    SHA-256 of the bytes in the folder, and the folder holds those files and mod.json and nothing else."""
    problems: list[str] = []
    if moddir.is_symlink() or not moddir.is_dir():
        return ["the mod folder is not a plain folder"]
    try:
        manifest = json.loads((moddir / "mod.json").read_bytes())
    except (OSError, ValueError):
        return ["mod.json cannot be read"]
    if not isinstance(manifest, dict) or manifest.get("id") != mod_id or moddir.name != mod_id:
        problems.append("mod.json's id is not the folder's name and the mod id")
    listed = {entry.get("path"): entry for entry in (manifest.get("files") or []) if isinstance(entry, dict)}
    if sorted(listed) != sorted(expected):
        problems.append(f"mod.json lists {len(listed)} files, not the {len(expected)} built")
    for rel, data in expected.items():
        path = moddir / rel
        if path.is_symlink() or not path.is_file():
            problems.append("a built file is missing from the folder or is not a plain file")
            continue
        on_disk = path.read_bytes()
        entry = listed.get(rel, {})
        if on_disk != data:
            problems.append("a file in the folder is not the built bytes")
        if entry.get("size") != len(on_disk) or entry.get("sha256") != sha256(on_disk):
            problems.append("mod.json's size or SHA-256 is not the file's")
    present = {p.relative_to(moddir).as_posix() for p in moddir.rglob("*") if p.is_file() or p.is_symlink()} - {"mod.json"}
    if present != set(expected):
        problems.append(f"the folder holds {len(present - set(expected))} files that are not built")
    return problems


def gate_checks(game: Path, install: lvl.Install, member: bytes, body: bytes, shadows: bytes, first: lvl.Build, moddir: Path | None, mod_id: str, check) -> None:
    """The checks that read the finished build (first) and the staged folder against the member (its world body and its shadow chunk) and the game folder; check(name, passed,
    detail) records one."""
    report = first.report
    archive, physics_bytes = first.files[lvl.ARCHIVE_PATH], first.files[lvl.PHYSICS_PATH]

    # the archive, from its bytes alone
    problem, unpacked = stage.check_packed(archive, unpack=True)
    walk = None if problem else stage.check_level_archive(unpacked, LEVEL)
    check("the archive is packed like the game's reader needs", problem is None, problem or "")
    check("it passes the loader's structure walk", problem is None and walk is None, (problem or walk) or "")
    chunks = chunk_list(unpacked) if unpacked else []
    worlds = enc.level_worlds(unpacked) if unpacked else {"bodies": {}, "baseLevel": None, "realLevel": None}
    out_body = worlds["bodies"].get("RLWD", b"")
    check("the world names level 888 alone (no base world)", (worlds["baseLevel"], worlds["realLevel"], sorted(worlds["bodies"])) == (-1, LEVEL, ["RLWD"]))
    check("the archive's RLWD is the member's world body, byte for byte", out_body == body, f"{len(out_body)} of {len(body)} bytes")
    model = enc.read_world_model(out_body) if out_body else {"things": [], "scripts": [], "header": {}, "waypointPaths": []}
    check("the world body reads back unchanged", bool(out_body) and enc.write_world_body(model) == out_body)
    parsed = headers.parse_worldheaders(install.read(lvl.WORLDHEADERS_PATH, lvl.LIMIT_SMALL))
    record = parsed.by_world(LEVEL)
    check("the world header is the worldheaders.dat record for 888", record is not None and all(model["header"].get(k) == v for k, v in lvl.header_from_record(record).items()))
    check("it is a versus world (world type 2)", model["header"].get("worldType") == 2)
    names = {s["name"] for s in model["scripts"]}
    used = {thing["init"].get(field) for thing in model["things"] for field in ("script", "spawnScript") if thing["init"].get(field)}
    dangling = collections.Counter(thing["kind"] for thing in model["things"] for field in ("script", "spawnScript")
                                   if thing["init"].get(field) and thing["init"][field] not in names)
    check("every script a thing names is one of the world's scripts", used <= names,
          f"{len(used - names)} missing of {len(used)} named; things that name one, by kind: {dict(sorted(dangling.items()))}")
    starts = sorted(t["init"]["start"]["playerNumber"] for t in model["things"] if t["kind"] == "start")
    check("the start points are those of players 1 and 2", starts == [1, 2], f"{len(starts)} start points")

    # the closure, from the output files and the game folder
    physics = lvl.Physics(physics_bytes)
    definitions = {t["definition"] for t in model["things"] if "definition" in t}
    defined = {s.name for s in physics.statements}
    check("every definition the world places is in the physics file", definitions <= defined, f"{len(definitions - defined)} missing of {len(definitions)}")
    out_index = lvl.descriptors(chunks)
    units, meshes = [], []
    for definition in dict.fromkeys(t["definition"] for t in model["things"] if t["kind"] == "unit"):
        found_units, found_meshes = physics.closure(definition)
        units += [u for u in found_units if u not in units]
        meshes += [m for m in found_meshes if m.lower() not in (known.lower() for known in meshes)]
    missing_meshes, missing_textures, no_file = [], [], []
    for mesh in meshes:
        if ("MESH", normalize_asset_name(mesh)) not in out_index:
            missing_meshes.append(mesh)
        if not install.has(lvl.loose_mesh_path(mesh)):
            no_file.append(mesh)
            continue
        for texture in lvl.mesh_textures(install, mesh):
            if ("TEXT", normalize_asset_name(texture)) not in out_index:
                missing_textures.append(texture)
    check("every mesh the units need has a descriptor", not missing_meshes, f"{len(missing_meshes)} missing of {len(meshes)} meshes of {len(units)} units")
    check("every texture those meshes ask for has a descriptor", not missing_textures, f"{len(missing_textures)} missing")
    check("every mesh the units need has its loose file", not no_file, f"{len(no_file)} without")
    donor = lvl.unpack(install, lvl.DONOR)

    def names_of(tag: str, listed: list[tuple[str, bytes]]) -> collections.Counter:
        return collections.Counter(logical_key(tag, payload)[0] for t, payload in listed if t == tag)

    added_counts = {}
    for tag in ("TEXT", "MESH"):
        gained = names_of(tag, chunks) - names_of(tag, donor)
        lost = names_of(tag, donor) - names_of(tag, chunks)
        wanted = collections.Counter(normalize_asset_name(entry["name"]) for entry in report["added"][tag.lower()])
        added_counts[tag] = sum(gained.values())
        check(f"the {tag} descriptors gained are exactly the ones reported, and none of the donor's is lost", gained == wanted and not lost, f"{sum(wanted.values())} added")
    donor_ids = [lvl.mesh_id(p) for t, p in donor if t == "MESH"]
    out_ids = [lvl.mesh_id(p) for t, p in chunks if t == "MESH"]
    new_ids = sorted(set(out_ids) - set(donor_ids))
    check("no MESH runtime id twice; the new ones follow the donor's highest", len(set(out_ids)) == len(out_ids) and new_ids == list(range(max(donor_ids) + 1, max(donor_ids) + 1 + added_counts["MESH"])),
          f"{len(out_ids)} meshes, {len(new_ids)} new ids")
    donor_names = {"TEXT": set(names_of("TEXT", donor)), "MESH": set(names_of("MESH", donor))}
    kept_out = [(t, p) for t, p in chunks if t != "WRES" and not (t in donor_names and logical_key(t, p)[0] not in donor_names[t])]
    check("the donor's chunks (terrain, lists, descriptors) are kept byte for byte and in order, its baked shadows replaced by the member's shadow chunk",
          kept_out == [(t, shadows if t == "SSHD" else p) for t, p in donor if t != "WRES"], f"{len(kept_out)} chunks")
    out_shadows = [p for t, p in chunks if t == "SSHD"]
    check("the archive's one shadow chunk is the member's, byte for byte", out_shadows == [shadows], f"{len(out_shadows)} chunks, {len(shadows)} bytes wanted")

    # the physics file is the original with the stand-in's mesh name and nothing else, re-derived here from the original's own offsets
    original_bytes = install.read(lvl.PHYSICS_PATH, lvl.LIMIT_SMALL)
    original = lvl.Physics(original_bytes)
    differing = [s.name for s, o in zip(physics.statements, original.statements)
                 if (s.kind, s.name, [(n.field, n.value) for n in s.nodes]) != (o.kind, o.name, [(n.field, n.value) for n in o.nodes])]
    check("the physics file differs from the original in exactly one unit definition",
          len(physics.statements) == len(original.statements) and differing == [lvl.FENRIR], f"{len(differing)} differing of {len(physics.statements)}")
    expected_physics = None
    fenrir = [s for s in original.statements if s.kind == lvl.UNIT_KIND and s.name == lvl.FENRIR]
    mesh_nodes = [n for n in fenrir[0].nodes if n.field == lvl.MESH_FIELD[lvl.UNIT_KIND]] if fenrir else []
    if len(mesh_nodes) == 1:
        statement, node = fenrir[0], mesh_nodes[0]
        value = lvl.FENRIR_MESH.encode("ascii") + b"\0"
        delta = len(value) - len(node.value)
        expected_physics = (original_bytes[:statement.at + 4] + struct.pack("<I", statement.size + delta) + original_bytes[statement.at + 8:node.at + 4]
                            + struct.pack("<I", len(value)) + value + original_bytes[node.at + 8 + len(node.value):])
    check("it is the original with the Fenrir's mesh name replaced and not one other byte changed", expected_physics is not None and physics_bytes == expected_physics,
          f"{len(physics_bytes) - len(original_bytes)} bytes longer")
    check("the stand-in is a mesh the game has a file for, in place of one it has no file for",
          install.has(lvl.loose_mesh_path(lvl.FENRIR_MESH)) and not install.has(lvl.loose_mesh_path(lvl.FENRIR_FILELESS_MESH)))
    check("the report names the stand-in", report["physics"].get("unit") == lvl.FENRIR and report["physics"].get("mesh") == f"{lvl.FENRIR_FILELESS_MESH} -> {lvl.FENRIR_MESH}")

    def unit_mesh(source: lvl.Physics, name: str) -> str | None:
        found = [n.value.rstrip(b"\0").decode("latin-1") for s in source.statements if s.kind == lvl.UNIT_KIND and s.name == name
                 for n in s.nodes if n.field == lvl.MESH_FIELD[lvl.UNIT_KIND]]
        return found[0] if len(found) == 1 else None
    replaced = [(unit_mesh(original, name), unit_mesh(physics, name)) for name in differing]
    stand_ins = report.get("standIns")
    reported = [(str(e.get("named by the world's units")), str(e.get("used instead"))) for e in stand_ins if isinstance(e, dict)] if isinstance(stand_ins, list) else None
    check("the report's stand-ins are the replacements the physics file shows: the mesh it named, the one it names now, and the file through which",
          reported is not None and len(reported) == len(stand_ins) and reported == replaced
          and all(e.get("kind") == "mesh" and e.get("through") == lvl.PHYSICS_PATH for e in stand_ins) and all(install.has(lvl.loose_mesh_path(new)) for _, new in replaced),
          f"{len(replaced)} replacements, {len(reported or [])} reported")

    # the report says what the files are
    check("the report's archive and physics figures are the files' own",
          report["archive"]["size"] == len(archive) and report["archive"]["sha256"] == sha256(archive) and report["archive"]["unpackedSize"] == len(unpacked or b"")
          and report["physics"]["size"] == len(physics_bytes) and report["physics"]["sha256"] == sha256(physics_bytes) and report["physics"]["was"] == len(original_bytes))
    check("the report counts the world's things and scripts, and its body", report["archive"]["things"] == len(model["things"]) and report["archive"]["worldBodyBytes"] == len(out_body)
          and [(s["instructions"], s["handlers"]) for s in report["scripts"]] == [(len(r["code"]["instructions"]), len(r["code"]["eventFunctions"])) for r in model["scripts"]])
    check("the report says the world is the PS2 copy's and that lives and the AI state had no part", report.get("world") == "ps2-copy" and report.get("lives") is None and report.get("aiState") is None)
    counts = shadow_counts(shadows)
    donor_shadow_sizes = [len(p) for t, p in donor if t == "SSHD"]
    check("the report says the shadows are the PS2 copy's, with the sizes of both chunks and the counts the decoder reads in the member's",
          counts is not None and len(donor_shadow_sizes) == 1
          and report.get("shadows") == {"from": "ps2-copy", "bytes": len(shadows), "donorBytes": donor_shadow_sizes[0], **counts}, f"{len(shadows)} bytes from the member, {donor_shadow_sizes} in the donor")

    # the stager and the staged folder
    try:
        manifest = stage.build_files_manifest(mod_id, "gate", "1", first.files, game_has=install.has, ce_min="0.1.13", description=lvl.description("0.1.13", None))
        check("the mod stager (the loader's rules) accepts the files", True, f"mod.json {sha256(manifest)[:16]}...")
    except stage.ModStageError as error:
        check("the mod stager (the loader's rules) accepts the files", False, str(error))
    if moddir is not None:
        problems = mod_folder_problems(moddir, first.files, mod_id)
        check("the staged mod folder is what mod.json says, file by file, and holds nothing else", not problems,
              "; ".join(problems) or f"mod.json sha256 {sha256((moddir / 'mod.json').read_bytes())[:16]}")
        try:
            imp.check_mod_folder(moddir)
            importer_agrees = True
        except imp.ImportFailure:
            importer_agrees = False
        check("the importer's own folder check agrees", importer_agrees)
        try:
            description = json.loads((moddir / "mod.json").read_bytes()).get("description", "")
        except (OSError, ValueError, AttributeError):
            description = ""
        no_shadows = counts is not None and not any(counts.values())
        check("the mod's description says what came from the PS2 copy and what from this game, and calls the shadow chunk empty only if it is",
              isinstance(description, str) and "FROM YOUR PS2 COPY" in description and "FROM THIS GAME" in description and ("empty static-shadow chunk" in description) == no_shadows,
              f"{len(description) if isinstance(description, str) else 0} characters")

    # the folders were only read
    changed = [rel for rel, info in install.reads.items() if sha256(lvl.Install(game).read(rel, lvl.LIMIT_ARCHIVE)) != info["sha256"]]
    check("the game folder's files were not changed during the run", not changed, f"{len(changed)} changed")
    check("every pinned file is the one the recipe was checked against", not install.warnings, f"{len(install.warnings)} warnings")


def run_gate(game: Path, source: Path, work: Path, *, strict_pins: bool = False, ce_min: str = "0.1.13", keep: bool = False) -> list[tuple[str, bool, str]]:
    """Checks on the builder's output against the member and the player's game folder. Each result is (name, passed, detail)."""
    results: list[tuple[str, bool, str]] = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        results.append((name, bool(ok), detail))

    private_folder(work)
    try:
        member, record = imp.read_source(source, strict_pins=strict_pins)
    except imp.ImportFailure as error:
        check("the source", False, str(error))
        return results
    pin = imp.ps2_disc.MEMBER_SHA256.get(imp.ps2_disc.fold_member_path(imp.ps2_disc.LEVEL_888_MEMBER))
    check("the member is the pinned one (SHA-256)", sha256(member) == pin, f"{len(member)} bytes")
    check("reading the source raised no pin warning", not record["warnings"], f"{len(record['warnings'])} warnings")
    try:
        worlds = enc.level_worlds(member)
        body = worlds["bodies"]["RLWD"]
    except (enc.EncodeError, ValueError, KeyError, IndexError) as error:
        check("the member has a readable world", False, f"{type(error).__name__}")
        return results
    check("the member's world is level 888 alone, one RLWD, no base world", (worlds["baseLevel"], worlds["realLevel"], sorted(worlds["bodies"])) == (-1, LEVEL, ["RLWD"]))
    try:
        check("the member's world body reads back unchanged", enc.write_world_body(enc.read_world_model(body)) == body, f"{len(body)} bytes")
    except (enc.EncodeError, ValueError, KeyError, struct.error) as error:
        check("the member's world body reads back unchanged", False, type(error).__name__)
        return results

    shadows = member_shadows(member)
    check("the member has one shadow chunk, and the decoder reads it", shadows is not None and shadow_counts(shadows) is not None,
          "none or several" if shadows is None else f"{len(shadows)} bytes, {shadow_counts(shadows)}")
    if shadows is None or shadow_counts(shadows) is None:
        return results

    install = lvl.Install(game, strict_pins=strict_pins)
    try:
        first = lvl.build(install, world_body=body, shadows=shadows)
        second = lvl.build(lvl.Install(game, strict_pins=strict_pins), world_body=body, shadows=shadows)
        third = lvl.build(lvl.Install(game, strict_pins=strict_pins), lives=7, ai_state=3, world_body=body, shadows=shadows)
    except BuildError as error:
        check("build", False, str(error))
        return results
    check("build", True, f"{first.report['archive']['size']} byte archive (sha256 {first.report['archive']['sha256'][:16]}), "
                         f"{first.report['physics']['size']} byte physics file (sha256 {first.report['physics']['sha256'][:16]})")
    check("deterministic: two builds from the same inputs give the same bytes", first.files == second.files and first.report == second.report)
    check("lives and the AI state have no part in the disc's world", first.files == third.files)

    work.mkdir(parents=True, exist_ok=True)
    staged = Path(tempfile.mkdtemp(prefix="gate-", dir=work))
    try:
        try:
            summary, imported = imp.build(source, game, staged, ce_min=ce_min, strict_pins=strict_pins)
        except imp.ImportFailure as error:
            check("the importer's build", False, str(error))
            gate_checks(game, install, member, body, shadows, first, None, imp.MOD_ID, check)
            return results
        moddir = Path(summary["root"])
        check("the importer's build succeeded and staged one folder", moddir.parent == staged and moddir.name == imp.MOD_ID, f"{len(summary['files'])} files")
        check("the importer's staged files are the library build's", all((moddir / rel).read_bytes() == data for rel, data in first.files.items()))
        check("the importer's report is the library's, plus the member", {k: v for k, v in imported.items() if k not in ("member", "warnings")}
              == {k: v for k, v in first.report.items() if k != "warnings"})
        try:
            gate_checks(game, install, member, body, shadows, first, moddir, imp.MOD_ID, check)
        except (BuildError, enc.EncodeError, ValueError, KeyError, TypeError, struct.error) as error:
            check("the checks ran to the end", False, f"{type(error).__name__}: {error}")
    finally:
        if not keep:
            shutil.rmtree(staged, ignore_errors=True)
    return results


def verdict(results: list[tuple[str, bool, str]]) -> tuple[list[str], list[str]]:
    """(the checks of the builder that failed, the findings about the disc's world that did not hold)."""
    faults = [name for name, ok, _ in results if not ok and name not in FINDINGS]
    findings = [name for name, ok, _ in results if not ok and name in FINDINGS]
    return faults, findings


# ---- command line ---------------------------------------------------------------------------------------------------------
def option(value: str) -> Path:
    if not value:
        raise argparse.ArgumentTypeError("a non-empty path is required")
    return Path(value)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("gate")
    p.add_argument("source", type=option, help="the image or the extracted member")
    p.add_argument("--game", type=option, default=os.environ.get("BEA_GAME"), required="BEA_GAME" not in os.environ, help="the game folder (or BEA_GAME)")
    p.add_argument("--work", type=option, required=True, help="a private folder for the staged copy")
    p.add_argument("--strict-pins", action="store_true", help="refuse a file whose SHA-256 is not the one the recipe was checked against")
    p.add_argument("--ce-min", default="0.1.13")
    p.add_argument("--keep", action="store_true", help="keep the staged copy in --work")
    args = parser.parse_args(argv)
    results = run_gate(args.game, args.source, args.work, strict_pins=args.strict_pins, ce_min=args.ce_min, keep=args.keep)
    for name, ok, detail in results:
        print(f"{'ok  ' if ok else ('note' if name in FINDINGS else 'FAIL')} {name}" + (f" - {detail}" if detail else ""))
    faults, findings = verdict(results)
    print(f"{len(results) - len(faults) - len(findings)} of {len(results)} checks passed" + (f"; {len(findings)} findings about the disc's world (not the builder's)" if findings else ""))
    return 1 if faults else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (GateRefusal, BuildError, enc.EncodeError) as error:
        print(f"level 888 gate: {error}", file=sys.stderr)
        sys.exit(2)
