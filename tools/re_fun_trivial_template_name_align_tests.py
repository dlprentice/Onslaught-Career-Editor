#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
import importlib.util
import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "m", ROOT / "tools/re_fun_trivial_template_name_align.py"
)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class T(unittest.TestCase):
    def test_ret(self):
        r = m.classify_body(0x401000, bytes([0xC3]))
        self.assertEqual(r["lane"], "RET")

    def test_zero3(self):
        b = bytes.fromhex(
            "c7056000660000000000c7056400660000000000c7056800660000000000c3"
        )
        r = m.classify_body(0x4010C0, b)
        self.assertEqual(r["lane"], "ZERO_DWORDS3")
        self.assertIn("00660060", r["newName"])

    def test_jmp_thunk(self):
        entry = 0x401000
        target = 0x402000
        rel = target - (entry + 10)
        b = (
            bytes([0xB9])
            + struct.pack("<I", 0x12345678)
            + bytes([0xE9])
            + struct.pack("<i", rel)
        )
        r = m.classify_body(entry, b)
        self.assertEqual(r["lane"], "JMP_THUNK")

    def test_store_dwords3_nonzero(self):
        base = 0x704B68
        parts = []
        for i, imm in enumerate([0xBF800000, 0xBF800000, 0xBF800000]):
            parts.append(
                b"\xc7\x05" + struct.pack("<I", base + 4 * i) + struct.pack("<I", imm)
            )
        b = b"".join(parts) + b"\xc3"
        r = m.classify_body(0x4ABF00, b)
        self.assertEqual(r["lane"], "STORE_DWORDS3")

    def test_dyninit22(self):
        # b9 ecx; e8 call; 68 push; e8 call; 59 c3
        b = (
            bytes([0xB9])
            + struct.pack("<I", 0x6602A0)
            + bytes([0xE8])
            + struct.pack("<i", 0x100)
            + bytes([0x68])
            + struct.pack("<I", 0x40F500)
            + bytes([0xE8])
            + struct.pack("<i", 0x200)
            + bytes([0x59, 0xC3])
        )
        self.assertEqual(len(b), 22)
        r = m.classify_body(0x40F4E0, b)
        self.assertEqual(r["lane"], "DYNINIT22")
        self.assertIn("0040f500", r["newName"])

    def test_dyninit29(self):
        # 6a 00; 68 str; b9 ecx; e8; 68 func; e8; 59 c3
        b = (
            bytes([0x6A, 0x00])
            + bytes([0x68])
            + struct.pack("<I", 0x629084)
            + bytes([0xB9])
            + struct.pack("<I", 0x6602A0)
            + bytes([0xE8])
            + struct.pack("<i", 0x100)
            + bytes([0x68])
            + struct.pack("<I", 0x453090)
            + bytes([0xE8])
            + struct.pack("<i", 0x200)
            + bytes([0x59, 0xC3])
        )
        self.assertEqual(len(b), 29)
        r = m.classify_body(0x453070, b)
        self.assertEqual(r["lane"], "DYNINIT29")
        self.assertIn("00453090", r["newName"])

    def test_dyninit29_nonzero_push(self):
        b = (
            bytes([0x6A, 0x01])
            + bytes([0x68])
            + struct.pack("<I", 0x63DC24)
            + bytes([0xB9])
            + struct.pack("<I", 0x6602A0)
            + bytes([0xE8])
            + struct.pack("<i", 0x100)
            + bytes([0x68])
            + struct.pack("<I", 0x512000)
            + bytes([0xE8])
            + struct.pack("<i", 0x200)
            + bytes([0x59, 0xC3])
        )
        r = m.classify_body(0x511FE0, b)
        self.assertEqual(r["lane"], "DYNINIT29")
        self.assertIn("00512000", r["newName"])

    def test_store_dword1(self):
        b = (
            b"\xc7\x05"
            + struct.pack("<I", 0x66F580)
            + struct.pack("<I", 0x5DB01C)
            + b"\xc3"
        )
        self.assertEqual(len(b), 11)
        r = m.classify_body(0x441620, b)
        self.assertEqual(r["lane"], "STORE_DWORD1")
        self.assertIn("0066f580", r["newName"])

    def test_store_dwords2(self):
        base = 0x89C850
        b = (
            b"\xc7\x05"
            + struct.pack("<I", base)
            + struct.pack("<I", 0)
            + b"\xc7\x05"
            + struct.pack("<I", base + 4)
            + struct.pack("<I", 0)
            + b"\xc3"
        )
        self.assertEqual(len(b), 21)
        r = m.classify_body(0x53A2B0, b)
        self.assertEqual(r["lane"], "STORE_DWORDS2")

    def test_store_byte1(self):
        b = b"\xc6\x05" + struct.pack("<I", 0x8A97D0) + bytes([0x00, 0xC3])
        r = m.classify_body(0x5412D0, b)
        self.assertEqual(r["lane"], "STORE_BYTE1")

    def test_zero_a3_chain(self):
        b = bytes([0x33, 0xC0])
        for addr in (0x83D964, 0x83D974, 0x83D960, 0x83D978):
            b += bytes([0xA3]) + struct.pack("<I", addr)
        b += bytes([0xC3])
        r = m.classify_body(0x4F2120, b)
        self.assertEqual(r["lane"], "ZERO_A3x4")

    def test_init_identity_prefix(self):
        # Retail form: a3/89 0d/89 15 stores, not c7 05; ends add esp,0x30; ret.
        body = bytearray(195)
        body[0:3] = bytes([0x83, 0xEC, 0x30])
        body[3:11] = bytes([0xC7, 0x44, 0x24, 0x00, 0x00, 0x00, 0x80, 0x3F])
        body[50] = 0xA3
        body[51:55] = struct.pack("<I", 0x660070)
        body[-4:] = bytes([0x83, 0xC4, 0x30, 0xC3])
        r = m.classify_body(0x402080, bytes(body))
        self.assertEqual(r["lane"], "INIT_IDENTITY_MAT")
        self.assertIn("00660070", r["newName"])


if __name__ == "__main__":
    unittest.main()
