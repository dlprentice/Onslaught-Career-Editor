# SPDX-License-Identifier: MIT
"""Checks the glTF pose checker on synthetic parts and a hand-written glTF animation (no game bytes)."""
import unittest

import numpy as np

import gltf_pose_check as checker

IDENTITY = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0]


def parts(child_positions):
    """A root at the origin and a child keyed at the given game-space positions, one per virtual frame."""
    keys = len(child_positions)
    return [
        {"vframes": 1, "parent": None, "map": bytes([0]), "orientations": IDENTITY, "positions": [0, 0, 0, 0]},
        {"vframes": keys, "parent": 0, "map": bytes(range(keys)), "orientations": IDENTITY * keys,
         "positions": [v for p in child_positions for v in (*p, 0)]},
    ]


def gltf(child_translations):
    """The matching glTF: the child's translation animated over two samples, frames 0..1."""
    return {
        "nodes": [{"children": [1]}, {"translation": list(child_translations[0])}],
        "animations": [{
            "name": "move", "extras": {"startFrame": 0, "frameScaler": 1},
            "channels": [{"sampler": 0, "target": {"node": 1, "path": "translation"}}],
            "samplers": [{"input": 0, "output": 1, "interpolation": "LINEAR"}],
        }],
    }, {0: np.array([[0.0], [1.0]]), 1: np.array(child_translations, float)}


def game_to_gltf(p):
    x, y, z = p
    return (-x, -z, y)


class PoseCheckTests(unittest.TestCase):
    def test_matching_poses_pass(self):
        moves = [(1, 2, 3), (4, 5, 6)]
        document, accessors = gltf([game_to_gltf(p) for p in moves])
        counts, worst = checker.check_model(parts(moves), document, accessors.__getitem__)
        self.assertEqual(counts["animations"], 1)
        self.assertEqual(counts["poses"], 4)
        self.assertEqual(counts["poses differ"], 0)
        self.assertLess(worst, 1e-9)

    def test_a_wrong_pose_is_reported(self):
        moves = [(1, 2, 3), (4, 5, 6)]
        document, accessors = gltf([game_to_gltf(moves[0]), (0, 0, 0)])
        counts, _ = checker.check_model(parts(moves), document, accessors.__getitem__)
        self.assertEqual(counts["poses differ"], 1)

    def test_an_unconverted_axis_is_reported(self):
        moves = [(1, 2, 3), (4, 5, 6)]
        document, accessors = gltf([tuple(moves[0]), tuple(moves[1])])
        counts, _ = checker.check_model(parts(moves), document, accessors.__getitem__)
        self.assertEqual(counts["poses differ"], 2)

    def test_an_animation_without_its_frames_is_reported(self):
        moves = [(1, 2, 3), (4, 5, 6)]
        document, accessors = gltf([game_to_gltf(p) for p in moves])
        del document["animations"][0]["extras"]
        counts, _ = checker.check_model(parts(moves), document, accessors.__getitem__)
        self.assertEqual(counts["animations without frames"], 1)


if __name__ == "__main__":
    unittest.main()
