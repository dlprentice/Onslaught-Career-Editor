#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Check the companion's glTF exports pose by pose against the game's own key composition.

For every model whose export has animations, each animation is evaluated by the glTF rules (node local = T·R·S,
composed down the node hierarchy) at every sample, and every node's world transform is compared with the game's
model-space transform at the matching virtual frame: keys composed from the root as
reverse-engineering/asset-formats/cmsh-animation-keys.md describes, read independently by tools/cmsh_grammar_walk.py,
then carried into glTF's frame by the exporter's reflection (x, y, z) -> (-x, -z, y). Each animation's extras name
the mode's startFrame and frameScaler. The install and the exports are only read.

Run:  BEA_GAME=GAME ASSET_KEEP=all python tools/companion_godot.py test --script Development/AssetCheck.cs
      python tools/gltf_pose_check.py --game GAME --exports <that run>/test-output
Needs numpy.
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import struct
import sys
from pathlib import Path

import numpy as np

import cmsh_grammar_walk as walker

GAME_TO_GLTF = np.array([[-1.0, 0.0, 0.0], [0.0, 0.0, -1.0], [0.0, 1.0, 0.0]])
COMPONENTS = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}


def read_glb(path: Path) -> tuple[dict, callable]:
    """The glTF JSON and a reader for float accessors."""
    data = path.read_bytes()
    if data[:4] != b"glTF":
        raise ValueError(f"{path.name} is not a binary glTF file")
    json_length = struct.unpack_from("<I", data, 12)[0]
    gltf = json.loads(data[20:20 + json_length])
    binary = 20 + json_length + 8

    def accessor(index: int) -> np.ndarray:
        a = gltf["accessors"][index]
        view = gltf["bufferViews"][a["bufferView"]]
        width = COMPONENTS[a["type"]]
        offset = binary + view.get("byteOffset", 0) + a.get("byteOffset", 0)
        return np.frombuffer(data, "<f4", a["count"] * width, offset).reshape(a["count"], width).astype(np.float64)

    return gltf, accessor


def rotation(q: np.ndarray) -> np.ndarray:
    x, y, z, w = q / np.linalg.norm(q)
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def check_model(parts: list[dict], gltf: dict, accessor, tolerance: float = 1e-4) -> tuple[collections.Counter, float]:
    """Every node of every animation at every sample against the game's composition: counts and the worst error."""
    totals: collections.Counter = collections.Counter()
    worst = 0.0
    nodes = gltf.get("nodes", [])
    parent = {child: index for index, node in enumerate(nodes) for child in node.get("children", [])}
    for animation in gltf.get("animations", []):
        extras = animation.get("extras", {})
        start, span = extras.get("startFrame"), extras.get("frameScaler")
        if not isinstance(start, int) or not isinstance(span, int) or span <= 0:
            totals["animations without frames"] += 1
            continue
        totals["animations"] += 1
        channels = {}
        for channel in animation["channels"]:
            sampler = animation["samplers"][channel["sampler"]]
            channels[(channel["target"]["node"], channel["target"]["path"])] = accessor(sampler["output"])
        for k in range(span + 1):
            local = []
            for index, node in enumerate(nodes):
                t = channels.get((index, "translation"), [np.array(node.get("translation", [0, 0, 0]), float)] * (span + 1))[k]
                r = channels.get((index, "rotation"), [np.array(node.get("rotation", [0, 0, 0, 1]), float)] * (span + 1))[k]
                s = channels.get((index, "scale"), [np.array(node.get("scale", [1, 1, 1]), float)] * (span + 1))[k]
                local.append((rotation(np.asarray(r)) @ np.diag(s), np.asarray(t)))
            world: dict[int, tuple[np.ndarray, np.ndarray]] = {}

            def at(index: int) -> tuple[np.ndarray, np.ndarray]:
                if index not in world:
                    m, t = local[index]
                    if index in parent:
                        pm, pt = at(parent[index])
                        m, t = pm @ m, pt + pm @ t
                    world[index] = (m, t)
                return world[index]

            for index in range(min(len(nodes), len(parts))):
                m, t = at(index)
                orientation, position = walker.model_space(parts, index, start + k)
                want_m = GAME_TO_GLTF @ np.array(orientation) @ GAME_TO_GLTF.T
                want_t = GAME_TO_GLTF @ np.array(position)
                error = max(float(np.abs(m - want_m).max()), float(np.abs(t - want_t).max()) / (1 + float(np.abs(want_t).max())))
                totals["poses"] += 1
                worst = max(worst, error)
                if error > tolerance:
                    totals["poses differ"] += 1
    return totals, worst


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--game", type=Path, default=os.environ.get("BEA_GAME"), help="the game folder, only read (default $BEA_GAME)")
    parser.add_argument("--exports", type=Path, required=True, help="folder of <model>.glb files written by AssetCheck with ASSET_KEEP=all")
    args = parser.parse_args(argv)
    if args.game is None:
        parser.error("name the game folder with --game or BEA_GAME")
    totals: collections.Counter = collections.Counter()
    worst = 0.0
    missing = []
    for path in sorted((Path(args.game) / "data/resources/meshes").glob("*.aya")):
        export = args.exports / (path.name[:-8] + ".glb" if path.name.lower().endswith(".msh.aya") else path.stem + ".glb")
        if not export.is_file():
            missing.append(export.name)
            continue
        gltf, accessor = read_glb(export)
        if not gltf.get("animations"):
            continue
        parts = walker.walk_stream(walker.inflate_aya(path.read_bytes()), collections.defaultdict(collections.Counter))[0]
        counts, model_worst = check_model(parts, gltf, accessor)
        totals.update(counts)
        worst = max(worst, model_worst)
    print(f"GLTF_POSES: {totals['animations']} animations, {totals['poses']} node poses checked, {totals['poses differ']} differ "
          f"(worst error {worst:.2e}); {len(missing)} exports missing")
    for name in missing[:10]:
        print("MISSING " + name)
    return 1 if missing or totals["poses differ"] or totals["animations without frames"] else 0


if __name__ == "__main__":
    sys.exit(main())
