#!/usr/bin/env python3
"""Focused regression gates for the Level 521 Damage/Hit write proof."""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import re_level521_damage_writes as proof  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
PARENT_READY = ROOT / proof.PARENT_RELATIVE / "campaign.ready.json"
PROOF_ROOT = ROOT / "local-lab/level521-damage-hit-write-proof-20260808-v2"
READY_SHA256 = "ffb2e0b8692ddada364a829d52a158841e5d800742c49bd2a1710b2af135869a"
AUTHOR_SHA256 = "8e8c22d3dbb31c7464ad47c211a5179d773aabd9dd665aa4960ee7aa7a0b47e9"


class Level521DamageWritesPortableTests(unittest.TestCase):
    def test_path_neutral_digest_ignores_only_the_metadata_row(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            left = Path(td) / "left.jsonl"
            right = Path(td) / "right.jsonl"
            left.write_text('{"kind":"metadata","trace":"A"}\n{"kind":"target","value":1}\n', encoding="utf-8")
            right.write_text('{"kind":"metadata","trace":"B"}\n{"kind":"target","value":1}\n', encoding="utf-8")
            _left_rows, left_digest = proof.parse_jsonl(left)
            _right_rows, right_digest = proof.parse_jsonl(right)
            self.assertEqual(left_digest, right_digest)
            right.write_text('{"kind":"metadata","trace":"B"}\n{"kind":"target","value":2}\n', encoding="utf-8")
            self.assertNotEqual(left_digest, proof.parse_jsonl(right)[1])


class Level521DamageWritesLocalAuthorityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not PARENT_READY.is_file():
            raise unittest.SkipTest("maintainer-local Generation 11 authority is absent")
        if not (PROOF_ROOT / "proof.ready.json").is_file():
            raise AssertionError("Generation 11 exists but the required Level 521 proof is absent")

    def test_saved_proof_rederives_and_has_literal_identity(self) -> None:
        receipt = proof.verify(ROOT, PROOF_ROOT)
        self.assertEqual(proof.PROOF_SCHEMA, receipt["schema"])
        self.assertEqual("SURVIVED", receipt["verdict"])
        self.assertEqual(READY_SHA256, hashlib.sha256((PROOF_ROOT / "proof.ready.json").read_bytes()).hexdigest())
        self.assertEqual(AUTHOR_SHA256, hashlib.sha256((PROOF_ROOT / "author.py").read_bytes()).hexdigest())
        self.assertEqual((ROOT / "tools/re_level521_damage_writes.py").read_bytes(), (PROOF_ROOT / "author.py").read_bytes())

    def test_four_targeted_counterexamples_are_rejected(self) -> None:
        result = proof.selftest(ROOT)
        self.assertEqual(
            ["writer-pc", "receiver", "write-order", "hit-write"],
            result["attacks"],
        )

    def test_rehashed_frozen_author_substitution_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            candidate = Path(td) / "proof"
            shutil.copytree(PROOF_ROOT, candidate)
            author = candidate / "author.py"
            data = bytearray(author.read_bytes())
            data[0] ^= 1
            author.write_bytes(data)
            ready = candidate / "proof.ready.json"
            receipt = json.loads(ready.read_text(encoding="utf-8"))
            receipt["author"] = proof.stamp(author, candidate)
            ready.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(proof.ProofError, "executing proof author differs"):
                proof.verify(ROOT, candidate)


if __name__ == "__main__":
    unittest.main(verbosity=2)
