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
OWNER_PATH = ROOT / "tools/re_mission_native_setpos_reproof.py"
SPEC = importlib.util.spec_from_file_location("re_mission_native_setpos_reproof", OWNER_PATH)
assert SPEC is not None and SPEC.loader is not None
proof = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(proof)


class MissionNativeSetPosReproofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(os.environ.get("BEA_REPO_ROOT", ROOT)).resolve()
        cls.ready_path = cls.root / proof.EVIDENCE_RELATIVE / proof.READY_NAME
        cls.ready = json.loads(cls.ready_path.read_text(encoding="utf-8"))
        cls.image = bytearray(
            (cls.root / "local-lab/safe-copy-bea-pristine/BEA.exe.original.backup").read_bytes()
        )

    def test_saved_receipt_is_exactly_rederived(self) -> None:
        proof.validate_saved(self.ready, self.root)
        self.assertEqual(self.ready["staticProof"]["instructionCount"], 17)
        self.assertEqual(self.ready["adjudication"]["newFunctionEntityKey"], proof.NEW_ENTITY)
        self.assertEqual(self.ready["ghidra"]["interiorInboundReferences"], 0)

    def test_pristine_partition_and_registry_poisons_are_rejected(self) -> None:
        cases = (
            (proof.RESIDUAL_START, 0xCC, "prefix"),
            (proof.FUNCTION_START + 8, 0x90, "body"),
            (proof.FUNCTION_END, 0xCC, "suffix"),
            (proof.REGISTRY_INIT + 1, 0x71, "initializer"),
            (proof.NAME_ADDRESS, ord("X"), "name"),
        )
        for address, value, label in cases:
            with self.subTest(label=label):
                poisoned = bytearray(self.image)
                poisoned[proof.pe_offset(poisoned, address)] = value
                with self.assertRaisesRegex(proof.ProofError, "differs|padding"):
                    proof.validate_pristine(bytes(poisoned))

    def test_receipt_cannot_launder_boundary_name_or_xref_claims(self) -> None:
        attacks = (
            ("name", lambda value: value["registry"].update({"shippedName": "Teleport"})),
            ("end", lambda value: value["staticProof"]["partition"][1].update({"endVa": "0x00536ca0"})),
            ("xref", lambda value: value["ghidra"].update({"interiorInboundReferences": 1})),
            ("grade", lambda value: value["adjudication"].update({"semanticGradeCeiling": "C2_BOUNDED_RUNTIME"})),
        )
        for label, mutate in attacks:
            with self.subTest(label=label):
                candidate = copy.deepcopy(self.ready)
                mutate(candidate)
                with self.assertRaisesRegex(proof.ProofError, "content differs"):
                    proof.validate_saved(candidate, self.root)


if __name__ == "__main__":
    unittest.main()
