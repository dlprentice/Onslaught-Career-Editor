#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Checks `world_resources_encode.py stage --as-mod` and `stage_mod(files=...)` (tools/world_mod_stage.py) on authored data only (no game bytes).

The staged folder must be exactly what the CE mod loader admits. LoaderRules below is an independent restatement of the
loader's start-up checks (onslaught-ce port/platform/common/mods.cpp: ValidId, ReadManifest, CheckPath, WorldFile,
LevelArchiveName, CheckPacked, CheckLevelArchive, LoadMod), used as the oracle; it has controls of its own so it cannot pass
everything, and the structure table at the bottom runs the stager and the oracle on the same archives and requires them to
agree. The real loader is the final arbiter: the staged folder is also loaded by CE in the acceptance run recorded in the
work's report, and by the loader's host driver."""
from __future__ import annotations

import hashlib
import inspect
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
import zlib
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
    ARCHIVE = re.compile(r"data/resources/([0-9]{3})_res_pc\.aya")
    TAGS = {b"LVLR", b"TARG", b"AYAD", b"TEXT", b"MESH", b"IMPS", b"LNDS", b"SURF", b"ERES", b"SSHD", b"WRES"}
    GUARDS = (344, 372, 316, 5084, 92)

    @staticmethod
    def game_has(game_dir: Path, path: str) -> bool:
        """A regular file at this path, each component compared without regard to case (the loader's PortGameHasFile)."""
        want = path.lower()
        for folder, _dirs, names in os.walk(game_dir):
            rel = Path(folder).relative_to(game_dir).parts
            if any("/".join([*rel, name]).lower() == want for name in names):
                return True
        return False

    @staticmethod
    def unpack(data: bytes, texture: bool = False, keep: bool = False):
        """CheckPacked: (None, the unpacked bytes) when the game's block reader can read the file, else (why, None)."""
        at, total, blocks, short, head = 0, 0, 0, False, b""
        pieces = []
        while at < len(data):
            if len(data) - at < 4:
                return "a cut block header", None
            n = int.from_bytes(data[at:at + 4], "little")
            at += 4
            if n == 0 or n > 0x102927:
                return "a block larger than the game's block buffer", None
            if len(data) - at < n:
                return "a cut block", None
            if short:
                return "a short block before the last", None
            reader = zlib.decompressobj()
            try:
                piece = reader.decompress(data[at:at + n], 0x102927 + 1)
            except zlib.error:
                return "a block that does not unpack", None
            if len(piece) > 0x102927 or not reader.eof or reader.unused_data:
                return "a block that does not unpack", None
            if len(piece) > 1 << 20:
                return "a block over 1 MiB", None
            short = len(piece) < 1 << 20
            head = (head + piece)[:128]
            total += len(piece)
            if keep and total > 32 << 20:
                return "unpacks to more than 32 MiB", None
            pieces.append(piece)
            at += n
            blocks += 1
            if total > 64 << 20:
                return "unpacks to more than 64 MiB", None
        if blocks == 0:
            return "an empty packed file", None
        if texture:
            if total >= 0x500000:
                return "a texture of 5 MiB or more", None
            if len(head) < 128 or head[:4] != b"DDS " or int.from_bytes(head[4:8], "little") != 124:
                return "a texture that is not a DDS image", None
            height, width = int.from_bytes(head[12:16], "little"), int.from_bytes(head[16:20], "little")
            if not (0 < width <= 4096 and 0 < height <= 4096):
                return "a texture over 4096 texels a side", None
        return None, b"".join(pieces) if keep else None

    @staticmethod
    def split(stream: bytes, start: int, end: int):
        """The chunks [(tag, payload offset, size)] that exactly tile stream[start:end], or ValueError."""
        out, at = [], start
        while at < end:
            if end - at < 8:
                raise ValueError("a cut chunk header")
            size = int.from_bytes(stream[at + 4:at + 8], "little")
            if size > end - at - 8:
                raise ValueError("a chunk past its end")
            out.append((stream[at:at + 4], at + 8, size))
            at += 8 + size
        return out

    @classmethod
    def walk(cls, stream: bytes, level: int):
        """CheckLevelArchive: None, or why the stream is not a level archive the loader's readers can walk."""
        try:
            top = cls.split(stream, 0, len(stream))
        except ValueError as error:
            return str(error)
        word = lambda at: int.from_bytes(stream[at:at + 4], "little")
        tags = [tag for tag, _, _ in top]
        if len(top) > 2048:
            return "more than 2048 chunks"
        if any(tag not in cls.TAGS for tag in tags):
            return "a tag a level archive does not hold"
        if len(top) < 3 or tags[:3] != [b"LVLR", b"TARG", b"AYAD"]:
            return "not LVLR, TARG, AYAD first"
        if (top[0][2], word(top[0][1])) != (4, 103) or (top[1][2], word(top[1][1])) != (4, 1):
            return "LVLR is not 103 or TARG is not 1"
        if top[2][2] != 24 or tuple(word(top[2][1] + 4 * i) for i in range(5)) != cls.GUARDS:
            return "AYAD guards"
        if any(tag in (b"LVLR", b"TARG", b"AYAD") for tag in tags[3:]):
            return "LVLR, TARG or AYAD again"
        for tag, at, size in top:
            if tag == b"TEXT" and (size < 360 or stream[at:at + 4] != b"DXTX" or word(at + 4) != size - 8 or stream[at + 8:at + 12] != b"CTEX"):
                return "a TEXT that is not DXTX/CTEX of 360 bytes"
            if tag == b"MESH" and (size < 9 or stream[at:at + 4] != b"PMSH" or word(at + 4) != size - 8):
                return "a MESH that is not PMSH"
        if tags.count(b"WRES") != 1 or tags[-1] != b"WRES":
            return "not exactly one WRES, last"
        _, at, size = top[-1]
        try:
            (wrld,) = cls.split(stream, at, at + size)
            if wrld[0] != b"WRLD":
                return "WRES does not hold a WRLD"
            kids = cls.split(stream, wrld[1], wrld[1] + wrld[2])
        except (ValueError, TypeError):
            return "WRES does not hold exactly one well-formed WRLD"
        if not kids or kids[0][0] != b"WDAT" or kids[0][2] != 8:
            return "WRLD does not start with an 8-byte WDAT"
        base, real = (int.from_bytes(stream[kids[0][1] + i:kids[0][1] + i + 4], "little", signed=True) for i in (0, 4))
        if real != level:
            return "WDAT names another level"
        if base != -1 and not 0 <= base <= 999:
            return "a base world that is not a level"
        if [kid[0] for kid in kids] != [b"WDAT"] + ([b"BSWD"] if base != -1 else []) + [b"RLWD"]:
            return "WRLD does not hold WDAT, then BSWD only with a base world, then RLWD, and nothing else"
        for kid in kids[1:]:
            if not 2 <= kid[2] <= 4 << 20:
                return "an unusable body size"
            if not 43 <= int.from_bytes(stream[kid[1]:kid[1] + 2], "little") <= 50:
                return "a body version CWorld::LoadWorld refuses"
        return None

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
            has = cls.game_has(game_dir, path)
            named = cls.ARCHIVE.fullmatch(key)
            archive = not has and named is not None and 850 <= int(named.group(1)) <= 899
            if not world and not archive and not has:
                out.append(f"{path}: the game has no such file")
            if world and size > 4 << 20:
                out.append(f"{path}: a world file larger than 4 MiB")
            if archive and size > 8 << 20:
                out.append(f"{path}: an added level archive larger than 8 MiB")
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
            elif key.endswith(".aya"):
                texture = key.startswith(("data/resources/textures/", "data/resources/dxtntextures/"))
                why, stream = cls.unpack((mod_dir / path).read_bytes(), texture=texture, keep=archive)
                if why is None and archive:
                    why = cls.walk(stream, int(named.group(1)))
                if why:
                    out.append(f"{path}: {why}")
        return out



# ---- authored level archives -------------------------------------------------------------------------------------------
GUARDS = LoaderRules.GUARDS
WORLD_BYTES = struct.pack("<H", 50) + bytes(30)
NOT_ZLIB = struct.pack("<I", 4) + b"abcd"   # one block whose four bytes are not a zlib stream


def mesh_descriptor(name: str, runtime_id: int) -> bytes:
    """A MESH chunk payload as the game's archives hold it (325 bytes): PMSH/PMS2, a 300-byte name, the runtime id, a zero and a NUL."""
    return (b"PMSH" + struct.pack("<I", 317) + b"PMS2" + struct.pack("<I", 309) + name.encode("ascii").ljust(300, b"\0")
            + struct.pack("<ii", runtime_id, 0) + b"\0")


def text_descriptor(name: str) -> bytes:
    """A TEXT chunk payload as the game's archives hold it (372 bytes): DXTX wrapper, CTEX with the name at 0x18."""
    return fixtures.text_record(name)[8:]


def level_chunks(level: int = 888, *, base: int = -1, texts=("a.tga",), meshes=("a.msh",), children=None, body: bytes = WORLD_BYTES):
    """The top-level chunks [(tag, payload)] of a level archive the loader admits (children replaces what WRLD holds)."""
    if children is None:
        children = [(b"WDAT", struct.pack("<ii", base, level))]
        if base != -1:
            children.append((b"BSWD", body))
        children.append((b"RLWD", body))
    wrld = b"".join(fixtures.chunk(tag, payload) for tag, payload in children)
    return ([(b"LVLR", struct.pack("<I", 103)), (b"TARG", struct.pack("<I", 1)), (b"AYAD", struct.pack("<6I", *GUARDS, 1))]
            + [(b"TEXT", text_descriptor(name)) for name in texts]
            + [(b"MESH", mesh_descriptor(name, 260 + index)) for index, name in enumerate(meshes)]
            + [(b"IMPS", b"i"), (b"LNDS", b""), (b"SURF", b"s"), (b"ERES", b"e"), (b"SSHD", b"h"),
               (b"WRES", fixtures.chunk(b"WRLD", wrld))])


def framed_text(size: int) -> bytes:
    """A TEXT payload of exactly `size` bytes whose DXTX and CTEX framing is right and whose contents are not looked at."""
    return b"DXTX" + struct.pack("<I", size - 8) + b"CTEX" + bytes(size - 12)


def level_stream(chunks) -> bytes:
    return b"".join(fixtures.chunk(tag, payload) for tag, payload in chunks)


def packed(stream: bytes, level: int = 6) -> bytes:
    """A stream in 1 MiB blocks, each [u32 length][zlib data] (CDXMemBuffer::ReadBlock's framing)."""
    out = b""
    for start in range(0, len(stream), 1 << 20):
        block = zlib.compress(stream[start:start + (1 << 20)], level)
        out += struct.pack("<I", len(block)) + block
    return out


def level_archive(level: int = 888, **options) -> bytes:
    return packed(level_stream(level_chunks(level, **options)))

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
            with self.assertRaisesRegex(stage.ModStageError, "could not write the mod"):
                stage.stage_mod(self.out, self.game, "half", {200: self.edited_body}, name="n")
        self.assertFalse((self.out / "half" / "mod.json").exists())

    def test_the_manifest_builder_holds_the_same_limits_as_the_loader(self) -> None:
        body = self.edited_body
        stage.build_manifest("a", "n", "1", {"data/worlds/world001.wrd": body})
        for files, words in (({}, "at least one file"), ({"data/worlds/world1.wrd": body}, "world files only"),
                             ({"data/other.bin": body}, "world files only"), ({"data/worlds/world001.wrd": b""}, "1 byte"),
                             ({"data/worlds/world001.wrd": bytes((4 << 20) + 1)}, "1 byte")):
            with self.subTest(words=words), self.assertRaisesRegex(stage.ModStageError, words):
                stage.build_manifest("a", "n", "1", files)
        # the loader refuses a world file over 4 MiB (mods.cpp kMaxWorld) and admits exactly 4 MiB: literals, not the module constant
        stage.build_manifest("a", "n", "1", {"data/worlds/world001.wrd": bytes(4 << 20)})
        for level in (-1, 1000, "3", True):
            with self.subTest(level=level), self.assertRaises(stage.ModStageError):
                stage.world_path(level)
        self.assertEqual("data/worlds/world007.wrd", stage.world_path(7))

    def test_stream_commands_still_refuse_every_output_path(self) -> None:
        for args in (["extract", "--game", str(self.game), "--level", "200", "--stdout", "--out", str(self.out)],
                     ["stage", "--game", str(self.game), "--level", "200", "--stdout", "--user", str(self.root / "u")]):
            result = self.cli(*args)
            self.assertEqual(2, result.returncode)
            self.assertFalse(self.out.exists() or (self.root / "u").exists())


# ---- the structure of an added level archive: the stager and the oracle must agree ----------------------------------------
def structure_cases():
    """(label, unpacked stream, the module's refusal contains this) for streams the loader refuses; the words are None for a
    stream it admits. Chunks are changed one rule at a time."""
    good = level_chunks()

    def put(index, payload=None, tag=None, chunks=None):
        out = list(chunks or good)
        old_tag, old_payload = out[index]
        out[index] = (tag or old_tag, old_payload if payload is None else payload)
        return out

    def insert(index, tag, payload):
        out = list(good)
        out.insert(index, (tag, payload))
        return out

    texts = 3  # LVLR, TARG, AYAD
    first_text, first_mesh, wres = texts, texts + 1, len(good) - 1
    word = lambda value: struct.pack("<I", value)
    wrld = lambda *kids: [(b"WRES", fixtures.chunk(b"WRLD", b"".join(fixtures.chunk(t, d) for t, d in kids)))]
    wdat = (b"WDAT", struct.pack("<ii", -1, 888))
    body = WORLD_BYTES
    cases = [
        ("an admitted archive", level_stream(good), None),
        ("an admitted archive with a base world", level_stream(level_chunks(base=10)), None),
        ("LVLR not first", level_stream([good[1], good[0]] + good[2:]), "LVLR 103"),
        ("LVLR 102", level_stream(put(0, word(102))), "LVLR 103"),
        ("LVLR with 8 bytes", level_stream(put(0, word(103) + word(0))), "LVLR 103"),
        ("TARG 2", level_stream(put(1, word(2))), "TARG 1"),
        ("TARG missing second", level_stream(good[:1] + good[2:]), "TARG 1"),
        ("AYAD not third", level_stream(good[:2] + [good[first_text], good[2]] + good[first_text + 1:]), "AYAD guards third"),
        ("AYAD of 20 bytes", level_stream(put(2, struct.pack("<5I", *GUARDS))), "AYAD guards third"),
        ("AYAD of 28 bytes", level_stream(put(2, struct.pack("<7I", *GUARDS, 1, 1))), "AYAD guards third"),
        *[(f"AYAD guard {i} wrong", level_stream(put(2, struct.pack("<6I", *[g + (j == i) for j, g in enumerate(GUARDS)], 1))),
           "other structure sizes") for i in range(5)],
        ("an unknown tag", level_stream(insert(first_text, b"XXXX", b"")), "tag a level archive does not hold"),
        ("a goodie tag", level_stream(insert(first_text, b"GDIE", b"")), "tag a level archive does not hold"),
        ("a base-archive tag", level_stream(insert(first_text, b"VSDS", b"")), "tag a level archive does not hold"),
        ("TEXT of 24 bytes", level_stream(put(first_text, bytes(24))), "DXTX/CTEX"),
        # the game reads a TEXT as DXTX, CTEX and 344 bytes whatever the headers say, so a shorter one is read into the next chunk
        ("TEXT of 25 bytes", level_stream(put(first_text, framed_text(25))), "texture record of at least 360 bytes"),
        ("TEXT of 344 bytes with a PLAT chunk inside", level_stream(put(first_text, b"DXTX" + word(336) + b"CTEX" + word(0)
                                                                      + fixtures.chunk(b"PLAT", bytes(8)) + bytes(344 - 36))),
         "texture record of at least 360 bytes"),
        ("TEXT of 359 bytes", level_stream(put(first_text, framed_text(359))), "texture record of at least 360 bytes"),
        ("TEXT of 360 bytes", level_stream(put(first_text, framed_text(360))), None),
        ("a second LVLR", level_stream(insert(3, b"LVLR", b"")), "repeats LVLR, TARG or AYAD"),
        ("a second TARG", level_stream(insert(3, b"TARG", b"")), "repeats LVLR, TARG or AYAD"),
        ("a second AYAD", level_stream(insert(3, b"AYAD", b"")), "repeats LVLR, TARG or AYAD"),
        ("a second AYAD late", level_stream(insert(len(good) - 1, b"AYAD", struct.pack("<6I", *GUARDS, 1))), "repeats LVLR, TARG or AYAD"),
        ("TEXT without DXTX", level_stream(put(first_text, b"XXXX" + good[first_text][1][4:])), "DXTX/CTEX"),
        ("TEXT with a wrong wrapper size", level_stream(put(first_text, good[first_text][1][:4] + word(7) + good[first_text][1][8:])), "DXTX/CTEX"),
        ("TEXT without CTEX", level_stream(put(first_text, good[first_text][1][:8] + b"XXXX" + good[first_text][1][12:])), "DXTX/CTEX"),
        ("MESH of 8 bytes", level_stream(put(first_mesh, b"PMSH" + word(0))), "PMSH"),
        ("MESH without PMSH", level_stream(put(first_mesh, b"XXXX" + good[first_mesh][1][4:])), "PMSH"),
        ("MESH with a wrong wrapper size", level_stream(put(first_mesh, good[first_mesh][1][:4] + word(1) + good[first_mesh][1][8:])), "PMSH"),
        ("no WRES", level_stream(good[:-1]), "exactly one WRES"),
        ("two WRES", level_stream(good + [good[-1]]), "exactly one WRES"),
        ("a chunk after WRES", level_stream(good + [(b"SSHD", b"x")]), "after its WRES"),
        ("WRES empty", level_stream(put(wres, b"")), "does not hold one WRLD"),
        ("WRES holds another tag", level_stream(put(wres, fixtures.chunk(b"WDAT", struct.pack("<ii", -1, 888)))), "does not hold one WRLD"),
        ("WRES holds two chunks", level_stream(put(wres, fixtures.chunk(b"WRLD", b"") * 2)), "does not hold one WRLD"),
        ("no WDAT", level_stream(level_chunks(children=[(b"RLWD", body)])), "WRLD that does not start with WDAT"),
        ("an empty WRLD", level_stream(level_chunks(children=[])), "WRLD without WDAT"),
        ("RLWD before WDAT", level_stream(level_chunks(children=[(b"RLWD", body), wdat])), "WRLD that does not start with WDAT"),
        ("RLWD and BSWD swapped", level_stream(level_chunks(children=[(b"WDAT", struct.pack("<ii", 10, 888)), (b"RLWD", body), (b"BSWD", body)])),
         "BSWD does not follow its WDAT"),
        ("WDAT of 12 bytes", level_stream(level_chunks(children=[(b"WDAT", struct.pack("<iii", -1, 888, 0)), (b"RLWD", body)])),
         "WDAT is not 8 bytes"),
        ("WDAT of 4 bytes", level_stream(level_chunks(children=[(b"WDAT", struct.pack("<i", -1)), (b"RLWD", body)])), "WDAT is not 8 bytes"),
        ("two WDAT", level_stream(level_chunks(children=[wdat, wdat, (b"RLWD", body)])), "RLWD does not follow its WDAT and base world"),
        ("no RLWD", level_stream(level_chunks(children=[wdat])), "without a real world body (RLWD)"),
        ("a base world and no real world", level_stream(level_chunks(children=[(b"WDAT", struct.pack("<ii", 10, 888)), (b"BSWD", body)])),
         "without a real world body (RLWD)"),
        ("a base level and nothing after WDAT", level_stream(level_chunks(children=[(b"WDAT", struct.pack("<ii", 10, 888))])),
         "names a base world but whose WRLD has no BSWD"),
        ("two RLWD", level_stream(level_chunks(children=[wdat, (b"RLWD", body), (b"RLWD", body)])), "chunks after its real world body"),
        ("two BSWD", level_stream(level_chunks(children=[(b"WDAT", struct.pack("<ii", 5, 888)), (b"BSWD", body), (b"BSWD", body), (b"RLWD", body)])),
         "RLWD does not follow its WDAT and base world"),
        ("an unknown child", level_stream(level_chunks(children=[wdat, (b"XXXX", b""), (b"RLWD", body)])), "RLWD does not follow its WDAT and base world"),
        ("an unknown child after RLWD", level_stream(level_chunks(children=[wdat, (b"RLWD", body), (b"XXXX", b"")])), "chunks after its real world body"),
        ("an RLWD of 1 byte", level_stream(level_chunks(children=[wdat, (b"RLWD", b"2")])), "unusable size"),
        ("a body of version 42", level_stream(level_chunks(body=struct.pack("<H", 42) + bytes(30))), "version"),
        ("a body of version 51", level_stream(level_chunks(body=struct.pack("<H", 51) + bytes(30))), "version"),
        ("a body of version 43", level_stream(level_chunks(body=struct.pack("<H", 43) + bytes(30))), None),
        ("an RLWD that declares one byte more than WRLD holds", level_stream(put(wres, fixtures.chunk(
            b"WRLD", fixtures.chunk(*wdat) + b"RLWD" + word(len(body) + 1) + body))), "past its end"),
        ("an RLWD that declares eight bytes more than WRLD holds", level_stream(put(wres, fixtures.chunk(
            b"WRLD", fixtures.chunk(*wdat) + b"RLWD" + word(len(body) + 8) + body))), "past its end"),
        ("a BSWD that declares one byte more than WRLD holds", level_stream(put(wres, fixtures.chunk(
            b"WRLD", fixtures.chunk(b"WDAT", struct.pack("<ii", 10, 888)) + b"BSWD" + word(len(body) + 1) + body))), "past its end"),
        ("a child that runs past its WRLD", level_stream(put(wres, fixtures.chunk(b"WRLD", wdat[0] + word(8) + struct.pack("<ii", -1, 888) + b"RLWD" + word(500) + b"xx"))), "past its end"),
        ("WDAT names level 889", level_stream(level_chunks(889)), "another level"),
        ("base world -2", level_stream(level_chunks(base=-2)), "not a level number"),
        ("base world 1000", level_stream(level_chunks(base=1000)), "not a level number"),
        ("base world 999", level_stream(level_chunks(base=999)), None),
        ("base world 0", level_stream(level_chunks(base=0)), None),
        ("a base world without BSWD", level_stream(level_chunks(children=[(b"WDAT", struct.pack("<ii", 5, 888)), (b"RLWD", body)])),
         "BSWD does not follow its WDAT"),
        ("no base world, but a BSWD", level_stream(level_chunks(children=[wdat, (b"BSWD", body), (b"RLWD", body)])),
         "RLWD does not follow its WDAT and base world"),
        ("a chunk past the stream", level_stream(good)[:-1], "past the end"),
        ("a header that declares one byte more than follows", level_stream(good) + b"ERES" + word(1), "past the end"),
        ("a header that declares eight bytes more than follow", level_stream(good) + b"ERES" + word(8), "past the end"),
        ("an RLWD of exactly 4 MiB", level_stream(level_chunks(body=struct.pack("<H", 50) + bytes((4 << 20) - 2))), None),
        ("an RLWD of 4 MiB and 1 byte", level_stream(level_chunks(body=struct.pack("<H", 50) + bytes((4 << 20) - 1))), "unusable size"),
        ("a BSWD of 4 MiB and 1 byte", level_stream(level_chunks(children=[(b"WDAT", struct.pack("<ii", 10, 888)),
                                                                           (b"BSWD", struct.pack("<H", 50) + bytes((4 << 20) - 1)), (b"RLWD", body)])),
         "unusable size"),
    ]
    # fewer than a header's eight bytes left, at the end of the stream and inside WRLD
    for extra in range(1, 8):
        junk = b"abcdefg"[:extra]
        cases += [
            (f"{extra} bytes after the last chunk", level_stream(good) + junk, "cut chunk header"),
            (f"{extra} bytes after WDAT in WRLD", level_stream(put(wres, fixtures.chunk(b"WRLD", fixtures.chunk(*wdat) + junk))), "past its end"),
            (f"{extra} bytes after BSWD in WRLD", level_stream(put(wres, fixtures.chunk(b"WRLD", fixtures.chunk(b"WDAT", struct.pack("<ii", 10, 888))
                                                                                     + fixtures.chunk(b"BSWD", body) + junk))), "past its end"),
            (f"{extra} bytes after RLWD in WRLD", level_stream(put(wres, fixtures.chunk(b"WRLD", fixtures.chunk(*wdat) + fixtures.chunk(b"RLWD", body) + junk))),
             "chunks after its real world body"),
        ]
    # the chunk-count cap (2048) and the unpacked cap (32 MiB), at and past the limit
    for extra, words in ((2048 - len(good), None), (2049 - len(good), "more than 2048 chunks")):
        padded = good[:first_text] + [(b"TEXT", good[first_text][1])] * extra + good[first_text:]
        cases.append((f"{len(padded)} chunks", level_stream(padded), words))
    base = level_stream(good)
    for extra, words in ((0, None), (1, "32 MiB")):
        filler = (32 << 20) - len(base) - 8 + extra
        cases.append((f"{32 + extra / (1 << 20):.6f} MiB unpacked", level_stream(good[:-1] + [(b"ERES", bytes(filler)), good[-1]]), words))
    return cases


class StructureTable(unittest.TestCase):
    """The stager and the oracle agree on every stream, and the table can fail (each refusal names its rule)."""

    def test_the_stager_and_the_oracle_agree_on_every_level_archive(self) -> None:
        cases = structure_cases()
        self.assertGreater(len(cases), 80)
        refused = admitted = 0
        for label, stream, words in cases:
            with self.subTest(label):
                archive = packed(stream, 1)
                why, unpacked = stage.check_packed(archive, unpack=True)
                module = why or stage.check_level_archive(unpacked, 888)
                oracle_why, oracle_stream = LoaderRules.unpack(archive, keep=True)
                oracle = oracle_why or LoaderRules.walk(oracle_stream, 888)
                self.assertEqual(module is None, oracle is None, (module, oracle))
                if words is None:
                    self.assertIsNone(module, module)
                    admitted += 1
                else:
                    self.assertIsNotNone(module, "the stager admitted what the loader refuses")
                    self.assertIn(words, module)
                    refused += 1
        self.assertGreater(refused, 70)
        self.assertGreaterEqual(admitted, 9)

    def test_the_limits_are_the_loaders_literals(self) -> None:
        # not the module's constants: mods.cpp's kMaxFile, kMaxTotal, kMaxArchive, kMaxArchiveUnpacked, kMaxLevelChunks
        self.assertEqual((64 << 20, 1 << 30, 8 << 20, 32 << 20, 2048), (stage.MAX_FILE_BYTES, stage.MAX_TOTAL_BYTES, stage.MAX_ARCHIVE_BYTES,
                                                                         stage.MAX_ARCHIVE_UNPACKED_BYTES, stage.MAX_LEVEL_CHUNKS))
        self.assertEqual((850, 899), (stage.ARCHIVE_FIRST, stage.ARCHIVE_LAST))
        self.assertEqual((0x102927, 1 << 20, 0x500000, 4096), (stage.PACK_BUFFER, stage.PACK_BLOCK, stage.TEXTURE_SCRATCH, stage.MAX_TEXTURE_SIDE))
        self.assertEqual((344, 372, 316, 5084, 92), stage.AYAD_GUARDS)


class PathRuleTable(unittest.TestCase):
    """CheckPath: the stager and the oracle agree one character, one name and one length at a time."""

    def agree(self, path: str, admitted: bool) -> None:
        module, oracle = stage.path_problem(path), LoaderRules.path_problem(path)
        self.assertEqual(admitted, module is None, (path, module))
        self.assertEqual(admitted, oracle is None, (path, oracle))

    def test_every_character_from_0_to_255(self) -> None:
        for code in range(256):
            char = chr(code)
            with self.subTest(code=code):
                self.agree(f"data/a{char}b", 32 <= code < 127 and char not in '\\:*?"<>|')
        self.agree("data/a b", True)   # a space inside a name is fine (data/default physics.dat)

    def test_device_names_with_or_without_an_extension_or_trailing_spaces(self) -> None:
        devices = ["CON", "PRN", "AUX", "NUL", "CONIN$", "CONOUT$", *(f"{p}{d}" for p in ("COM", "LPT") for d in "0123456789")]
        for name in devices:
            for form in (name, name.lower(), name + ".txt", name.lower() + ".x.y", name + " .txt"):
                with self.subTest(form):
                    self.agree(f"data/{form}", False)
                    self.agree(f"data/{form}/x", False)
        for name in ("COM10", "COMA", "LPT", "CONSOLE", "CONIN", "NULL", "AUXILIARY", "PRNT", "xCON", "CON-1", "NUL_"):
            with self.subTest(name):
                self.agree(f"data/{name}", True)
                self.agree(f"data/{name}.txt", True)

    def test_lengths_and_depth_at_and_past_the_limit(self) -> None:
        self.agree("data/" + "a" * 128, True)
        self.agree("data/" + "a" * 129, False)
        self.agree("data/" + "/".join(["a"] * 11), True)    # 12 components with data
        self.agree("data/" + "/".join(["a"] * 12), False)   # 13
        for length in (239, 240, 241):
            path = "data/" + "a" * 60 + "/" + "a" * 60 + "/" + "a" * (length - 127)
            self.assertEqual(length, len(path))
            self.agree(path, length <= 240)

    def test_other_shapes(self) -> None:
        for path, admitted in (("data", True), ("DATA/x", True), ("Data/X/y.z", True), ("other/x", False), ("datax/x", False),
                               ("", False), ("/data/x", False), ("data//x", False), ("data/./x", False), ("data/../x", False),
                               ("data/x/", False), ("data/x.", False), ("data/x ", False), ("data/ x", False), ("data/.x", True),
                               ("data/x.y.z", True), ("data/x/..", False), ("data/x\\y", False)):
            with self.subTest(path):
                self.agree(path, admitted)


class PackedBlockTable(unittest.TestCase):
    """CheckPacked: what the game's block reader can read."""

    def blocks(self, *pieces: bytes, level: int = 1) -> bytes:
        out = b""
        for piece in pieces:
            z = zlib.compress(piece, level)
            out += struct.pack("<I", len(z)) + z
        return out

    def test_the_stager_and_the_oracle_agree_on_every_block_layout(self) -> None:
        mib = bytes(1 << 20)
        z = zlib.compress(b"abc")
        cases = [
            ("one short block", self.blocks(b"abc"), None),
            ("two full blocks and a short one", self.blocks(mib, mib, b"x"), None),
            ("a full block last", self.blocks(b"abc"[:0] + mib), None),
            ("an empty block last", self.blocks(mib, b""), None),
            ("an empty file", b"", "empty packed file"),
            ("a cut block header", self.blocks(b"abc") + b"\1\0", "cut block header"),
            ("a cut block", self.blocks(b"abc")[:-1], "cut block"),
            ("a zero-length block", struct.pack("<I", 0), "block buffer"),
            ("a block longer than the game's buffer", struct.pack("<I", 0x102928) + bytes(0x102928), "block buffer"),
            ("a short block before the last", self.blocks(b"abc", b"def"), "before the last block"),
            ("a block of 1 MiB and 1 byte", self.blocks(mib + b"x"), "more than 1 MiB"),
            ("a block that is not zlib", struct.pack("<I", 4) + b"abcd", "does not unpack"),
            ("a block with trailing bytes", struct.pack("<I", len(z) + 1) + z + b"x", "does not unpack"),
            ("a block cut inside its zlib stream", struct.pack("<I", len(z) - 2) + z[:-2], "does not unpack"),
        ]
        for label, data, words in cases:
            with self.subTest(label):
                module, _ = stage.check_packed(data)
                oracle, _ = LoaderRules.unpack(data)
                self.assertEqual(module is None, oracle is None, (module, oracle))
                if words is None:
                    self.assertIsNone(module)
                else:
                    self.assertIn(words, module)

    def test_a_texture_must_be_a_dds_the_game_can_load(self) -> None:
        def dds(width=4, height=4, size_word=124, magic=b"DDS ", pad=0):
            return magic + struct.pack("<II", size_word, 0x81007) + struct.pack("<II", height, width) + bytes(128 - 20) + bytes(pad)
        cases = [
            ("a 4x4 image", dds(), None),
            ("4096 by 4096", dds(4096, 4096), None),
            ("4097 wide", dds(4097, 4), "4096 texels"),
            ("4097 high", dds(4, 4097), "4096 texels"),
            ("zero wide", dds(0, 4), "4096 texels"),
            ("not DDS", dds(magic=b"XDS "), "not a DDS"),
            ("a header size other than 124", dds(size_word=100), "not a DDS"),
            ("shorter than a header", b"DDS " + bytes(60), "not a DDS"),
            ("just under 5 MiB", dds(pad=0x4FFFFF - 128), None),
            ("5 MiB", dds(pad=0x500000 - 128), "5 MiB"),
        ]
        for label, image, words in cases:
            with self.subTest(label):
                data = packed(image, 1)
                module, _ = stage.check_packed(data, texture=True)
                oracle, _ = LoaderRules.unpack(data, texture=True)
                self.assertEqual(module is None, oracle is None, (module, oracle))
                if words is None:
                    self.assertIsNone(module)
                else:
                    self.assertIn(words, module)
        # and a packed file that is not a texture is not held to any of that
        self.assertIsNone(stage.check_packed(self.blocks(b"not an image"))[0])


# ---- staging files other than worlds ----------------------------------------------------------------------------------------
class FilesBase(Base):
    """A game folder with a level archive and a physics file (spelled with capitals, as a Windows install may be)."""

    def setUp(self) -> None:
        super().setUp()
        self.physics_path = self.game / "Data" / "Default Physics.dat"
        (self.game / "data").rename(self.game / "Data")
        self.resources = self.game / "Data" / "resources"
        self.archive_path = self.resources / "200_res_PC.aya"
        self.physics_path.write_bytes(b"\x12\x00physics")
        self.good = level_archive(888)
        self.files = {"data/resources/888_res_PC.aya": self.good, "data/default physics.dat": b"\x12\x00edited physics"}

    def stage_files(self, files=None, mod_id: str = "duel", **options):
        options.setdefault("name", "Duel")
        return stage.stage_mod(self.out, self.game, mod_id, None, files=self.files if files is None else files, **options)

    def assert_refused(self, files, words: str, **options) -> None:
        with self.assertRaises(stage.ModStageError) as caught:
            self.stage_files(files, **options)
        self.assertIn(words, str(caught.exception))
        self.assertFalse(self.out.exists(), "a refused stage must not create the destination")
        self.assertEqual(["Data"], sorted(p.name for p in self.game.iterdir()))


class StageFilesTests(FilesBase):
    def test_the_signature_is_the_one_callers_are_told(self) -> None:
        params = inspect.signature(stage.stage_mod).parameters
        self.assertEqual(["parent", "game", "mod_id", "worlds", "name", "version", "author", "description", "ce_min", "ce_max", "files"],
                         list(params))
        kinds = {name: p.kind for name, p in params.items()}
        self.assertEqual({"parent", "game", "mod_id", "worlds"}, {n for n, k in kinds.items() if k is inspect.Parameter.POSITIONAL_OR_KEYWORD})
        self.assertEqual({"name", "version", "author", "description", "ce_min", "ce_max", "files"},
                         {n for n, k in kinds.items() if k is inspect.Parameter.KEYWORD_ONLY})
        self.assertEqual({"worlds": None, "version": "1", "author": "", "description": "", "ce_min": None, "ce_max": None, "files": None},
                         {n: params[n].default for n in ("worlds", "version", "author", "description", "ce_min", "ce_max", "files")})
        self.assertIs(params["name"].default, inspect.Parameter.empty)

    def test_an_added_archive_and_a_replacement_stage_as_the_loader_admits(self) -> None:
        summary = self.stage_files(version="2", author="tests", description="Adds 888.", ce_min="0.1.14")
        mod = self.out / "duel"
        self.assertEqual(["data", "mod.json"], sorted(p.name for p in mod.iterdir()))
        self.assertEqual(self.good, (mod / "data/resources/888_res_PC.aya").read_bytes())
        self.assertEqual(b"\x12\x00edited physics", (mod / "data/default physics.dat").read_bytes())
        manifest = json.loads((mod / "mod.json").read_text())
        self.assertEqual({"schema": 1, "id": "duel", "name": "Duel", "version": "2", "author": "tests", "description": "Adds 888.",
                          "ce_min": "0.1.14",
                          "files": [{"path": "data/default physics.dat", "size": len(self.files["data/default physics.dat"]), "sha256": hashlib.sha256(self.files["data/default physics.dat"]).hexdigest()},
                                    {"path": "data/resources/888_res_PC.aya", "size": len(self.good), "sha256": hashlib.sha256(self.good).hexdigest()}]},
                         manifest)
        self.assertEqual([entry["path"] for entry in manifest["files"]], [entry["path"] for entry in summary["files"]])
        self.assertEqual(hashlib.sha256((mod / "mod.json").read_bytes()).hexdigest(), summary["manifestSha256"])
        self.assertEqual([], LoaderRules.problems(mod, self.game))
        for path in mod.rglob("*"):
            self.assertFalse(path.is_symlink())
            if path.is_file():
                self.assertEqual(1, path.stat().st_nlink)
        self.assertEqual(b"\x12\x00physics", self.physics_path.read_bytes(), "the game's own file is not touched")
        self.assertEqual(["200_res_PC.aya"], sorted(p.name for p in self.resources.iterdir()))

    def test_without_files_the_world_only_stager_is_unchanged(self) -> None:
        by_worlds = stage.stage_mod(self.out, self.game, "same", {200: self.edited_body}, name="n", ce_min="0.1.11")
        by_files = stage.stage_mod(self.root / "other", self.game, "same", None, name="n", ce_min="0.1.11",
                                   files={"data/worlds/world200.wrd": self.edited_body})
        self.assertEqual(by_worlds["manifestSha256"], by_files["manifestSha256"])
        self.assertEqual(by_worlds["files"], by_files["files"])
        for call in (lambda: stage.stage_mod(self.root / "n1", self.game, "a", name="n"),
                     lambda: stage.stage_mod(self.root / "n2", self.game, "a", {}, name="n"),
                     lambda: stage.stage_mod(self.root / "n3", self.game, "a", None, name="n", files={}),
                     lambda: stage.stage_mod(self.root / "n4", self.game, "a", {}, name="n", files={})):
            with self.assertRaisesRegex(stage.ModStageError, "at least one file"):
                call()
        # a non-world file passed without files= is still refused by the world-only manifest, with its message
        with self.assertRaisesRegex(stage.ModStageError, "world files only"):
            stage.build_manifest("a", "n", "1", {"data/default physics.dat": b"x"})

    def test_worlds_and_files_may_be_given_together_but_not_the_same_world_twice(self) -> None:
        stage.stage_mod(self.out, self.game, "both", {200: self.edited_body}, name="n", files=self.files)
        mod = self.out / "both"
        self.assertEqual(["data/default physics.dat", "data/resources/888_res_PC.aya", "data/worlds/world200.wrd"],
                         [entry["path"] for entry in json.loads((mod / "mod.json").read_text())["files"]])
        self.assertEqual([], LoaderRules.problems(mod, self.game))
        with self.assertRaisesRegex(stage.ModStageError, "both as a world and as a file"):
            stage.stage_mod(self.root / "twice", self.game, "twice", {200: self.edited_body}, name="n",
                            files={"Data/Worlds/World200.WRD": self.edited_body})
        self.assertFalse((self.root / "twice").exists())

    def test_the_loader_decides_the_kind_of_a_file_as_the_stager_does(self) -> None:
        for level, admitted in ((849, False), (850, True), (888, True), (899, True), (900, False), (0, False), (999, False)):
            with self.subTest(level=level):
                files = {f"data/resources/{level:03d}_res_PC.aya": level_archive(level)}
                out = self.root / f"level{level}"
                if admitted:
                    stage.stage_mod(out, self.game, "a", None, name="n", files=files)
                    self.assertEqual([], LoaderRules.problems(out / "a", self.game))
                else:
                    with self.assertRaisesRegex(stage.ModStageError, "the game has no such file"):
                        stage.stage_mod(out, self.game, "a", None, name="n", files=files)
                    self.assertFalse(out.exists())

    def test_an_archive_the_game_has_is_a_replacement_and_its_structure_is_not_walked(self) -> None:
        # level 200 is outside 850..899 and the game has its archive: any packed file is a replacement of it
        junk = packed(b"this is not a level archive")
        stage.stage_mod(self.out, self.game, "swap", None, name="n", files={"data/resources/200_res_PC.aya": junk})
        self.assertEqual([], LoaderRules.problems(self.out / "swap", self.game))
        # the same for a level in 850..899 that the game already has an archive for
        (self.resources / "888_res_PC.aya").write_bytes(self.good)
        stage.stage_mod(self.root / "swap2", self.game, "swap2", None, name="n", files={"data/resources/888_res_PC.aya": junk})
        self.assertEqual([], LoaderRules.problems(self.root / "swap2" / "swap2", self.game))
        # but a replacement is still held to the block reader's rules
        with self.assertRaisesRegex(stage.ModStageError, "does not unpack"):
            stage.stage_mod(self.root / "bad", self.game, "bad", None, name="n", files={"data/resources/200_res_PC.aya": NOT_ZLIB})
        self.assertFalse((self.root / "bad").exists())

    def test_case_does_not_change_the_kind_of_a_file(self) -> None:
        stage.stage_mod(self.out, self.game, "caps", None, name="n",
                        files={"DATA/RESOURCES/888_RES_PC.AYA": self.good, "Data/DEFAULT PHYSICS.DAT": b"edited"})
        mod = self.out / "caps"
        self.assertEqual([], LoaderRules.problems(mod, self.game))
        self.assertTrue((mod / "DATA/RESOURCES/888_RES_PC.AYA").is_file())
        # two spellings of one path are one path whichever sorts first: capitals sort before lower case, so the pair with a
        # lower-case member and the pair of two mixed spellings are different cases
        for first, second in (("data/default physics.dat", "Data/Default Physics.dat"),
                              ("DATA/DEFAULT PHYSICS.DAT", "Data/Default Physics.dat"),
                              ("Data/Default Physics.dat", "data/DEFAULT physics.dat")):
            with self.subTest(first=first, second=second):
                with self.assertRaisesRegex(stage.ModStageError, "listed twice"):
                    stage.stage_mod(self.root / "dup", self.game, "dup", None, name="n", files={first: b"a", second: b"b"})
                self.assertFalse((self.root / "dup").exists())

    def test_what_the_loader_refuses_is_refused_and_nothing_is_written(self) -> None:
        big_archive = level_stream(level_chunks()[:-1] + [(b"ERES", os.urandom(8 << 20)), level_chunks()[-1]])
        cases = [
            ("a file the game lacks", {"data/other.bin": b"x"}, "the game has no such file"),
            ("a file outside data", {"other/default physics.dat": b"x"}, "outside data/"),
            ("a dotdot path", {"data/../x": b"x"}, "'..'"),
            ("a backslash", {"data\\default physics.dat": b"x"}, "not allowed in a path"),
            ("a colon", {"data/a:b": b"x"}, "not allowed in a path"),
            ("a device name", {"data/CON.txt": b"x"}, "Windows device name"),
            ("a trailing dot", {"data/default physics.dat.": b"x"}, "ends with a space or a dot"),
            ("a leading space", {"data/ default physics.dat": b"x"}, "starts with a space"),
            ("a non-ASCII name", {"data/caf\u00e9": b"x"}, "not allowed in a path"),
            ("an empty component", {"data//a": b"x"}, "empty path component"),
            ("13 components", {"data/" + "/".join(["a"] * 12): b"x"}, "too many path components"),
            ("a path of 241 characters", {"data/" + "a" * 236: b"x"}, "over-long path"),
            ("an empty file", {"data/default physics.dat": b""}, "1 byte"),
            ("text for bytes", {"data/default physics.dat": "text"}, "1 byte"),
            ("a path that is not text", {7: b"x"}, "path is text"),
            ("an unpackable archive", {"data/resources/888_res_PC.aya": NOT_ZLIB}, "does not unpack"),
            ("a cut archive", {"data/resources/888_res_PC.aya": self.good[:-1]}, "cut block"),
            ("a packed non-archive", {"data/resources/888_res_PC.aya": packed(b"x" * 100)}, "level archive"),
            ("an archive of another level", {"data/resources/888_res_PC.aya": level_archive(889)}, "another level"),
            ("an archive over 8 MiB packed", {"data/resources/888_res_PC.aya": packed(big_archive)}, "larger than 8 MiB"),
            ("an archive over 32 MiB unpacked", {"data/resources/888_res_PC.aya": packed(level_stream(
                level_chunks()[:-1] + [(b"ERES", bytes(32 << 20)), level_chunks()[-1]]))}, "32 MiB"),
            ("a world over 4 MiB", {"data/worlds/world001.wrd": bytes((4 << 20) + 1)}, "world file larger than 4 MiB"),
            ("a file over 64 MiB", {"data/default physics.dat": bytes((64 << 20) + 1)}, "1 byte to"),
        ]
        for label, files, words in cases:
            with self.subTest(label):
                self.assert_refused(files, words)
        self.assert_refused({f"data/f{n}": b"x" for n in range(4097)}, "at most 4096 files")

    def test_the_limits_are_inclusive(self) -> None:
        game_has = lambda path: LoaderRules.game_has(self.game, path)
        build = lambda files: stage.build_files_manifest("a", "n", "1", files, game_has=game_has)
        build({"data/default physics.dat": bytes(64 << 20)})  # exactly 64 MiB of a file the game has
        with patch.object(stage, "MAX_TOTAL_BYTES", 100):
            build({"data/default physics.dat": bytes(100)})
            with self.assertRaisesRegex(stage.ModStageError, "1 GiB"):
                build({"data/default physics.dat": bytes(50), "data/worlds/world001.wrd": bytes(51)})
        eight_mib = level_stream(level_chunks()[:-1] + [(b"ERES", os.urandom(8 << 20)), level_chunks()[-1]])
        self.assertGreater(len(packed(eight_mib)), 8 << 20)
        small = level_stream(level_chunks()[:-1] + [(b"ERES", os.urandom((8 << 20) - 4096)), level_chunks()[-1]])
        self.assertLessEqual(len(packed(small)), 8 << 20)
        build({"data/resources/888_res_PC.aya": packed(small)})

    def test_a_replacement_texture_must_load(self) -> None:
        folder = self.resources / "dxtntextures"
        folder.mkdir()
        (folder / "skin.tga(0)A1R5G5B5.aya").write_bytes(b"x")
        image = fixtures.dds_dxt1_4x4()
        path = "data/resources/dxtntextures/skin.tga(0)A1R5G5B5.aya"
        stage.stage_mod(self.out, self.game, "skin", None, name="n", files={path: packed(image)})
        self.assertEqual([], LoaderRules.problems(self.out / "skin", self.game))
        for label, data, words in (("not an image", packed(b"x" * 200), "not a DDS"),
                                   ("too wide", packed(image[:16] + struct.pack("<I", 8192) + image[20:]), "4096 texels")):
            with self.subTest(label):
                with self.assertRaisesRegex(stage.ModStageError, words):
                    stage.stage_mod(self.root / label.replace(" ", "-"), self.game, "bad", None, name="n", files={path: data})

    def test_game_has_file_compares_each_component_without_case(self) -> None:
        for path, expected in (("data/default physics.dat", True), ("DATA/DEFAULT PHYSICS.DAT", True), ("data/resources/200_res_pc.aya", True),
                               ("data/resources/888_res_PC.aya", False), ("data/resources", False), ("data", False),
                               ("data/default physics.dat/x", False), ("", False), ("nothing/here", False)):
            with self.subTest(path=path):
                self.assertEqual(expected, stage.game_has_file(self.game, path))
                self.assertEqual(expected and bool(path), LoaderRules.game_has(self.game, path))
        self.assertFalse(stage.game_has_file(self.root / "missing", "data/a"))

    def test_files_are_published_in_sorted_order_and_the_manifest_last(self) -> None:
        order = []
        real = safe.SecuredOutputRoot.atomic_write_new_bytes

        def record(self_, path, payload):
            order.append(Path(path).relative_to(self.out / "duel").as_posix())
            return real(self_, path, payload)
        with patch.object(safe.SecuredOutputRoot, "atomic_write_new_bytes", record):
            self.stage_files()
        self.assertEqual(["data/default physics.dat", "data/resources/888_res_PC.aya", "mod.json"], order)

        def fail_on_manifest(self_, path, payload):
            if Path(path).name == "mod.json":
                raise OSError("disk full")
            return real(self_, path, payload)
        with patch.object(safe.SecuredOutputRoot, "atomic_write_new_bytes", fail_on_manifest):
            with self.assertRaisesRegex(stage.ModStageError, "could not write the mod"):
                self.stage_files(mod_id="half")
        self.assertFalse((self.out / "half" / "mod.json").exists())

    def test_a_destination_inside_the_game_folder_is_still_refused(self) -> None:
        for out in (self.game / "mods", self.game / "Data"):
            with self.subTest(out=out.name):
                with self.assertRaisesRegex(stage.ModStageError, "refused"):
                    stage.stage_mod(out, self.game, "duel", None, name="n", files=self.files)
        self.assertEqual(["200_res_PC.aya"], sorted(p.name for p in self.resources.iterdir()))

    def test_a_folder_that_holds_anything_is_never_written_into(self) -> None:
        (self.out / "duel").mkdir(parents=True)
        (self.out / "duel" / "keep.txt").write_text("mine")
        with self.assertRaisesRegex(stage.ModStageError, "already holds"):
            self.stage_files()
        self.assertEqual(["keep.txt"], sorted(p.name for p in (self.out / "duel").iterdir()))


class LoaderRulesFilesControls(FilesBase):
    """The oracle's new rules can fail: each control breaks a staged mod in one way and the oracle must say so."""

    def test_each_control_fails(self) -> None:
        self.stage_files()
        mod = self.out / "duel"
        self.assertEqual([], LoaderRules.problems(mod, self.game))

        def restage(label, mutate, expect):
            with self.subTest(label):
                copy = self.root / f"control-{label.replace(' ', '-')}" / "duel"
                shutil.copytree(mod, copy)
                mutate(copy)
                manifest = json.loads((copy / "mod.json").read_text())
                for entry in manifest["files"]:
                    data = (copy / entry["path"]).read_bytes()
                    entry["size"], entry["sha256"] = len(data), hashlib.sha256(data).hexdigest()
                (copy / "mod.json").write_text(json.dumps(manifest))
                found = LoaderRules.problems(copy, self.game)
                self.assertTrue(any(expect in line for line in found), (label, found))

        def archive_with(chunks):
            return lambda c: (c / "data/resources/888_res_PC.aya").write_bytes(packed(level_stream(chunks)))
        good = level_chunks()
        restage("a packed block that does not unpack", lambda c: (c / "data/resources/888_res_PC.aya").write_bytes(NOT_ZLIB), "does not unpack")
        restage("an unknown tag", archive_with(good[:3] + [(b"XXXX", b"")] + good[3:]), "tag a level archive does not hold")
        restage("a wrong guard", archive_with([good[0], good[1], (b"AYAD", struct.pack("<6I", 344, 372, 316, 5084, 93, 1))] + good[3:]), "AYAD")
        restage("another level", lambda c: (c / "data/resources/888_res_PC.aya").write_bytes(level_archive(889)), "another level")
        restage("no WRES", archive_with(good[:-1]), "WRES")
        restage("a base world without its body", archive_with(level_chunks(children=[(b"WDAT", struct.pack("<ii", 5, 888)), (b"RLWD", WORLD_BYTES)])), "BSWD only with a base world")
        restage("a level the game could have", lambda c: (shutil.move(c / "data/resources/888_res_PC.aya", c / "data/resources/849_res_PC.aya"),
                                                          self.rewrite_path(c, "data/resources/888_res_PC.aya", "data/resources/849_res_PC.aya")), "no such file")
        restage("a device name", lambda c: (shutil.move(c / "data/default physics.dat", c / "data/CON.dat"),
                                           self.rewrite_path(c, "data/default physics.dat", "data/CON.dat")), "device name")

    @staticmethod
    def rewrite_path(mod: Path, old: str, new: str) -> None:
        manifest = json.loads((mod / "mod.json").read_text())
        for entry in manifest["files"]:
            if entry["path"] == old:
                entry["path"] = new
        (mod / "mod.json").write_text(json.dumps(manifest))


if __name__ == "__main__":
    unittest.main()
