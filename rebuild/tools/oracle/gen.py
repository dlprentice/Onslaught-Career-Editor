# SPDX-License-Identifier: GPL-3.0-or-later
"""Input generators for the per-function oracle: deterministic (seeded per function name), bit-exact text cases.

A generator yields lists of 32-bit words (ints); floats are passed as IEEE bits through f()."""
from __future__ import annotations

import hashlib
import math
import random
import struct


def f(x: float) -> int:
    return struct.unpack("<I", struct.pack("<f", x))[0]


def rng(name: str) -> random.Random:
    return random.Random(int.from_bytes(hashlib.sha256(name.encode()).digest()[:8], "little"))


def special_floats() -> list[float]:
    return [0.0, -0.0, 1.0, -1.0, 0.5, 1e-30, -1e-30, 1e-7, 3.4e38, 0.9999999, 1.0000001]


def hf_position(name: str, count: int):
    """A position over the 512 x 512 map and a margin around it, with grid points, cell edges and ties."""
    r = rng(name)
    out = []
    for i in range(count):
        c = r.random()
        if c < 0.55:
            x, y = r.uniform(-3, 515), r.uniform(-3, 515)
        elif c < 0.75:  # exact and near-exact sample positions (the 8.8 fixed point's grid)
            x, y = r.randrange(0, 512) + r.choice([0.0, 1 / 256, 0.5, 255 / 256, 0.999, 0.001]), \
                r.randrange(0, 512) + r.choice([0.0, 1 / 256, 0.5, 255 / 256, 0.999, 0.001])
        elif c < 0.9:  # ties at the packed representation's rounding boundaries
            x = (r.randrange(0, 131072) + 0.5) / 256.0 + r.choice([0.0, 1e-5, -1e-5, 1e-7])
            y = (r.randrange(0, 131072) + 0.5) / 256.0 + r.choice([0.0, 1e-5, -1e-5, 1e-7])
            x, y = x % 515, y % 515
        else:
            x, y = r.choice(special_floats() + [511.99, 512.0, 512.01, -0.01]), r.choice(special_floats() + [511.99, 512.0, 512.01, -0.01])
        out.append([f(x), f(y)])
    return out


TYPES = {"building": 0x80000100, "component": 0x80080000, "battle_ground": 0x80000208, "battle_air": 0x80000008,
         "other": 0x80000000, "tank": 0x80000210}


def thing_centre(name: str, count: int):
    """CThing::GetCentrePos: a thing of each kind, at a position with a rotation and a bounding-box origin, with and
    without a box. Words: type bits, position, 9 matrix entries, has box, box origin, 'a render thing exists'."""
    r = rng(name)
    out = []
    for i in range(count):
        kind = r.choice(list(TYPES))
        pos = [r.uniform(-20, 530), r.uniform(-20, 530), r.uniform(-40, 20)]
        yaw, pitch, roll = r.uniform(-math.pi, math.pi), r.uniform(-1.5, 1.5), r.uniform(-math.pi, math.pi)
        cy, sy, cr, sr, cp, sp = math.cos(yaw), math.sin(yaw), math.cos(roll), math.sin(roll), math.cos(pitch), math.sin(pitch)
        rows = [cr * cy - sp * sr * sy, -cp * sy, sp * cr * sy + sr * cy,
                sp * sr * cy + cr * sy, cp * cy, sr * sy - sp * cr * cy,
                -cp * sr, sp, cp * cr]
        has_box = r.random() < 0.8
        origin = [r.uniform(-12, 12) for _ in range(3)] if r.random() < 0.9 else [r.choice(special_floats()) for _ in range(3)]
        words = [TYPES[kind]] + [f(v) for v in pos] + [f(v) for v in rows] + [1 if has_box else 0] + [f(v) for v in origin] + [1]
        out.append(words)
    return out


GENERATORS = {
    "hf_position": hf_position,
    "thing_centre": thing_centre,
}
