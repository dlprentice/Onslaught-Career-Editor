# SPDX-License-Identifier: GPL-3.0-or-later
"""Settle CPOS/CORI semantics from the bytes.

Hypothesis under test: for each part, CPOS/CORI are indexed by *virtual* frame
(CMSP+0xBC `vFrames`) and hold the model-space composition of the per-part local
hierarchy track HORI/HPOS (indexed by *hierarchy* frame, CMSP+0xC0 `hFrames`,
selected through the VHFM virtual->hierarchy frame map) up the PRNT chain.

The test composes the local chain itself and reports the maximum absolute
element error against the stored CPOS/CORI. Analysis only; writes nothing.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import struct
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cmsh_track_probe import parse  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "rebuild" / "tools"))
from cmsh_static_preview import inflate_aya  # noqa: E402


def mat(payload: bytes, index: int):
    """HORI/CORI record -> 3x3 basis rows (each stored row is 4 floats)."""
    f = struct.unpack_from("<12f", payload, index * 48)
    return (f[0:3], f[4:7], f[8:11])


def vec(payload: bytes, index: int):
    return struct.unpack_from("<3f", payload, index * 16)


def mul(a, b):
    """(a*b)[i][j] = sum_k a[i][k]*b[k][j] (row-major storage, column vectors)."""
    return tuple(
        tuple(sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3))
        for i in range(3)
    )


def xform(m, v):
    """(m*v)[i] = sum_k m[i][k]*v[k]."""
    return tuple(sum(m[i][k] * v[k] for k in range(3)) for i in range(3))


def track(part, tag, count_fallback):
    rec = part["records"].get(tag)
    return rec[1] if rec else None


def analyse(path: Path, verbose_part: int | None = None):
    parts = parse(inflate_aya(path.read_bytes()))
    parent = {}
    for p in parts:
        prnt = p["records"].get("PRNT")
        parent[p["number"]] = struct.unpack("<I", prnt[1])[0] if prnt else None

    worst_ori = worst_pos = 0.0
    checked = 0
    for p in parts:
        cori = track(p, "CORI", 0)
        cpos = track(p, "CPOS", 0)
        if cpos is None:
            continue
        vframes = p["vFrames"]
        n_pos = len(cpos) // 16
        n_ori = len(cori) // 48 if cori else 0
        chain = []
        node = p["number"]
        while node is not None:
            chain.append(node)
            node = parent[node]
        chain.reverse()  # root first
        for v in range(vframes):
            # Compose root -> leaf: M = M_parent * M_local, t = M_parent*t_local + t_parent.
            m = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))
            t = (0.0, 0.0, 0.0)
            for node in chain:
                q = parts[node]
                vhfm = q["records"]["VHFM"][1]
                h = min(vhfm[v] if v < len(vhfm) else 0, q["hFrames"] - 1)
                lm = mat(q["records"]["HORI"][1], h)
                lp = vec(q["records"]["HPOS"][1], h)
                t = tuple(a + b for a, b in zip(xform(m, lp), t))
                m = mul(m, lm)
            ci = min(v, n_pos - 1)
            sp = vec(cpos, ci)
            worst_pos = max(worst_pos, max(abs(a - b) for a, b in zip(t, sp)))
            if n_ori:
                sm = mat(cori, min(v, n_ori - 1))
                worst_ori = max(
                    worst_ori,
                    max(abs(m[i][j] - sm[i][j]) for i in range(3) for j in range(3)),
                )
            checked += 1
    print(f"{path.name}: {checked} (part, vframe) samples")
    print(f"  max |composed CPOS - stored CPOS| = {worst_pos:.6g}")
    print(f"  max |composed CORI - stored CORI| = {worst_ori:.6g}")

    if verbose_part is not None:
        p = parts[verbose_part]
        print(f"\n  part {verbose_part} '{p['name']}' hFrames={p['hFrames']} vFrames={p['vFrames']}")
        vhfm = p["records"]["VHFM"][1]
        print(f"  VHFM = {list(vhfm)}")
        hori = p["records"]["HORI"][1]
        hpos = p["records"]["HPOS"][1]
        for h in range(p["hFrames"]):
            m = mat(hori, h)
            det = (
                m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
                - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
                + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0])
            )
            import math
            about_z = math.degrees(math.atan2(m[0][1], m[0][0]))
            about_y = math.degrees(math.atan2(-m[0][2], m[0][0]))
            about_x = math.degrees(math.atan2(m[1][2], m[1][1]))
            print(f"   h{h:>3} pos={tuple(round(x,4) for x in vec(hpos,h))} "
                  f"det={det:+.6f} rotZ={about_z:+8.3f} rotY={about_y:+8.3f} "
                  f"rotX={about_x:+8.3f}  row0={tuple(round(x,5) for x in m[0])}")
    return parts


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("path", type=Path)
    ap.add_argument("--part", type=int)
    args = ap.parse_args()
    analyse(args.path, args.part)
