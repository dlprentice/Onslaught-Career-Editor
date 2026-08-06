#!/usr/bin/env python3
"""Unit tests for tools/re_runtime_slot_read.py (no live CDB)."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from re_runtime_slot_read import (  # noqa: E402
    PRISTINE_SHA256,
    decode_mov_rm_imm32,
    parse_cdb_log,
    pe_map,
)


class DecodeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        candidates = [
            ROOT
            / "local-lab"
            / "pristine-verification-2026-07-26"
            / "pristine-target"
            / "BEA.exe",
            ROOT / "local-lab" / "safe-copy-bea-pristine" / "BEA.exe.original.backup",
        ]
        cls.spec = next((p for p in candidates if p.is_file()), None)
        if cls.spec is None:
            raise unittest.SkipTest("pristine BEA not available")
        cls.raw = cls.spec.read_bytes()
        import hashlib

        if hashlib.sha256(cls.raw).hexdigest() != PRISTINE_SHA256:
            raise unittest.SkipTest("specimen hash mismatch")
        cls.ib, cls.secs = pe_map(cls.raw)

    def test_create_install_esp28(self):
        d = decode_mov_rm_imm32(self.raw, self.ib, self.secs, 0x00529151)
        self.assertNotIn("error", d)
        self.assertEqual(d["form"], "[esp+disp]")
        self.assertEqual(d["disp"], 0x28)
        self.assertEqual(d["imm"], 0x00529070)
        self.assertEqual(d["insnLen"], 8)
        self.assertEqual(d["cdbDump"], "dd esp+0x28 L1")

    def test_parse_post_install_and_entry(self):
        plan = {
            "candidates": [
                {
                    "candidateVa": "0x00529070",
                    "endVa": "0x00529090",
                    "joinGrade": "CALLBACK_SLOT_INSTALL",
                    "installs": [],
                    "consumers": [],
                },
                {
                    "candidateVa": "0x0057aea4",
                    "endVa": "0x0057aedc",
                    "joinGrade": "CALLBACK_SLOT_INSTALL",
                    "installs": [],
                    "consumers": [],
                },
            ]
        }
        log = """
PROBE_GO
HIT_INSTALL_CAND_00529070_AT_00529151
eax=0
00529151 c744242870905200 mov dword ptr [esp+28h],offset BEA+0x129070 (00529070)
SLOT_DUMP_CAND_00529070_AT_00529151
001af690  00529070
SLOT_EXPECT_CAND_00529070=00529070
HIT_CAND_00529070
eip=00529070
001af014  77099283 USER32!_InternalCallWinProc+0x2b
"""
        p = parse_cdb_log(log, plan)
        self.assertEqual(p["nSlotOk"], 1)
        self.assertEqual(p["nEntryHit"], 1)
        self.assertEqual(p["nEntryExternalRet"], 1)
        g = p["perCandidate"][0]["runtimeGrade"]
        self.assertEqual(g, "RUNTIME_SLOT_INSTALL_AND_ENTRY_EXTERNAL_RET")
        self.assertEqual(p["perCandidate"][1]["runtimeGrade"], "RUNTIME_UNREACHED")
        evidence = p["perCandidate"][0]["installHits"][0]["evidence"]
        self.assertEqual(evidence, "post_install_dd")

    def test_parse_interleaved_slot_dumps(self):
        """One-shot BPs emit dumps out of order; must bind by exact token."""
        plan = {
            "candidates": [
                {
                    "candidateVa": "0x0057aea4",
                    "endVa": "0x0057aebe",
                    "joinGrade": "CALLBACK_SLOT_INSTALL",
                    "installs": [],
                    "consumers": [],
                },
                {
                    "candidateVa": "0x0057aedc",
                    "endVa": "0x0057aef0",
                    "joinGrade": "CALLBACK_SLOT_INSTALL",
                    "installs": [],
                    "consumers": [],
                },
            ]
        }
        log = """
PROBE_GO
HIT_INSTALL_CAND_0057aea4_AT_0057af47
HIT_INSTALL_CAND_0057aedc_AT_0057afad
SLOT_DUMP_CAND_0057aea4_AT_0057af47
001ae9ac  0057aea4
SLOT_DUMP_CAND_0057aedc_AT_0057afad
02f5150c  0057aedc
"""
        p = parse_cdb_log(log, plan)
        self.assertEqual(p["nSlotOk"], 2)
        self.assertEqual(
            p["perCandidate"][0]["installHits"][0]["slotDword"], "0x0057aea4"
        )
        self.assertEqual(
            p["perCandidate"][1]["installHits"][0]["slotDword"], "0x0057aedc"
        )


if __name__ == "__main__":
    unittest.main()
