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
OWNER_PATH = ROOT / "tools/re_hud_source_identity_reproof.py"
SPEC = importlib.util.spec_from_file_location("re_hud_source_identity_reproof", OWNER_PATH)
assert SPEC is not None and SPEC.loader is not None
proof = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(proof)


class HudSourceIdentityReproofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(os.environ.get("BEA_REPO_ROOT", ROOT)).resolve()
        cls.ready_path = cls.root / proof.EVIDENCE_RELATIVE / proof.READY_NAME
        cls.ready = json.loads(cls.ready_path.read_text(encoding="utf-8"))
        cls.pc = (cls.root / "references/Onslaught/PCEngine.cpp").read_text(encoding="utf-8")
        cls.dx = (cls.root / "references/Onslaught/DXEngine.cpp").read_text(encoding="utf-8")
        cls.w005 = proof.read_tsv(cls.root / proof.W005_RELATIVE)
        cls.w010 = proof.read_tsv(cls.root / proof.W010_RELATIVE)
        cls.image = bytearray(
            (cls.root / "local-lab/safe-copy-bea-pristine/BEA.exe.original.backup").read_bytes()
        )

    def test_saved_receipt_is_exactly_rederived(self) -> None:
        proof.validate_saved(self.ready, self.root)
        corrections = self.ready["adjudication"]["corrections"]
        self.assertEqual(len(corrections), 3)
        self.assertEqual(corrections[1]["to"], "CHud__Render")
        self.assertEqual(corrections[2]["to"], "CHud__RenderOverlay")

    def test_source_call_substitution_is_rejected(self) -> None:
        poisoned = self.dx.replace("\tHUD.RenderOverlay();", "\tHUD.Render();", 1)
        with self.assertRaisesRegex(proof.ProofError, "source line differs"):
            proof.validate_source_text(self.pc, poisoned)

    def test_retail_call_swap_is_rejected(self) -> None:
        poisoned = copy.deepcopy(self.w010)
        row = next(row for row in poisoned if row["instruction_addr"] == "0x0053ef26")
        row["operands"] = "0x00487bc0"
        with self.assertRaisesRegex(proof.ProofError, "call target differs"):
            proof.validate_retail_rows(self.w005, poisoned)

    def test_body_landmark_substitution_is_rejected(self) -> None:
        poisoned = copy.deepcopy(self.w005)
        row = next(row for row in poisoned if row["instruction_addr"] == "0x0048815f")
        row["operands"] = "0x004879e0"
        with self.assertRaisesRegex(proof.ProofError, "body landmark differs"):
            proof.validate_retail_rows(poisoned, self.w010)

    def test_pristine_body_poison_is_rejected(self) -> None:
        poisoned = bytearray(self.image)
        offset = proof.pe_offset(poisoned, 0x00488096)
        poisoned[offset] ^= 1
        with self.assertRaisesRegex(proof.ProofError, "body bytes differ"):
            proof.validate_pristine(bytes(poisoned), require_whole_image=False)

    def test_receipt_cannot_launder_runtime_or_rebuild_claim(self) -> None:
        candidate = copy.deepcopy(self.ready)
        candidate["adjudication"]["confidence"] = "RUNTIME_COMPLETE_REBUILD_READY"
        with self.assertRaisesRegex(proof.ProofError, "saved proof content differs"):
            proof.validate_saved(candidate, self.root)


if __name__ == "__main__":
    unittest.main()
