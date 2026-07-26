# SPDX-License-Identifier: GPL-3.0-or-later
"""Raw CMSH per-part track probe.

Decodes MESP part records from a retail `.msh.aya` without the static-preview
profile's acceptance rules, and reports the measured shape of every animation
track chunk (VHFM / HORI / HPOS / HFOV / CPOS / CORI / PBKT).

Analysis only. Reads its input read-only; writes nothing.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import struct
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "rebuild" / "tools"))
from cmsh_static_preview import inflate_aya  # noqa: E402


def chunks(data: memoryview, base: int = 0):
    pos = 0
    while pos + 8 <= len(data):
        tag = bytes(data[pos : pos + 4])
        length = struct.unpack_from("<I", data, pos + 4)[0]
        if pos + 8 + length > len(data):
            break
        yield tag, data[pos + 8 : pos + 8 + length], base + pos
        pos += 8 + length


def parse(data: bytes):
    assert data[:4] == b"CMSH", data[:4]
    part_count = struct.unpack_from("<I", data, 0x164)[0]
    body = memoryview(data)[380:]
    parts = []
    for tag, payload, off in chunks(body, 380):
        if tag != b"MESP":
            continue
        part = {"offset": off, "records": {}}
        for rtag, rpayload, roff in chunks(payload, off + 8):
            if rtag == b"CMSP":
                p = rpayload
                part["curOri"] = struct.unpack_from("<12f", p, 0x00)
                part["baseOri"] = struct.unpack_from("<12f", p, 0x30)
                part["offPos"] = struct.unpack_from("<4f", p, 0x60)
                part["basePos"] = struct.unpack_from("<4f", p, 0x70)
                num, ptype, nchild = struct.unpack_from("<III", p, 0x88)
                dvert, pvert, tris, aframes, vframes, hframes, bones = struct.unpack_from("<7I", p, 0xA8)
                part.update(
                    number=num, type=ptype, children=nchild, aFrames=aframes,
                    vFrames=vframes, hFrames=hframes, bones=bones,
                    name=bytes(p[0xDC:0xFC]).split(b"\0", 1)[0].decode("utf-8", "replace"),
                )
            else:
                part["records"][rtag.decode("ascii", "replace")] = (len(rpayload), bytes(rpayload), roff)
        parts.append(part)
    assert len(parts) == part_count, (len(parts), part_count)
    return parts


def summarize(path: Path):
    parts = parse(inflate_aya(path.read_bytes()))
    print(f"== {path.name}: {len(parts)} parts")
    print(f"{'#':>3} {'name':<24}{'aF':>4}{'vF':>5}{'hF':>5}  " +
          "  ".join(f"{t:>14}" for t in ("VHFM", "HORI", "HPOS", "CPOS", "CORI", "PBKT", "HFOV")))
    for part in parts:
        cells = []
        for tag, unit in (("VHFM", 1), ("HORI", 48), ("HPOS", 16),
                          ("CPOS", 16), ("CORI", 48), ("PBKT", 0), ("HFOV", 4)):
            rec = part["records"].get(tag)
            if rec is None:
                cells.append(f"{'-':>14}")
            elif unit and rec[0] % unit == 0:
                cells.append(f"{rec[0]//unit:>7}x{unit:<6}")
            else:
                cells.append(f"{rec[0]:>10}B    ")
        print(f"{part['number']:>3} {part['name'][:24]:<24}{part['aFrames']:>4}"
              f"{part['vFrames']:>5}{part['hFrames']:>5}  " + "  ".join(cells))
    return parts


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+", type=Path)
    ap.add_argument("--json", type=Path)
    args = ap.parse_args()
    dump = {}
    for p in args.paths:
        parts = summarize(p)
        dump[p.name] = [
            {k: v for k, v in part.items() if k != "records"}
            | {"records": {t: r[0] for t, r in part["records"].items()}}
            for part in parts
        ]
        print()
    if args.json:
        args.json.write_text(json.dumps(dump, indent=1), encoding="utf-8")
