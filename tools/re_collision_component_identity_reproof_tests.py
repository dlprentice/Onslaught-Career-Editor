#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import copy
import importlib.util
import json
import os
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OWNER_PATH = ROOT / "tools/re_collision_component_identity_reproof.py"
SPEC = importlib.util.spec_from_file_location(
    "re_collision_component_identity_reproof", OWNER_PATH)
assert SPEC is not None and SPEC.loader is not None
proof = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(proof)


class CollisionComponentIdentityReproofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(os.environ.get("BEA_REPO_ROOT", ROOT)).resolve()
        cls.ready = json.loads(
            (cls.root / proof.EVIDENCE_RELATIVE / proof.READY_NAME).read_text(encoding="utf-8"))
        cls.thing = (cls.root / "references/Onslaught/thing.cpp").read_text(encoding="utf-8")
        cls.init = (cls.root / "references/Onslaught/InitThing.h").read_text(encoding="utf-8")
        cls.event = (cls.root / "references/Onslaught/eventmanager.cpp").read_text(encoding="utf-8")
        cls.instructions = proof.read_tsv(cls.root / proof.INSTRUCTIONS_RELATIVE)
        cls.xrefs = proof.read_tsv(cls.root / proof.XREFS_RELATIVE)
        cls.vtables = proof.read_tsv(cls.root / proof.VTABLES_RELATIVE)
        cls.functions = proof.read_tsv(cls.root / proof.FUNCTIONS_RELATIVE)
        cls.program = proof.read_tsv(cls.root / proof.PROGRAM_RELATIVE)
        cls.image = bytearray(
            (cls.root / "local-lab/safe-copy-bea-pristine/BEA.exe.original.backup").read_bytes())

    def test_saved_receipt_is_exactly_rederived(self) -> None:
        proof.validate_saved(self.ready, self.root)
        corrections = self.ready["adjudication"]["corrections"]
        self.assertEqual(len(corrections), 5)
        self.assertEqual(corrections[0]["to"], "CCollisionSeekingThing__dtor_base")
        self.assertEqual(corrections[-1]["to"], "CCSPersistentThing__HandleEvent")
        self.assertIn("folded derived aliases", " ".join(self.ready["limitations"]))

    def test_base_vtable_slot_substitution_is_rejected(self) -> None:
        poisoned = copy.deepcopy(self.vtables)
        row = next(row for row in poisoned if row["class"] == "CCSPersistentThing" and
                   row["slot"] == "0")
        row["function_va"] = "0x004014c0"
        with self.assertRaisesRegex(proof.ProofError, "strict vtable row differs"):
            proof.validate_vtables(poisoned)

    def test_derived_placement_removal_is_rejected(self) -> None:
        poisoned = [row for row in copy.deepcopy(self.vtables) if not (
            row["class"] == "CCollisionSeekingInfantryBloke" and
            row["slot"] == "5" and row["function_va"] == "0x00426a00")]
        with self.assertRaisesRegex(proof.ProofError, "placement set differs"):
            proof.validate_vtables(poisoned)

    def test_init_source_owner_substitution_is_rejected(self) -> None:
        poisoned = self.thing.replace("new( MT_CST ) CCSPersistentThing",
                                      "new( MT_CST ) CCollisionSeekingRound", 1)
        with self.assertRaisesRegex(proof.ProofError, "thing.cpp source line differs"):
            proof.validate_source_text(poisoned, self.init, self.event)

    def test_event_landmark_substitution_is_rejected(self) -> None:
        poisoned = copy.deepcopy(self.instructions)
        row = next(row for row in poisoned if row["instruction_addr"] == "0x00426a24")
        row["operands"] = "word ptr [EAX + 0x4], 0x7d0"
        with self.assertRaisesRegex(proof.ProofError, "body landmark differs"):
            proof.validate_instructions(poisoned, self.xrefs)

    def test_pristine_body_poison_is_rejected(self) -> None:
        poisoned = bytearray(self.image)
        offset = proof.pe_offset(poisoned, 0x00426A2F)
        poisoned[offset] ^= 1
        with self.assertRaisesRegex(proof.ProofError, "body bytes differ"):
            proof.validate_pristine(bytes(poisoned), require_whole_image=False)

    def test_current_ghidra_preimage_substitution_is_rejected(self) -> None:
        poisoned = copy.deepcopy(self.functions)
        row = next(row for row in poisoned if row["address"] == "0x004269b0")
        row["name"] = "CCSPersistentThing__Init"
        with self.assertRaisesRegex(proof.ProofError, "PRE name differs"):
            proof.validate_inventory(poisoned, self.program)

    def test_receipt_cannot_launder_runtime_or_alias_claim(self) -> None:
        candidate = copy.deepcopy(self.ready)
        candidate["adjudication"]["confidence"] = "RUNTIME_COMPLETE_NO_FOLDED_ALIASES"
        with self.assertRaisesRegex(proof.ProofError, "saved proof content differs"):
            proof.validate_saved(candidate, self.root)


if __name__ == "__main__":
    unittest.main()
