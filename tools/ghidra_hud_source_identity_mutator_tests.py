#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import hashlib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/GhidraApplyHudSourceIdentity.java"
PROOF = ROOT / "local-lab/hud-source-identity-reproof-20260812-v1/proof.ready.json"


class HudSourceIdentityMutatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = TOOL.read_text(encoding="utf-8")

    def test_exact_proof_is_bound(self) -> None:
        raw = PROOF.read_bytes()
        self.assertIn(f"private static final long PROOF_BYTES = {len(raw)};", self.source)
        self.assertIn(hashlib.sha256(raw).hexdigest(), self.source)
        self.assertIn("requireEvidence(repositoryRoot, PROOF_RELATIVE", self.source)

    def test_exact_three_function_permutation_is_present(self) -> None:
        pairs = (
            ("CHud__RenderOverlay", "CHud__Render"),
            ("CHud__RenderActiveHudComponentPass", "CHud__RenderOverlay"),
            ("CHud__PromotePendingHudComponent", "CHud__SwitchInOverlay"),
        )
        for old, new in pairs:
            self.assertIn(f'"{old}", "{new}"', self.source)
        self.assertEqual(self.source.count("new Target("), 3)

    def test_mutation_has_rollback_and_readback_modes(self) -> None:
        for marker in (
            "probe-after-one", "probe-post-inner", "apply", "readback",
            "HUD_SOURCE_IDENTITY_FORCED_AFTER_ONE_FAILURE",
            "HUD_SOURCE_IDENTITY_COMPENSATING_PRE_RESTORE_COMPLETE",
            "loaded_state_verified=true",
        ):
            self.assertIn(marker, self.source)
        self.assertIn("currentProgram.endTransaction(transaction, false)", self.source)

    def test_scope_forbids_program_structure_changes(self) -> None:
        self.assertNotIn("createFunction(", self.source)
        self.assertNotIn("removeFunction(", self.source)
        self.assertNotIn("setBytes(", self.source)
        self.assertNotIn("createData(", self.source)
        self.assertNotIn("addMemoryReference(", self.source)
        self.assertIn('"boundariesChanged\\\": 0', self.source)
        self.assertIn('"bytesChanged\\\": 0', self.source)
        self.assertIn('"referencesChanged\\\": 0', self.source)

    def test_no_generic_external_rename_map(self) -> None:
        self.assertNotIn("renameFile", self.source)
        self.assertNotIn("BufferedReader", self.source)
        self.assertNotIn("askFile", self.source)


if __name__ == "__main__":
    unittest.main()
