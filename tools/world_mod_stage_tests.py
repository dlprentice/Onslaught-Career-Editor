#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Checks `world_resources_encode.py stage --as-mod` (tools/world_mod_stage.py) on authored data only (no game bytes).

The staged folder must be exactly what the CE mod loader admits. LoaderRules below is an independent restatement of the
loader's start-up checks (onslaught-ce port/platform/common/mods.cpp: ValidId, ReadManifest, CheckPath, WorldFile, LoadMod),
used as the oracle; it has controls of its own so it cannot pass everything. The real loader is the final arbiter: the
staged folder is also loaded by CE in the acceptance run recorded in the work's report, and by the loader's host driver."""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import stat
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import content_catalog_tests as fixtures
import safe_generated_output as safe
import world_mod_stage as stage
import world_resources_encode as enc

TOOLS = Path(__file__).resolve().parent


# ---- the loader's start-up rules, restated -----------------------------------------------------------------------------
class LoaderRules:
    KNOWN = {"schema", "id", "name", "version", "author", "description", "ce_min", "ce_max", "files"}
    DEVICES = {"CON", "PRN", "AUX", "NUL", "CONIN$", "CONOUT$"} | {f"{p}{d}" for p in ("COM", "LPT") for d in "0123456789"}
    WORLD = re.compile(r"data/worlds/world[0-9]{3}\.wrd")

    @classmethod
    def strict_json(cls, text: bytes):
        """mods.cpp's Parser: integers only, bounded depth, no repeated keys, no control characters in strings."""
        def pairs(items):
            keys = [k for k, _ in items]
            if len(set(keys)) != len(keys):
                raise ValueError("a repeated key")
            return dict(items)

        def no_float(text_):
            raise ValueError("a number that is not an integer")
        value = json.loads(text.decode("ascii"), object_pairs_hook=pairs, parse_float=no_float,
                           parse_constant=no_float)

        def walk(node, level):
            if level > 8:
                raise ValueError("nesting deeper than 8")
            if isinstance(node, dict):
                for child in node.values():
                    walk(child, level + 1)
            elif isinstance(node, list):
                for child in node:
                    walk(child, level + 1)
        walk(value, 1)
        return value

    @classmethod
    def version_ok(cls, text) -> bool:
        return isinstance(text, str) and re.fullmatch(r"[0-9]{1,5}(\.[0-9]{1,5}){0,3}", text) is not None

    @classmethod
    def path_problem(cls, path: str):
        if not path or len(path) > 240:
            return "an empty or over-long path"
        parts = path.split("/")
        if len(parts) > 12:
            return "too many path components"
        for part in parts:
            if not part:
                return "an absolute path or an empty path component"
            if part in (".", ".."):
                return "a '.' or '..' component"
            if len(part) > 128:
                return "an over-long path component"
            if any(ord(c) < 32 or ord(c) >= 127 or c in '\\:*?"<>|' for c in part):
                return "a character that is not allowed in a path"
            if part[0] == " " or part[-1] in " .":
                return "a component that starts with a space or ends with a space or a dot"
            if part.split(".")[0].rstrip(" ").upper() in cls.DEVICES:
                return "a Windows device name"
        if parts[0].lower() != "data":
            return "a path outside data/"
        return None

    @classmethod
    def problems(cls, mod_dir: Path, game_dir: Path) -> list[str]:
        out: list[str] = []
        manifest_path = mod_dir / "mod.json"
        info = os.lstat(manifest_path)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > 256 << 10:
            return ["mod.json is missing, a link, or not a regular file (or over 256 KiB)"]
        try:
            root = cls.strict_json(manifest_path.read_bytes())
        except (ValueError, UnicodeDecodeError) as error:
            return [f"manifest: {error}"]
        if not isinstance(root, dict) or set(root) - cls.KNOWN:
            return ["the manifest is not an object of known keys"]
        if root.get("schema") != 1 or isinstance(root.get("schema"), bool):
            out.append("schema is not 1")
        if root.get("id") != mod_dir.name or not re.fullmatch(r"[a-z0-9_-]{1,48}", mod_dir.name):
            out.append("id is not the mod folder's name")
        for key, low, high in (("name", 1, 64), ("version", 1, 32), ("author", 0, 64), ("description", 0, 1024)):
            value = root.get(key)
            if value is None and low == 0:
                continue
            if not isinstance(value, str) or not low <= len(value) <= high or any(ord(c) < 32 for c in value):
                out.append(f"{key} is missing, not a string, or not {low} to {high} characters")
        for key in ("ce_min", "ce_max"):
            if key in root and not cls.version_ok(root[key]):
                out.append(f"{key} is not a version")
        files = root.get("files")
        if not isinstance(files, list) or not files or len(files) > 4096:
            return out + ["files is missing, not a list, empty, or over 4096"]
        seen = set()
        for entry in files:
            if not isinstance(entry, dict) or set(entry) - {"path", "size", "sha256"}:
                out.append("a files entry is not an object of path, size and sha256")
                continue
            path, size, sha = entry.get("path"), entry.get("size"), entry.get("sha256")
            if (not isinstance(path, str) or type(size) is not int or size < 0 or not isinstance(sha, str)
                    or re.fullmatch(r"[0-9a-f]{64}", sha) is None or size > 64 << 20):
                out.append("a files entry lacks path, a size within 64 MiB, or a lowercase 64-digit sha256")
                continue
            bad = cls.path_problem(path)
            if bad:
                out.append(f"{path}: {bad}")
                continue
            key = path.lower()
            if key in seen:
                out.append(f"{path}: listed twice")
            seen.add(key)
            world = cls.WORLD.fullmatch(key) is not None
            if not world and not (game_dir / path).is_file():
                out.append(f"{path}: the game has no such file")
            if world and size > 4 << 20:
                out.append(f"{path}: a world file larger than 4 MiB")
            try:
                file_info = os.lstat(mod_dir / path)
            except OSError:
                out.append(f"{path}: a file that cannot be opened")
                continue
            if not stat.S_ISREG(file_info.st_mode) or file_info.st_nlink != 1:
                out.append(f"{path}: a link, a folder or a file with more than one name")
                continue
            if file_info.st_size != size:
                out.append(f"{path}: its size is not the manifest's")
            elif hashlib.sha256((mod_dir / path).read_bytes()).hexdigest() != sha:
                out.append(f"{path}: its SHA-256 is not the manifest's")
        return out


# ---- authored fixtures -------------------------------------------------------------------------------------------------
def archive(real_body: bytes, base_body: bytes | None = None, base_level: int = -1, real_level: int = 200) -> bytes:
    inner = fixtures.chunk(b"WDAT", struct.pack("<ii", base_level, real_level))
    if base_body is not None:
        inner += fixtures.chunk(b"BSWD", base_body)
    inner += fixtures.chunk(b"RLWD", real_body)
    return fixtures.aya(fixtures.chunk(b"WRES", fixtures.chunk(b"WRLD", inner)))


def model_json(model: dict) -> bytes:
    return (json.dumps(model, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode("ascii")


class Base(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.game = self.root / "game"
        self.resources = self.game / "data" / "resources"
        self.resources.mkdir(parents=True)
        self.body = fixtures.world_body()
        self.model = enc.read_world_model(self.body)
        self.edited = json.loads(json.dumps(self.model))
        self.edited["things"][0]["init"]["position"][0] = 12.5
        self.edited_body = enc.write_world_body(self.edited)
        self.write_archive(archive(self.body))
        self.out = self.root / "mods"
        self.model_file = self.root / "edited.json"
        self.model_file.write_bytes(model_json(self.edited))

    def write_archive(self, data: bytes) -> None:
        self.archive_path = self.resources / "200_res_PC.aya"
        self.archive_path.write_bytes(data)
        self.archive_bytes = data

    def cli(self, *args: str):
        return subprocess.run([sys.executable, str(TOOLS / "world_resources_encode.py"), *args], capture_output=True,
                              timeout=60, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})

    def stage_args(self, *extra: str, level: str = "200", mod_id: str = "tank-move", out: Path | None = None):
        return ["stage", "--game", str(self.game), "--level", level, "--as-mod", "--out", str(out or self.out),
                "--id", mod_id, "--name", "Moved tank", *extra]

    def assert_game_unchanged(self) -> None:
        self.assertEqual(self.archive_bytes, self.archive_path.read_bytes())
        self.assertEqual(["200_res_PC.aya"], sorted(p.name for p in self.resources.iterdir()))
        self.assertEqual(["data"], sorted(p.name for p in self.game.iterdir()))

    def assert_nothing_written(self) -> None:
        self.assertFalse(self.out.exists(), "a refused stage must not create the destination")
        self.assert_game_unchanged()


class LoaderRulesControls(Base):
    """The oracle must be able to fail: every control below breaks one rule the loader enforces."""

    def make(self) -> Path:
        result = self.cli(*self.stage_args("--world", str(self.model_file)))
        self.assertEqual(0, result.returncode, result.stderr)
        return self.out / "tank-move"

    def test_a_staged_mod_passes_and_each_control_fails(self) -> None:
        mod = self.make()
        self.assertEqual([], LoaderRules.problems(mod, self.game))
        manifest = json.loads((mod / "mod.json").read_text())

        def broken(label, mutate, expect):
            with self.subTest(label):
                copy = self.root / f"control-{label}" / "tank-move"
                shutil.copytree(mod, copy)
                mutate(copy)
                found = LoaderRules.problems(copy, self.game)
                self.assertTrue(any(expect in line for line in found), (label, found))

        def rewrite(copy, change):
            data = json.loads((copy / "mod.json").read_text())
            change(data)
            (copy / "mod.json").write_text(json.dumps(data))
        broken("hash", lambda c: (c / "data/worlds/world200.wrd").write_bytes(b"x" * manifest["files"][0]["size"]), "SHA-256")
        broken("size", lambda c: (c / "data/worlds/world200.wrd").write_bytes(b"x"), "size")
        broken("schema", lambda c: rewrite(c, lambda d: d.update(schema=2)), "schema")
        broken("unknown key", lambda c: rewrite(c, lambda d: d.update(extra=1)), "known keys")
        broken("id", lambda c: rewrite(c, lambda d: d.update(id="other")), "id")
        broken("name", lambda c: rewrite(c, lambda d: d.update(name="")), "name")
        broken("dots", lambda c: rewrite(c, lambda d: d["files"][0].update(path="data/../x.wrd")), "'..'")
        broken("outside data", lambda c: rewrite(c, lambda d: d["files"][0].update(path="other/world200.wrd")), "outside data")
        broken("game lacks it", lambda c: rewrite(c, lambda d: d["files"][0].update(path="data/worlds/other.wrd")), "no such file")
        broken("hash text", lambda c: rewrite(c, lambda d: d["files"][0].update(sha256=d["files"][0]["sha256"].upper())), "lowercase")
        broken("ce_min", lambda c: rewrite(c, lambda d: d.update(ce_min="1.2.3.4.5")), "not a version")
        broken("hard link", lambda c: os.link(c / "data/worlds/world200.wrd", c / "data/worlds/second.wrd"), "more than one name")
        broken("float size", lambda c: (c / "mod.json").write_text(
            (c / "mod.json").read_text().replace(f'"size": {manifest["files"][0]["size"]}', f'"size": {manifest["files"][0]["size"]}.0')), "integer")
        broken("repeated key", lambda c: (c / "mod.json").write_text(
            (c / "mod.json").read_text().replace('"schema": 1,', '"schema": 1, "schema": 1,')), "repeated key")


# ---- the staged folder ------------------------------------------------------------------------------------------------
class StageAsModTests(Base):
    def world_with_source(self, text: str) -> bytes:
        model = enc.read_world_model(self.edited_body)
        model["scripts"] = [stage.mc.compile_script("main", text, stage.mc.includes_from(self.game), 70)]
        return enc.write_world_body(model)

    def test_a_script_source_is_staged_with_the_world_and_its_game_file_is_unchanged(self) -> None:
        path = "data/MissionScripts/level200/main.msl"
        original = self.game / path
        original.parent.mkdir(parents=True)
        original.write_bytes(b"// shipped source\n")
        text = "// my edit\ninit() { Pause(1); }\n"
        world = self.world_with_source(text)
        order = []
        real = safe.SecuredOutputRoot.atomic_write_new_bytes

        def record(self_, name, payload):
            order.append(Path(name).relative_to(self.out / "with-source").as_posix())
            return real(self_, name, payload)

        with patch.object(safe.SecuredOutputRoot, "atomic_write_new_bytes", record):
            result = stage.stage_mod(self.out, self.game, "with-source", {200: world}, name="n", sources={path: text})
        mod = self.out / "with-source"
        self.assertEqual(text.encode("latin-1"), (mod / path).read_bytes())
        self.assertEqual(b"// shipped source\n", original.read_bytes())
        self.assertEqual(world, (mod / "data/worlds/world200.wrd").read_bytes())
        self.assertEqual([], LoaderRules.problems(mod, self.game))
        self.assertEqual([path, "data/worlds/world200.wrd", "mod.json"], order)
        self.assertEqual([path, "data/worlds/world200.wrd"], [f["path"] for f in result["files"]])
        self.assert_game_unchanged()

    def test_source_refusals_write_nothing(self) -> None:
        path = "data/MissionScripts/level200/main.msl"
        original = self.game / path
        original.parent.mkdir(parents=True)
        original.write_bytes(b"// original\n")
        text = "init() { Pause(1); }\n"
        world = self.world_with_source(text)
        cases = (
            {"data/MissionScripts/level200/../other.msl": "x"},
            {"data/MissionScripts/level200/NUL.msl": "x"},
            {"data/MissionScripts/level200/missing.msl": "x"},
            {"data/MissionScripts/level201/main.msl": text},
            {path: "\N{EURO SIGN}"},
            {path: "x" * (stage.MAX_SOURCE_BYTES + 1)},
            {path: "init() { Pause(2); }\n"},
            {path: text, "data/MissionScripts/level200/MAIN.msl": text},
            {f"data/MissionScripts/level200/s{i}.msl": text for i in range(stage.MAX_SOURCE_FILES + 1)},
        )
        for sources in cases:
            with self.subTest(paths=list(sources)), self.assertRaises(stage.ModStageError):
                stage.stage_mod(self.out, self.game, "refused", {200: world}, name="n", sources=sources)
            self.assertFalse(self.out.exists())
            self.assertEqual(b"// original\n", original.read_bytes())
        self.assert_game_unchanged()
        with self.assertRaisesRegex(stage.ModStageError, "listed twice"):
            stage.build_manifest("a", "n", "1", {"data/worlds/world200.wrd": world, path: b"x", path.replace("main", "MAIN"): b"x"})

    def test_source_validation_uses_the_world_snapshot_when_the_caller_changes_its_mapping(self) -> None:
        path = "data/MissionScripts/level200/main.msl"
        original = self.game / path
        original.parent.mkdir(parents=True)
        original.write_bytes(b"// original\n")
        source_a, source_b = "init() { Pause(1); }\n", "init() { Pause(2); }\n"
        world_a, world_b = self.world_with_source(source_a), self.world_with_source(source_b)
        real = stage.mc.read_game_source

        def swap(game, requested):
            result = real(game, requested)
            worlds[200] = world_b
            return result

        worlds = {200: world_a}
        with patch.object(stage.mc, "read_game_source", side_effect=swap):
            with self.assertRaisesRegex(stage.ModStageError, "does not compile to the script"):
                stage.stage_mod(self.out, self.game, "mismatch", worlds, name="n", sources={path: source_b})
        self.assertFalse(self.out.exists())

        worlds = {200: world_a}
        with patch.object(stage.mc, "read_game_source", side_effect=swap):
            stage.stage_mod(self.out, self.game, "matches", worlds, name="n", sources={path: source_a})
        self.assertEqual(world_a, (self.out / "matches/data/worlds/world200.wrd").read_bytes())
        self.assertEqual(source_a.encode("latin-1"), (self.out / "matches" / path).read_bytes())

        extra = "data/MissionScripts/level201/main.msl"
        (self.game / extra).parent.mkdir(parents=True)
        (self.game / extra).write_bytes(b"// original\n")
        worlds = {200: world_a}

        def add_level(game, requested):
            result = real(game, requested)
            worlds[201] = world_b
            return result

        with patch.object(stage.mc, "read_game_source", side_effect=add_level):
            with self.assertRaisesRegex(stage.ModStageError, "world being staged"):
                stage.stage_mod(self.out, self.game, "added", worlds, name="n", sources={path: source_a, extra: source_b})
        self.assertFalse((self.out / "added").exists())
        self.assertEqual(b"// original\n", original.read_bytes())

    def test_a_source_cannot_be_attached_to_invalid_or_ambiguous_worlds(self) -> None:
        path = "data/MissionScripts/level200/main.msl"
        original = self.game / path
        original.parent.mkdir(parents=True)
        original.write_bytes(b"// original\n")
        text = "init() { Pause(1); }\n"
        world = self.world_with_source(text)
        model = enc.read_world_model(world)
        model["scripts"].append(model["scripts"][0])
        for body in (b"broken world", world + b"extra", enc.write_world_body(model)):
            with self.subTest(size=len(body)), self.assertRaises(stage.ModStageError):
                stage.stage_mod(self.out, self.game, "refused", {200: body}, name="n", sources={path: text})
            self.assertFalse(self.out.exists())
        self.assertEqual(b"// original\n", original.read_bytes())

    def test_changed_included_header_refuses_the_stale_source_world_pair(self) -> None:
        path = "data/MissionScripts/level200/main.msl"
        original, header = self.game / path, self.game / "data/inc/defs.msl"
        original.parent.mkdir(parents=True)
        header.parent.mkdir(parents=True)
        original.write_text("// original\n", encoding="latin-1")
        header.write_text("#define DELAY 1\n", encoding="latin-1")
        text = "#include data\\inc\\defs.msl\ninit() { Pause(DELAY); }\n"
        world = self.world_with_source(text)
        header.write_text("#define DELAY 2\n", encoding="latin-1")
        with self.assertRaisesRegex(stage.ModStageError, "does not compile to the script"):
            stage.stage_mod(self.out, self.game, "refused", {200: world}, name="n", sources={path: text})
        self.assertFalse(self.out.exists())
        self.assertEqual("#define DELAY 2\n", header.read_text(encoding="latin-1"))

    def test_include_budget_covers_all_sources_before_any_output(self) -> None:
        main = "data/MissionScripts/level200/main.msl"
        other = "data/MissionScripts/level200/second.msl"
        header = self.game / "data/inc/defs.msl"
        header.parent.mkdir(parents=True)
        header_text = "#define DELAY 1\n"
        header.write_text(header_text, encoding="latin-1")
        for path in (main, other):
            (self.game / path).parent.mkdir(parents=True, exist_ok=True)
            (self.game / path).write_text("// original\n", encoding="latin-1")
        text = "#include data\\inc\\defs.msl\ninit() { Pause(DELAY); }\n"
        model = enc.read_world_model(self.world_with_source(text))
        model["scripts"].append(stage.mc.compile_script("second", text, stage.mc.includes_from(self.game), 70))
        world = enc.write_world_body(model)
        for limit, value, words in (("MAX_STAGE_INCLUDES", 1, "included files"), ("MAX_STAGE_INCLUDE_CHARS", len(header_text), "characters of included text")):
            with self.subTest(limit=limit), patch.object(stage, limit, value), self.assertRaisesRegex(stage.ModStageError, words):
                stage.stage_mod(self.out, self.game, "refused", {200: world}, name="n", sources={main: text, other: text})
            self.assertFalse(self.out.exists())

    def test_the_staged_folder_is_exactly_what_the_loader_admits(self) -> None:
        result = self.cli(*self.stage_args("--world", str(self.model_file), "--version", "0.1", "--author", "tests",
                                           "--description", "Moves the first unit.", "--ce-min", "0.1.11"))
        self.assertEqual(0, result.returncode, result.stderr)
        mod = self.out / "tank-move"
        self.assertEqual(["data", "mod.json"], sorted(p.name for p in mod.iterdir()))
        self.assertEqual(["world200.wrd"], sorted(p.name for p in (mod / "data/worlds").iterdir()))
        self.assertEqual(self.edited_body, (mod / "data/worlds/world200.wrd").read_bytes())
        manifest = json.loads((mod / "mod.json").read_text())
        self.assertEqual({"schema": 1, "id": "tank-move", "name": "Moved tank", "version": "0.1", "author": "tests",
                          "description": "Moves the first unit.", "ce_min": "0.1.11",
                          "files": [{"path": "data/worlds/world200.wrd", "size": len(self.edited_body),
                                     "sha256": hashlib.sha256(self.edited_body).hexdigest()}]}, manifest)
        self.assertEqual([], LoaderRules.problems(mod, self.game))
        self.assertIn(f"staged CE mod 'tank-move' in {mod}", result.stdout.decode())
        self.assertIn("mods=tank-move", result.stdout.decode())
        for words in ("refuses mods on Windows", "replays", "recordings", "probes", "virtual clocks", "pilots", "network sessions"):
            self.assertIn(words, result.stdout.decode(), "the closing message says where CE does not load mods")
        self.assert_game_unchanged()
        for path in mod.rglob("*"):
            self.assertFalse(path.is_symlink())
            if path.is_file():
                self.assertEqual(1, path.stat().st_nlink)

    def test_an_edit_made_by_the_move_tool_stages_with_the_pins_its_preview_printed(self) -> None:
        baseline = self.root / "world200.wrd"
        baseline.write_bytes(self.body)
        move = [sys.executable, str(TOOLS / "world_edit_move.py"), str(baseline), "--thing", "0", "--position", "12.5", "3", "4"]
        env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        preview = subprocess.run(move, capture_output=True, timeout=60, env=env)
        self.assertEqual(0, preview.returncode, preview.stderr)
        report = json.loads(preview.stdout)["preview"]
        pins = ["--baseline-sha256", report["baseline"]["sha256"], "--model-sha256", report["model"]["sha256"]]
        emitted = subprocess.run([*move, *pins, "--emit-model", "--acknowledge-unvalidated"], capture_output=True, timeout=60, env=env)
        self.assertEqual(0, emitted.returncode, emitted.stderr)
        self.model_file.write_bytes(emitted.stdout)
        result = self.cli(*self.stage_args("--world", str(self.model_file), *pins))
        self.assertEqual(0, result.returncode, result.stderr)
        mod = self.out / "tank-move"
        self.assertEqual([], LoaderRules.problems(mod, self.game))
        staged = (mod / "data/worlds/world200.wrd").read_bytes()
        self.assertNotEqual(self.body, staged)
        moved = enc.read_world_model(staged)
        self.assertEqual([12.5, 3.0, 4.0], moved["things"][0]["init"]["position"])
        # only that thing's position differs from the baseline model
        moved["things"][0]["init"]["position"] = self.model["things"][0]["init"]["position"]
        self.assertEqual(self.model, moved)

    def test_wrong_pins_refuse_and_nothing_is_written(self) -> None:
        good_model = hashlib.sha256(self.model_file.read_bytes()).hexdigest()
        good_baseline = hashlib.sha256(self.body).hexdigest()
        for flag, value, words in (("--model-sha256", "0" * 64, "model"), ("--baseline-sha256", "f" * 64, "level's own world")):
            with self.subTest(flag):
                result = self.cli(*self.stage_args("--world", str(self.model_file), flag, value))
                self.assertEqual(2, result.returncode)
                self.assertIn(words, result.stderr.decode())
                self.assert_nothing_written()
        result = self.cli(*self.stage_args("--world", str(self.model_file), "--model-sha256", good_model.upper(),
                                           "--baseline-sha256", good_baseline))
        self.assertEqual(0, result.returncode, result.stderr)

    def test_a_base_world_is_staged_beside_the_real_world(self) -> None:
        base_model = json.loads(json.dumps(self.model))
        base_model["things"][1]["init"]["position"][1] = 99.0
        base_body = enc.write_world_body(base_model)
        real_model = json.loads(json.dumps(self.model))
        real_model["baseLevel"] = 1
        self.write_archive(archive(enc.write_world_body(real_model), base_body, base_level=1))
        edited_real = json.loads(json.dumps(real_model))
        edited_real["things"][0]["init"]["position"][0] = 21.0
        edited_base = json.loads(json.dumps(base_model))
        edited_base["things"][1]["init"]["position"][1] = 7.0
        self.model_file.write_bytes(model_json(edited_real))
        base_file = self.root / "base.json"
        base_file.write_bytes(model_json(edited_base))
        result = self.cli(*self.stage_args("--world", str(self.model_file), "--base-world", str(base_file)))
        self.assertEqual(0, result.returncode, result.stderr)
        mod = self.out / "tank-move"
        self.assertEqual(["world001.wrd", "world200.wrd"], sorted(p.name for p in (mod / "data/worlds").iterdir()))
        self.assertEqual(enc.write_world_body(edited_base), (mod / "data/worlds/world001.wrd").read_bytes())
        self.assertEqual(enc.write_world_body(edited_real), (mod / "data/worlds/world200.wrd").read_bytes())
        self.assertEqual([], LoaderRules.problems(mod, self.game))
        # the base world alone: the real world then comes from the archive, and an unedited base world is a no-op
        other = self.root / "other"
        result = self.cli(*self.stage_args("--base-world", str(base_file), mod_id="base-only", out=other))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(["world001.wrd"], sorted(p.name for p in (other / "base-only/data/worlds").iterdir()))
        self.assertEqual([], LoaderRules.problems(other / "base-only", self.game))
        same = self.root / "same-base.json"
        same.write_bytes(model_json(base_model))
        result = self.cli(*self.stage_args("--base-world", str(same), mod_id="noop", out=other))
        self.assertEqual(2, result.returncode)
        self.assertIn("byte-identical", result.stderr.decode())
        self.assertFalse((other / "noop").exists())

    def test_a_real_world_that_names_itself_as_its_base_cannot_share_its_file_with_a_base_world(self) -> None:
        # The real world of level 200 is data/worlds/world200.wrd; if its baseLevel is 200 too, a base-world file would
        # have the same name and the second would silently replace the first.
        self.edited["baseLevel"] = 200
        self.model_file.write_bytes(model_json(self.edited))
        base_file = self.root / "base.json"
        base_file.write_bytes(model_json(self.model))
        result = self.cli(*self.stage_args("--world", str(self.model_file), "--base-world", str(base_file)))
        self.assertEqual(2, result.returncode, result.stdout)
        self.assertIn("would both be data/worlds/world200.wrd", result.stderr.decode())
        self.assert_nothing_written()
        # without a base-world file the same edit is a plain world and stages (the archive holds no base world, and
        # a base world that is the level itself is the loader's business, not a second file)
        self.edited["baseLevel"] = -1
        self.model_file.write_bytes(model_json(self.edited))
        result = self.cli(*self.stage_args("--world", str(self.model_file)))
        self.assertEqual(0, result.returncode, result.stderr)

    def test_ce_min_after_ce_max_is_refused_and_a_range_of_one_version_is_not(self) -> None:
        # compared number by number with the missing ones zero, as the loader orders versions: 1.10 is after 1.9
        for low, high, refused in (("1.2", "1.1", True), ("0.1.11", "0.1.10", True), ("1.10", "1.9", True), ("2", "1.99999", True),
                                   ("1.2.0.1", "1.2", True), ("1.2", "1.2", False), ("1.2.0", "1.2", False), ("1.2", "1.2.0.0", False),
                                   ("1.9", "1.10", False), ("0.1.11", "0.1.12", False), ("1", "99999.99999.99999.99999", False)):
            with self.subTest(ce_min=low, ce_max=high):
                out = self.root / f"range-{low}-{high}"
                result = self.cli(*self.stage_args("--world", str(self.model_file), "--ce-min", low, "--ce-max", high, out=out))
                if refused:
                    self.assertEqual(2, result.returncode, result.stdout)
                    self.assertIn(f"ce_min {low} is after ce_max {high}", result.stderr.decode())
                    self.assertFalse(out.exists(), "a refused range writes nothing")
                else:
                    self.assertEqual(0, result.returncode, result.stderr)
                    self.assertEqual([], LoaderRules.problems(out / "tank-move", self.game))
        # one bound alone is never a range to compare
        for flag, value in (("--ce-min", "99999"), ("--ce-max", "0")):
            with self.subTest(only=flag):
                out = self.root / f"one{flag}"
                result = self.cli(*self.stage_args("--world", str(self.model_file), flag, value, out=out))
                self.assertEqual(0, result.returncode, result.stderr)
        for low, high in (("1.2", "1.1"), ("1.10", "1.9")):
            with self.subTest(builder=(low, high)), self.assertRaisesRegex(stage.ModStageError, "is after ce_max"):
                stage.build_manifest("a", "n", "1", {"data/worlds/world001.wrd": self.edited_body}, ce_min=low, ce_max=high)
        stage.build_manifest("a", "n", "1", {"data/worlds/world001.wrd": self.edited_body}, ce_min="1.9", ce_max="1.10")

    def test_what_the_loader_would_not_find_is_refused(self) -> None:
        # a different base world than the archive holds needs its own file; a base file needs a base world to be read
        self.edited["baseLevel"] = 3
        self.model_file.write_bytes(model_json(self.edited))
        result = self.cli(*self.stage_args("--world", str(self.model_file)))
        self.assertEqual(2, result.returncode)
        self.assertIn("world003.wrd", result.stderr.decode())
        self.assert_nothing_written()
        base_file = self.root / "base.json"
        base_file.write_bytes(model_json(self.model))
        result = self.cli(*self.stage_args("--base-world", str(base_file)))
        self.assertEqual(2, result.returncode)
        self.assertIn("no base world", result.stderr.decode())
        self.assert_nothing_written()
        self.edited["baseLevel"] = -1
        self.model_file.write_bytes(model_json(self.edited))
        result = self.cli(*self.stage_args("--world", str(self.model_file), "--base-world", str(base_file)))
        self.assertEqual(2, result.returncode)
        self.assert_nothing_written()

    def test_nothing_to_stage_and_no_op_edits_are_refused(self) -> None:
        for args, words in (([], "nothing to stage"), (["--world", str(self.root / "same.json")], "byte-identical")):
            with self.subTest(words):
                (self.root / "same.json").write_bytes(model_json(self.model))
                result = self.cli(*self.stage_args(*args))
                self.assertEqual(2, result.returncode)
                self.assertIn(words, result.stderr.decode())
                self.assert_nothing_written()

    def test_a_destination_inside_the_game_folder_is_refused(self) -> None:
        link = self.root / "link"
        link.symlink_to(self.game / "data", target_is_directory=True)
        for label, out in (("inside the game", self.game / "mods"), ("in the data folder", self.game / "data"),
                           ("through a link", link / "mods")):
            with self.subTest(label):
                result = self.cli(*self.stage_args("--world", str(self.model_file), out=out))
                self.assertEqual(2, result.returncode, result.stdout)
                self.assertIn("refused", result.stderr.decode())
                self.assertEqual(["200_res_PC.aya"], sorted(p.name for p in self.resources.iterdir()))
                self.assertEqual(["data"], sorted(p.name for p in self.game.iterdir()))
                self.assertEqual(self.archive_bytes, self.archive_path.read_bytes())

    def test_a_folder_that_holds_anything_is_never_written_into(self) -> None:
        mod = self.out / "tank-move"
        mod.mkdir(parents=True)
        (mod / "keep.txt").write_text("mine")
        result = self.cli(*self.stage_args("--world", str(self.model_file)))
        self.assertEqual(2, result.returncode)
        self.assertIn("already holds", result.stderr.decode())
        self.assertEqual(["keep.txt"], sorted(p.name for p in mod.iterdir()))
        # a second stage into a finished mod leaves the first one intact
        other = self.root / "again"
        self.assertEqual(0, self.cli(*self.stage_args("--world", str(self.model_file), out=other)).returncode)
        first = (other / "tank-move/mod.json").read_bytes()
        result = self.cli(*self.stage_args("--world", str(self.model_file), out=other))
        self.assertEqual(2, result.returncode)
        self.assertEqual(first, (other / "tank-move/mod.json").read_bytes())

    def test_identity_text_is_held_to_the_loaders_rules_before_anything_is_read(self) -> None:
        bad = (("--id", "Tank", "id"), ("--id", "a" * 49, "id"), ("--id", "../x", "id"), ("--id", "", "id"),
               ("--name", "", "name"), ("--name", "n" * 65, "name"), ("--name", "café", "ASCII"),
               ("--version", "", "version"), ("--version", "v" * 33, "version"), ("--author", "a" * 65, "author"),
               ("--description", "d" * 1025, "description"), ("--ce-min", "1.2.3.4.5", "ce_min"),
               ("--ce-min", "a.b", "ce_min"), ("--ce-max", "123456", "ce_max"), ("--ce-max", "0.", "ce_max"))
        for flag, value, words in bad:
            with self.subTest(flag=flag, value=value[:12]):
                args = self.stage_args("--world", str(self.model_file))
                if flag in args:
                    args[args.index(flag) + 1] = value
                else:
                    args += [flag, value]
                result = self.cli(*args)
                self.assertEqual(2, result.returncode, result.stdout)
                self.assertIn(words, result.stderr.decode())
                self.assert_nothing_written()
        for flag, value in (("--id", "a" * 48), ("--name", "n" * 64), ("--version", "v" * 32), ("--ce-max", "99999.99999.99999.99999")):
            with self.subTest(flag=flag, edge="accepted"):
                args = self.stage_args("--world", str(self.model_file), out=self.root / f"edge{flag}")
                if flag in args:
                    args[args.index(flag) + 1] = value
                else:
                    args += [flag, value]
                result = self.cli(*args)
                self.assertEqual(0, result.returncode, result.stderr)
                folder = self.root / f"edge{flag}" / (value if flag == "--id" else "tank-move")
                self.assertEqual([], LoaderRules.problems(folder, self.game))

    def test_modes_that_do_not_belong_together_are_refused(self) -> None:
        cases = ((["stage", "--game", str(self.game), "--level", "200", "--as-mod", "--stdout", "--out", str(self.out), "--id", "a",
                   "--name", "n", "--world", str(self.model_file)], "--stdout"),
                 (["stage", "--game", str(self.game), "--level", "200", "--as-mod", "--out", str(self.out), "--name", "n",
                   "--world", str(self.model_file)], "--id"),
                 (["stage", "--game", str(self.game), "--level", "200", "--stdout", "--out", str(self.out)], "only for --as-mod"),
                 (["stage", "--game", str(self.game), "--level", "200", "--stdout", "--id", "a"], "only for --as-mod"),
                 (["stage", "--game", str(self.game), "--level", "200", "--as-mod", "--user", str(self.root / "u"), "--out", str(self.out),
                   "--id", "a", "--name", "n", "--world", str(self.model_file)], "--user"),
                 (["stage", "--game", str(self.game), "--level", "999", "--as-mod", "--out", str(self.out), "--id", "a",
                   "--name", "n", "--world", str(self.model_file)], "no level archive"))
        for args, words in cases:
            with self.subTest(words=words):
                result = self.cli(*args)
                self.assertEqual(2, result.returncode, result.stdout)
                self.assertIn(words, result.stderr.decode())
                self.assert_nothing_written()
        self.assertFalse((self.root / "u").exists())

    def test_a_model_the_encoder_cannot_hold_produces_no_folder(self) -> None:
        self.edited["things"][0]["init"]["position"][0] = 0.1  # not a float32 value
        self.model_file.write_bytes(model_json(self.edited))
        result = self.cli(*self.stage_args("--world", str(self.model_file)))
        self.assertEqual(2, result.returncode)
        self.assert_nothing_written()
        self.model_file.write_bytes(b"not json")
        result = self.cli(*self.stage_args("--world", str(self.model_file)))
        self.assertEqual(2, result.returncode)
        self.assertIn("not JSON", result.stderr.decode())
        self.assert_nothing_written()

    def test_files_are_published_before_the_manifest_and_a_failed_manifest_leaves_the_mod_inert(self) -> None:
        order = []
        real = safe.SecuredOutputRoot.atomic_write_new_bytes

        def record(self_, path, payload):
            order.append(Path(path).name)
            return real(self_, path, payload)
        with patch.object(safe.SecuredOutputRoot, "atomic_write_new_bytes", record):
            stage.stage_mod(self.out, self.game, "tank-move", {200: self.edited_body}, name="n")
        self.assertEqual(["world200.wrd", "mod.json"], order)

        def fail_on_manifest(self_, path, payload):
            if Path(path).name == "mod.json":
                raise OSError("disk full")
            return real(self_, path, payload)
        with patch.object(safe.SecuredOutputRoot, "atomic_write_new_bytes", fail_on_manifest):
            with self.assertRaisesRegex(stage.ModStageError, "including mod.json"):
                stage.stage_mod(self.out, self.game, "half", {200: self.edited_body}, name="n")
        self.assertFalse((self.out / "half" / "mod.json").exists())

        def fail_after_manifest(self_, path, payload):
            real(self_, path, payload)
            if Path(path).name == "mod.json":
                raise OSError("failed after publication")
        with patch.object(safe.SecuredOutputRoot, "atomic_write_new_bytes", fail_after_manifest):
            with self.assertRaisesRegex(stage.ModStageError, "including mod.json") as raised:
                stage.stage_mod(self.out, self.game, "published", {200: self.edited_body}, name="n")
        self.assertIn(str(self.out / "published"), str(raised.exception))
        self.assertIn("may be active on the next game launch", str(raised.exception))
        self.assertTrue((self.out / "published/mod.json").exists())

    def test_the_manifest_builder_holds_the_same_limits_as_the_loader(self) -> None:
        body = self.edited_body
        stage.build_manifest("a", "n", "1", {"data/worlds/world001.wrd": body})
        for files, words in (({}, "at least one file"), ({"data/worlds/world1.wrd": body}, "world files and mission sources only"),
                             ({"data/other.bin": body}, "world files and mission sources only"), ({"data/worlds/world001.wrd": b""}, "1 byte"),
                             ({"data/worlds/world001.wrd": bytes((4 << 20) + 1)}, "1 byte")):
            with self.subTest(words=words), self.assertRaisesRegex(stage.ModStageError, words):
                stage.build_manifest("a", "n", "1", files)
        # the loader refuses a world file over 4 MiB (mods.cpp kMaxWorld) and admits exactly 4 MiB: literals, not the module constant
        stage.build_manifest("a", "n", "1", {"data/worlds/world001.wrd": bytes(4 << 20)})
        for level in (-1, 1000, "3", True):
            with self.subTest(level=level), self.assertRaises(stage.ModStageError):
                stage.world_path(level)
        self.assertEqual("data/worlds/world007.wrd", stage.world_path(7))
        with patch.object(stage, "MAX_TOTAL_BYTES", 3), self.assertRaisesRegex(stage.ModStageError, "total at most"):
            stage.build_manifest("a", "n", "1", {"data/worlds/world001.wrd": b"ab", "data/MissionScripts/level001/a.msl": b"cd"})

    def test_stream_commands_still_refuse_every_output_path(self) -> None:
        for args in (["extract", "--game", str(self.game), "--level", "200", "--stdout", "--out", str(self.out)],
                     ["stage", "--game", str(self.game), "--level", "200", "--stdout", "--user", str(self.root / "u")]):
            result = self.cli(*args)
            self.assertEqual(2, result.returncode)
            self.assertFalse(self.out.exists() or (self.root / "u").exists())


if __name__ == "__main__":
    unittest.main()
