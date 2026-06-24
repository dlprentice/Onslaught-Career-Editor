#!/usr/bin/env python3
"""Tests for the BattleEngine weapon slot-0 raw boundary probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import battleengine_weapon_slot0_boundary_probe as probe


STUB_TEXT = """address\tbytes\tmnemonic\toperands
00506930\t8B 44 24 04\tMOV\tEAX, dword ptr [ESP + 0x4]
00506934\t53\tPUSH\tEBX
00506935\t56\tPUSH\tESI
00506936\t57\tPUSH\tEDI
00506937\t66 81 78 04 89 13\tCMP\tword ptr [EAX + 0x4], 0x1389
0050693f\t0F 85 A5 00 00 00\tJNZ\t0x005069ea
005069a3\tC2 04 00\tRET\t0x4
005069b6\tE8 35 00 00 00\tCALL\t0x005069f0
005069e5\tE8 86 49 F4 FF\tCALL\t0x0044b370
005069ed\tC2 04 00\tRET\t0x4
005069f0\t64 A1 00 00 00 00\tMOV\tEAX, FS:[0x0]
"""

BODY_TEXT = """address\tbytes\tmnemonic\toperands
005069f0\t64 A1 00 00 00 00\tMOV\tEAX, FS:[0x0]
00506a05\t81 EC 80 0A 00 00\tSUB\tESP, 0xa80
00506a1f\tE8 BC 58 F0 FF\tCALL\t0x0040c2e0
00506a26\t0F 84 67 0E 00 00\tJZ\t0x00507893
00506a38\t0F 84 53 0E 00 00\tJZ\t0x00507891
00506aae\tE8 ED 8C 00 00\tCALL\t0x0050f7a0
00506abc\t0F 84 BB 0D 00 00\tJZ\t0x0050787d
005074c9\tE8 92 FB EF FF\tCALL\t0x00407060
005074d3\tE8 D8 35 FD FF\tCALL\t0x004daab0
00507871\tE8 CA 4A F0 FF\tCALL\t0x0040c340
00507891\t8B C6\tMOV\tEAX, ESI
00507893\t8B 8C 24 90 0A 00 00\tMOV\tECX, dword ptr [ESP + 0xa90]
005078a5\t81 C4 8C 0A 00 00\tADD\tESP, 0xa8c
005078ab\tC3\tRET\t
005078b0\t8B 41 4C\tMOV\tEAX, dword ptr [ECX + 0x4c]
"""


def write_fixture(root: Path, *, omit_inner_call: bool = False) -> tuple[Path, Path]:
    stub = root / "slot0_stub.tsv"
    body = root / "slot0_body.tsv"
    stub_text = STUB_TEXT.replace("005069b6\tE8 35 00 00 00\tCALL\t0x005069f0\n", "")
    stub.write_text(stub_text if omit_inner_call else STUB_TEXT, encoding="utf-8")
    body.write_text(BODY_TEXT, encoding="utf-8")
    return stub, body


class BattleEngineWeaponSlot0BoundaryProbeTests(unittest.TestCase):
    def test_passes_for_current_raw_stub_and_inner_body_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            stub, body = write_fixture(Path(tmp))

            report = probe.build_report(stub_path=stub, body_path=body)

            self.assertEqual(report["status"], "PASS")
            self.assertEqual(report["candidateClassification"], "raw-slot0-boundary-candidate")
            self.assertEqual(report["outerStub"]["startAddress"], "0x00506930")
            self.assertEqual(report["outerStub"]["innerCallTarget"], "0x005069f0")
            self.assertEqual(report["innerBody"]["startAddress"], "0x005069f0")
            self.assertEqual(report["innerBody"]["terminalRetAddress"], "0x005078ab")
            self.assertEqual(report["innerBody"]["firstPostRetAddress"], "0x005078b0")
            self.assertIn("0x0050f7a0", report["innerBodyCallTargets"])
            self.assertEqual(report["unexpectedStealthResetTokens"], [])

    def test_fails_when_stub_does_not_call_inner_body(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            stub, body = write_fixture(Path(tmp), omit_inner_call=True)

            report = probe.build_report(stub_path=stub, body_path=body)

            self.assertEqual(report["status"], "FAIL")
            self.assertTrue(any("missing outer stub call to 0x005069f0" in item for item in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
