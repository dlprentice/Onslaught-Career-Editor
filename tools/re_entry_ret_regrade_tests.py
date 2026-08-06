#!/usr/bin/env python3
"""Unit tests for tools/re_entry_ret_regrade.py."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from re_entry_ret_regrade import (  # noqa: E402
    PRISTINE_SHA256,
    parse_entry_hits,
    regrade,
    stream_align_ret,
    pe_map,
)


class ParseTests(unittest.TestCase):
    def test_parse_dds_and_k(self):
        log = """
HIT_CAND_0057aea4
eip=0057aea4
001ae938  005925a4 BEA+0x1925a4
001ae93c  001aea70
ChildEBP RetAddr
001ae940 005925a4     BEA+0x1925a4
001ae980 0059b000     BEA+0x19b000
"""
        hits = parse_entry_hits(log)
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["eip"], "0x0057aea4")
        self.assertEqual(hits[0]["ddsFirstDword"], "0x005925a4")
        # k may also capture
        self.assertTrue(
            hits[0]["kRetAddr"] is None or hits[0]["kRetAddr"] == "0x005925a4"
        )


class AlignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        candidates = [
            ROOT
            / "local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe",
            ROOT / "local-lab/safe-copy-bea-pristine/BEA.exe.original.backup",
        ]
        cls.spec = next((p for p in candidates if p.is_file()), None)
        if cls.spec is None:
            raise unittest.SkipTest("pristine BEA not available")
        cls.raw = cls.spec.read_bytes()
        import hashlib

        if hashlib.sha256(cls.raw).hexdigest() != PRISTINE_SHA256:
            raise unittest.SkipTest("hash mismatch")
        cls.ib, cls.secs = pe_map(cls.raw)

    def test_post_call_aligned(self):
        # 0x00592548 is immediately after call [esi+0xc] at 0x00592545
        a = stream_align_ret(self.raw, self.ib, self.secs, 0x00592548)
        self.assertTrue(a["instructionBoundary"])
        self.assertTrue(a["immediatelyAfterCall"])
        self.assertEqual(a["grade"], "POST_CALL_ALIGNED")

    def test_regrade_synthetic(self):
        plan = {
            "candidates": [
                {
                    "candidateVa": "0x0057aedc",
                    "endVa": "0x0057aef4",
                },
                {
                    "candidateVa": "0x0057aea4",
                    "endVa": "0x0057aebe",
                },
            ]
        }
        log = """
HIT_CAND_0057aedc
eip=0057aedc
001ae938  00592548 BEA+0x192548
HIT_CAND_0057af07
eip=0057af07
001ae92c  0057aeaf BEA+0x17aeaf
"""
        # second hit uses sibling residual ret - plan needs 0057af07
        plan["candidates"].append(
            {"candidateVa": "0x0057af07", "endVa": "0x0057af0a"}
        )
        r = regrade(self.spec, plan, log)
        self.assertEqual(r["nHits"], 2)
        g0 = r["hits"][0]["entryRetGrade"]
        self.assertIn("POST_CALL", g0)
        # sibling
        g1 = r["hits"][1]
        self.assertEqual(g1["candidateVa"], "0x0057af07")
        self.assertTrue(
            g1["retLocality"] and g1["retLocality"].startswith("SIBLING")
        )


if __name__ == "__main__":
    unittest.main()
