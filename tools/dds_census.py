#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Census of the installed textures (data/resources/dxtntextures and data/resources/textures): every DDS header, mip
chain and pixel format, checked against the stored bytes.

For each .aya texture the envelope is inflated (reverse-engineering/asset-formats/aya-container.md) and the legacy DDS
header read. The tool checks that the payload is exactly the sum of the declared mip levels for the declared format,
and that the header's own size, pitch, mip-count and caps fields agree with that chain. It then classifies how alpha is
used at the top level: DXT1 blocks that use the transparent colour, DXT2 explicit alpha, the one-bit alpha of
A1R5G5B5, and 8-bit alpha. With --mips it also decodes every stored mip level and compares each with a 2x2 box
reduction of the level above it: it reports the worst mean RGB difference (0-255) by level size, and, for textures
whose alpha is only on or off, how a lower level's alpha follows the number of opaque parent pixels. The install is
only read.

Run:  python ./tools/dds_census.py --game GAME_FOLDER [--mips]    (or set BEA_GAME to the game folder)
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import os
import struct
import sys
import zlib
from pathlib import Path

DDSD_PITCH, DDSD_MIPMAPCOUNT, DDSD_LINEARSIZE = 0x8, 0x20000, 0x80000
DDSCAPS_COMPLEX, DDSCAPS_TEXTURE, DDSCAPS_MIPMAP = 0x8, 0x1000, 0x400000
SHELVES = ("dxtntextures", "textures")
SIZE_BANDS = ((64, ">=64"), (16, "16-32"), (4, "4-8"), (1, "1-2"))


class TextureError(ValueError):
    pass


def inflate_aya(data: bytes) -> bytes:
    out, position = bytearray(), 0
    while position < len(data):
        (length,) = struct.unpack_from("<I", data, position)
        member = data[position + 4:position + 4 + length]
        if length == 0 or len(member) != length:
            raise TextureError("bad AYA member length")
        out += zlib.decompress(member)
        position += 4 + length
    return bytes(out)


def header(dds: bytes) -> dict:
    if len(dds) < 128 or dds[:4] != b"DDS ":
        raise TextureError("not a DDS file")
    size, flags, height, width, pitch, depth, mips = struct.unpack_from("<7I", dds, 4)
    pf_size, pf_flags = struct.unpack_from("<2I", dds, 76)
    fourcc = dds[84:88].decode("latin-1")
    bits, rmask, gmask, bmask, amask = struct.unpack_from("<5I", dds, 88)
    caps1, caps2 = struct.unpack_from("<2I", dds, 108)
    if size != 124 or pf_size != 32:
        raise TextureError("unexpected header or pixel-format size")
    if pf_flags & 0x4:
        layout = fourcc
    elif pf_flags & 0x40 and (bits, rmask, gmask, bmask, amask) == (16, 0x7C00, 0x3E0, 0x1F, 0x8000):
        layout = "A1R5G5B5"
    elif pf_flags & 0x40 and (bits, rmask, gmask, bmask, amask) == (32, 0xFF0000, 0xFF00, 0xFF, 0xFF000000):
        layout = "A8R8G8B8"
    else:
        layout = f"RGB{bits}:{rmask:x}/{gmask:x}/{bmask:x}/{amask:x}"
    return {"flags": flags, "width": width, "height": height, "pitch": pitch, "depth": depth, "mips": mips,
            "layout": layout, "caps1": caps1, "caps2": caps2}


def level_bytes(layout: str, width: int, height: int) -> int:
    if layout == "DXT1":
        return max(1, (width + 3) // 4) * max(1, (height + 3) // 4) * 8
    if layout in ("DXT2", "DXT3", "DXT4", "DXT5"):
        return max(1, (width + 3) // 4) * max(1, (height + 3) // 4) * 16
    if layout == "A1R5G5B5":
        return width * height * 2
    if layout == "A8R8G8B8":
        return width * height * 4
    raise TextureError(f"unsupported pixel format {layout}")


def chain(h: dict) -> list[tuple[int, int, int]]:
    """The mip levels the header declares: (width, height, bytes), largest first."""
    levels = max(1, h["mips"]) if h["flags"] & DDSD_MIPMAPCOUNT else 1
    out, w, hh = [], h["width"], h["height"]
    for _ in range(levels):
        out.append((w, hh, level_bytes(h["layout"], w, hh)))
        w, hh = max(1, w // 2), max(1, hh // 2)
    return out


def decode_level(layout: str, data: bytes, width: int, height: int):
    """One stored level as an RGBA uint8 array of shape (height, width, 4), values as stored (DXT2 stays premultiplied)."""
    import numpy as np

    if layout == "A8R8G8B8":
        bgra = np.frombuffer(data, np.uint8).reshape(height, width, 4)
        return bgra[..., [2, 1, 0, 3]].copy()
    if layout == "A1R5G5B5":
        v = np.frombuffer(data, "<u2").reshape(height, width).astype(np.uint16)
        r, g, b = (v >> 10) & 31, (v >> 5) & 31, v & 31
        five = lambda c: ((c << 3) | (c >> 2)).astype(np.uint8)
        return np.stack([five(r), five(g), five(b), np.where(v >> 15, 255, 0).astype(np.uint8)], -1)
    block_bytes = 8 if layout == "DXT1" else 16
    bw, bh = max(1, (width + 3) // 4), max(1, (height + 3) // 4)
    blocks = np.frombuffer(data, np.uint8).reshape(bh, bw, block_bytes)
    colour = blocks[..., block_bytes - 8:]
    c0 = colour[..., 0].astype(np.uint16) | (colour[..., 1].astype(np.uint16) << 8)
    c1 = colour[..., 2].astype(np.uint16) | (colour[..., 3].astype(np.uint16) << 8)
    selectors = (colour[..., 4].astype(np.uint32) | (colour[..., 5].astype(np.uint32) << 8) |
                 (colour[..., 6].astype(np.uint32) << 16) | (colour[..., 7].astype(np.uint32) << 24))

    def rgb(c):
        r, g, b = (c >> 11) & 31, (c >> 5) & 63, c & 31
        return np.stack([(r << 3) | (r >> 2), (g << 2) | (g >> 4), (b << 3) | (b >> 2)], -1).astype(np.int32)

    p0, p1 = rgb(c0), rgb(c1)
    four = (c0 > c1)[..., None] if layout == "DXT1" else np.ones(c0.shape + (1,), bool)
    p2 = np.where(four, (2 * p0 + p1) // 3, (p0 + p1) // 2)
    p3 = np.where(four, (p0 + 2 * p1) // 3, 0)
    palette = np.stack([p0, p1, p2, p3], 2)                                   # (bh, bw, 4, 3)
    alpha_palette = np.full(c0.shape + (4,), 255, np.int32)
    if layout == "DXT1":
        alpha_palette[..., 3] = np.where(c0 > c1, 255, 0)
    index = np.stack([(selectors >> (2 * p)) & 3 for p in range(16)], -1).astype(np.int64)   # (bh, bw, 16)
    rgb_out = np.take_along_axis(palette, index[..., None].repeat(3, -1), 2)  # (bh, bw, 16, 3)
    alpha = np.take_along_axis(alpha_palette, index, 2)
    if layout != "DXT1":
        bits = np.zeros(c0.shape, np.uint64)
        for i in range(8):
            bits |= blocks[..., i].astype(np.uint64) << np.uint64(8 * i)
        alpha = np.stack([((bits >> np.uint64(4 * p)) & np.uint64(15)).astype(np.int32) * 17 for p in range(16)], -1)
    pixels = np.concatenate([rgb_out, alpha[..., None]], -1).reshape(bh, bw, 4, 4, 4)
    image = pixels.transpose(0, 2, 1, 3, 4).reshape(bh * 4, bw * 4, 4)
    return image[:height, :width].astype(np.uint8)


def reduce_2x2(image):
    """A 2x2 box reduction (a 1-pixel axis is averaged along the other axis only)."""
    import numpy as np

    h, w = image.shape[:2]
    fy, fx = (2 if h > 1 else 1), (2 if w > 1 else 1)
    return image.astype(np.float64).reshape(h // fy, fy, w // fx, fx, 4).mean((1, 3))


def decode_chain(dds: bytes, h: dict) -> list:
    """Every stored level, largest first, decoded to RGBA."""
    levels, offset = [], 128
    for width, height, size in chain(h):
        levels.append(decode_level(h["layout"], dds[offset:offset + size], width, height))
        offset += size
    return levels


def mip_errors(levels: list) -> list[tuple[float, float]]:
    """For each level below the top: (mean absolute RGB difference, mean absolute alpha difference) from the reduced level above."""
    import numpy as np

    errors = []
    for above, level in zip(levels, levels[1:]):
        diff = np.abs(reduce_2x2(above) - level.astype(np.float64))
        errors.append((float(diff[..., :3].mean()), float(diff[..., 3].mean())))
    return errors


def alpha_rule(levels: list, counts: list[list[int]]) -> bool:
    """For a chain whose top alpha is only 0 or 255: adds, per number of opaque parents (0-4) in the level above, how many
    stored pixels are opaque and how many there are. Returns False (adding nothing) for any other alpha."""
    import numpy as np

    if not set(np.unique(levels[0][..., 3]).tolist()) <= {0, 255}:
        return False
    for above, level in zip(levels, levels[1:]):
        h, w = above.shape[:2]
        if h < 2 or w < 2:
            continue
        opaque_parents = (above[..., 3].reshape(h // 2, 2, w // 2, 2) == 255).sum((1, 3))
        for n in range(5):
            chosen = opaque_parents == n
            counts[n][0] += int((level[..., 3][chosen] == 255).sum())
            counts[n][1] += int(chosen.sum())
    return True


def alpha_use(layout: str, top: bytes, width: int, height: int) -> str:
    """How the top level uses alpha: none (all opaque), binary (0 or full only) or graded."""
    if layout == "DXT1":
        for block in range(len(top) // 8):
            c0, c1, selectors = struct.unpack_from("<HHI", top, block * 8)
            if c0 <= c1 and any(((selectors >> (2 * p)) & 3) == 3 for p in range(16)):
                return "binary"
        return "none"
    if layout in ("DXT2", "DXT3"):
        values = set()
        for block in range(len(top) // 16):
            bits = int.from_bytes(top[block * 16:block * 16 + 8], "little")
            values.update((bits >> (4 * p)) & 0xF for p in range(16))
        return "none" if values == {15} else "binary" if values <= {0, 15} else "graded"
    if layout == "A1R5G5B5":
        tops = {top[2 * i + 1] >> 7 for i in range(width * height)}
        return "none" if tops == {1} else "binary"
    if layout == "A8R8G8B8":
        values = set(top[3::4])
        return "none" if values == {255} else "binary" if values <= {0, 255} else "graded"
    return "unknown"


def census(path: Path, mips: bool = False) -> dict:
    dds = inflate_aya(path.read_bytes())
    h = header(dds)
    levels = chain(h)
    expected = sum(size for _, _, size in levels)
    payload = len(dds) - 128
    problems = []
    if payload != expected:
        problems.append(f"payload {payload} bytes, mip chain {expected}")
    top = levels[0][2]
    if h["flags"] & DDSD_LINEARSIZE and h["pitch"] != top:
        problems.append(f"linear size {h['pitch']} differs from the top level's {top}")
    if h["flags"] & DDSD_PITCH and h["pitch"] != top // max(1, h["height"]):
        problems.append(f"pitch {h['pitch']} differs from the row size {top // max(1, h['height'])}")
    mipmapped = len(levels) > 1
    if mipmapped != bool(h["caps1"] & DDSCAPS_MIPMAP):
        problems.append("the mipmap cap disagrees with the mip count")
    if h["caps2"]:
        problems.append(f"caps2 {h['caps2']:#x} (cube map or volume)")
    full_chain = (max(h["width"], h["height"]).bit_length())
    return {"layout": h["layout"], "size": (h["width"], h["height"]), "levels": len(levels),
            "full_chain": len(levels) == full_chain, "power_of_two": all(v & (v - 1) == 0 for v in (h["width"], h["height"])),
            "alpha": alpha_use(h["layout"], dds[128:128 + top], h["width"], h["height"]), "problems": problems,
            "levels_rgba": decode_chain(dds, h) if mips and not problems and len(levels) > 1 else []}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--game", type=Path, default=os.environ.get("BEA_GAME"), help="the game folder, only read (default $BEA_GAME)")
    parser.add_argument("--mips", action="store_true", help="decode every mip level and compare it with the level above")
    args = parser.parse_args(argv)
    if args.game is None:
        parser.error("name the game folder with --game or BEA_GAME")
    files = [p for shelf in SHELVES for p in sorted((Path(args.game) / "data/resources" / shelf).glob("*.aya"))]
    if not files:
        print(f"no textures under {args.game}", file=sys.stderr)
        return 2
    digest = hashlib.sha256()
    tally: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    failures, mip_rows, binary_alpha = [], [], 0
    worst_rgb = {label: 0.0 for _, label in SIZE_BANDS}
    rule = [[0, 0] for _ in range(5)]
    for path in files:
        raw = path.read_bytes()
        digest.update(f"{path.parent.name}/{path.name} {hashlib.sha256(raw).hexdigest()}\n".encode())
        try:
            row = census(path, args.mips)
        except (TextureError, zlib.error, struct.error) as error:
            failures.append(f"{path.name}: {error}")
            continue
        shelf = path.parent.name
        tally["format"][f"{shelf} {row['layout']}"] += 1
        tally["alpha"][f"{row['layout']} {row['alpha']}"] += 1
        tally["mips"][f"{row['levels']} level{'s' if row['levels'] != 1 else ''}" + (" (full chain)" if row["full_chain"] and row["levels"] > 1 else "")] += 1
        tally["shape"]["power-of-two" if row["power_of_two"] else "not power-of-two"] += 1
        tally["shape"]["square" if row["size"][0] == row["size"][1] else "not square"] += 1
        tally["size"][f"{row['size'][0]}x{row['size'][1]}"] += 1
        for problem in row["problems"]:
            failures.append(f"{path.name}: {problem}")
        if row["levels_rgba"]:
            errors = mip_errors(row["levels_rgba"])
            for (width, height), (rgb, alpha) in zip(((l.shape[1], l.shape[0]) for l in row["levels_rgba"][1:]), errors):
                band = next(label for limit, label in SIZE_BANDS if min(width, height) >= limit)
                worst_rgb[band] = max(worst_rgb[band], rgb)
            worst = max(errors, key=lambda e: e[0])
            mip_rows.append((worst[0], errors.index(worst) + 1, row["layout"], f"{path.parent.name}/{path.name}"))
            binary_alpha += alpha_rule(row["levels_rgba"], rule)
    print(f"DDS_CENSUS: {len(files)} textures; {len(failures)} problems; manifest {digest.hexdigest()}")
    for key in ("format", "alpha", "mips", "shape"):
        print(f"  {key}: " + ", ".join(f"{name} {count}" for name, count in sorted(tally[key].items())))
    print("  common sizes: " + ", ".join(f"{name} {count}" for name, count in tally["size"].most_common(8)))
    if args.mips:
        print(f"MIP_CHECK: {len(mip_rows)} mipmapped textures; worst mean RGB difference of a stored level from the 2x2 "
              "reduction of the level above, by the level's smaller side: " +
              ", ".join(f"{label} px {worst_rgb[label]:.2f}" for _, label in SIZE_BANDS))
        print(f"MIP_ALPHA: {binary_alpha} mipmapped textures with only on/off alpha; a lower-level pixel is opaque for n opaque "
              "parents: " + ", ".join(f"n={n} {opaque}/{total}" for n, (opaque, total) in enumerate(rule)))
        for rgb, level, layout, name in sorted(mip_rows, reverse=True)[:8]:
            print(f"  MIP {name} level {level} ({layout}): RGB {rgb:.2f}")
    for failure in failures[:40]:
        print("PROBLEM " + failure)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
