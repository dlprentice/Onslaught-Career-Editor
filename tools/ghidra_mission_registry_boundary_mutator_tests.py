#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MUTATOR = ROOT / "tools/GhidraApplyMissionRegistryBoundaries.java"


class MissionRegistryBoundaryMutatorSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = MUTATOR.read_text(encoding="utf-8")

    def test_only_boundary_mutations_are_present(self) -> None:
        forbidden = (
            "setName(", "setComment(", "setRepeatableComment(", "addTag(",
            "setCallingConvention(", "replaceParameters(", "setReturnType(",
            "createData(", "setBytes(", "addMemoryReference(",
        )
        for token in forbidden:
            self.assertNotIn(token, self.source)
        self.assertEqual(self.source.count("createFunction("), 1)
        self.assertEqual(self.source.count("removeFunction("), 1)
        self.assertIn('\\"namesAuthorized\\": false', self.source)
        self.assertIn('\\"metadataAuthorized\\": false', self.source)

    def test_half_open_endpoint_is_converted_once_and_byte_count_is_checked(self) -> None:
        self.assertIn("endExclusive.subtract(1)", self.source)
        self.assertIn("body.getNumAddresses()", self.source)
        self.assertIn("half-open byte count", self.source)
        self.assertNotIn("new AddressSet(start, endExclusive)", self.source)

    def test_modes_and_rollback_markers_are_explicit(self) -> None:
        for mode in ("dry", "apply", "readback", "probe-after-one", "probe-post-inner"):
            self.assertIn(f'"{mode}"', self.source)
        for marker in (
            "MISSION_REGISTRY_BOUNDARIES_FORCED_AFTER_ONE_FAILURE",
            "MISSION_REGISTRY_BOUNDARIES_COMPENSATING_PRE_RESTORE_COMPLETE",
            "MISSION_REGISTRY_BOUNDARIES_FORCED_POST_INNER_FAILURE",
            "MISSION_REGISTRY_BOUNDARIES_MUTATION_TAINTED",
        ):
            self.assertIn(marker, self.source)

    def test_mutator_is_bound_to_the_immutable_manifest_and_program(self) -> None:
        self.assertIn("e53fd6f4c44ab7f91779e0673e91ae3701514c486594cc733025334fe6289a42",
                      self.source)
        self.assertIn("74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750",
                      self.source)
        self.assertRegex(self.source, re.compile(r"PRE_FUNCTIONS\s*=\s*8136"))
        self.assertRegex(self.source, re.compile(r"POST_FUNCTIONS\s*=\s*8170"))


if __name__ == "__main__":
    unittest.main()
