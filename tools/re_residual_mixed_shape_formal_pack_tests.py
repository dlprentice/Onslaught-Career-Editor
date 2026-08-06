#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import struct
import tempfile
import unittest
from pathlib import Path

from re_residual_mixed_shape_formal_pack import (
    PRISTINE_SHA256,
    build_pack,
    recheck_kind,
    proposed_for_kind,
)


def _minimal_pe_with_text(text_blob: bytes, text_rva: int = 0x1000) -> bytes:
    """Build a tiny PE32 with one .text section containing text_blob at VA image_base+text_rva."""
    # DOS header
    dos = bytearray(0x80)
    dos[0:2] = b"MZ"
    struct.pack_into("<I", dos, 0x3C, 0x80)
    # PE + COFF + optional
    pe = bytearray()
    pe += struct.pack("<I", 0x00004550)  # PE sig
    pe += struct.pack("<H", 0x14C)  # machine
    pe += struct.pack("<H", 1)  # sections
    pe += struct.pack("<I", 0)  # timestamp
    pe += struct.pack("<I", 0)  # ptr symbols
    pe += struct.pack("<I", 0)  # num symbols
    pe += struct.pack("<H", 0x60)  # size optional (PE32 min-ish)
    pe += struct.pack("<H", 0x010F)  # characteristics
    # Optional header PE32
    opt = bytearray(0x60)
    struct.pack_into("<H", opt, 0, 0x10B)  # magic
    struct.pack_into("<I", opt, 28, 0x00400000)  # image base
    struct.pack_into("<I", opt, 56, 0x2000)  # size of image
    # Section header
    sec = bytearray(40)
    sec[0:5] = b".text"
    struct.pack_into("<I", sec, 8, len(text_blob))  # vsize
    struct.pack_into("<I", sec, 12, text_rva)  # va
    struct.pack_into("<I", sec, 16, len(text_blob))  # rawsize
    raw_ptr = 0x80 + 24 + 0x60 + 40  # after headers
    # Fix: PE at 0x80, COFF 20 bytes after sig? PE sig 4 + COFF 20 = 24, then optional 0x60, then section 40
    # Actually after PE sig: COFF is 20 bytes (machine through characteristics) - I already packed that as part of pe starting with sig.
    # Layout: 0x80 PE sig(4)+COFF(20)+opt(0x60)+sec(40) = 0x80+4+20+0x60+40 = 0x80+0xA8 = 0x128
    raw_ptr = 0x200  # align
    struct.pack_into("<I", sec, 20, raw_ptr)
    header = bytes(dos) + bytes(pe) + bytes(opt) + bytes(sec)
    if len(header) > raw_ptr:
        raise AssertionError("header too large")
    out = bytearray(raw_ptr + len(text_blob))
    out[: len(header)] = header
    out[raw_ptr : raw_ptr + len(text_blob)] = text_blob
    return bytes(out)


class RecheckKindTests(unittest.TestCase):
    def test_pad_ok(self) -> None:
        ok, note = recheck_kind("ALIGN_PAD_PREFIX", b"\x90" * 8)
        self.assertTrue(ok)
        self.assertEqual("pad_bytes_only", note)

    def test_pad_fail(self) -> None:
        ok, _ = recheck_kind("ALIGN_PAD_PREFIX", b"\x90\x90\xC3\x90")
        self.assertFalse(ok)

    def test_code_ptr_table(self) -> None:
        # 8 dwords of .text pointers
        blob = b"".join(struct.pack("<I", 0x00401000 + i * 4) for i in range(8))
        ok, note = recheck_kind("CODE_ADDRESS_TABLE_PREFIX", blob)
        self.assertTrue(ok)
        self.assertIn("code_ptrs=8", note)

    def test_proposed_mapping(self) -> None:
        self.assertEqual(
            "TERMINAL_PADDING",
            proposed_for_kind("ALIGN_PAD_PREFIX")["terminalState"],
        )
        self.assertEqual(
            "TERMINAL_DATA",
            proposed_for_kind("CODE_ADDRESS_TABLE_PREFIX")["terminalState"],
        )
        self.assertEqual(
            "TERMINAL_BOUNDED_AMBIGUITY",
            proposed_for_kind("STATIC_CODE_DECODE_ENVELOPE")["terminalState"],
        )


class BuildPackSyntheticTests(unittest.TestCase):
    def test_build_pack_accepts_pad_whole_span_excludes_executed(self) -> None:
        # pad residual at VA 0x401000
        text = b"\xCC" * 16 + b"\x90" * 16
        pe = _minimal_pe_with_text(text, text_rva=0x1000)
        # Force pristine hash bypass by monkeypatching in build? build_pack checks sha.
        # For unit test, call internal path without hash check via temporary override.
        deeper = {
            "schema": "test",
            "specimen_sha256": hashlib.sha256(pe).hexdigest(),
            "rows": [
                {
                    "startVa": "0x00401000",
                    "endVa": "0x00401010",
                    "bytes": 16,
                    "baseKind": "CODE_LIKE_OPEN",
                    "primary": "FULLY_SUBSPAN_TERMINAL",
                    "wholeSpanTerminal": True,
                    "subspans": [
                        {
                            "startVa": "0x00401000",
                            "endVa": "0x00401010",
                            "bytes": 16,
                            "kind": "ALIGN_PAD_PREFIX",
                            "terminal": True,
                            "reason": "test",
                        }
                    ],
                },
                {
                    "startVa": "0x00401010",
                    "endVa": "0x00401020",
                    "bytes": 16,
                    "baseKind": "EXECUTED_CODE_SPAN_OPEN_BOUNDARY",
                    "primary": "FULLY_SUBSPAN_TERMINAL",
                    "wholeSpanTerminal": True,
                    "subspans": [
                        {
                            "startVa": "0x00401010",
                            "endVa": "0x00401020",
                            "bytes": 16,
                            "kind": "ALIGN_PAD_PREFIX",
                            "terminal": True,
                            "reason": "test",
                        }
                    ],
                },
            ],
        }
        camp = (
            "# bea.re.campaign.v5\n"
            "entityKey\tstartVa\tendVa\tbytes\tobservedBytes\tobservationState\t"
            "classification\tclassificationVerdict\tterminalState\tbytePattern\t"
            "prevFunc\tnextFunc\tcampaignState\tlever\trequiresElevation\t"
            "cheapestFalsifier\tquestionIds\tlastMeasurementDate\n"
            "EK1\t0x00401000\t0x00401010\t16\t0\tDARK\tAMBIGUOUS\tUNSCORED\t\t"
            "PADDING_LIKE_BYTES\tA\tB\tOPEN_DARK_RESIDUAL\tL\tFalse\tfals\tQ-test1\t2026-08-05\n"
            "EK2\t0x00401010\t0x00401020\t16\t16\tEXECUTED\tAMBIGUOUS\tUNSCORED\t\t"
            "MIXED_OR_CODE_LIKE_BYTES\tA\tB\tOPEN_EXECUTED_RESIDUAL\tL\tFalse\tfals\tQ-test2\t2026-08-05\n"
        )
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            pe_path = td_path / "BEA.exe"
            # build_pack requires pristine hash — patch module constant locally
            import re_residual_mixed_shape_formal_pack as mod

            pe_path.write_bytes(pe)
            deeper_path = td_path / "deeper.json"
            deeper["specimen_sha256"] = hashlib.sha256(pe).hexdigest()
            deeper_path.write_text(json.dumps(deeper), encoding="utf-8")
            camp_path = td_path / "residuals.tsv"
            camp_path.write_text(camp, encoding="utf-8")
            old = mod.PRISTINE_SHA256
            try:
                mod.PRISTINE_SHA256 = hashlib.sha256(pe).hexdigest()
                pack = mod.build_pack(pe_path, deeper_path, camp_path)
            finally:
                mod.PRISTINE_SHA256 = old
            self.assertEqual(1, pack["n_proofs"])
            self.assertEqual(1, pack["n_excluded_executed"])
            self.assertEqual("READY_FOR_GENERATION", pack["status"])
            self.assertTrue(pack["proofs"][0]["proposed"]["requiresQuestionSupersession"])
            self.assertEqual("TERMINAL_PADDING", pack["proofs"][0]["proposed"]["terminalState"])


if __name__ == "__main__":
    unittest.main()
