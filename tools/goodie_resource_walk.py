#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Walk every Goodie resource (data/resources/goodie_N_res_PC.aya) with the layout in
reverse-engineering/asset-formats/goodie-resources.md and resolve what each Goodie shows.

Each archive must be the LVLR prefix and one GDIE chunk that ends exactly at the end of the stream. Its GDAT record
must carry the archive's own number and the type the game's number rule gives. An image Goodie names one texture,
and a model Goodie names its textures and its mesh. Every name must resolve to exactly one installed file by the
game's own path rule. Video and level Goodies carry no content; the report lists the file or level the game picks for
each from its number. GOODIE_CONTENT is a SHA-256 over one "number type item | item" line per archive, for comparison
with the companion's reader. The install is only read.

Run:  python ./tools/goodie_resource_walk.py --game GAME_FOLDER    (or set BEA_GAME to the game folder)
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import struct
import sys
import zlib
from pathlib import Path

IMAGE, MODEL, VIDEO, LEVEL = 0, 1, 2, 3
TYPE_NAMES = {IMAGE: "image", MODEL: "model", VIDEO: "video", LEVEL: "level"}
TEXTURE_RECORD = 344
FORMATS = ("UNKNOWN", "A1R5G5B5", "A4R4G4B4", "X8R8G8B8", "A8R8G8B8", "R5G6B5", "DXT1", "DXT2", "DXT4", "V8U8", "Q8W8V8U8")
MESH_REFERENCE = 309


class GoodieError(ValueError):
    pass


def goodie_type(number: int) -> int:
    """The type the PC resource writer gives a Goodie number (pinned by every installed archive)."""
    if number <= 7 or number in (12, 13, 24, 33, 34, 35):
        return IMAGE
    if number <= 57:
        return MODEL
    if number <= 65:
        return IMAGE
    if number <= 70:
        return LEVEL
    if number <= 74:
        return IMAGE
    if number in (75, 77) or number > 200:
        return VIDEO
    if number == 76:
        return MODEL
    return IMAGE


def video_file(number: int) -> str | None:
    """The video a video Goodie plays, as a path under data/video without the .vid extension."""
    if 201 <= number <= 231:
        return f"cutscenes/{number - 200:02d}"
    if number == 232:
        return "cutscenes/33"
    return {75: "GILL_M_on_a_fork", 77: "UsTheMovie"}.get(number)


def level_number(number: int) -> int | None:
    return {66: 901, 67: 902, 68: 903, 69: 904, 70: 905}.get(number)


def inflate_aya(data: bytes) -> bytes:
    out, position = bytearray(), 0
    while position < len(data):
        (length,) = struct.unpack_from("<I", data, position)
        member = data[position + 4:position + 4 + length]
        if length == 0 or len(member) != length:
            raise GoodieError("bad AYA member length")
        out += zlib.decompress(member)
        position += 4 + length
    return bytes(out)


class Chunks:
    """Reads nested chunks (four-character tag, u32 size, payload) and checks that each closes exactly."""

    def __init__(self, data: bytes, start: int = 0, end: int | None = None):
        self.data, self.position, self.end = data, start, len(data) if end is None else end

    def take(self, tag: bytes) -> "Chunks":
        if self.position + 8 > self.end:
            raise GoodieError(f"expected {tag.decode()} at {self.position}, found the end")
        found = self.data[self.position:self.position + 4]
        (size,) = struct.unpack_from("<I", self.data, self.position + 4)
        if found != tag:
            raise GoodieError(f"expected {tag.decode()} at {self.position}, found {found!r}")
        start = self.position + 8
        if start + size > self.end:
            raise GoodieError(f"{tag.decode()} at {self.position} runs past its parent")
        self.position = start + size
        return Chunks(self.data, start, start + size)

    def read(self, count: int) -> bytes:
        if self.position + count > self.end:
            raise GoodieError(f"a field at {self.position} runs past its chunk")
        value = self.data[self.position:self.position + count]
        self.position += count
        return value

    def closed(self, what: str) -> None:
        if self.position != self.end:
            raise GoodieError(f"{what} has {self.end - self.position} unread bytes")


def texture_reference(chunks: Chunks) -> dict:
    """A DXTX chunk: the texture record, then one TFRM (mip level count) per frame."""
    dxtx = chunks.take(b"DXTX")
    record = dxtx.take(b"CTEX")
    raw = record.read(TEXTURE_RECORD)
    record.closed("CTEX")
    name = raw[8:136].split(b"\0", 1)[0].decode("latin-1")
    (width,) = struct.unpack_from("<i", raw, 172)
    (height,) = struct.unpack_from("<h", raw, 176)
    (frames,) = struct.unpack_from("<i", raw, 312)
    (texture_format,) = struct.unpack_from("<i", raw, 324)
    compressible = raw[340] != 0
    if not 1 <= frames <= 16:
        raise GoodieError(f"texture {name!r} has {frames} frames")
    levels = []
    for _ in range(frames):
        frame = dxtx.take(b"TFRM")
        levels.append(struct.unpack("<i", frame.read(4))[0])
        frame.closed("TFRM")
    dxtx.closed("DXTX")
    if not 0 <= texture_format < len(FORMATS):
        raise GoodieError(f"texture {name!r} has format {texture_format}")
    return {"name": name, "width": width, "height": height, "frames": frames, "format": FORMATS[texture_format],
            "compressible": compressible, "levels": levels}


def texture_candidates(texture: dict, frame: int = 0) -> list[str]:
    """The game's file names for one frame, in the order it tries them with DXTn textures enabled."""
    name = texture["name"].replace("\\", "%")

    def cut(prefix: str, body: str) -> str:
        # The whole path may be at most the prefix plus 65 characters; a longer one keeps 61 and gets ".aya".
        path = body + ".aya"
        return prefix + (body[:61] + ".aya" if len(path) > 65 else path)

    stem = f"{name}({frame}){texture['format']}"
    dxtn = cut("dxtntextures/", stem)
    plain = cut("textures/", stem if texture["compressible"] else "mustbe_" + stem)
    return [dxtn] if texture["compressible"] else [plain]


def read_goodie(data: bytes) -> dict:
    stream = Chunks(data)
    for tag in (b"LVLR", b"TARG", b"AYAD"):
        stream.take(tag)
    gdie = stream.take(b"GDIE")
    stream.closed("the stream after GDIE")
    gdat = gdie.take(b"GDAT")
    gdie.closed("GDIE")
    number, kind = struct.unpack("<2i", gdat.read(8))
    goodie = {"number": number, "type": kind, "textures": [], "mesh": None}
    if kind == IMAGE:
        goodie["textures"].append(texture_reference(gdat))
    elif kind == MODEL:
        mdat = gdat.take(b"MDAT")
        (count,) = struct.unpack("<i", mdat.read(4))
        mdat.closed("MDAT")
        for _ in range(count):
            txtr = gdat.take(b"TXTR")
            goodie["textures"].append(texture_reference(txtr))
            txtr.closed("TXTR")
        mesh = gdat.take(b"MESH")
        pmsh = mesh.take(b"PMSH")
        mesh.closed("MESH")
        pms2 = pmsh.take(b"PMS2")
        pmsh.closed("PMSH")
        raw = pms2.read(MESH_REFERENCE)
        pms2.closed("PMS2")
        name = raw[:300].split(b"\0", 1)[0].decode("latin-1")
        runtime_id, optional = struct.unpack_from("<2i", raw, 300)
        goodie["mesh"] = {"name": name, "runtime_id": runtime_id, "optional": optional, "keep_buckets": raw[308]}
    elif kind not in (VIDEO, LEVEL):
        raise GoodieError(f"unknown Goodie type {kind}")
    gdat.closed("GDAT")
    return goodie


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--game", type=Path, default=os.environ.get("BEA_GAME"), help="the game folder, only read (default $BEA_GAME)")
    parser.add_argument("--list", action="store_true", help="print one line per Goodie")
    args = parser.parse_args(argv)
    if args.game is None:
        parser.error("name the game folder with --game or BEA_GAME")
    resources = Path(args.game) / "data" / "resources"
    files = sorted(resources.glob("goodie_*_res_PC.aya"), key=lambda p: int(re.search(r"goodie_(\d+)_", p.name).group(1)))
    if not files:
        print(f"no Goodie resources under {args.game}", file=sys.stderr)
        return 2
    shelf = {str(p.relative_to(resources)).lower(): p for folder in ("dxtntextures", "textures", "meshes")
             for p in (resources / folder).glob("*.aya")}
    videos = {str(p.relative_to(Path(args.game) / "data" / "video")).lower()[:-4] for p in (Path(args.game) / "data" / "video").rglob("*.vid")}
    digest, content, failures, tally = hashlib.sha256(), hashlib.sha256(), [], {}
    references = set()
    for path in files:
        raw = path.read_bytes()
        digest.update(f"{path.name} {hashlib.sha256(raw).hexdigest()}\n".encode())
        expected = int(re.search(r"goodie_(\d+)_", path.name).group(1))
        try:
            goodie = read_goodie(inflate_aya(raw))
        except (GoodieError, zlib.error, struct.error) as error:
            failures.append(f"{path.name}: {error}")
            continue
        number, kind = goodie["number"], goodie["type"]
        if number != expected:
            failures.append(f"{path.name}: carries number {number}")
        if kind != goodie_type(number):
            failures.append(f"{path.name}: type {kind}, the number rule gives {goodie_type(number)}")
        tally[TYPE_NAMES.get(kind, kind)] = tally.get(TYPE_NAMES.get(kind, kind), 0) + 1
        shown = []
        for texture in goodie["textures"]:
            for frame in range(texture["frames"]):
                found = [c for c in texture_candidates(texture, frame) if c.lower() in shelf]
                if len(found) != 1:
                    failures.append(f"{path.name}: texture {texture['name']!r} frame {frame} resolves to {found}")
                else:
                    references.add(found[0].lower())
                    shown.append(found[0])
        if goodie["mesh"]:
            mesh = f"meshes/m_{goodie['mesh']['name']}.aya"
            if mesh.lower() not in shelf:
                failures.append(f"{path.name}: mesh {mesh} is not installed")
            references.add(mesh.lower())
            shown.append(mesh)
        if kind == VIDEO:
            video = video_file(number)
            if video is None or video.lower() not in videos:
                failures.append(f"{path.name}: video {video} is not installed")
            shown.append(f"video/{video}.vid")
        if kind == LEVEL:
            shown.append(f"level {level_number(number)}")
        content.update(f"{number} {kind} {' | '.join(shown)}\n".encode())
        if args.list:
            print(f"GOODIE {number:3d} {TYPE_NAMES.get(kind, kind):5s} " + " | ".join(shown))
    counts = ", ".join(f"{name} {count}" for name, count in sorted(tally.items()))
    print(f"GOODIE_WALK: {len(files) - len(failures)} of {len(files)} archives clean; {counts}; "
          f"{len(references)} distinct installed files referenced; manifest {digest.hexdigest()}")
    print(f"GOODIE_CONTENT {content.hexdigest()}")
    for failure in failures[:40]:
        print("FAIL " + failure)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
