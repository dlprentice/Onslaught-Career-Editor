#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import hashlib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/GhidraApplyCollisionComponentIdentity.java"
PROOF = ROOT / "local-lab/collision-component-identity-reproof-20260812-v1/proof.ready.json"


class CollisionComponentIdentityMutatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = TOOL.read_text(encoding="utf-8")

    def test_exact_proof_is_bound(self) -> None:
        raw = PROOF.read_bytes()
        self.assertIn(f"private static final long PROOF_BYTES = {len(raw)};", self.source)
        self.assertIn(hashlib.sha256(raw).hexdigest(), self.source)
        self.assertIn("requireEvidence(repositoryRoot, PROOF_RELATIVE", self.source)

    def test_exact_five_function_mapping_is_present(self) -> None:
        pairs = (
            ("CCollisionSeekingRound__Destructor", "CCollisionSeekingThing__dtor_base"),
            ("CCollisionSeekingThing__ResolveRoundCollisionResponse",
             "CCollisionSeekingThing__ResolveCollisionResponse"),
            ("CCSPersistentThing__InitWithSound", "CCSPersistentThing__Init"),
            ("CCollisionSeekingRound__ProcessMapWhoCollisionSweep",
             "CCSPersistentThing__ProcessMapWhoCollisionSweep"),
            ("CCollisionSeekingRound__MarkDelayedCollisionReady",
             "CCSPersistentThing__HandleEvent"),
        )
        for old, new in pairs:
            self.assertIn(f'"{old}"', self.source)
            self.assertIn(f'"{new}"', self.source)
        self.assertEqual(self.source.count("new Target("), 5)

    def test_mixed_signatures_are_exact_and_parameter_names_are_not_laundered(self) -> None:
        self.assertIn("void __fastcall CCollisionSeekingThing__dtor_base(void * this)",
                      self.source)
        self.assertIn("CCollisionSeekingThing__ResolveCollisionResponse\" +\n"
                      "                \"(void * this, void * otherRound)", self.source)
        self.assertIn("CCSPersistentThing__Init\" +\n"
                      "                \"(void * this, void * roundConfig)", self.source)
        self.assertIn("legacy otherRound parameter label", self.source)
        self.assertIn("legacy roundConfig", self.source)

    def test_mutation_has_rollback_and_readback_modes(self) -> None:
        for marker in (
            "probe-after-one", "probe-post-inner", "apply", "readback",
            "COLLISION_COMPONENT_IDENTITY_FORCED_AFTER_ONE_FAILURE",
            "COLLISION_COMPONENT_IDENTITY_COMPENSATING_PRE_RESTORE_COMPLETE",
            "loaded_state_verified=true",
        ):
            self.assertIn(marker, self.source)
        self.assertIn("currentProgram.endTransaction(transaction, false)", self.source)

    def test_scope_forbids_program_structure_changes(self) -> None:
        for forbidden in (
            "createFunction(", "removeFunction(", "setBytes(", "createData(",
            "addMemoryReference(", "replaceParameters(", "setCallingConvention(",
            "setReturnType(",
        ):
            self.assertNotIn(forbidden, self.source)
        self.assertIn('"boundariesChanged\\\": 0', self.source)
        self.assertIn('"bytesChanged\\\": 0', self.source)
        self.assertIn('"referencesChanged\\\": 0', self.source)

    def test_no_generic_external_rename_map_or_stale_hud_cohort(self) -> None:
        for forbidden in (
            "renameFile", "BufferedReader", "askFile", "CHud__", "HUD_SOURCE_IDENTITY",
            "hud-source-identity-reproof",
        ):
            self.assertNotIn(forbidden, self.source)


if __name__ == "__main__":
    unittest.main()
